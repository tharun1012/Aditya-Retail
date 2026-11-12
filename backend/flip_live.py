import asyncio, os, re
from datetime import datetime, timezone
from database import db
HOLD = {"/kitchen-appliances", "/kitchen-appliances/siemens", "/home-appliances",
        "/home-appliances/bosch", "/home-appliances/siemens", "/accessories", "/accessories/bosch"}
async def m():
    dry = os.environ.get("DRY", "1") == "1"
    n = 0
    async for d in db.seo_pages.find({"status": "draft"}, {"_id": 0, "page_path": 1, "description": 1}):
        mt = re.search(r"Browse (\d+)", d.get("description", ""))
        if not mt or int(mt.group(1)) < 3 or d["page_path"] in HOLD:
            continue
        n += 1
        print(("would flip " if dry else "flipping ") + d["page_path"], mt.group(1))
        if not dry:
            await db.seo_pages.update_one({"page_path": d["page_path"]}, {"$set": {"status": "live", "updated_at": datetime.now(timezone.utc).isoformat()}})
    print("total:", n)
asyncio.run(m())
