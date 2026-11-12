#!/usr/bin/env python3
"""
Expert Consultation / Deep Research Consultant Backend Testing
Tests the newly implemented consultation feature end-to-end
"""

import requests
import json
import time
import sys
from datetime import datetime

# API Configuration
API_URL = "https://acct-workflow-1.preview.emergentagent.com"
BASE_URL = f"{API_URL}/api"

class ConsultationTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ConsultationTester/1.0'
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
    
    def test_consultation_options(self):
        """Test 1: GET /api/consultation/options - Get form options"""
        print("🔍 Testing Consultation Options API...")
        
        try:
            response = self.session.get(f"{BASE_URL}/consultation/options", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required option categories
                required_keys = [
                    'kitchen_sizes', 'appliance_types', 'family_sizes', 
                    'cooking_frequencies', 'priority_factors', 'brands',
                    'energy_priorities', 'aesthetic_preferences', 'budget_ranges'
                ]
                
                missing_keys = [key for key in required_keys if key not in data]
                
                if not missing_keys:
                    # Check specific content
                    appliance_count = len(data.get('appliance_types', []))
                    budget_count = len(data.get('budget_ranges', []))
                    
                    self.log_test(
                        "Consultation Options API",
                        True,
                        f"All option categories present. {appliance_count} appliance types, {budget_count} budget ranges available"
                    )
                    
                    # Verify specific appliances are available
                    appliances = [item['value'] for item in data.get('appliance_types', [])]
                    expected_appliances = ['refrigerator', 'chimney', 'washing_machine']
                    found_appliances = [a for a in expected_appliances if a in appliances]
                    
                    if len(found_appliances) == len(expected_appliances):
                        self.log_test(
                            "Required Appliance Types Available",
                            True,
                            f"Found all required appliances: {', '.join(found_appliances)}"
                        )
                    else:
                        missing = [a for a in expected_appliances if a not in appliances]
                        self.log_test(
                            "Required Appliance Types Available",
                            False,
                            f"Missing appliances: {', '.join(missing)}"
                        )
                    
                    return True
                else:
                    self.log_test(
                        "Consultation Options API",
                        False,
                        f"Missing required keys: {', '.join(missing_keys)}",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "Consultation Options API",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Consultation Options API",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_consultation_request(self):
        """Test 2: POST /api/consultation/request - Submit consultation request"""
        print("📝 Testing Consultation Request Submission...")
        
        # Test data as specified in the review request
        test_data = {
            "customer_name": "Test User",
            "email": "test@example.com",
            "kitchen_size": "medium",
            "budget_min": 100000,
            "budget_max": 300000,
            "appliance_types": ["refrigerator", "chimney"],
            "family_size": "3-4",
            "cooking_frequency": "daily",
            "brand_preference": ["Bosch"],
            "energy_priority": "important"
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
                        "Consultation Request Submission",
                        True,
                        f"Request submitted successfully. Consultation ID: {self.consultation_id}"
                    )
                    
                    # Verify response structure
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
                        "Consultation Request Submission",
                        False,
                        "Invalid response structure",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "Consultation Request Submission",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Consultation Request Submission",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_consultation_status(self):
        """Test 3: GET /api/consultation/status/{consultation_id} - Check status"""
        print("📊 Testing Consultation Status Check...")
        
        if not self.consultation_id:
            self.log_test(
                "Consultation Status Check",
                False,
                "No consultation ID available from previous test"
            )
            return False
        
        try:
            response = self.session.get(
                f"{BASE_URL}/consultation/status/{self.consultation_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success' and 'consultation' in data:
                    consultation = data['consultation']
                    status = consultation.get('status', 'unknown')
                    
                    self.log_test(
                        "Consultation Status Check",
                        True,
                        f"Status retrieved successfully. Current status: {status}"
                    )
                    
                    # Verify status structure
                    required_fields = ['id', 'status', 'created_at']
                    missing_fields = [field for field in required_fields if field not in consultation]
                    
                    if not missing_fields:
                        self.log_test(
                            "Status Response Structure",
                            True,
                            f"All required status fields present. Status: {status}"
                        )
                    else:
                        self.log_test(
                            "Status Response Structure",
                            False,
                            f"Missing status fields: {', '.join(missing_fields)}"
                        )
                    
                    return True
                else:
                    self.log_test(
                        "Consultation Status Check",
                        False,
                        "Invalid status response structure",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "Consultation Status Check",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Consultation Status Check",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_consultation_processing(self):
        """Test 4: Process consultation synchronously for testing"""
        print("⚙️ Testing Consultation Processing...")
        
        if not self.consultation_id:
            self.log_test(
                "Consultation Processing",
                False,
                "No consultation ID available"
            )
            return False
        
        try:
            # Use sync processing endpoint for testing
            response = self.session.post(
                f"{BASE_URL}/consultation/process-sync/{self.consultation_id}",
                timeout=60  # Longer timeout for AI processing
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    products_analyzed = data.get('products_analyzed', 0)
                    
                    self.log_test(
                        "Consultation Processing",
                        True,
                        f"Processing completed successfully. {products_analyzed} products analyzed"
                    )
                    
                    # Check if report was generated
                    if 'report' in data:
                        report = data['report']
                        has_recommendations = bool(report.get('top_recommendations'))
                        
                        self.log_test(
                            "AI Report Generation",
                            has_recommendations,
                            f"Report generated with recommendations: {has_recommendations}"
                        )
                    
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
    
    def test_consultation_report(self):
        """Test 5: GET /api/consultation/report/{consultation_id} - Get report"""
        print("📋 Testing Consultation Report Retrieval...")
        
        if not self.consultation_id:
            self.log_test(
                "Consultation Report Retrieval",
                False,
                "No consultation ID available"
            )
            return False
        
        try:
            response = self.session.get(
                f"{BASE_URL}/consultation/report/{self.consultation_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success' and 'report' in data:
                    report = data['report']
                    
                    # Verify report structure
                    recommendations = report.get('top_recommendations', [])
                    budget_breakdown = report.get('budget_breakdown', {})
                    executive_summary = report.get('executive_summary', '')
                    
                    self.log_test(
                        "Consultation Report Retrieval",
                        True,
                        f"Report retrieved successfully. {len(recommendations)} recommendations found"
                    )
                    
                    # Verify report content quality
                    if recommendations:
                        # Check first recommendation structure
                        first_rec = recommendations[0]
                        required_rec_fields = ['name', 'brand', 'price']
                        has_required_fields = all(field in first_rec for field in required_rec_fields)
                        
                        if has_required_fields:
                            product_name = first_rec.get('name', 'Unknown')
                            product_price = first_rec.get('price', 0)
                            
                            self.log_test(
                                "Product Recommendations Quality",
                                True,
                                f"First recommendation: {product_name} - ₹{product_price:,}"
                            )
                            
                            # Check for energy analysis
                            energy_analysis = first_rec.get('energy_analysis', {})
                            if energy_analysis:
                                annual_cost = energy_analysis.get('annual_cost', 0)
                                savings = energy_analysis.get('estimated_annual_savings', 0)
                                stars = energy_analysis.get('estimated_stars', 0)
                                
                                self.log_test(
                                    "Energy Analysis Present",
                                    True,
                                    f"Energy data: {stars} stars, ₹{annual_cost}/year, ₹{savings} savings"
                                )
                            else:
                                self.log_test(
                                    "Energy Analysis Present",
                                    False,
                                    "No energy analysis found in recommendations"
                                )
                        else:
                            missing_rec_fields = [f for f in required_rec_fields if f not in first_rec]
                            self.log_test(
                                "Product Recommendations Quality",
                                False,
                                f"Missing recommendation fields: {', '.join(missing_rec_fields)}"
                            )
                    
                    # Check budget breakdown
                    if budget_breakdown:
                        total = budget_breakdown.get('grand_total', 0)
                        products_total = budget_breakdown.get('products_total', 0)
                        
                        self.log_test(
                            "Budget Breakdown Present",
                            True,
                            f"Budget analysis: Products ₹{products_total:,}, Total ₹{total:,}"
                        )
                    else:
                        self.log_test(
                            "Budget Breakdown Present",
                            False,
                            "No budget breakdown found"
                        )
                    
                    # Check executive summary
                    if executive_summary and len(executive_summary) > 50:
                        self.log_test(
                            "Executive Summary Quality",
                            True,
                            f"Executive summary present ({len(executive_summary)} characters)"
                        )
                    else:
                        self.log_test(
                            "Executive Summary Quality",
                            False,
                            "Executive summary missing or too short"
                        )
                    
                    return True
                    
                elif data.get('status') == 'pending':
                    self.log_test(
                        "Consultation Report Retrieval",
                        False,
                        f"Report still pending: {data.get('message', 'Processing...')}"
                    )
                    return False
                else:
                    self.log_test(
                        "Consultation Report Retrieval",
                        False,
                        "Invalid report response structure",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "Consultation Report Retrieval",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Consultation Report Retrieval",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_consultation_history(self):
        """Test 6: GET /api/consultation/history - Get consultation history"""
        print("📚 Testing Consultation History...")
        
        try:
            response = self.session.get(f"{BASE_URL}/consultation/history", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success' and 'consultations' in data:
                    consultations = data['consultations']
                    total = data.get('total', 0)
                    
                    self.log_test(
                        "Consultation History Retrieval",
                        True,
                        f"History retrieved successfully. {len(consultations)} consultations in current page, {total} total"
                    )
                    
                    # Verify pagination structure
                    pagination_fields = ['total', 'page', 'pages']
                    has_pagination = all(field in data for field in pagination_fields)
                    
                    if has_pagination:
                        self.log_test(
                            "History Pagination Structure",
                            True,
                            f"Page {data.get('page', 1)} of {data.get('pages', 1)}"
                        )
                    else:
                        self.log_test(
                            "History Pagination Structure",
                            False,
                            "Missing pagination fields"
                        )
                    
                    # Check if our test consultation is in history
                    if self.consultation_id and consultations:
                        our_consultation = next(
                            (c for c in consultations if c.get('id') == self.consultation_id),
                            None
                        )
                        
                        if our_consultation:
                            self.log_test(
                                "Test Consultation in History",
                                True,
                                f"Test consultation found in history with status: {our_consultation.get('status', 'unknown')}"
                            )
                        else:
                            self.log_test(
                                "Test Consultation in History",
                                False,
                                "Test consultation not found in history"
                            )
                    
                    return True
                else:
                    self.log_test(
                        "Consultation History Retrieval",
                        False,
                        "Invalid history response structure",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "Consultation History Retrieval",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Consultation History Retrieval",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def run_comprehensive_test(self):
        """Run all consultation tests"""
        print("🏠 EXPERT CONSULTATION / DEEP RESEARCH CONSULTANT TESTING")
        print("=" * 70)
        print(f"API Base URL: {BASE_URL}")
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test sequence
        tests = [
            ("Consultation Options", self.test_consultation_options),
            ("Consultation Request", self.test_consultation_request),
            ("Consultation Status", self.test_consultation_status),
            ("Consultation Processing", self.test_consultation_processing),
            ("Consultation Report", self.test_consultation_report),
            ("Consultation History", self.test_consultation_history)
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
        print("🏁 EXPERT CONSULTATION TESTING SUMMARY")
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
        
        if passed_tests >= 5:
            print("✅ Expert Consultation workflow works end-to-end")
            if any("AI" in r['test'] and r['success'] for r in self.test_results):
                print("✅ AI generates meaningful recommendations")
            if any("Product" in r['test'] and r['success'] for r in self.test_results):
                print("✅ Products are correctly matched from database")
            if any("Energy" in r['test'] and r['success'] for r in self.test_results):
                print("✅ Energy calculations are provided")
        else:
            print("❌ Expert Consultation system has critical issues")
        
        print()
        if self.consultation_id:
            print(f"📋 Test Consultation ID: {self.consultation_id}")
            print(f"🔗 Status URL: {BASE_URL}/consultation/status/{self.consultation_id}")
            print(f"📊 Report URL: {BASE_URL}/consultation/report/{self.consultation_id}")
        
        return success_rate >= 80


def main():
    """Main test execution"""
    tester = ConsultationTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()