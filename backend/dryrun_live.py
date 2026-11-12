import json, csv, re, urllib.request
from collections import Counter
BASE = "https://adityaretail.com"

def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "audit"})
    return json.load(urllib.request.urlopen(req, timeout=120))

key = lambda s: re.sub(r"\s+", " ", str(s or "")).strip().lower()

BRAND_MAP = {k: v for v, ks in {
    "Bosch": ["bosch", "bosch limited - powertools"],
    "Electrolux": ["electrolux", "electrolux india private limited"],
    "Haier": ["haier", "haier appliances india pvt limited"],
    "Siemens": ["siemens"],
    "Borosil": ["borosil"], "Dyson": ["dyson"], "Finish": ["finish"], "IFB": ["ifb"],
    "Instant Pot": ["instant pot"], "Kuvings": ["kuvings"],
}.items() for k in ks}

CANON = ["Washing Machine", "Refrigerator", "Gas Hob", "Induction Hob", "Dishwasher", "Chimney", "Oven",
         "Mixer Grinder", "Air Fryer", "Coffee Machine", "Detergents", "Power Tools", "TV", "Clothes Dryer",
         "Warmer Drawer", "AC - Air Conditioners", "Accessories", "Microwave", "Geysers", "Vacuum Cleaners"]
CANON_L = {key(c): c for c in CANON}
CAT_ALIAS = {
    "ref": "Refrigerator", "refrigerators": "Refrigerator",
    "w/m": "Washing Machine", "washing_machine": "Washing Machine", "washing machines": "Washing Machine",
    "ac": "AC - Air Conditioners", "air conditioner": "AC - Air Conditioners",
    "microwaves": "Microwave", "microwave oven": "Microwave",
    "detergent": "Detergents", "powertools": "Power Tools",
    "dryer": "Clothes Dryer",
}
KEEP = {"uncategorized", "other", "home appliances", "kitchen appliances", "appliances",
        "water dispenser", "water heater", "powertool accessories", ""}

def new_brand(p):
    b = p.get("brand") or ""
    k = key(b)
    if k in BRAND_MAP: return BRAND_MAP[k]
    if k.startswith("bsh household"):
        n = (p.get("name") or "").lower()
        if "siemens" in n: return "Siemens"
        if "bosch" in n: return "Bosch"
    return None  # review

def new_cat(p):
    c = p.get("category") or ""
    k = key(c)
    if k in CANON_L: return CANON_L[k]
    if k in CAT_ALIAS: return CAT_ALIAS[k]
    if k in KEEP: return c.strip()
    return None  # review

items = get("/api/products")
items = items if isinstance(items, list) else items.get("products", [])
rows, bc, cc = [], Counter(), Counter()
for p in items:
    ob, oc = p.get("brand") or "", p.get("category") or ""
    nb, nc = new_brand(p), new_cat(p)
    bs = "same" if nb == ob else ("review" if nb is None else "auto")
    cs = "same" if nc == oc else ("review" if nc is None else "auto")
    if ob == "": bs = "review"
    bc[bs] += 1; cc[cs] += 1
    if bs != "same" or cs != "same":
        rows.append([p.get("id"), p.get("name"), p.get("model_number") or p.get("sku"), ob, nb or "", bs, oc, nc or "", cs])
with open("review_live.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "name", "model", "brand_now", "brand_new", "brand_status", "cat_now", "cat_new", "cat_status"])
    w.writerows(rows)
print("products:", len(items))
print("brand  ->", dict(bc))
print("category ->", dict(cc))
print("\nBrands needing review:")
for k, v in Counter(r[3] for r in rows if r[5] == "review").most_common(): print(f"{v:5}  {k!r}")
print("\nCategory values needing review:", len({r[6] for r in rows if r[8] == "review"}), "distinct")
try:
    print("\n/api/categories/all sample:\n", json.dumps(get("/api/categories/all"))[:1500])
except Exception as e:
    print("categories endpoint:", e)
