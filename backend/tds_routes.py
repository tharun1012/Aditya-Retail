"""
TDS (Tax Deducted at Source) Rates & Vendor TDS Profile Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from database import get_db
import logging

router = APIRouter(prefix="/tds", tags=["TDS"])
logger = logging.getLogger(__name__)


@router.get("/rates")
async def get_tds_rates(search: Optional[str] = None, db = Depends(get_db)):
    """List all TDS rate sections. Optional search filters by old_section only."""
    query = {}
    if search:
        query["old_section"] = {"$regex": search, "$options": "i"}
    rates = await db.tds_rates.find(query, {"_id": 0}).sort("code", 1).to_list(None)
    return {"status": "success", "count": len(rates), "rates": rates}


@router.get("/rates/{code}")
async def get_tds_rate_by_code(code: str, db = Depends(get_db)):
    rate = await db.tds_rates.find_one({"code": code}, {"_id": 0})
    if not rate:
        raise HTTPException(status_code=404, detail="TDS rate not found")
    return {"status": "success", "rate": rate}


@router.get("/vendor-profile")
async def get_vendor_tds_profile(name: str, db = Depends(get_db)):
    """Look up a saved vendor record (details + last used TDS) for autosuggest, by exact/partial name."""
    profile = await db.vendor_tds_profiles.find_one(
        {"vendor_name": {"$regex": f"^{name}$", "$options": "i"}}, {"_id": 0}
    )
    if not profile:
        # fallback: partial match, most recently updated
        profile = await db.vendor_tds_profiles.find_one(
            {"vendor_name": {"$regex": name, "$options": "i"}}, {"_id": 0}, sort=[("updated_at", -1)]
        )
    return {"status": "success", "profile": profile}


@router.get("/vendor-suggestions")
async def get_vendor_suggestions(q: str, db = Depends(get_db)):
    """Autosuggest list of saved vendors matching partial name typed so far."""
    if not q or len(q) < 2:
        return {"status": "success", "suggestions": []}
    cursor = db.vendor_tds_profiles.find(
        {"vendor_name": {"$regex": q, "$options": "i"}}, {"_id": 0}
    ).sort("updated_at", -1).limit(10)
    suggestions = await cursor.to_list(None)
    return {"status": "success", "suggestions": suggestions}


class VendorTDSUpsert(BaseModel):
    vendor_name: str
    phone: Optional[str] = ""
    email: Optional[str] = ""
    gst_number: Optional[str] = ""
    msme_udyam_number: Optional[str] = ""
    address: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    pincode: Optional[str] = ""
    tds: Optional[Dict[str, Any]] = None  # {section, code, rate_applied, deducted, amount_deducted}


@router.post("/vendor-profile")
async def upsert_vendor_tds_profile(payload: VendorTDSUpsert, db = Depends(get_db)):
    """Create/update a vendor's saved details + last TDS usage. Called after a bill is saved."""
    now = datetime.now(timezone.utc).isoformat()
    doc = payload.dict()
    doc["updated_at"] = now
    existing = await db.vendor_tds_profiles.find_one({"vendor_name": {"$regex": f"^{payload.vendor_name}$", "$options": "i"}})
    if existing:
        await db.vendor_tds_profiles.update_one({"id": existing["id"]}, {"$set": doc})
    else:
        doc["id"] = __import__("uuid").uuid4().hex
        doc["created_at"] = now
        await db.vendor_tds_profiles.insert_one(doc)
    return {"status": "success"}
