"""
CRM Lead Notifier — sends an email to the internal CRM inbox
(dasarahalli.adityaretail@gmail.com) every time a new lead is captured
from any of these sources:
  - AI Sales Agent chat
  - AI Service Agent chat
  - AI Delivery Agent chat
  - Expert Consultation form
"""
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# The single CRM inbox that receives every new-lead notification.
# Configurable via env; defaults to the address requested by Aditya Retail.
CRM_NOTIFICATION_INBOX = os.getenv(
    "CRM_NOTIFICATION_INBOX",
    "dasarahalli.adityaretail@gmail.com",
)

# Human-readable labels per source
SOURCE_LABELS = {
    "sales": "🛒 AI Sales Agent",
    "service": "🔧 AI Service Agent",
    "delivery": "🚚 AI Delivery Agent",
    "consultation": "🎯 Expert Consultation",
}


def _fmt(v: Any) -> str:
    if v is None or v == "":
        return "—"
    if isinstance(v, list):
        return ", ".join(str(x) for x in v) or "—"
    return str(v)


def _inr(amount: Any) -> str:
    try:
        n = float(amount or 0)
    except Exception:
        n = 0.0
    # Indian number format ₹1,23,456.78
    s = f"{n:,.2f}"
    return f"₹{s}"


def _build_order_email_body(order_doc: Dict[str, Any], lead: Dict[str, Any], extra: Dict[str, Any]) -> str:
    """Render the full-order email that looks like the admin Order Details modal."""
    cust = order_doc.get("customer_details") or {}
    addr = order_doc.get("shipping_address") or {}
    items = order_doc.get("items") or []
    order_number = order_doc.get("order_number") or order_doc.get("id") or "—"

    # Line item rows
    item_rows = "".join(
        f"""
        <tr>
          <td style="padding:10px 12px;border-bottom:1px solid #f3f4f6;">
            <div style="font-weight:600;color:#111827;">{it.get('name','Product')}</div>
            {f'<div style="font-size:11px;color:#6b7280;margin-top:2px;">SKU: {it.get("sku","")}</div>' if it.get("sku") else ''}
          </td>
          <td style="padding:10px 12px;border-bottom:1px solid #f3f4f6;text-align:center;color:#374151;">{it.get('quantity', 1)}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #f3f4f6;text-align:right;color:#374151;">{_inr(it.get('price', 0))}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #f3f4f6;text-align:right;font-weight:600;color:#111827;">{_inr(float(it.get('price', 0)) * int(it.get('quantity', 1)))}</td>
        </tr>
        """
        for it in items
    )

    subtotal = order_doc.get("subtotal") or sum(float(it.get("price", 0)) * int(it.get("quantity", 1)) for it in items)
    tax_amount = order_doc.get("tax_amount") or 0
    shipping_cost = order_doc.get("shipping_cost") or 0
    total = order_doc.get("total_amount") or (subtotal + tax_amount + shipping_cost)

    payment_method = (order_doc.get("payment_method") or "COD").upper()
    payment_status = (order_doc.get("payment_status") or (order_doc.get("payment") or {}).get("status") or "pending").upper()
    payment_status_color = {
        "COMPLETED": "#059669", "PAID": "#059669", "CAPTURED": "#059669",
        "PENDING": "#d97706", "FAILED": "#dc2626",
    }.get(payment_status, "#6b7280")

    address_html = ""
    if addr:
        address_lines = [addr.get("address") or addr.get("line1", ""), addr.get("line2", "")]
        city_line = ", ".join(filter(None, [addr.get("city"), addr.get("state"), str(addr.get("pincode") or addr.get("zipcode") or "")]))
        address_lines.append(city_line)
        address_html = "<br>".join(filter(None, address_lines))

    return f"""
<!doctype html>
<html><body style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:#f3f4f6;padding:24px;color:#111827;margin:0;">
  <div style="max-width:720px;margin:0 auto;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
    <!-- Header -->
    <div style="background:linear-gradient(135deg,#065f46,#059669);color:#ffffff;padding:22px 28px;">
      <div style="font-size:11px;letter-spacing:1.5px;opacity:0.85;text-transform:uppercase;">Aditya Retail · Online Store</div>
      <div style="font-size:22px;font-weight:700;margin-top:6px;">🎉 Congratulations! New Order Received</div>
      <div style="font-size:14px;margin-top:6px;opacity:0.95;">Order <strong>{order_number}</strong> · {_inr(total)} · {payment_method}</div>
    </div>

    <!-- Top summary strip -->
    <div style="padding:16px 28px;background:#f0fdf4;border-bottom:1px solid #d1fae5;display:flex;justify-content:space-between;font-size:12px;color:#065f46;">
      <div><strong>Payment Status:</strong> <span style="color:{payment_status_color};font-weight:700;">{payment_status}</span></div>
      <div><strong>Items:</strong> {len(items)}</div>
      <div><strong>Amount:</strong> {_inr(total)}</div>
    </div>

    <div style="padding:24px 28px;">
      <!-- 2-column: Customer & Order Info -->
      <table style="width:100%;border-collapse:collapse;margin-bottom:20px;">
        <tr>
          <td style="vertical-align:top;width:50%;padding-right:12px;">
            <h3 style="margin:0 0 10px;font-size:14px;color:#111827;text-transform:uppercase;letter-spacing:0.5px;">Customer Information</h3>
            <div style="font-size:15px;font-weight:700;color:#111827;">{cust.get('name','Customer')}</div>
            <div style="font-size:13px;color:#6b7280;margin-top:4px;">📧 <a href="mailto:{cust.get('email','')}" style="color:#2563eb;">{cust.get('email','—')}</a></div>
            <div style="font-size:13px;color:#6b7280;margin-top:4px;">📞 <a href="tel:{cust.get('phone','')}" style="color:#2563eb;">{cust.get('phone','—')}</a></div>
          </td>
          <td style="vertical-align:top;width:50%;padding-left:12px;border-left:1px solid #e5e7eb;">
            <h3 style="margin:0 0 10px;font-size:14px;color:#111827;text-transform:uppercase;letter-spacing:0.5px;">Order Information</h3>
            <div style="font-size:13px;color:#374151;line-height:1.7;">
              <div><strong>Order #:</strong> {order_number}</div>
              <div><strong>Order ID:</strong> <span style="font-family:monospace;font-size:11px;">{order_doc.get('id','—')}</span></div>
              <div><strong>Date:</strong> {order_doc.get('created_at','—')[:19].replace('T',' ')}</div>
              <div><strong>Status:</strong> <span style="text-transform:capitalize;">{order_doc.get('order_status') or order_doc.get('status','placed')}</span></div>
            </div>
          </td>
        </tr>
      </table>

      <!-- Shipping Address -->
      <div style="margin-bottom:20px;">
        <h3 style="margin:0 0 8px;font-size:14px;color:#111827;text-transform:uppercase;letter-spacing:0.5px;">Shipping Address</h3>
        <div style="font-size:13px;color:#374151;line-height:1.6;background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:12px 14px;">{address_html or '—'}</div>
      </div>

      <!-- Payment Info -->
      <div style="margin-bottom:20px;">
        <h3 style="margin:0 0 8px;font-size:14px;color:#111827;text-transform:uppercase;letter-spacing:0.5px;">Payment Information</h3>
        <div style="font-size:13px;color:#374151;line-height:1.7;">
          <div><strong>Method:</strong> {payment_method}</div>
          <div><strong>Status:</strong> <span style="display:inline-block;padding:2px 10px;border-radius:12px;background:{payment_status_color}22;color:{payment_status_color};font-weight:600;font-size:11px;text-transform:uppercase;">{payment_status}</span></div>
          {f'<div><strong>Transaction ID:</strong> <span style="font-family:monospace;font-size:11px;">{(order_doc.get("payment") or {}).get("transaction_id","")}</span></div>' if (order_doc.get("payment") or {}).get("transaction_id") else ''}
        </div>
      </div>

      <!-- Order Items -->
      <h3 style="margin:0 0 8px;font-size:14px;color:#111827;text-transform:uppercase;letter-spacing:0.5px;">Order Items</h3>
      <table style="width:100%;border-collapse:collapse;background:#ffffff;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
        <thead>
          <tr style="background:#f9fafb;">
            <th style="text-align:left;padding:10px 12px;font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;">Product</th>
            <th style="text-align:center;padding:10px 12px;font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;">Qty</th>
            <th style="text-align:right;padding:10px 12px;font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;">Price</th>
            <th style="text-align:right;padding:10px 12px;font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;">Total</th>
          </tr>
        </thead>
        <tbody>
          {item_rows or '<tr><td colspan="4" style="padding:20px;text-align:center;color:#9ca3af;">No items</td></tr>'}
        </tbody>
        <tfoot>
          <tr>
            <td colspan="3" style="padding:8px 12px;text-align:right;font-size:13px;color:#6b7280;border-top:1px solid #e5e7eb;">Subtotal</td>
            <td style="padding:8px 12px;text-align:right;font-size:13px;color:#374151;border-top:1px solid #e5e7eb;">{_inr(subtotal)}</td>
          </tr>
          <tr>
            <td colspan="3" style="padding:6px 12px;text-align:right;font-size:13px;color:#6b7280;">Tax (18%)</td>
            <td style="padding:6px 12px;text-align:right;font-size:13px;color:#374151;">{_inr(tax_amount)}</td>
          </tr>
          <tr>
            <td colspan="3" style="padding:6px 12px;text-align:right;font-size:13px;color:#6b7280;">Shipping</td>
            <td style="padding:6px 12px;text-align:right;font-size:13px;color:#374151;">{_inr(shipping_cost)}</td>
          </tr>
          <tr style="background:#f0fdf4;">
            <td colspan="3" style="padding:12px 12px;text-align:right;font-weight:700;font-size:15px;color:#065f46;border-top:2px solid #d1fae5;">Total</td>
            <td style="padding:12px 12px;text-align:right;font-weight:700;font-size:15px;color:#065f46;border-top:2px solid #d1fae5;">{_inr(total)}</td>
          </tr>
        </tfoot>
      </table>
    </div>

    <div style="padding:16px 28px;background:#f9fafb;border-top:1px solid #e5e7eb;font-size:12px;color:#6b7280;">
      This order has been auto-recorded in your CRM and pushed to Shiprocket. Log in to the admin dashboard for full details.
    </div>
  </div>
</body></html>
""".strip()


