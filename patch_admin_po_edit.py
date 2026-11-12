#!/usr/bin/env python3
import shutil

TARGET = "frontend/src/components/AdminPORequestsView.js"
with open(TARGET, "r") as f:
    content = f.read()
shutil.copy(TARGET, TARGET + ".bak_search_edit1")

# --- 1. Replace state/handlers block: fix stale-closure bug + add product-picker state ---
old_state = """const EditPORequestModal = ({ request, onClose, onSuccess }) => {
  const [items, setItems] = useState(
    (request.items || []).map(i => ({
      model_number: i.model_number || '',
      product_name: i.product_name || '',
      sku: i.sku || '',
      product_id: i.product_id || '',
      quantity: i.quantity || 1,
      cost_price: i.cost_price || i.unit_price || 0,
      notes: i.notes || ''
    }))
  );
  const [supplierName, setSupplierName] = useState(request.supplier_name || request.vendor_name || '');
  const [urgency, setUrgency] = useState(request.urgency || 'normal');
  const [notes, setNotes] = useState(request.notes || '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const updateItem = (index, field, value) => {
    const next = [...items];
    next[index][field] = value;
    setItems(next);
  };

  const addItem = () => {
    setItems([...items, { model_number: '', product_name: '', sku: '', product_id: '', quantity: 1, cost_price: 0, notes: '' }]);
  };

  const removeItem = (index) => {
    if (items.length > 1) setItems(items.filter((_, i) => i !== index));
  };"""

