import re


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


async def find_store_for_customer(db, email=None, phone=None, product_name=None, invoice_number=None):
    """Find which store sold to this customer: by invoice number, else by the customer's invoices
    (prefer one containing the same product, else the most recent)."""
    proj = {"_id": 0, "invoice_number": 1, "store_code": 1, "store_details.name": 1, "items.product_name": 1, "created_at": 1}
    inv = None
    if invoice_number:
        inv = await db.offline_invoices.find_one({"invoice_number": invoice_number}, proj)
    if not inv:
        ors = []
        if email and email.strip():
            ors.append({"customer.email": {"$regex": f"^{re.escape(email.strip())}$", "$options": "i"}})
        p = re.sub(r"\D", "", phone or "")[-10:]
        if len(p) == 10:
            ors.append({"customer.phone": {"$regex": f"{p}$"}})
        if not ors:
            return None
        invs = await db.offline_invoices.find({"document_type": "invoice", "$or": ors}, proj).sort("created_at", -1).limit(50).to_list(50)
        pn = _norm(product_name)
        for i in invs:
            for it in i.get("items") or []:
                n = _norm(it.get("product_name"))
                if pn and n and (pn in n or n in pn):
                    inv = i
                    break
            if inv:
                break
        if not inv and invs:
            inv = invs[0]
    if not inv or not inv.get("store_code"):
        return None
    return {"store_code": inv["store_code"], "store_name": (inv.get("store_details") or {}).get("name"),
            "invoice_number": inv.get("invoice_number")}
