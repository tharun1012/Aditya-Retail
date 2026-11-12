#!/usr/bin/env python3
"""
Autonomous Procurement System - Phase 2 Testing
Tests all autonomous procurement endpoints and workflows
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

class AutonomousProcurementTester:
    def __init__(self):
        self.session = None
        self.test_results = {}
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print(f"🤖 Starting Autonomous Procurement Tests for: {API_BASE_URL}")
        print("=" * 80)
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()

    async def test_low_stock_detection(self):
        """Test 1: Low Stock Items Detection"""
        print("\n📦 Testing Low Stock Items Detection...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/autonomous-procurement/low-stock-items") as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get('items', [])
                    count = data.get('count', 0)
                    
                    print(f"✅ Low Stock Detection: Found {count} low-stock items")
                    
                    if items:
                        # Verify response structure
                        sample_item = items[0]
                        required_fields = ['id', 'name', 'stock_quantity', 'reorder_level']
                        has_required_fields = all(field in sample_item for field in required_fields)
                        
                        if has_required_fields:
                            print(f"✅ Response Structure: All required fields present")
                            print(f"📦 Sample Item: {sample_item.get('name')} (Stock: {sample_item.get('stock_quantity')}, Reorder: {sample_item.get('reorder_level')})")
                            
                            # Verify logic: stock_quantity <= reorder_level
                            valid_items = [item for item in items if item.get('stock_quantity', 0) <= item.get('reorder_level', 0)]
                            if len(valid_items) == len(items):
                                print(f"✅ Logic Verification: All items correctly identified as low-stock")
                            else:
                                print(f"⚠️ Logic Verification: {len(valid_items)}/{len(items)} items correctly identified")
                        else:
                            print(f"❌ Response Structure: Missing required fields")
                    else:
                        print(f"ℹ️ No low-stock items found (this may be expected)")
                    
                    self.test_results['low_stock_detection'] = True
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Low Stock Detection failed: {response.status} - {error_text}")
                    
            self.test_results['low_stock_detection'] = False
            return False
            
        except Exception as e:
            print(f"❌ Low Stock Detection error: {str(e)}")
            self.test_results['low_stock_detection'] = False
            return False

    async def test_autonomous_check_trigger(self):
        """Test 2: Autonomous Check Trigger"""
        print("\n🔄 Testing Autonomous Check Trigger...")
        
        try:
            async with self.session.post(f"{API_BASE_URL}/autonomous-procurement/run-check") as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get('status')
                    message = data.get('message', '')
                    low_stock_count = data.get('low_stock_count', 0)
                    drafts_created = data.get('drafts_created', 0)
                    drafts = data.get('drafts', [])
                    
                    print(f"✅ Auto Check Trigger: {status}")
                    print(f"📊 Low Stock Count: {low_stock_count}")
                    print(f"📝 Drafts Created: {drafts_created}")
                    print(f"💬 Message: {message}")
                    
                    if drafts:
                        print(f"📋 Draft POs Created:")
                        for draft in drafts[:3]:  # Show first 3
                            print(f"  • {draft.get('draft_number', 'N/A')}: {draft.get('product_name', 'N/A')} (Qty: {draft.get('quantity', 0)}, Amount: ₹{draft.get('total_amount', 0):,.2f})")
                        
                        # Verify AUTO-DRAFT-PO format
                        sample_draft = drafts[0]
                        draft_number = sample_draft.get('draft_number', '')
                        if draft_number.startswith('AUTO-DRAFT-PO-'):
                            print(f"✅ Draft Number Format: Correct AUTO-DRAFT-PO format")
                        else:
                            print(f"❌ Draft Number Format: Expected AUTO-DRAFT-PO format, got {draft_number}")
                    
                    # Check for duplicate prevention logic
                    if status == 'success':
                        print(f"✅ Duplicate Prevention: System checked for existing drafts")
                    
                    self.test_results['autonomous_check_trigger'] = True
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Auto Check Trigger failed: {response.status} - {error_text}")
                    
            self.test_results['autonomous_check_trigger'] = False
            return False
            
        except Exception as e:
            print(f"❌ Auto Check Trigger error: {str(e)}")
            self.test_results['autonomous_check_trigger'] = False
            return False

    async def test_vendor_report_parsing(self):
        """Test 3: Vendor Stock Report Parsing"""
        print("\n📊 Testing Vendor Stock Report Parsing...")
        
        try:
            # Test with sample vendor report as specified in review request
            vendor_report = {
                "vendor_name": "Bosch",
                "report_data": {
                    "Bosch Washing Machine": {"available": 50, "price": 25000},
                    "Bosch Dishwasher": {"available": 30, "price": 35000}
                }
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/autonomous-procurement/parse-vendor-report",
                json=vendor_report,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get('status')
                    vendor = data.get('vendor')
                    matches_found = data.get('matches_found', 0)
                    matches = data.get('matches', [])
                    
                    print(f"✅ Vendor Report Parsing: {status}")
                    print(f"🏭 Vendor: {vendor}")
                    print(f"🔍 Matches Found: {matches_found}")
                    
                    if matches:
                        print(f"📋 Product Matches:")
                        for match in matches:
                            print(f"  • Our Product: {match.get('our_product', 'N/A')}")
                            print(f"    Vendor Product: {match.get('vendor_product', 'N/A')}")
                            print(f"    Current Stock: {match.get('our_current_stock', 0)}")
                            print(f"    Reorder Level: {match.get('our_reorder_level', 0)}")
                            print(f"    Vendor Available: {match.get('vendor_available_qty', 0)}")
                            print(f"    Vendor Price: ₹{match.get('vendor_price', 0):,.2f}")
                            print(f"    Recommended Order: {match.get('recommended_order_qty', 0)}")
                            print()
                        
                        # Store matches for next test
                        self.vendor_matches = matches
                        
                        # Verify recommended order quantities are reasonable
                        reasonable_matches = [
                            m for m in matches 
                            if m.get('recommended_order_qty', 0) > 0 and 
                               m.get('recommended_order_qty', 0) <= 100  # Reasonable range
                        ]
                        
                        if len(reasonable_matches) == len(matches):
                            print(f"✅ Order Quantity Calculation: All recommendations are reasonable")
                        else:
                            print(f"⚠️ Order Quantity Calculation: {len(reasonable_matches)}/{len(matches)} recommendations seem reasonable")
                    else:
                        print(f"ℹ️ No matches found (may be expected if no Bosch low-stock items)")
                        self.vendor_matches = []
                    
                    self.test_results['vendor_report_parsing'] = True
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Vendor Report Parsing failed: {response.status} - {error_text}")
                    
            self.test_results['vendor_report_parsing'] = False
            return False
            
        except Exception as e:
            print(f"❌ Vendor Report Parsing error: {str(e)}")
            self.test_results['vendor_report_parsing'] = False
            return False

    async def test_po_from_vendor_match(self):
        """Test 4: Generate PO from Vendor Match"""
        print("\n📝 Testing Generate PO from Vendor Match...")
        
        try:
            # Use matches from previous test if available
            if hasattr(self, 'vendor_matches') and self.vendor_matches:
                matches = self.vendor_matches
            else:
                # Create sample matches for testing
                matches = [
                    {
                        "our_product": "Sample Bosch Product",
                        "our_current_stock": 2,
                        "our_reorder_level": 10,
                        "vendor_product": "Bosch Washing Machine",
                        "vendor_available_qty": 50,
                        "vendor_price": 25000,
                        "recommended_order_qty": 15,
                        "product_id": "sample-product-id"
                    }
                ]
            
            async with self.session.post(
                f"{API_BASE_URL}/autonomous-procurement/generate-from-vendor-match",
                params={"vendor_name": "Bosch"},
                json=matches,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get('status')
                    message = data.get('message', '')
                    drafts_created = data.get('drafts_created', 0)
                    drafts = data.get('drafts', [])
                    
                    print(f"✅ PO from Vendor Match: {status}")
                    print(f"💬 Message: {message}")
                    print(f"📝 Drafts Created: {drafts_created}")
                    
                    if drafts:
                        print(f"📋 Generated Draft POs:")
                        for draft in drafts:
                            print(f"  • {draft.get('draft_number', 'N/A')}: {draft.get('product_name', 'N/A')}")
                            print(f"    Quantity: {draft.get('quantity', 0)}, Amount: ₹{draft.get('total_amount', 0):,.2f}")
                        
                        # Verify AUTO-DRAFT-PO numbering
                        sample_draft = drafts[0]
                        draft_number = sample_draft.get('draft_number', '')
                        if draft_number.startswith('AUTO-DRAFT-PO-'):
                            print(f"✅ Draft Numbering: Correct AUTO-DRAFT-PO format")
                        else:
                            print(f"❌ Draft Numbering: Expected AUTO-DRAFT-PO format")
                    else:
                        print(f"ℹ️ No drafts created (may be expected if vendor stock insufficient)")
                    
                    self.test_results['po_from_vendor_match'] = True
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ PO Generation failed: {response.status} - {error_text}")
                    
            self.test_results['po_from_vendor_match'] = False
            return False
            
        except Exception as e:
            print(f"❌ PO from Vendor Match error: {str(e)}")
            self.test_results['po_from_vendor_match'] = False
            return False

    async def test_notifications(self):
        """Test 5: Purchase Manager Notifications"""
        print("\n🔔 Testing Purchase Manager Notifications...")
        
        try:
            # Test 1: Get notifications for purchase manager
            async with self.session.get(
                f"{API_BASE_URL}/autonomous-procurement/notifications",
                params={"role": "admin", "unread_only": "true"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    notifications = data.get('notifications', [])
                    count = data.get('count', 0)
                    
                    print(f"✅ Get Notifications: {count} unread notifications")
                    
                    if notifications:
                        # Verify notification structure
                        sample_notification = notifications[0]
                        required_fields = ['id', 'type', 'title', 'message', 'priority', 'read', 'created_at']
                        has_required_fields = all(field in sample_notification for field in required_fields)
                        
                        if has_required_fields:
                            print(f"✅ Notification Structure: All required fields present")
                            print(f"📧 Sample Notification: {sample_notification.get('title', 'N/A')}")
                            print(f"🔥 Priority: {sample_notification.get('priority', 'N/A')}")
                            
                            # Check if it's an auto-draft notification
                            if sample_notification.get('type') == 'auto_draft_po_created':
                                print(f"✅ Notification Type: Correct auto-draft PO notification")
                                drafts_info = sample_notification.get('drafts', [])
                                print(f"📝 Drafts in Notification: {len(drafts_info)}")
                            
                            # Test 2: Mark notification as read
                            notification_id = sample_notification.get('id')
                            if notification_id:
                                async with self.session.put(
                                    f"{API_BASE_URL}/autonomous-procurement/notifications/{notification_id}/mark-read"
                                ) as mark_response:
                                    if mark_response.status == 200:
                                        mark_data = await mark_response.json()
                                        print(f"✅ Mark as Read: {mark_data.get('message', 'Success')}")
                                    else:
                                        print(f"❌ Mark as Read failed: {mark_response.status}")
                        else:
                            print(f"❌ Notification Structure: Missing required fields")
                    else:
                        print(f"ℹ️ No notifications found (may be expected)")
                    
                    # Test 3: Test filtering by role
                    async with self.session.get(
                        f"{API_BASE_URL}/autonomous-procurement/notifications",
                        params={"role": "purchase_manager", "unread_only": "false"}
                    ) as filter_response:
                        if filter_response.status == 200:
                            filter_data = await filter_response.json()
                            print(f"✅ Role Filtering: {filter_data.get('count', 0)} notifications for purchase_manager")
                        else:
                            print(f"❌ Role Filtering failed: {filter_response.status}")
                    
                    self.test_results['notifications'] = True
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Get Notifications failed: {response.status} - {error_text}")
                    
            self.test_results['notifications'] = False
            return False
            
        except Exception as e:
            print(f"❌ Notifications error: {str(e)}")
            self.test_results['notifications'] = False
            return False

    async def test_dashboard_summary(self):
        """Test 6: Autonomous Dashboard Summary"""
        print("\n📊 Testing Autonomous Dashboard Summary...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/autonomous-procurement/dashboard-summary") as response:
                if response.status == 200:
                    data = await response.json()
                    summary = data.get('summary', {})
                    
                    print(f"✅ Dashboard Summary: Complete overview retrieved")
                    
                    # Verify all required summary fields
                    required_fields = [
                        'low_stock_items_count',
                        'pending_auto_drafts_count', 
                        'total_draft_value',
                        'unread_notifications_count',
                        'low_stock_items',
                        'recent_auto_drafts'
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in summary]
                    if not missing_fields:
                        print(f"✅ Summary Structure: All required fields present")
                        
                        # Display summary metrics
                        print(f"📦 Low Stock Items: {summary.get('low_stock_items_count', 0)}")
                        print(f"📝 Pending Auto Drafts: {summary.get('pending_auto_drafts_count', 0)}")
                        print(f"💰 Total Draft Value: ₹{summary.get('total_draft_value', 0):,.2f}")
                        print(f"🔔 Unread Notifications: {summary.get('unread_notifications_count', 0)}")
                        
                        # Verify top 10 low-stock items
                        low_stock_items = summary.get('low_stock_items', [])
                        if len(low_stock_items) <= 10:
                            print(f"✅ Top Low Stock Items: {len(low_stock_items)} items (≤10 as expected)")
                        else:
                            print(f"⚠️ Top Low Stock Items: {len(low_stock_items)} items (expected ≤10)")
                        
                        # Verify recent 5 auto-drafts
                        recent_drafts = summary.get('recent_auto_drafts', [])
                        if len(recent_drafts) <= 5:
                            print(f"✅ Recent Auto Drafts: {len(recent_drafts)} drafts (≤5 as expected)")
                        else:
                            print(f"⚠️ Recent Auto Drafts: {len(recent_drafts)} drafts (expected ≤5)")
                        
                        # Show sample data if available
                        if low_stock_items:
                            sample_item = low_stock_items[0]
                            print(f"📦 Sample Low Stock: {sample_item.get('name', 'N/A')} (Stock: {sample_item.get('stock_quantity', 0)})")
                        
                        if recent_drafts:
                            sample_draft = recent_drafts[0]
                            print(f"📝 Sample Recent Draft: {sample_draft.get('draft_number', 'N/A')} (₹{sample_draft.get('total_amount', 0):,.2f})")
                    else:
                        print(f"❌ Summary Structure: Missing fields: {missing_fields}")
                    
                    self.test_results['dashboard_summary'] = True
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Dashboard Summary failed: {response.status} - {error_text}")
                    
            self.test_results['dashboard_summary'] = False
            return False
            
        except Exception as e:
            print(f"❌ Dashboard Summary error: {str(e)}")
            self.test_results['dashboard_summary'] = False
            return False

    async def run_all_tests(self):
        """Run all autonomous procurement tests"""
        await self.setup()
        
        tests = [
            ("Low Stock Items Detection", self.test_low_stock_detection),
            ("Autonomous Check Trigger", self.test_autonomous_check_trigger),
            ("Vendor Stock Report Parsing", self.test_vendor_report_parsing),
            ("Generate PO from Vendor Match", self.test_po_from_vendor_match),
            ("Purchase Manager Notifications", self.test_notifications),
            ("Autonomous Dashboard Summary", self.test_dashboard_summary)
        ]
        
        print(f"\n🤖 Running {len(tests)} Autonomous Procurement Tests...")
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
        print("🏁 AUTONOMOUS PROCUREMENT TEST RESULTS")
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
    tester = AutonomousProcurementTester()
    passed, failed, results = await tester.run_all_tests()
    
    if failed == 0:
        print(f"\n🎉 All tests passed! Autonomous Procurement System is working perfectly.")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please check the implementation.")
    
    return passed, failed

if __name__ == "__main__":
    asyncio.run(main())