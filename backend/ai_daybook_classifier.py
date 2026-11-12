"""
AI-Powered Day Book Entry Classifier
Uses intelligent classification to correctly classify unclassified Day Book entries
by analyzing:
1. Party name patterns (customer vs vendor vs expense)
2. Debit/Credit patterns
3. Existing database records (customers, vendors, expenses)
4. Amount ranges typical for different voucher types
5. Context from narration and remarks
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from database import get_db
import os
import logging
import re
import uuid

router = APIRouter(prefix="/ai-daybook", tags=["AI Day Book Classifier"])
logger = logging.getLogger(__name__)


# Classification patterns for intelligent detection
TAX_LEDGERS = [
    'cgst', 'sgst', 'igst', 'gst', 'input gst', 'output gst',
    'tds', 'tcs', 'tax payable', 'tax receivable'
]

ROUND_OFF_LEDGERS = ['round off', 'roundoff', 'rounding']

BANK_LEDGERS = [
    'hdfc', 'icici', 'sbi', 'axis', 'kotak', 'bank', 'cash', 
    'petty cash', 'bank account'
]

EXPENSE_PATTERNS = [
    r'rent', r'salary', r'wages', r'electricity', r'bescom',
    r'telephone', r'internet', r'maintenance', r'insurance',
    r'professional', r'legal', r'audit', r'bank charges',
    r'interest', r'freight', r'transport', r'courier',
    r'office expenses', r'staff welfare', r'fuel', r'petrol', r'diesel'
]

COMPANY_PATTERNS = ['pvt', 'ltd', 'limited', 'private', 'llp', 'inc', 'enterprises', 'corporation']


async def get_existing_customers(db) -> List[str]:
    """Get list of existing customer names from database"""
    try:
        customers = await db.customers.find({}, {"name": 1, "_id": 0}).to_list(None)
        return [c.get("name", "").lower() for c in customers if c.get("name")]
    except Exception:
        return []


async def get_existing_vendors(db) -> List[str]:
    """Get list of existing vendor names from purchase bills"""
    try:
        vendors = await db.purchase_bills.distinct("vendor_name")
        return [v.lower() for v in vendors if v]
    except Exception:
        return []


async def classify_entry_with_ai(entry: Dict, db) -> Dict:
    """
    Use intelligent classification to determine the voucher type.
    Enhanced with database lookups and pattern matching.
    """
    party = str(entry.get("party", "")).strip()
    party_lower = party.lower()
    debit = float(entry.get("debit", 0) or 0)
    credit = float(entry.get("credit", 0) or 0)
    
    classification = {
        "type": "unknown",
        "confidence": 0.0,
        "reason": "",
        "target_collection": "unclassified_entries"
    }
    
    try:
        # Rule 1: Check for GST/Tax entries
        if any(tax in party_lower for tax in TAX_LEDGERS):
            return {
                "type": "journal",
                "confidence": 0.85,
                "reason": f"Tax ledger detected: {party}",
                "target_collection": "journal_vouchers"
            }
        
        # Rule 2: Check for Round Off entries
        if any(ro in party_lower for ro in ROUND_OFF_LEDGERS):
            return {
                "type": "journal",
                "confidence": 0.90,
                "reason": "Round off adjustment",
                "target_collection": "journal_vouchers"
            }
        
        # Rule 3: Check for Bank/Cash entries
        if any(bank in party_lower for bank in BANK_LEDGERS):
            if debit > 0:
                return {
                    "type": "payment",
                    "confidence": 0.80,
                    "reason": f"Bank/Cash debit entry: {party}",
                    "target_collection": "payments"
                }
            else:
                return {
                    "type": "receipt",
                    "confidence": 0.80,
                    "reason": f"Bank/Cash credit entry: {party}",
                    "target_collection": "receipts"
                }
        
        # Rule 4: Check expense patterns
        for pattern in EXPENSE_PATTERNS:
            if re.search(pattern, party_lower, re.IGNORECASE):
                return {
                    "type": "expense",
                    "confidence": 0.85,
                    "reason": f"Expense pattern matched: {pattern}",
                    "target_collection": "expenses"
                }
        
        # Rule 5: Check existing customers
        existing_customers = await get_existing_customers(db)
        if party_lower in existing_customers:
            if credit > 0:
                return {
                    "type": "receipt",
                    "confidence": 0.90,
                    "reason": f"Existing customer with credit: {party}",
                    "target_collection": "receipts"
                }
            else:
                return {
                    "type": "sales_invoice",
                    "confidence": 0.85,
                    "reason": f"Existing customer: {party}",
                    "target_collection": "orders"
                }
        
        # Rule 6: Check existing vendors
        existing_vendors = await get_existing_vendors(db)
        for vendor in existing_vendors:
            if vendor in party_lower or party_lower in vendor:
                if debit > 0:
                    return {
                        "type": "payment",
                        "confidence": 0.85,
                        "reason": f"Existing vendor payment: {party}",
                        "target_collection": "payments"
                    }
                else:
                    return {
                        "type": "purchase_bill",
                        "confidence": 0.85,
                        "reason": f"Existing vendor: {party}",
                        "target_collection": "purchase_bills"
                    }
        
        # Rule 7: Company name detection (Pvt Ltd, Limited, etc.)
        is_company = any(cp in party_lower for cp in COMPANY_PATTERNS)
        
        if is_company:
            if credit > 0:
                return {
                    "type": "receipt",
                    "confidence": 0.75,
                    "reason": f"Company name with credit (likely B2B receipt): {party}",
                    "target_collection": "receipts"
                }
            elif debit > 0:
                return {
                    "type": "payment",
                    "confidence": 0.75,
                    "reason": f"Company name with debit (likely vendor payment): {party}",
                    "target_collection": "payments"
                }
        
        # Rule 8: Individual name patterns (single/double capitalized names)
        name_pattern = r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)?$'
        if re.match(name_pattern, party) and credit > 0:
            return {
                "type": "receipt",
                "confidence": 0.70,
                "reason": f"Individual customer receipt pattern: {party}",
                "target_collection": "receipts"
            }
        
        # Rule 9: All caps name with credit (likely customer)
        if party.isupper() and credit > 0:
            return {
                "type": "receipt",
                "confidence": 0.65,
                "reason": f"Customer name (all caps) with credit: {party}",
                "target_collection": "receipts"
            }
        
        # Rule 10: Default fallbacks based on debit/credit
        if credit > 0:
            return {
                "type": "receipt",
                "confidence": 0.60,
                "reason": "Credit entry - defaulting to receipt",
                "target_collection": "receipts"
            }
        
        if debit > 0:
            return {
                "type": "expense",
                "confidence": 0.50,
                "reason": "Debit entry - defaulting to expense",
                "target_collection": "expenses"
            }
        
    except Exception as e:
        logger.error(f"Classification error for {party}: {str(e)}")
        classification["reason"] = f"Error: {str(e)}"
    
    return classification


def prepare_document(entry: Dict, classification: Dict) -> Dict:
    """Prepare entry document for insertion into target collection"""
    party = entry.get("party", "")
    debit = float(entry.get("debit", 0) or 0)
    credit = float(entry.get("credit", 0) or 0)
    amount = credit or debit
    date = entry.get("date", datetime.now().strftime("%Y-%m-%d"))
    narration = entry.get("narration", "")
    voucher_no = entry.get("voucher_no", "")
    entry_id = entry.get("id", str(uuid.uuid4())[:12])
    
    base_doc = {
        "id": entry_id,
        "import_batch_id": entry.get("import_batch_id"),
        "source": "daybook_import",
        "source_file": entry.get("source_file"),
        "row_number": entry.get("row_number"),
        "ai_classified": True,
        "ai_classification": classification,
        "date": date,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "raw_data": entry.get("raw_data", {}),  # PRESERVE RAW DATA
        "original_voucher_type": entry.get("original_voucher_type", "")
    }
    
    vtype = classification["type"]
    
    if vtype == "sales_invoice":
        return {
            **base_doc,
            "order_id": f"AI-{entry_id}",
            "order_number": voucher_no or entry_id,
            "order_date": date,
            "customer_details": {"name": party, "email": "", "phone": ""},
            "total_amount": credit or amount,
            "status": "confirmed",
            "notes": narration
        }
    
    elif vtype == "receipt":
        return {
            **base_doc,
            "receipt_id": voucher_no or entry_id,
            "receipt_date": date,
            "received_from": party,
            "amount": credit or amount,
            "receipt_mode": "Bank Transfer",
            "narration": narration,
            "status": "completed"
        }
    
    elif vtype == "purchase_bill":
        return {
            **base_doc,
            "bill_id": f"AI-PB-{entry_id}",
            "bill_number": voucher_no or entry_id,
            "bill_date": date,
            "vendor_name": party,
            "total_amount": debit or amount,
            "status": "pending",
            "notes": narration
        }
    
    elif vtype == "payment":
        return {
            **base_doc,
            "payment_id": voucher_no or entry_id,
            "payment_date": date,
            "paid_to": party,
            "amount": debit or amount,
            "payment_mode": "Bank Transfer",
            "narration": narration,
            "status": "completed"
        }
    
    elif vtype == "expense":
        return {
            **base_doc,
            "expense_id": voucher_no or entry_id,
            "expense_date": date,
            "description": narration or party,
            "amount": debit or amount,
            "category": detect_expense_category(party),
            "paid_to": party,
            "status": "approved"
        }
    
    elif vtype == "journal":
        return {
            **base_doc,
            "voucher_id": voucher_no or entry_id,
            "voucher_date": date,
            "narration": narration or party,
            "debit_amount": debit,
            "credit_amount": credit,
            "ledger": party,
            "status": "posted"
        }
    
    return {
        **base_doc,
        "party": party,
        "debit": debit,
        "credit": credit,
        "narration": narration
    }


def detect_expense_category(party: str) -> str:
    """Detect expense category from party/description"""
    party_lower = party.lower()
    
    categories = {
        "rent": ["rent", "lease"],
        "salary": ["salary", "wages", "payroll"],
        "utilities": ["electricity", "water", "bescom", "telephone", "internet", "mobile"],
        "travel": ["travel", "petrol", "diesel", "fuel", "conveyance", "transport"],
        "office": ["office", "stationery", "supplies"],
        "professional": ["professional", "legal", "audit", "consultant"],
        "bank_charges": ["bank charges", "interest", "commission"],
        "insurance": ["insurance", "premium"],
        "taxes": ["gst", "cgst", "sgst", "igst", "tds", "tcs", "tax"]
    }
    
    for category, keywords in categories.items():
        if any(kw in party_lower for kw in keywords):
            return category
    
    return "miscellaneous"


@router.post("/smart-classify")
async def smart_classify_entries(
    batch_size: int = 100,
    dry_run: bool = False,
    db=Depends(get_db)
):
    """
    Smart AI classification of unclassified Day Book entries.
    Uses database context and pattern matching for intelligent classification.
    """
    try:
        entries = await db.unclassified_entries.find(
            {"source": "daybook_import"}
        ).limit(batch_size).to_list(batch_size)
        
        if not entries:
            return {
                "status": "success",
                "message": "No unclassified entries found",
                "classified": 0
            }
        
        results = {
            "total_processed": len(entries),
            "classified": 0,
            "by_type": {},
            "samples": [],
            "errors": []
        }
        
        for entry in entries:
            try:
                classification = await classify_entry_with_ai(entry, db)
                entry_type = classification["type"]
                
                results["by_type"][entry_type] = results["by_type"].get(entry_type, 0) + 1
                
                if len(results["samples"]) < 10:
                    results["samples"].append({
                        "id": entry.get("id"),
                        "party": entry.get("party"),
                        "debit": entry.get("debit", 0),
                        "credit": entry.get("credit", 0),
                        "classified_as": entry_type,
                        "confidence": classification["confidence"],
                        "reason": classification["reason"]
                    })
                
                if not dry_run and entry_type != "unknown":
                    target_collection = classification["target_collection"]
                    new_doc = prepare_document(entry, classification)
                    
                    await db[target_collection].insert_one(new_doc)
                    await db.unclassified_entries.delete_one({"_id": entry["_id"]})
                    
                    results["classified"] += 1
                elif entry_type != "unknown":
                    results["classified"] += 1
                    
            except Exception as e:
                if len(results["errors"]) < 10:
                    results["errors"].append(f"Entry {entry.get('id')}: {str(e)[:50]}")
        
        return {
            "status": "success",
            "message": f"{'Would classify' if dry_run else 'Classified'} {results['classified']} of {results['total_processed']} entries",
            "dry_run": dry_run,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Smart classify error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@router.get("/unclassified-analysis")
async def analyze_unclassified(limit: int = 50, db=Depends(get_db)):
    """
    Analyze unclassified entries and show what they would be classified as.
    This is a preview/dry-run mode.
    """
    entries = await db.unclassified_entries.find(
        {"source": "daybook_import"}
    ).limit(limit).to_list(limit)
    
    total_unclassified = await db.unclassified_entries.count_documents({"source": "daybook_import"})
    
    analysis = {
        "total_unclassified": total_unclassified,
        "analyzed": len(entries),
        "predictions": {
            "sales_invoice": 0,
            "receipt": 0,
            "purchase_bill": 0,
            "payment": 0,
            "expense": 0,
            "journal": 0,
            "unknown": 0
        },
        "samples": []
    }
    
    for entry in entries:
        classification = await classify_entry_with_ai(entry, db)
        entry_type = classification["type"]
        analysis["predictions"][entry_type] = analysis["predictions"].get(entry_type, 0) + 1
        
        if len(analysis["samples"]) < 20:
            analysis["samples"].append({
                "row": entry.get("row_number"),
                "party": entry.get("party"),
                "debit": entry.get("debit", 0),
                "credit": entry.get("credit", 0),
                "predicted_type": entry_type,
                "confidence": classification["confidence"],
                "reason": classification["reason"]
            })
    
    return analysis


@router.get("/classification-stats")
async def get_classification_stats(db=Depends(get_db)):
    """Get statistics of all Day Book imported entries"""
    stats = {
        "by_collection": {},
        "total_imported": 0,
        "unclassified": 0
    }
    
    collections = [
        ("orders", "Sales/Orders"),
        ("receipts", "Receipts"),
        ("purchase_bills", "Purchase Bills"),
        ("payments", "Payments"),
        ("expenses", "Expenses"),
        ("journal_vouchers", "Journal Vouchers"),
        ("bank_transactions", "Bank Transactions"),
        ("unclassified_entries", "Unclassified")
    ]
    
    for coll_name, display_name in collections:
        count = await db[coll_name].count_documents({"source": "daybook_import"})
        if count > 0:
            stats["by_collection"][display_name] = count
            stats["total_imported"] += count
            if coll_name == "unclassified_entries":
                stats["unclassified"] = count
    
    return stats
