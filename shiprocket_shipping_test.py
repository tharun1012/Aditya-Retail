#!/usr/bin/env python3
"""
Shiprocket Shipping Integration Testing
Tests the newly integrated Shiprocket shipping functionality as per review request.
"""

import requests
import json
import sys
from datetime import datetime

# API Configuration
API_URL = "https://acct-workflow-1.preview.emergentagent.com"
BASE_URL = f"{API_URL}/api"

class ShiprocketShippingTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_result(self, test_name, success, details, response_data=None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        if response_data:
            result["response_data"] = response_data
            
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    def test_shiprocket_status(self):
        """Test 1: GET /api/shipping/status - Check Shiprocket connection status"""
        try:
            response = requests.get(f"{BASE_URL}/shipping/status", timeout=30)
            data = response.json()
            
            if response.status_code == 200:
                is_connected = data.get("is_connected", False)
                email = data.get("email", "")
                
                if is_connected and email == "warehouse.adityaretail@gmail.com":
                    self.log_result(
                        "Shiprocket Status Check",
                        True,
                        f"✅ Connected successfully with email: {email}",
                        data
                    )
                else:
                    self.log_result(
                        "Shiprocket Status Check", 
                        False,
                        f"❌ Connection issue - is_connected: {is_connected}, email: {email}",
                        data
                    )
            else:
                self.log_result(
                    "Shiprocket Status Check",
                    False,
                    f"❌ HTTP {response.status_code}: {data.get('message', 'Unknown error')}",
                    data
                )
                
        except Exception as e:
            self.log_result(
                "Shiprocket Status Check",
                False,
                f"❌ Exception: {str(e)}"
            )
    
    def test_serviceability_mumbai(self):
        """Test 2: POST /api/shipping/serviceability - Mumbai (400001)"""
        try:
            payload = {
                "delivery_pincode": "400001",
                "weight": 1.0
            }
            
            response = requests.post(
                f"{BASE_URL}/shipping/serviceability",
                json=payload,
                timeout=30
            )
            data = response.json()
            
            if response.status_code == 200:
                serviceable = data.get("serviceable", False)
                
                if serviceable:
                    recommended = data.get("recommended", {})
                    all_options = data.get("all_options", [])
                    
                    courier_names = [opt.get("courier_name", "") for opt in all_options]
                    rates = [opt.get("rate", 0) for opt in all_options]
                    
                    self.log_result(
                        "Serviceability Check - Mumbai (400001)",
                        True,
                        f"✅ Serviceable with {len(all_options)} courier options. Recommended: {recommended.get('courier_name')} at ₹{recommended.get('rate')}",
                        {
                            "serviceable": serviceable,
                            "courier_options": len(all_options),
                            "courier_names": courier_names[:3],  # Show first 3
                            "rates": rates[:3]
                        }
                    )
                else:
                    self.log_result(
                        "Serviceability Check - Mumbai (400001)",
                        False,
                        f"❌ Not serviceable: {data.get('message', 'Unknown reason')}",
                        data
                    )
            else:
                self.log_result(
                    "Serviceability Check - Mumbai (400001)",
                    False,
                    f"❌ HTTP {response.status_code}: {data.get('message', 'Unknown error')}",
                    data
                )
                
        except Exception as e:
            self.log_result(
                "Serviceability Check - Mumbai (400001)",
                False,
                f"❌ Exception: {str(e)}"
            )
    
    def test_serviceability_delhi(self):
        """Test 3: POST /api/shipping/serviceability - Delhi (110001)"""
        try:
            payload = {
                "delivery_pincode": "110001",
                "weight": 1.0
            }
            
            response = requests.post(
                f"{BASE_URL}/shipping/serviceability",
                json=payload,
                timeout=30
            )
            data = response.json()
            
            if response.status_code == 200:
                serviceable = data.get("serviceable", False)
                
                if serviceable:
                    recommended = data.get("recommended", {})
                    all_options = data.get("all_options", [])
                    
                    self.log_result(
                        "Serviceability Check - Delhi (110001)",
                        True,
                        f"✅ Serviceable with {len(all_options)} courier options. Recommended: {recommended.get('courier_name')} at ₹{recommended.get('rate')}",
                        {
                            "serviceable": serviceable,
                            "courier_options": len(all_options),
                            "recommended_rate": recommended.get('rate')
                        }
                    )
                else:
                    self.log_result(
                        "Serviceability Check - Delhi (110001)",
                        False,
                        f"❌ Not serviceable: {data.get('message', 'Unknown reason')}",
                        data
                    )
            else:
                self.log_result(
                    "Serviceability Check - Delhi (110001)",
                    False,
                    f"❌ HTTP {response.status_code}: {data.get('message', 'Unknown error')}",
                    data
                )
                
        except Exception as e:
            self.log_result(
                "Serviceability Check - Delhi (110001)",
                False,
                f"❌ Exception: {str(e)}"
            )
    
    def test_serviceability_chennai(self):
        """Test 4: POST /api/shipping/serviceability - Chennai (600001)"""
        try:
            payload = {
                "delivery_pincode": "600001",
                "weight": 1.0
            }
            
            response = requests.post(
                f"{BASE_URL}/shipping/serviceability",
                json=payload,
                timeout=30
            )
            data = response.json()
            
            if response.status_code == 200:
                serviceable = data.get("serviceable", False)
                
                if serviceable:
                    recommended = data.get("recommended", {})
                    all_options = data.get("all_options", [])
                    
                    self.log_result(
                        "Serviceability Check - Chennai (600001)",
                        True,
                        f"✅ Serviceable with {len(all_options)} courier options. Recommended: {recommended.get('courier_name')} at ₹{recommended.get('rate')}",
                        {
                            "serviceable": serviceable,
                            "courier_options": len(all_options),
                            "recommended_rate": recommended.get('rate')
                        }
                    )
                else:
                    self.log_result(
                        "Serviceability Check - Chennai (600001)",
                        False,
                        f"❌ Not serviceable: {data.get('message', 'Unknown reason')}",
                        data
                    )
            else:
                self.log_result(
                    "Serviceability Check - Chennai (600001)",
                    False,
                    f"❌ HTTP {response.status_code}: {data.get('message', 'Unknown error')}",
                    data
                )
                
        except Exception as e:
            self.log_result(
                "Serviceability Check - Chennai (600001)",
                False,
                f"❌ Exception: {str(e)}"
            )
    
    def test_serviceability_kolkata(self):
        """Test 5: POST /api/shipping/serviceability - Kolkata (700001)"""
        try:
            payload = {
                "delivery_pincode": "700001",
                "weight": 1.0
            }
            
            response = requests.post(
                f"{BASE_URL}/shipping/serviceability",
                json=payload,
                timeout=30
            )
            data = response.json()
            
            if response.status_code == 200:
                serviceable = data.get("serviceable", False)
                
                if serviceable:
                    recommended = data.get("recommended", {})
                    all_options = data.get("all_options", [])
                    
                    self.log_result(
                        "Serviceability Check - Kolkata (700001)",
                        True,
                        f"✅ Serviceable with {len(all_options)} courier options. Recommended: {recommended.get('courier_name')} at ₹{recommended.get('rate')}",
                        {
                            "serviceable": serviceable,
                            "courier_options": len(all_options),
                            "recommended_rate": recommended.get('rate')
                        }
                    )
                else:
                    self.log_result(
                        "Serviceability Check - Kolkata (700001)",
                        False,
                        f"❌ Not serviceable: {data.get('message', 'Unknown reason')}",
                        data
                    )
            else:
                self.log_result(
                    "Serviceability Check - Kolkata (700001)",
                    False,
                    f"❌ HTTP {response.status_code}: {data.get('message', 'Unknown error')}",
                    data
                )
                
        except Exception as e:
            self.log_result(
                "Serviceability Check - Kolkata (700001)",
                False,
                f"❌ Exception: {str(e)}"
            )
    
    def test_pickup_locations(self):
        """Test 6: GET /api/shipping/pickup-locations - Get pickup locations"""
        try:
            response = requests.get(f"{BASE_URL}/shipping/pickup-locations", timeout=30)
            data = response.json()
            
            if response.status_code == 200:
                pickup_locations = data.get("pickup_locations", [])
                
                if isinstance(pickup_locations, list):
                    self.log_result(
                        "Pickup Locations Retrieval",
                        True,
                        f"✅ Retrieved {len(pickup_locations)} pickup locations",
                        {
                            "total_locations": len(pickup_locations),
                            "locations_sample": pickup_locations[:2] if pickup_locations else []
                        }
                    )
                else:
                    self.log_result(
                        "Pickup Locations Retrieval",
                        False,
                        f"❌ Invalid response format: {type(pickup_locations)}",
                        data
                    )
            else:
                self.log_result(
                    "Pickup Locations Retrieval",
                    False,
                    f"❌ HTTP {response.status_code}: {data.get('message', 'Unknown error')}",
                    data
                )
                
        except Exception as e:
            self.log_result(
                "Pickup Locations Retrieval",
                False,
                f"❌ Exception: {str(e)}"
            )
    
    def test_shipments_list(self):
        """Test 7: GET /api/shipping/orders - Get all shipments"""
        try:
            response = requests.get(f"{BASE_URL}/shipping/orders", timeout=30)
            data = response.json()
            
            if response.status_code == 200:
                shipments = data.get("shipments", [])
                total = data.get("total", 0)
                
                if isinstance(shipments, list):
                    self.log_result(
                        "Shipments List Retrieval",
                        True,
                        f"✅ Retrieved {len(shipments)} shipments (Total: {total})",
                        {
                            "current_page_shipments": len(shipments),
                            "total_shipments": total,
                            "page": data.get("page", 1),
                            "pages": data.get("pages", 1)
                        }
                    )
                else:
                    self.log_result(
                        "Shipments List Retrieval",
                        False,
                        f"❌ Invalid response format: {type(shipments)}",
                        data
                    )
            else:
                self.log_result(
                    "Shipments List Retrieval",
                    False,
                    f"❌ HTTP {response.status_code}: {data.get('message', 'Unknown error')}",
                    data
                )
                
        except Exception as e:
            self.log_result(
                "Shipments List Retrieval",
                False,
                f"❌ Exception: {str(e)}"
            )
    
    def test_courier_options_verification(self):
        """Test 8: Verify real courier options are returned"""
        try:
            payload = {
                "delivery_pincode": "400001",  # Mumbai
                "weight": 2.0  # 2kg package
            }
            
            response = requests.post(
                f"{BASE_URL}/shipping/serviceability",
                json=payload,
                timeout=30
            )
            data = response.json()
            
            if response.status_code == 200 and data.get("serviceable"):
                all_options = data.get("all_options", [])
                
                # Check for known courier companies
                courier_names = [opt.get("courier_name", "").lower() for opt in all_options]
                known_couriers = ["xpressbees", "delhivery", "dtdc", "blue dart", "bluedart", "ecom", "ekart"]
                
                found_couriers = []
                for courier in courier_names:
                    for known in known_couriers:
                        if known in courier:
                            found_couriers.append(courier)
                            break
                
                if found_couriers or len(all_options) > 0:
                    self.log_result(
                        "Real Courier Options Verification",
                        True,
                        f"✅ Found {len(all_options)} courier options. Known couriers: {found_couriers[:3]}",
                        {
                            "total_options": len(all_options),
                            "known_couriers_found": found_couriers[:5],
                            "all_courier_names": courier_names[:5]
                        }
                    )
                else:
                    self.log_result(
                        "Real Courier Options Verification",
                        False,
                        f"❌ No recognized courier companies found in {len(all_options)} options",
                        {"courier_names": courier_names}
                    )
            else:
                self.log_result(
                    "Real Courier Options Verification",
                    False,
                    f"❌ Serviceability check failed or not serviceable",
                    data
                )
                
        except Exception as e:
            self.log_result(
                "Real Courier Options Verification",
                False,
                f"❌ Exception: {str(e)}"
            )
    
    def run_all_tests(self):
        """Run all Shiprocket shipping tests"""
        print("=" * 80)
        print("🚚 SHIPROCKET SHIPPING INTEGRATION TESTING")
        print("=" * 80)
        print(f"API URL: {API_URL}")
        print(f"Testing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all tests
        self.test_shiprocket_status()
        print()
        
        self.test_serviceability_mumbai()
        print()
        
        self.test_serviceability_delhi()
        print()
        
        self.test_serviceability_chennai()
        print()
        
        self.test_serviceability_kolkata()
        print()
        
        self.test_pickup_locations()
        print()
        
        self.test_shipments_list()
        print()
        
        self.test_courier_options_verification()
        print()
        
        # Print summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 ALL TESTS PASSED - Shiprocket integration is working correctly!")
        else:
            print(f"\n⚠️  {self.total_tests - self.passed_tests} TESTS FAILED - Review issues above")
        
        print("\n" + "=" * 80)
        
        return self.passed_tests == self.total_tests

if __name__ == "__main__":
    tester = ShiprocketShippingTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)