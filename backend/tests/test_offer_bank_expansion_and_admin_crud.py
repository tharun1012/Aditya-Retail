"""Tests for iteration 12:
- Bank name expansion in _serialize_public (All Banks -> friendly bank list)
- Admin POST /api/offers/admin/create supports extended_warranty
- Brand-wide extended_warranty appears on Bosch PDP (SKU + brand-wide fallback)
- Admin PUT /api/offers/admin/{id} accepts terms, is_active, offer_type
- Regression: total Bosch offers should still be ~442
"""
import os
import pytest
import requests
from pathlib import Path


def _load_backend_url():
    val = os.environ.get("REACT_APP_BACKEND_URL")
    if val:
        return val.rstrip("/")
    env_path = Path("/app/frontend/.env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("REACT_APP_BACKEND_URL"):
                return line.split("=", 1)[1].strip().rstrip("/")
    raise RuntimeError("REACT_APP_BACKEND_URL not set")


BASE_URL = _load_backend_url()
BOSCH_PID = "15b0268c-226e-4544-9b0a-204688f8ce3c"  # Bosch KGN56LB42I

DEFAULT_BANKS_FRAGMENTS = ["HDFC", "ICICI", "Axis", "SBI", "Kotak"]


@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# --- Bank name expansion ---
class TestBankExpansion:
    def test_bosch_kgn56lb42i_bank_list_expanded(self, api):
        r = api.get(f"{BASE_URL}/api/offers/product/{BOSCH_PID}", timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        offers = data.get("offers", [])
        assert len(offers) >= 1, "Expected at least 1 offer for Bosch KGN56LB42I"
        # There should be an SKU-level offer with valid_bank expanded
        sku_offer = next((o for o in offers if o.get("sku") == "KGN56LB42I" or o.get("sku")), offers[0])
        vb = sku_offer.get("valid_bank") or ""
        assert vb.lower() not in ("all banks", "all bank", "any bank", ""), (
            f"valid_bank should be expanded, got: {vb!r}"
        )
        # Should contain typical banks
        for frag in DEFAULT_BANKS_FRAGMENTS:
            assert frag in vb, f"Missing bank {frag} in {vb!r}"


# --- Extended warranty create / brand-wide fallback / cleanup ---
class TestExtendedWarrantyCRUD:
    created_id = None

    def test_create_extended_warranty(self, api):
        payload = {
            "offer_type": "extended_warranty",
            "title": "TEST 3-year Extended Warranty",
            "amount_upto": 5000,
            "amount_type": "flat",
            "brand": "Bosch",
            "categories": ["Refrigerator"],
            "terms": "Compressor+PCB+Motor coverage",
            "redeem_location": "offline_store",
            "valid_bank": "Available at store",
        }
        r = api.post(f"{BASE_URL}/api/offers/admin/create", json=payload, timeout=30)
        assert r.status_code == 200, r.text
        body = r.json()
        offer = body.get("offer")
        assert offer and offer.get("id"), "Response missing offer.id"
        assert offer["offer_type"] == "extended_warranty"
        assert offer["title"] == payload["title"]
        assert offer.get("whatsapp_message"), "whatsapp_message should be auto-generated"
        TestExtendedWarrantyCRUD.created_id = offer["id"]

    def test_bosch_pdp_now_shows_two_offers(self, api):
        assert TestExtendedWarrantyCRUD.created_id, "prev test must have created warranty"
        r = api.get(f"{BASE_URL}/api/offers/product/{BOSCH_PID}", timeout=30)
        assert r.status_code == 200, r.text
        offers = r.json().get("offers", [])
        types = [o.get("offer_type") for o in offers]
        assert "extended_warranty" in types, f"Expected extended_warranty in offers, got {types}"
        assert len(offers) >= 2, f"Expected >=2 offers (SKU + warranty), got {len(offers)}"

    def test_update_offer_terms_and_deactivate(self, api):
        oid = TestExtendedWarrantyCRUD.created_id
        assert oid
        r = api.put(
            f"{BASE_URL}/api/offers/admin/{oid}",
            json={"terms": "Updated terms", "is_active": False},
            timeout=30,
        )
        assert r.status_code == 200, r.text
        offer = r.json().get("offer")
        assert offer["terms"] == "Updated terms"
        assert offer["is_active"] is False

        # Verify via admin list (public endpoint filters by is_active)
        r2 = api.get(f"{BASE_URL}/api/offers/admin/list", timeout=30)
        assert r2.status_code == 200
        found = next((o for o in r2.json().get("offers", []) if o.get("id") == oid), None)
        assert found is not None
        assert found["terms"] == "Updated terms"
        assert found["is_active"] is False

    def test_update_accepts_offer_type_field(self, api):
        """Regression: OfferUpdate now supports offer_type."""
        oid = TestExtendedWarrantyCRUD.created_id
        assert oid
        r = api.put(
            f"{BASE_URL}/api/offers/admin/{oid}",
            json={"offer_type": "partner_offer"},
            timeout=30,
        )
        assert r.status_code == 200, r.text
        assert r.json()["offer"]["offer_type"] == "partner_offer"
        # revert back to extended_warranty for cleanliness
        api.put(f"{BASE_URL}/api/offers/admin/{oid}", json={"offer_type": "extended_warranty"}, timeout=30)

    def test_zzz_cleanup_delete_offer(self, api):
        oid = TestExtendedWarrantyCRUD.created_id
        if not oid:
            pytest.skip("no offer created")
        r = api.delete(f"{BASE_URL}/api/offers/admin/{oid}", timeout=30)
        assert r.status_code == 200, r.text


# --- Regression: total offers preserved (~442 Bosch offers) ---
class TestRegression:
    def test_total_offers_count(self, api):
        r = api.get(f"{BASE_URL}/api/offers/admin/list", timeout=30)
        assert r.status_code == 200
        # After cleanup our test offer is gone; expected 442 Bosch offers still there
        count = r.json().get("count", 0)
        assert count >= 400, f"Expected >=400 offers preserved, got {count}"
