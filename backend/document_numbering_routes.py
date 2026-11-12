"""
Document Numbering Configuration Routes
Handles store-prefixed document numbering with admin control over sequences
"""
from fastapi import APIRouter, HTTPException, Depends
from pymongo import ReturnDocument
from typing import Optional, Dict, List
from datetime import datetime, timezone
from database import get_db
from admin_data_management_routes import verify_super_admin
from pydantic import BaseModel
import uuid
import re

router = APIRouter(prefix="/document-numbering", tags=["Document Numbering"])

# ============ MODELS ============

class DocumentTypeConfig(BaseModel):
    prefix: str  # e.g., "INV", "SO", "QT", "PO"
    description: str
    starting_number: int = 1
    current_number: int = 1
    # Free format template with placeholders
    custom_format: str = ""  # User's custom format string e.g., "ARPL/{STORE}/{PREFIX}/{FY}/{SEQ:4}"
    use_custom_format: bool = False  # Whether to use custom format or structured format
    # Structured format options (used when use_custom_format is False)
    format_template: str = "{store_code}-{prefix}-{year}-{sequence:04d}"
    include_store_code: bool = True
    include_year: bool = True
    year_format: str = "full"  # "full" (2026), "short" (26), "fy" (25-26)
    separator: str = "-"
    sequence_padding: int = 4  # Number of digits for sequence (e.g., 4 = 0001)

class StoreNumberingConfig(BaseModel):
    store_id: str
    store_code: str
    document_configs: Dict[str, DocumentTypeConfig]

class UpdateStartingNumber(BaseModel):
    document_type: str  # invoice, sales_order, quotation, purchase_order, voucher
    starting_number: int
    store_id: Optional[str] = None  # If None, resolved from store_code
    store_code: Optional[str] = None  # Preferred way for UI callers to identify the store

class UpdateDocumentFormat(BaseModel):
    document_type: str
    store_id: str
    prefix: Optional[str] = None
    custom_format: Optional[str] = None  # Free format string
    use_custom_format: Optional[bool] = None
    format_template: Optional[str] = None
    include_store_code: Optional[bool] = None
    include_year: Optional[bool] = None
    year_format: Optional[str] = None  # "full", "short", "fy"
    separator: Optional[str] = None
    sequence_padding: Optional[int] = None
    starting_number: Optional[int] = None

# Default document types
DEFAULT_DOCUMENT_TYPES = {
    "invoice": DocumentTypeConfig(
        prefix="INV",
        description="Sales Invoice",
        starting_number=1,
        current_number=1,
        custom_format="",
        use_custom_format=False,
        format_template="{store_code}{sep}{prefix}{sep}{year}{sep}{sequence}",
        include_store_code=True,
        include_year=True,
        year_format="full",
        separator="-",
        sequence_padding=4
    ),
    "sales_order": DocumentTypeConfig(
        prefix="SO",
        description="Sales Order",
        starting_number=1,
        current_number=1,
        custom_format="",
        use_custom_format=False,
        format_template="{store_code}{sep}{prefix}{sep}{year}{sep}{sequence}",
        include_store_code=True,
        include_year=True,
        year_format="full",
        separator="-",
        sequence_padding=4
    ),
    "quotation": DocumentTypeConfig(
        prefix="QT",
        description="Quotation",
        starting_number=1,
        current_number=1,
        custom_format="",
        use_custom_format=False,
        format_template="{store_code}{sep}{prefix}{sep}{year}{sep}{sequence}",
        include_store_code=True,
        include_year=True,
        year_format="full",
        separator="-",
        sequence_padding=4
    ),
    "purchase_order": DocumentTypeConfig(
        prefix="PO",
        description="Purchase Order",
        starting_number=1,
        current_number=1,
        custom_format="",
        use_custom_format=False,
        format_template="{store_code}{sep}{prefix}{sep}{year}{sep}{sequence}",
        include_store_code=True,
        include_year=True,
        year_format="full",
        separator="-",
        sequence_padding=4
    ),
    "voucher": DocumentTypeConfig(
        prefix="VCH",
        description="Payment Voucher",
        starting_number=1,
        current_number=1,
        custom_format="",
        use_custom_format=False,
        format_template="{store_code}{sep}{prefix}{sep}{year}{sep}{sequence}",
        include_store_code=True,
        include_year=True,
        year_format="full",
        separator="-",
        sequence_padding=4
    ),
    "delivery_challan": DocumentTypeConfig(
        prefix="DC",
        description="Delivery Challan",
        starting_number=1,
        current_number=1,
        custom_format="",
        use_custom_format=False,
        format_template="{store_code}{sep}{prefix}{sep}{year}{sep}{sequence}",
        include_store_code=True,
        include_year=True,
        year_format="full",
        separator="-",
        sequence_padding=4
    ),
    "credit_note": DocumentTypeConfig(
        prefix="CN",
        description="Credit Note",
        starting_number=1,
        current_number=1,
        custom_format="",
        use_custom_format=False,
        format_template="{store_code}{sep}{prefix}{sep}{year}{sep}{sequence}",
        include_store_code=True,
        include_year=True,
        year_format="full",
        separator="-",
        sequence_padding=4
    ),
    "debit_note": DocumentTypeConfig(
        prefix="DN",
        description="Debit Note",
        starting_number=1,
        current_number=1,
        custom_format="",
        use_custom_format=False,
        format_template="{store_code}{sep}{prefix}{sep}{year}{sep}{sequence}",
        include_store_code=True,
        include_year=True,
        year_format="full",
        separator="-",
        sequence_padding=4
    )
}

