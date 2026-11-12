path = "/app/frontend/src/components/CustomerCRM.js"
with open(path, "r") as f:
    content = f.read()

old_marker = """        {selectedCustomerId && (
          <CustomerDetailModal"""

new_marker = """        {/* Quotations Section */}
        <Card className="mb-8 mt-8">
          <CardHeader>
            <CardTitle>Quotations</CardTitle>
            <CardDescription>All quotations created, across all customers</CardDescription>
          </CardHeader>
          <CardContent>
            {quotationsLoading ? (
              <div className="text-center py-8 text-gray-500 text-sm">Loading quotations...</div>
            ) : quotations.length === 0 ? (
              <div className="text-center py-12">
                <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Quotations Found</h3>
                <p className="text-gray-600">Quotations you create will show up here.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 font-semibold text-sm text-gray-600">Quotation #</th>
                      <th className="text-left py-3 px-4 font-semibold text-sm text-gray-600">Customer</th>
                      <th className="text-left py-3 px-4 font-semibold text-sm text-gray-600">Contact</th>
                      <th className="text-right py-3 px-4 font-semibold text-sm text-gray-600">Amount</th>
                      <th className="text-center py-3 px-4 font-semibold text-sm text-gray-600">Status</th>
                      <th className="text-right py-3 px-4 font-semibold text-sm text-gray-600">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {quotations.map((q, index) => (
                      <tr key={q.id || index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                        <td className="py-4 px-4">
                          <span className="font-semibold text-orange-600">{q.quotation_number || '-'}</span>
                        </td>
                        <td className="py-4 px-4">
                          <span className="text-sm text-gray-900">{q.customer_name || 'Unknown'}</span>
                        </td>
                        <td className="py-4 px-4">
                          <span className="text-sm text-gray-500">{q.customer_phone || '-'}</span>
                        </td>
                        <td className="py-4 px-4 text-right">
                          <span className="text-sm font-semibold text-gray-900">
                            {formatCurrency(q.total_amount || q.grand_total || q.total || 0)}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-center">
                          {quotationStatusBadge(q.status)}
                        </td>
                        <td className="py-4 px-4 text-right">
                          <span className="text-sm text-gray-500">{formatDate(q.created_at)}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>

        {selectedCustomerId && (
          <CustomerDetailModal"""

assert old_marker in content, "insertion marker not found"
content = content.replace(old_marker, new_marker)

with open(path, "w") as f:
    f.write(content)

print("Quotations table section inserted successfully.")
