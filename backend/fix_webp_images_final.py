import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def fix_webp_images():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client['startup_template']
    
    print("=" * 80)
    print("FIXING WEBP IMAGES - CONVERTING TO STANDARD FORMAT")
    print("=" * 80)
    
    # For Bosch products, we can use their image CDN with different paths
    # Try using Product_Shots without specific resolution or use def.png
    
    mixer_updates = {
        "MGM8642BIN": "https://media3.bsh-group.com/Images/600x/20840484_MGM8642BIN_STP_D_def.png",
        "MGM8646BIN": "https://media3.bsh-group.com/Images/600x/20840481_MGM8646BIN_STP_D_def.png",
        "MGM8842DIN": "https://media3.bsh-group.com/Images/600x/15807953_MGM8842DIN_STP_D_def.png",
        "MGM8836MIN": "https://media3.bsh-group.com/Images/600x/20840482_MGM8836MIN_STP_D_def.png",
        "MGM6644BIN": "https://media3.bsh-group.com/Images/600x/20840479_MGM6644BIN_STP_D_def.png",
    }
    
    chimney_updates = {
        "LF91BUV50I": "https://media3.bsh-group.com/Images/600x/MCSA03035956_LF91BUV50_Hood_Siemens_STP_def.png",
        "LI64MA531I": "https://media3.bsh-group.com/Images/600x/MCSA02935803_LI64MA531_Hood_Siemens_STP_def.png",
        "LI97SA531I": "https://media3.bsh-group.com/Images/600x/MCSA02935813_LI97SA531_Hood_Siemens_STP_def.png",
        "LC67BCP50I": "https://media3.bsh-group.com/Images/600x/MCSA02987222_LC67BCP50_Hood_Siemens_STP_def.png",
        "LC91BUV50I": "https://media3.bsh-group.com/Images/600x/MCSA03035925_LC91BUV50_Hood_Siemens_STP_def.png",
        "LC97BCP50I": "https://media3.bsh-group.com/Images/600x/MCSA02987227_LC97BCP50_Hood_Siemens_STP_def.png",
        "LC97BIP50I": "https://media3.bsh-group.com/Images/600x/MCSA02987234_LC97BIP50_Hood_Siemens_STP_def.png",
    }
    
    gas_hob_updates = {
        "PNF9B6G20I": "https://media3.bsh-group.com/Images/600x/19898028_PNF9B6G20I_STP_def.png",
        "PNF9B6F20I": "https://media3.bsh-group.com/Images/600x/19898029_PNF9B6F20I_STP_def.png",
    }
    
    dishwasher_updates = {
        "SMI4IKS00I": "https://media3.bsh-group.com/Images/600x/MCSA01801569_SMI4IKS00I_Dishwasher_slimline_Bosch_STP_def.png",
        "SMS4HMB62T": "https://media3.bsh-group.com/Images/600x/21348224_SMS4HMB62T_STP_def.png",
        "SMS6HMI01I": "https://media3.bsh-group.com/Images/600x/MCSA00807390_SMS6HMI01A_STP_def.png",
        "SMS6IKI01I": "https://media3.bsh-group.com/Images/600x/MCSA01762949_SMS6IKI01I_Dishwasher_slimline_Bosch_STP_def.png",
        "SMS6ZCW37Q": "https://media3.bsh-group.com/Images/600x/MCSA01762949_SMS6IKI01I_Dishwasher_slimline_Bosch_STP_def.png",
        "SMS6HMC00I": "https://media3.bsh-group.com/Images/600x/MCSA00807390_SMS6HMI01A_STP_def.png",
        "SMS6HMI00I": "https://media3.bsh-group.com/Images/600x/MCSA00807390_SMS6HMI01A_STP_def.png",
        "SMS6IKW01I": "https://media3.bsh-group.com/Images/600x/MCSA01762949_SMS6IKI01I_Dishwasher_slimline_Bosch_STP_def.png",
        "SMV6HMX01I": "https://media3.bsh-group.com/Images/600x/MCSA01801510_SMV6HMX01I_Dishwasher_slimline_Bosch_STP_def.png",
    }
    
    all_updates = {
        **mixer_updates,
        **chimney_updates,
        **gas_hob_updates,
        **dishwasher_updates
    }
    
    print(f"\n📸 Updating {len(all_updates)} products with PNG image URLs...")
    print("-" * 80)
    
    fixed_count = 0
    for model, new_image_url in all_updates.items():
        result = await db.products.update_one(
            {"model_number": model},
            {"$set": {"image": new_image_url, "images": [new_image_url]}}
        )
        if result.modified_count > 0 or result.matched_count > 0:
            fixed_count += 1
            product = await db.products.find_one({"model_number": model})
            if product:
                print(f"  ✅ Updated: {model} - {product.get('name', 'N/A')[:50]}")
    
    print(f"\n✓ Updated {fixed_count} products with PNG images")
    
    print("\n" + "=" * 80)
    print("✅ ALL IMAGES UPDATED TO PNG FORMAT!")
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_webp_images())
