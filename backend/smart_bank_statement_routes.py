"""
Smart Bank Statement Import - Enhanced with PDF support and auto-categorization
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from database import get_db
import uuid
import logging
import csv
import io
import re
import os

router = APIRouter(prefix="/bank-statement", tags=["Bank Statement Import"])
logger = logging.getLogger(__name__)

# ============ SMART CATEGORIZATION RULES ============

CATEGORIZATION_RULES = {
    "payments": {
        "keywords": ["NEFT", "RTGS", "IMPS", "UPI", "PAYMENT", "TRF", "TRANSFER", "PAY"],
        "patterns": [r"TO\s+\w+", r"NEFT[-/]\w+", r"UPI[-/]\w+"]
    },
    "receipts": {
        "keywords": ["RECEIVED", "RECEIPT", "COLLECTION", "FROM", "BY", "CREDIT"],
        "patterns": [r"FROM\s+\w+", r"RCVD\s+"]
    },
    "expenses": {
        "keywords": ["ELECTRICITY", "TELEPHONE", "RENT", "SALARY", "WAGES", "GST", "TAX", 
                    "INSURANCE", "MAINTENANCE", "OFFICE", "PETROL", "FUEL", "TRAVEL",
                    "MOBILE", "INTERNET", "SUBSCRIPTION", "CHARGES", "FEE"],
        "sub_categories": {
            "utilities": ["ELECTRICITY", "TELEPHONE", "MOBILE", "INTERNET", "GAS", "WATER"],
            "rent": ["RENT", "LEASE"],
            "salary": ["SALARY", "WAGES", "PAYROLL"],
            "taxes": ["GST", "TAX", "TDS", "ADVANCE TAX"],
            "bank_charges": ["CHARGES", "FEE", "COMMISSION", "INTEREST"],
            "travel": ["TRAVEL", "PETROL", "FUEL", "DIESEL"],
            "office": ["OFFICE", "STATIONERY", "SUPPLIES"]
        }
    },
    "vendor_payments": {
        "keywords": ["VENDOR", "SUPPLIER", "PURCHASE", "BOSCH", "SIEMENS", "HINDWARE"],
        "patterns": [r"INV[-/]?\d+", r"BILL[-/]?\d+", r"PO[-/]?\d+"]
    },
    "customer_receipts": {
        "keywords": ["CUSTOMER", "SALES", "ORDER", "INV"],
        "patterns": [r"ORD[-/]?\d+", r"AD\d{12}"]
    },
    "loans": {
        "keywords": ["LOAN", "EMI", "INSTALLMENT", "PRINCIPAL", "INTEREST"],
        "patterns": [r"EMI\s+\d+", r"LOAN\s+A/C"]
    },
    "investments": {
        "keywords": ["FD", "FIXED DEPOSIT", "MUTUAL FUND", "MF", "INVESTMENT", "DIVIDEND"],
        "patterns": []
    }
}


def categorize_transaction(description: str, amount: float, is_credit: bool) -> Dict[str, Any]:
    """Smart categorization of bank transaction"""
    desc_upper = description.upper()
    
    result = {
        "category": "uncategorized",
        "sub_category": None,
        "entry_type": "receipt" if is_credit else "payment",
        "suggested_ledger": None,
        "confidence": 0.0,
        "matched_keywords": []
    }
    
    # Check each category
    for category, rules in CATEGORIZATION_RULES.items():
        keywords = rules.get("keywords", [])
        patterns = rules.get("patterns", [])
        
        # Check keywords
        matched = [kw for kw in keywords if kw in desc_upper]
        
        # Check patterns
        for pattern in patterns:
            if re.search(pattern, desc_upper):
                matched.append(f"pattern:{pattern}")
        
        if matched:
            confidence = len(matched) / (len(keywords) + len(patterns)) if keywords or patterns else 0.5
            
            if confidence > result["confidence"]:
                result["category"] = category
                result["confidence"] = min(confidence * 2, 1.0)  # Boost confidence
                result["matched_keywords"] = matched
                
                # Check sub-categories for expenses
                if category == "expenses" and "sub_categories" in rules:
                    for sub_cat, sub_keywords in rules["sub_categories"].items():
                        if any(sk in desc_upper for sk in sub_keywords):
                            result["sub_category"] = sub_cat
                            break
    
    # Set entry type based on category and credit/debit
    if is_credit:
        if result["category"] in ["customer_receipts", "receipts"]:
            result["entry_type"] = "receipt"
        elif result["category"] == "loans":
            result["entry_type"] = "loan_received"
        else:
            result["entry_type"] = "receipt"
    else:
        if result["category"] in ["vendor_payments", "payments"]:
            result["entry_type"] = "payment"
        elif result["category"] == "expenses":
            result["entry_type"] = "expense"
        elif result["category"] == "loans":
            result["entry_type"] = "loan_payment"
        else:
            result["entry_type"] = "payment"
    
    # Suggest ledger based on category
    ledger_map = {
        "vendor_payments": "Sundry Creditors",
        "customer_receipts": "Sundry Debtors",
        "expenses": "Operating Expenses",
        "payments": "Bank Payments",
        "receipts": "Bank Receipts",
        "loans": "Loan Account",
        "investments": "Investments"
    }
    result["suggested_ledger"] = ledger_map.get(result["category"], "Suspense Account")
    
    return result


async def parse_pdf_statement(content: bytes, db) -> List[Dict]:
    """Parse PDF bank statement using AI"""
    import json
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY not configured")

        # Save PDF temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            import PyPDF2

            with open(tmp_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"

            parse_prompt = f"""Extract bank transactions from this text extracted from a bank statement:

{text[:8000]}

Return ONLY a JSON array with this structure for each transaction:
[{{"date": "DD-MM-YYYY", "description": "narration", "reference": "ref", "debit": 0, "credit": 0, "balance": 0}}]

Rules:
- date should be in DD-MM-YYYY format
- debit/credit should be numeric (no commas)
- Return empty array [] if no transactions found
"""

            chat = LlmChat(
                api_key=api_key,
                session_id=f"bank-stmt-{uuid.uuid4()}",
                system_message="You are a precise financial data extraction assistant."
            ).with_model("gemini", "gemini-2.5-flash")

            response = await chat.send_message(UserMessage(text=parse_prompt))

            # Clean and parse JSON
            json_str = response.strip()
            if json_str.startswith("```"):
                json_str = json_str.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
            json_str = json_str.strip()

            transactions = json.loads(json_str)
            return transactions

        except ImportError:
            logger.warning("PyPDF2 not installed, cannot parse PDF")
            raise HTTPException(status_code=400, detail="PDF parsing requires PyPDF2. Please upload CSV format or install PyPDF2.")
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return []


def _num(value) -> float:
    try:
        return float(str(value).replace(",", "").replace("₹", "").strip() or 0)
    except (ValueError, TypeError):
        return 0.0


def parse_csv_statement(content: bytes) -> List[Dict]:
    """Parse a CSV bank statement with flexible header matching"""
    text = content.decode("utf-8-sig", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return []

    def find_col(*candidates):
        for field in reader.fieldnames:
            key = (field or "").strip().lower()
            for cand in candidates:
                if re.search(rf"\b{re.escape(cand)}\b", key):
                    return field
        return None

    date_col = find_col("date")
    desc_col = find_col("description", "narration", "particular", "details", "remarks")
    ref_col = find_col("reference", "ref no", "cheque", "chq", "utr", "txn id")
    debit_col = find_col("debit", "withdrawal", "dr")
    credit_col = find_col("credit", "deposit", "cr")
    balance_col = find_col("balance")
    amount_col = find_col("amount")
    type_col = find_col("type", "dr/cr")

    transactions = []
    for row in reader:
        if not row or not date_col or not (row.get(date_col) or "").strip():
            continue
        debit = _num(row.get(debit_col)) if debit_col else 0.0
        credit = _num(row.get(credit_col)) if credit_col else 0.0
        if not debit_col and not credit_col and amount_col:
            amount = _num(row.get(amount_col))
            txn_type = (row.get(type_col) or "").strip().lower() if type_col else ""
            if txn_type.startswith("d") or amount < 0:
                debit = abs(amount)
            else:
                credit = abs(amount)
        if debit == 0 and credit == 0:
            continue
        transactions.append({
            "date": (row.get(date_col) or "").strip(),
            "description": (row.get(desc_col) or "").strip() if desc_col else "",
            "reference": (row.get(ref_col) or "").strip() if ref_col else "",
            "debit": debit,
            "credit": credit,
            "balance": _num(row.get(balance_col)) if balance_col else 0.0,
        })
    return transactions


@router.post("/upload")
async def upload_bank_statement(
    bank_account_id: str = Form(...),
    file: UploadFile = File(...),
    auto_categorize: bool = Form(default=True),
    auto_sync: bool = Form(default=False),
    db = Depends(get_db)
):
    """
    Upload bank statement (CSV or PDF) with smart categorization
    
    - auto_categorize: Automatically categorize transactions
    - auto_sync: Automatically create accounting entries (payments, receipts, expenses)
    """
    try:
        # Verify bank account exists
        account = await db.bank_accounts.find_one({"id": bank_account_id})
        if not account:
            raise HTTPException(status_code=404, detail="Bank account not found")
        
        content = await file.read()
        filename = file.filename.lower()
        
        # Parse based on file type
        if filename.endswith('.pdf'):
            transactions = await parse_pdf_statement(content, db)
        elif filename.endswith('.csv'):
            transactions = parse_csv_statement(content)
        else:
            raise HTTPException(status_code=400, detail="Please upload CSV or PDF file")
        
        if not transactions:
            return {
                "status": "warning",
                "message": "No transactions found in the file",
                "imported": 0,
                "skipped": 0
            }
        
        # Process transactions
        imported = 0
        skipped = 0
        categorized = 0
        synced = 0
        now = datetime.now(timezone.utc).isoformat()
        
        results = []
        
        for txn in transactions:
            try:
                date_str = txn.get("date", "")
                description = txn.get("description", "")
                debit = float(txn.get("debit", 0) or 0)
                credit = float(txn.get("credit", 0) or 0)
                reference = txn.get("reference", "")
                balance = float(txn.get("balance", 0) or 0)
                
                if not date_str or not description:
                    skipped += 1
                    continue
                
                # Check for duplicate
                existing = await db.bank_transactions.find_one({
                    "bank_account_id": bank_account_id,
                    "transaction_date": date_str,
                    "description": description,
                    "debit_amount": debit,
                    "credit_amount": credit
                })
                
                if existing:
                    skipped += 1
                    continue
                
                # Categorize transaction
                category_info = {}
                if auto_categorize:
                    category_info = categorize_transaction(description, credit or debit, credit > 0)
                    categorized += 1
                
                txn_id = str(uuid.uuid4())
                
                bank_txn = {
                    "id": txn_id,
                    "bank_account_id": bank_account_id,
                    "transaction_date": date_str,
                    "description": description,
                    "reference_number": reference,
                    "debit_amount": debit,
                    "credit_amount": credit,
                    "closing_balance": balance,
                    "transaction_type": "credit" if credit > 0 else "debit",
                    "category": category_info.get("category", "uncategorized"),
                    "sub_category": category_info.get("sub_category"),
                    "entry_type": category_info.get("entry_type", "unknown"),
                    "suggested_ledger": category_info.get("suggested_ledger"),
                    "confidence": category_info.get("confidence", 0),
                    "matched_keywords": category_info.get("matched_keywords", []),
                    "is_reconciled": False,
                    "is_synced": False,
                    "synced_entry_id": None,
                    "matched_ledger_id": None,
                    "created_at": now,
                    "imported": True
                }
                
                await db.bank_transactions.insert_one(bank_txn)
                imported += 1
                
                # Auto-sync to accounting entries if enabled
                if auto_sync and category_info.get("confidence", 0) >= 0.5:
                    sync_result = await sync_transaction_to_accounting(db, bank_txn, account)
                    if sync_result:
                        synced += 1
                        await db.bank_transactions.update_one(
                            {"id": txn_id},
                            {"$set": {"is_synced": True, "synced_entry_id": sync_result}}
                        )
                
                results.append({
                    "date": date_str,
                    "description": description[:50],
                    "amount": credit or debit,
                    "type": "credit" if credit > 0 else "debit",
                    "category": category_info.get("category", "uncategorized"),
                    "entry_type": category_info.get("entry_type", "unknown"),
                    "synced": auto_sync and category_info.get("confidence", 0) >= 0.5
                })
                
            except Exception as e:
                logger.warning(f"Error processing transaction: {e}")
                skipped += 1
        
        # Update bank account balance
        if imported > 0 and transactions[-1].get("balance"):
            await db.bank_accounts.update_one(
                {"id": bank_account_id},
                {"$set": {
                    "current_balance": transactions[-1].get("balance"),
                    "updated_at": now
                }}
            )
        
        return {
            "status": "success",
            "message": f"Imported {imported} transactions",
            "imported": imported,
            "skipped": skipped,
            "categorized": categorized,
            "synced": synced,
            "transactions": results[:20]  # Return first 20 for preview
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bank statement upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def sync_transaction_to_accounting(db, bank_txn: Dict, bank_account: Dict) -> Optional[str]:
    """Create accounting entry from bank transaction"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        entry_id = str(uuid.uuid4())
        
        entry_type = bank_txn.get("entry_type", "unknown")
        category = bank_txn.get("category", "uncategorized")
        amount = bank_txn.get("credit_amount") or bank_txn.get("debit_amount")
        
        # Create appropriate entry based on type
        if entry_type == "payment" or entry_type == "expense":
            # Create expense/payment entry
            entry = {
                "id": entry_id,
                "entry_type": "payment",
                "date": bank_txn.get("transaction_date"),
                "amount": amount,
                "description": bank_txn.get("description"),
                "reference": bank_txn.get("reference_number"),
                "category": category,
                "sub_category": bank_txn.get("sub_category"),
                "bank_account_id": bank_txn.get("bank_account_id"),
                "bank_transaction_id": bank_txn.get("id"),
                "payment_mode": "bank_transfer",
                "status": "completed",
                "created_at": now,
                "auto_synced": True
            }
            await db.payments.insert_one(entry)
            
            # Also create expense entry if it's an expense
            if entry_type == "expense":
                expense_entry = {
                    "id": str(uuid.uuid4()),
                    "date": bank_txn.get("transaction_date"),
                    "amount": amount,
                    "category": bank_txn.get("sub_category") or category,
                    "description": bank_txn.get("description"),
                    "reference": bank_txn.get("reference_number"),
                    "payment_id": entry_id,
                    "bank_transaction_id": bank_txn.get("id"),
                    "created_at": now,
                    "auto_synced": True
                }
                await db.expenses.insert_one(expense_entry)
            
        elif entry_type == "receipt":
            # Create receipt entry
            entry = {
                "id": entry_id,
                "entry_type": "receipt",
                "date": bank_txn.get("transaction_date"),
                "amount": amount,
                "description": bank_txn.get("description"),
                "reference": bank_txn.get("reference_number"),
                "category": category,
                "bank_account_id": bank_txn.get("bank_account_id"),
                "bank_transaction_id": bank_txn.get("id"),
                "payment_mode": "bank_transfer",
                "status": "completed",
                "created_at": now,
                "auto_synced": True
            }
            await db.receipts.insert_one(entry)
        
        else:
            # Create general journal entry
            entry = {
                "id": entry_id,
                "voucher_type": "journal",
                "date": bank_txn.get("transaction_date"),
                "narration": bank_txn.get("description"),
                "reference": bank_txn.get("reference_number"),
                "entries": [
                    {
                        "ledger": bank_account.get("name"),
                        "debit": bank_txn.get("debit_amount", 0),
                        "credit": bank_txn.get("credit_amount", 0)
                    },
                    {
                        "ledger": bank_txn.get("suggested_ledger", "Suspense Account"),
                        "debit": bank_txn.get("credit_amount", 0),
                        "credit": bank_txn.get("debit_amount", 0)
                    }
                ],
                "bank_transaction_id": bank_txn.get("id"),
                "created_at": now,
                "auto_synced": True
            }
            await db.journal_vouchers.insert_one(entry)
        
        return entry_id
        
    except Exception as e:
        logger.error(f"Sync to accounting failed: {e}")
        return None


