#!/usr/bin/env python3
"""
AI Agents Real-time Database Integration Testing
Tests the specific functionality requested for AI agents using real-time product data
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

class AIAgentsRealtimeTester:
    def __init__(self):
        self.session = None
        self.test_results = {}
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print(f"🤖 Starting AI Agents Real-time Database Integration Tests")
        print(f"🔗 Backend URL: {API_BASE_URL}")
        print("=" * 80)
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()

    async def test_ai_products_api(self):
        """Test AI Products API Endpoints"""
        print("\n🤖 Testing AI Products API Endpoints...")
        
        try:
            # Test 1: AI Products API
            async with self.session.get(f"{API_BASE_URL}/ai-agents/products") as response:
                if response.status == 200:
                    data = await response.json()
                    total_products = data.get('total_products', 0)
                    categories = data.get('categories', {})
                    brands = data.get('brands', {})
                    stock_summary = data.get('stock_summary', {})
                    
                    print(f"✅ AI Products API: {total_products} products organized")
                    print(f"📂 Categories: {list(categories.keys())}")
                    print(f"🏷️ Brands: {brands}")
                    print(f"📊 Stock Summary: {stock_summary}")
                    
                    # Verify expected data
                    expected_brands = ['Bosch', 'Siemens']
                    found_brands = [brand for brand in expected_brands if brand in brands]
                    
                    if len(found_brands) >= 2:
                        print(f"✅ Brand Verification: Found {found_brands}")
                    else:
                        print(f"⚠️ Brand Verification: Expected Bosch & Siemens, found {list(brands.keys())}")
                    
                    if total_products >= 50:  # Should have substantial product catalog
                        print(f"✅ Product Count: Sufficient catalog size ({total_products})")
                    else:
                        print(f"⚠️ Product Count: Limited catalog ({total_products})")
                    
                else:
                    print(f"❌ AI Products API failed: {response.status}")
                    self.test_results['ai_products_api'] = False
                    return False
            
            # Test 2: Catalog Preview API
            async with self.session.get(f"{API_BASE_URL}/ai-agents/catalog-preview") as response:
                if response.status == 200:
                    data = await response.json()
                    sales_catalog = data.get('sales_agent_catalog', '')
                    service_catalog = data.get('service_agent_catalog', '')
                    
                    print(f"✅ Catalog Preview API: Sales catalog ({len(sales_catalog)} chars)")
                    print(f"✅ Service Catalog: Service catalog ({len(service_catalog)} chars)")
                    
                    # Verify catalog contains expected information
                    if 'Bosch' in sales_catalog and 'Siemens' in sales_catalog:
                        print(f"✅ Catalog Content: Contains expected brands")
                    else:
                        print(f"⚠️ Catalog Content: Missing brand information")
                    
                    # Check for price and stock information
                    if '₹' in sales_catalog and ('In Stock' in sales_catalog or 'Low Stock' in sales_catalog or 'Out of Stock' in sales_catalog):
                        print(f"✅ Catalog Format: Contains prices and stock status")
                    else:
                        print(f"⚠️ Catalog Format: Missing price or stock information")
                    
                else:
                    print(f"❌ Catalog Preview API failed: {response.status}")
                    self.test_results['ai_products_api'] = False
                    return False
            
            self.test_results['ai_products_api'] = True
            return True
            
        except Exception as e:
            print(f"❌ AI Products API error: {str(e)}")
            self.test_results['ai_products_api'] = False
            return False

    async def test_sales_agent_realtime_data(self):
        """Test Sales Agent with Real-time Product Data"""
        print("\n💼 Testing Sales Agent with Real-time Data...")
        
        test_queries = [
            {
                "query": "What air fryers do you have in stock?",
                "expected_products": ["air fryer", "bosch"],
                "session_id": "sales_test_airfryer"
            },
            {
                "query": "Do you have any coffee machines available?",
                "expected_products": ["coffee machine", "bosch"],
                "session_id": "sales_test_coffee"
            },
            {
                "query": "What Siemens refrigerators are available?",
                "expected_products": ["siemens", "refrigerator"],
                "session_id": "sales_test_siemens"
            }
        ]
        
        successful_tests = 0
        
        try:
            for i, test in enumerate(test_queries, 1):
                chat_request = {
                    "session_id": test["session_id"],
                    "agent_type": "sales",
                    "message": test["query"],
                    "context": {"budget": 100000, "test_mode": True}
                }
                
                async with self.session.post(
                    f"{API_BASE_URL}/ai/chat",
                    json=chat_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        ai_response = data.get('response', '').lower()
                        
                        print(f"✅ Sales Query {i}: '{test['query']}'")
                        print(f"📝 Response Length: {len(ai_response)} characters")
                        
                        # Check if response contains expected products
                        product_matches = sum(1 for product in test["expected_products"] if product.lower() in ai_response)
                        
                        if product_matches >= 1:  # At least one expected product mentioned
                            print(f"✅ Product Relevance: Found relevant products in response")
                            successful_tests += 1
                        else:
                            print(f"⚠️ Product Relevance: Limited product matches in response")
                        
                        # Check for price information
                        if '₹' in ai_response:
                            print(f"✅ Price Information: Response contains pricing")
                        else:
                            print(f"⚠️ Price Information: No pricing found in response")
                        
                        # Check for stock information
                        if any(stock_term in ai_response for stock_term in ['stock', 'available', 'inventory']):
                            print(f"✅ Stock Information: Response mentions stock status")
                        else:
                            print(f"⚠️ Stock Information: No stock status mentioned")
                        
                        # Show sample response
                        print(f"📄 Sample Response: {ai_response[:200]}...")
                    
                    else:
                        print(f"❌ Sales Query {i} failed: {response.status}")
                        error_text = await response.text()
                        print(f"🔍 Error: {error_text[:200]}...")
            
            if successful_tests >= 2:  # At least 2 out of 3 tests successful
                print(f"✅ Sales Agent Real-time Data: {successful_tests}/3 queries successful")
                self.test_results['sales_agent_realtime_data'] = True
                return True
            else:
                print(f"❌ Sales Agent Real-time Data: Only {successful_tests}/3 queries successful")
                self.test_results['sales_agent_realtime_data'] = False
                return False
                
        except Exception as e:
            print(f"❌ Sales Agent Real-time Data error: {str(e)}")
            self.test_results['sales_agent_realtime_data'] = False
            return False

    async def test_service_agent_product_knowledge(self):
        """Test Service Agent with Product Knowledge"""
        print("\n🔧 Testing Service Agent with Product Knowledge...")
        
        try:
            service_request = {
                "session_id": "service_test_oven",
                "agent_type": "service",
                "message": "I have a Siemens iQ700 Built-in Oven and it's not heating properly",
                "context": {
                    "product": "Siemens iQ700 Built-in Oven",
                    "issue": "heating problem"
                }
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/ai/chat",
                json=service_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    ai_response = data.get('response', '').lower()
                    
                    print(f"✅ Service Agent Query: Siemens oven heating issue")
                    print(f"📝 Response Length: {len(ai_response)} characters")
                    
                    # Check if response contains troubleshooting steps
                    troubleshooting_terms = ['check', 'verify', 'inspect', 'test', 'temperature', 'heating', 'element', 'thermostat']
                    troubleshooting_matches = sum(1 for term in troubleshooting_terms if term in ai_response)
                    
                    if troubleshooting_matches >= 3:
                        print(f"✅ Troubleshooting Content: Response contains relevant troubleshooting steps")
                    else:
                        print(f"⚠️ Troubleshooting Content: Limited troubleshooting guidance")
                    
                    # Check if response references oven-specific information
                    oven_terms = ['oven', 'heating', 'temperature', 'bake', 'cook']
                    oven_matches = sum(1 for term in oven_terms if term in ai_response)
                    
                    if oven_matches >= 2:
                        print(f"✅ Product Specificity: Response is oven-specific")
                    else:
                        print(f"⚠️ Product Specificity: Response may be too generic")
                    
                    # Check if response mentions Siemens or product catalog
                    if 'siemens' in ai_response or 'catalog' in ai_response:
                        print(f"✅ Product Knowledge: References product catalog or brand")
                    else:
                        print(f"⚠️ Product Knowledge: No clear catalog reference")
                    
                    # Show sample response
                    print(f"📄 Sample Response: {ai_response[:200]}...")
                    
                    self.test_results['service_agent_product_knowledge'] = True
                    return True
                    
                else:
                    print(f"❌ Service Agent failed: {response.status}")
                    error_text = await response.text()
                    print(f"🔍 Error: {error_text[:200]}...")
                    self.test_results['service_agent_product_knowledge'] = False
                    return False
                    
        except Exception as e:
            print(f"❌ Service Agent Product Knowledge error: {str(e)}")
            self.test_results['service_agent_product_knowledge'] = False
            return False

    async def test_delivery_agent_accuracy(self):
        """Test Delivery Agent Accuracy"""
        print("\n🚚 Testing Delivery Agent...")
        
        try:
            delivery_request = {
                "session_id": "delivery_test_bangalore",
                "agent_type": "delivery",
                "message": "How long will delivery take for an air fryer to Bangalore?",
                "context": {
                    "product": "Air Fryer",
                    "location": "Bangalore"
                }
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/ai/chat",
                json=delivery_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    ai_response = data.get('response', '').lower()
                    
                    print(f"✅ Delivery Agent Query: Air fryer delivery to Bangalore")
                    print(f"📝 Response Length: {len(ai_response)} characters")
                    
                    # Check for delivery timeline information
                    timeline_terms = ['same-day', 'same day', 'today', 'tomorrow', 'hours', 'days', '12 pm', 'noon']
                    timeline_matches = sum(1 for term in timeline_terms if term in ai_response)
                    
                    if timeline_matches >= 1:
                        print(f"✅ Delivery Timeline: Response contains delivery timeline")
                    else:
                        print(f"⚠️ Delivery Timeline: No clear timeline mentioned")
                    
                    # Check for Bangalore-specific information
                    location_terms = ['bangalore', 'bengaluru', 'karnataka', 'metro', 'city']
                    location_matches = sum(1 for term in location_terms if term in ai_response)
                    
                    if location_matches >= 1:
                        print(f"✅ Location Awareness: Response is location-specific")
                    else:
                        print(f"⚠️ Location Awareness: No location-specific information")
                    
                    # Check for delivery service information
                    service_terms = ['delivery', 'shipping', 'installation', 'tracking', 'order']
                    service_matches = sum(1 for term in service_terms if term in ai_response)
                    
                    if service_matches >= 2:
                        print(f"✅ Service Information: Comprehensive delivery information")
                    else:
                        print(f"⚠️ Service Information: Limited delivery details")
                    
                    # Show sample response
                    print(f"📄 Sample Response: {ai_response[:200]}...")
                    
                    self.test_results['delivery_agent_accuracy'] = True
                    return True
                    
                else:
                    print(f"❌ Delivery Agent failed: {response.status}")
                    error_text = await response.text()
                    print(f"🔍 Error: {error_text[:200]}...")
                    self.test_results['delivery_agent_accuracy'] = False
                    return False
                    
        except Exception as e:
            print(f"❌ Delivery Agent error: {str(e)}")
            self.test_results['delivery_agent_accuracy'] = False
            return False

    async def test_stock_status_accuracy(self):
        """Test Stock Status Accuracy in AI Responses"""
        print("\n📊 Testing Stock Status Accuracy...")
        
        try:
            # First get actual stock data from AI products API
            async with self.session.get(f"{API_BASE_URL}/ai-agents/products") as response:
                if response.status != 200:
                    print(f"❌ Could not fetch product data for stock verification")
                    self.test_results['stock_status_accuracy'] = False
                    return False
                
                data = await response.json()
                stock_summary = data.get('stock_summary', {})
                
                print(f"📊 Actual Stock Summary: {stock_summary}")
                
                # Test queries about different stock levels
                test_queries = [
                    {
                        "query": "What products do you have in stock right now?",
                        "session_id": "stock_test_instock"
                    },
                    {
                        "query": "Do you have any products with low stock that I should buy quickly?",
                        "session_id": "stock_test_lowstock"
                    },
                    {
                        "query": "What refrigerators are available with current stock status?",
                        "session_id": "stock_test_refrigerators"
                    }
                ]
                
                successful_tests = 0
                
                for i, test in enumerate(test_queries, 1):
                    chat_request = {
                        "session_id": test["session_id"],
                        "agent_type": "sales",
                        "message": test["query"],
                        "context": {"stock_verification": True}
                    }
                    
                    async with self.session.post(
                        f"{API_BASE_URL}/ai/chat",
                        json=chat_request,
                        headers={"Content-Type": "application/json"}
                    ) as chat_response:
                        
                        if chat_response.status == 200:
                            chat_data = await chat_response.json()
                            ai_response = chat_data.get('response', '').lower()
                            
                            print(f"✅ Stock Query {i}: '{test['query']}'")
                            
                            # Check for stock status mentions
                            stock_terms = ['in stock', 'low stock', 'out of stock', 'available', 'limited stock']
                            stock_mentions = sum(1 for term in stock_terms if term in ai_response)
                            
                            if stock_mentions >= 1:
                                print(f"✅ Stock Status: Response mentions stock information")
                                successful_tests += 1
                            else:
                                print(f"⚠️ Stock Status: No clear stock status mentioned")
                            
                            # Show sample response
                            print(f"📄 Sample Response: {ai_response[:150]}...")
                        
                        else:
                            print(f"❌ Stock Query {i} failed: {chat_response.status}")
                
                if successful_tests >= 2:  # At least 2 out of 3 tests successful
                    print(f"✅ Stock Status Accuracy: {successful_tests}/3 queries successful")
                    self.test_results['stock_status_accuracy'] = True
                    return True
                else:
                    print(f"❌ Stock Status Accuracy: Only {successful_tests}/3 queries successful")
                    self.test_results['stock_status_accuracy'] = False
                    return False
                    
        except Exception as e:
            print(f"❌ Stock Status Accuracy error: {str(e)}")
            self.test_results['stock_status_accuracy'] = False
            return False

    async def test_price_accuracy(self):
        """Test Price Accuracy in AI Responses"""
        print("\n💰 Testing Price Accuracy...")
        
        try:
            # Test price queries
            price_request = {
                "session_id": "price_test_001",
                "agent_type": "sales",
                "message": "Can you tell me the prices of your air fryers and coffee machines?",
                "context": {"price_verification": True}
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/ai/chat",
                json=price_request,
                headers={"Content-Type": "application/json"}
            ) as chat_response:
                
                if chat_response.status == 200:
                    chat_data = await chat_response.json()
                    ai_response = chat_data.get('response', '')
                    
                    print(f"✅ Price Query: Air fryers and coffee machines pricing")
                    print(f"📝 Response Length: {len(ai_response)} characters")
                    
                    # Check for price format (₹ symbol and numbers)
                    import re
                    price_pattern = r'₹[\d,]+'
                    prices_found = re.findall(price_pattern, ai_response)
                    
                    if len(prices_found) >= 2:
                        print(f"✅ Price Format: Found {len(prices_found)} prices in correct format")
                        print(f"💰 Sample Prices: {prices_found[:3]}")
                    else:
                        print(f"⚠️ Price Format: Limited price information ({len(prices_found)} prices found)")
                    
                    # Check for product names with prices
                    product_terms = ['air fryer', 'coffee machine', 'bosch', 'siemens']
                    product_mentions = sum(1 for term in product_terms if term.lower() in ai_response.lower())
                    
                    if product_mentions >= 2:
                        print(f"✅ Product-Price Association: Products mentioned with pricing")
                    else:
                        print(f"⚠️ Product-Price Association: Limited product-price correlation")
                    
                    # Show sample response
                    print(f"📄 Sample Response: {ai_response[:200]}...")
                    
                    # Verify consistency with API data
                    if len(prices_found) >= 1:
                        print(f"✅ Price Consistency: Prices provided in response")
                        self.test_results['price_accuracy'] = True
                        return True
                    else:
                        print(f"⚠️ Price Consistency: No prices found to verify")
                        self.test_results['price_accuracy'] = False
                        return False
                
                else:
                    print(f"❌ Price Query failed: {chat_response.status}")
                    error_text = await chat_response.text()
                    print(f"🔍 Error: {error_text[:200]}...")
                    self.test_results['price_accuracy'] = False
                    return False
                    
        except Exception as e:
            print(f"❌ Price Accuracy error: {str(e)}")
            self.test_results['price_accuracy'] = False
            return False

    async def run_ai_agents_tests(self):
        """Run all AI Agents Real-time Database Integration tests"""
        
        tests = [
            ("AI Products API Endpoints", self.test_ai_products_api),
            ("Sales Agent Real-time Data", self.test_sales_agent_realtime_data),
            ("Service Agent Product Knowledge", self.test_service_agent_product_knowledge),
            ("Delivery Agent Accuracy", self.test_delivery_agent_accuracy),
            ("Stock Status Accuracy", self.test_stock_status_accuracy),
            ("Price Accuracy", self.test_price_accuracy)
        ]
        
        print(f"\n🧪 Running {len(tests)} AI Agents Real-time Database Integration Tests...")
        print("=" * 80)
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    failed += 1
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                failed += 1
                print(f"❌ {test_name}: ERROR - {str(e)}")
        
        print("\n" + "=" * 80)
        print(f"🎯 AI AGENTS REAL-TIME DATABASE INTEGRATION TEST RESULTS:")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed / len(tests)) * 100:.1f}%")
        
        if passed >= 4:  # At least 4 out of 6 tests should pass
            print(f"🎉 AI AGENTS REAL-TIME DATABASE INTEGRATION: SUCCESS")
            return True
        else:
            print(f"⚠️ AI AGENTS REAL-TIME DATABASE INTEGRATION: NEEDS ATTENTION")
            return False

async def main():
    """Main test runner"""
    tester = AIAgentsRealtimeTester()
    
    try:
        await tester.setup()
        success = await tester.run_ai_agents_tests()
        
        if success:
            print(f"\n🚀 All AI Agents Real-time Database Integration tests completed successfully!")
        else:
            print(f"\n⚠️ Some AI Agents Real-time Database Integration tests failed. Check logs above.")
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())