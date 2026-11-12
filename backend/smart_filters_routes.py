"""
AI-Powered Smart Filters for Category Pages
Uses Gemini 2.0 Flash to analyze products and generate dynamic filters
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from json import JSONDecodeError, loads as json_loads, dumps as json_dumps
import os
import asyncio
from database import get_db
from emergentintegrations.llm.chat import LlmChat, UserMessage

router = APIRouter(prefix="/smart-filters", tags=["Smart Filters"])

# Cache smart filters in memory to avoid repeated AI calls
_smart_filters_cache = {}

# Initialize Gemini client
def get_gemini_client():
    try:
        api_key = os.environ.get("EMERGENT_LLM_KEY") or os.environ.get("EMERGENT_API_KEY")
        if not api_key:
            return None
        
        client = LlmChat(
            api_key=api_key,
            session_id="smart-filters",
            system_message="You are an AI assistant that analyzes product data and generates smart filter categories. Always respond with valid JSON only."
        )
        return client.with_model("gemini", "gemini-2.5-flash")
    except Exception as e:
        print(f"Warning: Could not initialize Gemini client: {e}")
        return None

class SmartFiltersResponse(BaseModel):
    status: str
    category: str
    total_products: int
    smart_filters: List[Dict[str, Any]]

@router.get("/{category_name}")
async def get_smart_filters(category_name: str, db = Depends(get_db)):
    """
    Generate AI-powered smart filters for a specific category.
    Uses in-memory cache. Runs AI call in a thread pool to prevent blocking.
    """
    # Check cache first
    if category_name in _smart_filters_cache:
        return _smart_filters_cache[category_name]

    # Check persistent cache (survives restarts)
    db_cached = await db.smart_filters_cache.find_one({"category": category_name}, {"_id": 0})
    if db_cached and db_cached.get("result"):
        _smart_filters_cache[category_name] = db_cached["result"]
        return db_cached["result"]

    empty_result = {"status": "success", "category": category_name, "total_products": 0, "smart_filters": []}
    
    try:
        client = get_gemini_client()
        if not client:
            return empty_result
        
        # Use wait_for with a strict timeout
        # Run in thread pool to prevent blocking the event loop
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            _generate_smart_filters(client, category_name, db),
            timeout=15.0
        )
        _smart_filters_cache[category_name] = result
        if result.get("smart_filters"):
            await db.smart_filters_cache.update_one(
                {"category": category_name},
                {"$set": {"category": category_name, "result": result}},
                upsert=True
            )
        return result
        
    except (asyncio.TimeoutError, asyncio.CancelledError, Exception):
        return empty_result


async def _generate_smart_filters(client, category_name: str, db):
    """Internal function to generate smart filters with AI. Has internal timeout."""
    # Fetch products in this category
    products = await db.products.find(
        {"category": {"$regex": category_name.replace('-', ' '), "$options": "i"}, "is_listed": {"$ne": False}},
        {"_id": 0, "name": 1, "brand": 1, "specifications": 1, "features": 1, "price": 1}
    ).to_list(length=500)
    
    if not products:
        return {
            "status": "success",
            "category": category_name,
            "total_products": 0,
            "smart_filters": []
        }
    
    # Prepare product data for AI analysis
    product_summary = []
    for p in products[:50]:
        product_info = {
            "name": p.get("name", ""),
            "brand": p.get("brand", ""),
            "price": p.get("price", 0),
        }
        product_summary.append(product_info)
    
    prompt = f"""Analyze these {len(product_summary)} products in the "{category_name}" category.

Products: {str(product_summary)[:3000]}

Generate 2-3 smart filters. Return ONLY a JSON array:
[{{"filter_name": "Type", "filter_options": ["Option 1", "Option 2"]}}]
No markdown, no explanations. JSON only.
"""
    
    user_message = UserMessage(text=prompt)
    response = await client.send_message(user_message)
    
    ai_response = response.strip()
    if ai_response.startswith("```json"):
        ai_response = ai_response.replace("```json", "").replace("```", "").strip()
    elif ai_response.startswith("```"):
        ai_response = ai_response.replace("```", "").strip()
    
    smart_filters = json_loads(ai_response)
    
    return {
        "status": "success",
        "category": category_name,
        "total_products": len(products),
        "smart_filters": smart_filters
    }

@router.post("/{category_name}/filter-products")
async def filter_products_by_smart_filters(
    category_name: str,
    filter_criteria: Dict[str, List[str]],
    db = Depends(get_db)
):
    """
    Filter products based on AI-generated smart filter selections
    """
    try:
        # Base query for category
        query = {"category": {"$regex": category_name.replace('-', ' '), "$options": "i"}}
        
        # Fetch all products in category
        query.setdefault("is_listed", {"$ne": False})
        products = await db.products.find(query, {"_id": 0}).to_list(length=500)
        
        # Apply smart filters
        filtered_products = []
        for product in products:
            matches_all_filters = True
            
            for filter_name, selected_options in filter_criteria.items():
                if not selected_options:  # Skip if no options selected for this filter
                    continue
                
                # Check if product matches any of the selected options
                product_matches_filter = False
                
                # Search in product name, specifications, and features
                search_text = f"{product.get('name', '')} "
                
                if product.get('specifications'):
                    for spec in product['specifications']:
                        search_text += f"{spec.get('name', '')} {spec.get('value', '')} "
                
                if product.get('features'):
                    search_text += " ".join(product.get('features', []))
                
                search_text = search_text.lower()
                
                # Check if any selected option appears in search text
                for option in selected_options:
                    if option.lower() in search_text:
                        product_matches_filter = True
                        break
                
                if not product_matches_filter:
                    matches_all_filters = False
                    break
            
            if matches_all_filters:
                filtered_products.append(product)
        
        return {
            "status": "success",
            "category": category_name,
            "total_filtered": len(filtered_products),
            "products": filtered_products
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error filtering products: {str(e)}")
