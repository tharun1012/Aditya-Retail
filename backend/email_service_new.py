"""
Enhanced Email Service for Aditya Retail
Supports multiple email accounts for different agents (Service, Delivery, Sales)
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class EmailServiceNew:
    def __init__(self):
        # SMTP Configuration
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "True") == "True"
        
        # Email accounts for different agents
        self.email_accounts = {
            "service": {
                "email": os.getenv("SERVICE_EMAIL", "service.adityaretail@gmail.com"),
                "password": os.getenv("SERVICE_EMAIL_PASSWORD", ""),
                "display_name": "Aditya Retail Service Team"
            },
            "delivery": {
                "email": os.getenv("DELIVERY_EMAIL", "warehouse.adityaretail@gmail.com"),
                "password": os.getenv("DELIVERY_EMAIL_PASSWORD", ""),
                "display_name": "Aditya Retail Delivery Team"
            },
            "sales": {
                "email": os.getenv("SALES_EMAIL", "online.adityaretail@gmail.com"),
                "password": os.getenv("SALES_EMAIL_PASSWORD", ""),
                "display_name": "Aditya Retail Sales Team"
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
        html: bool = False
    ) -> Dict[str, Any]:
        """
        Send email from specified agent account
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            from_agent: Which agent to send from ('service', 'delivery', 'sales')
            html: Whether body is HTML or plain text
        
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
            
            account = self.email_accounts[from_agent]
            sender_email = account["email"]
            sender_password = account["password"]
            display_name = account["display_name"]
            
            if not sender_password:
                print(f"⚠️ Email password not configured for {from_agent}")
                return {
                    "status": "error",
                    "message": f"Email credentials not configured for {from_agent}"
                }
            
            # Create message
            if html:
                message = MIMEMultipart("alternative")
                text_part = MIMEText(body, "plain")
                html_part = MIMEText(body, "html")
                message.attach(text_part)
                message.attach(html_part)
            else:
                message = MIMEText(body, "plain")
            
            message["Subject"] = subject
            message["From"] = f"{display_name} <{sender_email}>"
            message["To"] = to_email
            message["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
            
            # Create secure SSL context
            context = ssl.create_default_context()
            
            # Connect and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls(context=context)
                
                server.login(sender_email, sender_password)
                server.send_message(message)
            
            print(f"✅ Email sent successfully to {to_email} from {display_name}")
            return {
                "status": "success",
                "message": f"Email sent to {to_email}",
                "from": sender_email,
                "timestamp": datetime.now().isoformat()
            }
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP Authentication failed for {from_agent}: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "error_type": "authentication"
            }
        
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "error_type": "smtp"
            }
        
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "error_type": "general"
            }
    
    def get_brand_email(self, brand: str) -> Optional[str]:
        """Get service email for a brand"""
        return self.brand_emails.get(brand, None)
    
    def test_email_connection(self, agent_type: str = "service") -> Dict[str, Any]:
        """Test email connection for an agent"""
        try:
            account = self.email_accounts.get(agent_type)
            if not account:
                return {"status": "error", "message": f"Unknown agent type: {agent_type}"}
            
            sender_email = account["email"]
            sender_password = account["password"]
            
            if not sender_password:
                return {"status": "error", "message": "Password not configured"}
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls(context=context)
                server.login(sender_email, sender_password)
            
            return {
                "status": "success",
                "message": f"Successfully connected to SMTP server for {agent_type}",
                "email": sender_email
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}"
            }

# Create global instance
email_service_new = EmailServiceNew()
