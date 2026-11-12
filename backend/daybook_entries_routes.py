"""
Unclassified Entries Manager with AI Classification
- View all unclassified entries from Day Book import
- AI-powered smart classification
- Manual reclassification
- Create new voucher types if needed
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from bson import ObjectId
import logging
import os

router = APIRouter(prefix="/daybook-entries", tags=["Day Book Entries Manager"])
logger = logging.getLogger(__name__)

def get_db():
    from pymongo import MongoClient
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'startup_template')
    client = MongoClient(mongo_url)
    return client[db_name]


# Voucher type definitions with their target collections
VOUCHER_TYPES = {
    "sales_invoice": {"collection": "orders", "display": "Sales Invoice"},
    "sales_order": {"collection": "orders", "display": "Sales Order"},
    "purchase_bill": {"collection": "purchase_bills", "display": "Purchase Bill"},
    "purchase_order": {"collection": "purchase_orders", "display": "Purchase Order"},
    "payment": {"collection": "payments", "display": "Payment"},
    "receipt": {"collection": "receipts", "display": "Receipt"},
    "expense": {"collection": "expenses", "display": "Expense"},
    "journal": {"collection": "journal_vouchers", "display": "Journal Voucher"},
    "bank_entry": {"collection": "bank_transactions", "display": "Bank Entry"},
    "credit_note": {"collection": "credit_notes", "display": "Credit Note"},
    "debit_note": {"collection": "debit_notes", "display": "Debit Note"},
    "contra": {"collection": "contra_entries", "display": "Contra Entry"},
}


@router.get("/summary")
async def get_import_summary():
    """Get summary of all Day Book imported entries by voucher type"""
    db = get_db()
    
    summary = {
        "total_imported": 0,
        "by_voucher_type": {},
        "unclassified_count": 0,
        "collections": {}
    }
    
    # Check each collection for daybook imports
    collections_to_check = [
        ("orders", "Sales/Orders"),
        ("purchase_bills", "Purchase Bills"),
        ("purchase_orders", "Purchase Orders"),
        ("payments", "Payments"),
        ("receipts", "Receipts"),
        ("expenses", "Expenses"),
        ("journal_vouchers", "Journal Vouchers"),
        ("bank_transactions", "Bank Transactions"),
        ("credit_notes", "Credit Notes"),
        ("debit_note", "Debit Notes"),
        ("contra_entries", "Contra Entries"),
        ("unclassified_entries", "Unclassified")
    ]
    
    for coll_name, display_name in collections_to_check:
        count = db[coll_name].count_documents({"source": "daybook_import"})
        if count > 0:
            summary["collections"][display_name] = count
            summary["total_imported"] += count
            if coll_name == "unclassified_entries":
                summary["unclassified_count"] = count
    
    return summary


@router.get("/unclassified")
async def get_unclassified_entries(skip: int = 0, limit: int = 50):
    """Get all unclassified entries with pagination"""
    db = get_db()
    
    total = db.unclassified_entries.count_documents({"source": "daybook_import"})
    
    entries = list(db.unclassified_entries.find(
        {"source": "daybook_import"},
        {"_id": 0}
    ).skip(skip).limit(limit).sort("row_number", 1))
    
    return {
        "total": total,
        "entries": entries,
        "skip": skip,
        "limit": limit
    }


@router.get("/by-collection/{collection_name}")
async def get_entries_by_collection(collection_name: str, skip: int = 0, limit: int = 50):
    """Get Day Book imported entries from a specific collection"""
    db = get_db()
    
    # Validate collection name
    valid_collections = ["orders", "purchase_bills", "payments", "receipts", 
                         "expenses", "journal_vouchers", "bank_transactions", 
                         "unclassified_entries", "credit_notes", "debit_notes", "contra_entries"]
    
    if collection_name not in valid_collections:
        raise HTTPException(status_code=400, detail=f"Invalid collection. Valid options: {valid_collections}")
    
    total = db[collection_name].count_documents({"source": "daybook_import"})
    
    entries = list(db[collection_name].find(
        {"source": "daybook_import"},
        {"_id": 0}
    ).skip(skip).limit(limit).sort("created_at", -1))
    
    return {
        "collection": collection_name,
        "total": total,
        "entries": entries,
        "skip": skip,
        "limit": limit
    }


@router.post("/ai-classify")
async def ai_classify_entries(classify_all: bool = True):
    """
    Use AI to smartly classify unclassified entries.
    """
    db = get_db()
    
    # Get entries to classify
    entries = list(db.unclassified_entries.find({"source": "daybook_import"}))
    
    if not entries:
        return {"message": "No entries to classify", "classified": 0}
    
    results = {
        "total_processed": len(entries),
        "classified": 0,
        "failed": 0,
        "by_type": {},
        "errors": []
    }
    
    for entry in entries:
        try:
            # AI Classification Logic
            classification = smart_classify_entry(entry)
            
            if classification["voucher_type"] != "unknown":
                # Move entry to the correct collection
                target_collection = VOUCHER_TYPES.get(classification["voucher_type"], {}).get("collection")
                
                if target_collection:
                    # Prepare document for target collection
                    new_doc = prepare_document_for_collection(entry, classification)
                    
                    # Insert into target collection
                    db[target_collection].insert_one(new_doc)
                    
                    # Remove from unclassified
                    db.unclassified_entries.delete_one({"_id": entry["_id"]})
                    
                    results["classified"] += 1
                    vtype = classification["voucher_type"]
                    results["by_type"][vtype] = results["by_type"].get(vtype, 0) + 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"No target collection for type: {classification['voucher_type']}")
            else:
                results["failed"] += 1
        except Exception as e:
            results["failed"] += 1
            if len(results["errors"]) < 10:
                results["errors"].append(str(e)[:100])
    
    return results


def smart_classify_entry(entry: Dict) -> Dict:
    """
    AI-powered smart classification based on entry data patterns.
    Analyzes raw_data, amounts, party info, and narration to determine voucher type.
    """
    raw_data = entry.get("raw_data", {})
    amounts = entry.get("amounts", {})
    party = entry.get("party", {})
    refs = entry.get("references", {})
    
    # Combine all text for analysis
    all_text = " ".join([
        str(v).upper() for v in raw_data.values() if v
    ] + [
        str(refs.get("narration", "")).upper(),
        str(party.get("name", "")).upper()
    ])
    
    confidence = 0.0
    voucher_type = "unknown"
    reason = ""
    
    # Pattern matching rules with priority
    
    # 1. Check for Sales patterns
    if any(kw in all_text for kw in ["SALES", "SOLD", "INVOICE", "TAX INVOICE", "CUSTOMER"]):
        if amounts.get("credit", 0) > 0 or "SALES" in all_text:
            voucher_type = "sales_invoice"
            confidence = 0.8
            reason = "Sales keywords detected with credit amount"
    
    # 2. Check for Purchase patterns
    elif any(kw in all_text for kw in ["PURCHASE", "BOUGHT", "VENDOR", "SUPPLIER", "BILL"]):
        if amounts.get("debit", 0) > 0:
            voucher_type = "purchase_bill"
            confidence = 0.8
            reason = "Purchase keywords detected with debit amount"
    
    # 3. Check for Payment patterns
    elif any(kw in all_text for kw in ["PAYMENT", "PAID", "NEFT", "RTGS", "CHEQUE", "UPI PAYMENT"]):
        if amounts.get("debit", 0) > 0:
            voucher_type = "payment"
            confidence = 0.85
            reason = "Payment keywords detected"
    
    # 4. Check for Receipt patterns
    elif any(kw in all_text for kw in ["RECEIPT", "RECEIVED", "COLLECTION", "RECD"]):
        if amounts.get("credit", 0) > 0:
            voucher_type = "receipt"
            confidence = 0.85
            reason = "Receipt keywords detected"
    
    # 5. Check for Expense patterns
    elif any(kw in all_text for kw in ["EXPENSE", "RENT", "SALARY", "ELECTRICITY", "TELEPHONE", 
                                        "MAINTENANCE", "OFFICE", "TRAVEL", "CONVEYANCE"]):
        voucher_type = "expense"
        confidence = 0.75
        reason = "Expense keywords detected"
    
    # 6. Check for Journal patterns
    elif any(kw in all_text for kw in ["JOURNAL", "JV", "ADJUSTMENT", "PROVISION", "DEPRECIATION"]):
        voucher_type = "journal"
        confidence = 0.7
        reason = "Journal entry keywords detected"
    
    # 7. Check for Bank Entry patterns
    elif any(kw in all_text for kw in ["BANK", "STATEMENT", "INTEREST", "BANK CHARGES"]):
        voucher_type = "bank_entry"
        confidence = 0.7
        reason = "Bank transaction keywords detected"
    
    # 8. Check for Credit Note patterns
    elif any(kw in all_text for kw in ["CREDIT NOTE", "CN", "SALES RETURN", "RETURN INWARD"]):
        voucher_type = "credit_note"
        confidence = 0.8
        reason = "Credit note keywords detected"
    
    # 9. Check for Debit Note patterns
    elif any(kw in all_text for kw in ["DEBIT NOTE", "DN", "PURCHASE RETURN", "RETURN OUTWARD"]):
        voucher_type = "debit_note"
        confidence = 0.8
        reason = "Debit note keywords detected"
    
    # 10. Check for Contra patterns
    elif any(kw in all_text for kw in ["CONTRA", "CASH DEPOSIT", "CASH WITHDRAWAL", "BANK TO CASH"]):
        voucher_type = "contra"
        confidence = 0.85
        reason = "Contra entry keywords detected"
    
    # 11. Amount-based fallback classification
    elif amounts.get("credit", 0) > 0 and amounts.get("debit", 0) == 0:
        # Credit only - likely receipt or sales
        if "BANK" in all_text:
            voucher_type = "receipt"
            confidence = 0.5
            reason = "Credit amount with bank reference"
        else:
            voucher_type = "sales_invoice"
            confidence = 0.4
            reason = "Credit amount - possibly sales"
    
    elif amounts.get("debit", 0) > 0 and amounts.get("credit", 0) == 0:
        # Debit only - likely payment or purchase
        if "BANK" in all_text:
            voucher_type = "payment"
            confidence = 0.5
            reason = "Debit amount with bank reference"
        else:
            voucher_type = "expense"
            confidence = 0.4
            reason = "Debit amount - possibly expense"
    
    return {
        "voucher_type": voucher_type,
        "confidence": confidence,
        "reason": reason,
        "target_collection": VOUCHER_TYPES.get(voucher_type, {}).get("collection")
    }


def prepare_document_for_collection(entry: Dict, classification: Dict) -> Dict:
    """Prepare entry document for insertion into target collection"""
    import uuid
    
    raw_data = entry.get("raw_data", {})
    amounts = entry.get("amounts", {})
    party = entry.get("party", {})
    refs = entry.get("references", {})
    date = entry.get("date", datetime.now().strftime("%Y-%m-%d"))
    
    base_doc = {
        "id": entry.get("id", str(uuid.uuid4())[:12]),
        "import_batch_id": entry.get("import_batch_id"),
        "source": "daybook_import",
        "source_file": entry.get("source_file"),
        "reclassified": True,
        "reclassified_at": datetime.now(timezone.utc).isoformat(),
        "ai_classification": classification,
        "date": date,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    vtype = classification["voucher_type"]
    
    if vtype == "sales_invoice":
        return {
            **base_doc,
            "order_id": f"AI-{entry.get('id', uuid.uuid4().hex[:8])}",
            "order_number": refs.get("doc_number") or base_doc["id"],
            "order_date": date,
            "customer_details": {
                "name": party.get("name", ""),
                "email": party.get("email", ""),
                "phone": party.get("phone", "")
            },
            "total_amount": amounts.get("credit") or amounts.get("total", 0),
            "status": "confirmed",
            "notes": refs.get("narration", "")
        }
    
    elif vtype == "purchase_bill":
        return {
            **base_doc,
            "bill_id": f"AI-PB-{entry.get('id', uuid.uuid4().hex[:8])}",
            "bill_number": refs.get("doc_number") or base_doc["id"],
            "bill_date": date,
            "vendor_name": party.get("name", ""),
            "total_amount": amounts.get("debit") or amounts.get("total", 0),
            "status": "pending",
            "notes": refs.get("narration", "")
        }
    
    elif vtype == "payment":
        return {
            **base_doc,
            "payment_id": refs.get("doc_number") or base_doc["id"],
            "payment_date": date,
            "paid_to": party.get("name", ""),
            "amount": amounts.get("debit") or amounts.get("total", 0),
            "payment_mode": "Bank Transfer",
            "narration": refs.get("narration", ""),
            "status": "completed"
        }
    
    elif vtype == "receipt":
        return {
            **base_doc,
            "receipt_id": refs.get("doc_number") or base_doc["id"],
            "receipt_date": date,
            "received_from": party.get("name", ""),
            "amount": amounts.get("credit") or amounts.get("total", 0),
            "receipt_mode": "Bank Transfer",
            "narration": refs.get("narration", ""),
            "status": "completed"
        }
    
    elif vtype == "expense":
        return {
            **base_doc,
            "expense_id": refs.get("doc_number") or base_doc["id"],
            "expense_date": date,
            "description": refs.get("narration") or party.get("name", ""),
            "amount": amounts.get("debit") or amounts.get("total", 0),
            "category": "miscellaneous",
            "status": "approved"
        }
    
    elif vtype == "journal":
        return {
            **base_doc,
            "voucher_id": refs.get("doc_number") or base_doc["id"],
            "voucher_date": date,
            "narration": refs.get("narration", ""),
            "debit_amount": amounts.get("debit", 0),
            "credit_amount": amounts.get("credit", 0),
            "status": "posted"
        }
    
    elif vtype == "bank_entry":
        return {
            **base_doc,
            "transaction_id": refs.get("doc_number") or base_doc["id"],
            "transaction_date": date,
            "description": refs.get("narration") or party.get("name", ""),
            "debit": amounts.get("debit", 0),
            "credit": amounts.get("credit", 0),
            "reconciled": False
        }
    
    elif vtype in ["credit_note", "debit_note"]:
        return {
            **base_doc,
            "note_id": refs.get("doc_number") or base_doc["id"],
            "note_date": date,
            "party_name": party.get("name", ""),
            "amount": amounts.get("credit") or amounts.get("debit") or amounts.get("total", 0),
            "reason": refs.get("narration", ""),
            "status": "approved"
        }
    
    elif vtype == "contra":
        return {
            **base_doc,
            "contra_id": refs.get("doc_number") or base_doc["id"],
            "contra_date": date,
            "debit_account": party.get("name", ""),
            "credit_account": "",
            "debit_amount": amounts.get("debit", 0),
            "credit_amount": amounts.get("credit", 0),
            "narration": refs.get("narration", ""),
            "status": "posted"
        }
    
    # Default
    return base_doc


# Reverse mapping from display names to collection names
DISPLAY_TO_COLLECTION = {
    'Sales/Orders': 'orders',
    'Purchase Bills': 'purchase_bills',
    'Payments': 'payments',
    'Receipts': 'receipts',
    'Expenses': 'expenses',
    'Journal Vouchers': 'journal_vouchers',
    'Bank Transactions': 'bank_transactions',
    'Credit Notes': 'credit_notes',
    'Debit Notes': 'debit_notes',
    'Contra Entries': 'contra_entries',
    'Unclassified': 'unclassified_entries'
}


@router.post("/reclassify")
async def reclassify_entry(data: dict):
    """
    Move an entry from one collection to another.
    Used when AI classification was wrong and user wants to manually correct it.
    """
    db = get_db()
    
    entry_id = data.get('entry_id')
    current_collection_display = data.get('current_collection')
    new_voucher_type = data.get('new_voucher_type')
    
    if not entry_id or not current_collection_display or not new_voucher_type:
        raise HTTPException(
            status_code=400, 
            detail="Missing required fields: entry_id, current_collection, new_voucher_type"
        )
    
    if new_voucher_type not in VOUCHER_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid voucher type. Valid options: {list(VOUCHER_TYPES.keys())}"
        )
    
    # Get current collection name
    current_collection = DISPLAY_TO_COLLECTION.get(current_collection_display)
    if not current_collection:
        # Try direct mapping
        current_collection = current_collection_display.lower().replace(' ', '_').replace('/', '_')
    
    # Find the entry in current collection
    entry = db[current_collection].find_one({"id": entry_id})
    if not entry:
        # Try finding by _id
        try:
            entry = db[current_collection].find_one({"_id": ObjectId(entry_id)})
        except Exception:
            pass
    
    if not entry:
        raise HTTPException(status_code=404, detail=f"Entry {entry_id} not found in {current_collection}")
    
    # Get target collection
    target_collection = VOUCHER_TYPES[new_voucher_type]["collection"]
    
    # Don't move if same collection
    if current_collection == target_collection:
        return {"status": "success", "message": "Entry is already in this collection"}
    
    # Prepare the document for the new collection
    entry_copy = {k: v for k, v in entry.items() if k != '_id'}
    entry_copy['reclassified'] = True
    entry_copy['reclassified_from'] = current_collection
    entry_copy['reclassified_to'] = target_collection
    entry_copy['reclassified_at'] = datetime.now(timezone.utc).isoformat()
    entry_copy['reclassified_voucher_type'] = new_voucher_type
    
    # Insert into new collection
    db[target_collection].insert_one(entry_copy)
    
    # Delete from old collection
    db[current_collection].delete_one({"_id": entry["_id"]})
    
    return {
        "status": "success",
        "message": f"Entry moved from {current_collection} to {target_collection}",
        "new_voucher_type": VOUCHER_TYPES[new_voucher_type]['display'],
        "moved_to": target_collection
    }


@router.post("/manual-classify/{entry_id}")
async def manual_classify_entry(entry_id: str, voucher_type: str):
    """Manually classify an unclassified entry to a specific voucher type"""
    db = get_db()
    
    if voucher_type not in VOUCHER_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid voucher type. Valid options: {list(VOUCHER_TYPES.keys())}"
        )
    
    # Find the entry
    entry = db.unclassified_entries.find_one({"id": entry_id})
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Prepare classification
    classification = {
        "voucher_type": voucher_type,
        "confidence": 1.0,
        "reason": "Manual classification",
        "target_collection": VOUCHER_TYPES[voucher_type]["collection"]
    }
    
    # Prepare and insert document
    target_collection = VOUCHER_TYPES[voucher_type]["collection"]
    new_doc = prepare_document_for_collection(entry, classification)
    
    db[target_collection].insert_one(new_doc)
    db.unclassified_entries.delete_one({"_id": entry["_id"]})
    
    return {
        "status": "success",
        "message": f"Entry classified as {VOUCHER_TYPES[voucher_type]['display']}",
        "moved_to": target_collection
    }


@router.get("/voucher-types")
async def get_available_voucher_types():
    """Get list of available voucher types for classification"""
    return {
        "voucher_types": [
            {"id": k, "display": v["display"], "collection": v["collection"]}
            for k, v in VOUCHER_TYPES.items()
        ]
    }
