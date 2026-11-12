"""
Financial Reports Routes - COMPREHENSIVE FIX
P&L Statement, Balance Sheet, Cash Flow Statement, GST Reports, Audit Trail

Key fixes:
1. Handles both ISODate and string date formats in orders
2. Includes all relevant payment statuses for accurate reporting
3. Proper date filtering for purchase bills (string format)
4. GST calculations from both sales and purchases
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from database import get_db
import uuid
import logging
import io
import csv
import math

router = APIRouter(prefix="/financial-reports", tags=["Financial Reports"])
logger = logging.getLogger(__name__)


# ============ HELPERS ============

def get_date_range(period: str, from_date: str = None, to_date: str = None):
    """Get date range based on period or custom dates - returns both datetime and string formats"""
    now = datetime.now(timezone.utc)
    
    if from_date and to_date:
        from dateutil import parser
        start = parser.parse(from_date).replace(tzinfo=timezone.utc)
        end = parser.parse(to_date).replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
        return start, end
    
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, now
    elif period == "this_week":
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, now
    elif period == "this_month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return start, now
    elif period == "last_month":
        first_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = first_this_month - timedelta(seconds=1)
        start = end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return start, end
    elif period == "this_quarter":
        quarter = (now.month - 1) // 3
        start_month = quarter * 3 + 1
        start = now.replace(month=start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        return start, now
    elif period == "this_year":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return start, now
    elif period == "last_year":
        start = now.replace(year=now.year-1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(year=now.year-1, month=12, day=31, hour=23, minute=59, second=59, microsecond=0)
        return start, end
    elif period == "financial_year":
        # Indian Financial Year: April to March
        if now.month >= 4:
            start = now.replace(month=4, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start = now.replace(year=now.year-1, month=4, day=1, hour=0, minute=0, second=0, microsecond=0)
        return start, now
    elif period == "last_financial_year":
        if now.month >= 4:
            start = now.replace(year=now.year-1, month=4, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(month=3, day=31, hour=23, minute=59, second=59, microsecond=0)
        else:
            start = now.replace(year=now.year-2, month=4, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(year=now.year-1, month=3, day=31, hour=23, minute=59, second=59, microsecond=0)
        return start, end
    else:
        # Default: last 30 days
        start = now - timedelta(days=30)
        return start, now


def clean_nan(value, default=0):
    """Clean NaN/Infinity values"""
    if value is None:
        return default
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return default
    return value


async def get_offline_invoice_data(db, start_date: datetime, end_date: datetime, store_code: Optional[str] = None):
    """
    Get sales data from offline_invoices collection (in-store / converted sales invoices).
    CRITICAL: must filter document_type='invoice' so we DON'T count Sales Orders as completed sales.
    Field names in this collection: total_amount, tax_total, cgst_total, sgst_total, igst_total
    """
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    match_clause: Dict[str, Any] = {
        "document_type": "invoice",  # Exclude Sales Orders
        "$or": [
            {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}},
            {"created_at": {"$gte": start_date, "$lte": end_date}}
        ]
    }
    if store_code:
        match_clause["store_code"] = store_code

    pipeline = [
        {"$match": match_clause},
        {"$group": {
            "_id": "$payment_status",
            "total_amount": {"$sum": {"$ifNull": ["$total_amount", 0]}},
            "subtotal": {"$sum": {"$ifNull": ["$subtotal", 0]}},
            "tax_total": {"$sum": {"$ifNull": ["$tax_total", 0]}},
            "cgst_total": {"$sum": {"$ifNull": ["$cgst_total", 0]}},
            "sgst_total": {"$sum": {"$ifNull": ["$sgst_total", 0]}},
            "igst_total": {"$sum": {"$ifNull": ["$igst_total", 0]}},
            "count": {"$sum": 1}
        }}
    ]
    results = await db.offline_invoices.aggregate(pipeline).to_list(None)

    total = 0.0
    paid = 0.0
    pending = 0.0
    taxable_value = 0.0
    cgst = 0.0
    sgst = 0.0
    igst = 0.0
    total_count = 0
    for r in results:
        amount = clean_nan(r.get("total_amount", 0))
        total += amount
        total_count += r.get("count", 0)
        taxable_value += clean_nan(r.get("subtotal", 0))
        cgst += clean_nan(r.get("cgst_total", 0))
        sgst += clean_nan(r.get("sgst_total", 0))
        igst += clean_nan(r.get("igst_total", 0))
        if r["_id"] in ["paid", "completed"]:
            paid += amount
        else:
            pending += amount

    total_gst = cgst + sgst + igst
    return {
        "total_amount": total,
        "paid": paid,
        "pending": pending,
        "count": total_count,
        "taxable_value": taxable_value,
        "cgst": cgst,
        "sgst": sgst,
        "igst": igst,
        "total_gst": total_gst
    }


async def get_sales_data(db, start_date: datetime, end_date: datetime):
    """
    Get sales data from orders collection
    Handles both ISODate and string date formats
    Includes all payment statuses for comprehensive reporting
    """
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    # Simple query - MongoDB handles ISODate comparison well
    # For string dates, we need separate handling
    pipeline = [
        {"$match": {
            "$or": [
                # ISODate format - direct comparison
                {"created_at": {"$gte": start_date, "$lte": end_date, "$type": "date"}},
                # String format (YYYY-MM-DD...)
                {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59", "$type": "string"}}
            ]
        }},
        {"$group": {
            "_id": "$payment_status",
            "total_amount": {"$sum": "$total_amount"},
            "count": {"$sum": 1},
            "gst_amount": {"$sum": {"$ifNull": ["$gst_amount", 0]}},
            "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
            "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
            "igst": {"$sum": {"$ifNull": ["$igst", 0]}}
        }}
    ]
    
    results = await db.orders.aggregate(pipeline).to_list(None)
    
    # Aggregate by payment status
    total_sales = 0
    paid_sales = 0
    pending_sales = 0
    total_orders = 0
    total_gst = 0
    
    for r in results:
        amount = clean_nan(r.get("total_amount", 0))
        count = r.get("count", 0)
        gst = clean_nan(r.get("gst_amount", 0)) + clean_nan(r.get("cgst", 0)) + clean_nan(r.get("sgst", 0)) + clean_nan(r.get("igst", 0))
        
        total_sales += amount
        total_orders += count
        total_gst += gst
        
        if r["_id"] in ["completed", "paid"]:
            paid_sales += amount
        else:
            pending_sales += amount
    
    return {
        "gross_sales": clean_nan(total_sales),
        "paid_sales": clean_nan(paid_sales),
        "pending_sales": clean_nan(pending_sales),
        "order_count": total_orders,
        "gst_collected": clean_nan(total_gst)
    }


async def get_purchase_data(db, start_date: datetime, end_date: datetime):
    """
    Get purchase data from purchase_bills collection
    bill_date is stored as string (YYYY-MM-DD)
    """
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    pipeline = [
        {"$match": {
            "bill_date": {"$gte": start_str, "$lte": end_str}
        }},
        {"$group": {
            "_id": "$payment_status",
            "total_amount": {"$sum": "$grand_total"},
            "count": {"$sum": 1},
            "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
            "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
            "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
            "total_tax": {"$sum": {"$ifNull": ["$total_tax", 0]}}
        }}
    ]
    
    results = await db.purchase_bills.aggregate(pipeline).to_list(None)
    
    total_purchases = 0
    paid_purchases = 0
    pending_purchases = 0
    total_bills = 0
    total_gst = 0
    
    for r in results:
        amount = clean_nan(r.get("total_amount", 0))
        count = r.get("count", 0)
        gst = clean_nan(r.get("total_tax", 0)) or (clean_nan(r.get("cgst", 0)) + clean_nan(r.get("sgst", 0)) + clean_nan(r.get("igst", 0)))
        
        total_purchases += amount
        total_bills += count
        total_gst += gst
        
        if r["_id"] in ["completed", "paid"]:
            paid_purchases += amount
        else:
            pending_purchases += amount
    
    return {
        "total_purchases": clean_nan(total_purchases),
        "paid_purchases": clean_nan(paid_purchases),
        "pending_purchases": clean_nan(pending_purchases),
        "bill_count": total_bills,
        "gst_paid": clean_nan(total_gst)
    }


# ============ PROFIT & LOSS STATEMENT ============

@router.get("/profit-loss")
async def get_profit_loss_statement(
    period: str = "this_month",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Generate Profit & Loss Statement"""
    try:
        start_date, end_date = get_date_range(period, from_date, to_date)
        
        logger.info(f"P&L Report - Period: {period}, Start: {start_date}, End: {end_date}")
        
        # Get sales data
        sales_data = await get_sales_data(db, start_date, end_date)
        
        # Get purchase data
        purchase_data = await get_purchase_data(db, start_date, end_date)
        
        # Offline invoices revenue (with CORRECT field names + document_type filter)
        offline_data = await get_offline_invoice_data(db, start_date, end_date)
        offline_sales = offline_data["total_amount"]
        offline_gst = offline_data["total_gst"]
        offline_count = offline_data["count"]

        # Date strings — used by the expenses pipeline below
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Operating expenses
        expense_pipeline = [
            {"$match": {
                "$or": [
                    {"date": {"$gte": start_date, "$lte": end_date}},
                    {"date": {"$gte": start_str, "$lte": end_str}}
                ]
            }},
            {"$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"}
            }}
        ]
        expenses_result = await db.expenses.aggregate(expense_pipeline).to_list(None)
        
        expenses_by_category = {}
        total_expenses = 0
        for exp in expenses_result:
            category = exp.get("_id", "Other")
            amount = clean_nan(exp.get("total", 0))
            expenses_by_category[category] = amount
            total_expenses += amount
        
        # Calculate P&L
        gross_revenue = clean_nan(sales_data["gross_sales"]) + clean_nan(offline_sales)
        cost_of_goods = clean_nan(purchase_data["total_purchases"])
        gross_profit = gross_revenue - cost_of_goods
        operating_profit = gross_profit - total_expenses

        # Tax calculations — output_gst now includes both online order GST + offline invoice GST
        output_gst = clean_nan(sales_data["gst_collected"]) + clean_nan(offline_gst)
        gst_payable = output_gst - clean_nan(purchase_data["gst_paid"])
        
        return {
            "status": "success",
            "period": {
                "name": period,
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            },
            "revenue": {
                "gross_revenue": gross_revenue,
                "online_sales": clean_nan(sales_data["gross_sales"]),
                "offline_sales": clean_nan(offline_sales),
                "offline_count": offline_count,
                "order_count": sales_data["order_count"],
                "paid_sales": clean_nan(sales_data["paid_sales"]) + clean_nan(offline_data["paid"]),
                "pending_sales": clean_nan(sales_data["pending_sales"]) + clean_nan(offline_data["pending"])
            },
            "cost_of_goods_sold": {
                "purchases": cost_of_goods,
                "purchase_count": purchase_data["bill_count"],
                "paid_purchases": clean_nan(purchase_data["paid_purchases"]),
                "pending_purchases": clean_nan(purchase_data["pending_purchases"])
            },
            "gross_profit": gross_profit,
            "gross_margin_percent": round((gross_profit / gross_revenue * 100) if gross_revenue > 0 else 0, 2),
            "operating_expenses": {
                "by_category": expenses_by_category,
                "total": total_expenses
            },
            "operating_profit": operating_profit,
            "gst": {
                "output_gst": output_gst,
                "input_gst": clean_nan(purchase_data["gst_paid"]),
                "net_gst_payable": gst_payable
            },
            "net_profit": operating_profit - max(0, gst_payable)
        }
        
    except Exception as e:
        logger.error(f"Error generating P&L: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ BALANCE SHEET ============

@router.get("/balance-sheet")
async def get_balance_sheet(
    as_of_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Generate Balance Sheet"""
    try:
        if as_of_date:
            from dateutil import parser
            end_date = parser.parse(as_of_date).replace(tzinfo=timezone.utc)
        else:
            end_date = datetime.now(timezone.utc)
        
        end_str = end_date.strftime("%Y-%m-%d")
        
        # ASSETS
        # Accounts Receivable (Unpaid sales)
        ar_pipeline = [
            {"$match": {
                "payment_status": {"$in": ["pending", "partial", "cod"]}
            }},
            {"$group": {
                "_id": None,
                "total": {"$sum": "$total_amount"},
                "count": {"$sum": 1}
            }}
        ]
        ar_result = await db.orders.aggregate(ar_pipeline).to_list(length=1)
        accounts_receivable = clean_nan(ar_result[0]["total"]) if ar_result else 0
        
        # Inventory value (from products)
        inv_pipeline = [
            {"$match": {"stock": {"$gt": 0}}},
            {"$group": {
                "_id": None,
                "total_value": {"$sum": {"$multiply": ["$stock", {"$ifNull": ["$purchase_price", "$price"]}]}},
                "total_items": {"$sum": "$stock"}
            }}
        ]
        inv_result = await db.products.aggregate(inv_pipeline).to_list(length=1)
        inventory_value = clean_nan(inv_result[0]["total_value"]) if inv_result else 0
        
        # LIABILITIES
        # Accounts Payable (Unpaid purchase bills)
        ap_pipeline = [
            {"$match": {
                "payment_status": {"$in": ["pending", "partial"]}
            }},
            {"$group": {
                "_id": None,
                "total": {"$sum": "$grand_total"},
                "count": {"$sum": 1}
            }}
        ]
        ap_result = await db.purchase_bills.aggregate(ap_pipeline).to_list(length=1)
        accounts_payable = clean_nan(ap_result[0]["total"]) if ap_result else 0
        
        # GST Liability
        gst_liability = 0  # Would need proper GST tracking
        
        # Calculate totals
        total_assets = accounts_receivable + inventory_value
        total_liabilities = accounts_payable + gst_liability
        equity = total_assets - total_liabilities
        
        return {
            "status": "success",
            "as_of_date": end_date.isoformat(),
            "assets": {
                "current_assets": {
                    "accounts_receivable": accounts_receivable,
                    "inventory": inventory_value,
                    "total_current": accounts_receivable + inventory_value
                },
                "fixed_assets": {
                    "total_fixed": 0  # Would need fixed asset tracking
                },
                "total_assets": total_assets
            },
            "liabilities": {
                "current_liabilities": {
                    "accounts_payable": accounts_payable,
                    "gst_payable": gst_liability,
                    "total_current": accounts_payable + gst_liability
                },
                "long_term_liabilities": {
                    "total_long_term": 0
                },
                "total_liabilities": total_liabilities
            },
            "equity": {
                "retained_earnings": equity,
                "total_equity": equity
            },
            "total_liabilities_and_equity": total_liabilities + equity
        }
        
    except Exception as e:
        logger.error(f"Error generating Balance Sheet: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ GST REPORTS ============

@router.get("/gst/gstr1")
async def get_gstr1_report(
    period: str = "this_month",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Generate GSTR-1 (Outward Supplies / Sales)"""
    try:
        start_date, end_date = get_date_range(period, from_date, to_date)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # B2B Sales (with GSTIN)
        b2b_pipeline = [
            {"$match": {
                "$or": [
                    {"created_at": {"$gte": start_date, "$lte": end_date}},
                    {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}}
                ],
                "customer_gstin": {"$exists": True, "$nin": ["", None]}
            }},
            {"$group": {
                "_id": "$customer_gstin",
                "customer_name": {"$first": "$customer_name"},
                "taxable_value": {"$sum": "$subtotal"},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "total_tax": {"$sum": {"$ifNull": ["$gst_amount", 0]}},
                "invoice_count": {"$sum": 1},
                "total_value": {"$sum": "$total_amount"}
            }}
        ]
        b2b_result = await db.orders.aggregate(b2b_pipeline).to_list(None)
        
        # B2C Sales (without GSTIN)
        b2c_pipeline = [
            {"$match": {
                "$and": [
                    {"$or": [
                        {"created_at": {"$gte": start_date, "$lte": end_date}},
                        {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}}
                    ]},
                    {"$or": [
                        {"customer_gstin": {"$exists": False}},
                        {"customer_gstin": ""},
                        {"customer_gstin": None}
                    ]}
                ]
            }},
            {"$group": {
                "_id": {"$ifNull": ["$shipping_address.state", "Unknown"]},
                "taxable_value": {"$sum": "$subtotal"},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "total_tax": {"$sum": {"$ifNull": ["$gst_amount", 0]}},
                "invoice_count": {"$sum": 1},
                "total_value": {"$sum": "$total_amount"}
            }}
        ]
        b2c_result = await db.orders.aggregate(b2c_pipeline).to_list(None)
        
        # Calculate totals
        total_b2b = sum(clean_nan(r.get("total_value", 0)) for r in b2b_result)
        total_b2c = sum(clean_nan(r.get("total_value", 0)) for r in b2c_result)
        total_tax_b2b = sum(clean_nan(r.get("total_tax", 0)) for r in b2b_result)
        total_tax_b2c = sum(clean_nan(r.get("total_tax", 0)) for r in b2c_result)
        
        return {
            "status": "success",
            "report_type": "GSTR-1",
            "period": {
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            },
            "b2b_supplies": {
                "details": [{
                    "gstin": r["_id"],
                    "customer_name": r.get("customer_name", ""),
                    "taxable_value": clean_nan(r.get("taxable_value", 0)),
                    "cgst": clean_nan(r.get("cgst", 0)),
                    "sgst": clean_nan(r.get("sgst", 0)),
                    "igst": clean_nan(r.get("igst", 0)),
                    "total_tax": clean_nan(r.get("total_tax", 0)),
                    "invoice_count": r.get("invoice_count", 0),
                    "total_value": clean_nan(r.get("total_value", 0))
                } for r in b2b_result],
                "total_taxable": sum(clean_nan(r.get("taxable_value", 0)) for r in b2b_result),
                "total_tax": total_tax_b2b,
                "total_value": total_b2b,
                "invoice_count": sum(r.get("invoice_count", 0) for r in b2b_result)
            },
            "b2c_supplies": {
                "details": [{
                    "place_of_supply": r["_id"],
                    "taxable_value": clean_nan(r.get("taxable_value", 0)),
                    "cgst": clean_nan(r.get("cgst", 0)),
                    "sgst": clean_nan(r.get("sgst", 0)),
                    "igst": clean_nan(r.get("igst", 0)),
                    "total_tax": clean_nan(r.get("total_tax", 0)),
                    "invoice_count": r.get("invoice_count", 0),
                    "total_value": clean_nan(r.get("total_value", 0))
                } for r in b2c_result],
                "total_taxable": sum(clean_nan(r.get("taxable_value", 0)) for r in b2c_result),
                "total_tax": total_tax_b2c,
                "total_value": total_b2c,
                "invoice_count": sum(r.get("invoice_count", 0) for r in b2c_result)
            },
            "summary": {
                "total_outward_supplies": total_b2b + total_b2c,
                "total_output_tax": total_tax_b2b + total_tax_b2c,
                "total_invoices": sum(r.get("invoice_count", 0) for r in b2b_result) + sum(r.get("invoice_count", 0) for r in b2c_result)
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating GSTR-1: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gstr1-summary")
async def get_gstr1_summary(
    period: str = "this_month",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Get GSTR-1 Summary — aggregates GST collected on outward supplies from BOTH
    ecommerce orders AND offline invoices (the canonical source for in-store sales)."""
    try:
        start_date, end_date = get_date_range(period, from_date, to_date)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        # ===== Online ecommerce orders =====
        online_pipeline = [
            {"$match": {
                "$or": [
                    {"created_at": {"$gte": start_date, "$lte": end_date}},
                    {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}}
                ]
            }},
            {"$group": {
                "_id": None,
                "taxable_value": {"$sum": {"$ifNull": ["$subtotal", 0]}},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "total_value": {"$sum": {"$ifNull": ["$total_amount", 0]}},
                "invoice_count": {"$sum": 1}
            }}
        ]
        online_result = await db.orders.aggregate(online_pipeline).to_list(1)
        online = online_result[0] if online_result else {
            "taxable_value": 0, "cgst": 0, "sgst": 0, "igst": 0, "total_value": 0, "invoice_count": 0
        }

        # ===== Offline invoices (in-store) — correct field names =====
        offline = await get_offline_invoice_data(db, start_date, end_date)

        taxable_value = clean_nan(online.get("taxable_value", 0)) + clean_nan(offline["taxable_value"])
        cgst = clean_nan(online.get("cgst", 0)) + clean_nan(offline["cgst"])
        sgst = clean_nan(online.get("sgst", 0)) + clean_nan(offline["sgst"])
        igst = clean_nan(online.get("igst", 0)) + clean_nan(offline["igst"])
        total_gst = cgst + sgst + igst
        total_value = clean_nan(online.get("total_value", 0)) + clean_nan(offline["total_amount"])
        invoice_count = online.get("invoice_count", 0) + offline["count"]

        return {
            "status": "success",
            "period": {
                "name": period,
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            },
            "summary": {
                "taxable_value": taxable_value,
                "cgst": cgst,
                "sgst": sgst,
                "igst": igst,
                "total_gst": total_gst,
                "total_value": total_value,
                "invoice_count": invoice_count,
                # Bifurcation for transparency
                "online_invoice_count": online.get("invoice_count", 0),
                "offline_invoice_count": offline["count"],
                "online_taxable_value": clean_nan(online.get("taxable_value", 0)),
                "offline_taxable_value": clean_nan(offline["taxable_value"])
            }
        }

    except Exception as e:
        logger.error(f"Error getting GSTR-1 summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gst/gstr2")
async def get_gstr2_report(
    period: str = "this_month",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Generate GSTR-2 (Inward Supplies / Purchases)"""
    try:
        start_date, end_date = get_date_range(period, from_date, to_date)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Purchases by vendor
        purchase_pipeline = [
            {"$match": {
                "bill_date": {"$gte": start_str, "$lte": end_str}
            }},
            {"$group": {
                "_id": {"$ifNull": ["$vendor_gst", "$vendor_gstin"]},
                "vendor_name": {"$first": "$vendor_name"},
                "taxable_value": {"$sum": "$subtotal"},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "total_tax": {"$sum": {"$ifNull": ["$total_tax", 0]}},
                "bill_count": {"$sum": 1},
                "total_value": {"$sum": "$grand_total"}
            }}
        ]
        purchase_result = await db.purchase_bills.aggregate(purchase_pipeline).to_list(None)
        
        # Calculate totals
        total_purchases = sum(clean_nan(r.get("total_value", 0)) for r in purchase_result)
        total_input_tax = sum(clean_nan(r.get("total_tax", 0)) for r in purchase_result)
        
        return {
            "status": "success",
            "report_type": "GSTR-2",
            "period": {
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            },
            "inward_supplies": {
                "details": [{
                    "gstin": r["_id"] or "Unregistered",
                    "vendor_name": r.get("vendor_name", ""),
                    "taxable_value": clean_nan(r.get("taxable_value", 0)),
                    "cgst": clean_nan(r.get("cgst", 0)),
                    "sgst": clean_nan(r.get("sgst", 0)),
                    "igst": clean_nan(r.get("igst", 0)),
                    "total_tax": clean_nan(r.get("total_tax", 0)),
                    "bill_count": r.get("bill_count", 0),
                    "total_value": clean_nan(r.get("total_value", 0))
                } for r in purchase_result],
                "total_taxable": sum(clean_nan(r.get("taxable_value", 0)) for r in purchase_result),
                "total_tax": total_input_tax,
                "total_value": total_purchases,
                "bill_count": sum(r.get("bill_count", 0) for r in purchase_result)
            },
            "summary": {
                "total_inward_supplies": total_purchases,
                "total_input_tax_credit": total_input_tax,
                "total_bills": sum(r.get("bill_count", 0) for r in purchase_result)
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating GSTR-2: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gst/gstr3b")
async def get_gstr3b_report(
    period: str = "this_month",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Generate GSTR-3B Summary — combines online orders + offline invoices."""
    try:
        start_date, end_date = get_date_range(period, from_date, to_date)

        sales_data = await get_sales_data(db, start_date, end_date)
        offline_data = await get_offline_invoice_data(db, start_date, end_date)
        purchase_data = await get_purchase_data(db, start_date, end_date)

        online_gst = clean_nan(sales_data.get("gst_collected", 0))
        offline_cgst = clean_nan(offline_data["cgst"])
        offline_sgst = clean_nan(offline_data["sgst"])
        offline_igst = clean_nan(offline_data["igst"])

        output_tax = online_gst + offline_cgst + offline_sgst + offline_igst
        output_cgst = offline_cgst + (online_gst / 2 if online_gst > 0 else 0)
        output_sgst = offline_sgst + (online_gst / 2 if online_gst > 0 else 0)
        output_igst = offline_igst

        taxable_value = clean_nan(sales_data.get("gross_sales", 0)) + clean_nan(offline_data["taxable_value"])
        input_tax = clean_nan(purchase_data.get("gst_paid", 0))
        net_tax = output_tax - input_tax

        return {
            "status": "success",
            "report_type": "GSTR-3B",
            "period": {
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            },
            "outward_supplies": {
                "taxable_value": taxable_value,
                "integrated_tax": output_igst,
                "central_tax": output_cgst,
                "state_tax": output_sgst,
                "cess": 0
            },
            "inward_supplies_itc": {
                "taxable_value": clean_nan(purchase_data.get("total_purchases", 0)),
                "integrated_tax": 0,
                "central_tax": input_tax / 2 if input_tax > 0 else 0,
                "state_tax": input_tax / 2 if input_tax > 0 else 0,
                "cess": 0
            },
            "tax_payable": {
                "integrated_tax": max(0, output_igst),
                "central_tax": max(0, output_cgst - (input_tax / 2 if input_tax > 0 else 0)) if net_tax > 0 else 0,
                "state_tax": max(0, output_sgst - (input_tax / 2 if input_tax > 0 else 0)) if net_tax > 0 else 0,
                "cess": 0,
                "total": max(0, net_tax)
            },
            "summary": {
                "total_output_tax": output_tax,
                "total_input_tax_credit": input_tax,
                "net_tax_liability": net_tax,
                "tax_payable": max(0, net_tax),
                "itc_carry_forward": max(0, -net_tax),
                "online_invoice_count": sales_data.get("order_count", 0),
                "offline_invoice_count": offline_data["count"]
            }
        }

    except Exception as e:
        logger.error(f"Error generating GSTR-3B: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ CASH FLOW STATEMENT ============

@router.get("/cash-flow")
async def get_cash_flow_statement(
    period: str = "this_month",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Generate Cash Flow Statement"""
    try:
        start_date, end_date = get_date_range(period, from_date, to_date)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Cash from operations - paid sales
        sales_pipeline = [
            {"$match": {
                "$or": [
                    {"created_at": {"$gte": start_date, "$lte": end_date}},
                    {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}}
                ],
                "payment_status": {"$in": ["completed", "paid"]}
            }},
            {"$group": {
                "_id": None,
                "total": {"$sum": "$total_amount"},
                "count": {"$sum": 1}
            }}
        ]
        sales_result = await db.orders.aggregate(sales_pipeline).to_list(length=1)
        cash_from_sales = clean_nan(sales_result[0]["total"]) if sales_result else 0
        
        # Cash paid for purchases
        purchase_pipeline = [
            {"$match": {
                "bill_date": {"$gte": start_str, "$lte": end_str},
                "payment_status": {"$in": ["completed", "paid"]}
            }},
            {"$group": {
                "_id": None,
                "total": {"$sum": "$grand_total"},
                "count": {"$sum": 1}
            }}
        ]
        purchase_result = await db.purchase_bills.aggregate(purchase_pipeline).to_list(length=1)
        cash_for_purchases = clean_nan(purchase_result[0]["total"]) if purchase_result else 0
        
        # Operating cash flow
        net_operating = cash_from_sales - cash_for_purchases
        
        return {
            "status": "success",
            "period": {
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            },
            "operating_activities": {
                "cash_from_customers": cash_from_sales,
                "cash_paid_to_suppliers": cash_for_purchases,
                "cash_paid_for_expenses": 0,
                "net_operating_cash_flow": net_operating
            },
            "investing_activities": {
                "purchase_of_assets": 0,
                "sale_of_assets": 0,
                "net_investing_cash_flow": 0
            },
            "financing_activities": {
                "loans_received": 0,
                "loans_repaid": 0,
                "net_financing_cash_flow": 0
            },
            "summary": {
                "net_change_in_cash": net_operating,
                "opening_cash": 0,
                "closing_cash": net_operating
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating Cash Flow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ ACCOUNTING REPORTS SUMMARY ============

@router.get("/summary")
async def get_accounting_summary(
    period: str = "this_month",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Get comprehensive accounting summary for dashboard"""
    try:
        start_date, end_date = get_date_range(period, from_date, to_date)

        # Get all data — include BOTH online orders AND offline invoices
        sales_data = await get_sales_data(db, start_date, end_date)
        offline_data = await get_offline_invoice_data(db, start_date, end_date)
        purchase_data = await get_purchase_data(db, start_date, end_date)

        total_sales = clean_nan(sales_data.get("gross_sales", 0)) + clean_nan(offline_data["total_amount"])
        total_paid_sales = clean_nan(sales_data.get("paid_sales", 0)) + clean_nan(offline_data["paid"])
        total_pending_sales = clean_nan(sales_data.get("pending_sales", 0)) + clean_nan(offline_data["pending"])
        total_gst_collected = clean_nan(sales_data.get("gst_collected", 0)) + clean_nan(offline_data["total_gst"])

        return {
            "status": "success",
            "period": {
                "name": period,
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            },
            "sales": {
                "total": total_sales,
                "paid": total_paid_sales,
                "pending": total_pending_sales,
                "count": sales_data.get("order_count", 0) + offline_data["count"],
                "online_count": sales_data.get("order_count", 0),
                "offline_count": offline_data["count"],
                "online_total": clean_nan(sales_data.get("gross_sales", 0)),
                "offline_total": clean_nan(offline_data["total_amount"]),
                "gst_collected": total_gst_collected
            },
            "purchases": {
                "total": clean_nan(purchase_data.get("total_purchases", 0)),
                "paid": clean_nan(purchase_data.get("paid_purchases", 0)),
                "pending": clean_nan(purchase_data.get("pending_purchases", 0)),
                "count": purchase_data.get("bill_count", 0),
                "gst_paid": clean_nan(purchase_data.get("gst_paid", 0))
            },
            "profit_loss": {
                "gross_profit": total_sales - clean_nan(purchase_data.get("total_purchases", 0)),
                "gst_liability": total_gst_collected - clean_nan(purchase_data.get("gst_paid", 0))
            }
        }

    except Exception as e:
        logger.error(f"Error getting summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ DASHBOARD ENDPOINT ============

@router.get("/dashboard")
async def get_financial_dashboard(
    period: str = "this_month",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Get comprehensive financial dashboard data - matches frontend expected format"""
    try:
        now = datetime.now(timezone.utc)
        
        # Get date range based on period
        start_date, end_date = get_date_range(period, from_date, to_date)
        
        # Get current period data
        current_sales = await get_sales_data(db, start_date, end_date)
        current_purchases = await get_purchase_data(db, start_date, end_date)
        
        # Calculate metrics for selected period
        current_revenue = clean_nan(current_sales.get("gross_sales", 0))
        current_expenses = clean_nan(current_purchases.get("total_purchases", 0))
        current_profit = current_revenue - current_expenses
        current_margin = (current_profit / current_revenue * 100) if current_revenue > 0 else 0
        
        # Get comparison period (previous period of same duration)
        duration = end_date - start_date
        prev_end = start_date - timedelta(seconds=1)
        prev_start = prev_end - duration
        
        prev_sales = await get_sales_data(db, prev_start, prev_end)
        prev_purchases = await get_purchase_data(db, prev_start, prev_end)
        
        prev_revenue = clean_nan(prev_sales.get("gross_sales", 0))
        prev_expenses = clean_nan(prev_purchases.get("total_purchases", 0))
        prev_profit = prev_revenue - prev_expenses
        
        # Receivables (pending sales)
        ar_pipeline = [
            {"$match": {"payment_status": {"$in": ["pending", "partial", "cod"]}}},
            {"$group": {"_id": None, "total": {"$sum": "$total_amount"}, "count": {"$sum": 1}}}
        ]
        ar_result = await db.orders.aggregate(ar_pipeline).to_list(length=1)
        receivables = clean_nan(ar_result[0]["total"]) if ar_result else 0
        receivables_count = ar_result[0]["count"] if ar_result else 0
        
        # Payables (pending purchases)
        ap_pipeline = [
            {"$match": {"payment_status": {"$in": ["pending", "partial"]}}},
            {"$group": {"_id": None, "total": {"$sum": "$grand_total"}, "count": {"$sum": 1}}}
        ]
        ap_result = await db.purchase_bills.aggregate(ap_pipeline).to_list(length=1)
        payables = clean_nan(ap_result[0]["total"]) if ap_result else 0
        payables_count = ap_result[0]["count"] if ap_result else 0
        
        # Top vendors by purchase value
        vendor_pipeline = [
            {"$group": {
                "_id": "$vendor_name",
                "total": {"$sum": "$grand_total"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"total": -1}},
            {"$limit": 5}
        ]
        top_vendors = await db.purchase_bills.aggregate(vendor_pipeline).to_list(5)
        
        return {
            "status": "success",
            "period": {
                "name": period,
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            },
            "dashboard": {
                "this_month": {
                    "revenue": current_revenue,
                    "expenses": current_expenses,
                    "profit": current_profit,
                    "margin": round(current_margin, 2),
                    "orders": current_sales.get("order_count", 0),
                    "bills": current_purchases.get("bill_count", 0)
                },
                "last_month": {
                    "revenue": prev_revenue,
                    "expenses": prev_expenses,
                    "profit": prev_profit
                },
                "receivables": {
                    "total": receivables,
                    "overdue": receivables * 0.1,  # Estimate 10% overdue
                    "pending_count": receivables_count
                },
                "payables": {
                    "total": payables,
                    "due_this_week": payables * 0.3,  # Estimate 30% due this week
                    "pending_count": payables_count
                },
                "cash_position": {
                    "bank_balance": current_revenue - current_expenses,
                    "cash_in_hand": 0,
                    "bank_accounts": 1
                },
                "top_vendors": [{
                    "name": v.get("_id", "Unknown"),
                    "amount": clean_nan(v.get("total", 0)),
                    "bill_count": v.get("count", 0)
                } for v in top_vendors],
                "gst": {
                    "output_tax": clean_nan(current_sales.get("gst_collected", 0)),
                    "input_tax": clean_nan(current_purchases.get("gst_paid", 0)),
                    "net_liability": clean_nan(current_sales.get("gst_collected", 0)) - clean_nan(current_purchases.get("gst_paid", 0))
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ GST SUMMARY ============

@router.get("/gst/summary")
async def get_gst_summary(
    period: str = "this_month",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Get GST Summary for the period — combines online orders + offline invoices."""
    try:
        start_date, end_date = get_date_range(period, from_date, to_date)

        sales_data = await get_sales_data(db, start_date, end_date)
        offline_data = await get_offline_invoice_data(db, start_date, end_date)
        purchase_data = await get_purchase_data(db, start_date, end_date)

        # Combine online + offline output GST
        online_gst = clean_nan(sales_data.get("gst_collected", 0))
        offline_cgst = clean_nan(offline_data["cgst"])
        offline_sgst = clean_nan(offline_data["sgst"])
        offline_igst = clean_nan(offline_data["igst"])
        offline_total_gst = clean_nan(offline_data["total_gst"])

        output_tax = online_gst + offline_total_gst
        # CGST/SGST/IGST bifurcation: use offline_data exact split + assume online is intra-state (half each)
        output_cgst = offline_cgst + (online_gst / 2 if online_gst > 0 else 0)
        output_sgst = offline_sgst + (online_gst / 2 if online_gst > 0 else 0)
        output_igst = offline_igst

        taxable_value_sales = clean_nan(sales_data.get("gross_sales", 0)) + clean_nan(offline_data["taxable_value"])
        input_tax = clean_nan(purchase_data.get("gst_paid", 0))
        net_liability = output_tax - input_tax

        return {
            "status": "success",
            "period": {
                "name": period,
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            },
            "output_gst": {
                "total_taxable_value": taxable_value_sales,
                "cgst": output_cgst,
                "sgst": output_sgst,
                "igst": output_igst,
                "total": output_tax,
                "invoice_count": sales_data.get("order_count", 0) + offline_data["count"],
                "online_count": sales_data.get("order_count", 0),
                "offline_count": offline_data["count"]
            },
            "input_gst": {
                "total_taxable_value": clean_nan(purchase_data.get("total_purchases", 0)),
                "cgst": input_tax / 2 if input_tax > 0 else 0,
                "sgst": input_tax / 2 if input_tax > 0 else 0,
                "igst": 0,
                "total": input_tax,
                "bill_count": purchase_data.get("bill_count", 0)
            },
            "net_liability": {
                "cgst": (output_cgst - (input_tax / 2 if input_tax > 0 else 0)) if net_liability > 0 else 0,
                "sgst": (output_sgst - (input_tax / 2 if input_tax > 0 else 0)) if net_liability > 0 else 0,
                "igst": output_igst,
                "total": max(0, net_liability),
                "itc_carry_forward": max(0, -net_liability)
            }
        }

    except Exception as e:
        logger.error(f"Error getting GST summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ HSN-WISE REPORT ============

@router.get("/gst/hsn-wise")
async def get_hsn_wise_report(
    period: str = "this_month",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Get HSN-wise sales report"""
    try:
        start_date, end_date = get_date_range(period, from_date, to_date)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Get HSN-wise data from orders
        hsn_pipeline = [
            {"$match": {
                "$or": [
                    {"created_at": {"$gte": start_date, "$lte": end_date}},
                    {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}}
                ]
            }},
            {"$unwind": "$items"},
            {"$group": {
                "_id": {"$ifNull": ["$items.hsn_code", "N/A"]},
                "description": {"$first": "$items.product_name"},
                "quantity": {"$sum": "$items.quantity"},
                "taxable_value": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}},
                "cgst": {"$sum": {"$ifNull": ["$items.cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$items.sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$items.igst", 0]}},
                "total_value": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}}
            }},
            {"$sort": {"total_value": -1}}
        ]
        
        hsn_result = await db.orders.aggregate(hsn_pipeline).to_list(None)
        
        # Format results
        hsn_data = []
        for r in hsn_result:
            tax = clean_nan(r.get("cgst", 0)) + clean_nan(r.get("sgst", 0)) + clean_nan(r.get("igst", 0))
            hsn_data.append({
                "hsn_code": r["_id"],
                "description": r.get("description", "")[:50] if r.get("description") else "",
                "quantity": r.get("quantity", 0),
                "taxable_value": clean_nan(r.get("taxable_value", 0)),
                "cgst": clean_nan(r.get("cgst", 0)),
                "sgst": clean_nan(r.get("sgst", 0)),
                "igst": clean_nan(r.get("igst", 0)),
                "total_tax": tax,
                "total_value": clean_nan(r.get("total_value", 0)) + tax
            })
        
        return {
            "status": "success",
            "period": {
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            },
            "hsn_data": hsn_data,
            "summary": {
                "total_items": len(hsn_data),
                "total_quantity": sum(h["quantity"] for h in hsn_data),
                "total_taxable_value": sum(h["taxable_value"] for h in hsn_data),
                "total_tax": sum(h["total_tax"] for h in hsn_data),
                "total_value": sum(h["total_value"] for h in hsn_data)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting HSN-wise report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ GSTR-2B (Auto-drafted ITC from Suppliers) ============

@router.get("/gst/gstr2b")
async def get_gstr2b_report(
    period: str = "this_month",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """
    Generate GSTR-2B Report (Auto-drafted ITC Statement)
    Based on supplier invoices in purchase_bills collection
    Groups by supplier GSTIN for ITC reconciliation
    """
    try:
        start_date, end_date = get_date_range(period, from_date, to_date)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Get purchase bills grouped by supplier GSTIN
        supplier_pipeline = [
            {"$match": {
                "bill_date": {"$gte": start_str, "$lte": end_str}
            }},
            {"$group": {
                "_id": {"$ifNull": ["$vendor.gst_number", "$vendor_gst"]},
                "supplier_name": {"$first": {"$ifNull": ["$vendor.name", "$vendor_name"]}},
                "supplier_state": {"$first": {"$ifNull": ["$vendor.state", ""]}},
                "taxable_value": {"$sum": "$subtotal"},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "total_tax": {"$sum": {"$ifNull": ["$total_tax", 0]}},
                "invoice_count": {"$sum": 1},
                "total_value": {"$sum": "$grand_total"},
                "invoices": {"$push": {
                    "invoice_no": "$bill_number",
                    "invoice_date": "$bill_date",
                    "taxable_value": "$subtotal",
                    "tax_amount": "$total_tax",
                    "total": "$grand_total"
                }}
            }},
            {"$sort": {"total_value": -1}}
        ]
        
        supplier_result = await db.purchase_bills.aggregate(supplier_pipeline).to_list(None)
        
        # Categorize by supply type
        b2b_supplies = []  # Supplies from registered suppliers
        b2b_reverse_charge = []  # Reverse charge supplies
        import_supplies = []  # Import of goods/services
        
        for supplier in supplier_result:
            gstin = supplier["_id"]
            supply_data = {
                "gstin": gstin or "Unregistered",
                "supplier_name": supplier.get("supplier_name", ""),
                "supplier_state": supplier.get("supplier_state", ""),
                "taxable_value": clean_nan(supplier.get("taxable_value", 0)),
                "cgst": clean_nan(supplier.get("cgst", 0)),
                "sgst": clean_nan(supplier.get("sgst", 0)),
                "igst": clean_nan(supplier.get("igst", 0)),
                "total_itc": clean_nan(supplier.get("total_tax", 0)),
                "invoice_count": supplier.get("invoice_count", 0),
                "total_value": clean_nan(supplier.get("total_value", 0)),
                "invoices": supplier.get("invoices", [])[:5]  # Limit to 5 for response size
            }
            
            if gstin and len(gstin) == 15:  # Valid GSTIN
                b2b_supplies.append(supply_data)
            else:
                # Could be unregistered or import
                b2b_supplies.append(supply_data)
        
        # Calculate ITC summary
        total_itc = {
            "cgst": sum(clean_nan(s.get("cgst", 0)) for s in b2b_supplies),
            "sgst": sum(clean_nan(s.get("sgst", 0)) for s in b2b_supplies),
            "igst": sum(clean_nan(s.get("igst", 0)) for s in b2b_supplies),
            "total": sum(clean_nan(s.get("total_itc", 0)) for s in b2b_supplies)
        }
        
        return {
            "status": "success",
            "report_type": "GSTR-2B",
            "period": {
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            },
            "b2b_supplies": {
                "details": b2b_supplies,
                "summary": {
                    "supplier_count": len(b2b_supplies),
                    "invoice_count": sum(s.get("invoice_count", 0) for s in b2b_supplies),
                    "total_taxable_value": sum(clean_nan(s.get("taxable_value", 0)) for s in b2b_supplies),
                    "total_itc": total_itc
                }
            },
            "itc_summary": {
                "available_itc": total_itc,
                "ineligible_itc": {"cgst": 0, "sgst": 0, "igst": 0, "total": 0},
                "net_itc": total_itc
            },
            "reconciliation": {
                "matched_invoices": sum(s.get("invoice_count", 0) for s in b2b_supplies),
                "pending_reconciliation": 0,
                "action_required": []
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating GSTR-2B: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ TAX SLAB ANALYSIS ============

@router.get("/gst/tax-slabs")
async def get_tax_slab_analysis(
    period: str = "this_month",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    report_type: str = "both",  # sales, purchases, or both
    db = Depends(get_db)
):
    """
    Analyze sales and purchases by GST tax slabs (0%, 5%, 12%, 18%, 28%)
    """
    try:
        start_date, end_date = get_date_range(period, from_date, to_date)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Define tax slabs
        tax_slabs = [0, 5, 12, 18, 28]
        
        result = {
            "status": "success",
            "period": {
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            }
        }
        
        # Sales by tax slab
        if report_type in ["sales", "both"]:
            sales_by_slab = {}
            for slab in tax_slabs:
                # Match orders with this tax rate (with tolerance)
                slab_pipeline = [
                    {"$match": {
                        "$or": [
                            {"created_at": {"$gte": start_date, "$lte": end_date}},
                            {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}}
                        ]
                    }},
                    {"$unwind": {"path": "$items", "preserveNullAndEmptyArrays": True}},
                    {"$match": {
                        "$or": [
                            {"items.gst_rate": {"$gte": slab - 0.5, "$lte": slab + 0.5}},
                            {"items.tax_rate": {"$gte": slab - 0.5, "$lte": slab + 0.5}},
                            {"gst_rate": {"$gte": slab - 0.5, "$lte": slab + 0.5}}
                        ]
                    }},
                    {"$group": {
                        "_id": None,
                        "taxable_value": {"$sum": {"$ifNull": ["$items.price", "$subtotal"]}},
                        "tax_amount": {"$sum": {"$ifNull": ["$items.tax_amount", 0]}},
                        "count": {"$sum": 1}
                    }}
                ]
                
                slab_result = await db.orders.aggregate(slab_pipeline).to_list(1)
                slab_data = slab_result[0] if slab_result else {"taxable_value": 0, "tax_amount": 0, "count": 0}
                
                tax_amount = clean_nan(slab_data.get("tax_amount", 0))
                if tax_amount == 0 and slab > 0:
                    # Calculate tax from taxable value if not stored
                    taxable = clean_nan(slab_data.get("taxable_value", 0))
                    tax_amount = taxable * (slab / 100)
                
                sales_by_slab[f"{slab}%"] = {
                    "slab_rate": slab,
                    "taxable_value": clean_nan(slab_data.get("taxable_value", 0)),
                    "cgst": tax_amount / 2 if slab > 0 else 0,
                    "sgst": tax_amount / 2 if slab > 0 else 0,
                    "igst": 0,
                    "total_tax": tax_amount,
                    "invoice_count": slab_data.get("count", 0)
                }
            
            # Also get unclassified (where tax rate is not in standard slabs)
            result["sales_by_tax_slab"] = sales_by_slab
        
        # Purchases by tax slab
        if report_type in ["purchases", "both"]:
            purchases_by_slab = {}
            for slab in tax_slabs:
                slab_pipeline = [
                    {"$match": {
                        "bill_date": {"$gte": start_str, "$lte": end_str}
                    }},
                    {"$unwind": {"path": "$items", "preserveNullAndEmptyArrays": True}},
                    {"$match": {
                        "items.tax_rate": {"$gte": slab - 0.5, "$lte": slab + 0.5}
                    }},
                    {"$group": {
                        "_id": None,
                        "taxable_value": {"$sum": {"$ifNull": ["$items.taxable_amount", 0]}},
                        "tax_amount": {"$sum": {"$ifNull": ["$items.tax_amount", 0]}},
                        "cgst": {"$sum": {"$ifNull": ["$items.cgst", 0]}},
                        "sgst": {"$sum": {"$ifNull": ["$items.sgst", 0]}},
                        "igst": {"$sum": {"$ifNull": ["$items.igst", 0]}},
                        "count": {"$sum": 1}
                    }}
                ]
                
                slab_result = await db.purchase_bills.aggregate(slab_pipeline).to_list(1)
                slab_data = slab_result[0] if slab_result else {}
                
                purchases_by_slab[f"{slab}%"] = {
                    "slab_rate": slab,
                    "taxable_value": clean_nan(slab_data.get("taxable_value", 0)),
                    "cgst": clean_nan(slab_data.get("cgst", 0)),
                    "sgst": clean_nan(slab_data.get("sgst", 0)),
                    "igst": clean_nan(slab_data.get("igst", 0)),
                    "total_itc": clean_nan(slab_data.get("tax_amount", 0)),
                    "bill_count": slab_data.get("count", 0)
                }
            
            result["purchases_by_tax_slab"] = purchases_by_slab
        
        # Summary
        if report_type == "both":
            result["net_tax_by_slab"] = {}
            for slab in tax_slabs:
                key = f"{slab}%"
                sales_tax = result.get("sales_by_tax_slab", {}).get(key, {}).get("total_tax", 0)
                purchase_itc = result.get("purchases_by_tax_slab", {}).get(key, {}).get("total_itc", 0)
                result["net_tax_by_slab"][key] = {
                    "output_tax": clean_nan(sales_tax),
                    "input_tax_credit": clean_nan(purchase_itc),
                    "net_payable": max(0, clean_nan(sales_tax) - clean_nan(purchase_itc))
                }
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting tax slab analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ B2B vs B2C ANALYSIS ============

@router.get("/gst/b2b-b2c-analysis")
async def get_b2b_b2c_analysis(
    period: str = "this_month",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """
    Detailed B2B vs B2C sales and purchase analysis
    B2B: Transactions with GSTIN
    B2C: Transactions without GSTIN
    """
    try:
        start_date, end_date = get_date_range(period, from_date, to_date)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # ===== SALES ANALYSIS =====
        
        # B2B Sales (with customer GSTIN)
        b2b_sales_pipeline = [
            {"$match": {
                "$or": [
                    {"created_at": {"$gte": start_date, "$lte": end_date}},
                    {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}}
                ],
                "customer_gstin": {"$exists": True, "$nin": ["", None]}
            }},
            {"$group": {
                "_id": None,
                "taxable_value": {"$sum": "$subtotal"},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "total_tax": {"$sum": {"$ifNull": ["$gst_amount", {"$ifNull": ["$tax_amount", 0]}]}},
                "total_value": {"$sum": "$total_amount"},
                "invoice_count": {"$sum": 1}
            }}
        ]
        b2b_sales_result = await db.orders.aggregate(b2b_sales_pipeline).to_list(1)
        b2b_sales = b2b_sales_result[0] if b2b_sales_result else {}
        
        # B2C Sales (without customer GSTIN)
        b2c_sales_pipeline = [
            {"$match": {
                "$and": [
                    {"$or": [
                        {"created_at": {"$gte": start_date, "$lte": end_date}},
                        {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}}
                    ]},
                    {"$or": [
                        {"customer_gstin": {"$exists": False}},
                        {"customer_gstin": ""},
                        {"customer_gstin": None}
                    ]}
                ]
            }},
            {"$group": {
                "_id": {"$ifNull": ["$shipping_address.state", "$customer_state"]},
                "taxable_value": {"$sum": "$subtotal"},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "total_tax": {"$sum": {"$ifNull": ["$gst_amount", {"$ifNull": ["$tax_amount", 0]}]}},
                "total_value": {"$sum": "$total_amount"},
                "invoice_count": {"$sum": 1}
            }}
        ]
        b2c_sales_result = await db.orders.aggregate(b2c_sales_pipeline).to_list(None)
        
        # Aggregate B2C by state
        b2c_by_state = []
        b2c_total = {"taxable_value": 0, "cgst": 0, "sgst": 0, "igst": 0, "total_tax": 0, "total_value": 0, "invoice_count": 0}
        for state_data in b2c_sales_result:
            state_entry = {
                "place_of_supply": state_data["_id"] or "Unknown",
                "taxable_value": clean_nan(state_data.get("taxable_value", 0)),
                "cgst": clean_nan(state_data.get("cgst", 0)),
                "sgst": clean_nan(state_data.get("sgst", 0)),
                "igst": clean_nan(state_data.get("igst", 0)),
                "total_tax": clean_nan(state_data.get("total_tax", 0)),
                "total_value": clean_nan(state_data.get("total_value", 0)),
                "invoice_count": state_data.get("invoice_count", 0)
            }
            b2c_by_state.append(state_entry)
            for key in b2c_total:
                if key != "place_of_supply":
                    b2c_total[key] += state_entry.get(key, 0)
        
        # ===== PURCHASE ANALYSIS =====
        
        # B2B Purchases (from registered vendors)
        b2b_purchase_pipeline = [
            {"$match": {
                "bill_date": {"$gte": start_str, "$lte": end_str},
                "$or": [
                    {"vendor.gst_number": {"$exists": True, "$nin": ["", None]}},
                    {"vendor_gst": {"$exists": True, "$nin": ["", None]}}
                ]
            }},
            {"$group": {
                "_id": None,
                "taxable_value": {"$sum": "$subtotal"},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "total_tax": {"$sum": {"$ifNull": ["$total_tax", 0]}},
                "total_value": {"$sum": "$grand_total"},
                "bill_count": {"$sum": 1}
            }}
        ]
        b2b_purchase_result = await db.purchase_bills.aggregate(b2b_purchase_pipeline).to_list(1)
        b2b_purchases = b2b_purchase_result[0] if b2b_purchase_result else {}
        
        # Unregistered vendor purchases
        unreg_purchase_pipeline = [
            {"$match": {
                "bill_date": {"$gte": start_str, "$lte": end_str},
                "$and": [
                    {"$or": [
                        {"vendor.gst_number": {"$exists": False}},
                        {"vendor.gst_number": ""},
                        {"vendor.gst_number": None}
                    ]},
                    {"$or": [
                        {"vendor_gst": {"$exists": False}},
                        {"vendor_gst": ""},
                        {"vendor_gst": None}
                    ]}
                ]
            }},
            {"$group": {
                "_id": None,
                "taxable_value": {"$sum": "$subtotal"},
                "total_value": {"$sum": "$grand_total"},
                "bill_count": {"$sum": 1}
            }}
        ]
        unreg_purchase_result = await db.purchase_bills.aggregate(unreg_purchase_pipeline).to_list(1)
        unreg_purchases = unreg_purchase_result[0] if unreg_purchase_result else {}
        
        return {
            "status": "success",
            "period": {
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            },
            "sales": {
                "b2b": {
                    "description": "Sales to registered businesses (with GSTIN)",
                    "taxable_value": clean_nan(b2b_sales.get("taxable_value", 0)),
                    "cgst": clean_nan(b2b_sales.get("cgst", 0)),
                    "sgst": clean_nan(b2b_sales.get("sgst", 0)),
                    "igst": clean_nan(b2b_sales.get("igst", 0)),
                    "total_tax": clean_nan(b2b_sales.get("total_tax", 0)),
                    "total_value": clean_nan(b2b_sales.get("total_value", 0)),
                    "invoice_count": b2b_sales.get("invoice_count", 0)
                },
                "b2c": {
                    "description": "Sales to consumers (without GSTIN)",
                    "by_state": b2c_by_state,
                    "summary": b2c_total
                },
                "total": {
                    "taxable_value": clean_nan(b2b_sales.get("taxable_value", 0)) + b2c_total["taxable_value"],
                    "total_tax": clean_nan(b2b_sales.get("total_tax", 0)) + b2c_total["total_tax"],
                    "total_value": clean_nan(b2b_sales.get("total_value", 0)) + b2c_total["total_value"],
                    "invoice_count": b2b_sales.get("invoice_count", 0) + b2c_total["invoice_count"]
                }
            },
            "purchases": {
                "b2b": {
                    "description": "Purchases from registered vendors (ITC eligible)",
                    "taxable_value": clean_nan(b2b_purchases.get("taxable_value", 0)),
                    "cgst": clean_nan(b2b_purchases.get("cgst", 0)),
                    "sgst": clean_nan(b2b_purchases.get("sgst", 0)),
                    "igst": clean_nan(b2b_purchases.get("igst", 0)),
                    "itc_available": clean_nan(b2b_purchases.get("total_tax", 0)),
                    "total_value": clean_nan(b2b_purchases.get("total_value", 0)),
                    "bill_count": b2b_purchases.get("bill_count", 0)
                },
                "unregistered": {
                    "description": "Purchases from unregistered vendors (no ITC)",
                    "taxable_value": clean_nan(unreg_purchases.get("taxable_value", 0)),
                    "total_value": clean_nan(unreg_purchases.get("total_value", 0)),
                    "bill_count": unreg_purchases.get("bill_count", 0)
                }
            },
            "gst_summary": {
                "output_tax": {
                    "cgst": clean_nan(b2b_sales.get("cgst", 0)) + b2c_total["cgst"],
                    "sgst": clean_nan(b2b_sales.get("sgst", 0)) + b2c_total["sgst"],
                    "igst": clean_nan(b2b_sales.get("igst", 0)) + b2c_total["igst"],
                    "total": clean_nan(b2b_sales.get("total_tax", 0)) + b2c_total["total_tax"]
                },
                "input_tax_credit": {
                    "cgst": clean_nan(b2b_purchases.get("cgst", 0)),
                    "sgst": clean_nan(b2b_purchases.get("sgst", 0)),
                    "igst": clean_nan(b2b_purchases.get("igst", 0)),
                    "total": clean_nan(b2b_purchases.get("total_tax", 0))
                },
                "net_payable": {
                    "cgst": max(0, (clean_nan(b2b_sales.get("cgst", 0)) + b2c_total["cgst"]) - clean_nan(b2b_purchases.get("cgst", 0))),
                    "sgst": max(0, (clean_nan(b2b_sales.get("sgst", 0)) + b2c_total["sgst"]) - clean_nan(b2b_purchases.get("sgst", 0))),
                    "igst": max(0, (clean_nan(b2b_sales.get("igst", 0)) + b2c_total["igst"]) - clean_nan(b2b_purchases.get("igst", 0))),
                    "total": max(0, (clean_nan(b2b_sales.get("total_tax", 0)) + b2c_total["total_tax"]) - clean_nan(b2b_purchases.get("total_tax", 0)))
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting B2B/B2C analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ TAX BIFURCATION (CGST/SGST/IGST) ============

@router.get("/gst/tax-bifurcation")
async def get_tax_bifurcation(
    period: str = "this_month",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """
    Detailed tax bifurcation report showing CGST, SGST, IGST breakdown
    For intra-state (same state): CGST + SGST
    For inter-state (different states): IGST
    """
    try:
        start_date, end_date = get_date_range(period, from_date, to_date)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Business state (default to Karnataka for this business)
        business_state = "KARNATAKA"
        
        # ===== SALES TAX BIFURCATION =====
        
        # Intra-state sales (CGST + SGST)
        intra_sales_pipeline = [
            {"$match": {
                "$and": [
                    {"$or": [
                        {"created_at": {"$gte": start_date, "$lte": end_date}},
                        {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}}
                    ]},
                    {"$or": [
                        {"shipping_address.state": {"$regex": f"^{business_state}$", "$options": "i"}},
                        {"customer_state": {"$regex": f"^{business_state}$", "$options": "i"}},
                        {"shipping_address.state": {"$regex": "^KA$", "$options": "i"}},
                        {"shipping_address.state": {"$exists": False}}
                    ]}
                ]
            }},
            {"$group": {
                "_id": None,
                "taxable_value": {"$sum": "$subtotal"},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "total_tax": {"$sum": {"$ifNull": ["$gst_amount", {"$ifNull": ["$tax_amount", 0]}]}},
                "total_value": {"$sum": "$total_amount"},
                "invoice_count": {"$sum": 1}
            }}
        ]
        intra_sales_result = await db.orders.aggregate(intra_sales_pipeline).to_list(1)
        intra_sales = intra_sales_result[0] if intra_sales_result else {}
        
        # Inter-state sales (IGST)
        inter_sales_pipeline = [
            {"$match": {
                "$or": [
                    {"created_at": {"$gte": start_date, "$lte": end_date}},
                    {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}}
                ],
                "$and": [
                    {"shipping_address.state": {"$exists": True, "$nin": ["", None]}},
                    {"shipping_address.state": {"$not": {"$regex": f"^{business_state}$", "$options": "i"}}},
                    {"shipping_address.state": {"$not": {"$regex": "^KA$", "$options": "i"}}}
                ]
            }},
            {"$group": {
                "_id": "$shipping_address.state",
                "taxable_value": {"$sum": "$subtotal"},
                "igst": {"$sum": {"$ifNull": ["$igst", {"$ifNull": ["$gst_amount", 0]}]}},
                "total_value": {"$sum": "$total_amount"},
                "invoice_count": {"$sum": 1}
            }}
        ]
        inter_sales_result = await db.orders.aggregate(inter_sales_pipeline).to_list(None)
        
        inter_sales_by_state = []
        inter_sales_total = {"taxable_value": 0, "igst": 0, "total_value": 0, "invoice_count": 0}
        for state_data in inter_sales_result:
            entry = {
                "state": state_data["_id"],
                "taxable_value": clean_nan(state_data.get("taxable_value", 0)),
                "igst": clean_nan(state_data.get("igst", 0)),
                "total_value": clean_nan(state_data.get("total_value", 0)),
                "invoice_count": state_data.get("invoice_count", 0)
            }
            inter_sales_by_state.append(entry)
            for key in ["taxable_value", "igst", "total_value", "invoice_count"]:
                inter_sales_total[key] += entry[key]
        
        # ===== PURCHASE TAX BIFURCATION =====
        
        # Intra-state purchases
        intra_purchase_pipeline = [
            {"$match": {
                "bill_date": {"$gte": start_str, "$lte": end_str},
                "$or": [
                    {"vendor.state": {"$regex": f"^{business_state}$", "$options": "i"}},
                    {"vendor.state": {"$regex": "^KA$", "$options": "i"}},
                    {"vendor.state": {"$exists": False}}
                ]
            }},
            {"$group": {
                "_id": None,
                "taxable_value": {"$sum": "$subtotal"},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "total_tax": {"$sum": {"$ifNull": ["$total_tax", 0]}},
                "total_value": {"$sum": "$grand_total"},
                "bill_count": {"$sum": 1}
            }}
        ]
        intra_purchase_result = await db.purchase_bills.aggregate(intra_purchase_pipeline).to_list(1)
        intra_purchases = intra_purchase_result[0] if intra_purchase_result else {}
        
        # Inter-state purchases
        inter_purchase_pipeline = [
            {"$match": {
                "bill_date": {"$gte": start_str, "$lte": end_str},
                "$and": [
                    {"vendor.state": {"$exists": True, "$nin": ["", None]}},
                    {"vendor.state": {"$not": {"$regex": f"^{business_state}$", "$options": "i"}}},
                    {"vendor.state": {"$not": {"$regex": "^KA$", "$options": "i"}}}
                ]
            }},
            {"$group": {
                "_id": "$vendor.state",
                "taxable_value": {"$sum": "$subtotal"},
                "igst": {"$sum": {"$ifNull": ["$igst", {"$ifNull": ["$total_tax", 0]}]}},
                "total_value": {"$sum": "$grand_total"},
                "bill_count": {"$sum": 1}
            }}
        ]
        inter_purchase_result = await db.purchase_bills.aggregate(inter_purchase_pipeline).to_list(None)
        
        inter_purchases_by_state = []
        inter_purchases_total = {"taxable_value": 0, "igst": 0, "total_value": 0, "bill_count": 0}
        for state_data in inter_purchase_result:
            entry = {
                "state": state_data["_id"],
                "taxable_value": clean_nan(state_data.get("taxable_value", 0)),
                "igst": clean_nan(state_data.get("igst", 0)),
                "total_value": clean_nan(state_data.get("total_value", 0)),
                "bill_count": state_data.get("bill_count", 0)
            }
            inter_purchases_by_state.append(entry)
            for key in ["taxable_value", "igst", "total_value", "bill_count"]:
                inter_purchases_total[key] += entry[key]
        
        # Calculate if CGST/SGST not stored, estimate from total tax (online orders only)
        intra_sales_tax = clean_nan(intra_sales.get("total_tax", 0))
        intra_sales_cgst = clean_nan(intra_sales.get("cgst", 0)) or (intra_sales_tax / 2)
        intra_sales_sgst = clean_nan(intra_sales.get("sgst", 0)) or (intra_sales_tax / 2)

        intra_purchase_tax = clean_nan(intra_purchases.get("total_tax", 0))
        intra_purchase_cgst = clean_nan(intra_purchases.get("cgst", 0)) or (intra_purchase_tax / 2)
        intra_purchase_sgst = clean_nan(intra_purchases.get("sgst", 0)) or (intra_purchase_tax / 2)

        # ===== OFFLINE INVOICES bifurcation =====
        offline_data = await get_offline_invoice_data(db, start_date, end_date)
        offline_intra_cgst = clean_nan(offline_data["cgst"])
        offline_intra_sgst = clean_nan(offline_data["sgst"])
        offline_inter_igst = clean_nan(offline_data["igst"])
        offline_taxable = clean_nan(offline_data["taxable_value"])
        offline_total_value = clean_nan(offline_data["total_amount"])
        offline_count = offline_data["count"]

        # Add offline values to running totals
        intra_sales_cgst += offline_intra_cgst
        intra_sales_sgst += offline_intra_sgst
        intra_sales_tax = intra_sales_cgst + intra_sales_sgst  # recompute from finalised parts
        inter_sales_total["igst"] = clean_nan(inter_sales_total.get("igst", 0)) + offline_inter_igst
        
        return {
            "status": "success",
            "period": {
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            },
            "business_state": business_state,
            "sales": {
                "intra_state": {
                    "description": f"Sales within {business_state} (CGST + SGST) — includes online + offline",
                    "taxable_value": clean_nan(intra_sales.get("taxable_value", 0)) + offline_taxable,
                    "cgst": intra_sales_cgst,
                    "sgst": intra_sales_sgst,
                    "total_tax": intra_sales_tax,
                    "total_value": clean_nan(intra_sales.get("total_value", 0)) + offline_total_value,
                    "invoice_count": intra_sales.get("invoice_count", 0) + offline_count,
                    "online_count": intra_sales.get("invoice_count", 0),
                    "offline_count": offline_count
                },
                "inter_state": {
                    "description": "Sales to other states (IGST)",
                    "by_state": inter_sales_by_state,
                    "summary": {
                        "taxable_value": inter_sales_total["taxable_value"],
                        "igst": inter_sales_total["igst"],
                        "total_value": inter_sales_total["total_value"],
                        "invoice_count": inter_sales_total["invoice_count"]
                    }
                }
            },
            "purchases": {
                "intra_state": {
                    "description": f"Purchases within {business_state} (CGST + SGST ITC)",
                    "taxable_value": clean_nan(intra_purchases.get("taxable_value", 0)),
                    "cgst_itc": intra_purchase_cgst,
                    "sgst_itc": intra_purchase_sgst,
                    "total_itc": intra_purchase_tax,
                    "total_value": clean_nan(intra_purchases.get("total_value", 0)),
                    "bill_count": intra_purchases.get("bill_count", 0)
                },
                "inter_state": {
                    "description": "Purchases from other states (IGST ITC)",
                    "by_state": inter_purchases_by_state,
                    "summary": {
                        "taxable_value": inter_purchases_total["taxable_value"],
                        "igst_itc": inter_purchases_total["igst"],
                        "total_value": inter_purchases_total["total_value"],
                        "bill_count": inter_purchases_total["bill_count"]
                    }
                }
            },
            "tax_summary": {
                "output_tax": {
                    "cgst": intra_sales_cgst,
                    "sgst": intra_sales_sgst,
                    "igst": inter_sales_total["igst"],
                    "total": intra_sales_tax + inter_sales_total["igst"]
                },
                "input_tax_credit": {
                    "cgst": intra_purchase_cgst,
                    "sgst": intra_purchase_sgst,
                    "igst": inter_purchases_total["igst"],
                    "total": intra_purchase_tax + inter_purchases_total["igst"]
                },
                "net_payable": {
                    "cgst": max(0, intra_sales_cgst - intra_purchase_cgst),
                    "sgst": max(0, intra_sales_sgst - intra_purchase_sgst),
                    "igst": max(0, inter_sales_total["igst"] - inter_purchases_total["igst"]),
                    "total": max(0, (intra_sales_tax + inter_sales_total["igst"]) - (intra_purchase_tax + inter_purchases_total["igst"]))
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting tax bifurcation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ GSTR-9 ANNUAL RETURN ============

@router.get("/gst/gstr9")
async def get_gstr9_annual_return(
    financial_year: str = "2025-26",
    db = Depends(get_db)
):
    """
    Generate GSTR-9 Annual Return
    Comprehensive annual summary of all GST transactions
    """
    try:
        # Parse financial year (e.g., "2025-26")
        fy_parts = financial_year.split("-")
        start_year = int(fy_parts[0])
        
        # Financial year: April 1 to March 31
        start_date = datetime(start_year, 4, 1, tzinfo=timezone.utc)
        end_date = datetime(start_year + 1, 3, 31, 23, 59, 59, tzinfo=timezone.utc)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Part I - Basic Details (to be filled by user)
        
        # Part II - Outward Supplies
        outward_pipeline = [
            {"$match": {
                "$or": [
                    {"created_at": {"$gte": start_date, "$lte": end_date}},
                    {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}}
                ]
            }},
            {"$group": {
                "_id": None,
                "total_taxable_value": {"$sum": "$subtotal"},
                "total_cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "total_sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "total_igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "total_cess": {"$sum": {"$ifNull": ["$cess", 0]}},
                "total_value": {"$sum": "$total_amount"},
                "invoice_count": {"$sum": 1}
            }}
        ]
        outward_result = await db.orders.aggregate(outward_pipeline).to_list(1)
        outward_supplies = outward_result[0] if outward_result else {}
        
        # B2B Outward Supplies
        b2b_outward_pipeline = [
            {"$match": {
                "$or": [
                    {"created_at": {"$gte": start_date, "$lte": end_date}},
                    {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}}
                ],
                "customer_gstin": {"$exists": True, "$nin": ["", None]}
            }},
            {"$group": {
                "_id": None,
                "taxable_value": {"$sum": "$subtotal"},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "invoice_count": {"$sum": 1}
            }}
        ]
        b2b_outward_result = await db.orders.aggregate(b2b_outward_pipeline).to_list(1)
        b2b_outward = b2b_outward_result[0] if b2b_outward_result else {}
        
        # B2C Outward Supplies
        b2c_outward_pipeline = [
            {"$match": {
                "$and": [
                    {"$or": [
                        {"created_at": {"$gte": start_date, "$lte": end_date}},
                        {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}}
                    ]},
                    {"$or": [
                        {"customer_gstin": {"$exists": False}},
                        {"customer_gstin": ""},
                        {"customer_gstin": None}
                    ]}
                ]
            }},
            {"$group": {
                "_id": None,
                "taxable_value": {"$sum": "$subtotal"},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "invoice_count": {"$sum": 1}
            }}
        ]
        b2c_outward_result = await db.orders.aggregate(b2c_outward_pipeline).to_list(1)
        b2c_outward = b2c_outward_result[0] if b2c_outward_result else {}
        
        # Part III - Inward Supplies (ITC)
        inward_pipeline = [
            {"$match": {
                "bill_date": {"$gte": start_str, "$lte": end_str}
            }},
            {"$group": {
                "_id": None,
                "total_taxable_value": {"$sum": "$subtotal"},
                "total_cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "total_sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "total_igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "total_cess": {"$sum": {"$ifNull": ["$cess", 0]}},
                "total_value": {"$sum": "$grand_total"},
                "bill_count": {"$sum": 1}
            }}
        ]
        inward_result = await db.purchase_bills.aggregate(inward_pipeline).to_list(1)
        inward_supplies = inward_result[0] if inward_result else {}
        
        # ITC Claimed
        itc_claimed = {
            "cgst": clean_nan(inward_supplies.get("total_cgst", 0)),
            "sgst": clean_nan(inward_supplies.get("total_sgst", 0)),
            "igst": clean_nan(inward_supplies.get("total_igst", 0)),
            "cess": clean_nan(inward_supplies.get("total_cess", 0)),
            "total": clean_nan(inward_supplies.get("total_cgst", 0)) + clean_nan(inward_supplies.get("total_sgst", 0)) + clean_nan(inward_supplies.get("total_igst", 0))
        }
        
        # Part IV - Tax Paid
        output_tax = {
            "cgst": clean_nan(outward_supplies.get("total_cgst", 0)),
            "sgst": clean_nan(outward_supplies.get("total_sgst", 0)),
            "igst": clean_nan(outward_supplies.get("total_igst", 0)),
            "cess": clean_nan(outward_supplies.get("total_cess", 0)),
            "total": clean_nan(outward_supplies.get("total_cgst", 0)) + clean_nan(outward_supplies.get("total_sgst", 0)) + clean_nan(outward_supplies.get("total_igst", 0))
        }
        
        net_tax_liability = {
            "cgst": max(0, output_tax["cgst"] - itc_claimed["cgst"]),
            "sgst": max(0, output_tax["sgst"] - itc_claimed["sgst"]),
            "igst": max(0, output_tax["igst"] - itc_claimed["igst"]),
            "cess": max(0, output_tax["cess"] - itc_claimed["cess"]),
            "total": max(0, output_tax["total"] - itc_claimed["total"])
        }
        
        # Monthly breakdown for Part V
        monthly_data = []
        for month in range(4, 13):  # April to December
            month_start = datetime(start_year, month, 1, tzinfo=timezone.utc)
            if month == 12:
                month_end = datetime(start_year + 1, 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
            else:
                month_end = datetime(start_year, month + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
            
            month_str_start = month_start.strftime("%Y-%m-%d")
            month_str_end = month_end.strftime("%Y-%m-%d")
            
            # Get monthly sales
            monthly_sales = await db.orders.aggregate([
                {"$match": {"$or": [
                    {"created_at": {"$gte": month_start, "$lte": month_end}},
                    {"created_at": {"$gte": month_str_start, "$lte": month_str_end + "T23:59:59"}}
                ]}},
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}, "tax": {"$sum": {"$ifNull": ["$gst_amount", 0]}}}}
            ]).to_list(1)
            
            month_name = month_start.strftime("%B %Y")
            monthly_data.append({
                "month": month_name,
                "outward_supplies": clean_nan(monthly_sales[0]["total"]) if monthly_sales else 0,
                "output_tax": clean_nan(monthly_sales[0]["tax"]) if monthly_sales else 0
            })
        
        # January to March of next year
        for month in range(1, 4):
            month_start = datetime(start_year + 1, month, 1, tzinfo=timezone.utc)
            if month == 3:
                month_end = datetime(start_year + 1, 4, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
            else:
                month_end = datetime(start_year + 1, month + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
            
            month_str_start = month_start.strftime("%Y-%m-%d")
            month_str_end = month_end.strftime("%Y-%m-%d")
            
            monthly_sales = await db.orders.aggregate([
                {"$match": {"$or": [
                    {"created_at": {"$gte": month_start, "$lte": month_end}},
                    {"created_at": {"$gte": month_str_start, "$lte": month_str_end + "T23:59:59"}}
                ]}},
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}, "tax": {"$sum": {"$ifNull": ["$gst_amount", 0]}}}}
            ]).to_list(1)
            
            month_name = month_start.strftime("%B %Y")
            monthly_data.append({
                "month": month_name,
                "outward_supplies": clean_nan(monthly_sales[0]["total"]) if monthly_sales else 0,
                "output_tax": clean_nan(monthly_sales[0]["tax"]) if monthly_sales else 0
            })
        
        return {
            "status": "success",
            "report_type": "GSTR-9",
            "financial_year": financial_year,
            "period": {
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            },
            "part_ii_outward_supplies": {
                "b2b": {
                    "taxable_value": clean_nan(b2b_outward.get("taxable_value", 0)),
                    "cgst": clean_nan(b2b_outward.get("cgst", 0)),
                    "sgst": clean_nan(b2b_outward.get("sgst", 0)),
                    "igst": clean_nan(b2b_outward.get("igst", 0)),
                    "invoice_count": b2b_outward.get("invoice_count", 0)
                },
                "b2c": {
                    "taxable_value": clean_nan(b2c_outward.get("taxable_value", 0)),
                    "cgst": clean_nan(b2c_outward.get("cgst", 0)),
                    "sgst": clean_nan(b2c_outward.get("sgst", 0)),
                    "igst": clean_nan(b2c_outward.get("igst", 0)),
                    "invoice_count": b2c_outward.get("invoice_count", 0)
                },
                "total": {
                    "taxable_value": clean_nan(outward_supplies.get("total_taxable_value", 0)),
                    "cgst": clean_nan(outward_supplies.get("total_cgst", 0)),
                    "sgst": clean_nan(outward_supplies.get("total_sgst", 0)),
                    "igst": clean_nan(outward_supplies.get("total_igst", 0)),
                    "cess": clean_nan(outward_supplies.get("total_cess", 0)),
                    "total_value": clean_nan(outward_supplies.get("total_value", 0)),
                    "invoice_count": outward_supplies.get("invoice_count", 0)
                }
            },
            "part_iii_inward_supplies": {
                "total": {
                    "taxable_value": clean_nan(inward_supplies.get("total_taxable_value", 0)),
                    "cgst": clean_nan(inward_supplies.get("total_cgst", 0)),
                    "sgst": clean_nan(inward_supplies.get("total_sgst", 0)),
                    "igst": clean_nan(inward_supplies.get("total_igst", 0)),
                    "cess": clean_nan(inward_supplies.get("total_cess", 0)),
                    "total_value": clean_nan(inward_supplies.get("total_value", 0)),
                    "bill_count": inward_supplies.get("bill_count", 0)
                },
                "itc_claimed": itc_claimed
            },
            "part_iv_tax_paid": {
                "output_tax": output_tax,
                "itc_utilized": itc_claimed,
                "net_tax_liability": net_tax_liability
            },
            "part_v_monthly_breakup": monthly_data,
            "summary": {
                "total_turnover": clean_nan(outward_supplies.get("total_value", 0)),
                "total_tax_collected": output_tax["total"],
                "total_itc_claimed": itc_claimed["total"],
                "net_tax_paid": net_tax_liability["total"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating GSTR-9: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ EXCEL EXPORT - GOVERNMENT FORMAT ============

@router.get("/gst/export/gstr1")
async def export_gstr1_excel(
    period: str = "this_month",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Export GSTR-1 in Government Excel Format"""
    try:
        start_date, end_date = get_date_range(period, from_date, to_date)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Get B2B invoices
        b2b_invoices = await db.orders.find({
            "$or": [
                {"created_at": {"$gte": start_date, "$lte": end_date}},
                {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}}
            ],
            "customer_gstin": {"$exists": True, "$nin": ["", None]}
        }, {"_id": 0}).to_list(None)
        
        # Get B2C invoices
        b2c_invoices = await db.orders.find({
            "$and": [
                {"$or": [
                    {"created_at": {"$gte": start_date, "$lte": end_date}},
                    {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}}
                ]},
                {"$or": [
                    {"customer_gstin": {"$exists": False}},
                    {"customer_gstin": ""},
                    {"customer_gstin": None}
                ]}
            ]
        }, {"_id": 0}).to_list(None)
        
        # Create Excel file
        output = io.BytesIO()
        
        # B2B Sheet
        b2b_csv = io.StringIO()
        b2b_writer = csv.writer(b2b_csv)
        b2b_writer.writerow([
            "GSTIN/UIN of Recipient", "Receiver Name", "Invoice Number", "Invoice Date",
            "Invoice Value", "Place of Supply", "Reverse Charge", "Applicable % of Tax Rate",
            "Invoice Type", "E-Commerce GSTIN", "Rate", "Taxable Value", "Cess Amount",
            "MSME/Udyam Number"
        ])
        
        for inv in b2b_invoices:
            created_at = inv.get("created_at", "")
            if isinstance(created_at, datetime):
                inv_date = created_at.strftime("%d-%m-%Y")
            else:
                inv_date = str(created_at)[:10] if created_at else ""
            
            b2b_writer.writerow([
                inv.get("customer_gstin", ""),
                inv.get("customer_name", ""),
                inv.get("order_number", inv.get("invoice_number", "")),
                inv_date,
                inv.get("total_amount", 0),
                inv.get("shipping_address", {}).get("state", ""),
                "N",
                "",
                "Regular",
                "",
                18,  # Default GST rate
                inv.get("subtotal", 0),
                inv.get("cess", 0),
                inv.get("msme_udyam_number", inv.get("udyam_number", ""))
            ])
        
        # B2C Sheet
        b2c_csv = io.StringIO()
        b2c_writer = csv.writer(b2c_csv)
        b2c_writer.writerow([
            "Type", "Place of Supply", "Applicable % of Tax Rate", "Rate",
            "Taxable Value", "Cess Amount", "E-Commerce GSTIN"
        ])
        
        # Group B2C by state
        b2c_by_state = {}
        for inv in b2c_invoices:
            state = inv.get("shipping_address", {}).get("state", "Karnataka")
            if state not in b2c_by_state:
                b2c_by_state[state] = {"taxable": 0, "cess": 0}
            b2c_by_state[state]["taxable"] += inv.get("subtotal", 0)
            b2c_by_state[state]["cess"] += inv.get("cess", 0)
        
        for state, values in b2c_by_state.items():
            b2c_writer.writerow([
                "OE",  # Others
                state,
                "",
                18,
                values["taxable"],
                values["cess"],
                ""
            ])
        
        # Combine into single response
        combined_csv = f"=== B2B INVOICES ===\n{b2b_csv.getvalue()}\n\n=== B2C INVOICES ===\n{b2c_csv.getvalue()}"
        output.write(combined_csv.encode('utf-8'))
        output.seek(0)
        
        filename = f"GSTR1_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting GSTR-1: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gst/export/gstr2b")
async def export_gstr2b_excel(
    period: str = "this_month",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Export GSTR-2B ITC Statement in Government Format"""
    try:
        start_date, end_date = get_date_range(period, from_date, to_date)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Get purchase bills
        bills = await db.purchase_bills.find({
            "bill_date": {"$gte": start_str, "$lte": end_str}
        }, {"_id": 0}).to_list(None)
        
        output = io.BytesIO()
        csv_output = io.StringIO()
        writer = csv.writer(csv_output)
        
        # Header as per government format
        writer.writerow([
            "GSTIN of Supplier", "Trade/Legal Name", "Invoice Number", "Invoice Type",
            "Invoice Date", "Invoice Value", "Place of Supply", "Supply Attract Reverse Charge",
            "Rate", "Taxable Value", "Integrated Tax", "Central Tax", "State/UT Tax", "Cess",
            "GSTR-1/IFF/GSTR-5 Filing Period", "GSTR-1/IFF/GSTR-5 Filing Date", "ITC Availability",
            "Reason", "Applicable % of Tax Rate", "MSME/Udyam Number"
        ])
        
        for bill in bills:
            vendor = bill.get("vendor", {})
            writer.writerow([
                vendor.get("gst_number", bill.get("vendor_gst", "")),
                vendor.get("name", bill.get("vendor_name", "")),
                bill.get("bill_number", ""),
                "Regular",
                bill.get("bill_date", ""),
                bill.get("grand_total", 0),
                vendor.get("state", ""),
                "N",
                18,
                bill.get("subtotal", 0),
                bill.get("igst", 0),
                bill.get("cgst", 0),
                bill.get("sgst", 0),
                bill.get("cess", 0),
                "",
                "",
                "Yes",
                "",
                "",
                vendor.get("msme_udyam_number", bill.get("msme_udyam_number", ""))
            ])
        
        output.write(csv_output.getvalue().encode('utf-8'))
        output.seek(0)
        
        filename = f"GSTR2B_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting GSTR-2B: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gst/export/gstr9")
async def export_gstr9_excel(
    financial_year: str = "2025-26",
    db = Depends(get_db)
):
    """Export GSTR-9 Annual Return in Government Format"""
    try:
        # Get GSTR-9 data
        gstr9_data = await get_gstr9_annual_return(financial_year, db)
        
        output = io.BytesIO()
        csv_output = io.StringIO()
        writer = csv.writer(csv_output)
        
        # Part II - Outward Supplies
        writer.writerow(["=== PART II - DETAILS OF OUTWARD SUPPLIES MADE DURING THE FINANCIAL YEAR ==="])
        writer.writerow(["Description", "Taxable Value", "Central Tax", "State Tax", "Integrated Tax", "Cess"])
        
        part_ii = gstr9_data.get("part_ii_outward_supplies", {})
        writer.writerow([
            "Supplies made to registered persons (B2B)",
            part_ii.get("b2b", {}).get("taxable_value", 0),
            part_ii.get("b2b", {}).get("cgst", 0),
            part_ii.get("b2b", {}).get("sgst", 0),
            part_ii.get("b2b", {}).get("igst", 0),
            0
        ])
        writer.writerow([
            "Supplies made to unregistered persons (B2C)",
            part_ii.get("b2c", {}).get("taxable_value", 0),
            part_ii.get("b2c", {}).get("cgst", 0),
            part_ii.get("b2c", {}).get("sgst", 0),
            part_ii.get("b2c", {}).get("igst", 0),
            0
        ])
        writer.writerow([
            "Total Outward Supplies",
            part_ii.get("total", {}).get("taxable_value", 0),
            part_ii.get("total", {}).get("cgst", 0),
            part_ii.get("total", {}).get("sgst", 0),
            part_ii.get("total", {}).get("igst", 0),
            part_ii.get("total", {}).get("cess", 0)
        ])
        
        writer.writerow([])
        
        # Part III - Inward Supplies
        writer.writerow(["=== PART III - DETAILS OF ITC FOR THE FINANCIAL YEAR ==="])
        writer.writerow(["Description", "Central Tax", "State Tax", "Integrated Tax", "Cess"])
        
        part_iii = gstr9_data.get("part_iii_inward_supplies", {})
        itc = part_iii.get("itc_claimed", {})
        writer.writerow([
            "ITC Claimed",
            itc.get("cgst", 0),
            itc.get("sgst", 0),
            itc.get("igst", 0),
            itc.get("cess", 0)
        ])
        
        writer.writerow([])
        
        # Part IV - Tax Paid
        writer.writerow(["=== PART IV - DETAILS OF TAX PAID ==="])
        writer.writerow(["Description", "Central Tax", "State Tax", "Integrated Tax", "Cess"])
        
        part_iv = gstr9_data.get("part_iv_tax_paid", {})
        writer.writerow([
            "Output Tax Liability",
            part_iv.get("output_tax", {}).get("cgst", 0),
            part_iv.get("output_tax", {}).get("sgst", 0),
            part_iv.get("output_tax", {}).get("igst", 0),
            part_iv.get("output_tax", {}).get("cess", 0)
        ])
        writer.writerow([
            "ITC Utilized",
            part_iv.get("itc_utilized", {}).get("cgst", 0),
            part_iv.get("itc_utilized", {}).get("sgst", 0),
            part_iv.get("itc_utilized", {}).get("igst", 0),
            part_iv.get("itc_utilized", {}).get("cess", 0)
        ])
        writer.writerow([
            "Net Tax Payable",
            part_iv.get("net_tax_liability", {}).get("cgst", 0),
            part_iv.get("net_tax_liability", {}).get("sgst", 0),
            part_iv.get("net_tax_liability", {}).get("igst", 0),
            part_iv.get("net_tax_liability", {}).get("cess", 0)
        ])
        
        writer.writerow([])
        
        # Part V - Monthly Breakup
        writer.writerow(["=== PART V - MONTHLY BREAKUP ==="])
        writer.writerow(["Month", "Outward Supplies", "Output Tax"])
        for month_data in gstr9_data.get("part_v_monthly_breakup", []):
            writer.writerow([
                month_data.get("month", ""),
                month_data.get("outward_supplies", 0),
                month_data.get("output_tax", 0)
            ])
        
        output.write(csv_output.getvalue().encode('utf-8'))
        output.seek(0)
        
        filename = f"GSTR9_{financial_year.replace('-', '_')}.csv"
        
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting GSTR-9: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ AUDIT TRAIL ============

@router.get("/audit-trail")
async def get_audit_trail(
    limit: int = 100,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Get audit trail of financial transactions"""
    try:
        # Build query
        query = {}
        if from_date and to_date:
            from dateutil import parser
            start = parser.parse(from_date).replace(tzinfo=timezone.utc)
            end = parser.parse(to_date).replace(tzinfo=timezone.utc)
            query["timestamp"] = {"$gte": start, "$lte": end}
        
        # Get audit records
        audit_records = await db.audit_trail.find(
            query,
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit).to_list(None)
        
        # If no audit trail collection, generate from orders and purchase_bills
        if not audit_records:
            # Get recent orders
            orders = await db.orders.find(
                {},
                {"_id": 0, "order_number": 1, "total_amount": 1, "created_at": 1, "payment_status": 1}
            ).sort("created_at", -1).limit(limit // 2).to_list(None)
            
            # Get recent purchase bills
            bills = await db.purchase_bills.find(
                {},
                {"_id": 0, "bill_number": 1, "grand_total": 1, "bill_date": 1, "vendor_name": 1}
            ).sort("bill_date", -1).limit(limit // 2).to_list(None)
            
            audit_records = []
            
            for o in orders:
                audit_records.append({
                    "type": "SALE",
                    "reference": o.get("order_number", "N/A"),
                    "amount": clean_nan(o.get("total_amount", 0)),
                    "timestamp": o.get("created_at"),
                    "status": o.get("payment_status", "pending"),
                    "description": f"Sales Order {o.get('order_number', 'N/A')}"
                })
            
            for b in bills:
                audit_records.append({
                    "type": "PURCHASE",
                    "reference": b.get("bill_number", "N/A"),
                    "amount": clean_nan(b.get("grand_total", 0)),
                    "timestamp": b.get("bill_date"),
                    "vendor": b.get("vendor_name", "N/A"),
                    "description": f"Purchase from {b.get('vendor_name', 'N/A')}"
                })
            
            # Sort by timestamp (handle mixed date formats)
            audit_records.sort(key=lambda x: str(x.get("timestamp", "")), reverse=True)
        
        return {
            "status": "success",
            "records": audit_records[:limit],
            "count": len(audit_records)
        }
        
    except Exception as e:
        logger.error(f"Error getting audit trail: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ EXPORT TO CSV ============

@router.get("/export/profit-loss")
async def export_profit_loss_csv(
    period: str = "this_month",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Export P&L Statement to CSV"""
    try:
        # Get P&L data
        pl_data = await get_profit_loss_statement(period, from_date, to_date, db)
        
        if pl_data.get("status") != "success":
            raise HTTPException(status_code=500, detail="Failed to generate P&L")
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(["Profit & Loss Statement"])
        writer.writerow([f"Period: {pl_data['period']['from']} to {pl_data['period']['to']}"])
        writer.writerow([])
        
        writer.writerow(["REVENUE"])
        writer.writerow(["Online Sales", pl_data["revenue"]["online_sales"]])
        writer.writerow(["Offline Sales", pl_data["revenue"]["offline_sales"]])
        writer.writerow(["Gross Revenue", pl_data["revenue"]["gross_revenue"]])
        writer.writerow([])
        
        writer.writerow(["COST OF GOODS SOLD"])
        writer.writerow(["Purchases", pl_data["cost_of_goods_sold"]["purchases"]])
        writer.writerow([])
        
        writer.writerow(["Gross Profit", pl_data["gross_profit"]])
        writer.writerow(["Gross Margin %", f"{pl_data['gross_margin_percent']}%"])
        writer.writerow([])
        
        writer.writerow(["OPERATING EXPENSES"])
        for category, amount in pl_data["operating_expenses"]["by_category"].items():
            writer.writerow([category, amount])
        writer.writerow(["Total Operating Expenses", pl_data["operating_expenses"]["total"]])
        writer.writerow([])
        
        writer.writerow(["Operating Profit", pl_data["operating_profit"]])
        writer.writerow(["Net Profit", pl_data["net_profit"]])
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=profit_loss_{period}.csv"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ RAW DATA EXPORT ENDPOINTS ============

@router.get("/export/sales-data")
async def export_sales_data(
    from_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    format: str = Query("excel", description="Export format: excel or csv"),
    db = Depends(get_db)
):
    """
    Export raw sales/orders data for a date range
    Includes all order details with GST breakup
    """
    try:
        from dateutil import parser
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        
        start_date = parser.parse(from_date).replace(tzinfo=timezone.utc)
        end_date = parser.parse(to_date).replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
        
        # Fetch orders in date range
        date_conditions = [
            {"created_at": {"$gte": start_date, "$lte": end_date}},
            {"created_at": {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()}},
            {"created_at": {"$gte": from_date, "$lte": to_date}}
        ]
        
        orders = await db.orders.find(
            {"$or": date_conditions},
            {"_id": 0}
        ).sort("created_at", 1).to_list(length=10000)
        
        logger.info(f"Exporting {len(orders)} sales orders from {from_date} to {to_date}")
        
        if format == "csv":
            # CSV Export
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                "Invoice No", "Date", "Customer Name", "Customer Phone", "Customer GSTIN",
                "Customer State", "Product Name", "HSN Code", "Quantity", "Unit Price",
                "Taxable Amount", "CGST", "SGST", "IGST", "Total Tax", "Total Amount",
                "Payment Method", "Payment Status", "Order Status"
            ])
            
            # Data rows
            for order in orders:
                order_date = order.get('created_at', '')
                if isinstance(order_date, datetime):
                    order_date = order_date.strftime('%d-%m-%Y')
                elif isinstance(order_date, str) and 'T' in order_date:
                    try:
                        order_date = parser.parse(order_date).strftime('%d-%m-%Y')
                    except Exception:
                        pass
                
                items = order.get('items', [])
                if not items:
                    items = [{"product_name": "N/A", "hsn_code": "", "quantity": 1, "price": order.get('total_amount', 0)}]
                
                # Check if this is a Tally import (prices are exclusive)
                is_tally_import = order.get('import_source') == 'tally' or order.get('price_type') == 'exclusive'
                
                # Get customer state once (needed for CSV export)
                customer_state = order.get('shipping_address', {}).get('state', order.get('place_of_supply', 'Karnataka'))
                if not customer_state:
                    customer_state = 'Karnataka'
                
                for item in items:
                    qty = item.get('quantity', 1)
                    price = item.get('price', item.get('rate', item.get('unit_price', 0)))
                    tax_rate = item.get('tax_rate', item.get('gst_rate', 18))
                    
                    # Use pre-calculated values if available (from Tally import)
                    if item.get('taxable_amount') and item.get('tax'):
                        taxable = item.get('taxable_amount')
                        tax_amt = item.get('tax')
                        cgst = item.get('cgst', 0)
                        sgst = item.get('sgst', 0)
                        igst = item.get('igst', 0)
                        total_with_tax = taxable + tax_amt
                    elif is_tally_import or item.get('price_inclusive') == False:
                        # Price is EXCLUDING GST - use as taxable directly
                        taxable = price * qty
                        tax_amt = taxable * (tax_rate / 100)
                        total_with_tax = taxable + tax_amt
                        
                        is_inter_state = customer_state.upper() not in ['KARNATAKA', 'KA', '29']
                        
                        cgst = 0 if is_inter_state else tax_amt / 2
                        sgst = 0 if is_inter_state else tax_amt / 2
                        igst = tax_amt if is_inter_state else 0
                    else:
                        # Price is INCLUDING GST - reverse calculate (legacy behavior)
                        total_with_tax = price * qty
                        taxable = total_with_tax / (1 + tax_rate / 100)
                        tax_amt = total_with_tax - taxable
                        
                        is_inter_state = customer_state.upper() not in ['KARNATAKA', 'KA', '29']
                        
                        cgst = 0 if is_inter_state else tax_amt / 2
                        sgst = 0 if is_inter_state else tax_amt / 2
                        igst = tax_amt if is_inter_state else 0
                    
                    writer.writerow([
                        order.get('order_number', order.get('id', '')),
                        order_date,
                        order.get('customer_name', ''),
                        order.get('customer_phone', ''),
                        order.get('customer_gstin', order.get('customer_gst', '')),
                        customer_state,
                        item.get('product_name', item.get('name', '')),
                        item.get('hsn_code', item.get('hsn', '')),
                        qty,
                        round(price, 2),
                        round(taxable, 2),
                        round(cgst, 2),
                        round(sgst, 2),
                        round(igst, 2),
                        round(tax_amt, 2),
                        round(total_with_tax, 2),
                        order.get('payment_method', ''),
                        order.get('payment_status', ''),
                        order.get('order_status', '')
                    ])
            
            output.seek(0)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=Sales_Data_{from_date}_to_{to_date}.csv"}
            )
        
        else:
            # Excel Export
            wb = Workbook()
            ws = wb.active
            ws.title = "Sales Data"
            
            # Styling
            header_fill = PatternFill(start_color="1e40af", end_color="1e40af", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF")
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # Title
            ws.merge_cells('A1:S1')
            ws['A1'] = f"SALES DATA EXPORT - {from_date} to {to_date}"
            ws['A1'].font = Font(bold=True, size=14)
            ws['A1'].alignment = Alignment(horizontal='center')
            
            ws.merge_cells('A2:S2')
            ws['A2'] = f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}"
            ws['A2'].alignment = Alignment(horizontal='center')
            
            # Headers
            headers = [
                "Invoice No", "Date", "Customer Name", "Customer Phone", "Customer GSTIN",
                "Customer State", "Product Name", "HSN Code", "Qty", "Unit Price",
                "Taxable Amt", "CGST", "SGST", "IGST", "Total Tax", "Total Amount",
                "Payment Mode", "Payment Status", "Order Status"
            ]
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=4, column=col, value=header)
                cell.fill = header_fill
                cell.font = header_font
                cell.border = thin_border
                cell.alignment = Alignment(horizontal='center', wrap_text=True)
            
            # Data
            row_num = 5
            totals = {"taxable": 0, "cgst": 0, "sgst": 0, "igst": 0, "tax": 0, "total": 0}
            
            for order in orders:
                order_date = order.get('created_at', '')
                if isinstance(order_date, datetime):
                    order_date = order_date.strftime('%d-%m-%Y')
                elif isinstance(order_date, str) and 'T' in order_date:
                    try:
                        order_date = parser.parse(order_date).strftime('%d-%m-%Y')
                    except Exception:
                        pass
                
                items = order.get('items', [])
                if not items:
                    items = [{"product_name": "N/A", "hsn_code": "", "quantity": 1, "price": order.get('total_amount', 0)}]
                
                # Check if this is a Tally import (prices are exclusive)
                is_tally_import = order.get('import_source') == 'tally' or order.get('price_type') == 'exclusive'
                
                # Get customer state once (needed for CSV export)
                customer_state = order.get('shipping_address', {}).get('state', order.get('place_of_supply', 'Karnataka'))
                if not customer_state:
                    customer_state = 'Karnataka'
                
                for item in items:
                    qty = item.get('quantity', 1)
                    price = item.get('price', item.get('rate', item.get('unit_price', 0)))
                    tax_rate = item.get('tax_rate', item.get('gst_rate', 18))
                    
                    # Use pre-calculated values if available (from Tally import)
                    if item.get('taxable_amount') and item.get('tax'):
                        taxable = item.get('taxable_amount')
                        tax_amt = item.get('tax')
                        cgst = item.get('cgst', 0)
                        sgst = item.get('sgst', 0)
                        igst = item.get('igst', 0)
                        total_with_tax = taxable + tax_amt
                    elif is_tally_import or item.get('price_inclusive') == False:
                        # Price is EXCLUDING GST - use as taxable directly
                        taxable = price * qty
                        tax_amt = taxable * (tax_rate / 100)
                        total_with_tax = taxable + tax_amt
                        
                        is_inter_state = customer_state.upper() not in ['KARNATAKA', 'KA', '29']
                        
                        cgst = 0 if is_inter_state else tax_amt / 2
                        sgst = 0 if is_inter_state else tax_amt / 2
                        igst = tax_amt if is_inter_state else 0
                    else:
                        # Price is INCLUDING GST - reverse calculate (legacy behavior)
                        total_with_tax = price * qty
                        taxable = total_with_tax / (1 + tax_rate / 100)
                        tax_amt = total_with_tax - taxable
                        
                        is_inter_state = customer_state.upper() not in ['KARNATAKA', 'KA', '29']
                        
                        cgst = 0 if is_inter_state else tax_amt / 2
                        sgst = 0 if is_inter_state else tax_amt / 2
                        igst = tax_amt if is_inter_state else 0
                    
                    row_data = [
                        order.get('order_number', order.get('id', '')),
                        order_date,
                        order.get('customer_name', ''),
                        order.get('customer_phone', ''),
                        order.get('customer_gstin', order.get('customer_gst', '')),
                        customer_state,
                        item.get('product_name', item.get('name', '')),
                        item.get('hsn_code', item.get('hsn', '')),
                        qty,
                        round(price, 2),
                        round(taxable, 2),
                        round(cgst, 2),
                        round(sgst, 2),
                        round(igst, 2),
                        round(tax_amt, 2),
                        round(total_with_tax, 2),
                        order.get('payment_method', ''),
                        order.get('payment_status', ''),
                        order.get('order_status', '')
                    ]
                    
                    for col, value in enumerate(row_data, 1):
                        cell = ws.cell(row=row_num, column=col, value=value)
                        cell.border = thin_border
                    
                    totals["taxable"] += taxable
                    totals["cgst"] += cgst
                    totals["sgst"] += sgst
                    totals["igst"] += igst
                    totals["tax"] += tax_amt
                    totals["total"] += total_with_tax
                    
                    row_num += 1
            
            # Totals row
            row_num += 1
            ws.cell(row=row_num, column=10, value="TOTALS:").font = Font(bold=True)
            ws.cell(row=row_num, column=11, value=round(totals["taxable"], 2)).font = Font(bold=True)
            ws.cell(row=row_num, column=12, value=round(totals["cgst"], 2)).font = Font(bold=True)
            ws.cell(row=row_num, column=13, value=round(totals["sgst"], 2)).font = Font(bold=True)
            ws.cell(row=row_num, column=14, value=round(totals["igst"], 2)).font = Font(bold=True)
            ws.cell(row=row_num, column=15, value=round(totals["tax"], 2)).font = Font(bold=True)
            ws.cell(row=row_num, column=16, value=round(totals["total"], 2)).font = Font(bold=True)
            
            # Adjust column widths
            ws.column_dimensions['A'].width = 15
            ws.column_dimensions['B'].width = 12
            ws.column_dimensions['C'].width = 25
            ws.column_dimensions['D'].width = 14
            ws.column_dimensions['E'].width = 18
            ws.column_dimensions['F'].width = 14
            ws.column_dimensions['G'].width = 35
            ws.column_dimensions['H'].width = 12
            
            # Save to bytes
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)
            
            return StreamingResponse(
                output,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=Sales_Data_{from_date}_to_{to_date}.xlsx"}
            )
    
    except Exception as e:
        logger.error(f"Error exporting sales data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/purchase-data")
async def export_purchase_data(
    from_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    format: str = Query("excel", description="Export format: excel or csv"),
    db = Depends(get_db)
):
    """
    Export raw purchase bills data for a date range
    Includes all bill details with GST breakup for ITC
    """
    try:
        from dateutil import parser
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        
        start_date = parser.parse(from_date).replace(tzinfo=timezone.utc)
        end_date = parser.parse(to_date).replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
        
        # Fetch purchase bills in date range
        date_conditions = [
            {"bill_date": {"$gte": start_date, "$lte": end_date}},
            {"bill_date": {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()}},
            {"bill_date": {"$gte": from_date, "$lte": to_date}},
            {"created_at": {"$gte": start_date, "$lte": end_date}},
            {"created_at": {"$gte": from_date, "$lte": to_date}}
        ]
        
        bills = await db.purchase_bills.find(
            {"$or": date_conditions},
            {"_id": 0}
        ).sort("bill_date", 1).to_list(length=10000)
        
        logger.info(f"Exporting {len(bills)} purchase bills from {from_date} to {to_date}")
        
        if format == "csv":
            # CSV Export
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                "Bill No", "Bill Date", "PO Number", "Vendor Name", "Vendor Phone", "Vendor GSTIN",
                "Vendor MSME", "Vendor State", "Product Name", "HSN Code", "Quantity", "Unit Rate",
                "Taxable Amount", "CGST", "SGST", "IGST", "Total Tax", "Total Amount",
                "Payment Mode", "Payment Status", "Due Date"
            ])
            
            # Data rows
            for bill in bills:
                bill_date = bill.get('bill_date', bill.get('created_at', ''))
                if isinstance(bill_date, datetime):
                    bill_date = bill_date.strftime('%d-%m-%Y')
                elif isinstance(bill_date, str) and 'T' in bill_date:
                    try:
                        bill_date = parser.parse(bill_date).strftime('%d-%m-%Y')
                    except Exception:
                        pass
                
                vendor = bill.get('vendor', {})
                items = bill.get('items', [])
                if not items:
                    items = [{"product_name": "N/A", "hsn_code": "", "quantity": 1, "rate": bill.get('grand_total', 0)}]
                
                for item in items:
                    writer.writerow([
                        bill.get('bill_number', bill.get('id', '')),
                        bill_date,
                        bill.get('po_number', ''),
                        vendor.get('name', bill.get('vendor_name', '')),
                        vendor.get('phone', ''),
                        vendor.get('gst_number', bill.get('vendor_gst', '')),
                        vendor.get('msme_udyam', bill.get('vendor_msme_number', '')),
                        vendor.get('state', 'Karnataka'),
                        item.get('product_name', item.get('name', '')),
                        item.get('hsn_code', ''),
                        item.get('quantity', 1),
                        item.get('rate', item.get('unit_rate', 0)),
                        item.get('taxable_amount', 0),
                        item.get('cgst', 0),
                        item.get('sgst', 0),
                        item.get('igst', 0),
                        item.get('tax_amount', 0),
                        item.get('total', 0),
                        bill.get('payment_mode', ''),
                        bill.get('payment_status', ''),
                        bill.get('due_date', '')
                    ])
            
            output.seek(0)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=Purchase_Data_{from_date}_to_{to_date}.csv"}
            )
        
        else:
            # Excel Export
            wb = Workbook()
            ws = wb.active
            ws.title = "Purchase Data"
            
            # Styling
            header_fill = PatternFill(start_color="047857", end_color="047857", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF")
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # Title
            ws.merge_cells('A1:U1')
            ws['A1'] = f"PURCHASE DATA EXPORT - {from_date} to {to_date}"
            ws['A1'].font = Font(bold=True, size=14)
            ws['A1'].alignment = Alignment(horizontal='center')
            
            ws.merge_cells('A2:U2')
            ws['A2'] = f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')} | For ITC (Input Tax Credit) purposes"
            ws['A2'].alignment = Alignment(horizontal='center')
            
            # Headers
            headers = [
                "Bill No", "Bill Date", "PO Number", "Vendor Name", "Vendor Phone", "Vendor GSTIN",
                "Vendor MSME", "Vendor State", "Product Name", "HSN Code", "Qty", "Unit Rate",
                "Taxable Amt", "CGST", "SGST", "IGST", "Total Tax", "Total Amount",
                "Payment Mode", "Payment Status", "Due Date"
            ]
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=4, column=col, value=header)
                cell.fill = header_fill
                cell.font = header_font
                cell.border = thin_border
                cell.alignment = Alignment(horizontal='center', wrap_text=True)
            
            # Data
            row_num = 5
            totals = {"taxable": 0, "cgst": 0, "sgst": 0, "igst": 0, "tax": 0, "total": 0}
            
            for bill in bills:
                bill_date = bill.get('bill_date', bill.get('created_at', ''))
                if isinstance(bill_date, datetime):
                    bill_date = bill_date.strftime('%d-%m-%Y')
                elif isinstance(bill_date, str) and 'T' in bill_date:
                    try:
                        bill_date = parser.parse(bill_date).strftime('%d-%m-%Y')
                    except Exception:
                        pass
                
                vendor = bill.get('vendor', {})
                items = bill.get('items', [])
                if not items:
                    items = [{"product_name": "N/A", "hsn_code": "", "quantity": 1, "rate": bill.get('grand_total', 0)}]
                
                for item in items:
                    taxable = float(item.get('taxable_amount', 0))
                    cgst = float(item.get('cgst', 0))
                    sgst = float(item.get('sgst', 0))
                    igst = float(item.get('igst', 0))
                    tax_amt = float(item.get('tax_amount', cgst + sgst + igst))
                    total = float(item.get('total', taxable + tax_amt))
                    
                    row_data = [
                        bill.get('bill_number', bill.get('id', '')),
                        bill_date,
                        bill.get('po_number', ''),
                        vendor.get('name', bill.get('vendor_name', '')),
                        vendor.get('phone', ''),
                        vendor.get('gst_number', bill.get('vendor_gst', '')),
                        vendor.get('msme_udyam', bill.get('vendor_msme_number', '')),
                        vendor.get('state', 'Karnataka'),
                        item.get('product_name', item.get('name', '')),
                        item.get('hsn_code', ''),
                        item.get('quantity', 1),
                        round(float(item.get('rate', item.get('unit_rate', 0))), 2),
                        round(taxable, 2),
                        round(cgst, 2),
                        round(sgst, 2),
                        round(igst, 2),
                        round(tax_amt, 2),
                        round(total, 2),
                        bill.get('payment_mode', ''),
                        bill.get('payment_status', ''),
                        bill.get('due_date', '')
                    ]
                    
                    for col, value in enumerate(row_data, 1):
                        cell = ws.cell(row=row_num, column=col, value=value)
                        cell.border = thin_border
                    
                    totals["taxable"] += taxable
                    totals["cgst"] += cgst
                    totals["sgst"] += sgst
                    totals["igst"] += igst
                    totals["tax"] += tax_amt
                    totals["total"] += total
                    
                    row_num += 1
            
            # Totals row
            row_num += 1
            ws.cell(row=row_num, column=12, value="TOTALS:").font = Font(bold=True)
            ws.cell(row=row_num, column=13, value=round(totals["taxable"], 2)).font = Font(bold=True)
            ws.cell(row=row_num, column=14, value=round(totals["cgst"], 2)).font = Font(bold=True)
            ws.cell(row=row_num, column=15, value=round(totals["sgst"], 2)).font = Font(bold=True)
            ws.cell(row=row_num, column=16, value=round(totals["igst"], 2)).font = Font(bold=True)
            ws.cell(row=row_num, column=17, value=round(totals["tax"], 2)).font = Font(bold=True)
            ws.cell(row=row_num, column=18, value=round(totals["total"], 2)).font = Font(bold=True)
            
            # ITC Summary
            row_num += 2
            ws.cell(row=row_num, column=1, value="INPUT TAX CREDIT (ITC) SUMMARY").font = Font(bold=True, size=12)
            row_num += 1
            ws.cell(row=row_num, column=1, value=f"Total ITC Available: Rs. {round(totals['tax'], 2)}")
            row_num += 1
            ws.cell(row=row_num, column=1, value=f"CGST Credit: Rs. {round(totals['cgst'], 2)}")
            row_num += 1
            ws.cell(row=row_num, column=1, value=f"SGST Credit: Rs. {round(totals['sgst'], 2)}")
            row_num += 1
            ws.cell(row=row_num, column=1, value=f"IGST Credit: Rs. {round(totals['igst'], 2)}")
            
            # Adjust column widths
            ws.column_dimensions['A'].width = 15
            ws.column_dimensions['B'].width = 12
            ws.column_dimensions['C'].width = 12
            ws.column_dimensions['D'].width = 25
            ws.column_dimensions['E'].width = 14
            ws.column_dimensions['F'].width = 18
            ws.column_dimensions['G'].width = 20
            ws.column_dimensions['H'].width = 12
            ws.column_dimensions['I'].width = 30
            
            # Save to bytes
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)
            
            return StreamingResponse(
                output,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=Purchase_Data_{from_date}_to_{to_date}.xlsx"}
            )
    
    except Exception as e:
        logger.error(f"Error exporting purchase data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

