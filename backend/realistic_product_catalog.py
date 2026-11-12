# Realistic Product Catalog for Aditya Retail
# Based on actual brands: Bosch, Siemens, Hindware + Bosch Power Tools & Care Products

import uuid
import random

# Realistic Brand Portfolio
REALISTIC_BRANDS = {
    "bosch": {
        "name": "Bosch",
        "description": "German engineering excellence in home appliances",
        "country": "Germany",
        "categories": ["appliances", "power_tools", "care_products"],
        "warranty": "2 Years",
        "premium_factor": 1.3
    },
    "siemens": {
        "name": "Siemens", 
        "description": "Premium German technology for modern homes",
        "country": "Germany",
        "categories": ["appliances"],
        "warranty": "3 Years",
        "premium_factor": 1.4
    },
    "hindware": {
        "name": "Hindware",
        "description": "Leading Indian brand for kitchen and bath solutions",
        "country": "India", 
        "categories": ["appliances", "sinks", "faucets", "geysers"],
        "warranty": "2 Years",
        "premium_factor": 1.0
    }
}

# Realistic Categories Structure
REALISTIC_CATEGORIES = {
    "appliances": {
        "microwaves": {
            "name": "Microwaves",
            "subcategories": ["Built-in Microwave", "Countertop Microwave", "Convection Microwave"]
        },
        "refrigerators": {
            "name": "Refrigerators", 
            "subcategories": ["Single Door Fridge", "Double Door Fridge", "Side by Side", "Bottom Freezer"]
        },
        "washing_machines": {
            "name": "Washing Machines",
            "subcategories": ["Front Load", "Top Load", "Washer Dryer Combo"]
        },
        "dishwashers": {
            "name": "Dishwashers",
            "subcategories": ["Built-in Dishwasher", "Freestanding Dishwasher", "Compact Dishwasher"]
        },
        "cooktops": {
            "name": "Cooktops",
            "subcategories": ["Induction Cooktop", "Gas Hob", "Electric Cooktop"]
        },
        "ovens": {
            "name": "Ovens", 
            "subcategories": ["Built-in Oven", "Steam Oven", "Combination Oven"]
        },
        "chimneys": {
            "name": "Chimneys",
            "subcategories": ["Wall Mount Chimney", "Island Chimney", "Built-in Hood"]
        }
    },
    "sinks": {
        "kitchen_sinks": {
            "name": "Kitchen Sinks",
            "subcategories": ["Stainless Steel Sinks", "Granite Sinks", "Undermount Sinks", "Designer Sinks"]
        }
    },
    "faucets": {
        "kitchen_faucets": {
            "name": "Kitchen Faucets", 
            "subcategories": ["Single Lever Faucets", "Wall Mount Faucets", "Sensor Faucets"]
        },
        "bathroom_faucets": {
            "name": "Bathroom Faucets",
            "subcategories": ["Basin Faucets", "Shower Faucets", "Bath Fittings"]
        }
    },
    "geysers": {
        "water_heaters": {
            "name": "Water Heaters",
            "subcategories": ["Electric Geysers", "Gas Geysers", "Solar Water Heaters", "Instant Water Heaters"]
        }
    },
    "power_tools": {
        "drilling": {
            "name": "Drilling Tools",
            "subcategories": ["Drill Machines", "Impact Drills", "Hammer Drills", "Cordless Drills"]
        },
        "cutting": {
            "name": "Cutting Tools", 
            "subcategories": ["Angle Grinders", "Circular Saws", "Jigsaw", "Multi Cutter"]
        },
        "measuring": {
            "name": "Measuring Tools",
            "subcategories": ["Laser Measures", "Digital Levels", "Measuring Tapes"]
        }
    },
    "care_products": {
        "detergents": {
            "name": "Detergents",
            "subcategories": ["Washing Machine Detergent", "Dishwasher Detergent", "Fabric Softener"]
        },
        "cleaners": {
            "name": "Cleaners", 
            "subcategories": ["Drum Cleaners", "Descaling Agents", "Glass Cleaners", "Appliance Cleaners"]
        }
    }
}

