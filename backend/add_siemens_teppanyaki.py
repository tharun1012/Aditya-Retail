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

async def add_teppanyaki():
    """Add Siemens Teppanyaki Domino Hob to database"""
    
    product = {
        "id": str(uuid.uuid4()),
        "name": "Siemens iQ500 Modular Teppanyaki 40 cm ET475FYB1E",
        "brand": "Siemens",
        "model_number": "ET475FYB1E",
        "category": "Induction Hob",
        "sub_category": "Domino Hob",
        "price": 219990.00,
        "description": "Premium Siemens iQ500 Teppanyaki griddle with 40 cm width, 2 independently controlled cooking zones, touchSlider control, and keep warm function.",
        "short_description": "iQ500 40 cm Teppanyaki griddle with 2 zones, touchSlider control, and keep warm at 70°C.",
        "long_description": "The Siemens iQ500 Modular Teppanyaki ET475FYB1E brings Japanese-style griddle cooking to your kitchen. This premium 40 cm wide teppanyaki is ideal for combining with other Domino or faceted design cooktops, allowing for complete cooking customization. The two cooking zones can be heated together or separately depending on your requirements and quantities, offering maximum flexibility. The intuitive touchSlider allows precise power level control with one touch. The keep warm setting maintains dishes at a perfect 70°C, while the cleaning function heats to 40°C for easier removal of grease deposits. Perfect for preparing vegetables, seafood, meat, and more with authentic teppanyaki-style cooking.",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/5120x/MCSA00999544_623100_ET475FYB1E_def.webp",
            "https://media3.bsh-group.com/Product_Shots/5120x/MCSA00999552_623101_ET475FYB1E_mitDeckel_def.webp",
            "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01074641_DA2_ET475FYB1E_def.webp",
            "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01058954_DA3_ET675LMP1D_Top_Siemens_Facette_vorne_def.webp",
            "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01752943_ET475FYB1E_ElectricHob_Siemens_PGA3_def.webp",
            "https://media3.bsh-group.com/Product_Shots/5120x/MCSA03035105_118193__BSH_Siemens_kitchen__stills_scene_10_def.webp"
        ],
        "stock": 4,
        "rating": 0.0,
        "reviews_count": 0,
        "specifications": {
            "Type": "Teppanyaki griddle",
            "Width": "40 cm",
            "Number of Cooking Zones": "2",
            "Controls": "touchSlider",
            "Keep Warm Temperature": "70°C",
            "Cleaning Temperature": "40°C",
            "Color": "Black",
            "Series": "iQ500",
            "Modular Design": "Yes"
        },
        "key_features": [
            "40 cm width - ideal for combining with Domino cooktops",
            "2 independent cooking zones for flexibility",
            "touchSlider for precise power control",
            "Keep warm setting at 70°C",
            "Cleaning mode at 40°C for easy grease removal",
            "Zones can be heated together or separately",
            "Authentic Japanese-style griddle cooking",
            "Perfect for vegetables, seafood, and meat"
        ],
        "highlights": [
            "40 cm wide teppanyaki for modular kitchens",
            "2 cooking zones with independent control",
            "Temperature control at your fingertips",
            "Keep warm setting at 70°C"
        ],
        "documents": [
            {
                "type": "User Manual",
                "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/hobs-and-cooktops/domino-cooktops/ET475FYB1E",
                "title": "ET475FYB1E User Manual"
            },
            {
                "type": "Product Specification Sheet",
                "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/hobs-and-cooktops/domino-cooktops/ET475FYB1E",
                "title": "ET475FYB1E Specifications"
            }
        ],
        "warranty": "2 years manufacturer warranty",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    print("=" * 70)
    print("Adding Siemens Teppanyaki to Database")
    print("=" * 70)
    
    # Check if product already exists
    existing = await products_collection.find_one({"model_number": product["model_number"]})
    if existing:
        print(f"⚠️  Product {product['model_number']} already exists. Skipping...")
        return
    
    # Insert product
    result = await products_collection.insert_one(product)
    print(f"\n✅ Added: {product['name']}")
    print(f"   Model: {product['model_number']}")
    print(f"   Price: ₹{product['price']:,.2f}")
    print(f"   Category: {product['category']}")
    print(f"   Sub-category: {product['sub_category']}")
    print(f"   Images: {len(product['images'])} images")
    print(f"   ID: {product['id']}")
    
    # Get total product count
    total_count = await products_collection.count_documents({})
    induction_count = await products_collection.count_documents({"category": "Induction Hob"})
    siemens_count = await products_collection.count_documents({"brand": "Siemens"})
    filtered_count = await products_collection.count_documents({"price": {"$gt": 100000}})
    
    print("\n" + "=" * 70)
    print(f"✅ Teppanyaki added successfully!")
    print(f"Total products in database: {total_count}")
    print(f"Total Induction Hobs: {induction_count}")
    print(f"Total Siemens products: {siemens_count}")
    print(f"High-priced products (>₹100k): {filtered_count}")
    print(f"Visible on frontend: {total_count - filtered_count}")
    print("=" * 70)
    print("\n⚠️  NOTE: This premium product (₹2,19,990) will be filtered on frontend.")

if __name__ == "__main__":
    asyncio.run(add_teppanyaki())
