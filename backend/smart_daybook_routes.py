"""
Smart AI Day Book Import - Format Agnostic
Automatically detects and understands ANY Excel/CSV format from Tally or other systems.
Uses intelligent column detection and content analysis.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import pandas as pd
import numpy as np
import uuid
import os
import io
import re
import logging

router = APIRouter(prefix="/smart-daybook", tags=["Smart Day Book Import"])
logger = logging.getLogger(__name__)

UPLOAD_DIR = "/app/backend/uploads/daybook_imports"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============ INTELLIGENT COLUMN DETECTION ============

def detect_column_type(column_name: str, sample_values: List) -> str:
    """
    AI-powered column type detection based on column name and sample values.
    Returns: date, amount, debit, credit, party, voucher_type, voucher_no, narration, account, unknown
    """
    col_lower = column_name.lower().strip()
    
    # Check column name patterns
    date_patterns = ['date', 'dt', 'dated', 'vch date', 'voucher date', 'trans date', 'transaction date']
    debit_patterns = ['debit', 'dr', 'dr.', 'dr amt', 'debit amount', 'debit amt']
    credit_patterns = ['credit', 'cr', 'cr.', 'cr amt', 'credit amount', 'credit amt']
    amount_patterns = ['amount', 'amt', 'value', 'total', 'net', 'gross']
    party_patterns = ['party', 'customer', 'vendor', 'supplier', 'name', 'party name', 'ledger', 'account name', 'particulars']
    voucher_type_patterns = ['voucher type', 'vch type', 'type', 'vch ty', 'trans type', 'transaction type', 'v type']
    voucher_no_patterns = ['voucher no', 'vch no', 'voucher number', 'invoice no', 'bill no', 'doc no', 'ref no', 'reference', 'vch no.']
    narration_patterns = ['narration', 'description', 'remarks', 'notes', 'particular', 'details', 'memo']
    
    # Match by column name
    if any(p in col_lower for p in date_patterns):
        return 'date'
    if any(p == col_lower or col_lower.startswith(p) for p in debit_patterns):
        return 'debit'
    if any(p == col_lower or col_lower.startswith(p) for p in credit_patterns):
        return 'credit'
    if any(p in col_lower for p in voucher_type_patterns):
        return 'voucher_type'
    if any(p in col_lower for p in voucher_no_patterns):
        return 'voucher_no'
    if any(p in col_lower for p in narration_patterns):
        return 'narration'
    if any(p in col_lower for p in party_patterns):
        return 'party'
    if any(p in col_lower for p in amount_patterns):
        return 'amount'
    
    # If column name doesn't match, analyze sample values
    non_null_values = [v for v in sample_values if v is not None and str(v).strip() and not pd.isna(v)]
    
    if not non_null_values:
        return 'unknown'
    
    # Check if values look like dates
    date_count = 0
    for v in non_null_values[:10]:
        try:
            if isinstance(v, (datetime, pd.Timestamp)):
                date_count += 1
            elif re.match(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', str(v)):
                date_count += 1
            elif re.match(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}', str(v)):
                date_count += 1
        except Exception:
            pass
    if date_count >= len(non_null_values[:10]) * 0.7:
        return 'date'
    
    # Check if values look like numbers (amounts)
    number_count = 0
    for v in non_null_values[:10]:
        try:
            cleaned = re.sub(r'[₹,$,\s]', '', str(v))
            float(cleaned)
            number_count += 1
        except Exception:
            pass
    if number_count >= len(non_null_values[:10]) * 0.8:
        return 'amount'
    
    # Check if values look like voucher types
    voucher_keywords = ['SALES', 'PURCHASE', 'PAYMENT', 'RECEIPT', 'JOURNAL', 'CONTRA', 'CREDIT NOTE', 'DEBIT NOTE']
    voucher_match = sum(1 for v in non_null_values[:10] if any(kw in str(v).upper() for kw in voucher_keywords))
    if voucher_match >= len(non_null_values[:10]) * 0.5:
        return 'voucher_type'
    
    return 'unknown'


def analyze_file_structure(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze the file structure and detect column mappings automatically.
    """
    column_mapping = {}
    detected_columns = {}
    
    for col in df.columns:
        sample_values = df[col].head(20).tolist()
        col_type = detect_column_type(str(col), sample_values)
        
        detected_columns[col] = {
            'detected_type': col_type,
            'sample_values': [str(v)[:50] for v in sample_values[:5] if v is not None and not pd.isna(v)]
        }
        
        # Build mapping (prefer first match for each type)
        if col_type not in ['unknown'] and col_type not in column_mapping:
            column_mapping[col_type] = col
        elif col_type == 'amount' and 'debit' not in column_mapping:
            # If we find a generic amount column and no debit yet, use it as amount
            column_mapping['amount'] = col
    
    return {
        'columns': list(df.columns),
        'column_mapping': column_mapping,
        'detected_columns': detected_columns,
        'row_count': len(df)
    }


