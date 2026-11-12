"""
Autonomous Procurement Routes - Phase 2
API endpoints for autonomous procurement features
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from database import get_db
from autonomous_procurement_service import AutonomousProcurementService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/autonomous-procurement", tags=["Autonomous Procurement"])

class VendorStockReport(BaseModel):
    vendor_name: str
    report_data: Dict[str, Dict[str, Any]]  # {"product_name": {"available": qty, "price": price}}

@router.post("/run-check")
async def run_autonomous_check(db = Depends(get_db)):
    """
    Manually trigger autonomous procurement check
    Checks inventory levels and auto-generates draft POs for low-stock items
    """
    try:
        service = AutonomousProcurementService(db)
        result = await service.run_autonomous_procurement_check()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/low-stock-items")
async def get_low_stock_items(db = Depends(get_db)):
    """Get list of products below reorder level"""
    try:
        service = AutonomousProcurementService(db)
        low_stock_items = await service.check_low_stock_items()
        
        return {
            "status": "success",
            "count": len(low_stock_items),
            "items": low_stock_items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse-vendor-report")
async def parse_vendor_report(report: VendorStockReport, db = Depends(get_db)):
    """
    Parse vendor stock report and match with our inventory needs
    
    Example request body:
    {
        "vendor_name": "Bosch",
        "report_data": {
            "Bosch Washing Machine 7kg": {"available": 50, "price": 25000},
            "Bosch Dishwasher": {"available": 30, "price": 35000}
        }
    }
    """
    try:
        service = AutonomousProcurementService(db)
        result = await service.parse_vendor_stock_report(
            report.vendor_name, 
            report.report_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-from-vendor-match")
async def generate_po_from_vendor_match(
    vendor_name: str,
    matches: List[Dict[str, Any]],
    db = Depends(get_db)
):
    """
    Generate draft POs from vendor stock report matches
    """
    try:
        service = AutonomousProcurementService(db)
        drafts = await service.generate_po_from_vendor_match(matches, vendor_name)
        
        return {
            "status": "success",
            "message": f"Created {len(drafts)} draft POs from vendor matches",
            "drafts_created": len(drafts),
            "drafts": [
                {
                    "draft_number": d["draft_number"],
                    "product_name": d["items"][0]["product_name"],
                    "quantity": d["items"][0]["quantity"],
                    "total_amount": d["total_amount"]
                }
                for d in drafts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notifications")
async def get_purchase_notifications(
    role: str = "admin",
    unread_only: bool = True,
    db = Depends(get_db)
):
    """
    Get notifications for purchase managers
    """
    try:
        query = {
            "target_roles": role
        }
        
        if unread_only:
            query["read"] = False
        
        notifications = await db.notifications.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).limit(50).to_list(50)
        
        return {
            "status": "success",
            "count": len(notifications),
            "notifications": notifications
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/notifications/{notification_id}/mark-read")
async def mark_notification_read(notification_id: str, db = Depends(get_db)):
    """Mark a notification as read"""
    try:
        result = await db.notifications.update_one(
            {"id": notification_id},
            {"$set": {"read": True}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {
            "status": "success",
            "message": "Notification marked as read"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard-summary")
async def get_autonomous_dashboard_summary(db = Depends(get_db)):
    """
    Get summary dashboard for autonomous procurement system
    """
    try:
        service = AutonomousProcurementService(db)
        
        # Get low stock items
        low_stock_items = await service.check_low_stock_items()
        
        # Get pending auto-generated drafts
        auto_drafts = await db.purchase_drafts.find(
            {
                "status": "draft",
                "auto_generated": True
            },
            {"_id": 0}
        ).to_list(None)
        
        # Get unread notifications
        notifications = await db.notifications.find(
            {
                "read": False,
                "type": "auto_draft_po_created"
            },
            {"_id": 0}
        ).to_list(None)
        
        # Calculate total value of auto-generated drafts
        total_draft_value = sum(draft.get("total_amount", 0) for draft in auto_drafts)
        
        return {
            "status": "success",
            "summary": {
                "low_stock_items_count": len(low_stock_items),
                "pending_auto_drafts_count": len(auto_drafts),
                "total_draft_value": total_draft_value,
                "unread_notifications_count": len(notifications),
                "low_stock_items": low_stock_items[:10],  # Top 10
                "recent_auto_drafts": auto_drafts[:5]  # Recent 5
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
