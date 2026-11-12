import os
from collections import Counter
env = {}
for line in open('.env'):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        env[k] = v.strip().strip('"').strip("'")
from pymongo import MongoClient
db = MongoClient(env['MONGO_URL'])[env['DB_NAME']]
print("collections:", db.list_collection_names())
brands, cats = Counter(), Counter()
for p in db.products.find({}, {"brand": 1, "category": 1}):
    brands[p.get("brand")] += 1
    cats[p.get("category")] += 1
print("=== BRANDS ===")
for k, v in sorted(brands.items(), key=lambda x: str(x[0]).lower()): print(f"{v:5}  {k!r}")
print("\n=== CATEGORIES ===")
for k, v in sorted(cats.items(), key=lambda x: str(x[0]).lower()): print(f"{v:5}  {k!r}")
