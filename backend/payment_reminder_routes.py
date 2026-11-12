"""
Payment Reminder Routes
Automated payment reminders for customers with outstanding balances
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from database import get_db
import uuid
import logging
import asyncio

router = APIRouter(prefix="/payment-reminders", tags=["Payment Reminders"])
logger = logging.getLogger(__name__)


# ============ MODELS ============

class ReminderSettingsUpdate(BaseModel):
    enabled: bool = True
    reminder_days: List[int] = [7, 15, 30]  # Days after due date to send reminders
    min_amount: float = 100  # Minimum outstanding amount to trigger reminder
    include_sms: bool = False
    include_whatsapp: bool = False
    email_template: Optional[str] = None
    escalation_enabled: bool = False
    escalation_days: int = 45  # Days after which to escalate


class ManualReminderRequest(BaseModel):
    ledger_ids: List[str]
    message_type: str = "email"  # email, sms, whatsapp
    custom_message: Optional[str] = None


class ReminderTemplateCreate(BaseModel):
    name: str
    subject: str
    body: str
    reminder_type: str = "standard"  # standard, friendly, urgent, final
    is_default: bool = False


# ============ REMINDER SETTINGS ============

@router.get("/settings")
async def get_reminder_settings(db = Depends(get_db)):
    """Get payment reminder settings"""
    try:
        settings = await db.reminder_settings.find_one({"type": "payment_reminder"}, {"_id": 0})
        
        if not settings:
            # Return default settings
            settings = {
                "type": "payment_reminder",
                "enabled": True,
                "reminder_days": [7, 15, 30],
                "min_amount": 100,
                "include_sms": False,
                "include_whatsapp": False,
                "escalation_enabled": False,
                "escalation_days": 45,
                "auto_send_time": "09:00",
                "exclude_weekends": True
            }
        
        return {"status": "success", "settings": settings}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/settings")
async def update_reminder_settings(settings: ReminderSettingsUpdate, db = Depends(get_db)):
    """Update payment reminder settings"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        
        settings_data = {
            "type": "payment_reminder",
            **settings.dict(),
            "updated_at": now
        }
        
        await db.reminder_settings.update_one(
            {"type": "payment_reminder"},
            {"$set": settings_data},
            upsert=True
        )
        
        return {"status": "success", "message": "Settings updated"}
        
    except Exception as e:
        logger.error(f"Update settings failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ REMINDER TEMPLATES ============

@router.post("/templates/create")
async def create_reminder_template(template: ReminderTemplateCreate, db = Depends(get_db)):
    """Create a reminder email template"""
    try:
        template_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        # If default, unset others
        if template.is_default:
            await db.reminder_templates.update_many(
                {"reminder_type": template.reminder_type, "is_default": True},
                {"$set": {"is_default": False}}
            )
        
        template_data = {
            "id": template_id,
            **template.dict(),
            "is_active": True,
            "created_at": now
        }
        
        await db.reminder_templates.insert_one(template_data)
        
        return {
            "status": "success",
            "message": f"Template '{template.name}' created",
            "template_id": template_id
        }
        
    except Exception as e:
        logger.error(f"Create template failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_reminder_templates(db = Depends(get_db)):
    """Get all reminder templates"""
    try:
        templates = await db.reminder_templates.find(
            {"is_active": True},
            {"_id": 0}
        ).sort("name", 1).to_list(length=100)
        
        return {"status": "success", "templates": templates}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ PENDING REMINDERS ============

@router.get("/pending")
async def get_pending_reminders(
    min_days_overdue: int = 0,
    min_amount: float = 0,
    limit: int = 100,
    db = Depends(get_db)
):
    """Get customers with pending payments who need reminders"""
    try:
        # Get settings
        settings = await db.reminder_settings.find_one({"type": "payment_reminder"})
        min_amt = min_amount or (settings.get("min_amount", 0) if settings else 0)
        
        # Get customers with outstanding balances
        query = {
            "account_type": "customer",
            "is_active": True,
            "current_balance": {"$gt": min_amt}
        }
        
        customers = await db.ledgers.find(query, {"_id": 0}).sort("current_balance", -1).limit(limit).to_list(length=limit)
        
        pending_reminders = []
        today = datetime.now(timezone.utc)
        
        for customer in customers:
            last_txn_date = customer.get("last_transaction_date")
            days_since_last_txn = 0
            
            if last_txn_date:
                try:
                    last_date = datetime.fromisoformat(last_txn_date.replace("Z", "+00:00"))
                    days_since_last_txn = (today - last_date).days
                except Exception:
                    pass
            
            # Get last reminder sent
            last_reminder = await db.reminder_history.find_one(
                {"ledger_id": customer["id"]},
                sort=[("sent_at", -1)]
            )
            
            days_since_reminder = None
            if last_reminder:
                try:
                    reminder_date = datetime.fromisoformat(last_reminder["sent_at"].replace("Z", "+00:00"))
                    days_since_reminder = (today - reminder_date).days
                except Exception:
                    pass
            
            # Determine reminder status
            reminder_type = "standard"
            if days_since_last_txn > 45:
                reminder_type = "final"
            elif days_since_last_txn > 30:
                reminder_type = "urgent"
            elif days_since_last_txn > 15:
                reminder_type = "friendly"
            
            pending_reminders.append({
                "id": customer["id"],
                "name": customer.get("name"),
                "phone": customer.get("phone"),
                "email": customer.get("email"),
                "outstanding_amount": customer.get("current_balance", 0),
                "days_overdue": days_since_last_txn,
                "last_reminder_sent": last_reminder.get("sent_at") if last_reminder else None,
                "days_since_reminder": days_since_reminder,
                "reminder_count": last_reminder.get("reminder_number", 0) if last_reminder else 0,
                "suggested_reminder_type": reminder_type
            })
        
        # Filter by days overdue
        if min_days_overdue > 0:
            pending_reminders = [r for r in pending_reminders if r["days_overdue"] >= min_days_overdue]
        
        return {
            "status": "success",
            "pending_count": len(pending_reminders),
            "total_outstanding": sum(r["outstanding_amount"] for r in pending_reminders),
            "reminders": pending_reminders
        }
        
    except Exception as e:
        logger.error(f"Get pending reminders failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ SEND REMINDERS ============

@router.post("/send")
async def send_payment_reminders(
    request: ManualReminderRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Send payment reminders to selected customers"""
    try:
        # Queue the reminder sending in background
        background_tasks.add_task(
            process_reminders,
            request.ledger_ids,
            request.message_type,
            request.custom_message,
            db
        )
        
        return {
            "status": "success",
            "message": f"Sending reminders to {len(request.ledger_ids)} customers",
            "queued_count": len(request.ledger_ids)
        }
        
    except Exception as e:
        logger.error(f"Send reminders failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_reminders(
    ledger_ids: List[str],
    message_type: str,
    custom_message: Optional[str],
    db
):
    """Process and send reminders (background task)"""
    try:
        from sendgrid_email_service import sendgrid_email_service
        
        sent_count = 0
        failed_count = 0
        now = datetime.now(timezone.utc).isoformat()
        
        for ledger_id in ledger_ids:
            try:
                # Get customer details
                customer = await db.ledgers.find_one({"id": ledger_id})
                if not customer:
                    continue
                
                email = customer.get("email")
                if not email and message_type == "email":
                    failed_count += 1
                    continue
                
                # Get reminder count for this customer
                reminder_count = await db.reminder_history.count_documents({"ledger_id": ledger_id})
                
                # Generate email content
                outstanding = customer.get("current_balance", 0)
                customer_name = customer.get("name", "Customer")
                
                if custom_message:
                    body = custom_message.replace("{name}", customer_name).replace("{amount}", f"₹{outstanding:,.2f}")
                else:
                    body = generate_reminder_email(customer_name, outstanding, reminder_count + 1)
                
                # Send email
                if message_type == "email" and email:
                    result = sendgrid_email_service.send_email(
                        to_email=email,
                        subject=f"Payment Reminder - Outstanding Balance ₹{outstanding:,.2f}",
                        body=body,
                        from_agent="sales",
                        html=True
                    )
                    
                    if result.get("status") == "success":
                        sent_count += 1
                        
                        # Record reminder
                        await db.reminder_history.insert_one({
                            "id": str(uuid.uuid4()),
                            "ledger_id": ledger_id,
                            "customer_name": customer_name,
                            "customer_email": email,
                            "customer_phone": customer.get("phone"),
                            "outstanding_amount": outstanding,
                            "reminder_number": reminder_count + 1,
                            "message_type": message_type,
                            "sent_at": now,
                            "status": "sent"
                        })
                    else:
                        failed_count += 1
                        
            except Exception as e:
                logger.error(f"Failed to send reminder to {ledger_id}: {e}")
                failed_count += 1
        
        logger.info(f"Reminder batch complete: {sent_count} sent, {failed_count} failed")
        
    except Exception as e:
        logger.error(f"Process reminders failed: {e}")


def generate_reminder_email(customer_name: str, outstanding: float, reminder_number: int) -> str:
    """Generate reminder email HTML"""
    
    urgency = "friendly"
    if reminder_number >= 4:
        urgency = "final"
    elif reminder_number >= 3:
        urgency = "urgent"
    
    urgency_colors = {
        "friendly": {"bg": "#f0f9ff", "border": "#3b82f6", "text": "#1e40af"},
        "urgent": {"bg": "#fef3c7", "border": "#f59e0b", "text": "#92400e"},
        "final": {"bg": "#fef2f2", "border": "#ef4444", "text": "#991b1b"}
    }
    
    colors = urgency_colors.get(urgency, urgency_colors["friendly"])
    
    urgency_message = {
        "friendly": "This is a friendly reminder about your outstanding balance.",
        "urgent": "This is an urgent reminder. Please clear your dues at the earliest.",
        "final": "FINAL NOTICE: Please settle your account immediately to avoid further action."
    }
    
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
        <div style="background: {colors['bg']}; border-left: 4px solid {colors['border']}; padding: 20px; margin: 20px 0;">
            <h2 style="color: {colors['text']}; margin-top: 0;">Payment Reminder</h2>
            <p style="color: {colors['text']};">{urgency_message.get(urgency)}</p>
        </div>
        
        <p>Dear <strong>{customer_name}</strong>,</p>
        
        <p>We hope this message finds you well. We would like to bring to your attention that your account has an outstanding balance.</p>
        
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 20px 0; text-align: center;">
            <p style="margin: 0; color: #64748b; font-size: 14px;">Outstanding Amount</p>
            <p style="margin: 10px 0 0 0; font-size: 32px; font-weight: bold; color: #0f172a;">₹{outstanding:,.2f}</p>
        </div>
        
        <p>We kindly request you to settle this amount at your earliest convenience. You can make the payment through:</p>
        
        <ul style="color: #475569;">
            <li>Bank Transfer (NEFT/RTGS/IMPS)</li>
            <li>UPI Payment</li>
            <li>Cheque</li>
            <li>Cash at our store</li>
        </ul>
        
        <p>If you have already made the payment, please disregard this reminder and accept our thanks.</p>
        
        <p>For any queries or payment assistance, please feel free to contact us.</p>
        
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
        
        <p style="color: #64748b; font-size: 12px;">
            <strong>Aditya Retail</strong><br>
            Email: online.adityaretail@gmail.com<br>
            This is reminder #{reminder_number}
        </p>
    </body>
    </html>
    """


# ============ REMINDER HISTORY ============

@router.get("/history")
async def get_reminder_history(
    ledger_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get reminder history"""
    try:
        query = {}
        
        if ledger_id:
            query["ledger_id"] = ledger_id
        
        if from_date:
            query["sent_at"] = {"$gte": from_date}
        if to_date:
            if "sent_at" in query:
                query["sent_at"]["$lte"] = to_date
            else:
                query["sent_at"] = {"$lte": to_date}
        
        skip = (page - 1) * limit
        
        history = await db.reminder_history.find(query, {"_id": 0}).sort("sent_at", -1).skip(skip).limit(limit).to_list(length=limit)
        total = await db.reminder_history.count_documents(query)
        
        return {
            "status": "success",
            "history": history,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{ledger_id}")
async def get_customer_reminder_history(ledger_id: str, db = Depends(get_db)):
    """Get reminder history for a specific customer"""
    try:
        # Get customer details
        customer = await db.ledgers.find_one({"id": ledger_id}, {"_id": 0})
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get reminder history
        history = await db.reminder_history.find(
            {"ledger_id": ledger_id},
            {"_id": 0}
        ).sort("sent_at", -1).to_list(length=50)
        
        return {
            "status": "success",
            "customer": customer,
            "reminder_count": len(history),
            "history": history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ STATISTICS ============

@router.get("/stats")
async def get_reminder_stats(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Get reminder statistics"""
    try:
        query = {}
        
        if from_date:
            query["sent_at"] = {"$gte": from_date}
        if to_date:
            if "sent_at" in query:
                query["sent_at"]["$lte"] = to_date
            else:
                query["sent_at"] = {"$lte": to_date}
        
        # Total reminders sent
        total_sent = await db.reminder_history.count_documents(query)
        
        # Unique customers reminded
        unique_customers = await db.reminder_history.distinct("ledger_id", query)
        
        # Total outstanding at time of reminders
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": None,
                "total_outstanding": {"$sum": "$outstanding_amount"}
            }}
        ]
        result = await db.reminder_history.aggregate(pipeline).to_list(length=1)
        total_outstanding = result[0]["total_outstanding"] if result else 0
        
        # Reminders by type
        type_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$message_type",
                "count": {"$sum": 1}
            }}
        ]
        by_type = await db.reminder_history.aggregate(type_pipeline).to_list(length=10)
        
        # Recent reminders
        recent = await db.reminder_history.find(query, {"_id": 0}).sort("sent_at", -1).limit(5).to_list(length=5)
        
        return {
            "status": "success",
            "stats": {
                "total_reminders_sent": total_sent,
                "unique_customers_reminded": len(unique_customers),
                "total_outstanding_reminded": round(total_outstanding, 2),
                "by_type": {item["_id"]: item["count"] for item in by_type}
            },
            "recent_reminders": recent
        }
        
    except Exception as e:
        logger.error(f"Get reminder stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ AUTO REMINDER SCHEDULER ============

@router.post("/trigger-auto")
async def trigger_auto_reminders(
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Manually trigger automatic reminder sending"""
    try:
        # Get settings
        settings = await db.reminder_settings.find_one({"type": "payment_reminder"})
        
        if not settings or not settings.get("enabled", True):
            return {"status": "skipped", "message": "Automatic reminders are disabled"}
        
        min_amount = settings.get("min_amount", 100)
        reminder_days = settings.get("reminder_days", [7, 15, 30])
        
        # Get customers due for reminders
        query = {
            "account_type": "customer",
            "is_active": True,
            "current_balance": {"$gt": min_amount}
        }
        
        customers = await db.ledgers.find(query, {"_id": 0}).to_list(length=500)
        
        today = datetime.now(timezone.utc)
        eligible_ids = []
        
        for customer in customers:
            last_txn = customer.get("last_transaction_date")
            if not last_txn:
                continue
            
            try:
                last_date = datetime.fromisoformat(last_txn.replace("Z", "+00:00"))
                days_overdue = (today - last_date).days
            except Exception:
                continue
            
            # Check if days match reminder schedule
            if days_overdue not in reminder_days:
                continue
            
            # Check if reminder already sent today
            today_start = today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            existing = await db.reminder_history.find_one({
                "ledger_id": customer["id"],
                "sent_at": {"$gte": today_start}
            })
            
            if not existing:
                eligible_ids.append(customer["id"])
        
        if eligible_ids:
            background_tasks.add_task(
                process_reminders,
                eligible_ids,
                "email",
                None,
                db
            )
        
        return {
            "status": "success",
            "message": f"Queued {len(eligible_ids)} reminders for sending",
            "eligible_count": len(eligible_ids)
        }
        
    except Exception as e:
        logger.error(f"Trigger auto reminders failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
