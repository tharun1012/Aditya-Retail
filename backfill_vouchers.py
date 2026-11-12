"""
Backfill vouchers for historical paid offline_invoices / sales_orders
that don't yet have a linked voucher.

Usage:
    python3 backfill_vouchers.py            # dry run - prints what it would create
    python3 backfill_vouchers.py --live      # actually inserts the vouchers
"""
import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'startup_template')

LIVE = "--live" in sys.argv
APPROVAL_STATUS_FOR_BACKFILL = "approved"  # change to "pending" if preferred


async def main():
    client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]

    print(f"Connected to DB: {DB_NAME}")
    print(f"Mode: {'LIVE (will write)' if LIVE else 'DRY RUN (no writes)'}")
    print()

    existing_linked_ids = set()
    async for v in db.vouchers.find({"linked_document.id": {"$exists": True}}, {"linked_document.id": 1}):
        linked = v.get("linked_document") or {}
        if linked.get("id"):
            existing_linked_ids.add(linked["id"])

    print(f"Existing vouchers with a linked_document.id: {len(existing_linked_ids)}")

    query = {"payment_details.advance_amount": {"$gt": 0}}
    cursor = db.offline_invoices.find(query)

    to_create = []
    skipped_already_linked = 0
    today = datetime.now(timezone.utc)
    receipt_prefix = "RCP-" + today.strftime("%Y%m%d")

    existing_count_today = await db.vouchers.count_documents({
        "voucher_type": "receipt",
        "created_at": {"$gte": today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()}
    })
    seq = existing_count_today

    async for inv in cursor:
        inv_id = inv.get("id")
        if inv_id in existing_linked_ids:
            skipped_already_linked += 1
            continue

        payment_details = inv.get("payment_details") or {}
        amount = payment_details.get("advance_amount", 0)
        document_type = inv.get("document_type", "invoice")
        invoice_number = inv.get("invoice_number") or inv.get("so_number") or inv_id

        seq += 1
        voucher_number = receipt_prefix + "-" + str(seq).zfill(4)

        voucher_data = {
            "id": str(uuid.uuid4()),
            "voucher_number": voucher_number,
            "voucher_type": "receipt",
            "party_name": (inv.get("customer") or {}).get("name", "Unknown"),
            "amount": amount,
            "payment_mode": inv.get("payment_mode"),
            "reference_number": payment_details.get("transaction_reference"),
            "description": "Backfilled payment for " + document_type + ": " + str(invoice_number),
            "voucher_date": inv.get("created_at", today.isoformat()),
            "created_by": "system_backfill",
            "linked_document": {
                "type": document_type,
                "number": invoice_number,
                "id": inv_id
            },
            "is_advance": payment_details.get("is_advance", False),
            "approval_status": APPROVAL_STATUS_FOR_BACKFILL,
            "approved_by": None,
            "approved_at": None,
            "is_locked": True,
            "is_backfilled": True,
            "created_at": today.isoformat(),
            "updated_at": today.isoformat()
        }
        to_create.append(voucher_data)

    print(f"Skipped (already linked): {skipped_already_linked}")
    print(f"Vouchers to create: {len(to_create)}")
    print()
    print("Sample of first 10:")
    for v in to_create[:10]:
        ld = v["linked_document"]
        print("  " + v["voucher_number"] + " | " + v["party_name"] + " | amount=" + str(v["amount"]) + " | linked=" + ld["type"] + ":" + str(ld["number"]))

    if LIVE:
        if to_create:
            result = await db.vouchers.insert_many(to_create)
            print()
            print("Inserted " + str(len(result.inserted_ids)) + " vouchers.")
        else:
            print()
            print("Nothing to insert.")
    else:
        print()
        print("Dry run only - no writes made. Re-run with --live to insert.")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
