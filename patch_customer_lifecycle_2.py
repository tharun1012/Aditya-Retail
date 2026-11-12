import os, shutil
B, BK = "/app/backend", "/app/_backup/lifecycle2"
os.makedirs(BK, exist_ok=True)

# ---- customer_dashboard_routes.py ----
p = f"{B}/customer_dashboard_routes.py"
src = open(p).read()
if "build_suggestions" in src:
    print("dashboard: already patched")
else:
    shutil.copy(p, f"{BK}/customer_dashboard_routes.py")
    old = 'customer = invoice.get("customer", {})'
    print("dashboard: owner-check lines found:", src.count(old))
    src = src.replace(old, 'customer = invoice.get("customer") or invoice.get("customer_details") or {}')

    s = src.find('@router.get("/consumables/suggestions")')
    e = src.find("class QuickOrderRequest(BaseModel):")
    if s < 0 or e < 0 or e < s:
        raise SystemExit("ABORT: suggestions route anchors not found; nothing written")
    new_fn = '''@router.get("/consumables/suggestions")
async def get_consumable_suggestions(user_id: str, database = Depends(get_db)):
    """Smart consumable suggestions: category-based, real catalog products, reorders"""
    try:
        from customer_lifecycle import build_suggestions
        suggestions = await build_suggestions(database, user_id)
        return {"status": "success", "suggestions": suggestions, "total": len(suggestions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


'''
    src = src[:s] + new_fn + src[e:]
    src = src.rstrip("\n") + '''


# ============================================
# ORDER TIMELINE (customer view)
# ============================================
@router.get("/orders/{order_id}/timeline")
async def get_order_timeline(order_id: str, user_id: str, database = Depends(get_db)):
    order = await database.orders.find_one(
        {"$or": [{"id": order_id}, {"order_number": order_id}], "customer_id": user_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    stages = ["placed", "confirmed", "processing", "shipped", "out_for_delivery", "delivered"]
    status = (order.get("order_status") or "placed").lower()
    alias = {"pending": "placed", "packed": "processing"}
    current = alias.get(status, status)
    idx = stages.index(current) if current in stages else -1
    times = {t.get("status"): t.get("timestamp") for t in order.get("timeline", [])}
    times.setdefault("placed", order.get("created_at"))
    steps = [{"stage": s, "done": i <= idx, "current": i == idx, "at": times.get(s)} for i, s in enumerate(stages)]
    return {
        "status": "success", "order_number": order.get("order_number"), "order_status": status,
        "cancelled": status in ("cancelled", "refunded"), "steps": steps,
        "courier": order.get("sr_courier"), "awb": order.get("sr_awb_code"),
        "tracking_url": order.get("tracking_url"),
        "payment_method": order.get("payment_method"), "payment_status": order.get("payment_status"),
    }
'''
    open(p, "w").write(src)
    print("dashboard: patched")

# ---- invoice_numbering.py (IST date part, sequence untouched) ----
p = f"{B}/invoice_numbering.py"
src = open(p).read()
if "_IST" in src:
    print("invoice_numbering: already patched")
else:
    shutil.copy(p, f"{BK}/invoice_numbering.py")
    a = "from datetime import datetime, timezone"
    b = "date_prefix = today.strftime('%Y%m%d')"
    print("invoice_numbering: import lines:", src.count(a), "| date lines:", src.count(b))
    if src.count(a) >= 1 and src.count(b) >= 1:
        src = src.replace(a, a + ", timedelta\n_IST = timezone(timedelta(hours=5, minutes=30))", 1)
        src = src.replace(b, "date_prefix = today.astimezone(_IST).strftime('%Y%m%d')")
        open(p, "w").write(src)
        print("invoice_numbering: patched")
    else:
        print("invoice_numbering: anchors missing, skipped")
