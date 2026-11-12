"""
Landed Cost Routes
Calculate total cost of goods including freight, customs, insurance, and other expenses
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from database import get_db
import uuid
import logging

router = APIRouter(prefix="/landed-cost", tags=["Landed Cost"])
logger = logging.getLogger(__name__)


# ============ MODELS ============

class LandedCostComponent(BaseModel):
    name: str  # freight, customs_duty, insurance, handling, etc.
    amount: float
    is_percentage: bool = False  # If true, amount is percentage of base cost
    allocation_method: str = "value"  # value, quantity, weight


class LandedCostCreate(BaseModel):
    purchase_bill_id: str
    additional_costs: List[LandedCostComponent]
    notes: Optional[str] = ""


class LandedCostTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    components: List[LandedCostComponent]
    is_default: bool = False


# ============ COST TEMPLATES ============

@router.post("/templates/create")
async def create_landed_cost_template(template: LandedCostTemplateCreate, db = Depends(get_db)):
    """Create a reusable landed cost template"""
    try:
        template_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        # If this is default, unset other defaults
        if template.is_default:
            await db.landed_cost_templates.update_many(
                {"is_default": True},
                {"$set": {"is_default": False}}
            )
        
        template_data = {
            "id": template_id,
            "name": template.name,
            "description": template.description,
            "components": [c.dict() for c in template.components],
            "is_default": template.is_default,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
        
        await db.landed_cost_templates.insert_one(template_data)
        
        return {
            "status": "success",
            "message": f"Template '{template.name}' created",
            "template_id": template_id
        }
        
    except Exception as e:
        logger.error(f"Create template failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_landed_cost_templates(db = Depends(get_db)):
    """Get all landed cost templates"""
    try:
        templates = await db.landed_cost_templates.find(
            {"is_active": True},
            {"_id": 0}
        ).sort("name", 1).to_list(length=100)
        
        return {"status": "success", "templates": templates}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/templates/{template_id}")
async def delete_template(template_id: str, db = Depends(get_db)):
    """Delete a landed cost template"""
    try:
        result = await db.landed_cost_templates.update_one(
            {"id": template_id},
            {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {"status": "success", "message": "Template deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ LANDED COST CALCULATION ============

@router.post("/calculate")
async def calculate_landed_cost(data: LandedCostCreate, db = Depends(get_db)):
    """Calculate and apply landed cost to a purchase bill"""
    try:
        # Get purchase bill
        bill = await db.purchase_bills.find_one({"id": data.purchase_bill_id})
        if not bill:
            raise HTTPException(status_code=404, detail="Purchase bill not found")
        
        items = bill.get("items", [])
        base_total = bill.get("grand_total", 0)
        
        if not items:
            raise HTTPException(status_code=400, detail="Purchase bill has no items")
        
        # Calculate total weight and quantity for allocation
        total_quantity = sum(item.get("quantity", 0) for item in items)
        total_weight = sum(item.get("quantity", 0) * item.get("weight", 1) for item in items)
        
        # Calculate total additional costs
        total_additional_cost = 0
        cost_breakdown = []
        
        for component in data.additional_costs:
            if component.is_percentage:
                cost_amount = base_total * (component.amount / 100)
            else:
                cost_amount = component.amount
            
            total_additional_cost += cost_amount
            cost_breakdown.append({
                "name": component.name,
                "amount": cost_amount,
                "allocation_method": component.allocation_method
            })
        
        # Allocate costs to items
        items_with_landed_cost = []
        
        for item in items:
            item_base_cost = item.get("total", 0)
            item_quantity = item.get("quantity", 0)
            item_weight = item_quantity * item.get("weight", 1)
            
            # Calculate item's share of additional costs
            item_additional = 0
            item_cost_details = []
            
            for cost in cost_breakdown:
                if cost["allocation_method"] == "value":
                    share = (item_base_cost / base_total) if base_total > 0 else 0
                elif cost["allocation_method"] == "quantity":
                    share = (item_quantity / total_quantity) if total_quantity > 0 else 0
                elif cost["allocation_method"] == "weight":
                    share = (item_weight / total_weight) if total_weight > 0 else 0
                else:
                    share = (item_base_cost / base_total) if base_total > 0 else 0
                
                cost_share = cost["amount"] * share
                item_additional += cost_share
                item_cost_details.append({
                    "name": cost["name"],
                    "amount": round(cost_share, 2)
                })
            
            landed_total = item_base_cost + item_additional
            landed_unit_cost = (landed_total / item_quantity) if item_quantity > 0 else 0
            
            items_with_landed_cost.append({
                **item,
                "base_cost": item_base_cost,
                "additional_costs": item_cost_details,
                "total_additional": round(item_additional, 2),
                "landed_cost": round(landed_total, 2),
                "landed_unit_cost": round(landed_unit_cost, 2)
            })
        
        # Save landed cost record
        now = datetime.now(timezone.utc).isoformat()
        landed_cost_id = str(uuid.uuid4())
        
        landed_cost_record = {
            "id": landed_cost_id,
            "purchase_bill_id": data.purchase_bill_id,
            "bill_number": bill.get("bill_number"),
            "vendor_name": bill.get("vendor", {}).get("name"),
            "base_total": base_total,
            "additional_costs": cost_breakdown,
            "total_additional_cost": round(total_additional_cost, 2),
            "landed_total": round(base_total + total_additional_cost, 2),
            "items": items_with_landed_cost,
            "notes": data.notes,
            "created_at": now
        }
        
        await db.landed_costs.insert_one(landed_cost_record)
        
        # Update purchase bill with landed cost
        await db.purchase_bills.update_one(
            {"id": data.purchase_bill_id},
            {"$set": {
                "has_landed_cost": True,
                "landed_cost_id": landed_cost_id,
                "landed_total": round(base_total + total_additional_cost, 2),
                "updated_at": now
            }}
        )
        
        return {
            "status": "success",
            "message": "Landed cost calculated successfully",
            "landed_cost_id": landed_cost_id,
            "summary": {
                "base_total": base_total,
                "additional_costs": round(total_additional_cost, 2),
                "landed_total": round(base_total + total_additional_cost, 2),
                "cost_increase_percent": round((total_additional_cost / base_total * 100), 2) if base_total > 0 else 0
            },
            "items": items_with_landed_cost
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Calculate landed cost failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bill/{purchase_bill_id}")
async def get_landed_cost_for_bill(purchase_bill_id: str, db = Depends(get_db)):
    """Get landed cost details for a purchase bill"""
    try:
        landed_cost = await db.landed_costs.find_one(
            {"purchase_bill_id": purchase_bill_id},
            {"_id": 0}
        )
        
        if not landed_cost:
            # Return bill without landed cost
            bill = await db.purchase_bills.find_one({"id": purchase_bill_id}, {"_id": 0})
            if not bill:
                raise HTTPException(status_code=404, detail="Purchase bill not found")
            
            return {
                "status": "success",
                "has_landed_cost": False,
                "bill": bill
            }
        
        return {
            "status": "success",
            "has_landed_cost": True,
            "landed_cost": landed_cost
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_landed_cost_history(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    vendor: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    db = Depends(get_db)
):
    """Get landed cost calculation history"""
    try:
        query = {}
        
        if from_date:
            query["created_at"] = {"$gte": from_date}
        if to_date:
            if "created_at" in query:
                query["created_at"]["$lte"] = to_date
            else:
                query["created_at"] = {"$lte": to_date}
        
        if vendor:
            query["vendor_name"] = {"$regex": vendor, "$options": "i"}
        
        skip = (page - 1) * limit
        
        records = await db.landed_costs.find(query, {"_id": 0, "items": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
        total = await db.landed_costs.count_documents(query)
        
        return {
            "status": "success",
            "records": records,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ PRODUCT COST UPDATE ============

@router.post("/update-product-costs/{landed_cost_id}")
async def update_product_costs(landed_cost_id: str, db = Depends(get_db)):
    """Update product cost prices based on landed cost calculation"""
    try:
        landed_cost = await db.landed_costs.find_one({"id": landed_cost_id})
        if not landed_cost:
            raise HTTPException(status_code=404, detail="Landed cost record not found")
        
        updated_count = 0
        now = datetime.now(timezone.utc).isoformat()
        
        for item in landed_cost.get("items", []):
            product_id = item.get("product_id")
            if not product_id:
                continue
            
            landed_unit_cost = item.get("landed_unit_cost", 0)
            
            # Update product cost price
            result = await db.products.update_one(
                {"id": product_id},
                {"$set": {
                    "cost_price": landed_unit_cost,
                    "last_cost_update": now,
                    "last_landed_cost_id": landed_cost_id
                }}
            )
            
            if result.modified_count > 0:
                updated_count += 1
        
        return {
            "status": "success",
            "message": f"Updated cost price for {updated_count} products",
            "updated_count": updated_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update product costs failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ STATISTICS ============

@router.get("/stats")
async def get_landed_cost_stats(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Get landed cost statistics"""
    try:
        query = {}
        
        if from_date:
            query["created_at"] = {"$gte": from_date}
        if to_date:
            if "created_at" in query:
                query["created_at"]["$lte"] = to_date
            else:
                query["created_at"] = {"$lte": to_date}
        
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": None,
                "total_records": {"$sum": 1},
                "total_base_cost": {"$sum": "$base_total"},
                "total_additional": {"$sum": "$total_additional_cost"},
                "total_landed": {"$sum": "$landed_total"}
            }}
        ]
        
        result = await db.landed_costs.aggregate(pipeline).to_list(length=1)
        stats = result[0] if result else {
            "total_records": 0,
            "total_base_cost": 0,
            "total_additional": 0,
            "total_landed": 0
        }
        
        # Get cost breakdown by type
        breakdown_pipeline = [
            {"$match": query},
            {"$unwind": "$additional_costs"},
            {"$group": {
                "_id": "$additional_costs.name",
                "total_amount": {"$sum": "$additional_costs.amount"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"total_amount": -1}}
        ]
        
        breakdown = await db.landed_costs.aggregate(breakdown_pipeline).to_list(length=20)
        
        avg_increase = (stats.get("total_additional", 0) / stats.get("total_base_cost", 1) * 100) if stats.get("total_base_cost", 0) > 0 else 0
        
        return {
            "status": "success",
            "stats": {
                "total_records": stats.get("total_records", 0),
                "total_base_cost": round(stats.get("total_base_cost", 0), 2),
                "total_additional": round(stats.get("total_additional", 0), 2),
                "total_landed": round(stats.get("total_landed", 0), 2),
                "average_increase_percent": round(avg_increase, 2)
            },
            "cost_breakdown": [
                {
                    "name": b["_id"],
                    "total_amount": round(b["total_amount"], 2),
                    "count": b["count"]
                }
                for b in breakdown
            ]
        }
        
    except Exception as e:
        logger.error(f"Get landed cost stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
