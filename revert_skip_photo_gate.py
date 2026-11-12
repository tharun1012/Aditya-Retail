FILE = "frontend/src/components/DeliveryPersonInterface.js"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

new = "{(challan.source === 'invoice' || (challan.delivery_photos.length > 0 && (!challan.is_cod && !challan.is_pod || challan.payment_collected))) && ("
old = "{challan.delivery_photos.length > 0 && (!challan.is_cod && !challan.is_pod || challan.payment_collected) && ("

count = content.count(new)
if count == 0:
    print("!!! Could not find the patched condition to revert. Aborting.")
else:
    content = content.replace(new, old)
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Reverted {count} occurrence(s) back to the original photo-proof gate.")
