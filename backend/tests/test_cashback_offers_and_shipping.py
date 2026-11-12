"""
Backend tests for:
1. Cashback Offers upload flow (Bosch large Excel, small Excel LLM fallback, small PDF LLM)
2. Public/admin cashback offer endpoints (list, product, delete)
3. Shipping endpoints (cod-charges, serviceability)

Run:
  pytest /app/backend/tests/test_cashback_offers_and_shipping.py -v \
    --junitxml=/app/test_reports/pytest/pytest_cashback_offers.xml
"""
import os
import io
import time
import pytest
import requests
from typing import Optional
from dotenv import load_dotenv

# Frontend env holds REACT_APP_BACKEND_URL (public URL). Backend env may not.
load_dotenv("/app/frontend/.env")
load_dotenv("/app/backend/.env")

_BASE = os.environ.get("REACT_APP_BACKEND_URL")
assert _BASE, "REACT_APP_BACKEND_URL must be set in frontend/.env"
BASE_URL = _BASE.rstrip("/")
BOSCH_URL = ("https://customer-assets.emergentagent.com/job_2d674e41-b40c-4b0d-80ff-5713a6c78b21/"
             "artifacts/bj5a7stu_BOSCH%20CASH%20BACK%20OFFERS.xlsx")
BOSCH_LOCAL = "/tmp/bosch_cashback.xlsx"


# --------------------- Fixtures ---------------------
@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    return s


@pytest.fixture(scope="session")
def bosch_file_path():
    """Download the real Bosch cashback Excel file once."""
    if not os.path.exists(BOSCH_LOCAL) or os.path.getsize(BOSCH_LOCAL) < 1000:
        r = requests.get(BOSCH_URL, timeout=60)
        assert r.status_code == 200, f"Failed to download Bosch file: {r.status_code}"
        with open(BOSCH_LOCAL, "wb") as f:
            f.write(r.content)
    assert os.path.getsize(BOSCH_LOCAL) > 1000
    return BOSCH_LOCAL


@pytest.fixture(scope="session")
def small_excel_path():
    """Build a small 4-row Excel file that should force LLM fallback (no SKU column)."""
    import openpyxl
    path = "/tmp/small_offers.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Offers"
    ws.append(["Offer Title", "Description", "Bank", "Amount"])
    ws.append(["Flat Rs 2000 Cashback", "Get flat Rs 2000 cashback on all Bosch refrigerators above Rs 40000",
               "HDFC", 2000])
    ws.append(["10% Bank Discount", "10% instant discount with ICICI credit cards on Bosch washing machines",
               "ICICI", 10])
    ws.append(["No Cost EMI", "6 months no cost EMI available on Bosch appliances",
               "Any Bank", 0])
    ws.append(["Exchange Bonus", "Additional Rs 3000 exchange bonus on old refrigerator exchange",
               "", 3000])
    wb.save(path)
    return path


