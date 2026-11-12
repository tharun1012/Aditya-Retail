"""
Customer Reviews System
Allow customers to leave reviews and ratings for products
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
from database import get_db

router = APIRouter(prefix="/reviews", tags=["Reviews"])

class ReviewCreate(BaseModel):
    product_id: str
    user_name: str
    user_email: str
    rating: int  # 1-5
    review_title: str
    review_text: str
    verified_purchase: bool = False
    images: Optional[List[str]] = None

class ReviewUpdate(BaseModel):
    status: Optional[str] = None  # pending, approved, rejected
    helpful_count: Optional[int] = None

@router.post("/")
async def submit_review(review: ReviewCreate, db = Depends(get_db)):
    """Submit a product review"""
    try:
        # Validate rating
        if review.rating < 1 or review.rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Check if product exists
        product = await db.products.find_one({"id": review.product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Create review document
        review_doc = {
            "id": str(uuid.uuid4()),
            "product_id": review.product_id,
            "user_name": review.user_name,
            "user_email": review.user_email,
            "rating": review.rating,
            "review_title": review.review_title,
            "review_text": review.review_text,
            "verified_purchase": review.verified_purchase,
            "images": review.images or [],
            "helpful_count": 0,
            "status": "pending",  # pending, approved, rejected
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.reviews.insert_one(review_doc)
        review_doc.pop("_id", None)
        
        return {
            "status": "success",
            "message": "Review submitted successfully. It will be visible after approval.",
            "review": review_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting review: {str(e)}")

@router.get("/product/{product_id}")
async def get_product_reviews(
    product_id: str,
    status: Optional[str] = "approved",
    sort_by: Optional[str] = "recent",  # recent, helpful, rating
    db = Depends(get_db)
):
    """Get reviews for a specific product"""
    try:
        query = {"product_id": product_id}
        
        if status:
            query["status"] = status
        
        # Determine sort order
        sort_field = "created_at"
        sort_direction = -1  # descending
        
        if sort_by == "helpful":
            sort_field = "helpful_count"
        elif sort_by == "rating":
            sort_field = "rating"
        
        reviews = await db.reviews.find(query, {"_id": 0}).sort(sort_field, sort_direction).to_list(100)
        
        # Calculate rating statistics
        if reviews:
            total_reviews = len(reviews)
            total_rating = sum(r["rating"] for r in reviews)
            average_rating = total_rating / total_reviews
            
            rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for review in reviews:
                rating_distribution[review["rating"]] += 1
        else:
            total_reviews = 0
            average_rating = 0
            rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        return {
            "status": "success",
            "total_reviews": total_reviews,
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution,
            "reviews": reviews
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reviews: {str(e)}")

@router.get("/{review_id}")
async def get_review(review_id: str, db = Depends(get_db)):
    """Get a single review"""
    try:
        review = await db.reviews.find_one({"id": review_id}, {"_id": 0})
        
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        return {
            "status": "success",
            "review": review
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching review: {str(e)}")

@router.put("/{review_id}/helpful")
async def mark_review_helpful(review_id: str, db = Depends(get_db)):
    """Mark a review as helpful"""
    try:
        result = await db.reviews.update_one(
            {"id": review_id},
            {"$inc": {"helpful_count": 1}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Review not found")
        
        updated_review = await db.reviews.find_one({"id": review_id}, {"_id": 0})
        
        return {
            "status": "success",
            "message": "Review marked as helpful",
            "review": updated_review
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating review: {str(e)}")

@router.put("/{review_id}/approve")
async def approve_review(review_id: str, db = Depends(get_db)):
    """Admin: Approve a review"""
    try:
        result = await db.reviews.update_one(
            {"id": review_id},
            {
                "$set": {
                    "status": "approved",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Review not found")
        
        return {
            "status": "success",
            "message": "Review approved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving review: {str(e)}")

@router.put("/{review_id}/reject")
async def reject_review(review_id: str, db = Depends(get_db)):
    """Admin: Reject a review"""
    try:
        result = await db.reviews.update_one(
            {"id": review_id},
            {
                "$set": {
                    "status": "rejected",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Review not found")
        
        return {
            "status": "success",
            "message": "Review rejected successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rejecting review: {str(e)}")

@router.delete("/{review_id}")
async def delete_review(review_id: str, db = Depends(get_db)):
    """Admin: Delete a review"""
    try:
        result = await db.reviews.delete_one({"id": review_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Review not found")
        
        return {
            "status": "success",
            "message": "Review deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting review: {str(e)}")

@router.get("/")
async def get_all_reviews(
    status: Optional[str] = None,
    limit: int = 50,
    db = Depends(get_db)
):
    """Admin: Get all reviews with optional status filter"""
    try:
        query = {}
        if status:
            query["status"] = status
        
        reviews = await db.reviews.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
        
        return {
            "status": "success",
            "total": len(reviews),
            "reviews": reviews
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reviews: {str(e)}")
