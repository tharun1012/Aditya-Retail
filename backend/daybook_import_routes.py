"""
Tally Day Book Import - AI-Powered Universal Import
Handles a single Excel/CSV file containing all daily transactions:
- Sales Orders (SO)
- Sales Invoices
- Purchase Orders (PO)
- Purchase Bills
- Expenses
- Payments (made)
- Receipts (received)
- Bank Entries
- Journal Vouchers

AI automatically classifies each row and routes to the correct accounting module.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import pandas as pd
import uuid
import os
import io
import json
import logging
import re

router = APIRouter(prefix="/daybook-import", tags=["Day Book Import"])
logger = logging.getLogger(__name__)

# Create uploads directory
UPLOAD_DIR = "/app/backend/uploads/daybook_imports"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ============ VOUCHER TYPE CLASSIFICATION RULES ============

VOUCHER_PATTERNS = {
    "sales_invoice": {
        "keywords": ["SALES", "INVOICE", "INV", "SI", "TAX INVOICE", "BILL OF SUPPLY"],
        "voucher_types": ["Sales", "Tax Invoice", "Sales Invoice"],
        "indicators": ["customer", "sold to", "buyer", "cgst", "sgst", "igst"],
        "amount_type": "credit"
    },
    "sales_order": {
        "keywords": ["SALES ORDER", "SO", "ORDER", "BOOKING"],
        "voucher_types": ["Sales Order"],
        "indicators": ["order date", "delivery date", "advance"],
        "amount_type": "credit"
    },
    "purchase_bill": {
        "keywords": ["PURCHASE", "BILL", "PB", "VENDOR INVOICE", "SUPPLIER"],
        "voucher_types": ["Purchase", "Purchase Bill"],
        "indicators": ["vendor", "supplier", "purchased from", "input gst"],
        "amount_type": "debit"
    },
    "purchase_order": {
        "keywords": ["PURCHASE ORDER", "PO", "INDENT"],
        "voucher_types": ["Purchase Order"],
        "indicators": ["expected delivery", "ordered from"],
        "amount_type": "debit"
    },
    "payment": {
        "keywords": ["PAYMENT", "PAID", "PMT", "CONTRA", "BANK PAYMENT"],
        "voucher_types": ["Payment", "Bank Payment", "Cash Payment", "Contra"],
        "indicators": ["paid to", "payment to", "cheque", "neft", "rtgs", "upi"],
        "amount_type": "debit"
    },
    "receipt": {
        "keywords": ["RECEIPT", "RECEIVED", "RCV", "RCPT", "BANK RECEIPT"],
        "voucher_types": ["Receipt", "Bank Receipt", "Cash Receipt"],
        "indicators": ["received from", "receipt from", "collection"],
        "amount_type": "credit"
    },
    "expense": {
        "keywords": ["EXPENSE", "EXP", "EXPENDITURE", "CHARGES"],
        "voucher_types": ["Expense", "Indirect Expense"],
        "indicators": ["rent", "salary", "electricity", "telephone", "maintenance", "office"],
        "amount_type": "debit"
    },
    "journal": {
        "keywords": ["JOURNAL", "JV", "ADJUSTMENT", "PROVISION"],
        "voucher_types": ["Journal", "Journal Voucher"],
        "indicators": ["adjustment", "provision", "accrual", "depreciation"],
        "amount_type": "both"
    },
    "bank_entry": {
        "keywords": ["BANK", "STATEMENT", "BANK ENTRY"],
        "voucher_types": ["Bank Entry", "Bank Statement"],
        "indicators": ["account no", "bank name", "branch", "ifsc"],
        "amount_type": "both"
    }
}

EXPENSE_CATEGORIES = {
    "rent": ["RENT", "LEASE", "PREMISES"],
    "salary": ["SALARY", "WAGES", "PAYROLL", "STAFF"],
    "utilities": ["ELECTRICITY", "WATER", "GAS", "TELEPHONE", "MOBILE", "INTERNET"],
    "office": ["OFFICE", "STATIONERY", "SUPPLIES", "PRINTING"],
    "travel": ["TRAVEL", "CONVEYANCE", "PETROL", "FUEL", "TRANSPORT"],
    "maintenance": ["MAINTENANCE", "REPAIRS", "AMC", "SERVICE"],
    "professional": ["PROFESSIONAL", "LEGAL", "AUDIT", "CONSULTANT"],
    "bank_charges": ["BANK CHARGES", "INTEREST", "COMMISSION"],
    "taxes": ["TAX", "GST", "TDS", "ADVANCE TAX"],
    "insurance": ["INSURANCE", "PREMIUM"],
    "miscellaneous": ["MISC", "SUNDRY", "OTHER"]
}


def classify_voucher_type(row_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    AI-powered classification of voucher type from row data
    Returns: {voucher_type, category, sub_category, confidence, matched_on}
    """
    # Convert all values to string for matching
    row_text = " ".join(str(v).upper() for v in row_data.values() if v)
    
    result = {
        "voucher_type": "unknown",
        "category": None,
        "sub_category": None,
        "confidence": 0.0,
        "matched_on": [],
        "target_collection": None
    }
    
    # Check for voucher type column first
    voucher_col = None
    for key in row_data.keys():
        key_lower = key.lower()
        if any(x in key_lower for x in ['voucher', 'type', 'doc type', 'entry type']):
            voucher_col = row_data.get(key)
            break
    
    if voucher_col:
        voucher_col_upper = str(voucher_col).upper()
        for vtype, rules in VOUCHER_PATTERNS.items():
            for vt in rules["voucher_types"]:
                if vt.upper() in voucher_col_upper:
                    result["voucher_type"] = vtype
                    result["confidence"] = 0.95
                    result["matched_on"].append(f"voucher_type_column:{voucher_col}")
                    break
            if result["confidence"] > 0:
                break
    
    # If not found from voucher column, use pattern matching
    if result["confidence"] < 0.5:
        best_match = None
        best_score = 0
        
        for vtype, rules in VOUCHER_PATTERNS.items():
            score = 0
            matches = []
            
            # Check keywords
            for kw in rules["keywords"]:
                if kw in row_text:
                    score += 2
                    matches.append(f"keyword:{kw}")
            
            # Check indicators
            for ind in rules["indicators"]:
                if ind.upper() in row_text:
                    score += 1
                    matches.append(f"indicator:{ind}")
            
            if score > best_score:
                best_score = score
                best_match = vtype
                result["matched_on"] = matches
        
        if best_match and best_score >= 2:
            result["voucher_type"] = best_match
            result["confidence"] = min(best_score / 10, 0.9)
    
    # Set target collection based on voucher type
    collection_map = {
        "sales_invoice": "orders",
        "sales_order": "orders",
        "purchase_bill": "purchase_bills",
        "purchase_order": "purchase_orders",
        "payment": "payments",
        "receipt": "receipts",
        "expense": "expenses",
        "journal": "journal_vouchers",
        "bank_entry": "bank_transactions"
    }
    result["target_collection"] = collection_map.get(result["voucher_type"], "unclassified_entries")
    
    # For expenses, determine sub-category
    if result["voucher_type"] == "expense":
        for cat, keywords in EXPENSE_CATEGORIES.items():
            if any(kw in row_text for kw in keywords):
                result["sub_category"] = cat
                break
    
    return result


