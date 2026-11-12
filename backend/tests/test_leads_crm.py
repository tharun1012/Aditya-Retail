"""
Backend tests for the Lead Management CRM.
Covers:
- GET /api/leads/ (lead_type classification, filtering, funnel)
- POST/PUT/DELETE /api/leads/
- POST /api/leads/follow-up
- GET /api/admin/customers/{customer_id} for Customer detail modal
- POST /api/auth/admin/login for admin auth
Uses ONLY throwaway TEST_ leads for destructive checks; does NOT touch
seeded Ravi Kumar/Sunita Sharma/Mohan Das/Priya Nair leads.
"""
import os
import pytest
import requests
from datetime import datetime, timedelta

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

ADMIN_EMAIL = "rohit.gadiya@gmail.com"
ADMIN_PASSWORD = "Purvi@vriddhi01"


# ---------- Fixtures ----------

@pytest.fixture(scope="module")
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def admin_token(client):
    """Admin login returns a JWT for protected endpoints."""
    r = client.post(f"{BASE_URL}/api/auth/admin/login",
                    json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, f"Admin login failed: {r.status_code} {r.text[:200]}"
    data = r.json()
    token = data.get("access_token") or data.get("token")
    assert token, f"No token in login response: {data}"
    return token


@pytest.fixture(scope="module")
def auth_client(client, admin_token):
    client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return client


# ---------- Auth ----------

class TestAdminAuth:
    def test_admin_login_success(self, client):
        r = client.post(f"{BASE_URL}/api/auth/admin/login",
                        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        assert r.status_code == 200
        d = r.json()
        assert d.get("access_token") or d.get("token")


# ---------- Lead listing / classification ----------

class TestLeadListing:
    def test_get_all_leads_returns_lead_type(self, auth_client):
        r = auth_client.get(f"{BASE_URL}/api/leads/")
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "success"
        assert isinstance(d["leads"], list)
        assert d["total"] == len(d["leads"])
        assert d["total"] > 0, "Expected at least some seeded leads"
        # Every lead must have lead_type computed
        for lead in d["leads"]:
            assert "lead_type" in lead, f"Missing lead_type in {lead.get('id')}"
            assert lead["lead_type"] in {"sales", "service", "delivery", "expert", "other"}
        # Ensure NO mongo _id leaks
        for lead in d["leads"]:
            assert "_id" not in lead

    def test_seeded_leads_classification(self, auth_client):
        r = auth_client.get(f"{BASE_URL}/api/leads/")
        leads = r.json()["leads"]
        by_name = {(l.get("name") or "").strip(): l for l in leads}
        # Only assert if seeded leads exist — soft check
        expected = {
            "Ravi Kumar": "sales",
            "Sunita Sharma": "service",
            "Mohan Das": "delivery",
            "Priya Nair": "expert",
        }
        found = 0
        for name, want in expected.items():
            if name in by_name:
                found += 1
                assert by_name[name]["lead_type"] == want, (
                    f"{name} classified as {by_name[name]['lead_type']} expected {want}"
                )
        assert found >= 1, f"None of expected seeded leads found. Names present: {list(by_name.keys())[:10]}"

    def test_lead_type_filter(self, auth_client):
        r = auth_client.get(f"{BASE_URL}/api/leads/?lead_type=service")
        assert r.status_code == 200
        leads = r.json()["leads"]
        for l in leads:
            assert l["lead_type"] == "service"

    def test_funnel_has_by_type(self, auth_client):
        r = auth_client.get(f"{BASE_URL}/api/leads/funnel")
        assert r.status_code == 200
        f = r.json()["funnel"]
        assert "by_type" in f, "funnel must include by_type buckets"
        # Should have at least one team bucket
        assert isinstance(f["by_type"], dict)
        assert sum(f["by_type"].values()) == f["total_leads"], (
            f"by_type sum {sum(f['by_type'].values())} != total_leads {f['total_leads']}"
        )


# ---------- Lead CRUD (isolated to TEST_ leads) ----------

class TestLeadCRUD:
    created_id = None

    def test_create_lead(self, auth_client):
        payload = {
            "name": "TEST_Playwright Lead",
            "email": "test_playwright_lead@example.com",
            "phone": "9999999999",
            "source": "Neural Sales Agent",
            "notes": "Created by automated test",
        }
        r = auth_client.post(f"{BASE_URL}/api/leads/", json=payload)
        assert r.status_code == 200, r.text[:200]
        d = r.json()
        assert d["status"] == "success"
        assert d.get("lead_id")
        TestLeadCRUD.created_id = d["lead_id"]

        # Verify GET returns it with sales classification
        gr = auth_client.get(f"{BASE_URL}/api/leads/{TestLeadCRUD.created_id}")
        assert gr.status_code == 200
        lead = gr.json()["lead"]
        assert lead["name"] == payload["name"]
        assert lead["lead_type"] == "sales"

    def test_update_lead_status_and_assignee(self, auth_client):
        assert TestLeadCRUD.created_id, "Requires prior create"
        r = auth_client.put(f"{BASE_URL}/api/leads/{TestLeadCRUD.created_id}",
                            json={"status": "contacted",
                                  "assigned_to": "TEST_agent_1",
                                  "notes": "TEST_ note from automation"})
        assert r.status_code == 200
        updated = r.json()["lead"]
        assert updated["status"] == "contacted"
        assert updated["assigned_to"] == "TEST_agent_1"
        # notes push to interactions
        assert any(i.get("content") == "TEST_ note from automation"
                   for i in updated.get("interactions", []))

    def test_add_follow_up(self, auth_client):
        assert TestLeadCRUD.created_id
        due = (datetime.utcnow() + timedelta(days=1)).isoformat()
        r = auth_client.post(f"{BASE_URL}/api/leads/follow-up",
                             json={"lead_id": TestLeadCRUD.created_id,
                                   "follow_up_date": due,
                                   "action": "TEST_call_back",
                                   "notes": "TEST_ follow-up"})
        assert r.status_code == 200, r.text[:200]
        d = r.json()
        assert d["status"] == "success"
        assert d["follow_up"]["action"] == "TEST_call_back"

        # Verify persisted
        gr = auth_client.get(f"{BASE_URL}/api/leads/{TestLeadCRUD.created_id}")
        lead = gr.json()["lead"]
        actions = [fu.get("action") for fu in lead.get("follow_ups", [])]
        assert "TEST_call_back" in actions

    def test_delete_lead(self, auth_client):
        assert TestLeadCRUD.created_id
        r = auth_client.delete(f"{BASE_URL}/api/leads/{TestLeadCRUD.created_id}")
        assert r.status_code == 200
        # Confirm gone
        gr = auth_client.get(f"{BASE_URL}/api/leads/{TestLeadCRUD.created_id}")
        assert gr.status_code == 404


# ---------- Classification via source strings ----------

class TestLeadTypeClassification:
    """Create disposable leads with different sources and confirm classification."""

    @pytest.mark.parametrize("source,expected", [
        ("ai_chat_website", "sales"),
        ("Neural Service Agent", "service"),
        ("Neural Delivery Agent", "delivery"),
        ("Expert Consultation", "expert"),
        ("phone", "other"),
    ])
    def test_source_classification(self, auth_client, source, expected):
        payload = {"name": f"TEST_cls_{expected}", "source": source,
                   "email": None, "phone": None}
        r = auth_client.post(f"{BASE_URL}/api/leads/", json=payload)
        assert r.status_code == 200
        lead_id = r.json()["lead_id"]
        try:
            gr = auth_client.get(f"{BASE_URL}/api/leads/{lead_id}")
            assert gr.status_code == 200
            assert gr.json()["lead"]["lead_type"] == expected, (
                f"source={source} expected={expected} got={gr.json()['lead']['lead_type']}"
            )
        finally:
            auth_client.delete(f"{BASE_URL}/api/leads/{lead_id}")


# ---------- Customer detail (View Details fix) ----------

class TestCustomerDetails:
    def test_customer_detail_endpoint(self, auth_client):
        # List customers first
        r = auth_client.get(f"{BASE_URL}/api/admin/customers/?page=1&limit=5")
        assert r.status_code == 200, r.text[:200]
        d = r.json()
        # customers list may be under different keys — be forgiving
        customers = d.get("customers") or d.get("data") or []
        if not customers:
            pytest.skip("No customers available to test detail endpoint")
        cust_id = customers[0].get("id") or customers[0].get("customer_id") or customers[0].get("_id")
        if not cust_id:
            pytest.skip("Customer object missing id")
        r2 = auth_client.get(f"{BASE_URL}/api/admin/customers/{cust_id}")
        assert r2.status_code == 200, r2.text[:200]
        # response should include some contact / order info
        body = r2.json()
        assert body  # non-empty
