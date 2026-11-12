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

async def add_air_fryers():
    """Add two Bosch Series 6 Air Fryer models to database"""
    
    products = [
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Air Fryer Black MAF671B5IN",
            "brand": "Bosch",
            "model_number": "MAF671B5IN",
            "category": "Uncategorized",
            "sub_category": "Air Fryer",
            "price": 18545.00,
            "description": "Experience guilt-free fried food with the Bosch Series 6 Air Fryer. Featuring a spacious 7.2L capacity, this air fryer comfortably cooks up to 5 portions for the whole family.",
            "short_description": "Series 6 Air Fryer with 7.2L capacity, illuminated window, and dishwasher-safe parts for easy cleaning.",
            "long_description": "The Bosch Series 6 Air Fryer MAF671B5IN brings healthy cooking to your kitchen with its innovative design. With a generous 7.2 litre capacity, you can prepare meals for the entire family. The illuminated window lets you monitor cooking progress without opening the basket, while the touch control panel offers intuitive operation. Seven preset programmes make cooking fish, meat, vegetables, and more incredibly simple. The compact basket and removable grid are dishwasher-safe for effortless cleaning.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/25767357_MAF671B0GB_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27289805_MAF671B5IN_AirFryer_Careline_top_open_cake_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27289804_MAF671B5IN_Serie6_AirFryer_4L_AF-03062025_Tray_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27289803_MAF671B0IN_MAF671B5IN_Serie6_AirFryer_Visual_fries_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27289799_MAF671B0IN_MAF671B5IN_Serie6_AirFryer_front_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27289797_MAF671B0IN_MAF671B5IN_Serie6_AirFryer_front_open_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27289791_MAF671B0IN_MAF671B5IN_Serie6_AirFryer_screenshot_def.webp"
            ],
            "stock": 15,
            "rating": 5.0,
            "reviews_count": 1,
            "specifications": {
                "Frying Basket Capacity": "7.2 L",
                "Number of Baskets": "1",
                "Programmes": "Bread, Fish, French fries, Keep warm, Meat, Small Pastries, Poultry, Vegetables",
                "Type of Control": "Touch Control",
                "Temperature Range": "40-200 °C",
                "Connection Rating": "1800 W",
                "Heating Type": "Top Heat",
                "Dimensions": "370 x 348 x 355 mm",
                "Color": "Black",
                "Series": "Series 6",
                "Dishwasher Safe Parts": "Yes",
                "Illuminated Window": "Yes"
            },
            "key_features": [
                "7.2 litre capacity - Comfortably cook up to 5 portions for the whole family",
                "Quicker clean ups - The compact basket and removable grid, easily cleaned under the tap or in the dishwasher",
                "Stay in control - Keep an eye on your cooking through an illuminated window",
                "Less oil needed - Without sacrificing any of the flavour",
                "Seven presets - Easily guides your cooking from fish and meat to vegetables",
                "Touch control panel for intuitive operation",
                "Temperature range: 40-200°C for versatile cooking"
            ],
            "highlights": [
                "Whip up meals for everyone with its spacious 7.2L capacity",
                "Quick, hassle-free cleaning with dishwasher-safe parts",
                "Illuminated window: Effortlessly monitor your cooking",
                "Enjoy fried food without the guilt"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.bosch-home.in/en/product/MAF671B5IN",
                    "title": "MAF671B5IN User Manual"
                },
                {
                    "type": "Product Specification Sheet",
                    "url": "https://www.bosch-home.in/en/product/MAF671B5IN",
                    "title": "MAF671B5IN Specifications"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Air Fryer Black MAF671B0IN",
            "brand": "Bosch",
            "model_number": "MAF671B0IN",
            "category": "Uncategorized",
            "sub_category": "Air Fryer",
            "price": 17555.00,
            "description": "Experience guilt-free fried food with the Bosch Series 6 Air Fryer. Featuring a spacious 7.2L capacity, this air fryer comfortably cooks up to 5 portions for the whole family.",
            "short_description": "Series 6 Air Fryer with 7.2L capacity, illuminated window, and dishwasher-safe parts for easy cleaning.",
            "long_description": "The Bosch Series 6 Air Fryer MAF671B0IN brings healthy cooking to your kitchen with its innovative design. With a generous 7.2 litre capacity, you can prepare meals for the entire family. The illuminated window lets you monitor cooking progress without opening the basket, while the touch control panel offers intuitive operation. Seven preset programmes make cooking fish, meat, vegetables, and more incredibly simple. The compact basket and removable grid are dishwasher-safe for effortless cleaning.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/25767357_MAF671B0GB_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27289803_MAF671B0IN_MAF671B5IN_Serie6_AirFryer_Visual_fries_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27289805_MAF671B5IN_AirFryer_Careline_top_open_cake_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27289799_MAF671B0IN_MAF671B5IN_Serie6_AirFryer_front_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27289797_MAF671B0IN_MAF671B5IN_Serie6_AirFryer_front_open_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/27289791_MAF671B0IN_MAF671B5IN_Serie6_AirFryer_screenshot_def.webp"
            ],
            "stock": 20,
            "rating": 5.0,
            "reviews_count": 2,
            "specifications": {
                "Frying Basket Capacity": "7.2 L",
                "Number of Baskets": "1",
                "Programmes": "Bread, Fish, French fries, Keep warm, Meat, Small Pastries, Poultry, Vegetables",
                "Type of Control": "Touch Control",
                "Temperature Range": "40-200 °C",
                "Connection Rating": "1800 W",
                "Heating Type": "Top Heat",
                "Dimensions": "370 x 348 x 355 mm",
                "Color": "Black",
                "Series": "Series 6",
                "Dishwasher Safe Parts": "Yes",
                "Illuminated Window": "Yes"
            },
            "key_features": [
                "7.2 litre capacity - Comfortably cook up to 5 portions for the whole family",
                "Quicker clean ups - The compact basket and removable grid, easily cleaned under the tap or in the dishwasher",
                "Stay in control - Keep an eye on your cooking through an illuminated window",
                "Less oil needed - Without sacrificing any of the flavour",
                "Seven presets - Easily guides your cooking from fish and meat to vegetables",
                "Touch control panel for intuitive operation",
                "Temperature range: 40-200°C for versatile cooking"
            ],
            "highlights": [
                "Whip up meals for everyone with its spacious 7.2L capacity",
                "Quick, hassle-free cleaning with dishwasher-safe parts",
                "Illuminated window: Effortlessly monitor your cooking",
                "Enjoy fried food without the guilt"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.bosch-home.in/en/product/MAF671B0IN",
                    "title": "MAF671B0IN User Manual"
                },
                {
                    "type": "Product Specification Sheet",
                    "url": "https://www.bosch-home.in/en/product/MAF671B0IN",
                    "title": "MAF671B0IN Specifications"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    print("=" * 60)
    print("Adding Bosch Air Fryers to Database")
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
    
    print("=" * 60)
    print(f"✅ Air Fryers added successfully!")
    print(f"Total products in database: {total_count}")
    print(f"Products in 'Uncategorized': {uncategorized_count}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(add_air_fryers())
