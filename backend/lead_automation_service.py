"""
AI-Powered Lead Automation Service
Handles automated email follow-ups, lead scoring, and escalation
"""
import os
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from sendgrid_email_service import sendgrid_email_service
from emergentintegrations.llm.chat import LlmChat, UserMessage

class LeadAutomationService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        
    async def auto_create_lead_from_chat(
        self,
        conversation_data: Dict[str, Any],
        db
    ) -> Optional[str]:
        """
        Automatically create lead from AI chat conversation
        Extracts contact info and buying signals from conversation
        """
        try:
            # Analyze conversation for contact info and intent
            analysis = await self._analyze_conversation(conversation_data)
            
            if not analysis.get('has_contact_info'):
                return None
            
            import uuid
            lead_id = str(uuid.uuid4())
            
            lead = {
                "id": lead_id,
                "name": analysis.get('name', 'Website Visitor'),
                "email": analysis.get('email'),
                "phone": analysis.get('phone'),
                "source": "ai_chat",
                "status": analysis.get('initial_status', 'new'),
                "interested_products": analysis.get('interested_products', []),
                "notes": analysis.get('conversation_summary'),
                "ai_agent_interaction": conversation_data.get('full_conversation'),
                "expected_value": analysis.get('estimated_budget', 0),
                "lead_score": analysis.get('score', 0),
                "assigned_to": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "last_contact_date": datetime.now(timezone.utc).isoformat(),
                "next_follow_up": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
                "interactions": [{
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "type": "ai_chat",
                    "agent": conversation_data.get('agent_type', 'sales'),
                    "content": conversation_data.get('summary', 'Initial AI chat conversation')
                }],
                "follow_ups": [],
                "email_sequence_status": "pending",
                "emails_sent": []
            }
            
            await db.leads.insert_one(lead)
            
            # Send welcome email immediately
            if lead.get('email'):
                await self.send_welcome_email(lead, db)
            
            return lead_id
            
        except Exception as e:
            print(f"Error auto-creating lead: {e}")
            return None
    
    async def _analyze_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use AI to analyze conversation and extract:
        - Contact information (email, phone, name)
        - Buying intent (budget, timeline, urgency)
        - Interested products
        - Lead score (Hot/Warm/Cold)
        """
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"lead_analysis_{datetime.now().timestamp()}",
                system_message="You are a lead analysis assistant. Extract contact information and buying intent from conversations."
            ).with_model("openai", "gpt-4o-mini")
            
            prompt = f"""Analyze this customer conversation and extract lead information:

Conversation:
{conversation_data.get('full_conversation', '')}

Extract and return in JSON format:
{{
    "has_contact_info": true/false,
    "name": "customer name if mentioned",
    "email": "email if provided",
    "phone": "phone if provided",
    "interested_products": ["list of products mentioned"],
    "estimated_budget": estimated budget in rupees,
    "urgency": "high/medium/low",
    "buying_timeline": "immediate/this_week/this_month/long_term",
    "initial_status": "hot/warm/cold/new",
    "score": score from 0-100,
    "conversation_summary": "brief 2-3 line summary",
    "buying_signals": ["list of positive signals"]
}}

Scoring criteria:
- Budget mentioned: +20 points
- Specific product interest: +15 points
- Ready to buy: +25 points
- Price inquiry: +10 points
- Just browsing: -10 points
- Hot (80-100): Ready to buy, budget clear, urgent
- Warm (50-79): Interested, needs nurturing
- Cold (0-49): Just exploring, long timeline

