import json, re
import urllib.request

def slugify(s):
    return re.sub(r'\s+', '-', s.strip().lower())

with open('/app/debug/valid_categories.json') as f:
    valid_cats = set(json.load(f))

req = urllib.request.Request("https://adityaretail.com/api/products?limit=1000")
data = json.loads(urllib.request.urlopen(req).read())
products = data.get('products', [])

pairs = set()
for p in products:
    cat, brand = p.get('category'), p.get('brand')
    if cat in valid_cats and brand and brand not in ('TestBrand', 'Test'):
        pairs.add((cat, brand))

routes = sorted(f"{slugify(cat)}/{slugify(brand)}" for cat, brand in pairs)
with open('/app/debug/brand_routes.txt', 'w') as f:
    f.write('\n'.join(routes) + '\n')

print(f"Total real brand-category combinations: {len(routes)}")
