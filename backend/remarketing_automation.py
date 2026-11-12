"""
Remarketing & Retargeting Automation
Automated email campaigns for re-engagement
"""
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

class RemarketingAutomation:
    def __init__(self):
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME', 'startup_template')
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[db_name]
        
        self.sendgrid_key = os.environ.get('SENDGRID_API_KEY')
        self.from_email = os.environ.get('SALES_EMAIL', 'sales.aronline@gmail.com')
    
    async def send_email(self, to_email, subject, html_content):
        """Send email via SendGrid"""
        if not self.sendgrid_key:
            print("⚠️  SendGrid not configured")
            return False
        
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            sg = SendGridAPIClient(self.sendgrid_key)
            response = sg.send(message)
            
            print(f"✅ Email sent to {to_email}: {subject}")
            return response.status_code == 202
            
        except Exception as e:
            print(f"❌ Email error: {str(e)}")
            return False
    
    async def cold_lead_reengagement(self):
        """
        Re-engage leads who haven't been contacted in 30+ days
        """
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Find cold leads
        cold_leads = await self.db.leads.find({
            "status": {"$in": ["new", "contacted", "interested"]},
            "last_contact": {"$lt": thirty_days_ago},
            "email": {"$exists": True, "$ne": None}
        }, {"_id": 0}).to_list(100)
        
        sent_count = 0
        
        for lead in cold_leads:
            email = lead.get('email')
            name = lead.get('name', 'Valued Customer')
            
            subject = f"We miss you, {name}! Here's what's new at Aditya Retail"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2563eb;">We Haven't Heard From You in a While!</h2>
                
                <p>Hi {name},</p>
                
                <p>It's been a month since we last connected. We wanted to reach out and see if you're still interested in premium home appliances from Siemens, Bosch, and Hindware.</p>
                
                <div style="background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #2563eb; margin-top: 0;">What's New This Month:</h3>
                    <ul>
                        <li>New Siemens iQ700 series launched</li>
                        <li>Special festive discounts up to 25% off</li>
                        <li>Free installation on all orders</li>
                        <li>Extended warranty at no extra cost</li>
                    </ul>
                </div>
                
                <p><strong>Still interested?</strong> Reply to this email or call us at +91-XXXXXXXXXX</p>
                
                <p>We're here to help you find the perfect appliance for your home!</p>
                
                <p>Best regards,<br>Aditya Retail Team</p>
            </div>
            """
            
            if await self.send_email(email, subject, html_content):
                # Update last contact date
                await self.db.leads.update_one(
                    {"email": email},
                    {"$set": {"last_contact": datetime.utcnow()}}
                )
                sent_count += 1
        
        print(f"📧 Re-engagement emails sent: {sent_count}")
        return sent_count
    
    async def cart_abandonment_reminder(self):
        """
        Send reminder to users who added items to cart but didn't checkout
        (Placeholder - requires cart tracking implementation)
        """
        # This would work once cart abandonment tracking is implemented
        print("📧 Cart abandonment tracking - coming soon")
        return 0
    
    async def inactive_customer_winback(self):
        """
        Win back customers who haven't purchased in 90+ days
        """
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        
        # Find customers with last order > 90 days ago
        recent_orders = await self.db.orders.find({
            "created_at": {"$gte": ninety_days_ago.isoformat()}
        }, {"_id": 0, "customer_email": 1}).to_list(10000)
        
        recent_customer_emails = set(order.get('customer_email') for order in recent_orders)
        
        # Get all customers
        all_orders = await self.db.orders.find({}, {"_id": 0, "customer_email": 1, "customer_name": 1}).to_list(10000)
        
        inactive_customers = []
        seen_emails = set()
        
        for order in all_orders:
            email = order.get('customer_email')
            if email and email not in recent_customer_emails and email not in seen_emails:
                inactive_customers.append({
                    "email": email,
                    "name": order.get('customer_name', 'Valued Customer')
                })
                seen_emails.add(email)
        
        sent_count = 0
        
        for customer in inactive_customers[:50]:  # Limit to 50 per run
            email = customer['email']
            name = customer['name']
            
            subject = f"{name}, We Want You Back! Exclusive 15% OFF"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0;">We Miss You! 💜</h1>
                </div>
                
                <div style="padding: 30px; background: white;">
                    <p>Dear {name},</p>
                    
                    <p>It's been a while since your last purchase from Aditya Retail, and we'd love to have you back!</p>
                    
                    <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 20px; margin: 20px 0;">
                        <h3 style="color: #92400e; margin-top: 0;">🎁 Exclusive Win-Back Offer</h3>
                        <p style="font-size: 24px; font-weight: bold; color: #92400e; margin: 10px 0;">15% OFF</p>
                        <p style="margin: 0;">on your next purchase</p>
                        <p style="font-size: 12px; color: #78350f; margin-top: 10px;">Valid for 7 days only</p>
                    </div>
                    
                    <h3>Why Shop With Us Again?</h3>
                    <ul>
                        <li>Authorized dealer - 100% genuine products</li>
                        <li>Free installation & demo</li>
                        <li>Extended warranty options</li>
                        <li>24/7 customer support</li>
                    </ul>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="#" style="background: #2563eb; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">
                            SHOP NOW & SAVE 15%
                        </a>
                    </div>
                    
                    <p>Use code: <strong>WELCOME15</strong> at checkout</p>
                    
                    <p>Looking forward to serving you again!</p>
                    
                    <p>Warm regards,<br>Aditya Retail Team</p>
                </div>
            </div>
            """
            
            if await self.send_email(email, subject, html_content):
                sent_count += 1
        
        print(f"📧 Win-back emails sent: {sent_count}")
        return sent_count
    
    async def follow_up_interested_leads(self):
        """
        Follow up with leads who are in 'interested' stage but haven't progressed
        """
        # Get leads who have been "interested" for 7+ days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        stuck_leads = await self.db.leads.find({
            "status": "interested",
            "created_at": {"$lt": seven_days_ago},
            "email": {"$exists": True, "$ne": None}
        }, {"_id": 0}).to_list(100)
        
        sent_count = 0
        
        for lead in stuck_leads:
            email = lead.get('email')
            name = lead.get('name', 'there')
            
            subject = f"{name}, Ready to Move Forward? Let's Help You Decide!"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2563eb;">Still Evaluating Your Options?</h2>
                
                <p>Hi {name},</p>
                
                <p>We noticed you showed interest in our premium appliances about a week ago. We'd love to help you make the best choice!</p>
                
                <div style="background: #f0fdf4; border-left: 4px solid #10b981; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #065f46; margin-top: 0;">🎯 Let Us Help You:</h3>
                    <ul style="color: #065f46;">
                        <li>Free product comparison</li>
                        <li>Expert consultation (no obligation)</li>
                        <li>In-store or virtual demo</li>
                        <li>Special pricing just for you</li>
                    </ul>
                </div>
                
                <h3>What Our Customers Say:</h3>
                <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 15px 0; font-style: italic;">
                    "Aditya Retail helped me choose the perfect refrigerator for my family. The team was patient and knowledgeable!"
                    <div style="text-align: right; margin-top: 10px; font-weight: bold;">- Priya S., Mumbai</div>
                </div>
                
                <p><strong>Ready to take the next step?</strong></p>
                <p>Simply reply to this email or call us at +91-XXXXXXXXXX</p>
                
                <p>Best regards,<br>Your Aditya Retail Advisor</p>
            </div>
            """
            
            if await self.send_email(email, subject, html_content):
                sent_count += 1
        
        print(f"📧 Follow-up emails sent: {sent_count}")
        return sent_count
    
    async def run_all_campaigns(self):
        """Run all remarketing campaigns"""
        print("🚀 Starting remarketing automation...")
        
        results = {
            "cold_leads": await self.cold_lead_reengagement(),
            "inactive_customers": await self.inactive_customer_winback(),
            "interested_leads": await self.follow_up_interested_leads()
        }
        
        print(f"\n✅ Remarketing complete: {sum(results.values())} total emails sent")
        return results

async def main():
    """Main entry point for remarketing automation"""
    automation = RemarketingAutomation()
    return await automation.run_all_campaigns()

if __name__ == "__main__":
    asyncio.run(main())
