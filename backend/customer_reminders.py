import os, asyncio, logging, html
from datetime import datetime, timedelta, timezone
from customer_lifecycle import build_suggestions, _parse_dt, _now

logger = logging.getLogger(__name__)
STORE_URL = os.environ.get("STORE_URL", "https://adityaretail.com").rstrip("/")
WARRANTY_DAYS = 30
REORDER_DAYS = 7
MAX_OVERDUE_DAYS = 30


def _dry():
    return os.environ.get("REMINDER_DRY_RUN", "true").lower() != "false"


def _page(name, intro, rows, btn, link):
    items = "".join(f"<li style='margin:6px 0'>{r}</li>" for r in rows)
    return (f"<div style='font-family:Arial,sans-serif;max-width:560px;margin:auto;color:#333'>"
            f"<p>Hi {html.escape(name)},</p><p>{intro}</p><ul>{items}</ul>"
            f"<p style='margin:20px 0'><a href='{link}' style='background:#1e3a5f;color:#fff;padding:12px 22px;"
            f"border-radius:6px;text-decoration:none;font-weight:bold'>{btn}</a></p>"
            f"<p style='font-size:12px;color:#888'>Aditya Retail</p></div>")


async def _send(to, subject, body):
    from sendgrid_email_service import sendgrid_email_service
    res = await asyncio.to_thread(lambda: sendgrid_email_service.send_email(
        to_email=to, subject=subject, body=body, from_agent="delivery", html=True))
    return bool(res and res.get("status") in ("sent", "success"))


async def run_reminders(db):
    now = _now()
    dry = _dry()
    per_user = {}
    stats = {"warranty": 0, "reorder": 0, "users": 0, "dry_run": dry}

    def bucket(uid):
        return per_user.setdefault(uid, {"warranty": [], "reorder": []})

    # 1) Warranty ending within 30 days
    regs = await db.registered_products.find({"status": "active"}, {"_id": 0}).to_list(10000)
    for rp in regs:
        end = _parse_dt(rp.get("warranty_end_date"))
        uid = rp.get("user_id")
        if not end or not uid:
            continue
        days = (end - now).days
        if 0 <= days <= WARRANTY_DAYS:
            key = f"warranty:{rp.get('id')}"
            if not await db.reminder_log.find_one({"key": key}):
                bucket(uid)["warranty"].append((rp, days, key))

    # 2) Consumable reorders due within 7 days
    for uid in await db.consumable_purchases.distinct("user_id"):
        try:
            sugg = await build_suggestions(db, uid)
        except Exception as e:
            logger.warning(f"[Reminders] suggestions failed for {uid}: {e}")
            continue
        for s in sugg:
            if s.get("kind") != "reorder" or s.get("days_until_needed", 99) > REORDER_DAYS:
                continue
            due = _parse_dt(s.get("next_reminder_date"))
            if due and (now - due).days > MAX_OVERDUE_DAYS:
                continue
            key = f"reorder:{uid}:{s.get('product_id')}:{s.get('next_reminder_date')}"
            if not await db.reminder_log.find_one({"key": key}):
                bucket(uid)["reorder"].append((s, key))

    # 3) One email per type per customer
    for uid, b in per_user.items():
        user = await db.users.find_one({"$or": [{"id": uid}, {"user_id": uid}]}, {"_id": 0}) or {}
        email = (user.get("email") or "").strip()
        name = user.get("name") or user.get("full_name") or "Customer"
        if not email:
            continue
        stats["users"] += 1

        if b["warranty"]:
            rows = [f"<b>{html.escape(str(rp.get('product_name')))}</b>: warranty ends on "
                    f"{(_parse_dt(rp.get('warranty_end_date')) or now).strftime('%d %b %Y')} ({d} days left)"
                    for rp, d, _ in b["warranty"]]
            body = _page(name, "Your warranty is ending soon. Book a service check while you are still covered:",
                         rows, "Book service", f"{STORE_URL}/my-account")
            subject = "Your product warranty is ending soon"
            if dry:
                logger.info(f"[Reminders][DRY] warranty -> {email}: {len(rows)} item(s)")
            elif await _send(email, subject, body):
                for _, _, key in b["warranty"]:
                    await db.reminder_log.insert_one({"key": key, "user_id": uid, "sent_at": now.isoformat()})
                stats["warranty"] += len(rows)

        if b["reorder"]:
            rows = [f"<b>{html.escape(str(s.get('product_name')))}</b>: due around {s.get('next_reminder_date')}"
                    for s, _ in b["reorder"]]
            body = _page(name, "These items you bought earlier are due for a refill:",
                         rows, "Reorder now", f"{STORE_URL}/my-account")
            subject = "Time to reorder your essentials"
            if dry:
                logger.info(f"[Reminders][DRY] reorder -> {email}: {len(rows)} item(s)")
            elif await _send(email, subject, body):
                for _, key in b["reorder"]:
                    await db.reminder_log.insert_one({"key": key, "user_id": uid, "sent_at": now.isoformat()})
                stats["reorder"] += len(rows)

    logger.info(f"[Reminders] done: {stats}")
    return stats


async def reminders_loop(db):
    """Runs daily at 9:00 IST. Set REMINDER_RUN_ON_START=true to also run once, 60s after startup (for testing)."""
    ist = timezone(timedelta(hours=5, minutes=30))
    if os.environ.get("REMINDER_RUN_ON_START", "false").lower() == "true":
        await asyncio.sleep(60)
        try:
            await run_reminders(db)
        except Exception as e:
            logger.warning(f"[Reminders] run failed: {e}")
    while True:
        n = datetime.now(ist)
        nxt = n.replace(hour=9, minute=0, second=0, microsecond=0)
        if nxt <= n:
            nxt += timedelta(days=1)
        await asyncio.sleep((nxt - n).total_seconds())
        try:
            await run_reminders(db)
        except Exception as e:
            logger.warning(f"[Reminders] run failed: {e}")
