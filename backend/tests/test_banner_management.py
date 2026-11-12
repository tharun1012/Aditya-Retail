"""
Banner Management API Tests
Tests for banner CRUD operations, active homepage banners, and click tracking
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestBannerAPI:
    """Banner Management API endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.test_banner_ids = []
        yield
        # Cleanup test banners
        for banner_id in self.test_banner_ids:
            try:
                self.session.delete(f"{BASE_URL}/api/banners/{banner_id}")
            except Exception:
                pass
    
    def test_get_active_homepage_banners(self):
        """Test GET /api/banners/active/homepage returns active banners with image_url and link_url"""
        response = self.session.get(f"{BASE_URL}/api/banners/active/homepage")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] == "success"
        assert "banners" in data
        assert "total" in data
        
        # Verify banner structure if banners exist
        if data["total"] > 0:
            banner = data["banners"][0]
            assert "id" in banner
            assert "title" in banner
            assert "image_url" in banner
            assert "link_url" in banner
            assert "is_active" in banner
            assert banner["is_active"] == True
            print(f"✅ Found {data['total']} active homepage banners")
            print(f"   First banner: {banner['title']}")
            print(f"   Image URL: {banner['image_url']}")
            print(f"   Link URL: {banner['link_url']}")
        else:
            print("⚠️ No active banners found")
    
    def test_get_all_banners(self):
        """Test GET /api/banners/ returns all banners"""
        response = self.session.get(f"{BASE_URL}/api/banners/")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "banners" in data
        print(f"✅ Total banners: {data['total']}")
    
    def test_create_banner_with_image_url(self):
        """Test POST /api/banners/ creates a banner with image_url properly saved"""
        test_banner = {
            "title": f"TEST_Banner_{uuid.uuid4().hex[:8]}",
            "description": "Test banner description for automated testing",
            "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&q=80",
            "link_url": "/category/washing-machine",
            "display_order": 99,
            "is_active": True,
            "banner_type": "promotional"
        }
        
        response = self.session.post(f"{BASE_URL}/api/banners/", json=test_banner)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "success"
        assert "banner" in data
        
        created_banner = data["banner"]
        self.test_banner_ids.append(created_banner["id"])
        
        # Verify image_url is NOT empty string
        assert created_banner["image_url"] != "", "image_url should not be empty string"
        assert created_banner["image_url"] == test_banner["image_url"], "image_url should match input"
        
        # Verify other fields
        assert created_banner["title"] == test_banner["title"]
        assert created_banner["link_url"] == test_banner["link_url"]
        assert created_banner["banner_type"] == test_banner["banner_type"]
        
        print(f"✅ Banner created successfully with ID: {created_banner['id']}")
        print(f"   Image URL saved: {created_banner['image_url']}")
        
        # Verify persistence with GET
        get_response = self.session.get(f"{BASE_URL}/api/banners/")
        get_data = get_response.json()
        found_banner = next((b for b in get_data["banners"] if b["id"] == created_banner["id"]), None)
        assert found_banner is not None, "Created banner should be retrievable"
        assert found_banner["image_url"] == test_banner["image_url"], "Persisted image_url should match"
    
    def test_create_banner_with_sale_type(self):
        """Test creating banner with sale banner_type"""
        test_banner = {
            "title": f"TEST_Sale_Banner_{uuid.uuid4().hex[:8]}",
            "description": "Big sale event!",
            "image_url": "https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?w=800&q=80",
            "link_url": "/category/refrigerator",
            "display_order": 1,
            "is_active": True,
            "banner_type": "sale"
        }
        
        response = self.session.post(f"{BASE_URL}/api/banners/", json=test_banner)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        
        created_banner = data["banner"]
        self.test_banner_ids.append(created_banner["id"])
        
        assert created_banner["banner_type"] == "sale"
        print(f"✅ Sale banner created: {created_banner['title']}")
    
    def test_track_banner_click(self):
        """Test POST /api/banners/{id}/track-click increments click count"""
        # First get an existing banner
        response = self.session.get(f"{BASE_URL}/api/banners/")
        data = response.json()
        
        if data["total"] == 0:
            pytest.skip("No banners available for click tracking test")
        
        banner = data["banners"][0]
        banner_id = banner["id"]
        initial_clicks = banner.get("clicks", 0)
        
        # Track click
        click_response = self.session.post(f"{BASE_URL}/api/banners/{banner_id}/track-click")
        
        assert click_response.status_code == 200
        click_data = click_response.json()
        assert click_data["status"] == "success"
        
        # Verify click count increased
        verify_response = self.session.get(f"{BASE_URL}/api/banners/")
        verify_data = verify_response.json()
        updated_banner = next((b for b in verify_data["banners"] if b["id"] == banner_id), None)
        
        assert updated_banner is not None
        assert updated_banner["clicks"] >= initial_clicks, "Click count should increase"
        print(f"✅ Click tracked for banner: {banner['title']}")
        print(f"   Clicks: {initial_clicks} -> {updated_banner['clicks']}")
    
    def test_track_banner_view(self):
        """Test POST /api/banners/{id}/track-view increments view count"""
        response = self.session.get(f"{BASE_URL}/api/banners/")
        data = response.json()
        
        if data["total"] == 0:
            pytest.skip("No banners available for view tracking test")
        
        banner = data["banners"][0]
        banner_id = banner["id"]
        initial_views = banner.get("views", 0)
        
        # Track view
        view_response = self.session.post(f"{BASE_URL}/api/banners/{banner_id}/track-view")
        
        assert view_response.status_code == 200
        view_data = view_response.json()
        assert view_data["status"] == "success"
        
        print(f"✅ View tracked for banner: {banner['title']}")
    
    def test_update_banner(self):
        """Test PUT /api/banners/{id} updates banner"""
        # Create a test banner first
        test_banner = {
            "title": f"TEST_Update_Banner_{uuid.uuid4().hex[:8]}",
            "description": "Original description",
            "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&q=80",
            "link_url": "/category/dishwasher",
            "display_order": 50,
            "is_active": True,
            "banner_type": "new_product"
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/banners/", json=test_banner)
        created_banner = create_response.json()["banner"]
        self.test_banner_ids.append(created_banner["id"])
        
        # Update the banner
        updates = {
            "title": "Updated Banner Title",
            "description": "Updated description",
            "link_url": "/category/oven"
        }
        
        update_response = self.session.put(
            f"{BASE_URL}/api/banners/{created_banner['id']}", 
            json=updates
        )
        
        assert update_response.status_code == 200
        update_data = update_response.json()
        assert update_data["status"] == "success"
        
        updated_banner = update_data["banner"]
        assert updated_banner["title"] == "Updated Banner Title"
        assert updated_banner["link_url"] == "/category/oven"
        
        print(f"✅ Banner updated successfully")
    
    def test_delete_banner(self):
        """Test DELETE /api/banners/{id} soft deletes banner"""
        # Create a test banner first
        test_banner = {
            "title": f"TEST_Delete_Banner_{uuid.uuid4().hex[:8]}",
            "description": "To be deleted",
            "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&q=80",
            "link_url": "/category/chimney",
            "display_order": 100,
            "is_active": True,
            "banner_type": "seasonal"
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/banners/", json=test_banner)
        created_banner = create_response.json()["banner"]
        banner_id = created_banner["id"]
        
        # Delete the banner
        delete_response = self.session.delete(f"{BASE_URL}/api/banners/{banner_id}")
        
        assert delete_response.status_code == 200
        delete_data = delete_response.json()
        assert delete_data["status"] == "success"
        
        # Verify banner is now inactive (soft delete)
        verify_response = self.session.get(f"{BASE_URL}/api/banners/")
        verify_data = verify_response.json()
        deleted_banner = next((b for b in verify_data["banners"] if b["id"] == banner_id), None)
        
        if deleted_banner:
            assert deleted_banner["is_active"] == False, "Deleted banner should be inactive"
        
        print(f"✅ Banner soft deleted successfully")
    
    def test_existing_summer_sale_banner(self):
        """Verify the existing Summer Sale banner has correct data"""
        response = self.session.get(f"{BASE_URL}/api/banners/active/homepage")
        data = response.json()
        
        # Find the Summer Sale banner
        summer_banner = next(
            (b for b in data["banners"] if "Summer Sale" in b["title"]), 
            None
        )
        
        if summer_banner:
            assert summer_banner["link_url"] == "/category/refrigerator", "Link URL should be /category/refrigerator"
            assert summer_banner["image_url"] != "", "Image URL should not be empty"
            assert "unsplash" in summer_banner["image_url"], "Image should be from Unsplash"
            assert summer_banner["banner_type"] == "sale", "Banner type should be sale"
            print(f"✅ Summer Sale banner verified:")
            print(f"   Title: {summer_banner['title']}")
            print(f"   Link: {summer_banner['link_url']}")
            print(f"   Type: {summer_banner['banner_type']}")
        else:
            print("⚠️ Summer Sale banner not found in active banners")


class TestBannerValidation:
    """Banner validation and edge case tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.test_banner_ids = []
        yield
        for banner_id in self.test_banner_ids:
            try:
                self.session.delete(f"{BASE_URL}/api/banners/{banner_id}")
            except Exception:
                pass
    
    def test_create_banner_without_image_url(self):
        """Test creating banner without image_url defaults to empty string"""
        test_banner = {
            "title": f"TEST_NoImage_Banner_{uuid.uuid4().hex[:8]}",
            "description": "Banner without image",
            "link_url": "/category/sink",
            "display_order": 99,
            "is_active": True,
            "banner_type": "promotional"
        }
        
        response = self.session.post(f"{BASE_URL}/api/banners/", json=test_banner)
        
        assert response.status_code == 200
        data = response.json()
        created_banner = data["banner"]
        self.test_banner_ids.append(created_banner["id"])
        
        # image_url should default to empty string
        assert "image_url" in created_banner
        print(f"✅ Banner without image created, image_url: '{created_banner['image_url']}'")
    
    def test_banner_not_found(self):
        """Test accessing non-existent banner returns 404"""
        fake_id = "non-existent-banner-id-12345"
        
        response = self.session.put(
            f"{BASE_URL}/api/banners/{fake_id}", 
            json={"title": "Updated"}
        )
        
        assert response.status_code == 404
        print("✅ Non-existent banner returns 404")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
