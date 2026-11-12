"""
Unified Invoice Numbering System
Generates sequential invoice numbers for both online and offline orders
Format: ARO-YYYYMMDD-NNNN (e.g., ARO-20251115-0001)
"""

from datetime import datetime, timezone, timedelta
_IST = timezone(timedelta(hours=5, minutes=30))
from motor.motor_asyncio import AsyncIOMotorDatabase

async def generate_invoice_number(db: AsyncIOMotorDatabase, order_type: str = "online") -> str:
    """
    Generate a unique sequential invoice number
    
    Args:
        db: MongoDB database instance
        order_type: "online" or "offline" (for tracking purposes)
    
    Returns:
        Invoice number in format: ARO-YYYYMMDD-NNNN
    """
    today = datetime.now(timezone.utc)
    date_prefix = today.astimezone(_IST).strftime('%Y%m%d')
    
    # Use a counter collection for atomic increments
    counter_doc = await db.invoice_counters.find_one_and_update(
        {"key": "global"},
        {
            "$inc": {"sequence": 1},
            "$setOnInsert": {"created_at": today.isoformat()}
        },
        upsert=True,
        return_document=True  # Return updated document
    )
    
    sequence_number = counter_doc["sequence"]
    invoice_number = f"ARO-{date_prefix}-{sequence_number:04d}"
    
    # Log invoice generation for audit trail
    await db.invoice_audit_log.insert_one({
        "invoice_number": invoice_number,
        "order_type": order_type,
        "date": date_prefix,
        "sequence": sequence_number,
        "generated_at": today.isoformat()
    })
    
    return invoice_number

async def get_next_invoice_preview(db: AsyncIOMotorDatabase) -> str:
    """
    Preview what the next invoice number will be (without incrementing)
    """
    today = datetime.now(timezone.utc)
    date_prefix = today.astimezone(_IST).strftime('%Y%m%d')
    
    counter_doc = await db.invoice_counters.find_one({"key": "global"})
    
    if counter_doc:
        next_sequence = counter_doc["sequence"] + 1
    else:
        next_sequence = 1
    
    return f"ARO-{date_prefix}-{next_sequence:04d}"

async def get_invoice_stats(db: AsyncIOMotorDatabase, date: str = None) -> dict:
    """
    Get invoice statistics for a given date
    
    Args:
        date: Date in YYYYMMDD format. If None, uses today
    
    Returns:
        Dictionary with invoice statistics
    """
    if not date:
        date = datetime.now(timezone.utc).strftime('%Y%m%d')
    
    counter_doc = await db.invoice_counters.find_one({"date": date})
    
    if not counter_doc:
        return {
            "date": date,
            "total_invoices": 0,
            "online_invoices": 0,
            "offline_invoices": 0
        }
    
    # Count invoices by type
    online_count = await db.invoice_audit_log.count_documents({
        "date": date,
        "order_type": "online"
    })
    
    offline_count = await db.invoice_audit_log.count_documents({
        "date": date,
        "order_type": "offline"
    })
    
    return {
        "date": date,
        "total_invoices": counter_doc["sequence"],
        "online_invoices": online_count,
        "offline_invoices": offline_count,
        "last_invoice": f"ARO-{date}-{counter_doc['sequence']:04d}"
    }
