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

async def add_siemens_ovens():
    """Add six Siemens Oven models to database"""
    
    products = [
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ300 Built-In Microwave with Grill Stainless Steel BE550LMR0I",
            "brand": "Siemens",
            "model_number": "BE550LMR0I",
            "category": "Oven",
            "sub_category": "Built-In Microwave",
            "price": 71990.00,
            "description": "Siemens iQ300 Built-In Microwave with powerful 900W microwave and grill function, 25L capacity, and humidClean easy cleaning system.",
            "short_description": "iQ300 Built-In Microwave with 900W power, grill function, 25L capacity, and side-opening door.",
            "long_description": "The Siemens iQ300 Built-In Microwave BE550LMR0I combines powerful microwave cooking with grilling capabilities. With 900W of microwave power and 5 power levels, you can prepare a wide variety of dishes quickly and efficiently. The 25-litre cavity capacity provides ample space for family meals. The powerful grill function ensures foods are evenly browned. The side-opening hinged door is ideal for elevated installation and provides easy access. humidClean makes cleaning effortless by vaporizing soapy water to soften dirt, which can then be removed easily. Perfect for modern kitchens seeking convenience and performance.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02032270_BE550LMR0_CompactOven_Siemens_STP___EOX5_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02792894_BE550LMR0_Microwave_Siemens_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02792896_BE550LMR0_Microwave_Siemens_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02792897_BE550LMR0_Microwave_Siemens_PGA3_def.webp"
            ],
            "stock": 8,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Built-in microwave with grill",
                "Maximum Microwave Power": "900 W",
                "Cavity Capacity": "25 L",
                "Power Levels": "5",
                "Cleaning System": "Hydrolytic (humidClean)",
                "Door Type": "Side-opening hinged door",
                "Color": "Stainless Steel",
                "Series": "iQ300"
            },
            "key_features": [
                "900W microwave power for fast cooking",
                "Grill function for even browning",
                "25L cavity capacity",
                "5 power levels for versatility",
                "Side-opening hinged door - ideal for elevated installation",
                "humidClean easy cleaning system",
                "Stainless steel finish"
            ],
            "highlights": [
                "Powerful 900W microwave",
                "Side-opening hinged door for easy access",
                "Grill function for perfect browning",
                "Easy cleaning with humidClean"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/ovens/small-ovens/BE550LMR0I",
                    "title": "BE550LMR0I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ700 Built-in Compact Oven with Steam Function 60x45cm Black CS736G1B1",
            "brand": "Siemens",
            "model_number": "CS736G1B1",
            "category": "Oven",
            "sub_category": "Compact Steam Oven",
            "price": 242990.00,
            "description": "Premium Siemens iQ700 compact oven with integrated steam function, TFT touch display, Home Connect, and Made in Germany quality.",
            "short_description": "iQ700 Compact Steam Oven 60x45cm with TFT display, Home Connect, and multiple heating methods.",
            "long_description": "The Siemens iQ700 Built-in Compact Oven CS736G1B1 represents premium cooking technology Made in Germany. This versatile compact oven combines traditional heating with steam functionality for healthier cooking and better results. The TFT touch display provides intuitive control over all functions. Home Connect integration allows remote monitoring and control via smartphone. With multiple heating methods and steam support, you can prepare everything from perfectly risen bread to tender meats and vegetables. The compact 60x45cm size makes it perfect for modern kitchens while providing full oven functionality.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/26056410_CS736G1B1_STP_def.webp"
            ],
            "stock": 3,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Built-in compact oven with steam",
                "Dimensions": "60 x 45 cm",
                "Home Connect": "Yes",
                "Display": "TFT touch display",
                "Color": "Black",
                "Series": "iQ700",
                "Made in": "Germany"
            },
            "key_features": [
                "Steam function for healthier cooking",
                "TFT touch display for intuitive control",
                "Home Connect enabled",
                "Multiple heating methods",
                "Compact 60x45cm design",
                "Made in Germany",
                "Premium iQ700 series quality"
            ],
            "highlights": [
                "Integrated steam function",
                "TFT touch display",
                "Home Connect enabled",
                "Made in Germany quality"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/ovens/small-ovens/CS736G1B1",
                    "title": "CS736G1B1 User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ700 Built-in Oven 60x60cm Black HB736G1B1",
            "brand": "Siemens",
            "model_number": "HB736G1B1",
            "category": "Oven",
            "sub_category": "Built-In Oven",
            "price": 181990.00,
            "description": "Premium Siemens iQ700 built-in oven with pyrolytic self-cleaning, TFT display, Home Connect, and Made in Germany quality.",
            "short_description": "iQ700 60x60cm Built-in Oven with pyrolytic cleaning, TFT display, and Home Connect.",
            "long_description": "The Siemens iQ700 Built-in Oven HB736G1B1 delivers exceptional cooking performance with German engineering excellence. This full-size oven features pyrolytic self-cleaning that burns away food residues at high temperatures, eliminating the need for manual scrubbing. The TFT display provides clear, intuitive control over all functions. Home Connect integration enables smart cooking with recipe suggestions and remote monitoring. With multiple heating modes and precise temperature control, you can achieve professional cooking results at home. The premium black finish adds elegance to any kitchen.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/26056387_HB736G1B1_STP_def.webp"
            ],
            "stock": 5,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Built-in oven",
                "Dimensions": "60 x 60 cm",
                "Cleaning System": "Pyrolytic",
                "Home Connect": "Yes",
                "Display": "TFT display",
                "Color": "Black",
                "Series": "iQ700",
                "Made in": "Germany"
            },
            "key_features": [
                "Pyrolytic self-cleaning - effortless maintenance",
                "TFT display for easy control",
                "Home Connect smart connectivity",
                "Multiple heating modes",
                "60x60cm standard size",
                "Made in Germany",
                "Premium iQ700 quality"
            ],
            "highlights": [
                "Pyrolytic self-cleaning",
                "TFT display",
                "Home Connect enabled",
                "Made in Germany"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/ovens/built-in-ovens/HB736G1B1",
                    "title": "HB736G1B1 User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ700 Built-in Oven 60x60cm Black HB978GNB1B",
            "brand": "Siemens",
            "model_number": "HB978GNB1B",
            "category": "Oven",
            "sub_category": "Built-In Oven",
            "price": 301990.00,
            "description": "Premium Siemens iQ700 built-in oven with advanced features, pyrolytic cleaning, TFT display, Home Connect, and Made in Germany quality.",
            "short_description": "iQ700 60x60cm Premium Built-in Oven with pyrolytic cleaning, TFT display, and smart features.",
            "long_description": "The Siemens iQ700 Built-in Oven HB978GNB1B represents the pinnacle of oven technology. This premium model combines German engineering with smart features for exceptional cooking results. Pyrolytic self-cleaning at high temperatures eliminates manual scrubbing. The TFT display offers intuitive navigation through all functions. Home Connect provides smart cooking guidance, remote monitoring, and automatic settings updates. With precision temperature control and multiple cooking modes, you can prepare restaurant-quality dishes at home. Made in Germany ensures the highest quality standards.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/19151347_HB978GMB1_STP_def.webp"
            ],
            "stock": 4,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Built-in oven",
                "Dimensions": "60 x 60 cm",
                "Cleaning System": "Pyrolytic",
                "Home Connect": "Yes",
                "Display": "TFT display",
                "Color": "Black",
                "Series": "iQ700",
                "Made in": "Germany"
            },
            "key_features": [
                "Advanced pyrolytic self-cleaning",
                "TFT display with intuitive navigation",
                "Home Connect smart features",
                "Precision temperature control",
                "Multiple cooking modes",
                "60x60cm standard size",
                "Premium Made in Germany quality"
            ],
            "highlights": [
                "Premium iQ700 features",
                "Pyrolytic self-cleaning",
                "Smart Home Connect",
                "Made in Germany excellence"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/ovens/built-in-ovens/HB978GNB1B",
                    "title": "HB978GNB1B User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ700 Built-in Oven with Microwave Function 60x60cm Black HM778GNB1I",
            "brand": "Siemens",
            "model_number": "HM778GNB1I",
            "category": "Oven",
            "sub_category": "Oven with Microwave",
            "price": 349990.00,
            "description": "Premium Siemens iQ700 oven combining traditional cooking with integrated microwave function, pyrolytic cleaning, TFT display, Home Connect, Made in Germany.",
            "short_description": "iQ700 60x60cm Oven with integrated microwave, pyrolytic cleaning, and Home Connect.",
            "long_description": "The Siemens iQ700 Built-in Oven with Microwave Function HM778GNB1I offers the ultimate in cooking versatility. This premium appliance combines a full-featured oven with an integrated microwave in a single 60x60cm unit, saving valuable kitchen space. Use them separately or together for faster cooking. Pyrolytic self-cleaning makes maintenance effortless. The TFT display provides clear control over all functions. Home Connect enables smart cooking with guided recipes and remote operation. Multiple cooking modes allow you to bake, roast, grill, and microwave with precision. Made in Germany ensures exceptional quality and durability.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/26055175_HM778GNB1I_STP_def.webp"
            ],
            "stock": 3,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Built-in oven with microwave",
                "Dimensions": "60 x 60 cm",
                "Cleaning System": "Pyrolytic",
                "Home Connect": "Yes",
                "Display": "TFT display",
                "Microwave": "Integrated",
                "Color": "Black",
                "Series": "iQ700",
                "Made in": "Germany"
            },
            "key_features": [
                "Integrated microwave and oven in one unit",
                "Pyrolytic self-cleaning",
                "TFT display for intuitive control",
                "Home Connect smart features",
                "Use microwave and oven separately or together",
                "Multiple cooking modes",
                "Made in Germany premium quality"
            ],
            "highlights": [
                "Oven and microwave in one",
                "Pyrolytic self-cleaning",
                "Home Connect enabled",
                "Made in Germany"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/ovens/ovens-with-microwave/HM778GNB1I",
                    "title": "HM778GNB1I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ700 Built-in Oven with Steam Function 60x60cm Black HS958GDD1",
            "brand": "Siemens",
            "model_number": "HS958GDD1",
            "category": "Oven",
            "sub_category": "Steam Oven",
            "price": 436990.00,
            "description": "Premium Siemens iQ700 oven with integrated steam and sous-vide functionality, pyrolytic cleaning, TFT display, Home Connect, Made in Germany.",
            "short_description": "iQ700 60x60cm Steam Oven with sous-vide function, pyrolytic cleaning, and smart features.",
            "long_description": "The Siemens iQ700 Built-in Oven with Steam Function HS958GDD1 represents the ultimate in premium cooking technology. This top-of-the-line model combines traditional oven functions with integrated steam cooking and professional sous-vide functionality. Steam cooking preserves nutrients and flavors while ensuring perfect moisture levels. Sous-vide enables restaurant-quality precision cooking at precise temperatures. Pyrolytic self-cleaning eliminates manual maintenance. The TFT display provides intuitive control. Home Connect offers guided cooking, automatic updates, and remote monitoring. With the widest range of cooking methods available, you can master any culinary technique. Made in Germany ensures uncompromising quality.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/19151347_HB978GMB1_STP_def.webp"
            ],
            "stock": 2,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Built-in steam oven",
                "Dimensions": "60 x 60 cm",
                "Cleaning System": "Pyrolytic",
                "Home Connect": "Yes",
                "Display": "TFT display",
                "Steam Function": "Yes",
                "Sous-vide": "Yes",
                "Color": "Black",
                "Series": "iQ700",
                "Made in": "Germany"
            },
            "key_features": [
                "Integrated steam cooking for healthier meals",
                "Professional sous-vide functionality",
                "Pyrolytic self-cleaning",
                "TFT display with guided cooking",
                "Home Connect smart features",
                "Multiple cooking modes including steam",
                "Premium Made in Germany quality"
            ],
            "highlights": [
                "Steam and sous-vide cooking",
                "Pyrolytic self-cleaning",
                "Home Connect enabled",
                "Ultimate Made in Germany quality"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/ovens/ovens-with-sous-vide-functionality/HS958GDD1",
                    "title": "HS958GDD1 User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    print("=" * 70)
    print("Adding 6 Siemens Ovens to Database")
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
        print(f"\n✅ Added: {product['name']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Price: ₹{product['price']:,.2f}")
        print(f"   Category: {product['category']}")
        print(f"   Sub-category: {product['sub_category']}")
        print(f"   ID: {product['id']}")
    
    # Get total product count
    total_count = await products_collection.count_documents({})
    oven_count = await products_collection.count_documents({"category": "Oven"})
    siemens_count = await products_collection.count_documents({"brand": "Siemens"})
    filtered_count = await products_collection.count_documents({"price": {"$gt": 100000}})
    
    print("\n" + "=" * 70)
    print(f"✅ Successfully added {added_count} Siemens Ovens!")
    print(f"Total products in database: {total_count}")
    print(f"Total Ovens: {oven_count}")
    print(f"Total Siemens products: {siemens_count}")
    print(f"High-priced products (>₹100k): {filtered_count}")
    print(f"Visible on frontend: {total_count - filtered_count}")
    print("=" * 70)
    print("\n⚠️  NOTE: 5 ovens are premium (>₹100k) and will be filtered on frontend.")

if __name__ == "__main__":
    asyncio.run(add_siemens_ovens())
