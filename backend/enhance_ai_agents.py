import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
import json

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
products_collection = db['products']

async def generate_product_knowledge_base():
    """Generate comprehensive product knowledge base for AI agents"""
    
    print("=" * 70)
    print("GENERATING AI AGENT PRODUCT KNOWLEDGE BASE")
    print("=" * 70)
    
    # Get all products
    all_products = []
    async for product in products_collection.find({}):
        all_products.append(product)
    
    # Organize by category
    products_by_category = {}
    for product in all_products:
        category = product['category']
        if category not in products_by_category:
            products_by_category[category] = []
        products_by_category[category].append(product)
    
    # Generate knowledge base text
    knowledge_base = []
    knowledge_base.append(f"\n## COMPLETE PRODUCT CATALOG ({len(all_products)} Products)\n")
    
    for category, products in sorted(products_by_category.items()):
        knowledge_base.append(f"\n### {category.upper()} ({len(products)} products):\n")
        
        for product in sorted(products, key=lambda x: x['price']):
            kb_entry = f"""
**{product['model_number']}** - {product['name']}
- Brand: {product['brand']}
- Price: ₹{product['price']:,.0f}
- Category: {product['category']} > {product.get('sub_category', 'N/A')}
- Description: {product.get('description', 'N/A')[:200]}
- Key Features: {', '.join(product.get('key_features', [])[:3])}
- Stock: {product.get('stock', 0)} units
- Rating: {product.get('rating', 0)}/5 ({product.get('reviews_count', 0)} reviews)
"""
            knowledge_base.append(kb_entry)
    
    # Save to file
    kb_text = '\n'.join(knowledge_base)
    
    with open('/app/backend/product_knowledge_base.txt', 'w') as f:
        f.write(kb_text)
    
    print(f"\n✅ Generated knowledge base with {len(all_products)} products")
    print(f"   Categories: {len(products_by_category)}")
    print(f"   File saved: /app/backend/product_knowledge_base.txt")
    print(f"   Size: {len(kb_text)} characters")
    
    # Generate summary stats
    stats = {
        'total_products': len(all_products),
        'categories': list(products_by_category.keys()),
        'brands': list(set([p['brand'] for p in all_products])),
        'price_range': {
            'min': min([p['price'] for p in all_products]),
            'max': max([p['price'] for p in all_products]),
            'avg': sum([p['price'] for p in all_products]) / len(all_products)
        }
    }
    
    print("\n" + "=" * 70)
    print("CATALOG STATISTICS:")
    print("=" * 70)
    print(f"Total Products: {stats['total_products']}")
    print(f"Categories: {', '.join(stats['categories'])}")
    print(f"Brands: {', '.join(stats['brands'])}")
    print(f"Price Range: ₹{stats['price_range']['min']:,.0f} - ₹{stats['price_range']['max']:,.0f}")
    print(f"Average Price: ₹{stats['price_range']['avg']:,.0f}")
    print("=" * 70)
    
    return kb_text

if __name__ == "__main__":
    asyncio.run(generate_product_knowledge_base())
