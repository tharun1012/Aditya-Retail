#!/usr/bin/env python3
"""
Fixes the PO Request -> PO flow so that:
1. Store submits a request -> stays 'pending_review' (no auto PO creation)
2. Background task only attaches AI/vendor suggestions (no purchases insert)
3. Admin can PUT-edit the request (items/pricing/vendor) while pending_review
4. Only on POST .../approve is a real Purchase Order actually created in db.purchases
"""
import re
import shutil

TARGET = "backend/stock_transfer_routes.py"

with open(TARGET, "r") as f:
    content = f.read()

shutil.copy(TARGET, TARGET + ".bak")

# EDIT 1: stop the background task from auto-creating a PO
old_1 = '''        # Trigger AI PO generation in background
        background_tasks.add_task(generate_smart_po, request_id, db)'''

new_1 = '''        # Generate AI/vendor suggestions in background (no PO is created here)
        background_tasks.add_task(generate_po_suggestions, request_id, db)'''

assert old_1 in content, "EDIT 1 anchor not found - check trigger line in create_po_request"
content = content.replace(old_1, new_1, 1)

# EDIT 2: replace generate_smart_po with generate_po_suggestions
old_2 = '''async def generate_smart_po(request_id: str, db):
    """Background task to generate PO using AI"""
    try:
        po_request = await db.po_requests.find_one({"id": request_id})
        if not po_request:
            return
        
        # Get vendor suggestions based on product categories
        vendors = []
        categories = set()
        brands = set()
        
        for item in po_request["items"]:
            if item.get("category"):
                categories.add(item["category"])
            if item.get("brand"):
                brands.add(item["brand"])
        
        # Find vendors for these categories/brands
        vendor_query = {}
        if brands:
            vendor_query["brands"] = {"$in": list(brands)}
        
        suggested_vendors = await db.vendors.find(vendor_query, {"_id": 0}).limit(3).to_list(3)
        
        # Try to use AI for smart suggestions
        ai_suggestions = None
        try:
            api_key = os.environ.get("EMERGENT_LLM_KEY")
            if api_key:
                from emergentintegrations.llm.gemini import GeminiConfig, gemini_text_request
                
                config = GeminiConfig(
                    api_key=api_key,
                    model="gemini-2.5-flash"
                )
                
                items_text = "\\n".join([
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
        
        # Generate the PO
        po_count = await db.purchases.count_documents({})
        po_number = f"PO-{datetime.now().strftime('%Y%m')}-{po_count + 1:04d}"
        po_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        # Select primary vendor
        primary_vendor = suggested_vendors[0] if suggested_vendors else {
            "id": "default",
            "name": "Default Vendor",
            "contact": ""
        }
        
        po_data = {
            "id": po_id,
            "po_number": po_number,
            "vendor_id": primary_vendor.get("id"),
            "vendor_name": primary_vendor.get("name", "To Be Assigned"),
            "store_id": po_request["store_id"],
            "store_name": po_request["store_name"],
            "po_request_id": request_id,
            "items": [{
                "product_id": item.get("product_id", ""),
                "product_name": item["product_name"],
                "model_number": item["model_number"],
                "sku": item.get("sku"),
                "quantity": item["quantity"],
                "unit_price": item.get("cost_price", 0),
                "total": item["quantity"] * (item.get("cost_price", 0) or 0)
            } for item in po_request["items"]],
            "subtotal": po_request["estimated_value"],
            "tax_amount": po_request["estimated_value"] * 0.18,  # 18% GST estimate
            "total_amount": po_request["estimated_value"] * 1.18,
            "status": "draft",  # draft, pending_approval, approved, sent_to_vendor, partial, completed
            "urgency": po_request["urgency"],
            "notes": po_request["notes"],
            "ai_generated": True,
            "ai_suggestions": ai_suggestions,
            "created_at": now,
            "updated_at": now
        }
        
        await db.purchases.insert_one(po_data)
        
        # Update PO request
        await db.po_requests.update_one(
            {"id": request_id},
            {"$set": {
                "status": "po_generated",
                "generated_po_id": po_id,
                "generated_po_number": po_number,
                "ai_suggestions": ai_suggestions,
                "updated_at": now
            }}
        )
        
        logger.info(f"Generated PO {po_number} for request {po_request['request_number']}")
        
    except Exception as e:
        logger.error(f"Error generating smart PO: {e}")
        await db.po_requests.update_one(
            {"id": request_id},
            {"$set": {
                "status": "generation_failed",
                "ai_suggestions": f"PO generation failed: {str(e)}",
                "updated_at": datetime.now(timezone.utc)
            }}
        )'''

