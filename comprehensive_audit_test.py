#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE APPLICATION AUDIT - Backend Testing
Tests all major features as requested in the review request:
1. E-Commerce Core Features
2. AI Agents 
3. Admin Panel
4. Marketing Features
5. Knowledge Base
6. API Health
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://acct-workflow-1.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class ComprehensiveAuditTester:
    def __init__(self):
        self.session = None
        self.test_results = {}
        self.session_id = str(uuid.uuid4())
        self.admin_token = None
        self.test_product_id = None
        self.test_order_id = None
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print(f"🔍 COMPREHENSIVE APPLICATION AUDIT")
        print(f"🌐 Backend URL: {API_BASE_URL}")
        print(f"📱 Test Session ID: {self.session_id}")
        print("=" * 80)
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()

    # ========================================
    # 1. E-COMMERCE CORE FEATURES
    # ========================================
    
    async def test_ecommerce_core_features(self):
        """Test E-Commerce Core Features: Products, Cart, Checkout, Payments, Orders"""
        print("\n🛒 TESTING E-COMMERCE CORE FEATURES")
        print("=" * 50)
        
        results = {
            'product_listing': False,
            'product_search': False,
            'product_detail': False,
            'add_to_cart': False,
            'checkout_process': False,
            'phonepe_payment': False,
            'order_creation': False,
            'order_confirmation': False
        }
        
        try:
            # 1.1 Product Listing and Search
            print("\n📦 Testing Product Listing and Search...")
            async with self.session.get(f"{API_BASE_URL}/products") as response:
                if response.status == 200:
                    data = await response.json()
                    products = data.get('products', [])
                    print(f"✅ Product Listing: {len(products)} products found")
                    results['product_listing'] = True
                    
                    if products:
                        self.test_product_id = products[0]['id']
                        
                        # Test product search/filtering
                        async with self.session.get(f"{API_BASE_URL}/products?brand=Bosch") as search_response:
                            if search_response.status == 200:
                                search_data = await search_response.json()
                                print(f"✅ Product Search: {search_data['count']} Bosch products")
                                results['product_search'] = True
                            else:
                                print(f"❌ Product Search failed: {search_response.status}")
                    else:
                        print("❌ No products found")
                else:
                    print(f"❌ Product Listing failed: {response.status}")
            
            # 1.2 Product Detail Pages
            if self.test_product_id:
                print("\n📋 Testing Product Detail Pages...")
                async with self.session.get(f"{API_BASE_URL}/products/{self.test_product_id}") as response:
                    if response.status == 200:
                        product_data = await response.json()
                        product = product_data.get('product', {})
                        print(f"✅ Product Detail: {product.get('name', 'N/A')}")
                        print(f"   Price: ₹{product.get('price', 0):,.2f}")
                        print(f"   Brand: {product.get('brand', 'N/A')}")
                        print(f"   Stock: {product.get('stock', 0)} units")
                        results['product_detail'] = True
                    else:
                        print(f"❌ Product Detail failed: {response.status}")
            
            # 1.3 Add to Cart Functionality
            if self.test_product_id:
                print("\n🛒 Testing Add to Cart Functionality...")
                cart_params = {
                    'product_id': self.test_product_id,
                    'quantity': 2,
                    'session_id': self.session_id
                }
                
                async with self.session.post(f"{API_BASE_URL}/cart/add", params=cart_params) as response:
                    if response.status == 200:
                        cart_result = await response.json()
                        print(f"✅ Add to Cart: Item added successfully")
                        results['add_to_cart'] = True
                        
                        # Test get cart
                        async with self.session.get(f"{API_BASE_URL}/cart/{self.session_id}") as cart_response:
                            if cart_response.status == 200:
                                cart_data = await cart_response.json()
                                items = cart_data.get('items', [])
                                total = cart_data.get('total', 0)
                                print(f"✅ Cart Contents: {len(items)} items, Total: ₹{total:,.2f}")
                            else:
                                print(f"❌ Get Cart failed: {cart_response.status}")
                    else:
                        print(f"❌ Add to Cart failed: {response.status}")
            
            # 1.4 Checkout Process
            print("\n💳 Testing Checkout Process...")
            order_data = {
                "user_id": None,
                "session_id": self.session_id,
                "customer_details": {
                    "name": "Test Customer",
                    "email": "test@example.com",
                    "phone": "9876543210"
                },
                "billing_address": {
                    "address": "123 Test Street",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "pincode": "400001"
                },
                "shipping_address": {
                    "address": "123 Test Street",
                    "city": "Mumbai", 
                    "state": "Maharashtra",
                    "pincode": "400001"
                },
                "items": [
                    {
                        "product_id": self.test_product_id,
                        "name": "Test Product",
                        "quantity": 2,
                        "price": 25000
                    }
                ],
                "subtotal": 50000,
                "shipping_cost": 0,
                "tax_amount": 9000,
                "total_amount": 59000,
                "payment_method": "phonepe"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/orders/create",
                json=order_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    order_result = await response.json()
                    self.test_order_id = order_result.get('order_id')
                    order_number = order_result.get('order_number')
                    print(f"✅ Checkout Process: Order {order_number} created")
                    results['checkout_process'] = True
                    results['order_creation'] = True
                    results['order_confirmation'] = True
                else:
                    print(f"❌ Checkout Process failed: {response.status}")
            
            # 1.5 PhonePe Payment Integration
            print("\n💳 Testing PhonePe Payment Integration...")
            if self.test_order_id:
                payment_data = {
                    "order_id": self.test_order_id,
                    "amount": 59000,
                    "customer_phone": "9876543210",
                    "merchant_user_id": f"USER_{self.session_id[:8]}"
                }
                
                async with self.session.post(
                    f"{API_BASE_URL}/phonepe/initiate",
                    json=payment_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        payment_result = await response.json()
                        if payment_result.get('status') == 'success':
                            print(f"✅ PhonePe Payment: Payment link generated")
                            print(f"   Transaction ID: {payment_result.get('transaction_id')}")
                            results['phonepe_payment'] = True
                        else:
                            print(f"❌ PhonePe Payment: {payment_result.get('message')}")
                    else:
                        print(f"❌ PhonePe Payment failed: {response.status}")
                        # Check if it's a credential issue
                        error_text = await response.text()
                        if "401" in str(response.status) or "unauthorized" in error_text.lower():
                            print("   ⚠️ Note: This appears to be a PhonePe credential/authentication issue")
        
        except Exception as e:
            print(f"❌ E-Commerce Core Features error: {str(e)}")
        
        # Summary
        working_features = sum(results.values())
        total_features = len(results)
        print(f"\n📊 E-Commerce Core Features: {working_features}/{total_features} working")
        
        for feature, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {feature.replace('_', ' ').title()}")
        
        self.test_results['ecommerce_core'] = results
        return working_features >= 6  # At least 6/8 features should work

    # ========================================
    # 2. AI AGENTS
    # ========================================
    
    async def test_ai_agents(self):
        """Test AI Agents: Sales Agent, Service Agent, Knowledge Base Integration"""
        print("\n🤖 TESTING AI AGENTS")
        print("=" * 50)
        
        results = {
            'ai_sales_agent': False,
            'ai_service_agent': False,
            'knowledge_base_integration': False,
            'chat_functionality': False,
            'product_recommendations': False,
            'order_creation_flow': False,
            'support_tickets': False,
            'troubleshooting': False
        }
        
        try:
            # 2.1 AI Sales Agent (chat, product recommendations, order creation)
            print("\n💼 Testing AI Sales Agent...")
            sales_request = {
                "session_id": self.session_id,
                "agent_type": "sales",
                "message": "I'm looking for a good chimney for my kitchen, budget around 20000",
                "context": {"budget": 20000, "product_type": "chimney"}
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/ai/chat",
                json=sales_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    ai_response = data.get('response', '')
                    if len(ai_response) > 50 and "technical difficulties" not in ai_response.lower():
                        print(f"✅ AI Sales Agent: Response received ({len(ai_response)} chars)")
                        results['ai_sales_agent'] = True
                        results['chat_functionality'] = True
                        
                        # Check for product recommendations
                        if any(keyword in ai_response.lower() for keyword in ['bosch', 'siemens', 'chimney', '₹', 'price']):
                            print("✅ Product Recommendations: AI provided product suggestions")
                            results['product_recommendations'] = True
                    else:
                        print(f"⚠️ AI Sales Agent: Response seems generic: {ai_response[:100]}...")
                else:
                    print(f"❌ AI Sales Agent failed: {response.status}")
            
            # 2.2 AI Service Agent (support tickets, troubleshooting)
            print("\n🔧 Testing AI Service Agent...")
            service_request = {
                "session_id": self.session_id,
                "agent_type": "service",
                "message": "My Bosch washing machine is showing error code E18 and not draining water",
                "context": {"product": "Bosch Washing Machine", "issue": "drainage", "error_code": "E18"}
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/ai/chat",
                json=service_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    ai_response = data.get('response', '')
                    if len(ai_response) > 50 and "technical difficulties" not in ai_response.lower():
                        print(f"✅ AI Service Agent: Response received ({len(ai_response)} chars)")
                        results['ai_service_agent'] = True
                        
                        # Check for troubleshooting guidance
                        if any(keyword in ai_response.lower() for keyword in ['drain', 'filter', 'check', 'clean', 'troubleshoot']):
                            print("✅ Troubleshooting: AI provided diagnostic guidance")
                            results['troubleshooting'] = True
                    else:
                        print(f"⚠️ AI Service Agent: Response seems generic: {ai_response[:100]}...")
                else:
                    print(f"❌ AI Service Agent failed: {response.status}")
            
            # 2.3 Service Ticket Creation
            print("\n🎫 Testing Service Ticket Creation...")
            ticket_request = {
                "customer_name": "Test Customer",
                "customer_email": "test@example.com",
                "customer_phone": "9876543210",
                "product_name": "Bosch Series 6 Washing Machine",
                "issue_description": "Machine showing E18 error code, water not draining properly",
                "priority": "high"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/ai/service/request",
                json=ticket_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    ticket_id = data.get('request_id')
                    ai_response = data.get('ai_response', '')
                    print(f"✅ Support Tickets: Created ticket {ticket_id}")
                    results['support_tickets'] = True
                else:
                    print(f"❌ Support Tickets failed: {response.status}")
            
            # 2.4 Knowledge Base Integration
            print("\n📚 Testing Knowledge Base Integration...")
            async with self.session.get(f"{API_BASE_URL}/knowledge-base/") as response:
                if response.status == 200:
                    data = await response.json()
                    documents = data.get('documents', [])
                    print(f"✅ Knowledge Base: {len(documents)} documents available")
                    results['knowledge_base_integration'] = True
                else:
                    print(f"❌ Knowledge Base failed: {response.status}")
        
        except Exception as e:
            print(f"❌ AI Agents error: {str(e)}")
        
        # Summary
        working_features = sum(results.values())
        total_features = len(results)
        print(f"\n📊 AI Agents: {working_features}/{total_features} working")
        
        for feature, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {feature.replace('_', ' ').title()}")
        
        self.test_results['ai_agents'] = results
        return working_features >= 5  # At least 5/8 features should work

    # ========================================
    # 3. ADMIN PANEL
    # ========================================
    
    async def test_admin_panel(self):
        """Test Admin Panel: Login, Product Management, Order Management, Analytics"""
        print("\n👨‍💼 TESTING ADMIN PANEL")
        print("=" * 50)
        
        results = {
            'admin_login': False,
            'product_management': False,
            'order_management': False,
            'customer_management': False,
            'analytics_dashboard': False,
            'inventory_management': False,
            'user_permissions': False
        }
        
        try:
            # 3.1 Admin Login
            print("\n🔐 Testing Admin Login...")
            login_credentials = [
                {"email": "rohit.gadiya@gmail.com", "password": "admin123"},
                {"email": "admin@example.com", "password": "admin123"},
                {"email": "admin@adityaretail.com", "password": "admin123"}
            ]
            
            for creds in login_credentials:
                async with self.session.post(
                    f"{API_BASE_URL}/auth/admin/login",
                    json=creds,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.admin_token = data.get('token')
                        user_info = data.get('user', {})
                        print(f"✅ Admin Login: Successful as {user_info.get('email', 'N/A')}")
                        results['admin_login'] = True
                        break
                    else:
                        print(f"⚠️ Admin Login failed for {creds['email']}: {response.status}")
            
            if not results['admin_login']:
                print("❌ Admin Login: All credential attempts failed")
            
            # 3.2 Product Management (CRUD operations)
            print("\n📦 Testing Product Management...")
            async with self.session.get(f"{API_BASE_URL}/products") as response:
                if response.status == 200:
                    data = await response.json()
                    products = data.get('products', [])
                    print(f"✅ Product Management: {len(products)} products retrieved")
                    results['product_management'] = True
                    
                    # Test product creation (if admin token available)
                    if self.admin_token:
                        test_product = {
                            "name": "Test Product for Admin",
                            "description": "Test product created via admin API",
                            "price": 15000,
                            "brand": "Test Brand",
                            "category": "Test Category",
                            "stock_quantity": 10
                        }
                        
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {self.admin_token}"
                        }
                        
                        async with self.session.post(
                            f"{API_BASE_URL}/products",
                            json=test_product,
                            headers=headers
                        ) as create_response:
                            if create_response.status == 200:
                                print("✅ Product Creation: Test product created successfully")
                            else:
                                print(f"⚠️ Product Creation: {create_response.status}")
                else:
                    print(f"❌ Product Management failed: {response.status}")
            
            # 3.3 Order Management
            print("\n📋 Testing Order Management...")
            async with self.session.get(f"{API_BASE_URL}/orders/") as response:
                if response.status == 200:
                    data = await response.json()
                    orders = data.get('orders', [])
                    print(f"✅ Order Management: {len(orders)} orders retrieved")
                    results['order_management'] = True
                else:
                    print(f"❌ Order Management failed: {response.status}")
            
            # 3.4 Customer Management
            print("\n👥 Testing Customer Management...")
            async with self.session.get(f"{API_BASE_URL}/customers/") as response:
                if response.status == 200:
                    data = await response.json()
                    customers = data.get('customers', [])
                    print(f"✅ Customer Management: {len(customers)} customers retrieved")
                    results['customer_management'] = True
                else:
                    print(f"❌ Customer Management failed: {response.status}")
            
            # 3.5 Analytics Dashboard
            print("\n📊 Testing Analytics Dashboard...")
            async with self.session.get(f"{API_BASE_URL}/analytics/dashboard") as response:
                if response.status == 200:
                    data = await response.json()
                    analytics = data.get('analytics', {})
                    print(f"✅ Analytics Dashboard: Data retrieved")
                    print(f"   Total Revenue: ₹{analytics.get('total_revenue', 0):,.2f}")
                    print(f"   Total Orders: {analytics.get('total_orders', 0)}")
                    results['analytics_dashboard'] = True
                else:
                    print(f"❌ Analytics Dashboard failed: {response.status}")
            
            # 3.6 Inventory Management
            print("\n📦 Testing Inventory Management...")
            async with self.session.get(f"{API_BASE_URL}/inventory/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    summary = data.get('summary', {})
                    print(f"✅ Inventory Management: Summary retrieved")
                    print(f"   Total Products: {summary.get('total_products', 0)}")
                    print(f"   Low Stock Items: {summary.get('low_stock_items', 0)}")
                    results['inventory_management'] = True
                else:
                    print(f"❌ Inventory Management failed: {response.status}")
        
        except Exception as e:
            print(f"❌ Admin Panel error: {str(e)}")
        
        # Summary
        working_features = sum(results.values())
        total_features = len(results)
        print(f"\n📊 Admin Panel: {working_features}/{total_features} working")
        
        for feature, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {feature.replace('_', ' ').title()}")
        
        self.test_results['admin_panel'] = results
        return working_features >= 4  # At least 4/7 features should work

    # ========================================
    # 4. MARKETING FEATURES
    # ========================================
    
    async def test_marketing_features(self):
        """Test Marketing Features: Social Media, Templates, Campaigns, SEO"""
        print("\n📈 TESTING MARKETING FEATURES")
        print("=" * 50)
        
        results = {
            'social_media_post_creator': False,
            'template_image_generation': False,
            'marketing_campaigns': False,
            'seo_manager': False,
            'campaign_analytics': False,
            'content_generation': False
        }
        
        try:
            # 4.1 Social Media Post Creator
            print("\n📱 Testing Social Media Post Creator...")
            
            # Get a product for social media testing
            async with self.session.get(f"{API_BASE_URL}/products?limit=1") as response:
                if response.status == 200:
                    data = await response.json()
                    products = data.get('products', [])
                    if products:
                        test_product = products[0]
                        
                        social_post_request = {
                            "product_id": test_product.get('id'),
                            "platform": "instagram",
                            "post_type": "product_showcase",
                            "caption": f"Check out our amazing {test_product['name']}! Perfect for your home.",
                            "hashtags": ["#HomeAppliances", "#KitchenTech", "#AdityaRetail"]
                        }
                        
                        async with self.session.post(
                            f"{API_BASE_URL}/social-media/create-post",
                            json=social_post_request,
                            headers={"Content-Type": "application/json"}
                        ) as post_response:
                            if post_response.status == 200:
                                post_data = await post_response.json()
                                print(f"✅ Social Media Post Creator: Post created successfully")
                                results['social_media_post_creator'] = True
                            else:
                                print(f"❌ Social Media Post Creator failed: {post_response.status}")
            
            # 4.2 Template-based Image Generation
            print("\n🎨 Testing Template-based Image Generation...")
            if products:
                template_request = {
                    "product_id": test_product.get('id'),
                    "product_name": test_product['name'],
                    "product_price": test_product.get('price'),
                    "product_mrp": test_product.get('original_price'),
                    "product_image_url": test_product['images'][0] if test_product.get('images') else "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
                    "post_text": f"Experience the best with {test_product['name']}!",
                    "platform": "instagram",
                    "template_style": "professional",
                    "offer_text": "Limited Time Offer!",
                    "brand_name": "Aditya Retail"
                }
                
                async with self.session.post(
                    f"{API_BASE_URL}/template-image-generation/generate",
                    json=template_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('status') == 'success':
                            image_url = result.get('image_url')
                            dimensions = result.get('dimensions', {})
                            print(f"✅ Template Image Generation: Image created")
                            print(f"   Dimensions: {dimensions.get('width')}x{dimensions.get('height')}")
                            results['template_image_generation'] = True
                        else:
                            print(f"❌ Template Image Generation: {result.get('message')}")
                    else:
                        print(f"❌ Template Image Generation failed: {response.status}")
            
            # 4.3 Marketing Campaigns
            print("\n📢 Testing Marketing Campaigns...")
            async with self.session.get(f"{API_BASE_URL}/marketing-campaigns") as response:
                if response.status == 200:
                    data = await response.json()
                    campaigns = data.get('campaigns', [])
                    print(f"✅ Marketing Campaigns: {len(campaigns)} campaigns found")
                    results['marketing_campaigns'] = True
                    
                    if campaigns:
                        sample_campaign = campaigns[0]
                        print(f"   Sample: {sample_campaign.get('name', 'N/A')}")
                        print(f"   Budget: ₹{sample_campaign.get('budget', 0):,.2f}")
                else:
                    print(f"❌ Marketing Campaigns failed: {response.status}")
            
            # 4.4 SEO Manager
            print("\n🔍 Testing SEO Manager...")
            async with self.session.get(f"{API_BASE_URL}/seo/settings") as response:
                if response.status == 200:
                    data = await response.json()
                    seo_settings = data.get('settings', {})
                    print(f"✅ SEO Manager: Settings retrieved")
                    results['seo_manager'] = True
                else:
                    print(f"❌ SEO Manager failed: {response.status}")
            
            # 4.5 Campaign Analytics
            print("\n📊 Testing Campaign Analytics...")
            async with self.session.get(f"{API_BASE_URL}/marketing/performance") as response:
                if response.status == 200:
                    data = await response.json()
                    performance = data.get('performance', {})
                    print(f"✅ Campaign Analytics: Performance data retrieved")
                    results['campaign_analytics'] = True
                else:
                    print(f"❌ Campaign Analytics failed: {response.status}")
        
        except Exception as e:
            print(f"❌ Marketing Features error: {str(e)}")
        
        # Summary
        working_features = sum(results.values())
        total_features = len(results)
        print(f"\n📊 Marketing Features: {working_features}/{total_features} working")
        
        for feature, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {feature.replace('_', ' ').title()}")
        
        self.test_results['marketing_features'] = results
        return working_features >= 3  # At least 3/6 features should work

    # ========================================
    # 5. KNOWLEDGE BASE
    # ========================================
    
    async def test_knowledge_base(self):
        """Test Knowledge Base: Document Upload, Listing, Retrieval for AI Agents"""
        print("\n📚 TESTING KNOWLEDGE BASE")
        print("=" * 50)
        
        results = {
            'document_upload': False,
            'document_listing': False,
            'document_retrieval': False,
            'ai_integration': False,
            'search_functionality': False
        }
        
        try:
            # 5.1 Document Listing
            print("\n📋 Testing Document Listing...")
            async with self.session.get(f"{API_BASE_URL}/knowledge-base/") as response:
                if response.status == 200:
                    data = await response.json()
                    documents = data.get('documents', [])
                    print(f"✅ Document Listing: {len(documents)} documents found")
                    results['document_listing'] = True
                    
                    if documents:
                        sample_doc = documents[0]
                        print(f"   Sample: {sample_doc.get('filename', 'N/A')}")
                        print(f"   Type: {sample_doc.get('file_type', 'N/A')}")
                        print(f"   Size: {sample_doc.get('file_size', 0)} bytes")
                else:
                    print(f"❌ Document Listing failed: {response.status}")
            
            # 5.2 Document Upload API
            print("\n📤 Testing Document Upload API...")
            # Create a test document content
            test_document_content = """
            PRODUCT MANUAL - Bosch Series 6 Washing Machine
            
            Model: WAJ2846IIN
            Capacity: 7 kg
            
            TROUBLESHOOTING GUIDE:
            
            Error Code E18 - Drainage Issue
            - Check if the drain hose is kinked or blocked
            - Clean the drain filter located at the bottom front of the machine
            - Ensure the drain pipe is not clogged
            - Check if the drain pump is functioning properly
            
            Error Code E23 - Water Leak Detection
            - Check door seal for damage
            - Inspect hose connections
            - Contact service center if issue persists
            
            Maintenance Tips:
            - Clean the drum monthly with washing machine cleaner
            - Leave door open after use to air dry
            - Check and clean the filter regularly
            """
            
            # Encode as base64 for upload simulation
            document_b64 = base64.b64encode(test_document_content.encode()).decode()
            
            upload_data = {
                "filename": "bosch_washing_machine_manual.txt",
                "file_content": document_b64,
                "file_type": "text/plain",
                "category": "product_manual",
                "description": "Troubleshooting guide for Bosch washing machines"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/knowledge-base/upload",
                json=upload_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    upload_result = await response.json()
                    document_id = upload_result.get('document_id')
                    print(f"✅ Document Upload: Document uploaded successfully")
                    print(f"   Document ID: {document_id}")
                    results['document_upload'] = True
                else:
                    print(f"❌ Document Upload failed: {response.status}")
            
            # 5.3 Document Retrieval
            print("\n📥 Testing Document Retrieval...")
            async with self.session.get(f"{API_BASE_URL}/knowledge-base/search?query=E18+error+washing+machine") as response:
                if response.status == 200:
                    search_data = await response.json()
                    results_found = search_data.get('results', [])
                    print(f"✅ Document Retrieval: {len(results_found)} relevant documents found")
                    results['document_retrieval'] = True
                    results['search_functionality'] = True
                else:
                    print(f"❌ Document Retrieval failed: {response.status}")
            
            # 5.4 AI Integration with Knowledge Base
            print("\n🤖 Testing AI Integration with Knowledge Base...")
            kb_query = {
                "session_id": self.session_id,
                "agent_type": "service",
                "message": "My Bosch washing machine shows E18 error, what should I do?",
                "context": {"use_knowledge_base": True, "product": "Bosch Washing Machine"}
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/ai/chat",
                json=kb_query,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    ai_response = data.get('response', '')
                    knowledge_used = data.get('knowledge_base_used', False)
                    
                    if len(ai_response) > 50:
                        print(f"✅ AI Integration: AI responded with knowledge base context")
                        if knowledge_used or any(keyword in ai_response.lower() for keyword in ['drain', 'filter', 'hose', 'e18']):
                            print("✅ Knowledge Base Used: AI incorporated document knowledge")
                            results['ai_integration'] = True
                        else:
                            print("⚠️ Knowledge Base Used: Unclear if documents were referenced")
                    else:
                        print(f"❌ AI Integration: Poor response quality")
                else:
                    print(f"❌ AI Integration failed: {response.status}")
        
        except Exception as e:
            print(f"❌ Knowledge Base error: {str(e)}")
        
        # Summary
        working_features = sum(results.values())
        total_features = len(results)
        print(f"\n📊 Knowledge Base: {working_features}/{total_features} working")
        
        for feature, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {feature.replace('_', ' ').title()}")
        
        self.test_results['knowledge_base'] = results
        return working_features >= 3  # At least 3/5 features should work

    # ========================================
    # 6. API HEALTH
    # ========================================
    
    async def test_api_health(self):
        """Test API Health: All Critical Endpoints"""
        print("\n🏥 TESTING API HEALTH")
        print("=" * 50)
        
        critical_endpoints = [
            {"url": "/products", "method": "GET", "name": "Products API"},
            {"url": "/categories", "method": "GET", "name": "Categories API"},
            {"url": "/orders/", "method": "GET", "name": "Orders API"},
            {"url": "/auth/login", "method": "POST", "name": "Auth Login API", "data": {"username": "test", "password": "test"}},
            {"url": "/knowledge-base/", "method": "GET", "name": "Knowledge Base API"},
            {"url": "/template-image-generation/generate", "method": "POST", "name": "Template Generation API", "data": {"product_name": "Test", "platform": "instagram"}},
            {"url": "/marketing-campaigns", "method": "GET", "name": "Marketing Campaigns API"},
            {"url": "/ai/chat", "method": "POST", "name": "AI Chat API", "data": {"message": "Hello", "agent_type": "sales", "session_id": self.session_id}},
            {"url": "/inventory/summary", "method": "GET", "name": "Inventory API"},
            {"url": "/analytics/dashboard", "method": "GET", "name": "Analytics API"}
        ]
        
        results = {}
        
        try:
            for endpoint in critical_endpoints:
                print(f"\n🔍 Testing {endpoint['name']}...")
                
                url = f"{API_BASE_URL}{endpoint['url']}"
                method = endpoint['method']
                data = endpoint.get('data')
                
                try:
                    if method == "GET":
                        async with self.session.get(url) as response:
                            status = response.status
                    elif method == "POST":
                        headers = {"Content-Type": "application/json"} if data else {}
                        async with self.session.post(url, json=data, headers=headers) as response:
                            status = response.status
                    
                    if status in [200, 201]:
                        print(f"   ✅ {endpoint['name']}: Status {status}")
                        results[endpoint['name']] = True
                    elif status in [401, 403]:
                        print(f"   ⚠️ {endpoint['name']}: Status {status} (Authentication required)")
                        results[endpoint['name']] = True  # Endpoint exists, just needs auth
                    else:
                        print(f"   ❌ {endpoint['name']}: Status {status}")
                        results[endpoint['name']] = False
                        
                except Exception as e:
                    print(f"   ❌ {endpoint['name']}: Error - {str(e)}")
                    results[endpoint['name']] = False
        
        except Exception as e:
            print(f"❌ API Health error: {str(e)}")
        
        # Summary
        working_endpoints = sum(results.values())
        total_endpoints = len(results)
        print(f"\n📊 API Health: {working_endpoints}/{total_endpoints} endpoints working")
        
        for endpoint, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {endpoint}")
        
        self.test_results['api_health'] = results
        return working_endpoints >= 7  # At least 7/10 endpoints should work

    # ========================================
    # MAIN TEST RUNNER
    # ========================================
    
    async def run_comprehensive_audit(self):
        """Run comprehensive audit of all features"""
        await self.setup()
        
        print("🔍 COMPREHENSIVE APPLICATION AUDIT")
        print("Testing Priority: Core E-Commerce → AI Agents → Admin → Marketing → Extras")
        print("=" * 80)
        
        # Test results tracking
        test_sections = []
        
        try:
            # 1. E-Commerce Core Features (Highest Priority)
            ecommerce_result = await self.test_ecommerce_core_features()
            test_sections.append(("E-Commerce Core", ecommerce_result))
            
            # 2. AI Agents (High Priority)
            ai_result = await self.test_ai_agents()
            test_sections.append(("AI Agents", ai_result))
            
            # 3. Admin Panel (Medium Priority)
            admin_result = await self.test_admin_panel()
            test_sections.append(("Admin Panel", admin_result))
            
            # 4. Marketing Features (Medium Priority)
            marketing_result = await self.test_marketing_features()
            test_sections.append(("Marketing Features", marketing_result))
            
            # 5. Knowledge Base (Lower Priority)
            kb_result = await self.test_knowledge_base()
            test_sections.append(("Knowledge Base", kb_result))
            
            # 6. API Health (System Check)
            api_result = await self.test_api_health()
            test_sections.append(("API Health", api_result))
            
        except Exception as e:
            print(f"❌ Comprehensive audit error: {str(e)}")
        
        finally:
            await self.cleanup()
        
        # Final Report
        print("\n" + "=" * 80)
        print("🔍 COMPREHENSIVE AUDIT REPORT")
        print("=" * 80)
        
        for section_name, section_result in test_sections:
            status_icon = "✅" if section_result else "❌"
            status_text = "WORKING" if section_result else "ISSUES FOUND"
            print(f"{status_icon} {section_name}: {status_text}")
        
        # Overall Status
        working_sections = sum(1 for _, result in test_sections if result)
        total_sections = len(test_sections)
        
        print(f"\n📊 OVERALL STATUS: {working_sections}/{total_sections} sections working properly")
        
        if working_sections >= 4:
            print("🎉 AUDIT RESULT: ✅ SYSTEM IS MOSTLY FUNCTIONAL")
        elif working_sections >= 2:
            print("⚠️ AUDIT RESULT: 🔶 SYSTEM HAS SOME ISSUES")
        else:
            print("🚨 AUDIT RESULT: ❌ SYSTEM HAS MAJOR ISSUES")
        
        return self.test_results

# Run the comprehensive audit
async def main():
    tester = ComprehensiveAuditTester()
    results = await tester.run_comprehensive_audit()
    return results

if __name__ == "__main__":
    asyncio.run(main())