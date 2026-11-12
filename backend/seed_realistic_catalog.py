# Seed Realistic Product Catalog for Aditya Retail
import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from realistic_product_catalog import generate_realistic_catalog, REALISTIC_BRANDS

# Add the current directory to Python path
sys.path.append('/app/backend')

load_dotenv()

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')

# Realistic Categories for your business
REALISTIC_CATEGORIES = [
    {
        "id": "appliances",
        "name": "Home Appliances", 
        "description": "Premium kitchen and home appliances from Bosch, Siemens, and Hindware",
        "icon": "Home",
        "subcategories": [
            {"id": "microwaves", "name": "Microwaves", "description": "Built-in and countertop microwaves"},
            {"id": "refrigerators", "name": "Refrigerators", "description": "Single door, double door, and side-by-side fridges"},
            {"id": "washing_machines", "name": "Washing Machines", "description": "Front load and top load washing machines"},
            {"id": "dishwashers", "name": "Dishwashers", "description": "Built-in and freestanding dishwashers"},
            {"id": "cooktops", "name": "Cooktops", "description": "Induction, gas, and electric cooktops"},
            {"id": "ovens", "name": "Ovens", "description": "Built-in and steam ovens"},
            {"id": "chimneys", "name": "Chimneys", "description": "Wall mount and island chimneys"}
        ]
    },
    {
        "id": "kitchen-bath",
        "name": "Kitchen & Bath",
        "description": "Premium sinks, faucets, and water heaters from Hindware",
        "icon": "Droplets",
        "subcategories": [
            {"id": "sinks", "name": "Kitchen Sinks", "description": "Stainless steel, granite, and designer sinks"},
            {"id": "faucets", "name": "Faucets", "description": "Kitchen and bathroom faucets and fittings"},
            {"id": "geysers", "name": "Water Heaters", "description": "Electric, gas, and solar water heaters"}
        ]
    },
    {
        "id": "power-tools", 
        "name": "Bosch Power Tools",
        "description": "Professional power tools for drilling, cutting, and measuring",
        "icon": "Wrench",
        "subcategories": [
            {"id": "drilling", "name": "Drilling Tools", "description": "Drill machines, impact drills, and hammer drills"},
            {"id": "cutting", "name": "Cutting Tools", "description": "Angle grinders, circular saws, and multi cutters"},
            {"id": "measuring", "name": "Measuring Tools", "description": "Laser measures and digital levels"}
        ]
    },
    {
        "id": "care-products",
        "name": "Bosch Care Products", 
        "description": "Professional detergents and cleaners for appliances",
        "icon": "Sparkles",
        "subcategories": [
            {"id": "detergents", "name": "Detergents", "description": "Washing machine and dishwasher detergents"},
            {"id": "cleaners", "name": "Cleaners", "description": "Drum cleaners, descaling agents, and appliance cleaners"}
        ]
    }
]

async def clear_existing_data():
    """Clear existing product data"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    await db.products.delete_many({})
    await db.categories.delete_many({})
    await db.brands.delete_many({})
    
    print("✅ Cleared existing product data")

async def seed_realistic_brands():
    """Seed realistic brands"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    brands = list(REALISTIC_BRANDS.values())
    await db.brands.insert_many(brands)
    print(f"✅ Seeded {len(brands)} realistic brands")

async def seed_realistic_categories():
    """Seed realistic categories"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    await db.categories.insert_many(REALISTIC_CATEGORIES)
    print(f"✅ Seeded {len(REALISTIC_CATEGORIES)} realistic categories")

async def seed_realistic_products():
    """Seed realistic products"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("Generating realistic product catalog...")
    products = generate_realistic_catalog()
    
    # Convert to MongoDB format
    mongo_products = []
    for product in products:
        mongo_product = {}
        for key, value in product.items():
            if value is not None:
                mongo_product[key] = value
        mongo_products.append(mongo_product)
    
    # Insert in batches
    batch_size = 15
    for i in range(0, len(mongo_products), batch_size):
        batch = mongo_products[i:i + batch_size]
        await db.products.insert_many(batch)
        print(f"✅ Inserted batch {i//batch_size + 1}/{(len(mongo_products) + batch_size - 1)//batch_size}")
    
    print(f"✅ Successfully seeded {len(mongo_products)} realistic products")
    
    # Show distribution
    brand_counts = {}
    category_counts = {}
    
    for product in mongo_products:
        brand = product.get('brand', 'Unknown')
        category = product.get('subcategory', 'unknown')
        
        brand_counts[brand] = brand_counts.get(brand, 0) + 1
        category_counts[category] = category_counts.get(category, 0) + 1
    
    print(f"\n📊 Brand Distribution:")
    for brand, count in sorted(brand_counts.items()):
        print(f"  {brand}: {count} products")
        
    print(f"\n📋 Category Distribution:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category.replace('_', ' ').title()}: {count} products")

async def create_realistic_indexes():
    """Create indexes for realistic catalog"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    indexes = [
        "category", "subcategory", "brand", "brand_id", "price", 
        "stock", "customer_rating", "fast_moving", "is_featured", "tags"
    ]
    
    for field in indexes:
        await db.products.create_index([(field, 1)])
    
    # Text search index
    await db.products.create_index([
        ("name", "text"),
        ("description", "text"),
        ("features", "text")
    ])
    
    print("✅ Created realistic catalog indexes")

async def verify_realistic_seeding():
    """Verify realistic catalog seeding"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Check counts
    product_count = await db.products.count_documents({})
    category_count = await db.categories.count_documents({})
    brand_count = await db.brands.count_documents({})
    
    print(f"\n🔍 Realistic Catalog Verification:")
    print(f"  Products: {product_count}")
    print(f"  Categories: {category_count}")
    print(f"  Brands: {brand_count}")
    
    # Check each brand
    for brand_id in ["bosch", "siemens", "hindware"]:
        count = await db.products.count_documents({"brand_id": brand_id})
        print(f"  {brand_id.title()}: {count} products")
    
    # Sample products from each brand
    print(f"\n🎯 Sample Products:")
    
    for brand_id in ["bosch", "siemens", "hindware"]:
        sample = await db.products.find_one({"brand_id": brand_id})
        if sample:
            print(f"  {sample['brand']}: {sample['name']} - ₹{sample['price']:,}")
    
    # Check categories
    appliance_count = await db.products.count_documents({"subcategory": {"$in": ["microwaves", "refrigerators", "washing_machines"]}})
    tools_count = await db.products.count_documents({"subcategory": {"$in": ["drilling", "cutting"]}})
    care_count = await db.products.count_documents({"subcategory": {"$in": ["detergents", "cleaners"]}})
    
    print(f"\n📈 Product Type Analytics:")
    print(f"  Appliances: {appliance_count}")
    print(f"  Power Tools: {tools_count}")
    print(f"  Care Products: {care_count}")

async def main():
    """Main realistic catalog seeding"""
    print("🏭 Starting Realistic Aditya Retail Catalog Seeding...")
    print("=" * 60)
    
    try:
        await clear_existing_data()
        await seed_realistic_brands()
        await seed_realistic_categories()
        await seed_realistic_products()
        await create_realistic_indexes()
        await verify_realistic_seeding()
        
        print("\n🎉 Realistic Catalog Seeding Complete!")
        print("Your Aditya Retail platform now has products from:")
        print("  • Bosch (Appliances + Power Tools + Care Products)")
        print("  • Siemens (Premium Appliances)")
        print("  • Hindware (Appliances + Sinks + Faucets + Geysers)")
        
    except Exception as e:
        print(f"❌ Error during realistic catalog seeding: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())