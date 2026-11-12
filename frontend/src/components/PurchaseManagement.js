import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { ShoppingBag, Plus, Search, Download, Eye, Edit, CheckCircle, XCircle, Clock, Sparkles, FileText } from 'lucide-react';
import DocumentActions from './DocumentActions';
import BulkActionToolbar from './BulkActionToolbar';
import FilterPanel from './FilterPanel';
import { exportPurchasesToExcel } from '../utils/excelExport';
import { TableSkeleton } from './LoadingSkeleton';
import EmptyState from './EmptyState';
import Pagination from './Pagination';
import { showToast, successMessages, errorMessages } from '../utils/toast';
import AIPOGenerator from './AIPOGenerator';


const PurchaseManagement = () => {
  const [purchases, setPurchases] = useState([]);
  const [filteredPurchases, setFilteredPurchases] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedPurchase, setSelectedPurchase] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedItems, setSelectedItems] = useState([]);
  const [filters, setFilters] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [showAIGenerator, setShowAIGenerator] = useState(false);
  const [drafts, setDrafts] = useState([]);
  const [showDraftsTab, setShowDraftsTab] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    po_date: new Date().toISOString().split('T')[0],
    expected_delivery_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    vendor: {
      name: '',
      phone: '',
      email: '',
      gst_number: '',
      address: '',
      city: '',
      state: '',
      pincode: ''
    },
    items: [],
    payment_mode: 'cash',
    discount: 0,
    shipping_charges: 0,
    round_off: 0,
    notes: '',
    created_by: 'admin'
  });
  const [currentItem, setCurrentItem] = useState({
    product_id: '',
    product_name: '',
    hsn_code: '',
    quantity: 1,
    rate: 0,
    discount: 0,
    tax_rate: 18.0
  });
  const [productSearch, setProductSearch] = useState('');
  const [showProductDropdown, setShowProductDropdown] = useState(false);

  useEffect(() => {
    fetchPurchases();
    fetchProducts();
    fetchDrafts();
  }, []);

  const fetchPurchases = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/purchase-orders/?limit=100`);
      const data = await response.json();
      if (data.status === 'success') {
        setPurchases(data.purchase_orders);
      }
    } catch (error) {
      console.error('Failed to fetch purchases:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/products?include_unlisted=true`);
      const data = await response.json();
      // API returns { status: 'success', products: [...] }
      setProducts(data.products || []);
    } catch (error) {
      console.error('Failed to fetch products:', error);
      setProducts([]); // Ensure products is always an array
    }
  };

  const fetchDrafts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/ai-po-generator/drafts`);
      const data = await response.json();
      if (data.status === 'success') {
        setDrafts(data.drafts);
      }
    } catch (error) {
      console.error('Failed to fetch drafts:', error);
    }
  };

  const handleApproveDraft = async (draftId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/ai-po-generator/drafts/${draftId}/approve`, {
        method: 'POST',
      });
      const data = await response.json();
      if (data.status === 'success') {
        showToast.success(successMessages.purchaseOrder.create(data.po_number));
        fetchPurchases();
        fetchDrafts();
      } else {
        showToast.error(errorMessages.purchaseOrder.create);
      }
    } catch (error) {
      console.error('Failed to approve draft:', error);
      showToast.error(errorMessages.purchaseOrder.create);
    }
  };

  const handleDeleteDraft = async (draftId) => {
    if (!window.confirm('Are you sure you want to delete this draft?')) {
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/ai-po-generator/drafts/${draftId}`, {
        method: 'DELETE',
      });
      const data = await response.json();
      if (data.status === 'success') {
        showToast.success('Draft deleted successfully');
        fetchDrafts();
      } else {
        showToast.error('Failed to delete draft');
      }
    } catch (error) {
      console.error('Failed to delete draft:', error);
      showToast.error('Failed to delete draft');
    }
  };

  const handleAIGeneratorClose = () => {
    setShowAIGenerator(false);
    fetchDrafts();
  };

  // Apply filters
  useEffect(() => {
    let filtered = [...purchases];

    // Apply date filter
    if (filters?.dateFrom) {
      filtered = filtered.filter(p => new Date(p.po_date) >= filters.dateFrom);
    }
    if (filters?.dateTo) {
      filtered = filtered.filter(p => new Date(p.po_date) <= filters.dateTo);
    }

    // Apply amount filter
    if (filters?.amountMin) {
      filtered = filtered.filter(p => p.total_amount >= parseFloat(filters.amountMin));
    }
    if (filters?.amountMax) {
      filtered = filtered.filter(p => p.total_amount <= parseFloat(filters.amountMax));
    }

    // Apply status filter
    if (filters?.status && filters.status !== 'All') {
      filtered = filtered.filter(p => p.status?.toLowerCase() === filters.status.toLowerCase());
    }

    // Apply search term
    if (filters?.searchTerm) {
      filtered = filtered.filter(p =>
        p.po_number?.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
        p.vendor_name?.toLowerCase().includes(filters.searchTerm.toLowerCase())
      );
    }

    setFilteredPurchases(filtered);
  }, [purchases, filters]);

  const handleApplyFilters = (newFilters) => {
    setFilters(newFilters);
  };

  const handleClearFilters = () => {
    setFilters(null);
    setFilteredPurchases(purchases);
  };

  // Bulk actions
  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedItems(filteredPurchases.map(p => p.id));
    } else {
      setSelectedItems([]);
    }
  };

  const handleSelectItem = (id) => {
    setSelectedItems(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const handleExportExcel = () => {
    const selectedPurchases = purchases.filter(p => selectedItems.includes(p.id));
    const result = exportPurchasesToExcel(selectedPurchases);
    if (result.success) {
      showToast.success(`Exported ${selectedPurchases.length} purchases to ${result.filename}`);
    } else {
      showToast.error(errorMessages.failed('export'));
    }
  };

  const handleDeleteSelected = async () => {
    if (window.confirm(`Are you sure you want to delete ${selectedItems.length} purchase orders?`)) {
      const toastId = showToast.loading('Deleting purchase orders...');
      try {
        // Delete each selected purchase
        for (const id of selectedItems) {
          await fetch(`${BACKEND_URL}/api/purchases/${id}`, { method: 'DELETE' });
        }
        showToast.dismiss(toastId);
        showToast.success(successMessages.deleted('Purchase orders'));
        setSelectedItems([]);
        fetchPurchases();
      } catch (error) {
        console.error('Delete failed:', error);
        showToast.dismiss(toastId);
        showToast.error(errorMessages.failed('delete purchase orders'));
      }
    }
  };

  const handlePrintSelected = () => {
    alert('Print functionality will open print dialog for selected purchases');
    // Implement print logic here
  };

  const handleProductSelect = (product) => {
    setCurrentItem({
      ...currentItem,
      product_id: product.id,
      product_name: product.name,
      hsn_code: product.hsn_code || '',
      rate: product.price || 0
    });
    setProductSearch(product.name);
    setShowProductDropdown(false);
  };

  const filteredProducts = Array.isArray(products) ? products.filter(p =>
    p.name?.toLowerCase().includes(productSearch.toLowerCase()) ||
    p.brand?.toLowerCase().includes(productSearch.toLowerCase()) ||
    p.model_number?.toLowerCase().includes(productSearch.toLowerCase())
  ) : [];

  const addItemToList = () => {
    if (currentItem.product_name && currentItem.rate > 0 && currentItem.quantity > 0) {
      setFormData({
        ...formData,
        items: [...formData.items, { ...currentItem }]
      });
      setCurrentItem({
        product_id: '',
        product_name: '',
        hsn_code: '',
        quantity: 1,
        rate: 0,
        discount: 0,
        tax_rate: 18.0
      });
      setProductSearch('');
    }
  };

  const removeItem = (index) => {
    const newItems = formData.items.filter((_, i) => i !== index);
    setFormData({ ...formData, items: newItems });
  };

  const calculateSubtotal = () => {
    return formData.items.reduce((sum, item) => {
      const itemSubtotal = item.rate * item.quantity;
      const itemDiscount = (itemSubtotal * item.discount) / 100;
      const taxableAmount = itemSubtotal - itemDiscount;
      const taxAmount = (taxableAmount * item.tax_rate) / 100;
      return sum + taxableAmount + taxAmount;
    }, 0);
  };

  const handleCreatePurchase = async () => {
    const toastId = showToast.loading('Creating purchase order...');
    try {
      const subtotal = calculateSubtotal();
      const purchaseData = {
        ...formData,
        subtotal: subtotal
      };

      const response = await fetch(`${BACKEND_URL}/api/purchases/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(purchaseData)
      });

      const data = await response.json();
      if (data.status === 'success') {
        showToast.dismiss(toastId);
        showToast.success(`Purchase Order Created: ${data.po_number}`);
        setShowCreateModal(false);
        fetchPurchases();
        resetForm();
      } else {
        showToast.dismiss(toastId);
        showToast.error(data.message || 'Failed to create purchase order');
      }
    } catch (error) {
      console.error('Failed to create purchase:', error);
      showToast.dismiss(toastId);
      showToast.error(errorMessages.failed('create purchase order'));
    }
  };

  const resetForm = () => {
    setFormData({
      po_date: new Date().toISOString().split('T')[0],
      expected_delivery_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      vendor: {
        name: '',
        phone: '',
        email: '',
        gst_number: '',
        address: '',
        city: '',
        state: '',
        pincode: ''
      },
      items: [],
      payment_mode: 'cash',
      discount: 0,
      shipping_charges: 0,
      round_off: 0,
      notes: '',
      created_by: 'admin'
    });
  };

  const updatePurchaseStatus = async (purchaseId, newStatus) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/purchases/${purchaseId}/status?status=${newStatus}`, {
        method: 'PUT'
      });
      const data = await response.json();
      if (data.status === 'success') {
        fetchPurchases();
      }
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };

  // Paginate filtered purchases
  const totalPages = Math.ceil(filteredPurchases.length / pageSize);
  const paginatedPurchases = filteredPurchases.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  if (loading) {
    return (
      <div className="p-6">
        <div className="mb-6">
          <div className="h-8 bg-gray-200 rounded w-64 mb-2 animate-pulse"></div>
          <div className="h-4 bg-gray-200 rounded w-96 animate-pulse"></div>
        </div>
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                {['', 'PO Number', 'Vendor', 'Amount', 'Date', 'Status', 'Actions'].map((header, i) => (
                  <th key={i} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              <TableSkeleton rows={5} columns={7} />
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <ShoppingBag className="text-blue-500" />
              Purchase Management
            </h1>
            <p className="text-gray-600 mt-1">Create and manage purchase orders</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setShowAIGenerator(true)}
              className="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 flex items-center gap-2 transition-all shadow-lg hover:shadow-xl"
            >
              <Sparkles size={20} />
              AI Generate PO
            </button>
            {drafts.length > 0 && (
              <button
                onClick={() => setShowDraftsTab(!showDraftsTab)}
                className="px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 flex items-center gap-2 relative"
              >
                <FileText size={20} />
                Draft POs
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center font-bold">
                  {drafts.length}
                </span>
              </button>
            )}
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2"
            >
              <Plus size={20} />
              Create Purchase Order
            </button>
          </div>
        </div>

        {/* Advanced Filters */}
        <FilterPanel
          onApplyFilters={handleApplyFilters}
          onClearFilters={handleClearFilters}
          showDateRange={true}
          showAmountRange={true}
          showStatus={true}
          showPaymentMode={false}
          showSearch={true}
          statusOptions={['All', 'Pending', 'Approved', 'Received', 'Cancelled']}
          searchPlaceholder="Search by PO number or vendor..."
        />

        {/* Bulk Actions */}
        <BulkActionToolbar
          selectedCount={selectedItems.length}
          onExportExcel={handleExportExcel}
          onDelete={handleDeleteSelected}
          onPrint={handlePrintSelected}
          onClear={() => setSelectedItems([])}
          showPrint={true}
        />
      </div>

      {/* Draft POs Section */}
      {showDraftsTab && drafts.length > 0 && (
        <div className="bg-gradient-to-r from-amber-50 to-yellow-50 rounded-lg shadow-lg overflow-hidden border-2 border-amber-200">
          <div className="bg-gradient-to-r from-amber-600 to-yellow-600 px-6 py-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <FileText size={24} />
              AI Generated Draft Purchase Orders ({drafts.length})
            </h2>
            <p className="text-amber-100 text-sm mt-1">Review and approve AI-generated purchase orders</p>
          </div>
          
          <div className="p-6 space-y-4">
            {drafts.map((draft) => (
              <div key={draft.id} className="bg-white rounded-lg border border-amber-200 p-6 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{draft.draft_number}</h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {draft.ai_generated && (
                        <span className="inline-flex items-center gap-1 text-purple-600">
                          <Sparkles size={14} />
                          AI Generated
                        </span>
                      )}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleApproveDraft(draft.id)}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2 transition-colors"
                    >
                      <CheckCircle size={18} />
                      Approve
                    </button>
                    <button
                      onClick={() => handleDeleteDraft(draft.id)}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2 transition-colors"
                    >
                      <XCircle size={18} />
                      Delete
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <p className="text-xs text-gray-500">Vendor</p>
                    <p className="text-sm font-medium text-gray-900">{draft.vendor?.name || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Items</p>
                    <p className="text-sm font-medium text-gray-900">{draft.items?.length || 0} item(s)</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Total Amount</p>
                    <p className="text-sm font-medium text-green-600">₹{draft.total_amount?.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Created</p>
                    <p className="text-sm font-medium text-gray-900">
                      {new Date(draft.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                {draft.items && draft.items.length > 0 && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs font-semibold text-gray-700 mb-2">Items:</p>
                    <div className="space-y-2">
                      {draft.items.map((item, idx) => (
                        <div key={idx} className="flex justify-between items-center text-sm">
                          <span className="text-gray-900">{item.product_name}</span>
                          <span className="text-gray-600">
                            Qty: {item.quantity} × ₹{item.rate?.toLocaleString()} = ₹{(item.quantity * item.rate)?.toLocaleString()}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {draft.original_request && (
                  <div className="mt-4 bg-blue-50 rounded-lg p-3 border border-blue-200">
                    <p className="text-xs font-semibold text-blue-900 mb-1">Original Request:</p>
                    <p className="text-sm text-blue-800 italic">"{draft.original_request}"</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Purchase List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-3 py-3 text-left">
                <input
                  type="checkbox"
                  checked={selectedItems.length === filteredPurchases.length && filteredPurchases.length > 0}
                  onChange={handleSelectAll}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">PO Number</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vendor</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {paginatedPurchases.length === 0 ? (
              <tr>
                <td colSpan="7" className="px-6 py-0">
                  <EmptyState
                    type={filters ? 'search' : 'purchases'}
                    actionLabel={!filters ? "Create Purchase Order" : undefined}
                    onAction={!filters ? () => setShowCreateModal(true) : undefined}
                  />
                </td>
              </tr>
            ) : (
              paginatedPurchases.map((purchase) => (
                <tr key={purchase.id} className={selectedItems.includes(purchase.id) ? 'bg-blue-50' : ''}>
                  <td className="px-3 py-4">
                    <input
                      type="checkbox"
                      checked={selectedItems.includes(purchase.id)}
                      onChange={() => handleSelectItem(purchase.id)}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {purchase.po_number}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {purchase.vendor_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">
                    ₹{purchase.total_amount?.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(purchase.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      purchase.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      purchase.status === 'approved' ? 'bg-blue-100 text-blue-800' :
                      purchase.status === 'received' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {purchase.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => {
                        setSelectedPurchase(purchase);
                        setShowDetailsModal(true);
                      }}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                      title="View"
                    >
                      <Eye size={18} />
                    </button>
                    {(purchase.status === 'pending' || purchase.status === 'draft') && (
                      <button
                        onClick={() => {
                          setSelectedPurchase(purchase);
                          setShowEditModal(true);
                        }}
                        className="text-amber-600 hover:text-amber-900 mr-3"
                        title="Edit"
                      >
                        <Edit size={18} />
                      </button>
                    )}
                    {purchase.status === 'pending' && (
                      <button
                        onClick={() => updatePurchaseStatus(purchase.id, 'approved')}
                        className="text-green-600 hover:text-green-900"
                        title="Approve"
                      >
                        <CheckCircle size={18} />
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
        
        {/* Pagination */}
        {filteredPurchases.length > 0 && (
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={filteredPurchases.length}
            pageSize={pageSize}
            onPageChange={setCurrentPage}
            onPageSizeChange={setPageSize}
            showPageSizeSelector={true}
          />
        )}
      </div>

      {/* Create Purchase Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 my-8">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold">Create Purchase Order</h2>
            </div>
            <div className="p-6 max-h-[70vh] overflow-y-auto">
              {/* PO Details */}
              <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3 text-blue-900">Purchase Order Details</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">PO Number</label>
                    <input
                      type="text"
                      value="Auto-generated on submit"
                      disabled
                      className="px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">PO Date *</label>
                    <input
                      type="date"
                      value={formData.po_date}
                      onChange={(e) => setFormData({ ...formData, po_date: e.target.value })}
                      className="px-3 py-2 border border-gray-300 rounded-lg w-full"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Expected Delivery Date *</label>
                    <input
                      type="date"
                      value={formData.expected_delivery_date}
                      onChange={(e) => setFormData({ ...formData, expected_delivery_date: e.target.value })}
                      className="px-3 py-2 border border-gray-300 rounded-lg w-full"
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Vendor Details */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">Vendor Details</h3>
                <div className="grid grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="Vendor Name *"
                    value={formData.vendor.name}
                    onChange={(e) => setFormData({ ...formData, vendor: { ...formData.vendor, name: e.target.value } })}
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                  />
                  <input
                    type="text"
                    placeholder="Phone *"
                    value={formData.vendor.phone}
                    onChange={(e) => setFormData({ ...formData, vendor: { ...formData.vendor, phone: e.target.value } })}
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                  />
                  <input
                    type="email"
                    placeholder="Email"
                    value={formData.vendor.email}
                    onChange={(e) => setFormData({ ...formData, vendor: { ...formData.vendor, email: e.target.value } })}
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                  />
                  <input
                    type="text"
                    placeholder="GST Number"
                    value={formData.vendor.gst_number}
                    onChange={(e) => setFormData({ ...formData, vendor: { ...formData.vendor, gst_number: e.target.value } })}
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                  />
                  <input
                    type="text"
                    placeholder="Address *"
                    value={formData.vendor.address}
                    onChange={(e) => setFormData({ ...formData, vendor: { ...formData.vendor, address: e.target.value } })}
                    className="px-3 py-2 border border-gray-300 rounded-lg col-span-2"
                  />
                  <input
                    type="text"
                    placeholder="City *"
                    value={formData.vendor.city}
                    onChange={(e) => setFormData({ ...formData, vendor: { ...formData.vendor, city: e.target.value } })}
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                  />
                  <input
                    type="text"
                    placeholder="State *"
                    value={formData.vendor.state}
                    onChange={(e) => setFormData({ ...formData, vendor: { ...formData.vendor, state: e.target.value } })}
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                  />
                  <input
                    type="text"
                    placeholder="Pincode *"
                    value={formData.vendor.pincode}
                    onChange={(e) => setFormData({ ...formData, vendor: { ...formData.vendor, pincode: e.target.value } })}
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>

              {/* Items */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">Add Items</h3>
                <div className="grid grid-cols-6 gap-2 mb-2">
                  {/* Searchable Product Dropdown */}
                  <div className="col-span-2 relative">
                    <input
                      type="text"
                      placeholder="Search product by name, brand, model..."
                      value={productSearch}
                      onChange={(e) => {
                        setProductSearch(e.target.value);
                        setShowProductDropdown(true);
                      }}
                      onFocus={() => setShowProductDropdown(true)}
                      className="px-3 py-2 border border-gray-300 rounded-lg w-full"
                    />
                    {showProductDropdown && productSearch && filteredProducts.length > 0 && (
                      <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                        {filteredProducts.slice(0, 10).map((product) => (
                          <div
                            key={product.id}
                            onClick={() => handleProductSelect(product)}
                            className="px-3 py-2 hover:bg-blue-50 cursor-pointer border-b border-gray-100"
                          >
                            <div className="font-semibold text-sm">{product.name}</div>
                            <div className="text-xs text-gray-600">
                              {product.brand} {product.model_number ? `• ${product.model_number}` : ''} • ₹{product.price}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <input
                    type="text"
                    placeholder="HSN Code"
                    value={currentItem.hsn_code}
                    onChange={(e) => setCurrentItem({ ...currentItem, hsn_code: e.target.value })}
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                  />
                  <input
                    type="number"
                    placeholder="Qty"
                    value={currentItem.quantity}
                    onChange={(e) => setCurrentItem({ ...currentItem, quantity: parseInt(e.target.value) || 0 })}
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                    min="1"
                  />
                  <input
                    type="number"
                    placeholder="Rate"
                    value={currentItem.rate}
                    onChange={(e) => setCurrentItem({ ...currentItem, rate: parseFloat(e.target.value) || 0 })}
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                    min="0"
                    step="0.01"
                  />
                  <button
                    onClick={addItemToList}
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                    disabled={!currentItem.product_name || currentItem.quantity <= 0 || currentItem.rate <= 0}
                  >
                    Add
                  </button>
                </div>
                {currentItem.product_name && (
                  <div className="text-sm text-green-600 mb-2">
                    ✓ Selected: {currentItem.product_name} {currentItem.hsn_code && `(HSN: ${currentItem.hsn_code})`}
                  </div>
                )}

                {/* Items List */}
                {formData.items.length > 0 && (
                  <div className="border border-gray-300 rounded-lg p-4">
                    {formData.items.map((item, index) => (
                      <div key={index} className="flex justify-between items-center mb-2 pb-2 border-b border-gray-200">
                        <div className="flex-1">
                          <span className="font-medium">{item.product_name}</span>
                          <span className="text-gray-500 ml-2">Qty: {item.quantity} × ₹{item.rate}</span>
                        </div>
                        <button
                          onClick={() => removeItem(index)}
                          className="text-red-500 hover:text-red-700"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Payment & Other Details */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <select
                  value={formData.payment_mode}
                  onChange={(e) => setFormData({ ...formData, payment_mode: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="cash">Cash</option>
                  <option value="upi">UPI</option>
                  <option value="bank_transfer">Bank Transfer</option>
                  <option value="cheque">Cheque</option>
                </select>
                <input
                  type="number"
                  placeholder="Shipping Charges"
                  value={formData.shipping_charges}
                  onChange={(e) => setFormData({ ...formData, shipping_charges: parseFloat(e.target.value) || 0 })}
                  className="px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <textarea
                placeholder="Notes"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                rows="3"
              />
            </div>
            <div className="p-6 border-t border-gray-200 flex justify-between items-center">
              <div className="text-lg font-bold">
                Subtotal: ₹{calculateSubtotal().toFixed(2)}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    resetForm();
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreatePurchase}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                >
                  Create Purchase Order
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Details Modal */}
      {showDetailsModal && selectedPurchase && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold">Purchase Order Details</h2>
              <p className="text-gray-600">{selectedPurchase.po_number}</p>
            </div>
            <div className="p-6 max-h-[60vh] overflow-y-auto">
              <div className="mb-4">
                <h3 className="font-semibold mb-2">Vendor Information</h3>
                <p className="text-gray-700">{selectedPurchase.vendor_name}</p>
                <p className="text-gray-600 text-sm">{selectedPurchase.vendor?.phone}</p>
                <p className="text-gray-600 text-sm">{selectedPurchase.vendor?.address}</p>
              </div>
              {selectedPurchase.delivery_location && (
                <div className="mb-4">
                  <h3 className="font-semibold mb-2">Delivery Location</h3>
                  <p className="text-gray-700">{selectedPurchase.delivery_location}</p>
                </div>
              )}
              <div className="mb-4">
                <h3 className="font-semibold mb-2">Items</h3>
                {selectedPurchase.items?.map((item, index) => {
                  const rate = item.rate ?? item.unit_price ?? 0;
                  const lineTotal = item.total ?? (item.quantity * rate);
                  return (
                    <div key={index} className="border-b border-gray-200 py-2">
                      <div className="flex justify-between items-start">
                        <p className="font-medium">{item.product_name}</p>
                        {item.hsn_code && (
                          <span className="text-xs text-gray-500 bg-gray-100 rounded px-2 py-0.5">HSN: {item.hsn_code}</span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600">
                        Qty: {item.quantity} × ₹{rate?.toLocaleString()} = ₹{lineTotal?.toFixed(2)}
                      </p>
                      {(item.taxable_amount != null) && (
                        <div className="grid grid-cols-3 gap-2 text-xs bg-gray-50 rounded p-2 mt-1">
                          <div>
                            <div className="font-medium text-gray-500">Taxable Amt</div>
                            <div className="text-gray-900">₹{item.taxable_amount?.toFixed(2)}</div>
                          </div>
                          <div>
                            <div className="font-medium text-gray-500">CGST @{(item.tax_rate || 0) / 2}%</div>
                            <div className="text-gray-900">₹{item.cgst_amount?.toFixed(2)}</div>
                          </div>
                          <div>
                            <div className="font-medium text-gray-500">SGST @{(item.tax_rate || 0) / 2}%</div>
                            <div className="text-gray-900">₹{item.sgst_amount?.toFixed(2)}</div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
              <div className="border-t pt-4">
                <div className="flex justify-between mb-2">
                  <span>Subtotal:</span>
                  <span>₹{selectedPurchase.subtotal?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span>Tax Total:</span>
                  <span>₹{selectedPurchase.tax_amount?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between font-bold text-lg">
                  <span>Total:</span>
                  <span>₹{selectedPurchase.total_amount?.toFixed(2)}</span>
                </div>
              </div>

              {/* Document Actions */}
              <div className="border-t border-gray-200 pt-4 mt-4">
                <h3 className="font-semibold mb-3">Document Actions</h3>
                <DocumentActions 
                  document={selectedPurchase} 
                  documentType="purchase-order"
                />
              </div>
            </div>
            <div className="p-6 border-t border-gray-200 flex justify-end">
              <button
                onClick={() => setShowDetailsModal(false)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* AI PO Generator Modal */}
      <AIPOGenerator
        isOpen={showAIGenerator}
        onClose={handleAIGeneratorClose}
        onPOGenerated={() => {
          fetchDrafts();
          setShowDraftsTab(true);
        }}
      />
    </div>
  );
};

export default PurchaseManagement;