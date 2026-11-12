import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_island_hood_120cm():
    """Add Bosch Island Hood DIB128G50I (120cm) to the database"""
    
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        print("❌ MONGO_URL not found in environment variables")
        return
    
    client = AsyncIOMotorClient(mongo_url)
    db = client.ecommerce_db
    products_collection = db.products
    
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch Series 4 Island Cooker Hood 120 cm",
        "model_number": "DIB128G50I",
        "brand": "Bosch",
        "category": "Chimney",
        "sub_category": "Island Chimney",
        "price": 73490.00,
        "original_price": 81490.00,
        "currency": "INR",
        "stock_quantity": 12,
        "description": "Bosch Series 4 Island Cooker Hood with powerful 705 m³/h air extraction capacity in boost mode. Features elegant stainless steel design perfect for larger island kitchens at 120 cm width with ducted or non-ducted installation options.",
        "long_description": "The Bosch DIB128G50I Series 4 Island Cooker Hood is designed for spacious kitchens with its impressive 120 cm width. With a maximum air extraction capacity of 705 m³/h in boost mode, this hood efficiently removes cooking odors and steam even in larger cooking areas. The premium stainless steel construction ensures durability and easy maintenance with washable grease filters. Features 3-stage speed settings plus an intensive mode for heavy cooking, energy-efficient LED lighting with 4000K cold white illumination, and delay shut-off function for added convenience.",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/MCSA01859865_DIB128G50I_ChimneyHood_Bosch_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/MCSA01858395_DIB098G50I_ChimneyHood_Bosch_PGA1_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/MCSA01859866_DIB128G50I_ChimneyHood_Bosch_PGA2_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/MCSA01859867_DIB128G50I_ChimneyHood_Bosch_PGA3_def.webp"
        ],
        "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/MCSA01859865_DIB128G50I_ChimneyHood_Bosch_STP_def.webp",
        "features": [
            "Powerful 705 m³/h air extraction in boost mode",
            "3-stage speed settings + intensive setting",
            "Premium stainless steel body and finish",
            "Washable stainless steel grease filters",
            "Energy-efficient LED lighting (4W)",
            "Ducted or recirculation installation options",
            "Delay shut-off function",
            "Suitable for both electric and gas hobs",
            "120 cm wide - ideal for larger island kitchens",
            "Annual energy consumption: 114.4 kWh",
            "Cold white LED illumination (4000K)"
        ],
        "specifications": {
            "Dimensions": {
                "Width": "120 cm (1200 mm)",
                "Height": "340 mm",
                "Depth": "610 mm",
                "Net Weight": "29.4 kg"
            },
            "Performance": {
                "Air Extraction Capacity (Boost)": "705 m³/h",
                "Max Recirculation": "545 m³/h",
                "Boost Recirculation": "575 m³/h",
                "Motor Power": "350 W",
                "Annual Energy Consumption": "114.4 kWh"
            },
            "Noise Level": {
                "Max Speed Recirculation": "76 dB",
                "Boost Recirculation": "77 dB"
            },
            "Lighting": {
                "Type": "LED",
                "Power": "4 W",
                "Color Temperature": "4000 K (Cold White)"
            },
            "Installation": {
                "Installation Type": "Island",
                "Operating Mode": "Convertible (Ducted/Recirculation)",
                "Distance to Electric Hob": "750 mm",
                "Distance to Gas Hob": "750 mm",
                "Air Outlet Diameter": "120 / 150 mm"
            },
            "Design": {
                "Color": "Stainless Steel",
                "Material": "Stainless steel",
                "Filter Type": "Washable stainless steel grease filter"
            },
            "Control Features": {
                "Speed Settings": "3-stages + intensive setting",
                "Boost Position": "Yes",
                "Delay Shut-off": "Yes",
                "Remote Control": "No",
                "Home Connect": "No",
                "PerfectAir Sensor": "No",
                "EcoSilence Drive": "No"
            }
        },
        "highlights": [
            "Extra-Wide Coverage: 120 cm width provides excellent coverage for larger cooktops",
            "Island Centerpiece: Designed to be a stunning focal point in spacious island kitchens",
            "Powerful Extraction: 705 m³/h boost capacity efficiently removes cooking odors and grease",
            "Flexible Installation: Convertible design works with ducted or recirculation setup",
            "Easy Maintenance: Washable stainless steel grease filters for hassle-free cleaning",
            "Energy Efficient: LED lighting and optimized motor consume only 114.4 kWh annually",
            "Premium Build: Heavy-duty stainless steel construction (29.4 kg) ensures stability"
        ],
        "ai_features": {
            "smart_recommendations": "Perfect for large island kitchens up to 300 sq ft with wide cooktops",
            "usage_tips": [
                "Use boost mode for heavy frying or grilling across multiple burners",
                "Clean grease filters monthly for optimal performance",
                "Regular speed sufficient for everyday cooking",
                "Ensure proper ducting for maximum efficiency",
                "LED lighting provides excellent task illumination across wide cooking area",
                "Ideal for professional-grade cooking setups"
            ],
            "compatibility": "Suitable for both electric and gas cooktops with 750mm minimum distance"
        },
        "documents": [
            {
                "name": "User Manual",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/island-hoods/DIB128G50I",
                "description": "Complete user manual with installation and operation instructions"
            },
            {
                "name": "Installation Instructions",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/island-hoods/DIB128G50I",
                "description": "Detailed installation guide for 120cm island hood setup"
            },
            {
                "name": "Product Specification Sheet",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/island-hoods/DIB128G50I",
                "description": "Complete technical specifications"
            }
        ],
        "warranty": "2 years manufacturer warranty",
        "tags": ["chimney", "island hood", "bosch", "series 4", "kitchen appliance", "stainless steel", "premium", "120cm", "wide", "large kitchen"],
        "rating": 0.0,
        "reviews_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
        "discount_percentage": 10
    }
    
    try:
        result = await products_collection.insert_one(product)
        print(f"✅ Successfully added Bosch Island Hood DIB128G50I (120cm)")
        print(f"   Product ID: {product['id']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Price: ₹{product['price']:,.2f} (was ₹{product['original_price']:,.2f})")
        print(f"   Category: {product['category']} - {product['sub_category']}")
        print(f"   Width: 120 cm")
        print(f"   Images: {len(product['images'])} images added")
        
    except Exception as e:
        print(f"❌ Error adding product: {e}")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_island_hood_120cm())
