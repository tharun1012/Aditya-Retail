from fastapi import APIRouter, HTTPException
from sendgrid_email_service import sendgrid_email_service
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/email-test", tags=["Email Testing - SendGrid"])

class TestEmailRequest(BaseModel):
    to_email: EmailStr
    agent_type: str = "service"  # service, delivery, or sales

@router.post("/send")
async def send_test_email(request: TestEmailRequest):
    """Send a test email to verify configuration"""
    
    try:
        subject = "Test Email from Aditya Retail"
        body = f"""
Hello,

This is a test email from Aditya Retail {request.agent_type.title()} Team.

If you're receiving this email, your email configuration is working correctly!

Timestamp: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best regards,
Aditya Retail {request.agent_type.title()} Team
"""
        
        result = sendgrid_email_service.send_email(
            to_email=request.to_email,
            subject=subject,
            body=body,
            from_agent=request.agent_type,
            html=False
        )
        
        return {
            "status": "success" if result.get("status") == "success" else "error",
            "message": result.get("message"),
            "from": result.get("from"),
            "to": request.to_email,
            "agent": request.agent_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending test email: {str(e)}")

@router.get("/test-connection/{agent_type}")
async def test_connection(agent_type: str):
    """Test SendGrid API connection for an agent type"""
    
    if agent_type not in ["service", "delivery", "sales"]:
        raise HTTPException(status_code=400, detail="Invalid agent type. Use 'service', 'delivery', or 'sales'")
    
    result = sendgrid_email_service.test_sendgrid_connection(agent_type)
    
    return result

@router.get("/config")
async def get_email_config():
    """Get SendGrid email configuration"""
    
    config = {
        "email_service": "SendGrid",
        "api_key_configured": bool(sendgrid_email_service.api_key),
        "service_email": sendgrid_email_service.email_accounts["service"]["email"],
        "delivery_email": sendgrid_email_service.email_accounts["delivery"]["email"],
        "sales_email": sendgrid_email_service.email_accounts["sales"]["email"],
        "brand_emails": sendgrid_email_service.brand_emails,
        "support_phone": sendgrid_email_service.support_phone
    }
    
    return {
        "status": "success",
        "config": config
    }
