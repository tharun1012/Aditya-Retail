import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def fix_images_and_categories():
    # Get MongoDB connection
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.getenv('DB_NAME', 'startup_template')
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    products_collection = db['products']
    
    print("=" * 80)
    print("COMPREHENSIVE FIX: IMAGES AND CATEGORIES")
    print("=" * 80)
    
    # ===========================
    # PART 1: Fix Chimney Images
    # ===========================
    print("\n📸 PART 1: Fixing Chimney Images...")
    print("-" * 80)
    
    chimneys = await products_collection.find({"category": "Chimney"}).to_list(length=None)
    chimney_fixed = 0
    
    for chimney in chimneys:
        images_array = chimney.get('images', [])
        current_image = chimney.get('image', 'N/A')
        
        if (current_image == 'N/A' or not current_image) and images_array:
            # Set the 'image' field to the first image from 'images' array
            first_image = images_array[0]
            result = await products_collection.update_one(
                {"id": chimney['id']},
                {"$set": {"image": first_image}}
            )
            if result.modified_count > 0:
                chimney_fixed += 1
                print(f"  ✅ Fixed: {chimney.get('model_number', 'N/A')} - {chimney.get('name', 'N/A')[:50]}")
                print(f"     Image: {first_image[:80]}...")
    
    print(f"\n✓ Fixed {chimney_fixed} chimney images")
    
    # ================================
    # PART 2: Fix Dishwasher Images
    # ================================
    print("\n📸 PART 2: Fixing Dishwasher Images...")
    print("-" * 80)
    
    dishwashers = await products_collection.find({"category": "Dishwasher"}).to_list(length=None)
    dishwasher_fixed = 0
    
    for dishwasher in dishwashers:
        images_array = dishwasher.get('images', [])
        current_image = dishwasher.get('image', 'N/A')
        
        if (current_image == 'N/A' or not current_image) and images_array:
            # Set the 'image' field to the first image from 'images' array
            first_image = images_array[0]
            result = await products_collection.update_one(
                {"id": dishwasher['id']},
                {"$set": {"image": first_image}}
            )
            if result.modified_count > 0:
                dishwasher_fixed += 1
                print(f"  ✅ Fixed: {dishwasher.get('model_number', 'N/A')} - {dishwasher.get('name', 'N/A')[:50]}")
                print(f"     Image: {first_image[:80]}...")
    
    print(f"\n✓ Fixed {dishwasher_fixed} dishwasher images")
    
    # ====================================
    # PART 3: Categorize Air Fryers
    # ====================================
    print("\n🗂️  PART 3: Categorizing Air Fryers...")
    print("-" * 80)
    
    air_fryers = await products_collection.find({
        "category": "Uncategorized",
        "name": {"$regex": "air fryer", "$options": "i"}
    }).to_list(length=None)
    
    air_fryer_fixed = 0
    
    for af in air_fryers:
        result = await products_collection.update_one(
            {"id": af['id']},
            {"$set": {"category": "Air Fryer"}}
        )
        if result.modified_count > 0:
            air_fryer_fixed += 1
            print(f"  ✅ Categorized: {af.get('model_number', 'N/A')} - {af.get('name', 'N/A')}")
    
    print(f"\n✓ Categorized {air_fryer_fixed} air fryers")
    
    # ======================================
    # PART 4: Categorize Coffee Machines
    # ======================================
    print("\n☕ PART 4: Categorizing Coffee Machines...")
    print("-" * 80)
    
    coffee_machines = await products_collection.find({
        "category": "Uncategorized",
        "name": {"$regex": "coffee", "$options": "i"}
    }).to_list(length=None)
    
    coffee_fixed = 0
    
    for cm in coffee_machines:
        result = await products_collection.update_one(
            {"id": cm['id']},
            {"$set": {"category": "Coffee Machine"}}
        )
        if result.modified_count > 0:
            coffee_fixed += 1
            print(f"  ✅ Categorized: {cm.get('model_number', 'N/A')} - {cm.get('name', 'N/A')}")
    
    print(f"\n✓ Categorized {coffee_fixed} coffee machines")
    
    # ====================================
    # PART 5: Summary & Verification
    # ====================================
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    
    print(f"\nFixed Images:")
    print(f"  • Chimneys: {chimney_fixed} products")
    print(f"  • Dishwashers: {dishwasher_fixed} products")
    
    print(f"\nCategorized Products:")
    print(f"  • Air Fryers: {air_fryer_fixed} products → 'Air Fryer'")
    print(f"  • Coffee Machines: {coffee_fixed} products → 'Coffee Machine'")
    
    # Final verification
    print("\n" + "=" * 80)
    print("🔍 VERIFICATION")
    print("=" * 80)
    
    # Check chimneys
    chimneys_with_no_image = await products_collection.count_documents({
        "category": "Chimney",
        "$or": [{"image": "N/A"}, {"image": None}, {"image": ""}]
    })
    print(f"\nChimneys without 'image' field: {chimneys_with_no_image} (should be 0)")
    
    # Check dishwashers
    dishwashers_with_no_image = await products_collection.count_documents({
        "category": "Dishwasher",
        "$or": [{"image": "N/A"}, {"image": None}, {"image": ""}]
    })
    print(f"Dishwashers without 'image' field: {dishwashers_with_no_image} (should be 0)")
    
    # Check uncategorized
    remaining_uncategorized = await products_collection.count_documents({"category": "Uncategorized"})
    print(f"Remaining Uncategorized products: {remaining_uncategorized}")
    
    # Show new category counts
    print("\n📦 Updated Category Counts:")
    categories = await products_collection.distinct("category")
    for cat in sorted(categories):
        count = await products_collection.count_documents({"category": cat})
        print(f"  • {cat}: {count} products")
    
    print("\n" + "=" * 80)
    print("✅ ALL FIXES COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_images_and_categories())
