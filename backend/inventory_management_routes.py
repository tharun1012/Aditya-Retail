"""
Multi-Warehouse Inventory Management Routes
Handles store-level inventory, stock transfers, and cross-store visibility
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from database import get_db
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/inventory", tags=["Multi-Warehouse Inventory"])

# ============ MODELS ============

class StockUpdate(BaseModel):
    product_id: str
    quantity: int
    reason: str = "manual_adjustment"  # manual_adjustment, purchase, sale, transfer, return

class StockTransferRequest(BaseModel):
    from_store_id: str
    to_store_id: str
    items: List[Dict[str, Any]]  # [{"product_id": "xxx", "quantity": 10}]
    notes: Optional[str] = None

class StockTransferApproval(BaseModel):
    status: str  # approved, rejected
    notes: Optional[str] = None

# ============ INVENTORY QUERIES ============

@router.get("/store/{store_id}")
async def get_store_inventory(
    store_id: str,
    low_stock_only: bool = False,
    search: Optional[str] = None,
    db = Depends(get_db)
):
    """Get inventory for a specific store"""
    try:
        # Verify store exists
        store = await db.stores.find_one({"id": store_id})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        inventory = await db.store_inventory.find_one({"store_id": store_id})
        if not inventory:
            return {
                "status": "success",
                "store": {"id": store_id, "code": store["code"], "name": store["name"]},
                "products": [],
                "summary": {"total_products": 0, "total_stock": 0, "low_stock_count": 0}
            }
        
        # Get product details
        product_ids = list(inventory.get("products", {}).keys())
        products = await db.products.find(
            {"id": {"$in": product_ids}},
            {"_id": 0, "id": 1, "name": 1, "sku": 1, "category": 1, "price": 1, "images": 1}
        ).to_list(None)
        
        product_map = {p["id"]: p for p in products}
        
        result = []
        low_stock_count = 0
        total_stock = 0
        
        for product_id, qty in inventory.get("products", {}).items():
            product = product_map.get(product_id, {})
            
            # Apply search filter
            if search:
                search_lower = search.lower()
                if search_lower not in product.get("name", "").lower() and search_lower not in product.get("sku", "").lower():
                    continue
            
            # Apply low stock filter
            is_low_stock = qty < 5
            if low_stock_only and not is_low_stock:
                continue
            
            if is_low_stock:
                low_stock_count += 1
            
            total_stock += qty
            
            result.append({
                "product_id": product_id,
                "product_name": product.get("name", "Unknown"),
                "sku": product.get("sku", "N/A"),
                "category": product.get("category", ""),
                "price": product.get("price", 0),
                "quantity": qty,
                "is_low_stock": is_low_stock,
                "stock_value": qty * product.get("price", 0)
            })
        
        # Sort by quantity (low stock first)
        result.sort(key=lambda x: x["quantity"])
        
        return {
            "status": "success",
            "store": {"id": store_id, "code": store["code"], "name": store["name"]},
            "products": result,
            "summary": {
                "total_products": len(result),
                "total_stock": total_stock,
                "low_stock_count": low_stock_count,
                "total_stock_value": sum(p["stock_value"] for p in result)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all-stores")
async def get_all_stores_inventory(
    product_id: Optional[str] = None,
    db = Depends(get_db)
):
    """Get inventory across all stores (for admin/cross-store visibility)"""
    try:
        stores = await db.stores.find({"is_active": True}, {"_id": 0}).to_list(None)
        
        result = []
        for store in stores:
            inventory = await db.store_inventory.find_one({"store_id": store["id"]})
            
            if product_id:
                # Get specific product stock
                qty = inventory.get("products", {}).get(product_id, 0) if inventory else 0
                result.append({
                    "store_id": store["id"],
                    "store_code": store["code"],
                    "store_name": store["name"],
                    "quantity": qty
                })
            else:
                # Get summary
                products = inventory.get("products", {}) if inventory else {}
                result.append({
                    "store_id": store["id"],
                    "store_code": store["code"],
                    "store_name": store["name"],
                    "is_warehouse": store.get("is_warehouse", False),
                    "total_products": len(products),
                    "total_stock": sum(products.values())
                })
        
        return {
            "status": "success",
            "stores": result,
            "total_stores": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/product/{product_id}/availability")
async def get_product_availability(product_id: str, db = Depends(get_db)):
    """Get product availability across all stores"""
    try:
        # Get product details
        product = await db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get inventory from all stores
        stores = await db.stores.find({"is_active": True}, {"_id": 0}).to_list(None)
        
        availability = []
        total_available = 0
        
        for store in stores:
            inventory = await db.store_inventory.find_one({"store_id": store["id"]})
            qty = inventory.get("products", {}).get(product_id, 0) if inventory else 0
            total_available += qty
            
            availability.append({
                "store_id": store["id"],
                "store_code": store["code"],
                "store_name": store["name"],
                "city": store.get("city", ""),
                "quantity": qty,
                "is_available": qty > 0
            })
        
        # Sort by quantity (highest first)
        availability.sort(key=lambda x: x["quantity"], reverse=True)
        
        return {
            "status": "success",
            "product": {
                "id": product["id"],
                "name": product.get("name"),
                "sku": product.get("sku")
            },
            "total_available": total_available,
            "availability": availability
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ STOCK UPDATES ============

@router.post("/store/{store_id}/update")
async def update_store_stock(
    store_id: str,
    update: StockUpdate,
    db = Depends(get_db)
):
    """Update stock for a product in a store"""
    try:
        # Verify store exists
        store = await db.stores.find_one({"id": store_id})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Verify product exists
        product = await db.products.find_one({"id": update.product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get or create inventory
        inventory = await db.store_inventory.find_one({"store_id": store_id})
        if not inventory:
            await db.store_inventory.insert_one({
                "store_id": store_id,
                "store_code": store["code"],
                "products": {},
                "last_updated": datetime.now(timezone.utc)
            })
            current_qty = 0
        else:
            current_qty = inventory.get("products", {}).get(update.product_id, 0)
        
        new_qty = current_qty + update.quantity
        if new_qty < 0:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        
        # Update inventory
        await db.store_inventory.update_one(
            {"store_id": store_id},
            {
                "$set": {
                    f"products.{update.product_id}": new_qty,
                    "last_updated": datetime.now(timezone.utc)
                }
            }
        )
        
        # Log the change
        await db.stock_movements.insert_one({
            "id": str(uuid.uuid4()),
            "store_id": store_id,
            "store_code": store["code"],
            "product_id": update.product_id,
            "product_name": product.get("name"),
            "previous_qty": current_qty,
            "change": update.quantity,
            "new_qty": new_qty,
            "reason": update.reason,
            "created_at": datetime.now(timezone.utc)
        })
        
        return {
            "status": "success",
            "message": "Stock updated",
            "product_id": update.product_id,
            "previous_qty": current_qty,
            "change": update.quantity,
            "new_qty": new_qty
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ STOCK TRANSFERS ============

@router.post("/transfer")
async def create_stock_transfer(
    transfer: StockTransferRequest,
    db = Depends(get_db)
):
    """Create a stock transfer request between stores"""
    try:
        # Verify both stores exist
        from_store = await db.stores.find_one({"id": transfer.from_store_id})
        to_store = await db.stores.find_one({"id": transfer.to_store_id})
        
        if not from_store:
            raise HTTPException(status_code=404, detail="Source store not found")
        if not to_store:
            raise HTTPException(status_code=404, detail="Destination store not found")
        
        # Check source inventory
        from_inventory = await db.store_inventory.find_one({"store_id": transfer.from_store_id})
        if not from_inventory:
            raise HTTPException(status_code=400, detail="Source store has no inventory")
        
        # Validate all items have sufficient stock
        validated_items = []
        for item in transfer.items:
            product_id = item.get("product_id")
            requested_qty = item.get("quantity", 0)
            
            available_qty = from_inventory.get("products", {}).get(product_id, 0)
            if available_qty < requested_qty:
                product = await db.products.find_one({"id": product_id})
                product_name = product.get("name", product_id) if product else product_id
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {product_name}. Available: {available_qty}, Requested: {requested_qty}"
                )
            
            # Get product details
            product = await db.products.find_one({"id": product_id})
            validated_items.append({
                "product_id": product_id,
                "product_name": product.get("name") if product else "Unknown",
                "quantity": requested_qty,
                "available_before": available_qty
            })
        
        # Create transfer record
        transfer_id = str(uuid.uuid4())
        transfer_data = {
            "id": transfer_id,
            "transfer_number": f"TRF{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "from_store_id": transfer.from_store_id,
            "from_store_code": from_store["code"],
            "from_store_name": from_store["name"],
            "to_store_id": transfer.to_store_id,
            "to_store_code": to_store["code"],
            "to_store_name": to_store["name"],
            "items": validated_items,
            "notes": transfer.notes,
            "status": "pending",  # pending, approved, rejected, completed
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.stock_transfers.insert_one(transfer_data)
        
        return {
            "status": "success",
            "message": "Stock transfer request created",
            "transfer_id": transfer_id,
            "transfer_number": transfer_data["transfer_number"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/transfer/{transfer_id}/approve")
async def approve_stock_transfer(
    transfer_id: str,
    approval: StockTransferApproval,
    db = Depends(get_db)
):
    """Approve or reject a stock transfer"""
    try:
        transfer = await db.stock_transfers.find_one({"id": transfer_id})
        if not transfer:
            raise HTTPException(status_code=404, detail="Transfer not found")
        
        if transfer["status"] != "pending":
            raise HTTPException(status_code=400, detail=f"Transfer is already {transfer['status']}")
        
        if approval.status == "approved":
            # Execute the transfer
            for item in transfer["items"]:
                product_id = item["product_id"]
                qty = item["quantity"]
                
                # Deduct from source
                await db.store_inventory.update_one(
                    {"store_id": transfer["from_store_id"]},
                    {"$inc": {f"products.{product_id}": -qty}}
                )
                
                # Add to destination
                await db.store_inventory.update_one(
                    {"store_id": transfer["to_store_id"]},
                    {
                        "$inc": {f"products.{product_id}": qty},
                        "$set": {"last_updated": datetime.now(timezone.utc)}
                    },
                    upsert=True
                )
                
                # Log movements
                await db.stock_movements.insert_many([
                    {
                        "id": str(uuid.uuid4()),
                        "store_id": transfer["from_store_id"],
                        "store_code": transfer["from_store_code"],
                        "product_id": product_id,
                        "product_name": item["product_name"],
                        "change": -qty,
                        "reason": f"transfer_out:{transfer_id}",
                        "created_at": datetime.now(timezone.utc)
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "store_id": transfer["to_store_id"],
                        "store_code": transfer["to_store_code"],
                        "product_id": product_id,
                        "product_name": item["product_name"],
                        "change": qty,
                        "reason": f"transfer_in:{transfer_id}",
                        "created_at": datetime.now(timezone.utc)
                    }
                ])
        
        # Update transfer status
        await db.stock_transfers.update_one(
            {"id": transfer_id},
            {"$set": {
                "status": "completed" if approval.status == "approved" else "rejected",
                "approval_notes": approval.notes,
                "approved_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        return {
            "status": "success",
            "message": f"Transfer {approval.status}",
            "transfer_id": transfer_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transfers")
async def list_stock_transfers(
    store_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db = Depends(get_db)
):
    """List stock transfers"""
    try:
        query = {}
        if store_id:
            query["$or"] = [
                {"from_store_id": store_id},
                {"to_store_id": store_id}
            ]
        if status:
            query["status"] = status
        
        transfers = await db.stock_transfers.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(None)
        
        return {
            "status": "success",
            "transfers": transfers,
            "count": len(transfers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ STOCK MOVEMENTS LOG ============

@router.get("/movements")
async def get_stock_movements(
    store_id: Optional[str] = None,
    product_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 100,
    db = Depends(get_db)
):
    """Get stock movement history"""
    try:
        query = {}
        if store_id:
            query["store_id"] = store_id
        if product_id:
            query["product_id"] = product_id
        
        if from_date or to_date:
            from dateutil import parser
            date_query = {}
            if from_date:
                date_query["$gte"] = parser.parse(from_date).replace(tzinfo=timezone.utc)
            if to_date:
                date_query["$lte"] = parser.parse(to_date).replace(tzinfo=timezone.utc)
            query["created_at"] = date_query
        
        movements = await db.stock_movements.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(None)
        
        return {
            "status": "success",
            "movements": movements,
            "count": len(movements)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