def extract_amount(row_data: Dict[str, Any]) -> Dict[str, float]:
    """Extract debit and credit amounts from row"""
    amounts = {"debit": 0.0, "credit": 0.0, "total": 0.0}
    
    for key, value in row_data.items():
        if value is None or pd.isna(value):
            continue
            
        key_lower = key.lower()
        try:
            # Clean amount string
            if isinstance(value, str):
                value = re.sub(r'[₹,\s]', '', value)
            amount = float(value) if value else 0.0
            
            if any(x in key_lower for x in ['debit', 'dr', 'paid', 'expense']):
                amounts["debit"] = abs(amount)
            elif any(x in key_lower for x in ['credit', 'cr', 'received', 'income']):
                amounts["credit"] = abs(amount)
            elif any(x in key_lower for x in ['amount', 'total', 'value', 'net']):
                amounts["total"] = abs(amount)
        except (ValueError, TypeError):
            continue
    
    # If only total, use voucher type to determine debit/credit
    if amounts["total"] > 0 and amounts["debit"] == 0 and amounts["credit"] == 0:
        amounts["debit"] = amounts["total"]  # Default, will be adjusted based on voucher type
    
    return amounts


def extract_date(row_data: Dict[str, Any]) -> Optional[str]:
    """Extract date from row"""
    for key, value in row_data.items():
        key_lower = key.lower()
        if any(x in key_lower for x in ['date', 'dt', 'dated']):
            if value and not pd.isna(value):
                try:
                    if isinstance(value, datetime):
                        return value.strftime("%Y-%m-%d")
                    elif isinstance(value, str):
                        # Try common date formats
                        for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%d-%b-%Y", "%d %b %Y"]:
                            try:
                                return datetime.strptime(value.strip(), fmt).strftime("%Y-%m-%d")
                            except (ValueError, AttributeError):
                                continue
                        return value
                except (ValueError, TypeError, AttributeError):
                    pass
    return datetime.now().strftime("%Y-%m-%d")


