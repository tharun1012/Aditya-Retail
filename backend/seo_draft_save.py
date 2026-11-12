import asyncio, json, sys, uuid
from datetime import datetime, timezone
from database import db
from seo_settings_routes import SEOPage, norm_path

APPLY = "--apply" in sys.argv

async def main():
    drafts = json.load(open("/tmp/seo_drafts.json"))
    new = skipped = 0
    for d in drafts:
        d = {k: v for k, v in d.items() if k not in ("title_len", "desc_len")}
        data = SEOPage(**d).dict()
        data["status"], data["source"] = "draft", "ai"
        data["page_path"] = norm_path(data["page_path"])
        if await db.seo_pages.find_one({"page_path": data["page_path"]}):
            skipped += 1
            continue
        now = datetime.now(timezone.utc).isoformat()
        data.update(id=str(uuid.uuid4()), created_at=now, updated_at=now)
        if APPLY:
            await db.seo_pages.insert_one(data)
        new += 1
    print(("SAVED" if APPLY else "DRY RUN (nothing saved)"), f"| new: {new} | skipped existing: {skipped}")

asyncio.run(main())
