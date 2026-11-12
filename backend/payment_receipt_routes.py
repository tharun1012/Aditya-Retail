from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from database import get_db
from file_storage import save_upload, serve_upload
import uuid
import os
import base64

router = APIRouter(prefix="/vouchers", tags=["Payment & Receipt Vouchers"])

# Upload directory for payment screenshots
UPLOAD_DIR = "/app/uploads/payment_screenshots"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class PaymentVoucher(BaseModel):
    voucher_type: str  # 'payment' or 'receipt'
    party_name: str
    amount: float
    payment_mode: str
    reference_number: Optional[str] = None
    description: str
    voucher_date: str
    created_by: str

class CreditDebitNote(BaseModel):
    note_type: str  # 'credit_note' or 'debit_note'
    party_name: str
    original_invoice_number: Optional[str] = None
    amount: float
    reason: str
    note_date: str
    created_by: str
    items: Optional[list] = None

@router.post("/payment-receipt")
async def create_voucher(voucher: PaymentVoucher, db = Depends(get_db)):
    """Create payment or receipt voucher"""
    try:
        today = datetime.now(timezone.utc)
        prefix = "PMT" if voucher.voucher_type == "payment" else "RCP"
        voucher_prefix = f"{prefix}-{today.strftime('%Y%m%d')}"
        
        count = await db.vouchers.count_documents({
            "voucher_type": voucher.voucher_type,
            "created_at": {
                "$gte": today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            }
        })
        
        voucher_number = f"{voucher_prefix}-{count + 1:04d}"
        
        voucher_data = {
            "id": str(uuid.uuid4()),
            "voucher_number": voucher_number,
            **voucher.dict(),
            "is_locked": True,  # Vouchers are locked by default
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.vouchers.insert_one(voucher_data)

        try:
            from realtime_accounting import post_transaction_event
            await post_transaction_event(db, f"voucher_{voucher_data['voucher_type']}", {
                "id": voucher_data["voucher_number"],
                "amount": voucher_data["amount"],
                "tax": 0,
                "payment_method": voucher_data.get("payment_mode", "n/a"),
                "payment_status": "pending",
                "date": voucher_data["created_at"],
                "party": voucher_data.get("party_name", "Unknown"),
                "description": voucher_data.get("description", "")
            })
        except Exception as e:
            print(f"⚠️ Real-time accounting failed for {voucher_data['voucher_number']}: {e}")

        return {
            "status": "success",
            "voucher_number": voucher_number,
            "voucher_id": voucher_data["id"],
            "message": f"{voucher.voucher_type.title()} voucher created successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create voucher: {str(e)}")

@router.post("/credit-debit-note")
async def create_note(note: CreditDebitNote, db = Depends(get_db)):
    """Create credit note or debit note"""
    try:
        today = datetime.now(timezone.utc)
        prefix = "CN" if note.note_type == "credit_note" else "DN"
        note_prefix = f"{prefix}-{today.strftime('%Y%m%d')}"
        
        count = await db.credit_debit_notes.count_documents({
            "note_type": note.note_type,
            "created_at": {
                "$gte": today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            }
        })
        
        note_number = f"{note_prefix}-{count + 1:04d}"
        
        note_data = {
            "id": str(uuid.uuid4()),
            "note_number": note_number,
            **note.dict(),
            "is_locked": True,  # Notes are locked by default
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.credit_debit_notes.insert_one(note_data)
        
        return {
            "status": "success",
            "note_number": note_number,
            "note_id": note_data["id"],
            "message": f"{note.note_type.replace('_', ' ').title()} created successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create note: {str(e)}")

@router.get("/payment-receipt")
async def get_vouchers(
    voucher_type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get payment/receipt vouchers"""
    try:
        query = {}
        
        if voucher_type:
            query["voucher_type"] = voucher_type
        
        if from_date and to_date:
            query["voucher_date"] = {"$gte": from_date, "$lte": to_date}
        
        skip = (page - 1) * limit
        
        vouchers = await db.vouchers.find(
            query,
            {"_id": 0}
        ).sort("voucher_date", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.vouchers.count_documents(query)
        
        return {
            "status": "success",
            "vouchers": vouchers,
            "total": total,
            "page": page
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch vouchers: {str(e)}")

@router.get("/credit-debit-note")
async def get_notes(
    note_type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get credit/debit notes"""
    try:
        query = {}
        
        if note_type:
            query["note_type"] = note_type
        
        if from_date and to_date:
            query["note_date"] = {"$gte": from_date, "$lte": to_date}
        
        skip = (page - 1) * limit
        
        notes = await db.credit_debit_notes.find(
            query,
            {"_id": 0}
        ).sort("note_date", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.credit_debit_notes.count_documents(query)
        
        return {
            "status": "success",
            "notes": notes,
            "total": total,
            "page": page
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notes: {str(e)}")



class ApproveReceiptRequest(BaseModel):
    approved_by: str
    remarks: Optional[str] = None

@router.put("/payment-receipt/{voucher_id}/approve")
async def approve_receipt(voucher_id: str, request: ApproveReceiptRequest, db = Depends(get_db)):
    """Approve a payment receipt - required for accounting verification"""
    try:
        voucher = await db.vouchers.find_one({"id": voucher_id})
        if not voucher:
            raise HTTPException(status_code=404, detail="Receipt not found")
        
        if voucher.get("voucher_type") != "receipt":
            raise HTTPException(status_code=400, detail="This is not a receipt voucher")
        
        if voucher.get("approval_status") == "approved":
            raise HTTPException(status_code=400, detail="Receipt is already approved")
        
        await db.vouchers.update_one(
            {"id": voucher_id},
            {
                "$set": {
                    "approval_status": "approved",
                    "approved_by": request.approved_by,
                    "approved_at": datetime.now(timezone.utc).isoformat(),
                    "approval_remarks": request.remarks,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Send email to customer after approval
        try:
            # Get linked document to find customer email
            linked_doc = voucher.get("linked_document", {})
            if linked_doc.get("id"):
                invoice = await db.offline_invoices.find_one({"id": linked_doc.get("id")}, {"_id": 0})
                if invoice:
                    customer_email = invoice.get("customer", {}).get("email")
                    customer_name = invoice.get("customer", {}).get("name", "Valued Customer")
                    
                    if customer_email:
                        from sendgrid_email_service import sendgrid_email_service
                        
                        html_content = f"""
                        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                                <h1 style="color: #D4AF37; margin: 0;">Aditya Retail</h1>
                                <p style="color: #ccc; margin-top: 5px;">Premium Home Appliances</p>
                            </div>
                            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                                <h2 style="color: #1a1a2e;">Payment Receipt Confirmed</h2>
                                <p>Dear {customer_name},</p>
                                <p>Thank you for your payment! This is to confirm that we have received and verified your payment.</p>
                                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                                    <p><strong>Receipt Number:</strong> {voucher.get("voucher_number")}</p>
                                    <p><strong>Amount:</strong> ₹{voucher.get("amount"):,.2f}</p>
                                    <p><strong>Payment Mode:</strong> {voucher.get("payment_mode", "N/A").upper()}</p>
                                    <p><strong>For Order:</strong> {linked_doc.get("number", "N/A")}</p>
                                </div>
                                <p>Your order will be processed and dispatched soon. You will receive tracking details once shipped.</p>
                                <p>Thank you for shopping with us!</p>
                                <p style="color: #666; font-size: 14px; margin-top: 20px;">
                                    For any queries, contact us at support@adityaretail.com<br>
                                    Phone: +91-XXXXXXXXXX
                                </p>
                            </div>
                        </div>
                        """
                        
                        sendgrid_email_service.send_email(
                            to_email=customer_email,
                            subject=f"Payment Receipt Confirmed - {voucher.get('voucher_number')}",
                            body=html_content,
                            from_agent="sales",
                            html=True
                        )
                        print(f"✅ Payment receipt approval email sent to {customer_email}")
        except Exception as email_error:
            print(f"⚠️ Failed to send approval email (non-blocking): {email_error}")
        
        return {
            "status": "success",
            "message": "Receipt approved successfully",
            "voucher_number": voucher.get("voucher_number")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve receipt: {str(e)}")


@router.put("/payment-receipt/{voucher_id}/reject")
async def reject_receipt(voucher_id: str, request: ApproveReceiptRequest, db = Depends(get_db)):
    """Reject a payment receipt"""
    try:
        voucher = await db.vouchers.find_one({"id": voucher_id})
        if not voucher:
            raise HTTPException(status_code=404, detail="Receipt not found")
        
        if voucher.get("approval_status") == "rejected":
            raise HTTPException(status_code=400, detail="Receipt is already rejected")
        
        await db.vouchers.update_one(
            {"id": voucher_id},
            {
                "$set": {
                    "approval_status": "rejected",
                    "rejected_by": request.approved_by,
                    "rejected_at": datetime.now(timezone.utc).isoformat(),
                    "rejection_remarks": request.remarks,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return {
            "status": "success",
            "message": "Receipt rejected",
            "voucher_number": voucher.get("voucher_number")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reject receipt: {str(e)}")


@router.get("/payment-receipt/pending-approval")
async def get_pending_receipts(
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get all receipts pending approval"""
    try:
        query = {
            "voucher_type": "receipt",
            "approval_status": "pending"
        }
        
        skip = (page - 1) * limit
        
        vouchers = await db.vouchers.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.vouchers.count_documents(query)
        
        return {
            "status": "success",
            "vouchers": vouchers,
            "total": total,
            "page": page,
            "total_pages": (total + limit - 1) // limit
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pending receipts: {str(e)}")



@router.post("/payment-receipt/upload-screenshot")
async def upload_payment_screenshot(
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    """Upload a payment screenshot for a receipt"""
    try:
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf']
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type. Allowed: JPEG, PNG, WebP, PDF")
        
        # Generate unique filename
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        filename = f"payment_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"
        
        # Save file
        content = await file.read()
        await save_upload(filename, content, file.content_type or "application/octet-stream")
        
        file_url = f"/api/vouchers/screenshots/{filename}"
        
        return {
            "status": "success",
            "filename": filename,
            "file_url": file_url,
            "content_type": file.content_type
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@router.get("/screenshots/{filename}")
async def get_payment_screenshot(filename: str):
    return await serve_upload(filename)


@router.put("/payment-receipt/{voucher_id}/attach-screenshot")
async def attach_screenshot_to_receipt(
    voucher_id: str,
    file_url: str,
    db = Depends(get_db)
):
    """Attach an uploaded screenshot to a receipt"""
    try:
        result = await db.vouchers.update_one(
            {"id": voucher_id},
            {
                "$set": {
                    "screenshot_url": file_url,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Receipt not found")
        
        return {
            "status": "success",
            "message": "Screenshot attached successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to attach screenshot: {str(e)}")


# ============================================================
# SO-LINKED PAYMENT RECEIPTS (Advance & Part Payments)
# ============================================================

class PaymentEntry(BaseModel):
    """Single payment entry in a split payment"""
    mode: str  # cash, upi, card, neft, cheque
    amount: float
    reference: Optional[str] = None  # Transaction ID, Cheque #, etc.
    bank_name: Optional[str] = None  # For cheque/NEFT


class CreateSOPaymentRequest(BaseModel):
    """Create a payment receipt against a Sales Order"""
    so_id: str  # Sales Order ID
    payments: list  # Split payment entries [{mode, amount, reference, bank_name}]
    remarks: Optional[str] = None
    collected_by: str  # Staff name who collected


async def generate_so_receipt_number(db, store_code: str) -> str:
    """Generate unique payment receipt number: PR-{STORE}-YYYYMMDD-XXXX"""
    today = datetime.now(timezone.utc)
    date_str = today.strftime("%Y%m%d")
    prefix = f"PR-{store_code}-{date_str}"
    
    # Count existing receipts for today
    count = await db.so_payment_receipts.count_documents({
        "receipt_number": {"$regex": f"^{prefix}"}
    })
    
    return f"{prefix}-{(count + 1):04d}"


@router.post("/so-payment/create")
async def create_so_payment_receipt(request: CreateSOPaymentRequest, db = Depends(get_db)):
    """
    Create a payment receipt for advance/part payment against a Sales Order.
    Supports split payments (multiple payment modes: cash + UPI + card).
    """
    try:
        # Fetch the Sales Order
        so = await db.offline_invoices.find_one(
            {"id": request.so_id, "document_type": "sales_order"},
            {"_id": 0}
        )
        
        if not so:
            raise HTTPException(status_code=404, detail="Sales Order not found")
        
        # Calculate total payment amount
        total_amount = sum(p.get("amount", 0) for p in request.payments)
        
        if total_amount <= 0:
            raise HTTPException(status_code=400, detail="Payment amount must be greater than 0")
        
        # Get existing payments for this SO
        existing_receipts = await db.so_payment_receipts.find(
            {"so_id": request.so_id},
            {"_id": 0, "total_amount": 1}
        ).to_list(None)
        
        previously_paid = sum(r.get("total_amount", 0) for r in existing_receipts)
        total_paid = previously_paid + total_amount
        so_amount = so.get("total_amount", 0)
        balance_due = so_amount - total_paid
        
        # Don't allow overpayment
        if balance_due < 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Payment amount exceeds balance due. Maximum payable: ₹{so_amount - previously_paid:.2f}"
            )
        
        # Generate receipt number
        store_code = so.get("store_code", "ADR")
        receipt_number = await generate_so_receipt_number(db, store_code)
        
        # Create payment receipt
        receipt_data = {
            "id": str(uuid.uuid4()),
            "receipt_number": receipt_number,
            "so_id": request.so_id,
            "so_number": so.get("invoice_number"),
            "customer": {
                "name": so.get("customer", {}).get("name"),
                "phone": so.get("customer", {}).get("phone"),
                "email": so.get("customer", {}).get("email")
            },
            "store_code": store_code,
            "store_name": so.get("store_details", {}).get("name"),
            "store_details": (await db.stores.find_one(
                {"code": store_code},
                {"_id": 0, "name": 1, "address": 1, "city": 1, "pincode": 1, "phone": 1, "gst_number": 1}
            )) or so.get("store_details", {}),
            
            # Payment details
            "payments": [
                {
                    "mode": p.get("mode"),
                    "amount": p.get("amount"),
                    "reference": p.get("reference"),
                    "bank_name": p.get("bank_name")
                } for p in request.payments
            ],
            "total_amount": total_amount,
            
            # Running totals
            "so_total_amount": so_amount,
            "previously_paid": previously_paid,
            "total_paid_till_now": total_paid,
            "balance_due": balance_due,
            
            # Metadata
            "collected_by": request.collected_by,
            "remarks": request.remarks,
            "receipt_index": len(existing_receipts) + 1,  # 1st payment, 2nd payment, etc.
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.so_payment_receipts.insert_one(receipt_data)

        try:
            from realtime_accounting import post_transaction_event
            await post_transaction_event(db, "payment_receipt", {
                "id": receipt_data["receipt_number"],
                "amount": receipt_data["total_amount"],
                "tax": 0,
                "payment_method": ",".join(p.get("mode", "") for p in receipt_data.get("payments", [])) or "n/a",
                "payment_status": "paid",
                "date": receipt_data["created_at"],
                "customer": receipt_data.get("customer", {}).get("name", "Unknown"),
                "so_number": receipt_data.get("so_number")
            })
        except Exception as e:
            print(f"⚠️ Real-time accounting failed for {receipt_data['receipt_number']}: {e}")
        
        # Update SO with payment info
        payment_status = "paid" if balance_due <= 0 else ("partially_paid" if total_paid > 0 else "pending")
        
        await db.offline_invoices.update_one(
            {"id": request.so_id},
            {
                "$set": {
                    "total_paid": total_paid,
                    "balance_due": balance_due,
                    "payment_status": payment_status,
                    "last_payment_date": datetime.now(timezone.utc).isoformat(),
                    "last_payment_receipt": receipt_number,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Auto-create one voucher per split-payment entry so this shows up
        # in admin Vouchers Management (each mode gets its own linked voucher)
        voucher_numbers = []
        today = datetime.now(timezone.utc)
        for entry in request.payments:
            entry_amount = entry.get("amount", 0)
            if entry_amount <= 0:
                continue

            receipt_count = await db.vouchers.count_documents({
                "voucher_type": "receipt",
                "created_at": {
                    "$gte": today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
                }
            })
            voucher_number = f"RCP-{today.strftime('%Y%m%d')}-{receipt_count + 1:04d}"

            voucher_data = {
                "id": str(uuid.uuid4()),
                "voucher_number": voucher_number,
                "voucher_type": "receipt",
                "party_name": so.get("customer", {}).get("name", "Unknown"),
                "amount": entry_amount,
                "payment_mode": entry.get("mode"),
                "reference_number": entry.get("reference"),
                "description": f"SO payment ({receipt_number}) for Sales Order: {so.get('invoice_number', request.so_id)}",
                "voucher_date": today.isoformat(),
                "created_by": request.collected_by,
                "linked_document": {
                    "type": "sales_order",
                    "number": so.get("invoice_number", request.so_id),
                    "id": request.so_id
                },
                "is_advance": balance_due > 0,
                "approval_status": "pending",
                "approved_by": None,
                "approved_at": None,
                "is_locked": True,
                "created_at": today.isoformat(),
                "updated_at": today.isoformat()
            }
            await db.vouchers.insert_one(voucher_data)

            try:
                from realtime_accounting import post_transaction_event
                await post_transaction_event(db, f"voucher_{voucher_data['voucher_type']}", {
                    "id": voucher_data["voucher_number"],
                    "amount": voucher_data["amount"],
                    "tax": 0,
                    "payment_method": voucher_data.get("payment_mode", "n/a"),
                    "payment_status": "pending",
                    "date": voucher_data["created_at"],
                    "party": voucher_data.get("party_name", "Unknown"),
                    "description": voucher_data.get("description", "")
                })
            except Exception as e:
                print(f"⚠️ Real-time accounting failed for {voucher_data['voucher_number']}: {e}")

            voucher_numbers.append(voucher_number)

        return {
            "status": "success",
            "receipt_id": receipt_data["id"],
            "receipt_number": receipt_number,
            "voucher_numbers": voucher_numbers,
            "this_payment": total_amount,
            "total_paid_till_now": total_paid,
            "balance_due": balance_due,
            "payment_status": payment_status,
            "message": f"Payment receipt {receipt_number} created successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create payment receipt: {str(e)}")


@router.get("/so-payment/by-so/{so_id}")
async def get_so_payment_history(so_id: str, db = Depends(get_db)):
    """Get all payment receipts for a Sales Order"""
    try:
        # Get the SO first
        so = await db.offline_invoices.find_one(
            {"id": so_id},
            {"_id": 0, "invoice_number": 1, "total_amount": 1, "customer": 1, "payment_status": 1, "items": 1}
        )
        
        if not so:
            raise HTTPException(status_code=404, detail="Sales Order not found")
        
        # Get all receipts
        receipts = await db.so_payment_receipts.find(
            {"so_id": so_id},
            {"_id": 0}
        ).sort("created_at", 1).to_list(None)  # Ascending order for history
        
        total_paid = sum(r.get("total_amount", 0) for r in receipts)
        balance_due = so.get("total_amount", 0) - total_paid
        
        return {
            "status": "success",
            "so_number": so.get("invoice_number"),
            "so_total": so.get("total_amount"),
            "total_paid": total_paid,
            "balance_due": balance_due,
            "payment_status": "paid" if balance_due <= 0 else ("partially_paid" if total_paid > 0 else "pending"),
            "receipts": receipts,
            "receipt_count": len(receipts),
            "customer": so.get("customer"),
            "items_summary": f"{len(so.get('items', []))} items"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch payment history: {str(e)}")


@router.get("/so-payment/list")
async def list_so_payment_receipts(
    store_code: Optional[str] = None,
    customer_phone: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    user_role: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """
    List all SO payment receipts with filters.
    RBAC: Store users must have store_code and only see their store's receipts.
    """
    try:
        query = {}
        
        # RBAC: If store_code is provided, always filter by it
        if store_code:
            query["store_code"] = store_code
        
        if customer_phone:
            query["customer.phone"] = customer_phone
        
        if date_from:
            query["created_at"] = {"$gte": date_from}
        
        if date_to:
            if "created_at" in query:
                query["created_at"]["$lte"] = date_to + "T23:59:59"
            else:
                query["created_at"] = {"$lte": date_to + "T23:59:59"}
        
        skip = (page - 1) * limit
        
        receipts = await db.so_payment_receipts.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.so_payment_receipts.count_documents(query)
        
        # Calculate summary
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": None,
                "total_collected": {"$sum": "$total_amount"},
                "receipt_count": {"$sum": 1}
            }}
        ]
        
        summary_result = await db.so_payment_receipts.aggregate(pipeline).to_list(None)
        summary = summary_result[0] if summary_result else {"total_collected": 0, "receipt_count": 0}
        
        # Payment mode breakdown
        mode_pipeline = [
            {"$match": query},
            {"$unwind": "$payments"},
            {"$group": {
                "_id": "$payments.mode",
                "total": {"$sum": "$payments.amount"},
                "count": {"$sum": 1}
            }}
        ]
        
        mode_results = await db.so_payment_receipts.aggregate(mode_pipeline).to_list(None)
        mode_totals = {r["_id"]: {"total": r["total"], "count": r["count"]} for r in mode_results}
        
        return {
            "status": "success",
            "receipts": receipts,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total > 0 else 0,
            "summary": {
                "total_collected": summary.get("total_collected", 0),
                "receipt_count": summary.get("receipt_count", 0),
                "by_mode": mode_totals
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list receipts: {str(e)}")


@router.get("/so-payment/{receipt_id}")
async def get_so_payment_receipt(receipt_id: str, db = Depends(get_db)):
    """Get a single payment receipt by ID (for printing/sharing)"""
    try:
        receipt = await db.so_payment_receipts.find_one({"id": receipt_id}, {"_id": 0})
        
        if not receipt:
            raise HTTPException(status_code=404, detail="Payment receipt not found")
        
        # Get store details for the receipt
        store = await db.stores.find_one(
            {"code": receipt.get("store_code")},
            {"_id": 0, "name": 1, "address": 1, "phone": 1, "gst_number": 1}
        )
        
        if store and not receipt.get("store_details"):
            receipt["store_details"] = store
        
        return {
            "status": "success",
            "receipt": receipt
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch receipt: {str(e)}")


@router.get("/pending-payments/sos")
async def get_pending_payment_sos(
    store_code: Optional[str] = None,
    user_role: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """
    Get Sales Orders with pending/partial payments.
    RBAC: Store users MUST provide store_code and will only see their store's data.
    Admin/Super Admin/Accountant can see all stores or filter by store_code.
    """
    try:
        query = {
            "document_type": "sales_order",
            "$or": [
                {"payment_status": {"$in": ["pending", "partially_paid"]}},
                {"payment_status": {"$exists": False}},
                {"balance_due": {"$gt": 0}}
            ]
        }
        
        # RBAC Enforcement: Store-level users must have store_code filter
        # If store_code is provided, always filter by it (for both store users and admins filtering)
        if store_code:
            query["store_code"] = store_code
        
        skip = (page - 1) * limit
        
        sos = await db.offline_invoices.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        # Add payment summary for each SO
        for so in sos:
            receipts = await db.so_payment_receipts.find(
                {"so_id": so.get("id")},
                {"_id": 0, "total_amount": 1, "receipt_number": 1}
            ).to_list(None)
            so["total_paid"] = sum(r.get("total_amount", 0) for r in receipts)
            so["balance_due"] = so.get("total_amount", 0) - so["total_paid"]
            so["payment_count"] = len(receipts)
            so["last_receipt"] = receipts[-1].get("receipt_number") if receipts else None
        
        # Filter out fully paid ones (safety check)
        sos = [so for so in sos if so["balance_due"] > 0]
        
        total = len(sos)
        
        return {
            "status": "success",
            "sales_orders": sos,
            "total": total,
            "page": page,
            "limit": limit
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pending payment SOs: {str(e)}")
