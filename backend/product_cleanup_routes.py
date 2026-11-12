from collections import Counter
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pymongo import UpdateOne
from admin_data_management_routes import verify_super_admin, get_db
from product_normalize import clean_brand, clean_category

router = APIRouter(prefix="/admin/product-cleanup", tags=["product-cleanup"])

async def _plan(db):
    changes = []
    async for p in db.products.find({}, {"_id": 0, "id": 1, "name": 1, "brand": 1, "category": 1}):
        upd = {}
        ob, oc = p.get("brand"), p.get("category")
        if isinstance(ob, str):
            nb = clean_brand(ob, p.get("name", ""))
            if nb != ob:
                upd["brand"] = nb
        if isinstance(oc, str):
            nc = clean_category(oc)
            if nc != oc:
                upd["category"] = nc
        if upd and p.get("id"):
            changes.append((p["id"], ob, oc, upd))
    return changes

def _summary(changes):
    b, c = Counter(), Counter()
    for _id, ob, oc, upd in changes:
        if "brand" in upd:
            b[f"{ob!r} -> {upd['brand']!r}"] += 1
        if "category" in upd:
            c[f"{oc!r} -> {upd['category']!r}"] += 1
    return {"products_to_change": len(changes), "brand_changes": dict(b.most_common()), "category_changes": dict(c.most_common())}

@router.get("/dry-run")
async def dry_run(db=Depends(get_db), admin=Depends(verify_super_admin)):
    return {"status": "dry_run", "written": False, **_summary(await _plan(db))}

@router.post("/apply")
async def apply(confirm: bool = False, db=Depends(get_db), admin=Depends(verify_super_admin)):
    if not confirm:
        raise HTTPException(400, "Add ?confirm=true to apply. Run /dry-run first.")
    changes = await _plan(db)
    backup = "products_backup_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    docs = await db.products.find({}).to_list(None)
    if docs:
        await db[backup].insert_many(docs)
    ops = [UpdateOne({"id": i}, {"$set": u}) for i, _b, _c, u in changes]
    for n in range(0, len(ops), 500):
        await db.products.bulk_write(ops[n:n + 500])
    return {"status": "applied", "backup_collection": backup, "backed_up": len(docs), **_summary(changes)}
