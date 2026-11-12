"""Daily Orders Digest — evening summary email with PDF for the CRM inbox"""
import io
import uuid
import logging
from datetime import datetime, timedelta, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))
NAVY = colors.HexColor('#1e3a5f')
LIGHT = colors.HexColor('#f4f6f8')
DIGEST_HOUR_IST = 19  # 7 PM IST


def _inr(v) -> str:
    try:
        return f"Rs. {float(v):,.2f}"
    except (TypeError, ValueError):
        return "Rs. 0.00"


def _parse_dt(value):
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return None
    return None


async def build_digest_data(db, for_date=None) -> dict:
    """Collect the day's orders (IST calendar day) + summary stats"""
    now_ist = datetime.now(IST)
    day = for_date or now_ist.date()
    day_start = datetime(day.year, day.month, day.day, tzinfo=IST)
    day_end = day_start + timedelta(days=1)

    recent = await db.orders.find({}, {"_id": 0}).sort("created_at", -1).limit(500).to_list(500)
    todays = []
    for o in recent:
        dt = _parse_dt(o.get("created_at"))
        if dt and day_start <= dt.astimezone(IST) < day_end:
            todays.append(o)

    total_revenue = sum(o.get("total_amount") or 0 for o in todays)
    paid = [o for o in todays if (o.get("payment_status") or "").lower() in ("completed", "paid", "success")]
    pending = [o for o in todays if (o.get("payment_status") or "pending").lower() not in ("completed", "paid", "success")]
    cod = [o for o in todays if (o.get("payment_method") or "").lower() in ("cod", "cash_on_delivery", "cash on delivery")]

    all_pending = await db.orders.count_documents({"payment_status": {"$nin": ["completed", "paid", "success"]}})

    return {
        "date": day.strftime("%d %b %Y"),
        "orders": todays,
        "total_orders": len(todays),
        "total_revenue": total_revenue,
        "paid_revenue": sum(o.get("total_amount") or 0 for o in paid),
        "paid_count": len(paid),
        "pending_count": len(pending),
        "pending_value": sum(o.get("total_amount") or 0 for o in pending),
        "cod_count": len(cod),
        "prepaid_count": len(todays) - len(cod),
        "all_time_pending_payments": all_pending,
    }


def build_digest_pdf(data: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm,
                            topMargin=14 * mm, bottomMargin=14 * mm)
    styles = getSampleStyleSheet()
    h = ParagraphStyle('h', parent=styles['Title'], textColor=NAVY, fontSize=17, spaceAfter=2)
    sub = ParagraphStyle('sub', parent=styles['Normal'], textColor=colors.grey, fontSize=9)
    sec = ParagraphStyle('sec', parent=styles['Heading3'], textColor=NAVY, fontSize=11, spaceBefore=10, spaceAfter=4)
    normal = styles['Normal']

    story = [
        Paragraph("ADITYA RETAIL — Daily Orders Digest", h),
        Paragraph(f"Business day: {data['date']} (IST) · Generated automatically", sub),
        Spacer(1, 8),
    ]

    stats = [
        ["Orders Today", str(data["total_orders"]), "Revenue Today", _inr(data["total_revenue"])],
        ["Payments Received", f"{data['paid_count']} ({_inr(data['paid_revenue'])})",
         "Payments Pending", f"{data['pending_count']} ({_inr(data['pending_value'])})"],
        ["COD Orders", str(data["cod_count"]), "Prepaid Orders", str(data["prepaid_count"])],
        ["All-time Pending Payments", str(data["all_time_pending_payments"]), "", ""],
    ]
    t = Table(stats, colWidths=[46 * mm, 43 * mm, 46 * mm, 43 * mm])
    t.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.grey),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d7de')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)

    story.append(Paragraph("Orders Placed Today", sec))
    if not data["orders"]:
        story.append(Paragraph("No orders were placed today.", normal))
    else:
        rows = [["Order #", "Customer", "Items", "Amount", "Payment", "Status"]]
        for o in data["orders"]:
            cust = o.get("customer_details") or {}
            rows.append([
                str(o.get("order_number") or o.get("id") or "")[:22],
                Paragraph(f"{cust.get('name') or 'Guest'}<br/><font size=7 color=grey>{cust.get('phone') or ''}</font>", normal),
                str(len(o.get("items") or [])),
                _inr(o.get("total_amount")),
                f"{(o.get('payment_method') or 'N/A').upper()}\n{(o.get('payment_status') or 'pending')}",
                str(o.get("order_status") or o.get("status") or "placed"),
            ])
        t2 = Table(rows, colWidths=[38 * mm, 52 * mm, 12 * mm, 28 * mm, 28 * mm, 20 * mm])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#d0d7de')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (2, 0), (3, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t2)

    story.append(Spacer(1, 12))
    story.append(Paragraph("Automatically generated by the Aditya Retail CRM system every evening.", sub))
    doc.build(story)
    return buf.getvalue()


