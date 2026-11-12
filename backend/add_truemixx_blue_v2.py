import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_truemixx_blue_v2_mixer():
    """Add Bosch TrueMixx Mixer Grinder Blue V2 to the database"""
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    products_collection = db.products
    
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch TrueMixx Pro Mixer Grinder 500W - Blue",
        "model_number": "MG2213C4BI",
        "brand": "Bosch",
        "category": "Mixer Grinder",
        "sub_category": "TrueMixx Range",
        "price": 4290.00,
        "original_price": 4290.00,
        "currency": "INR",
        "stock_quantity": 40,
        "description": "Bosch TrueMixx Pro Mixer Grinder with powerful 500W HiFlux Motor in Blue, 3 jars, 3-speed control with 60-minute motor rating.",
        "long_description": "The Bosch TrueMixx Pro MG2213C4BI Mixer Grinder features a stylish Blue design with 500W HiFlux Motor. Premium variant with 3 jars - 1.2L wet, dry, and chutney grinding jars. Built for daily Indian cooking needs.",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/27058950_K5404_MG2213C4BI_STP_blue_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/24555961_MG2213C3BI_TrueMixx_pers_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/24555962_MG2213C3BI_TrueMixx_Serie2_visual_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/24555960_MG2213C3BI_TrueMixx_Serie2_visual_02_def.webp"
        ],
        "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/27058950_K5404_MG2213C4BI_STP_blue_def.webp",
        "features": [
            "500W HiFlux Motor",
            "3 jars - Wet (1.2L), Dry, Chutney",
            "3-speed control",
            "60 minutes motor rating",
            "Detachable stainless steel blades",
            "Blue color design",
            "2 years warranty"
        ],
        "specifications": {
            "Dimensions": {"Size": "300 x 190 x 255 mm"},
            "Motor": {"Power": "500 W", "Type": "HiFlux Motor", "Motor Rating": "60 minutes"},
            "Jars": {"Total Jars": "3", "Wet Jar": "1.2L", "Dry Jar": "Yes", "Chutney Jar": "Yes"},
            "Control": {"Speed Settings": "3-stage", "Pulse Function": "No"},
            "Design": {"Body Material": "Plastic", "Color": "Blue", "Blade Material": "Stainless steel"}
        },
        "highlights": [
            "TrueMixx Pro: Premium variant",
            "500W HiFlux Motor for superior grinding",
            "3 specialized jars",
            "60 minute continuous operation",
            "Stylish Blue design"
        ],
        "ai_features": {
            "smart_recommendations": "Perfect for Indian households. Ideal for daily grinding.",
            "usage_tips": ["Chutney jar for small quantities", "Dry jar for spices", "Wet jar for batters"],
            "compatibility": "Standard 220-240V power supply"
        },
        "documents": [{"name": "User Manual", "type": "PDF", "url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MG2213C4BI"}],
        "warranty": "2 years product warranty",
        "tags": ["mixer grinder", "truemixx pro", "bosch", "500w", "blue", "premium"],
        "rating": 0.0,
        "reviews_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
        "discount_percentage": 0
    }
    
    try:
        result = await products_collection.insert_one(product)
        print(f"✅ Added {product['name']}")
        print(f"   Model: {product['model_number']} | Price: ₹{product['price']:,.0f} | Stock: {product['stock_quantity']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_truemixx_blue_v2_mixer())
