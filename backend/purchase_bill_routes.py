"""
Purchase Bill/Invoice Management Routes
Handles actual vendor invoices (different from Purchase Orders)
Includes AI-powered invoice scanning
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from database import get_db
from dotenv import load_dotenv
from pathlib import Path
import uuid
import os
import tempfile
import base64
import logging

# Import notification helper
from notifications_routes import notify_stock_inward


def compute_gst_split(vendor_gst_number: str, total_tax: float, own_state_code: str = "29") -> dict:
    """
    Determines CGST+SGST vs IGST based on the vendor's GSTIN state code
    (first 2 digits), compared against adityaretail's own registered
    state code (29 = Karnataka). This is now the single source of truth
    for GST split - frontend-sent cgst/sgst/igst values are ignored.
    """
    vendor_state_code = (vendor_gst_number or "")[:2]
    is_interstate = vendor_state_code.isdigit() and vendor_state_code != own_state_code

    if is_interstate:
        return {"cgst": 0.0, "sgst": 0.0, "igst": round(total_tax, 2)}
    else:
        return {"cgst": round(total_tax / 2, 2), "sgst": round(total_tax / 2, 2), "igst": 0.0}



# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

router = APIRouter(prefix="/purchase-bills", tags=["Purchase Bills"])
logger = logging.getLogger(__name__)

# Create uploads directory for invoices
INVOICE_UPLOAD_DIR = "/app/backend/uploads/purchase_invoices"
os.makedirs(INVOICE_UPLOAD_DIR, exist_ok=True)


class PurchaseBillItem(BaseModel):
    product_name: str
    hsn_code: Optional[str] = ""
    quantity: int = 1
    rate: float = 0
    discount_percent: float = 0
    tax_rate: float = 18.0
    taxable_amount: Optional[float] = 0
    tax_amount: Optional[float] = 0
    total: Optional[float] = 0


class VendorInfo(BaseModel):
    name: str
    phone: Optional[str] = ""
    email: Optional[str] = ""
    gst_number: Optional[str] = ""
    msme_udyam_number: Optional[str] = ""  # MSME/Udyam registration number
    address: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    pincode: Optional[str] = ""


class PurchaseBillCreate(BaseModel):
    bill_number: str
    bill_date: str
    po_number: Optional[str] = ""  # Reference to PO or "VERBAL" for direct purchases
    po_reference: Optional[str] = ""  # Original PO selection for reference
    is_verbal_purchase: Optional[bool] = False  # True if no PO (direct purchase)
    vendor: VendorInfo
    items: List[PurchaseBillItem]
    subtotal: float = 0
    cgst: float = 0
    sgst: float = 0
    igst: float = 0
    total_tax: float = 0
    other_charges: float = 0
    round_off: float = 0
    grand_total: float = 0
    payment_mode: str = "credit"
    payment_status: str = "pending"
    due_date: Optional[str] = None
    notes: Optional[str] = ""
    invoice_file_url: Optional[str] = None
    bypass_po_check: bool = False  # Only super_admin can set this to True
    tds: Optional[Dict[str, Any]] = None  # {section, code, rate_applied, deducted, amount_deducted}


class PurchaseBillResponse(BaseModel):
    status: str
    message: str
    bill: Optional[Dict[str, Any]] = None


# ============ CRUD OPERATIONS ============

@router.get("/")
async def get_all_purchase_bills(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    vendor: Optional[str] = None,
    search: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    gst_number: Optional[str] = None,
    db = Depends(get_db)
):
    """
    Get all purchase bills with pagination and comprehensive filters
    
    Filters:
    - status: Payment status (pending, partial, paid)
    - vendor: Vendor name (partial match)
    - search: Search across bill_number, vendor name, GST, items (searches ALL records)
    - from_date: Filter bills from this date (YYYY-MM-DD)
    - to_date: Filter bills until this date (YYYY-MM-DD)
    - gst_number: Filter by vendor GST number (partial match)
    """
    try:
        query = {}
        
        # Payment status filter
        if status and status != 'all':
            query["payment_status"] = status.lower()
        
        # Vendor name filter (exact vendor parameter for backward compatibility)
        if vendor:
            query["vendor.name"] = {"$regex": vendor, "$options": "i"}
        
        # GST number filter
        if gst_number:
            query["vendor.gst_number"] = {"$regex": gst_number, "$options": "i"}
        
        # Date range filter
        if from_date or to_date:
            date_query = {}
            if from_date:
                date_query["$gte"] = from_date
            if to_date:
                date_query["$lte"] = to_date
            if date_query:
                query["bill_date"] = date_query
        
        # Comprehensive search (searches across multiple fields - ALL records)
        if search:
            search_regex = {"$regex": search, "$options": "i"}
            query["$or"] = [
                {"bill_number": search_regex},
                {"vendor.name": search_regex},
                {"vendor.gst_number": search_regex},
                {"po_number": search_regex},
                {"items.product_name": search_regex},
                {"notes": search_regex}
            ]
        
        skip = (page - 1) * limit
        
        # Sort by bill_date descending (newest first), then by created_at
        bills = await db.purchase_bills.find(query).sort([
            ("bill_date", -1),
            ("created_at", -1)
        ]).skip(skip).limit(limit).to_list(length=limit)
        
        total = await db.purchase_bills.count_documents(query)
        
        # Convert ObjectId to string
        for bill in bills:
            bill.pop('_id', None)
        
        return {
            "status": "success",
            "bills": bills,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit,
            "filters_applied": {
                "status": status,
                "vendor": vendor,
                "search": search,
                "from_date": from_date,
                "to_date": to_date,
                "gst_number": gst_number
            }
        }
    except Exception as e:
        logger.error(f"Failed to fetch purchase bills: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{bill_id}")
async def get_purchase_bill(bill_id: str, db = Depends(get_db)):
    """Get a single purchase bill by ID"""
    try:
        bill = await db.purchase_bills.find_one({"id": bill_id})
        if not bill:
            raise HTTPException(status_code=404, detail="Purchase bill not found")
        
        bill.pop('_id', None)
        return {"status": "success", "bill": bill}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create")
async def create_purchase_bill(bill_data: PurchaseBillCreate, db = Depends(get_db)):
    """Create a new purchase bill - PO is MANDATORY unless bypassed by super_admin"""
    try:
        # ========== PO VALIDATION ==========
        # Allow "VERBAL" for direct purchases without PO
        is_verbal_purchase = bill_data.po_number == "VERBAL" or getattr(bill_data, 'is_verbal_purchase', False)
        
        if not bill_data.po_number and not bill_data.bypass_po_check and not is_verbal_purchase:
            raise HTTPException(
                status_code=400, 
                detail="Please select a Purchase Order or choose 'VERBAL' for direct purchases."
            )
        
        # Validate PO exists if provided (skip for VERBAL purchases)
        if bill_data.po_number and bill_data.po_number != "VERBAL" and not is_verbal_purchase:
            po_exists = await db.purchases.find_one({"po_number": bill_data.po_number}) \
                or await db.purchase_orders.find_one({"po_number": bill_data.po_number})
            if not po_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"Purchase Order {bill_data.po_number} not found. Please select a valid PO or choose 'VERBAL'."
                )
        
        # Check for duplicate bill number from same vendor
        existing = await db.purchase_bills.find_one({
            "bill_number": bill_data.bill_number,
            "vendor.gst_number": bill_data.vendor.gst_number
        })
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"Bill {bill_data.bill_number} from this vendor already exists"
            )
        
        # Calculate item totals. Rates are GST-INCLUSIVE (the vendor's actual
        # invoice amount), so tax is extracted out of the entered rate rather
        # than added on top.
        items = []
        subtotal = 0
        total_tax = 0
        
        for item in bill_data.items:
            item_gross = item.quantity * item.rate
            discount_amt = item_gross * (item.discount_percent / 100)
            inclusive_after_discount = item_gross - discount_amt
            tax_rate = item.tax_rate or 0
            taxable = inclusive_after_discount / (1 + tax_rate / 100)
            tax_amt = inclusive_after_discount - taxable
            item_total = inclusive_after_discount
            
            items.append({
                "product_name": item.product_name,
                "hsn_code": item.hsn_code,
                "quantity": item.quantity,
                "rate": item.rate,
                "discount_percent": item.discount_percent,
                "tax_rate": item.tax_rate,
                "taxable_amount": round(taxable, 2),
                "tax_amount": round(tax_amt, 2),
                "total": round(item_total, 2)
            })
            subtotal += taxable
            total_tax += tax_amt
        
        # ========== MSME PAYMENT COMPLIANCE ==========
        # If vendor has MSME/Udyam number, set due date to 45 days as per MSMED Act
        is_msme_vendor = bool(bill_data.vendor.msme_udyam_number)
        bill_date = datetime.strptime(bill_data.bill_date, "%Y-%m-%d")
        
        if is_msme_vendor and not bill_data.due_date:
            # MSME Act: Payment must be made within 45 days
            msme_due_date = bill_date + timedelta(days=45)
            due_date_str = msme_due_date.strftime("%Y-%m-%d")
        else:
            due_date_str = bill_data.due_date
        
        # Create bill document
        bill_doc = {
            "id": str(uuid.uuid4()),
            "bill_number": bill_data.bill_number,
            "bill_date": bill_data.bill_date,
            "po_number": None if is_verbal_purchase else bill_data.po_number,
            "po_reference": bill_data.po_number,  # Keep original selection for reference
            "is_verbal_purchase": is_verbal_purchase,
            "vendor": {
                **bill_data.vendor.dict(),
                "is_msme": is_msme_vendor
            },
            "items": items,
            "subtotal": round(subtotal, 2),
            # Use frontend-computed values when explicitly provided (including
            # legitimate 0 for an interstate bill's cgst/sgst, or an
            # intrastate bill's igst) rather than treating 0 as "not sent".
            **compute_gst_split(bill_data.vendor.gst_number, total_tax),
            "total_tax": round(total_tax, 2),
            "other_charges": bill_data.other_charges,
            "round_off": bill_data.round_off,
            "payment_mode": bill_data.payment_mode,
            "payment_status": bill_data.payment_status,
            "due_date": due_date_str,
            "is_msme_vendor": is_msme_vendor,
            "msme_compliance_required": is_msme_vendor,
            "notes": bill_data.notes,
            "invoice_file_url": bill_data.invoice_file_url,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "created_by": "admin",
            "source": "manual",
            "po_bypassed": bill_data.bypass_po_check,
            "tds": bill_data.tds
        }

        # subtotal here is already the tax-EXCLUSIVE taxable amount (tax was
        # extracted from the inclusive rate above), so this reconstructs the
        # original inclusive invoice amount before any TDS deduction.
        invoice_total_before_tds = round(subtotal + total_tax + bill_data.other_charges + bill_data.round_off, 2)
        tds_amount_deducted = (
            bill_data.tds.get("amount_deducted", 0)
            if bill_data.tds and bill_data.tds.get("deducted") else 0
        )
        bill_doc["invoice_total_before_tds"] = invoice_total_before_tds
        # grand_total is what's shown everywhere (dashboard, pending amount,
        # reports, bill list/details) - reflects TDS deduction when applicable.
        bill_doc["grand_total"] = round(invoice_total_before_tds - tds_amount_deducted, 2)
        
        await db.purchase_bills.insert_one(bill_doc)

        # Real-time accounting: is_inter_state derived from the same
        # compute_gst_split() result already merged into bill_doc -
        # igst > 0 means it was classified inter-state.
        try:
            from realtime_accounting import post_transaction_event
            await post_transaction_event(db, "purchase_bill", {
                "id": bill_doc["bill_number"],
                "amount": bill_doc["grand_total"],
                "tax": bill_doc["total_tax"],
                "is_inter_state": bill_doc["igst"] > 0,
                "igst": bill_doc["igst"],
                "cgst": bill_doc["cgst"],
                "sgst": bill_doc["sgst"],
                "payment_method": bill_doc["payment_mode"],
                "payment_status": bill_doc["payment_status"],
                "date": bill_doc["created_at"],
                "items": bill_doc["items"]
            })
        except Exception as e:
            print(f"⚠️ Real-time accounting failed for {bill_doc['bill_number']}: {e}")

        bill_doc.pop('_id', None)

        # Remember vendor details + last TDS usage for future autosuggest
        try:
            vendor_dict = bill_data.vendor.dict()
            profile_doc = {
                "vendor_name": vendor_dict.get("name"),
                "phone": vendor_dict.get("phone", ""),
                "email": vendor_dict.get("email", ""),
                "gst_number": vendor_dict.get("gst_number", ""),
                "msme_udyam_number": vendor_dict.get("msme_udyam_number", ""),
                "address": vendor_dict.get("address", ""),
                "city": vendor_dict.get("city", ""),
                "state": vendor_dict.get("state", ""),
                "pincode": vendor_dict.get("pincode", ""),
                "tds": bill_data.tds,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            if vendor_dict.get("name"):
                existing_profile = await db.vendor_tds_profiles.find_one(
                    {"vendor_name": {"$regex": f"^{vendor_dict['name']}$", "$options": "i"}}
                )
                if existing_profile:
                    await db.vendor_tds_profiles.update_one(
                        {"id": existing_profile["id"]}, {"$set": profile_doc}
                    )
                else:
                    profile_doc["id"] = str(uuid.uuid4())
                    profile_doc["created_at"] = profile_doc["updated_at"]
                    await db.vendor_tds_profiles.insert_one(profile_doc)
        except Exception as vendor_profile_error:
            logger.warning(f"Vendor TDS profile upsert failed (non-blocking): {vendor_profile_error}")
        
        # ========== AUTO-MATCH WITH GRN ==========
        # Try to find a matching GRN by vendor invoice number
        matched_grn = None
        if bill_data.bill_number:
            matched_grn = await db.grn.find_one({
                "vendor_invoice_number": bill_data.bill_number,
                "linked_bill_id": {"$exists": False}  # Not already matched
            })
            
            if matched_grn:
                # Link both documents
                await db.purchase_bills.update_one(
                    {"id": bill_doc["id"]},
                    {
                        "$set": {
                            "linked_grn_id": matched_grn["id"],
                            "linked_grn_number": matched_grn["grn_number"],
                            "grn_matched_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                
                await db.grn.update_one(
                    {"id": matched_grn["id"]},
                    {
                        "$set": {
                            "linked_bill_id": bill_doc["id"],
                            "linked_bill_number": bill_data.bill_number,
                            "bill_matched_at": datetime.now(timezone.utc).isoformat(),
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
        
        # Send stock inward notification
        try:
            total_quantity = sum(item["quantity"] for item in items)
            inward_data = {
                "grn_number": bill_data.bill_number,
                "supplier_name": bill_data.vendor.name,
                "total_items": len(items),
                "total_quantity": total_quantity,
                "store_id": bill_doc.get("store_id"),
                "store_name": bill_doc.get("store_name", "Warehouse"),
                "warehouse_id": bill_doc.get("warehouse_id"),
                "purchase_bill_id": bill_doc["id"]
            }
            await notify_stock_inward(db, inward_data)
        except Exception as notify_error:
            logger.warning(f"Failed to send stock inward notification: {notify_error}")
        
        return {
            "status": "success",
            "message": f"Purchase Bill {bill_data.bill_number} created successfully",
            "bill": bill_doc,
            "msme_compliance": {
                "is_msme_vendor": is_msme_vendor,
                "due_date": due_date_str,
                "days_to_pay": 45 if is_msme_vendor else None
            },
            "auto_matched": matched_grn is not None,
            "matched_grn_number": matched_grn["grn_number"] if matched_grn else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create purchase bill: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ GRN MATCHING ENDPOINTS ============

@router.get("/grn-matching/unmatched-grns")
async def get_unmatched_grns(
    page: int = 1,
    limit: int = 20,
    db = Depends(get_db)
):
    """Get GRNs that haven't been matched to any Purchase Bill"""
    try:
        # Match GRNs where linked_bill_id doesn't exist OR is null/empty
        query = {
            "$or": [
                {"linked_bill_id": {"$exists": False}},
                {"linked_bill_id": None},
                {"linked_bill_id": ""},
                {"linked_bill_id": {"$eq": None}}
            ]
        }
        
        skip = (page - 1) * limit
        
        grns = await db.grn.find(
            query, {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.grn.count_documents(query)
        
        logger.info(f"Unmatched GRNs query: found {len(grns)} of {total} total")
        
        return {
            "status": "success",
            "grns": grns,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error fetching unmatched GRNs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/grn-matching/debug")
async def debug_grn_matching(db = Depends(get_db)):
    """Debug endpoint to check GRN data state - checks ALL possible collections"""
    try:
        # Get list of ALL collections in the database
        all_collections = await db.list_collection_names()
        
        # Check various possible GRN collection names
        possible_grn_collections = ['grn', 'grns', 'goods_receipts', 'goods_receipt_notes', 'GRN', 'GRNs']
        grn_data = {}
        
        for coll_name in possible_grn_collections:
            try:
                count = await db[coll_name].count_documents({})
                if count > 0:
                    sample = await db[coll_name].find_one({}, {"_id": 0})
                    grn_data[coll_name] = {
                        "count": count,
                        "sample_fields": list(sample.keys()) if sample else [],
                        "sample_grn_number": sample.get("grn_number") if sample else None
                    }
            except Exception:
                pass
        
        # Also check any collection that might contain "grn" in its name
        grn_related_collections = [c for c in all_collections if 'grn' in c.lower()]
        
        # Check the main grn collection specifically
        grn_count = await db.grn.count_documents({})
        
        # Check unmatched query
        unmatched_query = {
            "$or": [
                {"linked_bill_id": {"$exists": False}},
                {"linked_bill_id": None},
                {"linked_bill_id": ""},
                {"linked_bill_id": {"$eq": None}}
            ]
        }
        unmatched_count = await db.grn.count_documents(unmatched_query)
        
        # Get sample from grn collection
        sample_grn = await db.grn.find_one({}, {"_id": 0})
        
        # Get all GRN numbers if any exist
        all_grn_numbers = []
        if grn_count > 0:
            grns = await db.grn.find({}, {"_id": 0, "grn_number": 1}).limit(20).to_list(None)
            all_grn_numbers = [g.get("grn_number") for g in grns]
        
        return {
            "status": "success",
            "debug_data": {
                "all_collections_in_db": all_collections,
                "grn_related_collections": grn_related_collections,
                "collections_with_grn_data": grn_data,
                "grn_collection_count": grn_count,
                "unmatched_grns": unmatched_count,
                "all_grn_numbers": all_grn_numbers,
                "sample_grn": {
                    "grn_number": sample_grn.get("grn_number") if sample_grn else None,
                    "linked_bill_id": sample_grn.get("linked_bill_id") if sample_grn else None,
                    "vendor_name": sample_grn.get("vendor_name") if sample_grn else None,
                } if sample_grn else None
            }
        }
    except Exception as e:
        logger.error(f"Debug error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/grn-matching/all-grns")
async def get_all_grns_for_matching(
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get ALL GRNs for debugging - shows all GRNs regardless of linked status"""
    try:
        skip = (page - 1) * limit
        
        grns = await db.grn.find(
            {}, {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.grn.count_documents({})
        
        logger.info(f"All GRNs query: found {len(grns)} of {total} total")
        
        return {
            "status": "success",
            "grns": grns,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total > 0 else 0,
            "debug_info": {
                "query": "all GRNs",
                "collection": "grn"
            }
        }
    except Exception as e:
        logger.error(f"Error fetching all GRNs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/grn-matching/unmatched-bills")
async def get_unmatched_bills(
    page: int = 1,
    limit: int = 20,
    db = Depends(get_db)
):
    """Get Purchase Bills that haven't been matched to any GRN"""
    try:
        query = {
            "linked_grn_id": {"$exists": False}
        }
        
        skip = (page - 1) * limit
        
        bills = await db.purchase_bills.find(
            query, {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.purchase_bills.count_documents(query)
        
        return {
            "status": "success",
            "bills": bills,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/grn-matching/link")
async def manually_link_grn_to_bill(
    grn_id: str,
    bill_id: str,
    db = Depends(get_db)
):
    """Manually link a GRN to a Purchase Bill"""
    try:
        # Verify both exist
        grn = await db.grn.find_one({"id": grn_id})
        if not grn:
            raise HTTPException(status_code=404, detail="GRN not found")
        
        bill = await db.purchase_bills.find_one({"id": bill_id})
        if not bill:
            raise HTTPException(status_code=404, detail="Purchase Bill not found")
        
        # Check if already linked
        if grn.get("linked_bill_id"):
            raise HTTPException(status_code=400, detail=f"GRN already linked to bill {grn.get('linked_bill_number')}")
        
        if bill.get("linked_grn_id"):
            raise HTTPException(status_code=400, detail=f"Bill already linked to GRN {bill.get('linked_grn_number')}")
        
        # Link them
        now = datetime.now(timezone.utc).isoformat()
        
        await db.grn.update_one(
            {"id": grn_id},
            {
                "$set": {
                    "linked_bill_id": bill_id,
                    "linked_bill_number": bill["bill_number"],
                    "bill_matched_at": now,
                    "updated_at": now
                }
            }
        )
        
        await db.purchase_bills.update_one(
            {"id": bill_id},
            {
                "$set": {
                    "linked_grn_id": grn_id,
                    "linked_grn_number": grn["grn_number"],
                    "grn_matched_at": now,
                    "updated_at": now
                }
            }
        )
        
        return {
            "status": "success",
            "message": f"GRN {grn['grn_number']} linked to Purchase Bill {bill['bill_number']}",
            "grn_number": grn["grn_number"],
            "bill_number": bill["bill_number"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/grn-matching/unlink/{bill_id}")
async def unlink_grn_from_bill(
    bill_id: str,
    db = Depends(get_db)
):
    """Unlink a GRN from a Purchase Bill"""
    try:
        bill = await db.purchase_bills.find_one({"id": bill_id})
        if not bill:
            raise HTTPException(status_code=404, detail="Purchase Bill not found")
        
        grn_id = bill.get("linked_grn_id")
        if not grn_id:
            raise HTTPException(status_code=400, detail="Bill is not linked to any GRN")
        
        now = datetime.now(timezone.utc).isoformat()
        
        # Unlink from GRN
        await db.grn.update_one(
            {"id": grn_id},
            {
                "$unset": {
                    "linked_bill_id": "",
                    "linked_bill_number": "",
                    "bill_matched_at": ""
                },
                "$set": {"updated_at": now}
            }
        )
        
        # Unlink from Bill
        await db.purchase_bills.update_one(
            {"id": bill_id},
            {
                "$unset": {
                    "linked_grn_id": "",
                    "linked_grn_number": "",
                    "grn_matched_at": ""
                },
                "$set": {"updated_at": now}
            }
        )
        
        return {
            "status": "success",
            "message": "GRN unlinked from Purchase Bill"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/grn-matching/suggest/{bill_id}")
async def suggest_grn_for_bill(
    bill_id: str,
    db = Depends(get_db)
):
    """Suggest potential GRN matches for a Purchase Bill based on vendor and amounts"""
    try:
        bill = await db.purchase_bills.find_one({"id": bill_id}, {"_id": 0})
        if not bill:
            raise HTTPException(status_code=404, detail="Purchase Bill not found")
        
        vendor_name = bill.get("vendor", {}).get("name", "")
        bill_total = bill.get("grand_total", 0)
        bill_date = bill.get("bill_date")
        
        # Find unmatched GRNs from similar vendor or with similar amounts
        query = {
            "linked_bill_id": {"$exists": False},
            "$or": [
                {"vendor_name": {"$regex": vendor_name[:10], "$options": "i"}} if vendor_name else {},
                {"total_value": {"$gte": bill_total * 0.9, "$lte": bill_total * 1.1}}  # Within 10% of amount
            ]
        }
        
        suggestions = await db.grn.find(
            query, {"_id": 0}
        ).sort("created_at", -1).limit(10).to_list(None)
        
        # Score each suggestion
        scored_suggestions = []
        for grn in suggestions:
            score = 0
            reasons = []
            
            # Vendor name match
            if vendor_name and grn.get("vendor_name", "").lower().startswith(vendor_name[:5].lower()):
                score += 40
                reasons.append("Vendor name match")
            
            # Amount match (within 5%)
            grn_total = grn.get("total_value", 0)
            if grn_total and abs(grn_total - bill_total) / max(bill_total, 1) < 0.05:
                score += 30
                reasons.append("Amount matches")
            elif grn_total and abs(grn_total - bill_total) / max(bill_total, 1) < 0.1:
                score += 15
                reasons.append("Amount similar")
            
            # Date proximity (within 7 days)
            if bill_date and grn.get("created_at"):
                try:
                    grn_date = datetime.fromisoformat(grn["created_at"].replace("Z", "+00:00"))
                    bill_dt = datetime.strptime(bill_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    days_diff = abs((grn_date - bill_dt).days)
                    if days_diff <= 7:
                        score += 30
                        reasons.append(f"Date within {days_diff} days")
                    elif days_diff <= 14:
                        score += 15
                        reasons.append(f"Date within {days_diff} days")
                except Exception:
                    pass
            
            scored_suggestions.append({
                **grn,
                "match_score": score,
                "match_reasons": reasons
            })
        
        # Sort by score
        scored_suggestions.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "status": "success",
            "bill": {
                "id": bill["id"],
                "bill_number": bill["bill_number"],
                "vendor_name": vendor_name,
                "grand_total": bill_total
            },
            "suggestions": scored_suggestions[:5]  # Top 5 suggestions
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{bill_id}")
async def update_purchase_bill(bill_id: str, bill_data: PurchaseBillCreate, db = Depends(get_db)):
    """Update an existing purchase bill"""
    try:
        existing = await db.purchase_bills.find_one({"id": bill_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Purchase bill not found")
        
        # Recalculate totals
        items = []
        subtotal = 0
        total_tax = 0
        
        for item in bill_data.items:
            item_subtotal = item.quantity * item.rate
            discount_amt = item_subtotal * (item.discount_percent / 100)
            taxable = item_subtotal - discount_amt
            tax_amt = taxable * (item.tax_rate / 100)
            item_total = taxable + tax_amt
            
            items.append({
                "product_name": item.product_name,
                "hsn_code": item.hsn_code,
                "quantity": item.quantity,
                "rate": item.rate,
                "discount_percent": item.discount_percent,
                "tax_rate": item.tax_rate,
                "taxable_amount": round(taxable, 2),
                "tax_amount": round(tax_amt, 2),
                "total": round(item_total, 2)
            })
            subtotal += taxable
            total_tax += tax_amt
        
        update_data = {
            "bill_number": bill_data.bill_number,
            "bill_date": bill_data.bill_date,
            "po_number": bill_data.po_number,
            "vendor": bill_data.vendor.dict(),
            "items": items,
            "subtotal": round(subtotal, 2),
            **compute_gst_split(bill_data.vendor.gst_number, total_tax),
            "total_tax": round(total_tax, 2),
            "other_charges": bill_data.other_charges,
            "round_off": bill_data.round_off,
            "grand_total": round(subtotal + total_tax + bill_data.other_charges + bill_data.round_off, 2),
            "payment_mode": bill_data.payment_mode,
            "payment_status": bill_data.payment_status,
            "due_date": bill_data.due_date,
            "notes": bill_data.notes,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.purchase_bills.update_one({"id": bill_id}, {"$set": update_data})
        
        return {"status": "success", "message": "Purchase bill updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{bill_id}")
async def delete_purchase_bill(bill_id: str, db = Depends(get_db)):
    """Delete a purchase bill"""
    try:
        result = await db.purchase_bills.delete_one({"id": bill_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Purchase bill not found")
        
        return {"status": "success", "message": "Purchase bill deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear/tally-imported")
async def clear_tally_imported_bills(db = Depends(get_db)):
    """Clear all purchase bills imported from Tally"""
    try:
        result = await db.purchase_bills.delete_many({"source": "tally_import"})
        return {
            "status": "success",
            "message": f"Deleted {result.deleted_count} Tally-imported purchase bills",
            "deleted_count": result.deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear/all")
async def clear_all_purchase_bills(confirm: bool = False, db = Depends(get_db)):
    """Clear ALL purchase bills (use with caution!)"""
    try:
        if not confirm:
            raise HTTPException(status_code=400, detail="Please confirm deletion by adding ?confirm=true")
        
        result = await db.purchase_bills.delete_many({})
        return {
            "status": "success",
            "message": f"Deleted {result.deleted_count} purchase bills",
            "deleted_count": result.deleted_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{bill_id}/payment-status")
async def update_payment_status(bill_id: str, status: str, db = Depends(get_db)):
    """Update payment status of a purchase bill"""
    try:
        valid_statuses = ["pending", "partial", "paid"]
        if status.lower() not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Use: {valid_statuses}")
        
        result = await db.purchase_bills.update_one(
            {"id": bill_id},
            {"$set": {"payment_status": status.lower(), "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Purchase bill not found")
        
        return {"status": "success", "message": f"Payment status updated to {status}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ MSME COMPLIANCE & OVERDUE TRACKING ============

@router.get("/compliance/msme-pending")
async def get_msme_pending_payments(db = Depends(get_db)):
    """
    Get all pending payments to MSME vendors with compliance status
    MSMED Act requires payment within 45 days
    """
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # Find all unpaid/partial bills from MSME vendors
        msme_bills = await db.purchase_bills.find({
            "$or": [
                {"is_msme_vendor": True},
                {"vendor.is_msme": True},
                {"vendor.msme_udyam_number": {"$exists": True, "$nin": ["", None]}}
            ],
            "payment_status": {"$in": ["pending", "partial"]}
        }, {"_id": 0}).sort("due_date", 1).to_list(None)
        
        critical = []  # Overdue
        warning = []   # Due in 7 days
        upcoming = []  # Due in 8-45 days
        
        for bill in msme_bills:
            due_date = bill.get("due_date")
            if not due_date:
                # Calculate from bill_date if not set
                bill_date = datetime.strptime(bill.get("bill_date", today), "%Y-%m-%d")
                due_date = (bill_date + timedelta(days=45)).strftime("%Y-%m-%d")
            
            days_remaining = (datetime.strptime(due_date, "%Y-%m-%d") - datetime.strptime(today, "%Y-%m-%d")).days
            
            bill_summary = {
                "bill_id": bill.get("id"),
                "bill_number": bill.get("bill_number"),
                "vendor_name": bill.get("vendor", {}).get("name"),
                "msme_udyam_number": bill.get("vendor", {}).get("msme_udyam_number"),
                "grand_total": bill.get("grand_total", 0),
                "bill_date": bill.get("bill_date"),
                "due_date": due_date,
                "days_remaining": days_remaining,
                "payment_status": bill.get("payment_status")
            }
            
            if days_remaining < 0:
                bill_summary["status"] = "OVERDUE"
                bill_summary["days_overdue"] = abs(days_remaining)
                bill_summary["interest_applicable"] = True  # As per MSMED Act
                critical.append(bill_summary)
            elif days_remaining <= 7:
                bill_summary["status"] = "DUE_SOON"
                warning.append(bill_summary)
            else:
                bill_summary["status"] = "UPCOMING"
                upcoming.append(bill_summary)
        
        total_critical = sum(b["grand_total"] for b in critical)
        total_warning = sum(b["grand_total"] for b in warning)
        total_upcoming = sum(b["grand_total"] for b in upcoming)
        
        return {
            "status": "success",
            "compliance_summary": {
                "critical_count": len(critical),
                "critical_amount": total_critical,
                "warning_count": len(warning),
                "warning_amount": total_warning,
                "upcoming_count": len(upcoming),
                "upcoming_amount": total_upcoming,
                "total_msme_pending": total_critical + total_warning + total_upcoming
            },
            "critical_overdue": critical,
            "warning_due_soon": warning,
            "upcoming": upcoming,
            "msmed_act_notice": "As per MSMED Act 2006, interest at 3x bank rate is applicable on delayed payments to MSME vendors"
        }
    except Exception as e:
        logger.error(f"Failed to get MSME compliance data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance/overdue-invoices")
async def get_overdue_purchase_invoices(db = Depends(get_db)):
    """
    Get all overdue purchase invoices (MSME and non-MSME)
    Returns invoices past their due date
    """
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # Find all overdue unpaid bills
        overdue_bills = await db.purchase_bills.find({
            "due_date": {"$lt": today, "$exists": True, "$nin": ["", None]},
            "payment_status": {"$in": ["pending", "partial"]}
        }, {"_id": 0}).sort("due_date", 1).to_list(None)
        
        overdue_summary = []
        total_overdue = 0
        msme_overdue = 0
        
        for bill in overdue_bills:
            days_overdue = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(bill.get("due_date"), "%Y-%m-%d")).days
            is_msme = bill.get("is_msme_vendor") or bill.get("vendor", {}).get("is_msme") or bool(bill.get("vendor", {}).get("msme_udyam_number"))
            
            overdue_summary.append({
                "bill_id": bill.get("id"),
                "bill_number": bill.get("bill_number"),
                "vendor_name": bill.get("vendor", {}).get("name"),
                "grand_total": bill.get("grand_total", 0),
                "due_date": bill.get("due_date"),
                "days_overdue": days_overdue,
                "is_msme": is_msme,
                "msme_udyam_number": bill.get("vendor", {}).get("msme_udyam_number"),
                "payment_status": bill.get("payment_status"),
                "priority": "CRITICAL" if is_msme else "HIGH"
            })
            
            total_overdue += bill.get("grand_total", 0)
            if is_msme:
                msme_overdue += bill.get("grand_total", 0)
        
        return {
            "status": "success",
            "summary": {
                "total_overdue_count": len(overdue_summary),
                "total_overdue_amount": total_overdue,
                "msme_overdue_count": sum(1 for b in overdue_summary if b["is_msme"]),
                "msme_overdue_amount": msme_overdue,
                "non_msme_overdue_amount": total_overdue - msme_overdue
            },
            "overdue_invoices": overdue_summary,
            "action_required": "Please clear MSME overdue payments immediately to avoid interest penalties under MSMED Act"
        }
    except Exception as e:
        logger.error(f"Failed to get overdue invoices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ AI INVOICE SCANNER ============

@router.post("/scan-invoice")
async def scan_invoice_with_ai(
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    """
    AI-powered invoice scanning
    Upload PDF or image of vendor invoice, AI extracts all details
    """
    try:
        # Read file content
        content = await file.read()
        filename = file.filename.lower()
        
        # Validate file type
        allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.webp']
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )
        
        # Save file temporarily for AI extraction
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(suffix=file_ext, prefix="purchase_invoice_", delete=False) as tmp_f:
            tmp_f.write(content)
            saved_path = tmp_f.name
        
        # Determine mime type
        mime_types = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(file_ext, 'application/octet-stream')

        # If it's a PDF, try extracting text directly first — far more
        # reliable than vision-parsing a dense invoice/tax table.
        pdf_text = None
        if file_ext == '.pdf':
            try:
                import pdfplumber
                with pdfplumber.open(saved_path) as _pdf:
                    _pages = [p.extract_text() or "" for p in _pdf.pages]
                _combined = "\n".join(_pages).strip()
                if len(_combined) >= 20:
                    pdf_text = _combined
            except Exception as _pdf_err:
                logger.warning(f"pdfplumber text extraction failed, will fall back to vision: {_pdf_err}")

        # Use Claude to extract invoice data
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType
            
            extraction_prompt = """You are an expert invoice data extractor. Analyze this purchase invoice/bill and extract ALL information in the following JSON format. Be precise with numbers and GST calculations.

Extract and return ONLY a valid JSON object with this structure:
{
    "bill_number": "invoice/bill number from the document",
    "bill_date": "YYYY-MM-DD format",
    "po_number": "PO reference if mentioned, else empty string",
    "vendor": {
        "name": "vendor/supplier company name",
        "phone": "phone number if visible",
        "email": "email if visible",
        "gst_number": "GSTIN number (15 characters)",
        "address": "full address",
        "city": "city name",
        "state": "state name",
        "pincode": "PIN code"
    },
    "items": [
        {
            "product_name": "product/item description",
            "hsn_code": "HSN/SAC code",
            "quantity": number,
            "rate": unit_price_number,
            "discount_percent": discount_percentage_number,
            "tax_rate": GST_rate_number
        }
    ],
    "subtotal": taxable_amount_number,
    "cgst": cgst_amount_number,
    "sgst": sgst_amount_number,
    "igst": igst_amount_number,
    "other_charges": shipping_or_other_charges_number,
    "round_off": round_off_amount_number,
    "grand_total": final_total_number,
    "payment_terms": "payment terms if mentioned",
    "due_date": "YYYY-MM-DD if mentioned, else null"
}

Important:
- The "vendor" is the SUPPLIER/seller party (labeled "Supplier", "Bill from", "Seller" etc. on the invoice) — this is NEVER Aditya Retail (the buyer), and NEVER the "Consignee"/"Ship to"/"Bill to" party. Extract the supplier's own name, GSTIN, and address into the vendor object.
- All number fields should be numbers, not strings
- If a field is not visible/found, use empty string for text fields and 0 for number fields
- Extract ALL line items from the invoice
- GST numbers in India are 15 characters (e.g., 29AAECB6071D1ZS)
- Parse dates carefully and convert to YYYY-MM-DD format
- Return ONLY the JSON object, no other text"""

            llm_key = os.environ.get('EMERGENT_LLM_KEY', '') or os.environ.get('LLM_KEY', '')
            
            if not llm_key:
                raise ValueError("No LLM key configured")
            
            session_id = f"invoice_scan_{file_id}"
            llm = LlmChat(
                api_key=llm_key,
                session_id=session_id,
                system_message="You are an expert invoice data extractor. Extract data from invoices accurately. Always identify the SUPPLIER/vendor (the party billing/selling) — never the buyer — as the 'vendor' in your output."
            ).with_model("anthropic", "claude-sonnet-4-6")

            if pdf_text:
                # Text-only path: reliable for text-based invoice PDFs
                full_prompt = extraction_prompt + "\n\nINVOICE TEXT:\n---\n" + pdf_text + "\n---"
                user_msg = UserMessage(text=full_prompt)
            else:
                # Vision path: scanned PDFs or image uploads
                file_content = FileContentWithMimeType(
                    file_path=saved_path,
                    mime_type=mime_type
                )
                user_msg = UserMessage(
                    text=extraction_prompt,
                    file_contents=[file_content]
                )

            # Send message (await the async call)
            response = await llm.send_message(user_message=user_msg)
            
            # Parse the response
            import json
            import re
            
            response_text = response
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                extracted_data = json.loads(json_match.group())
            else:
                raise ValueError("Could not extract JSON from AI response")
            
            # Return extracted data with file URL
            extracted_data['invoice_file_url'] = f"/api/purchase-bills/invoice-file/{file_id}{file_ext}"
            extracted_data['extraction_status'] = 'success'
            
            return {
                "status": "success",
                "message": "Invoice scanned successfully",
                "extracted_data": extracted_data
            }
            
        except ImportError:
            logger.error("emergentintegrations not installed")
            raise HTTPException(
                status_code=500, 
                detail="AI service not available. Please configure LLM integration."
            )
        except Exception as ai_error:
            logger.error(f"AI extraction failed: {ai_error}")
            # Return partial success with file saved
            return {
                "status": "partial",
                "message": "File uploaded but AI extraction failed. Please enter details manually.",
                "invoice_file_url": f"/api/purchase-bills/invoice-file/{file_id}{file_ext}",
                "error": str(ai_error)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Invoice scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoice-file/{filename}")
async def get_invoice_file(filename: str):
    """Serve uploaded invoice files"""
    from fastapi.responses import FileResponse
    
    file_path = f"{INVOICE_UPLOAD_DIR}/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)


# ============ DASHBOARD STATS ============

@router.get("/stats/summary")
async def get_purchase_bill_stats(db = Depends(get_db)):
    """Get purchase bill statistics for dashboard"""
    try:
        # Total bills
        total_bills = await db.purchase_bills.count_documents({})
        
        # By payment status
        pending_bills = await db.purchase_bills.count_documents({"payment_status": "pending"})
        paid_bills = await db.purchase_bills.count_documents({"payment_status": "paid"})
        
        # Total amounts
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_amount": {"$sum": "$grand_total"},
                    "total_tax": {"$sum": "$total_tax"},
                    "pending_amount": {
                        "$sum": {
                            "$cond": [{"$eq": ["$payment_status", "pending"]}, "$grand_total", 0]
                        }
                    }
                }
            }
        ]
        
        result = await db.purchase_bills.aggregate(pipeline).to_list(length=1)
        amounts = result[0] if result else {"total_amount": 0, "total_tax": 0, "pending_amount": 0}
        
        return {
            "status": "success",
            "stats": {
                "total_bills": total_bills,
                "pending_bills": pending_bills,
                "paid_bills": paid_bills,
                "total_amount": amounts.get("total_amount", 0),
                "total_tax": amounts.get("total_tax", 0),
                "pending_amount": amounts.get("pending_amount", 0)
            }
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ FILE PREVIEW/ANALYSIS ============

@router.post("/preview-columns")
async def preview_import_columns(
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    """
    Preview the columns in an import file and show how they will be mapped.
    Use this to debug import issues before actually importing.
    """
    try:
        import pandas as pd
        import io
        
        content = await file.read()
        filename = file.filename.lower()
        
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content), nrows=5)  # Only read first 5 rows
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(content), nrows=5)
        else:
            raise HTTPException(status_code=400, detail="Please upload CSV or Excel file")
        
        # Get raw columns before cleaning
        raw_columns = list(df.columns)
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        cleaned_columns = list(df.columns)
        
        # Column mapping
        column_mapping = {
            'bill_number': ['voucher_no', 'voucher_number', 'bill_no', 'invoice_no', 'invoice_number', 'bill_number', 'ref_no', 'document_no'],
            'bill_date': ['date', 'voucher_date', 'bill_date', 'invoice_date'],
            'po_number': ['po_number', 'po_no', 'purchase_order', 'order_no', 'order_number'],
            'vendor_name': ['party_name', 'party', 'vendor_name', 'supplier', 'supplier_name', 'ledger_name', 'vendor', 'from_party', 'party_ledger'],
            'vendor_gst': ['vendor_gst', 'party_gst', 'gst_no', 'gstin', 'gst_number', 'supplier_gst', 'party_gstin'],
            'product_name': ['product_name', 'item_name', 'particular', 'particulars', 'description', 'item', 'stock_item', 'goods'],
            'quantity': ['quantity', 'qty', 'units', 'billed_qty'],
            'rate': ['rate', 'unit_rate', 'price', 'unit_price', 'mrp', 'selling_price', 'purchase_price'],
            'tax_rate': ['tax_rate', 'gst_rate', 'gst_%', 'tax_%', 'gst', 'tax_percent'],
            'total': ['total', 'grand_total', 'bill_amount', 'invoice_amount', 'amount', 'net_amount'],
        }
        
        # Detect mappings
        detected_mappings = {}
        for field, possible_cols in column_mapping.items():
            for col in possible_cols:
                matching = [c for c in cleaned_columns if c.lower().strip() == col.lower()]
                if matching:
                    sample_val = "N/A"
                    if len(df) > 0:
                        val = df[matching[0]].iloc[0]
                        if pd.notna(val):
                            sample_val = str(val)
                    detected_mappings[field] = {
                        "mapped_to": matching[0],
                        "sample_value": sample_val
                    }
                    break
            if field not in detected_mappings:
                detected_mappings[field] = {"mapped_to": None, "sample_value": "NOT FOUND - Column missing"}
        
        # Get sample data (convert NaN to None for JSON compatibility)
        df_clean = df.head(3).fillna('')
        sample_rows = df_clean.to_dict('records')
        
        # Re-read file for total row count
        await file.seek(0)
        content = await file.read()
        if filename.endswith('.csv'):
            total_rows = len(pd.read_csv(io.BytesIO(content)))
        else:
            total_rows = len(pd.read_excel(io.BytesIO(content)))
        
        return {
            "status": "success",
            "file_info": {
                "filename": file.filename,
                "total_rows": total_rows,
            },
            "raw_columns": raw_columns,
            "cleaned_columns": cleaned_columns,
            "detected_mappings": detected_mappings,
            "sample_rows": sample_rows,
            "recommendations": [
                f"Missing column: {field}" for field, info in detected_mappings.items() 
                if info["mapped_to"] is None and field in ['vendor_name', 'bill_number', 'rate']
            ]
        }
        
    except Exception as e:
        logger.error(f"Preview failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ BULK IMPORT FROM TALLY ============

@router.post("/import-tally")
async def import_purchase_bills_from_tally(
    file: UploadFile = File(...),
    update_existing: bool = Form(default=False),
    clear_before_import: bool = Form(default=False),
    db = Depends(get_db)
):
    """
    Import purchase bills from Tally CSV/Excel export
    Flexible column mapping to handle various Tally export formats
    
    Parameters:
    - update_existing: Update bills if they already exist
    - clear_before_import: Clear all existing bills before importing (use with caution!)
    """
    try:
        import pandas as pd
        import io
        
        # Clear existing data if requested
        if clear_before_import:
            delete_result = await db.purchase_bills.delete_many({"source": "tally_import"})
            logger.info(f"Cleared {delete_result.deleted_count} existing tally-imported bills")
        
        content = await file.read()
        filename = file.filename.lower()
        
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Please upload CSV or Excel file")
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        logger.info(f"Import columns found: {list(df.columns)}")
        
        # Flexible column mapping for various Tally export formats
        # NOTE: Order matters for disambiguation - more specific names first
        column_mapping = {
            # Bill number variations
            'bill_number': ['voucher_no', 'voucher_number', 'bill_no', 'invoice_no', 'invoice_number', 'bill_number', 'ref_no', 'document_no'],
            # Date variations
            'bill_date': ['date', 'voucher_date', 'bill_date', 'invoice_date'],
            # PO reference - removed 'reference' as it's too generic and conflicts with party_name in some exports
            'po_number': ['po_number', 'po_no', 'purchase_order', 'order_no', 'order_number'],
            # Vendor variations - PRIORITY: Check party_name and party first as these are standard Tally names
            'vendor_name': ['party_name', 'party', 'vendor_name', 'supplier', 'supplier_name', 'ledger_name', 'vendor', 'from_party', 'party_ledger'],
            'vendor_gst': ['vendor_gst', 'party_gst', 'gst_no', 'gstin', 'gst_number', 'supplier_gst', 'party_gstin'],
            'vendor_address': ['vendor_address', 'party_address', 'address', 'supplier_address'],
            'vendor_city': ['vendor_city', 'party_city', 'city'],
            'vendor_state': ['vendor_state', 'party_state', 'state', 'place_of_supply'],
            'vendor_pincode': ['vendor_pincode', 'party_pincode', 'pincode', 'pin'],
            'vendor_phone': ['vendor_phone', 'party_phone', 'phone', 'mobile', 'contact'],
            'vendor_email': ['vendor_email', 'party_email', 'email'],
            # Item details
            'product_name': ['product_name', 'item_name', 'particular', 'particulars', 'description', 'item', 'stock_item', 'goods'],
            'hsn_code': ['hsn_code', 'hsn', 'hsn/sac', 'sac_code', 'hsn_sac'],
            'quantity': ['quantity', 'qty', 'units', 'billed_qty'],
            'rate': ['rate', 'unit_rate', 'price', 'unit_price', 'mrp', 'selling_price', 'purchase_price'],
            'discount_percent': ['discount_percent', 'discount', 'disc_%', 'discount_%', 'disc_per'],
            'tax_rate': ['tax_rate', 'gst_rate', 'gst_%', 'tax_%', 'gst', 'tax_percent'],
            # Amounts
            'taxable_amount': ['taxable_amount', 'taxable_value', 'assessable_value', 'basic_amount', 'taxable'],
            'cgst': ['cgst', 'cgst_amount', 'central_tax'],
            'sgst': ['sgst', 'sgst_amount', 'state_tax'],
            'igst': ['igst', 'igst_amount', 'integrated_tax'],
            'total': ['total', 'grand_total', 'bill_amount', 'invoice_amount', 'amount', 'net_amount'],
            # Payment
            'payment_mode': ['payment_mode', 'payment_method', 'mode_of_payment'],
            'payment_status': ['payment_status', 'status'],
            'notes': ['notes', 'narration', 'remarks']
        }
        
        # Log detected column mappings for debugging
        detected_mappings = {}
        for field, possible_cols in column_mapping.items():
            for col in possible_cols:
                # Case-insensitive matching
                matching_cols = [c for c in df.columns if c.lower().strip() == col.lower()]
                if matching_cols:
                    detected_mappings[field] = matching_cols[0]
                    break
                elif col in df.columns:
                    detected_mappings[field] = col
                    break
        logger.info(f"Detected column mappings: {detected_mappings}")
        
        def get_column_value(row, field_name):
            """Get value from row using flexible column mapping (case-insensitive)"""
            possible_columns = column_mapping.get(field_name, [field_name])
            for col in possible_columns:
                # Try exact match first
                if col in df.columns:
                    val = row.get(col)
                    if pd.notna(val):
                        return val
                # Try case-insensitive match
                matching_cols = [c for c in df.columns if c.lower().strip() == col.lower()]
                for match_col in matching_cols:
                    val = row.get(match_col)
                    if pd.notna(val):
                        return val
            return None
        
        imported = 0
        skipped = 0
        errors = []
        
        # Group by bill number if possible (case-insensitive)
        bill_col = None
        for col in column_mapping['bill_number']:
            if col in df.columns:
                bill_col = col
                break
            # Case-insensitive search
            matching = [c for c in df.columns if c.lower().strip() == col.lower()]
            if matching:
                bill_col = matching[0]
                break
        
        if bill_col:
            grouped = df.groupby(bill_col)
        else:
            # No bill number column, treat each row as separate bill
            grouped = [(f"BILL-{i+1}", df.iloc[[i]]) for i in range(len(df))]
        
        # Default seller state (our business state)
        seller_state = "KARNATAKA"
        
        for bill_num, group in grouped:
            try:
                first_row = group.iloc[0]
                bill_number = str(bill_num)
                
                # Check if bill exists
                existing = await db.purchase_bills.find_one({"bill_number": bill_number})
                if existing and not update_existing:
                    skipped += 1
                    continue
                
                # Get vendor state for GST calculation
                vendor_state = str(get_column_value(first_row, 'vendor_state') or get_column_value(first_row, 'state') or '').upper().strip()
                is_inter_state = vendor_state and vendor_state != seller_state.upper() and vendor_state not in ['', 'KA', 'KARNATAKA']
                
                # Build items with smart GST calculation
                items = []
                subtotal = 0
                total_tax = 0
                total_cgst = 0
                total_sgst = 0
                total_igst = 0
                
                for _, row in group.iterrows():
                    qty = int(get_column_value(row, 'quantity') or 1)
                    rate = float(get_column_value(row, 'rate') or 0)
                    discount_pct = float(get_column_value(row, 'discount_percent') or 0)
                    tax_rate = float(get_column_value(row, 'tax_rate') or 18)
                    
                    item_subtotal = qty * rate
                    discount_amt = item_subtotal * (discount_pct / 100)
                    taxable = item_subtotal - discount_amt
                    tax_amt = taxable * (tax_rate / 100)
                    item_total = taxable + tax_amt
                    
                    # Smart GST split based on vendor state
                    if is_inter_state:
                        item_cgst = 0
                        item_sgst = 0
                        item_igst = tax_amt
                    else:
                        item_cgst = tax_amt / 2
                        item_sgst = tax_amt / 2
                        item_igst = 0
                    
                    items.append({
                        "product_name": str(get_column_value(row, 'product_name') or 'Unknown Item'),
                        "hsn_code": str(get_column_value(row, 'hsn_code') or ''),
                        "quantity": qty,
                        "rate": rate,
                        "discount_percent": discount_pct,
                        "tax_rate": tax_rate,
                        "taxable_amount": round(taxable, 2),
                        "tax_amount": round(tax_amt, 2),
                        "cgst": round(item_cgst, 2),
                        "sgst": round(item_sgst, 2),
                        "igst": round(item_igst, 2),
                        "total": round(item_total, 2)
                    })
                    
                    subtotal += taxable
                    total_tax += tax_amt
                    total_cgst += item_cgst
                    total_sgst += item_sgst
                    total_igst += item_igst
                
                # Parse date
                bill_date = get_column_value(first_row, 'bill_date')
                if bill_date:
                    if hasattr(bill_date, 'isoformat'):
                        bill_date = bill_date.strftime('%Y-%m-%d')
                    elif isinstance(bill_date, str):
                        try:
                            from dateutil import parser
                            bill_date = parser.parse(bill_date).strftime('%Y-%m-%d')
                        except Exception:
                            bill_date = datetime.now().strftime('%Y-%m-%d')
                else:
                    bill_date = datetime.now().strftime('%Y-%m-%d')
                
                # Check if explicit GST columns exist in file
                file_cgst = float(get_column_value(first_row, 'cgst') or 0)
                file_sgst = float(get_column_value(first_row, 'sgst') or 0)
                file_igst = float(get_column_value(first_row, 'igst') or 0)
                
                # Use file values if provided, otherwise use calculated values
                if file_cgst > 0 or file_sgst > 0 or file_igst > 0:
                    cgst = file_cgst
                    sgst = file_sgst
                    igst = file_igst
                else:
                    cgst = round(total_cgst, 2)
                    sgst = round(total_sgst, 2)
                    igst = round(total_igst, 2)
                
                grand_total = float(get_column_value(first_row, 'total') or (subtotal + total_tax))
                
                bill_doc = {
                    "id": str(uuid.uuid4()),
                    "bill_number": bill_number,
                    "bill_date": bill_date,
                    "po_number": str(get_column_value(first_row, 'po_number') or ''),
                    "vendor": {
                        "name": str(get_column_value(first_row, 'vendor_name') or 'Unknown Vendor'),
                        "phone": str(get_column_value(first_row, 'vendor_phone') or ''),
                        "email": str(get_column_value(first_row, 'vendor_email') or ''),
                        "gst_number": str(get_column_value(first_row, 'vendor_gst') or ''),
                        "address": str(get_column_value(first_row, 'vendor_address') or ''),
                        "city": str(get_column_value(first_row, 'vendor_city') or ''),
                        "state": str(get_column_value(first_row, 'vendor_state') or ''),
                        "pincode": str(get_column_value(first_row, 'vendor_pincode') or '')
                    },
                    "items": items,
                    "subtotal": round(subtotal, 2),
                    "cgst": cgst,
                    "sgst": sgst,
                    "igst": igst,
                    "total_tax": round(total_tax, 2),
                    "other_charges": 0,
                    "round_off": 0,
                    "grand_total": round(grand_total, 2),
                    "payment_mode": str(get_column_value(first_row, 'payment_mode') or 'credit'),
                    "payment_status": str(get_column_value(first_row, 'payment_status') or 'pending').lower(),
                    "notes": str(get_column_value(first_row, 'notes') or ''),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "source": "tally_import"
                }
                
                if existing and update_existing:
                    await db.purchase_bills.update_one(
                        {"bill_number": bill_number},
                        {"$set": bill_doc}
                    )
                else:
                    await db.purchase_bills.insert_one(bill_doc)
                
                imported += 1
                
            except Exception as e:
                errors.append(f"Bill {bill_num}: {str(e)}")
        
        return {
            "status": "success",
            "message": f"Import completed. {imported} bills imported, {skipped} skipped.",
            "result": {
                "total_rows": len(df),
                "imported": imported,
                "skipped": skipped,
                "errors": errors[:10]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Import failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fix-vendor-names")
async def fix_vendor_names_from_po(db = Depends(get_db)):
    """
    Fix existing data where vendor name was incorrectly placed in po_number field.
    This moves the po_number value to vendor.name for bills where vendor.name is 'Unknown Vendor'.
    """
    try:
        # Find all bills with Unknown Vendor
        bills = await db.purchase_bills.find({
            "vendor.name": "Unknown Vendor",
            "po_number": {"$exists": True, "$nin": ["", None, "Unknown"]}
        }).to_list(None)
        
        fixed_count = 0
        for bill in bills:
            vendor_name = bill.get("po_number", "")
            if vendor_name and vendor_name != "Unknown":
                # Update vendor name from po_number, clear po_number
                await db.purchase_bills.update_one(
                    {"id": bill["id"]},
                    {
                        "$set": {
                            "vendor.name": vendor_name,
                            "po_number": "",  # Clear the incorrect PO number
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                fixed_count += 1
        
        return {
            "status": "success",
            "message": f"Fixed {fixed_count} bills - vendor names restored from po_number field",
            "fixed_count": fixed_count,
            "total_checked": len(bills)
        }
        
    except Exception as e:
        logger.error(f"Fix vendor names failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
