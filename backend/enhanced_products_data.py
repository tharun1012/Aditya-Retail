# Enhanced Product Database with 100+ Products for AI-Powered E-commerce
# This file contains comprehensive product data with AI-enhanced features

from datetime import datetime
import uuid

# Enhanced Categories with detailed subcategories
ENHANCED_CATEGORIES = [
    {
        "id": "kitchen-appliances",
        "name": "Kitchen Appliances",
        "description": "Complete range of modern kitchen appliances",
        "icon": "ChefHat",
        "subcategories": [
            {"id": "microwaves", "name": "Microwaves", "description": "Built-in and countertop microwaves"},
            {"id": "ovens", "name": "Ovens", "description": "Conventional and steam ovens"},
            {"id": "dishwashers", "name": "Dishwashers", "description": "Built-in and freestanding dishwashers"},
            {"id": "food-processors", "name": "Food Processors", "description": "Mixers, grinders, and food processors"},
            {"id": "water-purifiers", "name": "Water Purifiers", "description": "RO and UV water purification systems"}
        ]
    },
    {
        "id": "cooking-equipment",
        "name": "Cooking Equipment", 
        "description": "Professional cooking solutions",
        "icon": "Flame",
        "subcategories": [
            {"id": "cooktops", "name": "Cooktops", "description": "Gas, induction, and electric cooktops"},
            {"id": "cooking-ranges", "name": "Cooking Ranges", "description": "Professional cooking ranges"},
            {"id": "chimneys", "name": "Chimneys", "description": "Kitchen ventilation and exhaust systems"},
            {"id": "grills", "name": "Grills", "description": "Indoor and outdoor grilling solutions"}
        ]
    },
    {
        "id": "home-appliances",
        "name": "Home Appliances",
        "description": "Essential home appliances for modern living",
        "icon": "Home",
        "subcategories": [
            {"id": "refrigerators", "name": "Refrigerators", "description": "Single door, double door, and side-by-side fridges"},
            {"id": "washing-machines", "name": "Washing Machines", "description": "Front load, top load, and washer-dryer combos"},
            {"id": "air-conditioners", "name": "Air Conditioners", "description": "Split, window, and central AC systems"},
            {"id": "water-heaters", "name": "Water Heaters", "description": "Electric, gas, and solar water heaters"},
            {"id": "vacuum-cleaners", "name": "Vacuum Cleaners", "description": "Robotic, handheld, and canister vacuums"}
        ]
    },
    {
        "id": "smart-home",
        "name": "Smart Home",
        "description": "IoT and smart home automation",
        "icon": "Smartphone",
        "subcategories": [
            {"id": "smart-switches", "name": "Smart Switches", "description": "WiFi enabled switches and dimmers"},
            {"id": "smart-security", "name": "Smart Security", "description": "Smart locks, cameras, and sensors"},
            {"id": "smart-lighting", "name": "Smart Lighting", "description": "Connected bulbs and lighting systems"}
        ]
    }
]

# Enhanced Brands with detailed information
ENHANCED_BRANDS = [
    {
        "id": "bosch",
        "name": "Bosch",
        "description": "German engineering excellence in home appliances",
        "country": "Germany",
        "founded": 1886,
        "specialties": ["Kitchen Appliances", "Home Appliances", "Professional Tools"],
        "warranty_standard": "2 years",
        "customer_rating": 4.6
    },
    {
        "id": "siemens", 
        "name": "Siemens",
        "description": "Premium German technology for modern homes",
        "country": "Germany", 
        "founded": 1847,
        "specialties": ["Premium Appliances", "Smart Home", "Energy Solutions"],
        "warranty_standard": "3 years",
        "customer_rating": 4.7
    },
    {
        "id": "hindware",
        "name": "Hindware",
        "description": "Leading Indian brand for kitchen and bath solutions",
        "country": "India",
        "founded": 1960,
        "specialties": ["Kitchen Appliances", "Bath Fittings", "Water Solutions"],
        "warranty_standard": "2 years",
        "customer_rating": 4.3
    },
    {
        "id": "lg",
        "name": "LG",
        "description": "Life's Good with innovative Korean technology",
        "country": "South Korea",
        "founded": 1958,
        "specialties": ["Electronics", "Home Appliances", "Smart Solutions"],
        "warranty_standard": "2 years",
        "customer_rating": 4.5
    },
    {
        "id": "samsung",
        "name": "Samsung",
        "description": "Cutting-edge technology for every home",
        "country": "South Korea",
        "founded": 1938,
        "specialties": ["Smart Appliances", "Electronics", "IoT Solutions"],
        "warranty_standard": "2 years",
        "customer_rating": 4.4
    },
    {
        "id": "whirlpool",
        "name": "Whirlpool",
        "description": "American innovation in home appliances",
        "country": "USA",
        "founded": 1911,
        "specialties": ["Washing Machines", "Refrigerators", "Kitchen Appliances"],
        "warranty_standard": "2 years", 
        "customer_rating": 4.2
    }
]

