# Seed Enhanced Product Catalog to MongoDB
import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from generate_product_catalog import generate_complete_catalog
from enhanced_products_data import ENHANCED_CATEGORIES, ENHANCED_BRANDS

# Add the current directory to Python path
sys.path.append('/app/backend')

load_dotenv()

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')

async def clear_existing_data():
    """Clear existing product data to avoid duplicates"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Clear existing collections
    await db.products.delete_many({})
    await db.categories.delete_many({})
    await db.brands.delete_many({})
    
    print("✅ Cleared existing product data")

async def seed_categories():
    """Seed enhanced categories"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Insert categories
    await db.categories.insert_many(ENHANCED_CATEGORIES)
    print(f"✅ Seeded {len(ENHANCED_CATEGORIES)} enhanced categories")

async def seed_brands():
    """Seed enhanced brands"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Insert brands
    await db.brands.insert_many(ENHANCED_BRANDS)
    print(f"✅ Seeded {len(ENHANCED_BRANDS)} enhanced brands")

async def seed_products():
    """Seed 100+ enhanced products"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Generate complete catalog
    print("Generating 100+ products...")
    products = generate_complete_catalog()
    
    # Convert products to MongoDB format (remove None values and ensure proper structure)
    mongo_products = []
    for product in products:
        mongo_product = {}
        for key, value in product.items():
            if value is not None:
                mongo_product[key] = value
        mongo_products.append(mongo_product)
    
    # Insert products in batches for better performance
    batch_size = 20
    for i in range(0, len(mongo_products), batch_size):
        batch = mongo_products[i:i + batch_size]
        await db.products.insert_many(batch)
        print(f"✅ Inserted batch {i//batch_size + 1}/{(len(mongo_products) + batch_size - 1)//batch_size}")
    
    print(f"✅ Successfully seeded {len(mongo_products)} enhanced products")
    
    # Print category distribution
    category_counts = {}
    for product in mongo_products:
        cat = product.get('subcategory', 'unknown')
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print("\n📊 Product Distribution by Category:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category.replace('_', ' ').title()}: {count} products")

async def create_enhanced_indexes():
    """Create indexes for better performance"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Enhanced indexes for better search and filtering
    single_indexes = [
        "category",
        "subcategory", 
        "brand",
        "brand_id",
        "price",
        "stock",
        "customer_rating",
        "fast_moving",
        "is_featured",
        "tags"
    ]
    
    # Create single field indexes
    for field in single_indexes:
        await db.products.create_index([(field, 1)])
    
    # Create text search index
    await db.products.create_index([
        ("name", "text"),
        ("description", "text"), 
        ("features", "text")
    ])
    
    print("✅ Created enhanced search indexes")

async def verify_seeding():
    """Verify that seeding was successful"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Check counts
    product_count = await db.products.count_documents({})
    category_count = await db.categories.count_documents({})
    brand_count = await db.brands.count_documents({})
    
    print(f"\n🔍 Database Verification:")
    print(f"  Products: {product_count}")
    print(f"  Categories: {category_count}")
    print(f"  Brands: {brand_count}")
    
    # Sample queries
    featured_products = await db.products.count_documents({"is_featured": True})
    premium_products = await db.products.count_documents({"tags": "premium"})
    out_of_stock = await db.products.count_documents({"stock": 0})
    
    print(f"\n📈 Product Analytics:")
    print(f"  Featured Products: {featured_products}")
    print(f"  Premium Products: {premium_products}")
    print(f"  Out of Stock: {out_of_stock}")
    print(f"  In Stock: {product_count - out_of_stock}")
    
    # Sample product
    sample_product = await db.products.find_one({"is_featured": True})
    if sample_product:
        print(f"\n🎯 Sample Featured Product:")
        print(f"  Name: {sample_product['name']}")
        print(f"  Brand: {sample_product['brand']}")
        print(f"  Price: ₹{sample_product['price']:,}")
        print(f"  Rating: {sample_product['customer_rating']}/5")
        print(f"  Stock: {sample_product['stock']}")

async def main():
    """Main seeding function"""
    print("🚀 Starting Enhanced Catalog Seeding...")
    print("=" * 50)
    
    try:
        # Step 1: Clear existing data
        await clear_existing_data()
        
        # Step 2: Seed categories
        await seed_categories()
        
        # Step 3: Seed brands
        await seed_brands()
        
        # Step 4: Seed products
        await seed_products()
        
        # Step 5: Create indexes
        await create_enhanced_indexes()
        
        # Step 6: Verify seeding
        await verify_seeding()
        
        print("\n🎉 Enhanced Catalog Seeding Complete!")
        print("The AI-powered e-commerce platform now has 100+ products with enhanced features.")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())