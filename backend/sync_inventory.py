"""
Migration script to sync product current_stock to store_inventory collection.
This ensures GRN stock data is properly reflected in the stock list.
Run: python sync_inventory.py
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

async def sync_inventory():
    """Sync product stock to store_inventory collection"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'startup_template')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("Starting inventory sync...")
    
    # Get all stores
    stores = await db.stores.find({}).to_list(None)
    print(f"Found {len(stores)} stores")
    
    # Get all products with stock > 0
    products_with_stock = await db.products.find(
        {"current_stock": {"$gt": 0}},
        {"id": 1, "name": 1, "current_stock": 1}
    ).to_list(None)
    print(f"Found {len(products_with_stock)} products with stock > 0")
    
    # Get inventory transactions to understand which store received which products
    transactions = await db.inventory_transactions.find({}).to_list(None)
    print(f"Found {len(transactions)} inventory transactions")
    
    # Build store-product mapping from transactions
    store_products = {}
    for trans in transactions:
        store_code = trans.get('store_code')
        product_id = trans.get('product_id')
        qty_change = trans.get('quantity_change', 0)
        
        if store_code and product_id:
            if store_code not in store_products:
                store_products[store_code] = {}
            if product_id not in store_products[store_code]:
                store_products[store_code][product_id] = 0
            store_products[store_code][product_id] += qty_change
    
    # Also check the inventory collection (separate tracking)
    inventory_docs = await db.inventory.find({}).to_list(None)
    print(f"Found {len(inventory_docs)} inventory documents")
    
    for inv in inventory_docs:
        store_code = inv.get('store_code')
        product_id = inv.get('product_id')
        qty = inv.get('quantity', 0)
        
        if store_code and product_id and qty > 0:
            if store_code not in store_products:
                store_products[store_code] = {}
            # Use max of transaction-based or inventory-based quantity
            current = store_products[store_code].get(product_id, 0)
            store_products[store_code][product_id] = max(current, qty)
    
    # Update store_inventory for each store
    synced_count = 0
    for store in stores:
        store_id = store.get('id')
        store_code = store.get('code')
        store_name = store.get('name')
        
        # Get products for this store
        products_map = store_products.get(store_code, {})
        
        if products_map:
            # Update store_inventory
            await db.store_inventory.update_one(
                {"store_id": store_id},
                {
                    "$set": {
                        "products": products_map,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                },
                upsert=True
            )
            synced_count += 1
            print(f"  Synced {store_name} ({store_code}): {len(products_map)} products")
    
    # If no transactions exist but products have stock, assign to first warehouse
    if not store_products and products_with_stock:
        # Find the warehouse
        warehouse = next((s for s in stores if s.get('is_warehouse')), stores[0] if stores else None)
        
        if warehouse:
            products_map = {}
            for product in products_with_stock:
                products_map[product['id']] = product.get('current_stock', 0)
            
            await db.store_inventory.update_one(
                {"store_id": warehouse['id']},
                {
                    "$set": {
                        "products": products_map,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                },
                upsert=True
            )
            print(f"  Assigned all stock to warehouse: {warehouse.get('name')}")
            synced_count = 1
    
    print(f"\nSync complete! Updated {synced_count} store inventories.")
    
    # Verify
    store_inv_count = await db.store_inventory.count_documents({})
    print(f"Total store_inventory documents: {store_inv_count}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(sync_inventory())