async def send_daily_digest(db, force: bool = False) -> dict:
    """Build & email today's digest to the CRM inbox. Deduped per IST date unless force."""
    from crm_lead_notifier import CRM_NOTIFICATION_INBOX
    from sendgrid_email_service import sendgrid_email_service

    date_key = datetime.now(IST).strftime("%Y-%m-%d")
    if not force:
        already = await db.outgoing_emails.find_one({"tag": "daily_digest", "date_key": date_key, "status": "sent"})
        if already:
            return {"status": "skipped", "message": f"Digest already sent for {date_key}"}

    data = await build_digest_data(db)
    pdf_bytes = build_digest_pdf(data)

    body = f"""<div style="font-family:Arial,sans-serif;max-width:560px;">
<h2 style="color:#1e3a5f;">📊 Daily Orders Digest — {data['date']}</h2>
<table style="font-size:14px;color:#333;border-collapse:collapse;">
<tr><td style="padding:6px 14px 6px 0;color:#777;">Orders today</td><td><b>{data['total_orders']}</b></td></tr>
<tr><td style="padding:6px 14px 6px 0;color:#777;">Revenue today</td><td><b>₹{data['total_revenue']:,.2f}</b></td></tr>
<tr><td style="padding:6px 14px 6px 0;color:#777;">Payments received</td><td>{data['paid_count']} (₹{data['paid_revenue']:,.2f})</td></tr>
<tr><td style="padding:6px 14px 6px 0;color:#777;">Payments pending</td><td style="color:#b45309;"><b>{data['pending_count']} (₹{data['pending_value']:,.2f})</b></td></tr>
<tr><td style="padding:6px 14px 6px 0;color:#777;">COD / Prepaid</td><td>{data['cod_count']} / {data['prepaid_count']}</td></tr>
<tr><td style="padding:6px 14px 6px 0;color:#777;">All-time pending payments</td><td>{data['all_time_pending_payments']}</td></tr>
</table>
<p>Full order-by-order breakdown is attached as PDF.</p>
<p style="color:#999;font-size:12px;">Sent automatically every evening by the Aditya Retail CRM system.</p>
</div>"""

    result = sendgrid_email_service.send_email(
        to_email=CRM_NOTIFICATION_INBOX,
        subject=f"📊 Daily Orders Digest — {data['date']} · {data['total_orders']} orders · ₹{data['total_revenue']:,.0f}",
        body=body,
        from_agent="sales",
        html=True,
        attachments=[{"content": pdf_bytes, "filename": f"Daily-Digest-{date_key}.pdf", "type": "application/pdf"}],
    )
    success = bool(result and result.get("status") in ("sent", "success"))
    await db.outgoing_emails.insert_one({
        "id": str(uuid.uuid4()),
        "tag": "daily_digest",
        "date_key": date_key,
        "to": CRM_NOTIFICATION_INBOX,
        "status": "sent" if success else "failed",
        "orders": data["total_orders"],
        "revenue": data["total_revenue"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    logger.info(f"[Daily Digest] {date_key}: {'sent' if success else 'FAILED'} ({data['total_orders']} orders)")
    return {"status": "sent" if success else "failed", "date": date_key,
            "orders": data["total_orders"], "revenue": data["total_revenue"]}