Return ONLY valid JSON, no other text."""

            response = await chat.send_message(UserMessage(text=prompt))
            
            # Parse JSON response
            import json
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                analysis = json.loads(json_str)
                return analysis
            
            return {"has_contact_info": False}
            
        except Exception as e:
            print(f"Error analyzing conversation: {e}")
            return {"has_contact_info": False}
    
    async def send_welcome_email(self, lead: Dict[str, Any], db):
        """Send immediate AI-personalized welcome email to new lead"""
        try:
            email = lead.get('email')
            if not email:
                return
            
            name = lead.get('name', 'Valued Customer')
            first_name = name.split()[0]
            notes = lead.get('notes', '')
            interested_products = lead.get('interested_products', [])
            
            # Get personalized product recommendations
            recommendations = await self._get_product_recommendations(notes, interested_products, db)
            
            subject = f"Hi {first_name}, Perfect Home Appliances Just for You! 🏡"
            
            # Build personalized product section
            products_html = ""
            if recommendations:
                products_html = "\n\n🎯 BASED ON YOUR INTEREST, WE RECOMMEND:\n\n"
                for idx, product in enumerate(recommendations[:3], 1):
                    products_html += f"""{idx}. {product['name']} - {product['brand']}
   💰 Price: ₹{product['price']:,}
   ✨ {product['highlight']}
   🔗 View: https://adityaretail.com
   
"""
            
            # Build personalized message based on notes
            personal_note = ""
            if notes:
                personal_note = f"\nI noticed you're interested in {notes.lower()}. "
            
            body = f"""Hi {first_name},

Thank you for reaching out to Aditya Retail! I'm excited to help you find exactly what you need.
{personal_note}
{products_html}
🎁 SPECIAL OFFERS RUNNING NOW:
• 15% OFF on orders above ₹1,00,000
• FREE Installation & Demo (Worth ₹2,000)
• 2-Year Extended Warranty on Bosch & Siemens
• 0% EMI available on credit cards

🏆 WHY CUSTOMERS CHOOSE US:
✅ Authorized Dealer - Bosch, Siemens & Hindware
✅ 10,000+ Happy Customers Across Bangalore
✅ Same Day Delivery Available
✅ Expert Guidance & After-Sales Support

📞 LET'S TALK! I'm here to help personally:
   Call/WhatsApp: +91-9844577440
   Email: service.adityaretail@gmail.com
   
🌐 Explore Full Catalog: https://adityaretail.com

💬 Got Questions? 
   Simply reply to this email - I read every message personally!
   Or chat with our AI assistant on our website 24/7

Looking forward to helping you create your perfect home!

Warm Regards,
Rohit Upadhyaya
Sales Manager
Aditya Retail

📍 Showroom: JP Nagar, Bangalore
⏰ Visit Us: Mon-Sat, 10 AM - 8 PM
"""
            
            result = sendgrid_email_service.send_email(
                to_email=email,
                subject=subject,
                body=body,
                from_agent="sales",
                html=False
            )
            
            # Log email sent and UPDATE STATUS to "contacted"
            if result.get('status') == 'success':
                await db.leads.update_one(
                    {"id": lead['id']},
                    {
                        "$push": {
                            "emails_sent": {
                                "type": "welcome",
                                "sent_at": datetime.now(timezone.utc).isoformat(),
                                "status": "sent"
                            }
                        },
                        "$set": {
                            "email_sequence_status": "active",
                            "status": "contacted",  # ✅ UPDATE STATUS
                            "last_contact_date": datetime.now(timezone.utc).isoformat(),
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                print(f"✅ Welcome email sent to {email} - Status updated to 'contacted'")
            
        except Exception as e:
            print(f"Error sending welcome email: {e}")
    
    async def _get_product_recommendations(
        self, 
        notes: str, 
        interested_products: List[str], 
        db
    ) -> List[Dict[str, Any]]:
        """Get AI-powered product recommendations based on lead notes"""
        try:
            # Fetch products from database
            products = await db.products.find({}, {"_id": 0}).to_list(200)
            
            if not products:
                return []
            
            # If no notes or interests, return top 3 popular products
            if not notes and not interested_products:
                return products[:3]
            
            # Use AI to find best matching products
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"product_rec_{datetime.now().timestamp()}",
                system_message="You are a product recommendation assistant. Your job is to match customer needs with the best products."
            ).with_model("openai", "gpt-4o-mini")
            
            products_summary = "\n".join([
                f"{p.get('id')}: {p.get('name')} - {p.get('brand')} - ₹{p.get('price')} - {p.get('category')}"
                for p in products[:50]  # First 50 products for faster processing
            ])
            
            prompt = f"""Based on customer interest: "{notes} {' '.join(interested_products)}"

