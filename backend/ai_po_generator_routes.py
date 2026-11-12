"""
AI Purchase Order Generator
Generates draft POs from natural language requests
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from database import get_db
from datetime import datetime, timezone
import uuid
import os
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json

router = APIRouter(prefix="/ai-po-generator", tags=["AI PO Generator"])

class GeneratePORequest(BaseModel):
    request: str  # Natural language request
    user_email: str

@router.post("/generate")
async def generate_po_from_request(request: GeneratePORequest, db = Depends(get_db)):
    """
    Generate draft purchase order from natural language request
    Example: "Create PO for 10 Bosch washing machines model WAJ2846IIN"
    """
    try:
        # Step 1: Use LLM to extract structured data from request
        system_prompt = """You are an AI assistant that extracts purchase order information from natural language.
Extract the following information and return ONLY a JSON object:
{
  "quantity": <number>,
  "product_search": "<product name, brand, model number to search>",
  "vendor_preference": "<vendor name if mentioned, else null>",
  "notes": "<any special instructions>"
}

Examples:
Input: "Create PO for 10 Bosch washing machines model WAJ2846IIN"
Output: {"quantity": 10, "product_search": "Bosch washing machine WAJ2846IIN", "vendor_preference": null, "notes": null}

Input: "Need 5 Samsung fridges from Vendor ABC with urgent delivery"
Output: {"quantity": 5, "product_search": "Samsung fridge", "vendor_preference": "Vendor ABC", "notes": "urgent delivery"}

