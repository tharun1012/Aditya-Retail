import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def fix_all_na_images():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client['startup_template']
    
    print("=" * 80)
    print("FIXING ALL PRODUCTS WITH 'N/A' IMAGE FIELD")
    print("=" * 80)
    
    # Find all products where image is "N/A" or None or empty
    products_with_na = await db.products.find({
        "$or": [
            {"image": "N/A"},
            {"image": None},
            {"image": ""},
            {"image": {"$exists": False}}
        ]
    }).to_list(length=None)
    
    print(f"\nFound {len(products_with_na)} products with missing 'image' field")
    print("-" * 80)
    
    fixed_count = 0
    failed_count = 0
    
    for product in products_with_na:
        model = product.get('model_number', 'N/A')
        name = product.get('name', 'N/A')
        images_array = product.get('images', [])
        
        if images_array and len(images_array) > 0:
            # Use the first image from the images array
            first_image = images_array[0]
            
            result = await db.products.update_one(
                {"id": product['id']},
                {"$set": {"image": first_image}}
            )
            
            if result.modified_count > 0:
                fixed_count += 1
                print(f"  ✅ {model[:15]:<15} - {name[:50]}")
                print(f"     → {first_image[:75]}...")
            else:
                failed_count += 1
                print(f"  ⚠️  {model[:15]:<15} - Failed to update")
        else:
            failed_count += 1
            print(f"  ❌ {model[:15]:<15} - No images array available")
    
    print("\n" + "=" * 80)
    print(f"📊 SUMMARY")
    print("=" * 80)
    print(f"  Fixed: {fixed_count} products")
    print(f"  Failed: {failed_count} products")
    print(f"  Total processed: {len(products_with_na)} products")
    
    # Verify the fix
    print("\n" + "=" * 80)
    print("🔍 VERIFICATION")
    print("=" * 80)
    
    remaining_na = await db.products.count_documents({
        "$or": [
            {"image": "N/A"},
            {"image": None},
            {"image": ""}
        ]
    })
    
    print(f"  Remaining products with 'N/A' image: {remaining_na}")
    
    if remaining_na == 0:
        print("\n✅ ALL PRODUCTS NOW HAVE VALID IMAGE FIELDS!")
    else:
        print(f"\n⚠️  {remaining_na} products still need attention")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_all_na_images())
