import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def manage_categories():
    """
    Utility script to manage product categories
    """
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['startup_template']
    products_collection = db['products']
    
    print("=" * 70)
    print("PRODUCT CATEGORY MANAGEMENT")
    print("=" * 70)
    
    while True:
        print("\nOptions:")
        print("1. View all categories and counts")
        print("2. View uncategorized products")
        print("3. Move product to category")
        print("4. Bulk move products to category")
        print("5. List products by category")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ")
        
        if choice == "1":
            # View all categories
            pipeline = [
                {'$group': {
                    '_id': '$category',
                    'count': {'$sum': 1}
                }},
                {'$sort': {'_id': 1}}
            ]
            categories = await products_collection.aggregate(pipeline).to_list(length=None)
            
            print("\n" + "=" * 70)
            print("CATEGORIES AND COUNTS")
            print("=" * 70)
            for cat in categories:
                print(f"  {cat['_id']}: {cat['count']} products")
            
        elif choice == "2":
            # View uncategorized products
            uncategorized = await products_collection.find({
                '$or': [
                    {'category': 'Uncategorized'},
                    {'category': 'Product'},
                    {'category': {'$exists': False}}
                ]
            }).to_list(length=None)
            
            print("\n" + "=" * 70)
            print(f"UNCATEGORIZED PRODUCTS ({len(uncategorized)})")
            print("=" * 70)
            
            for i, prod in enumerate(uncategorized, 1):
                print(f"{i}. {prod.get('model_number')}: {prod.get('name')}")
            
        elif choice == "3":
            # Move single product
            model = input("\nEnter model number: ").strip()
            new_category = input("Enter new category: ").strip()
            
            result = await products_collection.update_one(
                {'model_number': model},
                {'$set': {'category': new_category}}
            )
            
            if result.modified_count > 0:
                print(f"✅ Moved {model} to {new_category}")
            else:
                print(f"❌ Product {model} not found")
        
        elif choice == "4":
            # Bulk move
            print("\nAvailable categories:")
            print("- Chimney")
            print("- Gas Hob")
            print("- Induction Hob")
            print("- Mixer Grinder")
            print("- Washing Machine")
            print("- Oven")
            print("- Refrigerator")
            print("- Dishwasher")
            
            new_category = input("\nEnter target category: ").strip()
            models = input("Enter model numbers (comma-separated): ").strip()
            model_list = [m.strip() for m in models.split(',')]
            
            updated = 0
            for model in model_list:
                result = await products_collection.update_one(
                    {'model_number': model},
                    {'$set': {'category': new_category}}
                )
                updated += result.modified_count
            
            print(f"✅ Updated {updated} products to {new_category}")
        
        elif choice == "5":
            # List by category
            category = input("\nEnter category name: ").strip()
            products = await products_collection.find({'category': category}).to_list(length=None)
            
            print("\n" + "=" * 70)
            print(f"{category.upper()} PRODUCTS ({len(products)})")
            print("=" * 70)
            
            for i, prod in enumerate(products, 1):
                print(f"{i}. {prod.get('model_number')}: {prod.get('name')} - ₹{prod.get('price'):,.0f}")
        
        elif choice == "6":
            print("\nExiting...")
            break
        
        else:
            print("Invalid choice!")
    
    client.close()

if __name__ == "__main__":
    print("\n🔧 Product Category Management Tool")
    print("This tool helps you organize products into categories\n")
    asyncio.run(manage_categories())
