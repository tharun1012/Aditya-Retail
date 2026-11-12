"""
New Product Highlighting
Mark and showcase new products on homepage
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from database import get_db

router = APIRouter(prefix="/new-products", tags=["New Products"])

class NewProductMark(BaseModel):
    product_id: str
    highlight_until: Optional[str] = None  # If not set, highlight for 30 days
    badge_text: Optional[str] = "NEW"
    priority: Optional[int] = 0  # Higher priority shows first

@router.post("/mark")
async def mark_as_new_product(data: NewProductMark, db = Depends(get_db)):
    """Mark a product as new"""
    try:
        # Check if product exists
        product = await db.products.find_one({"id": data.product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Set highlight_until to 30 days from now if not provided
        if not data.highlight_until:
            highlight_until = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        else:
            highlight_until = data.highlight_until
        
        # Update product
        await db.products.update_one(
            {"id": data.product_id},
            {"$set": {
                "is_new": True,
                "new_badge_text": data.badge_text,
                "new_priority": data.priority,
                "new_until": highlight_until,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        updated_product = await db.products.find_one({"id": data.product_id}, {"_id": 0})
        
        return {
            "status": "success",
            "message": "Product marked as new",
            "product": updated_product
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking product as new: {str(e)}")

@router.get("/")
async def get_new_products(limit: int = 10, db = Depends(get_db)):
    """Get all new products"""
    try:
        current_date = datetime.now(timezone.utc).isoformat()
        
        # Get products marked as new and still within highlight period
        products = await db.products.find({
            "is_new": True,
            "new_until": {"$gte": current_date}
        }, {"_id": 0}).sort([("new_priority", -1), ("created_at", -1)]).limit(limit).to_list(limit)
        
        return {
            "status": "success",
            "total": len(products),
            "products": products
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching new products: {str(e)}")

@router.post("/bulk-mark")
async def bulk_mark_new_products(product_ids: List[str], days: int = 30, db = Depends(get_db)):
    """Mark multiple products as new"""
    try:
        highlight_until = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
        
        result = await db.products.update_many(
            {"id": {"$in": product_ids}},
            {"$set": {
                "is_new": True,
                "new_badge_text": "NEW",
                "new_priority": 0,
                "new_until": highlight_until,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "status": "success",
            "message": f"Marked {result.modified_count} products as new",
            "modified_count": result.modified_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error bulk marking products: {str(e)}")

@router.delete("/{product_id}/remove-new")
async def remove_new_badge(product_id: str, db = Depends(get_db)):
    """Remove new badge from product"""
    try:
        result = await db.products.update_one(
            {"id": product_id},
            {"$set": {
                "is_new": False,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {
            "status": "success",
            "message": "New badge removed from product"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing new badge: {str(e)}")

@router.post("/cleanup-expired")
async def cleanup_expired_new_products(db = Depends(get_db)):
    """Remove new badge from expired products (can be run as cron job)"""
    try:
        current_date = datetime.now(timezone.utc).isoformat()
        
        result = await db.products.update_many(
            {
                "is_new": True,
                "new_until": {"$lt": current_date}
            },
            {"$set": {
                "is_new": False,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "status": "success",
            "message": f"Cleaned up {result.modified_count} expired new product badges",
            "modified_count": result.modified_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up expired products: {str(e)}")