Find the 3 BEST MATCHING products from this list:
{products_summary}

Return ONLY product IDs as comma-separated values (e.g., "BOSCH001,SIE002,HIN003")
Focus on: budget mentioned, category, brand preference, features needed."""

            response = await chat.send_message(UserMessage(text=prompt))
            
            # Extract product IDs
            recommended_ids = [pid.strip() for pid in response.replace('\n', '').split(',')]
            
            # Get full product details
            recommendations = []
            for product in products:
                if product.get('id') in recommended_ids and len(recommendations) < 3:
                    recommendations.append({
                        'name': product.get('name'),
                        'brand': product.get('brand'),
                        'price': product.get('price'),
                        'category': product.get('category'),
                        'highlight': product.get('ai_features', [None])[0] or product.get('features', [None])[0] or 'Premium quality'
                    })
            
            # Fallback to top products if AI didn't match
            if not recommendations:
                recommendations = [
                    {
                        'name': p.get('name'),
                        'brand': p.get('brand'),
                        'price': p.get('price'),
                        'category': p.get('category'),
                        'highlight': p.get('ai_features', [None])[0] or 'Premium quality'
                    }
                    for p in products[:3]
                ]
            
            return recommendations
            
        except Exception as e:
            print(f"Error getting product recommendations: {e}")
            return []
    
    async def send_follow_up_email(self, lead: Dict[str, Any], follow_up_type: str, db):
        """Send automated follow-up emails"""
        try:
            email = lead.get('email')
            if not email:
                return
            
            name = lead.get('name', 'Valued Customer')
            first_name = name.split()[0]
            
            emails = {
                "day2": {
                    "subject": f"Still thinking about the perfect appliance, {first_name}?",
                    "body": f"""Hi {first_name},

We hope you're doing well!

We noticed you were interested in our premium home appliances. We'd love to help you make the perfect choice for your home.

🤔 Have any questions? Our team is ready to assist:
• Product comparisons and recommendations
• Installation and warranty details  
• Pricing and special offers

💰 Special offer: Get up to 15% off on orders above ₹1,00,000

📱 Quick ways to reach us:
• Reply to this email
• Call: +91-XXXXXXXXXX
• Chat on website: https://adityaretail.com

Looking forward to helping you!

Best regards,
Aditya Retail Team
"""
                },
                "day4": {
                    "subject": f"⭐ Why our customers love us - Real reviews",
                    "body": f"""Hi {first_name},

See what our happy customers are saying:

⭐⭐⭐⭐⭐ "Best appliances and excellent service!"
⭐⭐⭐⭐⭐ "Installation was seamless and professional"
⭐⭐⭐⭐⭐ "Great quality, worth every rupee"

✅ What makes us different:
• Genuine products with manufacturer warranty
• Free installation by certified technicians
• Lifetime support and guidance
• Easy returns and exchanges

🎁 Plus: 2-year warranty on all products!

Ready to experience the difference?
👉 Shop now: https://adityaretail.com

Questions? Just hit reply!

Warm regards,
Aditya Retail Team
"""
                },
                "day7": {
                    "subject": f"🔥 Limited time: Special discount for {first_name}!",
                    "body": f"""Hi {first_name},

Great news! We have a special offer just for you:

🎉 EXCLUSIVE DISCOUNT
Save ₹5,000 on your purchase!

Offer valid only till: {(datetime.now() + timedelta(days=3)).strftime('%d %B %Y')}

✨ Your benefits:
💰 ₹5,000 instant discount
🚚 Free delivery
🔧 Free installation
📞 Priority customer support

Don't miss out on this limited-time offer!

👉 Shop now: https://adityaretail.com
Use code: ADITYA5000

