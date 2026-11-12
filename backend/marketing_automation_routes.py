"""
Marketing Automation Control API
Endpoints to control and monitor the autonomous AI Marketing Agent
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from database import get_db
from ai_marketing_automation import AIMarketingAgent
import asyncio

router = APIRouter(prefix="/marketing-automation", tags=["Marketing Automation"])

# Global agent instance
marketing_agent = AIMarketingAgent()
automation_active = False

class TargetsUpdate(BaseModel):
    monthly_leads: int
    monthly_revenue: int
    conversion_rate: float
    cost_per_lead: float

@router.get("/status")
async def get_automation_status(db = Depends(get_db)):
    """Get current automation status"""
    try:
        # Check if automation is active
        status_doc = await db.automation_status.find_one({"type": "main"})
        
        if not status_doc:
            return {
                "status": "inactive",
                "message": "Automation not yet activated"
            }
        
        return {
            "status": status_doc.get("status", "inactive"),
            "last_run": status_doc.get("last_run"),
            "next_run": status_doc.get("next_run")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/progress")
async def get_monthly_progress():
    """Get current month progress towards targets"""
    try:
        progress = await marketing_agent.track_monthly_progress()
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/activate")
async def activate_automation(
    targets: TargetsUpdate,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Activate autonomous marketing automation"""
    try:
        # Set targets
        await marketing_agent.set_monthly_targets(
            targets.monthly_leads,
            targets.monthly_revenue,
            targets.conversion_rate,
            targets.cost_per_lead
        )
        
        # Mark as active
        await db.automation_status.update_one(
            {"type": "main"},
            {"$set": {
                "status": "active",
                "activated_at": datetime.now(timezone.utc).isoformat(),
                "targets": targets.dict()
            }},
            upsert=True
        )
        
        # Run initial automation in background
        background_tasks.add_task(run_initial_automation)
        
        return {
            "status": "success",
            "message": "AI Marketing Agent activated successfully!",
            "targets": targets.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pause")
async def pause_automation(db = Depends(get_db)):
    """Pause automation"""
    try:
        await db.automation_status.update_one(
            {"type": "main"},
            {"$set": {
                "status": "paused",
                "paused_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "status": "success",
            "message": "Automation paused"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resume")
async def resume_automation(db = Depends(get_db)):
    """Resume automation"""
    try:
        await db.automation_status.update_one(
            {"type": "main"},
            {"$set": {
                "status": "active",
                "resumed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "status": "success",
            "message": "Automation resumed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/targets")
async def update_targets(targets: TargetsUpdate, db = Depends(get_db)):
    """Update monthly targets"""
    try:
        await marketing_agent.set_monthly_targets(
            targets.monthly_leads,
            targets.monthly_revenue,
            targets.conversion_rate,
            targets.cost_per_lead
        )
        
        return {
            "status": "success",
            "message": "Targets updated successfully",
            "targets": targets.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_automation_logs(limit: int = 10, db = Depends(get_db)):
    """Get recent automation logs"""
    try:
        logs = await db.automation_logs.find(
            {}, 
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit).to_list(limit)
        
        return {
            "status": "success",
            "logs": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-now")
async def run_automation_now(background_tasks: BackgroundTasks):
    """Manually trigger automation run"""
    try:
        background_tasks.add_task(run_manual_automation)
        
        return {
            "status": "success",
            "message": "Automation triggered manually"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns")
async def get_marketing_campaigns(db = Depends(get_db)):
    """Get all AI-generated marketing campaigns"""
    try:
        campaigns = await db.marketing_campaigns.find(
            {},
            {"_id": 0}
        ).sort("created_at", -1).to_list(100)
        
        return {
            "status": "success",
            "campaigns": campaigns,
            "count": len(campaigns)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background task functions
async def run_initial_automation():
    """Run initial automation after activation"""
    try:
        # Generate campaigns
        campaigns = await marketing_agent.generate_marketing_campaigns()
        print(f"✅ Initial automation: Created {len(campaigns)} campaigns")
    except Exception as e:
        print(f"❌ Initial automation error: {e}")

async def run_manual_automation():
    """Run full automation cycle manually"""
    try:
        # Run daily automation tasks
        campaigns = await marketing_agent.generate_marketing_campaigns()
        progress = await marketing_agent.track_monthly_progress()
        optimizations = await marketing_agent.optimize_campaigns()
        
        print(f"✅ Manual automation complete")
        print(f"   Campaigns: {len(campaigns)}")
        print(f"   Progress: {progress['leads_generated']}/{progress['target_leads']} leads")
        print(f"   Optimizations: {optimizations['campaigns_updated']} campaigns updated")
    except Exception as e:
        print(f"❌ Manual automation error: {e}")