new_state = """const EditPORequestModal = ({ request, onClose, onSuccess }) => {
  const [items, setItems] = useState(
    (request.items || []).map(i => ({
      model_number: i.model_number || '',
      product_name: i.product_name || '',
      sku: i.sku || '',
      product_id: i.product_id || '',
      quantity: i.quantity || 1,
      cost_price: i.cost_price || i.unit_price || 0,
      notes: i.notes || ''
    }))
  );
  const [supplierName, setSupplierName] = useState(request.supplier_name || request.vendor_name || '');
  const [urgency, setUrgency] = useState(request.urgency || 'normal');
  const [notes, setNotes] = useState(request.notes || '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const [products, setProducts] = useState([]);
  const [hsnCodes, setHsnCodes] = useState([]);
  const [productSearch, setProductSearch] = useState({});
  const [showAddProductModal, setShowAddProductModal] = useState(false);
  const [addProductForIndex, setAddProductForIndex] = useState(null);
  const [newProduct, setNewProduct] = useState({
    name: '',
    brand: '',
    model_number: '',
    price: 0,
    hsn_code: '',
    category: '',
    description: '',
    current_stock: 0
  });
  const [addProductLoading, setAddProductLoading] = useState(false);
  const [newProductHsnSuggestions, setNewProductHsnSuggestions] = useState([]);
  const [manualHsnMode, setManualHsnMode] = useState(false);
  const [manualHsnGstRate, setManualHsnGstRate] = useState(18);

  useEffect(() => {
    fetchProducts();
    fetchHSNCodes();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/products?limit=1000`);
      const data = await response.json();
      if (data.status === 'success') {
        setProducts(data.products);
      }
    } catch (err) {
      console.error('Failed to fetch products');
    }
  };

  const fetchHSNCodes = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/hsn/?active_only=true`);
      const data = await response.json();
      setHsnCodes(data);
    } catch (err) {
      console.error('Failed to fetch HSN codes');
    }
  };

  const getFilteredProducts = (searchTerm) => {
    if (!searchTerm) return products;
    const term = searchTerm.toLowerCase();
    return products.filter(p =>
      p.name.toLowerCase().includes(term) ||
      p.brand?.toLowerCase().includes(term) ||
      p.model_number?.toLowerCase().includes(term)
    );
  };

  const updateItem = (index, field, value) => {
    setItems(prev => {
      const next = [...prev];
      next[index] = { ...next[index], [field]: value };
      return next;
    });
  };

  const handleProductSelect = (index, productId) => {
    const product = products.find(p => p.id === productId);
    if (product) {
      setItems(prev => {
        const next = [...prev];
        next[index] = {
          ...next[index],
          product_id: product.id,
          product_name: product.name,
          model_number: product.model_number || product.sku || next[index].model_number,
          cost_price: product.price ?? next[index].cost_price
        };
        return next;
      });
    }
  };

  const fetchNewProductHsnSuggestion = async (productName) => {
    if (!productName || productName.length < 2) {
      setNewProductHsnSuggestions([]);
      return;
    }
    try {
      const response = await fetch(`${BACKEND_URL}/api/hsn/suggest?product_name=${encodeURIComponent(productName)}`);
      const data = await response.json();
      if (data.suggestions && data.suggestions.length > 0) {
        setNewProductHsnSuggestions(data.suggestions);
        if (!newProduct.hsn_code && data.suggestions[0].match_score >= 50) {
          setNewProduct(prev => ({ ...prev, hsn_code: data.suggestions[0].code }));
        }
      } else {
        setNewProductHsnSuggestions([]);
      }
    } catch (err) {
      console.error('Error fetching HSN suggestions:', err);
    }
  };

  const openAddProductModal = (index) => {
    setAddProductForIndex(index);
    setNewProduct({
      name: '',
      brand: '',
      model_number: '',
      price: 0,
      hsn_code: '',
      category: '',
      description: '',
      current_stock: 0
    });
    setManualHsnMode(false);
    setManualHsnGstRate(18);
    setNewProductHsnSuggestions([]);
    setShowAddProductModal(true);
  };

  const handleCreateProduct = async () => {
    if (!newProduct.name || !newProduct.price || !newProduct.hsn_code) {
      setError('Please fill in product name, price, and HSN code');
      return;
    }

    setAddProductLoading(true);
    try {
      let gstRate = 18.0;
      const existingHsn = hsnCodes.find(h => h.code === newProduct.hsn_code);

      if (manualHsnMode && !existingHsn) {
        try {
          const hsnResponse = await fetch(`${BACKEND_URL}/api/hsn/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              code: newProduct.hsn_code,
              description: `HSN ${newProduct.hsn_code} - ${newProduct.category || newProduct.name}`,
              gst_rate: manualHsnGstRate,
              category: newProduct.category || 'Uncategorized',
              is_active: true
            })
          });
          if (hsnResponse.ok) {
            await fetchHSNCodes();
            gstRate = manualHsnGstRate;
          }
        } catch (hsnError) {
          console.log('HSN code might already exist or failed to save:', hsnError);
        }
        gstRate = manualHsnGstRate;
      } else if (existingHsn) {
        gstRate = existingHsn.gst_rate || 18.0;
      }

      const response = await fetch(`${BACKEND_URL}/api/products`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newProduct,
          id: `PROD-${Date.now()}`,
          price: parseFloat(newProduct.price),
          current_stock: parseInt(newProduct.current_stock) || 0
        })
      });

      const data = await response.json();

      if (response.ok) {
        await fetchProducts();

        if (addProductForIndex !== null) {
          setItems(prev => {
            const next = [...prev];
            next[addProductForIndex] = {
              ...next[addProductForIndex],
              product_id: data.product?.id || data.id,
              product_name: newProduct.name,
              model_number: newProduct.model_number || next[addProductForIndex].model_number,
              cost_price: parseFloat(newProduct.price) || next[addProductForIndex].cost_price
            };
            return next;
          });
        }
        setShowAddProductModal(false);
        setAddProductForIndex(null);
      } else {
        setError(data.detail || 'Failed to add product');
      }
    } catch (err) {
      setError('Connection error: ' + err.message);
    } finally {
      setAddProductLoading(false);
    }
  };

  const addItem = () => {
    setItems(prev => [...prev, { model_number: '', product_name: '', sku: '', product_id: '', quantity: 1, cost_price: 0, notes: '' }]);
  };

  const removeItem = (index) => {
    setItems(prev => (prev.length > 1 ? prev.filter((_, i) => i !== index) : prev));
  };"""

assert content.count(old_state) == 1, "EDIT STATE anchor not found or not unique"
content = content.replace(old_state, new_state, 1)

