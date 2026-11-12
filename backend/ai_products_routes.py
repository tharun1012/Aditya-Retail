from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from database import get_db

router = APIRouter(prefix="/ai-agents", tags=["AI Agents - Products"])

@router.get("/products")
async def get_ai_agent_products(db = Depends(get_db), limit: int = 200):
    """
    Get the product catalog that AI agents have access to.
    This endpoint shows real-time product data that agents use for recommendations.
    """
    try:
        # Fetch products with pagination for better performance
        products = await db.products.find({}, {"_id": 0}).limit(limit).to_list(length=limit)
        
        # Organize products by category and brand
        categories = {}
        brands = {}
        stock_summary = {"in_stock": 0, "low_stock": 0, "out_of_stock": 0}
        
        for product in products:
            # Organize by category
            category = product.get('category', 'Uncategorized')
            if category not in categories:
                categories[category] = []
            categories[category].append({
                "name": product.get('name'),
                "brand": product.get('brand'),
                "price": product.get('price'),
                "stock": product.get('stock'),
                "id": product.get('id')
            })
            
            # Organize by brand
            brand = product.get('brand', 'Unknown')
            if brand not in brands:
                brands[brand] = 0
            brands[brand] += 1
            
            # Stock summary
            stock = product.get('stock', 0)
            if stock == 0:
                stock_summary["out_of_stock"] += 1
            elif stock <= 5:
                stock_summary["low_stock"] += 1
            else:
                stock_summary["in_stock"] += 1
        
        return {
            "status": "success",
            "total_products": len(products),
            "categories": {cat: len(prods) for cat, prods in categories.items()},
            "brands": brands,
            "stock_summary": stock_summary,
            "products_by_category": categories,
            "message": "This is the real-time product catalog that AI agents use for recommendations."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching AI agent products: {str(e)}")

@router.get("/catalog-preview")
async def get_catalog_preview(db = Depends(get_db)):
    """
    Get a preview of the product catalog text that AI agents receive in their system messages.
    This shows exactly what information the AI agents have about products.
    """
    try:
        from ai_agents import AIAgentManager
        
        # Create AI manager instance
        ai_manager = AIAgentManager()
        
        # Fetch catalog
        catalog = await ai_manager._fetch_product_catalog()
        
        # Build catalog summaries for each agent
        sales_summary = ai_manager._build_catalog_summary(catalog)
        service_summary = ai_manager._build_service_catalog_summary(catalog)
        
        return {
            "status": "success",
            "total_products": catalog.get("total_count", 0),
            "sales_agent_catalog": sales_summary,
            "service_agent_catalog": service_summary,
            "stock_summary": catalog.get("stock_summary", {}),
            "message": "This is the catalog information that AI agents receive in their system messages."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating catalog preview: {str(e)}")
