# 🤖 AI Agents - Detailed Roles & Responsibilities

## Overview
The platform uses 5 AI agents powered by GPT-4o-mini (via Emergent LLM). 3 are customer-facing, 2 are internal operations.

---

## 1. 🛒 AI SALES AGENT (Customer-Facing)

### **Primary Role:**
Act as a virtual sales consultant to help customers find the perfect products, negotiate deals, and complete purchases.

### **Core Responsibilities:**

#### **Product Recommendations:**
- Analyze customer needs based on conversation
- Ask qualifying questions (budget, space, family size, cooking habits)
- Recommend best-fit products from catalog
- Compare multiple products side-by-side
- Explain technical features in simple terms
- Match products to specific use cases

**Example Interaction:**
```
Customer: "I need a microwave for a family of 4"
AI Sales: "I'd recommend the Bosch 25L Convection Microwave. It's perfect for 
a family of 4 because:
- 25L capacity handles family-sized meals
- Convection mode for baking and grilling
- Auto-cook menus for Indian dishes
- 5-year warranty
Currently ₹18,999 (15% off). Would you like to see similar options?"
```

#### **Price Negotiations:**
- Inform about current discounts and offers
- Suggest bundle deals (e.g., microwave + oven combo)
- Explain financing options if available
- Highlight value propositions (warranty, service, features)
- **Note:** Cannot override fixed prices, but can emphasize value

#### **Feature Comparisons:**
- Compare 2-3 products side-by-side
- Highlight key differences (capacity, power, features)
- Explain technical specifications in layman's terms
- Help customers understand what they're paying for

#### **Cart Assistance:**
- Remind customers of items in cart
- Suggest complementary products
- Answer pre-purchase questions
- Guide through checkout process
- Address concerns about delivery, installation

#### **Lead Generation:**
- Capture customer preferences
- Log conversation for follow-up
- Identify high-intent buyers
- Pass qualified leads to human sales team

### **Key Capabilities:**
- ✅ Access to full product catalog with real-time data
- ✅ Knowledge of current pricing, discounts, stock levels
- ✅ Understanding of product specifications and features
- ✅ Comparison logic for similar products
- ✅ Context retention across conversation
- ✅ Escalation to human agent when needed

### **Limitations:**
- ❌ Cannot process payments directly
- ❌ Cannot override prices without admin approval
- ❌ Cannot guarantee delivery dates (should check with Delivery Agent)
- ❌ Cannot provide technical troubleshooting (refer to Service Agent)

### **Success Metrics:**
- Conversion rate (chat to purchase)
- Average order value
- Customer satisfaction score
- Number of products recommended per session
- Cart abandonment recovery rate

---

## 2. 🔧 AI SERVICE AGENT (Customer-Facing)

### **Primary Role:**
Provide 24/7 technical support, troubleshooting, and service request management for all products.

### **Core Responsibilities:**

#### **Instant Troubleshooting:**
- Diagnose common product issues
- Provide step-by-step troubleshooting guides
- Use product manuals and documentation
- Walk customers through fixes
- Identify when professional service is needed

**Example Interaction:**
```
Customer: "My Bosch dishwasher is showing E15 error"
AI Service: "E15 indicates a water leakage issue. Let's troubleshoot:
1. Turn off the dishwasher and unplug it
2. Check if water is pooling at the bottom
3. Tilt the machine slightly forward to drain excess water
4. Check the drain hose for clogs
5. Inspect door seal for damage

If these steps don't resolve it, I can create a service request for a 
technician visit. Would you like me to do that?"
```

#### **Service Request Creation:**
- Create automated service tickets
- Capture product details (model, serial number, purchase date)
- Document issue description with photos (if uploaded)
- Schedule service appointments
- Provide service ticket number for tracking
- Send confirmation via SMS/Email

#### **Technical Support:**
- Answer product usage questions
- Explain features and settings
- Provide maintenance tips
- Share user manuals and video guides
- Help with installation queries
- Warranty information and claims

#### **Repair Scheduling:**
- Check technician availability
- Suggest convenient time slots
- Coordinate with customer's schedule
- Send appointment reminders
- Provide technician contact details
- Track service completion

#### **Issue Documentation:**
- Log all customer issues in database
- Track recurring problems by product/model
- Generate insights for product improvements
- Maintain service history per customer
- Create knowledge base articles from common issues

### **Key Capabilities:**
- ✅ Access to product manuals and technical documentation
- ✅ Common error code database (Bosch/Siemens specific)
- ✅ Service request management system integration
- ✅ Warranty verification capability
- ✅ Multi-step troubleshooting logic
- ✅ Image analysis for visual diagnosis (if implemented)

### **Limitations:**
- ❌ Cannot perform physical repairs remotely
- ❌ Cannot guarantee fix without professional inspection
- ❌ Cannot override warranty terms
- ❌ Cannot schedule service in areas without coverage

### **Success Metrics:**
- First-contact resolution rate
- Average troubleshooting time
- Service request creation accuracy
- Customer satisfaction (CSAT) score
- Reduction in repeat service calls
- Self-service success rate