Return ONLY the JSON object, nothing else."""

        chat = LlmChat(
            api_key=os.environ.get("EMERGENT_LLM_KEY"),
            session_id=f"po_gen_{datetime.now().timestamp()}",
            system_message=system_prompt
        ).with_model("gemini", "gemini-2.5-pro")
        
        user_msg = UserMessage(text=request.request)
        response = await chat.send_message(user_msg)
        
        # Parse LLM response
        if isinstance(response, dict):
            llm_response = response.get('content', response.get('message', ''))
        else:
            llm_response = str(response)
        
        # Clean and parse JSON
        llm_response = llm_response.strip()
        if llm_response.startswith('```json'):
            llm_response = llm_response[7:]
        if llm_response.startswith('```'):
            llm_response = llm_response[3:]
        if llm_response.endswith('```'):
            llm_response = llm_response[:-3]
        llm_response = llm_response.strip()
        
        extracted_data = json.loads(llm_response)
        
        # Step 2: Search for product in database
        product_search = extracted_data.get('product_search', '')
        search_terms = product_search.lower().split()
        
        # Build search query
        search_conditions = []
        for term in search_terms:
            search_conditions.append({
                "$or": [
                    {"name": {"$regex": term, "$options": "i"}},
                    {"brand": {"$regex": term, "$options": "i"}},
                    {"model_number": {"$regex": term, "$options": "i"}},
                    {"category": {"$regex": term, "$options": "i"}}
                ]
            })
        
        products = await db.products.find(
            {"$and": search_conditions} if search_conditions else {},
            {"_id": 0}
        ).limit(5).to_list(5)
        
        if not products:
            return {
                "status": "error",
                "message": f"No products found matching: {product_search}",
                "extracted_data": extracted_data
            }
        
        # Use first matching product
        product = products[0]
        quantity = extracted_data.get('quantity', 1)
        
        # Step 3: Create draft PO
        draft_po_id = str(uuid.uuid4())
        draft_number = f"DRAFT-PO-{datetime.now().strftime('%Y%m%d')}-{draft_po_id[:8].upper()}"
        
        # Calculate amounts
        rate = product.get('price', 0)
        item_subtotal = rate * quantity
        tax_rate = 18.0  # Default GST
        tax_amount = (item_subtotal * tax_rate) / 100
        total_amount = item_subtotal + tax_amount
        
        draft_po = {
            "id": draft_po_id,
            "draft_number": draft_number,
            "po_number": None,  # Will be generated on approval
            "status": "draft",
            "po_date": datetime.now(timezone.utc).isoformat(),
            "expected_delivery_date": datetime.now(timezone.utc).isoformat(),
            "vendor": {
                "name": extracted_data.get('vendor_preference') or "TO BE DECIDED",
                "phone": "",
                "email": "",
                "gst_number": "",
                "address": "",
                "city": "",
                "state": "",
                "pincode": ""
            },
            "items": [{
                "product_id": product.get('id'),
                "product_name": product.get('name'),
                "hsn_code": product.get('hsn_code', ''),
                "quantity": quantity,
                "rate": rate,
                "discount": 0,
                "tax_rate": tax_rate
            }],
            "payment_mode": "cash",
            "discount": 0,
            "shipping_charges": 0,
            "round_off": 0,
            "subtotal": item_subtotal,
            "total_amount": total_amount,
            "notes": extracted_data.get('notes') or f"AI Generated from request: {request.request}",
            "created_by": request.user_email,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "ai_generated": True,
            "original_request": request.request
        }
        
        # Save draft to database
        await db.purchase_drafts.insert_one(draft_po)
        
        # Create a clean version of draft_po for response (excluding any potential ObjectId fields)
        clean_draft_po = {
            "id": draft_po["id"],
            "draft_number": draft_po["draft_number"],
            "status": draft_po["status"],
            "vendor": draft_po["vendor"],
            "items": draft_po["items"],
            "subtotal": draft_po["subtotal"],
            "total_amount": draft_po["total_amount"],
            "notes": draft_po["notes"],
            "created_by": draft_po["created_by"],
            "ai_generated": draft_po["ai_generated"],
            "original_request": draft_po["original_request"]
        }
        
        return {
            "status": "success",
            "message": f"Draft PO created successfully: {draft_number}",
            "draft_id": draft_po_id,
            "draft_number": draft_number,
            "draft_po": clean_draft_po,
            "matched_product": {
                "name": product.get('name'),
                "brand": product.get('brand'),
                "model_number": product.get('model_number'),
                "price": product.get('price')
            },
            "alternative_products": [
                {
                    "name": p.get('name'),
                    "brand": p.get('brand'),
                    "model_number": p.get('model_number'),
                    "price": p.get('price')
                } for p in products[1:4]
            ] if len(products) > 1 else []
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI PO Generator error: {str(e)}")

@router.get("/drafts")
async def get_draft_pos(db = Depends(get_db)):
    """Get all draft purchase orders"""
    try:
        drafts = await db.purchase_drafts.find(
            {"status": "draft"},
            {"_id": 0}
        ).sort("created_at", -1).to_list(None)
        
        return {
            "status": "success",
            "drafts": drafts,
            "count": len(drafts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/drafts/{draft_id}/approve")
async def approve_draft_po(draft_id: str, db = Depends(get_db)):
    """Approve draft and convert to actual PO"""
    try:
        # Get draft
        draft = await db.purchase_drafts.find_one({"id": draft_id}, {"_id": 0})
        
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")
        
        # Generate actual PO number
        po_count = await db.purchases.count_documents({})
        po_number = f"PO-ADR-{datetime.now().strftime('%Y%m%d')}-{po_count + 1:04d}"
        
        # Create actual PO
        purchase_order = {
            **draft,
            "po_number": po_number,
            "status": "pending",
            "approved_at": datetime.now(timezone.utc).isoformat()
        }
        purchase_order.pop("draft_number", None)
        purchase_order.pop("ai_generated", None)
        purchase_order.pop("original_request", None)
        
        # Save to purchases collection
        await db.purchases.insert_one(purchase_order)
        
        # Update draft status
        await db.purchase_drafts.update_one(
            {"id": draft_id},
            {"$set": {
                "status": "approved",
                "po_number": po_number,
                "approved_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "status": "success",
            "message": f"Draft approved and converted to PO: {po_number}",
            "po_number": po_number,
            "po_id": draft_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/drafts/{draft_id}")
async def delete_draft_po(draft_id: str, db = Depends(get_db)):
    """Delete a draft PO"""
    try:
        result = await db.purchase_drafts.delete_one({"id": draft_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Draft not found")
        
        return {
            "status": "success",
            "message": "Draft deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/drafts/{draft_id}")
async def update_draft_po(draft_id: str, updated_data: dict, db = Depends(get_db)):
    """Update a draft PO"""
    try:
        updated_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        result = await db.purchase_drafts.update_one(
            {"id": draft_id},
            {"$set": updated_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Draft not found")
        
        return {
            "status": "success",
            "message": "Draft updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
