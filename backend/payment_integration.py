# PhonePe Payment Integration for AI Ecommerce Platform
import hashlib
import base64
import json
import uuid
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Float, DateTime, Boolean, Text
from app.database import Base
import os

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, nullable=False)
    transaction_id = Column(String, unique=True, nullable=False)
    payment_method = Column(String(50), nullable=False)  # phonepe, cod
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    status = Column(String(50), default="pending")  # pending, success, failed, cancelled
    gateway_response = Column(Text)  # Store full gateway response
    gateway_transaction_id = Column(String(200))
    failure_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)

class PhonePePayment:
    def __init__(self):
        # PhonePe Configuration - Replace with actual credentials
        self.merchant_id = os.getenv("PHONEPE_MERCHANT_ID", "PGTESTPAYUAT")
        self.salt_key = os.getenv("PHONEPE_SALT_KEY", "099eb0cd-02cf-4e2a-8aca-3e6c6aff0399")
        self.salt_index = os.getenv("PHONEPE_SALT_INDEX", "1")
        self.base_url = os.getenv("PHONEPE_BASE_URL", "https://api-preprod.phonepe.com/apis/pg-sandbox")
        self.redirect_url = os.getenv("PHONEPE_REDIRECT_URL", "http://localhost:3000/payment/callback")
        self.callback_url = os.getenv("PHONEPE_CALLBACK_URL", "http://localhost:8001/api/payment/phonepe/callback")
    
    def generate_transaction_id(self) -> str:
        """Generate unique transaction ID"""
        return f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
    
    def generate_checksum(self, payload: str) -> str:
        """Generate PhonePe checksum"""
        string_to_hash = payload + "/pg/v1/pay" + self.salt_key
        sha256_hash = hashlib.sha256(string_to_hash.encode()).hexdigest()
        return sha256_hash + "###" + self.salt_index
    
    def create_payment_request(
        self, 
        order_id: str, 
        amount: float, 
        user_phone: str, 
        user_name: str,
        user_email: str
    ) -> Dict[str, Any]:
        """Create PhonePe payment request"""
        
        transaction_id = self.generate_transaction_id()
        amount_in_paisa = int(amount * 100)  # PhonePe expects amount in paisa
        
        # Payment payload
        payload_data = {
            "merchantId": self.merchant_id,
            "merchantTransactionId": transaction_id,
            "merchantUserId": f"USER_{order_id}",
            "amount": amount_in_paisa,
            "redirectUrl": self.redirect_url,
            "redirectMode": "POST",
            "callbackUrl": self.callback_url,
            "mobileNumber": user_phone,
            "paymentInstrument": {
                "type": "PAY_PAGE"
            }
        }
        
        # Encode payload
        payload_json = json.dumps(payload_data)
        payload_base64 = base64.b64encode(payload_json.encode()).decode()
        
        # Generate checksum
        checksum = self.generate_checksum(payload_base64)
        
        # Prepare request
        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": checksum
        }
        
        request_data = {
            "request": payload_base64
        }
        
        try:
            # Make API call to PhonePe
            response = requests.post(
                f"{self.base_url}/pg/v1/pay",
                json=request_data,
                headers=headers,
                timeout=30
            )
            
            response_data = response.json()
            
            if response_data.get("success") and response_data.get("code") == "PAYMENT_INITIATED":
                payment_url = response_data["data"]["instrumentResponse"]["redirectInfo"]["url"]
                
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "payment_url": payment_url,
                    "message": "Payment initiated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": response_data.get("message", "Payment initiation failed"),
                    "code": response_data.get("code")
                }
                
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def verify_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Verify payment status with PhonePe"""
        
        # Generate checksum for status check
        string_to_hash = f"/pg/v1/status/{self.merchant_id}/{transaction_id}" + self.salt_key
        checksum = hashlib.sha256(string_to_hash.encode()).hexdigest() + "###" + self.salt_index
        
        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": checksum,
            "X-MERCHANT-ID": self.merchant_id
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/pg/v1/status/{self.merchant_id}/{transaction_id}",
                headers=headers,
                timeout=30
            )
            
            response_data = response.json()
            
            if response_data.get("success"):
                payment_data = response_data["data"]
                return {
                    "success": True,
                    "status": payment_data.get("state"),
                    "amount": payment_data.get("amount", 0) / 100,  # Convert paisa to rupees
                    "transaction_id": payment_data.get("merchantTransactionId"),
                    "gateway_transaction_id": payment_data.get("transactionId"),
                    "payment_method": payment_data.get("paymentInstrument", {}).get("type"),
                    "response_code": payment_data.get("responseCode"),
                    "raw_response": response_data
                }
            else:
                return {
                    "success": False,
                    "error": response_data.get("message", "Payment verification failed"),
                    "code": response_data.get("code")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Payment verification error: {str(e)}"
            }

class PaymentCRUD:
    @staticmethod
    def create_payment_transaction(
        db: Session,
        order_id: str,
        transaction_id: str,
        amount: float,
        payment_method: str = "phonepe"
    ) -> PaymentTransaction:
        """Create payment transaction record"""
        
        payment = PaymentTransaction(
            order_id=order_id,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=amount,
            status="pending",
            expires_at=datetime.utcnow() + timedelta(minutes=15)  # 15 minutes expiry
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    
    @staticmethod
    def update_payment_status(
        db: Session,
        transaction_id: str,
        status: str,
        gateway_response: Optional[str] = None,
        gateway_transaction_id: Optional[str] = None,
        failure_reason: Optional[str] = None
    ) -> Optional[PaymentTransaction]:
        """Update payment transaction status"""
        
        payment = db.query(PaymentTransaction).filter(
            PaymentTransaction.transaction_id == transaction_id
        ).first()
        
        if not payment:
            return None
        
        payment.status = status
        payment.updated_at = datetime.utcnow()
        
        if gateway_response:
            payment.gateway_response = gateway_response
        
        if gateway_transaction_id:
            payment.gateway_transaction_id = gateway_transaction_id
        
        if failure_reason:
            payment.failure_reason = failure_reason
        
        db.commit()
        db.refresh(payment)
        return payment
    
    @staticmethod
    def get_payment_by_transaction_id(db: Session, transaction_id: str) -> Optional[PaymentTransaction]:
        """Get payment transaction by transaction ID"""
        return db.query(PaymentTransaction).filter(
            PaymentTransaction.transaction_id == transaction_id
        ).first()
    
    @staticmethod
    def get_payments_by_order_id(db: Session, order_id: str) -> list[PaymentTransaction]:
        """Get all payment transactions for an order"""
        return db.query(PaymentTransaction).filter(
            PaymentTransaction.order_id == order_id
        ).order_by(PaymentTransaction.created_at.desc()).all()

# Payment service class that combines PhonePe and other payment methods
class PaymentService:
    def __init__(self):
        self.phonepe = PhonePePayment()
    
    def initiate_payment(
        self, 
        db: Session,
        order_id: str, 
        amount: float, 
        payment_method: str,
        user_details: Dict[str, str]
    ) -> Dict[str, Any]:
        """Initiate payment based on method"""
        
        if payment_method.lower() == "phonepe":
            # Create PhonePe payment
            result = self.phonepe.create_payment_request(
                order_id=order_id,
                amount=amount,
                user_phone=user_details.get("phone", ""),
                user_name=user_details.get("name", ""),
                user_email=user_details.get("email", "")
            )
            
            if result["success"]:
                # Store payment transaction
                PaymentCRUD.create_payment_transaction(
                    db=db,
                    order_id=order_id,
                    transaction_id=result["transaction_id"],
                    amount=amount,
                    payment_method="phonepe"
                )
                
                return {
                    "success": True,
                    "payment_method": "phonepe",
                    "transaction_id": result["transaction_id"],
                    "payment_url": result["payment_url"],
                    "redirect_required": True
                }
            else:
                return result
                
        elif payment_method.lower() == "cod":
            # Cash on Delivery
            transaction_id = f"COD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
            
            PaymentCRUD.create_payment_transaction(
                db=db,
                order_id=order_id,
                transaction_id=transaction_id,
                amount=amount,
                payment_method="cod"
            )
            
            # Update payment status to success for COD
            PaymentCRUD.update_payment_status(
                db=db,
                transaction_id=transaction_id,
                status="success",
                gateway_response="Cash on Delivery - No payment gateway required"
            )
            
            return {
                "success": True,
                "payment_method": "cod",
                "transaction_id": transaction_id,
                "redirect_required": False,
                "message": "Order placed successfully. Pay cash on delivery."
            }
        else:
            return {
                "success": False,
                "error": f"Payment method {payment_method} not supported"
            }
    
    def verify_payment(self, db: Session, transaction_id: str) -> Dict[str, Any]:
        """Verify payment status"""
        
        payment = PaymentCRUD.get_payment_by_transaction_id(db, transaction_id)
        if not payment:
            return {"success": False, "error": "Payment transaction not found"}
        
        if payment.payment_method == "phonepe":
            # Verify with PhonePe
            result = self.phonepe.verify_payment(transaction_id)
            
            if result["success"]:
                # Update payment status in database
                status_map = {
                    "COMPLETED": "success",
                    "FAILED": "failed",
                    "PENDING": "pending"
                }
                
                new_status = status_map.get(result["status"], "pending")
                
                PaymentCRUD.update_payment_status(
                    db=db,
                    transaction_id=transaction_id,
                    status=new_status,
                    gateway_response=json.dumps(result["raw_response"]),
                    gateway_transaction_id=result.get("gateway_transaction_id")
                )
                
                return {
                    "success": True,
                    "status": new_status,
                    "amount": result["amount"],
                    "payment_method": "phonepe"
                }
            else:
                PaymentCRUD.update_payment_status(
                    db=db,
                    transaction_id=transaction_id,
                    status="failed",
                    failure_reason=result.get("error", "Payment verification failed")
                )
                
                return result
                
        elif payment.payment_method == "cod":
            # COD is always successful when order is placed
            return {
                "success": True,
                "status": "success",
                "amount": payment.amount,
                "payment_method": "cod"
            }
        
        return {"success": False, "error": "Unsupported payment method"}

# Initialize payment service
payment_service = PaymentService()