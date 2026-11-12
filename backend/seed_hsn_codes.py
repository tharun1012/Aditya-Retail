"""
Comprehensive HSN Code Seeder for Home Appliances & Kitchen Equipment
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
from datetime import datetime, timezone

# Comprehensive HSN codes for home appliances and kitchen equipment
HSN_CODES = [
    # Refrigerators & Freezers (8418)
    {"code": "84181000", "description": "Combined refrigerator-freezers", "gst_rate": 18.0, "category": "Refrigerators"},
    {"code": "84182100", "description": "Household refrigerators - Compression type", "gst_rate": 18.0, "category": "Refrigerators"},
    {"code": "84182900", "description": "Other household refrigerators", "gst_rate": 18.0, "category": "Refrigerators"},
    {"code": "84183000", "description": "Freezers of the chest type", "gst_rate": 18.0, "category": "Freezers"},
    {"code": "84184000", "description": "Freezers of the upright type", "gst_rate": 18.0, "category": "Freezers"},
    {"code": "84185000", "description": "Refrigerating/freezing display counters, cabinets", "gst_rate": 18.0, "category": "Commercial Refrigeration"},
    
    # Washing Machines (8450)
    {"code": "84501100", "description": "Fully-automatic household washing machines (≤10kg dry linen)", "gst_rate": 18.0, "category": "Washing Machines"},
    {"code": "84501200", "description": "Other machines with built-in centrifugal drier", "gst_rate": 18.0, "category": "Washing Machines"},
    {"code": "84501900", "description": "Other household washing machines (≤10kg dry linen)", "gst_rate": 18.0, "category": "Washing Machines"},
    {"code": "84502000", "description": "Machines of capacity exceeding 10kg", "gst_rate": 18.0, "category": "Washing Machines"},
    
    # Dishwashers (8422)
    {"code": "84221100", "description": "Household type dishwashing machines", "gst_rate": 18.0, "category": "Dishwashers"},
    {"code": "84221900", "description": "Other dishwashing machines", "gst_rate": 18.0, "category": "Dishwashers"},
    
    # Electric Water Heaters & Geysers (8516)
    {"code": "8516", "description": "Electric instantaneous or storage water heaters", "gst_rate": 18.0, "category": "Water Heaters"},
    {"code": "85161000", "description": "Electric instantaneous water heaters", "gst_rate": 18.0, "category": "Water Heaters"},
    {"code": "85161010", "description": "Electric storage water heaters (Geysers)", "gst_rate": 18.0, "category": "Water Heaters"},
    {"code": "85161090", "description": "Other electric water heaters", "gst_rate": 18.0, "category": "Water Heaters"},
    
    # Electric Ovens & Cooking (8516 continued)
    {"code": "85166010", "description": "Electric ovens - Domestic", "gst_rate": 18.0, "category": "Ovens"},
    {"code": "85166020", "description": "Microwave ovens", "gst_rate": 18.0, "category": "Microwaves"},
    {"code": "85166030", "description": "Electric cooking ranges and hot plates", "gst_rate": 18.0, "category": "Cooktops"},
    {"code": "85166040", "description": "Electric grills and roasters", "gst_rate": 18.0, "category": "Grills"},
    {"code": "85166050", "description": "Electric toasters", "gst_rate": 18.0, "category": "Small Appliances"},
    {"code": "85166090", "description": "Other electric cooking appliances", "gst_rate": 18.0, "category": "Cooking Appliances"},
    
    # Electric Irons (8516)
    {"code": "85164000", "description": "Electric smoothing irons", "gst_rate": 18.0, "category": "Irons"},
    
    # Air Conditioners (8415)
    {"code": "84151010", "description": "Split system air conditioners", "gst_rate": 28.0, "category": "Air Conditioners"},
    {"code": "84151020", "description": "Window or wall type air conditioners", "gst_rate": 28.0, "category": "Air Conditioners"},
    {"code": "84158110", "description": "Split system with heat pump", "gst_rate": 28.0, "category": "Air Conditioners"},
    {"code": "84158210", "description": "Other air conditioning with refrigerating unit", "gst_rate": 28.0, "category": "Air Conditioners"},
    
    # Fans & Ventilation (8414)
    {"code": "84145100", "description": "Table, floor, wall, ceiling fans (motor ≤125W)", "gst_rate": 18.0, "category": "Fans"},
    {"code": "84145910", "description": "Ceiling fans", "gst_rate": 18.0, "category": "Fans"},
    {"code": "84145920", "description": "Pedestal fans", "gst_rate": 18.0, "category": "Fans"},
    {"code": "84145930", "description": "Exhaust fans", "gst_rate": 18.0, "category": "Fans"},
    {"code": "84146010", "description": "Kitchen hoods/chimneys (max dimension ≤120cm)", "gst_rate": 18.0, "category": "Chimneys"},
    {"code": "84146020", "description": "Kitchen hoods/chimneys (max dimension >120cm)", "gst_rate": 18.0, "category": "Chimneys"},
    
    # Air Purifiers (8421)
    {"code": "84213920", "description": "Air purifiers/cleaners", "gst_rate": 18.0, "category": "Air Purifiers"},
    
    # Vacuum Cleaners (8508)
    {"code": "85081100", "description": "Vacuum cleaners (≤1500W, dust bag/receptacle ≤20L)", "gst_rate": 18.0, "category": "Vacuum Cleaners"},
    {"code": "85081900", "description": "Other vacuum cleaners with self-contained motor", "gst_rate": 18.0, "category": "Vacuum Cleaners"},
    {"code": "85086000", "description": "Other vacuum cleaners", "gst_rate": 18.0, "category": "Vacuum Cleaners"},
    
    # Food Processors & Mixers (8509)
    {"code": "85094010", "description": "Food grinders/mixers/blenders (Mixer Grinder)", "gst_rate": 18.0, "category": "Mixers & Grinders"},
    {"code": "85094020", "description": "Juicers", "gst_rate": 18.0, "category": "Juicers"},
    {"code": "85094030", "description": "Food processors", "gst_rate": 18.0, "category": "Food Processors"},
    {"code": "85094090", "description": "Other food grinders and mixers", "gst_rate": 18.0, "category": "Mixers & Grinders"},
    
    # Coffee Machines (8516)
    {"code": "85167100", "description": "Coffee/tea makers - Electro-thermic", "gst_rate": 18.0, "category": "Coffee Machines"},
    {"code": "85167110", "description": "Coffee machines - Automatic", "gst_rate": 18.0, "category": "Coffee Machines"},
    {"code": "85167190", "description": "Other coffee/tea makers", "gst_rate": 18.0, "category": "Coffee Machines"},
    
    # Electric Kettles (8516)
    {"code": "85167200", "description": "Electric kettles", "gst_rate": 18.0, "category": "Kettles"},
    
    # Hair Dryers & Styling (8516)
    {"code": "85163100", "description": "Hair dryers - Electro-thermic", "gst_rate": 18.0, "category": "Personal Care"},
    {"code": "85163200", "description": "Other hair-dressing apparatus", "gst_rate": 18.0, "category": "Personal Care"},
    {"code": "85163300", "description": "Hand-drying apparatus", "gst_rate": 18.0, "category": "Personal Care"},
    
    # Electric Razors/Shavers (8510)
    {"code": "85101000", "description": "Shavers with self-contained electric motor", "gst_rate": 18.0, "category": "Personal Care"},
    {"code": "85102000", "description": "Hair clippers with self-contained motor", "gst_rate": 18.0, "category": "Personal Care"},
    
    # Gas Stoves & Hobs (7321)
    {"code": "73211100", "description": "Gas cooking appliances using gaseous fuel", "gst_rate": 18.0, "category": "Gas Hobs"},
    {"code": "73211900", "description": "Other cooking appliances using gaseous fuel", "gst_rate": 18.0, "category": "Gas Appliances"},
    {"code": "73218200", "description": "Cooking appliances using liquid fuel", "gst_rate": 18.0, "category": "Cooking Appliances"},
    
    # Induction Cooktops (8516)
    {"code": "85166000", "description": "Electric cooking appliances - Induction hobs", "gst_rate": 18.0, "category": "Induction Hobs"},
    {"code": "85166091", "description": "Induction cooktops - Single burner", "gst_rate": 18.0, "category": "Induction Hobs"},
    {"code": "85166092", "description": "Induction cooktops - Multi-burner", "gst_rate": 18.0, "category": "Induction Hobs"},
    
    # TV & Electronics (8528)
    {"code": "85287100", "description": "Television receivers (not designed with video display)", "gst_rate": 18.0, "category": "Television"},
    {"code": "85287200", "description": "Television receivers - Colour (LCD/LED)", "gst_rate": 18.0, "category": "Television"},
    {"code": "85287300", "description": "Television receivers - Black/white or monochrome", "gst_rate": 18.0, "category": "Television"},
    
    # Clothes Dryers (8451)
    {"code": "84512100", "description": "Drying machines (≤10kg dry linen capacity)", "gst_rate": 18.0, "category": "Dryers"},
    {"code": "84512900", "description": "Other drying machines", "gst_rate": 18.0, "category": "Dryers"},
    
    # Ironing Machines (8420)
    {"code": "84201000", "description": "Calendering/rolling machines (ironing)", "gst_rate": 18.0, "category": "Irons"},
    
    # Room Heaters (8516)
    {"code": "85162100", "description": "Electric storage heating radiators", "gst_rate": 18.0, "category": "Heaters"},
    {"code": "85162910", "description": "Room heaters - Convection type", "gst_rate": 18.0, "category": "Heaters"},
    {"code": "85162920", "description": "Room heaters - Fan type", "gst_rate": 18.0, "category": "Heaters"},
    {"code": "85162990", "description": "Other space heating apparatus", "gst_rate": 18.0, "category": "Heaters"},
    
    # Humidifiers & Dehumidifiers (8479)
    {"code": "84798910", "description": "Humidifiers", "gst_rate": 18.0, "category": "Humidifiers"},
    {"code": "84798920", "description": "Dehumidifiers", "gst_rate": 18.0, "category": "Dehumidifiers"},
    
    # Water Purifiers (8421)
    {"code": "84212110", "description": "Water purifiers - Domestic RO", "gst_rate": 18.0, "category": "Water Purifiers"},
    {"code": "84212190", "description": "Other water purifiers", "gst_rate": 18.0, "category": "Water Purifiers"},
    
    # Built-in Kitchen Equipment
    {"code": "84198990", "description": "Built-in ovens", "gst_rate": 18.0, "category": "Built-in Ovens"},
    {"code": "84178010", "description": "Industrial/Commercial ovens", "gst_rate": 18.0, "category": "Commercial Ovens"},
    
    # Small Kitchen Appliances
    {"code": "85168000", "description": "Electric heating resistors", "gst_rate": 18.0, "category": "Accessories"},
    {"code": "85167900", "description": "Other electro-thermic appliances", "gst_rate": 18.0, "category": "Small Appliances"},
    
    # Air Fryers
    {"code": "85166093", "description": "Air fryers - Electric", "gst_rate": 18.0, "category": "Air Fryers"},
    
    # Pressure Cookers
    {"code": "73239300", "description": "Pressure cookers - Stainless steel", "gst_rate": 12.0, "category": "Cookware"},
    {"code": "85166094", "description": "Electric pressure cookers", "gst_rate": 18.0, "category": "Electric Cookers"},
    
    # Rice Cookers
    {"code": "85167300", "description": "Rice cookers - Electric", "gst_rate": 18.0, "category": "Rice Cookers"},
    
    # Hand Blenders & Beaters
    {"code": "85094050", "description": "Hand blenders/immersion blenders", "gst_rate": 18.0, "category": "Blenders"},
    {"code": "85094060", "description": "Electric egg beaters/whisks", "gst_rate": 18.0, "category": "Beaters"},
    
    # Sandwich Makers & Grills
    {"code": "85166095", "description": "Sandwich makers/grills - Electric", "gst_rate": 18.0, "category": "Small Appliances"},
    
    # Electric Choppers
    {"code": "85094070", "description": "Electric food choppers", "gst_rate": 18.0, "category": "Choppers"},
    
    # Wet Grinders (South Indian)
    {"code": "84798100", "description": "Wet grinders - Electric", "gst_rate": 18.0, "category": "Wet Grinders"},
    
    # Idli/Dosa Makers
    {"code": "85166096", "description": "Idli makers/dosa makers - Electric", "gst_rate": 18.0, "category": "Small Appliances"},
    
    # Roti Makers
    {"code": "85166097", "description": "Roti makers/chapati makers - Electric", "gst_rate": 18.0, "category": "Small Appliances"},
    
    # Popcorn Makers
    {"code": "85166098", "description": "Popcorn makers - Electric", "gst_rate": 18.0, "category": "Small Appliances"},
    
    # Services (998)
    {"code": "998716", "description": "Installation services for machinery and equipment", "gst_rate": 18.0, "category": "Services"},
    {"code": "998719", "description": "Maintenance and repair services", "gst_rate": 18.0, "category": "Services"},
    {"code": "998732", "description": "Repair services for household appliances", "gst_rate": 18.0, "category": "Services"},
    
    # Transportation/Shipping (9965)
    {"code": "996511", "description": "Goods transport services - Road", "gst_rate": 5.0, "category": "Services"},
    {"code": "996521", "description": "Courier/express delivery services", "gst_rate": 18.0, "category": "Services"},
]

async def seed_hsn_codes():
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.environ.get("DB_NAME", "startup_template")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    created_count = 0
    skipped_count = 0
    
    print(f"🔄 Seeding HSN codes...")
    
    for hsn in HSN_CODES:
        # Check if already exists
        existing = await db.hsn_codes.find_one({"code": hsn["code"]})
        if existing:
            skipped_count += 1
            continue
        
        hsn_data = {
            "id": str(uuid.uuid4()),
            "code": hsn["code"],
            "description": hsn["description"],
            "gst_rate": hsn["gst_rate"],
            "category": hsn.get("category", "General"),
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.hsn_codes.insert_one(hsn_data)
        created_count += 1
    
    print(f"✅ Created {created_count} HSN codes, skipped {skipped_count} duplicates")
    
    # Verify count
    total = await db.hsn_codes.count_documents({})
    print(f"📊 Total HSN codes in database: {total}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_hsn_codes())
