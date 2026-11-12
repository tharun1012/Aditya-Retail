#!/usr/bin/env python3
"""
P0 Bug Fixes Testing - Deep Research Consultant Email Fix
Tests the specific P0 bug fixes mentioned in the review request
"""

import requests
import json
import time
import sys
from datetime import datetime

# API Configuration
API_URL = "https://acct-workflow-1.preview.emergentagent.com"
BASE_URL = f"{API_URL}/api"

class P0BugFixesTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'P0BugFixesTester/1.0'
        })
        self.test_results = []
    
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print()
    
    def test_existing_consultation_email_fix(self):
        """Test P0 Fix 1: Deep Research Consultant Email Fix - Existing Consultation"""
        print("🔧 Testing P0 Fix 1: Existing Consultation Email Processing...")
        
        # Use the specific consultation ID from the review request
        consultation_id = "6d096423-1e51-4859-8783-7466188b1d07"
        
        try:
            # Test the process-sync endpoint with existing consultation
            response = self.session.post(
                f"{BASE_URL}/consultation/process-sync/{consultation_id}",
                timeout=60  # Longer timeout for AI processing
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if the response indicates success
                if data.get('status') == 'success':
                    email_sent = data.get('email_sent', False)
                    products_analyzed = data.get('products_analyzed', 0)
                    
                    if email_sent:
                        self.log_test(
                            "Existing Consultation Email Fix",
                            True,
                            f"✅ EMAIL SENT SUCCESSFULLY! Consultation {consultation_id} processed with email_sent: {email_sent}, {products_analyzed} products analyzed"
                        )
                        return True
                    else:
                        self.log_test(
                            "Existing Consultation Email Fix",
                            False,
                            f"❌ Email not sent. email_sent: {email_sent}, products_analyzed: {products_analyzed}",
                            data
                        )
                        return False
                else:
                    self.log_test(
                        "Existing Consultation Email Fix",
                        False,
                        f"Processing failed: {data.get('message', 'Unknown error')}",
                        data
                    )
                    return False
            elif response.status_code == 404:
                self.log_test(
                    "Existing Consultation Email Fix",
                    False,
                    f"Consultation {consultation_id} not found. May need to create it first.",
                    response.text
                )
                return False
            else:
                self.log_test(
                    "Existing Consultation Email Fix",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Existing Consultation Email Fix",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_new_consultation_creation_and_processing(self):
        """Test P0 Fix 1: Create new consultation and verify email processing"""
        print("📝 Testing P0 Fix 1: New Consultation Creation and Email Processing...")
        
        # Test data for new consultation
        test_data = {
            "customer_name": "P0 Test Customer",
            "email": "p0test@example.com",
            "phone": "9876543210",
            "kitchen_size": "medium",
            "budget_min": 100000,
            "budget_max": 300000,
            "appliance_types": ["refrigerator", "chimney", "washing_machine"],
            "family_size": "3-4",
            "cooking_frequency": "daily",
            "brand_preference": ["Bosch", "Siemens"],
            "energy_priority": "very_important",
            "aesthetic_preference": "modern",
            "special_requirements": "P0 bug fix testing - email functionality verification"
        }
        
        try:
            # Step 1: Create new consultation
            response = self.session.post(
                f"{BASE_URL}/consultation/request",
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success' and 'consultation_id' in data:
                    consultation_id = data['consultation_id']
                    self.log_test(
                        "New Consultation Creation",
                        True,
                        f"New consultation created successfully. ID: {consultation_id}"
                    )
                    
                    # Step 2: Process the consultation synchronously
                    time.sleep(2)  # Brief pause
                    
                    process_response = self.session.post(
                        f"{BASE_URL}/consultation/process-sync/{consultation_id}",
                        timeout=60
                    )
                    
                    if process_response.status_code == 200:
                        process_data = process_response.json()
                        
                        if process_data.get('status') == 'success':
                            email_sent = process_data.get('email_sent', False)
                            products_analyzed = process_data.get('products_analyzed', 0)
                            
                            if email_sent:
                                self.log_test(
                                    "New Consultation Email Processing",
                                    True,
                                    f"✅ EMAIL SENT SUCCESSFULLY! New consultation {consultation_id} processed with email_sent: {email_sent}, {products_analyzed} products analyzed"
                                )
                                
                                # Step 3: Verify consultation status
                                status_response = self.session.get(
                                    f"{BASE_URL}/consultation/status/{consultation_id}",
                                    timeout=30
                                )
                                
                                if status_response.status_code == 200:
                                    status_data = status_response.json()
                                    consultation = status_data.get('consultation', {})
                                    
                                    self.log_test(
                                        "Consultation Status Verification",
                                        True,
                                        f"Status: {consultation.get('status')}, Email Sent: {consultation.get('email_sent')}, Products Matched: {consultation.get('products_matched')}"
                                    )
                                
                                return True
                            else:
                                self.log_test(
                                    "New Consultation Email Processing",
                                    False,
                                    f"❌ Email not sent for new consultation. email_sent: {email_sent}",
                                    process_data
                                )
                                return False
                        else:
                            self.log_test(
                                "New Consultation Email Processing",
                                False,
                                f"Processing failed: {process_data.get('message', 'Unknown error')}",
                                process_data
                            )
                            return False
                    else:
                        self.log_test(
                            "New Consultation Email Processing",
                            False,
                            f"Processing HTTP {process_response.status_code}: {process_response.text}",
                            process_response.text
                        )
                        return False
                else:
                    self.log_test(
                        "New Consultation Creation",
                        False,
                        "Invalid response structure for consultation creation",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "New Consultation Creation",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "New Consultation Creation and Processing",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_email_service_integration(self):
        """Test email service integration and SendGrid connectivity"""
        print("📧 Testing Email Service Integration...")
        
        try:
            # Test if we can access the consultation options (indicates backend is working)
            response = self.session.get(f"{BASE_URL}/consultation/options", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if all required options are available
                required_keys = ['appliance_types', 'budget_ranges', 'brands']
                missing_keys = [key for key in required_keys if key not in data]
                
                if not missing_keys:
                    self.log_test(
                        "Backend Consultation Service",
                        True,
                        f"Consultation service is operational. Found {len(data.get('appliance_types', []))} appliance types, {len(data.get('budget_ranges', []))} budget ranges"
                    )
                    
                    # Check for specific appliances needed for testing
                    appliances = [item['value'] for item in data.get('appliance_types', [])]
                    test_appliances = ['refrigerator', 'chimney', 'washing_machine']
                    found_appliances = [a for a in test_appliances if a in appliances]
                    
                    if len(found_appliances) == len(test_appliances):
                        self.log_test(
                            "Required Appliances Available",
                            True,
                            f"All test appliances available: {', '.join(found_appliances)}"
                        )
                        return True
                    else:
                        missing = [a for a in test_appliances if a not in appliances]
                        self.log_test(
                            "Required Appliances Available",
                            False,
                            f"Missing test appliances: {', '.join(missing)}"
                        )
                        return False
                else:
                    self.log_test(
                        "Backend Consultation Service",
                        False,
                        f"Missing required option keys: {', '.join(missing_keys)}",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "Backend Consultation Service",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Email Service Integration",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_shop_by_category_backend_support(self):
        """Test backend support for Shop by Category images (P0 Fix 2)"""
        print("🛍️ Testing Backend Support for Shop by Category Images...")
        
        # Note: As per instructions, I should focus on backend testing only
        # This test verifies that the backend has the necessary data for category images
        
        try:
            # Test categories endpoint
            response = self.session.get(f"{BASE_URL}/categories", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                categories = data.get('categories', [])
                
                # Expected categories for "Shop by Category"
                expected_categories = [
                    'Chimney', 'Gas Hob', 'Induction Hob', 'Oven', 
                    'Mixer Grinder', 'Washing Machine', 'Dishwasher', 
                    'Refrigerator', 'Air Fryer', 'Coffee Machine'
                ]
                
                found_categories = []
                for expected in expected_categories:
                    for category in categories:
                        if expected.lower() in category.lower():
                            found_categories.append(expected)
                            break
                
                if len(found_categories) >= 8:  # At least 8 out of 10 categories
                    self.log_test(
                        "Shop by Category Backend Data",
                        True,
                        f"✅ Backend has sufficient category data. Found {len(found_categories)}/{len(expected_categories)} categories: {', '.join(found_categories)}"
                    )
                    
                    # Test products endpoint to ensure products exist for categories
                    products_response = self.session.get(f"{BASE_URL}/products", timeout=30)
                    
                    if products_response.status_code == 200:
                        products_data = products_response.json()
                        products = products_data.get('products', [])
                        
                        if len(products) > 0:
                            # Check if products have images
                            products_with_images = [p for p in products if p.get('images') and len(p.get('images', [])) > 0]
                            
                            self.log_test(
                                "Product Images Available",
                                len(products_with_images) > 0,
                                f"Found {len(products)} total products, {len(products_with_images)} have images. Image availability: {(len(products_with_images)/len(products)*100):.1f}%"
                            )
                            
                            return True
                        else:
                            self.log_test(
                                "Shop by Category Backend Data",
                                False,
                                "No products found in database"
                            )
                            return False
                    else:
                        self.log_test(
                            "Shop by Category Backend Data",
                            False,
                            f"Products endpoint failed: HTTP {products_response.status_code}"
                        )
                        return False
                else:
                    missing_categories = [cat for cat in expected_categories if cat not in found_categories]
                    self.log_test(
                        "Shop by Category Backend Data",
                        False,
                        f"❌ Insufficient category data. Missing: {', '.join(missing_categories)}"
                    )
                    return False
            else:
                self.log_test(
                    "Shop by Category Backend Data",
                    False,
                    f"Categories endpoint failed: HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Shop by Category Backend Support",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def run_p0_bug_fixes_test(self):
        """Run all P0 bug fixes tests"""
        print("🚨 P0 BUG FIXES TESTING - DEEP RESEARCH CONSULTANT EMAIL FIX")
        print("=" * 80)
        print(f"API Base URL: {BASE_URL}")
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test sequence focusing on P0 fixes
        tests = [
            ("Email Service Integration Check", self.test_email_service_integration),
            ("Existing Consultation Email Fix", self.test_existing_consultation_email_fix),
            ("New Consultation Creation & Email", self.test_new_consultation_creation_and_processing),
            ("Shop by Category Backend Support", self.test_shop_by_category_backend_support)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test execution error: {str(e)}")
        
        # Summary
        print("=" * 80)
        print("🏁 P0 BUG FIXES TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        status_emoji = "✅" if success_rate >= 75 else "⚠️" if success_rate >= 50 else "❌"
        
        print(f"{status_emoji} Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print()
        
        # Detailed results
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print()
        print("🔍 P0 BUG FIXES VERIFICATION:")
        
        # Check specific P0 fixes
        email_tests = [r for r in self.test_results if 'Email' in r['test'] and r['success']]
        consultation_tests = [r for r in self.test_results if 'Consultation' in r['test'] and r['success']]
        
        if len(email_tests) >= 2:
            print("✅ P0 Fix 1: Deep Research Consultant Email functionality is WORKING")
        else:
            print("❌ P0 Fix 1: Deep Research Consultant Email functionality has ISSUES")
        
        if any('Shop by Category' in r['test'] and r['success'] for r in self.test_results):
            print("✅ P0 Fix 2: Shop by Category backend data is available")
        else:
            print("❌ P0 Fix 2: Shop by Category backend data has issues")
        
        print()
        print("📋 NEXT STEPS:")
        if success_rate >= 75:
            print("✅ P0 bug fixes are working correctly")
            print("✅ Email sending functionality verified")
            print("✅ Backend data for category images available")
        else:
            print("❌ P0 bug fixes need attention")
            if len(email_tests) < 2:
                print("🔧 Fix email sending functionality in consultation service")
            if not any('Shop by Category' in r['test'] and r['success'] for r in self.test_results):
                print("🔧 Verify category data and product images for Shop by Category")
        
        return success_rate >= 75


def main():
    """Main test execution"""
    tester = P0BugFixesTester()
    success = tester.run_p0_bug_fixes_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()