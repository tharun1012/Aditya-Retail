"""Customer lifecycle: delivery hook, warranty auto-registration, smart suggestions."""
import re
import uuid
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta

CONSUMABLE_CATEGORIES = {"detergent"}   # extend if more consumable categories appear
DEFAULT_WARRANTY_MONTHS = 12
DEFAULT_REFILL_DAYS = 30

# appliance category keyword -> [(name, [catalog keywords], refill days, type)]
CATEGORY_CONSUMABLES = {
    "dishwasher": [
        ("Dishwasher Tablets", ["tablet"], 30, "detergent"),
        ("Dishwasher Salt", ["salt"], 60, "salt"),
        ("Rinse Aid", ["rinse"], 45, "cleaning"),
        ("Dishwasher Cleaner", ["cleaner", "machine care"], 90, "cleaning"),
    ],
    "washing machine": [
        ("Washing Machine Cleaner / Descaler", ["descal", "cleaner"], 90, "cleaning"),
        ("Liquid Detergent", ["detergent"], 30, "detergent"),
    ],
    "refrigerator": [
        ("Refrigerator Deodorizer / Cleaner", ["deodor", "fridge", "refrigerator"], 90, "cleaning"),
    ],
    "coffee machine": [
        ("Descaling Tablets", ["descal"], 60, "cleaning"),
        ("Cleaning Tablets", ["cleaning tablet"], 30, "cleaning"),
    ],
    "chimney": [
        ("Chimney Filter", ["filter"], 90, "filter"),
        ("Chimney Cleaner", ["degreaser", "cleaner"], 60, "cleaning"),
    ],
    "oven": [
        ("Oven Cleaner", ["oven cleaner"], 90, "cleaning"),
    ],
}


def _now():
    return datetime.now(timezone.utc)


def _parse_dt(v):
    if isinstance(v, datetime):
        return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
    if isinstance(v, str) and v:
        try:
            d = datetime.fromisoformat(v.replace("Z", "+00:00"))
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
        except Exception:
            return None
    return None


def parse_warranty(w):
    """Return (months, text). Uses the first 'N year/month' found, default 12 months."""
    text = ""
    if isinstance(w, dict):
        text = str(w.get("period") or "")
    elif w:
        text = str(w)
    m = re.search(r"(\d+)\s*(year|yr|month)", text, re.I)
    if not m:
        return DEFAULT_WARRANTY_MONTHS, text
    n, unit = int(m.group(1)), m.group(2).lower()
    return (n * 12 if unit.startswith("y") else n), text


async def on_order_delivered(db, order):
    """Idempotent. Registers appliances (warranty) and records consumable purchases (reorder reminders)."""
    try:
        _pm = str(order.get("payment_method") or "").lower()
        _ps = str(order.get("payment_status") or "pending").lower()
        if order.get("id") and _ps in ("pending", "unpaid", "") and ("cod" in _pm or "cash" in _pm):
            await db.orders.update_one(
                {"id": order["id"]},
                {"$set": {"payment_status": "completed", "cod_collected_at": _now().isoformat()}})
    except Exception as _e:
        print(f"COD payment update error (non-blocking): {_e}")
    user_id = order.get("customer_id")
    email = ((order.get("customer_details") or {}).get("email") or "").lower()
    if not user_id and email:
        u = await db.users.find_one({"email": email})
        if u:
            user_id = u.get("id")
            await db.orders.update_one({"id": order.get("id")}, {"$set": {"customer_id": user_id}})
    if not user_id:
        return {"skipped": "no customer account for this order"}

    now = _now()
    result = {"registered": 0, "consumables": 0}
    for item in order.get("items", []):
        pid = item.get("product_id")
        prod = await db.products.find_one({"id": pid}, {"_id": 0}) or {}
        category = (prod.get("category") or "").strip()
        name = item.get("product_name") or item.get("name") or prod.get("name") or "Product"
        qty = int(item.get("quantity") or 1)

        if category.lower() in CONSUMABLE_CATEGORIES:
            if not await db.consumable_purchases.find_one({"order_id": order.get("id"), "product_id": pid}):
                await db.consumable_purchases.insert_one({
                    "id": str(uuid.uuid4()), "user_id": user_id,
                    "order_id": order.get("id"), "order_number": order.get("order_number"),
                    "product_id": pid, "product_name": name, "category": category,
                    "quantity": qty, "purchased_at": now.isoformat(),
                    "refill_interval_days": int(prod.get("refill_interval_days") or DEFAULT_REFILL_DAYS),
                })
                result["consumables"] += 1
            continue

        if await db.registered_products.find_one(
                {"user_id": user_id, "order_id": order.get("id"), "product_id": pid}):
            continue
        months, wtext = parse_warranty(prod.get("warranty"))
        await db.registered_products.insert_one({
            "id": str(uuid.uuid4()), "user_id": user_id,
            "invoice_number": order.get("order_number"), "invoice_id": order.get("id"),
            "order_id": order.get("id"), "product_id": pid, "product_name": name,
            "brand": prod.get("brand"), "category": category,
            "model_number": prod.get("model_number"),
            "serial_numbers": [], "quantity": qty, "rate": item.get("price", 0),
            "purchase_date": now.isoformat(), "warranty_start_date": now.isoformat(),
            "warranty_end_date": (now + relativedelta(months=months)).isoformat(),
            "warranty_months": months, "warranty_terms": wtext,
            "source": "order", "status": "active",
            "created_at": now.isoformat(), "updated_at": now.isoformat(),
        })
        result["registered"] += 1
    return result


