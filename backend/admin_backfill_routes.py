from fastapi import APIRouter, Depends, Header, HTTPException
from database import get_db
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/admin", tags=["Admin Backfill"])

BACKFILL_SECRET = "d2e9d4d70b9c12d8b982e8a9b84103c8"


@router.post("/backfill-vouchers-from-receipts")
async def backfill_vouchers_from_receipts(
    live: bool = False,
    x_backfill_secret: str = Header(None),
    db = Depends(get_db)
):
    if x_backfill_secret != BACKFILL_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    existing_linked_ids = set()
    async for v in db.vouchers.find({"linked_document.id": {"$exists": True}}, {"linked_document.id": 1}):
        linked = v.get("linked_document") or {}
        if linked.get("id"):
            existing_linked_ids.add(linked["id"])

    to_create = []
    skipped = 0
    today = datetime.now(timezone.utc)

    async for r in db.so_payment_receipts.find({}):
        r_id = r.get("id")
        so_id = r.get("so_id")
        if r_id in existing_linked_ids or so_id in existing_linked_ids:
            skipped += 1
            continue

        customer = r.get("customer") or {}
        payments = r.get("payments") or []
        payment_mode = payments[0].get("mode") if payments and isinstance(payments[0], dict) else r.get("collected_by")
        created_at = r.get("created_at", today.isoformat())

        voucher_data = {
            "id": str(uuid.uuid4()),
            "voucher_number": r.get("receipt_number", f"BF-{r_id}"),
            "voucher_type": "receipt",
            "party_name": customer.get("name", "Unknown"),
            "amount": r.get("total_amount", 0),
            "payment_mode": payment_mode,
            "reference_number": r.get("receipt_number"),
            "description": r.get("remarks") or f"Backfilled SO payment: {r.get('so_number', so_id)}",
            "voucher_date": created_at,
            "created_by": "system_backfill",
            "linked_document": {
                "type": "sales_order",
                "number": r.get("so_number", so_id),
                "id": so_id or r_id
            },
            "is_advance": (r.get("receipt_index") == 1),
            "approval_status": "approved",
            "approved_by": None,
            "approved_at": None,
            "is_locked": True,
            "is_backfilled": True,
            "source_receipt_id": r_id,
            "store_code": r.get("store_code"),
            "store_name": r.get("store_name"),
            "created_at": created_at,
            "updated_at": today.isoformat()
        }
        to_create.append(voucher_data)

    result = {"skipped_already_linked": skipped, "vouchers_to_create": len(to_create), "sample": to_create[:10]}

    if live and to_create:
        insert_result = await db.vouchers.insert_many(to_create)
        result["inserted"] = len(insert_result.inserted_ids)
        result["mode"] = "LIVE"
    else:
        result["mode"] = "DRY_RUN"

    return result
