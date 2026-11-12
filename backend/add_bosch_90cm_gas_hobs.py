import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_90cm_gas_hobs():
    """Add 4 Bosch 90cm Gas Hobs to the database"""
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    if not mongo_url:
        print("❌ MONGO_URL not found in environment variables")
        return
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    products_collection = db.products
    
    products = [
        # Product 1: PNF9B6F20I - Series 6, 4 Burner
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Gas Hob 90 cm - Tempered Glass Black",
            "model_number": "PNF9B6F20I",
            "brand": "Bosch",
            "category": "Gas Hob",
            "sub_category": "Built-in Gas Hob 90cm",
            "price": 51990.00,
            "original_price": 57990.00,
            "currency": "INR",
            "stock_quantity": 10,
            "description": "Bosch Series 6 Gas Hob 90 cm with 4 burners, premium 6mm tempered glass in black. Features cast iron supports, low profile design for spacious cooking.",
            "long_description": "The Bosch PNF9B6F20I Series 6 Gas Hob offers premium 90 cm cooking space with elegant 6mm tempered glass surface. Featuring 4 powerful burners with cast iron single pan supports, this hob provides ample space for large families. The low profile stainless steel cooking surface is easily accessible and quick to clean. Made in Europe with Series 6 quality, perfect for spacious kitchens requiring maximum cooking area.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/19898032_PNF9B6F20I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790769_PNF9B6F20I_PGA5_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790772_PNF9B6F20I_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20807825_PNF9B6F20I_PGA3_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/19898032_PNF9B6F20I_STP_def.webp",
            "features": [
                "4 powerful gas burners",
                "Premium 6mm tempered glass",
                "90 cm wide cooking area",
                "Cast iron single pan supports",
                "Low profile design",
                "Series 6 quality",
                "Made in Europe",
                "Suitable for LPG and natural gas",
                "Easy to clean surface"
            ],
            "specifications": {
                "Dimensions": {"Width": "90 cm", "Cooktop Type": "Gas cooktop"},
                "Burners": {"Total Burners": "4", "Pan Support Material": "Cast iron single"},
                "Design": {"Surface Material": "Tempered glass - 6mm", "Color": "Black"},
                "Gas": {"Gas Type": "LPG G30,31", "Pressure": "28-30/37 mbar", "Alternative Gas": "Natural gas H/E/(L) 20 (25) mbar included"},
                "Installation": {"Type": "Built-in", "Style": "Standard 90cm"},
                "Special Features": {"Low Profile Design": "Yes"}
            },
            "highlights": [
                "Spacious 90cm Width: Maximum cooking space for large families",
                "4 Burner Configuration: Versatile cooking with multiple dishes",
                "Premium Series 6: Higher-tier quality with refined features",
                "6mm Tempered Glass: Safety and durability with elegant black finish",
                "Made in Europe: Premium Bosch craftsmanship"
            ],
            "ai_features": {
                "smart_recommendations": "Perfect for large families with spacious kitchens. Ideal for 6-8 people.",
                "usage_tips": [
                    "90cm width provides maximum cooking flexibility",
                    "Four burners handle complete meal preparation",
                    "Cast iron supports for heavy cookware",
                    "Works with both LPG and natural gas"
                ],
                "compatibility": "Requires LPG or natural gas connection. 90cm cutout required."
            },
            "documents": [{"name": "User Manual", "type": "PDF", "url": "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/gas-hobs-90-cm/PNF9B6F20I", "description": "Complete user manual"}],
            "warranty": "2 years manufacturer warranty",
            "tags": ["gas hob", "90cm", "bosch", "series 6", "tempered glass", "black", "4 burner", "made in europe"],
            "rating": 0.0,
            "reviews_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "discount_percentage": 10
        },
        # Product 2: PNF9B6G20I - Series 6, 4 Burner
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Gas Hob 90 cm - Premium Tempered Glass Black",
            "model_number": "PNF9B6G20I",
            "brand": "Bosch",
            "category": "Gas Hob",
            "sub_category": "Built-in Gas Hob 90cm",
            "price": 56490.00,
            "original_price": 62490.00,
            "currency": "INR",
            "stock_quantity": 8,
            "description": "Bosch Series 6 Gas Hob 90 cm with 4 burners, premium 6mm tempered glass. Features elegant design with cast iron supports.",
            "long_description": "The Bosch PNF9B6G20I Series 6 Gas Hob represents premium 90 cm cooking with elegant 6mm tempered glass. Four powerful burners with cast iron supports provide versatile cooking in a stylish package. Made in Europe with Series 6 excellence.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/19898031_PNF9B6G20I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790658_PNF9B6G20I_PGA5_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790668_PNF9B6G20I_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20807797_PNF9B6G20I_PGA3_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/19898031_PNF9B6G20I_STP_def.webp",
            "features": ["4 powerful gas burners", "Premium 6mm tempered glass", "90 cm wide", "Cast iron supports", "Low profile design", "Series 6 quality", "Made in Europe"],
            "specifications": {
                "Dimensions": {"Width": "90 cm", "Cooktop Type": "Gas cooktop"},
                "Burners": {"Total Burners": "4", "Pan Support Material": "Cast iron single"},
                "Design": {"Surface Material": "Tempered glass - 6mm", "Color": "Black"},
                "Gas": {"Gas Type": "LPG G30,31", "Pressure": "28-30/37 mbar"},
                "Installation": {"Type": "Built-in", "Style": "Standard 90cm"}
            },
            "highlights": ["90cm Premium Space", "Series 6 Excellence", "4 Burner Versatility", "Made in Europe"],
            "ai_features": {"smart_recommendations": "Ideal for premium large kitchens.", "usage_tips": ["90cm width for large families", "Four burners for multi-dish cooking"], "compatibility": "Requires LPG or natural gas. 90cm cutout."},
            "documents": [{"name": "User Manual", "type": "PDF", "url": "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/gas-hobs-90-cm/PNF9B6G20I"}],
            "warranty": "2 years manufacturer warranty",
            "tags": ["gas hob", "90cm", "bosch", "series 6", "tempered glass", "4 burner", "premium"],
            "rating": 0.0,
            "reviews_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "discount_percentage": 10
        },
        # Product 3: PNV9B6F20I - Series 6, 5 Burner
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Gas Hob 90 cm - 5 Burner Tempered Glass Black",
            "model_number": "PNV9B6F20I",
            "brand": "Bosch",
            "category": "Gas Hob",
            "sub_category": "Built-in Gas Hob 90cm",
            "price": 58990.00,
            "original_price": 65490.00,
            "currency": "INR",
            "stock_quantity": 12,
            "description": "Bosch Series 6 Gas Hob 90 cm with 5 burners, premium 6mm tempered glass in black. Maximum cooking versatility with full BTU range.",
            "long_description": "The Bosch PNV9B6F20I Series 6 Gas Hob offers maximum cooking versatility with 5 powerful burners in 90 cm width. Premium 6mm tempered glass surface with cast iron supports. Full BTU range performance for all cooking styles. Made in Europe with Series 6 quality - perfect for serious cooking enthusiasts.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/19898041_PNV9B6F20I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20630472_PNV9B6F20I_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20791004_PNV9B6F20I_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20791087_PNV9B6F20I_PGA5_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/19898041_PNV9B6F20I_STP_def.webp",
            "features": ["5 powerful gas burners", "Premium 6mm tempered glass", "90 cm wide", "Full BTU range", "Cast iron supports", "Low profile design", "Series 6 quality", "Made in Europe"],
            "specifications": {
                "Dimensions": {"Width": "90 cm", "Cooktop Type": "Gas cooktop"},
                "Burners": {"Total Burners": "5", "Pan Support Material": "Cast iron single"},
                "Design": {"Surface Material": "Tempered glass - 6mm", "Color": "Black"},
                "Gas": {"Gas Type": "LPG G30,31", "Pressure": "28-30/37 mbar"},
                "Installation": {"Type": "Built-in", "Style": "Standard 90cm"},
                "Special Features": {"Full BTU Range": "Yes"}
            },
            "highlights": ["5 Burner Configuration: Maximum versatility for serious cooks", "90cm Space with 5 Burners", "Full BTU Range Performance", "Premium Series 6 Quality", "Made in Europe"],
            "ai_features": {"smart_recommendations": "Perfect for large families who love cooking. Ideal for 6-10 people.", "usage_tips": ["Five burners for complete meal preparation", "90cm width accommodates all cookware", "Full BTU range handles all cooking styles"], "compatibility": "Requires LPG or natural gas. 90cm cutout."},
            "documents": [{"name": "User Manual", "type": "PDF", "url": "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/gas-hobs-90-cm/PNV9B6F20I"}],
            "warranty": "2 years manufacturer warranty",
            "tags": ["gas hob", "90cm", "bosch", "series 6", "tempered glass", "5 burner", "premium", "made in europe"],
            "rating": 0.0,
            "reviews_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "discount_percentage": 10
        },
        # Product 4: PNV9B6G20I - Series 6, 5 Burner Premium
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Gas Hob 90 cm - Premium 5 Burner Tempered Glass Black",
            "model_number": "PNV9B6G20I",
            "brand": "Bosch",
            "category": "Gas Hob",
            "sub_category": "Built-in Gas Hob 90cm",
            "price": 64490.00,
            "original_price": 71490.00,
            "currency": "INR",
            "stock_quantity": 10,
            "description": "Bosch Series 6 Gas Hob 90 cm with 5 burners, premium 6mm tempered glass. Top-tier 90cm model with maximum cooking power.",
            "long_description": "The Bosch PNV9B6G20I Series 6 Gas Hob represents the pinnacle of 90 cm gas cooking. Five powerful burners with premium 6mm tempered glass and cast iron supports. Full BTU range with elegant design. Made in Europe - the ultimate choice for serious home chefs.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/19898040_PNV9B6G20I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20630404_PNV9B6G20I_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790869_PNV9B6G20I_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790878_PNV9B6G20I_PGA5_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/19898040_PNV9B6G20I_STP_def.webp",
            "features": ["5 powerful gas burners", "Premium 6mm tempered glass", "90 cm wide", "Full BTU range", "Cast iron supports", "Series 6 premium quality", "Made in Europe"],
            "specifications": {
                "Dimensions": {"Width": "90 cm", "Cooktop Type": "Gas cooktop"},
                "Burners": {"Total Burners": "5", "Pan Support Material": "Cast iron single"},
                "Design": {"Surface Material": "Tempered glass - 6mm", "Color": "Black"},
                "Gas": {"Gas Type": "LPG G30,31", "Pressure": "28-30/37 mbar"},
                "Installation": {"Type": "Built-in", "Style": "Standard 90cm"},
                "Special Features": {"Full BTU Range": "Yes"}
            },
            "highlights": ["Premium 5 Burner: Top-tier 90cm model", "Series 6 Excellence", "Professional Cooking Capability", "Made in Europe"],
            "ai_features": {"smart_recommendations": "Ultimate choice for serious home chefs and large families.", "usage_tips": ["Five burners for professional-level cooking", "Maximum versatility for all cooking styles"], "compatibility": "Requires LPG or natural gas. 90cm cutout."},
            "documents": [{"name": "User Manual", "type": "PDF", "url": "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/gas-hobs-90-cm/PNV9B6G20I"}],
            "warranty": "2 years manufacturer warranty",
            "tags": ["gas hob", "90cm", "bosch", "series 6", "tempered glass", "5 burner", "premium", "professional"],
            "rating": 0.0,
            "reviews_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "discount_percentage": 10
        }
    ]
    
    try:
        for product in products:
            result = await products_collection.insert_one(product)
            print(f"✅ Successfully added {product['name']}")
            print(f"   Model: {product['model_number']}")
            print(f"   Burners: {product['specifications']['Burners']['Total Burners']}")
            print(f"   Price: ₹{product['price']:,.2f} (Save {product['discount_percentage']}%)")
            print(f"   Stock: {product['stock_quantity']} units")
            print()
        
    except Exception as e:
        print(f"❌ Error adding products: {e}")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_90cm_gas_hobs())