# ============ HELPER FUNCTIONS ============

def parse_custom_format(format_string: str, store_code: str, prefix: str, sequence: int, sequence_padding: int = 4) -> str:
    """
    Parse a custom format string and replace placeholders with actual values.
    
    Available placeholders:
    - {STORE} or {STORE_CODE} - Store code
    - {PREFIX} - Document prefix
    - {YEAR} or {YYYY} - Full year (2026)
    - {YY} - Short year (26)
    - {FY} - Financial year (25-26)
    - {MONTH} or {MM} - Month (01-12)
    - {DAY} or {DD} - Day (01-31)
    - {SEQ} - Sequence number
    - {SEQ:N} - Sequence with N digit padding (e.g., {SEQ:4} = 0001)
    
    Any other text is kept as-is.
    """
    import re
    from datetime import datetime
    
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    current_day = now.day
    
    # Calculate financial year (April to March)
    if current_month >= 4:
        fy_start = str(current_year)[-2:]
        fy_end = str(current_year + 1)[-2:]
    else:
        fy_start = str(current_year - 1)[-2:]
        fy_end = str(current_year)[-2:]
    
    result = format_string
    
    # Replace store code placeholders
    result = re.sub(r'\{STORE_CODE\}', store_code, result, flags=re.IGNORECASE)
    result = re.sub(r'\{STORE\}', store_code, result, flags=re.IGNORECASE)
    
    # Replace prefix
    result = re.sub(r'\{PREFIX\}', prefix, result, flags=re.IGNORECASE)
    
    # Replace year placeholders
    result = re.sub(r'\{YYYY\}', str(current_year), result, flags=re.IGNORECASE)
    result = re.sub(r'\{YEAR\}', str(current_year), result, flags=re.IGNORECASE)
    result = re.sub(r'\{YY\}', str(current_year)[-2:], result, flags=re.IGNORECASE)
    result = re.sub(r'\{FY\}', f"{fy_start}-{fy_end}", result, flags=re.IGNORECASE)
    
    # Replace month/day
    result = re.sub(r'\{MONTH\}', f"{current_month:02d}", result, flags=re.IGNORECASE)
    result = re.sub(r'\{MM\}', f"{current_month:02d}", result, flags=re.IGNORECASE)
    result = re.sub(r'\{DAY\}', f"{current_day:02d}", result, flags=re.IGNORECASE)
    result = re.sub(r'\{DD\}', f"{current_day:02d}", result, flags=re.IGNORECASE)
    
    # Replace sequence with custom padding {SEQ:N}
    seq_pattern = r'\{SEQ:(\d+)\}'
    match = re.search(seq_pattern, result, flags=re.IGNORECASE)
    if match:
        padding = int(match.group(1))
        result = re.sub(seq_pattern, str(sequence).zfill(padding), result, flags=re.IGNORECASE)
    
    # Replace simple sequence placeholder
    result = re.sub(r'\{SEQ\}', str(sequence).zfill(sequence_padding), result, flags=re.IGNORECASE)
    result = re.sub(r'\{SEQUENCE\}', str(sequence).zfill(sequence_padding), result, flags=re.IGNORECASE)
    
    return result

def extract_sequence_number(invoice_number: str):
    """
    Extract the real sequence number from a generated document number,
    regardless of format (FY-before-seq or FY-after-seq, with or without
    separators, custom or default template). Strips any financial-year
    shaped substring (e.g. "26-27") before searching, so it can never be
    mistaken for the sequence, then returns the longest remaining digit run.
    """
    if not invoice_number:
        return None
    fy_spans = {m.span() for m in re.finditer(r'\d{2}-\d{2}', invoice_number)}
    def in_fy(m):
        return any(m.start() >= s and m.end() <= e for s, e in fy_spans)
    candidates = [m for m in re.finditer(r'\d+', invoice_number) if not in_fy(m)]
    if not candidates:
        return None
    max_len = max(len(m.group(0)) for m in candidates)
    longest = [m for m in candidates if len(m.group(0)) == max_len]
    best = longest[-1]  # prefer the last occurrence when tied on length
    try:
        return int(best.group(0))
    except ValueError:
        return None


def find_sequence_match(invoice_number: str):
    """Same FY-aware logic as extract_sequence_number, but returns the
    regex Match object (not the int) so callers can splice the original
    string in place without touching the FY portion."""
    if not invoice_number:
        return None
    fy_spans = {m.span() for m in re.finditer(r'\d{2}-\d{2}', invoice_number)}
    def in_fy(m):
        return any(m.start() >= s and m.end() <= e for s, e in fy_spans)
    candidates = [m for m in re.finditer(r'\d+', invoice_number) if not in_fy(m)]
    if not candidates:
        return None
    max_len = max(len(m.group(0)) for m in candidates)
    longest = [m for m in candidates if len(m.group(0)) == max_len]
    return longest[-1]