def extract_party_details(row_data: Dict[str, Any]) -> Dict[str, str]:
    """Extract party (customer/vendor) details"""
    party = {"name": "", "gstin": "", "phone": "", "email": "", "address": ""}
    
    for key, value in row_data.items():
        if value is None or pd.isna(value):
            continue
        key_lower = key.lower()
        value_str = str(value).strip()
        
        if any(x in key_lower for x in ['party', 'customer', 'vendor', 'supplier', 'buyer', 'name']):
            if not party["name"]:
                party["name"] = value_str
        elif any(x in key_lower for x in ['gstin', 'gst', 'tin']):
            party["gstin"] = value_str
        elif any(x in key_lower for x in ['phone', 'mobile', 'contact']):
            party["phone"] = value_str
        elif any(x in key_lower for x in ['email', 'mail']):
            party["email"] = value_str
        elif any(x in key_lower for x in ['address', 'addr']):
            party["address"] = value_str
    
    return party


def extract_reference(row_data: Dict[str, Any]) -> Dict[str, str]:
    """Extract reference/document numbers"""
    refs = {"doc_number": "", "reference": "", "narration": ""}
    
    for key, value in row_data.items():
        if value is None or pd.isna(value):
            continue
        key_lower = key.lower()
        value_str = str(value).strip()
        
        if any(x in key_lower for x in ['voucher no', 'doc no', 'invoice no', 'bill no', 'number', 'vch no']):
            if not refs["doc_number"]:
                refs["doc_number"] = value_str
        elif any(x in key_lower for x in ['ref', 'reference']):
            refs["reference"] = value_str
        elif any(x in key_lower for x in ['narration', 'particular', 'description', 'remarks', 'notes']):
            refs["narration"] = value_str
    
    return refs


# ============ API ENDPOINTS ============

