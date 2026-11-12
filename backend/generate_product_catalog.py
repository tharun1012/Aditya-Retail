# Generate 100+ Products for AI-Enhanced E-commerce Platform
import uuid
import random
from enhanced_products_data import ENHANCED_CATEGORIES, ENHANCED_BRANDS, generate_ai_features

# High-quality product images from our previous vision expert results
PRODUCT_IMAGES = {
    "microwaves": [
        "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=500&h=500&fit=crop",
        "https://images.unsplash.com/photo-1626143508000-4b5904e5e84a?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=500&h=500&fit=crop",
        "https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?ixlib=rb-4.0.3&w=500&h=500&fit=crop"
    ],
    "cooktops": [
        "https://images.unsplash.com/photo-1629234356883-c37e616a2d43?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=500&h=500&fit=crop"
    ],
    "refrigerators": [
        "https://images.unsplash.com/photo-1484154218962-a197022b5858?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=500&h=500&fit=crop"
    ],
    "washing_machines": [
        "https://images.unsplash.com/photo-1626806819282-2c1dc01a5e0c?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=500&h=500&fit=crop",
        "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=500&h=500&fit=crop"
    ],
    "hoods": [
        "https://images.unsplash.com/photo-1556908493-4ac5f138ab77?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=500&h=500&fit=crop"
    ],
    "kitchen_setup": [
        "https://images.unsplash.com/photo-1722942722302-3e8a6dd7e77c?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=500&h=500&fit=crop"
    ]
}

# Product name templates for different categories
PRODUCT_TEMPLATES = {
    "microwaves": [
        "{brand} {series} Built-in Microwave {capacity}L {color}",
        "{brand} {series} Countertop Microwave {capacity}L {features}",
        "{brand} {series} Convection Microwave {capacity}L {premium_features}"
    ],
    "refrigerators": [
        "{brand} {series} Double Door Refrigerator {capacity}L {color}",
        "{brand} {series} Single Door Fridge {capacity}L {features}",
        "{brand} {series} Side by Side Refrigerator {capacity}L {premium_features}",
        "{brand} {series} Bottom Freezer Fridge {capacity}L {color}"
    ],
    "washing_machines": [
        "{brand} {series} Front Load Washing Machine {capacity}KG {rpm}RPM",
        "{brand} {series} Top Load Washer {capacity}KG {features}",
        "{brand} {series} Washer Dryer Combo {capacity}KG {premium_features}"
    ],
    "dishwashers": [
        "{brand} {series} Built-in Dishwasher {place_settings} Place Settings",
        "{brand} {series} Freestanding Dishwasher {features}",
        "{brand} {series} Compact Dishwasher {place_settings}PS {color}"
    ],
    "cooktops": [
        "{brand} {series} Induction Cooktop {burners} Burner {size}cm",
        "{brand} {series} Gas Hob {burners} Burner {features}",
        "{brand} {series} Electric Cooktop {size}cm {premium_features}"
    ],
    "ovens": [
        "{brand} {series} Built-in Oven {capacity}L {features}",
        "{brand} {series} Steam Oven {capacity}L {premium_features}",
        "{brand} {series} Combination Oven {capacity}L {color}"
    ],
    "chimneys": [
        "{brand} {series} Wall Mount Chimney {size}cm {suction}m3/hr",
        "{brand} {series} Island Chimney {size}cm {features}",
        "{brand} {series} Built-in Hood {size}cm {premium_features}"
    ],
    "water_heaters": [
        "{brand} {series} Electric Geyser {capacity}L {features}",
        "{brand} {series} Gas Water Heater {capacity}L {color}",
        "{brand} {series} Solar Water Heater {capacity}L {premium_features}"
    ],
    "air_conditioners": [
        "{brand} {series} Split AC {capacity} Ton {star_rating} Star",
        "{brand} {series} Window AC {capacity} Ton {features}",
        "{brand} {series} Inverter AC {capacity} Ton {premium_features}"
    ]
}

