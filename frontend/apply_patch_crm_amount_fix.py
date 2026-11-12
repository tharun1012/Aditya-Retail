path = "/app/frontend/src/components/CustomerCRM.js"
with open(path, "r") as f:
    content = f.read()

old = """                          <span className="text-sm font-semibold text-gray-900">
                            {formatCurrency(q.total_amount || q.grand_total || q.total || 0)}
                          </span>"""

new = """                          <span className="text-sm font-semibold text-gray-900">
                            {formatCurrency(q.totals?.grand_total || q.total_amount || q.grand_total || q.total || 0)}
                          </span>"""

assert content.count(old) == 1, "amount span not found or not unique"
content = content.replace(old, new)

with open(path, "w") as f:
    f.write(content)

print("Amount field fixed successfully.")
