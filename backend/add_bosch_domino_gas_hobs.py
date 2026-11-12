import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_domino_gas_hobs():
    """Add 2 Bosch Domino Gas Hobs to the database"""
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    if not mongo_url:
        print("❌ MONGO_URL not found in environment variables")
        return
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    products_collection = db.products
    
    products = [
        # Product 1: PRA3A6D70I - 1 Burner
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 8 Domino Gas Hob 30 cm - 1 Burner",
            "model_number": "PRA3A6D70I",
            "brand": "Bosch",
            "category": "Gas Hob",
            "sub_category": "Domino Gas Hob",
            "price": 57990.00,
            "original_price": 64490.00,
            "currency": "INR",
            "stock_quantity": 8,
            "description": "Bosch Series 8 Domino Gas Hob 30 cm with 1 powerful burner, ceramic black surface, and elegant design frame. Perfect for compact kitchens or modular cooktop configurations.",
            "long_description": "The Bosch PRA3A6D70I Series 8 Domino Gas Hob combines premium design with efficient cooking in just 30 cm width. Featuring a single powerful burner with ceramic black surface and design frame, this hob is perfect for space-saving kitchens or creating modular cooktop combinations. Made in Europe with Bosch quality, it includes residual heat indicator for safety and ergonomic knob control for precise flame adjustment. The ceramic surface ensures easy cleaning and durability.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01656668_PRA3A6D70_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01758908_PRA3A6D70_GasHob_build-in_Bosch_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01775569_PRP6A6D70_GasHob_build-in_Bosch_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01835216_PRA3A6D70_GasHob_build-in_Bosch_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01754075_PRA3A6D70_GasHob_build-in_Bosch_PGA5_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/MCSA01656668_PRA3A6D70_def.webp",
            "features": [
                "Single powerful burner",
                "Premium ceramic black surface",
                "Elegant design frame",
                "Compact 30 cm width",
                "Residual heat indicator",
                "Knob control",
                "Made in Europe",
                "Easy to clean ceramic surface",
                "Suitable for LPG (G30,31 28-30/37 mbar)",
                "Perfect for modular cooktop combinations"
            ],
            "specifications": {
                "Dimensions": {
                    "Width": "30.6 cm",
                    "Height": "5.9 cm",
                    "Depth": "52.7 cm"
                },
                "Burners": {
                    "Total Burners": "1",
                    "Burner Type": "Gas burner"
                },
                "Design": {
                    "Surface Material": "Ceramic",
                    "Color": "Black",
                    "Frame Type": "Design frame",
                    "Control Type": "Knob"
                },
                "Safety": {
                    "Residual Heat Indicator": "Yes - Separate"
                },
                "Gas": {
                    "Gas Type": "LPG G30,31",
                    "Pressure": "28-30/37 mbar"
                },
                "Installation": {
                    "Type": "Built-in",
                    "Style": "Domino"
                }
            },
            "highlights": [
                "Compact Domino Design: Perfect 30 cm width saves space and allows modular combinations",
                "Premium Series 8: Top-tier quality with elegant ceramic black surface",
                "Easy Maintenance: Ceramic surface wipes clean effortlessly",
                "Made in Europe: Premium Bosch quality and craftsmanship",
                "Residual Heat Indicator: Safety feature shows when surface is still hot",
                "Modular Flexibility: Combine with other Domino units for custom cooktop"
            ],
            "ai_features": {
                "smart_recommendations": "Perfect for compact kitchens, studio apartments, or as part of a modular cooktop setup. Ideal for single-person cooking or supplementary burner.",
                "usage_tips": [
                    "Ideal for single-pot cooking or simmering",
                    "Combine with other Domino units (gas or induction) for versatile cooking",
                    "Perfect as a wok station or for tea/coffee preparation",
                    "Ceramic surface requires gentle cleaning - avoid abrasives",
                    "Residual heat indicator prevents burns",
                    "Works with standard LPG gas connections",
                    "Space-saving design perfect for small kitchens"
                ],
                "compatibility": "Requires LPG gas connection. Can be installed alongside other Domino hobs for modular configuration."
            },
            "documents": [
                {
                    "name": "User Manual",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/domino-gas-hobs/PRA3A6D70I",
                    "description": "Complete user manual with installation and operation instructions"
                },
                {
                    "name": "Installation Instructions",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/domino-gas-hobs/PRA3A6D70I",
                    "description": "Detailed installation guide"
                },
                {
                    "name": "Product Specification Sheet",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/domino-gas-hobs/PRA3A6D70I",
                    "description": "Complete technical specifications"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "tags": ["gas hob", "domino", "bosch", "series 8", "kitchen appliance", "compact", "1 burner", "ceramic", "30cm", "made in europe"],
            "rating": 0.0,
            "reviews_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "discount_percentage": 10
        },
        
        # Product 2: PRB3A6D70I - 2 Burner with FlameSelect
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 8 Domino Gas Hob 30 cm - 2 Burner",
            "model_number": "PRB3A6D70I",
            "brand": "Bosch",
            "category": "Gas Hob",
            "sub_category": "Domino Gas Hob",
            "price": 50990.00,
            "original_price": 56490.00,
            "currency": "INR",
            "stock_quantity": 10,
            "description": "Bosch Series 8 Domino Gas Hob 30 cm with 2 burners, FlameSelect technology with 9 precise flame levels, ceramic black surface, and sword knobs for ergonomic control.",
            "long_description": "The Bosch PRB3A6D70I Series 8 Domino Gas Hob represents the pinnacle of compact gas cooking technology. Featuring 2 burners with revolutionary FlameSelect technology that offers 9 precisely defined flame levels, this hob provides ultra-precise flame control for perfect cooking results. The ergonomic sword knobs offer comfortable operation while the premium ceramic black surface with design frame ensures elegant aesthetics. Made in Europe with Bosch quality, it includes residual heat indicator for safety. Perfect for compact spaces or modular cooktop configurations.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01656673_PRB3A6D70_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01758915_PRB3A6D70_GasHob_build-in_Bosch_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01775567_PRB3A6D70_GasHob_build-in_Bosch_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01835218_PRB3A6D70_GasHob_build-in_Bosch_PGA3_i2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01754077_PRB3A6D70_GasHob_build-in_Bosch_PGA5_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/MCSA01656673_PRB3A6D70_def.webp",
            "features": [
                "2 powerful burners",
                "FlameSelect technology - 9 precise flame levels",
                "Ergonomic sword knobs",
                "Premium ceramic black surface",
                "Elegant design frame",
                "Compact 30 cm width",
                "Residual heat indicator",
                "Ultra-precise flame control",
                "Made in Europe",
                "Easy to clean ceramic surface",
                "Suitable for LPG (G30,31 28-30/37 mbar)",
                "Perfect for modular cooktop combinations"
            ],
            "specifications": {
                "Dimensions": {
                    "Width": "30.6 cm",
                    "Height": "4.7 cm",
                    "Depth": "52.7 cm"
                },
                "Burners": {
                    "Total Burners": "2",
                    "Burner Type": "Gas burner",
                    "FlameSelect Levels": "9 precise levels"
                },
                "Design": {
                    "Surface Material": "Ceramic",
                    "Color": "Black",
                    "Frame Type": "Design frame",
                    "Control Type": "Sword knobs"
                },
                "Safety": {
                    "Residual Heat Indicator": "Yes - Separate"
                },
                "Gas": {
                    "Gas Type": "LPG G30,31",
                    "Pressure": "28-30/37 mbar"
                },
                "Installation": {
                    "Type": "Built-in",
                    "Style": "Domino"
                },
                "Smart Features": {
                    "FlameSelect": "Yes - 9 defined flame levels"
                }
            },
            "highlights": [
                "FlameSelect Technology: Adjust gas flame precisely using 9 defined levels - perfect control for delicate simmering or high-heat cooking",
                "Sword Knobs: Ergonomic design for comfortable, precise control at your fingertips",
                "Compact 30cm Design: Two burners in minimal space - perfect for small kitchens or modular setups",
                "Premium Series 8: Top-tier quality with elegant ceramic black surface",
                "Made in Europe: Premium Bosch quality and craftsmanship",
                "Ultra-Precise Control: FlameSelect eliminates guesswork - select exact flame level needed"
            ],
            "ai_features": {
                "smart_recommendations": "Perfect for compact kitchens, apartments, or as part of modular cooktop. Ideal for 1-2 person households or as secondary cooking station.",
                "usage_tips": [
                    "Use FlameSelect level 1-3 for gentle simmering and melting",
                    "Levels 4-6 perfect for regular cooking and frying",
                    "Levels 7-9 for high-heat cooking, boiling, and searing",
                    "Sword knobs provide better grip and precise adjustment",
                    "Ceramic surface requires gentle cleaning - avoid abrasives",
                    "Residual heat indicator prevents burns",
                    "Two burners allow simultaneous cooking",
                    "Combine with other Domino units for complete cooking solution",
                    "FlameSelect makes temperature control as precise as electric cooking"
                ],
                "compatibility": "Requires LPG gas connection. Can be installed alongside other Domino hobs for modular configuration."
            },
            "documents": [
                {
                    "name": "User Manual",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/domino-gas-hobs/PRB3A6D70I",
                    "description": "Complete user manual with installation and operation instructions"
                },
                {
                    "name": "Installation Instructions",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/domino-gas-hobs/PRB3A6D70I",
                    "description": "Detailed installation guide"
                },
                {
                    "name": "Product Specification Sheet",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/domino-gas-hobs/PRB3A6D70I",
                    "description": "Complete technical specifications"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "tags": ["gas hob", "domino", "bosch", "series 8", "kitchen appliance", "compact", "2 burner", "flameselect", "ceramic", "30cm", "made in europe", "sword knobs"],
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
            print(f"   Product ID: {product['id']}")
            print(f"   Model: {product['model_number']}")
            print(f"   Burners: {product['specifications']['Burners']['Total Burners']}")
            print(f"   Price: ₹{product['price']:,.2f} (was ₹{product['original_price']:,.2f})")
            print(f"   Category: {product['category']} - {product['sub_category']}")
            if 'FlameSelect' in str(product.get('features', [])):
                print(f"   Special: FlameSelect with 9 precise levels")
            print(f"   Images: {len(product['images'])} images added")
            print()
        
    except Exception as e:
        print(f"❌ Error adding products: {e}")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_domino_gas_hobs())
