import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { 
  FileText, Plus, Search, ArrowLeft, Eye, Edit, XCircle, 
  ArrowRight, Calendar, User, Phone, Mail, Package, 
  CheckCircle, Clock, AlertCircle, Link2, ChevronDown, ChevronUp
} from 'lucide-react';

const CustomerPOManagement = () => {
  const navigate = useNavigate();
  const [customerPOs, setCustomerPOs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedPO, setSelectedPO] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [message, setMessage] = useState({ type: '', text: '' });
  const [quotations, setQuotations] = useState([]);
  const [showQuotationSearch, setShowQuotationSearch] = useState(false);
  const [quotationSearchTerm, setQuotationSearchTerm] = useState('');
  
  const storeCode = localStorage.getItem('store_code') || '';
  
  const [formData, setFormData] = useState({
    customer_po_number: '',
    customer_po_date: new Date().toISOString().split('T')[0],
    quotation_id: '',
    quotation_number: '',
    customer_name: '',
    customer_email: '',
    customer_phone: '',
    customer_gst: '',
    customer_address: '',
    billing_address: '',
    shipping_address: '',
    expected_delivery_date: '',
    payment_terms: '',
    notes: '',
    items: [{ product_name: '', quantity: 1, unit_price: 0, gst_rate: 18.0, hsn_code: '' }]
  });

  useEffect(() => {
    fetchCustomerPOs();
    fetchQuotations();
  }, [storeCode]);

  const fetchCustomerPOs = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (storeCode) params.append('store_code', storeCode);
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (searchTerm) params.append('search', searchTerm);
      
      const response = await fetch(`${BACKEND_URL}/api/customer-pos/?${params}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setCustomerPOs(data.customer_pos || []);
      }
    } catch (error) {
      showMessage('error', 'Failed to fetch Customer POs');
    } finally {
      setLoading(false);
    }
  };

  const fetchQuotations = async () => {
    try {
      const params = new URLSearchParams();
      if (storeCode) params.append('store_code', storeCode);
      if (quotationSearchTerm) params.append('search', quotationSearchTerm);
      
      const response = await fetch(`${BACKEND_URL}/api/customer-pos/quotations/available?${params}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setQuotations(data.quotations || []);
      }
    } catch (error) {
      console.error('Failed to fetch quotations:', error);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      if (quotationSearchTerm) {
        fetchQuotations();
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [quotationSearchTerm]);

  useEffect(() => {
    fetchCustomerPOs();
  }, [statusFilter, searchTerm]);

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  const selectQuotation = async (quotation) => {
    // Fetch full quotation details
    try {
      const response = await fetch(`${BACKEND_URL}/api/quotations/${quotation.id}`);
      const data = await response.json();
      
      if (data.quotation) {
        const q = data.quotation;
        setFormData({
          ...formData,
          quotation_id: q.id,
          quotation_number: q.quotation_number,
          customer_name: q.customer_name || '',
          customer_email: q.customer_email || '',
          customer_phone: q.customer_phone || '',
          customer_address: q.customer_address || '',
          items: (q.items || []).map(item => ({
            product_id: item.product_id || '',
            product_name: item.product_name || item.model_number || '',
            brand: item.brand || '',
            model_number: item.model_number || '',
            quantity: item.quantity || 1,
            unit_price: item.offer_price || item.mrp || 0,
            gst_rate: 18.0,
            hsn_code: item.hsn_code || ''
          }))
        });
      }
    } catch (error) {
      showMessage('error', 'Failed to load quotation details');
    }
    setShowQuotationSearch(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.customer_po_number) {
      showMessage('error', 'Customer PO Number is required');
      return;
    }
    
    if (!formData.customer_name) {
      showMessage('error', 'Customer Name is required');
      return;
    }
    
    if (formData.items.length === 0 || !formData.items[0].product_name) {
      showMessage('error', 'At least one item is required');
      return;
    }
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/customer-pos/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          store_code: storeCode,
          ...formData,
          created_by: localStorage.getItem('user_email') || ''
        })
      });
      
      const result = await response.json();
      
      if (response.ok) {
        showMessage('success', `Customer PO ${result.internal_reference} created successfully`);
        setShowModal(false);
        resetForm();
        fetchCustomerPOs();
      } else {
        showMessage('error', result.detail || 'Failed to create Customer PO');
      }
    } catch (error) {
      showMessage('error', 'Error: ' + error.message);
    }
  };

  const resetForm = () => {
    setFormData({
      customer_po_number: '',
      customer_po_date: new Date().toISOString().split('T')[0],
      quotation_id: '',
      quotation_number: '',
      customer_name: '',
      customer_email: '',
      customer_phone: '',
      customer_gst: '',
      customer_address: '',
      billing_address: '',
      shipping_address: '',
      expected_delivery_date: '',
      payment_terms: '',
      notes: '',
      items: [{ product_name: '', quantity: 1, unit_price: 0, gst_rate: 18.0, hsn_code: '' }]
    });
  };

  const addItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { product_name: '', quantity: 1, unit_price: 0, gst_rate: 18.0, hsn_code: '' }]
    });
  };

  const removeItem = (index) => {
    if (formData.items.length > 1) {
      setFormData({
        ...formData,
        items: formData.items.filter((_, i) => i !== index)
      });
    }
  };

  const updateItem = (index, field, value) => {
    const updatedItems = [...formData.items];
    updatedItems[index][field] = value;
    setFormData({ ...formData, items: updatedItems });
  };

  const calculateTotal = () => {
    return formData.items.reduce((sum, item) => {
      const itemTotal = (item.unit_price || 0) * (item.quantity || 1);
      const gst = itemTotal * ((item.gst_rate || 18) / 100);
      return sum + itemTotal + gst;
    }, 0);
  };

  const handleViewDetail = (po) => {
    setSelectedPO(po);
    setShowDetailModal(true);
  };

  const handleConvertToSO = async (po) => {
    if (!window.confirm('Convert this Customer PO to a Sales Order?')) return;
    
    // Navigate to invoice creation with pre-filled data
    navigate('/store/offline-invoice', { 
      state: { 
        fromCustomerPO: true,
        customerPOId: po.id,
        customerPONumber: po.customer_po_number,
        documentType: 'sales_order',
        customer: po.customer,
        items: po.items
      }
    });
  };

  const handleCancelPO = async (po) => {
    const reason = window.prompt('Enter cancellation reason:');
    if (reason === null) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/customer-pos/${po.id}/cancel?reason=${encodeURIComponent(reason)}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        showMessage('success', 'Customer PO cancelled');
        fetchCustomerPOs();
      } else {
        const result = await response.json();
        showMessage('error', result.detail || 'Failed to cancel');
      }
    } catch (error) {
      showMessage('error', 'Error: ' + error.message);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: Clock, label: 'Pending' },
      converted_to_so: { bg: 'bg-blue-100', text: 'text-blue-800', icon: ArrowRight, label: 'Converted to SO' },
      converted_to_invoice: { bg: 'bg-green-100', text: 'text-green-800', icon: CheckCircle, label: 'Invoiced' },
      cancelled: { bg: 'bg-red-100', text: 'text-red-800', icon: XCircle, label: 'Cancelled' }
    };
    const badge = badges[status] || badges.pending;
    const Icon = badge.icon;
    
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}>
        <Icon className="w-3 h-3" />
        {badge.label}
      </span>
    );
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount || 0);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-violet-700"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center px-4 py-2 mb-6 text-gray-700 bg-white hover:bg-gray-100 rounded-lg transition-all border border-gray-300 shadow-sm"
        data-testid="back-btn"
      >
        <ArrowLeft className="h-5 w-5 mr-2" />
        <span className="font-medium">Back</span>
      </button>

      {/* Header */}
      <div className="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <FileText className="w-8 h-8 text-violet-700" />
            Customer Purchase Orders
          </h1>
          <p className="text-gray-600 mt-2">Manage POs received from customers against quotations</p>
        </div>
        <button
          onClick={() => {
            resetForm();
            setShowModal(true);
          }}
          className="bg-violet-700 text-white px-6 py-3 rounded-lg hover:bg-violet-800 transition-colors flex items-center gap-2"
          data-testid="create-cpo-btn"
        >
          <Plus className="w-5 h-5" />
          Record Customer PO
        </button>
      </div>

      {/* Message */}
      {message.text && (
        <div className={`mb-4 p-4 rounded-lg flex items-center gap-2 ${
          message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {message.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
          {message.text}
        </div>
      )}

      {/* Filters */}
      <div className="mb-6 bg-white rounded-lg shadow p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search by PO number, customer name, or quotation..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="converted_to_so">Converted to SO</option>
            <option value="converted_to_invoice">Invoiced</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-gray-900">{customerPOs.length}</div>
          <div className="text-sm text-gray-600">Total Customer POs</div>
        </div>
        <div className="bg-yellow-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-yellow-700">
            {customerPOs.filter(p => p.status === 'pending').length}
          </div>
          <div className="text-sm text-yellow-600">Pending</div>
        </div>
        <div className="bg-blue-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-blue-700">
            {customerPOs.filter(p => p.status === 'converted_to_so').length}
          </div>
          <div className="text-sm text-blue-600">Converted to SO</div>
        </div>
        <div className="bg-green-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-green-700">
            {customerPOs.filter(p => p.status === 'converted_to_invoice').length}
          </div>
          <div className="text-sm text-green-600">Invoiced</div>
        </div>
      </div>

      {/* Customer POs Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="text-left py-4 px-6 font-semibold text-sm text-gray-600">Internal Ref</th>
                <th className="text-left py-4 px-6 font-semibold text-sm text-gray-600">Customer PO #</th>
                <th className="text-left py-4 px-6 font-semibold text-sm text-gray-600">PO Date</th>
                <th className="text-left py-4 px-6 font-semibold text-sm text-gray-600">Customer</th>
                <th className="text-left py-4 px-6 font-semibold text-sm text-gray-600">Quotation</th>
                <th className="text-right py-4 px-6 font-semibold text-sm text-gray-600">Amount</th>
                <th className="text-center py-4 px-6 font-semibold text-sm text-gray-600">Status</th>
                <th className="text-center py-4 px-6 font-semibold text-sm text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody>
              {customerPOs.length === 0 ? (
                <tr>
                  <td colSpan="8" className="py-12 text-center text-gray-500">
                    <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                    <p className="font-medium">No Customer POs found</p>
                    <p className="text-sm">Record a new Customer PO to get started</p>
                  </td>
                </tr>
              ) : (
                customerPOs.map((po) => (
                  <tr key={po.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                    <td className="py-4 px-6 font-semibold text-violet-700">{po.internal_reference}</td>
                    <td className="py-4 px-6 font-medium text-gray-900">{po.customer_po_number}</td>
                    <td className="py-4 px-6 text-sm text-gray-600">{formatDate(po.customer_po_date)}</td>
                    <td className="py-4 px-6">
                      <div className="text-sm font-medium text-gray-900">{po.customer?.name}</div>
                      <div className="text-xs text-gray-500">{po.customer?.phone}</div>
                    </td>
                    <td className="py-4 px-6">
                      {po.quotation_number ? (
                        <span className="inline-flex items-center gap-1 text-sm text-blue-600">
                          <Link2 className="w-3 h-3" />
                          {po.quotation_number}
                        </span>
                      ) : (
                        <span className="text-gray-400 text-sm">-</span>
                      )}
                    </td>
                    <td className="py-4 px-6 text-right font-medium">{formatCurrency(po.grand_total)}</td>
                    <td className="py-4 px-6 text-center">{getStatusBadge(po.status)}</td>
                    <td className="py-4 px-6">
                      <div className="flex items-center justify-center gap-1">
                        <button
                          onClick={() => handleViewDetail(po)}
                          className="p-2 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                          title="View Details"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        {po.status === 'pending' && (
                          <>
                            <button
                              onClick={() => handleConvertToSO(po)}
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                              title="Convert to SO/Invoice"
                            >
                              <ArrowRight className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleCancelPO(po)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                              title="Cancel"
                            >
                              <XCircle className="h-4 w-4" />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full my-8">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900">Record Customer Purchase Order</h2>
                <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">
                  <XCircle className="w-6 h-6" />
                </button>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="p-6 max-h-[70vh] overflow-y-auto">
              {/* Link to Quotation */}
              <div className="mb-6 bg-blue-50 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
                  <Link2 className="w-4 h-4" />
                  Link to Quotation (Optional)
                </h3>
                {formData.quotation_number ? (
                  <div className="flex items-center justify-between bg-white rounded-lg p-3 border border-blue-200">
                    <span className="text-blue-700 font-medium">
                      Linked to: {formData.quotation_number}
                    </span>
                    <button
                      type="button"
                      onClick={() => setFormData({...formData, quotation_id: '', quotation_number: ''})}
                      className="text-red-500 hover:text-red-700"
                    >
                      Remove
                    </button>
                  </div>
                ) : (
                  <div className="relative">
                    <button
                      type="button"
                      onClick={() => setShowQuotationSearch(!showQuotationSearch)}
                      className="w-full text-left px-4 py-2 border border-blue-200 rounded-lg bg-white hover:bg-gray-50 flex justify-between items-center"
                    >
                      <span className="text-gray-500">Search and select a quotation...</span>
                      {showQuotationSearch ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                    {showQuotationSearch && (
                      <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg">
                        <div className="p-2">
                          <input
                            type="text"
                            placeholder="Search by quotation number or customer..."
                            value={quotationSearchTerm}
                            onChange={(e) => setQuotationSearchTerm(e.target.value)}
                            className="w-full px-3 py-2 border rounded-lg text-sm"
                            autoFocus
                          />
                        </div>
                        <div className="max-h-48 overflow-y-auto">
                          {quotations.length === 0 ? (
                            <div className="p-4 text-center text-gray-500 text-sm">No quotations found</div>
                          ) : (
                            quotations.map(q => (
                              <button
                                key={q.id}
                                type="button"
                                onClick={() => selectQuotation(q)}
                                className="w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                              >
                                <div className="font-medium text-gray-900">{q.quotation_number}</div>
                                <div className="text-sm text-gray-500 flex justify-between">
                                  <span>{q.customer_name}</span>
                                  <span>{formatCurrency(q.grand_total)}</span>
                                </div>
                              </button>
                            ))
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Customer PO Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Customer PO Number *</label>
                  <input
                    type="text"
                    value={formData.customer_po_number}
                    onChange={(e) => setFormData({...formData, customer_po_number: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-violet-600"
                    required
                    placeholder="e.g., PO-2024-001"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Customer PO Date *</label>
                  <input
                    type="date"
                    value={formData.customer_po_date}
                    onChange={(e) => setFormData({...formData, customer_po_date: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-violet-600"
                    required
                  />
                </div>
              </div>

              {/* Customer Details */}
              <div className="mb-6">
                <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <User className="w-4 h-4" />
                  Customer Details
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Customer Name *</label>
                    <input
                      type="text"
                      value={formData.customer_name}
                      onChange={(e) => setFormData({...formData, customer_name: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-violet-600"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                    <input
                      type="tel"
                      value={formData.customer_phone}
                      onChange={(e) => setFormData({...formData, customer_phone: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-violet-600"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                      type="email"
                      value={formData.customer_email}
                      onChange={(e) => setFormData({...formData, customer_email: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-violet-600"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">GST Number</label>
                    <input
                      type="text"
                      value={formData.customer_gst}
                      onChange={(e) => setFormData({...formData, customer_gst: e.target.value.toUpperCase()})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-violet-600"
                      placeholder="e.g., 29ABCDE1234F1Z5"
                    />
                  </div>
                </div>
                <div className="mt-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Billing Address</label>
                  <textarea
                    value={formData.billing_address}
                    onChange={(e) => setFormData({...formData, billing_address: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-violet-600"
                    rows="2"
                  />
                </div>
              </div>

              {/* Items */}
              <div className="mb-6">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-semibold text-gray-800 flex items-center gap-2">
                    <Package className="w-4 h-4" />
                    Items
                  </h3>
                  <button
                    type="button"
                    onClick={addItem}
                    className="text-sm text-violet-600 hover:text-violet-800"
                  >
                    + Add Item
                  </button>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4 space-y-4">
                  {formData.items.map((item, index) => (
                    <div key={index} className="bg-white rounded-lg p-4 border border-gray-200">
                      <div className="grid grid-cols-12 gap-3">
                        <div className="col-span-4">
                          <label className="block text-xs font-medium text-gray-600 mb-1">Product/Item Name *</label>
                          <input
                            type="text"
                            value={item.product_name}
                            onChange={(e) => updateItem(index, 'product_name', e.target.value)}
                            className="w-full px-3 py-2 border rounded-lg text-sm"
                            required
                          />
                        </div>
                        <div className="col-span-2">
                          <label className="block text-xs font-medium text-gray-600 mb-1">HSN Code</label>
                          <input
                            type="text"
                            value={item.hsn_code}
                            onChange={(e) => updateItem(index, 'hsn_code', e.target.value)}
                            className="w-full px-3 py-2 border rounded-lg text-sm"
                          />
                        </div>
                        <div className="col-span-1">
                          <label className="block text-xs font-medium text-gray-600 mb-1">Qty</label>
                          <input
                            type="number"
                            min="1"
                            value={item.quantity}
                            onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value) || 1)}
                            className="w-full px-3 py-2 border rounded-lg text-sm"
                          />
                        </div>
                        <div className="col-span-2">
                          <label className="block text-xs font-medium text-gray-600 mb-1">Unit Price</label>
                          <input
                            type="number"
                            step="0.01"
                            value={item.unit_price}
                            onChange={(e) => updateItem(index, 'unit_price', parseFloat(e.target.value) || 0)}
                            className="w-full px-3 py-2 border rounded-lg text-sm"
                          />
                        </div>
                        <div className="col-span-2">
                          <label className="block text-xs font-medium text-gray-600 mb-1">GST %</label>
                          <select
                            value={item.gst_rate}
                            onChange={(e) => updateItem(index, 'gst_rate', parseFloat(e.target.value))}
                            className="w-full px-3 py-2 border rounded-lg text-sm"
                          >
                            <option value={0}>0%</option>
                            <option value={5}>5%</option>
                            <option value={12}>12%</option>
                            <option value={18}>18%</option>
                            <option value={28}>28%</option>
                          </select>
                        </div>
                        <div className="col-span-1 flex items-end">
                          {formData.items.length > 1 && (
                            <button
                              type="button"
                              onClick={() => removeItem(index)}
                              className="p-2 text-red-500 hover:bg-red-50 rounded"
                            >
                              <XCircle className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </div>
                      <div className="mt-2 text-right text-sm text-gray-600">
                        Line Total: {formatCurrency(item.unit_price * item.quantity * (1 + item.gst_rate / 100))}
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="mt-4 text-right">
                  <span className="text-lg font-bold text-gray-900">
                    Grand Total: {formatCurrency(calculateTotal())}
                  </span>
                </div>
              </div>

              {/* Additional Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Expected Delivery Date</label>
                  <input
                    type="date"
                    value={formData.expected_delivery_date}
                    onChange={(e) => setFormData({...formData, expected_delivery_date: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-violet-600"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Payment Terms</label>
                  <input
                    type="text"
                    value={formData.payment_terms}
                    onChange={(e) => setFormData({...formData, payment_terms: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-violet-600"
                    placeholder="e.g., Net 30 days"
                  />
                </div>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({...formData, notes: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-violet-600"
                  rows="2"
                />
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-violet-700 text-white px-4 py-2 rounded-lg hover:bg-violet-800"
                >
                  Save Customer PO
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Detail View Modal */}
      {showDetailModal && selectedPO && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 sticky top-0 bg-white">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{selectedPO.internal_reference}</h2>
                  <p className="text-sm text-gray-500">Customer PO: {selectedPO.customer_po_number}</p>
                </div>
                <button onClick={() => setShowDetailModal(false)} className="text-gray-400 hover:text-gray-600">
                  <XCircle className="w-6 h-6" />
                </button>
              </div>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-2 gap-6 mb-6">
                <div>
                  <h4 className="text-sm font-semibold text-gray-500 mb-2">Customer Details</h4>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="font-medium text-gray-900">{selectedPO.customer?.name}</p>
                    {selectedPO.customer?.phone && (
                      <p className="text-sm text-gray-600 flex items-center gap-1 mt-1">
                        <Phone className="w-3 h-3" /> {selectedPO.customer.phone}
                      </p>
                    )}
                    {selectedPO.customer?.email && (
                      <p className="text-sm text-gray-600 flex items-center gap-1">
                        <Mail className="w-3 h-3" /> {selectedPO.customer.email}
                      </p>
                    )}
                    {selectedPO.customer?.gst_number && (
                      <p className="text-sm text-gray-600 mt-2">GST: {selectedPO.customer.gst_number}</p>
                    )}
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-gray-500 mb-2">PO Information</h4>
                  <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                    <p className="flex justify-between">
                      <span className="text-gray-600">PO Date:</span>
                      <span className="font-medium">{formatDate(selectedPO.customer_po_date)}</span>
                    </p>
                    <p className="flex justify-between">
                      <span className="text-gray-600">Status:</span>
                      {getStatusBadge(selectedPO.status)}
                    </p>
                    {selectedPO.quotation_number && (
                      <p className="flex justify-between">
                        <span className="text-gray-600">Quotation:</span>
                        <span className="text-blue-600">{selectedPO.quotation_number}</span>
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Items */}
              <h4 className="text-sm font-semibold text-gray-500 mb-2">Items</h4>
              <div className="bg-gray-50 rounded-lg overflow-hidden mb-4">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="text-left py-2 px-3">Item</th>
                      <th className="text-center py-2 px-3">Qty</th>
                      <th className="text-right py-2 px-3">Price</th>
                      <th className="text-right py-2 px-3">GST</th>
                      <th className="text-right py-2 px-3">Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(selectedPO.items || []).map((item, idx) => (
                      <tr key={idx} className="border-t border-gray-200">
                        <td className="py-2 px-3">{item.product_name}</td>
                        <td className="py-2 px-3 text-center">{item.quantity}</td>
                        <td className="py-2 px-3 text-right">{formatCurrency(item.unit_price)}</td>
                        <td className="py-2 px-3 text-right">{item.gst_rate}%</td>
                        <td className="py-2 px-3 text-right font-medium">
                          {formatCurrency(item.unit_price * item.quantity * (1 + item.gst_rate / 100))}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Totals */}
              <div className="flex justify-end">
                <div className="w-64 space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Subtotal:</span>
                    <span>{formatCurrency(selectedPO.subtotal)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">CGST:</span>
                    <span>{formatCurrency(selectedPO.cgst)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">SGST:</span>
                    <span>{formatCurrency(selectedPO.sgst)}</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t border-gray-300 font-bold text-base">
                    <span>Grand Total:</span>
                    <span>{formatCurrency(selectedPO.grand_total)}</span>
                  </div>
                </div>
              </div>

              {/* Actions */}
              {selectedPO.status === 'pending' && (
                <div className="mt-6 pt-4 border-t border-gray-200 flex gap-3">
                  <button
                    onClick={() => {
                      setShowDetailModal(false);
                      handleConvertToSO(selectedPO);
                    }}
                    className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
                  >
                    <ArrowRight className="w-4 h-4" />
                    Convert to SO/Invoice
                  </button>
                  <button
                    onClick={() => {
                      setShowDetailModal(false);
                      handleCancelPO(selectedPO);
                    }}
                    className="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50"
                  >
                    Cancel PO
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CustomerPOManagement;