new_2 = '''async def generate_po_suggestions(request_id: str, db):
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

                items_text = "\\n".join([
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
        logger.error(f"Error generating PO suggestions: {e}")'''

assert old_2 in content, "EDIT 2 anchor not found - generate_smart_po body did not match exactly"
content = content.replace(old_2, new_2, 1)

# EDIT 3: insert PUT edit endpoint before approve endpoint, and rewrite approve branch
old_3 = '''@router.post("/po-requests/{request_id}/approve")
async def approve_po_request(
    request_id: str,
    action: ApprovalAction,
    db = Depends(get_db)
):
    """Approve or reject PO request and its generated PO"""
    try:
        po_request = await db.po_requests.find_one({"id": request_id})
        if not po_request:
            raise HTTPException(status_code=404, detail="PO request not found")
        
        # Allow approval from pending, pending_review, or po_generated status
        if po_request["status"] not in ["pending", "pending_review", "po_generated"]:
            raise HTTPException(status_code=400, detail=f"Cannot approve request in {po_request['status']} status")
        
        now = datetime.now(timezone.utc)
        
        if action.action == "approve":
            new_status = "approved"
            po_status = "approved"
            message = "PO request approved. Purchase order ready to send to vendor."
            
            # Build update data
            update_data = {
                "status": new_status,
                "approved_by": action.approved_by,
                "approved_at": now,
                "review_date": now,
                "review_comments": action.comments,
                "updated_at": now
            }
            
            # Add delivery location if provided
            if action.delivery_location:
                update_data["delivery_location"] = action.delivery_location
            
            # Update the generated PO status if exists
            if po_request.get("generated_po_id"):
                await db.purchases.update_one(
                    {"id": po_request["generated_po_id"]},
                    {"$set": {
                        "status": po_status, 
                        "delivery_location": action.delivery_location,
                        "approved_by": action.approved_by,
                        "approved_at": now,
                        "updated_at": now
                    }}
                )
            
            # Create a notification for the requesting store'''

new_3 = '''class POItemEdit(BaseModel):
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
            update_data["estimated_value"] = sum(
                (i.get("quantity", 0) or 0) * (i.get("cost_price", 0) or 0) for i in new_items
            )

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
                await db.purchases.update_one(
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
                po_count = await db.purchases.count_documents({})
                po_number = f"PO-{datetime.now().strftime('%Y%m')}-{po_count + 1:04d}"
                po_id = str(uuid.uuid4())

                items = po_request.get("items", [])
                subtotal = sum(
                    (item.get("quantity", 0) or 0) * (item.get("cost_price", item.get("unit_price", 0)) or 0)
                    for item in items
                )

                po_data = {
                    "id": po_id,
                    "po_number": po_number,
                    "vendor_id": po_request.get("suggested_vendor_id"),
                    "vendor_name": po_request.get("supplier_name") or po_request.get("suggested_vendor_name") or "To Be Assigned",
                    "store_id": po_request["store_id"],
                    "store_name": po_request["store_name"],
                    "po_request_id": request_id,
                    "items": [{
                        "product_id": item.get("product_id", ""),
                        "product_name": item.get("product_name"),
                        "model_number": item.get("model_number"),
                        "sku": item.get("sku"),
                        "quantity": item.get("quantity", 0),
                        "unit_price": item.get("cost_price", item.get("unit_price", 0)) or 0,
                        "total": (item.get("quantity", 0) or 0) * (item.get("cost_price", item.get("unit_price", 0)) or 0)
                    } for item in items],
                    "subtotal": subtotal,
                    "tax_amount": subtotal * 0.18,
                    "total_amount": subtotal * 1.18,
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

                await db.purchases.insert_one(po_data)

                update_data["generated_po_id"] = po_id
                update_data["generated_po_number"] = po_number
            
            # Create a notification for the requesting store'''

assert old_3 in content, "EDIT 3 anchor not found - approve_po_request start did not match exactly"
content = content.replace(old_3, new_3, 1)

needs = []
if "from typing import" in content:
    m = re.search(r"from typing import[^\n]*", content).group(0)
    if "Optional" not in m:
        needs.append("Add Optional to 'from typing import' line")
    if "List" not in m:
        needs.append("Add List to 'from typing import' line")
else:
    needs.append("Add 'from typing import Optional, List' near top of file")

if "from pydantic import" not in content and "import pydantic" not in content:
    needs.append("Add 'from pydantic import BaseModel' near top of file")

with open(TARGET, "w") as f:
    f.write(content)

print("Patched", TARGET)
print("Backup saved at", TARGET + ".bak")
if needs:
    print("\nACTION NEEDED:")
    for n in needs:
        print(" -", n)
else:
    print("Typing/pydantic imports look fine.")
