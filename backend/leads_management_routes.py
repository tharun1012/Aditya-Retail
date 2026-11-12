from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timezone
import uuid
from database import get_db

router = APIRouter(prefix="/leads", tags=["Lead Management"])

import os as _os, jwt as _jwt
from fastapi import Header as _Header

_LEAD_ROLES = {"admin", "super_admin", "accountant", "store_manager", "sales", "manager"}

async def require_lead_admin(authorization: str = _Header(None), db = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    token = authorization.replace("Bearer ", "").strip()

    # Path 1: JWT issued by admin email/password login
    secret = _os.environ.get("JWT_SECRET_KEY")
    if secret:
        try:
            payload = _jwt.decode(token, secret, algorithms=["HS256"])
            if payload.get("role") in _LEAD_ROLES:
                return payload
            raise HTTPException(status_code=403, detail="Not allowed")
        except HTTPException:
            raise
        except Exception:
            pass  # not a JWT — try Emergent session token below

    # Path 2: Emergent Google-auth session token (opaque, stored in user_sessions)
    session = await db.user_sessions.find_one({"session_token": token}, {"_id": 0})
    if session:
        expires_at = session.get("expires_at")
        if isinstance(expires_at, str):
            try:
                from dateutil.parser import parse as _parse_date
                exp_dt = _parse_date(expires_at)
                if exp_dt.tzinfo is None:
                    from datetime import timezone as _tz
                    exp_dt = exp_dt.replace(tzinfo=_tz.utc)
                from datetime import datetime as _dt, timezone as _tz2
                if exp_dt < _dt.now(_tz2.utc):
                    raise HTTPException(status_code=401, detail="Session expired")
            except HTTPException:
                raise
            except Exception:
                pass
        user_id = session.get("user_id")
        user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
        if not user_doc:
            user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
        role = (user_doc or {}).get("role")
        if role in _LEAD_ROLES:
            return {"sub": (user_doc or {}).get("email"), "role": role}
        raise HTTPException(status_code=403, detail="Not allowed")

    raise HTTPException(status_code=401, detail="Invalid or expired token")

# Lead Status Options
LEAD_STATUS = {
    "new": "New Lead",
    "contacted": "Contacted",
    "qualified": "Qualified",
    "hot": "Hot Lead",
    "warm": "Warm Lead",
    "cold": "Cold Lead",
    "negotiation": "In Negotiation",
    "won": "Converted to Customer",
    "lost": "Lost"
}

# Lead Source Options
LEAD_SOURCES = {
    "website": "Website",
    "ai_chat": "AI Chat Agent",
    "phone": "Phone Call",
    "email": "Email",
    "social_media": "Social Media",
    "referral": "Referral",
    "walk_in": "Walk-in",
    "other": "Other"
}

def classify_lead_type(lead: dict) -> str:
    """Classify a lead into a team bucket: sales / service / delivery / expert / other"""
    at = (lead.get("agent_type") or "").lower()
    src = (lead.get("source") or "").lower()
    text = f"{at} {src}"
    if "delivery" in text:
        return "delivery"
    if "service" in text:
        return "service"
    if "consultation" in text or "expert" in text:
        return "expert"
    if "sales" in text or "ai_chat" in text or "website_signup" in text or "payment_failed" in text or "repeat_buyer" in text:
        return "sales"
    return "other"

def sanitize_lead(lead: dict) -> dict:
    """Coerce legacy/foreign data shapes into display-safe values.
    Some automations stored notes as a LIST of objects ({timestamp,type,message,agent,method})
    which crashes the React UI. Fold them into interactions and stringify."""
    notes = lead.get("notes")
    if isinstance(notes, list):
        interactions = lead.get("interactions") or []
        for n in notes:
            if isinstance(n, dict):
                interactions.append({
                    "timestamp": str(n.get("timestamp") or ""),
                    "type": str(n.get("type") or "note"),
                    "content": str(n.get("message") or n.get("content") or n.get("note") or ""),
                    "agent": str(n.get("agent") or ""),
                })
            else:
                interactions.append({"type": "note", "content": str(n), "agent": "", "timestamp": ""})
        lead["interactions"] = interactions
        lead["notes"] = ""
    elif notes is not None and not isinstance(notes, str):
        lead["notes"] = str(notes)

    # Stringify any non-primitive values inside interactions/follow_ups
    for coll_key in ("interactions", "follow_ups"):
        items = lead.get(coll_key)
        if isinstance(items, list):
            for it in items:
                if isinstance(it, dict):
                    for k, v in list(it.items()):
                        if not isinstance(v, (str, int, float, bool, type(None))):
                            it[k] = str(v)
    return lead


class LeadCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    source: str = "website"
    interested_products: Optional[List[str]] = []
    notes: Optional[str] = None
    ai_agent_interaction: Optional[str] = None
    product: Optional[str] = None
    brand: Optional[str] = None
    quantity: Optional[int] = None
    expected_value: Optional[float] = None

class LeadUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None
    interested_products: Optional[List[str]] = None
    expected_value: Optional[float] = None
    store_id: Optional[str] = None

class FollowUpCreate(BaseModel):
    lead_id: str
    follow_up_date: str
    action: str
    notes: Optional[str] = None
    assigned_to: Optional[str] = None

@router.post("/")
async def create_lead(lead_data: LeadCreate, db = Depends(get_db)):
    """Create a new lead"""
    try:
        lead_id = str(uuid.uuid4())
        
        lead = {
            "id": lead_id,
            "name": lead_data.name,
            "email": lead_data.email,
            "phone": lead_data.phone,
            "source": lead_data.source,
            "status": "new",
            "interested_products": (lead_data.interested_products or ([f"{lead_data.brand or ''} {lead_data.product}".strip()] if lead_data.product else [])),
            "product": lead_data.product,
            "brand": lead_data.brand,
            "quantity": lead_data.quantity,
            "notes": lead_data.notes,
            "ai_agent_interaction": lead_data.ai_agent_interaction,
            "expected_value": lead_data.expected_value or 0,
            "assigned_to": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "last_contact_date": None,
            "next_follow_up": None,
            "interactions": [],
            "follow_ups": []
        }
        
        await db.leads.insert_one(lead)
        
        # Send welcome email immediately
        if lead_data.email:
            try:
                from lead_automation_service import lead_automation
                await lead_automation.send_welcome_email(lead, db)
                print(f"✅ Welcome email sent to {lead_data.email}")
            except Exception as e:
                print(f"⚠️ Error sending welcome email: {e}")
        
        return {
            "status": "success",
            "message": "Lead created successfully. Welcome email sent!" if lead_data.email else "Lead created successfully",
            "lead_id": lead_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating lead: {str(e)}")

@router.get("/", dependencies=[Depends(require_lead_admin)])
async def get_leads(
    status: Optional[str] = None,
    source: Optional[str] = None,
    assigned_to: Optional[str] = None,
    lead_type: Optional[str] = None,
    limit: int = 500,
    db = Depends(get_db)
):
    """Get all leads with filters"""
    try:
        query = {}
        
        if status:
            query["status"] = status
        if source:
            query["source"] = source
        if assigned_to:
            query["assigned_to"] = assigned_to
        
        # Sort by _id descending (newest first) - more reliable than created_at string
        leads_with_id = await db.leads.find(query).sort([("_id", -1)]).limit(limit).to_list(limit)
        # Remove _id from response
        leads = []
        for lead in leads_with_id:
            lead.pop('_id', None)
            if not lead.get("id"):
                lead["id"] = lead.get("lead_id") or ""
            lead = sanitize_lead(lead)
            lead["lead_type"] = classify_lead_type(lead)
            if lead_type and lead["lead_type"] != lead_type:
                continue
            leads.append(lead)
        
        return {
            "status": "success",
            "total": len(leads),
            "leads": leads
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching leads: {str(e)}")

@router.get("/funnel", dependencies=[Depends(require_lead_admin)])
async def get_lead_funnel(db = Depends(get_db)):
    """Get lead funnel statistics"""
    try:
        all_leads = await db.leads.find({}, {"_id": 0}).to_list(1000)
        
        funnel = {
            "total_leads": len(all_leads),
            "by_status": {},
            "by_source": {},
            "by_type": {},
            "conversion_rate": 0,
            "avg_deal_value": 0,
            "hot_leads": 0,
            "cold_leads": 0
        }
        
        # Count by status
        for lead in all_leads:
            status = lead.get("status", "new")
            funnel["by_status"][status] = funnel["by_status"].get(status, 0) + 1
            
            # Count by source
            source = lead.get("source") or "other"
            funnel["by_source"][source] = funnel["by_source"].get(source, 0) + 1

            ltype = classify_lead_type(lead)
            funnel["by_type"][ltype] = funnel["by_type"].get(ltype, 0) + 1
            
            # Hot/Cold leads
            if status == "hot":
                funnel["hot_leads"] += 1
            elif status == "cold":
                funnel["cold_leads"] += 1
        
        # Calculate conversion rate
        converted = funnel["by_status"].get("won", 0)
        if len(all_leads) > 0:
            funnel["conversion_rate"] = round((converted / len(all_leads)) * 100, 2)
        
        # Calculate average deal value
        total_value = sum([lead.get("expected_value", 0) for lead in all_leads if lead.get("status") == "won"])
        if converted > 0:
            funnel["avg_deal_value"] = round(total_value / converted, 2)
        
        return {
            "status": "success",
            "funnel": funnel
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching funnel: {str(e)}")

@router.get("/{lead_id}", dependencies=[Depends(require_lead_admin)])
async def get_lead(lead_id: str, db = Depends(get_db)):
    """Get specific lead details"""
    try:
        lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        lead = sanitize_lead(lead)
        lead["lead_type"] = classify_lead_type(lead)
        return {
            "status": "success",
            "lead": lead
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lead: {str(e)}")

@router.put("/{lead_id}", dependencies=[Depends(require_lead_admin)])
async def update_lead(lead_id: str, update_data: LeadUpdate, db = Depends(get_db)):
    """Update lead details"""
    try:
        lead_query = {"$or": [{"id": lead_id}, {"lead_id": lead_id}]}
        lead = await db.leads.find_one(lead_query)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        update_fields = {"updated_at": datetime.now(timezone.utc).isoformat()}
        
        if update_data.status:
            update_fields["status"] = update_data.status
            update_fields["last_contact_date"] = datetime.now(timezone.utc).isoformat()
        
        if update_data.notes:
            # Add to interactions
            interaction = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "note",
                "content": update_data.notes,
                "agent": "admin"
            }
            await db.leads.update_one(
                lead_query,
                {"$push": {"interactions": interaction}}
            )
        
        if update_data.assigned_to:
            update_fields["assigned_to"] = update_data.assigned_to
        
        if update_data.interested_products:
            update_fields["interested_products"] = update_data.interested_products
        
        if update_data.expected_value is not None:
            update_fields["expected_value"] = update_data.expected_value

        if update_data.store_id is not None:
            sid = update_data.store_id.strip()
            if sid and not await db.stores.find_one({"id": sid}):
                raise HTTPException(status_code=400, detail="Store not found")
            update_fields["store_id"] = sid or None
        
        await db.leads.update_one(
            lead_query,
            {"$set": update_fields}
        )
        
        updated_lead = await db.leads.find_one(lead_query, {"_id": 0})
        
        return {
            "status": "success",
            "message": "Lead updated successfully",
            "lead": updated_lead
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating lead: {str(e)}")

@router.delete("/{lead_id}", dependencies=[Depends(require_lead_admin)])
async def delete_lead(lead_id: str, db = Depends(get_db)):
    """Delete a lead"""
    try:
        result = await db.leads.delete_one({"$or": [{"id": lead_id}, {"lead_id": lead_id}]})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Lead not found")
        return {"status": "success", "message": "Lead deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting lead: {str(e)}")

@router.post("/follow-up", dependencies=[Depends(require_lead_admin)])
async def add_follow_up(follow_up_data: FollowUpCreate, db = Depends(get_db)):
    """Add a follow-up activity to a lead"""
    try:
        lead = await db.leads.find_one({"id": follow_up_data.lead_id})
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        follow_up = {
            "id": str(uuid.uuid4()),
            "date": follow_up_data.follow_up_date,
            "action": follow_up_data.action,
            "notes": follow_up_data.notes,
            "assigned_to": follow_up_data.assigned_to,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.leads.update_one(
            {"id": follow_up_data.lead_id},
            {
                "$push": {"follow_ups": follow_up},
                "$set": {
                    "next_follow_up": follow_up_data.follow_up_date,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return {
            "status": "success",
            "message": "Follow-up added successfully",
            "follow_up": follow_up
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding follow-up: {str(e)}")

@router.post("/trigger-email-automation", dependencies=[Depends(require_lead_admin)])
async def trigger_email_automation(db = Depends(get_db)):
    """Manually trigger email automation (for testing)"""
    try:
        from lead_automation_service import lead_automation
        from datetime import datetime, timezone, timedelta
        
        # Process all leads for email sequences
        leads = await db.leads.find({
            "email": {"$exists": True, "$ne": None},
            "status": {"$nin": ["won", "lost"]}
        }).to_list(1000)
        
        processed = 0
        emails_sent = 0
        
        for lead in leads:
            try:
                created_at = datetime.fromisoformat(lead.get('created_at').replace('Z', '+00:00'))
                days_since_creation = (datetime.now(timezone.utc) - created_at).days
                emails_sent_list = lead.get('emails_sent', [])
                sent_types = [e.get('type') for e in emails_sent_list]
                
                # Send appropriate emails based on days
                if 'welcome' not in sent_types:
                    await lead_automation.send_welcome_email(lead, db)
                    emails_sent += 1
                elif days_since_creation >= 2 and 'day2' not in sent_types:
                    await lead_automation.send_follow_up_email(lead, 'day2', db)
                    emails_sent += 1
                elif days_since_creation >= 4 and 'day4' not in sent_types:
                    await lead_automation.send_follow_up_email(lead, 'day4', db)
                    emails_sent += 1
                elif days_since_creation >= 7 and 'day7' not in sent_types:
                    await lead_automation.send_follow_up_email(lead, 'day7', db)
                    emails_sent += 1
                
                # Update lead score
                await lead_automation.update_lead_status_by_score(lead['id'], db)
                processed += 1
                
            except Exception as e:
                print(f"Error processing lead: {e}")
                continue
        
        # Check for hot leads
        escalations = await lead_automation.check_and_escalate_hot_leads(db)
        
        return {
            "status": "success",
            "message": "Email automation triggered successfully",
            "leads_processed": processed,
            "emails_sent": emails_sent,
            "hot_leads_escalated": len(escalations),
            "escalations": escalations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering automation: {str(e)}")

@router.get("/ai-interactions/log", dependencies=[Depends(require_lead_admin)])
async def log_ai_interaction(
    lead_id: str,
    agent_type: str,
    message: str,
    db = Depends(get_db)
):
    """Log AI agent interaction with a lead"""
    try:
        interaction = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "ai_chat",
            "agent": agent_type,
            "content": message
        }
        
        result = await db.leads.update_one(
            {"id": lead_id},
            {
                "$push": {"interactions": interaction},
                "$set": {
                    "last_contact_date": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if result.modified_count == 0:
            # Lead doesn't exist, might need to create
            return {
                "status": "info",
                "message": "Lead not found. Consider creating lead first."
            }
        
        return {
            "status": "success",
            "message": "Interaction logged successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging interaction: {str(e)}")

@router.get("/marketing-agent/activity", dependencies=[Depends(require_lead_admin)])
async def get_marketing_agent_activity(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db = Depends(get_db)
):
    """Get marketing agent activity summary"""
    try:
        all_leads = await db.leads.find({}, {"_id": 0}).to_list(1000)
        
        activity = {
            "total_interactions": 0,
            "leads_contacted": 0,
            "leads_qualified": 0,
            "leads_converted": 0,
            "interactions_by_agent": {},
            "recent_activities": []
        }
        
        for lead in all_leads:
            interactions = lead.get("interactions", [])
            activity["total_interactions"] += len(interactions)
            
            if lead.get("status") in ["contacted", "qualified", "hot", "warm"]:
                activity["leads_contacted"] += 1
            
            if lead.get("status") == "qualified":
                activity["leads_qualified"] += 1
            
            if lead.get("status") == "won":
                activity["leads_converted"] += 1
            
            # Count by agent type
            for interaction in interactions:
                agent = interaction.get("agent", "unknown")
                activity["interactions_by_agent"][agent] = activity["interactions_by_agent"].get(agent, 0) + 1
                
                # Add to recent activities
                activity["recent_activities"].append({
                    "lead_name": lead.get("name"),
                    "lead_id": lead.get("id"),
                    "agent": agent,
                    "timestamp": interaction.get("timestamp"),
                    "type": interaction.get("type"),
                    "content": interaction.get("content", "")[:100]  # First 100 chars
                })
        
        # Sort recent activities by timestamp
        activity["recent_activities"].sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        activity["recent_activities"] = activity["recent_activities"][:50]  # Last 50 activities
        
        return {
            "status": "success",
            "activity": activity
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching marketing activity: {str(e)}")

@router.get("/status-options/list", dependencies=[Depends(require_lead_admin)])
async def get_status_options():
    """Get available lead status options"""
    return {
        "status": "success",
        "statuses": LEAD_STATUS,
        "sources": LEAD_SOURCES
    }


# ================= STORE-LEVEL LEADS =================
async def require_store_user(authorization: str = _Header(None), db = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    token = authorization.replace("Bearer ", "").strip()
    session = await db.store_sessions.find_one({"token": token}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await db.store_users.find_one({"id": session["user_id"], "is_active": True}, {"_id": 0})
    if not user or not user.get("store_id"):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"store_id": user["store_id"], "store_code": user.get("store_code"), "user_id": user["id"],
            "name": f'{user.get("first_name", "")} {user.get("last_name", "")}'.strip()}

class StoreLeadUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    expected_value: Optional[float] = None

class StoreLeadCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: str = "walk_in"
    interested_products: Optional[List[str]] = []
    notes: Optional[str] = None
    product: Optional[str] = None
    brand: Optional[str] = None
    quantity: Optional[int] = None
    expected_value: Optional[float] = None

@router.get("/store/list")
async def store_get_leads(status: Optional[str] = None, lead_type: Optional[str] = None,
                          limit: int = 500, store = Depends(require_store_user), db = Depends(get_db)):
    query = {"store_id": store["store_id"]}
    if status:
        query["status"] = status
    rows = await db.leads.find(query).sort([("_id", -1)]).limit(limit).to_list(limit)
    leads = []
    for lead in rows:
        lead.pop("_id", None)
        if not lead.get("id"):
            lead["id"] = lead.get("lead_id") or ""
        lead = sanitize_lead(lead)
        lead["lead_type"] = classify_lead_type(lead)
        if lead_type and lead["lead_type"] != lead_type:
            continue
        leads.append(lead)
    return {"status": "success", "total": len(leads), "leads": leads}

@router.put("/store/{lead_id}")
async def store_update_lead(lead_id: str, data: StoreLeadUpdate,
                            store = Depends(require_store_user), db = Depends(get_db)):
    q = {"$and": [{"$or": [{"id": lead_id}, {"lead_id": lead_id}]}, {"store_id": store["store_id"]}]}
    if not await db.leads.find_one(q):
        raise HTTPException(status_code=404, detail="Lead not found")
    now = datetime.now(timezone.utc).isoformat()
    fields = {"updated_at": now}
    if data.status:
        if data.status not in LEAD_STATUS:
            raise HTTPException(status_code=400, detail="Invalid status")
        fields["status"] = data.status
        fields["last_contact_date"] = now
    if data.expected_value is not None:
        fields["expected_value"] = data.expected_value
    update = {"$set": fields}
    if data.notes:
        update["$push"] = {"interactions": {"timestamp": now, "type": "note",
                                            "content": data.notes, "agent": store["name"] or "store"}}
    await db.leads.update_one(q, update)
    return {"status": "success", "lead": await db.leads.find_one(q, {"_id": 0})}

@router.post("/store/create")
async def store_create_lead(data: StoreLeadCreate, store = Depends(require_store_user), db = Depends(get_db)):
    now = datetime.now(timezone.utc).isoformat()
    lead_id = str(uuid.uuid4())
    await db.leads.insert_one({
        "id": lead_id, "name": data.name, "email": data.email or None, "phone": data.phone,
        "source": data.source, "status": "new", "interested_products": (data.interested_products or ([f"{data.brand or ''} {data.product}".strip()] if data.product else [])),
        "product": data.product, "brand": data.brand, "quantity": data.quantity,
        "notes": data.notes, "ai_agent_interaction": None, "expected_value": data.expected_value or 0, "assigned_to": None,
        "store_id": store["store_id"], "created_by": store["user_id"],
        "created_at": now, "updated_at": now, "last_contact_date": None,
        "next_follow_up": None, "interactions": [], "follow_ups": []
    })
    return {"status": "success", "lead_id": lead_id}


@router.get("/store/funnel")
async def store_get_funnel(store = Depends(require_store_user), db = Depends(get_db)):
    all_leads = await db.leads.find({"store_id": store["store_id"]}, {"_id": 0}).to_list(1000)
    funnel = {"total_leads": len(all_leads), "by_status": {}, "by_source": {}, "by_type": {},
              "conversion_rate": 0, "avg_deal_value": 0, "hot_leads": 0, "cold_leads": 0}
    for lead in all_leads:
        status = lead.get("status", "new")
        funnel["by_status"][status] = funnel["by_status"].get(status, 0) + 1
        source = lead.get("source") or "other"
        funnel["by_source"][source] = funnel["by_source"].get(source, 0) + 1
        ltype = classify_lead_type(lead)
        funnel["by_type"][ltype] = funnel["by_type"].get(ltype, 0) + 1
        if status == "hot":
            funnel["hot_leads"] += 1
        elif status == "cold":
            funnel["cold_leads"] += 1
    converted = funnel["by_status"].get("won", 0)
    if all_leads:
        funnel["conversion_rate"] = round(converted / len(all_leads) * 100, 2)
    if converted:
        total = sum((l.get("expected_value") or 0) for l in all_leads if l.get("status") == "won")
        funnel["avg_deal_value"] = round(total / converted, 2)
    return {"status": "success", "funnel": funnel}

@router.get("/store/mail")
async def store_get_mail_leads(brand: Optional[str] = None, store = Depends(require_store_user), db = Depends(get_db)):
    if not store.get("store_code"):
        return []
    q = {"store_code": store["store_code"]}
    if brand and brand != "All Mail":
        q["brand"] = brand
    out = []
    async for d in db.mail_leads.find(q).sort("received_at", -1):
        d["id"] = str(d.pop("_id"))
        out.append(d)
    return out


@router.get("/store/quotations")
async def store_get_quotations(limit: int = 2000, store = Depends(require_store_user), db = Depends(get_db)):
    from quotation_routes import _crm_stage_of
    limit = min(max(int(limit or 2000), 1), 5000)
    query = {"store_id": store["store_id"]}
    docs = await db.quotations.find(
        query, {"_id": 0, "items": 0, "terms_and_conditions": 0, "crm_history": 0}
    ).sort("created_at", -1).limit(limit).to_list(None)
    for d in docs:
        d["crm_stage"] = _crm_stage_of(d)
        d["amount"] = (d.get("totals") or {}).get("grand_total", 0)
    total = await db.quotations.count_documents(query)
    return {"status": "success", "quotations": docs, "total": total}


@router.get("/store/{lead_id}")
async def store_get_lead(lead_id: str, store = Depends(require_store_user), db = Depends(get_db)):
    q = {"$and": [{"$or": [{"id": lead_id}, {"lead_id": lead_id}]}, {"store_id": store["store_id"]}]}
    lead = await db.leads.find_one(q, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead = sanitize_lead(lead)
    lead["lead_type"] = classify_lead_type(lead)
    return {"status": "success", "lead": lead}


@router.post("/store/follow-up")
async def store_add_follow_up(data: FollowUpCreate, store = Depends(require_store_user), db = Depends(get_db)):
    q = {"id": data.lead_id, "store_id": store["store_id"]}
    if not await db.leads.find_one(q):
        raise HTTPException(status_code=404, detail="Lead not found")
    now = datetime.now(timezone.utc).isoformat()
    follow_up = {"id": str(uuid.uuid4()), "date": data.follow_up_date, "action": data.action,
                 "notes": data.notes, "assigned_to": data.assigned_to, "status": "pending", "created_at": now}
    await db.leads.update_one(q, {"$push": {"follow_ups": follow_up},
                                  "$set": {"next_follow_up": data.follow_up_date, "updated_at": now}})
    return {"status": "success", "follow_up": follow_up}


# ================= STORE-LEVEL MAIL LEADS =================
class StoreMailStatus(BaseModel):
    status: str


@router.patch("/store/mail/{lead_id}/status")
async def store_update_mail_status(lead_id: str, body: StoreMailStatus,
                                   store = Depends(require_store_user), db = Depends(get_db)):
    from bson import ObjectId
    from mail_leads import STATUSES
    if body.status not in STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")
    try:
        oid = ObjectId(lead_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Not found")
    r = await db.mail_leads.update_one({"_id": oid, "store_code": store.get("store_code")},
                                       {"$set": {"status": body.status}})
    if not r.matched_count:
        raise HTTPException(status_code=404, detail="Not found")
    return {"status": "success"}


# ================= STORE-LEVEL QUOTATIONS =================
from fastapi import Body as _Body


@router.put("/store/quotations/{quotation_id}/crm-stage")
async def store_update_quotation_crm(quotation_id: str, payload: dict = _Body(...),
                                     store = Depends(require_store_user), db = Depends(get_db)):
    from quotation_routes import update_quotation_crm, QuotationCrmUpdate
    owned = await db.quotations.find_one({"id": quotation_id, "store_id": store["store_id"]}, {"_id": 0, "id": 1})
    if not owned:
        raise HTTPException(status_code=404, detail="Quotation not found")
    payload["updated_by"] = store.get("name") or "store"
    return await update_quotation_crm(quotation_id, QuotationCrmUpdate(**payload), db)


# ---- store-scoped mail lead panel actions ----
class _StoreMailAssign(BaseModel):
    assigned_to: str

class _StoreMailNote(BaseModel):
    text: str

class _StoreMailFollowUp(BaseModel):
    follow_up_at: Optional[str] = None


def _store_mail_q(lead_id: str, store):
    from bson import ObjectId
    try:
        oid = ObjectId(lead_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Not found")
    if not store.get("store_code"):
        raise HTTPException(status_code=404, detail="Not found")
    return {"_id": oid, "store_code": store["store_code"]}


@router.patch("/store/mail/{lead_id}/assign")
async def store_mail_assign(lead_id: str, body: _StoreMailAssign,
                            store = Depends(require_store_user), db = Depends(get_db)):
    r = await db.mail_leads.update_one(_store_mail_q(lead_id, store), {"$set": {"assigned_to": body.assigned_to.strip()}})
    if not r.matched_count:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}


@router.post("/store/mail/{lead_id}/notes")
async def store_mail_note(lead_id: str, body: _StoreMailNote,
                          store = Depends(require_store_user), db = Depends(get_db)):
    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty note")
    note = {"text": text, "at": datetime.now(timezone.utc).isoformat()}
    r = await db.mail_leads.update_one(_store_mail_q(lead_id, store), {"$push": {"notes": note}})
    if not r.matched_count:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}


@router.patch("/store/mail/{lead_id}/followup")
async def store_mail_followup(lead_id: str, body: _StoreMailFollowUp,
                              store = Depends(require_store_user), db = Depends(get_db)):
    r = await db.mail_leads.update_one(_store_mail_q(lead_id, store), {"$set": {"follow_up_at": body.follow_up_at or None}})
    if not r.matched_count:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}
