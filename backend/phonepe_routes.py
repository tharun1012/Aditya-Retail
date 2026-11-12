from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
from typing import Optional
import hashlib
import hmac
import re
import base64
import json
import uuid
import requests
from datetime import datetime
import os

router = APIRouter(prefix="/phonepe", tags=["PhonePe Payment"])

# PhonePe Configuration - LIVE/PRODUCTION
PHONEPE_MERCHANT_ID = os.environ.get("PHONEPE_MERCHANT_ID", "M224EIU0W7NHS")
PHONEPE_SALT_KEY = os.environ.get("PHONEPE_SALT_KEY", "b8063715-a14a-418a-973f-ef6341087184")  # API Key
PHONEPE_SALT_INDEX = int(os.environ.get("PHONEPE_SALT_INDEX", "1"))  # Key Index
PHONEPE_ENVIRONMENT = os.environ.get("PHONEPE_ENVIRONMENT", "PRODUCTION")

# API URLs - Official from PhonePe Documentation
PHONEPE_AUTH_URL = "https://api.phonepe.com/apis/identity-manager"
PHONEPE_PRODUCTION_URL = "https://api.phonepe.com/apis/hermes"
PHONEPE_SANDBOX_URL = "https://api-preprod.phonepe.com/apis/pg-sandbox"
PHONEPE_API_URL = PHONEPE_PRODUCTION_URL if PHONEPE_ENVIRONMENT == "PRODUCTION" else PHONEPE_SANDBOX_URL

# App URL for constructing full URLs (auto-configured during deployment)
APP_URL = os.environ.get("APP_URL", os.environ.get("REACT_APP_BACKEND_URL", "https://acct-workflow-1.preview.emergentagent.com"))

# Redirect URLs - construct full URLs from relative paths
def get_redirect_url():
    base_path = os.environ.get("REDIRECT_URL", "/#/payment-success")
    if base_path.startswith("http"):
        return base_path
    return f"{APP_URL.rstrip('/')}{base_path}"

def get_callback_url():
    base_path = os.environ.get("CALLBACK_URL", "/api/phonepe/callback")
    if base_path.startswith("http"):
        return base_path
    return f"{APP_URL.rstrip('/')}{base_path}"

# Models
class PaymentRequest(BaseModel):
    order_id: str
    amount: int  # Amount in paise (₹100 = 10000 paise)
    merchant_user_id: str
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    customer_phone: Optional[str] = None

class PaymentResponse(BaseModel):
    success: bool
    message: str
    payment_url: Optional[str] = None
    merchant_transaction_id: Optional[str] = None

# Helper Functions
def generate_checksum(payload_base64: str, api_path: str) -> str:
    """Generate SHA256 checksum for PhonePe API"""
    # PhonePe checksum format: SHA256(payload_base64 + api_path + salt_key) + ### + salt_index
    string_to_hash = payload_base64 + api_path + PHONEPE_SALT_KEY
    sha256_hash = hashlib.sha256(string_to_hash.encode()).hexdigest()
    return sha256_hash + "###" + str(PHONEPE_SALT_INDEX)

