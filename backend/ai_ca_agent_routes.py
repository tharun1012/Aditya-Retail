from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from database import get_db
import os
import uuid
from emergentintegrations.llm.chat import LlmChat, UserMessage

router = APIRouter(prefix="/ai-ca", tags=["AI CA Agent"])


# ==================== MODELS ====================

class ChatMessage(BaseModel):
    query: str
    user_role: Optional[str] = "admin"
    date_range: Optional[Dict[str, str]] = None  # {"start": "2025-04-01", "end": "2025-04-30"}


class ChatResponse(BaseModel):
    response: str
    data: Optional[dict] = None
    suggestions: Optional[List[str]] = None


class AuditRequest(BaseModel):
    audit_type: str  # daily, weekly, monthly, custom
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class AuditResponse(BaseModel):
    audit_id: str
    audit_type: str
    period: Dict[str, str]
    summary: Dict[str, Any]
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    ai_analysis: str


# ==================== UTILITY FUNCTIONS ====================

def parse_date(date_str: str) -> datetime:
    """Parse various date formats to datetime"""
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%d-%m-%Y",
        "%d/%m/%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.split('+')[0].split('Z')[0], fmt.split('%z')[0])
        except Exception:
            continue
    raise ValueError(f"Cannot parse date: {date_str}")


