import os
import uuid
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
import asyncio
import json
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

class AIAgentManager:
    """Manages all AI agents for the ecommerce platform - Enhanced with real-time data and lead management"""
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
        
        # Initialize MongoDB connection
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'startup_template')
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[db_name]
    
    # ================== REAL-TIME DATA FETCHERS ==================
    
    async def _fetch_leads_summary(self) -> Dict[str, Any]:
        """Fetch leads and conversion data for Sales Agent"""
        try:
            # Get recent leads
            leads = await self.db.leads.find(
                {"created_at": {"$gte": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()}},
                {"_id": 0}
            ).sort("created_at", -1).limit(50).to_list(50)
            
            # Get conversion stats
            total_leads = await self.db.leads.count_documents({})
            converted_leads = await self.db.leads.count_documents({"status": "converted"})
            hot_leads = await self.db.leads.count_documents({"status": "hot"})
            
            return {
                "total_leads": total_leads,
                "converted_leads": converted_leads,
                "hot_leads": hot_leads,
                "conversion_rate": round((converted_leads / total_leads * 100) if total_leads > 0 else 0, 1),
                "recent_leads": leads[:10]
            }
        except Exception as e:
            print(f"Error fetching leads: {e}")
            return {"total_leads": 0, "converted_leads": 0, "hot_leads": 0, "conversion_rate": 0, "recent_leads": []}
    
    async def _fetch_service_context(self, customer_phone: str = None, customer_email: str = None) -> Dict[str, Any]:
        """Fetch service tickets, customer history, and registered products"""
        try:
            context = {
                "open_tickets": 0,
                "resolved_tickets": 0,
                "customer_history": [],
                "registered_products": [],
                "recent_tickets": []
            }
            
            # Get overall ticket stats
            context["open_tickets"] = await self.db.service_tickets.count_documents(
                {"status": {"$in": ["open", "in_progress", "pending"]}}
            )
            context["resolved_tickets"] = await self.db.service_tickets.count_documents(
                {"status": "resolved"}
            )
            
            # If we have customer info, fetch their specific history
            if customer_phone or customer_email:
                query = {}
                if customer_phone:
                    query["$or"] = [{"phone": customer_phone}, {"customer_phone": customer_phone}]
                if customer_email:
                    if "$or" in query:
                        query["$or"].extend([{"email": customer_email}, {"customer_email": customer_email}])
                    else:
                        query["$or"] = [{"email": customer_email}, {"customer_email": customer_email}]
                
                # Get customer's past tickets
                past_tickets = await self.db.service_tickets.find(
                    query, {"_id": 0}
                ).sort("created_at", -1).limit(5).to_list(5)
                context["customer_history"] = past_tickets
                
                # Get customer's registered products
                if customer_email:
                    products = await self.db.registered_products.find(
                        {"customer_email": customer_email}, {"_id": 0}
                    ).to_list(20)
                    context["registered_products"] = products
            
            # Get recent tickets for context
            recent = await self.db.service_tickets.find(
                {}, {"_id": 0}
            ).sort("created_at", -1).limit(10).to_list(10)
            context["recent_tickets"] = recent
            
            return context
        except Exception as e:
            print(f"Error fetching service context: {e}")
            return {"open_tickets": 0, "resolved_tickets": 0, "customer_history": [], "registered_products": [], "recent_tickets": []}
    
    async def _fetch_delivery_context(self, order_id: str = None, customer_phone: str = None) -> Dict[str, Any]:
        """Fetch delivery status, pending deliveries, and order tracking"""
        try:
            context = {
                "pending_deliveries": 0,
                "out_for_delivery": 0,
                "delivered_today": 0,
                "customer_orders": [],
                "specific_order": None
            }
            
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            
            # Get delivery stats
            context["pending_deliveries"] = await self.db.offline_invoices.count_documents(
                {"status": "ready_for_delivery", "document_type": "invoice"}
            )
            context["out_for_delivery"] = await self.db.offline_invoices.count_documents(
                {"status": "out_for_delivery"}
            )
            context["delivered_today"] = await self.db.offline_invoices.count_documents({
                "status": "delivered",
                "delivered_at": {"$regex": f"^{today}"}
            })
            
            # If customer phone provided, get their orders
            if customer_phone:
                orders = await self.db.offline_invoices.find(
                    {"customer_phone": {"$regex": customer_phone[-10:]}},
                    {"_id": 0}
                ).sort("created_at", -1).limit(5).to_list(5)
                context["customer_orders"] = orders
            
            # If specific order ID provided
            if order_id:
                order = await self.db.offline_invoices.find_one(
                    {"$or": [{"id": order_id}, {"invoice_number": order_id}]},
                    {"_id": 0}
                )
                if not order:
                    order = await self.db.orders.find_one(
                        {"$or": [{"id": order_id}, {"order_number": order_id}]},
                        {"_id": 0}
                    )
                context["specific_order"] = order
            
            return context
        except Exception as e:
            print(f"Error fetching delivery context: {e}")
            return {"pending_deliveries": 0, "out_for_delivery": 0, "delivered_today": 0, "customer_orders": [], "specific_order": None}
    
    async def _fetch_marketing_metrics(self) -> Dict[str, Any]:
        """Fetch marketing metrics and campaign performance"""
        try:
            today = datetime.now(timezone.utc)
            month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Get customer signups this month
            new_customers = await self.db.customers.count_documents({
                "created_at": {"$gte": month_start.isoformat()}
            })
            
            # Get total customers
            total_customers = await self.db.customers.count_documents({})
            
            # Get email campaigns
            campaigns = await self.db.marketing_campaigns.find(
                {}, {"_id": 0}
            ).sort("created_at", -1).limit(10).to_list(10)
            
            # Get email stats if available
            email_stats = await self.db.email_logs.aggregate([
                {"$match": {"sent_at": {"$gte": month_start.isoformat()}}},
                {"$group": {
                    "_id": None,
                    "total_sent": {"$sum": 1},
                    "successful": {"$sum": {"$cond": [{"$eq": ["$status", "sent"]}, 1, 0]}}
                }}
            ]).to_list(1)
            
            return {
                "new_customers_this_month": new_customers,
                "total_customers": total_customers,
                "recent_campaigns": campaigns,
                "email_stats": email_stats[0] if email_stats else {"total_sent": 0, "successful": 0}
            }
        except Exception as e:
            print(f"Error fetching marketing metrics: {e}")
            return {"new_customers_this_month": 0, "total_customers": 0, "recent_campaigns": [], "email_stats": {}}
    
    # ================== LEAD MANAGEMENT ==================
    
    async def save_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save or update a lead from conversation"""
        try:
            lead = {
                "id": str(uuid.uuid4()),
                "name": lead_data.get("name"),
                "phone": lead_data.get("phone"),
                "email": lead_data.get("email"),
                "address": lead_data.get("address"),
                "interested_in": lead_data.get("product_category"),
                "budget": lead_data.get("budget"),
                "source": "ai_chat",
                "status": "new",
                "notes": lead_data.get("notes", ""),
                "conversation_id": lead_data.get("session_id"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Check if lead already exists (by phone or email)
            existing = None
            if lead["phone"]:
                existing = await self.db.leads.find_one({"phone": lead["phone"]})
            if not existing and lead["email"]:
                existing = await self.db.leads.find_one({"email": lead["email"]})
            
            if existing:
                # Update existing lead
                update_data = {k: v for k, v in lead.items() if v and k not in ["id", "created_at"]}
                update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
                await self.db.leads.update_one({"id": existing["id"]}, {"$set": update_data})
                return {"status": "updated", "lead_id": existing["id"]}
            else:
                # Create new lead
                await self.db.leads.insert_one(lead)
                return {"status": "created", "lead_id": lead["id"]}
        except Exception as e:
            print(f"Error saving lead: {e}")
            return {"status": "error", "message": str(e)}
    
    # ================== SERVICE TICKET CREATION ==================
    
    async def create_service_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a service ticket from chat conversation"""
        try:
            ticket_number = f"SRV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
            
            ticket = {
                "id": str(uuid.uuid4()),
                "ticket_number": ticket_number,
                "customer_name": ticket_data.get("name"),
                "customer_phone": ticket_data.get("phone"),
                "customer_email": ticket_data.get("email"),
                "customer_address": ticket_data.get("address"),
                "product_name": ticket_data.get("product_name"),
                "product_model": ticket_data.get("model"),
                "issue_type": ticket_data.get("issue_type", "general"),
                "issue_description": ticket_data.get("issue_description"),
                "purchase_date": ticket_data.get("purchase_date"),
                "warranty_status": "under_warranty",  # Default, to be verified
                "status": "open",
                "priority": ticket_data.get("priority", "medium"),
                "source": "ai_chat",
                "conversation_id": ticket_data.get("session_id"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await self.db.service_tickets.insert_one(ticket)
            
            return {
                "status": "created",
                "ticket_id": ticket["id"],
                "ticket_number": ticket_number,
                "message": f"Service ticket {ticket_number} created successfully"
            }
        except Exception as e:
            print(f"Error creating service ticket: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_agent_response(self, agent_type: str, message: str, context: Dict[str, Any] = None) -> str:
        """Get response from specified AI agent with conversation history and real-time data"""
        
        session_id = context.get('session_id', 'default') if context else 'default'
        full_session_id = f"{agent_type}_{session_id}"
        
        # Fetch conversation history from database
        conversation_history = await self._get_conversation_history(session_id, agent_type)
        
        # Fetch real-time product data from database
        product_catalog = await self._fetch_product_catalog()
        
        # Fetch agent-specific real-time context
        agent_context = {}
        if agent_type == "sales":
            agent_context = await self._fetch_leads_summary()
        elif agent_type == "service":
            # Extract phone/email from context for customer lookup
            customer_phone = context.get('customer', {}).get('phone') if context else None
            customer_email = context.get('customer', {}).get('email') if context else None
            agent_context = await self._fetch_service_context(customer_phone, customer_email)
        elif agent_type == "delivery":
            order_id = context.get('order', {}).get('order_id') if context else None
            customer_phone = context.get('customer', {}).get('phone') if context else None
            agent_context = await self._fetch_delivery_context(order_id, customer_phone)
        elif agent_type == "marketing":
            agent_context = await self._fetch_marketing_metrics()
        
        # Initialize chat with agent-specific system message (now with real-time data)
        system_message = await self._get_system_message(agent_type, product_catalog, agent_context)
        
        # Track data already collected from conversation
        collected_info = {
            'name': None, 'phone': None, 'email': None, 
            'address': None, 'model': None, 'issue': None,
            'budget': None, 'product_category': None
        }
        
        # Add conversation history to system message with extracted data
        if conversation_history:
            history_text = "\n\n🔍 CONVERSATION HISTORY (READ CAREFULLY - DO NOT ASK FOR INFO ALREADY PROVIDED):\n"
            
            for idx, msg in enumerate(conversation_history[-15:], 1):  # Last 15 messages
                sender = "Customer" if msg['sender'] == 'user' else "You"
                message_text = msg['message']
                history_text += f"{idx}. {sender}: {message_text}\n"
                
                # Auto-extract common info patterns from user messages
                if msg['sender'] == 'user':
                    # Check for phone number
                    phone_match = re.search(r'\b[6-9]\d{9}\b', message_text)
                    if phone_match:
                        collected_info['phone'] = phone_match.group()
                    # Check for email
                    email_match = re.search(r'\b[\w.-]+@[\w.-]+\.\w+\b', message_text)
                    if email_match:
                        collected_info['email'] = email_match.group()
                    # Check for budget patterns
                    budget_match = re.search(r'(\d+[,.]?\d*)\s*(k|lakh|lac|L|thousand|rupees|rs|₹)?', message_text, re.IGNORECASE)
                    if budget_match:
                        collected_info['budget'] = budget_match.group()
            
            # Add extracted info summary
            info_summary = "\n\n📋 ALREADY COLLECTED (DO NOT ASK AGAIN):\n"
            has_info = False
            for key, value in collected_info.items():
                if value:
                    info_summary += f"  ✓ {key.title()}: {value}\n"
                    has_info = True
            
            if has_info:
                history_text += info_summary
            
            history_text += "\n⚠️ CRITICAL: Before asking ANY question, check if customer already provided it above!\n"
            system_message += history_text
        
        # Use GPT-4o for better intelligence
        chat = LlmChat(
            api_key=self.api_key,
            session_id=full_session_id,
            system_message=system_message
        ).with_model("openai", "gpt-4o")  # Upgraded to GPT-4o for smarter responses
        
        # Add context to the message if provided
        enhanced_message = self._enhance_message_with_context(message, context, agent_type)
        
        user_message = UserMessage(text=enhanced_message)
        
        try:
            response = await chat.send_message(user_message)
            
            # For sales agent, try to capture lead info
            if agent_type == "sales" and collected_info.get('phone') or collected_info.get('email'):
                await self.save_lead({
                    "phone": collected_info.get('phone'),
                    "email": collected_info.get('email'),
                    "name": collected_info.get('name'),
                    "budget": collected_info.get('budget'),
                    "product_category": collected_info.get('product_category'),
                    "session_id": session_id
                })
            
            return response
        except Exception as e:
            return f"I apologize, but I'm experiencing technical difficulties. Please try again later. Error: {str(e)}"
    
    async def _get_conversation_history(self, session_id: str, agent_type: str, limit: int = 20) -> List[Dict]:
        """Fetch recent conversation history for context"""
        try:
            print(f"🔍 Fetching history for session_id: {session_id}, agent_type: {agent_type}")
            
            messages = await self.db.chat_messages.find(
                {"session_id": session_id, "agent_type": agent_type},
                {"_id": 0, "sender": 1, "message": 1, "timestamp": 1}
            ).sort("timestamp", 1).limit(limit).to_list(limit)
            
            print(f"📚 Found {len(messages)} messages in history")
            for msg in messages:
                print(f"  - {msg.get('sender', 'unknown')}: {msg.get('message', '')[:50]}...")
            
            return messages
        except Exception as e:
            print(f"❌ Error fetching conversation history: {e}")
            return []
    
    async def _fetch_product_catalog(self) -> Dict[str, Any]:
        """Fetch real-time product catalog from MongoDB"""
        try:
            # Fetch all products
            products = await self.db.products.find({}, {"_id": 0}).to_list(1000)
            
            # Organize products by category and brand
            categories = {}
            brands = {}
            price_ranges = {"under_20k": [], "20k_50k": [], "50k_100k": [], "above_100k": []}
            stock_summary = {"in_stock": 0, "low_stock": 0, "out_of_stock": 0}
            
            for product in products:
                # Organize by category
                category = product.get('category', 'Uncategorized')
                if category not in categories:
                    categories[category] = []
                categories[category].append(product)
                
                # Organize by brand
                brand = product.get('brand', 'Unknown')
                if brand not in brands:
                    brands[brand] = []
                brands[brand].append(product)
                
                # Organize by price range
                price = product.get('price', 0)
                if price < 20000:
                    price_ranges["under_20k"].append(product)
                elif price < 50000:
                    price_ranges["20k_50k"].append(product)
                elif price < 100000:
                    price_ranges["50k_100k"].append(product)
                else:
                    price_ranges["above_100k"].append(product)
                
                # Stock summary
                stock = product.get('stock', 0)
                if stock == 0:
                    stock_summary["out_of_stock"] += 1
                elif stock <= 5:
                    stock_summary["low_stock"] += 1
                else:
                    stock_summary["in_stock"] += 1
            
            return {
                "products": products,
                "total_count": len(products),
                "categories": categories,
                "brands": brands,
                "price_ranges": price_ranges,
                "stock_summary": stock_summary
            }
        except Exception as e:
            print(f"Error fetching product catalog: {e}")
            return {"products": [], "total_count": 0, "categories": {}, "brands": {}, "price_ranges": {}, "stock_summary": {}}
    
    async def _get_system_message(self, agent_type: str, product_catalog: Dict[str, Any], agent_context: Dict[str, Any] = None) -> str:
        """Get system message for each agent type with real-time product data and context"""
        
        # Build dynamic product catalog summary
        catalog_summary = self._build_catalog_summary(product_catalog)
        agent_context = agent_context or {}
        
        # Build leads summary for sales agent
        leads_info = ""
        if agent_type == "sales" and agent_context:
            leads_info = f"""
**📊 YOUR CURRENT PERFORMANCE METRICS:**
- Total Leads Captured: {agent_context.get('total_leads', 0)}
- Converted to Sales: {agent_context.get('converted_leads', 0)}
- Hot Leads (Active): {agent_context.get('hot_leads', 0)}
- Conversion Rate: {agent_context.get('conversion_rate', 0)}%
"""

        # Build service context for service agent
        service_info = ""
        if agent_type == "service" and agent_context:
            service_info = f"""
**📋 CURRENT SERVICE STATUS:**
- Open Tickets: {agent_context.get('open_tickets', 0)}
- Resolved This Month: {agent_context.get('resolved_tickets', 0)}
"""
            if agent_context.get('customer_history'):
                service_info += "\n**⚡ THIS CUSTOMER'S HISTORY:**\n"
                for ticket in agent_context['customer_history'][:3]:
                    service_info += f"  - {ticket.get('ticket_number', 'N/A')}: {ticket.get('issue_type', 'N/A')} - {ticket.get('status', 'N/A')}\n"
            if agent_context.get('registered_products'):
                service_info += "\n**🏠 CUSTOMER'S REGISTERED PRODUCTS:**\n"
                for prod in agent_context['registered_products'][:5]:
                    service_info += f"  - {prod.get('product_name', 'N/A')} (Warranty: {prod.get('warranty_status', 'Unknown')})\n"

        # Build delivery context for delivery agent
        delivery_info = ""
        if agent_type == "delivery" and agent_context:
            delivery_info = f"""
**📦 TODAY'S DELIVERY STATUS:**
- Pending Deliveries: {agent_context.get('pending_deliveries', 0)}
- Out for Delivery: {agent_context.get('out_for_delivery', 0)}
- Delivered Today: {agent_context.get('delivered_today', 0)}
"""
            if agent_context.get('specific_order'):
                order = agent_context['specific_order']
                delivery_info += f"""
**📍 CURRENT ORDER DETAILS:**
- Order/Invoice #: {order.get('invoice_number') or order.get('order_number', 'N/A')}
- Status: {order.get('status', 'N/A')}
- Customer: {order.get('customer_name', 'N/A')}
- Phone: {order.get('customer_phone', 'N/A')}
- Delivery Address: {order.get('shipping_address', 'N/A')}
- Items: {len(order.get('items', []))} products
- Amount: ₹{order.get('total_amount', 0):,.2f}
"""

        # Build marketing context
        marketing_info = ""
        if agent_type == "marketing" and agent_context:
            marketing_info = f"""
**📈 MARKETING PERFORMANCE (This Month):**
- New Customers: {agent_context.get('new_customers_this_month', 0)}
- Total Customer Base: {agent_context.get('total_customers', 0)}
- Emails Sent: {agent_context.get('email_stats', {}).get('total_sent', 0)}
- Success Rate: {round((agent_context.get('email_stats', {}).get('successful', 0) / max(agent_context.get('email_stats', {}).get('total_sent', 1), 1)) * 100, 1)}%
"""
        
        system_messages = {
            "sales": f"""You are Ai.ditya, an elite AI Sales Assistant for Aditya Retail - India's premium Bosch & Siemens home appliances retailer.

🎯 YOUR MISSION: Convert every conversation into a qualified lead and potential sale. Be warm, helpful, but strategically guide customers toward purchase decisions.

{catalog_summary}
{leads_info}

## **🏆 SALES EXCELLENCE PROTOCOL:**

### **PHASE 1: CAPTURE CONTACT FIRST (Messages 1-2) - CRITICAL!**
⚠️ **DO NOT share product recommendations until you have at least NAME + PHONE!**

1. Warmly greet: "Hi! I'm Ai.ditya from Aditya Retail 😊"
2. Acknowledge their need briefly
3. **IMMEDIATELY ask**: "Before I show you the best options, may I know your good name and mobile number? I'll share exclusive prices directly!"

**Example Flow:**
- Customer: "I need a washing machine"
- You: "Great choice! 🎉 I have some amazing Bosch & Siemens options for you. Before I share the best deals, may I know your good name and the best number to reach you? I'll make sure you get our exclusive web prices!"

### **PHASE 2: QUALIFY & RECOMMEND (After getting contact)**
1. Ask about budget and family size
2. Present 2-3 best-fit products with clear benefits
3. Create urgency when appropriate

### **PHASE 3: CLOSE & FOLLOW-UP**
1. Offer store visit scheduling
2. Confirm callback time
3. Send product details via WhatsApp/Email

## **💡 SMART SELLING TECHNIQUES:**

**VALUE FRAMING:**
- Instead of "This costs ₹80,000", say "For just ₹80,000, you get 10+ years of reliability, 5-star energy savings worth ₹15,000/year, and premium German engineering"

**SOCIAL PROOF:**
- "This is our best-seller in Bangalore"
- "Most families of 4-5 prefer this model"

**URGENCY CREATION:**
- "We have only 3 units in stock"
- "Current festive offer ends this week"

**OBJECTION HANDLING:**
- Price concern: Highlight EMI options, long-term savings
- Brand doubt: Share warranty coverage, service network
- Need to think: Offer callback, exclusive web price

## **📞 LEAD CAPTURE (YOUR #1 PRIORITY - BEFORE ANYTHING ELSE!):**

**🚨 RULE: NO PRODUCT DETAILS WITHOUT CONTACT INFO!**

**Message 1 Response - ALWAYS include:**
"Before I show you the best options, may I know your good name and mobile number?"

**If customer asks for products without giving contact:**
"I'd love to help! Just share your name and number, and I'll send you our best deals with exclusive prices! 📱"

**If customer resists:**
- "No spam, promise! Just want to WhatsApp you the best price 😊"
- "It helps me check real-time stock and reserve it for you"
- "I'll send you a personalized quote - much better than website prices!"

**MUST collect before showing ANY product:**
1. Full Name ✓
2. Mobile Number ✓ (10 digits)
3. Email (ask after phone)

**Natural conversation starters:**
- "Hi! I'm Ai.ditya 😊 May I know your good name?"
- "Perfect! And what's the best number to reach you? I'll share exclusive offers!"
- "Great [Name]! Let me also take your email to send detailed specs"

**🎯 GOLDEN RULE: Name + Phone FIRST → Then Product Recommendations**

## **🏪 STORE VISIT BOOKING:**

Our stores:
- **HRBR Layout, Bangalore**: Near HRBR 4th Block, Banaswadi Road
- **JP Nagar, Bangalore**: JP Nagar 7th Phase

"Would you like to visit our showroom? I can arrange a personal demo with our product specialist. What day works best for you?"

## **📱 PRODUCT RECOMMENDATIONS FORMAT:**

For washing machines under ₹80,000:

**1. [Bosch 8kg AI Wash WAJ2846WIN](PRODUCT_LINK:id)** - ₹72,990 ✅ In Stock
   ⭐ AI-powered wash technology
   ⭐ 5-star energy rating (saves ₹8,000/year)
   ⭐ 2-year warranty + 10-year motor warranty
   → Perfect for 4-5 member families

**2. [Siemens 9kg iQdrive WG54A2X0IN](PRODUCT_LINK:id)** - ₹79,500 ✅ Only 2 left!
   ⭐ German engineering with iQdrive motor
   ⭐ Stain removal programs for Indian fabrics
   → Recommended for premium homes

**Special Offer:** Free installation + ₹3,000 cashback this week!

📞 Shall I connect you with our appliance expert?

---

**RESPONSE STYLE:**
- Be enthusiastic but professional
- Use emojis sparingly but effectively
- Always end with a call-to-action
- Never end abruptly - always offer next steps

Be the best salesperson - helpful, knowledgeable, and results-driven! 🚀
""",

            "service": f"""You are Aditya Retail's Expert Service Agent - a certified technical support specialist for premium Bosch and Siemens home appliances.

{self._build_service_catalog_summary(product_catalog)}
{service_info}

## **🎯 YOUR SERVICE EXCELLENCE PROTOCOL:**

### **PHASE 1: WARM GREETING & INITIAL ASSESSMENT**
1. Greet professionally and empathetically
2. Ask about the appliance and issue
3. Confirm warranty status if possible

### **PHASE 2: INTELLIGENT TROUBLESHOOTING**
Before escalating, try to resolve common issues:

**🔧 WASHING MACHINE ISSUES:**
- Not draining: Check drain hose, clean pump filter
- Not spinning: Check load balance, door lock
- Error E18/E21: Water inlet issue - check taps, filters
- Vibrating: Level the machine, remove transit bolts

**🔧 REFRIGERATOR ISSUES:**
- Not cooling: Check door seal, clean condenser coils
- Freezing everything: Adjust thermostat (4°C ideal)
- Ice buildup: Defrost, check door gasket
- Noise: Level the unit, check compressor

**🔧 DISHWASHER ISSUES:**
- Not cleaning: Check spray arms, clean filters
- Water remaining: Clean drain filter, check drain hose
- Not draining: Reset, run empty hot cycle
- Door issues: Check hinges, spring tension

**🔧 CHIMNEY/HOB ISSUES:**
- Low suction: Clean baffle filters (monthly required)
- Not igniting: Clean igniter, check gas connection
- Noise: Tighten mounting screws

**🔧 MICROWAVE/OVEN ISSUES:**
- Not heating: Check door switch, magnetron
- Uneven heating: Use turntable, rotate dishes
- Sparking: Remove metal, clean interior

### **PHASE 3: TICKET CREATION (If unresolved)**
Once troubleshooting fails, collect:
✅ Full Name
✅ Phone Number (10 digits)
✅ Email Address  
✅ Complete Address (for technician visit)
✅ Product Model Number (on label/sticker)
✅ Purchase Date (approximate)
✅ Detailed Issue Description

**DO NOT ask for info already provided in conversation!**

### **PHASE 4: TICKET CONFIRMATION**
"I've created your service ticket: **[TICKET_NUMBER]**

📧 You'll receive:
1. Email confirmation within 5 minutes
2. Brand complaint number within 24-48 hours
3. Technician call to schedule visit

⏰ Typical resolution: 3-5 business days
📞 For urgent issues, contact our helpline: +91 98445 77440

Is there anything else I can help you with?"

## **⚡ SMART CONTEXT USAGE:**

**If customer has registered products:**
- Reference their specific model
- Check warranty status
- Mention any previous service history

**If customer has past tickets:**
- "I see you had a similar issue before..."
- Reference resolution from previous ticket
- Ensure continuity of service

## **🏅 SERVICE STANDARDS:**
- **Response Time:** Acknowledge within 1 message
- **Resolution Time:** Self-help fix within 3 messages OR ticket created
- **Follow-up:** Promise callback within 48 hours
- **Empathy:** Always acknowledge frustration, apologize for inconvenience

## **📋 IMPORTANT REMINDERS:**
- Safety first! For gas leaks/electrical hazards - advise immediate shutdown
- Don't recommend DIY for complex repairs
- Warranty covers manufacturing defects, not physical damage
- Free service visits during warranty period
- Genuine spare parts only

Be empathetic, efficient, and resolution-focused! 🛠️
""",

            "delivery": f"""You are Aditya Retail's Delivery Coordination Agent - managing order fulfillment and ensuring customer satisfaction with every delivery.

{delivery_info}

## **🎯 YOUR DELIVERY EXCELLENCE PROTOCOL:**

### **INFORMATION YOU CAN PROVIDE:**

**1. ORDER STATUS TRACKING:**
- Order placed & confirmed
- Processing at warehouse
- Ready for dispatch
- Out for delivery
- Delivered

**2. DELIVERY TIMELINES:**
- **Bangalore (Same city):** Same-day delivery (orders before 12 PM)
- **Karnataka cities (Mysore, Mangalore):** Next-day delivery
- **Metro cities (Delhi, Mumbai, Chennai):** 2-3 business days
- **Other locations:** 4-7 business days

**3. DELIVERY OPTIONS:**
- **Standard Delivery:** Free above ₹15,000
- **Express Delivery:** ₹500 extra (Bangalore same-day)
- **Scheduled Delivery:** Choose date/time slot
- **White-Glove Service:** Installation + demo included

### **📦 ORDER LOOKUP PROCESS:**

When customer asks about their order:
1. Ask for Order Number OR Phone Number
2. Retrieve order details from system
3. Provide current status and expected delivery
4. Offer rescheduling if needed

**Sample Response:**
"I found your order **[ORDER_NUMBER]**! Here's the status:

📦 **Status:** Out for Delivery
🚚 **Expected:** Today by 6 PM
📍 **Address:** [Customer's delivery address]
📞 **Delivery contact:** Our delivery partner will call 30 mins before arrival

Would you like to:
a) Reschedule to a different time?
b) Change delivery address?
c) Add installation service?"

### **🔄 RESCHEDULING REQUESTS:**

"I can help you reschedule! Here are available slots:
- Tomorrow, 10 AM - 1 PM
- Tomorrow, 2 PM - 5 PM
- [Next Date], 10 AM - 1 PM

Which slot works best for you?"

### **❌ ISSUE HANDLING:**

**Delayed Delivery:**
"I sincerely apologize for the delay. Let me check with our logistics team and update you.

🔍 I'm escalating this immediately
📞 You'll receive a callback within 2 hours
💝 We'll ensure priority delivery"

**Wrong/Damaged Product:**
"I'm so sorry about this! Here's what we'll do:

1. ⏰ Immediate replacement request raised
2. 📦 New product will ship within 24 hours
3. 🔄 Free pickup of damaged item
4. 💰 Compensation for inconvenience

Our team will call you shortly to arrange pickup."

**Address Change:**
"I can update the delivery address! Please provide:
- New complete address with landmark
- New contact number (if different)
- Preferred delivery time slot"

### **📞 INSTALLATION SERVICES:**

For appliances requiring installation:
"Great news! Your [Product] includes free installation.

📅 Our technician will call to schedule
⏱️ Installation takes 30-60 minutes
📋 They'll demonstrate all features
📝 Please keep purchase bill ready

Any specific time preference for installation?"

### **🌟 PROACTIVE COMMUNICATION:**

Always:
- Provide estimated delivery window
- Share tracking link when available
- Mention what happens next
- Offer callbacks for complex issues
- Thank them for their patience

Be efficient, accurate, and customer-first! 📦
""",

            "marketing": f"""You are Aditya Retail's Digital Marketing Strategist - driving customer engagement, brand awareness, and sales growth.

{marketing_info}

## **🎯 YOUR MARKETING EXPERTISE:**

### **1. CAMPAIGN STRATEGY:**

**Campaign Types We Run:**
- 🎉 **Festive Campaigns:** Diwali, New Year, Pongal, Summer
- 🆕 **Product Launch:** New Bosch/Siemens arrivals
- 💰 **Flash Sales:** Limited-time discounts
- 🎁 **Bundle Offers:** Combo deals, accessories
- ♻️ **Retention:** Win-back, loyalty rewards
- 🛒 **Abandoned Cart:** Recovery emails

**Channel Mix:**
- 📧 Email Marketing (primary)
- 📱 SMS/WhatsApp (urgent offers)
- 🖼️ Social Media (Instagram, Facebook)
- 🔍 Google Ads (search, display)
- 👥 Influencer partnerships

### **2. CUSTOMER SEGMENTATION:**

**Segments We Target:**
- **Premium Buyers:** ₹1L+ purchases, Bosch preference
- **Value Seekers:** Budget-conscious, deal-hunters
- **New Movers:** Recently relocated, full home setup
- **Upgrade Seekers:** 5+ year old appliances
- **Business Buyers:** Hotels, restaurants, offices

### **3. CAMPAIGN IDEAS:**

**Seasonal:**
- "Summer Cool Sale" - ACs, refrigerators
- "Monsoon Ready" - Washing machines, dryers
- "Festive Kitchen" - Ovens, dishwashers

**Evergreen:**
- "Trade-in Offer" - Old appliance exchange
- "Refer a Friend" - Get ₹5,000 credit
- "Extended Warranty" - Peace of mind

### **4. METRICS I TRACK:**

📊 **Key Performance Indicators:**
- Open Rate Target: 25%+
- Click Rate Target: 5%+
- Conversion Rate: 2%+
- Customer Acquisition Cost: <₹500
- Email ROI: 40x

### **5. CONTENT STRATEGY:**

**Blog Topics:**
- "How to Choose the Right Washing Machine"
- "Energy Saving Tips for Home Appliances"
- "Bosch vs Siemens: Which is Right for You?"

**Social Content:**
- Product demos and reviews
- Customer testimonials
- Behind-the-scenes at showroom
- Appliance care tips

### **📈 RECOMMENDATIONS FORMAT:**

"Based on our current data, I recommend:

**Campaign:** Summer Cool Sale
**Target:** All customers, focus on Bangalore
**Channels:** Email + SMS + Instagram
**Offer:** Up to 25% off ACs + Free Installation
**Duration:** 2 weeks

**Expected Results:**
- Reach: 50,000 customers
- Conversions: 200+ sales
- Revenue: ₹80L+

**Budget:** ₹50,000
**ROI Projection:** 15x

Shall I create the campaign brief?"

Be strategic, data-driven, and creative! 📊
""",

            "stock": """You are an Inventory Management Agent for Aditya Retail, responsible for stock optimization and supply chain management. Your role is to:

1. Monitor real-time inventory levels across all products
2. Generate low-stock alerts and reorder recommendations
3. Analyze sales trends and demand patterns
4. Optimize stock levels to minimize overstocking and stockouts
5. Provide inventory reports and analytics
6. Manage supplier relationships and purchase orders

Key Metrics to Track:
- Current stock levels vs. reorder points
- Sales velocity and turnover rates
- Seasonal demand patterns
- Fast-moving vs. slow-moving items
- Stock valuation and carrying costs
- Supplier lead times and reliability

Inventory Strategy:
- Maintain 15-30 days stock for fast-moving items
- Keep 45-60 days stock for seasonal products
- Use ABC analysis for inventory classification
- Implement Just-in-Time for high-value items
- Monitor competitor pricing and market trends

Alert Thresholds:
- Critical: Less than 5 units (immediate reorder)
- Low: Less than 10 units (plan reorder)
- Excess: More than 90 days stock (promote/clearance)

Provide actionable insights with specific recommendations, quantities, and timelines."""
        }
        
        return system_messages.get(agent_type, "You are a helpful AI assistant for Aditya Retail.")
    
    def _build_catalog_summary(self, catalog: Dict[str, Any]) -> str:
        """Build a comprehensive product catalog summary for sales agent"""
        if not catalog or catalog.get("total_count", 0) == 0:
            return "**NO PRODUCTS CURRENTLY AVAILABLE IN CATALOG**"
        
        summary = f"""**YOUR COMPLETE PRODUCT CATALOG ({catalog['total_count']} Products):**

**BRANDS AVAILABLE:**
"""
        # First show all brands so AI knows what's available
        for brand, products in catalog.get("brands", {}).items():
            categories_for_brand = set(p.get('category', 'Unknown') for p in products)
            summary += f"  - **{brand}**: {len(products)} products in {', '.join(categories_for_brand)}\n"
        
        summary += f"\n**CATEGORIES & SAMPLE PRODUCTS:**\n"
        summary += f"(Use PRODUCT_LINK:product_id format for links, e.g., [Product Name](PRODUCT_LINK:abc123))\n\n"
        
        # List products by category (show more variety by including different brands)
        for category, products in catalog.get("categories", {}).items():
            summary += f"\n**{category}** ({len(products)} products):\n"
            
            # Group by brand within category to ensure all brands are shown
            brands_in_category = {}
            for product in products:
                brand = product.get('brand', 'Unknown')
                if brand not in brands_in_category:
                    brands_in_category[brand] = []
                brands_in_category[brand].append(product)
            
            # Show products from each brand in this category
            products_shown = 0
            for brand, brand_products in brands_in_category.items():
                for product in brand_products[:3]:  # Show up to 3 per brand per category
                    if products_shown >= 15:  # Max 15 per category total
                        break
                    name = product.get('name', 'Unknown')
                    product_id = product.get('id', '')
                    price = product.get('price', 0)
                    stock = product.get('stock', 0)
                    stock_status = "In Stock" if stock > 5 else f"Low Stock ({stock} left)" if stock > 0 else "Out of Stock"
                    # Include product ID for linking
                    summary += f"  - **{name}** (ID: {product_id}) by {brand}: Rs. {price:,.0f} [{stock_status}]\n"
                    products_shown += 1
        
        # Stock summary
        stock_sum = catalog.get("stock_summary", {})
        summary += f"\n**STOCK STATUS:**\n"
        summary += f"  - In Stock: {stock_sum.get('in_stock', 0)} products\n"
        summary += f"  - Low Stock: {stock_sum.get('low_stock', 0)} products (≤5 units)\n"
        summary += f"  - Out of Stock: {stock_sum.get('out_of_stock', 0)} products\n"
        
        # Price range summary
        summary += f"\n**PRICE RANGES:**\n"
        summary += f"  - Under Rs. 20,000: {len(catalog.get('price_ranges', {}).get('under_20k', []))} products\n"
        summary += f"  - Rs. 20,000 - Rs. 50,000: {len(catalog.get('price_ranges', {}).get('20k_50k', []))} products\n"
        summary += f"  - Rs. 50,000 - Rs. 1,00,000: {len(catalog.get('price_ranges', {}).get('50k_100k', []))} products\n"
        summary += f"  - Above Rs. 1,00,000: {len(catalog.get('price_ranges', {}).get('above_100k', []))} products\n"
        
        summary += f"\n**IMPORTANT LINK FORMAT:**\n"
        summary += f"When recommending products, ALWAYS use this exact format:\n"
        summary += f"[Product Name](PRODUCT_LINK:product_id)\n"
        summary += f"Example: [Bosch 8kg Washing Machine](PRODUCT_LINK:abc123)\n"
        
        return summary
    
    def _build_service_catalog_summary(self, catalog: Dict[str, Any]) -> str:
        """Build a product catalog summary for service agent"""
        if not catalog or catalog.get("total_count", 0) == 0:
            return "**NO PRODUCTS CURRENTLY IN CATALOG**"
        
        summary = f"""We service {catalog['total_count']} products across the following categories:\n"""
        
        for category, products in catalog.get("categories", {}).items():
            summary += f"\n**{category}** ({len(products)} models):\n"
            for product in products[:5]:  # Show up to 5 products per category
                name = product.get('name', 'Unknown')
                brand = product.get('brand', '')
                summary += f"  - {name} by {brand}\n"
                # Add features if available
                features = product.get('features', [])
                if features and len(features) > 0:
                    summary += f"    Features: {', '.join(features[:3])}\n"
        
        return summary
    
    def _enhance_message_with_context(self, message: str, context: Dict[str, Any], agent_type: str) -> str:
        """Enhance user message with relevant context information"""
        
        if not context:
            return message
        
        enhanced_message = message
        
        # Add product context if available
        if 'product' in context:
            product = context['product']
            
            # Handle both string and dict product context
            if isinstance(product, str):
                enhanced_message += f"\n\nContext - Customer is interested in: {product}"
            elif isinstance(product, dict):
                enhanced_message += f"\n\nContext - Customer is interested in: {product.get('name', 'Unknown Product')}"
                enhanced_message += f"\nPrice: Rs. {product.get('price', 'N/A')}"
                enhanced_message += f"\nBrand: {product.get('brand', 'N/A')}"
                enhanced_message += f"\nCategory: {product.get('category', 'N/A')}"
                if product.get('stock', 0) <= 5:
                    enhanced_message += f"\nStock Alert: Only {product.get('stock', 0)} units left!"
                
                # Add product documents if available
                if 'documents' in product and product['documents']:
                    enhanced_message += f"\n\nAvailable Product Documents:"
                    for doc in product['documents']:
                        enhanced_message += f"\n- {doc.get('title', 'Document')}: {doc.get('url', 'N/A')} ({doc.get('size', 'Unknown size')})"
                    enhanced_message += "\n\nIMPORTANT: When customer asks for manual, PDF, specification sheet, or installation guide, share these download links directly in your response."
        
        # Add customer context for service agents
        if agent_type == 'service' and 'customer' in context:
            customer = context['customer']
            enhanced_message += f"\n\nCustomer Details:"
            enhanced_message += f"\nName: {customer.get('name', 'N/A')}"
            enhanced_message += f"\nEmail: {customer.get('email', 'N/A')}"
            enhanced_message += f"\nPhone: {customer.get('phone', 'N/A')}"
        
        # Add inventory context for stock agents
        if agent_type == 'stock' and 'inventory' in context:
            inventory = context['inventory']
            enhanced_message += f"\n\nCurrent Inventory Status:"
            for item in inventory:
                enhanced_message += f"\n- {item.get('name', 'Unknown')}: {item.get('stock', 0)} units"
        
        # Add order context for delivery agents
        if agent_type == 'delivery' and 'order' in context:
            order = context['order']
            enhanced_message += f"\n\nOrder Details:"
            enhanced_message += f"\nOrder ID: {order.get('order_id', 'N/A')}"
            enhanced_message += f"\nStatus: {order.get('status', 'N/A')}"
            enhanced_message += f"\nDelivery Address: {order.get('address', 'N/A')}"
        
        return enhanced_message


class InventoryAnalyzer:
    """Analyzes inventory and generates insights"""
    
    @staticmethod
    def analyze_stock_levels(products: List[Dict]) -> Dict[str, Any]:
        """Analyze current stock levels and generate alerts"""
        
        low_stock_items = []
        out_of_stock_items = []
        fast_moving_low_stock = []
        excess_stock_items = []
        
        for product in products:
            stock = product.get('stock', 0)
            fast_moving = product.get('fast_moving', False)
            
            if stock == 0:
                out_of_stock_items.append(product)
            elif stock <= 5:
                low_stock_items.append(product)
                if fast_moving:
                    fast_moving_low_stock.append(product)
            elif stock > 50:  # Assuming 50+ is excess for most items
                excess_stock_items.append(product)
        
        return {
            "low_stock_count": len(low_stock_items),
            "out_of_stock_count": len(out_of_stock_items),
            "fast_moving_low_stock_count": len(fast_moving_low_stock),
            "excess_stock_count": len(excess_stock_items),
            "alerts": {
                "critical": out_of_stock_items,
                "low_stock": low_stock_items,
                "fast_moving_low": fast_moving_low_stock,
                "excess_stock": excess_stock_items
            },
            "recommendations": InventoryAnalyzer._generate_recommendations(
                low_stock_items, out_of_stock_items, fast_moving_low_stock
            )
        }
    
    @staticmethod
    def _generate_recommendations(low_stock, out_of_stock, fast_moving_low) -> List[str]:
        """Generate inventory management recommendations"""
        
        recommendations = []
        
        if out_of_stock:
            recommendations.append(f"🚨 URGENT: {len(out_of_stock)} products are out of stock. Immediate reorder required.")
        
        if fast_moving_low:
            recommendations.append(f"⚡ PRIORITY: {len(fast_moving_low)} fast-moving items are low on stock. Reorder within 24 hours.")
        
        if low_stock:
            recommendations.append(f"⚠️ WARNING: {len(low_stock)} products need reordering within this week.")
        
        # Calculate total reorder value
        total_reorder_value = sum(p.get('price', 0) * 10 for p in (out_of_stock + fast_moving_low))
        if total_reorder_value > 0:
            recommendations.append(f"💰 Estimated reorder value: Rs. {total_reorder_value:,.2f}")
        
        return recommendations


class MarketingInsights:
    """Generates marketing insights and campaign suggestions"""
    
    @staticmethod
    def analyze_customer_behavior(sessions: List[Dict]) -> Dict[str, Any]:
        """Analyze customer behavior patterns"""
        
        popular_categories = {}
        conversion_funnel = {"views": 0, "cart_adds": 0, "purchases": 0}
        
        # Simulate analysis (in real app, this would process actual data)
        insights = {
            "top_categories": ["Washing Machine", "Microwave", "Fridge"],
            "peak_hours": ["10 AM - 12 PM", "7 PM - 9 PM"],
            "conversion_rate": "3.2%",
            "avg_session_duration": "8 minutes",
            "cart_abandonment_rate": "68%",
            "recommendations": [
                "Launch remarketing campaign for cart abandoners",
                "Create bundle offers for popular categories",
                "Optimize mobile experience during peak hours",
                "Implement urgency messaging for low stock items"
            ]
        }
        
        return insights
    
    @staticmethod
    def suggest_campaigns(current_season: str, inventory_data: Dict) -> List[Dict]:
        """Suggest marketing campaigns based on season and inventory"""
        
        campaigns = []
        
        # Seasonal campaigns
        if current_season in ["winter", "december"]:
            campaigns.append({
                "name": "Winter Appliance Festival",
                "type": "seasonal",
                "description": "Special discounts on heating appliances and winter essentials",
                "discount": "15-25%",
                "duration": "7 days"
            })
        
        # Inventory-based campaigns
        if inventory_data.get("excess_stock_count", 0) > 0:
            campaigns.append({
                "name": "Clearance Sale",
                "type": "inventory_clearance",
                "description": "Clear excess inventory with attractive discounts",
                "discount": "20-40%",
                "duration": "14 days"
            })
        
        if inventory_data.get("fast_moving_low_stock_count", 0) > 0:
            campaigns.append({
                "name": "Limited Stock Alert",
                "type": "urgency",
                "description": "Create urgency for fast-moving low stock items",
                "discount": "5-10%",
                "duration": "3 days"
            })
        
        return campaigns