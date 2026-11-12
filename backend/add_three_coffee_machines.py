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

async def add_coffee_machines():
    """Add three Bosch Coffee Machine models to database"""
    
    products = [
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 8 Built-In Fully Automatic Coffee Machine Black CTL7181B0",
            "brand": "Bosch",
            "model_number": "CTL7181B0",
            "category": "Uncategorized",
            "sub_category": "Coffee Machine",
            "price": 349990.00,
            "description": "Discover international coffee specialties with the Bosch Series 8 Built-In Fully Automatic Coffee Machine. With Home Connect and integrated milk system, enjoy barista-quality coffee at home.",
            "short_description": "Series 8 Built-In Coffee Machine with Home Connect, integrated milk system, and international coffee specialties.",
            "long_description": "The Bosch Series 8 Built-In Fully Automatic Coffee Machine CTL7181B0 brings café-quality beverages to your kitchen. Featuring Home Connect technology for remote control via smartphone, this premium machine offers a wide range of international coffee specialties. The integrated milk system with hose ensures perfect milk froth for cappuccinos and lattes. With a 2.4L water container and 400g bean container capacity, enjoy multiple servings without frequent refills. The sleek black design seamlessly integrates into your kitchen cabinetry. Made in Europe with the highest quality standards.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/19924515_CTL7181B0_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/23058859_CTL7181B0_FlatWhite_PGA_D_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/23153812_CTL7181B0_flatwhite_display_PGA_D_def.webp",
                "https://media3.bsh-group.com/Line_Drawings/5120x/19656856_CT718L1B0_en-IN.webp",
                "https://media3.bsh-group.com/Line_Drawings/5120x/19478739_CT718L1B0_en-IN.webp"
            ],
            "stock": 5,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Built-In Fully Automatic",
                "Required Niche Size": "449 x 558 x 376 mm",
                "Water Container Capacity": "2.4 L",
                "Number of Bean Containers": "1",
                "Bean Container Capacity": "400 g",
                "Milk System": "Integrated milk system with hose",
                "Home Connect": "Yes",
                "Color": "Black",
                "Series": "Series 8",
                "Made in": "Europe"
            },
            "key_features": [
                "Coffee World - Discover international coffee specialties",
                "Home Connect - Control via smartphone",
                "Integrated milk system with hose for perfect milk froth",
                "2.4L water container capacity",
                "400g bean container capacity",
                "Built-in design for seamless kitchen integration",
                "Made in Europe with premium quality"
            ],
            "highlights": [
                "Discover international coffee specialties",
                "Home Connect enabled for remote control",
                "Integrated milk system for barista-quality drinks",
                "Premium Series 8 quality and design"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.bosch-home.in/en/product/filter-coffee-makers/built-in-fully-automatic-coffee-machines/CTL7181B0",
                    "title": "CTL7181B0 User Manual"
                },
                {
                    "type": "Product Specification Sheet",
                    "url": "https://www.bosch-home.in/en/product/filter-coffee-makers/built-in-fully-automatic-coffee-machines/CTL7181B0",
                    "title": "CTL7181B0 Specifications"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 2 Fully Automatic Coffee Machine VeroCafe Silk Silver TIE20301IN",
            "brand": "Bosch",
            "model_number": "TIE20301IN",
            "category": "Uncategorized",
            "sub_category": "Coffee Machine",
            "price": 77000.00,
            "original_price": 110000.00,
            "description": "Enjoy barista-quality coffee at home with the Bosch Series 2 VeroCafe. Featuring easy-to-use control panel, Calc'n Clean system, and durable Ceram Grinder for full aroma extraction.",
            "short_description": "Series 2 VeroCafe with Easy Select Panel, Calc'n Clean, and Ceram Grinder for consistent coffee quality.",
            "long_description": "The Bosch Series 2 Fully Automatic Coffee Machine VeroCafe TIE20301IN combines user-friendly design with advanced technology. The Easy Select Panel makes coffee selection intuitive, while the Calc'n Clean feature guides you through maintenance for long-lasting performance. The durable Ceram Grinder ensures full aroma extraction from every bean. One-touch cappuccino function makes milk-based beverages effortless - simply pour milk into a cup and let the machine do the rest. The seamless interplay of technology guarantees consistent coffee quality with every cup. Made in Europe with Bosch's renowned quality standards.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/20303272_TIE20301_STP_D_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/21861515_BSH-EN_BO_FAEM_812_TIE20301_General_SecImg-02_3200x1800px_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/21861516_BSH-EN_BO_FAEM_812_TIE20301_General_SecImg-03_3200x1800px_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/21861517_BSH-EN_BO_FAEM_812_TIE20301_General_SecImg-01_3200x1800px_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/21861531_BSH-EN_BO_FAEM_812_TIE20301_General_SecImg-05_3200x1800px_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/21861532_BSH-EN_BO_FAEM_812_TIE20301_General_SecImg-04_3200x1800px_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/21861533_BSH-EN_BO_FAEM_812_TIE20301_General_SecImg-06_3200x1800px_def.webp"
            ],
            "stock": 8,
            "rating": 3.0,
            "reviews_count": 1,
            "specifications": {
                "Type": "Fully Automatic",
                "Control Panel": "Easy Select Panel",
                "Grinder": "Ceram Grinder",
                "Cappuccino Function": "One-touch",
                "Cleaning": "Calc'n Clean",
                "Color": "Silk Silver",
                "Series": "Series 2 VeroCafe",
                "Made in": "Europe"
            },
            "key_features": [
                "Easy Select Panel for intuitive coffee selection",
                "Calc'n Clean - Guided descaling and cleaning",
                "Durable Ceram Grinder for full aroma extraction",
                "One-touch cappuccino function",
                "Seamless technology for consistent quality",
                "Made in Europe",
                "Limited stock offer - Save ₹33,000"
            ],
            "highlights": [
                "User-friendly design for easy coffee selection",
                "Convenient cleaning for long-lasting enjoyment",
                "Seamless technology for consistent coffee quality",
                "Durable Ceram Grinder ensures full aroma"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.bosch-home.in/en/product/filter-coffee-makers/fullyautomaticcoffeemachines/series2verocafe/TIE20301IN",
                    "title": "TIE20301IN User Manual"
                },
                {
                    "type": "Product Specification Sheet",
                    "url": "https://www.bosch-home.in/en/product/filter-coffee-makers/fullyautomaticcoffeemachines/series2verocafe/TIE20301IN",
                    "title": "TIE20301IN Specifications"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Fully Automatic Coffee Machine Vero Barista 600 Silver TIS65621IN",
            "brand": "Bosch",
            "model_number": "TIS65621IN",
            "category": "Uncategorized",
            "sub_category": "Coffee Machine",
            "price": 122500.00,
            "original_price": 175000.00,
            "description": "Experience barista-level coffee at home with the Bosch Series 6 Vero Barista 600. Features dual grinding system, automatic milk cleaning, ceramic grinders, and removable brewing unit.",
            "short_description": "Series 6 Vero Barista with dual grinding system, automatic milk cleaning, and ceramic grinders for café-quality coffee.",
            "long_description": "The Bosch Series 6 Fully Automatic Coffee Machine Vero Barista 600 TIS65621IN delivers premium coffee experiences. The unique dual grinding and brewing process creates extra-strong coffee with less bitterness. Automatic steam cleaning after every milk-based beverage ensures perfect hygiene without manual intervention. The long-lasting ceramic grinders unlock the perfect grind consistency every time. Calc'n Clean guides you through maintenance, while the removable brewing unit makes manual cleaning simple. Brew café-quality espresso, cappuccino, and latte at home with ease. Made in Europe with exceptional build quality.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02913434_J1036_2235675_TIS65621RW_korr_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/25870429_BSH-EN_BO_FAEM_812_TIS65621IN_General_Sec_Img-02_plain_3200x1800px_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/25870530_BSH-EN_BO_FAEM_812_TIS65621IN_General_Sec_Img-01_plain_3200x1800px_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/25870531_BSH-EN_BO_FAEM_812_TIS65621IN_General_Sec_Img-03_plain_3200x1800px_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/25870535_BSH-EN_BO_FAEM_812_TIS65621IN_General_Sec_Img-04_plain_3200x1800px_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/25870536_BSH-EN_BO_FAEM_812_TIS65621IN_General_Sec_Img-05_plain_3200x1800px_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/25870537_BSH-EN_BO_FAEM_812_TIS65621IN_General_Sec_Img-06_plain_3200x1800px_def.webp"
            ],
            "stock": 6,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Fully Automatic",
                "Grinding System": "Dual grinding and brewing",
                "Grinder": "Ceramic grinders",
                "Milk Cleaning": "Automatic steam cleaning",
                "Brewing Unit": "Removable",
                "Cleaning": "Calc'n Clean",
                "Color": "Silver",
                "Series": "Series 6 Vero Barista",
                "Made in": "Europe"
            },
            "key_features": [
                "Dual grinding and brewing for extra-strong coffee with less bitterness",
                "Automatic steam cleaning of milk system after every beverage",
                "Long-lasting ceramic grinders for perfect grind consistency",
                "Calc'n Clean guided maintenance",
                "Removable brewing unit for easy manual cleaning",
                "Made in Europe",
                "Limited stock offer - Save ₹52,500"
            ],
            "highlights": [
                "Extra strong coffee with less bitterness",
                "Automatic cleaning of milk system for perfect hygiene",
                "Perfectly ground every time for the perfect cup",
                "Convenient cleaning for long-lasting enjoyment"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.bosch-home.in/en/product/filter-coffee-makers/fullyautomaticcoffeemachines/series6verocafe/TIS65621IN",
                    "title": "TIS65621IN User Manual"
                },
                {
                    "type": "Product Specification Sheet",
                    "url": "https://www.bosch-home.in/en/product/filter-coffee-makers/fullyautomaticcoffeemachines/series6verocafe/TIS65621IN",
                    "title": "TIS65621IN Specifications"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    print("=" * 70)
    print("Adding Bosch Coffee Machines to Database")
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
        if 'original_price' in product:
            savings = product['original_price'] - product['price']
            print(f"   Original Price: ₹{product['original_price']:,.2f} (Save ₹{savings:,.2f})")
        print(f"   Category: {product['category']}")
        print(f"   Sub-category: {product['sub_category']}")
        print(f"   Images: {len(product['images'])} images")
        print(f"   Key Features: {len(product['key_features'])} features")
        print(f"   ID: {product['id']}")
    
    # Get total product count
    total_count = await products_collection.count_documents({})
    uncategorized_count = await products_collection.count_documents({"category": "Uncategorized"})
    coffee_count = await products_collection.count_documents({"sub_category": "Coffee Machine"})
    
    print("\n" + "=" * 70)
    print(f"✅ Coffee Machines added successfully!")
    print(f"Total products in database: {total_count}")
    print(f"Products in 'Uncategorized': {uncategorized_count}")
    print(f"Total Coffee Machines: {coffee_count}")
    print("=" * 70)
    print("\n⚠️  NOTE: Coffee machines are high-priced items.")
    print("   Products over ₹100,000 may be filtered on frontend for display.")

if __name__ == "__main__":
    asyncio.run(add_coffee_machines())
