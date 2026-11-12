path = "/app/backend/quotation_routes.py"

with open(path, "r") as f:
    content = f.read()

old = '''        quotation_data = {
            "id": quotation_id,
            "quotation_number": quotation_number,
            "store_id": quotation.store_id,
            "store_code": store["code"],
            "store_name": store["name"],
            "store_address": store.get("address", ""),
            "store_phone": store.get("phone", ""),
            "store_gst": store.get("gst_number", ""),
            "customer_name": quotation.customer_name,
            "customer_email": quotation.customer_email,
            "customer_phone": quotation.customer_phone,
            "customer_address": quotation.customer_address,'''

new = '''        # Link this quotation to an existing CRM customer record, if one
        # matches by phone. Stored as None when no match is found so
        # walk-in / non-CRM customers don't block quotation creation.
        linked_customer = None
        if quotation.customer_phone:
            linked_customer = await db.customers.find_one(
                {"phone": quotation.customer_phone}, {"_id": 0, "id": 1}
            )
        linked_customer_id = linked_customer["id"] if linked_customer else None

        quotation_data = {
            "id": quotation_id,
            "quotation_number": quotation_number,
            "store_id": quotation.store_id,
            "store_code": store["code"],
            "store_name": store["name"],
            "store_address": store.get("address", ""),
            "store_phone": store.get("phone", ""),
            "store_gst": store.get("gst_number", ""),
            "customer_id": linked_customer_id,
            "customer_name": quotation.customer_name,
            "customer_email": quotation.customer_email,
            "customer_phone": quotation.customer_phone,
            "customer_address": quotation.customer_address,'''

if old not in content:
    raise SystemExit("OLD BLOCK NOT FOUND — aborting, no changes made.")
if content.count(old) != 1:
    raise SystemExit(f"OLD BLOCK MATCHES {content.count(old)} TIMES — expected exactly 1. Aborting.")

content = content.replace(old, new)

with open(path, "w") as f:
    f.write(content)

print("Patch A applied successfully.")
