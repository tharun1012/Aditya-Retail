#!/usr/bin/env python3
import shutil

TARGET = "frontend/src/components/PORequestsTab.js"
with open(TARGET, "r") as f:
    content = f.read()
shutil.copy(TARGET, TARGET + ".bak_search2")

old_row = '''              {items.map((item, index) => (
                <div key={index} className="flex gap-2 items-start">
                  <div className="flex-1">
                    <input
                      type="text"
                      value={item.model_number}
                      onChange={(e) => updateItem(index, 'model_number', e.target.value)}
                      placeholder="Model Number / SKU"
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                      required
                    />
                  </div>
                  <div className="w-24">
                    <input
                      type="number"
                      value={item.quantity}
                      onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value) || 1)}
                      placeholder="Qty"
                      min="1"
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                      required
                    />
                  </div>
                  <div className="flex-1">
                    <input
                      type="text"
                      value={item.notes}
                      onChange={(e) => updateItem(index, 'notes', e.target.value)}
                      placeholder="Notes (optional)"
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                    />
                  </div>
                  <button
                    type="button"
                    onClick={() => removeItem(index)}
                    className="p-2 text-red-500 hover:bg-red-50 rounded-lg"
                    disabled={items.length === 1}
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}'''

new_row = '''              {items.map((item, index) => (
                <div key={index} className="border rounded-lg p-3 space-y-2">
                  <div className="flex gap-2 items-start">
                    <div className="flex-1 relative">
                      <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="text"
                        value={productSearch[index] || ''}
                        onChange={(e) => setProductSearch({ ...productSearch, [index]: e.target.value })}
                        placeholder="Type model no, brand or product name to search..."
                        className="w-full pl-8 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                      />
                      {productSearch[index] && productSearch[index].length > 1 && (
                        <div className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg max-h-60 overflow-y-auto">
                          {getFilteredProducts(productSearch[index]).length === 0 ? (
                            <div className="p-3 text-sm text-gray-500">No products found matching "{productSearch[index]}"</div>
                          ) : (
                            getFilteredProducts(productSearch[index]).slice(0, 10).map(product => (
                              <div
                                key={product.id}
                                onClick={() => {
                                  handleProductSelect(index, product.id);
                                  setProductSearch({ ...productSearch, [index]: '' });
                                }}
                                className="p-3 hover:bg-teal-50 cursor-pointer border-b last:border-b-0"
                              >
                                <div className="font-medium text-gray-900 text-sm">{product.name}</div>
                                <div className="text-xs text-gray-500 flex gap-2 mt-1">
                                  <span className="bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">{product.brand}</span>
                                  {product.model_number && <span className="bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">{product.model_number}</span>}
                                  <span className={`px-1.5 py-0.5 rounded ${(product.stock_quantity ?? product.current_stock ?? 0) > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                    Stock: {product.stock_quantity ?? product.current_stock ?? 0}
                                  </span>
                                </div>
                              </div>
                            ))
                          )}
                        </div>
                      )}
                    </div>
                    <select
                      value={item.product_id || ''}
                      onChange={(e) => { if (e.target.value) handleProductSelect(index, e.target.value); }}
                      className="w-40 px-2 py-2 border rounded-lg text-sm bg-white"
                    >
                      <option value="">All Products ▼</option>
                      {products.map(product => (
                        <option key={product.id} value={product.id}>
                          {product.model_number || product.name?.substring(0, 30)}
                        </option>
                      ))}
                    </select>
                    <button
                      type="button"
                      onClick={() => openAddProductModal(index)}
                      className="px-2 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 flex items-center gap-1 whitespace-nowrap"
                      title="Add new product to inventory"
                    >
                      <Package className="w-4 h-4" />
                      + New
                    </button>
                    <button
                      type="button"
                      onClick={() => removeItem(index)}
                      className="p-2 text-red-500 hover:bg-red-50 rounded-lg"
                      disabled={items.length === 1}
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  {item.product_name && (
                    <div className="text-xs text-teal-700 bg-teal-50 rounded px-2 py-1">
                      Selected: {item.product_name} {item.model_number && `(${item.model_number})`}
                    </div>
                  )}
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={item.model_number}
                      onChange={(e) => updateItem(index, 'model_number', e.target.value)}
                      placeholder="Model Number / SKU"
                      className="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                      required
                    />
                    <input
                      type="number"
                      value={item.quantity}
                      onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value) || 1)}
                      placeholder="Qty"
                      min="1"
                      className="w-24 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                      required
                    />
                    <input
                      type="text"
                      value={item.notes}
                      onChange={(e) => updateItem(index, 'notes', e.target.value)}
                      placeholder="Notes (optional)"
                      className="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                    />
                  </div>
                </div>
              ))}'''

assert old_row in content, "ITEM ROW anchor not found"
content = content.replace(old_row, new_row, 1)

with open(TARGET, "w") as f:
    f.write(content)

print("Patched", TARGET, "- step 2 of 3 (item row picker UI)")
