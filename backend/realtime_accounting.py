"""
Real-time accounting event posting.

Call post_transaction_event() directly from a creation route (invoice,
SO, GRN, purchase bill, voucher, journal voucher, payment receipt)
right after the document is inserted, to post its journal entry and
update GST liability immediately instead of waiting for the nightly
batch. Uses the exact same categorization/journal-entry logic as the
nightly batch (shared_accounting_logic.py) so the two paths can never
disagree with each other.

GST liability is updated with an atomic $inc on a per-day document,
which is safe even if multiple transactions fire concurrently.
"""
from datetime import datetime, timezone
import uuid
from shared_accounting_logic import categorize_single_transaction, build_journal_entry


async def post_transaction_event(db, transaction_type: str, txn: dict):
    """
    txn must already be in the same shape gather_daily_transactions()
    builds, e.g.:
        {
            "type": "sale_offline",   # or sale_online / purchase_bill / grn / voucher_receipt / journal_voucher / payment_receipt
            "id": "ARH0064/26-27",
            "amount": 21000,
            "tax": 3203.39,
            "payment_method": "cash",
            "payment_status": "paid",
            "date": "2026-09-26T10:00:00+00:00",
            "items": [...],            # optional, used for return detection
            "category": "...",         # only for expenses
        }
    Returns the journal entry that was posted, or None if this
    transaction type is visibility-only and doesn't post one.
    """
    txn = dict(txn)  # don't mutate caller's dict
    txn["type"] = transaction_type

    categorized = categorize_single_transaction(txn)
    journal_entry = build_journal_entry(categorized, created_by="Realtime Accounting")

    if journal_entry is not None:
        # Idempotency guard: skip if this transaction already has a
        # posted journal entry (from a prior real-time call, or from
        # Run Now / the nightly batch already having processed today).
        existing = await db.journal_entries.find_one({
            "transaction_id": journal_entry["transaction_id"],
            "transaction_type": journal_entry["transaction_type"]
        })
        if existing:
            return existing
        await db.journal_entries.insert_one(journal_entry)

        # Update today's running GST liability atomically. "sale" types
        # add to output tax, purchase/purchase_bill add to input tax -
        # same rule calculate_gst_liability() uses in the nightly batch.
        tax = categorized.get("tax", 0)
        if tax:
            today_str = datetime.now(timezone.utc).date().isoformat()
            if "sale" in transaction_type:
                inc_field = "output_tax"
            elif transaction_type in ["purchase", "purchase_bill"]:
                inc_field = "input_tax"
            else:
                inc_field = None

            if inc_field:
                await db.gst_liability.update_one(
                    {"date": today_str},
                    {
                        "$inc": {inc_field: round(tax, 2)},
                        "$setOnInsert": {
                            "id": str(uuid.uuid4()),
                            "date": today_str,
                            "calculated_at": datetime.now(timezone.utc).isoformat()
                        }
                    },
                    upsert=True
                )
                # Recompute net/cgst/sgst from the running totals so they
                # stay consistent after this increment.
                doc = await db.gst_liability.find_one({"date": today_str})
                output_tax = doc.get("output_tax", 0)
                input_tax = doc.get("input_tax", 0)
                net = output_tax - input_tax
                await db.gst_liability.update_one(
                    {"date": today_str},
                    {"$set": {
                        "net_liability": round(net, 2),
                        "cgst": round(net / 2, 2),
                        "sgst": round(net / 2, 2)
                    }}
                )

    # Keep the Daily Accounting Reports page live: regenerate today's
    # report immediately so it reflects this transaction without waiting
    # for the nightly job or a manual "Run Now". Runs after the journal
    # entry/GST work above so a failure here never blocks those from
    # having already been posted.
    try:
        from ai_daily_accountant import DailyAccountantAgent
        agent = DailyAccountantAgent(db, target_date=datetime.now(timezone.utc))
        await agent.run_daily_accounting()
    except Exception as e:
        print(f"⚠️ Real-time daily report refresh failed: {e}")

    return journal_entry
