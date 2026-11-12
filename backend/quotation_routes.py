import asyncio
"""
Quotation Management Routes
Handles quotation generation, PDF export, email, and WhatsApp sharing
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from database import get_db
from pydantic import BaseModel, EmailStr
import uuid
import io
import os
import logging
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Import document numbering helper
from document_numbering_routes import get_next_document_number, initialize_store_numbering

router = APIRouter(prefix="/quotations", tags=["Quotations"])
logger = logging.getLogger(__name__)

# Register Unicode-capable fonts so ₹ (Rupee) and other non-ASCII
# characters render correctly in generated PDFs (Helvetica has no ₹ glyph)
DEJAVU_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

if os.path.exists(DEJAVU_REGULAR) and os.path.exists(DEJAVU_BOLD):
    pdfmetrics.registerFont(TTFont("DejaVu", DEJAVU_REGULAR))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", DEJAVU_BOLD))
    PDF_FONT = "DejaVu"
    PDF_FONT_BOLD = "DejaVu-Bold"
else:
    logger.warning("DejaVu fonts not found - currency symbols may not render correctly")
    PDF_FONT = "Helvetica"
    PDF_FONT_BOLD = "Helvetica-Bold"

# ============ MODELS ============

class QuotationItem(BaseModel):
    product_id: Optional[str] = None  # None for manually-entered items
    brand: str = ""
    model_number: str = ""
    product_name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    mrp: float
    offer_price: float
    quantity: int = 1
    is_manual_entry: bool = False

class QuotationCreate(BaseModel):
    store_id: str
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    items: List[QuotationItem]
    terms_and_conditions: Optional[str] = None
    validity_days: int = 15
    notes: Optional[str] = None
    discount_percent: float = 0
    include_gst: bool = True

class QuotationUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    items: Optional[List[QuotationItem]] = None
    terms_and_conditions: Optional[str] = None
    validity_days: Optional[int] = None
    notes: Optional[str] = None
    discount_percent: Optional[float] = None
    status: Optional[str] = None

class EmailQuotation(BaseModel):
    to_email: EmailStr
    subject: Optional[str] = None
    message: Optional[str] = None

# Default Terms and Conditions
DEFAULT_TERMS = """
1. This quotation is valid for {validity_days} days from the date of issue.
2. Prices are inclusive of GST unless otherwise specified.
3. Delivery charges may apply based on location.
4. Payment terms: 100% advance for free-standing products; 50% advance and balance before dispatch for built-in products.
5. Installation charges (if applicable) will be communicated separately.
6. Warranty as per manufacturer's policy.
7. Prices are subject to change without prior notice.
8. E&OE (Errors and Omissions Excepted)
"""

# ============ HELPER FUNCTIONS ============

def calculate_quotation_totals(items: List[dict], discount_percent: float = 0, include_gst: bool = True):
    """Calculate quotation totals"""
    subtotal = sum(item["offer_price"] * item["quantity"] for item in items)
    discount_amount = subtotal * (discount_percent / 100)
    gross_amount = subtotal - discount_amount  # already GST-inclusive

    if include_gst:
        taxable_amount = gross_amount / 1.18
        total_gst = gross_amount - taxable_amount
        cgst = total_gst / 2
        sgst = total_gst / 2
    else:
        taxable_amount = gross_amount
        cgst = 0
        sgst = 0
        total_gst = 0

    grand_total = gross_amount  # GST extracted, not added on top
    
    # Calculate savings
    total_mrp = sum(item["mrp"] * item["quantity"] for item in items)
    savings = total_mrp - grand_total
    
    return {
        "subtotal": round(subtotal, 2),
        "discount_percent": discount_percent,
        "discount_amount": round(discount_amount, 2),
        "taxable_amount": round(taxable_amount, 2),
        "cgst": round(cgst, 2),
        "sgst": round(sgst, 2),
        "total_gst": round(total_gst, 2),
        "grand_total": round(grand_total, 2),
        "total_mrp": round(total_mrp, 2),
        "total_savings": round(savings, 2)
    }

async def generate_quotation_pdf(quotation: dict) -> bytes:
    """Generate PDF for quotation with proper store details and formatting"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    import aiohttp
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=15*mm, bottomMargin=15*mm, leftMargin=15*mm, rightMargin=15*mm)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, fontName=PDF_FONT_BOLD, alignment=TA_CENTER, spaceAfter=5, textColor=colors.HexColor('#2C3E50'))
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=11, fontName=PDF_FONT, alignment=TA_CENTER, textColor=colors.grey)
    header_style = ParagraphStyle('Header', parent=styles['Heading2'], fontSize=12, fontName=PDF_FONT_BOLD, spaceAfter=5, textColor=colors.HexColor('#2C3E50'))
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=9, fontName=PDF_FONT, leading=12)
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=8, fontName=PDF_FONT, textColor=colors.grey, leading=10)
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=9, fontName=PDF_FONT_BOLD)
    
    elements = []
    
    # Get store details from quotation
    store_name = quotation.get('store_name', 'Aditya Retail')
    store_address = quotation.get('store_address', '')
    store_phone = quotation.get('store_phone', '')
    store_gst = quotation.get('store_gst', '')
    
    # Header with Store Name
    # Add company logo above the QUOTATION title
    logo_path = "/app/frontend/public/aditya-logo.png"
    if os.path.exists(logo_path):
        logo_img = Image(logo_path, width=120, height=41)
        logo_img.hAlign = "CENTER"
        elements.append(logo_img)
        elements.append(Spacer(1, 8))
    elements.append(Paragraph("QUOTATION", title_style))
    elements.append(Paragraph(store_name, subtitle_style))
    if store_address:
        elements.append(Paragraph(store_address, small_style))
    if store_phone:
        elements.append(Paragraph(f"Phone: {store_phone}", small_style))
    if store_gst:
        elements.append(Paragraph(f"GSTIN: {store_gst}", small_style))
    elements.append(Spacer(1, 15))
    
    # Quotation Info in a box
    info_data = [
        ["Quotation No:", quotation["quotation_number"], "Date:", quotation["created_at"][:10]],
        ["Valid Until:", quotation["valid_until"][:10], "Store Code:", quotation.get("store_code", "HQ")]
    ]
    info_table = Table(info_data, colWidths=[80, 150, 80, 150])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), PDF_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), PDF_FONT_BOLD),
        ('FONTNAME', (2, 0), (2, -1), PDF_FONT_BOLD),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))
    
    # Customer Info
    elements.append(Paragraph("Customer Details", header_style))
    customer_info = f"""
    <b>Name:</b> {quotation['customer_name']}<br/>
    <b>Phone:</b> {quotation.get('customer_phone', 'N/A')}<br/>
    <b>Email:</b> {quotation.get('customer_email', 'N/A')}<br/>
    <b>Address:</b> {quotation.get('customer_address', 'N/A')}
    """
    elements.append(Paragraph(customer_info, normal_style))
    elements.append(Spacer(1, 15))
    
    # Items Table
    elements.append(Paragraph("Product Details", header_style))
    
    # Table header - adjusted column widths for better text display (added Image column)
    table_data = [["#", "Image", "Product Details", "MRP", "Offer Price", "Qty", "Total"]]

    async def fetch_product_image(url, max_w=36, max_h=36):
        """Fetch a product image and return a ReportLab Image flowable sized
        to fit within max_w x max_h (points), preserving aspect ratio.
        Returns None if the URL is missing or the fetch/decode fails, so the
        caller can fall back to a placeholder without breaking PDF generation."""
        if not url:
            return None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                    if resp.status != 200:
                        return None
                    img_bytes = await resp.read()
            img_buffer = io.BytesIO(img_bytes)
            from PIL import Image as PILImage
            pil_img = PILImage.open(img_buffer)
            pil_img = pil_img.convert("RGB")
            orig_w, orig_h = pil_img.size
            scale = min(max_w / orig_w, max_h / orig_h)
            target_w = max(1, int(orig_w * scale * 2))
            target_h = max(1, int(orig_h * scale * 2))
            pil_img = pil_img.resize((target_w, target_h), PILImage.LANCZOS)
            resized_buffer = io.BytesIO()
            pil_img.save(resized_buffer, format="JPEG", quality=80, optimize=True)
            resized_buffer.seek(0)
            return Image(resized_buffer, width=orig_w * scale, height=orig_h * scale)
        except Exception as e:
            logging.warning(f"Quotation PDF: failed to fetch product image {url}: {e}")
            return None

    # Fetch all product images concurrently instead of one at a time —
    # cuts PDF generation time roughly from N * (up to 8s) down to ~max 8s total.
    image_flowables = await asyncio.gather(
        *(fetch_product_image(item.get('image_url')) for item in quotation["items"]),
        return_exceptions=True
    )

    for idx, (item, image_flowable) in enumerate(zip(quotation["items"], image_flowables), 1):
        # Format product details with proper line breaks
        brand = item.get('brand') or ''
        model = item.get('model_number') or ''
        product_name = item.get('product_name') or ''
        
        # Truncate description if too long (guard against None from DB)
        description = item.get('description') or product_name or ''
        if len(description) > 80:
            description = description[:77] + "..."
        
        product_details = f"<b>{brand}</b><br/>{model}<br/><font size='7'>{description}</font>"
        
        total = item['offer_price'] * item['quantity']

        if isinstance(image_flowable, Exception) or not image_flowable:
            image_cell = Paragraph("<font size='7' color='grey'>No image</font>", small_style)
        else:
            image_cell = image_flowable

        table_data.append([
            str(idx),
            image_cell,
            Paragraph(product_details, normal_style),
            f"₹{item['mrp']:,.0f}",
            f"₹{item['offer_price']:,.0f}",
            str(item['quantity']),
            f"₹{total:,.0f}"
        ])
    
    # Create table with better column widths (added Image column, same total width as before)
    col_widths = [25, 45, 175, 65, 75, 35, 75]
    items_table = Table(table_data, colWidths=col_widths)
    items_table.setStyle(TableStyle([
        ('FONTNAME', (0, 1), (-1, -1), PDF_FONT),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), PDF_FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (5, 1), (5, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 15))
    
    # Totals
    totals = quotation["totals"]
    totals_data = [
        ["Subtotal (MRP):", f"₹{totals['total_mrp']:,.2f}"],
        ["Your Price:", f"₹{totals['subtotal']:,.2f}"],
    ]
    
    if totals["discount_amount"] > 0:
        totals_data.append([f"Discount ({totals['discount_percent']}%):", f"-₹{totals['discount_amount']:,.2f}"])
    
    if quotation.get("include_gst", True):
        totals_data.append(["CGST (9%):", f"₹{totals['cgst']:,.2f}"])
        totals_data.append(["SGST (9%):", f"₹{totals['sgst']:,.2f}"])
    
    totals_data.append(["Grand Total:", f"₹{totals['grand_total']:,.2f}"])
    totals_data.append(["You Save:", f"₹{totals['total_savings']:,.2f}"])
    
    totals_table = Table(totals_data, colWidths=[380, 100])
    totals_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), PDF_FONT),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, -2), (-1, -2), PDF_FONT_BOLD),
        ('FONTNAME', (0, -1), (-1, -1), PDF_FONT_BOLD),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#27AE60')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEABOVE', (0, -2), (-1, -2), 1, colors.black),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 20))
    
    # Bank Details
    elements.append(Paragraph("Bank Details for Payment", header_style))
    elements.append(Paragraph("Bank Name: DBS Bank | Account Name: Aditya Retail | A/C No: 827200176347", small_style))
    elements.append(Paragraph("IFSC Code: DBSS0IN0827 | Branch: Ulsoor Road, Bangalore | Account Type: Current Account", small_style))
    elements.append(Paragraph("GST: 29ABAFA6295J1Z2", small_style))
    elements.append(Spacer(1, 12))
    
    # Terms and Conditions
    elements.append(Paragraph("Terms & Conditions", header_style))
    terms = quotation.get("terms_and_conditions", DEFAULT_TERMS.format(validity_days=quotation.get("validity_days", 15)))
    for line in terms.strip().split('\n'):
        if line.strip():
            elements.append(Paragraph(line.strip(), small_style))
    
    elements.append(Spacer(1, 20))
    
    # Footer
    footer_text = """
    <b>Aditya Retail</b> - Premium Bosch, Siemens & Hindware Products<br/>
    Contact: +91-9876543210 | Email: sales@adityaretail.com<br/>
    Website: www.adityaretail.com
    """
    elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# ============ ROUTES ============

