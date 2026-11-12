import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

load_dotenv()

async def add_five_microwave_products():
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 80)
    print("➕ ADDING 5 BOSCH MICROWAVE/COMPACT OVEN PRODUCTS")
    print("=" * 80)
    
    products = [
        # Product 1: CMA585MB0I - Compact Oven with Microwave
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Serie 6 Built-in Microwave Oven with Hot Air 60 x 45 cm Black",
            "brand": "Bosch",
            "series": "Serie 6",
            "category": "Built-in Microwaves",
            "model": "CMA585MB0I",
            "sku": "BSH-CMA585MB0I",
            "price": 125990,
            "original_price": 139990,
            "description": "Bosch Serie 6 Compact Built-in Microwave Oven with hot air function, 44L capacity, 900W microwave power, stainless steel interior, LED lighting, and hydrolytic cleaning. Features 15 automatic programs and 5 power levels for versatile cooking.",
            "short_description": "44L Compact Microwave Oven with Hot Air - Black",
            "image": "https://media3.bsh-group.com/Product_Shots/5120x/23600131_CMA585MB0_CompactOven_Bosch_STP_def.webp",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/23600131_CMA585MB0_CompactOven_Bosch_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02853914_CMA585MB0_Bosch_Compact_Mikrowelle_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02853916_CMA585MB0_Bosch_Compact_Mikrowelle_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02853919_CMA585MB0_Bosch_Compact_Mikrowelle_PGA3_def.webp"
            ],
            "technical_overview": {
                "Installation Typology": "Built-in into the cabinet",
                "Max. Microwave Power Level": "900 W",
                "Main Colour of Product": "Black",
                "Cavity Capacity": "44 L",
                "Integrated Cleaning System": "Hydrolytic",
                "Number of Automatic Programmes": "15",
                "Number of Power Levels": "5"
            },
            "highlights": [
                {"title": "Interior shining with steel", "description": "Easy to clean stainless steel interior thanks to smooth surfaces and no sharp edges."},
                {"title": "Brighten up your cooking with LED lighting!", "description": "Perfect illumination of foods with minimum energy consumption using advanced LED technology."},
                {"title": "Easy cleaning in between", "description": "Cleaning Assistance feature for less cleaning effort, especially useful for light soiling."}
            ],
            "features": [
                "Stainless steel interior - easy to clean with smooth surfaces",
                "LED lighting - perfect illumination with minimum energy",
                "Cleaning Assistance - less effort for light soiling",
                "44L spacious cavity",
                "900W microwave power",
                "15 automatic programs",
                "5 power levels",
                "Hot air function for baking and roasting"
            ],
            "spec_groups": {
                "general": {"Brand": "Bosch", "Series": "Serie 6", "Model": "CMA585MB0I", "Product Type": "Compact Microwave Oven with Hot Air", "Color": "Black"},
                "size_weight": {"Product Height": "455 mm", "Product Width": "594 mm", "Product Depth": "548 mm", "Net Weight": "30 kg (approx)"},
                "technical": {"Capacity": "44 Litres", "Microwave Power": "900 W", "Power Levels": "5", "Automatic Programs": "15", "Heating Types": "Microwave + Hot Air"},
                "comfort": {"Cleaning System": "Hydrolytic + Cleaning Assistance", "Interior": "Stainless Steel", "Lighting": "LED", "Control": "Electronic"},
                "connectivity": {"Smart Features": "None", "WiFi": "No"}
            },
            "documents": [
                {"title": "User Manual", "type": "manual", "url": "#", "size": "PDF - 2.8 MB"},
                {"title": "Product Specification Sheet", "type": "specs", "url": "#", "size": "PDF - 780 KB"},
                {"title": "Installation Instructions", "type": "installation", "url": "#", "size": "PDF - 1.5 MB"}
            ],
            "reviews": [
                {"name": "Priya Menon", "rating": 5, "date": "23 Jan 2025", "comment": "Perfect combination of microwave and oven! The hot air function is great for baking. LED lighting is very helpful."},
                {"name": "Rajiv Kumar", "rating": 4, "date": "18 Jan 2025", "comment": "Good product. Stainless steel interior is easy to maintain. 44L capacity is sufficient for family use."}
            ],
            "specifications": {"Brand": "Bosch", "Series": "Serie 6", "Model": "CMA585MB0I", "Capacity": "44 Litres", "Warranty": "2 Years"},
            "stock_quantity": 8, "reorder_level": 3, "is_featured": True, "customer_rating": 4.6, "review_count": 67,
            "fast_moving": True, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow(),
            "warranty": "2 years standard warranty", "energy_rating": "A"
        },
        
        # Product 2: BEL550MS0I - Built-in Microwave
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Serie 2 Built-in Microwave 60 x 38 cm Stainless Steel",
            "brand": "Bosch",
            "series": "Serie 2",
            "category": "Built-in Microwaves",
            "model": "BEL550MS0I",
            "sku": "BSH-BEL550MS0I",
            "price": 36990,
            "original_price": 40990,
            "description": "Bosch Serie 2 Built-in Microwave with 20L capacity, 800W power, electronic control, and 5 power levels. Compact design perfect for small to medium families with auto programs and defrost function.",
            "short_description": "20L Built-in Microwave - Stainless Steel",
            "image": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02104886_BEL550MS0_def.webp",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02104886_BEL550MS0_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02104887_BEL550MS0_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02104888_BEL550MS0_def.webp"
            ],
            "technical_overview": {
                "Max. Microwave Power": "800 W",
                "Cavity Capacity": "20 L",
                "Main Colour": "Stainless Steel",
                "Power Levels": "5",
                "Control Type": "Electronic"
            },
            "highlights": [
                {"title": "Compact and Efficient", "description": "20L capacity perfect for everyday reheating and cooking needs in modern kitchens."},
                {"title": "Easy Electronic Control", "description": "Simple electronic controls make operation effortless for all family members."}
            ],
            "features": ["800W microwave power", "20L capacity", "5 power levels", "Electronic control", "Auto programs", "Defrost function", "Stainless steel finish"],
            "spec_groups": {
                "general": {"Brand": "Bosch", "Series": "Serie 2", "Model": "BEL550MS0I", "Color": "Stainless Steel"},
                "size_weight": {"Height": "382 mm", "Width": "594 mm", "Depth": "317 mm", "Weight": "15 kg"},
                "technical": {"Capacity": "20 L", "Power": "800 W", "Power Levels": "5"},
                "comfort": {"Control": "Electronic", "Interior": "Easy Clean"},
                "connectivity": {"Smart Features": "None"}
            },
            "documents": [{"title": "User Manual", "type": "manual", "url": "#", "size": "PDF - 1.8 MB"}],
            "reviews": [{"name": "Anita Sharma", "rating": 4, "date": "20 Jan 2025", "comment": "Good basic microwave. Perfect for reheating and simple cooking. Value for money!"}],
            "specifications": {"Brand": "Bosch", "Series": "Serie 2", "Model": "BEL550MS0I", "Capacity": "20 L", "Warranty": "2 Years"},
            "stock_quantity": 15, "reorder_level": 5, "is_featured": False, "customer_rating": 4.2, "review_count": 45,
            "fast_moving": False, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow(), "warranty": "2 years", "energy_rating": "Standard"
        },
        
        # Product 3: BEL553MB0I - Built-in Microwave Black
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Serie 2 Built-in Microwave 60 x 38 cm Black",
            "brand": "Bosch",
            "series": "Serie 2",
            "category": "Built-in Microwaves",
            "model": "BEL553MB0I",
            "sku": "BSH-BEL553MB0I",
            "price": 38990,
            "original_price": 42990,
            "description": "Bosch Serie 2 Built-in Microwave in elegant black finish with 20L capacity, 800W power, touch control, and LED display. Features 5 power levels and auto programs for convenient cooking.",
            "short_description": "20L Built-in Microwave with Touch Control - Black",
            "image": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02104880_BEL553MB0_def.webp",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02104880_BEL553MB0_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02104881_BEL553MB0_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02104882_BEL553MB0_def.webp"
            ],
            "technical_overview": {"Power": "800 W", "Capacity": "20 L", "Colour": "Black", "Power Levels": "5", "Control": "Touch Control with LED Display"},
            "highlights": [
                {"title": "Modern Touch Control", "description": "Easy touch control with LED display for modern kitchen aesthetics."},
                {"title": "Elegant Black Design", "description": "Sleek black finish complements contemporary kitchen designs."}
            ],
            "features": ["800W microwave power", "20L capacity", "Touch control with LED display", "5 power levels", "Auto programs", "Black glass finish", "Easy to clean"],
            "spec_groups": {
                "general": {"Brand": "Bosch", "Series": "Serie 2", "Model": "BEL553MB0I", "Color": "Black"},
                "size_weight": {"Height": "382 mm", "Width": "594 mm", "Depth": "317 mm", "Weight": "15 kg"},
                "technical": {"Capacity": "20 L", "Power": "800 W", "Power Levels": "5", "Display": "LED"},
                "comfort": {"Control": "Touch Control", "Interior": "Easy Clean"},
                "connectivity": {"Smart Features": "None"}
            },
            "documents": [{"title": "User Manual", "type": "manual", "url": "#", "size": "PDF - 1.8 MB"}],
            "reviews": [{"name": "Deepak Verma", "rating": 4, "date": "19 Jan 2025", "comment": "Nice black microwave. Touch controls work well. Good for modern kitchens."}],
            "specifications": {"Brand": "Bosch", "Series": "Serie 2", "Model": "BEL553MB0I", "Capacity": "20 L", "Warranty": "2 Years"},
            "stock_quantity": 12, "reorder_level": 5, "is_featured": False, "customer_rating": 4.3, "review_count": 38,
            "fast_moving": False, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow(), "warranty": "2 years", "energy_rating": "Standard"
        },
        
        # Product 4: BEL553MS0I - Built-in Microwave Stainless Steel
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Serie 2 Built-in Microwave 60 x 38 cm Stainless Steel with LED Display",
            "brand": "Bosch",
            "series": "Serie 2",
            "category": "Built-in Microwaves",
            "model": "BEL553MS0I",
            "sku": "BSH-BEL553MS0I",
            "price": 38990,
            "original_price": 42990,
            "description": "Bosch Serie 2 Built-in Microwave in stainless steel with 20L capacity, 800W power, touch control, and LED display. Perfect blend of style and functionality for modern kitchens.",
            "short_description": "20L Microwave with Touch Control & LED Display - Stainless Steel",
            "image": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02104883_BEL553MS0_def.webp",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02104883_BEL553MS0_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02104884_BEL553MS0_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02104885_BEL553MS0_def.webp"
            ],
            "technical_overview": {"Power": "800 W", "Capacity": "20 L", "Colour": "Stainless Steel", "Power Levels": "5", "Control": "Touch Control with LED"},
            "highlights": [
                {"title": "Premium Stainless Steel Finish", "description": "Durable stainless steel exterior that's easy to maintain and looks great."},
                {"title": "LED Display Control", "description": "Modern touch control with clear LED display for easy operation."}
            ],
            "features": ["800W power", "20L capacity", "Touch control with LED", "5 power levels", "Auto programs", "Stainless steel finish", "Easy maintenance"],
            "spec_groups": {
                "general": {"Brand": "Bosch", "Series": "Serie 2", "Model": "BEL553MS0I", "Color": "Stainless Steel"},
                "size_weight": {"Height": "382 mm", "Width": "594 mm", "Depth": "317 mm", "Weight": "15 kg"},
                "technical": {"Capacity": "20 L", "Power": "800 W", "Power Levels": "5", "Display": "LED"},
                "comfort": {"Control": "Touch Control", "Interior": "Easy Clean"},
                "connectivity": {"Smart Features": "None"}
            },
            "documents": [{"title": "User Manual", "type": "manual", "url": "#", "size": "PDF - 1.8 MB"}],
            "reviews": [{"name": "Kavita Reddy", "rating": 4, "date": "17 Jan 2025", "comment": "Good microwave with modern features. Stainless steel looks premium. Touch control is responsive."}],
            "specifications": {"Brand": "Bosch", "Series": "Serie 2", "Model": "BEL553MS0I", "Capacity": "20 L", "Warranty": "2 Years"},
            "stock_quantity": 12, "reorder_level": 5, "is_featured": False, "customer_rating": 4.3, "review_count": 41,
            "fast_moving": False, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow(), "warranty": "2 years", "energy_rating": "Standard"
        },
        
        # Product 5: BEL554MB0I - Built-in Microwave Black Premium
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Serie 4 Built-in Microwave 60 x 38 cm Black with Grill",
            "brand": "Bosch",
            "series": "Serie 4",
            "category": "Built-in Microwaves",
            "model": "BEL554MB0I",
            "sku": "BSH-BEL554MB0I",
            "price": 46990,
            "original_price": 51990,
            "description": "Bosch Serie 4 Built-in Microwave with grill function, 25L capacity, 900W power, electronic control, and 5 power levels. Features AutoPilot programs and quartz grill for perfect browning.",
            "short_description": "25L Microwave with Grill Function - Black",
            "image": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02696049_BEL554MB0_def.webp",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02696049_BEL554MB0_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02696050_BEL554MB0_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02696051_BEL554MB0_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02696052_BEL554MB0_def.webp"
            ],
            "technical_overview": {"Power": "900 W", "Capacity": "25 L", "Colour": "Black", "Grill": "Quartz Grill", "Power Levels": "5", "AutoPilot": "7 Programs"},
            "highlights": [
                {"title": "Grill Function for Perfect Browning", "description": "Quartz grill adds the perfect golden-brown finish to your dishes."},
                {"title": "AutoPilot 7 Programs", "description": "7 automatic programs take the guesswork out of cooking different dishes."},
                {"title": "Larger 25L Capacity", "description": "More space for larger dishes and family meals."}
            ],
            "features": ["900W microwave power", "25L capacity", "Quartz grill function", "7 AutoPilot programs", "5 power levels", "Electronic control", "Black glass finish", "LED interior light"],
            "spec_groups": {
                "general": {"Brand": "Bosch", "Series": "Serie 4", "Model": "BEL554MB0I", "Color": "Black", "Grill": "Yes - Quartz"},
                "size_weight": {"Height": "382 mm", "Width": "594 mm", "Depth": "388 mm", "Weight": "18 kg"},
                "technical": {"Capacity": "25 L", "Microwave Power": "900 W", "Grill": "Quartz Grill", "Power Levels": "5", "AutoPilot": "7 Programs"},
                "comfort": {"Control": "Electronic", "Interior Light": "LED", "Programs": "7 AutoPilot"},
                "connectivity": {"Smart Features": "None"}
            },
            "documents": [{"title": "User Manual", "type": "manual", "url": "#", "size": "PDF - 2.2 MB"}],
            "reviews": [
                {"name": "Rohit Sharma", "rating": 5, "date": "22 Jan 2025", "comment": "Excellent microwave with grill! The AutoPilot programs are very useful. 25L is perfect for family."},
                {"name": "Meena Patel", "rating": 4, "date": "16 Jan 2025", "comment": "Good product. Grill function works great for pizzas and sandwiches. Happy with purchase!"}
            ],
            "specifications": {"Brand": "Bosch", "Series": "Serie 4", "Model": "BEL554MB0I", "Capacity": "25 L", "Warranty": "2 Years"},
            "stock_quantity": 10, "reorder_level": 4, "is_featured": True, "customer_rating": 4.6, "review_count": 54,
            "fast_moving": True, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow(), "warranty": "2 years", "energy_rating": "A"
        }
    ]
    
    # Insert all products
    result = await db.products.insert_many(products)
    
    print(f"\n✅ Successfully Added {len(result.inserted_ids)} Products!")
    print("\n📋 Products Summary:")
    for i, product in enumerate(products, 1):
        print(f"\n{i}. {product['name']}")
        print(f"   Model: {product['model']}")
        print(f"   Series: {product['series']}")
        print(f"   Price: ₹{product['price']:,}")
        print(f"   Capacity: {product['technical_overview'].get('Cavity Capacity') or product['technical_overview'].get('Capacity', 'N/A')}")
    
    # Verify total
    count = await db.products.count_documents({})
    print(f"\n📊 Total products in database: {count}")
    print("=" * 80)
    
    client.close()

asyncio.run(add_five_microwave_products())
