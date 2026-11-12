#!/usr/bin/env python3
import shutil

TARGET = "frontend/src/components/AdminPORequestsView.js"
with open(TARGET, "r") as f:
    content = f.read()
shutil.copy(TARGET, TARGET + ".bak4")

# --- Fix 1: select options use unique store.code as value/key instead of ambiguous store.name ---
old_1 = '''                      {stores.map(store => (
                        <option key={store.code || store.id} value={store.name}>
                          {store.name} ({store.code})
                        </option>
                      ))}'''
new_1 = '''                      {stores.map(store => (
                        <option key={store.code || store.id} value={store.code}>
                          {store.name} ({store.code})
                        </option>
                      ))}'''
assert old_1 in content, "EDIT 1 anchor not found"
content = content.replace(old_1, new_1, 1)

# --- Fix 2: build unambiguous delivery_location text from the matched store before submitting ---
old_2 = '''          body: JSON.stringify({
            action: approvalAction,
            delivery_location: deliveryLocation,
            rejection_reason: approvalAction === 'reject' ? rejectionReason : null,'''
new_2 = '''          body: JSON.stringify({
            action: approvalAction,
            delivery_location: (() => {
              const selStore = stores.find(s => s.code === deliveryLocation);
              return selStore ? `${selStore.name} (${selStore.code})` : deliveryLocation;
            })(),
            rejection_reason: approvalAction === 'reject' ? rejectionReason : null,'''
assert old_2 in content, "EDIT 2 anchor not found"
content = content.replace(old_2, new_2, 1)

with open(TARGET, "w") as f:
    f.write(content)

print("Patched", TARGET)
