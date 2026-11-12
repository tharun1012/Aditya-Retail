import os, re
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from bs4 import BeautifulSoup

router = APIRouter(prefix="/mail-leads", tags=["mail-leads"])
BRANDS = {"bosch": "Bosch", "siemens": "Siemens"}
STORE_CODES = {
    "DAS": "Dasarahalli Bosch Brand Store",
    "ARM": "Malleswaram Bosch Brand Store",
    "BNS": "Banaswadi Siemens And Bosch Brand Store",
    "ARH": "Malleswaram Haier Experience Center",
    "ART": "RT Nagar Bosch Brand Store",
    "HRBR": "HRBR Electrolux Exclusive Store",
}
PHONE_RE = re.compile(r"^\+?[\d\s\-]{10,15}$")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
DETAIL_FIELDS = {"Bosch": ["product_category", "enquiry_type", "timeline"], "Siemens": ["product_category", "message"]}
STATUSES = ["New", "Contacted", "Qualified", "Negotiation", "Won", "Lost"]

def get_db():
    from server import db
    return db

class IngestIn(BaseModel):
    message_id: str
    subject: str
    html: str
    received_at: str | None = None
    store_code: str

class StatusIn(BaseModel):
    status: str

def parse_mail(subject, html):
    subj = re.sub(r"^(fwd?:\s*)+", "", subject.strip(), flags=re.I)
    m = re.search(r"(\w+)\s+Home Appliances Contact Query Received From\s+(.+?)\.?$", subj, re.I)
    brand = BRANDS.get(m.group(1).lower(), "Other") if m else "Other"
    subj_name = m.group(2).strip() if m else None
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for td in soup.find_all("td"):
        if td.find("td"):
            continue
        t = " ".join(td.get_text(" ", strip=True).split())
        if t:
            rows.append(t)
    phone_i = next((i for i, r in enumerate(rows) if PHONE_RE.match(r)), None)
    if phone_i is None:
        raise ValueError("phone row not found")
    email_i = next((i for i in range(phone_i + 1, len(rows)) if EMAIL_RE.fullmatch(rows[i])), None)
    if email_i is None:
        raise ValueError("email row not found")
    name = rows[phone_i - 1] if phone_i > 0 else subj_name
    details = []
    for r in rows[email_i + 1:]:
        if r.lower().startswith("regards"):
            break
        details.append(r)
    fields = DETAIL_FIELDS.get(brand, [])
    parsed = dict(zip(fields, details))
    text = soup.get_text("\n", strip=True)
    addr = re.search(r"Query from,\s*(.+?)(?:\n\n|$)", text, re.S)
    return {
        "brand": brand, "name": name or subj_name,
        "phone": re.sub(r"[\s\-]", "", rows[phone_i]), "email": rows[email_i].lower(),
        "product_category": parsed.get("product_category"), "enquiry_type": parsed.get("enquiry_type"),
        "timeline": parsed.get("timeline"), "message": parsed.get("message"),
        "extra_fields": details[len(fields):],
        "store_address": " ".join(addr.group(1).split()) if addr else None,
    }

def check_secret(x):
    s = os.environ.get("MAIL_WEBHOOK_SECRET")
    if not s or x != s:
        raise HTTPException(401, "Invalid webhook secret")

@router.post("/ingest")
async def ingest(body: IngestIn, x_webhook_secret: str | None = Header(default=None)):
    check_secret(x_webhook_secret)
    if body.store_code not in STORE_CODES:
        raise HTTPException(400, "Invalid store_code")
    db = get_db()
    log = db.mail_ingest_log
    await log.create_index("message_id", unique=True)
    if await log.find_one({"message_id": body.message_id}):
        return {"status": "duplicate"}
    now = datetime.now(timezone.utc).isoformat()
    try:
        p = parse_mail(body.subject, body.html)
    except Exception as e:
        await log.insert_one({"message_id": body.message_id, "subject": body.subject,
                              "html": body.html, "status": "failed", "error": str(e), "created_at": now})
        raise HTTPException(422, f"Parse failed: {e}")
    hot = (p["timeline"] or "").lower().startswith("immediate") or "urgent" in (p["message"] or "").lower()
    existing = await db.mail_leads.find_one({"$or": [{"phone": p["phone"]}, {"email": p["email"]}]})
    lead = {**p, "source": "email", "status": "New", "is_hot": hot, "repeat_enquiry": bool(existing),
            "store_code": body.store_code, "store_name": STORE_CODES[body.store_code],
            "mail_message_id": body.message_id, "received_at": body.received_at or now, "created_at": now}
    await db.mail_leads.insert_one(lead)
    await log.insert_one({"message_id": body.message_id, "subject": body.subject, "status": "parsed", "created_at": now})
    return {"status": "created", "brand": p["brand"]}

@router.get("")
async def list_mail_leads(brand: str | None = None, store_code: str | None = None):
    q = {}
    if brand and brand != "All Mail":
        q["brand"] = brand
    if store_code and store_code != "all":
        q["store_code"] = store_code
    out = []
    async for d in get_db().mail_leads.find(q).sort("received_at", -1):
        d["id"] = str(d.pop("_id"))
        out.append(d)
    return out

@router.patch("/{lead_id}/status")
async def update_status(lead_id: str, body: StatusIn):
    if body.status not in STATUSES:
        raise HTTPException(400, "Invalid status")
    r = await get_db().mail_leads.update_one({"_id": ObjectId(lead_id)}, {"$set": {"status": body.status}})
    if not r.matched_count:
        raise HTTPException(404, "Not found")
    return {"ok": True}

@router.get("/failed")
async def failed():
    out = []
    async for d in get_db().mail_ingest_log.find({"status": "failed"}).sort("created_at", -1):
        d["id"] = str(d.pop("_id"))
        out.append(d)
    return out


class AssignIn(BaseModel):
    assigned_to: str

class NoteIn(BaseModel):
    text: str

class FollowUpIn(BaseModel):
    follow_up_at: str | None = None

def _oid(lead_id):
    try:
        return ObjectId(lead_id)
    except Exception:
        raise HTTPException(404, "Not found")

@router.patch("/{lead_id}/assign")
async def assign_lead(lead_id: str, body: AssignIn):
    r = await get_db().mail_leads.update_one({"_id": _oid(lead_id)}, {"$set": {"assigned_to": body.assigned_to.strip()}})
    if not r.matched_count:
        raise HTTPException(404, "Not found")
    return {"ok": True}

@router.post("/{lead_id}/notes")
async def add_note(lead_id: str, body: NoteIn):
    text = body.text.strip()
    if not text:
        raise HTTPException(400, "Empty note")
    note = {"text": text, "at": datetime.now(timezone.utc).isoformat()}
    r = await get_db().mail_leads.update_one({"_id": _oid(lead_id)}, {"$push": {"notes": note}})
    if not r.matched_count:
        raise HTTPException(404, "Not found")
    return {"ok": True}

@router.patch("/{lead_id}/followup")
async def set_followup(lead_id: str, body: FollowUpIn):
    r = await get_db().mail_leads.update_one({"_id": _oid(lead_id)}, {"$set": {"follow_up_at": body.follow_up_at or None}})
    if not r.matched_count:
        raise HTTPException(404, "Not found")
    return {"ok": True}
