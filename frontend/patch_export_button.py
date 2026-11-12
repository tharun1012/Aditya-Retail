path = "/app/frontend/src/components/OrderManagement.js"
with open(path, "r") as f:
    content = f.read()

# 1. Add the handler function, right after handleCleanupOffline's closing brace
marker_func = '''  const updateOrderStatus = async (orderId, newStatus) => {'''
assert content.count(marker_func) == 1, "handler insertion marker not unique/found"

export_handler = '''  const handleExportOrders = (format) => {
    const params = new URLSearchParams();
    if (filterStatus !== 'all') params.set('status', filterStatus);
    if (orderTypeFilter !== 'all') params.set('order_type', orderTypeFilter);
    if (dateFrom) params.set('date_from', dateFrom);
    if (dateTo) params.set('date_to', dateTo);
    if (storeFilter) params.set('store_code', storeFilter);
    params.set('format', format);
    const url = `${BACKEND_URL}/api/admin/orders/export?${params.toString()}`;
    window.open(url, '_blank');
  };

'''

content = content.replace(marker_func, export_handler + marker_func, 1)

# 2. Add the two buttons right before the Cleanup Offline button
marker_btn = '''                  onClick={handleCleanupOffline}'''
assert content.count(marker_btn) == 1, "button insertion marker not unique/found"

export_buttons = '''                  onClick={() => handleExportOrders('xlsx')}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                  title="Export current filtered orders as Excel"
                >
                  <Download className="w-4 h-4" />
                  Export Excel
                </button>
                <button
                  onClick={() => handleExportOrders('csv')}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm"
                  title="Export current filtered orders as CSV"
                >
                  <Download className="w-4 h-4" />
                  Export CSV
                </button>
                <button
'''

content = content.replace(
    '                <button\n' + marker_btn,
    export_buttons + marker_btn,
    1
)

with open(path, "w") as f:
    f.write(content)

print("Frontend patched successfully.")
