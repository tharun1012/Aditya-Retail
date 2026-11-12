import json, urllib.request
from collections import Counter
req = urllib.request.Request("https://adityaretail.com/api/products", headers={"User-Agent": "audit"})
d = json.load(urllib.request.urlopen(req, timeout=120))
items = d if isinstance(d, list) else d.get("products", [])
c = Counter()
ex = {}
for p in items:
    imgs = p.get("images") or ([p["image"]] if p.get("image") else [])
    first = imgs[0] if imgs else ""
    if not first: k = "(none)"
    elif first.startswith("data:"): k = "data-uri"
    elif first.startswith("http"): k = "http: " + first.split("/")[2]
    else: k = "relative: " + first.split("?")[0][:50]
    c[k] += 1
    ex.setdefault(k, p.get("name"))
for k, v in c.most_common(25): print(f"{v:5}  {k}   e.g. {ex[k]!r}")
