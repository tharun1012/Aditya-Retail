import React, { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { 
  FileText, Search, Filter, Download, Eye, RefreshCw, 
  Calendar, IndianRupee, User, ChevronLeft, ChevronRight,
  X, Package, CheckCircle, Clock, AlertCircle, ArrowLeft,
  Send, Printer, Edit, Store, FileCheck2, Loader2
} from 'lucide-react';
import DocumentActions from './DocumentActions';

const SalesOrderList = ({ storeCode = null }) => {
  const navigate = useNavigate();
  const [salesOrders, setSalesOrders] = useState([]);
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState(storeCode || 'all');
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [converting, setConverting] = useState(false);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 100,
    total: 0,
    pages: 0
  });

  // Fetch list of stores once (only when not scoped to a single store via prop)
  useEffect(() => {
    if (storeCode) return; // store-scoped view (warehouse staff), no store filter needed
    (async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/invoices/offline/stores`);
        const data = await res.json();
        if (data.status === 'success' && Array.isArray(data.stores)) {
          setStores(data.stores);
        }
      } catch (e) {
        console.error('Failed to fetch stores:', e);
      }
    })();
  }, [storeCode]);

  // Get logged-in admin name for "converted_by" audit trail
  const getAdminIdentity = () => {
    try {
      const stored = localStorage.getItem('adminUser') || localStorage.getItem('user');
      if (stored) {
        const u = JSON.parse(stored);
        return u?.name || u?.email || u?.first_name || 'Super Admin';
      }
    } catch { /* ignore */ }
    return 'Super Admin';
  };

  // Convert a single SO to Invoice
  const handleConvertToInvoice = async (orderIds, sourceLabel = '') => {
    if (!orderIds || orderIds.length === 0) return;
    const msg = orderIds.length === 1
      ? `Convert this Sales Order to an Invoice?\n\nThis will create a new Invoice document and mark the SO as completed.`
      : `Convert ${orderIds.length} Sales Orders to Invoices?\n\nThis will create new Invoice documents for each selected SO.`;
    if (!window.confirm(msg)) return;

    setConverting(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/invoices/offline/sales-orders/convert-to-invoice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sales_order_ids: orderIds,
          converted_by: getAdminIdentity(),
        }),
      });
      const data = await response.json();
      if (response.ok && data.status === 'success') {
        const created = data.converted_orders || data.invoices || [];
        const failed = data.failed_conversions || [];
        let summary = `✅ Converted: ${data.converted_count || created.length}`;
        if (created.length > 0) {
          summary += `\n\nNew Invoices:\n${created.map(c => `• ${c.invoice_number || c.new_invoice_number || c.id}`).slice(0, 5).join('\n')}`;
        }
        if (failed.length > 0) {
          summary += `\n\n⚠️ Failed: ${failed.length}\n${failed.slice(0, 3).map(f => `• ${f.id}: ${f.reason}`).join('\n')}`;
        }
        alert(summary);
        setSelectedIds(new Set());
        fetchSalesOrders();
      } else {
        alert(`Conversion failed: ${data.detail || data.message || 'Unknown error'}`);
      }
    } catch (e) {
      alert(`Error: ${e.message}`);
    } finally {
      setConverting(false);
    }
  };

  const toggleSelectOne = (orderId, checked) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (checked) next.add(orderId); else next.delete(orderId);
      return next;
    });
  };

  const toggleSelectAll = (checked) => {
    if (checked) {
      const convertibleIds = salesOrders
        .filter(o => ['pending_delivery', 'partially_delivered'].includes(o.status))
        .map(o => o.id);
      setSelectedIds(new Set(convertibleIds));
    } else {
      setSelectedIds(new Set());
    }
  };

  const fetchSalesOrders = useCallback(async () => {
    setLoading(true);
    try {
      // If component is forced into single-store mode (via prop), use that.
      // Otherwise, honour the dropdown filter (which can be 'all' or a specific store_code).
      const effectiveStoreCode = storeCode || (selectedStore !== 'all' ? selectedStore : null);

      const params = new URLSearchParams({
        page: pagination.page,
        limit: pagination.limit,
        document_type: 'sales_order',
        ...(searchTerm && { search: searchTerm }),
        ...(effectiveStoreCode && { store_code: effectiveStoreCode }),
        ...(dateRange.start && { from_date: dateRange.start }),
        ...(dateRange.end && { to_date: dateRange.end })
      });

      const response = await fetch(`${BACKEND_URL}/api/invoices/offline/?${params}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setSalesOrders(data.invoices || []);
        setPagination(prev => ({
          ...prev,
          total: data.total || 0,
          pages: data.pages || 1
        }));
      }
    } catch (error) {
      console.error('Error fetching sales orders:', error);
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.limit, searchTerm, storeCode, selectedStore, dateRange]);

  useEffect(() => {
    fetchSalesOrders();
  }, [fetchSalesOrders]);

  const getStatusBadge = (status) => {
    const badges = {
      pending_delivery: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
      delivered: 'bg-blue-100 text-blue-800'
    };
    return badges[status] || 'bg-gray-100 text-gray-800';
  };

  const getPaymentStatusBadge = (status) => {
    const badges = {
      paid: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      partial: 'bg-orange-100 text-orange-800'
    };
    return badges[status] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    try {
      return new Date(dateStr).toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      });
    } catch {
      return dateStr;
    }
  };

  const formatCurrency = (amount) => {
    if (!amount && amount !== 0) return '₹0';
    return `₹${Number(amount).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
  };

  const handleViewDetails = (order) => {
    setSelectedOrder(order);
    setShowDetailsModal(true);
  };

  // Print order via PDF
  const handlePrintOrder = async () => {
    if (!selectedOrder) return;
    
    const orderId = selectedOrder.id || selectedOrder.invoice_number;
    const printUrl = `${BACKEND_URL}/api/invoices/${orderId}/pdf`;
    
    try {
      const response = await fetch(printUrl);
      if (response.ok) {
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        const printWindow = window.open(blobUrl, '_blank');
        if (printWindow) {
          printWindow.onload = () => {
            setTimeout(() => {
              printWindow.print();
            }, 500);
          };
        }
      } else {
        window.open(printUrl, '_blank');
      }
    } catch (error) {
      console.error('Print error:', error);
      window.open(printUrl, '_blank');
    }
  };

  // Send via WhatsApp
  const handleSendWhatsApp = (order) => {
    const phone = order.customer?.phone;
    if (!phone) {
      alert('Customer phone number not available');
      return;
    }
    
    let formattedPhone = phone.replace(/\D/g, '');
    if (formattedPhone.length === 10) {
      formattedPhone = '91' + formattedPhone;
    }
    
    const message = encodeURIComponent(
      `Dear ${order.customer?.name},\n\n` +
      `Thank you for your order!\n\n` +
      `Sales Order: ${order.invoice_number}\n` +
      `Amount: ₹${Number(order.total_amount).toLocaleString('en-IN')}\n\n` +
      `We will contact you soon for delivery.\n\n` +
      `- Aditya Retail`
    );
    
    window.open(`https://wa.me/${formattedPhone}?text=${message}`, '_blank');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6" data-testid="sales-order-list">
      {/* Back Button */}
      {!storeCode && (
        <button
          onClick={() => navigate('/admin')}
          className="flex items-center px-4 py-2 mb-6 text-gray-700 bg-white hover:bg-gray-100 rounded-lg transition-all border border-gray-300 shadow-sm"
          data-testid="back-to-dashboard-btn"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          <span className="font-medium">Back to Dashboard</span>
        </button>
      )}

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Package className="w-7 h-7 text-blue-600" />
          Sales Orders
        </h1>
        <p className="text-gray-600 mt-1">Manage and track all sales orders</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl shadow-sm p-4 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Sales Orders</p>
              <p className="text-2xl font-bold text-gray-900">{pagination.total}</p>
            </div>
            <Package className="w-10 h-10 text-blue-100" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Value</p>
              <p className="text-2xl font-bold text-green-600">
                {formatCurrency(salesOrders.reduce((sum, o) => sum + (o.total_amount || 0), 0))}
              </p>
            </div>
            <IndianRupee className="w-10 h-10 text-green-100" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border-l-4 border-yellow-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Pending Delivery</p>
              <p className="text-2xl font-bold text-yellow-600">
                {salesOrders.filter(o => o.status === 'pending_delivery').length}
              </p>
            </div>
            <Clock className="w-10 h-10 text-yellow-100" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Completed</p>
              <p className="text-2xl font-bold text-purple-600">
                {salesOrders.filter(o => o.status === 'completed').length}
              </p>
            </div>
            <CheckCircle className="w-10 h-10 text-purple-100" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search by SO no, customer..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                data-testid="search-orders"
              />
            </div>
          </div>
          {/* Store Filter (only shown in admin context, not when viewed inside a single store) */}
          {!storeCode && (
            <div className="flex items-center gap-2 min-w-[220px]">
              <Store className="w-4 h-4 text-gray-400" />
              <select
                value={selectedStore}
                onChange={(e) => {
                  setSelectedStore(e.target.value);
                  setPagination(prev => ({ ...prev, page: 1 }));
                }}
                className="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 text-sm bg-white"
                data-testid="store-filter"
              >
                <option value="all">All Stores ({stores.length})</option>
                {stores.map((s) => (
                  <option key={s.code} value={s.code}>
                    {s.code} — {s.name}
                  </option>
                ))}
              </select>
            </div>
          )}
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-gray-400" />
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
              className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <span className="text-gray-400">to</span>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
              className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            onClick={fetchSalesOrders}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            data-testid="refresh-orders"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Bulk Action Bar — shows when SOs are selected */}
      {selectedIds.size > 0 && (
        <div className="bg-purple-50 border-2 border-purple-300 rounded-xl px-4 py-3 mb-4 flex items-center justify-between" data-testid="bulk-action-bar">
          <div className="flex items-center gap-2 text-sm text-purple-900 font-medium">
            <FileCheck2 className="w-5 h-5" />
            {selectedIds.size} Sales Order{selectedIds.size > 1 ? 's' : ''} selected
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSelectedIds(new Set())}
              className="px-3 py-2 text-sm text-purple-700 hover:bg-purple-100 rounded-lg"
              data-testid="clear-selection-btn"
            >
              Clear
            </button>
            <button
              onClick={() => handleConvertToInvoice([...selectedIds])}
              disabled={converting}
              className="px-4 py-2 text-sm bg-purple-600 hover:bg-purple-700 disabled:opacity-60 text-white rounded-lg font-semibold flex items-center gap-2"
              data-testid="bulk-convert-btn"
            >
              {converting ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileCheck2 className="w-4 h-4" />}
              Convert {selectedIds.size} to Invoice
            </button>
          </div>
        </div>
      )}

      {/* Orders Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : salesOrders.length === 0 ? (
          <div className="text-center py-12">
            <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900">No sales orders found</h3>
            <p className="text-gray-500">Create a new sales order to get started</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full" data-testid="orders-table">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left">
                      <input
                        type="checkbox"
                        onChange={(e) => toggleSelectAll(e.target.checked)}
                        checked={salesOrders.filter(o => ['pending_delivery', 'partially_delivered'].includes(o.status)).length > 0 &&
                                 salesOrders.filter(o => ['pending_delivery', 'partially_delivered'].includes(o.status)).every(o => selectedIds.has(o.id))}
                        title="Select all pending SOs on this page"
                        className="w-4 h-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500 cursor-pointer"
                        data-testid="select-all-checkbox"
                      />
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SO Number</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                    {!storeCode && (
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Store</th>
                    )}
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payment</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Source</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {salesOrders.map((order, idx) => {
                    const isPending = ['pending_delivery', 'partially_delivered'].includes(order.status);
                    const isSelected = selectedIds.has(order.id);
                    return (
                    <tr key={order.id || idx} className={`hover:bg-gray-50 ${isSelected ? 'bg-purple-50' : ''}`}>
                      <td className="px-4 py-4">
                        {isPending ? (
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={(e) => toggleSelectOne(order.id, e.target.checked)}
                            className="w-4 h-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500 cursor-pointer"
                            data-testid={`select-order-${idx}`}
                          />
                        ) : (
                          <span className="w-4 h-4 inline-block" />
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="font-medium text-blue-600">{order.invoice_number || '-'}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(order.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <User className="w-4 h-4 text-gray-400 mr-2" />
                          <div>
                            <div className="text-sm font-medium text-gray-900">{order.customer?.name || '-'}</div>
                            <div className="text-xs text-gray-500">{order.customer?.phone}</div>
                          </div>
                        </div>
                      </td>
                      {!storeCode && (
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-1">
                            <Store className="w-4 h-4 text-gray-400" />
                            <span className="text-sm text-gray-600">{order.store_details?.name || order.store_code}</span>
                          </div>
                        </td>
                      )}
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-semibold text-gray-900">{formatCurrency(order.total_amount)}</div>
                        {order.tax_total > 0 && (
                          <div className="text-xs text-gray-500">Tax: {formatCurrency(order.tax_total)}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-xs font-semibold rounded-full px-3 py-1 ${getStatusBadge(order.status)}`}>
                          {order.status?.replace('_', ' ') || 'N/A'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-xs font-semibold rounded-full px-3 py-1 ${getPaymentStatusBadge(order.payment_status)}`}>
                          {order.payment_status || 'pending'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-xs text-gray-600 bg-gray-100 px-2 py-1 rounded">
                          {order.order_source?.replace('_', ' ') || '-'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-1">
                          {isPending && (
                            <button
                              onClick={() => handleConvertToInvoice([order.id])}
                              disabled={converting}
                              className="p-2 text-purple-600 hover:bg-purple-50 rounded-lg transition-colors disabled:opacity-50"
                              title="Convert SO to Invoice"
                              data-testid={`convert-order-${idx}`}
                            >
                              <FileCheck2 className="w-5 h-5" />
                            </button>
                          )}
                          <button
                            onClick={() => handleViewDetails(order)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="View Details"
                            data-testid={`view-order-${idx}`}
                          >
                            <Eye className="w-5 h-5" />
                          </button>
                          <button
                            onClick={() => navigate(`/admin/sales-orders/edit/${order.id}`)}
                            className="p-2 text-amber-600 hover:bg-amber-50 rounded-lg transition-colors"
                            title="Edit Order"
                            data-testid={`edit-order-${idx}`}
                          >
                            <Edit className="w-5 h-5" />
                          </button>
                          <button
                            onClick={() => handleSendWhatsApp(order)}
                            className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                            title="Send via WhatsApp"
                          >
                            <Send className="w-5 h-5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-6 py-4 border-t flex items-center justify-between">
              <div className="text-sm text-gray-500">
                Showing {((pagination.page - 1) * pagination.limit) + 1} to {Math.min(pagination.page * pagination.limit, pagination.total)} of {pagination.total} orders
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                  disabled={pagination.page === 1}
                  className="p-2 rounded-lg border hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <span className="px-4 py-2 bg-blue-50 text-blue-600 rounded-lg font-medium">
                  {pagination.page}
                </span>
                <button
                  onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                  disabled={pagination.page >= pagination.pages}
                  className="p-2 rounded-lg border hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Order Details Modal */}
      {showDetailsModal && selectedOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-3xl max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b flex items-center justify-between bg-gradient-to-r from-blue-600 to-blue-700 text-white">
              <h2 className="text-xl font-bold flex items-center gap-2">
                <Package className="w-6 h-6" />
                Sales Order - {selectedOrder.invoice_number}
              </h2>
              <button 
                onClick={() => setShowDetailsModal(false)}
                className="p-2 hover:bg-white/20 rounded-full transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div id="order-print-content" className="p-6 overflow-y-auto max-h-[70vh]">
              {/* Store & Order Info */}
              <div className="grid grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Store Details</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="font-medium text-gray-900">{selectedOrder.store_details?.name}</p>
                    <p className="text-sm text-gray-600">{selectedOrder.store_details?.address}</p>
                    <p className="text-sm text-gray-600">{selectedOrder.store_details?.phone}</p>
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Order Info</h3>
                  <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">SO Number:</span>
                      <span className="font-medium">{selectedOrder.invoice_number}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Date:</span>
                      <span className="font-medium">{formatDate(selectedOrder.created_at)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Created By:</span>
                      <span className="font-medium">{selectedOrder.created_by}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Source:</span>
                      <span className="font-medium">{selectedOrder.order_source?.replace('_', ' ') || '-'}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Customer Info */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Customer Details</h3>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="font-medium text-gray-900">{selectedOrder.customer?.name}</p>
                      <p className="text-sm text-gray-600">{selectedOrder.customer?.phone}</p>
                      {selectedOrder.customer?.email && (
                        <p className="text-sm text-gray-600">{selectedOrder.customer?.email}</p>
                      )}
                      {selectedOrder.customer?.gst_number && (
                        <p className="text-sm text-blue-600 font-medium mt-1">GSTIN: {selectedOrder.customer?.gst_number}</p>
                      )}
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">{selectedOrder.customer?.address}</p>
                      <p className="text-sm text-gray-600">
                        {selectedOrder.customer?.city}, {selectedOrder.customer?.state} - {selectedOrder.customer?.pincode}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Items Table */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Items</h3>
                <div className="overflow-x-auto border rounded-lg">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left">Item</th>
                        <th className="px-4 py-2 text-left">HSN</th>
                        <th className="px-4 py-2 text-right">Qty</th>
                        <th className="px-4 py-2 text-right">Rate</th>
                        <th className="px-4 py-2 text-right">GST</th>
                        <th className="px-4 py-2 text-right">Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedOrder.items?.map((item, idx) => (
                        <tr key={idx} className="border-t">
                          <td className="px-4 py-2 font-medium">{item.product_name}</td>
                          <td className="px-4 py-2 text-gray-600">{item.hsn_code}</td>
                          <td className="px-4 py-2 text-right">{item.quantity}</td>
                          <td className="px-4 py-2 text-right">{formatCurrency(item.rate)}</td>
                          <td className="px-4 py-2 text-right">{item.tax_rate}%</td>
                          <td className="px-4 py-2 text-right font-medium">{formatCurrency(item.total)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Totals */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Taxable Amount:</span>
                    <span>{formatCurrency(selectedOrder.subtotal)}</span>
                  </div>
                  <div className="flex justify-between text-gray-600">
                    <span>CGST:</span>
                    <span>{formatCurrency(selectedOrder.cgst_total || selectedOrder.tax_total / 2)}</span>
                  </div>
                  <div className="flex justify-between text-gray-600">
                    <span>SGST:</span>
                    <span>{formatCurrency(selectedOrder.sgst_total || selectedOrder.tax_total / 2)}</span>
                  </div>
                  {selectedOrder.discount_amount > 0 && (
                    <div className="flex justify-between text-green-600">
                      <span>Discount:</span>
                      <span>-{formatCurrency(selectedOrder.discount_amount)}</span>
                    </div>
                  )}
                  {selectedOrder.delivery_charges > 0 && (
                    <div className="flex justify-between">
                      <span>Delivery:</span>
                      <span>{formatCurrency(selectedOrder.delivery_charges)}</span>
                    </div>
                  )}
                  <div className="flex justify-between font-bold text-lg pt-2 border-t">
                    <span>Grand Total:</span>
                    <span className="text-green-600">{formatCurrency(selectedOrder.total_amount)}</span>
                  </div>
                </div>
              </div>

              {/* Payment Details */}
              {selectedOrder.payment_details && (
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <h3 className="text-sm font-medium text-blue-800 mb-2">Payment Details</h3>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    {selectedOrder.payment_details.transaction_reference && (
                      <div>
                        <span className="text-gray-600">Reference:</span>
                        <span className="ml-2 font-medium">{selectedOrder.payment_details.transaction_reference}</span>
                      </div>
                    )}
                    {selectedOrder.payment_details.bank_name && (
                      <div>
                        <span className="text-gray-600">Bank/App:</span>
                        <span className="ml-2 font-medium">{selectedOrder.payment_details.bank_name}</span>
                      </div>
                    )}
                    {selectedOrder.payment_details.amount_paid && (
                      <div>
                        <span className="text-gray-600">Amount Paid:</span>
                        <span className="ml-2 font-medium">{formatCurrency(selectedOrder.payment_details.amount_paid)}</span>
                      </div>
                    )}
                    {selectedOrder.payment_details.is_advance && (
                      <div className="col-span-2">
                        <span className="bg-orange-100 text-orange-700 px-2 py-1 rounded text-xs font-medium">
                          Advance Payment - Balance Due: {formatCurrency(selectedOrder.total_amount - (selectedOrder.payment_details.advance_amount || 0))}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Document Actions */}
              <div className="mt-4 border-t pt-4">
                <h3 className="text-sm font-medium text-gray-500 mb-3">Document Actions</h3>
                <DocumentActions 
                  document={selectedOrder} 
                  documentType="invoice"
                />
              </div>
            </div>

            <div className="p-6 border-t bg-gray-50 flex justify-between">
              <button
                onClick={() => setShowDetailsModal(false)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Close
              </button>
              <div className="flex gap-3">
                <button
                  onClick={() => handleSendWhatsApp(selectedOrder)}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  WhatsApp
                </button>
                <button
                  onClick={handlePrintOrder}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center gap-2"
                >
                  <Printer className="w-4 h-4" />
                  Print
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SalesOrderList;
