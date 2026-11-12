from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List, Optional
import os
import uuid
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/admin/campaigns", tags=["Campaigns"])

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

@router.get("/")
async def get_all_campaigns(status: Optional[str] = None):
    """Get all marketing campaigns"""
    try:
        query = {}
        if status:
            query["status"] = status
        
        collections = await db.list_collection_names()
        if 'campaigns' not in collections:
            return {"status": "success", "campaigns": []}
        
        campaigns = await db.campaigns.find(query, {"_id": 0}).sort("created_at", -1).to_list(None)
        
        return {
            "status": "success",
            "campaigns": campaigns
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_campaign(campaign_data: dict):
    """Create a new marketing campaign"""
    try:
        campaign = {
            "id": str(uuid.uuid4()),
            "name": campaign_data.get("name"),
            "type": campaign_data.get("type", "email"),
            "status": "draft",
            "target_audience": campaign_data.get("target_audience", "all"),
            "subject": campaign_data.get("subject"),
            "message": campaign_data.get("message"),
            "start_date": campaign_data.get("start_date"),
            "end_date": campaign_data.get("end_date"),
            "sent_count": 0,
            "opened_count": 0,
            "clicked_count": 0,
            "converted_count": 0,
            "revenue_generated": 0,
            "created_by": "admin",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        await db.campaigns.insert_one(campaign)
        
        return {
            "status": "success",
            "message": "Campaign created successfully",
            "campaign_id": campaign["id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{campaign_id}")
async def update_campaign(campaign_id: str, campaign_data: dict):
    """Update a campaign"""
    try:
        campaign_data["updated_at"] = datetime.now().isoformat()
        
        result = await db.campaigns.update_one(
            {"id": campaign_id},
            {"$set": campaign_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return {
            "status": "success",
            "message": "Campaign updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """Delete a campaign"""
    try:
        result = await db.campaigns.delete_one({"id": campaign_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return {
            "status": "success",
            "message": "Campaign deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{campaign_id}/launch")
async def launch_campaign(campaign_id: str):
    """Launch a campaign"""
    try:
        result = await db.campaigns.update_one(
            {"id": campaign_id},
            {"$set": {"status": "active", "updated_at": datetime.now().isoformat()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return {
            "status": "success",
            "message": "Campaign launched successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary")
async def get_campaign_stats():
    """Get campaign statistics"""
    try:
        collections = await db.list_collection_names()
        if 'campaigns' not in collections:
            return {
                "status": "success",
                "data": {
                    "total_campaigns": 0,
                    "active_campaigns": 0,
                    "total_sent": 0,
                    "average_open_rate": 0,
                    "average_ctr": 0,
                    "total_revenue": 0
                }
            }
        
        total = await db.campaigns.count_documents({})
        active = await db.campaigns.count_documents({"status": "active"})
        
        # Aggregate stats
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_sent": {"$sum": "$sent_count"},
                    "total_opened": {"$sum": "$opened_count"},
                    "total_clicked": {"$sum": "$clicked_count"},
                    "total_revenue": {"$sum": "$revenue_generated"}
                }
            }
        ]
        
        stats = await db.campaigns.aggregate(pipeline).to_list(1)
        
        if stats:
            s = stats[0]
            open_rate = (s['total_opened'] / s['total_sent'] * 100) if s['total_sent'] > 0 else 0
            ctr = (s['total_clicked'] / s['total_sent'] * 100) if s['total_sent'] > 0 else 0
            
            return {
                "status": "success",
                "data": {
                    "total_campaigns": total,
                    "active_campaigns": active,
                    "total_sent": s['total_sent'],
                    "average_open_rate": round(open_rate, 2),
                    "average_ctr": round(ctr, 2),
                    "total_revenue": s['total_revenue']
                }
            }
        else:
            return {
                "status": "success",
                "data": {
                    "total_campaigns": total,
                    "active_campaigns": active,
                    "total_sent": 0,
                    "average_open_rate": 0,
                    "average_ctr": 0,
                    "total_revenue": 0
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
