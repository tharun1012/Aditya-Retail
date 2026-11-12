import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

async def add_truemixx_pro_1000w_green():
    # Get MongoDB connection string
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client['startup_template']
    products_collection = db['products']
    
    # Product data for Bosch TrueMixx Pro 1000W Green (MGM8842GIN)
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch TrueMixx Pro Mixer Grinder 1000W - Green",
        "model_number": "MGM8842GIN",
        "brand": "Bosch",
        "category": "Mixer Grinder",
        "subcategory": "TrueMixx Pro",
        "price": 7584.00,
        "original_price": 11130.00,
        "currency": "INR",
        "in_stock": True,
        "stock_quantity": 22,
        "rating": 3.5,
        "reviews_count": 24,
        "short_description": "Powerful 1000W ball bearing motor with stone pounding blade and active flow breaker technology",
        "long_description": "The Bosch TrueMixx Pro Mixer Grinder features a powerful 1000W ball bearing motor designed to deliver high torque for exceptional grinding performance. Its uniquely designed blunt pounding blade with thick edges replicates the pounding effect on dry ingredients, giving authentic texture and taste. The innovative Active Flow Breaker guarantees finer, fluffier batters with enhanced aeration. Comes in an elegant green finish with comprehensive accessories.",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/14916338_MGM8842GIN_STP_D_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/15810587_BO_U_16_other_TrueMixx_Pro_MGM8842GIN_picture_KF1_front_ENG_010720_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/15810589_BO_U_16_other_TrueMixx_Pro_MGM8842GIN_picture_nKF_blender_blade_ENG_010720_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/15810555_BO_U_16_other_TrueMixx_Pro_MGM8842GIN_picture_KF3_with_accessories_ENG_010720_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/15810557_BO_U_16_other_TrueMixx_Pro_MGM8842GIN_picture_KF2_perspective_ENG_010720_def.webp"
        ],
        "key_features": [
            "1000W ball bearing motor for high torque",
            "Stone pounding blade for authentic texture and taste",
            "Active Flow Breaker for finer, fluffier batters",
            "1.5L capacity liquidizing jar",
            "3-stage speed settings",
            "Pulse function for precise control",
            "4-wing stainless steel blades",
            "Elegant green color",
            "Complete accessory set included",
            "Free delivery",
            "2 years comprehensive warranty"
        ],
        "specifications": {
            "Power": "1000W",
            "Motor Type": "Ball bearing motor",
            "Capacity": "1.5 L",
            "Speed Settings": "3-stage",
            "Pulse Function": "Yes",
            "Color": "Green",
            "Dimensions": "495 x 210 x 219 mm",
            "Blade Design": "4-wing blade, Stone pounding blade, Chutney Grinding Blade (Fixed), Dry grinding blade (detachable), Wet Grinding Blade (detachable)",
            "Blade Material": "Stainless Steel",
            "Warranty": "2 years"
        },
        "warranty": "2 years comprehensive warranty",
        "free_delivery": True,
        "product_url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MGM8842GIN"
    }
    
    # Check if product already exists
    existing = await products_collection.find_one({"model_number": product["model_number"]})
    if existing:
        print(f"⚠️  Product {product['model_number']} already exists in database")
        client.close()
        return
    
    # Insert product
    result = await products_collection.insert_one(product)
    discount = int((1 - product['price']/product['original_price']) * 100)
    
    print(f"✓ Added product: {product['name']}")
    print(f"  Model: {product['model_number']}")
    print(f"  Price: ₹{product['price']:,.2f} (Original: ₹{product['original_price']:,.2f})")
    print(f"  Discount: {discount}%")
    print(f"  Rating: {product['rating']}/5 ({product['reviews_count']} reviews)")
    print(f"  Color: Green")
    print(f"  Product ID: {product['id']}")
    print(f"  MongoDB ID: {result.inserted_id}")
    
    # Close connection
    client.close()
    print("\n✓ Product added successfully to startup_template database!")

if __name__ == "__main__":
    asyncio.run(add_truemixx_pro_1000w_green())
