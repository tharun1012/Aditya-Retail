"""
Migration script to sync existing GRN data to store_inventory collection.
This fixes the issue where GRNs were created but stock doesn't show in Stock List.

Run this AFTER deploying the code fix:
  cd /app/backend && python migrate_grn_to_store_inventory.py
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

async def migrate_grn_stock():
    """Migrate existing GRN stock data to store_inventory collection"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'startup_template')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 60)
    print("GRN to Store Inventory Migration Script")
    print("=" * 60)
    
    # Step 1: Get all stores
    stores = await db.stores.find({}).to_list(None)
    store_map = {s.get('code'): s for s in stores}
    print(f"\nFound {len(stores)} stores:")
    for s in stores:
        print(f"  - {s.get('name')} ({s.get('code')}) - ID: {s.get('id')}")
    
    # Step 2: Get all GRNs
    grns = await db.grn.find({}).to_list(None)
    print(f"\nFound {len(grns)} GRNs to process")
    
    if not grns:
        print("\nNo GRNs found. Nothing to migrate.")
        client.close()
        return
    
    # Step 3: Build store-product quantity map from GRNs
    store_products = {}  # {store_id: {product_id: quantity}}
    
    for grn in grns:
        store_code = grn.get('store_code')
        grn_number = grn.get('grn_number', 'Unknown')
        
        if not store_code:
            print(f"  WARNING: GRN {grn_number} has no store_code, skipping...")
            continue
        
        store = store_map.get(store_code)
        if not store:
            print(f"  WARNING: Store code '{store_code}' not found for GRN {grn_number}")
            continue
        
        store_id = store.get('id')
        if store_id not in store_products:
            store_products[store_id] = {}
        
        items = grn.get('items', [])
        for item in items:
            product_id = item.get('product_id')
            received_qty = item.get('received_quantity', 0)
            
            if product_id and received_qty > 0:
                if product_id not in store_products[store_id]:
                    store_products[store_id][product_id] = 0
                store_products[store_id][product_id] += received_qty
        
        print(f"  Processed GRN: {grn_number} - {len(items)} items for store {store_code}")
    
    # Step 4: Also include inventory transactions (if any)
    transactions = await db.inventory_transactions.find({
        'transaction_type': 'grn_receipt'
    }).to_list(None)
    
    print(f"\nFound {len(transactions)} inventory transactions")
    
    for trans in transactions:
        store_code = trans.get('store_code')
        product_id = trans.get('product_id')
        qty_change = trans.get('quantity_change', 0)
        
        if store_code and product_id and qty_change > 0:
            store = store_map.get(store_code)
            if store:
                store_id = store.get('id')
                if store_id not in store_products:
                    store_products[store_id] = {}
                # Use max to avoid double-counting
                current = store_products[store_id].get(product_id, 0)
                store_products[store_id][product_id] = max(current, qty_change)
    
    # Step 5: Update store_inventory collection
    print(f"\n{'=' * 60}")
    print("Updating store_inventory collection...")
    print("=" * 60)
    
    updated_count = 0
    for store_id, products in store_products.items():
        if not products:
            continue
        
        # Find store name for logging
        store_name = next((s.get('name') for s in stores if s.get('id') == store_id), 'Unknown')
        
        # Get existing store inventory
        existing = await db.store_inventory.find_one({'store_id': store_id})
        existing_products = existing.get('products', {}) if existing else {}
        
        # Merge: add new quantities to existing
        merged_products = existing_products.copy()
        for product_id, qty in products.items():
            if product_id in merged_products:
                # Already has stock, add to it (or take the higher value)
                merged_products[product_id] = max(merged_products[product_id], qty)
            else:
                merged_products[product_id] = qty
        
        # Update store_inventory
        result = await db.store_inventory.update_one(
            {'store_id': store_id},
            {
                '$set': {
                    'products': merged_products,
                    'updated_at': datetime.now(timezone.utc).isoformat(),
                    'migrated_at': datetime.now(timezone.utc).isoformat()
                }
            },
            upsert=True
        )
        
        total_qty = sum(merged_products.values())
        print(f"  ✅ {store_name}: {len(merged_products)} products, {total_qty} total units")
        updated_count += 1
    
    # Step 6: Verify
    print(f"\n{'=' * 60}")
    print("Migration Complete!")
    print("=" * 60)
    print(f"Updated {updated_count} store inventories")
    
    # Show final state
    final_inventories = await db.store_inventory.find({}).to_list(None)
    print(f"\nFinal store_inventory state:")
    for inv in final_inventories:
        store_id = inv.get('store_id')
        store_name = next((s.get('name') for s in stores if s.get('id') == store_id), 'Unknown')
        products = inv.get('products', {})
        total = sum(products.values())
        print(f"  - {store_name}: {len(products)} products, {total} total units")
    
    client.close()
    print("\nDone! Stock should now appear in the Stock List.")

if __name__ == "__main__":
    asyncio.run(migrate_grn_stock())
