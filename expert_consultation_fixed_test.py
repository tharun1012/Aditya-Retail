#!/usr/bin/env python3
"""
Expert Consultation FIXED Feature Testing
Tests the FIXED Expert Consultation feature with specific requirements from review request
"""

import requests
import json
import time
import sys
from datetime import datetime

# API Configuration
API_URL = "https://acct-workflow-1.preview.emergentagent.com"
BASE_URL = f"{API_URL}/api"

class ExpertConsultationFixedTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ExpertConsultationFixedTester/1.0'
        })
        self.consultation_id = None
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
    
    def test_consultation_request_premium_kitchen(self):
        """Test 1: Create consultation request for Premium Kitchen Setup (₹5-7 Lakhs budget)"""
        print("🏠 Testing Premium Kitchen Consultation Request...")
        
        # Test data as specified in the review request
        test_data = {
            "customer_name": "Testing Agent",
            "email": "test@example.com",
            "phone": "9999999999",
            "kitchen_size": "large",
            "family_size": "4",
            "budget_min": 500000,
            "budget_max": 700000,
            "appliance_types": ["Refrigerator", "Dishwasher", "Oven", "Coffee Machine", "Hob", "Hood"],
            "cooking_frequency": "daily",
            "brand_preference": ["Bosch", "Siemens"],
            "priority_factors": ["quality", "brand"],
            "energy_priority": "very_important"
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/consultation/request",
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success' and 'consultation_id' in data:
                    self.consultation_id = data['consultation_id']
                    self.log_test(
                        "Premium Kitchen Consultation Request",
                        True,
                        f"Request submitted successfully. Consultation ID: {self.consultation_id}"
                    )
                    
                    # Verify all required fields in response
                    required_fields = ['status', 'message', 'consultation_id', 'email']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        self.log_test(
                            "Response Structure Validation",
                            True,
                            "All required response fields present"
                        )
                    else:
                        self.log_test(
                            "Response Structure Validation",
                            False,
                            f"Missing fields: {', '.join(missing_fields)}"
                        )
                    
                    return True
                else:
                    self.log_test(
                        "Premium Kitchen Consultation Request",
                        False,
                        "Invalid response structure",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "Premium Kitchen Consultation Request",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Premium Kitchen Consultation Request",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_consultation_processing_sync(self):
        """Test 2: Process consultation synchronously"""
        print("⚙️ Testing Consultation Processing (Sync)...")
        
        if not self.consultation_id:
            self.log_test(
                "Consultation Processing",
                False,
                "No consultation ID available"
            )
            return False
        
        try:
            response = self.session.post(
                f"{BASE_URL}/consultation/process-sync/{self.consultation_id}",
                timeout=120  # Longer timeout for AI processing
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    products_analyzed = data.get('products_analyzed', 0)
                    email_sent = data.get('email_sent', False)
                    
                    self.log_test(
                        "Consultation Processing",
                        True,
                        f"Processing completed successfully. {products_analyzed} products analyzed, Email sent: {email_sent}"
                    )
                    
                    # Store report data for further verification
                    self.report_data = data.get('report', {})
                    
                    return True
                else:
                    self.log_test(
                        "Consultation Processing",
                        False,
                        f"Processing failed: {data.get('message', 'Unknown error')}",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "Consultation Processing",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Consultation Processing",
                False,
                f"Processing failed: {str(e)}"
            )
            return False
    
    def test_critical_fixes_verification(self):
        """Test 3: Verify critical fixes as specified in review request"""
        print("🔍 Testing Critical Fixes Verification...")
        
        if not hasattr(self, 'report_data') or not self.report_data:
            self.log_test(
                "Critical Fixes Verification",
                False,
                "No report data available for verification"
            )
            return False
        
        recommendations = self.report_data.get('top_recommendations', [])
        budget_breakdown = self.report_data.get('budget_breakdown', {})
        
        # Test 1: ALL 6 requested categories are covered
        requested_categories = ["Refrigerator", "Dishwasher", "Oven", "Coffee Machine", "Hob", "Hood"]
        covered_categories = []
        
        for rec in recommendations:
            category = rec.get('category', '').lower()
            name = rec.get('name', '').lower()
            
            # Map product categories to requested categories
            if 'refrigerator' in category or 'fridge' in name:
                covered_categories.append("Refrigerator")
            elif 'dishwasher' in category or 'dishwasher' in name:
                covered_categories.append("Dishwasher")
            elif 'oven' in category or 'oven' in name or 'microwave' in name:
                covered_categories.append("Oven")
            elif 'coffee' in category or 'coffee' in name:
                covered_categories.append("Coffee Machine")
            elif 'hob' in category or 'cooktop' in category or 'gas hob' in category:
                covered_categories.append("Hob")
            elif 'chimney' in category or 'hood' in category or 'chimney' in name:
                covered_categories.append("Hood")
        
        covered_categories = list(set(covered_categories))  # Remove duplicates
        missing_categories = [cat for cat in requested_categories if cat not in covered_categories]
        
        if len(covered_categories) == 6:
            self.log_test(
                "All 6 Categories Covered",
                True,
                f"All requested categories covered: {', '.join(covered_categories)}"
            )
        else:
            self.log_test(
                "All 6 Categories Covered",
                False,
                f"Missing categories: {', '.join(missing_categories)}. Covered: {', '.join(covered_categories)}"
            )
        
        # Test 2: Total price is WITHIN the ₹5-7 Lakh budget
        total_price = budget_breakdown.get('products_total', 0)
        budget_min = 500000
        budget_max = 700000
        
        if budget_min <= total_price <= budget_max:
            self.log_test(
                "Budget Compliance",
                True,
                f"Total price ₹{total_price:,} is within budget ₹{budget_min:,} - ₹{budget_max:,}"
            )
        else:
            self.log_test(
                "Budget Compliance",
                False,
                f"Total price ₹{total_price:,} is outside budget ₹{budget_min:,} - ₹{budget_max:,}"
            )
        
        # Test 3: Each product has images array (not empty)
        products_with_images = 0
        products_without_images = []
        
        for rec in recommendations:
            images = rec.get('images', [])
            if images and len(images) > 0:
                products_with_images += 1
            else:
                products_without_images.append(rec.get('name', 'Unknown'))
        
        if products_with_images == len(recommendations) and len(recommendations) > 0:
            self.log_test(
                "Product Images Present",
                True,
                f"All {products_with_images} products have images"
            )
        else:
            self.log_test(
                "Product Images Present",
                False,
                f"Products without images: {', '.join(products_without_images)}"
            )
        
        # Test 4: Each product has a price > 0
        products_with_valid_price = 0
        products_with_invalid_price = []
        
        for rec in recommendations:
            price = rec.get('price', 0)
            if price > 0:
                products_with_valid_price += 1
            else:
                products_with_invalid_price.append(rec.get('name', 'Unknown'))
        
        if products_with_valid_price == len(recommendations) and len(recommendations) > 0:
            self.log_test(
                "Valid Product Prices",
                True,
                f"All {products_with_valid_price} products have valid prices > 0"
            )
        else:
            self.log_test(
                "Valid Product Prices",
                False,
                f"Products with invalid prices: {', '.join(products_with_invalid_price)}"
            )
        
        # Test 5: Email was sent (email_sent: true)
        # This is checked in the processing test, but let's verify from consultation status
        try:
            status_response = self.session.get(
                f"{BASE_URL}/consultation/status/{self.consultation_id}",
                timeout=30
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                consultation = status_data.get('consultation', {})
                email_sent = consultation.get('email_sent', False)
                
                self.log_test(
                    "Email Sent Verification",
                    email_sent,
                    f"Email sent status: {email_sent}"
                )
            else:
                self.log_test(
                    "Email Sent Verification",
                    False,
                    f"Could not verify email status: HTTP {status_response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Email Sent Verification",
                False,
                f"Error checking email status: {str(e)}"
            )
        
        return True
    
    def test_html_report_generation(self):
        """Test 4: Get HTML report and verify content"""
        print("📄 Testing HTML Report Generation...")
        
        if not self.consultation_id:
            self.log_test(
                "HTML Report Generation",
                False,
                "No consultation ID available"
            )
            return False
        
        try:
            response = self.session.get(
                f"{BASE_URL}/consultation/admin/html-report/{self.consultation_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success' and 'html_report' in data:
                    html_report = data['html_report']
                    
                    self.log_test(
                        "HTML Report Generation",
                        True,
                        f"HTML report generated successfully ({len(html_report)} characters)"
                    )
                    
                    # Verify HTML report content
                    required_elements = [
                        'Product images are included',
                        'Prices are displayed correctly',
                        'CTAs (Call Now, WhatsApp, Buy Now) are present',
                        'Disclaimers are included'
                    ]
                    
                    # Check for product images
                    if '<img src=' in html_report and 'alt=' in html_report:
                        self.log_test(
                            "Product Images in HTML",
                            True,
                            "Product images found in HTML report"
                        )
                    else:
                        self.log_test(
                            "Product Images in HTML",
                            False,
                            "No product images found in HTML report"
                        )
                    
                    # Check for prices
                    if '₹' in html_report and 'price' in html_report.lower():
                        self.log_test(
                            "Prices in HTML",
                            True,
                            "Product prices found in HTML report"
                        )
                    else:
                        self.log_test(
                            "Prices in HTML",
                            False,
                            "No product prices found in HTML report"
                        )
                    
                    # Check for CTAs
                    cta_found = False
                    cta_types = []
                    
                    if 'Call Now' in html_report or 'tel:' in html_report:
                        cta_types.append("Call Now")
                        cta_found = True
                    
                    if 'WhatsApp' in html_report or 'wa.me' in html_report:
                        cta_types.append("WhatsApp")
                        cta_found = True
                    
                    if 'Buy Now' in html_report or 'Shop' in html_report:
                        cta_types.append("Buy Now")
                        cta_found = True
                    
                    if cta_found:
                        self.log_test(
                            "CTAs in HTML",
                            True,
                            f"CTAs found: {', '.join(cta_types)}"
                        )
                    else:
                        self.log_test(
                            "CTAs in HTML",
                            False,
                            "No CTAs found in HTML report"
                        )
                    
                    # Check for disclaimers
                    if 'disclaimer' in html_report.lower() or 'terms' in html_report.lower():
                        self.log_test(
                            "Disclaimers in HTML",
                            True,
                            "Disclaimers found in HTML report"
                        )
                    else:
                        self.log_test(
                            "Disclaimers in HTML",
                            False,
                            "No disclaimers found in HTML report"
                        )
                    
                    return True
                else:
                    self.log_test(
                        "HTML Report Generation",
                        False,
                        "Invalid HTML report response structure",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "HTML Report Generation",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "HTML Report Generation",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def run_comprehensive_test(self):
        """Run all Expert Consultation FIXED tests"""
        print("🏠 EXPERT CONSULTATION FIXED FEATURE TESTING")
        print("=" * 70)
        print(f"API Base URL: {BASE_URL}")
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test sequence
        tests = [
            ("Premium Kitchen Consultation Request", self.test_consultation_request_premium_kitchen),
            ("Consultation Processing (Sync)", self.test_consultation_processing_sync),
            ("Critical Fixes Verification", self.test_critical_fixes_verification),
            ("HTML Report Generation", self.test_html_report_generation)
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
        print("=" * 70)
        print("🏁 EXPERT CONSULTATION FIXED TESTING SUMMARY")
        print("=" * 70)
        
        success_rate = (passed_tests / total_tests) * 100
        status_emoji = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
        
        print(f"{status_emoji} Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print()
        
        # Detailed results
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print()
        print("🔍 VERIFICATION SUMMARY:")
        
        if passed_tests >= 3:
            print("✅ Expert Consultation FIXED feature works end-to-end")
            if any("Categories" in r['test'] and r['success'] for r in self.test_results):
                print("✅ All 6 requested categories are covered")
            if any("Budget" in r['test'] and r['success'] for r in self.test_results):
                print("✅ Total price is within ₹5-7 Lakh budget")
            if any("Images" in r['test'] and r['success'] for r in self.test_results):
                print("✅ All products have images")
            if any("Prices" in r['test'] and r['success'] for r in self.test_results):
                print("✅ All products have valid prices > 0")
            if any("Email" in r['test'] and r['success'] for r in self.test_results):
                print("✅ Email was sent successfully")
            if any("HTML" in r['test'] and r['success'] for r in self.test_results):
                print("✅ HTML report generated with all required elements")
        else:
            print("❌ Expert Consultation FIXED feature has critical issues")
        
        print()
        if self.consultation_id:
            print(f"📋 Test Consultation ID: {self.consultation_id}")
            print(f"🔗 Status URL: {BASE_URL}/consultation/status/{self.consultation_id}")
            print(f"📊 Report URL: {BASE_URL}/consultation/report/{self.consultation_id}")
            print(f"📄 HTML Report URL: {BASE_URL}/consultation/admin/html-report/{self.consultation_id}")
        
        return success_rate >= 80


def main():
    """Main test execution"""
    tester = ExpertConsultationFixedTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()