---

## 3. 🚚 AI DELIVERY AGENT (Customer-Facing)

### **Primary Role:**
Manage delivery logistics, provide real-time tracking, and ensure smooth delivery experience.

### **Core Responsibilities:**

#### **Delivery Optimization:**
- Calculate estimated delivery dates based on location
- Suggest optimal delivery time slots
- Coordinate with logistics partners
- Plan efficient delivery routes
- Handle delivery preference changes

**Example Interaction:**
```
Customer: "When will my order arrive? Pincode 400001"
AI Delivery: "Your order #AD202511030032 will be delivered to Mumbai (400001) 
within 3-5 business days. Estimated delivery: Nov 8-10, 2025.

Delivery options:
1. Standard (Free) - 9 AM to 6 PM
2. Express (₹199) - Next-day delivery
3. Scheduled - Choose specific time slot

You can track your order in real-time using the tracking link sent to your email."
```

#### **Real-time Tracking:**
- Provide order status updates
- Share tracking links
- Send proactive notifications at each stage
- Estimate accurate delivery time
- Alert about delays immediately
- Provide delivery person contact details

#### **Customer Updates:**
- Order confirmation messages
- Dispatch notifications
- Out-for-delivery alerts
- Delivery completion confirmation
- Failed delivery follow-up
- Return/exchange status tracking

#### **Route Planning:**
- Calculate fastest delivery routes
- Optimize for multiple deliveries
- Consider traffic and weather conditions
- Suggest alternative delivery addresses
- Handle delivery to remote locations

#### **Delivery Exception Handling:**
- Manage delivery failures (customer unavailable)
- Reschedule deliveries
- Update delivery addresses
- Handle special delivery instructions
- Coordinate for re-delivery attempts

### **Integration Points:**
- Shiprocket API (when integrated)
- Google Maps for location verification
- SMS/Email notification systems
- Order management system
- Customer database for preferences

### **Key Capabilities:**
- ✅ Pincode serviceability check
- ✅ Delivery time estimation based on location
- ✅ Order status tracking in real-time
- ✅ Multi-language delivery notifications
- ✅ Delivery preference management
- ✅ COD amount confirmation

### **Limitations:**
- ❌ Cannot override courier partner timelines
- ❌ Cannot guarantee delivery in non-serviceable areas
- ❌ Cannot process returns without proper verification
- ❌ Manual until Shiprocket integration (then automated)

### **Success Metrics:**
- On-time delivery rate
- Customer notification response rate
- Delivery exception resolution time
- Customer satisfaction with delivery
- Failed delivery rate
- Re-delivery success rate

---

## 4. 📊 AI MARKETING AGENT (Internal - Not Customer-Facing)

### **Primary Role:**
Autonomous marketing campaign management, customer behavior analysis, and personalized promotions.

### **Core Responsibilities:**

#### **Smart Campaign Creation:**
- Analyze product performance data
- Identify slow-moving inventory
- Create targeted promotional campaigns
- Design discount strategies
- Generate campaign copy and visuals
- Schedule campaigns for optimal timing

**Example Campaign:**
```
Product: Bosch Dishwashers (slow-moving)
Target: Customers who viewed but didn't purchase
Campaign: "Weekend Special - 20% off Dishwashers + Free Installation"
Timing: Friday evening (when purchase intent is high)
Channel: Email + WhatsApp + Website banner
```

#### **Customer Insights & Segmentation:**
- Analyze purchase patterns
- Segment customers by behavior (frequent buyers, cart abandoners, etc.)
- Identify high-value customers
- Track customer lifetime value
- Predict churn risk
- Create lookalike audiences

#### **Personalized Offers:**
- Send product recommendations based on browsing history
- Create personalized discount codes
- Birthday/anniversary special offers
- Re-engagement campaigns for inactive customers
- Cross-sell and up-sell opportunities
- Loyalty program management

#### **ROI Optimization:**
- Track campaign performance metrics
- A/B test different messaging
- Optimize ad spend allocation
- Calculate customer acquisition cost
- Measure return on marketing investment
- Adjust strategies based on data

#### **Content Generation:**
- Create email marketing copy
- Generate product descriptions
- Write social media posts
- Design promotional banners
- Craft SMS marketing messages
- Produce blog post ideas

### **Autonomous Features:**
- Runs campaigns without human intervention
- Self-optimizes based on performance
- Automatically pauses underperforming campaigns
- Reallocates budget to winning strategies
- Sends performance reports to admins

### **Key Capabilities:**
- ✅ Customer data analysis
- ✅ Predictive analytics
- ✅ Campaign automation
- ✅ Multi-channel marketing
- ✅ Performance tracking
- ✅ Budget optimization

### **Success Metrics:**
- Campaign ROI
- Email open rates and click-through rates
- Conversion rate from campaigns
- Customer engagement score
- Revenue attributed to marketing
- Cost per acquisition

---

## 5. 📦 AI STOCK MANAGER (Internal - Not Customer-Facing)

### **Primary Role:**
Intelligent inventory management, demand forecasting, and automated reordering.

### **Core Responsibilities:**

