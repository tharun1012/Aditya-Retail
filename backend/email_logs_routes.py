"""
Email Logs API Routes
View all sent emails across the system
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime, timedelta, timezone
from database import get_db

router = APIRouter(prefix="/email-logs", tags=["Email Logs"])


@router.get("/")
async def get_email_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    from_agent: Optional[str] = None,
    status: Optional[str] = None,
    to_email: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    db=Depends(get_db)
):
    """Get all email logs with filtering options"""
    try:
        # Build filter
        filter_query = {}
        
        # Filter by date range
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        filter_query["timestamp"] = {"$gte": cutoff_date}
        
        if from_agent:
            filter_query["from_agent"] = from_agent
        if status:
            filter_query["status"] = status
        if to_email:
            filter_query["to_email"] = {"$regex": to_email, "$options": "i"}
        
        # Get total count
        total = await db.email_logs.count_documents(filter_query)
        
        # Get paginated results
        skip = (page - 1) * limit
        emails = await db.email_logs.find(filter_query, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
        
        return {
            "status": "success",
            "emails": emails,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_email_stats(
    days: int = Query(30, ge=1, le=365),
    db=Depends(get_db)
):
    """Get email sending statistics"""
    try:
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        # Total emails sent
        total_sent = await db.email_logs.count_documents({
            "timestamp": {"$gte": cutoff_date},
            "status": "sent"
        })
        
        # Emails by agent
        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_date}}},
            {"$group": {
                "_id": "$from_agent",
                "count": {"$sum": 1}
            }}
        ]
        by_agent = await db.email_logs.aggregate(pipeline).to_list(100)
        
        # Recent emails (last 24 hours)
        last_24h = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        recent_count = await db.email_logs.count_documents({
            "timestamp": {"$gte": last_24h}
        })
        
        # Format agent stats
        agent_stats = {item["_id"] or "unknown": item["count"] for item in by_agent}
        
        return {
            "status": "success",
            "period_days": days,
            "stats": {
                "total_sent": total_sent,
                "last_24_hours": recent_count,
                "by_agent": agent_stats
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_email_summary(db=Depends(get_db)):
    """Get a quick summary of email types and their counts"""
    try:
        # Email types pipeline
        pipeline = [
            {"$group": {
                "_id": {
                    "agent": "$from_agent",
                    "status": "$status"
                },
                "count": {"$sum": 1},
                "last_sent": {"$max": "$timestamp"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        results = await db.email_logs.aggregate(pipeline).to_list(100)
        
        # Get unique recipients
        unique_recipients = await db.email_logs.distinct("to_email")
        
        # Get total
        total = await db.email_logs.count_documents({})
        
        return {
            "status": "success",
            "summary": {
                "total_emails": total,
                "unique_recipients": len(unique_recipients),
                "breakdown": results
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