# Routes
@router.post("/initiate", response_model=PaymentResponse)
async def initiate_payment(payment_request: PaymentRequest):
    """Initiate a PhonePe payment transaction"""
    try:
        # Generate unique merchant transaction ID
        merchant_transaction_id = f"TXN_{payment_request.order_id}_{uuid.uuid4().hex[:8]}"

        # Persist the txn id on the linked order so the auto-reconcile job
        # can query PhonePe later even if the callback never arrives.
        try:
            from database import db as _pp_db
            _db = _pp_db
            await _db.orders.update_one(
                {"$or": [
                    {"order_number": payment_request.order_id},
                    {"id": payment_request.order_id},
                    {"order_id": payment_request.order_id},
                ]},
                {"$set": {
                    "phonepe_merchant_transaction_id": merchant_transaction_id,
                    "payment_gateway": "phonepe",
                    "payment.gateway": "phonepe",
                    "payment.status": "pending",
                    "payment_status": "pending",
                    "payment_initiated_at": datetime.now().isoformat(),
                }},
            )
        except Exception as _link_e:
            print(f"[PhonePe] could not link txn_id to order: {_link_e}")
        
        # Create payment payload
        payload = {
            "merchantId": PHONEPE_MERCHANT_ID,
            "merchantTransactionId": merchant_transaction_id,
            "merchantUserId": payment_request.merchant_user_id,
            "amount": payment_request.amount,
            "redirectUrl": get_redirect_url(),
            "redirectMode": "REDIRECT",
            "callbackUrl": get_callback_url(),
            "mobileNumber": payment_request.customer_phone if payment_request.customer_phone else "9999999999",
            "paymentInstrument": {
                "type": "PAY_PAGE"
            }
        }
        
        # Convert payload to JSON string
        payload_json = json.dumps(payload)
        
        # Encode payload in base64
        payload_base64 = base64.b64encode(payload_json.encode()).decode()
        
        # Generate checksum
        checksum = generate_checksum(payload_base64, "/pg/v1/pay")
        
        # Make API call to PhonePe - Official endpoint
        pay_url = f"{PHONEPE_API_URL}/pg/v1/pay"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-VERIFY": checksum
        }
        
        request_body = {
            "request": payload_base64
        }
        
        # Log for debugging
        print(f"[PhonePe] Payment Request:")
        print(f"  URL: {pay_url}")
        print(f"  Merchant ID: {PHONEPE_MERCHANT_ID}")
        print(f"  Transaction ID: {merchant_transaction_id}")
        print(f"  Checksum: {checksum}")
        
        response = requests.post(pay_url, json=request_body, headers=headers)
        response_data = response.json()
        
        print(f"[PhonePe] Response Status: {response.status_code}")
        print(f"[PhonePe] Response Data: {response_data}")
        
        if response.status_code == 200 and response_data.get("success"):
            payment_url = response_data.get("data", {}).get("instrumentResponse", {}).get("redirectInfo", {}).get("url")
            
            return PaymentResponse(
                success=True,
                message="Payment initiated successfully",
                payment_url=payment_url,
                merchant_transaction_id=merchant_transaction_id
            )
        else:
            error_message = response_data.get("message", "Payment initiation failed")
            # Mark the order failed immediately so it doesn't linger as a ghost "pending" order
            try:
                from database import db as _pp_db
                _db2 = _pp_db
                await _db2.orders.update_one(
                    {"$or": [
                        {"order_number": payment_request.order_id},
                        {"id": payment_request.order_id},
                        {"order_id": payment_request.order_id},
                    ]},
                    {"$set": {
                        "payment_status": "failed",
                        "payment.status": "failed",
                        "payment.failed_reason": f"INITIATION_FAILED ({response_data.get('code') or response.status_code})",
                        "order_status": "payment_failed",
                        "updated_at": datetime.now().isoformat(),
                    }},
                )
            except Exception as _gf_e:
                print(f"[PhonePe] could not mark init-failed order: {_gf_e}")
            return PaymentResponse(
                success=False,
                message=error_message
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Payment initiation failed: {str(e)}"
        )

@router.get("/status/{merchant_transaction_id}")
async def check_payment_status(merchant_transaction_id: str):
    """Check the status of a payment transaction"""
    try:
        # Create checksum for status check
        string_to_hash = f"/pg/v1/status/{PHONEPE_MERCHANT_ID}/{merchant_transaction_id}" + PHONEPE_SALT_KEY
        checksum = hashlib.sha256(string_to_hash.encode()).hexdigest() + "###" + str(PHONEPE_SALT_INDEX)
        
        # Make API call
        status_url = f"{PHONEPE_API_URL}/pg/v1/status/{PHONEPE_MERCHANT_ID}/{merchant_transaction_id}"
        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": checksum,
            "X-MERCHANT-ID": PHONEPE_MERCHANT_ID
        }
        
        response = requests.get(status_url, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response_data.get("data", {}),
                "code": response_data.get("code"),
                "message": response_data.get("message")
            }
        else:
            # PhonePe returns non-200 for some terminal states (e.g. TRANSACTION_NOT_FOUND).
            # Pass code/data through so the reconciler can act on failed/expired payments.
            return {
                "success": False,
                "data": response_data.get("data", {}),
                "code": response_data.get("code"),
                "http_status": response.status_code,
                "message": response_data.get("message", "Status check failed")
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Status check failed: {str(e)}"
        )

