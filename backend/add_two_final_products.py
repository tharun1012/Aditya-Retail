import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

async def add_two_products():
    # Get MongoDB connection string
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client['startup_template']
    products_collection = db['products']
    
    # Product data for both products
    products = [
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch TrueMixx Pro Mixer Grinder 1000W - Black",
            "model_number": "MGM8856BIN",
            "brand": "Bosch",
            "category": "Mixer Grinder",
            "subcategory": "TrueMixx Pro",
            "price": 7936.00,
            "original_price": 11950.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 20,
            "rating": 4.4,
            "reviews_count": 23,
            "short_description": "Powerful 1000W ball bearing motor with 60-minute rating and stone pounding technology",
            "long_description": "The Bosch TrueMixx Pro Mixer Grinder MGM8856BIN features a powerful 1000W ball bearing motor with an impressive 60-minute motor rating, designed to deliver high torque for exceptional grinding performance. Its uniquely designed blunt pounding blade with thick edges replicates the pounding effect on dry ingredients for authentic texture and taste. The innovative Active Flow Breaker guarantees finer, fluffier batters with enhanced aeration. Features heavy-duty motor coupler and metallic jar collar for durability.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/22535822_MGM8856BIN_STP_D_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/22226361_MGM8856BIN_TrueMixxPro_MainUnit_WetGrinder_FRONTAL_F39_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/22226362_MGM8856BIN_TrueMixxPro_Indien_Grinder_Flagship_visual_F39_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/22226352_MGM8856BIN_MG_Motor_Coupler_Heavy_Duty_v02_F39_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/22226356_MGM8856BIN_Metallic_Jar_Collar_F39_def.webp"
            ],
            "key_features": [
                "1000W ball bearing motor with 60-minute rating",
                "Stone pounding blade for authentic texture and taste",
                "Active Flow Breaker for finer, fluffier batters",
                "Heavy-duty motor coupler for durability",
                "Metallic jar collar",
                "1.5L capacity liquidizing jar",
                "3-stage speed settings",
                "Pulse function",
                "4-wing stainless steel blades",
                "Free delivery",
                "2 years comprehensive warranty"
            ],
            "specifications": {
                "Power": "1000W",
                "Motor Type": "Ball bearing motor with 60-minute rating",
                "Capacity": "1.5 L",
                "Speed Settings": "3-stage",
                "Pulse Function": "Yes",
                "Color": "Black",
                "Dimensions": "495 x 210 x 219 mm",
                "Blade Design": "4-wing blade, Stone pounding blade, Chutney Grinding Blade (Fixed), Dry grinding blade (detachable), Wet Grinding Blade (detachable)",
                "Blade Material": "Stainless Steel",
                "Warranty": "2 years"
            },
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MGM8856BIN"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch TrueMixx Juicer Mixer Grinder 750W - Mint Green",
            "model_number": "MJ4412A1GI",
            "brand": "Bosch",
            "category": "Mixer Grinder",
            "subcategory": "TrueMixx Pro",
            "price": 9900.00,
            "original_price": 9900.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 15,
            "rating": 4.5,
            "reviews_count": 0,
            "short_description": "Versatile juicer mixer grinder with 750W motor and stone pounding technology",
            "long_description": "The Bosch TrueMixx Juicer Mixer Grinder combines the functionality of a juicer and mixer grinder in one powerful appliance. Featuring a 750W HiFlux Motor for consistent high performance, it comes with a uniquely designed blunt pounding blade for authentic texture and taste. The elegant mint green finish adds a fresh look to your kitchen while delivering professional grinding and juicing performance.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/26839359_K5402_MJ4412A1GI_STP_mintgreen_def.webp"
            ],
            "key_features": [
                "750W HiFlux Motor for consistent performance",
                "Juicer and mixer grinder combined functionality",
                "Stone pounding blade for authentic taste",
                "Multipurpose blade for versatility",
                "3-stage speed settings",
                "4-wing stainless steel blade",
                "Elegant mint green color",
                "Chutney grinding blade included",
                "Free delivery",
                "2 years warranty"
            ],
            "specifications": {
                "Power": "750W",
                "Speed Settings": "3-stage",
                "Pulse Function": "No",
                "Color": "Mint Green",
                "Dimensions": "495 x 210 x 219 mm",
                "Blade Design": "4-wing blade, Multipurpose blade (detachable), Chutney Grinding Blade (Fixed), Stone pounding blade (blunt, detachable)",
                "Blade Material": "Stainless Steel",
                "Product Type": "Juicer Mixer Grinder",
                "Warranty": "2 years"
            },
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MJ4412A1GI"
        }
    ]
    
    print("=" * 70)
    print("ADDING 2 NEW PRODUCTS")
    print("=" * 70)
    
    added_count = 0
    
    for product in products:
        # Check if product already exists
        existing = await products_collection.find_one({"model_number": product["model_number"]})
        if existing:
            print(f"\n⚠️  {product['model_number']} already exists, skipping...")
            continue
        
        # Insert product
        result = await products_collection.insert_one(product)
        discount = 0
        if product.get('original_price') and product['price'] < product['original_price']:
            discount = int((1 - product['price']/product['original_price']) * 100)
        discount_str = f' (-{discount}%)' if discount > 0 else ''
        
        print(f"\n✅ Added: {product['name']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Category: {product['category']}")
        print(f"   Price: ₹{product['price']:,.0f}{discount_str}")
        print(f"   Rating: {product['rating']}/5 ({product['reviews_count']} reviews)")
        print(f"   Color: {product['specifications'].get('Color', 'N/A')}")
        print(f"   MongoDB ID: {result.inserted_id}")
        
        added_count += 1
    
    # Close connection
    client.close()
    
    print("\n" + "=" * 70)
    print("OPERATION COMPLETE")
    print("=" * 70)
    print(f"✅ Successfully Added: {added_count}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(add_two_products())
