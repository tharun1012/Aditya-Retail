"""
Goods Receipt Note (GRN) Routes
Handles recording of goods received from suppliers with PO matching and Serial Number tracking
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timezone
from database import get_db
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/grn", tags=["Goods Receipt Notes"])


class SerialNumberEntry(BaseModel):
    """Serial number entry for a product"""
    serial_number: str
    condition: str = "new"  # new, refurbished, damaged
    warranty_start_date: Optional[str] = None
    warranty_end_date: Optional[str] = None
    warranty_months: Optional[int] = 12
    notes: Optional[str] = None


class GRNItem(BaseModel):
    product_id: str
    product_name: str
    model_number: Optional[str] = None
    ordered_quantity: int
    received_quantity: int
    unit_price: float
    hsn_code: Optional[str] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[str] = None
    serial_numbers: Optional[List[SerialNumberEntry]] = []  # NEW: Serial numbers list
    has_serial_tracking: bool = False  # Whether this product requires serial tracking
    notes: Optional[str] = None


class CreateGRNRequest(BaseModel):
    po_number: Optional[str] = None  # Optional - can receive without PO
    po_id: Optional[str] = None
    vendor_id: Optional[str] = None
    vendor_name: str
    vendor_invoice_number: Optional[str] = None
    vendor_invoice_date: Optional[str] = None
    vendor_gstin: Optional[str] = None
    items: List[GRNItem]
    warehouse_id: str
    store_code: Optional[str] = None  # If receiving at a specific store
    received_by: str
    notes: Optional[str] = None


@router.post("/create")
async def create_grn(request: CreateGRNRequest, db = Depends(get_db)):
    """
    Create a Goods Receipt Note for items received from supplier.
    Supports serial number entry for tracking individual units.
    """
    try:
        # Generate GRN number
        today = datetime.now()
        grn_count = await db.grn.count_documents({})
        grn_number = f"GRN-{today.strftime('%Y%m%d')}-{grn_count + 1:04d}"
        
        # Calculate totals
        total_ordered = sum(item.ordered_quantity for item in request.items)
        total_received = sum(item.received_quantity for item in request.items)
        total_value = sum(item.received_quantity * item.unit_price for item in request.items)
        
        # Check discrepancies
        discrepancies = []
        serial_number_warnings = []
        
        for item in request.items:
            # Check quantity discrepancy
            if item.received_quantity != item.ordered_quantity:
                discrepancies.append({
                    "product_name": item.product_name,
                    "ordered": item.ordered_quantity,
                    "received": item.received_quantity,
                    "difference": item.received_quantity - item.ordered_quantity
                })
            
            # Validate serial numbers if tracking is enabled
            if item.has_serial_tracking and item.serial_numbers:
                if len(item.serial_numbers) != item.received_quantity:
                    serial_number_warnings.append({
                        "product_name": item.product_name,
                        "received_qty": item.received_quantity,
                        "serial_count": len(item.serial_numbers),
                        "warning": f"Serial count mismatch: {len(item.serial_numbers)} serials for {item.received_quantity} units"
                    })
        
        # Process items with serial numbers
        items_data = []
        for item in request.items:
            item_dict = item.dict()
            
            # Process serial numbers if provided
            if item.serial_numbers:
                serial_data = []
                for sn in item.serial_numbers:
                    serial_data.append({
                        "serial_number": sn.serial_number,
                        "condition": sn.condition,
                        "warranty_start_date": sn.warranty_start_date or today.strftime("%Y-%m-%d"),
                        "warranty_end_date": sn.warranty_end_date,
                        "warranty_months": sn.warranty_months,
                        "notes": sn.notes
                    })
                item_dict["serial_numbers"] = serial_data
            
            items_data.append(item_dict)
        
        grn_data = {
            "id": str(uuid.uuid4()),
            "grn_number": grn_number,
            "po_number": request.po_number,
            "po_id": request.po_id,
            "vendor_id": request.vendor_id,
            "vendor_name": request.vendor_name,
            "vendor_invoice_number": request.vendor_invoice_number,
            "vendor_invoice_date": request.vendor_invoice_date,
            "vendor_gstin": request.vendor_gstin,
            "items": items_data,
            "total_items": len(request.items),
            "total_ordered_quantity": total_ordered,
            "total_received_quantity": total_received,
            "total_value": round(total_value, 2),
            "has_discrepancies": len(discrepancies) > 0,
            "discrepancies": discrepancies,
            "serial_number_warnings": serial_number_warnings,
            "warehouse_id": request.warehouse_id,
            "store_code": request.store_code,
            "received_by": request.received_by,
            "notes": request.notes,
            "status": "completed",  # draft, completed, verified
            "verified_by": None,
            "verified_at": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.grn.insert_one(grn_data)

        try:
            from realtime_accounting import post_transaction_event
            await post_transaction_event(db, "grn", {
                "id": grn_data["grn_number"],
                "amount": grn_data["total_value"],
                "tax": 0,
                "payment_method": "n/a",
                "payment_status": grn_data.get("status", "completed"),
                "date": grn_data["created_at"],
                "vendor": grn_data.get("vendor_name", "Unknown"),
                "items": grn_data.get("items", [])
            })
        except Exception as e:
            print(f"⚠️ Real-time accounting failed for {grn_data['grn_number']}: {e}")

        # Update inventory for received items
        for item in request.items:
            if item.received_quantity > 0:
                # Update product stock
                await db.products.update_one(
                    {"id": item.product_id},
                    {
                        "$inc": {"current_stock": item.received_quantity},
                        "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                    }
                )
                
                # Update store-level inventory if store_code is provided
                if request.store_code:
                    # Update the inventory collection (for transactions tracking)
                    await db.inventory.update_one(
                        {"product_id": item.product_id, "store_code": request.store_code},
                        {
                            "$inc": {"quantity": item.received_quantity},
                            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                        },
                        upsert=True
                    )
                    
                    # ALSO update store_inventory (for stock list display)
                    # First, get the store_id from store_code
                    store = await db.stores.find_one({"code": request.store_code})
                    if store:
                        store_id = store.get("id")
                        # Update or create store_inventory document
                        await db.store_inventory.update_one(
                            {"store_id": store_id},
                            {
                                "$inc": {f"products.{item.product_id}": item.received_quantity},
                                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                            },
                            upsert=True
                        )
                
                # Create inventory transaction
                transaction = {
                    "id": str(uuid.uuid4()),
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "transaction_type": "grn_receipt",
                    "quantity_change": item.received_quantity,
                    "reference_id": grn_data["id"],
                    "reference_number": grn_number,
                    "reason": f"GRN: {grn_number} from {request.vendor_name}",
                    "store_code": request.store_code,
                    "created_by": request.received_by,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                await db.inventory_transactions.insert_one(transaction)
                
                # Create serial number inventory entries if serial tracking is enabled
                if item.has_serial_tracking and item.serial_numbers:
                    for sn in item.serial_numbers:
                        serial_inventory = {
                            "id": str(uuid.uuid4()),
                            "serial_number": sn.serial_number,
                            "product_id": item.product_id,
                            "product_name": item.product_name,
                            "model_number": item.model_number,
                            "grn_id": grn_data["id"],
                            "grn_number": grn_number,
                            "vendor_name": request.vendor_name,
                            "purchase_date": today.strftime("%Y-%m-%d"),
                            "purchase_price": item.unit_price,
                            "condition": sn.condition,
                            "warranty_start_date": sn.warranty_start_date or today.strftime("%Y-%m-%d"),
                            "warranty_end_date": sn.warranty_end_date,
                            "warranty_months": sn.warranty_months,
                            "store_code": request.store_code,
                            "warehouse_id": request.warehouse_id,
                            "status": "in_stock",  # in_stock, sold, returned, damaged, warranty_claim
                            "sold_invoice_id": None,
                            "sold_invoice_number": None,
                            "sold_date": None,
                            "customer_id": None,
                            "customer_name": None,
                            "notes": sn.notes,
                            "created_at": datetime.now(timezone.utc).isoformat(),
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                        await db.serial_inventory.insert_one(serial_inventory)
        
        # Update PO status if linked
        if request.po_id:
            await db.purchases.update_one(
                {"id": request.po_id},
                {
                    "$set": {
                        "status": "partial" if len(discrepancies) > 0 else "completed",
                        "grn_id": grn_data["id"],
                        "grn_number": grn_number,
                        "received_at": datetime.now(timezone.utc).isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
        
        # ========== AUTO-MATCH WITH PURCHASE BILL ==========
        # Try to find a matching Purchase Bill by vendor invoice number
        matched_bill = None
        if request.vendor_invoice_number:
            matched_bill = await db.purchase_bills.find_one({
                "bill_number": request.vendor_invoice_number,
                "linked_grn_id": {"$exists": False}  # Not already matched
            })
            
            if matched_bill:
                # Link both documents
                await db.purchase_bills.update_one(
                    {"id": matched_bill["id"]},
                    {
                        "$set": {
                            "linked_grn_id": grn_data["id"],
                            "linked_grn_number": grn_number,
                            "grn_matched_at": datetime.now(timezone.utc).isoformat(),
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                
                await db.grn.update_one(
                    {"id": grn_data["id"]},
                    {
                        "$set": {
                            "linked_bill_id": matched_bill["id"],
                            "linked_bill_number": matched_bill["bill_number"],
                            "bill_matched_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
        
        return {
            "status": "success",
            "message": f"GRN {grn_number} created successfully",
            "grn_id": grn_data["id"],
            "grn_number": grn_number,
            "total_received": total_received,
            "total_value": round(total_value, 2),
            "has_discrepancies": len(discrepancies) > 0,
            "discrepancies": discrepancies,
            "serial_number_warnings": serial_number_warnings,
            "auto_matched": matched_bill is not None,
            "matched_bill_number": matched_bill["bill_number"] if matched_bill else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_grns(
    warehouse_id: Optional[str] = None,
    vendor_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    db = Depends(get_db)
):
    """List all GRNs with filters"""
    try:
        query = {}
        if warehouse_id:
            query["warehouse_id"] = warehouse_id
        if vendor_id:
            query["vendor_id"] = vendor_id
        if status:
            query["status"] = status
        
        skip = (page - 1) * limit
        
        grns = await db.grn.find(
            query, {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.grn.count_documents(query)
        
        return {
            "status": "success",
            "grns": grns,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending-pos")
async def get_pending_purchase_orders(
    warehouse_id: Optional[str] = None,
    db = Depends(get_db)
):
    """Get Purchase Orders pending receipt - includes approved PO requests"""
    try:
        # First get POs from purchases collection
        query = {
            "status": {"$in": ["approved", "sent_to_vendor", "partial"]}
        }
        
        pos = await db.purchases.find(
            query, {"_id": 0}
        ).sort("created_at", -1).to_list(None)
        
        # Also get approved PO requests
        approved_requests = await db.po_requests.find(
            {"status": "approved"},
            {"_id": 0}
        ).sort("created_at", -1).to_list(None)
        
        # Transform PO requests to match PO format for GRN
        for req in approved_requests:
            po_from_request = {
                "id": req.get("id"),
                "po_number": req.get("request_number", f"POR-{req.get('id', '')[:8]}"),
                "supplier_name": req.get("supplier_name") or req.get("vendor_name") or "TBD",
                "vendor_name": req.get("supplier_name") or req.get("vendor_name") or "TBD",
                "items": req.get("items", []),
                "total_amount": req.get("total_amount", 0),
                "status": "approved",
                "delivery_location": req.get("delivery_location"),
                "store_name": req.get("store_name") or req.get("requesting_store"),
                "created_at": req.get("created_at"),
                "approved_at": req.get("approved_at"),
                "source": "po_request"  # Mark as coming from PO request
            }
            pos.append(po_from_request)
        
        return {
            "status": "success",
            "purchase_orders": pos,
            "total": len(pos)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{grn_id}")
async def get_grn(grn_id: str, db = Depends(get_db)):
    """Get GRN details"""
    try:
        grn = await db.grn.find_one({"id": grn_id}, {"_id": 0})
        if not grn:
            raise HTTPException(status_code=404, detail="GRN not found")
        
        return {"status": "success", "grn": grn}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lookup-by-invoice/{invoice_number}")
async def lookup_grn_by_invoice(invoice_number: str, db = Depends(get_db)):
    """Find a GRN matching a given vendor invoice number - used for live lookup while creating a Purchase Bill"""
    try:
        grn = await db.grn.find_one({"vendor_invoice_number": invoice_number}, {"_id": 0})
        if not grn:
            return {"status": "success", "found": False, "grn": None}
        return {"status": "success", "found": True, "grn": grn}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ============================================================================
# SERIAL NUMBER INVENTORY MANAGEMENT
# ============================================================================

@router.get("/serial-inventory/list")
async def list_serial_inventory(
    product_id: Optional[str] = None,
    store_code: Optional[str] = None,
    status: Optional[str] = None,  # in_stock, sold, returned, damaged
    search: Optional[str] = None,  # Search by serial number
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """List serial number inventory with filters"""
    try:
        query = {}
        
        if product_id:
            query["product_id"] = product_id
        if store_code:
            query["store_code"] = store_code
        if status:
            query["status"] = status
        if search:
            query["serial_number"] = {"$regex": search, "$options": "i"}
        
        skip = (page - 1) * limit
        
        serials = await db.serial_inventory.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.serial_inventory.count_documents(query)
        
        # Get counts by status
        status_counts = {}
        for s in ["in_stock", "sold", "returned", "damaged", "warranty_claim"]:
            count_query = dict(query)
            count_query["status"] = s
            status_counts[s] = await db.serial_inventory.count_documents(count_query)
        
        return {
            "status": "success",
            "serials": serials,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
            "status_counts": status_counts
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list serial inventory: {str(e)}")


@router.get("/serial-inventory/warranty-expiring")
async def get_warranty_expiring_serials(
    days: int = 30,  # Serials with warranty expiring in next N days
    db = Depends(get_db)
):
    """Get serial numbers with warranty expiring soon"""
    try:
        from datetime import timedelta
        
        today = datetime.now().date()
        expiry_threshold = (today + timedelta(days=days)).isoformat()
        
        serials = await db.serial_inventory.find(
            {
                "status": "sold",
                "warranty_end_date": {"$lte": expiry_threshold, "$gte": today.isoformat()}
            },
            {"_id": 0}
        ).sort("warranty_end_date", 1).to_list(None)
        
        return {
            "status": "success",
            "threshold_days": days,
            "count": len(serials),
            "serials": serials
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get warranty expiring serials: {str(e)}")


@router.get("/serial-inventory/{serial_number}")
async def get_serial_by_number(serial_number: str, db = Depends(get_db)):
    """Get serial number details and history"""
    try:
        serial = await db.serial_inventory.find_one(
            {"serial_number": serial_number},
            {"_id": 0}
        )
        
        if not serial:
            raise HTTPException(status_code=404, detail=f"Serial number {serial_number} not found")
        
        # Get transaction history for this serial
        history = await db.serial_transactions.find(
            {"serial_number": serial_number},
            {"_id": 0}
        ).sort("created_at", -1).to_list(None)
        
        return {
            "status": "success",
            "serial": serial,
            "history": history
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get serial: {str(e)}")


@router.get("/serial-inventory/product/{product_id}/available")
async def get_available_serials_for_product(
    product_id: str,
    store_code: Optional[str] = None,
    db = Depends(get_db)
):
    """Get available serial numbers for a product (for use in SO/Invoice creation)"""
    try:
        query = {
            "product_id": product_id,
            "status": "in_stock"
        }
        
        if store_code:
            query["store_code"] = store_code
        
        serials = await db.serial_inventory.find(
            query,
            {"_id": 0, "serial_number": 1, "condition": 1, "warranty_months": 1, "warranty_end_date": 1, "purchase_date": 1}
        ).sort("created_at", 1).to_list(None)  # FIFO - oldest first
        
        return {
            "status": "success",
            "product_id": product_id,
            "available_count": len(serials),
            "serials": serials
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available serials: {str(e)}")


class MarkSerialSoldRequest(BaseModel):
    serial_numbers: List[str]
    invoice_id: str
    invoice_number: str
    customer_id: Optional[str] = None
    customer_name: str
    sold_by: str

@router.post("/serial-inventory/mark-sold")
async def mark_serials_as_sold(request: MarkSerialSoldRequest, db = Depends(get_db)):
    """Mark serial numbers as sold (called when creating invoice with serial-tracked items)"""
    try:
        sold_date = datetime.now(timezone.utc).isoformat()
        updated_count = 0
        errors = []
        
        for serial_number in request.serial_numbers:
            # Check if serial exists and is in stock
            serial = await db.serial_inventory.find_one({"serial_number": serial_number})
            
            if not serial:
                errors.append(f"Serial {serial_number} not found")
                continue
            
            if serial.get("status") != "in_stock":
                errors.append(f"Serial {serial_number} is not in stock (status: {serial.get('status')})")
                continue
            
            # Update serial status
            result = await db.serial_inventory.update_one(
                {"serial_number": serial_number, "status": "in_stock"},
                {
                    "$set": {
                        "status": "sold",
                        "sold_invoice_id": request.invoice_id,
                        "sold_invoice_number": request.invoice_number,
                        "sold_date": sold_date,
                        "customer_id": request.customer_id,
                        "customer_name": request.customer_name,
                        "updated_at": sold_date
                    }
                }
            )
            
            if result.modified_count > 0:
                updated_count += 1
                
                # Create transaction record
                transaction = {
                    "id": str(uuid.uuid4()),
                    "serial_number": serial_number,
                    "product_id": serial.get("product_id"),
                    "transaction_type": "sold",
                    "reference_type": "invoice",
                    "reference_id": request.invoice_id,
                    "reference_number": request.invoice_number,
                    "customer_name": request.customer_name,
                    "created_by": request.sold_by,
                    "created_at": sold_date
                }
                await db.serial_transactions.insert_one(transaction)
        
        return {
            "status": "success" if updated_count > 0 else "partial",
            "message": f"Marked {updated_count} serial(s) as sold",
            "updated_count": updated_count,
            "errors": errors if errors else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark serials as sold: {str(e)}")


class ReturnSerialRequest(BaseModel):
    serial_number: str
    return_reason: str
    return_condition: str = "good"  # good, damaged, defective
    returned_by: str
    notes: Optional[str] = None

@router.post("/serial-inventory/return")
async def return_serial(request: ReturnSerialRequest, db = Depends(get_db)):
    """Process a serial number return"""
    try:
        serial = await db.serial_inventory.find_one({"serial_number": request.serial_number})
        
        if not serial:
            raise HTTPException(status_code=404, detail=f"Serial number {request.serial_number} not found")
        
        if serial.get("status") != "sold":
            raise HTTPException(status_code=400, detail=f"Serial {request.serial_number} is not sold (status: {serial.get('status')})")
        
        return_date = datetime.now(timezone.utc).isoformat()
        
        # Determine new status based on condition
        new_status = "in_stock" if request.return_condition == "good" else "damaged"
        
        # Update serial
        result = await db.serial_inventory.update_one(
            {"serial_number": request.serial_number},
            {
                "$set": {
                    "status": new_status,
                    "condition": request.return_condition,
                    "return_date": return_date,
                    "return_reason": request.return_reason,
                    "return_notes": request.notes,
                    "updated_at": return_date
                },
                "$unset": {
                    "sold_invoice_id": "",
                    "sold_invoice_number": "",
                    "sold_date": "",
                    "customer_id": "",
                    "customer_name": ""
                }
            }
        )
        
        if result.modified_count > 0:
            # Create transaction record
            transaction = {
                "id": str(uuid.uuid4()),
                "serial_number": request.serial_number,
                "product_id": serial.get("product_id"),
                "transaction_type": "returned",
                "return_reason": request.return_reason,
                "return_condition": request.return_condition,
                "previous_customer": serial.get("customer_name"),
                "previous_invoice": serial.get("sold_invoice_number"),
                "created_by": request.returned_by,
                "notes": request.notes,
                "created_at": return_date
            }
            await db.serial_transactions.insert_one(transaction)
            
            # Update product stock if returning to inventory
            if new_status == "in_stock":
                await db.products.update_one(
                    {"id": serial.get("product_id")},
                    {"$inc": {"current_stock": 1}}
                )
        
        return {
            "status": "success",
            "message": f"Serial {request.serial_number} returned successfully",
            "new_status": new_status
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process return: {str(e)}")


@router.get("/serial-inventory/check-product/{product_id}")
async def check_product_serial_tracking(product_id: str, store_code: Optional[str] = None, db = Depends(get_db)):
    """
    Check if a product has serial tracking enabled by checking if any serials exist for it.
    Also returns available serial count for the product.
    """
    try:
        query = {"product_id": product_id}
        if store_code:
            query["store_code"] = store_code
        
        # Check if any serials exist for this product
        total_serials = await db.serial_inventory.count_documents(query)
        
        # Count available (in_stock) serials
        query["status"] = "in_stock"
        available_serials = await db.serial_inventory.count_documents(query)
        
        has_serial_tracking = total_serials > 0
        
        return {
            "status": "success",
            "product_id": product_id,
            "has_serial_tracking": has_serial_tracking,
            "total_serials": total_serials,
            "available_serials": available_serials
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check product: {str(e)}")