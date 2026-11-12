"""
In-App Notifications System
Real-time notifications for delivery team, store managers, and admin
With WebSocket push support for instant delivery
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timezone
from database import get_db
from pydantic import BaseModel
import uuid
import logging

# Import WebSocket push function
from websocket_manager import push_notification

router = APIRouter(prefix="/notifications", tags=["Notifications"])
logger = logging.getLogger(__name__)

# ============ MODELS ============

class NotificationCreate(BaseModel):
    recipient_type: str  # user, role, store, all
    recipient_id: Optional[str] = None  # user_id or store_id
    recipient_role: Optional[str] = None  # admin, delivery_team, store_manager, accountant
    title: str
    message: str
    type: str  # po_request, stock_transfer, order, delivery, alert, system
    priority: str = "normal"  # low, normal, high, urgent
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    metadata: Optional[dict] = None

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_archived: Optional[bool] = None

# ============ HELPER FUNCTIONS ============

async def create_notification(db, notification_data: dict):
    """Helper function to create a notification and push via WebSocket"""
    notification_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    notification = {
        "id": notification_id,
        "recipient_type": notification_data.get("recipient_type", "role"),
        "recipient_id": notification_data.get("recipient_id"),
        "recipient_role": notification_data.get("recipient_role"),
        "title": notification_data["title"],
        "message": notification_data["message"],
        "type": notification_data.get("type", "system"),
        "priority": notification_data.get("priority", "normal"),
        "action_url": notification_data.get("action_url"),
        "action_label": notification_data.get("action_label"),
        "metadata": notification_data.get("metadata", {}),
        "is_read": False,
        "is_archived": False,
        "created_at": now,
        "read_at": None
    }
    
    # Store in database
    await db.notifications.insert_one(notification)
    
    # Push via WebSocket for instant delivery
    try:
        # Prepare notification for WebSocket (convert datetime to string)
        ws_notification = {**notification, "created_at": now.isoformat()}
        await push_notification(ws_notification)
    except Exception as ws_error:
        logger.warning(f"WebSocket push failed (non-blocking): {ws_error}")
    
    return notification_id


async def notify_po_request_created(db, po_request: dict):
    """Notify admin and accounts team when a PO request is created"""
    await create_notification(db, {
        "recipient_type": "role",
        "recipient_role": "admin",
        "title": f"New PO Request: {po_request['request_number']}",
        "message": f"{po_request['store_name']} has submitted a purchase request for {po_request['total_items']} items.",
        "type": "po_request",
        "priority": "high" if po_request.get("urgency") == "urgent" else "normal",
        "action_url": f"/admin/accounting?tab=po-requests&id={po_request['id']}",
        "action_label": "Review Request",
        "metadata": {
            "po_request_id": po_request["id"],
            "request_number": po_request["request_number"],
            "store_id": po_request["store_id"],
            "store_name": po_request["store_name"],
            "total_items": po_request["total_items"]
        }
    })
    
    # Also notify accountant role
    await create_notification(db, {
        "recipient_type": "role",
        "recipient_role": "accountant",
        "title": f"PO Request Pending: {po_request['request_number']}",
        "message": f"Review and approve PO request from {po_request['store_name']}.",
        "type": "po_request",
        "priority": "normal",
        "action_url": f"/admin/accounting?tab=po-requests&id={po_request['id']}",
        "action_label": "Review",
        "metadata": {
            "po_request_id": po_request["id"],
            "request_number": po_request["request_number"]
        }
    })


async def notify_po_approved(db, po_request: dict, generated_po: dict = None):
    """Notify store manager when their PO request is approved"""
    await create_notification(db, {
        "recipient_type": "store",
        "recipient_id": po_request["store_id"],
        "title": f"PO Request Approved: {po_request['request_number']}",
        "message": f"Your purchase request has been approved. PO #{generated_po.get('po_number', 'N/A') if generated_po else 'N/A'} is ready.",
        "type": "po_request",
        "priority": "normal",
        "action_url": f"/store/dashboard?tab=po-requests",
        "action_label": "View Details",
        "metadata": {
            "po_request_id": po_request["id"],
            "po_number": generated_po.get("po_number") if generated_po else None
        }
    })


async def notify_stock_transfer_created(db, transfer: dict):
    """Notify warehouse/source store and delivery team about new transfer request"""
    # Notify source store (warehouse)
    await create_notification(db, {
        "recipient_type": "store",
        "recipient_id": transfer["from_store_id"],
        "title": f"Stock Transfer Request: {transfer['transfer_number']}",
        "message": f"{transfer['to_store_name']} has requested {transfer['total_quantity']} items for transfer.",
        "type": "stock_transfer",
        "priority": "high" if transfer.get("urgency") == "urgent" else "normal",
        "action_url": f"/store/dashboard?tab=transfers",
        "action_label": "Review Request",
        "metadata": {
            "transfer_id": transfer["id"],
            "transfer_number": transfer["transfer_number"],
            "from_store": transfer["from_store_name"],
            "to_store": transfer["to_store_name"]
        }
    })
    
    # Notify admin for approval
    await create_notification(db, {
        "recipient_type": "role",
        "recipient_role": "admin",
        "title": f"Transfer Pending Approval: {transfer['transfer_number']}",
        "message": f"Stock transfer from {transfer['from_store_name']} to {transfer['to_store_name']} needs approval.",
        "type": "stock_transfer",
        "priority": "normal",
        "action_url": f"/admin/store-management?tab=transfers",
        "action_label": "Approve/Reject",
        "metadata": {
            "transfer_id": transfer["id"],
            "transfer_number": transfer["transfer_number"]
        }
    })


async def notify_stock_transfer_approved(db, transfer: dict):
    """Notify delivery team when transfer is approved and ready for dispatch"""
    # Notify delivery team
    await create_notification(db, {
        "recipient_type": "role",
        "recipient_role": "delivery_team",
        "title": f"📦 New Dispatch: {transfer['transfer_number']}",
        "message": f"Transfer approved! Dispatch {transfer['total_quantity']} items from {transfer['from_store_name']} to {transfer['to_store_name']}.",
        "type": "stock_transfer",
        "priority": "high",
        "action_url": f"/delivery/transfers/{transfer['id']}",
        "action_label": "Start Dispatch",
        "metadata": {
            "transfer_id": transfer["id"],
            "transfer_number": transfer["transfer_number"],
            "from_store": transfer["from_store_name"],
            "to_store": transfer["to_store_name"],
            "total_items": transfer["total_items"],
            "total_quantity": transfer["total_quantity"]
        }
    })
    
    # Notify requesting store
    await create_notification(db, {
        "recipient_type": "store",
        "recipient_id": transfer["to_store_id"],
        "title": f"Transfer Approved: {transfer['transfer_number']}",
        "message": f"Your stock transfer request has been approved. Items will be dispatched soon.",
        "type": "stock_transfer",
        "priority": "normal",
        "action_url": f"/store/dashboard?tab=transfers",
        "action_label": "Track Transfer",
        "metadata": {
            "transfer_id": transfer["id"],
            "transfer_number": transfer["transfer_number"]
        }
    })


async def notify_stock_transfer_dispatched(db, transfer: dict):
    """Notify destination store when transfer is dispatched"""
    await create_notification(db, {
        "recipient_type": "store",
        "recipient_id": transfer["to_store_id"],
        "title": f"🚚 Stock In Transit: {transfer['transfer_number']}",
        "message": f"{transfer['total_quantity']} items dispatched from {transfer['from_store_name']}. Prepare to receive.",
        "type": "stock_transfer",
        "priority": "high",
        "action_url": f"/store/dashboard?tab=transfers",
        "action_label": "View Details",
        "metadata": {
            "transfer_id": transfer["id"],
            "transfer_number": transfer["transfer_number"]
        }
    })


async def notify_stock_transfer_received(db, transfer: dict):
    """Notify source store and admin when transfer is received"""
    await create_notification(db, {
        "recipient_type": "store",
        "recipient_id": transfer["from_store_id"],
        "title": f"✅ Transfer Complete: {transfer['transfer_number']}",
        "message": f"{transfer['to_store_name']} has received {transfer['total_quantity']} items.",
        "type": "stock_transfer",
        "priority": "normal",
        "action_url": f"/store/dashboard?tab=transfers",
        "action_label": "View Details",
        "metadata": {
            "transfer_id": transfer["id"],
            "transfer_number": transfer["transfer_number"]
        }
    })
    
    # Also notify admin
    await create_notification(db, {
        "recipient_type": "role",
        "recipient_role": "admin",
        "title": f"✅ Transfer Complete: {transfer['transfer_number']}",
        "message": f"Stock transfer from {transfer['from_store_name']} to {transfer['to_store_name']} completed successfully.",
        "type": "stock_transfer",
        "priority": "low",
        "action_url": f"/admin/store-management?tab=transfers",
        "action_label": "View",
        "metadata": {
            "transfer_id": transfer["id"],
            "transfer_number": transfer["transfer_number"]
        }
    })


async def notify_stock_inward(db, inward_data: dict):
    """Notify when stock is received at warehouse"""
    # Notify warehouse
    await create_notification(db, {
        "recipient_type": "store",
        "recipient_id": inward_data.get("warehouse_id") or inward_data.get("store_id"),
        "title": f"📦 Stock Inward: {inward_data.get('grn_number', 'GRN')}",
        "message": f"Received {inward_data.get('total_quantity', 0)} units of {inward_data.get('total_items', 0)} items from {inward_data.get('supplier_name', 'Supplier')}.",
        "type": "stock_inward",
        "priority": "normal",
        "action_url": f"/store/dashboard?tab=inventory",
        "action_label": "View Stock",
        "metadata": {
            "grn_number": inward_data.get("grn_number"),
            "supplier_name": inward_data.get("supplier_name"),
            "total_items": inward_data.get("total_items"),
            "total_quantity": inward_data.get("total_quantity"),
            "purchase_bill_id": inward_data.get("purchase_bill_id")
        }
    })
    
    # Notify admin
    await create_notification(db, {
        "recipient_type": "role",
        "recipient_role": "admin",
        "title": f"📦 Stock Inward at {inward_data.get('store_name', 'Warehouse')}",
        "message": f"GRN {inward_data.get('grn_number', 'N/A')}: {inward_data.get('total_quantity', 0)} units received from {inward_data.get('supplier_name', 'Supplier')}.",
        "type": "stock_inward",
        "priority": "normal",
        "action_url": f"/admin/accounting?tab=purchases",
        "action_label": "View Details",
        "metadata": inward_data
    })
    
    # Notify accountant
    await create_notification(db, {
        "recipient_type": "role",
        "recipient_role": "accountant",
        "title": f"📋 Purchase Bill Pending: {inward_data.get('grn_number', 'GRN')}",
        "message": f"Stock received from {inward_data.get('supplier_name', 'Supplier')}. Please verify and process payment.",
        "type": "stock_inward",
        "priority": "normal",
        "action_url": f"/admin/accounting?tab=purchases",
        "action_label": "Process",
        "metadata": inward_data
    })


async def notify_new_order(db, order: dict):
    """Notify when a new order is placed"""
    store_id = order.get("store_id")
    store_name = order.get("store_name", "Main Store")
    
    # Notify the store
    if store_id:
        await create_notification(db, {
            "recipient_type": "store",
            "recipient_id": store_id,
            "title": f"🛒 New Order: {order.get('order_number', order.get('id', 'N/A')[:8])}",
            "message": f"New order from {order.get('customer_name', 'Customer')} - ₹{order.get('total', 0):,.0f}. {order.get('item_count', 1)} item(s).",
            "type": "order",
            "priority": "high",
            "action_url": f"/store/dashboard?tab=orders&id={order.get('id')}",
            "action_label": "View Order",
            "metadata": {
                "order_id": order.get("id"),
                "order_number": order.get("order_number"),
                "customer_name": order.get("customer_name"),
                "total": order.get("total"),
                "payment_method": order.get("payment_method")
            }
        })
    
    # Notify admin
    await create_notification(db, {
        "recipient_type": "role",
        "recipient_role": "admin",
        "title": f"🛒 New Order: {order.get('order_number', order.get('id', 'N/A')[:8])}",
        "message": f"Order placed at {store_name} by {order.get('customer_name', 'Customer')} - ₹{order.get('total', 0):,.0f}",
        "type": "order",
        "priority": "normal",
        "action_url": f"/admin/orders?id={order.get('id')}",
        "action_label": "View",
        "metadata": {
            "order_id": order.get("id"),
            "order_number": order.get("order_number"),
            "store_id": store_id,
            "store_name": store_name,
            "total": order.get("total")
        }
    })
    
    # Notify warehouse if order needs stock dispatch
    if order.get("requires_dispatch", True):
        await create_notification(db, {
            "recipient_type": "role",
            "recipient_role": "warehouse",
            "title": f"📦 Pack Order: {order.get('order_number', order.get('id', 'N/A')[:8])}",
            "message": f"Order ready for packing - {order.get('item_count', 1)} item(s) for {order.get('customer_name', 'Customer')}.",
            "type": "order",
            "priority": "high",
            "action_url": f"/warehouse/orders?id={order.get('id')}",
            "action_label": "Start Packing",
            "metadata": {
                "order_id": order.get("id"),
                "order_number": order.get("order_number"),
                "delivery_type": order.get("delivery_type", "standard")
            }
        })


async def notify_order_status_change(db, order: dict, old_status: str, new_status: str):
    """Notify relevant parties when order status changes"""
    order_number = order.get('order_number', order.get('id', 'N/A')[:8])
    
    status_messages = {
        "confirmed": ("✅ Order Confirmed", "Your order has been confirmed and is being processed."),
        "processing": ("🔄 Order Processing", "Your order is being prepared."),
        "packed": ("📦 Order Packed", "Your order has been packed and is ready for dispatch."),
        "shipped": ("🚚 Order Shipped", "Your order is on its way!"),
        "out_for_delivery": ("🛵 Out for Delivery", "Your order is out for delivery today."),
        "delivered": ("✅ Order Delivered", "Your order has been delivered successfully."),
        "cancelled": ("❌ Order Cancelled", "Your order has been cancelled."),
        "returned": ("↩️ Order Returned", "Your order return has been processed.")
    }
    
    title, message = status_messages.get(new_status, (f"Order Update: {new_status}", f"Order status changed to {new_status}"))
    
    # Notify customer
    if order.get("customer_id"):
        await create_notification(db, {
            "recipient_type": "user",
            "recipient_id": order["customer_id"],
            "title": f"{title}: #{order_number}",
            "message": message,
            "type": "order",
            "priority": "normal",
            "action_url": f"/my-account/orders/{order.get('id')}",
            "action_label": "Track Order",
            "metadata": {
                "order_id": order.get("id"),
                "order_number": order_number,
                "old_status": old_status,
                "new_status": new_status
            }
        })
    
    # Notify store for key status changes
    if new_status in ["cancelled", "returned"] and order.get("store_id"):
        await create_notification(db, {
            "recipient_type": "store",
            "recipient_id": order["store_id"],
            "title": f"{title}: #{order_number}",
            "message": f"Order {order_number} has been {new_status}.",
            "type": "order",
            "priority": "high" if new_status == "cancelled" else "normal",
            "action_url": f"/store/dashboard?tab=orders&id={order.get('id')}",
            "action_label": "View",
            "metadata": {
                "order_id": order.get("id"),
                "new_status": new_status
            }
        })


async def notify_delivery_assigned(db, delivery: dict):
    """Notify when delivery is assigned to a delivery person"""
    # Notify delivery person
    await create_notification(db, {
        "recipient_type": "user",
        "recipient_id": delivery.get("delivery_person_id"),
        "title": f"🚚 New Delivery: {delivery.get('order_number', 'Order')}",
        "message": f"Deliver to {delivery.get('customer_name', 'Customer')} at {delivery.get('delivery_address', {}).get('city', 'N/A')}.",
        "type": "delivery",
        "priority": "high",
        "action_url": f"/delivery/task/{delivery.get('id')}",
        "action_label": "Start Delivery",
        "metadata": {
            "delivery_id": delivery.get("id"),
            "order_id": delivery.get("order_id"),
            "customer_name": delivery.get("customer_name"),
            "customer_phone": delivery.get("customer_phone"),
            "delivery_address": delivery.get("delivery_address")
        }
    })
    
    # Notify store
    if delivery.get("store_id"):
        await create_notification(db, {
            "recipient_type": "store",
            "recipient_id": delivery["store_id"],
            "title": f"🚚 Delivery Assigned: {delivery.get('order_number', 'Order')}",
            "message": f"Assigned to {delivery.get('delivery_person_name', 'Delivery Partner')}.",
            "type": "delivery",
            "priority": "normal",
            "action_url": f"/store/dashboard?tab=deliveries",
            "action_label": "Track",
            "metadata": {
                "delivery_id": delivery.get("id"),
                "delivery_person": delivery.get("delivery_person_name")
            }
        })


async def notify_delivery_status_change(db, delivery: dict, new_status: str):
    """Notify when delivery status changes"""
    status_emojis = {
        "picked_up": "📦",
        "in_transit": "🚚",
        "out_for_delivery": "🛵",
        "delivered": "✅",
        "failed": "❌",
        "rescheduled": "📅"
    }
    
    emoji = status_emojis.get(new_status, "📋")
    
    # Notify customer
    if delivery.get("customer_id"):
        await create_notification(db, {
            "recipient_type": "user",
            "recipient_id": delivery["customer_id"],
            "title": f"{emoji} Delivery Update: {delivery.get('order_number', 'Order')}",
            "message": f"Your delivery is now {new_status.replace('_', ' ')}.",
            "type": "delivery",
            "priority": "high" if new_status in ["out_for_delivery", "delivered", "failed"] else "normal",
            "action_url": f"/track-order/{delivery.get('order_id')}",
            "action_label": "Track",
            "metadata": {
                "delivery_id": delivery.get("id"),
                "order_id": delivery.get("order_id"),
                "status": new_status
            }
        })
    
    # Notify store on completion or failure
    if new_status in ["delivered", "failed"] and delivery.get("store_id"):
        await create_notification(db, {
            "recipient_type": "store",
            "recipient_id": delivery["store_id"],
            "title": f"{emoji} Delivery {new_status.title()}: {delivery.get('order_number', 'Order')}",
            "message": f"Order to {delivery.get('customer_name', 'Customer')} - {new_status.replace('_', ' ')}.",
            "type": "delivery",
            "priority": "high" if new_status == "failed" else "normal",
            "action_url": f"/store/dashboard?tab=deliveries",
            "action_label": "View",
            "metadata": {
                "delivery_id": delivery.get("id"),
                "status": new_status
            }
        })
    
    # Notify admin on delivery completion
    if new_status == "delivered":
        await create_notification(db, {
            "recipient_type": "role",
            "recipient_role": "admin",
            "title": f"✅ Delivery Complete: {delivery.get('order_number', 'Order')}",
            "message": f"Delivered to {delivery.get('customer_name', 'Customer')} by {delivery.get('delivery_person_name', 'Driver')}.",
            "type": "delivery",
            "priority": "low",
            "action_url": f"/admin/orders",
            "action_label": "View",
            "metadata": {
                "delivery_id": delivery.get("id"),
                "order_id": delivery.get("order_id")
            }
        })


async def notify_low_stock_alert(db, product: dict, store: dict):
    """Notify when stock falls below threshold"""
    await create_notification(db, {
        "recipient_type": "store",
        "recipient_id": store.get("id"),
        "title": f"⚠️ Low Stock: {product.get('name', 'Product')}",
        "message": f"Only {product.get('current_stock', 0)} units left. Reorder level: {product.get('reorder_level', 10)}.",
        "type": "alert",
        "priority": "high",
        "action_url": f"/store/dashboard?tab=inventory&product={product.get('id')}",
        "action_label": "Reorder",
        "metadata": {
            "product_id": product.get("id"),
            "product_name": product.get("name"),
            "current_stock": product.get("current_stock"),
            "reorder_level": product.get("reorder_level"),
            "store_id": store.get("id")
        }
    })
    
    # Notify admin
    await create_notification(db, {
        "recipient_type": "role",
        "recipient_role": "admin",
        "title": f"⚠️ Low Stock Alert: {product.get('name', 'Product')}",
        "message": f"{store.get('name', 'Store')} has only {product.get('current_stock', 0)} units of {product.get('name')}.",
        "type": "alert",
        "priority": "normal",
        "action_url": f"/admin/inventory?product={product.get('id')}",
        "action_label": "View",
        "metadata": {
            "product_id": product.get("id"),
            "store_id": store.get("id"),
            "store_name": store.get("name"),
            "current_stock": product.get("current_stock")
        }
    })


# ============ API ENDPOINTS ============

@router.get("/")
async def get_notifications(
    user_id: Optional[str] = None,
    user_role: Optional[str] = None,
    store_id: Optional[str] = None,
    type: Optional[str] = None,
    is_read: Optional[bool] = None,
    is_archived: bool = False,
    page: int = 1,
    limit: int = 20,
    db = Depends(get_db)
):
    """Get notifications for a user/role/store"""
    try:
        # Base query - always filter archived
        query = {"is_archived": is_archived}
        
        # Build recipient conditions using OR (notification should match ANY of the provided identifiers)
        recipient_conditions = []
        
        if user_id:
            recipient_conditions.append({"recipient_type": "user", "recipient_id": user_id})
        
        if user_role:
            recipient_conditions.append({"recipient_type": "role", "recipient_role": user_role})
            recipient_conditions.append({"recipient_type": "role", "recipient_role": "all"})
        
        if store_id:
            recipient_conditions.append({"recipient_type": "store", "recipient_id": store_id})
            # Also match by store_id field directly for backwards compatibility
            recipient_conditions.append({"store_id": store_id})
        
        # Always include "all" type notifications
        recipient_conditions.append({"recipient_type": "all"})
        
        # Add recipient conditions to query using OR
        if recipient_conditions:
            query["$or"] = recipient_conditions
        
        if type:
            query["type"] = type
        
        if is_read is not None:
            query["is_read"] = is_read
        
        skip = (page - 1) * limit
        
        notifications = await db.notifications.find(
            query, {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.notifications.count_documents(query)
        unread_count = await db.notifications.count_documents({**query, "is_read": False})
        
        return {
            "status": "success",
            "notifications": notifications,
            "total": total,
            "unread_count": unread_count,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unread-count")
async def get_unread_count(
    user_role: Optional[str] = None,
    store_id: Optional[str] = None,
    db = Depends(get_db)
):
    """Get unread notification count"""
    try:
        query_conditions = [{"is_read": False, "is_archived": False}]
        
        if user_role:
            query_conditions.append({
                "$or": [
                    {"recipient_type": "role", "recipient_role": user_role},
                    {"recipient_type": "all"}
                ]
            })
        
        if store_id:
            query_conditions.append({
                "$or": [
                    {"recipient_type": "store", "recipient_id": store_id},
                    {"recipient_type": "all"}
                ]
            })
        
        query = {"$and": query_conditions} if len(query_conditions) > 1 else query_conditions[0]
        
        count = await db.notifications.count_documents(query)
        
        # Get priority breakdown
        high_priority = await db.notifications.count_documents({
            **query, "priority": {"$in": ["high", "urgent"]}
        })
        
        return {
            "status": "success",
            "unread_count": count,
            "high_priority_count": high_priority
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_notification_endpoint(
    notification: NotificationCreate,
    db = Depends(get_db)
):
    """Create a new notification (admin use)"""
    try:
        notification_id = await create_notification(db, notification.dict())
        
        return {
            "status": "success",
            "message": "Notification created",
            "notification_id": notification_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{notification_id}")
async def update_notification(
    notification_id: str,
    update: NotificationUpdate,
    db = Depends(get_db)
):
    """Update notification (mark as read/archived)"""
    try:
        update_data = {"updated_at": datetime.now(timezone.utc)}
        
        if update.is_read is not None:
            update_data["is_read"] = update.is_read
            if update.is_read:
                update_data["read_at"] = datetime.now(timezone.utc)
        
        if update.is_archived is not None:
            update_data["is_archived"] = update.is_archived
        
        result = await db.notifications.update_one(
            {"id": notification_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {
            "status": "success",
            "message": "Notification updated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-all-read")
async def mark_all_read(
    user_role: Optional[str] = None,
    store_id: Optional[str] = None,
    db = Depends(get_db)
):
    """Mark all notifications as read for a user/role/store"""
    try:
        query_conditions = [{"is_read": False}]
        
        if user_role:
            query_conditions.append({
                "$or": [
                    {"recipient_type": "role", "recipient_role": user_role},
                    {"recipient_type": "all"}
                ]
            })
        
        if store_id:
            query_conditions.append({
                "$or": [
                    {"recipient_type": "store", "recipient_id": store_id},
                    {"recipient_type": "all"}
                ]
            })
        
        query = {"$and": query_conditions} if len(query_conditions) > 1 else query_conditions[0]
        
        now = datetime.now(timezone.utc)
        result = await db.notifications.update_many(
            query,
            {"$set": {"is_read": True, "read_at": now}}
        )
        
        return {
            "status": "success",
            "message": f"Marked {result.modified_count} notifications as read"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{notification_id}")
async def delete_notification(notification_id: str, db = Depends(get_db)):
    """Delete a notification"""
    try:
        result = await db.notifications.delete_one({"id": notification_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {
            "status": "success",
            "message": "Notification deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
