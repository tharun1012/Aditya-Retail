"""
Neural AI Agent Routes - Advanced API endpoints for Neural AI agents
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from database import get_db
from neural_ai_agents import NeuralAIAgentManager
import logging
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/neural-ai", tags=["Neural AI Agents"])

class NeuralChatRequest(BaseModel):
    agent_type: str  # "sales", "service", "delivery"
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None  # For logged-in users - enables context retention
    context: Optional[Dict[str, Any]] = None

class ServiceTicketCreate(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: str
    customer_address: str
    product_model: str
    product_brand: str
    issue_description: str
    purchase_date: Optional[str] = None
    session_id: str

@router.post("/chat")
async def neural_chat(request: NeuralChatRequest, db = Depends(get_db)):
    """
    Main endpoint for Neural AI chat
    Supports: sales, service, delivery agents
    """
    try:
        # Generate session_id if not provided
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        
        # Initialize Neural AI Manager with database connection
        manager = NeuralAIAgentManager(db=db)
        
        # Store user message in database with user_id for context retention
        user_message_doc = {
            "id": str(uuid.uuid4()),
            "session_id": request.session_id,
            "user_id": request.user_id,  # Store user_id for future session retrieval
            "agent_type": request.agent_type,
            "sender": "user",
            "message": request.message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await db.chat_messages.insert_one(user_message_doc)
        
        # Get Neural AI response
        context = request.context or {}
        context['session_id'] = request.session_id
        
        response_data = await manager.get_neural_response(
            agent_type=request.agent_type,
            message=request.message,
            context=context
        )
        
        # Store AI response in database
        ai_message_doc = {
            "id": str(uuid.uuid4()),
            "session_id": request.session_id,
            "agent_type": request.agent_type,
            "sender": "ai",
            "message": response_data['response'],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "collected_data": response_data.get('collected_data', {}),
            "action_required": response_data.get('action_required', ''),
            "confidence": response_data.get('confidence', 0.0),
            "ticket_number": response_data.get('ticket_number'),
            "payment_link": response_data.get('payment_link'),
            "order_id": response_data.get('order_id')
        }
        await db.chat_messages.insert_one(ai_message_doc)
        
        return {
            "status": "success",
            "session_id": request.session_id,
            "response": response_data['response'],
            "collected_data": response_data.get('collected_data', {}),
            "action_required": response_data.get('action_required', ''),
            "confidence": response_data.get('confidence', 0.0),
            "ticket_number": response_data.get('ticket_number'),
            "payment_link": response_data.get('payment_link'),
            "order_id": response_data.get('order_id')
        }
        
    except Exception as e:
        logger.error(f"Neural AI chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-service-ticket")
async def create_service_ticket(ticket: ServiceTicketCreate, db = Depends(get_db)):
    """
    Create service ticket when Neural Service Agent escalates issue
    """
    try:
        # Generate ticket number
        ticket_number = f"ADR-SVC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Create ticket document
        ticket_doc = {
            "id": str(uuid.uuid4()),
            "ticket_number": ticket_number,
            "session_id": ticket.session_id,
            "customer_name": ticket.customer_name,
            "customer_email": ticket.customer_email,
            "customer_phone": ticket.customer_phone,
            "customer_address": ticket.customer_address,
            "product_model": ticket.product_model,
            "product_brand": ticket.product_brand,
            "issue_description": ticket.issue_description,
            "purchase_date": ticket.purchase_date,
            "status": "open",
            "priority": "medium",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "created_by": "neural_service_ai",
            "assigned_to": None,
            "resolution": None,
            "brand_complaint_number": None,
            "technician_name": None,
            "technician_phone": None,
            "scheduled_visit_date": None,
            "notes": []
        }
        
        # Save to database
        await db.service_tickets.insert_one(ticket_doc)
        
        # Send email notification (using existing email service)
        try:
            await send_service_ticket_email(ticket_doc, db)
        except Exception as e:
            logger.error(f"Error sending ticket email: {str(e)}")
        
        return {
            "status": "success",
            "ticket_number": ticket_number,
            "message": f"Service ticket {ticket_number} created successfully",
            "ticket_details": {
                "ticket_number": ticket_number,
                "customer_name": ticket.customer_name,
                "product": f"{ticket.product_brand} {ticket.product_model}",
                "status": "open",
                "created_at": ticket_doc["created_at"]
            }
        }
        
    except Exception as e:
        logger.error(f"Service ticket creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation-history/{session_id}")
async def get_conversation_history(
    session_id: str, 
    agent_type: Optional[str] = None,
    db = Depends(get_db)
):
    """Get conversation history for a session"""
    try:
        query = {"session_id": session_id}
        if agent_type:
            query["agent_type"] = agent_type
        
        messages = await db.chat_messages.find(
            query,
            {"_id": 0}
        ).sort("timestamp", 1).to_list(100)
        
        return {
            "status": "success",
            "session_id": session_id,
            "message_count": len(messages),
            "messages": messages
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-sessions/{user_id}")
async def get_user_chat_sessions(
    user_id: str,
    agent_type: Optional[str] = None,
    limit: int = 10,
    db = Depends(get_db)
):
    """Get recent chat sessions for a logged-in user"""
    try:
        # Find sessions for this user
        match_query = {"user_id": user_id}
        if agent_type:
            match_query["agent_type"] = agent_type
        
        # Get unique sessions with latest message
        pipeline = [
            {"$match": match_query},
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": {"session_id": "$session_id", "agent_type": "$agent_type"},
                "last_message": {"$first": "$message"},
                "last_timestamp": {"$first": "$timestamp"},
                "message_count": {"$sum": 1}
            }},
            {"$sort": {"last_timestamp": -1}},
            {"$limit": limit}
        ]
        
        sessions = await db.chat_messages.aggregate(pipeline).to_list(limit)
        
        formatted_sessions = []
        for s in sessions:
            formatted_sessions.append({
                "session_id": s["_id"]["session_id"],
                "agent_type": s["_id"]["agent_type"],
                "last_message": s["last_message"][:100] + "..." if len(s["last_message"]) > 100 else s["last_message"],
                "last_timestamp": s["last_timestamp"],
                "message_count": s["message_count"]
            })
        
        return {
            "status": "success",
            "user_id": user_id,
            "sessions": formatted_sessions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resume-session")
async def resume_chat_session(
    session_id: str,
    user_id: Optional[str] = None,
    db = Depends(get_db)
):
    """Resume a previous chat session - returns conversation history"""
    try:
        # Get conversation history
        messages = await db.chat_messages.find(
            {"session_id": session_id},
            {"_id": 0}
        ).sort("timestamp", 1).to_list(50)
        
        if not messages:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get agent type from first message
        agent_type = messages[0].get("agent_type", "sales")
        
        # Extract collected data from the session
        collected_data = {}
        for msg in messages:
            if msg.get("collected_data"):
                collected_data.update(msg["collected_data"])
        
        return {
            "status": "success",
            "session_id": session_id,
            "agent_type": agent_type,
            "messages": messages,
            "collected_data": collected_data,
            "can_resume": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/service-tickets")
async def get_service_tickets(
    status: Optional[str] = None,
    customer_email: Optional[str] = None,
    db = Depends(get_db)
):
    """Get service tickets with optional filters"""
    try:
        query = {}
        if status:
            query["status"] = status
        if customer_email:
            query["customer_email"] = customer_email
        
        tickets = await db.service_tickets.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).limit(50).to_list(50)
        
        return {
            "status": "success",
            "count": len(tickets),
            "tickets": tickets
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/service-tickets/{ticket_number}")
async def get_service_ticket_details(ticket_number: str, db = Depends(get_db)):
    """Get detailed information about a specific service ticket"""
    try:
        ticket = await db.service_tickets.find_one(
            {"ticket_number": ticket_number},
            {"_id": 0}
        )
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return {
            "status": "success",
            "ticket": ticket
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/service-tickets/{ticket_number}/status")
async def update_ticket_status(
    ticket_number: str,
    status: str,
    notes: Optional[str] = None,
    db = Depends(get_db)
):
    """Update service ticket status"""
    try:
        update_doc = {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if notes:
            # Append note to notes array
            note_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "note": notes
            }
            update_result = await db.service_tickets.update_one(
                {"ticket_number": ticket_number},
                {
                    "$set": update_doc,
                    "$push": {"notes": note_entry}
                }
            )
        else:
            update_result = await db.service_tickets.update_one(
                {"ticket_number": ticket_number},
                {"$set": update_doc}
            )
        
        if update_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return {
            "status": "success",
            "message": f"Ticket {ticket_number} updated to {status}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def send_service_ticket_email(ticket_doc: Dict[str, Any], db):
    """Send service ticket confirmation email"""
    try:
        from sendgrid_email_service import sendgrid_email_service
        
        # Email configuration from environment
        service_email = os.environ.get('SERVICE_EMAIL', 'service.adityaretail@gmail.com')
        
        # Email content
        email_subject = f"Service Ticket Created: {ticket_doc['ticket_number']}"
        email_body = f"""
