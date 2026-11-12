from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/mock-payment", tags=["Mock Payment"])

class MockPaymentRequest(BaseModel):
    order_id: str
    amount: int
    merchant_user_id: str
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    customer_phone: Optional[str] = None

@router.post("/initiate")
async def mock_payment_initiate(payment_request: MockPaymentRequest):
    """Mock payment for testing - Always succeeds"""
    try:
        transaction_id = f"MOCK_TXN_{payment_request.order_id}_{uuid.uuid4().hex[:8]}"
        
        # Simulate PhonePe-like response
        payment_url = f"https://acct-workflow-1.preview.emergentagent.com/mock-payment-page?txn_id={transaction_id}&amount={payment_request.amount}"
        
        return {
            "success": True,
            "message": "Mock payment initiated successfully",
            "payment_url": payment_url,
            "merchant_transaction_id": transaction_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{transaction_id}")
async def mock_payment_status(transaction_id: str):
    """Mock payment status - Always returns SUCCESS"""
    return {
        "success": True,
        "data": {
            "state": "COMPLETED",
            "amount": 100,  # ₹1
            "transactionId": transaction_id,
            "paymentInstrument": {
                "type": "UPI"
            }
        },
        "code": "PAYMENT_SUCCESS",
        "message": "Payment completed successfully (MOCK)"
    }
