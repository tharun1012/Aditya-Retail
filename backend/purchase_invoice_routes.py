from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from database import get_db
import uuid

router = APIRouter(prefix="/purchase-invoices", tags=["Purchase Invoices"])


class PurchaseInvoiceItem(BaseModel):
    product_name: str
    hsn_code: Optional[str] = None
    quantity: int
    unit_price: float
    tax_rate: float = 18.0
    discount_percent: float = 0


class PurchaseInvoiceCreate(BaseModel):
    warehouse_id: str
    vendor_name: str
    vendor_gst: Optional[str] = None
    vendor_address: Optional[str] = None
    vendor_invoice_number: str
    vendor_invoice_date: str
    grn_id: Optional[str] = None  # Link to GRN if exists
    items: List[PurchaseInvoiceItem]
    subtotal: float
    cgst_amount: float = 0
    sgst_amount: float = 0
    igst_amount: float = 0
    total_amount: float
    payment_status: str = "pending"  # pending, partial, paid
    payment_due_date: Optional[str] = None
    notes: Optional[str] = None
    entered_by: str


@router.post("/create")
async def create_purchase_invoice(invoice: PurchaseInvoiceCreate, db=Depends(get_db)):
    """Create a new purchase invoice/bill entry"""
    try:
        # Generate purchase invoice number
        today = datetime.now()
        fiscal_year = f"{str(today.year)[2:]}-{str(today.year + 1)[2:]}" if today.month >= 4 else f"{str(today.year - 1)[2:]}-{str(today.year)[2:]}"
        
        # Get warehouse code
        warehouse = await db.stores.find_one({"id": invoice.warehouse_id}, {"_id": 0, "code": 1})
        warehouse_code = warehouse.get("code", "WH") if warehouse else "WH"
        
        # Get next sequence
        counter = await db.counters.find_one_and_update(
            {"_id": f"purchase_invoice_{warehouse_code}"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        )
        seq = counter.get("seq", 1)
        
        pi_number = f"{warehouse_code}-PI-{fiscal_year}-{str(seq).zfill(4)}"
        
        # Calculate tax breakup per item
        items_with_tax = []
        for item in invoice.items:
            base_price = item.unit_price * item.quantity
            discount = base_price * (item.discount_percent / 100)
            taxable = base_price - discount
            tax_amount = taxable * (item.tax_rate / 100)
            
            items_with_tax.append({
                "product_name": item.product_name,
                "hsn_code": item.hsn_code,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "discount_percent": item.discount_percent,
                "discount_amount": round(discount, 2),
                "taxable_amount": round(taxable, 2),
                "tax_rate": item.tax_rate,
                "tax_amount": round(tax_amount, 2),
                "total": round(taxable + tax_amount, 2)
            })
        
        invoice_data = {
            "id": str(uuid.uuid4()),
            "pi_number": pi_number,
            "warehouse_id": invoice.warehouse_id,
            "warehouse_code": warehouse_code,
            "vendor_name": invoice.vendor_name,
            "vendor_gst": invoice.vendor_gst,
            "vendor_address": invoice.vendor_address,
            "vendor_invoice_number": invoice.vendor_invoice_number,
            "vendor_invoice_date": invoice.vendor_invoice_date,
            "grn_id": invoice.grn_id,
            "items": items_with_tax,
            "subtotal": round(invoice.subtotal, 2),
            "cgst_amount": round(invoice.cgst_amount, 2),
            "sgst_amount": round(invoice.sgst_amount, 2),
            "igst_amount": round(invoice.igst_amount, 2),
            "total_tax": round(invoice.cgst_amount + invoice.sgst_amount + invoice.igst_amount, 2),
            "total_amount": round(invoice.total_amount, 2),
            "payment_status": invoice.payment_status,
            "payment_due_date": invoice.payment_due_date,
            "amount_paid": 0,
            "balance_due": round(invoice.total_amount, 2),
            "notes": invoice.notes,
            "entered_by": invoice.entered_by,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.purchase_invoices.insert_one(invoice_data)
        
        return {
            "status": "success",
            "message": "Purchase invoice created successfully",
            "pi_number": pi_number,
            "pi_id": invoice_data["id"],
            "total_amount": invoice_data["total_amount"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create purchase invoice: {str(e)}")


@router.get("/")
async def list_purchase_invoices(
    warehouse_id: Optional[str] = None,
    vendor_name: Optional[str] = None,
    payment_status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db=Depends(get_db)
):
    """List purchase invoices with filters"""
    try:
        query = {"status": "active"}
        
        if warehouse_id:
            query["warehouse_id"] = warehouse_id
        if vendor_name:
            query["vendor_name"] = {"$regex": vendor_name, "$options": "i"}
        if payment_status:
            query["payment_status"] = payment_status
        if from_date:
            query["vendor_invoice_date"] = {"$gte": from_date}
        if to_date:
            if "vendor_invoice_date" in query:
                query["vendor_invoice_date"]["$lte"] = to_date
            else:
                query["vendor_invoice_date"] = {"$lte": to_date}
        
        skip = (page - 1) * limit
        
        invoices = await db.purchase_invoices.find(
            query, {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.purchase_invoices.count_documents(query)
        
        # Calculate summary
        all_invoices = await db.purchase_invoices.find(query, {"_id": 0, "total_amount": 1, "amount_paid": 1, "payment_status": 1}).to_list(None)
        total_value = sum(inv.get("total_amount", 0) for inv in all_invoices)
        total_paid = sum(inv.get("amount_paid", 0) for inv in all_invoices)
        pending_count = len([inv for inv in all_invoices if inv.get("payment_status") == "pending"])
        
        return {
            "status": "success",
            "purchase_invoices": invoices,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
            "summary": {
                "total_value": round(total_value, 2),
                "total_paid": round(total_paid, 2),
                "balance_due": round(total_value - total_paid, 2),
                "pending_count": pending_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pi_id}")
async def get_purchase_invoice(pi_id: str, db=Depends(get_db)):
    """Get a specific purchase invoice"""
    try:
        invoice = await db.purchase_invoices.find_one({"id": pi_id}, {"_id": 0})
        if not invoice:
            raise HTTPException(status_code=404, detail="Purchase invoice not found")
        
        # Get linked GRN if exists
        grn = None
        if invoice.get("grn_id"):
            grn = await db.grns.find_one({"id": invoice["grn_id"]}, {"_id": 0})
        
        return {
            "status": "success",
            "purchase_invoice": invoice,
            "linked_grn": grn
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{pi_id}/record-payment")
async def record_payment(pi_id: str, payment_data: dict, db=Depends(get_db)):
    """Record a payment against a purchase invoice"""
    try:
        invoice = await db.purchase_invoices.find_one({"id": pi_id})
        if not invoice:
            raise HTTPException(status_code=404, detail="Purchase invoice not found")
        
        amount = payment_data.get("amount", 0)
        payment_method = payment_data.get("payment_method", "bank_transfer")
        reference = payment_data.get("reference", "")
        payment_date = payment_data.get("payment_date", datetime.now().strftime("%Y-%m-%d"))
        
        new_paid = invoice.get("amount_paid", 0) + amount
        new_balance = invoice.get("total_amount", 0) - new_paid
        
        # Determine payment status
        if new_balance <= 0:
            new_status = "paid"
        elif new_paid > 0:
            new_status = "partial"
        else:
            new_status = "pending"
        
        # Record payment history
        payment_record = {
            "id": str(uuid.uuid4()),
            "amount": amount,
            "payment_method": payment_method,
            "reference": reference,
            "payment_date": payment_date,
            "recorded_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.purchase_invoices.update_one(
            {"id": pi_id},
            {
                "$set": {
                    "amount_paid": round(new_paid, 2),
                    "balance_due": round(max(0, new_balance), 2),
                    "payment_status": new_status,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                "$push": {"payment_history": payment_record}
            }
        )

        # Auto-create voucher so this shows up in admin Vouchers Management
        today = datetime.now(timezone.utc)
        payment_count = await db.vouchers.count_documents({
            "voucher_type": "payment",
            "created_at": {
                "$gte": today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            }
        })
        voucher_number = f"PMT-{today.strftime('%Y%m%d')}-{payment_count + 1:04d}"

        voucher_data = {
            "id": payment_record["id"],
            "voucher_number": voucher_number,
            "voucher_type": "payment",
            "party_name": invoice.get("vendor_name", invoice.get("party_name", "Unknown")),
            "amount": amount,
            "payment_mode": payment_method,
            "reference_number": reference,
            "description": f"Payment for Purchase Invoice: {invoice.get('invoice_number', pi_id)}",
            "voucher_date": payment_date,
            "created_by": payment_data.get("created_by", "system"),
            "linked_document": {
                "type": "purchase_invoice",
                "number": invoice.get("invoice_number", pi_id),
                "id": pi_id
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

        return {
            "status": "success",
            "message": "Payment recorded successfully",
            "voucher_number": voucher_number,
            "amount_paid": round(new_paid, 2),
            "balance_due": round(max(0, new_balance), 2),
            "payment_status": new_status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/payables")
async def get_payables_summary(warehouse_id: Optional[str] = None, db=Depends(get_db)):
    """Get accounts payable summary"""
    try:
        query = {"status": "active"}
        if warehouse_id:
            query["warehouse_id"] = warehouse_id
        
        invoices = await db.purchase_invoices.find(query, {"_id": 0}).to_list(None)
        
        # Group by vendor
        vendor_payables = {}
        for inv in invoices:
            vendor = inv.get("vendor_name", "Unknown")
            if vendor not in vendor_payables:
                vendor_payables[vendor] = {
                    "vendor_name": vendor,
                    "total_invoices": 0,
                    "total_amount": 0,
                    "amount_paid": 0,
                    "balance_due": 0
                }
            vendor_payables[vendor]["total_invoices"] += 1
            vendor_payables[vendor]["total_amount"] += inv.get("total_amount", 0)
            vendor_payables[vendor]["amount_paid"] += inv.get("amount_paid", 0)
            vendor_payables[vendor]["balance_due"] += inv.get("balance_due", 0)
        
        # Sort by balance due
        sorted_vendors = sorted(vendor_payables.values(), key=lambda x: x["balance_due"], reverse=True)
        
        # Aging analysis
        today = datetime.now().date()
        aging = {"current": 0, "30_days": 0, "60_days": 0, "90_plus": 0}
        
        for inv in invoices:
            if inv.get("payment_status") == "paid":
                continue
            balance = inv.get("balance_due", 0)
            due_date_str = inv.get("payment_due_date") or inv.get("vendor_invoice_date")
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str[:10], "%Y-%m-%d").date()
                    days_overdue = (today - due_date).days
                    if days_overdue <= 0:
                        aging["current"] += balance
                    elif days_overdue <= 30:
                        aging["30_days"] += balance
                    elif days_overdue <= 60:
                        aging["60_days"] += balance
                    else:
                        aging["90_plus"] += balance
                except Exception:
                    aging["current"] += balance
        
        total_payable = sum(v["balance_due"] for v in vendor_payables.values())
        
        return {
            "status": "success",
            "total_payable": round(total_payable, 2),
            "vendor_wise": sorted_vendors[:20],
            "aging_analysis": {
                "current": round(aging["current"], 2),
                "overdue_30_days": round(aging["30_days"], 2),
                "overdue_60_days": round(aging["60_days"], 2),
                "overdue_90_plus": round(aging["90_plus"], 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
