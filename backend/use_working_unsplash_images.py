import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Using JPG/PNG alternatives from Bosch CDN or retailer sites
WORKING_IMAGE_URLS = {
    # Gas Hobs - try different format
    "PNF9B6G20I": "https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=600&q=80",
    "PNF9B6F20I": "https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=600&q=80",
    
    # Dishwashers - use generic working images
    "SMI4IKS00I": "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?w=600&q=80",
    "SMS4HMB62T": "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?w=600&q=80",
    "SMS6HMI01I": "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?w=600&q=80",
    "SMS6IKI01I": "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?w=600&q=80",
    "SMS6ZCW37Q": "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?w=600&q=80",
    "SMS6HMC00I": "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?w=600&q=80",
    "SMS6HMI00I": "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?w=600&q=80",
    "SMS6IKW01I": "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?w=600&q=80",
    "SMV6HMX01I": "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?w=600&q=80",
    
    # Chimneys - use generic chimney images
    "LF91BUV50I": "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=600&q=80",
    "LI64MA531I": "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=600&q=80",
    "LI97SA531I": "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=600&q=80",
    "LC67BCP50I": "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=600&q=80",
    "LC91BUV50I": "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=600&q=80",
    "LC97BCP50I": "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=600&q=80",
    "LC97BIP50I": "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=600&q=80",
    
    # Mixer Grinders - use generic mixer images
    "MGM8642BIN": "https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=600&q=80",
    "MGM8646BIN": "https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=600&q=80",
    "MGM8842DIN": "https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=600&q=80",
    "MGM8836MIN": "https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=600&q=80",
    "MGM6644BIN": "https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=600&q=80",
}

async def use_working_images():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client['startup_template']
    
    print("=" * 80)
    print("USING WORKING IMAGE URLs (UNSPLASH - CORS-FREE)")
    print("=" * 80)
    print("\nNote: Using generic appliance images from Unsplash")
    print("      These are guaranteed to work but not product-specific")
    print("=" * 80)
    
    success = 0
    for model, url in WORKING_IMAGE_URLS.items():
        result = await db.products.update_one(
            {"model_number": model},
            {"$set": {"image": url, "images": [url]}}
        )
        if result.matched_count > 0:
            success += 1
            product = await db.products.find_one({"model_number": model})
            print(f"✅ {model}: {product.get('name', 'N/A')[:50]}")
    
    print(f"\n✓ Updated {success}/{len(WORKING_IMAGE_URLS)} products")
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(use_working_images())
