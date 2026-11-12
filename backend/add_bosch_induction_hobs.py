import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_induction_hobs():
    """Add 2 Bosch Induction Hobs to the database"""
    
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        print("❌ MONGO_URL not found in environment variables")
        return
    
    client = AsyncIOMotorClient(mongo_url)
    db = client.ecommerce_db
    products_collection = db.products
    
    products = [
        # Product 1: PIB375FB5I - Domino 30cm
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Domino Induction Hob 30 cm",
            "model_number": "PIB375FB5I",
            "brand": "Bosch",
            "category": "Induction Hob",
            "sub_category": "Domino Induction Hob",
            "price": 54990.00,
            "original_price": 60990.00,
            "currency": "INR",
            "stock_quantity": 10,
            "description": "Bosch Series 6 Domino Induction Hob 30 cm with 2 cooking zones, PowerBoost function, and touch control. Perfect for compact kitchens with surface mount design and elegant frame.",
            "long_description": "The Bosch PIB375FB5I Series 6 Domino Induction Hob combines compact design with powerful performance in just 30 cm width. Featuring 2 induction cooking zones (210mm - 1400W and 145mm - 2200W) with PowerBoost function for up to 35% faster heating. The touch control panel offers 17-stage power settings per zone for precise cooking control. Made in Europe with induction technology that saves an average of 20% energy compared to radiant technology. The elegant design frame and ceramic surface ensure easy cleaning while the timer with switch-off function and child lock provide safety and convenience.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA02951098_PIB375FB5I_ElectricHob_Bosch_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01058952_DA3_PKC675DP1D_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA03248475_PIB375FB5I_ElectricHob_Bosch_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA03248478_PIB375FB5I_ElectricHob_Bosch_PGA3_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/MCSA02951098_PIB375FB5I_ElectricHob_Bosch_STP_def.webp",
            "features": [
                "2 induction cooking zones",
                "PowerBoost function - up to 35% faster heating",
                "Touch control with 17-stage power settings per zone",
                "Timer with automatic switch-off function",
                "Child lock for safety",
                "Quick Start function",
                "Residual heat indicator",
                "Energy efficient - saves 20% vs radiant technology",
                "Compact 30 cm width - ideal for small spaces",
                "Ceramic surface with design frame",
                "Total power: 3700W",
                "Made in Europe"
            ],
            "specifications": {
                "Dimensions": {
                    "Width": "306 mm (30 cm)",
                    "Depth": "527 mm",
                    "Height": "51 mm",
                    "Height Above Worktop": "6 mm"
                },
                "Cooking Zones": {
                    "Total Zones": "2",
                    "Zone 1": "210 mm Ø - 1400W",
                    "Zone 2": "145 mm Ø - 2200W",
                    "PowerBoost": "Available on all zones"
                },
                "Power": {
                    "Total Connected Load": "3700W (3.7 kW)",
                    "Voltage": "220-240V",
                    "Energy Consumption": "175 Wh/kg"
                },
                "Control": {
                    "Type": "Touch Control",
                    "Power Settings": "17-stage per zone",
                    "Quick Start": "Yes"
                },
                "Design": {
                    "Surface Material": "Ceramic",
                    "Color": "Black",
                    "Frame Type": "Design frame",
                    "Installation": "Surface mount with frame"
                },
                "Safety Features": {
                    "Residual Heat Indicator": "Separate per zone",
                    "Child Lock": "Yes",
                    "Auto Switch-off Timer": "Yes"
                },
                "Installation": {
                    "Cutout Width": "270 mm",
                    "Cutout Depth": "490 mm",
                    "Cord Length": "110 cm",
                    "Plug Type": "No plug (hardwired)"
                }
            },
            "highlights": [
                "Compact Domino Design: Perfect 30 cm width for space-saving kitchens or modular cooktop configurations",
                "PowerBoost Technology: Heat up to 35% faster than highest power level for quick cooking",
                "Precision Control: 17-stage power settings per zone for accurate temperature management",
                "Energy Efficient: Induction technology saves 20% energy compared to radiant cooktops",
                "Made in Europe: Premium quality and craftsmanship",
                "Smart Safety: Timer with auto switch-off and child lock for peace of mind"
            ],
            "ai_features": {
                "smart_recommendations": "Perfect for compact kitchens, studio apartments, or as an additional cooktop. Ideal for 1-2 person households or side-by-side installation with other Domino units.",
                "usage_tips": [
                    "Use PowerBoost for quick water boiling - saves time and energy",
                    "17-stage control allows precise simmering for delicate sauces",
                    "Set timer for automatic switch-off to prevent overcooking",
                    "Activate child lock when not in use for safety",
                    "Clean ceramic surface with soft cloth after each use",
                    "Use induction-compatible cookware with magnetic base",
                    "Zone 2 (2200W) ideal for main cooking, Zone 1 (1400W) for simmering",
                    "Combine with other Domino units for custom cooktop configuration"
                ],
                "compatibility": "Requires induction-compatible cookware (magnetic base). Surface mount installation."
            },
            "documents": [
                {
                    "name": "User Manual",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/inductionandelectrohobs/induction-hobs/PIB375FB5I",
                    "description": "Complete user manual with installation and operation instructions"
                },
                {
                    "name": "Installation Instructions",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/inductionandelectrohobs/induction-hobs/PIB375FB5I",
                    "description": "Detailed installation guide"
                },
                {
                    "name": "Product Specification Sheet",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/inductionandelectrohobs/induction-hobs/PIB375FB5I",
                    "description": "Complete technical specifications"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "tags": ["induction hob", "domino", "bosch", "series 6", "kitchen appliance", "compact", "powerboost", "touch control", "30cm", "energy efficient", "made in europe"],
            "rating": 0.0,
            "reviews_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "discount_percentage": 10
        },
        
        # Product 2: PIE651BB5I - 60cm 4 Zone
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 4 Induction Hob 60 cm",
            "model_number": "PIE651BB5I",
            "brand": "Bosch",
            "category": "Induction Hob",
            "sub_category": "Built-in Induction Hob",
            "price": 67490.00,
            "original_price": 74990.00,
            "currency": "INR",
            "stock_quantity": 15,
            "description": "Bosch Series 4 Induction Hob 60 cm with 4 cooking zones, PowerBoost on all zones, TouchControl +/-, and U-bevel frameless design. Perfect for modern kitchens with surface mount installation.",
            "long_description": "The Bosch PIE651BB5I Series 4 Induction Hob offers exceptional cooking flexibility with 4 induction zones ranging from 14.5cm to 21cm. All zones feature PowerBoost function for up to 35% faster heating. The intuitive TouchControl +/- allows easy selection and precise power adjustment across 17 stages. The elegant U-bevel frameless design creates a seamless look in your kitchen. With 7400W total power, restart function to restore settings after accidental switch-off, and comprehensive safety features including child lock and residual heat indicators, this hob is perfect for families and cooking enthusiasts. Made in Europe with premium quality.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA02951099_PIE651BB5I_ElectricHob_Bosch_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA03248479_PIE651BB5I_ElectricHob_Bosch_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA03248480_PIE651BB5I_ElectricHob_Bosch_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/23070571_DeisgnLine_Bosch_U-formBevel_Black_PGA2_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/MCSA02951099_PIE651BB5I_ElectricHob_Bosch_STP_def.webp",
            "features": [
                "4 induction cooking zones with flexible sizes",
                "PowerBoost on all zones - up to 35% faster heating",
                "TouchControl +/- for easy zone selection and power adjustment",
                "17-stage power settings per zone",
                "Timer with automatic switch-off function",
                "Countdown timer",
                "Restart function - restores settings after accidental switch-off",
                "Quick Start function",
                "Child lock for safety",
                "Residual heat indicator per zone",
                "Elegant U-bevel frameless design",
                "Total power: 7400W",
                "Made in Europe",
                "Rated 5.0 stars (2 reviews)"
            ],
            "specifications": {
                "Dimensions": {
                    "Width": "592 mm (60 cm)",
                    "Depth": "522 mm",
                    "Height": "51 mm",
                    "Minimum Worktop Thickness": "16 mm"
                },
                "Cooking Zones": {
                    "Total Zones": "4",
                    "Front Left Zone": "18 cm Ø - 1.8 kW (3.1 kW with PowerBoost)",
                    "Rear Left Zone": "18 cm Ø - 1.8 kW (3.1 kW with PowerBoost)",
                    "Rear Right Zone": "14.5 cm Ø - 1.4 kW (2.2 kW with PowerBoost)",
                    "Front Right Zone": "21 cm Ø - 2.2 kW (3.7 kW with PowerBoost)",
                    "PowerBoost": "Available on all zones"
                },
                "Power": {
                    "Total Connected Load": "7400W (7.4 kW)",
                    "Voltage": "220-240V"
                },
                "Control": {
                    "Type": "TouchControl +/-",
                    "Power Settings": "17-stage per zone",
                    "Quick Start": "Yes",
                    "Restart Function": "Yes"
                },
                "Design": {
                    "Surface Material": "Ceramic glass",
                    "Color": "Black",
                    "Frame Type": "U-form bevel (frameless)",
                    "Installation": "Built-in surface mount"
                },
                "Safety Features": {
                    "Residual Heat Indicator": "Separate per zone",
                    "Child Lock": "Yes",
                    "Auto Switch-off Timer": "Yes",
                    "Countdown Timer": "Yes"
                },
                "Installation": {
                    "Cutout Width": "560 mm",
                    "Cutout Depth": "490-500 mm",
                    "Cord Length": "110 cm",
                    "Plug Type": "No plug (hardwired)"
                }
            },
            "highlights": [
                "4-Zone Flexibility: Multiple cooking zones from 14.5cm to 21cm accommodate various pot and pan sizes",
                "PowerBoost on All Zones: Every zone heats up to 35% faster for maximum efficiency",
                "TouchControl +/-: Intuitive control with direct zone selection and easy power adjustment",
                "Restart Function: Automatically restores your settings if accidentally switched off - no need to start over",
                "Frameless U-Bevel Design: Sleek, seamless look that's easy to clean with elegant beveled edges",
                "Made in Europe: Premium quality and reliability with 5-star customer rating"
            ],
            "ai_features": {
                "smart_recommendations": "Perfect for standard 60cm kitchen countertops. Ideal for families of 3-5 people or cooking enthusiasts who need multiple zones.",
                "usage_tips": [
                    "Use PowerBoost on all zones for quick water boiling and faster cooking",
                    "Front right 21cm zone perfect for large pots and woks",
                    "Rear right 14.5cm zone ideal for small pots and sauces",
                    "Two 18cm left zones provide excellent flexibility for medium cookware",
                    "Set individual timers for each zone to manage multiple dishes",
                    "Restart function saves time if accidentally switched off",
                    "Touch Select makes switching between zones quick and easy",
                    "U-bevel design - wipe spills directly off the edge for easy cleaning",
                    "Use induction-compatible cookware with magnetic base for best results"
                ],
                "compatibility": "Requires induction-compatible cookware (magnetic base). Built-in installation requires 560mm x 490-500mm cutout."
            },
            "documents": [
                {
                    "name": "User Manual",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/inductionandelectrohobs/induction-hobs/PIE651BB5I",
                    "description": "Complete user manual with installation and operation instructions"
                },
                {
                    "name": "Installation Instructions",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/inductionandelectrohobs/induction-hobs/PIE651BB5I",
                    "description": "Detailed installation guide"
                },
                {
                    "name": "Product Specification Sheet",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/inductionandelectrohobs/induction-hobs/PIE651BB5I",
                    "description": "Complete technical specifications"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "tags": ["induction hob", "built-in", "bosch", "series 4", "kitchen appliance", "60cm", "powerboost", "touch control", "4 zones", "energy efficient", "made in europe", "frameless"],
            "rating": 5.0,
            "reviews_count": 2,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "discount_percentage": 10
        }
    ]
    
    try:
        for product in products:
            result = await products_collection.insert_one(product)
            print(f"✅ Successfully added {product['name']}")
            print(f"   Product ID: {product['id']}")
            print(f"   Model: {product['model_number']}")
            print(f"   Price: ₹{product['price']:,.2f} (was ₹{product['original_price']:,.2f})")
            print(f"   Category: {product['category']} - {product['sub_category']}")
            print(f"   Images: {len(product['images'])} images added")
            if product['rating'] > 0:
                print(f"   Rating: {product['rating']}/5.0 ({product['reviews_count']} reviews)")
            print()
        
    except Exception as e:
        print(f"❌ Error adding products: {e}")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_induction_hobs())
