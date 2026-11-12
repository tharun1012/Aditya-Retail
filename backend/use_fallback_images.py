import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def use_fallback_chimney_images():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client['startup_template']
    
    print("=" * 80)
    print("USING FALLBACK CHIMNEY IMAGES (Generic Placeholders)")
    print("=" * 80)
    
    # Use generic chimney/kitchen hood images from reliable sources
    # These are publicly accessible images that won't be blocked
    fallback_images = {
        "LF91BUV50I": "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=600&h=600&fit=crop",  # Island hood
        "LI64MA531I": "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?w=600&h=600&fit=crop",  # Telescopic hood
        "LI97SA531I": "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?w=600&h=600&fit=crop",  # Telescopic hood
        "LC67BCP50I": "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=600&h=600&fit=crop",  # Wall mounted
        "LC91BUV50I": "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=600&h=600&fit=crop",  # Wall mounted
        "LC97BCP50I": "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=600&h=600&fit=crop",  # Wall mounted
        "LC97BIP50I": "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=600&h=600&fit=crop",  # Wall mounted
    }
    
    print("\n⚠️  Note: Using generic kitchen hood images as fallback")
    print("     Bosch CDN images are being blocked by CORS/Referrer policies")
    print("-" * 80)
    
    fixed_count = 0
    for model, image_url in fallback_images.items():
        result = await db.products.update_one(
            {"model_number": model},
            {"$set": {"image": image_url, "images": [image_url]}}
        )
        if result.matched_count > 0:
            fixed_count += 1
            product = await db.products.find_one({"model_number": model})
            print(f"  ✅ Updated: {model} - {product.get('name', 'N/A')[:50]}")
    
    print(f"\n✓ Updated {fixed_count} products with fallback images")
    
    print("\n" + "=" * 80)
    print("✅ FALLBACK IMAGES APPLIED!")
    print("=" * 80)
    print("\nRecommendation: To use actual product images, you may need to:")
    print("  1. Download images from Siemens website and host them locally")
    print("  2. Use an image proxy service to bypass CORS restrictions")
    print("  3. Contact Siemens for permission to use their CDN images")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(use_fallback_chimney_images())
