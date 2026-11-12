# Email Service for AI Ecommerce Platform
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from jinja2 import Template
import os
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

class EmailService:
    def __init__(self):
        # Gmail SMTP Configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL", "")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")  # Use App Password for Gmail
        self.sender_name = os.getenv("SENDER_NAME", "Aditya Retail")
        
        # Thread pool for async email sending
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def _send_email_sync(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Synchronous email sending function"""
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = to_email
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Add attachments if any
            if attachments:
                for file_path in attachments:
                    if os.path.isfile(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            message.attach(part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, to_email, message.as_string())
            
            return {
                "success": True,
                "message": f"Email sent successfully to {to_email}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Asynchronous email sending"""
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._send_email_sync,
            to_email,
            subject, 
            html_content,
            text_content,
            attachments
        )
    
    def get_order_confirmation_template(self, order_data: Dict[str, Any]) -> str:
        """Generate order confirmation email template"""
        
        template_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Order Confirmation - {{ order_number }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
                .header { text-align: center; margin-bottom: 30px; }
                .logo { font-size: 28px; font-weight: bold; color: #B8441E; }
                .order-info { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .item-row { border-bottom: 1px solid #eee; padding: 10px 0; }
                .total-row { font-weight: bold; font-size: 16px; color: #B8441E; }
                .footer { text-align: center; margin-top: 30px; color: #666; }
                .btn { background: #B8441E; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">Aditya Retail</div>
                    <h2>Order Confirmation</h2>
                    <p>Thank you for your purchase!</p>
                </div>
                
                <div class="order-info">
                    <h3>Order Details</h3>
                    <p><strong>Order Number:</strong> {{ order_number }}</p>
                    <p><strong>Order Date:</strong> {{ order_date }}</p>
                    <p><strong>Payment Method:</strong> {{ payment_method }}</p>
                    <p><strong>Estimated Delivery:</strong> {{ estimated_delivery }}</p>
                </div>
                
                <h3>Items Ordered</h3>
                {% for item in items %}
                <div class="item-row">
                    <strong>{{ item.product_name }}</strong><br>
                    Quantity: {{ item.quantity }} × ₹{{ item.unit_price }} = ₹{{ item.total_price }}
                </div>
                {% endfor %}
                
                <div class="order-info">
                    <div class="item-row">Subtotal: ₹{{ subtotal }}</div>
                    <div class="item-row">Shipping: ₹{{ shipping_cost }}</div>
                    <div class="item-row">Tax: ₹{{ tax_amount }}</div>
                    <div class="item-row total-row">Total: ₹{{ total_amount }}</div>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{{ tracking_url }}" class="btn">Track Your Order</a>
                </div>
                
                <div class="footer">
                    <p>Need help? Contact us at support@adityaretail.com or call +91 80 1234 5678</p>
                    <p>Visit our stores: Malleshwaram & Banaswadi, Bangalore</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        template = Template(template_html)
        return template.render(**order_data)
    
    def get_shipping_update_template(self, tracking_data: Dict[str, Any]) -> str:
        """Generate shipping update email template"""
        
        template_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Shipping Update - {{ order_number }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
                .header { text-align: center; margin-bottom: 30px; }
                .logo { font-size: 28px; font-weight: bold; color: #B8441E; }
                .status-update { background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745; }
                .tracking-info { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .btn { background: #B8441E; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }
                .footer { text-align: center; margin-top: 30px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">Aditya Retail</div>
                    <h2>Shipping Update</h2>
                </div>
                
                <div class="status-update">
                    <h3>{{ status_title }}</h3>
                    <p>{{ status_message }}</p>
                </div>
                
                <div class="tracking-info">
                    <h3>Tracking Information</h3>
                    <p><strong>Order Number:</strong> {{ order_number }}</p>
                    <p><strong>AWB Number:</strong> {{ awb_number }}</p>
                    <p><strong>Courier:</strong> {{ courier_name }}</p>
                    <p><strong>Current Status:</strong> {{ current_status }}</p>
                    {% if expected_delivery %}
                    <p><strong>Expected Delivery:</strong> {{ expected_delivery }}</p>
                    {% endif %}
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{{ tracking_url }}" class="btn">Track Shipment</a>
                </div>
                
                <div class="footer">
                    <p>For any questions, contact us at support@adityaretail.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        template = Template(template_html)
        return template.render(**tracking_data)
    
    def get_service_request_template(self, service_data: Dict[str, Any]) -> str:
        """Generate service request email template"""
        
        template_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Service Request Created - {{ request_id }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
                .header { text-align: center; margin-bottom: 30px; }
                .logo { font-size: 28px; font-weight: bold; color: #B8441E; }
                .service-info { background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107; }
                .footer { text-align: center; margin-top: 30px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">Aditya Retail</div>
                    <h2>Service Request Created</h2>
                </div>
                
                <div class="service-info">
                    <h3>Your service request has been created successfully</h3>
                    <p><strong>Request ID:</strong> {{ request_id }}</p>
                    <p><strong>Product:</strong> {{ product_name }}</p>
                    <p><strong>Issue:</strong> {{ issue_description }}</p>
                    <p><strong>Priority:</strong> {{ priority }}</p>
                    <p><strong>Created:</strong> {{ created_at }}</p>
                </div>
                
                <p>Our technical team will contact you within 24 hours to schedule a service visit.</p>
                <p>You can track the status of your service request using the Request ID provided above.</p>
                
                <div class="footer">
                    <p>For urgent issues, call us at +91 80 1234 5678</p>
                    <p>Email: service@adityaretail.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        template = Template(template_html)
        return template.render(**service_data)
    
    async def send_order_confirmation(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send order confirmation email"""
        
        subject = f"Order Confirmation - {order_data['order_number']}"
        html_content = self.get_order_confirmation_template(order_data)
        
        return await self.send_email(
            to_email=order_data['customer_email'],
            subject=subject,
            html_content=html_content
        )
    
    async def send_shipping_update(self, tracking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send shipping update email"""
        
        subject = f"Shipping Update - {tracking_data['order_number']}"
        html_content = self.get_shipping_update_template(tracking_data)
        
        return await self.send_email(
            to_email=tracking_data['customer_email'],
            subject=subject,
            html_content=html_content
        )
    
    async def send_service_request_confirmation(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send service request confirmation email"""
        
        subject = f"Service Request Created - {service_data['request_id']}"
        html_content = self.get_service_request_template(service_data)
        
        return await self.send_email(
            to_email=service_data['customer_email'],
            subject=subject,
            html_content=html_content
        )

# Notification queue for background processing
class EmailNotificationQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.email_service = EmailService()
    
    async def add_notification(self, notification_data: Dict[str, Any]):
        """Add email notification to queue"""
        await self.queue.put(notification_data)
    
    async def process_queue(self):
        """Process email notifications from queue"""
        while True:
            try:
                notification = await self.queue.get()
                
                notification_type = notification.get("type")
                data = notification.get("data")
                
                if notification_type == "order_confirmation":
                    result = await self.email_service.send_order_confirmation(data)
                elif notification_type == "shipping_update":
                    result = await self.email_service.send_shipping_update(data)
                elif notification_type == "service_request":
                    result = await self.email_service.send_service_request_confirmation(data)
                else:
                    print(f"Unknown notification type: {notification_type}")
                    continue
                
                if result["success"]:
                    print(f"Email sent successfully: {notification_type}")
                else:
                    print(f"Email failed: {notification_type} - {result['error']}")
                
                self.queue.task_done()
                
            except Exception as e:
                print(f"Email queue processing error: {str(e)}")
                await asyncio.sleep(1)

# Initialize services
email_service = EmailService()
email_queue = EmailNotificationQueue()