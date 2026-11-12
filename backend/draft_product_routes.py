"""
Draft Product Management Routes
Handles auto-creation of products from purchase bills
Products are created as drafts until images/details are added
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from database import get_db
from file_storage import save_upload, serve_upload
import uuid
import os
import logging

router = APIRouter(prefix="/draft-products", tags=["Draft Products"])
logger = logging.getLogger(__name__)

# Upload directory for product images
PRODUCT_IMAGE_DIR = "/app/backend/uploads/product_images"
os.makedirs(PRODUCT_IMAGE_DIR, exist_ok=True)


class CreateDraftProductRequest(BaseModel):
    item_name: str
    model_number: Optional[str] = ""
    hsn_code: Optional[str] = ""
    brand: Optional[str] = ""
    category: Optional[str] = "uncategorized"
    purchase_price: float = 0
    selling_price: Optional[float] = None
    mrp: Optional[float] = None
    item_type: str = "product"  # product, part, consumable
    vendor_name: Optional[str] = ""
    # Link to purchase bill
    source_bill_id: Optional[str] = None
    source_bill_number: Optional[str] = None


class BulkCreateRequest(BaseModel):
    items: List[CreateDraftProductRequest]


class PublishProductRequest(BaseModel):
    product_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    selling_price: Optional[float] = None
    mrp: Optional[float] = None


# ============ CHECK IF ITEM EXISTS ============

@router.post("/check-items")
async def check_items_exist(
    items: List[Dict[str, Any]],
    db = Depends(get_db)
):
    """
    Check which items from a purchase bill already exist in catalog
    Returns list of new items that need to be created
    """
    try:
        results = []
        
        for item in items:
            item_name = item.get('product_name', '').strip()
            item_name_upper = item_name.upper()
            
            # Check by exact name
            existing_by_name = await db.products.find_one({
                "name": {"$regex": f"^{item_name}$", "$options": "i"}
            })
            
            # Check by model number
            existing_by_model = await db.products.find_one({
                "model_number": {"$regex": f"^{item_name_upper}$", "$options": "i"}
            })
            
            if existing_by_name or existing_by_model:
                existing = existing_by_name or existing_by_model
                results.append({
                    "item_name": item_name,
                    "exists": True,
                    "matched_product_id": existing.get('id'),
                    "matched_product_name": existing.get('name'),
                    "matched_model": existing.get('model_number')
                })
            else:
                # Check if already in drafts
                draft = await db.products.find_one({
                    "model_number": {"$regex": f"^{item_name_upper}$", "$options": "i"},
                    "status": "draft"
                })
                
                results.append({
                    "item_name": item_name,
                    "exists": False,
                    "is_draft": draft is not None,
                    "draft_id": draft.get('id') if draft else None,
                    "hsn_code": item.get('hsn_code', ''),
                    "quantity": item.get('quantity', 1),
                    "rate": item.get('rate', 0)
                })
        
        new_items = [r for r in results if not r.get('exists') and not r.get('is_draft')]
        
        return {
            "status": "success",
            "total_items": len(items),
            "existing_items": len([r for r in results if r.get('exists')]),
            "draft_items": len([r for r in results if r.get('is_draft')]),
            "new_items": len(new_items),
            "results": results,
            "items_to_create": new_items
        }
        
    except Exception as e:
        logger.error(f"Check items failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ CREATE DRAFT PRODUCT ============

@router.post("/create")
async def create_draft_product(
    request: CreateDraftProductRequest,
    db = Depends(get_db)
):
    """
    Create a single draft product from purchase bill item
    """
    try:
        # Check if already exists
        existing = await db.products.find_one({
            "$or": [
                {"name": {"$regex": f"^{request.item_name}$", "$options": "i"}},
                {"model_number": {"$regex": f"^{request.model_number or request.item_name}$", "$options": "i"}}
            ]
        })
        
        if existing:
            return {
                "status": "exists",
                "message": f"Product already exists: {existing.get('name')}",
                "product_id": existing.get('id')
            }
        
        # Calculate prices
        purchase_price = request.purchase_price
        selling_price = request.selling_price or round(purchase_price * 1.20, 2)  # 20% margin
        mrp = request.mrp or round(purchase_price * 1.30, 2)  # 30% markup for MRP
        
        # Determine visibility based on item type
        is_visible = False  # All drafts start hidden
        
        product_id = str(uuid.uuid4())
        product_data = {
            "id": product_id,
            "name": request.item_name,
            "model_number": request.model_number or request.item_name,
            "brand": request.brand or "Unknown",
            "category": request.category or "uncategorized",
            "hsn_code": request.hsn_code or "",
            "purchase_price": purchase_price,
            "price": selling_price,
            "mrp": mrp,
            "stock_quantity": 0,
            "item_type": request.item_type,  # product, part, consumable
            "status": "draft",  # draft, published, archived
            "is_visible": is_visible,
            "description": "Auto-created from purchase bill. Please add description.",
            "short_description": "",
            "images": [],
            "specifications": [],
            "features": [],
            "warranty": "",
            "vendor_name": request.vendor_name,
            "source_bill_id": request.source_bill_id,
            "source_bill_number": request.source_bill_number,
            "needs_review": True,
            "review_notes": ["Missing images", "Missing description"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "created_from": "purchase_bill"
        }
        
        await db.products.insert_one(product_data)
        
        return {
            "status": "success",
            "message": f"Draft product '{request.item_name}' created",
            "product_id": product_id,
            "product": {
                "id": product_id,
                "name": request.item_name,
                "model_number": product_data["model_number"],
                "status": "draft",
                "item_type": request.item_type,
                "price": selling_price
            }
        }
        
    except Exception as e:
        logger.error(f"Create draft product failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-create")
async def bulk_create_draft_products(
    request: BulkCreateRequest,
    db = Depends(get_db)
):
    """
    Create multiple draft products at once
    """
    try:
        created = []
        skipped = []
        
        for item in request.items:
            # Check if exists
            existing = await db.products.find_one({
                "$or": [
                    {"name": {"$regex": f"^{item.item_name}$", "$options": "i"}},
                    {"model_number": {"$regex": f"^{item.model_number or item.item_name}$", "$options": "i"}}
                ]
            })
            
            if existing:
                skipped.append({
                    "item_name": item.item_name,
                    "reason": f"Already exists as: {existing.get('name')}"
                })
                continue
            
            # Create product
            purchase_price = item.purchase_price
            selling_price = item.selling_price or round(purchase_price * 1.20, 2)
            mrp = item.mrp or round(purchase_price * 1.30, 2)
            
            product_id = str(uuid.uuid4())
            product_data = {
                "id": product_id,
                "name": item.item_name,
                "model_number": item.model_number or item.item_name,
                "brand": item.brand or "Unknown",
                "category": item.category or "uncategorized",
                "hsn_code": item.hsn_code or "",
                "purchase_price": purchase_price,
                "price": selling_price,
                "mrp": mrp,
                "stock_quantity": 0,
                "item_type": item.item_type,
                "status": "draft",
                "is_visible": False,
                "description": "Auto-created from purchase bill. Please add description.",
                "images": [],
                "specifications": [],
                "vendor_name": item.vendor_name,
                "source_bill_id": item.source_bill_id,
                "source_bill_number": item.source_bill_number,
                "needs_review": True,
                "review_notes": ["Missing images", "Missing description"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "created_from": "purchase_bill"
            }
            
            await db.products.insert_one(product_data)
            created.append({
                "id": product_id,
                "name": item.item_name,
                "item_type": item.item_type
            })
        
        return {
            "status": "success",
            "message": f"Created {len(created)} draft products, skipped {len(skipped)}",
            "created": created,
            "skipped": skipped
        }
        
    except Exception as e:
        logger.error(f"Bulk create failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ GET DRAFT PRODUCTS ============

@router.get("/")
async def get_draft_products(
    page: int = 1,
    limit: int = 20,
    item_type: Optional[str] = None,
    needs_review: Optional[bool] = None,
    db = Depends(get_db)
):
    """
    Get all draft products pending review
    """
    try:
        query = {"status": "draft"}
        
        if item_type:
            query["item_type"] = item_type
        if needs_review is not None:
            query["needs_review"] = needs_review
        
        skip = (page - 1) * limit
        
        products = await db.products.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
        total = await db.products.count_documents(query)
        
        # Get counts by type
        product_count = await db.products.count_documents({"status": "draft", "item_type": "product"})
        part_count = await db.products.count_documents({"status": "draft", "item_type": "part"})
        consumable_count = await db.products.count_documents({"status": "draft", "item_type": "consumable"})
        
        return {
            "status": "success",
            "products": products,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit,
            "counts": {
                "all": total,
                "products": product_count,
                "parts": part_count,
                "consumables": consumable_count
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_draft_summary(db = Depends(get_db)):
    """
    Get summary of draft products
    """
    try:
        total_drafts = await db.products.count_documents({"status": "draft"})
        missing_images = await db.products.count_documents({"status": "draft", "images": {"$size": 0}})
        missing_description = await db.products.count_documents({
            "status": "draft", 
            "$or": [
                {"description": ""},
                {"description": {"$regex": "Auto-created"}}
            ]
        })
        
        by_type = {
            "products": await db.products.count_documents({"status": "draft", "item_type": "product"}),
            "parts": await db.products.count_documents({"status": "draft", "item_type": "part"}),
            "consumables": await db.products.count_documents({"status": "draft", "item_type": "consumable"})
        }
        
        return {
            "status": "success",
            "summary": {
                "total_drafts": total_drafts,
                "missing_images": missing_images,
                "missing_description": missing_description,
                "ready_to_publish": total_drafts - missing_images,
                "by_type": by_type
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ UPDATE DRAFT PRODUCT ============

@router.put("/{product_id}")
async def update_draft_product(
    product_id: str,
    updates: Dict[str, Any],
    db = Depends(get_db)
):
    """
    Update a draft product
    """
    try:
        existing = await db.products.find_one({"id": product_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Don't allow changing certain fields
        protected_fields = ["id", "created_at", "created_from"]
        for field in protected_fields:
            updates.pop(field, None)
        
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Update review notes based on what's filled
        review_notes = []
        if not updates.get("images") and not existing.get("images"):
            review_notes.append("Missing images")
        if updates.get("description", existing.get("description", "")).startswith("Auto-created"):
            review_notes.append("Missing description")
        
        updates["review_notes"] = review_notes
        updates["needs_review"] = len(review_notes) > 0
        
        await db.products.update_one({"id": product_id}, {"$set": updates})
        
        return {"status": "success", "message": "Product updated"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ PUBLISH PRODUCT ============

@router.post("/{product_id}/publish")
async def publish_product(
    product_id: str,
    db = Depends(get_db)
):
    """
    Publish a draft product to make it visible on website
    """
    try:
        product = await db.products.find_one({"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if product.get("status") == "published":
            return {"status": "info", "message": "Product is already published"}
        
        # Check if it has images (required for publishing)
        if not product.get("images") or len(product.get("images", [])) == 0:
            raise HTTPException(
                status_code=400, 
                detail="Cannot publish product without images. Please add at least one image."
            )
        
        await db.products.update_one(
            {"id": product_id},
            {"$set": {
                "status": "published",
                "is_visible": True,
                "needs_review": False,
                "review_notes": [],
                "published_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "status": "success",
            "message": f"Product '{product.get('name')}' is now live on website!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-publish")
async def bulk_publish_products(
    product_ids: List[str],
    db = Depends(get_db)
):
    """
    Publish multiple products at once
    """
    try:
        published = []
        failed = []
        
        for product_id in product_ids:
            product = await db.products.find_one({"id": product_id})
            if not product:
                failed.append({"id": product_id, "reason": "Not found"})
                continue
            
            if not product.get("images") or len(product.get("images", [])) == 0:
                failed.append({"id": product_id, "name": product.get("name"), "reason": "No images"})
                continue
            
            await db.products.update_one(
                {"id": product_id},
                {"$set": {
                    "status": "published",
                    "is_visible": True,
                    "needs_review": False,
                    "review_notes": [],
                    "published_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            published.append({"id": product_id, "name": product.get("name")})
        
        return {
            "status": "success",
            "message": f"Published {len(published)} products, {len(failed)} failed",
            "published": published,
            "failed": failed
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ UPLOAD IMAGE ============

@router.post("/{product_id}/upload-image")
async def upload_product_image(
    product_id: str,
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    """
    Upload an image for a draft product
    """
    try:
        product = await db.products.find_one({"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Only JPEG, PNG, and WebP images are allowed")
        
        # Save file
        file_ext = os.path.splitext(file.filename)[1]
        image_id = str(uuid.uuid4())
        filename = f"{product_id}_{image_id}{file_ext}"
        
        content = await file.read()
        await save_upload(filename, content, file.content_type)
        
        # Generate URL
        image_url = f"/api/draft-products/images/{filename}"
        
        # Add to product images
        images = product.get("images", [])
        images.append({
            "id": image_id,
            "url": image_url,
            "filename": filename,
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Update review notes
        review_notes = [note for note in product.get("review_notes", []) if note != "Missing images"]
        
        await db.products.update_one(
            {"id": product_id},
            {"$set": {
                "images": images,
                "review_notes": review_notes,
                "needs_review": len(review_notes) > 0,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "status": "success",
            "message": "Image uploaded successfully",
            "image": {
                "id": image_id,
                "url": image_url
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/{filename}")
async def get_product_image(filename: str):
    """
    Serve product images
    """
    from fastapi.responses import FileResponse
    
    filepath = f"{PRODUCT_IMAGE_DIR}/{filename}"
    if os.path.exists(filepath):
        return FileResponse(filepath)
    
    return await serve_upload(filename)


# ============ DELETE DRAFT ============

@router.delete("/{product_id}")
async def delete_draft_product(
    product_id: str,
    db = Depends(get_db)
):
    """
    Delete a draft product
    """
    try:
        result = await db.products.delete_one({"id": product_id, "status": "draft"})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Draft product not found")
        
        return {"status": "success", "message": "Draft product deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ FIND INCOMPLETE PRODUCTS ============

@router.get("/incomplete")
async def get_incomplete_products(
    page: int = 1,
    limit: int = 20,
    filter_type: str = "all",  # all, no_image, no_category, no_description, pending_review
    db = Depends(get_db)
):
    """
    Find products that are incomplete - missing images, category, or description.
    These are products that were created during billing but need enhancement.
    Also includes any product flagged with is_listed=False (i.e. pending admin
    approval from store/Tally/reconciliation insertions).
    """
    try:
        # Build query for incomplete products
        # A product is incomplete if it's missing: image, proper category, or description
        query_conditions = []
        
        # Missing image — a product truly has NO image only when ALL of these are
        # empty/missing: images[] (primary), image (legacy singular), image_url
        # (legacy alt name). Using $or here was the original bug: that matched
        # products that had a usable image but lacked one of the alt fields.
        missing_image_condition = {
            "$and": [
                {"$or": [{"images": {"$exists": False}}, {"images": {"$size": 0}}, {"images": None}]},
                {"$or": [{"image": {"$exists": False}}, {"image": ""}, {"image": None}]},
                {"$or": [{"image_url": {"$exists": False}}, {"image_url": ""}, {"image_url": None}]},
            ]
        }

        # Products awaiting admin approval (auto-gated from offline workflows)
        pending_review_condition = {
            "$or": [
                {"is_listed": False},
                {"review_status": "pending_review"},
            ]
        }

        if filter_type in ["all", "no_image"]:
            query_conditions.append(missing_image_condition)
        
        # Missing or uncategorized category
        if filter_type in ["all", "no_category"]:
            query_conditions.append({
                "$or": [
                    {"category": {"$exists": False}},
                    {"category": ""},
                    {"category": None},
                    {"category": "uncategorized"},
                    {"category": "other"},
                    {"category": "Unknown"}
                ]
            })
        
        # Missing description
        if filter_type in ["all", "no_description"]:
            query_conditions.append({
                "$or": [
                    {"description": {"$exists": False}},
                    {"description": ""},
                    {"description": None}
                ]
            })
        
        # Combine with OR for "all" filter, use single condition for specific filter
        if filter_type == "pending_review":
            query = pending_review_condition
        elif filter_type == "all":
            # "all" = anything incomplete OR pending review
            query = {"$or": query_conditions + [pending_review_condition]}
        elif query_conditions:
            query = query_conditions[0]
        else:
            query = {}
        
        # Exclude already-draft products (they're managed elsewhere)
        query["status"] = {"$ne": "draft"}
        
        # Get total count
        total = await db.products.count_documents(query)
        
        # Pagination
        skip = (page - 1) * limit
        
        # Fetch products
        products = await db.products.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        # Categorize missing fields for each product
        for product in products:
            missing = []
            # A product has no image only when all 3 fields are empty
            if (not product.get("images") and
                    not product.get("image") and
                    not product.get("image_url")):
                missing.append("image")
            if not product.get("category") or product.get("category") in ["uncategorized", "other", "Unknown"]:
                missing.append("category")
            if not product.get("description"):
                missing.append("description")
            if not product.get("specifications"):
                missing.append("specifications")
            product["missing_fields"] = missing
        
        return {
            "status": "success",
            "products": products,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error fetching incomplete products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incomplete/summary")
async def get_incomplete_products_summary(db = Depends(get_db)):
    """
    Get summary of incomplete products
    """
    try:
        # Reusable "missing image" predicate: a product has NO image only when
        # all of images[], image (legacy singular) and image_url are missing/empty.
        # Note: don't include {"images": []} in the $or — Mongo's $size:0 already
        # covers that case, and the literal empty array equality is buggy in some
        # Mongo versions for type-mismatched docs.
        missing_image_clause = {
            "$and": [
                {"$or": [{"images": {"$exists": False}}, {"images": {"$size": 0}}, {"images": None}]},
                {"$or": [{"image": {"$exists": False}}, {"image": ""}, {"image": None}]},
                {"$or": [{"image_url": {"$exists": False}}, {"image_url": ""}, {"image_url": None}]},
            ]
        }

        # Count products with missing images (true missing — all 3 fields empty)
        no_image_count = await db.products.count_documents({
            "status": {"$ne": "draft"},
            **missing_image_clause,
        })
        
        # Count products with missing/bad category
        no_category_count = await db.products.count_documents({
            "status": {"$ne": "draft"},
            "$or": [
                {"category": {"$exists": False}},
                {"category": ""},
                {"category": None},
                {"category": "uncategorized"},
                {"category": "other"}
            ]
        })
        
        # Count products with missing description
        no_description_count = await db.products.count_documents({
            "status": {"$ne": "draft"},
            "$or": [
                {"description": {"$exists": False}},
                {"description": ""},
                {"description": None}
            ]
        })

        # Count products awaiting admin approval (auto-gated from offline)
        pending_review_count = await db.products.count_documents({
            "status": {"$ne": "draft"},
            "$or": [
                {"is_listed": False},
                {"review_status": "pending_review"},
            ]
        })
        
        # Total incomplete: any one of {no image, no category, no description}
        total_incomplete = await db.products.count_documents({
            "status": {"$ne": "draft"},
            "$or": [
                missing_image_clause,
                {"category": {"$in": ["", None, "uncategorized", "other"]}},
                {"category": {"$exists": False}},
                {"description": {"$in": ["", None]}},
                {"description": {"$exists": False}},
            ]
        })
        
        return {
            "status": "success",
            "summary": {
                "total_incomplete": total_incomplete,
                "missing_image": no_image_count,
                "missing_category": no_category_count,
                "missing_description": no_description_count,
                "pending_review": pending_review_count,
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching incomplete summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/incomplete/{product_id}/ai-enhance")
async def ai_enhance_product(
    product_id: str,
    db = Depends(get_db)
):
    """
    Use AI to automatically enhance an incomplete product:
    - Determine category based on product name
    - Generate description and specifications
    - Note: Images need to be manually added
    """
    try:
        # Find the product
        product = await db.products.find_one({"id": product_id}, {"_id": 0})
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product_name = product.get("name", "")
        brand = product.get("brand", "")
        
        # Determine category from product name
        category_keywords = {
            "refrigerator": ["refrigerator", "fridge", "freezer"],
            "washing_machine": ["washing", "washer", "laundry"],
            "dishwasher": ["dishwasher", "dish washer"],
            "microwave": ["microwave", "oven microwave"],
            "oven": ["oven", "otg", "built-in oven"],
            "cooktop": ["cooktop", "hob", "induction", "gas stove", "burner"],
            "chimney": ["chimney", "hood", "exhaust"],
            "dryer": ["dryer", "tumble dry"],
            "coffee_machine": ["coffee", "espresso"],
            "air_fryer": ["air fryer", "airfryer"],
            "mixer_grinder": ["mixer", "grinder", "blender", "juicer"],
            "vacuum_cleaner": ["vacuum", "cleaner"],
            "water_purifier": ["purifier", "ro", "water filter"],
            "air_conditioner": ["ac", "air conditioner", "air-conditioner"],
            "geyser": ["geyser", "water heater"],
            "power_tools": ["drill", "grinder", "saw", "sander", "angle grinder", "pressure washer"],
            "cooking_range": ["cooking range", "range cooker", "free standing"]
        }
        
        detected_category = "other"
        name_lower = product_name.lower()
        
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in name_lower:
                    detected_category = category
                    break
            if detected_category != "other":
                break
        
        # Generate simple description
        description = f"{brand} {product_name}. "
        if detected_category != "other":
            category_display = detected_category.replace("_", " ").title()
            description += f"A high-quality {category_display.lower()} from {brand}."
        
        # Update the product
        update_data = {
            "category": detected_category,
            "description": description,
            "ai_enhanced": True,
            "ai_enhanced_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.products.update_one(
            {"id": product_id},
            {"$set": update_data}
        )
        
        return {
            "status": "success",
            "message": f"Product enhanced with AI. Category: {detected_category}",
            "updates": update_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enhancing product: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/incomplete/bulk-ai-enhance")
async def bulk_ai_enhance_products(
    limit: int = 50,
    db = Depends(get_db)
):
    """
    AI enhance multiple incomplete products at once
    """
    try:
        # Find incomplete products
        query = {
            "status": {"$ne": "draft"},
            "$or": [
                {"category": {"$exists": False}},
                {"category": ""},
                {"category": "uncategorized"},
                {"category": "other"},
                {"description": {"$exists": False}},
                {"description": ""}
            ]
        }
        
        products = await db.products.find(query, {"_id": 0}).limit(limit).to_list(None)
        
        enhanced_count = 0
        
        for product in products:
            product_id = product.get("id")
            if product_id:
                try:
                    # Call the single product enhance endpoint logic
                    product_name = product.get("name", "")
                    brand = product.get("brand", "")
                    
                    # Determine category
                    category_keywords = {
                        "refrigerator": ["refrigerator", "fridge", "freezer"],
                        "washing_machine": ["washing", "washer", "laundry"],
                        "dishwasher": ["dishwasher"],
                        "microwave": ["microwave"],
                        "oven": ["oven", "otg"],
                        "cooktop": ["cooktop", "hob", "induction", "gas stove"],
                        "chimney": ["chimney", "hood"],
                        "dryer": ["dryer"],
                        "coffee_machine": ["coffee", "espresso"],
                        "air_fryer": ["air fryer"],
                        "mixer_grinder": ["mixer", "grinder", "blender"],
                        "vacuum_cleaner": ["vacuum"],
                        "water_purifier": ["purifier", "ro"],
                        "air_conditioner": ["ac", "air conditioner"],
                        "power_tools": ["drill", "grinder", "saw", "sander", "pressure washer"]
                    }
                    
                    detected_category = "other"
                    name_lower = product_name.lower()
                    
                    for category, keywords in category_keywords.items():
                        for keyword in keywords:
                            if keyword in name_lower:
                                detected_category = category
                                break
                        if detected_category != "other":
                            break
                    
                    description = f"{brand} {product_name}. A quality product from {brand}."
                    
                    await db.products.update_one(
                        {"id": product_id},
                        {"$set": {
                            "category": detected_category,
                            "description": description,
                            "ai_enhanced": True,
                            "ai_enhanced_at": datetime.now(timezone.utc).isoformat()
                        }}
                    )
                    enhanced_count += 1
                    
                except Exception as e:
                    logger.error(f"Error enhancing product {product_id}: {e}")
        
        return {
            "status": "success",
            "message": f"Enhanced {enhanced_count} products with AI",
            "enhanced_count": enhanced_count
        }
        
    except Exception as e:
        logger.error(f"Error in bulk AI enhance: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# ============================================================================
# URL EXTRACTION + APPROVAL FLOW
# These endpoints power the "Extract from URL" and "Approve & Publish" buttons
# in the Incomplete Products Manager. Designed for the offline → review →
# approve workflow:
#   1. Product gets created via store/Tally/reconciliation with is_listed=False
#   2. Admin opens Incomplete Products Manager, paste a competitor/brand URL
#   3. Frontend calls /api/products/extract-from-url (existing endpoint) and
#      then passes the result to apply-extracted-data here.
#   4. Once happy, admin clicks Approve & Publish.
# ============================================================================


class ApplyExtractedDataRequest(BaseModel):
    """Payload sent by the Incomplete Products Manager after the user paste-
    extracts product info from a URL via the existing
    /api/products/extract-from-url endpoint. Fields are all optional so the
    admin can selectively merge — empty strings/arrays do NOT overwrite the
    existing product value (keeps the store-entered name/price intact unless
    the admin explicitly wants to replace them)."""
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    model_number: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    images: Optional[List[str]] = None
    specifications: Optional[Any] = None
    highlights: Optional[List[str]] = None
    special_features: Optional[List[str]] = None
    technical_overview: Optional[str] = None
    energy_rating: Optional[str] = None
    dimensions: Optional[Dict[str, Any]] = None
    documents: Optional[List[Any]] = None
    warranty: Optional[Dict[str, Any]] = None
    price: Optional[float] = None
    mrp: Optional[float] = None
    source_url: Optional[str] = None


@router.post("/incomplete/{product_id}/apply-extracted-data")
async def apply_extracted_data(
    product_id: str,
    payload: ApplyExtractedDataRequest,
    db = Depends(get_db),
):
    """Merge AI-extracted product data into an existing (pending-review)
    product. The admin pasted a URL into Incomplete Products Manager → the
    frontend already called /api/products/extract-from-url → now we apply the
    extracted JSON onto the existing product document."""
    try:
        product = await db.products.find_one({"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Build update dict, only including fields the extractor actually
        # returned (so empty strings don't clobber the store-entered values).
        candidate = payload.model_dump(exclude_none=True)

        update_fields: Dict[str, Any] = {}
        for key, value in candidate.items():
            if key == "source_url":
                update_fields["product_url"] = value
                continue
            # Skip empty strings / empty lists so they don't blank out a
            # field that already has data.
            if isinstance(value, str) and not value.strip():
                continue
            if isinstance(value, list) and not value:
                continue
            update_fields[key] = value

        if not update_fields:
            return {
                "status": "success",
                "message": "No new data to apply",
                "updated_fields": [],
            }

        update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
        update_fields["last_extracted_at"] = datetime.now(timezone.utc).isoformat()

        await db.products.update_one(
            {"id": product_id},
            {"$set": update_fields},
        )

        return {
            "status": "success",
            "message": f"Applied {len(update_fields) - 2} fields from extracted data",
            "updated_fields": [k for k in update_fields.keys()
                               if k not in ("updated_at", "last_extracted_at")],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying extracted data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/incomplete/{product_id}/approve-publish")
async def approve_and_publish_product(product_id: str, db = Depends(get_db)):
    """Mark a pending-review product as approved and visible on storefront.

    Sets is_listed=True and review_status='published'. Idempotent — calling
    twice has no further effect."""
    try:
        product = await db.products.find_one({"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Friendly validation — at least require a name and an image before
        # publishing. Admin can still bypass by editing the product directly.
        has_image = bool(product.get("images") or product.get("image") or product.get("image_url"))
        if not (product.get("name") and has_image):
            raise HTTPException(
                status_code=400,
                detail="Product must have a name and at least one image before publishing.",
            )

        await db.products.update_one(
            {"id": product_id},
            {"$set": {
                "is_listed": True,
                "approval_status": "approved", "review_status": "published",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }}
        )
        return {
            "status": "success",
            "message": "Product approved and now visible on storefront",
            "product_id": product_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving product: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class BulkApproveRequest(BaseModel):
    product_ids: List[str]


@router.post("/incomplete/bulk-approve-publish")
async def bulk_approve_publish(payload: BulkApproveRequest, db = Depends(get_db)):
    """Bulk-approve several pending products at once. Products that don't pass
    the publish guard (no name or no image) are reported back as skipped."""
    if not payload.product_ids:
        raise HTTPException(status_code=400, detail="product_ids is required")

    approved: List[str] = []
    skipped: List[Dict[str, str]] = []

    for pid in payload.product_ids:
        try:
            product = await db.products.find_one({"id": pid})
            if not product:
                skipped.append({"id": pid, "reason": "Not found"})
                continue
            has_image = bool(product.get("images") or product.get("image") or product.get("image_url"))
            if not (product.get("name") and has_image):
                skipped.append({"id": pid, "reason": "Missing name or image"})
                continue
            await db.products.update_one(
                {"id": pid},
                {"$set": {
                    "is_listed": True,
                    "approval_status": "approved", "review_status": "published",
                    "published_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }}
            )
            approved.append(pid)
        except Exception as e:
            skipped.append({"id": pid, "reason": str(e)})

    return {
        "status": "success",
        "approved_count": len(approved),
        "skipped_count": len(skipped),
        "approved": approved,
        "skipped": skipped,
    }
