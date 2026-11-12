"""
Test Suite for Multi-Store, Advanced Reports, and AI Chat Context Retention
Tests: Store Login, Store Dashboard, Report Export (PDF/Excel), Customer Reorder, AI Chat Sessions
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://acct-workflow-1.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "admin@adityaretail.com"
ADMIN_PASSWORD = "admin123"
STORE_MANAGER_EMAIL = "manager@mgroad.adityaretail.com"
STORE_MANAGER_PASSWORD = "store123"


class TestStoreAuthentication:
    """Test store manager authentication"""
    
    def test_store_login_success(self):
        """Test store manager login with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/stores/auth/login",
            json={"email": STORE_MANAGER_EMAIL, "password": STORE_MANAGER_PASSWORD}
        )
        print(f"Store login response: {response.status_code}")
        
        # Check status code
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success", f"Login failed: {data}"
        assert "token" in data, "Token not returned"
        assert "user" in data, "User data not returned"
        assert "store" in data, "Store data not returned"
        
        # Verify user data
        user = data["user"]
        assert user.get("email") == STORE_MANAGER_EMAIL.lower()
        assert user.get("role") in ["store_manager", "store_staff"]
        
        # Verify store data
        store = data["store"]
        assert "id" in store
        assert "name" in store
        assert "code" in store
        
        print(f"✓ Store login successful - User: {user.get('first_name')} {user.get('last_name')}, Store: {store.get('name')}")
        return data
    
    def test_store_login_invalid_credentials(self):
        """Test store login with invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/stores/auth/login",
            json={"email": "invalid@test.com", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid credentials correctly rejected")
    
    def test_store_login_missing_fields(self):
        """Test store login with missing fields"""
        response = requests.post(
            f"{BASE_URL}/api/stores/auth/login",
            json={"email": STORE_MANAGER_EMAIL}
        )
        
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        print("✓ Missing password correctly rejected")


class TestStoreDashboard:
    """Test store dashboard endpoints"""
    
    @pytest.fixture
    def store_auth(self):
        """Get store authentication data"""
        response = requests.post(
            f"{BASE_URL}/api/stores/auth/login",
            json={"email": STORE_MANAGER_EMAIL, "password": STORE_MANAGER_PASSWORD}
        )
        if response.status_code == 200:
            return response.json()
        pytest.skip("Store login failed")
    
    def test_store_dashboard_overview(self, store_auth):
        """Test store dashboard overview endpoint"""
        store_id = store_auth["store"]["id"]
        
        response = requests.get(f"{BASE_URL}/api/stores/{store_id}/dashboard?period=today")
        
        assert response.status_code == 200, f"Dashboard failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        assert "summary" in data
        
        summary = data["summary"]
        # Check expected fields exist
        expected_fields = ["total_sales", "order_count", "total_purchases", "pending_deliveries", "low_stock_items"]
        for field in expected_fields:
            assert field in summary, f"Missing field: {field}"
        
        print(f"✓ Dashboard overview - Sales: ₹{summary.get('total_sales', 0)}, Orders: {summary.get('order_count', 0)}")
    
    def test_store_dashboard_periods(self, store_auth):
        """Test dashboard with different periods"""
        store_id = store_auth["store"]["id"]
        
        periods = ["today", "week", "month", "year"]
        for period in periods:
            response = requests.get(f"{BASE_URL}/api/stores/{store_id}/dashboard?period={period}")
            assert response.status_code == 200, f"Dashboard failed for period {period}"
            print(f"✓ Dashboard period '{period}' works")
    
    def test_store_inventory(self, store_auth):
        """Test store inventory endpoint"""
        store_id = store_auth["store"]["id"]
        
        response = requests.get(f"{BASE_URL}/api/inventory/store/{store_id}?low_stock_only=false")
        
        assert response.status_code == 200, f"Inventory failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        print(f"✓ Store inventory retrieved - Products: {len(data.get('products', []))}")
    
    def test_store_orders(self, store_auth):
        """Test store orders endpoint"""
        store_id = store_auth["store"]["id"]
        
        response = requests.get(f"{BASE_URL}/api/reports/so/list?store_id={store_id}")
        
        assert response.status_code == 200, f"Orders failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        print(f"✓ Store orders retrieved - Count: {len(data.get('orders', []))}")
    
    def test_store_transfers(self, store_auth):
        """Test store transfers endpoint"""
        store_id = store_auth["store"]["id"]
        
        response = requests.get(f"{BASE_URL}/api/inventory/transfers?store_id={store_id}")
        
        assert response.status_code == 200, f"Transfers failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        print(f"✓ Store transfers retrieved - Count: {len(data.get('transfers', []))}")


class TestAdvancedReports:
    """Test advanced reports endpoints"""
    
    def test_daily_sales_report(self):
        """Test daily sales report"""
        today = datetime.now().strftime("%Y-%m-%d")
        response = requests.get(f"{BASE_URL}/api/reports/sales/daily?date={today}")
        
        assert response.status_code == 200, f"Daily report failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        print(f"✓ Daily sales report - Orders: {len(data.get('orders', []))}")
    
    def test_monthly_sales_report(self):
        """Test monthly sales report"""
        year = datetime.now().year
        month = datetime.now().month
        
        response = requests.get(f"{BASE_URL}/api/reports/sales/monthly?year={year}&month={month}")
        
        assert response.status_code == 200, f"Monthly report failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        print(f"✓ Monthly sales report retrieved")
    
    def test_yearly_sales_report(self):
        """Test yearly sales report"""
        year = datetime.now().year
        
        response = requests.get(f"{BASE_URL}/api/reports/sales/yearly?year={year}")
        
        assert response.status_code == 200, f"Yearly report failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        print(f"✓ Yearly sales report retrieved")
    
    def test_item_wise_sales_report(self):
        """Test item-wise sales report"""
        response = requests.get(f"{BASE_URL}/api/reports/sales/by-item?limit=20")
        
        assert response.status_code == 200, f"Item-wise report failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        print(f"✓ Item-wise sales report - Items: {len(data.get('items', []))}")
    
    def test_pending_deliveries_report(self):
        """Test pending deliveries report"""
        response = requests.get(f"{BASE_URL}/api/reports/pending/deliveries")
        
        assert response.status_code == 200, f"Pending deliveries failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        print(f"✓ Pending deliveries report - Count: {data.get('total_pending', 0)}")
    
    def test_pending_purchase_orders_report(self):
        """Test pending purchase orders report"""
        response = requests.get(f"{BASE_URL}/api/reports/pending/purchase-orders")
        
        assert response.status_code == 200, f"Pending PO failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        print(f"✓ Pending PO report retrieved")
    
    def test_pending_bills_report(self):
        """Test pending purchase bills report"""
        response = requests.get(f"{BASE_URL}/api/reports/pending/purchase-bills")
        
        assert response.status_code == 200, f"Pending bills failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        print(f"✓ Pending bills report retrieved")


class TestReportExport:
    """Test report export functionality (PDF/Excel)"""
    
    def test_export_daily_sales_excel(self):
        """Test export daily sales to Excel"""
        response = requests.get(f"{BASE_URL}/api/reports/export/sales/daily?format=excel")
        
        assert response.status_code == 200, f"Excel export failed: {response.status_code}"
        assert "spreadsheet" in response.headers.get("content-type", "").lower() or \
               "octet-stream" in response.headers.get("content-type", "").lower(), \
               f"Wrong content type: {response.headers.get('content-type')}"
        
        # Check file size
        assert len(response.content) > 0, "Empty Excel file"
        print(f"✓ Daily sales Excel export - Size: {len(response.content)} bytes")
    
    def test_export_daily_sales_pdf(self):
        """Test export daily sales to PDF"""
        response = requests.get(f"{BASE_URL}/api/reports/export/sales/daily?format=pdf")
        
        assert response.status_code == 200, f"PDF export failed: {response.status_code}"
        assert "pdf" in response.headers.get("content-type", "").lower(), \
               f"Wrong content type: {response.headers.get('content-type')}"
        
        # Check file size
        assert len(response.content) > 0, "Empty PDF file"
        print(f"✓ Daily sales PDF export - Size: {len(response.content)} bytes")
    
    def test_export_monthly_sales_excel(self):
        """Test export monthly sales to Excel"""
        year = datetime.now().year
        month = datetime.now().month
        
        response = requests.get(f"{BASE_URL}/api/reports/export/sales/monthly?format=excel&year={year}&month={month}")
        
        assert response.status_code == 200, f"Monthly Excel export failed: {response.status_code}"
        assert len(response.content) > 0, "Empty Excel file"
        print(f"✓ Monthly sales Excel export - Size: {len(response.content)} bytes")
    
    def test_export_item_wise_sales_excel(self):
        """Test export item-wise sales to Excel"""
        response = requests.get(f"{BASE_URL}/api/reports/export/sales/item-wise?format=excel")
        
        assert response.status_code == 200, f"Item-wise Excel export failed: {response.status_code}"
        assert len(response.content) > 0, "Empty Excel file"
        print(f"✓ Item-wise sales Excel export - Size: {len(response.content)} bytes")
    
    def test_export_pending_deliveries_excel(self):
        """Test export pending deliveries to Excel"""
        response = requests.get(f"{BASE_URL}/api/reports/export/pending/deliveries?format=excel")
        
        assert response.status_code == 200, f"Pending deliveries Excel export failed: {response.status_code}"
        assert len(response.content) > 0, "Empty Excel file"
        print(f"✓ Pending deliveries Excel export - Size: {len(response.content)} bytes")
    
    def test_export_pending_deliveries_pdf(self):
        """Test export pending deliveries to PDF"""
        response = requests.get(f"{BASE_URL}/api/reports/export/pending/deliveries?format=pdf")
        
        assert response.status_code == 200, f"Pending deliveries PDF export failed: {response.status_code}"
        assert len(response.content) > 0, "Empty PDF file"
        print(f"✓ Pending deliveries PDF export - Size: {len(response.content)} bytes")


class TestAIChatContextRetention:
    """Test AI chat context retention for logged-in users"""
    
    def test_neural_ai_chat_with_user_id(self):
        """Test AI chat stores user_id for context retention"""
        test_user_id = "test_user_123"
        test_session_id = f"test_session_{datetime.now().timestamp()}"
        
        response = requests.post(
            f"{BASE_URL}/api/neural-ai/chat",
            json={
                "agent_type": "sales",
                "message": "I'm looking for a washing machine",
                "session_id": test_session_id,
                "user_id": test_user_id,
                "context": {"user_name": "Test User"}
            }
        )
        
        assert response.status_code == 200, f"AI chat failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        assert "response" in data
        assert data.get("session_id") == test_session_id
        
        print(f"✓ AI chat with user_id - Response received")
        return test_session_id, test_user_id
    
    def test_get_user_sessions(self):
        """Test retrieving user's previous chat sessions"""
        # First create a session
        test_user_id = f"test_user_{datetime.now().timestamp()}"
        test_session_id = f"test_session_{datetime.now().timestamp()}"
        
        # Create a chat message
        requests.post(
            f"{BASE_URL}/api/neural-ai/chat",
            json={
                "agent_type": "sales",
                "message": "Hello, I need help",
                "session_id": test_session_id,
                "user_id": test_user_id
            }
        )
        
        # Get user sessions
        response = requests.get(f"{BASE_URL}/api/neural-ai/user-sessions/{test_user_id}?limit=5")
        
        assert response.status_code == 200, f"Get user sessions failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        assert "sessions" in data
        
        print(f"✓ User sessions retrieved - Count: {len(data.get('sessions', []))}")
    
    def test_resume_session(self):
        """Test resuming a previous chat session"""
        # First create a session
        test_user_id = f"test_user_{datetime.now().timestamp()}"
        test_session_id = f"test_session_{datetime.now().timestamp()}"
        
        # Create a chat message
        requests.post(
            f"{BASE_URL}/api/neural-ai/chat",
            json={
                "agent_type": "service",
                "message": "My dishwasher is not working",
                "session_id": test_session_id,
                "user_id": test_user_id
            }
        )
        
        # Resume session
        response = requests.post(f"{BASE_URL}/api/neural-ai/resume-session?session_id={test_session_id}")
        
        assert response.status_code == 200, f"Resume session failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        assert "messages" in data
        assert data.get("can_resume") == True
        
        print(f"✓ Session resumed - Messages: {len(data.get('messages', []))}")
    
    def test_conversation_history(self):
        """Test getting conversation history for a session"""
        test_session_id = f"test_session_{datetime.now().timestamp()}"
        
        # Create a chat message
        requests.post(
            f"{BASE_URL}/api/neural-ai/chat",
            json={
                "agent_type": "delivery",
                "message": "Where is my order?",
                "session_id": test_session_id
            }
        )
        
        # Get conversation history
        response = requests.get(f"{BASE_URL}/api/neural-ai/conversation-history/{test_session_id}")
        
        assert response.status_code == 200, f"Get history failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        assert "messages" in data
        
        print(f"✓ Conversation history retrieved - Messages: {data.get('message_count', 0)}")


