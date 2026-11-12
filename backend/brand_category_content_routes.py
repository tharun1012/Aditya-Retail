"""
Brand + Category Content Generation Routes
--------------------------------------------
Automatically generates SEO landing-page content (H1, Why Buy, Types, How to Choose, FAQs)
for any category+brand combination, in the exact structure Aditya Retail's manually-written
Haier and Bosch washing machine pages use.

Content is grounded in REAL product data pulled from MongoDB (actual product names, prices,
brands) so the AI does not invent facts. Internal links are requested in markdown syntax
`[anchor text](/path)` and the frontend renders these as real clickable links.
"""
import os
import re
import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException
from database import get_db
from emergentintegrations.llm.chat import LlmChat, UserMessage

router = APIRouter(prefix="/brand-category-content", tags=["Brand Category Content"])

EMERGENT_API_KEY = os.environ.get("EMERGENT_API_KEY")

# Known internal pages the AI is allowed to link to. Extend this list as new pages are added.
KNOWN_INTERNAL_PAGES = {
    "detergent": "/detergent",
    "blog": "/blog",
    "contact": "/contact",
    "ai_chat": "?chat=open",
}


def slugify(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9\s-]", "", text.lower()).strip().replace(" ", "-"))


SCHEMA_EXAMPLE = """{
  "h1": "Brand CategoryName - Buy Online at Best Price",
  "metaTitle": "Buy Brand CategoryName Online | Aditya Retail",
  "metaDescription": "One or two sentence meta description, under 160 characters.",
  "intro": "2-4 sentence intro paragraph. Include one internal link in markdown syntax, e.g. Browse our full [CategoryName range](/category-slug) to compare across brands.",
  "whyBuyHeading": "Why Buy Brand CategoryName from Aditya Retail",
  "whyBuy": [
    { "label": "Short Label", "text": "supporting sentence fragment" }
  ],
  "typesHeading": "Types of Brand CategoryName",
  "typesIntro": "1 sentence intro to the types list.",
  "types": [
    { "h3": "Brand Type Name", "text": "2-3 sentence description grounded in the real product data provided." }
  ],
  "howToChooseHeading": "How to Choose the Right Brand CategoryName",
  "howToChoose": [
    { "label": "Short Label", "text": "supporting sentence fragment" }
  ],
  "closingText": "Still unsure which model fits your needs? Chat with our [AI Sales Agent](?chat=open) for a personalised recommendation based on your family size, budget, and usage pattern.",
  "faqHeading": "Brand CategoryName FAQs",
  "faqs": [
    { "question": "A real, useful question", "answer": "A factual answer grounded only in the provided product data or general dealer-service facts (warranty, installation, delivery)." }
  ]
}"""


async def fetch_grounding_products(db, category: str, brand: str, limit: int = 20):
    """Pull real product data to ground the generated content in facts, not invented specs."""
    cursor = db.products.find(
        {"category": {"$regex": f"^{re.escape(category)}$", "$options": "i"},
         "brand": {"$regex": f"^{re.escape(brand)}$", "$options": "i"}},
        {"_id": 0, "name": 1, "price": 1, "brand": 1, "category": 1, "description": 1, "specifications": 1}
    ).limit(limit)
    return [p async for p in cursor]


async def generate_content(category: str, brand: str, products: list) -> dict:
    if not EMERGENT_API_KEY:
        raise RuntimeError("EMERGENT_API_KEY not configured")

    product_facts = "\n".join(
        f"- {p.get('name')} — ₹{p.get('price', 'N/A')}" for p in products
    ) or "No specific product data available yet — keep all claims generic and avoid inventing series names, exact prices, or capacities."

    category_slug = slugify(category)
    brand_slug = slugify(brand)

    system_message = f"""You are a copywriter for Aditya Retail, an Indian authorised dealer of home appliances.
Generate landing-page content for the {brand} {category} page, in strict JSON matching this exact schema (same keys, same nesting):

{SCHEMA_EXAMPLE}

STRICT RULES:
1. Output ONLY valid JSON. No markdown fences, no commentary before or after.
2. Ground every factual claim (prices, capacities, series/model names) ONLY in this real product data — do not invent anything not implied by it:
{product_facts}
3. Where relevant, include internal links using markdown syntax [anchor text](/path). Only use these real internal paths:
   - Category page: /{category_slug}
   - This brand's category page: /{category_slug}/{brand_slug}
   - Detergent product page (only if category relates to washing/cleaning): /detergent
   - AI Sales Agent chat: ?chat=open
   Do not invent other internal paths.
4. Tone: confident, factual, concise — matching a premium appliance retailer, not hyperbolic.
5. Keep the FAQ answers short (1-3 sentences) and genuinely useful.
"""

    chat = LlmChat(
        api_key=EMERGENT_API_KEY,
        session_id=f"brand-content-{category_slug}-{brand_slug}",
        system_message=system_message
    ).with_model("openai", "gpt-4o")

    user_message = UserMessage(text=f"Generate the JSON content for {brand} {category} now.")
    response = await chat.send_message(user_message)

    raw = response.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(json)?", "", raw)
        raw = re.sub(r"```$", "", raw).strip()

    return json.loads(raw)


@router.get("/{category}/{brand}")
async def get_or_generate_content(category: str, brand: str):
    db = await get_db()
    category_norm = category.replace("-", " ")
    key = f"{slugify(category_norm)}|{brand}"

    existing = await db.brand_category_content.find_one({"_key": key}, {"_id": 0})
    if existing:
        return {"status": "success", "content": existing["content"], "source": existing.get("source", "ai_generated")}

    try:
        products = await fetch_grounding_products(db, category_norm, brand)
        content = await generate_content(category_norm, brand, products)

        doc = {
            "_key": key,
            "category": category_norm,
            "brand": brand,
            "content": content,
            "source": "ai_generated",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "product_count_at_generation": len(products)
        }
        await db.brand_category_content.update_one({"_key": key}, {"$set": doc}, upsert=True)
        return {"status": "success", "content": content, "source": "ai_generated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")


@router.post("/reconcile")
async def reconcile_missing_content():
    """
    Scans all real products for distinct (category, brand) pairs and generates
    content for any combination that doesn't have it yet. Safe to call repeatedly
    (a cron job, or a manual admin trigger) — already-generated combos are skipped.
    """
    db = await get_db()
    pairs_cursor = db.products.aggregate([
        {"$match": {"category": {"$ne": None}, "brand": {"$ne": None}}},
        {"$group": {"_id": {"category": "$category", "brand": "$brand"}}}
    ])
    pairs = [p["_id"] async for p in pairs_cursor]

    generated, skipped, failed = [], [], []
    for pair in pairs:
        category, brand = pair.get("category"), pair.get("brand")
        if not category or not brand:
            continue
        key = f"{slugify(category)}|{brand}"
        existing = await db.brand_category_content.find_one({"_key": key})
        if existing:
            skipped.append(key)
            continue
        try:
            products = await fetch_grounding_products(db, category, brand)
            content = await generate_content(category, brand, products)
            await db.brand_category_content.update_one(
                {"_key": key},
                {"$set": {
                    "_key": key, "category": category, "brand": brand, "content": content,
                    "source": "ai_generated", "generated_at": datetime.now(timezone.utc).isoformat(),
                    "product_count_at_generation": len(products)
                }},
                upsert=True
            )
            generated.append(key)
        except Exception as e:
            failed.append({"key": key, "error": str(e)})

    return {"status": "success", "generated": generated, "skipped": skipped, "failed": failed}
