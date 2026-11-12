path = "/app/frontend/src/components/CustomerCRM.js"
with open(path, "r") as f:
    content = f.read()

# 1. Add the import (adjust if CustomerCRM.js already imports something from QuotationManagement)
import_old = "import React"
import_new = "import { ViewQuotationModal } from './QuotationManagement';\nimport React"

assert content.count(import_old) >= 1, "React import not found"
content = content.replace(import_old, import_new, 1)

with open(path, "w") as f:
    f.write(content)

print("Import added successfully.")
