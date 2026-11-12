import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Package, AlertTriangle, TrendingDown, DollarSign, RefreshCw, BarChart3, ArrowLeft } from 'lucide-react';
import { utils } from '../services/api';

const InventoryManagement = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [inventoryValue, setInventoryValue] = useState({});
  const [turnover, setTurnover] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInventoryData();
  }, []);

  const fetchInventoryData = async () => {
    try {
      setLoading(true);
      
      // Fetch inventory alerts
      const alertsRes = await utils.fetchAPI('/api/admin/inventory/alerts');
      const alertsData = await alertsRes.json();
      setAlerts(alertsData.alerts || []);

      // Fetch inventory value
      const valueRes = await utils.fetchAPI('/api/admin/inventory/value');
      const valueData = await valueRes.json();
      setInventoryValue(valueData.data || {});

      // Fetch turnover data
      const turnoverRes = await utils.fetchAPI('/api/admin/inventory/turnover');
      const turnoverData = await turnoverRes.json();
      setTurnover(turnoverData.data || {});

      // Calculate stats from alerts
      const lowStock = alerts.filter(a => a.alert_type === 'low_stock').length;
      const outOfStock = alerts.filter(a => a.alert_type === 'out_of_stock').length;
      
      setStats({
        total_alerts: alerts.length,
        low_stock: lowStock,
        out_of_stock: outOfStock
      });

      setLoading(false);
    } catch (error) {
      console.error('Error fetching inventory data:', error);
      setLoading(false);
    }
  };

  const handleReorder = async (productId) => {
    try {
      const response = await utils.fetchAPI(`/api/admin/inventory/reorder/${productId}?quantity=50`, {
        method: 'POST',
      });

      if (response.ok) {
        alert('Reorder request created successfully!');
        fetchInventoryData();
      }
    } catch (error) {
      console.error('Error creating reorder:', error);
      alert('Failed to create reorder request');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading inventory data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => navigate('/admin')}
          className="flex items-center px-4 py-2 mb-6 text-gray-700 bg-white hover:bg-gray-100 rounded-lg transition-all border border-gray-300 hover:border-gray-400 shadow-sm"
          data-testid="back-to-dashboard-btn"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          <span className="font-medium">Back to Dashboard</span>
        </button>

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Inventory Management</h1>
          <p className="text-gray-600">Track stock levels, manage reorders, and monitor inventory health</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-600">Total Inventory Value</CardTitle>
                <DollarSign className="h-5 w-5 text-green-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">
                {formatCurrency(inventoryValue.total_inventory_value || 0)}
              </div>
              <p className="text-xs text-gray-500 mt-1">Across all products</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-600">Total Alerts</CardTitle>
                <AlertTriangle className="h-5 w-5 text-orange-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">{stats.total_alerts || 0}</div>
              <p className="text-xs text-red-600 mt-1">{stats.low_stock || 0} low stock, {stats.out_of_stock || 0} out of stock</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-600">Fast Moving Items</CardTitle>
                <TrendingDown className="h-5 w-5 text-blue-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">{turnover.fast_moving?.length || 0}</div>
              <p className="text-xs text-gray-500 mt-1">Top selling products</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-600">Slow Moving Items</CardTitle>
                <Package className="h-5 w-5 text-purple-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">{turnover.slow_moving?.length || 0}</div>
              <p className="text-xs text-gray-500 mt-1">High stock, low sales</p>
            </CardContent>
          </Card>
        </div>

        {/* Inventory Value by Category */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Inventory Value by Category</CardTitle>
            <CardDescription>Stock value distribution across product categories</CardDescription>
          </CardHeader>
          <CardContent>
            {inventoryValue.by_category && inventoryValue.by_category.length > 0 ? (
              <div className="space-y-4">
                {inventoryValue.by_category.map((cat, index) => (
                  <div key={index} className="flex items-center">
                    <div className="w-32 text-sm font-medium text-gray-700">{cat.category || 'Uncategorized'}</div>
                    <div className="flex-1 mx-4">
                      <div className="h-8 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-green-500 to-blue-600 transition-all duration-500"
                          style={{ 
                            width: `${((cat.value / inventoryValue.total_inventory_value) * 100)}%` 
                          }}
                        ></div>
                      </div>
                    </div>
                    <div className="w-32 text-right">
                      <div className="text-sm font-semibold text-gray-900">{formatCurrency(cat.value)}</div>
                      <div className="text-xs text-gray-500">{cat.products} products</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">No inventory data available</div>
            )}
          </CardContent>
        </Card>

        {/* Stock Alerts */}
        <Card className="mb-8">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Stock Alerts</CardTitle>
                <CardDescription>Products requiring attention</CardDescription>
              </div>
              <button
                onClick={fetchInventoryData}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </button>
            </div>
          </CardHeader>
          <CardContent>
            {alerts.length === 0 ? (
              <div className="text-center py-12">
                <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">All Stock Levels Healthy</h3>
                <p className="text-gray-600">No low stock or out of stock alerts at this time.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {alerts.map((alert, index) => (
                  <div
                    key={index}
                    className={`border rounded-lg p-4 ${getPriorityColor(alert.priority)}`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <AlertTriangle className="h-4 w-4" />
                          <h4 className="font-semibold">{alert.product_name}</h4>
                          <span className="px-2 py-0.5 rounded text-xs font-medium bg-white bg-opacity-50">
                            {alert.model_number}
                          </span>
                        </div>
                        <div className="text-sm">
                          <span className="font-medium">Current Stock: </span>
                          <span className="font-bold">{alert.current_stock} units</span>
                          {alert.reserved_stock > 0 && (
                            <span className="ml-2 text-orange-600 font-medium">
                              ({alert.reserved_stock} blocked)
                            </span>
                          )}
                          <span className="ml-4 text-gray-600">Category: {alert.category}</span>
                        </div>
                        <div className="mt-2 text-xs font-medium">
                          {alert.alert_type === 'out_of_stock' ? '⚠️ OUT OF STOCK' : '⚡ LOW STOCK'}
                        </div>
                      </div>
                      <button
                        onClick={() => handleReorder(alert.id)}
                        className="px-4 py-2 bg-white bg-opacity-80 hover:bg-opacity-100 rounded-lg font-medium text-sm transition-all"
                      >
                        Create Reorder
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Fast & Slow Moving Items */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Fast Moving */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingDown className="h-5 w-5 text-green-600" />
                Fast Moving Items
              </CardTitle>
              <CardDescription>Products with high turnover rate</CardDescription>
            </CardHeader>
            <CardContent>
              {turnover.fast_moving && turnover.fast_moving.length > 0 ? (
                <div className="space-y-3">
                  {turnover.fast_moving.slice(0, 5).map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <div className="flex-1">
                        <div className="font-semibold text-gray-900">{item.product_name}</div>
                        <div className="text-sm text-gray-600">{item.model_number}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-green-600">{item.stock} units</div>
                        <div className="text-xs text-gray-500">{item.category}</div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">No data available</div>
              )}
            </CardContent>
          </Card>

          {/* Slow Moving */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-orange-600" />
                Slow Moving Items
              </CardTitle>
              <CardDescription>Products with low turnover rate</CardDescription>
            </CardHeader>
            <CardContent>
              {turnover.slow_moving && turnover.slow_moving.length > 0 ? (
                <div className="space-y-3">
                  {turnover.slow_moving.slice(0, 5).map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                      <div className="flex-1">
                        <div className="font-semibold text-gray-900">{item.product_name}</div>
                        <div className="text-sm text-gray-600">{item.model_number}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-orange-600">{item.stock} units</div>
                        <div className="text-xs text-gray-500">{item.category}</div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">No data available</div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default InventoryManagement;
