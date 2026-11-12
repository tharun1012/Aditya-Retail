"""
Inventory Management API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from database import get_db
from inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory Management"])

class StockAdjustmentRequest(BaseModel):
    product_id: str
    new_stock_level: int
    reason: str
    adjusted_by: str

class BulkStockInitRequest(BaseModel):
    default_stock: int = 10
    reorder_level: int = 5

@router.post("/initialize-all-products")
async def initialize_all_products(request: BulkStockInitRequest, db = Depends(get_db)):
    """Initialize stock tracking for all products"""
    try:
        inventory_service = InventoryService(db)
        
        # Get all products
        products = await db.products.find({}, {"_id": 0, "id": 1, "name": 1}).to_list(None)
        
        initialized_count = 0
        for product in products:
            # Check if already initialized
            existing = await db.products.find_one(
                {"id": product["id"], "current_stock": {"$exists": True}}
            )
            
            if not existing:
                success = await inventory_service.initialize_product_stock(
                    product["id"],
                    request.default_stock,
                    request.reorder_level
                )
                if success:
                    initialized_count += 1
        
        return {
            "status": "success",
            "message": f"Initialized stock for {initialized_count} products",
            "total_products": len(products),
            "already_initialized": len(products) - initialized_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize products: {str(e)}")

@router.get("/summary")
async def get_inventory_summary(db = Depends(get_db)):
    """Get overall inventory summary"""
    try:
        inventory_service = InventoryService(db)
        summary = await inventory_service.get_stock_summary()
        
        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/low-stock")
async def get_low_stock_products(db = Depends(get_db)):
    """Get products with low stock (at or below reorder level)"""
    try:
        inventory_service = InventoryService(db)
        products = await inventory_service.get_low_stock_products()
        
        return {
            "status": "success",
            "count": len(products),
            "products": products
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/out-of-stock")
async def get_out_of_stock_products(db = Depends(get_db)):
    """Get products that are out of stock"""
    try:
        inventory_service = InventoryService(db)
        products = await inventory_service.get_out_of_stock_products()
        
        return {
            "status": "success",
            "count": len(products),
            "products": products
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_inventory_alerts(db = Depends(get_db)):
    """Get all inventory alerts (low stock + out of stock)"""
    try:
        inventory_service = InventoryService(db)
        
        low_stock = await inventory_service.get_low_stock_products()
        out_of_stock = await inventory_service.get_out_of_stock_products()
        
        return {
            "status": "success",
            "alerts": {
                "low_stock": {
                    "count": len(low_stock),
                    "products": low_stock
                },
                "out_of_stock": {
                    "count": len(out_of_stock),
                    "products": out_of_stock
                }
            },
            "total_alerts": len(low_stock) + len(out_of_stock)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}/history")
async def get_product_stock_history(product_id: str, limit: int = 50, db = Depends(get_db)):
    """Get stock movement history for a specific product"""
    try:
        inventory_service = InventoryService(db)
        history = await inventory_service.get_stock_history(product_id, limit)
        
        return {
            "status": "success",
            "product_id": product_id,
            "count": len(history),
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/adjust")
async def manual_stock_adjustment(request: StockAdjustmentRequest, db = Depends(get_db)):
    """Manually adjust stock level for a product"""
    try:
        inventory_service = InventoryService(db)
        
        result = await inventory_service.manual_stock_adjustment(
            product_id=request.product_id,
            new_stock_level=request.new_stock_level,
            reason=request.reason,
            adjusted_by=request.adjusted_by
        )
        
        if result["success"]:
            return {
                "status": "success",
                "message": result["message"],
                "current_stock": result["current_stock"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_inventory_dashboard(db = Depends(get_db)):
    """Get comprehensive inventory dashboard data"""
    try:
        inventory_service = InventoryService(db)
        summary = await inventory_service.get_stock_summary()
        low_stock_products = await inventory_service.get_low_stock_products()
        out_of_stock_products = await inventory_service.get_out_of_stock_products()
        
        # Get recent stock movements
        pipeline = [
            {"$match": {"stock_history": {"$exists": True}}},
            {"$unwind": "$stock_history"},
            {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$stock_history", {"product_id": "$id", "product_name": "$name"}]}}},
            {"$sort": {"created_at": -1}},
            {"$limit": 10},
            {"$project": {"_id": 0}}
        ]
        recent_movements = await db.products.aggregate(pipeline).to_list(10)
        recent_movements = [{k: v for k, v in m.items() if k != "_id"} for m in recent_movements]
        
        return {
            "status": "success",
            "summary": summary,
            "low_stock_count": len(low_stock_products),
            "low_stock_products": low_stock_products[:5],
            "out_of_stock_count": len(out_of_stock_products),
            "out_of_stock_products": out_of_stock_products[:5],
            "recent_movements": recent_movements
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}/check")
async def check_stock_availability(product_id: str, quantity: int, db = Depends(get_db)):
    """Check if sufficient stock is available for a product"""
    try:
        inventory_service = InventoryService(db)
        result = await inventory_service.check_stock_availability(product_id, quantity)
        
        return {
            "status": "success",
            "available": result["available"],
            "current_stock": result["current_stock"],
            "message": result["message"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/movement-report")
async def get_stock_movement_report(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    transaction_type: Optional[str] = None,
    db = Depends(get_db)
):
    """Get stock movement report with filters"""
    try:
        # Aggregate all stock movements from all products
        pipeline = [
            {"$unwind": "$stock_history"},
            {"$replaceRoot": {"newRoot": "$stock_history"}},
            {"$sort": {"created_at": -1}},
            {"$project": {"_id": 0}}
        ]
        
        # Apply filters if provided
        match_stage = {}
        if from_date:
            match_stage["created_at"] = {"$gte": from_date}
        if to_date:
            if "created_at" in match_stage:
                match_stage["created_at"]["$lte"] = to_date
            else:
                match_stage["created_at"] = {"$lte": to_date}
        if transaction_type:
            match_stage["type"] = transaction_type
        
        if match_stage:
            pipeline.insert(1, {"$match": match_stage})
        
        movements = await db.products.aggregate(pipeline).to_list(None)
        
        # Calculate summary
        total_in = sum(m["quantity"] for m in movements if m["quantity"] > 0)
        total_out = abs(sum(m["quantity"] for m in movements if m["quantity"] < 0))
        
        return {
            "status": "success",
            "count": len(movements),
            "movements": movements,
            "summary": {
                "total_stock_in": total_in,
                "total_stock_out": total_out,
                "net_change": total_in - total_out
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/valuation-report")
async def get_stock_valuation_report(db = Depends(get_db)):
    """Get stock valuation report (stock value by category)"""
    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$category",
                    "total_products": {"$sum": 1},
                    "total_quantity": {"$sum": "$current_stock"},
                    "total_value": {
                        "$sum": {"$multiply": ["$current_stock", "$price"]}
                    }
                }
            },
            {"$sort": {"total_value": -1}}
        ]
        
        category_wise = await db.products.aggregate(pipeline).to_list(None)
        
        # Calculate overall totals
        overall_total_value = sum(c["total_value"] for c in category_wise)
        overall_total_quantity = sum(c["total_quantity"] for c in category_wise)
        
        return {
            "status": "success",
            "valuation": {
                "category_wise": category_wise,
                "overall": {
                    "total_products": len(category_wise),
                    "total_quantity": overall_total_quantity,
                    "total_value": overall_total_value
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock-with-reservations")
async def get_stock_with_reservations(db = Depends(get_db)):
    """Get all products with their stock levels including reservations"""
    try:
        products = await db.products.find(
            {},
            {
                "_id": 0,
                "id": 1,
                "name": 1,
                "brand": 1,
                "model_number": 1,
                "sku": 1,
                "price": 1,
                "category": 1,
                "current_stock": 1,
                "reserved_stock": 1,
                "reorder_level": 1
            }
        ).to_list(None)
        
        # Calculate available stock for each product
        for product in products:
            current = product.get("current_stock", 0)
            reserved = product.get("reserved_stock", 0)
            product["available_stock"] = current - reserved
            product["is_low_stock"] = current <= product.get("reorder_level", 5)
            product["is_out_of_stock"] = (current - reserved) <= 0
        
        return {
            "status": "success",
            "count": len(products),
            "products": products
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reservations")
async def get_all_reservations(status: str = "active", db = Depends(get_db)):
    """Get all stock reservations"""
    try:
        query = {}
        if status:
            query["status"] = status
        
        reservations = await db.stock_reservations.find(query, {"_id": 0}).to_list(None)
        
        # Enrich with product names
        for res in reservations:
            product = await db.products.find_one(
                {"id": res.get("product_id")}, 
                {"_id": 0, "name": 1, "brand": 1, "model_number": 1}
            )
            if product:
                res["product_name"] = product.get("name", "Unknown")
                res["product_brand"] = product.get("brand", "")
        
        return {
            "status": "success",
            "count": len(reservations),
            "reservations": reservations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-stock")
async def add_stock_to_product(
    product_id: str,
    quantity: int,
    store_code: str = None,
    reason: str = "Stock addition",
    db = Depends(get_db)
):
    """Add stock to a product (receiving inventory)"""
    try:
        inventory_service = InventoryService(db)
        
        result = await inventory_service.update_stock(
            product_id=product_id,
            quantity_change=quantity,  # Positive for addition
            transaction_type="purchase",
            reference_id=store_code,
            reason=reason,
            created_by="admin"
        )
        
        if result["success"]:
            return {
                "status": "success",
                "message": f"Added {quantity} units to stock",
                "current_stock": result["current_stock"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

