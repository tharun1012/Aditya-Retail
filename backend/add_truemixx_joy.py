import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_truemixx_joy():
    """Add Bosch TrueMixx Joy 500W"""
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    products_collection = db.products
    
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch TrueMixx Joy Mixer Grinder 500W - Black (3 Jars)",
        "model_number": "MGM2133BIN",
        "brand": "Bosch",
        "category": "Mixer Grinder",
        "sub_category": "TrueMixx Joy Range",
        "price": 3196.00,
        "original_price": 5050.00,
        "currency": "INR",
        "stock_quantity": 35,
        "description": "Bosch TrueMixx Joy Mixer Grinder with 500W HiFlux Motor, 3 jars (Wet, Dry, Chutney), Pulse function, 3-speed control. Compact design with 37% discount - perfect entry-level choice.",
        "long_description": "The Bosch TrueMixx Joy MGM2133BIN is the perfect entry-level mixer grinder featuring 500W HiFlux Motor for high-torque performance. Compact design with 3 essential jars - 1.2L wet grinding jar with detachable blade, dry grinding jar with detachable blade, and chutney jar with fixed blade. Features pulse function for precise control and 3-stage speed settings. Limited stock available. Save 37%!",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/15805487_MGM2133BIN_STP_D_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/16464177_MGM2133BIN_TrueMixxJoy_Visual_F39_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/16464176_MGM2130WIN_TrueMixxJoy_White_fuge_main_unit_Jar_Coupler_v3_F39_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/16464174_MGM2133BIN_TrueMixxJoy_Black_fuge_main_unit_schraeg_F39_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/16464173_MGM2133BIN_TrueMixxJoy_Black_fuge_main_unit_frontal_F39_def.webp"
        ],
        "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/15805487_MGM2133BIN_STP_D_def.webp",
        "features": [
            "500W HiFlux Motor",
            "3 jars - Wet (1.2L), Dry, Chutney",
            "Pulse function for precise control",
            "3-stage speed control",
            "Compact design - 280x550x218 mm",
            "4-wing blade design",
            "Detachable wet and dry blades",
            "Fixed chutney blade",
            "Black color",
            "2 years warranty",
            "Limited stock - 37% off"
        ],
        "specifications": {
            "Dimensions": {"Size": "280 x 550 x 218 mm"},
            "Motor": {"Power": "500 W", "Type": "HiFlux Motor - High Torque"},
            "Jars": {
                "Total Jars": "3",
                "Wet Jar": "1.2L with detachable blade",
                "Dry Jar": "Detachable blade",
                "Chutney Jar": "Fixed blade"
            },
            "Control": {"Speed Settings": "3-stage", "Pulse Function": "Yes"},
            "Design": {
                "Body Material": "Plastic",
                "Color": "Black",
                "Blade Material": "Stainless steel - 4-wing"
            }
        },
        "highlights": [
            "TrueMixx Joy: Entry-level model with essential features",
            "Best Entry Price: ₹3,196 (Save 37% - was ₹5,050)",
            "Pulse Function: Precise control even in entry model",
            "Compact Design: Space-saving dimensions perfect for small kitchens",
            "Complete Jar Set: All essential jars included",
            "Limited Stock: Great value while stocks last"
        ],
        "ai_features": {
            "smart_recommendations": "Perfect for small families, bachelors, or first-time buyers. Ideal for basic daily grinding needs.",
            "usage_tips": [
                "Entry-level with all essential features",
                "Pulse function adds versatility",
                "1.2L wet jar for batters",
                "Dry jar for spices and masalas",
                "Chutney jar for small quantities",
                "3-speed control for different ingredients",
                "Compact size saves counter space",
                "Great value at 37% discount"
            ],
            "compatibility": "Standard 220-240V. Perfect for basic Indian kitchen needs."
        },
        "documents": [
            {
                "name": "User Manual",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MGM2133BIN"
            }
        ],
        "warranty": "2 years product warranty",
        "tags": ["mixer grinder", "truemixx joy", "bosch", "500w", "3 jars", "pulse", "entry level", "compact", "best value", "black"],
        "rating": 0.0,
        "reviews_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
        "discount_percentage": 37
    }
    
    try:
        result = await products_collection.insert_one(product)
        print(f"✅ Added {product['name']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Range: TrueMixx Joy (Entry Level)")
        print(f"   Power: {product['specifications']['Motor']['Power']}")
        print(f"   Jars: {product['specifications']['Jars']['Total Jars']}")
        print(f"   Price: ₹{product['price']:,.0f} (Save {product['discount_percentage']}% - was ₹{product['original_price']:,.0f})")
        print(f"   Stock: {product['stock_quantity']} units (Limited)")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_truemixx_joy())