# High-quality product images (organized by category)
PRODUCT_IMAGES = {
    "microwaves": [
        "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=500&h=500&fit=crop",
        "https://images.unsplash.com/photo-1626143508000-4b5904e5e84a?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=500&h=500&fit=crop"
    ],
    "refrigerators": [
        "https://images.unsplash.com/photo-1484154218962-a197022b5858?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=500&h=500&fit=crop"
    ],
    "washing_machines": [
        "https://images.unsplash.com/photo-1626806819282-2c1dc01a5e0c?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=500&h=500&fit=crop",
        "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=500&h=500&fit=crop"
    ],
    "cooktops": [
        "https://images.unsplash.com/photo-1629234356883-c37e616a2d43?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=500&h=500&fit=crop"
    ],
    "hoods": [
        "https://images.unsplash.com/photo-1556908493-4ac5f138ab77?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=500&h=500&fit=crop"
    ],
    "kitchen_setup": [
        "https://images.unsplash.com/photo-1722942722302-3e8a6dd7e77c?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=500&h=500&fit=crop"
    ],
    "default": [
        "https://images.unsplash.com/photo-1722942722302-3e8a6dd7e77c?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=500&h=500&fit=crop"
    ]
}

# Realistic Product Templates with Series Names
BOSCH_SERIES = ["Serie 2", "Serie 4", "Serie 6", "Serie 8", "iQ300", "iQ500", "iQ700"]
SIEMENS_SERIES = ["iQ100", "iQ300", "iQ500", "iQ700", "studioline", "avantgarde"] 
HINDWARE_SERIES = ["Elanza", "Senzo", "Calisto", "Chimera", "Atlantic", "Snowcrest"]

# Realistic Product Data
REALISTIC_PRODUCTS = {
    # BOSCH APPLIANCES
    "bosch_appliances": {
        "microwaves": [
            {
                "name_template": "Bosch {series} Built-in Microwave {capacity}L {color}",
                "capacities": [20, 25, 28, 32, 38, 45],
                "price_range": (25000, 85000),
                "features": ["AutoPilot Programs", "LED Display", "Child Lock", "Stainless Steel Interior", "QuickStart"]
            }
        ],
        "refrigerators": [
            {
                "name_template": "Bosch {series} {type} Refrigerator {capacity}L {features}",
                "types": ["Double Door", "Side by Side", "Bottom Freezer"],
                "capacities": [215, 260, 310, 385, 450, 565],
                "price_range": (25000, 150000),
                "features": ["VitaFresh Technology", "NoFrost", "LED Lighting", "Digital Temperature Control"]
            }
        ],
        "washing_machines": [
            {
                "name_template": "Bosch {series} {type} Washing Machine {capacity}KG",
                "types": ["Front Load", "Top Load"],
                "capacities": [6, 7, 8, 9, 10],
                "price_range": (25000, 75000),
                "features": ["EcoSilence Drive", "ActiveWater Plus", "AllergyPlus", "SpeedPerfect"]
            }
        ],
        "dishwashers": [
            {
                "name_template": "Bosch {series} Dishwasher {place_settings} Place Settings {features}",
                "place_settings": [12, 13, 14, 15],
                "price_range": (35000, 120000),
                "features": ["AquaStop", "VarioDrawer", "EcoSilence Drive", "Glass Protection"]
            }
        ]
    },
    
    # SIEMENS APPLIANCES  
    "siemens_appliances": {
        "microwaves": [
            {
                "name_template": "Siemens {series} Built-in Microwave {capacity}L {color}",
                "capacities": [25, 32, 38, 45],
                "price_range": (35000, 120000),
                "features": ["cookControl Plus", "LED Display", "AutoPilot", "Ceramic Base"]
            }
        ],
        "ovens": [
            {
                "name_template": "Siemens {series} Built-in Oven {capacity}L {features}",
                "capacities": [65, 71, 85], 
                "price_range": (45000, 200000),
                "features": ["activeClean", "coolStart", "LED Lighting", "TFT Display"]
            }
        ]
    },
    
    # HINDWARE PRODUCTS
    "hindware_products": {
        "appliances": [
            {
                "name_template": "Hindware {series} Built-in Microwave {capacity}L",
                "capacities": [20, 25, 28],
                "price_range": (15000, 45000),
                "features": ["Multi-stage Cooking", "LED Display", "Auto Cook Menus"]
            }
        ],
        "sinks": [
            {
                "name_template": "Hindware {series} {material} Kitchen Sink {size}",
                "materials": ["Stainless Steel", "Granite", "Quartz"],
                "sizes": ["Single Bowl", "Double Bowl", "Triple Bowl"],
                "price_range": (5000, 25000),
                "features": ["Anti-Bacterial Coating", "Sound Dampening", "Easy Clean Surface"]
            }
        ],
        "faucets": [
            {
                "name_template": "Hindware {series} {type} Faucet {finish}",
                "types": ["Single Lever", "Wall Mount", "Sensor"],
                "finishes": ["Chrome", "Matt Black", "Brushed Steel"],
                "price_range": (2000, 15000),
                "features": ["Ceramic Cartridge", "360° Swivel", "Water Saving", "Leak Proof"]
            }
        ],
        "geysers": [
            {
                "name_template": "Hindware {series} Electric Geyser {capacity}L {features}",
                "capacities": [10, 15, 25, 35, 50],
                "price_range": (8000, 30000),
                "features": ["Magnesium Anode", "Glass Lined Tank", "ISI Certified", "Auto Cut-off"]
            }
        ]
    },
    
    # BOSCH POWER TOOLS
    "bosch_power_tools": {
        "drilling": [
            {
                "name_template": "Bosch {series} {type} {power}W Professional",
                "types": ["Drill Machine", "Impact Drill", "Hammer Drill", "Cordless Drill"],
                "power": [500, 600, 700, 850, 1050],
                "price_range": (2000, 25000),
                "features": ["Keyless Chuck", "Variable Speed", "Reverse Function", "LED Light"]
            }
        ],
        "cutting": [
            {
                "name_template": "Bosch {series} Angle Grinder {disc_size}mm {power}W",
                "disc_sizes": [100, 125, 150, 180, 230],
                "power": [650, 850, 1200, 1400, 2000],
                "price_range": (3000, 18000),
                "features": ["Vibration Control", "Tool-free Guard", "Soft Grip", "Overload Protection"]
            }
        ]
    },
    
    # BOSCH CARE PRODUCTS
    "bosch_care": {
        "detergents": [
            {
                "name_template": "Bosch {type} Detergent {size}",
                "types": ["Washing Machine", "Dishwasher"],
                "sizes": ["500ml", "1L", "2L"],
                "price_range": (200, 1500),
                "features": ["Enzyme Formula", "Color Protection", "Fresh Fragrance", "Eco-Friendly"]
            }
        ],
        "cleaners": [
            {
                "name_template": "Bosch {type} Cleaner {size}",
                "types": ["Drum", "Descaling", "Glass", "Appliance"],
                "sizes": ["250ml", "500ml", "1L"],
                "price_range": (150, 800),
                "features": ["Deep Cleaning", "Limescale Removal", "Safe Formula", "Professional Grade"]
            }
        ]
    }
}

