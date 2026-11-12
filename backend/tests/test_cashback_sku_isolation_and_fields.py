"""
Backend tests — Iteration 10 (SKU isolation + field extraction bug fix).

Validates the two Bosch cashback bugs fixed in
/app/backend/cashback_offers_routes.py:

1. SKU-specific offer isolation: GET /api/offers/product/{product_id}
   returns EXACTLY the SKU-matched offer(s) — not every Bosch offer.
2. Field extraction: valid_bank contains bank names (e.g. "All Banks"),
   NOT EMI terms text. `terms` and `tenure` fields are populated correctly.

Regression:
3. Non-Bosch product returns 0 offers (no leakage).
4. Brand-wide manual offer still shows up on Bosch products.
5. Upload time <10s.
6. LLM fallback still works on small Excel.

Run:
  pytest /app/backend/tests/test_cashback_sku_isolation_and_fields.py -v \
    --junitxml=/app/test_reports/pytest/pytest_cashback_iter10.xml
"""
import os
import time
import pytest
import requests
import pymongo
from dotenv import load_dotenv

load_dotenv("/app/frontend/.env")
load_dotenv("/app/backend/.env")

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ.get("DB_NAME", "startup_template")

BOSCH_URL = (
    "https://customer-assets.emergentagent.com/job_2d674e41-b40c-4b0d-80ff-5713a6c78b21/"
    "artifacts/bj5a7stu_BOSCH%20CASH%20BACK%20OFFERS.xlsx"
)
BOSCH_LOCAL = "/tmp/bosch_cashback.xlsx"


# --------------------- Fixtures ---------------------
@pytest.fixture(scope="session")
def mongo_db():
    c = pymongo.MongoClient(MONGO_URL)
    return c[DB_NAME]


@pytest.fixture(scope="session")
def api():
    return requests.Session()


@pytest.fixture(scope="session")
def bosch_file_path():
    if not os.path.exists(BOSCH_LOCAL) or os.path.getsize(BOSCH_LOCAL) < 1000:
        r = requests.get(BOSCH_URL, timeout=60)
        assert r.status_code == 200, f"Failed download: {r.status_code}"
        with open(BOSCH_LOCAL, "wb") as f:
            f.write(r.content)
    return BOSCH_LOCAL


