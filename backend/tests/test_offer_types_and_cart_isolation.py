"""Iteration 13 tests:
- Cart offer SKU isolation: POST /api/offers/cart should NOT leak SKU-specific offers for other Bosch products
- New offer types accepted: seasonal_offer, upi_offer via /api/offers/admin/create
- Bosch PDP with a brand-wide seasonal_offer shows it alongside SKU-specific offer
- Cleanup any test offers created
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


@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# Track offers we create so we always cleanup, even on failures
_CREATED_OFFERS: list[str] = []


@pytest.fixture(scope="session", autouse=True)
def _cleanup_after_run(api):
    yield
    for oid in list(_CREATED_OFFERS):
        try:
            api.delete(f"{BASE_URL}/api/offers/admin/{oid}", timeout=15)
        except Exception:
            pass


# --- Baseline PDP regression check ---
class TestPDPRegression:
    def test_bosch_kgn56lb42i_has_sku_offer_baseline(self, api):
        r = api.get(f"{BASE_URL}/api/offers/product/{BOSCH_PID}", timeout=30)
        assert r.status_code == 200, r.text
        offers = r.json().get("offers", [])
        assert len(offers) >= 1, f"Expected >=1 offer baseline, got {len(offers)}"
        # Store baseline count for later comparison
        TestPDPRegression.baseline_count = len(offers)


# --- Cart SKU isolation ---
class TestCartOfferIsolation:
    def test_cart_with_bosch_product_returns_bosch_offers_only(self, api):
        """Cart with a Bosch product should return offers where (a) product is in offer's product_ids
        OR (b) the offer has no SKU (truly brand-wide). SKU-specific offers for OTHER Bosch products
        must NOT leak in."""
        r = api.post(f"{BASE_URL}/api/offers/cart",
                     json={"product_ids": [BOSCH_PID]}, timeout=30)
        assert r.status_code == 200, r.text
        body = r.json()
        offers = body.get("offers", [])
        count = body.get("count", 0)
        print(f"Cart offers count for single Bosch product: {count}")
        # It should not blow up to 442
        assert count < 100, f"Cart should not return all Bosch offers ({count})"
        # Verify each returned offer is either (a) SKU-matched for BOSCH_PID or (b) non-SKU brand/category-wide
        for o in offers:
            pids = o.get("product_ids") or []
            sku = o.get("sku")
            if BOSCH_PID in pids:
                continue  # SKU-scoped to our cart product - fine
            # Otherwise must be truly brand-wide (no sku set) AND either no product_ids or empty
            assert not sku, (
                f"Offer {o.get('id')} has sku='{sku}' but is not in cart product_ids "
                f"({pids}) — SKU leakage detected"
            )
            assert not pids, (
                f"Offer {o.get('id')} has non-cart product_ids {pids} — cross-SKU leakage"
            )

    def test_cart_offers_align_with_pdp_offers(self, api):
        """Cart offers for a single Bosch product should be a superset (or roughly equal) of
        PDP offers for the same product. (Same isolation logic.)"""
        pdp = api.get(f"{BASE_URL}/api/offers/product/{BOSCH_PID}", timeout=30).json().get("offers", [])
        cart = api.post(f"{BASE_URL}/api/offers/cart",
                        json={"product_ids": [BOSCH_PID]}, timeout=30).json().get("offers", [])
        pdp_ids = {o["id"] for o in pdp}
        cart_ids = {o["id"] for o in cart}
        # PDP offers should be subset of cart offers (both apply same brand/cat/SKU logic).
        missing = pdp_ids - cart_ids
        assert not missing, f"PDP offers missing from cart: {missing}"

    def test_cart_empty_returns_empty(self, api):
        r = api.post(f"{BASE_URL}/api/offers/cart", json={"product_ids": []}, timeout=15)
        assert r.status_code == 200
        assert r.json().get("offers") == []


# --- New offer types acceptance ---
class TestNewOfferTypes:
    def test_create_seasonal_offer(self, api):
        payload = {
            "offer_type": "seasonal_offer",
            "title": "TEST Monsoon Combo Offer + 1yr warranty",
            "brand": "Bosch",
            "categories": ["Refrigerator"],
            "amount_upto": 3000,
            "amount_type": "flat",
            "redeem_location": "offline_store",
        }
        r = api.post(f"{BASE_URL}/api/offers/admin/create", json=payload, timeout=30)
        assert r.status_code == 200, r.text
        offer = r.json().get("offer")
        assert offer and offer.get("id")
        assert offer["offer_type"] == "seasonal_offer"
        assert offer["title"] == payload["title"]
        _CREATED_OFFERS.append(offer["id"])
        TestNewOfferTypes.seasonal_id = offer["id"]

        # Round-trip via admin/list to verify persisted with correct type
        lst = api.get(f"{BASE_URL}/api/offers/admin/list", timeout=15).json().get("offers", [])
        found = next((o for o in lst if o.get("id") == offer["id"]), None)
        assert found is not None, "Seasonal offer not returned by admin/list"
        assert found["offer_type"] == "seasonal_offer"

    def test_create_upi_offer(self, api):
        payload = {
            "offer_type": "upi_offer",
            "title": "TEST UPI Rs 500 cashback",
            "valid_bank": "GooglePay, PhonePe, Paytm",
            "redeem_location": "online",
            "amount_upto": 500,
            "amount_type": "flat",
        }
        r = api.post(f"{BASE_URL}/api/offers/admin/create", json=payload, timeout=30)
        assert r.status_code == 200, r.text
        offer = r.json().get("offer")
        assert offer and offer.get("id")
        assert offer["offer_type"] == "upi_offer"
        assert offer["title"] == payload["title"]
        _CREATED_OFFERS.append(offer["id"])

        lst = api.get(f"{BASE_URL}/api/offers/admin/list", timeout=15).json().get("offers", [])
        found = next((o for o in lst if o.get("id") == offer["id"]), None)
        assert found is not None
        assert found["offer_type"] == "upi_offer"

    def test_bosch_pdp_now_shows_seasonal_offer(self, api):
        assert getattr(TestNewOfferTypes, "seasonal_id", None), "must create seasonal first"
        r = api.get(f"{BASE_URL}/api/offers/product/{BOSCH_PID}", timeout=30)
        assert r.status_code == 200
        offers = r.json().get("offers", [])
        types = [o.get("offer_type") for o in offers]
        assert "seasonal_offer" in types, f"seasonal_offer missing from PDP offers: {types}"
        # And SKU-specific offer(s) still present alongside
        assert len(offers) >= 2, f"Expected PDP to show SKU + brand-wide seasonal, got {len(offers)}"

    def test_cart_shows_new_brand_wide_seasonal(self, api):
        """After creating brand-wide seasonal_offer, cart with Bosch product should include it."""
        r = api.post(f"{BASE_URL}/api/offers/cart",
                     json={"product_ids": [BOSCH_PID]}, timeout=30)
        assert r.status_code == 200
        types = [o.get("offer_type") for o in r.json().get("offers", [])]
        assert "seasonal_offer" in types, f"seasonal_offer missing from cart: {types}"


# --- Regression: total offers preserved (~442 Bosch offers minus tests) ---
class TestTotalOffersPreserved:
    def test_total_offers_count(self, api):
        r = api.get(f"{BASE_URL}/api/offers/admin/list", timeout=30)
        assert r.status_code == 200
        count = r.json().get("count", 0)
        # 442 + our 2 test offers = 444 during test; allow small variance
        assert count >= 440, f"Expected >=440 offers, got {count}"


# --- Cleanup step (also runs from autouse fixture) ---
class TestZZZCleanup:
    def test_delete_created_offers(self, api):
        for oid in list(_CREATED_OFFERS):
            r = api.delete(f"{BASE_URL}/api/offers/admin/{oid}", timeout=15)
            assert r.status_code == 200, f"delete failed for {oid}: {r.text}"
            _CREATED_OFFERS.remove(oid)
