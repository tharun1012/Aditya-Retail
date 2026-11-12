import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def migrate_products():
    """Migrate all products from ecommerce_db to startup_template"""
    
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    
    source_db = client.ecommerce_db
    target_db = client.startup_template
    
    print("🔄 Starting product migration...")
    print(f"Source: ecommerce_db")
    print(f"Target: startup_template")
    
    # Get all products from source
    products = await source_db.products.find({}).to_list(length=None)
    print(f"\n📦 Found {len(products)} products in source database")
    
    if len(products) == 0:
        print("❌ No products to migrate!")
        client.close()
        return
    
    # Clear existing products in target (optional - comment out if you want to keep old products)
    deleted_count = await target_db.products.delete_many({})
    print(f"🗑️  Deleted {deleted_count.deleted_count} old products from target database")
    
    # Insert all products into target
    result = await target_db.products.insert_many(products)
    print(f"✅ Successfully migrated {len(result.inserted_ids)} products to startup_template")
    
    # Verify
    new_count = await target_db.products.count_documents({})
    print(f"✅ Target database now has {new_count} products")
    
    # Show categories
    all_products = await target_db.products.find({}).to_list(length=None)
    categories = set([p.get('category') for p in all_products])
    print(f"\n📊 Categories in target database: {sorted(categories)}")
    
    # Show count by category
    for cat in sorted(categories):
        count = len([p for p in all_products if p.get('category') == cat])
        print(f"   - {cat}: {count} products")
    
    client.close()
    print("\n✅ Migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate_products())
