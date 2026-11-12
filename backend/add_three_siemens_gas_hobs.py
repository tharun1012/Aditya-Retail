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

async def add_siemens_gas_hobs():
    """Add three Siemens Gas Hob models to database"""
    
    products = [
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ700 Gas Hob 90 cm Ceramic Black ER9A6SD70I",
            "brand": "Siemens",
            "model_number": "ER9A6SD70I",
            "category": "Gas Hob",
            "sub_category": "90 cm Gas Hob",
            "price": 149990.00,
            "description": "Premium Siemens iQ700 Gas Hob featuring stepFlame Technology, ceramic surface, and 5 burner positions. Designed for professional-level cooking performance.",
            "short_description": "iQ700 90 cm Gas Hob with stepFlame Technology, ceramic surface, and cast iron pan supports with rubber feet.",
            "long_description": "The Siemens iQ700 Gas Hob ER9A6SD70I represents the pinnacle of gas cooking technology. Featuring stepFlame Technology for precise flame control across 5 burner positions, this 90 cm hob offers exceptional cooking versatility. The elegant black ceramic surface combines premium aesthetics with easy cleaning. Cast iron pan supports with rubber feet provide stability and protection for your cookware. The design frame adds a sophisticated touch to your kitchen. Compatible with both liquid gas (G30,31 28-30/37 mbar) and includes nozzle set for natural gas (H/E/(L) 20 (25) mbar). Perfect for those who demand professional-grade performance at home.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01657010_ER9A6SD70_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01775585_ER3A6AD70_GasHob_build-in_Siemens_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01835308_ER9A6SD70_GasHob_build-in_Siemens_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01835309_ER9A6SD70_GasHob_build-in_Bosch_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01835311_ER9A6SD70_GasHob_build-in_Siemens_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01790030_ER9A6SD70_GasHob_build-in_Siemens_PGA5_def.webp"
            ],
            "stock": 8,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Cooktop Type": "Gas cooktop",
                "Number of Burners": "5",
                "stepFlame Technology": "Yes",
                "Frame Type": "Design frame",
                "Surface Material": "Ceramic",
                "Pan Supports": "Cast iron with rubber feet",
                "Gas Type Preset": "Liquid gas G30,31 28-30/37 mbar",
                "Alternative Gas": "Natural gas H/E/(L) 20 (25) mbar",
                "Width": "90 cm",
                "Color": "Black",
                "Series": "iQ700"
            },
            "key_features": [
                "stepFlame Technology for precise flame control",
                "5 burner positions for versatile cooking",
                "Premium black ceramic surface",
                "Cast iron pan supports with rubber feet for stability",
                "Design frame for elegant aesthetics",
                "Compatible with liquid gas and natural gas",
                "Easy to clean ceramic surface",
                "Professional-grade performance"
            ],
            "highlights": [
                "stepFlame Technology for ultimate control",
                "5 burner positions for maximum versatility",
                "Premium ceramic surface - elegant and easy to clean",
                "Cast iron pan supports for cookware stability"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/hobs-and-cooktops/gas-stoves/ER9A6SD70I",
                    "title": "ER9A6SD70I User Manual"
                },
                {
                    "type": "Product Specification Sheet",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/hobs-and-cooktops/gas-stoves/ER9A6SD70I",
                    "title": "ER9A6SD70I Specifications"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ500 Gas Hob 90 cm Stainless Steel EC9A5RB90I",
            "brand": "Siemens",
            "model_number": "EC9A5RB90I",
            "category": "Gas Hob",
            "sub_category": "90 cm Gas Hob",
            "price": 102990.00,
            "description": "Siemens iQ500 Gas Hob with frameless design, stainless steel surface, and stepFlame Technology. Features 5 burner positions for efficient cooking.",
            "short_description": "iQ500 90 cm Frameless Gas Hob with stainless steel finish, stepFlame Technology, and 5 burner positions.",
            "long_description": "The Siemens iQ500 Gas Hob EC9A5RB90I combines modern design with practical functionality. The frameless construction creates a sleek, contemporary look while the stainless steel surface ensures durability and easy maintenance. stepFlame Technology provides precise flame control across all 5 burner positions, allowing you to adjust heat levels with exceptional accuracy. Cast iron pan supports with rubber feet offer excellent stability for pots and pans. The hob comes preset for liquid gas (G30,31 28-30/37 mbar) and includes a nozzle set for natural gas conversion (H/E/(L) 20 (25) mbar). Ideal for modern kitchens seeking both style and performance.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01657122_EC9A5RB90_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01837540_EC9A5RB90_GasHob_build-in_Siemens_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01797919_EC6A5PB90_GasHob_build-in_Siemens_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01837546_EC9A5RB90_GasHob_build-in_Siemens_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01833608_EC7A5RB90_GasHob_build-in_Siemens_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01791826_EC9A5RB90_GasHob_build-in_Siemens_PGA5_def.webp"
            ],
            "stock": 12,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Cooktop Type": "Gas cooktop",
                "Number of Burners": "5",
                "stepFlame Technology": "Yes",
                "Frame Type": "Frameless",
                "Surface Material": "Stainless steel",
                "Pan Supports": "Cast iron with rubber feet",
                "Gas Type Preset": "Liquid gas G30,31 28-30/37 mbar",
                "Alternative Gas": "Natural gas H/E/(L) 20 (25) mbar",
                "Width": "90 cm",
                "Color": "Stainless Steel",
                "Series": "iQ500"
            },
            "key_features": [
                "stepFlame Technology for precise control",
                "Frameless design for modern aesthetics",
                "Durable stainless steel surface",
                "5 burner positions for versatile cooking",
                "Cast iron pan supports with rubber feet",
                "Compatible with liquid and natural gas",
                "Easy to clean and maintain",
                "Contemporary kitchen integration"
            ],
            "highlights": [
                "Frameless design for sleek appearance",
                "stepFlame Technology for precise cooking",
                "Stainless steel - durable and easy to clean",
                "5 burner cooking flexibility"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/hobs-and-cooktops/gas-stoves/EC9A5RB90I",
                    "title": "EC9A5RB90I User Manual"
                },
                {
                    "type": "Product Specification Sheet",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/hobs-and-cooktops/gas-stoves/EC9A5RB90I",
                    "title": "EC9A5RB90I Specifications"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ500 Gas Hob 90 cm Tempered Glass Black EP9B6VG20I",
            "brand": "Siemens",
            "model_number": "EP9B6VG20I",
            "category": "Gas Hob",
            "sub_category": "90 cm Gas Hob",
            "price": 89990.00,
            "description": "Siemens iQ500 Gas Hob featuring tempered glass surface, sword knobs, and individual cast-iron pan supports. Modern design with 5 burner positions.",
            "short_description": "iQ500 90 cm Gas Hob with tempered glass surface, sword knobs for easy use, and individual cast-iron pan supports.",
            "long_description": "The Siemens iQ500 Gas Hob EP9B6VG20I brings modern elegance to your kitchen with its black tempered glass surface. The sword knobs combine highest ease of use with modern design, making operation intuitive and comfortable. Individual cast-iron pan supports provide excellent stability and demonstrate high-quality materials and workmanship. The tempered glass surface is extremely heat-resistant and easy to clean, maintaining its pristine appearance even with regular use. With 5 burner positions, you have ample space for multiple pots and pans. Preset for liquid gas (G30,31 28-30/37 mbar) with included nozzle set for natural gas (H/E/(L) 20 (25) mbar). Perfect for those seeking a balance of style, functionality, and value.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/21344097_EP9B6VG20I_STP_def.webp"
            ],
            "stock": 15,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Cooktop Type": "Gas cooktop",
                "Number of Burners": "5",
                "stepFlame Technology": "No",
                "Surface Material": "Tempered glass",
                "Pan Supports": "Cast iron single (individual)",
                "Knob Type": "Sword knob",
                "Gas Type Preset": "Liquid gas G30,31 28-30/37 mbar",
                "Alternative Gas": "Natural gas H/E/(L) 20 (25) mbar",
                "Width": "90 cm",
                "Color": "Black",
                "Series": "iQ500"
            },
            "key_features": [
                "Modern black tempered glass surface",
                "Sword knobs for ease of use and modern design",
                "Individual cast-iron pan supports for stability",
                "5 burner positions for cooking versatility",
                "Extremely heat-resistant tempered glass",
                "Easy to clean surface",
                "Compatible with liquid and natural gas",
                "High-quality materials and workmanship"
            ],
            "highlights": [
                "Individual cast-iron pan supports for quality and stability",
                "Sword knob combines ease of use with modern design",
                "Black tempered glass - heat-resistant and easy to clean"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/hobs-and-cooktops/gas-stoves/EP9B6VG20I",
                    "title": "EP9B6VG20I User Manual"
                },
                {
                    "type": "Product Specification Sheet",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/hobs-and-cooktops/gas-stoves/EP9B6VG20I",
                    "title": "EP9B6VG20I Specifications"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    print("=" * 70)
    print("Adding Siemens Gas Hobs to Database")
    print("=" * 70)
    
    for product in products:
        # Check if product already exists
        existing = await products_collection.find_one({"model_number": product["model_number"]})
        if existing:
            print(f"⚠️  Product {product['model_number']} already exists. Skipping...")
            continue
        
        # Insert product
        result = await products_collection.insert_one(product)
        print(f"\n✅ Added: {product['name']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Price: ₹{product['price']:,.2f}")
        print(f"   Category: {product['category']}")
        print(f"   Sub-category: {product['sub_category']}")
        print(f"   Images: {len(product['images'])} images")
        print(f"   Key Features: {len(product['key_features'])} features")
        print(f"   ID: {product['id']}")
    
    # Get total product count
    total_count = await products_collection.count_documents({})
    gas_hob_count = await products_collection.count_documents({"category": "Gas Hob"})
    siemens_count = await products_collection.count_documents({"brand": "Siemens"})
    
    print("\n" + "=" * 70)
    print(f"✅ Siemens Gas Hobs added successfully!")
    print(f"Total products in database: {total_count}")
    print(f"Total Gas Hobs: {gas_hob_count}")
    print(f"Total Siemens products: {siemens_count}")
    print("=" * 70)
    print("\n⚠️  NOTE: Gas hobs are high-priced items.")
    print("   Products over ₹100,000 may be filtered on frontend for display.")

if __name__ == "__main__":
    asyncio.run(add_siemens_gas_hobs())
