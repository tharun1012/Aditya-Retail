import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_truemixx_premium():
    """Add Bosch TrueMixx Premium 750W Black with 5 Jars"""
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    products_collection = db.products
    
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch TrueMixx Premium Mixer Grinder 750W - Black (5 Jars)",
        "model_number": "MG6415A1KI",
        "brand": "Bosch",
        "category": "Mixer Grinder",
        "sub_category": "TrueMixx Range",
        "price": 6899.00,
        "original_price": 10990.00,
        "currency": "INR",
        "stock_quantity": 30,
        "description": "Bosch TrueMixx Premium Mixer Grinder with powerful 750W HiFlux Motor, 5 jars including unique Stone Pounding Blade, Active Flow Breaker technology, Pulse function. Ultimate grinding solution with 37% discount.",
        "long_description": "The Bosch TrueMixx Premium MG6415A1KI is the ultimate mixer grinder featuring revolutionary Stone Pounding Blade technology that replicates traditional pounding for authentic texture and taste. With 750W HiFlux Motor, Active Flow Breaker for enhanced aeration, and 5 specialized jars (1.5L Multipurpose, Chutney, Personal Blender, Plastic Blender with fruit filter), this is the most complete grinding solution. Features pulse function, 3-stage speed control, and includes spatula. Perfect 5-star rating. Save 37%!",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/25107720_K4358_MG6415A1KI_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25312727_MGxxxxA1KI_TrueMixx_FlowBreaker_top_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25312729_MGxxxxA1KI_TrueMixx_MultipurposeJar_CrossSection_StonePounding_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25313461_MGxxxxA1KI_TrueMixx_ChutneyChar_frontal_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25313463_MGxxxxA1KI_TrueMixx_MultipurposeJar_frontal_def.webp"
        ],
        "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/25107720_K4358_MG6415A1KI_STP_def.webp",
        "features": [
            "Powerful 750W HiFlux Motor",
            "5 jars - most complete set",
            "Unique Stone Pounding Blade - authentic texture",
            "Active Flow Breaker - finer, fluffier batters",
            "Pulse function for precise control",
            "3-stage speed control",
            "1.5L Multipurpose jar",
            "Chutney jar with fixed blade",
            "Personal blender jar",
            "Plastic blender with fruit filter",
            "4-wing blade design",
            "Includes spatula",
            "2 years warranty",
            "5-star rated",
            "Save 37%"
        ],
        "specifications": {
            "Dimensions": {
                "Size": "495 x 214 x 248 mm"
            },
            "Motor": {
                "Power": "750 W",
                "Type": "HiFlux Motor - High Performance"
            },
            "Jars": {
                "Total Jars": "5",
                "Multipurpose Jar": "1.5L with stone pounding blade",
                "Chutney Jar": "Fixed grinding blade",
                "Personal Blender": "On-the-go blending",
                "Plastic Blender": "With fruit filter",
                "Wet Jar": "Detachable blade"
            },
            "Control": {
                "Speed Settings": "3-stage",
                "Pulse Function": "Yes"
            },
            "Design": {
                "Body Material": "Plastic",
                "Color": "Black",
                "Blade Types": "4-wing, Stone pounding, Multipurpose, Chutney, Wet grinding"
            },
            "Technology": {
                "Stone Pounding Blade": "Blunt blade replicates traditional pounding",
                "Active Flow Breaker": "Enhanced aeration for finer batters"
            }
        },
        "highlights": [
            "Ultimate 5-Jar Set: Most comprehensive jar collection - multipurpose, chutney, personal blender, plastic blender, wet jar",
            "Revolutionary Stone Pounding: Unique blunt blade replicates traditional stone grinding for authentic taste and texture",
            "Active Flow Breaker: Innovative technology ensures finer, fluffier batters with enhanced aeration",
            "750W Power + Pulse: Professional-grade performance with precise pulse control",
            "Best Value: Save ₹4,091 (37% off) - ₹6,899 (was ₹10,990)",
            "Perfect 5-Star Rating: Highest customer satisfaction"
        ],
        "ai_features": {
            "smart_recommendations": "Ultimate choice for serious home chefs and large families. Perfect for complete Indian cooking needs - from batters to masalas to smoothies.",
            "usage_tips": [
                "Stone pounding blade for authentic masala texture",
                "Active Flow Breaker makes fluffiest dosa/idli batter",
                "Multipurpose 1.5L jar for large batch grinding",
                "Personal blender for smoothies and shakes",
                "Plastic blender with filter for fresh juices",
                "Chutney jar for small quantity grinding",
                "Pulse function for coarse grinding control",
                "5 jars cover all kitchen needs",
                "750W handles toughest ingredients",
                "Includes spatula for easy jar cleaning"
            ],
            "compatibility": "Standard 220-240V. Complete solution for all Indian kitchen grinding needs."
        },
        "documents": [
            {
                "name": "User Manual",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MG6415A1KI"
            },
            {
                "name": "Product Specification Sheet",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MG6415A1KI"
            }
        ],
        "warranty": "2 years product warranty",
        "tags": ["mixer grinder", "truemixx premium", "bosch", "750w", "5 jars", "stone pounding", "active flow breaker", "pulse", "best value", "black"],
        "rating": 5.0,
        "reviews_count": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
        "discount_percentage": 37
    }
    
    try:
        result = await products_collection.insert_one(product)
        print(f"✅ Added {product['name']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Power: {product['specifications']['Motor']['Power']}")
        print(f"   Jars: {product['specifications']['Jars']['Total Jars']}")
        print(f"   Special: Stone Pounding Blade + Active Flow Breaker")
        print(f"   Rating: ⭐{product['rating']}/5.0")
        print(f"   Price: ₹{product['price']:,.0f} (Save {product['discount_percentage']}% - was ₹{product['original_price']:,.0f})")
        print(f"   Stock: {product['stock_quantity']} units")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_truemixx_premium())