# AI-Enhanced Product Features
def generate_ai_features(product_type, brand, price_range):
    """Generate AI-powered product features and recommendations"""
    
    ai_features = {
        "ai_consultant_tips": [],
        "smart_comparisons": [],
        "usage_recommendations": [],
        "installation_guide": [],
        "compatibility_check": [],
        "energy_efficiency": {},
        "smart_features": []
    }
    
    # AI Consultant Tips based on product type
    if "microwave" in product_type.lower():
        ai_features["ai_consultant_tips"] = [
            "Perfect for reheating and quick cooking",
            "Built-in models save counter space",
            "Look for sensor cooking for best results",
            "Consider wattage for cooking speed"
        ]
        ai_features["usage_recommendations"] = [
            "Ideal for families of 3-4 members",
            "Great for working professionals",
            "Perfect for quick meal preparation"
        ]
        
    elif "washing machine" in product_type.lower():
        ai_features["ai_consultant_tips"] = [
            "Front load offers better cleaning efficiency", 
            "Top load is easier to load/unload",
            "Consider water hardness in your area",
            "Look for energy star ratings"
        ]
        ai_features["usage_recommendations"] = [
            "Front load for premium washing experience",
            "Top load for ease of use",
            "Large capacity for big families"
        ]
        
    elif "refrigerator" in product_type.lower():
        ai_features["ai_consultant_tips"] = [
            "Consider your family size for capacity",
            "Inverter technology saves energy",
            "Frost-free reduces maintenance",
            "Smart features enhance convenience"
        ]
        
    # Smart features based on price range
    if price_range == "premium":
        ai_features["smart_features"] = [
            "WiFi connectivity for remote control",
            "Smart diagnostics for maintenance alerts", 
            "Energy monitoring and optimization",
            "Voice control compatibility"
        ]
    elif price_range == "mid":
        ai_features["smart_features"] = [
            "Digital display for easy control",
            "Auto-sensing for optimal performance",
            "Energy-efficient operation"
        ]
        
    return ai_features

# Sample enhanced products (first 10 of 100+)
ENHANCED_PRODUCTS_SAMPLE = [
    {
        "id": str(uuid.uuid4()),
        "name": "Bosch Serie 8 Built-in Microwave Oven 45L",
        "category": "microwaves",
        "subcategory": "built-in-microwaves",
        "brand": "bosch",
        "model_number": "BFL634GB1",
        "price": 85990,
        "original_price": 95990,
        "images": [
            "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?w=500&h=500&fit=crop",
            "https://images.unsplash.com/photo-1626143508000-4b5904e5e84a?w=500&h=500&fit=crop"
        ],
        "description": "Premium built-in microwave with advanced cooking technology and sleek black design. Features multiple cooking modes and smart sensors for perfect results every time.",
        "short_description": "45L premium built-in microwave with smart cooking technology",
        "features": [
            "45L Large Capacity",
            "AutoPilot 8 Automatic Programs", 
            "Electronic Clock Display",
            "Child Safety Lock",
            "LED Interior Lighting",
            "Stainless Steel Interior",
            "QuickStart Function"
        ],
        "specifications": {
            "capacity": "45 Liters",
            "power": "900 Watts",
            "voltage": "230V, 50Hz", 
            "dimensions": "59.4 x 45.5 x 32.2 cm",
            "weight": "18 kg",
            "warranty": "2 Years Comprehensive",
            "installation": "Built-in Installation Required",
            "color": "Black Glass",
            "interior_material": "Stainless Steel"
        },
        "stock": 12,
        "fast_moving": True,
        "is_featured": True,
        "energy_rating": "4 Star",
        "customer_rating": 4.6,
        "review_count": 234,
        "ai_features": generate_ai_features("microwave", "bosch", "premium"),
        "tags": ["premium", "built-in", "smart-cooking", "energy-efficient"],
        "related_products": [],
        "warranty_details": {
            "manufacturer": "2 Years",
            "extended_available": True,
            "service_network": "Pan India"
        }
    }
]