import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_premium_ventilation_hobs():
    """Add 2 Premium Bosch Induction Hobs with Integrated Ventilation"""
    
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        print("❌ MONGO_URL not found in environment variables")
        return
    
    client = AsyncIOMotorClient(mongo_url)
    db = client.ecommerce_db
    products_collection = db.products
    
    products = [
        # Product 1: PVQ811F15E - Series 6 with Ventilation
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Induction Hob with Integrated Ventilation 80 cm",
            "model_number": "PVQ811F15E",
            "brand": "Bosch",
            "category": "Induction Hob",
            "sub_category": "Ventilation Induction Hob",
            "price": 245990.00,
            "original_price": 272990.00,
            "currency": "INR",
            "stock_quantity": 5,
            "description": "Bosch Series 6 Induction Hob 80 cm with integrated ventilation system, 4 cooking zones with CombiZone, PowerBoost, AutoOn ventilation, and DirectSelect control. Frameless design with 622 m³/h extraction.",
            "long_description": "The Bosch PVQ811F15E Series 6 Induction Hob revolutionizes cooking with its integrated ventilation system - eliminating the need for a separate chimney. The 80 cm frameless design features 4 induction zones including CombiZone for large cookware. PowerBoost provides up to 35% faster heating while the AutoOn function automatically starts ventilation when the hob heats up. With 622 m³/h air extraction and whisper-quiet 69 dB operation, it efficiently removes cooking odors right at the source. DirectSelect control, restart function, and Made in Europe quality make this a premium choice for modern kitchens.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/14486486_PVQ811F15E_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01059168_DA3_ET611BM17E_Bosch_Design_Plano_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/14486590_PVQ811F15E_PGA_1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/14486594_PVQ811F15E_PGA_3_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/14486486_PVQ811F15E_STP_def.webp",
            "features": [
                "Integrated ventilation system - no separate chimney needed",
                "4 induction cooking zones with CombiZone",
                "PowerBoost - up to 35% faster heating",
                "AutoOn function - ventilation starts automatically",
                "DirectSelect control - direct zone selection",
                "622 m³/h boost air extraction",
                "Quiet 69 dB operation",
                "Restart function - restores settings",
                "CombiZone - combine zones for large cookware",
                "Timer with auto switch-off",
                "Child lock",
                "Residual heat indicator",
                "Frameless design - 80 cm width",
                "Made in Europe"
            ],
            "specifications": {
                "Dimensions": {
                    "Width": "80 cm",
                    "Installation Type": "Built-in surface mount"
                },
                "Induction Hob": {
                    "Total Zones": "4",
                    "PowerBoost": "Yes - all zones",
                    "CombiZone": "Yes",
                    "Control Type": "DirectSelect",
                    "Frame": "Frameless"
                },
                "Integrated Ventilation": {
                    "Boost Air Extraction": "622 m³/h",
                    "Sound Level": "69 dB",
                    "AutoOn Function": "Yes - automatic start",
                    "Operating Modes": "Ducted / Recirculation"
                },
                "Smart Features": {
                    "Restart Function": "Yes",
                    "Timer with Auto Switch-off": "Yes",
                    "Child Lock": "Yes",
                    "Residual Heat Indicator": "Yes",
                    "Home Connect": "No"
                },
                "Design": {
                    "Color": "Black",
                    "Surface": "Ceramic glass",
                    "Style": "Frameless"
                }
            },
            "highlights": [
                "2-in-1 Solution: Induction hob with integrated downdraft ventilation eliminates need for overhead chimney",
                "AutoOn Ventilation: Smart system automatically starts when hob heats up - no manual intervention needed",
                "CombiZone Flexibility: Combine two zones for large pots, woks, and roasting pans",
                "Powerful Extraction: 622 m³/h removes cooking odors right at the source with 69 dB quiet operation",
                "Premium DirectSelect: Direct zone selection with simple power adjustment",
                "Made in Europe: Premium quality and engineering excellence"
            ],
            "ai_features": {
                "smart_recommendations": "Perfect for open-plan kitchens or islands where overhead chimney installation is not feasible. Ideal for modern minimalist designs.",
                "usage_tips": [
                    "Integrated ventilation extracts odors at cooking surface - more efficient than overhead hoods",
                    "AutoOn ensures ventilation starts automatically when needed",
                    "Use CombiZone for large cookware like woks and roasting pans",
                    "PowerBoost on all zones for fast water boiling",
                    "Frameless design for seamless countertop integration",
                    "Ducted installation provides best performance",
                    "Recirculation mode available with optional filters",
                    "80cm width accommodates multiple large pots simultaneously",
                    "Quiet 69 dB operation won't disturb conversations"
                ],
                "compatibility": "Requires induction-compatible cookware. Integrated ventilation requires ducting or recirculation setup."
            },
            "documents": [
                {
                    "name": "User Manual",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/inductionandelectrohobs/induction-hobs/PVQ811F15E",
                    "description": "Complete user manual with installation and operation instructions"
                },
                {
                    "name": "Installation Instructions",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/inductionandelectrohobs/induction-hobs/PVQ811F15E",
                    "description": "Detailed installation guide for ventilation system"
                },
                {
                    "name": "Product Specification Sheet",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/inductionandelectrohobs/induction-hobs/PVQ811F15E",
                    "description": "Complete technical specifications"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "tags": ["induction hob", "ventilation", "downdraft", "bosch", "series 6", "80cm", "combizone", "powerboost", "made in europe", "premium", "integrated extraction", "frameless"],
            "rating": 0.0,
            "reviews_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "discount_percentage": 10
        },
        
        # Product 2: PXX875D67E - Series 8 Premium with Ventilation
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 8 Induction Hob with Integrated Ventilation 80 cm",
            "model_number": "PXX875D67E",
            "brand": "Bosch",
            "category": "Induction Hob",
            "sub_category": "Ventilation Induction Hob",
            "price": 326990.00,
            "original_price": 363490.00,
            "currency": "INR",
            "stock_quantity": 4,
            "description": "Bosch Series 8 Premium Induction Hob 80 cm with integrated ventilation, FlexInduction zones, Move Mode, Automatic Setting Transfer, PowerBoost, Home Connect, and DirectSelect Premium control. 622 m³/h extraction with elegant frame design.",
            "long_description": "The Bosch PXX875D67E Series 8 represents the pinnacle of cooking technology with integrated ventilation. The 80 cm premium design features FlexInduction for ultimate flexibility with large pots and pans. Move Mode divides zones into three power levels (boiling, cooking, simmering) while Automatic Setting Transfer seamlessly moves your cooking settings when you move cookware. With Home Connect smart connectivity, DirectSelect Premium control, and 622 m³/h extraction, this professional-grade hob eliminates the need for overhead ventilation. The elegant facette frame design with side profiles adds sophistication to any kitchen. Made in Europe with premium craftsmanship.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA03293721_PXX875D67E_ElectricHob_Bosch_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA03296464_PXX875D67E_U_ElectricHob_Bosch_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01058952_DA3_PKC675DP1D_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA03295881_PXX875D67E_ElectricHob_Bosch_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA03295884_PXX875D67E_ElectricHob_Bosch_PGA3_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/MCSA03293721_PXX875D67E_ElectricHob_Bosch_STP_def.webp",
            "features": [
                "Integrated ventilation system - no chimney needed",
                "FlexInduction - ultimate zone flexibility",
                "Move Mode - 3 power levels (boil, cook, simmer)",
                "Automatic Setting Transfer - moves settings with cookware",
                "DirectSelect Premium control",
                "Home Connect - smart connectivity",
                "PowerBoost - 35% faster heating",
                "622 m³/h boost air extraction",
                "Quiet 69 dB operation",
                "4 induction cooking zones",
                "Timer with auto switch-off",
                "Child lock",
                "Residual heat indicator",
                "Elegant facette frame design",
                "Made in Europe"
            ],
            "specifications": {
                "Dimensions": {
                    "Width": "80 cm",
                    "Installation Type": "Built-in surface mount with frame"
                },
                "Induction Hob": {
                    "Total Zones": "4",
                    "FlexInduction": "Yes - flexible zones",
                    "Move Mode": "Yes - 3 power levels",
                    "Automatic Setting Transfer": "Yes",
                    "PowerBoost": "Yes - all zones",
                    "Control Type": "DirectSelect Premium",
                    "Frame": "Facette front+rear, side profiles"
                },
                "Integrated Ventilation": {
                    "Boost Air Extraction": "622 m³/h",
                    "Sound Level": "69 dB",
                    "Operating Modes": "Ducted / Recirculation"
                },
                "Smart Features": {
                    "Home Connect": "Yes - WiFi connectivity",
                    "Move Mode": "Yes - intelligent power zones",
                    "Automatic Transfer": "Yes - settings follow cookware",
                    "Timer with Auto Switch-off": "Yes",
                    "Child Lock": "Yes",
                    "Residual Heat Indicator": "Yes"
                },
                "Design": {
                    "Color": "Black",
                    "Surface": "Ceramic glass",
                    "Style": "Premium facette frame"
                }
            },
            "highlights": [
                "FlexInduction Technology: Flexible cooking zones adapt to any pot or pan size and shape - ultimate versatility",
                "Move Mode Intelligence: Divide zones into boiling, cooking, and simmering areas - just move your pan",
                "Automatic Setting Transfer: Move cookware across hob and settings follow automatically - truly smart cooking",
                "Home Connect: Control and monitor via smartphone app, receive notifications, access recipes",
                "Premium Ventilation: 622 m³/h integrated extraction eliminates overhead chimney with elegant design",
                "DirectSelect Premium: Most advanced touch control with direct zone selection and power adjustment"
            ],
            "ai_features": {
                "smart_recommendations": "Perfect for luxury kitchens, smart homes, and professional home chefs. Ideal for open-plan spaces and islands where design and functionality matter equally.",
                "usage_tips": [
                    "Use Home Connect app to control remotely and receive cooking notifications",
                    "FlexInduction zones accommodate any cookware size - even multiple small pots",
                    "Move Mode: boil at back, cook in center, simmer at front",
                    "Automatic Transfer tracks cookware movement - no need to reset power",
                    "Integrated ventilation more efficient than traditional hoods",
                    "PowerBoost all zones for professional-speed heating",
                    "Premium DirectSelect offers most intuitive control",
                    "Elegant frame design complements premium kitchen aesthetics",
                    "Connect to smart home ecosystem via Home Connect",
                    "Access recipe library and cooking guides through app"
                ],
                "compatibility": "Requires induction-compatible cookware. WiFi for Home Connect. Integrated ventilation requires ducting or recirculation setup."
            },
            "documents": [
                {
                    "name": "User Manual",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/inductionandelectrohobs/induction-hobs/PXX875D67E",
                    "description": "Complete user manual with installation and operation instructions"
                },
                {
                    "name": "Home Connect Guide",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/inductionandelectrohobs/induction-hobs/PXX875D67E",
                    "description": "Setup guide for Home Connect smart features"
                },
                {
                    "name": "Installation Instructions",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/inductionandelectrohobs/induction-hobs/PXX875D67E",
                    "description": "Detailed installation guide for ventilation system"
                },
                {
                    "name": "Product Specification Sheet",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/inductionandelectrohobs/induction-hobs/PXX875D67E",
                    "description": "Complete technical specifications"
                },
                {
                    "name": "Cookbook",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/inductionandelectrohobs/induction-hobs/PXX875D67E",
                    "description": "Recipe collection and cooking tips"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "tags": ["induction hob", "ventilation", "downdraft", "bosch", "series 8", "80cm", "flexinduction", "move mode", "home connect", "smart", "premium", "made in europe", "integrated extraction"],
            "rating": 0.0,
            "reviews_count": 0,
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
            print(f"   Series: {product['model_number'][:3]}")
            print(f"   Price: ₹{product['price']:,.2f} (was ₹{product['original_price']:,.2f})")
            print(f"   Category: {product['category']} - {product['sub_category']}")
            print(f"   Key Feature: Integrated Ventilation (622 m³/h)")
            print(f"   Images: {len(product['images'])} images added")
            print()
        
    except Exception as e:
        print(f"❌ Error adding products: {e}")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_premium_ventilation_hobs())