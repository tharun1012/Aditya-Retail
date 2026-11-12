"""
Website Analytics API Tests
Tests for AI Chat Analytics, Expert Consultations, and Abandoned Carts endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAIChatAnalytics:
    """AI Chat Analytics endpoint tests"""
    
    def test_ai_chat_summary(self):
        """Test GET /api/website-analytics/ai-chat/summary"""
        response = requests.get(f"{BASE_URL}/api/website-analytics/ai-chat/summary?days=30")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "success"
        assert "summary" in data
        assert "total_messages" in data["summary"]
        assert "total_sessions" in data["summary"]
        assert "recent_messages" in data["summary"]
        assert "recent_sessions" in data["summary"]
        assert "avg_messages_per_session" in data["summary"]
        assert "agent_breakdown" in data
        assert "sender_breakdown" in data
        assert "daily_trend" in data
        
        # Verify data types
        assert isinstance(data["summary"]["total_messages"], int)
        assert isinstance(data["summary"]["total_sessions"], int)
        print(f"✅ AI Chat Summary: {data['summary']['total_messages']} messages, {data['summary']['total_sessions']} sessions")
    
    def test_ai_chat_sessions_list(self):
        """Test GET /api/website-analytics/ai-chat/sessions"""
        response = requests.get(f"{BASE_URL}/api/website-analytics/ai-chat/sessions?page=1&limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "success"
        assert "sessions" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        
        # Verify pagination
        assert data["page"] == 1
        assert isinstance(data["total"], int)
        assert isinstance(data["pages"], int)
        
        # Verify session structure if sessions exist
        if data["sessions"]:
            session = data["sessions"][0]
            assert "session_id" in session
            assert "message_count" in session
            assert "agent_types" in session
            print(f"✅ AI Chat Sessions: {len(data['sessions'])} sessions returned, {data['total']} total")
        else:
            print("✅ AI Chat Sessions: No sessions found (empty collection)")
    
    def test_ai_chat_session_detail(self):
        """Test GET /api/website-analytics/ai-chat/session/{session_id}"""
        # First get a session ID from the list
        list_response = requests.get(f"{BASE_URL}/api/website-analytics/ai-chat/sessions?page=1&limit=1")
        assert list_response.status_code == 200
        
        list_data = list_response.json()
        if list_data["sessions"]:
            session_id = list_data["sessions"][0]["session_id"]
            
            # Get session detail
            response = requests.get(f"{BASE_URL}/api/website-analytics/ai-chat/session/{session_id}")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            data = response.json()
            assert data["status"] == "success"
            assert data["session_id"] == session_id
            assert "messages" in data
            assert "message_count" in data
            assert isinstance(data["messages"], list)
            
            # Verify message structure
            if data["messages"]:
                msg = data["messages"][0]
                assert "sender" in msg
                assert "message" in msg
                assert "timestamp" in msg
            
            print(f"✅ AI Chat Session Detail: {data['message_count']} messages in session {session_id[:20]}...")
        else:
            print("⚠️ AI Chat Session Detail: Skipped (no sessions available)")
    
    def test_ai_chat_session_not_found(self):
        """Test GET /api/website-analytics/ai-chat/session/{session_id} with invalid ID"""
        response = requests.get(f"{BASE_URL}/api/website-analytics/ai-chat/session/nonexistent_session_12345")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✅ AI Chat Session Not Found: Returns 404 for invalid session")


class TestConsultationsAnalytics:
    """Expert Consultations Analytics endpoint tests"""
    
    def test_consultations_summary(self):
        """Test GET /api/website-analytics/consultations/summary"""
        response = requests.get(f"{BASE_URL}/api/website-analytics/consultations/summary?days=30")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "success"
        assert "summary" in data
        assert "total_consultations" in data["summary"]
        assert "recent_consultations" in data["summary"]
        assert "pending" in data["summary"]
        assert "completed" in data["summary"]
        assert "emails_sent" in data["summary"]
        assert "budget_stats" in data
        assert "appliance_interests" in data
        assert "status_breakdown" in data
        assert "daily_trend" in data
        
        print(f"✅ Consultations Summary: {data['summary']['total_consultations']} total, {data['summary']['pending']} pending")
    
    def test_consultations_list(self):
        """Test GET /api/website-analytics/consultations/list"""
        response = requests.get(f"{BASE_URL}/api/website-analytics/consultations/list?page=1&limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "success"
        assert "consultations" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        
        # Verify pagination
        assert data["page"] == 1
        assert isinstance(data["total"], int)
        
        print(f"✅ Consultations List: {len(data['consultations'])} consultations returned, {data['total']} total")
    
    def test_consultations_list_with_status_filter(self):
        """Test GET /api/website-analytics/consultations/list with status filter"""
        response = requests.get(f"{BASE_URL}/api/website-analytics/consultations/list?page=1&limit=10&status=pending")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "success"
        
        # All returned consultations should have pending status
        for consultation in data["consultations"]:
            assert consultation.get("status") == "pending", f"Expected pending status, got {consultation.get('status')}"
        
        print(f"✅ Consultations List (filtered): {len(data['consultations'])} pending consultations")


class TestAbandonedCartsAnalytics:
    """Abandoned Carts Analytics endpoint tests"""
    
    def test_abandoned_carts_summary(self):
        """Test GET /api/website-analytics/abandoned-carts/summary"""
        response = requests.get(f"{BASE_URL}/api/website-analytics/abandoned-carts/summary?days=30")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "success"
        assert "summary" in data
        assert "total_carts" in data["summary"]
        assert "carts_with_items" in data["summary"]
        assert "total_potential_value" in data["summary"]
        assert "high_value_carts" in data["summary"]
        assert "unique_products_in_carts" in data["summary"]
        assert "most_abandoned_products" in data
        assert "daily_trend" in data
        
        print(f"✅ Abandoned Carts Summary: {data['summary']['total_carts']} carts, ₹{data['summary']['total_potential_value']} potential value")
    
    def test_abandoned_carts_list(self):
        """Test GET /api/website-analytics/abandoned-carts/list"""
        response = requests.get(f"{BASE_URL}/api/website-analytics/abandoned-carts/list?page=1&limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "success"
        assert "carts" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        
        # Verify cart structure if carts exist
        if data["carts"]:
            cart = data["carts"][0]
            assert "session_id" in cart or "id" in cart
            assert "items" in cart
            assert "cart_value" in cart
            print(f"✅ Abandoned Carts List: {len(data['carts'])} carts returned, {data['total']} total")
        else:
            print("✅ Abandoned Carts List: No abandoned carts found (empty collection)")
    
    def test_abandoned_carts_list_with_user_filter(self):
        """Test GET /api/website-analytics/abandoned-carts/list with has_user filter"""
        response = requests.get(f"{BASE_URL}/api/website-analytics/abandoned-carts/list?page=1&limit=10&has_user=true")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "success"
        
        # All returned carts should have user_id
        for cart in data["carts"]:
            assert cart.get("user_id") is not None, "Expected cart with user_id"
        
        print(f"✅ Abandoned Carts List (with user): {len(data['carts'])} carts with registered users")
    
    def test_send_recovery_email_missing_params(self):
        """Test POST /api/website-analytics/abandoned-carts/send-recovery-email with missing params"""
        response = requests.post(
            f"{BASE_URL}/api/website-analytics/abandoned-carts/send-recovery-email",
            json={"email": "test@example.com"}  # Missing cart_id or session_id
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✅ Recovery Email: Returns 400 when cart_id/session_id missing")
    
    def test_send_recovery_email_cart_not_found(self):
        """Test POST /api/website-analytics/abandoned-carts/send-recovery-email with invalid cart"""
        response = requests.post(
            f"{BASE_URL}/api/website-analytics/abandoned-carts/send-recovery-email",
            json={
                "cart_id": "nonexistent_cart_12345",
                "email": "test@example.com"
            }
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✅ Recovery Email: Returns 404 for non-existent cart")
    
    def test_bulk_recovery_endpoint(self):
        """Test POST /api/website-analytics/abandoned-carts/bulk-recovery"""
        response = requests.post(
            f"{BASE_URL}/api/website-analytics/abandoned-carts/bulk-recovery?min_value=10000&max_emails=5"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "success"
        assert "emails_queued" in data
        assert "min_value_threshold" in data
        
        print(f"✅ Bulk Recovery: {data['emails_queued']} emails queued (min value: ₹{data['min_value_threshold']})")


class TestCrossTabIntegration:
    """Cross-tab integration tests"""
    
    def test_all_summaries_load(self):
        """Test that all three summary endpoints work together"""
        # AI Chat Summary
        chat_response = requests.get(f"{BASE_URL}/api/website-analytics/ai-chat/summary?days=30")
        assert chat_response.status_code == 200
        
        # Consultations Summary
        consult_response = requests.get(f"{BASE_URL}/api/website-analytics/consultations/summary?days=30")
        assert consult_response.status_code == 200
        
        # Abandoned Carts Summary
        carts_response = requests.get(f"{BASE_URL}/api/website-analytics/abandoned-carts/summary?days=30")
        assert carts_response.status_code == 200
        
        print("✅ All three analytics summaries load successfully")
    
    def test_pagination_consistency(self):
        """Test pagination works consistently across all list endpoints"""
        endpoints = [
            "/api/website-analytics/ai-chat/sessions",
            "/api/website-analytics/consultations/list",
            "/api/website-analytics/abandoned-carts/list"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}?page=1&limit=5")
            assert response.status_code == 200, f"Failed for {endpoint}"
            
            data = response.json()
            assert "page" in data
            assert "pages" in data
            assert "total" in data
            assert data["page"] == 1
        
        print("✅ Pagination works consistently across all list endpoints")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
