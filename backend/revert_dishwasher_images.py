import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
products_collection = db['products']

async def revert_dishwasher_images():
    """Revert dishwasher images back to 900x resolution"""
    
    print("=" * 70)
    print("REVERTING DISHWASHER IMAGES - Back to 900x Resolution")
    print("=" * 70)
    
    updated_count = 0
    
    async for product in products_collection.find({'category': 'Dishwasher'}):
        model = product['model_number']
        old_images = product.get('images', [])
        
        if not old_images:
            print(f"\n⚠️  {model}: No images found!")
            continue
        
        # Check if images are 5120x
        if old_images and '900x' in old_images[0]:
            print(f"\n✅ {model}: Already using 900x resolution")
            continue
        
        # Update 5120x back to 900x
        new_images = []
        for img_url in old_images:
            if '5120x' in img_url:
                new_url = img_url.replace('5120x', '900x')
                new_images.append(new_url)
            else:
                new_images.append(img_url)
        
        # Update in database
        result = await products_collection.update_one(
            {'_id': product['_id']},
            {'$set': {'images': new_images}}
        )
        
        if result.modified_count > 0:
            updated_count += 1
            print(f"\n✅ Reverted {model}:")
            print(f"   From: {old_images[0][:80]}...")
            print(f"   To:   {new_images[0][:80]}...")
        
    print("\n" + "=" * 70)
    print(f"✅ Reverted {updated_count} dishwasher products back to 900x!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(revert_dishwasher_images())
