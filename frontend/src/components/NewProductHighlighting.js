import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { Sparkles, Plus, Calendar, Star, Tag, X, Check } from 'lucide-react';


const NewProductHighlighting = () => {
  const [products, setProducts] = useState([]);
  const [newProducts, setNewProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [highlightDays, setHighlightDays] = useState(30);
  const [badgeText, setBadgeText] = useState('NEW');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch all products
      const productsRes = await fetch(`${BACKEND_URL}/api/products`);
      const productsData = await productsRes.json();
      setProducts(productsData.products || productsData || []);

      // Fetch new products
      const newRes = await fetch(`${BACKEND_URL}/api/new-products/`);
      const newData = await newRes.json();
      setNewProducts(newData.products || []);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  const handleMarkAsNew = async () => {
    if (selectedProducts.length === 0) {
      alert('Please select at least one product');
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/new-products/bulk-mark`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_ids: selectedProducts,
          days: highlightDays
        })
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        alert(`✅ ${data.modified_count} product(s) marked as new!`);
        setShowModal(false);
        setSelectedProducts([]);
        setBadgeText('NEW');
        setHighlightDays(30);
        fetchData();
      }
    } catch (error) {
      console.error('Error marking products:', error);
      alert('Failed to mark products as new');
    }
  };

  const handleRemoveBadge = async (productId) => {
    if (!window.confirm('Remove NEW badge from this product?')) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/new-products/${productId}/remove-new`, {
        method: 'DELETE'
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        alert('NEW badge removed!');
        fetchData();
      }
    } catch (error) {
      console.error('Error removing badge:', error);
    }
  };

  const handleCleanupExpired = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/new-products/cleanup-expired`, {
        method: 'POST'
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        alert(`✅ Cleaned up ${data.modified_count} expired badges`);
        fetchData();
      }
    } catch (error) {
      console.error('Error cleaning up:', error);
    }
  };

  const toggleProductSelection = (productId) => {
    setSelectedProducts(prev => 
      prev.includes(productId)
        ? prev.filter(id => id !== productId)
        : [...prev, productId]
    );
  };

  const filteredProducts = products.filter(p => 
    p.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.brand?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-700"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-amber-700" />
            New Product Highlighting
          </h1>
          <p className="text-gray-600 mt-2">Mark products as "NEW" to highlight them on the homepage</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleCleanupExpired}
            className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors flex items-center gap-2"
          >
            <Calendar className="w-5 h-5" />
            Cleanup Expired
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="bg-amber-700 text-white px-6 py-3 rounded-lg hover:bg-amber-800 transition-colors flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Mark Products as NEW
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-gray-900">{newProducts.length}</div>
          <div className="text-sm text-gray-600">Currently Highlighted</div>
        </div>
        <div className="bg-green-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-green-700">{products.length}</div>
          <div className="text-sm text-green-600">Total Products</div>
        </div>
        <div className="bg-amber-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-amber-700">
            {products.filter(p => p.is_new).length}
          </div>
          <div className="text-sm text-amber-600">Active Badges</div>
        </div>
        <div className="bg-blue-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-blue-700">30</div>
          <div className="text-sm text-blue-600">Default Days</div>
        </div>
      </div>

      {/* Empty State or Currently Highlighted Products */}
      {newProducts.length === 0 ? (
        <div className="bg-white rounded-lg shadow-lg p-12 text-center">
          <Sparkles className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Products Highlighted Yet</h3>
          <p className="text-gray-600 mb-6">
            Mark products as NEW to highlight them on your homepage and attract customers
          </p>
          <button
            onClick={() => setShowModal(true)}
            className="bg-amber-700 text-white px-6 py-3 rounded-lg hover:bg-amber-800 transition-colors flex items-center gap-2 mx-auto"
          >
            <Plus className="w-5 h-5" />
            Mark First Product as NEW
          </button>
        </div>
      ) : (
        <div>
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Star className="w-6 h-6 text-amber-500" />
            Currently Highlighted Products
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {newProducts.map((product) => (
              <div key={product.id} className="bg-white rounded-lg shadow-lg overflow-hidden relative">
                {/* NEW Badge */}
                <div className="absolute top-2 left-2 z-10">
                  <span className="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg">
                    {product.new_badge_text || 'NEW'}
                  </span>
                </div>

                {/* Product Image */}
                <div className="h-48 bg-gray-100 relative">
                  {product.image ? (
                    <img
                      src={product.image}
                      alt={product.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <Tag className="w-16 h-16 text-gray-300" />
                    </div>
                  )}
                </div>

                <div className="p-4">
                  <h3 className="font-bold text-lg text-gray-900 mb-1">{product.name}</h3>
                  <p className="text-sm text-gray-600 mb-2">{product.brand}</p>
                  <p className="text-xl font-bold text-amber-700 mb-3">₹{product.price?.toLocaleString()}</p>

                  {/* Expiry Info */}
                  <div className="flex items-center gap-2 text-xs text-gray-600 mb-3">
                    <Calendar className="w-4 h-4" />
                    <span>
                      Expires: {new Date(product.new_until).toLocaleDateString()}
                    </span>
                  </div>

                  {/* Priority Badge */}
                  {product.new_priority > 0 && (
                    <div className="mb-3">
                      <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs">
                        Priority: {product.new_priority}
                      </span>
                    </div>
                  )}

                  {/* Remove Button */}
                  <button
                    onClick={() => handleRemoveBadge(product.id)}
                    className="w-full bg-red-50 text-red-600 py-2 rounded-lg hover:bg-red-100 transition-colors flex items-center justify-center gap-2"
                  >
                    <X className="w-4 h-4" />
                    Remove Badge
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
        </div>
      )}

      {/* Add Products Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full my-8">
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <Sparkles className="w-6 h-6 text-amber-700" />
                Mark Products as NEW
              </h2>

              {/* Configuration */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Highlight Duration (Days)</label>
                  <input
                    type="number"
                    value={highlightDays}
                    onChange={(e) => setHighlightDays(parseInt(e.target.value))}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                    min="1"
                    max="365"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Badge Text</label>
                  <input
                    type="text"
                    value={badgeText}
                    onChange={(e) => setBadgeText(e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                    placeholder="e.g., NEW, FRESH, LATEST"
                    maxLength="10"
                  />
                </div>
              </div>

              {/* Search */}
              <div className="mb-4">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                  placeholder="Search products by name or brand..."
                />
              </div>

              {/* Product Selection */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-3">
                  <label className="block text-sm font-medium text-gray-700">
                    Select Products ({selectedProducts.length} selected)
                  </label>
                  <button
                    onClick={() => {
                      if (selectedProducts.length === filteredProducts.length) {
                        setSelectedProducts([]);
                      } else {
                        setSelectedProducts(filteredProducts.map(p => p.id));
                      }
                    }}
                    className="text-sm text-amber-700 hover:text-amber-800"
                  >
                    {selectedProducts.length === filteredProducts.length ? 'Deselect All' : 'Select All'}
                  </button>
                </div>
                <div className="border rounded-lg p-4 max-h-96 overflow-y-auto">
                  <div className="grid grid-cols-2 gap-2">
                    {filteredProducts.slice(0, 50).map((product) => (
                      <label
                        key={product.id}
                        className={`flex items-center gap-2 p-3 rounded cursor-pointer transition-colors ${
                          selectedProducts.includes(product.id) 
                            ? 'bg-amber-50 border-2 border-amber-500' 
                            : 'bg-gray-50 border-2 border-transparent hover:bg-gray-100'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={selectedProducts.includes(product.id)}
                          onChange={() => toggleProductSelection(product.id)}
                          className="w-4 h-4 text-amber-600"
                        />
                        <div className="flex-1">
                          <div className="text-sm font-medium">{product.name}</div>
                          <div className="text-xs text-gray-500">
                            {product.brand} - ₹{product.price?.toLocaleString()}
                          </div>
                          {product.is_new && (
                            <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded mt-1 inline-block">
                              Already marked NEW
                            </span>
                          )}
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              {/* Preview */}
              {selectedProducts.length > 0 && (
                <div className="mb-6 p-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg border-2 border-amber-200">
                  <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <Check className="w-5 h-5 text-green-600" />
                    Preview
                  </h3>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Products Selected:</span>
                      <span className="font-bold text-gray-900">{selectedProducts.length}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Highlight Duration:</span>
                      <span className="font-bold text-gray-900">{highlightDays} days</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Expires On:</span>
                      <span className="font-bold text-gray-900">
                        {new Date(Date.now() + highlightDays * 24 * 60 * 60 * 1000).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="mt-3">
                      <span className="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow">
                        {badgeText}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setSelectedProducts([]);
                    setBadgeText('NEW');
                    setHighlightDays(30);
                  }}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleMarkAsNew}
                  className="flex-1 bg-amber-700 text-white px-4 py-2 rounded-lg hover:bg-amber-800 disabled:bg-gray-300 disabled:cursor-not-allowed"
                  disabled={selectedProducts.length === 0}
                >
                  Mark as NEW ({selectedProducts.length})
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NewProductHighlighting;
