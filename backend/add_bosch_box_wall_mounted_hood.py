import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_box_wall_mounted_hood():
    """Add Bosch Box Wall-Mounted Hood DWB98IJ60I to the database"""
    
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        print("❌ MONGO_URL not found in environment variables")
        return
    
    client = AsyncIOMotorClient(mongo_url)
    db = client.ecommerce_db
    products_collection = db.products
    
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch Series 4 Box Wall-Mounted Cooker Hood 90 cm",
        "model_number": "DWB98IJ60I",
        "brand": "Bosch",
        "category": "Chimney",
        "sub_category": "Wall-Mounted Chimney",
        "price": 33490.00,
        "original_price": 33490.00,
        "currency": "INR",
        "stock_quantity": 15,
        "description": "Bosch Series 4 Box Wall-Mounted Cooker Hood 90 cm with Gesture Control and powerful 1200-1300 m³/h extraction rate. Features elegant black glass box design with defined suction modes and filter saturation display.",
        "long_description": "The Bosch DWB98IJ60I Series 4 Box Wall-Mounted Cooker Hood combines premium box styling with innovative technology in a sleek 90 cm design. Featuring revolutionary Gesture Control for touchless operation and an impressive extraction rate of 1200-1300 m³/h, it efficiently removes cooking odors and steam during heavy cooking. The defined suction mode offers optimized fan speeds for different cooking methods - Boiling, Cooking, and Frying. The elegant black glass box body, filter saturation display for maintenance reminders, and energy-efficient LED lighting make it perfect for modern kitchens seeking both style and performance.",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/25909184_DWB98IJ60I_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25909185_DWB98IJ60I_PGA1_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25909181_DWB98IJ60I_PGA3_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25909186_DWB98IJ60I_PGA4_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25909183_DWB98IJ60I_PGA5_def.webp"
        ],
        "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/25909184_DWB98IJ60I_STP_def.webp",
        "features": [
            "Revolutionary Gesture Control - touchless operation",
            "Powerful 1200-1300 m³/h extraction rate",
            "Elegant black glass box design",
            "Defined Suction Mode - optimized for Boiling, Cooking, Frying",
            "Filter saturation display for maintenance reminders",
            "Boost mode for maximum extraction",
            "Energy-efficient LED lighting (3W) with cold white illumination",
            "Touch control panel",
            "90 cm width - ideal for wider cooktops",
            "Compact box design at 14.2 kg",
            "130 cm power cord for flexible installation"
        ],
        "specifications": {
            "Dimensions": {
                "Width": "90 cm (900 mm)",
                "Height": "470 mm",
                "Depth": "450 mm",
                "Net Weight": "14.2 kg"
            },
            "Performance": {
                "Operating Mode": "Air extraction only",
                "Extraction Rate": "1200-1300 m³/h (as per IS 374*)",
                "Motor Power": "180 W",
                "Speed Settings": "Multiple speeds with defined modes",
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
                "Defined Suction Mode": "Yes - Boiling, Cooking, Frying modes",
                "Filter Saturation Display": "Yes",
                "Boost Position": "Yes",
                "Touch Control": "Yes",
                "Remote Control": "No",
                "Home Connect": "No"
            }
        },
        "highlights": [
            "Powerful Box Design: 1200-1300 m³/h extraction rate in a compact box design efficiently handles heavy cooking",
            "Gesture Control: Wave your hand to turn on/off - no touching, no fingerprints on the elegant glass surface",
            "Defined Suction Mode: Three optimized modes - Boiling (low), Cooking (medium), Frying (high) for efficient energy use",
            "Smart Maintenance: Filter saturation display reminds you when to clean filters, ensuring optimal performance",
            "Premium Box Styling: Elegant black glass box design adds a modern architectural element to your kitchen",
            "Effective Source Suction: Powerful extraction captures cooking fumes, grease, and odors right at the source"
        ],
        "ai_features": {
            "smart_recommendations": "Perfect for modern kitchens up to 200 sq ft with 90cm cooktops, ideal for Indian cooking",
            "usage_tips": [
                "Use gesture control to avoid fingerprints on the glass surface",
                "Select Boiling mode for gentle simmering and steaming",
                "Use Cooking mode for regular frying and sautéing",
                "Activate Frying mode for heavy frying, grilling, or tandoor-style cooking",
                "Monitor filter saturation display and clean when indicated",
                "Powerful extraction ideal for Indian cooking with heavy spices",
                "Boost mode handles multiple burners operating simultaneously",
                "Energy-efficient 3W LED provides excellent illumination",
                "Box design provides quieter operation than traditional chimneys"
            ],
            "compatibility": "Suitable for both electric and gas cooktops with 750mm minimum distance"
        },
        "documents": [
            {
                "name": "User Manual",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/wall-mounted-hoods/DWB98IJ60I",
                "description": "Complete user manual with installation and operation instructions"
            },
            {
                "name": "Installation Instructions",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/wall-mounted-hoods/DWB98IJ60I",
                "description": "Detailed installation guide for 90cm box wall-mounted hood"
            },
            {
                "name": "Product Specification Sheet",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/wall-mounted-hoods/DWB98IJ60I",
                "description": "Complete technical specifications"
            }
        ],
        "warranty": "2 years manufacturer warranty",
        "tags": ["chimney", "wall-mounted hood", "bosch", "series 4", "kitchen appliance", "black glass", "gesture control", "premium", "90cm", "touchless", "powerful", "box design"],
        "rating": 3.0,
        "reviews_count": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
        "discount_percentage": 0
    }
    
    try:
        result = await products_collection.insert_one(product)
        print(f"✅ Successfully added Bosch Box Wall-Mounted Hood DWB98IJ60I")
        print(f"   Product ID: {product['id']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Price: ₹{product['price']:,.2f}")
        print(f"   Category: {product['category']} - {product['sub_category']}")
        print(f"   Style: Box Design")
        print(f"   Width: 90 cm")
        print(f"   Extraction Rate: 1200-1300 m³/h")
        print(f"   Special Features: Gesture Control, Defined Suction Modes, Filter Display")
        print(f"   Rating: {product['rating']}/5.0 ({product['reviews_count']} review)")
        print(f"   Images: {len(product['images'])} images added")
        
    except Exception as e:
        print(f"❌ Error adding product: {e}")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_box_wall_mounted_hood())
