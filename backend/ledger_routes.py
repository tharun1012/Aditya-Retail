"""
Party Ledger Management Routes
Manages customer and vendor ledger accounts with outstanding tracking
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from database import get_db
import uuid
import logging

router = APIRouter(prefix="/ledger", tags=["Party Ledger"])
logger = logging.getLogger(__name__)


# ============ MODELS ============

class LedgerAccountCreate(BaseModel):
    name: str
    account_type: str  # customer, vendor, bank, cash, expense, income
    phone: Optional[str] = ""
    email: Optional[str] = ""
    gst_number: Optional[str] = ""
    pan_number: Optional[str] = ""
    address: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    pincode: Optional[str] = ""
    credit_limit: float = 0
    credit_days: int = 30
    opening_balance: float = 0
    opening_balance_type: str = "debit"  # debit or credit


class LedgerTransactionCreate(BaseModel):
    ledger_id: str
    transaction_type: str  # invoice, payment, receipt, journal, credit_note, debit_note
    reference_type: Optional[str] = ""  # order, purchase_bill, expense, etc.
    reference_id: Optional[str] = ""
    reference_number: Optional[str] = ""
    debit_amount: float = 0
    credit_amount: float = 0
    narration: Optional[str] = ""
    transaction_date: Optional[str] = None


class PaymentCreate(BaseModel):
    ledger_id: str
    amount: float
    payment_mode: str  # cash, bank, upi, cheque, card
    payment_date: Optional[str] = None
    reference_number: Optional[str] = ""  # cheque no, UTR, etc.
    bank_account_id: Optional[str] = ""
    narration: Optional[str] = ""
    # Link to invoices/bills being paid
    allocations: Optional[List[Dict[str, Any]]] = []  # [{invoice_id, amount}]


# ============ LEDGER ACCOUNTS ============

@router.post("/accounts/create")
async def create_ledger_account(account: LedgerAccountCreate, db = Depends(get_db)):
    """Create a new ledger account (customer/vendor/bank)"""
    try:
        # Check for duplicate
        existing = await db.ledgers.find_one({
            "name": {"$regex": f"^{account.name}$", "$options": "i"},
            "account_type": account.account_type
        })
        if existing:
            raise HTTPException(status_code=400, detail=f"Account '{account.name}' already exists")
        
        account_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        # Calculate opening balance
        debit_balance = account.opening_balance if account.opening_balance_type == "debit" else 0
        credit_balance = account.opening_balance if account.opening_balance_type == "credit" else 0
        
        ledger_data = {
            "id": account_id,
            "name": account.name,
            "account_type": account.account_type,
            "phone": account.phone,
            "email": account.email,
            "gst_number": account.gst_number,
            "pan_number": account.pan_number,
            "address": account.address,
            "city": account.city,
            "state": account.state,
            "pincode": account.pincode,
            "credit_limit": account.credit_limit,
            "credit_days": account.credit_days,
            "opening_balance": account.opening_balance,
            "opening_balance_type": account.opening_balance_type,
            "current_debit": debit_balance,
            "current_credit": credit_balance,
            "current_balance": debit_balance - credit_balance,
            "total_transactions": 0,
            "last_transaction_date": None,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
        
        await db.ledgers.insert_one(ledger_data)
        
        # Create opening balance entry if any
        if account.opening_balance > 0:
            await db.ledger_transactions.insert_one({
                "id": str(uuid.uuid4()),
                "ledger_id": account_id,
                "transaction_type": "opening",
                "reference_type": "opening_balance",
                "reference_id": "",
                "reference_number": "Opening Balance",
                "debit_amount": debit_balance,
                "credit_amount": credit_balance,
                "balance_after": debit_balance - credit_balance,
                "narration": "Opening Balance",
                "transaction_date": now,
                "created_at": now
            })
        
        return {
            "status": "success",
            "message": f"Ledger account '{account.name}' created",
            "account_id": account_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create ledger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts")
async def get_ledger_accounts(
    account_type: Optional[str] = None,
    search: Optional[str] = None,
    has_balance: Optional[bool] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get all ledger accounts with filters"""
    try:
        query = {"is_active": True}
        
        if account_type:
            query["account_type"] = account_type
        
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"phone": {"$regex": search, "$options": "i"}},
                {"gst_number": {"$regex": search, "$options": "i"}}
            ]
        
        if has_balance is not None:
            if has_balance:
                query["current_balance"] = {"$ne": 0}
            else:
                query["current_balance"] = 0
        
        skip = (page - 1) * limit
        
        accounts = await db.ledgers.find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit).to_list(length=limit)
        total = await db.ledgers.count_documents(query)
        
        # Get summary by type
        summary = {}
        for acc_type in ["customer", "vendor"]:
            pipeline = [
                {"$match": {"account_type": acc_type, "is_active": True}},
                {"$group": {
                    "_id": None,
                    "total_accounts": {"$sum": 1},
                    "total_debit": {"$sum": "$current_debit"},
                    "total_credit": {"$sum": "$current_credit"},
                    "total_balance": {"$sum": "$current_balance"}
                }}
            ]
            result = await db.ledgers.aggregate(pipeline).to_list(length=1)
            summary[acc_type] = result[0] if result else {"total_accounts": 0, "total_balance": 0}
        
        return {
            "status": "success",
            "accounts": accounts,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ PENDING INVOICES/BILLS FOR ALLOCATION ============

@router.get("/pending/invoices/{ledger_id}")
async def get_pending_invoices(ledger_id: str, db = Depends(get_db)):
    """Get pending invoices for a customer (for payment allocation)"""
    try:
        # Get ledger to find customer
        ledger = await db.ledgers.find_one({"id": ledger_id}, {"_id": 0})
        if not ledger:
            raise HTTPException(status_code=404, detail="Ledger not found")
        
        # Find orders with pending payment
        # Match by customer phone/email or customer_id
        query = {
            "payment_status": {"$in": ["pending", "partial"]},
            "$or": []
        }
        
        if ledger.get("phone"):
            query["$or"].append({"customer_details.phone": ledger.get("phone")})
        if ledger.get("email"):
            query["$or"].append({"customer_details.email": ledger.get("email")})
        
        # If no matching criteria, return empty
        if not query["$or"]:
            return {"status": "success", "invoices": [], "total_pending": 0}
        
        orders = await db.orders.find(
            query,
            {"_id": 0, "id": 1, "order_number": 1, "total_amount": 1, "created_at": 1, 
             "payment_status": 1, "amount_paid": 1}
        ).sort("created_at", -1).limit(50).to_list(length=50)
        
        # Calculate pending amounts
        invoices = []
        total_pending = 0
        
        for order in orders:
            paid = order.get("amount_paid", 0)
            pending = order.get("total_amount", 0) - paid
            if pending > 0:
                invoices.append({
                    "id": order.get("id"),
                    "invoice_number": order.get("order_number"),
                    "date": order.get("created_at"),
                    "total_amount": order.get("total_amount", 0),
                    "amount_paid": paid,
                    "pending_amount": pending
                })
                total_pending += pending
        
        return {
            "status": "success",
            "invoices": invoices,
            "total_pending": total_pending
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get pending invoices failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending/bills/{ledger_id}")
async def get_pending_bills(ledger_id: str, db = Depends(get_db)):
    """Get pending purchase bills for a vendor (for payment allocation)"""
    try:
        # Get ledger to find vendor
        ledger = await db.ledgers.find_one({"id": ledger_id}, {"_id": 0})
        if not ledger:
            raise HTTPException(status_code=404, detail="Ledger not found")
        
        # Find purchase bills with pending payment
        query = {
            "payment_status": {"$in": ["pending", "partial", None]},
            "$or": []
        }
        
        # Match by vendor name (case insensitive)
        if ledger.get("name"):
            query["$or"].append({"vendor.name": {"$regex": f"^{ledger.get('name')}$", "$options": "i"}})
        if ledger.get("gst_number"):
            query["$or"].append({"vendor.gst_number": ledger.get("gst_number")})
        
        # If no matching criteria, return empty
        if not query["$or"]:
            return {"status": "success", "bills": [], "total_pending": 0}
        
        bills = await db.purchase_bills.find(
            query,
            {"_id": 0, "id": 1, "bill_number": 1, "grand_total": 1, "bill_date": 1,
             "payment_status": 1, "amount_paid": 1}
        ).sort("bill_date", -1).limit(50).to_list(length=50)
        
        # Calculate pending amounts
        pending_bills = []
        total_pending = 0
        
        for bill in bills:
            paid = bill.get("amount_paid", 0)
            pending = bill.get("grand_total", 0) - paid
            if pending > 0:
                pending_bills.append({
                    "id": bill.get("id"),
                    "bill_number": bill.get("bill_number"),
                    "date": bill.get("bill_date"),
                    "total_amount": bill.get("grand_total", 0),
                    "amount_paid": paid,
                    "pending_amount": pending
                })
                total_pending += pending
        
        return {
            "status": "success",
            "bills": pending_bills,
            "total_pending": total_pending
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get pending bills failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts/{account_id}")
async def get_ledger_account(account_id: str, db = Depends(get_db)):
    """Get single ledger account with recent transactions"""
    try:
        account = await db.ledgers.find_one({"id": account_id}, {"_id": 0})
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Get recent transactions
        transactions = await db.ledger_transactions.find(
            {"ledger_id": account_id},
            {"_id": 0}
        ).sort("transaction_date", -1).limit(20).to_list(length=20)
        
        return {
            "status": "success",
            "account": account,
            "recent_transactions": transactions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/accounts/{account_id}")
async def update_ledger_account(
    account_id: str,
    updates: Dict[str, Any],
    db = Depends(get_db)
):
    """Update ledger account details"""
    try:
        # Don't allow updating balance fields directly
        protected = ["id", "current_debit", "current_credit", "current_balance", "created_at"]
        for field in protected:
            updates.pop(field, None)
        
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        result = await db.ledgers.update_one({"id": account_id}, {"$set": updates})
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Account not found")
        
        return {"status": "success", "message": "Account updated"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ LEDGER TRANSACTIONS ============

@router.post("/transactions/create")
async def create_ledger_transaction(txn: LedgerTransactionCreate, db = Depends(get_db)):
    """Create a ledger transaction entry"""
    try:
        # Verify ledger exists
        ledger = await db.ledgers.find_one({"id": txn.ledger_id})
        if not ledger:
            raise HTTPException(status_code=404, detail="Ledger account not found")
        
        now = datetime.now(timezone.utc).isoformat()
        txn_date = txn.transaction_date or now
        
        # Calculate new balance
        new_debit = ledger.get("current_debit", 0) + txn.debit_amount
        new_credit = ledger.get("current_credit", 0) + txn.credit_amount
        new_balance = new_debit - new_credit
        
        txn_id = str(uuid.uuid4())
        txn_data = {
            "id": txn_id,
            "ledger_id": txn.ledger_id,
            "ledger_name": ledger.get("name"),
            "transaction_type": txn.transaction_type,
            "reference_type": txn.reference_type,
            "reference_id": txn.reference_id,
            "reference_number": txn.reference_number,
            "debit_amount": txn.debit_amount,
            "credit_amount": txn.credit_amount,
            "balance_after": new_balance,
            "narration": txn.narration,
            "transaction_date": txn_date,
            "created_at": now
        }
        
        await db.ledger_transactions.insert_one(txn_data)
        
        # Update ledger balance
        await db.ledgers.update_one(
            {"id": txn.ledger_id},
            {"$set": {
                "current_debit": new_debit,
                "current_credit": new_credit,
                "current_balance": new_balance,
                "last_transaction_date": txn_date,
                "updated_at": now
            },
            "$inc": {"total_transactions": 1}}
        )
        
        return {
            "status": "success",
            "message": "Transaction recorded",
            "transaction_id": txn_id,
            "new_balance": new_balance
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create transaction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/{ledger_id}")
async def get_ledger_transactions(
    ledger_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    transaction_type: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get transactions for a ledger account (ledger statement)"""
    try:
        query = {"ledger_id": ledger_id}
        
        if from_date:
            query["transaction_date"] = {"$gte": from_date}
        if to_date:
            if "transaction_date" in query:
                query["transaction_date"]["$lte"] = to_date
            else:
                query["transaction_date"] = {"$lte": to_date}
        
        if transaction_type:
            query["transaction_type"] = transaction_type
        
        skip = (page - 1) * limit
        
        transactions = await db.ledger_transactions.find(query, {"_id": 0}).sort("transaction_date", -1).skip(skip).limit(limit).to_list(length=limit)
        total = await db.ledger_transactions.count_documents(query)
        
        # Get ledger details
        ledger = await db.ledgers.find_one({"id": ledger_id}, {"_id": 0})
        
        return {
            "status": "success",
            "ledger": ledger,
            "transactions": transactions,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ OUTSTANDING & AGING ============

@router.get("/outstanding/customers")
async def get_customer_outstanding(
    days_filter: Optional[int] = None,
    min_amount: Optional[float] = None,
    db = Depends(get_db)
):
    """Get all customers with outstanding balance (receivables)"""
    try:
        query = {
            "account_type": "customer",
            "is_active": True,
            "current_balance": {"$gt": 0}  # Debit balance = customer owes us
        }
        
        if min_amount:
            query["current_balance"]["$gte"] = min_amount
        
        customers = await db.ledgers.find(query, {"_id": 0}).sort("current_balance", -1).to_list(length=500)
        
        # Calculate aging for each customer
        today = datetime.now(timezone.utc)
        
        for customer in customers:
            # Get unpaid invoices for aging
            unpaid_invoices = await db.ledger_transactions.find({
                "ledger_id": customer["id"],
                "transaction_type": "invoice",
                "debit_amount": {"$gt": 0}
            }, {"_id": 0}).to_list(length=100)
            
            # Simple aging calculation
            customer["aging"] = {
                "current": 0,  # 0-30 days
                "days_31_60": 0,
                "days_61_90": 0,
                "over_90": 0
            }
            
            for inv in unpaid_invoices:
                try:
                    inv_date = datetime.fromisoformat(inv.get("transaction_date", "").replace("Z", "+00:00"))
                    days_old = (today - inv_date).days
                    amount = inv.get("debit_amount", 0)
                    
                    if days_old <= 30:
                        customer["aging"]["current"] += amount
                    elif days_old <= 60:
                        customer["aging"]["days_31_60"] += amount
                    elif days_old <= 90:
                        customer["aging"]["days_61_90"] += amount
                    else:
                        customer["aging"]["over_90"] += amount
                except Exception:
                    customer["aging"]["current"] += inv.get("debit_amount", 0)
        
        # Calculate totals
        total_outstanding = sum(c.get("current_balance", 0) for c in customers)
        
        return {
            "status": "success",
            "total_outstanding": total_outstanding,
            "customer_count": len(customers),
            "customers": customers
        }
        
    except Exception as e:
        logger.error(f"Get customer outstanding failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/outstanding/vendors")
async def get_vendor_outstanding(
    days_filter: Optional[int] = None,
    min_amount: Optional[float] = None,
    db = Depends(get_db)
):
    """Get all vendors with outstanding balance (payables)"""
    try:
        query = {
            "account_type": "vendor",
            "is_active": True,
            "current_balance": {"$lt": 0}  # Credit balance = we owe vendor
        }
        
        vendors = await db.ledgers.find(query, {"_id": 0}).sort("current_balance", 1).to_list(length=500)
        
        # Convert to positive amounts for display
        for vendor in vendors:
            vendor["amount_payable"] = abs(vendor.get("current_balance", 0))
        
        total_payable = sum(v.get("amount_payable", 0) for v in vendors)
        
        return {
            "status": "success",
            "total_payable": total_payable,
            "vendor_count": len(vendors),
            "vendors": vendors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/outstanding/aging-report")
async def get_aging_report(
    account_type: str = "customer",
    db = Depends(get_db)
):
    """Get detailed aging report for receivables/payables"""
    try:
        balance_condition = {"$gt": 0} if account_type == "customer" else {"$lt": 0}
        
        accounts = await db.ledgers.find({
            "account_type": account_type,
            "is_active": True,
            "current_balance": balance_condition
        }, {"_id": 0}).to_list(length=500)
        
        today = datetime.now(timezone.utc)
        
        aging_summary = {
            "current": {"count": 0, "amount": 0},
            "days_31_60": {"count": 0, "amount": 0},
            "days_61_90": {"count": 0, "amount": 0},
            "over_90": {"count": 0, "amount": 0}
        }
        
        detailed_aging = []
        
        for account in accounts:
            balance = abs(account.get("current_balance", 0))
            last_txn = account.get("last_transaction_date")
            
            days_old = 0
            if last_txn:
                try:
                    last_date = datetime.fromisoformat(last_txn.replace("Z", "+00:00"))
                    days_old = (today - last_date).days
                except Exception:
                    pass
            
            bucket = "current"
            if days_old > 90:
                bucket = "over_90"
            elif days_old > 60:
                bucket = "days_61_90"
            elif days_old > 30:
                bucket = "days_31_60"
            
            aging_summary[bucket]["count"] += 1
            aging_summary[bucket]["amount"] += balance
            
            detailed_aging.append({
                "id": account.get("id"),
                "name": account.get("name"),
                "phone": account.get("phone"),
                "balance": balance,
                "days_old": days_old,
                "bucket": bucket,
                "last_transaction": last_txn
            })
        
        # Sort by amount descending
        detailed_aging.sort(key=lambda x: x["balance"], reverse=True)
        
        return {
            "status": "success",
            "account_type": account_type,
            "summary": aging_summary,
            "total_amount": sum(s["amount"] for s in aging_summary.values()),
            "total_accounts": len(detailed_aging),
            "details": detailed_aging
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ PAYMENTS ============

@router.post("/payments/receive")
async def receive_payment(payment: PaymentCreate, db = Depends(get_db)):
    """Record payment received from customer"""
    try:
        ledger = await db.ledgers.find_one({"id": payment.ledger_id})
        if not ledger:
            raise HTTPException(status_code=404, detail="Customer account not found")
        
        now = datetime.now(timezone.utc).isoformat()
        payment_date = payment.payment_date or now
        payment_id = str(uuid.uuid4())
        
        # Create payment record
        payment_data = {
            "id": payment_id,
            "payment_type": "receipt",  # receipt from customer
            "ledger_id": payment.ledger_id,
            "ledger_name": ledger.get("name"),
            "amount": payment.amount,
            "payment_mode": payment.payment_mode,
            "payment_date": payment_date,
            "reference_number": payment.reference_number,
            "bank_account_id": payment.bank_account_id,
            "narration": payment.narration or f"Payment received from {ledger.get('name')}",
            "allocations": payment.allocations,
            "status": "completed",
            "created_at": now
        }
        
        await db.payments.insert_one(payment_data)
        
        # Create ledger transaction (credit entry for receipt)
        await db.ledger_transactions.insert_one({
            "id": str(uuid.uuid4()),
            "ledger_id": payment.ledger_id,
            "ledger_name": ledger.get("name"),
            "transaction_type": "receipt",
            "reference_type": "payment",
            "reference_id": payment_id,
            "reference_number": payment.reference_number or payment_id[:8],
            "debit_amount": 0,
            "credit_amount": payment.amount,
            "balance_after": ledger.get("current_balance", 0) - payment.amount,
            "narration": payment.narration or f"Payment received - {payment.payment_mode}",
            "transaction_date": payment_date,
            "created_at": now
        })
        
        # Update ledger balance
        new_credit = ledger.get("current_credit", 0) + payment.amount
        new_balance = ledger.get("current_debit", 0) - new_credit
        
        await db.ledgers.update_one(
            {"id": payment.ledger_id},
            {"$set": {
                "current_credit": new_credit,
                "current_balance": new_balance,
                "last_transaction_date": payment_date,
                "updated_at": now
            },
            "$inc": {"total_transactions": 1}}
        )
        
        # Update invoice payment status if allocations provided
        for alloc in (payment.allocations or []):
            if alloc.get("invoice_id"):
                await db.orders.update_one(
                    {"id": alloc["invoice_id"]},
                    {"$set": {"payment_status": "paid", "updated_at": now}}
                )
        
        return {
            "status": "success",
            "message": f"Payment of ₹{payment.amount} received from {ledger.get('name')}",
            "payment_id": payment_id,
            "new_balance": new_balance
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Receive payment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payments/make")
async def make_payment(payment: PaymentCreate, db = Depends(get_db)):
    """Record payment made to vendor"""
    try:
        ledger = await db.ledgers.find_one({"id": payment.ledger_id})
        if not ledger:
            raise HTTPException(status_code=404, detail="Vendor account not found")
        
        now = datetime.now(timezone.utc).isoformat()
        payment_date = payment.payment_date or now
        payment_id = str(uuid.uuid4())
        
        # Create payment record
        payment_data = {
            "id": payment_id,
            "payment_type": "payment",  # payment to vendor
            "ledger_id": payment.ledger_id,
            "ledger_name": ledger.get("name"),
            "amount": payment.amount,
            "payment_mode": payment.payment_mode,
            "payment_date": payment_date,
            "reference_number": payment.reference_number,
            "bank_account_id": payment.bank_account_id,
            "narration": payment.narration or f"Payment made to {ledger.get('name')}",
            "allocations": payment.allocations,
            "status": "completed",
            "created_at": now
        }
        
        await db.payments.insert_one(payment_data)
        
        # Create ledger transaction (debit entry for payment)
        await db.ledger_transactions.insert_one({
            "id": str(uuid.uuid4()),
            "ledger_id": payment.ledger_id,
            "ledger_name": ledger.get("name"),
            "transaction_type": "payment",
            "reference_type": "payment",
            "reference_id": payment_id,
            "reference_number": payment.reference_number or payment_id[:8],
            "debit_amount": payment.amount,
            "credit_amount": 0,
            "balance_after": ledger.get("current_balance", 0) + payment.amount,
            "narration": payment.narration or f"Payment made - {payment.payment_mode}",
            "transaction_date": payment_date,
            "created_at": now
        })
        
        # Update ledger balance
        new_debit = ledger.get("current_debit", 0) + payment.amount
        new_balance = new_debit - ledger.get("current_credit", 0)
        
        await db.ledgers.update_one(
            {"id": payment.ledger_id},
            {"$set": {
                "current_debit": new_debit,
                "current_balance": new_balance,
                "last_transaction_date": payment_date,
                "updated_at": now
            },
            "$inc": {"total_transactions": 1}}
        )
        
        # Update purchase bill payment status if allocations provided
        for alloc in (payment.allocations or []):
            if alloc.get("bill_id"):
                await db.purchase_bills.update_one(
                    {"id": alloc["bill_id"]},
                    {"$set": {"payment_status": "paid", "updated_at": now}}
                )
        
        return {
            "status": "success",
            "message": f"Payment of ₹{payment.amount} made to {ledger.get('name')}",
            "payment_id": payment_id,
            "new_balance": new_balance
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Make payment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payments")
async def get_payments(
    payment_type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get all payments with filters"""
    try:
        query = {}
        
        if payment_type:
            query["payment_type"] = payment_type
        
        if from_date:
            query["payment_date"] = {"$gte": from_date}
        if to_date:
            if "payment_date" in query:
                query["payment_date"]["$lte"] = to_date
            else:
                query["payment_date"] = {"$lte": to_date}
        
        skip = (page - 1) * limit
        
        payments = await db.payments.find(query, {"_id": 0}).sort("payment_date", -1).skip(skip).limit(limit).to_list(length=limit)
        total = await db.payments.count_documents(query)
        
        return {
            "status": "success",
            "payments": payments,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ SYNC FROM EXISTING DATA ============

@router.post("/sync/customers")
async def sync_customers_to_ledger(db = Depends(get_db)):
    """Create ledger accounts from existing customers"""
    try:
        customers = await db.customers.find({}).to_list(length=1000)
        created = 0
        skipped = 0
        
        for customer in customers:
            # Check if ledger exists
            existing = await db.ledgers.find_one({
                "phone": customer.get("phone"),
                "account_type": "customer"
            })
            
            if existing:
                skipped += 1
                continue
            
            # Create ledger
            now = datetime.now(timezone.utc).isoformat()
            await db.ledgers.insert_one({
                "id": str(uuid.uuid4()),
                "name": customer.get("name", "Unknown"),
                "account_type": "customer",
                "phone": customer.get("phone", ""),
                "email": customer.get("email", ""),
                "gst_number": customer.get("gst_number", ""),
                "address": customer.get("address", ""),
                "city": customer.get("city", ""),
                "state": customer.get("state", ""),
                "pincode": customer.get("pincode", ""),
                "credit_limit": 0,
                "credit_days": 30,
                "opening_balance": 0,
                "current_debit": 0,
                "current_credit": 0,
                "current_balance": 0,
                "total_transactions": 0,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
                "synced_from": "customers"
            })
            created += 1
        
        return {
            "status": "success",
            "message": f"Synced {created} customers to ledger, {skipped} already existed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/vendors")
async def sync_vendors_to_ledger(db = Depends(get_db)):
    """Create ledger accounts from purchase bills vendors"""
    try:
        # Get unique vendors from purchase bills
        pipeline = [
            {"$group": {
                "_id": "$vendor.name",
                "vendor": {"$first": "$vendor"},
                "total_bills": {"$sum": 1},
                "total_amount": {"$sum": "$grand_total"}
            }}
        ]
        
        vendors = await db.purchase_bills.aggregate(pipeline).to_list(length=500)
        created = 0
        skipped = 0
        
        for v in vendors:
            vendor = v.get("vendor", {})
            vendor_name = vendor.get("name", v.get("_id"))
            
            if not vendor_name:
                continue
            
            # Check if exists
            existing = await db.ledgers.find_one({
                "name": {"$regex": f"^{vendor_name}$", "$options": "i"},
                "account_type": "vendor"
            })
            
            if existing:
                skipped += 1
                continue
            
            now = datetime.now(timezone.utc).isoformat()
            await db.ledgers.insert_one({
                "id": str(uuid.uuid4()),
                "name": vendor_name,
                "account_type": "vendor",
                "phone": vendor.get("phone", ""),
                "email": vendor.get("email", ""),
                "gst_number": vendor.get("gst_number", ""),
                "address": vendor.get("address", ""),
                "city": vendor.get("city", ""),
                "state": vendor.get("state", ""),
                "pincode": vendor.get("pincode", ""),
                "credit_limit": 0,
                "credit_days": 30,
                "opening_balance": 0,
                "current_debit": 0,
                "current_credit": 0,
                "current_balance": 0,
                "total_transactions": 0,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
                "synced_from": "purchase_bills"
            })
            created += 1
        
        return {
            "status": "success",
            "message": f"Synced {created} vendors to ledger, {skipped} already existed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ DASHBOARD STATS ============

@router.get("/dashboard/stats")
async def get_ledger_dashboard_stats(db = Depends(get_db)):
    """Get dashboard statistics for ledger management"""
    try:
        # Customer stats
        customer_pipeline = [
            {"$match": {"account_type": "customer", "is_active": True}},
            {"$group": {
                "_id": None,
                "total_customers": {"$sum": 1},
                "total_receivable": {"$sum": {"$cond": [{"$gt": ["$current_balance", 0]}, "$current_balance", 0]}},
                "customers_with_balance": {"$sum": {"$cond": [{"$gt": ["$current_balance", 0]}, 1, 0]}}
            }}
        ]
        customer_stats = await db.ledgers.aggregate(customer_pipeline).to_list(length=1)
        
        # Vendor stats
        vendor_pipeline = [
            {"$match": {"account_type": "vendor", "is_active": True}},
            {"$group": {
                "_id": None,
                "total_vendors": {"$sum": 1},
                "total_payable": {"$sum": {"$cond": [{"$lt": ["$current_balance", 0]}, {"$abs": "$current_balance"}, 0]}},
                "vendors_with_balance": {"$sum": {"$cond": [{"$lt": ["$current_balance", 0]}, 1, 0]}}
            }}
        ]
        vendor_stats = await db.ledgers.aggregate(vendor_pipeline).to_list(length=1)
        
        # Recent payments
        recent_payments = await db.payments.find({}, {"_id": 0}).sort("created_at", -1).limit(5).to_list(length=5)
        
        return {
            "status": "success",
            "stats": {
                "customers": customer_stats[0] if customer_stats else {"total_customers": 0, "total_receivable": 0},
                "vendors": vendor_stats[0] if vendor_stats else {"total_vendors": 0, "total_payable": 0},
                "recent_payments": recent_payments
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
