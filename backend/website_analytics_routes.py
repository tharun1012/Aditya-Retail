"""
Website Analytics Routes
Provides analytics for AI Chat, Expert Consultations, and Abandoned Carts
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, EmailStr
import os

from database import get_db

router = APIRouter(prefix="/website-analytics", tags=["Website Analytics"])


# ======================= AI CHAT ANALYTICS =======================

@router.get("/ai-chat/summary")
async def get_ai_chat_summary(
    days: int = 30,
    db = Depends(get_db)
):
    """
    Get AI chat analytics summary
    """
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_str = cutoff_date.isoformat()
        
        # Total messages
        total_messages = await db.chat_messages.count_documents({})
        recent_messages = await db.chat_messages.count_documents({
            "timestamp": {"$gte": cutoff_str}
        })
        
        # Total unique sessions
        all_sessions = await db.chat_messages.distinct("session_id")
        total_sessions = len(all_sessions)
        
        # Recent unique sessions
        recent_sessions_cursor = db.chat_messages.aggregate([
            {"$match": {"timestamp": {"$gte": cutoff_str}}},
            {"$group": {"_id": "$session_id"}}
        ])
        recent_sessions = len(await recent_sessions_cursor.to_list(10000))
        
        # Agent type breakdown
        agent_breakdown = await db.chat_messages.aggregate([
            {"$group": {
                "_id": "$agent_type",
                "count": {"$sum": 1}
            }}
        ]).to_list(100)
        
        # Daily message trend (last N days)
        daily_trend = await db.chat_messages.aggregate([
            {"$match": {"timestamp": {"$gte": cutoff_str}}},
            {"$addFields": {
                "date": {"$substr": ["$timestamp", 0, 10]}
            }},
            {"$group": {
                "_id": "$date",
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]).to_list(100)
        
        # User vs AI message breakdown
        sender_breakdown = await db.chat_messages.aggregate([
            {"$group": {
                "_id": "$sender",
                "count": {"$sum": 1}
            }}
        ]).to_list(10)
        
        # Average messages per session
        avg_messages_pipeline = await db.chat_messages.aggregate([
            {"$group": {
                "_id": "$session_id",
                "message_count": {"$sum": 1}
            }},
            {"$group": {
                "_id": None,
                "avg_messages": {"$avg": "$message_count"},
                "max_messages": {"$max": "$message_count"},
                "min_messages": {"$min": "$message_count"}
            }}
        ]).to_list(1)
        
        avg_stats = avg_messages_pipeline[0] if avg_messages_pipeline else {
            "avg_messages": 0, "max_messages": 0, "min_messages": 0
        }
        
        return {
            "status": "success",
            "summary": {
                "total_messages": total_messages,
                "recent_messages": recent_messages,
                "total_sessions": total_sessions,
                "recent_sessions": recent_sessions,
                "avg_messages_per_session": round(avg_stats.get("avg_messages", 0), 2),
                "max_messages_in_session": avg_stats.get("max_messages", 0),
                "period_days": days
            },
            "agent_breakdown": {item["_id"]: item["count"] for item in agent_breakdown if item["_id"]},
            "sender_breakdown": {item["_id"]: item["count"] for item in sender_breakdown if item["_id"]},
            "daily_trend": [{"date": item["_id"], "count": item["count"]} for item in daily_trend]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-chat/sessions")
async def get_ai_chat_sessions(
    page: int = 1,
    limit: int = 20,
    agent_type: Optional[str] = None,
    search: Optional[str] = None,
    db = Depends(get_db)
):
    """
    Get list of AI chat sessions with details
    """
    try:
        skip = (page - 1) * limit
        
        # Build aggregation pipeline to get session summaries
        match_stage = {}
        if agent_type:
            match_stage["agent_type"] = agent_type
        
        pipeline = [
            {"$match": match_stage} if match_stage else {"$match": {}},
            {"$group": {
                "_id": "$session_id",
                "agent_types": {"$addToSet": "$agent_type"},
                "message_count": {"$sum": 1},
                "first_message": {"$min": "$timestamp"},
                "last_message": {"$max": "$timestamp"},
                "user_messages": {"$sum": {"$cond": [{"$eq": ["$sender", "user"]}, 1, 0]}},
                "ai_messages": {"$sum": {"$cond": [{"$eq": ["$sender", "ai"]}, 1, 0]}},
                "sample_messages": {"$push": {
                    "sender": "$sender",
                    "message": {"$substrCP": ["$message", 0, 100]},
                    "timestamp": "$timestamp"
                }}
            }},
            {"$sort": {"last_message": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ]
        
        sessions = await db.chat_messages.aggregate(pipeline).to_list(limit)
        
        # Get total count
        total_pipeline = [
            {"$match": match_stage} if match_stage else {"$match": {}},
            {"$group": {"_id": "$session_id"}},
            {"$count": "total"}
        ]
        total_result = await db.chat_messages.aggregate(total_pipeline).to_list(1)
        total = total_result[0]["total"] if total_result else 0
        
        # Format response
        formatted_sessions = []
        for session in sessions:
            # Get first user message as preview
            first_user_msg = next(
                (m for m in sorted(session.get("sample_messages", []), 
                                   key=lambda x: x.get("timestamp", ""))
                 if m.get("sender") == "user"),
                None
            )
            
            formatted_sessions.append({
                "session_id": session["_id"],
                "agent_types": session.get("agent_types", []),
                "message_count": session.get("message_count", 0),
                "user_messages": session.get("user_messages", 0),
                "ai_messages": session.get("ai_messages", 0),
                "first_message": session.get("first_message"),
                "last_message": session.get("last_message"),
                "preview": first_user_msg.get("message", "")[:100] if first_user_msg else ""
            })
        
        return {
            "status": "success",
            "sessions": formatted_sessions,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit if total > 0 else 1
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-chat/session/{session_id}")
async def get_chat_session_detail(
    session_id: str,
    db = Depends(get_db)
):
    """
    Get full conversation for a specific session
    """
    try:
        messages = await db.chat_messages.find(
            {"session_id": session_id},
            {"_id": 0}
        ).sort("timestamp", 1).to_list(1000)
        
        if not messages:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "status": "success",
            "session_id": session_id,
            "message_count": len(messages),
            "messages": messages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================= EXPERT CONSULTATIONS =======================

@router.get("/consultations/summary")
async def get_consultations_summary(
    days: int = 30,
    db = Depends(get_db)
):
    """
    Get expert consultation analytics summary
    """
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_str = cutoff_date.isoformat()
        
        # Total consultations
        total_consultations = await db.consultations.count_documents({})
        recent_consultations = await db.consultations.count_documents({
            "created_at": {"$gte": cutoff_str}
        })
        
        # Status breakdown
        status_breakdown = await db.consultations.aggregate([
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]).to_list(100)
        
        # Email sent stats
        emails_sent = await db.consultations.count_documents({"email_sent": True})
        
        # Budget range analysis
        budget_analysis = await db.consultations.aggregate([
            {"$match": {"requirements.budget_min": {"$exists": True}}},
            {"$group": {
                "_id": None,
                "avg_budget_min": {"$avg": "$requirements.budget_min"},
                "avg_budget_max": {"$avg": "$requirements.budget_max"},
                "max_budget": {"$max": "$requirements.budget_max"},
                "min_budget": {"$min": "$requirements.budget_min"}
            }}
        ]).to_list(1)
        
        budget_stats = budget_analysis[0] if budget_analysis else {}
        
        # Appliance interest breakdown
        appliance_interests = await db.consultations.aggregate([
            {"$unwind": "$requirements.appliance_types"},
            {"$group": {
                "_id": "$requirements.appliance_types",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]).to_list(10)
        
        # Daily trend
        daily_trend = await db.consultations.aggregate([
            {"$match": {"created_at": {"$gte": cutoff_str}}},
            {"$addFields": {
                "date": {"$substr": ["$created_at", 0, 10]}
            }},
            {"$group": {
                "_id": "$date",
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]).to_list(100)
        
        return {
            "status": "success",
            "summary": {
                "total_consultations": total_consultations,
                "recent_consultations": recent_consultations,
                "pending": next((s["count"] for s in status_breakdown if s["_id"] == "pending"), 0),
                "completed": next((s["count"] for s in status_breakdown if s["_id"] == "completed"), 0),
                "emails_sent": emails_sent,
                "period_days": days
            },
            "budget_stats": {
                "avg_budget_min": round(budget_stats.get("avg_budget_min", 0), 0),
                "avg_budget_max": round(budget_stats.get("avg_budget_max", 0), 0),
                "max_budget": budget_stats.get("max_budget", 0),
                "min_budget": budget_stats.get("min_budget", 0)
            },
            "appliance_interests": [{"appliance": item["_id"], "count": item["count"]} for item in appliance_interests],
            "status_breakdown": {item["_id"]: item["count"] for item in status_breakdown if item["_id"]},
            "daily_trend": [{"date": item["_id"], "count": item["count"]} for item in daily_trend]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consultations/list")
async def get_consultations_list(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db = Depends(get_db)
):
    """
    Get list of consultations with filtering
    """
    try:
        skip = (page - 1) * limit
        
        query = {}
        if status:
            query["status"] = status
        if search:
            query["$or"] = [
                {"customer_name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"phone": {"$regex": search, "$options": "i"}}
            ]
        
        consultations = await db.consultations.find(
            query,
            {"_id": 0, "report": 0}  # Exclude large report field
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        total = await db.consultations.count_documents(query)
        
        return {
            "status": "success",
            "consultations": consultations,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit if total > 0 else 1
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================= ABANDONED CARTS =======================

@router.get("/abandoned-carts/summary")
async def get_abandoned_carts_summary(
    days: int = 30,
    db = Depends(get_db)
):
    """
    Get abandoned cart analytics summary
    """
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_str = cutoff_date.isoformat()
        
        # Total carts
        total_carts = await db.carts.count_documents({})
        
        # Recent carts
        recent_carts = await db.carts.count_documents({
            "$or": [
                {"created_at": {"$gte": cutoff_str}},
                {"created_at": {"$gte": cutoff_date}}  # Handle both string and datetime
            ]
        })
        
        # Carts with items (non-empty)
        carts_with_items = await db.carts.count_documents({
            "items": {"$exists": True, "$ne": []}
        })
        
        # Total cart value calculation
        carts_cursor = db.carts.find(
            {"items": {"$exists": True, "$ne": []}},
            {"_id": 0, "items": 1, "session_id": 1, "user_id": 1, "created_at": 1, "updated_at": 1}
        )
        
        all_carts = await carts_cursor.to_list(10000)
        
        total_value = 0
        high_value_carts = 0
        product_ids = set()
        
        for cart in all_carts:
            cart_value = 0
            for item in cart.get("items", []):
                product_id = item.get("product_id")
                quantity = item.get("quantity", 1)
                if product_id:
                    product_ids.add(product_id)
                    # Fetch product price
                    product = await db.products.find_one({"id": product_id}, {"price": 1})
                    if product:
                        cart_value += product.get("price", 0) * quantity
            
            total_value += cart_value
            if cart_value >= 50000:  # High value threshold: 50K
                high_value_carts += 1
        
        # Get most abandoned products
        abandoned_products = await db.carts.aggregate([
            {"$unwind": "$items"},
            {"$group": {
                "_id": "$items.product_id",
                "abandonment_count": {"$sum": 1},
                "total_quantity": {"$sum": "$items.quantity"}
            }},
            {"$sort": {"abandonment_count": -1}},
            {"$limit": 10}
        ]).to_list(10)
        
        # Enrich with product names
        enriched_products = []
        for item in abandoned_products:
            product = await db.products.find_one({"id": item["_id"]}, {"name": 1, "price": 1, "image": 1})
            if product:
                enriched_products.append({
                    "product_id": item["_id"],
                    "name": product.get("name", "Unknown"),
                    "price": product.get("price", 0),
                    "image": product.get("image"),
                    "abandonment_count": item["abandonment_count"],
                    "total_quantity": item["total_quantity"]
                })
        
        # Daily trend
        # Handle both datetime objects and ISO strings in created_at
        daily_trend = []
        for cart in all_carts:
            created = cart.get("created_at")
            if created:
                if isinstance(created, datetime):
                    date_str = created.strftime("%Y-%m-%d")
                else:
                    date_str = str(created)[:10]
                
                existing = next((d for d in daily_trend if d["date"] == date_str), None)
                if existing:
                    existing["count"] += 1
                else:
                    daily_trend.append({"date": date_str, "count": 1})
        
        daily_trend.sort(key=lambda x: x["date"])
        
        return {
            "status": "success",
            "summary": {
                "total_carts": total_carts,
                "recent_carts": recent_carts,
                "carts_with_items": carts_with_items,
                "total_potential_value": round(total_value, 2),
                "high_value_carts": high_value_carts,
                "unique_products_in_carts": len(product_ids),
                "period_days": days
            },
            "most_abandoned_products": enriched_products,
            "daily_trend": daily_trend[-30:]  # Last 30 days only
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/abandoned-carts/list")
async def get_abandoned_carts_list(
    page: int = 1,
    limit: int = 20,
    min_value: Optional[float] = None,
    has_user: Optional[bool] = None,
    db = Depends(get_db)
):
    """
    Get list of abandoned carts with details
    """
    try:
        skip = (page - 1) * limit
        
        query = {"items": {"$exists": True, "$ne": []}}
        
        if has_user is True:
            query["user_id"] = {"$exists": True, "$ne": None}
        elif has_user is False:
            query["$or"] = [
                {"user_id": {"$exists": False}},
                {"user_id": None}
            ]
        
        # Fetch carts
        carts_cursor = db.carts.find(query, {"_id": 0}).sort("updated_at", -1).skip(skip).limit(limit)
        carts = await carts_cursor.to_list(limit)
        
        total = await db.carts.count_documents(query)
        
        # Enrich carts with product details and calculate values
        enriched_carts = []
        for cart in carts:
            cart_items = []
            cart_value = 0
            
            for item in cart.get("items", []):
                product = await db.products.find_one(
                    {"id": item.get("product_id")},
                    {"name": 1, "price": 1, "image": 1}
                )
                if product:
                    item_value = product.get("price", 0) * item.get("quantity", 1)
                    cart_value += item_value
                    cart_items.append({
                        "product_id": item.get("product_id"),
                        "name": product.get("name", "Unknown"),
                        "price": product.get("price", 0),
                        "image": product.get("image"),
                        "quantity": item.get("quantity", 1),
                        "item_value": item_value
                    })
            
            # Filter by min_value if specified
            if min_value and cart_value < min_value:
                continue
            
            # Try to get user info if user_id exists
            user_info = None
            if cart.get("user_id"):
                user = await db.users.find_one(
                    {"id": cart["user_id"]},
                    {"name": 1, "email": 1, "phone": 1}
                )
                if user:
                    user_info = {
                        "name": user.get("name"),
                        "email": user.get("email"),
                        "phone": user.get("phone")
                    }
            
            enriched_carts.append({
                "id": cart.get("id"),
                "session_id": cart.get("session_id"),
                "user_id": cart.get("user_id"),
                "user_info": user_info,
                "items": cart_items,
                "item_count": len(cart_items),
                "cart_value": cart_value,
                "created_at": cart.get("created_at"),
                "updated_at": cart.get("updated_at"),
                "recovery_email_sent": cart.get("recovery_email_sent", False),
                "recovery_email_sent_at": cart.get("recovery_email_sent_at")
            })
        
        return {
            "status": "success",
            "carts": enriched_carts,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit if total > 0 else 1
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================= CART RECOVERY ACTIONS =======================

class RecoveryEmailRequest(BaseModel):
    cart_id: Optional[str] = None
    session_id: Optional[str] = None
    email: EmailStr
    custom_message: Optional[str] = None


@router.post("/abandoned-carts/send-recovery-email")
async def send_cart_recovery_email(
    request: RecoveryEmailRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """
    Send a recovery email for an abandoned cart
    """
    try:
        # Find the cart
        query = {}
        if request.cart_id:
            query["id"] = request.cart_id
        elif request.session_id:
            query["session_id"] = request.session_id
        else:
            raise HTTPException(status_code=400, detail="Either cart_id or session_id required")
        
        cart = await db.carts.find_one(query, {"_id": 0})
        
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        if not cart.get("items"):
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Get product details for email
        cart_items = []
        cart_value = 0
        
        for item in cart.get("items", []):
            product = await db.products.find_one(
                {"id": item.get("product_id")},
                {"name": 1, "price": 1, "image": 1}
            )
            if product:
                item_value = product.get("price", 0) * item.get("quantity", 1)
                cart_value += item_value
                cart_items.append({
                    "name": product.get("name"),
                    "price": product.get("price", 0),
                    "quantity": item.get("quantity", 1),
                    "image": product.get("image")
                })
        
        # Send email in background
        background_tasks.add_task(
            _send_recovery_email_task,
            email=request.email,
            cart_items=cart_items,
            cart_value=cart_value,
            custom_message=request.custom_message,
            cart_id=cart.get("id") or cart.get("session_id")
        )
        
        # Update cart record
        await db.carts.update_one(
            query,
            {"$set": {
                "recovery_email_sent": True,
                "recovery_email_sent_at": datetime.now(timezone.utc).isoformat(),
                "recovery_email_to": request.email
            }}
        )
        
        return {
            "status": "success",
            "message": f"Recovery email queued for {request.email}",
            "cart_value": cart_value,
            "items_count": len(cart_items)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _send_recovery_email_task(
    email: str,
    cart_items: List[Dict],
    cart_value: float,
    custom_message: Optional[str],
    cart_id: str
):
    """
    Background task to send recovery email
    """
    try:
        from sendgrid_email_service import sendgrid_email_service
        
        # Build cart items HTML
        items_html = ""
        for item in cart_items:
            items_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">
                    <img src="{item.get('image', '')}" alt="{item.get('name', '')}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px;">
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">
                    <strong>{item.get('name', 'Product')}</strong><br>
                    <span style="color: #666;">Qty: {item.get('quantity', 1)}</span>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: right;">
                    <strong>₹{item.get('price', 0):,.0f}</strong>
                </td>
            </tr>
            """
        
        # Get frontend URL from environment
        frontend_url = os.environ.get('FRONTEND_URL', 'https://adityaretail.com')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px;">Your Cart is Waiting!</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Don't miss out on your selected items</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 30px;">
                    {f'<p style="color: #333; line-height: 1.6; margin-bottom: 20px;">{custom_message}</p>' if custom_message else ''}
                    
                    <p style="color: #333; line-height: 1.6;">
                        You left some amazing products in your cart. Complete your purchase now before they're gone!
                    </p>
                    
                    <!-- Cart Items -->
                    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                        <thead>
                            <tr style="background: #f8f9fa;">
                                <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">Image</th>
                                <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">Product</th>
                                <th style="padding: 12px; text-align: right; border-bottom: 2px solid #dee2e6;">Price</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                        <tfoot>
                            <tr>
                                <td colspan="2" style="padding: 15px; font-weight: bold; font-size: 18px;">Total Value</td>
                                <td style="padding: 15px; font-weight: bold; font-size: 18px; text-align: right; color: #667eea;">₹{cart_value:,.0f}</td>
                            </tr>
                        </tfoot>
                    </table>
                    
                    <!-- CTA Button -->
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{frontend_url}/#/checkout" 
                           style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px;">
                            Complete Your Purchase
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px; text-align: center;">
                        Need help? Reply to this email or call us at <strong>+91 99720 31931</strong>
                    </p>
                </div>
                
                <!-- Footer -->
                <div style="background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #eee;">
                    <p style="margin: 0; color: #666; font-size: 12px;">
                        Aditya Retail | Premium Kitchen Appliances<br>
                        Bangalore, Karnataka, India
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        sendgrid_email_service.send_email(
            to_email=email,
            subject="Complete Your Purchase - Your Cart is Waiting!",
            body=html_content,
            from_agent="sales",
            html=True
        )
        
        print(f"✅ Recovery email sent to {email} for cart {cart_id}")
        
    except Exception as e:
        print(f"❌ Failed to send recovery email: {e}")


