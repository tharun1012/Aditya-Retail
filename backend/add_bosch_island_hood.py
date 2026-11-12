import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_island_hood():
    """Add Bosch Island Hood DIB098G50I to the database"""
    
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        print("❌ MONGO_URL not found in environment variables")
        return
    
    client = AsyncIOMotorClient(mongo_url)
    db = client.ecommerce_db
    products_collection = db.products
    
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch Series 4 Island Cooker Hood 90 cm",
        "model_number": "DIB098G50I",
        "brand": "Bosch",
        "category": "Chimney",
        "sub_category": "Island Chimney",
        "price": 66490.00,
        "original_price": 73990.00,
        "currency": "INR",
        "stock_quantity": 15,
        "description": "Bosch Series 4 Island Cooker Hood with powerful 705 m³/h air extraction capacity in boost mode. Features elegant stainless steel design perfect for modern island kitchens with ducted or non-ducted installation options.",
        "long_description": "The Bosch DIB098G50I Series 4 Island Cooker Hood combines powerful performance with elegant design. With a maximum air extraction capacity of 705 m³/h in boost mode, this 90 cm wide hood efficiently removes cooking odors and steam. The premium stainless steel construction ensures durability and easy maintenance with washable grease filters. Features 3-stage speed settings plus an intensive mode for heavy cooking, energy-efficient LED lighting, and delay shut-off function for convenience.",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/MCSA01858394_DIB098G50I_ChimneyHood_Bosch_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/MCSA01858395_DIB098G50I_ChimneyHood_Bosch_PGA1_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/MCSA01858396_DIB098G50I_ChimneyHood_Bosch_PGA2_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/MCSA01858397_DIB098G50I_ChimneyHood_Bosch_PGA3_def.webp"
        ],
        "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/MCSA01858394_DIB098G50I_ChimneyHood_Bosch_STP_def.webp",
        "features": [
            "Powerful 705 m³/h air extraction in boost mode",
            "3-stage speed settings + intensive setting",
            "Premium stainless steel body and finish",
            "Washable stainless steel grease filters",
            "Energy-efficient LED lighting (4W)",
            "Ducted or recirculation installation options",
            "Delay shut-off function",
            "Suitable for both electric and gas hobs",
            "90 cm wide - perfect for island kitchens",
            "Annual energy consumption: 114.4 kWh"
        ],
        "specifications": {
            "Dimensions": {
                "Width": "900 mm",
                "Height": "340 mm",
                "Depth": "610 mm",
                "Net Weight": "26.8 kg"
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
                "Color Temperature": "4000 K"
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
                "Home Connect": "No"
            }
        },
        "highlights": [
            "Island Installation: Designed specifically for island kitchens, creating a stunning centerpiece",
            "Powerful Extraction: 705 m³/h boost capacity efficiently removes cooking odors and grease",
            "Flexible Installation: Convertible design works with ducted or recirculation setup",
            "Easy Maintenance: Washable stainless steel grease filters for hassle-free cleaning",
            "Energy Efficient: LED lighting and optimized motor consume only 114.4 kWh annually",
            "Premium Build: Stainless steel construction ensures durability and elegant appearance"
        ],
        "ai_features": {
            "smart_recommendations": "Ideal for modern island kitchens up to 250 sq ft",
            "usage_tips": [
                "Use boost mode for heavy frying or grilling",
                "Clean grease filters monthly for optimal performance",
                "Regular speed sufficient for everyday cooking",
                "Ensure proper ducting for maximum efficiency",
                "LED lighting provides excellent task illumination"
            ],
            "compatibility": "Suitable for both electric and gas cooktops with 750mm minimum distance"
        },
        "documents": [
            {
                "name": "User Manual",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/island-hoods/DIB098G50I",
                "description": "Complete user manual with installation and operation instructions"
            },
            {
                "name": "Installation Instructions",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/island-hoods/DIB098G50I",
                "description": "Detailed installation guide for island hood setup"
            },
            {
                "name": "Product Specification Sheet",
                "type": "PDF",
                "url": "https://www.bosch-home.in/en/product/cooking-baking/built-in-hoods/island-hoods/DIB098G50I",
                "description": "Complete technical specifications"
            }
        ],
        "warranty": "2 years manufacturer warranty",
        "tags": ["chimney", "island hood", "bosch", "series 4", "kitchen appliance", "stainless steel", "premium", "90cm"],
        "rating": 0.0,
        "reviews_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
        "discount_percentage": 10
    }
    
    try:
        result = await products_collection.insert_one(product)
        print(f"✅ Successfully added Bosch Island Hood DIB098G50I")
        print(f"   Product ID: {product['id']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Price: ₹{product['price']:,.2f} (was ₹{product['original_price']:,.2f})")
        print(f"   Category: {product['category']} - {product['sub_category']}")
        print(f"   Images: {len(product['images'])} images added")
        
    except Exception as e:
        print(f"❌ Error adding product: {e}")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_island_hood())
