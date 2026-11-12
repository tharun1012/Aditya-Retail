import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

async def add_eight_dishwashers():
    # Get MongoDB connection string
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client['startup_template']
    products_collection = db['products']
    
    print("=" * 70)
    print("BULK ADDING 8 DISHWASHERS TO UNCATEGORIZED")
    print("=" * 70)
    
    # Product data for all 8 dishwashers
    products = [
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Free-Standing Dishwasher 60 cm - Steel",
            "model_number": "SMS6HMC00I",
            "brand": "Bosch",
            "category": "Uncategorized",
            "subcategory": "Series 6",
            "price": 64990.00,
            "original_price": 76990.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 5,
            "rating": 4.5,
            "reviews_count": 0,
            "short_description": "Free-standing dishwasher with 13 place settings, 6 programs, and efficient cleaning performance",
            "long_description": "The Bosch Series 6 Free-Standing Dishwasher SMS6HMC00I offers exceptional cleaning performance with 13 place settings capacity, making it ideal for larger families. Features 6 specialized wash programs, heat exchanger drying, and energy-efficient operation. The stainless steel finish adds elegance to any kitchen while delivering professional-grade dishwashing results.",
            "images": ["https://media3.bsh-group.com/Product_Shots/900x/SMS6HMC00I_def.webp"],
            "key_features": ["13 place settings capacity", "6 wash programs", "Heat exchanger drying", "Steel finish", "Energy efficient", "Free delivery", "6 wash programs for versatile cleaning", "Durable construction", "Easy operation", "2 years warranty"],
            "specifications": {"Type": "Free-Standing", "Series": "Series 6", "Width": "60 cm", "Place Settings": "13", "Programs": "6", "Drying System": "Heat exchanger", "Color": "Steel", "Warranty": "2 years"},
            "documents": [
                {"title": "User Manual", "type": "manual", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6HMC00I-Manual.pdf", "size": "3.0 MB", "description": "Complete user manual"},
                {"title": "Specification Sheet", "type": "specification", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6HMC00I-Specs.pdf", "size": "900 KB", "description": "Technical specifications"},
                {"title": "Installation Guide", "type": "guide", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6HMC00I-Install.pdf", "size": "1.5 MB", "description": "Installation instructions"},
                {"title": "Warranty Info", "type": "warranty", "url": "https://www.bosch-home.in/store/medias/Bosch-Warranty.pdf", "size": "450 KB", "description": "Warranty terms"}
            ],
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/dishwashers/free-standing-dishwashers/free-standing-dishwashers-with-60cm-width/SMS6HMC00I"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Free-Standing Dishwasher 60 cm - Black",
            "model_number": "SMS6HMI01I",
            "brand": "Bosch",
            "category": "Uncategorized",
            "subcategory": "Series 6",
            "price": 67990.00,
            "original_price": 79990.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 6,
            "rating": 4.6,
            "reviews_count": 0,
            "short_description": "Free-standing dishwasher with 13 place settings, advanced cleaning technology, and elegant black finish",
            "long_description": "The Bosch Series 6 SMS6HMI01I combines superior cleaning performance with modern aesthetics. With 13 place settings and advanced wash programs, it handles large loads effortlessly. The elegant black finish complements contemporary kitchens while delivering exceptional dishwashing results with energy-efficient operation.",
            "images": ["https://media3.bsh-group.com/Product_Shots/900x/SMS6HMI01I_def.webp"],
            "key_features": ["13 place settings capacity", "Advanced wash programs", "Heat exchanger drying", "Elegant black finish", "Energy efficient operation", "Multiple wash options", "Quiet operation", "Easy to use controls", "Free delivery", "2 years warranty"],
            "specifications": {"Type": "Free-Standing", "Series": "Series 6", "Width": "60 cm", "Place Settings": "13", "Programs": "6", "Drying System": "Heat exchanger", "Color": "Black", "Warranty": "2 years"},
            "documents": [
                {"title": "User Manual", "type": "manual", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6HMI01I-Manual.pdf", "size": "3.0 MB", "description": "Complete user manual"},
                {"title": "Specification Sheet", "type": "specification", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6HMI01I-Specs.pdf", "size": "900 KB", "description": "Technical specifications"},
                {"title": "Installation Guide", "type": "guide", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6HMI01I-Install.pdf", "size": "1.5 MB", "description": "Installation instructions"},
                {"title": "Warranty Info", "type": "warranty", "url": "https://www.bosch-home.in/store/medias/Bosch-Warranty.pdf", "size": "450 KB", "description": "Warranty terms"}
            ],
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/dishwashers/free-standing-dishwashers/free-standing-dishwashers-with-60cm-width/SMS6HMI01I"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Free-Standing Dishwasher 60 cm - White",
            "model_number": "SMS6HMI00I",
            "brand": "Bosch",
            "category": "Uncategorized",
            "subcategory": "Series 6",
            "price": 67990.00,
            "original_price": 79990.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 6,
            "rating": 4.5,
            "reviews_count": 0,
            "short_description": "Free-standing dishwasher with 13 place settings and classic white finish",
            "long_description": "The Bosch Series 6 SMS6HMI00I offers premium dishwashing performance in a classic white finish. With 13 place settings and multiple wash programs, it delivers spotless results every time. Energy-efficient operation and quiet performance make it perfect for modern homes.",
            "images": ["https://media3.bsh-group.com/Product_Shots/900x/SMS6HMI00I_def.webp"],
            "key_features": ["13 place settings capacity", "Classic white finish", "6 specialized programs", "Heat exchanger drying", "Energy efficient", "Quiet operation", "Easy to clean interior", "Durable construction", "Free delivery", "2 years warranty"],
            "specifications": {"Type": "Free-Standing", "Series": "Series 6", "Width": "60 cm", "Place Settings": "13", "Programs": "6", "Drying System": "Heat exchanger", "Color": "White", "Warranty": "2 years"},
            "documents": [
                {"title": "User Manual", "type": "manual", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6HMI00I-Manual.pdf", "size": "3.0 MB", "description": "Complete user manual"},
                {"title": "Specification Sheet", "type": "specification", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6HMI00I-Specs.pdf", "size": "900 KB", "description": "Technical specifications"},
                {"title": "Installation Guide", "type": "guide", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6HMI00I-Install.pdf", "size": "1.5 MB", "description": "Installation instructions"},
                {"title": "Warranty Info", "type": "warranty", "url": "https://www.bosch-home.in/store/medias/Bosch-Warranty.pdf", "size": "450 KB", "description": "Warranty terms"}
            ],
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/dishwashers/free-standing-dishwashers/free-standing-dishwashers-with-60cm-width/SMS6HMI00I"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Free-Standing Dishwasher 60 cm - Silver",
            "model_number": "SMS6ZCW37Q",
            "brand": "Bosch",
            "category": "Uncategorized",
            "subcategory": "Series 6",
            "price": 72990.00,
            "original_price": 85990.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 4,
            "rating": 4.7,
            "reviews_count": 0,
            "short_description": "Premium free-standing dishwasher with 14 place settings and advanced features",
            "long_description": "The Bosch Series 6 SMS6ZCW37Q is a premium dishwasher offering 14 place settings capacity and advanced cleaning technology. With Zeolith drying for exceptional drying results and multiple specialized programs, it delivers professional-grade performance. The elegant silver finish adds sophistication to any kitchen.",
            "images": ["https://media3.bsh-group.com/Product_Shots/900x/SMS6ZCW37Q_def.webp"],
            "key_features": ["14 place settings capacity", "Zeolith drying technology", "Premium silver finish", "Advanced wash programs", "Energy efficient A+++ rating", "Extra quiet operation", "Perfect drying results", "Home Connect ready", "Free delivery", "2 years warranty"],
            "specifications": {"Type": "Free-Standing", "Series": "Series 6", "Width": "60 cm", "Place Settings": "14", "Programs": "6", "Drying System": "Zeolith", "Color": "Silver", "Energy Rating": "A+++", "Warranty": "2 years"},
            "documents": [
                {"title": "User Manual", "type": "manual", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6ZCW37Q-Manual.pdf", "size": "3.2 MB", "description": "Complete user manual"},
                {"title": "Specification Sheet", "type": "specification", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6ZCW37Q-Specs.pdf", "size": "950 KB", "description": "Technical specifications"},
                {"title": "Installation Guide", "type": "guide", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6ZCW37Q-Install.pdf", "size": "1.6 MB", "description": "Installation instructions"},
                {"title": "Warranty Info", "type": "warranty", "url": "https://www.bosch-home.in/store/medias/Bosch-Warranty.pdf", "size": "450 KB", "description": "Warranty terms"}
            ],
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/dishwashers/free-standing-dishwashers/free-standing-dishwashers-with-60cm-width/SMS6ZCW37Q"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Free-Standing Dishwasher 60 cm - Black Inox",
            "model_number": "SMS6IKI01I",
            "brand": "Bosch",
            "category": "Uncategorized",
            "subcategory": "Series 6",
            "price": 74990.00,
            "original_price": 88990.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 5,
            "rating": 4.8,
            "reviews_count": 0,
            "short_description": "Premium dishwasher with 14 place settings, Home Connect, and black inox finish",
            "long_description": "The Bosch Series 6 SMS6IKI01I represents the pinnacle of dishwashing technology. With 14 place settings, Home Connect smart connectivity, and advanced wash programs, it offers unmatched convenience and performance. The sophisticated black inox finish adds a premium touch to your kitchen.",
            "images": ["https://media3.bsh-group.com/Product_Shots/900x/SMS6IKI01I_def.webp"],
            "key_features": ["14 place settings capacity", "Home Connect smart control", "Black inox premium finish", "varioSpeed Plus", "IntensiveZone technology", "PerfectDry with Zeolith", "Extra quiet 42dB", "8 specialized programs", "Free delivery", "2 years warranty"],
            "specifications": {"Type": "Free-Standing", "Series": "Series 6", "Width": "60 cm", "Place Settings": "14", "Programs": "8", "Drying System": "Zeolith", "Color": "Black Inox", "Home Connect": "Yes", "Noise Level": "42 dB", "Warranty": "2 years"},
            "documents": [
                {"title": "User Manual", "type": "manual", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6IKI01I-Manual.pdf", "size": "3.5 MB", "description": "Complete user manual"},
                {"title": "Specification Sheet", "type": "specification", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6IKI01I-Specs.pdf", "size": "1.0 MB", "description": "Technical specifications"},
                {"title": "Installation Guide", "type": "guide", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6IKI01I-Install.pdf", "size": "1.7 MB", "description": "Installation instructions"},
                {"title": "Warranty Info", "type": "warranty", "url": "https://www.bosch-home.in/store/medias/Bosch-Warranty.pdf", "size": "450 KB", "description": "Warranty terms"}
            ],
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/dishwashers/free-standing-dishwashers/free-standing-dishwashers-with-60cm-width/SMS6IKI01I"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Free-Standing Dishwasher 60 cm - White",
            "model_number": "SMS6IKW01I",
            "brand": "Bosch",
            "category": "Uncategorized",
            "subcategory": "Series 6",
            "price": 74990.00,
            "original_price": 88990.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 5,
            "rating": 4.8,
            "reviews_count": 0,
            "short_description": "Premium dishwasher with 14 place settings, Home Connect, and white finish",
            "long_description": "The Bosch Series 6 SMS6IKW01I combines premium features with classic elegance. Featuring 14 place settings, Home Connect connectivity, and Zeolith drying technology, it delivers exceptional results. The pristine white finish suits any kitchen style while providing professional-grade performance.",
            "images": ["https://media3.bsh-group.com/Product_Shots/900x/SMS6IKW01I_def.webp"],
            "key_features": ["14 place settings capacity", "Home Connect connectivity", "Classic white finish", "Zeolith drying technology", "varioSpeed Plus option", "IntensiveZone feature", "Ultra quiet 42dB operation", "8 wash programs", "Free delivery", "2 years warranty"],
            "specifications": {"Type": "Free-Standing", "Series": "Series 6", "Width": "60 cm", "Place Settings": "14", "Programs": "8", "Drying System": "Zeolith", "Color": "White", "Home Connect": "Yes", "Noise Level": "42 dB", "Warranty": "2 years"},
            "documents": [
                {"title": "User Manual", "type": "manual", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6IKW01I-Manual.pdf", "size": "3.5 MB", "description": "Complete user manual"},
                {"title": "Specification Sheet", "type": "specification", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6IKW01I-Specs.pdf", "size": "1.0 MB", "description": "Technical specifications"},
                {"title": "Installation Guide", "type": "guide", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMS6IKW01I-Install.pdf", "size": "1.7 MB", "description": "Installation instructions"},
                {"title": "Warranty Info", "type": "warranty", "url": "https://www.bosch-home.in/store/medias/Bosch-Warranty.pdf", "size": "450 KB", "description": "Warranty terms"}
            ],
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/dishwashers/free-standing-dishwashers/free-standing-dishwashers-with-60cm-width/SMS6IKW01I"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Fully Integrated Dishwasher 60 cm",
            "model_number": "SMV6HMX01I",
            "brand": "Bosch",
            "category": "Uncategorized",
            "subcategory": "Series 6",
            "price": 79990.00,
            "original_price": 94990.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 4,
            "rating": 4.9,
            "reviews_count": 0,
            "short_description": "Fully integrated built-in dishwasher with 13 place settings and seamless design",
            "long_description": "The Bosch Series 6 SMV6HMX01I is a fully integrated dishwasher that disappears seamlessly into your kitchen cabinetry. With 13 place settings and advanced cleaning technology, it offers the perfect blend of aesthetics and performance. Features Home Connect for smart control and multiple wash programs for every cleaning need.",
            "images": ["https://media3.bsh-group.com/Product_Shots/900x/SMV6HMX01I_def.webp"],
            "key_features": ["13 place settings capacity", "Fully integrated design", "Home Connect enabled", "InfoLight indicator", "TimeLight floor projection", "Heat exchanger drying", "Multiple wash programs", "Quiet operation", "Free delivery and installation", "2 years warranty"],
            "specifications": {"Type": "Fully Integrated", "Series": "Series 6", "Width": "60 cm", "Place Settings": "13", "Programs": "6", "Drying System": "Heat exchanger", "Home Connect": "Yes", "InfoLight": "Yes", "TimeLight": "Yes", "Warranty": "2 years"},
            "documents": [
                {"title": "User Manual", "type": "manual", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMV6HMX01I-Manual.pdf", "size": "3.8 MB", "description": "Complete user manual"},
                {"title": "Specification Sheet", "type": "specification", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMV6HMX01I-Specs.pdf", "size": "1.1 MB", "description": "Technical specifications"},
                {"title": "Installation Guide", "type": "guide", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMV6HMX01I-Install.pdf", "size": "2.0 MB", "description": "Installation instructions"},
                {"title": "Warranty Info", "type": "warranty", "url": "https://www.bosch-home.in/store/medias/Bosch-Warranty.pdf", "size": "450 KB", "description": "Warranty terms"}
            ],
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/dishwashers/built-in-dishwashers/fully-integrated-dishwasher-60-cm/SMV6HMX01I"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 4 Semi-Integrated Dishwasher 60 cm",
            "model_number": "SMI4IKS00I",
            "brand": "Bosch",
            "category": "Uncategorized",
            "subcategory": "Series 4",
            "price": 69990.00,
            "original_price": 82990.00,
            "currency": "INR",
            "in_stock": True,
            "stock_quantity": 6,
            "rating": 4.6,
            "reviews_count": 0,
            "short_description": "Semi-integrated dishwasher with 13 place settings and visible control panel",
            "long_description": "The Bosch Series 4 SMI4IKS00I offers the perfect balance between integrated design and accessible controls. With 13 place settings and semi-integrated installation, the control panel remains visible for easy operation while the door seamlessly blends with your kitchen. Features multiple wash programs and energy-efficient performance.",
            "images": ["https://media3.bsh-group.in/Product_Shots/900x/SMI4IKS00I_def.webp"],
            "key_features": ["13 place settings capacity", "Semi-integrated design", "Visible control panel", "Heat exchanger drying", "Multiple wash programs", "Energy efficient", "Quiet operation", "Easy to use controls", "Free delivery and installation", "2 years warranty"],
            "specifications": {"Type": "Semi-Integrated", "Series": "Series 4", "Width": "60 cm", "Place Settings": "13", "Programs": "6", "Drying System": "Heat exchanger", "Home Connect": "No", "Control Panel": "Visible", "Warranty": "2 years"},
            "documents": [
                {"title": "User Manual", "type": "manual", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMI4IKS00I-Manual.pdf", "size": "3.0 MB", "description": "Complete user manual"},
                {"title": "Specification Sheet", "type": "specification", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMI4IKS00I-Specs.pdf", "size": "950 KB", "description": "Technical specifications"},
                {"title": "Installation Guide", "type": "guide", "url": f"https://www.bosch-home.in/store/medias/Bosch-SMI4IKS00I-Install.pdf", "size": "1.8 MB", "description": "Installation instructions"},
                {"title": "Warranty Info", "type": "warranty", "url": "https://www.bosch-home.in/store/medias/Bosch-Warranty.pdf", "size": "450 KB", "description": "Warranty terms"}
            ],
            "warranty": "2 years comprehensive warranty",
            "free_delivery": True,
            "product_url": "https://www.bosch-home.in/en/product/dishwashers/built-in-dishwashers/semi-integrated-dishwasher-60-cm/SMI4IKS00I"
        }
    ]
    
    added_count = 0
    skipped_count = 0
    
    for product in products:
        # Check if product already exists
        existing = await products_collection.find_one({"model_number": product["model_number"]})
        if existing:
            print(f"\n⚠️  {product['model_number']} already exists, skipping...")
            skipped_count += 1
            continue
        
        # Insert product
        result = await products_collection.insert_one(product)
        discount = int((1 - product['price']/product['original_price']) * 100)
        
        print(f"\n✅ Added: {product['name']}")
        print(f"   Model: {product['model_number']}")
        print(f"   Price: ₹{product['price']:,.0f} (-{discount}%)")
        print(f"   Place Settings: {product['specifications'].get('Place Settings', 'N/A')}")
        print(f"   Type: {product['specifications'].get('Type', 'N/A')}")
        
        added_count += 1
    
    # Close connection
    client.close()
    
    print("\n" + "=" * 70)
    print("BULK ADDITION COMPLETE")
    print("=" * 70)
    print(f"✅ Successfully Added: {added_count}")
    print(f"⏭️  Skipped (Already Exist): {skipped_count}")
    print(f"📦 Total Processed: {len(products)}")
    print("\n🎯 All products added to 'Uncategorized' category")
    print("   Use manage_categories.py to assign proper categories")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(add_eight_dishwashers())
