import re, uuid, logging
from datetime import datetime, timezone
from fastapi import APIRouter, Header
from mail_leads import check_secret, get_db

router = APIRouter(prefix="/website-leads", tags=["website-leads"])
log = logging.getLogger(__name__)

async def create_website_signup_lead(db, user):
    """Create a CRM lead from a website signup. Never raises."""
    try:
        if not user or user.get("role") not in (None, "customer") or user.get("auto_created"):
            return None
        email = (user.get("email") or "").strip().lower() or None
        phone = "".join(c for c in str(user.get("phone") or "") if c.isdigit())[-10:] or None
        uid = user.get("id") or user.get("user_id") or email
        dedup_key = "website_signup_" + str(uid)
        if await db.leads.find_one({"dedup_key": dedup_key}):
            return None
        conds = []
        if email:
            conds.append({"email": {"$regex": "^" + re.escape(email) + "$", "$options": "i"}})
        if phone:
            conds.append({"phone": {"$regex": phone + "$"}})
        if conds and await db.leads.find_one({"$or": conds}):
            return None
        name = (user.get("name") or user.get("full_name")
                or " ".join(x for x in [user.get("first_name"), user.get("last_name")] if x).strip()
                or (email.split("@")[0] if email else "Website Visitor"))
        now = datetime.now(timezone.utc).isoformat()
        lead = {
            "id": "LEAD-WEB-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:6].upper(),
            "dedup_key": dedup_key, "name": name, "email": email, "phone": phone,
            "source": "website_signup", "status": "new", "lead_type": "sales", "score": 50,
            "notes": "Signed up on the website", "interested_products": [], "assigned_to": None,
            "user_id": uid, "created_at": now, "updated_at": now,
        }
        await db.leads.insert_one(lead)
        return lead["id"]
    except Exception as e:
        log.warning("website signup lead failed: %s", e)
        return None

@router.post("/backfill")
async def backfill(x_webhook_secret: str | None = Header(default=None)):
    check_secret(x_webhook_secret)
    db = get_db()
    scanned = created = 0
    async for u in db.users.find({"role": "customer", "auto_created": {"$ne": True}}):
        scanned += 1
        if await create_website_signup_lead(db, u):
            created += 1
    return {"scanned": scanned, "created": created}
