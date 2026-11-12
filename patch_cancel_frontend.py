import re, shutil, os
p = "/app/frontend/src/components/CustomerDashboard.js"
s = open(p).read()
if "cancelMyOrder" in s:
    raise SystemExit("already patched")
fn_a = "  const handleAddAddress = async () => {"
btn_re = re.compile(r"<button\s+onClick=\{\(\) => fetchOrderDetail\(order\.id\)\}")
counts = {"fn": s.count(fn_a), "btn": len(btn_re.findall(s))}
print("anchors:", counts)
if any(v != 1 for v in counts.values()):
    raise SystemExit("ABORT: anchors not unique, nothing written")
fn = """  const cancelMyOrder = async (order) => {
    if (!window.confirm('Cancel this order? This cannot be undone.')) return;
    const reason = window.prompt('Reason for cancelling (optional):') || '';
    try {
      const response = await authFetch(`${BACKEND_URL}/api/customer/orders/${order.id}/cancel?user_id=${user.id}&reason=${encodeURIComponent(reason)}`, { method: 'POST' });
      const data = await response.json().catch(() => ({}));
      if (response.ok && data.status === 'success') {
        alert(data.message || 'Order cancelled.');
        fetchOrders(user.id);
      } else {
        alert(data.detail || 'Could not cancel this order.');
      }
    } catch (error) {
      console.error('Error cancelling order:', error);
      alert('Could not cancel this order. Please try again.');
    }
  };

"""
btn = """{['placed', 'pending', 'confirmed'].includes(order.order_status) && !order.sr_awb_code && !order.shiprocket_order_id && (
                                <button
                                  onClick={() => cancelMyOrder(order)}
                                  className="px-4 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors"
                                >
                                  Cancel Order
                                </button>
                              )}
                              """
s = s.replace(fn_a, fn + fn_a, 1)
s = btn_re.sub(lambda m: btn + m.group(0), s, count=1)
os.makedirs("/app/_backup/cancelfe", exist_ok=True)
shutil.copy(p, "/app/_backup/cancelfe/CustomerDashboard.js")
open(p, "w").write(s)
print("written OK")
