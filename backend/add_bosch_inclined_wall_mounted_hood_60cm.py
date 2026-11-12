import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_inclined_wall_mounted_hood_60cm():
    """Add Bosch Inclined Wall-Mounted Hood DWK68IJ60I (60cm) to the database"""
    
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        print("❌ MONGO_URL not found in environment variables")
        return
    
    client = AsyncIOMotorClient(mongo_url)
    db = client.ecommerce_db
    products_collection = db.products
    
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch Series 4 Inclined Wall-Mounted Cooker Hood 60 cm",
        "model_number": "DWK68IJ60I",
        "brand": "Bosch",
        "category": "Chimney",
        "sub_category": "Wall-Mounted Chimney",
        "price": 35990.00,
        "original_price": 35990.00,
        "currency": "INR",
        "stock_quantity": 14,
        "description": "Bosch Series 4 Inclined Wall-Mounted Cooker Hood 60 cm with Gesture Control and Auto Clean Technology. Features sleek inclined black glass design with 680 m³/h extraction capacity for modern kitchens.",
        "long_description": "The Bosch DWK68IJ60I Series 4 Inclined Wall-Mounted Cooker Hood represents the perfect fusion of contemporary design and advanced technology. The striking inclined black glass design not only looks stunning but also provides better head clearance while cooking. Featuring revolutionary Gesture Control for touchless operation and Auto Clean Technology that uses heat to melt grease automatically, this hood makes maintenance effortless. With a powerful 680 m³/h extraction capacity and quiet 69 dB operation, it efficiently removes cooking odors and steam. The defined suction mode offers optimized fan speeds for different cooking methods, while the energy-efficient LED lighting illuminates your cooking area beautifully.",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/26060196_DWK68IJ60I_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/26060190_DWK68IJ60I_PGA1_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/26060187_DWK68IJ60I_PGA3_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/26060189_DWK68IJ60I_PGA4_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/26060192_DWK68IJ60I_PGA5_def.webp"
        ],
        "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/26060196_DWK68IJ60I_STP_def.webp",
        "features": [
            "Revolutionary Gesture Control - touchless operation",
            "Auto Clean Technology with heat-based self-cleaning",
            "Sleek inclined black glass design",
            "Powerful 680 m³/h air extraction capacity",
            "Defined Suction Mode for different cooking styles",
            "3-stage speed settings",
            "Quiet operation at 69 dB max speed",
            "Energy-efficient LED lighting (3W) with cold white illumination",
            "Touch control panel",
            "Delay shut-off function",
            "60 cm width - ideal for standard cooktops",
            "Improved head clearance with inclined design",
            "130 cm power cord for flexible installation"
        ],
        "specifications": {
            "Dimensions": {
                "Width": "60 cm (595 mm)",
                "Height": "810 mm",
                "Depth": "340 mm",
                "Chimney Height": "350 mm",
                "Net Weight": "14.6 kg"
            },
            "Performance": {
                "Operating Mode": "Air extraction only",
                "Max Air Extraction Capacity": "680 m³/h",
                "Motor Power": "180 W",
                "Speed Settings": "3-stage",
                "Sound Power at Max Speed": "69 dB",
                "Defined Suction Modes": "Boiling, Cooking, Frying"
            },
            "Installation": {
                "Installation Type": "Wall-mounted (Inclined style)",
                "Distance to Electric Hob": "650 mm",
                "Distance to Gas Hob": "500 mm",
                "Power Cord Length": "130 cm",
                "No-return Airflow Flap": "No"
            },
            "Design": {
                "Color": "Black",
                "Material": "Premium Glass",
                "Series": "Series 4",
                "Style": "Inclined Design"
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
                "Delay Shut-off": "Yes",
                "Touch Control": "Yes",
                "Boost Position": "No",
                "Remote Control": "No",
                "Home Connect": "No"
            }
        },
        "highlights": [
            "Modern Inclined Design: Sleek angled black glass design provides better head clearance and stunning aesthetics",
            "Dual Smart Control: Gesture Control for touchless operation and Touch Control for precise settings",
            "Auto Clean Technology: Self-cleaning function uses heat to melt grease, collecting it in an easy-to-clean oil collector in just 10 minutes",
            "Effective Extraction: 680 m³/h capacity efficiently removes cooking odors, smoke, and grease from source",
            "Defined Suction Mode: Three optimized modes - Boiling (low), Cooking (medium), Frying (high) for efficient energy use",
            "Whisper Quiet: Only 69 dB at maximum speed ensures peaceful cooking experience"
        ],
        "ai_features": {
            "smart_recommendations": "Perfect for modern kitchens up to 150 sq ft with 60cm cooktops, ideal for contemporary home designs",
            "usage_tips": [
                "Use gesture control to avoid fingerprints on the inclined glass surface",
                "Run Auto Clean function weekly for heavy cooking or monthly for regular use",
                "Inclined design provides better visibility and head clearance while cooking",
                "Select Boiling mode for gentle simmering and steaming",
                "Use Cooking mode for regular frying and sautéing",
                "Activate Frying mode for heavy frying or intensive cooking",
                "Empty oil collector after each auto-clean cycle",
                "Lower installation height (500mm for gas) thanks to inclined design",
                "Energy-efficient 3W LED provides excellent focused illumination",
                "Inclined surface is easier to clean than traditional vertical designs"
            ],
            "compatibility": "Suitable for both electric and gas cooktops with minimum distances: 650mm (electric) and 500mm (gas)"
        },
        "documents": [
            {
                "name": "User Manual",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/wall-mounted-hoods/DWK68IJ60I",
                "description": "Complete user manual with installation and operation instructions"
            },
            {
                "name": "Installation Instructions",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/wall-mounted-hoods/DWK68IJ60I",
                "description": "Detailed installation guide for 60cm inclined wall-mounted hood"
            },
            {
                "name": "Product Specification Sheet",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/wall-mounted-hoods/DWK68IJ60I",
                "description": "Complete technical specifications"
            }
        ],
        "warranty": "2 years manufacturer warranty",
        "tags": ["chimney", "wall-mounted hood", "bosch", "series 4", "kitchen appliance", "black glass", "gesture control", "auto clean", "premium", "60cm", "touchless", "inclined design", "modern"],
        "rating": 0.0,
        "reviews_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
        "discount_percentage": 0
    }
    
    try:
        result = await products_collection.insert_one(product)
        print(f"✅ Successfully added Bosch Inclined Wall-Mounted Hood DWK68IJ60I (60cm)")
        print(f"   Product ID: {product['id']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Price: ₹{product['price']:,.2f}")
        print(f"   Category: {product['category']} - {product['sub_category']}")
        print(f"   Style: Inclined Design")
        print(f"   Width: 60 cm")
        print(f"   Extraction Capacity: 680 m³/h")
        print(f"   Special Features: Gesture Control, Auto Clean, Inclined Design")
        print(f"   Images: {len(product['images'])} images added")
        
    except Exception as e:
        print(f"❌ Error adding product: {e}")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_inclined_wall_mounted_hood_60cm())
