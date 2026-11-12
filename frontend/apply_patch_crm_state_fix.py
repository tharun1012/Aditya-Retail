path = "/app/frontend/src/components/CustomerCRM.js"
with open(path, "r") as f:
    content = f.read()

old_state = "  const [selectedCustomerId, setSelectedCustomerId] = useState(null);"
new_state = """  const [selectedCustomerId, setSelectedCustomerId] = useState(null);
  const [quotations, setQuotations] = useState([]);
  const [quotationsLoading, setQuotationsLoading] = useState(true);"""

assert old_state in content, "state line not found"
assert content.count(old_state) == 1, "state line not unique"
content = content.replace(old_state, new_state)

with open(path, "w") as f:
    f.write(content)

print("State fix applied successfully.")
