"""
Email Lead Capture Routes
API endpoints for receiving forwarded emails and parsing them into leads
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr
from database import get_db
from email_lead_capture_service import email_lead_capture_service

router = APIRouter(prefix="/email-capture", tags=["Email Lead Capture"])

class EmailForwardRequest(BaseModel):
    from_email: EmailStr
    to_email: EmailStr  # Which store email received this
    subject: str
    body: str
    received_at: Optional[str] = None

@router.post("/parse")
async def parse_forwarded_email(
    email_data: EmailForwardRequest,
    db = Depends(get_db)
):
    """
    Parse forwarded email and create lead
    Supports: SingleInterface, BSH Direct
    """
    
    try:
        lead_data = None
        email_type = None
        
        # Determine email type and parse accordingly
        if 'singleinterface.com' in email_data.from_email.lower():
            # SingleInterface format
            lead_data = email_lead_capture_service.parse_singleinterface_email(
                email_data.body,
                email_data.to_email
            )
            email_type = 'singleinterface'
            
        elif 'bshg.com' in email_data.from_email.lower() or 'brand store' in email_data.subject.lower():
            # BSH Direct format
            lead_data = email_lead_capture_service.parse_bsh_email(
                email_data.body,
                email_data.subject,
                email_data.to_email
            )
            email_type = 'bsh_direct'
        
        elif 'justdial' in email_data.from_email.lower() or 'jd.com' in email_data.from_email.lower():
            # JustDial format
            lead_data = email_lead_capture_service.parse_justdial_email(
                email_data.body,
                email_data.subject,
                email_data.to_email
            )
            email_type = 'justdial'
            
        else:
            return {
                "status": "unsupported",
                "message": f"Email format not recognized from {email_data.from_email}"
            }
        
        if not lead_data:
            raise HTTPException(status_code=400, detail="Failed to parse email content")
        
        # Create lead in database
        lead_id = await email_lead_capture_service.create_lead_from_email(
            lead_data,
            email_type,
            db
        )
        
        if not lead_id:
            raise HTTPException(status_code=500, detail="Failed to create lead")
        
        return {
            "status": "success",
            "message": f"Lead created successfully from {email_type} email",
            "lead_id": lead_id,
            "lead_data": {
                "name": lead_data.get('name'),
                "email": lead_data.get('email'),
                "phone": lead_data.get('phone'),
                "source": lead_data.get('source'),
                "store": lead_data.get('store_location'),
                "status": lead_data.get('status', 'new')
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing email: {str(e)}")

@router.post("/webhook")
async def email_webhook(
    payload: Dict[str, Any] = Body(...),
    db = Depends(get_db)
):
    """
    Webhook endpoint for email services (SendGrid Inbound Parse, etc.)
    Automatically processes incoming emails
    """
    
    try:
        # Extract email data from webhook payload
        # Format varies by provider, this is a generic handler
        
        from_email = payload.get('from', payload.get('sender', '')).lower()
        to_email = payload.get('to', payload.get('recipient', '')).lower()
        subject = payload.get('subject', '')
        body = payload.get('text', payload.get('html', payload.get('body', '')))
        
        if not from_email or not body:
            raise HTTPException(status_code=400, detail="Missing required email fields")
        
        # Create EmailForwardRequest object
        email_request = EmailForwardRequest(
            from_email=from_email,
            to_email=to_email,
            subject=subject,
            body=body
        )
        
        # Parse and create lead
        result = await parse_forwarded_email(email_request, db)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing error: {str(e)}")

@router.get("/test")
async def test_email_parsing():
    """
    Test endpoint to verify email parsing logic
    """
    
    # Sample SingleInterface email
    singleinterface_sample = """Dear Alfred,

You have just received a contact query on your website. The following are the details:

User Name: Priya Sharma
Mobile: 9876543210
Email: priya.test@example.com
Interest In: Washing Machines / Dryers
Query Type: Pricing / Offers
Planning Time: Immediately

