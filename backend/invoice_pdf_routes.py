"""
Invoice PDF Routes
API endpoints for generating and downloading invoice PDFs
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from io import BytesIO
from datetime import datetime
import logging

from invoice_pdf_generator import generate_invoice_pdf

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/invoice-pdf", tags=["Invoice PDF"])

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'startup_template')

async def get_db():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    try:
        yield db
    finally:
        client.close()


@router.get("/order/{order_id}")
async def generate_order_invoice_pdf(
    order_id: str,
    db = Depends(get_db)
):
    """Generate PDF invoice for an online order"""
    try:
        # Find order by ID or order_number
        order = await db.orders.find_one(
            {"$or": [{"id": order_id}, {"order_id": order_id}, {"order_number": order_id}]},
            {"_id": 0}
        )
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Prepare invoice data
        invoice_data = {
            "invoice_number": order.get('order_number', order.get('id')),
            "invoice_date": order.get('created_at', datetime.now().isoformat()),
            "customer_name": order.get('customer_name', 'Customer'),
            "customer_phone": order.get('customer_phone', ''),
            "customer_email": order.get('customer_email', ''),
            "customer_gstin": order.get('customer_gstin', order.get('customer_gst', '')),
            "customer_msme": order.get('customer_msme_number', ''),
            "shipping_address": order.get('shipping_address', {}),
            "place_of_supply": order.get('place_of_supply', 'Karnataka'),
            "items": order.get('items', []),
            "subtotal": order.get('subtotal', 0),
            "tax_amount": order.get('tax_amount', order.get('gst_amount', 0)),
            "cgst": order.get('cgst', 0),
            "sgst": order.get('sgst', 0),
            "igst": order.get('igst', 0),
            "discount_amount": order.get('discount_amount', 0),
            "shipping_charges": order.get('shipping_charges', 0),
            "round_off": order.get('round_off', 0),
            "total_amount": order.get('total_amount', 0),
            "payment_method": order.get('payment_method', 'Cash'),
            "payment_status": order.get('payment_status', 'pending'),
        }
        
        # Generate PDF
        pdf_bytes = generate_invoice_pdf(invoice_data, "online")
        
        # Return as streaming response
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Invoice_{order.get('order_number', order_id)}.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating order invoice PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/offline/{invoice_id}")
async def generate_offline_invoice_pdf(
    invoice_id: str,
    db = Depends(get_db)
):
    """Generate PDF for an offline invoice"""
    try:
        # Find offline invoice
        invoice = await db.offline_invoices.find_one(
            {"$or": [{"id": invoice_id}, {"invoice_number": invoice_id}]},
            {"_id": 0}
        )
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Offline invoice not found")
        
        # Get store details for Ship From address
        store_code = invoice.get('store_code')
        store_details = invoice.get('store_details', {})
        
        # If store_details not in invoice, fetch from stores collection
        if not store_details or not store_details.get('address'):
            if store_code:
                store = await db.stores.find_one({"code": store_code}, {"_id": 0})
                if store:
                    store_details = {
                        "name": store.get('name', ''),
                        "address": store.get('address', ''),
                        "city": store.get('city', ''),
                        "state": store.get('state', 'Karnataka'),
                        "pincode": store.get('pincode', ''),
                        "phone": store.get('phone', ''),
                        "gst_number": store.get('gst_number', store.get('gstin', ''))
                    }
        
        # Prepare invoice data
        customer = invoice.get('customer', {})
        billing_address = invoice.get('billing_address', {})
        shipping_address = invoice.get('shipping_address', {})
        
        # Build billing address from various sources
        if not billing_address or not billing_address.get('address'):
            billing_address = {
                "address": customer.get('address', invoice.get('customer_address', '')),
                "city": customer.get('city', invoice.get('customer_city', '')),
                "state": customer.get('state', invoice.get('customer_state', 'Karnataka')),
                "pincode": customer.get('pincode', invoice.get('customer_pincode', ''))
            }
        
        # Build shipping address
        if not shipping_address or not shipping_address.get('address'):
            shipping_address = billing_address.copy()
        
        invoice_data = {
            "invoice_number": invoice.get('invoice_number', invoice.get('id')),
            "document_type": invoice.get('document_type', 'invoice'),  # Pass document_type!
            "invoice_date": invoice.get('invoice_date') or invoice.get('converted_to_invoice_at') or invoice.get('created_at', datetime.now().isoformat()),
            "customer_name": customer.get('name', invoice.get('customer_name', 'Walk-in Customer')),
            "customer_phone": customer.get('phone', invoice.get('customer_phone', '')),
            "customer_email": customer.get('email', invoice.get('customer_email', '')),
            "customer_gstin": customer.get('gst_number', invoice.get('customer_gstin', '')),
            "customer_msme": customer.get('msme_udyam', invoice.get('customer_msme', '')),
            "billing_address": billing_address,  # Pass billing_address!
            "shipping_address": shipping_address,  # Pass proper shipping_address!
            "store_details": store_details,  # Pass store_details for Ship From!
            "place_of_supply": customer.get('state', invoice.get('place_of_supply', 'Karnataka')),
            "items": invoice.get('items', []),
            "subtotal": invoice.get('subtotal', 0),
            "tax_amount": invoice.get('total_tax', invoice.get('tax_amount', 0)),
            "cgst": invoice.get('cgst', 0),
            "sgst": invoice.get('sgst', 0),
            "igst": invoice.get('igst', 0),
            "discount_amount": invoice.get('discount_amount', 0),
            "delivery_charges": invoice.get('delivery_charges', 0),
            "round_off": invoice.get('round_off', 0),
            "total_amount": invoice.get('total_amount', invoice.get('grand_total', 0)),
            "payment_method": invoice.get('payment_mode', 'Cash'),
            "payment_status": invoice.get('payment_status', 'completed'),
        }
        
        # Generate PDF
        pdf_bytes = generate_invoice_pdf(invoice_data, "offline")
        
        # Return as streaming response
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Invoice_{invoice.get('invoice_number', invoice_id)}.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating offline invoice PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview")
async def preview_invoice_pdf(invoice_data: dict):
    """Generate a preview PDF without saving to database"""
    try:
        # Generate PDF from provided data
        pdf_bytes = generate_invoice_pdf(invoice_data, invoice_data.get('invoice_type', 'offline'))
        
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline; filename=Invoice_Preview.pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating invoice preview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/purchase-bill/{bill_id}")
async def generate_purchase_bill_pdf(
    bill_id: str,
    db = Depends(get_db)
):
    """Generate PDF for a purchase bill"""
    try:
        # Find purchase bill
        bill = await db.purchase_bills.find_one(
            {"$or": [{"id": bill_id}, {"bill_number": bill_id}]},
            {"_id": 0}
        )
        
        if not bill:
            raise HTTPException(status_code=404, detail="Purchase bill not found")
        
        # For purchase bills, we swap supplier and recipient
        vendor = bill.get('vendor', {})
        
        invoice_data = {
            "invoice_number": bill.get('bill_number', bill.get('id')),
            "invoice_date": bill.get('bill_date', bill.get('created_at', datetime.now().isoformat())),
            "document_type": "Purchase Bill",
            # Vendor is the supplier
            "supplier_name": vendor.get('name', bill.get('vendor_name', '')),
            "supplier_gstin": vendor.get('gst_number', bill.get('vendor_gst', '')),
            "supplier_address": vendor.get('address', ''),
            "supplier_city": vendor.get('city', ''),
            "supplier_state": vendor.get('state', 'Karnataka'),
            "supplier_pincode": vendor.get('pincode', ''),
            "supplier_phone": vendor.get('phone', ''),
            # We are the recipient
            "customer_name": "ADITYA RETAIL",
            "customer_gstin": "29ABAFA6295J1Z2",
            "shipping_address": {
                "address_line1": "#21/1, 16th Cross, Sampige Road, Malleshwaram",
                "city": "Bangalore",
                "state": "Karnataka",
                "pincode": "560003"
            },
            "items": bill.get('items', []),
            "subtotal": bill.get('subtotal', 0),
            "cgst": bill.get('cgst', 0),
            "sgst": bill.get('sgst', 0),
            "igst": bill.get('igst', 0),
            "total_tax": bill.get('total_tax', 0),
            "total_amount": bill.get('grand_total', 0),
            "payment_method": bill.get('payment_mode', 'Bank Transfer'),
            "payment_status": bill.get('payment_status', 'pending'),
        }
        
        pdf_bytes = generate_invoice_pdf(invoice_data, "purchase")
        
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=PurchaseBill_{bill.get('bill_number', bill_id)}.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating purchase bill PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
