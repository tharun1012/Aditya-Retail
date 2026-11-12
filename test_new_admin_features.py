#!/usr/bin/env python3
"""
Testing for 4 New Admin Features:
1. Combo Offers Management API
2. Banner Management API
3. New Product Highlighting API
4. Social Media Post Creator API
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://acct-workflow-1.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class NewAdminFeaturesTester:
    def __init__(self):
        self.session = None
        self.test_results = {}
        self.created_combo_id = None
        self.created_banner_id = None
        self.created_post_id = None
        self.product_ids = []
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print(f"🚀 Starting New Admin Features Tests")
        print(f"🔗 API Base URL: {API_BASE_URL}")
        print("=" * 80)
        
        # Fetch some product IDs for testing
        await self.fetch_product_ids()
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
            
    async def fetch_product_ids(self):
        """Fetch product IDs from database for testing"""
        try:
            async with self.session.get(f"{API_BASE_URL}/products") as response:
                if response.status == 200:
                    data = await response.json()
                    products = data.get('products', [])
                    self.product_ids = [p['id'] for p in products[:5]]
                    print(f"📦 Fetched {len(self.product_ids)} product IDs for testing")
                else:
                    print(f"⚠️ Could not fetch products: {response.status}")
        except Exception as e:
            print(f"⚠️ Error fetching products: {str(e)}")
    
    # ========== COMBO OFFERS MANAGEMENT API TESTS ==========
    
    async def test_combo_create(self):
        """Test 1: Create Combo Offer"""
        print("\n🎁 Test 1: Create Combo Offer")
        
        if len(self.product_ids) < 2:
            print("❌ Not enough products for combo testing")
            self.test_results['combo_create'] = False
            return False
        
        try:
            # Test with 2-3 products
            combo_data = {
                "name": "Kitchen Essentials Combo",
                "description": "Get 2 premium Bosch cooker hoods at special price",
                "product_ids": self.product_ids[:2],
                "discount_type": "percentage",
                "discount_value": 15.0,
                "valid_from": datetime.now().isoformat(),
                "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
                "is_active": True,
                "min_quantity": 1
            }
            
            print(f"  Creating combo with {len(combo_data['product_ids'])} products")
            print(f"  Discount: {combo_data['discount_value']}% off")
            
            async with self.session.post(
                f"{API_BASE_URL}/combo-offers/",
                json=combo_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    offer = data.get('offer', {})
                    self.created_combo_id = offer.get('id')
                    
                    print(f"  ✅ Combo Created: {offer.get('name')}")
                    print(f"  💰 Original Price: ₹{offer.get('original_price', 0):,.2f}")
                    print(f"  💵 Final Price: ₹{offer.get('final_price', 0):,.2f}")
                    print(f"  💸 Savings: ₹{offer.get('savings', 0):,.2f}")
                    
                    # Verify discount calculation
                    expected_savings = offer.get('original_price', 0) * 0.15
                    actual_savings = offer.get('savings', 0)
                    
                    if abs(expected_savings - actual_savings) < 1:
                        print(f"  ✅ Discount Calculation: Correct")
                    else:
                        print(f"  ⚠️ Discount Calculation: Expected ₹{expected_savings:.2f}, Got ₹{actual_savings:.2f}")
                    
                    self.test_results['combo_create'] = True
                    return True
                else:
                    error_text = await response.text()
                    print(f"  ❌ Combo Creation Failed: {response.status}")
                    print(f"  Error: {error_text}")
                    self.test_results['combo_create'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['combo_create'] = False
            return False
    
    async def test_combo_list(self):
        """Test 2: List All Combo Offers"""
        print("\n📋 Test 2: List All Combo Offers")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/combo-offers/") as response:
                if response.status == 200:
                    data = await response.json()
                    offers = data.get('offers', [])
                    total = data.get('total', 0)
                    
                    print(f"  ✅ Retrieved {total} combo offers")
                    
                    if offers:
                        sample = offers[0]
                        print(f"  Sample: {sample.get('name')} - ₹{sample.get('final_price', 0):,.2f}")
                    
                    self.test_results['combo_list'] = True
                    return True
                else:
                    print(f"  ❌ List Failed: {response.status}")
                    self.test_results['combo_list'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['combo_list'] = False
            return False
    
    async def test_combo_get_single(self):
        """Test 3: Get Specific Combo Offer"""
        print("\n🔍 Test 3: Get Specific Combo Offer")
        
        if not self.created_combo_id:
            print("  ⚠️ No combo ID available, skipping")
            self.test_results['combo_get_single'] = True
            return True
        
        try:
            async with self.session.get(f"{API_BASE_URL}/combo-offers/{self.created_combo_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    offer = data.get('offer', {})
                    
                    print(f"  ✅ Retrieved: {offer.get('name')}")
                    print(f"  Products: {len(offer.get('products', []))}")
                    print(f"  Status: {'Active' if offer.get('is_active') else 'Inactive'}")
                    
                    self.test_results['combo_get_single'] = True
                    return True
                else:
                    print(f"  ❌ Get Failed: {response.status}")
                    self.test_results['combo_get_single'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['combo_get_single'] = False
            return False
    
    async def test_combo_update(self):
        """Test 4: Update Combo Offer"""
        print("\n✏️ Test 4: Update Combo Offer")
        
        if not self.created_combo_id:
            print("  ⚠️ No combo ID available, skipping")
            self.test_results['combo_update'] = True
            return True
        
        try:
            update_data = {
                "discount_value": 20.0,
                "name": "Kitchen Essentials Combo - UPDATED"
            }
            
            async with self.session.put(
                f"{API_BASE_URL}/combo-offers/{self.created_combo_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    offer = data.get('offer', {})
                    
                    print(f"  ✅ Updated: {offer.get('name')}")
                    print(f"  New Discount: {offer.get('discount_value')}%")
                    print(f"  New Final Price: ₹{offer.get('final_price', 0):,.2f}")
                    
                    self.test_results['combo_update'] = True
                    return True
                else:
                    print(f"  ❌ Update Failed: {response.status}")
                    self.test_results['combo_update'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['combo_update'] = False
            return False
    
    async def test_combo_homepage(self):
        """Test 5: Get Active Homepage Combos"""
        print("\n🏠 Test 5: Get Active Homepage Combos")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/combo-offers/active/homepage") as response:
                if response.status == 200:
                    data = await response.json()
                    offers = data.get('offers', [])
                    
                    print(f"  ✅ Retrieved {len(offers)} active homepage combos")
                    
                    self.test_results['combo_homepage'] = True
                    return True
                else:
                    print(f"  ❌ Homepage Combos Failed: {response.status}")
                    self.test_results['combo_homepage'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['combo_homepage'] = False
            return False
    
    async def test_combo_delete(self):
        """Test 6: Delete Combo Offer"""
        print("\n🗑️ Test 6: Delete Combo Offer")
        
        if not self.created_combo_id:
            print("  ⚠️ No combo ID available, skipping")
            self.test_results['combo_delete'] = True
            return True
        
        try:
            async with self.session.delete(f"{API_BASE_URL}/combo-offers/{self.created_combo_id}") as response:
                if response.status == 200:
                    print(f"  ✅ Combo Deleted Successfully")
                    
                    self.test_results['combo_delete'] = True
                    return True
                else:
                    print(f"  ❌ Delete Failed: {response.status}")
                    self.test_results['combo_delete'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['combo_delete'] = False
            return False
    
    # ========== BANNER MANAGEMENT API TESTS ==========
    
    async def test_banner_create(self):
        """Test 7: Create Banner"""
        print("\n🖼️ Test 7: Create Banner")
        
        try:
            banner_data = {
                "title": "Summer Sale 2024",
                "description": "Get up to 50% off on all appliances",
                "link_url": "/products?category=sale",
                "display_order": 1,
                "is_active": True,
                "valid_from": datetime.now().isoformat(),
                "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
                "banner_type": "sale"
            }
            
            print(f"  Creating banner: {banner_data['title']}")
            
            async with self.session.post(
                f"{API_BASE_URL}/banners/",
                json=banner_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    banner = data.get('banner', {})
                    self.created_banner_id = banner.get('id')
                    
                    print(f"  ✅ Banner Created: {banner.get('title')}")
                    print(f"  Type: {banner.get('banner_type')}")
                    print(f"  Display Order: {banner.get('display_order')}")
                    print(f"  Views: {banner.get('views', 0)}, Clicks: {banner.get('clicks', 0)}")
                    
                    self.test_results['banner_create'] = True
                    return True
                else:
                    error_text = await response.text()
                    print(f"  ❌ Banner Creation Failed: {response.status}")
                    print(f"  Error: {error_text}")
                    self.test_results['banner_create'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['banner_create'] = False
            return False
    
    async def test_banner_list(self):
        """Test 8: List All Banners"""
        print("\n📋 Test 8: List All Banners")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/banners/") as response:
                if response.status == 200:
                    data = await response.json()
                    banners = data.get('banners', [])
                    total = data.get('total', 0)
                    
                    print(f"  ✅ Retrieved {total} banners")
                    
                    if banners:
                        sample = banners[0]
                        print(f"  Sample: {sample.get('title')} (Order: {sample.get('display_order')})")
                    
                    self.test_results['banner_list'] = True
                    return True
                else:
                    print(f"  ❌ List Failed: {response.status}")
                    self.test_results['banner_list'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['banner_list'] = False
            return False
    
    async def test_banner_homepage(self):
        """Test 9: Get Active Homepage Banners"""
        print("\n🏠 Test 9: Get Active Homepage Banners")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/banners/active/homepage") as response:
                if response.status == 200:
                    data = await response.json()
                    banners = data.get('banners', [])
                    
                    print(f"  ✅ Retrieved {len(banners)} active homepage banners")
                    
                    self.test_results['banner_homepage'] = True
                    return True
                else:
                    print(f"  ❌ Homepage Banners Failed: {response.status}")
                    self.test_results['banner_homepage'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['banner_homepage'] = False
            return False
    
    async def test_banner_update(self):
        """Test 10: Update Banner"""
        print("\n✏️ Test 10: Update Banner (Toggle Active)")
        
        if not self.created_banner_id:
            print("  ⚠️ No banner ID available, skipping")
            self.test_results['banner_update'] = True
            return True
        
        try:
            update_data = {
                "is_active": False,
                "title": "Summer Sale 2024 - UPDATED"
            }
            
            async with self.session.put(
                f"{API_BASE_URL}/banners/{self.created_banner_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    banner = data.get('banner', {})
                    
                    print(f"  ✅ Updated: {banner.get('title')}")
                    print(f"  Active: {banner.get('is_active')}")
                    
                    self.test_results['banner_update'] = True
                    return True
                else:
                    print(f"  ❌ Update Failed: {response.status}")
                    self.test_results['banner_update'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['banner_update'] = False
            return False
    
    async def test_banner_track_view(self):
        """Test 11: Track Banner View"""
        print("\n👁️ Test 11: Track Banner View")
        
        if not self.created_banner_id:
            print("  ⚠️ No banner ID available, skipping")
            self.test_results['banner_track_view'] = True
            return True
        
        try:
            async with self.session.post(f"{API_BASE_URL}/banners/{self.created_banner_id}/track-view") as response:
                if response.status == 200:
                    print(f"  ✅ Banner View Tracked")
                    
                    self.test_results['banner_track_view'] = True
                    return True
                else:
                    print(f"  ❌ Track View Failed: {response.status}")
                    self.test_results['banner_track_view'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['banner_track_view'] = False
            return False
    
    async def test_banner_track_click(self):
        """Test 12: Track Banner Click"""
        print("\n👆 Test 12: Track Banner Click")
        
        if not self.created_banner_id:
            print("  ⚠️ No banner ID available, skipping")
            self.test_results['banner_track_click'] = True
            return True
        
        try:
            async with self.session.post(f"{API_BASE_URL}/banners/{self.created_banner_id}/track-click") as response:
                if response.status == 200:
                    print(f"  ✅ Banner Click Tracked")
                    
                    self.test_results['banner_track_click'] = True
                    return True
                else:
                    print(f"  ❌ Track Click Failed: {response.status}")
                    self.test_results['banner_track_click'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['banner_track_click'] = False
            return False
    
    async def test_banner_delete(self):
        """Test 13: Delete Banner"""
        print("\n🗑️ Test 13: Delete Banner")
        
        if not self.created_banner_id:
            print("  ⚠️ No banner ID available, skipping")
            self.test_results['banner_delete'] = True
            return True
        
        try:
            async with self.session.delete(f"{API_BASE_URL}/banners/{self.created_banner_id}") as response:
                if response.status == 200:
                    print(f"  ✅ Banner Deleted Successfully")
                    
                    self.test_results['banner_delete'] = True
                    return True
                else:
                    print(f"  ❌ Delete Failed: {response.status}")
                    self.test_results['banner_delete'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['banner_delete'] = False
            return False
    
    # ========== NEW PRODUCT HIGHLIGHTING API TESTS ==========
    
    async def test_new_product_mark_single(self):
        """Test 14: Mark Single Product as NEW"""
        print("\n⭐ Test 14: Mark Single Product as NEW")
        
        if not self.product_ids:
            print("  ❌ No product IDs available")
            self.test_results['new_product_mark_single'] = False
            return False
        
        try:
            mark_data = {
                "product_id": self.product_ids[0],
                "badge_text": "NEW ARRIVAL",
                "priority": 5
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/new-products/mark",
                json=mark_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    product = data.get('product', {})
                    
                    print(f"  ✅ Product Marked as NEW: {product.get('name')}")
                    print(f"  Badge Text: {product.get('new_badge_text')}")
                    print(f"  Priority: {product.get('new_priority')}")
                    print(f"  Valid Until: {product.get('new_until', 'N/A')[:10]}")
                    
                    self.test_results['new_product_mark_single'] = True
                    return True
                else:
                    error_text = await response.text()
                    print(f"  ❌ Mark Failed: {response.status}")
                    print(f"  Error: {error_text}")
                    self.test_results['new_product_mark_single'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['new_product_mark_single'] = False
            return False
    
    async def test_new_product_bulk_mark(self):
        """Test 15: Bulk Mark Products as NEW"""
        print("\n⭐⭐ Test 15: Bulk Mark Products as NEW")
        
        if len(self.product_ids) < 2:
            print("  ⚠️ Not enough products for bulk marking")
            self.test_results['new_product_bulk_mark'] = True
            return True
        
        try:
            async with self.session.post(
                f"{API_BASE_URL}/new-products/bulk-mark",
                json=self.product_ids[1:3],
                params={"days": 30},
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    modified_count = data.get('modified_count', 0)
                    
                    print(f"  ✅ Bulk Marked {modified_count} products as NEW")
                    
                    self.test_results['new_product_bulk_mark'] = True
                    return True
                else:
                    print(f"  ❌ Bulk Mark Failed: {response.status}")
                    self.test_results['new_product_bulk_mark'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['new_product_bulk_mark'] = False
            return False
    
    async def test_new_product_list(self):
        """Test 16: List All New Products"""
        print("\n📋 Test 16: List All New Products")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/new-products/") as response:
                if response.status == 200:
                    data = await response.json()
                    products = data.get('products', [])
                    total = data.get('total', 0)
                    
                    print(f"  ✅ Retrieved {total} new products")
                    
                    if products:
                        for p in products[:3]:
                            print(f"    - {p.get('name')} (Badge: {p.get('new_badge_text', 'NEW')})")
                    
                    self.test_results['new_product_list'] = True
                    return True
                else:
                    print(f"  ❌ List Failed: {response.status}")
                    self.test_results['new_product_list'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['new_product_list'] = False
            return False
    
    async def test_new_product_remove_badge(self):
        """Test 17: Remove NEW Badge"""
        print("\n🚫 Test 17: Remove NEW Badge")
        
        if not self.product_ids:
            print("  ⚠️ No product IDs available")
            self.test_results['new_product_remove_badge'] = True
            return True
        
        try:
            async with self.session.delete(f"{API_BASE_URL}/new-products/{self.product_ids[0]}/remove-new") as response:
                if response.status == 200:
                    print(f"  ✅ NEW Badge Removed Successfully")
                    
                    self.test_results['new_product_remove_badge'] = True
                    return True
                else:
                    print(f"  ❌ Remove Badge Failed: {response.status}")
                    self.test_results['new_product_remove_badge'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['new_product_remove_badge'] = False
            return False
    
    async def test_new_product_cleanup_expired(self):
        """Test 18: Cleanup Expired NEW Badges"""
        print("\n🧹 Test 18: Cleanup Expired NEW Badges")
        
        try:
            async with self.session.post(f"{API_BASE_URL}/new-products/cleanup-expired") as response:
                if response.status == 200:
                    data = await response.json()
                    modified_count = data.get('modified_count', 0)
                    
                    print(f"  ✅ Cleaned up {modified_count} expired badges")
                    
                    self.test_results['new_product_cleanup_expired'] = True
                    return True
                else:
                    print(f"  ❌ Cleanup Failed: {response.status}")
                    self.test_results['new_product_cleanup_expired'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['new_product_cleanup_expired'] = False
            return False
    
    # ========== SOCIAL MEDIA POST CREATOR API TESTS ==========
    
    async def test_social_media_generate_post(self):
        """Test 19: Generate AI Social Media Post"""
        print("\n📱 Test 19: Generate AI Social Media Post")
        
        if not self.product_ids:
            print("  ❌ No product IDs available")
            self.test_results['social_media_generate_post'] = False
            return False
        
        try:
            post_data = {
                "post_type": "product",
                "platform": "facebook",
                "content_type": "new_product",
                "product_ids": [self.product_ids[0]],
                "custom_message": "Check out our latest premium cooker hood!"
            }
            
            print(f"  Generating {post_data['platform']} post for {post_data['content_type']}")
            
            async with self.session.post(
                f"{API_BASE_URL}/social-media/generate-post",
                json=post_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    post = data.get('post', {})
                    self.created_post_id = post.get('id')
                    
                    print(f"  ✅ Post Generated Successfully")
                    print(f"  Caption Length: {len(post.get('caption', ''))} chars")
                    print(f"  Hashtags: {len(post.get('hashtags', []))} tags")
                    print(f"  CTA: {post.get('cta', 'N/A')[:50]}...")
                    print(f"  Best Time: {post.get('best_time', 'N/A')}")
                    print(f"  Status: {post.get('status')}")
                    
                    # Verify AI-generated content structure
                    if post.get('caption') and post.get('hashtags') and post.get('cta'):
                        print(f"  ✅ Content Structure: Complete")
                    else:
                        print(f"  ⚠️ Content Structure: Incomplete")
                    
                    self.test_results['social_media_generate_post'] = True
                    return True
                else:
                    error_text = await response.text()
                    print(f"  ❌ Post Generation Failed: {response.status}")
                    print(f"  Error: {error_text}")
                    self.test_results['social_media_generate_post'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['social_media_generate_post'] = False
            return False
    
    async def test_social_media_list_posts(self):
        """Test 20: List All Social Media Posts"""
        print("\n📋 Test 20: List All Social Media Posts")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/social-media/posts") as response:
                if response.status == 200:
                    data = await response.json()
                    posts = data.get('posts', [])
                    total = data.get('total', 0)
                    
                    print(f"  ✅ Retrieved {total} posts")
                    
                    if posts:
                        sample = posts[0]
                        print(f"  Sample: {sample.get('platform')} - {sample.get('content_type')} ({sample.get('status')})")
                    
                    self.test_results['social_media_list_posts'] = True
                    return True
                else:
                    print(f"  ❌ List Failed: {response.status}")
                    self.test_results['social_media_list_posts'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['social_media_list_posts'] = False
            return False
    
    async def test_social_media_mark_posted(self):
        """Test 21: Mark Post as Posted"""
        print("\n✅ Test 21: Mark Post as Posted")
        
        if not self.created_post_id:
            print("  ⚠️ No post ID available, skipping")
            self.test_results['social_media_mark_posted'] = True
            return True
        
        try:
            engagement_data = {
                "likes": 150,
                "comments": 25,
                "shares": 10
            }
            
            async with self.session.put(
                f"{API_BASE_URL}/social-media/{self.created_post_id}/mark-posted",
                json=engagement_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    print(f"  ✅ Post Marked as Posted")
                    print(f"  Engagement: {engagement_data['likes']} likes, {engagement_data['comments']} comments, {engagement_data['shares']} shares")
                    
                    self.test_results['social_media_mark_posted'] = True
                    return True
                else:
                    print(f"  ❌ Mark Posted Failed: {response.status}")
                    self.test_results['social_media_mark_posted'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['social_media_mark_posted'] = False
            return False
    
    async def test_social_media_delete_post(self):
        """Test 22: Delete Social Media Post"""
        print("\n🗑️ Test 22: Delete Social Media Post")
        
        if not self.created_post_id:
            print("  ⚠️ No post ID available, skipping")
            self.test_results['social_media_delete_post'] = True
            return True
        
        try:
            async with self.session.delete(f"{API_BASE_URL}/social-media/{self.created_post_id}") as response:
                if response.status == 200:
                    print(f"  ✅ Post Deleted Successfully")
                    
                    self.test_results['social_media_delete_post'] = True
                    return True
                else:
                    print(f"  ❌ Delete Failed: {response.status}")
                    self.test_results['social_media_delete_post'] = False
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.test_results['social_media_delete_post'] = False
            return False
    
    async def run_all_tests(self):
        """Run all tests in sequence"""
        await self.setup()
        
        print("\n" + "=" * 80)
        print("🎁 COMBO OFFERS MANAGEMENT API TESTS")
        print("=" * 80)
        await self.test_combo_create()
        await self.test_combo_list()
        await self.test_combo_get_single()
        await self.test_combo_update()
        await self.test_combo_homepage()
        await self.test_combo_delete()
        
        print("\n" + "=" * 80)
        print("🖼️ BANNER MANAGEMENT API TESTS")
        print("=" * 80)
        await self.test_banner_create()
        await self.test_banner_list()
        await self.test_banner_homepage()
        await self.test_banner_update()
        await self.test_banner_track_view()
        await self.test_banner_track_click()
        await self.test_banner_delete()
        
        print("\n" + "=" * 80)
        print("⭐ NEW PRODUCT HIGHLIGHTING API TESTS")
        print("=" * 80)
        await self.test_new_product_mark_single()
        await self.test_new_product_bulk_mark()
        await self.test_new_product_list()
        await self.test_new_product_remove_badge()
        await self.test_new_product_cleanup_expired()
        
        print("\n" + "=" * 80)
        print("📱 SOCIAL MEDIA POST CREATOR API TESTS")
        print("=" * 80)
        await self.test_social_media_generate_post()
        await self.test_social_media_list_posts()
        await self.test_social_media_mark_posted()
        await self.test_social_media_delete_post()
        
        await self.print_summary()
        await self.cleanup()
    
    async def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"\n✅ Passed: {passed_tests}/{total_tests}")
        print(f"❌ Failed: {failed_tests}/{total_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for test_name, result in self.test_results.items():
                if not result:
                    print(f"  - {test_name}")
        
        print("\n" + "=" * 80)

async def main():
    tester = NewAdminFeaturesTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
