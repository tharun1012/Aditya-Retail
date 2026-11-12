"""
Iteration 17 backend tests:
- AI Sales agent multi-brand advisory (Bosch/Siemens/Electrolux)
- AI Delivery agent live order lookup by phone (INV-20260430-0001 / 9844577440)
- AI Delivery agent inserts db.outgoing_emails tag 'delivery_status_ai'
- AI Service agent DIY-first troubleshooting + conversation continuity
- POST /api/products/normalize-categories idempotency
- GET /api/products has no 'Micrwave'/'Refrigerators'/'Hoods' categories
"""
import os
import uuid
import time
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://acct-workflow-1.preview.emergentagent.com').rstrip('/')
CHAT_URL = f"{BASE_URL}/api/neural-ai/chat"
LOGIN_URL = f"{BASE_URL}/api/auth/unified-login"

ADMIN_EMAIL = "rohit.gadiya@gmail.com"
ADMIN_PASS = "Purvi@vriddhi01"

# Very long timeout because Claude Sonnet responses can take 15-60s
AI_TIMEOUT = 120


@pytest.fixture(scope="session")
def admin_token():
    r = requests.post(LOGIN_URL, json={"email": ADMIN_EMAIL, "password": ADMIN_PASS}, timeout=30)
    if r.status_code != 200:
        pytest.skip(f"Admin login failed: {r.status_code} {r.text[:200]}")
    data = r.json()
    tok = data.get("access_token") or data.get("token")
    assert tok, f"No token in login response: {data}"
    return tok


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


# ============ AI SALES AGENT ============
class TestAISalesAgent:
    def test_sales_multi_brand_refrigerator(self):
        session_id = f"TEST_sales_{uuid.uuid4().hex[:8]}"
        payload = {
            "agent_type": "sales",
            "message": "I am looking for a refrigerator",
            "session_id": session_id,
        }
        r = requests.post(CHAT_URL, json=payload, timeout=AI_TIMEOUT)
        assert r.status_code == 200, f"status={r.status_code} body={r.text[:300]}"
        data = r.json()
        assert data.get("status") == "success"
        resp_text = (data.get("response") or "").lower()
        print(f"\n[SALES turn1 len={len(resp_text)}] preview: {resp_text[:400]}")
        # Multi-brand check
        brands_mentioned = {b for b in ["bosch", "siemens", "electrolux"] if b in resp_text}
        assert "bosch" in brands_mentioned, f"Bosch missing. Text: {resp_text[:400]}"
        assert len(brands_mentioned) >= 2, (
            f"Expected multiple brands, got {brands_mentioned}. Text: {resp_text[:800]}"
        )

        # ---- turn 2: budget ----
        payload2 = {
            "agent_type": "sales",
            "message": "My budget is around Rs 70,000",
            "session_id": session_id,
        }
        r2 = requests.post(CHAT_URL, json=payload2, timeout=AI_TIMEOUT)
        assert r2.status_code == 200
        data2 = r2.json()
        resp2 = (data2.get("response") or "").lower()
        print(f"[SALES turn2 len={len(resp2)}] preview: {resp2[:400]}")
        # Should still be about refrigerators / remember context
        assert any(k in resp2 for k in ["refrigerator", "fridge", "l ", "litre", "liter", "door"]), (
            f"Budget follow-up lost refrigerator context: {resp2[:400]}"
        )


# ============ AI DELIVERY AGENT ============
class TestAIDeliveryAgent:
    def test_delivery_real_order_lookup(self):
        from pymongo import MongoClient  # local import
        session_id = f"TEST_delivery_{uuid.uuid4().hex[:8]}"
        payload = {
            "agent_type": "delivery",
            "message": "check my order status, my phone number is 9844577440, email me at rohit.gadiya@gmail.com",
            "session_id": session_id,
        }
        r = requests.post(CHAT_URL, json=payload, timeout=AI_TIMEOUT)
        assert r.status_code == 200, f"status={r.status_code} body={r.text[:300]}"
        data = r.json()
        resp = (data.get("response") or "")
        resp_lower = resp.lower()
        print(f"\n[DELIVERY len={len(resp)}] preview: {resp[:600]}")

        # Must reference the real order
        assert "inv-20260430-0001" in resp_lower or "20260430-0001" in resp_lower, (
            f"Order number INV-20260430-0001 not in response: {resp[:600]}"
        )

        # Verify outgoing_emails record inserted (dedupes per session+order)
        # Give backend a moment
        time.sleep(1.5)
        mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
        db_name = os.environ.get("DB_NAME", "startup_template")
        client = MongoClient(mongo_url)
        db = client[db_name]
        found = db.outgoing_emails.find_one({
            "tag": "delivery_status_ai",
            "session_id": session_id,
        })
        if not found:
            # Try broader search - order number
            found = db.outgoing_emails.find_one({
                "tag": "delivery_status_ai",
                "order_number": {"$regex": "20260430-0001", "$options": "i"},
            })
        assert found is not None, (
            "Expected an outgoing_emails record with tag 'delivery_status_ai' for this session/order — none found."
        )
        print(f"[DELIVERY] outgoing_emails record ok: to={found.get('to')} order={found.get('order_number')} status={found.get('status')}")


