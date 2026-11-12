import asyncio, re, uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from pydantic import BaseModel
from database import get_db
from leads_management_routes import require_lead_admin

router = APIRouter(prefix="/store-service", tags=["store-service"])
_lock = asyncio.Lock()
ISSUES = {"installation", "repair", "warranty", "general"}
BRANDS = {"bosch": "Bosch", "siemens": "Siemens"}
ADMIN_ROLES = {"admin", "super_admin"}


class ProductIn(BaseModel):
    product_name: Optional[str] = ""
    model: Optional[str] = ""


class StoreTicketIn(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = ""
    address: str
    city: Optional[str] = ""
    pincode: Optional[str] = ""
    brand: str
    model: Optional[str] = ""
    product_name: Optional[str] = ""
    products: Optional[List[ProductIn]] = None
    issue_type: str = "general"
    issue_description: Optional[str] = ""
    preferred_date: Optional[str] = ""
    preferred_time_slot: Optional[str] = ""
    store_code: Optional[str] = None  # used only when an admin raises the ticket


async def store_ctx(authorization: str = Header(None), db=Depends(get_db)):
    if not authorization:
        raise HTTPException(401, "Authorization required")
    token = authorization.replace("Bearer ", "").strip()

    # 1) Store login: opaque session token saved in store_sessions
    session = await db.store_sessions.find_one({"token": token}, {"_id": 0})
    if session:
        user = await db.store_users.find_one({"id": session.get("user_id"), "is_active": True}, {"_id": 0})
        if user and user.get("store_code"):
            name = user.get("store_name")
            if not name:
                try:
                    st = await db.stores.find_one(
                        {"$or": [{"code": user["store_code"]}, {"store_code": user["store_code"]}, {"id": user.get("store_id")}]},
                        {"_id": 0})
                    name = (st or {}).get("name") or (st or {}).get("store_name")
                except Exception:
                    name = None
            return {"role": user.get("role") or "store_manager", "email": user.get("email"),
                    "store_code": user["store_code"], "store_name": name or user["store_code"], "is_admin": False}
        raise HTTPException(401, "Invalid or expired token")

    # 2) Admin / JWT logins
    auth = await require_lead_admin(authorization, db)
    role = auth.get("role")
    keys = [v for v in (auth.get("sub"), auth.get("email"), auth.get("user_id"), auth.get("id")) if v]
    user = None
    for v in keys:
        user = await db.users.find_one({"$or": [{"email": v}, {"id": v}, {"user_id": v}]}, {"_id": 0})
        if user:
            break
    code = (user or {}).get("store_code") or auth.get("store_code")
    name = (user or {}).get("store_name") or auth.get("store_name")
    is_admin = role in ADMIN_ROLES
    if not is_admin and not code:
        raise HTTPException(403, "No store is assigned to this user")
    return {"role": role, "email": (user or {}).get("email") or auth.get("sub"),
            "store_code": code, "store_name": name, "is_admin": is_admin}


async def next_ticket_number(db):
    from ticket_numbering import next_ticket_number as _next
    return await _next(db, "SRV")


@router.post("/tickets")
async def create_ticket(body: StoreTicketIn, ctx=Depends(store_ctx), db=Depends(get_db)):
    brand = BRANDS.get((body.brand or "").strip().lower())
    if not brand:
        raise HTTPException(400, "Brand must be Bosch or Siemens")
    issue = (body.issue_type or "general").lower()
    if issue not in ISSUES:
        raise HTTPException(400, "Invalid issue type")
    phone = re.sub(r"\D", "", body.customer_phone or "")[-10:]
    if len(phone) != 10:
        raise HTTPException(400, "Enter a 10-digit phone number")
    items = [p for p in (body.products or []) if (p.product_name or "").strip() or (p.model or "").strip()]
    if not items:
        items = [ProductIn(product_name=body.product_name or "", model=body.model or "")]
    if len(items) > 10:
        raise HTTPException(400, "A ticket can have at most 10 products")
    for p in items:
        if len((p.model or "").strip()) < 4:
            raise HTTPException(400, "Enter the model number for every product")
        if not (p.product_name or "").strip():
            raise HTTPException(400, "Enter the product name for every product")
    model = (items[0].model or "").strip().upper()
    if not (body.customer_name or "").strip() or not (body.address or "").strip():
        raise HTTPException(400, "Customer name and address are required")
    if issue != "installation" and not (body.issue_description or "").strip():
        raise HTTPException(400, "Describe the issue")

    store_code, store_name = ctx["store_code"], ctx["store_name"]
    if ctx["is_admin"]:
        store_code = (body.store_code or store_code or "").strip()
        if not store_code:
            raise HTTPException(400, "store_code is required")
    products = []
    for p in items:
        pm = (p.model or "").strip().upper()
        pn = (p.product_name or "").strip()
        if brand.lower() not in pn.lower():
            pn = f"{brand} {pn}"
        if pm not in pn.upper():
            pn = f"{pn} {pm}"
        products.append({"product_name": pn, "model": pm, "qty": 1})
    name = " + ".join(x["product_name"] for x in products)

    now = datetime.now(timezone.utc).isoformat()
    async with _lock:
        ticket_number = await next_ticket_number(db)
        ticket = {
            "id": str(uuid.uuid4()), "ticket_number": ticket_number, "source": "store",
            "store_code": store_code, "store_name": store_name, "raised_by": ctx["email"],
            "customer_name": body.customer_name.strip(), "customer_phone": phone,
            "contact_email": (body.customer_email or "").strip(),
            "address": (body.address or "").strip(),
            "city": (body.city or "").strip() or "Bangalore",
            "pincode": (body.pincode or "").strip(),
            "brand": brand, "model_number": model,
            "product_name": name, "products": products, "serial_numbers": [], "invoice_number": None,
            "issue_description": (body.issue_description or "").strip(), "issue_type": issue,
            "preferred_date": body.preferred_date or "", "preferred_time_slot": body.preferred_time_slot or "",
            "priority": "normal", "status": "open", "store_status": "open", "address": body.address.strip(), "city": (body.city or "").strip(), "pincode": (body.pincode or "").strip(), "assigned_technician": None, "resolution_notes": None,
            "created_at": now, "updated_at": now,
        }
        await db.service_tickets.insert_one(ticket)

    try:
        from service_mail import send_company_mail
        addr = {"address_line1": body.address.strip(), "city": (body.city or "").strip() or "Bangalore",
                "pincode": (body.pincode or "").strip()}
        await send_company_mail(db, dict(ticket), {"brand": brand, "model_number": model}, {"address": addr})
    except Exception as e:
        print(f"Warning: store service mail failed: {e}")

    saved = await db.service_tickets.find_one({"ticket_number": ticket_number}, {"_id": 0})
    return {"status": "success", "ticket": saved}


@router.get("/tickets")
async def list_tickets(store_code: Optional[str] = Query(None), ctx=Depends(store_ctx), db=Depends(get_db)):
    if ctx["is_admin"]:
        q = {"store_code": store_code} if store_code else {"source": "store"}
    else:
        q = {"store_code": ctx["store_code"]}
    tickets = await db.service_tickets.find(q, {"_id": 0}).sort("created_at", -1).limit(500).to_list(500)
    return {"status": "success", "tickets": tickets, "total": len(tickets)}



STORE_STATUSES = {"open", "in_progress", "closed"}


class StoreStatusIn(BaseModel):
    status: str


@router.put("/tickets/{ticket_number}/status")
async def update_store_status(ticket_number: str, body: StoreStatusIn, ctx=Depends(store_ctx), db=Depends(get_db)):
    s = (body.status or "").strip().lower()
    if s not in STORE_STATUSES:
        raise HTTPException(400, "Status must be open, in_progress or closed")
    q = {"ticket_number": ticket_number}
    if not ctx["is_admin"]:
        q["store_code"] = ctx["store_code"]
    now = datetime.now(timezone.utc).isoformat()
    res = await db.service_tickets.update_one(q, {"$set": {
        "store_status": s, "store_status_updated_by": ctx["email"],
        "store_status_updated_at": now, "updated_at": now}})
    if not res.matched_count:
        raise HTTPException(404, "Ticket not found")
    return {"status": "success", "ticket_number": ticket_number, "store_status": s}



class ResendIn(BaseModel):
    address: Optional[str] = ""
    city: Optional[str] = ""
    pincode: Optional[str] = ""


@router.post("/tickets/{ticket_number}/resend-mail")
async def resend_mail(ticket_number: str, body: ResendIn, ctx=Depends(store_ctx), db=Depends(get_db)):
    t = await db.service_tickets.find_one({"ticket_number": ticket_number}, {"_id": 0})
    if not t or (not ctx["is_admin"] and t.get("store_code") != ctx["store_code"]):
        raise HTTPException(404, "Ticket not found")
    if t.get("company_mail_status") == "sent":
        raise HTTPException(409, "Mail was already sent for this ticket")
    from service_mail import send_company_mail
    try:
        if t.get("source") == "customer" or t.get("user_id"):
            uid = t.get("user_id")
            user = await db.users.find_one({"$or": [{"id": uid}, {"user_id": uid}]}) or {"email": t.get("customer_email"), "phone": t.get("customer_phone")}
            rp = None
            if t.get("registered_product_id"):
                rp = await db.registered_products.find_one({"id": t["registered_product_id"]}, {"_id": 0})
            await send_company_mail(db, dict(t), rp, user)
        else:
            address = (body.address or t.get("address") or "").strip()
            if not address:
                raise HTTPException(400, "Enter the customer address to resend this ticket")
            city = (body.city or t.get("city") or "").strip() or "Bangalore"
            pincode = (body.pincode or t.get("pincode") or "").strip()
            if body.address:
                await db.service_tickets.update_one({"ticket_number": ticket_number}, {"$set": {"address": address, "city": city, "pincode": pincode}})
            addr = {"address_line1": address, "city": city, "pincode": pincode}
            await send_company_mail(db, dict(t), {"brand": t.get("brand") or "", "model_number": t.get("model") or ""}, {"address": addr})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Resend failed: {str(e)[:150]}")
    saved = await db.service_tickets.find_one({"ticket_number": ticket_number}, {"_id": 0})
    return {"status": "success", "company_mail_status": saved.get("company_mail_status"),
            "error": saved.get("company_mail_error") or "", "ticket": saved}
