from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from database import get_db
from pydantic import BaseModel
import uuid
import random

router = APIRouter(prefix="/marketing", tags=["marketing"])

# Coupon Models
class CouponCreate(BaseModel):
    code: str
    discount_type: str  # percentage, fixed
    discount_value: float
    min_order_value: float = 0
    max_discount: Optional[float] = None
    valid_from: str
    valid_until: str
    usage_limit: int = 100
    description: Optional[str] = None

class CouponValidate(BaseModel):
    coupon_code: str
    order_value: float

# Cart Abandonment Models
class CartAbandonmentEmail(BaseModel):
    customer_email: str
    cart_items: List[dict]
    cart_total: float

# Create Coupon
@router.post("/coupons/create")
async def create_coupon(
    coupon: CouponCreate,
    database = Depends(get_db)
):
    """Create a new discount coupon"""
    try:
        # Check if coupon code already exists
        existing = await database.coupons.find_one({"code": coupon.code.upper()})
        if existing:
            raise HTTPException(status_code=400, detail="Coupon code already exists")
        
        coupon_data = {
            "id": str(uuid.uuid4()),
            "code": coupon.code.upper(),
            "discount_type": coupon.discount_type,
            "discount_value": coupon.discount_value,
            "min_order_value": coupon.min_order_value,
            "max_discount": coupon.max_discount,
            "valid_from": coupon.valid_from,
            "valid_until": coupon.valid_until,
            "usage_limit": coupon.usage_limit,
            "usage_count": 0,
            "description": coupon.description or f"{coupon.discount_value}{'%' if coupon.discount_type == 'percentage' else ' OFF'}",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await database.coupons.insert_one(coupon_data)
        coupon_data.pop("_id", None)
        
        return {
            "success": True,
            "message": "Coupon created successfully",
            "data": coupon_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create coupon: {str(e)}")


@router.post("/coupons/validate")
async def validate_coupon(
    validation: CouponValidate,
    database = Depends(get_db)
):
    """Validate coupon and calculate discount"""
    try:
        coupon = await database.coupons.find_one({"code": validation.coupon_code.upper()})
        
        if not coupon:
            raise HTTPException(status_code=404, detail="Invalid coupon code")
        
        # Check if coupon is active
        if not coupon.get("is_active"):
            raise HTTPException(status_code=400, detail="Coupon is no longer active")
        
        # Check validity dates
        now = datetime.now(timezone.utc).isoformat()
        if coupon["valid_from"] > now or coupon["valid_until"] < now:
            raise HTTPException(status_code=400, detail="Coupon has expired")
        
        # Check usage limit
        if coupon["usage_count"] >= coupon["usage_limit"]:
            raise HTTPException(status_code=400, detail="Coupon usage limit reached")
        
        # Check minimum order value
        if validation.order_value < coupon["min_order_value"]:
            raise HTTPException(
                status_code=400,
                detail=f"Minimum order value of ₹{coupon['min_order_value']} required"
            )
        
        # Calculate discount
        if coupon["discount_type"] == "percentage":
            discount = (validation.order_value * coupon["discount_value"]) / 100
            if coupon.get("max_discount"):
                discount = min(discount, coupon["max_discount"])
        else:  # fixed
            discount = coupon["discount_value"]
        
        discount = min(discount, validation.order_value)  # Can't exceed order value
        
        return {
            "success": True,
            "valid": True,
            "discount": round(discount, 2),
            "final_amount": round(validation.order_value - discount, 2),
            "coupon": {
                "code": coupon["code"],
                "description": coupon["description"]
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate coupon: {str(e)}")


@router.get("/coupons")
async def get_coupons(
    database = Depends(get_db)
):
    """Get all coupons"""
    try:
        cursor = database.coupons.find({})
        coupons = await cursor.to_list(length=100)
        
        for coupon in coupons:
            if "_id" in coupon:
                del coupon["_id"]
        
        return {
            "success": True,
            "data": coupons
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch coupons: {str(e)}")


@router.post("/coupons/{coupon_id}/apply")
async def apply_coupon(
    coupon_id: str,
    database = Depends(get_db)
):
    """Apply/use a coupon (increment usage count)"""
    try:
        result = await database.coupons.update_one(
            {"id": coupon_id},
            {"$inc": {"usage_count": 1}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Coupon not found")
        
        return {
            "success": True,
            "message": "Coupon applied successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply coupon: {str(e)}")


# Cart Abandonment
@router.post("/cart-abandonment/send-email")
async def send_cart_abandonment_email(
    data: CartAbandonmentEmail,
    database = Depends(get_db)
):
    """Send cart abandonment email (Mock)"""
    try:
        # In real implementation, this would send an actual email
        # For now, we'll just log the abandonment
        
        abandonment_data = {
            "id": str(uuid.uuid4()),
            "customer_email": data.customer_email,
            "cart_items": data.cart_items,
            "cart_total": data.cart_total,
            "email_sent": True,
            "email_opened": False,
            "clicked_link": False,
            "recovered": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await database.cart_abandonments.insert_one(abandonment_data)
        
        return {
            "success": True,
            "message": "Cart abandonment email sent successfully (Mock)",
            "data": {
                "email_id": abandonment_data["id"],
                "email": data.customer_email,
                "items_count": len(data.cart_items),
                "cart_value": data.cart_total
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@router.get("/cart-abandonment/analytics")
async def get_cart_abandonment_analytics(
    database = Depends(get_db)
):
    """Get cart abandonment analytics"""
    try:
        total = await database.cart_abandonments.count_documents({})
        emails_sent = await database.cart_abandonments.count_documents({"email_sent": True})
        emails_opened = await database.cart_abandonments.count_documents({"email_opened": True})
        recovered = await database.cart_abandonments.count_documents({"recovered": True})
        
        recovery_rate = (recovered / total * 100) if total > 0 else 0
        open_rate = (emails_opened / emails_sent * 100) if emails_sent > 0 else 0
        
        return {
            "success": True,
            "data": {
                "total_abandonments": total,
                "emails_sent": emails_sent,
                "emails_opened": emails_opened,
                "carts_recovered": recovered,
                "recovery_rate": round(recovery_rate, 2),
                "open_rate": round(open_rate, 2)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")


# Points/Rewards System
@router.get("/rewards/customer/{customer_email}")
async def get_customer_points(
    customer_email: str,
    database = Depends(get_db)
):
    """Get customer reward points"""
    try:
        customer = await database.customer_points.find_one({"email": customer_email})
        
        if not customer:
            # Create new customer with 0 points
            customer_data = {
                "email": customer_email,
                "points": 0,
                "lifetime_points": 0,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await database.customer_points.insert_one(customer_data)
            customer = customer_data
        
        if "_id" in customer:
            del customer["_id"]
        
        return {
            "success": True,
            "data": customer
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch points: {str(e)}")


@router.post("/rewards/add-points")
async def add_reward_points(
    customer_email: str,
    points: int,
    reason: str,
    database = Depends(get_db)
):
    """Add reward points to customer"""
    try:
        result = await database.customer_points.update_one(
            {"email": customer_email},
            {
                "$inc": {"points": points, "lifetime_points": points},
                "$push": {
                    "history": {
                        "points": points,
                        "reason": reason,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }
            },
            upsert=True
        )
        
        return {
            "success": True,
            "message": f"Added {points} points for {reason}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add points: {str(e)}")
