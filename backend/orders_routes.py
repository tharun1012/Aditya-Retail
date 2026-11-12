from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List, Optional
import os
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from enterprise_models import Order, OrderStatus, PaymentStatus, OrderTimelineEvent
from fastapi.responses import StreamingResponse
import io
import csv as csv_module
from openpyxl import Workbook

# Import notification functions
from notifications_routes import notify_order_status_change, notify_new_order

router = APIRouter(prefix="/admin/orders", tags=["Orders"])

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

@router.get("/")
async def get_all_orders(
    status: Optional[str] = None,
    order_type: Optional[str] = None,  # "online" | "offline" | None (=all)
    store_code: Optional[str] = None,  # filter by store, e.g. "DAS" | "BNS" | "ART"
    date_from: Optional[str] = None,   # "YYYY-MM-DD" (inclusive, local calendar day)
    date_to: Optional[str] = None,     # "YYYY-MM-DD" (inclusive, local calendar day)
    page: int = 1,
    limit: int = 20
):
    """Get all orders with optional filters.

    order_type:
      - "online" -> only db.orders (real online e-commerce orders)
      - "offline" -> only db.offline_invoices (document_type == "invoice", all stores)
      - None/"all" -> both, merged and re-sorted by created_at

    store_code: exact match on store_code (offline invoices always have it;
      online orders only match if that field exists on the order doc).

    date_from/date_to: filtered against created_at (stored as an ISO-8601
      string), by simple lexicographic string range, so both bounds must be
      "YYYY-MM-DD" only -- day/time components are appended here.
    """
    try:
        def normalize_offline(doc):
            """Map an offline_invoices doc into the same shape as an orders doc."""
            return {
                "id": doc.get("id"),
                "order_number": doc.get("invoice_number"),
                "order_type": "offline",
                "customer_details": {
                    "name": (doc.get("customer") or {}).get("name"),
                    "email": (doc.get("customer") or {}).get("email"),
                    "phone": (doc.get("customer") or {}).get("phone"),
                },
                "items": doc.get("items", []),
                "total_amount": doc.get("total_amount"),
                "payment_status": doc.get("payment_status"),
                "order_status": doc.get("status"),
                "store_code": doc.get("store_code"),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at"),
            }

        def date_range_filter():
            """Build a Mongo range filter for created_at from date_from/date_to."""
            rng = {}
            if date_from:
                rng["$gte"] = f"{date_from}T00:00:00"
            if date_to:
                rng["$lte"] = f"{date_to}T23:59:59.999999"
            return rng

        online_docs = []
        offline_docs = []
        online_total = 0
        offline_total = 0
        fetch_cap = page * limit
        date_filter = date_range_filter()

        if order_type in (None, "all", "online"):
            online_query = {
                "$or": [
                    {"order_type": {"$ne": "offline"}},
                    {"order_type": {"$exists": False}},
                ]
            }
            if status:
                online_query["order_status"] = {"$in": ["placed", "pending"]} if status == "pending" else status
            if store_code:
                online_query["store_code"] = store_code
            if date_filter:
                online_query["created_at"] = date_filter
            cursor = db.orders.find(online_query, {"_id": 0}).sort("created_at", -1).limit(fetch_cap)
            online_docs = await cursor.to_list(length=fetch_cap)
            online_total = await db.orders.count_documents(online_query)

        if order_type in (None, "all", "offline"):
            offline_query = {"document_type": "invoice"}
            if status:
                offline_query["status"] = {"$in": ["pending_delivery"]} if status == "pending" else status
            if store_code:
                offline_query["store_code"] = store_code
            if date_filter:
                offline_query["created_at"] = date_filter
            cursor = db.offline_invoices.find(offline_query, {"_id": 0}).sort("created_at", -1).limit(fetch_cap)
            raw_offline = await cursor.to_list(length=fetch_cap)
            offline_total = await db.offline_invoices.count_documents(offline_query)
            offline_docs = [normalize_offline(d) for d in raw_offline]

        combined = online_docs + offline_docs
        combined.sort(key=lambda d: d.get("created_at") or "", reverse=True)

        total = online_total + offline_total
        skip = (page - 1) * limit
        paged = combined[skip: skip + limit]

        return {
            "status": "success",
            "orders": paged,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/track")
async def track_order(order_number: str, email: str):
    """Public order tracking endpoint"""
    try:
        # Find order by order number and email (for security)
        order = await db.orders.find_one({
            "order_number": order_number,
            "customer_details.email": email
        })
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found. Please check your order number and email.")
        
        # Remove sensitive data
        order.pop('_id', None)
        
        return {
            "status": "success",
            "order": order
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_orders(
    status: Optional[str] = None,
    order_type: Optional[str] = None,
    store_code: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    format: str = "xlsx"
):
    """Export ALL orders matching filters (no pagination) as XLSX or CSV."""
    try:
        def normalize_offline(doc):
            return {
                "id": doc.get("id"),
                "order_number": doc.get("invoice_number"),
                "order_type": "offline",
                "customer_details": {
                    "name": (doc.get("customer") or {}).get("name"),
                    "email": (doc.get("customer") or {}).get("email"),
                    "phone": (doc.get("customer") or {}).get("phone"),
                },
                "items": doc.get("items", []),
                "total_amount": doc.get("total_amount"),
                "payment_status": doc.get("payment_status"),
                "order_status": doc.get("status"),
                "store_code": doc.get("store_code"),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at"),
            }

        def date_range_filter():
            rng = {}
            if date_from:
                rng["$gte"] = f"{date_from}T00:00:00"
            if date_to:
                rng["$lte"] = f"{date_to}T23:59:59.999999"
            return rng

        date_filter = date_range_filter()
        online_docs = []
        offline_docs = []

        if order_type in (None, "all", "online"):
            online_query = {
                "$or": [
                    {"order_type": {"$ne": "offline"}},
                    {"order_type": {"$exists": False}},
                ]
            }
            if status:
                online_query["order_status"] = {"$in": ["placed", "pending"]} if status == "pending" else status
            if store_code:
                online_query["store_code"] = store_code
            if date_filter:
                online_query["created_at"] = date_filter
            cursor = db.orders.find(online_query, {"_id": 0}).sort("created_at", -1)
            online_docs = await cursor.to_list(length=None)

        if order_type in (None, "all", "offline"):
            offline_query = {"document_type": "invoice"}
            if status:
                offline_query["status"] = {"$in": ["pending_delivery"]} if status == "pending" else status
            if store_code:
                offline_query["store_code"] = store_code
            if date_filter:
                offline_query["created_at"] = date_filter
            cursor = db.offline_invoices.find(offline_query, {"_id": 0}).sort("created_at", -1)
            raw_offline = await cursor.to_list(length=None)
            offline_docs = [normalize_offline(d) for d in raw_offline]

        combined = online_docs + offline_docs
        combined.sort(key=lambda d: d.get("created_at") or "", reverse=True)

        headers = ["Order ID", "Customer Name", "Email", "Phone", "Date", "Items", "Total", "Order Status", "Payment Status", "Channel", "Store"]
        rows = []
        for o in combined:
            cust = o.get("customer_details") or {}
            rows.append({
                "Order ID": o.get("order_number") or o.get("id"),
                "Customer Name": cust.get("name"),
                "Email": cust.get("email"),
                "Phone": cust.get("phone"),
                "Date": (o.get("created_at") or "")[:10],
                "Items": len(o.get("items") or []),
                "Total": o.get("total_amount"),
                "Order Status": o.get("order_status"),
                "Payment Status": o.get("payment_status"),
                "Channel": o.get("order_type"),
                "Store": o.get("store_code"),
            })

        if format == "csv":
            buf = io.StringIO()
            writer = csv_module.DictWriter(buf, fieldnames=headers)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
            byte_buf = io.BytesIO(buf.getvalue().encode("utf-8-sig"))
            return StreamingResponse(
                byte_buf,
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=orders_export.csv"}
            )
        else:
            wb = Workbook()
            ws = wb.active
            ws.title = "Orders"
            ws.append(headers)
            for r in rows:
                ws.append([r[h] for h in headers])
            byte_buf = io.BytesIO()
            wb.save(byte_buf)
            byte_buf.seek(0)
            return StreamingResponse(
                byte_buf,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=orders_export.xlsx"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{order_id}")
async def get_order_details(order_id: str):
    """Get detailed information for a specific order"""
    try:
        order = await db.orders.find_one({"id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Remove MongoDB _id
        order.pop('_id', None)
        
        return {
            "status": "success",
            "order": order
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{order_id}/status")
async def update_order_status(order_id: str, new_status: str, message: Optional[str] = None):
    """Update order status"""
    try:
        order = await db.orders.find_one({"id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        old_status = order.get("order_status", "pending")
        
        # Create timeline event
        timeline_event = {
            "status": new_status,
            "timestamp": datetime.now().isoformat(),
            "message": message or f"Order status updated to {new_status}",
            "updated_by": "admin"
        }
        
        # Update order
        await db.orders.update_one(
            {"id": order_id},
            {
                "$set": {
                    "order_status": new_status,
                    "updated_at": datetime.now().isoformat()
                },
                "$push": {"timeline": timeline_event}
            }
        )
        
        # Customer lifecycle: auto-register warranty / reminders on delivery
        if new_status == "delivered" and old_status != "delivered":
            try:
                from customer_lifecycle import on_order_delivered
                await on_order_delivered(db, {**order, "order_status": "delivered"})
            except Exception as lifecycle_error:
                print(f"Lifecycle hook error (non-blocking): {lifecycle_error}")

            # admin delivered email (once only, shares the flag with the Shiprocket path)
            try:
                _notified = order.get("shipping_notifications") or {}
                _email = (order.get("customer_details") or {}).get("email")
                if _email and not _notified.get("delivered"):
                    from sendgrid_email_service import sendgrid_email_service
                    from shiprocket_tracking_service import _stage_email
                    _subj, _body = _stage_email("delivered", order, order.get("sr_awb_code"), order.get("sr_courier"))
                    _res = sendgrid_email_service.send_email(
                        to_email=_email, subject=_subj, body=_body, from_agent="delivery", html=True)
                    if _res and _res.get("status") in ("sent", "success"):
                        await db.orders.update_one(
                            {"id": order_id},
                            {"$set": {"shipping_notifications.delivered": datetime.now().isoformat()}})
            except Exception as _email_err:
                print(f"Delivered email error (non-blocking): {_email_err}")

        # Send notification for status change
        try:
            await notify_order_status_change(db, order, old_status, new_status)
        except Exception as notify_error:
            print(f"Notification error (non-blocking): {notify_error}")
        
        return {
            "status": "success",
            "message": "Order status updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{order_id}/payment-status")
async def update_payment_status(order_id: str, payment_status: str):
    """Update payment status (useful for COD orders)"""
    try:
        order = await db.orders.find_one({"id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Validate payment status
        valid_statuses = ["pending", "completed", "failed", "refunded"]
        if payment_status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid payment status. Must be one of: {valid_statuses}")
        
        # Update payment status
        await db.orders.update_one(
            {"id": order_id},
            {
                "$set": {
                    "payment_status": payment_status,
                    "updated_at": datetime.now().isoformat()
                }
            }
        )
        
        return {
            "status": "success",
            "message": f"Payment status updated to {payment_status}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{order_id}/tracking")
async def update_tracking_info(order_id: str, tracking_number: str, delivery_partner: str):
    """Update shipping tracking information"""
    try:
        result = await db.orders.update_one(
            {"id": order_id},
            {
                "$set": {
                    "tracking_number": tracking_number,
                    "delivery_partner": delivery_partner,
                    "updated_at": datetime.now().isoformat()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {
            "status": "success",
            "message": "Tracking information updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary")
async def get_order_stats(
    order_type: Optional[str] = None,
    status: Optional[str] = None,
    store_code: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    """Get order statistics summary.

    order_type:
      - "online"  -> only db.orders (real online orders)
      - "offline" -> only db.offline_invoices (document_type == "invoice", all stores)
      - None/"all" -> combined online + offline

    status, store_code, date_from/date_to mirror the same filters accepted
    by GET / (the orders list endpoint), so the summary tiles always match
    what the list is currently showing.
    """
    try:
        online_stats = {"total_orders": 0, "total_revenue": 0}
        offline_stats = {"total_orders": 0, "total_revenue": 0}
        status_counts = {
            "pending": 0, "confirmed": 0, "processing": 0,
            "shipped": 0, "delivered": 0, "cancelled": 0,
        }

        date_filter = {}
        if date_from:
            date_filter["$gte"] = f"{date_from}T00:00:00"
        if date_to:
            date_filter["$lte"] = f"{date_to}T23:59:59.999999"

        if order_type in (None, "all", "online"):
            # Exclude legacy/stray records that were mistakenly tagged
            # order_type: "offline" inside the orders collection (orphan
            # data from an untraced migration). Real offline sales now
            # live exclusively in offline_invoices.
            base_filter = {
                "$or": [
                    {"order_type": {"$ne": "offline"}},
                    {"order_type": {"$exists": False}},
                ]
            }
            if store_code:
                base_filter["store_code"] = store_code
            if date_filter:
                base_filter["created_at"] = date_filter
            if status:
                base_filter["order_status"] = {"$in": ["placed", "pending"]} if status == "pending" else status

            async def count_with_status(statuses):
                q = dict(base_filter)
                q["order_status"] = {"$in": statuses} if isinstance(statuses, list) else statuses
                return await db.orders.count_documents(q)

            status_counts["pending"] += await count_with_status(["pending", "placed"])
            status_counts["confirmed"] += await count_with_status("confirmed")
            status_counts["processing"] += await count_with_status("processing")
            status_counts["shipped"] += await count_with_status("shipped")
            status_counts["delivered"] += await count_with_status("delivered")
            status_counts["cancelled"] += await count_with_status("cancelled")

            online_stats["total_orders"] = await db.orders.count_documents(base_filter)

            revenue_filter = {
                **base_filter,
                "$or": [
                    {"order_status": "delivered"},
                    {"payment_status": {"$in": ["completed", "paid", "success", "captured", "successful"]}},
                ]
            }
            pipeline = [
                {"$match": revenue_filter},
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            result = await db.orders.aggregate(pipeline).to_list(1)
            online_stats["total_revenue"] = result[0]["total"] if result else 0

        if order_type in (None, "all", "offline"):
            base_filter = {"document_type": "invoice"}
            if store_code:
                base_filter["store_code"] = store_code
            if date_filter:
                base_filter["created_at"] = date_filter
            if status:
                base_filter["status"] = {"$in": ["pending_delivery"]} if status == "pending" else status

            offline_stats["total_orders"] = await db.offline_invoices.count_documents(base_filter)

            pending_filter = {**base_filter, "payment_status": "pending"}
            status_counts["pending"] += await db.offline_invoices.count_documents(pending_filter)

            delivered_filter = {**base_filter, "status": "ready_for_delivery"}
            status_counts["delivered"] += await db.offline_invoices.count_documents(delivered_filter)

            revenue_filter = {
                **base_filter,
                "payment_status": {"$in": ["paid", "completed", "success", "captured", "successful"]}
            }
            pipeline = [
                {"$match": revenue_filter},
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            result = await db.offline_invoices.aggregate(pipeline).to_list(1)
            offline_stats["total_revenue"] = result[0]["total"] if result else 0

        total_orders = online_stats["total_orders"] + offline_stats["total_orders"]
        total_revenue = online_stats["total_revenue"] + offline_stats["total_revenue"]
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        return {
            "status": "success",
            "data": {
                "status_breakdown": status_counts,
                "total_orders": total_orders,
                "total_revenue": total_revenue,
                "average_order_value": avg_order_value,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{order_id}/cancel")
async def cancel_order(order_id: str, reason: str):
    """Cancel an order"""
    try:
        order = await db.orders.find_one({"id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.get("order_status") in ["delivered", "cancelled"]:
            raise HTTPException(status_code=400, detail="Cannot cancel this order")
        
        # Update status to cancelled
        timeline_event = {
            "status": "cancelled",
            "timestamp": datetime.now().isoformat(),
            "message": f"Order cancelled. Reason: {reason}",
            "updated_by": "admin"
        }
        
        await db.orders.update_one(
            {"id": order_id},
            {
                "$set": {
                    "order_status": "cancelled",
                    "updated_at": datetime.now().isoformat()
                },
                "$push": {"timeline": timeline_event}
            }
        )
        
        return {
            "status": "success",
            "message": "Order cancelled successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{order_id}/refund")
async def process_refund(order_id: str, amount: float, reason: str):
    """Process refund for an order"""
    try:
        order = await db.orders.find_one({"id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Update payment status
        timeline_event = {
            "status": "refunded",
            "timestamp": datetime.now().isoformat(),
            "message": f"Refund of ₹{amount} processed. Reason: {reason}",
            "updated_by": "admin"
        }
        
        await db.orders.update_one(
            {"id": order_id},
            {
                "$set": {
                    "payment_status": "refunded",
                    "order_status": "refunded",
                    "updated_at": datetime.now().isoformat()
                },
                "$push": {"timeline": timeline_event}
            }
        )
        
        return {
            "status": "success",
            "message": "Refund processed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.delete("/clear/all")
async def clear_all_orders(confirm: bool = False):
    """Clear ALL orders (use with caution!)"""
    try:
        if not confirm:
            raise HTTPException(status_code=400, detail="Please confirm deletion by adding ?confirm=true")
        
        result = await db.orders.delete_many({})
        return {
            "status": "success",
            "message": f"Deleted {result.deleted_count} orders",
            "deleted_count": result.deleted_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ============ SALES INVOICE LOCKING ============

@router.get("/compliance/overdue-sales")
async def get_overdue_sales_invoices():
    """
    Get all overdue sales invoices
    Invoices with pending payment past due date are auto-locked
    """
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # Find all overdue unpaid sales
        overdue_orders = await db.orders.find({
            "due_date": {"$lt": today, "$exists": True, "$nin": ["", None]},
            "payment_status": {"$in": ["pending", "partial", "unpaid"]}
        }, {"_id": 0}).sort("due_date", 1).to_list(None)
        
        locked_invoices = []
        total_overdue = 0
        
        for order in overdue_orders:
            due_date = order.get("due_date", "")
            if due_date:
                days_overdue = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(due_date, "%Y-%m-%d")).days
            else:
                days_overdue = 0
            
            # Auto-lock status for overdue invoices
            is_locked = order.get("is_locked", days_overdue > 0)
            
            locked_invoices.append({
                "order_id": order.get("id") or order.get("order_id"),
                "order_number": order.get("order_number") or order.get("invoice_number"),
                "customer_name": order.get("customer_name"),
                "total_amount": order.get("total_amount", 0),
                "due_date": due_date,
                "days_overdue": days_overdue,
                "is_locked": is_locked,
                "locked_reason": "Overdue payment" if is_locked else None,
                "payment_status": order.get("payment_status"),
                "unlock_required_from": "super_admin"
            })
            
            total_overdue += order.get("total_amount", 0)
            
            # Mark as locked in DB if overdue
            if days_overdue > 0 and not order.get("is_locked"):
                await db.orders.update_one(
                    {"$or": [{"id": order.get("id")}, {"order_id": order.get("order_id")}]},
                    {"$set": {
                        "is_locked": True,
                        "locked_at": datetime.now(timezone.utc).isoformat(),
                        "locked_reason": "Auto-locked: Overdue payment"
                    }}
                )
        
        return {
            "status": "success",
            "summary": {
                "total_overdue_count": len(locked_invoices),
                "total_overdue_amount": total_overdue,
                "locked_count": sum(1 for o in locked_invoices if o["is_locked"])
            },
            "overdue_invoices": locked_invoices,
            "action_required": "Contact super admin to unlock invoices for further processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{order_id}/lock")
async def lock_sales_invoice(order_id: str, reason: str = "Manual lock"):
    """Lock a sales invoice - prevents modifications"""
    try:
        order = await db.orders.find_one({"$or": [{"id": order_id}, {"order_id": order_id}]})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        await db.orders.update_one(
            {"$or": [{"id": order_id}, {"order_id": order_id}]},
            {"$set": {
                "is_locked": True,
                "locked_at": datetime.now(timezone.utc).isoformat(),
                "locked_reason": reason,
                "locked_by": "system"
            }}
        )
        
        return {
            "status": "success",
            "message": f"Invoice {order.get('order_number', order_id)} has been locked",
            "locked_reason": reason
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{order_id}/unlock")
async def unlock_sales_invoice(
    order_id: str,
    unlock_reason: str,
    requested_by: str,
    approved_by_super_admin: bool = False
):
    """
    Unlock a sales invoice - SUPER ADMIN ONLY
    Must provide reason and super_admin approval
    """
    try:
        if not approved_by_super_admin:
            raise HTTPException(
                status_code=403,
                detail="Only super_admin can unlock invoices. Please get super_admin approval."
            )
        
        order = await db.orders.find_one({"$or": [{"id": order_id}, {"order_id": order_id}]})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if not order.get("is_locked"):
            return {
                "status": "success",
                "message": "Invoice is not locked"
            }
        
        await db.orders.update_one(
            {"$or": [{"id": order_id}, {"order_id": order_id}]},
            {"$set": {
                "is_locked": False,
                "unlocked_at": datetime.now(timezone.utc).isoformat(),
                "unlock_reason": unlock_reason,
                "unlock_requested_by": requested_by,
                "unlocked_by": "super_admin"
            }}
        )
        
        # Log unlock action for audit
        await db.audit_trail.insert_one({
            "id": str(uuid.uuid4()),
            "action": "INVOICE_UNLOCK",
            "entity_type": "order",
            "entity_id": order_id,
            "order_number": order.get("order_number", order_id),
            "previous_lock_reason": order.get("locked_reason"),
            "unlock_reason": unlock_reason,
            "requested_by": requested_by,
            "approved_by": "super_admin",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "status": "success",
            "message": f"Invoice {order.get('order_number', order_id)} has been unlocked by super_admin",
            "unlock_reason": unlock_reason,
            "requested_by": requested_by
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance/locked-invoices")
async def get_all_locked_invoices():
    """Get all currently locked sales invoices"""
    try:
        locked = await db.orders.find(
            {"is_locked": True},
            {"_id": 0}
        ).to_list(None)
        
        locked_summary = []
        for order in locked:
            locked_summary.append({
                "order_id": order.get("id") or order.get("order_id"),
                "order_number": order.get("order_number") or order.get("invoice_number"),
                "customer_name": order.get("customer_name"),
                "total_amount": order.get("total_amount", 0),
                "locked_at": order.get("locked_at"),
                "locked_reason": order.get("locked_reason"),
                "locked_by": order.get("locked_by", "system"),
                "due_date": order.get("due_date"),
                "payment_status": order.get("payment_status")
            })
        
        return {
            "status": "success",
            "total_locked": len(locked_summary),
            "total_locked_amount": sum(o["total_amount"] for o in locked_summary),
            "locked_invoices": locked_summary,
            "unlock_procedure": "Store/Sales manager must request unlock from super_admin with valid reason"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{order_id}/convert-to-so")
async def convert_order_to_sales_order(order_id: str, store_code: str):
    """Convert an online order to a Sales Order for a specific store"""
    from document_numbering_routes import get_next_document_number
    
    try:
        # Get the online order
        order = await db.orders.find_one({"id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Check if already converted
        if order.get("converted_to_so") or order.get("converted_to_invoice"):
            raise HTTPException(status_code=400, detail="Order has already been converted")
        
        # Get store details
        store = await db.stores.find_one({"code": store_code})
        if not store:
            raise HTTPException(status_code=404, detail=f"Store with code {store_code} not found")
        
        store_id = store.get("id")
        
        # Generate SO number using document numbering system
        so_number = await get_next_document_number(db, store_id, store_code, "sales_order")
        
        # Prepare items from online order
        items = []
        for item in order.get("items", []):
            items.append({
                "product_id": item.get("product_id"),
                "product_name": item.get("name") or item.get("product_name"),
                "model_number": item.get("model_number", ""),
                "quantity": item.get("quantity", 1),
                "unit_price": item.get("price") or item.get("unit_price", 0),
                "amount": (item.get("price") or item.get("unit_price", 0)) * item.get("quantity", 1),
                "gst_rate": item.get("gst_rate", 18),
                "hsn_code": item.get("hsn_code", "")
            })
        
        # Create Sales Order document
        so_doc = {
            "id": str(uuid.uuid4()),
            "invoice_number": so_number,
            "document_type": "sales_order",
            "store_code": store_code,
            "store_id": store_id,
            "store_name": store.get("name", store_code),
            "customer_name": order.get("customer_details", {}).get("name") or order.get("customer_name", "Online Customer"),
            "customer_email": order.get("customer_details", {}).get("email") or order.get("customer_email", ""),
            "customer_phone": order.get("customer_details", {}).get("phone") or order.get("customer_phone", ""),
            "customer_address": order.get("shipping_address", {}),
            "items": items,
            "subtotal": order.get("subtotal", sum(i.get("amount", 0) for i in items)),
            "total_tax": order.get("tax_amount", 0),
            "total_amount": order.get("total_amount", 0),
            "delivery_charges": order.get("delivery_charges", 0),
            "payment_method": order.get("payment_method", "online"),
            "payment_status": order.get("payment_status", "pending"),
            "status": "pending",
            "source": "online_order",
            "online_order_id": order_id,
            "online_order_number": order.get("order_number"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "notes": f"Converted from online order #{order.get('order_number', order_id)}"
        }
        
        # Insert Sales Order
        await db.offline_invoices.insert_one(so_doc)

        # Real-time accounting: SO is a booking (visibility only, no
        # journal entry) - matches the same rule used for offline SOs.
        try:
            from realtime_accounting import post_transaction_event
            await post_transaction_event(db, "sales_order_booking", {
                "id": so_doc["invoice_number"],
                "amount": so_doc["total_amount"],
                "tax": so_doc["total_tax"],
                "payment_method": so_doc["payment_method"],
                "payment_status": so_doc["payment_status"],
                "date": so_doc["created_at"],
                "items": so_doc["items"]
            })
        except Exception as e:
            print(f"⚠️ Real-time accounting failed for {so_doc['invoice_number']}: {e}")

        # Update original order to mark as converted
        await db.orders.update_one(
            {"id": order_id},
            {"$set": {
                "converted_to_so": True,
                "converted_so_id": so_doc["id"],
                "converted_so_number": so_number,
                "converted_to_store": store_code,
                "converted_at": datetime.now().isoformat(),
                "order_status": "processing"
            }}
        )
        
        return {
            "status": "success",
            "message": f"Order converted to Sales Order {so_number}",
            "so_id": so_doc["id"],
            "so_number": so_number,
            "store_code": store_code
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{order_id}/convert-to-invoice")
async def convert_order_to_invoice(order_id: str, store_code: str):
    """Convert an online order directly to an Invoice for a specific store"""
    from document_numbering_routes import get_next_document_number
    
    try:
        # Get the online order
        order = await db.orders.find_one({"id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Check if already converted
        if order.get("converted_to_so") or order.get("converted_to_invoice"):
            raise HTTPException(status_code=400, detail="Order has already been converted")
        
        # Get store details
        store = await db.stores.find_one({"code": store_code})
        if not store:
            raise HTTPException(status_code=404, detail=f"Store with code {store_code} not found")
        
        store_id = store.get("id")
        
        # Generate Invoice number using document numbering system
        invoice_number = await get_next_document_number(db, store_id, store_code, "invoice")
        
        # Prepare items from online order
        items = []
        for item in order.get("items", []):
            items.append({
                "product_id": item.get("product_id"),
                "product_name": item.get("name") or item.get("product_name"),
                "model_number": item.get("model_number", ""),
                "quantity": item.get("quantity", 1),
                "unit_price": item.get("price") or item.get("unit_price", 0),
                "amount": (item.get("price") or item.get("unit_price", 0)) * item.get("quantity", 1),
                "gst_rate": item.get("gst_rate", 18),
                "hsn_code": item.get("hsn_code", "")
            })
        
        # Create Invoice document
        invoice_doc = {
            "id": str(uuid.uuid4()),
            "invoice_number": invoice_number,
            "document_type": "invoice",
            "store_code": store_code,
            "store_id": store_id,
            "store_name": store.get("name", store_code),
            "customer_name": order.get("customer_details", {}).get("name") or order.get("customer_name", "Online Customer"),
            "customer_email": order.get("customer_details", {}).get("email") or order.get("customer_email", ""),
            "customer_phone": order.get("customer_details", {}).get("phone") or order.get("customer_phone", ""),
            "customer_address": order.get("shipping_address", {}),
            "items": items,
            "subtotal": order.get("subtotal", sum(i.get("amount", 0) for i in items)),
            "total_tax": order.get("tax_amount", 0),
            "total_amount": order.get("total_amount", 0),
            "delivery_charges": order.get("delivery_charges", 0),
            "payment_method": order.get("payment_method", "online"),
            "payment_status": order.get("payment_status", "pending"),
            "status": "pending_delivery",
            "source": "online_order",
            "online_order_id": order_id,
            "online_order_number": order.get("order_number"),
            "invoice_date": datetime.now().strftime("%Y-%m-%d"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "notes": f"Converted from online order #{order.get('order_number', order_id)}"
        }
        
        # Insert Invoice
        await db.offline_invoices.insert_one(invoice_doc)

        # Real-time accounting: this invoice doc doesn't track
        # is_inter_state/igst - falls back to the default 50/50
        # CGST/SGST split (same as the nightly batch would do for it).
        try:
            from realtime_accounting import post_transaction_event
            await post_transaction_event(db, "sale_offline", {
                "id": invoice_doc["invoice_number"],
                "amount": invoice_doc["total_amount"],
                "tax": invoice_doc["total_tax"],
                "payment_method": invoice_doc["payment_method"],
                "payment_status": invoice_doc["payment_status"],
                "date": invoice_doc["created_at"],
                "items": invoice_doc["items"]
            })
        except Exception as e:
            print(f"⚠️ Real-time accounting failed for {invoice_doc['invoice_number']}: {e}")

        # Update original order to mark as converted
        await db.orders.update_one(
            {"id": order_id},
            {"$set": {
                "converted_to_invoice": True,
                "converted_invoice_id": invoice_doc["id"],
                "converted_invoice_number": invoice_number,
                "converted_to_store": store_code,
                "converted_at": datetime.now().isoformat(),
                "order_status": "processing"
            }}
        )
        
        return {
            "status": "success",
            "message": f"Order converted to Invoice {invoice_number}",
            "invoice_id": invoice_doc["id"],
            "invoice_number": invoice_number,
            "store_code": store_code
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stores/list")
async def get_stores_for_conversion():
    """Get list of stores for order conversion dropdown"""
    try:
        stores = await db.stores.find(
            {"status": {"$ne": "inactive"}},
            {"_id": 0, "id": 1, "code": 1, "name": 1, "address": 1}
        ).to_list(None)
        
        return {
            "status": "success",
            "stores": stores
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cleanup-offline-orders")
async def cleanup_offline_orders():
    """Remove offline orders from the orders collection (one-time cleanup)"""
    try:
        # Count offline orders before deletion
        offline_count = await db.orders.count_documents({"order_type": "offline"})
        
        if offline_count == 0:
            return {
                "status": "success",
                "message": "No offline orders found in the orders collection",
                "deleted": 0
            }
        
        # Delete offline orders
        result = await db.orders.delete_many({"order_type": "offline"})
        
        return {
            "status": "success",
            "message": f"Cleaned up {result.deleted_count} offline orders from the orders collection",
            "deleted": result.deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{order_id}")
async def delete_order(order_id: str):
    """Delete a single order"""
    try:
        # Check if order exists
        order = await db.orders.find_one({"id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Delete the order
        result = await db.orders.delete_one({"id": order_id})
        
        if result.deleted_count > 0:
            return {
                "status": "success",
                "message": f"Order {order.get('order_number', order_id)} deleted successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete order")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

