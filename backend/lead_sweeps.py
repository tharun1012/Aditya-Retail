import re, uuid, logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Header
from mail_leads import check_secret, get_db

router = APIRouter(prefix="/lead-sweeps", tags=["lead-sweeps"])
log = logging.getLogger(__name__)

def _dt(v):
    if isinstance(v, datetime):
        return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
    try:
        d = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except Exception:
        return None

def _phone(v):
    return "".join(c for c in str(v or "") if c.isdigit())[-10:] or None

def _email(v):
    return (v or "").strip().lower() or None

async def add_lead(db, key, name, email, phone, source, note, products=None, score=60):
    """Create a lead, or add a note to the existing one. Never raises."""
    try:
        email, phone = _email(email), _phone(phone)
        if not (email or phone):
            return None
        if await db.leads.find_one({"$or": [{"dedup_key": key}, {"sweep_keys": key}]}):
            return None
        conds = []
        if email:
            conds.append({"email": {"$regex": "^" + re.escape(email) + "$", "$options": "i"}})
        if phone:
            conds.append({"phone": {"$regex": phone + "$"}})
        now = datetime.now(timezone.utc).isoformat()
        ex = await db.leads.find_one({"$or": conds})
        if ex:
            await db.leads.update_one({"_id": ex["_id"]}, {
                "$addToSet": {"sweep_keys": key},
                "$push": {"interactions": {"timestamp": now, "type": "note", "content": note, "agent": source}},
                "$set": {"updated_at": now}})
            return "linked"
        await db.leads.insert_one({
            "id": "LEAD-SWP-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:6].upper(),
            "dedup_key": key, "name": name or email or "Customer", "email": email, "phone": phone,
            "source": source, "status": "new", "lead_type": "sales", "score": score,
            "notes": note, "interested_products": products or [], "assigned_to": None,
            "created_at": now, "updated_at": now})
        return "created"
    except Exception as e:
        log.warning("sweep lead failed: %s", e)
        return None

def _count(c, r):
    if r:
        c[r] += 1

async def sweep_payments(db):
    c = {"created": 0, "linked": 0}
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
    async for o in db.orders.find({"payment_status": {"$in": ["pending", "failed"]}}):
        d = _dt(o.get("created_at"))
        if not d or d > cutoff:
            continue
        cd = o.get("customer_details") or {}
        prods = [i.get("product_name") for i in (o.get("items") or []) if i.get("product_name")]
        note = "Payment %s on order %s (total %s)" % (o.get("payment_status"), o.get("order_number"), o.get("total_amount"))
        _count(c, await add_lead(db, "payment_" + str(o.get("order_id") or o.get("id")),
               cd.get("name"), cd.get("email"), cd.get("phone"), "payment_failed", note, prods, 70))
    return c

async def sweep_service(db):
    c = {"created": 0, "linked": 0}
    async for t in db.service_tickets.find({}):
        note = "Service ticket %s (%s, warranty: %s). Upsell: AMC / accessories" % (
            t.get("ticket_number"), t.get("product_name"), t.get("warranty_status"))
        _count(c, await add_lead(db, "service_" + str(t.get("ticket_number") or t.get("id")),
               t.get("customer_name"), t.get("customer_email"), t.get("customer_phone"),
               "service_upsell", note, [t["product_name"]] if t.get("product_name") else [], 55))
    return c

async def sweep_repeat(db):
    c = {"created": 0, "linked": 0}
    cutoff = datetime.now(timezone.utc) - timedelta(days=5 * 365)
    latest = {}
    async for o in db.orders.find({"payment_status": {"$nin": ["pending", "failed"]}}):
        cd = o.get("customer_details") or {}
        k = _phone(cd.get("phone")) or _email(cd.get("email"))
        d = _dt(o.get("created_at"))
        if not k or not d:
            continue
        if k not in latest or d > latest[k][0]:
            latest[k] = (d, o)
    for k, (d, o) in latest.items():
        if d > cutoff:
            continue
        cd = o.get("customer_details") or {}
        prods = [i.get("product_name") for i in (o.get("items") or []) if i.get("product_name")]
        note = "Last purchase %s, 5+ years ago. Replacement / upgrade candidate" % d.date()
        _count(c, await add_lead(db, "repeat_" + k, cd.get("name"), cd.get("email"), cd.get("phone"),
               "repeat_buyer", note, prods, 45))
    return c

@router.post("/run")
async def run(x_webhook_secret: str | None = Header(default=None)):
    check_secret(x_webhook_secret)
    db = get_db()
    return {"payments": await sweep_payments(db), "service": await sweep_service(db), "repeat": await sweep_repeat(db)}

import asyncio

async def _loop():
    await asyncio.sleep(60)
    while True:
        try:
            db = get_db()
            await sweep_payments(db)
            await sweep_service(db)
            await sweep_repeat(db)
        except Exception as e:
            log.warning("sweep loop failed: %s", e)
        await asyncio.sleep(1800)

def start_loop():
    asyncio.create_task(_loop())
