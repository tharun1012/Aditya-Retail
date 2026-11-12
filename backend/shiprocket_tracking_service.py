"""Shiprocket tracking sync — maps courier events to order statuses and notifies customers"""
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Shiprocket status text → internal order status
PROCESSING_STATES = {
    "AWB ASSIGNED", "LABEL GENERATED", "PICKUP SCHEDULED", "PICKUP QUEUED",
    "MANIFEST GENERATED", "READY TO SHIP", "PICKUP GENERATED", "INVOICED",
    "PICKUP RESCHEDULED", "PICKUP ERROR",
}
SHIPPED_STATES = {
    "SHIPPED", "PICKED UP", "IN TRANSIT", "OUT FOR DELIVERY",
    "REACHED AT DESTINATION HUB", "REACHED DESTINATION HUB", "MISROUTED",
    "OUT FOR PICKUP", "PICKED",
}
DELIVERED_STATES = {"DELIVERED"}
CANCELLED_STATES = {"CANCELED", "CANCELLED"}

STAGE_ORDER = {"processing": 1, "shipped": 2, "delivered": 3}


def map_sr_status(sr_status: str):
    """Return internal order status for a Shiprocket status text (or None if not mapped)"""
    s = (sr_status or "").strip().upper()
    if s in DELIVERED_STATES:
        return "delivered"
    if s in SHIPPED_STATES:
        return "shipped"
    if s in PROCESSING_STATES:
        return "processing"
    if s in CANCELLED_STATES:
        return "cancelled"
    if s.startswith("RTO"):
        return "shipped"  # keep as shipped; RTO noted in sr_status
    return None


def _stage_email(stage: str, order: dict, awb: str, courier: str) -> tuple:
    cust = order.get("customer_details") or {}
    name = cust.get("name") or "Customer"
    order_num = order.get("order_number") or order.get("id")
    items = "".join(
        f"<li>{(i.get('product_name') or i.get('name') or 'Item')} × {i.get('quantity', 1)}</li>"
        for i in (order.get("items") or [])
    )
    track_link = f"https://shiprocket.co/tracking/{awb}" if awb else None
    track_html = (
        f'<p style="margin:16px 0;"><a href="{track_link}" style="background:#1e3a5f;color:#fff;padding:12px 22px;'
        f'border-radius:6px;text-decoration:none;font-weight:bold;">📦 Track Your Shipment</a></p>'
        if track_link else ""
    )
    awb_html = ""
    if awb:
        awb_html = f"""<table style="font-size:14px;color:#333;background:#f4f6f8;border-radius:8px;padding:8px;width:100%;">
<tr><td style="padding:6px 12px;color:#777;">Courier Partner</td><td style="padding:6px 12px;font-weight:bold;">{courier or 'Assigned'}</td></tr>
<tr><td style="padding:6px 12px;color:#777;">AWB / Tracking No.</td><td style="padding:6px 12px;font-weight:bold;">{awb}</td></tr>
</table>"""

    if stage == "processing":
        subject = f"📦 Your order {order_num} is being prepared for dispatch!"
        headline = "Great news! Your order is packed and booked for shipping."
        note = "Our courier partner will pick it up shortly. You'll get another email with live tracking once it ships."
    elif stage == "shipped":
        subject = f"🚚 Your order {order_num} has been shipped!"
        headline = "Your order is on its way!"
        note = "You can track your shipment live using the button below."
    else:  # delivered
        subject = f"✅ Your order {order_num} has been delivered!"
        headline = "Your order has been delivered. We hope you love it!"
        note = "If anything isn't right, just reply to this email or chat with our AI Service Assistant on the website — we're here to help."

    body = f"""<div style="font-family:Arial,sans-serif;max-width:560px;">
<h2 style="color:#1e3a5f;">{headline}</h2>
<p>Dear {name},</p>
<p>Order <b>{order_num}</b>:</p>
<ul>{items}</ul>
{awb_html}
{track_html}
<p style="color:#555;">{note}</p>
<p style="color:#999;font-size:12px;margin-top:18px;">Thank you for shopping with Aditya Retail!</p>
</div>"""
    return subject, body


