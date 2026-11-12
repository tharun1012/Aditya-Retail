import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { 
  Store, ShoppingCart, Package, TrendingUp, AlertTriangle, Truck,
  FileText, Receipt, Users, ArrowRightLeft, BarChart3, Calendar,
  LogOut, RefreshCw, ChevronDown, Search, Eye, Check, X, Clock, Home,
  Plus, Printer, Download
} from 'lucide-react';
import PORequestsTab from './PORequestsTab';
import NotificationBell from './NotificationBell';


const StoreDashboard = () => {
  const navigate = useNavigate();
  const [storeUser, setStoreUser] = useState(null);
  const [storeData, setStoreData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [period, setPeriod] = useState('today');
  const [dashboardData, setDashboardData] = useState(null);
  const [inventory, setInventory] = useState(null);
  const [orders, setOrders] = useState([]);
  const [transfers, setTransfers] = useState([]);
  const [reportData, setReportData] = useState(null);
  
  // Create Sales Order State
  const [showCreateOrder, setShowCreateOrder] = useState(false);
  const [products, setProducts] = useState([]);
  const [orderForm, setOrderForm] = useState({
    customer_name: '',
    customer_phone: '',
    customer_email: '',
    customer_address: '',
    items: [],
    notes: ''
  });
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    const user = localStorage.getItem('storeUser');
    const store = localStorage.getItem('storeData');
    
    if (!user || !store) {
      navigate('/store/login');
      return;
    }
    
    setStoreUser(JSON.parse(user));
    setStoreData(JSON.parse(store));
  }, [navigate]);

  useEffect(() => {
    if (storeData) {
      fetchDashboardData();
      fetchInventory();
      fetchOrders();
      fetchTransfers();
    }
  }, [storeData, period]);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/stores/${storeData.id}/dashboard?period=${period}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setDashboardData(data.summary);
      }
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchInventory = async () => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/inventory/store/${storeData.id}?low_stock_only=false`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setInventory(data);
      }
    } catch (error) {
      console.error('Error fetching inventory:', error);
    }
  };

  const fetchOrders = async () => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/reports/so/list?store_id=${storeData.id}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setOrders(data.orders?.slice(0, 20) || []);
      }
    } catch (error) {
      console.error('Error fetching orders:', error);
    }
  };

  const fetchTransfers = async () => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/inventory/transfers?store_id=${storeData.id}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setTransfers(data.transfers || []);
      }
    } catch (error) {
      console.error('Error fetching transfers:', error);
    }
  };

  const fetchReportData = async (reportType) => {
    try {
      let url = '';
      if (reportType === 'daily') {
        url = `${BACKEND_URL}/api/reports/sales/daily?store_id=${storeData.id}`;
      } else if (reportType === 'monthly') {
        url = `${BACKEND_URL}/api/reports/sales/monthly?store_id=${storeData.id}`;
      } else if (reportType === 'item-wise') {
        url = `${BACKEND_URL}/api/reports/sales/by-item?store_id=${storeData.id}&limit=20`;
      }
      
      const response = await fetch(url);
      const data = await response.json();
      if (data.status === 'success') {
        setReportData({ type: reportType, data });
      }
    } catch (error) {
      console.error('Error fetching report:', error);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/products?limit=100`);
      const data = await response.json();
      if (data.products) {
        setProducts(data.products);
      }
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const addItemToOrder = () => {
    if (!selectedProduct || quantity < 1) return;
    
    const existingIndex = orderForm.items.findIndex(item => item.product_id === selectedProduct.id);
    
    if (existingIndex >= 0) {
      const updatedItems = [...orderForm.items];
      updatedItems[existingIndex].quantity += quantity;
      setOrderForm({ ...orderForm, items: updatedItems });
    } else {
      setOrderForm({
        ...orderForm,
        items: [...orderForm.items, {
          product_id: selectedProduct.id,
          product_name: selectedProduct.name,
          price: selectedProduct.price,
          quantity: quantity
        }]
      });
    }
    
    setSelectedProduct(null);
    setQuantity(1);
  };

  const removeItemFromOrder = (index) => {
    const updatedItems = orderForm.items.filter((_, i) => i !== index);
    setOrderForm({ ...orderForm, items: updatedItems });
  };

  const calculateOrderTotal = () => {
    return orderForm.items.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  const handleCreateOrder = async (e) => {
    e.preventDefault();
    
    if (orderForm.items.length === 0) {
      alert('Please add at least one product to the order');
      return;
    }
    
    try {
      const orderData = {
        store_id: storeData.id,
        store_code: storeData.code,
        customer: {
          name: orderForm.customer_name,
          phone: orderForm.customer_phone,
          email: orderForm.customer_email,
          address: orderForm.customer_address
        },
        items: orderForm.items.map(item => ({
          product_id: item.product_id,
          name: item.product_name,
          price: item.price,
          quantity: item.quantity,
          subtotal: item.price * item.quantity
        })),
        total_amount: calculateOrderTotal(),
        notes: orderForm.notes,
        created_by: storeUser.email,
        source: 'store_dashboard'
      };

      const response = await fetch(`${BACKEND_URL}/api/orders/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData)
      });

      const data = await response.json();
      
      if (response.ok) {
        alert(`✅ Order created successfully! Order #: ${data.order_number || data.id}`);
        setShowCreateOrder(false);
        setOrderForm({
          customer_name: '', customer_phone: '', customer_email: '',
          customer_address: '', items: [], notes: ''
        });
        fetchOrders();
      } else {
        alert(`Failed to create order: ${data.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error creating order:', error);
      alert('Error creating order');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('storeToken');
    localStorage.removeItem('storeUser');
    localStorage.removeItem('storeData');
    navigate('/store/login');
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'orders', label: 'Sales Orders', icon: ShoppingCart },
    { id: 'inventory', label: 'Inventory', icon: Package },
    { id: 'transfers', label: 'Stock Transfers', icon: ArrowRightLeft },
    { id: 'po-requests', label: 'PO Requests', icon: Receipt },
    { id: 'reports', label: 'Reports', icon: FileText }
  ];

  if (!storeUser || !storeData) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-teal-700 to-emerald-700 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-white/10 rounded-lg">
                <Store className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-xl font-bold">{storeData.name}</h1>
                <p className="text-teal-100 text-sm">Store Code: {storeData.code}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {/* Notification Bell */}
              <NotificationBell 
                userRole={storeUser?.role || 'store_manager'}
                storeId={storeData?.id}
                userId={storeUser?.id}
              />
              
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium">{storeUser.first_name} {storeUser.last_name}</p>
                <p className="text-teal-200 text-xs">{storeUser.role}</p>
              </div>
              <button
                onClick={() => navigate('/')}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                title="Go to Main Website"
              >
                <Home className="w-5 h-5" />
              </button>
              <button
                onClick={handleLogout}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                title="Logout"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-1 mt-4 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-t-lg transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-white text-teal-700 font-medium'
                    : 'text-teal-100 hover:bg-white/10'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Period Selector */}
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-800">Dashboard Overview</h2>
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
              >
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="year">This Year</option>
              </select>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-emerald-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Total Sales</p>
                    <p className="text-2xl font-bold text-gray-800">
                      {formatCurrency(dashboardData?.total_sales)}
                    </p>
                  </div>
                  <TrendingUp className="w-10 h-10 text-emerald-500/20" />
                </div>
                <p className="text-xs text-gray-400 mt-2">{dashboardData?.order_count || 0} orders</p>
              </div>

              <div className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-blue-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Purchases</p>
                    <p className="text-2xl font-bold text-gray-800">
                      {formatCurrency(dashboardData?.total_purchases)}
                    </p>
                  </div>
                  <Receipt className="w-10 h-10 text-blue-500/20" />
                </div>
                <p className="text-xs text-gray-400 mt-2">{dashboardData?.purchase_count || 0} bills</p>
              </div>

              <div className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-orange-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Pending Deliveries</p>
                    <p className="text-2xl font-bold text-gray-800">
                      {dashboardData?.pending_deliveries || 0}
                    </p>
                  </div>
                  <Truck className="w-10 h-10 text-orange-500/20" />
                </div>
                <p className="text-xs text-gray-400 mt-2">Awaiting dispatch</p>
              </div>

              <div className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-red-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Low Stock Items</p>
                    <p className="text-2xl font-bold text-gray-800">
                      {dashboardData?.low_stock_items || 0}
                    </p>
                  </div>
                  <AlertTriangle className="w-10 h-10 text-red-500/20" />
                </div>
                <p className="text-xs text-gray-400 mt-2">Need restock</p>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <button
                onClick={() => { fetchProducts(); setShowCreateOrder(true); }}
                className="p-4 bg-gradient-to-r from-teal-500 to-teal-600 rounded-xl shadow-sm hover:shadow-md transition-shadow text-left text-white"
              >
                <Plus className="w-8 h-8 mb-2" />
                <p className="font-medium">Create Order</p>
                <p className="text-sm text-teal-100">New sales order</p>
              </button>
              
              <button
                onClick={() => setActiveTab('orders')}
                className="p-4 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow text-left"
              >
                <ShoppingCart className="w-8 h-8 text-teal-600 mb-2" />
                <p className="font-medium text-gray-800">View Orders</p>
                <p className="text-sm text-gray-500">Manage sales orders</p>
              </button>
              
              <button
                onClick={() => setActiveTab('inventory')}
                className="p-4 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow text-left"
              >
                <Package className="w-8 h-8 text-blue-600 mb-2" />
                <p className="font-medium text-gray-800">Stock Check</p>
                <p className="text-sm text-gray-500">View inventory</p>
              </button>
              
              <button
                onClick={() => setActiveTab('transfers')}
                className="p-4 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow text-left"
              >
                <ArrowRightLeft className="w-8 h-8 text-purple-600 mb-2" />
                <p className="font-medium text-gray-800">Stock Transfer</p>
                <p className="text-sm text-gray-500">Request/receive stock</p>
              </button>
              
              <button
                onClick={() => setActiveTab('reports')}
                className="p-4 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow text-left"
              >
                <BarChart3 className="w-8 h-8 text-emerald-600 mb-2" />
                <p className="font-medium text-gray-800">Reports</p>
                <p className="text-sm text-gray-500">Sales & analytics</p>
              </button>
            </div>
          </div>
        )}

        {/* Orders Tab */}
        {activeTab === 'orders' && (
          <div className="bg-white rounded-xl shadow-sm">
            <div className="p-4 border-b flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-800">Recent Sales Orders</h2>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => { fetchProducts(); setShowCreateOrder(true); }}
                  className="flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  Create Order
                </button>
                <button
                  onClick={fetchOrders}
                  className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
                >
                  <RefreshCw className="w-5 h-5" />
                </button>
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order #</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {orders.map((order) => (
                    <tr key={order.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium text-teal-600">
                        {order.order_number || order.id?.slice(0, 8)}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-800">
                        {order.customer_name || 'N/A'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {formatDate(order.created_at)}
                      </td>
                      <td className="px-4 py-3 text-sm font-medium text-gray-800">
                        {formatCurrency(order.total_amount)}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          order.order_status === 'delivered' ? 'bg-green-100 text-green-700' :
                          order.order_status === 'shipped' ? 'bg-blue-100 text-blue-700' :
                          order.order_status === 'processing' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {order.order_status || 'pending'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {orders.length === 0 && (
                <div className="p-8 text-center text-gray-500">
                  No orders found for this store
                </div>
              )}
            </div>
          </div>
        )}

        {/* Inventory Tab */}
        {activeTab === 'inventory' && (
          <div className="bg-white rounded-xl shadow-sm">
            <div className="p-4 border-b flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-800">Store Inventory</h2>
                <p className="text-sm text-gray-500">
                  {inventory?.summary?.total_products || 0} products | {inventory?.summary?.total_stock || 0} units
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">
                  Stock Value: {formatCurrency(inventory?.summary?.total_stock_value)}
                </span>
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Price</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Qty</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Value</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {inventory?.products?.slice(0, 30).map((item) => (
                    <tr key={item.product_id} className={`hover:bg-gray-50 ${item.is_low_stock ? 'bg-red-50' : ''}`}>
                      <td className="px-4 py-3 text-sm text-gray-800">
                        {item.product_name}
                        {item.is_low_stock && (
                          <span className="ml-2 text-xs text-red-600">(Low Stock)</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">{item.sku}</td>
                      <td className="px-4 py-3 text-sm text-gray-500">{item.category}</td>
                      <td className="px-4 py-3 text-sm text-right text-gray-800">
                        {formatCurrency(item.price)}
                      </td>
                      <td className={`px-4 py-3 text-sm text-right font-medium ${item.is_low_stock ? 'text-red-600' : 'text-gray-800'}`}>
                        {item.quantity}
                      </td>
                      <td className="px-4 py-3 text-sm text-right text-gray-800">
                        {formatCurrency(item.stock_value)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Transfers Tab */}
        {activeTab === 'transfers' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm">
              <div className="p-4 border-b">
                <h2 className="text-lg font-semibold text-gray-800">Stock Transfer Requests</h2>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Transfer #</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">From</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">To</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Items</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {transfers.map((transfer) => (
                      <tr key={transfer.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm font-medium text-teal-600">
                          {transfer.transfer_number}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-800">
                          {transfer.from_store_name}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-800">
                          {transfer.to_store_name}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-500">
                          {transfer.items?.length || 0} items
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-500">
                          {formatDate(transfer.created_at)}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            transfer.status === 'completed' ? 'bg-green-100 text-green-700' :
                            transfer.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                            transfer.status === 'rejected' ? 'bg-red-100 text-red-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {transfer.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                
                {transfers.length === 0 && (
                  <div className="p-8 text-center text-gray-500">
                    No stock transfers found
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* PO Requests Tab */}
        {activeTab === 'po-requests' && (
          <PORequestsTab storeData={storeData} formatCurrency={formatCurrency} />
        )}

        {/* Reports Tab */}
        {activeTab === 'reports' && (
          <div className="space-y-6">
            <div className="grid grid-cols-3 gap-4">
              <button
                onClick={() => fetchReportData('daily')}
                className="p-4 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow text-left"
              >
                <Calendar className="w-8 h-8 text-blue-600 mb-2" />
                <p className="font-medium text-gray-800">Daily Report</p>
                <p className="text-sm text-gray-500">Today's sales breakdown</p>
              </button>
              
              <button
                onClick={() => fetchReportData('monthly')}
                className="p-4 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow text-left"
              >
                <BarChart3 className="w-8 h-8 text-emerald-600 mb-2" />
                <p className="font-medium text-gray-800">Monthly Report</p>
                <p className="text-sm text-gray-500">This month's trend</p>
              </button>
              
              <button
                onClick={() => fetchReportData('item-wise')}
                className="p-4 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow text-left"
              >
                <Package className="w-8 h-8 text-purple-600 mb-2" />
                <p className="font-medium text-gray-800">Item-wise Sales</p>
                <p className="text-sm text-gray-500">Product performance</p>
              </button>
            </div>

            {reportData && (
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">
                  {reportData.type === 'daily' && 'Daily Sales Report'}
                  {reportData.type === 'monthly' && 'Monthly Sales Report'}
                  {reportData.type === 'item-wise' && 'Item-wise Sales Report'}
                </h3>
                
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-500">Total Revenue</p>
                    <p className="text-xl font-bold text-gray-800">
                      {formatCurrency(reportData.data.summary?.total_revenue || reportData.data.summary?.total_sales)}
                    </p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-500">Total Orders</p>
                    <p className="text-xl font-bold text-gray-800">
                      {reportData.data.summary?.total_orders || 0}
                    </p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-500">Avg Order Value</p>
                    <p className="text-xl font-bold text-gray-800">
                      {formatCurrency(reportData.data.summary?.average_order_value || reportData.data.summary?.avg_order_value)}
                    </p>
                  </div>
                </div>

                {reportData.type === 'item-wise' && reportData.data.items && (
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Product</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Qty Sold</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Revenue</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {reportData.data.items.slice(0, 10).map((item, idx) => (
                        <tr key={idx}>
                          <td className="px-4 py-2 text-sm">{item.product_name || item._id}</td>
                          <td className="px-4 py-2 text-sm text-right">{item.quantity_sold}</td>
                          <td className="px-4 py-2 text-sm text-right font-medium">
                            {formatCurrency(item.total_revenue)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Create Order Modal */}
      {showCreateOrder && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b flex items-center justify-between sticky top-0 bg-white">
              <h2 className="text-xl font-bold text-gray-800">Create Sales Order</h2>
              <button onClick={() => setShowCreateOrder(false)} className="p-2 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={handleCreateOrder} className="p-6 space-y-6">
              {/* Customer Details */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-700 mb-3">Customer Details</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Customer Name *</label>
                    <input
                      type="text"
                      value={orderForm.customer_name}
                      onChange={(e) => setOrderForm({...orderForm, customer_name: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone *</label>
                    <input
                      type="tel"
                      value={orderForm.customer_phone}
                      onChange={(e) => setOrderForm({...orderForm, customer_phone: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                      type="email"
                      value={orderForm.customer_email}
                      onChange={(e) => setOrderForm({...orderForm, customer_email: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                    <input
                      type="text"
                      value={orderForm.customer_address}
                      onChange={(e) => setOrderForm({...orderForm, customer_address: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    />
                  </div>
                </div>
              </div>

              {/* Add Products */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-700 mb-3">Add Products</h3>
                <div className="flex gap-3 items-end">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Select Product</label>
                    <select
                      value={selectedProduct?.id || ''}
                      onChange={(e) => {
                        const product = products.find(p => p.id === e.target.value);
                        setSelectedProduct(product || null);
                      }}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    >
                      <option value="">-- Select Product --</option>
                      {products.map(product => (
                        <option key={product.id} value={product.id}>
                          {product.name} - {formatCurrency(product.price)}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="w-24">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Qty</label>
                    <input
                      type="number"
                      min="1"
                      value={quantity}
                      onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    />
                  </div>
                  <button
                    type="button"
                    onClick={addItemToOrder}
                    disabled={!selectedProduct}
                    className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    <Plus className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Order Items */}
              {orderForm.items.length > 0 && (
                <div className="bg-white border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Product</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Price</th>
                        <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Qty</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Subtotal</th>
                        <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {orderForm.items.map((item, index) => (
                        <tr key={index}>
                          <td className="px-4 py-2 text-sm">{item.product_name}</td>
                          <td className="px-4 py-2 text-sm text-right">{formatCurrency(item.price)}</td>
                          <td className="px-4 py-2 text-sm text-center">{item.quantity}</td>
                          <td className="px-4 py-2 text-sm text-right font-medium">{formatCurrency(item.price * item.quantity)}</td>
                          <td className="px-4 py-2 text-center">
                            <button
                              type="button"
                              onClick={() => removeItemFromOrder(index)}
                              className="text-red-500 hover:text-red-700"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot className="bg-teal-50">
                      <tr>
                        <td colSpan="3" className="px-4 py-3 text-right font-semibold text-gray-700">Total:</td>
                        <td className="px-4 py-3 text-right font-bold text-teal-700 text-lg">{formatCurrency(calculateOrderTotal())}</td>
                        <td></td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              )}

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Order Notes</label>
                <textarea
                  value={orderForm.notes}
                  onChange={(e) => setOrderForm({...orderForm, notes: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                  rows={2}
                  placeholder="Any special instructions..."
                ></textarea>
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setShowCreateOrder(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={orderForm.items.length === 0}
                  className="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <Receipt className="w-4 h-4" />
                  Create Order
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default StoreDashboard;
