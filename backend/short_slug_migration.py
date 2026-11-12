"""AI-powered short slug + short title generation for products"""
import os
import re
import json
import uuid
import asyncio
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from database import db
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/product-slugs", tags=["product-slugs"])

STATUS_KEY = "short_slug_migration"
BATCH_SIZE = 20

PROMPT_HEADER = """You generate SEO-friendly short URL slugs and short display titles for home appliance products.

For EACH product below return: id, short_slug, short_title.

RULES for short_slug:
- lowercase, hyphen-separated, NO brand name in it
- format: {model-number}-{key-spec}-{product-type}
- key spec = capacity/size only (e.g. 10kg, 335l, 60cm, 15l, 8-place). OMIT rpm, series, colour, star rating, dimensions.
- product type derived from category, singular, hyphenated (e.g. washing-machine, refrigerator, chimney, dishwasher, hob, oven, geyser, microwave)
- Example: name "Bosch WGA254ZPIN Series 6 washing machine, front loader 10 kg 1400 rpm", brand "Bosch", category "Washing Machine"
  -> short_slug: "wga254zpin-10kg-front-load-washing-machine"
- Example: name "Bosch CMC36K03GI Series 4 free-standing fridge-freezer with freezer at top 187 x 67 cm 335L 3 Star Smoky Silver 3 door", brand "Bosch", category "Refrigerator"
  -> short_slug: "cmc36k03gi-335l-3-door-refrigerator"

RULES for short_title:
- "{Brand} {MODEL} {Key Spec} {Product Type}" in Title Case, model number in UPPERCASE
- Example: "Bosch WGA254ZPIN 10 Kg Front Load Washing Machine"
- Example: "Bosch CMC36K03GI 335L 3 Door Refrigerator"

Return ONLY a valid JSON array, no markdown, no explanation:
[{"id": "...", "short_slug": "...", "short_title": "..."}]

PRODUCTS:
"""


def _sanitize_slug(s):
    if not s:
        return None
    s = s.lower()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s or None


def _strip_brand(slug, brand):
    b = _sanitize_slug(brand or '')
    if not slug or not b:
        return slug
    cleaned = re.sub(rf'^{re.escape(b)}-', '', slug)
    return cleaned if len(cleaned) >= 8 else slug


def _parse_json_array(text):
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    start, end = text.find('['), text.rfind(']')
    if start == -1 or end == -1:
        raise ValueError("No JSON array in AI response")
    return json.loads(text[start:end + 1])


async def _ai_batch(products):
    lines = []
    for p in products:
        lines.append(f"- id={p['id']} | brand={p.get('brand') or 'Unknown'} | category={p.get('category') or 'Appliance'} | name={p.get('name')}")
    chat = LlmChat(
        api_key=os.environ.get('EMERGENT_LLM_KEY'),
        session_id=f"slug-migration-{uuid.uuid4().hex[:8]}",
        system_message="You are a precise SEO slug generator. Respond with valid JSON only."
    ).with_model("gemini", "gemini-2.5-flash")
    response = await chat.send_message(UserMessage(text=PROMPT_HEADER + "\n".join(lines)))
    return _parse_json_array(response)


async def _set_status(**fields):
    fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.migration_status.update_one({"key": STATUS_KEY}, {"$set": fields}, upsert=True)


async def run_short_slug_migration(force=False):
    try:
        await db.products.create_index("slug")
        await db.products.create_index("legacy_slug")
        query = {} if force else {"$or": [{"short_title": {"$exists": False}}, {"short_title": None}, {"short_title": ""}]}
        products = await db.products.find(
            query, {"_id": 0, "id": 1, "name": 1, "brand": 1, "category": 1, "slug": 1, "legacy_slug": 1}
        ).to_list(None)

        all_docs = await db.products.find({}, {"_id": 0, "id": 1, "slug": 1}).to_list(None)
        used_slugs = {d.get("slug"): d["id"] for d in all_docs if d.get("slug")}
        pending_ids = {p["id"] for p in products}

        await _set_status(state="running", total=len(products), processed=0, updated=0, errors=0,
                          started_at=datetime.now(timezone.utc).isoformat(), finished_at=None, error_detail=None)

        processed = updated = errors = 0
        by_id = {p["id"]: p for p in products}

        for i in range(0, len(products), BATCH_SIZE):
            batch = products[i:i + BATCH_SIZE]
            try:
                results = await _ai_batch(batch)
            except Exception as e:
                logger.error(f"Slug AI batch failed: {e}")
                errors += len(batch)
                processed += len(batch)
                await _set_status(processed=processed, updated=updated, errors=errors)
                continue

            for r in results:
                pid = r.get("id")
                p = by_id.get(pid)
                if not p:
                    continue
                slug = _strip_brand(_sanitize_slug(r.get("short_slug")), p.get("brand"))
                title = (r.get("short_title") or "").strip()
                if not slug or len(slug) < 8 or not title:
                    errors += 1
                    continue
                # ensure uniqueness (ignore slugs held by products still pending re-generation)
                base, n = slug, 2
                while slug in used_slugs and used_slugs[slug] != pid and used_slugs[slug] not in pending_ids:
                    slug = f"{base}-{n}"
                    n += 1
                update = {"slug": slug, "short_title": title}
                if p.get("slug") and p["slug"] != slug and not p.get("legacy_slug"):
                    update["legacy_slug"] = p["slug"]
                await db.products.update_one({"id": pid}, {"$set": update})
                used_slugs[slug] = pid
                pending_ids.discard(pid)
                updated += 1
            processed += len(batch)
            await _set_status(processed=processed, updated=updated, errors=errors)

        await _set_status(state="completed", processed=processed, updated=updated, errors=errors,
                          finished_at=datetime.now(timezone.utc).isoformat())
        logger.info(f"Short slug migration done: {updated} updated, {errors} errors of {len(products)}")
    except Exception as e:
        logger.error(f"Short slug migration crashed: {e}")
        await _set_status(state="failed", error_detail=str(e), finished_at=datetime.now(timezone.utc).isoformat())


@router.post("/generate")
async def generate_short_slugs(force: bool = False):
    """Start AI short-slug migration in background. force=true regenerates all."""
    status = await db.migration_status.find_one({"key": STATUS_KEY}, {"_id": 0})
    if status and status.get("state") == "running":
        return {"status": "already_running", "progress": status}
    asyncio.create_task(run_short_slug_migration(force=force))
    return {"status": "started", "message": "Check progress at GET /api/product-slugs/status"}


@router.get("/status")
async def short_slug_status():
    status = await db.migration_status.find_one({"key": STATUS_KEY}, {"_id": 0})
    if not status:
        return {"status": "never_run"}
    return status
