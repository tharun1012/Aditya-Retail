"""AI Product Comparison routes — Claude-powered side-by-side comparison"""
import os
import uuid
import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from database import get_db
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products-compare", tags=["Product Comparison"])


class CompareRequest(BaseModel):
    product_id_1: str
    product_id_2: str


def _product_context(p: dict) -> str:
    specs = p.get('specifications')
    if isinstance(specs, dict):
        specs_text = "; ".join(f"{k}: {v}" for k, v in list(specs.items())[:20])
    elif isinstance(specs, list):
        specs_text = "; ".join(str(s.get('value', s) if isinstance(s, dict) else s) for s in specs[:20])
    else:
        specs_text = str(specs or '')[:800]
    features = p.get('features') or []
    return (
        f"Name: {p.get('name')}\nBrand: {p.get('brand')}\nModel: {p.get('model_number')}\n"
        f"Category: {p.get('category')}\nPrice: ₹{p.get('price', 0):,}\n"
        f"Stock: {p.get('stock_quantity', 0)}\nWarranty: {p.get('warranty_period', '2 years')}\n"
        f"Description: {str(p.get('description') or '')[:500]}\n"
        f"Specifications: {specs_text}\n"
        f"Features: {', '.join(str(f) for f in features[:15])}"
    )


@router.post("/")
async def compare_products(req: CompareRequest, db = Depends(get_db)):
    """Generate (or return cached) AI comparison of two products"""
    try:
        pair_key = "_".join(sorted([req.product_id_1, req.product_id_2]))
        cached = await db.product_comparisons.find_one({"pair_key": pair_key}, {"_id": 0})
        if cached:
            return {"status": "success", "cached": True, "comparison": cached["comparison"]}

        p1 = await db.products.find_one({"id": req.product_id_1}, {"_id": 0})
        p2 = await db.products.find_one({"id": req.product_id_2}, {"_id": 0})
        if not p1 or not p2:
            raise HTTPException(status_code=404, detail="One or both products not found")

        prompt = f"""Compare these two appliances for an Indian retail customer. Respond with ONLY valid JSON (no markdown fences, no extra text) in exactly this schema:
{{
  "summary": "2-3 sentence overview of the comparison",
  "rows": [
    {{"feature": "Price", "product1": "...", "product2": "...", "advantage": "product1|product2|tie"}},
    ... 8-12 rows covering price, capacity/size, key features, energy efficiency, build quality, warranty, brand strengths, value for money ...
  ],
  "verdict": "Clear 2-3 sentence recommendation on who should buy which product",
  "best_for_product1": "one line: ideal buyer for product 1",
  "best_for_product2": "one line: ideal buyer for product 2"
}}

PRODUCT 1:
{_product_context(p1)}

PRODUCT 2:
{_product_context(p2)}"""

        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"compare-{uuid.uuid4().hex[:8]}",
            system_message="You are an expert home-appliance consultant. You output ONLY valid JSON."
        ).with_model("anthropic", "claude-sonnet-4-6")

        response = await chat.send_message(UserMessage(text=prompt))
        text = str(response).strip()
        if text.startswith("```"):
            text = text.split("```")[1].lstrip("json").strip()
        comparison = json.loads(text)
        comparison["product1"] = {"id": p1["id"], "name": p1.get("name"), "brand": p1.get("brand"),
                                  "price": p1.get("price", 0), "image": (p1.get("images") or [p1.get("image_url")])[0]}
        comparison["product2"] = {"id": p2["id"], "name": p2.get("name"), "brand": p2.get("brand"),
                                  "price": p2.get("price", 0), "image": (p2.get("images") or [p2.get("image_url")])[0]}

        await db.product_comparisons.insert_one({
            "pair_key": pair_key,
            "comparison": comparison,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        return {"status": "success", "cached": False, "comparison": comparison}
    except HTTPException:
        raise
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="AI returned an invalid comparison. Please try again.")
    except Exception as e:
        logger.error(f"Product comparison error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