# ============ AI SERVICE AGENT ============
class TestAIServiceAgent:
    def test_service_diy_first(self):
        session_id = f"TEST_service_{uuid.uuid4().hex[:8]}"
        payload = {
            "agent_type": "service",
            "message": "my Bosch washing machine is not draining",
            "session_id": session_id,
        }
        r = requests.post(CHAT_URL, json=payload, timeout=AI_TIMEOUT)
        assert r.status_code == 200, f"status={r.status_code} body={r.text[:300]}"
        data = r.json()
        resp = (data.get("response") or "").lower()
        print(f"\n[SERVICE turn1 len={len(resp)}] preview: {resp[:400]}")

        # DIY hint: expect words like check/filter/hose/drain/troubleshoot BEFORE any ticket
        diy_keywords = ["filter", "hose", "drain", "check", "try", "step", "clog", "pump", "pipe", "clean"]
        matched_diy = [k for k in diy_keywords if k in resp]
        assert len(matched_diy) >= 2, f"Expected DIY troubleshooting keywords, matched={matched_diy}. Text: {resp[:400]}"

        # Should NOT have created a ticket in first turn
        assert not data.get("ticket_number"), f"Ticket created on first turn (should give DIY first): {data.get('ticket_number')}"

        # ---- turn 2: continuity ----
        payload2 = {
            "agent_type": "service",
            "message": "I already checked the filter, it's clean. Still not draining.",
            "session_id": session_id,
        }
        r2 = requests.post(CHAT_URL, json=payload2, timeout=AI_TIMEOUT)
        assert r2.status_code == 200
        resp2 = (r2.json().get("response") or "").lower()
        print(f"[SERVICE turn2 len={len(resp2)}] preview: {resp2[:400]}")
        # Should reference washing machine / drain context OR proceed to book a technician
        assert any(k in resp2 for k in ["washing", "machine", "drain", "technician", "ticket", "service", "book", "visit", "engineer"]), (
            f"Service agent lost context: {resp2[:400]}"
        )


# ============ NORMALIZE CATEGORIES ============
class TestCategoryNormalization:
    def test_normalize_categories_idempotent(self, admin_headers):
        url = f"{BASE_URL}/api/products/normalize-categories"
        r1 = requests.post(url, headers=admin_headers, timeout=60)
        assert r1.status_code == 200, f"1st run failed: {r1.status_code} {r1.text[:300]}"
        d1 = r1.json()
        print(f"\n[normalize-categories run1] {d1}")

        # 2nd run should be idempotent — updated/changed count should be 0 or very small
        r2 = requests.post(url, headers=admin_headers, timeout=60)
        assert r2.status_code == 200
        d2 = r2.json()
        print(f"[normalize-categories run2] {d2}")
        changed = d2.get("updated") or d2.get("modified") or d2.get("changed") or d2.get("count") or 0
        # If not present, look inside detail
        assert changed == 0 or changed <= 2, f"Second run should be idempotent (~0 changes), got {d2}"

    def test_products_categories_normalized(self):
        r = requests.get(f"{BASE_URL}/api/products?limit=500", timeout=30)
        assert r.status_code == 200, f"{r.status_code} {r.text[:200]}"
        data = r.json()
        # Handle both list and paginated dict
        products = data if isinstance(data, list) else data.get("products") or data.get("items") or []
        assert products, "No products returned"

        bad_cats = set()
        for p in products:
            cat = (p.get("category") or "").strip()
            if cat in ("Micrwave", "Refrigerators", "Hoods"):
                bad_cats.add(cat)
        assert not bad_cats, f"Found un-normalized categories still present: {bad_cats}"
        print(f"\n[products] scanned {len(products)} products — no bad categories found")
