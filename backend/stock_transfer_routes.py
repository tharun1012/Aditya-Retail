"""
Stock Transfer and PO Request Routes
Handles inter-store stock transfers and smart PO generation for stores
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from database import get_db
from pydantic import BaseModel
import uuid
import logging
import os

# Import notification helpers
from notifications_routes import (
    notify_stock_transfer_created,
    notify_stock_transfer_approved,
    notify_stock_transfer_dispatched,
    notify_stock_transfer_received,
    notify_po_request_created,
    notify_po_approved
)

router = APIRouter(prefix="/stock-transfer", tags=["Stock Transfer & PO Requests"])
logger = logging.getLogger(__name__)

# ============ MODELS ============

class StockTransferItem(BaseModel):
    product_id: str
    product_name: str
    sku: Optional[str] = None
    quantity: int
    unit_price: Optional[float] = 0

class StockTransferRequest(BaseModel):
    from_store_id: str
    to_store_id: str
    items: List[StockTransferItem]
    notes: Optional[str] = None
    urgency: str = "normal"  # normal, urgent, critical

class PORequestItem(BaseModel):
    model_number: str  # Product SKU/Model number
    product_name: Optional[str] = None
    quantity: int
    notes: Optional[str] = None
    hsn_code: Optional[str] = None
    rate: Optional[float] = 0  # Per-unit rate, inclusive of GST
    tax_rate: Optional[float] = 18
    discount_percent: Optional[float] = 0

class PORequest(BaseModel):
    store_id: str
    items: List[PORequestItem]
    urgency: str = "normal"
    notes: Optional[str] = None

class ApprovalAction(BaseModel):
    action: str  # approve, reject
    comments: Optional[str] = None
    delivery_location: Optional[str] = None
    approved_by: Optional[str] = None
    rejection_reason: Optional[str] = None

# ============ STOCK TRANSFER ENDPOINTS ============

@router.post("/request")
async def create_transfer_request(
    request: StockTransferRequest,
    db = Depends(get_db)
):
    """Create a stock transfer request from one store to another"""
    try:
        # Verify stores exist
        from_store = await db.stores.find_one({"id": request.from_store_id})
        to_store = await db.stores.find_one({"id": request.to_store_id})
        
        if not from_store:
            raise HTTPException(status_code=404, detail="Source store not found")
        if not to_store:
            raise HTTPException(status_code=404, detail="Destination store not found")
        
        # Generate transfer number
        count = await db.stock_transfers.count_documents({})
        transfer_number = f"TRF-{datetime.now().strftime('%Y%m')}-{count + 1:04d}"
        
        transfer_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        # Calculate total value
        total_value = sum(item.quantity * (item.unit_price or 0) for item in request.items)
        
        transfer_data = {
            "id": transfer_id,
            "transfer_number": transfer_number,
            "from_store_id": request.from_store_id,
            "from_store_name": from_store["name"],
            "from_store_code": from_store["code"],
            "to_store_id": request.to_store_id,
            "to_store_name": to_store["name"],
            "to_store_code": to_store["code"],
            "items": [item.dict() for item in request.items],
            "total_items": len(request.items),
            "total_quantity": sum(item.quantity for item in request.items),
            "total_value": total_value,
            "notes": request.notes,
            "urgency": request.urgency,
            "status": "pending",  # pending, approved, rejected, in_transit, completed, cancelled
            "requested_by": None,  # Will be set when auth is integrated
            "approved_by": None,
            "approval_date": None,
            "approval_comments": None,
            "dispatch_date": None,
            "received_date": None,
            "created_at": now,
            "updated_at": now
        }
        
        await db.stock_transfers.insert_one(transfer_data)
        
        # Send notifications to warehouse and admin
        try:
            await notify_stock_transfer_created(db, transfer_data)
        except Exception as notify_err:
            logger.warning(f"Failed to send transfer notification: {notify_err}")
        
        return {
            "status": "success",
            "message": f"Transfer request {transfer_number} created successfully",
            "transfer_id": transfer_id,
            "transfer_number": transfer_number
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating transfer request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transfers/all")
async def list_transfers(
    store_id: Optional[str] = None,
    status: Optional[str] = None,
    direction: Optional[str] = None,  # incoming, outgoing, all
    page: int = 1,
    limit: int = 20,
    db = Depends(get_db)
):
    """List stock transfers for a store or all transfers"""
    try:
        query = {}
        
        if store_id:
            if direction == "incoming":
                query["to_store_id"] = store_id
            elif direction == "outgoing":
                query["from_store_id"] = store_id
            else:
                query["$or"] = [{"from_store_id": store_id}, {"to_store_id": store_id}]
        
        if status:
            query["status"] = status
        
        skip = (page - 1) * limit
        
        transfers = await db.stock_transfers.find(
            query, {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.stock_transfers.count_documents(query)
        
        return {
            "status": "success",
            "transfers": transfers,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/po-requests/all")
async def list_po_requests(
    store_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    db = Depends(get_db)
):
    """List PO requests"""
    try:
        query = {}
        if store_id:
            query["store_id"] = store_id
        if status:
            query["status"] = status
        
        skip = (page - 1) * limit
        
        requests = await db.po_requests.find(
            query, {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.po_requests.count_documents(query)
        
        return {
            "status": "success",
            "requests": requests,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transfers/{transfer_id}")
async def get_transfer(transfer_id: str, db = Depends(get_db)):
    """Get transfer details"""
    try:
        transfer = await db.stock_transfers.find_one({"id": transfer_id}, {"_id": 0})
        if not transfer:
            raise HTTPException(status_code=404, detail="Transfer not found")
        
        return {
            "status": "success",
            "transfer": transfer
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transfers/{transfer_id}/approve")
async def approve_transfer(
    transfer_id: str,
    action: ApprovalAction,
    db = Depends(get_db)
):
    """Approve or reject a stock transfer request"""
    try:
        transfer = await db.stock_transfers.find_one({"id": transfer_id})
        if not transfer:
            raise HTTPException(status_code=404, detail="Transfer not found")
        
        if transfer["status"] != "pending":
            raise HTTPException(status_code=400, detail=f"Transfer is already {transfer['status']}")
        
        now = datetime.now(timezone.utc)
        
        if action.action == "approve":
            # Check stock availability in source store
            from_inventory = await db.store_inventory.find_one({"store_id": transfer["from_store_id"]})
            if from_inventory:
                for item in transfer["items"]:
                    available = from_inventory.get("products", {}).get(item["product_id"], 0)
                    if available < item["quantity"]:
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Insufficient stock for {item['product_name']}. Available: {available}, Requested: {item['quantity']}"
                        )
            
            new_status = "approved"
            message = "Transfer approved and ready for dispatch"
        else:
            new_status = "rejected"
            message = "Transfer request rejected"
        
        await db.stock_transfers.update_one(
            {"id": transfer_id},
            {"$set": {
                "status": new_status,
                "approval_date": now,
                "approval_comments": action.comments,
                "updated_at": now
            }}
        )
        
        # Send notifications
        if new_status == "approved":
            try:
                transfer["status"] = new_status  # Update status for notification
                await notify_stock_transfer_approved(db, transfer)
            except Exception as notify_err:
                logger.warning(f"Failed to send approval notification: {notify_err}")
        
        return {
            "status": "success",
            "message": message,
            "new_status": new_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transfers/{transfer_id}/dispatch")
async def dispatch_transfer(transfer_id: str, db = Depends(get_db)):
    """Mark transfer as dispatched/in transit"""
    try:
        transfer = await db.stock_transfers.find_one({"id": transfer_id})
        if not transfer:
            raise HTTPException(status_code=404, detail="Transfer not found")
        
        if transfer["status"] != "approved":
            raise HTTPException(status_code=400, detail="Transfer must be approved before dispatch")
        
        now = datetime.now(timezone.utc)
        
        # Deduct stock from source store
        from_inventory = await db.store_inventory.find_one({"store_id": transfer["from_store_id"]})
        if from_inventory:
            products = from_inventory.get("products", {})
            for item in transfer["items"]:
                if item["product_id"] in products:
                    products[item["product_id"]] = max(0, products[item["product_id"]] - item["quantity"])
            
            await db.store_inventory.update_one(
                {"store_id": transfer["from_store_id"]},
                {"$set": {"products": products, "last_updated": now}}
            )
        
        await db.stock_transfers.update_one(
            {"id": transfer_id},
            {"$set": {
                "status": "in_transit",
                "dispatch_date": now,
                "updated_at": now
            }}
        )
        
        # Notify destination store
        try:
            transfer["status"] = "in_transit"
            await notify_stock_transfer_dispatched(db, transfer)
        except Exception as notify_err:
            logger.warning(f"Failed to send dispatch notification: {notify_err}")
        
        return {
            "status": "success",
            "message": "Transfer dispatched successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transfers/{transfer_id}/receive")
async def receive_transfer(transfer_id: str, db = Depends(get_db)):
    """Mark transfer as received and update destination inventory"""
    try:
        transfer = await db.stock_transfers.find_one({"id": transfer_id})
        if not transfer:
            raise HTTPException(status_code=404, detail="Transfer not found")
        
        if transfer["status"] != "in_transit":
            raise HTTPException(status_code=400, detail="Transfer must be in transit to receive")
        
        now = datetime.now(timezone.utc)
        
        # Add stock to destination store
        to_inventory = await db.store_inventory.find_one({"store_id": transfer["to_store_id"]})
        if to_inventory:
            products = to_inventory.get("products", {})
            for item in transfer["items"]:
                if item["product_id"] in products:
                    products[item["product_id"]] += item["quantity"]
                else:
                    products[item["product_id"]] = item["quantity"]
            
            await db.store_inventory.update_one(
                {"store_id": transfer["to_store_id"]},
                {"$set": {"products": products, "last_updated": now}}
            )
        else:
            # Create inventory record
            products = {item["product_id"]: item["quantity"] for item in transfer["items"]}
            await db.store_inventory.insert_one({
                "store_id": transfer["to_store_id"],
                "store_code": transfer["to_store_code"],
                "products": products,
                "last_updated": now
            })
        
        await db.stock_transfers.update_one(
            {"id": transfer_id},
            {"$set": {
                "status": "completed",
                "received_date": now,
                "updated_at": now
            }}
        )
        
        # Notify source store that transfer is complete
        try:
            transfer["status"] = "completed"
            await notify_stock_transfer_received(db, transfer)
        except Exception as notify_err:
            logger.warning(f"Failed to send receive notification: {notify_err}")
        
        return {
            "status": "success",
            "message": "Transfer received and inventory updated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ SMART PO REQUEST ENDPOINTS ============

@router.post("/po-request")
async def create_po_request(
    request: PORequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Create a PO request from a store - AI will generate the PO"""
    try:
        # Verify store exists
        store = await db.stores.find_one({"id": request.store_id})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Generate PO request number
        count = await db.po_requests.count_documents({})
        po_request_number = f"POR-{datetime.now().strftime('%Y%m')}-{count + 1:04d}"
        
        request_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        # Lookup product details from model numbers
        enriched_items = []
        total_estimated_value = 0
        
        for item in request.items:
            # Find product by SKU/model number
            product = await db.products.find_one({
                "$or": [
                    {"sku": {"$regex": item.model_number, "$options": "i"}},
                    {"model_number": {"$regex": item.model_number, "$options": "i"}},
                    {"name": {"$regex": item.model_number, "$options": "i"}}
                ]
            })
            
            enriched_item = {
                "model_number": item.model_number,
                "quantity": item.quantity,
                "notes": item.notes,
                "product_found": product is not None
            }
            
            if product:
                enriched_item.update({
                    "product_id": str(product.get("_id", product.get("id", ""))),
                    "product_name": product.get("name", item.product_name or item.model_number),
                    "sku": product.get("sku"),
                    "brand": product.get("brand"),
                    "category": product.get("category"),
                    "cost_price": product.get("cost_price", product.get("price", 0)),
                    "mrp": product.get("price", 0)
                })
            else:
                enriched_item.update({
                    "product_name": item.product_name or item.model_number,
                    "cost_price": 0,
                    "mrp": 0
                })

            # Tax calculation (rate is inclusive of GST, mirrors offline invoice logic)
            rate = item.rate or 0
            qty = item.quantity
            tax_rate = item.tax_rate if item.tax_rate is not None else 18
            discount_pct = item.discount_percent or 0

            gross = rate * qty
            discount_amt = gross * (discount_pct / 100)
            net = gross - discount_amt
            taxable_amount = net / (1 + tax_rate / 100) if tax_rate else net
            total_tax = net - taxable_amount
            cgst_amount = total_tax / 2
            sgst_amount = total_tax / 2
            line_total = net

            enriched_item.update({
                "hsn_code": item.hsn_code,
                "rate": rate,
                "tax_rate": tax_rate,
                "discount_percent": discount_pct,
                "taxable_amount": round(taxable_amount, 2),
                "cgst_amount": round(cgst_amount, 2),
                "sgst_amount": round(sgst_amount, 2),
                "total_tax": round(total_tax, 2),
                "line_total": round(line_total, 2)
            })

            total_estimated_value += line_total

            enriched_items.append(enriched_item)
        
        po_request_data = {
            "id": request_id,
            "request_number": po_request_number,
            "store_id": request.store_id,
            "store_name": store["name"],
            "store_code": store["code"],
            "items": enriched_items,
            "total_items": len(enriched_items),
            "total_quantity": sum(item.quantity for item in request.items),
            "estimated_value": total_estimated_value,
            "total_amount": total_estimated_value,
            "urgency": request.urgency,
            "notes": request.notes,
            "status": "pending_review",  # pending_review, po_generated, approved, rejected, ordered
            "generated_po_id": None,
            "generated_po_number": None,
            "ai_suggestions": None,
            "reviewed_by": None,
            "review_date": None,
            "review_comments": None,
            "created_at": now,
            "updated_at": now
        }
        
        await db.po_requests.insert_one(po_request_data)
        
        # Send notifications to admin and accounts
        try:
            await notify_po_request_created(db, po_request_data)
        except Exception as notify_err:
            logger.warning(f"Failed to send PO request notification: {notify_err}")
        
        # Generate AI/vendor suggestions in background (no PO is created here)
        background_tasks.add_task(generate_po_suggestions, request_id, db)
        
        return {
            "status": "success",
            "message": f"PO Request {po_request_number} submitted successfully. AI is generating the purchase order.",
            "request_id": request_id,
            "request_number": po_request_number,
            "items_found": sum(1 for item in enriched_items if item["product_found"]),
            "items_not_found": sum(1 for item in enriched_items if not item["product_found"]),
            "estimated_value": total_estimated_value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating PO request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def generate_po_suggestions(request_id: str, db):
    """Background task: attach AI + vendor suggestions to a PO request.
    Does NOT create a Purchase Order and does NOT change status away from
    pending_review - that only happens when admin explicitly approves."""
    try:
        po_request = await db.po_requests.find_one({"id": request_id})
        if not po_request:
            return

        categories = set()
        brands = set()

        for item in po_request["items"]:
            if item.get("category"):
                categories.add(item["category"])
            if item.get("brand"):
                brands.add(item["brand"])

        vendor_query = {}
        if brands:
            vendor_query["brands"] = {"$in": list(brands)}

        suggested_vendors = await db.vendors.find(vendor_query, {"_id": 0}).limit(3).to_list(3)
        primary_vendor = suggested_vendors[0] if suggested_vendors else None

        ai_suggestions = None
        try:
            api_key = os.environ.get("EMERGENT_LLM_KEY")
            if api_key:
                from emergentintegrations.llm.gemini import GeminiConfig, gemini_text_request

                config = GeminiConfig(
                    api_key=api_key,
                    model="gemini-2.5-flash"
                )

                items_text = "\n".join([
                    f"- {item['product_name']} (Model: {item['model_number']}, Qty: {item['quantity']})"
                    for item in po_request["items"]
                ])

                prompt = f"""As a procurement AI assistant, analyze this purchase request from store {po_request['store_name']}:

Items Requested:
{items_text}

Provide brief suggestions for:
1. Recommended vendor(s) for these products (Bosch, Siemens, or Hindware distributors)
2. Any bulk discount opportunities
3. Alternative products if any item seems discontinued
4. Urgency assessment

Keep response under 200 words, focus on actionable insights."""

                ai_response = await gemini_text_request(config, prompt, max_tokens=300)
                ai_suggestions = ai_response.strip()
        except Exception as ai_error:
            logger.warning(f"AI suggestion failed: {ai_error}")
            ai_suggestions = "AI suggestions unavailable. Manual review recommended."

        now = datetime.now(timezone.utc)
        update_data = {
            "ai_suggestions": ai_suggestions,
            "updated_at": now
        }
        if primary_vendor:
            update_data["suggested_vendor_id"] = primary_vendor.get("id")
            update_data["suggested_vendor_name"] = primary_vendor.get("name")

        await db.po_requests.update_one(
            {"id": request_id},
            {"$set": update_data}
        )

        logger.info(f"Attached AI suggestions to PO request {po_request.get('request_number')}")

    except Exception as e:
        logger.error(f"Error generating PO suggestions: {e}")


@router.get("/po-requests/{request_id}")
async def get_po_request(request_id: str, db = Depends(get_db)):
    """Get PO request details"""
    try:
        request = await db.po_requests.find_one({"id": request_id}, {"_id": 0})
        if not request:
            raise HTTPException(status_code=404, detail="PO request not found")
        
        # Get generated PO if exists
        generated_po = None
        if request.get("generated_po_id"):
            generated_po = await db.purchase_orders.find_one(
                {"id": request["generated_po_id"]},
                {"_id": 0}
            )
        
        return {
            "status": "success",
            "request": request,
            "generated_po": generated_po
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class POItemEdit(BaseModel):
    model_number: Optional[str] = None
    product_name: Optional[str] = None
    sku: Optional[str] = None
    product_id: Optional[str] = None
    quantity: int
    cost_price: Optional[float] = 0
    notes: Optional[str] = None


class POEditRequest(BaseModel):
    items: Optional[List[POItemEdit]] = None
    supplier_name: Optional[str] = None
    urgency: Optional[str] = None
    notes: Optional[str] = None


@router.put("/po-requests/{request_id}")
async def edit_po_request(request_id: str, edit: POEditRequest, db = Depends(get_db)):
    """Admin edits a PO request (items/pricing/vendor) before approving it.
    Only allowed while the request is still pending review."""
    try:
        po_request = await db.po_requests.find_one({"id": request_id})
        if not po_request:
            raise HTTPException(status_code=404, detail="PO request not found")

        if po_request["status"] not in ["pending", "pending_review"]:
            raise HTTPException(status_code=400, detail=f"Cannot edit request in {po_request['status']} status")

        now = datetime.now(timezone.utc)
        update_data = {"updated_at": now}

        if edit.items is not None:
            new_items = [item.dict() for item in edit.items]
            update_data["items"] = new_items
            update_data["total_items"] = len(new_items)
            update_data["total_quantity"] = sum(i.get("quantity", 0) or 0 for i in new_items)
            new_total = sum(
                (i.get("quantity", 0) or 0) * (i.get("cost_price", 0) or 0) for i in new_items
            )
            update_data["estimated_value"] = new_total
            update_data["total_amount"] = new_total

        if edit.supplier_name is not None:
            update_data["supplier_name"] = edit.supplier_name
        if edit.urgency is not None:
            update_data["urgency"] = edit.urgency
        if edit.notes is not None:
            update_data["notes"] = edit.notes

        await db.po_requests.update_one({"id": request_id}, {"$set": update_data})

        return {"status": "success", "message": "PO request updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/po-requests/{request_id}/approve")
async def approve_po_request(
    request_id: str,
    action: ApprovalAction,
    db = Depends(get_db)
):
    """Approve or reject PO request. Approving is what creates the real PO."""
    try:
        po_request = await db.po_requests.find_one({"id": request_id})
        if not po_request:
            raise HTTPException(status_code=404, detail="PO request not found")
        
        if po_request["status"] not in ["pending", "pending_review", "po_generated"]:
            raise HTTPException(status_code=400, detail=f"Cannot approve request in {po_request['status']} status")
        
        now = datetime.now(timezone.utc)
        
        if action.action == "approve":
            new_status = "approved"
            message = "PO request approved and Purchase Order created."
            
            update_data = {
                "status": new_status,
                "approved_by": action.approved_by,
                "approved_at": now,
                "review_date": now,
                "review_comments": action.comments,
                "updated_at": now
            }
            
            if action.delivery_location:
                update_data["delivery_location"] = action.delivery_location
            
            if po_request.get("generated_po_id"):
                await db.purchase_orders.update_one(
                    {"id": po_request["generated_po_id"]},
                    {"$set": {
                        "status": "approved", 
                        "delivery_location": action.delivery_location,
                        "approved_by": action.approved_by,
                        "approved_at": now,
                        "updated_at": now
                    }}
                )
            else:
                po_count = await db.purchase_orders.count_documents({})
                po_number = f"PO-{datetime.now().strftime('%Y%m')}-{po_count + 1:04d}"
                po_id = str(uuid.uuid4())

                items = po_request.get("items", [])

                item_docs = []
                subtotal = 0.0
                tax_total = 0.0
                for item in items:
                    qty = item.get("quantity", 0) or 0
                    rate = item.get("rate")
                    if rate is None:
                        rate = item.get("cost_price", item.get("unit_price", 0)) or 0
                    tax_rate = item.get("tax_rate")
                    if tax_rate is None:
                        tax_rate = 18
                    discount_pct = item.get("discount_percent", 0) or 0

                    if item.get("taxable_amount") is not None:
                        taxable_amount = item.get("taxable_amount") or 0
                        item_total_tax = item.get("total_tax", 0) or 0
                        cgst_amount = item.get("cgst_amount", 0) or 0
                        sgst_amount = item.get("sgst_amount", 0) or 0
                        line_total = item.get("line_total", taxable_amount + item_total_tax)
                    else:
                        gross = rate * qty
                        discount_amt = gross * (discount_pct / 100)
                        net = gross - discount_amt
                        taxable_amount = net / (1 + tax_rate / 100) if tax_rate else net
                        item_total_tax = net - taxable_amount
                        cgst_amount = item_total_tax / 2
                        sgst_amount = item_total_tax / 2
                        line_total = net

                    subtotal += taxable_amount
                    tax_total += item_total_tax

                    item_docs.append({
                        "product_id": item.get("product_id", ""),
                        "product_name": item.get("product_name"),
                        "model_number": item.get("model_number"),
                        "sku": item.get("sku"),
                        "hsn_code": item.get("hsn_code"),
                        "quantity": qty,
                        "rate": rate,
                        "unit_price": rate,
                        "tax_rate": tax_rate,
                        "discount_percent": discount_pct,
                        "taxable_amount": round(taxable_amount, 2),
                        "cgst_amount": round(cgst_amount, 2),
                        "sgst_amount": round(sgst_amount, 2),
                        "total_tax": round(item_total_tax, 2),
                        "total": round(line_total, 2)
                    })

                po_data = {
                    "id": po_id,
                    "po_number": po_number,
                    "vendor_id": po_request.get("suggested_vendor_id"),
                    "vendor_name": po_request.get("supplier_name") or po_request.get("suggested_vendor_name") or "To Be Assigned",
                    "store_id": po_request["store_id"],
                    "store_name": po_request["store_name"],
                    "po_request_id": request_id,
                    "items": item_docs,
                    "subtotal": round(subtotal, 2),
                    "tax_amount": round(tax_total, 2),
                    "total_amount": round(subtotal + tax_total, 2),
                    "status": "approved",
                    "urgency": po_request.get("urgency"),
                    "notes": po_request.get("notes"),
                    "ai_generated": False,
                    "ai_suggestions": po_request.get("ai_suggestions"),
                    "delivery_location": action.delivery_location,
                    "approved_by": action.approved_by,
                    "approved_at": now,
                    "created_at": now,
                    "updated_at": now
                }

                await db.purchase_orders.insert_one(po_data)

                update_data["generated_po_id"] = po_id
                update_data["generated_po_number"] = po_number
            
            # Create a notification for the requesting store
            notification = {
                "id": str(uuid.uuid4()),
                "type": "po_approved",
                "title": "PO Request Approved",
                "message": f"Your purchase order request {po_request.get('request_number', request_id[:8])} has been approved.",
                "store_id": po_request.get("store_id"),
                "reference_id": request_id,
                "is_read": False,
                "created_at": now.isoformat()
            }
            await db.notifications.insert_one(notification)
            
            # Also notify via po_approved function if available
            try:
                await notify_po_approved(db, po_request)
            except Exception as notify_error:
                print(f"Notification error (non-critical): {notify_error}")
                
        else:
            new_status = "rejected"
            message = "PO request rejected"
            
            update_data = {
                "status": new_status,
                "rejected_by": action.approved_by,
                "rejection_reason": action.rejection_reason,
                "review_date": now,
                "review_comments": action.comments or action.rejection_reason,
                "updated_at": now
            }
            
            # Create rejection notification
            notification = {
                "id": str(uuid.uuid4()),
                "type": "po_rejected",
                "title": "PO Request Rejected",
                "message": f"Your purchase order request {po_request.get('request_number', request_id[:8])} has been rejected. Reason: {action.rejection_reason or 'Not specified'}",
                "store_id": po_request.get("store_id"),
                "reference_id": request_id,
                "is_read": False,
                "created_at": now.isoformat()
            }
            await db.notifications.insert_one(notification)
        
        await db.po_requests.update_one(
            {"id": request_id},
            {"$set": update_data}
        )
        
        return {
            "status": "success",
            "message": message,
            "new_status": new_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ DASHBOARD STATS ============

@router.get("/stats/{store_id}")
async def get_store_transfer_stats(store_id: str, db = Depends(get_db)):
    """Get transfer and PO request statistics for a store"""
    try:
        # Transfer stats
        pending_incoming = await db.stock_transfers.count_documents({
            "to_store_id": store_id,
            "status": {"$in": ["pending", "approved", "in_transit"]}
        })
        
        pending_outgoing = await db.stock_transfers.count_documents({
            "from_store_id": store_id,
            "status": {"$in": ["pending", "approved", "in_transit"]}
        })
        
        # PO request stats
        pending_po_requests = await db.po_requests.count_documents({
            "store_id": store_id,
            "status": {"$in": ["pending_review", "po_generated"]}
        })
        
        approved_pos = await db.po_requests.count_documents({
            "store_id": store_id,
            "status": "approved"
        })
        
        return {
            "status": "success",
            "stats": {
                "pending_incoming_transfers": pending_incoming,
                "pending_outgoing_transfers": pending_outgoing,
                "pending_po_requests": pending_po_requests,
                "approved_pos": approved_pos
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
