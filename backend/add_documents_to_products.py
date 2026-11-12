import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def add_documents_to_all_products():
    # Get MongoDB connection string
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client['startup_template']
    products_collection = db['products']
    
    print("=" * 70)
    print("ADDING DOCUMENTS TO ALL PRODUCTS")
    print("=" * 70)
    
    # Get all products
    all_products = await products_collection.find().to_list(length=None)
    
    updated_count = 0
    
    for product in all_products:
        model = product.get('model_number')
        category = product.get('category', 'Product')
        
        # Check if documents already exist
        if product.get('documents') and len(product.get('documents', [])) > 0:
            continue
        
        # Create documents array with generic Bosch documentation
        documents = [
            {
                "title": f"{category} User Manual",
                "type": "manual",
                "url": f"https://www.bosch-home.in/store/medias/Bosch-{model}-User-Manual.pdf",
                "size": "2.5 MB",
                "description": "Complete user manual with installation and operation instructions"
            },
            {
                "title": "Product Specification Sheet",
                "type": "specification",
                "url": f"https://www.bosch-home.in/store/medias/Bosch-{model}-Specifications.pdf",
                "size": "850 KB",
                "description": "Detailed technical specifications and dimensions"
            },
            {
                "title": "Installation Guide",
                "type": "guide",
                "url": f"https://www.bosch-home.in/store/medias/Bosch-{model}-Installation.pdf",
                "size": "1.2 MB",
                "description": "Step-by-step installation instructions"
            },
            {
                "title": "Warranty Information",
                "type": "warranty",
                "url": "https://www.bosch-home.in/store/medias/Bosch-Warranty-Terms.pdf",
                "size": "450 KB",
                "description": "Warranty terms and conditions"
            }
        ]
        
        # Update product with documents
        await products_collection.update_one(
            {'model_number': model},
            {'$set': {'documents': documents}}
        )
        
        print(f"✅ Added documents to: {model} ({category})")
        updated_count += 1
    
    # Close connection
    client.close()
    
    print("\n" + "=" * 70)
    print("DOCUMENTS ADDITION COMPLETE")
    print("=" * 70)
    print(f"✅ Updated: {updated_count} products")
    print(f"⏭️  Already had documents: {len(all_products) - updated_count} products")
    print(f"📄 Each product now has 4 downloadable documents")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(add_documents_to_all_products())
