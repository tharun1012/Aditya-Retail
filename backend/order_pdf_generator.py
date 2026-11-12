"""Order PDF generator — invoice-style order summary for CRM emails"""
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

NAVY = colors.HexColor('#1e3a5f')
LIGHT = colors.HexColor('#f4f6f8')


def _inr(v) -> str:
    try:
        return f"Rs. {float(v):,.2f}"
    except (TypeError, ValueError):
        return "Rs. 0.00"


def build_order_pdf(order_doc: dict) -> bytes:
    """Build a PDF order summary and return raw bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=16 * mm)
    styles = getSampleStyleSheet()
    h_style = ParagraphStyle('h', parent=styles['Title'], textColor=NAVY, fontSize=18, spaceAfter=2)
    sub_style = ParagraphStyle('sub', parent=styles['Normal'], textColor=colors.grey, fontSize=9)
    sec_style = ParagraphStyle('sec', parent=styles['Heading3'], textColor=NAVY, fontSize=11, spaceBefore=10, spaceAfter=4)
    normal = styles['Normal']

    cust = order_doc.get('customer_details') or {}
    addr = order_doc.get('shipping_address') or {}
    order_num = order_doc.get('order_number') or order_doc.get('id') or 'N/A'
    created = str(order_doc.get('created_at') or datetime.now().isoformat())[:19].replace('T', ' ')

    story = [
        Paragraph("ADITYA RETAIL", h_style),
        Paragraph("Order Summary (Internal CRM Copy)", sub_style),
        Spacer(1, 6),
    ]

    meta = [
        ["Order Number:", order_num, "Order Date:", created],
        ["Payment Method:", str(order_doc.get('payment_method') or 'N/A').upper(),
         "Payment Status:", str(order_doc.get('payment_status') or 'pending').upper()],
        ["Order Status:", str(order_doc.get('order_status') or order_doc.get('status') or 'placed').upper(),
         "Shiprocket:", str(order_doc.get('shiprocket_order_id') or 'Not synced')],
    ]
    t = Table(meta, colWidths=[32 * mm, 55 * mm, 32 * mm, 55 * mm])
    t.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)

    story.append(Paragraph("Customer Details", sec_style))
    cust_rows = [
        ["Name:", cust.get('name') or 'N/A', "Phone:", cust.get('phone') or 'N/A'],
        ["Email:", cust.get('email') or 'N/A', "", ""],
    ]
    addr_line = ", ".join(str(x) for x in [
        addr.get('address') or addr.get('address_line1'), addr.get('city'),
        addr.get('state'), addr.get('pincode')] if x)
    if addr_line:
        cust_rows.append(["Delivery:", addr_line, "", ""])
    t2 = Table(cust_rows, colWidths=[22 * mm, 90 * mm, 18 * mm, 44 * mm])
    t2.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('SPAN', (1, -1), (3, -1)) if addr_line else ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t2)

    story.append(Paragraph("Items", sec_style))
    item_rows = [["#", "Product", "Qty", "Unit Price", "Total"]]
    for idx, item in enumerate(order_doc.get('items') or [], 1):
        name = item.get('product_name') or item.get('name') or 'Item'
        qty = item.get('quantity') or 1
        price = item.get('price') or item.get('unit_price') or 0
        total = item.get('total') or (float(price or 0) * int(qty))
        item_rows.append([str(idx), Paragraph(str(name), normal), str(qty), _inr(price), _inr(total)])
    t3 = Table(item_rows, colWidths=[10 * mm, 92 * mm, 14 * mm, 29 * mm, 29 * mm])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#d0d7de')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t3)

    totals = [
        ["Subtotal", _inr(order_doc.get('subtotal') or order_doc.get('total_amount') or 0)],
    ]
    if order_doc.get('discount_amount'):
        totals.append(["Discount", f"- {_inr(order_doc['discount_amount'])}"])
    if order_doc.get('tax_amount'):
        totals.append(["Tax (GST)", _inr(order_doc['tax_amount'])])
    if order_doc.get('shipping_cost'):
        totals.append(["Shipping", _inr(order_doc['shipping_cost'])])
    totals.append(["GRAND TOTAL", _inr(order_doc.get('total_amount') or 0)])
    t4 = Table(totals, colWidths=[135 * mm, 39 * mm])
    t4.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, -1), (-1, -1), NAVY),
        ('LINEABOVE', (0, -1), (-1, -1), 0.8, NAVY),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(Spacer(1, 4))
    story.append(t4)
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "This is an automatically generated internal order copy from the Aditya Retail CRM system.",
        sub_style))

    doc.build(story)
    return buf.getvalue()