Dear {ticket_doc['customer_name']},

Your service request has been successfully registered with Aditya Retail.

TICKET DETAILS:
--------------
Ticket Number: {ticket_doc['ticket_number']}
Product: {ticket_doc['product_brand']} {ticket_doc['product_model']}
Issue: {ticket_doc['issue_description']}
Status: {ticket_doc['status']}
Created: {ticket_doc['created_at']}

WHAT'S NEXT:
-----------
1. Our service team will review your request within 24-48 hours
2. You'll receive an email with the brand complaint number
3. Brand technician will contact you to schedule a visit
4. We'll follow up to ensure your issue is resolved

You can check your ticket status anytime in your customer dashboard or by replying to this email.

For urgent matters, call us at: +91-80-23460269
Service Email: {service_email}

Thank you for choosing Aditya Retail!

Best regards,
Aditya Retail Service Team
"""
        
        # Send email immediately using SendGrid
        email_result = sendgrid_email_service.send_email(
            to_email=ticket_doc['customer_email'],
            subject=email_subject,
            body=email_body,
            from_account="service"
        )
        
        # Store email record in database
        email_doc = {
            "id": str(uuid.uuid4()),
            "to": ticket_doc['customer_email'],
            "from": service_email,
            "subject": email_subject,
            "body": email_body,
            "status": "sent" if email_result.get("success") else "failed",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "sent_at": datetime.now(timezone.utc).isoformat() if email_result.get("success") else None,
            "ticket_number": ticket_doc['ticket_number'],
            "sendgrid_response": email_result
        }
        
        await db.outgoing_emails.insert_one(email_doc)
        logger.info(f"Service ticket email sent to {ticket_doc['customer_email']}: {email_result}")
        
    except Exception as e:
        logger.error(f"Error sending service ticket email: {str(e)}")

import os
