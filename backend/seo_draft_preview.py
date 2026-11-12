import asyncio, json, re, itertools
from collections import Counter
from database import db
from seo_settings_routes import norm_path

try:
    from brand_category_content_routes import slugify
except Exception:
    def slugify(t):
        return re.sub(r'[^a-z0-9]+', '-', (t or '').lower()).strip('-')

SITE = "Aditya Retail"
LO, HI = 150, 160
JUNK = re.compile(r'\b(test|dummy)|uncategori[sz]ed', re.I)

PRODUCT_FILLERS = ["Compare models, prices and specifications in one place.",
                   "Find the right fit for your home.",
                   "See features side by side.",
                   "Read the details before you buy.",
                   "Easy to browse and compare.",
                   "Pick the model that suits your needs.",
                   "Check key features and prices before you decide.",
                   "Shop now."]
STATIC_FILLERS = ["Read more.", "Learn more.", "See details.",
                  "Find out more here.", "All in one place.", "Quick and easy."]

def nice(x):
    return x if any(ch.isupper() for ch in x) else x.title()

def pick_title(options, limit=60):
    for o in options:
        if len(o) <= limit:
            return o
    return options[-1][:limit].rsplit(' ', 1)[0].rstrip(' |-')

def fit(parts, fillers):
    base = ""
    for p in parts:
        cand = (base + " " + p).strip()
        if len(cand) <= HI:
            base = cand
    if LO <= len(base) <= HI:
        return base
    for r in range(1, len(fillers) + 1):
        for combo in itertools.combinations(fillers, r):
            cand = " ".join([base, *combo]).strip()
            if LO <= len(cand) <= HI:
                return cand
    return base

STATIC = [
    ("/about", "About Us",
     "Learn about Aditya Retail, who we are and what we stand for. Find out how we help customers choose the right products and get support after purchase."),
    ("/contact", "Contact Us",
     "Get in touch with Aditya Retail for product questions, orders and after-sales support. Find our contact details and reach the team that can help you."),
    ("/faq", "FAQs",
     "Find answers to common questions about ordering, payments, delivery, returns and support at Aditya Retail. Quick help before you contact our team."),
    ("/track-order", "Track Your Order",
     "Track your Aditya Retail order online. Enter your order details to see the latest status of your purchase and expected delivery updates in one place."),
    ("/privacy-policy", "Privacy Policy",
     "Read the Aditya Retail privacy policy to understand what personal information we collect, how we use it and the choices you have over your data."),
    ("/terms-and-conditions", "Terms and Conditions",
     "Read the terms and conditions for using the Aditya Retail website and placing orders, including your rights, our responsibilities and key policies."),
    ("/return-policy", "Return Policy",
     "Review the Aditya Retail return policy to learn how returns, replacements and refunds work, and what to do if you need help with a purchase."),
    ("/shipping-policy", "Shipping Policy",
     "Review the Aditya Retail shipping policy covering how orders are processed and delivered, and who to contact if you need help with a shipment."),
    ("/blog", "Buying Guides and Tips",
     "Read buying guides, product comparisons and practical tips from Aditya Retail to help you choose the right products for your home with confidence."),
]

