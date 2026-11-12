import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_truemixx_pro_1000w():
    """Add Bosch TrueMixx Pro 1000W - Top Tier Model"""
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    products_collection = db.products
    
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch TrueMixx Pro Mixer Grinder 1000W - Black (4 Jars)",
        "model_number": "MG8724A1KI",
        "brand": "Bosch",
        "category": "Mixer Grinder",
        "sub_category": "TrueMixx Range",
        "price": 11250.00,
        "original_price": 11250.00,
        "currency": "INR",
        "stock_quantity": 25,
        "description": "Bosch TrueMixx Pro with powerful 1000W Ball Bearing Motor, 4 jars, Stone Pounding Blade, Active Flow Breaker, 60-minute motor rating. Top-tier professional-grade mixer grinder.",
        "long_description": "The Bosch TrueMixx Pro MG8724A1KI is the ultimate professional-grade mixer grinder with powerful 1000W ball bearing motor designed for high torque and superior performance. Features 60-minute motor rating for extended grinding sessions. Includes Stone Pounding Blade for authentic texture, Active Flow Breaker for finer batters, and 4 premium jars (1.5L Multipurpose, Wet, Chutney, Plastic Blender with fruit filter). Pulse function and 3-stage speed control. Perfect 5-star rating. Most powerful in the range!",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/25352631_K4360_MG8724A1KI_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25312727_MGxxxxA1KI_TrueMixx_FlowBreaker_top_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25312729_MGxxxxA1KI_TrueMixx_MultipurposeJar_CrossSection_StonePounding_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25313461_MGxxxxA1KI_TrueMixx_ChutneyChar_frontal_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25313463_MGxxxxA1KI_TrueMixx_MultipurposeJar_frontal_def.webp"
        ],
        "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/25352631_K4360_MG8724A1KI_STP_def.webp",
        "features": [
            "Powerful 1000W Ball Bearing Motor - Most powerful",
            "60-minute motor rating - Extended operation",
            "4 premium jars",
            "Stone Pounding Blade - authentic texture",
            "Active Flow Breaker - finer batters",
            "Pulse function",
            "3-stage speed control",
            "1.5L Multipurpose jar",
            "Wet grinding jar",
            "Chutney jar with fixed blade",
            "Plastic blender with fruit filter",
            "4-wing blade design",
            "Professional-grade performance",
            "2 years warranty",
            "5-star rated"
        ],
        "specifications": {
            "Dimensions": {"Size": "495 x 214 x 248 mm"},
            "Motor": {
                "Power": "1000 W",
                "Type": "Ball Bearing Motor - High Torque",
                "Motor Rating": "60 minutes continuous operation"
            },
            "Jars": {
                "Total Jars": "4",
                "Multipurpose Jar": "1.5L with stone pounding blade",
                "Wet Jar": "Detachable blade",
                "Chutney Jar": "Fixed grinding blade",
                "Plastic Blender": "With fruit filter"
            },
            "Control": {"Speed Settings": "3-stage", "Pulse Function": "Yes"},
            "Design": {
                "Body Material": "Plastic",
                "Color": "Black",
                "Blade Types": "4-wing, Stone pounding, Multipurpose, Chutney, Wet grinding"
            },
            "Technology": {
                "Ball Bearing Motor": "Professional-grade 1000W for maximum performance",
                "Stone Pounding Blade": "Authentic traditional grinding texture",
                "Active Flow Breaker": "Finer, fluffier batters"
            }
        },
        "highlights": [
            "Most Powerful: 1000W Ball Bearing Motor - professional-grade performance for toughest ingredients",
            "60-Minute Rating: Extended continuous operation - perfect for large batch grinding",
            "Stone Pounding Technology: Authentic texture and taste like traditional stone grinding",
            "Active Flow Breaker: Innovative technology for finest, fluffiest batters",
            "Professional Grade: Ball bearing motor ensures durability and high torque",
            "Perfect 5-Star Rating: Ultimate customer satisfaction"
        ],
        "ai_features": {
            "smart_recommendations": "Ultimate choice for professional home chefs, large families, and heavy users. Perfect for commercial-level home cooking and catering.",
            "usage_tips": [
                "1000W handles hardest ingredients effortlessly",
                "60-minute rating for large batch grinding",
                "Ball bearing motor ensures long life",
                "Stone pounding for authentic masala texture",
                "Active Flow Breaker for restaurant-quality batters",
                "Multipurpose 1.5L jar for bulk grinding",
                "Plastic blender with filter for fresh juices",
                "Pulse function for precise control",
                "Professional performance for daily heavy use"
            ],
            "compatibility": "Standard 220-240V. Professional-grade solution for all grinding needs."
        },
        "documents": [
            {
                "name": "User Manual",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MG8724A1KI"
            }
        ],
        "warranty": "2 years product warranty",
        "tags": ["mixer grinder", "truemixx pro", "bosch", "1000w", "4 jars", "ball bearing", "professional", "most powerful", "black"],
        "rating": 5.0,
        "reviews_count": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
        "discount_percentage": 0
    }
    
    try:
        result = await products_collection.insert_one(product)
        print(f"✅ Added {product['name']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Power: {product['specifications']['Motor']['Power']} (MOST POWERFUL)")
        print(f"   Motor Type: Ball Bearing Motor")
        print(f"   Motor Rating: 60 minutes")
        print(f"   Jars: {product['specifications']['Jars']['Total Jars']}")
        print(f"   Rating: ⭐{product['rating']}/5.0")
        print(f"   Price: ₹{product['price']:,.0f}")
        print(f"   Stock: {product['stock_quantity']} units")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_truemixx_pro_1000w())
