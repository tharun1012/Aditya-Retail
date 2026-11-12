"""
Purchase Order (PO) Management Routes
PO is mandatory before creating a Purchase Bill
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import uuid
import logging

from database import get_db

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])
logger = logging.getLogger(__name__)


# ============ MODELS ============

class POItem(BaseModel):
    product_name: str
    hsn_code: Optional[str] = ""
    quantity: int
    rate: float
    tax_rate: float = 18.0
    estimated_delivery_date: Optional[str] = None


class POVendorInfo(BaseModel):
    name: str
    phone: Optional[str] = ""
    email: Optional[str] = ""
    gst_number: Optional[str] = ""
    msme_udyam_number: Optional[str] = ""
    address: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""


class PurchaseOrderCreate(BaseModel):
    vendor: POVendorInfo
    items: List[POItem]
    expected_delivery_date: Optional[str] = None
    delivery_address: Optional[str] = ""
    payment_terms: str = "30 days"
    notes: Optional[str] = ""
    priority: str = "normal"  # low, normal, high, urgent


class PurchaseOrderUpdate(BaseModel):
    vendor: Optional[POVendorInfo] = None
    items: Optional[List[POItem]] = None
    status: Optional[str] = None
    expected_delivery_date: Optional[str] = None
    delivery_address: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[str] = None


# ============ ROUTES ============

@router.post("/create")
async def create_purchase_order(po_data: PurchaseOrderCreate, db = Depends(get_db)):
    """Create a new Purchase Order"""
    try:
        # Generate PO number
        today = datetime.now(timezone.utc)
        po_count = await db.purchase_orders.count_documents({
            "created_at": {"$gte": today.replace(hour=0, minute=0, second=0).isoformat()}
        })
        po_number = f"PO-{today.strftime('%Y%m%d')}-{str(po_count + 1).zfill(4)}"
        
        # Calculate totals
        items = []
        subtotal = 0
        total_tax = 0
        
        for item in po_data.items:
            item_total = item.quantity * item.rate
            tax_amt = item_total * (item.tax_rate / 100)
            
            items.append({
                "product_name": item.product_name,
                "hsn_code": item.hsn_code,
                "quantity": item.quantity,
                "rate": item.rate,
                "tax_rate": item.tax_rate,
                "tax_amount": round(tax_amt, 2),
                "total": round(item_total + tax_amt, 2),
                "estimated_delivery_date": item.estimated_delivery_date
            })
            subtotal += item_total
            total_tax += tax_amt
        
        po_doc = {
            "id": str(uuid.uuid4()),
            "po_number": po_number,
            "vendor": po_data.vendor.dict(),
            "items": items,
            "subtotal": round(subtotal, 2),
            "total_tax": round(total_tax, 2),
            "grand_total": round(subtotal + total_tax, 2),
            "expected_delivery_date": po_data.expected_delivery_date,
            "delivery_address": po_data.delivery_address,
            "payment_terms": po_data.payment_terms,
            "notes": po_data.notes,
            "priority": po_data.priority,
            "status": "pending",  # pending, approved, sent, partial, completed, cancelled
            "created_at": today.isoformat(),
            "updated_at": today.isoformat(),
            "created_by": "admin",
            "bill_created": False,
            "linked_bill_numbers": []
        }
        
        await db.purchase_orders.insert_one(po_doc)
        po_doc.pop('_id', None)
        
        return {
            "status": "success",
            "message": f"Purchase Order {po_number} created successfully",
            "po": po_doc
        }
    except Exception as e:
        logger.error(f"Failed to create PO: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_purchase_orders(
    status: Optional[str] = None,
    vendor_name: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """List all purchase orders with filters"""
    try:
        query = {}
        
        if status:
            query["status"] = status
        if vendor_name:
            query["vendor.name"] = {"$regex": vendor_name, "$options": "i"}
        if from_date:
            query["created_at"] = {"$gte": from_date}
        if to_date:
            if "created_at" in query:
                query["created_at"]["$lte"] = to_date + "T23:59:59"
            else:
                query["created_at"] = {"$lte": to_date + "T23:59:59"}
        
        total = await db.purchase_orders.count_documents(query)
        skip = (page - 1) * limit
        
        pos = await db.purchase_orders.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        return {
            "status": "success",
            "total": total,
            "page": page,
            "limit": limit,
            "purchase_orders": pos
        }
    except Exception as e:
        logger.error(f"Failed to list POs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{po_id}")
async def get_purchase_order(po_id: str, db = Depends(get_db)):
    """Get a specific purchase order"""
    try:
        po = await db.purchase_orders.find_one(
            {"$or": [{"id": po_id}, {"po_number": po_id}]},
            {"_id": 0}
        )
        if not po:
            raise HTTPException(status_code=404, detail="Purchase Order not found")
        
        return {"status": "success", "po": po}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{po_id}/status")
async def update_po_status(po_id: str, status: str, db = Depends(get_db)):
    """Update PO status"""
    try:
        valid_statuses = ["pending", "approved", "sent", "partial", "completed", "cancelled"]
        if status.lower() not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Use: {valid_statuses}")
        
        result = await db.purchase_orders.update_one(
            {"$or": [{"id": po_id}, {"po_number": po_id}]},
            {"$set": {
                "status": status.lower(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Purchase Order not found")
        
        return {"status": "success", "message": f"PO status updated to {status}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending/for-billing")
async def get_pos_pending_for_billing(db = Depends(get_db)):
    """Get POs that are approved/sent but don't have bills created"""
    try:
        pending_pos = await db.purchase_orders.find({
            "status": {"$in": ["approved", "sent", "partial"]},
            "bill_created": {"$ne": True}
        }, {"_id": 0}).sort("created_at", 1).to_list(None)
        
        return {
            "status": "success",
            "total": len(pending_pos),
            "pending_pos": pending_pos,
            "message": "These POs can be used to create purchase bills"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{po_id}")
async def delete_purchase_order(po_id: str, db = Depends(get_db)):
    """Delete a PO (only if not linked to any bill)"""
    try:
        po = await db.purchase_orders.find_one(
            {"$or": [{"id": po_id}, {"po_number": po_id}]}
        )
        if not po:
            raise HTTPException(status_code=404, detail="Purchase Order not found")
        
        if po.get("linked_bill_numbers"):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete PO. Linked to bills: {', '.join(po.get('linked_bill_numbers'))}"
            )
        
        await db.purchase_orders.delete_one({"$or": [{"id": po_id}, {"po_number": po_id}]})
        
        return {"status": "success", "message": f"PO {po.get('po_number')} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{po_id}")
