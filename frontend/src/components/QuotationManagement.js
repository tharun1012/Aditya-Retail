import React, { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL as API_URL } from '../config/api';
import { 
  FileText, Plus, Search, Download, Mail, Send, Eye, Edit,
  Trash2, RefreshCw, ChevronRight, X, Check, Package,
  Phone, User, MapPin, Calendar, Tag, Percent, FileCheck
} from 'lucide-react';

const QuotationManagement = ({ storeId: propStoreId, storeName: propStoreName, isEmbedded = false }) => {
  const [quotations, setQuotations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState(propStoreId || '');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedQuotation, setSelectedQuotation] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [message, setMessage] = useState({ type: '', text: '' });

  
  useEffect(() => {
    // If embedded with a fixed store, use that store directly
    if (propStoreId) {
      setSelectedStore(propStoreId);
      if (propStoreName) {
        setStores([{ id: propStoreId, name: propStoreName }]);
      }
    } else {
      fetchStores();
    }
  }, [propStoreId, propStoreName]);

  useEffect(() => {
    if (selectedStore) {
      fetchQuotations();
    }
  }, [selectedStore, statusFilter]);

  const fetchStores = async () => {
    try {
      const response = await fetch(`${API_URL}/api/stores/`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('admin_token')}` }
      });
      if (response.ok) {
        const data = await response.json();
        setStores(data.stores || []);
        if (data.stores?.length > 0) {
          setSelectedStore(data.stores[0].id);
        }
      }
    } catch (error) {
      console.error('Error fetching stores:', error);
    }
  };

  const fetchQuotations = async () => {
    setLoading(true);
    try {
      let url = `${API_URL}/api/quotations/list?store_id=${selectedStore}`;
      if (statusFilter) url += `&status=${statusFilter}`;
      
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setQuotations(data.quotations || []);
      }
    } catch (error) {
      console.error('Error fetching quotations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async (quotationId) => {
    try {
      window.open(`${API_URL}/api/quotations/${quotationId}/pdf`, '_blank');
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to download PDF' });
    }
  };

  const handleWhatsApp = async (quotationId) => {
    try {
      const response = await fetch(`${API_URL}/api/quotations/${quotationId}/whatsapp`);
      if (response.ok) {
        const data = await response.json();
        window.open(data.whatsapp_link, '_blank');
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to generate WhatsApp link' });
    }
  };

  const handleViewQuotation = async (quotationId) => {
    try {
      const response = await fetch(`${API_URL}/api/quotations/${quotationId}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedQuotation(data.quotation);
        setShowViewModal(true);
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load quotation details' });
    }
  };

  const handleEditQuotation = async (quotationId) => {
    try {
      const response = await fetch(`${API_URL}/api/quotations/${quotationId}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedQuotation(data.quotation);
        setShowEditModal(true);
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load quotation for editing' });
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      draft: 'bg-gray-100 text-gray-700',
      sent: 'bg-blue-100 text-blue-700',
      accepted: 'bg-green-100 text-green-700',
      rejected: 'bg-red-100 text-red-700',
      expired: 'bg-yellow-100 text-yellow-700',
      converted: 'bg-purple-100 text-purple-700'
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
  };

  const filteredQuotations = quotations.filter(q => 
    !searchQuery || 
    q.quotation_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
    q.customer_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    q.customer_phone?.includes(searchQuery)
  );

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-amber-100 rounded-xl">
                <FileText className="w-6 h-6 text-amber-700" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Quotations</h1>
                <p className="text-gray-600 text-sm">Create and manage customer quotations</p>
              </div>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors"
              data-testid="create-quotation-btn"
            >
              <Plus className="w-5 h-5" />
              <span>New Quotation</span>
            </button>
          </div>
        </div>

        {/* Message */}
        {message.text && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : 
            'bg-red-50 text-red-800 border border-red-200'
          }`}>
            {message.text}
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
          <div className="flex flex-wrap items-center gap-4">
            <select
              value={selectedStore}
              onChange={(e) => setSelectedStore(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500"
              data-testid="store-filter"
            >
              {stores.map(store => (
                <option key={store.id} value={store.id}>{store.name}</option>
              ))}
            </select>

            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by quotation number, customer..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500"
                data-testid="search-input"
              />
            </div>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500"
              data-testid="status-filter"
            >
              <option value="">All Status</option>
              <option value="draft">Draft</option>
              <option value="sent">Sent</option>
              <option value="accepted">Accepted</option>
              <option value="rejected">Rejected</option>
              <option value="converted">Converted</option>
            </select>

            <button
              onClick={fetchQuotations}
              className="p-2 text-gray-500 hover:text-amber-600 hover:bg-amber-50 rounded-lg"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Quotations List */}
        {loading ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <RefreshCw className="w-8 h-8 text-amber-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Loading quotations...</p>
          </div>
        ) : filteredQuotations.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600">No quotations found</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="mt-4 text-amber-600 hover:text-amber-700 font-medium"
            >
              Create your first quotation
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Quotation #</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Customer</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Items</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Amount</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Valid Until</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Status</th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {filteredQuotations.map(quotation => (
                    <tr key={quotation.id} className="hover:bg-gray-50" data-testid={`quotation-row-${quotation.id}`}>
                      <td className="px-4 py-3">
                        <span className="font-mono text-amber-600 font-medium">{quotation.quotation_number}</span>
                        <p className="text-xs text-gray-500">{quotation.created_at?.slice(0, 10)}</p>
                      </td>
                      <td className="px-4 py-3">
                        <p className="font-medium text-gray-900">{quotation.customer_name}</p>
                        <p className="text-sm text-gray-500">{quotation.customer_phone || quotation.customer_email}</p>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-gray-900">{quotation.item_count} items</span>
                      </td>
                      <td className="px-4 py-3">
                        <p className="font-semibold text-gray-900">₹{quotation.totals?.grand_total?.toLocaleString()}</p>
                        {quotation.totals?.total_savings > 0 && (
                          <p className="text-xs text-green-600">Save ₹{quotation.totals.total_savings.toLocaleString()}</p>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-gray-900">{quotation.valid_until?.slice(0, 10)}</span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${getStatusColor(quotation.status)}`}>
                          {quotation.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center justify-center space-x-1">
                          <button
                            onClick={() => handleViewQuotation(quotation.id)}
                            className="p-2 text-gray-500 hover:text-amber-600 hover:bg-amber-50 rounded-lg"
                            title="View"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          {(quotation.status === 'draft' || quotation.status === 'sent') && (
                            <button
                              onClick={() => handleEditQuotation(quotation.id)}
                              className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg"
                              title="Edit Quotation"
                              data-testid={`edit-quotation-${quotation.id}`}
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                          )}
                          <button
                            onClick={() => handleDownloadPDF(quotation.id)}
                            className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg"
                            title="Download PDF"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleWhatsApp(quotation.id)}
                            className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg"
                            title="Share on WhatsApp"
                          >
                            <Send className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Create Quotation Modal */}
      {showCreateModal && (
        <CreateQuotationModal
          stores={stores}
          selectedStore={selectedStore}
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            fetchQuotations();
            setMessage({ type: 'success', text: 'Quotation created successfully!' });
            setTimeout(() => setMessage({ type: '', text: '' }), 3000);
          }}
          API_URL={API_URL}
        />
      )}

      {/* View Quotation Modal */}
      {showViewModal && selectedQuotation && (
        <ViewQuotationModal
          quotation={selectedQuotation}
          onClose={() => {
            setShowViewModal(false);
            setSelectedQuotation(null);
          }}
          onDownload={() => handleDownloadPDF(selectedQuotation.id)}
          onWhatsApp={() => handleWhatsApp(selectedQuotation.id)}
          API_URL={API_URL}
        />
      )}

      {/* Edit Quotation Modal */}
      {showEditModal && selectedQuotation && (
        <EditQuotationModal
          quotation={selectedQuotation}
          onClose={() => {
            setShowEditModal(false);
            setSelectedQuotation(null);
          }}
          onSuccess={() => {
            setShowEditModal(false);
            setSelectedQuotation(null);
            fetchQuotations();
            setMessage({ type: 'success', text: 'Quotation updated successfully!' });
            setTimeout(() => setMessage({ type: '', text: '' }), 3000);
          }}
          API_URL={API_URL}
        />
      )}
    </div>
  );
};

// Create Quotation Modal Component
const CreateQuotationModal = ({ stores, selectedStore, onClose, onSuccess, API_URL }) => {
  const [step, setStep] = useState(1); // 1: Customer Details, 2: Products, 3: Review
  const [customerData, setCustomerData] = useState({
    store_id: selectedStore,
    customer_name: '',
    customer_email: '',
    customer_phone: '',
    customer_address: '',
    validity_days: 15,
    discount_percent: 0,
    include_gst: true,
    terms_and_conditions: ''
  });
  const [items, setItems] = useState([]);
  const [productSearch, setProductSearch] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');

  const searchProducts = useCallback(async (query) => {
    if (!query || query.length < 2) {
      setSearchResults([]);
      return;
    }
    
    setSearching(true);
    try {
      const response = await fetch(`${API_URL}/api/quotations/search/products?query=${encodeURIComponent(query)}`);
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.products || []);
      }
    } catch (error) {
      console.error('Error searching products:', error);
    } finally {
      setSearching(false);
    }
  }, [API_URL]);

  useEffect(() => {
    const timer = setTimeout(() => {
      searchProducts(productSearch);
    }, 300);
    return () => clearTimeout(timer);
  }, [productSearch, searchProducts]);

  const addProduct = (product) => {
    const existingIndex = items.findIndex(i => i.product_id === product.product_id);
    if (existingIndex >= 0) {
      const updated = [...items];
      updated[existingIndex].quantity += 1;
      setItems(updated);
    } else {
      setItems([...items, { ...product, quantity: 1 }]);
    }
    setProductSearch('');
    setSearchResults([]);
  };

  const [showManualEntry, setShowManualEntry] = useState(false);
  const [manualItem, setManualItem] = useState({
    brand: '', model_number: '', product_name: '', mrp: '', offer_price: '', quantity: 1
  });

  const addManualItem = () => {
    setItems([...items, {
      product_id: null,
      brand: manualItem.brand,
      model_number: manualItem.model_number,
      product_name: manualItem.product_name,
      description: '',
      image_url: null,
      mrp: parseFloat(manualItem.mrp) || parseFloat(manualItem.offer_price) || 0,
      offer_price: parseFloat(manualItem.offer_price) || 0,
      quantity: parseInt(manualItem.quantity) || 1,
      is_manual_entry: true
    }]);
    setManualItem({ brand: '', model_number: '', product_name: '', mrp: '', offer_price: '', quantity: 1 });
    setShowManualEntry(false);
  };

  const updateItemQuantity = (index, quantity) => {
    const updated = [...items];
    updated[index].quantity = Math.max(1, parseInt(quantity) || 1);
    setItems(updated);
  };

  const updateItemPrice = (index, field, value) => {
    const updated = [...items];
    updated[index][field] = parseFloat(value) || 0;
    setItems(updated);
  };

  const removeItem = (index) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const calculateTotals = () => {
    const subtotal = items.reduce((sum, item) => sum + (item.offer_price * item.quantity), 0);
    const mrpTotal = items.reduce((sum, item) => sum + (item.mrp * item.quantity), 0);
    const discount = subtotal * (customerData.discount_percent / 100);
    const grossAmount = subtotal - discount; // already GST-inclusive
    const taxable = customerData.include_gst ? grossAmount / 1.18 : grossAmount;
    const gst = customerData.include_gst ? grossAmount - taxable : 0;
    const total = grossAmount; // GST extracted, not added on top
    const savings = mrpTotal - total;
    return { subtotal, mrpTotal, discount, taxable, gst, total, savings };
  };

  const handleSubmit = async () => {
    if (items.length === 0) {
      setError('Please add at least one product');
      return;
    }

    setCreating(true);
    setError('');

    try {
      const payload = {
        ...customerData,
        items: items.map(item => ({
          product_id: item.product_id,
          brand: item.brand,
          model_number: item.model_number,
          product_name: item.product_name,
          description: item.description,
          image_url: item.image_url,
          mrp: item.mrp,
          offer_price: item.offer_price,
          quantity: item.quantity
        }))
      };

      const response = await fetch(`${API_URL}/api/quotations/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        onSuccess();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create quotation');
      }
    } catch (error) {
      setError('Failed to create quotation');
    } finally {
      setCreating(false);
    }
  };

  const totals = calculateTotals();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-amber-50 to-orange-50">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Create New Quotation</h2>
            <p className="text-sm text-gray-600">Step {step} of 3</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white rounded-lg transition-colors">
            <X className="w-6 h-6 text-gray-500" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-6 pt-4">
          <div className="flex items-center space-x-2">
            {[1, 2, 3].map(s => (
              <React.Fragment key={s}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
                  s <= step ? 'bg-amber-600 text-white' : 'bg-gray-200 text-gray-500'
                }`}>
                  {s}
                </div>
                {s < 3 && <div className={`flex-1 h-1 rounded ${s < step ? 'bg-amber-600' : 'bg-gray-200'}`} />}
              </React.Fragment>
            ))}
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Customer</span>
            <span>Products</span>
            <span>Review</span>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg border border-red-200">
              {error}
            </div>
          )}

          {/* Step 1: Customer Details */}
          {step === 1 && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Store</label>
                  <select
                    value={customerData.store_id}
                    onChange={(e) => setCustomerData({ ...customerData, store_id: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500"
                  >
                    {stores.map(store => (
                      <option key={store.id} value={store.id}>{store.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Validity (Days)</label>
                  <input
                    type="number"
                    value={customerData.validity_days}
                    onChange={(e) => setCustomerData({ ...customerData, validity_days: parseInt(e.target.value) || 15 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Customer Name *</label>
                <input
                  type="text"
                  value={customerData.customer_name}
                  onChange={(e) => setCustomerData({ ...customerData, customer_name: e.target.value })}
                  placeholder="Enter customer name"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                  <input
                    type="tel"
                    value={customerData.customer_phone}
                    onChange={(e) => setCustomerData({ ...customerData, customer_phone: e.target.value })}
                    placeholder="+91 98765 43210"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={customerData.customer_email}
                    onChange={(e) => setCustomerData({ ...customerData, customer_email: e.target.value })}
                    placeholder="customer@email.com"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                <textarea
                  value={customerData.customer_address}
                  onChange={(e) => setCustomerData({ ...customerData, customer_address: e.target.value })}
                  placeholder="Enter delivery address"
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Discount %</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={customerData.discount_percent}
                    onChange={(e) => setCustomerData({ ...customerData, discount_percent: parseFloat(e.target.value) || 0 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500"
                  />
                </div>
                <div className="flex items-center pt-6">
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={customerData.include_gst}
                      onChange={(e) => setCustomerData({ ...customerData, include_gst: e.target.checked })}
                      className="w-4 h-4 text-amber-600 rounded focus:ring-amber-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">Include GST (18%)</span>
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Products */}
          {step === 2 && (
            <div className="space-y-4">
              {/* Product Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={productSearch}
                  onChange={(e) => setProductSearch(e.target.value)}
                  placeholder="Search products by name, brand, model..."
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500"
                />
                
                {/* Search Results Dropdown */}
                {searchResults.length > 0 && (
                  <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-lg border max-h-64 overflow-y-auto z-10">
                    {searchResults.map((product, idx) => (
                      <button
                        key={idx}
                        onClick={() => addProduct(product)}
                        className="w-full p-3 text-left hover:bg-amber-50 border-b last:border-0 flex items-center space-x-3"
                      >
                        {product.image_url ? (
                          <img src={product.image_url} alt="" className="w-12 h-12 object-contain rounded" />
                        ) : (
                          <div className="w-12 h-12 bg-gray-100 rounded flex items-center justify-center">
                            <Package className="w-6 h-6 text-gray-400" />
                          </div>
                        )}
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{product.brand} {product.model_number}</p>
                          <p className="text-sm text-gray-500 truncate">{product.product_name}</p>
                          <p className="text-sm font-semibold text-amber-600">₹{product.offer_price?.toLocaleString()}</p>
                        </div>
                        <Plus className="w-5 h-5 text-amber-600" />
                      </button>
                    ))}
                  </div>
                )}
                
                {searching && (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    <RefreshCw className="w-5 h-5 text-amber-600 animate-spin" />
                  </div>
                )}
              </div>

              {/* Manual Entry Toggle */}
              <div>
                <button
                  onClick={() => setShowManualEntry(!showManualEntry)}
                  className="text-sm text-amber-600 font-medium hover:text-amber-700"
                >
                  {showManualEntry ? '- Cancel manual entry' : '+ Add item manually'}
                </button>
                {showManualEntry && (
                  <div className="mt-3 border rounded-lg p-4 bg-gray-50 space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <input
                        type="text" placeholder="Brand"
                        value={manualItem.brand}
                        onChange={(e) => setManualItem({ ...manualItem, brand: e.target.value })}
                        className="px-3 py-2 border rounded text-sm"
                      />
                      <input
                        type="text" placeholder="Model Number"
                        value={manualItem.model_number}
                        onChange={(e) => setManualItem({ ...manualItem, model_number: e.target.value })}
                        className="px-3 py-2 border rounded text-sm"
                      />
                    </div>
                    <input
                      type="text" placeholder="Product Name *"
                      value={manualItem.product_name}
                      onChange={(e) => setManualItem({ ...manualItem, product_name: e.target.value })}
                      className="w-full px-3 py-2 border rounded text-sm"
                    />
                    <div className="grid grid-cols-3 gap-3">
                      <div>
                        <label className="text-xs text-gray-500">MRP</label>
                        <input
                          type="number"
                          value={manualItem.mrp}
                          onChange={(e) => setManualItem({ ...manualItem, mrp: e.target.value })}
                          className="w-full px-2 py-1 border rounded text-sm"
                        />
                      </div>
                      <div>
                        <label className="text-xs text-gray-500">Offer Price *</label>
                        <input
                          type="number"
                          value={manualItem.offer_price}
                          onChange={(e) => setManualItem({ ...manualItem, offer_price: e.target.value })}
                          className="w-full px-2 py-1 border rounded text-sm"
                        />
                      </div>
                      <div>
                        <label className="text-xs text-gray-500">Qty</label>
                        <input
                          type="number" min="1"
                          value={manualItem.quantity}
                          onChange={(e) => setManualItem({ ...manualItem, quantity: e.target.value })}
                          className="w-full px-2 py-1 border rounded text-sm"
                        />
                      </div>
                    </div>
                    <button
                      onClick={addManualItem}
                      className="w-full py-2 bg-amber-600 text-white rounded-lg text-sm font-medium hover:bg-amber-700"
                    >
                      Add Item
                    </button>
                  </div>
                )}
              </div>

              {/* Selected Items */}
              {items.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Package className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Search and add products to create quotation</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {items.map((item, idx) => (
                    <div key={idx} className="border rounded-lg p-4 bg-gray-50">
                      <div className="flex items-start space-x-4">
                        {item.image_url ? (
                          <img src={item.image_url} alt="" className="w-16 h-16 object-contain rounded" />
                        ) : (
                          <div className="w-16 h-16 bg-white rounded flex items-center justify-center">
                            <Package className="w-8 h-8 text-gray-300" />
                          </div>
                        )}
                        <div className="flex-1">
                          <p className="font-semibold text-gray-900">{item.brand} {item.model_number}</p>
                          <p className="text-sm text-gray-600">{item.product_name}</p>
                          
                          <div className="mt-2 flex items-center space-x-4">
                            <div>
                              <label className="text-xs text-gray-500">MRP</label>
                              <input
                                type="number"
                                value={item.mrp}
                                onChange={(e) => updateItemPrice(idx, 'mrp', e.target.value)}
                                className="w-24 px-2 py-1 border rounded text-sm"
                              />
                            </div>
                            <div>
                              <label className="text-xs text-gray-500">Offer Price</label>
                              <input
                                type="number"
                                value={item.offer_price}
                                onChange={(e) => updateItemPrice(idx, 'offer_price', e.target.value)}
                                className="w-24 px-2 py-1 border rounded text-sm"
                              />
                            </div>
                            <div>
                              <label className="text-xs text-gray-500">Qty</label>
                              <input
                                type="number"
                                min="1"
                                value={item.quantity}
                                onChange={(e) => updateItemQuantity(idx, e.target.value)}
                                className="w-16 px-2 py-1 border rounded text-sm text-center"
                              />
                            </div>
                            <div className="text-right">
                              <label className="text-xs text-gray-500">Total</label>
                              <p className="font-semibold text-amber-600">₹{(item.offer_price * item.quantity).toLocaleString()}</p>
                            </div>
                          </div>
                        </div>
                        <button
                          onClick={() => removeItem(idx)}
                          className="p-2 text-red-500 hover:bg-red-50 rounded-lg"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Step 3: Review */}
          {step === 3 && (
            <div className="space-y-6">
              {/* Customer Summary */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">Customer Details</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center space-x-2">
                    <User className="w-4 h-4 text-gray-400" />
                    <span>{customerData.customer_name}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Phone className="w-4 h-4 text-gray-400" />
                    <span>{customerData.customer_phone || 'Not provided'}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Mail className="w-4 h-4 text-gray-400" />
                    <span>{customerData.customer_email || 'Not provided'}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Calendar className="w-4 h-4 text-gray-400" />
                    <span>Valid for {customerData.validity_days} days</span>
                  </div>
                </div>
                {customerData.customer_address && (
                  <div className="mt-3 flex items-start space-x-2 text-sm">
                    <MapPin className="w-4 h-4 text-gray-400 mt-0.5" />
                    <span>{customerData.customer_address}</span>
                  </div>
                )}
              </div>

              {/* Items Summary */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Products ({items.length})</h3>
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 text-left">#</th>
                        <th className="px-3 py-2 text-left">Product</th>
                        <th className="px-3 py-2 text-right">MRP</th>
                        <th className="px-3 py-2 text-right">Offer</th>
                        <th className="px-3 py-2 text-center">Qty</th>
                        <th className="px-3 py-2 text-right">Total</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {items.map((item, idx) => (
                        <tr key={idx}>
                          <td className="px-3 py-2">{idx + 1}</td>
                          <td className="px-3 py-2">
                            <p className="font-medium">{item.brand}</p>
                            <p className="text-gray-500">{item.model_number}</p>
                          </td>
                          <td className="px-3 py-2 text-right">₹{item.mrp.toLocaleString()}</td>
                          <td className="px-3 py-2 text-right">₹{item.offer_price.toLocaleString()}</td>
                          <td className="px-3 py-2 text-center">{item.quantity}</td>
                          <td className="px-3 py-2 text-right font-medium">₹{(item.offer_price * item.quantity).toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Totals */}
              <div className="bg-amber-50 rounded-lg p-4">
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">MRP Total:</span>
                    <span className="line-through text-gray-400">₹{totals.mrpTotal.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Your Price:</span>
                    <span>₹{totals.subtotal.toLocaleString()}</span>
                  </div>
                  {totals.discount > 0 && (
                    <div className="flex justify-between text-green-600">
                      <span>Discount ({customerData.discount_percent}%):</span>
                      <span>-₹{totals.discount.toLocaleString()}</span>
                    </div>
                  )}
                  {customerData.include_gst && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">GST (18%):</span>
                      <span>₹{totals.gst.toLocaleString()}</span>
                    </div>
                  )}
                  <div className="flex justify-between pt-2 border-t border-amber-200 font-bold text-lg">
                    <span>Grand Total:</span>
                    <span className="text-amber-700">₹{totals.total.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-green-600 font-medium">
                    <span>You Save:</span>
                    <span>₹{totals.savings.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* Terms */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Terms & Conditions (Optional)</label>
                <textarea
                  value={customerData.terms_and_conditions}
                  onChange={(e) => setCustomerData({ ...customerData, terms_and_conditions: e.target.value })}
                  placeholder="Default terms will be applied if left empty"
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 text-sm"
                />
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t bg-gray-50 flex items-center justify-between">
          <button
            onClick={() => step > 1 ? setStep(step - 1) : onClose()}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium"
          >
            {step > 1 ? 'Back' : 'Cancel'}
          </button>
          
          <div className="flex items-center space-x-3">
            {step < 3 ? (
              <button
                onClick={() => {
                  if (step === 1 && !customerData.customer_name) {
                    setError('Please enter customer name');
                    return;
                  }
                  if (step === 2 && items.length === 0) {
                    setError('Please add at least one product');
                    return;
                  }
                  setError('');
                  setStep(step + 1);
                }}
                className="flex items-center space-x-2 px-6 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 font-medium"
              >
                <span>Continue</span>
                <ChevronRight className="w-5 h-5" />
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={creating}
                className="flex items-center space-x-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium disabled:opacity-50"
              >
                {creating ? (
                  <RefreshCw className="w-5 h-5 animate-spin" />
                ) : (
                  <FileCheck className="w-5 h-5" />
                )}
                <span>{creating ? 'Creating...' : 'Create Quotation'}</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// View Quotation Modal
export const ViewQuotationModal = ({ quotation, onClose, onDownload, onWhatsApp, API_URL }) => {
  const [sendingEmail, setSendingEmail] = useState(false);
  const [emailTo, setEmailTo] = useState(quotation.customer_email || '');
  const [showEmailForm, setShowEmailForm] = useState(false);
  const [message, setMessage] = useState('');

  const handleSendEmail = async () => {
    if (!emailTo) return;
    
    setSendingEmail(true);
    try {
      const response = await fetch(`${API_URL}/api/quotations/${quotation.id}/email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ to_email: emailTo })
      });

      if (response.ok) {
        setMessage('Email sent successfully!');
        setShowEmailForm(false);
      } else {
        setMessage('Failed to send email');
      }
    } catch (error) {
      setMessage('Failed to send email');
    } finally {
      setSendingEmail(false);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-amber-50 to-orange-50">
          <div>
            <h2 className="text-xl font-bold text-gray-900">{quotation.quotation_number}</h2>
            <p className="text-sm text-gray-600">Created on {quotation.created_at?.slice(0, 10)}</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white rounded-lg transition-colors">
            <X className="w-6 h-6 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {message && (
            <div className={`p-3 rounded-lg ${message.includes('success') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
              {message}
            </div>
          )}

          {/* Customer Info */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-3">Customer</h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <p><span className="text-gray-500">Name:</span> {quotation.customer_name}</p>
              <p><span className="text-gray-500">Phone:</span> {quotation.customer_phone || 'N/A'}</p>
              <p><span className="text-gray-500">Email:</span> {quotation.customer_email || 'N/A'}</p>
              <p><span className="text-gray-500">Valid Until:</span> {quotation.valid_until?.slice(0, 10)}</p>
            </div>
          </div>

          {/* Items */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Products</h3>
            <div className="space-y-2">
              {quotation.items?.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    {item.image_url ? (
                      <img src={item.image_url} alt="" className="w-12 h-12 object-contain rounded" />
                    ) : (
                      <div className="w-12 h-12 bg-white rounded flex items-center justify-center">
                        <Package className="w-6 h-6 text-gray-300" />
                      </div>
                    )}
                    <div>
                      <p className="font-medium">{item.brand} {item.model_number}</p>
                      <p className="text-sm text-gray-500">Qty: {item.quantity}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="line-through text-gray-400 text-sm">₹{item.mrp?.toLocaleString()}</p>
                    <p className="font-semibold text-amber-600">₹{(item.offer_price * item.quantity).toLocaleString()}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Totals */}
          <div className="bg-amber-50 rounded-lg p-4">
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Subtotal:</span>
                <span>₹{quotation.totals?.subtotal?.toLocaleString()}</span>
              </div>
              {quotation.totals?.discount_amount > 0 && (
                <div className="flex justify-between text-green-600">
                  <span>Discount:</span>
                  <span>-₹{quotation.totals.discount_amount.toLocaleString()}</span>
                </div>
              )}
              {quotation.include_gst && (
                <div className="flex justify-between">
                  <span>GST:</span>
                  <span>₹{quotation.totals?.total_gst?.toLocaleString()}</span>
                </div>
              )}
              <div className="flex justify-between pt-2 border-t border-amber-200 font-bold text-lg">
                <span>Grand Total:</span>
                <span className="text-amber-700">₹{quotation.totals?.grand_total?.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-green-600 font-medium">
                <span>Customer Saves:</span>
                <span>₹{quotation.totals?.total_savings?.toLocaleString()}</span>
              </div>
            </div>
          </div>

          {/* Bank Details */}
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
            <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Bank Details for Payment</h4>
            <div className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-xs">
              <span className="text-gray-500">Bank Name:</span>
              <span className="font-medium">DBS Bank</span>
              <span className="text-gray-500">Account Name:</span>
              <span className="font-medium">Aditya Retail</span>
              <span className="text-gray-500">A/C No:</span>
              <span className="font-medium">827200176347</span>
              <span className="text-gray-500">IFSC Code:</span>
              <span className="font-medium">DBSS0IN0827</span>
              <span className="text-gray-500">Branch:</span>
              <span className="font-medium">Ulsoor Road, Bangalore</span>
              <span className="text-gray-500">Account Type:</span>
              <span className="font-medium">Current Account</span>
              <span className="text-gray-500">GST:</span>
              <span className="font-medium">29ABAFA6295J1Z2</span>
            </div>
          </div>

          {/* Email Form */}
          {showEmailForm && (
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-3">Send via Email</h3>
              <div className="flex space-x-3">
                <input
                  type="email"
                  value={emailTo}
                  onChange={(e) => setEmailTo(e.target.value)}
                  placeholder="Enter email address"
                  className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleSendEmail}
                  disabled={sendingEmail || !emailTo}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
                >
                  {sendingEmail ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                  <span>Send</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-6 border-t bg-gray-50 flex items-center justify-between">
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            quotation.status === 'draft' ? 'bg-gray-100 text-gray-700' :
            quotation.status === 'sent' ? 'bg-blue-100 text-blue-700' :
            quotation.status === 'accepted' ? 'bg-green-100 text-green-700' :
            'bg-gray-100 text-gray-700'
          }`}>
            {quotation.status?.toUpperCase()}
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={onDownload}
              className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <Download className="w-4 h-4" />
              <span>Download PDF</span>
            </button>
            <button
              onClick={() => setShowEmailForm(!showEmailForm)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Mail className="w-4 h-4" />
              <span>Email</span>
            </button>
            <button
              onClick={onWhatsApp}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <Send className="w-4 h-4" />
              <span>WhatsApp</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Edit Quotation Modal
const EditQuotationModal = ({ quotation, onClose, onSuccess, API_URL }) => {
  const [formData, setFormData] = useState({
    customer_name: quotation.customer_name || '',
    customer_phone: quotation.customer_phone || '',
    customer_email: quotation.customer_email || '',
    customer_address: quotation.customer_address || '',
    notes: quotation.notes || '',
    terms_and_conditions: quotation.terms_and_conditions || '',
    discount_percent: quotation.discount_percent || 0,
    validity_days: quotation.validity_days || 15
  });
  const [items, setItems] = useState(quotation.items || []);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const updateItem = (index, field, value) => {
    const updated = [...items];
    updated[index] = { ...updated[index], [field]: value };
    setItems(updated);
  };

  const removeItem = (index) => {
    if (items.length > 1) {
      setItems(items.filter((_, i) => i !== index));
    }
  };

  const addItem = () => {
    setItems([...items, {
      product_name: '',
      model_number: '',
      brand: '',
      quantity: 1,
      mrp: 0,
      offer_price: 0
    }]);
  };

  const calculateTotal = () => {
    const subtotal = items.reduce((sum, item) => sum + (item.offer_price || item.mrp || 0) * (item.quantity || 1), 0);
    const discount = subtotal * (formData.discount_percent / 100);
    return subtotal - discount;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/quotations/${quotation.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          items: items
        })
      });

      if (response.ok) {
        onSuccess();
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to update quotation');
      }
    } catch (err) {
      setError('Network error: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-blue-50">
          <h2 className="text-xl font-bold text-gray-900">
            Edit Quotation: {quotation.quotation_number}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6">
          {error && (
            <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">{error}</div>
          )}

          {/* Customer Details */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Customer Details</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Customer Name *</label>
                <input
                  type="text"
                  value={formData.customer_name}
                  onChange={(e) => setFormData({...formData, customer_name: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                <input
                  type="tel"
                  value={formData.customer_phone}
                  onChange={(e) => setFormData({...formData, customer_phone: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  value={formData.customer_email}
                  onChange={(e) => setFormData({...formData, customer_email: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                <input
                  type="text"
                  value={formData.customer_address}
                  onChange={(e) => setFormData({...formData, customer_address: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
            </div>
          </div>

          {/* Items */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-lg font-semibold text-gray-800">Items</h3>
              <button
                type="button"
                onClick={addItem}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                + Add Item
              </button>
            </div>
            <div className="space-y-3">
              {items.map((item, index) => (
                <div key={index} className="bg-gray-50 rounded-lg p-3">
                  <div className="grid grid-cols-12 gap-2">
                    <div className="col-span-4">
                      <label className="block text-xs text-gray-500 mb-1">Product Name</label>
                      <input
                        type="text"
                        value={item.product_name || ''}
                        onChange={(e) => updateItem(index, 'product_name', e.target.value)}
                        className="w-full px-2 py-1 border rounded text-sm"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-xs text-gray-500 mb-1">Model</label>
                      <input
                        type="text"
                        value={item.model_number || ''}
                        onChange={(e) => updateItem(index, 'model_number', e.target.value)}
                        className="w-full px-2 py-1 border rounded text-sm"
                      />
                    </div>
                    <div className="col-span-1">
                      <label className="block text-xs text-gray-500 mb-1">Qty</label>
                      <input
                        type="number"
                        min="1"
                        value={item.quantity || 1}
                        onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value) || 1)}
                        className="w-full px-2 py-1 border rounded text-sm"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-xs text-gray-500 mb-1">MRP</label>
                      <input
                        type="number"
                        value={item.mrp || 0}
                        onChange={(e) => updateItem(index, 'mrp', parseFloat(e.target.value) || 0)}
                        className="w-full px-2 py-1 border rounded text-sm"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-xs text-gray-500 mb-1">Offer Price</label>
                      <input
                        type="number"
                        value={item.offer_price || 0}
                        onChange={(e) => updateItem(index, 'offer_price', parseFloat(e.target.value) || 0)}
                        className="w-full px-2 py-1 border rounded text-sm"
                      />
                    </div>
                    <div className="col-span-1 flex items-end">
                      {items.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeItem(index)}
                          className="p-1 text-red-500 hover:bg-red-50 rounded"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Discount & Validity */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Discount %</label>
              <input
                type="number"
                min="0"
                max="100"
                value={formData.discount_percent}
                onChange={(e) => setFormData({...formData, discount_percent: parseFloat(e.target.value) || 0})}
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Validity (Days)</label>
              <input
                type="number"
                min="1"
                value={formData.validity_days}
                onChange={(e) => setFormData({...formData, validity_days: parseInt(e.target.value) || 15})}
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
          </div>

          {/* Notes */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
              className="w-full px-3 py-2 border rounded-lg"
              rows="2"
            />
          </div>

          {/* Total */}
          <div className="text-right mb-4">
            <span className="text-lg font-bold text-gray-900">
              Estimated Total: ₹{calculateTotal().toLocaleString('en-IN')}
            </span>
          </div>
        </form>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 flex justify-end gap-3 bg-gray-50">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border rounded-lg hover:bg-gray-100"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={saving}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuotationManagement;
