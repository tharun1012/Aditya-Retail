import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def categorize_dishwashers():
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['startup_template']
    products_collection = db['products']
    
    print("=" * 70)
    print("CATEGORIZING DISHWASHERS")
    print("=" * 70)
    
    # Get all uncategorized dishwasher models
    dishwasher_models = [
        'SMS4HMB62T', 'SMS6HMC00I', 'SMS6HMI01I', 'SMS6HMI00I',
        'SMS6ZCW37Q', 'SMS6IKI01I', 'SMS6IKW01I', 'SMV6HMX01I', 'SMI4IKS00I'
    ]
    
    updated = 0
    for model in dishwasher_models:
        result = await products_collection.update_one(
            {'model_number': model},
            {'$set': {'category': 'Dishwasher'}}
        )
        if result.modified_count > 0:
            print(f"✅ {model} → Dishwasher")
            updated += 1
    
    print("\n" + "=" * 70)
    print(f"✅ Categorized {updated} dishwashers")
    print("=" * 70)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(categorize_dishwashers())