def _build_email_body(lead: Dict[str, Any], source: str, extra: Optional[Dict[str, Any]] = None) -> str:
    """Build a clean HTML body for the notification email."""
    src_label = SOURCE_LABELS.get(source, source or "Lead")
    extra = extra or {}

    # If this is an ORDER (extra.order_doc set), render the full order-details layout
    order_doc: Optional[Dict[str, Any]] = extra.get("order_doc") if isinstance(extra, dict) else None
    if order_doc:
        return _build_order_email_body(order_doc, lead, extra)

    rows = [
        ("Name", lead.get("name") or lead.get("customer_name")),
        ("Email", lead.get("email")),
        ("Phone", lead.get("phone")),
        ("Source", src_label),
        ("Status", lead.get("status")),
        ("Lead ID", lead.get("id")),
    ]

    # Optional context fields per source
    if source == "consultation":
        rows.extend([
            ("Budget", f"₹{lead.get('budget_min', 0):,} – ₹{lead.get('budget_max', 0):,}" if lead.get("budget_min") else None),
            ("Appliances", lead.get("appliance_interests")),
            ("Brand Preference", lead.get("brand_preference")),
            ("Kitchen Size", extra.get("kitchen_size")),
        ])
    else:
        rows.extend([
            ("Interested Products", lead.get("interested_products")),
            ("Budget Range", lead.get("budget_range")),
            ("Buying Timeline", lead.get("buying_timeline")),
            ("Key Concerns", lead.get("key_concerns")),
        ])

    # Notes / conversation summary (kept for future use; excerpt is rendered below)
    _ = lead.get("notes") or extra.get("summary")

    row_html = "".join(
        f'<tr><td style="padding:6px 12px;font-weight:600;color:#374151;white-space:nowrap;">{k}</td>'
        f'<td style="padding:6px 12px;color:#111827;">{_fmt(v)}</td></tr>'
        for k, v in rows if v is not None
    )

    conversation_html = ""
    if extra.get("conversation_excerpt"):
        conversation_html = (
            '<h3 style="margin:24px 0 8px;color:#111827;font-size:14px;">💬 Recent Conversation</h3>'
            f'<pre style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:12px;'
            'font-family:ui-monospace,Menlo,monospace;font-size:12px;color:#374151;white-space:pre-wrap;">'
            f'{extra["conversation_excerpt"]}</pre>'
        )

    consultation_html = ""
    if source == "consultation" and extra.get("consultation_details"):
        consultation_html = (
            '<h3 style="margin:24px 0 8px;color:#111827;font-size:14px;">📋 Expert Consultation Details</h3>'
            f'<pre style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:12px;'
            'font-family:ui-monospace,Menlo,monospace;font-size:12px;color:#1e3a8a;white-space:pre-wrap;">'
            f'{extra["consultation_details"]}</pre>'
        )

    return f"""
<!doctype html>
<html><body style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:#f3f4f6;padding:24px;color:#111827;">
  <div style="max-width:640px;margin:0 auto;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
    <div style="background:linear-gradient(135deg,#0f172a,#1e40af);color:#ffffff;padding:20px 24px;">
      <div style="font-size:12px;letter-spacing:1px;opacity:0.75;text-transform:uppercase;">Aditya Retail CRM</div>
      <div style="font-size:20px;font-weight:700;margin-top:4px;">New Lead Captured</div>
      <div style="font-size:13px;margin-top:4px;opacity:0.9;">{src_label}</div>
    </div>
    <div style="padding:20px 24px;">
      <table style="width:100%;border-collapse:collapse;font-size:13px;">
        {row_html}
      </table>
      {consultation_html}
      {conversation_html}
    </div>
    <div style="padding:16px 24px;background:#f9fafb;border-top:1px solid #e5e7eb;font-size:12px;color:#6b7280;">
      This lead has been auto-saved to your CRM. Reply directly to the customer or open the Leads dashboard to follow up.
    </div>
  </div>
</body></html>
""".strip()


