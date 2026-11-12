import json
from pathlib import Path
from database import db

SEED_FILE = Path(__file__).parent / "seo_seed.json"
FLAG = "seo_pages_seed_v1"


async def seed_seo_pages():
    """Runs once per database: inserts seed SEO pages whose page_path is missing. Never overwrites."""
    if not SEED_FILE.exists():
        return
    if await db.seed_flags.find_one({"_id": FLAG}):
        return
    docs = json.loads(SEED_FILE.read_text())
    added = 0
    for d in docs:
        path = d.get("page_path")
        if not path:
            continue
        if await db.seo_pages.find_one({"page_path": path}, {"_id": 1}):
            continue
        await db.seo_pages.insert_one(d)
        added += 1
    await db.seed_flags.insert_one({"_id": FLAG, "added": added})
    print(f"SEO pages seeded: {added} added of {len(docs)}")
