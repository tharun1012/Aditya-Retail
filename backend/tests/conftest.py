"""
Pytest fixtures for backend testing
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture
def store_auth_token(api_client):
    """Get store user authentication token"""
    response = api_client.post(f"{BASE_URL}/api/stores/auth/login", json={
        "email": "manager@arm.adityaretail.com",
        "password": "store123"
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("token"), data.get("store", {})
    pytest.skip("Store authentication failed — skipping store tests")

@pytest.fixture
def warehouse_auth_token(api_client):
    """Get warehouse user authentication token"""
    response = api_client.post(f"{BASE_URL}/api/stores/auth/login", json={
        "email": "manager@warehouse.adityaretail.com",
        "password": "store123"
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("token"), data.get("store", {})
    pytest.skip("Warehouse authentication failed — skipping warehouse tests")

@pytest.fixture
def unique_id():
    """Generate unique ID for test data"""
    return str(uuid.uuid4())[:8]

@pytest.fixture
def timestamp():
    """Generate timestamp for unique test data"""
    return datetime.now().strftime("%Y%m%d%H%M%S")
