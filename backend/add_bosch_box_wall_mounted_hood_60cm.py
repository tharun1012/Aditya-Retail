import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_box_wall_mounted_hood_60cm():
    """Add Bosch Box Wall-Mounted Hood DWB68IJ60I (60cm) to the database"""
    
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        print("❌ MONGO_URL not found in environment variables")
        return
    
    client = AsyncIOMotorClient(mongo_url)
    db = client.ecommerce_db
    products_collection = db.products
    
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch Series 4 Box Wall-Mounted Cooker Hood 60 cm",
        "model_number": "DWB68IJ60I",
        "brand": "Bosch",
        "category": "Chimney",
        "sub_category": "Wall-Mounted Chimney",
        "price": 29990.00,
        "original_price": 29990.00,
        "currency": "INR",
        "stock_quantity": 18,
        "description": "Bosch Series 4 Box Wall-Mounted Cooker Hood 60 cm with Gesture Control and Auto Clean Technology. Features powerful 1200-1300 m³/h extraction rate with elegant black glass box design, perfect for standard kitchens.",
        "long_description": "The Bosch DWB68IJ60I Series 4 Box Wall-Mounted Cooker Hood combines premium box styling with cutting-edge technology in a compact 60 cm design. Featuring revolutionary Gesture Control for touchless operation and Auto Clean Technology that uses heat to melt grease automatically, this hood makes maintenance effortless. With an impressive extraction rate of 1200-1300 m³/h, it efficiently removes cooking odors and steam even during heavy cooking. The defined suction mode offers optimized fan speeds for different cooking methods - Boiling, Cooking, and Frying. The elegant black glass box body, quiet 69 dB operation, and energy-efficient LED lighting make it perfect for modern standard-sized kitchens.",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/25909177_DWB68IJ60I_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25909178_DWB68IJ60I_PGA1_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25909180_DWB68IJ60I_PGA3_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25909179_DWB68IJ60I_PGA4_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25909182_DWB68IJ60I_PGA5_def.webp"
        ],
        "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/25909177_DWB68IJ60I_STP_def.webp",
        "features": [
            "Revolutionary Gesture Control - touchless operation",
            "Auto Clean Technology with heat-based self-cleaning",
            "Powerful 1200-1300 m³/h extraction rate",
            "Elegant black glass box design",
            "Defined Suction Mode - optimized for Boiling, Cooking, Frying",
            "3-stage speed settings with boost mode",
            "Quiet operation at 69 dB max speed",
            "Energy-efficient LED lighting (3W) with cold white illumination",
            "Touch control panel",
            "Delay shut-off function",
            "60 cm width - ideal for standard cooktops",
            "Lightweight box design at 11.9 kg",
            "130 cm power cord for flexible installation"
        ],
        "specifications": {
            "Dimensions": {
                "Width": "60 cm (600 mm)",
                "Height": "470 mm",
                "Depth": "450 mm",
                "Chimney Height": "450 mm",
                "Net Weight": "11.9 kg"
            },
            "Performance": {
                "Operating Mode": "Air extraction only",
                "Extraction Rate": "1200-1300 m³/h (as per IS 374*)",
                "Motor Power": "180 W",
                "Speed Settings": "3-stage + boost",
                "Sound Power at Max Speed": "69 dB",
                "Defined Suction Modes": "Boiling, Cooking, Frying"
            },
            "Installation": {
                "Installation Type": "Wall-mounted (Box style)",
                "Distance to Electric Hob": "750 mm",
                "Distance to Gas Hob": "750 mm",
                "Power Cord Length": "130 cm",
                "No-return Airflow Flap": "No"
            },
            "Design": {
                "Color": "Black",
                "Material": "Premium Glass",
                "Series": "Series 4",
                "Style": "Box Design"
            },
            "Lighting": {
                "Type": "LED",
                "Power": "3 W",
                "Color Temperature": "4000 K (Cold White)"
            },
            "Smart Features": {
                "Gesture Control": "Yes - Touchless operation",
                "Auto Clean Technology": "Yes - Heat-based self-cleaning",
                "Defined Suction Mode": "Yes - Boiling, Cooking, Frying modes",
                "Boost Position": "Yes",
                "Delay Shut-off": "Yes",
                "Touch Control": "Yes",
                "Remote Control": "No",
                "Home Connect": "No"
            }
        },
        "highlights": [
            "Powerful Compact Design: 1200-1300 m³/h extraction rate in a 60 cm box design - perfect for standard kitchens",
            "Dual Smart Control: Gesture Control for touchless operation and Touch Control for precise settings",
            "Auto Clean Technology: Self-cleaning function uses heat to melt grease, collecting it in an easy-to-clean oil collector in just 10 minutes",
            "Defined Suction Mode: Three optimized modes - Boiling (low), Cooking (medium), Frying (high) for efficient energy use",
            "Premium Box Styling: Elegant black glass box design adds a modern architectural element to your kitchen",
            "Whisper Quiet: Only 69 dB at maximum speed despite powerful 1200-1300 m³/h extraction capacity"
        ],
        "ai_features": {
            "smart_recommendations": "Perfect for standard kitchens up to 150 sq ft with 60cm cooktops, ideal for apartments and homes",
            "usage_tips": [
                "Use gesture control to avoid fingerprints on the glass surface",
                "Run Auto Clean function weekly for heavy cooking or monthly for regular use",
                "Select Boiling mode for gentle simmering and steaming",
                "Use Cooking mode for regular frying and sautéing",
                "Activate Frying mode for heavy frying, grilling, or intensive cooking",
                "Empty oil collector after each auto-clean cycle",
                "Powerful extraction ideal for Indian cooking with spices and frying",
                "Boost mode handles intensive cooking sessions",
                "Energy-efficient 3W LED provides excellent illumination",
                "Box design provides quieter operation than traditional chimneys"
            ],
            "compatibility": "Suitable for both electric and gas cooktops with 750mm minimum distance"
        },
        "documents": [
            {
                "name": "User Manual",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/wall-mounted-hoods/DWB68IJ60I",
                "description": "Complete user manual with installation and operation instructions"
            },
            {
                "name": "Installation Instructions",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/wall-mounted-hoods/DWB68IJ60I",
                "description": "Detailed installation guide for 60cm box wall-mounted hood"
            },
            {
                "name": "Product Specification Sheet",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/wall-mounted-hoods/DWB68IJ60I",
                "description": "Complete technical specifications"
            }
        ],
        "warranty": "2 years manufacturer warranty",
        "tags": ["chimney", "wall-mounted hood", "bosch", "series 4", "kitchen appliance", "black glass", "gesture control", "auto clean", "premium", "60cm", "touchless", "powerful", "box design"],
        "rating": 0.0,
        "reviews_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
        "discount_percentage": 0
    }
    
    try:
        result = await products_collection.insert_one(product)
        print(f"✅ Successfully added Bosch Box Wall-Mounted Hood DWB68IJ60I (60cm)")
        print(f"   Product ID: {product['id']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Price: ₹{product['price']:,.2f}")
        print(f"   Category: {product['category']} - {product['sub_category']}")
        print(f"   Style: Box Design")
        print(f"   Width: 60 cm")
        print(f"   Extraction Rate: 1200-1300 m³/h")
        print(f"   Special Features: Gesture Control, Auto Clean, Defined Suction Modes")
        print(f"   Images: {len(product['images'])} images added")
        
    except Exception as e:
        print(f"❌ Error adding product: {e}")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_box_wall_mounted_hood_60cm())
