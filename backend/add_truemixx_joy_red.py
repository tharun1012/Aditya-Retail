import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

async def add_truemixx_joy_red():
    # Get MongoDB connection string
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client['startup_template']
    products_collection = db['products']
    
    # Product data for Bosch TrueMixx Joy 500W Red (MGM2133RIN)
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch TrueMixx Joy Mixer Grinder 500W",
        "model_number": "MGM2133RIN",
        "brand": "Bosch",
        "category": "Mixer Grinders",
        "subcategory": "TrueMixx Pro",
        "price": 3196.00,
        "original_price": 5050.00,
        "currency": "INR",
        "in_stock": True,
        "stock_quantity": 15,
        "rating": 3.3,
        "reviews_count": 3,
        "short_description": "Powerful 500W HiFlux Motor for high performance grinding with 2 years warranty",
        "long_description": "The Bosch TrueMixx Joy Mixer Grinder delivers powerful performance with its 500W HiFlux Motor designed to provide high torque for efficient grinding. This versatile mixer grinder comes in an attractive red color and includes multiple jars for various grinding needs. With 3-stage speed settings and pulse function, it offers precise control for all your kitchen tasks.",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/21348203_21572856_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21690486_BO_U_16_other_TrueMixx_MGM4331RIN_picture_nKF_spatula_ENG_290518_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21690489_BO_U_16_other_TrueMixx_MGM2130RIN_picture_nKF_dry_jar_ENG_230219_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21690487_BO_U_16_other_TrueMixx_MGM2130RIN_picture_nKF_chutney_jar_ENG_230219_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21692570_BO_U_16_other_TrueMixx_MGM2130RIN_picture_nKF_visual_2_ENG_230219_def.webp"
        ],
        "key_features": [
            "500W HiFlux Motor - High torque for efficient grinding",
            "1.2L capacity liquidizing jar",
            "3-stage speed settings for precise control",
            "Pulse function for quick bursts",
            "4-wing stainless steel blade for wet grinding",
            "Separate blades for dry and chutney grinding",
            "Durable plastic body",
            "Free delivery available",
            "2 years product warranty"
        ],
        "specifications": {
            "Power": "500W",
            "Voltage": "230V",
            "Frequency": "50Hz",
            "Capacity": "1.2 L",
            "Speed Settings": "3-stage",
            "Pulse Function": "Yes",
            "Material": "Plastic body",
            "Color": "Red",
            "Dimensions": "280 x 550 x 218 mm (W x H x D)",
            "Blade Design": "4-wing blade, Chutney Grinding Blade (Fixed), Dry grinding blade (detachable), Wet Grinding Blade (detachable)",
            "Blade Material": "Stainless Steel",
            "Warranty": "2 years"
        },
        "warranty": "2 years comprehensive warranty",
        "free_delivery": True,
        "product_url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MGM2133RIN"
    }
    
    # Insert product
    result = await products_collection.insert_one(product)
    print(f"✓ Added product: {product['name']}")
    print(f"  Model: {product['model_number']}")
    print(f"  Price: ₹{product['price']:,.2f} (Original: ₹{product['original_price']:,.2f})")
    print(f"  Product ID: {product['id']}")
    print(f"  MongoDB ID: {result.inserted_id}")
    
    # Close connection
    client.close()
    print("\n✓ Product added successfully to startup_template database!")

if __name__ == "__main__":
    asyncio.run(add_truemixx_joy_red())
