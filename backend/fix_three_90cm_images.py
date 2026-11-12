import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def fix_three_90cm_hob_images():
    """Fix image URLs for the 3 problematic 90cm gas hobs"""
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    products_collection = db.products
    
    # Correct image mappings from Bosch website
    image_updates = {
        "PNV9B6G20I": {
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/19898027_PNV9B6G20I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20631174_PNV9B6G20I_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20631177_PNV9B6G20I_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20788662_PNV9B6G20I_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20802340_PNV9B6G20I_PGA3_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/19898027_PNV9B6G20I_STP_def.webp"
        },
        "PNF9B6G20I": {
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/19898028_PNF9B6G20I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20631145_PNF9B6G20I_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20631150_PNF9B6G20I_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20788544_PNF9B6G20I_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20802273_PNF9B6G20I_PGA3_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/19898028_PNF9B6G20I_STP_def.webp"
        },
        "PNF9B6F20I": {
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/19898029_PNF9B6F20I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20630986_PNF9B6F20I_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20630994_PNF9B6F20I_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20788493_PNF9B6F20I_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20802231_PNF9B6F20I_PGA3_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/19898029_PNF9B6F20I_STP_def.webp"
        }
    }
    
    print("🔧 Fixing image URLs for 3 problematic 90cm gas hobs...\n")
    
    for model_number, image_data in image_updates.items():
        result = await products_collection.update_one(
            {"model_number": model_number},
            {"$set": {
                "images": image_data["images"],
                "thumbnail": image_data["thumbnail"]
            }}
        )
        
        if result.modified_count > 0:
            print(f"✅ Updated {model_number}")
            print(f"   Images: {len(image_data['images'])} URLs updated")
            print(f"   Thumbnail: {image_data['thumbnail']}")
        else:
            print(f"⚠️  {model_number} - No changes made (might already be correct)")
        print()
    
    print("✅ All image URLs updated successfully!")
    print("\nℹ️  Please refresh your browser (Ctrl+F5 or Cmd+Shift+R) to see the updated images.")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_three_90cm_hob_images())
