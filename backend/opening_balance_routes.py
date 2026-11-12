"""
Opening Balance & Balance Sheet Management
- Import previous year balance sheet
- Set opening balances for all accounts
- AI CA Agent analysis of balance sheet
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from database import get_db
import pandas as pd
import io
import os
import uuid
import logging

router = APIRouter(prefix="/opening-balance", tags=["Opening Balance Management"])
logger = logging.getLogger(__name__)

UPLOAD_DIR = "/app/backend/uploads/balance_sheets"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Account categories for balance sheet
ACCOUNT_CATEGORIES = {
    "assets": {
        "current_assets": [
            "Cash in Hand", "Cash at Bank", "Sundry Debtors", "Stock in Trade",
            "Accounts Receivable", "Inventory", "Prepaid Expenses", "Short Term Investments"
        ],
        "fixed_assets": [
            "Land", "Building", "Plant & Machinery", "Furniture & Fixtures",
            "Vehicles", "Computer & Equipment", "Intangible Assets"
        ],
        "investments": [
            "Long Term Investments", "Shares", "Bonds", "Mutual Funds"
        ]
    },
    "liabilities": {
        "current_liabilities": [
            "Sundry Creditors", "Accounts Payable", "Short Term Loans",
            "Outstanding Expenses", "Advance from Customers", "Provisions"
        ],
        "long_term_liabilities": [
            "Long Term Loans", "Bank Loans", "Secured Loans", "Unsecured Loans",
            "Deferred Tax Liability"
        ]
    },
    "equity": {
        "capital": [
            "Share Capital", "Partners Capital", "Proprietor Capital",
            "Reserves & Surplus", "Retained Earnings", "General Reserve"
        ]
    }
}


def get_sync_db():
    """Get synchronous MongoDB connection"""
    from pymongo import MongoClient
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'startup_template')
    client = MongoClient(mongo_url)
    return client[db_name]


@router.get("/template")
async def download_balance_sheet_template():
    """Download template for balance sheet / opening balance import"""
    template_data = {
        "Account Name": [
            "Cash in Hand", "Cash at Bank - SBI", "Cash at Bank - HDFC",
            "Sundry Debtors", "Stock in Trade", "Furniture & Fixtures",
            "Computer & Equipment", "Sundry Creditors", "Short Term Loans",
            "Capital Account", "Reserves & Surplus", "Profit & Loss A/c"
        ],
        "Account Type": [
            "Asset", "Asset", "Asset", "Asset", "Asset", "Asset",
            "Asset", "Liability", "Liability", "Equity", "Equity", "Equity"
        ],
        "Sub Category": [
            "Current Asset", "Current Asset", "Current Asset",
            "Current Asset", "Current Asset", "Fixed Asset",
            "Fixed Asset", "Current Liability", "Current Liability",
            "Capital", "Capital", "Capital"
        ],
        "Debit Balance": [
            50000, 250000, 150000, 500000, 800000, 100000, 75000, 0, 0, 0, 0, 0
        ],
        "Credit Balance": [
            0, 0, 0, 0, 0, 0, 0, 300000, 200000, 500000, 200000, 725000
        ],
        "As On Date": [
            "31-03-2025", "31-03-2025", "31-03-2025", "31-03-2025",
            "31-03-2025", "31-03-2025", "31-03-2025", "31-03-2025",
            "31-03-2025", "31-03-2025", "31-03-2025", "31-03-2025"
        ],
        "Remarks": [
            "Petty Cash", "Main Operating Account", "Savings Account",
            "Customer Outstanding", "Closing Stock", "Office Furniture",
            "Laptops & Printers", "Vendor Outstanding", "Working Capital Loan",
            "Owner's Capital", "General Reserve", "Previous Year P&L"
        ]
    }
    
    df = pd.DataFrame(template_data)
    template_path = f"{UPLOAD_DIR}/opening_balance_template.xlsx"
    df.to_excel(template_path, index=False)
    
    return FileResponse(
        template_path,
        filename="opening_balance_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.post("/import")
async def import_opening_balances(
    file: UploadFile = File(...),
    financial_year: str = Form(...),  # e.g., "2025-26"
    as_on_date: str = Form(...)  # e.g., "2025-04-01"
):
    """
    Import opening balances from balance sheet.
    Creates/updates ledger accounts with opening balances.
    """
    db = get_sync_db()
    
    try:
        content = await file.read()
        filename = file.filename.lower()
        
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Detect columns
        col_mapping = detect_balance_columns(df)
        
        results = {
            "total_rows": len(df),
            "accounts_created": 0,
            "accounts_updated": 0,
            "errors": [],
            "total_debit": 0,
            "total_credit": 0,
            "balance_check": "pending"
        }
        
        import_batch_id = str(uuid.uuid4())[:8]
        import_timestamp = datetime.now(timezone.utc)
        
        for idx, row in df.iterrows():
            try:
                account_name = str(row.get(col_mapping.get('name', ''), '')).strip()
                if not account_name or account_name == 'nan':
                    continue
                
                debit = parse_amount(row.get(col_mapping.get('debit', ''), 0))
                credit = parse_amount(row.get(col_mapping.get('credit', ''), 0))
                account_type = str(row.get(col_mapping.get('type', ''), 'Asset')).strip()
                sub_category = str(row.get(col_mapping.get('sub_category', ''), '')).strip()
                remarks = str(row.get(col_mapping.get('remarks', ''), '')).strip()
                
                results["total_debit"] += debit
                results["total_credit"] += credit
                
                # Determine balance type
                if debit > credit:
                    opening_balance = debit - credit
                    balance_type = "debit"
                else:
                    opening_balance = credit - debit
                    balance_type = "credit"
                
                # Check if account exists
                existing = db.opening_balances.find_one({
                    "account_name": account_name,
                    "financial_year": financial_year
                })
                
                account_doc = {
                    "account_name": account_name,
                    "account_type": account_type.lower(),
                    "sub_category": sub_category,
                    "debit_balance": debit,
                    "credit_balance": credit,
                    "net_balance": opening_balance,
                    "balance_type": balance_type,
                    "financial_year": financial_year,
                    "as_on_date": as_on_date,
                    "remarks": remarks,
                    "import_batch_id": import_batch_id,
                    "updated_at": import_timestamp.isoformat()
                }
                
                if existing:
                    db.opening_balances.update_one(
                        {"_id": existing["_id"]},
                        {"$set": account_doc}
                    )
                    results["accounts_updated"] += 1
                else:
                    account_doc["id"] = f"OB-{import_batch_id}-{idx+1}"
                    account_doc["created_at"] = import_timestamp.isoformat()
                    db.opening_balances.insert_one(account_doc)
                    results["accounts_created"] += 1
                
            except Exception as e:
                if len(results["errors"]) < 10:
                    results["errors"].append(f"Row {idx+1}: {str(e)[:100]}")
        
        # Check if balance sheet balances
        diff = abs(results["total_debit"] - results["total_credit"])
        if diff < 1:  # Allow ₹1 tolerance
            results["balance_check"] = "balanced"
        else:
            results["balance_check"] = f"difference of ₹{diff:,.2f}"
        
        # Store import log
        db.opening_balance_imports.insert_one({
            "id": import_batch_id,
            "filename": file.filename,
            "financial_year": financial_year,
            "as_on_date": as_on_date,
            "imported_at": import_timestamp.isoformat(),
            "results": results
        })
        
        return {
            "status": "success",
            "message": f"Imported {results['accounts_created']} new accounts, updated {results['accounts_updated']}",
            "import_batch_id": import_batch_id,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Import error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def detect_balance_columns(df: pd.DataFrame) -> Dict[str, str]:
    """Auto-detect column mapping for balance sheet"""
    mapping = {}
    
    for col in df.columns:
        col_lower = col.lower()
        
        if any(x in col_lower for x in ['account', 'name', 'ledger', 'particular']):
            if 'name' not in mapping:
                mapping['name'] = col
        elif any(x in col_lower for x in ['debit', 'dr']):
            mapping['debit'] = col
        elif any(x in col_lower for x in ['credit', 'cr']):
            mapping['credit'] = col
        elif any(x in col_lower for x in ['type', 'category', 'group']):
            if 'sub' in col_lower:
                mapping['sub_category'] = col
            else:
                mapping['type'] = col
        elif any(x in col_lower for x in ['remark', 'note', 'description']):
            mapping['remarks'] = col
    
    return mapping


def parse_amount(value) -> float:
    """Parse amount from various formats"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0.0
    try:
        if isinstance(value, (int, float)):
            return abs(float(value))
        cleaned = str(value).replace('₹', '').replace(',', '').replace(' ', '').strip()
        return abs(float(cleaned)) if cleaned and cleaned != 'nan' else 0.0
    except Exception:
        return 0.0


