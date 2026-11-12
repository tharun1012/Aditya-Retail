import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

async def add_six_mixer_grinders():
    # Get MongoDB connection string
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client['startup_template']
    products_collection = db['products']
    
    # Product data for all 6 mixer grinders
    products = [
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch TrueMixx Style Mixer Grinder 750W - Blue",
            "model_number": "MGM6642DIN",
            "brand": "Bosch",
            "category": "Mixer Grinder",
            "subcategory": "TrueMixx Pro",
            "price": 6346.00,
            "original_price": 10450.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 25,
            "rating": 4.8,
            "reviews_count": 4,
            "short_description": "Powerful 750W mixer grinder with stone pounding blade and active flow breaker technology",
            "long_description": "The Bosch TrueMixx Style Mixer Grinder features a powerful 750W HiFlux Motor for consistent high performance grinding. Its uniquely designed blunt pounding blade with thick edges replicates the pounding effect on dry ingredients, giving authentic texture and taste. The innovative Active Flow Breaker guarantees finer, fluffier batters with enhanced aeration.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/20840476_MGM6642DIN_STP_D_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/19723017_MGM6642DIN_TrueMixxPro_MainUnit_WetGrinder_PERS_New_Bf_Blue_F39_02_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/19723100_MGM6642DIN_TrueMixxPro_MainUnit_WetGrinder_FRONTAL_New_Bf_Blue_F39_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/19723109_MGM6642DIN_TrueMixxPro_MainUnit_WetGrinder_PERS_New_Bf_Blue_F39_def.webp"
            ],
            "key_features": [
                "750W HiFlux Motor for consistent high performance",
                "Stone pounding blade for authentic texture and taste",
                "Active Flow Breaker for finer, fluffier batters",
                "1.5L capacity liquidizing jar",
                "3-stage speed settings",
                "Pulse function",
                "4-wing stainless steel blade",
                "Stylish blue color",
                "Free delivery",
                "2 years warranty"
            ],
            "specifications": {
                "Power": "750W",
                "Capacity": "1.5 L",
                "Speed Settings": "3-stage",
                "Pulse Function": "Yes",
                "Color": "Blue",
                "Dimensions": "495 x 210 x 219 mm",
                "Blade Material": "Stainless Steel",
                "Warranty": "2 years"
            },
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MGM6642DIN"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch TrueMixx Style Mixer Grinder 750W - Black",
            "model_number": "MGM6644BIN",
            "brand": "Bosch",
            "category": "Mixer Grinder",
            "subcategory": "TrueMixx Pro",
            "price": 6346.00,
            "original_price": 10450.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 25,
            "rating": 4.7,
            "reviews_count": 3,
            "short_description": "Powerful 750W mixer grinder with stone pounding blade and active flow breaker technology",
            "long_description": "The Bosch TrueMixx Style Mixer Grinder in elegant black features a powerful 750W HiFlux Motor for consistent high performance grinding. Its uniquely designed blunt pounding blade with thick edges replicates the pounding effect on dry ingredients, giving authentic texture and taste. The innovative Active Flow Breaker guarantees finer, fluffier batters.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/20840479_MGM6644BIN_STP_D_def.webp"
            ],
            "key_features": [
                "750W HiFlux Motor for consistent high performance",
                "Stone pounding blade for authentic texture and taste",
                "Active Flow Breaker for finer, fluffier batters",
                "1.5L capacity liquidizing jar",
                "3-stage speed settings",
                "Pulse function",
                "4-wing stainless steel blade",
                "Elegant black finish",
                "Free delivery",
                "2 years warranty"
            ],
            "specifications": {
                "Power": "750W",
                "Capacity": "1.5 L",
                "Speed Settings": "3-stage",
                "Pulse Function": "Yes",
                "Color": "Black",
                "Dimensions": "495 x 210 x 219 mm",
                "Blade Material": "Stainless Steel",
                "Warranty": "2 years"
            },
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MGM6644BIN"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch TrueMixx Bold Mixer Grinder 1000W - Black",
            "model_number": "MGM8642BIN",
            "brand": "Bosch",
            "category": "Mixer Grinder",
            "subcategory": "TrueMixx Pro",
            "price": 8696.00,
            "original_price": 13950.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 20,
            "rating": 4.9,
            "reviews_count": 5,
            "short_description": "Premium 1000W mixer grinder with stone pounding technology and active flow breaker",
            "long_description": "The Bosch TrueMixx Bold Mixer Grinder delivers exceptional power with its 1000W HiFlux Motor designed for superior grinding performance. Features stone pounding blade technology for authentic texture, active flow breaker for perfect batters, and multiple jars for all your grinding needs.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/20840484_MGM8642BIN_STP_D_def.webp"
            ],
            "key_features": [
                "1000W HiFlux Motor for superior performance",
                "Stone pounding blade for authentic taste",
                "Active Flow Breaker technology",
                "1.5L capacity liquidizing jar",
                "3-stage speed settings with pulse",
                "4-wing stainless steel blades",
                "Premium black finish",
                "Multiple grinding jars",
                "Free delivery",
                "2 years warranty"
            ],
            "specifications": {
                "Power": "1000W",
                "Capacity": "1.5 L",
                "Speed Settings": "3-stage",
                "Pulse Function": "Yes",
                "Color": "Black",
                "Dimensions": "495 x 210 x 219 mm",
                "Blade Material": "Stainless Steel",
                "Warranty": "2 years"
            },
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MGM8642BIN"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch TrueMixx Bold Mixer Grinder 1000W - Blue",
            "model_number": "MGM8646BIN",
            "brand": "Bosch",
            "category": "Mixer Grinder",
            "subcategory": "TrueMixx Pro",
            "price": 8696.00,
            "original_price": 13950.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 20,
            "rating": 4.9,
            "reviews_count": 6,
            "short_description": "Premium 1000W mixer grinder with stone pounding technology and active flow breaker",
            "long_description": "The Bosch TrueMixx Bold Mixer Grinder in vibrant blue delivers exceptional power with its 1000W HiFlux Motor designed for superior grinding performance. Features stone pounding blade technology for authentic texture, active flow breaker for perfect batters, and multiple jars for versatile cooking needs.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/20840481_MGM8646BIN_STP_D_def.webp"
            ],
            "key_features": [
                "1000W HiFlux Motor for superior performance",
                "Stone pounding blade for authentic taste",
                "Active Flow Breaker technology",
                "1.5L capacity liquidizing jar",
                "3-stage speed settings with pulse",
                "4-wing stainless steel blades",
                "Vibrant blue color",
                "Multiple grinding jars",
                "Free delivery",
                "2 years warranty"
            ],
            "specifications": {
                "Power": "1000W",
                "Capacity": "1.5 L",
                "Speed Settings": "3-stage",
                "Pulse Function": "Yes",
                "Color": "Blue",
                "Dimensions": "495 x 210 x 219 mm",
                "Blade Material": "Stainless Steel",
                "Warranty": "2 years"
            },
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MGM8646BIN"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch TrueMixx Bold Mixer Grinder 1000W - Mint Green",
            "model_number": "MGM8836MIN",
            "brand": "Bosch",
            "category": "Mixer Grinder",
            "subcategory": "TrueMixx Pro",
            "price": 8696.00,
            "original_price": 13950.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 18,
            "rating": 5.0,
            "reviews_count": 2,
            "short_description": "Premium 1000W mixer grinder with stone pounding technology in elegant mint green",
            "long_description": "The Bosch TrueMixx Bold Mixer Grinder in elegant mint green delivers exceptional power with its 1000W HiFlux Motor designed for superior grinding performance. Features stone pounding blade technology, active flow breaker for perfect batters, and a unique color that adds style to your kitchen.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/20840482_MGM8836MIN_STP_D_def.webp"
            ],
            "key_features": [
                "1000W HiFlux Motor for superior performance",
                "Stone pounding blade for authentic taste",
                "Active Flow Breaker technology",
                "1.5L capacity liquidizing jar",
                "3-stage speed settings with pulse",
                "4-wing stainless steel blades",
                "Unique mint green color",
                "Multiple grinding jars",
                "Free delivery",
                "2 years warranty"
            ],
            "specifications": {
                "Power": "1000W",
                "Capacity": "1.5 L",
                "Speed Settings": "3-stage",
                "Pulse Function": "Yes",
                "Color": "Mint Green",
                "Dimensions": "495 x 210 x 219 mm",
                "Blade Material": "Stainless Steel",
                "Warranty": "2 years"
            },
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MGM8836MIN"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch TrueMixx Bold Mixer Grinder 1000W - Blue",
            "model_number": "MGM8842DIN",
            "brand": "Bosch",
            "category": "Mixer Grinder",
            "subcategory": "TrueMixx Pro",
            "price": 8696.00,
            "original_price": 13950.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 22,
            "rating": 4.8,
            "reviews_count": 8,
            "short_description": "Premium 1000W mixer grinder with stone pounding technology and superior performance",
            "long_description": "The Bosch TrueMixx Bold Mixer Grinder delivers exceptional 1000W power for superior grinding performance. Features advanced stone pounding blade technology for authentic texture and taste, active flow breaker for perfect batters, and comprehensive set of jars for all your kitchen needs.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/15807953_MGM8842DIN_STP_D_def.webp"
            ],
            "key_features": [
                "1000W HiFlux Motor for exceptional performance",
                "Stone pounding blade for authentic taste",
                "Active Flow Breaker technology",
                "1.5L capacity liquidizing jar",
                "3-stage speed settings with pulse",
                "4-wing stainless steel blades",
                "Deep blue finish",
                "Complete jar set included",
                "Free delivery",
                "2 years warranty"
            ],
            "specifications": {
                "Power": "1000W",
                "Capacity": "1.5 L",
                "Speed Settings": "3-stage",
                "Pulse Function": "Yes",
                "Color": "Blue",
                "Dimensions": "495 x 210 x 219 mm",
                "Blade Material": "Stainless Steel",
                "Warranty": "2 years"
            },
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MGM8842DIN"
        }
    ]
    
    print("=" * 70)
    print("ADDING 6 NEW MIXER GRINDERS - BULK OPERATION")
    print("=" * 70)
    
    added_count = 0
    skipped_count = 0
    
    for product in products:
        # Check if product already exists
        existing = await products_collection.find_one({"model_number": product["model_number"]})
        if existing:
            print(f"\n⚠️  {product['model_number']} already exists, skipping...")
            skipped_count += 1
            continue
        
        # Insert product
        result = await products_collection.insert_one(product)
        discount = int((1 - product['price']/product['original_price']) * 100)
        
        print(f"\n✅ Added: {product['name']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Price: ₹{product['price']:,.0f} (-{discount}%)")
        print(f"   Rating: {product['rating']}/5")
        print(f"   MongoDB ID: {result.inserted_id}")
        
        added_count += 1
    
    # Close connection
    client.close()
    
    print("\n" + "=" * 70)
    print("BULK OPERATION COMPLETE")
    print("=" * 70)
    print(f"✅ Successfully Added: {added_count}")
    print(f"⏭️  Skipped (Already Exist): {skipped_count}")
    print(f"📦 Total Processed: {len(products)}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(add_six_mixer_grinders())
