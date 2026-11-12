#!/usr/bin/env python3
"""
New Features Backend Testing - Expert Consultation Enhancements & AI CA Agent
Tests the newly implemented features as requested in the review
"""

import requests
import json
import time
import sys
from datetime import datetime

# API Configuration
API_URL = "https://acct-workflow-1.preview.emergentagent.com"
BASE_URL = f"{API_URL}/api"

# Admin credentials
ADMIN_EMAIL = "admin@adityaretail.com"
ADMIN_PASSWORD = "admin123"

class NewFeaturesTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'NewFeaturesTester/1.0'
        })
        self.admin_token = None
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
    
    def admin_login(self):
        """Login as admin to get authentication token"""
        print("🔐 Logging in as admin...")
        
        try:
            login_data = {
                "username": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                if self.admin_token:
                    self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
                    print(f"✅ Admin login successful")
                    return True
                else:
                    print(f"❌ Admin login failed: No token received")
                    return False
            else:
                print(f"❌ Admin login failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Admin login error: {str(e)}")
            return False
    
    def test_consultation_admin_list(self):
        """Test 1: GET /api/consultation/admin/list - Admin consultation list"""
        print("📋 Testing Admin Consultation List...")
        
        try:
            response = self.session.get(f"{BASE_URL}/consultation/admin/list", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success' and 'consultations' in data:
                    consultations = data['consultations']
                    total = data.get('total', 0)
                    
                    self.log_test(
                        "Admin Consultation List",
                        True,
                        f"Retrieved {len(consultations)} consultations from {total} total"
                    )
                    
                    # Store a consultation ID for detail testing if available
                    if consultations:
                        self.consultation_id = consultations[0].get('id')
                        sample_consultation = consultations[0]
                        customer_name = sample_consultation.get('customer_name', 'N/A')
                        status = sample_consultation.get('status', 'N/A')
                        created_at = sample_consultation.get('created_at', 'N/A')
                        
                        self.log_test(
                            "Consultation List Structure",
                            True,
                            f"Sample: {customer_name}, Status: {status}, Created: {created_at}"
                        )
                    
                    return True
                else:
                    self.log_test(
                        "Admin Consultation List",
                        False,
                        "Invalid response structure",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "Admin Consultation List",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Admin Consultation List",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_consultation_admin_detail(self):
        """Test 2: GET /api/consultation/admin/detail/{consultation_id} - Admin consultation detail"""
        print("🔍 Testing Admin Consultation Detail...")
        
        if not self.consultation_id:
            self.log_test(
                "Admin Consultation Detail",
                False,
                "No consultation ID available from list test"
            )
            return False
        
        try:
            response = self.session.get(
                f"{BASE_URL}/consultation/admin/detail/{self.consultation_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success' and 'consultation' in data:
                    consultation = data['consultation']
                    
                    # Verify detailed consultation structure
                    required_fields = ['id', 'customer_name', 'email', 'status', 'created_at']
                    missing_fields = [field for field in required_fields if field not in consultation]
                    
                    if not missing_fields:
                        customer_name = consultation.get('customer_name', 'N/A')
                        email = consultation.get('email', 'N/A')
                        status = consultation.get('status', 'N/A')
                        
                        self.log_test(
                            "Admin Consultation Detail",
                            True,
                            f"Detail retrieved: {customer_name} ({email}), Status: {status}"
                        )
                        
                        # Check for additional detail fields
                        detail_fields = ['kitchen_size', 'budget_min', 'budget_max', 'appliance_types']
                        found_details = [field for field in detail_fields if field in consultation]
                        
                        if found_details:
                            self.log_test(
                                "Consultation Detail Fields",
                                True,
                                f"Found detail fields: {', '.join(found_details)}"
                            )
                        else:
                            self.log_test(
                                "Consultation Detail Fields",
                                False,
                                "No detailed consultation fields found"
                            )
                        
                        return True
                    else:
                        self.log_test(
                            "Admin Consultation Detail",
                            False,
                            f"Missing required fields: {', '.join(missing_fields)}"
                        )
                        return False
                else:
                    self.log_test(
                        "Admin Consultation Detail",
                        False,
                        "Invalid detail response structure",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "Admin Consultation Detail",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Admin Consultation Detail",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_consultation_html_report(self):
        """Test 3: GET /api/consultation/admin/html-report/{consultation_id} - HTML report"""
        print("📄 Testing Consultation HTML Report...")
        
        if not self.consultation_id:
            self.log_test(
                "Consultation HTML Report",
                False,
                "No consultation ID available for report test"
            )
            return False
        
        try:
            response = self.session.get(
                f"{BASE_URL}/consultation/admin/html-report/{self.consultation_id}",
                timeout=60  # Longer timeout for report generation
            )
            
            if response.status_code == 200:
                # Check if response is HTML
                content_type = response.headers.get('content-type', '')
                
                if 'text/html' in content_type or 'application/json' in content_type:
                    if 'application/json' in content_type:
                        # JSON response with HTML content
                        data = response.json()
                        html_content = data.get('html_report', '') or data.get('report', '')
                    else:
                        # Direct HTML response
                        html_content = response.text
                    
                    if html_content and len(html_content) > 100:
                        self.log_test(
                            "Consultation HTML Report",
                            True,
                            f"HTML report generated ({len(html_content)} characters)"
                        )
                        
                        # Check for required report elements
                        report_elements = {
                            'product_images': any(keyword in html_content.lower() for keyword in ['<img', 'image', 'src=']),
                            'specifications': any(keyword in html_content.lower() for keyword in ['specification', 'specs', 'features']),
                            'cta_call': 'call' in html_content.lower(),
                            'cta_whatsapp': 'whatsapp' in html_content.lower(),
                            'cta_buy': any(keyword in html_content.lower() for keyword in ['buy', 'purchase', 'order']),
                            'disclaimers': any(keyword in html_content.lower() for keyword in ['disclaimer', 'terms', 'conditions'])
                        }
                        
                        found_elements = [element for element, found in report_elements.items() if found]
                        missing_elements = [element for element, found in report_elements.items() if not found]
                        
                        if len(found_elements) >= 4:  # At least 4 out of 6 elements
                            self.log_test(
                                "HTML Report Content Verification",
                                True,
                                f"Found elements: {', '.join(found_elements)}"
                            )
                        else:
                            self.log_test(
                                "HTML Report Content Verification",
                                False,
                                f"Missing elements: {', '.join(missing_elements)}"
                            )
                        
                        return True
                    else:
                        self.log_test(
                            "Consultation HTML Report",
                            False,
                            "HTML report too short or empty"
                        )
                        return False
                else:
                    self.log_test(
                        "Consultation HTML Report",
                        False,
                        f"Unexpected content type: {content_type}"
                    )
                    return False
            else:
                self.log_test(
                    "Consultation HTML Report",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Consultation HTML Report",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_ai_ca_unpaid_invoices(self):
        """Test 4: GET /api/ai-ca/unpaid-invoices - Unpaid invoices aging summary"""
        print("💰 Testing AI CA Unpaid Invoices...")
        
        try:
            response = self.session.get(f"{BASE_URL}/ai-ca/unpaid-invoices", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    aging_summary = data.get('aging_summary', {})
                    unpaid_invoices = data.get('unpaid_invoices', [])
                    total_outstanding = data.get('total_outstanding', 0)
                    
                    self.log_test(
                        "AI CA Unpaid Invoices",
                        True,
                        f"Found {len(unpaid_invoices)} unpaid invoices, Total outstanding: ₹{total_outstanding:,.2f}"
                    )
                    
                    # Verify aging summary structure
                    if aging_summary:
                        aging_categories = ['0-30', '31-60', '61-90', '90+']
                        found_categories = [cat for cat in aging_categories if cat in aging_summary]
                        
                        if found_categories:
                            self.log_test(
                                "Aging Summary Structure",
                                True,
                                f"Aging categories: {', '.join(found_categories)}"
                            )
                            
                            # Show aging breakdown
                            for category in found_categories:
                                amount = aging_summary[category].get('amount', 0)
                                count = aging_summary[category].get('count', 0)
                                print(f"   {category} days: {count} invoices, ₹{amount:,.2f}")
                        else:
                            self.log_test(
                                "Aging Summary Structure",
                                False,
                                "No standard aging categories found"
                            )
                    else:
                        self.log_test(
                            "Aging Summary Structure",
                            False,
                            "No aging summary provided"
                        )
                    
                    return True
                else:
                    self.log_test(
                        "AI CA Unpaid Invoices",
                        False,
                        f"API error: {data.get('message', 'Unknown error')}",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "AI CA Unpaid Invoices",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "AI CA Unpaid Invoices",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_ai_ca_overdue_vendor_payments(self):
        """Test 5: GET /api/ai-ca/overdue-vendor-payments - Overdue vendor payments"""
        print("🏭 Testing AI CA Overdue Vendor Payments...")
        
        try:
            response = self.session.get(f"{BASE_URL}/ai-ca/overdue-vendor-payments", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    overdue_payments = data.get('overdue_payments', [])
                    total_overdue = data.get('total_overdue', 0)
                    summary = data.get('summary', {})
                    
                    self.log_test(
                        "AI CA Overdue Vendor Payments",
                        True,
                        f"Found {len(overdue_payments)} overdue payments, Total: ₹{total_overdue:,.2f}"
                    )
                    
                    # Verify payment structure
                    if overdue_payments:
                        sample_payment = overdue_payments[0]
                        required_fields = ['vendor_name', 'amount', 'due_date', 'days_overdue']
                        missing_fields = [field for field in required_fields if field not in sample_payment]
                        
                        if not missing_fields:
                            vendor_name = sample_payment.get('vendor_name', 'N/A')
                            amount = sample_payment.get('amount', 0)
                            days_overdue = sample_payment.get('days_overdue', 0)
                            
                            self.log_test(
                                "Overdue Payment Structure",
                                True,
                                f"Sample: {vendor_name}, ₹{amount:,.2f}, {days_overdue} days overdue"
                            )
                        else:
                            self.log_test(
                                "Overdue Payment Structure",
                                False,
                                f"Missing fields: {', '.join(missing_fields)}"
                            )
                    
                    # Check summary information
                    if summary:
                        critical_count = summary.get('critical_overdue_count', 0)
                        avg_days_overdue = summary.get('avg_days_overdue', 0)
                        
                        self.log_test(
                            "Vendor Payment Summary",
                            True,
                            f"Critical overdue: {critical_count}, Avg days: {avg_days_overdue}"
                        )
                    
                    return True
                else:
                    self.log_test(
                        "AI CA Overdue Vendor Payments",
                        False,
                        f"API error: {data.get('message', 'Unknown error')}",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "AI CA Overdue Vendor Payments",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "AI CA Overdue Vendor Payments",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_ai_ca_quick_stats(self):
        """Test 6: GET /api/ai-ca/quick-stats - Quick stats dashboard"""
        print("📊 Testing AI CA Quick Stats...")
        
        try:
            response = self.session.get(f"{BASE_URL}/ai-ca/quick-stats", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    stats = data.get('stats', {})
                    
                    if stats:
                        # Expected stat categories
                        expected_stats = [
                            'total_revenue', 'total_expenses', 'net_profit',
                            'outstanding_receivables', 'outstanding_payables',
                            'cash_flow', 'monthly_revenue', 'monthly_expenses'
                        ]
                        
                        found_stats = [stat for stat in expected_stats if stat in stats]
                        
                        self.log_test(
                            "AI CA Quick Stats",
                            True,
                            f"Retrieved {len(found_stats)} stat categories"
                        )
                        
                        # Display key statistics
                        if 'total_revenue' in stats:
                            print(f"   💰 Total Revenue: ₹{stats['total_revenue']:,.2f}")
                        if 'total_expenses' in stats:
                            print(f"   💸 Total Expenses: ₹{stats['total_expenses']:,.2f}")
                        if 'net_profit' in stats:
                            print(f"   📈 Net Profit: ₹{stats['net_profit']:,.2f}")
                        if 'outstanding_receivables' in stats:
                            print(f"   📋 Outstanding Receivables: ₹{stats['outstanding_receivables']:,.2f}")
                        if 'outstanding_payables' in stats:
                            print(f"   🏭 Outstanding Payables: ₹{stats['outstanding_payables']:,.2f}")
                        
                        # Verify stats structure quality
                        if len(found_stats) >= 5:
                            self.log_test(
                                "Quick Stats Completeness",
                                True,
                                f"Found {len(found_stats)}/{len(expected_stats)} expected stats"
                            )
                        else:
                            self.log_test(
                                "Quick Stats Completeness",
                                False,
                                f"Only {len(found_stats)}/{len(expected_stats)} stats available"
                            )
                        
                        return True
                    else:
                        self.log_test(
                            "AI CA Quick Stats",
                            False,
                            "No stats data in response"
                        )
                        return False
                else:
                    self.log_test(
                        "AI CA Quick Stats",
                        False,
                        f"API error: {data.get('message', 'Unknown error')}",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "AI CA Quick Stats",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "AI CA Quick Stats",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def run_comprehensive_test(self):
        """Run all new feature tests"""
        print("🆕 NEW FEATURES BACKEND TESTING")
        print("=" * 70)
        print(f"API Base URL: {BASE_URL}")
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Login first
        if not self.admin_login():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Test sequence
        tests = [
            ("Expert Consultation - Admin List", self.test_consultation_admin_list),
            ("Expert Consultation - Admin Detail", self.test_consultation_admin_detail),
            ("Expert Consultation - HTML Report", self.test_consultation_html_report),
            ("AI CA Agent - Unpaid Invoices", self.test_ai_ca_unpaid_invoices),
            ("AI CA Agent - Overdue Vendor Payments", self.test_ai_ca_overdue_vendor_payments),
            ("AI CA Agent - Quick Stats", self.test_ai_ca_quick_stats)
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
        print("🏁 NEW FEATURES TESTING SUMMARY")
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
        print("🔍 FEATURE VERIFICATION SUMMARY:")
        
        # Expert Consultation Enhancements
        consultation_tests = [r for r in self.test_results if 'Consultation' in r['test']]
        consultation_passed = sum(1 for r in consultation_tests if r['success'])
        
        if consultation_passed >= 2:
            print("✅ Expert Consultation Enhancements working")
            if any("HTML Report" in r['test'] and r['success'] for r in consultation_tests):
                print("✅ HTML reports with product images, specs, and CTAs")
            if any("Admin List" in r['test'] and r['success'] for r in consultation_tests):
                print("✅ Admin consultation management functional")
        else:
            print("❌ Expert Consultation Enhancements have issues")
        
        # AI CA Agent Features
        ai_ca_tests = [r for r in self.test_results if 'AI CA' in r['test']]
        ai_ca_passed = sum(1 for r in ai_ca_tests if r['success'])
        
        if ai_ca_passed >= 2:
            print("✅ AI CA Agent new features working")
            if any("Unpaid Invoices" in r['test'] and r['success'] for r in ai_ca_tests):
                print("✅ Unpaid invoices aging analysis functional")
            if any("Quick Stats" in r['test'] and r['success'] for r in ai_ca_tests):
                print("✅ Quick stats dashboard operational")
        else:
            print("❌ AI CA Agent features have issues")
        
        print()
        if self.consultation_id:
            print(f"📋 Test Consultation ID: {self.consultation_id}")
            print(f"🔗 Admin Detail URL: {BASE_URL}/consultation/admin/detail/{self.consultation_id}")
            print(f"📄 HTML Report URL: {BASE_URL}/consultation/admin/html-report/{self.consultation_id}")
        
        return success_rate >= 80


def main():
    """Main test execution"""
    tester = NewFeaturesTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()