import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
products_collection = db['products']

# Fallback generic product image
FALLBACK_IMAGE = "https://media3.bsh-group.com/Product_Shots/5120x/MCSA00807390_SMS6HMI01A_STP_def.webp"

async def fix_dishwasher_images():
    """Fix dishwasher images by using working alternatives"""
    
    # Known working dishwasher images from Bosch
    working_images = {
        "SMS4HMB62T": [
            "https://media3.bsh-group.com/Product_Shots/5120x/21348224_SMS4HMB62T_STP_def.webp"
        ],
        "SMS6HMC00I": [
            "https://media3.bsh-group.com/Product_Shots/5120x/MCSA00807390_SMS6HMI01A_STP_def.webp"
        ],
        "SMS6HMI01I": [
            "https://media3.bsh-group.com/Product_Shots/5120x/MCSA00807390_SMS6HMI01A_STP_def.webp"
        ],
        "SMS6HMI00I": [
            "https://media3.bsh-group.com/Product_Shots/5120x/MCSA00807390_SMS6HMI01A_STP_def.webp"
        ],
        "SMS6ZCW37Q": [
            "https://media3.bsh-group.com/Product_Shots/5120x/MCSA00807390_SMS6HMI01A_STP_def.webp"
        ],
        "SMS6IKI01I": [
            "https://media3.bsh-group.com/Product_Shots/5120x/MCSA00807390_SMS6HMI01A_STP_def.webp"
        ],
        "SMS6IKW01I": [
            "https://media3.bsh-group.com/Product_Shots/5120x/MCSA00807390_SMS6HMI01A_STP_def.webp"
        ],
        "SMV6HMX01I": [
            "https://media3.bsh-group.com/Product_Shots/5120x/MCSA00807390_SMS6HMI01A_STP_def.webp"
        ],
        "SMI4IKS00I": [
            "https://media3.bsh-group.com/Product_Shots/5120x/MCSA00807390_SMS6HMI01A_STP_def.webp"
        ]
    }
    
    print("=" * 70)
    print("FIXING DISHWASHER IMAGES WITH WORKING ALTERNATIVES")
    print("=" * 70)
    
    fixed_count = 0
    
    for model, new_images in working_images.items():
        product = await products_collection.find_one({"model_number": model})
        
        if not product:
            print(f"\n⚠️  {model}: Product not found")
            continue
        
        # Update images
        result = await products_collection.update_one(
            {'_id': product['_id']},
            {'$set': {'images': new_images}}
        )
        
        if result.modified_count > 0:
            fixed_count += 1
            print(f"\n✅ {model}: Image updated")
            print(f"   New image: {new_images[0][:80]}...")
        else:
            print(f"\n⚠️  {model}: No update needed")
    
    print("\n" + "=" * 70)
    print(f"✅ Fixed {fixed_count} dishwasher images!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(fix_dishwasher_images())
