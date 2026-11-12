"""
Daily AI Accountant Agent
Runs nightly to automate accounting tasks:
- Categorize transactions
- Create journal entries
- Calculate GST liability
- Reconcile payments
- Generate daily summary
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List
import uuid
from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
from shared_accounting_logic import categorize_single_transaction, build_journal_entry

class DailyAccountantAgent:
    def __init__(self, db, target_date=None):
        self.db = db
        self.today = datetime.now(timezone.utc)
        self.yesterday = self.today - timedelta(days=1)
        # target_date: the date this run processes. Defaults to yesterday
        # (the nightly 2 AM job's original behavior, unchanged). Pass
        # today's date to process/report on today's transactions live.
        self.target_date = target_date if target_date is not None else self.yesterday
        
    async def run_daily_accounting(self):
        """Main entry point for daily accounting automation"""
        print(f"🤖 Daily AI Accountant started at {self.today.isoformat()}")
        
        results = {
            "date": self.target_date.date().isoformat(),
            "transactions_processed": 0,
            "journal_entries_created": 0,
            "gst_liability": 0,
            "reconciliation_status": {},
            "issues_found": [],
            "summary": ""
        }
        
        try:
            # Step 1: Read all yesterday's transactions
            transactions = await self.gather_daily_transactions()
            results["transactions_processed"] = len(transactions)
            
            # Step 2: Categorize transactions with AI
            categorized = await self.categorize_transactions(transactions)
            results["transactions"] = categorized
            
            # Step 3: Create journal entries
            journal_entries = await self.create_journal_entries(categorized)
            results["journal_entries_created"] = len(journal_entries)
            
            # Step 4: Calculate GST liability
            gst_data = await self.calculate_gst_liability(transactions)
            results["gst_liability"] = gst_data["net_liability"]
            
            # Step 5: Reconcile payments
            reconciliation = await self.reconcile_payments(transactions)
            results["reconciliation_status"] = reconciliation
            
            # Step 6: Flag issues
            issues = await self.flag_issues(transactions, reconciliation)
            results["issues_found"] = issues
            
            # Step 7: Generate daily summary
            summary = await self.generate_daily_summary(results, transactions, gst_data)
            results["summary"] = summary
            
            # Step 8: Save the report
            await self.save_daily_report(results)
            
            print(f"✅ Daily accounting completed: {results['transactions_processed']} transactions processed")
            return results
            
        except Exception as e:
            print(f"❌ Daily accountant error: {str(e)}")
            results["error"] = str(e)
            return results
    
    async def gather_daily_transactions(self) -> List[Dict]:
        """Gather all transactions for target_date (yesterday by default,
        or today when called from the real-time hook)."""
        yesterday_start = self.target_date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        yesterday_end = self.target_date.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()
        
        transactions = []
        
        # Get online orders
        online_orders = await self.db.orders.find({
            "created_at": {"$gte": yesterday_start, "$lte": yesterday_end},
            "order_status": {"$ne": "cancelled"}
        }, {"_id": 0}).to_list(None)
        
        for order in online_orders:
            transactions.append({
                "type": "sale_online",
                "id": order.get("order_number"),
                "amount": order.get("total_amount", 0),
                "tax": order.get("tax_amount", 0),
                "payment_method": order.get("payment_method", "online"),
                "payment_status": order.get("payment_status", "pending"),
                "date": order.get("created_at"),
                "customer": order.get("customer_details", {}).get("name", "Unknown"),
                "items": order.get("items", [])
            })
        
        # Get offline invoices
        offline_invoices = await self.db.offline_invoices.find({
            "created_at": {"$gte": yesterday_start, "$lte": yesterday_end}
        }, {"_id": 0}).to_list(None)
        
        for invoice in offline_invoices:
            transactions.append({
                "type": "sale_offline",
                "id": invoice.get("invoice_number"),
                "amount": invoice.get("total_amount", 0),
                "tax": invoice.get("tax_total", 0),
                "payment_method": invoice.get("payment_mode", "cash"),
                "payment_status": invoice.get("payment_status", "paid"),
                "date": invoice.get("created_at"),
                "customer": invoice.get("customer", {}).get("name", "Walk-in"),
                "items": invoice.get("items", [])
            })
        
        # Get purchases
        purchases = await self.db.purchases.find({
            "created_at": {"$gte": yesterday_start, "$lte": yesterday_end}
        }, {"_id": 0}).to_list(None)
        
        for purchase in purchases:
            transactions.append({
                "type": "purchase",
                "id": purchase.get("po_number"),
                "amount": purchase.get("total_amount", 0),
                "tax": purchase.get("tax_total", 0),
                "payment_method": purchase.get("payment_mode", "credit"),
                "payment_status": purchase.get("payment_status", "pending"),
                "date": purchase.get("created_at"),
                "vendor": purchase.get("vendor", {}).get("name", "Unknown"),
                "items": purchase.get("items", [])
            })
        
        # Get expenses
        expenses = await self.db.expenses.find({
            "expense_date": {"$gte": yesterday_start, "$lte": yesterday_end}
        }, {"_id": 0}).to_list(None)
        
        for expense in expenses:
            transactions.append({
                "type": "expense",
                "id": expense.get("expense_number"),
                "amount": expense.get("amount", 0),
                "tax": 0,
                "payment_method": expense.get("payment_mode", "cash"),
                "payment_status": "paid",
                "date": expense.get("expense_date"),
                "category": expense.get("category", "General"),
                "description": expense.get("description", "")
            })
        
        # Get GRNs (Goods Received Notes)
        grns = await self.db.grn.find({
            "created_at": {"$gte": yesterday_start, "$lte": yesterday_end}
        }, {"_id": 0}).to_list(None)
        
        for grn in grns:
            transactions.append({
                "type": "grn",
                "id": grn.get("grn_number"),
                "amount": grn.get("total_value", 0),
                "tax": 0,
                "payment_method": "n/a",
                "payment_status": grn.get("status", "completed"),
                "date": grn.get("created_at"),
                "vendor": grn.get("vendor_name", "Unknown"),
                "items": grn.get("items", [])
            })
        
        # Get purchase bills (replaces the old, unused "purchases" collection)
        purchase_bills = await self.db.purchase_bills.find({
            "created_at": {"$gte": yesterday_start, "$lte": yesterday_end}
        }, {"_id": 0}).to_list(None)
        
        for bill in purchase_bills:
            transactions.append({
                "type": "purchase_bill",
                "id": bill.get("bill_number"),
                "amount": bill.get("grand_total", 0),
                "tax": bill.get("total_tax", 0),
                "payment_method": bill.get("payment_mode", "credit"),
                "payment_status": bill.get("payment_status", "pending"),
                "date": bill.get("created_at"),
                "vendor": (bill.get("vendor") or {}).get("name", "Unknown"),
                "items": bill.get("items", [])
            })
        
        # Get vouchers (receipts, payments, contra entries, etc. logged via the voucher system)
        vouchers = await self.db.vouchers.find({
            "created_at": {"$gte": yesterday_start, "$lte": yesterday_end}
        }, {"_id": 0}).to_list(None)
        
        for voucher in vouchers:
            transactions.append({
                "type": f"voucher_{voucher.get('voucher_type', 'other')}",
                "id": voucher.get("voucher_number"),
                "amount": voucher.get("amount", 0),
                "tax": 0,
                "payment_method": voucher.get("payment_mode", "n/a"),
                "payment_status": voucher.get("approval_status", "pending"),
                "date": voucher.get("created_at"),
                "party": voucher.get("party_name", "Unknown"),
                "description": voucher.get("description", "")
            })
        
        # Get manual journal vouchers (double-entry adjustments posted directly to ledgers)
        journal_vouchers = await self.db.journal_vouchers.find({
            "created_at": {"$gte": yesterday_start, "$lte": yesterday_end}
        }, {"_id": 0}).to_list(None)
        
        for jv in journal_vouchers:
            transactions.append({
                "type": "journal_voucher",
                "id": jv.get("voucher_number"),
                "amount": jv.get("total_amount", 0),
                "tax": 0,
                "payment_method": "n/a",
                "payment_status": jv.get("status", "posted"),
                "date": jv.get("created_at"),
                "description": jv.get("narration", "")
            })
        
        # Get sales order payment receipts (advance/split payments against SOs)
        so_receipts = await self.db.so_payment_receipts.find({
            "created_at": {"$gte": yesterday_start, "$lte": yesterday_end}
        }, {"_id": 0}).to_list(None)
        
        for receipt in so_receipts:
            transactions.append({
                "type": "payment_receipt",
                "id": receipt.get("receipt_number"),
                "amount": receipt.get("total_amount", 0),
                "tax": 0,
                "payment_method": ",".join(p.get("mode", "") for p in receipt.get("payments", [])) or "n/a",
                "payment_status": "paid",
                "date": receipt.get("created_at"),
                "customer": (receipt.get("customer") or {}).get("name", "Unknown"),
                "so_number": receipt.get("so_number")
            })
        
        return transactions
    
    async def categorize_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """Categorize and validate transactions using the shared logic
        module (also used by real-time transaction hooks)."""
        return [categorize_single_transaction(txn) for txn in transactions]
    
    async def create_journal_entries(self, transactions: List[Dict]) -> List[Dict]:
        """Build and persist journal entries using the shared logic
        module (also used by real-time transaction hooks)."""
        journal_entries = []
        
        for txn in transactions:
            journal_entry = build_journal_entry(txn, created_by="AI Daily Accountant")
            if journal_entry is None:
                continue

            # Idempotency guard: skip if this transaction already has a
            # posted journal entry (from a prior Run Now, or from the
            # real-time hook firing at creation time). Prevents double-
            # counting revenue/tax when the same day is processed twice.
            existing = await self.db.journal_entries.find_one({
                "transaction_id": journal_entry["transaction_id"],
                "transaction_type": journal_entry["transaction_type"]
            })
            if existing:
                continue

            journal_entries.append(journal_entry)
            await self.db.journal_entries.insert_one(journal_entry)
        
        return journal_entries
    
    async def calculate_gst_liability(self, transactions: List[Dict]) -> Dict:
        """Calculate daily GST liability"""
        
        output_tax = sum(txn.get("tax", 0) for txn in transactions if "sale" in txn["type"])
        input_tax = sum(txn.get("tax", 0) for txn in transactions if txn["type"] in ["purchase", "purchase_bill"])
        
        net_liability = output_tax - input_tax
        
        gst_data = {
            "date": self.target_date.date().isoformat(),
            "output_tax": round(output_tax, 2),
            "input_tax": round(input_tax, 2),
            "net_liability": round(net_liability, 2),
            "cgst": round(net_liability / 2, 2),
            "sgst": round(net_liability / 2, 2),
            "calculated_at": self.today.isoformat()
        }
        
        # Save GST liability - upsert on date so re-running for the same
        # day (real-time refresh firing repeatedly, or a manual Run Now)
        # replaces the existing figure instead of piling up duplicates.
        date_str = gst_data["date"]
        existing = await self.db.gst_liability.find_one({"date": date_str})
        await self.db.gst_liability.update_one(
            {"date": date_str},
            {"$set": {
                "id": existing["id"] if existing else str(uuid.uuid4()),
                **gst_data
            }},
            upsert=True
        )
        
        return gst_data
    
    async def reconcile_payments(self, transactions: List[Dict]) -> Dict:
        """Reconcile payments with expected amounts"""
        
        reconciliation = {
            "total_expected": 0,
            "total_received": 0,
            "cash_expected": 0,
            "cash_received": 0,
            "online_expected": 0,
            "online_received": 0,
            "mismatches": []
        }
        
        for txn in transactions:
            if "sale" in txn["type"]:
                reconciliation["total_expected"] += txn["amount"]
                
                if txn["payment_status"] == "paid":
                    reconciliation["total_received"] += txn["amount"]
                    
                    if txn["payment_method"] == "cash":
                        reconciliation["cash_expected"] += txn["amount"]
                        reconciliation["cash_received"] += txn["amount"]
                    else:
                        reconciliation["online_expected"] += txn["amount"]
                        reconciliation["online_received"] += txn["amount"]
                else:
                    # Payment pending
                    reconciliation["mismatches"].append({
                        "transaction_id": txn["id"],
                        "issue": "Payment pending",
                        "expected": txn["amount"],
                        "received": 0
                    })
        
        reconciliation["difference"] = reconciliation["total_expected"] - reconciliation["total_received"]
        reconciliation["reconciled"] = abs(reconciliation["difference"]) < 1.0  # Within ₹1
        
        return reconciliation
    
    async def flag_issues(self, transactions: List[Dict], reconciliation: Dict) -> List[Dict]:
        """Flag potential issues and anomalies"""
        
        issues = []
        
        # Check for unreconciled amounts
        if not reconciliation["reconciled"]:
            issues.append({
                "type": "reconciliation_mismatch",
                "severity": "high",
                "message": f"Payment mismatch: ₹{reconciliation['difference']:,.2f}",
                "details": reconciliation
            })
        
        # Check for duplicate transactions
        transaction_ids = [txn["id"] for txn in transactions]
        duplicates = [tid for tid in transaction_ids if transaction_ids.count(tid) > 1]
        if duplicates:
            issues.append({
                "type": "duplicate_transaction",
                "severity": "medium",
                "message": f"Duplicate transaction IDs found: {', '.join(set(duplicates))}"
            })
        
        # Check for unusual amounts (>₹50,000 for expenses)
        high_expenses = [txn for txn in transactions if txn["type"] == "expense" and txn["amount"] > 50000]
        if high_expenses:
            issues.append({
                "type": "high_value_expense",
                "severity": "medium",
                "message": f"{len(high_expenses)} high-value expenses found (>₹50,000)",
                "transactions": [{"id": e["id"], "amount": e["amount"]} for e in high_expenses]
            })
        
        # Check for missing GST on sales
        sales_without_gst = [txn for txn in transactions if "sale" in txn["type"] and txn.get("tax", 0) == 0]
        if sales_without_gst:
            issues.append({
                "type": "missing_gst",
                "severity": "high",
                "message": f"{len(sales_without_gst)} sales transactions without GST",
                "transactions": [s["id"] for s in sales_without_gst]
            })
        
        return issues
    
    async def generate_daily_summary(self, results: Dict, transactions: List[Dict], gst_data: Dict) -> str:
        """Generate AI-powered daily summary"""
        
        sales_txns = [t for t in transactions if "sale" in t["type"]]
        purchase_txns = [t for t in transactions if t["type"] == "purchase"]
        expense_txns = [t for t in transactions if t["type"] == "expense"]
        
        total_sales = sum(t["amount"] for t in sales_txns)
        total_purchases = sum(t["amount"] for t in purchase_txns)
        total_expenses = sum(t["amount"] for t in expense_txns)
        
        # Use AI to generate insights
        prompt = f"""As a Chartered Accountant, provide a brief summary and insights for yesterday's business performance:

