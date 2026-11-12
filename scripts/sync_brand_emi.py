import sys
from pymongo import MongoClient

APPLY = "--apply" in sys.argv
env = {}
for l in open("backend/.env"):
    if "=" in l and not l.strip().startswith("#"):
        k, v = l.strip().split("=", 1)
        env[k] = v.strip('"').strip("'")

skus = [s.strip().upper() for s in open("scripts/pine_skus.txt") if s.strip() and not s.startswith("#")]
skus = list(dict.fromkeys(skus))
if not skus:
    sys.exit("scripts/pine_skus.txt is empty. Paste the SKU_CODE column (one per line), then re-run.")

col = MongoClient(env["MONGO_URL"])[env["DB_NAME"]]["products"]

matched, missing = [], []
for s in skus:
    docs = list(col.find({"$or": [{"model_number": {"$regex": f"^{s}$", "$options": "i"}},
                                  {"modelNumber": {"$regex": f"^{s}$", "$options": "i"}}]},
                         {"_id": 0, "id": 1, "name": 1, "model_number": 1}))
    (matched if docs else missing).append((s, docs))

print(f"Pine Labs SKUs: {len(skus)} | found on website: {len(matched)} | MISSING from website: {len(missing)}\n")
print("--- MISSING (send this list to your boss) ---")
for s, _ in missing:
    print(s)

if APPLY:
    n = 0
    for s, docs in matched:
        for d in docs:
            col.update_one({"id": d["id"]}, {"$set": {"brand_emi_sku": s}})
            n += 1
    print(f"\nAPPLIED: brand_emi_sku set on {n} products")
else:
    print("\nDRY RUN only. Re-run with --apply to write brand_emi_sku.")