def extract_value(row: pd.Series, column_mapping: Dict, field: str, default=None):
    """Extract value from row using column mapping"""
    col = column_mapping.get(field)
    if col and col in row.index:
        val = row[col]
        if pd.isna(val):
            return default
        return val
    return default


def parse_amount(value) -> float:
    """Parse amount from various formats"""
    if value is None or pd.isna(value):
        return 0.0
    try:
        if isinstance(value, (int, float)):
            return abs(float(value))
        # Remove currency symbols and commas
        cleaned = re.sub(r'[₹$,\s()]', '', str(value))
        # Handle negative in parentheses like (1000)
        if cleaned.startswith('-') or '(' in str(value):
            return abs(float(cleaned.replace('-', '')))
        return abs(float(cleaned)) if cleaned else 0.0
    except Exception:
        return 0.0


def parse_date(value) -> str:
    """Parse date from various formats"""
    if value is None or pd.isna(value):
        return datetime.now().strftime("%Y-%m-%d")
    
    try:
        if isinstance(value, (datetime, pd.Timestamp)):
            return value.strftime("%Y-%m-%d")
        
        # Try various date formats
        date_formats = [
            "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y",
            "%d-%b-%Y", "%d %b %Y", "%d-%B-%Y", "%Y/%m/%d",
            "%d.%m.%Y", "%Y.%m.%d"
        ]
        
        value_str = str(value).strip()
        for fmt in date_formats:
            try:
                return datetime.strptime(value_str, fmt).strftime("%Y-%m-%d")
            except Exception:
                continue
        
        return value_str
    except Exception:
        return datetime.now().strftime("%Y-%m-%d")