# Series names for different brands
BRAND_SERIES = {
    "bosch": ["Serie 2", "Serie 4", "Serie 6", "Serie 8", "iQ300", "iQ500", "iQ700", "iQ900"],
    "siemens": ["iQ100", "iQ300", "iQ500", "iQ700", "iQ900", "studioline", "avantgarde"],
    "lg": ["ThinQ", "InstaView", "Door-in-Door", "LinearCooling", "AI DD", "Smart Inverter"],
    "samsung": ["Digital Inverter", "WindFree", "SpaceMax", "FlexZone", "AddWash", "EcoBubble"],
    "whirlpool": ["Supreme Care", "Stainwash", "Fresh Care", "6th Sense", "Intellifresh"],
    "hindware": ["Elanza", "Senzo", "Calisto", "Chimera", "Atlantic"]
}

# Feature sets
FEATURES_BASIC = ["Energy Efficient", "Easy Clean", "Digital Display", "Auto Shut-off"]
FEATURES_MID = ["Smart Controls", "Multi-Function", "Timer Settings", "Child Lock", "LED Display"]
FEATURES_PREMIUM = ["WiFi Enabled", "App Control", "Voice Commands", "AI Optimization", "Smart Diagnostics"]

def generate_product_data(category, brand_id, product_index):
    """Generate a complete product with all enhanced features"""
    
    brand = next(b for b in ENHANCED_BRANDS if b["id"] == brand_id)
    series = random.choice(BRAND_SERIES[brand_id])
    
    # Generate price based on brand positioning
    base_prices = {
        "microwaves": (25000, 150000),
        "refrigerators": (15000, 200000),
        "washing_machines": (20000, 120000),
        "dishwashers": (30000, 180000),
        "cooktops": (8000, 80000),
        "ovens": (40000, 250000),
        "chimneys": (15000, 100000),
        "water_heaters": (8000, 50000),
        "air_conditioners": (25000, 150000)
    }
    
    min_price, max_price = base_prices.get(category, (10000, 100000))
    
    # Premium brands get 20-40% higher pricing
    if brand_id in ["bosch", "siemens"]:
        min_price = int(min_price * 1.3)
        max_price = int(max_price * 1.4)
    elif brand_id in ["lg", "samsung"]:
        min_price = int(min_price * 1.2)
        max_price = int(max_price * 1.3)
    
    price = random.randint(min_price, max_price)
    original_price = int(price * random.uniform(1.1, 1.3)) if random.random() > 0.3 else None
    
    # Determine price category for AI features
    price_category = "premium" if price > (max_price * 0.7) else "mid" if price > (max_price * 0.4) else "basic"
    
    # Generate capacity/size based on category
    capacities = {
        "microwaves": [20, 25, 28, 32, 38, 45],
        "refrigerators": [185, 215, 260, 310, 385, 450, 565],
        "washing_machines": [6, 7, 8, 9, 10, 12],
        "dishwashers": [12, 14, 15, 16],
        "cooktops": [60, 75, 90],
        "ovens": [65, 71, 85],
        "chimneys": [60, 75, 90],
        "water_heaters": [15, 25, 35, 50],
        "air_conditioners": [1.0, 1.5, 2.0]
    }
    
    capacity = random.choice(capacities.get(category, [1]))
    
    # Generate product name
    template = random.choice(PRODUCT_TEMPLATES.get(category, ["{brand} {series} {category}"]))
    
    name_vars = {
        "brand": brand["name"],
        "series": series,
        "capacity": capacity,
        "color": random.choice(["Black", "White", "Silver", "Stainless Steel"]),
        "features": random.choice(["Digital", "Smart", "Pro", "Elite"]),
        "premium_features": random.choice(["AI Enabled", "IoT Ready", "Smart Connect", "Premium"]),
        "burners": random.choice([2, 3, 4]),
        "size": random.choice([60, 75, 90]),
        "suction": random.choice([1200, 1350, 1500]),
        "place_settings": random.choice([12, 14, 15, 16]),
        "rpm": random.choice([1000, 1200, 1400]),
        "star_rating": random.choice([3, 4, 5])
    }
    
    name = template.format(**name_vars)
    
    # Select appropriate images
    image_key = category
    if image_key not in PRODUCT_IMAGES:
        image_key = "kitchen_setup"  # fallback
        
    images = PRODUCT_IMAGES[image_key][:3]  # Take up to 3 images
    
    # Generate features based on price category
    if price_category == "premium":
        features = FEATURES_BASIC + FEATURES_MID + random.sample(FEATURES_PREMIUM, 3)
    elif price_category == "mid":
        features = FEATURES_BASIC + random.sample(FEATURES_MID, 3)
    else:
        features = random.sample(FEATURES_BASIC, 3)
    
    # Generate stock (realistic distribution)
    stock_options = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27]  # 10 options
    stock_weights = [1, 2, 5, 8, 15, 20, 15, 8, 5, 3]     # 10 weights - favor 12-18 range
    stock = random.choices(stock_options, weights=stock_weights)[0]
    
    product = {
        "id": str(uuid.uuid4()),
        "name": name,
        "category": category.replace("_", " ").title(),
        "subcategory": category,
        "brand": brand["name"],
        "brand_id": brand_id,
        "model_number": f"{brand['name'][:2].upper()}{series.replace(' ', '')}{str(product_index).zfill(3)}",
        "price": price,
        "original_price": original_price,
        "images": images,
        "description": f"Premium {category.replace('_', ' ')} from {brand['name']} featuring advanced technology and superior build quality. Perfect for modern homes with {', '.join(features[:3]).lower()}.",
        "short_description": f"{capacity}{' KG' if category == 'washing_machines' else 'L' if category in ['microwaves', 'refrigerators', 'ovens'] else 'cm' if category in ['cooktops', 'chimneys'] else ''} {category.replace('_', ' ')} with premium features",
        "features": features,
        "specifications": {
            "capacity": f"{capacity} {'KG' if category == 'washing_machines' else 'Liters' if category in ['microwaves', 'refrigerators', 'ovens', 'water_heaters'] else 'cm' if category in ['cooktops', 'chimneys'] else 'Ton' if category == 'air_conditioners' else 'Place Settings' if category == 'dishwashers' else ''}",
            "warranty": f"{brand['warranty_standard']} Comprehensive",
            "energy_rating": f"{random.choice([3, 4, 5])} Star",
            "color": name_vars.get("color", "Black"),
            "installation": "Professional Installation Recommended" if category in ["dishwashers", "ovens", "chimneys"] else "Easy Installation"
        },
        "stock": stock,
        "fast_moving": random.choice([True, False]) if stock > 5 else False,
        "is_featured": random.choice([True, False]) if price_category == "premium" else False,
        "customer_rating": round(random.uniform(3.5, 5.0), 1),
        "review_count": random.randint(10, 500),
        "ai_features": generate_ai_features(category, brand_id, price_category),
        "tags": [price_category, category.replace("_", "-"), brand_id, "energy-efficient"] + (["smart-enabled"] if price_category == "premium" else []),
        "warranty_details": {
            "manufacturer": brand["warranty_standard"],
            "extended_available": True,
            "service_network": "Pan India"
        }
    }
    
    return product

def generate_complete_catalog():
    """Generate 100+ products across all categories"""
    
    products = []
    product_counter = 1
    
    categories = ["microwaves", "refrigerators", "washing_machines", "dishwashers", 
                 "cooktops", "ovens", "chimneys", "water_heaters", "air_conditioners"]
    
    brands = ["bosch", "siemens", "lg", "samsung", "whirlpool", "hindware"]
    
    # Generate products ensuring good distribution
    for category in categories:
        products_per_category = 12  # 12 products per category = 108 total
        
        for i in range(products_per_category):
            # Cycle through brands for variety
            brand = brands[i % len(brands)]
            
            product = generate_product_data(category, brand, product_counter)
            products.append(product)
            product_counter += 1
    
    return products

# Generate the complete catalog
if __name__ == "__main__":
    catalog = generate_complete_catalog()
    print(f"Generated {len(catalog)} products")
    
    # Sample product for verification
    sample = catalog[0]
    print(f"\nSample Product: {sample['name']}")
    print(f"Price: ₹{sample['price']:,}")
    print(f"Features: {', '.join(sample['features'][:3])}")