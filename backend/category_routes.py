"""
Product Category and Sub-Category Management
"""
from fastapi import APIRouter, HTTPException, Depends
import re
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
from database import get_db

router = APIRouter(prefix="/categories", tags=["Categories"])

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    display_order: Optional[int] = 0
    is_active: Optional[bool] = True

class SubCategoryCreate(BaseModel):
    category_id: str
    name: str
    description: Optional[str] = None
    display_order: Optional[int] = 0
    is_active: Optional[bool] = True

@router.post("/")
async def create_category(category: CategoryCreate, db = Depends(get_db)):
    """Create a new product category"""
    try:
        # Check if category already exists
        existing = await db.categories.find_one({"name": category.name})
        if existing:
            raise HTTPException(status_code=400, detail="Category already exists")
        
        category_doc = {
            "id": str(uuid.uuid4()),
            "name": category.name,
            "description": category.description,
            "icon": category.icon,
            "display_order": category.display_order,
            "is_active": category.is_active,
            "sub_categories": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.categories.insert_one(category_doc)
        category_doc.pop("_id", None)
        
        return {
            "status": "success",
            "message": "Category created successfully",
            "category": category_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating category: {str(e)}")

@router.get("/")
async def get_categories(db = Depends(get_db)):
    """Get all categories with sub-categories"""
    try:
        categories = await db.categories.find(
            {"is_active": True},
            {"_id": 0}
        ).sort([("display_order", 1)]).to_list(100)
        
        return {
            "status": "success",
            "total": len(categories),
            "categories": categories
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")

@router.post("/sub-category")
async def create_sub_category(sub_category: SubCategoryCreate, db = Depends(get_db)):
    """Create a sub-category under a category"""
    try:
        # Check if parent category exists
        category = await db.categories.find_one({"id": sub_category.category_id})
        if not category:
            raise HTTPException(status_code=404, detail="Parent category not found")
        
        sub_cat_doc = {
            "id": str(uuid.uuid4()),
            "name": sub_category.name,
            "description": sub_category.description,
            "display_order": sub_category.display_order,
            "is_active": sub_category.is_active,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Add sub-category to parent category
        await db.categories.update_one(
            {"id": sub_category.category_id},
            {
                "$push": {"sub_categories": sub_cat_doc},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        return {
            "status": "success",
            "message": "Sub-category created successfully",
            "sub_category": sub_cat_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating sub-category: {str(e)}")

@router.put("/{category_id}")
async def update_category(category_id: str, updates: dict, db = Depends(get_db)):
    """Update category details"""
    try:
        category = await db.categories.find_one({"id": category_id})
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await db.categories.update_one(
            {"id": category_id},
            {"$set": updates}
        )
        
        updated_category = await db.categories.find_one({"id": category_id}, {"_id": 0})
        
        return {
            "status": "success",
            "message": "Category updated successfully",
            "category": updated_category
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating category: {str(e)}")

@router.post("/populate-from-products")
async def populate_categories_from_products(db = Depends(get_db)):
    """Auto-populate categories from existing product data"""
    try:
        # Get all unique categories and sub-categories from products
        products = await db.products.find({}, {"_id": 0, "category": 1, "sub_category": 1}).to_list(1000)
        
        category_map = {}
        for product in products:
            cat_name = product.get('category')
            sub_cat_name = product.get('sub_category')
            
            if cat_name:
                if cat_name not in category_map:
                    category_map[cat_name] = set()
                if sub_cat_name:
                    category_map[cat_name].add(sub_cat_name)
        
        # Create categories if they don't exist
        created_count = 0
        for idx, (cat_name, sub_cats) in enumerate(category_map.items()):
            existing = await db.categories.find_one({"name": cat_name})
            
            if not existing:
                # Create sub-category documents
                sub_cat_docs = []
                for sub_idx, sub_name in enumerate(sorted(sub_cats)):
                    sub_cat_docs.append({
                        "id": str(uuid.uuid4()),
                        "name": sub_name,
                        "description": f"{sub_name} products",
                        "display_order": sub_idx,
                        "is_active": True,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    })
                
                category_doc = {
                    "id": str(uuid.uuid4()),
                    "name": cat_name,
                    "description": f"{cat_name} products",
                    "icon": "",
                    "display_order": idx,
                    "is_active": True,
                    "sub_categories": sub_cat_docs,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                
                await db.categories.insert_one(category_doc)
                created_count += 1
        
        return {
            "status": "success",
            "message": f"Created {created_count} categories from product data",
            "created_count": created_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error populating categories: {str(e)}")

@router.put("/product/{product_id}/move")
async def move_product_to_category(
    product_id: str,
    category: str,
    sub_category: Optional[str] = None,
    db = Depends(get_db)
):
    """Move a product to a different category"""
    try:
        product = await db.products.find_one({"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        from product_normalize import clean_category
        update_data = {
            "category": clean_category(category),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if sub_category:
            update_data["sub_category"] = sub_category
        
        await db.products.update_one(
            {"id": product_id},
            {"$set": update_data}
        )
        
        updated_product = await db.products.find_one({"id": product_id}, {"_id": 0})
        
        return {
            "status": "success",
            "message": "Product moved successfully",
            "product": updated_product
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error moving product: {str(e)}")

@router.get("/all")
async def get_all_categories(db = Depends(get_db)):
    """Get ALL categories (including inactive) for admin"""
    try:
        categories = await db.categories.find(
            {},
            {"_id": 0}
        ).sort([("display_order", 1)]).to_list(100)
        
        return {
            "status": "success",
            "total": len(categories),
            "categories": categories
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")

@router.put("/products/bulk-move")
async def bulk_move_products(
    product_ids: List[str],
    category: str,
    sub_category: Optional[str] = None,
    db = Depends(get_db)
):
    """Move multiple products to a different category"""
    try:
        if not product_ids:
            raise HTTPException(status_code=400, detail="No product IDs provided")
        
        # Verify all products exist
        products = await db.products.find({"id": {"$in": product_ids}}).to_list(length=None)
        if len(products) != len(product_ids):
            raise HTTPException(status_code=404, detail="Some products not found")
        
        from product_normalize import clean_category
        update_data = {
            "category": clean_category(category),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if sub_category:
            update_data["sub_category"] = sub_category
        
        # Bulk update
        result = await db.products.update_many(
            {"id": {"$in": product_ids}},
            {"$set": update_data}
        )
        
        return {
            "status": "success",
            "message": f"Moved {result.modified_count} products successfully",
            "modified_count": result.modified_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error bulk moving products: {str(e)}")

@router.get("/{category_name}/products")
async def get_products_by_category(category_name: str, db = Depends(get_db)):
    """Get all listed products in a specific category"""
    try:
        # Normalize: collapse any run of hyphens/whitespace into a single space
        normalized_name = re.sub(r'[-\s]+', ' ', category_name).strip()
        
        # Build a flexible regex: allow hyphens OR spaces (any amount) between words
        escaped = re.escape(normalized_name)
        pattern = escaped.replace(r'\ ', r'[\s-]+')
        
        # Find listed products matching the category (case-insensitive)
        products = await db.products.find({
            "is_listed": {"$ne": False},
            "$or": [
                {"category": {"$regex": f"^{pattern}$", "$options": "i"}},
                {"category": {"$regex": pattern, "$options": "i"}},
            ]
        }, {"_id": 0}).sort("created_at", -1).to_list(5000)
        
        return {
            "status": "success",
            "category": category_name,
            "total": len(products),
            "products": products
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")

@router.get("/products/by-category")
async def get_all_products_grouped_by_category(db = Depends(get_db)):
    """Get all products grouped by category"""
    try:
        products = await db.products.find(
            {},
            {"_id": 0, "id": 1, "name": 1, "brand": 1, "price": 1, "image": 1, "category": 1, "sub_category": 1}
        ).to_list(length=None)
        
        # Group products by category
        grouped = {}
        for product in products:
            category = product.get('category', 'Uncategorized')
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(product)
        
        return {
            "status": "success",
            "total_products": len(products),
            "categories_count": len(grouped),
            "products_by_category": grouped
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching products by category: {str(e)}")

@router.delete("/{category_id}")
async def delete_category(category_id: str, db = Depends(get_db)):
    """Delete a category (soft delete - mark as inactive)"""
    try:
        category = await db.categories.find_one({"id": category_id})
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Soft delete
        await db.categories.update_one(
            {"id": category_id},
            {"$set": {
                "is_active": False,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "status": "success",
            "message": "Category deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting category: {str(e)}")
