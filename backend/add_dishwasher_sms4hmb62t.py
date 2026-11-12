import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

async def add_dishwasher():
    # Get MongoDB connection string
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client['startup_template']
    products_collection = db['products']
    
    # Product data for Bosch Dishwasher (SMS4HMB62T)
    product = {
        "id": str(uuid.uuid4()),
        "name": "Bosch Series 6 Free-Standing Dishwasher 60 cm - Black",
        "model_number": "SMS4HMB62T",
        "brand": "Bosch",
        "category": "Uncategorized",
        "subcategory": "Series 6",
        "price": 70124.00,
        "original_price": 82490.00,
        "currency": "INR",
        "in_stock": False,
        "stock_quantity": 0,
        "rating": 3.0,
        "reviews_count": 9,
        "short_description": "Free-standing dishwasher with 12 place settings, 6 programs, Home Connect, and heat exchanger drying",
        "long_description": "The Bosch Series 6 Free-Standing Dishwasher SMS4HMB62T combines superior cleaning performance with smart connectivity. With a capacity of 12 place settings, it's perfect for medium to large families. The heat exchanger drying system ensures perfectly dry dishes every time while being energy efficient. Featuring 6 specialized wash programs including a steam cleaning program that releases high-temperature steam during pre-wash to soften stubborn stains, this dishwasher delivers exceptional results. The innovative Bosch Self Cleaning Filter cleans itself after each wash with a built-in cleaning nozzle, reducing maintenance needs. With Home Connect smart connectivity, you can control and monitor your dishwasher remotely via smartphone. The varioSpeed Plus option reduces washing time by up to 66% while maintaining excellent cleaning results. Additional features include Intensive Zone for heavily soiled items, Extra Rinse for sensitive skin, and a Favourite programme that you can personalize with just one touch. The elegant black finish adds a modern touch to any kitchen.",
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/21043435_SMS4HMB62T_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21085814_SMS4HMB62T_PGA3_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/19714426_A01_CD10_PGA6_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/25583534_AP4250BO_1_FS_SCH_E_J_2SR_16_FHK2_PGA2_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21031518_UR65AX05_BPR_SIDG_2FL_2PKL_MID_2SR_PGA4_def.webp"
        ],
        "key_features": [
            "12 place settings capacity - ideal for medium to large families",
            "6 specialized wash programs for every cleaning need",
            "Heat exchanger drying system for perfectly dry dishes",
            "Steam cleaning program for stubborn stains",
            "Bosch Self Cleaning Filter - automatic filter cleaning",
            "Home Connect - smart connectivity and remote control",
            "varioSpeed Plus - up to 66% faster washing",
            "Intensive Zone for heavily soiled items",
            "Extra Rinse option for sensitive skin",
            "Favourite programme - personalized one-touch operation",
            "60 cm width - standard size fits most kitchens",
            "Energy efficient operation",
            "Elegant black finish",
            "Free delivery included"
        ],
        "specifications": {
            "Type": "Free-Standing Dishwasher",
            "Series": "Series 6",
            "Width": "60 cm",
            "Place Settings": "12",
            "Number of Programs": "6",
            "Drying System": "Heat exchanger",
            "Color": "Black",
            "Home Connect": "Yes",
            "Additional Options": "Remote control, Intensive Zone, Pretreatment, Extra Rinse, varioSpeed Plus",
            "Energy Rating": "Standard",
            "Dimensions (H x W x D)": "845 x 598 x 600 mm",
            "Weight": "Approx. 50 kg",
            "Noise Level": "Standard",
            "Water Consumption": "Standard",
            "Warranty": "2 years",
            "Hygiene Certified": "Yes"
        },
        "documents": [
            {
                "title": "Dishwasher User Manual",
                "type": "manual",
                "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS4HMB62T-User-Manual.pdf",
                "size": "3.2 MB",
                "description": "Complete user manual with installation and operation instructions"
            },
            {
                "title": "Product Specification Sheet",
                "type": "specification",
                "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS4HMB62T-Specifications.pdf",
                "size": "950 KB",
                "description": "Detailed technical specifications and dimensions"
            },
            {
                "title": "Installation Guide",
                "type": "guide",
                "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS4HMB62T-Installation.pdf",
                "size": "1.5 MB",
                "description": "Step-by-step installation instructions"
            },
            {
                "title": "Warranty Information",
                "type": "warranty",
                "url": "https://www.bosch-home.in/store/medias/Bosch-Warranty-Terms.pdf",
                "size": "450 KB",
                "description": "Warranty terms and conditions"
            }
        ],
        "warranty": "2 years comprehensive warranty",
        "free_delivery": True,
        "product_url": "https://www.bosch-home.in/en/product/dishwashers/free-standing-dishwashers/free-standing-dishwashers-with-60cm-width/SMS4HMB62T"
    }
    
    # Check if product already exists
    existing = await products_collection.find_one({"model_number": product["model_number"]})
    if existing:
        print(f"⚠️  Product {product['model_number']} already exists in database")
        client.close()
        return
    
    # Insert product
    result = await products_collection.insert_one(product)
    discount = int((1 - product['price']/product['original_price']) * 100)
    
    print("=" * 70)
    print("✅ PRODUCT ADDED TO UNCATEGORIZED")
    print("=" * 70)
    print(f"Name: {product['name']}")
    print(f"Model: {product['model_number']}")
    print(f"Category: {product['category']} (can be changed later)")
    print(f"Price: ₹{product['price']:,.0f} (Save {discount}%)")
    print(f"Rating: {product['rating']}/5 ({product['reviews_count']} reviews)")
    print(f"Stock Status: Currently unavailable")
    print(f"\nProduct Details:")
    print(f"  • Place Settings: 12")
    print(f"  • Programs: 6")
    print(f"  • Home Connect: Yes")
    print(f"  • Key Features: {len(product['key_features'])}")
    print(f"  • Specifications: {len(product['specifications'])}")
    print(f"  • Images: {len(product['images'])}")
    print(f"  • Documents: {len(product['documents'])}")
    print(f"\nMongoDB ID: {result.inserted_id}")
    print("=" * 70)
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(add_dishwasher())
