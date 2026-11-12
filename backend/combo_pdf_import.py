import base64, hashlib, json, os, re, uuid
from datetime import datetime, timezone
from typing import List, Optional
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
import anthropic
from database import get_db
# TODO: add your admin auth dependency to both routes (see grep in step 4)

router = APIRouter(prefix="/combo-offers/pdf-import", tags=["Combo PDF Import"])
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
IST = ZoneInfo("Asia/Kolkata")

PROMPT = """Extract every fixed bundle/combo offer from this brand leaflet.
Return ONLY JSON (no markdown) in this shape:
{"valid_from":"YYYY-MM-DD or null","valid_till":"YYYY-MM-DD or null","rules":["text of any 'pair any X with any Y' style offers"],
 "combos":[{"name":"...","section":"section title","items":[{"model":"exact model code","type":"Hob|Hood|Oven|Microwave|Dishwasher|Other","mrp":number,"festive_price":number}],
            "total_mrp":number,"combo_price":number,"extras":"warranty/gift text or null"}]}
Rules:
- One entry per lettered combo (A/B/C/D, Serie 6 / Serie 8 combos too).
- Prefix names so they are unique, e.g. "Hob+Hood Combo 1A - 90 cm Power Duo Inclined Hood" or "Oven+Microwave Combo 2B - Cooking Duo (Serie 4)" or "Kitchen Master Trio A".
- Plain numbers only (no commas, no rupee sign). Copy model codes exactly as printed.
- Skip single-product offer sections (hobs, hoods, ovens listed alone) and the combi steam oven.
- Pairing rules like 'Complete Kitchen Combo' go in "rules", not "combos"."""

def norm(s):
    return re.sub(r"[^A-Z0-9]", "", (s or "").upper()).replace("O", "0")

def keys(model):
    n = norm(model)
    return {n, n[:-1]} if n.endswith("I") and len(n) > 6 else {n}

def to_utc(d, end=False):
    dt = datetime.strptime(d, "%Y-%m-%d")
    if end: dt = dt.replace(hour=23, minute=59, second=59)
    return dt.replace(tzinfo=IST).astimezone(timezone.utc).isoformat()

EMERGENT_MODEL = os.getenv("EMERGENT_COMBO_MODEL", "claude-sonnet-4-5-20250929")

async def run_extraction(pdf_bytes):
    key = os.getenv("EMERGENT_LLM_KEY")
    if not key:
        raise HTTPException(500, "EMERGENT_LLM_KEY missing in backend/.env")
    try:
        import fitz
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
    except ImportError as e:
        raise HTTPException(500, f"Missing package: {e}")
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    if doc.page_count > 20:
        raise HTTPException(400, "PDF has more than 20 pages, split it first")
    imgs = []
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6))
        imgs.append(ImageContent(image_base64=base64.b64encode(pix.tobytes("jpeg")).decode()))
    try:
        chat = LlmChat(api_key=key, session_id=str(uuid.uuid4()),
                       system_message="You extract structured data from retail leaflets. Reply with JSON only."
                       ).with_model("gemini", EMERGENT_MODEL)
        return await chat.send_message(UserMessage(text=PROMPT, file_contents=imgs))
    except Exception as e:
        raise HTTPException(502, f"AI call failed: {str(e)[:300]}")