class TestCustomerDashboard:
    """Test customer dashboard endpoints"""
    
    @pytest.fixture
    def customer_auth(self):
        """Get customer authentication"""
        # Try to login as a customer
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "test@example.com", "password": "test123"}
        )
        if response.status_code == 200:
            return response.json()
        
        # Create a test customer if login fails
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "username": "testcustomer",
                "email": "testcustomer@example.com",
                "password": "test123",
                "first_name": "Test",
                "last_name": "Customer"
            }
        )
        
        if register_response.status_code in [200, 400]:  # 400 if already exists
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": "testcustomer", "password": "test123"}
            )
            if login_response.status_code == 200:
                return login_response.json()
        
        pytest.skip("Could not authenticate customer")
    
    def test_customer_profile(self, customer_auth):
        """Test customer profile endpoint"""
        user_id = customer_auth["user"]["id"]
        
        response = requests.get(f"{BASE_URL}/api/customer/profile?user_id={user_id}")
        
        assert response.status_code == 200, f"Profile failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        print(f"✓ Customer profile retrieved")
    
    def test_customer_orders(self, customer_auth):
        """Test customer orders endpoint"""
        user_id = customer_auth["user"]["id"]
        
        response = requests.get(f"{BASE_URL}/api/customer/orders?user_id={user_id}&page=1&limit=10")
        
        assert response.status_code == 200, f"Orders failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        assert "orders" in data
        assert "pagination" in data
        
        print(f"✓ Customer orders retrieved - Count: {len(data.get('orders', []))}")


class TestStoresList:
    """Test stores list endpoint"""
    
    def test_list_stores(self):
        """Test listing all stores"""
        response = requests.get(f"{BASE_URL}/api/stores/")
        
        assert response.status_code == 200, f"List stores failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        assert "stores" in data
        
        stores = data.get("stores", [])
        print(f"✓ Stores list retrieved - Count: {len(stores)}")
        
        if stores:
            store = stores[0]
            assert "id" in store
            assert "name" in store
            assert "code" in store
            print(f"  First store: {store.get('name')} ({store.get('code')})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
