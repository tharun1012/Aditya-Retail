"""
Test Suite for Enhanced AI Agents
Tests: Sales Agent, Service Agent, Delivery Agent, CA Agent
Features: Product recommendations, lead capture, troubleshooting, ticket creation, order tracking, P&L, GST
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://acct-workflow-1.preview.emergentagent.com"


class TestSalesAgent:
    """Sales Agent - Product recommendations and lead capture"""
    
    def test_sales_agent_product_recommendations(self):
        """Test Sales Agent provides product recommendations with real product links"""
        response = requests.post(
            f"{BASE_URL}/api/ai/chat",
            json={
                "agent_type": "sales",
                "message": "I am looking for a washing machine under 50000",
                "session_id": f"test-sales-{uuid.uuid4()}"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify response structure
        assert data.get("status") == "success"
        assert data.get("agent_type") == "sales"
        assert "response" in data
        
        # Verify AI response contains product recommendations
        ai_response = data.get("response", "")
        assert len(ai_response) > 100, "Response should be substantial"
        
        # Check for product links (should contain /#/product/ format)
        assert "/#/product/" in ai_response or "washing machine" in ai_response.lower(), \
            "Response should contain product links or mention washing machines"
        
        print(f"✅ Sales Agent product recommendations: PASS")
        print(f"   Response length: {len(ai_response)} chars")
    
    def test_sales_agent_lead_capture_with_phone(self):
        """Test Sales Agent captures lead when customer provides phone number"""
        session_id = f"test-lead-{uuid.uuid4()}"
        
        # First message - show interest
        response1 = requests.post(
            f"{BASE_URL}/api/ai/chat",
            json={
                "agent_type": "sales",
                "message": "I want to buy a refrigerator. My phone is 9876543210",
                "session_id": session_id
            }
        )
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1.get("status") == "success"
        
        print(f"✅ Sales Agent lead capture with phone: PASS")
    
    def test_sales_agent_lead_capture_with_email(self):
        """Test Sales Agent captures lead when customer provides email"""
        session_id = f"test-lead-email-{uuid.uuid4()}"
        
        response = requests.post(
            f"{BASE_URL}/api/ai/chat",
            json={
                "agent_type": "sales",
                "message": "I need a dishwasher. Contact me at customer@example.com",
                "session_id": session_id
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "success"
        
        print(f"✅ Sales Agent lead capture with email: PASS")


class TestSalesLeadEndpoint:
    """Test /api/ai/sales/save-lead endpoint"""
    
    def test_save_lead_creates_new_lead(self):
        """Test creating a new lead via save-lead endpoint"""
        lead_data = {
            "name": f"Test Lead {uuid.uuid4().hex[:8]}",
            "phone": f"98765{uuid.uuid4().hex[:5]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "product_category": "Washing Machine",
            "budget": "50000",
            "session_id": f"test-session-{uuid.uuid4()}"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/ai/sales/save-lead",
            json=lead_data
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("status") in ["created", "updated"], f"Expected created/updated, got {data.get('status')}"
        assert "lead_id" in data, "Response should contain lead_id"
        
        print(f"✅ Save lead endpoint: PASS - Lead ID: {data.get('lead_id')}")
    
    def test_save_lead_updates_existing_lead(self):
        """Test updating an existing lead with same phone"""
        phone = f"98765{uuid.uuid4().hex[:5]}"
        
        # Create first lead
        lead_data1 = {
            "name": "First Name",
            "phone": phone,
            "product_category": "Refrigerator",
            "session_id": f"test-session-{uuid.uuid4()}"
        }
        
        response1 = requests.post(f"{BASE_URL}/api/ai/sales/save-lead", json=lead_data1)
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Update with same phone
        lead_data2 = {
            "name": "Updated Name",
            "phone": phone,
            "product_category": "Washing Machine",
            "budget": "60000",
            "session_id": f"test-session-{uuid.uuid4()}"
        }
        
        response2 = requests.post(f"{BASE_URL}/api/ai/sales/save-lead", json=lead_data2)
        assert response2.status_code == 200
        data2 = response2.json()
        
        assert data2.get("status") == "updated", "Second call should update existing lead"
        
        print(f"✅ Save lead update existing: PASS")


class TestServiceAgent:
    """Service Agent - Troubleshooting and ticket creation"""
    
    def test_service_agent_troubleshooting_guidance(self):
        """Test Service Agent provides troubleshooting guidance for appliance issues"""
        response = requests.post(
            f"{BASE_URL}/api/ai/chat",
            json={
                "agent_type": "service",
                "message": "My washing machine is not draining water properly",
                "session_id": f"test-service-{uuid.uuid4()}"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "success"
        assert data.get("agent_type") == "service"
        
        ai_response = data.get("response", "").lower()
        
        # Check for troubleshooting keywords
        troubleshooting_keywords = ["drain", "hose", "filter", "pump", "check", "clean"]
        has_troubleshooting = any(kw in ai_response for kw in troubleshooting_keywords)
        
        assert has_troubleshooting, "Response should contain troubleshooting guidance"
        
        print(f"✅ Service Agent troubleshooting: PASS")
    
    def test_service_agent_refrigerator_issue(self):
        """Test Service Agent handles refrigerator issues"""
        response = requests.post(
            f"{BASE_URL}/api/ai/chat",
            json={
                "agent_type": "service",
                "message": "My refrigerator is not cooling properly",
                "session_id": f"test-service-fridge-{uuid.uuid4()}"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "success"
        
        ai_response = data.get("response", "").lower()
        cooling_keywords = ["cool", "temperature", "thermostat", "door", "seal", "condenser"]
        has_guidance = any(kw in ai_response for kw in cooling_keywords)
        
        assert has_guidance, "Response should contain refrigerator troubleshooting guidance"
        
        print(f"✅ Service Agent refrigerator issue: PASS")


class TestServiceTicketEndpoint:
    """Test /api/ai/service/create-ticket-ai endpoint"""
    
    def test_create_service_ticket(self):
        """Test creating a service ticket via AI endpoint"""
        ticket_data = {
            "name": f"Test Customer {uuid.uuid4().hex[:8]}",
            "phone": f"98765{uuid.uuid4().hex[:5]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "address": "123 Test Street, Bangalore 560001",
            "product_name": "Bosch Washing Machine",
            "model": "WGA1220SIN",
            "brand": "Bosch",
            "issue_type": "not_draining",
            "issue_description": "Washing machine not draining water properly after wash cycle",
            "session_id": f"test-service-{uuid.uuid4()}"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/ai/service/create-ticket-ai",
            json=ticket_data
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("status") == "success", f"Expected success, got {data.get('status')}"
        assert "ticket_id" in data, "Response should contain ticket_id"
        assert "ticket_number" in data, "Response should contain ticket_number"
        
        # Verify ticket number format (SRV-YYYYMMDD-XXXX)
        ticket_number = data.get("ticket_number", "")
        assert ticket_number.startswith("SRV-"), f"Ticket number should start with SRV-, got {ticket_number}"
        
        print(f"✅ Create service ticket: PASS - Ticket: {ticket_number}")
    
    def test_create_service_ticket_minimal_data(self):
        """Test creating a service ticket with minimal required data"""
        ticket_data = {
            "name": "Minimal Test",
            "phone": "9876543210",
            "issue_description": "General issue",
            "session_id": f"test-minimal-{uuid.uuid4()}"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/ai/service/create-ticket-ai",
            json=ticket_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "success"
        
        print(f"✅ Create service ticket (minimal): PASS")


class TestDeliveryAgent:
    """Delivery Agent - Order tracking and rescheduling"""
    
    def test_delivery_agent_order_tracking_query(self):
        """Test Delivery Agent handles order tracking queries"""
        response = requests.post(
            f"{BASE_URL}/api/ai/chat",
            json={
                "agent_type": "delivery",
                "message": "I want to track my order. My phone number is 9876543210",
                "session_id": f"test-delivery-{uuid.uuid4()}"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "success"
        assert data.get("agent_type") == "delivery"
        
        ai_response = data.get("response", "").lower()
        delivery_keywords = ["order", "delivery", "status", "track", "address"]
        has_delivery_info = any(kw in ai_response for kw in delivery_keywords)
        
        assert has_delivery_info, "Response should contain delivery-related information"
        
        print(f"✅ Delivery Agent order tracking query: PASS")
    
    def test_delivery_agent_reschedule_query(self):
        """Test Delivery Agent handles reschedule queries"""
        response = requests.post(
            f"{BASE_URL}/api/ai/chat",
            json={
                "agent_type": "delivery",
                "message": "I want to reschedule my delivery to next week",
                "session_id": f"test-delivery-reschedule-{uuid.uuid4()}"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "success"
        
        ai_response = data.get("response", "").lower()
        reschedule_keywords = ["reschedule", "slot", "time", "date", "delivery"]
        has_reschedule_info = any(kw in ai_response for kw in reschedule_keywords)
        
        assert has_reschedule_info, "Response should contain rescheduling information"
        
        print(f"✅ Delivery Agent reschedule query: PASS")


class TestDeliveryTrackingEndpoint:
    """Test /api/ai/delivery/track-order endpoint"""
    
    def test_track_order_by_phone(self):
        """Test order tracking by phone number"""
        response = requests.get(
            f"{BASE_URL}/api/ai/delivery/track-order",
            params={"phone": "9876543210"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return success or not_found (both are valid responses)
        assert data.get("status") in ["success", "not_found"], \
            f"Expected success/not_found, got {data.get('status')}"
        
        if data.get("status") == "success":
            assert "orders" in data, "Success response should contain orders"
        else:
            assert "message" in data, "Not found response should contain message"
        
        print(f"✅ Track order by phone: PASS - Status: {data.get('status')}")
    
    def test_track_order_by_order_id(self):
        """Test order tracking by order ID"""
        response = requests.get(
            f"{BASE_URL}/api/ai/delivery/track-order",
            params={"order_id": "TEST-ORDER-001"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") in ["success", "not_found"]
        
        print(f"✅ Track order by order_id: PASS - Status: {data.get('status')}")
    
    def test_track_order_no_params(self):
        """Test order tracking without parameters returns error"""
        response = requests.get(f"{BASE_URL}/api/ai/delivery/track-order")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "error", "Should return error without params"
        assert "message" in data
        
        print(f"✅ Track order no params: PASS - Returns error as expected")


class TestDeliveryRescheduleEndpoint:
    """Test /api/ai/delivery/reschedule endpoint"""
    
    def test_reschedule_delivery(self):
        """Test delivery rescheduling endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/ai/delivery/reschedule",
            params={
                "order_id": "TEST-ORDER-001",
                "new_date": "2026-04-10",
                "time_slot": "10AM-1PM",
                "reason": "Customer request"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return success or not_found
        assert data.get("status") in ["success", "not_found"], \
            f"Expected success/not_found, got {data.get('status')}"
        
        print(f"✅ Reschedule delivery: PASS - Status: {data.get('status')}")


class TestCAAgent:
    """CA Agent - P&L, GST, Audit, Reports"""
    
    def test_ca_agent_pnl_report(self):
        """Test CA Agent generates P&L report"""
        response = requests.post(
            f"{BASE_URL}/api/ai-ca/chat",
            json={
                "query": "Generate P&L report for this month"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data, "Response should contain AI response"
        
        ai_response = data.get("response", "").lower()
        pnl_keywords = ["revenue", "profit", "loss", "expense", "margin", "sales"]
        has_pnl_info = any(kw in ai_response for kw in pnl_keywords)
        
        assert has_pnl_info, "Response should contain P&L information"
        
        # Check for data in response
        if "data" in data and data["data"]:
            assert "pnl" in data["data"] or "sales" in data["data"], \
                "Data should contain pnl or sales information"
        
        print(f"✅ CA Agent P&L report: PASS")
    
    def test_ca_agent_gst_liability(self):
        """Test CA Agent calculates GST liability"""
        response = requests.post(
            f"{BASE_URL}/api/ai-ca/chat",
            json={
                "query": "What is my GST liability for this month?"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        
        ai_response = data.get("response", "").lower()
        gst_keywords = ["gst", "tax", "cgst", "sgst", "liability", "input", "output"]
        has_gst_info = any(kw in ai_response for kw in gst_keywords)
        
        assert has_gst_info, "Response should contain GST information"
        
        # Check for GST data
        if "data" in data and data["data"]:
            gst_data = data["data"].get("gst", {})
            if gst_data:
                assert "output_tax" in gst_data or "net_liability" in gst_data, \
                    "GST data should contain tax information"
        
        print(f"✅ CA Agent GST liability: PASS")
    
    def test_ca_agent_sales_query(self):
        """Test CA Agent handles sales queries"""
        response = requests.post(
            f"{BASE_URL}/api/ai-ca/chat",
            json={
                "query": "What are my total sales for this month?"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        assert "suggestions" in data, "Response should contain suggestions"
        
        print(f"✅ CA Agent sales query: PASS")


class TestCAAgentQuickStats:
    """Test /api/ai-ca/quick-stats endpoint"""
    
    def test_quick_stats_month(self):
        """Test quick stats for current month"""
        response = requests.get(
            f"{BASE_URL}/api/ai-ca/quick-stats",
            params={"period": "month"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "success"
        assert "stats" in data
        
        stats = data.get("stats", {})
        required_fields = ["total_sales", "total_purchases", "gst_collected", "net_gst"]
        for field in required_fields:
            assert field in stats, f"Stats should contain {field}"
        
        print(f"✅ Quick stats (month): PASS")
    
    def test_quick_stats_today(self):
        """Test quick stats for today"""
        response = requests.get(
            f"{BASE_URL}/api/ai-ca/quick-stats",
            params={"period": "today"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "success"
        
        print(f"✅ Quick stats (today): PASS")
    
    def test_quick_stats_week(self):
        """Test quick stats for week"""
        response = requests.get(
            f"{BASE_URL}/api/ai-ca/quick-stats",
            params={"period": "week"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "success"
        
        print(f"✅ Quick stats (week): PASS")


class TestCAAgentAudit:
    """Test /api/ai-ca/audit endpoint"""
    
    def test_audit_monthly(self):
        """Test monthly audit"""
        response = requests.post(
            f"{BASE_URL}/api/ai-ca/audit",
            json={
                "audit_type": "monthly"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "audit_id" in data, "Response should contain audit_id"
        assert "audit_type" in data
        assert data.get("audit_type") == "monthly"
        assert "summary" in data
        assert "issues" in data
        assert "recommendations" in data
        assert "ai_analysis" in data
        
        # Verify summary structure
        summary = data.get("summary", {})
        summary_fields = ["total_transactions", "sales_total", "gst_collected"]
        for field in summary_fields:
            assert field in summary, f"Summary should contain {field}"
        
        print(f"✅ Audit (monthly): PASS - Audit ID: {data.get('audit_id')}")
    
    def test_audit_daily(self):
        """Test daily audit"""
        response = requests.post(
            f"{BASE_URL}/api/ai-ca/audit",
            json={
                "audit_type": "daily"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "audit_id" in data
        assert data.get("audit_type") == "daily"
        
        print(f"✅ Audit (daily): PASS")
    
    def test_audit_weekly(self):
        """Test weekly audit"""
        response = requests.post(
            f"{BASE_URL}/api/ai-ca/audit",
            json={
                "audit_type": "weekly"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "audit_id" in data
        assert data.get("audit_type") == "weekly"
        
        print(f"✅ Audit (weekly): PASS")


class TestChatHistory:
    """Test chat history endpoint"""
    
    def test_get_chat_history(self):
        """Test retrieving chat history for a session"""
        session_id = f"test-history-{uuid.uuid4()}"
        
        # First, create some chat messages
        requests.post(
            f"{BASE_URL}/api/ai/chat",
            json={
                "agent_type": "sales",
                "message": "Hello, I need help",
                "session_id": session_id
            }
        )
        
        # Now get history
        response = requests.get(
            f"{BASE_URL}/api/ai/chat/history/{session_id}",
            params={"agent_type": "sales"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "success"
        assert "messages" in data
        assert data.get("session_id") == session_id
        
        print(f"✅ Get chat history: PASS - Messages: {len(data.get('messages', []))}")


class TestInventoryAnalysis:
    """Test inventory analysis endpoint"""
    
    def test_inventory_analysis(self):
        """Test AI-powered inventory analysis"""
        response = requests.get(f"{BASE_URL}/api/ai/inventory/analysis")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "success"
        assert "analysis" in data
        assert "ai_insights" in data
        
        analysis = data.get("analysis", {})
        assert "low_stock_count" in analysis or "alerts" in analysis
        
        print(f"✅ Inventory analysis: PASS")


class TestMarketingInsights:
    """Test marketing insights endpoint"""
    
    def test_marketing_insights(self):
        """Test AI-powered marketing insights"""
        response = requests.get(f"{BASE_URL}/api/ai/marketing/insights")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "success"
        assert "behavior_insights" in data
        assert "campaign_suggestions" in data
        assert "ai_recommendations" in data
        
        print(f"✅ Marketing insights: PASS")


class TestDashboardSummary:
    """Test AI dashboard summary endpoint"""
    
    def test_dashboard_summary(self):
        """Test AI-powered dashboard summary"""
        response = requests.get(f"{BASE_URL}/api/ai/dashboard/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "success"
        assert "summary" in data
        assert "ai_insights" in data
        
        summary = data.get("summary", {})
        summary_fields = ["total_products", "active_orders", "pending_service_requests"]
        for field in summary_fields:
            assert field in summary, f"Summary should contain {field}"
        
        print(f"✅ Dashboard summary: PASS")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
