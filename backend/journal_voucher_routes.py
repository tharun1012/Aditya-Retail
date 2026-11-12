"""
Journal Voucher Routes
Manual journal entries for adjustments, contra entries, and corrections
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from database import get_db
import uuid
import logging

router = APIRouter(prefix="/journal-vouchers", tags=["Journal Vouchers"])
logger = logging.getLogger(__name__)


# ============ MODELS ============

class JournalEntry(BaseModel):
    ledger_id: str
    ledger_name: str
    debit: float = 0
    credit: float = 0


class JournalVoucherCreate(BaseModel):
    voucher_date: str
    narration: str
    entries: List[JournalEntry]


# ============ HELPERS ============

async def generate_voucher_number(db) -> str:
    """Generate sequential journal voucher number"""
    today = datetime.now(timezone.utc)
    prefix = f"JV-{today.strftime('%Y%m')}-"
    
    # Find last voucher number this month
    last_voucher = await db.journal_vouchers.find_one(
        {"voucher_number": {"$regex": f"^{prefix}"}},
        sort=[("voucher_number", -1)]
    )
    
    if last_voucher:
        try:
            last_num = int(last_voucher["voucher_number"].split("-")[-1])
            next_num = last_num + 1
        except Exception:
            next_num = 1
    else:
        next_num = 1
    
    return f"{prefix}{next_num:04d}"


# ============ ROUTES ============

@router.post("/create")
async def create_journal_voucher(voucher: JournalVoucherCreate, db = Depends(get_db)):
    """Create a new journal voucher with multiple entries"""
    try:
        # Validate entries
        if len(voucher.entries) < 2:
            raise HTTPException(status_code=400, detail="Minimum 2 entries required")
        
        # Calculate totals
        total_debit = sum(e.debit for e in voucher.entries)
        total_credit = sum(e.credit for e in voucher.entries)
        
        # Check if balanced
        if abs(total_debit - total_credit) > 0.01:
            raise HTTPException(
                status_code=400, 
                detail=f"Voucher not balanced. Debit: {total_debit}, Credit: {total_credit}"
            )
        
        if total_debit == 0:
            raise HTTPException(status_code=400, detail="Total amount cannot be zero")
        
        # Verify all ledgers exist
        for entry in voucher.entries:
            ledger = await db.ledgers.find_one({"id": entry.ledger_id})
            if not ledger:
                raise HTTPException(status_code=404, detail=f"Ledger not found: {entry.ledger_id}")
        
        now = datetime.now(timezone.utc).isoformat()
        voucher_id = str(uuid.uuid4())
        voucher_number = await generate_voucher_number(db)
        
        # Create voucher record
        voucher_data = {
            "id": voucher_id,
            "voucher_number": voucher_number,
            "voucher_date": voucher.voucher_date,
            "narration": voucher.narration,
            "entries": [e.dict() for e in voucher.entries],
            "total_amount": total_debit,
            "status": "posted",
            "is_locked": True,  # Vouchers are locked by default
            "created_at": now,
            "updated_at": now
        }
        
        await db.journal_vouchers.insert_one(voucher_data)

        try:
            from realtime_accounting import post_transaction_event
            await post_transaction_event(db, "journal_voucher", {
                "id": voucher_data["voucher_number"],
                "amount": voucher_data["total_amount"],
                "tax": 0,
                "payment_method": "n/a",
                "payment_status": voucher_data.get("status", "posted"),
                "date": voucher_data["created_at"],
                "description": voucher_data.get("narration", "")
            })
        except Exception as e:
            print(f"⚠️ Real-time accounting failed for {voucher_data['voucher_number']}: {e}")

        # Create ledger transactions for each entry
        for entry in voucher.entries:
            # Get ledger for balance calculation
            ledger = await db.ledgers.find_one({"id": entry.ledger_id})
            
            # Calculate new balance
            current_debit = ledger.get("current_debit", 0)
            current_credit = ledger.get("current_credit", 0)
            
            new_debit = current_debit + entry.debit
            new_credit = current_credit + entry.credit
            new_balance = new_debit - new_credit
            
            # Create transaction
            await db.ledger_transactions.insert_one({
                "id": str(uuid.uuid4()),
                "ledger_id": entry.ledger_id,
                "ledger_name": entry.ledger_name,
                "transaction_type": "journal",
                "reference_type": "journal_voucher",
                "reference_id": voucher_id,
                "reference_number": voucher_number,
                "debit_amount": entry.debit,
                "credit_amount": entry.credit,
                "balance_after": new_balance,
                "narration": voucher.narration,
                "transaction_date": voucher.voucher_date,
                "created_at": now
            })
            
            # Update ledger balance
            await db.ledgers.update_one(
                {"id": entry.ledger_id},
                {"$set": {
                    "current_debit": new_debit,
                    "current_credit": new_credit,
                    "current_balance": new_balance,
                    "last_transaction_date": voucher.voucher_date,
                    "updated_at": now
                },
                "$inc": {"total_transactions": 1}}
            )
        
        logger.info(f"Created journal voucher {voucher_number}")
        
        return {
            "status": "success",
            "message": f"Journal voucher {voucher_number} created successfully",
            "voucher_id": voucher_id,
            "voucher_number": voucher_number
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create journal voucher failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def get_journal_vouchers(
    search: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    db = Depends(get_db)
):
    """Get all journal vouchers with filters"""
    try:
        query = {}
        
        if search:
            query["$or"] = [
                {"voucher_number": {"$regex": search, "$options": "i"}},
                {"narration": {"$regex": search, "$options": "i"}}
            ]
        
        if from_date:
            query["voucher_date"] = {"$gte": from_date}
        if to_date:
            if "voucher_date" in query:
                query["voucher_date"]["$lte"] = to_date
            else:
                query["voucher_date"] = {"$lte": to_date}
        
        skip = (page - 1) * limit
        
        vouchers = await db.journal_vouchers.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
        total = await db.journal_vouchers.count_documents(query)
        
        return {
            "status": "success",
            "vouchers": vouchers,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Get journal vouchers failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{voucher_id}")
async def get_journal_voucher(voucher_id: str, db = Depends(get_db)):
    """Get single journal voucher details"""
    try:
        voucher = await db.journal_vouchers.find_one({"id": voucher_id}, {"_id": 0})
        if not voucher:
            raise HTTPException(status_code=404, detail="Voucher not found")
        
        return {"status": "success", "voucher": voucher}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{voucher_id}")
async def delete_journal_voucher(voucher_id: str, db = Depends(get_db)):
    """Delete journal voucher and reverse all ledger entries"""
    try:
        voucher = await db.journal_vouchers.find_one({"id": voucher_id})
        if not voucher:
            raise HTTPException(status_code=404, detail="Voucher not found")
        
        now = datetime.now(timezone.utc).isoformat()
        
        # Reverse each ledger entry
        for entry in voucher.get("entries", []):
            ledger = await db.ledgers.find_one({"id": entry["ledger_id"]})
            if ledger:
                # Reverse the amounts (debit becomes credit and vice versa)
                current_debit = ledger.get("current_debit", 0)
                current_credit = ledger.get("current_credit", 0)
                
                new_debit = current_debit - entry.get("debit", 0)
                new_credit = current_credit - entry.get("credit", 0)
                new_balance = new_debit - new_credit
                
                # Create reversal transaction
                await db.ledger_transactions.insert_one({
                    "id": str(uuid.uuid4()),
                    "ledger_id": entry["ledger_id"],
                    "ledger_name": entry.get("ledger_name"),
                    "transaction_type": "journal_reversal",
                    "reference_type": "journal_voucher",
                    "reference_id": voucher_id,
                    "reference_number": f"REV-{voucher.get('voucher_number')}",
                    "debit_amount": entry.get("credit", 0),  # Reverse
                    "credit_amount": entry.get("debit", 0),  # Reverse
                    "balance_after": new_balance,
                    "narration": f"Reversal of {voucher.get('voucher_number')}",
                    "transaction_date": now,
                    "created_at": now
                })
                
                # Update ledger balance
                await db.ledgers.update_one(
                    {"id": entry["ledger_id"]},
                    {"$set": {
                        "current_debit": new_debit,
                        "current_credit": new_credit,
                        "current_balance": new_balance,
                        "updated_at": now
                    },
                    "$inc": {"total_transactions": 1}}
                )
        
        # Mark voucher as reversed (or delete it)
        await db.journal_vouchers.update_one(
            {"id": voucher_id},
            {"$set": {"status": "reversed", "reversed_at": now}}
        )
        
        logger.info(f"Reversed journal voucher {voucher.get('voucher_number')}")
        
        return {
            "status": "success",
            "message": f"Journal voucher {voucher.get('voucher_number')} reversed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete journal voucher failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ STATISTICS ============

@router.get("/stats/summary")
async def get_journal_stats(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Get journal voucher statistics"""
    try:
        query = {"status": "posted"}
        
        if from_date:
            query["voucher_date"] = {"$gte": from_date}
        if to_date:
            if "voucher_date" in query:
                query["voucher_date"]["$lte"] = to_date
            else:
                query["voucher_date"] = {"$lte": to_date}
        
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": None,
                "total_vouchers": {"$sum": 1},
                "total_amount": {"$sum": "$total_amount"}
            }}
        ]
        
        result = await db.journal_vouchers.aggregate(pipeline).to_list(length=1)
        stats = result[0] if result else {"total_vouchers": 0, "total_amount": 0}
        
        # Get recent vouchers
        recent = await db.journal_vouchers.find(
            {"status": "posted"},
            {"_id": 0}
        ).sort("created_at", -1).limit(5).to_list(length=5)
        
        return {
            "status": "success",
            "stats": {
                "total_vouchers": stats.get("total_vouchers", 0),
                "total_amount": stats.get("total_amount", 0),
                "recent_vouchers": recent
            }
        }
        
    except Exception as e:
        logger.error(f"Get journal stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
