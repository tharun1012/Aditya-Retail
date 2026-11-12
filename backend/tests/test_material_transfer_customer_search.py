"""
Backend API Tests for Material Transfer and Customer Search Features
Tests:
1. GET /api/delivery-challans/material-transfer/list - List material transfer DCs with filters
2. POST /api/delivery-challans/material-transfer/{challan_id}/receive - Receive material transfer
3. GET /api/customers/search?q={query} - Customer search API
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://acct-workflow-1.preview.emergentagent.com')

# Test credentials from review request
STORE_MANAGER_EMAIL = "hrbr.adityaretail@gmail.com"
STORE_MANAGER_PASSWORD = "Hrbr@2026"
ADMIN_EMAIL = "rohit.gadiya@gmail.com"
ADMIN_PASSWORD = "Purvi@vriddhi01"


class TestMaterialTransferListAPI:
    """Tests for GET /api/delivery-challans/material-transfer/list endpoint"""
    
    def test_list_material_transfer_dcs_no_filters(self):
        """Test listing material transfer DCs without any filters"""
        response = requests.get(f"{BASE_URL}/api/delivery-challans/material-transfer/list")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success", f"Expected success status, got: {data}"
        assert "challans" in data, "Response should contain 'challans' key"
        assert "total" in data, "Response should contain 'total' key"
        assert "page" in data, "Response should contain 'page' key"
        assert "limit" in data, "Response should contain 'limit' key"
        assert isinstance(data["challans"], list), "challans should be a list"
        print(f"✓ List material transfer DCs - Found {data['total']} challans")
    
    def test_list_material_transfer_dcs_with_to_location_filter(self):
        """Test listing material transfer DCs filtered by to_location"""
        # Test with HRBR store code
        response = requests.get(f"{BASE_URL}/api/delivery-challans/material-transfer/list?to_location=HRBR")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        assert "challans" in data
        
        # Verify all returned challans have to_location.code = HRBR
        for challan in data["challans"]:
            to_loc = challan.get("to_location", {})
            assert to_loc.get("code") == "HRBR", f"Expected to_location.code=HRBR, got {to_loc.get('code')}"
        
        print(f"✓ List with to_location=HRBR filter - Found {len(data['challans'])} challans")
    
    def test_list_material_transfer_dcs_with_status_filter(self):
        """Test listing material transfer DCs filtered by status"""
        # Test with dispatched status
        response = requests.get(f"{BASE_URL}/api/delivery-challans/material-transfer/list?status=dispatched")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        assert "challans" in data
        
        # Verify all returned challans have status = dispatched
        for challan in data["challans"]:
            assert challan.get("status") == "dispatched", f"Expected status=dispatched, got {challan.get('status')}"
        
        print(f"✓ List with status=dispatched filter - Found {len(data['challans'])} challans")
    
    def test_list_material_transfer_dcs_with_combined_filters(self):
        """Test listing material transfer DCs with both to_location and status filters"""
        response = requests.get(f"{BASE_URL}/api/delivery-challans/material-transfer/list?to_location=HRBR&status=dispatched&limit=50")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        assert "challans" in data
        assert data.get("limit") == 50
        
        print(f"✓ List with combined filters - Found {len(data['challans'])} challans")
    
    def test_list_material_transfer_dcs_pagination(self):
        """Test pagination parameters work correctly"""
        response = requests.get(f"{BASE_URL}/api/delivery-challans/material-transfer/list?page=1&limit=10")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "success"
        assert data.get("page") == 1
        assert data.get("limit") == 10
        assert "pages" in data
        
        print(f"✓ Pagination test - Page {data['page']}, Limit {data['limit']}, Total pages {data['pages']}")


class TestMaterialTransferReceiveAPI:
    """Tests for POST /api/delivery-challans/material-transfer/{challan_id}/receive endpoint"""
    
    def test_receive_material_transfer_invalid_challan_id(self):
        """Test receiving with invalid challan ID returns 404"""
        fake_challan_id = str(uuid.uuid4())
        
        response = requests.post(
            f"{BASE_URL}/api/delivery-challans/material-transfer/{fake_challan_id}/receive",
            json={
                "challan_id": fake_challan_id,
                "received_by": "test_user",
                "received_by_name": "Test User",
                "goods_condition": "good",
                "receiver_remarks": "Test receive"
            }
        )
        
        assert response.status_code == 404, f"Expected 404 for invalid challan, got {response.status_code}"
        print("✓ Invalid challan ID returns 404")
    
    def test_receive_material_transfer_request_structure(self):
        """Test that the receive endpoint accepts correct request structure"""
        # First, get a list of challans to find one that might be receivable
        list_response = requests.get(f"{BASE_URL}/api/delivery-challans/material-transfer/list?status=pending&limit=1")
        
        if list_response.status_code == 200:
            data = list_response.json()
            if data.get("challans") and len(data["challans"]) > 0:
                challan = data["challans"][0]
                challan_id = challan.get("id")
                
                # Try to receive it
                response = requests.post(
                    f"{BASE_URL}/api/delivery-challans/material-transfer/{challan_id}/receive",
                    json={
                        "challan_id": challan_id,
                        "received_by": "test_user_id",
                        "received_by_name": "Test User",
                        "goods_condition": "good",
                        "receiver_remarks": "Goods received in good condition"
                    }
                )
                
                # Should either succeed (200) or fail with business logic error (400)
                # but not with 422 (validation error) or 500 (server error)
                assert response.status_code in [200, 400, 404], f"Unexpected status: {response.status_code}: {response.text}"
                print(f"✓ Receive endpoint accepts correct request structure - Status: {response.status_code}")
            else:
                print("⚠ No pending challans found to test receive - skipping")
                pytest.skip("No pending challans available for testing")
        else:
            print("⚠ Could not fetch challans list - skipping receive test")
            pytest.skip("Could not fetch challans list")


class TestCustomerSearchAPI:
    """Tests for GET /api/customers/search endpoint"""
    
    def test_customer_search_basic(self):
        """Test basic customer search functionality"""
        response = requests.get(f"{BASE_URL}/api/customers/search?q=test&limit=10")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success", f"Expected success status, got: {data}"
        assert "customers" in data, "Response should contain 'customers' key"
        assert isinstance(data["customers"], list), "customers should be a list"
        
        print(f"✓ Customer search for 'test' - Found {len(data['customers'])} customers")
    
    def test_customer_search_by_phone(self):
        """Test customer search by phone number"""
        response = requests.get(f"{BASE_URL}/api/customers/search?q=9876&limit=10")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "success"
        assert "customers" in data
        
        print(f"✓ Customer search by phone '9876' - Found {len(data['customers'])} customers")
    
    def test_customer_search_short_query(self):
        """Test customer search with short query (< 2 chars) returns empty"""
        response = requests.get(f"{BASE_URL}/api/customers/search?q=a&limit=10")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "success"
        # Short queries should return empty list
        assert data.get("customers") == [] or len(data.get("customers", [])) == 0
        
        print("✓ Short query returns empty list as expected")
    
    def test_customer_search_empty_query(self):
        """Test customer search with empty query"""
        response = requests.get(f"{BASE_URL}/api/customers/search?q=&limit=10")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "success"
        assert data.get("customers") == []
        
        print("✓ Empty query returns empty list")
    
    def test_customer_search_with_store_code(self):
        """Test customer search with store_code filter"""
        response = requests.get(f"{BASE_URL}/api/customers/search?q=test&store_code=HRBR&limit=10")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "success"
        assert "customers" in data
        
        print(f"✓ Customer search with store_code=HRBR - Found {len(data['customers'])} customers")
    
    def test_customer_search_response_structure(self):
        """Test that customer search returns proper data structure"""
        response = requests.get(f"{BASE_URL}/api/customers/search?q=john&limit=5")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "success"
        
        # If customers found, verify structure
        if data.get("customers") and len(data["customers"]) > 0:
            customer = data["customers"][0]
            # Check expected fields exist
            expected_fields = ["name", "phone"]
            for field in expected_fields:
                assert field in customer, f"Customer should have '{field}' field"
            print(f"✓ Customer response structure verified - Sample: {customer.get('name')}")
        else:
            print("✓ Customer search response structure valid (no customers found)")


class TestStoreLogin:
    """Tests for store authentication"""
    
    def test_store_manager_login(self):
        """Test store manager can login"""
        response = requests.post(
            f"{BASE_URL}/api/stores/auth/login",
            json={
                "email": STORE_MANAGER_EMAIL,
                "password": STORE_MANAGER_PASSWORD
            }
        )
        
        assert response.status_code == 200, f"Store login failed: {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success" or "token" in data or "user" in data
        
        print(f"✓ Store manager login successful")
        return data


class TestHealthCheck:
    """Basic health check tests"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        
        print("✓ API health check passed")
    
    def test_root_endpoint(self):
        """Test root API endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        print("✓ Root endpoint accessible")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