@router.post("/create")
async def create_quotation(
    quotation: QuotationCreate,
    db = Depends(get_db)
):
    """Create a new quotation"""
    try:
        # Verify store exists
        store = await db.stores.find_one({"id": quotation.store_id})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Initialize numbering if needed
        await initialize_store_numbering(db, quotation.store_id, store["code"])
        
        # Generate quotation number
        quotation_number = await get_next_document_number(
            db, quotation.store_id, store["code"], "quotation"
        )
        
        quotation_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        valid_until = now + timedelta(days=quotation.validity_days)
        
        # Enrich items with product data if missing
        enriched_items = []
        for item in quotation.items:
            item_dict = item.dict()
            
            # Try to get product details if not provided
            if not item_dict.get("description") or not item_dict.get("image_url"):
                product = await db.products.find_one({
                    "$or": [
                        {"id": item.product_id},
                        {"sku": item.model_number},
                        {"model_number": item.model_number}
                    ]
                })
                
                if product:
                    if not item_dict.get("description"):
                        item_dict["description"] = product.get("short_description") or product.get("description", "")[:100]
                    if not item_dict.get("image_url"):
                        images = product.get("images", [])
                        item_dict["image_url"] = images[0] if images else None
            
            enriched_items.append(item_dict)
        
        # Calculate totals
        totals = calculate_quotation_totals(
            enriched_items,
            quotation.discount_percent,
            quotation.include_gst
        )
        
        # Use provided terms or default
        terms = quotation.terms_and_conditions or DEFAULT_TERMS.format(
            validity_days=quotation.validity_days
        )
        
        # Link this quotation to an existing CRM customer record, if one
        # matches by phone. Stored as None when no match is found so
        # walk-in / non-CRM customers don't block quotation creation.
        linked_customer = None
        if quotation.customer_phone:
            normalized_phone = "".join(ch for ch in quotation.customer_phone if ch.isdigit())[-10:]
            if normalized_phone:
                linked_customer = await db.customers.find_one(
                    {"phone": {"$regex": normalized_phone + "$"}}, {"_id": 0, "id": 1}
                )
        linked_customer_id = linked_customer["id"] if linked_customer else None

        quotation_data = {
            "id": quotation_id,
            "quotation_number": quotation_number,
            "store_id": quotation.store_id,
            "store_code": store["code"],
            "store_name": store["name"],
            "store_address": store.get("address", ""),
            "store_phone": store.get("phone", ""),
            "store_gst": store.get("gst_number", ""),
            "customer_id": linked_customer_id,
            "customer_name": quotation.customer_name,
            "customer_email": quotation.customer_email,
            "customer_phone": quotation.customer_phone,
            "customer_address": quotation.customer_address,
            "items": enriched_items,
            "item_count": len(enriched_items),
            "totals": totals,
            "discount_percent": quotation.discount_percent,
            "include_gst": quotation.include_gst,
            "terms_and_conditions": terms,
            "validity_days": quotation.validity_days,
            "valid_until": valid_until.isoformat(),
            "notes": quotation.notes,
            "status": "draft",  # draft, sent, accepted, rejected, expired, converted
            "converted_to_order": None,
            "email_sent": False,
            "whatsapp_sent": False,
            "pdf_downloaded": False,
            "created_by": None,  # Will be set when auth is integrated
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        
        await db.quotations.insert_one(quotation_data)
        
        return {
            "status": "success",
            "message": f"Quotation {quotation_number} created successfully",
            "quotation_id": quotation_id,
            "quotation_number": quotation_number,
            "totals": totals
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating quotation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_quotations(
    store_id: Optional[str] = None,
    status: Optional[str] = None,
    customer_search: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    db = Depends(get_db)
):
    """List quotations with filters"""
    try:
        query = {}
        
        if store_id:
            query["store_id"] = store_id
        if status:
            query["status"] = status
        if customer_search:
            query["$or"] = [
                {"customer_name": {"$regex": customer_search, "$options": "i"}},
                {"customer_phone": {"$regex": customer_search, "$options": "i"}},
                {"customer_email": {"$regex": customer_search, "$options": "i"}}
            ]
        
        if from_date or to_date:
            date_query = {}
            if from_date:
                date_query["$gte"] = from_date
            if to_date:
                date_query["$lte"] = to_date
            query["created_at"] = date_query
        
        skip = (page - 1) * limit
        
        quotations = await db.quotations.find(
            query, {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.quotations.count_documents(query)
        
        return {
            "status": "success",
            "quotations": quotations,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

CRM_STAGES = ["new", "contacted", "qualified", "negotiation", "won", "lost"]


def _crm_stage_of(q):
    """Pipeline stage: explicit crm_stage, else derived from quotation status."""
    if q.get("crm_stage") in CRM_STAGES:
        return q["crm_stage"]
    return "contacted" if q.get("status") == "sent" else "new"


class QuotationCrmUpdate(BaseModel):
    crm_stage: Optional[str] = None
    crm_notes: Optional[str] = None
    follow_up_date: Optional[str] = None
    updated_by: Optional[str] = None


@router.get("/crm/pipeline")
async def crm_pipeline(store_code: Optional[str] = None, limit: int = 2000, db = Depends(get_db)):
    """All quotations with their CRM pipeline stage (line items excluded)."""
    try:
        limit = min(max(int(limit or 2000), 1), 5000)
        query = {}
        if store_code:
            query["store_code"] = store_code
        docs = await db.quotations.find(
            query, {"_id": 0, "items": 0, "terms_and_conditions": 0, "crm_history": 0}
        ).sort("created_at", -1).limit(limit).to_list(None)
        for d in docs:
            d["crm_stage"] = _crm_stage_of(d)
            d["amount"] = (d.get("totals") or {}).get("grand_total", 0)
        total = await db.quotations.count_documents(query)
        return {"status": "success", "quotations": docs, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{quotation_id}/crm-stage")
async def update_quotation_crm(quotation_id: str, payload: QuotationCrmUpdate, db = Depends(get_db)):
    """Update pipeline stage / follow-up date / notes. Does not touch quotation status."""
    try:
        q = await db.quotations.find_one({"id": quotation_id}, {"_id": 0, "id": 1, "status": 1, "crm_stage": 1})
        if not q:
            raise HTTPException(status_code=404, detail="Quotation not found")
        now = datetime.now(timezone.utc).isoformat()
        fields = {"crm_updated_at": now}
        history = None
        if payload.crm_stage is not None:
            if payload.crm_stage not in CRM_STAGES:
                raise HTTPException(status_code=400, detail="Invalid stage")
            if payload.crm_stage != _crm_stage_of(q):
                history = {"stage": payload.crm_stage, "at": now, "by": payload.updated_by}
            fields["crm_stage"] = payload.crm_stage
        if payload.crm_notes is not None:
            fields["crm_notes"] = payload.crm_notes
        if payload.follow_up_date is not None:
            fields["crm_follow_up_date"] = payload.follow_up_date or None
        update = {"$set": fields}
        if history:
            update["$push"] = {"crm_history": history}
        await db.quotations.update_one({"id": quotation_id}, update)
        return {"status": "success", "crm_stage": fields.get("crm_stage")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{quotation_id}")
async def get_quotation(quotation_id: str, db = Depends(get_db)):
    """Get quotation details"""
    try:
        quotation = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})
        if not quotation:
            raise HTTPException(status_code=404, detail="Quotation not found")
        
        return {
            "status": "success",
            "quotation": quotation
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{quotation_id}")
async def update_quotation(
    quotation_id: str,
    update: QuotationUpdate,
    db = Depends(get_db)
):
    """Update quotation"""
    try:
        quotation = await db.quotations.find_one({"id": quotation_id})
        if not quotation:
            raise HTTPException(status_code=404, detail="Quotation not found")
        
        update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
        
        if update.customer_name:
            update_data["customer_name"] = update.customer_name
        if update.customer_email:
            update_data["customer_email"] = update.customer_email
        if update.customer_phone:
            update_data["customer_phone"] = update.customer_phone
        if update.customer_address:
            update_data["customer_address"] = update.customer_address
        if update.terms_and_conditions:
            update_data["terms_and_conditions"] = update.terms_and_conditions
        if update.notes:
            update_data["notes"] = update.notes
        if update.status:
            update_data["status"] = update.status
        
        if update.items is not None:
            items = [item.dict() for item in update.items]
            update_data["items"] = items
            update_data["item_count"] = len(items)
            
            discount = update.discount_percent if update.discount_percent is not None else quotation.get("discount_percent", 0)
            include_gst = quotation.get("include_gst", True)
            
            totals = calculate_quotation_totals(items, discount, include_gst)
            update_data["totals"] = totals
        
        if update.discount_percent is not None:
            update_data["discount_percent"] = update.discount_percent
            items = update_data.get("items") or quotation.get("items", [])
            include_gst = quotation.get("include_gst", True)
            totals = calculate_quotation_totals(items, update.discount_percent, include_gst)
            update_data["totals"] = totals
        
        if update.validity_days:
            update_data["validity_days"] = update.validity_days
            created_at = datetime.fromisoformat(quotation["created_at"].replace('Z', '+00:00'))
            valid_until = created_at + timedelta(days=update.validity_days)
            update_data["valid_until"] = valid_until.isoformat()
        
        await db.quotations.update_one(
            {"id": quotation_id},
            {"$set": update_data}
        )
        
        return {
            "status": "success",
            "message": "Quotation updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{quotation_id}/pdf")
async def download_quotation_pdf(quotation_id: str, db = Depends(get_db)):
    """Download quotation as PDF"""
    try:
        quotation = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})
        if not quotation:
            raise HTTPException(status_code=404, detail="Quotation not found")
        
        # Generate PDF
        pdf_bytes = await generate_quotation_pdf(quotation)
        
        # Mark as downloaded
        await db.quotations.update_one(
            {"id": quotation_id},
            {"$set": {"pdf_downloaded": True, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        filename = f"{quotation['quotation_number']}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{quotation_id}/email")
async def send_quotation_email(
    quotation_id: str,
    email_data: EmailQuotation,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Send quotation via email"""
    try:
        quotation = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})
        if not quotation:
            raise HTTPException(status_code=404, detail="Quotation not found")
        
        # Generate PDF
        pdf_bytes = await generate_quotation_pdf(quotation)
        
        # Send email using SendGrid
        sendgrid_key = os.environ.get("SENDGRID_API_KEY")
        
        if not sendgrid_key:
            raise HTTPException(status_code=500, detail="Email service not configured")
        
        import sendgrid
        from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
        import base64
        
        subject = email_data.subject or f"Quotation {quotation['quotation_number']} from Aditya Retail"
        
        message_body = email_data.message or f"""
Dear {quotation['customer_name']},

Thank you for your interest in our products. Please find attached the quotation as requested.

Quotation Number: {quotation['quotation_number']}
Valid Until: {quotation['valid_until'][:10]}
Total Amount: ₹{quotation['totals']['grand_total']:,.2f}

Please feel free to contact us for any queries.

Best regards,
{quotation.get('store_name', 'Aditya Retail')} Team
"""
        
        sg = sendgrid.SendGridAPIClient(api_key=sendgrid_key)
        
        mail = Mail(
            from_email="sales.aronline@gmail.com",
            to_emails=email_data.to_email,
            subject=subject,
            plain_text_content=message_body
        )
        
        # Attach PDF
        encoded_pdf = base64.b64encode(pdf_bytes).decode()
        attachment = Attachment(
            FileContent(encoded_pdf),
            FileName(f"{quotation['quotation_number']}.pdf"),
            FileType('application/pdf'),
            Disposition('attachment')
        )
        mail.attachment = attachment
        
        response = sg.send(mail)
        
        # Update quotation status
        await db.quotations.update_one(
            {"id": quotation_id},
            {"$set": {
                "email_sent": True,
                "status": "sent" if quotation["status"] == "draft" else quotation["status"],
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "status": "success",
            "message": f"Quotation sent to {email_data.to_email}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@router.get("/{quotation_id}/whatsapp")
async def get_whatsapp_link(quotation_id: str, db = Depends(get_db)):
    """Generate WhatsApp share link for quotation"""
    try:
        quotation = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})
        if not quotation:
            raise HTTPException(status_code=404, detail="Quotation not found")
        
        # Generate message
        items_text = "\n".join([
            f"• {item['brand']} {item['model_number']} - ₹{item['offer_price']:,.0f}"
            for item in quotation["items"][:5]  # Limit to 5 items for WhatsApp
        ])
        
        if len(quotation["items"]) > 5:
            items_text += f"\n...and {len(quotation['items']) - 5} more items"
        
        backend_url = os.environ.get("REACT_APP_BACKEND_URL", "https://adityaretail.com")
        pdf_link = f"{backend_url}/api/quotations/{quotation_id}/pdf"

        message = f"""
*Quotation from Aditya Retail*
━━━━━━━━━━━━━━━━

📋 *Quotation No:* {quotation['quotation_number']}
📅 *Valid Until:* {quotation['valid_until'][:10]}

*Products:*
{items_text}

💰 *Total:* ₹{quotation['totals']['grand_total']:,.2f}
💚 *You Save:* ₹{quotation['totals']['total_savings']:,.2f}

📄 View/Download PDF: {pdf_link}

📞 Call: +91-9876543210
🌐 www.adityaretail.com
        """.strip()
        
        # URL encode the message
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        
        # Generate WhatsApp link
        phone = quotation.get("customer_phone", "").replace("+", "").replace("-", "").replace(" ", "")
        
        if phone:
            whatsapp_link = f"https://wa.me/{phone}?text={encoded_message}"
        else:
            whatsapp_link = f"https://wa.me/?text={encoded_message}"
        
        # Update quotation
        await db.quotations.update_one(
            {"id": quotation_id},
            {"$set": {"whatsapp_sent": True, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        return {
            "status": "success",
            "whatsapp_link": whatsapp_link,
            "message": message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{quotation_id}/convert-to-order")
async def convert_to_order(quotation_id: str, db = Depends(get_db)):
    """Convert accepted quotation to sales order"""
    try:
        quotation = await db.quotations.find_one({"id": quotation_id})
        if not quotation:
            raise HTTPException(status_code=404, detail="Quotation not found")
        
        if quotation["status"] not in ["sent", "accepted"]:
            raise HTTPException(status_code=400, detail="Only sent or accepted quotations can be converted")
        
        # Import document numbering
        store = await db.stores.find_one({"id": quotation["store_id"]})
        order_number = await get_next_document_number(
            db, quotation["store_id"], store["code"], "sales_order"
        )
        
        order_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        # Create order from quotation
        order_data = {
            "id": order_id,
            "order_number": order_number,
            "store_id": quotation["store_id"],
            "store_code": quotation["store_code"],
            "store_name": quotation["store_name"],
            "customer_name": quotation["customer_name"],
            "customer_email": quotation["customer_email"],
            "customer_phone": quotation["customer_phone"],
            "customer_address": quotation["customer_address"],
            "items": quotation["items"],
            "totals": quotation["totals"],
            "quotation_id": quotation_id,
            "quotation_number": quotation["quotation_number"],
            "order_status": "confirmed",
            "payment_status": "pending",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        
        await db.orders.insert_one(order_data)
        
        # Update quotation
        await db.quotations.update_one(
            {"id": quotation_id},
            {"$set": {
                "status": "converted",
                "converted_to_order": order_id,
                "updated_at": now.isoformat()
            }}
        )
        
        return {
            "status": "success",
            "message": f"Quotation converted to Sales Order {order_number}",
            "order_id": order_id,
            "order_number": order_number
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/products")
async def search_products_for_quotation(
    query: str,
    limit: int = 10,
    db = Depends(get_db)
):
    """Search products to add to quotation"""
    try:
        search_query = {
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"brand": {"$regex": query, "$options": "i"}},
                {"sku": {"$regex": query, "$options": "i"}},
                {"model_number": {"$regex": query, "$options": "i"}},
                {"category": {"$regex": query, "$options": "i"}}
            ]
        }
        
        products = await db.products.find(
            search_query,
            {
                "_id": 0,
                "id": 1,
                "name": 1,
                "brand": 1,
                "sku": 1,
                "model_number": 1,
                "short_description": 1,
                "description": 1,
                "images": 1,
                "price": 1,
                "original_price": 1,
                "category": 1
            }
        ).limit(limit).to_list(None)
        
        # Format for quotation
        formatted_products = []
        for p in products:
            formatted_products.append({
                "product_id": p.get("id", str(p.get("_id", ""))),
                "brand": p.get("brand", ""),
                "model_number": p.get("sku") or p.get("model_number", ""),
                "product_name": p.get("name", ""),
                "description": p.get("short_description") or (p.get("description", "")[:100] if p.get("description") else ""),
                "image_url": p.get("images", [None])[0],
                "mrp": p.get("original_price") or p.get("price", 0),
                "offer_price": p.get("price", 0),
                "category": p.get("category", "")
            })
        
        return {
            "status": "success",
            "products": formatted_products,
            "count": len(formatted_products)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ============ SMART QUOTE ============

class SmartQuoteItem(BaseModel):
    model_number: str
    quantity: int = 1
    offer_price: Optional[float] = None  # Optional override

class SmartQuoteCreate(BaseModel):
    store_id: str
    customer_name: str
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    customer_address: Optional[str] = None
    items: List[SmartQuoteItem]
    discount_percent: float = 0
    include_gst: bool = True
    notes: Optional[str] = None

@router.post("/smart-quote")
async def create_smart_quote(smart_quote: SmartQuoteCreate, db=Depends(get_db)):
    """
    Create a quotation using just model numbers and quantities.
    The system automatically fetches product details from the catalog.
    """
    try:
        # Validate store
        store = await db.stores.find_one({"id": smart_quote.store_id})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Initialize document numbering for store if needed
        await initialize_store_numbering(db, smart_quote.store_id, store["code"])
        
        # Generate quotation number
        quotation_number = await get_next_document_number(
            db, smart_quote.store_id, store["code"], "quotation"
        )
        
        # Fetch product details for each model number
        enriched_items = []
        not_found_items = []
        
        for item in smart_quote.items:
            # Search for product by model number, SKU, or name
            product = await db.products.find_one({
                "$or": [
                    {"model_number": {"$regex": item.model_number, "$options": "i"}},
                    {"sku": {"$regex": item.model_number, "$options": "i"}},
                    {"name": {"$regex": item.model_number, "$options": "i"}}
                ]
            })
            
            if product:
                images = product.get("images", [])
                enriched_items.append({
                    "product_id": product.get("id", str(uuid.uuid4())),
                    "brand": product.get("brand", "Unknown"),
                    "model_number": product.get("model_number") or product.get("sku") or item.model_number,
                    "product_name": product.get("name", "Unknown Product"),
                    "description": product.get("short_description") or (product.get("description", "")[:100] if product.get("description") else ""),
                    "image_url": images[0] if images else None,
                    "mrp": product.get("original_price") or product.get("price", 0),
                    "offer_price": item.offer_price if item.offer_price else product.get("price", 0),
                    "quantity": item.quantity,
                    "category": product.get("category", "")
                })
            else:
                not_found_items.append(item.model_number)
        
        if not enriched_items:
            raise HTTPException(
                status_code=400, 
                detail=f"No products found for the provided model numbers: {', '.join(not_found_items)}"
            )
        
        # Calculate totals
        totals = calculate_quotation_totals(
            enriched_items,
            smart_quote.discount_percent,
            smart_quote.include_gst
        )
        
        quotation_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        valid_until = now + timedelta(days=15)
        
        quotation_data = {
            "id": quotation_id,
            "quotation_number": quotation_number,
            "store_id": smart_quote.store_id,
            "store_code": store["code"],
            "store_name": store["name"],
            "customer_name": smart_quote.customer_name,
            "customer_email": smart_quote.customer_email,
            "customer_phone": smart_quote.customer_phone,
            "customer_address": smart_quote.customer_address,
            "items": enriched_items,
            "item_count": len(enriched_items),
            "totals": totals,
            "discount_percent": smart_quote.discount_percent,
            "include_gst": smart_quote.include_gst,
            "terms_and_conditions": DEFAULT_TERMS.format(validity_days=15),
            "validity_days": 15,
            "valid_until": valid_until.isoformat(),
            "notes": smart_quote.notes,
            "status": "draft",
            "converted_to_order": None,
            "email_sent": False,
            "whatsapp_sent": False,
            "pdf_downloaded": False,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "created_by": "smart_quote",
            "is_smart_quote": True
        }
        
        await db.quotations.insert_one(quotation_data)
        
        # Remove MongoDB _id
        quotation_data.pop('_id', None)
        
        response = {
            "status": "success",
            "message": f"Smart quote created with {len(enriched_items)} items",
            "quotation": quotation_data
        }
        
        if not_found_items:
            response["warnings"] = f"Products not found for: {', '.join(not_found_items)}"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating smart quote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{quotation_id}/convert-to-order")
async def convert_quotation_to_order(quotation_id: str, db=Depends(get_db)):
    """
    Convert an accepted quotation to a Sales Order.
    """
    try:
        # Find the quotation
        quotation = await db.quotations.find_one({"id": quotation_id})
        if not quotation:
            raise HTTPException(status_code=404, detail="Quotation not found")
        
        if quotation.get("converted_to_order"):
            raise HTTPException(
                status_code=400, 
                detail=f"Quotation already converted to order: {quotation['converted_to_order']}"
            )
        
        # Generate order number
        order_number = f"SO-{quotation['quotation_number'].replace('QT-', '')}"
        order_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        # Create order from quotation
        order_data = {
            "id": order_id,
            "order_number": order_number,
            "store_id": quotation["store_id"],
            "store_code": quotation.get("store_code"),
            "store_name": quotation.get("store_name"),
            "customer_name": quotation["customer_name"],
            "customer_email": quotation.get("customer_email"),
            "customer_phone": quotation.get("customer_phone"),
            "shipping_address": quotation.get("customer_address"),
            "items": quotation["items"],
            "subtotal": quotation["totals"]["subtotal"],
            "discount_amount": quotation["totals"]["discount_amount"],
            "tax_amount": quotation["totals"]["total_gst"],
            "total_amount": quotation["totals"]["grand_total"],
            "payment_status": "pending",
            "payment_method": "to_be_collected",
            "order_status": "placed",
            "source": "quotation",
            "quotation_id": quotation_id,
            "quotation_number": quotation["quotation_number"],
            "notes": quotation.get("notes"),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        
        await db.orders.insert_one(order_data)
        
        # Update quotation status
        await db.quotations.update_one(
            {"id": quotation_id},
            {
                "$set": {
                    "status": "converted",
                    "converted_to_order": order_id,
                    "converted_at": now.isoformat(),
                    "updated_at": now.isoformat()
                }
            }
        )
        
        # Remove MongoDB _id
        order_data.pop('_id', None)
        
        return {
            "status": "success",
            "message": f"Quotation converted to Sales Order: {order_number}",
            "order": order_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting quotation to order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
