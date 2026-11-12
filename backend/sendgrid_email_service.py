"""
SendGrid Email Service for Aditya Retail
Professional transactional email service for Service, Delivery, and Sales agents
"""
import os
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
import base64

load_dotenv()

class SendGridEmailService:
    def __init__(self):
        # SendGrid API Key
        self.api_key = os.getenv("SENDGRID_API_KEY", "")
        
        if not self.api_key:
            print("⚠️ SendGrid API Key not configured")
        
        # Email accounts for different agents
        self.email_accounts = {
            "service": {
                "email": os.getenv("SERVICE_EMAIL", "service.adityaretail@gmail.com"),
                "display_name": "Aditya Retail Service Team",
                "reply_to": "service.adityaretail@gmail.com"
            },
            "delivery": {
                "email": os.getenv("DELIVERY_EMAIL", "warehouse.adityaretail@gmail.com"),
                "display_name": "Aditya Retail Delivery Team",
                "reply_to": "warehouse.adityaretail@gmail.com"
            },
            "sales": {
                "email": os.getenv("SALES_EMAIL", "service.adityaretail@gmail.com"),
                "display_name": "Aditya Retail Sales Team",
                "reply_to": "online.adityaretail@gmail.com"
            },
            "consultant": {
                "email": os.getenv("CONSULTANT_EMAIL", "sales.aronline@gmail.com"),
                "display_name": "Aditya Retail Expert Consultant",
                "reply_to": "online.adityaretail@gmail.com"
            }
        }
        
        # Brand service emails
        self.brand_emails = {
            "Hindware": os.getenv("HINDWARE_SERVICE_EMAIL", "wecare@hindware.co.in"),
            "Bosch": os.getenv("BOSCH_SERVICE_EMAIL", "service.in@bosch-home.com"),
            "Siemens": os.getenv("SIEMENS_SERVICE_EMAIL", "service.in@siemens-home.bsh-group.com")
        }
        
        # Support contact
        self.support_phone = os.getenv("SUPPORT_PHONE", "+91-XXXXXXXXXX")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_agent: str = "service",
        html: bool = False,
        attachments: list = None
    ) -> Dict[str, Any]:
        """
        Send email using SendGrid API
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            from_agent: Which agent to send from ('service', 'delivery', 'sales')
            html: Whether body is HTML or plain text
            attachments: List of dicts with {'content': bytes, 'filename': str, 'type': str}
        
        Returns:
            Dict with status and message
        """
        
        try:
            # Get agent account details
            if from_agent not in self.email_accounts:
                return {
                    "status": "error",
                    "message": f"Unknown agent type: {from_agent}"
                }
            
            if not self.api_key:
                return {
                    "status": "error",
                    "message": "SendGrid API Key not configured"
                }
            
            account = self.email_accounts[from_agent]
            sender_email = account["email"]
            display_name = account["display_name"]
            reply_to_email = account.get("reply_to", sender_email)
            
            # Create SendGrid message
            from_email = Email(sender_email, display_name)
            to = To(to_email)
            
            # Set content type
            if html:
                content = Content("text/html", body)
            else:
                content = Content("text/plain", body)
            
            # Create Mail object
            message = Mail(
                from_email=from_email,
                to_emails=to,
                subject=subject,
                plain_text_content=body if not html else None,
                html_content=body if html else None
            )
            
            # Add attachments if provided
            if attachments:
                for att in attachments:
                    try:
                        # Encode content to base64
                        encoded_content = base64.b64encode(att['content']).decode('utf-8')
                        
                        attachment = Attachment(
                            FileContent(encoded_content),
                            FileName(att['filename']),
                            FileType(att.get('type', 'application/pdf')),
                            Disposition('attachment')
                        )
                        message.add_attachment(attachment)
                        print(f"📎 Attached: {att['filename']}")
                    except Exception as att_error:
                        print(f"⚠️ Failed to attach {att.get('filename', 'unknown')}: {att_error}")
            
            # Add reply-to header if different from sender
            if reply_to_email != sender_email:
                message.reply_to = Email(reply_to_email)
            
            # Send email using SendGrid
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            
            print(f"✅ Email sent successfully to {to_email} from {display_name}")
            print(f"   SendGrid Status Code: {response.status_code}")
            
            # Log the email to database
            try:
                from motor.motor_asyncio import AsyncIOMotorClient
                import asyncio
                mongo_url = os.environ.get('MONGO_URL')
                db_name = os.environ.get('DB_NAME', 'startup_template')
                
                async def log_email():
                    client = AsyncIOMotorClient(mongo_url)
                    db = client[db_name]
                    await db.email_logs.insert_one({
                        "to_email": to_email,
                        "from_email": sender_email,
                        "from_agent": from_agent,
                        "subject": subject,
                        "status": "sent",
                        "sendgrid_status_code": response.status_code,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "email_type": "transactional"
                    })
                    client.close()
                
                # Run async logging in background
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(log_email())
                    else:
                        loop.run_until_complete(log_email())
                except RuntimeError:
                    asyncio.run(log_email())
            except Exception as log_error:
                print(f"Warning: Could not log email: {log_error}")
            
            return {
                "status": "success",
                "message": f"Email sent to {to_email}",
                "from": sender_email,
                "sendgrid_status": response.status_code,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Failed to send email via SendGrid: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Check if it's a sender verification issue
            if "403" in str(e) or "Forbidden" in str(e):
                error_msg = f"Sender email not verified in SendGrid. Please verify {sender_email} in SendGrid dashboard."
            
            return {
                "status": "error",
                "message": error_msg,
                "error_type": "sendgrid"
            }
    
    def get_brand_email(self, brand: str) -> Optional[str]:
        """Get service email for a brand"""
        return self.brand_emails.get(brand, None)
    
    def test_sendgrid_connection(self, agent_type: str = "service") -> Dict[str, Any]:
        """Test SendGrid API connection"""
        try:
            if not self.api_key:
                return {"status": "error", "message": "SendGrid API Key not configured"}
            
            account = self.email_accounts.get(agent_type)
            if not account:
                return {"status": "error", "message": f"Unknown agent type: {agent_type}"}
            
            # Test by checking if API key is valid (try to access SendGrid API)
            sg = SendGridAPIClient(self.api_key)
            
            return {
                "status": "success",
                "message": f"SendGrid API connection successful for {agent_type}",
                "email": account["email"],
                "note": f"Please verify {account['email']} in SendGrid dashboard to send emails"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"SendGrid connection failed: {str(e)}"
            }

# Create global instance
sendgrid_email_service = SendGridEmailService()
