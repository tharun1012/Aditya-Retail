import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

async def add_two_washing_machines():
    # Get MongoDB connection string
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client['startup_template']
    products_collection = db['products']
    
    # Product data for both washing machines
    products = [
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Front Load Washing Machine 9kg 1200 rpm",
            "model_number": "WGA2420SIN",
            "brand": "Bosch",
            "category": "Washing Machine",
            "subcategory": "Series 6",
            "price": 52190.00,
            "original_price": 52190.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 8,
            "rating": 5.0,
            "reviews_count": 1,
            "short_description": "9 kg front load washing machine with AntiWrinkle, AutoStain Removal, and EcoSilence Drive",
            "long_description": "The Bosch Series 6 Front Load Washing Machine WGA2420SIN offers superior washing performance with 9 kg capacity and 1200 rpm spin speed. Features AntiWrinkle technology that minimizes wrinkles by up to 50%, making laundry gentler on fabric and easier to iron. The AutoStain Removal reliably removes 4 different stubborn stains (blood, butter/oil, grass, red wine) without additional pre-treatment. SpeedPerfect™ option washes in shorter time with excellent cleaning results. EcoSilence Drive ensures efficient and highly durable performance with minimal noise.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/26214365_WGA2420SIN_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/26222359_WGA2420SIN_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/26222360_WGA2420SIN_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/26222361_WGA2420SIN_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/26222362_WGA2420SIN_PGA6_def.webp"
            ],
            "key_features": [
                "9 kg loading capacity",
                "1200 rpm maximum spin speed",
                "AntiWrinkle - minimizes wrinkles by up to 50%",
                "AutoStain Removal - removes 4 common stains without pre-treatment",
                "SpeedPerfect™ - faster washing with same results",
                "EcoSilence Drive - efficient and silent motor",
                "Multiple wash programs",
                "Front loading design",
                "Graphite color",
                "Energy efficient operation",
                "2 years warranty"
            ],
            "specifications": {
                "Type": "Front Load Washing Machine",
                "Series": "Series 6",
                "Capacity": "9 kg",
                "Spin Speed": "1200 rpm",
                "EcoSilence Drive": "Yes",
                "Home Connect": "No",
                "i-DOS": "No",
                "Color": "Graphite",
                "Energy Rating": "Standard",
                "Warranty": "2 years"
            },
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/washer-dryer/washing-machines/front-loading-washing-machines/WGA2420SIN"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Front Load Washing Machine 10kg 1400 rpm",
            "model_number": "WGA254ZPIN",
            "brand": "Bosch",
            "category": "Washing Machine",
            "subcategory": "Series 6",
            "price": 62590.00,
            "original_price": 62590.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 6,
            "rating": 4.0,
            "reviews_count": 4,
            "short_description": "10 kg front load washing machine with 1400 rpm spin speed and EcoSilence Drive",
            "long_description": "The Bosch Series 6 Front Load Washing Machine WGA254ZPIN delivers exceptional washing performance with 10 kg capacity and high 1400 rpm spin speed for faster drying. Features EcoSilence Drive for efficient, silent, and durable operation. The elegant blue color adds style to your laundry room. Perfect for larger families with multiple wash programs and advanced features ensuring thorough cleaning and fabric care.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/25796548_WGA254ZPIN_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/25796552_WGA254ZPIN_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/25796556_WGA254ZPIN_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/25796514_WGA254ZPIN_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/25796603_WGA254ZPIN_PGA12_def.webp"
            ],
            "key_features": [
                "10 kg loading capacity",
                "1400 rpm maximum spin speed for faster drying",
                "EcoSilence Drive - efficient and silent motor",
                "Multiple wash programs",
                "Front loading design",
                "Blue color finish",
                "Energy efficient operation",
                "Perfect for large families",
                "Durable and reliable",
                "Advanced drum technology",
                "2 years warranty"
            ],
            "specifications": {
                "Type": "Front Load Washing Machine",
                "Series": "Series 6",
                "Capacity": "10 kg",
                "Spin Speed": "1400 rpm",
                "EcoSilence Drive": "Yes",
                "Home Connect": "No",
                "i-DOS": "No",
                "Color": "Blue",
                "Energy Rating": "Standard",
                "Warranty": "2 years"
            },
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/washer-dryer/washing-machines/front-loading-washing-machines/WGA254ZPIN"
        }
    ]
    
    print("=" * 70)
    print("ADDING 2 WASHING MACHINES - NEW CATEGORY!")
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
        
        print(f"\n✅ Added: {product['name']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Category: {product['category']} ({product['subcategory']})")
        print(f"   Capacity: {product['specifications']['Capacity']}")
        print(f"   Spin Speed: {product['specifications']['Spin Speed']}")
        print(f"   Price: ₹{product['price']:,.0f}")
        print(f"   Rating: {product['rating']}/5 ({product['reviews_count']} reviews)")
        print(f"   Color: {product['specifications']['Color']}")
        print(f"   MongoDB ID: {result.inserted_id}")
        
        added_count += 1
    
    # Close connection
    client.close()
    
    print("\n" + "=" * 70)
    print("OPERATION COMPLETE")
    print("=" * 70)
    print(f"✅ Successfully Added: {added_count} washing machines")
    print("🎉 New product category unlocked: Washing Machines!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(add_two_washing_machines())