#### **Stock Monitoring:**
- Track real-time inventory levels
- Monitor stock across all SKUs
- Identify low-stock items
- Track stock movement patterns
- Detect dead stock
- Manage stock across multiple warehouses (if applicable)

**Example Alert:**
```
Alert: Bosch 25L Microwave - Stock Level Critical
Current Stock: 3 units
Average Daily Sales: 2 units
Estimated Days to Stockout: 1.5 days
Recommendation: Reorder 20 units immediately
Lead Time: 7 days
```

#### **Demand Forecasting:**
- Predict future demand using historical data
- Identify seasonal trends
- Account for promotional campaigns
- Consider market trends
- Adjust forecasts based on external factors
- Predict stockouts before they occur

#### **Reorder Alerts & Automation:**
- Calculate optimal reorder points
- Suggest reorder quantities
- Automate purchase orders (when integrated)
- Consider lead times from suppliers
- Balance cost vs. stockout risk
- Optimize safety stock levels

#### **Inventory Analytics:**
- Stock turnover rate
- Days of inventory on hand
- Slow-moving product identification
- Fast-moving product insights
- Stock value analysis
- ABC analysis (high-value vs. low-value items)

#### **Optimization Recommendations:**
- Suggest markdown for slow-moving items
- Recommend bundling opportunities
- Identify products to discontinue
- Optimize warehouse space utilization
- Reduce holding costs
- Minimize waste and obsolescence

### **Integration Points:**
- Product catalog database
- Order management system
- Supplier management (when implemented)
- Warehouse management system
- Financial systems for cost tracking

### **Key Capabilities:**
- ✅ Real-time stock level monitoring
- ✅ Predictive analytics for demand
- ✅ Automated alert generation
- ✅ Multi-product portfolio management
- ✅ Historical data analysis
- ✅ What-if scenario modeling

### **Success Metrics:**
- Stock-out rate (target: <2%)
- Inventory turnover ratio
- Forecast accuracy
- Carrying cost reduction
- Order fulfillment rate
- Cash flow improvement from optimized inventory

---

## 🔗 Inter-Agent Communication

### How Agents Work Together:

**Scenario 1: Customer Purchase Journey**
```
Sales Agent → Recommends product, adds to cart
↓
Customer places order
↓
Delivery Agent → Provides delivery timeline
↓
Service Agent → Available for post-purchase support
↓
Marketing Agent → Sends follow-up satisfaction survey
```

**Scenario 2: Stock Management**
```
Stock Manager → Detects low inventory on popular item
↓
Alerts Admin
↓
Marketing Agent → Pauses promotions on that item
↓
Sales Agent → Updated with stock info, suggests alternatives to customers
```

**Scenario 3: Service Issue Leading to Sale**
```
Service Agent → Customer complaining about old product
↓
Identifies product is out of warranty, expensive to repair
↓
Transfers to Sales Agent
↓
Sales Agent → Offers upgrade deal on new model with discount
```

---

## 🎯 Fine-Tuning Recommendations

### For Sales Agent:
- **Train on negotiation tactics** - Handle price objections better
- **Product knowledge enhancement** - Deep dive into technical specs
- **Upsell training** - Suggest premium models effectively
- **Regional customization** - Adapt to local buying patterns

### For Service Agent:
- **Expand error code database** - Cover all Bosch/Siemens error codes
- **Visual diagnosis** - Add image recognition for physical issues
- **Preventive maintenance tips** - Proactive customer education
- **Multi-language support** - Hindi, Tamil, Telugu, etc.

### For Delivery Agent:
- **Shiprocket integration** - Automate tracking completely
- **Route optimization** - Real-time traffic-based ETAs
- **Exception handling** - Better failed delivery recovery
- **Customer preference learning** - Remember delivery preferences

### For Marketing Agent:
- **Campaign personalization depth** - More granular segmentation
- **Multi-channel orchestration** - Coordinate email, SMS, WhatsApp
- **Creative generation** - Auto-generate campaign visuals
- **Budget optimization AI** - Machine learning for spend allocation

### For Stock Manager:
- **Supplier integration** - Automatic PO generation
- **Multi-warehouse support** - Manage stock across locations
- **Seasonal forecasting** - Better handle festival seasons
- **Financial integration** - Consider cash flow in reorder decisions

---

## 📋 Configuration & Customization

### Current Setup:
- **Model:** GPT-4o-mini (via Emergent LLM)
- **Temperature:** 0.7 (balanced creativity vs. accuracy)
- **Max Tokens:** 2000 (sufficient for detailed responses)
- **Context Window:** Last 10 messages retained
- **Language:** English (Hindi support can be added)

### Recommended Enhancements:
1. **Add knowledge base** - Upload product manuals, FAQs
2. **Session persistence** - Remember customer across visits
3. **Sentiment analysis** - Detect frustrated customers, escalate
4. **Intent classification** - Route to correct agent automatically
5. **Response templates** - Consistent formatting for common queries

---

**All AI agents are operational and can be further customized based on your specific business needs. Let me know which agents you'd like to fine-tune!**
