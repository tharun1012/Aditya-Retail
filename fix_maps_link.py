FILE = "frontend/src/components/DeliveryPersonInterface.js"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

old = "                      href={challan.google_maps_link}"
new = "                      href={challan.google_maps_link || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent((challan.customer?.address || '') + ', ' + (challan.customer?.city || '') + ' ' + (challan.customer?.pincode || ''))}`}"

count = content.count(old)
if count == 0:
    print("!!! Could not find the href line to replace. Aborting.")
else:
    content = content.replace(old, new)
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Patched {count} occurrence(s) — Open in Maps now falls back to an address-based Google Maps search link.")
