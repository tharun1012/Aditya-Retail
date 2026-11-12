import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def fix_90cm_hob_images():
    """Fix image URLs for 90cm gas hobs"""
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    products_collection = db.products
    
    # Updated image mappings with working URLs
    image_updates = {
        "PNF9B6F20I": {
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/19898032_PNF9B6F20I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790769_PNF9B6F20I_PGA5_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790772_PNF9B6F20I_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20807825_PNF9B6F20I_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01753946_PPQ7A6B90_GasHob_build-in_Bosch_PGA2_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/19898032_PNF9B6F20I_STP_def.webp"
        },
        "PNF9B6G20I": {
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/19898031_PNF9B6G20I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790658_PNF9B6G20I_PGA5_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790668_PNF9B6G20I_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790669_PNF9B6G20I_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20807797_PNF9B6G20I_PGA3_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/19898031_PNF9B6G20I_STP_def.webp"
        },
        "PNV9B6F20I": {
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/19898041_PNV9B6F20I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20630472_PNV9B6F20I_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20630481_PNV9B6F20I_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20791004_PNV9B6F20I_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20791087_PNV9B6F20I_PGA5_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/19898041_PNV9B6F20I_STP_def.webp"
        },
        "PNV9B6G20I": {
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/19898040_PNV9B6G20I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20630404_PNV9B6G20I_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20630411_PNV9B6G20I_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790869_PNV9B6G20I_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790878_PNV9B6G20I_PGA5_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/19898040_PNV9B6G20I_STP_def.webp"
        }
    }
    
    print("🔧 Fixing image URLs for 90cm gas hobs...\n")
    
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
            print(f"⚠️  {model_number} - No changes made")
        print()
    
    print("✅ Image URLs updated successfully!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_90cm_hob_images())
