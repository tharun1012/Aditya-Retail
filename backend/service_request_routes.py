"""
Service Request Management System
AI Service Agent creates service requests and sends emails to brands
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from database import get_db

router = APIRouter(prefix="/service-requests", tags=["Service Requests"])

class ServiceRequestCreate(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: str
    product_id: str
    product_name: str
    brand: str
    issue_category: str  # installation, repair, maintenance, warranty_claim
    issue_description: str
    error_code: Optional[str] = None
    troubleshooting_attempted: Optional[str] = None
    urgency: str = "medium"  # low, medium, high, critical

class ServiceRequestUpdate(BaseModel):
    status: Optional[str] = None  # pending, assigned, in_progress, resolved, closed
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    estimated_resolution_date: Optional[str] = None

@router.post("/")
async def create_service_request(request: ServiceRequestCreate, db = Depends(get_db)):
    """Create new service request and send email to brand"""
    try:
        # Generate service request number
        sr_number = f"SR{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        
        # Create service request document
        service_request = {
            "id": str(uuid.uuid4()),
            "sr_number": sr_number,
            "customer_name": request.customer_name,
            "customer_email": request.customer_email,
            "customer_phone": request.customer_phone,
            "product_id": request.product_id,
            "product_name": request.product_name,
            "brand": request.brand,
            "issue_category": request.issue_category,
            "issue_description": request.issue_description,
            "error_code": request.error_code,
            "troubleshooting_attempted": request.troubleshooting_attempted,
            "urgency": request.urgency,
            "status": "pending",
            "assigned_to": None,
            "resolution_notes": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "resolved_at": None
        }
        
        # Save to database
        await db.service_requests.insert_one(service_request)
        
        # Send email to brand service team
        email_sent = await _send_service_request_email_to_brand(service_request)
        
        # Send confirmation email to customer
        customer_email_sent = await _send_customer_confirmation_email(service_request)
        
        return {
            "status": "success",
            "message": "Service request created successfully",
            "sr_number": sr_number,
            "service_request_id": service_request["id"],
            "brand_email_sent": email_sent,
            "customer_email_sent": customer_email_sent
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating service request: {str(e)}")

async def _send_service_request_email_to_brand(service_request: dict) -> bool:
    """Send service request email to brand service team"""
    try:
        # Brand service email mapping
        brand_emails = {
            "Bosch": os.environ.get("BOSCH_SERVICE_EMAIL", "service.bosch@example.com"),
            "Siemens": os.environ.get("SIEMENS_SERVICE_EMAIL", "service.siemens@example.com"),
            "Hindware": os.environ.get("HINDWARE_SERVICE_EMAIL", "service.hindware@example.com"),
        }
        
        brand_email = brand_emails.get(service_request["brand"], "service@adityaretail.com")
        
        # Email configuration
        smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ.get("SMTP_USER", "")
        smtp_password = os.environ.get("SMTP_PASSWORD", "")
        
        if not smtp_user or not smtp_password:
            print("SMTP credentials not configured")
            return False
        
        # Create email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🔧 Service Request: {service_request['sr_number']} - {service_request['brand']} {service_request['product_name']}"
        msg['From'] = smtp_user
        msg['To'] = brand_email
        msg['Cc'] = "service@adityaretail.com"
        
        # HTML email body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: #d32f2f; color: white; padding: 20px; }}
                .content {{ padding: 20px; background-color: #f5f5f5; }}
                .field {{ margin: 10px 0; }}
                .label {{ font-weight: bold; }}
                .urgent {{ color: #d32f2f; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🔧 New Service Request</h2>
                    <h3>SR Number: {service_request['sr_number']}</h3>
                </div>
                <div class="content">
                    <h3>Customer Information</h3>
                    <div class="field">
                        <span class="label">Name:</span> {service_request['customer_name']}
                    </div>
                    <div class="field">
                        <span class="label">Email:</span> {service_request['customer_email']}
                    </div>
                    <div class="field">
                        <span class="label">Phone:</span> {service_request['customer_phone']}
                    </div>
                    
                    <hr>
                    
                    <h3>Product Information</h3>
                    <div class="field">
                        <span class="label">Brand:</span> {service_request['brand']}
                    </div>
                    <div class="field">
                        <span class="label">Product:</span> {service_request['product_name']}
                    </div>
                    <div class="field">
                        <span class="label">Product ID:</span> {service_request['product_id']}
                    </div>
                    
                    <hr>
                    
                    <h3>Issue Details</h3>
                    <div class="field">
                        <span class="label">Category:</span> {service_request['issue_category'].replace('_', ' ').title()}
                    </div>
                    <div class="field">
                        <span class="label">Urgency:</span> <span class="{'urgent' if service_request['urgency'] in ['high', 'critical'] else ''}">{service_request['urgency'].upper()}</span>
                    </div>
                    {f'<div class="field"><span class="label">Error Code:</span> {service_request["error_code"]}</div>' if service_request.get('error_code') else ''}
                    <div class="field">
                        <span class="label">Issue Description:</span>
                        <p>{service_request['issue_description']}</p>
                    </div>
                    {f'<div class="field"><span class="label">Troubleshooting Attempted:</span><p>{service_request["troubleshooting_attempted"]}</p></div>' if service_request.get('troubleshooting_attempted') else ''}
                    
                    <hr>
                    
                    <div class="field">
                        <span class="label">Request Date:</span> {datetime.fromisoformat(service_request['created_at']).strftime('%d %B %Y, %I:%M %p')}
                    </div>
                    
                    <p><strong>Please acknowledge this service request and provide estimated resolution timeline.</strong></p>
                    
                    <p>Best regards,<br>
                    Aditya Retail Service Team<br>
                    service@adityaretail.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        print(f"Service request email sent to {brand_email}")
        return True
        
    except Exception as e:
        print(f"Error sending brand service email: {e}")
        return False

async def _send_customer_confirmation_email(service_request: dict) -> bool:
    """Send confirmation email to customer"""
    try:
        smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ.get("SMTP_USER", "")
        smtp_password = os.environ.get("SMTP_PASSWORD", "")
        
        if not smtp_user or not smtp_password:
            return False
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Service Request Confirmation - {service_request['sr_number']}"
        msg['From'] = smtp_user
        msg['To'] = service_request['customer_email']
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #d32f2f;">Service Request Confirmation</h2>
            
            <p>Dear {service_request['customer_name']},</p>
            
            <p>Thank you for contacting Aditya Retail Service. Your service request has been registered successfully.</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; margin: 20px 0;">
                <h3>Service Request Details</h3>
                <p><strong>SR Number:</strong> {service_request['sr_number']}</p>
                <p><strong>Product:</strong> {service_request['brand']} {service_request['product_name']}</p>
                <p><strong>Issue:</strong> {service_request['issue_category'].replace('_', ' ').title()}</p>
                <p><strong>Status:</strong> Pending</p>
            </div>
            
            <p>We have forwarded your request to the {service_request['brand']} service team. You will receive an update within 24-48 hours.</p>
            
            <p>For any queries, please contact us at:<br>
            Email: service@adityaretail.com<br>
            Phone: +91-XXXXXXXXXX<br>
            Reference: {service_request['sr_number']}</p>
            
            <p>Best regards,<br>
            Aditya Retail Service Team</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"Error sending customer email: {e}")
        return False

@router.get("/")
async def get_all_service_requests(
    status: Optional[str] = None,
    brand: Optional[str] = None,
    urgency: Optional[str] = None,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get all service requests with filters"""
    try:
        query = {}
        if status:
            query["status"] = status
        if brand:
            query["brand"] = brand
        if urgency:
            query["urgency"] = urgency
        
        requests = await db.service_requests.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
        
        return {
            "status": "success",
            "total": len(requests),
            "service_requests": requests
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/{sr_number}")
async def get_service_request(sr_number: str, db = Depends(get_db)):
    """Get service request by SR number"""
    try:
        request = await db.service_requests.find_one({"sr_number": sr_number}, {"_id": 0})
        
        if not request:
            raise HTTPException(status_code=404, detail="Service request not found")
        
        return {
            "status": "success",
            "service_request": request
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/{sr_number}")
async def update_service_request(
    sr_number: str,
    update: ServiceRequestUpdate,
    db = Depends(get_db)
):
    """Update service request status"""
    try:
        update_doc = {"updated_at": datetime.now(timezone.utc).isoformat()}
        
        if update.status:
            update_doc["status"] = update.status
            if update.status == "resolved":
                update_doc["resolved_at"] = datetime.now(timezone.utc).isoformat()
        
        if update.assigned_to:
            update_doc["assigned_to"] = update.assigned_to
        
        if update.resolution_notes:
            update_doc["resolution_notes"] = update.resolution_notes
        
        if update.estimated_resolution_date:
            update_doc["estimated_resolution_date"] = update.estimated_resolution_date
        
        result = await db.service_requests.update_one(
            {"sr_number": sr_number},
            {"$set": update_doc}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Service request not found")
        
        # Get updated request
        updated_request = await db.service_requests.find_one({"sr_number": sr_number}, {"_id": 0})
        
        # Send update email to customer
        if update.status:
            await _send_status_update_email(updated_request)
        
        return {
            "status": "success",
            "message": "Service request updated successfully",
            "service_request": updated_request
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

async def _send_status_update_email(service_request: dict) -> bool:
    """Send status update email to customer"""
    try:
        smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ.get("SMTP_USER", "")
        smtp_password = os.environ.get("SMTP_PASSWORD", "")
        
        if not smtp_user or not smtp_password:
            return False
        
        status_messages = {
            "assigned": "Your service request has been assigned to a technician.",
            "in_progress": "Our technician is working on your service request.",
            "resolved": "Your service request has been resolved.",
            "closed": "Your service request has been closed."
        }
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Service Request Update - {service_request['sr_number']}"
        msg['From'] = smtp_user
        msg['To'] = service_request['customer_email']
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #d32f2f;">Service Request Update</h2>
            
            <p>Dear {service_request['customer_name']},</p>
            
            <p>{status_messages.get(service_request['status'], 'Your service request has been updated.')}</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; margin: 20px 0;">
                <p><strong>SR Number:</strong> {service_request['sr_number']}</p>
                <p><strong>Status:</strong> {service_request['status'].replace('_', ' ').title()}</p>
                {f"<p><strong>Assigned To:</strong> {service_request['assigned_to']}</p>" if service_request.get('assigned_to') else ''}
                {f"<p><strong>Resolution Notes:</strong> {service_request['resolution_notes']}</p>" if service_request.get('resolution_notes') else ''}
            </div>
            
            <p>Thank you for your patience.</p>
            
            <p>Best regards,<br>
            Aditya Retail Service Team</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"Error sending status update email: {e}")
        return False
