"""Document Management Routes - PDF, Print, Email, WhatsApp"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from database import get_db
from pdf_generator import (
    generate_invoice_html, 
    generate_purchase_order_html,
    generate_voucher_html,
    generate_credit_debit_note_html,
    generate_expense_receipt_html,
    generate_delivery_challan_html,
    generate_grn_html,
    html_to_pdf_bytes
)
from sendgrid_email_service import sendgrid_email_service
import urllib.parse
import io

router = APIRouter(prefix="/documents", tags=["Documents"])

class EmailDocumentRequest(BaseModel):
    document_id: str
    document_type: str  # invoice, purchase_order, voucher, note, expense
    recipient_email: EmailStr
    recipient_name: str

@router.get("/invoice/{invoice_id}/html")
async def get_invoice_html(invoice_id: str, db = Depends(get_db)):
    """
    Generate HTML for invoice (for printing or preview)
    """
    try:
        invoice = await db.offline_invoices.find_one({"id": invoice_id}, {"_id": 0})
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        html_content = generate_invoice_html(invoice)
        return HTMLResponse(content=html_content)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate invoice HTML: {str(e)}")

@router.get("/invoice/{invoice_id}/pdf")
async def get_invoice_pdf(invoice_id: str, db = Depends(get_db)):
    """
    Generate PDF for invoice download
    """
    try:
        # Try to find invoice in multiple collections
        invoice = await db.offline_invoices.find_one({"id": invoice_id}, {"_id": 0})
        
        if not invoice:
            invoice = await db.orders.find_one({"id": invoice_id}, {"_id": 0})
        
        if not invoice:
            invoice = await db.orders.find_one({"order_id": invoice_id}, {"_id": 0})
            
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Try using invoice_pdf_generator
        try:
            from invoice_pdf_generator import generate_invoice_pdf
            pdf_bytes = generate_invoice_pdf(invoice, invoice_type="offline")
            
            invoice_number = invoice.get('invoice_number') or invoice.get('order_number') or invoice_id
            filename = f"Invoice_{invoice_number}.pdf"
            
            return StreamingResponse(
                io.BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
        except ImportError:
            # Fallback to HTML response for printing
            html_content = generate_invoice_html(invoice)
            return HTMLResponse(content=html_content)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate invoice PDF: {str(e)}")

@router.get("/voucher/{voucher_id}/html")
async def get_voucher_html(voucher_id: str, db = Depends(get_db)):
    """
    Generate HTML for payment/receipt voucher
    """
    try:
        voucher = await db.vouchers.find_one({"id": voucher_id}, {"_id": 0})
        
        if not voucher:
            raise HTTPException(status_code=404, detail="Voucher not found")
        
        html_content = generate_voucher_html(voucher)
        return HTMLResponse(content=html_content)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate voucher HTML: {str(e)}")

@router.get("/note/{note_id}/html")
async def get_note_html(note_id: str, db = Depends(get_db)):
    """
    Generate HTML for credit/debit note
    """
    try:
        note = await db.credit_debit_notes.find_one({"id": note_id}, {"_id": 0})
        
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        html_content = generate_credit_debit_note_html(note)
        return HTMLResponse(content=html_content)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate note HTML: {str(e)}")

@router.get("/expense/{expense_id}/html")
async def get_expense_html(expense_id: str, db = Depends(get_db)):
    """
    Generate HTML for expense receipt
    """
    try:
        expense = await db.expenses.find_one({"id": expense_id}, {"_id": 0})
        
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        
        html_content = generate_expense_receipt_html(expense)
        return HTMLResponse(content=html_content)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate expense HTML: {str(e)}")

@router.get("/delivery-challan/{challan_id}/html")
async def get_delivery_challan_html(challan_id: str, db = Depends(get_db)):
    """
    Generate HTML for delivery challan
    """
    try:
        challan = await db.delivery_challans.find_one({"id": challan_id}, {"_id": 0})
        
        if not challan:
            raise HTTPException(status_code=404, detail="Delivery challan not found")
        
        html_content = generate_delivery_challan_html(challan)
        return HTMLResponse(content=html_content)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate delivery challan HTML: {str(e)}")

        return HTMLResponse(content=html_content)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate expense HTML: {str(e)}")

        raise HTTPException(status_code=500, detail=f"Failed to generate invoice HTML: {str(e)}")

@router.get("/purchase-order/{po_id}/html")
async def get_purchase_order_html(po_id: str, db = Depends(get_db)):
    """
    Generate HTML for purchase order
    """
    try:
        po = await db.purchase_orders.find_one({"id": po_id}, {"_id": 0})
        
        if not po:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        
        html_content = generate_purchase_order_html(po)
        return HTMLResponse(content=html_content)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PO HTML: {str(e)}")

@router.get("/grn/{grn_id}/html")
async def get_grn_html(grn_id: str, db = Depends(get_db)):
    """
    Generate printable HTML for a Goods Receipt Note
    """
    try:
        grn = await db.grn.find_one(
            {"$or": [{"id": grn_id}, {"grn_number": grn_id}]},
            {"_id": 0}
        )

        if not grn:
            raise HTTPException(status_code=404, detail="GRN not found")

        html_content = generate_grn_html(grn)
        return HTMLResponse(content=html_content)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate GRN HTML: {str(e)}")

@router.post("/email")
async def email_document(request: EmailDocumentRequest, db = Depends(get_db)):
    """
    Email document to customer
    """
    try:
        # Fetch document
        if request.document_type == "invoice":
            doc = await db.offline_invoices.find_one({"id": request.document_id}, {"_id": 0})
            if not doc:
                raise HTTPException(status_code=404, detail="Invoice not found")
            
            doc_number = doc.get('invoice_number', 'N/A')
            doc_type_label = "Sales Order" if doc.get('document_type') == 'sales_order' else "Invoice"
            html_content = generate_invoice_html(doc)
            
        elif request.document_type in ("purchase_order", "purchase-order"):
            doc = await db.purchase_orders.find_one({"id": request.document_id}, {"_id": 0})
            if not doc:
                raise HTTPException(status_code=404, detail="Purchase order not found")
            
            doc_number = doc.get('po_number', 'N/A')
            doc_type_label = "Purchase Order"
            html_content = generate_purchase_order_html(doc)
        
        elif request.document_type == "voucher":
            doc = await db.vouchers.find_one({"id": request.document_id}, {"_id": 0})
            if not doc:
                raise HTTPException(status_code=404, detail="Voucher not found")
            
            doc_number = doc.get('voucher_number', 'N/A')
            doc_type_label = "Payment Voucher" if doc.get('voucher_type') == 'payment' else "Receipt Voucher"
            html_content = generate_voucher_html(doc)
        
        elif request.document_type == "note":
            doc = await db.credit_debit_notes.find_one({"id": request.document_id}, {"_id": 0})
            if not doc:
                raise HTTPException(status_code=404, detail="Note not found")
            
            doc_number = doc.get('note_number', 'N/A')
            doc_type_label = "Credit Note" if doc.get('note_type') == 'credit_note' else "Debit Note"
            html_content = generate_credit_debit_note_html(doc)
        
        elif request.document_type == "expense":
            doc = await db.expenses.find_one({"id": request.document_id}, {"_id": 0})
            if not doc:
                raise HTTPException(status_code=404, detail="Expense not found")
            
            doc_number = doc.get('expense_number', 'N/A')
            doc_type_label = "Expense Receipt"
            html_content = generate_expense_receipt_html(doc)
        
        else:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        # Prepare email
        subject = f"Your {doc_type_label} - {doc_number}"
        
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <p>Dear {request.recipient_name},</p>
            
            <p>Thank you for your business with <strong>Aditya Retail</strong>.</p>
            
            <p>Please find attached your {doc_type_label} <strong>{doc_number}</strong>.</p>
            
            <p>If you have any questions, please don't hesitate to contact us.</p>
            
            <br>
            <p>Best regards,<br>
            <strong>Aditya Retail Team</strong><br>
            Premium Bosch, Siemens & Hindware Home Appliances<br>
            Website: www.adityaretail.com</p>
        </body>
        </html>
        """
        
        # Generate PDF attachment from the document's HTML
        attachments = None
        try:
            pdf_bytes = html_to_pdf_bytes(html_content)
            attachments = [{
                "content": pdf_bytes,
                "filename": f"{doc_number}.pdf",
                "type": "application/pdf"
            }]
        except Exception as pdf_error:
            print(f"Warning: Could not generate PDF attachment: {pdf_error}")

        # Send email using SendGrid
        result = sendgrid_email_service.send_email(
            to_email=request.recipient_email,
            subject=subject,
            body=email_body,
            from_agent="sales",
            html=True,
            attachments=attachments
        )
        
        if result.get('status') == 'success':
            return {
                "status": "success",
                "message": f"{doc_type_label} emailed successfully to {request.recipient_email}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to email document: {str(e)}")

