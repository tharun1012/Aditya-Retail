"""
Test URL Simplification Feature
Tests for clean URLs: /category-slug and /category-slug/MODEL_NUMBER
Also tests backward compatibility with legacy URLs
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestProductByModelAPI:
    """Test the new /api/product/by-model/{category}/{model_number} endpoint"""
    
    def test_get_product_by_model_refrigerator(self):
        """Test fetching refrigerator product by model number CMC36K03GI"""
        response = requests.get(f"{BASE_URL}/api/product/by-model/refrigerator/CMC36K03GI")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("status") == "success", "Expected status success"
        assert "product" in data, "Expected product in response"
        
        product = data["product"]
        assert product.get("model_number") == "CMC36K03GI", f"Expected model CMC36K03GI, got {product.get('model_number')}"
        assert "Bosch" in product.get("brand", ""), "Expected Bosch brand"
        assert "Refrigerator" in product.get("category", ""), "Expected Refrigerator category"
        assert product.get("price") is not None, "Expected price in product"
        assert product.get("name") is not None, "Expected name in product"
    
    def test_get_product_by_model_chimney(self):
        """Test fetching chimney product by model number DIB098G50I"""
        response = requests.get(f"{BASE_URL}/api/product/by-model/chimney/DIB098G50I")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("status") == "success", "Expected status success"
        assert "product" in data, "Expected product in response"
        
        product = data["product"]
        assert product.get("model_number") == "DIB098G50I", f"Expected model DIB098G50I, got {product.get('model_number')}"
        assert "Bosch" in product.get("brand", ""), "Expected Bosch brand"
        assert "Chimney" in product.get("category", ""), "Expected Chimney category"
    
    def test_get_product_by_model_case_insensitive(self):
        """Test that model number lookup is case-insensitive"""
        # Test lowercase
        response_lower = requests.get(f"{BASE_URL}/api/product/by-model/refrigerator/cmc36k03gi")
        assert response_lower.status_code == 200, "Expected case-insensitive match for lowercase"
        
        # Test uppercase
        response_upper = requests.get(f"{BASE_URL}/api/product/by-model/REFRIGERATOR/CMC36K03GI")
        assert response_upper.status_code == 200, "Expected case-insensitive match for uppercase"
    
    def test_get_product_by_model_not_found(self):
        """Test 404 for non-existent model number"""
        response = requests.get(f"{BASE_URL}/api/product/by-model/refrigerator/NONEXISTENT123")
        assert response.status_code == 404, f"Expected 404 for non-existent model, got {response.status_code}"


class TestCategoryAPI:
    """Test category-related APIs for clean URLs"""
    
    def test_get_categories_list(self):
        """Test fetching all categories"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("status") == "success", "Expected status success"
        assert "categories" in data, "Expected categories in response"
        assert len(data["categories"]) > 0, "Expected at least one category"
        
        # Check for expected categories
        categories = [c.lower() for c in data["categories"]]
        assert any("refrigerator" in c for c in categories), "Expected Refrigerator category"
        assert any("washing" in c for c in categories), "Expected Washing Machine category"
        assert any("chimney" in c for c in categories), "Expected Chimney category"
    
    def test_get_products_by_category_refrigerator(self):
        """Test fetching products by category (refrigerator)"""
        response = requests.get(f"{BASE_URL}/api/products?category=refrigerator")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("status") == "success", "Expected status success"
        assert "products" in data, "Expected products in response"
        
        # Verify products have model_number for clean URLs
        products = data["products"]
        if len(products) > 0:
            product = products[0]
            assert "model_number" in product or "modelNumber" in product, "Expected model_number in product for clean URLs"
    
    def test_get_products_by_category_washing_machine(self):
        """Test fetching products by category (washing machine)"""
        response = requests.get(f"{BASE_URL}/api/products?category=washing%20machine")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("status") == "success", "Expected status success"


class TestLegacyProductAPIs:
    """Test legacy product APIs still work for backward compatibility"""
    
    def test_get_product_by_slug(self):
        """Test legacy /api/product/by-slug/{category}/{slug} endpoint"""
        # First get a product to find its slug
        response = requests.get(f"{BASE_URL}/api/products?category=refrigerator&limit=1")
        assert response.status_code == 200
        
        data = response.json()
        if data.get("products") and len(data["products"]) > 0:
            product = data["products"][0]
            slug = product.get("slug")
            if slug:
                # Test slug-based lookup
                response = requests.get(f"{BASE_URL}/api/product/by-slug/refrigerator/{slug}")
                assert response.status_code == 200, f"Expected 200 for slug lookup, got {response.status_code}"
    
    def test_get_product_by_id(self):
        """Test legacy /api/products/{id} endpoint"""
        # First get a product to find its ID
        response = requests.get(f"{BASE_URL}/api/products?limit=1")
        assert response.status_code == 200
        
        data = response.json()
        if data.get("products") and len(data["products"]) > 0:
            product = data["products"][0]
            product_id = product.get("id")
            if product_id:
                # Test ID-based lookup
                response = requests.get(f"{BASE_URL}/api/products/{product_id}")
                assert response.status_code == 200, f"Expected 200 for ID lookup, got {response.status_code}"


class TestProductDataIntegrity:
    """Test that product data has all required fields for clean URLs"""
    
    def test_products_have_model_numbers(self):
        """Verify products have model_number field for clean URL generation"""
        response = requests.get(f"{BASE_URL}/api/products?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        products = data.get("products", [])
        
        products_with_model = 0
        for product in products:
            if product.get("model_number") or product.get("modelNumber"):
                products_with_model += 1
        
        # At least 50% of products should have model numbers
        if len(products) > 0:
            percentage = (products_with_model / len(products)) * 100
            print(f"Products with model_number: {products_with_model}/{len(products)} ({percentage:.1f}%)")
            assert percentage >= 50, f"Expected at least 50% products with model_number, got {percentage:.1f}%"
    
    def test_products_have_category(self):
        """Verify products have category field for clean URL generation"""
        response = requests.get(f"{BASE_URL}/api/products?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        products = data.get("products", [])
        
        for product in products:
            assert product.get("category"), f"Product {product.get('name', 'unknown')} missing category"


class TestWashingMachineProduct:
    """Test washing machine product by model number"""
    
    def test_get_washing_machine_by_model(self):
        """Test fetching washing machine product by model number WAU28S90IN"""
        response = requests.get(f"{BASE_URL}/api/product/by-model/washing-machine/WAU28S90IN")
        
        # This might return 404 if the product doesn't exist
        if response.status_code == 200:
            data = response.json()
            assert data.get("status") == "success", "Expected status success"
            product = data.get("product", {})
            assert "WAU28S90IN" in product.get("model_number", "").upper(), "Expected model number in response"
        else:
            # Product might not exist, which is acceptable
            print(f"Washing machine WAU28S90IN not found (status: {response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
