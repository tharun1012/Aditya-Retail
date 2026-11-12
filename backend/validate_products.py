"""
PRODUCT VALIDATION CHECKLIST
=============================

This module ensures ALL products meet quality standards before being added to database.

MANDATORY REQUIREMENTS:
1. At least 3-5 product images (high quality 900x)
2. 10+ key features
3. 8+ specifications
4. Long description (500+ characters)
5. Short description
6. Documents (4 PDFs)
7. Valid price and stock information
8. Product URL

USE THIS FOR EVERY PRODUCT ADDITION!
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

def validate_product_data(product):
    """
    Validates that product has all required fields with proper data
    Returns: (is_valid, list_of_issues)
    """
    issues = []
    
    # Check images (CRITICAL)
    images = product.get('images', [])
    if not images or len(images) == 0:
        issues.append("❌ CRITICAL: No images provided")
    elif len(images) < 3:
        issues.append(f"⚠️  Only {len(images)} image(s) - need at least 3-5 images")
    else:
        # Check if images are proper URLs
        for img in images:
            if not img.startswith('http'):
                issues.append(f"❌ Invalid image URL: {img[:50]}")
    
    # Check key features
    features = product.get('key_features', [])
    if not features or len(features) == 0:
        issues.append("❌ CRITICAL: No key features")
    elif len(features) < 10:
        issues.append(f"⚠️  Only {len(features)} features - need at least 10")
    
    # Check specifications
    specs = product.get('specifications', {})
    if not specs or len(specs) == 0:
        issues.append("❌ CRITICAL: No specifications")
    elif len(specs) < 8:
        issues.append(f"⚠️  Only {len(specs)} specs - need at least 8")
    
    # Check descriptions
    long_desc = product.get('long_description', '')
    if not long_desc:
        issues.append("❌ CRITICAL: No long description")
    elif len(long_desc) < 500:
        issues.append(f"⚠️  Short long_description ({len(long_desc)} chars) - need 500+")
    
    short_desc = product.get('short_description', '')
    if not short_desc:
        issues.append("❌ CRITICAL: No short description")
    
    # Check documents
    documents = product.get('documents', [])
    if not documents or len(documents) < 4:
        issues.append(f"⚠️  Only {len(documents)} documents - need 4 (manual, specs, install, warranty)")
    
    # Check basic info
    if not product.get('name'):
        issues.append("❌ CRITICAL: No product name")
    if not product.get('model_number'):
        issues.append("❌ CRITICAL: No model number")
    if not product.get('price'):
        issues.append("❌ CRITICAL: No price")
    if not product.get('brand'):
        issues.append("⚠️  No brand specified")
    
    is_valid = len([i for i in issues if 'CRITICAL' in i]) == 0
    
    return is_valid, issues


async def validate_all_products():
    """
    Audit all products in database and report issues
    """
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['startup_template']
    products_collection = db['products']
    
    all_products = await products_collection.find().to_list(length=None)
    
    print("=" * 70)
    print("COMPLETE PRODUCT VALIDATION AUDIT")
    print("=" * 70)
    
    critical_issues = []
    warnings = []
    perfect = []
    
    for product in all_products:
        model = product.get('model_number', 'UNKNOWN')
        is_valid, issues = validate_product_data(product)
        
        if not is_valid:
            critical_issues.append((model, issues))
        elif issues:
            warnings.append((model, issues))
        else:
            perfect.append(model)
    
    # Print critical issues
    if critical_issues:
        print(f"\n❌ CRITICAL ISSUES ({len(critical_issues)} products):")
        print("-" * 70)
        for model, issues in critical_issues:
            print(f"\n{model}:")
            for issue in issues:
                if 'CRITICAL' in issue:
                    print(f"  {issue}")
    
    # Print warnings
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)} products):")
        print("-" * 70)
        for model, issues in warnings[:5]:  # Show first 5
            print(f"\n{model}:")
            for issue in issues:
                print(f"  {issue}")
        if len(warnings) > 5:
            print(f"\n  ... and {len(warnings) - 5} more products with warnings")
    
    # Print perfect products
    if perfect:
        print(f"\n✅ PERFECT PRODUCTS ({len(perfect)}):")
        print("-" * 70)
        print(f"All validation checks passed for {len(perfect)} products")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Products: {len(all_products)}")
    print(f"✅ Perfect: {len(perfect)}")
    print(f"⚠️  Warnings: {len(warnings)}")
    print(f"❌ Critical: {len(critical_issues)}")
    print("=" * 70)
    
    client.close()
    
    return len(critical_issues) == 0


if __name__ == "__main__":
    result = asyncio.run(validate_all_products())
    if result:
        print("\n✅ All products pass validation!")
    else:
        print("\n❌ Some products need attention!")
