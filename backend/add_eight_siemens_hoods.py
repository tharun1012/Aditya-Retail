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

async def add_siemens_hoods():
    """Add 8 Siemens Kitchen Hood and Ventilation products to database"""
    
    products = [
        # WORKTOP VENTILATION
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ700 Induction Hob with Integrated Ventilation System 80cm EX875LX67E",
            "brand": "Siemens",
            "model_number": "EX875LX67E",
            "category": "Induction Hob",
            "sub_category": "InductionAir System",
            "price": 443990.00,
            "description": "Revolutionary Siemens iQ700 induction hob with integrated ventilation system, combining cooking and extraction in one unit. Features powerMove Plus and Home Connect.",
            "short_description": "iQ700 80cm Induction hob with integrated ventilation, powerMove Plus, and Home Connect.",
            "long_description": "The Siemens iQ700 Induction Hob with Integrated Ventilation System EX875LX67E represents the pinnacle of kitchen innovation. This revolutionary appliance combines a powerful induction hob with an integrated downdraft ventilation system, eliminating the need for a separate hood. The powerMove Plus feature enables intuitive control with three heating zones at different temperatures, activated by simply moving your pot. With 4 induction zones, Dual lightSlider touch control, and 622 m³/h air extraction at boost mode, this system delivers exceptional performance. Home Connect integration allows smart control via smartphone. The front facette with side profiles design adds premium aesthetics to your kitchen.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA03293439_EX875LX67E_ElectricHob_Siemens_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA03296476_EX875LX67E_U_ElectricHob_Siemens_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA03295620_EX875LX67E_ElectricHob_Siemens_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA03295625_EX875LX67E_ElectricHob_Siemens_PGA3_def.webp"
            ],
            "stock": 2,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Induction hob with integrated ventilation",
                "Width": "80 cm",
                "Number of Induction Plates": "4",
                "Control Type": "Dual lightSlider touch control",
                "Frame Type": "Front facette, side profiles",
                "Boost Air Extraction": "622 m³/h",
                "Sound Power Max Speed": "69 dB",
                "Home Connect": "Yes",
                "Color": "Black",
                "Series": "iQ700"
            },
            "key_features": [
                "Integrated ventilation system - no separate hood needed",
                "powerMove Plus - move pot to change settings",
                "4 induction zones with flexInduction",
                "Dual lightSlider touch control",
                "622 m³/h powerful air extraction",
                "Home Connect smart features",
                "Premium design with facette frame"
            ],
            "highlights": [
                "Induction cooking and ventilation in one unit",
                "powerMove Plus for intuitive control",
                "Home Connect enabled",
                "Powerful 622 m³/h extraction"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/kitchen-hoods/worktop-ventilation-solutions/inductionair-system/EX875LX67E",
                    "title": "EX875LX67E User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        # ISLAND HOOD
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens Island Chimney Hood 90cm Black LF91BUV50I",
            "brand": "Siemens",
            "model_number": "LF91BUV50I",
            "category": "Chimney",
            "sub_category": "Island Hood",
            "price": 212990.00,
            "description": "Premium Siemens island chimney hood with 90cm width, powerful 1000 m³/h extraction, LED lighting, and sophisticated black design.",
            "short_description": "90cm Island chimney with 1000 m³/h extraction, LED lighting, and touch control.",
            "long_description": "The Siemens Island Chimney Hood LF91BUV50I makes a bold design statement in your kitchen. Suspended from the ceiling above your island cooking area, this 90cm hood combines powerful performance with elegant styling. With 1000 m³/h maximum air extraction rate at intensive setting, it efficiently removes cooking odors and steam. Energy-efficient LED lighting illuminates your cooking surface. Touch control operation provides convenient access to functions. The premium black finish complements modern kitchen aesthetics. Perfect for open-plan kitchens with island configurations.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA03035956_LF91BUV50_Hood_Siemens_STP_def.webp"
            ],
            "stock": 5,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Island chimney hood",
                "Width": "90 cm",
                "Max Air Extraction Rate": "1000 m³/h",
                "Lighting": "LED",
                "Control Type": "Touch control",
                "Color": "Black",
                "Installation": "Ceiling mounted"
            },
            "key_features": [
                "1000 m³/h powerful extraction at intensive setting",
                "90cm width perfect for island cooking",
                "Energy-efficient LED lighting",
                "Touch control operation",
                "Premium black finish",
                "Ceiling suspended design",
                "Modern aesthetics for open kitchens"
            ],
            "highlights": [
                "Powerful 1000 m³/h extraction",
                "LED lighting",
                "Touch control",
                "Premium island design"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/kitchen-hoods/island-chimney-and-ceiling-hoods/island-chimney-hoods/LF91BUV50I",
                    "title": "LF91BUV50I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        # WALL MOUNTED HOODS
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens Wall Mounted Chimney Hood 90cm Black LC91BUV50I",
            "brand": "Siemens",
            "model_number": "LC91BUV50I",
            "category": "Chimney",
            "sub_category": "Wall Mounted Hood",
            "price": 165990.00,
            "description": "Siemens 90cm wall-mounted chimney hood with 950 m³/h extraction, LED lighting, and elegant black design.",
            "short_description": "90cm Wall-mounted chimney with 950 m³/h extraction and LED lighting.",
            "long_description": "The Siemens Wall Mounted Chimney Hood LC91BUV50I delivers powerful ventilation for your kitchen. With 950 m³/h maximum extraction rate, it effectively removes cooking odors and grease. The 90cm width is ideal for standard cooking zones. LED lighting provides energy-efficient illumination. Touch control operation ensures convenient access to all functions. The sleek black finish adds modern sophistication to your kitchen design.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA03035925_LC91BUV50_Hood_Siemens_STP_def.webp"
            ],
            "stock": 8,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Wall-mounted chimney hood",
                "Width": "90 cm",
                "Max Air Extraction Rate": "950 m³/h",
                "Lighting": "LED",
                "Control Type": "Touch control",
                "Color": "Black"
            },
            "key_features": [
                "950 m³/h powerful extraction",
                "90cm width for standard hobs",
                "LED lighting",
                "Touch control",
                "Black finish",
                "Wall-mounted installation"
            ],
            "highlights": [
                "950 m³/h extraction power",
                "Energy-efficient LED lighting",
                "Touch control operation",
                "Elegant black design"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/kitchen-hoods/chimney-hoods/wall-mounted-chimneys/LC91BUV50I",
                    "title": "LC91BUV50I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens Wall Mounted Chimney Hood 90cm Stainless Steel LC97BIP50I",
            "brand": "Siemens",
            "model_number": "LC97BIP50I",
            "category": "Chimney",
            "sub_category": "Wall Mounted Hood",
            "price": 189990.00,
            "description": "Premium Siemens 90cm wall-mounted chimney with iQ700 features, 850 m³/h extraction, Home Connect, and stainless steel finish.",
            "short_description": "iQ700 90cm Wall chimney with Home Connect, 850 m³/h extraction, and premium stainless steel.",
            "long_description": "The Siemens iQ700 Wall Mounted Chimney Hood LC97BIP50I combines performance with smart features. With 850 m³/h extraction capacity and Home Connect integration, you can control and monitor remotely. The premium stainless steel finish complements professional-style kitchens. LED lighting provides excellent illumination. Touch control ensures easy operation. This 90cm hood delivers both functionality and style for modern cooking spaces.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02987234_LC97BIP50_Hood_Siemens_STP_def.webp"
            ],
            "stock": 6,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Wall-mounted chimney hood",
                "Width": "90 cm",
                "Max Air Extraction Rate": "850 m³/h",
                "Lighting": "LED",
                "Control Type": "Touch control",
                "Home Connect": "Yes",
                "Color": "Stainless Steel",
                "Series": "iQ700"
            },
            "key_features": [
                "Home Connect smart connectivity",
                "850 m³/h extraction power",
                "Premium stainless steel finish",
                "LED lighting",
                "Touch control",
                "iQ700 series quality",
                "90cm width"
            ],
            "highlights": [
                "Home Connect enabled",
                "850 m³/h powerful extraction",
                "Premium stainless steel",
                "iQ700 series"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/kitchen-hoods/chimney-hoods/wall-mounted-chimneys/LC97BIP50I",
                    "title": "LC97BIP50I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens Wall Mounted Chimney Hood 90cm Black LC97BCP50I",
            "brand": "Siemens",
            "model_number": "LC97BCP50I",
            "category": "Chimney",
            "sub_category": "Wall Mounted Hood",
            "price": 189990.00,
            "description": "Siemens iQ700 90cm wall-mounted chimney with 850 m³/h extraction, Home Connect, and sophisticated black finish.",
            "short_description": "iQ700 90cm Wall chimney with Home Connect, 850 m³/h extraction, and black finish.",
            "long_description": "The Siemens iQ700 Wall Mounted Chimney Hood LC97BCP50I offers smart cooking ventilation. With 850 m³/h extraction and Home Connect integration, manage your hood remotely via smartphone. The elegant black finish adds contemporary style. LED lighting illuminates your cooking area. Touch control provides convenient operation. This 90cm hood delivers performance and connectivity for modern kitchens.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02987227_LC97BCP50_Hood_Siemens_STP_def.webp"
            ],
            "stock": 7,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Wall-mounted chimney hood",
                "Width": "90 cm",
                "Max Air Extraction Rate": "850 m³/h",
                "Lighting": "LED",
                "Control Type": "Touch control",
                "Home Connect": "Yes",
                "Color": "Black",
                "Series": "iQ700"
            },
            "key_features": [
                "Home Connect smart features",
                "850 m³/h extraction",
                "Elegant black finish",
                "LED lighting",
                "Touch control",
                "iQ700 series",
                "Remote operation via app"
            ],
            "highlights": [
                "Home Connect enabled",
                "850 m³/h extraction power",
                "Sophisticated black design",
                "iQ700 quality"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/kitchen-hoods/chimney-hoods/wall-mounted-chimneys/LC97BCP50I",
                    "title": "LC97BCP50I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens Wall Mounted Chimney Hood 60cm Black LC67BCP50I",
            "brand": "Siemens",
            "model_number": "LC67BCP50I",
            "category": "Chimney",
            "sub_category": "Wall Mounted Hood",
            "price": 175990.00,
            "description": "Siemens iQ700 60cm compact wall-mounted chimney with 700 m³/h extraction, Home Connect, and black finish.",
            "short_description": "iQ700 60cm Compact wall chimney with Home Connect and 700 m³/h extraction.",
            "long_description": "The Siemens iQ700 Wall Mounted Chimney Hood LC67BCP50I is perfect for smaller kitchens or 60cm hobs. Despite its compact 60cm width, it delivers 700 m³/h extraction power. Home Connect enables smart control and monitoring. The black finish provides elegant styling. LED lighting and touch control ensure modern convenience. Ideal for apartments and compact cooking spaces requiring efficient ventilation.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02987222_LC67BCP50_Hood_Siemens_STP_def.webp"
            ],
            "stock": 10,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Wall-mounted chimney hood",
                "Width": "60 cm",
                "Max Air Extraction Rate": "700 m³/h",
                "Lighting": "LED",
                "Control Type": "Touch control",
                "Home Connect": "Yes",
                "Color": "Black",
                "Series": "iQ700"
            },
            "key_features": [
                "Compact 60cm width",
                "Home Connect smart connectivity",
                "700 m³/h extraction power",
                "LED lighting",
                "Touch control",
                "Perfect for smaller hobs",
                "iQ700 series quality"
            ],
            "highlights": [
                "Compact 60cm design",
                "Home Connect enabled",
                "700 m³/h extraction",
                "iQ700 quality"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/kitchen-hoods/chimney-hoods/wall-mounted-chimneys/LC67BCP50I",
                    "title": "LC67BCP50I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        # TELESCOPIC HOODS
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens Telescopic Hood 90cm Stainless Steel LI97SA531I",
            "brand": "Siemens",
            "model_number": "LI97SA531I",
            "category": "Chimney",
            "sub_category": "Telescopic Hood",
            "price": 134990.00,
            "description": "Siemens 90cm telescopic integrated hood with 700 m³/h extraction, LED lighting, and space-saving slide-out design.",
            "short_description": "90cm Telescopic hood with 700 m³/h extraction and slide-out design.",
            "long_description": "The Siemens Telescopic Hood LI97SA531I offers integrated ventilation that slides out when needed. This space-saving 90cm hood installs beneath cabinets and extends during cooking for optimal extraction. With 700 m³/h maximum air flow, it effectively removes odors and steam. LED lighting illuminates the cooking surface. The stainless steel finish complements any kitchen style. Perfect for kitchens where a traditional chimney hood isn't feasible or desired. Retractable design maintains clean lines when not in use.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02935813_LI97SA531_Hood_Siemens_STP_def.webp"
            ],
            "stock": 12,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Telescopic integrated hood",
                "Width": "90 cm",
                "Max Air Extraction Rate": "700 m³/h",
                "Lighting": "LED",
                "Color": "Stainless Steel",
                "Installation": "Built-in under cabinet"
            },
            "key_features": [
                "Space-saving telescopic design",
                "Slides out during cooking",
                "700 m³/h extraction power",
                "LED lighting",
                "90cm width",
                "Installs under cabinets",
                "Stainless steel finish"
            ],
            "highlights": [
                "Telescopic slide-out design",
                "700 m³/h extraction",
                "LED lighting",
                "Space-saving solution"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/kitchen-hoods/integrated-built-in-hoods/telescopic-chimneys/LI97SA531I",
                    "title": "LI97SA531I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens Telescopic Hood 60cm Stainless Steel LI64MA531I",
            "brand": "Siemens",
            "model_number": "LI64MA531I",
            "category": "Chimney",
            "sub_category": "Telescopic Hood",
            "price": 99990.00,
            "description": "Compact Siemens 60cm telescopic integrated hood with 650 m³/h extraction, LED lighting, and retractable design.",
            "short_description": "60cm Telescopic hood with 650 m³/h extraction and compact slide-out design.",
            "long_description": "The Siemens Telescopic Hood LI64MA531I is the perfect ventilation solution for compact kitchens. This 60cm hood slides out from beneath cabinets when needed and retracts to save space. With 650 m³/h extraction capacity, it handles cooking ventilation efficiently. LED lighting provides clear illumination. The stainless steel construction ensures durability and easy cleaning. Ideal for apartments, smaller kitchens, or where overhead space is limited. Maintains clean aesthetics with hidden installation.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02935803_LI64MA531_Hood_Siemens_STP_def.webp"
            ],
            "stock": 15,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Telescopic integrated hood",
                "Width": "60 cm",
                "Max Air Extraction Rate": "650 m³/h",
                "Lighting": "LED",
                "Color": "Stainless Steel",
                "Installation": "Built-in under cabinet"
            },
            "key_features": [
                "Compact 60cm width",
                "Telescopic retractable design",
                "650 m³/h extraction",
                "LED lighting",
                "Hidden under-cabinet installation",
                "Stainless steel finish",
                "Perfect for small kitchens"
            ],
            "highlights": [
                "Compact 60cm design",
                "Telescopic slide-out",
                "650 m³/h extraction",
                "Space-saving solution"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/kitchen-hoods/integrated-built-in-hoods/telescopic-chimneys/LI64MA531I",
                    "title": "LI64MA531I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    print("=" * 70)
    print("Adding 8 Siemens Kitchen Hoods & Ventilation Products")
    print("=" * 70)
    
    added_count = 0
    for product in products:
        # Check if product already exists
        existing = await products_collection.find_one({"model_number": product["model_number"]})
        if existing:
            print(f"⚠️  Product {product['model_number']} already exists. Skipping...")
            continue
        
        # Insert product
        result = await products_collection.insert_one(product)
        added_count += 1
        print(f"\n✅ Added: {product['name'][:60]}...")
        print(f"   Model: {product['model_number']}")
        print(f"   Price: ₹{product['price']:,.2f}")
        print(f"   Category: {product['category']}")
        print(f"   Sub-category: {product['sub_category']}")
    
    # Get total product count
    total_count = await products_collection.count_documents({})
    chimney_count = await products_collection.count_documents({"category": "Chimney"})
    induction_count = await products_collection.count_documents({"category": "Induction Hob"})
    siemens_count = await products_collection.count_documents({"brand": "Siemens"})
    
    print("\n" + "=" * 70)
    print(f"✅ Successfully added {added_count} products!")
    print(f"Total products in database: {total_count}")
    print(f"Total Chimneys: {chimney_count}")
    print(f"Total Induction Hobs: {induction_count}")
    print(f"Total Siemens products: {siemens_count}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(add_siemens_hoods())
