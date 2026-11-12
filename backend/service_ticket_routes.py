from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field
import uuid
from database import get_db
from sendgrid_email_service import sendgrid_email_service

router = APIRouter(prefix="/service-tickets", tags=["Service Tickets"])

# Pydantic Models
class CustomerDetails(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

class ProductDetails(BaseModel):
    product_name: str
    brand: str
    model_number: Optional[str] = None
    purchase_date: Optional[str] = None
    warranty_status: Optional[str] = "Unknown"

class ServiceTicketCreate(BaseModel):
    customer_details: CustomerDetails
    product_details: ProductDetails
    issue_description: str
    troubleshooting_attempted: Optional[str] = None
    session_id: Optional[str] = None
    priority: Optional[str] = "normal"
    source: Optional[str] = "ai_chat"

class ServiceTicketUpdate(BaseModel):
    brand_complaint_number: Optional[str] = None
    brand_response_date: Optional[str] = None
    status: Optional[str] = None
    technician_assigned: Optional[str] = None
    resolution_notes: Optional[str] = None

class TicketFeedback(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None

# Email configuration is now handled by email_service_new

@router.post("/")
async def create_ticket_root(
    ticket_data: ServiceTicketCreate,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Create a new service ticket (alias for /create)"""
    return await create_service_ticket(ticket_data, background_tasks, db)

@router.post("/create")
async def create_service_ticket(
    ticket_data: ServiceTicketCreate,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """
    Create a new service ticket and send email to brand service
    """
    try:
        # Generate ticket ID
        ticket_id = f"ADR-SRV-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Create ticket document
        ticket = {
            "ticket_id": ticket_id,
            "customer_details": ticket_data.customer_details.dict(),
            "product_details": ticket_data.product_details.dict(),
            "issue_description": ticket_data.issue_description,
            "troubleshooting_attempted": ticket_data.troubleshooting_attempted,
            "session_id": ticket_data.session_id,
            "status": "open",  # open, awaiting_brand_response, brand_ticket_created, in_progress, resolved, closed
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "brand_complaint_number": None,
            "brand_response_date": None,
            "technician_assigned": None,
            "resolution_date": None,
            "resolution_notes": None,
            "customer_feedback": None,
            "customer_rating": None,
            "follow_ups": []
        }
        
        # Insert into database
        await db.service_tickets.insert_one(ticket)
        
        # Send email to brand service
        brand = ticket_data.product_details.brand
        brand_email = sendgrid_email_service.get_brand_email(brand)
        service_email = sendgrid_email_service.email_accounts["service"]["email"]
        
        if brand_email:
            # Prepare email content
            email_subject = f"Service Request - {ticket_data.product_details.product_name} - Ticket {ticket_id}"
            email_body = f"""
Dear {brand} Service Team,

We are writing on behalf of our customer regarding a service request for their {brand} product.

CUSTOMER DETAILS:
Name: {ticket_data.customer_details.name}
Phone: {ticket_data.customer_details.phone}
Email: {ticket_data.customer_details.email}
Address: {ticket_data.customer_details.address}

PRODUCT DETAILS:
Product: {ticket_data.product_details.product_name}
Brand: {brand}
Model Number: {ticket_data.product_details.model_number or 'Not provided'}
Purchase Date: {ticket_data.product_details.purchase_date or 'Not provided'}
Warranty Status: {ticket_data.product_details.warranty_status}

ISSUE DESCRIPTION:
{ticket_data.issue_description}

TROUBLESHOOTING ATTEMPTED:
{ticket_data.troubleshooting_attempted or 'Customer requires technician assistance'}

Our internal ticket number: {ticket_id}

Please assign this service request and provide us with your complaint/ticket number for our records.

Best regards,
Aditya Retail Service Team
{service_email}
"""
            
            # Send email to brand service
            email_result = sendgrid_email_service.send_email(
                to_email=brand_email,
                subject=email_subject,
                body=email_body,
                from_agent="service",
                html=False
            )
            
            # Update ticket status
            await db.service_tickets.update_one(
                {"ticket_id": ticket_id},
                {"$set": {
                    "status": "awaiting_brand_response",
                    "brand_email_sent_at": datetime.now(timezone.utc).isoformat(),
                    "brand_email": brand_email,
                    "brand_email_status": email_result.get("status")
                }}
            )
            
            if email_result.get("status") == "success":
                print(f"✅ Email sent to {brand_email} for ticket {ticket_id}")
            else:
                print(f"⚠️ Email failed to {brand_email}: {email_result.get('message')}")
        
        # Send confirmation email to customer (in background)
        customer_email_subject = f"Service Request Received - Ticket {ticket_id}"
        customer_email_body = f"""
Dear {ticket_data.customer_details.name},

Thank you for contacting Aditya Retail Service Center.

We have received your service request for:
Product: {ticket_data.product_details.product_name}
Brand: {brand}

Your ticket number is: {ticket_id}

We have forwarded your request to the {brand} service team and will update you once we receive a complaint number from them.

Expected response time: 24-48 hours

You can track your service request status by contacting us with your ticket number.

For urgent queries, please call: {sendgrid_email_service.support_phone}

Best regards,
Aditya Retail Service Team
"""
        
        # Send confirmation email to customer
        customer_email_result = sendgrid_email_service.send_email(
            to_email=ticket_data.customer_details.email,
            subject=customer_email_subject,
            body=customer_email_body,
            from_agent="service",
            html=False
        )
        
        if customer_email_result.get("status") == "success":
            print(f"✅ Confirmation email sent to {ticket_data.customer_details.email}")
        else:
            print(f"⚠️ Confirmation email failed: {customer_email_result.get('message')}")
        
        return {
            "status": "success",
            "message": "Service ticket created successfully. Emails sent to brand service and customer.",
            "ticket_id": ticket_id,
            "ticket_status": "awaiting_brand_response",
            "brand_email": brand_email if brand_email else "Brand email not configured",
            "emails_sent": {
                "brand": email_result.get("status") if brand_email else "N/A",
                "customer": customer_email_result.get("status")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating service ticket: {str(e)}")

@router.get("/")
async def get_service_tickets(
    status: Optional[str] = None,
    customer_email: Optional[str] = None,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get all service tickets with optional filters"""
    try:
        query = {}
        
        if status:
            query["status"] = status
        
        if customer_email:
            query["customer_details.email"] = customer_email
        
        tickets = await db.service_tickets.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
        
        return {
            "status": "success",
            "total": len(tickets),
            "tickets": tickets
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching service tickets: {str(e)}")

@router.get("/{ticket_id}")
async def get_service_ticket(ticket_id: str, db = Depends(get_db)):
    """Get a specific service ticket by ID"""
    try:
        ticket = await db.service_tickets.find_one({"ticket_id": ticket_id}, {"_id": 0})
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Service ticket not found")
        
        return {
            "status": "success",
            "ticket": ticket
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching service ticket: {str(e)}")

@router.put("/{ticket_id}/update")
async def update_service_ticket(
    ticket_id: str,
    update_data: ServiceTicketUpdate,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Update service ticket with brand complaint number or status"""
    try:
        # Get existing ticket (supports both nested ticket_id and flat ticket_number schemas)
        ticket = await db.service_tickets.find_one(
            {"$or": [{"ticket_id": ticket_id}, {"ticket_number": ticket_id}, {"id": ticket_id}]},
            {"_id": 0}
        )
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Service ticket not found")
        
        # Prepare update
        update_fields = {
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        customer_email = ticket.get("customer_details", {}).get("email") or ticket.get("customer_email")
        customer_name = ticket.get("customer_details", {}).get("name") or ticket.get("customer_name")
        brand = ticket.get("product_details", {}).get("brand") or ticket.get("brand")
        product_name = ticket.get("product_details", {}).get("product_name") or ticket.get("product_name")
        
        if update_data.brand_complaint_number:
            update_fields["brand_complaint_number"] = update_data.brand_complaint_number
            update_fields["brand_response_date"] = update_data.brand_response_date or datetime.now(timezone.utc).isoformat()
            update_fields["status"] = "brand_ticket_created"
            
            # Send email to customer with brand complaint number
            if customer_email:
                email_subject = f"✅ Service Update - Brand Complaint Number Received - {ticket_id}"
                email_body = f"""Dear {customer_name},

Good news! Your service request has been registered with {brand} service team.

📋 TICKET DETAILS:
Your Aditya Retail Ticket: {ticket_id}
{brand} Complaint Number: {update_data.brand_complaint_number}
Product: {product_name}

⏰ NEXT STEPS:
A {brand} certified technician will contact you within 24-48 hours to schedule a service visit.

📞 FOR QUERIES:
Please reference both ticket numbers when contacting us or {brand} service team.
Aditya Retail Support: {sendgrid_email_service.support_phone}

Thank you for choosing Aditya Retail.

Best regards,
Aditya Retail Service Team
"""
                
                # Send email to customer
                email_result = sendgrid_email_service.send_email(
                    to_email=customer_email,
                    subject=email_subject,
                    body=email_body,
                    from_agent="service",
                    html=False
                )
                
                if email_result.get("status") == "success":
                    print(f"✅ Brand complaint number email sent to {customer_email}")
        
        if update_data.status:
            update_fields["status"] = update_data.status
            
            if update_data.status == "resolved":
                update_fields["resolution_date"] = datetime.now(timezone.utc).isoformat()
                
                # Send resolution notification to customer
                if customer_email:
                    email_subject = f"🎉 Service Ticket Resolved - {ticket_id}"
                    email_body = f"""Dear {customer_name},

Great news! Your service ticket has been marked as RESOLVED.

📋 TICKET DETAILS:
Ticket Number: {ticket_id}
Brand Complaint Number: {ticket.get('brand_complaint_number', 'N/A')}
Product: {product_name}
Resolution Date: {datetime.now(timezone.utc).strftime('%d %B %Y')}

{f"Resolution Notes: {update_data.resolution_notes}" if update_data.resolution_notes else ""}

We hope your {product_name} is working perfectly now!

⭐ FEEDBACK REQUEST:
We'd love to hear about your service experience. Please rate our service by replying to this email.

If you face any further issues, feel free to reach out to us anytime.

Thank you for choosing Aditya Retail!

Best regards,
Aditya Retail Service Team
Contact: {sendgrid_email_service.support_phone}
"""
                    
                    email_result = sendgrid_email_service.send_email(
                        to_email=customer_email,
                        subject=email_subject,
                        body=email_body,
                        from_agent="service",
                        html=False
                    )
                    
                    if email_result.get("status") == "success":
                        print(f"✅ Resolution email sent to {customer_email}")
        
        if update_data.technician_assigned:
            update_fields["technician_assigned"] = update_data.technician_assigned
            if ticket.get("status") not in ["resolved", "closed"]:
                update_fields["status"] = "in_progress"
        
        if update_data.resolution_notes:
            update_fields["resolution_notes"] = update_data.resolution_notes
        
        # Update ticket
        ticket_query = {"$or": [{"ticket_id": ticket_id}, {"ticket_number": ticket_id}, {"id": ticket_id}]}
        await db.service_tickets.update_one(
            ticket_query,
            {"$set": update_fields}
        )
        
        # Get updated ticket
        updated_ticket = await db.service_tickets.find_one(ticket_query, {"_id": 0})
        
        return {
            "status": "success",
            "message": "Service ticket updated successfully. Customer notified via email.",
            "ticket": updated_ticket
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating service ticket: {str(e)}")

@router.post("/{ticket_id}/follow-up")
async def add_follow_up(
    ticket_id: str,
    follow_up_note: str,
    agent_name: Optional[str] = "Service Agent",
    db = Depends(get_db)
):
    """Add a follow-up note to service ticket"""
    try:
        follow_up = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent_name,
            "note": follow_up_note
        }
        
        result = await db.service_tickets.update_one(
            {"ticket_id": ticket_id},
            {
                "$push": {"follow_ups": follow_up},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Service ticket not found")
        
        return {
            "status": "success",
            "message": "Follow-up added successfully",
            "follow_up": follow_up
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding follow-up: {str(e)}")

@router.post("/{ticket_id}/feedback")
async def submit_feedback(
    ticket_id: str,
    feedback_data: TicketFeedback,
    db = Depends(get_db)
):
    """Submit customer feedback and rating for resolved ticket"""
    try:
        # Update ticket with feedback and close it
        result = await db.service_tickets.update_one(
            {"ticket_id": ticket_id},
            {
                "$set": {
                    "customer_rating": feedback_data.rating,
                    "customer_feedback": feedback_data.feedback,
                    "status": "closed",
                    "closed_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Service ticket not found")
        
        return {
            "status": "success",
            "message": "Thank you for your feedback! Your ticket has been closed.",
            "rating": feedback_data.rating
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

@router.get("/stats/summary")
async def get_ticket_stats(db = Depends(get_db)):
    """Get service ticket statistics"""
    try:
        # Get all tickets
        all_tickets = await db.service_tickets.find({}, {"_id": 0}).to_list(1000)
        
        # Calculate stats
        total_tickets = len(all_tickets)
        open_tickets = len([t for t in all_tickets if t.get("status") in ["open", "awaiting_brand_response"]])
        in_progress = len([t for t in all_tickets if t.get("status") in ["brand_ticket_created", "in_progress"]])
        resolved = len([t for t in all_tickets if t.get("status") == "resolved"])
        closed = len([t for t in all_tickets if t.get("status") == "closed"])
        
        # Calculate average rating
        ratings = [t.get("customer_rating", 0) for t in all_tickets if t.get("customer_rating")]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        return {
            "status": "success",
            "stats": {
                "total_tickets": total_tickets,
                "open_tickets": open_tickets,
                "in_progress": in_progress,
                "resolved": resolved,
                "closed": closed,
                "average_rating": round(avg_rating, 2)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching ticket stats: {str(e)}")