@router.get("/list")
async def get_opening_balances(financial_year: Optional[str] = None):
    """Get all opening balances, optionally filtered by financial year"""
    db = get_sync_db()
    
    query = {}
    if financial_year:
        query["financial_year"] = financial_year
    
    balances = list(db.opening_balances.find(query, {"_id": 0}).sort("account_name", 1))
    
    # Calculate totals
    total_debit = sum(b.get("debit_balance", 0) for b in balances)
    total_credit = sum(b.get("credit_balance", 0) for b in balances)
    
    # Group by type
    by_type = {
        "assets": [],
        "liabilities": [],
        "equity": []
    }
    
    for b in balances:
        acc_type = b.get("account_type", "").lower()
        if acc_type in ["asset", "assets"]:
            by_type["assets"].append(b)
        elif acc_type in ["liability", "liabilities"]:
            by_type["liabilities"].append(b)
        elif acc_type in ["equity", "capital"]:
            by_type["equity"].append(b)
    
    return {
        "balances": balances,
        "by_type": by_type,
        "summary": {
            "total_accounts": len(balances),
            "total_debit": total_debit,
            "total_credit": total_credit,
            "difference": abs(total_debit - total_credit),
            "is_balanced": abs(total_debit - total_credit) < 1
        }
    }


@router.get("/balance-sheet")
async def get_balance_sheet(financial_year: Optional[str] = None):
    """Generate balance sheet from opening balances"""
    db = get_sync_db()
    
    query = {}
    if financial_year:
        query["financial_year"] = financial_year
    
    balances = list(db.opening_balances.find(query, {"_id": 0}))
    
    # Structure balance sheet
    balance_sheet = {
        "assets": {
            "current_assets": {"items": [], "total": 0},
            "fixed_assets": {"items": [], "total": 0},
            "investments": {"items": [], "total": 0},
            "total": 0
        },
        "liabilities": {
            "current_liabilities": {"items": [], "total": 0},
            "long_term_liabilities": {"items": [], "total": 0},
            "total": 0
        },
        "equity": {
            "capital": {"items": [], "total": 0},
            "total": 0
        }
    }
    
    for b in balances:
        acc_type = b.get("account_type", "").lower()
        sub_cat = b.get("sub_category", "").lower().replace(" ", "_")
        amount = b.get("net_balance", 0)
        
        item = {
            "name": b.get("account_name"),
            "amount": amount,
            "balance_type": b.get("balance_type")
        }
        
        if acc_type in ["asset", "assets"]:
            if "fixed" in sub_cat:
                balance_sheet["assets"]["fixed_assets"]["items"].append(item)
                balance_sheet["assets"]["fixed_assets"]["total"] += amount
            elif "invest" in sub_cat:
                balance_sheet["assets"]["investments"]["items"].append(item)
                balance_sheet["assets"]["investments"]["total"] += amount
            else:
                balance_sheet["assets"]["current_assets"]["items"].append(item)
                balance_sheet["assets"]["current_assets"]["total"] += amount
            balance_sheet["assets"]["total"] += amount
            
        elif acc_type in ["liability", "liabilities"]:
            if "long" in sub_cat or "term" in sub_cat:
                balance_sheet["liabilities"]["long_term_liabilities"]["items"].append(item)
                balance_sheet["liabilities"]["long_term_liabilities"]["total"] += amount
            else:
                balance_sheet["liabilities"]["current_liabilities"]["items"].append(item)
                balance_sheet["liabilities"]["current_liabilities"]["total"] += amount
            balance_sheet["liabilities"]["total"] += amount
            
        elif acc_type in ["equity", "capital"]:
            balance_sheet["equity"]["capital"]["items"].append(item)
            balance_sheet["equity"]["capital"]["total"] += amount
            balance_sheet["equity"]["total"] += amount
    
    # Calculate totals
    total_assets = balance_sheet["assets"]["total"]
    total_liabilities_equity = balance_sheet["liabilities"]["total"] + balance_sheet["equity"]["total"]
    
    return {
        "financial_year": financial_year,
        "balance_sheet": balance_sheet,
        "summary": {
            "total_assets": total_assets,
            "total_liabilities": balance_sheet["liabilities"]["total"],
            "total_equity": balance_sheet["equity"]["total"],
            "total_liabilities_equity": total_liabilities_equity,
            "is_balanced": abs(total_assets - total_liabilities_equity) < 1
        }
    }