def notify_new_lead(
    lead: Dict[str, Any],
    source: str,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Send a notification email to the CRM inbox that a new lead was captured.

    Args:
        lead: The lead document that was inserted into db.leads.
        source: One of 'sales' | 'service' | 'delivery' | 'consultation'.
        extra: Optional additional context (e.g. conversation excerpt, consultation form data).

    Returns:
        {"status": "sent" | "skipped" | "error", "message": str}
    """
    try:
        # Lazy import so this module can be imported without breaking anything
        # if sendgrid_email_service fails to configure at boot.
        from sendgrid_email_service import sendgrid_email_service

        name = lead.get("name") or lead.get("customer_name") or "Anonymous Visitor"
        email = lead.get("email") or "—"
        src_label = SOURCE_LABELS.get(source, source or "Lead")
        # Special-case: full order confirmation gets a celebratory subject
        if (extra or {}).get("order_doc"):
            order_num = (extra["order_doc"].get("order_number") or extra["order_doc"].get("id") or "").upper()
            total_amt = _inr(extra["order_doc"].get("total_amount") or 0)
            subject = f"🎉 Congratulations! New Order Received — {order_num} · {total_amt}"
        else:
            subject = f"🔔 New Lead — {name} ({email}) via {src_label}"
        body_html = _build_email_body(lead, source, extra)

        # Attach a PDF order copy when this notification is for an actual order
        attachments = None
        if (extra or {}).get("order_doc"):
            try:
                from order_pdf_generator import build_order_pdf
                order_doc = extra["order_doc"]
                pdf_bytes = build_order_pdf(order_doc)
                order_num = (order_doc.get("order_number") or order_doc.get("id") or "order")
                attachments = [{
                    "content": pdf_bytes,
                    "filename": f"Order-{order_num}.pdf",
                    "type": "application/pdf",
                }]
            except Exception as _pdf_e:
                logger.warning(f"Order PDF generation failed (email sent without attachment): {_pdf_e}")

        # Use the sales SendGrid identity so the CRM inbox sees the mail land from a known Aditya sender.
        result = sendgrid_email_service.send_email(
            to_email=CRM_NOTIFICATION_INBOX,
            subject=subject,
            body=body_html,
            from_agent="sales",
            html=True,
            attachments=attachments,
        )
        if result and result.get("status") in ("sent", "success"):
            logger.info(f"CRM lead notification sent for {name} <{email}> via {source}")
            return {"status": "sent", "message": "Notification email delivered"}
        logger.warning(f"CRM lead notification failed for {name}: {result}")
        return {"status": "error", "message": str(result)}
    except Exception as e:
        logger.error(f"notify_new_lead failed: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
