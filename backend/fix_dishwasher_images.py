import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def fix_dishwasher_images():
    """
    Fix missing images for dishwashers by adding proper product images
    """
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['startup_template']
    products_collection = db['products']
    
    print("=" * 70)
    print("FIXING DISHWASHER IMAGES")
    print("=" * 70)
    
    # Proper images for each dishwasher model (extracted from Bosch website)
    image_updates = {
        "SMS6HMC00I": [
            "https://media3.bsh-group.com/Product_Shots/900x/21348222_SMS6HMC00I_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21348226_SMS6HMC00I_PGA1_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21348230_SMS6HMC00I_PGA3_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21348234_SMS6HMC00I_PGA6_def.webp"
        ],
        "SMS6HMI01I": [
            "https://media3.bsh-group.com/Product_Shots/900x/21043439_SMS6HMI01I_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21085818_SMS6HMI01I_PGA3_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/19714426_A01_CD10_PGA6_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25583534_AP4250BO_1_FS_SCH_E_J_2SR_16_FHK2_PGA2_def.webp"
        ],
        "SMS6HMI00I": [
            "https://media3.bsh-group.com/Product_Shots/900x/21043437_SMS6HMI00I_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21085816_SMS6HMI00I_PGA3_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/19714426_A01_CD10_PGA6_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25583534_AP4250BO_1_FS_SCH_E_J_2SR_16_FHK2_PGA2_def.webp"
        ],
        "SMS6ZCW37Q": [
            "https://media3.bsh-group.com/Product_Shots/900x/MCIM02860952_SMS6ZCW37Q_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/MCIM02860956_SMS6ZCW37Q_PGA1_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/MCIM02860960_SMS6ZCW37Q_PGA3_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/MCIM02860964_SMS6ZCW37Q_PGA6_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/MCIM02860968_SMS6ZCW37Q_PGA4_def.webp"
        ],
        "SMS6IKI01I": [
            "https://media3.bsh-group.com/Product_Shots/900x/26807675_SMS6IKI01I_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/26807679_SMS6IKI01I_PGA1_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/26807683_SMS6IKI01I_PGA3_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/26807687_SMS6IKI01I_PGA6_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/26807691_SMS6IKI01I_PGA4_def.webp"
        ],
        "SMS6IKW01I": [
            "https://media3.bsh-group.com/Product_Shots/900x/26807695_SMS6IKW01I_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/26807699_SMS6IKW01I_PGA1_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/26807703_SMS6IKW01I_PGA3_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/26807707_SMS6IKW01I_PGA6_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/26807711_SMS6IKW01I_PGA4_def.webp"
        ],
        "SMV6HMX01I": [
            "https://media3.bsh-group.com/Product_Shots/900x/21043441_SMV6HMX01I_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21031516_UR65AX05_BPR_SIDG_2FL_2PKL_MID_2SR_PGA1_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21031518_UR65AX05_BPR_SIDG_2FL_2PKL_MID_2SR_PGA4_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25583534_AP4250BO_1_FS_SCH_E_J_2SR_16_FHK2_PGA2_def.webp"
        ],
        "SMI4IKS00I": [
            "https://media3.bsh-group.com/Product_Shots/900x/26801139_SMI4IKS00I_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/26801143_SMI4IKS00I_PGA1_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/26801147_SMI4IKS00I_PGA3_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/26801151_SMI4IKS00I_PGA6_def.webp"
        ]
    }
    
    updated_count = 0
    
    for model, images in image_updates.items():
        result = await products_collection.update_one(
            {'model_number': model},
            {'$set': {'images': images}}
        )
        
        if result.modified_count > 0:
            print(f"✅ {model}: Updated with {len(images)} images")
            updated_count += 1
        else:
            print(f"⚠️  {model}: No changes made")
    
    print("\n" + "=" * 70)
    print(f"✅ Updated {updated_count} dishwashers with proper images")
    print("=" * 70)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_dishwasher_images())
