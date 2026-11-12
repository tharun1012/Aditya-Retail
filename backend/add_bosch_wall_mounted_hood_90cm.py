import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_wall_mounted_hood_90cm():
    """Add Bosch Wall-Mounted Hood DWA98IJ60I (90cm) to the database"""
    
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        print("❌ MONGO_URL not found in environment variables")
        return
    
    client = AsyncIOMotorClient(mongo_url)
    db = client.ecommerce_db
    products_collection = db.products
    
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch Series 4 Wall-Mounted Cooker Hood 90 cm",
        "model_number": "DWA98IJ60I",
        "brand": "Bosch",
        "category": "Chimney",
        "sub_category": "Wall-Mounted Chimney",
        "price": 23990.00,
        "original_price": 23990.00,
        "currency": "INR",
        "stock_quantity": 18,
        "description": "Bosch Series 4 Wall-Mounted Cooker Hood 90 cm with revolutionary Gesture Control technology and Auto Clean function. Features powerful 1200-1300 m³/h extraction rate with elegant black glass design and touchless operation.",
        "long_description": "The Bosch DWA98IJ60I Series 4 Wall-Mounted Cooker Hood combines powerful performance with innovative technology in a sleek 90 cm design. Featuring revolutionary Gesture Control for touchless operation and Auto Clean Technology that uses heat to melt grease automatically, this hood makes maintenance effortless. With an impressive extraction rate of 1200-1300 m³/h, it efficiently removes cooking odors and steam even during heavy cooking. The elegant black glass body, 3-stage speed settings, and quiet 69 dB operation make it perfect for modern kitchens. The defined suction mode offers optimized fan speeds for different cooking methods.",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/25909175_DWA98IJ60I_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25909170_DWA98IJ60I_PGA1_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25909171_DWA98IJ60I_PGA3_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25909174_DWA98IJ60I_PGA4_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25909176_DWA98IJ60I_PGA5_def.webp"
        ],
        "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/25909175_DWA98IJ60I_STP_def.webp",
        "features": [
            "Revolutionary Gesture Control - touchless operation",
            "Auto Clean Technology with heat-based self-cleaning",
            "Powerful 1200-1300 m³/h extraction rate",
            "Elegant black glass body design",
            "3-stage speed settings with boost mode",
            "Defined Suction Mode for different cooking styles",
            "Quiet operation at 69 dB max speed",
            "Energy-efficient LED lighting (3W) with cold white illumination",
            "No-return airflow flap included",
            "Delay shut-off function",
            "90 cm width - ideal for wider cooktops",
            "Lightweight design at 13.2 kg"
        ],
        "specifications": {
            "Dimensions": {
                "Width": "90 cm (900 mm)",
                "Height": "420 mm",
                "Depth": "420 mm",
                "Chimney Height": "450 mm",
                "Net Weight": "13.2 kg"
            },
            "Performance": {
                "Operating Mode": "Air extraction only",
                "Extraction Rate": "1200-1300 m³/h (as per IS 374*)",
                "Motor Power": "180 W",
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
                "Power": "3 W",
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
            "Powerful Performance: 1200-1300 m³/h extraction rate efficiently handles heavy cooking and larger cooktops",
            "Gesture Control: Wave your hand to turn on/off - no touching, no fingerprints on the elegant glass surface",
            "Auto Clean Technology: Self-cleaning function uses heat to melt grease, collecting it in an easy-to-clean oil collector in just 10 minutes",
            "Defined Suction Mode: Different fan speeds optimized for various cooking methods - from gentle simmering to intensive frying",
            "Premium Glass Design: Elegant curved black glass body with 90 cm width adds sophistication to spacious kitchens",
            "Quiet Performance: Only 69 dB at maximum speed despite powerful extraction capacity"
        ],
        "ai_features": {
            "smart_recommendations": "Perfect for modern kitchens up to 200 sq ft with 90cm cooktops",
            "usage_tips": [
                "Use gesture control to avoid fingerprints on the glass surface",
                "Run Auto Clean function weekly for heavy cooking or monthly for regular use",
                "Wave hand right to turn on, left to turn off",
                "Empty oil collector after each auto-clean cycle",
                "Use defined suction modes for optimal performance based on cooking type",
                "Powerful extraction ideal for Indian cooking with heavy spices and frying",
                "Boost mode handles multiple burners operating simultaneously",
                "Energy-efficient 3W LED provides excellent illumination"
            ],
            "compatibility": "Suitable for both electric and gas cooktops with 750mm minimum distance"
        },
        "documents": [
            {
                "name": "User Manual",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/wall-mounted-hoods/DWA98IJ60I",
                "description": "Complete user manual with installation and operation instructions"
            },
            {
                "name": "Installation Instructions",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/wall-mounted-hoods/DWA98IJ60I",
                "description": "Detailed installation guide for 90cm wall-mounted hood"
            },
            {
                "name": "Product Specification Sheet",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/wall-mounted-hoods/DWA98IJ60I",
                "description": "Complete technical specifications"
            }
        ],
        "warranty": "2 years manufacturer warranty",
        "tags": ["chimney", "wall-mounted hood", "bosch", "series 4", "kitchen appliance", "black glass", "gesture control", "auto clean", "premium", "90cm", "touchless", "powerful"],
        "rating": 0.0,
        "reviews_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
        "discount_percentage": 0
    }
    
    try:
        result = await products_collection.insert_one(product)
        print(f"✅ Successfully added Bosch Wall-Mounted Hood DWA98IJ60I (90cm)")
        print(f"   Product ID: {product['id']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Price: ₹{product['price']:,.2f}")
        print(f"   Category: {product['category']} - {product['sub_category']}")
        print(f"   Width: 90 cm")
        print(f"   Extraction Rate: 1200-1300 m³/h")
        print(f"   Special Features: Gesture Control, Auto Clean")
        print(f"   Images: {len(product['images'])} images added")
        
    except Exception as e:
        print(f"❌ Error adding product: {e}")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_wall_mounted_hood_90cm())
