path = "/app/backend/quotation_routes.py"
with open(path, "r") as f:
    content = f.read()

old = '''        linked_customer = None
        if quotation.customer_phone:
            linked_customer = await db.customers.find_one(
                {"phone": quotation.customer_phone}, {"_id": 0, "id": 1}
            )
        linked_customer_id = linked_customer["id"] if linked_customer else None'''

new = '''        linked_customer = None
        if quotation.customer_phone:
            normalized_phone = "".join(ch for ch in quotation.customer_phone if ch.isdigit())[-10:]
            if normalized_phone:
                linked_customer = await db.customers.find_one(
                    {"phone": {"$regex": normalized_phone + "$"}}, {"_id": 0, "id": 1}
                )
        linked_customer_id = linked_customer["id"] if linked_customer else None'''

if old not in content:
    print("OLD BLOCK NOT FOUND - aborting, no changes made")
else:
    content = content.replace(old, new)
    with open(path, "w") as f:
        f.write(content)
    print("Patch applied successfully.")