def generate_realistic_product(brand, category, subcategory, product_data, index):
    """Generate a realistic product based on actual brand portfolio"""
    
    brand_info = REALISTIC_BRANDS[brand]
    
    # Select appropriate series
    if brand == "bosch":
        series = random.choice(BOSCH_SERIES)
    elif brand == "siemens":
        series = random.choice(SIEMENS_SERIES) 
    else:  # hindware
        series = random.choice(HINDWARE_SERIES)
    
    # Generate product name
    template = product_data["name_template"]
    name_vars = {"series": series}
    
    # Add capacity/size if applicable
    if "capacities" in product_data:
        name_vars["capacity"] = random.choice(product_data["capacities"])
    if "sizes" in product_data:
        name_vars["size"] = random.choice(product_data["sizes"])
    if "power" in product_data:
        name_vars["power"] = random.choice(product_data["power"])
    if "types" in product_data:
        name_vars["type"] = random.choice(product_data["types"])
    if "materials" in product_data:
        name_vars["material"] = random.choice(product_data["materials"])
    if "finishes" in product_data:
        name_vars["finish"] = random.choice(product_data["finishes"])
    if "disc_sizes" in product_data:
        name_vars["disc_size"] = random.choice(product_data["disc_sizes"])
    if "place_settings" in product_data:
        name_vars["place_settings"] = random.choice(product_data["place_settings"])
        
    # Add common variables
    name_vars.update({
        "color": random.choice(["Black", "White", "Silver", "Stainless Steel"]),
        "features": random.choice(["Smart", "Pro", "Elite", "Premium", "Digital"])
    })
    
    try:
        name = template.format(**name_vars)
    except KeyError:
        # Fallback if template has variables not in our dict
        name = f"{brand_info['name']} {series} {subcategory} {index}"
    
    # Generate price with brand premium
    min_price, max_price = product_data["price_range"]
    premium = brand_info["premium_factor"]
    price = int(random.randint(min_price, max_price) * premium)
    original_price = int(price * random.uniform(1.1, 1.25)) if random.random() > 0.4 else None
    
    # Select images
    image_key = subcategory if subcategory in PRODUCT_IMAGES else "default"
    images = PRODUCT_IMAGES[image_key]
    
    # Generate stock
    stock_options = [0, 3, 6, 9, 12, 15, 18, 21, 24]
    stock_weights = [1, 2, 5, 10, 15, 20, 15, 8, 5]
    stock = random.choices(stock_options, weights=stock_weights)[0]
    
    product = {
        "id": str(uuid.uuid4()),
        "name": name,
        "category": subcategory.replace("_", " ").title(),
        "subcategory": subcategory,
        "brand": brand_info["name"],
        "brand_id": brand,
        "model_number": f"{brand_info['name'][:2].upper()}{series.replace(' ', '')}{str(index).zfill(3)}",
        "price": price,
        "original_price": original_price,
        "images": images,
        "description": f"Premium {subcategory.replace('_', ' ')} from {brand_info['name']} featuring {', '.join(product_data['features'][:3])}. {brand_info['description']}.",
        "short_description": f"{brand_info['name']} {subcategory.replace('_', ' ')} with professional features",
        "features": product_data["features"] + [f"{brand_info['warranty']} Warranty", "Professional Installation", "Pan India Service"],
        "specifications": {
            "brand": brand_info["name"],
            "warranty": brand_info["warranty"],
            "country_of_origin": brand_info["country"],
            "energy_rating": f"{random.choice([3, 4, 5])} Star" if category == "appliances" else "N/A",
            "installation": "Professional Recommended" if category == "appliances" else "Easy Installation"
        },
        "stock": stock,
        "fast_moving": random.choice([True, False]) if stock > 5 else False,
        "is_featured": random.choice([True, False]) if brand in ["bosch", "siemens"] else False,
        "customer_rating": round(random.uniform(4.0, 4.8), 1),
        "review_count": random.randint(15, 250),
        "tags": [brand, category, subcategory.replace("_", "-"), "professional", "warranty"],
        "warranty_details": {
            "manufacturer": brand_info["warranty"],
            "extended_available": True,
            "service_network": "Pan India"
        }
    }
    
    return product

