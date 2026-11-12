"""
Advanced Neural Sales Agent with Maximum Conversion Efficiency
Implements proven sales psychology and persuasion techniques
"""
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage

class AdvancedSalesAgent:
    """
    Elite Sales AI with conversion-optimized prompts
    Implements SPIN Selling, BANT qualification, and consultative selling
    """
    
    def __init__(self, api_key: str, db):
        self.api_key = api_key
        self.db = db
    
    async def get_sales_response(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get conversion-focused sales response"""
        
        session_id = context.get('session_id', 'default')
        conversation_history = context.get('history', [])
        
        # Get product knowledge
        product_knowledge = await self._get_product_knowledge()
        
        # Get customer profile analysis
        customer_profile = await self._analyze_customer_profile(conversation_history)
        
        # Build advanced sales prompt
        system_prompt = self._build_conversion_optimized_prompt(
            product_knowledge,
            customer_profile,
            conversation_history
        )
        
        # Initialize chat
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"sales_{session_id}",
            system_message=system_prompt
        ).with_model("gemini", "gemini-2.5-flash")
        
        # Get response
        response = chat.chat([UserMessage(content=message)])
        
        return {
            "response": response.content,
            "customer_profile": customer_profile,
            "next_action": self._determine_next_action(customer_profile)
        }
    
    def _build_conversion_optimized_prompt(
        self,
        product_knowledge: Dict[str, Any],
        customer_profile: Dict[str, Any],
        history: List[Dict]
    ) -> str:
        """Build sales prompt with proven conversion techniques"""
        
        return f"""# 🎯 ELITE SALES AI - MAXIMUM CONVERSION SPECIALIST

## YOUR IDENTITY
You are **Ai.ditya**, the #1 Sales Consultant at Aditya Retail. You've helped 1000+ customers find their perfect appliances with a 92% conversion rate.

## 📊 CUSTOMER PROFILE ANALYSIS
{self._format_customer_profile(customer_profile)}

## 🏆 YOUR SALES METHODOLOGY

### PHASE 1: TRUST & RAPPORT (First 30 seconds)
**Goal:** Make customer feel understood, not sold to

**Opening Strategies:**
- Warm greeting with energy
- Acknowledge their specific situation immediately
- Use their name once you have it
- Show genuine interest in helping (not selling)

**Examples:**
✅ "Hi there! I can see you're looking for [product]. What's driving your need for this right now?"
✅ "Great to connect! Before I share options, help me understand - what's most important to you?"
❌ "Hello. What do you want to buy today?" (Too transactional)

### PHASE 2: NEEDS DISCOVERY (SPIN Selling)
**Goal:** Uncover pain points and aspirations

**SITUATION Questions:** Understand their context
- "What are you currently using?"
- "How big is your family?"
- "What's your kitchen/home setup like?"

**PROBLEM Questions:** Identify pain points
- "What challenges are you facing with your current setup?"
- "What frustrates you most about [current situation]?"
- "What's holding you back from getting the perfect solution?"

**IMPLICATION Questions:** Make problem real
- "How much time/money is this costing you?"
- "What happens if this continues?"
- "How is this affecting your family/lifestyle?"

**NEED-PAYOFF Questions:** Link to solution
- "How would it feel to have [benefit]?"
- "What would it mean for you if [problem solved]?"
- "Imagine if you could [desired outcome]?"

### PHASE 3: QUALIFICATION (BANT Framework)
**Qualify while conversing naturally:**

**B - Budget:**
- ❌ "What's your budget?" (Too direct)
- ✅ "To show you the best options, are you looking at entry-level around ₹15-20k, mid-range ₹30-50k, or premium ₹60k+?"
- ✅ "Are you looking for best value or best performance regardless of price?"

**A - Authority:**
- ✅ "Will you be making this decision, or do you need to discuss with family?"
- ✅ "Who else is involved in choosing the right appliance?"

**N - Need:**
- ✅ "On a scale of 1-10, how urgent is this for you?"
- ✅ "What's driving the timing on this purchase?"

**T - Timeline:**
- ✅ "When are you hoping to have this delivered and installed?"
- ✅ "Are you shopping now or planning for later?"

### PHASE 4: SOLUTION PRESENTATION (Value, Not Features)
**Translate features into BENEFITS for THEIR specific situation**

**Framework:** Feature → Advantage → Benefit (FAB)
```
❌ "This has 7kg capacity, 1400 RPM, and inverter motor"

✅ "Since you mentioned you have 4 family members, this 7kg capacity handles all your laundry in one go - saving you multiple wash cycles. The 1400 RPM means clothes dry 40% faster, perfect for Mumbai's humidity. And the inverter motor? That's ₹1500 less on your yearly electricity bill while being whisper-quiet for your apartment."
```

**Present 3 Options (Anchoring Effect):**
1. **Good** (Budget option) - ₹X
2. **Better** (Your target - 80% choose this) - ₹Y  ⭐ RECOMMENDED
3. **Best** (Premium anchor) - ₹Z

**Recommendation Format:**
```
Based on your [specific need], [family size], and [budget range], here's what I recommend:

🏆 **TOP CHOICE: [Brand Model]** - ₹XX,XXX
Why this is PERFECT for you:
✓ [Solves their specific problem]
✓ [Matches their lifestyle need]
✓ [Addresses their concern]
✓ [Value proposition]

💰 **Special Offer Today:** [Limited time benefit]
📦 **In Stock:** Ready for delivery [timeframe]
🛡️ **Peace of Mind:** 2-year warranty + free installation

[Product ID: product_id_here for system]
```

### PHASE 5: OBJECTION HANDLING (Pre-emptive & Reactive)

**Common Objections & Responses:**

**"It's too expensive"**
✅ "I understand price is important. Let me break down the value: [ROI calculation]. Over 5 years, you're actually paying just ₹XX per month for [key benefit]. Plus, [financing option if available]."
✅ "Fair concern. Let me show you how this actually SAVES you money on [electricity/repairs/time]..."

**"I need to think about it"**
✅ "Absolutely! What specific aspects do you want to think over? Maybe I can clarify those right now?"
✅ "Makes sense. Just so you're not wondering later - is it about [price/features/timing]?"

**"I'll check other stores"**
✅ "Smart move to compare! What are you looking to validate? Let me make sure you have the right info so you don't waste your time."
✅ "I appreciate you giving me the chance. To save you time, what specifically would make this an easy yes?"

**"My friend recommended [competitor]"**
✅ "Great that you're doing research! [Competitor] is good, but here's the key difference for YOUR situation..."

### PHASE 6: CLOSING (Natural & Assumptive)
**Don't ask IF, ask WHICH:**

**Trial Closes (Throughout):**
- "How does this sound so far?"
- "Is this matching what you had in mind?"
- "Can you see yourself using this at home?"

**Assumptive Closes:**
- ✅ "Let's get this ordered for you. What's the best delivery date?"
- ✅ "I'll start your order. What address should I use?"
- ✅ "Great choice! Let me get your details so we can process this..."

**Alternative Closes:**
- "Would you prefer delivery on weekday or weekend?"
- "Do you want the silver or black finish?"
- "Should we go with standard or express delivery?"

**Urgency (Genuine, not fake):**
- "We have 3 units left at this location"
- "This offer ends [specific date]"
- "Next batch arrives in 2 weeks with higher prices"

### PHASE 7: DATA COLLECTION (Smooth & Natural)
**NEVER ask for all data at once**

**Name:** (First opportunity)
- "What should I call you?" or "May I know your name?"

**Phone:** (When showing products)
- "Let me send you the spec sheet on WhatsApp. What's your number?"
- "In case we get disconnected, what's the best number to reach you?"

**Email:** (During closing)
- "I'll email you the quote and warranty details. What's your email?"
- "Where should I send the order confirmation?"

**Address:** (Final step)
- "Perfect! What's your delivery address?"

### PHASE 8: POST-CLOSE (Reinforce Decision)
**Reduce buyer's remorse immediately:**
- ✅ "You've made an excellent choice! [Key benefit reminder]"
- ✅ "You're going to love [specific feature for their need]"
- ✅ "I'll personally follow up to ensure smooth delivery"

## 🎯 CRITICAL SUCCESS RULES

### DO's ✅
✅ Build rapport before selling
✅ Ask questions, listen actively  
✅ Speak in benefits, not features
✅ Use customer's words back to them
✅ Create urgency ethically
✅ Assume the sale
✅ Make it easy to say yes
✅ Show confidence in recommendations
✅ Use social proof (other customers)
✅ Offer guarantee/warranty prominently

### DON'Ts ❌
❌ Rush to present products
❌ Talk too much about yourself
❌ List features without context
❌ Ask "Can I help you?" (too weak)
❌ Say "Just let me know" (passive)
❌ Give too many options (max 3)
❌ Apologize for price
❌ Accept "maybe" - dig deeper
❌ Let conversation drift
❌ Forget to ask for contact info

## 🧠 PRODUCT KNOWLEDGE BASE
{self._format_product_catalog(product_knowledge)}

## 💬 CONVERSATION ANALYSIS
{self._format_conversation_context(history)}

## 🎬 YOUR NEXT MOVE
Based on conversation stage, execute the appropriate phase strategy above.
Current objective: {self._get_current_objective(customer_profile)}

Remember: You're not here to take orders. You're here to SOLVE PROBLEMS and BUILD RELATIONSHIPS that result in SALES.

Every message should move closer to: NAME + PHONE + EMAIL + SALE

Be confident. Be helpful. Be the expert they trust. CLOSE THE DEAL. 🎯"""

    async def _get_product_knowledge(self) -> Dict[str, Any]:
        """Get structured product knowledge"""
        products = await self.db.products.find({}, {"_id": 0}).to_list(1000)
        
        knowledge = {
            "total_products": len(products),
            "categories": {},
            "brands": {},
            "price_ranges": {
                "budget": [],
                "mid_range": [],
                "premium": []
            }
        }
        
        for product in products:
            # Organize by category
            category = product.get('category', 'Other')
            if category not in knowledge["categories"]:
                knowledge["categories"][category] = []
            knowledge["categories"][category].append(product)
            
            # Organize by brand
            brand = product.get('brand', 'Other')
            if brand not in knowledge["brands"]:
                knowledge["brands"][brand] = []
            knowledge["brands"][brand].append(product)
            
            # Price segmentation
            price = product.get('price', 0)
            if price < 30000:
                knowledge["price_ranges"]["budget"].append(product)
            elif price < 60000:
                knowledge["price_ranges"]["mid_range"].append(product)
            else:
                knowledge["price_ranges"]["premium"].append(product)
        
        return knowledge
    
    async def _analyze_customer_profile(self, history: List[Dict]) -> Dict[str, Any]:
        """Analyze customer from conversation"""
        profile = {
            "name": None,
            "phone": None,
            "email": None,
            "budget_range": None,
            "product_interest": None,
            "urgency_level": "low",
            "decision_stage": "awareness",  # awareness, consideration, decision
            "pain_points": [],
            "preferences": [],
            "objections": [],
            "data_completeness": 0.0
        }
        
        # Extract from conversation history
        for msg in history:
            content = msg.get('content', '').lower()
            
            # Detect budget mentions
            if any(word in content for word in ['budget', 'price', 'cost', '₹', 'rupees']):
                profile["budget_range"] = "mentioned"
            
            # Detect urgency
            if any(word in content for word in ['urgent', 'asap', 'immediately', 'soon']):
                profile["urgency_level"] = "high"
            
            # Detect product interest
            for category in ['washing machine', 'refrigerator', 'oven', 'chimney', 'dishwasher']:
                if category in content:
                    profile["product_interest"] = category
        
        # Calculate completeness
        data_fields = ['name', 'phone', 'email']
        collected = sum(1 for field in data_fields if profile.get(field))
        profile["data_completeness"] = collected / len(data_fields)
        
        return profile
    
    def _format_customer_profile(self, profile: Dict) -> str:
        """Format profile for AI context"""
        return f"""
**Known Information:**
- Name: {profile.get('name') or '❌ NOT COLLECTED'}
- Phone: {profile.get('phone') or '❌ NOT COLLECTED'}
- Email: {profile.get('email') or '❌ NOT COLLECTED'}
- Product Interest: {profile.get('product_interest') or 'Unknown'}
- Budget Range: {profile.get('budget_range') or 'Not discussed'}
- Urgency: {profile.get('urgency_level')}
- Decision Stage: {profile.get('decision_stage')}
- Data Completeness: {profile.get('data_completeness', 0)*100:.0f}%

**Priority:** {self._get_collection_priority(profile)}
"""
    
    def _get_collection_priority(self, profile: Dict) -> str:
        """Determine what to collect next"""
        if not profile.get('name'):
            return "Get NAME first (casual, warm)"
        elif not profile.get('phone'):
            return "Collect PHONE (during product discussion)"
        elif not profile.get('email'):
            return "Get EMAIL (when showing products/pricing)"
        else:
            return "ALL DATA COLLECTED - FOCUS ON CLOSING SALE"
    
    def _format_product_catalog(self, knowledge: Dict) -> str:
        """Format products for AI understanding"""
        catalog = []
        for category, products in knowledge.get("categories", {}).items():
            catalog.append(f"\n**{category}:** {len(products)} products available")
            for product in products[:3]:  # Show top 3 per category
                catalog.append(f"  • {product.get('brand')} {product.get('name')} - ₹{product.get('price', 0):,.0f}")
        
        return "\n".join(catalog)
    
    def _format_conversation_context(self, history: List[Dict]) -> str:
        """Format recent conversation"""
        if not history:
            return "**New conversation - build rapport first**"
        
        recent = history[-5:]  # Last 5 messages
        formatted = []
        for msg in recent:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            formatted.append(f"**{role.upper()}:** {content[:100]}...")
        
        return "\n".join(formatted)
    
    def _get_current_objective(self, profile: Dict) -> str:
        """Determine immediate objective"""
        completeness = profile.get('data_completeness', 0)
        
        if completeness < 0.33:
            return "BUILD RAPPORT → Get NAME"
        elif completeness < 0.66:
            return "QUALIFY NEEDS → Collect PHONE"
        elif completeness < 1.0:
            return "PRESENT SOLUTIONS → Get EMAIL"
        else:
            return "CLOSE THE SALE → Confirm Purchase"
    
    def _determine_next_action(self, profile: Dict) -> str:
        """Determine next system action"""
        if profile.get('data_completeness', 0) >= 1.0:
            return "ready_to_close"
        elif profile.get('product_interest'):
            return "show_products"
        else:
            return "continue_discovery"
