path = "backend/offline_invoice_routes.py"
with open(path, "r") as f:
    content = f.read()

changes_made = []

# 1. Add the import near the top of the file, right after the first import block
import_old = "import uuid"
import_new = "import uuid\nfrom utils import normalize_phone"
if import_new not in content and import_old in content:
    content = content.replace(import_old, import_new, 1)
    changes_made.append("added import")

# 2. Replace the phone lookup + create/update block
old = '''        # Save customer to customers collection if phone number exists
        if customer_data.get("phone"):
            existing_customer = await db.customers.find_one({"phone": customer_data.get("phone")})
            if existing_customer:'''

new = '''        # Save customer to customers collection if phone number exists
        if customer_data.get("phone"):
            normalized_phone = normalize_phone(customer_data.get("phone"))
            existing_customer = await db.customers.find_one({"phone": normalized_phone}) if normalized_phone else None
            if existing_customer:'''

if old not in content:
    print("BLOCK 1 NOT FOUND - aborting, no changes written")
    exit()
content = content.replace(old, new)
changes_made.append("normalized lookup")

# 3. Store the normalized phone on both update and new-customer paths, and add order_count/total_spent
old2 = '''                new_customer = {
                    "id": customer_id,
                    "name": customer_data.get("name"),
                    "phone": customer_data.get("phone"),
                    "email": customer_data.get("email"),'''

new2 = '''                new_customer = {
                    "id": customer_id,
                    "name": customer_data.get("name"),
                    "phone": normalized_phone,
                    "email": customer_data.get("email"),
                    "order_count": 0,
                    "total_spent": 0,'''

if old2 not in content:
    print("BLOCK 2 NOT FOUND - aborting, no changes written")
    exit()
content = content.replace(old2, new2)
changes_made.append("normalized new-customer phone + added order_count/total_spent")

with open(path, "w") as f:
    f.write(content)

print("Patch applied successfully:", ", ".join(changes_made))
