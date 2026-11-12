# Comprehensive Bulk Product Management System
# For updating all 46 products with complete details

import asyncio
import csv
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import pandas as pd
from typing import Dict, List, Optional

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')

class BulkProductManager:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[DB_NAME]

    async def get_all_products(self) -> List[Dict]:
        """Get all current products for bulk update"""
        products = await self.db.products.find({}).to_list(length=None)
        return products

    async def export_products_to_csv(self, filename: str = "products_for_update.csv"):
        """Export current products to CSV for editing"""
        products = await self.get_all_products()
        
        # Prepare data for CSV
        csv_data = []
        for product in products:
            row = {
                'id': product.get('id'),
                'name': product.get('name'),
                'brand': product.get('brand'),
                'category': product.get('category'),
                'subcategory': product.get('subcategory'),
                'price': product.get('price'),
                'original_price': product.get('original_price', ''),
                'stock': product.get('stock'),
                'description': product.get('description', ''),
                'short_description': product.get('short_description', ''),
                
                # Current basic features (comma-separated)
                'features': ', '.join(product.get('features', [])),
                
                # Specifications to be filled
                'capacity': product.get('specifications', {}).get('capacity', ''),
                'power': '',
                'dimensions_length': '',
                'dimensions_width': '', 
                'dimensions_height': '',
                'weight': '',
                'voltage': '',
                'frequency': '',
                'material': '',
                'color': product.get('specifications', {}).get('color', ''),
                'energy_rating': product.get('specifications', {}).get('energy_rating', ''),
                'warranty': product.get('specifications', {}).get('warranty', ''),
                'installation_type': product.get('specifications', {}).get('installation', ''),
                
                # Images (pipe-separated URLs)
                'image_1': product.get('images', [''])[0] if product.get('images') else '',
                'image_2': product.get('images', ['', ''])[1] if len(product.get('images', [])) > 1 else '',
                'image_3': product.get('images', ['', '', ''])[2] if len(product.get('images', [])) > 2 else '',
                'image_4': '',
                'image_5': '',
                
                # Additional details to be filled
                'detailed_features': '',  # Detailed feature list
                'benefits': '',  # Product benefits
                'usage_instructions': '',  # How to use
                'installation_instructions': '',  # Installation guide
                'maintenance_tips': '',  # Maintenance guidance
                'compatibility': '',  # What it works with
                'certifications': '',  # ISI, BIS, etc.
                'package_contents': '',  # What's in the box
                'service_support': '',  # Service information
                
                # SEO and Marketing
                'seo_title': '',
                'seo_description': '',
                'marketing_highlights': '',  # Key selling points
                'target_audience': '',  # Who should buy this
                'use_cases': ''  # Where/when to use
            }
            csv_data.append(row)
        
        # Write to CSV
        if csv_data:
            df = pd.DataFrame(csv_data)
            df.to_csv(filename, index=False)
            print(f"✅ Exported {len(csv_data)} products to {filename}")
            return filename
        
        return None

    async def import_products_from_csv(self, filename: str):
        """Import updated products from CSV"""
        try:
            df = pd.read_csv(filename)
            updated_count = 0
            
            for _, row in df.iterrows():
                product_id = row['id']
                
                # Build updated product data
                update_data = {}
                
                # Basic information
                if pd.notna(row.get('description')) and row['description'].strip():
                    update_data['description'] = row['description'].strip()
                    
                if pd.notna(row.get('short_description')) and row['short_description'].strip():
                    update_data['short_description'] = row['short_description'].strip()
                
                # Features
                if pd.notna(row.get('features')) and row['features'].strip():
                    features = [f.strip() for f in row['features'].split(',') if f.strip()]
                    update_data['features'] = features
                
                # Images
                images = []
                for i in range(1, 6):
                    img_url = row.get(f'image_{i}')
                    if pd.notna(img_url) and img_url.strip():
                        images.append(img_url.strip())
                
                if images:
                    update_data['images'] = images
                
                # Specifications
                specs = {}
                spec_fields = [
                    'capacity', 'power', 'weight', 'voltage', 'frequency', 
                    'material', 'color', 'energy_rating', 'warranty', 'installation_type'
                ]
                
                for field in spec_fields:
                    value = row.get(field)
                    if pd.notna(value) and str(value).strip():
                        specs[field] = str(value).strip()
                
                # Dimensions
                if any(pd.notna(row.get(f'dimensions_{d}')) for d in ['length', 'width', 'height']):
                    dimensions = {}
                    for dim in ['length', 'width', 'height']:
                        val = row.get(f'dimensions_{dim}')
                        if pd.notna(val) and str(val).strip():
                            dimensions[dim] = str(val).strip()
                    if dimensions:
                        specs['dimensions'] = dimensions
                
                if specs:
                    update_data['specifications'] = specs
                
                # Enhanced product details
                enhanced_fields = [
                    'detailed_features', 'benefits', 'usage_instructions',
                    'installation_instructions', 'maintenance_tips', 'compatibility',
                    'certifications', 'package_contents', 'service_support',
                    'seo_title', 'seo_description', 'marketing_highlights',
                    'target_audience', 'use_cases'
                ]
                
                enhanced_data = {}
                for field in enhanced_fields:
                    value = row.get(field)
                    if pd.notna(value) and str(value).strip():
                        enhanced_data[field] = str(value).strip()
                
                if enhanced_data:
                    update_data['enhanced_details'] = enhanced_data
                
                # Update product if we have data to update
                if update_data:
                    result = await self.db.products.update_one(
                        {'id': product_id},
                        {'$set': update_data}
                    )
                    
                    if result.modified_count > 0:
                        updated_count += 1
            
            print(f"✅ Updated {updated_count} products from CSV")
            return updated_count
            
        except Exception as e:
            print(f"❌ Error importing CSV: {e}")
            return 0

    async def get_product_update_template(self) -> Dict:
        """Get a template for updating a single product"""
        return {
            "description": "Detailed product description highlighting key features and benefits",
            "short_description": "Brief one-line product summary",
            "features": [
                "Feature 1", "Feature 2", "Feature 3", "Feature 4", "Feature 5"
            ],
            "images": [
                "https://example.com/image1.jpg",
                "https://example.com/image2.jpg", 
                "https://example.com/image3.jpg",
                "https://example.com/image4.jpg",
                "https://example.com/image5.jpg"
            ],
            "specifications": {
                "capacity": "25 Liters",
                "power": "900 Watts",
                "dimensions": {
                    "length": "59.4 cm",
                    "width": "45.5 cm",
                    "height": "32.2 cm"
                },
                "weight": "18 kg",
                "voltage": "230V, 50Hz",
                "material": "Stainless Steel",
                "color": "Black",
                "energy_rating": "4 Star",
                "warranty": "2 Years Comprehensive",
                "installation_type": "Built-in Installation Required",
                "certifications": "ISI Certified, BIS Approved"
            },
            "enhanced_details": {
                "detailed_features": "Feature 1: Description, Feature 2: Description",
                "benefits": "Benefit 1, Benefit 2, Benefit 3",
                "usage_instructions": "Step-by-step usage guide",
                "installation_instructions": "Professional installation recommended",
                "maintenance_tips": "Regular cleaning and maintenance guidelines",
                "compatibility": "Compatible with standard kitchen setups",
                "package_contents": "Main unit, User manual, Warranty card, Installation kit",
                "service_support": "24/7 customer support, Pan India service network",
                "marketing_highlights": "Premium German engineering, Energy efficient, Smart features",
                "target_audience": "Modern families, Working professionals, Premium home buyers",
                "use_cases": "Daily cooking, Quick meals, Dinner parties, Professional cooking"
            }
        }

    async def update_single_product(self, product_id: str, update_data: Dict):
        """Update a single product with comprehensive data"""
        result = await self.db.products.update_one(
            {'id': product_id},
            {'$set': update_data}
        )
        return result.modified_count > 0

    async def generate_sample_updates(self):
        """Generate sample updates for the first few products"""
        products = await self.get_all_products()
        
        sample_updates = {}
        for i, product in enumerate(products[:5]):  # First 5 products
            product_id = product['id']
            brand = product.get('brand', '')
            category = product.get('subcategory', '')
            
            # Generate realistic sample data based on product type
            sample_data = await self._generate_realistic_data(product)
            sample_updates[product_id] = sample_data
        
        return sample_updates

    async def _generate_realistic_data(self, product: Dict) -> Dict:
        """Generate realistic product data based on brand and category"""
        brand = product.get('brand', '').lower()
        category = product.get('subcategory', '').lower()
        name = product.get('name', '')
        
        # Base template
        data = {
            "description": f"Premium {category} from {product.get('brand')} featuring advanced technology and superior build quality. Designed for modern homes with reliability and performance in mind.",
            "short_description": f"Professional {category} with advanced features and premium build quality",
            "features": [],
            "images": product.get('images', []),
            "specifications": {},
            "enhanced_details": {}
        }
        
        # Category-specific features and specs
        if 'microwave' in category:
            data["features"] = [
                "Multiple Power Levels", "Digital Display", "Auto Cook Menus",
                "Child Safety Lock", "LED Interior Lighting", "Quick Start Function"
            ]
            data["specifications"] = {
                "capacity": "25 Liters",
                "power": "900 Watts",
                "voltage": "230V, 50Hz",
                "dimensions": {"length": "51.3 cm", "width": "40.6 cm", "height": "31.7 cm"},
                "weight": "16 kg",
                "material": "Stainless Steel Interior",
                "energy_rating": "4 Star",
                "warranty": f"2 Years" if brand != 'siemens' else "3 Years"
            }
            
        elif 'refrigerator' in category:
            data["features"] = [
                "Multi Air Flow", "Digital Temperature Control", "LED Lighting",
                "Large Vegetable Crisper", "Frost Free Technology", "Energy Efficient Compressor"
            ]
            data["specifications"] = {
                "capacity": "260 Liters",
                "energy_rating": "3 Star",
                "voltage": "230V, 50Hz", 
                "dimensions": {"length": "55 cm", "width": "62 cm", "height": "144 cm"},
                "weight": "45 kg",
                "refrigerant": "R600a",
                "warranty": f"2 Years Product, 10 Years Compressor" if brand != 'siemens' else "3 Years Comprehensive"
            }
            
        elif 'washing' in category:
            data["features"] = [
                "Multiple Wash Programs", "Digital Display", "Delay Start",
                "Child Lock", "Auto Water Level", "Stainless Steel Drum"
            ]
            data["specifications"] = {
                "capacity": "7 KG",
                "max_rpm": "1200 RPM",
                "voltage": "230V, 50Hz",
                "dimensions": {"length": "60 cm", "width": "55 cm", "height": "85 cm"},
                "weight": "65 kg",
                "water_consumption": "90 Liters per cycle",
                "energy_rating": "5 Star",
                "warranty": f"2 Years Product, 10 Years Motor" if brand != 'siemens' else "3 Years Comprehensive"
            }
        
        # Brand-specific enhancements
        if brand == 'bosch':
            data["enhanced_details"]["marketing_highlights"] = "German Engineering Excellence, EcoSilence Drive, Advanced Sensor Technology"
            data["enhanced_details"]["service_support"] = "Bosch Service Network across India, 24/7 Customer Support"
            
        elif brand == 'siemens':
            data["enhanced_details"]["marketing_highlights"] = "Premium German Technology, iQ Drive System, Studio Line Design"
            data["enhanced_details"]["service_support"] = "Siemens Premium Service, Extended Warranty Options"
            
        elif brand == 'hindware':
            data["enhanced_details"]["marketing_highlights"] = "Made in India, Cost Effective, Reliable Performance"
            data["enhanced_details"]["service_support"] = "Pan India Service Network, Local Support"
        
        # Common enhanced details
        data["enhanced_details"].update({
            "installation_instructions": "Professional installation recommended for optimal performance",
            "maintenance_tips": "Regular cleaning and periodic servicing recommended",
            "target_audience": "Modern families seeking reliable and efficient appliances",
            "certifications": "ISI Certified, BIS Approved"
        })
        
        return data

