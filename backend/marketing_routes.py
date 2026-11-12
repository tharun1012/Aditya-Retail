from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from ai_marketing_automation import AIMarketingCRMOrchestrator, AIMarketingAgent, AICRMAgent

router = APIRouter()

# Initialize the orchestrator
orchestrator = AIMarketingCRMOrchestrator()

class MarketingTargetsInput(BaseModel):
    monthly_leads: int
    monthly_revenue: int
    conversion_rate: float
    cost_per_lead: float

class LeadInput(BaseModel):
    name: str
    email: str
    phone: str
    product_interest: str
    budget_range: str
    timeline: str = "Within 30 days"
    source: str = "website"

@router.post("/marketing/setup")
async def setup_marketing_system(targets: MarketingTargetsInput):
    """Setup AI Marketing & CRM system with targets"""
    try:
        result = await orchestrator.setup_complete_system({
            "monthly_leads": targets.monthly_leads,
            "monthly_revenue": targets.monthly_revenue,
            "conversion_rate": targets.conversion_rate,
            "cost_per_lead": targets.cost_per_lead
        })
        
        return {
            "success": True,
            "message": "AI Marketing & CRM System setup successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/marketing/campaigns")
async def get_marketing_campaigns():
    """Get all active marketing campaigns"""
    try:
        campaigns = await orchestrator.marketing_agent.db.marketing_campaigns.find(
            {"status": "active"}
        ).to_list(length=None)
        
        # Remove MongoDB _id field
        for campaign in campaigns:
            campaign.pop('_id', None)
        
        return {
            "success": True,
            "total_campaigns": len(campaigns),
            "campaigns": campaigns
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/marketing/performance")
async def get_marketing_performance():
    """Get marketing campaign performance"""
    try:
        performance = await orchestrator.marketing_agent.track_campaign_performance()
        
        return {
            "success": True,
            "performance": performance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crm/leads")
async def capture_lead(lead: LeadInput):
    """Capture a new lead"""
    try:
        lead_data = {
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "product_interest": lead.product_interest,
            "budget_range": lead.budget_range,
            "timeline": lead.timeline,
            "source": lead.source
        }
        
        lead_id = await orchestrator.crm_agent.capture_lead(lead.source, lead_data)
        
        return {
            "success": True,
            "message": "Lead captured successfully",
            "lead_id": lead_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crm/leads")
async def get_all_leads(status: Optional[str] = None, limit: int = 50):
    """Get all leads with optional status filter"""
    try:
        query = {}
        if status:
            query["status"] = status
        
        leads = await orchestrator.crm_agent.db.leads.find(query).limit(limit).to_list(length=None)
        
        # Remove MongoDB _id field
        for lead in leads:
            lead.pop('_id', None)
        
        return {
            "success": True,
            "total_leads": len(leads),
            "leads": leads
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crm/leads/{lead_id}")
async def get_lead_details(lead_id: str):
    """Get detailed information about a specific lead"""
    try:
        lead = await orchestrator.crm_agent.db.leads.find_one({"id": lead_id})
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Remove MongoDB _id field
        lead.pop('_id', None)
        
        return {
            "success": True,
            "lead": lead
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crm/follow-ups")
async def process_follow_ups():
    """Process all pending follow-ups"""
    try:
        follow_ups = await orchestrator.crm_agent.process_follow_ups()
        
        return {
            "success": True,
            "message": f"Processed {len(follow_ups)} follow-ups",
            "follow_ups": follow_ups
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crm/reports")
async def get_crm_reports():
    """Get CRM performance reports"""
    try:
        report = await orchestrator.crm_agent.generate_crm_reports()
        
        return {
            "success": True,
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/marketing-crm/dashboard")
async def get_marketing_crm_dashboard():
    """Get complete Marketing & CRM dashboard data"""
    try:
        # Get marketing performance
        marketing_performance = await orchestrator.marketing_agent.track_campaign_performance()
        
        # Get CRM reports
        crm_report = await orchestrator.crm_agent.generate_crm_reports()
        
        # Get active campaigns
        campaigns = await orchestrator.marketing_agent.db.marketing_campaigns.find(
            {"status": "active"}
        ).to_list(length=None)
        
        # Get recent leads
        recent_leads = await orchestrator.crm_agent.db.leads.find().sort(
            "created_at", -1
        ).limit(10).to_list(length=None)
        
        # Remove MongoDB _id fields
        for campaign in campaigns:
            campaign.pop('_id', None)
        for lead in recent_leads:
            lead.pop('_id', None)
        
        return {
            "success": True,
            "dashboard": {
                "marketing": {
                    "total_campaigns": marketing_performance["total_campaigns"],
                    "total_budget": marketing_performance["total_budget"],
                    "expected_monthly_leads": marketing_performance["expected_monthly_leads"],
                    "campaigns": campaigns[:5]  # Top 5 campaigns
                },
                "crm": {
                    "total_leads": crm_report["total_leads"],
                    "monthly_leads": crm_report["monthly_leads"],
                    "lead_distribution": crm_report["lead_distribution"],
                    "conversion_funnel": crm_report["conversion_funnel"],
                    "recent_leads": recent_leads
                },
                "targets_vs_actual": {
                    "target_leads": marketing_performance.get("expected_monthly_leads", 100),
                    "actual_leads": crm_report["monthly_leads"],
                    "target_achievement": round((crm_report["monthly_leads"] / max(1, marketing_performance.get("expected_monthly_leads", 100))) * 100, 2)
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/automation/run-daily")
async def run_daily_automation():
    """Run daily AI automation tasks"""
    try:
        result = await orchestrator.run_daily_automation()
        
        return {
            "success": True,
            "message": "Daily automation completed successfully",
            "results": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/marketing/simulate-leads")
async def simulate_leads(num_leads: int = 5):
    """Simulate lead generation for testing (admin only)"""
    try:
        if num_leads > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 leads can be simulated at once")
        
        leads = await orchestrator.simulate_lead_generation(num_leads)
        
        return {
            "success": True,
            "message": f"Successfully simulated {len(leads)} leads",
            "lead_ids": leads
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