def _urgency(days):
    return "high" if days <= 7 else "medium" if days <= 30 else "low"


async def build_suggestions(db, user_id):
    now = _now()
    catalog = await db.products.find(
        {"category": {"$regex": "^(detergent|accessories)$", "$options": "i"}}, {"_id": 0}
    ).to_list(500)

    def pick(keywords, brand, appliance):
        cands = []
        for p in catalog:
            n = (p.get("name") or "").lower()
            if appliance != "dishwasher" and "dishwasher" in n:
                continue
            if any(k in n for k in keywords):
                cands.append(p)
        cands.sort(key=lambda p: 0 if (p.get("brand") or "").lower() == (brand or "").lower() else 1)
        return cands[0] if cands else None

    def card(p):
        if not p:
            return {"catalog_product_id": None, "price": None, "image": None, "in_catalog": False}
        imgs = p.get("images")
        img = imgs[0] if isinstance(imgs, list) and imgs and isinstance(imgs[0], str) else (p.get("image") or p.get("image_url"))
        return {"catalog_product_id": p.get("id"), "catalog_name": p.get("name"),
                "price": p.get("price") or p.get("selling_price"), "image": img, "in_catalog": True}

    out, seen = [], set()

    # 1) Reorders of consumables the customer already bought (latest purchase per product)
    purchases = await db.consumable_purchases.find({"user_id": user_id}, {"_id": 0}).sort("purchased_at", -1).to_list(200)
    bought = set()
    for cp in purchases:
        pid = cp.get("product_id")
        if pid in bought:
            continue
        bought.add(pid)
        freq = int(cp.get("refill_interval_days") or DEFAULT_REFILL_DAYS)
        due = (_parse_dt(cp.get("purchased_at")) or now) + timedelta(days=freq)
        days = (due - now).days
        prod = next((p for p in catalog if p.get("id") == pid), None)
        out.append({
            "kind": "reorder", "product_name": cp.get("product_name"), "product_id": pid,
            "consumable_name": cp.get("product_name"), "category": "reorder",
            "frequency_days": freq, "next_reminder_date": due.strftime("%Y-%m-%d"),
            "days_until_needed": max(0, days), "urgency": _urgency(days),
            "reason": f"Reorder: you bought this on {(_parse_dt(cp.get('purchased_at')) or now).strftime('%d %b %Y')}",
            **(card(prod) if prod else {"catalog_product_id": pid, "price": None, "image": None, "in_catalog": True}),
        })

    # 2) Cross-sell from registered appliances, matched by category
    regs = await db.registered_products.find({"user_id": user_id, "status": "active"}, {"_id": 0}).to_list(200)
    for rp in regs:
        pname = rp.get("product_name") or ""
        cat = (rp.get("category") or "").lower()
        if not cat and rp.get("product_id"):
            pr = await db.products.find_one({"id": rp["product_id"]}, {"category": 1}) or {}
            cat = (pr.get("category") or "").lower()
        appliance = next((k for k in CATEGORY_CONSUMABLES if k == cat or k in cat or k in pname.lower()), None)
        if not appliance:
            continue
        base = _parse_dt(rp.get("purchase_date")) or now
        for cname, kws, freq, ctype in CATEGORY_CONSUMABLES[appliance]:
            p = pick(kws, rp.get("brand"), appliance)
            if p and p.get("id") in bought:
                continue                      # already covered by a reorder card
            key = (rp.get("id"), cname)
            if key in seen:
                continue
            seen.add(key)
            cycles = max(0, (now - base).days) // freq
            due = base + timedelta(days=(cycles + 1) * freq)
            days = (due - now).days
            out.append({
                "kind": "cross_sell", "product_name": pname, "product_id": rp.get("product_id"),
                "consumable_name": cname, "category": ctype, "frequency_days": freq,
                "next_reminder_date": due.strftime("%Y-%m-%d"),
                "days_until_needed": max(0, days), "urgency": _urgency(days),
                "reason": f"Because you bought {pname}", **card(p),
            })

    rank = {"high": 0, "medium": 1, "low": 2}
    out.sort(key=lambda s: (rank.get(s["urgency"], 3), s["days_until_needed"]))
    return out