# --- 2. Replace the Items table with the search/select/+New picker per row ---
old_items_jsx = """          <div>
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
            </div>
            <button type="button" onClick={addItem} className="mt-2 text-sm text-blue-600 hover:text-blue-700">
              + Add Item
            </button>
            <p className="mt-2 text-sm font-medium text-gray-700">Estimated total: ₹{total.toLocaleString()}</p>
          </div>"""

new_items_jsx = """          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Items</label>
            <div className="space-y-3">
              {items.map((item, idx) => (
                <div key={idx} className="border rounded-lg p-3 space-y-2">
                  <div className="flex gap-2 items-start">
                    <div className="flex-1 relative">
                      <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="text"
                        value={productSearch[idx] || ''}
                        onChange={(e) => setProductSearch({ ...productSearch, [idx]: e.target.value })}
                        placeholder="Type model no, brand or product name to search..."
                        className="w-full pl-8 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                      />
                      {productSearch[idx] && productSearch[idx].length > 1 && (
                        <div className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg max-h-60 overflow-y-auto">
                          {getFilteredProducts(productSearch[idx]).length === 0 ? (
                            <div className="p-3 text-sm text-gray-500">No products found matching "{productSearch[idx]}"</div>
                          ) : (
                            getFilteredProducts(productSearch[idx]).slice(0, 10).map(product => (
                              <div
                                key={product.id}
                                onClick={() => {
                                  handleProductSelect(idx, product.id);
                                  setProductSearch({ ...productSearch, [idx]: '' });
                                }}
                                className="p-3 hover:bg-blue-50 cursor-pointer border-b last:border-b-0"
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
                      onChange={(e) => { if (e.target.value) handleProductSelect(idx, e.target.value); }}
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
                      onClick={() => openAddProductModal(idx)}
                      className="px-2 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 flex items-center gap-1 whitespace-nowrap"
                      title="Add new product to inventory"
                    >
                      <Package className="w-4 h-4" />
                      + New
                    </button>
                    <button
                      type="button"
                      onClick={() => removeItem(idx)}
                      className="p-2 text-red-500 hover:bg-red-50 rounded-lg"
                      disabled={items.length === 1}
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="grid grid-cols-12 gap-2 items-center">
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
                    <span className="col-span-2 text-xs text-gray-600 text-right">
                      ₹{((parseFloat(item.quantity) || 0) * (parseFloat(item.cost_price) || 0)).toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <button type="button" onClick={addItem} className="mt-2 text-sm text-blue-600 hover:text-blue-700">
              + Add Item
            </button>
            <p className="mt-2 text-sm font-medium text-gray-700">Estimated total: ₹{total.toLocaleString()}</p>
          </div>"""

assert content.count(old_items_jsx) == 1, "EDIT ITEMS JSX anchor not found or not unique"
content = content.replace(old_items_jsx, new_items_jsx, 1)

# --- 3. Wrap the Edit modal's return in a Fragment ---
old_open = """  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <div className="p-4 border-b bg-blue-600 text-white flex items-center justify-between">
          <h3 className="text-lg font-bold">Edit PO Request</h3>"""
new_open = """  return (
    <>
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <div className="p-4 border-b bg-blue-600 text-white flex items-center justify-between">
          <h3 className="text-lg font-bold">Edit PO Request</h3>"""
assert content.count(old_open) == 1, "EDIT OPEN anchor not found or not unique"
content = content.replace(old_open, new_open, 1)

# --- 4. Close Fragment and append the Add Product modal ---
old_close = """        <div className="p-4 border-t bg-gray-50 flex justify-end gap-2">
          <button onClick={onClose} className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300" disabled={saving}>
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
};

const AdminCreatePORequestModal = ({ stores, onClose, onSuccess }) => {"""

new_close = """        <div className="p-4 border-t bg-gray-50 flex justify-end gap-2">
          <button onClick={onClose} className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300" disabled={saving}>
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
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
};

const AdminCreatePORequestModal = ({ stores, onClose, onSuccess }) => {"""

assert content.count(old_close) == 1, "EDIT CLOSE anchor not found or not unique"
content = content.replace(old_close, new_close, 1)

with open(TARGET, "w") as f:
    f.write(content)

print("Patched", TARGET, "- Edit PO Request modal: fixed live price/total bug + added product search/select/+New picker")
