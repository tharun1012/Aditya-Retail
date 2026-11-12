"""
Bank Reconciliation Routes
Match bank statements with ledger transactions for accurate financial tracking
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from database import get_db
import uuid
import logging
import csv
import io

router = APIRouter(prefix="/bank-reconciliation", tags=["Bank Reconciliation"])
logger = logging.getLogger(__name__)


# ============ MODELS ============

class BankAccountCreate(BaseModel):
    name: str
    account_number: str
    bank_name: str
    ifsc_code: Optional[str] = ""
    branch: Optional[str] = ""
    account_type: str = "current"  # current, savings
    opening_balance: float = 0
    as_of_date: Optional[str] = None


class BankTransactionCreate(BaseModel):
    bank_account_id: str
    transaction_date: str
    description: str
    reference_number: Optional[str] = ""
    debit_amount: float = 0
    credit_amount: float = 0
    transaction_type: str  # deposit, withdrawal, transfer, charge, interest


class ReconciliationMatchCreate(BaseModel):
    bank_transaction_id: str
    ledger_transaction_id: str
    match_type: str = "exact"  # exact, partial, manual


# ============ BANK ACCOUNTS ============

@router.post("/accounts/create")
async def create_bank_account(account: BankAccountCreate, db = Depends(get_db)):
    """Create a new bank account for reconciliation"""
    try:
        # Check for duplicate
        existing = await db.bank_accounts.find_one({
            "account_number": account.account_number,
            "bank_name": account.bank_name
        })
        if existing:
            raise HTTPException(status_code=400, detail="Bank account already exists")
        
        account_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        as_of = account.as_of_date or now
        
        bank_data = {
            "id": account_id,
            "name": account.name,
            "account_number": account.account_number,
            "bank_name": account.bank_name,
            "ifsc_code": account.ifsc_code,
            "branch": account.branch,
            "account_type": account.account_type,
            "opening_balance": account.opening_balance,
            "current_balance": account.opening_balance,
            "as_of_date": as_of,
            "last_reconciled_date": None,
            "last_reconciled_balance": None,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
        
        await db.bank_accounts.insert_one(bank_data)
        
        # Also create a ledger account for this bank
        await db.ledgers.insert_one({
            "id": str(uuid.uuid4()),
            "name": f"{account.bank_name} - {account.account_number[-4:]}",
            "account_type": "bank",
            "bank_account_id": account_id,
            "phone": "",
            "email": "",
            "opening_balance": account.opening_balance,
            "current_debit": account.opening_balance if account.opening_balance > 0 else 0,
            "current_credit": abs(account.opening_balance) if account.opening_balance < 0 else 0,
            "current_balance": account.opening_balance,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        })
        
        return {
            "status": "success",
            "message": f"Bank account '{account.name}' created",
            "account_id": account_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create bank account failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts")
async def get_bank_accounts(db = Depends(get_db)):
    """Get all bank accounts"""
    try:
        accounts = await db.bank_accounts.find(
            {"is_active": True}, 
            {"_id": 0}
        ).sort("name", 1).to_list(length=100)
        
        # Calculate unreconciled count for each account
        for account in accounts:
            unreconciled = await db.bank_transactions.count_documents({
                "bank_account_id": account["id"],
                "is_reconciled": {"$ne": True}
            })
            account["unreconciled_count"] = unreconciled
        
        return {"status": "success", "accounts": accounts}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts/{account_id}")
async def get_bank_account(account_id: str, db = Depends(get_db)):
    """Get bank account details"""
    try:
        account = await db.bank_accounts.find_one({"id": account_id}, {"_id": 0})
        if not account:
            raise HTTPException(status_code=404, detail="Bank account not found")
        
        # Get recent transactions
        transactions = await db.bank_transactions.find(
            {"bank_account_id": account_id},
            {"_id": 0}
        ).sort("transaction_date", -1).limit(50).to_list(length=50)
        
        return {
            "status": "success",
            "account": account,
            "recent_transactions": transactions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ BANK TRANSACTIONS ============

@router.post("/transactions/create")
async def create_bank_transaction(txn: BankTransactionCreate, db = Depends(get_db)):
    """Record a bank transaction"""
    try:
        account = await db.bank_accounts.find_one({"id": txn.bank_account_id})
        if not account:
            raise HTTPException(status_code=404, detail="Bank account not found")
        
        now = datetime.now(timezone.utc).isoformat()
        txn_id = str(uuid.uuid4())
        
        # Calculate new balance
        amount = txn.credit_amount - txn.debit_amount
        new_balance = account.get("current_balance", 0) + amount
        
        txn_data = {
            "id": txn_id,
            "bank_account_id": txn.bank_account_id,
            "transaction_date": txn.transaction_date,
            "description": txn.description,
            "reference_number": txn.reference_number,
            "debit_amount": txn.debit_amount,
            "credit_amount": txn.credit_amount,
            "balance_after": new_balance,
            "transaction_type": txn.transaction_type,
            "is_reconciled": False,
            "matched_ledger_id": None,
            "created_at": now
        }
        
        await db.bank_transactions.insert_one(txn_data)
        
        # Update bank account balance
        await db.bank_accounts.update_one(
            {"id": txn.bank_account_id},
            {"$set": {"current_balance": new_balance, "updated_at": now}}
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
        logger.error(f"Create bank transaction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transactions/import")
async def import_bank_statement(
    bank_account_id: str,
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    """Import bank statement from CSV"""
    try:
        account = await db.bank_accounts.find_one({"id": bank_account_id})
        if not account:
            raise HTTPException(status_code=404, detail="Bank account not found")
        
        # Read CSV
        content = await file.read()
        csv_text = content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(csv_text))
        
        imported = 0
        skipped = 0
        now = datetime.now(timezone.utc).isoformat()
        
        for row in reader:
            try:
                # Flexible column mapping
                date_str = row.get('Date', row.get('Transaction Date', row.get('Value Date', '')))
                description = row.get('Description', row.get('Narration', row.get('Particulars', '')))
                debit = float(row.get('Debit', row.get('Withdrawal', row.get('Dr', 0))) or 0)
                credit = float(row.get('Credit', row.get('Deposit', row.get('Cr', 0))) or 0)
                ref = row.get('Reference', row.get('Ref No', row.get('Chq No', '')))
                
                if not date_str or not description:
                    skipped += 1
                    continue
                
                # Check for duplicate
                existing = await db.bank_transactions.find_one({
                    "bank_account_id": bank_account_id,
                    "transaction_date": date_str,
                    "description": description,
                    "debit_amount": debit,
                    "credit_amount": credit
                })
                
                if existing:
                    skipped += 1
                    continue
                
                await db.bank_transactions.insert_one({
                    "id": str(uuid.uuid4()),
                    "bank_account_id": bank_account_id,
                    "transaction_date": date_str,
                    "description": description,
                    "reference_number": ref,
                    "debit_amount": debit,
                    "credit_amount": credit,
                    "transaction_type": "deposit" if credit > 0 else "withdrawal",
                    "is_reconciled": False,
                    "matched_ledger_id": None,
                    "created_at": now,
                    "imported": True
                })
                imported += 1
                
            except Exception as e:
                logger.warning(f"Skipped row due to error: {e}")
                skipped += 1
        
        return {
            "status": "success",
            "message": f"Imported {imported} transactions, skipped {skipped}",
            "imported": imported,
            "skipped": skipped
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Import bank statement failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/{account_id}")
async def get_bank_transactions(
    account_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    reconciled: Optional[bool] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get bank transactions for reconciliation"""
    try:
        query = {"bank_account_id": account_id}
        
        if from_date:
            query["transaction_date"] = {"$gte": from_date}
        if to_date:
            if "transaction_date" in query:
                query["transaction_date"]["$lte"] = to_date
            else:
                query["transaction_date"] = {"$lte": to_date}
        
        if reconciled is not None:
            query["is_reconciled"] = reconciled
        
        skip = (page - 1) * limit
        
        transactions = await db.bank_transactions.find(query, {"_id": 0}).sort("transaction_date", -1).skip(skip).limit(limit).to_list(length=limit)
        total = await db.bank_transactions.count_documents(query)
        
        return {
            "status": "success",
            "transactions": transactions,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ RECONCILIATION ============

@router.get("/suggestions/{account_id}")
async def get_reconciliation_suggestions(
    account_id: str,
    db = Depends(get_db)
):
    """Get auto-match suggestions for unreconciled transactions"""
    try:
        # Get unreconciled bank transactions
        bank_txns = await db.bank_transactions.find({
            "bank_account_id": account_id,
            "is_reconciled": {"$ne": True}
        }, {"_id": 0}).to_list(length=100)
        
        suggestions = []
        
        for bank_txn in bank_txns:
            amount = bank_txn.get("credit_amount", 0) - bank_txn.get("debit_amount", 0)
            
            # Find matching ledger transactions by amount
            ledger_matches = await db.ledger_transactions.find({
                "$or": [
                    {"debit_amount": abs(amount), "credit_amount": 0} if amount < 0 else {"credit_amount": abs(amount), "debit_amount": 0},
                    {"credit_amount": abs(amount), "debit_amount": 0} if amount > 0 else {"debit_amount": abs(amount), "credit_amount": 0}
                ],
                "is_reconciled": {"$ne": True}
            }, {"_id": 0}).limit(5).to_list(length=5)
            
            if ledger_matches:
                suggestions.append({
                    "bank_transaction": bank_txn,
                    "suggested_matches": ledger_matches,
                    "match_confidence": "high" if len(ledger_matches) == 1 else "medium"
                })
        
        return {
            "status": "success",
            "suggestions": suggestions,
            "total_unreconciled": len(bank_txns)
        }
        
    except Exception as e:
        logger.error(f"Get suggestions failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/match")
async def match_transactions(match: ReconciliationMatchCreate, db = Depends(get_db)):
    """Match a bank transaction with a ledger transaction"""
    try:
        bank_txn = await db.bank_transactions.find_one({"id": match.bank_transaction_id})
        if not bank_txn:
            raise HTTPException(status_code=404, detail="Bank transaction not found")
        
        ledger_txn = await db.ledger_transactions.find_one({"id": match.ledger_transaction_id})
        if not ledger_txn:
            raise HTTPException(status_code=404, detail="Ledger transaction not found")
        
        now = datetime.now(timezone.utc).isoformat()
        
        # Mark both as reconciled
        await db.bank_transactions.update_one(
            {"id": match.bank_transaction_id},
            {"$set": {
                "is_reconciled": True,
                "matched_ledger_id": match.ledger_transaction_id,
                "match_type": match.match_type,
                "reconciled_at": now
            }}
        )
        
        await db.ledger_transactions.update_one(
            {"id": match.ledger_transaction_id},
            {"$set": {
                "is_reconciled": True,
                "matched_bank_id": match.bank_transaction_id,
                "reconciled_at": now
            }}
        )
        
        return {
            "status": "success",
            "message": "Transactions matched successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Match transactions failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unmatch/{bank_transaction_id}")
async def unmatch_transaction(bank_transaction_id: str, db = Depends(get_db)):
    """Unmatch a reconciled transaction"""
    try:
        bank_txn = await db.bank_transactions.find_one({"id": bank_transaction_id})
        if not bank_txn:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        matched_ledger_id = bank_txn.get("matched_ledger_id")
        
        # Clear reconciliation from bank transaction
        await db.bank_transactions.update_one(
            {"id": bank_transaction_id},
            {"$set": {
                "is_reconciled": False,
                "matched_ledger_id": None,
                "match_type": None,
                "reconciled_at": None
            }}
        )
        
        # Clear reconciliation from ledger transaction if exists
        if matched_ledger_id:
            await db.ledger_transactions.update_one(
                {"id": matched_ledger_id},
                {"$set": {
                    "is_reconciled": False,
                    "matched_bank_id": None,
                    "reconciled_at": None
                }}
            )
        
        return {"status": "success", "message": "Transaction unmatched"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ RECONCILIATION SUMMARY ============

@router.get("/summary/{account_id}")
async def get_reconciliation_summary(account_id: str, db = Depends(get_db)):
    """Get reconciliation summary for a bank account"""
    try:
        account = await db.bank_accounts.find_one({"id": account_id}, {"_id": 0})
        if not account:
            raise HTTPException(status_code=404, detail="Bank account not found")
        
        # Bank side
        bank_balance = account.get("current_balance", 0)
        
        # Unreconciled in bank
        unreconciled_bank = await db.bank_transactions.aggregate([
            {"$match": {"bank_account_id": account_id, "is_reconciled": {"$ne": True}}},
            {"$group": {
                "_id": None,
                "total_credit": {"$sum": "$credit_amount"},
                "total_debit": {"$sum": "$debit_amount"},
                "count": {"$sum": 1}
            }}
        ]).to_list(length=1)
        
        # Unreconciled in books (ledger)
        ledger_account = await db.ledgers.find_one({"bank_account_id": account_id})
        ledger_balance = ledger_account.get("current_balance", 0) if ledger_account else 0
        
        unreconciled_ledger = await db.ledger_transactions.aggregate([
            {"$match": {"ledger_id": ledger_account.get("id") if ledger_account else "", "is_reconciled": {"$ne": True}}},
            {"$group": {
                "_id": None,
                "total_debit": {"$sum": "$debit_amount"},
                "total_credit": {"$sum": "$credit_amount"},
                "count": {"$sum": 1}
            }}
        ]).to_list(length=1)
        
        bank_unreconciled = unreconciled_bank[0] if unreconciled_bank else {"total_credit": 0, "total_debit": 0, "count": 0}
        ledger_unreconciled = unreconciled_ledger[0] if unreconciled_ledger else {"total_debit": 0, "total_credit": 0, "count": 0}
        
        # Calculate difference
        difference = bank_balance - ledger_balance
        
        return {
            "status": "success",
            "account": account,
            "bank_balance": bank_balance,
            "ledger_balance": ledger_balance,
            "difference": difference,
            "unreconciled_bank": {
                "count": bank_unreconciled.get("count", 0),
                "credits": bank_unreconciled.get("total_credit", 0),
                "debits": bank_unreconciled.get("total_debit", 0)
            },
            "unreconciled_ledger": {
                "count": ledger_unreconciled.get("count", 0),
                "debits": ledger_unreconciled.get("total_debit", 0),
                "credits": ledger_unreconciled.get("total_credit", 0)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get reconciliation summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/finalize/{account_id}")
async def finalize_reconciliation(
    account_id: str,
    reconciled_balance: float,
    as_of_date: str,
    db = Depends(get_db)
):
    """Finalize reconciliation for a period"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        
        # Update bank account
        await db.bank_accounts.update_one(
            {"id": account_id},
            {"$set": {
                "last_reconciled_date": as_of_date,
                "last_reconciled_balance": reconciled_balance,
                "updated_at": now
            }}
        )
        
        # Create reconciliation record
        await db.reconciliation_history.insert_one({
            "id": str(uuid.uuid4()),
            "bank_account_id": account_id,
            "reconciled_date": as_of_date,
            "reconciled_balance": reconciled_balance,
            "reconciled_by": "admin",  # TODO: Get from auth
            "created_at": now
        })
        
        return {
            "status": "success",
            "message": f"Reconciliation finalized as of {as_of_date}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
