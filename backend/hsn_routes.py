from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from database import get_db
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hsn", tags=["HSN Codes"])

class HSNCode(BaseModel):
    code: str
    description: str
    gst_rate: float
    category: Optional[str] = None
    is_active: bool = True

class HSNCodeResponse(BaseModel):
    id: str
    code: str
    description: str
    gst_rate: float
    category: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: str

@router.post("/", response_model=HSNCodeResponse)
async def create_hsn_code(hsn: HSNCode, db = Depends(get_db)):
    """Create a new HSN code"""
    try:
        # Validate HSN code length (minimum 6 digits)
        clean_code = hsn.code.strip()
        if len(clean_code) < 6:
            raise HTTPException(status_code=400, detail="HSN code must be at least 6 digits")
        if not clean_code.isdigit():
            raise HTTPException(status_code=400, detail="HSN code must contain only numbers")
        
        # Check if HSN code already exists
        existing = await db.hsn_codes.find_one({"code": clean_code})
        if existing:
            raise HTTPException(status_code=400, detail="HSN code already exists")
        
        hsn_data = {
            "id": str(uuid.uuid4()),
            "code": clean_code,
            "description": hsn.description,
            "gst_rate": hsn.gst_rate,
            "category": hsn.category,
            "is_active": hsn.is_active,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.hsn_codes.insert_one(hsn_data)
        
        return HSNCodeResponse(**hsn_data)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create HSN code: {str(e)}")

@router.get("/", response_model=List[HSNCodeResponse])
async def get_all_hsn_codes(
    active_only: bool = False,
    search: Optional[str] = None,
    db = Depends(get_db)
):
    """Get all HSN codes"""
    try:
        query = {}
        if active_only:
            query["is_active"] = True
        if search:
            query["$or"] = [
                {"code": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        hsn_codes = await db.hsn_codes.find(query, {"_id": 0}).to_list(None)
        return [HSNCodeResponse(**hsn) for hsn in hsn_codes]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch HSN codes: {str(e)}")


# Keywords mapping for intelligent HSN suggestion
HSN_KEYWORD_MAPPING = {
    # Television
    "85287300": ["tv", "television", "led tv", "lcd tv", "smart tv", "oled", "qled", "android tv", "4k tv", "uhd", "hd tv"],
    # Air Conditioners
    "84151010": ["ac", "air conditioner", "split ac", "inverter ac", "air conditioning"],
    "84151090": ["window ac", "portable ac", "cassette ac"],
    # Refrigerators
    "84182100": ["refrigerator", "fridge", "freezer", "double door", "single door", "side by side", "convertible refrigerator"],
    # Washing Machines
    "84501110": ["washing machine", "top load", "washer", "fully automatic washing"],
    "84501190": ["front load", "front load washing", "combo washer dryer"],
    # Dishwashers
    "84221100": ["dishwasher", "dish washer", "dish washing machine"],
    # Vacuum Cleaners
    "85081100": ["vacuum", "vacuum cleaner", "robotic vacuum", "robot vacuum", "handheld vacuum", "cordless vacuum", "wet dry vacuum"],
    # Water Heaters
    "85161000": ["water heater", "geyser", "instant heater", "storage heater"],
    # Microwave
    "85165000": ["microwave", "microwave oven", "otg", "oven toaster", "convection microwave"],
    # Cooking Appliances
    "85166000": ["oven", "cooker", "electric oven", "cooking range", "induction"],
    "85166010": ["induction cooktop", "induction stove", "induction plate"],
    # Kitchen Chimneys
    "84146000": ["chimney", "kitchen hood", "cooker hood", "range hood", "exhaust hood"],
    # Mixers/Grinders
    "85094000": ["mixer", "grinder", "juicer", "blender", "food processor", "hand blender", "wet grinder"],
    # Iron
    "85164000": ["iron", "steam iron", "dry iron", "press", "clothes iron"],
    # Fans
    "84145100": ["fan", "ceiling fan", "table fan", "wall fan", "pedestal fan", "tower fan", "exhaust fan"],
    # Water Purifiers
    "84212110": ["water purifier", "ro purifier", "uv purifier", "water filter"],
    # Air Purifiers
    "84213920": ["air purifier", "air filter", "hepa filter"],
    # Personal Care
    "85163100": ["hair dryer", "blow dryer", "hair blower"],
    "85101000": ["shaver", "trimmer", "electric shaver", "beard trimmer", "grooming"],
    # Kitchen Appliances
    "85167100": ["kettle", "electric kettle", "coffee maker", "tea maker", "espresso"],
    "85167200": ["toaster", "sandwich maker", "grill"],
    # Gas Appliances
    "73211100": ["gas stove", "gas hob", "burner", "cooktop", "gas range"],
    # Power Tools
    "84672100": ["drill", "drill machine", "impact drill", "hammer drill", "rotary drill"],
    "84672200": ["saw", "circular saw", "jigsaw", "angle grinder", "grinder"],
    "84672900": ["sander", "polisher", "router", "planer", "screwdriver machine"],
    # Room Heaters
    "85162900": ["room heater", "space heater", "oil heater", "blower heater", "convector"],
    # Cleaning Supplies
    "34022090": ["detergent", "washing liquid", "fabric softener", "cleaning solution"],
    # Laptops
    "84713010": ["laptop", "notebook", "chromebook", "macbook", "ultrabook"],
    # Paintings/Art
    "97019099": ["painting", "canvas", "art", "artwork", "wall art", "mural"],
    # Hand Tools
    "82042000": ["wrench", "socket set", "spanner", "ratchet"],
    "82032000": ["plier", "cutter", "nipper", "wire cutter"],
    # Drill Bits
    "82075000": ["drill bit", "masonry bit", "wood bit", "metal bit", "hole saw"],
    # Appliance Parts
    "85099000": ["spare part", "appliance part", "motor", "blade", "jar"],
    "85169000": ["heating element", "coil", "thermostat"],
}


@router.get("/suggest")
async def suggest_hsn_code(product_name: str, db = Depends(get_db)):
    """
    Intelligently suggest HSN code based on product name.
    Returns matching HSN codes ranked by relevance.
    """
    import re
    
    try:
        product_lower = product_name.lower()
        suggestions = []
        matched_codes = set()
        
        # First pass: Word boundary keyword matching (more precise)
        for hsn_code, keywords in HSN_KEYWORD_MAPPING.items():
            for keyword in keywords:
                # Use word boundary regex for better matching
                # This prevents "ac" from matching "vacuum"
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, product_lower):
                    if hsn_code not in matched_codes:
                        # Fetch full HSN data from database
                        hsn_data = await db.hsn_codes.find_one({"code": hsn_code}, {"_id": 0})
                        if hsn_data:
                            # Calculate relevance score based on keyword length match
                            score = len(keyword) / len(product_lower) * 100
                            suggestions.append({
                                **hsn_data,
                                "match_score": round(score, 2),
                                "matched_keyword": keyword
                            })
                            matched_codes.add(hsn_code)
                    break
        
        # Second pass: Partial word matching for longer keywords (at least 4 chars)
        if not suggestions:
            for hsn_code, keywords in HSN_KEYWORD_MAPPING.items():
                for keyword in keywords:
                    if len(keyword) >= 4 and keyword in product_lower:
                        if hsn_code not in matched_codes:
                            hsn_data = await db.hsn_codes.find_one({"code": hsn_code}, {"_id": 0})
                            if hsn_data:
                                score = len(keyword) / len(product_lower) * 100
                                suggestions.append({
                                    **hsn_data,
                                    "match_score": round(score, 2),
                                    "matched_keyword": keyword
                                })
                                matched_codes.add(hsn_code)
                        break
        
        # If still no matches, try database search
        if not suggestions:
            # Search by description in database
            db_results = await db.hsn_codes.find(
                {
                    "$or": [
                        {"description": {"$regex": product_name, "$options": "i"}},
                        {"category": {"$regex": product_name, "$options": "i"}}
                    ],
                    "is_active": True
                },
                {"_id": 0}
            ).limit(5).to_list(5)
            
            for result in db_results:
                suggestions.append({
                    **result,
                    "match_score": 50.0,
                    "matched_keyword": "database search"
                })
        
        # Sort by match score (higher is better)
        suggestions.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        return {
            "product_name": product_name,
            "suggestions": suggestions[:5],  # Top 5 suggestions
            "total_matches": len(suggestions)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to suggest HSN code: {str(e)}")


@router.get("/categories")
async def get_hsn_categories(db = Depends(get_db)):
    """Get all unique HSN categories"""
    try:
        categories = await db.hsn_codes.distinct("category", {"is_active": True})
        categories = [c for c in categories if c]  # Filter out None/empty
        return {"categories": sorted(categories)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch categories: {str(e)}")


@router.get("/by-category/{category}")
async def get_hsn_by_category(category: str, db = Depends(get_db)):
    """Get all HSN codes for a specific category"""
    try:
        hsn_codes = await db.hsn_codes.find(
            {"category": category, "is_active": True},
            {"_id": 0}
        ).to_list(None)
        return hsn_codes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch HSN codes: {str(e)}")


@router.get("/{hsn_id}", response_model=HSNCodeResponse)
async def get_hsn_code(hsn_id: str, db = Depends(get_db)):
    """Get a specific HSN code"""
    try:
        hsn = await db.hsn_codes.find_one({"id": hsn_id}, {"_id": 0})
        if not hsn:
            raise HTTPException(status_code=404, detail="HSN code not found")
        
        return HSNCodeResponse(**hsn)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch HSN code: {str(e)}")

@router.put("/{hsn_id}", response_model=HSNCodeResponse)
async def update_hsn_code(hsn_id: str, hsn: HSNCode, db = Depends(get_db)):
    """Update an HSN code"""
    try:
        existing = await db.hsn_codes.find_one({"id": hsn_id})
        if not existing:
            raise HTTPException(status_code=404, detail="HSN code not found")
        
        # Check if new code conflicts with another HSN
        if hsn.code != existing["code"]:
            conflict = await db.hsn_codes.find_one({"code": hsn.code, "id": {"$ne": hsn_id}})
            if conflict:
                raise HTTPException(status_code=400, detail="HSN code already exists")
        
        update_data = {
            **hsn.dict(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.hsn_codes.update_one(
            {"id": hsn_id},
            {"$set": update_data}
        )
        
        updated_hsn = await db.hsn_codes.find_one({"id": hsn_id}, {"_id": 0})
        return HSNCodeResponse(**updated_hsn)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update HSN code: {str(e)}")

@router.delete("/{hsn_id}")
async def delete_hsn_code(hsn_id: str, db = Depends(get_db)):
    """Delete an HSN code (soft delete)"""
    try:
        result = await db.hsn_codes.update_one(
            {"id": hsn_id},
            {"$set": {
                "is_active": False,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="HSN code not found")
        
        return {"status": "success", "message": "HSN code deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete HSN code: {str(e)}")

@router.post("/bulk-assign-to-products")
async def bulk_assign_hsn_to_products(
    dry_run: bool = True,
    db = Depends(get_db)
):
    """
    Automatically assign HSN codes to products based on their names.
    Uses the HSN_KEYWORD_MAPPING to find matching products.
    Set dry_run=False to actually update the products.
    """
    import re
    
    try:
        # Get all products without HSN codes
        products = await db.products.find(
            {"$or": [
                {"hsn_code": {"$exists": False}},
                {"hsn_code": None},
                {"hsn_code": ""}
            ]},
            {"_id": 0, "id": 1, "name": 1, "model_number": 1, "category": 1}
        ).to_list(None)
        
        logger.info(f"Found {len(products)} products without HSN codes")
        
        assignments = []
        unmatched = []
        
        for product in products:
            product_text = f"{product.get('name', '')} {product.get('category', '')}".lower()
            matched_hsn = None
            matched_keyword = None
            best_score = 0
            
            # Try to match using keyword mapping
            for hsn_code, keywords in HSN_KEYWORD_MAPPING.items():
                for keyword in keywords:
                    # Use word boundary for better matching
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    if re.search(pattern, product_text):
                        score = len(keyword)
                        if score > best_score:
                            best_score = score
                            matched_hsn = hsn_code
                            matched_keyword = keyword
            
            if matched_hsn:
                # Get full HSN data
                hsn_data = await db.hsn_codes.find_one({"code": matched_hsn}, {"_id": 0})
                assignments.append({
                    "product_id": product["id"],
                    "product_name": product.get("name", "")[:50],
                    "model_number": product.get("model_number", ""),
                    "hsn_code": matched_hsn,
                    "hsn_description": hsn_data.get("description", "") if hsn_data else "",
                    "matched_keyword": matched_keyword,
                    "gst_rate": hsn_data.get("gst_rate", 18.0) if hsn_data else 18.0
                })
            else:
                unmatched.append({
                    "product_id": product["id"],
                    "product_name": product.get("name", "")[:50],
                    "model_number": product.get("model_number", ""),
                    "category": product.get("category", "")
                })
        
        # Actually update products if not dry run
        updated_count = 0
        if not dry_run and assignments:
            for assignment in assignments:
                result = await db.products.update_one(
                    {"id": assignment["product_id"]},
                    {"$set": {
                        "hsn_code": assignment["hsn_code"],
                        "tax_rate": assignment["gst_rate"],
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                if result.modified_count > 0:
                    updated_count += 1
        
        return {
            "status": "success",
            "dry_run": dry_run,
            "total_products_without_hsn": len(products),
            "matched": len(assignments),
            "unmatched": len(unmatched),
            "updated": updated_count if not dry_run else 0,
            "assignments": assignments[:50],  # Limit for response size
            "unmatched_products": unmatched[:20],  # Sample of unmatched
            "message": f"{'Would update' if dry_run else 'Updated'} {len(assignments)} products with HSN codes. {len(unmatched)} products could not be auto-matched."
        }
        
    except Exception as e:
        logger.error(f"Error in bulk HSN assignment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to assign HSN codes: {str(e)}")


@router.post("/bulk-upload")
async def bulk_upload_hsn_codes(hsn_codes: List[HSNCode], db = Depends(get_db)):
    """Bulk upload HSN codes"""
    try:
        created_count = 0
        skipped_count = 0
        invalid_count = 0
        
        for hsn in hsn_codes:
            # Validate HSN code (min 6 digits, numbers only)
            clean_code = str(hsn.code).strip()
            if len(clean_code) < 6 or not clean_code.isdigit():
                invalid_count += 1
                continue
            
            # Check if already exists
            existing = await db.hsn_codes.find_one({"code": clean_code})
            if existing:
                skipped_count += 1
                continue
            
            hsn_data = {
                "id": str(uuid.uuid4()),
                "code": clean_code,
                "description": hsn.description,
                "gst_rate": hsn.gst_rate,
                "category": hsn.category,
                "is_active": hsn.is_active,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.hsn_codes.insert_one(hsn_data)
            created_count += 1
        
        return {
            "status": "success",
            "created": created_count,
            "skipped": skipped_count,
            "invalid": invalid_count,
            "message": f"Created {created_count} HSN codes, skipped {skipped_count} duplicates, {invalid_count} invalid"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to bulk upload: {str(e)}")