# Usage functions
async def export_for_editing():
    """Export current products to CSV for comprehensive editing"""
    manager = BulkProductManager()
    filename = await manager.export_products_to_csv()
    manager.client.close()
    return filename

async def import_updated_products(filename: str):
    """Import updated products from edited CSV"""
    manager = BulkProductManager()
    updated_count = await manager.import_products_from_csv(filename)
    manager.client.close()
    return updated_count

async def show_sample_product_data():
    """Show sample data structure for product updates"""
    manager = BulkProductManager()
    template = await manager.get_product_update_template()
    sample_updates = await manager.generate_sample_updates()
    manager.client.close()
    
    print("📋 Sample Product Update Template:")
    print(json.dumps(template, indent=2))
    
    print(f"\n🎯 Sample Updates for First Few Products:")
    for product_id, data in list(sample_updates.items())[:2]:
        print(f"\nProduct ID: {product_id}")
        print(json.dumps(data, indent=2)[:500] + "...")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "export":
            filename = asyncio.run(export_for_editing())
            print(f"Products exported to: {filename}")
            
        elif command == "import" and len(sys.argv) > 2:
            csv_file = sys.argv[2]
            count = asyncio.run(import_updated_products(csv_file))
            print(f"Updated {count} products")
            
        elif command == "sample":
            asyncio.run(show_sample_product_data())
            
    else:
        print("Usage:")
        print("  python bulk_product_management.py export")
        print("  python bulk_product_management.py import <csv_file>") 
        print("  python bulk_product_management.py sample")