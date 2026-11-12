"""
Test SEO Product URL Structure (short-slug + legacy backward compat)
- GET /api/product/by-slug/{category}/{slug} -> matches slug or legacy_slug
- GET /api/product-slugs/status -> reports migration state
"""
import os
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestShortSlugProductLookup:
    """Verify the new short-slug (excludes brand) resolves to correct product"""

    def test_wga254zpin_short_slug_resolves(self):
        url = f"{BASE_URL}/api/product/by-slug/washing-machine/wga254zpin-10kg-front-load-washing-machine"
        r = requests.get(url, timeout=30)
        assert r.status_code == 200, f"{url} -> {r.status_code} {r.text[:200]}"
        data = r.json()
        assert data.get("status") == "success"
        p = data.get("product") or {}
        # Slug and short_title fields must exist
        assert p.get("slug") == "wga254zpin-10kg-front-load-washing-machine", f"slug mismatch: {p.get('slug')}"
        assert p.get("short_title"), f"short_title missing: {p}"
        assert "WGA254ZPIN" in (p.get("model_number") or "").upper()
        assert "Bosch" in (p.get("brand") or "")

    def test_short_title_content_bosch_wga254zpin(self):
        url = f"{BASE_URL}/api/product/by-slug/washing-machine/wga254zpin-10kg-front-load-washing-machine"
        r = requests.get(url, timeout=30)
        assert r.status_code == 200
        p = r.json().get("product") or {}
        short_title = p.get("short_title") or ""
        # Reasonable check — should be short-form Bosch title, not full marketing string
        assert "Bosch" in short_title
        assert "WGA254ZPIN" in short_title.upper() or "WGA254" in short_title.upper()


class TestLegacySlugBackwardCompat:
    """Verify old long slugs still resolve via legacy_slug field"""

    def test_cmc36k03gi_legacy_slug_resolves(self):
        legacy = ("bosch-cmc36k03gi-series-4-free-standing-fridge-freezer-with-freezer-at-top-"
                  "187-x-67-cm-335l-3-star-smoky-silver-3-door")
        url = f"{BASE_URL}/api/product/by-slug/refrigerator/{legacy}"
        r = requests.get(url, timeout=30)
        assert r.status_code == 200, f"legacy slug should resolve: {r.status_code} {r.text[:200]}"
        data = r.json()
        assert data.get("status") == "success"
        p = data.get("product") or {}
        assert "CMC36K03GI" in (p.get("model_number") or "").upper()
        assert "Bosch" in (p.get("brand") or "")

    def test_dib098g50i_legacy_slug_resolves(self):
        legacy = "bosch-dib098g50i-series-4-island-cooker-hood-90-cm"
        url = f"{BASE_URL}/api/product/by-slug/chimney/{legacy}"
        r = requests.get(url, timeout=30)
        assert r.status_code == 200, f"legacy DIB098G50I slug should resolve: {r.status_code} {r.text[:200]}"
        p = r.json().get("product") or {}
        assert "DIB098G50I" in (p.get("model_number") or "").upper()


class TestMigrationStatus:
    """Verify /api/product-slugs/status returns completed state"""

    def test_status_completed(self):
        url = f"{BASE_URL}/api/product-slugs/status"
        r = requests.get(url, timeout=30)
        assert r.status_code == 200, f"status endpoint: {r.status_code} {r.text[:200]}"
        data = r.json()
        # Accept either 'state' or 'status' key — but per playbook it should be 'state'
        state = data.get("state") or data.get("status")
        assert state == "completed", f"Expected state=completed, got: {data}"


class TestNotFoundStillReturns404:
    """Sanity: a truly-unknown slug returns 404 (not 500)"""

    def test_nonexistent_slug_404(self):
        url = f"{BASE_URL}/api/product/by-slug/washing-machine/definitely-not-a-real-slug-xyz-123"
        r = requests.get(url, timeout=30)
        assert r.status_code == 404
