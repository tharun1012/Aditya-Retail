import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database import get_db

# Exact 9 document IDs confirmed against the Sales Invoices list — nothing else touched
IDS_TO_DELETE = [
    "f41794c1-a129-4c81-a8d9-cbc1cff87025",  # DAS0308/26-27 - SIDDEGOWDA
    "d03225c2-abd3-4d59-b362-d1013a15fa01",  # DAS0307/26-27 - venkatesan surya
    "7d94156b-867f-4c8f-9312-1d51b03ad7cd",  # DAS0003/26-27 - S SURESH
    "83ce3d5e-bae7-4b8c-93db-28756dc3e05a",  # DAS0002/26-27 - S SURESH
    "b9ad10df-e054-4306-89f6-cf735b160b01",  # DAS0001/26-27 - NIRANJAN
    "423c021c-4be4-4b73-bf60-e30909c8ad9c",  # DAS0004/26-27 - ProConnect Supply Chain Solutions Ltd
    "579d533c-b086-41a2-b10c-ff102c93cf18",  # DAS0017/26-27 - g s chandrappa
    "ded6b3c4-40eb-4a14-8c26-233b5dda45fb",  # DAS0012/26-27 - shylaja a
    "f23149af-54f3-4036-b190-8f4682fc9d4f",  # DAS0011/26-27 - BALA T
]

async def delete_das_invoices():
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
    asyncio.run(delete_das_invoices())
