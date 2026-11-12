"""
Accounting Reports Routes - Fixed for proper date handling and data sources
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime, timezone, timedelta
from database import get_db
import math

router = APIRouter(prefix="/accounting/reports", tags=["Accounting Reports"])


def clean_nan(value, default=0):
    """Clean NaN/Infinity values"""
    if value is None:
        return default
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return default
    return value


def parse_date(date_str):
    """Parse date string to datetime with timezone"""
    if not date_str:
        return None
    try:
        from dateutil import parser
        dt = parser.parse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


@router.get("/dashboard-summary")
async def get_dashboard_summary(db = Depends(get_db)):
    """Get dashboard summary with all key metrics"""
    try:
        now = datetime.now(timezone.utc)
        
        # This month range
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_start_str = month_start.strftime("%Y-%m-%d")
        now_str = now.strftime("%Y-%m-%d") + "T23:59:59"
        
        # Get orders (handle both date formats)
        orders_pipeline = [
            {"$match": {
                "$or": [
                    {"created_at": {"$gte": month_start, "$lte": now, "$type": "date"}},
                    {"created_at": {"$gte": month_start_str, "$lte": now_str, "$type": "string"}}
                ]
            }},
            {"$group": {
                "_id": None,
                "total_sales": {"$sum": "$total_amount"},
                "total_tax": {"$sum": {"$ifNull": ["$tax_amount", 0]}},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "count": {"$sum": 1}
            }}
        ]
        orders_result = await db.orders.aggregate(orders_pipeline).to_list(1)
        orders_data = orders_result[0] if orders_result else {"total_sales": 0, "total_tax": 0, "cgst": 0, "sgst": 0, "igst": 0, "count": 0}

        # Get OFFLINE invoices (in-store sales — read with correct field names)
        offline_pipeline = [
            {"$match": {
                "document_type": "invoice",
                "$or": [
                    {"created_at": {"$gte": month_start, "$lte": now, "$type": "date"}},
                    {"created_at": {"$gte": month_start_str, "$lte": now_str, "$type": "string"}}
                ]
            }},
            {"$group": {
                "_id": None,
                "total_sales": {"$sum": {"$ifNull": ["$total_amount", 0]}},
                "total_tax": {"$sum": {"$ifNull": ["$tax_total", 0]}},
                "cgst": {"$sum": {"$ifNull": ["$cgst_total", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst_total", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst_total", 0]}},
                "count": {"$sum": 1}
            }}
        ]
        offline_result = await db.offline_invoices.aggregate(offline_pipeline).to_list(1)
        offline_data = offline_result[0] if offline_result else {"total_sales": 0, "total_tax": 0, "cgst": 0, "sgst": 0, "igst": 0, "count": 0}
        
        # Get purchase bills
        bills_pipeline = [
            {"$match": {
                "bill_date": {"$gte": month_start_str, "$lte": now_str[:10]}
            }},
            {"$group": {
                "_id": None,
                "total_purchases": {"$sum": "$grand_total"},
                "total_tax": {"$sum": {"$ifNull": ["$total_tax", 0]}},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "count": {"$sum": 1}
            }}
        ]
        bills_result = await db.purchase_bills.aggregate(bills_pipeline).to_list(1)
        bills_data = bills_result[0] if bills_result else {"total_purchases": 0, "total_tax": 0, "cgst": 0, "sgst": 0, "igst": 0, "count": 0}
        
        # Get expenses
        expenses_pipeline = [
            {"$match": {
                "$or": [
                    {"date": {"$gte": month_start, "$lte": now}},
                    {"date": {"$gte": month_start_str, "$lte": now_str[:10]}}
                ]
            }},
            {"$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"}
            }}
        ]
        expenses_result = await db.expenses.aggregate(expenses_pipeline).to_list(None)
        total_expenses = sum(clean_nan(e.get("total", 0)) for e in expenses_result)
        
        # Receivables — include BOTH online order pending + offline invoice pending
        receivables = await db.orders.aggregate([
            {"$match": {"payment_status": {"$in": ["pending", "partial"]}}},
            {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
        ]).to_list(1)
        offline_receivables = await db.offline_invoices.aggregate([
            {"$match": {"document_type": "invoice", "payment_status": {"$in": ["pending", "partial"]}}},
            {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
        ]).to_list(1)
        total_receivables = (clean_nan(receivables[0]["total"]) if receivables else 0) + \
                            (clean_nan(offline_receivables[0]["total"]) if offline_receivables else 0)

        payables = await db.purchase_bills.aggregate([
            {"$match": {"payment_status": {"$in": ["pending", "partial"]}}},
            {"$group": {"_id": None, "total": {"$sum": "$grand_total"}}}
        ]).to_list(1)

        total_sales = clean_nan(orders_data.get("total_sales", 0)) + clean_nan(offline_data.get("total_sales", 0))
        total_purchases = clean_nan(bills_data.get("total_purchases", 0))

        return {
            "status": "success",
            "summary": {
                "total_sales": round(total_sales, 2),
                "online_sales": round(clean_nan(orders_data.get("total_sales", 0)), 2),
                "offline_sales": round(clean_nan(offline_data.get("total_sales", 0)), 2),
                "total_purchases": round(total_purchases, 2),
                "total_expenses": round(total_expenses, 2),
                "gross_profit": round(total_sales - total_purchases, 2),
                "net_profit": round(total_sales - total_purchases - total_expenses, 2),
                "sales_count": orders_data.get("count", 0) + offline_data.get("count", 0),
                "online_sales_count": orders_data.get("count", 0),
                "offline_sales_count": offline_data.get("count", 0),
                "purchase_count": bills_data.get("count", 0),
                "gst_collected": {
                    "cgst": round(clean_nan(orders_data.get("cgst", 0)) + clean_nan(offline_data.get("cgst", 0)), 2),
                    "sgst": round(clean_nan(orders_data.get("sgst", 0)) + clean_nan(offline_data.get("sgst", 0)), 2),
                    "igst": round(clean_nan(orders_data.get("igst", 0)) + clean_nan(offline_data.get("igst", 0)), 2),
                    "total": round(clean_nan(orders_data.get("total_tax", 0)) + clean_nan(offline_data.get("total_tax", 0)), 2)
                },
                "gst_paid": {
                    "cgst": round(clean_nan(bills_data.get("cgst", 0)), 2),
                    "sgst": round(clean_nan(bills_data.get("sgst", 0)), 2),
                    "igst": round(clean_nan(bills_data.get("igst", 0)), 2),
                    "total": round(clean_nan(bills_data.get("total_tax", 0)), 2)
                },
                "receivables": round(total_receivables, 2),
                "payables": round(clean_nan(payables[0]["total"]) if payables else 0, 2),
                "period": "This Month"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard summary: {str(e)}")


@router.get("/sales-summary")
async def get_sales_summary(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Get sales summary report"""
    try:
        now = datetime.now(timezone.utc)
        
        if from_date and to_date:
            start_dt = parse_date(from_date) or now.replace(day=1)
            end_dt = parse_date(to_date) or now
        else:
            start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_dt = now
        
        start_str = start_dt.strftime("%Y-%m-%d")
        end_str = end_dt.strftime("%Y-%m-%d") + "T23:59:59"
        
        # Get online orders (handle both date formats)
        orders_pipeline = [
            {"$match": {
                "$or": [
                    {"created_at": {"$gte": start_dt, "$lte": end_dt, "$type": "date"}},
                    {"created_at": {"$gte": start_str, "$lte": end_str, "$type": "string"}}
                ],
                "order_status": {"$ne": "cancelled"}
            }},
            {"$group": {
                "_id": None,
                "total_amount": {"$sum": "$total_amount"},
                "subtotal": {"$sum": "$subtotal"},
                "tax_amount": {"$sum": {"$ifNull": ["$tax_amount", 0]}},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "count": {"$sum": 1}
            }}
        ]
        orders_result = await db.orders.aggregate(orders_pipeline).to_list(1)
        orders_data = orders_result[0] if orders_result else {}
        
        # Get offline invoices — correct fields + filter to invoices (not SOs)
        offline_pipeline = [
            {"$match": {
                "document_type": "invoice",
                "$or": [
                    {"created_at": {"$gte": start_dt, "$lte": end_dt}},
                    {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}}
                ]
            }},
            {"$group": {
                "_id": None,
                "total_amount": {"$sum": {"$ifNull": ["$total_amount", 0]}},
                "tax_total": {"$sum": {"$ifNull": ["$tax_total", 0]}},
                "cgst": {"$sum": {"$ifNull": ["$cgst_total", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst_total", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst_total", 0]}},
                "count": {"$sum": 1}
            }}
        ]
        offline_result = await db.offline_invoices.aggregate(offline_pipeline).to_list(1)
        offline_data = offline_result[0] if offline_result else {}
        
        # Get payment breakdown
        payment_pipeline = [
            {"$match": {
                "$or": [
                    {"created_at": {"$gte": start_dt, "$lte": end_dt, "$type": "date"}},
                    {"created_at": {"$gte": start_str, "$lte": end_str, "$type": "string"}}
                ]
            }},
            {"$group": {
                "_id": "$payment_method",
                "count": {"$sum": 1},
                "amount": {"$sum": "$total_amount"}
            }}
        ]
        payment_result = await db.orders.aggregate(payment_pipeline).to_list(None)
        payment_breakdown = {p["_id"]: {"count": p["count"], "amount": round(clean_nan(p["amount"]), 2)} for p in payment_result}
        
        total_online = clean_nan(orders_data.get("total_amount", 0))
        total_offline = clean_nan(offline_data.get("total_amount", 0))
        total_sales = total_online + total_offline
        total_orders = orders_data.get("count", 0) + offline_data.get("count", 0)
        
        return {
            "status": "success",
            "report": {
                "from_date": start_str,
                "to_date": end_str[:10],
                "total_sales": round(total_sales, 2),
                "online_sales": round(total_online, 2),
                "offline_sales": round(total_offline, 2),
                "total_orders": total_orders,
                "online_orders": orders_data.get("count", 0),
                "offline_orders": offline_data.get("count", 0),
                "subtotal": round(clean_nan(orders_data.get("subtotal", 0)), 2),
                "total_tax_collected": round(clean_nan(orders_data.get("tax_amount", 0)), 2),
                "cgst": round(clean_nan(orders_data.get("cgst", 0)), 2),
                "sgst": round(clean_nan(orders_data.get("sgst", 0)), 2),
                "igst": round(clean_nan(orders_data.get("igst", 0)), 2),
                "average_order_value": round(total_sales / total_orders, 2) if total_orders > 0 else 0,
                "payment_breakdown": payment_breakdown
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate sales report: {str(e)}")


@router.get("/purchase-summary")
async def get_purchase_summary(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Get purchase summary report from purchase_bills"""
    try:
        now = datetime.now(timezone.utc)
        
        if from_date and to_date:
            start_dt = parse_date(from_date) or now.replace(day=1)
            end_dt = parse_date(to_date) or now
        else:
            start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_dt = now
        
        start_str = start_dt.strftime("%Y-%m-%d")
        end_str = end_dt.strftime("%Y-%m-%d")
        
        # Get purchase bills (bill_date is string format)
        bills_pipeline = [
            {"$match": {
                "bill_date": {"$gte": start_str, "$lte": end_str}
            }},
            {"$group": {
                "_id": "$payment_status",
                "total_amount": {"$sum": "$grand_total"},
                "subtotal": {"$sum": "$subtotal"},
                "total_tax": {"$sum": {"$ifNull": ["$total_tax", 0]}},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "count": {"$sum": 1}
            }}
        ]
        bills_result = await db.purchase_bills.aggregate(bills_pipeline).to_list(None)
        
        # Aggregate results
        total_amount = 0
        total_tax = 0
        total_cgst = 0
        total_sgst = 0
        total_igst = 0
        total_count = 0
        pending_count = 0
        paid_count = 0
        
        for r in bills_result:
            total_amount += clean_nan(r.get("total_amount", 0))
            total_tax += clean_nan(r.get("total_tax", 0))
            total_cgst += clean_nan(r.get("cgst", 0))
            total_sgst += clean_nan(r.get("sgst", 0))
            total_igst += clean_nan(r.get("igst", 0))
            total_count += r.get("count", 0)
            
            if r["_id"] in ["pending", "partial"]:
                pending_count += r.get("count", 0)
            else:
                paid_count += r.get("count", 0)
        
        # Get vendor breakdown
        vendor_pipeline = [
            {"$match": {"bill_date": {"$gte": start_str, "$lte": end_str}}},
            {"$group": {
                "_id": "$vendor_name",
                "total": {"$sum": "$grand_total"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"total": -1}},
            {"$limit": 10}
        ]
        vendor_result = await db.purchase_bills.aggregate(vendor_pipeline).to_list(10)
        top_vendors = [{"name": v["_id"], "amount": round(clean_nan(v["total"]), 2), "count": v["count"]} for v in vendor_result]
        
        return {
            "status": "success",
            "report": {
                "from_date": start_str,
                "to_date": end_str,
                "total_purchases": round(total_amount, 2),
                "total_orders": total_count,
                "total_tax_paid": round(total_tax, 2),
                "cgst": round(total_cgst, 2),
                "sgst": round(total_sgst, 2),
                "igst": round(total_igst, 2),
                "average_purchase_value": round(total_amount / total_count, 2) if total_count > 0 else 0,
                "pending_orders": pending_count,
                "completed_orders": paid_count,
                "top_vendors": top_vendors
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate purchase report: {str(e)}")


@router.get("/expense-summary")
async def get_expense_summary(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Get expense summary report"""
    try:
        now = datetime.now(timezone.utc)
        
        if from_date and to_date:
            start_dt = parse_date(from_date) or now.replace(day=1)
            end_dt = parse_date(to_date) or now
        else:
            start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_dt = now
        
        start_str = start_dt.strftime("%Y-%m-%d")
        end_str = end_dt.strftime("%Y-%m-%d")
        
        # Get expenses by category
        expenses_pipeline = [
            {"$match": {
                "$or": [
                    {"date": {"$gte": start_dt, "$lte": end_dt}},
                    {"date": {"$gte": start_str, "$lte": end_str}}
                ]
            }},
            {"$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"total": -1}}
        ]
        expenses_result = await db.expenses.aggregate(expenses_pipeline).to_list(None)
        
        total_expenses = sum(clean_nan(e.get("total", 0)) for e in expenses_result)
        category_breakdown = {e["_id"] or "Uncategorized": {"amount": round(clean_nan(e["total"]), 2), "count": e["count"]} for e in expenses_result}
        
        return {
            "status": "success",
            "report": {
                "from_date": start_str,
                "to_date": end_str,
                "total_expenses": round(total_expenses, 2),
                "expense_count": sum(e.get("count", 0) for e in expenses_result),
                "by_category": category_breakdown,
                "top_categories": [{"category": e["_id"] or "Uncategorized", "amount": round(clean_nan(e["total"]), 2)} for e in expenses_result[:5]]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate expense report: {str(e)}")


@router.get("/gst-report")
async def get_gst_report(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    report_type: str = "gstr1",
    db = Depends(get_db)
):
    """Get GST report for GSTR-1 or GSTR-3B - matches frontend expectations"""
    try:
        now = datetime.now(timezone.utc)
        
        if from_date and to_date:
            start_dt = parse_date(from_date) or now.replace(day=1)
            end_dt = parse_date(to_date) or now
        else:
            start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_dt = now
        
        start_str = start_dt.strftime("%Y-%m-%d")
        end_str = end_dt.strftime("%Y-%m-%d") + "T23:59:59"
        
        # Output GST (from sales)
        output_pipeline = [
            {"$match": {
                "$or": [
                    {"created_at": {"$gte": start_dt, "$lte": end_dt, "$type": "date"}},
                    {"created_at": {"$gte": start_str, "$lte": end_str, "$type": "string"}}
                ]
            }},
            {"$group": {
                "_id": None,
                "taxable_value": {"$sum": "$subtotal"},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "total_tax": {"$sum": {"$ifNull": ["$tax_amount", 0]}},
                "invoice_count": {"$sum": 1}
            }}
        ]
        output_result = await db.orders.aggregate(output_pipeline).to_list(1)
        output_data = output_result[0] if output_result else {}

        # Merge offline invoice output GST into output_data
        offline_out_pipeline = [
            {"$match": {
                "document_type": "invoice",
                "$or": [
                    {"created_at": {"$gte": start_dt, "$lte": end_dt}},
                    {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}}
                ]
            }},
            {"$group": {
                "_id": None,
                "taxable_value": {"$sum": {"$ifNull": ["$subtotal", 0]}},
                "cgst": {"$sum": {"$ifNull": ["$cgst_total", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst_total", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst_total", 0]}},
                "total_tax": {"$sum": {"$ifNull": ["$tax_total", 0]}},
                "invoice_count": {"$sum": 1}
            }}
        ]
        offline_out_result = await db.offline_invoices.aggregate(offline_out_pipeline).to_list(1)
        offline_out = offline_out_result[0] if offline_out_result else {}
        for _k in ("taxable_value", "cgst", "sgst", "igst", "total_tax", "invoice_count"):
            output_data[_k] = clean_nan(output_data.get(_k, 0)) + clean_nan(offline_out.get(_k, 0))

        
        # Input GST (from purchases)
        input_pipeline = [
            {"$match": {
                "bill_date": {"$gte": start_str, "$lte": end_str[:10]}
            }},
            {"$group": {
                "_id": None,
                "taxable_value": {"$sum": "$subtotal"},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "total_tax": {"$sum": {"$ifNull": ["$total_tax", 0]}},
                "bill_count": {"$sum": 1}
            }}
        ]
        input_result = await db.purchase_bills.aggregate(input_pipeline).to_list(1)
        input_data = input_result[0] if input_result else {}
        
        output_total = clean_nan(output_data.get("total_tax", 0))
        input_total = clean_nan(input_data.get("total_tax", 0))
        output_cgst = clean_nan(output_data.get("cgst", 0))
        output_sgst = clean_nan(output_data.get("sgst", 0))
        output_igst = clean_nan(output_data.get("igst", 0))
        input_cgst = clean_nan(input_data.get("cgst", 0))
        input_sgst = clean_nan(input_data.get("sgst", 0))
        input_igst = clean_nan(input_data.get("igst", 0))
        
        if report_type.lower() == "gstr1":
            # GSTR-1: Outward Supplies Report
            # Get HSN-wise summary
            hsn_pipeline = [
                {"$match": {
                    "$or": [
                        {"created_at": {"$gte": start_dt, "$lte": end_dt, "$type": "date"}},
                        {"created_at": {"$gte": start_str, "$lte": end_str, "$type": "string"}}
                    ]
                }},
                {"$unwind": {"path": "$items", "preserveNullAndEmptyArrays": True}},
                {"$group": {
                    "_id": {"$ifNull": ["$items.hsn_code", "N/A"]},
                    "quantity": {"$sum": {"$ifNull": ["$items.quantity", 1]}},
                    "taxable_value": {"$sum": {"$ifNull": ["$items.subtotal", "$subtotal"]}},
                    "tax_amount": {"$sum": {"$ifNull": ["$items.tax_amount", 0]}}
                }},
                {"$sort": {"taxable_value": -1}},
                {"$limit": 20}
            ]
            hsn_result = await db.orders.aggregate(hsn_pipeline).to_list(20)
            
            hsn_summary = [{
                "hsn_code": h["_id"],
                "quantity": h.get("quantity", 0),
                "taxable_value": round(clean_nan(h.get("taxable_value", 0)), 2),
                "tax_amount": round(clean_nan(h.get("tax_amount", 0)), 2)
            } for h in hsn_result]
            
            return {
                "status": "success",
                "report_type": "GSTR-1",
                "period": {"from": start_str, "to": end_str[:10]},
                "summary": {
                    "total_outward_supplies": round(clean_nan(output_data.get("taxable_value", 0)), 2),
                    "total_tax": round(output_total, 2),
                    "cgst": round(output_cgst, 2),
                    "sgst": round(output_sgst, 2),
                    "igst": round(output_igst, 2),
                    "invoice_count": output_data.get("invoice_count", 0)
                },
                "hsn_summary": hsn_summary
            }
        else:
            # GSTR-3B: Summary Return
            net_liability = output_total - input_total
            
            return {
                "status": "success",
                "report_type": "GSTR-3B",
                "period": {"from": start_str, "to": end_str[:10]},
                "tax_liability": {
                    "output_tax": round(output_total, 2),
                    "input_tax_credit": round(input_total, 2),
                    "net_tax_payable": round(max(0, net_liability), 2),
                    "cgst_payable": round(max(0, output_cgst - input_cgst), 2),
                    "sgst_payable": round(max(0, output_sgst - input_sgst), 2),
                    "igst_payable": round(max(0, output_igst - input_igst), 2)
                },
                "inward_supplies": {
                    "total_purchases": round(clean_nan(input_data.get("taxable_value", 0)), 2),
                    "cgst": round(input_cgst, 2),
                    "sgst": round(input_sgst, 2),
                    "igst": round(input_igst, 2),
                    "total_itc": round(input_total, 2),
                    "bill_count": input_data.get("bill_count", 0)
                },
                "summary": {
                    "total_output_tax": round(output_total, 2),
                    "total_input_tax_credit": round(input_total, 2),
                    "net_tax_payable": round(max(0, net_liability), 2),
                    "itc_carry_forward": round(max(0, -net_liability), 2)
                }
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate GST report: {str(e)}")


@router.get("/gst-summary")
async def get_gst_summary_report(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Get GST summary report"""
    try:
        now = datetime.now(timezone.utc)
        
        if from_date and to_date:
            start_dt = parse_date(from_date) or now.replace(day=1)
            end_dt = parse_date(to_date) or now
        else:
            start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_dt = now
        
        start_str = start_dt.strftime("%Y-%m-%d")
        end_str = end_dt.strftime("%Y-%m-%d") + "T23:59:59"
        
        # Output GST (from sales)
        output_pipeline = [
            {"$match": {
                "$or": [
                    {"created_at": {"$gte": start_dt, "$lte": end_dt, "$type": "date"}},
                    {"created_at": {"$gte": start_str, "$lte": end_str, "$type": "string"}}
                ]
            }},
            {"$group": {
                "_id": None,
                "taxable_value": {"$sum": "$subtotal"},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "total_tax": {"$sum": {"$ifNull": ["$tax_amount", 0]}},
                "invoice_count": {"$sum": 1}
            }}
        ]
        output_result = await db.orders.aggregate(output_pipeline).to_list(1)
        output_data = output_result[0] if output_result else {}
        
        # Input GST (from purchases)
        input_pipeline = [
            {"$match": {
                "bill_date": {"$gte": start_str, "$lte": end_str[:10]}
            }},
            {"$group": {
                "_id": None,
                "taxable_value": {"$sum": "$subtotal"},
                "cgst": {"$sum": {"$ifNull": ["$cgst", 0]}},
                "sgst": {"$sum": {"$ifNull": ["$sgst", 0]}},
                "igst": {"$sum": {"$ifNull": ["$igst", 0]}},
                "total_tax": {"$sum": {"$ifNull": ["$total_tax", 0]}},
                "bill_count": {"$sum": 1}
            }}
        ]
        input_result = await db.purchase_bills.aggregate(input_pipeline).to_list(1)
        input_data = input_result[0] if input_result else {}
        
        output_total = clean_nan(output_data.get("total_tax", 0))
        input_total = clean_nan(input_data.get("total_tax", 0))
        net_liability = output_total - input_total
        
        return {
            "status": "success",
            "report": {
                "from_date": start_str,
                "to_date": end_str[:10],
                "output_gst": {
                    "taxable_value": round(clean_nan(output_data.get("taxable_value", 0)), 2),
                    "cgst": round(clean_nan(output_data.get("cgst", 0)), 2),
                    "sgst": round(clean_nan(output_data.get("sgst", 0)), 2),
                    "igst": round(clean_nan(output_data.get("igst", 0)), 2),
                    "total": round(output_total, 2),
                    "invoice_count": output_data.get("invoice_count", 0)
                },
                "input_gst": {
                    "taxable_value": round(clean_nan(input_data.get("taxable_value", 0)), 2),
                    "cgst": round(clean_nan(input_data.get("cgst", 0)), 2),
                    "sgst": round(clean_nan(input_data.get("sgst", 0)), 2),
                    "igst": round(clean_nan(input_data.get("igst", 0)), 2),
                    "total": round(input_total, 2),
                    "bill_count": input_data.get("bill_count", 0)
                },
                "net_liability": {
                    "cgst": round(max(0, clean_nan(output_data.get("cgst", 0)) - clean_nan(input_data.get("cgst", 0))), 2),
                    "sgst": round(max(0, clean_nan(output_data.get("sgst", 0)) - clean_nan(input_data.get("sgst", 0))), 2),
                    "igst": round(max(0, clean_nan(output_data.get("igst", 0)) - clean_nan(input_data.get("igst", 0))), 2),
                    "total_payable": round(max(0, net_liability), 2),
                    "itc_carry_forward": round(max(0, -net_liability), 2)
                }
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate GST report: {str(e)}")


@router.get("/payment-receipt-summary")
async def get_payment_receipt_summary(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Get payment and receipt summary"""
    try:
        now = datetime.now(timezone.utc)
        
        if from_date and to_date:
            start_dt = parse_date(from_date) or now.replace(day=1)
            end_dt = parse_date(to_date) or now
        else:
            start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_dt = now
        
        start_str = start_dt.strftime("%Y-%m-%d")
        end_str = end_dt.strftime("%Y-%m-%d")
        
        # Get payments made
        payments = await db.payments.find({
            "$or": [
                {"date": {"$gte": start_dt, "$lte": end_dt}},
                {"date": {"$gte": start_str, "$lte": end_str}}
            ]
        }, {"_id": 0}).to_list(None)
        
        total_payments = sum(clean_nan(p.get("amount", 0)) for p in payments)
        
        # Get receipts received
        receipts = await db.receipts.find({
            "$or": [
                {"date": {"$gte": start_dt, "$lte": end_dt}},
                {"date": {"$gte": start_str, "$lte": end_str}}
            ]
        }, {"_id": 0}).to_list(None)
        
        total_receipts = sum(clean_nan(r.get("amount", 0)) for r in receipts)
        
        return {
            "status": "success",
            "report": {
                "from_date": start_str,
                "to_date": end_str,
                "payments": {
                    "total": round(total_payments, 2),
                    "count": len(payments)
                },
                "receipts": {
                    "total": round(total_receipts, 2),
                    "count": len(receipts)
                },
                "net_cash_flow": round(total_receipts - total_payments, 2)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate payment/receipt report: {str(e)}")
