from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from database import get_db
import uuid

router = APIRouter(prefix="/expenses", tags=["Expenses"])

class ExpenseEntry(BaseModel):
    category: str
    amount: float
    payment_mode: str
    vendor_name: Optional[str] = None
    description: str
    expense_date: str
    created_by: str
    notes: Optional[str] = None

@router.post("/create")
async def create_expense(expense: ExpenseEntry, db = Depends(get_db)):
    """Create new expense entry"""
    try:
        today = datetime.now(timezone.utc)
        exp_prefix = f"EXP-{today.strftime('%Y%m%d')}"
        
        count = await db.expenses.count_documents({
            "created_at": {
                "$gte": today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            }
        })
        
        expense_number = f"{exp_prefix}-{count + 1:04d}"
        
        expense_data = {
            "id": str(uuid.uuid4()),
            "expense_number": expense_number,
            **expense.dict(),
            "status": "recorded",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.expenses.insert_one(expense_data)
        
        return {
            "status": "success",
            "expense_number": expense_number,
            "expense_id": expense_data["id"],
            "message": "Expense recorded successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create expense: {str(e)}")

@router.get("/")
async def get_expenses(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get all expenses with filters"""
    try:
        query = {}
        
        if from_date and to_date:
            query["expense_date"] = {"$gte": from_date, "$lte": to_date}
        
        if category:
            query["category"] = category
        
        skip = (page - 1) * limit
        
        expenses = await db.expenses.find(
            query,
            {"_id": 0}
        ).sort("expense_date", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.expenses.count_documents(query)
        
        # Calculate total amount
        pipeline = [{"$match": query}, {"$group": {"_id": None, "total": {"$sum": "$amount"}}}]
        result = await db.expenses.aggregate(pipeline).to_list(1)
        total_amount = result[0]["total"] if result else 0
        
        return {
            "status": "success",
            "expenses": expenses,
            "total": total,
            "total_amount": total_amount,
            "page": page,
            "limit": limit
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch expenses: {str(e)}")

@router.get("/categories")
async def get_expense_categories(db = Depends(get_db)):
    """Get all expense categories"""
    try:
        categories = await db.expenses.distinct("category")
        return {"status": "success", "categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch categories: {str(e)}")
