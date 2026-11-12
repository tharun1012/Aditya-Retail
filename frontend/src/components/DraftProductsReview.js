import React, { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Package, Eye, Trash2, Upload, CheckCircle, AlertCircle, 
  Image as ImageIcon, Edit, RefreshCw, Filter, Search,
  FileText, Wrench, ShoppingBag, X, Check, ChevronDown
} from 'lucide-react';
import { showToast } from '../utils/toast';


const DraftProductsReview = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [typeFilter, setTypeFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [uploading, setUploading] = useState(false);

  const fetchProducts = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({ page: currentPage, limit: 20 });
      if (typeFilter !== 'all') params.append('item_type', typeFilter);
      
      const response = await fetch(`${BACKEND_URL}/api/draft-products/?${params}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setProducts(data.products);
        setTotalPages(data.pages);
      }
    } catch (error) {
      console.error('Failed to fetch products:', error);
      showToast.error('Failed to load draft products');
    } finally {
      setLoading(false);
    }
  }, [currentPage, typeFilter]);

  const fetchSummary = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/draft-products/summary`);
      const data = await response.json();
      if (data.status === 'success') {
        setSummary(data.summary);
      }
    } catch (error) {
      console.error('Failed to fetch summary:', error);
    }
  };

  useEffect(() => {
    fetchProducts();
    fetchSummary();
  }, [fetchProducts]);

  const handlePublish = async (productId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/draft-products/${productId}/publish`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success(data.message);
        fetchProducts();
        fetchSummary();
      } else {
        showToast.error(data.detail || 'Failed to publish');
      }
    } catch (error) {
      showToast.error('Failed to publish product');
    }
  };

  const handleBulkPublish = async () => {
    if (selectedProducts.length === 0) {
      showToast.error('Select products to publish');
      return;
    }
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/draft-products/bulk-publish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(selectedProducts)
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success(data.message);
        if (data.failed?.length > 0) {
          showToast.warning(`${data.failed.length} products couldn't be published (missing images)`);
        }
        setSelectedProducts([]);
        fetchProducts();
        fetchSummary();
      }
    } catch (error) {
      showToast.error('Bulk publish failed');
    }
  };

  const handleDelete = async (productId) => {
    if (!window.confirm('Delete this draft product?')) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/draft-products/${productId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        showToast.success('Draft deleted');
        fetchProducts();
        fetchSummary();
      }
    } catch (error) {
      showToast.error('Failed to delete');
    }
  };

  const handleImageUpload = async (productId, file) => {
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/draft-products/${productId}/upload-image`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success('Image uploaded!');
        fetchProducts();
        fetchSummary();
      } else {
        showToast.error(data.detail || 'Upload failed');
      }
    } catch (error) {
      showToast.error('Failed to upload image');
    } finally {
      setUploading(false);
    }
  };

  const handleUpdateProduct = async () => {
    if (!editingProduct) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/draft-products/${editingProduct.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: editingProduct.name,
          description: editingProduct.description,
          category: editingProduct.category,
          brand: editingProduct.brand,
          price: editingProduct.price,
          mrp: editingProduct.mrp,
          item_type: editingProduct.item_type
        })
      });
      
      if (response.ok) {
        showToast.success('Product updated');
        setShowEditModal(false);
        setEditingProduct(null);
        fetchProducts();
      }
    } catch (error) {
      showToast.error('Failed to update');
    }
  };

  const toggleSelectAll = () => {
    if (selectedProducts.length === products.length) {
      setSelectedProducts([]);
    } else {
      setSelectedProducts(products.map(p => p.id));
    }
  };

  const toggleSelect = (productId) => {
    setSelectedProducts(prev => 
      prev.includes(productId) 
        ? prev.filter(id => id !== productId)
        : [...prev, productId]
    );
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'product': return <ShoppingBag size={16} className="text-blue-500" />;
      case 'part': return <Wrench size={16} className="text-orange-500" />;
      case 'consumable': return <Package size={16} className="text-green-500" />;
      default: return <Package size={16} className="text-gray-500" />;
    }
  };

  const getTypeLabel = (type) => {
    const labels = {
      product: 'Product (Website)',
      part: 'Part (Backend)',
      consumable: 'Consumable'
    };
    return labels[type] || type;
  };

  const filteredProducts = products.filter(p => 
    p.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.model_number?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <FileText className="text-purple-500" />
              Draft Products Review
            </h1>
            <p className="text-gray-600 mt-1">Review and publish products from purchase bills</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => { fetchProducts(); fetchSummary(); }}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <RefreshCw size={18} />
              Refresh
            </button>
            {selectedProducts.length > 0 && (
              <button
                onClick={handleBulkPublish}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
              >
                <CheckCircle size={18} />
                Publish {selectedProducts.length} Selected
              </button>
            )}
          </div>
        </div>

        {/* Summary Stats */}
        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <FileText className="text-purple-600" size={20} />
                </div>
                <div>
                  <p className="text-xs text-gray-500">Total Drafts</p>
                  <p className="text-xl font-bold text-gray-900">{summary.total_drafts}</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-red-100 rounded-lg">
                  <ImageIcon className="text-red-600" size={20} />
                </div>
                <div>
                  <p className="text-xs text-gray-500">Missing Images</p>
                  <p className="text-xl font-bold text-red-600">{summary.missing_images}</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <CheckCircle className="text-green-600" size={20} />
                </div>
                <div>
                  <p className="text-xs text-gray-500">Ready to Publish</p>
                  <p className="text-xl font-bold text-green-600">{summary.ready_to_publish}</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <ShoppingBag className="text-blue-600" size={20} />
                </div>
                <div>
                  <p className="text-xs text-gray-500">Products</p>
                  <p className="text-xl font-bold text-blue-600">{summary.by_type?.products || 0}</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <Wrench className="text-orange-600" size={20} />
                </div>
                <div>
                  <p className="text-xs text-gray-500">Parts/Consumables</p>
                  <p className="text-xl font-bold text-orange-600">
                    {(summary.by_type?.parts || 0) + (summary.by_type?.consumables || 0)}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 flex flex-wrap gap-4 items-center">
          <div className="flex items-center gap-2">
            <Filter size={18} className="text-gray-500" />
            <select
              value={typeFilter}
              onChange={(e) => { setTypeFilter(e.target.value); setCurrentPage(1); }}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
            >
              <option value="all">All Types</option>
              <option value="product">Products (Website)</option>
              <option value="part">Parts (Backend)</option>
              <option value="consumable">Consumables</option>
            </select>
          </div>
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="Search by name or model..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Products Grid */}
      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
            <p className="mt-4 text-gray-500">Loading drafts...</p>
          </div>
        ) : filteredProducts.length === 0 ? (
          <div className="p-12 text-center">
            <CheckCircle size={48} className="mx-auto mb-4 text-green-500" />
            <p className="text-lg font-medium text-gray-900">No draft products!</p>
            <p className="text-gray-500 mt-2">All products have been reviewed and published.</p>
          </div>
        ) : (
          <>
            {/* Table Header */}
            <div className="px-6 py-3 bg-gray-50 border-b flex items-center gap-4">
              <input
                type="checkbox"
                checked={selectedProducts.length === products.length && products.length > 0}
                onChange={toggleSelectAll}
                className="w-4 h-4 text-purple-600 rounded"
              />
              <span className="text-sm text-gray-500">
                {selectedProducts.length > 0 ? `${selectedProducts.length} selected` : 'Select all'}
              </span>
            </div>

            {/* Products List */}
            <div className="divide-y divide-gray-200">
              {filteredProducts.map(product => (
                <div 
                  key={product.id} 
                  className={`p-4 hover:bg-gray-50 ${selectedProducts.includes(product.id) ? 'bg-purple-50' : ''}`}
                >
                  <div className="flex items-start gap-4">
                    {/* Checkbox */}
                    <input
                      type="checkbox"
                      checked={selectedProducts.includes(product.id)}
                      onChange={() => toggleSelect(product.id)}
                      className="w-4 h-4 text-purple-600 rounded mt-1"
                    />

                    {/* Image */}
                    <div className="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden">
                      {product.images?.length > 0 ? (
                        <img 
                          src={`${BACKEND_URL}${product.images[0].url}`} 
                          alt={product.name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <label className="cursor-pointer text-center p-2 hover:bg-gray-200 w-full h-full flex flex-col items-center justify-center">
                          <ImageIcon size={24} className="text-gray-400 mb-1" />
                          <span className="text-xs text-gray-500">Add Image</span>
                          <input
                            type="file"
                            accept="image/*"
                            className="hidden"
                            onChange={(e) => e.target.files[0] && handleImageUpload(product.id, e.target.files[0])}
                          />
                        </label>
                      )}
                    </div>

                    {/* Details */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        {getTypeIcon(product.item_type)}
                        <h3 className="font-medium text-gray-900 truncate">{product.name}</h3>
                      </div>
                      <p className="text-sm text-gray-500">Model: {product.model_number}</p>
                      <p className="text-sm text-gray-500">
                        Brand: {product.brand} | HSN: {product.hsn_code || 'N/A'}
                      </p>
                      <div className="flex items-center gap-4 mt-2">
                        <span className="text-sm">
                          <span className="text-gray-500">Purchase:</span> ₹{product.purchase_price?.toLocaleString()}
                        </span>
                        <span className="text-sm">
                          <span className="text-gray-500">Selling:</span> ₹{product.price?.toLocaleString()}
                        </span>
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          product.item_type === 'product' ? 'bg-blue-100 text-blue-700' :
                          product.item_type === 'part' ? 'bg-orange-100 text-orange-700' :
                          'bg-green-100 text-green-700'
                        }`}>
                          {getTypeLabel(product.item_type)}
                        </span>
                      </div>
                      
                      {/* Review Notes */}
                      {product.review_notes?.length > 0 && (
                        <div className="flex gap-2 mt-2">
                          {product.review_notes.map((note, idx) => (
                            <span key={idx} className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded">
                              ⚠️ {note}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => { setEditingProduct({...product}); setShowEditModal(true); }}
                        className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg"
                        title="Edit"
                      >
                        <Edit size={18} />
                      </button>
                      
                      {product.images?.length > 0 && product.item_type === 'product' ? (
                        <button
                          onClick={() => handlePublish(product.id)}
                          className="px-3 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 flex items-center gap-1"
                        >
                          <CheckCircle size={16} />
                          Publish
                        </button>
                      ) : product.item_type !== 'product' ? (
                        <span className="text-xs text-gray-500 px-2 py-1 bg-gray-100 rounded">
                          Backend Only
                        </span>
                      ) : (
                        <span className="text-xs text-yellow-600 px-2 py-1 bg-yellow-50 rounded">
                          Needs Image
                        </span>
                      )}
                      
                      <button
                        onClick={() => handleDelete(product.id)}
                        className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg"
                        title="Delete"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="px-6 py-4 border-t flex justify-center gap-2">
                {Array.from({ length: totalPages }, (_, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentPage(i + 1)}
                    className={`px-3 py-1 rounded ${
                      currentPage === i + 1 
                        ? 'bg-purple-600 text-white' 
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {i + 1}
                  </button>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* Edit Modal */}
      {showEditModal && editingProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold">Edit Draft Product</h2>
                <button onClick={() => setShowEditModal(false)} className="text-gray-500 hover:text-gray-700">
                  <X size={24} />
                </button>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Product Name</label>
                <input
                  type="text"
                  value={editingProduct.name || ''}
                  onChange={(e) => setEditingProduct({...editingProduct, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={editingProduct.description || ''}
                  onChange={(e) => setEditingProduct({...editingProduct, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  rows={3}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Brand</label>
                  <input
                    type="text"
                    value={editingProduct.brand || ''}
                    onChange={(e) => setEditingProduct({...editingProduct, brand: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <input
                    type="text"
                    value={editingProduct.category || ''}
                    onChange={(e) => setEditingProduct({...editingProduct, category: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Selling Price</label>
                  <input
                    type="number"
                    value={editingProduct.price || 0}
                    onChange={(e) => setEditingProduct({...editingProduct, price: parseFloat(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">MRP</label>
                  <input
                    type="number"
                    value={editingProduct.mrp || 0}
                    onChange={(e) => setEditingProduct({...editingProduct, mrp: parseFloat(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Item Type</label>
                <select
                  value={editingProduct.item_type || 'product'}
                  onChange={(e) => setEditingProduct({...editingProduct, item_type: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="product">Product (Visible on Website)</option>
                  <option value="part">Part (Backend Only)</option>
                  <option value="consumable">Consumable (Backend Only)</option>
                </select>
              </div>
            </div>
            <div className="p-6 border-t bg-gray-50 flex justify-end gap-2">
              <button
                onClick={() => setShowEditModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                onClick={handleUpdateProduct}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DraftProductsReview;