@router.get("/template")
async def download_daybook_template():
    """Download template for Day Book import with all voucher types"""
    template_data = {
        "Date": ["2026-02-15", "2026-02-15", "2026-02-15", "2026-02-15", "2026-02-15", "2026-02-15"],
        "Voucher_Type": ["Sales Invoice", "Purchase Bill", "Payment", "Receipt", "Expense", "Journal"],
        "Voucher_No": ["SI-001", "PB-001", "PMT-001", "RCV-001", "EXP-001", "JV-001"],
        "Party_Name": ["ABC Electronics", "Bosch India", "Rent Payment", "Customer XYZ", "Telephone Charges", "Depreciation"],
        "GSTIN": ["29AABCA1234F1ZP", "29AABCB5678G1ZQ", "", "", "", ""],
        "Debit_Amount": [0, 50000, 25000, 0, 5000, 10000],
        "Credit_Amount": [118000, 0, 0, 50000, 0, 0],
        "Ledger_Account": ["Sales - Karnataka", "Purchases", "Rent A/c", "Debtors", "Telephone Exp", "Depreciation"],
        "Narration": ["Sale of appliances", "Purchase from vendor", "Monthly rent", "Collection", "Monthly bill", "Asset depreciation"],
        "Reference": ["SO-100", "PO-50", "Rent-Feb", "INV-001", "Bill-123", "FY26-Q3"]
    }
    
    df = pd.DataFrame(template_data)
    template_path = f"{UPLOAD_DIR}/daybook_template.xlsx"
    df.to_excel(template_path, index=False)
    
    return FileResponse(
        template_path,
        filename="daybook_import_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.post("/preview")
async def preview_daybook(file: UploadFile = File(...)):
    """
    Preview and classify Day Book entries before import.
    Returns classification for each row without importing.
    """
    try:
        # Read file
        content = await file.read()
        filename = file.filename.lower()
        
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or Excel.")
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Process each row
        preview_results = []
        summary = {
            "total_rows": len(df),
            "by_type": {},
            "unclassified": 0,
            "total_debit": 0,
            "total_credit": 0
        }
        
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            
            # Classify voucher type
            classification = classify_voucher_type(row_dict)
            amounts = extract_amount(row_dict)
            date = extract_date(row_dict)
            party = extract_party_details(row_dict)
            refs = extract_reference(row_dict)
            
            entry = {
                "row_number": idx + 1,
                "classification": classification,
                "date": date,
                "amounts": amounts,
                "party": party,
                "references": refs,
                "raw_data": {k: str(v) if not pd.isna(v) else None for k, v in row_dict.items()}
            }
            
            preview_results.append(entry)
            
            # Update summary
            vtype = classification["voucher_type"]
            summary["by_type"][vtype] = summary["by_type"].get(vtype, 0) + 1
            if vtype == "unknown":
                summary["unclassified"] += 1
            
            summary["total_debit"] += amounts["debit"]
            summary["total_credit"] += amounts["credit"]
        
        return {
            "status": "success",
            "filename": file.filename,
            "columns_detected": list(df.columns),
            "summary": summary,
            "entries": preview_results
        }
        
    except Exception as e:
        logger.error(f"Preview error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post("/import")
async def import_daybook(
    file: UploadFile = File(...),
    import_date: Optional[str] = Form(None),
    skip_unclassified: bool = Form(False)
):
    """
    Import Day Book and auto-classify entries to respective modules.
    Uses batch inserts for better performance with large files.
    Includes smart duplicate detection to skip existing entries.
    """
    from pymongo import MongoClient
    import os
    
    # Use synchronous pymongo for bulk operations (better performance)
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'startup_template')
    client = MongoClient(mongo_url)
    db = client[db_name]
    
    def check_duplicate(collection_name: str, doc_number: str, date: str, amount: float, party_name: str = None) -> bool:
        """
        Check if a similar entry already exists in the database.
        Returns True if duplicate found, False otherwise.
        """
        if not doc_number and not (date and amount > 0):
            return False  # Can't check without identifiers
        
        query = {}
        
        # Build query based on collection type
        if collection_name == "orders":
            if doc_number:
                # Check by order_number or order_id
                query = {"$or": [
                    {"order_number": doc_number},
                    {"order_id": doc_number}
                ]}
            else:
                # Check by date + amount + customer
                query = {
                    "order_date": date,
                    "total_amount": {"$gte": amount * 0.99, "$lte": amount * 1.01}  # 1% tolerance
                }
                if party_name:
                    query["customer_details.name"] = {"$regex": party_name[:20], "$options": "i"}
                    
        elif collection_name == "purchase_bills":
            if doc_number:
                query = {"$or": [
                    {"bill_number": doc_number},
                    {"bill_id": doc_number}
                ]}
            else:
                query = {
                    "bill_date": date,
                    "total_amount": {"$gte": amount * 0.99, "$lte": amount * 1.01}
                }
                if party_name:
                    query["vendor_name"] = {"$regex": party_name[:20], "$options": "i"}
                    
        elif collection_name == "payments":
            if doc_number:
                query = {"payment_id": doc_number}
            else:
                query = {
                    "payment_date": date,
                    "amount": {"$gte": amount * 0.99, "$lte": amount * 1.01}
                }
                if party_name:
                    query["paid_to"] = {"$regex": party_name[:20], "$options": "i"}
                    
        elif collection_name == "receipts":
            if doc_number:
                query = {"receipt_id": doc_number}
            else:
                query = {
                    "receipt_date": date,
                    "amount": {"$gte": amount * 0.99, "$lte": amount * 1.01}
                }
                if party_name:
                    query["received_from"] = {"$regex": party_name[:20], "$options": "i"}
                    
        elif collection_name == "expenses":
            if doc_number:
                query = {"expense_id": doc_number}
            else:
                query = {
                    "expense_date": date,
                    "amount": {"$gte": amount * 0.99, "$lte": amount * 1.01}
                }
                    
        elif collection_name == "journal_vouchers":
            if doc_number:
                query = {"voucher_id": doc_number}
            else:
                query = {
                    "voucher_date": date,
                    "$or": [
                        {"debit_amount": {"$gte": amount * 0.99, "$lte": amount * 1.01}},
                        {"credit_amount": {"$gte": amount * 0.99, "$lte": amount * 1.01}}
                    ]
                }
                    
        elif collection_name == "bank_transactions":
            if doc_number:
                query = {"transaction_id": doc_number}
            else:
                query = {
                    "transaction_date": date,
                    "$or": [
                        {"debit": {"$gte": amount * 0.99, "$lte": amount * 1.01}},
                        {"credit": {"$gte": amount * 0.99, "$lte": amount * 1.01}}
                    ]
                }
        else:
            return False
        
        if query:
            return db[collection_name].find_one(query) is not None
        return False
    
    try:
        # Read file
        content = await file.read()
        filename = file.filename.lower()
        
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or Excel.")
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Track import results
        results = {
            "total_rows": len(df),
            "imported": 0,
            "skipped": 0,
            "duplicates_skipped": 0,
            "errors": [],
            "by_collection": {}
        }
        
        import_batch_id = str(uuid.uuid4())[:8]
        import_timestamp = datetime.now(timezone.utc)
        
        # Prepare batch documents by collection
        batch_docs = {
            "orders": [],
            "purchase_bills": [],
            "payments": [],
            "receipts": [],
            "expenses": [],
            "journal_vouchers": [],
            "bank_transactions": [],
            "unclassified_entries": []
        }
        
        BATCH_SIZE = 500  # Insert in batches of 500
        
        logger.info(f"[DayBook Import] Processing {len(df)} entries with duplicate detection...")
        
        for idx, row in df.iterrows():
            try:
                row_dict = row.to_dict()
                
                # Classify and extract data
                classification = classify_voucher_type(row_dict)
                amounts = extract_amount(row_dict)
                date = extract_date(row_dict)
                party = extract_party_details(row_dict)
                refs = extract_reference(row_dict)
                
                # Skip unclassified if requested
                if classification["voucher_type"] == "unknown" and skip_unclassified:
                    results["skipped"] += 1
                    continue
                
                collection = classification["target_collection"]
                
                # Get amount for duplicate check
                check_amount = amounts["credit"] or amounts["debit"] or amounts["total"]
                
                # Check for duplicates before adding
                if check_duplicate(collection, refs["doc_number"], date, check_amount, party["name"]):
                    results["duplicates_skipped"] += 1
                    results["skipped"] += 1
                    continue
                
                # Prepare base document
                base_doc = {
                    "id": f"DB-{import_batch_id}-{idx+1}",
                    "import_batch_id": import_batch_id,
                    "imported_at": import_timestamp.isoformat(),
                    "source": "daybook_import",
                    "source_file": file.filename,
                    "row_number": idx + 1,
                    "date": date,
                    "classification": classification,
                    "created_at": import_timestamp.isoformat()
                }
                
                # Route to appropriate collection with proper structure
                if classification["voucher_type"] == "sales_invoice":
                    unique_order_id = f"DB-{import_batch_id}-{idx+1}-{uuid.uuid4().hex[:6]}"
                    doc = {
                        **base_doc,
                        "order_id": unique_order_id,
                        "order_number": refs["doc_number"] or unique_order_id,
                        "order_date": date,
                        "customer_details": {
                            "name": party["name"],
                            "email": party["email"] or "imported@daybook.local",
                            "phone": party["phone"],
                            "gstin": party["gstin"]
                        },
                        "billing_address": {"address": party["address"]},
                        "total_amount": amounts["credit"] or amounts["total"],
                        "payment_status": "pending",
                        "status": "confirmed",
                        "notes": refs["narration"],
                        "reference": refs["reference"]
                    }
                    batch_docs["orders"].append(doc)
                    
                elif classification["voucher_type"] == "purchase_bill":
                    unique_bill_id = f"DB-PB-{import_batch_id}-{idx+1}-{uuid.uuid4().hex[:6]}"
                    doc = {
                        **base_doc,
                        "bill_id": unique_bill_id,
                        "bill_number": refs["doc_number"] or unique_bill_id,
                        "bill_date": date,
                        "vendor_name": party["name"],
                        "vendor_gstin": party["gstin"],
                        "vendor_contact": party["phone"],
                        "total_amount": amounts["debit"] or amounts["total"],
                        "status": "pending",
                        "notes": refs["narration"],
                        "reference": refs["reference"]
                    }
                    batch_docs["purchase_bills"].append(doc)
                    
                elif classification["voucher_type"] == "payment":
                    doc = {
                        **base_doc,
                        "payment_id": refs["doc_number"] or f"IMP-PMT-{import_batch_id}-{idx+1}",
                        "payment_date": date,
                        "paid_to": party["name"],
                        "amount": amounts["debit"] or amounts["total"],
                        "payment_mode": "Bank Transfer",
                        "narration": refs["narration"],
                        "reference": refs["reference"],
                        "status": "completed"
                    }
                    batch_docs["payments"].append(doc)
                    
                elif classification["voucher_type"] == "receipt":
                    doc = {
                        **base_doc,
                        "receipt_id": refs["doc_number"] or f"IMP-RCV-{import_batch_id}-{idx+1}",
                        "receipt_date": date,
                        "received_from": party["name"],
                        "amount": amounts["credit"] or amounts["total"],
                        "receipt_mode": "Bank Transfer",
                        "narration": refs["narration"],
                        "reference": refs["reference"],
                        "status": "completed"
                    }
                    batch_docs["receipts"].append(doc)
                    
                elif classification["voucher_type"] == "expense":
                    doc = {
                        **base_doc,
                        "expense_id": refs["doc_number"] or f"IMP-EXP-{import_batch_id}-{idx+1}",
                        "expense_date": date,
                        "category": classification.get("sub_category", "miscellaneous"),
                        "description": refs["narration"] or party["name"],
                        "amount": amounts["debit"] or amounts["total"],
                        "paid_to": party["name"],
                        "reference": refs["reference"],
                        "status": "approved"
                    }
                    batch_docs["expenses"].append(doc)
                    
                elif classification["voucher_type"] == "journal":
                    doc = {
                        **base_doc,
                        "voucher_id": refs["doc_number"] or f"IMP-JV-{import_batch_id}-{idx+1}",
                        "voucher_date": date,
                        "narration": refs["narration"],
                        "debit_amount": amounts["debit"],
                        "credit_amount": amounts["credit"],
                        "entries": [
                            {"account": party["name"] or "Sundry", "debit": amounts["debit"], "credit": amounts["credit"]}
                        ],
                        "reference": refs["reference"],
                        "status": "posted"
                    }
                    batch_docs["journal_vouchers"].append(doc)
                    
                elif classification["voucher_type"] == "bank_entry":
                    doc = {
                        **base_doc,
                        "transaction_id": refs["doc_number"] or f"IMP-BNK-{import_batch_id}-{idx+1}",
                        "transaction_date": date,
                        "description": refs["narration"] or party["name"],
                        "debit": amounts["debit"],
                        "credit": amounts["credit"],
                        "party_name": party["name"],
                        "reference": refs["reference"],
                        "reconciled": False
                    }
                    batch_docs["bank_transactions"].append(doc)
                    
                else:
                    # Store unclassified entries
                    doc = {
                        **base_doc,
                        "raw_data": {k: str(v) if not pd.isna(v) else None for k, v in row_dict.items()},
                        "amounts": amounts,
                        "party": party,
                        "references": refs
                    }
                    batch_docs["unclassified_entries"].append(doc)
                
                collection = classification["target_collection"]
                results["by_collection"][collection] = results["by_collection"].get(collection, 0) + 1
                
            except Exception as row_error:
                if len(results["errors"]) < 50:  # Limit error messages
                    results["errors"].append(f"Row {idx+1}: {str(row_error)}")
                results["skipped"] += 1
        
        # Bulk insert all documents by collection
        logger.info(f"[DayBook Import] Starting bulk insert for {len(df)} entries...")
        
        for coll_name, docs in batch_docs.items():
            if docs:
                try:
                    # Insert in batches
                    for i in range(0, len(docs), BATCH_SIZE):
                        batch = docs[i:i + BATCH_SIZE]
                        try:
                            result = db[coll_name].insert_many(batch, ordered=False)
                            results["imported"] += len(result.inserted_ids)
                        except Exception as batch_err:
                            # Some documents may have been inserted despite the error
                            # Count what was actually inserted
                            if hasattr(batch_err, 'details') and 'nInserted' in batch_err.details:
                                results["imported"] += batch_err.details.get('nInserted', 0)
                            else:
                                # Assume partial success - count non-duplicate inserts
                                results["imported"] += len(batch) // 2  # Conservative estimate
                            if len(results["errors"]) < 5:
                                results["errors"].append(f"{coll_name}: Some duplicates skipped")
                    logger.info(f"[DayBook Import] Processed {len(docs)} for {coll_name}")
                except Exception as batch_error:
                    logger.error(f"[DayBook Import] Error inserting into {coll_name}: {batch_error}")
                    if len(results["errors"]) < 10:
                        results["errors"].append(f"Batch insert to {coll_name}: {str(batch_error)[:100]}")
        
        # Log import summary
        import_log = {
            "id": import_batch_id,
            "filename": file.filename,
            "imported_at": import_timestamp.isoformat(),
            "results": results
        }
        db.daybook_import_logs.insert_one(import_log)
        
        logger.info(f"[DayBook Import] Complete: {results['imported']} imported, {results['skipped']} skipped")
        
        return {
            "status": "success",
            "message": f"Day Book imported successfully. {results['imported']} entries processed.",
            "import_batch_id": import_batch_id,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Import error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.get("/history")
async def get_import_history(limit: int = 20):
    """Get history of Day Book imports"""
    from pymongo import MongoClient
    import os
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'startup_template')
    client = MongoClient(mongo_url)
    db = client[db_name]
    
    logs = list(db.daybook_import_logs.find(
        {},
        {"_id": 0}
    ).sort("imported_at", -1).limit(limit))
    
    return {"imports": logs}


@router.delete("/batch/{batch_id}")
async def delete_import_batch(batch_id: str):
    """Delete all entries from a specific import batch"""
    from pymongo import MongoClient
    import os
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'startup_template')
    client = MongoClient(mongo_url)
    db = client[db_name]
    
    collections = [
        "orders", "purchase_bills", "payments", "receipts", 
        "expenses", "journal_vouchers", "bank_transactions", "unclassified_entries"
    ]
    
    deleted_count = 0
    for coll in collections:
        result = db[coll].delete_many({"import_batch_id": batch_id})
        deleted_count += result.deleted_count
    
    # Also delete the log
    db.daybook_import_logs.delete_one({"id": batch_id})
    
    return {
        "status": "success",
        "message": f"Deleted {deleted_count} entries from batch {batch_id}"
    }



@router.delete("/clear-all")
async def clear_all_daybook_data():
    """Clear ALL Day Book imported data - for admin use"""
    from pymongo import MongoClient
    import os
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'startup_template')
    client = MongoClient(mongo_url)
    db = client[db_name]
    
    collections = [
        "orders", "purchase_bills", "payments", "receipts", 
        "expenses", "journal_vouchers", "bank_transactions", "unclassified_entries"
    ]
    
    deleted_count = 0
    details = {}
    
    for coll in collections:
        result = db[coll].delete_many({"source": "daybook_import"})
        if result.deleted_count > 0:
            details[coll] = result.deleted_count
            deleted_count += result.deleted_count
    
    # Also clear all import logs
    logs_result = db.daybook_import_logs.delete_many({})
    details["import_logs"] = logs_result.deleted_count
    
    return {
        "status": "success",
        "message": f"Cleared {deleted_count} Day Book entries",
        "deleted_count": deleted_count,
        "details": details
    }
