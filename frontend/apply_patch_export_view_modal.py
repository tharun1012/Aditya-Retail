path = "/app/frontend/src/components/QuotationManagement.js"
with open(path, "r") as f:
    content = f.read()

old = "const ViewQuotationModal = ({ quotation, onClose, onDownload, onWhatsApp, API_URL }) => {"
new = "export const ViewQuotationModal = ({ quotation, onClose, onDownload, onWhatsApp, API_URL }) => {"

assert content.count(old) == 1, "ViewQuotationModal declaration not found or not unique"
content = content.replace(old, new)

with open(path, "w") as f:
    f.write(content)

print("ViewQuotationModal exported successfully.")
