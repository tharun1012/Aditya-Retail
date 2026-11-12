from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timezone
from database import get_db
from pydantic import BaseModel
import uuid
import random

# Import notification functions
from notifications_routes import notify_delivery_assigned, notify_delivery_status_change

router = APIRouter(prefix="/delivery", tags=["delivery"])

# Mock Shiprocket Models
class ShipmentCreate(BaseModel):
    order_id: str
    customer_name: str
    customer_phone: str
    customer_email: str
    shipping_address: str
    city: str
    pincode: str
    weight: float = 1.0  # kg
    length: float = 10.0  # cm
    breadth: float = 10.0  # cm
    height: float = 10.0  # cm

class TrackingUpdate(BaseModel):
    shipment_id: str
    status: str
    location: str
    remarks: Optional[str] = None

# Mock Shiprocket API responses
MOCK_COURIERS = ["Delhivery", "BlueDart", "DTDC", "Ecom Express", "Ekart"]
MOCK_DELIVERY_STATUSES = [
    "Order Placed",
    "Pickup Scheduled",
    "In Transit",
    "Out for Delivery",
    "Delivered",
    "Failed Delivery Attempt",
    "RTO Initiated",
    "Cancelled"
]

@router.post("/shipment/create")
async def create_shipment(
    shipment: ShipmentCreate,
    database = Depends(get_db)
):
    """
    Create a new shipment (Mock Shiprocket)
    """
    try:
        # Generate mock AWB and shipment ID
        awb_number = f"AWB{random.randint(100000000, 999999999)}"
        shipment_id = str(uuid.uuid4())
        courier = random.choice(MOCK_COURIERS)
        
        # Calculate estimated delivery date (3-7 days)
        estimated_days = random.randint(3, 7)
        
        # Create shipment record
        shipment_data = {
            "id": shipment_id,
            "shipment_id": shipment_id,
            "order_id": shipment.order_id,
            "awb_number": awb_number,
            "courier_name": courier,
            "customer_name": shipment.customer_name,
            "customer_phone": shipment.customer_phone,
            "customer_email": shipment.customer_email,
            "shipping_address": shipment.shipping_address,
            "city": shipment.city,
            "pincode": shipment.pincode,
            "weight": shipment.weight,
            "dimensions": {
                "length": shipment.length,
                "breadth": shipment.breadth,
                "height": shipment.height
            },
            "status": "Order Placed",
            "current_location": "Warehouse - Mumbai",
            "estimated_delivery_days": estimated_days,
            "tracking_history": [
                {
                    "status": "Order Placed",
                    "location": "Warehouse - Mumbai",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "remarks": "Shipment created successfully"
                }
            ],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await database.shipments.insert_one(shipment_data)
        
        # Update order with shipment details
        await database.orders.update_one(
            {"order_number": shipment.order_id},
            {
                "$set": {
                    "shipment_id": shipment_id,
                    "awb_number": awb_number,
                    "courier_name": courier,
                    "delivery_status": "Shipment Created",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Shipment created successfully",
            "data": {
                "shipment_id": shipment_id,
                "awb_number": awb_number,
                "courier_name": courier,
                "estimated_delivery_days": estimated_days,
                "status": "Order Placed"
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create shipment: {str(e)}")


@router.get("/shipment/track/{shipment_id}")
async def track_shipment(
    shipment_id: str,
    database = Depends(get_db)
):
    """
    Track shipment status (Mock Shiprocket)
    """
    try:
        shipment = await database.shipments.find_one({"shipment_id": shipment_id})
        
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        
        # Clean up MongoDB _id
        if "_id" in shipment:
            del shipment["_id"]
        
        return {
            "success": True,
            "data": shipment
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track shipment: {str(e)}")


@router.post("/shipment/update-status")
async def update_shipment_status(
    update: TrackingUpdate,
    database = Depends(get_db)
):
    """
    Update shipment tracking status
    """
    try:
        shipment = await database.shipments.find_one({"shipment_id": update.shipment_id})
        
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        
        # Add new tracking event
        tracking_event = {
            "status": update.status,
            "location": update.location,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "remarks": update.remarks or f"Status updated to {update.status}"
        }
        
        # Update shipment
        await database.shipments.update_one(
            {"shipment_id": update.shipment_id},
            {
                "$set": {
                    "status": update.status,
                    "current_location": update.location,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                "$push": {
                    "tracking_history": tracking_event
                }
            }
        )
        
        # Update order delivery status if delivered
        if update.status == "Delivered":
            order = await database.orders.find_one({"shipment_id": update.shipment_id})
            await database.orders.update_one(
                {"shipment_id": update.shipment_id},
                {
                    "$set": {
                        "delivery_status": "Delivered",
                        "status": "completed",
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            # Send delivery completed email
            if order and order.get("customer", {}).get("email"):
                try:
                    from email_notification_service import email_notification_service
                    await email_notification_service.send_delivery_completed(
                        customer_email=order["customer"]["email"],
                        customer_name=order["customer"].get("name", "Valued Customer"),
                        order_id=order.get("order_id", order.get("order_number", "N/A")),
                        delivered_at=datetime.now().strftime('%B %d, %Y at %I:%M %p')
                    )
                    print(f"✅ Delivery completed email sent")
                except Exception as email_error:
                    print(f"⚠️ Failed to send delivery email: {email_error}")
        
        # Send dispatch email when order goes in transit
        if update.status in ["In Transit", "Out for Delivery"]:
            order = await database.orders.find_one({"shipment_id": update.shipment_id})
            if order and order.get("customer", {}).get("email"):
                try:
                    from email_notification_service import email_notification_service
                    await email_notification_service.send_delivery_dispatched(
                        customer_email=order["customer"]["email"],
                        customer_name=order["customer"].get("name", "Valued Customer"),
                        order_id=order.get("order_id", order.get("order_number", "N/A")),
                        tracking_number=shipment.get("awb_number"),
                        delivery_partner=shipment.get("courier"),
                        expected_date=shipment.get("estimated_delivery")
                    )
                    print(f"✅ Dispatch notification email sent")
                except Exception as email_error:
                    print(f"⚠️ Failed to send dispatch email: {email_error}")
        
        # Send delivery status notification
        try:
            # Map shipment status to delivery status
            status_mapping = {
                "In Transit": "in_transit",
                "Out for Delivery": "out_for_delivery",
                "Delivered": "delivered",
                "Failed Delivery Attempt": "failed",
                "RTO Initiated": "returned"
            }
            mapped_status = status_mapping.get(update.status)
            
            if mapped_status:
                # Get order info for notification
                order = await database.orders.find_one({"shipment_id": update.shipment_id})
                if order:
                    delivery_data = {
                        "id": shipment.get("shipment_id"),
                        "order_id": order.get("id"),
                        "order_number": order.get("order_number", order.get("id", "")[:8]),
                        "customer_id": order.get("customer_id"),
                        "customer_name": shipment.get("customer_name"),
                        "store_id": order.get("store_id"),
                        "delivery_person_name": shipment.get("courier", "Delivery Partner")
                    }
                    await notify_delivery_status_change(database, delivery_data, mapped_status)
        except Exception as notify_error:
            print(f"Notification error (non-blocking): {notify_error}")
        
        return {
            "success": True,
            "message": "Shipment status updated successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")


@router.get("/shipments/pending")
async def get_pending_shipments(
    database = Depends(get_db)
):
    """
    Get orders pending shipment creation
    """
    try:
        # Find orders without shipment_id
        cursor = database.orders.find(
            {
                "$or": [
                    {"shipment_id": {"$exists": False}},
                    {"shipment_id": None}
                ],
                "payment_status": "completed"
            }
        )
        
        orders = await cursor.to_list(length=100)
        
        # Clean up MongoDB _id
        for order in orders:
            if "_id" in order:
                del order["_id"]
        
        return {
            "success": True,
            "count": len(orders),
            "data": orders
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pending shipments: {str(e)}")


@router.get("/shipments/active")
async def get_active_shipments(
    database = Depends(get_db)
):
    """
    Get active shipments (not delivered)
    """
    try:
        cursor = database.shipments.find(
            {"status": {"$nin": ["Delivered", "Cancelled", "RTO Initiated"]}}
        )
        
        shipments = await cursor.to_list(length=100)
        
        # Clean up MongoDB _id
        for shipment in shipments:
            if "_id" in shipment:
                del shipment["_id"]
        
        return {
            "success": True,
            "count": len(shipments),
            "data": shipments
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch active shipments: {str(e)}")


@router.get("/analytics/summary")
async def get_delivery_analytics(
    database = Depends(get_db)
):
    """
    Get delivery analytics summary
    """
    try:
        # Get total shipments
        total_shipments = await database.shipments.count_documents({})
        
        # Get delivered shipments
        delivered = await database.shipments.count_documents({"status": "Delivered"})
        
        # Get in-transit shipments
        in_transit = await database.shipments.count_documents(
            {"status": {"$in": ["In Transit", "Out for Delivery", "Pickup Scheduled"]}}
        )
        
        # Get pending shipments
        pending = await database.orders.count_documents(
            {
                "$or": [
                    {"shipment_id": {"$exists": False}},
                    {"shipment_id": None}
                ],
                "payment_status": "completed"
            }
        )
        
        # Get failed deliveries
        failed = await database.shipments.count_documents(
            {"status": {"$in": ["Failed Delivery Attempt", "RTO Initiated", "Cancelled"]}}
        )
        
        # Calculate delivery rate
        delivery_rate = (delivered / total_shipments * 100) if total_shipments > 0 else 0
        
        return {
            "success": True,
            "data": {
                "total_shipments": total_shipments,
                "delivered": delivered,
                "in_transit": in_transit,
                "pending": pending,
                "failed": failed,
                "delivery_rate": round(delivery_rate, 2),
                "average_delivery_days": 5  # Mock value
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")
