from datetime import datetime, timezone, timedelta
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

IST = timezone(timedelta(hours=5, minutes=30))


async def next_ticket_number(db, prefix):
    """PREFIX-YYYYMMDD-NNNN: date is today (IST), NNNN is a continuous counter that never resets."""
    for _ in range(3):
        try:
            doc = await db.ticket_counters.find_one_and_update(
                {"_id": prefix}, {"$inc": {"seq": 1}}, upsert=True, return_document=ReturnDocument.AFTER)
            return f"{prefix}-{datetime.now(IST).strftime('%Y%m%d')}-{doc['seq']:04d}"
        except DuplicateKeyError:
            continue
    raise RuntimeError("Could not allocate ticket number")
