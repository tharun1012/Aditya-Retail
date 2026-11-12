"""
Migration script to standardize category structure
Changes 'subcategories' to 'sub_categories' in all category documents
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def migrate():
    client = AsyncIOMotorClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
    db_name = os.environ.get("DB_NAME", "startup_template")
    db = client[db_name]
    
    print("Starting category structure migration...")
    
    # Find all categories with 'subcategories' key
    categories = await db.categories.find({"subcategories": {"$exists": True}}).to_list(length=None)
    
    print(f"Found {len(categories)} categories to migrate")
    
    updated_count = 0
    for cat in categories:
        if 'subcategories' in cat:
            # Rename the key from 'subcategories' to 'sub_categories'
            await db.categories.update_one(
                {"_id": cat["_id"]},
                {
                    "$set": {"sub_categories": cat['subcategories']},
                    "$unset": {"subcategories": ""}
                }
            )
            updated_count += 1
            print(f"  ✓ Updated: {cat.get('name')}")
    
    print(f"\n✅ Migration complete! Updated {updated_count} categories")
    
    # Verify
    remaining = await db.categories.count_documents({"subcategories": {"$exists": True}})
    if remaining == 0:
        print("✅ Verification passed: No 'subcategories' key found in any category")
    else:
        print(f"⚠️ Warning: {remaining} categories still have 'subcategories' key")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate())