@router.post("/abandoned-carts/bulk-recovery")
async def send_bulk_recovery_emails(
    min_value: float = 10000,
    max_emails: int = 50,
    background_tasks: BackgroundTasks = None,
    db = Depends(get_db)
):
    """
    Send recovery emails to multiple abandoned carts based on criteria
    Only sends to carts with user_id (registered users with email)
    """
    try:
        # Find eligible carts (with user_id and not already emailed)
        carts_cursor = db.carts.find({
            "items": {"$exists": True, "$ne": []},
            "user_id": {"$exists": True, "$ne": None},
            "$or": [
                {"recovery_email_sent": {"$exists": False}},
                {"recovery_email_sent": False}
            ]
        }, {"_id": 0}).limit(max_emails * 2)  # Fetch extra in case some are filtered
        
        carts = await carts_cursor.to_list(max_emails * 2)
        
        eligible_carts = []
        
        for cart in carts:
            # Calculate cart value
            cart_value = 0
            for item in cart.get("items", []):
                product = await db.products.find_one({"id": item.get("product_id")}, {"price": 1})
                if product:
                    cart_value += product.get("price", 0) * item.get("quantity", 1)
            
            if cart_value >= min_value:
                # Get user email
                user = await db.users.find_one({"id": cart["user_id"]}, {"email": 1, "name": 1})
                if user and user.get("email"):
                    eligible_carts.append({
                        "cart": cart,
                        "user": user,
                        "value": cart_value
                    })
            
            if len(eligible_carts) >= max_emails:
                break
        
        # Queue emails
        emails_queued = 0
        for item in eligible_carts:
            try:
                # Get product details
                cart_items = []
                for cart_item in item["cart"].get("items", []):
                    product = await db.products.find_one(
                        {"id": cart_item.get("product_id")},
                        {"name": 1, "price": 1, "image": 1}
                    )
                    if product:
                        cart_items.append({
                            "name": product.get("name"),
                            "price": product.get("price", 0),
                            "quantity": cart_item.get("quantity", 1),
                            "image": product.get("image")
                        })
                
                if background_tasks:
                    background_tasks.add_task(
                        _send_recovery_email_task,
                        email=item["user"]["email"],
                        cart_items=cart_items,
                        cart_value=item["value"],
                        custom_message=f"Hi {item['user'].get('name', 'Valued Customer')},",
                        cart_id=item["cart"].get("id") or item["cart"].get("session_id")
                    )
                
                # Mark as sent
                await db.carts.update_one(
                    {"session_id": item["cart"]["session_id"]},
                    {"$set": {
                        "recovery_email_sent": True,
                        "recovery_email_sent_at": datetime.now(timezone.utc).isoformat(),
                        "recovery_email_to": item["user"]["email"]
                    }}
                )
                
                emails_queued += 1
                
            except Exception as e:
                print(f"Error queuing email for cart: {e}")
        
        return {
            "status": "success",
            "message": f"Queued {emails_queued} recovery emails",
            "emails_queued": emails_queued,
            "min_value_threshold": min_value
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