async def update_purchase_order(po_id: str, update_data: PurchaseOrderUpdate, db = Depends(get_db)):
    """Update a Purchase Order (only if pending or draft)"""
    try:
        po = await db.purchase_orders.find_one(
            {"$or": [{"id": po_id}, {"po_number": po_id}]}
        )
        if not po:
            raise HTTPException(status_code=404, detail="Purchase Order not found")
        
        # Only allow editing pending or draft POs
        if po.get("status") not in ["pending", "draft"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot edit PO with status '{po.get('status')}'. Only pending/draft POs can be edited."
            )
        
        update_fields = {"updated_at": datetime.now(timezone.utc).isoformat()}
        
        if update_data.vendor:
            update_fields["vendor"] = update_data.vendor.dict()
        
        if update_data.items:
            # Recalculate totals
            items_data = []
            subtotal = 0
            total_tax = 0
            
            for item in update_data.items:
                item_total = item.rate * item.quantity
                item_tax = item_total * (item.tax_rate / 100)
                items_data.append({
                    **item.dict(),
                    "total": round(item_total, 2),
                    "tax_amount": round(item_tax, 2)
                })
                subtotal += item_total
                total_tax += item_tax
            
            update_fields["items"] = items_data
            update_fields["totals"] = {
                "subtotal": round(subtotal, 2),
                "tax": round(total_tax, 2),
                "grand_total": round(subtotal + total_tax, 2)
            }
        
        if update_data.expected_delivery_date is not None:
            update_fields["expected_delivery_date"] = update_data.expected_delivery_date
        
        if update_data.delivery_address is not None:
            update_fields["delivery_address"] = update_data.delivery_address
        
        if update_data.payment_terms is not None:
            update_fields["payment_terms"] = update_data.payment_terms
        
        if update_data.notes is not None:
            update_fields["notes"] = update_data.notes
        
        if update_data.priority is not None:
            update_fields["priority"] = update_data.priority
        
        await db.purchase_orders.update_one(
            {"$or": [{"id": po_id}, {"po_number": po_id}]},
            {"$set": update_fields}
        )
        
        updated_po = await db.purchase_orders.find_one(
            {"$or": [{"id": po_id}, {"po_number": po_id}]},
            {"_id": 0}
        )
        
        return {
            "status": "success",
            "message": f"PO {po.get('po_number')} updated successfully",
            "purchase_order": updated_po
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