Need help choosing? Call us at +91-XXXXXXXXXX

Hurry, offer ending soon!

Best regards,
Aditya Retail Team
"""
                }
            }
            
            email_config = emails.get(follow_up_type)
            if not email_config:
                return
            
            result = sendgrid_email_service.send_email(
                to_email=email,
                subject=email_config['subject'],
                body=email_config['body'],
                from_agent="sales",
                html=False
            )
            
            # Log email sent
            if result.get('status') == 'success':
                await db.leads.update_one(
                    {"id": lead['id']},
                    {
                        "$push": {
                            "emails_sent": {
                                "type": follow_up_type,
                                "sent_at": datetime.now(timezone.utc).isoformat(),
                                "status": "sent"
                            }
                        },
                        "$set": {
                            "last_contact_date": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                print(f"✅ {follow_up_type} email sent to {email}")
            
        except Exception as e:
            print(f"Error sending follow-up email: {e}")
    
    async def score_lead(self, lead: Dict[str, Any]) -> int:
        """
        Calculate lead score based on:
        - Interaction history
        - Email engagement
        - Conversation analysis
        - Time since last contact
        """
        score = 0
        
        # Base score from initial analysis
        score += lead.get('lead_score', 0)
        
        # Email engagement
        emails_sent = lead.get('emails_sent', [])
        if len(emails_sent) > 0:
            # Engagement bonus (would track opens/clicks with SendGrid webhooks)
            score += len(emails_sent) * 5
        
        # Recent interaction bonus
        last_contact = lead.get('last_contact_date')
        if last_contact:
            try:
                last_contact_dt = datetime.fromisoformat(last_contact.replace('Z', '+00:00'))
                days_since = (datetime.now(timezone.utc) - last_contact_dt).days
                if days_since <= 2:
                    score += 10
                elif days_since <= 7:
                    score += 5
            except Exception:
                pass
        
        # Multiple interactions
        interactions = lead.get('interactions', [])
        score += min(len(interactions) * 5, 20)
        
        # Has budget
        if lead.get('expected_value', 0) > 0:
            score += 15
        
        # Cap score at 100
        return min(score, 100)
    
    async def update_lead_status_by_score(self, lead_id: str, db):
        """Update lead status based on score"""
        try:
            lead = await db.leads.find_one({"id": lead_id})
            if not lead:
                return
            
            score = await self.score_lead(lead)
            
            # Determine status
            if score >= 80:
                status = "hot"
            elif score >= 50:
                status = "warm"
            elif score >= 30:
                status = "contacted"
            else:
                status = "cold"
            
            await db.leads.update_one(
                {"id": lead_id},
                {
                    "$set": {
                        "status": status,
                        "lead_score": score,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            print(f"✅ Lead {lead_id} updated: Score={score}, Status={status}")
            
        except Exception as e:
            print(f"Error updating lead status: {e}")
    
    async def check_and_escalate_hot_leads(self, db) -> list:
        """Check for hot leads that need human attention"""
        try:
            # Find hot leads that haven't been escalated
            hot_leads = await db.leads.find({
                "status": "hot",
                "escalated": {"$ne": True}
            }).to_list(50)
            
            escalations = []
            
            for lead in hot_leads:
                # Mark as escalated
                await db.leads.update_one(
                    {"id": lead['id']},
                    {
                        "$set": {
                            "escalated": True,
                            "escalated_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                
                escalations.append({
                    "lead_id": lead['id'],
                    "name": lead.get('name'),
                    "email": lead.get('email'),
                    "phone": lead.get('phone'),
                    "score": lead.get('lead_score', 0),
                    "interested_products": lead.get('interested_products', []),
                    "notes": lead.get('notes', ''),
                    "message": f"🔥 HOT LEAD ALERT: {lead.get('name')} is ready for human contact!"
                })
            
            return escalations
            
        except Exception as e:
            print(f"Error checking hot leads: {e}")
            return []

# Global instance
lead_automation = LeadAutomationService()
