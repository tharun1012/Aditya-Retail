"""Delivery Challan Management Routes"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from database import get_db
from file_storage import save_upload, serve_upload
import uuid
import os
import shutil
from pathlib import Path

router = APIRouter(prefix="/delivery-challans", tags=["Delivery Challans"])

# Ensure upload directory exists
UPLOAD_DIR = Path("/app/backend/uploads/delivery_photos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class CreateChallanRequest(BaseModel):
    invoice_id: str
    delivery_person_id: str  # ID of the delivery person from admin_users
    vehicle_number: Optional[str] = None
    expected_delivery_date: str
    notes: Optional[str] = None
    created_by: str

class UpdateDeliveryStatusRequest(BaseModel):
    status: str  # pending, in_transit, delivered, failed
    delivery_notes: Optional[str] = None
    delivered_by: Optional[str] = None

def generate_challan_number(db_sync, store_code: str = "ADR"):
    """Generate delivery challan number"""
    from datetime import datetime
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")
    
    # This is async but we'll handle it properly
    count = 1  # Simplified for now
    return f"DC-{store_code}-{date_str}-{count:04d}"

def generate_google_maps_link(address: str, city: str = "", pincode: str = "") -> str:
    """Generate Google Maps link from address"""
    import urllib.parse
    
    full_address = f"{address}, {city} {pincode}".strip()
    encoded_address = urllib.parse.quote(full_address)
    
    return f"https://maps.google.com/?q={encoded_address}"

@router.post("/create")
async def create_delivery_challan(request: CreateChallanRequest, db = Depends(get_db)):
    """
    Create delivery challan from invoice
    """
    try:
        # Import here to avoid circular dependency
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        
        # Get MongoDB connection for admin_users
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'startup_template')
        client = AsyncIOMotorClient(mongo_url)
        auth_db = client[db_name]
        
        # Fetch delivery person details
        delivery_person = await auth_db.admin_users.find_one(
            {"id": request.delivery_person_id, "role": "delivery_person"},
            {"_id": 0, "password": 0}
        )
        
        if not delivery_person:
            raise HTTPException(status_code=404, detail="Delivery person not found")
        
        # Fetch invoice details
        invoice = await db.offline_invoices.find_one({"id": request.invoice_id}, {"_id": 0})
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Check if invoice is already delivered
        if invoice.get('delivery_status') == 'delivered':
            raise HTTPException(status_code=400, detail="Invoice already delivered")
        
        # Generate challan number
        store_code = invoice.get('store_code', 'ADR')
        challan_count = await db.delivery_challans.count_documents({"store_code": store_code})
        challan_number = f"DC-{store_code}-{datetime.now().strftime('%Y%m%d')}-{challan_count + 1:04d}"
        
        # Generate Google Maps link from customer address
        customer = invoice.get('customer', {})
        maps_link = generate_google_maps_link(
            customer.get('address', ''),
            customer.get('city', ''),
            customer.get('pincode', '')
        )
        
        # Create delivery challan
        challan_data = {
            "id": str(uuid.uuid4()),
            "challan_number": challan_number,
            "invoice_id": request.invoice_id,
            "invoice_number": invoice.get('invoice_number'),
            "store_code": store_code,
            "store_details": invoice.get('store_details', {}),
            "customer": customer,
            "items": invoice.get('items', []),
            "total_amount": invoice.get('total_amount', 0),
            "is_cod": invoice.get('is_cod', False),
            "is_pod": invoice.get('is_pod', False),
            "payment_collected": False,
            "payment_details": None,
            "delivery_person_id": request.delivery_person_id,
            "delivery_person_name": delivery_person.get('full_name'),
            "delivery_person_phone": delivery_person.get('phone'),
            "delivery_person_email": delivery_person.get('email'),
            "vehicle_number": request.vehicle_number or delivery_person.get('vehicle_number'),
            "expected_delivery_date": request.expected_delivery_date,
            "google_maps_link": maps_link,
            "status": "pending",  # pending, in_transit, delivered, failed
            "delivery_photos": [],
            "notes": request.notes,
            "delivery_notes": None,
            "created_by": request.created_by,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "delivered_at": None
        }
        
        await db.delivery_challans.insert_one(challan_data)
        
        # Update invoice with challan reference
        await db.offline_invoices.update_one(
            {"id": request.invoice_id},
            {
                "$set": {
                    "delivery_challan_id": challan_data["id"],
                    "delivery_challan_number": challan_number,
                    "delivery_status": "pending",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Send delivery schedule email to customer
        try:
            from email_notification_service import email_notification_service
            customer_email = customer.get('email')
            if customer_email:
                delivery_address = f"{customer.get('shipping_address', customer.get('address', ''))}, {customer.get('shipping_city', customer.get('city', ''))}, {customer.get('shipping_state', customer.get('state', ''))} - {customer.get('shipping_pincode', customer.get('pincode', ''))}"
                await email_notification_service.send_delivery_schedule_email(
                    customer_email=customer_email,
                    customer_name=customer.get('name', 'Customer'),
                    challan_number=challan_number,
                    invoice_number=invoice.get('invoice_number'),
                    driver_name=delivery_person.get('full_name'),
                    driver_phone=delivery_person.get('phone'),
                    vehicle_number=challan_data.get('vehicle_number'),
                    expected_date=request.expected_delivery_date or datetime.now().strftime('%d-%m-%Y'),
                    delivery_address=delivery_address
                )
                print(f"📧 Delivery schedule email sent to {customer_email}")
        except Exception as email_error:
            print(f"⚠️ Failed to send delivery schedule email: {email_error}")
        
        return {
            "status": "success",
            "challan_number": challan_number,
            "challan_id": challan_data["id"],
            "google_maps_link": maps_link,
            "message": "Delivery challan created successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create delivery challan: {str(e)}")


@router.get("/pending-orders")
async def get_pending_delivery_orders(
    store_code: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """
    Get all Sales Orders/Invoices pending delivery (no challan created yet)
    """
    try:
        # Find all offline invoices with pending_delivery status that don't have a challan yet
        query = {
            "status": "pending_delivery",
            "document_type": {"$in": ["sales_order", "invoice"]}
        }
        
        if store_code:
            query["store_code"] = store_code
        
        # Get all challans to find which invoice_ids already have challans
        existing_challan_ids = await db.delivery_challans.distinct("invoice_id")
        
        # Exclude invoices that already have challans
        if existing_challan_ids:
            query["id"] = {"$nin": existing_challan_ids}
        
        skip = (page - 1) * limit
        
        orders = await db.offline_invoices.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.offline_invoices.count_documents(query)
        
        # Format for frontend
        pending_orders = []
        for order in orders:
            customer = order.get("customer", {})
            pending_orders.append({
                "id": order.get("id"),
                "order_number": order.get("invoice_number"),
                "document_type": order.get("document_type"),
                "customer_name": customer.get("name"),
                "customer_phone": customer.get("phone"),
                "customer_email": customer.get("email"),
                "customer_address": customer.get("address") or customer.get("shipping_address"),
                "customer_city": customer.get("city") or customer.get("shipping_city"),
                "customer_state": customer.get("state") or customer.get("shipping_state"),
                "customer_pincode": customer.get("pincode") or customer.get("shipping_pincode"),
                "total_amount": order.get("total_amount"),
                "items_count": len(order.get("items", [])),
                "store_code": order.get("store_code"),
                "store_name": order.get("store_details", {}).get("name"),
                "created_at": order.get("created_at"),
                "expected_delivery_date": order.get("expected_delivery_date"),
                "payment_status": order.get("payment_status"),
                "order_source": order.get("order_source")
            })
        
        return {
            "status": "success",
            "orders": pending_orders,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pending orders: {str(e)}")


@router.get("/")
async def list_delivery_challans(
    status: Optional[str] = None,
    store_code: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """
    List all delivery challans with filters
    """
    try:
        query = {}
        
        if status:
            query["status"] = status
        
        if store_code:
            query["store_code"] = store_code
        
        skip = (page - 1) * limit
        
        challans = await db.delivery_challans.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.delivery_challans.count_documents(query)
        
        return {
            "status": "success",
            "challans": challans,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch delivery challans: {str(e)}")

@router.get("/stock-transfer-requests")
async def get_stock_transfer_requests_for_challan(
    warehouse_id: Optional[str] = None,
    db = Depends(get_db)
):
    """
    Get approved stock transfer requests that need delivery challans
    """
    try:
        query = {
            "status": "approved"
        }
        
        if warehouse_id:
            query["from_store_id"] = warehouse_id
        
        transfers = await db.stock_transfers.find(
            query, {"_id": 0}
        ).sort("created_at", -1).to_list(None)
        
        return {
            "status": "success",
            "transfers": transfers,
            "total": len(transfers)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/photos/{filename}")
async def get_delivery_photo(filename: str):
    return await serve_upload(filename)


@router.get("/{challan_id}")
async def get_delivery_challan(challan_id: str, db = Depends(get_db)):
    """
    Get delivery challan details
    """
    try:
        challan = await db.delivery_challans.find_one({"id": challan_id}, {"_id": 0})
        
        if not challan:
            raise HTTPException(status_code=404, detail="Delivery challan not found")
        
        return {
            "status": "success",
            "challan": challan
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch delivery challan: {str(e)}")

@router.put("/{challan_id}/status")
async def update_delivery_status(challan_id: str, request: UpdateDeliveryStatusRequest, db = Depends(get_db)):
    """
    Update delivery status
    """
    try:
        challan = await db.delivery_challans.find_one({"id": challan_id})
        
        if not challan:
            raise HTTPException(status_code=404, detail="Delivery challan not found")
        
        update_data = {
            "status": request.status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if request.delivery_notes:
            update_data["delivery_notes"] = request.delivery_notes
        
        if request.delivered_by:
            update_data["delivered_by"] = request.delivered_by
        
        if request.status == "delivered":
            update_data["delivered_at"] = datetime.now(timezone.utc).isoformat()
        
        await db.delivery_challans.update_one(
            {"id": challan_id},
            {"$set": update_data}
        )
        
        # Update invoice delivery status
        await db.offline_invoices.update_one(
            {"id": challan.get('invoice_id')},
            {
                "$set": {
                    "delivery_status": request.status,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return {
            "status": "success",
            "message": f"Delivery status updated to {request.status}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update delivery status: {str(e)}")

@router.post("/{challan_id}/upload-photo")
async def upload_delivery_photo(challan_id: str, file: UploadFile = File(...), db = Depends(get_db)):
    """
    Upload delivery photo (stored locally for now)
    """
    try:
        challan = await db.delivery_challans.find_one({"id": challan_id})
        
        if not challan:
            raise HTTPException(status_code=404, detail="Delivery challan not found")
        
        # Validate file type
        allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Invalid file type. Only images allowed.")
        
        # Generate unique filename
        unique_filename = f"{challan_id}_{uuid.uuid4()}{file_extension}"
        
        # Save file
        content = await file.read()
        await save_upload(unique_filename, content, file.content_type or "image/jpeg")
        
        # Update challan with photo reference
        photo_url = f"/api/delivery-challans/photos/{unique_filename}"
        
        await db.delivery_challans.update_one(
            {"id": challan_id},
            {
                "$push": {"delivery_photos": {
                    "url": photo_url,
                    "filename": unique_filename,
                    "uploaded_at": datetime.now(timezone.utc).isoformat()
                }},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        return {
            "status": "success",
            "photo_url": photo_url,
            "message": "Photo uploaded successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")

@router.get("/{challan_id}/delivery-link")
async def get_delivery_link(challan_id: str, db = Depends(get_db)):
    """
    Get delivery person shareable link
    """
    try:
        challan = await db.delivery_challans.find_one({"id": challan_id}, {"_id": 0})
        
        if not challan:
            raise HTTPException(status_code=404, detail="Delivery challan not found")
        
        # Generate shareable link for delivery person
        # In production, this would be your actual domain
        delivery_link = f"https://adityaretail.com/#/delivery/{challan_id}"
        
        return {
            "status": "success",
            "delivery_link": delivery_link,
            "challan_number": challan.get('challan_number'),
            "google_maps_link": challan.get('google_maps_link')
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate delivery link: {str(e)}")


# Delivery Person Endpoints

class PaymentCollectionRequest(BaseModel):
    amount_received: float
    payment_mode: str  # Cash, Card, UPI, Bank Transfer, etc.
    reference_number: Optional[str] = None
    notes: Optional[str] = None

@router.get("/delivery-person/assigned")
async def get_assigned_deliveries(
    delivery_person_id: str,
    status: Optional[str] = None,
    db = Depends(get_db)
):
    """
    Get all assigned deliveries for a delivery person (both invoices and challans)
    """
    try:
        query = {"delivery_person_id": delivery_person_id}
        
        if status:
            query["status"] = status
        
        # Get assigned challans
        challans = await db.delivery_challans.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).to_list(None)
        
        # Also get invoices directly assigned (without challan)
        invoice_query = {
            "delivery_person_id": delivery_person_id,
            "delivery_status": {"$ne": "delivered"}
        }
        
        invoices = await db.offline_invoices.find(
            invoice_query,
            {"_id": 0}
        ).sort("created_at", -1).to_list(None)
        
        return {
            "status": "success",
            "challans": challans,
            "direct_invoices": invoices,
            "total_pending": len([c for c in challans if c.get('status') == 'pending']) + len(invoices)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch assigned deliveries: {str(e)}")

@router.post("/{challan_id}/collect-payment")
async def collect_payment(
    challan_id: str,
    payment: PaymentCollectionRequest,
    delivery_person_id: str,
    db = Depends(get_db)
):
    """
    Record payment collection for COD/POD deliveries
    """
    try:
        challan = await db.delivery_challans.find_one({"id": challan_id})
        
        if not challan:
            raise HTTPException(status_code=404, detail="Delivery challan not found")
        
        # Verify delivery person
        if challan.get('delivery_person_id') != delivery_person_id:
            raise HTTPException(status_code=403, detail="You are not assigned to this delivery")
        
        # Check if this is a COD/POD delivery
        if not challan.get('is_cod') and not challan.get('is_pod'):
            raise HTTPException(status_code=400, detail="This is not a COD/POD delivery")
        
        # Record payment details
        payment_details = {
            "amount_received": payment.amount_received,
            "payment_mode": payment.payment_mode,
            "reference_number": payment.reference_number,
            "notes": payment.notes,
            "collected_by": delivery_person_id,
            "collected_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Update challan
        await db.delivery_challans.update_one(
            {"id": challan_id},
            {
                "$set": {
                    "payment_collected": True,
                    "payment_details": payment_details,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Update invoice payment status
        await db.offline_invoices.update_one(
            {"id": challan.get('invoice_id')},
            {
                "$set": {
                    "payment_status": "paid",
                    "payment_collected_at": datetime.now(timezone.utc).isoformat(),
                    "payment_details": payment_details,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )

        # Auto-create voucher so this shows up in admin Vouchers Management
        import uuid as _uuid
        today = datetime.now(timezone.utc)
        receipt_count = await db.vouchers.count_documents({
            "voucher_type": "receipt",
            "created_at": {
                "$gte": today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            }
        })
        receipt_number = f"RCP-{today.strftime('%Y%m%d')}-{receipt_count + 1:04d}"

        linked_invoice = await db.offline_invoices.find_one({"id": challan.get('invoice_id')})

        voucher_data = {
            "id": str(_uuid.uuid4()),
            "voucher_number": receipt_number,
            "voucher_type": "receipt",
            "party_name": linked_invoice.get("customer", {}).get("name", "Unknown") if linked_invoice else "Unknown",
            "amount": payment.amount_received,
            "payment_mode": payment.payment_mode,
            "reference_number": payment.reference_number,
            "description": f"Delivery payment collection for Challan: {challan_id}",
            "voucher_date": today.isoformat(),
            "created_by": delivery_person_id,
            "linked_document": {
                "type": "delivery_challan",
                "number": challan_id,
                "id": challan_id
            },
            "is_advance": False,
            "approval_status": "pending",
            "approved_by": None,
            "approved_at": None,
            "is_locked": True,
            "created_at": today.isoformat(),
            "updated_at": today.isoformat()
        }
        await db.vouchers.insert_one(voucher_data)

        try:
            from realtime_accounting import post_transaction_event
            await post_transaction_event(db, f"voucher_{voucher_data['voucher_type']}", {
                "id": voucher_data["voucher_number"],
                "amount": voucher_data["amount"],
                "tax": 0,
                "payment_method": voucher_data.get("payment_mode", "n/a"),
                "payment_status": "pending",
                "date": voucher_data["created_at"],
                "party": voucher_data.get("party_name", "Unknown"),
                "description": voucher_data.get("description", "")
            })
        except Exception as e:
            print(f"⚠️ Real-time accounting failed for {voucher_data['voucher_number']}: {e}")

        return {
            "status": "success",
            "message": "Payment collected successfully",
            "payment_details": payment_details,
            "voucher_number": receipt_number
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to collect payment: {str(e)}")


@router.post("/{challan_id}/convert-to-invoice")
async def convert_so_to_invoice(challan_id: str, db = Depends(get_db)):
    """
    Convert a Sales Order to Tax Invoice after delivery is complete
    This generates a proper invoice number and updates the document type
    """
    try:
        # Get the challan
        challan = await db.delivery_challans.find_one({"id": challan_id})
        if not challan:
            raise HTTPException(status_code=404, detail="Delivery challan not found")
        
        # Get the linked invoice/SO
        invoice_id = challan.get("invoice_id")
        invoice = await db.offline_invoices.find_one({"id": invoice_id})
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Linked sales order not found")
        
        # Check if already an invoice
        if invoice.get("document_type") == "invoice":
            return {
                "status": "success",
                "message": "Document is already an invoice",
                "invoice_number": invoice.get("invoice_number")
            }
        
        # Generate new invoice number
        store_code = invoice.get("store_code", "GEN")
        
        # Get current fiscal year
        from datetime import datetime
        today = datetime.now()
        if today.month >= 4:
            fiscal_year = f"{str(today.year)[2:]}-{str(today.year + 1)[2:]}"
        else:
            fiscal_year = f"{str(today.year - 1)[2:]}-{str(today.year)[2:]}"
        
        # Get next invoice sequence
        last_invoice = await db.offline_invoices.find_one(
            {
                "store_code": store_code,
                "document_type": "invoice",
                "invoice_number": {"$regex": f"^{store_code}INV"}
            },
            sort=[("created_at", -1)]
        )
        
        if last_invoice:
            # Extract sequence from last invoice number
            last_num = last_invoice.get("invoice_number", "")
            try:
                seq_part = last_num.split("/")[0].replace(f"{store_code}INV", "")
                next_seq = int(seq_part) + 1
            except (ValueError, IndexError):
                next_seq = 1
        else:
            next_seq = 1
        
        new_invoice_number = f"{store_code}INV{str(next_seq).zfill(4)}/{fiscal_year}"
        
        # Update the document
        update_data = {
            "document_type": "invoice",
            "invoice_number": new_invoice_number,
            "original_so_number": invoice.get("invoice_number"),  # Keep reference to original SO
            "status": "delivered",
            "delivery_status": "delivered",
            "converted_at": datetime.now().isoformat(),
            "converted_from_challan": challan_id,
            "updated_at": datetime.now().isoformat()
        }
        
        await db.offline_invoices.update_one(
            {"id": invoice_id},
            {"$set": update_data}
        )
        
        # Update challan to reference new invoice number
        await db.delivery_challans.update_one(
            {"id": challan_id},
            {"$set": {
                "invoice_number": new_invoice_number,
                "converted_to_invoice": True,
                "updated_at": datetime.now().isoformat()
            }}
        )
        
        return {
            "status": "success",
            "message": "Sales Order converted to Invoice successfully",
            "original_so": invoice.get("invoice_number"),
            "new_invoice_number": new_invoice_number
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert to invoice: {str(e)}")


@router.post("/convert-so-to-invoice/{so_id}")
async def convert_so_directly_to_invoice(so_id: str, conversion_data: dict = None, db = Depends(get_db)):
    """
    Convert a Sales Order directly to Tax Invoice (without requiring a delivery challan)
    Used by warehouse team when processing immediate delivery SOs
    """
    from document_numbering_routes import get_next_document_number
    
    try:
        # Parse conversion data
        if conversion_data is None:
            conversion_data = {}
        
        ship_from_address = conversion_data.get("ship_from_address", "")
        e_way_bill_number = conversion_data.get("e_way_bill_number", "")
        force = bool(conversion_data.get("force", False))
        
        # Get the Sales Order
        sales_order = await db.offline_invoices.find_one({"id": so_id})
        
        if not sales_order:
            raise HTTPException(status_code=404, detail="Sales Order not found")
        
        # Check if it's actually a sales order
        if sales_order.get("document_type") == "invoice":
            return {
                "status": "success",
                "message": "Document is already an invoice",
                "invoice_number": sales_order.get("invoice_number")
            }
        
        # Duplicate-invoice safety check: if a store already created an invoice
        # directly for this same customer with a similar total amount recently,
        # warn instead of silently converting the SO into a duplicate invoice.
        # Skipped if force=True (manager confirmed it's not a duplicate).
        if not force:
            customer_phone = (sales_order.get("customer") or {}).get("phone")
            so_total = sales_order.get("total_amount", 0)
            
            if customer_phone:
                potential_duplicate = await db.offline_invoices.find_one({
                    "id": {"$ne": so_id},
                    "document_type": "invoice",
                    "customer.phone": customer_phone,
                    "total_amount": {
                        "$gte": so_total - 1,
                        "$lte": so_total + 1
                    }
                })
                
                if potential_duplicate:
                    return {
                        "status": "duplicate_warning",
                        "message": (
                            f"An invoice ({potential_duplicate.get('invoice_number')}) already "
                            f"exists for this customer with a matching amount (₹{so_total:,.2f}). "
                            f"This sales order may already be fulfilled. "
                            f"Confirm to convert anyway."
                        ),
                        "existing_invoice_number": potential_duplicate.get("invoice_number"),
                        "existing_invoice_id": potential_duplicate.get("id")
                    }
        
        # Get store details
        store_code = sales_order.get("store_code", "GEN")
        store = await db.stores.find_one({"code": store_code})
        store_id = store.get("id") if store else None
        
        # Use the proper document numbering system
        if store_id:
            new_invoice_number = await get_next_document_number(db, store_id, store_code, "invoice")
        else:
            # Fallback if store not found
            today = datetime.now()
            if today.month >= 4:
                fiscal_year = f"{str(today.year)[2:]}-{str(today.year + 1)[2:]}"
            else:
                fiscal_year = f"{str(today.year - 1)[2:]}-{str(today.year)[2:]}"
            
            # Simple fallback numbering
            last_invoice = await db.offline_invoices.find_one(
                {
                    "store_code": store_code,
                    "document_type": "invoice"
                },
                sort=[("created_at", -1)]
            )
            
            if last_invoice:
                try:
                    last_num = last_invoice.get("invoice_number", "")
                    seq_part = last_num.split("/")[-1] if "/" in last_num else last_num.split("-")[-1]
                    next_seq = int(seq_part) + 1
                except (ValueError, IndexError):
                    next_seq = 1
            else:
                next_seq = 1
            
            new_invoice_number = f"{store_code}INV{fiscal_year}/{str(next_seq).zfill(4)}"
        
        # Update the sales order to invoice
        await db.offline_invoices.update_one(
            {"id": so_id},
            {
                "$set": {
                    "document_type": "invoice",
                    "invoice_number": new_invoice_number,
                    "original_so_number": sales_order.get("invoice_number"),
                    "status": "pending_delivery",  # Ready for delivery challan creation
                    "payment_status": sales_order.get("payment_status", "pending"),  # Keep original payment status
                    "ship_from_address": ship_from_address,
                    "e_way_bill_number": e_way_bill_number,
                    "invoice_date": _today_ist(),
                    "so_date": sales_order.get("invoice_date") or (sales_order.get("created_at") or "")[:10],
                    "converted_to_invoice_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Notify the originating store that their SO was converted
        try:
            origin_store = await db.stores.find_one({"code": store_code})
            if origin_store:
                customer_name = sales_order.get("customer", {}).get("name", "Unknown")
                total_amount = sales_order.get("total_amount", 0)
                
                notification = {
                    "id": str(uuid.uuid4()),
                    "type": "so_converted",
                    "title": "Sales Order Converted to Invoice",
                    "message": f"SO #{sales_order.get('invoice_number')} converted to Invoice #{new_invoice_number} - {customer_name} - ₹{total_amount:,.2f}",
                    "store_id": origin_store.get("id"),
                    "store_code": store_code,
                    "reference_id": so_id,
                    "reference_type": "invoice",
                    "action_url": "/store/orders",  # Navigate to orders/invoices tab
                    "priority": "normal",
                    "is_read": False,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                await db.notifications.insert_one(notification)
                print(f"📢 Notification sent to store {store_code} for SO conversion")
        except Exception as notif_error:
            print(f"⚠️ Failed to create store notification: {notif_error}")
        
        return {
            "status": "success",
            "message": "Sales Order converted to Invoice successfully",
            "original_so": sales_order.get("invoice_number"),
            "new_invoice_number": new_invoice_number
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert SO to invoice: {str(e)}")


class DirectChallanItem(BaseModel):
    product_id: str
    product_name: str
    model_number: Optional[str] = None
    hsn_code: Optional[str] = None
    quantity: int
    unit_price: Optional[float] = 0


class CreateDirectChallanRequest(BaseModel):
    """Create delivery challan without SO - for direct material transfers"""
    from_warehouse_id: str
    to_store_id: str
    items: List[DirectChallanItem]
    delivery_person_id: Optional[str] = None
    vehicle_number: Optional[str] = None
    expected_delivery_date: str
    notes: Optional[str] = None
    created_by: str


@router.post("/create-direct")
async def create_direct_challan(request: CreateDirectChallanRequest, db = Depends(get_db)):
    """
    Create delivery challan without SO - for warehouse to store material transfers
    """
    try:
        # Verify warehouse and store exist
        from_warehouse = await db.stores.find_one({"id": request.from_warehouse_id, "is_warehouse": True})
        if not from_warehouse:
            raise HTTPException(status_code=404, detail="Source warehouse not found")
        
        to_store = await db.stores.find_one({"id": request.to_store_id})
        if not to_store:
            raise HTTPException(status_code=404, detail="Destination store not found")
        
        # Generate challan number
        challan_count = await db.delivery_challans.count_documents({})
        challan_number = f"DC-{from_warehouse.get('code', 'WH')}-{datetime.now().strftime('%Y%m%d')}-{challan_count + 1:04d}"
        
        # Calculate total value
        total_value = sum(item.quantity * (item.unit_price or 0) for item in request.items)
        
        # Get delivery person if provided
        delivery_person = None
        if request.delivery_person_id:
            from motor.motor_asyncio import AsyncIOMotorClient
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            db_name = os.environ.get('DB_NAME', 'startup_template')
            client = AsyncIOMotorClient(mongo_url)
            auth_db = client[db_name]
            delivery_person = await auth_db.admin_users.find_one(
                {"id": request.delivery_person_id},
                {"_id": 0, "password": 0}
            )
        
        challan_data = {
            "id": str(uuid.uuid4()),
            "challan_number": challan_number,
            "challan_type": "stock_transfer",  # Not linked to any invoice/SO
            "invoice_id": None,
            "invoice_number": None,
            "from_warehouse_id": request.from_warehouse_id,
            "from_warehouse_name": from_warehouse.get("name"),
            "from_warehouse_code": from_warehouse.get("code"),
            "to_store_id": request.to_store_id,
            "to_store_name": to_store.get("name"),
            "to_store_code": to_store.get("code"),
            "store_code": from_warehouse.get("code"),
            "store_details": {
                "name": from_warehouse.get("name"),
                "address": from_warehouse.get("address"),
                "city": from_warehouse.get("city"),
                "state": from_warehouse.get("state"),
                "pincode": from_warehouse.get("pincode"),
                "gst_number": from_warehouse.get("gst_number")
            },
            "customer": {
                "name": to_store.get("name"),
                "phone": to_store.get("phone"),
                "email": to_store.get("email"),
                "address": to_store.get("address"),
                "city": to_store.get("city"),
                "state": to_store.get("state"),
                "pincode": to_store.get("pincode")
            },
            "items": [item.dict() for item in request.items],
            "total_items": len(request.items),
            "total_quantity": sum(item.quantity for item in request.items),
            "total_amount": round(total_value, 2),
            "is_cod": False,
            "is_pod": False,
            "payment_collected": False,
            "delivery_person_id": request.delivery_person_id,
            "delivery_person_name": delivery_person.get("full_name") if delivery_person else None,
            "delivery_person_phone": delivery_person.get("phone") if delivery_person else None,
            "vehicle_number": request.vehicle_number,
            "expected_delivery_date": request.expected_delivery_date,
            "google_maps_link": None,
            "status": "pending",
            "delivery_photos": [],
            "notes": request.notes,
            "created_by": request.created_by,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "delivered_at": None
        }
        
        await db.delivery_challans.insert_one(challan_data)
        
        return {
            "status": "success",
            "message": f"Direct delivery challan {challan_number} created successfully",
            "challan_id": challan_data["id"],
            "challan_number": challan_number
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create direct challan: {str(e)}")


@router.post("/create-from-transfer/{transfer_id}")
async def create_challan_from_transfer(
    transfer_id: str,
    delivery_person_id: Optional[str] = None,
    vehicle_number: Optional[str] = None,
    created_by: str = "warehouse",
    db = Depends(get_db)
):
    """
    Create delivery challan from an approved stock transfer request
    """
    try:
        transfer = await db.stock_transfers.find_one({"id": transfer_id})
        if not transfer:
            raise HTTPException(status_code=404, detail="Stock transfer not found")
        
        if transfer.get("status") != "approved":
            raise HTTPException(status_code=400, detail="Transfer must be approved before creating challan")
        
        # Generate challan number
        challan_count = await db.delivery_challans.count_documents({})
        challan_number = f"DC-TRF-{datetime.now().strftime('%Y%m%d')}-{challan_count + 1:04d}"
        
        # Get delivery person if provided
        delivery_person = None
        if delivery_person_id:
            from motor.motor_asyncio import AsyncIOMotorClient
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            db_name = os.environ.get('DB_NAME', 'startup_template')
            client = AsyncIOMotorClient(mongo_url)
            auth_db = client[db_name]
            delivery_person = await auth_db.admin_users.find_one(
                {"id": delivery_person_id},
                {"_id": 0, "password": 0}
            )
        
        challan_data = {
            "id": str(uuid.uuid4()),
            "challan_number": challan_number,
            "challan_type": "stock_transfer",
            "stock_transfer_id": transfer_id,
            "transfer_number": transfer.get("transfer_number"),
            "invoice_id": None,
            "invoice_number": None,
            "from_warehouse_id": transfer.get("from_store_id"),
            "from_warehouse_name": transfer.get("from_store_name"),
            "from_warehouse_code": transfer.get("from_store_code"),
            "to_store_id": transfer.get("to_store_id"),
            "to_store_name": transfer.get("to_store_name"),
            "to_store_code": transfer.get("to_store_code"),
            "store_code": transfer.get("from_store_code"),
            "items": transfer.get("items", []),
            "total_items": transfer.get("total_items", 0),
            "total_quantity": transfer.get("total_quantity", 0),
            "total_amount": transfer.get("total_value", 0),
            "is_cod": False,
            "is_pod": False,
            "payment_collected": False,
            "delivery_person_id": delivery_person_id,
            "delivery_person_name": delivery_person.get("full_name") if delivery_person else None,
            "delivery_person_phone": delivery_person.get("phone") if delivery_person else None,
            "vehicle_number": vehicle_number,
            "expected_delivery_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "pending",
            "delivery_photos": [],
            "notes": transfer.get("notes"),
            "created_by": created_by,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "delivered_at": None
        }
        
        await db.delivery_challans.insert_one(challan_data)
        
        # Update transfer status
        await db.stock_transfers.update_one(
            {"id": transfer_id},
            {
                "$set": {
                    "status": "in_transit",
                    "challan_id": challan_data["id"],
                    "challan_number": challan_number,
                    "dispatch_date": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return {
            "status": "success",
            "message": f"Delivery challan {challan_number} created from transfer {transfer.get('transfer_number')}",
            "challan_id": challan_data["id"],
            "challan_number": challan_number
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create challan from transfer: {str(e)}")



# ==================== DELIVERY REPORTS ====================

@router.get("/reports/summary")
async def get_delivery_reports_summary(
    start_date: str = None,
    end_date: str = None,
    db = Depends(get_db)
):
    """Get delivery reports with driver-wise summary"""
    try:
        # Build date filter
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date + "T23:59:59"
        
        query = {}
        if date_filter:
            query["created_at"] = date_filter
        
        # Get all challans
        challans = await db.delivery_challans.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).to_list(None)
        
        # Calculate driver-wise stats
        driver_stats = {}
        for challan in challans:
            driver_id = challan.get("delivery_person_id")
            driver_name = challan.get("delivery_person_name", "Unassigned")
            
            if driver_name not in driver_stats:
                driver_stats[driver_name] = {
                    "driver_id": driver_id,
                    "driver_name": driver_name,
                    "total_deliveries": 0,
                    "completed": 0,
                    "pending": 0,
                    "in_transit": 0,
                    "failed": 0,
                    "total_amount": 0,
                    "collected_amount": 0
                }
            
            driver_stats[driver_name]["total_deliveries"] += 1
            driver_stats[driver_name]["total_amount"] += challan.get("total_amount", 0)
            
            status = challan.get("status", "pending")
            if status == "delivered":
                driver_stats[driver_name]["completed"] += 1
                driver_stats[driver_name]["collected_amount"] += challan.get("collected_amount", challan.get("total_amount", 0))
            elif status == "in_transit":
                driver_stats[driver_name]["in_transit"] += 1
            elif status == "failed":
                driver_stats[driver_name]["failed"] += 1
            else:
                driver_stats[driver_name]["pending"] += 1
        
        # Overall stats
        total_challans = len(challans)
        completed_count = sum(1 for c in challans if c.get("status") == "delivered")
        pending_count = sum(1 for c in challans if c.get("status") in ["pending", "in_transit"])
        failed_count = sum(1 for c in challans if c.get("status") == "failed")
        total_amount = sum(c.get("total_amount", 0) for c in challans)
        collected_amount = sum(c.get("collected_amount", c.get("total_amount", 0)) for c in challans if c.get("status") == "delivered")
        
        return {
            "status": "success",
            "summary": {
                "total_challans": total_challans,
                "completed": completed_count,
                "pending": pending_count,
                "failed": failed_count,
                "total_amount": total_amount,
                "collected_amount": collected_amount,
                "completion_rate": round((completed_count / total_challans * 100) if total_challans > 0 else 0, 1)
            },
            "driver_stats": list(driver_stats.values()),
            "challans": challans
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get delivery reports: {str(e)}")


# ============================================================================
# MATERIAL TRANSFER DELIVERY CHALLAN (Standalone DC without SO/Invoice)
# ============================================================================

class MaterialTransferItem(BaseModel):
    product_id: Optional[str] = None
    product_name: str
    hsn_code: Optional[str] = None
    quantity: int
    unit: str = "pcs"
    rate: Optional[float] = 0  # Optional - for valuation
    serial_numbers: Optional[List[str]] = []  # Serial numbers if applicable
    remarks: Optional[str] = None

class MaterialTransferDCRequest(BaseModel):
    """Create a standalone Delivery Challan for material transfer"""
    transfer_type: str  # store_to_store, warehouse_to_store, store_to_warehouse, warehouse_to_customer, store_to_customer
    from_location: str  # Store code or "WAREHOUSE"
    from_location_name: Optional[str] = None
    to_location: str  # Store code, "WAREHOUSE", or customer name
    to_location_name: Optional[str] = None
    to_location_address: Optional[str] = None
    to_location_city: Optional[str] = None
    to_location_state: Optional[str] = None
    to_location_pincode: Optional[str] = None
    to_contact_name: Optional[str] = None
    to_contact_phone: Optional[str] = None
    items: List[MaterialTransferItem]
    total_value: Optional[float] = 0  # Optional valuation
    e_way_bill_number: Optional[str] = None
    e_way_bill_date: Optional[str] = None
    vehicle_number: Optional[str] = None
    transporter_name: Optional[str] = None
    expected_delivery_date: str
    reason_for_transfer: Optional[str] = None
    notes: Optional[str] = None
    created_by: str

class MaterialTransferReceiveRequest(BaseModel):
    """Confirm receipt of material transfer"""
    challan_id: str
    received_by: str
    received_by_name: str
    received_items: Optional[List[dict]] = None  # Items received with any discrepancies
    goods_condition: str = "good"  # good, damaged, partial
    receiver_remarks: Optional[str] = None
    signature: Optional[str] = None  # Base64 signature

async def generate_material_transfer_dc_number(db, from_location: str):
    """Generate material transfer DC number: MT-{FROM}-YYYYMMDD-XXXX"""
    from datetime import datetime
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")
    prefix = f"MT-{from_location[:4].upper()}"
    
    # Count existing material transfer DCs for today
    count = await db.material_transfer_challans.count_documents({
        "challan_number": {"$regex": f"^{prefix}-{date_str}"}
    })
    
    return f"{prefix}-{date_str}-{count + 1:04d}"


@router.post("/material-transfer/create")
async def create_material_transfer_dc(request: MaterialTransferDCRequest, db = Depends(get_db)):
    """
    Create a standalone Delivery Challan for material transfer.
    Used for: Store↔Store, Warehouse↔Store, Store/Warehouse→Customer transfers.
    Does NOT require a Sales Order or Invoice.
    """
    try:
        # Validate transfer type
        valid_types = ["store_to_store", "warehouse_to_store", "store_to_warehouse", "warehouse_to_customer", "store_to_customer"]
        if request.transfer_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid transfer type. Must be one of: {valid_types}")
        
        # Get from location details
        from_store = None
        if request.from_location != "WAREHOUSE":
            from_store = await db.stores.find_one({"code": request.from_location}, {"_id": 0})
            if not from_store:
                raise HTTPException(status_code=404, detail=f"From location store '{request.from_location}' not found")
        
        # Get to location details (if it's a store)
        to_store = None
        if request.to_location not in ["WAREHOUSE"] and request.transfer_type not in ["warehouse_to_customer", "store_to_customer"]:
            to_store = await db.stores.find_one({"code": request.to_location}, {"_id": 0})
            if not to_store:
                raise HTTPException(status_code=404, detail=f"To location store '{request.to_location}' not found")
        
        # Generate challan number
        challan_number = await generate_material_transfer_dc_number(db, request.from_location)
        
        # Process items
        items_with_details = []
        total_quantity = 0
        total_value = 0
        
        for item in request.items:
            item_value = (item.rate or 0) * item.quantity
            total_value += item_value
            total_quantity += item.quantity
            
            items_with_details.append({
                "product_id": item.product_id,
                "product_name": item.product_name,
                "hsn_code": item.hsn_code,
                "quantity": item.quantity,
                "unit": item.unit,
                "rate": item.rate or 0,
                "value": item_value,
                "serial_numbers": item.serial_numbers or [],
                "remarks": item.remarks
            })
        
        # Create challan document
        challan_data = {
            "id": str(uuid.uuid4()),
            "challan_number": challan_number,
            "challan_type": "material_transfer",
            "transfer_type": request.transfer_type,
            
            # From location
            "from_location": {
                "code": request.from_location,
                "name": request.from_location_name or (from_store.get("name") if from_store else "Central Warehouse"),
                "address": from_store.get("address") if from_store else "Warehouse Address",
                "city": from_store.get("city") if from_store else "Bangalore",
                "state": from_store.get("state") if from_store else "Karnataka",
                "pincode": from_store.get("pincode") if from_store else "",
                "gst_number": from_store.get("gst_number") if from_store else "",
                "is_warehouse": request.from_location == "WAREHOUSE"
            },
            
            # To location
            "to_location": {
                "code": request.to_location,
                "name": request.to_location_name or (to_store.get("name") if to_store else request.to_location),
                "address": request.to_location_address or (to_store.get("address") if to_store else ""),
                "city": request.to_location_city or (to_store.get("city") if to_store else ""),
                "state": request.to_location_state or (to_store.get("state") if to_store else "Karnataka"),
                "pincode": request.to_location_pincode or (to_store.get("pincode") if to_store else ""),
                "contact_name": request.to_contact_name,
                "contact_phone": request.to_contact_phone,
                "is_warehouse": request.to_location == "WAREHOUSE",
                "is_customer": request.transfer_type in ["warehouse_to_customer", "store_to_customer"]
            },
            
            # Items
            "items": items_with_details,
            "total_quantity": total_quantity,
            "total_value": total_value if total_value > 0 else request.total_value,
            
            # Transport details
            "e_way_bill": {
                "number": request.e_way_bill_number,
                "date": request.e_way_bill_date,
                "required": total_value >= 50000  # E-way bill required for >₹50,000
            },
            "vehicle_number": request.vehicle_number,
            "transporter_name": request.transporter_name,
            
            # Dates
            "challan_date": datetime.now(timezone.utc).isoformat(),
            "expected_delivery_date": request.expected_delivery_date,
            
            # Status
            "status": "pending",  # pending, in_transit, delivered, cancelled
            "reason_for_transfer": request.reason_for_transfer,
            "notes": request.notes,
            
            # Tracking
            "created_by": request.created_by,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            
            # Receipt confirmation (filled when received)
            "receipt_confirmation": None
        }
        
        # Insert into database
        await db.material_transfer_challans.insert_one(challan_data)
        
        # Create notification for recipient location
        if to_store or request.transfer_type in ["warehouse_to_customer", "store_to_customer"]:
            notification = {
                "id": str(uuid.uuid4()),
                "type": "material_transfer",
                "title": "Incoming Material Transfer",
                "message": f"Material transfer {challan_number} dispatched from {challan_data['from_location']['name']}",
                "recipient_type": "store" if to_store else "customer",
                "recipient_id": to_store.get("id") if to_store else request.to_location,
                "data": {
                    "challan_id": challan_data["id"],
                    "challan_number": challan_number,
                    "from_location": challan_data["from_location"]["name"],
                    "total_items": total_quantity,
                    "expected_date": request.expected_delivery_date
                },
                "is_read": False,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.notifications.insert_one(notification)
        
        return {
            "status": "success",
            "message": f"Material Transfer DC {challan_number} created successfully",
            "challan_id": challan_data["id"],
            "challan_number": challan_number,
            "e_way_bill_required": challan_data["e_way_bill"]["required"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create material transfer DC: {str(e)}")


@router.get("/material-transfer/list")
async def list_material_transfer_dcs(
    from_location: Optional[str] = None,
    to_location: Optional[str] = None,
    transfer_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """List all material transfer DCs with optional filters"""
    try:
        query = {}
        
        if from_location:
            query["from_location.code"] = from_location
        if to_location:
            query["to_location.code"] = to_location
        if transfer_type:
            query["transfer_type"] = transfer_type
        if status:
            query["status"] = status
        
        skip = (page - 1) * limit
        
        challans = await db.material_transfer_challans.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.material_transfer_challans.count_documents(query)
        
        return {
            "status": "success",
            "challans": challans,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list material transfer DCs: {str(e)}")


@router.get("/material-transfer/{challan_id}")
async def get_material_transfer_dc(challan_id: str, db = Depends(get_db)):
    """Get a specific material transfer DC"""
    try:
        challan = await db.material_transfer_challans.find_one({"id": challan_id}, {"_id": 0})
        
        if not challan:
            raise HTTPException(status_code=404, detail="Material transfer DC not found")
        
        return {
            "status": "success",
            "challan": challan
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get material transfer DC: {str(e)}")


@router.put("/material-transfer/{challan_id}/status")
async def update_material_transfer_status(
    challan_id: str,
    status: str,
    notes: Optional[str] = None,
    db = Depends(get_db)
):
    """Update material transfer DC status"""
    try:
        valid_statuses = ["pending", "in_transit", "delivered", "cancelled"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        result = await db.material_transfer_challans.update_one(
            {"id": challan_id},
            {
                "$set": {
                    "status": status,
                    "status_notes": notes,
                    "status_updated_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Material transfer DC not found")
        
        return {
            "status": "success",
            "message": f"Status updated to {status}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")


@router.post("/material-transfer/{challan_id}/receive")
async def receive_material_transfer(challan_id: str, request: MaterialTransferReceiveRequest, db = Depends(get_db)):
    """
    Confirm receipt of material transfer with goods received confirmation.
    This completes the material transfer process.
    """
    try:
        # Get the challan
        challan = await db.material_transfer_challans.find_one({"id": challan_id}, {"_id": 0})
        
        if not challan:
            raise HTTPException(status_code=404, detail="Material transfer DC not found")
        
        if challan.get("status") == "delivered":
            raise HTTPException(status_code=400, detail="Material transfer already received")
        
        # Create receipt confirmation
        receipt_confirmation = {
            "received_by": request.received_by,
            "received_by_name": request.received_by_name,
            "received_at": datetime.now(timezone.utc).isoformat(),
            "goods_condition": request.goods_condition,
            "receiver_remarks": request.receiver_remarks or "Goods received in good condition",
            "signature": request.signature,
            "items_received": request.received_items or challan.get("items", [])
        }
        
        # Update challan
        await db.material_transfer_challans.update_one(
            {"id": challan_id},
            {
                "$set": {
                    "status": "delivered",
                    "receipt_confirmation": receipt_confirmation,
                    "delivered_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Update stock at destination (if store to store or warehouse to store)
        if challan.get("transfer_type") in ["warehouse_to_store", "store_to_store"]:
            to_store_code = challan.get("to_location", {}).get("code")
            if to_store_code and to_store_code != "WAREHOUSE":
                # Add stock at destination
                for item in challan.get("items", []):
                    if item.get("product_id"):
                        await db.inventory.update_one(
                            {"product_id": item["product_id"], "store_code": to_store_code},
                            {
                                "$inc": {"quantity": item["quantity"]},
                                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                            },
                            upsert=True
                        )
        
        # Deduct stock from source (if store to store or store to warehouse)
        if challan.get("transfer_type") in ["store_to_store", "store_to_warehouse", "store_to_customer"]:
            from_store_code = challan.get("from_location", {}).get("code")
            if from_store_code and from_store_code != "WAREHOUSE":
                for item in challan.get("items", []):
                    if item.get("product_id"):
                        await db.inventory.update_one(
                            {"product_id": item["product_id"], "store_code": from_store_code},
                            {
                                "$inc": {"quantity": -item["quantity"]},
                                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                            }
                        )
        
        return {
            "status": "success",
            "message": f"Material transfer {challan.get('challan_number')} received successfully",
            "challan_id": challan_id,
            "received_at": receipt_confirmation["received_at"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to receive material transfer: {str(e)}")


@router.get("/material-transfer/{challan_id}/print")
async def get_material_transfer_print_data(challan_id: str, db = Depends(get_db)):
    """Get material transfer DC data formatted for printing"""
    try:
        challan = await db.material_transfer_challans.find_one({"id": challan_id}, {"_id": 0})
        
        if not challan:
            raise HTTPException(status_code=404, detail="Material transfer DC not found")
        
        # Format for printing
        print_data = {
            "challan_number": challan.get("challan_number"),
            "challan_date": challan.get("challan_date"),
            "transfer_type": challan.get("transfer_type", "").replace("_", " ").title(),
            
            "from": challan.get("from_location", {}),
            "to": challan.get("to_location", {}),
            
            "items": challan.get("items", []),
            "total_quantity": challan.get("total_quantity", 0),
            "total_value": challan.get("total_value", 0),
            
            "e_way_bill": challan.get("e_way_bill", {}),
            "vehicle_number": challan.get("vehicle_number"),
            "transporter_name": challan.get("transporter_name"),
            
            "reason": challan.get("reason_for_transfer"),
            "notes": challan.get("notes"),
            
            "status": challan.get("status"),
            "receipt_confirmation": challan.get("receipt_confirmation"),
            
            "created_by": challan.get("created_by"),
            "created_at": challan.get("created_at")
        }
        
        return {
            "status": "success",
            "print_data": print_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get print data: {str(e)}")


def _today_ist() -> str:
    from datetime import timedelta as _td
    return datetime.now(timezone(_td(hours=5, minutes=30))).strftime("%Y-%m-%d")
