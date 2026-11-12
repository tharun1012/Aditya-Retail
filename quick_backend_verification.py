#!/usr/bin/env python3
"""
Quick Backend Verification for Aditya Retail
Verifies core systems are working after catalog testing
"""

import asyncio
import aiohttp
import json
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://acct-workflow-1.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

async def quick_verification():
    """Quick verification of core backend systems"""
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Quick Backend Verification...")
        
        tests_passed = 0
        tests_total = 0
        
        # Test 1: API Health
        tests_total += 1
        try:
            async with session.get(f"{API_BASE_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API Health: {data.get('message', 'OK')}")
                    tests_passed += 1
                else:
                    print(f"❌ API Health failed: {response.status}")
        except Exception as e:
            print(f"❌ API Health error: {str(e)}")
            
        # Test 2: Products API
        tests_total += 1
        try:
            async with session.get(f"{API_BASE_URL}/products") as response:
                if response.status == 200:
                    data = await response.json()
                    products = data.get('products', [])
                    print(f"✅ Products API: {len(products)} products")
                    tests_passed += 1
                else:
                    print(f"❌ Products API failed: {response.status}")
        except Exception as e:
            print(f"❌ Products API error: {str(e)}")
            
        # Test 3: AI Agent (Sales)
        tests_total += 1
        try:
            chat_request = {
                "session_id": str(uuid.uuid4()),
                "agent_type": "sales",
                "message": "Quick test - recommend a Bosch appliance",
                "context": {"test": True}
            }
            
            async with session.post(
                f"{API_BASE_URL}/ai/chat",
                json=chat_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    ai_response = data.get('response', '')
                    if len(ai_response) > 50:
                        print(f"✅ AI Sales Agent: Working ({len(ai_response)} chars)")
                        tests_passed += 1
                    else:
                        print(f"❌ AI Sales Agent: Poor response")
                else:
                    print(f"❌ AI Sales Agent failed: {response.status}")
        except Exception as e:
            print(f"❌ AI Sales Agent error: {str(e)}")
            
        # Test 4: Cart Operations
        tests_total += 1
        try:
            # Get a product first
            async with session.get(f"{API_BASE_URL}/products") as response:
                if response.status == 200:
                    data = await response.json()
                    products = data.get('products', [])
                    if products:
                        product_id = products[0]['id']
                        session_id = str(uuid.uuid4())
                        
                        # Add to cart
                        async with session.post(
                            f"{API_BASE_URL}/cart/add",
                            params={"product_id": product_id, "quantity": 1, "session_id": session_id}
                        ) as cart_response:
                            if cart_response.status == 200:
                                print(f"✅ Cart Operations: Add to cart working")
                                tests_passed += 1
                            else:
                                print(f"❌ Cart Operations failed: {cart_response.status}")
                    else:
                        print(f"❌ Cart Operations: No products available")
                else:
                    print(f"❌ Cart Operations: Products fetch failed")
        except Exception as e:
            print(f"❌ Cart Operations error: {str(e)}")
            
        print(f"\n📊 Quick Verification Results: {tests_passed}/{tests_total} systems working")
        return tests_passed, tests_total

if __name__ == "__main__":
    asyncio.run(quick_verification())