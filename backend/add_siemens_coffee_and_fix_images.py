import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
products_collection = db['products']

async def add_coffee_and_fix_images():
    """Add Siemens coffee machine and fix image issues"""
    
    # First, add the Siemens coffee machine
    coffee_machine = {
        "id": str(uuid.uuid4()),
        "name": "Siemens iQ700 Built-In Fully Automatic Coffee Machine Black CT718L1B0",
        "brand": "Siemens",
        "model_number": "CT718L1B0",
        "category": "Oven",
        "sub_category": "Built-In Coffee Machine",
        "price": 383500.00,
        "description": "Premium Siemens iQ700 built-in coffee machine with ceramDrive grinder, coffeeSensor System, oneTouch DoubleCup, and Home Connect.",
        "short_description": "iQ700 Built-in coffee machine with ceramDrive, coffeeSensor, oneTouch DoubleCup, and Home Connect.",
        "long_description": "The Siemens iQ700 Built-In Fully Automatic Coffee Machine CT718L1B0 delivers barista-quality beverages at home. The ceramDrive grinding system ensures finely ground coffee with fuller flavor while operating quietly. The intelligent coffeeSensor System adapts to each bean variety and grinds the perfect quantity every time. With oneTouch DoubleCup functionality, prepare two beverages simultaneously, even with milk. The sensoFlow System maintains ideal brewing temperature for maximum aroma extraction. The integrated milk system with hose creates perfect milk froth. Home Connect enables smart control via smartphone. With 2.4L water tank and 400g bean container, enjoy multiple cups without frequent refills.",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/5120x/18051948_CT718L1B0_STP_def.webp"
        ],
        "stock": 3,
        "rating": 0.0,
        "reviews_count": 0,
        "specifications": {
            "Type": "Built-in fully automatic coffee machine",
            "Required Niche Size": "449 x 558 x 376 mm",
            "Water Container Capacity": "2.4 L",
            "Bean Container": "1 container, 400g capacity",
            "Milk System": "Integrated with hose",
            "Grinder": "ceramDrive",
            "Home Connect": "Yes",
            "Color": "Black",
            "Series": "iQ700"
        },
        "key_features": [
            "ceramDrive - Finely ground coffee with fuller flavor",
            "coffeeSensor System - Adapts to each bean variety",
            "oneTouch DoubleCup - Two beverages at once",
            "sensoFlow System - Ideal brewing temperature",
            "Integrated milk system with hose",
            "Home Connect enabled",
            "2.4L water tank, 400g bean container",
            "Premium iQ700 series"
        ],
        "highlights": [
            "ceramDrive grinding system",
            "coffeeSensor System intelligence",
            "oneTouch DoubleCup functionality",
            "sensoFlow ideal temperature"
        ],
        "documents": [
            {
                "type": "User Manual",
                "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/coffee-machines/built-in-coffee-machines/CT718L1B0",
                "title": "CT718L1B0 User Manual"
            }
        ],
        "warranty": "2 years manufacturer warranty",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    print("=" * 70)
    print("ADDING SIEMENS COFFEE MACHINE & FIXING IMAGE ISSUES")
    print("=" * 70)
    
    # Add coffee machine
    existing = await products_collection.find_one({"model_number": coffee_machine["model_number"]})
    if existing:
        print(f"\n⚠️  Coffee machine {coffee_machine['model_number']} already exists.")
    else:
        await products_collection.insert_one(coffee_machine)
        print(f"\n✅ Added: {coffee_machine['name']}")
        print(f"   Model: {coffee_machine['model_number']}")
        print(f"   Price: ₹{coffee_machine['price']:,.2f}")
    
    # Fix Bosch chimney and dishwasher images (900x to 5120x)
    print("\n" + "=" * 70)
    print("UPGRADING BOSCH CHIMNEY & DISHWASHER IMAGES TO 5120x")
    print("=" * 70)
    
    fixed_count = 0
    categories_to_fix = ['Chimney', 'Dishwasher']
    
    for category in categories_to_fix:
        print(f"\n{category.upper()}S:")
        async for product in products_collection.find({'category': category, 'brand': 'Bosch'}):
            old_images = product.get('images', [])
            if not old_images:
                continue
            
            # Skip if already using 5120x
            if '5120x' in old_images[0]:
                continue
            
            # Update 900x to 5120x
            new_images = []
            for img_url in old_images:
                if '900x' in img_url:
                    new_url = img_url.replace('900x', '5120x')
                    new_images.append(new_url)
                else:
                    new_images.append(img_url)
            
            # Update in database
            result = await products_collection.update_one(
                {'_id': product['_id']},
                {'$set': {'images': new_images}}
            )
            
            if result.modified_count > 0:
                fixed_count += 1
                print(f"  ✅ {product['model_number']}: Upgraded to 5120x")
    
    # Get final stats
    total_count = await products_collection.count_documents({})
    siemens_count = await products_collection.count_documents({"brand": "Siemens"})
    oven_count = await products_collection.count_documents({"category": "Oven"})
    
    print("\n" + "=" * 70)
    print(f"✅ Coffee machine added and {fixed_count} products' images upgraded!")
    print(f"Total products: {total_count}")
    print(f"Total Siemens products: {siemens_count}")
    print(f"Total Ovens (including coffee machines): {oven_count}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(add_coffee_and_fix_images())
