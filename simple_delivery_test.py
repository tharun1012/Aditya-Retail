#!/usr/bin/env python3
"""
Simple E-Delivery Challan System Test
Tests the core delivery functionality with existing delivery person
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

class SimpleDeliveryTester:
    def __init__(self):
        self.session = None
        self.delivery_person_id = "04491d33-de3c-4901-8542-bebb825434f3"  # From previous test
        self.delivery_token = None
        self.delivery_headers = None
        self.cod_invoice_id = None
        self.challan_id = None
        self.store_code = 'BNS'
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print(f"🚀 Simple E-Delivery Challan System Test")
        print(f"🌐 Backend URL: {API_BASE_URL}")
        print("=" * 60)
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()

    async def test_delivery_person_login(self):
        """Test delivery person login"""
        print("\n🔐 Testing Delivery Person Login...")
        
        try:
            delivery_login = {
                "email": "delivery1@test.com",
                "password": "test123"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/auth/delivery-person/login",
                json=delivery_login,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    login_data = await response.json()
                    self.delivery_token = login_data.get('access_token')
                    delivery_user = login_data.get('user', {})
                    
                    self.delivery_headers = {
                        "Authorization": f"Bearer {self.delivery_token}",
                        "Content-Type": "application/json"
                    }
                    
                    print(f"   ✅ Login successful: {delivery_user.get('full_name')}")
                    print(f"   ✅ Role: {delivery_user.get('role')}")
                    print(f"   ✅ ID: {delivery_user.get('id')}")
                    
                    # Update delivery person ID from login response
                    self.delivery_person_id = delivery_user.get('id')
                    return True
                        
                else:
                    error_text = await response.text()
                    print(f"   ❌ Login failed: {response.status} - {error_text}")
                    return False
            
        except Exception as e:
            print(f"   ❌ Login error: {str(e)}")
            return False

    async def test_create_cod_invoice(self):
        """Test COD invoice creation"""
        print("\n💰 Testing COD Invoice Creation...")
        
        try:
            cod_invoice_data = {
                "customer": {
                    "name": "Rajesh Kumar",
                    "phone": "9876543210",
                    "email": "rajesh.kumar@example.com",
                    "address": "123 MG Road",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "pincode": "400001"
                },
                "items": [
                    {
                        "product_name": "Bosch Washing Machine",
                        "hsn_code": "8450",
                        "quantity": 1,
                        "rate": 45000,
                        "discount": 0,
                        "tax_rate": 18.0
                    }
                ],
                "payment_mode": "cod",
                "subtotal": 45000,
                "discount": 0,
                "delivery_charges": 500,
                "round_off": 0,
                "created_by": "Test Admin",
                "document_type": "invoice",
                "store_code": self.store_code,
                "is_cod": True,
                "is_pod": False
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/invoices/offline/create",
                json=cod_invoice_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    cod_data = await response.json()
                    self.cod_invoice_id = cod_data.get('invoice_id')
                    cod_invoice_number = cod_data.get('invoice_number')
                    print(f"   ✅ COD invoice created: {cod_invoice_number}")
                    print(f"   ✅ Invoice ID: {self.cod_invoice_id}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"   ❌ COD invoice creation failed: {response.status} - {error_text}")
                    return False
            
        except Exception as e:
            print(f"   ❌ COD invoice error: {str(e)}")
            return False

    async def test_create_delivery_challan(self):
        """Test delivery challan creation"""
        print("\n📋 Testing Delivery Challan Creation...")
        
        try:
            challan_data = {
                "invoice_id": self.cod_invoice_id,
                "delivery_person_id": self.delivery_person_id,
                "vehicle_number": "DL-01-AB-1234",
                "expected_delivery_date": "2024-12-02",
                "notes": "Handle with care - fragile item",
                "created_by": "Test Admin"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/delivery-challans/create",
                json=challan_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    challan_response = await response.json()
                    self.challan_id = challan_response.get('challan_id')
                    challan_number = challan_response.get('challan_number')
                    google_maps_link = challan_response.get('google_maps_link')
                    
                    print(f"   ✅ Challan created: {challan_number}")
                    print(f"   ✅ Challan ID: {self.challan_id}")
                    print(f"   ✅ Google Maps: {google_maps_link[:50]}...")
                    return True
                else:
                    error_text = await response.text()
                    print(f"   ❌ Challan creation failed: {response.status} - {error_text}")
                    return False
            
        except Exception as e:
            print(f"   ❌ Challan creation error: {str(e)}")
            return False

    async def test_get_assigned_deliveries(self):
        """Test getting assigned deliveries"""
        print("\n👤 Testing Assigned Deliveries...")
        
        try:
            async with self.session.get(
                f"{API_BASE_URL}/delivery-challans/delivery-person/assigned?delivery_person_id={self.delivery_person_id}"
            ) as response:
                if response.status == 200:
                    deliveries_data = await response.json()
                    challans = deliveries_data.get('challans', [])
                    direct_invoices = deliveries_data.get('direct_invoices', [])
                    total_pending = deliveries_data.get('total_pending', 0)
                    
                    print(f"   ✅ Assigned deliveries: {len(challans)} challans, {len(direct_invoices)} direct invoices")
                    print(f"   ✅ Total pending: {total_pending}")
                    
                    if len(challans) > 0:
                        print(f"   ✅ Found assigned challan")
                        return True
                    else:
                        print(f"   ⚠️ No challans found")
                        return False
                        
                else:
                    error_text = await response.text()
                    print(f"   ❌ Get assigned deliveries failed: {response.status} - {error_text}")
                    return False
            
        except Exception as e:
            print(f"   ❌ Assigned deliveries error: {str(e)}")
            return False

    async def test_collect_payment(self):
        """Test payment collection"""
        print("\n💳 Testing Payment Collection...")
        
        try:
            payment_data = {
                "amount_received": 53100.0,
                "payment_mode": "Cash",
                "reference_number": None,
                "notes": "Payment collected successfully"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/delivery-challans/{self.challan_id}/collect-payment?delivery_person_id={self.delivery_person_id}",
                json=payment_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    payment_response = await response.json()
                    payment_details = payment_response.get('payment_details', {})
                    
                    print(f"   ✅ Payment collected: ₹{payment_details.get('amount_received', 0):,.2f}")
                    print(f"   ✅ Payment mode: {payment_details.get('payment_mode')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"   ❌ Payment collection failed: {response.status} - {error_text}")
                    return False
            
        except Exception as e:
            print(f"   ❌ Payment collection error: {str(e)}")
            return False

    async def test_update_delivery_status(self):
        """Test delivery status update"""
        print("\n📸 Testing Delivery Status Update...")
        
        try:
            status_update = {
                "status": "delivered",
                "delivery_notes": "Package delivered successfully to customer",
                "delivered_by": self.delivery_person_id
            }
            
            async with self.session.put(
                f"{API_BASE_URL}/delivery-challans/{self.challan_id}/status",
                json=status_update,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    status_response = await response.json()
                    message = status_response.get('message', '')
                    
                    print(f"   ✅ Status updated: {message}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"   ❌ Status update failed: {response.status} - {error_text}")
                    return False
            
        except Exception as e:
            print(f"   ❌ Status update error: {str(e)}")
            return False

    async def test_delivery_link(self):
        """Test delivery link generation"""
        print("\n🔗 Testing Delivery Link...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/delivery-challans/{self.challan_id}/delivery-link") as response:
                if response.status == 200:
                    link_data = await response.json()
                    delivery_link = link_data.get('delivery_link')
                    challan_number = link_data.get('challan_number')
                    
                    print(f"   ✅ Delivery link: {delivery_link}")
                    print(f"   ✅ Challan number: {challan_number}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"   ❌ Delivery link failed: {response.status} - {error_text}")
                    return False
            
        except Exception as e:
            print(f"   ❌ Delivery link error: {str(e)}")
            return False

    async def run_test(self):
        """Run the simple delivery test"""
        await self.setup()
        
        tests = [
            ("Delivery Person Login", self.test_delivery_person_login),
            ("COD Invoice Creation", self.test_create_cod_invoice),
            ("Delivery Challan Creation", self.test_create_delivery_challan),
            ("Get Assigned Deliveries", self.test_get_assigned_deliveries),
            ("Payment Collection", self.test_collect_payment),
            ("Delivery Status Update", self.test_update_delivery_status),
            ("Delivery Link Generation", self.test_delivery_link)
        ]
        
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
        print("\n" + "=" * 60)
        print("🏁 SIMPLE DELIVERY TEST RESULTS")
        print("=" * 60)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if passed == len(tests):
            print(f"\n🎉 ALL TESTS PASSED! Core delivery functionality working!")
        else:
            print(f"\n⚠️ {failed} test(s) failed. Review issues above.")
        
        return passed, failed

async def main():
    """Main test runner"""
    tester = SimpleDeliveryTester()
    passed, failed = await tester.run_test()
    
    return {
        "passed": passed,
        "failed": failed,
        "total": passed + failed,
        "success_rate": (passed/(passed+failed)*100) if (passed+failed) > 0 else 0
    }

if __name__ == "__main__":
    asyncio.run(main())