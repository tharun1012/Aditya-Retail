# Maps the store-visit form keys to real store codes in db.stores
VISIT_KEY_TO_CODE = {"banaswadi": "BNS", "bosch": "ARM", "dasarahalli": "DAS"}

async def store_id_for_visit(db, key):
    code = VISIT_KEY_TO_CODE.get(key)
    if not code:
        return None
    s = await db.stores.find_one({"code": code, "is_active": True}, {"_id": 0, "id": 1})
    return s["id"] if s else None
