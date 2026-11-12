import React, { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Link2, Unlink, Package, CheckCircle, AlertCircle, Plus, Search,
  RefreshCw, Zap, ArrowRight, X, Filter, ChevronDown, ChevronUp,
  FileText, Tag, Boxes
} from 'lucide-react';
import { showToast } from '../utils/toast';


const StockReconciliation = () => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [autoLinking, setAutoLinking] = useState(false);
  const [activeTab, setActiveTab] = useState('linkable');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showLinkModal, setShowLinkModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [productSearch, setProductSearch] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [categories, setCategories] = useState([]);
  const [expandedGroups, setExpandedGroups] = useState({});

  // Form for adding new product
  const [newProduct, setNewProduct] = useState({
    item_name: '',
    model_number: '',
    hsn_code: '',
    category: 'uncategorized',
    brand: '',
    purchase_price: 0,
    selling_price: 0,
    item_type: 'product'
  });

  const fetchAnalysis = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/stock-reconciliation/analysis`);
      const data = await response.json();
      if (data.status === 'success') {
        setAnalysis(data);
      }
    } catch (error) {
      console.error('Failed to fetch analysis:', error);
      showToast.error('Failed to load reconciliation data');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/stock-reconciliation/categories`);
      const data = await response.json();
      if (data.status === 'success') {
        setCategories(data.categories);
      }
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  useEffect(() => {
    fetchAnalysis();
    fetchCategories();
  }, [fetchAnalysis]);

  const handleAutoLink = async (dryRun = true) => {
    setAutoLinking(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/stock-reconciliation/auto-link`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dry_run: dryRun })
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        if (dryRun) {
          showToast.success(`Found ${data.links.length} items that can be auto-linked`);
        } else {
          showToast.success(`Successfully linked ${data.links.length} items!`);
          fetchAnalysis();
        }
      }
    } catch (error) {
      showToast.error('Auto-link failed');
    } finally {
      setAutoLinking(false);
    }
  };

  const handleManualLink = async (productId) => {
    if (!selectedItem) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/stock-reconciliation/link-item`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          purchase_bill_id: selectedItem.bill_id,
          item_index: selectedItem.item_index,
          product_id: productId
        })
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        showToast.success(data.message);
        setShowLinkModal(false);
        setSelectedItem(null);
        fetchAnalysis();
      } else {
        showToast.error(data.detail || 'Link failed');
      }
    } catch (error) {
      showToast.error('Failed to link item');
    }
  };

  const handleAddToCatalog = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/stock-reconciliation/add-to-catalog`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newProduct)
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        showToast.success(data.message);
        setShowAddModal(false);
        setNewProduct({
          item_name: '',
          model_number: '',
          hsn_code: '',
          category: 'uncategorized',
          brand: '',
          purchase_price: 0,
          selling_price: 0,
          item_type: 'product'
        });
        fetchAnalysis();
      } else {
        showToast.error(data.detail || 'Failed to add product');
      }
    } catch (error) {
      showToast.error('Failed to add to catalog');
    }
  };

  const searchProducts = async (query) => {
    if (!query || query.length < 2) {
      setSearchResults([]);
      return;
    }
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/stock-reconciliation/products/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      if (data.status === 'success') {
        setSearchResults(data.products);
      }
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const openAddModal = (item) => {
    setNewProduct({
      item_name: item.item_name || item.name,
      model_number: item.item_name || '',
      hsn_code: item.hsn_code || '',
      category: 'uncategorized',
      brand: '',
      purchase_price: item.rate || 0,
      selling_price: (item.rate || 0) * 1.2,
      item_type: 'product'
    });
    setShowAddModal(true);
  };

  const openLinkModal = (item) => {
    setSelectedItem(item);
    setProductSearch('');
    setSearchResults([]);
    setShowLinkModal(true);
  };

  const toggleGroup = (groupKey) => {
    setExpandedGroups(prev => ({
      ...prev,
      [groupKey]: !prev[groupKey]
    }));
  };

  if (loading) {
    return (
      <div className="p-6 bg-gray-50 min-h-screen">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-64 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-96 mb-8"></div>
          <div className="grid grid-cols-4 gap-4 mb-8">
            {[1,2,3,4].map(i => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const summary = analysis?.summary || {};

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Link2 className="text-blue-500" />
              Stock Reconciliation
            </h1>
            <p className="text-gray-600 mt-1">Match purchase bill items with product catalog</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={fetchAnalysis}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <RefreshCw size={18} />
              Refresh
            </button>
            <button
              onClick={() => handleAutoLink(false)}
              disabled={autoLinking || summary.can_auto_link === 0}
              className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 flex items-center gap-2 disabled:opacity-50 shadow-lg"
              data-testid="auto-link-btn"
            >
              <Zap size={18} />
              {autoLinking ? 'Linking...' : `Auto-Link ${summary.can_auto_link || 0} Items`}
            </button>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <FileText className="text-blue-600" size={20} />
              </div>
              <div>
                <p className="text-xs text-gray-500">Purchase Bills</p>
                <p className="text-xl font-bold text-gray-900">{summary.total_bills || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Package className="text-purple-600" size={20} />
              </div>
              <div>
                <p className="text-xs text-gray-500">Products</p>
                <p className="text-xl font-bold text-gray-900">{summary.total_products || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="text-green-600" size={20} />
              </div>
              <div>
                <p className="text-xs text-gray-500">Already Linked</p>
                <p className="text-xl font-bold text-green-600">{summary.already_linked || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Link2 className="text-blue-600" size={20} />
              </div>
              <div>
                <p className="text-xs text-gray-500">Can Auto-Link</p>
                <p className="text-xl font-bold text-blue-600">{summary.can_auto_link || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertCircle className="text-red-600" size={20} />
              </div>
              <div>
                <p className="text-xs text-gray-500">Unmatched</p>
                <p className="text-xl font-bold text-red-600">{summary.unique_unmatched || 0}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('linkable')}
                className={`px-6 py-4 text-sm font-medium border-b-2 ${
                  activeTab === 'linkable' 
                    ? 'border-blue-500 text-blue-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Link2 size={16} className="inline mr-2" />
                Can Auto-Link ({summary.can_auto_link || 0})
              </button>
              <button
                onClick={() => setActiveTab('unmatched')}
                className={`px-6 py-4 text-sm font-medium border-b-2 ${
                  activeTab === 'unmatched' 
                    ? 'border-red-500 text-red-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <AlertCircle size={16} className="inline mr-2" />
                Unmatched ({summary.unique_unmatched || 0})
              </button>
              <button
                onClick={() => setActiveTab('matched')}
                className={`px-6 py-4 text-sm font-medium border-b-2 ${
                  activeTab === 'matched' 
                    ? 'border-green-500 text-green-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <CheckCircle size={16} className="inline mr-2" />
                Linked ({summary.already_linked || 0})
              </button>
            </nav>
          </div>

          <div className="p-4">
            {/* Linkable Items Tab */}
            {activeTab === 'linkable' && (
              <div>
                {analysis?.linkable_items?.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <Link2 size={48} className="mx-auto mb-4 opacity-50" />
                    <p>No items to auto-link. All matching items are already linked!</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {analysis?.linkable_items?.map((item, idx) => (
                      <div key={idx} className="flex items-center justify-between p-4 bg-blue-50 rounded-lg border border-blue-200">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-gray-900">{item.item_name}</span>
                            <ArrowRight size={16} className="text-blue-500" />
                            <span className="text-blue-600 font-medium">{item.suggested_product_name}</span>
                          </div>
                          <div className="text-sm text-gray-500 mt-1">
                            Bill: {item.bill_number} | Match: {item.match_type} | Qty: {item.quantity} × ₹{item.rate}
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => openLinkModal(item)}
                            className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100"
                          >
                            Change
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Unmatched Items Tab */}
            {activeTab === 'unmatched' && (
              <div>
                <div className="mb-4 text-sm text-gray-600">
                  <p>These items don't match any product in your catalog. You can:</p>
                  <ul className="list-disc ml-5 mt-1">
                    <li>Add them as new products</li>
                    <li>Manually link them to existing products</li>
                    <li>Mark them as parts/consumables</li>
                  </ul>
                </div>
                
                {analysis?.frequent_unmatched?.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <CheckCircle size={48} className="mx-auto mb-4 opacity-50 text-green-500" />
                    <p>All items are matched! Great job.</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {analysis?.frequent_unmatched?.map((item, idx) => (
                      <div key={idx} className="flex items-center justify-between p-4 bg-amber-50 rounded-lg border border-amber-200">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-gray-900">{item.name}</span>
                            <span className="text-xs bg-amber-200 text-amber-800 px-2 py-0.5 rounded">
                              {item.count}x in bills
                            </span>
                          </div>
                          <div className="text-sm text-gray-500 mt-1">
                            Total Qty: {item.total_qty} | Total Value: ₹{item.total_value?.toLocaleString()}
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => openLinkModal({ item_name: item.name, bill_id: null })}
                            className="px-3 py-1 text-sm border border-blue-300 text-blue-600 rounded hover:bg-blue-50"
                          >
                            <Link2 size={14} className="inline mr-1" />
                            Link
                          </button>
                          <button
                            onClick={() => openAddModal(item)}
                            className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                          >
                            <Plus size={14} className="inline mr-1" />
                            Add to Catalog
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Matched Items Tab */}
            {activeTab === 'matched' && (
              <div>
                {analysis?.matched_items?.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <Unlink size={48} className="mx-auto mb-4 opacity-50" />
                    <p>No items linked yet. Use Auto-Link to get started!</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {analysis?.matched_items?.map((item, idx) => (
                      <div key={idx} className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <CheckCircle size={16} className="text-green-500" />
                            <span className="font-medium text-gray-900">{item.item_name}</span>
                            <ArrowRight size={16} className="text-green-500" />
                            <span className="text-green-600 font-medium">{item.linked_product_name}</span>
                          </div>
                          <div className="text-sm text-gray-500 mt-1">
                            Bill: {item.bill_number} | Qty: {item.quantity} × ₹{item.rate}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add to Catalog Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold">Add to Product Catalog</h2>
                <button onClick={() => setShowAddModal(false)} className="text-gray-500 hover:text-gray-700">
                  <X size={24} />
                </button>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Product Name *</label>
                <input
                  type="text"
                  value={newProduct.item_name}
                  onChange={(e) => setNewProduct({ ...newProduct, item_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Model Number</label>
                  <input
                    type="text"
                    value={newProduct.model_number}
                    onChange={(e) => setNewProduct({ ...newProduct, model_number: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">HSN Code</label>
                  <input
                    type="text"
                    value={newProduct.hsn_code}
                    onChange={(e) => setNewProduct({ ...newProduct, hsn_code: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select
                    value={newProduct.category}
                    onChange={(e) => setNewProduct({ ...newProduct, category: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="uncategorized">Uncategorized</option>
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Brand</label>
                  <input
                    type="text"
                    value={newProduct.brand}
                    onChange={(e) => setNewProduct({ ...newProduct, brand: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="e.g., Bosch, Siemens"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Purchase Price</label>
                  <input
                    type="number"
                    value={newProduct.purchase_price}
                    onChange={(e) => setNewProduct({ ...newProduct, purchase_price: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Selling Price</label>
                  <input
                    type="number"
                    value={newProduct.selling_price}
                    onChange={(e) => setNewProduct({ ...newProduct, selling_price: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Item Type</label>
                <div className="flex gap-4">
                  {['product', 'part', 'consumable'].map(type => (
                    <label key={type} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="item_type"
                        value={type}
                        checked={newProduct.item_type === type}
                        onChange={(e) => setNewProduct({ ...newProduct, item_type: e.target.value })}
                        className="text-blue-600"
                      />
                      <span className="capitalize">{type}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
            <div className="p-6 border-t bg-gray-50 flex justify-end gap-2">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                onClick={handleAddToCatalog}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Add to Catalog
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Manual Link Modal */}
      {showLinkModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold">Link to Product</h2>
                <button onClick={() => setShowLinkModal(false)} className="text-gray-500 hover:text-gray-700">
                  <X size={24} />
                </button>
              </div>
              {selectedItem && (
                <p className="text-sm text-gray-600 mt-2">
                  Linking: <span className="font-medium">{selectedItem.item_name}</span>
                </p>
              )}
            </div>
            <div className="p-6">
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Search Products</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                  <input
                    type="text"
                    value={productSearch}
                    onChange={(e) => {
                      setProductSearch(e.target.value);
                      searchProducts(e.target.value);
                    }}
                    placeholder="Search by name, model, or brand..."
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              
              <div className="max-h-64 overflow-y-auto border border-gray-200 rounded-lg">
                {searchResults.length === 0 ? (
                  <div className="p-4 text-center text-gray-500">
                    {productSearch.length < 2 ? 'Type at least 2 characters to search' : 'No products found'}
                  </div>
                ) : (
                  searchResults.map(product => (
                    <div
                      key={product.id}
                      onClick={() => handleManualLink(product.id)}
                      className="p-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                    >
                      <div className="font-medium text-gray-900">{product.name}</div>
                      <div className="text-sm text-gray-500">
                        Model: {product.model_number} | Brand: {product.brand}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
            <div className="p-6 border-t bg-gray-50 flex justify-end">
              <button
                onClick={() => setShowLinkModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockReconciliation;