@router.get("/transactions/{bank_account_id}")
async def get_imported_transactions(
    bank_account_id: str,
    category: Optional[str] = None,
    synced: Optional[bool] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get imported bank transactions with filters"""
    try:
        query = {"bank_account_id": bank_account_id}
        
        if category:
            query["category"] = category
        if synced is not None:
            query["is_synced"] = synced
        if from_date:
            query["transaction_date"] = {"$gte": from_date}
        if to_date:
            if "transaction_date" in query:
                query["transaction_date"]["$lte"] = to_date
            else:
                query["transaction_date"] = {"$lte": to_date}
        
        skip = (page - 1) * limit
        
        transactions = await db.bank_transactions.find(
            query,
            {"_id": 0}
        ).sort("transaction_date", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.bank_transactions.count_documents(query)
        
        # Get category summary
        summary_pipeline = [
            {"$match": {"bank_account_id": bank_account_id}},
            {"$group": {
                "_id": "$category",
                "count": {"$sum": 1},
                "total_debit": {"$sum": "$debit_amount"},
                "total_credit": {"$sum": "$credit_amount"}
            }}
        ]
        category_summary = await db.bank_transactions.aggregate(summary_pipeline).to_list(None)
        
        return {
            "status": "success",
            "transactions": transactions,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit,
            "category_summary": category_summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-all/{bank_account_id}")
async def sync_all_transactions(
    bank_account_id: str,
    min_confidence: float = 0.5,
    db = Depends(get_db)
):
    """Sync all unsynced transactions to accounting"""
    try:
        account = await db.bank_accounts.find_one({"id": bank_account_id})
        if not account:
            raise HTTPException(status_code=404, detail="Bank account not found")
        
        # Get unsynced transactions with sufficient confidence
        transactions = await db.bank_transactions.find({
            "bank_account_id": bank_account_id,
            "is_synced": False,
            "confidence": {"$gte": min_confidence}
        }).to_list(None)
        
        synced = 0
        failed = 0
        
        for txn in transactions:
            result = await sync_transaction_to_accounting(db, txn, account)
            if result:
                await db.bank_transactions.update_one(
                    {"id": txn["id"]},
                    {"$set": {"is_synced": True, "synced_entry_id": result}}
                )
                synced += 1
            else:
                failed += 1
        
        return {
            "status": "success",
            "message": f"Synced {synced} transactions",
            "synced": synced,
            "failed": failed,
            "remaining": await db.bank_transactions.count_documents({
                "bank_account_id": bank_account_id,
                "is_synced": False
            })
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/recategorize/{transaction_id}")
async def recategorize_transaction(
    transaction_id: str,
    category: str,
    sub_category: Optional[str] = None,
    entry_type: str = "payment",
    db = Depends(get_db)
):
    """Manually recategorize a transaction"""
    try:
        result = await db.bank_transactions.update_one(
            {"id": transaction_id},
            {"$set": {
                "category": category,
                "sub_category": sub_category,
                "entry_type": entry_type,
                "confidence": 1.0,  # Manual = 100% confidence
                "manually_categorized": True
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return {"status": "success", "message": "Transaction recategorized"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