@router.get("/admin/repair-counters")
async def repair_document_counters(
    store_code: Optional[str] = None,
    dry_run: bool = True,
    db = Depends(get_db),
    admin = Depends(verify_super_admin)
):
    """
    One-time repair: recompute each store/document-type's current_number
    from the actual invoice_number values present in offline_invoices,
    using the FY-aware sequence extractor (so a financial-year suffix like
    26-27 can never be mistaken for the real sequence). Safe to re-run --
    it always recomputes from source data rather than incrementing.
    Defaults to dry_run=true: reports what WOULD change without writing.
    Pass dry_run=false to actually apply the fix.
    """
    store_query = {"code": store_code} if store_code else {}
    stores = await db.stores.find(store_query).to_list(None)
    report = []

    for store in stores:
        store_id = store.get("id")
        s_code = store.get("code")
        numbering = await db.document_numbering.find_one({"store_id": store_id})
        if not numbering:
            continue
        doc_configs = numbering.get("document_configs", {})
        for doc_type in doc_configs.keys():
            docs = await db.offline_invoices.find(
                {"store_code": s_code, "document_type": doc_type},
                {"_id": 0, "invoice_number": 1}
            ).to_list(None)

            max_seq = 0
            for d in docs:
                seq = extract_sequence_number(d.get("invoice_number", ""))
                if seq is not None and seq > max_seq:
                    max_seq = seq

            stored = doc_configs[doc_type].get("current_number", 1)
            has_data = len(docs) > 0
            # current_number holds the NEXT sequence to assign (verified
            # against get_next_document_number: it uses the stored value
            # directly, then increments after). So the correct target is
            # max_seq + 1, NOT max_seq -- setting it to max_seq would
            # reissue a number that's already in use on a real document.
            # Only touch types that actually have real documents; a type
            # with zero documents has never drifted from its correct
            # default of 1.
            target = max_seq + 1
            needs_change = has_data and stored != target
            entry = {
                "store_code": s_code,
                "document_type": doc_type,
                "stored_current_number": stored,
                "computed_from_data": max_seq,
                "target_current_number": target if has_data else None,
                "document_count": len(docs),
                "will_change": needs_change
            }
            report.append(entry)

            if not dry_run and needs_change:
                await db.document_numbering.update_one(
                    {"store_id": store_id},
                    {"$set": {
                        f"document_configs.{doc_type}.current_number": target,
                        "updated_at": datetime.now(timezone.utc)
                    }}
                )

    changed = [r for r in report if r["will_change"]]
    return {
        "status": "success",
        "dry_run": dry_run,
        "total_checked": len(report),
        "total_changed": len(changed),
        "details": report
    }