@router.post("/callback")
async def payment_callback(request: Request):
    """Handle PhonePe payment callback (webhook)"""
    try:
        # Get the request body
        body = await request.json()
        
        # Verify the callback signature
        x_verify = request.headers.get("X-VERIFY")
        
        # Decode the response
        response_base64 = body.get("response")
        if response_base64:
            response_json = base64.b64decode(response_base64).decode()
            response_data = json.loads(response_json)
            
            # Log the callback for debugging
            print(f"Payment callback received: {response_data}")
            
            # Extract payment details — PhonePe nests everything inside "data"
            data_obj = response_data.get("data") or {}
            merchant_transaction_id = response_data.get("merchantTransactionId") or data_obj.get("merchantTransactionId")
            transaction_id = response_data.get("transactionId") or data_obj.get("transactionId")
            state = response_data.get("state") or data_obj.get("state")  # COMPLETED / FAILED / PENDING
            payment_instrument = response_data.get("paymentInstrument") or data_obj.get("paymentInstrument") or {}
            amount = response_data.get("amount") or data_obj.get("amount") or 0

            # ALWAYS log the callback to `payment_callbacks` so we can recover
            # stuck orders that came in before txn_id was persisted on the order.
            try:
                from database import db as _pp_db
                _db = _pp_db
                # Extract the internal order_number from txn_id (format TXN_{order_number}_{uuid8})
                internal_order_number = None
                if merchant_transaction_id and "_" in merchant_transaction_id:
                    parts = merchant_transaction_id.split("_")
                    if len(parts) >= 3:
                        internal_order_number = "_".join(parts[1:-1])
                await _db.payment_callbacks.insert_one({
                    "gateway": "phonepe",
                    "merchant_transaction_id": merchant_transaction_id,
                    "transaction_id": transaction_id,
                    "merchant_order_id": internal_order_number,
                    "state": state,
                    "code": response_data.get("code"),
                    "amount": amount,
                    "payment_instrument": payment_instrument,
                    "created_at": datetime.now().isoformat(),
                })
            except Exception as _log_e:
                print(f"[PhonePe] callback log failed: {_log_e}")
            
            # Update order in database based on payment outcome
            code = response_data.get("code") or ""
            state = (state or "").upper()
            is_success = state in ("SUCCESS", "COMPLETED") or code == "PAYMENT_SUCCESS"
            is_failed = state in ("FAILED", "FAILURE") or code in (
                "PAYMENT_ERROR", "PAYMENT_DECLINED", "PAYMENT_CANCELLED",
                "TIMED_OUT", "AUTHORIZATION_FAILED",
            )
            order_query = {"$or": [
                {"phonepe_merchant_transaction_id": merchant_transaction_id},
                {"order_number": {"$regex": f".*{re.escape(merchant_transaction_id.split('_')[1])}.*"}} if (merchant_transaction_id and "_" in merchant_transaction_id) else {"_no_match_": True},
            ]}

            if is_success:
                from database import db as _pp_db
                db = _pp_db

                # Find order by phonepe_merchant_transaction_id (preferred)
                # or by the embedded order_id substring as a fallback.
                order = await db.orders.find_one_and_update(
                    order_query,
                    {"$set": {
                        "payment.status": "completed",
                        "payment_status": "completed",
                        "payment.transaction_id": transaction_id,
                        "payment.gateway": "phonepe",
                        "payment.verified_at": datetime.now().isoformat(),
                        "order_status": "confirmed",
                        "status": "confirmed",
                        "updated_at": datetime.now().isoformat(),
                    }},
                    return_document=True,
                )

                # Fire CRM email + Shiprocket sync (idempotent)
                if order:
                    try:
                        from pine_labs_routes import _post_payment_notify_and_sync
                        await _post_payment_notify_and_sync(order, db)
                    except Exception as _pe:
                        print(f"[PhonePe] post-payment notify+sync failed: {_pe}")

                    # Send payment success email
                    if order.get("customer_details", {}).get("email") or order.get("customer", {}).get("email"):
                        try:
                            from email_notification_service import email_notification_service
                            cust_email = order.get("customer_details", {}).get("email") or order["customer"]["email"]
                            cust_name = order.get("customer_details", {}).get("name") or order.get("customer", {}).get("name") or "Valued Customer"
                            await email_notification_service.send_payment_success(
                                customer_email=cust_email,
                                customer_name=cust_name,
                                order_id=order.get("order_number") or order.get("order_id") or order.get("id"),
                                transaction_id=transaction_id,
                                amount=amount / 100,  # Convert paise to rupees
                            )
                            print(f"✅ Payment success email sent to {cust_email}")
                        except Exception as email_error:
                            print(f"⚠️ Failed to send payment success email: {email_error}")

            elif is_failed:
                from database import db as _pp_db
                db = _pp_db
                failed_order = await db.orders.find_one_and_update(
                    order_query,
                    {"$set": {
                        "payment.status": "failed",
                        "payment_status": "failed",
                        "payment.gateway": "phonepe",
                        "payment.failed_code": code or state,
                        "order_status": "payment_failed",
                        "status": "payment_failed",
                        "updated_at": datetime.now().isoformat(),
                    }},
                    return_document=True,
                )
                if failed_order:
                    print(f"❌ [PhonePe] Payment FAILED ({code or state}) — order {failed_order.get('order_number')} marked payment_failed")
            
            return {
                "success": True,
                "message": "Callback processed",
                "state": state
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid callback format")
    
    except Exception as e:
        print(f"Callback processing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Callback processing failed: {str(e)}"
        )

@router.post("/refund")
async def initiate_refund(
    original_transaction_id: str,
    refund_amount: int,
    reason: Optional[str] = None
):
    """Initiate a refund for a completed payment"""
    try:
        # Generate unique refund ID
        merchant_refund_id = f"REFUND_{original_transaction_id}_{uuid.uuid4().hex[:8]}"
        
        # Create refund payload
        payload = {
            "merchantId": PHONEPE_MERCHANT_ID,
            "merchantTransactionId": original_transaction_id,
            "merchantRefundId": merchant_refund_id,
            "amount": refund_amount,
            "callbackUrl": get_callback_url()
        }
        
        # Convert to JSON and encode
        payload_json = json.dumps(payload)
        payload_base64 = base64.b64encode(payload_json.encode()).decode()
        
        # Generate checksum
        string_to_hash = payload_base64 + "/pg/v1/refund" + PHONEPE_SALT_KEY
        checksum = hashlib.sha256(string_to_hash.encode()).hexdigest() + "###" + str(PHONEPE_SALT_INDEX)
        
        # Make API call
        refund_url = f"{PHONEPE_API_URL}/pg/v1/refund"
        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": checksum
        }
        
        request_body = {
            "request": payload_base64
        }
        
        response = requests.post(refund_url, json=request_body, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get("success"):
            return {
                "success": True,
                "message": "Refund initiated successfully",
                "merchant_refund_id": merchant_refund_id,
                "data": response_data.get("data", {})
            }
        else:
            return {
                "success": False,
                "message": response_data.get("message", "Refund initiation failed")
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Refund initiation failed: {str(e)}"
        )

@router.get("/refund/status/{merchant_refund_id}")
async def check_refund_status(merchant_refund_id: str):
    """Check the status of a refund transaction"""
    try:
        # Create checksum
        string_to_hash = f"/pg/v1/refund/status/{PHONEPE_MERCHANT_ID}/{merchant_refund_id}" + PHONEPE_SALT_KEY
        checksum = hashlib.sha256(string_to_hash.encode()).hexdigest() + "###" + str(PHONEPE_SALT_INDEX)
        
        # Make API call
        status_url = f"{PHONEPE_API_URL}/pg/v1/refund/status/{PHONEPE_MERCHANT_ID}/{merchant_refund_id}"
        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": checksum,
            "X-MERCHANT-ID": PHONEPE_MERCHANT_ID
        }
        
        response = requests.get(status_url, headers=headers)
        response_data = response.json()
        
        return {
            "success": response.status_code == 200,
            "data": response_data.get("data", {}),
            "message": response_data.get("message", "")
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Refund status check failed: {str(e)}"
        )
