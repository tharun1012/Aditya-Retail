import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Scraped working image URLs from Bosch and Siemens product pages
PRODUCT_IMAGE_MAP = {
    # Gas Hobs
    "PNF9B6G20I": "https://media3.bsh-group.com/Product_Shots/5120x/19898051_PNF9B6G20I_STP_def.webp",
    "PNF9B6F20I": "https://media3.bsh-group.com/Product_Shots/5120x/19898029_PNF9B6F20I_STP_def.webp",
    
    # Dishwashers - Will scrape these next
    "SMI4IKS00I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01801569_SMI4IKS00I_Dishwasher_slimline_Bosch_STP_def.webp",
    "SMS4HMB62T": "https://media3.bsh-group.com/Product_Shots/5120x/21348224_SMS4HMB62T_STP_def.webp",
    "SMS6HMI01I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA00807390_SMS6HMI01A_STP_def.webp",
    "SMS6IKI01I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01762949_SMS6IKI01I_Dishwasher_slimline_Bosch_STP_def.webp",
    "SMS6ZCW37Q": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01762949_SMS6IKI01I_Dishwasher_slimline_Bosch_STP_def.webp",
    "SMS6HMC00I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA00807390_SMS6HMI01A_STP_def.webp",
    "SMS6HMI00I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA00807390_SMS6HMI01A_STP_def.webp",
    "SMS6IKW01I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01762949_SMS6IKI01I_Dishwasher_slimline_Bosch_STP_def.webp",
    "SMV6HMX01I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01801510_SMV6HMX01I_Dishwasher_slimline_Bosch_STP_def.webp",
    
    # Chimneys - Will scrape these
    "LF91BUV50I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA03035956_LF91BUV50_Hood_Siemens_STP_def.webp",
    "LI64MA531I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02935803_LI64MA531_Hood_Siemens_STP_def.webp",
    "LI97SA531I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02935813_LI97SA531_Hood_Siemens_STP_def.webp",
    "LC67BCP50I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02987222_LC67BCP50_Hood_Siemens_STP_def.webp",
    "LC91BUV50I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA03035925_LC91BUV50_Hood_Siemens_STP_def.webp",
    "LC97BCP50I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02987227_LC97BCP50_Hood_Siemens_STP_def.webp",
    "LC97BIP50I": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02987234_LC97BIP50_Hood_Siemens_STP_def.webp",
    
    # Mixer Grinders
    "MGM8642BIN": "https://media3.bsh-group.com/Product_Shots/5120x/20840484_MGM8642BIN_STP_D_def.webp",
    "MGM8646BIN": "https://media3.bsh-group.com/Product_Shots/5120x/20840481_MGM8646BIN_STP_D_def.webp",
    "MGM8842DIN": "https://media3.bsh-group.com/Product_Shots/5120x/15807953_MGM8842DIN_STP_D_def.webp",
    "MGM8836MIN": "https://media3.bsh-group.com/Product_Shots/5120x/20840482_MGM8836MIN_STP_D_def.webp",
    "MGM6644BIN": "https://media3.bsh-group.com/Product_Shots/5120x/20840479_MGM6644BIN_STP_D_def.webp",
}

async def update_product_images():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client['startup_template']
    
    print("=" * 80)
    print("UPDATING PRODUCT IMAGES WITH SCRAPED URLs")
    print("=" * 80)
    
    success_count = 0
    failed_count = 0
    
    for model_number, image_url in PRODUCT_IMAGE_MAP.items():
        try:
            result = await db.products.update_one(
                {"model_number": model_number},
                {"$set": {"image": image_url, "images": [image_url]}}
            )
            
            if result.matched_count > 0:
                success_count += 1
                product = await db.products.find_one({"model_number": model_number})
                if product:
                    print(f"✅ {model_number}: {product.get('name', 'N/A')[:50]}")
                else:
                    print(f"✅ {model_number}: Updated")
            else:
                failed_count += 1
                print(f"❌ {model_number}: NOT FOUND IN DATABASE")
        except Exception as e:
            failed_count += 1
            print(f"❌ {model_number}: ERROR - {str(e)}")
    
    print("\n" + "=" * 80)
    print(f"📊 SUMMARY")
    print("=" * 80)
    print(f"Successfully updated: {success_count} products")
    print(f"Failed: {failed_count} products")
    print(f"Total processed: {len(PRODUCT_IMAGE_MAP)} products")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(update_product_images())