async def main():
    existing = set()
    async for d in db.seo_pages.find({}, {"_id": 0, "page_path": 1}):
        if d.get("page_path"):
            existing.add(norm_path(d["page_path"]))

    rows = await db.products.aggregate([
        {"$match": {"category": {"$nin": [None, ""]},
                    "is_active": {"$ne": False}, "is_listed": {"$ne": False}}},
        {"$group": {"_id": {"c": "$category", "b": "$brand"}, "n": {"$sum": 1}}}
    ]).to_list(None)

    cats, brandpages, excluded = {}, {}, set()
    for r in rows:
        c, b, n = r["_id"].get("c"), r["_id"].get("b"), r["n"]
        if not isinstance(c, str) or not c.strip():
            continue
        c = c.strip()
        if JUNK.search(c):
            excluded.add(c); continue
        if isinstance(b, str) and JUNK.search(b):
            excluded.add(b); continue
        cs = slugify(c)
        if not cs:
            continue
        e = cats.setdefault(cs, {"names": Counter(), "n": 0, "brands": Counter()})
        e["names"][c] += n
        e["n"] += n
        if isinstance(b, str) and b.strip():
            b = b.strip()
            e["brands"][b] += n
            bs = slugify(b)
            if bs:
                bp = brandpages.setdefault((cs, bs), {"names": Counter(), "n": 0})
                bp["names"][b] += n
                bp["n"] += n

    drafts, seen, skipped = [], set(), 0

    def add(path, ptype, title, desc):
        nonlocal skipped
        p = norm_path(path)
        if p in existing:
            skipped += 1; return
        if p in seen:
            return
        seen.add(p)
        drafts.append({"page_path": p, "page_type": ptype, "title": title,
                       "description": desc, "status": "draft", "source": "ai"})

    top = [nice(v["names"].most_common(1)[0][0]) for _, v in
           sorted(cats.items(), key=lambda kv: -kv[1]["n"])[:4]]
    if top:
        add("/", "page", f"{SITE} | Premium Home Products Online",
            fit([f"Shop {', '.join(top)} and more online at {SITE}.",
                 "Compare brands, prices and specifications in one place."], PRODUCT_FILLERS))

    for path, title, desc in STATIC:
        add(path, "page", f"{title} | {SITE}", fit([desc], STATIC_FILLERS))

    for cs, e in cats.items():
        cat = nice(e["names"].most_common(1)[0][0])
        brands = [nice(b) for b, _ in e["brands"].most_common(4)]
        title = pick_title([f"{cat} Online | Buy {cat} | {SITE}",
                            f"{cat} Online | {SITE}", f"{cat} | {SITE}"])
        parts = [f"Shop {cat} online at {SITE}.",
                 f"Browse {e['n']} product{'s' if e['n'] != 1 else ''}" +
                 (f" from {', '.join(brands)}." if brands else ".")]
        add(f"/{cs}", "category", title, fit(parts, PRODUCT_FILLERS))

    for (cs, bs), bp in brandpages.items():
        cat = nice(cats[cs]["names"].most_common(1)[0][0])
        brand = nice(bp["names"].most_common(1)[0][0])
        title = pick_title([f"{brand} {cat} Online | Buy {brand} {cat} | {SITE}",
                            f"{brand} {cat} Online | {SITE}", f"{brand} {cat} | {SITE}"])
        parts = [f"Shop {brand} {cat} online at {SITE}.",
                 f"Browse {bp['n']} {brand} model{'s' if bp['n'] != 1 else ''}."]
        add(f"/{cs}/{bs}", "category", title, fit(parts, PRODUCT_FILLERS))

    for d in drafts:
        d["title_len"], d["desc_len"] = len(d["title"]), len(d["description"])
    json.dump(drafts, open("/tmp/seo_drafts.json", "w"), indent=2)

    bad = [d for d in drafts if not LO <= d["desc_len"] <= HI or d["title_len"] > 60]
    print(f"Drafts: {len(drafts)} | skipped (already exist): {skipped}")
    print(f"Excluded test names: {sorted(excluded)}")
    print(f"Outside limits: {len(bad)}")
    for d in bad[:15]:
        print(f"  {d['page_path']}  T={d['title_len']} D={d['desc_len']}")
    print("\nSamples:")
    cat_s = [x for x in drafts if x["page_path"].count("/") == 1 and x["page_type"] == "category"][:2]
    br_s = [x for x in drafts if x["page_path"].count("/") == 2][:2]
    for d in drafts[:2] + cat_s + br_s:
        print(f"\n{d['page_path']}\n  T ({d['title_len']}): {d['title']}\n  D ({d['desc_len']}): {d['description']}")
    print("\nAll paths:")
    for d in drafts:
        print(" ", d["page_path"])

asyncio.run(main())
