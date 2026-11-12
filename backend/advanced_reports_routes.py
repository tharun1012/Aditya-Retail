"""
Advanced Reporting Routes
Date-wise, Month-wise, Year-wise, Item-wise reports
Pending deliveries, SO/PO tracking
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from database import get_db
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/reports", tags=["Advanced Reports"])

# ============ DATE-WISE REPORTS ============

@router.get("/sales/daily")
async def get_daily_sales_report(
    date: Optional[str] = None,
    store_id: Optional[str] = None,
    db = Depends(get_db)
):
    """Get sales report for a specific day - includes both orders and offline invoices"""
    try:
        from dateutil import parser
        
        if date:
            report_date = parser.parse(date).replace(tzinfo=timezone.utc)
        else:
            report_date = datetime.now(timezone.utc)
        
        start = report_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = report_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Query for date strings (used by offline_invoices)
        start_str = start.isoformat()
        end_str = end.isoformat()
        
        # Get from orders collection (online orders)
        orders_query = {
            "created_at": {"$gte": start, "$lte": end},
            "payment_status": {"$in": ["completed", "paid"]}
        }
        if store_id:
            orders_query["store_id"] = store_id
        
        orders = await db.orders.find(
            orders_query,
            {"_id": 0, "id": 1, "order_number": 1, "customer_name": 1, "total_amount": 1, 
             "payment_method": 1, "order_status": 1, "created_at": 1, "items": 1}
        ).sort("created_at", 1).to_list(None)
        
        # Get from offline_invoices collection (store invoices and SOs)
        offline_query = {
            "created_at": {"$gte": start_str, "$lte": end_str}
        }
        if store_id:
            # store_id could be UUID or store_code - check both
            offline_query["$or"] = [
                {"store_code": store_id},
                {"store_id": store_id}
            ]
        
        offline_invoices = await db.offline_invoices.find(
            offline_query,
            {"_id": 0}
        ).sort("created_at", 1).to_list(None)
        
        # Transform offline invoices to match order format
        all_orders = list(orders)
        for inv in offline_invoices:
            customer = inv.get("customer", {})
            all_orders.append({
                "id": inv.get("id"),
                "order_number": inv.get("invoice_number"),
                "customer_name": customer.get("name", "N/A"),
                "total_amount": inv.get("total_amount", 0),
                "payment_method": inv.get("payment_mode", "unknown"),
                "order_status": inv.get("status", "unknown"),
                "created_at": inv.get("created_at"),
                "items": inv.get("items", []),
                "document_type": inv.get("document_type", "invoice"),
                "store_code": inv.get("store_code")
            })
        
        # Calculate totals
        total_sales = sum(o.get("total_amount", 0) for o in all_orders)
        total_items = sum(sum(i.get("quantity", 0) for i in o.get("items", [])) for o in all_orders)
        
        # Payment method breakdown
        payment_breakdown = {}
        for o in all_orders:
            method = o.get("payment_method", "unknown")
            if method not in payment_breakdown:
                payment_breakdown[method] = {"count": 0, "amount": 0}
            payment_breakdown[method]["count"] += 1
            payment_breakdown[method]["amount"] += o.get("total_amount", 0)
        
        # Document type breakdown for offline invoices
        doc_breakdown = {"invoice": 0, "sales_order": 0, "online": 0}
        for o in all_orders:
            doc_type = o.get("document_type", "online")
            doc_breakdown[doc_type] = doc_breakdown.get(doc_type, 0) + 1
        
        return {
            "status": "success",
            "date": start.strftime("%Y-%m-%d"),
            "orders": all_orders,
            "summary": {
                "total_orders": len(all_orders),
                "total_sales": round(total_sales, 2),
                "total_items_sold": total_items,
                "average_order_value": round(total_sales / len(all_orders), 2) if all_orders else 0
            },
            "payment_breakdown": payment_breakdown,
            "document_breakdown": doc_breakdown
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sales/monthly")
async def get_monthly_sales_report(
    year: int = None,
    month: int = None,
    store_id: Optional[str] = None,
    db = Depends(get_db)
):
    """Get sales report for a specific month - includes offline invoices"""
    try:
        now = datetime.now(timezone.utc)
        year = year or now.year
        month = month or now.month
        
        start = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
        if month == 12:
            end = datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=timezone.utc) - timedelta(seconds=1)
        else:
            end = datetime(year, month + 1, 1, 0, 0, 0, tzinfo=timezone.utc) - timedelta(seconds=1)
        
        start_str = start.isoformat()
        end_str = end.isoformat()
        
        # Get from orders collection (online orders)
        orders_query = {
            "created_at": {"$gte": start, "$lte": end},
            "payment_status": {"$in": ["completed", "paid"]}
        }
        if store_id:
            orders_query["store_id"] = store_id
        
        # Daily breakdown from orders
        pipeline = [
            {"$match": orders_query},
            {"$group": {
                "_id": {"$dayOfMonth": "$created_at"},
                "date": {"$first": "$created_at"},
                "total_sales": {"$sum": "$total_amount"},
                "order_count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        daily_data = await db.orders.aggregate(pipeline).to_list(None)
        
        # Get from offline_invoices collection
        offline_query = {
            "created_at": {"$gte": start_str, "$lte": end_str}
        }
        if store_id:
            offline_query["store_code"] = store_id
        
        offline_invoices = await db.offline_invoices.find(
            offline_query,
            {"_id": 0, "total_amount": 1, "created_at": 1, "document_type": 1}
        ).to_list(None)
        
        # Process offline invoices into daily breakdown
        offline_daily = {}
        for inv in offline_invoices:
            try:
                inv_date = datetime.fromisoformat(inv.get("created_at", "").replace("Z", "+00:00"))
                day = inv_date.day
                if day not in offline_daily:
                    offline_daily[day] = {"total_sales": 0, "order_count": 0}
                offline_daily[day]["total_sales"] += inv.get("total_amount", 0)
                offline_daily[day]["order_count"] += 1
            except Exception:
                continue
        
        # Merge daily data
        merged_daily = {}
        for d in daily_data:
            day = d["_id"]
            merged_daily[day] = {
                "_id": day,
                "date": d.get("date"),
                "total_sales": d.get("total_sales", 0),
                "order_count": d.get("order_count", 0)
            }
        
        for day, data in offline_daily.items():
            if day in merged_daily:
                merged_daily[day]["total_sales"] += data["total_sales"]
                merged_daily[day]["order_count"] += data["order_count"]
            else:
                merged_daily[day] = {
                    "_id": day,
                    "date": datetime(year, month, day, tzinfo=timezone.utc).isoformat(),
                    "total_sales": data["total_sales"],
                    "order_count": data["order_count"]
                }
        
        final_daily = sorted(merged_daily.values(), key=lambda x: x["_id"])
        
        # Overall summary
        total_sales = sum(d.get("total_sales", 0) for d in final_daily)
        total_orders = sum(d.get("order_count", 0) for d in final_daily)
        
        return {
            "status": "success",
            "year": year,
            "month": month,
            "daily_breakdown": final_daily,
            "summary": {
                "total_orders": total_orders,
                "total_sales": round(total_sales, 2),
                "average_daily_sales": round(total_sales / len(final_daily), 2) if final_daily else 0,
                "best_day": max(final_daily, key=lambda x: x["total_sales"]) if final_daily else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sales/yearly")
async def get_yearly_sales_report(
    year: int = None,
    store_id: Optional[str] = None,
    db = Depends(get_db)
):
    """Get sales report for a specific year"""
    try:
        now = datetime.now(timezone.utc)
        year = year or now.year
        
        start = datetime(year, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        
        match_query = {
            "created_at": {"$gte": start, "$lte": end},
            "payment_status": {"$in": ["completed", "paid"]}
        }
        if store_id:
            match_query["store_id"] = store_id
        
        # Monthly breakdown
        pipeline = [
            {"$match": match_query},
            {"$group": {
                "_id": {"$month": "$created_at"},
                "month": {"$first": {"$month": "$created_at"}},
                "total_sales": {"$sum": "$total_amount"},
                "order_count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        monthly_data = await db.orders.aggregate(pipeline).to_list(None)
        
        total_sales = sum(d.get("total_sales", 0) for d in monthly_data)
        total_orders = sum(d.get("order_count", 0) for d in monthly_data)
        
        return {
            "status": "success",
            "year": year,
            "monthly_breakdown": monthly_data,
            "summary": {
                "total_orders": total_orders,
                "total_sales": total_sales,
                "average_monthly_sales": total_sales / 12,
                "best_month": max(monthly_data, key=lambda x: x["total_sales"]) if monthly_data else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ ITEM-WISE REPORTS ============

@router.get("/sales/by-item")
async def get_item_wise_sales_report(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    store_id: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 100,
    db = Depends(get_db)
):
    """Get item-wise sales report - includes offline invoices"""
    try:
        from dateutil import parser
        
        now = datetime.now(timezone.utc)
        if from_date:
            start = parser.parse(from_date).replace(tzinfo=timezone.utc)
        else:
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if to_date:
            end = parser.parse(to_date).replace(tzinfo=timezone.utc)
        else:
            end = now
        
        start_str = start.isoformat()
        end_str = end.isoformat()
        
        # Get from orders collection
        orders_query = {
            "created_at": {"$gte": start, "$lte": end},
            "payment_status": {"$in": ["completed", "paid"]}
        }
        if store_id:
            orders_query["store_id"] = store_id
        
        pipeline = [
            {"$match": orders_query},
            {"$unwind": "$items"},
            {"$group": {
                "_id": "$items.product_id",
                "product_name": {"$first": "$items.product_name"},
                "quantity_sold": {"$sum": "$items.quantity"},
                "total_revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}},
                "order_count": {"$sum": 1},
                "avg_price": {"$avg": "$items.price"}
            }},
            {"$sort": {"total_revenue": -1}},
            {"$limit": limit}
        ]
        
        results = await db.orders.aggregate(pipeline).to_list(None)
        
        # Get from offline_invoices
        offline_query = {
            "created_at": {"$gte": start_str, "$lte": end_str}
        }
        if store_id:
            offline_query["store_code"] = store_id
        
        offline_invoices = await db.offline_invoices.find(
            offline_query,
            {"_id": 0, "items": 1}
        ).to_list(None)
        
        # Aggregate offline items
        offline_items = {}
        for inv in offline_invoices:
            for item in inv.get("items", []):
                product_id = item.get("product_id") or item.get("product_name")
                if product_id not in offline_items:
                    offline_items[product_id] = {
                        "_id": product_id,
                        "product_name": item.get("product_name", ""),
                        "quantity_sold": 0,
                        "total_revenue": 0,
                        "order_count": 0
                    }
                qty = item.get("quantity", 0)
                price = item.get("rate", 0) or item.get("price", 0)
                offline_items[product_id]["quantity_sold"] += qty
                offline_items[product_id]["total_revenue"] += qty * price
                offline_items[product_id]["order_count"] += 1
        
        # Merge results
        results_dict = {r["_id"]: r for r in results}
        for pid, data in offline_items.items():
            if pid in results_dict:
                results_dict[pid]["quantity_sold"] += data["quantity_sold"]
                results_dict[pid]["total_revenue"] += data["total_revenue"]
                results_dict[pid]["order_count"] += data["order_count"]
            else:
                results_dict[pid] = data
        
        final_results = sorted(results_dict.values(), key=lambda x: x.get("total_revenue", 0), reverse=True)[:limit]
        
        # Get product details
        for item in final_results:
            product = await db.products.find_one({"id": item["_id"]}, {"_id": 0, "category": 1, "sku": 1})
            if product:
                item["category"] = product.get("category", "")
                item["sku"] = product.get("sku", "")
        
        # Filter by category if specified
        if category:
            final_results = [r for r in final_results if r.get("category", "").lower() == category.lower()]
        
        return {
            "status": "success",
            "period": {"from": start.isoformat(), "to": end.isoformat()},
            "items": final_results,
            "summary": {
                "total_items": len(final_results),
                "total_revenue": round(sum(r.get("total_revenue", 0) for r in final_results), 2),
                "total_quantity": sum(r.get("quantity_sold", 0) for r in final_results)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/purchases/by-item")
async def get_item_wise_purchases_report(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    store_id: Optional[str] = None,
    limit: int = 100,
    db = Depends(get_db)
):
    """Get item-wise purchases report"""
    try:
        from dateutil import parser
        
        now = datetime.now(timezone.utc)
        if from_date:
            start = parser.parse(from_date).replace(tzinfo=timezone.utc)
        else:
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if to_date:
            end = parser.parse(to_date).replace(tzinfo=timezone.utc)
        else:
            end = now
        
        match_query = {"created_at": {"$gte": start, "$lte": end}}
        if store_id:
            match_query["store_id"] = store_id
        
        pipeline = [
            {"$match": match_query},
            {"$unwind": "$items"},
            {"$group": {
                "_id": "$items.product_id",
                "product_name": {"$first": "$items.product_name"},
                "quantity_purchased": {"$sum": "$items.quantity"},
                "total_cost": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}},
                "bill_count": {"$sum": 1},
                "avg_price": {"$avg": "$items.price"}
            }},
            {"$sort": {"total_cost": -1}},
            {"$limit": limit}
        ]
        
        results = await db.purchase_bills.aggregate(pipeline).to_list(None)
        
        return {
            "status": "success",
            "period": {"from": start.isoformat(), "to": end.isoformat()},
            "items": results,
            "summary": {
                "total_items": len(results),
                "total_cost": sum(r["total_cost"] for r in results),
                "total_quantity": sum(r["quantity_purchased"] for r in results)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ PENDING REPORTS ============

@router.get("/pending/deliveries")
async def get_pending_deliveries(
    store_id: Optional[str] = None,
    db = Depends(get_db)
):
    """Get all pending deliveries"""
    try:
        query = {
            "order_status": {"$in": ["confirmed", "processing", "shipped", "out_for_delivery"]},
            "payment_status": {"$in": ["completed", "paid", "cod"]}
        }
        if store_id:
            query["store_id"] = store_id
        
        orders = await db.orders.find(
            query,
            {"_id": 0}
        ).sort("created_at", 1).to_list(None)
        
        # Group by status
        status_breakdown = {}
        for o in orders:
            status = o.get("order_status", "unknown")
            if status not in status_breakdown:
                status_breakdown[status] = []
            status_breakdown[status].append({
                "order_id": o.get("id"),
                "order_number": o.get("order_number"),
                "customer_name": o.get("customer_name"),
                "total_amount": o.get("total_amount"),
                "created_at": o.get("created_at"),
                "shipping_address": o.get("shipping_address")
            })
        
        return {
            "status": "success",
            "total_pending": len(orders),
            "status_breakdown": status_breakdown,
            "orders": orders
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending/purchase-orders")
async def get_pending_purchase_orders(
    store_id: Optional[str] = None,
    db = Depends(get_db)
):
    """Get pending purchase orders"""
    try:
        query = {"status": {"$in": ["pending", "partial", "approved"]}}
        if store_id:
            query["store_id"] = store_id
        
        pos = await db.purchases.find(query, {"_id": 0}).sort("created_at", -1).to_list(None)
        
        # Calculate pending amounts
        total_pending = sum(p.get("total_amount", 0) for p in pos)
        
        return {
            "status": "success",
            "total_pending_orders": len(pos),
            "total_pending_amount": total_pending,
            "purchase_orders": pos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending/purchase-bills")
async def get_pending_purchase_bills(
    store_id: Optional[str] = None,
    db = Depends(get_db)
):
    """Get pending/unpaid purchase bills"""
    try:
        query = {"payment_status": {"$in": ["pending", "partial"]}}
        if store_id:
            query["store_id"] = store_id
        
        bills = await db.purchase_bills.find(query, {"_id": 0}).sort("due_date", 1).to_list(None)
        
        # Calculate totals
        total_pending = sum(b.get("total_amount", 0) for b in bills)
        total_paid = sum(b.get("paid_amount", 0) for b in bills)
        total_due = total_pending - total_paid
        
        # Mark overdue bills
        now = datetime.now(timezone.utc)
        for bill in bills:
            due_date = bill.get("due_date")
            if due_date:
                if isinstance(due_date, str):
                    from dateutil import parser
                    due_date = parser.parse(due_date)
                bill["is_overdue"] = due_date < now
        
        overdue_bills = [b for b in bills if b.get("is_overdue")]
        
        return {
            "status": "success",
            "total_pending_bills": len(bills),
            "total_pending_amount": total_pending,
            "total_paid_amount": total_paid,
            "total_due_amount": total_due,
            "overdue_count": len(overdue_bills),
            "bills": bills
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ SO/PO TRACKING ============

@router.get("/so/list")
async def get_sales_orders_list(
    status: Optional[str] = None,
    store_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Get list of Sales Orders with tracking"""
    try:
        query = {}
        if status:
            query["order_status"] = status
        if store_id:
            query["store_id"] = store_id
        
        if from_date or to_date:
            from dateutil import parser
            date_query = {}
            if from_date:
                date_query["$gte"] = parser.parse(from_date).replace(tzinfo=timezone.utc)
            if to_date:
                date_query["$lte"] = parser.parse(to_date).replace(tzinfo=timezone.utc)
            query["created_at"] = date_query
        
        orders = await db.orders.find(query, {"_id": 0}).sort("created_at", -1).to_list(None)
        
        # Status summary
        status_summary = {}
        for o in orders:
            s = o.get("order_status", "unknown")
            status_summary[s] = status_summary.get(s, 0) + 1
        
        return {
            "status": "success",
            "total_orders": len(orders),
            "status_summary": status_summary,
            "orders": orders
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/po/list")
async def get_purchase_orders_list(
    status: Optional[str] = None,
    store_id: Optional[str] = None,
    vendor_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Get list of Purchase Orders with tracking"""
    try:
        query = {}
        if status:
            query["status"] = status
        if store_id:
            query["store_id"] = store_id
        if vendor_id:
            query["vendor_id"] = vendor_id
        
        if from_date or to_date:
            from dateutil import parser
            date_query = {}
            if from_date:
                date_query["$gte"] = parser.parse(from_date).replace(tzinfo=timezone.utc)
            if to_date:
                date_query["$lte"] = parser.parse(to_date).replace(tzinfo=timezone.utc)
            query["created_at"] = date_query
        
        pos = await db.purchases.find(query, {"_id": 0}).sort("created_at", -1).to_list(None)
        
        # Status summary
        status_summary = {}
        for p in pos:
            s = p.get("status", "unknown")
            status_summary[s] = status_summary.get(s, 0) + 1
        
        return {
            "status": "success",
            "total_purchase_orders": len(pos),
            "status_summary": status_summary,
            "purchase_orders": pos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