async def _set_job(db, job_id, doc):
    await db.pdf_import_jobs.update_one(
        {"job_id": job_id},
        {"$set": {**doc, "job_id": job_id, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True)

async def _run_job(job_id, data, db, filename):
    try:
        result = await _build_preview(data, db, filename)
        await _set_job(db, job_id, {"status": "done", "result": result})
    except HTTPException as e:
        await _set_job(db, job_id, {"status": "error", "detail": str(e.detail)})
    except Exception as e:
        await _set_job(db, job_id, {"status": "error", "detail": f"Unexpected error: {str(e)[:300]}"})

@router.post("/preview")
async def preview(file: UploadFile = File(...), db=Depends(get_db)):
    import asyncio
    data = await file.read()
    if not data.startswith(b"%PDF"):
        raise HTTPException(400, "Please upload a PDF")
    job_id = str(uuid.uuid4())
    await _set_job(db, job_id, {"status": "running"})
    asyncio.create_task(_run_job(job_id, data, db, file.filename))
    return {"job_id": job_id, "status": "running"}

@router.get("/preview/{job_id}")
async def preview_status(job_id: str, db=Depends(get_db)):
    job = await db.pdf_import_jobs.find_one({"job_id": job_id}, {"_id": 0})
    if not job:
        raise HTTPException(404, "Job not found. Please upload again.")
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(job["updated_at"])).total_seconds()
    if job["status"] == "running" and age > 420:
        return {"status": "error", "detail": "Import was interrupted. Please upload again."}
    return {k: v for k, v in job.items() if k not in ("job_id", "updated_at")}

async def _build_preview(data, db, filename):
    text = await run_extraction(data)
    try:
        parsed = json.loads(text[text.find("{"): text.rfind("}") + 1])
    except Exception:
        raise HTTPException(422, "Could not parse AI output, please retry")

    proj = {"_id": 0, "id": 1, "name": 1, "model_number": 1, "modelNumber": 1,
            "price": 1, "stock_quantity": 1, "current_stock": 1}
    idx = {}
    for p in await db.products.find({}, proj).to_list(10000):
        for f in ("model_number", "modelNumber"):
            for k in keys(p.get(f)):
                if k: idx.setdefault(k, p)

    combos = []
    for c in parsed.get("combos", []):
        items, ok = [], True
        for it in c.get("items", []):
            p = next((idx[k] for k in keys(it.get("model")) if k in idx), None)
            ok = ok and bool(p)
            items.append({**it, "matched": bool(p),
                          "product_id": p["id"] if p else None,
                          "inventory_name": p.get("name") if p else None,
                          "inventory_price": p.get("price") if p else None,
                          "stock": (p.get("current_stock", p.get("stock_quantity")) if p else None)})
        s = sum(i.get("festive_price") or 0 for i in items)
        combos.append({**c, "items": items, "fully_matched": ok,
                       "price_check_ok": abs(s - (c.get("combo_price") or 0)) <= 1})
    def fix_year(d):
        return "2026" + d[4:] if isinstance(d, str) and len(d) == 10 and d[:4] < "2026" else d
    return {"valid_from": fix_year(parsed.get("valid_from")), "valid_till": fix_year(parsed.get("valid_till")),
            "rules": parsed.get("rules", []), "source_file": filename, "combos": combos}

class ConfirmIn(BaseModel):
    combos: List[dict]
    valid_from: Optional[str] = None      # YYYY-MM-DD
    valid_until: Optional[str] = None     # YYYY-MM-DD
    show_on_banner: bool = False
    source_file: Optional[str] = None

@router.post("/confirm")
async def confirm(body: ConfirmIn, db=Depends(get_db)):
    if not body.valid_until:
        raise HTTPException(400, "valid_until is required")
    if body.valid_until < datetime.now(IST).strftime("%Y-%m-%d"):
        raise HTTPException(400, "valid_until is in the past, please correct the date")
    now = datetime.now(timezone.utc).isoformat()
    vfrom = to_utc(body.valid_from) if body.valid_from else now
    vuntil = to_utc(body.valid_until, end=True)
    created = updated = skipped = 0
    for c in body.combos:
        ids = [i.get("product_id") for i in c.get("items", [])]
        if not c.get("fully_matched") or not all(ids):
            skipped += 1; continue
        prods = []
        for pid in ids:
            p = await db.products.find_one({"id": pid}, {"_id": 0, "stock_history": 0})
            if p: prods.append(p)
        if len(prods) != len(ids):
            skipped += 1; continue
        original = c.get("total_mrp") or sum(i.get("mrp") or 0 for i in c["items"])
        final = c["combo_price"]
        if not final or final <= 0:
            skipped += 1; continue
        savings = original - final
        key = hashlib.md5("|".join(sorted(ids)).encode() + c["name"].encode()).hexdigest()
        doc = {
            "name": c["name"],
            "description": c.get("extras") or c.get("section") or "",
            "product_ids": ids, "products": prods,
            "discount_type": "fixed", "discount_value": savings,
            "original_price": original, "final_price": final, "savings": savings,
            "valid_from": vfrom, "valid_until": vuntil, "is_active": True, "min_quantity": 1,
            "banner_image": (prods[0].get("images") or [None])[0],
            "banner_title": f"Save ₹{savings:,.0f}!", "banner_subtitle": c["name"],
            "banner_cta_text": "Shop Bundle", "banner_gradient": "from-purple-600 to-pink-600",
            "banner_priority": 5, "source": "pdf_import", "source_key": key,
            "source_file": body.source_file, "updated_at": now,
        }
        r = await db.combo_offers.update_one(
            {"source_key": key}, {"$set": doc, "$setOnInsert": {
                "id": str(uuid.uuid4()), "show_on_banner": body.show_on_banner,
                "orders_count": 0, "revenue_generated": 0, "created_at": now}}, upsert=True)
        if r.upserted_id: created += 1
        else: updated += 1
    return {"status": "success", "created": created, "updated": updated, "skipped": skipped}
