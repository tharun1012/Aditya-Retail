"""Dynamic sitemap.xml for Google indexing"""
import os
import re
from datetime import datetime, timezone
from xml.sax.saxutils import escape

from fastapi import APIRouter, Response
from database import db

router = APIRouter(tags=["sitemap"])

STORE_URL = os.environ.get("STORE_URL", "https://adityaretail.com").rstrip("/")

STATIC_PAGES = [
    ("", "daily", "1.0"),
    ("/about", "monthly", "0.5"),
    ("/contact", "monthly", "0.5"),
    ("/faq", "monthly", "0.5"),
    ("/blog", "weekly", "0.6"),
]


def _slugify(s):
    if not s:
        return None
    s = s.lower()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s or None


@router.get("/sitemap.xml")
async def sitemap():
    lastmods = {}
    async for d in db.seo_pages.find({"status": "live"}, {"_id": 0, "page_path": 1, "updated_at": 1}):
        lastmods[(d.get("page_path") or "").lower()] = (d.get("updated_at") or "")[:10]

    def _lm(path):
        v = lastmods.get(path or "/")
        return f"<lastmod>{v}</lastmod>" if v else ""

    entries = []

    def add(path, changefreq, priority):
        entries.append(
            f"<url><loc>{escape(STORE_URL + path)}</loc>"
            f"{_lm(path)}"
            f"<changefreq>{changefreq}</changefreq>"
            f"<priority>{priority}</priority></url>"
        )

    for path, freq, prio in STATIC_PAGES:
        add(path, freq, prio)

    products = await db.products.find(
        {"is_listed": {"$ne": False}},
        {"_id": 0, "slug": 1, "name": 1, "brand": 1, "category": 1}
    ).to_list(None)

    seen_categories = set()
    seen_urls = set()
    for p in products:
        cat = _slugify(p.get("category"))
        if cat and cat not in seen_categories:
            seen_categories.add(cat)
            add(f"/{cat}", "daily", "0.8")

    managed = await db.categories.find({"is_active": True}, {"_id": 0, "name": 1}).to_list(100)
    for c in managed:
        cat = _slugify(c.get("name"))
        if cat and cat not in seen_categories:
            seen_categories.add(cat)
            add(f"/{cat}", "daily", "0.8")

    counts = {}
    for p in products:
        c, b = _slugify(p.get("category")), _slugify(p.get("brand"))
        if c and b:
            counts[(c, b)] = counts.get((c, b), 0) + 1
    multi = {}
    for (c, b) in counts:
        multi[c] = multi.get(c, 0) + 1
    for (c, b), n in sorted(counts.items()):
        if n >= 3 and multi[c] > 1:
            add(f"/{c}/{b}", "weekly", "0.7")

    for p in products:
        cat = _slugify(p.get("category"))
        slug = p.get("slug") or _slugify(p.get("name"))
        if not cat or not slug:
            continue
        brand = _slugify(p.get("brand"))
        path = f"/{cat}/{brand}/{slug}" if brand else f"/{cat}/{slug}"
        if path in seen_urls:
            continue
        seen_urls.add(path)
        add(path, "weekly", "0.7")

    posts = await db.blog_posts.find(
        {"status": {"$nin": ["draft", "archived"]}, "slug": {"$exists": True, "$ne": None}},
        {"_id": 0, "slug": 1}
    ).to_list(None)
    for post in posts:
        add(f"/blog/{post['slug']}", "monthly", "0.5")

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>"
    )
    return Response(content=xml, media_type="application/xml")
