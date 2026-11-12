"""
Lead Scraping API Routes
Endpoints for managing autonomous lead generation
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from typing import Optional, List
import os
from dotenv import load_dotenv

from lead_scraping_service import lead_scraping_service, INDIAN_CITIES, DEFAULT_KEYWORDS, BUSINESS_TYPES

load_dotenv()

router = APIRouter(prefix="/lead-scraping", tags=["Lead Scraping"])

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]


@router.get("/dashboard")
async def get_scraping_dashboard():
    """Get lead scraping dashboard overview"""
    try:
        # Get settings
        settings = await lead_scraping_service.get_settings()
        
        # Get lead counts by source
        pipeline = [
            {"$group": {"_id": "$source", "count": {"$sum": 1}}}
        ]
        source_counts = await db.scraped_leads.aggregate(pipeline).to_list(100)
        leads_by_source = {item["_id"]: item["count"] for item in source_counts}
        
        # Get total leads
        total_leads = await db.scraped_leads.count_documents({})
        
        # Get leads from today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_leads = await db.scraped_leads.count_documents({
            "created_at": {"$gte": today_start.isoformat()}
        })
        
        # Get converted leads
        converted_leads = await db.scraped_leads.count_documents({"status": "converted"})
        
        # Get recent jobs
        recent_jobs = await db.lead_scraping_jobs.find(
            {}, {"_id": 0}
        ).sort("completed_at", -1).limit(5).to_list(5)
        
        # Get platform status
        platforms = ["twitter", "instagram", "facebook_ads", "youtube", "linkedin"]
        platform_status = []
        
        for platform in platforms:
            platform_settings = await db.admin_settings.find_one({"platform": platform}, {"_id": 0})
            platform_status.append({
                "platform": platform.replace("_ads", ""),
                "is_configured": bool(platform_settings),
                "is_enabled": platform_settings.get("is_enabled", False) if platform_settings else False
            })
        
        return {
            "status": "success",
            "overview": {
                "total_leads": total_leads,
                "leads_today": today_leads,
                "converted_leads": converted_leads,
                "conversion_rate": round((converted_leads / total_leads * 100) if total_leads > 0 else 0, 1)
            },
            "leads_by_source": leads_by_source,
            "platform_status": platform_status,
            "settings": {
                "is_enabled": settings.get("is_enabled", False),
                "target_cities_count": len(settings.get("target_cities", [])),
                "keywords_count": len(settings.get("keywords", [])),
                "scraping_frequency": settings.get("scraping_frequency", "daily")
            },
            "recent_jobs": recent_jobs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run")
async def run_scraping_job(background_tasks: BackgroundTasks):
    """Manually trigger a lead scraping job"""
    try:
        # Run in background
        background_tasks.add_task(lead_scraping_service.run_full_scraping_job)
        
        return {
            "status": "success",
            "message": "Lead scraping job started in background"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-sync")
async def run_scraping_job_sync():
    """Run lead scraping job synchronously (for testing)"""
    try:
        result = await lead_scraping_service.run_full_scraping_job()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leads")
async def get_scraped_leads(
    source: Optional[str] = None,
    status: Optional[str] = None,
    lead_type: Optional[str] = None,
    city: Optional[str] = None,
    min_score: Optional[int] = None,
    page: int = 1,
    limit: int = 50
):
    """Get scraped leads with filtering"""
    try:
        query = {}
        
        if source:
            query["source"] = source
        if status:
            query["status"] = status
        if lead_type:
            query["lead_type"] = lead_type
        if city:
            query["$or"] = [
                {"location": {"$regex": city, "$options": "i"}},
                {"city_matched": {"$regex": city, "$options": "i"}}
            ]
        if min_score:
            query["score"] = {"$gte": min_score}
        
        skip = (page - 1) * limit
        
        leads = await db.scraped_leads.find(
            query, {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        total = await db.scraped_leads.count_documents(query)
        
        return {
            "status": "success",
            "leads": leads,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/leads/{lead_id}/convert")
async def convert_lead_to_crm(lead_id: str):
    """Convert a scraped lead to a CRM lead"""
    try:
        result = await lead_scraping_service.convert_to_crm_lead(lead_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return {
            "status": "success",
            "message": "Lead converted to CRM successfully",
            "crm_lead": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/leads/{lead_id}")
async def delete_scraped_lead(lead_id: str):
    """Delete a scraped lead"""
    try:
        result = await db.scraped_leads.delete_one({"id": lead_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return {"status": "success", "message": "Lead deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/leads/bulk-convert")
async def bulk_convert_leads(lead_ids: List[str]):
    """Convert multiple scraped leads to CRM leads"""
    try:
        converted = []
        failed = []
        
        for lead_id in lead_ids:
            result = await lead_scraping_service.convert_to_crm_lead(lead_id)
            
            if "error" in result:
                failed.append({"id": lead_id, "error": result["error"]})
            else:
                converted.append(result)
        
        return {
            "status": "success",
            "converted_count": len(converted),
            "failed_count": len(failed),
            "converted": converted,
            "failed": failed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
async def get_scraping_jobs(limit: int = 20):
    """Get lead scraping job history"""
    try:
        jobs = await db.lead_scraping_jobs.find(
            {}, {"_id": 0}
        ).sort("completed_at", -1).limit(limit).to_list(limit)
        
        return {
            "status": "success",
            "jobs": jobs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/cities")
async def get_available_cities():
    """Get list of available Indian cities for targeting"""
    return {
        "status": "success",
        "metro_cities": INDIAN_CITIES["metro"],
        "tier2_cities": INDIAN_CITIES["tier2"]
    }


@router.get("/config/keywords")
async def get_default_keywords():
    """Get default keywords for lead scraping"""
    return {
        "status": "success",
        "keywords": DEFAULT_KEYWORDS
    }


@router.get("/config/business-types")
async def get_business_types():
    """Get available business types for B2B targeting"""
    return {
        "status": "success",
        "business_types": BUSINESS_TYPES
    }


@router.get("/analytics")
async def get_scraping_analytics():
    """Get detailed analytics on lead scraping performance"""
    try:
        # Leads by day (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        daily_pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": seven_days_ago.isoformat()}
                }
            },
            {
                "$group": {
                    "_id": {"$substr": ["$created_at", 0, 10]},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        daily_leads = await db.scraped_leads.aggregate(daily_pipeline).to_list(100)
        
        # Leads by score range
        score_pipeline = [
            {
                "$bucket": {
                    "groupBy": "$score",
                    "boundaries": [0, 40, 60, 80, 101],
                    "default": "unknown",
                    "output": {
                        "count": {"$sum": 1}
                    }
                }
            }
        ]
        score_distribution = await db.scraped_leads.aggregate(score_pipeline).to_list(100)
        
        # Leads by type
        type_pipeline = [
            {"$group": {"_id": "$lead_type", "count": {"$sum": 1}}}
        ]
        type_distribution = await db.scraped_leads.aggregate(type_pipeline).to_list(100)
        
        # Top cities
        city_pipeline = [
            {"$match": {"location": {"$exists": True, "$ne": ""}}},
            {"$group": {"_id": "$location", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_cities = await db.scraped_leads.aggregate(city_pipeline).to_list(100)
        
        # Conversion funnel
        total = await db.scraped_leads.count_documents({})
        new = await db.scraped_leads.count_documents({"status": "new"})
        converted = await db.scraped_leads.count_documents({"status": "converted"})
        
        return {
            "status": "success",
            "daily_leads": [{"date": d["_id"], "count": d["count"]} for d in daily_leads],
            "score_distribution": score_distribution,
            "type_distribution": [{"type": t["_id"], "count": t["count"]} for t in type_distribution],
            "top_cities": [{"city": c["_id"], "count": c["count"]} for c in top_cities],
            "funnel": {
                "total": total,
                "new": new,
                "converted": converted,
                "conversion_rate": round((converted / total * 100) if total > 0 else 0, 1)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
