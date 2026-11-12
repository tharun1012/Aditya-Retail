"""
Generate comprehensive Siemens and Bosch product catalog
Based on actual product lines and realistic pricing
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')

# Comprehensive Siemens Product Catalog
SIEMENS_PRODUCTS = [
    # OVENS - iQ700 Series
    {
        "name": "Siemens iQ700 Built-in Oven 60 x 60 cm Black HB736G1B1",
        "series": "iQ700",
        "category": "Ovens",
        "model": "HB736G1B1",
        "price": 155900,
        "description": "Premium built-in oven with activeClean self-cleaning, coolStart, and Home Connect smart control",
        "features": ["activeClean pyrolytic self-cleaning", "coolStart for frozen foods", "Home Connect enabled", "LED interior lighting", "cookControl Plus", "71L capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/HB736G1B1-siemens-oven-1-1024x1024.jpg"
    },
    {
        "name": "Siemens iQ700 Built-in Oven 60 x 60 cm Black HB978GNB1B",
        "series": "iQ700",
        "category": "Ovens",
        "model": "HB978GNB1B",
        "price": 158900,
        "description": "Premium pyrolytic oven with fullSteam function and Home Connect",
        "features": ["Pyrolytic self-cleaning", "fullSteam function", "Home Connect", "varioClip rails", "softMove door", "71L capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/HB736G1B1-siemens-oven-1-1024x1024.jpg"
    },
    {
        "name": "Siemens iQ500 Built-in Oven 60 x 60 cm Stainless Steel HB573ABS0",
        "series": "iQ500",
        "category": "Ovens",
        "model": "HB573ABS0",
        "price": 98900,
        "description": "Built-in oven with 3D hotAir Plus and ecoClean Direct cleaning",
        "features": ["3D hotAir Plus", "ecoClean Direct", "LED interior lighting", "Electronic clock", "CoolStart", "71L capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/HB736G1B1-siemens-oven-1-1024x1024.jpg"
    },
    
    # DISHWASHERS - iQ700 & iQ500 Series
    {
        "name": "Siemens iQ700 Built-in Dishwasher 60cm SN778D06TI",
        "series": "iQ700",
        "category": "Dishwashers",
        "model": "SN778D06TI",
        "price": 124900,
        "description": "Premium dishwasher with Zeolith drying and Home Connect",
        "features": ["Zeolith drying technology", "varioSpeed Plus", "Home Connect", "brilliantShine system", "timeLight", "13 place settings"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/SN678X36TE-siemens-dishwasher-1-1024x1024.jpg"
    },
    {
        "name": "Siemens iQ500 Built-in Dishwasher 60cm SN658X06TE",
        "series": "iQ500",
        "category": "Dishwashers",
        "model": "SN658X06TE",
        "price": 94900,
        "description": "Efficient dishwasher with varioSpeed Plus and brilliant Shine",
        "features": ["varioSpeed Plus", "brilliantShine system", "varioDrawer", "glassProtect technology", "13 place settings", "44 dB noise level"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/SN678X36TE-siemens-dishwasher-1-1024x1024.jpg"
    },
    
    # COOKTOPS - iQ700 & iQ500 Series
    {
        "name": "Siemens iQ700 Induction Hob 80cm Black EX877LYV5E",
        "series": "iQ700",
        "category": "Cooktops",
        "model": "EX877LYV5E",
        "price": 124900,
        "description": "Premium induction cooktop with flexInduction Plus and fryingSensor Plus",
        "features": ["flexInduction Plus zones", "fryingSensor Plus", "powerBoost function", "Home Connect", "Touch control", "17 power levels"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/EH675FVB1E-siemens-hob-1024x1024.jpg"
    },
    {
        "name": "Siemens iQ500 Induction Hob 60cm Black EH675FVB1E",
        "series": "iQ500",
        "category": "Cooktops",
        "model": "EH675FVB1E",
        "price": 68900,
        "description": "Induction cooktop with flexInduction zones and powerBoost",
        "features": ["flexInduction zones", "powerBoost function", "Timer with switch-off", "Touch control", "Child lock", "17 power levels"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/EH675FVB1E-siemens-hob-1024x1024.jpg"
    },
    {
        "name": "Siemens iQ300 Gas Hob 75cm Stainless Steel ER7A6SD70",
        "series": "iQ300",
        "category": "Cooktops",
        "model": "ER7A6SD70",
        "price": 42900,
        "description": "5 burner gas hob with stepFlame technology",
        "features": ["stepFlame technology", "5 gas burners", "Cast iron pan supports", "Flame failure safety", "Easy to clean", "Stainless steel surface"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/EH675FVB1E-siemens-hob-1024x1024.jpg"
    },
    
    # HOODS - iQ700 & iQ500 Series
    {
        "name": "Siemens iQ700 Wall-mounted Hood 90cm Black LC91BUV60",
        "series": "iQ700",
        "category": "Hoods",
        "model": "LC91BUV60",
        "price": 84900,
        "description": "Premium hood with brushless iQdrive motor and LED lighting",
        "features": ["Brushless iQdrive motor", "LED lighting", "Touch control", "Metal grease filters", "Intensive mode", "850 m³/h airflow"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/hood-placeholder.jpg"
    },
    {
        "name": "Siemens iQ500 Wall-mounted Hood 60cm Stainless Steel LC68BIT60",
        "series": "iQ500",
        "category": "Hoods",
        "model": "LC68BIT60",
        "price": 54900,
        "description": "Efficient hood with LED lighting and push button control",
        "features": ["LED lighting", "Push button control", "Metal grease filters", "3 speed levels", "Intensive setting", "620 m³/h airflow"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/hood-placeholder.jpg"
    },
    
    # REFRIGERATORS - iQ700 & iQ500 Series
    {
        "name": "Siemens iQ700 Side-by-Side Refrigerator 659L Black KA93GAIEP",
        "series": "iQ700",
        "category": "Refrigerators",
        "model": "KA93GAIEP",
        "price": 189900,
        "description": "Premium side-by-side fridge with hyperFresh Plus and Home Connect",
        "features": ["hyperFresh Plus", "noFrost technology", "Home Connect", "LED lighting", "Ice & water dispenser", "659L capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/fridge-placeholder.jpg"
    },
    {
        "name": "Siemens iQ500 French Door Refrigerator 559L Stainless Steel KF96RSBEA",
        "series": "iQ500",
        "category": "Refrigerators",
        "model": "KF96RSBEA",
        "price": 149900,
        "description": "French door refrigerator with hyperFresh and noFrost",
        "features": ["hyperFresh drawers", "noFrost technology", "LED lighting", "Multi Airflow System", "BigBox freezer drawer", "559L capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/fridge-placeholder.jpg"
    },
    
    # WASHING MACHINES - iQ700 & iQ500 Series
    {
        "name": "Siemens iQ700 Front Load Washing Machine 9kg White WM14U640IN",
        "series": "iQ700",
        "category": "Washing Machines",
        "model": "WM14U640IN",
        "price": 84900,
        "description": "Premium washing machine with iQdrive motor and Home Connect",
        "features": ["iQdrive motor", "speedPerfect function", "varioSoft drum", "Home Connect", "antiVibration design", "9kg capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/washing-machine-placeholder.jpg"
    },
    {
        "name": "Siemens iQ500 Front Load Washing Machine 8kg White WM12U460IN",
        "series": "iQ500",
        "category": "Washing Machines",
        "model": "WM12U460IN",
        "price": 64900,
        "description": "Efficient washing machine with varioSoft drum and aquaStop",
        "features": ["varioSoft drum system", "speedPerfect", "aquaStop lifetime guarantee", "LED display", "Reload function", "8kg capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/washing-machine-placeholder.jpg"
    },
    
    # DRYERS - iQ700 Series
    {
        "name": "Siemens iQ700 Heat Pump Dryer 9kg White WT47XMH0IN",
        "series": "iQ700",
        "category": "Dryers",
        "model": "WT47XMH0IN",
        "price": 74900,
        "description": "Premium heat pump dryer with autoDry and Home Connect",
        "features": ["Heat pump technology", "autoDry sensor", "softDry drum", "Home Connect", "Energy efficiency A+++", "9kg capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/dryer-placeholder.jpg"
    },
    
    # COFFEE MACHINES - iQ700 Series
    {
        "name": "Siemens iQ700 Built-in Coffee Machine Black CT836LEB6",
        "series": "iQ700",
        "category": "Coffee Machines",
        "model": "CT836LEB6",
        "price": 124900,
        "description": "Premium built-in coffee machine with aromaDouble Shot",
        "features": ["aromaDouble Shot", "oneTouch DoubleCup", "sensoFlow System", "Home Connect", "Ceramic grinder", "TFT display"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/coffee-machine-placeholder.jpg"
    },
    
    # MICROWAVES - iQ500 & iQ300 Series
    {
        "name": "Siemens iQ500 Built-in Microwave 38L Black BF634LGS1",
        "series": "iQ500",
        "category": "Microwaves",
        "model": "BF634LGS1",
        "price": 54900,
        "description": "Built-in microwave with grill and hotAir function",
        "features": ["Grill and hotAir", "LED interior lighting", "Touch control", "Auto programs", "Child lock", "38L capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/microwave-placeholder.jpg"
    },
    {
        "name": "Siemens iQ300 Built-in Microwave 25L Stainless Steel BF525LMS0",
        "series": "iQ300",
        "category": "Microwaves",
        "model": "BF525LMS0",
        "price": 39900,
        "description": "Compact built-in microwave with LED lighting",
        "features": ["LED interior lighting", "Electronic control", "Auto programs", "Quick start", "Child lock", "25L capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/microwave-placeholder.jpg"
    }
]

# Comprehensive Bosch Product Catalog
BOSCH_PRODUCTS = [
    # OVENS - Serie 8 & Serie 6
    {
        "name": "Bosch Serie 8 Built-in Oven 60 x 60 cm Black HBG6767S1",
        "series": "Serie 8",
        "category": "Ovens",
        "model": "HBG6767S1",
        "price": 119900,
        "description": "Premium oven with PerfectBake sensor and EcoClean Direct",
        "features": ["PerfectBake sensor", "PerfectRoast sensor", "EcoClean Direct", "LED interior lighting", "3D Hotair Plus", "71L capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-oven-placeholder.jpg"
    },
    {
        "name": "Bosch Serie 6 Built-in Oven 60 x 60 cm Stainless Steel HBA5780S0",
        "series": "Serie 6",
        "category": "Ovens",
        "model": "HBA5780S0",
        "price": 84900,
        "description": "Built-in oven with 3D Hotair and EcoClean back wall",
        "features": ["3D Hotair", "EcoClean back wall", "LED interior lighting", "CoolStart", "Electronic clock", "71L capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-oven-placeholder.jpg"
    },
    {
        "name": "Bosch Serie 4 Built-in Oven 60 x 60 cm Black HBF113BR0A",
        "series": "Serie 4",
        "category": "Ovens",
        "model": "HBF113BR0A",
        "price": 64900,
        "description": "Reliable built-in oven with 7 heating functions",
        "features": ["7 heating functions", "LED interior lighting", "Electronic timer", "Top and bottom heating", "Grill function", "66L capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-oven-placeholder.jpg"
    },
    
    # DISHWASHERS - Serie 6 & Serie 4
    {
        "name": "Bosch Serie 6 Built-in Dishwasher 60cm SMV68TX06E",
        "series": "Serie 6",
        "category": "Dishwashers",
        "model": "SMV68TX06E",
        "price": 94900,
        "description": "Premium dishwasher with PerfectDry and VarioSpeed Plus",
        "features": ["PerfectDry with Zeolith", "VarioSpeed Plus", "EcoSilence Drive", "TimeLight", "Glass protection", "13 place settings"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-dishwasher-placeholder.jpg"
    },
    {
        "name": "Bosch Serie 4 Built-in Dishwasher 60cm SMV46MX03E",
        "series": "Serie 4",
        "category": "Dishwashers",
        "model": "SMV46MX03E",
        "price": 74900,
        "description": "Efficient dishwasher with VarioFlex baskets",
        "features": ["VarioFlex baskets", "EcoSilence Drive", "Load sensor", "Extra dry function", "Glass protection", "13 place settings"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-dishwasher-placeholder.jpg"
    },
    {
        "name": "Bosch Serie 2 Freestanding Dishwasher 60cm SMS24AW00I",
        "series": "Serie 2",
        "category": "Dishwashers",
        "model": "SMS24AW00I",
        "price": 44900,
        "description": "Value dishwasher with ActiveWater technology",
        "features": ["ActiveWater technology", "VarioSpeed", "LoadSensor", "Rack Stopper", "Delay start", "12 place settings"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-dishwasher-placeholder.jpg"
    },
    
    # COOKTOPS - Serie 8 & Serie 6
    {
        "name": "Bosch Serie 8 Induction Hob 80cm Black PXX875D34E",
        "series": "Serie 8",
        "category": "Cooktops",
        "model": "PXX875D34E",
        "price": 114900,
        "description": "Premium induction cooktop with FlexInduction",
        "features": ["FlexInduction zones", "PerfectFry sensor", "PowerBoost function", "Timer", "Touch control", "17 power levels"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-cooktop-placeholder.jpg"
    },
    {
        "name": "Bosch Serie 6 Induction Hob 60cm Black PID631BB3E",
        "series": "Serie 6",
        "category": "Cooktops",
        "model": "PID631BB3E",
        "price": 64900,
        "description": "Induction hob with DirectSelect control",
        "features": ["DirectSelect control", "PowerBoost function", "QuickStart", "ReStart function", "Timer", "17 power levels"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-cooktop-placeholder.jpg"
    },
    {
        "name": "Bosch Serie 4 Gas Hob 75cm Stainless Steel PCI6A5B90I",
        "series": "Serie 4",
        "category": "Cooktops",
        "model": "PCI6A5B90I",
        "price": 38900,
        "description": "4 burner gas hob with FlameSelect technology",
        "features": ["FlameSelect technology", "4 gas burners", "Cast iron pan supports", "Flame failure safety", "Easy cleaning", "Auto ignition"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-cooktop-placeholder.jpg"
    },
    
    # HOODS - Serie 6 & Serie 4
    {
        "name": "Bosch Serie 6 Wall-mounted Hood 90cm Black DWB97IM60",
        "series": "Serie 6",
        "category": "Hoods",
        "model": "DWB97IM60",
        "price": 74900,
        "description": "Premium hood with efficient EcoSilence Drive motor",
        "features": ["EcoSilence Drive", "LED lighting", "Touch control", "Metal grease filters", "Intensive setting", "730 m³/h airflow"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-hood-placeholder.jpg"
    },
    {
        "name": "Bosch Serie 4 Wall-mounted Hood 60cm Stainless Steel DWP64BC50I",
        "series": "Serie 4",
        "category": "Hoods",
        "model": "DWP64BC50I",
        "price": 44900,
        "description": "Efficient hood with halogen lighting",
        "features": ["Halogen lighting", "Push button control", "Metal grease filters", "3 power levels", "Intensive mode", "420 m³/h airflow"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-hood-placeholder.jpg"
    },
    
    # REFRIGERATORS - Serie 6 & Serie 4
    {
        "name": "Bosch Serie 6 Side-by-Side Refrigerator 656L Stainless Steel KAN93VIFP",
        "series": "Serie 6",
        "category": "Refrigerators",
        "model": "KAN93VIFP",
        "price": 149900,
        "description": "Premium side-by-side fridge with VitaFresh Pro",
        "features": ["VitaFresh Pro", "NoFrost", "SuperCooling", "SuperFreezing", "LED lighting", "656L capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-fridge-placeholder.jpg"
    },
    {
        "name": "Bosch Serie 4 French Door Refrigerator 510L Stainless Steel KFN96APEAG",
        "series": "Serie 4",
        "category": "Refrigerators",
        "model": "KFN96APEAG",
        "price": 114900,
        "description": "French door refrigerator with VitaFresh and NoFrost",
        "features": ["VitaFresh", "NoFrost", "LED lighting", "Multi Airflow", "BigBox freezer", "510L capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-fridge-placeholder.jpg"
    },
    {
        "name": "Bosch Serie 2 Double Door Refrigerator 347L Stainless Steel KDN43VL40I",
        "series": "Serie 2",
        "category": "Refrigerators",
        "model": "KDN43VL40I",
        "price": 54900,
        "description": "Reliable double door refrigerator with MultiAirflow",
        "features": ["MultiAirflow System", "LED lighting", "VitaFresh", "Frost free", "Energy efficient", "347L capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-fridge-placeholder.jpg"
    },
    
    # WASHING MACHINES - Serie 8 & Serie 6
    {
        "name": "Bosch Serie 8 Front Load Washing Machine 9kg White WAX32EH0IN",
        "series": "Serie 8",
        "category": "Washing Machines",
        "model": "WAX32EH0IN",
        "price": 74900,
        "description": "Premium washing machine with i-DOS automatic dosing",
        "features": ["i-DOS automatic dosing", "VarioDrum", "ActiveWater Plus", "SpeedPerfect", "Home Connect", "9kg capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-washing-machine-placeholder.jpg"
    },
    {
        "name": "Bosch Serie 6 Front Load Washing Machine 8kg White WAT28661IN",
        "series": "Serie 6",
        "category": "Washing Machines",
        "model": "WAT28661IN",
        "price": 54900,
        "description": "Efficient washing machine with VarioDrum and EcoSilence Drive",
        "features": ["VarioDrum", "EcoSilence Drive", "ActiveWater Plus", "SpeedPerfect", "Reload function", "8kg capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-washing-machine-placeholder.jpg"
    },
    {
        "name": "Bosch Serie 4 Front Load Washing Machine 7kg White WAJ24267IN",
        "series": "Serie 4",
        "category": "Washing Machines",
        "model": "WAJ24267IN",
        "price": 39900,
        "description": "Reliable washing machine with ActiveWater technology",
        "features": ["ActiveWater technology", "VarioDrum", "EcoSilence Drive", "LED display", "SpeedPerfect", "7kg capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-washing-machine-placeholder.jpg"
    },
    
    # DRYERS - Serie 6
    {
        "name": "Bosch Serie 6 Heat Pump Dryer 8kg White WTW85460IN",
        "series": "Serie 6",
        "category": "Dryers",
        "model": "WTW85460IN",
        "price": 64900,
        "description": "Energy efficient heat pump dryer with AutoDry",
        "features": ["Heat pump technology", "AutoDry sensor", "SoftDry drum", "LED display", "Energy efficiency A++", "8kg capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-dryer-placeholder.jpg"
    },
    
    # MICROWAVES - Serie 6 & Serie 4
    {
        "name": "Bosch Serie 6 Built-in Microwave 36L Black BFL634GS1",
        "series": "Serie 6",
        "category": "Microwaves",
        "model": "BFL634GS1",
        "price": 49900,
        "description": "Built-in microwave with grill and AutoPilot programs",
        "features": ["Grill function", "AutoPilot 7 programs", "LED interior lighting", "Touch control", "Child lock", "36L capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-microwave-placeholder.jpg"
    },
    {
        "name": "Bosch Serie 4 Built-in Microwave 25L Stainless Steel BFL523MS0",
        "series": "Serie 4",
        "category": "Microwaves",
        "model": "BFL523MS0",
        "price": 34900,
        "description": "Compact built-in microwave with LED lighting",
        "features": ["LED interior lighting", "Electronic control", "AutoPilot 5 programs", "Quick start", "Child lock", "25L capacity"],
        "image": "https://adityaretail.com/wp-content/uploads/2024/12/bosch-microwave-placeholder.jpg"
    }
]

async def generate_and_populate_catalog():
    """Generate and populate comprehensive Siemens and Bosch catalog"""
    
    print("=" * 80)
    print("🚀 GENERATING COMPREHENSIVE SIEMENS & BOSCH CATALOG")
    print("=" * 80)
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Step 1: Delete all existing products
        print("\n🗑️  Clearing existing products...")
        delete_result = await db.products.delete_many({})
        print(f"   ✅ Deleted {delete_result.deleted_count} products")
        
        # Step 2: Prepare Siemens products
        print("\n🔵 Preparing Siemens products...")
        siemens_products = []
        for product_data in SIEMENS_PRODUCTS:
            product = {
                "id": str(uuid.uuid4()),
                "name": product_data["name"],
                "brand": "Siemens",
                "series": product_data["series"],
                "category": product_data["category"],
                "model": product_data["model"],
                "sku": f"SIE-{product_data['model']}",
                "price": product_data["price"],
                "original_price": int(product_data["price"] * 1.15),
                "description": product_data["description"],
                "short_description": f"{product_data['series']} {product_data['category']}",
                "image": product_data["image"],
                "images": [product_data["image"]],
                "features": product_data["features"],
                "specifications": {
                    "Brand": "Siemens",
                    "Series": product_data["series"],
                    "Model": product_data["model"],
                    "Category": product_data["category"],
                    "Warranty": "2 Years Comprehensive"
                },
                "stock_quantity": 12,
                "reorder_level": 5,
                "is_featured": product_data["series"] in ["iQ700", "iQ800"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "warranty": "2 years comprehensive warranty",
                "energy_rating": "A++" if "iQ700" in product_data["series"] else "A+"
            }
            siemens_products.append(product)
        
        print(f"   ✅ Prepared {len(siemens_products)} Siemens products")
        
        # Step 3: Prepare Bosch products
        print("\n🟢 Preparing Bosch products...")
        bosch_products = []
        for product_data in BOSCH_PRODUCTS:
            product = {
                "id": str(uuid.uuid4()),
                "name": product_data["name"],
                "brand": "Bosch",
                "series": product_data["series"],
                "category": product_data["category"],
                "model": product_data["model"],
                "sku": f"BSH-{product_data['model']}",
                "price": product_data["price"],
                "original_price": int(product_data["price"] * 1.12),
                "description": product_data["description"],
                "short_description": f"{product_data['series']} {product_data['category']}",
                "image": product_data["image"],
                "images": [product_data["image"]],
                "features": product_data["features"],
                "specifications": {
                    "Brand": "Bosch",
                    "Series": product_data["series"],
                    "Model": product_data["model"],
                    "Category": product_data["category"],
                    "Warranty": "2 Years Standard"
                },
                "stock_quantity": 15,
                "reorder_level": 5,
                "is_featured": product_data["series"] in ["Serie 8", "Serie 6"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "warranty": "2 years standard warranty",
                "energy_rating": "A++" if "Serie 8" in product_data["series"] else "A+"
            }
            bosch_products.append(product)
        
        print(f"   ✅ Prepared {len(bosch_products)} Bosch products")
        
        # Step 4: Insert all products
        print("\n💾 Inserting products into database...")
        all_products = siemens_products + bosch_products
        result = await db.products.insert_many(all_products)
        print(f"   ✅ Successfully inserted {len(result.inserted_ids)} products")
        
        # Step 5: Summary
        print("\n" + "=" * 80)
        print("✅ CATALOG GENERATION COMPLETE")
        print("=" * 80)
        print(f"🔵 Siemens Products: {len(siemens_products)}")
        print(f"   - iQ700 Series: {sum(1 for p in siemens_products if p['series'] == 'iQ700')}")
        print(f"   - iQ500 Series: {sum(1 for p in siemens_products if p['series'] == 'iQ500')}")
        print(f"   - iQ300 Series: {sum(1 for p in siemens_products if p['series'] == 'iQ300')}")
        print(f"\n🟢 Bosch Products: {len(bosch_products)}")
        print(f"   - Serie 8: {sum(1 for p in bosch_products if p['series'] == 'Serie 8')}")
        print(f"   - Serie 6: {sum(1 for p in bosch_products if p['series'] == 'Serie 6')}")
        print(f"   - Serie 4: {sum(1 for p in bosch_products if p['series'] == 'Serie 4')}")
        print(f"   - Serie 2: {sum(1 for p in bosch_products if p['series'] == 'Serie 2')}")
        print(f"\n📦 Total Products in Database: {len(all_products)}")
        print("=" * 80)
        
        # Product category breakdown
        print("\n📊 CATEGORY BREAKDOWN:")
        categories = {}
        for product in all_products:
            cat = product['category']
            if cat not in categories:
                categories[cat] = {"Siemens": 0, "Bosch": 0}
            categories[cat][product['brand']] += 1
        
        for cat, brands in sorted(categories.items()):
            print(f"   {cat}: Siemens ({brands['Siemens']}) + Bosch ({brands['Bosch']}) = {sum(brands.values())}")
        
        print("=" * 80)
        
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(generate_and_populate_catalog())
