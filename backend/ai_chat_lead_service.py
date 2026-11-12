"""
AI Chat Lead Capture Service
Analyzes conversations to extract contact info and create leads automatically
"""
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from emergentintegrations.llm.chat import LlmChat, UserMessage
import os

class AIChatLeadService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
    
    async def extract_contact_info(self, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract name, email, phone from conversation history
        Uses regex patterns and AI analysis
        """
        
        contact_info = {
            "name": None,
            "email": None,
            "phone": None,
            "has_contact": False
        }
        
        # Combine all user messages
        user_messages = [msg.get('message', '') for msg in conversation_history if msg.get('sender') == 'user']
        full_text = ' '.join(user_messages)
        
        # Extract email using regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_matches = re.findall(email_pattern, full_text)
        if email_matches:
            contact_info['email'] = email_matches[0]
            contact_info['has_contact'] = True
        
        # Extract phone using regex (Indian format - simpler pattern)
        # Match 10-digit Indian mobile numbers starting with 6-9
        phone_pattern = r'\b[6-9]\d{9}\b'
        phone_match = re.search(phone_pattern, full_text)
        if phone_match:
            phone = phone_match.group()
            contact_info['phone'] = f"+91{phone}"
            contact_info['has_contact'] = True
        else:
            # Try with country code
            phone_pattern_with_code = r'(?:\+91|91|0)?[6-9]\d{9}'
            phone_match = re.search(phone_pattern_with_code, full_text)
            if phone_match:
                phone = ''.join(filter(str.isdigit, phone_match.group()))
                if len(phone) == 10:
                    contact_info['phone'] = f"+91{phone}"
                elif len(phone) == 12:
                    contact_info['phone'] = f"+{phone}"
                contact_info['has_contact'] = True
        
        # Extract name using AI (more intelligent)
        if not contact_info['name'] and len(user_messages) > 0:
            try:
                chat = LlmChat(
                    api_key=self.api_key,
                    session_id=f"name_extraction_{datetime.now().timestamp()}",
                    system_message="You extract customer names from conversations. Return ONLY the name, nothing else. If no name found, return 'NONE'."
                ).with_model("openai", "gpt-4o-mini")
                
                prompt = f"Extract the customer's name from this conversation:\n{full_text}\n\nReturn only the name or NONE."
                response = await chat.send_message(UserMessage(text=prompt))
                
                name = response.strip()
                if name and name != 'NONE' and len(name.split()) <= 4:
                    contact_info['name'] = name
                    contact_info['has_contact'] = True
            except Exception as e:
                print(f"Error extracting name: {e}")
        
        return contact_info
    
    async def analyze_conversation_intent(self, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze conversation to extract:
        - Product interests
        - Budget mentioned
        - Buying timeline
        - Key concerns
        """
        
        try:
            user_messages = [msg.get('message', '') for msg in conversation_history if msg.get('sender') == 'user']
            ai_messages = [msg.get('message', '') for msg in conversation_history if msg.get('sender') == 'ai']
            
            conversation_text = "\n".join([f"Customer: {msg}" for msg in user_messages[-10:]])  # Last 10 messages
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"intent_analysis_{datetime.now().timestamp()}",
                system_message="You analyze customer conversations to extract buying intent and product interests."
            ).with_model("openai", "gpt-4o-mini")
            
            prompt = f"""Analyze this customer conversation and extract information in JSON format:

Conversation:
{conversation_text}

Return ONLY valid JSON with these fields:
{{
    "interested_products": ["list of products mentioned"],
    "budget_range": "budget if mentioned, else null",
    "buying_timeline": "immediate/this_week/this_month/exploring",
    "key_concerns": ["list of questions or concerns"],
    "conversation_summary": "2-3 line summary of what customer wants"
}}"""
            
            response = await chat.send_message(UserMessage(text=prompt))
            
            # Extract JSON from response
            import json
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                analysis = json.loads(json_str)
                return analysis
            
            return {
                "interested_products": [],
                "budget_range": None,
                "buying_timeline": "exploring",
                "key_concerns": [],
                "conversation_summary": "Customer inquiry about home appliances"
            }
            
        except Exception as e:
            print(f"Error analyzing conversation: {e}")
            return {
                "interested_products": [],
                "budget_range": None,
                "buying_timeline": "exploring",
                "key_concerns": [],
                "conversation_summary": "Customer inquiry"
            }
    
    async def create_lead_from_chat(
        self, 
        contact_info: Dict[str, Any],
        conversation_analysis: Dict[str, Any],
        session_id: str,
        db
    ) -> Optional[str]:
        """
        Create lead in database from chat conversation
        Now creates leads even without contact info for high-intent visitors
        """
        
        try:
            # Check if lead already exists for this session
            existing_lead = await db.leads.find_one({"ai_chat_session_id": session_id})
            
            if existing_lead:
                # Update existing lead with new info
                update_fields = {
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                
                if contact_info.get('name') and (not existing_lead.get('name') or existing_lead.get('name') == 'AI Chat Visitor'):
                    update_fields['name'] = contact_info['name']
                if contact_info.get('email') and not existing_lead.get('email'):
                    update_fields['email'] = contact_info['email']
                    update_fields['status'] = 'warm'  # Upgrade status when we get email
                if contact_info.get('phone') and not existing_lead.get('phone'):
                    update_fields['phone'] = contact_info['phone']
                    update_fields['status'] = 'hot'  # Hot lead when we get phone
                
                # Update conversation analysis
                if conversation_analysis.get('interested_products'):
                    update_fields['interested_products'] = conversation_analysis['interested_products']
                if conversation_analysis.get('budget_range'):
                    update_fields['budget_range'] = conversation_analysis['budget_range']
                if conversation_analysis.get('conversation_summary'):
                    update_fields['notes'] = conversation_analysis['conversation_summary']
                if conversation_analysis.get('buying_timeline'):
                    update_fields['buying_timeline'] = conversation_analysis['buying_timeline']
                
                await db.leads.update_one(
                    {"id": existing_lead['id']},
                    {"$set": update_fields}
                )
                print(f"✅ Updated existing lead {existing_lead['id']} with new info")
                
                return existing_lead['id']
            
            # Create new lead
            lead_id = str(uuid.uuid4())
            
            # Determine initial lead status based on contact info
            initial_status = "new"
            if contact_info.get('phone'):
                initial_status = "hot"  # Phone = hot lead
            elif contact_info.get('email'):
                initial_status = "warm"  # Email only = warm lead
            elif conversation_analysis.get('buying_timeline') in ['immediate', 'this_week']:
                initial_status = "warm"  # High intent but no contact
            
            lead = {
                "id": lead_id,
                "name": contact_info.get('name', 'AI Chat Visitor'),
                "email": contact_info.get('email'),
                "phone": contact_info.get('phone'),
                "source": "ai_chat_website",
                "status": initial_status,
                "has_contact_info": contact_info.get('has_contact', False),
                "interested_products": conversation_analysis.get('interested_products', []),
                "notes": conversation_analysis.get('conversation_summary', 'Customer inquiry from AI chat'),
                "ai_agent_interaction": f"Budget: {conversation_analysis.get('budget_range', 'Not mentioned')}. Timeline: {conversation_analysis.get('buying_timeline', 'Unknown')}. Concerns: {', '.join(conversation_analysis.get('key_concerns', []))}",
                "expected_value": self._estimate_deal_value(conversation_analysis),
                "assigned_to": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "last_contact_date": datetime.now(timezone.utc).isoformat(),
                "next_follow_up": None,
                "interactions": [{
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "type": "ai_chat",
                    "agent": "sales",
                    "content": conversation_analysis.get('conversation_summary', 'AI chat conversation')
                }],
                "follow_ups": [],
                "email_sequence_status": "pending" if contact_info.get('email') else "no_email",
                "emails_sent": [],
                "ai_chat_session_id": session_id,
                "buying_timeline": conversation_analysis.get('buying_timeline', 'exploring'),
                "budget_range": conversation_analysis.get('budget_range'),
                "key_concerns": conversation_analysis.get('key_concerns', [])
            }
            
            await db.leads.insert_one(lead)
            print(f"✅ Created new lead from AI chat: {lead_id} - {contact_info.get('name', 'Visitor')} (Status: {initial_status})")

            # Notify CRM inbox (only if we have contact info; skip anonymous visitors)
            if contact_info.get('email') or contact_info.get('phone'):
                try:
                    from crm_lead_notifier import notify_new_lead
                    notify_new_lead(
                        lead,
                        source="sales",
                        extra={
                            "summary": conversation_analysis.get('conversation_summary'),
                            "conversation_excerpt": conversation_analysis.get('conversation_summary'),
                        },
                    )
                except Exception as _e:
                    print(f"CRM notify (sales chat) failed: {_e}")

            # Send personalized welcome email if email captured
            if contact_info.get('email'):
                await self.send_chat_welcome_email(lead, conversation_analysis, db)

            return lead_id
            
        except Exception as e:
            print(f"❌ Error creating lead from chat: {e}")
            return None
    
    def _estimate_deal_value(self, conversation_analysis: Dict[str, Any]) -> float:
        """Estimate potential deal value based on conversation"""
        budget = conversation_analysis.get('budget_range')
        if not budget:
            return 50000  # Default estimate
        
        # Try to extract numeric value from budget string
        import re
        numbers = re.findall(r'[\d,]+', str(budget))
        if numbers:
            try:
                # Take the highest number mentioned
                values = [int(n.replace(',', '')) for n in numbers]
                return max(values) if values else 50000
            except Exception:
                pass
        
        return 50000
    
    async def send_chat_welcome_email(
        self,
        lead: Dict[str, Any],
        conversation_analysis: Dict[str, Any],
        db
    ):
        """
        Send personalized welcome email with products discussed in chat
        """
        
        try:
            from sendgrid_email_service import sendgrid_email_service
            
            email = lead.get('email')
            if not email:
                return
            
            name = lead.get('name', 'Valued Customer')
            first_name = name.split()[0] if name != 'AI Chat Visitor' else 'there'
            interested_products = conversation_analysis.get('interested_products', [])
            budget = conversation_analysis.get('budget_range', 'Not specified')
            
            # Build products section
            products_section = ""
            if interested_products:
                products_section = "\n\n🛍️ PRODUCTS YOU WERE INTERESTED IN:\n"
                for idx, product in enumerate(interested_products[:3], 1):
                    products_section += f"{idx}. {product}\n"
            
            subject = f"Hi {first_name}, Thank You for Chatting with Rohit! 🙏"
            
            body = f"""Hi {first_name},

Thank you for connecting with me on Aditya Retail's website! I really enjoyed our conversation.
{products_section}

📋 QUICK SUMMARY OF OUR CHAT:
{conversation_analysis.get('conversation_summary', 'We discussed your home appliance needs')}

💰 Budget Range: {budget}
⏰ Timeline: {conversation_analysis.get('buying_timeline', 'Exploring options')}

🎁 EXCLUSIVE OFFERS FOR YOU:
• 15% OFF on orders above ₹1,00,000
• FREE Installation & Demo (Worth ₹2,000)
• 2-Year Extended Warranty on Bosch & Siemens
• 0% EMI available on all credit cards

🏆 WHY CHOOSE ADITYA RETAIL:
✅ Authorized Dealer - Bosch, Siemens & Hindware
✅ 10,000+ Happy Customers in Bangalore
✅ Same Day Delivery Available
✅ Expert Guidance & Lifetime Support

📞 NEXT STEPS - LET'S CONTINUE:
I'm here to help you make the perfect choice!

📱 Call/WhatsApp: +91-9844577440 (Rohit)
📧 Email: service.adityaretail@gmail.com
🌐 Browse Catalog: https://adityaretail.com

💬 You can also continue our chat anytime on the website!

Have questions? Just reply to this email - I read every message personally!

Looking forward to helping you!

Warm Regards,
Rohit Upadhyaya
Sales Consultant
Aditya Retail

📍 Visit Our Stores:
🏪 Banaswadi Store - No.5AC, 927, 5th 'A' Cross, HRBR Layout I Block, Kalyanagar
🏪 Bosch Brand Store - [Address]
🏪 Dasarahalli Store - [Address]

⏰ Store Hours: Mon-Sat, 10 AM - 8 PM
"""
            
            result = sendgrid_email_service.send_email(
                to_email=email,
                subject=subject,
                body=body,
                from_agent="sales",
                html=False
            )
            
            if result.get('status') == 'success':
                await db.leads.update_one(
                    {"id": lead['id']},
                    {
                        "$push": {
                            "emails_sent": {
                                "type": "chat_welcome",
                                "sent_at": datetime.now(timezone.utc).isoformat(),
                                "status": "sent"
                            }
                        },
                        "$set": {
                            "email_sequence_status": "active",
                            "status": "contacted"
                        }
                    }
                )
                print(f"✅ Chat welcome email sent to {email}")
            
        except Exception as e:
            print(f"❌ Error sending chat welcome email: {e}")

# Global instance
ai_chat_lead_service = AIChatLeadService()
