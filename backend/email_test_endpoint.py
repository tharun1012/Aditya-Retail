"""
Email Testing Endpoint
Quick way to test if SendGrid email is working
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/email-test", tags=["Email Testing"])

class EmailTestRequest(BaseModel):
    to_email: EmailStr
    test_type: str = "basic"  # basic, welcome, order

@router.post("/send-test")
async def send_test_email(request: EmailTestRequest):
    """
    Send a test email to verify SendGrid is working
    
    Usage:
    POST /api/email-test/send-test
    {
        "to_email": "your-email@example.com",
        "test_type": "basic"
    }
    """
    
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("SALES_EMAIL", "sales.aronline@gmail.com")
    
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="SendGrid API key not configured. Check backend/.env file."
        )
    
    # Email templates
    templates = {
        "basic": {
            "subject": "✅ Test Email from Aditya Retail",
            "html": """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #2563eb;">Email System Test</h1>
                    <p>Congratulations! Your email system is working correctly.</p>
                    <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3>✅ What's Working:</h3>
                        <ul>
                            <li>SendGrid API connection ✓</li>
                            <li>Email delivery ✓</li>
                            <li>HTML rendering ✓</li>
                        </ul>
                    </div>
                    <p><strong>Next Steps:</strong></p>
                    <ol>
                        <li>Verify sender email in SendGrid dashboard</li>
                        <li>Set up domain authentication (optional)</li>
                        <li>Start sending automated campaigns!</li>
                    </ol>
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                    <p style="color: #6b7280; font-size: 12px;">
                        This is a test email from Aditya Retail AI Marketing System
                    </p>
                </div>
            """
        },
        "welcome": {
            "subject": "Welcome to Aditya Retail - Premium Home Appliances",
            "html": """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #2563eb;">Welcome to Aditya Retail! 🎉</h1>
                    <p>Thank you for your interest in our premium home appliances.</p>
                    
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin: 20px 0;">
                        <h2 style="margin-top: 0; color: white;">Why Choose Us?</h2>
                        <ul style="list-style: none; padding: 0;">
                            <li>✓ Authorized dealer of Siemens, Bosch & Hindware</li>
                            <li>✓ Free installation & setup</li>
                            <li>✓ Extended warranty options</li>
                            <li>✓ 24/7 customer support</li>
                        </ul>
                    </div>
                    
                    <p><strong>I'm Ai.ditya, your AI shopping assistant!</strong> I'm here to help you find the perfect appliance for your needs.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="#" style="background: #2563eb; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block;">
                            Book Free Demo
                        </a>
                    </div>
                    
                    <p>Questions? Simply reply to this email!</p>
                    
                    <hr style="margin: 30px 0;">
                    <p style="color: #6b7280; font-size: 12px;">
                        Aditya Retail | Premium Home Appliances<br>
                        📧 sales.aronline@gmail.com | 📞 +91-XXXXXXXXXX
                    </p>
                </div>
            """
        },
        "order": {
            "subject": "✅ Order Confirmed - #TEST12345",
            "html": """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #10b981;">Order Confirmed! 🎉</h1>
                    <p>Thank you for your order from Aditya Retail.</p>
                    
                    <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Order Details</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0;"><strong>Order ID:</strong></td>
                                <td style="text-align: right;">#TEST12345</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0;"><strong>Product:</strong></td>
                                <td style="text-align: right;">Siemens iQ700 Oven</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0;"><strong>Amount:</strong></td>
                                <td style="text-align: right;">₹1,85,000</td>
                            </tr>
                            <tr style="border-top: 2px solid #d1d5db;">
                                <td style="padding: 8px 0;"><strong>Payment Status:</strong></td>
                                <td style="text-align: right; color: #10b981;"><strong>PAID ✓</strong></td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background: #dbeafe; padding: 20px; border-radius: 8px; border-left: 4px solid #2563eb;">
                        <h4 style="margin-top: 0;">📦 Delivery Information</h4>
                        <p style="margin: 5px 0;">Estimated Delivery: Dec 23-24, 2025</p>
                        <p style="margin: 5px 0;">Address: [Customer Address]</p>
                    </div>
                    
                    <h3>What's Next?</h3>
                    <ol>
                        <li>Order being prepared (1-2 days)</li>
                        <li>Quality check</li>
                        <li>Dispatch notification</li>
                        <li>Delivery scheduling call</li>
                    </ol>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="#" style="background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                            Track Your Order
                        </a>
                    </div>
                    
                    <hr style="margin: 30px 0;">
                    <p style="color: #6b7280; font-size: 12px;">
                        Questions? Reply to this email or call us at +91-XXXXXXXXXX<br>
                        Aditya Retail - Your trusted partner for premium appliances
                    </p>
                </div>
            """
        }
    }
    
    template = templates.get(request.test_type, templates["basic"])
    
    try:
        message = Mail(
            from_email=from_email,
            to_emails=request.to_email,
            subject=template["subject"],
            html_content=template["html"]
        )
        
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        return {
            "status": "success",
            "message": f"Test email sent successfully to {request.to_email}",
            "status_code": response.status_code,
            "note": "Check your inbox (and spam folder) in 1-5 minutes",
            "from_email": from_email,
            "email_type": request.test_type
        }
        
    except Exception as e:
        error_message = str(e)
        
        # Provide helpful error messages
        if "The from email does not contain a valid address" in error_message:
            raise HTTPException(
                status_code=400,
                detail=f"Sender email '{from_email}' is not verified in SendGrid. Please verify it first: https://app.sendgrid.com/settings/sender_auth/senders"
            )
        elif "Unauthorized" in error_message:
            raise HTTPException(
                status_code=401,
                detail="SendGrid API key is invalid. Please check your API key in backend/.env"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Email sending failed: {error_message}"
            )

@router.get("/status")
async def check_email_status():
    """Check if email system is configured"""
    
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("SALES_EMAIL")
    service_email = os.getenv("SERVICE_EMAIL")
    delivery_email = os.getenv("DELIVERY_EMAIL")
    
    return {
        "status": "configured" if api_key else "not_configured",
        "api_key_present": bool(api_key),
        "email_accounts": {
            "sales": from_email or "Not configured",
            "service": service_email or "Not configured",
            "delivery": delivery_email or "Not configured"
        },
        "next_steps": [
            "Verify sender emails in SendGrid dashboard",
            "Test email sending using /api/email-test/send-test",
            "Set up domain authentication (optional)"
        ] if api_key else [
            "Add SENDGRID_API_KEY to backend/.env",
            "Add email addresses (SALES_EMAIL, SERVICE_EMAIL, DELIVERY_EMAIL)"
        ]
    }
