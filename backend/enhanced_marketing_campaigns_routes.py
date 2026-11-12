"""
Enhanced Marketing Campaigns API
Multi-channel campaigns with automation, segmentation, and A/B testing
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from database import get_db
import uuid

router = APIRouter(prefix="/marketing-campaigns", tags=["Enhanced Marketing Campaigns"])

class CustomSegment(BaseModel):
    min_order_value: Optional[float] = 0
    max_order_value: Optional[float] = None
    last_purchase_days: Optional[int] = None
    category_interest: Optional[str] = None
    location: Optional[str] = None

class MarketingCampaignCreate(BaseModel):
    name: str
    type: str = "email"
    channels: List[str] = ["email"]
    target_segment: str = "all"
    custom_segment: Optional[CustomSegment] = None
    subject: Optional[str] = None
    email_content: Optional[str] = None
    sms_content: Optional[str] = None
    whatsapp_content: Optional[str] = None
    enable_ab_testing: bool = False
    variant_a_subject: Optional[str] = None
    variant_b_subject: Optional[str] = None
    schedule_type: str = "immediate"
    schedule_date: Optional[str] = None
    automation_trigger: str = "none"
    cart_abandonment_delay: int = 60

@router.get("")
async def get_campaigns(db = Depends(get_db)):
    """Get all marketing campaigns"""
    try:
        campaigns = await db.marketing_campaigns.find({}, {"_id": 0}).to_list(1000)
        return {
            "status": "success",
            "campaigns": campaigns
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_campaign(
    campaign: MarketingCampaignCreate,
    db = Depends(get_db)
):
    """Create a new marketing campaign"""
    try:
        campaign_id = str(uuid.uuid4())
        
        campaign_doc = {
            "id": campaign_id,
            **campaign.dict(),
            "status": "draft",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "stats": {
                "sent": 0,
                "opened": 0,
                "clicked": 0,
                "converted": 0,
                "revenue_generated": 0
            }
        }
        
        await db.marketing_campaigns.insert_one(campaign_doc)
        
        return {
            "status": "success",
            "message": "Campaign created successfully",
            "campaign_id": campaign_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{campaign_id}")
async def update_campaign(
    campaign_id: str,
    campaign: MarketingCampaignCreate,
    db = Depends(get_db)
):
    """Update an existing campaign"""
    try:
        update_data = {
            **campaign.dict(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = await db.marketing_campaigns.update_one(
            {"id": campaign_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return {
            "status": "success",
            "message": "Campaign updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{campaign_id}/launch")
async def launch_campaign(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Launch a marketing campaign"""
    try:
        # Get campaign
        campaign = await db.marketing_campaigns.find_one({"id": campaign_id}, {"_id": 0})
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get target customers based on segment
        customers = await get_target_customers(db, campaign)
        
        # Update campaign status
        await db.marketing_campaigns.update_one(
            {"id": campaign_id},
            {
                "$set": {
                    "status": "active",
                    "launched_at": datetime.now(timezone.utc).isoformat(),
                    "target_count": len(customers)
                }
            }
        )
        
        # Send campaign in background (simulated for now)
        # background_tasks.add_task(send_campaign_messages, campaign, customers)
        
        return {
            "status": "success",
            "message": f"Campaign launched to {len(customers)} customers",
            "target_count": len(customers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: str, db = Depends(get_db)):
    """Delete a campaign"""
    try:
        result = await db.marketing_campaigns.delete_one({"id": campaign_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return {
            "status": "success",
            "message": "Campaign deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{campaign_id}/analytics")
async def get_campaign_analytics(campaign_id: str, db = Depends(get_db)):
    """Get campaign analytics and performance metrics"""
    try:
        campaign = await db.marketing_campaigns.find_one({"id": campaign_id}, {"_id": 0})
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        stats = campaign.get("stats", {})
        
        # Calculate metrics
        sent = stats.get("sent", 0)
        opened = stats.get("opened", 0)
        clicked = stats.get("clicked", 0)
        converted = stats.get("converted", 0)
        
        open_rate = (opened / sent * 100) if sent > 0 else 0
        click_rate = (clicked / sent * 100) if sent > 0 else 0
        conversion_rate = (converted / sent * 100) if sent > 0 else 0
        
        return {
            "status": "success",
            "analytics": {
                "campaign_name": campaign.get("name"),
                "status": campaign.get("status"),
                "sent": sent,
                "opened": opened,
                "clicked": clicked,
                "converted": converted,
                "open_rate": round(open_rate, 2),
                "click_rate": round(click_rate, 2),
                "conversion_rate": round(conversion_rate, 2),
                "revenue_generated": stats.get("revenue_generated", 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_target_customers(db, campaign):
    """Get target customers based on campaign segment"""
    segment = campaign.get("target_segment", "all")
    
    query = {}
    
    if segment == "all":
        pass  # No filter
    elif segment == "high_value":
        # Customers with orders > ₹10,000
        query = {"total_spent": {"$gte": 10000}}
    elif segment == "recent":
        # Customers who ordered in last 30 days
        from datetime import timedelta
        thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        query = {"last_order_date": {"$gte": thirty_days_ago}}
    elif segment == "inactive":
        # Customers who haven't ordered in 90+ days
        from datetime import timedelta
        ninety_days_ago = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
        query = {"last_order_date": {"$lt": ninety_days_ago}}
    elif segment == "cart_abandoners":
        # Customers with abandoned carts
        query = {"has_abandoned_cart": True}
    elif segment == "first_time":
        # First time buyers
        query = {"order_count": 1}
    
    # Get customers
    customers = await db.customers.find(query, {"_id": 0}).to_list(1000)
    
    return customers

# Cart Abandonment Automation
@router.post("/automation/cart-abandonment")
async def trigger_cart_abandonment(
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Trigger cart abandonment campaign for eligible carts"""
    try:
        from datetime import timedelta
        
        # Find carts abandoned more than 1 hour ago
        one_hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        
        abandoned_carts = await db.carts.find({
            "updated_at": {"$lt": one_hour_ago},
            "items": {"$ne": []},
            "abandonment_email_sent": {"$ne": True}
        }, {"_id": 0}).to_list(100)
        
        # Find active cart abandonment campaigns
        campaign = await db.marketing_campaigns.find_one({
            "automation_trigger": "cart_abandonment",
            "status": "active"
        }, {"_id": 0})
        
        if not campaign:
            return {
                "status": "info",
                "message": "No active cart abandonment campaign found"
            }
        
        # Send emails (simulated)
        for cart in abandoned_carts:
            # Mark as sent
            await db.carts.update_one(
                {"user_id": cart.get("user_id")},
                {"$set": {"abandonment_email_sent": True}}
            )
        
        return {
            "status": "success",
            "message": f"Cart abandonment emails triggered for {len(abandoned_carts)} carts"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
