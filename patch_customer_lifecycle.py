import os, shutil

B, BK = "/app/backend", "/app/_backup/lifecycle"
os.makedirs(BK, exist_ok=True)

def patch(fn, fnc):
    p = f"{B}/{fn}"
    src = open(p).read()
    shutil.copy(p, f"{BK}/{fn}")
    new = fnc(src)
    if new == src:
        print("NO CHANGE (already patched or anchor missing):", fn)
    else:
        open(p, "w").write(new); print("patched:", fn)

def need_one(src, anchor, label):
    n = src.count(anchor)
    if n != 1:
        raise SystemExit(f"ABORT {label}: anchor found {n} times (expected 1)")

# 1) Admin status route -> delivery hook
def p_orders(src):
    if "customer_lifecycle" in src: return src
    a = ("        # Send notification for status change\n"
         "        try:\n"
         "            await notify_order_status_change(db, order, old_status, new_status)")
    need_one(src, a, "orders_routes")
    hook = ('        # Customer lifecycle: auto-register warranty / reminders on delivery\n'
            '        if new_status == "delivered" and old_status != "delivered":\n'
            '            try:\n'
            '                from customer_lifecycle import on_order_delivered\n'
            '                await on_order_delivered(db, {**order, "order_status": "delivered"})\n'
            '            except Exception as lifecycle_error:\n'
            '                print(f"Lifecycle hook error (non-blocking): {lifecycle_error}")\n\n')
    return src.replace(a, hook + a)
patch("orders_routes.py", p_orders)

# 2) Shiprocket poller -> timeline entry + delivery hook
def p_sr(src):
    if "customer_lifecycle" in src: return src
    a = '    await db.orders.update_one({"id": order.get("id")}, {"$set": update})\n'
    need_one(src, a, "shiprocket_tracking_service")
    hook = ('    if changed_stage:\n'
            '        try:\n'
            '            await db.orders.update_one({"id": order.get("id")}, {"$push": {"timeline": {\n'
            '                "status": changed_stage, "timestamp": datetime.now(timezone.utc).isoformat(),\n'
            '                "message": f"Shipment update: {sr_status}", "updated_by": "shiprocket"}}})\n'
            '            if changed_stage == "delivered":\n'
            '                from customer_lifecycle import on_order_delivered\n'
            '                await on_order_delivered(db, {**order, **update})\n'
            '        except Exception as _lc_err:\n'
            '            logger.warning(f"[SR-Track] lifecycle hook failed: {_lc_err}")\n')
    return src.replace(a, a + hook)
patch("shiprocket_tracking_service.py", p_sr)

# 3) Dashboard routes: ownership fix, suggestions rewrite, timeline endpoint
def p_dash(src):
    if "customer_lifecycle" in src: return src
    old = 'customer = invoice.get("customer", {})'
    need_one(src, old, "dashboard customer line")
    src = src.replace(old, 'customer = invoice.get("customer") or invoice.get("customer_details") or {}')

    s = src.index('@router.get("/consumables/suggestions")')
    e = src.index("class QuickOrderRequest(BaseModel):")
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
    return src
patch("customer_dashboard_routes.py", p_dash)

# 4) Invoice/order number: date part in IST (sequence unchanged)
def p_inv(src):
    if "_IST" in src: return src
    src = src.replace("from datetime import datetime, timezone",
                      "from datetime import datetime, timezone, timedelta\n_IST = timezone(timedelta(hours=5, minutes=30))", 1)
    return src.replace("date_prefix = today.strftime('%Y%m%d')",
                       "date_prefix = today.astimezone(_IST).strftime('%Y%m%d')")
patch("invoice_numbering.py", p_inv)