async def apply_tracking_update(db, order: dict, sr_status: str, awb: str = None, courier: str = None) -> dict:
    """Update an order from a Shiprocket status event + email the customer once per stage."""
    stage = map_sr_status(sr_status)
    order_num = order.get("order_number") or order.get("id")
    update = {
        "sr_status": sr_status,
        "sr_status_updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if awb:
        update["sr_awb_code"] = awb
        update["tracking_url"] = f"https://shiprocket.co/tracking/{awb}"
    if courier:
        update["sr_courier"] = courier

    current = (order.get("order_status") or "").lower()
    changed_stage = None
    if stage in ("processing", "shipped", "delivered"):
        # never move backwards (e.g. a late "processing" event after "shipped")
        if STAGE_ORDER[stage] > STAGE_ORDER.get(current, 0):
            update["order_status"] = stage
            update["status"] = stage
            changed_stage = stage
    elif stage == "cancelled" and current not in ("delivered", "cancelled"):
        update["order_status"] = "cancelled"
        update["status"] = "cancelled"

    await db.orders.update_one({"id": order.get("id")}, {"$set": update})
    if changed_stage:
        try:
            await db.orders.update_one({"id": order.get("id")}, {"$push": {"timeline": {
                "status": changed_stage, "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": f"Shipment update: {sr_status}", "updated_by": "shiprocket"}}})
            if changed_stage == "delivered":
                from customer_lifecycle import on_order_delivered
                await on_order_delivered(db, {**order, **update})
        except Exception as _lc_err:
            logger.warning(f"[SR-Track] lifecycle hook failed: {_lc_err}")

    # Customer email — once per stage
    if changed_stage:
        notified = order.get("shipping_notifications") or {}
        if not notified.get(changed_stage):
            cust_email = (order.get("customer_details") or {}).get("email")
            if cust_email:
                try:
                    from sendgrid_email_service import sendgrid_email_service
                    awb_final = awb or order.get("sr_awb_code")
                    courier_final = courier or order.get("sr_courier")
                    subject, body = _stage_email(changed_stage, order, awb_final, courier_final)
                    result = sendgrid_email_service.send_email(
                        to_email=cust_email,
                        subject=subject,
                        body=body,
                        from_agent="delivery",
                        html=True,
                    )
                    if result and result.get("status") in ("sent", "success"):
                        await db.orders.update_one(
                            {"id": order.get("id")},
                            {"$set": {f"shipping_notifications.{changed_stage}": datetime.now(timezone.utc).isoformat()}},
                        )
                        logger.info(f"[SR-Track] {order_num}: '{changed_stage}' email sent to {cust_email}")
                except Exception as e:
                    logger.warning(f"[SR-Track] email failed for {order_num}: {e}")
        logger.info(f"[SR-Track] {order_num}: {current or 'confirmed'} → {changed_stage} (SR: {sr_status})")

    return {"order": order_num, "sr_status": sr_status, "stage": changed_stage or "unchanged"}


async def poll_shiprocket_updates(db) -> dict:
    """Poll Shiprocket for all active synced orders and apply status changes."""
    import requests as _rq
    from shiprocket_routes import get_shiprocket_headers, SHIPROCKET_BASE_URL

    active = await db.orders.find({
        "shiprocket_order_id": {"$nin": [None, ""]},
        "order_status": {"$nin": ["delivered", "cancelled", "payment_failed"]},
    }, {"_id": 0}).limit(100).to_list(100)

    if not active:
        return {"checked": 0, "updated": 0}

    try:
        headers = get_shiprocket_headers()
    except Exception as e:
        logger.warning(f"[SR-Track] auth unavailable, skipping poll: {e}")
        return {"checked": 0, "updated": 0, "error": str(e)}

    checked = 0
    updated = 0
    for order in active:
        try:
            sr_id = order["shiprocket_order_id"]
            r = _rq.get(f"{SHIPROCKET_BASE_URL}/orders/show/{sr_id}", headers=headers, timeout=30)
            if r.status_code != 200:
                continue
            data = r.json().get("data") or {}
            sr_status = data.get("status") or ""
            ship = data.get("shipments") or {}
            if isinstance(ship, list):
                ship = ship[0] if ship else {}
            awb = ship.get("awb") or ship.get("awb_code")
            courier = ship.get("courier") or ship.get("courier_name")
            checked += 1
            if sr_status and sr_status != order.get("sr_status"):
                res = await apply_tracking_update(db, order, sr_status, awb, courier)
                if res.get("stage") != "unchanged":
                    updated += 1
        except Exception as e:
            logger.warning(f"[SR-Track] poll error for {order.get('order_number')}: {e}")

    if updated:
        logger.info(f"[SR-Track] poll complete: checked={checked} updated={updated}")
    return {"checked": checked, "updated": updated}
