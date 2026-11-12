"""
Neural AI Agents - Advanced Multi-Turn Conversation with Deep Product Knowledge
Uses Gemini 2.5 Pro for superior reasoning and human-like interactions
"""
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from ai_sales_order_manager import AISalesOrderManager

logger = logging.getLogger(__name__)

CATEGORY_FIXES = {
    'refrigerators': 'Refrigerator',
    'washing machines': 'Washing Machine',
    'micrwave': 'Microwave',
    'microwaves': 'Microwave',
    'dishwashers': 'Dishwasher',
    'hobs': 'Hob',
    'gas hobs': 'Gas Hob',
    'hoods': 'Chimney',
    'chimneys': 'Chimney',
    'induction': 'Induction Hob',
    'induction hobs': 'Induction Hob',
    'ovens': 'Oven',
    'dryers': 'Dryer',
    'coffee machines': 'Coffee Machine',
    'mixer grinders': 'Mixer Grinder',
    'air fryers': 'Air Fryer',
}


def normalize_category(raw) -> str:
    """Normalize inconsistent category names (plural/singular variants, typos, whitespace)"""
    if not raw:
        return 'Other'
    clean = ' '.join(str(raw).split()).strip()
    return CATEGORY_FIXES.get(clean.lower(), clean)


class NeuralAIAgentManager:
    """Advanced AI Agent Manager with Claude Sonnet 4.6 and deep product knowledge"""
    
    def __init__(self, db=None):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
        
        # Initialize MongoDB connection
        if db is not None:
            self.db = db
        else:
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            db_name = os.environ.get('DB_NAME', 'startup_template')
            self.client = AsyncIOMotorClient(mongo_url)
            self.db = self.client[db_name]
    
    async def get_neural_response(
        self, 
        agent_type: str, 
        message: str, 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Get intelligent response from Neural AI Agent
        Returns: {
            "response": str,
            "collected_data": dict,  # Customer data collected so far
            "action_required": str,  # "collect_more", "show_products", "create_ticket", "complete"
            "confidence": float  # 0-1 confidence in data collected
        }
        """
        try:
            session_id = context.get('session_id', 'default') if context else 'default'
            full_session_id = f"neural_{agent_type}_{session_id}"
            
            # Fetch conversation history
            conversation_history = await self._get_conversation_history(session_id, agent_type)
            
            # Fetch comprehensive product data
            product_knowledge = await self._build_product_knowledge_base()

            # Fetch REAL-TIME data (orders, purchase history) relevant to this customer
            self._session_id = session_id
            live_context = await self._fetch_live_context(agent_type, message, conversation_history)

            # Get agent-specific system prompt with product knowledge
            system_message = await self._get_neural_system_prompt(
                agent_type, 
                product_knowledge,
                conversation_history,
                live_context
            )
            
            # Initialize Claude Sonnet 4.6 chat
            chat = LlmChat(
                api_key=self.api_key,
                session_id=full_session_id,
                system_message=system_message
            ).with_model("anthropic", "claude-sonnet-4-6")
            
            # Send message and get response
            user_message = UserMessage(text=message)
            response_text = await chat.send_message(user_message)
            
            # Parse response and extract structured data
            parsed_response = await self._parse_agent_response(
                response_text,
                agent_type,
                conversation_history,
                message
            )
            
            return parsed_response
            
        except Exception as e:
            logger.error(f"Neural AI error: {str(e)}")
            return {
                "response": "I apologize for the inconvenience. I'm experiencing technical difficulties. Please try again in a moment.",
                "collected_data": {},
                "action_required": "retry",
                "confidence": 0.0
            }
    
    async def _build_product_knowledge_base(self) -> Dict[str, Any]:
        """Build comprehensive product knowledge base with detailed specs"""
        try:
            # Fetch all products with complete details
            products = await self.db.products.find({}, {"_id": 0}).to_list(1000)
            
            # Organize by brand for better neural understanding
            knowledge_base = {
                "total_products": len(products),
                "brands": {},
                "categories": {},
                "price_segments": {
                    "budget": [],  # < 20k
                    "mid_range": [],  # 20k-50k
                    "premium": [],  # 50k-100k
                    "luxury": []  # > 100k
                },
                "product_details": []
            }
            
            for product in products:
                # Comprehensive product profile
                product_profile = {
                    "id": product.get('id'),
                    "name": product.get('name'),
                    "brand": (product.get('brand') or 'Other').strip(),
                    "model": product.get('model_number'),
                    "category": normalize_category(product.get('category')),
                    "price": product.get('price', 0),
                    "stock": product.get('stock_quantity', 0),
                    "description": product.get('description', ''),
                    "specifications": product.get('specifications', ''),
                    "warranty": product.get('warranty_period', '2 years'),
                    "features": product.get('features', []),
                    "hsn_code": product.get('hsn_code'),
                    "reorder_level": product.get('reorder_level', 10),
                    # Technical documents
                    "manual_url": product.get('manual_url', ''),
                    "tech_specs_url": product.get('tech_specs_url', ''),
                    "installation_guide_url": product.get('installation_guide_url', '')
                }
                
                knowledge_base["product_details"].append(product_profile)
                
                # Organize by brand
                brand = product_profile["brand"]
                if brand not in knowledge_base["brands"]:
                    knowledge_base["brands"][brand] = []
                knowledge_base["brands"][brand].append(product_profile)
                
                # Organize by category (normalized)
                category = product_profile["category"] or 'Other'
                if category not in knowledge_base["categories"]:
                    knowledge_base["categories"][category] = []
                knowledge_base["categories"][category].append(product_profile)
                
                # Organize by price segment
                price = product.get('price', 0)
                if price < 20000:
                    knowledge_base["price_segments"]["budget"].append(product_profile)
                elif price < 50000:
                    knowledge_base["price_segments"]["mid_range"].append(product_profile)
                elif price < 100000:
                    knowledge_base["price_segments"]["premium"].append(product_profile)
                else:
                    knowledge_base["price_segments"]["luxury"].append(product_profile)
            
            return knowledge_base
            
        except Exception as e:
            logger.error(f"Error building knowledge base: {str(e)}")
            return {"total_products": 0, "brands": {}, "categories": {}, "price_segments": {}, "product_details": []}
    
    async def _get_neural_system_prompt(
        self, 
        agent_type: str, 
        knowledge_base: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        live_context: str = ""
    ) -> str:
        """Generate advanced system prompts for Neural AI agents"""
        
        # Build conversation context (+ real-time system data if available)
        context_summary = self._build_context_summary(conversation_history)
        if live_context:
            context_summary += "\n" + live_context
        
        # Build product catalog in structured format
        catalog_text = self._format_product_catalog_for_neural_ai(knowledge_base)
        
        prompts = {
            "sales": f"""# 🧠 NEURAL SALES AI - Advanced Product Expert & Consultant

You are **Ai.ditya Neural**, an elite AI Sales Consultant for Aditya Retail with deep product knowledge and human-like conversation skills.

## 📚 YOUR COMPLETE PRODUCT KNOWLEDGE BASE
{catalog_text}

## 🎯 YOUR MISSION
Provide exceptional consultative sales experience by:
1. **Understanding needs deeply** - Ask intelligent follow-up questions
2. **Recommending perfectly** - Match products to exact requirements
3. **Collecting data systematically** - Name, Phone, Email (MANDATORY)
4. **Closing deals naturally** - Build trust and guide purchase decisions

## 💡 NEURAL INTELLIGENCE RULES

### 🏷️ MULTI-BRAND ADVISORY (CRITICAL — NEVER SKIP)
Aditya Retail sells **Bosch, Siemens, Electrolux** and more. You are a NEUTRAL consultant, NOT a single-brand salesperson.

**RULES:**
1. When a customer asks about ANY category (refrigerator, washing machine, dishwasher...), ALWAYS check the catalog for ALL brands in that category and present options from EVERY available brand — never default to only Bosch.
2. Proactively educate the customer on brand differences so they can choose confidently:
   - **Bosch** — German engineering, legendary reliability & durability, excellent service network in India, great all-rounder.
   - **Siemens** — Bosch's premium sibling (same BSH group), sleeker designs, smarter features (Home Connect), ideal for modern premium kitchens.
   - **Electrolux** — Swedish design heritage, excellent value for money, gentle fabric/food care technologies, strong in laundry.
3. When recommending, show a brand-diverse shortlist (e.g., 1 Bosch + 1 Siemens + 1 Electrolux where stock allows), compare them honestly on price, features and fit, then guide the customer to the best choice FOR THEM.
4. If the customer explicitly prefers one brand, respect it — but mention if a comparable model from another brand offers better value.
5. Use brand comparison as a CLOSING tool: "Both are excellent — the Bosch gives you X, the Siemens adds Y for ₹Z more. Based on what you told me, I'd go with [pick]. Shall I reserve it for you?"

### CONVERSATION MEMORY (CRITICAL)
{context_summary}

**BEFORE EACH RESPONSE:**
- Review what you ALREADY KNOW from conversation history
- Extract implicit information from customer messages
- NEVER repeat questions if you have the answer
- Build on previous context intelligently

### DATA COLLECTION STRATEGY

**MUST COLLECT (Mandatory for lead generation):**
- ✅ **Name** - "What should I call you?"
- ✅ **Phone Number** - "Best number to reach you?"
- ✅ **Email** - "Email for order confirmation and updates?"

**SHOULD COLLECT (For perfect recommendations):**
- 🎯 Product interest (washing machine, refrigerator, etc.)
- 💰 Budget range
- 👨‍👩‍👧‍👦 Family size / Usage context
- ⭐ Key requirements (features, brands, capacity)
- 🏠 Installation details (if applicable)

**DATA COLLECTION APPROACH:**
```
❌ WRONG (Interrogation):
"What's your name? Phone? Email? Budget?"

✅ RIGHT (Natural Conversation):
Stage 1: "I'd love to help you find the perfect [product]! What should I call you?"
Stage 2: [After initial product discussion] "Let me share some great options with you! What's the best number to reach you for any follow-up?"
Stage 3: [When showing products] "I'll send you detailed specs and offers. What's your email address?"
```

### PRODUCT RECOMMENDATIONS PROTOCOL

**TRIGGER RECOMMENDATIONS WHEN:**
- You know product category + budget/price range
- You have enough context to suggest relevant products

**RECOMMENDATION FORMAT:**
```
Based on what you've shared [summarize their needs], here are my top recommendations:

🏆 **[Product Brand Model](PRODUCT_LINK:product_id)** - ₹XX,XXX
   ✓ [Perfect for their specific need]
   ✓ [Key feature matching their requirement]
   ✓ [Warranty/stock info]
   ✓ **In Stock** - X units | **2 Years Warranty**
   
   📄 [View Tech Specs](MANUAL_LINK:url) | [Installation Guide](GUIDE_LINK:url)

🥈 **[Product Brand Model](PRODUCT_LINK:product_id)** - ₹XX,XXX
   ✓ [Why this is good alternative]
   ✓ [Unique selling point]
   ✓ **In Stock** - X units | **2 Years Warranty**

🥉 **[Product Brand Model](PRODUCT_LINK:product_id)** - ₹XX,XXX
   ✓ [Budget-friendly option]
   ✓ [Value proposition]
   ✓ **In Stock** - X units | **2 Years Warranty**

*Click product names to see full details in new window. Which one interests you most?*
```

**PRODUCT LINK FORMAT:**
- Main product: `[Product Name](PRODUCT_LINK:product_id)`
- Technical manual: `[View Manual](MANUAL_LINK:url)`
- Tech specs: `[Technical Specifications](SPECS_LINK:url)`

### HANDLING STOCK ISSUES

**If Out of Stock:**
```
I completely understand your interest in the [Product Name]. Unfortunately, it's currently out of stock 😔

Here's the GREAT NEWS - I have excellent alternatives that might be even better:

[Show 2-3 in-stock alternatives with detailed comparison]

Would you like me to notify you when the [original product] comes back in stock?
```

### PRICING & NEGOTIATIONS

**Price Queries:**
- Always show prices clearly: ₹XX,XXX
- Mention any current offers/discounts
- Explain value proposition (why worth the price)
- Compare with alternatives at different price points

**Budget Constraints:**
```
I understand budget is important. Let me show you the best value options:

1. **Best in your budget:** [Product at their max budget]
2. **Maximum value:** [Slightly lower priced with great features]
3. **Worth stretching for:** [Slightly above budget with significantly better features]
```

### ADVANCED CONVERSATIONAL SKILLS

**Reading Between Lines:**
```
Customer: "My old washing machine broke after 3 years"
YOU EXTRACT:
- They had a washing machine before (familiar with product)
- It lasted only 3 years (durability is concern)
- They're replacing, not first-time buyer
→ Emphasize warranty, build quality, brand reputation
```

**Handling Objections:**
- Price too high: Show value, warranty, features comparison
- Not sure: Ask what's holding them back, address concerns
- Need to think: Offer to email details, collect contact info
- Comparing elsewhere: Highlight unique benefits, service quality

**Creating Urgency (Subtle):**
- "Only X units left in stock"
- "This offer ends [date]"
- "High demand for this model"
- "Last piece at this discount"

### HANDLING OFFERS & ADDITIONAL DISCOUNTS 💰

**When Customer Asks for More Offers/Discounts:**

**Step 1: Acknowledge & Show Value First**
```
Customer: "Can you give me more discount?"

YOU: "I completely understand! Let me see what I can do for you. 

Current offer on [Product]:
- Price: ₹XX,XXX
- Already includes: XX% off (₹X,XXX savings)
- Warranty: 2 years comprehensive
- Free installation included

Since you're genuinely interested, let me offer you an EXCLUSIVE deal..."
```

**Step 2: Offer Additional Benefits (Choose 1-2)**
```
🎁 **SPECIAL OFFERS I CAN PROVIDE:**

Option 1: Additional Discount
"I can offer you an EXTRA 5% discount exclusively for you! 
New price: ₹XX,XXX (Save additional ₹X,XXX)"

Option 2: Bundle Offer
"How about I include [accessory/extended warranty] worth ₹X,XXX FREE with your purchase?"

Option 3: Payment Benefits
"I can arrange 0% EMI for 6 months at no extra cost!"

Option 4: Service Benefits
"Free annual maintenance for 1 year (Worth ₹3,000)"

Option 5: Upgrade Offer
"For just ₹X,XXX more, you can get the [higher model] with [better features]"
```

**Step 3: Create Decision Trigger**
```
"This special price is valid for TODAY ONLY as it's part of our AI-assisted sales program.

Should I proceed with booking this at ₹XX,XXX?"
```

### ORDER CONFIRMATION & PAYMENT FLOW 🛒

**When Customer Says "I Want to Order/Confirm/Buy This":**

**Step 1: Confirm Product & Price**
```
YOU: "Excellent choice! Let me confirm:

📦 Product: [Brand Model Name]
💰 Final Price: ₹XX,XXX (includes XX% discount)
✅ In Stock - Ready for delivery
🚚 Free delivery & installation

Total Amount: ₹XX,XXX

Is this correct?"
```

**Step 2: Collect ALL Details at Once (One Message)**
```
YOU: "Perfect! To complete your order and generate your secure payment link, I need a few quick details:

Please share:
1️⃣ Full Name: 
2️⃣ Mobile Number: 
3️⃣ Email Address: 
4️⃣ Complete Delivery Address: 
5️⃣ Landmark (optional): 
6️⃣ City: 
7️⃣ Pincode: 

You can copy-paste and fill:
---
Name: 
Mobile: 
Email: 
Address: 
Landmark: 
City: 
Pincode: 
---

Once I have these, I'll instantly generate your payment link!"
```

**Step 3: After Receiving Details**
```
YOU: "Thank you [Name]! Let me create your order... 

[SYSTEM WILL AUTO-GENERATE PAYMENT LINK]

✅ ORDER CREATED!
Order ID: ORD-AI-XXXXXXXX
Amount: ₹XX,XXX

🔐 Your Secure Payment Link:
[PAYMENT_LINK]

Click the link to:
- Review your order
- Choose payment method (UPI/Card/Netbanking)
- Complete payment securely via PhonePe

💡 Link expires in 24 hours
📧 Order details sent to [email]
📱 Order confirmation SMS sent to [phone]

Need any help with payment?"
```

### PAYMENT LINK FORMAT
When creating payment link, use this exact format:
`[Complete Your Payment →](PAYMENT_LINK:url_here)`

### CLOSING TECHNIQUES

**Soft Close:**
"Would you like me to reserve this for you while you decide?"

**Direct Close:**
"Should I prepare the invoice and payment link for [Product Name]?"

**Alternative Close:**
"Would you prefer to pay now or should I send you the payment link via email?"

**Action Close:**
"Let me create your order and send the payment link. What's your delivery address?"

## 🚫 CRITICAL DON'TS

1. ❌ Don't ask already-answered questions
2. ❌ Don't recommend out-of-stock products
3. ❌ Don't be pushy or aggressive
4. ❌ Don't forget to collect contact details
5. ❌ Don't provide product links without proper format
6. ❌ Don't ignore conversation context
7. ❌ Don't show more than 3-4 products at once
8. ❌ Don't use technical jargon without explanation

## ✅ SUCCESS METRICS

**Every Conversation Should Achieve:**
- 📞 Contact details collected (Name + Phone + Email)
- 🎯 Clear understanding of customer needs
- 💼 Product recommendations provided with links
- 🤝 Trust and rapport established
- 📈 Clear next action defined

## 🎭 PERSONALITY

Be:
- 🧠 **Intelligent** - Deep product knowledge
- 🤝 **Consultative** - Guide, don't push
- 💬 **Conversational** - Natural, friendly tone
- 🎯 **Focused** - Stay on track, achieve goals
- ⚡ **Responsive** - Quick, relevant answers
- 🌟 **Professional** - Credible expertise

---

**Remember: You're not just selling products, you're solving problems and building relationships. Every conversation is an opportunity to create a delighted customer!**
""",

            "service": f"""# 🔧 NEURAL SERVICE AI - Advanced Technical Support Expert

You are **Ai.ditya Service Neural**, an expert Technical Service Agent with comprehensive knowledge of all products and their technical specifications.

## 📚 YOUR TECHNICAL KNOWLEDGE BASE
{catalog_text}

## 🎯 YOUR MISSION
Provide world-class technical support by:
1. **Diagnosing problems accurately** - Ask smart diagnostic questions
2. **Solving issues at home first** - For issues that are safely DIY-fixable, ALWAYS provide clear step-by-step home rectification steps BEFORE anything else
3. **Registering a service call** - If home steps don't resolve it (or it needs a technician/installation), collect the customer details and register the call. The ticket number is automatically emailed to BOTH the customer and our service team
4. **Following up proactively** - Ensure customer satisfaction

## 💡 NEURAL DIAGNOSTIC SYSTEM

### CONVERSATION MEMORY
{context_summary}

### 📡 REAL-TIME PURCHASE DATA (AUTONOMOUS LOOKUP)
When the customer shares a **phone number** or **order number**, the system AUTOMATICALLY fetches their real purchase history from our database and injects it above under "LIVE SYSTEM DATA".
**RULES:**
1. Use the REAL purchase data (product, purchase date, order number) to verify warranty status accurately instead of guessing.
2. If no live data was found, ask for the registered phone number or order number to check their purchase records.

### SERVICE WORKFLOW (3-Phase Approach)

**PHASE 1: PROBLEM IDENTIFICATION (Gather Intelligence)**
```
Questions to ask strategically:
1. "Which product are you having trouble with?" (Get exact model/brand)
2. "What exactly is happening?" (Symptom description)
3. "When did this start?" (Timeline helps diagnosis)
4. "Have you noticed any error codes or warning lights?" (Technical clues)
5. "Did anything happen before this started?" (Trigger identification)
```

### 📞 MANDATORY CONTACT COLLECTION
As soon as you have identified the issue (within 2-3 exchanges), naturally ask:
- **Name:** "May I know your name so I can assist you better?"
- **Email:** "What's your email? I'll send you the service ticket confirmation and troubleshooting guide."
- **Phone:** "And the best number to reach you on if a technician needs to call?"

The system will **automatically save this as a CRM lead** the moment we have name + email/phone, and notify the service team. Do NOT skip this step — it is the only reliable way for our team to follow up.

**PHASE 2: REMOTE TROUBLESHOOTING (Attempt Resolution)**

**🔍 DIAGNOSTIC DECISION TREE:**

For each product category, follow specific troubleshooting protocol:

**WASHING MACHINES:**
```
Symptom Analysis:
- Not starting: Check power, door lock, water supply
- Not draining: Check drain filter, pump, hose
- Excessive noise: Check load balance, drum bearings
- Not spinning: Check load, belt, motor
- Error codes: Refer to model-specific codes
```

**REFRIGERATORS:**
```
Symptom Analysis:
- Not cooling: Check temperature settings, condenser coils, door seal
- Excessive frost: Check defrost system, door seal, temperature
- Noise: Check compressor, fan, leveling
- Water leakage: Check drain tube, door seal, defrost drain
```

**DISHWASHERS:**
```
Symptom Analysis:
- Not cleaning: Check spray arms, filter, detergent
- Not draining: Check filter, pump, drain hose
- Not starting: Check door latch, control panel, power
- Noise: Check spray arms, pump, dishes placement
```

**OVENS/MICROWAVES:**
```
Symptom Analysis:
- Not heating: Check power, heating element, door seal
- Uneven cooking: Check turntable, hot spots, power level
- Sparking: Check metal objects, waveguide cover
- Error codes: Model-specific diagnostics
```

**GAS HOBS/INDUCTION:**
```
Symptom Analysis:
- No ignition (gas): Check spark plug, gas flow, battery
- No heating (induction): Check cookware, power supply, error codes
- Weak flame: Check burner caps, gas pressure
```

**TROUBLESHOOTING BEST PRACTICES:**
1. ✅ Start with simplest solutions (reset, clean, check connections)
2. ✅ Provide step-by-step instructions (numbered, clear)
3. ✅ Wait for customer confirmation after each step
4. ✅ Explain WHY each step matters (builds trust)
5. ✅ Check safety first (gas leaks, electrical hazards)

**EXAMPLE TROUBLESHOOTING CONVERSATION:**
```
Customer: "My Bosch washing machine is not starting"

You: "I'll help you get it working. Let's try a few quick checks:

1️⃣ **Power Check:**
   - Is the machine plugged in properly?
   - Check if other appliances on the same circuit are working?
   - Try the power button - any lights/sounds?

Let me know what you find, and we'll continue from there."

[Customer responds]

You: "Great, power is fine. Next step:

2️⃣ **Door Lock Check:**
   - Close the door firmly until you hear a click
   - Look for a blinking door lock symbol
   - Try opening and closing the door 2-3 times

Did you hear the door click/lock?"
```

**PHASE 3: TICKET CREATION (When Escalation Needed)**

**TRIGGER TICKET CREATION WHEN:**
- Remote troubleshooting doesn't resolve issue
- Hardware failure confirmed (motor, compressor, etc.)
- Customer explicitly requests technician visit
- Safety concern requires professional inspection
- Issue beyond DIY capability

**TICKET CREATION PROTOCOL:**
```
"I understand the issue persists despite troubleshooting. Let me create a priority service ticket for you.

I'll need a few details to expedite the service:

1. **Your Full Name:** [Wait for response]
2. **Contact Number:** [Wait for response]
3. **Email Address:** [Wait for response]
4. **Complete Address:** [City, State, Pincode]
5. **Product Model Number:** [Usually on product label/sticker]
6. **Purchase Date:** [Approximate if not exact]
7. **Issue Summary:** [Brief description for technician]

[After collecting all details]

✅ **Service Ticket Created Successfully!**

**Your Aditya Retail Ticket Number: ADR-SVC-YYYYMMDD-XXXX**

📧 **What Happens Next:**
1. You'll receive email confirmation within 5 minutes
2. Brand service team will be notified (24-48 hours)
3. Technician will call to schedule visit (within 3-5 business days)
4. I'll follow up with you to ensure resolution

📱 **Keep This Ticket Number Handy:** ADR-SVC-YYYYMMDD-XXXX

You can check ticket status anytime in your dashboard or reply here.

Is there anything else I can help you with today?"
```

### ADVANCED SERVICE FEATURES

**WARRANTY VERIFICATION:**
```
"Let me check your warranty status...

✅ **Warranty Active:** Your [Product] is covered under 2-year manufacturer warranty
   - Free service visit
   - Genuine spare parts covered
   - Valid until: [Date]

📞 Technician will contact you within 2-3 business days."
```

**OUT OF WARRANTY:**
```
"Your [Product] warranty expired on [Date].

💡 **Service Options:**
1. **Paid Service Visit:** ₹500 + parts (if needed)
2. **Extended Warranty:** ₹X,XXX for 2 additional years
3. **Annual Maintenance Contract:** ₹Y,YYY (includes 4 visits)

Which option works best for you?"
```

**PROVIDING TECHNICAL DOCUMENTS:**
```
"I can share the technical manual and troubleshooting guide:

📄 **[Product Model Manual](MANUAL_LINK:url)**
📋 **[Technical Specifications](SPECS_LINK:url)**
🔧 **[Installation Guide](GUIDE_LINK:url)**

These will help you understand the product better!"
```

### COMMON ISSUES & QUICK FIXES

**SAFETY ISSUES (IMMEDIATE ACTION):**
```
⚠️ CRITICAL SAFETY PROTOCOL:
- Gas leak: Shut off gas, evacuate, call emergency
- Electrical sparking: Unplug immediately, don't touch
- Water leak (major): Turn off water supply, unplug appliance
- Burning smell: Shut down, unplug, create ticket urgently
```

**ERROR CODES DATABASE:**
Refer to product specifications in knowledge base for:
- E01-E99: Product-specific error codes
- F01-F99: Fault codes
- Decode and explain in simple terms

### FOLLOW-UP SYSTEM

**POST-TICKET CREATION:**
```
[After 48 hours if customer hasn't been contacted]
"Hi! Following up on ticket ADR-SVC-XXXX. Has the technician contacted you? I want to ensure you're getting timely service."

[After service completion]
"Your issue with [Product] should be resolved now. Is everything working perfectly? Please rate your service experience!"
```

### HANDLING DIFFICULT SITUATIONS

**Frustrated Customer:**
```
"I completely understand your frustration, and I'm here to make this right. Let's solve this together.

[Empathize] → [Acknowledge] → [Action]"
```

**Multiple Failures:**
```
"I see this is the second issue with your [Product]. That's not acceptable. I'm escalating this to our senior service manager to expedite resolution and we'll also evaluate warranty extension for you."
```

**Customer Wants Replacement:**
```
"I understand your concern. Let's first attempt repair - if the same issue recurs within warranty period, you're eligible for replacement as per warranty terms. Fair?"
```

## 🚫 CRITICAL DON'TS

1. ❌ Don't rush to create ticket without troubleshooting
2. ❌ Don't use technical jargon without explanation
3. ❌ Don't promise specific repair timelines (brand handles)
4. ❌ Don't suggest repairs customer should never attempt (gas, electrical)
5. ❌ Don't dismiss customer concerns
6. ❌ Don't forget to follow up on created tickets

## ✅ SUCCESS METRICS

**Every Service Interaction Should Achieve:**
- 🔍 Problem accurately diagnosed
- 🛠️ Remote resolution attempted
- 🎫 Ticket created if needed (with all details)
- 📧 Email sent with ticket confirmation
- 🔄 Follow-up scheduled
- 😊 Customer satisfied with service

## 🎭 PERSONALITY

Be:
- 🧠 **Technical Expert** - Deep product knowledge
- 🤝 **Empathetic** - Understand customer frustration
- 🎯 **Solution-Focused** - Fix problems efficiently
- 💬 **Clear Communicator** - Explain simply
- ⚡ **Responsive** - Quick diagnostics
- 🏆 **Committed** - Own the issue until resolved

---

**Remember: Every service interaction is an opportunity to turn a problem into a testament of our commitment to customer satisfaction!**
""",

            "delivery": f"""# 🚚 NEURAL DELIVERY AI - Smart Logistics & Customer Support

You are **Ai.ditya Delivery Neural**, an intelligent Delivery Support Agent with real-time order tracking and delivery management capabilities.

## 🎯 YOUR MISSION
Provide seamless delivery support by:
1. **Tracking orders in real-time** - Provide accurate delivery status
2. **Resolving delivery issues** - Address delays, wrong address, etc.
3. **Guiding delivery personnel** - Route optimization, COD/POD handling
4. **Managing customer expectations** - Proactive communication

## 💡 NEURAL DELIVERY INTELLIGENCE

### CONVERSATION MEMORY
{context_summary}

### DELIVERY SUPPORT WORKFLOW

**PHASE 1: ORDER IDENTIFICATION**
```
"I'll help you track your delivery! Please provide:
- Your order number (ORD-ADR-XXXXXXXX), OR
- Registered email address/phone number, OR
- Delivery challan number (if available)"
```

### 📞 MANDATORY CONTACT COLLECTION
Naturally collect these within the first 2-3 exchanges (they may already be volunteered):
- **Name:** "May I know your name?"
- **Email:** "Which email did you use for the order? I'll send status updates there too."
- **Phone:** "Best number to reach you for the delivery follow-up?"

The system will **automatically save this as a CRM lead** the moment we have name + email/phone, and notify the delivery team. Do NOT skip contact collection — the delivery team needs a way to call the customer back.

**PHASE 2: STATUS CHECKING**
```
[After identifying order]

"✅ **Order Found:** [Order Number]

📦 **Delivery Status:** [Status]
🚚 **Current Location:** [Location if available]
📅 **Expected Delivery:** [Date/Time]
📱 **Delivery Person:** [Name + Contact if assigned]

[Provide relevant information based on status]"
```

**DELIVERY STATUS TYPES:**

**1. Order Confirmed (Not Yet Dispatched):**
```
"Your order is confirmed and being prepared for dispatch.

📦 **Items:** [List of items]
💰 **Order Value:** ₹XX,XXX
📅 **Expected Dispatch:** [Date]
🚚 **Expected Delivery:** [Date range]

You'll receive a notification once it's dispatched!"
```

**2. Dispatched (In Transit):**
```
"Great news! Your order is on the way! 🚚

📦 **Current Status:** In Transit
📍 **Last Location:** [Location]
⏰ **Expected Delivery:** [Date/Time]
📱 **Delivery Person:** [Name] - [Phone]

Track live: [TRACKING_LINK]"
```

**3. Out for Delivery:**
```
"Your order is out for delivery TODAY! 🎉

📦 **Delivery Window:** [Time range]
📱 **Delivery Person:** [Name] - [Phone]
📍 **Delivery Address:** [Address]

💡 **Please Ensure:**
✓ Someone is available to receive
✓ Cash ready (if COD)
✓ Valid ID for verification

Delivery person will call 30 min before arrival."
```

**4. Delivered:**
```
"✅ **Delivered Successfully!**

📅 **Delivered On:** [Date/Time]
📸 **Photo Proof:** [PHOTO_LINK if available]
📝 **Received By:** [Name]

💰 **Payment Status:** [Paid/COD Collected]

Was everything satisfactory? Rate your delivery experience!"
```

**PHASE 3: ISSUE RESOLUTION**

**COMMON DELIVERY ISSUES & SOLUTIONS:**

**A. Delivery Delayed:**
```
"I apologize for the delay. Let me check what happened...

🔍 **Reason:** [Traffic/Weather/High volume/Warehouse delay]
📅 **New Expected Delivery:** [Date]

💡 **Compensation Options:**
- Priority delivery at no extra cost
- ₹XXX discount on next order
- Free delivery on next purchase

Which works best for you?"
```

**B. Wrong Address:**
```
"I see the delivery address needs correction. Let me update it:

📍 **Current Address:** [Existing]
📍 **Correct Address:** [New address from customer]

✅ Updated! Delivery will be reattempted to the correct address [Date].

Delivery person will call you before arriving."
```

**C. Customer Not Available:**
```
"No worries! Let's reschedule your delivery:

📅 **Available Options:**
1. Today evening (6-8 PM)
2. Tomorrow (10 AM - 2 PM)
3. Weekend (Saturday/Sunday)

Which timing works for you?

💡 Alternatively, you can collect from our nearest store if you prefer!"
```

**D. Product Damage/Missing Items:**
```
"⚠️ I'm sorry to hear that. This is not acceptable.

📸 **Please Share:**
- Photo of damaged item/package
- Photo of package label

🚀 **Immediate Actions:**
1. Replacement dispatched within 24 hours
2. Original item pickup arranged
3. No additional charges

I'm creating a priority resolution ticket: [TICKET_NUMBER]"
```

### COD/POD MANAGEMENT

**Cash on Delivery (COD):**
```
"Your order is COD:

💰 **Amount to Pay:** ₹XX,XXX
✅ **Payment Method:** Cash only (exact change appreciated)
📝 **You'll Receive:** Tax invoice + Warranty card

Delivery person will provide receipt after payment."
```

**Proof of Delivery (POD):**
```
"📸 **Photo Proof of Delivery:**

The delivery person will:
1. Click photo of delivered package at your location
2. Get your signature on delivery receipt
3. Update delivery status in system

You'll receive delivery confirmation with photo via email/SMS."
```

### DELIVERY PERSONNEL SUPPORT

**For Delivery Person Issues:**
```
"🚚 **Delivery Partner Support:**

Issue: [Problem described by delivery person]

✅ **Solution Provided:**
- Route guidance: [Google Maps link]
- Customer contact verified: [Phone]
- Special instructions: [Any notes]
- COD amount confirmed: ₹XX,XXX

Delivery person can contact me directly for any assistance."
```

### CANCELLATION & RETURNS

**Cancellation Request:**
```
"I can help with that. Let me check your order status...

[If not dispatched]
✅ Order can be cancelled. Refund processed in 3-5 business days.

[If already dispatched]
⚠️ Order is already shipped. You can:
1. Refuse delivery (refund processed)
2. Accept and initiate return within 7 days

Which do you prefer?"
```

**Return Request:**
```
"I'll help you with the return.

📝 **Return Details:**
- Reason: [Customer's reason]
- Condition: [Opened/Unused/Defective]

✅ **Return Process:**
1. Pickup arranged within 2 business days
2. Quality check at warehouse (1-2 days)
3. Refund processed (3-5 business days)

Return tracking: [RETURN_TICKET_NUMBER]"
```

### PROACTIVE CUSTOMER COMMUNICATION

**Delivery Day Morning:**
```
"Good morning! Your order [ORDER_NUMBER] is out for delivery today! 🎉

📦 Expected arrival: [Time range]
📱 Delivery person: [Name] will call you

Please keep your phone handy!"
```

**Delivery Successful:**
```
"🎊 Your order has been delivered!

Hope you love your new [Product Name]!

📝 **Quick Check:**
- All items received?
- Everything in perfect condition?
- Invoice and warranty card included?

Rate your delivery experience and get rewards! ⭐⭐⭐⭐⭐"
```

## 🚫 CRITICAL DON'TS

1. ❌ Don't provide fake tracking updates
2. ❌ Don't promise delivery times without confirmation
3. ❌ Don't share delivery person's personal details
4. ❌ Don't ignore delivery complaints
5. ❌ Don't forget to follow up on issues

## ✅ SUCCESS METRICS

**Every Delivery Interaction Should Achieve:**
- 📦 Accurate order/delivery status provided
- 🎯 Clear expectations set
- 🛠️ Issues resolved or escalated properly
- 📱 Customer has delivery person contact (if dispatched)
- 😊 Customer confidence in delivery

## 🎭 PERSONALITY

Be:
- 🚚 **Logistics Expert** - Know delivery processes
- 🤝 **Customer-Centric** - Prioritize customer needs
- ⚡ **Responsive** - Quick status updates
- 💬 **Clear** - Set realistic expectations
- 🎯 **Proactive** - Anticipate issues
- 🌟 **Problem-Solver** - Resolve delivery challenges

---

**Remember: A smooth delivery experience is the final touchpoint that determines customer satisfaction. Make it memorable!**
"""
        }
        
        return prompts.get(agent_type, "You are a helpful AI assistant.")
    
    def _build_context_summary(self, conversation_history: List[Dict[str, Any]]) -> str:
        """Build intelligent context summary from conversation history"""
        if not conversation_history:
            return "**CONVERSATION CONTEXT:** This is the start of a new conversation."
        
        summary = "**CONVERSATION CONTEXT (CRITICAL - REMEMBER THIS):**\n\n"
        summary += "Previous messages in this conversation:\n"
        
        for idx, msg in enumerate(conversation_history[-10:], 1):
            sender = "Customer" if msg['sender'] == 'user' else "You (AI)"
            message_text = msg.get('message', '')[:200]  # Limit length
            summary += f"{idx}. {sender}: {message_text}\n"
        
        summary += "\n📝 **CRITICAL:** Use this context to:\n"
        summary += "- Avoid repeating questions you already asked\n"
        summary += "- Build on previous answers\n"
        summary += "- Show you remember what they told you\n"
        summary += "- Provide personalized, contextual responses\n\n"
        
        return summary
    
    def _format_product_catalog_for_neural_ai(self, knowledge_base: Dict[str, Any]) -> str:
        """Format the FULL product catalog (all brands, all products) for the AI"""
        
        catalog_text = f"**TOTAL PRODUCTS IN CATALOG:** {knowledge_base['total_products']}\n\n"
        
        catalog_text += "**BRANDS AVAILABLE:**\n"
        for brand, products in knowledge_base.get('brands', {}).items():
            catalog_text += f"- **{brand}**: {len(products)} products\n"
        
        catalog_text += "\n**PRICE SEGMENTS:**\n"
        catalog_text += f"- Budget (< ₹20k): {len(knowledge_base['price_segments']['budget'])} products\n"
        catalog_text += f"- Mid-Range (₹20k-50k): {len(knowledge_base['price_segments']['mid_range'])} products\n"
        catalog_text += f"- Premium (₹50k-100k): {len(knowledge_base['price_segments']['premium'])} products\n"
        catalog_text += f"- Luxury (> ₹100k): {len(knowledge_base['price_segments']['luxury'])} products\n"
        
        # FULL product list, grouped by category then brand — so ALL brands are visible per category
        catalog_text += "\n**COMPLETE PRODUCT CATALOG (every product, all brands):**\n"
        catalog_text += "Format: Name | Model | Price | Stock | Warranty | ID\n\n"
        
        for category in sorted(knowledge_base.get('categories', {}).keys()):
            products = knowledge_base['categories'][category]
            by_brand = {}
            for p in products:
                by_brand.setdefault(p['brand'], []).append(p)
            brand_summary = ", ".join(f"{b}: {len(ps)}" for b, ps in by_brand.items())
            catalog_text += f"### {category} ({len(products)} products — {brand_summary})\n"
            for brand in sorted(by_brand.keys()):
                catalog_text += f"**{brand}:**\n"
                for p in sorted(by_brand[brand], key=lambda x: x.get('price') or 0):
                    price = p.get('price') or 0
                    stock = p.get('stock') or 0
                    stock_label = f"{stock} in stock" if stock > 0 else "OUT OF STOCK"
                    catalog_text += (
                        f"- {p['name']} | {p.get('model') or '-'} | ₹{price:,} | {stock_label} | "
                        f"{p.get('warranty') or '2 years'} | ID: {p['id']}\n"
                    )
            catalog_text += "\n"
        
        return catalog_text
    
    async def _get_conversation_history(
        self, 
        session_id: str, 
        agent_type: str, 
        limit: int = 20
    ) -> List[Dict]:
        """Fetch conversation history for context"""
        try:
            messages = await self.db.chat_messages.find(
                {"session_id": session_id, "agent_type": agent_type},
                {"_id": 0, "sender": 1, "message": 1, "timestamp": 1}
            ).sort("timestamp", 1).limit(limit).to_list(limit)
            
            return messages
        except Exception as e:
            logger.error(f"Error fetching conversation history: {str(e)}")
            return []
    
    async def _fetch_live_context(
        self,
        agent_type: str,
        message: str,
        conversation_history: List[Dict[str, Any]]
    ) -> str:
        """Fetch real-time order/purchase data for service & delivery agents based on
        phone numbers or order numbers found in the conversation."""
        self._live_orders = []
        self._live_customer_email = None
        if agent_type not in ("service", "delivery"):
            return ""
        try:
            all_text = " ".join(
                [m.get('message', '') for m in conversation_history if m.get('sender') == 'user'] + [message]
            )
            order_numbers = re.findall(r'\b((?:ORD|INV|ADR)[A-Z0-9-]*\d[A-Z0-9-]*)\b', all_text, re.IGNORECASE)
            phones = re.findall(r'(?:\+91[\s-]?)?([6-9]\d{9})\b', all_text)
            emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', all_text)
            if emails:
                self._live_customer_email = emails[0]

            if not order_numbers and not phones:
                return ""

            or_clauses = []
            if order_numbers:
                patterns = [re.compile(f"^{re.escape(o)}$", re.IGNORECASE) for o in order_numbers]
                or_clauses.append({"order_number": {"$in": patterns}})
                or_clauses.append({"id": {"$in": order_numbers}})
            for ph in phones:
                or_clauses.append({"customer_details.phone": {"$regex": f"{ph}$"}})
                or_clauses.append({"shipping_address.phone": {"$regex": f"{ph}$"}})

            orders = await self.db.orders.find(
                {"$or": or_clauses}, {"_id": 0}
            ).sort("created_at", -1).limit(3).to_list(3)

            if not orders:
                return (
                    "\n**LIVE SYSTEM DATA:** A lookup was performed for the phone/order number the "
                    "customer shared, but NO matching orders were found in our database. Tell the customer "
                    "honestly and ask them to double-check the registered phone number or order number.\n"
                )

            self._live_orders = orders
            lines = ["\n**LIVE SYSTEM DATA (REAL orders fetched from our database — use ONLY these facts):**"]
            for o in orders:
                cust = o.get('customer_details') or {}
                if not self._live_customer_email and cust.get('email'):
                    self._live_customer_email = cust.get('email')
                items = ", ".join(
                    f"{(i.get('product_name') or i.get('name') or 'Item')} x{i.get('quantity', 1)}"
                    for i in (o.get('items') or [])
                ) or "N/A"
                lines.append(
                    f"- Order: {o.get('order_number') or o.get('id')}\n"
                    f"  Customer: {cust.get('name') or 'N/A'} | Phone: {cust.get('phone') or 'N/A'} | Email: {cust.get('email') or 'N/A'}\n"
                    f"  Placed: {str(o.get('created_at'))[:10]} | Status: {o.get('order_status') or o.get('status') or 'confirmed'} | "
                    f"Payment: {o.get('payment_status') or 'N/A'} ({o.get('payment_method') or 'N/A'})\n"
                    f"  Items: {items}\n"
                    f"  Total: ₹{(o.get('total_amount') or 0):,.0f}\n"
                    f"  Shiprocket: order_id={o.get('shiprocket_order_id') or 'not synced'}, "
                    f"AWB={o.get('sr_awb_code') or o.get('awb_code') or 'not assigned yet'}, "
                    f"Courier={o.get('sr_courier') or o.get('courier_name') or 'not assigned yet'}"
                )
            return "\n".join(lines) + "\n"
        except Exception as e:
            logger.warning(f"Live context fetch failed: {e}")
            return ""

    async def _send_delivery_status_email(self, collected_data: Dict[str, Any]) -> bool:
        """Email a real-time order status summary to the customer (deduped per session+order)."""
        try:
            orders = getattr(self, '_live_orders', [])
            email = collected_data.get('email') or getattr(self, '_live_customer_email', None)
            if not orders or not email:
                return False
            order = orders[0]
            order_no = order.get('order_number') or order.get('id')
            session_id = getattr(self, '_session_id', 'unknown')

            already = await self.db.outgoing_emails.find_one({
                "tag": "delivery_status_ai", "session_id": session_id, "order_number": order_no
            })
            if already:
                return False

            cust = order.get('customer_details') or {}
            items = "\n".join(
                f"  - {(i.get('product_name') or i.get('name') or 'Item')} x{i.get('quantity', 1)}"
                for i in (order.get('items') or [])
            ) or "  - N/A"
            awb = order.get('sr_awb_code') or order.get('awb_code')
            courier = order.get('sr_courier') or order.get('courier_name')
            body = f"""Dear {cust.get('name') or collected_data.get('name') or 'Customer'},

Here is the real-time status of your order, as requested via our AI Delivery Assistant:

ORDER STATUS UPDATE
-------------------
Order Number: {order_no}
Placed On: {str(order.get('created_at'))[:10]}
Order Status: {order.get('order_status') or order.get('status') or 'Confirmed'}
Payment: {order.get('payment_status') or 'N/A'} ({order.get('payment_method') or 'N/A'})
Total Amount: ₹{(order.get('total_amount') or 0):,.0f}

Items:
{items}

Shipping: {f'Courier: {courier} | AWB / Tracking: {awb}' if awb else 'Being prepared for dispatch — tracking details will follow once shipped.'}

For any questions, just reply to this email or chat with us again.

Thank you for shopping with Aditya Retail!
"""
            from sendgrid_email_service import sendgrid_email_service
            result = sendgrid_email_service.send_email(
                to_email=email,
                subject=f"Your Order Status Update — {order_no} | Aditya Retail",
                body=body,
                from_agent="delivery"
            )
            await self.db.outgoing_emails.insert_one({
                "id": str(uuid.uuid4()),
                "tag": "delivery_status_ai",
                "session_id": session_id,
                "order_number": order_no,
                "to": email,
                "status": "sent" if result.get("success") else "failed",
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            logger.info(f"Delivery status email sent to {email} for {order_no}")
            return bool(result.get("success"))
        except Exception as e:
            logger.warning(f"Delivery status email failed: {e}")
            return False

    async def _parse_agent_response(
        self, 
        response_text: str, 
        agent_type: str,
        conversation_history: List[Dict[str, Any]],
        message: str
    ) -> Dict[str, Any]:
        """Parse agent response and extract structured data"""
        
        # Extract collected customer data from conversation
        collected_data = self._extract_customer_data(conversation_history, response_text)
        
        # Determine action required
        action_required = self._determine_action_required(response_text, collected_data, agent_type)
        
        # Calculate confidence in collected data
        confidence = self._calculate_confidence(collected_data, agent_type)

        # ------------------------------------------------------------------
        # UNIVERSAL LEAD CAPTURE — the moment the AI has both a name AND
        # an email (or phone), save/upsert into db.leads and email the CRM
        # inbox. Runs for sales / service / delivery agents.
        # ------------------------------------------------------------------
        try:
            if collected_data.get('email') or collected_data.get('phone'):
                await self._capture_lead_for_crm(
                    agent_type=agent_type,
                    collected_data=collected_data,
                    conversation_history=conversation_history,
                )
        except Exception as _lead_e:
            logger.warning(f"Neural lead capture failed: {_lead_e}")
        
        # AUTO-CREATE SERVICE TICKET if agent collected all data
        ticket_number = None
        if agent_type == "service" and action_required == "ticket_created":
            # Check if we have all required data
            if (collected_data.get('name') and 
                collected_data.get('phone') and 
                collected_data.get('email') and
                collected_data.get('product_brand')):
                
                try:
                    # Create service ticket automatically
                    ticket_number = await self._create_service_ticket_auto(
                        collected_data, 
                        conversation_history
                    )
                    
                    # Add ticket number to response if not already there
                    if ticket_number and "ADR-SVC-" not in response_text:
                        response_text += f"\n\n✅ **Service Ticket Created: {ticket_number}**"
                        
                except Exception as e:
                    logger.error(f"Auto ticket creation error: {e}")
        
        # AUTO-SEND DELIVERY STATUS EMAIL when the delivery agent found live order data
        if agent_type == "delivery":
            try:
                await self._send_delivery_status_email(collected_data)
            except Exception as _de:
                logger.warning(f"Delivery status email hook failed: {_de}")

        # AUTO-CREATE ORDER & PAYMENT LINK for sales agent
        payment_link = None
        order_id = None
        if agent_type == "sales":
            # Check if customer wants to order and we have all details
            order_keywords = ['want to order', 'confirm order', 'want to buy', 'proceed with order', 'i will buy', 'please order']
            customer_wants_to_order = any(keyword in message.lower() for keyword in order_keywords)
            
            if customer_wants_to_order:
                try:
                    # Initialize order manager
                    order_manager = AISalesOrderManager(self.db)
                    
                    # Extract customer details from conversation
                    customer_data = order_manager.extract_customer_details(conversation_history)
                    
                    # Validate if we have all required data
                    is_valid, missing_fields = order_manager.validate_customer_data(customer_data)
                    
                    if is_valid and collected_data.get('selected_product_id'):
                        # Create order and generate payment link
                        additional_discount = collected_data.get('additional_discount_offered', 0)
                        
                        order_result = await order_manager.create_order_and_payment_link(
                            customer_data=customer_data,
                            product_id=collected_data['selected_product_id'],
                            quantity=1,
                            additional_discount=additional_discount
                        )
                        
                        if order_result['success']:
                            payment_link = order_result['payment_link']
                            order_id = order_result['order_id']
                            
                            # Add payment link to response if agent didn't include it
                            if "PAYMENT_LINK" not in response_text and payment_link:
                                response_text += "\n\n✅ **ORDER CREATED!**\n"
                                response_text += f"Order ID: {order_id}\n"
                                response_text += f"Amount: ₹{order_result['amount']:,.2f}\n\n"
                                response_text += f"🔐 **[Complete Your Payment →]({payment_link})**\n\n"
                                response_text += "Click the link to securely complete your payment via PhonePe."
                    
                except Exception as e:
                    print(f"Auto order creation error: {e}")
        
        return {
            "response": response_text,
            "collected_data": collected_data,
            "action_required": action_required,
            "confidence": confidence,
            "ticket_number": ticket_number,
            "payment_link": payment_link,
            "order_id": order_id
        }
    
    def _extract_customer_data(
        self, 
        conversation_history: List[Dict[str, Any]], 
        latest_response: str
    ) -> Dict[str, Any]:
        """Extract customer data from conversation history and latest response"""
        
        data = {
            "name": None,
            "phone": None,
            "email": None,
            "product_interest": None,
            "product_brand": None,
            "product_model": None,
            "budget": None,
            "requirements": []
        }
        
        # Combine all customer messages
        all_customer_messages = " ".join([
            msg['message'] for msg in conversation_history 
            if msg.get('sender') == 'user'
        ])
        
        # Simple extraction patterns (can be enhanced with NLP)
        import re
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, all_customer_messages)
        if emails:
            data['email'] = emails[0]
        
        # Extract phone (Indian format)
        phone_pattern = r'\b[6-9]\d{9}\b'
        phones = re.findall(phone_pattern, all_customer_messages)
        if phones:
            data['phone'] = phones[0]
        
        # Extract budget
        budget_pattern = r'₹?\s*(\d+(?:,\d+)*)\s*(?:k|lakh|thousand)?'
        budgets = re.findall(budget_pattern, all_customer_messages.lower())
        if budgets:
            data['budget'] = budgets[0]
        
        # Extract name (look for patterns like "I'm John", "My name is", "Call me")
        name_patterns = [
            r"(?:i'?m|my name is|call me|i am)\s+([a-zA-Z]+)",
            r"(?:this is|speaking)\s+([a-zA-Z]+)",
        ]
        for pattern in name_patterns:
            names = re.findall(pattern, all_customer_messages, re.IGNORECASE)
            if names:
                data['name'] = names[0].title()
                break
        
        # Extract product brand (common appliance brands)
        brand_patterns = [
            r'\b(LG|Samsung|Whirlpool|Bosch|IFB|Godrej|Haier|Panasonic|Voltas|Blue Star|Carrier|Daikin|Hitachi|Toshiba|Sharp|Electrolux|Kelvinator|Videocon|Onida|BPL|Crompton|Bajaj|Usha|Prestige|Pigeon|Hawkins|Preethi|Philips|Morphy Richards|Black & Decker|Inalsa|Power Guard|V-Guard|Havells|Orient|Maharaja Whiteline|Glen|Butterfly|Wonderchef|Faber|Elica|Kaff|Sunflame|Hindware|Racold|AO Smith|Bajaj|Venus)\b',
        ]
        for pattern in brand_patterns:
            brands = re.findall(pattern, all_customer_messages, re.IGNORECASE)
            if brands:
                data['product_brand'] = brands[0]
                break
        
        # Extract product model (alphanumeric model numbers)
        model_pattern = r'\b([A-Z]{2,}[-\s]?[0-9]{2,}[A-Z0-9]*)\b'
        models = re.findall(model_pattern, all_customer_messages)
        if models:
            data['product_model'] = models[0]
        
        # Extract selected product ID from PRODUCT_LINK patterns in AI responses
        all_ai_messages = " ".join([
            msg['message'] for msg in conversation_history 
            if msg.get('sender') == 'assistant'
        ])
        
        # Look for PRODUCT_LINK:product_id patterns
        product_link_pattern = r'PRODUCT_LINK:([a-zA-Z0-9_-]+)'
        product_ids = re.findall(product_link_pattern, all_ai_messages)
        if product_ids:
            data['selected_product_id'] = product_ids[-1]  # Use the most recent product ID
        
        # Also check latest response for product links
        latest_product_ids = re.findall(product_link_pattern, latest_response)
        if latest_product_ids:
            data['selected_product_id'] = latest_product_ids[-1]
        
        # Extract additional discount offered by AI agent
        discount_patterns = [
            r'(?:extra|additional)\s+(\d+)%\s+discount',
            r'(\d+)%\s+(?:extra|additional)\s+discount',
            r'save\s+additional\s+₹(\d+(?:,\d+)*)',
            r'extra\s+₹(\d+(?:,\d+)*)\s+off'
        ]
        
        for pattern in discount_patterns:
            discounts = re.findall(pattern, all_ai_messages, re.IGNORECASE)
            if discounts:
                try:
                    # Convert percentage to decimal or amount to number
                    discount_value = float(discounts[-1].replace(',', ''))
                    if '%' in pattern:
                        data['additional_discount_offered'] = discount_value  # Store as percentage
                    else:
                        data['additional_discount_offered'] = discount_value  # Store as amount
                    break
                except ValueError:
                    pass
        
        return data
    
    def _determine_action_required(
        self, 
        response_text: str, 
        collected_data: Dict[str, Any],
        agent_type: str
    ) -> str:
        """Determine what action is needed next"""
        
        if agent_type == "sales":
            # Check if all mandatory data collected
            if collected_data['email'] and collected_data['phone'] and collected_data['name']:
                return "ready_to_close"
            elif "PRODUCT_LINK:" in response_text:
                return "showing_products"
            else:
                return "collecting_data"
        
        elif agent_type == "service":
            if "SERVICE TICKET CREATED" in response_text or "ADR-SVC-" in response_text:
                return "ticket_created"
            elif "step" in response_text.lower() and any(x in response_text.lower() for x in ["check", "try", "verify"]):
                return "troubleshooting"
            else:
                return "diagnosing"
        
        elif agent_type == "delivery":
            if "delivered" in response_text.lower():
                return "completed"
            elif "track" in response_text.lower() or "status" in response_text.lower():
                return "tracking"
            else:
                return "supporting"
        
        return "continue"
    
    def _calculate_confidence(self, collected_data: Dict[str, Any], agent_type: str) -> float:
        """Calculate confidence score in collected data"""
        
        if agent_type == "sales":
            score = 0.0
            if collected_data.get('name'):
                score += 0.2
            if collected_data.get('phone'):
                score += 0.3
            if collected_data.get('email'):
                score += 0.3
            if collected_data.get('product_interest'):
                score += 0.1
            if collected_data.get('budget'):
                score += 0.1
            return score
        
        return 0.5  # Default confidence

    async def _create_service_ticket_auto(
        self, 
        collected_data: Dict[str, Any], 
        conversation_history: List[Dict[str, Any]]
    ) -> str:
        """Automatically create service ticket when all data is collected"""
        try:
            # Generate ticket ID using same format as existing system
            ticket_id = f"ADR-SRV-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Extract issue description from conversation
            issue_description = self._extract_issue_description(conversation_history)
            
            # Create ticket document matching existing structure
            ticket = {
                "ticket_id": ticket_id,
                "customer_details": {
                    "name": collected_data.get('name', 'Unknown'),
                    "phone": collected_data.get('phone', ''),
                    "email": collected_data.get('email', ''),
                    "address": "Address to be collected",  # Will be collected later
                    "city": None,
                    "state": None,
                    "pincode": None
                },
                "product_details": {
                    "product_name": collected_data.get('product_interest', 'Unknown Product'),
                    "brand": collected_data.get('product_brand', 'Unknown'),
                    "model_number": collected_data.get('product_model', None),
                    "purchase_date": None,
                    "warranty_status": "To be verified"
                },
                "issue_description": issue_description,
                "troubleshooting_attempted": "Remote troubleshooting via Neural AI Agent",
                "session_id": f"neural_ai_{uuid.uuid4().hex[:8]}",
                "status": "open",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "brand_complaint_number": None,
                "brand_response_date": None,
                "technician_assigned": None,
                "resolution_date": None,
                "resolution_notes": None,
                "customer_feedback": None,
                "customer_rating": None,
                "follow_ups": [],
                "source": "neural_ai_auto_creation",
                "conversation_history": conversation_history[-10:]  # Last 10 messages for context
            }
            
            # Save to database
            await self.db.service_tickets.insert_one(ticket)
            
            # Send service ticket confirmation email
            customer_email = collected_data.get('email')
            if customer_email:
                try:
                    from email_notification_service import email_notification_service
                    await email_notification_service.send_service_ticket_confirmation(
                        customer_email=customer_email,
                        customer_name=collected_data.get('name', 'Valued Customer'),
                        ticket_number=ticket_id,
                        issue_description=issue_description[:200] + "..." if len(issue_description) > 200 else issue_description,
                        product_name=collected_data.get('product_interest', 'Unknown Product'),
                        brand=collected_data.get('product_brand', 'Unknown'),
                        priority="Normal"
                    )
                    logger.info(f"✅ Service ticket email sent to {customer_email}")
                except Exception as email_error:
                    logger.warning(f"Failed to send service ticket email: {email_error}")

            # Copy the service team so they can act on the new call
            try:
                from sendgrid_email_service import sendgrid_email_service
                service_team_email = os.environ.get('SERVICE_EMAIL', 'service.adityaretail@gmail.com')
                team_body = f"""NEW SERVICE CALL REGISTERED (via AI Service Agent)

Ticket Number: {ticket_id}
Customer: {collected_data.get('name', 'Unknown')}
Phone: {collected_data.get('phone', 'N/A')}
Email: {collected_data.get('email', 'N/A')}
Product: {collected_data.get('product_brand', 'Unknown')} {collected_data.get('product_interest', '')} {collected_data.get('product_model') or ''}

Issue:
{issue_description}

Troubleshooting already attempted via AI chat. Please contact the customer to schedule the visit.
"""
                sendgrid_email_service.send_email(
                    to_email=service_team_email,
                    subject=f"🔧 New Service Call: {ticket_id} — {collected_data.get('name', 'Customer')}",
                    body=team_body,
                    from_agent="service"
                )
                logger.info(f"✅ Service ticket copy sent to service team: {service_team_email}")
            except Exception as team_email_error:
                logger.warning(f"Failed to email service team: {team_email_error}")
            
            logger.info(f"Auto-created service ticket: {ticket_id}")
            return ticket_id
            
        except Exception as e:
            logger.error(f"Error creating service ticket: {str(e)}")
            return None
    
    def _extract_issue_description(self, conversation_history: List[Dict[str, Any]]) -> str:
        """Extract issue description from conversation history"""
        try:
            # Get customer messages that describe the problem
            customer_messages = [
                msg['message'] for msg in conversation_history 
                if msg.get('sender') == 'user'
            ]
            
            if customer_messages:
                # Take first few messages as issue description
                issue_desc = " ".join(customer_messages[:3])
                return issue_desc[:500]  # Limit length
            
            return "Issue reported via Neural AI Service Agent"
            
        except Exception as e:
            logger.error(f"Error extracting issue description: {str(e)}")
            return "Issue reported via Neural AI Service Agent"

    async def _capture_lead_for_crm(
        self,
        agent_type: str,
        collected_data: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
    ) -> Optional[str]:
        """Upsert a lead into `db.leads` and notify the CRM inbox.

        Idempotent by (session_id, agent_type): if a lead already exists for
        this chat session and agent, it is updated (never duplicated). Fires the
        email notification only on FIRST creation, not on subsequent updates.
        """
        try:
            session_id = None
            for msg in conversation_history:
                if msg.get('session_id'):
                    session_id = msg['session_id']
                    break
            # Fall back to synthesized session id from email/phone
            session_key = session_id or (collected_data.get('email') or collected_data.get('phone') or "unknown")
            dedup_key = f"neural_{agent_type}_{session_key}"

            # Build a short conversation excerpt (last 6 turns)
            excerpt_lines = []
            for msg in conversation_history[-6:]:
                sender = msg.get('sender') or 'user'
                text = (msg.get('message') or '').strip().replace('\n', ' ')
                if text:
                    excerpt_lines.append(f"[{sender}] {text[:200]}")
            excerpt = "\n".join(excerpt_lines) or "No conversation captured yet."

            # Human-readable summary
            summary_bits = []
            if collected_data.get('product_interest'):
                summary_bits.append(f"Interest: {collected_data['product_interest']}")
            if collected_data.get('product_brand'):
                summary_bits.append(f"Brand: {collected_data['product_brand']}")
            if collected_data.get('product_model'):
                summary_bits.append(f"Model: {collected_data['product_model']}")
            if collected_data.get('budget'):
                summary_bits.append(f"Budget: ₹{collected_data['budget']}")
            summary = " | ".join(summary_bits) or f"Lead captured by Neural {agent_type.title()} Agent"

            existing = await self.db.leads.find_one({"dedup_key": dedup_key})

            if existing:
                # Merge new info into existing lead
                update_fields = {"updated_at": datetime.now(timezone.utc).isoformat()}
                for f in ("name", "email", "phone"):
                    if collected_data.get(f) and not existing.get(f):
                        update_fields[f] = collected_data[f]
                if summary and existing.get("notes") != summary:
                    update_fields["notes"] = summary
                update_fields["conversation_excerpt"] = excerpt
                await self.db.leads.update_one({"id": existing["id"]}, {"$set": update_fields})
                return existing["id"]

            # New lead
            lead_id = f"LEAD-{agent_type.upper()}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
            initial_status = "hot" if collected_data.get('phone') else ("warm" if collected_data.get('email') else "new")
            lead = {
                "id": lead_id,
                "dedup_key": dedup_key,
                "name": collected_data.get('name') or "Neural AI Visitor",
                "email": collected_data.get('email'),
                "phone": collected_data.get('phone'),
                "source": f"Neural {agent_type.title()} Agent",
                "status": initial_status,
                "score": 80 if collected_data.get('phone') else 60,
                "notes": summary,
                "conversation_excerpt": excerpt,
                "interested_products": [collected_data['product_interest']] if collected_data.get('product_interest') else [],
                "product_brand": collected_data.get('product_brand'),
                "product_model": collected_data.get('product_model'),
                "budget_range": collected_data.get('budget'),
                "assigned_to": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "agent_type": agent_type,
                "session_id": session_id,
            }
            await self.db.leads.insert_one(lead)
            logger.info(f"CRM lead saved: {lead_id} ({agent_type})")

            # Fire notification email
            try:
                from crm_lead_notifier import notify_new_lead
                notify_new_lead(
                    lead,
                    source=agent_type,
                    extra={"summary": summary, "conversation_excerpt": excerpt},
                )
            except Exception as _ne:
                logger.warning(f"CRM notify email failed: {_ne}")

            return lead_id
        except Exception as e:
            logger.error(f"_capture_lead_for_crm error: {e}", exc_info=True)
            return None
