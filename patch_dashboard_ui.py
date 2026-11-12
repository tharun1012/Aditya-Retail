import os, re, shutil
C = "/app/frontend/src/components"
BK = "/app/_backup/ui"
os.makedirs(BK, exist_ok=True)

def load(fn):
    p = f"{C}/{fn}"
    shutil.copy(p, f"{BK}/{fn}")
    return p, open(p).read()

def rep(src, old, new, label):
    n = src.count(old)
    if n != 1:
        print(f"  SKIP {label}: anchor found {n} times (expected 1)")
        return src
    print(f"  ok   {label}")
    return src.replace(old, new)

# ---------- Login.js: Forgot Password link ----------
p, src = load("Login.js")
print("Login.js")
pat = re.compile(r'(<button\s+type="button"\s+)(className="text-sm text-red-600 hover:text-red-700 transition-colors"\s*>\s*Forgot Password\?)')
src2, n = pat.subn(lambda m: m.group(1) + "onClick={() => { window.location.href = '/reset-password'; }}\n                " + m.group(2), src)
print("  ok   forgot link" if n == 1 else f"  SKIP forgot link: matched {n}")
open(p, "w").write(src2 if n == 1 else src)

# ---------- CustomerDashboard.js ----------
p, src = load("CustomerDashboard.js")
print("CustomerDashboard.js")

# import change-password card
src = rep(src, "import React, { useState, useEffect } from 'react';",
  "import React, { useState, useEffect } from 'react';\nimport ChangePasswordCard from './ChangePasswordCard';", "import card")

# timeline state + fetch
src = rep(src, "  const [showOrderDetail, setShowOrderDetail] = useState(false);",
r'''  const [showOrderDetail, setShowOrderDetail] = useState(false);
  const [timeline, setTimeline] = useState(null);
  useEffect(() => {
    if (!showOrderDetail || !selectedOrder || !user) { setTimeline(null); return; }
    fetch(`${BACKEND_URL}/api/customer/orders/${selectedOrder.id}/timeline?user_id=${user.id}`)
      .then(r => r.json())
      .then(d => setTimeline(d.status === 'success' ? d : null))
      .catch(() => setTimeline(null));
  }, [showOrderDetail, selectedOrder, user]);''', "timeline state")

# timeline block above shipping info
src = rep(src, "              {/* Shipping Info */}",
r'''              {/* Order Progress Timeline */}
              {timeline && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-4">Order Progress</h4>
                  {timeline.cancelled ? (
                    <p className="text-sm text-red-600 font-medium">This order was cancelled.</p>
                  ) : (
                    <div className="flex items-start justify-between">
                      {timeline.steps.map((s) => (
                        <div key={s.stage} className="flex-1 text-center">
                          <div className={`mx-auto w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${s.done ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-500'} ${s.current ? 'ring-4 ring-green-200' : ''}`}>
                            {s.done ? '✓' : ''}
                          </div>
                          <div className="mt-1 text-xs capitalize text-gray-700">{s.stage.replace(/_/g, ' ')}</div>
                          {s.at && <div className="text-[10px] text-gray-500">{formatDate(s.at)}</div>}
                        </div>
                      ))}
                    </div>
                  )}
                  {(timeline.awb || timeline.courier) && (
                    <p className="text-sm text-gray-600 mt-4">
                      {timeline.courier && <span>Courier: <b>{timeline.courier}</b> </span>}
                      {timeline.awb && <span>AWB: <b>{timeline.awb}</b> </span>}
                      {timeline.tracking_url && <a href={timeline.tracking_url} target="_blank" rel="noreferrer" className="text-blue-600 underline ml-2">Track shipment</a>}
                    </p>
                  )}
                  <p className="text-xs text-gray-500 mt-3">
                    Payment: {(timeline.payment_method || '').toUpperCase()} ({timeline.payment_status})
                  </p>
                </div>
              )}

              {/* Shipping Info */}''', "timeline block")

# products: days left + warranty terms
src = rep(src, "{formatDate(product.warranty_end_date)}</p>",
  "{formatDate(product.warranty_end_date)}</p>\n                            {product.warranty_days_remaining > 0 && <p className=\"text-xs text-gray-500\">{product.warranty_days_remaining} days left</p>}",
  "days left")
src = rep(src, '<p className="text-sm text-gray-500">Invoice: {product.invoice_number}</p>',
  '''<p className="text-sm text-gray-500">Invoice: {product.invoice_number}</p>
                              {(product.brand || product.model_number) && <p className="text-xs text-gray-500">{[product.brand, product.model_number].filter(Boolean).join(' · ')}</p>}
                              {product.warranty_terms && <p className="text-xs text-gray-500 mt-1">{product.warranty_terms}</p>}''',
  "product details")

# quick orders: reason, price, image, button label
src = rep(src, '<p className="text-sm text-gray-500">For: {suggestion.product_name}</p>',
  '''<p className="text-sm text-gray-500">{suggestion.reason || `For: ${suggestion.product_name}`}</p>
                              {suggestion.price ? <p className="text-sm font-semibold text-gray-900 mt-1">₹{Number(suggestion.price).toLocaleString('en-IN')}</p> : null}
                              {suggestion.image ? <img src={suggestion.image} alt="" className="h-16 mt-2 rounded object-contain" /> : null}''',
  "suggestion card details")
src = rep(src, "Add to Quick Order",
  "{suggestion.in_catalog === false ? 'Ask Us to Source' : (suggestion.kind === 'reorder' ? 'Reorder' : 'Add to Quick Order')}",
  "suggestion button label")

# change password card after profile tab
src = rep(src, "            {/* Addresses Tab */}",
  "            {activeTab === 'profile' && <ChangePasswordCard />}\n\n            {/* Addresses Tab */}", "change password card")

open(p, "w").write(src)
