path = "/app/frontend/src/components/CustomerCRM.js"
with open(path, "r") as f:
    content = f.read()

# 1. Add BACKEND_URL import (only used for window.open calls)
import_old = "import { utils } from '../services/api';"
import_new = "import { utils } from '../services/api';\nimport { BACKEND_URL } from '../config/api';"
assert content.count(import_old) == 1, "utils import not found or not unique"
content = content.replace(import_old, import_new)

# 2. Add state for selected quotation + view modal visibility
state_old = "  const [selectedSegment, setSelectedSegment] = useState(null);"
state_new = state_old + "\n  const [selectedQuotation, setSelectedQuotation] = useState(null);\n  const [showViewModal, setShowViewModal] = useState(false);"
assert content.count(state_old) == 1, "selectedSegment state line not found or not unique"
content = content.replace(state_old, state_new)

with open(path, "w") as f:
    f.write(content)

print("Import and state added successfully.")
