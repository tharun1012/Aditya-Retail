#!/usr/bin/env python3
import shutil

TARGET = "frontend/src/components/PORequestsTab.js"
with open(TARGET, "r") as f:
    content = f.read()
shutil.copy(TARGET, TARGET + ".bak_search3")

# --- Wrap outer return in a Fragment ---
old_open = '''  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-800">Create PO Request</h2>
            <p className="text-sm text-gray-500">Request stock from procurement</p>'''
new_open = '''  return (
    <>
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-800">Create PO Request</h2>
            <p className="text-sm text-gray-500">Request stock from procurement</p>'''
assert old_open in content, "OPEN anchor not found"
content = content.replace(old_open, new_open, 1)

# --- Close Fragment and append Add Product modal, right before this component's closing ---
old_close = '''              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                'Submit Request'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};'''

new_close = '''              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                'Submit Request'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>

    {showAddProductModal && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-4">
        <div className="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
          <div className="bg-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Package className="w-5 h-5" />
              Add New Product
            </h3>
            <button
              type="button"
              onClick={() => setShowAddProductModal(false)}
              className="text-white hover:bg-blue-700 p-1 rounded"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Product Name *</label>
              <input
                type="text"
                value={newProduct.name}
                onChange={(e) => {
                  setNewProduct({ ...newProduct, name: e.target.value });
                  fetchNewProductHsnSuggestion(e.target.value);
                }}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Bosch Built-in Oven 60cm"
                required
              />
              {newProductHsnSuggestions.length > 0 && (
                <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded">
                  <div className="text-xs font-medium text-blue-800 mb-1">
                    Suggested HSN Codes based on product name:
                  </div>
                  <div className="space-y-1">
                    {newProductHsnSuggestions.slice(0, 3).map((suggestion, sIdx) => (
                      <button
                        key={sIdx}
                        type="button"
                        onClick={() => {
                          setNewProduct({ ...newProduct, hsn_code: suggestion.code });
                          setNewProductHsnSuggestions([]);
                        }}
                        className={`w-full text-left px-2 py-1 rounded text-xs hover:bg-blue-100 transition-colors ${
                          newProduct.hsn_code === suggestion.code ? 'bg-blue-200 border border-blue-400' : 'bg-white'
                        }`}
                      >
                        <span className="font-semibold text-blue-700">{suggestion.code}</span>
                        <span className="text-gray-600 ml-2">{suggestion.category || suggestion.description?.substring(0, 30)}</span>
                        <span className="text-green-600 ml-2 font-medium">{suggestion.gst_rate}% GST</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Brand</label>
                <input
                  type="text"
                  value={newProduct.brand}
                  onChange={(e) => setNewProduct({ ...newProduct, brand: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Bosch, Siemens"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Model Number</label>
                <input
                  type="text"
                  value={newProduct.model_number}
                  onChange={(e) => setNewProduct({ ...newProduct, model_number: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., HBA534BS0"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Selling Price (₹) *</label>
                <input
                  type="number"
                  value={newProduct.price}
                  onChange={(e) => setNewProduct({ ...newProduct, price: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Price incl. GST"
                  required
                  step="0.01"
                  min="0"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Opening Stock</label>
                <input
                  type="number"
                  value={newProduct.current_stock}
                  onChange={(e) => setNewProduct({ ...newProduct, current_stock: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Initial stock quantity"
                  min="0"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-sm font-medium text-gray-700">HSN Code *</label>
                <button
                  type="button"
                  onClick={() => {
                    setManualHsnMode(!manualHsnMode);
                    if (!manualHsnMode) {
                      setNewProduct({ ...newProduct, hsn_code: '' });
                    }
                  }}
                  className="text-xs text-blue-600 hover:text-blue-800 underline"
                >
                  {manualHsnMode ? 'Select from list' : 'Enter manually'}
                </button>
              </div>

              {manualHsnMode ? (
                <div className="space-y-2">
                  <input
                    type="text"
                    value={newProduct.hsn_code}
                    onChange={(e) => setNewProduct({ ...newProduct, hsn_code: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter HSN code (e.g., 85081100)"
                    required
                    maxLength={8}
                  />
                  <div className="flex items-center gap-2">
                    <label className="text-xs text-gray-600">GST Rate:</label>
                    <select
                      value={manualHsnGstRate}
                      onChange={(e) => setManualHsnGstRate(parseFloat(e.target.value))}
                      className="px-2 py-1 border rounded text-sm"
                    >
                      <option value={0}>0%</option>
                      <option value={5}>5%</option>
                      <option value={12}>12%</option>
                      <option value={18}>18%</option>
                      <option value={28}>28%</option>
                    </select>
                  </div>
                  <p className="text-xs text-amber-600">
                    Note: Manually entered HSN codes will be added to the system
                  </p>
                </div>
              ) : (
                <>
                  <select
                    value={newProduct.hsn_code}
                    onChange={(e) => setNewProduct({ ...newProduct, hsn_code: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">-- Select HSN Code --</option>
                    {hsnCodes.map(hsn => (
                      <option key={hsn.id || hsn.code} value={hsn.code}>
                        {hsn.code} - {hsn.description?.substring(0, 40)}{hsn.description?.length > 40 ? '...' : ''} ({hsn.gst_rate}%)
                      </option>
                    ))}
                  </select>
                  {newProduct.hsn_code && (
                    <p className="text-xs text-gray-500 mt-1">
                      GST Rate: {hsnCodes.find(h => h.code === newProduct.hsn_code)?.gst_rate || 18}%
                    </p>
                  )}
                </>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <input
                type="text"
                value={newProduct.category}
                onChange={(e) => setNewProduct({ ...newProduct, category: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Built-in Ovens, Refrigerators"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={newProduct.description}
                onChange={(e) => setNewProduct({ ...newProduct, description: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                rows="2"
                placeholder="Brief product description"
              ></textarea>
            </div>

            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={() => setShowAddProductModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleCreateProduct}
                disabled={addProductLoading}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center justify-center gap-2"
              >
                {addProductLoading ? 'Saving...' : 'Add Product'}
              </button>
            </div>
          </div>
        </div>
      </div>
    )}
    </>
  );
};'''

assert old_close in content, "CLOSE anchor not found"
content = content.replace(old_close, new_close, 1)

with open(TARGET, "w") as f:
    f.write(content)

print("Patched", TARGET, "- step 3 of 3 (Add Product modal appended)")
