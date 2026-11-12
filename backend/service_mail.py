import os, re, html, asyncio
from datetime import datetime, timezone
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Cc, Bcc
from sendgrid_email_service import sendgrid_email_service

WHAT = {
    "installation": "Request for Installation And Demo",
    "repair": "Request for Repair",
    "warranty": "Warranty Claim Request",
    "general": "Service Request",
}
STYPE = {"installation": "INS", "repair": "REPAIR", "warranty": "WARRANTY", "general": "GENERAL"}
MODEL_RE = re.compile(r"\b(?=[A-Z0-9\-]*\d)(?=[A-Z0-9\-]*[A-Z])[A-Z0-9\-]{6,}\b")


def detect_brand(text):
    t = (text or "").lower()
    if "bosch" in t:
        return "Bosch"
    if "siemens" in t:
        return "Siemens"
    return ""


def detect_model(text):
    m = MODEL_RE.search((text or "").upper())
    return m.group(0) if m else ""


def _addr(a):
    if not a:
        return "", "", ""
    if isinstance(a, str):
        return a, "", ""
    keys = ["address_line1", "line1", "address", "street", "address_line2", "line2", "landmark", "area"]
    parts = [str(a.get(k)) for k in keys if a.get(k)]
    city = a.get("city") or "Bangalore"
    pin = a.get("pincode") or a.get("postal_code") or a.get("zip") or ""
    if a.get("state"):
        parts.append(str(a["state"]))
    return ", ".join(parts), city, str(pin)


def _table(c):
    e = lambda v: html.escape(str(v or ""))
    heads = ["Ticket No", "Date", "Category", "Brand", "Model", "Pincode", "City", "Qty", "Customer Name",
             "Address", "Phone", "Service Type", "Issue Details", "Preferred Date / Slot"]
    th = "".join(f'<th style="border:1px solid #000;padding:4px;background:#f3f3f3">{e(h)}</th>' for h in heads)
    items = c.get("items") or [{"product_name": c["product_name"], "model": c["model"], "qty": 1}]
    trs = ""
    for it in items:
        vals = [c["ticket_number"], c["date"], it.get("product_name"), c["brand"], it.get("model"), c["pincode"], c["city"],
                it.get("qty") or 1, c["customer_name"], c["address"], c["phone"], c["stype"], c["details"], c["slot"]]
        trs += "<tr>" + "".join(f'<td style="border:1px solid #000;padding:4px">{e(v)}</td>' for v in vals) + "</tr>"
    return f'<table style="border-collapse:collapse;font-size:13px"><tr>{th}</tr>{trs}</table>'


def _send(to, cc, reply_to, subject, body):
    acct = sendgrid_email_service.email_accounts["service"]
    msg = Mail(from_email=Email(os.environ.get("SERVICE_FROM_EMAIL") or acct["email"], acct["display_name"]), to_emails=To(to),
               subject=subject, html_content=body)
    copy_to = (os.environ.get("SERVICE_COPY_TO") or "").strip()
    if copy_to and copy_to.lower() != to.lower():
        msg.add_bcc(Bcc(copy_to))
    msg.reply_to = Email(reply_to)
    resp = SendGridAPIClient(sendgrid_email_service.api_key).send(msg)
    return resp.status_code


