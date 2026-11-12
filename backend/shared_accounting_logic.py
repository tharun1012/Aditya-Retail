"""
Shared accounting categorization and journal-entry logic.

Used by BOTH the nightly batch job (ai_daily_accountant.py) and the
real-time transaction hooks (called directly from invoice/SO/GRN/
purchase-bill/voucher creation routes). There is exactly ONE place
where "how do we categorize a sale vs a purchase bill vs a voucher"
and "how do we build a journal entry from it" is defined, so the two
code paths can never drift out of sync with each other the way the
duplicated field-mapping logic did across this codebase before.
"""
import uuid
from datetime import datetime, timezone


def categorize_single_transaction(txn: dict) -> dict:
    """Mutates and returns txn with accounting_category, debit_account,
    credit_account, skip_journal_entry, and GST fields set."""
    if txn["type"] in ["sale_online", "sale_offline"]:
        txn["accounting_category"] = "Sales Revenue"
        txn["debit_account"] = "Cash/Bank" if txn["payment_status"] == "paid" else "Accounts Receivable"
        txn["credit_account"] = "Sales Revenue"

        if any("return" in item.get("product_name", "").lower() for item in txn.get("items", [])):
            txn["accounting_category"] = "Sales Return"
            txn["debit_account"] = "Sales Return"
            txn["credit_account"] = "Cash/Bank"

    elif txn["type"] in ["purchase", "purchase_bill"]:
        txn["accounting_category"] = "Purchases"
        txn["debit_account"] = "Purchases/Inventory"
        txn["credit_account"] = "Cash/Bank" if txn["payment_status"] == "paid" else "Accounts Payable"

    elif txn["type"] == "expense":
        txn["accounting_category"] = f"Expense - {txn.get('category', 'General')}"
        txn["debit_account"] = f"Expense - {txn.get('category', 'General')}"
        txn["credit_account"] = "Cash/Bank"

    elif txn["type"] == "sales_order_booking":
        # A Sales Order is a booking, not yet a completed sale - shown live
        # for visibility (matches Tally's non-accounting SO voucher) but
        # does NOT post revenue. Revenue posts only when it becomes an
        # actual Invoice, to avoid double-counting.
        txn["accounting_category"] = "Sales Order (booked, not yet invoiced)"
        txn["skip_journal_entry"] = True

    elif txn["type"] == "grn":
        # Goods received but not yet billed - visibility only. The real
        # financial event is booked when the matching Purchase Bill is created.
        txn["accounting_category"] = "Goods Received (Pending Bill)"
        txn["skip_journal_entry"] = True

    elif txn["type"].startswith("voucher_"):
        # Collection/payment against a sale or purchase already booked
        # elsewhere - visibility only, avoids double-counting revenue.
        txn["accounting_category"] = f"Voucher - {txn['type'].replace('voucher_', '').title()}"
        txn["skip_journal_entry"] = True

    elif txn["type"] == "journal_voucher":
        # Already posts its own ledger entries at creation time.
        txn["accounting_category"] = "Journal Voucher (already posted)"
        txn["skip_journal_entry"] = True

    elif txn["type"] == "payment_receipt":
        # Payment against a Sales Order already booked as revenue.
        txn["accounting_category"] = "Payment Receipt (already recorded as revenue)"
        txn["skip_journal_entry"] = True

    else:
        # Safety net so an unexpected/future type never crashes downstream.
        txn["accounting_category"] = f"Uncategorized - {txn['type']}"
        txn["skip_journal_entry"] = True

    if txn.get("tax", 0) > 0:
        txn["gst_account"] = "GST Collected" if "sale" in txn["type"] else "GST Paid"
        if "cgst" not in txn or "sgst" not in txn:
            txn["cgst"] = txn["tax"] / 2
            txn["sgst"] = txn["tax"] / 2
        if "igst" not in txn:
            txn["igst"] = 0

    return txn


def build_journal_entry(txn: dict, created_by: str = "AI Daily Accountant"):
    """Returns a journal entry dict, or None if this transaction type
    should not post a new entry (skip_journal_entry set above)."""
    if txn.get("skip_journal_entry"):
        return None

    now_iso = datetime.now(timezone.utc).isoformat()

    journal_entry = {
        "id": str(uuid.uuid4()),
        "date": txn["date"],
        "transaction_id": txn["id"],
        "transaction_type": txn["type"],
        "description": f"{txn['accounting_category']} - {txn['id']}",
        "entries": [],
        "created_by": created_by,
        "created_at": now_iso
    }

    # The account holding the actual cash/bank movement gets the full
    # amount (incl. tax); the revenue/expense/inventory side gets the
    # amount net of tax. For a sale the cash-side account is the DEBIT
    # (Cash/Bank or Accounts Receivable); for a purchase/expense the
    # cash-side account is the CREDIT (Cash/Bank or Accounts Payable) -
    # opposite conventions, so this must branch on transaction type.
    if "sale" in txn["type"]:
        debit_amount = txn["amount"]
        credit_amount = txn["amount"] - txn.get("tax", 0)
    else:
        debit_amount = txn["amount"] - txn.get("tax", 0)
        credit_amount = txn["amount"]

    journal_entry["entries"].append({
        "account": txn["debit_account"],
        "debit": debit_amount,
        "credit": 0,
        "description": f"Transaction {txn['id']}"
    })

    if txn.get("tax", 0) > 0:
        if txn.get("is_inter_state") and txn.get("igst", 0) > 0:
            journal_entry["entries"].append({
                "account": f"{txn['gst_account']} - IGST",
                "debit": txn["igst"] if "purchase" in txn["type"] else 0,
                "credit": txn["igst"] if "sale" in txn["type"] else 0,
                "description": f"IGST on {txn['id']}"
            })
        else:
            journal_entry["entries"].append({
                "account": f"{txn['gst_account']} - CGST",
                "debit": txn["cgst"] if "purchase" in txn["type"] else 0,
                "credit": txn["cgst"] if "sale" in txn["type"] else 0,
                "description": f"CGST on {txn['id']}"
            })
            journal_entry["entries"].append({
                "account": f"{txn['gst_account']} - SGST",
                "debit": txn["sgst"] if "purchase" in txn["type"] else 0,
                "credit": txn["sgst"] if "sale" in txn["type"] else 0,
                "description": f"SGST on {txn['id']}"
            })

    journal_entry["entries"].append({
        "account": txn["credit_account"],
        "debit": 0,
        "credit": credit_amount,
        "description": f"Transaction {txn['id']}"
    })

    total_debit = sum(e["debit"] for e in journal_entry["entries"])
    total_credit = sum(e["credit"] for e in journal_entry["entries"])

    if abs(total_debit - total_credit) > 0.01:
        journal_entry["validation_error"] = f"Unbalanced entry: Debit={total_debit}, Credit={total_credit}"
    else:
        journal_entry["validated"] = True

    return journal_entry
