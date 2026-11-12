import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

async def add_truemixx_750w_green():
    # Get MongoDB connection string
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client['startup_template']
    products_collection = db['products']
    
    # Product data for Bosch TrueMixx 750W Green (MG4413C4GI)
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch TrueMixx Pro Mixer Grinder 750W - Mint Green",
        "model_number": "MG4413C4GI",
        "brand": "Bosch",
        "category": "Mixer Grinder",
        "subcategory": "TrueMixx Pro",
        "price": 5500.00,
        "original_price": 5500.00,
        "currency": "INR",
        "in_stock": True,
        "stock_quantity": 30,
        "rating": 5.0,
        "reviews_count": 1,
        "short_description": "Versatile 750W mixer grinder perfect for daily grinding and blending tasks",
        "long_description": "The Bosch TrueMixx Pro Mixer Grinder in elegant Mint Green features a powerful 750W motor designed for efficient grinding and blending. With a 1.2L capacity liquidizing jar and multiple jars for different grinding needs, this mixer grinder handles all your kitchen tasks with ease. The 3-stage speed settings provide precise control, while the durable stainless steel blades ensure long-lasting performance. The compact design with premium finish makes it a stylish addition to any modern kitchen.",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/27058951_K5405_MG4413C4GI_STP_mintgreen_def.webp"
        ],
        "key_features": [
            "750W powerful motor for efficient grinding",
            "1.2L liquidizing jar capacity",
            "Stylish Mint Green color",
            "Sharp stainless steel blades",
            "3-speed settings for precise control",
            "Ergonomic handles for easy grip",
            "Compact design with premium finish",
            "Durable plastic body",
            "Free delivery available",
            "2 years product warranty"
        ],
        "specifications": {
            "Power": "750W",
            "Voltage": "230V",
            "Frequency": "50Hz",
            "Capacity": "1.2 L",
            "Speed Settings": "3-stage",
            "Pulse Function": "No",
            "Material": "Plastic body",
            "Color": "Mint Green",
            "Dimensions": "300 x 190 x 255 mm (W x H x D)",
            "Blade Design": "Chutney Grinding Blade (Fixed), Dry grinding blade (detachable), Wet Grinding Blade (detachable)",
            "Blade Material": "Stainless Steel",
            "Warranty": "2 years"
        },
        "warranty": "2 years comprehensive warranty",
        "free_delivery": True,
        "product_url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MG4413C4GI"
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
    print(f"  Price: ₹{product['price']:,.2f}")
    print(f"  Rating: {product['rating']} ({product['reviews_count']} review)")
    print(f"  Color: Mint Green")
    print(f"  Product ID: {product['id']}")
    print(f"  MongoDB ID: {result.inserted_id}")
    
    # Close connection
    client.close()
    print("\n✓ Product added successfully to startup_template database!")

if __name__ == "__main__":
    asyncio.run(add_truemixx_750w_green())