def extract_date_range_from_query(query: str) -> Optional[Dict[str, datetime]]:
    """Extract date range from natural language query"""
    query_lower = query.lower()
    today = datetime.now(timezone.utc)
    
    # Check for specific months
    months = {
        'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
        'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6,
        'july': 7, 'jul': 7, 'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'sept': 9,
        'october': 10, 'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12
    }
    
    # Check for year
    year = today.year
    for y in range(2020, 2030):
        if str(y) in query:
            year = y
            break
    
    # Check for month names
    for month_name, month_num in months.items():
        if month_name in query_lower:
            start = datetime(year, month_num, 1, tzinfo=timezone.utc)
            if month_num == 12:
                end = datetime(year + 1, 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
            else:
                end = datetime(year, month_num + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
            return {"start": start, "end": end}
    
    # Check for relative time periods
    if 'today' in query_lower:
        start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        return {"start": start, "end": end}
    
    if 'yesterday' in query_lower:
        yesterday = today - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        return {"start": start, "end": end}
    
    if 'this week' in query_lower or 'current week' in query_lower:
        start = today - timedelta(days=today.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        return {"start": start, "end": end}
    
    if 'last week' in query_lower:
        start = today - timedelta(days=today.weekday() + 7)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return {"start": start, "end": end}
    
    if 'this month' in query_lower or 'current month' in query_lower:
        start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        return {"start": start, "end": end}
    
    if 'last month' in query_lower:
        first_of_this_month = today.replace(day=1)
        end = first_of_this_month - timedelta(days=1)
        start = end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        return {"start": start, "end": end}
    
    if 'last 7 days' in query_lower:
        start = (today - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        return {"start": start, "end": end}
    
    if 'last 30 days' in query_lower:
        start = (today - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        return {"start": start, "end": end}
    
    if 'this year' in query_lower or 'current year' in query_lower:
        start = datetime(today.year, 1, 1, tzinfo=timezone.utc)
        end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        return {"start": start, "end": end}
    
    if 'fy' in query_lower or 'financial year' in query_lower:
        # Indian Financial Year: April to March
        if today.month >= 4:
            start = datetime(today.year, 4, 1, tzinfo=timezone.utc)
            end = datetime(today.year + 1, 3, 31, 23, 59, 59, tzinfo=timezone.utc)
        else:
            start = datetime(today.year - 1, 4, 1, tzinfo=timezone.utc)
            end = datetime(today.year, 3, 31, 23, 59, 59, tzinfo=timezone.utc)
        return {"start": start, "end": end}
    
    # Default to current month
    return None


async def get_sales_data(db, start_date: datetime, end_date: datetime) -> Dict:
    """Get sales data for the given date range"""
    # Convert dates to ISO string format for string comparison
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    # For created_at stored as ISO strings, we need string comparison
    # Also handle datetime objects for backwards compatibility
    orders = await db.orders.find({
        "$or": [
            # String comparison for ISO format dates
            {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}},
            # Datetime comparison (if stored as datetime)
            {"created_at": {"$gte": start_date, "$lte": end_date}},
        ]
    }, {"_id": 0}).to_list(None)
    
    # Query offline_invoices - check multiple date fields
    # invoice_date is typically "YYYY-MM-DD" string
    # created_at can be ISO string or datetime
    offline = await db.offline_invoices.find({
        "$and": [
            # Only get invoices (not sales orders in pending state)
            {"$or": [
                {"document_type": "invoice"},
                {"document_type": {"$exists": False}}  # Legacy invoices
            ]},
            {"$or": [
                # Match by invoice_date (preferred for sales reports)
                {"invoice_date": {"$gte": start_str, "$lte": end_str}},
                # Fallback to created_at string comparison
                {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}},
                # Fallback to created_at datetime comparison
                {"created_at": {"$gte": start_date, "$lte": end_date}}
            ]}
        ]
    }, {"_id": 0}).to_list(None)
    
    # Calculate totals
    total_sales = sum(o.get("total_amount", 0) or 0 for o in orders)
    total_offline = sum(i.get("total_amount", 0) or 0 for i in offline)
    
    # Calculate tax
    total_tax = sum(o.get("tax_amount", 0) or o.get("gst_amount", 0) or 0 for o in orders)
    total_tax += sum(i.get("tax_total", 0) or i.get("total_tax", 0) or i.get("gst_amount", 0) or 0 for i in offline)
    
    return {
        "total_sales": round(total_sales + total_offline, 2),
        "online_sales": round(total_sales, 2),
        "offline_sales": round(total_offline, 2),
        "order_count": len(orders),
        "offline_count": len(offline),
        "total_tax": round(total_tax, 2),
        "orders": orders,
        "offline_invoices": offline
    }


async def get_purchase_data(db, start_date: datetime, end_date: datetime) -> Dict:
    """Get purchase data for the given date range"""
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    # Check purchase_bills collection (main purchase data)
    purchase_bills = await db.purchase_bills.find({
        "$or": [
            {"bill_date": {"$gte": start_str, "$lte": end_str}},
            {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}},
            {"created_at": {"$gte": start_date, "$lte": end_date}}
        ]
    }, {"_id": 0}).to_list(None)
    
    # Also check purchases collection
    purchases = await db.purchases.find({
        "$or": [
            {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}},
            {"created_at": {"$gte": start_date, "$lte": end_date}}
        ]
    }, {"_id": 0}).to_list(None)
    
    total_purchase_bills = sum(pb.get("grand_total", 0) or pb.get("total_amount", 0) or 0 for pb in purchase_bills)
    total_purchases = sum(p.get("total_amount", 0) or 0 for p in purchases)
    
    total_input_tax = sum(pb.get("total_tax", 0) or (pb.get("cgst", 0) or 0) + (pb.get("sgst", 0) or 0) + (pb.get("igst", 0) or 0) for pb in purchase_bills)
    total_input_tax += sum(p.get("tax_total", 0) or 0 for p in purchases)
    
    return {
        "total_purchases": round(total_purchase_bills + total_purchases, 2),
        "purchase_bill_total": round(total_purchase_bills, 2),
        "purchase_order_total": round(total_purchases, 2),
        "bill_count": len(purchase_bills),
        "order_count": len(purchases),
        "input_tax_credit": round(total_input_tax, 2),
        "purchase_bills": purchase_bills,
        "purchases": purchases
    }


async def get_expense_data(db, start_date: datetime, end_date: datetime) -> Dict:
    """Get expense data for the given date range"""
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    expenses = await db.expenses.find({
        "$or": [
            {"expense_date": {"$gte": start_str, "$lte": end_str}},
            {"created_at": {"$gte": start_str, "$lte": end_str + "T23:59:59"}},
            {"created_at": {"$gte": start_date, "$lte": end_date}}
        ]
    }, {"_id": 0}).to_list(None)
    
    total_expenses = sum(e.get("amount", 0) or 0 for e in expenses)
    
    # Category-wise breakdown
    by_category = {}
    for expense in expenses:
        category = expense.get("category", "Other")
        by_category[category] = by_category.get(category, 0) + (expense.get("amount", 0) or 0)
    
    return {
        "total_expenses": round(total_expenses, 2),
        "expense_count": len(expenses),
        "by_category": {k: round(v, 2) for k, v in by_category.items()},
        "expenses": expenses
    }


# ==================== MAIN CHAT ENDPOINT ====================

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai_ca(message: ChatMessage, db=Depends(get_db)):
    """Chat with AI CA Agent - Enhanced conversational accounting assistant"""
    try:
        query = message.query
        
        # Extract date range from query or use provided
        date_range = None
        if message.date_range:
            date_range = {
                "start": parse_date(message.date_range["start"]),
                "end": parse_date(message.date_range["end"])
            }
        else:
            date_range = extract_date_range_from_query(query)
        
        # Default to current month if no date range
        if not date_range:
            today = datetime.now(timezone.utc)
            date_range = {
                "start": today.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                "end": today.replace(hour=23, minute=59, second=59, microsecond=999999)
            }
        
        # Gather relevant data based on query
        context_data = await gather_accounting_context(query, db, date_range)
        
        # Build system prompt
        period_str = f"{date_range['start'].strftime('%d %b %Y')} to {date_range['end'].strftime('%d %b %Y')}"
        
        system_prompt = f"""You are the Chief Financial Advisor (AI CA) for Aditya Retail - a premium Bosch & Siemens home appliances retailer in Karnataka, India.

## 🎯 YOUR CORE COMPETENCIES:

### 1. FINANCIAL ANALYSIS & REPORTING
- **Profit & Loss Statements**: Generate P&L for any period with revenue breakdown
- **Balance Sheet Insights**: Asset, liability, and equity analysis
- **Cash Flow Analysis**: Operating, investing, and financing activities
- **Ratio Analysis**: Liquidity, profitability, efficiency ratios
- **Trend Analysis**: Month-over-month, year-over-year comparisons

### 2. GST COMPLIANCE (CRITICAL FOR INDIAN BUSINESS)
- **GSTR-1 Preparation**: B2B sales, B2C sales, HSN summary
- **GSTR-3B Calculation**: Output tax, input tax credit, net liability
- **Input Tax Credit (ITC)**: Eligible vs ineligible credits, ITC utilization
- **E-Way Bill Compliance**: Transactions > ₹50,000
- **GST Rate Verification**: Correct rates for appliances (typically 18%)

### 3. ACCOUNTS RECEIVABLE & PAYABLE
- **Customer Receivables**: Outstanding amounts, aging analysis, overdue tracking
- **Vendor Payables**: Bills pending, payment schedules, early payment discounts
- **DSO (Days Sales Outstanding)**: Collection efficiency
- **DPO (Days Payable Outstanding)**: Payment efficiency

### 4. AUDIT & COMPLIANCE
- **Daily Audit Checks**: Zero-value transactions, missing GST, duplicate entries
- **Month-End Close**: Reconciliation checklist, accruals, provisions
- **Statutory Compliance**: TDS, PF, ESI deadlines
- **Internal Controls**: Segregation of duties, approval hierarchies

### 5. BUSINESS INTELLIGENCE
- **Sales Performance**: By store, brand, category, salesperson
- **Inventory Valuation**: FIFO, weighted average, stock aging
- **Margin Analysis**: Gross margin, net margin by product category
- **Break-Even Analysis**: Fixed costs, variable costs, contribution margin

## 📊 CURRENT BUSINESS CONTEXT:

**Period:** {period_str}
**Business:** Aditya Retail (Bosch/Siemens Premium Appliances)
**Locations:** Bangalore (HRBR Layout, JP Nagar)

{context_data.get('summary', '')}

## 📋 RESPONSE FORMAT:

When providing financial information:
1. **State the source**: "Based on N invoices/transactions..."
2. **Use Indian notation**: Lakhs (₹1,00,000), Crores (₹1,00,00,000)
3. **Break down GST**: CGST + SGST for intra-state, IGST for inter-state
4. **Highlight concerns**: 🔴 Critical, 🟡 Warning, 🟢 Good
5. **Provide actionable recommendations**

## 🔧 SAMPLE QUERIES I CAN HANDLE:

**Sales Analysis:**
- "What's our sales for April 2025?"
- "Compare Q1 vs Q2 revenue"
- "Top 5 selling products this month"
- "Store-wise sales breakdown"

**GST Compliance:**
- "Calculate GSTR-3B for this month"
- "What's our GST liability?"
- "Show Input Tax Credit summary"
- "Prepare HSN-wise sales summary"

**P&L and Profitability:**
- "Generate P&L for current FY"
- "What's our gross profit margin?"
- "Show expense breakdown by category"
- "Calculate EBITDA"

**Receivables/Payables:**
- "List overdue customer payments"
- "Show vendor payment aging"
- "What's pending to be collected?"
- "Which invoices are 30+ days overdue?"

**Audit & Review:**
- "Run daily audit for yesterday"
- "Find invoices with GST errors"
- "Check for duplicate entries"
- "Identify high-value transactions"

## ⚠️ IMPORTANT GUIDELINES:

1. **Accuracy First**: If data is missing or zero, clearly state it
2. **Conservative Estimates**: When uncertain, flag it
3. **Compliance Focus**: Always consider GST/statutory implications
4. **Actionable Insights**: Every analysis should have recommendations
5. **Professional Tone**: You're the CA, be authoritative yet helpful

User Role: {message.user_role}
"""

        user_message = f"""Query: {message.query}

Available Data for {period_str}:
{format_context_for_llm(context_data)}

Provide a comprehensive, professional response with:
1. Direct answer to the query
2. Supporting data and calculations
3. Key observations or concerns
4. Recommended actions (if applicable)"""

        # Call LLM
        chat = LlmChat(
            api_key=os.environ.get("EMERGENT_LLM_KEY"),
            session_id=f"ai_ca_{datetime.now().timestamp()}",
            system_message=system_prompt
        ).with_model("openai", "gpt-4o")
        
        user_msg = UserMessage(text=user_message)
        response = await chat.send_message(user_msg)
        
        # Extract response
        if isinstance(response, dict):
            ai_response = response.get('content', response.get('message', 'No response generated'))
        else:
            ai_response = str(response)
        
        # Generate suggestions based on context
        suggestions = generate_suggestions(query, context_data)
        
        return ChatResponse(
            response=ai_response,
            data=context_data.get('raw_data'),
            suggestions=suggestions
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI CA Agent error: {str(e)}")


async def gather_accounting_context(query: str, db, date_range: Dict[str, datetime]) -> dict:
    """Gather relevant accounting data based on query intent"""
    
    context = {
        'summary': '',
        'raw_data': {},
        'period': {
            'start': date_range['start'].strftime('%Y-%m-%d'),
            'end': date_range['end'].strftime('%Y-%m-%d')
        }
    }
    
    query_lower = query.lower()
    start_date = date_range['start']
    end_date = date_range['end']
    
    # Always fetch sales data for sales-related queries
    if any(word in query_lower for word in ['sales', 'revenue', 'income', 'p&l', 'profit', 'order', 'invoice', 'customer', 'how much', 'total']):
        sales_data = await get_sales_data(db, start_date, end_date)
        
        total_orders = sales_data['order_count'] + sales_data['offline_count']
        avg_order = (sales_data['total_sales'] / total_orders) if total_orders > 0 else 0
        
        context['summary'] += f"""
SALES DATA ({start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}):
- Total Sales: ₹{sales_data['total_sales']:,.2f}
- Online Sales: ₹{sales_data['online_sales']:,.2f} ({sales_data['order_count']} orders)
- Offline Sales: ₹{sales_data['offline_sales']:,.2f} ({sales_data['offline_count']} invoices)
- Total GST Collected: ₹{sales_data['total_tax']:,.2f}
- Average Order Value: ₹{avg_order:,.2f}
- Total Transactions: {total_orders}
"""
        
        context['raw_data']['sales'] = {
            'total_sales': sales_data['total_sales'],
            'online_sales': sales_data['online_sales'],
            'offline_sales': sales_data['offline_sales'],
            'order_count': sales_data['order_count'],
            'offline_count': sales_data['offline_count'],
            'total_tax': sales_data['total_tax'],
            'avg_order_value': round(avg_order, 2)
        }
    
    # Fetch purchase data
    if any(word in query_lower for word in ['purchase', 'buying', 'vendor', 'supplier', 'bill', 'procurement', 'input', 'credit']):
        purchase_data = await get_purchase_data(db, start_date, end_date)
        
        context['summary'] += f"""
PURCHASE DATA ({start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}):
- Total Purchases: ₹{purchase_data['total_purchases']:,.2f}
- Purchase Bills: ₹{purchase_data['purchase_bill_total']:,.2f} ({purchase_data['bill_count']} bills)
- Purchase Orders: ₹{purchase_data['purchase_order_total']:,.2f} ({purchase_data['order_count']} orders)
- Input Tax Credit (ITC): ₹{purchase_data['input_tax_credit']:,.2f}
"""
        
        context['raw_data']['purchases'] = {
            'total_purchases': purchase_data['total_purchases'],
            'bill_count': purchase_data['bill_count'],
            'order_count': purchase_data['order_count'],
            'input_tax_credit': purchase_data['input_tax_credit']
        }
    
    # Fetch expense data
    if any(word in query_lower for word in ['expense', 'cost', 'spending', 'overhead']):
        expense_data = await get_expense_data(db, start_date, end_date)
        
        category_str = ', '.join([f"{k}: ₹{v:,.2f}" for k, v in list(expense_data['by_category'].items())[:5]])
        
        context['summary'] += f"""
EXPENSE DATA ({start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}):
- Total Expenses: ₹{expense_data['total_expenses']:,.2f}
- Expense Entries: {expense_data['expense_count']}
- Top Categories: {category_str if category_str else 'No expenses recorded'}
"""
        
        context['raw_data']['expenses'] = expense_data
    
    # GST calculations
    if any(word in query_lower for word in ['gst', 'tax', 'gstr', 'liability', 'itc', 'compliance']):
        sales_data = await get_sales_data(db, start_date, end_date)
        purchase_data = await get_purchase_data(db, start_date, end_date)
        
        output_tax = sales_data['total_tax']
        input_tax = purchase_data['input_tax_credit']
        net_gst = output_tax - input_tax
        
        context['summary'] += f"""
GST DATA ({start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}):
- Output Tax (Sales GST): ₹{output_tax:,.2f}
  - CGST: ₹{output_tax/2:,.2f}
  - SGST: ₹{output_tax/2:,.2f}
- Input Tax Credit (Purchase GST): ₹{input_tax:,.2f}
- Net GST Liability: ₹{net_gst:,.2f} {'(Payable)' if net_gst > 0 else '(Refundable)' if net_gst < 0 else '(Nil)'}
"""
        
        context['raw_data']['gst'] = {
            'output_tax': round(output_tax, 2),
            'input_tax': round(input_tax, 2),
            'net_liability': round(net_gst, 2),
            'cgst': round(output_tax/2, 2),
            'sgst': round(output_tax/2, 2)
        }
    
    # HSN Code lookup
    if any(word in query_lower for word in ['hsn', 'hsn code', 'hsn number', 'gst rate', 'tax rate for']):
        # Fetch all HSN codes
        hsn_codes = await db.hsn_codes.find({"is_active": True}, {"_id": 0}).to_list(None)
        
        if hsn_codes:
            # Format HSN codes for response
            hsn_list = []
            for hsn in hsn_codes[:20]:  # Limit to 20 for readability
                hsn_list.append(f"  - {hsn.get('code')}: {hsn.get('description')} (GST: {hsn.get('gst_rate', 18)}%)")
            
            context['summary'] += f"""
HSN CODES AVAILABLE:
{chr(10).join(hsn_list)}
{'... and more' if len(hsn_codes) > 20 else ''}

Total HSN codes in database: {len(hsn_codes)}
"""
            
            context['raw_data']['hsn_codes'] = hsn_codes
        else:
            context['summary'] += """
HSN CODES:
No HSN codes found in database. Please contact admin to seed HSN codes.
"""
    
    # Profit & Loss
    if any(word in query_lower for word in ['profit', 'loss', 'p&l', 'margin', 'net income']):
        sales_data = await get_sales_data(db, start_date, end_date)
        purchase_data = await get_purchase_data(db, start_date, end_date)
        expense_data = await get_expense_data(db, start_date, end_date)
        
        revenue = sales_data['total_sales']
        cogs = purchase_data['total_purchases']
        gross_profit = revenue - cogs
        gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
        
        operating_expenses = expense_data['total_expenses']
        net_profit = gross_profit - operating_expenses
        net_margin = (net_profit / revenue * 100) if revenue > 0 else 0
        
        context['summary'] += f"""
PROFIT & LOSS ({start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}):
- Revenue (Sales): ₹{revenue:,.2f}
- Cost of Goods Sold: ₹{cogs:,.2f}
- Gross Profit: ₹{gross_profit:,.2f} ({gross_margin:.1f}% margin)
- Operating Expenses: ₹{operating_expenses:,.2f}
- Net Profit: ₹{net_profit:,.2f} ({net_margin:.1f}% margin)
"""
        
        context['raw_data']['pnl'] = {
            'revenue': round(revenue, 2),
            'cogs': round(cogs, 2),
            'gross_profit': round(gross_profit, 2),
            'gross_margin': round(gross_margin, 2),
            'operating_expenses': round(operating_expenses, 2),
            'net_profit': round(net_profit, 2),
            'net_margin': round(net_margin, 2)
        }
    
    # If no specific context, provide general overview
    if not context['summary']:
        # Fetch all data for general queries
        sales_data = await get_sales_data(db, start_date, end_date)
        purchase_data = await get_purchase_data(db, start_date, end_date)
        
        context['summary'] = f"""
OVERVIEW ({start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}):
- Total Sales: ₹{sales_data['total_sales']:,.2f} ({sales_data['order_count'] + sales_data['offline_count']} transactions)
- Total Purchases: ₹{purchase_data['total_purchases']:,.2f} ({purchase_data['bill_count'] + purchase_data['order_count']} transactions)
- GST Collected: ₹{sales_data['total_tax']:,.2f}
- Input Tax Credit: ₹{purchase_data['input_tax_credit']:,.2f}

I can help you with: Sales analysis, Purchase reports, GST compliance, P&L statements, Audits, and more.
"""
        
        context['raw_data'] = {
            'sales': {'total': sales_data['total_sales'], 'count': sales_data['order_count'] + sales_data['offline_count']},
            'purchases': {'total': purchase_data['total_purchases'], 'count': purchase_data['bill_count'] + purchase_data['order_count']}
        }
    
    return context


def format_context_for_llm(context_data: dict) -> str:
    """Format context data for LLM consumption"""
    if not context_data.get('raw_data'):
        return "No specific data available for this query."
    
    formatted = []
    for key, value in context_data.get('raw_data', {}).items():
        if isinstance(value, dict):
            formatted.append(f"\n{key.upper()}:")
            for k, v in value.items():
                if isinstance(v, (int, float)):
                    formatted.append(f"  - {k}: ₹{v:,.2f}" if 'count' not in k.lower() else f"  - {k}: {v}")
                else:
                    formatted.append(f"  - {k}: {v}")
        else:
            formatted.append(f"{key}: {value}")
    
    return "\n".join(formatted)


def generate_suggestions(query: str, context_data: dict) -> List[str]:
    """Generate contextual follow-up suggestions"""
    query_lower = query.lower()
    
    if 'sales' in query_lower or 'revenue' in query_lower:
        return [
            "Show me top-selling products this month",
            "Compare sales with last month",
            "What's my gross profit margin?",
            "Show customer-wise sales breakdown"
        ]
    elif 'gst' in query_lower or 'tax' in query_lower:
        return [
            "Calculate GSTR-1 for this month",
            "Show HSN-wise sales summary",
            "What's my net GST liability?",
            "Check for GST compliance issues"
        ]
    elif 'purchase' in query_lower:
        return [
            "Show vendor-wise purchase breakdown",
            "List pending purchase payments",
            "Compare purchases with last month",
            "Show input tax credit details"
        ]
    elif 'expense' in query_lower:
        return [
            "Show expense breakdown by category",
            "Which expenses increased this month?",
            "Compare expenses with last month",
            "Show high-value expense transactions"
        ]
    elif 'profit' in query_lower or 'p&l' in query_lower:
        return [
            "Show detailed P&L statement",
            "What's my operating margin?",
            "Compare profitability with last month",
            "Show monthly profit trend"
        ]
    elif 'audit' in query_lower:
        return [
            "Run daily audit for today",
            "Check for invoice errors",
            "Find GST mismatches",
            "Show reconciliation status"
        ]
    else:
        return [
            "Show me sales for April 2025",
            "What's my GST liability this month?",
            "Run a daily audit",
            "Generate P&L report"
        ]


# ==================== AUDIT ENDPOINTS ====================

@router.post("/audit", response_model=AuditResponse)
async def run_audit(request: AuditRequest, db=Depends(get_db)):
    """Run comprehensive audit - daily, weekly, monthly or custom"""
    try:
        today = datetime.now(timezone.utc)
        
        # Determine date range based on audit type
        if request.audit_type == "daily":
            if request.start_date:
                start_date = parse_date(request.start_date)
                end_date = start_date.replace(hour=23, minute=59, second=59)
            else:
                # Default to yesterday for daily audit
                yesterday = today - timedelta(days=1)
                start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        elif request.audit_type == "weekly":
            if request.start_date:
                start_date = parse_date(request.start_date)
            else:
                # Last 7 days
                start_date = (today - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        elif request.audit_type == "monthly":
            if request.start_date:
                start_date = parse_date(request.start_date)
                # Get end of that month
                if start_date.month == 12:
                    end_date = datetime(start_date.year + 1, 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
                else:
                    end_date = datetime(start_date.year, start_date.month + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
            else:
                # Current month
                start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        else:  # custom
            if not request.start_date or not request.end_date:
                raise HTTPException(status_code=400, detail="Custom audit requires start_date and end_date")
            start_date = parse_date(request.start_date)
            end_date = parse_date(request.end_date)
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Run the audit
        audit_result = await perform_audit(db, start_date, end_date)
        
        # Generate AI analysis
        ai_analysis = await generate_audit_analysis(audit_result, start_date, end_date)
        
        # Save audit report
        audit_id = f"AUDIT-{today.strftime('%Y%m%d%H%M%S')}"
        audit_record = {
            "id": audit_id,
            "audit_type": request.audit_type,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": audit_result['summary'],
            "issues": audit_result['issues'],
            "recommendations": audit_result['recommendations'],
            "ai_analysis": ai_analysis,
            "created_at": today.isoformat()
        }
        
        await db.audit_reports.insert_one(audit_record)
        
        return AuditResponse(
            audit_id=audit_id,
            audit_type=request.audit_type,
            period={
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            },
            summary=audit_result['summary'],
            issues=audit_result['issues'],
            recommendations=audit_result['recommendations'],
            ai_analysis=ai_analysis
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")


async def perform_audit(db, start_date: datetime, end_date: datetime) -> Dict:
    """Perform comprehensive audit checks"""
    
    issues = []
    summary = {
        "total_transactions": 0,
        "sales_total": 0,
        "purchase_total": 0,
        "expense_total": 0,
        "gst_collected": 0,
        "gst_paid": 0,
        "issues_found": 0,
        "critical_issues": 0,
        "warnings": 0
    }
    
    # Fetch all data
    sales_data = await get_sales_data(db, start_date, end_date)
    purchase_data = await get_purchase_data(db, start_date, end_date)
    expense_data = await get_expense_data(db, start_date, end_date)
    
    # Update summary
    summary['sales_total'] = sales_data['total_sales']
    summary['purchase_total'] = purchase_data['total_purchases']
    summary['expense_total'] = expense_data['total_expenses']
    summary['gst_collected'] = sales_data['total_tax']
    summary['gst_paid'] = purchase_data['input_tax_credit']
    summary['total_transactions'] = (
        sales_data['order_count'] + sales_data['offline_count'] +
        purchase_data['bill_count'] + purchase_data['order_count'] +
        expense_data['expense_count']
    )
    
    # AUDIT CHECK 1: Sales with zero amount
    zero_amount_sales = [o for o in sales_data['orders'] if (o.get('total_amount') or 0) == 0]
    if zero_amount_sales:
        issues.append({
            "type": "zero_amount_sale",
            "severity": "critical",
            "count": len(zero_amount_sales),
            "message": f"{len(zero_amount_sales)} sales orders with zero amount detected",
            "details": [{"order_id": o.get('order_number', o.get('id'))} for o in zero_amount_sales[:10]]
        })
        summary['critical_issues'] += 1
    
    # AUDIT CHECK 2: Sales without GST
    sales_without_gst = [o for o in sales_data['orders'] 
                        if (o.get('total_amount', 0) or 0) > 0 and 
                        (o.get('tax_amount', 0) or 0) == 0 and 
                        (o.get('gst_amount', 0) or 0) == 0]
    if sales_without_gst:
        issues.append({
            "type": "missing_gst_on_sale",
            "severity": "critical",
            "count": len(sales_without_gst),
            "message": f"{len(sales_without_gst)} sales without GST (possible compliance issue)",
            "details": [{"order_id": o.get('order_number'), "amount": o.get('total_amount')} for o in sales_without_gst[:10]]
        })
        summary['critical_issues'] += 1
    
    # AUDIT CHECK 3: Purchase bills without vendor
    bills_without_vendor = [pb for pb in purchase_data['purchase_bills'] 
                          if not pb.get('vendor') or not pb.get('vendor', {}).get('name')]
    if bills_without_vendor:
        issues.append({
            "type": "missing_vendor",
            "severity": "high",
            "count": len(bills_without_vendor),
            "message": f"{len(bills_without_vendor)} purchase bills without vendor name",
            "details": [{"bill_number": pb.get('bill_number')} for pb in bills_without_vendor[:10]]
        })
        summary['warnings'] += 1
    
    # AUDIT CHECK 4: Duplicate bill numbers
    bill_numbers = [pb.get('bill_number') for pb in purchase_data['purchase_bills'] if pb.get('bill_number')]
    duplicate_bills = [bn for bn in bill_numbers if bill_numbers.count(bn) > 1]
    if duplicate_bills:
        unique_duplicates = list(set(duplicate_bills))
        issues.append({
            "type": "duplicate_bill_number",
            "severity": "critical",
            "count": len(unique_duplicates),
            "message": f"{len(unique_duplicates)} duplicate bill numbers found",
            "details": unique_duplicates[:10]
        })
        summary['critical_issues'] += 1
    
    # AUDIT CHECK 5: Duplicate order numbers
    order_numbers = [o.get('order_number') for o in sales_data['orders'] if o.get('order_number')]
    duplicate_orders = [on for on in order_numbers if order_numbers.count(on) > 1]
    if duplicate_orders:
        unique_dup_orders = list(set(duplicate_orders))
        issues.append({
            "type": "duplicate_order_number",
            "severity": "critical",
            "count": len(unique_dup_orders),
            "message": f"{len(unique_dup_orders)} duplicate order numbers found",
            "details": unique_dup_orders[:10]
        })
        summary['critical_issues'] += 1
    
    # AUDIT CHECK 6: Items with zero unit price
    orders_with_zero_price_items = []
    for order in sales_data['orders']:
        items = order.get('items', [])
        for item in items:
            if (item.get('unit_price', 0) or 0) == 0 and (item.get('price', 0) or 0) == 0:
                orders_with_zero_price_items.append({
                    "order_id": order.get('order_number'),
                    "item": item.get('product_name', item.get('name', 'Unknown'))
                })
    if orders_with_zero_price_items:
        issues.append({
            "type": "zero_unit_price",
            "severity": "high",
            "count": len(orders_with_zero_price_items),
            "message": f"{len(orders_with_zero_price_items)} line items with zero unit price",
            "details": orders_with_zero_price_items[:10]
        })
        summary['warnings'] += 1
    
    # AUDIT CHECK 7: GST rate anomalies (not 5%, 12%, 18%, or 28%)
    gst_anomalies = []
    for order in sales_data['orders']:
        total = order.get('total_amount', 0) or 0
        tax = order.get('tax_amount', 0) or order.get('gst_amount', 0) or 0
        if total > 0 and tax > 0:
            taxable = total - tax
            if taxable > 0:
                rate = (tax / taxable) * 100
                # Check if rate is close to standard GST rates
                standard_rates = [5, 12, 18, 28]
                if not any(abs(rate - sr) < 1 for sr in standard_rates):
                    gst_anomalies.append({
                        "order_id": order.get('order_number'),
                        "calculated_rate": round(rate, 2),
                        "total": total,
                        "tax": tax
                    })
    if gst_anomalies:
        issues.append({
            "type": "gst_rate_anomaly",
            "severity": "medium",
            "count": len(gst_anomalies),
            "message": f"{len(gst_anomalies)} orders with non-standard GST rates",
            "details": gst_anomalies[:10]
        })
        summary['warnings'] += 1
    
    # AUDIT CHECK 8: High-value transactions (>5 lakhs) without proper documentation
    high_value_orders = [o for o in sales_data['orders'] if (o.get('total_amount', 0) or 0) > 500000]
    if high_value_orders:
        issues.append({
            "type": "high_value_transaction",
            "severity": "info",
            "count": len(high_value_orders),
            "message": f"{len(high_value_orders)} high-value transactions (>₹5L) - verify documentation",
            "details": [{"order_id": o.get('order_number'), "amount": o.get('total_amount')} for o in high_value_orders[:10]]
        })
    
    # AUDIT CHECK 9: Mismatch between line items total and order total
    amount_mismatches = []
    for order in sales_data['orders']:
        items = order.get('items', [])
        if items:
            items_total = sum((item.get('total', 0) or item.get('amount', 0) or 
                              (item.get('unit_price', 0) or item.get('price', 0) or 0) * (item.get('quantity', 1) or 1)) 
                             for item in items)
            order_subtotal = order.get('subtotal', 0) or 0
            # Allow for small rounding differences
            if items_total > 0 and order_subtotal > 0 and abs(items_total - order_subtotal) > 10:
                amount_mismatches.append({
                    "order_id": order.get('order_number'),
                    "items_total": round(items_total, 2),
                    "order_subtotal": round(order_subtotal, 2),
                    "difference": round(abs(items_total - order_subtotal), 2)
                })
    if amount_mismatches:
        issues.append({
            "type": "amount_mismatch",
            "severity": "high",
            "count": len(amount_mismatches),
            "message": f"{len(amount_mismatches)} orders with line item total mismatch",
            "details": amount_mismatches[:10]
        })
        summary['warnings'] += 1
    
    # AUDIT CHECK 10: Missing GSTIN for B2B transactions
    b2b_without_gstin = [o for o in sales_data['orders'] 
                        if o.get('customer_type') == 'business' and not o.get('customer_gstin')]
    if b2b_without_gstin:
        issues.append({
            "type": "missing_gstin_b2b",
            "severity": "high",
            "count": len(b2b_without_gstin),
            "message": f"{len(b2b_without_gstin)} B2B transactions without GSTIN",
            "details": [{"order_id": o.get('order_number'), "customer": o.get('customer_name')} for o in b2b_without_gstin[:10]]
        })
        summary['warnings'] += 1
    
    summary['issues_found'] = len(issues)
    
    # Generate recommendations
    recommendations = []
    
    if summary['critical_issues'] > 0:
        recommendations.append("URGENT: Address critical issues immediately to ensure compliance")
    
    if any(i['type'] == 'missing_gst_on_sale' for i in issues):
        recommendations.append("Review sales without GST - may need invoice corrections or GST supplements")
    
    if any(i['type'] == 'duplicate_bill_number' for i in issues):
        recommendations.append("Investigate duplicate bill numbers - may indicate data import issues")
    
    if any(i['type'] == 'zero_unit_price' for i in issues):
        recommendations.append("Correct zero unit prices - affects inventory valuation and margins")
    
    if any(i['type'] == 'missing_gstin_b2b' for i in issues):
        recommendations.append("Collect GSTIN for B2B customers - required for GSTR-1 filing")
    
    if not recommendations:
        recommendations.append("No critical issues found. Continue regular monitoring.")
    
    return {
        "summary": summary,
        "issues": issues,
        "recommendations": recommendations
    }


async def generate_audit_analysis(audit_result: Dict, start_date: datetime, end_date: datetime) -> str:
    """Generate AI-powered audit analysis"""
    
    summary = audit_result['summary']
    issues = audit_result['issues']
    
    prompt = f"""As a senior Chartered Accountant, provide a concise audit summary for:

Period: {start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}

Financial Summary:
- Total Sales: ₹{summary['sales_total']:,.2f}
- Total Purchases: ₹{summary['purchase_total']:,.2f}
- GST Collected: ₹{summary['gst_collected']:,.2f}
- GST Paid: ₹{summary['gst_paid']:,.2f}
- Net GST: ₹{summary['gst_collected'] - summary['gst_paid']:,.2f}

Audit Findings:
- Total Issues: {summary['issues_found']}
- Critical Issues: {summary['critical_issues']}
- Warnings: {summary['warnings']}

Issue Details:
{chr(10).join([f"- {i['type']}: {i['message']}" for i in issues[:5]])}

Provide:
1. Overall assessment (1-2 sentences)
2. Key concerns (if any)
3. Immediate action items

Keep it concise and actionable (4-5 sentences max)."""

    try:
        chat = LlmChat(
            api_key=os.environ.get("EMERGENT_LLM_KEY"),
            session_id=f"audit_{datetime.now().timestamp()}",
            system_message="You are an expert CA providing audit assessments."
        ).with_model("openai", "gpt-4o")
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        if isinstance(response, dict):
            return response.get('content', response.get('message', ''))
        return str(response)
    except Exception as e:
        return f"Audit completed. {summary['issues_found']} issues found ({summary['critical_issues']} critical). Review the detailed findings above."


@router.get("/audit-history")
async def get_audit_history(
    limit: int = Query(default=10, le=50),
    db=Depends(get_db)
):
    """Get history of audit reports"""
    try:
        audits = await db.audit_reports.find(
            {},
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        return {
            "status": "success",
            "count": len(audits),
            "audits": audits
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit history: {str(e)}")


@router.get("/audit/{audit_id}")
async def get_audit_report(audit_id: str, db=Depends(get_db)):
    """Get a specific audit report"""
    try:
        audit = await db.audit_reports.find_one({"id": audit_id}, {"_id": 0})
        
        if not audit:
            raise HTTPException(status_code=404, detail="Audit report not found")
        
        return {
            "status": "success",
            "audit": audit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit report: {str(e)}")


# ==================== QUICK STATS ====================

@router.get("/quick-stats")
async def get_quick_stats(
    period: str = Query(default="month", regex="^(today|week|month|year)$"),
    db=Depends(get_db)
):
    """Get quick accounting statistics for dashboard"""
    try:
        today = datetime.now(timezone.utc)
        
        if period == "today":
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = (today - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "year":
            start_date = datetime(today.year, 1, 1, tzinfo=timezone.utc)
        else:  # month
            start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Get data
        sales_data = await get_sales_data(db, start_date, end_date)
        purchase_data = await get_purchase_data(db, start_date, end_date)
        expense_data = await get_expense_data(db, start_date, end_date)
        
        gross_profit = sales_data['total_sales'] - purchase_data['total_purchases'] - expense_data['total_expenses']
        
        return {
            "status": "success",
            "stats": {
                "total_sales": round(sales_data['total_sales'], 2),
                "total_purchases": round(purchase_data['total_purchases'], 2),
                "total_expenses": round(expense_data['total_expenses'], 2),
                "gross_profit": round(gross_profit, 2),
                "gst_collected": round(sales_data['total_tax'], 2),
                "input_tax_credit": round(purchase_data['input_tax_credit'], 2),
                "net_gst": round(sales_data['total_tax'] - purchase_data['input_tax_credit'], 2),
                "period": period.capitalize(),
                "period_start": start_date.strftime("%Y-%m-%d"),
                "period_end": end_date.strftime("%Y-%m-%d")
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")


# ==================== UNPAID INVOICES & PAYMENT FOLLOW-UPS ====================

@router.get("/unpaid-invoices")
async def get_unpaid_invoices(db=Depends(get_db)):
    """Get all unpaid/pending invoices for follow-up"""
    try:
        # Get offline invoices with pending payments
        unpaid_invoices = await db.offline_invoices.find({
            "$or": [
                {"payment_status": "pending"},
                {"payment_status": "partial"},
                {"payment_status": {"$exists": False}}
            ]
        }, {"_id": 0}).sort("created_at", -1).to_list(100)
        
        # Calculate aging
        today = datetime.now(timezone.utc)
        aged_invoices = {
            "0_30_days": [],
            "31_60_days": [],
            "61_90_days": [],
            "over_90_days": []
        }
        
        total_outstanding = 0
        
        for invoice in unpaid_invoices:
            created_at = invoice.get('created_at')
            if isinstance(created_at, str):
                try:
                    created_at = parse_date(created_at)
                except Exception:
                    created_at = today
            elif not created_at:
                created_at = today
            
            days_old = (today - created_at).days if created_at else 0
            amount = (invoice.get('total_amount', 0) or 0) - (invoice.get('amount_paid', 0) or 0)
            total_outstanding += amount
            
            invoice['days_old'] = days_old
            invoice['outstanding_amount'] = amount
            
            if days_old <= 30:
                aged_invoices["0_30_days"].append(invoice)
            elif days_old <= 60:
                aged_invoices["31_60_days"].append(invoice)
            elif days_old <= 90:
                aged_invoices["61_90_days"].append(invoice)
            else:
                aged_invoices["over_90_days"].append(invoice)
        
        return {
            "status": "success",
            "total_outstanding": round(total_outstanding, 2),
            "total_invoices": len(unpaid_invoices),
            "aging_summary": {
                "0_30_days": {"count": len(aged_invoices["0_30_days"]), "amount": sum(i.get('outstanding_amount', 0) for i in aged_invoices["0_30_days"])},
                "31_60_days": {"count": len(aged_invoices["31_60_days"]), "amount": sum(i.get('outstanding_amount', 0) for i in aged_invoices["31_60_days"])},
                "61_90_days": {"count": len(aged_invoices["61_90_days"]), "amount": sum(i.get('outstanding_amount', 0) for i in aged_invoices["61_90_days"])},
                "over_90_days": {"count": len(aged_invoices["over_90_days"]), "amount": sum(i.get('outstanding_amount', 0) for i in aged_invoices["over_90_days"])}
            },
            "invoices": unpaid_invoices[:50]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch unpaid invoices: {str(e)}")


@router.get("/overdue-vendor-payments")
async def get_overdue_vendor_payments(db=Depends(get_db)):
    """Get all overdue vendor/purchase payments"""
    try:
        # Get purchase bills with pending payments
        overdue_purchases = await db.purchase_bills.find({
            "$or": [
                {"payment_status": "pending"},
                {"payment_status": "partial"},
                {"payment_status": {"$exists": False}}
            ]
        }, {"_id": 0}).sort("bill_date", -1).to_list(100)
        
        today = datetime.now(timezone.utc)
        total_overdue = 0
        
        for purchase in overdue_purchases:
            bill_date = purchase.get('bill_date')
            if isinstance(bill_date, str):
                try:
                    bill_date = parse_date(bill_date)
                except Exception:
                    bill_date = today
            elif not bill_date:
                bill_date = today
            
            days_old = (today - bill_date).days if bill_date else 0
            due_date = purchase.get('due_date')
            
            if due_date:
                if isinstance(due_date, str):
                    try:
                        due_date = parse_date(due_date)
                    except Exception:
                        due_date = None
                if due_date:
                    days_overdue = (today - due_date).days
                else:
                    days_overdue = days_old - 30
            else:
                days_overdue = days_old - 30  # Assume 30 day payment terms
            
            purchase['days_overdue'] = max(0, days_overdue)
            purchase['outstanding_amount'] = (purchase.get('grand_total', 0) or purchase.get('total_amount', 0) or 0) - (purchase.get('amount_paid', 0) or 0)
            purchase['vendor_name'] = purchase.get('vendor', {}).get('name', 'Unknown Vendor') if isinstance(purchase.get('vendor'), dict) else purchase.get('vendor_name', 'Unknown')
            total_overdue += purchase['outstanding_amount']
        
        # Sort by days overdue
        overdue_purchases.sort(key=lambda x: x.get('days_overdue', 0), reverse=True)
        
        return {
            "status": "success",
            "total_overdue": round(total_overdue, 2),
            "total_purchases": len(overdue_purchases),
            "purchases": overdue_purchases[:50]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch overdue payments: {str(e)}")


@router.post("/send-payment-reminder")
async def send_payment_reminder(
    invoice_id: str,
    reminder_type: str = "friendly",
    db=Depends(get_db)
):
    """Send payment reminder for unpaid invoice"""
    try:
        from sendgrid_email_service import sendgrid_email_service
        
        invoice = await db.offline_invoices.find_one({"id": invoice_id}, {"_id": 0})
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        customer_email = invoice.get('customer_email')
        if not customer_email:
            raise HTTPException(status_code=400, detail="No customer email found")
        
        customer_name = invoice.get('customer_name', 'Valued Customer')
        invoice_number = invoice.get('invoice_number', invoice_id)
        amount = (invoice.get('total_amount', 0) or 0) - (invoice.get('amount_paid', 0) or 0)
        
        if reminder_type == "friendly":
            subject = f"Friendly Reminder: Invoice #{invoice_number} Payment Due"
            body = f"""
            <h2>Payment Reminder</h2>
            <p>Dear {customer_name},</p>
            <p>This is a friendly reminder that your invoice <strong>#{invoice_number}</strong> with an outstanding amount of <strong>₹{amount:,.2f}</strong> is due for payment.</p>
            <p>If you have already made the payment, please disregard this message.</p>
            <p>For any queries, please contact us at +91 98445 77440.</p>
            <p>Thank you for your business!</p>
            <p>Best regards,<br>Aditya Retail</p>
            """
        elif reminder_type == "urgent":
            subject = f"Urgent: Invoice #{invoice_number} Payment Overdue"
            body = f"""
            <h2 style="color: #dc2626;">Urgent Payment Required</h2>
            <p>Dear {customer_name},</p>
            <p>Your invoice <strong>#{invoice_number}</strong> with an outstanding amount of <strong>₹{amount:,.2f}</strong> is now overdue.</p>
            <p>Please arrange for immediate payment to avoid any inconvenience.</p>
            <p>Contact us at +91 98445 77440 for payment options.</p>
            <p>Best regards,<br>Aditya Retail</p>
            """
        else:
            subject = f"Final Notice: Invoice #{invoice_number} - Immediate Payment Required"
            body = f"""
            <h2 style="color: #dc2626;">Final Payment Notice</h2>
            <p>Dear {customer_name},</p>
            <p>This is a final notice for invoice <strong>#{invoice_number}</strong> with an outstanding amount of <strong>₹{amount:,.2f}</strong>.</p>
            <p>Please make the payment immediately to avoid further action.</p>
            <p>Contact: +91 98445 77440</p>
            <p>Aditya Retail</p>
            """
        
        result = sendgrid_email_service.send_email(
            to_email=customer_email,
            subject=subject,
            body=body,
            from_agent="sales",
            html=True
        )
        
        await db.payment_reminders.insert_one({
            "invoice_id": invoice_id,
            "invoice_number": invoice_number,
            "customer_email": customer_email,
            "reminder_type": reminder_type,
            "amount": amount,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "status": result.get('status')
        })
        
        return {
            "status": result.get('status'),
            "message": f"Payment reminder sent to {customer_email}",
            "reminder_type": reminder_type
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send reminder: {str(e)}")


# ==================== BANK STATEMENT ANALYSIS ====================

from fastapi import UploadFile, File
import csv
import io

@router.post("/analyze-bank-statement")
async def analyze_bank_statement(
    file: UploadFile = File(...),
    db=Depends(get_db)
):
    """Analyze uploaded bank statement (CSV format)"""
    try:
        content = await file.read()
        
        try:
            text_content = content.decode('utf-8')
        except Exception:
            text_content = content.decode('latin-1')
        
        csv_reader = csv.DictReader(io.StringIO(text_content))
        transactions = []
        
        for row in csv_reader:
            date = row.get('Date') or row.get('Transaction Date') or row.get('Txn Date') or row.get('date') or ''
            description = row.get('Description') or row.get('Particulars') or row.get('Narration') or row.get('description') or ''
            
            debit = row.get('Debit') or row.get('Withdrawal') or row.get('Dr') or '0'
            credit = row.get('Credit') or row.get('Deposit') or row.get('Cr') or '0'
            
            debit = float(str(debit).replace(',', '').replace('₹', '').strip() or '0')
            credit = float(str(credit).replace(',', '').replace('₹', '').strip() or '0')
            
            if debit > 0:
                transactions.append({
                    'date': date,
                    'description': description,
                    'amount': debit,
                    'type': 'debit',
                    'category': categorize_transaction(description)
                })
            if credit > 0:
                transactions.append({
                    'date': date,
                    'description': description,
                    'amount': credit,
                    'type': 'credit',
                    'category': categorize_transaction(description, is_credit=True)
                })
        
        if not transactions:
            raise HTTPException(status_code=400, detail="Could not parse any transactions from the file")
        
        analysis = analyze_transactions(transactions)
        
        analysis_id = f"BANK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        await db.bank_statement_analysis.insert_one({
            "id": analysis_id,
            "filename": file.filename,
            "transaction_count": len(transactions),
            "analysis": analysis,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "status": "success",
            "analysis_id": analysis_id,
            "transaction_count": len(transactions),
            "analysis": analysis
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze bank statement: {str(e)}")


def categorize_transaction(description: str, is_credit: bool = False) -> str:
    """Categorize transaction based on description"""
    desc_lower = description.lower()
    
    if is_credit:
        if any(word in desc_lower for word in ['neft', 'rtgs', 'imps', 'upi', 'transfer']):
            return "Bank Transfer (Income)"
        elif any(word in desc_lower for word in ['salary', 'wages']):
            return "Salary"
        elif any(word in desc_lower for word in ['interest']):
            return "Interest Income"
        elif any(word in desc_lower for word in ['refund']):
            return "Refund"
        else:
            return "Other Income"
    else:
        if any(word in desc_lower for word in ['rent', 'lease']):
            return "Rent"
        elif any(word in desc_lower for word in ['electricity', 'power', 'bescom']):
            return "Electricity"
        elif any(word in desc_lower for word in ['phone', 'mobile', 'airtel', 'jio', 'vodafone']):
            return "Phone/Internet"
        elif any(word in desc_lower for word in ['salary', 'wages', 'payroll']):
            return "Salary Expense"
        elif any(word in desc_lower for word in ['gst', 'tax', 'tds']):
            return "Tax Payment"
        elif any(word in desc_lower for word in ['amazon', 'flipkart', 'shopping']):
            return "Shopping"
        elif any(word in desc_lower for word in ['petrol', 'diesel', 'fuel', 'hp', 'indian oil']):
            return "Fuel"
        elif any(word in desc_lower for word in ['swiggy', 'zomato', 'food', 'restaurant']):
            return "Food & Dining"
        elif any(word in desc_lower for word in ['insurance', 'lic', 'hdfc life']):
            return "Insurance"
        elif any(word in desc_lower for word in ['emi', 'loan']):
            return "EMI/Loan"
        elif any(word in desc_lower for word in ['atm', 'cash']):
            return "Cash Withdrawal"
        elif any(word in desc_lower for word in ['neft', 'rtgs', 'imps', 'upi']):
            return "Bank Transfer (Payment)"
        else:
            return "Other Expense"


def analyze_transactions(transactions: List[dict]) -> dict:
    """Analyze transactions and generate insights"""
    
    total_credits = sum(t['amount'] for t in transactions if t['type'] == 'credit')
    total_debits = sum(t['amount'] for t in transactions if t['type'] == 'debit')
    
    expense_by_category = {}
    income_by_category = {}
    
    for t in transactions:
        category = t.get('category', 'Other')
        if t['type'] == 'debit':
            expense_by_category[category] = expense_by_category.get(category, 0) + t['amount']
        else:
            income_by_category[category] = income_by_category.get(category, 0) + t['amount']
    
    expense_by_category = dict(sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True))
    income_by_category = dict(sorted(income_by_category.items(), key=lambda x: x[1], reverse=True))
    
    insights = []
    
    top_expenses = list(expense_by_category.items())[:3]
    if top_expenses:
        insights.append(f"Your top 3 expense categories are: {', '.join([f'{cat} (₹{amt:,.0f})' for cat, amt in top_expenses])}")
    
    if total_credits > 0:
        savings_rate = ((total_credits - total_debits) / total_credits) * 100
        if savings_rate > 20:
            insights.append(f"Great job! Your savings rate is {savings_rate:.1f}%")
        elif savings_rate > 0:
            insights.append(f"Your savings rate is {savings_rate:.1f}%. Consider reducing discretionary spending.")
        else:
            insights.append(f"Warning: You're spending more than you're earning. Review your expenses immediately.")
    
    for category, amount in expense_by_category.items():
        if amount > total_credits * 0.3 and category not in ['Salary Expense', 'Bank Transfer (Payment)']:
            insights.append(f"Alert: {category} expenses (₹{amount:,.0f}) are over 30% of your income")
    
    return {
        "summary": {
            "total_income": round(total_credits, 2),
            "total_expenses": round(total_debits, 2),
            "net_savings": round(total_credits - total_debits, 2),
            "transaction_count": len(transactions)
        },
        "expense_breakdown": {k: round(v, 2) for k, v in expense_by_category.items()},
        "income_breakdown": {k: round(v, 2) for k, v in income_by_category.items()},
        "insights": insights,
        "recommendations": generate_recommendations(expense_by_category, total_credits, total_debits)
    }


def generate_recommendations(expenses: dict, income: float, total_expense: float) -> List[str]:
    """Generate actionable recommendations"""
    recommendations = []
    
    discretionary = sum(expenses.get(cat, 0) for cat in ['Shopping', 'Food & Dining', 'Entertainment'])
    if discretionary > income * 0.15:
        recommendations.append("Consider reducing discretionary spending (shopping, dining) to improve savings")
    
    if expenses.get('Fuel', 0) > income * 0.1:
        recommendations.append("Fuel expenses are high. Consider carpooling or using public transport")
    
    if income > total_expense:
        savings = income - total_expense
        recommendations.append(f"Build an emergency fund with your ₹{savings:,.0f} monthly savings (aim for 6 months of expenses)")
    
    if expenses.get('Tax Payment', 0) > 0:
        recommendations.append("Review tax-saving investments under Section 80C to optimize tax liability")
    
    return recommendations


@router.get("/bank-analysis-history")
async def get_bank_analysis_history(db=Depends(get_db)):
    """Get history of bank statement analyses"""
    try:
        analyses = await db.bank_statement_analysis.find(
            {},
            {"_id": 0}
        ).sort("created_at", -1).limit(20).to_list(20)
        
        return {
            "status": "success",
            "analyses": analyses
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analysis history: {str(e)}")
