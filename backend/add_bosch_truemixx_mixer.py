import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_truemixx_mixer():
    """Add Bosch TrueMixx Mixer Grinder to the database"""
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    products_collection = db.products
    
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch TrueMixx Mixer Grinder 500W - Black",
        "model_number": "MG2213C1KI",
        "brand": "Bosch",
        "category": "Mixer Grinder",
        "sub_category": "TrueMixx Range",
        "price": 2600.00,
        "original_price": 4000.00,
        "currency": "INR",
        "stock_quantity": 50,
        "description": "Bosch TrueMixx Mixer Grinder with powerful 500W HiFlux Motor, 3 jars (Wet, Dry, Chutney), 3-speed control with 60-minute motor rating. Perfect for Indian kitchen needs.",
        "long_description": "The Bosch TrueMixx MG2213C1KI Mixer Grinder is designed to deliver exceptional performance with its powerful 500W HiFlux Motor that provides high torque for efficient grinding. Comes with 3 versatile jars - a 1.2L wet grinding jar with detachable stainless steel blade, a dry grinding jar with detachable blade, and a chutney jar with fixed grinding blade. The 3-stage speed control allows you to adjust grinding intensity based on your requirements. With 60 minutes motor rating and 2 years warranty, this mixer grinder is built for daily Indian cooking needs.",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/24593362_K4318_MG2213C1KI_23348342_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/24555925_MG2213C1KI_TrueMixx_Serie_visual_02_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/24555926_MG2213C1KI_TrueMixx_Serie2_visual_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/24555940_MG2213C1KI_TrueMixx_pers_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/24593361_K4318_MG2213C1KI_23348342_5_def.webp"
        ],
        "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/24593362_K4318_MG2213C1KI_23348342_def.webp",
        "features": [
            "Powerful 500W HiFlux Motor",
            "High torque for efficient grinding",
            "3 jars - Wet (1.2L), Dry, Chutney",
            "3-speed control settings",
            "60 minutes motor rating",
            "Detachable stainless steel blades",
            "Fixed chutney grinding blade",
            "Plastic body - durable and lightweight",
            "Compact dimensions: 300x190x255 mm",
            "2 years product warranty",
            "Perfect for Indian kitchen"
        ],
        "specifications": {
            "Dimensions": {
                "Size": "300 x 190 x 255 mm",
                "Weight": "Lightweight plastic body"
            },
            "Motor": {
                "Power": "500 W",
                "Type": "HiFlux Motor - High Torque",
                "Motor Rating": "60 minutes continuous operation"
            },
            "Jars": {
                "Total Jars": "3",
                "Wet Jar": "1.2L capacity with detachable blade",
                "Dry Jar": "Detachable stainless steel blade",
                "Chutney Jar": "Fixed grinding blade"
            },
            "Control": {
                "Speed Settings": "3-stage",
                "Pulse Function": "No"
            },
            "Design": {
                "Body Material": "Plastic",
                "Color": "Black",
                "Blade Material": "Stainless steel"
            }
        },
        "highlights": [
            "HiFlux Motor Technology: 500W high-torque motor designed for superior grinding performance",
            "Complete Jar Set: 3 specialized jars for all your grinding needs - wet, dry, and chutney",
            "60 Minute Rating: Continuous operation capability for extended grinding sessions",
            "Detachable Blades: Easy to clean and maintain stainless steel blades",
            "3-Speed Control: Adjust grinding intensity based on ingredients",
            "Best Value: Save 35% - ₹2,600 (was ₹4,000)"
        ],
        "ai_features": {
            "smart_recommendations": "Perfect for Indian households. Ideal for daily grinding of masalas, chutneys, and batters.",
            "usage_tips": [
                "Use chutney jar for coconut chutney and small quantity grinding",
                "Dry jar perfect for masala powders and spices",
                "Wet jar ideal for batter grinding (dosa, idli)",
                "3-speed control: Low for delicate grinding, High for tough ingredients",
                "60-minute motor rating allows continuous operation",
                "Detachable blades make cleaning easy",
                "Add water gradually for smooth paste consistency",
                "Use pulse action by switching on/off for coarse grinding"
            ],
            "compatibility": "Standard 220-240V power supply. Works with all Indian kitchen ingredients."
        },
        "documents": [
            {
                "name": "User Manual",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MG2213C1KI",
                "description": "Complete user manual with operating instructions"
            },
            {
                "name": "Product Specification Sheet",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MG2213C1KI",
                "description": "Complete technical specifications"
            }
        ],
        "warranty": "2 years product warranty",
        "tags": ["mixer grinder", "truemixx", "bosch", "500w", "3 jars", "indian kitchen", "best value", "black"],
        "rating": 3.0,
        "reviews_count": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
        "discount_percentage": 35
    }
    
    try:
        result = await products_collection.insert_one(product)
        print(f"✅ Successfully added {product['name']}")
        print(f"   Product ID: {product['id']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Motor: {product['specifications']['Motor']['Power']}")
        print(f"   Jars: {product['specifications']['Jars']['Total Jars']}")
        print(f"   Price: ₹{product['price']:,.2f} (Save {product['discount_percentage']}% - was ₹{product['original_price']:,.2f})")
        print(f"   Rating: ⭐{product['rating']}/5.0 ({product['reviews_count']} reviews)")
        print(f"   Stock: {product['stock_quantity']} units")
        print(f"   Images: {len(product['images'])} images added")
        
    except Exception as e:
        print(f"❌ Error adding product: {e}")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_truemixx_mixer())
