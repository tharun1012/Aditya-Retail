FILE = "frontend/src/components/DeliveryPersonInterface.js"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

old = "`${BACKEND_URL}/api/invoices/out-for-delivery?delivery_person_id=${deliveryPersonId}`"
new = "`${BACKEND_URL}/api/invoices/offline/invoices/out-for-delivery?delivery_person_id=${deliveryPersonId}`"

if old not in content:
    print("!!! Could not find the URL string to replace. Aborting.")
else:
    content = content.replace(old, new)
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed the invoice endpoint URL.")
