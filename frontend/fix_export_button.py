path = "/app/frontend/src/components/OrderManagement.js"
with open(path, "r") as f:
    content = f.read()

broken = "                  onClick={() => handleExportOrders('xlsx')}"
assert content.count(broken) == 1, f"expected 1 occurrence, found {content.count(broken)}"

fixed = "                <button\n" + broken

content = content.replace(broken, fixed, 1)

with open(path, "w") as f:
    f.write(content)

print("Fixed missing opening <button> tag.")
