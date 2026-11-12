path = "backend/customers_routes.py"
with open(path, "r") as f:
    content = f.read()

changes_made = []

# 1. Add the import
import_old = "import uuid"
import_new = "import uuid\nfrom utils import normalize_phone"
if import_new not in content and import_old in content:
    content = content.replace(import_old, import_new, 1)
    changes_made.append("added import")

# 2. Normalize phone before the duplicate check, and store the normalized value
old = '''        # Check if customer with phone already exists
        existing = await db.customers.find_one({"phone": customer.phone})
        if existing:
            raise HTTPException(status_code=400, detail="Customer with this phone number already exists")
        
        customer_data = {
            "id": str(uuid.uuid4()),
            "name": customer.name,
            "phone": customer.phone,'''

new = '''        # Check if customer with phone already exists
        normalized_phone = normalize_phone(customer.phone)
        existing = await db.customers.find_one({"phone": normalized_phone}) if normalized_phone else None
        if existing:
            raise HTTPException(status_code=400, detail="Customer with this phone number already exists")
        
        customer_data = {
            "id": str(uuid.uuid4()),
            "name": customer.name,
            "phone": normalized_phone,'''

if old not in content:
    print("BLOCK NOT FOUND - aborting, no changes written")
    exit()
content = content.replace(old, new)
changes_made.append("normalized phone in create_customer")

with open(path, "w") as f:
    f.write(content)

print("Patch applied successfully:", ", ".join(changes_made))
