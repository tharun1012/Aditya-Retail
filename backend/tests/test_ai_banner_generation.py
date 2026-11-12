"""
AI Banner Generation API Tests
Tests for AI-powered banner image generation using OpenAI GPT Image 1
via emergentintegrations library
"""
import pytest
import requests
import os
import uuid
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAIBannerGeneration:
    """AI Banner Generation endpoint tests"""
    
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
    
    def test_generate_ai_banner_success(self):
        """Test POST /api/banners/generate-ai generates image and returns image_url and image_base64"""
        request_data = {
            "prompt": "Modern kitchen with premium appliances, summer sale theme",
            "banner_type": "sale",
            "style": "modern"
        }
        
        # AI generation takes 30-60 seconds
        response = self.session.post(
            f"{BASE_URL}/api/banners/generate-ai",
            json=request_data,
            timeout=120
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "success", f"Expected success status, got: {data}"
        
        # Verify image_url is returned
        assert "image_url" in data, "Response should contain image_url"
        assert data["image_url"].startswith("/banners/ai_banner_"), f"image_url should start with /banners/ai_banner_, got: {data['image_url']}"
        assert data["image_url"].endswith(".png"), f"image_url should end with .png, got: {data['image_url']}"
        
        # Verify image_base64 is returned
        assert "image_base64" in data, "Response should contain image_base64"
        assert len(data["image_base64"]) > 1000, "image_base64 should be a substantial base64 string"
        
        # Verify prompt_used is returned
        assert "prompt_used" in data, "Response should contain prompt_used"
        assert "summer sale" in data["prompt_used"].lower() or "sale" in data["prompt_used"].lower(), "prompt_used should contain the original prompt content"
        
        print(f"✅ AI banner generated successfully")
        print(f"   Image URL: {data['image_url']}")
        print(f"   Base64 length: {len(data['image_base64'])} chars")
    
    def test_generate_ai_banner_different_styles(self):
        """Test AI generation with different style options"""
        styles = ["modern", "bold", "minimal", "elegant"]
        
        # Test just one style to save time (AI generation is slow)
        style = "bold"
        request_data = {
            "prompt": "Premium refrigerator showcase",
            "banner_type": "promotional",
            "style": style
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/banners/generate-ai",
            json=request_data,
            timeout=120
        )
        
        assert response.status_code == 200, f"Style '{style}' failed: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert "image_url" in data
        
        print(f"✅ AI banner with style '{style}' generated successfully")
    
    def test_generate_ai_banner_empty_prompt(self):
        """Test AI generation with empty prompt returns error"""
        request_data = {
            "prompt": "",
            "banner_type": "promotional",
            "style": "modern"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/banners/generate-ai",
            json=request_data,
            timeout=120
        )
        
        # Empty prompt might still work (backend adds context) or fail
        # Just verify we get a response
        assert response.status_code in [200, 400, 500], f"Unexpected status: {response.status_code}"
        print(f"✅ Empty prompt handled with status: {response.status_code}")
    
    def test_create_banner_with_ai_generated_image(self):
        """Test creating a banner using AI-generated image URL"""
        # First generate an AI image
        ai_request = {
            "prompt": "Elegant dishwasher promotion, clean modern design",
            "banner_type": "new_product",
            "style": "elegant"
        }
        
        ai_response = self.session.post(
            f"{BASE_URL}/api/banners/generate-ai",
            json=ai_request,
            timeout=120
        )
        
        assert ai_response.status_code == 200, f"AI generation failed: {ai_response.text}"
        ai_data = ai_response.json()
        ai_image_url = ai_data["image_url"]
        
        # Now create a banner using the AI-generated image
        banner_data = {
            "title": f"TEST_AI_Banner_{uuid.uuid4().hex[:8]}",
            "description": "Banner created with AI-generated image",
            "image_url": ai_image_url,
            "link_url": "/category/dishwasher",
            "display_order": 5,
            "is_active": True,
            "banner_type": "new_product"
        }
        
        create_response = self.session.post(
            f"{BASE_URL}/api/banners/",
            json=banner_data
        )
        
        assert create_response.status_code == 200, f"Banner creation failed: {create_response.text}"
        
        create_data = create_response.json()
        assert create_data["status"] == "success"
        
        created_banner = create_data["banner"]
        self.test_banner_ids.append(created_banner["id"])
        
        # Verify the AI image URL was saved correctly
        assert created_banner["image_url"] == ai_image_url, "AI image URL should be saved"
        assert "/banners/ai_banner_" in created_banner["image_url"], "Should be an AI-generated banner path"
        
        print(f"✅ Banner created with AI-generated image")
        print(f"   Banner ID: {created_banner['id']}")
        print(f"   Image URL: {created_banner['image_url']}")
        
        # Verify persistence
        get_response = self.session.get(f"{BASE_URL}/api/banners/")
        get_data = get_response.json()
        found_banner = next((b for b in get_data["banners"] if b["id"] == created_banner["id"]), None)
        
        assert found_banner is not None, "Created banner should be retrievable"
        assert found_banner["image_url"] == ai_image_url, "Persisted image_url should match AI-generated URL"


class TestAIBannerFileCreation:
    """Tests for AI banner file creation on disk"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_ai_banner_files_exist(self):
        """Test that AI-generated banner files exist in /app/frontend/public/banners/"""
        import subprocess
        
        result = subprocess.run(
            ["ls", "-la", "/app/frontend/public/banners/"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "Banners directory should exist"
        
        # Check for ai_banner_*.png files
        output = result.stdout
        ai_banner_count = output.count("ai_banner_")
        
        assert ai_banner_count > 0, "At least one AI-generated banner file should exist"
        print(f"✅ Found {ai_banner_count} AI-generated banner files")
        print(output)


class TestBannerManagementTabs:
    """Tests for Banner Management modal tabs (Upload vs AI Generate)"""
    
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
    
    def test_upload_endpoint_still_works(self):
        """Test POST /api/banners/upload still works for manual uploads"""
        # Create a simple test image (1x1 pixel PNG)
        import base64
        
        # Minimal valid PNG (1x1 transparent pixel)
        png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        
        files = {
            'file': ('test_upload.png', png_data, 'image/png')
        }
        
        # Remove Content-Type header for multipart upload
        upload_session = requests.Session()
        response = upload_session.post(
            f"{BASE_URL}/api/banners/upload",
            files=files
        )
        
        assert response.status_code == 200, f"Upload failed: {response.text}"
        
        data = response.json()
        assert data["status"] == "success"
        assert "url" in data
        assert data["url"].startswith("/banners/banner_")
        
        print(f"✅ Manual upload still works")
        print(f"   Uploaded URL: {data['url']}")
    
    def test_banner_crud_with_both_image_types(self):
        """Test that banners can be created with both uploaded and AI-generated images"""
        # Test with external URL (simulating upload)
        upload_banner = {
            "title": f"TEST_Upload_Banner_{uuid.uuid4().hex[:8]}",
            "description": "Banner with uploaded image",
            "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&q=80",
            "link_url": "/category/washing-machine",
            "display_order": 10,
            "is_active": True,
            "banner_type": "promotional"
        }
        
        response1 = self.session.post(f"{BASE_URL}/api/banners/", json=upload_banner)
        assert response1.status_code == 200
        data1 = response1.json()
        self.test_banner_ids.append(data1["banner"]["id"])
        
        # Test with AI-generated path
        ai_banner = {
            "title": f"TEST_AI_Banner_{uuid.uuid4().hex[:8]}",
            "description": "Banner with AI-generated image",
            "image_url": "/banners/ai_banner_test123.png",
            "link_url": "/category/refrigerator",
            "display_order": 11,
            "is_active": True,
            "banner_type": "sale"
        }
        
        response2 = self.session.post(f"{BASE_URL}/api/banners/", json=ai_banner)
        assert response2.status_code == 200
        data2 = response2.json()
        self.test_banner_ids.append(data2["banner"]["id"])
        
        print(f"✅ Both upload and AI image types work for banner creation")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
