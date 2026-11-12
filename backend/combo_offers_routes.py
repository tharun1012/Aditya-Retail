"""
Combo and Bundle Offers Management
Create special offers when customers buy multiple products together
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import uuid
from database import get_db

router = APIRouter(prefix="/combo-offers", tags=["Combo Offers"])

class ComboOfferCreate(BaseModel):
    name: str
    description: str
    product_ids: List[str]  # List of product IDs in the combo
    discount_type: str  # 'percentage' or 'fixed'
    discount_value: float
    valid_from: str
    valid_until: str
    is_active: Optional[bool] = True
    min_quantity: Optional[int] = 1
    banner_image: Optional[str] = None
    # Banner display options
    show_on_banner: Optional[bool] = False
    banner_title: Optional[str] = None  # Custom title for banner
    banner_subtitle: Optional[str] = None
    banner_cta_text: Optional[str] = "Shop Now"
    banner_gradient: Optional[str] = "from-purple-600 to-indigo-600"
    banner_priority: Optional[int] = 1  # Higher shows first

@router.post("/")
async def create_combo_offer(offer: ComboOfferCreate, db = Depends(get_db)):
    """Create a new combo/bundle offer"""
    try:
        # Validate products exist
        products = []
        total_original_price = 0
        
        for product_id in offer.product_ids:
            product = await db.products.find_one({"id": product_id}, {"_id": 0})
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
            products.append(product)
            total_original_price += product.get('price', 0)
        
        # Calculate final price
        if offer.discount_type == 'percentage':
            final_price = total_original_price * (1 - offer.discount_value / 100)
            savings = total_original_price * (offer.discount_value / 100)
        else:  # fixed discount
            final_price = total_original_price - offer.discount_value
            savings = offer.discount_value
        
        combo_doc = {
            "id": str(uuid.uuid4()),
            "name": offer.name,
            "description": offer.description,
            "product_ids": offer.product_ids,
            "products": products,  # Store full product details
            "discount_type": offer.discount_type,
            "discount_value": offer.discount_value,
            "original_price": total_original_price,
            "final_price": final_price,
            "savings": savings,
            "valid_from": offer.valid_from,
            "valid_until": offer.valid_until,
            "is_active": offer.is_active,
            "min_quantity": offer.min_quantity,
            "banner_image": offer.banner_image,
            # Banner display options
            "show_on_banner": offer.show_on_banner,
            "banner_title": offer.banner_title or offer.name,
            "banner_subtitle": offer.banner_subtitle or f"Save ₹{savings:,.0f}",
            "banner_cta_text": offer.banner_cta_text,
            "banner_gradient": offer.banner_gradient,
            "banner_priority": offer.banner_priority,
            "orders_count": 0,
            "revenue_generated": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.combo_offers.insert_one(combo_doc)
        
        # Remove _id from response
        combo_doc.pop('_id', None)
        
        return {
            "status": "success",
            "message": "Combo offer created successfully",
            "offer": combo_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating combo offer: {str(e)}")

@router.get("/")
async def get_combo_offers(active_only: bool = False, db = Depends(get_db)):
    """Get all combo offers"""
    try:
        query = {}
        if active_only:
            query["is_active"] = True
            # Also check if current date is within valid range
            current_date = datetime.now(timezone.utc).isoformat()
            query["valid_from"] = {"$lte": current_date}
            query["valid_until"] = {"$gte": current_date}
        
        offers = await db.combo_offers.find(query, {"_id": 0}).to_list(100)
        offers = [await _live_pricing(db, o) for o in offers]
        
        # Transform offers for frontend compatibility
        transformed_combos = []
        for offer in offers:
            transformed_combos.append({
                "id": offer.get("id"),
                "name": offer.get("name"),
                "description": offer.get("description"),
                "products": offer.get("products", []),
                "discount_percentage": offer.get("discount_value") if offer.get("discount_type") == "percentage" else None,
                "combo_price": offer.get("final_price"),
                "total_price": offer.get("original_price"),
                "savings": offer.get("savings"),
                "banner_image": offer.get("banner_image"),
                "is_active": offer.get("is_active"),
                "valid_until": offer.get("valid_until")
            })
        
        return {
            "status": "success",
            "total": len(offers),
            "offers": offers,
            "combos": transformed_combos  # Frontend-compatible format
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching combo offers: {str(e)}")

@router.get("/{offer_id}")
async def get_combo_offer(offer_id: str, db = Depends(get_db)):
    """Get a specific combo offer"""
    try:
        offer = await db.combo_offers.find_one({"id": offer_id}, {"_id": 0})
        
        if not offer:
            raise HTTPException(status_code=404, detail="Combo offer not found")
        
        return {
            "status": "success",
            "offer": offer
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching combo offer: {str(e)}")

@router.put("/{offer_id}")
async def update_combo_offer(offer_id: str, updates: dict, db = Depends(get_db)):
    """Update combo offer"""
    try:
        offer = await db.combo_offers.find_one({"id": offer_id})
        if not offer:
            raise HTTPException(status_code=404, detail="Combo offer not found")
        
        # If product_ids or discount changed, recalculate prices
        if "product_ids" in updates or "discount_value" in updates or "discount_type" in updates:
            product_ids = updates.get("product_ids", offer["product_ids"])
            discount_type = updates.get("discount_type", offer["discount_type"])
            discount_value = updates.get("discount_value", offer["discount_value"])
            
            products = []
            total_original_price = 0
            
            for product_id in product_ids:
                product = await db.products.find_one({"id": product_id}, {"_id": 0})
                if product:
                    products.append(product)
                    total_original_price += product.get('price', 0)
            
            if discount_type == 'percentage':
                final_price = total_original_price * (1 - discount_value / 100)
                savings = total_original_price * (discount_value / 100)
            else:
                final_price = total_original_price - discount_value
                savings = discount_value
            
            updates["products"] = products
            updates["original_price"] = total_original_price
            updates["final_price"] = final_price
            updates["savings"] = savings
        
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await db.combo_offers.update_one(
            {"id": offer_id},
            {"$set": updates}
        )
        
        updated_offer = await db.combo_offers.find_one({"id": offer_id}, {"_id": 0})
        
        return {
            "status": "success",
            "message": "Combo offer updated successfully",
            "offer": updated_offer
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating combo offer: {str(e)}")

@router.delete("/{offer_id}")
async def delete_combo_offer(offer_id: str, hard_delete: bool = False, db = Depends(get_db)):
    """Delete combo offer (soft delete by default, hard delete if specified)"""
    try:
        offer = await db.combo_offers.find_one({"id": offer_id})
        if not offer:
            raise HTTPException(status_code=404, detail="Combo offer not found")
        
        if hard_delete:
            # Permanent deletion
            await db.combo_offers.delete_one({"id": offer_id})
            return {
                "status": "success",
                "message": "Combo offer permanently deleted"
            }
        else:
            # Soft delete - just deactivate
            await db.combo_offers.update_one(
                {"id": offer_id},
                {"$set": {
                    "is_active": False,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            return {
                "status": "success",
                "message": "Combo offer deactivated successfully"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting combo offer: {str(e)}")

@router.get("/active/homepage")
async def get_homepage_combos(db = Depends(get_db)):
    """Get active combo offers for homepage display"""
    try:
        current_date = datetime.now(timezone.utc).isoformat()
        
        offers = await db.combo_offers.find({
            "is_active": True,
            "valid_from": {"$lte": current_date},
            "valid_until": {"$gte": current_date}
        }, {"_id": 0}).sort([("created_at", -1)]).limit(6).to_list(6)
        
        return {
            "status": "success",
            "total": len(offers),
            "offers": offers
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching homepage combos: {str(e)}")


@router.get("/banner/featured")
async def get_banner_combos(db = Depends(get_db)):
    """Get combo offers that should be displayed on the homepage banner"""
    try:
        current_date = datetime.now(timezone.utc).isoformat()
        
        # Get combos marked to show on banner
        offers = await db.combo_offers.find({
            "is_active": True,
            "show_on_banner": True,
            "valid_from": {"$lte": current_date},
            "valid_until": {"$gte": current_date}
        }, {"_id": 0}).sort([("banner_priority", -1), ("created_at", -1)]).limit(5).to_list(5)
        
        # Format for banner display
        banner_items = []
        for offer in offers:
            banner_items.append({
                "id": offer.get("id"),
                "type": "combo",
                "title": offer.get("banner_title") or offer.get("name"),
                "subtitle": offer.get("banner_subtitle") or offer.get("description"),
                "cta_text": offer.get("banner_cta_text", "Shop Now"),
                "gradient": offer.get("banner_gradient", "from-purple-600 to-indigo-600"),
                "image": offer.get("banner_image") or (offer.get("products", [{}])[0].get("images", [None])[0] if offer.get("products") else None),
                "link": f"/combos/{offer.get('id')}",
                "discount": offer.get("discount_value"),
                "discount_type": offer.get("discount_type"),
                "savings": offer.get("savings"),
                "original_price": offer.get("original_price"),
                "final_price": offer.get("final_price"),
                "products_count": len(offer.get("products", [])),
                "valid_until": offer.get("valid_until")
            })
        
        return {
            "status": "success",
            "total": len(banner_items),
            "banners": banner_items
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching banner combos: {str(e)}")


@router.post("/ai/generate")
async def ai_generate_combo(
    category: Optional[str] = None,
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None,
    num_products: int = 3,
    discount_percent: float = 15,
    db = Depends(get_db)
):
    """AI-powered combo generation based on product analysis"""
    try:
        # Build product filter
        product_filter = {"is_active": {"$ne": False}}
        if category:
            product_filter["category"] = {"$regex": category, "$options": "i"}
        
        # Get available products
        product_filter.setdefault("is_listed", {"$ne": False})
        products = await db.products.find(product_filter, {"_id": 0}).to_list(500)
        
        if len(products) < num_products:
            raise HTTPException(status_code=400, detail=f"Not enough products available. Found {len(products)}, need {num_products}")
        
        # AI Logic: Select complementary products
        # Strategy 1: Same brand, different categories (complete kitchen solution)
        # Strategy 2: Same category, different brands (comparison bundle)
        # Strategy 3: Budget-optimized bundle
        
        selected_products = []
        total_price = 0
        
        # Group products by brand and category
        by_brand = {}
        for p in products:
            brand = p.get("brand", "Other")
            if brand not in by_brand:
                by_brand[brand] = []
            by_brand[brand].append(p)
        
        # Strategy 1: Try to get products from the same brand but different categories
        for brand, brand_products in by_brand.items():
            if len(brand_products) >= num_products:
                # Get unique categories from this brand
                categories = {}
                for p in brand_products:
                    cat = p.get("category", "Other")
                    if cat not in categories:
                        categories[cat] = p
                
                if len(categories) >= num_products:
                    selected_products = list(categories.values())[:num_products]
                    break
        
        # If Strategy 1 didn't work, just pick top products by price within budget
        if not selected_products:
            sorted_products = sorted(products, key=lambda x: x.get("price", 0), reverse=True)
            
            if budget_max:
                sorted_products = [p for p in sorted_products if p.get("price", 0) <= budget_max / num_products * 1.5]
            if budget_min:
                sorted_products = [p for p in sorted_products if p.get("price", 0) >= budget_min / num_products * 0.5]
            
            selected_products = sorted_products[:num_products]
        
        if len(selected_products) < num_products:
            # Fallback: just take any products
            selected_products = products[:num_products]
        
        # Calculate prices
        for p in selected_products:
            total_price += p.get("price", 0)
        
        final_price = total_price * (1 - discount_percent / 100)
        savings = total_price - final_price
        
        # Generate smart combo name
        brands = list(set(p.get("brand", "") for p in selected_products if p.get("brand")))
        categories = list(set(p.get("category", "") for p in selected_products if p.get("category")))
        
        if len(brands) == 1:
            combo_name = f"{brands[0]} Complete Kitchen Bundle"
        elif len(categories) == 1:
            combo_name = f"Premium {categories[0]} Collection"
        else:
            combo_name = f"Smart Home Appliance Bundle"
        
        # Generate description
        product_names = [p.get("name", "")[:30] for p in selected_products]
        description = f"Get {', '.join(product_names[:2])} and more at {discount_percent}% off!"
        
        # Create the combo offer
        valid_from = datetime.now(timezone.utc).isoformat()
        valid_until = (datetime.now(timezone.utc).replace(month=datetime.now().month + 1 if datetime.now().month < 12 else 1)).isoformat()
        
        combo_suggestion = {
            "name": combo_name,
            "description": description,
            "product_ids": [p.get("id") for p in selected_products],
            "products": selected_products,
            "discount_type": "percentage",
            "discount_value": discount_percent,
            "original_price": total_price,
            "final_price": final_price,
            "savings": savings,
            "valid_from": valid_from,
            "valid_until": valid_until,
            "ai_generated": True,
            "generation_params": {
                "category": category,
                "budget_min": budget_min,
                "budget_max": budget_max,
                "num_products": num_products,
                "discount_percent": discount_percent
            },
            # Suggested banner settings
            "suggested_banner_title": f"Save ₹{savings:,.0f} on {combo_name}",
            "suggested_banner_subtitle": f"{discount_percent}% off when you buy together",
            "suggested_banner_gradient": "from-purple-600 to-pink-600"
        }
        
        return {
            "status": "success",
            "message": "AI-generated combo suggestion ready",
            "suggestion": combo_suggestion,
            "actions": {
                "create": "POST /api/combo-offers/ with the suggestion data",
                "modify": "Adjust the suggestion and then create"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating AI combo: {str(e)}")


@router.post("/ai/create")
async def ai_create_combo(
    category: Optional[str] = None,
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None,
    num_products: int = 3,
    discount_percent: float = 15,
    show_on_banner: bool = True,
    db = Depends(get_db)
):
    """AI-powered combo creation - generates and saves in one step"""
    try:
        # First generate the suggestion
        product_filter = {"is_active": {"$ne": False}}
        if category:
            product_filter["category"] = {"$regex": category, "$options": "i"}
        
        product_filter.setdefault("is_listed", {"$ne": False})
        products = await db.products.find(product_filter, {"_id": 0}).to_list(500)
        
        if len(products) < num_products:
            raise HTTPException(status_code=400, detail=f"Not enough products. Found {len(products)}, need {num_products}")
        
        # Select products (same logic as generate)
        selected_products = []
        by_brand = {}
        for p in products:
            brand = p.get("brand", "Other")
            if brand not in by_brand:
                by_brand[brand] = []
            by_brand[brand].append(p)
        
        for brand, brand_products in by_brand.items():
            if len(brand_products) >= num_products:
                categories = {}
                for p in brand_products:
                    cat = p.get("category", "Other")
                    if cat not in categories:
                        categories[cat] = p
                if len(categories) >= num_products:
                    selected_products = list(categories.values())[:num_products]
                    break
        
        if not selected_products:
            sorted_products = sorted(products, key=lambda x: x.get("price", 0), reverse=True)
            if budget_max:
                sorted_products = [p for p in sorted_products if p.get("price", 0) <= budget_max / num_products * 1.5]
            selected_products = sorted_products[:num_products]
        
        if len(selected_products) < num_products:
            selected_products = products[:num_products]
        
        # Calculate
        total_price = sum(p.get("price", 0) for p in selected_products)
        final_price = total_price * (1 - discount_percent / 100)
        savings = total_price - final_price
        
        brands = list(set(p.get("brand", "") for p in selected_products if p.get("brand")))
        if len(brands) == 1:
            combo_name = f"{brands[0]} Complete Kitchen Bundle"
        else:
            combo_name = f"Smart Home Appliance Bundle"
        
        # Create and save
        combo_doc = {
            "id": str(uuid.uuid4()),
            "name": combo_name,
            "description": f"AI-curated bundle with {discount_percent}% savings",
            "product_ids": [p.get("id") for p in selected_products],
            "products": selected_products,
            "discount_type": "percentage",
            "discount_value": discount_percent,
            "original_price": total_price,
            "final_price": final_price,
            "savings": savings,
            "valid_from": datetime.now(timezone.utc).isoformat(),
            "valid_until": (datetime.now(timezone.utc).replace(year=datetime.now().year + 1)).isoformat(),
            "is_active": True,
            "min_quantity": 1,
            "banner_image": selected_products[0].get("images", [None])[0] if selected_products else None,
            "show_on_banner": show_on_banner,
            "banner_title": f"Save ₹{savings:,.0f}!",
            "banner_subtitle": f"{combo_name} - {discount_percent}% Off",
            "banner_cta_text": "Shop Bundle",
            "banner_gradient": "from-purple-600 to-pink-600",
            "banner_priority": 10,
            "ai_generated": True,
            "orders_count": 0,
            "revenue_generated": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.combo_offers.insert_one(combo_doc)
        combo_doc.pop("_id", None)
        
        return {
            "status": "success",
            "message": "AI combo offer created and added to banner!",
            "combo": combo_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating AI combo: {str(e)}")



@router.get("/detail/{combo_id}")
async def get_combo_by_id(combo_id: str, db = Depends(get_db)):
    """Get a single combo offer by ID"""
    try:
        combo = await db.combo_offers.find_one({"id": combo_id}, {"_id": 0})
        if combo:
            combo = await _live_pricing(db, combo)
        
        if not combo:
            raise HTTPException(status_code=404, detail="Combo offer not found")
        
        return {
            "status": "success",
            "combo": combo
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching combo: {str(e)}")



# ---- Combo price edit (admin only) ----
from admin_data_management_routes import verify_admin

class ComboPricingUpdate(BaseModel):
    final_price: float
    original_price: Optional[float] = None

@router.put("/{offer_id}/pricing")
async def update_combo_pricing(offer_id: str, body: ComboPricingUpdate, db=Depends(get_db), admin=Depends(verify_admin)):
    offer = await db.combo_offers.find_one({"id": offer_id}, {"_id": 0, "original_price": 1, "name": 1})
    if not offer:
        raise HTTPException(status_code=404, detail="Combo offer not found")
    original = body.original_price or offer.get("original_price") or 0
    final = body.final_price
    if final <= 0 or original <= 0 or final > original:
        raise HTTPException(status_code=400, detail="Combo price must be above 0 and not higher than the original price")
    savings = original - final
    pct = round(savings / original * 100, 1)
    await db.combo_offers.update_one({"id": offer_id}, {"$set": {
        "original_price": original, "final_price": final, "savings": savings,
        "discount_type": "fixed", "discount_value": savings,
        "banner_title": f"Save ₹{savings:,.0f}!",
        "banner_subtitle": f"{offer.get('name', '')} - {pct}% Off",
        "updated_at": datetime.now(timezone.utc).isoformat()}})
    return {"status": "success", "final_price": final, "original_price": original, "savings": savings}


# ---- Admin banner / active / permanent delete ----
class _BannerBody(BaseModel):
    show_on_banner: bool

class _ActiveBody(BaseModel):
    is_active: bool

@router.put("/{offer_id}/banner")
async def set_combo_banner(offer_id: str, body: _BannerBody, db=Depends(get_db), admin=Depends(verify_admin)):
    res = await db.combo_offers.update_one({"id": offer_id}, {"$set": {"show_on_banner": body.show_on_banner, "updated_at": datetime.now(timezone.utc).isoformat()}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Combo offer not found")
    return {"status": "success", "show_on_banner": body.show_on_banner}

@router.put("/{offer_id}/active")
async def set_combo_active(offer_id: str, body: _ActiveBody, db=Depends(get_db), admin=Depends(verify_admin)):
    res = await db.combo_offers.update_one({"id": offer_id}, {"$set": {"is_active": body.is_active, "updated_at": datetime.now(timezone.utc).isoformat()}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Combo offer not found")
    return {"status": "success", "is_active": body.is_active}

@router.delete("/{offer_id}/permanent")
async def delete_combo_permanently(offer_id: str, db=Depends(get_db), admin=Depends(verify_admin)):
    res = await db.combo_offers.delete_one({"id": offer_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Combo offer not found")
    return {"status": "success"}



# ---- Live pricing: original price and savings follow current product prices ----
async def _live_pricing(db, offer):
    ids = offer.get("product_ids") or [x.get("id") for x in offer.get("products", [])]
    products = []
    for pid in ids:
        prod = await db.products.find_one({"id": pid}, {"_id": 0})
        if prod:
            products.append(prod)
    if not products:
        return offer
    original = sum((x.get("price") or 0) for x in products)
    final = offer.get("final_price") or 0
    offer["products"] = products
    offer["original_price"] = original
    offer["savings"] = original - final
    return offer
