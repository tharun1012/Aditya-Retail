"""
Comprehensive Email Notification Service for Aditya Retail
Handles all email notifications: Orders, Service Tickets, Delivery, AI Consultation, etc.
"""
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from sendgrid_email_service import sendgrid_email_service

class EmailNotificationService:
    """Centralized email notification service for all business events"""
    
    def __init__(self):
        self.store_name = "Aditya Retail"
        self.store_url = os.environ.get("STORE_URL", "https://adityaretail.com")
        self.support_phone = os.environ.get("SUPPORT_PHONE", "+91-XXXXXXXXXX")
        self.support_email = os.environ.get("SERVICE_EMAIL", "service.adityaretail@gmail.com")
    
    # ============================================
    # ORDER NOTIFICATIONS
    # ============================================
    
    async def send_order_confirmation(
        self,
        customer_email: str,
        customer_name: str,
        order_id: str,
        order_items: List[Dict],
        total_amount: float,
        payment_link: Optional[str] = None,
        shipping_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send order confirmation email to customer"""
        
        # Format order items
        items_html = ""
        for item in order_items:
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{item.get('name', 'Product')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{item.get('quantity', 1)}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">₹{item.get('price', 0):,.2f}</td>
            </tr>
            """
        
        payment_section = ""
        if payment_link:
            payment_section = f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;">
                <p style="color: white; font-size: 16px; margin-bottom: 15px;">Complete your payment securely via PhonePe</p>
                <a href="{payment_link}" style="background: white; color: #667eea; padding: 12px 30px; border-radius: 25px; text-decoration: none; font-weight: bold; display: inline-block;">
                    Pay Now ₹{total_amount:,.2f}
                </a>
            </div>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
        </head>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: #D4AF37; margin: 0; font-size: 28px;">{self.store_name}</h1>
                <p style="color: #ccc; margin-top: 5px;">Premium Home Appliances</p>
            </div>
            
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <h2 style="color: #1a1a2e; margin-top: 0;">Order Confirmation</h2>
                
                <p>Dear {customer_name},</p>
                
                <p>Thank you for your order! We're excited to help you elevate your home experience.</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <p style="margin: 0; color: #666;"><strong>Order ID:</strong> <span style="color: #D4AF37; font-weight: bold;">{order_id}</span></p>
                    <p style="margin: 5px 0 0 0; color: #666;"><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <h3 style="color: #1a1a2e; border-bottom: 2px solid #D4AF37; padding-bottom: 10px;">Order Details</h3>
                
                <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                    <thead>
                        <tr style="background: #1a1a2e; color: white;">
                            <th style="padding: 12px; text-align: left;">Product</th>
                            <th style="padding: 12px; text-align: center;">Qty</th>
                            <th style="padding: 12px; text-align: right;">Price</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                    <tfoot>
                        <tr style="background: #f5f5f5; font-weight: bold;">
                            <td colspan="2" style="padding: 15px; text-align: right;">Total Amount:</td>
                            <td style="padding: 15px; text-align: right; color: #D4AF37; font-size: 18px;">₹{total_amount:,.2f}</td>
                        </tr>
                    </tfoot>
                </table>
                
                {payment_section}
                
                {f'<div style="background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 20px 0;"><strong>Shipping Address:</strong><br>{shipping_address}</div>' if shipping_address else ''}
                
                <div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #e65100;">What's Next?</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #666;">
                        <li>You'll receive a confirmation once your payment is verified</li>
                        <li>Our team will prepare your order for dispatch</li>
                        <li>Track your order in your customer dashboard</li>
                    </ul>
                </div>
                
                <p style="color: #666;">Need help? Contact our AI assistants or call us at <strong>{self.support_phone}</strong></p>
                
                <p>Best regards,<br><strong>Team {self.store_name}</strong></p>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
                <p>© {datetime.now().year} {self.store_name}. All rights reserved.</p>
                <p>Authorized Partner: Bosch | Siemens | Electrolux | Hindware</p>
            </div>
        </body>
        </html>
        """
        
        result = sendgrid_email_service.send_email(
            to_email=customer_email,
            subject=f"Order Confirmed - {order_id} | {self.store_name}",
            body=html_body,
            from_agent="sales",
            html=True
        )
        
        return result
    
    async def send_payment_success(
        self,
        customer_email: str,
        customer_name: str,
        order_id: str,
        transaction_id: str,
        amount: float
    ) -> Dict[str, Any]:
        """Send payment success confirmation"""
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #00c853 0%, #00e676 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <div style="font-size: 50px;">✅</div>
                <h1 style="color: white; margin: 10px 0;">Payment Successful!</h1>
            </div>
            
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p>Dear {customer_name},</p>
                
                <p>Great news! Your payment has been successfully processed.</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <table style="width: 100%;">
                        <tr><td style="color: #666; padding: 5px 0;">Order ID:</td><td style="text-align: right; font-weight: bold;">{order_id}</td></tr>
                        <tr><td style="color: #666; padding: 5px 0;">Transaction ID:</td><td style="text-align: right; font-weight: bold;">{transaction_id}</td></tr>
                        <tr><td style="color: #666; padding: 5px 0;">Amount Paid:</td><td style="text-align: right; font-weight: bold; color: #00c853; font-size: 20px;">₹{amount:,.2f}</td></tr>
                    </table>
                </div>
                
                <p>Your order is now being prepared for dispatch. You'll receive tracking details once shipped.</p>
                
                <p>Thank you for shopping with us!</p>
                
                <p>Best regards,<br><strong>Team {self.store_name}</strong></p>
            </div>
        </body>
        </html>
        """
        
        return sendgrid_email_service.send_email(
            to_email=customer_email,
            subject=f"Payment Confirmed ✅ - Order {order_id} | {self.store_name}",
            body=html_body,
            from_agent="sales",
            html=True
        )
    
    async def send_invoice_email(
        self,
        customer_email: str,
        customer_name: str,
        invoice_number: str,
        invoice_items: List[Dict],
        total_amount: float,
        store_name: str,
        store_address: str,
        store_gst: str,
        invoice_date: str,
        so_number: Optional[str] = None,
        pdf_bytes: bytes = None
    ) -> Dict[str, Any]:
        """Send invoice copy email to customer with optional PDF attachment"""
        
        # Format invoice items
        items_html = ""
        for item in invoice_items:
            item_total = item.get('rate', 0) * item.get('quantity', 1)
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{item.get('product_name', item.get('name', 'Product'))}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{item.get('hsn_code', '-')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{item.get('quantity', 1)}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">₹{item.get('rate', 0):,.0f}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">₹{item_total:,.0f}</td>
            </tr>
            """
        
        so_ref = f"<p><strong>Sales Order Reference:</strong> {so_number}</p>" if so_number else ""
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <div style="font-size: 50px;">📄</div>
                <h1 style="color: white; margin: 10px 0;">TAX INVOICE</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 0;">{invoice_number}</p>
            </div>
            
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p>Dear {customer_name},</p>
                
                <p>Please find your invoice details below. Thank you for your purchase!</p>
                
                {so_ref}
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <div style="border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px;">
                        <strong>From:</strong><br>
                        {store_name}<br>
                        <span style="color: #666; font-size: 13px;">{store_address}</span><br>
                        <span style="color: #666; font-size: 13px;">GSTIN: {store_gst}</span>
                    </div>
                    
                    <p><strong>Invoice Date:</strong> {invoice_date}</p>
                    
                    <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                        <thead>
                            <tr style="background: #f5f5f5;">
                                <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Item</th>
                                <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">HSN</th>
                                <th style="padding: 10px; text-align: center; border-bottom: 2px solid #ddd;">Qty</th>
                                <th style="padding: 10px; text-align: right; border-bottom: 2px solid #ddd;">Rate</th>
                                <th style="padding: 10px; text-align: right; border-bottom: 2px solid #ddd;">Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                        <tfoot>
                            <tr style="background: #e3f2fd;">
                                <td colspan="4" style="padding: 15px; text-align: right; font-weight: bold; font-size: 16px;">Total Amount:</td>
                                <td style="padding: 15px; text-align: right; font-weight: bold; font-size: 18px; color: #1565c0;">₹{total_amount:,.0f}</td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
                
                <p style="color: #666; font-size: 13px;">This is a computer generated invoice. For any queries, please contact our support team.</p>
                
                <p>Best regards,<br><strong>Team {self.store_name}</strong></p>
            </div>
        </body>
        </html>
        """
        
        # Prepare attachments
        attachments = []
        if pdf_bytes:
            attachments.append({
                'content': pdf_bytes,
                'filename': f'{invoice_number}.pdf',
                'type': 'application/pdf'
            })
        
        return sendgrid_email_service.send_email(
            to_email=customer_email,
            subject=f"Invoice {invoice_number} - {self.store_name}",
            body=html_body,
            from_agent="sales",
            html=True,
            attachments=attachments if attachments else None
        )
    
    async def send_delivery_schedule_email(
        self,
        customer_email: str,
        customer_name: str,
        challan_number: str,
        invoice_number: str,
        driver_name: str,
        driver_phone: str,
        vehicle_number: str,
        expected_date: str,
        delivery_address: str
    ) -> Dict[str, Any]:
        """Send delivery schedule notification with driver and vehicle details"""
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <div style="font-size: 50px;">🚚</div>
                <h1 style="color: white; margin: 10px 0;">Delivery Scheduled!</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 0;">Your order is on its way</p>
            </div>
            
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p>Dear {customer_name},</p>
                
                <p>Great news! Your delivery has been scheduled. Here are the details:</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <h3 style="color: #f57c00; margin-top: 0;">📦 Delivery Details</h3>
                    <table style="width: 100%;">
                        <tr><td style="color: #666; padding: 8px 0;">Challan Number:</td><td style="text-align: right; font-weight: bold;">{challan_number}</td></tr>
                        <tr><td style="color: #666; padding: 8px 0;">Invoice Number:</td><td style="text-align: right;">{invoice_number}</td></tr>
                        <tr><td style="color: #666; padding: 8px 0;">Expected Date:</td><td style="text-align: right; font-weight: bold; color: #f57c00;">{expected_date}</td></tr>
                    </table>
                </div>
                
                <div style="background: #e8f5e9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #2e7d32; margin-top: 0;">👤 Driver Information</h3>
                    <table style="width: 100%;">
                        <tr><td style="color: #666; padding: 8px 0;">Driver Name:</td><td style="text-align: right; font-weight: bold;">{driver_name}</td></tr>
                        <tr><td style="color: #666; padding: 8px 0;">Contact Number:</td><td style="text-align: right;"><a href="tel:{driver_phone}" style="color: #2e7d32; text-decoration: none;">{driver_phone}</a></td></tr>
                        <tr><td style="color: #666; padding: 8px 0;">Vehicle Number:</td><td style="text-align: right; font-weight: bold;">{vehicle_number}</td></tr>
                    </table>
                </div>
                
                <div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #e65100;">📍 Delivery Address</h4>
                    <p style="margin: 0; color: #666;">{delivery_address}</p>
                </div>
                
                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #1565c0;">💡 Delivery Tips</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #666;">
                        <li>Keep your phone handy - the driver may call</li>
                        <li>Ensure someone is available to receive the package</li>
                        <li>Please check the items before signing the delivery receipt</li>
                    </ul>
                </div>
                
                <p>Best regards,<br><strong>Delivery Team, {self.store_name}</strong></p>
            </div>
        </body>
        </html>
        """
        
        return sendgrid_email_service.send_email(
            to_email=customer_email,
            subject=f"Delivery Scheduled 🚚 - {challan_number} | {self.store_name}",
            body=html_body,
            from_agent="delivery",
            html=True
        )
    
    # ============================================
    # SERVICE TICKET NOTIFICATIONS
    # ============================================
    
    async def send_service_ticket_confirmation(
        self,
        customer_email: str,
        customer_name: str,
        ticket_number: str,
        issue_description: str,
        product_name: str,
        brand: str,
        priority: str = "Normal"
    ) -> Dict[str, Any]:
        """Send service ticket confirmation to customer"""
        
        brand_email = sendgrid_email_service.get_brand_email(brand) or "brand service team"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: #D4AF37; margin: 0;">{self.store_name}</h1>
                <p style="color: #ccc; margin-top: 5px;">Service Support</p>
            </div>
            
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <h2 style="color: #1a1a2e;">Service Ticket Created</h2>
                
                <p>Dear {customer_name},</p>
                
                <p>We've received your service request and created a ticket for you.</p>
                
                <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2196f3;">
                    <h3 style="margin: 0 0 15px 0; color: #1565c0;">Ticket Details</h3>
                    <table style="width: 100%;">
                        <tr><td style="padding: 5px 0; color: #666;">Ticket Number:</td><td style="font-weight: bold; color: #1565c0;">{ticket_number}</td></tr>
                        <tr><td style="padding: 5px 0; color: #666;">Product:</td><td style="font-weight: bold;">{product_name}</td></tr>
                        <tr><td style="padding: 5px 0; color: #666;">Brand:</td><td style="font-weight: bold;">{brand}</td></tr>
                        <tr><td style="padding: 5px 0; color: #666;">Priority:</td><td style="font-weight: bold;">{priority}</td></tr>
                    </table>
                </div>
                
                <div style="background: white; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <strong>Issue Description:</strong>
                    <p style="margin: 10px 0 0 0; color: #666;">{issue_description}</p>
                </div>
                
                <div style="background: #fff8e1; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #f57c00;">What happens next?</h4>
                    <ol style="margin: 0; padding-left: 20px; color: #666;">
                        <li>Our team will review your request within 24 hours</li>
                        <li>We'll coordinate with {brand} service team</li>
                        <li>A technician will be assigned and contact you</li>
                        <li>You can track status in your customer dashboard</li>
                    </ol>
                </div>
                
                <p style="color: #666;">For urgent issues, call us at <strong>{self.support_phone}</strong></p>
                
                <p>Best regards,<br><strong>Service Team, {self.store_name}</strong></p>
            </div>
        </body>
        </html>
        """
        
        return sendgrid_email_service.send_email(
            to_email=customer_email,
            subject=f"Service Ticket {ticket_number} Created | {self.store_name}",
            body=html_body,
            from_agent="service",
            html=True
        )
    
    async def send_service_ticket_update(
        self,
        customer_email: str,
        customer_name: str,
        ticket_number: str,
        status: str,
        update_message: str
    ) -> Dict[str, Any]:
        """Send service ticket status update"""
        
        status_colors = {
            "In Progress": "#2196f3",
            "Assigned": "#ff9800",
            "Resolved": "#4caf50",
            "Closed": "#9e9e9e"
        }
        status_color = status_colors.get(status, "#2196f3")
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: {status_color}; padding: 25px; text-align: center; border-radius: 10px 10px 0 0;">
                <h2 style="color: white; margin: 0;">Service Ticket Update</h2>
                <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0;">Ticket: {ticket_number}</p>
            </div>
            
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p>Dear {customer_name},</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid {status_color};">
                    <p style="margin: 0;"><strong>Status:</strong> <span style="color: {status_color}; font-weight: bold;">{status}</span></p>
                    <p style="margin: 15px 0 0 0; color: #666;">{update_message}</p>
                </div>
                
                <p>Track your ticket anytime in your customer dashboard.</p>
                
                <p>Best regards,<br><strong>Service Team, {self.store_name}</strong></p>
            </div>
        </body>
        </html>
        """
        
        return sendgrid_email_service.send_email(
            to_email=customer_email,
            subject=f"Ticket {ticket_number} Update: {status} | {self.store_name}",
            body=html_body,
            from_agent="service",
            html=True
        )
    
    # ============================================
    # DELIVERY NOTIFICATIONS
    # ============================================
    
    async def send_delivery_dispatched(
        self,
        customer_email: str,
        customer_name: str,
        order_id: str,
        tracking_number: Optional[str] = None,
        delivery_partner: Optional[str] = None,
        expected_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send order dispatched notification"""
        
        tracking_section = ""
        if tracking_number:
            tracking_section = f"""
            <div style="background: #e8f5e9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h4 style="margin: 0 0 10px 0; color: #2e7d32;">📦 Tracking Information</h4>
                <p style="margin: 5px 0;"><strong>Tracking Number:</strong> {tracking_number}</p>
                {f'<p style="margin: 5px 0;"><strong>Delivery Partner:</strong> {delivery_partner}</p>' if delivery_partner else ''}
                {f'<p style="margin: 5px 0;"><strong>Expected Delivery:</strong> {expected_date}</p>' if expected_date else ''}
            </div>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <div style="font-size: 50px;">🚚</div>
                <h1 style="color: white; margin: 10px 0;">Your Order is On the Way!</h1>
            </div>
            
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p>Dear {customer_name},</p>
                
                <p>Great news! Your order <strong>{order_id}</strong> has been dispatched and is on its way to you.</p>
                
                {tracking_section}
                
                <div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #e65100;">Delivery Tips</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #666;">
                        <li>Keep your phone handy - delivery executive may call</li>
                        <li>Ensure someone is available to receive the package</li>
                        <li>Check the package before accepting</li>
                    </ul>
                </div>
                
                <p>Best regards,<br><strong>Delivery Team, {self.store_name}</strong></p>
            </div>
        </body>
        </html>
        """
        
        return sendgrid_email_service.send_email(
            to_email=customer_email,
            subject=f"Your Order {order_id} is On the Way! 🚚 | {self.store_name}",
            body=html_body,
            from_agent="delivery",
            html=True
        )
    
    async def send_delivery_dispatched_with_invoice(
        self,
        customer_email: str,
        customer_name: str,
        invoice_number: str,
        delivery_person_name: str,
        delivery_person_phone: Optional[str] = None,
        estimated_delivery: Optional[str] = None,
        store_name: Optional[str] = None,
        delivery_address: Optional[str] = None,
        total_amount: float = 0,
        payment_mode: str = "",
        is_cod: bool = False,
        pdf_bytes: bytes = None
    ) -> Dict[str, Any]:
        """Send delivery dispatch notification WITH invoice PDF attachment"""
        
        payment_info = ""
        if is_cod:
            payment_info = f"""
            <div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ff9800;">
                <h4 style="margin: 0 0 10px 0; color: #e65100;">💰 Payment Required at Delivery</h4>
                <p style="margin: 0; color: #666;">Amount to Pay: <strong style="font-size: 18px; color: #e65100;">₹{total_amount:,.0f}</strong></p>
                <p style="margin: 5px 0 0 0; color: #888; font-size: 13px;">Please keep exact amount ready if possible</p>
            </div>
            """
        else:
            payment_info = f"""
            <div style="background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #4caf50;">
                <h4 style="margin: 0 0 5px 0; color: #2e7d32;">✅ Payment Received</h4>
                <p style="margin: 0; color: #666;">Payment Method: {payment_mode.upper()}</p>
            </div>
            """
        
        delivery_details = f"""
        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h3 style="color: #1a1a2e; margin-top: 0; border-bottom: 2px solid #D4AF37; padding-bottom: 10px;">📦 Delivery Details</h3>
            <table style="width: 100%;">
                <tr><td style="padding: 8px 0; color: #666; width: 40%;">Invoice Number:</td><td style="font-weight: bold; color: #1565c0;">{invoice_number}</td></tr>
                <tr><td style="padding: 8px 0; color: #666;">Delivery Person:</td><td style="font-weight: bold;">{delivery_person_name}</td></tr>
                {"<tr><td style='padding: 8px 0; color: #666;'>Contact:</td><td><a href='tel:" + delivery_person_phone + "' style='color: #1565c0; text-decoration: none;'>" + delivery_person_phone + "</a></td></tr>" if delivery_person_phone else ""}
                <tr><td style="padding: 8px 0; color: #666;">Expected Delivery:</td><td style="font-weight: bold; color: #ff9800;">{estimated_delivery or "Today"}</td></tr>
                <tr><td style="padding: 8px 0; color: #666;">Amount:</td><td style="font-weight: bold; font-size: 18px; color: #2e7d32;">₹{total_amount:,.0f}</td></tr>
            </table>
        </div>
        """
        
        address_section = ""
        if delivery_address:
            address_section = f"""
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h4 style="margin: 0 0 10px 0; color: #1565c0;">📍 Delivery Address</h4>
                <p style="margin: 0; color: #666;">{delivery_address}</p>
            </div>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <div style="font-size: 50px;">🚚</div>
                <h1 style="color: white; margin: 10px 0;">Your Order is Out for Delivery!</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 5px 0;">{store_name or self.store_name}</p>
            </div>
            
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p>Dear {customer_name},</p>
                
                <p>Great news! Your order has been dispatched and our delivery person is on the way. Your invoice is attached to this email for your records.</p>
                
                {delivery_details}
                
                {payment_info}
                
                {address_section}
                
                <div style="background: #fce4ec; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #c62828;">📋 Important: Upon Delivery</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #666;">
                        <li>Inspect all items before accepting</li>
                        <li>Sign the "Goods Received" section on the invoice</li>
                        <li>Keep your invoice copy for warranty purposes</li>
                        <li>Report any damage immediately to the delivery person</li>
                    </ul>
                </div>
                
                <p style="color: #666;">Need help? Contact us at <strong>{self.support_phone}</strong></p>
                
                <p>Best regards,<br><strong>Delivery Team, {store_name or self.store_name}</strong></p>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
                <p>© {datetime.now().year} {store_name or self.store_name}. All rights reserved.</p>
                <p style="color: #1565c0;">📎 Invoice PDF attached</p>
            </div>
        </body>
        </html>
        """
        
        # Prepare attachments
        attachments = []
        if pdf_bytes:
            attachments.append({
                'content': pdf_bytes,
                'filename': f'{invoice_number}.pdf',
                'type': 'application/pdf'
            })
        
        return sendgrid_email_service.send_email(
            to_email=customer_email,
            subject=f"Delivery Update: {invoice_number} is Out for Delivery! 🚚 | {store_name or self.store_name}",
            body=html_body,
            from_agent="delivery",
            html=True,
            attachments=attachments if attachments else None
        )
    
    async def send_delivery_completed(
        self,
        customer_email: str,
        customer_name: str,
        order_id: str,
        delivered_at: str
    ) -> Dict[str, Any]:
        """Send delivery completed notification"""
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <div style="font-size: 50px;">✅</div>
                <h1 style="color: white; margin: 10px 0;">Delivered Successfully!</h1>
            </div>
            
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p>Dear {customer_name},</p>
                
                <p>Your order <strong>{order_id}</strong> has been delivered successfully!</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Delivered on:</strong> {delivered_at}</p>
                </div>
                
                <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
                    <p style="margin: 0 0 15px 0; font-size: 16px;">We'd love to hear about your experience!</p>
                    <a href="{self.store_url}/review" style="background: #1976d2; color: white; padding: 12px 30px; border-radius: 25px; text-decoration: none; font-weight: bold;">Leave a Review</a>
                </div>
                
                <p>Need installation or have questions about your product? Our AI assistants are here to help 24/7!</p>
                
                <p>Thank you for choosing {self.store_name}!</p>
                
                <p>Best regards,<br><strong>Team {self.store_name}</strong></p>
            </div>
        </body>
        </html>
        """
        
        return sendgrid_email_service.send_email(
            to_email=customer_email,
            subject=f"Order {order_id} Delivered! ✅ | {self.store_name}",
            body=html_body,
            from_agent="delivery",
            html=True
        )
    
    # ============================================
    # AI CONSULTATION NOTIFICATIONS
    # ============================================
    
    async def send_consultation_report(
        self,
        customer_email: str,
        customer_name: str,
        consultation_id: str,
        recommendations: List[Dict],
        budget_range: str,
        kitchen_size: str
    ) -> Dict[str, Any]:
        """Send AI consultation report to customer"""
        
        recommendations_html = ""
        for i, rec in enumerate(recommendations[:5], 1):
            recommendations_html += f"""
            <div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #D4AF37;">
                <h4 style="margin: 0 0 5px 0; color: #1a1a2e;">{i}. {rec.get('name', 'Product')}</h4>
                <p style="margin: 0; color: #666; font-size: 14px;">{rec.get('brand', '')} | ₹{rec.get('price', 0):,.0f}</p>
                <p style="margin: 5px 0 0 0; color: #888; font-size: 13px;">{rec.get('reason', '')}</p>
            </div>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: #D4AF37; margin: 0;">Your Personalized Kitchen Report</h1>
                <p style="color: #ccc; margin-top: 10px;">AI-Powered Recommendations by {self.store_name}</p>
            </div>
            
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p>Dear {customer_name},</p>
                
                <p>Thank you for using our AI Kitchen Consultant! Based on your requirements, here are our personalized recommendations.</p>
                
                <div style="background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #2e7d32;">📋 Your Requirements</h4>
                    <p style="margin: 5px 0;"><strong>Budget Range:</strong> {budget_range}</p>
                    <p style="margin: 5px 0;"><strong>Kitchen Size:</strong> {kitchen_size}</p>
                    <p style="margin: 5px 0;"><strong>Consultation ID:</strong> {consultation_id}</p>
                </div>
                
                <h3 style="color: #1a1a2e; border-bottom: 2px solid #D4AF37; padding-bottom: 10px;">Top Recommendations</h3>
                
                {recommendations_html}
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; text-align: center; margin: 25px 0;">
                    <p style="color: white; margin: 0 0 15px 0;">Ready to make your kitchen dreams a reality?</p>
                    <a href="{self.store_url}" style="background: white; color: #667eea; padding: 12px 30px; border-radius: 25px; text-decoration: none; font-weight: bold;">Shop Now</a>
                </div>
                
                <p style="color: #666;">Have questions? Chat with our AI Sales Agent or call us at <strong>{self.support_phone}</strong></p>
                
                <p>Best regards,<br><strong>AI Consultant, {self.store_name}</strong></p>
            </div>
        </body>
        </html>
        """
        
        return sendgrid_email_service.send_email(
            to_email=customer_email,
            subject=f"Your Kitchen Consultation Report | {self.store_name}",
            body=html_body,
            from_agent="consultant",
            html=True
        )
    
    # ============================================
    # LEAD CAPTURE & FOLLOW-UP
    # ============================================
    
    async def send_lead_welcome(
        self,
        customer_email: str,
        customer_name: str,
        interested_product: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send welcome email to new lead captured via AI chat"""
        
        product_section = ""
        if interested_product:
            product_section = f"""
            <div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 0;"><strong>You showed interest in:</strong> {interested_product}</p>
                <p style="margin: 10px 0 0 0; color: #666;">Our sales team will reach out with the best offers!</p>
            </div>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: #D4AF37; margin: 0;">{self.store_name}</h1>
                <p style="color: #ccc; margin-top: 5px;">Premium Home Appliances</p>
            </div>
            
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <h2 style="color: #1a1a2e;">Welcome, {customer_name}! 👋</h2>
                
                <p>Thank you for connecting with us! We're thrilled to have you explore our premium collection of home appliances.</p>
                
                {product_section}
                
                <h3 style="color: #1a1a2e;">Why Choose {self.store_name}?</h3>
                <ul style="color: #666;">
                    <li>✅ Authorized dealer for Bosch, Siemens, Electrolux & Hindware</li>
                    <li>✅ 10+ Years of trusted service</li>
                    <li>✅ AI-powered shopping assistance 24/7</li>
                    <li>✅ Professional installation & after-sales support</li>
                </ul>
                
                <div style="background: linear-gradient(135deg, #D4AF37 0%, #c5a028 100%); padding: 20px; border-radius: 10px; text-align: center; margin: 25px 0;">
                    <p style="color: white; margin: 0 0 15px 0; font-size: 16px;">Get personalized recommendations from our AI</p>
                    <a href="{self.store_url}" style="background: white; color: #1a1a2e; padding: 12px 30px; border-radius: 25px; text-decoration: none; font-weight: bold;">Start Shopping</a>
                </div>
                
                <p>Best regards,<br><strong>Team {self.store_name}</strong></p>
            </div>
        </body>
        </html>
        """
        
        return sendgrid_email_service.send_email(
            to_email=customer_email,
            subject=f"Welcome to {self.store_name}! 🏠",
            body=html_body,
            from_agent="sales",
            html=True
        )
    
    # ============================================
    # CUSTOMER ACCOUNT CREATION
    # ============================================
    
    async def send_customer_account_created(
        self,
        customer_email: str,
        customer_name: str,
        temp_password: str,
        invoice_number: str,
        store_name: str,
        set_password_link: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send welcome email when a customer account is auto-created from their first purchase"""
        if set_password_link:
            pw_row = (
                '<tr><td style="padding: 8px 0; color: #666;">Password:</td><td>'
                f'<a href="{set_password_link}" style="background:#1a1a2e;color:#fff;padding:10px 20px;'
                'border-radius:6px;text-decoration:none;font-weight:bold;display:inline-block;">Set your password</a>'
                '<div style="color:#999;font-size:12px;margin-top:6px;">Link works once and expires in 72 hours.</div></td></tr>'
            )
        else:
            pw_row = (
                '<tr><td style="padding: 8px 0; color: #666;">Temporary Password:</td>'
                f'<td style="font-weight: bold; color: #d32f2f; font-family: monospace; font-size: 16px;">{temp_password}</td></tr>'
            )

        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: #D4AF37; margin: 0;">{self.store_name}</h1>
                <p style="color: #ccc; margin-top: 5px;">Your Account is Ready!</p>
            </div>
            
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <h2 style="color: #1a1a2e; margin-top: 0;">Welcome, {customer_name}! 🎉</h2>
                
                <p>Thank you for your purchase (Invoice: <strong>{invoice_number}</strong>)! We've automatically created a customer account for you to make future purchases easier and track your orders.</p>
                
                <div style="background: #e8f5e9; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #4caf50;">
                    <h3 style="color: #2e7d32; margin-top: 0;">Your Login Credentials</h3>
                    <table style="width: 100%;">
                        <tr><td style="padding: 8px 0; color: #666;">Email:</td><td style="font-weight: bold;">{customer_email}</td></tr>
                        {pw_row}
                    </table>
                </div>
                
                <div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #e65100;">🔐 Security Tip</h4>
                    <p style="margin: 0; color: #666;">For your security, please change your password after your first login.</p>
                </div>
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; text-align: center; margin: 25px 0;">
                    <p style="color: white; margin: 0 0 15px 0; font-size: 16px;">Access your customer dashboard</p>
                    <a href="{self.store_url}/login" style="background: white; color: #667eea; padding: 12px 30px; border-radius: 25px; text-decoration: none; font-weight: bold; display: inline-block;">Login Now</a>
                </div>
                
                <h3 style="color: #1a1a2e; border-bottom: 2px solid #D4AF37; padding-bottom: 10px;">What You Can Do</h3>
                <ul style="color: #666; margin: 15px 0;">
                    <li>📦 Track your orders and deliveries</li>
                    <li>📄 Download and access all your invoices</li>
                    <li>🔧 Register your products for warranty</li>
                    <li>🛒 Reorder products with one click</li>
                    <li>🎫 Raise service requests easily</li>
                </ul>
                
                <p style="color: #666;">Need help? Contact us at <strong>{self.support_phone}</strong> or reply to this email.</p>
                
                <p>Best regards,<br><strong>Team {self.store_name}</strong></p>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
                <p>© {datetime.now().year} {self.store_name}. All rights reserved.</p>
                <p style="color: #d32f2f; font-weight: bold;">This email contains your login credentials. Please keep it secure.</p>
            </div>
        </body>
        </html>
        """
        
        return sendgrid_email_service.send_email(
            to_email=customer_email,
            subject=f"Your Account is Ready - {self.store_name} 🎉",
            body=html_body,
            from_agent="sales",
            html=True
        )


# Create global instance
email_notification_service = EmailNotificationService()