def classify_by_content(row_data: Dict, voucher_type_value: str = None) -> Dict:
    """
    Classify entry based on voucher type and content analysis.
    """
    # Combine all text for analysis
    all_text = " ".join(str(v).upper() for v in row_data.values() if v and not pd.isna(v))
    
    # If voucher type column exists, use it first
    if voucher_type_value:
        vt_upper = str(voucher_type_value).upper()
        
        if any(kw in vt_upper for kw in ['SALES', 'TAX INVOICE', 'INVOICE']):
            if 'RETURN' in vt_upper or 'CN' in vt_upper:
                return {'type': 'credit_note', 'confidence': 0.95, 'collection': 'credit_notes'}
            return {'type': 'sales_invoice', 'confidence': 0.95, 'collection': 'orders'}
        
        if any(kw in vt_upper for kw in ['PURCHASE', 'BILL']):
            if 'RETURN' in vt_upper or 'DN' in vt_upper:
                return {'type': 'debit_note', 'confidence': 0.95, 'collection': 'debit_notes'}
            if 'ORDER' in vt_upper:
                return {'type': 'purchase_order', 'confidence': 0.95, 'collection': 'purchase_orders'}
            return {'type': 'purchase_bill', 'confidence': 0.95, 'collection': 'purchase_bills'}
        
        if any(kw in vt_upper for kw in ['PAYMENT', 'PAID']):
            return {'type': 'payment', 'confidence': 0.95, 'collection': 'payments'}
        
        if any(kw in vt_upper for kw in ['RECEIPT', 'RECEIVED', 'RCPT']):
            return {'type': 'receipt', 'confidence': 0.95, 'collection': 'receipts'}
        
        if any(kw in vt_upper for kw in ['JOURNAL', 'JV', 'JNL']):
            return {'type': 'journal', 'confidence': 0.95, 'collection': 'journal_vouchers'}
        
        if any(kw in vt_upper for kw in ['CONTRA']):
            return {'type': 'contra', 'confidence': 0.95, 'collection': 'contra_entries'}
        
        if any(kw in vt_upper for kw in ['CREDIT NOTE', 'CN']):
            return {'type': 'credit_note', 'confidence': 0.95, 'collection': 'credit_notes'}
        
        if any(kw in vt_upper for kw in ['DEBIT NOTE', 'DN']):
            return {'type': 'debit_note', 'confidence': 0.95, 'collection': 'debit_notes'}
    
    # Fallback to content analysis
    debit = row_data.get('debit', 0) or 0
    credit = row_data.get('credit', 0) or 0
    
    # Check keywords in all text
    if any(kw in all_text for kw in ['SALES', 'SOLD', 'CUSTOMER', 'TAX INVOICE']):
        return {'type': 'sales_invoice', 'confidence': 0.7, 'collection': 'orders'}
    
    if any(kw in all_text for kw in ['PURCHASE', 'BOUGHT', 'VENDOR', 'SUPPLIER']):
        return {'type': 'purchase_bill', 'confidence': 0.7, 'collection': 'purchase_bills'}
    
    if any(kw in all_text for kw in ['PAYMENT', 'PAID', 'NEFT', 'RTGS', 'CHEQUE']):
        return {'type': 'payment', 'confidence': 0.7, 'collection': 'payments'}
    
    if any(kw in all_text for kw in ['RECEIPT', 'RECEIVED', 'COLLECTION']):
        return {'type': 'receipt', 'confidence': 0.7, 'collection': 'receipts'}
    
    if any(kw in all_text for kw in ['RENT', 'SALARY', 'ELECTRICITY', 'EXPENSE', 'CHARGES']):
        return {'type': 'expense', 'confidence': 0.7, 'collection': 'expenses'}
    
    if any(kw in all_text for kw in ['BANK', 'INTEREST', 'BANK CHARGES']):
        return {'type': 'bank_entry', 'confidence': 0.6, 'collection': 'bank_transactions'}
    
    # Amount-based fallback
    if credit > 0 and debit == 0:
        return {'type': 'receipt', 'confidence': 0.4, 'collection': 'receipts'}
    if debit > 0 and credit == 0:
        return {'type': 'payment', 'confidence': 0.4, 'collection': 'payments'}
    
    return {'type': 'unknown', 'confidence': 0.0, 'collection': 'unclassified_entries'}


# ============ API ENDPOINTS ============

@router.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    """
    Analyze uploaded file and detect its structure automatically.
    Returns column mapping and sample data.
    """
    try:
        content = await file.read()
        filename = file.filename.lower()
        
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use CSV or Excel.")
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Analyze structure
        analysis = analyze_file_structure(df)
        
        # Add sample rows
        sample_rows = []
        for idx, row in df.head(5).iterrows():
            sample_rows.append({str(k): str(v)[:100] if not pd.isna(v) else None for k, v in row.items()})
        
        analysis['sample_rows'] = sample_rows
        analysis['filename'] = file.filename
        
        return analysis
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")


