import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
products_collection = db['products']

async def add_siemens_hobs():
    """Add seven Siemens Hob models to database - 3 Gas, 1 Induction, 3 Domino"""
    
    products = [
        # GAS HOBS
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ500 Gas Hob 90 cm Tempered Glass Black EP9B6FG20I",
            "brand": "Siemens",
            "model_number": "EP9B6FG20I",
            "category": "Gas Hob",
            "sub_category": "90 cm Gas Hob",
            "price": 84990.00,
            "description": "Siemens iQ500 Gas Hob with tempered glass surface, individual cast-iron pan supports, and sword knobs for modern design and ease of use.",
            "short_description": "iQ500 90 cm Gas Hob with tempered glass, sword knobs, and 4 burner positions.",
            "long_description": "The Siemens iQ500 Gas Hob EP9B6FG20I features a sleek black tempered glass surface that's extremely heat-resistant and easy to clean. The sword knobs combine the highest ease of use with modern design, making operation intuitive. Individual cast-iron pan supports demonstrate high-quality materials and workmanship, providing excellent stability for cookware. With 4 burner positions, you have flexibility for various cooking needs. The tempered glass surface maintains its pristine appearance even with regular use. Preset for liquid gas (G30,31 28-30/37 mbar) with included nozzle set for natural gas (H/E/(L) 20 (25) mbar).",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/21337001_EP9B6FG20I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/21579165_EP9B6FG20I_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/21579164_EP9B6FG20I_PGA5_def.webp"
            ],
            "stock": 12,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Cooktop Type": "Gas cooktop",
                "Number of Burners": "4",
                "Surface Material": "Tempered glass",
                "Pan Supports": "Cast iron single (individual)",
                "Knob Type": "Sword knob",
                "Gas Type Preset": "Liquid gas G30,31 28-30/37 mbar",
                "Alternative Gas": "Natural gas H/E/(L) 20 (25) mbar",
                "Width": "90 cm",
                "Color": "Black",
                "Series": "iQ500"
            },
            "key_features": [
                "Modern black tempered glass surface",
                "Individual cast-iron pan supports for stability",
                "Sword knobs for ease of use and modern design",
                "4 burner positions for cooking flexibility",
                "Extremely heat-resistant and easy to clean",
                "Compatible with liquid and natural gas",
                "High-quality materials and workmanship"
            ],
            "highlights": [
                "Individual cast-iron pan supports",
                "Sword knob combines ease of use with modern design",
                "Black tempered glass - heat-resistant and easy to clean"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/hobs-and-cooktops/gas-stoves/EP9B6FG20I",
                    "title": "EP9B6FG20I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ500 Gas Hob 60 cm Tempered Glass Black EP6A6HB20I",
            "brand": "Siemens",
            "model_number": "EP6A6HB20I",
            "category": "Gas Hob",
            "sub_category": "60 cm Gas Hob",
            "price": 72490.00,
            "description": "Siemens iQ500 Gas Hob featuring stepFlame Technology, powerful 3.6 kW wok burner, and individual cast-iron pan supports with rubber feet.",
            "short_description": "iQ500 60 cm Gas Hob with stepFlame Technology, wok burner, and tempered glass surface.",
            "long_description": "The Siemens iQ500 Gas Hob EP6A6HB20I delivers precise cooking control with stepFlame Technology and a powerful wok burner. The 3.6 kW wok burner is ideal for fast cooking with even heat distribution, perfect for a wide variety of foods even in large quantities. Individual cast-iron pan supports with rubber feet provide excellent stability and protection. The tempered glass surface combines modern aesthetics with easy maintenance. With 4 burner positions and stepFlame Technology, you can fine-tune heat levels for perfect cooking results. Compatible with both liquid gas and natural gas.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01657053_EP6A6HB20_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01753946_PPQ7A6B90_GasHob_build-in_Bosch_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01838335_EP6A6PB20_GasHob_build-in_Siemens_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01838339_EP6A6PB20_GasHob_build-in_Siemens_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01838341_EP6A6HB20_GasHob_build-in_Siemens_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01790046_EP6A6HB20_GasHob_build-in_Siemens_PGA5_def.webp"
            ],
            "stock": 15,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Cooktop Type": "Gas cooktop",
                "Number of Burners": "4",
                "stepFlame Technology": "Yes",
                "Wok Burner Power": "3.6 kW",
                "Surface Material": "Tempered glass",
                "Pan Supports": "Cast iron with rubber feet (individual)",
                "Gas Type Preset": "Liquid gas G30,31 28-30/37 mbar",
                "Alternative Gas": "Natural gas H/E/(L) 20 (25) mbar",
                "Width": "60 cm",
                "Color": "Black",
                "Series": "iQ500"
            },
            "key_features": [
                "stepFlame Technology for precise control",
                "Powerful 3.6 kW wok burner for fast cooking",
                "Individual cast-iron pan supports with rubber feet",
                "Even heat distribution",
                "4 burner positions",
                "Tempered glass surface - easy to clean",
                "Compatible with liquid and natural gas"
            ],
            "highlights": [
                "Fast cooking with even heat distribution: the wok burner with 3.6 kW",
                "Individual cast-iron pan supports"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/hobs-and-cooktops/gas-stoves/EP6A6HB20I",
                    "title": "EP6A6HB20I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ500 Gas Hob 60 cm Stainless Steel EC6A5HB90I",
            "brand": "Siemens",
            "model_number": "EC6A5HB90I",
            "category": "Gas Hob",
            "sub_category": "60 cm Gas Hob",
            "price": 59990.00,
            "description": "Siemens iQ500 Gas Hob with frameless design, stainless steel surface, stepFlame Technology, and powerful 3.6 kW wok burner.",
            "short_description": "iQ500 60 cm Frameless Gas Hob with stainless steel, stepFlame Technology, and wok burner.",
            "long_description": "The Siemens iQ500 Gas Hob EC6A5HB90I features a modern frameless design with durable stainless steel surface. The stepFlame Technology allows for precise flame control across all 4 burner positions. The powerful 3.6 kW wok burner delivers fast cooking with even heat distribution, perfect for large quantities and various cooking styles. Cast iron pan supports with rubber feet provide excellent stability and protection for your cookware. The stainless steel surface is easy to clean and maintain. Compatible with liquid gas (preset) and natural gas (nozzle set included).",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01676015_EC6A5HB90_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01837507_EC6A5PB90_GasHob_build-in_Siemens_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01797919_EC6A5PB90_GasHob_build-in_Siemens_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01837511_EC6A5PB90_GasHob_build-in_Siemens_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01833589_EC6A5HB90_GasHob_build-in_Siemens_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01791284_EC6A5HB90_GasHob_build-in_Siemens_PGA5_def.webp"
            ],
            "stock": 18,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Cooktop Type": "Gas cooktop",
                "Number of Burners": "4",
                "stepFlame Technology": "Yes",
                "Frame Type": "Frameless",
                "Wok Burner Power": "3.6 kW",
                "Surface Material": "Stainless steel",
                "Pan Supports": "Cast iron with rubber feet",
                "Gas Type Preset": "Liquid gas G30,31 28-30/37 mbar",
                "Alternative Gas": "Natural gas H/E/(L) 20 (25) mbar",
                "Width": "60 cm",
                "Color": "Stainless Steel",
                "Series": "iQ500"
            },
            "key_features": [
                "Frameless design for modern look",
                "stepFlame Technology for precise control",
                "Powerful 3.6 kW wok burner",
                "Durable stainless steel surface",
                "Cast iron pan supports with rubber feet",
                "4 burner positions",
                "Easy to clean and maintain"
            ],
            "highlights": [
                "Fast cooking with even heat distribution: the wok burner with 3.6 kW"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/hobs-and-cooktops/gas-stoves/EC6A5HB90I",
                    "title": "EC6A5HB90I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        # INDUCTION HOB
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ700 Induction Hob 60 cm Black EX675LYC5I",
            "brand": "Siemens",
            "model_number": "EX675LYC5I",
            "category": "Induction Hob",
            "sub_category": "60 cm Induction Hob",
            "price": 189990.00,
            "description": "Premium Siemens iQ700 Induction Hob with flexInduction Plus, fryingSensor Plus, powerMove Plus, and flexMotion for ultimate cooking flexibility.",
            "short_description": "iQ700 60 cm Induction Hob with flexInduction Plus, Dual lightSlider, and intelligent cooking zones.",
            "long_description": "The Siemens iQ700 Induction Hob EX675LYC5I represents the pinnacle of induction cooking technology. The flexInduction Plus feature creates smart, extendable cooking zones that adapt to your cookware size and shape. The innovative Dual lightSlider provides easy and intuitive hob operation with tap-and-slide control. fryingSensor Plus ensures perfect frying results with no burning or scorching. powerMove Plus enables intuitive control with three heating zones at different temperatures, activated by simply moving your cookware. The flexMotion feature remembers heat settings for individual pans while moving them freely across the hob. With dimensions of 51x602x520 mm and front facette design with side profiles, this hob combines premium performance with elegant aesthetics.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02951093_EX675LYC5I_ElectricHob_Siemens_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA03119596_EX675LYC5I_U_ElectricHob_Siemens_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA03119572_EX675LYC5I_ElectricHob_Siemens_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01058954_DA3_ET675LMP1D_Top_Siemens_Facette_vorne_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA03119577_EX675LYC5I_ElectricHob_Siemens_PGA3_def.webp"
            ],
            "stock": 6,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Induction cooktop",
                "Width": "60 cm",
                "Dimensions": "51 x 602 x 520 mm",
                "Control Type": "Dual lightSlider touch control",
                "Frame Type": "Front facette, side profiles",
                "Color": "Black",
                "Heating with Booster": "All zones",
                "Series": "iQ700"
            },
            "key_features": [
                "flexInduction Plus - Smart cooking zones adapt to cookware",
                "Dual lightSlider for easy and intuitive control",
                "fryingSensor Plus - No more burning or scorching",
                "powerMove Plus - Move pot to change settings",
                "flexMotion - Remembers settings while moving pans",
                "All zones with booster function",
                "Premium iQ700 series quality"
            ],
            "highlights": [
                "The hob that adapts to your cookware",
                "Tap and slide for smooth, effortless control",
                "Total control for frying",
                "Move the pot to change the setting"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/hobs-and-cooktops/induction-cooktops/EX675LYC5I",
                    "title": "EX675LYC5I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        # DOMINO HOBS
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ700 Flex Induction Domino Hob 30 cm Black EX375FXB5I",
            "brand": "Siemens",
            "model_number": "EX375FXB5I",
            "category": "Induction Hob",
            "sub_category": "Domino Hob",
            "price": 128990.00,
            "description": "Siemens iQ700 30 cm Domino Induction Hob with flexInduction, touchSlider, powerMove Plus, and powerBoost for modular kitchen design.",
            "short_description": "iQ700 30 cm Domino Induction Hob with flexInduction and powerMove Plus technology.",
            "long_description": "The Siemens iQ700 Flex Induction Domino Hob EX375FXB5I is perfect for creating customized cooking setups. At 30 cm wide, it's ideal for combining with other Domino or faceted design cooktops. The flexInduction technology creates smart cooking zones that adapt to your cookware size and shape. touchSlider allows precise power level control with one touch. powerMove Plus enables intuitive control with three heating zones at different temperatures, simply by moving your pot. powerBoost function provides extra power when needed. With dimensions of 51x302x520 mm and design frame, this domino hob offers premium flexibility for modern kitchens.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02951092_EX375FXB5I_ElectricHob_Siemens_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA03248470_EX375FXB5I_ElectricHob_Siemens_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01058954_DA3_ET675LMP1D_Top_Siemens_Facette_vorne_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA03248471_EX375FXB5I_ElectricHob_Siemens_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA03035105_118193__BSH_Siemens_kitchen__stills_scene_10_def.webp"
            ],
            "stock": 8,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Type": "Induction cooktop",
                "Width": "30 cm",
                "Dimensions": "51 x 302 x 520 mm",
                "Number of Cooking Zones": "2",
                "Controls": "Slider",
                "Residual Heat Indicator": "Separate",
                "Surface Material": "Ceramic",
                "Frame Type": "Design frame",
                "Color": "Black",
                "Series": "iQ700"
            },
            "key_features": [
                "30 cm width - ideal for combining with other Domino cooktops",
                "flexInduction - Smart zone adapts to cookware",
                "touchSlider for one-touch power control",
                "powerMove Plus - Move pot to change settings",
                "powerBoost for extra power when needed",
                "2 cooking zones",
                "Modular kitchen design flexibility"
            ],
            "highlights": [
                "Individual pleasure in cooking: domino hobs",
                "The hob that adjusts to your cookware",
                "Temperature control at your fingertips",
                "Move the pot to change the setting"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/hobs-and-cooktops/domino-cooktops/EX375FXB5I",
                    "title": "EX375FXB5I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ700 Domino Gas Hob 30 cm Ceramic Black ER3A6AD70I",
            "brand": "Siemens",
            "model_number": "ER3A6AD70I",
            "category": "Gas Hob",
            "sub_category": "Domino Hob",
            "price": 87990.00,
            "description": "Siemens iQ700 30 cm Domino Gas Hob with premium ceramic surface and design frame for modular kitchen configurations.",
            "short_description": "iQ700 30 cm Domino Gas Hob with ceramic surface and 1 burner position.",
            "long_description": "The Siemens iQ700 Domino Gas Hob ER3A6AD70I offers premium gas cooking in a compact 30 cm format. The elegant black ceramic surface combines style with durability and easy cleaning. With dimensions of 59x302x520 mm, this domino hob is perfect for creating customized cooking configurations. The design frame adds a sophisticated touch. Single burner position provides focused cooking power. Knob controls ensure reliable operation. Compatible with liquid gas (preset) and natural gas (nozzle set included). Ideal for combining with other Domino hobs to create your perfect cooking setup.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01656979_ER3A6AD70_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01775585_ER3A6AD70_GasHob_build-in_Siemens_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01835221_ER3A6AD70_GasHob_build-in_Siemens_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01835223_ER3A6AD70_GasHob_build-in_Siemens_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01775611_ER3A6AD70_GasHob_build-in_Siemens_PGA5_def.webp"
            ],
            "stock": 10,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Cooktop Type": "Gas cooktop",
                "Width": "30 cm",
                "Dimensions": "59 x 302 x 520 mm",
                "Number of Burners": "1",
                "Controls": "Knob",
                "Residual Heat Indicator": "Separate",
                "Surface Material": "Ceramic",
                "Frame Type": "Design frame",
                "Gas Type Preset": "Liquid gas G30,31 28-30/37 mbar",
                "Color": "Black",
                "Series": "iQ700"
            },
            "key_features": [
                "30 cm compact domino design",
                "Premium black ceramic surface",
                "Design frame for elegant aesthetics",
                "Single powerful burner",
                "Easy to clean ceramic surface",
                "Compatible with liquid and natural gas",
                "Perfect for modular kitchen setups"
            ],
            "highlights": [
                "Compact domino design for flexibility",
                "Premium ceramic surface",
                "Design frame"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/hobs-and-cooktops/domino-cooktops/ER3A6AD70I",
                    "title": "ER3A6AD70I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Siemens iQ700 Domino Gas Hob 30 cm Ceramic Black ER3A6BD70I",
            "brand": "Siemens",
            "model_number": "ER3A6BD70I",
            "category": "Gas Hob",
            "sub_category": "Domino Hob",
            "price": 75490.00,
            "description": "Siemens iQ700 30 cm Domino Gas Hob with ceramic surface, 2 burner positions, and design frame for modular cooking solutions.",
            "short_description": "iQ700 30 cm Domino Gas Hob with ceramic surface and 2 burner positions.",
            "long_description": "The Siemens iQ700 Domino Gas Hob ER3A6BD70I provides dual burner flexibility in a compact 30 cm format. The premium black ceramic surface offers elegant styling and easy maintenance. With dimensions of 47x302x520 mm, this domino hob fits seamlessly into modular kitchen designs. Two burner positions give you cooking flexibility while maintaining a compact footprint. The design frame adds a sophisticated aesthetic touch. Knob controls ensure reliable operation. Compatible with liquid gas (preset) and includes nozzle set for natural gas conversion. Perfect for creating customized cooking configurations with other Domino hobs.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01656989_ER3A6BD70_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01835224_ER3A6BD70_GasHob_build-in_Siemens_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01775587_ER3A6BD70_GasHob_build-in_ER3A6BD70_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01835220_ER3A6BD70_GasHob_build-in_Bosch_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01790022_ER3A6BD70_GasHob_build-in_Siemens_PGA5_def.webp"
            ],
            "stock": 12,
            "rating": 0.0,
            "reviews_count": 0,
            "specifications": {
                "Cooktop Type": "Gas cooktop",
                "Width": "30 cm",
                "Dimensions": "47 x 302 x 520 mm",
                "Number of Burners": "2",
                "Controls": "Knob",
                "Residual Heat Indicator": "Separate",
                "Surface Material": "Ceramic",
                "Frame Type": "Design frame",
                "Gas Type Preset": "Liquid gas G30,31 28-30/37 mbar",
                "Color": "Black",
                "Series": "iQ700"
            },
            "key_features": [
                "30 cm compact domino design",
                "2 burner positions for flexibility",
                "Premium black ceramic surface",
                "Design frame for elegant look",
                "Easy to clean and maintain",
                "Compatible with liquid and natural gas",
                "Ideal for modular kitchen configurations"
            ],
            "highlights": [
                "Compact domino design with 2 burners",
                "Premium ceramic surface",
                "Design frame"
            ],
            "documents": [
                {
                    "type": "User Manual",
                    "url": "https://www.siemens-home.bsh-group.in/en/mkt-product/cooking-baking/hobs-and-cooktops/domino-cooktops/ER3A6BD70I",
                    "title": "ER3A6BD70I User Manual"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    print("=" * 70)
    print("Adding 7 Siemens Hobs to Database")
    print("=" * 70)
    
    added_count = 0
    for product in products:
        # Check if product already exists
        existing = await products_collection.find_one({"model_number": product["model_number"]})
        if existing:
            print(f"⚠️  Product {product['model_number']} already exists. Skipping...")
            continue
        
        # Insert product
        result = await products_collection.insert_one(product)
        added_count += 1
        print(f"\n✅ Added: {product['name']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Price: ₹{product['price']:,.2f}")
        print(f"   Category: {product['category']}")
        print(f"   Sub-category: {product['sub_category']}")
        print(f"   Images: {len(product['images'])} images")
        print(f"   ID: {product['id']}")
    
    # Get total product count
    total_count = await products_collection.count_documents({})
    gas_hob_count = await products_collection.count_documents({"category": "Gas Hob"})
    induction_count = await products_collection.count_documents({"category": "Induction Hob"})
    siemens_count = await products_collection.count_documents({"brand": "Siemens"})
    
    print("\n" + "=" * 70)
    print(f"✅ Successfully added {added_count} Siemens Hobs!")
    print(f"Total products in database: {total_count}")
    print(f"Total Gas Hobs: {gas_hob_count}")
    print(f"Total Induction Hobs: {induction_count}")
    print(f"Total Siemens products: {siemens_count}")
    print("=" * 70)
    print("\n⚠️  NOTE: Premium hobs over ₹100,000 may be filtered on frontend.")

if __name__ == "__main__":
    asyncio.run(add_siemens_hobs())