async def send_company_mail(database, ticket, registered_product, user):
    rp = registered_product or {}
    text = " ".join([str(ticket.get("product_name") or ""), str(rp.get("brand") or rp.get("brand_name") or "")])
    brand = (ticket.get("brand_choice") or rp.get("brand") or rp.get("brand_name") or detect_brand(text) or "").title()
    model = rp.get("model_number") or rp.get("model") or detect_model(ticket.get("product_name"))
    test = os.environ.get("SERVICE_TEST_MODE", "0") == "1"

    if test:
        to = os.environ["SERVICE_TEST_COMPANY_EMAIL"]
        cc = os.environ["SERVICE_TEST_CC"]
        reply_to = cc
    else:
        to = sendgrid_email_service.get_brand_email(brand) if brand else None
        cc = os.environ.get("SERVICE_EMAIL")
        reply_to = cc

    if not to:
        await database.service_tickets.update_one(
            {"ticket_number": ticket["ticket_number"]},
            {"$set": {"brand": brand, "model": model, "company_mail_status": "brand_unknown"}})
        try:
            alert_to = (os.environ.get("SERVICE_COPY_TO") or "").strip()
            if alert_to:
                note = (f"<p>Ticket {html.escape(str(ticket['ticket_number']))} was not sent to any brand because Bosch or Siemens could not be identified.</p>"
                        f"<p>Product: {html.escape(str(ticket.get('product_name') or ''))}<br>"
                        f"Customer: {html.escape(str(ticket.get('customer_name') or ''))} / {html.escape(str(ticket.get('customer_phone') or ''))}</p>"
                        "<p>Please send this request to the brand manually.</p>")
                await asyncio.to_thread(_send, alert_to, None, alert_to,
                                        f"[{ticket['ticket_number']}] ACTION NEEDED: brand not recognised", note)
        except Exception:
            pass
        return

    addr = None
    try:
        rows = await database.customer_addresses.find({"user_id": ticket["user_id"]}, {"_id": 0}).to_list(None)
        addr = next((r for r in rows if r.get("is_default")), rows[-1] if rows else None)
    except Exception:
        pass
    address, city, pincode = _addr(addr or user.get("address"))
    issue = ticket.get("issue_type") or "general"
    what = WHAT.get(issue, "Service Request")
    c = {
        "ticket_number": ticket["ticket_number"],
        "date": datetime.now(timezone.utc).strftime("%d-%m-%Y"),
        "product_name": ticket.get("product_name"), "brand": brand or "Unknown", "model": model,
        "pincode": pincode, "city": city, "customer_name": ticket.get("customer_name"),
        "address": address, "phone": ticket.get("customer_phone"), "stype": STYPE.get(issue, "GENERAL"),
        "details": "" if issue == "installation" else ticket.get("issue_description"),
        "slot": f'{ticket.get("preferred_date") or ""} {ticket.get("preferred_time_slot") or ""}'.strip(),
    }
    if ticket.get("products"):
        c["items"] = [{"product_name": p.get("product_name"), "model": p.get("model") or detect_model(p.get("product_name")) or (model if n == 0 else ""), "qty": p.get("qty") or 1} for n, p in enumerate(ticket["products"])]
    subject = f"[{ticket['ticket_number']}] {what}"
    store_sig = (f"<br>Raised by store: {html.escape(str(ticket.get('store_name') or ''))} ({html.escape(str(ticket.get('store_code') or ''))})" if ticket.get("store_code") else "")
    body = (f"<p>Dear Sir,</p><p>Please find the customer details below for {html.escape(what)}.</p>"
            f"{_table(c)}<p>Thanks &amp; Regards,<br>Aditya Retail{store_sig}</p>")

    status, err = "sent", ""
    try:
        await asyncio.to_thread(_send, to, cc, reply_to, subject, body)
    except Exception as ex:
        status, err = "failed", str(ex)

    upd = {"brand": brand, "model": model, "company_mail_status": status, "company_mail_to": to,
           "company_mail_cc": cc, "company_mail_subject": subject, "company_mail_error": err,
           "company_mail_sent_at": datetime.now(timezone.utc).isoformat()}
    if status == "sent":
        upd["status"] = "awaiting_brand_response"
    await database.service_tickets.update_one({"ticket_number": ticket["ticket_number"]}, {"$set": upd})
    await database.service_ticket_messages.insert_one({
        "ticket_number": ticket["ticket_number"], "direction": "out", "subject": subject, "to": to,
        "cc": cc, "status": status, "error": err, "at": datetime.now(timezone.utc).isoformat()})
