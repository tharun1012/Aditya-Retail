"""
MANDATORY PRE-ADDITION QUALITY CHECK
=====================================

THIS SCRIPT MUST BE RUN BEFORE ADDING ANY PRODUCT TO DATABASE!

It validates:
1. Image URLs are accessible (HTTP 200)
2. Minimum 3-5 images per product
3. All required fields present
4. Data quality standards met

NO PRODUCT GETS ADDED WITHOUT PASSING THIS CHECK!
"""

import asyncio
import requests
from typing import List, Dict, Tuple

def validate_image_url(url: str, timeout: int = 5) -> Tuple[bool, str]:
    """
    Check if image URL is accessible
    Returns: (is_valid, message)
    """
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            return True, "✅ Accessible"
        else:
            return False, f"❌ HTTP {response.status_code}"
    except requests.Timeout:
        return False, "❌ Timeout"
    except requests.RequestException as e:
        return False, f"❌ Error: {str(e)[:50]}"


def validate_product_before_addition(product: Dict) -> Tuple[bool, List[str]]:
    """
    Complete validation before adding product to database
    Returns: (can_add, list_of_issues)
    """
    issues = []
    can_add = True
    
    model = product.get('model_number', 'UNKNOWN')
    
    print(f"\n{'=' * 70}")
    print(f"VALIDATING: {model}")
    print(f"{'=' * 70}")
    
    # 1. CRITICAL: Check images
    images = product.get('images', [])
    print(f"\n1. IMAGE VALIDATION:")
    
    if not images or len(images) == 0:
        issues.append("❌ CRITICAL: No images provided")
        can_add = False
        print("   ❌ CRITICAL: No images provided")
    elif len(images) < 3:
        issues.append(f"❌ CRITICAL: Only {len(images)} image(s) - need minimum 3")
        can_add = False
        print(f"   ❌ CRITICAL: Only {len(images)} images - need minimum 3")
    else:
        print(f"   ✅ Image count: {len(images)}")
        
        # Validate each image URL
        accessible_count = 0
        for i, img_url in enumerate(images, 1):
            is_valid, message = validate_image_url(img_url)
            if is_valid:
                accessible_count += 1
                print(f"   {i}. {message} - {img_url[:70]}...")
            else:
                print(f"   {i}. {message} - {img_url[:70]}...")
                issues.append(f"⚠️  Image {i} not accessible: {img_url[:50]}")
        
        if accessible_count == 0:
            can_add = False
            issues.append("❌ CRITICAL: No accessible images found")
        elif accessible_count < len(images):
            print(f"   ⚠️  Warning: Only {accessible_count}/{len(images)} images accessible")
    
    # 2. Check key features
    features = product.get('key_features', [])
    print(f"\n2. KEY FEATURES:")
    if not features or len(features) < 10:
        issues.append(f"❌ Need minimum 10 features (have {len(features)})")
        can_add = False
        print(f"   ❌ Only {len(features)} features - need minimum 10")
    else:
        print(f"   ✅ {len(features)} features provided")
    
    # 3. Check specifications
    specs = product.get('specifications', {})
    print(f"\n3. SPECIFICATIONS:")
    if not specs or len(specs) < 8:
        issues.append(f"❌ Need minimum 8 specs (have {len(specs)})")
        can_add = False
        print(f"   ❌ Only {len(specs)} specs - need minimum 8")
    else:
        print(f"   ✅ {len(specs)} specifications provided")
    
    # 4. Check descriptions
    print(f"\n4. DESCRIPTIONS:")
    long_desc = product.get('long_description', '')
    if len(long_desc) < 500:
        issues.append(f"⚠️  Long description too short ({len(long_desc)} chars)")
        print(f"   ⚠️  Long description: {len(long_desc)} chars (need 500+)")
    else:
        print(f"   ✅ Long description: {len(long_desc)} chars")
    
    if not product.get('short_description'):
        issues.append("❌ Missing short description")
        can_add = False
        print(f"   ❌ No short description")
    else:
        print(f"   ✅ Short description present")
    
    # 5. Check basic info
    print(f"\n5. BASIC INFO:")
    if not product.get('name'):
        issues.append("❌ CRITICAL: No product name")
        can_add = False
    if not product.get('model_number'):
        issues.append("❌ CRITICAL: No model number")
        can_add = False
    if not product.get('price'):
        issues.append("❌ CRITICAL: No price")
        can_add = False
    
    print(f"   Name: {'✅' if product.get('name') else '❌'}")
    print(f"   Model: {'✅' if product.get('model_number') else '❌'}")
    print(f"   Price: {'✅' if product.get('price') else '❌'}")
    
    # Final verdict
    print(f"\n{'=' * 70}")
    if can_add:
        print("✅ VALIDATION PASSED - PRODUCT CAN BE ADDED")
    else:
        print("❌ VALIDATION FAILED - PRODUCT CANNOT BE ADDED")
        print("\nCritical Issues:")
        for issue in issues:
            if 'CRITICAL' in issue:
                print(f"  {issue}")
    print(f"{'=' * 70}\n")
    
    return can_add, issues


# Example usage
if __name__ == "__main__":
    # Test with a sample product
    sample_product = {
        "model_number": "TEST123",
        "name": "Test Product",
        "price": 10000,
        "images": [
            "https://media3.bsh-group.com/Product_Shots/900x/21043435_SMS4HMB62T_STP_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/21085814_SMS4HMB62T_PGA3_def.webp",
            "https://media3.bsh-group.com/Product_Shots/900x/19714426_A01_CD10_PGA6_def.webp"
        ],
        "key_features": ["Feature " + str(i) for i in range(1, 11)],
        "specifications": {f"Spec{i}": f"Value{i}" for i in range(1, 9)},
        "long_description": "A" * 500,
        "short_description": "Test description"
    }
    
    can_add, issues = validate_product_before_addition(sample_product)
    
    if can_add:
        print("\n✅ This product meets all quality standards!")
    else:
        print("\n❌ This product needs work before adding!")