@router.post("/ai-analysis")
async def ai_analyze_balance_sheet(financial_year: Optional[str] = None):
    """Use AI CA Agent to analyze the balance sheet"""
    db = get_sync_db()
    
    # Get balance sheet data
    query = {}
    if financial_year:
        query["financial_year"] = financial_year
    
    balances = list(db.opening_balances.find(query, {"_id": 0}))
    
    if not balances:
        return {"error": "No opening balances found. Please import balance sheet first."}
    
    # Calculate key metrics
    assets = [b for b in balances if b.get("account_type", "").lower() in ["asset", "assets"]]
    liabilities = [b for b in balances if b.get("account_type", "").lower() in ["liability", "liabilities"]]
    equity = [b for b in balances if b.get("account_type", "").lower() in ["equity", "capital"]]
    
    total_assets = sum(b.get("net_balance", 0) for b in assets)
    total_liabilities = sum(b.get("net_balance", 0) for b in liabilities)
    total_equity = sum(b.get("net_balance", 0) for b in equity)
    
    # Current assets and liabilities
    current_assets = sum(b.get("net_balance", 0) for b in assets 
                        if "current" in b.get("sub_category", "").lower())
    current_liabilities = sum(b.get("net_balance", 0) for b in liabilities 
                             if "current" in b.get("sub_category", "").lower())
    
    # Calculate ratios
    current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
    debt_equity_ratio = total_liabilities / total_equity if total_equity > 0 else 0
    
    # AI Analysis
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        analysis_prompt = f"""
        Analyze this balance sheet as an expert Chartered Accountant:
        
        **Balance Sheet Summary (FY: {financial_year or 'Current'})**
        
        ASSETS:
        - Total Assets: ₹{total_assets:,.2f}
        - Current Assets: ₹{current_assets:,.2f}
        - Fixed Assets: ₹{total_assets - current_assets:,.2f}
        
        LIABILITIES:
        - Total Liabilities: ₹{total_liabilities:,.2f}
        - Current Liabilities: ₹{current_liabilities:,.2f}
        
        EQUITY:
        - Total Equity: ₹{total_equity:,.2f}
        
        KEY RATIOS:
        - Current Ratio: {current_ratio:.2f}
        - Debt-to-Equity Ratio: {debt_equity_ratio:.2f}
        
        DETAILED ACCOUNTS:
        Assets: {[f"{b['account_name']}: ₹{b['net_balance']:,.0f}" for b in assets[:10]]}
        Liabilities: {[f"{b['account_name']}: ₹{b['net_balance']:,.0f}" for b in liabilities[:10]]}
        Equity: {[f"{b['account_name']}: ₹{b['net_balance']:,.0f}" for b in equity[:5]]}
        
        Please provide:
        1. Overall financial health assessment
        2. Liquidity analysis
        3. Capital structure analysis
        4. Key concerns or red flags
        5. Recommendations for improvement
        6. Year-opening checklist items
        """
        
        llm = LlmChat(api_key=os.environ.get("EMERGENT_API_KEY"))
        llm.add_message(UserMessage(analysis_prompt))
        ai_response = llm.send()
        
        return {
            "status": "success",
            "financial_year": financial_year,
            "metrics": {
                "total_assets": total_assets,
                "total_liabilities": total_liabilities,
                "total_equity": total_equity,
                "current_ratio": round(current_ratio, 2),
                "debt_equity_ratio": round(debt_equity_ratio, 2)
            },
            "ai_analysis": ai_response,
            "accounts_analyzed": len(balances)
        }
        
    except Exception as e:
        logger.error(f"AI Analysis error: {str(e)}")
        # Return basic analysis without AI
        return {
            "status": "partial",
            "financial_year": financial_year,
            "metrics": {
                "total_assets": total_assets,
                "total_liabilities": total_liabilities,
                "total_equity": total_equity,
                "current_ratio": round(current_ratio, 2),
                "debt_equity_ratio": round(debt_equity_ratio, 2)
            },
            "basic_analysis": {
                "liquidity": "Good" if current_ratio >= 1.5 else "Moderate" if current_ratio >= 1 else "Needs Attention",
                "leverage": "Low" if debt_equity_ratio < 1 else "Moderate" if debt_equity_ratio < 2 else "High",
                "balance_check": "Balanced" if abs(total_assets - (total_liabilities + total_equity)) < 1 else "Unbalanced"
            },
            "accounts_analyzed": len(balances),
            "ai_error": str(e)
        }


@router.delete("/clear")
async def clear_opening_balances(financial_year: Optional[str] = None):
    """Clear opening balances (optionally for specific FY)"""
    db = get_sync_db()
    
    query = {}
    if financial_year:
        query["financial_year"] = financial_year
    
    result = db.opening_balances.delete_many(query)
    
    return {
        "status": "success",
        "deleted": result.deleted_count,
        "financial_year": financial_year or "all"
    }