Date: {self.target_date.date().isoformat()}

Financial Data:
- Total Sales: ₹{total_sales:,.2f} ({len(sales_txns)} transactions)
- Total Purchases: ₹{total_purchases:,.2f} ({len(purchase_txns)} orders)
- Total Expenses: ₹{total_expenses:,.2f} ({len(expense_txns)} entries)
- Net GST Liability: ₹{gst_data['net_liability']:,.2f}
- Issues Found: {len(results['issues_found'])}

Provide:
1. Overall performance assessment
2. Key highlights
3. Any concerns or recommendations

Keep it concise (3-4 sentences)."""

        try:
            chat = LlmChat(
                api_key=os.environ.get("EMERGENT_LLM_KEY"),
                session_id=f"daily_accountant_{self.today.timestamp()}",
                system_message="You are an expert Chartered Accountant providing daily business insights."
            ).with_model("openai", "gpt-4o")
            
            response = await chat.send_message(UserMessage(text=prompt))
            ai_summary = response if isinstance(response, str) else getattr(response, 'content', str(response))
        except Exception as e:
            print(f"AI summary generation failed: {str(e)}")
            ai_summary = f"Standard daily summary: {len(transactions)} transactions processed. Sales: ₹{total_sales:,.2f}, Purchases: ₹{total_purchases:,.2f}, Expenses: ₹{total_expenses:,.2f}."
        
        return ai_summary
    
    async def save_daily_report(self, results: Dict):
        """Save the daily accounting report"""
        
        report_date_str = self.target_date.date().isoformat()
        report = {
            "id": str(uuid.uuid4()),
            "report_date": report_date_str,
            "generated_at": self.today.isoformat(),
            "generated_by": "AI Daily Accountant",
            **results
        }

        # Upsert on report_date so re-running for the same day (repeated
        # real-time updates, or a manual Run Now) refreshes one report
        # instead of piling up duplicates for the same date.
        await self.db.daily_accounting_reports.update_one(
            {"report_date": report_date_str},
            {"$set": report},
            upsert=True
        )

        print(f"📊 Daily report saved for {report_date_str}")
