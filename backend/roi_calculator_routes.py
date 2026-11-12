"""
ROI Calculator API Routes
Endpoints for store ROI analysis, pre-feasibility, and breakeven calculations
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from database import get_db
from roi_calculator_service import ROICalculatorService
import json
import os
import logging

router = APIRouter(prefix="/roi-calculator", tags=["ROI Calculator"])
logger = logging.getLogger(__name__)

# Pydantic Models

class PreFeasibilityRequest(BaseModel):
    city: str = Field(..., description="City name")
    city_tier: str = Field(..., description="tier_1_city, tier_2_city, or tier_3_city")
    store_size_sqft: int = Field(..., ge=100, description="Store size in square feet")
    store_type: str = Field(default="standard", description="premium, standard, or budget")
    product_categories: List[str] = Field(..., description="List of product categories")
    investment_budget: Optional[float] = Field(None, description="Available investment budget")
    target_monthly_revenue: Optional[float] = Field(None, description="Target monthly revenue")
    use_historical_data: bool = Field(default=True, description="Use historical data if available")

class BreakevenRequest(BaseModel):
    store_name: str = Field(..., description="Name of the store")
    monthly_rent: float = Field(..., ge=0, description="Monthly rent amount")
    security_deposit: float = Field(..., ge=0, description="Security deposit paid")
    interior_setup_cost: float = Field(..., ge=0, description="Interior and setup cost")
    initial_inventory: float = Field(..., ge=0, description="Initial inventory investment")
    staff_salaries: float = Field(..., ge=0, description="Monthly staff salaries")
    utilities: float = Field(..., ge=0, description="Monthly utilities cost")
    other_expenses: float = Field(default=0, description="Other monthly expenses")
    expected_gross_margin: float = Field(..., gt=0, le=1, description="Expected gross margin (0.1 to 1.0)")
    target_breakeven_years: int = Field(default=2, ge=1, le=10, description="Target breakeven in years")

class StoreAnalysisRequest(BaseModel):
    store_id: str = Field(..., description="Store ID to analyze")
    period_months: int = Field(default=12, ge=1, le=60, description="Analysis period in months")

class CompetitorSearchRequest(BaseModel):
    location: str = Field(..., description="Location/address to search near")
    radius_km: int = Field(default=5, ge=1, le=50, description="Search radius in km")

class CentralOverheadRequest(BaseModel):
    monthly_loan_emi: float = Field(default=0, ge=0, description="Monthly loan EMI")
    monthly_od_interest: float = Field(default=0, ge=0, description="Monthly OD interest")
    other_central_costs: float = Field(default=0, ge=0, description="Other central costs")


# ==================== ENDPOINTS ====================

@router.post("/pre-feasibility")
async def pre_feasibility_analysis(request: PreFeasibilityRequest, db=Depends(get_db)):
    """
    Generate pre-feasibility analysis for a new store location
    
    Use this to understand:
    - Recommended rent range
    - Sales targets needed
    - Staff requirements
    - Initial investment breakdown
    - Projected profitability
    """
    try:
        service = ROICalculatorService(db)
        result = await service.pre_feasibility_analysis(
            city=request.city,
            city_tier=request.city_tier,
            store_size_sqft=request.store_size_sqft,
            store_type=request.store_type,
            product_categories=request.product_categories,
            investment_budget=request.investment_budget,
            target_monthly_revenue=request.target_monthly_revenue,
            use_historical_data=request.use_historical_data
        )
        return result
    except Exception as e:
        logger.error(f"Pre-feasibility error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/breakeven")
async def breakeven_analysis(request: BreakevenRequest, db=Depends(get_db)):
    """
    Calculate breakeven analysis for a finalized store with known expenses
    
    Returns:
    - Breakeven revenue target
    - Timeline to recover investment
    - Year-wise projections
    - Sensitivity analysis
    """
    try:
        service = ROICalculatorService(db)
        result = await service.breakeven_analysis(
            store_name=request.store_name,
            monthly_rent=request.monthly_rent,
            security_deposit=request.security_deposit,
            interior_setup_cost=request.interior_setup_cost,
            initial_inventory=request.initial_inventory,
            staff_salaries=request.staff_salaries,
            utilities=request.utilities,
            other_expenses=request.other_expenses,
            expected_gross_margin=request.expected_gross_margin,
            target_breakeven_years=request.target_breakeven_years
        )
        return result
    except Exception as e:
        logger.error(f"Breakeven error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/existing-store")
async def existing_store_analysis(request: StoreAnalysisRequest, db=Depends(get_db)):
    """
    Analyze ROI and performance of an existing store
    
    Uses Tally imported data to calculate:
    - Revenue analysis
    - Profitability metrics
    - ITC/GST analysis
    - Performance rating
    """
    try:
        service = ROICalculatorService(db)
        result = await service.existing_store_analysis(
            store_id=request.store_id,
            period_months=request.period_months
        )
        return result
    except Exception as e:
        logger.error(f"Store analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/business-overview")
async def business_overview(
    period_months: int = Query(default=12, ge=1, le=60),
    db=Depends(get_db)
):
    """
    Get consolidated ROI analysis for all stores
    
    Includes:
    - Individual store performance
    - Consolidated financials
    - Central overhead (loan/OD)
    - Net business profit
    """
    try:
        service = ROICalculatorService(db)
        result = await service.business_overview(period_months=period_months)
        return result
    except Exception as e:
        logger.error(f"Business overview error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set-central-overhead")
async def set_central_overhead(request: CentralOverheadRequest, db=Depends(get_db)):
    """
    Set business-level central overhead (loan/OD interest)
    This is tracked separately and not allocated to individual stores
    """
    try:
        overhead_data = {
            "type": "financial",
            "monthly_loan_emi": request.monthly_loan_emi,
            "monthly_od_interest": request.monthly_od_interest,
            "other_central_costs": request.other_central_costs,
            "total_central_overhead": request.monthly_loan_emi + request.monthly_od_interest + request.other_central_costs,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.business_settings.update_one(
            {"type": "financial"},
            {"$set": overhead_data},
            upsert=True
        )
        
        return {
            "status": "success",
            "message": "Central overhead updated successfully",
            "data": overhead_data
        }
    except Exception as e:
        logger.error(f"Set overhead error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/central-overhead")
async def get_central_overhead(db=Depends(get_db)):
    """Get current central overhead settings"""
    try:
        settings = await db.business_settings.find_one({"type": "financial"}, {"_id": 0})
        return {
            "status": "success",
            "data": settings or {
                "monthly_loan_emi": 0,
                "monthly_od_interest": 0,
                "other_central_costs": 0,
                "total_central_overhead": 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stores")
async def get_stores(db=Depends(get_db)):
    """Get list of all stores for analysis"""
    try:
        stores = await db.stores.find({}, {"_id": 0}).to_list(100)
        if not stores:
            # Return default stores if none configured
            stores = [
                {"id": "store_1", "name": "Store 1 - Main", "location": "Location 1"},
                {"id": "store_2", "name": "Store 2", "location": "Location 2"},
                {"id": "store_3", "name": "Store 3", "location": "Location 3"},
                {"id": "store_4", "name": "Store 4", "location": "Location 4"}
            ]
        return {"status": "success", "stores": stores}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stores")
async def create_store(
    name: str,
    location: str,
    city: str,
    city_tier: str = "tier_2_city",
    store_size_sqft: int = 500,
    db=Depends(get_db)
):
    """Create/register a new store for tracking"""
    try:
        import uuid
        store_data = {
            "id": str(uuid.uuid4())[:8],
            "name": name,
            "location": location,
            "city": city,
            "city_tier": city_tier,
            "store_size_sqft": store_size_sqft,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.stores.insert_one(store_data)
        store_data.pop("_id", None)
        
        return {"status": "success", "store": store_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/industry-benchmarks")
async def get_industry_benchmarks():
    """Get industry benchmark data for home appliance retail"""
    from roi_calculator_service import INDUSTRY_BENCHMARKS
    return {
        "status": "success",
        "benchmarks": INDUSTRY_BENCHMARKS
    }


# ==================== COMPETITOR ANALYSIS ====================

@router.post("/competitor-analysis")
async def competitor_analysis(request: CompetitorSearchRequest, db=Depends(get_db)):
    """
    Find competitor stores near a location using Google Maps
    
    Note: Requires Google Maps API key configured
    """
    try:
        # Check for Google Maps API key
        google_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        
        if not google_api_key:
            # Return mock data if no API key
            return {
                "status": "success",
                "message": "Google Maps API key not configured. Showing sample data.",
                "location": request.location,
                "radius_km": request.radius_km,
                "competitors": [
                    {
                        "name": "Sample Competitor 1",
                        "address": "Near " + request.location,
                        "rating": 4.2,
                        "type": "Home Appliance Store",
                        "note": "Configure GOOGLE_MAPS_API_KEY for real data"
                    }
                ],
                "api_configured": False
            }
        
        # If API key exists, make actual call
        import httpx
        
        async with httpx.AsyncClient() as client:
            # First, geocode the location
            geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json"
            geocode_response = await client.get(geocode_url, params={
                "address": request.location,
                "key": google_api_key
            })
            geocode_data = geocode_response.json()
            
            if geocode_data["status"] != "OK":
                return {"status": "error", "message": "Could not find location"}
            
            lat = geocode_data["results"][0]["geometry"]["location"]["lat"]
            lng = geocode_data["results"][0]["geometry"]["location"]["lng"]
            
            # Search for appliance stores nearby
            places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            places_response = await client.get(places_url, params={
                "location": f"{lat},{lng}",
                "radius": request.radius_km * 1000,
                "keyword": "home appliance store electronics",
                "key": google_api_key
            })
            places_data = places_response.json()
            
            competitors = []
            for place in places_data.get("results", [])[:10]:
                competitors.append({
                    "name": place.get("name"),
                    "address": place.get("vicinity"),
                    "rating": place.get("rating"),
                    "user_ratings_total": place.get("user_ratings_total"),
                    "types": place.get("types", []),
                    "place_id": place.get("place_id")
                })
            
            return {
                "status": "success",
                "location": request.location,
                "coordinates": {"lat": lat, "lng": lng},
                "radius_km": request.radius_km,
                "competitors_found": len(competitors),
                "competitors": competitors,
                "api_configured": True
            }
            
    except Exception as e:
        logger.error(f"Competitor analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== REPORT GENERATION ====================

@router.post("/generate-report/{report_type}")
async def generate_report(
    report_type: str,
    format: str = Query(default="json", enum=["json", "csv"]),
    db=Depends(get_db)
):
    """
    Generate downloadable ROI report
    
    report_type: pre_feasibility, breakeven, store_analysis, business_overview
    format: json or csv
    """
    try:
        # For now, return JSON data that can be used by frontend
        # PDF generation would require additional library like reportlab
        
        service = ROICalculatorService(db)
        
        if report_type == "business_overview":
            data = await service.business_overview(12)
        else:
            return {"status": "error", "message": "Use specific endpoints for other report types"}
        
        if format == "csv":
            # Convert to CSV format
            import csv
            import io
            
            output = io.StringIO()
            if report_type == "business_overview" and data.get("store_wise_analysis"):
                writer = csv.writer(output)
                writer.writerow(["Store", "Revenue", "Gross Profit", "Net Profit", "Margin %"])
                for store in data["store_wise_analysis"]:
                    writer.writerow([
                        store["store_info"]["store_name"],
                        store["revenue_analysis"]["total_revenue"],
                        store["profitability"]["gross_profit"],
                        store["profitability"]["net_profit"],
                        store["profitability"]["gross_margin_percentage"]
                    ])
                
                return {
                    "status": "success",
                    "format": "csv",
                    "data": output.getvalue()
                }
        
        return {
            "status": "success",
            "format": "json",
            "data": data
        }
        
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
