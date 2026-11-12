import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import time

# Use exact same format as working products with cache buster
cache_buster = f"?v={int(time.time())}"

PRODUCT_IMAGES_FINAL = {
    "PNF9B6G20I": f"https://media3.bsh-group.com/Product_Shots/5120x/19898051_PNF9B6G20I_STP_def.webp{cache_buster}",
    "PNF9B6F20I": f"https://media3.bsh-group.com/Product_Shots/5120x/19898029_PNF9B6F20I_STP_def.webp{cache_buster}",
    "SMI4IKS00I": f"https://media3.bsh-group.com/Product_Shots/5120x/MCSA01801569_SMI4IKS00I_Dishwasher_slimline_Bosch_STP_def.webp{cache_buster}",
    "SMS4HMB62T": f"https://media3.bsh-group.com/Product_Shots/5120x/21348224_SMS4HMB62T_STP_def.webp{cache_buster}",
    "SMS6HMI01I": f"https://media3.bsh-group.com/Product_Shots/5120x/MCSA00807390_SMS6HMI01A_STP_def.webp{cache_buster}",
    "SMS6IKI01I": f"https://media3.bsh-group.com/Product_Shots/5120x/MCSA01762949_SMS6IKI01I_Dishwasher_slimline_Bosch_STP_def.webp{cache_buster}",
    "SMS6ZCW37Q": f"https://media3.bsh-group.com/Product_Shots/5120x/MCSA01762949_SMS6IKI01I_Dishwasher_slimline_Bosch_STP_def.webp{cache_buster}",
    "SMS6HMC00I": f"https://media3.bsh-group.com/Product_Shots/5120x/MCSA00807390_SMS6HMI01A_STP_def.webp{cache_buster}",
    "SMS6HMI00I": f"https://media3.bsh-group.com/Product_Shots/5120x/MCSA00807390_SMS6HMI01A_STP_def.webp{cache_buster}",
    "SMS6IKW01I": f"https://media3.bsh-group.com/Product_Shots/5120x/MCSA01762949_SMS6IKI01I_Dishwasher_slimline_Bosch_STP_def.webp{cache_buster}",
    "SMV6HMX01I": f"https://media3.bsh-group.com/Product_Shots/5120x/MCSA01801510_SMV6HMX01I_Dishwasher_slimline_Bosch_STP_def.webp{cache_buster}",
    "LF91BUV50I": f"https://media3.bsh-group.com/Product_Shots/5120x/MCSA03035956_LF91BUV50_Hood_Siemens_STP_def.webp{cache_buster}",
    "LI64MA531I": f"https://media3.bsh-group.com/Product_Shots/5120x/MCSA02935803_LI64MA531_Hood_Siemens_STP_def.webp{cache_buster}",
    "LI97SA531I": f"https://media3.bsh-group.com/Product_Shots/5120x/MCSA02935813_LI97SA531_Hood_Siemens_STP_def.webp{cache_buster}",
    "LC67BCP50I": f"https://media3.bsh-group.com/Product_Shots/5120x/MCSA02987222_LC67BCP50_Hood_Siemens_STP_def.webp{cache_buster}",
    "LC91BUV50I": f"https://media3.bsh-group.com/Product_Shots/5120x/MCSA03035925_LC91BUV50_Hood_Siemens_STP_def.webp{cache_buster}",
    "LC97BCP50I": f"https://media3.bsh-group.com/Product_Shots/5120x/MCSA02987227_LC97BCP50_Hood_Siemens_STP_def.webp{cache_buster}",
    "LC97BIP50I": f"https://media3.bsh-group.com/Product_Shots/5120x/MCSA02987234_LC97BIP50_Hood_Siemens_STP_def.webp{cache_buster}",
    "MGM8642BIN": f"https://media3.bsh-group.com/Product_Shots/5120x/20840484_MGM8642BIN_STP_D_def.webp{cache_buster}",
    "MGM8646BIN": f"https://media3.bsh-group.com/Product_Shots/5120x/20840481_MGM8646BIN_STP_D_def.webp{cache_buster}",
    "MGM8842DIN": f"https://media3.bsh-group.com/Product_Shots/5120x/15807953_MGM8842DIN_STP_D_def.webp{cache_buster}",
    "MGM8836MIN": f"https://media3.bsh-group.com/Product_Shots/5120x/20840482_MGM8836MIN_STP_D_def.webp{cache_buster}",
    "MGM6644BIN": f"https://media3.bsh-group.com/Product_Shots/5120x/20840479_MGM6644BIN_STP_D_def.webp{cache_buster}",
}

async def update_with_cache_buster():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client['startup_template']
    
    print("=" * 80)
    print("UPDATING WITH CACHE-BUSTING URLs")
    print(f"Cache buster: {cache_buster}")
    print("=" * 80)
    
    for model, url in PRODUCT_IMAGES_FINAL.items():
        result = await db.products.update_one(
            {"model_number": model},
            {"$set": {"image": url, "images": [url]}}
        )
        if result.matched_count > 0:
            print(f"✅ {model}")
    
    print(f"\n✓ Updated {len(PRODUCT_IMAGES_FINAL)} products")
    print("=" * 80)
    
    client.close()

asyncio.run(update_with_cache_buster())