@router.post("/import")
async def smart_import(
    file: UploadFile = File(...),
    custom_mapping: Optional[str] = Form(None)  # JSON string of custom column mapping
):
    """
    Smart import that automatically detects format and classifies entries.
    Handles Tally Day Book format with header rows and merged cells.
    """
    from pymongo import MongoClient
    import json
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'startup_template')
    client = MongoClient(mongo_url)
    db = client[db_name]
    
    try:
        content = await file.read()
        filename = file.filename.lower()
        
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content), header=None)
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(content), header=None)
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use CSV or Excel.")
        
        logger.info(f"[Smart Import] File loaded with {len(df)} rows, {len(df.columns)} columns")
        
        # Find the header row by looking for common column names
        header_row = find_header_row(df)
        logger.info(f"[Smart Import] Header row detected at: {header_row}")
        
        if header_row >= 0:
            # Set proper column names from the header row
            df.columns = [str(c).strip() if pd.notna(c) else f"Col_{i}" for i, c in enumerate(df.iloc[header_row])]
            # Skip rows up to and including header
            df = df.iloc[header_row + 1:].reset_index(drop=True)
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Get column mapping (auto-detect or use custom)
        if custom_mapping:
            column_mapping = json.loads(custom_mapping)
        else:
            column_mapping = detect_tally_columns(df)
        
        logger.info(f"[Smart Import] Detected columns: {column_mapping}")
        
        # Track results
        import_batch_id = str(uuid.uuid4())[:8]
        import_timestamp = datetime.now(timezone.utc)
        
        results = {
            "total_rows": len(df),
            "imported": 0,
            "skipped_empty": 0,
            "by_type": {},
            "errors": [],
            "column_mapping_used": column_mapping
        }
        
        # Prepare batches by collection
        batches = {}
        
        for idx, row in df.iterrows():
            try:
                # Skip empty rows
                if is_empty_row(row):
                    results["skipped_empty"] += 1
                    continue
                
                # Extract data using detected mapping
                date = parse_date(extract_value(row, column_mapping, 'date'))
                debit = parse_amount(extract_value(row, column_mapping, 'debit', 0))
                credit = parse_amount(extract_value(row, column_mapping, 'credit', 0))
                
                # Skip rows with no amounts
                if debit == 0 and credit == 0:
                    # Check if there's an amount column
                    amount = parse_amount(extract_value(row, column_mapping, 'amount', 0))
                    if amount == 0:
                        results["skipped_empty"] += 1
                        continue
                else:
                    amount = debit or credit
                
                party = str(extract_value(row, column_mapping, 'party', '') or '')
                voucher_type = str(extract_value(row, column_mapping, 'voucher_type', '') or '')
                voucher_no = str(extract_value(row, column_mapping, 'voucher_no', '') or '')
                narration = str(extract_value(row, column_mapping, 'narration', '') or '')
                
                # Skip header-like rows
                if voucher_type.lower() in ['vch type', 'voucher type', 'type', '']:
                    if party.lower() in ['particulars', 'party name', 'ledger', '']:
                        results["skipped_empty"] += 1
                        continue
                
                # Classify the entry based on Tally voucher types
                row_data = {
                    'date': date, 'debit': debit, 'credit': credit,
                    'party': party, 'voucher_type': voucher_type,
                    'voucher_no': voucher_no, 'narration': narration
                }
                classification = classify_tally_voucher(row_data, voucher_type)
                
                # PRESERVE ALL RAW DATA FROM EXCEL ROW
                raw_row_data = {}
                for col in row.index:
                    val = row[col]
                    # Convert numpy types to Python native types
                    if pd.isna(val):
                        raw_row_data[str(col)] = None
                    elif isinstance(val, (np.integer, np.floating)):
                        raw_row_data[str(col)] = float(val) if isinstance(val, np.floating) else int(val)
                    else:
                        raw_row_data[str(col)] = str(val) if val is not None else None
                
                # Prepare document with raw data
                base_doc = {
                    "id": f"SI-{import_batch_id}-{idx+1}",
                    "import_batch_id": import_batch_id,
                    "source": "daybook_import",
                    "source_file": file.filename,
                    "row_number": idx + 1,
                    "date": date,
                    "imported_at": import_timestamp.isoformat(),
                    "created_at": import_timestamp.isoformat(),
                    "classification": classification,
                    "original_voucher_type": voucher_type,
                    "raw_data": raw_row_data  # PRESERVE ALL ORIGINAL DATA
                }
                
                # Build collection-specific document
                coll = classification['collection']
                entry_type = classification['type']
                
                if entry_type == 'sales_invoice':
                    doc = {
                        **base_doc,
                        "order_id": f"SI-{import_batch_id}-{idx+1}-{uuid.uuid4().hex[:4]}",
                        "order_number": voucher_no or base_doc["id"],
                        "order_date": date,
                        "customer_details": {"name": party, "email": "", "phone": ""},
                        "total_amount": credit or amount,
                        "status": "confirmed",
                        "notes": narration
                    }
                elif entry_type == 'purchase_bill':
                    doc = {
                        **base_doc,
                        "bill_id": f"PB-{import_batch_id}-{idx+1}-{uuid.uuid4().hex[:4]}",
                        "bill_number": voucher_no or base_doc["id"],
                        "bill_date": date,
                        "vendor_name": party,
                        "total_amount": debit or amount,
                        "status": "pending",
                        "notes": narration
                    }
                elif entry_type == 'payment':
                    doc = {
                        **base_doc,
                        "payment_id": voucher_no or base_doc["id"],
                        "payment_date": date,
                        "paid_to": party,
                        "amount": debit or amount,
                        "payment_mode": "Bank Transfer",
                        "narration": narration,
                        "status": "completed"
                    }
                elif entry_type == 'receipt':
                    doc = {
                        **base_doc,
                        "receipt_id": voucher_no or base_doc["id"],
                        "receipt_date": date,
                        "received_from": party,
                        "amount": credit or amount,
                        "receipt_mode": "Bank Transfer",
                        "narration": narration,
                        "status": "completed"
                    }
                elif entry_type == 'expense':
                    doc = {
                        **base_doc,
                        "expense_id": voucher_no or base_doc["id"],
                        "expense_date": date,
                        "description": narration or party,
                        "amount": debit or amount,
                        "category": "general",
                        "status": "approved"
                    }
                elif entry_type == 'journal':
                    doc = {
                        **base_doc,
                        "voucher_id": voucher_no or base_doc["id"],
                        "voucher_date": date,
                        "narration": narration or party,
                        "debit_amount": debit,
                        "credit_amount": credit,
                        "status": "posted"
                    }
                elif entry_type == 'contra':
                    doc = {
                        **base_doc,
                        "contra_id": voucher_no or base_doc["id"],
                        "contra_date": date,
                        "description": narration or party,
                        "debit_amount": debit,
                        "credit_amount": credit,
                        "status": "posted"
                    }
                elif entry_type == 'credit_note':
                    doc = {
                        **base_doc,
                        "note_id": voucher_no or base_doc["id"],
                        "note_type": "credit",
                        "note_date": date,
                        "party_name": party,
                        "amount": credit or amount,
                        "reason": narration,
                        "status": "approved"
                    }
                elif entry_type == 'debit_note':
                    doc = {
                        **base_doc,
                        "note_id": voucher_no or base_doc["id"],
                        "note_type": "debit",
                        "note_date": date,
                        "party_name": party,
                        "amount": debit or amount,
                        "reason": narration,
                        "status": "approved"
                    }
                elif entry_type == 'bank_entry':
                    doc = {
                        **base_doc,
                        "transaction_id": voucher_no or base_doc["id"],
                        "transaction_date": date,
                        "description": narration or party,
                        "debit": debit,
                        "credit": credit,
                        "reconciled": False
                    }
                else:
                    # Unclassified - store all original data
                    doc = {
                        **base_doc,
                        "party": party,
                        "voucher_type_raw": voucher_type,
                        "voucher_no": voucher_no,
                        "narration": narration,
                        "debit": debit,
                        "credit": credit,
                        "amount": amount
                    }
                
                # Add to batch
                if coll not in batches:
                    batches[coll] = []
                batches[coll].append(doc)
                
                results["by_type"][entry_type] = results["by_type"].get(entry_type, 0) + 1
                
            except Exception as row_error:
                if len(results["errors"]) < 20:
                    results["errors"].append(f"Row {idx+1}: {str(row_error)[:100]}")
        
        # Bulk insert
        for coll_name, docs in batches.items():
            if docs:
                try:
                    db[coll_name].insert_many(docs, ordered=False)
                    results["imported"] += len(docs)
                    logger.info(f"[Smart Import] Inserted {len(docs)} into {coll_name}")
                except Exception as e:
                    logger.error(f"[Smart Import] Error inserting into {coll_name}: {e}")
                    results["errors"].append(f"Batch insert {coll_name}: {str(e)[:100]}")
        
        # Log import
        db.daybook_import_logs.insert_one({
            "id": import_batch_id,
            "filename": file.filename,
            "imported_at": import_timestamp.isoformat(),
            "results": results,
            "column_mapping": column_mapping
        })
        
        return {
            "status": "success",
            "message": f"Imported {results['imported']} entries",
            "import_batch_id": import_batch_id,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Import error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


def find_header_row(df: pd.DataFrame) -> int:
    """Find the row containing column headers in Tally format"""
    header_keywords = ['date', 'particulars', 'vch type', 'voucher type', 'debit', 'credit', 'vch no', 'amount']
    
    for idx in range(min(20, len(df))):  # Check first 20 rows
        row_text = ' '.join(str(v).lower() for v in df.iloc[idx] if pd.notna(v))
        matches = sum(1 for kw in header_keywords if kw in row_text)
        if matches >= 3:  # At least 3 header keywords found
            return idx
    
    return -1  # No header found, use first row


def detect_tally_columns(df: pd.DataFrame) -> Dict[str, str]:
    """Detect column mapping for Tally Day Book format"""
    mapping = {}
    
    for col in df.columns:
        col_lower = str(col).lower().strip()
        
        # Date column
        if any(x in col_lower for x in ['date', 'dt']):
            if 'date' not in mapping:
                mapping['date'] = col
        
        # Particulars / Party column
        elif any(x in col_lower for x in ['particulars', 'party', 'ledger', 'name', 'account']):
            if 'party' not in mapping:
                mapping['party'] = col
        
        # Voucher Type
        elif any(x in col_lower for x in ['vch type', 'voucher type', 'type', 'vch ty']):
            mapping['voucher_type'] = col
        
        # Voucher Number
        elif any(x in col_lower for x in ['vch no', 'voucher no', 'no.', 'number', 'ref']):
            if 'voucher_no' not in mapping:
                mapping['voucher_no'] = col
        
        # Debit
        elif any(x in col_lower for x in ['debit', 'dr']):
            mapping['debit'] = col
        
        # Credit
        elif any(x in col_lower for x in ['credit', 'cr']):
            mapping['credit'] = col
        
        # Narration
        elif any(x in col_lower for x in ['narration', 'description', 'remarks']):
            mapping['narration'] = col
    
    return mapping


def is_empty_row(row: pd.Series) -> bool:
    """Check if row is essentially empty or a sub-header"""
    non_null_count = sum(1 for v in row if pd.notna(v) and str(v).strip() and str(v).strip() != 'nan')
    return non_null_count < 2


def classify_tally_voucher(row_data: Dict, voucher_type: str) -> Dict:
    """
    Classify entry based on Tally voucher type.
    Handles all standard Tally voucher types.
    """
    vt_upper = str(voucher_type).upper().strip()
    
    # Direct mapping of Tally voucher types
    tally_type_mapping = {
        # Sales related
        'SALES': ('sales_invoice', 'orders'),
        'SALE': ('sales_invoice', 'orders'),
        'TAX INVOICE': ('sales_invoice', 'orders'),
        'SALES INVOICE': ('sales_invoice', 'orders'),
        'GST SALES': ('sales_invoice', 'orders'),
        
        # Purchase related
        'PURCHASE': ('purchase_bill', 'purchase_bills'),
        'PURCHASE INVOICE': ('purchase_bill', 'purchase_bills'),
        'GST PURCHASE': ('purchase_bill', 'purchase_bills'),
        'PURCHASE BILL': ('purchase_bill', 'purchase_bills'),
        
        # Payment related
        'PAYMENT': ('payment', 'payments'),
        'BANK PAYMENT': ('payment', 'payments'),
        'CASH PAYMENT': ('payment', 'payments'),
        
        # Receipt related
        'RECEIPT': ('receipt', 'receipts'),
        'BANK RECEIPT': ('receipt', 'receipts'),
        'CASH RECEIPT': ('receipt', 'receipts'),
        
        # Journal related
        'JOURNAL': ('journal', 'journal_vouchers'),
        'JOURNAL VOUCHER': ('journal', 'journal_vouchers'),
        'JV': ('journal', 'journal_vouchers'),
        'JNL': ('journal', 'journal_vouchers'),
        
        # Contra related
        'CONTRA': ('contra', 'contra_entries'),
        'CONTRA ENTRY': ('contra', 'contra_entries'),
        
        # Credit/Debit Notes
        'CREDIT NOTE': ('credit_note', 'credit_notes'),
        'CN': ('credit_note', 'credit_notes'),
        'SALES RETURN': ('credit_note', 'credit_notes'),
        'DEBIT NOTE': ('debit_note', 'debit_notes'),
        'DN': ('debit_note', 'debit_notes'),
        'PURCHASE RETURN': ('debit_note', 'debit_notes'),
        
        # Stock related (treat as journal for now)
        'STOCK JOURNAL': ('journal', 'journal_vouchers'),
        'MANUFACTURING': ('journal', 'journal_vouchers'),
        'PHYSICAL STOCK': ('journal', 'journal_vouchers'),
        
        # Memo/Order (not actual transactions)
        'MEMO': ('journal', 'journal_vouchers'),
        'MEMORANDUM': ('journal', 'journal_vouchers'),
        'PURCHASE ORDER': ('purchase_order', 'purchase_orders'),
        'SALES ORDER': ('sales_order', 'sales_orders'),
        
        # Bank related
        'BANK': ('bank_entry', 'bank_transactions'),
        'BANK STATEMENT': ('bank_entry', 'bank_transactions'),
    }
    
    # Check direct mapping first
    for key, (entry_type, collection) in tally_type_mapping.items():
        if key in vt_upper or vt_upper == key:
            return {
                'type': entry_type,
                'confidence': 0.95,
                'collection': collection,
                'matched_on': f'voucher_type:{voucher_type}'
            }
    
    # Partial match for variations
    if 'SALES' in vt_upper and 'RETURN' not in vt_upper and 'ORDER' not in vt_upper:
        return {'type': 'sales_invoice', 'confidence': 0.85, 'collection': 'orders'}
    
    if 'PURCHASE' in vt_upper and 'RETURN' not in vt_upper and 'ORDER' not in vt_upper:
        return {'type': 'purchase_bill', 'confidence': 0.85, 'collection': 'purchase_bills'}
    
    if 'PAYMENT' in vt_upper or 'PAID' in vt_upper:
        return {'type': 'payment', 'confidence': 0.85, 'collection': 'payments'}
    
    if 'RECEIPT' in vt_upper or 'RECEIVED' in vt_upper:
        return {'type': 'receipt', 'confidence': 0.85, 'collection': 'receipts'}
    
    if 'JOURNAL' in vt_upper or 'JV' in vt_upper:
        return {'type': 'journal', 'confidence': 0.85, 'collection': 'journal_vouchers'}
    
    if 'CONTRA' in vt_upper:
        return {'type': 'contra', 'confidence': 0.85, 'collection': 'contra_entries'}
    
    # Content-based fallback if voucher type doesn't match
    debit = row_data.get('debit', 0) or 0
    credit = row_data.get('credit', 0) or 0
    party = str(row_data.get('party', '')).upper()
    
    # Check party name for clues
    if any(kw in party for kw in ['SALES', 'CUSTOMER', 'SOLD']):
        return {'type': 'sales_invoice', 'confidence': 0.5, 'collection': 'orders'}
    
    if any(kw in party for kw in ['PURCHASE', 'VENDOR', 'SUPPLIER']):
        return {'type': 'purchase_bill', 'confidence': 0.5, 'collection': 'purchase_bills'}
    
    if any(kw in party for kw in ['BANK', 'HDFC', 'SBI', 'ICICI', 'AXIS', 'KOTAK']):
        return {'type': 'bank_entry', 'confidence': 0.6, 'collection': 'bank_transactions'}
    
    if any(kw in party for kw in ['RENT', 'SALARY', 'ELECTRICITY', 'EXPENSE']):
        return {'type': 'expense', 'confidence': 0.6, 'collection': 'expenses'}
    
    # If we have a voucher type but couldn't match it, still classify based on amount
    if vt_upper and vt_upper not in ['', 'NAN', 'NONE']:
        # Unknown voucher type but has data - store as journal
        if debit > 0 or credit > 0:
            return {'type': 'journal', 'confidence': 0.4, 'collection': 'journal_vouchers', 'matched_on': f'fallback_journal:{voucher_type}'}
    
    return {'type': 'unknown', 'confidence': 0.0, 'collection': 'unclassified_entries'}


@router.get("/template")
async def download_template():
    """Download a sample template showing supported formats"""
    template_data = {
        "Date": ["15-02-2026", "15-02-2026", "16-02-2026", "16-02-2026"],
        "Voucher Type": ["Sales", "Purchase", "Payment", "Receipt"],
        "Voucher No": ["INV-001", "BILL-001", "PMT-001", "RCV-001"],
        "Party Name": ["Customer ABC", "Vendor XYZ", "Rent Payment", "Customer DEF"],
        "Debit": [0, 50000, 25000, 0],
        "Credit": [118000, 0, 0, 30000],
        "Narration": ["Sale of goods", "Purchase of inventory", "Office rent", "Payment received"]
    }
    
    df = pd.DataFrame(template_data)
    template_path = f"{UPLOAD_DIR}/smart_daybook_template.xlsx"
    df.to_excel(template_path, index=False)
    
    return FileResponse(
        template_path,
        filename="smart_daybook_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
