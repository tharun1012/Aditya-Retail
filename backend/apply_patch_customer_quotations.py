path = "/app/backend/customers_routes.py"

with open(path, "r") as f:
    content = f.read()

old = '''        # Get customer's orders (limit to most recent 100 for performance)
        orders = await db.orders.find({"customer_id": customer_id}, {"_id": 0}).sort("created_at", -1).limit(100).to_list(100)
        
        return {
            "status": "success",
            "customer": customer,
            "orders": orders
        }'''

new = '''        # Get customer's orders (limit to most recent 100 for performance)
        orders = await db.orders.find({"customer_id": customer_id}, {"_id": 0}).sort("created_at", -1).limit(100).to_list(100)

        # Get customer's quotations. Match by linked customer_id (new
        # quotations) OR by phone (older quotations created before the
        # customer_id link existed), so nothing falls through the cracks.
        quotation_query = {"customer_id": customer_id}
        if customer.get("phone"):
            quotation_query = {
                "$or": [
                    {"customer_id": customer_id},
                    {"customer_phone": customer["phone"]}
                ]
            }
        quotations = await db.quotations.find(quotation_query, {"_id": 0}).sort("created_at", -1).limit(100).to_list(100)

        return {
            "status": "success",
            "customer": customer,
            "orders": orders,
            "quotations": quotations
        }'''

if old not in content:
    raise SystemExit("OLD BLOCK NOT FOUND — aborting, no changes made.")
if content.count(old) != 1:
    raise SystemExit(f"OLD BLOCK MATCHES {content.count(old)} TIMES — expected exactly 1. Aborting.")

content = content.replace(old, new)

with open(path, "w") as f:
    f.write(content)

print("Patch B applied successfully.")
