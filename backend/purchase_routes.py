from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from database import get_db
import uuid

router = APIRouter(prefix="/purchases", tags=["Purchases"])

class VendorDetails(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    gst_number: Optional[str] = None
    address: str
    city: str
    state: str
    pincode: str

class PurchaseItem(BaseModel):
    product_name: str
    hsn_code: str
    quantity: int
    rate: float
    discount: float = 0
    tax_rate: float = 18.0

class PurchaseOrder(BaseModel):
    vendor: VendorDetails
    items: List[PurchaseItem]
    payment_mode: str
    subtotal: float
    discount: float = 0
    shipping_charges: float = 0
    round_off: float = 0
    notes: Optional[str] = None
    created_by: str

@router.post("/create")
async def create_purchase_order(purchase: PurchaseOrder, db = Depends(get_db)):
    """Create new purchase order"""
    try:
        today = datetime.now(timezone.utc)
        po_prefix = f"PO-{today.strftime('%Y%m%d')}"
        
        count = await db.purchases.count_documents({
            "created_at": {
                "$gte": today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            }
        })
        
        po_number = f"{po_prefix}-{count + 1:04d}"
        
        # Calculate totals
        items_total = 0
        tax_total = 0
        items_with_tax = []
        
        for item in purchase.items:
            item_subtotal = item.rate * item.quantity
            item_discount_amount = (item_subtotal * item.discount) / 100
            item_taxable_amount = item_subtotal - item_discount_amount
            item_tax_amount = (item_taxable_amount * item.tax_rate) / 100
            item_total = item_taxable_amount + item_tax_amount
            
            items_total += item_total
            tax_total += item_tax_amount
            
            items_with_tax.append({
                **item.dict(),
                "taxable_amount": round(item_taxable_amount, 2),
                "tax_amount": round(item_tax_amount, 2),
                "total": round(item_total, 2)
            })
        
        discount_amount = (items_total * purchase.discount) / 100 if purchase.discount > 0 else 0
        final_total = items_total - discount_amount + purchase.shipping_charges + purchase.round_off
        
        purchase_data = {
            "id": str(uuid.uuid4()),
            "po_number": po_number,
            "vendor": purchase.vendor.dict(),
            "items": items_with_tax,
            "payment_mode": purchase.payment_mode,
            "subtotal": round(purchase.subtotal, 2),
            "discount_percentage": purchase.discount,
            "discount_amount": round(discount_amount, 2),
            "shipping_charges": round(purchase.shipping_charges, 2),
            "round_off": round(purchase.round_off, 2),
            "tax_total": round(tax_total, 2),
            "total_amount": round(final_total, 2),
            "notes": purchase.notes,
            "created_by": purchase.created_by,
            "status": "pending",
            "payment_status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.purchases.insert_one(purchase_data)

        try:
            from realtime_accounting import post_transaction_event
            await post_transaction_event(db, "purchase", {
                "id": purchase_data["po_number"],
                "amount": purchase_data["total_amount"],
                "tax": purchase_data["tax_total"],
                "payment_method": purchase_data.get("payment_mode", "credit"),
                "payment_status": purchase_data.get("payment_status", "pending"),
                "date": purchase_data["created_at"],
                "vendor": purchase_data.get("vendor", {}).get("name", "Unknown"),
                "items": purchase_data.get("items", [])
            })
        except Exception as e:
            print(f"⚠️ Real-time accounting failed for {purchase_data['po_number']}: {e}")
        
        return {
            "status": "success",
            "po_number": po_number,
            "purchase_id": purchase_data["id"],
            "total_amount": final_total,
            "message": "Purchase order created successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create purchase order: {str(e)}")

@router.get("/")
async def get_purchases(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get all purchase orders with filters"""
    try:
        import math
        
        query = {}
        
        if from_date and to_date:
            query["created_at"] = {"$gte": from_date, "$lte": to_date}
        
        if status:
            query["status"] = status
        
        skip = (page - 1) * limit
        
        purchases = await db.purchases.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        # Clean NaN/Infinity values that break JSON serialization
        def clean_value(val):
            if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                return 0
            return val
        
        def clean_dict(d):
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [clean_dict(item) for item in d]
            else:
                return clean_value(d)
        
        purchases = [clean_dict(p) for p in purchases]
        
        total = await db.purchases.count_documents(query)
        
        return {
            "status": "success",
            "purchases": purchases,
            "total": total,
            "page": page,
            "limit": limit
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch purchases: {str(e)}")

@router.get("/{purchase_id}")
async def get_purchase(purchase_id: str, db = Depends(get_db)):
    """Get specific purchase order"""
    try:
        purchase = await db.purchases.find_one(
            {"$or": [{"id": purchase_id}, {"po_number": purchase_id}]},
            {"_id": 0}
        )
        if not purchase:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        
        return {"status": "success", "purchase": purchase}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch purchase: {str(e)}")

@router.put("/{purchase_id}/status")
async def update_purchase_status(purchase_id: str, status: str, db = Depends(get_db)):
    """Update purchase order status"""
    try:
        # Get purchase order details before updating
        purchase = await db.purchases.find_one({"id": purchase_id}, {"_id": 0})
        
        if not purchase:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        
        # Update status
        result = await db.purchases.update_one(
            {"id": purchase_id},
            {"$set": {
                "status": status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # If status is 'received', update stock for all items (increase inventory)
        if status == "received" and purchase.get("status") != "received":
            from inventory_service import InventoryService
            inventory_service = InventoryService(db)
            
            items = purchase.get("items", [])
            for item in items:
                # Try to match product by name (since PO might not have product_id)
                product = await db.products.find_one(
                    {"name": item.get("product_name")},
                    {"_id": 0, "id": 1}
                )
                
                if product:
                    await inventory_service.update_stock(
                        product_id=product["id"],
                        quantity_change=item["quantity"],  # Positive for purchase
                        transaction_type="purchase",
                        reference_id=purchase_id,
                        reason=f"Purchase receipt: {purchase.get('po_number')}",
                        created_by=purchase.get("created_by", "system")
                    )
        
        return {"status": "success", "message": "Status updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")
