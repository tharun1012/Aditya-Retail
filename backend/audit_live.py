import json, urllib.request
from collections import Counter
BASE = "https://adityaretail.com"
req = urllib.request.Request(BASE + "/api/products", headers={"User-Agent": "audit"})
d = json.load(urllib.request.urlopen(req, timeout=120))
items = d if isinstance(d, list) else d.get("products", [])
print("products fetched:", len(items))
brands, cats = Counter(), Counter()
for p in items:
    brands[p.get("brand")] += 1
    cats[p.get("category")] += 1
print("=== BRANDS ===")
for k, v in sorted(brands.items(), key=lambda x: str(x[0]).lower()): print(f"{v:5}  {k!r}")
print("\n=== CATEGORIES ===")
for k, v in sorted(cats.items(), key=lambda x: str(x[0]).lower()): print(f"{v:5}  {k!r}")