async def initialize_store_numbering(db, store_id: str, store_code: str):
    """Initialize document numbering for a new store"""
    existing = await db.document_numbering.find_one({"store_id": store_id})
    if existing:
        return {k: v for k, v in existing.items() if k != "_id"}
    
    config = {
        "id": str(uuid.uuid4()),
        "store_id": store_id,
        "store_code": store_code,
        "document_configs": {k: v.dict() for k, v in DEFAULT_DOCUMENT_TYPES.items()},
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.document_numbering.insert_one(config)
    config.pop("_id", None)
    return config

def format_document_number(store_code: str, doc_config: dict, sequence: int) -> str:
    """Format a document number for a given sequence using the store's config."""
    prefix = doc_config.get("prefix", "DOC")
    sequence_padding = doc_config.get("sequence_padding", 4)
    use_custom_format = doc_config.get("use_custom_format", False)
    custom_format = doc_config.get("custom_format", "")

    if use_custom_format and custom_format:
        return parse_custom_format(custom_format, store_code, prefix, sequence, sequence_padding)

    current_year = datetime.now().year
    current_month = datetime.now().month
    separator = doc_config.get("separator", "-")
    include_store_code = doc_config.get("include_store_code", True)
    include_year = doc_config.get("include_year", True)
    year_format = doc_config.get("year_format", "full")

    parts = []
    if include_store_code and store_code:
        parts.append(store_code)
    if prefix:
        parts.append(prefix)
    if include_year:
        if year_format == "short":
            parts.append(str(current_year)[-2:])
        elif year_format == "fy":
            if current_month >= 4:
                parts.append(f"{str(current_year)[-2:]}-{str(current_year + 1)[-2:]}")
            else:
                parts.append(f"{str(current_year - 1)[-2:]}-{str(current_year)[-2:]}")
        else:
            parts.append(str(current_year))
    parts.append(str(sequence).zfill(sequence_padding))
    return separator.join(parts)


async def find_next_free_sequence(db, store_code: str, doc_config: dict, start_sequence: int):
    """Advance past sequences whose numbers already exist (heals counter drift)."""
    doc_number = format_document_number(store_code, doc_config, start_sequence)
    # A format without a sequence placeholder can never advance — bail out
    if format_document_number(store_code, doc_config, start_sequence + 1) == doc_number:
        return start_sequence, doc_number
    sequence = start_sequence
    for _ in range(2000):
        exists = await db.offline_invoices.find_one({"invoice_number": doc_number}, {"_id": 1})
        if not exists:
            return sequence, doc_number
        sequence += 1
        doc_number = format_document_number(store_code, doc_config, sequence)
    return sequence, doc_number


async def get_next_document_number(db, store_id: str, store_code: str, document_type: str) -> str:
    """
    Generate next document number for a store and document type.
    Supports both custom free-format and structured format.
    Skips numbers that already exist so the counter can never collide.
    """
    # Ensure numbering config exists for this store
    config = await db.document_numbering.find_one({"store_id": store_id})
    
    if not config:
        config = await initialize_store_numbering(db, store_id, store_code)
    
    doc_config = config.get("document_configs", {}).get(document_type)
    
    if not doc_config:
        # Use default if not configured — persist it so atomic $inc works
        doc_config = DEFAULT_DOCUMENT_TYPES.get(document_type, DEFAULT_DOCUMENT_TYPES["invoice"]).dict()
        await db.document_numbering.update_one(
            {"store_id": store_id},
            {"$set": {f"document_configs.{document_type}": doc_config}}
        )
    
    # Static formats (no sequence placeholder) can't advance — single shot
    static_format = (
        format_document_number(store_code, doc_config, 1)
        == format_document_number(store_code, doc_config, 2)
    )
    
    doc_number = None
    for _ in range(2000):
        # Atomic allocation: prevents duplicate numbers under concurrent creation
        updated = await db.document_numbering.find_one_and_update(
            {"store_id": store_id},
            {"$inc": {f"document_configs.{document_type}.current_number": 1},
             "$set": {"updated_at": datetime.now(timezone.utc)}},
            return_document=ReturnDocument.AFTER
        )
        sequence = updated["document_configs"][document_type]["current_number"] - 1
        doc_number = format_document_number(store_code, doc_config, sequence)
        if static_format:
            return doc_number
        exists = await db.offline_invoices.find_one({"invoice_number": doc_number}, {"_id": 1})
        if not exists:
            return doc_number
    
    return doc_number


async def release_cancelled_document_number(db, doc):
    """When a document is cancelled: if it holds the latest issued number for its
    store+type, roll the counter back so the next document reuses that number."""
    import re as _re
    num = doc.get("invoice_number") or ""
    m = _re.search(r'[A-Za-z]+?(\d{2,})', num)
    doc_type = doc.get("document_type", "invoice")
    store_code = doc.get("store_code")
    entry = {
        "id": str(uuid.uuid4()),
        "invoice_number": num,
        "document_type": doc_type,
        "store_code": store_code,
        "cancelled_at": datetime.now(timezone.utc).isoformat()
    }
    if not m:
        entry["sequence"] = None
        await db.cancelled_document_numbers.insert_one(entry)
        return {"released": False, "reason": "Could not parse sequence from number"}
    seq = int(m.group(1))
    entry["sequence"] = seq
    await db.cancelled_document_numbers.insert_one(entry)

    store = await db.stores.find_one({"code": store_code}) if store_code else None
    if not store:
        return {"released": False, "reason": "Store not found"}
    config = await db.document_numbering.find_one({"store_id": store["id"]})
    if not config:
        return {"released": False, "reason": "Numbering config not found"}
    current = config.get("document_configs", {}).get(doc_type, {}).get("current_number")
    if current == seq + 1:
        await db.document_numbering.update_one(
            {"store_id": store["id"]},
            {"$set": {
                f"document_configs.{doc_type}.current_number": seq,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        return {"released": True, "counter_rolled_back_to": seq, "number_to_reuse": num}
    return {"released": False, "reason": f"Not the latest number (counter at {current}); counter unchanged"}

# ============ ROUTES ============

@router.get("/config")
async def get_numbering_config(
    store_id: Optional[str] = None,
    db = Depends(get_db)
):
    """Get document numbering configuration for a store or all stores"""
    try:
        if store_id:
            config = await db.document_numbering.find_one({"store_id": store_id}, {"_id": 0})
            if not config:
                # Get store info and initialize
                store = await db.stores.find_one({"id": store_id})
                if store:
                    config = await initialize_store_numbering(db, store_id, store["code"])
                    config.pop("_id", None)
            return {"status": "success", "config": config}
        else:
            # Get all stores' numbering configs
            configs = await db.document_numbering.find({}, {"_id": 0}).to_list(None)
            return {"status": "success", "configs": configs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/initialize/{store_id}")
async def initialize_store_numbering_endpoint(
    store_id: str,
    db = Depends(get_db)
):
    """Initialize document numbering for a store"""
    try:
        store = await db.stores.find_one({"id": store_id})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        config = await initialize_store_numbering(db, store_id, store["code"])
        config.pop("_id", None)
        
        return {
            "status": "success",
            "message": f"Document numbering initialized for store {store['name']}",
            "config": config
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/starting-number")
async def update_starting_number(
    update: UpdateStartingNumber,
    db = Depends(get_db)
):
    """Update starting number for a document type (Admin only)"""
    try:
        if update.document_type not in DEFAULT_DOCUMENT_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid document type. Valid types: {list(DEFAULT_DOCUMENT_TYPES.keys())}"
            )
        
        if update.starting_number < 1:
            raise HTTPException(status_code=400, detail="Starting number must be at least 1")

        resolved_store_id = update.store_id
        if not resolved_store_id and update.store_code:
            store = await db.stores.find_one({"code": update.store_code})
            if not store:
                raise HTTPException(status_code=404, detail=f"Store '{update.store_code}' not found")
            resolved_store_id = store.get("id")

        if resolved_store_id:
            # Update for specific store
            result = await db.document_numbering.update_one(
                {"store_id": resolved_store_id},
                {"$set": {
                    f"document_configs.{update.document_type}.starting_number": update.starting_number,
                    f"document_configs.{update.document_type}.current_number": update.starting_number,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Store numbering config not found")
            
            message = f"Starting number for {update.document_type} updated to {update.starting_number} for store"
        else:
            # Update for all stores
            result = await db.document_numbering.update_many(
                {},
                {"$set": {
                    f"document_configs.{update.document_type}.starting_number": update.starting_number,
                    f"document_configs.{update.document_type}.current_number": update.starting_number,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            
            message = f"Starting number for {update.document_type} updated to {update.starting_number} for all stores"
        
        return {
            "status": "success",
            "message": message
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config/{store_id}")
async def update_store_numbering_config(
    store_id: str,
    document_type: str,
    config_update: dict,
    db = Depends(get_db)
):
    """Update document numbering configuration for a store"""
    try:
        if document_type not in DEFAULT_DOCUMENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid document type. Valid types: {list(DEFAULT_DOCUMENT_TYPES.keys())}"
            )
        
        update_data = {"updated_at": datetime.now(timezone.utc)}
        
        # Extended allowed fields to include custom format options
        allowed_fields = [
            "prefix", "description", "starting_number", "current_number", 
            "format_template", "custom_format", "use_custom_format",
            "include_store_code", "include_year", "year_format", 
            "separator", "sequence_padding"
        ]
        for field in allowed_fields:
            if field in config_update:
                update_data[f"document_configs.{document_type}.{field}"] = config_update[field]
        
        result = await db.document_numbering.update_one(
            {"store_id": store_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Store numbering config not found")
        
        return {
            "status": "success",
            "message": f"Configuration updated for {document_type}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/format")
async def update_document_format(
    update: UpdateDocumentFormat,
    db = Depends(get_db)
):
    """
    Update complete document numbering format for a document type.
    Supports both custom free-format and structured format.
    """
    try:
        if update.document_type not in DEFAULT_DOCUMENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid document type. Valid types: {list(DEFAULT_DOCUMENT_TYPES.keys())}"
            )
        
        # Build update document
        update_data = {"updated_at": datetime.now(timezone.utc)}
        
        # Custom format fields
        if update.custom_format is not None:
            if (update.use_custom_format or update.custom_format) and "{SEQ" not in update.custom_format:
                raise HTTPException(
                    status_code=400,
                    detail="Custom format must include the {SEQ} placeholder (e.g. {STORE}{SEQ:4}/{FY}) — otherwise every document would get the same number"
                )
            update_data[f"document_configs.{update.document_type}.custom_format"] = update.custom_format
        
        if update.use_custom_format is not None:
            update_data[f"document_configs.{update.document_type}.use_custom_format"] = update.use_custom_format
        
        # Structured format fields
        if update.prefix is not None:
            update_data[f"document_configs.{update.document_type}.prefix"] = update.prefix
        
        if update.include_store_code is not None:
            update_data[f"document_configs.{update.document_type}.include_store_code"] = update.include_store_code
        
        if update.include_year is not None:
            update_data[f"document_configs.{update.document_type}.include_year"] = update.include_year
        
        if update.year_format is not None:
            if update.year_format not in ["full", "short", "fy"]:
                raise HTTPException(status_code=400, detail="Year format must be 'full', 'short', or 'fy'")
            update_data[f"document_configs.{update.document_type}.year_format"] = update.year_format
        
        if update.separator is not None:
            update_data[f"document_configs.{update.document_type}.separator"] = update.separator
        
        if update.sequence_padding is not None:
            if update.sequence_padding < 1 or update.sequence_padding > 10:
                raise HTTPException(status_code=400, detail="Sequence padding must be between 1 and 10")
            update_data[f"document_configs.{update.document_type}.sequence_padding"] = update.sequence_padding
        
        if update.starting_number is not None:
            if update.starting_number < 1:
                raise HTTPException(status_code=400, detail="Starting number must be at least 1")
            update_data[f"document_configs.{update.document_type}.starting_number"] = update.starting_number
            update_data[f"document_configs.{update.document_type}.current_number"] = update.starting_number
        
        result = await db.document_numbering.update_one(
            {"store_id": update.store_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Store numbering config not found")
        
        # Get updated config for preview
        config = await db.document_numbering.find_one({"store_id": update.store_id}, {"_id": 0})
        store = await db.stores.find_one({"id": update.store_id})
        
        # Generate preview of next number
        doc_config = config.get("document_configs", {}).get(update.document_type, {})
        preview = generate_number_preview(store.get("code", ""), doc_config)
        
        return {
            "status": "success",
            "message": f"Format updated for {update.document_type}",
            "preview": preview,
            "config": doc_config
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def generate_number_preview(store_code: str, doc_config: dict) -> str:
    """Generate a preview of what the document number will look like"""
    sequence = doc_config.get("current_number", 1)
    prefix = doc_config.get("prefix", "DOC")
    sequence_padding = doc_config.get("sequence_padding", 4)
    use_custom_format = doc_config.get("use_custom_format", False)
    custom_format = doc_config.get("custom_format", "")
    
    # Check if using custom format
    if use_custom_format and custom_format:
        return parse_custom_format(custom_format, store_code, prefix, sequence, sequence_padding)
    
    # Use structured format
    current_year = datetime.now().year
    current_month = datetime.now().month
    separator = doc_config.get("separator", "-")
    include_store_code = doc_config.get("include_store_code", True)
    include_year = doc_config.get("include_year", True)
    year_format = doc_config.get("year_format", "full")
    
    parts = []
    
    if include_store_code and store_code:
        parts.append(store_code)
    
    if prefix:
        parts.append(prefix)
    
    if include_year:
        if year_format == "short":
            parts.append(str(current_year)[-2:])
        elif year_format == "fy":
            if current_month >= 4:
                parts.append(f"{str(current_year)[-2:]}-{str(current_year + 1)[-2:]}")
            else:
                parts.append(f"{str(current_year - 1)[-2:]}-{str(current_year)[-2:]}")
        else:
            parts.append(str(current_year))
    
    parts.append(str(sequence).zfill(sequence_padding))
    
    return separator.join(parts)


@router.get("/preview/{store_id}/{document_type}")
async def preview_next_number(
    store_id: str,
    document_type: str,
    db = Depends(get_db)
):
    """Preview what the next document number will be (without incrementing)"""
    try:
        if document_type not in DEFAULT_DOCUMENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid document type. Valid types: {list(DEFAULT_DOCUMENT_TYPES.keys())}"
            )
        
        store = await db.stores.find_one({"id": store_id})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        config = await db.document_numbering.find_one({"store_id": store_id})
        
        if not config:
            config = await initialize_store_numbering(db, store_id, store["code"])
        
        doc_config = config.get("document_configs", {}).get(document_type, {})
        
        # Skip past numbers that already exist and self-heal the stored counter
        start_seq = doc_config.get("current_number", 1)
        free_seq, preview_number = await find_next_free_sequence(db, store["code"], doc_config, start_seq)
        if free_seq != start_seq:
            await db.document_numbering.update_one(
                {"store_id": store_id},
                {"$set": {
                    f"document_configs.{document_type}.current_number": free_seq,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
        
        return {
            "status": "success",
            "document_type": document_type,
            "preview": preview_number,
            "config": doc_config
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/types")
async def get_document_types():
    """Get all available document types"""
    return {
        "status": "success",
        "document_types": {
            k: {"prefix": v.prefix, "description": v.description}
            for k, v in DEFAULT_DOCUMENT_TYPES.items()
        }
    }



@router.post("/sync-sequences")
async def sync_all_sequences(db = Depends(get_db)):
    """
    Sync all document sequence numbers based on actual document counts.
    This fixes issues where the counter got out of sync with actual documents.
    """
    try:
        results = []
        
        # Get all stores
        stores = await db.stores.find({}, {"_id": 0}).to_list(None)
        
        for store in stores:
            store_id = store.get("id")
            store_code = store.get("code")
            
            if not store_id or not store_code:
                continue
            
            # Get or create document numbering config
            config = await db.document_numbering.find_one({"store_id": store_id})
            if not config:
                config = await initialize_store_numbering(db, store_id, store_code)
            
            store_result = {
                "store_code": store_code,
                "updates": []
            }
            
            # Document types to sync
            doc_types = ["invoice", "sales_order", "quotation", "delivery_challan", "credit_note", "debit_note"]
            
            for doc_type in doc_types:
                # Count actual documents of this type for this store
                if doc_type in ["invoice", "sales_order", "quotation"]:
                    count = await db.offline_invoices.count_documents({
                        "store_code": store_code,
                        "document_type": doc_type
                    })
                elif doc_type == "delivery_challan":
                    count = await db.delivery_challans.count_documents({
                        "store_code": store_code
                    })
                else:
                    count = await db.offline_invoices.count_documents({
                        "store_code": store_code,
                        "document_type": doc_type
                    })
                
                # The next number should be count + 1
                new_sequence = count + 1
                
                # Get current sequence from config
                current_sequence = config.get("document_configs", {}).get(doc_type, {}).get("current_number", 1)
                
                # Only update if the count is higher than current sequence
                # (don't decrease the sequence, just increase if needed)
                if new_sequence > current_sequence:
                    await db.document_numbering.update_one(
                        {"store_id": store_id},
                        {"$set": {
                            f"document_configs.{doc_type}.current_number": new_sequence,
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }}
                    )
                    store_result["updates"].append({
                        "doc_type": doc_type,
                        "old_sequence": current_sequence,
                        "new_sequence": new_sequence,
                        "actual_count": count
                    })
            
            if store_result["updates"]:
                results.append(store_result)
        
        return {
            "status": "success",
            "message": f"Synced sequences for {len(results)} stores",
            "details": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get("/sync-preview")
async def preview_sync(db = Depends(get_db)):
    """
    Preview what changes would be made by sync-sequences.
    Does not modify any data.
    """
    try:
        results = []
        
        stores = await db.stores.find({}, {"_id": 0}).to_list(None)
        
        for store in stores:
            store_id = store.get("id")
            store_code = store.get("code")
            
            if not store_id or not store_code:
                continue
            
            config = await db.document_numbering.find_one({"store_id": store_id})
            
            store_result = {
                "store_code": store_code,
                "store_name": store.get("name", store_code),
                "documents": []
            }
            
            doc_types = ["invoice", "sales_order", "quotation", "delivery_challan"]
            
            for doc_type in doc_types:
                if doc_type in ["invoice", "sales_order", "quotation"]:
                    count = await db.offline_invoices.count_documents({
                        "store_code": store_code,
                        "document_type": doc_type
                    })
                elif doc_type == "delivery_challan":
                    count = await db.delivery_challans.count_documents({
                        "store_code": store_code
                    })
                else:
                    count = 0
                
                current_sequence = 1
                if config:
                    current_sequence = config.get("document_configs", {}).get(doc_type, {}).get("current_number", 1)
                
                next_sequence = count + 1
                needs_update = next_sequence > current_sequence
                
                store_result["documents"].append({
                    "type": doc_type,
                    "actual_count": count,
                    "current_counter": current_sequence,
                    "should_be": next_sequence,
                    "needs_update": needs_update
                })
            
            results.append(store_result)
        
        return {
            "status": "success",
            "stores": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-from-highest")
async def sync_from_highest_numbers(db = Depends(get_db)):
    """
    Sync sequence counters based on the HIGHEST document number found.
    This is useful after manually editing document numbers.
    
    It extracts the numeric part from document numbers like:
    - HRBR/INV/2526/0045 → 45
    - HRBR/SO/2526/0123 → 123
    
    And sets the counter to highest + 1
    """
    import re
    
    try:
        results = []
        
        stores = await db.stores.find({}, {"_id": 0}).to_list(None)
        
        for store in stores:
            store_id = store.get("id")
            store_code = store.get("code")
            
            if not store_id or not store_code:
                continue
            
            store_result = {
                "store_code": store_code,
                "store_name": store.get("name", store_code),
                "updates": []
            }
            
            # Ensure document_numbering config exists
            config = await db.document_numbering.find_one({"store_id": store_id})
            if not config:
                config = await initialize_store_numbering(db, store_id, store_code)
            
            # Document types and their number fields
            doc_configs = [
                {"type": "invoice", "collection": "offline_invoices", "number_field": "invoice_number", "filter": {"store_code": store_code, "document_type": "invoice"}},
                {"type": "sales_order", "collection": "offline_invoices", "number_field": "invoice_number", "filter": {"store_code": store_code, "document_type": "sales_order"}},
                {"type": "quotation", "collection": "offline_invoices", "number_field": "invoice_number", "filter": {"store_code": store_code, "document_type": "quotation"}},
                {"type": "delivery_challan", "collection": "delivery_challans", "number_field": "challan_number", "filter": {"store_code": store_code}},
            ]
            
            for doc_config in doc_configs:
                doc_type = doc_config["type"]
                collection_name = doc_config["collection"]
                number_field = doc_config["number_field"]
                filter_query = doc_config["filter"]
                
                # Get all documents of this type
                collection = db[collection_name]
                documents = await collection.find(filter_query, {"_id": 0, number_field: 1}).to_list(None)
                
                highest_number = 0
                highest_doc_number = None
                
                for doc in documents:
                    doc_number = doc.get(number_field)
                    if not doc_number:
                        continue
                    
                    # Extract numeric part from document number
                    # Handles formats like: HRBR/INV/2526/0045, HRBR-INV-2526-0045, INV/0045, etc.
                    doc_str = str(doc_number)
                    # Formats seen in this data: "BNS0010/26-27" (seq before the "/",
                    # FY after) and legacy "BNS-INV-2026-0001" (seq is the last group,
                    # no "/"). Handle both: if there's a "/", the sequence is the last
                    # number in the part BEFORE it; otherwise take the last number overall.
                    if '/' in doc_str:
                        numbers = re.findall(r'\d+', doc_str.split('/')[0])
                    else:
                        numbers = re.findall(r'\d+', doc_str)
                    if numbers:
                        last_number = int(numbers[-1])
                        if last_number > highest_number:
                            highest_number = last_number
                            highest_doc_number = doc_number
                
                # Get current counter
                current_counter = config.get("document_configs", {}).get(doc_type, {}).get("current_number", 1)
                
                # New counter should be highest + 1
                new_counter = highest_number + 1
                
                if new_counter > current_counter:
                    # Update the counter
                    await db.document_numbering.update_one(
                        {"store_id": store_id},
                        {"$set": {
                            f"document_configs.{doc_type}.current_number": new_counter,
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }}
                    )
                    
                    store_result["updates"].append({
                        "doc_type": doc_type,
                        "highest_found": highest_doc_number,
                        "highest_number": highest_number,
                        "old_counter": current_counter,
                        "new_counter": new_counter
                    })
            
            if store_result["updates"]:
                results.append(store_result)
        
        return {
            "status": "success",
            "message": f"Synced sequences for {len(results)} stores based on highest document numbers",
            "details": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get("/sync-from-highest-preview")
async def preview_sync_from_highest(db = Depends(get_db)):
    """
    Preview what sync-from-highest would do.
    Shows the highest document number found for each type.
    """
    import re
    
    try:
        results = []
        
        stores = await db.stores.find({}, {"_id": 0}).to_list(None)
        
        for store in stores:
            store_id = store.get("id")
            store_code = store.get("code")
            
            if not store_id or not store_code:
                continue
            
            config = await db.document_numbering.find_one({"store_id": store_id})
            
            store_result = {
                "store_code": store_code,
                "store_name": store.get("name", store_code),
                "documents": []
            }
            
            doc_configs = [
                {"type": "invoice", "collection": "offline_invoices", "number_field": "invoice_number", "filter": {"store_code": store_code, "document_type": "invoice"}},
                {"type": "sales_order", "collection": "offline_invoices", "number_field": "invoice_number", "filter": {"store_code": store_code, "document_type": "sales_order"}},
                {"type": "quotation", "collection": "offline_invoices", "number_field": "invoice_number", "filter": {"store_code": store_code, "document_type": "quotation"}},
                {"type": "delivery_challan", "collection": "delivery_challans", "number_field": "challan_number", "filter": {"store_code": store_code}},
            ]
            
            for doc_config in doc_configs:
                doc_type = doc_config["type"]
                collection_name = doc_config["collection"]
                number_field = doc_config["number_field"]
                filter_query = doc_config["filter"]
                
                collection = db[collection_name]
                documents = await collection.find(filter_query, {"_id": 0, number_field: 1}).to_list(None)
                
                highest_number = 0
                highest_doc_number = None
                
                for doc in documents:
                    doc_number = doc.get(number_field)
                    if not doc_number:
                        continue
                    
                    doc_str = str(doc_number)
                    if '/' in doc_str:
                        numbers = re.findall(r'\d+', doc_str.split('/')[0])
                    else:
                        numbers = re.findall(r'\d+', doc_str)
                    if numbers:
                        last_number = int(numbers[-1])
                        if last_number > highest_number:
                            highest_number = last_number
                            highest_doc_number = doc_number
                
                current_counter = 1
                if config:
                    current_counter = config.get("document_configs", {}).get(doc_type, {}).get("current_number", 1)
                
                new_counter = highest_number + 1
                needs_update = new_counter > current_counter
                
                store_result["documents"].append({
                    "type": doc_type,
                    "total_docs": len(documents),
                    "highest_doc_number": highest_doc_number,
                    "highest_sequence": highest_number,
                    "current_counter": current_counter,
                    "will_set_to": new_counter,
                    "needs_update": needs_update
                })
            
            results.append(store_result)
        
        return {
            "status": "success",
            "stores": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RenumberAfterDeleteRequest(BaseModel):
    """Close numbering gaps after a mid-sequence delete, by shifting
    subsequent documents down so the sequence is contiguous again."""
    store_code: str
    document_type: str = "invoice"
    dry_run: bool = True
    after_seq: Optional[int] = None  # only touch docs with seq > after_seq;
    # scopes the fix to a single recent gap instead of compacting all
    # historical gaps in the store's entire numbering history.


@router.post("/admin/renumber-after-delete")
async def renumber_after_delete(
    req: RenumberAfterDeleteRequest,
    db = Depends(get_db),
    admin = Depends(verify_super_admin)
):
    """
    Renumber all documents of a store/type into a contiguous sequence,
    closing any gaps left by mid-sequence deletes. Defaults to dry_run=true.

    WARNING: this changes invoice_number on existing documents. Any other
    collection that stores invoice_number as a copied string (not the doc's
    'id') will go stale unless patched separately - this endpoint reports
    such references but does not touch them.
    """
    docs = await db.offline_invoices.find(
        {"store_code": req.store_code, "document_type": req.document_type}
    ).to_list(None)

    parsed = []
    unparsed = []
    for d in docs:
        seq = extract_sequence_number(d.get("invoice_number", ""))
        if seq is None:
            unparsed.append(d.get("invoice_number"))
            continue
        parsed.append((seq, d))
    parsed.sort(key=lambda x: x[0])

    if not parsed:
        return {"status": "success", "message": "No documents found.", "unparsed": unparsed}

    if req.after_seq is not None:
        parsed = [p for p in parsed if p[0] > req.after_seq]
        if not parsed:
            return {"status": "success", "message": f"No documents found with sequence > {req.after_seq}.", "unparsed": unparsed}
        start_seq = req.after_seq + 1
    else:
        start_seq = parsed[0][0]
    changes = []
    for i, (old_seq, d) in enumerate(parsed):
        new_seq = start_seq + i
        if new_seq != old_seq:
            old_number = d["invoice_number"]
            match = find_sequence_match(old_number)
            new_number = old_number[:match.start()] + str(new_seq).zfill(len(match.group(0))) + old_number[match.end():]
            changes.append({"id": d["id"], "old_number": old_number, "new_number": new_number, "new_seq": new_seq})

    if not changes:
        return {"status": "success", "message": "No gaps found - already contiguous.", "unparsed": unparsed}

    old_numbers = [c["old_number"] for c in changes]
    collections = await db.list_collection_names()
    referenced = {}
    for coll_name in collections:
        if coll_name in ("offline_invoices", "audit_trail"):
            continue
        coll = db[coll_name]
        count = await coll.count_documents({
            "$or": [
                {"invoice_number": {"$in": old_numbers}},
                {"reference_number": {"$in": old_numbers}},
                {"related_invoice_number": {"$in": old_numbers}},
                {"so_number": {"$in": old_numbers}},
            ]
        })
        if count > 0:
            referenced[coll_name] = count

    if req.dry_run:
        return {
            "status": "success",
            "dry_run": True,
            "changes_count": len(changes),
            "changes": changes,
            "unparsed": unparsed,
            "stale_references_warning": referenced
        }

    for c in changes:
        await db.offline_invoices.update_one({"id": c["id"]}, {"$set": {"invoice_number": c["new_number"]}})

    max_new_seq = max(c["new_seq"] for c in changes)
    store = await db.stores.find_one({"code": req.store_code})
    counter_update = None
    if store:
        store_id = store.get("id")
        await db.document_numbering.update_one(
            {"store_id": store_id},
            {"$set": {f"document_configs.{req.document_type}.current_number": max_new_seq + 1}}
        )
        counter_update = max_new_seq + 1

    await db.audit_trail.insert_one({
        "id": str(uuid.uuid4()),
        "action": "renumber_after_delete",
        "store_code": req.store_code,
        "document_type": req.document_type,
        "changes": changes,
        "admin": getattr(admin, "email", str(admin)),
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    return {
        "status": "success",
        "dry_run": False,
        "changes_count": len(changes),
        "changes": changes,
        "new_counter": counter_update,
        "stale_references_warning": referenced
    }
