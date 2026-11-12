import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

load_dotenv()

async def add_bosch_75cm_gas_hobs():
    """Add 3 Bosch 75cm Gas Hobs to the database"""
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    if not mongo_url:
        print("❌ MONGO_URL not found in environment variables")
        return
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    products_collection = db.products
    
    products = [
        # Product 1: PND7B6F20I - Series 6, 3 Burner
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Gas Hob 75 cm - Tempered Glass Black",
            "model_number": "PND7B6F20I",
            "brand": "Bosch",
            "category": "Gas Hob",
            "sub_category": "Built-in Gas Hob 75cm",
            "price": 45490.00,
            "original_price": 50490.00,
            "currency": "INR",
            "stock_quantity": 12,
            "description": "Bosch Series 6 Gas Hob 75 cm with premium 6mm tempered glass in black. Features 3 burners with cast iron supports, low profile design for easy accessibility and quick cleaning.",
            "long_description": "The Bosch PND7B6F20I Series 6 Gas Hob offers premium 75 cm cooking space with elegant 6mm tempered glass surface in black. Featuring 3 powerful burners with cast iron single pan supports, this hob combines style with functionality. The low profile stainless steel cooking surface is easily accessible and quick to clean. Made in Europe with Bosch quality, ideal for kitchens requiring wider cooking area.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/19898030_PND7B6F20I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790564_PND7B6F20I_PGA5_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790600_PND7B6F20I_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20807770_PND7B6F20I_PGA3_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/MCSA01753946_PPQ7A6B90_GasHob_build-in_Bosch_PGA2_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/19898030_PND7B6F20I_STP_def.webp",
            "features": [
                "3 powerful gas burners",
                "Premium 6mm tempered glass surface",
                "Elegant black finish",
                "Cast iron single pan supports",
                "Low profile design",
                "75 cm wide cooking area",
                "Made in Europe",
                "Suitable for LPG and natural gas",
                "Easy to clean tempered glass",
                "Series 6 premium quality"
            ],
            "specifications": {
                "Dimensions": {
                    "Width": "75 cm",
                    "Cooktop Type": "Gas cooktop"
                },
                "Burners": {
                    "Total Burners": "3",
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
                    "Style": "Standard 75cm"
                },
                "Special Features": {
                    "Low Profile Design": "Yes"
                }
            },
            "highlights": [
                "Wider 75cm Cooking Space: Extra width provides flexibility for larger pots and multiple dishes",
                "Premium Tempered Glass: 6mm thick glass ensures safety and durability",
                "Series 6 Quality: Higher-tier Bosch series with premium features",
                "Cast Iron Supports: Heavy-duty single-piece supports for stability",
                "Low Profile Design: Easily accessible cooking surface",
                "Made in Europe: Premium Bosch craftsmanship"
            ],
            "ai_features": {
                "smart_recommendations": "Perfect for families with spacious kitchens needing extra cooking width. Ideal for 4-6 people.",
                "usage_tips": [
                    "75cm width accommodates larger cookware",
                    "Three burners sufficient for most cooking needs",
                    "Tempered glass cleans easily with damp cloth",
                    "Cast iron supports handle heavy pots",
                    "Low profile design for easy pot handling",
                    "Works with both LPG and natural gas",
                    "Series 6 offers better build quality"
                ],
                "compatibility": "Requires LPG or natural gas connection. 75cm cutout required."
            },
            "documents": [
                {
                    "name": "User Manual",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/gas-hobs-75-cm/PND7B6F20I",
                    "description": "Complete user manual with installation instructions"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "tags": ["gas hob", "75cm", "bosch", "series 6", "tempered glass", "black", "3 burner", "cast iron", "made in europe"],
            "rating": 0.0,
            "reviews_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "discount_percentage": 10
        },
        
        # Product 2: PND7B6G20I - Series 6, 3 Burner
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Gas Hob 75 cm - Premium Tempered Glass Black",
            "model_number": "PND7B6G20I",
            "brand": "Bosch",
            "category": "Gas Hob",
            "sub_category": "Built-in Gas Hob 75cm",
            "price": 50490.00,
            "original_price": 55990.00,
            "currency": "INR",
            "stock_quantity": 10,
            "description": "Bosch Series 6 Gas Hob 75 cm with premium 6mm tempered glass in black. Features 3 burners with cast iron supports, low profile design with elegant styling.",
            "long_description": "The Bosch PND7B6G20I Series 6 Gas Hob represents premium cooking with 75 cm width and elegant 6mm tempered glass surface. Featuring 3 powerful burners with cast iron single pan supports, this hob offers versatile cooking in a stylish package. The low profile stainless steel cooking surface ensures easy accessibility and quick cleaning. Made in Europe with Series 6 premium quality.",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/19898029_PND7B6G20I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790467_PND7B6G20I_PGA2_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790491_PND7B6G20I_PGA5_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790494_PND7B6G20I_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790495_PND7B6G20I_PGA1_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/19898029_PND7B6G20I_STP_def.webp",
            "features": [
                "3 powerful gas burners",
                "Premium 6mm tempered glass surface",
                "Elegant black finish",
                "Cast iron single pan supports",
                "Low profile design",
                "75 cm wide cooking area",
                "Made in Europe",
                "Suitable for LPG and natural gas",
                "Easy to clean surface",
                "Series 6 premium quality"
            ],
            "specifications": {
                "Dimensions": {
                    "Width": "75 cm",
                    "Cooktop Type": "Gas cooktop"
                },
                "Burners": {
                    "Total Burners": "3",
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
                    "Style": "Standard 75cm"
                },
                "Special Features": {
                    "Low Profile Design": "Yes"
                }
            },
            "highlights": [
                "Premium 75cm Width: Extra cooking space for versatile meal preparation",
                "6mm Tempered Glass: Premium thick glass with safety and durability",
                "Series 6 Excellence: Higher-tier quality with refined features",
                "Cast Iron Supports: Heavy-duty stability for all cookware",
                "Elegant Black Finish: Modern aesthetics that complement premium kitchens",
                "Made in Europe: Premium Bosch craftsmanship and reliability"
            ],
            "ai_features": {
                "smart_recommendations": "Ideal for premium kitchens with 75cm space. Perfect for families of 4-6 people.",
                "usage_tips": [
                    "75cm width provides extra flexibility",
                    "Three burners handle daily cooking efficiently",
                    "Tempered glass maintains elegant appearance",
                    "Cast iron supports for heavy cookware",
                    "Low profile for comfortable cooking",
                    "Compatible with LPG and natural gas",
                    "Premium Series 6 build quality"
                ],
                "compatibility": "Requires LPG or natural gas connection. 75cm cutout required."
            },
            "documents": [
                {
                    "name": "User Manual",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/gas-hobs-75-cm/PND7B6G20I",
                    "description": "Complete user manual with installation instructions"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "tags": ["gas hob", "75cm", "bosch", "series 6", "tempered glass", "black", "3 burner", "cast iron", "made in europe", "premium"],
            "rating": 0.0,
            "reviews_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "discount_percentage": 10
        },
        
        # Product 3: PNI7B6G20I - Series 6, 4 Burner - Best Deal
        {
            "id": str(uuid.uuid4()),
            "name": "Bosch Series 6 Gas Hob 75 cm - 4 Burner Tempered Glass Black",
            "model_number": "PNI7B6G20I",
            "brand": "Bosch",
            "category": "Gas Hob",
            "sub_category": "Built-in Gas Hob 75cm",
            "price": 42490.00,
            "original_price": 56490.00,
            "currency": "INR",
            "stock_quantity": 15,
            "description": "Bosch Series 6 Gas Hob 75 cm with 4 burners, premium 6mm tempered glass in black. Features cast iron supports, full BTU range performance, low profile design - Best value!",
            "long_description": "The Bosch PNI7B6G20I Series 6 Gas Hob offers exceptional value with 75 cm width and 4 powerful burners. Featuring premium 6mm tempered glass surface in elegant black, this hob allows cooking multiple dishes with full range BTU performance. The cast iron single pan supports ensure stability while the low profile stainless steel cooking surface is easily accessible and quick to clean. Made in Europe with Series 6 quality - offering the best value in the 75cm category!",
            "images": [
                "https://media3.bsh-group.com/Product_Shots/900x/19898043_PNI7B6G20I_STP_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20630780_PNI7B6G20I_PGA4_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20630782_PNI7B6G20I_PGA1_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790314_PNI7B6G20I_PGA3_GROUP4B_15_def.webp",
                "https://media3.bsh-group.com/Product_Shots/900x/20790317_PNI7B6G20I_PGA5_def.webp"
            ],
            "thumbnail": "https://media3.bsh-group.com/Product_Shots/900x/19898043_PNI7B6G20I_STP_def.webp",
            "features": [
                "4 powerful gas burners",
                "Premium 6mm tempered glass surface",
                "Elegant black finish",
                "Cast iron single pan supports",
                "Full BTU range performance",
                "Low profile design",
                "75 cm wide cooking area",
                "Made in Europe",
                "Suitable for LPG and natural gas",
                "Multiple dish cooking capability",
                "Best value - Save 25%!"
            ],
            "specifications": {
                "Dimensions": {
                    "Width": "75 cm",
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
                    "Style": "Standard 75cm"
                },
                "Special Features": {
                    "Low Profile Design": "Yes",
                    "Full BTU Range": "Yes"
                }
            },
            "highlights": [
                "Best Value 75cm Hob: 4 burners at exceptional price - Save ₹14,000!",
                "Premium 4 Burner Configuration: Cook multiple dishes simultaneously with full BTU range",
                "75cm Extra Space: Wider cooking area perfect for large families",
                "6mm Tempered Glass: Premium thick glass with black elegance",
                "Cast Iron Supports: Heavy-duty stability for all cookware types",
                "Made in Europe: Premium Bosch Series 6 quality at unbeatable price"
            ],
            "ai_features": {
                "smart_recommendations": "Best value for families! 4 burners + 75cm width at lowest price. Perfect for 5-7 people or heavy cooking needs.",
                "usage_tips": [
                    "Four burners allow complete meal preparation",
                    "75cm width accommodates large cookware",
                    "Full BTU range handles all cooking styles",
                    "Excellent value - most burners for the price",
                    "Tempered glass easy to maintain",
                    "Cast iron supports handle pressure cookers",
                    "Low profile for comfortable cooking",
                    "Works with both LPG and natural gas",
                    "Best buy in 75cm category"
                ],
                "compatibility": "Requires LPG or natural gas connection. 75cm cutout required."
            },
            "documents": [
                {
                    "name": "User Manual",
                    "type": "PDF",
                    "url": "https://www.bosch-home.in/en/product/cooking-baking/gas-hobs/gas-hobs-75-cm/PNI7B6G20I",
                    "description": "Complete user manual with installation instructions"
                }
            ],
            "warranty": "2 years manufacturer warranty",
            "tags": ["gas hob", "75cm", "bosch", "series 6", "tempered glass", "black", "4 burner", "cast iron", "made in europe", "best value", "premium"],
            "rating": 0.0,
            "reviews_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "discount_percentage": 25
        }
    ]
    
    try:
        for product in products:
            result = await products_collection.insert_one(product)
            print(f"✅ Successfully added {product['name']}")
            print(f"   Product ID: {product['id']}")
            print(f"   Model: {product['model_number']}")
            print(f"   Burners: {product['specifications']['Burners']['Total Burners']}")
            print(f"   Price: ₹{product['price']:,.2f} (Save {product['discount_percentage']}% - was ₹{product['original_price']:,.2f})")
            print(f"   Stock: {product['stock_quantity']} units")
            print(f"   Images: {len(product['images'])} images added")
            print()
        
    except Exception as e:
        print(f"❌ Error adding products: {e}")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_bosch_75cm_gas_hobs())
