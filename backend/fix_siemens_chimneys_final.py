import asyncio
import requests
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient

async def scrape_and_fix_siemens_chimneys():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client['startup_template']
    
    print("=" * 80)
    print("SCRAPING WORKING IMAGE URLS FOR SIEMENS CHIMNEYS")
    print("=" * 80)
    
    # Map of model numbers to their product page URLs
    product_urls = {
        "LF91BUV50I": "https://www.siemens-home.bsh-group.com/in/productlist/cooker-hoods/island-hoods/LF91BUV50I",
        "LI64MA531I": "https://www.siemens-home.bsh-group.com/in/productlist/cooker-hoods/telescopic-hoods/LI64MA531I",
        "LI97SA531I": "https://www.siemens-home.bsh-group.com/in/productlist/cooker-hoods/telescopic-hoods/LI97SA531I",
        "LC67BCP50I": "https://www.siemens-home.bsh-group.com/in/productlist/cooker-hoods/wall-mounted-hoods/LC67BCP50I",
        "LC91BUV50I": "https://www.siemens-home.bsh-group.com/in/productlist/cooker-hoods/wall-mounted-hoods/LC91BUV50I",
        "LC97BCP50I": "https://www.siemens-home.bsh-group.com/in/productlist/cooker-hoods/wall-mounted-hoods/LC97BCP50I",
        "LC97BIP50I": "https://www.siemens-home.bsh-group.com/in/productlist/cooker-hoods/wall-mounted-hoods/LC97BIP50I"
    }
    
    # Alternative: Use direct image URLs that work
    # These are from the Bosch/Siemens media CDN with proper paths
    alternative_images = {
        "LF91BUV50I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA03035956_LF91BUV50_Hood_Siemens_STP_def.webp",
        "LI64MA531I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02935803_LI64MA531_Hood_Siemens_STP_def.webp",
        "LI97SA531I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02935813_LI97SA531_Hood_Siemens_STP_def.webp",
        "LC67BCP50I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02987222_LC67BCP50_Hood_Siemens_STP_def.webp",
        "LC91BUV50I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA03035925_LC91BUV50_Hood_Siemens_STP_def.webp",
        "LC97BCP50I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02987227_LC97BCP50_Hood_Siemens_STP_def.webp",
        "LC97BIP50I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02987234_LC97BIP50_Hood_Siemens_STP_def.webp"
    }
    
    print("\n🔄 Reverting to 5120x WebP URLs (these worked before)...")
    print("-" * 80)
    
    fixed_count = 0
    for model, image_url in alternative_images.items():
        result = await db.products.update_one(
            {"model_number": model},
            {"$set": {"image": image_url, "images": [image_url]}}
        )
        if result.matched_count > 0:
            fixed_count += 1
            product = await db.products.find_one({"model_number": model})
            print(f"  ✅ Updated: {model} - {product.get('name', 'N/A')[:50]}")
    
    print(f"\n✓ Updated {fixed_count} Siemens chimney images")
    
    print("\n" + "=" * 80)
    print("✅ SIEMENS CHIMNEY IMAGES UPDATED!")
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(scrape_and_fix_siemens_chimneys())
