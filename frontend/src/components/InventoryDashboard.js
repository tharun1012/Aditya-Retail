import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { Package, AlertTriangle, TrendingDown, TrendingUp, DollarSign, Edit, History } from 'lucide-react';


const InventoryDashboard = () => {
  const [summary, setSummary] = useState(null);
  const [lowStockProducts, setLowStockProducts] = useState([]);
  const [outOfStockProducts, setOutOfStockProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('summary');
  const [showAdjustModal, setShowAdjustModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [adjustmentData, setAdjustmentData] = useState({
    new_stock_level: 0,
    reason: ''
  });

  useEffect(() => {
    fetchInventoryData();
  }, []);

  const fetchInventoryData = async () => {
    setLoading(true);
    try {
      // Fetch summary
      const summaryRes = await fetch(`${BACKEND_URL}/api/inventory/summary`);
      const summaryData = await summaryRes.json();
      if (summaryData.status === 'success') {
        setSummary(summaryData.summary);
      }

      // Fetch low stock
      const lowStockRes = await fetch(`${BACKEND_URL}/api/inventory/low-stock`);
      const lowStockData = await lowStockRes.json();
      if (lowStockData.status === 'success') {
        setLowStockProducts(lowStockData.products);
      }

      // Fetch out of stock
      const outOfStockRes = await fetch(`${BACKEND_URL}/api/inventory/out-of-stock`);
      const outOfStockData = await outOfStockRes.json();
      if (outOfStockData.status === 'success') {
        setOutOfStockProducts(outOfStockData.products);
      }
    } catch (error) {
      console.error('Error fetching inventory data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAdjustStock = async () => {
    if (!selectedProduct) return;

    try {
      const adminUser = JSON.parse(localStorage.getItem('admin_user') || '{}');
      const response = await fetch(`${BACKEND_URL}/api/inventory/adjust`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: selectedProduct.id,
          new_stock_level: parseInt(adjustmentData.new_stock_level),
          reason: adjustmentData.reason,
          adjusted_by: adminUser.email || 'admin'
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        alert('Stock adjusted successfully!');
        setShowAdjustModal(false);
        fetchInventoryData();
      } else {
        alert('Failed to adjust stock');
      }
    } catch (error) {
      console.error('Error adjusting stock:', error);
      alert('Failed to adjust stock');
    }
  };

  const openAdjustModal = (product) => {
    setSelectedProduct(product);
    setAdjustmentData({
      new_stock_level: product.current_stock || 0,
      reason: ''
    });
    setShowAdjustModal(true);
  };

  const getStockIndicator = (current, reorder) => {
    if (current <= 0) return { color: 'bg-red-500', label: 'OUT OF STOCK' };
    if (current <= reorder) return { color: 'bg-orange-500', label: 'LOW STOCK' };
    return { color: 'bg-green-500', label: 'IN STOCK' };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <Package className="w-8 h-8 text-blue-600" />
          Inventory Management
        </h1>
        <p className="text-gray-600 mt-2">Track stock levels, manage inventory, and monitor alerts</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center gap-4">
            <div className="bg-blue-100 p-4 rounded-full">
              <Package className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600">{summary?.total_products || 0}</div>
              <div className="text-sm text-gray-600">Total Products</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center gap-4">
            <div className="bg-green-100 p-4 rounded-full">
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
            <div>
              <div className="text-3xl font-bold text-green-600">{summary?.in_stock_count || 0}</div>
              <div className="text-sm text-gray-600">In Stock</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center gap-4">
            <div className="bg-orange-100 p-4 rounded-full">
              <AlertTriangle className="w-8 h-8 text-orange-600" />
            </div>
            <div>
              <div className="text-3xl font-bold text-orange-600">{summary?.low_stock_count || 0}</div>
              <div className="text-sm text-gray-600">Low Stock</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center gap-4">
            <div className="bg-red-100 p-4 rounded-full">
              <TrendingDown className="w-8 h-8 text-red-600" />
            </div>
            <div>
              <div className="text-3xl font-bold text-red-600">{summary?.out_of_stock_count || 0}</div>
              <div className="text-sm text-gray-600">Out of Stock</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center gap-4">
            <div className="bg-purple-100 p-4 rounded-full">
              <DollarSign className="w-8 h-8 text-purple-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-600">₹{(summary?.total_stock_value / 100000).toFixed(1)}L</div>
              <div className="text-sm text-gray-600">Stock Value</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-lg mb-6">
        <div className="border-b border-gray-200">
          <div className="flex gap-4 px-6">
            <button
              onClick={() => setActiveTab('summary')}
              className={`py-4 px-4 font-semibold border-b-2 transition-colors ${
                activeTab === 'summary'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Summary
            </button>
            <button
              onClick={() => setActiveTab('low-stock')}
              className={`py-4 px-4 font-semibold border-b-2 transition-colors flex items-center gap-2 ${
                activeTab === 'low-stock'
                  ? 'border-orange-600 text-orange-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Low Stock Alerts
              {lowStockProducts.length > 0 && (
                <span className="bg-orange-500 text-white text-xs px-2 py-1 rounded-full">
                  {lowStockProducts.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setActiveTab('out-of-stock')}
              className={`py-4 px-4 font-semibold border-b-2 transition-colors flex items-center gap-2 ${
                activeTab === 'out-of-stock'
                  ? 'border-red-600 text-red-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Out of Stock
              {outOfStockProducts.length > 0 && (
                <span className="bg-red-500 text-white text-xs px-2 py-1 rounded-full">
                  {outOfStockProducts.length}
                </span>
              )}
            </button>
          </div>
        </div>

        <div className="p-6">
          {activeTab === 'summary' && (
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Inventory Summary</h3>
              <div className="grid grid-cols-2 gap-6">
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="text-gray-700 font-semibold mb-2">Stock Status Breakdown</div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>In Stock:</span>
                      <span className="font-bold text-green-600">{summary?.in_stock_count || 0} products</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Low Stock:</span>
                      <span className="font-bold text-orange-600">{summary?.low_stock_count || 0} products</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Out of Stock:</span>
                      <span className="font-bold text-red-600">{summary?.out_of_stock_count || 0} products</span>
                    </div>
                  </div>
                </div>
                <div className="bg-purple-50 rounded-lg p-4">
                  <div className="text-gray-700 font-semibold mb-2">Inventory Valuation</div>
                  <div className="text-3xl font-bold text-purple-600 mb-1">
                    ₹{(summary?.total_stock_value || 0).toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">Total Stock Value</div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'low-stock' && (
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <AlertTriangle className="w-6 h-6 text-orange-600" />
                Low Stock Products
              </h3>
              {lowStockProducts.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p>No low stock products</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                      <tr>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Product</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Category</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Current Stock</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Reorder Level</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {lowStockProducts.map((product) => {
                        const indicator = getStockIndicator(product.current_stock, product.reorder_level);
                        return (
                          <tr key={product.id} className="hover:bg-gray-50">
                            <td className="px-4 py-3">
                              <div className="font-semibold text-gray-900">{product.name}</div>
                              <div className="text-sm text-gray-500">{product.brand}</div>
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-600">{product.category}</td>
                            <td className="px-4 py-3">
                              <span className="text-lg font-bold text-orange-600">{product.current_stock || 0}</span>
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-600">{product.reorder_level || 5}</td>
                            <td className="px-4 py-3">
                              <span className={`${indicator.color} text-white text-xs px-3 py-1 rounded-full font-semibold`}>
                                {indicator.label}
                              </span>
                            </td>
                            <td className="px-4 py-3">
                              <button
                                onClick={() => openAdjustModal(product)}
                                className="text-blue-600 hover:text-blue-800 flex items-center gap-1"
                              >
                                <Edit className="w-4 h-4" />
                                Adjust
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {activeTab === 'out-of-stock' && (
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <TrendingDown className="w-6 h-6 text-red-600" />
                Out of Stock Products
              </h3>
              {outOfStockProducts.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p>No out of stock products</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                      <tr>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Product</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Category</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Price</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {outOfStockProducts.map((product) => (
                        <tr key={product.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3">
                            <div className="font-semibold text-gray-900">{product.name}</div>
                            <div className="text-sm text-gray-500">{product.brand}</div>
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-600">{product.category}</td>
                          <td className="px-4 py-3 text-sm font-semibold text-gray-900">₹{product.price?.toLocaleString()}</td>
                          <td className="px-4 py-3">
                            <span className="bg-red-500 text-white text-xs px-3 py-1 rounded-full font-semibold">
                              OUT OF STOCK
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            <button
                              onClick={() => openAdjustModal(product)}
                              className="text-blue-600 hover:text-blue-800 flex items-center gap-1"
                            >
                              <Edit className="w-4 h-4" />
                              Restock
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Stock Adjustment Modal */}
      {showAdjustModal && selectedProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-md">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 rounded-t-xl">
              <h3 className="text-xl font-bold">Adjust Stock</h3>
              <p className="text-blue-100 mt-1">{selectedProduct.name}</p>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Current Stock: <span className="text-blue-600">{selectedProduct.current_stock || 0} units</span>
                </label>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  New Stock Level *
                </label>
                <input
                  type="number"
                  value={adjustmentData.new_stock_level}
                  onChange={(e) => setAdjustmentData({...adjustmentData, new_stock_level: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter new stock level"
                  min="0"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Reason *
                </label>
                <textarea
                  value={adjustmentData.reason}
                  onChange={(e) => setAdjustmentData({...adjustmentData, reason: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows="3"
                  placeholder="e.g., Physical count correction, Damaged goods, etc."
                />
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-700">
                <strong>Change:</strong> {adjustmentData.new_stock_level - (selectedProduct.current_stock || 0)} units
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => setShowAdjustModal(false)}
                  className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-semibold"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAdjustStock}
                  disabled={!adjustmentData.reason}
                  className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Adjust Stock
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InventoryDashboard;