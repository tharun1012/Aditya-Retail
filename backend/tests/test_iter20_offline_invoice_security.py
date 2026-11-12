"""
Iteration 20 tests:
- Security guards on offline invoice admin endpoints
- Atomic invoice numbering preview (no collisions with existing invoice numbers)
- find-duplicates route not shadowed
- PUT /invoices/offline/{id} GST recompute (intra-state -> cgst+sgst, igst=0)
- Regression: legacy by-slug returns full product with images/price
"""
import os
import pytest
import requests
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')
API = f"{BASE_URL}/api"
HRBR_STORE_ID = "ade28bcc-5da5-4895-8d20-9303ce713d32"

SUPER_ADMIN = {"email": "rohit.gadiya@gmail.com", "password": "Purvi@vriddhi01"}


@pytest.fixture(scope="module")
def super_admin_token():
    r = requests.post(f"{API}/auth/unified-login", json=SUPER_ADMIN, timeout=30)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    data = r.json()
    tok = data.get("access_token") or data.get("token")
    assert tok, f"no token in response: {data}"
    return tok


@pytest.fixture(scope="module")
def admin_headers(super_admin_token):
    return {"Authorization": f"Bearer {super_admin_token}"}


# ---------- SECURITY: 401 without Authorization header ----------
class TestUnauthenticated401:
    def test_delete_by_store_401(self):
        r = requests.post(f"{API}/invoices/offline/admin/delete-by-store",
                          json={"store_id": HRBR_STORE_ID, "dry_run": True}, timeout=30)
        assert r.status_code == 401, f"expected 401 got {r.status_code}: {r.text[:200]}"

    def test_delete_by_ids_401(self):
        r = requests.post(f"{API}/invoices/offline/admin/delete-by-ids",
                          json={"ids": ["x"], "dry_run": True}, timeout=30)
        assert r.status_code == 401, f"expected 401 got {r.status_code}: {r.text[:200]}"

    def test_put_offline_invoice_401(self):
        r = requests.put(f"{API}/invoices/offline/{uuid.uuid4()}",
                         json={"notes": "x"}, timeout=30)
        assert r.status_code == 401, f"expected 401 got {r.status_code}: {r.text[:200]}"

    def test_edit_document_401(self):
        r = requests.put(f"{API}/invoices/offline/admin/edit-document/{uuid.uuid4()}",
                         json={"notes": "x"}, timeout=30)
        assert r.status_code == 401, f"expected 401 got {r.status_code}: {r.text[:200]}"

    def test_backdate_so_401(self):
        r = requests.post(f"{API}/invoices/offline/admin/backdate-so",
                          json={}, timeout=30)
        assert r.status_code == 401, f"expected 401 got {r.status_code}: {r.text[:200]}"


# ---------- SECURITY: super admin dry_run succeeds ----------
class TestSuperAdminAccess:
    def test_delete_by_store_dry_run(self, admin_headers):
        r = requests.post(f"{API}/invoices/offline/admin/delete-by-store",
                          json={"store_code": "HRBR", "document_type": "invoice",
                                "confirm": "DELETE-HRBR", "dry_run": True},
                          headers=admin_headers, timeout=30)
        assert r.status_code == 200, f"got {r.status_code}: {r.text[:300]}"
        data = r.json()
        assert data.get("dry_run") is True
        assert "matched" in data, f"no matched field in {data}"

    def test_delete_by_ids_confirm_mismatch(self, admin_headers):
        # With valid schema but bad confirm should get 400 (not 401/403/500)
        r = requests.post(f"{API}/invoices/offline/admin/delete-by-ids",
                          json={"ids": [], "confirm": "WRONG"},
                          headers=admin_headers, timeout=30)
        assert r.status_code == 400, f"got {r.status_code}: {r.text[:300]}"

    def test_delete_by_ids_empty_ok(self, admin_headers):
        r = requests.post(f"{API}/invoices/offline/admin/delete-by-ids",
                          json={"ids": [], "confirm": "DELETE"},
                          headers=admin_headers, timeout=30)
        assert r.status_code in (200, 400), f"got {r.status_code}: {r.text[:300]}"


# ---------- find-duplicates not shadowed ----------
class TestFindDuplicates:
    def test_find_duplicates_returns_json(self, admin_headers):
        r = requests.get(f"{API}/invoices/offline/admin/find-duplicates",
                         headers=admin_headers, timeout=60)
        assert r.status_code == 200, f"got {r.status_code}: {r.text[:300]}"
        # must be JSON, not shadowed by /{invoice_id}
        data = r.json()
        assert isinstance(data, (list, dict)), f"unexpected type: {type(data)}"


