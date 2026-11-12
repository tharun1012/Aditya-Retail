"""
Customer Purchase Order Management Routes
Handles customer POs received in response to quotations.
Flow: Quotation → Customer PO → Sales Order/Invoice
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from datetime import datetime, timezone
from database import get_db
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/customer-pos", tags=["Customer Purchase Orders"])


# ============ MODELS ============

class CustomerPOItem(BaseModel):
    product_id: Optional[str] = None
    brand: Optional[str] = None
    model_number: Optional[str] = None
    product_name: str
    description: Optional[str] = None
    hsn_code: Optional[str] = None
    quantity: int = 1
    unit_price: float
    gst_rate: float = 18.0


class CustomerPOCreate(BaseModel):
    store_code: str
    quotation_id: Optional[str] = None  # Link to original quotation
    quotation_number: Optional[str] = None
    customer_po_number: str  # Customer's own PO number
    customer_po_date: str  # Date on customer's PO
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_gst: Optional[str] = None
    customer_address: Optional[str] = None
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    items: List[CustomerPOItem]
    expected_delivery_date: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None


class CustomerPOUpdate(BaseModel):
    customer_po_number: Optional[str] = None
    customer_po_date: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_gst: Optional[str] = None
    customer_address: Optional[str] = None
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    items: Optional[List[CustomerPOItem]] = None
    expected_delivery_date: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


# ============ HELPER FUNCTIONS ============

def calculate_po_totals(items: List[dict]) -> dict:
    """Calculate totals for Customer PO"""
    subtotal = sum(item["unit_price"] * item["quantity"] for item in items)
    
    # Calculate tax by item
    total_cgst = 0
    total_sgst = 0
    for item in items:
        item_total = item["unit_price"] * item["quantity"]
        gst_rate = item.get("gst_rate", 18.0)
        item_gst = item_total * (gst_rate / 100)
        total_cgst += item_gst / 2
        total_sgst += item_gst / 2
    
    total_gst = total_cgst + total_sgst
    grand_total = subtotal + total_gst
    
    return {
        "subtotal": round(subtotal, 2),
        "cgst": round(total_cgst, 2),
        "sgst": round(total_sgst, 2),
        "total_gst": round(total_gst, 2),
        "grand_total": round(grand_total, 2)
    }


# ============ ROUTES ============

@router.post("/")
async def create_customer_po(po: CustomerPOCreate, db = Depends(get_db)):
    """Create a new Customer Purchase Order"""
    try:
        # Generate internal PO reference number
        today = datetime.now(timezone.utc)
        prefix = f"CPO-{today.strftime('%Y%m%d')}"
        
        # Count existing CPOs for today
        count = await db.customer_pos.count_documents({
            "created_at": {"$gte": today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()}
        })
        
        internal_ref = f"{prefix}-{count + 1:03d}"
        
        # Prepare items with calculated values
        items_data = [item.dict() for item in po.items]
        totals = calculate_po_totals(items_data)
        
        # Check if quotation exists and get details
        quotation_data = None
        if po.quotation_id:
            quotation = await db.quotations.find_one({"id": po.quotation_id})
            if quotation:
                quotation_data = {
                    "id": quotation.get("id"),
                    "quotation_number": quotation.get("quotation_number"),
                    "created_at": quotation.get("created_at")
                }
        
        po_data = {
            "id": str(uuid.uuid4()),
            "internal_reference": internal_ref,
            "customer_po_number": po.customer_po_number,
            "customer_po_date": po.customer_po_date,
            "store_code": po.store_code,
            "quotation_id": po.quotation_id,
            "quotation_number": po.quotation_number,
            "quotation_data": quotation_data,
            "customer": {
                "name": po.customer_name,
                "email": po.customer_email,
                "phone": po.customer_phone,
                "gst_number": po.customer_gst,
                "address": po.customer_address,
                "billing_address": po.billing_address or po.customer_address,
                "shipping_address": po.shipping_address or po.customer_address
            },
            "items": items_data,
            **totals,
            "expected_delivery_date": po.expected_delivery_date,
            "payment_terms": po.payment_terms,
            "notes": po.notes,
            "status": "pending",  # pending, converted_to_so, converted_to_invoice, cancelled
            "converted_to": None,  # Will hold SO/Invoice reference when converted
            "created_by": po.created_by,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.customer_pos.insert_one(po_data)
        
        # Update quotation status if linked
        if po.quotation_id:
            await db.quotations.update_one(
                {"id": po.quotation_id},
                {"$set": {
                    "status": "po_received",
                    "customer_po_reference": internal_ref,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
        
        return {
            "status": "success",
            "message": f"Customer PO recorded successfully",
            "id": po_data["id"],
            "internal_reference": internal_ref,
            "customer_po_number": po.customer_po_number,
            "grand_total": totals["grand_total"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Customer PO: {str(e)}")


@router.get("/")
async def get_customer_pos(
    store_code: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get all Customer POs with filters"""
    try:
        query = {}
        
        if store_code:
            query["store_code"] = store_code
        
        if status:
            query["status"] = status
        
        if search:
            query["$or"] = [
                {"customer_po_number": {"$regex": search, "$options": "i"}},
                {"internal_reference": {"$regex": search, "$options": "i"}},
                {"customer.name": {"$regex": search, "$options": "i"}},
                {"quotation_number": {"$regex": search, "$options": "i"}}
            ]
        
        skip = (page - 1) * limit
        
        pos = await db.customer_pos.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.customer_pos.count_documents(query)
        
        return {
            "status": "success",
            "customer_pos": pos,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Customer POs: {str(e)}")


@router.get("/pending")
async def get_pending_customer_pos(
    store_code: Optional[str] = None,
    db = Depends(get_db)
):
    """Get pending Customer POs (not yet converted to SO/Invoice)"""
    try:
        query = {"status": "pending"}
        if store_code:
            query["store_code"] = store_code
        
        pos = await db.customer_pos.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).to_list(None)
        
        return {
            "status": "success",
            "customer_pos": pos,
            "total": len(pos)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pending POs: {str(e)}")


@router.get("/by-quotation/{quotation_id}")
async def get_pos_by_quotation(quotation_id: str, db = Depends(get_db)):
    """Get Customer POs linked to a specific quotation"""
    try:
        pos = await db.customer_pos.find(
            {"quotation_id": quotation_id},
            {"_id": 0}
        ).to_list(None)
        
        return {
            "status": "success",
            "customer_pos": pos,
            "total": len(pos)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch POs: {str(e)}")


@router.get("/{po_id}")
async def get_customer_po(po_id: str, db = Depends(get_db)):
    """Get a specific Customer PO"""
    try:
        po = await db.customer_pos.find_one({"id": po_id}, {"_id": 0})
        if not po:
            raise HTTPException(status_code=404, detail="Customer PO not found")
        
        return {
            "status": "success",
            "customer_po": po
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Customer PO: {str(e)}")


@router.put("/{po_id}")
async def update_customer_po(po_id: str, po: CustomerPOUpdate, db = Depends(get_db)):
    """Update a Customer PO"""
    try:
        existing = await db.customer_pos.find_one({"id": po_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Customer PO not found")
        
        if existing.get("status") != "pending":
            raise HTTPException(status_code=400, detail="Cannot modify a converted or cancelled PO")
        
        update_data = {k: v for k, v in po.dict().items() if v is not None}
        
        # Recalculate totals if items changed
        if "items" in update_data:
            items_data = [item.dict() if hasattr(item, 'dict') else item for item in update_data["items"]]
            totals = calculate_po_totals(items_data)
            update_data.update(totals)
            update_data["items"] = items_data
        
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await db.customer_pos.update_one(
            {"id": po_id},
            {"$set": update_data}
        )
        
        updated = await db.customer_pos.find_one({"id": po_id}, {"_id": 0})
        
        return {
            "status": "success",
            "message": "Customer PO updated successfully",
            "customer_po": updated
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update Customer PO: {str(e)}")


@router.post("/{po_id}/convert")
async def convert_customer_po(
    po_id: str,
    convert_to: str,  # "sales_order" or "invoice"
    db = Depends(get_db)
):
    """
    Mark Customer PO as converted to SO or Invoice.
    The actual SO/Invoice creation happens in offline_invoice_routes.py
    This just updates the status and links.
    """
    try:
        po = await db.customer_pos.find_one({"id": po_id})
        if not po:
            raise HTTPException(status_code=404, detail="Customer PO not found")
        
        if po.get("status") != "pending":
            raise HTTPException(status_code=400, detail="Customer PO is already converted or cancelled")
        
        if convert_to not in ["sales_order", "invoice"]:
            raise HTTPException(status_code=400, detail="convert_to must be 'sales_order' or 'invoice'")
        
        status = "converted_to_so" if convert_to == "sales_order" else "converted_to_invoice"
        
        await db.customer_pos.update_one(
            {"id": po_id},
            {"$set": {
                "status": status,
                "converted_to": convert_to,
                "converted_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "status": "success",
            "message": f"Customer PO marked as converted to {convert_to}",
            "customer_po": po["customer_po_number"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert Customer PO: {str(e)}")


@router.post("/{po_id}/cancel")
async def cancel_customer_po(po_id: str, reason: Optional[str] = None, db = Depends(get_db)):
    """Cancel a Customer PO"""
    try:
        po = await db.customer_pos.find_one({"id": po_id})
        if not po:
            raise HTTPException(status_code=404, detail="Customer PO not found")
        
        if po.get("status") != "pending":
            raise HTTPException(status_code=400, detail="Only pending Customer POs can be cancelled")
        
        await db.customer_pos.update_one(
            {"id": po_id},
            {"$set": {
                "status": "cancelled",
                "cancellation_reason": reason,
                "cancelled_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "status": "success",
            "message": "Customer PO cancelled successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel Customer PO: {str(e)}")


@router.get("/quotations/available")
async def get_quotations_for_po_linking(
    store_code: Optional[str] = None,
    search: Optional[str] = None,
    db = Depends(get_db)
):
    """Get quotations that can be linked to a Customer PO"""
    try:
        query = {
            "status": {"$in": ["sent", "draft", "viewed"]}  # Exclude expired/rejected
        }
        
        if store_code:
            query["store_id"] = store_code
        
        if search:
            query["$or"] = [
                {"quotation_number": {"$regex": search, "$options": "i"}},
                {"customer_name": {"$regex": search, "$options": "i"}},
                {"customer_phone": {"$regex": search, "$options": "i"}}
            ]
        
        quotations = await db.quotations.find(
            query,
            {"_id": 0, "id": 1, "quotation_number": 1, "customer_name": 1, 
             "customer_phone": 1, "grand_total": 1, "created_at": 1, "status": 1}
        ).sort("created_at", -1).limit(50).to_list(None)
        
        return {
            "status": "success",
            "quotations": quotations,
            "total": len(quotations)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch quotations: {str(e)}")