@pytest.fixture(scope="session")
def small_pdf_path():
    """Build a small PDF with 2-3 offers."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    path = "/tmp/small_offers.pdf"
    c = canvas.Canvas(path, pagesize=A4)
    c.drawString(100, 800, "Bosch Cashback Offers - Test PDF")
    c.drawString(100, 770, "1. Flat Rs 5000 cashback on Bosch refrigerators above Rs 50000 - HDFC Bank")
    c.drawString(100, 750, "2. 10% instant discount on Bosch washing machines with ICICI credit cards")
    c.drawString(100, 730, "3. No cost EMI for 6 months on Bosch dishwashers with Axis Bank")
    c.save()
    return path


@pytest.fixture(scope="session")
def uploaded_bosch(api, bosch_file_path):
    """Upload Bosch file once; used by multiple tests."""
    with open(bosch_file_path, "rb") as f:
        files = {"file": (os.path.basename(bosch_file_path), f,
                          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        data = {"brand": "Bosch"}
        t0 = time.time()
        resp = api.post(f"{BASE_URL}/api/offers/admin/upload-pdf", files=files, data=data, timeout=90)
        elapsed = time.time() - t0
    return {"resp": resp, "elapsed": elapsed}


# --------------------- 1. Bosch large Excel upload (bug fix) ---------------------
class TestBoschLargeExcelUpload:
    def test_bosch_upload_completes_fast_and_returns_200(self, uploaded_bosch):
        resp = uploaded_bosch["resp"]
        elapsed = uploaded_bosch["elapsed"]
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text[:300]}"
        assert elapsed < 30, f"Upload took {elapsed:.2f}s (must be <30s to avoid Cloudflare timeout)"
        print(f"Bosch upload elapsed={elapsed:.2f}s")

    def test_bosch_upload_extracts_offers(self, uploaded_bosch):
        data = uploaded_bosch["resp"].json()
        assert data["status"] == "success"
        assert data["offers_extracted"] > 300, (
            f"Expected >300 offers, got {data['offers_extracted']}"
        )
        print(f"Extracted {data['offers_extracted']} offers")

    def test_bosch_upload_response_size_capped(self, uploaded_bosch):
        # Response must not include all 400+ offers - only first 10 preview
        resp = uploaded_bosch["resp"]
        size_kb = len(resp.content) / 1024
        assert size_kb < 500, f"Response too large: {size_kb:.1f} KB (should be truncated preview)"
        data = resp.json()
        assert len(data.get("offers", [])) <= 10, (
            f"Preview should be <=10 offers, got {len(data.get('offers', []))}"
        )

    def test_bosch_offers_matched_to_products(self, uploaded_bosch):
        data = uploaded_bosch["resp"].json()
        # Not a hard failure if catalog doesn't contain matching SKUs, but must exist
        assert "offers_matched_to_products" in data
        print(f"Offers matched: {data['offers_matched_to_products']}")

    def test_bosch_preview_offer_shape(self, uploaded_bosch):
        data = uploaded_bosch["resp"].json()
        assert isinstance(data["offers"], list) and len(data["offers"]) > 0
        first = data["offers"][0]
        # Basic schema
        for k in ("id", "offer_type", "title", "brand"):
            assert k in first, f"Missing key {k} in offer: {first}"
        assert "bosch" in first["brand"].lower(), f"Brand not Bosch-related: {first['brand']}"
        # Row-based offer must have sku
        assert first.get("sku"), "Row-based offer should carry SKU"


# --------------------- 2. Small Excel LLM fallback ---------------------
class TestSmallExcelLLMFallback:
    def test_small_excel_extract(self, api, small_excel_path):
        with open(small_excel_path, "rb") as f:
            files = {"file": ("small_offers.xlsx", f,
                              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            data = {"brand": "Bosch"}
            resp = api.post(f"{BASE_URL}/api/offers/admin/upload-pdf",
                            files=files, data=data, timeout=120)
        assert resp.status_code == 200, f"{resp.status_code}: {resp.text[:400]}"
        body = resp.json()
        assert body["status"] == "success"
        # LLM should extract ~4 offers (allow 2-8 tolerance)
        assert body["offers_extracted"] >= 2, f"Expected >=2 offers, got {body['offers_extracted']}"
        # Brand hint should be applied to at least one offer
        brands = [o.get("brand", "") for o in body.get("offers", [])]
        assert any(b and b.lower() == "bosch" for b in brands), f"No offer preserved 'Bosch' brand: {brands}"


# --------------------- 3. Small PDF LLM extraction ---------------------
class TestSmallPDFExtraction:
    def test_small_pdf_extract(self, api, small_pdf_path):
        with open(small_pdf_path, "rb") as f:
            files = {"file": ("small_offers.pdf", f, "application/pdf")}
            data = {"brand": "Bosch"}
            resp = api.post(f"{BASE_URL}/api/offers/admin/upload-pdf",
                            files=files, data=data, timeout=120)
        assert resp.status_code == 200, f"{resp.status_code}: {resp.text[:400]}"
        body = resp.json()
        assert body["status"] == "success"
        assert body["offers_extracted"] >= 1, "PDF LLM path should extract at least one offer"
        # Type must be one of allowed
        types = {o.get("offer_type") for o in body.get("offers", [])}
        valid = {"cashback", "bank_offer", "no_cost_emi", "partner_offer", "exchange_offer"}
        assert types.issubset(valid), f"Bad offer_type values: {types}"


# --------------------- 4. Admin list ---------------------
class TestAdminListAndProductAndDelete:
    def test_admin_list_returns_offers(self, api, uploaded_bosch):
        # Ensure at least Bosch upload happened
        assert uploaded_bosch["resp"].status_code == 200
        resp = api.get(f"{BASE_URL}/api/offers/admin/list", timeout=30)
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert isinstance(body["offers"], list)
        assert body["count"] >= 1
        # No _id should leak
        for o in body["offers"][:20]:
            assert "_id" not in o

    def test_offers_for_bosch_product(self, api, uploaded_bosch):
        """Find a Bosch product and verify its offers endpoint returns something,
        preferably including SKU-matched offers with whatsapp_message set."""
        # Fetch admin list, find any offer with product_ids
        list_resp = api.get(f"{BASE_URL}/api/offers/admin/list?brand=Bosch", timeout=30)
        assert list_resp.status_code == 200
        offers = list_resp.json().get("offers", [])
        product_id: Optional[str] = None
        for o in offers:
            if o.get("product_ids"):
                product_id = o["product_ids"][0]
                break
        if not product_id:
            # Fallback: pick any Bosch product from catalog
            p_resp = api.get(f"{BASE_URL}/api/products?brand=Bosch", timeout=30)
            if p_resp.status_code == 200:
                prods = p_resp.json()
                # products endpoint may return list or {products: [...]}
                if isinstance(prods, dict):
                    prods = prods.get("products") or prods.get("items") or []
                if prods:
                    product_id = prods[0].get("id")
        if not product_id:
            pytest.skip("No Bosch product available to test /offers/product/{id}")

        po_resp = api.get(f"{BASE_URL}/api/offers/product/{product_id}", timeout=30)
        assert po_resp.status_code == 200
        body = po_resp.json()
        assert body["status"] == "success"
        assert isinstance(body["offers"], list)
        # If offers returned, verify whatsapp_message is present
        for o in body["offers"]:
            assert o.get("whatsapp_message"), "whatsapp_message must be set on public offer"
            assert "wa.me/" in o["whatsapp_message"]
            assert "_id" not in o

    def test_delete_offer(self, api):
        # Grab any existing offer to delete
        list_resp = api.get(f"{BASE_URL}/api/offers/admin/list", timeout=30)
        offers = list_resp.json().get("offers", [])
        if not offers:
            pytest.skip("No offer available to delete")
        offer_id = offers[0]["id"]
        del_resp = api.delete(f"{BASE_URL}/api/offers/admin/{offer_id}", timeout=30)
        assert del_resp.status_code == 200
        assert del_resp.json()["status"] == "success"
        # Verify gone
        del_again = api.delete(f"{BASE_URL}/api/offers/admin/{offer_id}", timeout=30)
        assert del_again.status_code == 404


# --------------------- 5. Shipping ---------------------
class TestShipping:
    def test_cod_charges_delhi(self, api):
        payload = {"delivery_pincode": "110001", "order_value": 25000, "weight": 10}
        resp = api.post(f"{BASE_URL}/api/shipping/cod-charges", json=payload, timeout=45)
        assert resp.status_code == 200, f"{resp.status_code}: {resp.text[:300]}"
        body = resp.json()
        assert body["status"] == "success"
        assert body.get("cod_available") is True
        assert body.get("cod_charges", 0) > 0, f"cod_charges should be >0: {body}"

    def test_serviceability_invalid_pincode(self, api):
        payload = {"delivery_pincode": "999999", "weight": 5, "cod": 1}
        resp = api.post(f"{BASE_URL}/api/shipping/serviceability", json=payload, timeout=45)
        assert resp.status_code == 200
        body = resp.json()
        # Either serviceable=False or status=error, or fallback (manual)
        if body.get("status") == "error":
            return
        # Accept fallback path (manual calc). Only fail if serviceable=True without fallback
        if body.get("serviceable") is True and not body.get("fallback"):
            pytest.fail(f"Expected non-serviceable/fallback/error for 999999: {body}")

    def test_serviceability_valid_pincode_mumbai(self, api):
        payload = {"delivery_pincode": "400001", "weight": 5, "cod": 1}
        resp = api.post(f"{BASE_URL}/api/shipping/serviceability", json=payload, timeout=45)
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert body.get("serviceable") is True
        assert body.get("recommended", {}).get("rate", 0) > 0
