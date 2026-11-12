import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_60cm_gas_hobs():
    """Add 3 Bosch 60cm Gas Hobs to the database"""
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    if not mongo_url:
        print("❌ MONGO_URL not found in environment variables")
        return
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    products_collection = db.products
    
    products = [
        # Product 1: PGH6B5B60I - Stainless Steel 4 Burner
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 4 Gas Hob 60 cm - Stainless Steel",
            "model_number": "PGH6B5B60I",
            "brand": "Bosch",
            "category": "Gas Hob",
            "sub_category": "Built-in Gas Hob 60cm",
            "price": 18990.00,
            "original_price": 20990.00,
            "currency": "INR",
            "stock_quantity": 25,
            "description": "Bosch Series 4 Gas Hob 60 cm with 4 burners, elegant stainless steel surface, Tilt & Stay legs for easy cleaning - 1st in India. Frameless design with cast iron pan supports.",
            "long_description": "The Bosch PGH6B5B60I Series 4 Gas Hob combines elegant stainless steel design with practical features. Featuring 4 burners with frameless design and innovative Tilt & Stay legs - a first in India - making cooktop cleaning effortless. The cast iron pan supports with rubber feet ensure stability while the premium stainless steel surface provides durability and easy maintenance. Made in Europe with Bosch quality, this hob is perfect for everyday cooking needs.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01690570_PGH6B5B60_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01797988_PGH6B5B60_GasHob_build-in_Bosch_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01798042_PGH6B5B60_GasHob_build-in_Bosch_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01832981_PGH6B5B60_GasHob_build-in_Bosch_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01798027_PGH6B5B60_GasHob_build-in_Bosch_PGA4_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/MCSA01690570_PGH6B5B60_def.webp",
            "features": [
                "4 powerful gas burners",
                "Premium stainless steel surface",
                "Frameless design",
                "Tilt & Stay legs - 1st in India for easy cleaning",
                "Cast iron pan supports with rubber feet",
                "Made in Europe",
                "60 cm standard width",
                "Suitable for LPG and natural gas",
                "Elegant stainless steel design",
                "Easy to clean surface"
            ],
            "specifications": {
                "Dimensions": {
                    "Width": "60 cm",
                    "Cooktop Type": "Gas cooktop"
                },
                "Burners": {
                    "Total Burners": "4",
                    "Pan Support Material": "Cast iron with rubber feet"
                },
                "Design": {
                    "Surface Material": "Stainless steel",
                    "Frame Type": "Frameless"
                },
                "Gas": {
                    "Gas Type": "LPG G30,31",
                    "Pressure": "28-30/37 mbar",
                    "Alternative Gas": "Natural gas H/E/(L) 20 (25) mbar included"
                },
                "Installation": {
                    "Type": "Built-in",
                    "Style": "Standard 60cm"
                },
                "Special Features": {
                    "Tilt & Stay Legs": "Yes - 1st in India"
                }
            },
            "highlights": [
                "Tilt & Stay Legs: Industry-first in India - legs tilt for easy cleaning of cooktop surface",
                "Elegant Stainless Steel: Premium finish that matches modern kitchen aesthetics",
                "Frameless Design: Seamless integration with countertop",
                "4 Burner Configuration: Versatile cooking with multiple burner sizes",
                "Made in Europe: Premium Bosch quality and craftsmanship",
                "Cast Iron Supports: Durable pan supports with rubber feet for stability"
            ],
            "ai_features": {
                "smart_recommendations": "Perfect for standard 60cm kitchens. Ideal for families of 3-5 people with regular cooking needs.",
                "usage_tips": [
                    "Use Tilt & Stay feature for hassle-free cleaning",
                    "Stainless steel surface wipes clean easily",
                    "Four burners accommodate simultaneous cooking",
                    "Cast iron supports handle heavy cookware",
                    "Works with both LPG and natural gas",
                    "Frameless design prevents dirt accumulation"
                ],
                "compatibility": "Requires LPG or natural gas connection. Standard 60cm cutout."
            },
            "documents": [
                {
                    "name": "User Manual",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/gas-hobs-60-cm/PGH6B5B60I",
                    "description": "Complete user manual with installation and operation instructions"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "tags": ["gas hob", "60cm", "bosch", "series 4", "stainless steel", "4 burner", "frameless", "tilt stay", "made in europe"],
            "rating": 1.0,
            "reviews_count": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "discount_percentage": 10
        },
        
        # Product 2: PNC6B6F10I - Tempered Glass Black 3 Burner
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 4 Gas Hob 60 cm - Tempered Glass Black",
            "model_number": "PNC6B6F10I",
            "brand": "Bosch",
            "category": "Gas Hob",
            "sub_category": "Built-in Gas Hob 60cm",
            "price": 30990.00,
            "original_price": 34490.00,
            "currency": "INR",
            "stock_quantity": 15,
            "description": "Bosch Series 4 Gas Hob 60 cm with premium 6mm tempered glass in elegant black. Features 3 burners, low profile design, and matt enamel pan supports for easy cleaning.",
            "long_description": "The Bosch PNC6B6F10I Series 4 Gas Hob features premium 6mm tempered glass surface in elegant black finish. With 3 powerful burners and low profile stainless steel cooking surface, it offers easy accessibility and quick cleaning. The matt enamel pan supports provide durability while the tempered glass ensures safety and style. Made in Europe with Bosch quality, this hob combines aesthetics with functionality.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/19898034_PNC6B6F10I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20630262_PNC6B6F10I_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20791852_PNC6B6F10I_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20808525_PNC6B6F10I_PGA5_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20808658_PNC6B6F10I_PGA4_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/19898034_PNC6B6F10I_STP_def.webp",
            "features": [
                "3 powerful gas burners",
                "Premium 6mm tempered glass surface",
                "Elegant black finish",
                "Low profile design",
                "Matt enamel pan supports",
                "Made in Europe",
                "60 cm standard width",
                "Suitable for LPG and natural gas",
                "Easy to clean tempered glass",
                "Quick accessibility"
            ],
            "specifications": {
                "Dimensions": {
                    "Width": "60 cm",
                    "Cooktop Type": "Gas cooktop"
                },
                "Burners": {
                    "Total Burners": "3",
                    "Pan Support Material": "Matt enamel"
                },
                "Design": {
                    "Surface Material": "Tempered glass - 6mm",
                    "Color": "Black"
                },
                "Gas": {
                    "Gas Type": "LPG G30,31",
                    "Pressure": "28-30/37 mbar",
                    "Alternative Gas": "Natural gas H/E/(L) 20 (25) mbar included"
                },
                "Installation": {
                    "Type": "Built-in",
                    "Style": "Standard 60cm"
                },
                "Special Features": {
                    "Low Profile Design": "Yes"
                }
            },
            "highlights": [
                "Premium Tempered Glass: 6mm thick tempered glass ensures safety and durability",
                "Elegant Black Finish: Modern aesthetics that complement contemporary kitchens",
                "Low Profile Design: Easily accessible cooking surface for quick cleaning",
                "3 Burner Efficiency: Perfect for compact cooking needs",
                "Made in Europe: Premium Bosch quality and craftsmanship",
                "Matt Enamel Supports: Easy-to-clean pan supports"
            ],
            "ai_features": {
                "smart_recommendations": "Ideal for small to medium families or apartments with 60cm standard kitchens.",
                "usage_tips": [
                    "Tempered glass cleans with a damp cloth",
                    "Low profile design allows easy access",
                    "Three burners sufficient for daily cooking",
                    "Black finish hides minor stains",
                    "Works with both LPG and natural gas",
                    "Matt enamel supports wipe clean easily"
                ],
                "compatibility": "Requires LPG or natural gas connection. Standard 60cm cutout."
            },
            "documents": [
                {
                    "name": "User Manual",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/gas-hobs-60-cm/PNC6B6F10I",
                    "description": "Complete user manual with installation and operation instructions"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "tags": ["gas hob", "60cm", "bosch", "series 4", "tempered glass", "black", "3 burner", "made in europe"],
            "rating": 1.0,
            "reviews_count": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "discount_percentage": 10
        },
        
        # Product 3: PNH6B6F20I - Tempered Glass Black 4 Burner with Cast Iron
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 4 Gas Hob 60 cm - Premium Tempered Glass Black",
            "model_number": "PNH6B6F20I",
            "brand": "Bosch",
            "category": "Gas Hob",
            "sub_category": "Built-in Gas Hob 60cm",
            "price": 39990.00,
            "original_price": 44490.00,
            "currency": "INR",
            "stock_quantity": 20,
            "description": "Bosch Series 4 Gas Hob 60 cm with premium 6mm tempered glass in black. Features 4 powerful burners with cast iron supports, full BTU range performance, and low profile design.",
            "long_description": "The Bosch PNH6B6F20I Series 4 Gas Hob represents premium gas cooking with 6mm tempered glass surface in elegant black. Featuring 4 powerful gas burners with cast iron single pan supports, it allows cooking multiple dishes with full range BTU performance. The low profile stainless steel cooking surface is easily accessible and quick to clean. Made in Europe with Bosch quality, this hob is perfect for families who love to cook.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/19898048_PNH6B6F20I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20630341_PNH6B6F20I_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20808045_PNH6B6F20I_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01753946_PPQ7A6B90_GasHob_build-in_Bosch_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790939_PNH6B6F20I_PGA1_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/19898048_PNH6B6F20I_STP_def.webp",
            "features": [
                "4 powerful gas burners",
                "Premium 6mm tempered glass surface",
                "Elegant black finish",
                "Cast iron single pan supports",
                "Full BTU range performance",
                "Low profile design",
                "Made in Europe",
                "60 cm standard width",
                "Suitable for LPG and natural gas",
                "Multiple dish cooking capability",
                "Easy to clean surface"
            ],
            "specifications": {
                "Dimensions": {
                    "Width": "60 cm",
                    "Cooktop Type": "Gas cooktop"
                },
                "Burners": {
                    "Total Burners": "4",
                    "Pan Support Material": "Cast iron single"
                },
                "Design": {
                    "Surface Material": "Tempered glass - 6mm",
                    "Color": "Black"
                },
                "Gas": {
                    "Gas Type": "LPG G30,31",
                    "Pressure": "28-30/37 mbar",
                    "Alternative Gas": "Natural gas H/E/(L) 20 (25) mbar included"
                },
                "Installation": {
                    "Type": "Built-in",
                    "Style": "Standard 60cm"
                },
                "Special Features": {
                    "Low Profile Design": "Yes",
                    "Full BTU Range": "Yes"
                }
            },
            "highlights": [
                "Premium 4 Burner Configuration: Cook multiple dishes simultaneously with full BTU range",
                "6mm Tempered Glass: Premium thick glass ensures safety and durability",
                "Cast Iron Pan Supports: Heavy-duty single-piece supports for maximum stability",
                "Full BTU Performance: From gentle simmering to high-heat cooking",
                "Elegant Black Finish: Modern aesthetics with easy-to-clean surface",
                "Made in Europe: Premium Bosch quality with 2.2/5 rating from 6 reviews"
            ],
            "ai_features": {
                "smart_recommendations": "Perfect for families of 4-6 people who cook multiple dishes. Ideal for Indian cooking needs.",
                "usage_tips": [
                    "Four burners allow simultaneous cooking of full meals",
                    "Full BTU range handles everything from dal to tandoori",
                    "Tempered glass cleans with a damp cloth",
                    "Cast iron supports handle heavy pressure cookers",
                    "Low profile design for easy pot handling",
                    "Works with both LPG and natural gas",
                    "Black finish hides usage marks"
                ],
                "compatibility": "Requires LPG or natural gas connection. Standard 60cm cutout."
            },
            "documents": [
                {
                    "name": "User Manual",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/gas-hobs-60-cm/PNH6B6F20I",
                    "description": "Complete user manual with installation and operation instructions"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "tags": ["gas hob", "60cm", "bosch", "series 4", "tempered glass", "black", "4 burner", "cast iron", "made in europe", "premium"],
            "rating": 2.2,
            "reviews_count": 6,
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
            print(f"   Burners: {product['specifications']['Burners']['Total Burners']}")
            print(f"   Surface: {product['specifications']['Design']['Surface Material']}")
            print(f"   Price: ₹{product['price']:,.2f} (was ₹{product['original_price']:,.2f})")
            if product['rating'] > 0:
                print(f"   Rating: ⭐{product['rating']}/5.0 ({product['reviews_count']} reviews)")
            print(f"   Images: {len(product['images'])} images added")
            print()
        
    except Exception as e:
        print(f"❌ Error adding products: {e}")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_60cm_gas_hobs())