Regards,
BOSCH Brand Store - Aditya Retail

Query from,
No 2297M/, HRBR Layout, 2nd Block, HRBR Layout, Banasawadi, Bengaluru, Karnataka
"""
    
    parsed_single = email_lead_capture_service.parse_singleinterface_email(
        singleinterface_sample,
        "banaswadi.adityaretail@gmail.com"
    )
    
    # Sample BSH email
    bsh_sample = """Dear BOSCH Brand Store - Aditya Retail Team,

You received a new hot lead for Bengaluru Locality. Please find the details below.

Lead Details:
Name: Manjula Raghavendra
Mob: p:+919901269831
Product Inquiry: Overall festive offers
Buying Intent: just_exploring_
City: Bangalore
Pin Code: 560049

Action Required:
Please contact prospects within 10 business hours.
"""
    
    parsed_bsh = email_lead_capture_service.parse_bsh_email(
        bsh_sample,
        "New Lead Notification to BOSCH Brand Store - Aditya Retail",
        "bosch.adityaretail@gmail.com"
    )
    
    # Sample JustDial email
    justdial_sample = """Hi,

A new lead for your business from JustDial.

Lead Details:
Customer Name: Ramesh Kumar
Contact No: 9845123456
Email: ramesh.kumar@email.com
City: Bangalore
Location: Koramangala
Requirement: Looking for Bosch Refrigerator

Please contact the customer within 24 hours.

Thanks,
JustDial Team
"""
    
    parsed_justdial = email_lead_capture_service.parse_justdial_email(
        justdial_sample,
        "New Lead from JustDial",
        "banaswadi.adityaretail@gmail.com"
    )
    
    return {
        "status": "success",
        "message": "Email parsing test",
        "singleinterface_parsed": parsed_single,
        "bsh_parsed": parsed_bsh,
        "justdial_parsed": parsed_justdial
    }

@router.get("/instructions")
async def get_forwarding_instructions():
    """
    Provide instructions for setting up email forwarding
    """
    
    return {
        "title": "Email Auto-Capture Setup Instructions",
        "overview": "Forward brand emails to our system to automatically create leads",
        "supported_formats": [
            "SingleInterface (clientsupport1@singleinterface.com)",
            "BSH Direct (Abhishek.Kumar2@bshg.com)",
            "JustDial (leads@justdial.com, notifications@jd.com)"
        ],
        "stores": {
            "banaswadi": "banaswadi.adityaretail@gmail.com",
            "bosch": "bosch.adityaretail@gmail.com",
            "dasarahalli": "dasarahalli.adityaretail@gmail.com"
        },
        "setup_steps": [
            {
                "step": 1,
                "title": "Gmail Forwarding Setup",
                "instructions": [
                    "Open Gmail for each store account",
                    "Click Settings (gear icon) → See all settings",
                    "Go to 'Filters and Blocked Addresses' tab",
                    "Click 'Create a new filter'",
                    "In 'From' field, enter: clientsupport1@singleinterface.com OR Abhishek.Kumar2@bshg.com",
                    "Click 'Create filter'",
                    "Check 'Forward it to' and enter webhook email",
                    "Click 'Create filter'"
                ]
            },
            {
                "step": 2,
                "title": "Alternative: Manual Forwarding",
                "instructions": [
                    "When you receive a lead email from SingleInterface or BSH",
                    "Forward it to: leads-capture@adityaretail.com",
                    "System will automatically parse and create lead",
                    "You'll see it in the leads dashboard within seconds"
                ]
            },
            {
                "step": 3,
                "title": "Verification",
                "instructions": [
                    "After setup, forward a test email",
                    "Check leads dashboard for new entry",
                    "Lead should show correct store location and source",
                    "Customer should receive welcome email automatically"
                ]
            }
        ],
        "api_endpoint": "/api/email-capture/parse",
        "webhook_endpoint": "/api/email-capture/webhook"
    }
