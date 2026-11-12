import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database import get_db

IDS_TO_DELETE = [
    "e9852d37-3b50-4d94-a25d-a8f7fdf24736",  # DASSO00147/26-27 - siddhartha Entertainers - 64500
    "23e16297-afb9-47b5-af99-d962b0c902b2",  # DASSO0149/26-27 - kinshuk roy - 1238
    "66d4290d-2594-40ff-bdbf-ae09d4df64af",  # DASSO0148/26-27 - nithya v - 1109
    "45dd4998-aae2-4021-a470-34d6930a961c",  # DASSO0147/26-27 - venkatesan surya - 1629
]

async def delete_das_sales_orders():
    db = await get_db()

    print(f"About to delete {len(IDS_TO_DELETE)} documents from offline_invoices...")

    found = []
    for doc_id in IDS_TO_DELETE:
        doc = await db.offline_invoices.find_one({"id": doc_id})
        if doc:
            found.append(doc_id)
            print(f"  FOUND: {doc.get('invoice_number')} - {doc.get('customer', {}).get('name')} - {doc_id}")
        else:
            print(f"  NOT FOUND (already gone?): {doc_id}")

    if len(found) != len(IDS_TO_DELETE):
        print(f"\nWARNING: only {len(found)} of {len(IDS_TO_DELETE)} IDs found. Aborting to be safe.")
        return

    confirm = input(f"\nType 'DELETE' to permanently remove these {len(found)} documents: ")
    if confirm.strip() != "DELETE":
        print("Aborted — no changes made.")
        return

    result = await db.offline_invoices.delete_many({"id": {"$in": found}})
    print(f"\nDeleted {result.deleted_count} documents.")

if __name__ == "__main__":
    asyncio.run(delete_das_sales_orders())
