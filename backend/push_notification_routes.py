"""
Push Notification Routes for PWA
Handles push notification subscriptions and sending notifications
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from database import get_db
import json

router = APIRouter(prefix="/push", tags=["Push Notifications"])

class PushSubscription(BaseModel):
    subscription: Dict[str, Any]
    userId: Optional[str] = "guest"
    userAgent: Optional[str] = None
    timestamp: Optional[str] = None

class PushNotificationPayload(BaseModel):
    title: str
    body: str
    icon: Optional[str] = "/logo192.png"
    badge: Optional[str] = "/logo192.png"
    url: Optional[str] = "/"
    userId: Optional[str] = None
    userType: Optional[str] = "customer"  # customer, sales_staff, delivery_staff
    tag: Optional[str] = None
    actions: Optional[List[Dict[str, str]]] = None

@router.post("/subscribe")
async def subscribe_to_push(subscription_data: PushSubscription, db = Depends(get_db)):
    """Save push notification subscription"""
    try:
        # Store subscription in database
        subscription_doc = {
            "endpoint": subscription_data.subscription.get("endpoint"),
            "keys": subscription_data.subscription.get("keys", {}),
            "userId": subscription_data.userId,
            "userAgent": subscription_data.userAgent,
            "subscribed_at": datetime.now(timezone.utc).isoformat(),
            "active": True
        }
        
        # Check if subscription already exists
        existing = await db.push_subscriptions.find_one({
            "endpoint": subscription_doc["endpoint"]
        }, {"_id": 0})
        
        if existing:
            # Update existing subscription
            await db.push_subscriptions.update_one(
                {"endpoint": subscription_doc["endpoint"]},
                {"$set": subscription_doc}
            )
        else:
            # Insert new subscription
            await db.push_subscriptions.insert_one(subscription_doc)
        
        return {
            "status": "success",
            "message": "Push notification subscription saved"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/unsubscribe")
async def unsubscribe_from_push(data: Dict[str, str], db = Depends(get_db)):
    """Remove push notification subscription"""
    try:
        endpoint = data.get("endpoint")
        
        if not endpoint:
            raise HTTPException(status_code=400, detail="Endpoint required")
        
        # Mark subscription as inactive
        result = await db.push_subscriptions.update_one(
            {"endpoint": endpoint},
            {"$set": {"active": False, "unsubscribed_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        return {
            "status": "success",
            "message": "Unsubscribed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send")
async def send_push_notification(
    payload: PushNotificationPayload,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """
    Send push notification to user(s)
    Note: Actual push sending requires web-push library and VAPID keys
    This endpoint prepares the notification for sending
    """
    try:
        # Get subscriptions based on userId or userType
        query = {"active": True}
        
        if payload.userId:
            query["userId"] = payload.userId
        
        subscriptions = await db.push_subscriptions.find(query, {"_id": 0}).to_list(1000)
        
        if not subscriptions:
            return {
                "status": "info",
                "message": "No active subscriptions found",
                "sent_count": 0
            }
        
        # Store notification in database for tracking
        notification_doc = {
            "title": payload.title,
            "body": payload.body,
            "icon": payload.icon,
            "url": payload.url,
            "userId": payload.userId,
            "userType": payload.userType,
            "tag": payload.tag,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "recipient_count": len(subscriptions),
            "status": "queued"
        }
        
        await db.push_notifications.insert_one(notification_doc)
        
        # In production, you would send actual push notifications here using web-push library
        # For now, we're just storing the notification
        print(f"[Push] Notification queued for {len(subscriptions)} subscribers")
        print(f"[Push] Title: {payload.title}")
        print(f"[Push] Body: {payload.body}")
        
        return {
            "status": "success",
            "message": "Notification queued for delivery",
            "sent_count": len(subscriptions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscriptions")
async def get_push_subscriptions(user_id: Optional[str] = None, db = Depends(get_db)):
    """Get push notification subscriptions"""
    try:
        query = {"active": True}
        if user_id:
            query["userId"] = user_id
        
        subscriptions = await db.push_subscriptions.find(query, {"_id": 0}).to_list(1000)
        
        return {
            "status": "success",
            "count": len(subscriptions),
            "subscriptions": subscriptions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notifications/history")
async def get_notification_history(
    user_id: Optional[str] = None,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get notification history"""
    try:
        query = {}
        if user_id:
            query["userId"] = user_id
        
        notifications = await db.push_notifications.find(
            query,
            {"_id": 0}
        ).sort("sent_at", -1).limit(limit).to_list(limit)
        
        return {
            "status": "success",
            "count": len(notifications),
            "notifications": notifications
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions for sending notifications to specific user types

async def notify_customer(db, customer_id: str, title: str, body: str, url: str = "/"):
    """Send notification to a specific customer"""
    notification = PushNotificationPayload(
        title=title,
        body=body,
        url=url,
        userId=customer_id,
        userType="customer"
    )
    # This would trigger actual push notification in production
    print(f"[Push] Customer notification: {title} to {customer_id}")

async def notify_sales_staff(db, title: str, body: str, url: str = "/admin"):
    """Send notification to all sales staff"""
    notification = PushNotificationPayload(
        title=title,
        body=body,
        url=url,
        userType="sales_staff"
    )
    print(f"[Push] Sales staff notification: {title}")

async def notify_delivery_staff(db, staff_id: str, title: str, body: str, url: str = "/delivery-dashboard"):
    """Send notification to delivery staff"""
    notification = PushNotificationPayload(
        title=title,
        body=body,
        url=url,
        userId=staff_id,
        userType="delivery_staff"
    )
    print(f"[Push] Delivery staff notification: {title} to {staff_id}")