@router.get("/whatsapp-share/{document_id}")
async def generate_whatsapp_link(document_id: str, document_type: str, db = Depends(get_db)):
    """
    Generate WhatsApp share link with pre-filled message
    """
    try:
        # Fetch document
        if document_type == "invoice":
            doc = await db.offline_invoices.find_one({"id": document_id}, {"_id": 0})
            if not doc:
                raise HTTPException(status_code=404, detail="Invoice not found")
            
            doc_number = doc.get('invoice_number', 'N/A')
            doc_type_label = "Sales Order" if doc.get('document_type') == 'sales_order' else "Invoice"
            total_amount = doc.get('total_amount', 0)
            
        elif document_type in ("purchase_order", "purchase-order"):
            doc = await db.purchase_orders.find_one({"id": document_id}, {"_id": 0})
            if not doc:
                raise HTTPException(status_code=404, detail="Purchase order not found")
            
            doc_number = doc.get('po_number', 'N/A')
            doc_type_label = "Purchase Order"
            total_amount = doc.get('total_amount', 0)
            
        elif document_type == "voucher":
            doc = await db.vouchers.find_one({"id": document_id}, {"_id": 0})
            if not doc:
                raise HTTPException(status_code=404, detail="Voucher not found")
            
            doc_number = doc.get('voucher_number', 'N/A')
            doc_type_label = "Payment Voucher" if doc.get('voucher_type') == 'payment' else "Receipt Voucher"
            total_amount = doc.get('amount', 0)
            
        elif document_type == "note":
            doc = await db.credit_debit_notes.find_one({"id": document_id}, {"_id": 0})
            if not doc:
                raise HTTPException(status_code=404, detail="Note not found")
            
            doc_number = doc.get('note_number', 'N/A')
            doc_type_label = "Credit Note" if doc.get('note_type') == 'credit_note' else "Debit Note"
            total_amount = doc.get('amount', 0)
            
        elif document_type == "expense":
            doc = await db.expenses.find_one({"id": document_id}, {"_id": 0})
            if not doc:
                raise HTTPException(status_code=404, detail="Expense not found")
            
            doc_number = doc.get('expense_number', 'N/A')
            doc_type_label = "Expense Receipt"
            total_amount = doc.get('amount', 0)
            
        else:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        # Get common fields
        customer = doc.get('customer', {})
        store = doc.get('store_details', {})
        phone = customer.get('phone', '')
        
        # Prepare WhatsApp message
        message = f"""Hello {customer.get('name', 'Customer')},

Thank you for your business with *Aditya Retail*!

📄 *{doc_type_label} Details:*
Document No: {doc_number}
Total Amount: ₹{total_amount:.2f}
Payment Mode: {doc.get('payment_mode', 'Cash').upper()}

🏪 *Store:*
{store.get('name', '')}
{store.get('address', '')}
{store.get('city', '')} - {store.get('pincode', '')}

📞 Contact: {store.get('phone', '')}

Thank you for choosing us!
- Aditya Retail Team"""
        
        # URL encode the message
        encoded_message = urllib.parse.quote(message)
        
        # Generate WhatsApp link
        whatsapp_url = f"https://wa.me/{phone.replace('+', '').replace(' ', '')}?text={encoded_message}"
        
        return {
            "status": "success",
            "whatsapp_url": whatsapp_url,
            "phone": phone
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate WhatsApp link: {str(e)}")
