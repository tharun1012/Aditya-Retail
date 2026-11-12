"""
Tally Voucher Import Routes
Handles import of all voucher types from Tally Excel exports:
- Sales/Invoices
- Purchases
- Expenses
- Payments
- Receipts
- Credit Notes (CN)
- Debit Notes (DN)
- Journal Entries
- Contra Entries
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends, Body
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from database import get_db
import pandas as pd
import numpy as np
import io
import uuid
import logging

router = APIRouter(prefix="/tally-voucher", tags=["Tally Voucher Import"])
logger = logging.getLogger(__name__)


# Voucher type configurations
VOUCHER_CONFIG = {
    'sales': {
        'collection': 'orders',
        'display_name': 'Sales/Invoices',
        'id_prefix': 'SI',
        'date_field': 'order_date',
        'amount_field': 'total_amount',
        'party_field': 'customer_details',
        'number_field': 'order_number'
    },
    'purchases': {
        'collection': 'purchase_bills',
        'display_name': 'Purchase Bills',
        'id_prefix': 'PB',
        'date_field': 'bill_date',
        'amount_field': 'total_amount',
        'party_field': 'vendor_name',
        'number_field': 'bill_number'
    },
    'expenses': {
        'collection': 'expenses',
        'display_name': 'Expenses',
        'id_prefix': 'EXP',
        'date_field': 'expense_date',
        'amount_field': 'amount',
        'party_field': 'paid_to',
        'number_field': 'expense_id'
    },
    'payments': {
        'collection': 'payments',
        'display_name': 'Payments',
        'id_prefix': 'PAY',
        'date_field': 'payment_date',
        'amount_field': 'amount',
        'party_field': 'paid_to',
        'number_field': 'payment_id'
    },
    'receipts': {
        'collection': 'receipts',
        'display_name': 'Receipts',
        'id_prefix': 'RCT',
        'date_field': 'receipt_date',
        'amount_field': 'amount',
        'party_field': 'received_from',
        'number_field': 'receipt_id'
    },
    'credit_notes': {
        'collection': 'credit_notes',
        'display_name': 'Credit Notes',
        'id_prefix': 'CN',
        'date_field': 'note_date',
        'amount_field': 'amount',
        'party_field': 'party_name',
        'number_field': 'note_id'
    },
    'debit_notes': {
        'collection': 'debit_notes',
        'display_name': 'Debit Notes',
        'id_prefix': 'DN',
        'date_field': 'note_date',
        'amount_field': 'amount',
        'party_field': 'party_name',
        'number_field': 'note_id'
    },
    'journals': {
        'collection': 'journal_vouchers',
        'display_name': 'Journal Entries',
        'id_prefix': 'JV',
        'date_field': 'voucher_date',
        'amount_field': 'debit_amount',
        'party_field': 'ledger',
        'number_field': 'voucher_id'
    },
    'contra': {
        'collection': 'contra_entries',
        'display_name': 'Contra Entries',
        'id_prefix': 'CTR',
        'date_field': 'contra_date',
        'amount_field': 'debit_amount',
        'party_field': 'debit_account',
        'number_field': 'contra_id'
    }
}


def find_column(df, patterns: List[str]) -> Optional[str]:
    """Find column matching any of the patterns (case insensitive)"""
    for col in df.columns:
        col_lower = str(col).lower().strip()
        for pattern in patterns:
            if pattern.lower() in col_lower:
                return col
    return None


def parse_date(value) -> Optional[str]:
    """Parse date from various formats"""
    if pd.isna(value):
        return None
    try:
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d')
        elif isinstance(value, str):
            # Try common formats
            for fmt in ['%d-%b-%y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%b-%Y']:
                try:
                    return datetime.strptime(value.strip(), fmt).strftime('%Y-%m-%d')
                except Exception:
                    continue
            return value
        return str(value)
    except Exception:
        return None


def parse_amount(value) -> float:
    """Parse amount handling various formats"""
    if pd.isna(value):
        return 0.0
    try:
        if isinstance(value, (int, float)):
            return abs(float(value))
        # Remove currency symbols and commas
        clean = str(value).replace('₹', '').replace(',', '').replace(' ', '').strip()
        if clean.startswith('(') and clean.endswith(')'):
            clean = clean[1:-1]
        if clean == '' or clean == '-':
            return 0.0
        return abs(float(clean))
    except Exception:
        return 0.0


def convert_to_native(value):
    """Convert numpy types to native Python types"""
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


@router.post("/analyze/{voucher_type}")
async def analyze_tally_file(
    voucher_type: str,
    file: UploadFile = File(...)
):
    """
    Analyze a Tally Excel file and return column mapping suggestions
    """
    if voucher_type not in VOUCHER_CONFIG:
        raise HTTPException(status_code=400, detail=f"Invalid voucher type: {voucher_type}")
    
    try:
        content = await file.read()
        
        # Read Excel file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
        
        # Find header row (skip empty rows at top)
        header_row = 0
        for i in range(min(20, len(df))):
            non_null = df.iloc[i].notna().sum()
            if non_null >= 3:
                header_row = i
                break
        
        if header_row > 0:
            df = pd.read_excel(io.BytesIO(content), header=header_row)
        
        # Get column list
        columns = [str(col).strip() for col in df.columns.tolist()]
        
        # Auto-detect common columns
        detected_columns = {
            'date': find_column(df, ['date', 'voucher date', 'invoice date', 'bill date']),
            'voucher_number': find_column(df, ['voucher no', 'invoice no', 'bill no', 'number', 'ref no']),
            'party': find_column(df, ['party', 'customer', 'vendor', 'name', 'particulars', 'ledger']),
            'debit': find_column(df, ['debit', 'dr', 'debit amount']),
            'credit': find_column(df, ['credit', 'cr', 'credit amount']),
            'amount': find_column(df, ['amount', 'total', 'value', 'gross']),
            'narration': find_column(df, ['narration', 'description', 'remarks', 'notes']),
            'voucher_type': find_column(df, ['voucher type', 'vch type', 'type']),
        }
        
        # Get sample data
        sample_data = []
        for i in range(min(5, len(df))):
            row_data = {}
            for col in columns[:10]:  # First 10 columns
                val = df.iloc[i].get(col)
                row_data[col] = str(val) if not pd.isna(val) else ''
            sample_data.append(row_data)
        
        return {
            "status": "success",
            "file_name": file.filename,
            "total_rows": len(df),
            "columns": columns,
            "detected_columns": detected_columns,
            "sample_data": sample_data,
            "voucher_type": voucher_type,
            "config": VOUCHER_CONFIG[voucher_type]
        }
        
    except Exception as e:
        logger.error(f"File analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze file: {str(e)}")


@router.post("/import/{voucher_type}")
async def import_tally_vouchers(
    voucher_type: str,
    file: UploadFile = File(...),
    column_mapping: Optional[str] = None,
    skip_duplicates: bool = True,
    db=Depends(get_db)
):
    """
    Import vouchers from Tally Excel file
    """
    if voucher_type not in VOUCHER_CONFIG:
        raise HTTPException(status_code=400, detail=f"Invalid voucher type: {voucher_type}")
    
    config = VOUCHER_CONFIG[voucher_type]
    collection_name = config['collection']
    
    try:
        content = await file.read()
        
        # Read Excel file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
        
        # Find header row
        header_row = 0
        for i in range(min(20, len(df))):
            non_null = df.iloc[i].notna().sum()
            if non_null >= 3:
                header_row = i
                break
        
        if header_row > 0:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(content), skiprows=header_row)
            else:
                df = pd.read_excel(io.BytesIO(content), header=header_row)
        
        # Log all columns found in file
        all_columns = [str(col).strip() for col in df.columns.tolist()]
        logger.info(f"File columns: {all_columns}")
        
        # Detect columns
        date_col = find_column(df, ['date', 'voucher date', 'invoice date', 'bill date'])
        number_col = find_column(df, ['voucher no', 'invoice no', 'bill no', 'number', 'ref no', 'vch no'])
        party_col = find_column(df, ['party', 'customer', 'vendor', 'name', 'particulars', 'ledger'])
        debit_col = find_column(df, ['debit', 'dr', 'debit amount'])
        credit_col = find_column(df, ['credit', 'cr', 'credit amount'])
        amount_col = find_column(df, ['amount', 'total', 'value', 'gross'])
        narration_col = find_column(df, ['narration', 'description', 'remarks', 'notes'])
        
        # Log detected mappings
        detected_mapping = {
            'date': date_col,
            'number': number_col,
            'party': party_col,
            'debit': debit_col,
            'credit': credit_col,
            'amount': amount_col,
            'narration': narration_col
        }
        logger.info(f"Detected column mapping: {detected_mapping}")
        
        # Import tracking
        import_batch_id = str(uuid.uuid4())[:8]
        import_timestamp = datetime.now(timezone.utc)
        
        results = {
            "total_rows": len(df),
            "imported": 0,
            "skipped_duplicates": 0,
            "skipped_empty": 0,
            "errors": [],
            "imported_entries": [],  # List of imported entries with details
            "skipped_entries": [],   # List of skipped entries with details
            "detected_columns": detected_mapping,  # Include detected columns in response for debugging
            "file_columns": all_columns  # Include all file columns
        }
        
        # Additional column detection for specific fields
        unit_rate_col = find_column(df, ['unit_rate', 'rate', 'unit_price', 'price', 'unit price', 'unit rate'])
        quantity_col = find_column(df, ['quantity', 'qty', 'units'])
        tax_rate_col = find_column(df, ['tax_rate', 'tax', 'gst', 'tax %', 'gst %', 'tax rate'])
        
        documents = []
        
        for idx, row in df.iterrows():
            try:
                # Helper to safely get string value (handles NaN)
                def safe_str(val, default=''):
                    if pd.isna(val):
                        return default
                    return str(val).strip()
                
                # Extract values
                date = parse_date(row.get(date_col)) if date_col else None
                voucher_no = safe_str(row.get(number_col)) if number_col else ''
                party = safe_str(row.get(party_col)) if party_col else ''
                
                # Get amount - try multiple methods
                debit = parse_amount(row.get(debit_col)) if debit_col else 0
                credit = parse_amount(row.get(credit_col)) if credit_col else 0
                direct_amount = parse_amount(row.get(amount_col)) if amount_col else 0
                
                # Calculate from unit_rate * quantity if available
                unit_rate = parse_amount(row.get(unit_rate_col)) if unit_rate_col else 0
                quantity = parse_amount(row.get(quantity_col)) if quantity_col else 1
                tax_rate = parse_amount(row.get(tax_rate_col)) if tax_rate_col else 0
                
                calculated_amount = 0
                if unit_rate and quantity:
                    subtotal = unit_rate * quantity
                    tax = subtotal * (tax_rate / 100) if tax_rate else 0
                    calculated_amount = subtotal + tax
                
                # Use best available amount
                amount = calculated_amount or direct_amount or debit or credit
                
                narration = safe_str(row.get(narration_col)) if narration_col else ''
                
                # Preserve ALL raw data from Excel
                raw_data = {}
                for col in row.index:
                    val = row[col]
                    raw_data[str(col)] = convert_to_native(val)
                
                # Skip empty rows
                if not party and not amount and not voucher_no:
                    results["skipped_empty"] += 1
                    continue
                
                # Generate unique ID
                entry_id = f"{config['id_prefix']}-{import_batch_id}-{idx+1}"
                
                # Check for duplicates
                if skip_duplicates and voucher_no:
                    existing = await db[collection_name].find_one({
                        config['number_field']: voucher_no
                    })
                    if existing:
                        results["skipped_duplicates"] += 1
                        # Add to skipped entries list with details
                        results["skipped_entries"].append({
                            "row_number": idx + 1,
                            "voucher_no": voucher_no,
                            "date": date,
                            "party": party,
                            "debit": debit,
                            "credit": credit,
                            "amount": amount,
                            "narration": narration,
                            "reason": "Duplicate - Voucher number already exists",
                            "existing_id": existing.get("id"),
                            "raw_data": raw_data
                        })
                        continue
                
                # Create document based on voucher type
                # Pass additional calculated values for proper tax handling
                doc = create_voucher_document(
                    voucher_type, config, entry_id, import_batch_id,
                    file.filename, import_timestamp, idx + 1,
                    date, voucher_no, party, debit, credit, amount, narration, raw_data,
                    unit_rate=unit_rate, quantity=quantity, tax_rate=tax_rate
                )
                
                documents.append(doc)
                
                # Add to imported entries list
                results["imported_entries"].append({
                    "id": entry_id,
                    "row_number": idx + 1,
                    "voucher_no": voucher_no,
                    "date": date,
                    "party": party,
                    "debit": debit,
                    "credit": credit,
                    "amount": amount,
                    "narration": narration,
                    "status": "imported",
                    "raw_data": raw_data
                })
                
            except Exception as e:
                if len(results["errors"]) < 10:
                    results["errors"].append(f"Row {idx+1}: {str(e)[:50]}")
        
        # Bulk insert
        if documents:
            await db[collection_name].insert_many(documents)
            results["imported"] = len(documents)
        
        # Log import
        await db.tally_import_logs.insert_one({
            "id": import_batch_id,
            "voucher_type": voucher_type,
            "collection": collection_name,
            "file_name": file.filename,
            "total_rows": results["total_rows"],
            "imported": results["imported"],
            "skipped_duplicates": results["skipped_duplicates"],
            "skipped_empty": results["skipped_empty"],
            "errors": results["errors"],
            "imported_at": import_timestamp.isoformat()
        })
        
        return {
            "status": "success",
            "message": f"Imported {results['imported']} {config['display_name']}",
            "import_batch_id": import_batch_id,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Import error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


def create_voucher_document(
    voucher_type: str, config: Dict, entry_id: str, batch_id: str,
    file_name: str, timestamp: datetime, row_num: int,
    date: str, voucher_no: str, party: str, 
    debit: float, credit: float, amount: float, narration: str, raw_data: Dict,
    unit_rate: float = 0, quantity: float = 1, tax_rate: float = 0
) -> Dict:
    """Create document for specific voucher type"""
    
    # Calculate proper amounts if unit_rate is available
    if unit_rate and quantity:
        subtotal = unit_rate * quantity
        tax_amount = subtotal * (tax_rate / 100) if tax_rate else 0
        total_amount = subtotal + tax_amount
    else:
        subtotal = amount
        tax_amount = 0
        total_amount = amount
    
    base = {
        "id": entry_id,
        "import_batch_id": batch_id,
        "source": "tally_import",
        "source_file": file_name,
        "row_number": row_num,
        "imported_at": timestamp.isoformat(),
        "created_at": timestamp.isoformat(),
        "raw_data": raw_data
    }
    
    if voucher_type == 'sales':
        return {
            **base,
            "order_id": entry_id,
            "order_number": voucher_no or entry_id,
            "order_date": date,
            "customer_details": {"name": party, "email": "", "phone": ""},
            "total_amount": total_amount or credit or amount,
            "subtotal": subtotal or credit or amount,
            "tax_amount": tax_amount,
            "discount": 0,
            "status": "confirmed",
            "payment_status": "pending",
            "notes": narration
        }
    
    elif voucher_type == 'purchases':
        return {
            **base,
            "bill_id": entry_id,
            "bill_number": voucher_no or entry_id,
            "bill_date": date,
            "vendor_name": party,
            "vendor": {"name": party},
            "total_amount": total_amount or debit or amount,
            "subtotal": subtotal or debit or amount,
            "cgst": tax_amount / 2 if tax_amount else 0,
            "sgst": tax_amount / 2 if tax_amount else 0,
            "total_tax": tax_amount,
            "status": "pending",
            "payment_status": "pending",
            "notes": narration
        }
    
    elif voucher_type == 'expenses':
        return {
            **base,
            "expense_id": voucher_no or entry_id,
            "expense_date": date,
            "description": narration or party,
            "amount": debit or amount,
            "category": detect_expense_category(party, narration),
            "paid_to": party,
            "payment_mode": "bank",
            "status": "approved",
            "notes": narration
        }
    
    elif voucher_type == 'payments':
        return {
            **base,
            "payment_id": voucher_no or entry_id,
            "payment_date": date,
            "paid_to": party,
            "amount": debit or amount,
            "payment_mode": "bank",
            "reference_no": voucher_no,
            "narration": narration,
            "status": "completed"
        }
    
    elif voucher_type == 'receipts':
        return {
            **base,
            "receipt_id": voucher_no or entry_id,
            "receipt_date": date,
            "received_from": party,
            "amount": credit or amount,
            "receipt_mode": "bank",
            "reference_no": voucher_no,
            "narration": narration,
            "status": "completed"
        }
    
    elif voucher_type == 'credit_notes':
        return {
            **base,
            "note_id": voucher_no or entry_id,
            "note_number": voucher_no or entry_id,
            "note_date": date,
            "party_name": party,
            "amount": credit or amount,
            "reason": narration,
            "status": "approved"
        }
    
    elif voucher_type == 'debit_notes':
        return {
            **base,
            "note_id": voucher_no or entry_id,
            "note_number": voucher_no or entry_id,
            "note_date": date,
            "party_name": party,
            "amount": debit or amount,
            "reason": narration,
            "status": "approved"
        }
    
    elif voucher_type == 'journals':
        return {
            **base,
            "voucher_id": voucher_no or entry_id,
            "voucher_number": voucher_no or entry_id,
            "voucher_date": date,
            "ledger": party,
            "debit_amount": debit,
            "credit_amount": credit,
            "narration": narration,
            "status": "posted"
        }
    
    elif voucher_type == 'contra':
        return {
            **base,
            "contra_id": voucher_no or entry_id,
            "contra_number": voucher_no or entry_id,
            "contra_date": date,
            "debit_account": party if debit > 0 else "",
            "credit_account": party if credit > 0 else "",
            "debit_amount": debit,
            "credit_amount": credit,
            "narration": narration,
            "status": "posted"
        }
    
    return base


def detect_expense_category(party: str, narration: str) -> str:
    """Detect expense category from party name or narration"""
    text = f"{party} {narration}".lower()
    
    categories = {
        "rent": ["rent", "lease", "premises"],
        "salary": ["salary", "wages", "payroll", "staff"],
        "utilities": ["electricity", "water", "bescom", "telephone", "internet", "mobile"],
        "travel": ["travel", "petrol", "diesel", "fuel", "conveyance", "transport"],
        "office": ["office", "stationery", "supplies", "printing"],
        "professional": ["professional", "legal", "audit", "consultant", "ca ", "advocate"],
        "bank_charges": ["bank charges", "interest", "commission", "emi"],
        "insurance": ["insurance", "premium", "lic"],
        "marketing": ["marketing", "advertisement", "promotion"],
        "repairs": ["repair", "maintenance", "service", "amc"]
    }
    
    for category, keywords in categories.items():
        if any(kw in text for kw in keywords):
            return category
    
    return "miscellaneous"


@router.get("/stats")
async def get_import_stats(db=Depends(get_db)):
    """Get statistics of all imported vouchers"""
    stats = {
        "by_type": {},
        "total_imported": 0
    }
    
    for vtype, config in VOUCHER_CONFIG.items():
        count = await db[config['collection']].count_documents({"source": "tally_import"})
        if count > 0:
            stats["by_type"][config['display_name']] = count
            stats["total_imported"] += count
    
    return stats


@router.delete("/clear/{voucher_type}")
async def clear_voucher_type(voucher_type: str, db=Depends(get_db)):
    """Clear all imported vouchers of a specific type"""
    if voucher_type not in VOUCHER_CONFIG:
        raise HTTPException(status_code=400, detail=f"Invalid voucher type: {voucher_type}")
    
    config = VOUCHER_CONFIG[voucher_type]
    result = await db[config['collection']].delete_many({"source": "tally_import"})
    
    return {
        "status": "success",
        "message": f"Deleted {result.deleted_count} {config['display_name']}",
        "deleted_count": result.deleted_count
    }


@router.delete("/clear-all")
async def clear_all_imported(db=Depends(get_db)):
    """Clear all imported vouchers from all types"""
    total_deleted = 0
    deleted_by_type = {}
    
    for vtype, config in VOUCHER_CONFIG.items():
        result = await db[config['collection']].delete_many({"source": "tally_import"})
        if result.deleted_count > 0:
            deleted_by_type[config['display_name']] = result.deleted_count
            total_deleted += result.deleted_count
    
    return {
        "status": "success",
        "message": f"Deleted {total_deleted} total entries",
        "total_deleted": total_deleted,
        "deleted_by_type": deleted_by_type
    }


@router.post("/overwrite/{voucher_type}")
async def overwrite_voucher(
    voucher_type: str,
    entry_data: Dict[str, Any] = Body(...),
    db=Depends(get_db)
):
    """
    Overwrite an existing voucher entry with new data
    Used when user wants to force update a skipped duplicate
    """
    if voucher_type not in VOUCHER_CONFIG:
        raise HTTPException(status_code=400, detail=f"Invalid voucher type: {voucher_type}")
    
    config = VOUCHER_CONFIG[voucher_type]
    collection_name = config['collection']
    number_field = config['number_field']
    
    voucher_no = entry_data.get('voucher_no')
    if not voucher_no:
        raise HTTPException(status_code=400, detail="voucher_no is required")
    
    try:
        # Find existing entry
        existing = await db[collection_name].find_one({number_field: voucher_no})
        if not existing:
            raise HTTPException(status_code=404, detail=f"Entry with voucher number {voucher_no} not found")
        
        # Build update document from raw_data
        raw_data = entry_data.get('raw_data', {})
        
        # Parse values
        date = parse_date(entry_data.get('date'))
        party = entry_data.get('party', '')
        debit = parse_amount(entry_data.get('debit', 0))
        credit = parse_amount(entry_data.get('credit', 0))
        amount = parse_amount(entry_data.get('amount', 0)) or (debit or credit)
        narration = entry_data.get('narration', '')
        
        # Create update based on voucher type
        update_timestamp = datetime.now(timezone.utc)
        
        update_doc = {
            "raw_data": raw_data,
            "updated_at": update_timestamp.isoformat(),
            "overwritten": True,
            "overwritten_at": update_timestamp.isoformat()
        }
        
        # Add type-specific fields
        if voucher_type == 'sales':
            update_doc.update({
                "order_date": date,
                "customer_details": {"name": party, "email": "", "phone": ""},
                "total_amount": credit or amount,
                "subtotal": credit or amount,
                "notes": narration
            })
        elif voucher_type == 'purchases':
            update_doc.update({
                "bill_date": date,
                "vendor_name": party,
                "vendor": {"name": party},
                "total_amount": debit or amount,
                "subtotal": debit or amount,
                "notes": narration
            })
        elif voucher_type == 'expenses':
            update_doc.update({
                "expense_date": date,
                "description": narration or party,
                "amount": debit or amount,
                "paid_to": party,
                "notes": narration
            })
        elif voucher_type == 'payments':
            update_doc.update({
                "payment_date": date,
                "paid_to": party,
                "amount": debit or amount,
                "narration": narration
            })
        elif voucher_type == 'receipts':
            update_doc.update({
                "receipt_date": date,
                "received_from": party,
                "amount": credit or amount,
                "narration": narration
            })
        elif voucher_type == 'credit_notes':
            update_doc.update({
                "note_date": date,
                "party_name": party,
                "amount": credit or amount,
                "reason": narration
            })
        elif voucher_type == 'debit_notes':
            update_doc.update({
                "note_date": date,
                "party_name": party,
                "amount": debit or amount,
                "reason": narration
            })
        elif voucher_type == 'journals':
            update_doc.update({
                "voucher_date": date,
                "ledger": party,
                "debit_amount": debit,
                "credit_amount": credit,
                "narration": narration
            })
        elif voucher_type == 'contra':
            update_doc.update({
                "contra_date": date,
                "debit_account": party if debit > 0 else existing.get('debit_account', ''),
                "credit_account": party if credit > 0 else existing.get('credit_account', ''),
                "debit_amount": debit,
                "credit_amount": credit,
                "narration": narration
            })
        
        # Perform update
        result = await db[collection_name].update_one(
            {number_field: voucher_no},
            {"$set": update_doc}
        )
        
        if result.modified_count > 0:
            return {
                "status": "success",
                "message": f"Entry {voucher_no} has been overwritten",
                "voucher_no": voucher_no
            }
        else:
            return {
                "status": "warning",
                "message": "No changes made - data may be identical",
                "voucher_no": voucher_no
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Overwrite error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to overwrite entry: {str(e)}")



from fastapi.responses import StreamingResponse

# Template definitions for each voucher type
VOUCHER_TEMPLATES = {
    'sales': {
        'headers': ['Voucher No', 'Date', 'Party Name', 'Debit', 'Credit', 'Narration', 'GSTIN', 'Place of Supply'],
        'sample_rows': [
            ['SI-001', '15-Jan-2025', 'ABC Traders Pvt Ltd', '0', '50000', 'Sales of goods', '29AABCT1234F1Z5', 'Karnataka'],
            ['SI-002', '16-Jan-2025', 'XYZ Enterprises', '0', '75000', 'Service invoice', '27AABCX5678G1Z3', 'Maharashtra'],
        ]
    },
    'purchases': {
        'headers': ['Voucher No', 'Date', 'Party Name', 'Debit', 'Credit', 'Narration', 'GSTIN', 'Bill No'],
        'sample_rows': [
            ['PB-001', '10-Jan-2025', 'Supplier Corp', '45000', '0', 'Purchase of raw materials', '29AABCS1234H1Z8', 'SUP/2025/001'],
            ['PB-002', '12-Jan-2025', 'Vendor Industries', '32000', '0', 'Office supplies', '27AABCV5678K1Z2', 'VEN/2025/045'],
        ]
    },
    'expenses': {
        'headers': ['Voucher No', 'Date', 'Party Name', 'Debit', 'Credit', 'Narration', 'Category'],
        'sample_rows': [
            ['EXP-001', '05-Jan-2025', 'BESCOM', '5000', '0', 'Electricity bill for January', 'Utilities'],
            ['EXP-002', '08-Jan-2025', 'Office Rent Account', '25000', '0', 'Monthly rent payment', 'Rent'],
            ['EXP-003', '10-Jan-2025', 'Airtel', '2500', '0', 'Internet and phone charges', 'Telephone'],
        ]
    },
    'payments': {
        'headers': ['Voucher No', 'Date', 'Party Name', 'Debit', 'Credit', 'Narration', 'Payment Mode', 'Reference No'],
        'sample_rows': [
            ['PAY-001', '15-Jan-2025', 'Supplier Corp', '45000', '0', 'Payment against bill PB-001', 'Bank Transfer', 'UTR123456'],
            ['PAY-002', '18-Jan-2025', 'Vendor Industries', '32000', '0', 'Payment for supplies', 'Cheque', 'CHQ-789012'],
        ]
    },
    'receipts': {
        'headers': ['Voucher No', 'Date', 'Party Name', 'Debit', 'Credit', 'Narration', 'Receipt Mode', 'Reference No'],
        'sample_rows': [
            ['RCT-001', '20-Jan-2025', 'ABC Traders Pvt Ltd', '0', '50000', 'Receipt against invoice SI-001', 'Bank Transfer', 'UTR789456'],
            ['RCT-002', '22-Jan-2025', 'XYZ Enterprises', '0', '75000', 'Payment received for services', 'UPI', 'UPI/123/456'],
        ]
    },
    'credit_notes': {
        'headers': ['Voucher No', 'Date', 'Party Name', 'Debit', 'Credit', 'Narration', 'Against Invoice'],
        'sample_rows': [
            ['CN-001', '25-Jan-2025', 'ABC Traders Pvt Ltd', '0', '5000', 'Sales return - damaged goods', 'SI-001'],
            ['CN-002', '28-Jan-2025', 'XYZ Enterprises', '0', '2500', 'Discount adjustment', 'SI-002'],
        ]
    },
    'debit_notes': {
        'headers': ['Voucher No', 'Date', 'Party Name', 'Debit', 'Credit', 'Narration', 'Against Bill'],
        'sample_rows': [
            ['DN-001', '26-Jan-2025', 'Supplier Corp', '3000', '0', 'Purchase return - defective items', 'PB-001'],
            ['DN-002', '29-Jan-2025', 'Vendor Industries', '1500', '0', 'Rate difference claim', 'PB-002'],
        ]
    },
    'journals': {
        'headers': ['Voucher No', 'Date', 'Ledger', 'Debit', 'Credit', 'Narration'],
        'sample_rows': [
            ['JV-001', '31-Jan-2025', 'Depreciation A/c', '10000', '0', 'Monthly depreciation on machinery'],
            ['JV-001', '31-Jan-2025', 'Accumulated Depreciation', '0', '10000', 'Monthly depreciation on machinery'],
            ['JV-002', '31-Jan-2025', 'Interest Receivable', '5000', '0', 'Interest accrued on FD'],
            ['JV-002', '31-Jan-2025', 'Interest Income', '0', '5000', 'Interest accrued on FD'],
        ]
    },
    'contra': {
        'headers': ['Voucher No', 'Date', 'Debit Account', 'Credit Account', 'Debit', 'Credit', 'Narration'],
        'sample_rows': [
            ['CTR-001', '05-Jan-2025', 'HDFC Bank A/c', 'Cash in Hand', '50000', '0', 'Cash deposited to bank'],
            ['CTR-002', '10-Jan-2025', 'Cash in Hand', 'ICICI Bank A/c', '0', '25000', 'Cash withdrawn from bank'],
            ['CTR-003', '15-Jan-2025', 'SBI Bank A/c', 'HDFC Bank A/c', '100000', '0', 'Fund transfer between banks'],
        ]
    }
}


@router.get("/template/{voucher_type}")
async def download_voucher_template(voucher_type: str):
    """
    Download CSV template for a specific voucher type
    """
    if voucher_type not in VOUCHER_TEMPLATES:
        raise HTTPException(status_code=404, detail=f"Template not found for voucher type: {voucher_type}")
    
    template = VOUCHER_TEMPLATES[voucher_type]
    
    # Build CSV content
    lines = [','.join(template['headers'])]
    for row in template['sample_rows']:
        lines.append(','.join(str(cell) for cell in row))
    
    csv_content = '\n'.join(lines)
    
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={voucher_type}_template.csv"
        }
    )

