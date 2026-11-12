path = "/app/frontend/src/components/CustomerCRM.js"
with open(path, "r") as f:
    content = f.read()

# 1. Add icons to lucide-react import
icon_old = "import { Users, TrendingUp, UserCheck, AlertCircle, Search, Filter, ArrowLeft } from 'lucide-react';"
icon_new = "import { Users, TrendingUp, UserCheck, AlertCircle, Search, Filter, ArrowLeft, Eye, Download, Send } from 'lucide-react';"
assert content.count(icon_old) == 1, "lucide-react import not found or not unique"
content = content.replace(icon_old, icon_new)

# 2. Add Actions header
header_old = """                      <th className="text-right py-3 px-4 font-semibold text-sm text-gray-600">Created</th>
                    </tr>"""
header_new = """                      <th className="text-right py-3 px-4 font-semibold text-sm text-gray-600">Created</th>
                      <th className="text-center py-3 px-4 font-semibold text-sm text-gray-600">Actions</th>
                    </tr>"""
assert content.count(header_old) == 1, "table header not found or not unique"
content = content.replace(header_old, header_new)

# 3. Add Actions cell to each row
row_old = """                        <td className="py-4 px-4 text-right">
                          <span className="text-sm text-gray-500">{formatDate(q.created_at)}</span>
                        </td>
                      </tr>"""
row_new = """                        <td className="py-4 px-4 text-right">
                          <span className="text-sm text-gray-500">{formatDate(q.created_at)}</span>
                        </td>
                        <td className="py-4 px-4">
                          <div className="flex items-center justify-center space-x-1">
                            <button
                              onClick={() => handleViewQuotation(q.id)}
                              className="p-2 text-gray-500 hover:text-amber-600 hover:bg-amber-50 rounded-lg"
                              title="View"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDownloadPDF(q.id)}
                              className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg"
                              title="Download PDF"
                            >
                              <Download className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleWhatsApp(q.id)}
                              className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg"
                              title="Share on WhatsApp"
                            >
                              <Send className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>"""
assert content.count(row_old) == 1, "table row closing not found or not unique"
content = content.replace(row_old, row_new)

# 4. Render ViewQuotationModal, alongside existing CustomerDetailModal
modal_old = """        {selectedCustomerId && (
          <CustomerDetailModal
            customerId={selectedCustomerId}
            onClose={() => setSelectedCustomerId(null)}
          />
        )}"""
modal_new = modal_old + """

        {showViewModal && selectedQuotation && (
          <ViewQuotationModal
            quotation={selectedQuotation}
            onClose={() => setShowViewModal(false)}
            onDownload={() => handleDownloadPDF(selectedQuotation.id)}
            onWhatsApp={() => handleWhatsApp(selectedQuotation.id)}
            API_URL={BACKEND_URL}
          />
        )}"""
assert content.count(modal_old) == 1, "CustomerDetailModal render block not found or not unique"
content = content.replace(modal_old, modal_new)

with open(path, "w") as f:
    f.write(content)

print("Table actions and modal added successfully.")
