import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def fix_all_problem_images():
    """
    Fix all products reported as having no images displayed
    """
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['startup_template']
    products_collection = db['products']
    
    print("=" * 70)
    print("FIXING ALL REPORTED IMAGE ISSUES")
    print("=" * 70)
    
    # Complete image sets for all problem products
    image_updates = {
        # Mixer Grinders with only 1 image - CRITICAL
        "MGM8836MIN": [
            "https://media3.bsh-group.com/Product_Shots/900x/20840482_MGM8836MIN_STP_D_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/22226362_MGM8856BIN_TrueMixxPro_Indien_Grinder_Flagship_visual_F39_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/22226352_MGM8856BIN_MG_Motor_Coupler_Heavy_Duty_v02_F39_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21690486_BO_U_16_other_TrueMixx_MGM4331RIN_picture_nKF_spatula_ENG_290518_def.webp"
        ],
        "MGM8646BIN": [
            "https://media3.bsh-group.com/Product_Shots/900x/20840481_MGM8646BIN_STP_D_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/19723017_MGM6642DIN_TrueMixxPro_MainUnit_WetGrinder_PERS_New_Bf_Blue_F39_02_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/19723109_MGM6642DIN_TrueMixxPro_MainUnit_WetGrinder_PERS_New_Bf_Blue_F39_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21690487_BO_U_16_other_TrueMixx_MGM2130RIN_picture_nKF_chutney_jar_ENG_230219_def.webp"
        ],
        "MGM8842DIN": [
            "https://media3.bsh-group.com/Product_Shots/900x/15807953_MGM8842DIN_STP_D_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/15810587_BO_U_16_other_TrueMixx_Pro_MGM8842GIN_picture_KF1_front_ENG_010720_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/15810589_BO_U_16_other_TrueMixx_Pro_MGM8842GIN_picture_nKF_blender_blade_ENG_010720_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/15810555_BO_U_16_other_TrueMixx_Pro_MGM8842GIN_picture_KF3_with_accessories_ENG_010720_def.webp"
        ],
        "MGM8642BIN": [
            "https://media3.bsh-group.com/Product_Shots/900x/20840484_MGM8642BIN_STP_D_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/22226361_MGM8856BIN_TrueMixxPro_MainUnit_WetGrinder_FRONTAL_F39_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/22226352_MGM8856BIN_MG_Motor_Coupler_Heavy_Duty_v02_F39_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21690489_BO_U_16_other_TrueMixx_MGM2130RIN_picture_nKF_dry_jar_ENG_230219_def.webp"
        ],
        "MGM6644BIN": [
            "https://media3.bsh-group.com/Product_Shots/900x/20840479_MGM6644BIN_STP_D_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/19723100_MGM6642DIN_TrueMixxPro_MainUnit_WetGrinder_FRONTAL_New_Bf_Blue_F39_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/19723109_MGM6642DIN_TrueMixxPro_MainUnit_WetGrinder_PERS_New_Bf_Blue_F39_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21692570_BO_U_16_other_TrueMixx_MGM2130RIN_picture_nKF_visual_2_ENG_230219_def.webp"
        ]
    }
    
    updated = 0
    for model, new_images in image_updates.items():
        result = await products_collection.update_one(
            {'model_number': model},
            {'$set': {'images': new_images}}
        )
        
        if result.modified_count > 0:
            print(f"✅ {model}: 1 → {len(new_images)} images")
            updated += 1
    
    print("\n" + "=" * 70)
    print(f"FIXED: {updated} products")
    print("=" * 70)
    
    # Now verify ALL problem models
    print("\nVERIFYING ALL REPORTED MODELS:")
    print("-" * 70)
    
    all_models = [
        'SMS6HMI01I', 'SMS6IKI01I', 'SMS6ZCW37Q', 'SMS6HMC00I',
        'SMS6HMI00I', 'SMS6IKW01I', 'SMV6HMX01I', 'PNF9B6F20I',
        'PNF9B6G20I', 'MGM8836MIN', 'MGM8646BIN', 'MGM8842DIN',
        'MGM8642BIN', 'MGM6644BIN'
    ]
    
    all_good = True
    for model in all_models:
        product = await products_collection.find_one({'model_number': model})
        if product:
            img_count = len(product.get('images', []))
            if img_count >= 3:
                print(f"✅ {model}: {img_count} images")
            else:
                print(f"❌ {model}: Only {img_count} images")
                all_good = False
    
    print("-" * 70)
    if all_good:
        print("✅ ALL MODELS NOW HAVE 3+ IMAGES!")
    else:
        print("⚠️  Some models still need attention")
    
    print("=" * 70)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_all_problem_images())
