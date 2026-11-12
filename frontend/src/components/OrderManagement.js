import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { Package, TrendingUp, Clock, CheckCircle, XCircle, Truck, Eye, ArrowLeft, FileText, ShoppingCart, Store, ArrowRight, Trash2, CheckSquare, Square, AlertTriangle, RefreshCw, Download, Mail } from 'lucide-react';

const OrderManagement = () => {
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const [orderTypeFilter, setOrderTypeFilter] = useState('online'); // 'all' | 'online' | 'offline'
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [storeFilter, setStoreFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0, pages: 1 });
  const [loading, setLoading] = useState(true);
  const [stores, setStores] = useState([]);
  const [showConvertModal, setShowConvertModal] = useState(false);
  const [convertType, setConvertType] = useState(''); // 'so' or 'invoice'
  const [selectedStore, setSelectedStore] = useState('');
  const [converting, setConverting] = useState(false);
  const [selectedOrders, setSelectedOrders] = useState([]);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [syncingOrderId, setSyncingOrderId] = useState(null);
  const [syncMessage, setSyncMessage] = useState('');
  const [reconcileRunning, setReconcileRunning] = useState(false);
  const [emailOrder, setEmailOrder] = useState(null);
  const [emailTo, setEmailTo] = useState('');
  const [emailNote, setEmailNote] = useState('');
  const [emailSending, setEmailSending] = useState(false);

  const handleDownloadPdf = (order) => {
    const id = order.order_number || order.id;
    window.open(`${BACKEND_URL}/api/orders/${id}/pdf`, '_blank');
  };

  const handleSendOrderEmail = async () => {
    if (!emailOrder || !emailTo.trim()) return;
    setEmailSending(true);
    try {
      const id = emailOrder.order_number || emailOrder.id;
      const res = await fetch(`${BACKEND_URL}/api/orders/${id}/email-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ to_email: emailTo.trim(), note: emailNote.trim() || null }),
      });
      const data = await res.json();
      if (res.ok) {
        setSyncMessage(`✅ Order PDF emailed to ${emailTo.trim()}`);
        setEmailOrder(null);
        setEmailTo('');
        setEmailNote('');
      } else {
        alert(`Email failed: ${data.detail || res.status}`);
      }
    } catch (e) {
      alert(`Email failed: ${e.message}`);
    } finally {
      setEmailSending(false);
    }
  };

  const handleReconcileAllPending = async () => {
    if (reconcileRunning) return;
    setReconcileRunning(true);
    setSyncMessage('');
    try {
      const res = await fetch(`${BACKEND_URL}/api/pine-labs/admin/reconcile-all-pending?lookback_hours=72`, {
        method: 'POST',
      });
      const data = await res.json();
      if (data.success) {
        setSyncMessage(
          `✅ Refresh done — checked ${data.checked_with_gateway || 0} · updated ${data.updated || 0} · still pending ${data.still_pending || 0}`,
        );
        fetchOrders();
      } else {
        setSyncMessage(`❌ Refresh failed: ${data.message || 'unknown error'}`);
      }
    } catch (e) {
      setSyncMessage(`❌ Refresh failed: ${e.message}`);
    } finally {
      setReconcileRunning(false);
    }
  };

  const handleShiprocketSync = async (order) => {
    const id = order.order_number || order.id;
    if (!id) return;
    if (!window.confirm(`Push order ${id} to Shiprocket now?`)) return;
    setSyncingOrderId(order.id);
    setSyncMessage('');
    try {
      const res = await fetch(`${BACKEND_URL}/api/shipping/sync-order/${encodeURIComponent(id)}`, {
        method: 'POST',
      });
      const data = await res.json();
      if (data.status === 'success') {
        setSyncMessage(`✅ ${id} synced. Shiprocket order #${data.shiprocket_order_id}`);
        fetchOrders();
      } else if (data.status === 'already_synced') {
        setSyncMessage(`ℹ️ ${id} was already synced. Shiprocket #${data.shiprocket_order_id}`);
      } else {
        setSyncMessage(`❌ Sync failed for ${id}: ${data.message || data.detail || 'unknown error'}`);
      }
    } catch (e) {
      setSyncMessage(`❌ Sync failed for ${id}: ${e.message}`);
    } finally {
      setSyncingOrderId(null);
    }
  };

  
  useEffect(() => {
    fetchOrders();
    fetchStats();
    fetchStores();
  }, [filterStatus, orderTypeFilter, dateFrom, dateTo, storeFilter]);

  useEffect(() => {
    setCurrentPage(1);
  }, [filterStatus, orderTypeFilter, dateFrom, dateTo, storeFilter]);

  useEffect(() => {
    fetchOrders();
  }, [currentPage]);

  // Build the order_type query param shared by list + stats endpoints
  const buildOrderTypeParam = () => {
    if (orderTypeFilter === 'all') return '';
    return `order_type=${orderTypeFilter}`;
  };

  const fetchOrders = async () => {
    try {
      const params = new URLSearchParams();
      if (filterStatus !== 'all') params.set('status', filterStatus);
      if (orderTypeFilter !== 'all') params.set('order_type', orderTypeFilter);
      if (dateFrom) params.set('date_from', dateFrom);
      if (dateTo) params.set('date_to', dateTo);
      if (storeFilter) params.set('store_code', storeFilter);
      params.set('page', currentPage);
      params.set('limit', 20);
      const qs = params.toString();
      const url = `${BACKEND_URL}/api/admin/orders/${qs ? '?' + qs : ''}`;

      const response = await fetch(url);
      const data = await response.json();
      setOrders(data.orders || []);
      if (data.pagination) setPagination(data.pagination);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching orders:', error);
      setOrders([]);
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const params = new URLSearchParams();
      if (orderTypeFilter !== 'all') params.set('order_type', orderTypeFilter);
      if (filterStatus !== 'all') params.set('status', filterStatus);
      if (dateFrom) params.set('date_from', dateFrom);
      if (dateTo) params.set('date_to', dateTo);
      if (storeFilter) params.set('store_code', storeFilter);
      const qs = params.toString();
      const response = await fetch(`${BACKEND_URL}/api/admin/orders/stats/summary${qs ? '?' + qs : ''}`);
      const data = await response.json();
      setStats(data.data || data);  // Handle both data.data and direct data
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchStores = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/orders/stores/list`);
      const data = await response.json();
      setStores(data.stores || []);
    } catch (error) {
      console.error('Error fetching stores:', error);
    }
  };

  const openConvertModal = (type) => {
    setConvertType(type);
    setSelectedStore('');
    setShowConvertModal(true);
  };

  const handleConvert = async () => {
    if (!selectedStore) {
      alert('Please select a store');
      return;
    }
    
    setConverting(true);
    try {
      const endpoint = convertType === 'so' 
        ? `${BACKEND_URL}/api/admin/orders/${selectedOrder.id}/convert-to-so?store_code=${selectedStore}`
        : `${BACKEND_URL}/api/admin/orders/${selectedOrder.id}/convert-to-invoice?store_code=${selectedStore}`;
      
      const response = await fetch(endpoint, { method: 'POST' });
      const data = await response.json();
      
      if (data.status === 'success') {
        alert(`✅ ${data.message}\n\nThe ${convertType === 'so' ? 'Sales Order' : 'Invoice'} is now available in the ${selectedStore} store dashboard.`);
        setShowConvertModal(false);
        setSelectedOrder(null);
        fetchOrders();
      } else {
        alert(`Error: ${data.detail || 'Conversion failed'}`);
      }
    } catch (error) {
      console.error('Conversion error:', error);
      alert('Error converting order');
    } finally {
      setConverting(false);
    }
  };

  // Toggle order selection
  const toggleOrderSelection = (orderId) => {
    setSelectedOrders(prev => 
      prev.includes(orderId) 
        ? prev.filter(id => id !== orderId)
        : [...prev, orderId]
    );
  };

  // Select all orders
  const toggleSelectAll = () => {
    if (selectedOrders.length === orders.length) {
      setSelectedOrders([]);
    } else {
      setSelectedOrders(orders.map(o => o.id));
    }
  };

  // Delete selected orders
  const handleDeleteSelected = async () => {
    if (selectedOrders.length === 0) return;
    
    setDeleting(true);
    try {
      let deleted = 0;
      for (const orderId of selectedOrders) {
        const response = await fetch(`${BACKEND_URL}/api/admin/orders/${orderId}`, {
          method: 'DELETE'
        });
        if (response.ok) deleted++;
      }
      
      alert(`✅ Successfully deleted ${deleted} order(s)`);
      setSelectedOrders([]);
      setShowDeleteConfirm(false);
      fetchOrders();
      fetchStats();
    } catch (error) {
      console.error('Delete error:', error);
      alert('Error deleting orders');
    } finally {
      setDeleting(false);
    }
  };

  // Cleanup offline orders
  const handleCleanupOffline = async () => {
    if (!window.confirm('This will remove all offline orders from this list. Continue?')) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/orders/cleanup-offline-orders`, {
        method: 'DELETE'
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        alert(`✅ ${data.message}`);
        fetchOrders();
        fetchStats();
      } else {
        alert(`Error: ${data.detail || 'Cleanup failed'}`);
      }
    } catch (error) {
      console.error('Cleanup error:', error);
      alert('Error cleaning up offline orders');
    }
  };

  const handleExportOrders = (format) => {
    const params = new URLSearchParams();
    if (filterStatus !== 'all') params.set('status', filterStatus);
    if (orderTypeFilter !== 'all') params.set('order_type', orderTypeFilter);
    if (dateFrom) params.set('date_from', dateFrom);
    if (dateTo) params.set('date_to', dateTo);
    if (storeFilter) params.set('store_code', storeFilter);
    params.set('format', format);
    const url = `${BACKEND_URL}/api/admin/orders/export?${params.toString()}`;
    window.open(url, '_blank');
  };

  const updateOrderStatus = async (orderId, newStatus) => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/admin/orders/${orderId}/status?new_status=${newStatus}`,
        { method: 'PUT' }
      );
      
      if (response.ok) {
        // Refresh orders and update selected order
        await fetchOrders();
        setSelectedOrder(prev => ({ ...prev, order_status: newStatus }));
        alert('Order status updated successfully');
      } else {
        alert('Failed to update status');
      }
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Error updating status');
    }
  };

  const markCODAsCollected = async (orderId) => {
    if (!window.confirm('Are you sure you want to mark this COD payment as collected?')) {
      return;
    }
    
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/admin/orders/${orderId}/payment-status?payment_status=completed`,
        { method: 'PUT' }
      );
      
      if (response.ok) {
        // Refresh orders and update selected order
        await fetchOrders();
        setSelectedOrder(prev => ({ ...prev, payment_status: 'completed' }));
        alert('Payment status updated to Completed');
      } else {
        alert('Failed to update payment status');
      }
    } catch (error) {
      console.error('Error updating payment status:', error);
      alert('Error updating payment status');
    }
  };

  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800',
    placed: 'bg-yellow-100 text-yellow-800',
    confirmed: 'bg-blue-100 text-blue-800',
    processing: 'bg-indigo-100 text-indigo-800',
    shipped: 'bg-purple-100 text-purple-800',
    delivered: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
    payment_failed: 'bg-red-100 text-red-800'
  };

  const statusIcons = {
    pending: Clock,
    placed: Clock,
    confirmed: CheckCircle,
    processing: Package,
    shipped: Truck,
    delivered: CheckCircle,
    cancelled: XCircle,
    payment_failed: XCircle
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl">Loading orders...</div>
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
          <h1 className="text-3xl font-bold">Order Management</h1>
          <p className="text-gray-600 mt-2">Manage and track all customer orders</p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-4 md:p-6 min-w-0">
              <h3 className="text-gray-600 text-xs md:text-sm mb-2 truncate">Total Orders</h3>
              <p className="text-xl md:text-3xl font-bold truncate">{stats.total_orders || 0}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4 md:p-6 min-w-0">
              <h3 className="text-gray-600 text-xs md:text-sm mb-2 truncate">Total Revenue</h3>
              <p className="text-xl md:text-3xl font-bold truncate">₹{(stats.total_revenue || 0).toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4 md:p-6 min-w-0">
              <h3 className="text-gray-600 text-xs md:text-sm mb-2 truncate">Avg Order Value</h3>
              <p className="text-xl md:text-3xl font-bold truncate">₹{Math.round(stats.average_order_value || 0).toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4 md:p-6 min-w-0">
              <h3 className="text-gray-600 text-xs md:text-sm mb-2 truncate">Pending Orders</h3>
              <p className="text-xl md:text-3xl font-bold truncate">{stats.status_breakdown?.pending || 0}</p>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6 space-y-4">
          {/* Sales channel filter — Online vs Offline vs Both */}
          <div>
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Sales Channel</div>
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => setOrderTypeFilter('online')}
                data-testid="filter-online-orders"
                className={`px-4 py-2 rounded text-sm ${orderTypeFilter === 'online' ? 'bg-blue-600 text-white' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}
              >
                🌐 Online Sales
              </button>
              <button
                onClick={() => setOrderTypeFilter('offline')}
                data-testid="filter-offline-orders"
                className={`px-4 py-2 rounded text-sm ${orderTypeFilter === 'offline' ? 'bg-orange-600 text-white' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}
              >
                🏪 Offline / Store Sales
              </button>
              <button
                onClick={() => setOrderTypeFilter('all')}
                data-testid="filter-all-channels"
                className={`px-4 py-2 rounded text-sm ${orderTypeFilter === 'all' ? 'bg-gray-800 text-white' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}
              >
                All Channels
              </button>
            </div>
          </div>

          {/* Date range + Store filter */}
          <div>
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Date Range &amp; Store</div>
            <div className="flex gap-4 flex-wrap items-end">
              <div>
                <label className="block text-xs text-gray-500 mb-1">From</label>
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="px-3 py-2 border rounded text-sm"
                  data-testid="filter-date-from"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">To</label>
                <input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="px-3 py-2 border rounded text-sm"
                  data-testid="filter-date-to"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Store</label>
                <select
                  value={storeFilter}
                  onChange={(e) => setStoreFilter(e.target.value)}
                  className="px-3 py-2 border rounded text-sm"
                  data-testid="filter-store"
                >
                  <option value="">All Stores</option>
                  {stores.map(store => (
                    <option key={store.id} value={store.code}>
                      {store.name} ({store.code})
                    </option>
                  ))}
                </select>
              </div>
              {(dateFrom || dateTo || storeFilter) && (
                <button
                  onClick={() => { setDateFrom(''); setDateTo(''); setStoreFilter(''); }}
                  className="px-3 py-2 text-sm text-gray-600 hover:text-gray-900 underline"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          {/* Status filter */}
          <div>
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Order Status</div>
            <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setFilterStatus('all')}
              className={`px-4 py-2 rounded ${filterStatus === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            >
              All Orders
            </button>
            <button
              onClick={() => setFilterStatus('pending')}
              className={`px-4 py-2 rounded ${filterStatus === 'pending' ? 'bg-yellow-600 text-white' : 'bg-gray-200'}`}
            >
              Pending
            </button>
            <button
              onClick={() => setFilterStatus('processing')}
              className={`px-4 py-2 rounded ${filterStatus === 'processing' ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}
            >
              Processing
            </button>
            <button
              onClick={() => setFilterStatus('shipped')}
              className={`px-4 py-2 rounded ${filterStatus === 'shipped' ? 'bg-purple-600 text-white' : 'bg-gray-200'}`}
            >
              Shipped
            </button>
            <button
              onClick={() => setFilterStatus('delivered')}
              className={`px-4 py-2 rounded ${filterStatus === 'delivered' ? 'bg-green-600 text-white' : 'bg-gray-200'}`}
            >
              Delivered
            </button>
            </div>
          </div>
        </div>

        {/* Shiprocket sync toast */}
        {syncMessage && (
          <div
            data-testid="sr-sync-toast"
            className={`mb-4 px-4 py-3 rounded-lg text-sm ${syncMessage.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : syncMessage.startsWith('ℹ️') ? 'bg-blue-50 text-blue-800 border border-blue-200' : 'bg-red-50 text-red-800 border border-red-200'} flex items-center justify-between`}
          >
            <span>{syncMessage}</span>
            <button onClick={() => setSyncMessage('')} className="text-lg leading-none opacity-60 hover:opacity-100">×</button>
          </div>
        )}

        {/* Orders List or Empty State */}
        {orders.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-600 mb-2">
              {orderTypeFilter === 'offline' ? 'No Offline / Store Orders' :
               orderTypeFilter === 'all' ? 'No Orders Yet' :
               'No Online Orders Yet'}
            </h3>
            <p className="text-gray-500">
              {orderTypeFilter === 'offline' ? 'Offline / POS / store sales orders will appear here' :
               orderTypeFilter === 'all' ? 'Online and offline sales will appear here' :
               'Online orders from website, AI chat, or quotations will appear here'}
            </p>
            <button
              onClick={handleCleanupOffline}
              className="mt-4 px-4 py-2 text-sm text-gray-600 hover:text-gray-800 underline"
            >
              Cleanup any remaining offline orders
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow">
            {/* Action Bar */}
            <div className="p-4 border-b flex items-center justify-between bg-gray-50">
              <div className="flex items-center gap-4">
                <button
                  onClick={toggleSelectAll}
                  className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-200 rounded"
                >
                  {selectedOrders.length === orders.length ? (
                    <CheckSquare className="w-4 h-4 text-blue-600" />
                  ) : (
                    <Square className="w-4 h-4" />
                  )}
                  {selectedOrders.length === orders.length ? 'Deselect All' : 'Select All'}
                </button>
                
                {selectedOrders.length > 0 && (
                  <span className="text-sm text-gray-500">
                    {selectedOrders.length} order(s) selected
                  </span>
                )}
              </div>
              
              <div className="flex items-center gap-2">
                {selectedOrders.length > 0 && (
                  <button
                    onClick={() => setShowDeleteConfirm(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete Selected ({selectedOrders.length})
                  </button>
                )}

                {orderTypeFilter === 'online' && (
                  <button
                    onClick={handleReconcileAllPending}
                    disabled={reconcileRunning}
                    className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm disabled:opacity-60"
                    title="Query Pine Labs for all pending prepaid orders and update their status. Auto-runs every 5 min."
                    data-testid="reconcile-pending-btn"
                  >
                    <RefreshCw className={`w-4 h-4 ${reconcileRunning ? 'animate-spin' : ''}`} />
                    {reconcileRunning ? 'Refreshing…' : 'Refresh Payment Status'}
                  </button>
                )}

                <button
                  onClick={() => handleExportOrders('xlsx')}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                  title="Export current filtered orders as Excel"
                >
                  <Download className="w-4 h-4" />
                  Export Excel
                </button>
                <button
                  onClick={() => handleExportOrders('csv')}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm"
                  title="Export current filtered orders as CSV"
                >
                  <Download className="w-4 h-4" />
                  Export CSV
                </button>
                <button
                  onClick={handleCleanupOffline}
                  className="flex items-center gap-2 px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 text-sm"
                  title="Remove any offline orders that may have been mixed in"
                >
                  <AlertTriangle className="w-4 h-4" />
                  Cleanup Offline
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-center text-sm font-medium text-gray-700 w-10">
                      <button onClick={toggleSelectAll}>
                        {selectedOrders.length === orders.length ? (
                          <CheckSquare className="w-5 h-5 text-blue-600" />
                        ) : (
                          <Square className="w-5 h-5 text-gray-400" />
                        )}
                      </button>
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Order ID</th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Customer</th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Date</th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Items</th>
                    <th className="px-6 py-3 text-right text-sm font-medium text-gray-700">Total</th>
                    <th className="px-6 py-3 text-center text-sm font-medium text-gray-700">Status</th>
                    <th className="px-6 py-3 text-center text-sm font-medium text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((order) => {
                    const StatusIcon = statusIcons[order.order_status] || Package;
                    const isSelected = selectedOrders.includes(order.id);
                    return (
                      <tr key={order.id} className={`border-t hover:bg-gray-50 ${isSelected ? 'bg-blue-50' : ''}`}>
                        <td className="px-4 py-4 text-center">
                          <button onClick={() => toggleOrderSelection(order.id)}>
                            {isSelected ? (
                              <CheckSquare className="w-5 h-5 text-blue-600" />
                            ) : (
                              <Square className="w-5 h-5 text-gray-400" />
                            )}
                          </button>
                        </td>
                        <td className="px-6 py-4">
                          <div className="font-mono text-sm">{order.order_number}</div>
                          {order.order_type === 'offline' && (
                            <span className="text-xs px-1.5 py-0.5 bg-gray-200 text-gray-600 rounded">Offline</span>
                          )}
                          {order.converted_to_so && (
                            <span className="text-xs px-1.5 py-0.5 bg-amber-100 text-amber-700 rounded ml-1">→ SO</span>
                          )}
                          {order.converted_to_invoice && (
                            <span className="text-xs px-1.5 py-0.5 bg-green-100 text-green-700 rounded ml-1">→ Invoice</span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <div>
                            <div className="font-medium">{order.customer_details?.name || order.customer_name || 'Guest'}</div>
                            <div className="text-sm text-gray-500">{order.customer_details?.email || order.customer_email || 'N/A'}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm">
                          {new Date(order.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 text-sm">{order.items?.length || 0} items</td>
                        <td className="px-6 py-4 text-right font-semibold">₹{(order.total_amount || 0).toLocaleString()}</td>
                        <td className="px-6 py-4 text-center">
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${statusColors[order.order_status]}`}>
                            <StatusIcon className="w-4 h-4 mr-1" />
                            {order.order_status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <div className="flex items-center justify-center gap-1">
                            <button
                              onClick={() => setSelectedOrder(order)}
                              className="text-blue-600 hover:text-blue-800 p-2"
                              title="View Details"
                              data-testid={`view-order-${order.order_number}`}
                            >
                              <Eye className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => handleDownloadPdf(order)}
                              className="text-gray-600 hover:text-gray-900 p-2"
                              title="Download order PDF"
                              data-testid={`download-pdf-${order.order_number}`}
                            >
                              <Download className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => { setEmailOrder(order); setEmailTo(order.customer_details?.email || order.customer_email || ''); }}
                              className="text-indigo-600 hover:text-indigo-800 p-2"
                              title="Email order PDF to anyone"
                              data-testid={`email-pdf-${order.order_number}`}
                            >
                              <Mail className="w-5 h-5" />
                            </button>
                            {orderTypeFilter === 'online' && (
                              order.shiprocket_order_id ? (
                                <span
                                  className="inline-flex items-center gap-1 text-xs px-2 py-1 bg-emerald-100 text-emerald-700 rounded"
                                  title={`Shiprocket #${order.shiprocket_order_id} · synced ${order.shiprocket_synced_at || ''}`}
                                  data-testid={`sr-synced-${order.order_number}`}
                                >
                                  <Truck className="w-3 h-3" /> Synced
                                </span>
                              ) : (
                                <button
                                  onClick={() => handleShiprocketSync(order)}
                                  disabled={syncingOrderId === order.id}
                                  className="inline-flex items-center gap-1 text-xs px-2 py-1 border border-blue-500 text-blue-700 rounded hover:bg-blue-50 disabled:opacity-50"
                                  title={order.shiprocket_sync_error ? `Previous error: ${order.shiprocket_sync_error}` : 'Push this order to Shiprocket'}
                                  data-testid={`sr-sync-btn-${order.order_number}`}
                                >
                                  {syncingOrderId === order.id ? (
                                    <RefreshCw className="w-3 h-3 animate-spin" />
                                  ) : (
                                    <Truck className="w-3 h-3" />
                                  )}
                                  {order.shiprocket_sync_error ? 'Retry Sync' : 'Sync to Shiprocket'}
                                </button>
                              )
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>

              {/* Pagination Controls */}
              {pagination.pages > 1 && (
                <div className="flex items-center justify-between px-4 py-4 border-t border-gray-200">
                  <div className="text-sm text-gray-600">
                    Showing page {pagination.page} of {pagination.pages} ({pagination.total} total orders)
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage <= 1}
                      className="px-3 py-1.5 rounded text-sm border border-gray-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-100"
                    >
                      Previous
                    </button>
                    <span className="px-3 py-1.5 text-sm font-medium">
                      {currentPage} / {pagination.pages}
                    </span>
                    <button
                      onClick={() => setCurrentPage(p => Math.min(pagination.pages, p + 1))}
                      disabled={currentPage >= pagination.pages}
                      className="px-3 py-1.5 rounded text-sm border border-gray-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-100"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Email Order PDF Modal */}
        {emailOrder && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg w-full max-w-md p-6" data-testid="email-order-modal">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-bold">Email Order Copy</h2>
                <button onClick={() => setEmailOrder(null)} className="text-gray-500 hover:text-gray-700">✕</button>
              </div>
              <p className="text-sm text-gray-600 mb-3">
                Order <span className="font-mono font-semibold">{emailOrder.order_number || emailOrder.id}</span> — PDF will be attached automatically.
              </p>
              <label className="text-xs font-semibold text-gray-500 uppercase">Send To (any email)</label>
              <input
                type="email"
                value={emailTo}
                onChange={(e) => setEmailTo(e.target.value)}
                placeholder="store / customer / warehouse email"
                className="w-full mt-1 mb-3 px-3 py-2.5 border border-gray-300 rounded-lg text-sm"
                data-testid="email-order-to-input"
              />
              <label className="text-xs font-semibold text-gray-500 uppercase">Note (optional)</label>
              <textarea
                value={emailNote}
                onChange={(e) => setEmailNote(e.target.value)}
                rows={2}
                placeholder="e.g., Please arrange dispatch from warehouse"
                className="w-full mt-1 mb-4 px-3 py-2.5 border border-gray-300 rounded-lg text-sm"
                data-testid="email-order-note-input"
              />
              <div className="flex gap-2">
                <button
                  onClick={() => setEmailOrder(null)}
                  className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSendOrderEmail}
                  disabled={emailSending || !emailTo.trim()}
                  className="flex-1 px-4 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 flex items-center justify-center gap-2"
                  data-testid="email-order-send-btn"
                >
                  {emailSending ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Mail className="w-4 h-4" />}
                  {emailSending ? 'Sending...' : 'Send PDF'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Order Details Modal */}
        {selectedOrder && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-screen overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold">Order Details</h2>
                  <button
                    onClick={() => setSelectedOrder(null)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    ✕
                  </button>
                </div>

                {/* Order Info */}
                <div className="grid grid-cols-2 gap-6 mb-6">
                  <div>
                    <h3 className="font-semibold text-lg mb-3 text-gray-800">Customer Information</h3>
                    <div className="space-y-2">
                      <p className="font-medium text-gray-900">{selectedOrder.customer_details?.name || selectedOrder.customer_name || 'N/A'}</p>
                      <p className="text-sm text-gray-600">📧 {selectedOrder.customer_details?.email || selectedOrder.customer_email || 'N/A'}</p>
                      <p className="text-sm text-gray-600">📞 {selectedOrder.customer_details?.phone || selectedOrder.customer_phone || 'N/A'}</p>
                    </div>
                    
                    <h3 className="font-semibold text-lg mt-4 mb-3 text-gray-800">Shipping Address</h3>
                    <div className="text-sm text-gray-600 space-y-1">
                      <p>{selectedOrder.shipping_address?.name || ''}</p>
                      <p>{selectedOrder.shipping_address?.address || selectedOrder.shipping_address?.address_line1 || 'N/A'}</p>
                      <p>{[selectedOrder.shipping_address?.city, selectedOrder.shipping_address?.state, selectedOrder.shipping_address?.pincode].filter(Boolean).join(', ') || ''}</p>
                      {selectedOrder.shipping_address?.phone && <p>📞 {selectedOrder.shipping_address.phone}</p>}
                    </div>
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg mb-3 text-gray-800">Order Information</h3>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Order #:</span> {selectedOrder.order_number}</p>
                      <p><span className="font-medium">Order ID:</span> {selectedOrder.id}</p>
                      <p><span className="font-medium">Date:</span> {new Date(selectedOrder.created_at).toLocaleString()}</p>
                      <p><span className="font-medium">Status:</span> <span className={`px-2 py-1 rounded text-xs ${statusColors[selectedOrder.order_status]}`}>{selectedOrder.order_status}</span></p>
                    </div>
                    
                    <h3 className="font-semibold text-lg mt-4 mb-3 text-gray-800">Payment Information</h3>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Method:</span> {selectedOrder.payment_method?.toUpperCase() || 'N/A'}</p>
                      <p><span className="font-medium">Payment Status:</span> <span className={`px-2 py-1 rounded text-xs ${selectedOrder.payment_status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>{selectedOrder.payment_status || 'pending'}</span></p>
                      <p><span className="font-medium">Total Amount:</span> ₹{(selectedOrder.total_amount || 0).toLocaleString()}</p>
                      
                      {/* COD Payment Collection Button */}
                      {selectedOrder.payment_method === 'cod' && selectedOrder.payment_status !== 'completed' && (
                        <div className="mt-3 pt-3 border-t">
                          <button
                            onClick={() => markCODAsCollected(selectedOrder.id)}
                            className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
                          >
                            💰 Mark COD Payment as Collected
                          </button>
                          <p className="text-xs text-gray-500 mt-1">Click after cash is collected from customer</p>
                        </div>
                      )}
                      
                      {selectedOrder.payment_method === 'cod' && selectedOrder.payment_status === 'completed' && (
                        <div className="mt-3 pt-3 border-t">
                          <p className="text-sm text-green-600 font-medium">✅ COD Payment Collected</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Update Status */}
                <div className="mb-6 p-4 bg-gray-50 rounded">
                  <h3 className="font-semibold mb-2">Update Order Status</h3>
                  <select
                    value={selectedOrder.order_status}
                    onChange={(e) => updateOrderStatus(selectedOrder.id, e.target.value)}
                    className="w-full p-2 border rounded"
                  >
                    <option value="pending">Pending</option>
                    <option value="confirmed">Confirmed</option>
                    <option value="processing">Processing</option>
                    <option value="shipped">Shipped</option>
                    <option value="delivered">Delivered</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>

                {/* Order Items */}
                <div className="mb-6">
                  <h3 className="font-semibold text-lg mb-3 text-gray-800">Order Items</h3>
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left">Product</th>
                        <th className="px-4 py-2 text-right">Qty</th>
                        <th className="px-4 py-2 text-right">Price</th>
                        <th className="px-4 py-2 text-right">Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedOrder.items?.map((item, index) => (
                        <tr key={index} className="border-t">
                          <td className="px-4 py-2">{item.product_name}</td>
                          <td className="px-4 py-2 text-right">{item.quantity}</td>
                          <td className="px-4 py-2 text-right">₹{(item.price || 0).toLocaleString()}</td>
                          <td className="px-4 py-2 text-right">₹{(item.total || item.price * item.quantity || 0).toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  
                  {/* Order Summary */}
                  <div className="mt-4 border-t pt-4 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Subtotal:</span>
                      <span>₹{(selectedOrder.subtotal || 0).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Tax (18%):</span>
                      <span>₹{(selectedOrder.tax_amount || 0).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Shipping:</span>
                      <span>₹{(selectedOrder.shipping_cost || 0).toLocaleString()}</span>
                    </div>
                    {selectedOrder.discount_amount > 0 && (
                      <div className="flex justify-between text-sm text-green-600">
                        <span>Discount:</span>
                        <span>-₹{(selectedOrder.discount_amount || 0).toLocaleString()}</span>
                      </div>
                    )}
                    <div className="flex justify-between font-bold text-lg border-t pt-2">
                      <span>Total:</span>
                      <span>₹{(selectedOrder.total_amount || 0).toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                {/* Convert to SO/Invoice Section */}
                {!selectedOrder.converted_to_so && !selectedOrder.converted_to_invoice && (
                  <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <h3 className="font-semibold text-blue-800 mb-3 flex items-center gap-2">
                      <ArrowRight className="w-5 h-5" />
                      Process Order
                    </h3>
                    <p className="text-sm text-blue-600 mb-4">
                      Convert this online order to a Sales Order or Invoice for store fulfillment:
                    </p>
                    <div className="flex gap-3">
                      <button
                        onClick={() => openConvertModal('so')}
                        className="flex-1 px-4 py-3 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors font-medium flex items-center justify-center gap-2"
                      >
                        <ShoppingCart className="w-5 h-5" />
                        Convert to Sales Order
                        <span className="text-xs opacity-75">(Large Items)</span>
                      </button>
                      <button
                        onClick={() => openConvertModal('invoice')}
                        className="flex-1 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium flex items-center justify-center gap-2"
                      >
                        <FileText className="w-5 h-5" />
                        Convert to Invoice
                        <span className="text-xs opacity-75">(Direct Dispatch)</span>
                      </button>
                    </div>
                  </div>
                )}

                {/* Already Converted Badge */}
                {(selectedOrder.converted_to_so || selectedOrder.converted_to_invoice) && (
                  <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
                    <div className="flex items-center gap-2 text-green-700">
                      <CheckCircle className="w-5 h-5" />
                      <span className="font-medium">
                        {selectedOrder.converted_to_so 
                          ? `Converted to SO: ${selectedOrder.converted_so_number}` 
                          : `Converted to Invoice: ${selectedOrder.converted_invoice_number}`}
                      </span>
                      <span className="text-sm text-green-600">
                        (Store: {selectedOrder.converted_to_store})
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Convert Modal */}
        {showConvertModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Store className="w-6 h-6 text-blue-600" />
                Convert to {convertType === 'so' ? 'Sales Order' : 'Invoice'}
              </h2>
              
              <p className="text-gray-600 mb-4">
                Select the store that will fulfill this order:
              </p>
              
              <select
                value={selectedStore}
                onChange={(e) => setSelectedStore(e.target.value)}
                className="w-full p-3 border rounded-lg mb-4 text-lg"
              >
                <option value="">-- Select Store --</option>
                {stores.map(store => (
                  <option key={store.id} value={store.code}>
                    {store.name} ({store.code})
                  </option>
                ))}
              </select>
              
              <div className="bg-gray-50 rounded-lg p-3 mb-4 text-sm">
                <p className="font-medium text-gray-700">What happens next:</p>
                <ul className="mt-2 space-y-1 text-gray-600">
                  {convertType === 'so' ? (
                    <>
                      <li>• A Sales Order will be created in the selected store</li>
                      <li>• Store manager can then convert it to Invoice when ready</li>
                      <li>• Best for large items requiring delivery scheduling</li>
                    </>
                  ) : (
                    <>
                      <li>• An Invoice will be created in the selected store</li>
                      <li>• Ready for immediate dispatch/delivery assignment</li>
                      <li>• Best for small items or immediate fulfillment</li>
                    </>
                  )}
                </ul>
              </div>
              
              <div className="flex gap-3">
                <button
                  onClick={() => setShowConvertModal(false)}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                  disabled={converting}
                >
                  Cancel
                </button>
                <button
                  onClick={handleConvert}
                  disabled={!selectedStore || converting}
                  className={`flex-1 px-4 py-2 rounded-lg text-white font-medium ${
                    convertType === 'so' ? 'bg-amber-500 hover:bg-amber-600' : 'bg-green-600 hover:bg-green-700'
                  } disabled:opacity-50`}
                >
                  {converting ? 'Converting...' : `Create ${convertType === 'so' ? 'Sales Order' : 'Invoice'}`}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-red-100 rounded-full">
                  <Trash2 className="w-6 h-6 text-red-600" />
                </div>
                <h2 className="text-xl font-bold text-gray-900">Delete Orders</h2>
              </div>
              
              <p className="text-gray-600 mb-4">
                Are you sure you want to delete <strong>{selectedOrders.length}</strong> order(s)?
                This action cannot be undone.
              </p>
              
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                <p className="text-sm text-red-700 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" />
                  Warning: Deleted orders cannot be recovered.
                </p>
              </div>
              
              <div className="flex gap-3">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                  disabled={deleting}
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteSelected}
                  disabled={deleting}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                >
                  {deleting ? 'Deleting...' : `Delete ${selectedOrders.length} Order(s)`}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OrderManagement;
