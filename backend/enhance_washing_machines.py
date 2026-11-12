import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def enhance_washing_machines():
    # Get MongoDB connection string
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client['startup_template']
    products_collection = db['products']
    
    print("=" * 70)
    print("ENHANCING WASHING MACHINES WITH COMPLETE DETAILS")
    print("=" * 70)
    
    # Enhanced data for WGA2420SIN
    update_wga2420 = {
        "key_features": [
            "9 kg loading capacity - perfect for medium-sized families",
            "1200 rpm maximum spin speed for faster drying",
            "AntiWrinkle technology - minimizes wrinkles by up to 50%",
            "AutoStain Removal - removes blood, butter/oil, grass, and red wine stains",
            "SpeedPerfect™ - up to 65% time saving on washing",
            "EcoSilence Drive™ - efficient, silent, and durable motor",
            "VarioPerfect™ - choose between time or energy saving",
            "ActiveWater Plus - optimizes water usage",
            "Multiple specialized wash programs",
            "LED display for easy operation",
            "Reload function to add forgotten items",
            "Child lock for safety",
            "Free delivery and installation",
            "2 years comprehensive warranty"
        ],
        "specifications": {
            "Type": "Front Load Washing Machine",
            "Series": "Series 6",
            "Load Capacity": "9 kg",
            "Maximum Spin Speed": "1200 rpm",
            "Energy Rating": "5 Star",
            "Water Consumption": "48 liters per wash",
            "EcoSilence Drive": "Yes",
            "VarioPerfect": "Yes",
            "SpeedPerfect": "Yes",
            "AntiWrinkle": "Yes",
            "AutoStain Removal": "4 stain types",
            "Home Connect": "No",
            "i-DOS Automatic Dosing": "No",
            "Display Type": "LED",
            "Color": "Graphite",
            "Dimensions (W x H x D)": "598 x 848 x 590 mm",
            "Net Weight": "70 kg",
            "Door Opening": "180 degrees",
            "Number of Programs": "15+",
            "Noise Level (Wash)": "48 dB",
            "Noise Level (Spin)": "72 dB",
            "Warranty": "2 years on product, 10 years on motor"
        },
        "long_description": "The Bosch Series 6 WGA2420SIN Front Load Washing Machine redefines laundry care with its intelligent features and advanced technology. With a generous 9 kg capacity and powerful 1200 rpm spin speed, it handles medium to large loads effortlessly. The revolutionary AntiWrinkle technology reduces wrinkles by up to 50%, making ironing easier and protecting your fabrics. AutoStain Removal technology automatically adjusts wash parameters to remove 4 common stubborn stains - blood, butter/oil, grass, and red wine - without any pre-treatment. The SpeedPerfect™ option delivers impeccable cleaning results in up to 65% less time, perfect for busy households. EcoSilence Drive™ motor ensures whisper-quiet operation while delivering exceptional performance and durability. VarioPerfect™ gives you the flexibility to choose between saving time or energy based on your needs. With ActiveWater Plus technology, the machine optimizes water usage for each load size, making it both economical and environmentally friendly. The sleek graphite finish and intuitive LED display add a touch of sophistication to your laundry room."
    }
    
    # Enhanced data for WGA254ZPIN
    update_wga254 = {
        "key_features": [
            "10 kg loading capacity - ideal for large families",
            "1400 rpm maximum spin speed for superior drying",
            "EcoSilence Drive™ - efficient, silent, and durable motor",
            "VarioPerfect™ - flexible time or energy saving options",
            "ActiveWater Plus - intelligent water management",
            "SpeedPerfect™ - faster washing without compromising quality",
            "Multiple specialized wash programs including Sportswear",
            "AllergyPlus program for sensitive skin",
            "Reload function for convenience",
            "LED display with touch controls",
            "Elegant blue color finish",
            "Child lock for safety",
            "Self-cleaning detergent drawer",
            "Free delivery and installation",
            "2 years comprehensive warranty with 10 years motor warranty"
        ],
        "specifications": {
            "Type": "Front Load Washing Machine",
            "Series": "Series 6",
            "Load Capacity": "10 kg",
            "Maximum Spin Speed": "1400 rpm",
            "Energy Rating": "5 Star",
            "Water Consumption": "52 liters per wash",
            "EcoSilence Drive": "Yes",
            "VarioPerfect": "Yes",
            "SpeedPerfect": "Yes",
            "AllergyPlus": "Yes",
            "Home Connect": "No",
            "i-DOS Automatic Dosing": "No",
            "Display Type": "LED with Touch Control",
            "Color": "Blue",
            "Dimensions (W x H x D)": "598 x 848 x 590 mm",
            "Net Weight": "74 kg",
            "Door Opening": "180 degrees",
            "Number of Programs": "15+",
            "Special Programs": "Sportswear, AllergyPlus, Quick Wash",
            "Noise Level (Wash)": "47 dB",
            "Noise Level (Spin)": "71 dB",
            "Drum Volume": "65 liters",
            "Warranty": "2 years on product, 10 years on motor"
        },
        "long_description": "The Bosch Series 6 WGA254ZPIN Front Load Washing Machine is engineered for large families who demand superior performance and efficiency. With an impressive 10 kg capacity and high-speed 1400 rpm spin, it tackles substantial loads while ensuring clothes come out nearly dry, reducing drying time significantly. The powerful yet whisper-quiet EcoSilence Drive™ motor delivers exceptional washing performance while consuming minimal energy. VarioPerfect™ technology offers the flexibility to prioritize either time or energy savings based on your daily needs. ActiveWater Plus intelligently adjusts water consumption according to load size, making every wash economical and eco-friendly. The AllergyPlus program is specially designed for sensitive skin, using higher temperatures and extended rinse cycles to remove allergens effectively. SpeedPerfect™ reduces wash time by up to 65% without compromising cleaning quality - perfect for busy households. The elegant blue finish adds a modern aesthetic to any laundry space, while the intuitive LED touch control display makes operation effortless. With specialized programs for sportswear, delicates, and quick washes, this washing machine adapts to all your laundry needs. The self-cleaning detergent drawer and reload function add convenience to your daily routine."
    }
    
    # Update WGA2420SIN
    result1 = await products_collection.update_one(
        {'model_number': 'WGA2420SIN'},
        {'$set': update_wga2420}
    )
    
    print(f"\n✅ Updated WGA2420SIN (9 kg)")
    print(f"   Key Features: {len(update_wga2420['key_features'])} features")
    print(f"   Specifications: {len(update_wga2420['specifications'])} specs")
    print(f"   Long Description: Enhanced with detailed information")
    
    # Update WGA254ZPIN
    result2 = await products_collection.update_one(
        {'model_number': 'WGA254ZPIN'},
        {'$set': update_wga254}
    )
    
    print(f"\n✅ Updated WGA254ZPIN (10 kg)")
    print(f"   Key Features: {len(update_wga254['key_features'])} features")
    print(f"   Specifications: {len(update_wga254['specifications'])} specs")
    print(f"   Long Description: Enhanced with detailed information")
    
    # Close connection
    client.close()
    
    print("\n" + "=" * 70)
    print("ENHANCEMENT COMPLETE")
    print("=" * 70)
    print(f"✅ Both washing machines now have:")
    print(f"   • Comprehensive key features (14-15 features)")
    print(f"   • Detailed specifications (20+ specs)")
    print(f"   • Enhanced long descriptions")
    print(f"   • Technical highlights and program details")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(enhance_washing_machines())
