#!/usr/bin/env python3
"""
Additional Backend Testing for Authentication and Order Management
Tests user registration, login, order creation, and shipping calculator
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://acct-workflow-1.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class AuthOrderTester:
    def __init__(self):
        self.session = None
        self.test_results = {}
        self.user_token = None
        self.test_user_id = str(uuid.uuid4())
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print(f"🚀 Starting Auth & Order Tests for: {API_BASE_URL}")
        print("=" * 80)
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
            
    async def test_user_registration(self):
        """Test User Registration"""
        print("\n👤 Testing User Registration...")
        
        try:
            user_data = {
                "username": f"testuser_{self.test_user_id[:8]}",
                "email": f"test_{self.test_user_id[:8]}@example.com",
                "password": "testpass123",
                "first_name": "Arjun",
                "last_name": "Sharma"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/auth/register",
                json=user_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ User Registration: User created with ID {data.get('user_id')}")
                    self.test_results['user_registration'] = True
                    return True
                else:
                    print(f"❌ User Registration failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    
        except Exception as e:
            print(f"❌ User Registration error: {str(e)}")
            
        self.test_results['user_registration'] = False
        return False
        
    async def test_user_login(self):
        """Test User Login"""
        print("\n🔐 Testing User Login...")
        
        try:
            login_data = {
                "username": f"testuser_{self.test_user_id[:8]}",
                "password": "testpass123"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.user_token = data.get('token')
                    user_info = data.get('user', {})
                    print(f"✅ User Login: Token received for {user_info.get('username')}")
                    print(f"👤 User Role: {user_info.get('role', 'customer')}")
                    self.test_results['user_login'] = True
                    return True
                else:
                    print(f"❌ User Login failed: {response.status}")
                    
        except Exception as e:
            print(f"❌ User Login error: {str(e)}")
            
        self.test_results['user_login'] = False
        return False
        
    async def test_current_user(self):
        """Test Get Current User"""
        print("\n👥 Testing Get Current User...")
        
        if not self.user_token:
            print("❌ No token available for current user test")
            self.test_results['current_user'] = False
            return False
            
        try:
            async with self.session.get(
                f"{API_BASE_URL}/auth/me",
                params={"token": self.user_token}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    user_info = data.get('user', {})
                    print(f"✅ Current User: {user_info.get('first_name')} {user_info.get('last_name')}")
                    print(f"📧 Email: {user_info.get('email')}")
                    self.test_results['current_user'] = True
                    return True
                else:
                    print(f"❌ Get Current User failed: {response.status}")
                    
        except Exception as e:
            print(f"❌ Get Current User error: {str(e)}")
            
        self.test_results['current_user'] = False
        return False
        
    async def test_shipping_calculator(self):
        """Test Shipping Calculator"""
        print("\n🚚 Testing Shipping Calculator...")
        
        test_cases = [
            {"pincode": "110001", "weight": 2.5, "cod": True, "description": "Delhi Metro with COD"},
            {"pincode": "400001", "weight": 1.0, "cod": False, "description": "Mumbai Metro without COD"},
            {"pincode": "560001", "weight": 3.0, "cod": True, "description": "Bangalore Metro with COD"},
            {"pincode": "302001", "weight": 1.5, "cod": False, "description": "Jaipur Non-Metro"}
        ]
        
        successful_tests = 0
        
        for test_case in test_cases:
            try:
                shipping_data = {
                    "pincode": test_case["pincode"],
                    "weight": test_case["weight"],
                    "cod": test_case["cod"]
                }
                
                async with self.session.post(
                    f"{API_BASE_URL}/shipping/calculate",
                    json=shipping_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        cost = data.get('shipping_cost', 0)
                        days = data.get('estimated_delivery_days', 0)
                        zone = data.get('zone', 'unknown')
                        
                        print(f"✅ {test_case['description']}: ₹{cost}, {days} days, {zone} zone")
                        successful_tests += 1
                    else:
                        print(f"❌ {test_case['description']} failed: {response.status}")
                        
            except Exception as e:
                print(f"❌ {test_case['description']} error: {str(e)}")
                
        if successful_tests >= 3:
            print(f"✅ Shipping Calculator: {successful_tests}/4 test cases passed")
            self.test_results['shipping_calculator'] = True
            return True
        else:
            print(f"❌ Shipping Calculator: Only {successful_tests}/4 test cases passed")
            self.test_results['shipping_calculator'] = False
            return False
            
    async def test_authenticated_cart(self):
        """Test Authenticated Cart Operations"""
        print("\n🛒 Testing Authenticated Cart...")
        
        if not self.user_token:
            print("❌ No token available for authenticated cart test")
            self.test_results['authenticated_cart'] = False
            return False
            
        try:
            # First get a product
            async with self.session.get(f"{API_BASE_URL}/products") as response:
                if response.status == 200:
                    data = await response.json()
                    products = data.get('products', [])
                    
                    if products:
                        product_id = products[1]['id']  # Use second product
                        
                        # Test authenticated add to cart
                        async with self.session.post(
                            f"{API_BASE_URL}/cart/add-auth",
                            params={
                                "product_id": product_id,
                                "quantity": 1,
                                "token": self.user_token,
                                "session_id": f"auth_{self.test_user_id}"
                            }
                        ) as cart_response:
                            if cart_response.status == 200:
                                cart_result = await cart_response.json()
                                print(f"✅ Authenticated Cart: Item added successfully")
                                print(f"🆔 Cart ID: {cart_result.get('cart_id')}")
                                self.test_results['authenticated_cart'] = True
                                return True
                            else:
                                print(f"❌ Authenticated cart add failed: {cart_response.status}")
                    else:
                        print("❌ No products available for cart testing")
                else:
                    print(f"❌ Could not fetch products: {response.status}")
                    
        except Exception as e:
            print(f"❌ Authenticated Cart error: {str(e)}")
            
        self.test_results['authenticated_cart'] = False
        return False
        
    async def test_order_creation(self):
        """Test Order Creation"""
        print("\n📦 Testing Order Creation...")
        
        try:
            # Get a product for the order
            async with self.session.get(f"{API_BASE_URL}/products") as response:
                if response.status == 200:
                    data = await response.json()
                    products = data.get('products', [])
                    
                    if products:
                        product = products[0]
                        
                        order_data = {
                            "user_id": self.test_user_id,
                            "session_id": f"order_{self.test_user_id}",
                            "customer_details": {
                                "name": "Arjun Sharma",
                                "email": f"test_{self.test_user_id[:8]}@example.com",
                                "phone": "+91-9876543210"
                            },
                            "billing_address": {
                                "street": "123 MG Road",
                                "city": "Bangalore",
                                "state": "Karnataka",
                                "pincode": "560001",
                                "country": "India"
                            },
                            "shipping_address": {
                                "street": "123 MG Road",
                                "city": "Bangalore", 
                                "state": "Karnataka",
                                "pincode": "560001",
                                "country": "India"
                            },
                            "items": [
                                {
                                    "product_id": product['id'],
                                    "product_name": product['name'],
                                    "quantity": 1,
                                    "price": product['price'],
                                    "total": product['price']
                                }
                            ],
                            "subtotal": product['price'],
                            "shipping_cost": 40,
                            "tax_amount": product['price'] * 0.18,
                            "discount_amount": 0,
                            "total_amount": product['price'] + 40 + (product['price'] * 0.18),
                            "payment_method": "cod"
                        }
                        
                        async with self.session.post(
                            f"{API_BASE_URL}/orders/create",
                            json=order_data,
                            headers={"Content-Type": "application/json"}
                        ) as order_response:
                            if order_response.status == 200:
                                order_result = await order_response.json()
                                order_id = order_result.get('order_id')
                                order_number = order_result.get('order_number')
                                
                                print(f"✅ Order Creation: Order {order_number} created")
                                print(f"🆔 Order ID: {order_id}")
                                
                                # Test order retrieval
                                async with self.session.get(f"{API_BASE_URL}/orders/{order_id}") as get_order_response:
                                    if get_order_response.status == 200:
                                        order_data = await get_order_response.json()
                                        order_info = order_data.get('order', {})
                                        print(f"✅ Order Retrieval: Order status is {order_info.get('order_status')}")
                                        print(f"💰 Order Total: ₹{order_info.get('total_amount', 0)}")
                                        
                                        self.test_results['order_creation'] = True
                                        return True
                                    else:
                                        print(f"❌ Order retrieval failed: {get_order_response.status}")
                            else:
                                print(f"❌ Order creation failed: {order_response.status}")
                                error_text = await order_response.text()
                                print(f"Error: {error_text}")
                    else:
                        print("❌ No products available for order testing")
                else:
                    print(f"❌ Could not fetch products: {response.status}")
                    
        except Exception as e:
            print(f"❌ Order Creation error: {str(e)}")
            
        self.test_results['order_creation'] = False
        return False
        
    async def test_product_images(self):
        """Test Product Images Accessibility"""
        print("\n🖼️ Testing Product Images...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/products") as response:
                if response.status == 200:
                    data = await response.json()
                    products = data.get('products', [])
                    
                    if products:
                        working_images = 0
                        total_images = 0
                        
                        for product in products[:5]:  # Test first 5 products
                            product_name = product.get('name', 'Unknown')
                            
                            # Check if product has image or images field
                            image_url = None
                            if 'image' in product and product['image']:
                                image_url = product['image']
                            elif 'images' in product and product['images'] and len(product['images']) > 0:
                                image_url = product['images'][0]
                                
                            if image_url:
                                total_images += 1
                                try:
                                    async with self.session.get(image_url) as img_response:
                                        if img_response.status == 200:
                                            working_images += 1
                                            print(f"✅ {product_name}: Image accessible")
                                        else:
                                            print(f"❌ {product_name}: Image not accessible ({img_response.status})")
                                except Exception as img_e:
                                    print(f"❌ {product_name}: Image error - {str(img_e)}")
                            else:
                                print(f"⚠️ {product_name}: No image URL found")
                                
                        if total_images > 0:
                            success_rate = (working_images / total_images) * 100
                            print(f"📊 Image Test Results: {working_images}/{total_images} images working ({success_rate:.1f}%)")
                            
                            if success_rate >= 80:  # 80% success rate threshold
                                self.test_results['product_images'] = True
                                return True
                            else:
                                print("❌ Too many image failures")
                        else:
                            print("⚠️ No images found to test")
                    else:
                        print("❌ No products found")
                else:
                    print(f"❌ Could not fetch products: {response.status}")
                    
        except Exception as e:
            print(f"❌ Product Images error: {str(e)}")
            
        self.test_results['product_images'] = False
        return False
        
    async def run_all_tests(self):
        """Run all authentication and order tests"""
        await self.setup()
        
        tests = [
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Current User", self.test_current_user),
            ("Shipping Calculator", self.test_shipping_calculator),
            ("Authenticated Cart", self.test_authenticated_cart),
            ("Order Creation", self.test_order_creation),
            ("Product Images", self.test_product_images)
        ]
        
        print(f"\n🧪 Running {len(tests)} Auth & Order Tests...")
        print("=" * 80)
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ {test_name} crashed: {str(e)}")
                failed += 1
                
        await self.cleanup()
        
        # Print final results
        print("\n" + "=" * 80)
        print("🏁 AUTH & ORDER TEST RESULTS")
        print("=" * 80)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {test_name.replace('_', ' ').title()}")
            
        return passed, failed, self.test_results

async def main():
    """Main test runner"""
    tester = AuthOrderTester()
    passed, failed, results = await tester.run_all_tests()
    
    return {
        "passed": passed,
        "failed": failed,
        "total": passed + failed,
        "success_rate": (passed/(passed+failed)*100) if (passed+failed) > 0 else 0,
        "results": results
    }

if __name__ == "__main__":
    asyncio.run(main())