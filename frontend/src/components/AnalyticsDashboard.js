import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, ShoppingCart, Package, AlertTriangle, Users, Activity, UserPlus, Clock } from 'lucide-react';

const AnalyticsDashboard = () => {
  const [metrics, setMetrics] = useState({});
  const [salesTrend, setSalesTrend] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [customerData, setCustomerData] = useState({});
  const [siteActivity, setSiteActivity] = useState({});
  const [loading, setLoading] = useState(true);

  
  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      // Fetch dashboard metrics
      const metricsRes = await fetch(`${BACKEND_URL}/api/admin/analytics/dashboard`);
      const metricsData = await metricsRes.json();
      setMetrics(metricsData.data || {});

      // Fetch sales trend
      const trendRes = await fetch(`${BACKEND_URL}/api/admin/analytics/sales-trend?days=30`);
      const trendData = await trendRes.json();
      setSalesTrend(trendData.data || []);

      // Fetch category performance
      const categoryRes = await fetch(`${BACKEND_URL}/api/admin/analytics/category-performance`);
      const categoryData = await categoryRes.json();
      setCategoryData(categoryData.data || []);

      // Fetch customer signups
      const customerRes = await fetch(`${BACKEND_URL}/api/admin/analytics/customer-signups`);
      const customerResult = await customerRes.json();
      setCustomerData(customerResult.data || {});

      // Fetch site activity
      const activityRes = await fetch(`${BACKEND_URL}/api/admin/analytics/site-activity`);
      const activityResult = await activityRes.json();
      setSiteActivity(activityResult.data || {});

      setLoading(false);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      // Set default empty values on error
      setMetrics({});
      setSalesTrend([]);
      setCategoryData([]);
      setCustomerData({});
      setSiteActivity({});
      setLoading(false);
    }
  };

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl">Loading analytics...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-2">Real-time business intelligence and insights</p>
        </div>

        {/* Key Metrics Cards */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-600 text-sm font-medium">Total Revenue</h3>
              <DollarSign className="w-8 h-8 text-green-500" />
            </div>
            <p className="text-3xl font-bold">₹{metrics?.total_revenue?.toLocaleString() || 0}</p>
            <div className="flex items-center mt-2 text-green-600 text-sm">
              <TrendingUp className="w-4 h-4 mr-1" />
              <span>+12% vs last month</span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-600 text-sm font-medium">Total Orders</h3>
              <ShoppingCart className="w-8 h-8 text-blue-500" />
            </div>
            <p className="text-3xl font-bold">{metrics?.total_orders || 0}</p>
            <div className="flex items-center mt-2 text-blue-600 text-sm">
              <TrendingUp className="w-4 h-4 mr-1" />
              <span>+8% vs last month</span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-600 text-sm font-medium">Avg Order Value</h3>
              <DollarSign className="w-8 h-8 text-orange-500" />
            </div>
            <p className="text-3xl font-bold">₹{Math.round(metrics?.average_order_value || 0).toLocaleString()}</p>
            <div className="flex items-center mt-2 text-orange-600 text-sm">
              <TrendingUp className="w-4 h-4 mr-1" />
              <span>+5% vs last month</span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-600 text-sm font-medium">Low Stock Items</h3>
              <AlertTriangle className="w-8 h-8 text-red-500" />
            </div>
            <p className="text-3xl font-bold">{metrics?.low_stock_count || 0}</p>
            <p className="text-red-600 text-sm mt-2">Requires attention</p>
          </div>
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          {/* Sales Trend */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Sales Trend (Last 30 Days)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={salesTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{fontSize: 12}} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} name="Revenue (₹)" />
                <Line type="monotone" dataKey="orders" stroke="#10b981" strokeWidth={2} name="Orders" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Category Performance */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Products by Category</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={metrics?.categories || []}
                  dataKey="count"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={(entry) => `${entry.category}: ${entry.count}`}
                >
                  {(metrics?.categories || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          {/* Category Performance Bar Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Category Stock Levels</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" tick={{fontSize: 11}} angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="stock" fill="#3b82f6" name="Total Stock" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Average Price by Category */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Avg Price by Category</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" tick={{fontSize: 11}} angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="avg_price" fill="#10b981" name="Avg Price (₹)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Performance Table */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Category Performance Details</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Category</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">Products</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">Total Stock</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">Avg Price</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">Status</th>
                </tr>
              </thead>
              <tbody>
                {categoryData.map((cat, index) => (
                  <tr key={index} className="border-t hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{cat.category}</td>
                    <td className="px-4 py-3 text-right">{cat.products}</td>
                    <td className="px-4 py-3 text-right">{cat.stock}</td>
                    <td className="px-4 py-3 text-right">₹{cat.avg_price.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right">
                      <span className={`px-2 py-1 rounded text-xs ${
                        cat.stock > 100 ? 'bg-green-100 text-green-800' :
                        cat.stock > 50 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {cat.stock > 100 ? 'Healthy' : cat.stock > 50 ? 'Moderate' : 'Low'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Customer & Site Activity Section */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          {/* Customer Signups */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <UserPlus className="w-5 h-5 text-green-600" />
                Customer Signups
              </h2>
              <span className="text-2xl font-bold text-green-600">{customerData.total_customers || 0}</span>
            </div>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="bg-green-50 rounded-lg p-3 text-center">
                <div className="text-xl font-bold text-green-700">{customerData.signups_last_7_days || 0}</div>
                <div className="text-xs text-green-600">Last 7 Days</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-3 text-center">
                <div className="text-xl font-bold text-blue-700">{customerData.signups_last_30_days || 0}</div>
                <div className="text-xs text-blue-600">Last 30 Days</div>
              </div>
            </div>

            <h3 className="text-sm font-medium text-gray-600 mb-2">Recent Signups</h3>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {(customerData.recent_signups || []).map((user, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm">
                  <div>
                    <div className="font-medium">{user.name || 'Unknown'}</div>
                    <div className="text-xs text-gray-500">{user.email}</div>
                  </div>
                  <div className="text-xs text-gray-400">
                    {user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
                  </div>
                </div>
              ))}
              {(!customerData.recent_signups || customerData.recent_signups.length === 0) && (
                <div className="text-center text-gray-400 py-4">No signups yet</div>
              )}
            </div>
          </div>

          {/* Site Activity Summary */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <Activity className="w-5 h-5 text-purple-600" />
                Site Activity
              </h2>
            </div>
            
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="bg-purple-50 rounded-lg p-3 text-center">
                <div className="text-xl font-bold text-purple-700">{siteActivity.counts?.customers || 0}</div>
                <div className="text-xs text-purple-600">Total Customers</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-3 text-center">
                <div className="text-xl font-bold text-blue-700">{siteActivity.counts?.invoices || 0}</div>
                <div className="text-xs text-blue-600">Invoices</div>
              </div>
              <div className="bg-amber-50 rounded-lg p-3 text-center">
                <div className="text-xl font-bold text-amber-700">{siteActivity.counts?.sales_orders || 0}</div>
                <div className="text-xs text-amber-600">Sales Orders</div>
              </div>
              <div className="bg-rose-50 rounded-lg p-3 text-center">
                <div className="text-xl font-bold text-rose-700">{siteActivity.counts?.service_requests || 0}</div>
                <div className="text-xs text-rose-600">Service Requests</div>
              </div>
            </div>

            <h3 className="text-sm font-medium text-gray-600 mb-2">Recent Invoices</h3>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {(siteActivity.recent_invoices || []).map((inv, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm">
                  <div className="font-medium">{inv.invoice_number}</div>
                  <div className="text-green-600 font-medium">₹{(inv.total_amount || 0).toLocaleString()}</div>
                </div>
              ))}
              {(!siteActivity.recent_invoices || siteActivity.recent_invoices.length === 0) && (
                <div className="text-center text-gray-400 py-4">No recent invoices</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
