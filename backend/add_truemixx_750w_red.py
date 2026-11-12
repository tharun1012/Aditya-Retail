import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_truemixx_750w_red():
    """Add Bosch TrueMixx 750W Red Mixer Grinder"""
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    products_collection = db.products
    
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch TrueMixx Pro Mixer Grinder 750W - Cranberry Red",
        "model_number": "MG4413C4PI",
        "brand": "Bosch",
        "category": "Mixer Grinder",
        "sub_category": "TrueMixx Range",
        "price": 5500.00,
        "original_price": 5500.00,
        "currency": "INR",
        "stock_quantity": 35,
        "description": "Bosch TrueMixx Pro Mixer Grinder with powerful 750W motor in stunning Cranberry Red color, 3 jars, 3-speed control. Premium high-power variant for demanding grinding tasks.",
        "long_description": "The Bosch TrueMixx Pro MG4413C4PI Mixer Grinder is the premium powerhouse of the TrueMixx range, featuring a robust 750W motor for heavy-duty grinding. The stunning Cranberry Red design makes a bold statement in your kitchen. Comes with 3 versatile jars - 1.2L wet grinding jar, dry grinding jar, and chutney jar, all with high-quality stainless steel blades. The enhanced motor power handles tough ingredients with ease, making it perfect for large families and extensive cooking needs. Rated 5.0/5.0 by customers for exceptional performance.",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/27058954_K5406_MG4413C4PI_STP_cranberry-red_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/24555961_MG2213C3BI_TrueMixx_pers_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/24555962_MG2213C3BI_TrueMixx_Serie2_visual_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/24620955_MG2213C1KI_TrueMixx_Chutney_Jar_CrossSection_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/24620956_MG2213C1KI_TrueMixx_Wet_Jar_CrossSection_def.webp"
        ],
        "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/27058954_K5406_MG4413C4PI_STP_cranberry-red_def.webp",
        "features": [
            "Powerful 750W motor - highest in range",
            "Stunning Cranberry Red color",
            "3 jars - Wet (1.2L), Dry, Chutney",
            "3-speed control settings",
            "Heavy-duty grinding capability",
            "Detachable stainless steel blades",
            "Fixed chutney grinding blade",
            "Premium build quality",
            "Compact dimensions: 300x190x255 mm",
            "2 years product warranty",
            "5-star customer rating"
        ],
        "specifications": {
            "Dimensions": {
                "Size": "300 x 190 x 255 mm",
                "Weight": "Lightweight plastic body"
            },
            "Motor": {
                "Power": "750 W",
                "Type": "High Torque Motor",
                "Motor Rating": "Heavy-duty performance"
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
                "Color": "Cranberry Red",
                "Blade Material": "Stainless steel"
            }
        },
        "highlights": [
            "Premium 750W Power: Most powerful model in TrueMixx range - handles toughest grinding tasks",
            "Stunning Cranberry Red: Bold, eye-catching color that stands out in modern kitchens",
            "Perfect 5-Star Rating: Highest customer satisfaction with 5.0/5.0 rating",
            "Heavy-Duty Performance: 750W motor grinds hardest spices and toughest ingredients effortlessly",
            "Complete Jar Set: 3 specialized jars for all grinding needs",
            "Premium Build: Enhanced durability for long-lasting performance"
        ],
        "ai_features": {
            "smart_recommendations": "Perfect for large families and heavy users. Ideal for grinding tough ingredients like turmeric, pepper, and hard spices. Best for commercial-level home cooking.",
            "usage_tips": [
                "750W power handles hardest spices and ingredients",
                "Perfect for large batch grinding",
                "Excellent for wet grinding of dal and rice for dosa/idli",
                "Dry jar handles whole spices and hard ingredients easily",
                "Chutney jar for coconut and small quantity grinding",
                "3-speed control for all grinding intensities",
                "Heavy-duty performance for daily extensive use",
                "Red color adds vibrant aesthetics to kitchen",
                "Detachable blades for thorough cleaning"
            ],
            "compatibility": "Standard 220-240V power supply. Handles all Indian kitchen ingredients including toughest spices."
        },
        "documents": [
            {
                "name": "User Manual",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MG4413C4PI",
                "description": "Complete user manual with operating instructions"
            },
            {
                "name": "Product Specification Sheet",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/mixer-grinders/truemixx-pro/MG4413C4PI",
                "description": "Complete technical specifications"
            }
        ],
        "warranty": "2 years product warranty",
        "tags": ["mixer grinder", "truemixx pro", "bosch", "750w", "3 jars", "indian kitchen", "red", "premium", "powerful", "best rated"],
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
        print(f"   Power: {product['specifications']['Motor']['Power']}")
        print(f"   Color: {product['specifications']['Design']['Color']}")
        print(f"   Rating: ⭐{product['rating']}/5.0 ({product['reviews_count']} review)")
        print(f"   Price: ₹{product['price']:,.0f}")
        print(f"   Stock: {product['stock_quantity']} units")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_truemixx_750w_red())