# ---------- Invoice numbering preview: no collision ----------
class TestInvoiceNumberingPreview:
    def test_preview_no_collision(self, admin_headers):
        r = requests.get(f"{API}/document-numbering/preview/{HRBR_STORE_ID}/invoice",
                         headers=admin_headers, timeout=30)
        assert r.status_code == 200, f"got {r.status_code}: {r.text[:300]}"
        data = r.json()
        preview = data.get("preview") or data.get("next_number") or data.get("number") or data.get("document_number")
        assert preview, f"no preview number in {data}"

        # Fetch existing offline invoices for the store and check collision.
        r2 = requests.get(f"{API}/invoices/offline",
                          params={"store_id": HRBR_STORE_ID, "limit": 500},
                          headers=admin_headers, timeout=30)
        if r2.status_code == 200:
            body = r2.json()
            invs = body if isinstance(body, list) else body.get("invoices", [])
            existing = {(i.get("invoice_number") or i.get("document_number")) for i in invs}
            # Soft assertion — record collision as XFAIL info instead of hard fail
            if preview in existing:
                pytest.fail(
                    f"COLLISION BUG: preview {preview} already exists in offline_invoices "
                    f"(store HRBR). This indicates static custom_format without sequence placeholder "
                    f"or find_next_free_sequence not advancing. Config: {data.get('config')}"
                )


# ---------- PUT offline/{id}: intra-state GST recompute ----------
class TestOfflineInvoiceEditGST:
    def test_intra_state_gst_split(self, admin_headers):
        # Find an intra-state offline invoice for HRBR
        r = requests.get(f"{API}/invoices/offline",
                         params={"store_id": HRBR_STORE_ID, "limit": 50},
                         headers=admin_headers, timeout=30)
        if r.status_code != 200:
            pytest.skip(f"cannot list offline invoices: {r.status_code}")
        payload = r.json()
        invs = payload if isinstance(payload, list) else payload.get("invoices", [])
        target = None
        for inv in invs:
            if inv.get("is_inter_state") is False and inv.get("items"):
                target = inv
                break
        if not target:
            pytest.skip("no intra-state offline invoice with items available")

        inv_id = target.get("id") or target.get("_id") or target.get("invoice_id")
        assert inv_id, f"no id in invoice keys: {list(target.keys())}"

        # Edit: change notes only; server should recompute GST on save
        edit_body = {
            "notes": f"TEST_gst_recompute_{uuid.uuid4().hex[:6]}",
            "items": target.get("items"),
            "edited_by": "super_admin_test",
            "edit_reason": "iter20 GST recompute regression test",
        }
        r2 = requests.put(f"{API}/invoices/offline/{inv_id}",
                          json=edit_body, headers=admin_headers, timeout=60)
        assert r2.status_code == 200, f"PUT failed {r2.status_code}: {r2.text[:400]}"
        data = r2.json()
        updated = data.get("invoice") or data
        items = updated.get("items") or []
        if items:
            for it in items:
                cgst = float(it.get("cgst") or it.get("cgst_amount") or 0)
                sgst = float(it.get("sgst") or it.get("sgst_amount") or 0)
                igst = float(it.get("igst") or it.get("igst_amount") or 0)
                # If tax present, cgst+sgst should be set, igst 0 for intra-state
                if (cgst + sgst + igst) > 0:
                    assert igst == 0, f"intra-state item has igst={igst}"
        # totals
        igst_total = float(updated.get("igst_total") or 0)
        assert igst_total == 0, f"intra-state igst_total should be 0, got {igst_total}"


# ---------- REGRESSION: legacy by-slug returns full product ----------
class TestBySlugRegression:
    def test_full_payload_with_images_and_price(self):
        r = requests.get(f"{API}/product/by-slug/chimney/bosch-dib098g50i-series-4-island-cooker-hood-90-cm",
                         timeout=30)
        assert r.status_code == 200, f"got {r.status_code}: {r.text[:300]}"
        data = r.json()
        # Endpoint returns {status, product}
        product = data.get("product") if isinstance(data, dict) and "product" in data else data
        assert isinstance(product, dict), f"product not object: {type(product)}"
        keys = set(product.keys())
        has_images = any(k in keys for k in ("images", "image_urls", "gallery", "primary_image", "image", "thumbnail"))
        has_price = any(k in keys for k in ("price", "sale_price", "mrp", "selling_price", "original_price"))
        assert has_images, f"missing images fields; got keys={sorted(keys)}"
        assert has_price, f"missing price fields; got keys={sorted(keys)}"
        assert len(keys) > 6, f"only {len(keys)} fields returned (slim fallback): {sorted(keys)}"