def generate_realistic_catalog():
    """Generate complete realistic product catalog"""
    
    products = []
    product_counter = 1
    
    # BOSCH APPLIANCES
    for appliance_type, templates in REALISTIC_PRODUCTS["bosch_appliances"].items():
        for template in templates:
            # Generate 3-5 products per template
            for i in range(random.randint(3, 5)):
                product = generate_realistic_product("bosch", "appliances", appliance_type, template, product_counter)
                products.append(product)
                product_counter += 1
    
    # SIEMENS APPLIANCES  
    for appliance_type, templates in REALISTIC_PRODUCTS["siemens_appliances"].items():
        for template in templates:
            for i in range(random.randint(2, 4)):
                product = generate_realistic_product("siemens", "appliances", appliance_type, template, product_counter)
                products.append(product)
                product_counter += 1
                
    # HINDWARE PRODUCTS
    for category, templates in REALISTIC_PRODUCTS["hindware_products"].items():
        for template in templates:
            products_to_generate = 4 if category == "appliances" else 3
            for i in range(products_to_generate):
                product = generate_realistic_product("hindware", category, category, template, product_counter)
                products.append(product)
                product_counter += 1
    
    # BOSCH POWER TOOLS
    for tool_type, templates in REALISTIC_PRODUCTS["bosch_power_tools"].items():
        for template in templates:
            for i in range(3):
                product = generate_realistic_product("bosch", "power_tools", tool_type, template, product_counter)
                products.append(product)
                product_counter += 1
    
    # BOSCH CARE PRODUCTS
    for care_type, templates in REALISTIC_PRODUCTS["bosch_care"].items():
        for template in templates:
            for i in range(2):
                product = generate_realistic_product("bosch", "care_products", care_type, template, product_counter)
                products.append(product)
                product_counter += 1
    
    return products

if __name__ == "__main__":
    catalog = generate_realistic_catalog()
    print(f"Generated {len(catalog)} realistic products")
    
    # Show distribution
    brand_count = {}
    category_count = {}
    
    for product in catalog:
        brand = product["brand"]
        category = product["subcategory"]
        
        brand_count[brand] = brand_count.get(brand, 0) + 1
        category_count[category] = category_count.get(category, 0) + 1
    
    print(f"\n📊 Brand Distribution:")
    for brand, count in sorted(brand_count.items()):
        print(f"  {brand}: {count} products")
        
    print(f"\n📋 Category Distribution:")
    for category, count in sorted(category_count.items()):
        print(f"  {category.replace('_', ' ').title()}: {count} products")