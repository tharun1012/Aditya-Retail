import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_wall_mounted_hood():
    """Add Bosch Wall-Mounted Hood DWA68IJ60I to the database"""
    
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        print("❌ MONGO_URL not found in environment variables")
        return
    
    client = AsyncIOMotorClient(mongo_url)
    db = client.ecommerce_db
    products_collection = db.products
    
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch Series 4 Wall-Mounted Cooker Hood 60 cm",
        "model_number": "DWA68IJ60I",
        "brand": "Bosch",
        "category": "Chimney",
        "sub_category": "Wall-Mounted Chimney",
        "price": 21490.00,
        "original_price": 21490.00,
        "currency": "INR",
        "stock_quantity": 20,
        "description": "Bosch Series 4 Wall-Mounted Cooker Hood with revolutionary Gesture Control technology and Auto Clean function. Features elegant black glass design with touchless operation and self-cleaning capability for effortless maintenance.",
        "long_description": "The Bosch DWA68IJ60I Series 4 Wall-Mounted Cooker Hood represents the perfect blend of innovative technology and elegant design. Featuring revolutionary Gesture Control, you can operate the hood with simple hand waves - no touching, no fingerprints. The Auto Clean Technology uses heat elements to melt grease automatically, collecting it in an easy-to-clean oil collector. With its sleek black glass body, 3-stage speed settings, and quiet 69 dB operation, this 60 cm hood is ideal for modern kitchens. The defined suction mode offers different fan speeds optimized for various cooking methods.",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/25909172_DWA68IJ60I_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25909168_DWA68IJ60I_PGA1_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25909167_DWA68IJ60I_PGA3_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25909169_DWA68IJ60I_PGA4_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25909173_DWA68IJ60I_PGA5_def.webp"
        ],
        "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/25909172_DWA68IJ60I_STP_def.webp",
        "features": [
            "Revolutionary Gesture Control - touchless operation",
            "Auto Clean Technology with heat-based self-cleaning",
            "Elegant black glass body design",
            "3-stage speed settings with boost mode",
            "Defined Suction Mode for different cooking styles",
            "Quiet operation at 69 dB max speed",
            "LED lighting with cold white (4000K) illumination",
            "No-return airflow flap included",
            "Delay shut-off function",
            "60 cm width - perfect for standard kitchens",
            "Lightweight design at 11.4 kg"
        ],
        "specifications": {
            "Dimensions": {
                "Width": "60 cm (600 mm)",
                "Height": "470 mm",
                "Depth": "340 mm",
                "Chimney Height": "450 mm",
                "Net Weight": "11.4 kg"
            },
            "Performance": {
                "Operating Mode": "Air extraction only",
                "Motor Power": "182 W",
                "Speed Settings": "3-stage + boost",
                "Sound Power at Max Speed": "69 dB"
            },
            "Installation": {
                "Installation Type": "Wall-mounted",
                "Distance to Electric Hob": "750 mm",
                "Distance to Gas Hob": "750 mm",
                "Power Cord Length": "130 cm",
                "No-return Airflow Flap": "Yes"
            },
            "Design": {
                "Color": "Black",
                "Material": "Premium Glass",
                "Series": "Series 4"
            },
            "Lighting": {
                "Type": "LED",
                "Color Temperature": "4000 K (Cold White)"
            },
            "Smart Features": {
                "Gesture Control": "Yes - Touchless operation",
                "Auto Clean Technology": "Yes - Heat-based self-cleaning",
                "Defined Suction Mode": "Yes",
                "Boost Position": "Yes",
                "Delay Shut-off": "Yes",
                "Remote Control": "No",
                "Home Connect": "No"
            }
        },
        "highlights": [
            "Gesture Control: Wave your hand to turn on/off - no touching, no fingerprints on the elegant glass surface",
            "Auto Clean Technology: Self-cleaning function uses heat to melt grease, collecting it in an easy-to-clean oil collector in just 10 minutes",
            "Defined Suction Mode: Different fan speeds optimized for various cooking methods - from gentle simmering to intensive frying",
            "Premium Glass Design: Elegant curved black glass body adds a sophisticated touch to your kitchen",
            "Quiet Performance: Only 69 dB at maximum speed ensures peaceful cooking experience",
            "Easy Maintenance: Combination of auto-clean technology and simple oil collector removal makes maintenance effortless"
        ],
        "ai_features": {
            "smart_recommendations": "Perfect for modern kitchens up to 150 sq ft with standard 60cm cooktops",
            "usage_tips": [
                "Use gesture control to avoid fingerprints on the glass surface",
                "Run Auto Clean function weekly for heavy cooking or monthly for regular use",
                "Wave hand right to turn on, left to turn off",
                "Empty oil collector after each auto-clean cycle",
                "Use defined suction modes for optimal performance based on cooking type",
                "Boost mode ideal for heavy frying or grilling",
                "Regular LED lighting provides excellent task illumination"
            ],
            "compatibility": "Suitable for both electric and gas cooktops with 750mm minimum distance"
        },
        "documents": [
            {
                "name": "User Manual",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/wall-mounted-hoods/DWA68IJ60I",
                "description": "Complete user manual with installation and operation instructions"
            },
            {
                "name": "Installation Instructions",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/wall-mounted-hoods/DWA68IJ60I",
                "description": "Detailed installation guide for wall-mounted hood"
            },
            {
                "name": "Product Specification Sheet",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/wall-mounted-hoods/DWA68IJ60I",
                "description": "Complete technical specifications"
            }
        ],
        "warranty": "2 years manufacturer warranty",
        "tags": ["chimney", "wall-mounted hood", "bosch", "series 4", "kitchen appliance", "black glass", "gesture control", "auto clean", "premium", "60cm", "touchless"],
        "rating": 0.0,
        "reviews_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
        "discount_percentage": 0
    }
    
    try:
        result = await products_collection.insert_one(product)
        print(f"✅ Successfully added Bosch Wall-Mounted Hood DWA68IJ60I")
        print(f"   Product ID: {product['id']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Price: ₹{product['price']:,.2f}")
        print(f"   Category: {product['category']} - {product['sub_category']}")
        print(f"   Special Features: Gesture Control, Auto Clean")
        print(f"   Images: {len(product['images'])} images added")
        
    except Exception as e:
        print(f"❌ Error adding product: {e}")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_wall_mounted_hood())
