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

async def add_diverse_siemens_products():
    """Add 8 diverse Siemens products: Gas Hob, Ovens, Warming Drawers, Cooling Appliances"""
    
    products = [
        # GAS HOB
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ500 Gas Hob 75cm Tempered Glass Black EP7B6IG20I",
            "brand": "Siemens",
            "model_number": "EP7B6IG20I",
            "category": "Gas Hob",
            "sub_category": "75 cm Gas Hob",
            "price": 84990.00,
            "description": "Siemens iQ500 75cm gas hob with powerful 4kW wok burner, individual cast-iron pan supports, and modern tempered glass surface.",
            "short_description": "iQ500 75cm Gas Hob with 4kW wok burner and tempered glass.",
            "long_description": "The Siemens iQ500 Gas Hob EP7B6IG20I features a powerful 4000W wok burner ideal for fast cooking with even heat distribution. Individual cast-iron pan supports provide stability and demonstrate high-quality workmanship. The sword knob combines ease of use with modern design. The black tempered glass surface is extremely heat-resistant and easy to clean.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/21337000_EP7B6IG20I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/21579162_EP7B6IG20I_PGA5_def.webp"
            ],
            "stock": 10,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Cooktop Type": "Gas cooktop",
                "Number of Burners": "4",
                "Wok Burner Power": "4000 W",
                "Surface Material": "Tempered glass",
                "Pan Supports": "Cast iron single (individual)",
                "Knob Type": "Sword knob",
                "Width": "75 cm",
                "Color": "Black",
                "Series": "iQ500"
            },
            "key_features": [
                "Powerful 4000W wok burner",
                "Individual cast-iron pan supports",
                "Sword knob for easy operation",
                "Black tempered glass surface",
                "4 burner positions",
                "75cm width"
            ],
            "highlights": [
                "4kW wok burner for fast cooking",
                "Individual cast-iron supports",
                "Modern sword knob design",
                "Heat-resistant glass surface"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/EP7B6IG20I",
                    "title": "EP7B6IG20I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        # OVENS/MICROWAVES
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ700 Built-In Microwave Oven Black BE732L1B1I",
            "brand": "Siemens",
            "model_number": "BE732L1B1I",
            "category": "Oven",
            "sub_category": "Built-In Microwave",
            "price": 142990.00,
            "description": "Siemens iQ700 built-in microwave with 900W power, TFT touch display, humidClean Plus, cookControl10, and inverter technology.",
            "short_description": "iQ700 Microwave with TFT display, 900W, humidClean Plus, and cookControl10.",
            "long_description": "The Siemens iQ700 Built-In Microwave BE732L1B1I combines powerful 900W microwave performance with intelligent features. TFT touch display enables intuitive navigation. humidClean Plus softens dirt by vaporizing soapy water for easy cleaning. cookControl10 automatic programs ensure perfect results. Inverter Technology provides constant power for gradually heated food. 21L capacity with 5 power levels.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/18113214_BE732L1B1_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/20875716_BE732L1B1_PGA1_def.webp"
            ],
            "stock": 6,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Built-in microwave",
                "Maximum Microwave Power": "900 W",
                "Cavity Capacity": "21 L",
                "Power Levels": "5",
                "Cleaning System": "Hydrolytic (humidClean Plus)",
                "Display": "TFT touch display",
                "Automatic Programmes": "10",
                "Color": "Black",
                "Series": "iQ700"
            },
            "key_features": [
                "900W microwave power",
                "TFT touch display",
                "humidClean Plus easy cleaning",
                "cookControl10 automatic programs",
                "Inverter Technology",
                "21L capacity",
                "5 power levels"
            ],
            "highlights": [
                "TFT touch navigation",
                "humidClean Plus program",
                "cookControl10 automation",
                "Inverter Technology"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/BE732L1B1I",
                    "title": "BE732L1B1I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ700 Built-In Single Oven Black BF722L1B1I",
            "brand": "Siemens",
            "model_number": "BF722L1B1I",
            "category": "Oven",
            "sub_category": "Built-In Oven",
            "price": 175990.00,
            "description": "Siemens iQ700 built-in single oven with pyrolytic self-cleaning, TFT display, and multiple heating modes for perfect cooking results.",
            "short_description": "iQ700 Built-in Oven 60x60cm with pyrolytic cleaning and TFT display.",
            "long_description": "The Siemens iQ700 Built-In Single Oven BF722L1B1I delivers professional cooking performance at home. Pyrolytic self-cleaning burns away residue at high temperatures. TFT display provides intuitive control. Multiple heating modes ensure versatility. Made in Europe with premium quality standards.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/18113214_BE732L1B1_STP_def.webp"
            ],
            "stock": 5,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Built-in oven",
                "Dimensions": "60 x 60 cm",
                "Cleaning System": "Pyrolytic",
                "Display": "TFT display",
                "Color": "Black",
                "Series": "iQ700",
                "Made in": "Europe"
            },
            "key_features": [
                "Pyrolytic self-cleaning",
                "TFT display",
                "Multiple heating modes",
                "60x60cm standard size",
                "Made in Europe"
            ],
            "highlights": [
                "Pyrolytic self-cleaning",
                "TFT display control",
                "Premium iQ700 quality"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/BF722L1B1I",
                    "title": "BF722L1B1I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        # WARMING DRAWERS
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ700 Warming Drawer 60cm Black BI710D1B1",
            "brand": "Siemens",
            "model_number": "BI710D1B1",
            "category": "Oven",
            "sub_category": "Warming Drawer",
            "price": 185990.00,
            "description": "Siemens iQ700 warming drawer with 60cm width, perfect for keeping dishes warm, slow cooking, and dough proving.",
            "short_description": "iQ700 60cm Warming Drawer for keeping food warm and slow cooking.",
            "long_description": "The Siemens iQ700 Warming Drawer BI710D1B1 keeps cooked dishes warm until serving time. Also perfect for slow cooking, defrosting, and proving dough. The 60cm width integrates seamlessly beneath ovens. Multiple temperature settings provide versatility for different foods.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/18113214_BE732L1B1_STP_def.webp"
            ],
            "stock": 4,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Warming drawer",
                "Width": "60 cm",
                "Color": "Black",
                "Series": "iQ700"
            },
            "key_features": [
                "Keeps dishes warm",
                "Slow cooking function",
                "Dough proving",
                "60cm width",
                "Multiple temperature settings",
                "iQ700 series"
            ],
            "highlights": [
                "Multi-functional warming",
                "Slow cooking capability",
                "Premium iQ700 quality"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.com/za/en/mkt-product/cooking-and-baking/warmer-drawers/warming-drawers/BI710D1B1",
                    "title": "BI710D1B1 User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ500 Warming Drawer 60cm Black BI710C1B1",
            "brand": "Siemens",
            "model_number": "BI710C1B1",
            "category": "Oven",
            "sub_category": "Warming Drawer",
            "price": 165990.00,
            "description": "Siemens iQ500 warming drawer with 60cm width for keeping food warm and versatile cooking functions.",
            "short_description": "iQ500 60cm Warming Drawer for food warming and cooking.",
            "long_description": "The Siemens iQ500 Warming Drawer BI710C1B1 offers practical functionality for modern kitchens. Keep food warm, slow cook, defrost, or prove dough. The 60cm design fits beneath ovens. Multiple settings provide cooking versatility.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/18113214_BE732L1B1_STP_def.webp"
            ],
            "stock": 6,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Warming drawer",
                "Width": "60 cm",
                "Color": "Black",
                "Series": "iQ500"
            },
            "key_features": [
                "Food warming function",
                "Slow cooking",
                "Defrosting",
                "60cm width",
                "Multiple settings",
                "iQ500 series"
            ],
            "highlights": [
                "Practical food warming",
                "Versatile functions",
                "iQ500 quality"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.com/za/en/mkt-product/cooking-and-baking/warmer-drawers/warming-drawers/BI710C1B1",
                    "title": "BI710C1B1 User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        # COOLING APPLIANCES
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ700 Built-In Refrigerator 177cm KI81FHD30I",
            "brand": "Siemens",
            "model_number": "KI81FHD30I",
            "category": "Refrigerator",
            "sub_category": "Built-In Refrigerator",
            "price": 188590.00,
            "description": "Siemens iQ700 built-in refrigerator with hyperFresh Premium 0°C, Home Connect, superCooling, and 289L capacity.",
            "short_description": "iQ700 177cm Built-in Fridge with hyperFresh Premium, Home Connect, and 289L capacity.",
            "long_description": "The Siemens iQ700 Built-In Refrigerator KI81FHD30I offers maximum freshness with hyperFresh Premium 0°C technology for optimal storage. Home Connect enables smart control. superCooling quickly chills fresh groceries. varioShelf provides flexible storage. Safety glass shelves are shatterproof and easy to clean. 289L capacity with soft-close flat hinge.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02518041_i5455_1890181_KI81FSD30_STP_open_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02518010_i6153_1890130_KI81FSD30_PGA7_def.webp"
            ],
            "stock": 5,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Built-in refrigerator",
                "Dimensions": "177.2 x 55.8 cm",
                "Capacity": "289 L",
                "Freshness System": "hyperFresh Premium 0°C",
                "Home Connect": "Yes",
                "Color": "Not applicable",
                "Series": "iQ700"
            },
            "key_features": [
                "hyperFresh Premium 0°C",
                "Home Connect smart features",
                "superCooling function",
                "varioShelf flexibility",
                "Safety glass shelves",
                "289L capacity",
                "Soft-close flat hinge"
            ],
            "highlights": [
                "Maximum freshness storage",
                "Fast cooling",
                "Flexible storage",
                "Easy-clean safety glass"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooling/built-in-fridges-and-freezers/built-in-refrigerators/KI81FHD30I",
                    "title": "KI81FHD30I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ700 Built-In Freezer 177cm GI81NHD30I",
            "brand": "Siemens",
            "model_number": "GI81NHD30I",
            "category": "Refrigerator",
            "sub_category": "Built-In Freezer",
            "price": 178590.00,
            "description": "Siemens iQ700 built-in freezer with noFrost technology, Home Connect, superFreezing, and soft-close mechanism.",
            "short_description": "iQ700 177cm Built-in Freezer with noFrost and Home Connect.",
            "long_description": "The Siemens iQ700 Built-In Freezer GI81NHD30I features noFrost technology eliminating manual defrosting. Home Connect enables remote monitoring. superFreezing rapidly freezes fresh food. Soft-close mechanism ensures gentle door closing. Premium 177cm built-in design.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02518041_i5455_1890181_KI81FSD30_STP_open_def.webp"
            ],
            "stock": 4,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Built-in freezer",
                "Dimensions": "177 cm height",
                "noFrost": "Yes",
                "Home Connect": "Yes",
                "Color": "Not applicable",
                "Series": "iQ700"
            },
            "key_features": [
                "noFrost technology",
                "Home Connect enabled",
                "superFreezing function",
                "Soft-close mechanism",
                "177cm height",
                "Built-in design"
            ],
            "highlights": [
                "No manual defrosting",
                "Smart Home Connect",
                "Rapid freezing",
                "Premium iQ700"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooling/built-in-fridges-and-freezers/built-in-freezers/GI81NHD30I",
                    "title": "GI81NHD30I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ300 Freestanding Fridge-Freezer 193cm Black Steel KG56NCX41I",
            "brand": "Siemens",
            "model_number": "KG56NCX41I",
            "category": "Refrigerator",
            "sub_category": "Freestanding Fridge-Freezer",
            "price": 107640.00,
            "description": "Siemens iQ300 freestanding fridge-freezer with Total noFrost, hyperFresh, iceTwister, and 193cm height in brushed black steel.",
            "short_description": "iQ300 193cm Freestanding Fridge-Freezer with noFrost and hyperFresh.",
            "long_description": "The Siemens iQ300 Freestanding Fridge-Freezer KG56NCX41I features Total noFrost for no manual defrosting. hyperFresh system keeps food fresher longer. iceTwister provides ice cubes with simple lever action. bottleRack safely stores bottles. easyAccess shelves keep food in view. bigCapacity design with 193x70cm dimensions. Brushed black steel antiFingerprint finish.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/20834905_KG56NCX41I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/20835051_KG56NCX41I_PGA2_def.webp"
            ],
            "stock": 8,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Freestanding fridge-freezer",
                "Dimensions": "193 x 70 x 80 cm",
                "Freshness System": "hyperFresh",
                "noFrost": "Total noFrost",
                "Home Connect": "No",
                "Color": "Brushed black steel",
                "Series": "iQ300"
            },
            "key_features": [
                "Total noFrost technology",
                "hyperFresh freshness system",
                "iceTwister ice maker",
                "bottleRack storage",
                "easyAccess shelves",
                "bigCapacity design",
                "AntiFingerprint finish"
            ],
            "highlights": [
                "No-gap placement",
                "Spacious capacity",
                "Easy ice cubes",
                "Safe bottle storage"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooling/freestanding-fridges-and-freezers/freestanding-bottom-fridge-freezers/KG56NCX41I",
                    "title": "KG56NCX41I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    print("=" * 70)
    print("Adding 8 Diverse Siemens Products")
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
    
    # Get final stats
    total_count = await products_collection.count_documents({})
    siemens_count = await products_collection.count_documents({"brand": "Siemens"})
    gas_hob_count = await products_collection.count_documents({"category": "Gas Hob"})
    oven_count = await products_collection.count_documents({"category": "Oven"})
    refrigerator_count = await products_collection.count_documents({"category": "Refrigerator"})
    
    print("\n" + "=" * 70)
    print(f"✅ Successfully added {added_count} products!")
    print(f"Total products in database: {total_count}")
    print(f"Total Siemens products: {siemens_count}")
    print(f"Total Gas Hobs: {gas_hob_count}")
    print(f"Total Ovens (includes microwaves & warming drawers): {oven_count}")
    print(f"Total Refrigerators (new category): {refrigerator_count}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(add_diverse_siemens_products())
