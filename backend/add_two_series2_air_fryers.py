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

async def add_series2_air_fryers():
    """Add two Bosch Series 2 Air Fryer models to database"""
    
    products = [
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 2 Air Fryer Black MAF240B5IN",
            "brand": "Bosch",
            "model_number": "MAF240B5IN",
            "category": "Uncategorized",
            "sub_category": "Air Fryer",
            "price": 13775.00,
            "description": "Experience healthy cooking with the Bosch Series 2 Air Fryer. Featuring a 4.1L capacity, this compact air fryer is perfect for preparing delicious meals with minimal oil.",
            "short_description": "Series 2 Air Fryer with 4.1L capacity, touch control, and eight preset programmes for easy cooking.",
            "long_description": "The Bosch Series 2 Air Fryer MAF240B5IN brings convenient and healthy cooking to your kitchen. With a 4.1 litre capacity, it's ideal for preparing meals for 2-3 people. The touch control panel makes operation simple and intuitive. Eight preset programmes including Fish, French fries, Keep warm, Meat, Small Pastries, Poultry, Preheat, and Shell fish make cooking various dishes effortless. The wide temperature range of 60-200°C ensures versatility in your cooking. The compact design with dimensions of 322 x 302 x 293 mm fits easily on your countertop.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/27402409_IN-Air-Fryer-MAF240B0IN-MAF240B5IN_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27265958_MAF240B5IN_Serie2_AirFryer_WalnutCake_FF_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27265956_MAF240B0IN_MAF240B5IN_Serie2_AirFryer_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27265957_MAF240B5IN_Serie2_AirFryer_cake_FF_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27265954_MAF240B0IN_MAF240B5IN_Serie2_AirFryer_side_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27265950_MAF240B0IN_MAF240B5IN_Serie2_AirFryer_Insert_Hand_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27265946_MAF240B0IN_MAF240B5IN_Serie2_AirFryer_Insert_Flow_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27265947_MAF240B0IN_MAF240B5IN_Serie2_AirFryer_fries_Schatten_def.webp"
            ],
            "stock": 20,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Frying Basket Capacity": "4.1 L",
                "Number of Baskets": "1",
                "Programmes": "Fish, French fries, Keep warm, Meat, Small Pastries, Poultry, Preheat, Shell fish",
                "Type of Control": "Touch Control",
                "Temperature Range": "60-200 °C",
                "Connection Rating": "1350 W",
                "Heating Type": "Top Heat",
                "Dimensions": "322 x 302 x 293 mm",
                "Color": "Black",
                "Series": "Series 2"
            },
            "key_features": [
                "4.1 litre capacity - Perfect for preparing meals for 2-3 people",
                "Eight preset programmes - Fish, French fries, Keep warm, Meat, Small Pastries, Poultry, Preheat, Shell fish",
                "Touch control panel for easy operation",
                "Wide temperature range: 60-200°C for versatile cooking",
                "Compact design fits easily on countertop",
                "Energy efficient 1350W heating",
                "Less oil needed for healthier cooking"
            ],
            "highlights": [
                "4.1L capacity perfect for small families",
                "8 convenient preset programmes",
                "Touch control for intuitive operation",
                "Energy efficient cooking"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.bosch-home.in/en/product/MAF240B5IN",
                    "title": "MAF240B5IN User Manual"
                },
                {
                    "type": "Product Specification Sheet",
                    "url": "https://www.bosch-home.in/en/product/MAF240B5IN",
                    "title": "MAF240B5IN Specifications"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 2 Air Fryer Black MAF240B0IN",
            "brand": "Bosch",
            "model_number": "MAF240B0IN",
            "category": "Uncategorized",
            "sub_category": "Air Fryer",
            "price": 12785.00,
            "description": "Experience healthy cooking with the Bosch Series 2 Air Fryer. Featuring a 4.1L capacity, this compact air fryer is perfect for preparing delicious meals with minimal oil.",
            "short_description": "Series 2 Air Fryer with 4.1L capacity, touch control, and eight preset programmes for easy cooking.",
            "long_description": "The Bosch Series 2 Air Fryer MAF240B0IN brings convenient and healthy cooking to your kitchen. With a 4.1 litre capacity, it's ideal for preparing meals for 2-3 people. The touch control panel makes operation simple and intuitive. Eight preset programmes including Fish, French fries, Keep warm, Meat, Small Pastries, Poultry, Preheat, and Shell fish make cooking various dishes effortless. The wide temperature range of 60-200°C ensures versatility in your cooking. The compact design with dimensions of 322 x 302 x 293 mm fits easily on your countertop.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/27402409_IN-Air-Fryer-MAF240B0IN-MAF240B5IN_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27265956_MAF240B0IN_MAF240B5IN_Serie2_AirFryer_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27265954_MAF240B0IN_MAF240B5IN_Serie2_AirFryer_side_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27265952_MAF240B0IN_Serie2_AirFryer_veggie_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27265950_MAF240B0IN_MAF240B5IN_Serie2_AirFryer_Insert_Hand_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27265946_MAF240B0IN_MAF240B5IN_Serie2_AirFryer_Insert_Flow_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27265947_MAF240B0IN_MAF240B5IN_Serie2_AirFryer_fries_Schatten_def.webp"
            ],
            "stock": 18,
            "rating": 5.0,
            "reviews_count": 1,
            "specifications": {
                "Frying Basket Capacity": "4.1 L",
                "Number of Baskets": "1",
                "Programmes": "Fish, French fries, Keep warm, Meat, Small Pastries, Poultry, Preheat, Shell fish",
                "Type of Control": "Touch Control",
                "Temperature Range": "60-200 °C",
                "Connection Rating": "1350 W",
                "Heating Type": "Top Heat",
                "Dimensions": "322 x 302 x 293 mm",
                "Color": "Black",
                "Series": "Series 2"
            },
            "key_features": [
                "4.1 litre capacity - Perfect for preparing meals for 2-3 people",
                "Eight preset programmes - Fish, French fries, Keep warm, Meat, Small Pastries, Poultry, Preheat, Shell fish",
                "Touch control panel for easy operation",
                "Wide temperature range: 60-200°C for versatile cooking",
                "Compact design fits easily on countertop",
                "Energy efficient 1350W heating",
                "Less oil needed for healthier cooking"
            ],
            "highlights": [
                "4.1L capacity perfect for small families",
                "8 convenient preset programmes",
                "Touch control for intuitive operation",
                "Energy efficient cooking"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.bosch-home.in/en/product/MAF240B0IN",
                    "title": "MAF240B0IN User Manual"
                },
                {
                    "type": "Product Specification Sheet",
                    "url": "https://www.bosch-home.in/en/product/MAF240B0IN",
                    "title": "MAF240B0IN Specifications"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    print("=" * 60)
    print("Adding Bosch Series 2 Air Fryers to Database")
    print("=" * 60)
    
    for product in products:
        # Check if product already exists
        existing = await products_collection.find_one({"model_number": product["model_number"]})
        if existing:
            print(f"⚠️  Product {product['model_number']} already exists. Skipping...")
            continue
        
        # Insert product
        result = await products_collection.insert_one(product)
        print(f"✅ Added: {product['name']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Price: ₹{product['price']:,.2f}")
        print(f"   Category: {product['category']}")
        print(f"   Images: {len(product['images'])} images")
        print(f"   Key Features: {len(product['key_features'])} features")
        print(f"   ID: {product['id']}")
        print()
    
    # Get total product count
    total_count = await products_collection.count_documents({})
    uncategorized_count = await products_collection.count_documents({"category": "Uncategorized"})
    air_fryer_count = await products_collection.count_documents({"sub_category": "Air Fryer"})
    
    print("=" * 60)
    print(f"✅ Series 2 Air Fryers added successfully!")
    print(f"Total products in database: {total_count}")
    print(f"Products in 'Uncategorized': {uncategorized_count}")
    print(f"Total Air Fryers: {air_fryer_count}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(add_series2_air_fryers())