@pytest.fixture(scope="session")
def clean_and_upload_bosch(api, bosch_file_path, mongo_db):
    """Drop cashback_offers collection then upload the Bosch Excel. Session-scoped."""
    mongo_db.cashback_offers.drop()
    with open(bosch_file_path, "rb") as f:
        files = {"file": (os.path.basename(bosch_file_path), f,
                          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        data = {"brand": "Bosch"}
        t0 = time.time()
        resp = api.post(f"{BASE_URL}/api/offers/admin/upload-pdf",
                        files=files, data=data, timeout=90)
        elapsed = time.time() - t0
    assert resp.status_code == 200, f"Upload failed: {resp.status_code}: {resp.text[:400]}"
    return {"resp": resp, "elapsed": elapsed, "body": resp.json()}


# --------------------- Bug fix 1: SKU-specific isolation ---------------------
class TestSKUIsolation:
    def test_upload_completed(self, clean_and_upload_bosch):
        body = clean_and_upload_bosch["body"]
        assert body["status"] == "success"
        assert body["offers_extracted"] > 300, (
            f"expected >300 offers, got {body['offers_extracted']}"
        )
        print(f"Extracted {body['offers_extracted']} offers; matched="
              f"{body.get('offers_matched_to_products')}; "
              f"elapsed={clean_and_upload_bosch['elapsed']:.2f}s")

    def test_upload_under_10_seconds(self, clean_and_upload_bosch):
        elapsed = clean_and_upload_bosch["elapsed"]
        assert elapsed < 10, f"Row-based extraction too slow: {elapsed:.2f}s"

    def test_sku_matched_offer_returns_exactly_that_offer(
        self, clean_and_upload_bosch, mongo_db, api
    ):
        """Pick any SKU-matched offer (has sku + product_ids). GET
        /api/offers/product/{product_id} must return EXACTLY that offer's SKU
        (not all Bosch offers on the same brand/category)."""
        # Find an offer that has a SKU AND product_ids populated
        offer = mongo_db.cashback_offers.find_one({
            "sku": {"$ne": None, "$exists": True},
            "product_ids.0": {"$exists": True},
        })
        if not offer:
            pytest.skip("No SKU-matched offer found — nothing to isolate")
        product_id = offer["product_ids"][0]
        target_sku = offer["sku"]

        resp = api.get(f"{BASE_URL}/api/offers/product/{product_id}", timeout=30)
        assert resp.status_code == 200, resp.text[:300]
        body = resp.json()
        offers = body["offers"]
        assert body["status"] == "success"

        # Only offers with this exact SKU (or brand-wide with no sku) should appear.
        # Since we uploaded ONLY Bosch SKU-level file (no manual brand-wide),
        # the count should equal the number of offers whose sku == target_sku
        # AND product_ids includes product_id.
        skus_returned = [o.get("sku") for o in offers]
        print(f"product_id={product_id} target_sku={target_sku} returned={len(offers)} "
              f"skus={skus_returned}")

        # Every returned offer must EITHER have sku==target_sku OR be a brand-wide
        # (sku is None AND product_ids empty).
        for o in offers:
            osku = o.get("sku")
            pids = o.get("product_ids") or []
            if osku:
                assert osku == target_sku, (
                    f"Leaked offer with sku={osku} on product {product_id} "
                    f"(expected only sku={target_sku})"
                )
            else:
                assert not pids, (
                    f"Offer with no sku but non-empty product_ids leaked: {o}"
                )

        # Assert count == 1 for the pure SKU case (no other offers targeting this product)
        assert len(offers) >= 1
        assert len(offers) == 1, (
            f"Expected exactly 1 SKU-matched offer for {product_id}, got {len(offers)}: "
            f"{skus_returned}"
        )

    def test_no_sku_offer_leakage_via_brand_fallback(
        self, clean_and_upload_bosch, mongo_db, api
    ):
        """Offers that have a SKU but their SKU didn't match any product in
        catalog (product_ids == []) MUST NOT leak to other products via
        brand/category fallback."""
        # Find such an offer (has sku, empty product_ids)
        orphan = mongo_db.cashback_offers.find_one({
            "sku": {"$ne": None, "$exists": True},
            "$or": [{"product_ids": {"$exists": False}}, {"product_ids": {"$size": 0}}],
        })
        if not orphan:
            pytest.skip("No orphan SKU offer exists — nothing to verify")
        orphan_sku = orphan["sku"]
        orphan_brand = orphan.get("brand")
        orphan_cats = orphan.get("categories") or []
        print(f"Orphan offer sku={orphan_sku} brand={orphan_brand} categories={orphan_cats}")

        # Pick any Bosch product from catalog (a product that WILL be queried
        # by brand+category and might trigger the bug).
        q = {"brand": {"$regex": "^Bosch$", "$options": "i"}}
        if orphan_cats:
            q["category"] = {"$regex": f"^{orphan_cats[0]}$", "$options": "i"}
        prod = mongo_db.products.find_one(q)
        if not prod:
            pytest.skip("No Bosch product in catalog for regression check")
        pid = prod["id"]
        resp = api.get(f"{BASE_URL}/api/offers/product/{pid}", timeout=30)
        assert resp.status_code == 200
        body = resp.json()
        returned_skus = [o.get("sku") for o in body["offers"]]
        # Orphan SKU must NOT appear (unless the pid is actually inside its product_ids)
        assert orphan_sku not in [s for s in returned_skus if s != prod.get("model_number")], (
            f"Orphan SKU {orphan_sku} leaked into product {pid}: {returned_skus}"
        )


# --------------------- Bug fix 2: Correct field extraction ---------------------
class TestFieldExtraction:
    def test_valid_bank_is_bank_name_not_emi_text(self, clean_and_upload_bosch, mongo_db):
        """`valid_bank` must be a bank name from legend row, not EMI text."""
        sample = list(mongo_db.cashback_offers.find(
            {"sku": {"$ne": None}}, {"_id": 0}
        ).limit(20))
        assert sample, "No offers to inspect"

        # None of them should have EMI-terms text in valid_bank
        emi_markers = ["ncemi", "emi", "months", "3 months", "6 months", "2.5%"]
        for o in sample:
            vb = (o.get("valid_bank") or "").lower()
            for m in emi_markers:
                assert m not in vb, (
                    f"valid_bank contains EMI text '{m}': {o.get('valid_bank')!r} in offer {o.get('id')}"
                )

        # At least one offer should have a real bank hint like "all banks" or a bank name
        valid_banks = [o.get("valid_bank") for o in sample if o.get("valid_bank")]
        assert valid_banks, "valid_bank empty in all sampled offers"
        joined = " | ".join(str(v).lower() for v in valid_banks)
        assert any(k in joined for k in ["all banks", "hdfc", "icici", "sbi", "axis", "bank"]), (
            f"No recognizable bank name in valid_bank: {valid_banks[:5]}"
        )
        print(f"valid_bank samples: {valid_banks[:5]}")

    def test_terms_field_contains_emi_text(self, clean_and_upload_bosch, mongo_db):
        """`terms` field should carry the EMI/remarks description (or be null)."""
        # Find any offer that has terms set
        offer = mongo_db.cashback_offers.find_one({"terms": {"$ne": None, "$exists": True}})
        if not offer:
            pytest.skip("No offer has terms field populated (may be blank in Excel)")
        terms = offer["terms"]
        assert isinstance(terms, str) and len(terms.strip()) > 0
        print(f"terms sample: {terms[:200]!r}")

    def test_tenure_field_present(self, clean_and_upload_bosch, mongo_db):
        offer = mongo_db.cashback_offers.find_one({"tenure": {"$ne": None, "$exists": True}})
        if not offer:
            pytest.skip("No offer has tenure field populated")
        ten = offer["tenure"]
        assert isinstance(ten, str) and ten.strip()
        print(f"tenure sample: {ten!r}")

    def test_public_endpoint_exposes_new_fields(self, clean_and_upload_bosch, mongo_db, api):
        """`terms` and `tenure` should be returned in the public product-offers response."""
        offer = mongo_db.cashback_offers.find_one({
            "product_ids.0": {"$exists": True},
            "sku": {"$ne": None},
        })
        if not offer:
            pytest.skip("No SKU-matched offer to check public payload")
        pid = offer["product_ids"][0]
        resp = api.get(f"{BASE_URL}/api/offers/product/{pid}", timeout=30)
        assert resp.status_code == 200
        offers = resp.json()["offers"]
        assert offers, "No offers returned for the SKU-matched product"
        # At least one of the standard schema fields should be present
        o0 = offers[0]
        for k in ("valid_bank", "terms", "tenure"):
            assert k in o0, f"Missing field {k} in public offer payload: {list(o0.keys())}"
        assert "_id" not in o0


# --------------------- Regression: non-Bosch product ---------------------
class TestNonBoschRegression:
    def test_non_bosch_product_returns_zero_offers(self, clean_and_upload_bosch, mongo_db, api):
        """A product from another brand should NOT return any Bosch offer."""
        prod = mongo_db.products.find_one({
            "brand": {"$not": {"$regex": "^Bosch$", "$options": "i"}, "$exists": True},
            "id": {"$exists": True},
        })
        if not prod:
            pytest.skip("No non-Bosch product in catalog")
        pid = prod["id"]
        resp = api.get(f"{BASE_URL}/api/offers/product/{pid}", timeout=30)
        assert resp.status_code == 200
        body = resp.json()
        # All Bosch offers should be filtered out
        assert body["count"] == 0, (
            f"Non-Bosch product {pid} ({prod.get('brand')}) returned "
            f"{body['count']} offers: {[o.get('sku') for o in body['offers']]}"
        )


# --------------------- Regression: brand-wide manual offer ---------------------
class TestBrandWideManualOffer:
    def test_brand_wide_offer_shows_on_bosch_products(
        self, clean_and_upload_bosch, mongo_db, api
    ):
        """POST /api/offers/admin/create with no sku + empty product_ids +
        brand=Bosch — must appear on ANY Bosch refrigerator product."""
        payload = {
            "offer_type": "cashback",
            "title": "TEST_Brand_Wide_Bosch_Refrigerator_Offer",
            "description": "Flat Rs 999 off on all Bosch refrigerators (test)",
            "amount_upto": 999,
            "amount_type": "flat",
            "brand": "Bosch",
            "categories": ["Refrigerator"],
            "product_ids": [],
            # NOTE: sku is intentionally omitted so it's None
        }
        r = api.post(f"{BASE_URL}/api/offers/admin/create", json=payload, timeout=30)
        assert r.status_code == 200, r.text[:400]
        created_id = r.json()["offer"]["id"]

        try:
            # Find any Bosch refrigerator
            prod = mongo_db.products.find_one({
                "brand": {"$regex": "^Bosch$", "$options": "i"},
                "category": {"$regex": "^Refrigerator$", "$options": "i"},
            })
            if not prod:
                pytest.skip("No Bosch refrigerator in catalog")
            pid = prod["id"]

            resp = api.get(f"{BASE_URL}/api/offers/product/{pid}", timeout=30)
            assert resp.status_code == 200
            titles = [o.get("title") for o in resp.json()["offers"]]
            assert any("TEST_Brand_Wide_Bosch_Refrigerator_Offer" in t for t in titles), (
                f"Brand-wide offer missing on Bosch refrigerator {pid}. titles={titles}"
            )
        finally:
            api.delete(f"{BASE_URL}/api/offers/admin/{created_id}", timeout=30)


# --------------------- Regression: LLM fallback still works ---------------------
class TestSmallExcelLLMFallback:
    @pytest.fixture(scope="class")
    def small_excel_path(self):
        import openpyxl
        path = "/tmp/small_offers_iter10.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Offers"
        ws.append(["Offer Title", "Description", "Bank", "Amount"])
        ws.append(["Flat Rs 2000 Cashback",
                   "Get flat Rs 2000 cashback on all Bosch refrigerators above Rs 40000",
                   "HDFC", 2000])
        ws.append(["10% Bank Discount",
                   "10% instant discount with ICICI credit cards on Bosch washing machines",
                   "ICICI", 10])
        ws.append(["No Cost EMI",
                   "6 months no cost EMI available on Bosch appliances",
                   "Any Bank", 0])
        wb.save(path)
        return path

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
        assert body["offers_extracted"] >= 2, (
            f"Expected >=2 offers from LLM, got {body['offers_extracted']}"
        )
        brands = [o.get("brand", "") for o in body.get("offers", [])]
        assert any(b and b.lower() == "bosch" for b in brands), (
            f"No offer preserved 'Bosch' brand hint: {brands}"
        )
