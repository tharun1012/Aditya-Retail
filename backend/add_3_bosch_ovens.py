import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

load_dotenv()

async def add_three_bosch_ovens():
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 80)
    print("➕ ADDING 3 BOSCH OVENS TO DATABASE")
    print("=" * 80)
    
    products = [
        # Product 1: HBF512BS1I - Serie 2 with LED Display
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Serie 2 Built-in Oven 60 x 60 cm Stainless Steel with LED Display",
            "brand": "Bosch",
            "series": "Serie 2",
            "category": "Built-in Ovens",
            "model": "HBF512BS1I",
            "sku": "BSH-HBF512BS1I",
            "price": 91490,
            "original_price": 101490,
            "description": "Bosch Serie 2 Built-in Oven featuring 66L capacity, 7 heating modes, Red LED display with knob control, and hydrolytic cleaning. Premium stainless steel finish with advanced features for versatile cooking.",
            "short_description": "66L Oven with 7 Modes & LED Display - Stainless Steel",
            "image": "https://media3.bsh-group.com/Product_Shots/5120x/25231487_HBF512BS1I_STP_def.webp",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/25231487_HBF512BS1I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/25231490_HBF512BS1I_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/25231484_HBF512BS1I_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/25231493_HBF512BS1I_PGA3_def.webp"
            ],
            "technical_overview": {
                "Integrated Cleaning System": "Hydrolytic",
                "User Interface": "Red LED display with knob control",
                "Steam Technology": "Not applicable",
                "Telescopic Rails": "No",
                "SoftClose": "No",
                "No. Heating Modes": "7",
                "Main Colour of Product": "Stainless Steel",
                "Capacity": "66 Litres"
            },
            "highlights": [
                {"title": "Spacious 66-Liter Capacity", "description": "Perfect for every occasion with ample cooking space for large meals and family gatherings."},
                {"title": "Red LED Display Control", "description": "Modern digital display with intuitive knob control for precise temperature and mode selection."},
                {"title": "7 Versatile Heating Modes", "description": "Multiple cooking options including conventional heating, grilling, and specialized modes for different recipes."}
            ],
            "features": [
                "66L spacious capacity for family-sized cooking",
                "7 versatile heating modes for diverse recipes",
                "Red LED display with knob control",
                "Hydrolytic cleaning system",
                "Triple-glazed heat-resistant glass door",
                "Stainless steel premium finish",
                "Interior light",
                "Mechanical timer"
            ],
            "spec_groups": {
                "general": {"Brand": "Bosch", "Series": "Serie 2", "Model Number": "HBF512BS1I", "Product Type": "Built-in Electric Oven", "Color": "Stainless Steel", "Control Type": "LED Display with Knobs"},
                "size_weight": {"Product Height": "595 mm", "Product Width": "594 mm", "Product Depth": "548 mm", "Cutout Height": "597 mm", "Cutout Width": "568 mm", "Cutout Depth": "550 mm", "Net Weight": "28 kg (approx)"},
                "technical": {"Capacity": "66 Litres", "Heating Modes": "7", "Temperature Range": "50°C - 250°C", "Power Rating": "3200 W", "Voltage": "220-240V, 50Hz", "Display": "Red LED Display"},
                "comfort": {"Cleaning System": "Hydrolytic", "Telescopic Rails": "No", "SoftClose Door": "No", "Hot Air Safety Fan": "Yes", "Interior Light": "Yes"},
                "connectivity": {"Smart Features": "None", "WiFi Connectivity": "No", "Control Interface": "LED Display with Rotary Knobs"}
            },
            "documents": [
                {"title": "User Manual", "type": "manual", "url": "https://www.manualslib.com/products/Bosch-Hbf512bs1i-14643733.html", "size": "PDF - 2.4 MB"},
                {"title": "Product Specification Sheet", "type": "specs", "url": "https://media3.bosch-home.com/Documents/specsheet/en-IN/HBF512BS1I.pdf", "size": "PDF - 850 KB"},
                {"title": "Installation Instructions", "type": "installation", "url": "#", "size": "PDF - 1.8 MB"}
            ],
            "reviews": [
                {"name": "Vikram Singh", "rating": 5, "date": "20 Jan 2025", "comment": "Excellent oven with LED display. The 7 heating modes are very useful. Great value for money!"},
                {"name": "Anjali Mehta", "rating": 4, "date": "14 Jan 2025", "comment": "Good product. LED display is helpful. Stainless steel finish looks elegant in my kitchen."}
            ],
            "specifications": {"Brand": "Bosch", "Series": "Serie 2", "Model": "HBF512BS1I", "Capacity": "66 Litres", "Warranty": "2 Years"},
            "stock_quantity": 10, "reorder_level": 5, "is_featured": False, "customer_rating": 4.5, "review_count": 76,
            "fast_moving": False, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow(), "warranty": "2 years standard warranty",
            "energy_rating": "A", "warranty_details": {"manufacturer": "2 Years", "parts": "2 Years", "labor": "2 Years on-site service"},
            "delivery_info": {"standard_delivery": "3-5 business days", "installation_included": False, "installation_charges": "₹1,500 - ₹2,500"}
        },
        
        # Product 2: HBG7341B1 - Serie 8 Premium
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Serie 8 Built-in Oven 60 x 60 cm Black with TFT Display",
            "brand": "Bosch",
            "series": "Serie 8",
            "category": "Built-in Ovens",
            "model": "HBG7341B1",
            "sku": "BSH-HBG7341B1",
            "price": 153990,
            "original_price": 170990,
            "description": "Premium Bosch Serie 8 Built-in Oven with 66L capacity, 14 heating modes including Air Fry function, TFT touchdisplay with digital control ring, activeKlean & Hydrolytic cleaning, and SoftClose door. Features Made in Germany quality with advanced cooking technology.",
            "short_description": "66L Premium Oven with 14 Modes & TFT Display - Black",
            "image": "https://media3.bsh-group.com/Product_Shots/5120x/20123431_HBA7741B1_STP_def.webp",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/20123431_HBA7741B1_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/20346669_HBA7741B1_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/26054138_HBG7341B1_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/26054251_HBG7341B1_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/26222880_HBG7341B1_PGA5_def.webp"
            ],
            "technical_overview": {
                "Integrated Cleaning System": "activeKlean setting, Hydrolytic",
                "User Interface": "TFT touchdisplay with digital control ring",
                "Steam Technology": "Not applicable",
                "Telescopic Rails": "No",
                "SoftClose": "Yes",
                "No. Heating Modes": "14",
                "Main Colour of Product": "Black",
                "Capacity": "66 Litres",
                "Made in": "Germany"
            },
            "highlights": [
                {"title": "When intuitive meets digital", "description": "Advanced TFT touchdisplay with digital control ring offers simple and innovative way to select oven settings with premium user experience."},
                {"title": "The gentle way of cooking - Hotair Gentle", "description": "Saves energy while baking and roasting with gentle air circulation for perfect results."},
                {"title": "Air Fry Function", "description": "For perfectly fried foods without oil, such as vegetables, chicken wings, and chips. Healthier cooking made easy."}
            ],
            "features": [
                "Digital Control Ring: simple and innovative oven settings selection",
                "Hotair Gentle: energy-saving while baking and roasting",
                "Air Fry Function: perfectly fried foods without oil",
                "14 versatile heating modes",
                "TFT touchdisplay with digital control",
                "activeKlean & Hydrolytic cleaning systems",
                "SoftClose door mechanism",
                "Made in Germany quality"
            ],
            "spec_groups": {
                "general": {"Brand": "Bosch", "Series": "Serie 8", "Model Number": "HBG7341B1", "Product Type": "Built-in Electric Oven", "Color": "Black", "Control Type": "TFT Touchdisplay with Digital Control Ring", "Made in": "Germany"},
                "size_weight": {"Product Height": "595 mm", "Product Width": "594 mm", "Product Depth": "548 mm", "Cutout Height": "597 mm", "Cutout Width": "568 mm", "Cutout Depth": "550 mm", "Net Weight": "32 kg (approx)"},
                "technical": {"Capacity": "66 Litres", "Heating Modes": "14 (including Air Fry)", "Temperature Range": "30°C - 300°C", "Power Rating": "3600 W", "Voltage": "220-240V, 50Hz", "Display": "TFT Touchdisplay", "Energy Rating": "A+"},
                "comfort": {"Cleaning System": "activeKlean & Hydrolytic", "Telescopic Rails": "No", "SoftClose Door": "Yes", "Interior Light": "Yes - LED", "Child Lock": "Yes"},
                "connectivity": {"Smart Features": "Digital Control Ring", "WiFi Connectivity": "No", "Control Interface": "TFT Touchdisplay"}
            },
            "documents": [
                {"title": "User Manual", "type": "manual", "url": "https://www.manualslib.com/products/Bosch-Hbg7341b1-14810691.html", "size": "PDF - 3.2 MB"},
                {"title": "Product Specification Sheet", "type": "specs", "url": "https://media3.bosch-home.com/Documents/specsheet/en-IN/HBG7341B1.pdf", "size": "PDF - 950 KB"},
                {"title": "Installation Instructions", "type": "installation", "url": "#", "size": "PDF - 2.1 MB"}
            ],
            "reviews": [
                {"name": "Dr. Rajeev Kumar", "rating": 5, "date": "22 Jan 2025", "comment": "Best oven I've ever used! The Air Fry function is amazing. TFT display is so easy to use. Worth every rupee."},
                {"name": "Priya Sharma", "rating": 5, "date": "18 Jan 2025", "comment": "Excellent premium quality. Made in Germany tag shows in the build quality. The digital control ring is intuitive."},
                {"name": "Amit Patel", "rating": 4, "date": "10 Jan 2025", "comment": "Great oven with many features. SoftClose door is very smooth. A bit pricey but quality justifies the cost."}
            ],
            "specifications": {"Brand": "Bosch", "Series": "Serie 8", "Model": "HBG7341B1", "Capacity": "66 Litres", "Warranty": "2 Years"},
            "stock_quantity": 8, "reorder_level": 3, "is_featured": True, "customer_rating": 4.9, "review_count": 156,
            "fast_moving": True, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow(), "warranty": "2 years comprehensive warranty",
            "energy_rating": "A+", "warranty_details": {"manufacturer": "2 Years", "parts": "2 Years", "labor": "2 Years on-site service"},
            "delivery_info": {"standard_delivery": "3-5 business days", "installation_included": True, "installation_charges": "Free"}
        },
        
        # Product 3: HBJ577EB0I - Serie 6 with Pyrolytic Cleaning
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Serie 6 Built-in Oven 60 x 60 cm Black with Pyrolytic Cleaning",
            "brand": "Bosch",
            "series": "Serie 6",
            "category": "Built-in Ovens",
            "model": "HBJ577EB0I",
            "sku": "BSH-HBJ577EB0I",
            "price": 125990,
            "original_price": 139990,
            "description": "Bosch Serie 6 Built-in Oven with 63L capacity, 10 cooking functions including 3D HotAir, Pyrolytic self-cleaning system, telescopic rails, White LCD display with knob control. Energy efficient Class A oven with rapid heating and child lock features.",
            "short_description": "63L Oven with Pyrolytic Cleaning & 10 Functions - Black",
            "image": "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02592758_HBJ577ES0I_def.webp",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02592758_HBJ577ES0I_def.webp",
                "https://media3.bsh-group.com/Product_Shots/5120x/MCSA02592759_HBJ577ES0I_def.webp"
            ],
            "technical_overview": {
                "Integrated Cleaning System": "Pyrolytic Self-Cleaning",
                "User Interface": "White LCD with knob control",
                "Steam Technology": "Not applicable",
                "Telescopic Rails": "Yes",
                "SoftClose": "No",
                "No. Heating Modes": "10",
                "Main Colour of Product": "Black",
                "Capacity": "63 Litres",
                "Energy Efficiency": "Class A"
            },
            "highlights": [
                {"title": "Pyrolytic Self-Cleaning System", "description": "Automatic self-cleaning that burns residues to ash at high temperature. Just wipe away the ash - no manual scrubbing needed!"},
                {"title": "3D HotAir Technology", "description": "Bake or roast on up to 3 levels simultaneously with perfect results on every level thanks to innovative air circulation."},
                {"title": "Rapid Heating Function", "description": "Faster preheating saves time and gets you cooking quicker. Perfect for busy families and working professionals."}
            ],
            "features": [
                "Pyrolytic self-cleaning - burns residues to ash",
                "10 cooking functions including 3D HotAir",
                "Telescopic rails for easy tray access",
                "Rapid heating for faster preheating",
                "Child lock for safety",
                "Energy efficiency Class A",
                "Sabbath mode for religious observance",
                "Auto programs for various dishes"
            ],
            "spec_groups": {
                "general": {"Brand": "Bosch", "Series": "Serie 6", "Model Number": "HBJ577EB0I", "Product Type": "Built-in Electric Oven", "Color": "Black", "Control Type": "White LCD with Knobs"},
                "size_weight": {"Product Height": "595 mm", "Product Width": "594 mm", "Product Depth": "548 mm", "Cutout Height": "575-597 mm", "Cutout Width": "560-568 mm", "Cutout Depth": "550 mm", "Net Weight": "38.6 kg"},
                "technical": {"Capacity": "63 Litres", "Heating Modes": "10 (including 3D HotAir)", "Temperature Range": "30°C - 300°C", "Power Rating": "3000 W", "Voltage": "220-240V, 50Hz", "Display": "White LCD", "Energy Efficiency": "Class A", "Energy Consumption (Conventional)": "0.93 kWh", "Energy Consumption (Fan-Forced)": "0.77 kWh"},
                "comfort": {"Cleaning System": "Pyrolytic Self-Cleaning", "Telescopic Rails": "Yes", "SoftClose Door": "No", "Child Lock": "Yes", "Rapid Heating": "Yes", "Sabbath Mode": "Yes"},
                "connectivity": {"Smart Features": "Auto Programs", "WiFi Connectivity": "No", "Control Interface": "LCD Display with Rotary Knobs"}
            },
            "documents": [
                {"title": "User Manual", "type": "manual", "url": "https://media3.bosch-home.com/Documents/9001766217_C.pdf", "size": "PDF - 3.8 MB"},
                {"title": "Product Specification Sheet", "type": "specs", "url": "https://media3.bosch-home.com/Documents/specsheet/en-IN/HBJ577EB0I.pdf", "size": "PDF - 890 KB"},
                {"title": "Installation Instructions", "type": "installation", "url": "#", "size": "PDF - 2.0 MB"}
            ],
            "reviews": [
                {"name": "Kavita Reddy", "rating": 5, "date": "19 Jan 2025", "comment": "The pyrolytic cleaning is a game-changer! No more scrubbing. The 3D HotAir cooks evenly on all levels."},
                {"name": "Rohit Verma", "rating": 5, "date": "15 Jan 2025", "comment": "Excellent oven! Telescopic rails make it easy to check food. Energy efficient and cooks perfectly."},
                {"name": "Neha Kapoor", "rating": 4, "date": "8 Jan 2025", "comment": "Very good product. Pyrolytic cleaning works great. A bit heavy but solid build quality."}
            ],
            "specifications": {"Brand": "Bosch", "Series": "Serie 6", "Model": "HBJ577EB0I", "Capacity": "63 Litres", "Warranty": "2 Years"},
            "stock_quantity": 10, "reorder_level": 4, "is_featured": True, "customer_rating": 4.7, "review_count": 134,
            "fast_moving": True, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow(), "warranty": "2 years comprehensive warranty",
            "energy_rating": "A", "warranty_details": {"manufacturer": "2 Years", "parts": "2 Years", "labor": "2 Years on-site service"},
            "delivery_info": {"standard_delivery": "3-5 business days", "installation_included": True, "installation_charges": "Free"}
        }
    ]
    
    # Insert all products
    result = await db.products.insert_many(products)
    
    print(f"\n✅ Successfully Added {len(result.inserted_ids)} Products!")
    print("\n📋 Products Summary:")
    for i, product in enumerate(products, 1):
        print(f"\n{i}. {product['name']}")
        print(f"   Model: {product['model']}")
        print(f"   Series: {product['series']}")
        print(f"   Price: ₹{product['price']:,}")
        print(f"   Features: {product['technical_overview']['No. Heating Modes']} heating modes")
    
    # Verify total
    count = await db.products.count_documents({})
    print(f"\n📊 Total products in database: {count}")
    print("=" * 80)
    
    client.close()

asyncio.run(add_three_bosch_ovens())
