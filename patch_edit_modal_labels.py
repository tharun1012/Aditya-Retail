#!/usr/bin/env python3
import shutil

TARGET = "frontend/src/components/AdminPORequestsView.js"
with open(TARGET, "r") as f:
    content = f.read()
shutil.copy(TARGET, TARGET + ".bak3")

old = '''          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Items</label>
            <div className="space-y-2">
              {items.map((item, idx) => (
                <div key={idx} className="grid grid-cols-12 gap-2 items-center">
                  <input
                    className="col-span-3 px-2 py-1.5 border rounded text-sm"
                    placeholder="Model / SKU"
                    value={item.model_number}
                    onChange={(e) => updateItem(idx, 'model_number', e.target.value)}
                  />
                  <input
                    className="col-span-3 px-2 py-1.5 border rounded text-sm"
                    placeholder="Product name"
                    value={item.product_name}
                    onChange={(e) => updateItem(idx, 'product_name', e.target.value)}
                  />
                  <input
                    type="number"
                    className="col-span-2 px-2 py-1.5 border rounded text-sm"
                    placeholder="Qty"
                    value={item.quantity}
                    onChange={(e) => updateItem(idx, 'quantity', e.target.value)}
                  />
                  <input
                    type="number"
                    className="col-span-2 px-2 py-1.5 border rounded text-sm"
                    placeholder="Unit price"
                    value={item.cost_price}
                    onChange={(e) => updateItem(idx, 'cost_price', e.target.value)}
                  />
                  <span className="col-span-1 text-xs text-gray-600 text-right">
                    ₹{((parseFloat(item.quantity) || 0) * (parseFloat(item.cost_price) || 0)).toLocaleString()}
                  </span>
                  <button
                    type="button"
                    onClick={() => removeItem(idx)}
                    className="col-span-1 p-1 text-red-500 hover:bg-red-50 rounded"
                    disabled={items.length === 1}
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>'''

new = '''          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Items</label>
            <div className="grid grid-cols-12 gap-2 mb-1 px-1">
              <span className="col-span-3 text-xs font-medium text-gray-500 uppercase">Model / SKU</span>
              <span className="col-span-3 text-xs font-medium text-gray-500 uppercase">Product Name</span>
              <span className="col-span-2 text-xs font-medium text-gray-500 uppercase">Quantity</span>
              <span className="col-span-2 text-xs font-medium text-gray-500 uppercase">Unit Price</span>
              <span className="col-span-1 text-xs font-medium text-gray-500 uppercase text-right">Total</span>
              <span className="col-span-1"></span>
            </div>
            <div className="space-y-2">
              {items.map((item, idx) => (
                <div key={idx} className="grid grid-cols-12 gap-2 items-center">
                  <input
                    className="col-span-3 px-2 py-1.5 border rounded text-sm"
                    placeholder="Model / SKU"
                    value={item.model_number}
                    onChange={(e) => updateItem(idx, 'model_number', e.target.value)}
                  />
                  <input
                    className="col-span-3 px-2 py-1.5 border rounded text-sm"
                    placeholder="Product name"
                    value={item.product_name}
                    onChange={(e) => updateItem(idx, 'product_name', e.target.value)}
                  />
                  <input
                    type="number"
                    className="col-span-2 px-2 py-1.5 border rounded text-sm"
                    placeholder="Qty"
                    value={item.quantity}
                    onChange={(e) => updateItem(idx, 'quantity', e.target.value)}
                  />
                  <input
                    type="number"
                    className="col-span-2 px-2 py-1.5 border rounded text-sm"
                    placeholder="Unit price"
                    value={item.cost_price}
                    onChange={(e) => updateItem(idx, 'cost_price', e.target.value)}
                  />
                  <span className="col-span-1 text-xs text-gray-600 text-right">
                    ₹{((parseFloat(item.quantity) || 0) * (parseFloat(item.cost_price) || 0)).toLocaleString()}
                  </span>
                  <button
                    type="button"
                    onClick={() => removeItem(idx)}
                    className="col-span-1 p-1 text-red-500 hover:bg-red-50 rounded"
                    disabled={items.length === 1}
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>'''

assert old in content, "Anchor not found - EditPORequestModal items section did not match exactly"
content = content.replace(old, new, 1)

with open(TARGET, "w") as f:
    f.write(content)

print("Patched", TARGET)
