import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

async def add_truemixx_radiance():
    # Get MongoDB connection string
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client['startup_template']
    products_collection = db['products']
    
    # Product data for Bosch TrueMixx Radiance 600W Red (MGM4334RIN)
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch TrueMixx Radiance Mixer Grinder 600W",
        "model_number": "MGM4334RIN",
        "brand": "Bosch",
        "category": "Mixer Grinder",
        "subcategory": "TrueMixx Pro",
        "price": 4000.00,
        "original_price": 6270.00,
        "currency": "INR",
        "in_stock": True,
        "stock_quantity": 20,
        "rating": 3.8,
        "reviews_count": 4,
        "short_description": "Powerful 600W mixer grinder with stone pounding technology for authentic taste and texture",
        "long_description": "The Bosch TrueMixx Radiance Mixer Grinder features a powerful 600W 2-C Series Motor with 100% copper windings designed to deliver high torque for superior grinding performance. Its unique stone pounding blade with thick edges replicates the traditional pounding effect on dry ingredients, giving you authentic texture and taste. With a 1.5L capacity liquidizing jar and multiple jars for various grinding needs, this mixer grinder is perfect for everyday cooking. The stylish red design adds a vibrant touch to your kitchen.",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/15695224_20414681_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/MCIM02712607_BO_U_16_other_TrueMixx_MGM4331RIN_picture_nKF_front_ENG_290518.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/MCIM02712611_BO_U_16_other_TrueMixx_MGM4331RIN_picture_nKF_spatula_ENG_290518.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/MCMI03018737_BO_U_16_other_TrueMixx_MGM4341RIN_picture_nKF_visual_2_ENG_040219.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/MCIM02712605_BO_U_16_other_TrueMixx_MGM4331RIN_picture_nKF_dry_jar_ENG_290518.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/MCIM02712578_BO_U_16_other_TrueMixx_MGM4331RIN_picture_nKF_chutney_jar_ENG_290518.webp"
        ],
        "key_features": [
            "600W 2-C Series Motor with 100% copper windings",
            "Stone pounding blade for authentic texture and taste",
            "1.5L capacity liquidizing jar",
            "3-stage speed settings for precise control",
            "Pulse function for quick bursts",
            "4-wing stainless steel blade for wet grinding",
            "Separate blades for dry and chutney grinding",
            "Durable plastic body in vibrant red color",
            "Free delivery available",
            "2 years product warranty"
        ],
        "specifications": {
            "Power": "600W",
            "Motor Type": "2-C Series with 100% copper windings",
            "Voltage": "230V",
            "Frequency": "50Hz",
            "Capacity": "1.5 L",
            "Speed Settings": "3-stage",
            "Pulse Function": "Yes",
            "Material": "Plastic body",
            "Color": "Red",
            "Dimensions": "280 x 550 x 218 mm (W x H x D)",
            "Blade Design": "4-wing blade, Stone pounding blade (blunt, detachable), Chutney Grinding Blade (Fixed), Dry grinding blade (detachable), Wet Grinding Blade (detachable)",
            "Blade Material": "Stainless Steel",
            "Warranty": "2 years",
            "Special Feature": "Stone Pounding Technology"
        },
        "warranty": "2 years comprehensive warranty",
        "free_delivery": True,
        "product_url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MGM4334RIN"
    }
    
    # Check if product already exists
    existing = await products_collection.find_one({"model_number": product["model_number"]})
    if existing:
        print(f"⚠️  Product {product['model_number']} already exists in database")
        client.close()
        return
    
    # Insert product
    result = await products_collection.insert_one(product)
    print(f"✓ Added product: {product['name']}")
    print(f"  Model: {product['model_number']}")
    print(f"  Price: ₹{product['price']:,.2f} (Original: ₹{product['original_price']:,.2f})")
    print(f"  Discount: {int((1 - product['price']/product['original_price']) * 100)}%")
    print(f"  Rating: {product['rating']} ({product['reviews_count']} reviews)")
    print(f"  Product ID: {product['id']}")
    print(f"  MongoDB ID: {result.inserted_id}")
    
    # Close connection
    client.close()
    print("\n✓ Product added successfully to startup_template database!")

if __name__ == "__main__":
    asyncio.run(add_truemixx_radiance())
