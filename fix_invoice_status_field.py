FILE = "frontend/src/components/DeliveryPersonInterface.js"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

old = """        payment_details: null,
        google_maps_link: null,
        source: 'invoice'
      }));"""

new = """        payment_details: null,
        google_maps_link: null,
        status: inv.delivered_at ? 'delivered' : 'pending',
        source: 'invoice'
      }));"""

if old not in content:
    print("!!! Could not find the block to replace. Aborting.")
else:
    content = content.replace(old, new)
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print("Added status field to invoice normalization.")
