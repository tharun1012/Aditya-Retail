from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime, timezone
from database import get_db
import os

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.get("/generate/{order_number}")
async def generate_invoice(
    order_number: str,
    database = Depends(get_db)
):
    """Generate PDF invoice for an order"""
    try:
        # Fetch order details
        order = await database.orders.find_one({"order_number": order_number})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Create invoices directory if it doesn't exist
        invoice_dir = "/app/backend/invoices"
        os.makedirs(invoice_dir, exist_ok=True)
        
        # Generate PDF filename
        pdf_filename = f"{invoice_dir}/invoice_{order_number}.pdf"
        
        # Create PDF
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a56db'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Company Header
        elements.append(Paragraph("ADITYA RETAIL", title_style))
        elements.append(Paragraph("Premium Bosch & Siemens Products", styles['Normal']))
        elements.append(Paragraph("Mumbai, Maharashtra 400001", styles['Normal']))
        elements.append(Paragraph("GSTIN: 27AAAAA1234A1Z5", styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Invoice Title
        invoice_title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#1a56db'),
            spaceAfter=20
        )
        elements.append(Paragraph("TAX INVOICE", invoice_title_style))
        
        # Invoice Details
        invoice_data = [
            ['Invoice Number:', order_number],
            ['Order Date:', datetime.fromisoformat(order.get('created_at', datetime.now(timezone.utc).isoformat())).strftime('%d-%m-%Y')],
            ['Payment Status:', order.get('payment_status', 'pending').upper()],
            ['Payment Method:', order.get('payment_method', 'N/A').upper()]
        ]
        
        invoice_table = Table(invoice_data, colWidths=[2*inch, 3*inch])
        invoice_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(invoice_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Customer Details
        customer = order.get('customer_details', {})
        billing_address = order.get('billing_address', {})
        shipping_address = order.get('shipping_address', {})
        
        customer_data = [
            ['BILL TO:', 'SHIP TO:'],
            [
                f"{customer.get('name', 'N/A')}\n{customer.get('email', '')}\n{customer.get('phone', '')}\n{billing_address.get('address', '')}\n{billing_address.get('city', '')}, {billing_address.get('pincode', '')}",
                f"{customer.get('name', 'N/A')}\n{shipping_address.get('address', '')}\n{shipping_address.get('city', '')}, {shipping_address.get('pincode', '')}"
            ]
        ]
        
        customer_table = Table(customer_data, colWidths=[3*inch, 3*inch])
        customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(customer_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Order Items with HSN
        items_data = [['Item', 'HSN', 'Qty', 'Rate', 'Tax', 'Amount']]
        
        for item in order.get('items', []):
            hsn_code = item.get('hsn_code', 'N/A')
            tax_rate = item.get('tax_rate', 18.0)
            items_data.append([
                item.get('product_name', 'Product'),
                hsn_code,
                str(item.get('quantity', 1)),
                f"₹{item.get('price', 0):,.2f}",
                f"{tax_rate}%",
                f"₹{item.get('total', 0):,.2f}"
            ])
        
        items_table = Table(items_data, colWidths=[2.5*inch, 0.7*inch, 0.5*inch, 0.9*inch, 0.5*inch, 0.9*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a56db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Totals
        subtotal = order.get('subtotal', 0)
        tax = order.get('tax_amount', 0)
        shipping = order.get('shipping_cost', 0)
        discount = order.get('discount_amount', 0)
        total = order.get('total_amount', 0)
        
        totals_data = [
            ['Subtotal:', f"₹{subtotal:,.2f}"],
            ['Tax (GST 18%):', f"₹{tax:,.2f}"],
            ['Shipping:', f"₹{shipping:,.2f}"],
        ]
        
        if discount > 0:
            totals_data.append(['Discount:', f"-₹{discount:,.2f}"])
        
        totals_data.append(['TOTAL:', f"₹{total:,.2f}"])
        
        totals_table = Table(totals_data, colWidths=[5*inch, 1.7*inch])
        totals_table.setStyle(TableStyle([
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -2), 10),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(totals_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        elements.append(Paragraph("Thank you for your business!", footer_style))
        elements.append(Paragraph("For support, contact: support@adityaretail.com", footer_style))
        
        # Build PDF
        doc.build(elements)
        
        # Return PDF file
        return FileResponse(
            pdf_filename,
            media_type='application/pdf',
            filename=f"invoice_{order_number}.pdf"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate invoice: {str(e)}")
