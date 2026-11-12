import re, time, html as _html
from starlette.responses import Response
from database import db

CACHE = {}
TTL = 300
BASE = "https://adityaretail.com"

async def get_seo(path):
    hit = CACHE.get(path)
    if hit and time.time() - hit[0] < TTL:
        return hit[1]
    doc = await db.seo_pages.find_one({"page_path": path, "status": "live"}, {"_id": 0})
    CACHE[path] = (time.time(), doc)
    return doc

def build_tags(doc, path):
    e = lambda v: _html.escape(str(v or ""), quote=True)
    title = doc.get("title") or ""
    desc = doc.get("description") or ""
    canon = doc.get("canonical_url") or (BASE + path)
    img = doc.get("og_image") or ""
    tags = [
        "<title>" + e(title) + "</title>",
        '<meta name="description" content="' + e(desc) + '">',
        '<link rel="canonical" href="' + e(canon) + '">',
        '<meta property="og:title" content="' + e(title) + '">',
        '<meta property="og:description" content="' + e(desc) + '">',
        '<meta property="og:url" content="' + e(canon) + '">',
        '<meta property="og:type" content="website">',
    ]
    if img:
        tags.append('<meta property="og:image" content="' + e(img) + '">')
    return "\n".join(tags)

def install_seo(app):
    @app.middleware("http")
    async def seo_injector(request, call_next):
        response = await call_next(request)
        try:
            if request.method != "GET" or request.url.path.startswith("/api"):
                return response
            if "text/html" not in response.headers.get("content-type", ""):
                return response
            path = request.url.path.rstrip("/") or "/"
            doc = await get_seo(path)
            if not doc:
                return response
            body = b"".join([c async for c in response.body_iterator]).decode("utf-8")
            body = re.sub(r"<title>.*?</title>", "", body, flags=re.S | re.I)
            body = re.sub(r'<meta[^>]+name=["\']description["\'][^>]*>', "", body, flags=re.I)
            body = re.sub(r'<link[^>]+rel=["\']canonical["\'][^>]*>', "", body, flags=re.I)
            body = re.sub(r'<meta[^>]+property=["\']og:[a-z:_]+["\'][^>]*>', "", body, flags=re.I)
            body = body.replace("</head>", build_tags(doc, path) + "\n</head>", 1)
            headers = {k: v for k, v in response.headers.items() if k.lower() != "content-length"}
            headers["x-seo-source"] = "server"
            return Response(content=body, status_code=response.status_code, headers=headers)
        except Exception as ex:
            print("seo_injector error:", ex)
            return response
