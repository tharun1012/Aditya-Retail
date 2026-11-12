KINDS = {
    "microwave": ["microwave"],
    "refrigerator": ["refrigerator", "fridge", "freezer"],
    "dishwasher": ["dishwasher"],
    "washing machine": ["washing machine"],
    "clothes dryer": ["dryer"],
    "chimney": ["chimney"],
    "hob": ["hob", "cooktop"],
    "oven": ["oven"],
    "coffee machine": ["coffee"],
}
ACC_CATS = ("accessories", "detergent")
ACC_KW = {
    "washing machine": ["washing machine", "fabric softener"],
    "dishwasher": ["dishwasher", "rinse aid"],
    "refrigerator": ["fridge", "refrigerator", "deodor"],
    "chimney": ["chimney", "degreaser", "filter"],
    "oven": ["oven", "degreaser"],
    "hob": ["hob", "degreaser"],
    "coffee machine": ["coffee"],
    "microwave": ["microwave"],
    "clothes dryer": ["dryer"],
}
COMPLEMENT = {
    "refrigerator": ["dishwasher", "oven", "microwave", "chimney", "hob"],
    "dishwasher": ["refrigerator", "oven", "microwave", "chimney", "hob"],
    "washing machine": ["clothes dryer", "dishwasher", "refrigerator"],
    "clothes dryer": ["washing machine", "dishwasher", "refrigerator"],
    "chimney": ["hob", "oven", "dishwasher", "refrigerator"],
    "hob": ["chimney", "oven", "dishwasher", "refrigerator"],
    "oven": ["microwave", "chimney", "hob", "dishwasher"],
    "microwave": ["oven", "dishwasher", "refrigerator", "chimney"],
    "coffee machine": ["microwave", "oven", "dishwasher", "refrigerator"],
}


def kind_of(*texts):
    for t in texts:
        t = (t or "").lower()
        if not t:
            continue
        for k, kws in KINDS.items():
            if any(w in t for w in kws):
                return k
    return None


def _num(v):
    try:
        return float(v)
    except Exception:
        return 0.0


def _in_stock(p):
    for k in ("stock", "current_stock", "stock_quantity"):
        if p.get(k) is not None:
            return _num(p[k]) > 0
    return True


def _card(p):
    imgs = p.get("images")
    img = imgs[0] if isinstance(imgs, list) and imgs and isinstance(imgs[0], str) else (p.get("image") or p.get("thumbnail"))
    return {"id": p.get("id"), "name": p.get("name"), "brand": p.get("brand"),
            "category": p.get("category"), "price": p.get("price"),
            "original_price": p.get("original_price"), "image": img, "slug": p.get("slug")}


async def build_recommendations(db, user_id, per_group=4):
    catalog = await db.products.find(
        {"is_active": {"$ne": False}, "is_listed": {"$ne": False}},
        {"_id": 0, "id": 1, "name": 1, "brand": 1, "category": 1, "price": 1, "original_price": 1,
         "image": 1, "images": 1, "thumbnail": 1, "slug": 1, "rating": 1,
         "stock": 1, "current_stock": 1, "stock_quantity": 1}).to_list(2000)
    catalog = [p for p in catalog if p.get("id") and _in_stock(p)]
    regs = await db.registered_products.find(
        {"user_id": user_id, "status": {"$ne": "removed"}}, {"_id": 0}).to_list(200)

    bought = {r.get("product_id") for r in regs}
    for cp in await db.consumable_purchases.find({"user_id": user_id}, {"_id": 0, "product_id": 1}).to_list(500):
        bought.add(cp.get("product_id"))

    owned = {kind_of(r.get("category"), r.get("product_name")) for r in regs}
    owned.discard(None)

    accessories = [p for p in catalog if (p.get("category") or "").lower() in ACC_CATS]
    by_kind = {}
    for p in catalog:
        cat = (p.get("category") or "").lower()
        if cat in ACC_CATS:
            continue
        k = kind_of(p.get("category"))
        if k:
            by_kind.setdefault(k, []).append(p)

    def rank(brand):
        b = (brand or "").lower()
        return lambda p: (0 if (p.get("brand") or "").lower() == b else 1, -_num(p.get("rating")))

    groups, shown = [], set()
    for rp in regs:
        k = kind_of(rp.get("category"), rp.get("product_name"))
        if not k:
            continue
        brand = rp.get("brand")
        acc = [p for p in accessories
               if p["id"] not in bought
               and any(w in (p.get("name") or "").lower() for w in ACC_KW.get(k, []))]
        acc.sort(key=rank(brand))
        acc = acc[:per_group]

        comp = []
        for ck in COMPLEMENT.get(k, []):
            if ck in owned:
                continue
            cands = [p for p in by_kind.get(ck, []) if p["id"] not in bought and p["id"] not in shown]
            cands.sort(key=rank(brand))
            if cands:
                comp.append(cands[0])
                shown.add(cands[0]["id"])
            if len(comp) >= per_group:
                break

        if acc or comp:
            groups.append({
                "for_product": rp.get("product_name"), "for_product_id": rp.get("id"),
                "accessories": [_card(p) for p in acc],
                "complete_your_kitchen": [_card(p) for p in comp],
            })
    return groups
