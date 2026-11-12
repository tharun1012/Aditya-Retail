import React, { useState, useEffect } from 'react';
import { 
  ArrowRight, Package, Truck, Calendar, FileText, Plus, X, 
  RefreshCw, Check, AlertCircle, Printer, Eye, ExternalLink 
} from 'lucide-react';
import { BACKEND_URL } from '../config/api';

const MaterialTransferDC = ({ storeCode, storeName, isWarehouse = false }) => {
  const [activeTab, setActiveTab] = useState('create');
  const [transfers, setTransfers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stores, setStores] = useState([]);
  const [selectedTransfer, setSelectedTransfer] = useState(null);
  const [showReceiveModal, setShowReceiveModal] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    transfer_type: 'store_to_store',
    from_location: storeCode || '',
    from_location_name: storeName || '',
    to_location: '',
    to_location_name: '',
    to_location_address: '',
    to_location_city: '',
    to_location_state: 'Karnataka',
    to_location_pincode: '',
    to_contact_name: '',
    to_contact_phone: '',
    items: [{ product_name: '', hsn_code: '', quantity: 1, unit: 'pcs', rate: 0, serial_numbers: [] }],
    e_way_bill_number: '',
    e_way_bill_date: '',
    vehicle_number: '',
    transporter_name: '',
    expected_delivery_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    reason_for_transfer: '',
    notes: '',
    created_by: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).name : 'System'
  });

  const [receiveForm, setReceiveForm] = useState({
    goods_condition: 'good',
    receiver_remarks: 'Goods received in good condition'
  });

  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchStores();
    fetchTransfers();
  }, []);

  useEffect(() => {
    setFormData(prev => ({
      ...prev,
      from_location: storeCode || '',
      from_location_name: storeName || ''
    }));
  }, [storeCode, storeName]);

  const fetchStores = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/invoices/offline/stores`);
      const data = await response.json();
      if (data.stores) {
        setStores(data.stores);
      }
    } catch (error) {
      console.error('Error fetching stores:', error);
    }
  };

  const fetchTransfers = async () => {
    setLoading(true);
    try {
      const url = new URL(`${BACKEND_URL}/api/delivery-challans/material-transfer/list`);
      if (storeCode) {
        // Fetch both outgoing and incoming transfers
        url.searchParams.append('from_location', storeCode);
      }
      const response = await fetch(url);
      const data = await response.json();
      if (data.status === 'success') {
        setTransfers(data.challans || []);
      }
    } catch (error) {
      console.error('Error fetching transfers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddItem = () => {
    setFormData(prev => ({
      ...prev,
      items: [...prev.items, { product_name: '', hsn_code: '', quantity: 1, unit: 'pcs', rate: 0, serial_numbers: [] }]
    }));
  };

  const handleRemoveItem = (index) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }));
  };

  const handleItemChange = (index, field, value) => {
    setFormData(prev => {
      const newItems = [...prev.items];
      newItems[index] = { ...newItems[index], [field]: value };
      return { ...prev, items: newItems };
    });
  };

  // Handle transfer type change - update from/to locations accordingly
  const handleTransferTypeChange = (newType) => {
    let fromLocation = storeCode || '';
    let fromLocationName = storeName || '';
    
    // Determine the appropriate "from" location based on transfer type and current context
    if (newType === 'warehouse_to_store' || newType === 'warehouse_to_customer') {
      // If user is warehouse, keep current; otherwise they need to select
      if (isWarehouse) {
        fromLocation = storeCode || '';
        fromLocationName = storeName || 'Warehouse';
      } else {
        // Store user creating a warehouse transfer - they'll need to select warehouse
        fromLocation = '';
        fromLocationName = '';
      }
    } else {
      // Store to store, store to warehouse, store to customer
      fromLocation = storeCode || '';
      fromLocationName = storeName || '';
    }
    
    setFormData(prev => ({
      ...prev,
      transfer_type: newType,
      from_location: fromLocation,
      from_location_name: fromLocationName,
      // Reset destination when type changes
      to_location: '',
      to_location_name: '',
      to_location_address: '',
      to_location_city: '',
      to_location_state: 'Karnataka',
      to_location_pincode: '',
      to_contact_name: '',
      to_contact_phone: ''
    }));
  };

  // Get filtered destination options based on transfer type
  const getDestinationOptions = () => {
    const transferType = formData.transfer_type;
    
    if (transferType.includes('customer')) {
      // Customer transfers - no dropdown, use manual input
      return [];
    }
    
    if (transferType === 'store_to_warehouse') {
      // Filter to show only warehouses
      return stores.filter(s => s.is_warehouse && s.code !== storeCode);
    }
    
    if (transferType === 'warehouse_to_store') {
      // Filter to show only stores (not warehouses)
      return stores.filter(s => !s.is_warehouse && s.code !== storeCode);
    }
    
    // Default: store_to_store - show all stores except current
    return stores.filter(s => s.code !== storeCode);
  };

  // Get available "from" locations for warehouse transfers (when store user needs to select warehouse)
  const getFromLocationOptions = () => {
    const transferType = formData.transfer_type;
    
    if ((transferType === 'warehouse_to_store' || transferType === 'warehouse_to_customer') && !isWarehouse) {
      // Store user creating warehouse outbound - show warehouses
      return stores.filter(s => s.is_warehouse);
    }
    
    return [];
  };

  const handleFromLocationChange = (code) => {
    const store = stores.find(s => s.code === code);
    setFormData(prev => ({
      ...prev,
      from_location: code,
      from_location_name: store?.name || ''
    }));
  };

  const handleDestinationChange = (code) => {
    const store = stores.find(s => s.code === code);
    setFormData(prev => ({
      ...prev,
      to_location: code,
      to_location_name: store?.name || '',
      to_location_address: store?.address || '',
      to_location_city: store?.city || '',
      to_location_state: store?.state || 'Karnataka',
      to_location_pincode: store?.pincode || ''
    }));
  };

  const calculateTotalValue = () => {
    return formData.items.reduce((sum, item) => sum + (item.quantity * item.rate), 0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // For customer transfers, check customer name; for store transfers, check to_location
    if (formData.transfer_type.includes('customer')) {
      if (!formData.to_location_name) {
        alert('Please enter customer name');
        return;
      }
    } else {
      if (!formData.to_location) {
        alert('Please select destination');
        return;
      }
    }
    
    if (formData.items.some(item => !item.product_name || item.quantity < 1)) {
      alert('Please fill all item details');
      return;
    }

    setSubmitting(true);
    try {
      // Prepare payload - for customer transfers, use customer name as to_location_name
      const payload = {
        ...formData,
        to_location: formData.transfer_type.includes('customer') ? 'CUSTOMER' : formData.to_location,
        total_value: calculateTotalValue()
      };
      
      const response = await fetch(`${BACKEND_URL}/api/delivery-challans/material-transfer/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        alert(`Material Transfer DC ${data.challan_number} created successfully!${data.e_way_bill_required ? '\n\nNote: E-Way Bill is required for this transfer (value > ₹50,000)' : ''}`);
        
        // Reset form
        setFormData(prev => ({
          ...prev,
          to_location: '',
          to_location_name: '',
          to_location_address: '',
          to_location_city: '',
          to_location_pincode: '',
          to_contact_name: '',
          to_contact_phone: '',
          items: [{ product_name: '', hsn_code: '', quantity: 1, unit: 'pcs', rate: 0, serial_numbers: [] }],
          e_way_bill_number: '',
          e_way_bill_date: '',
          vehicle_number: '',
          transporter_name: '',
          reason_for_transfer: '',
          notes: ''
        }));
        
        fetchTransfers();
        setActiveTab('list');
      } else {
        alert(data.detail || 'Failed to create transfer DC');
      }
    } catch (error) {
      console.error('Error creating transfer:', error);
      alert('Error creating transfer DC');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReceive = async () => {
    if (!selectedTransfer) return;
    
    setSubmitting(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/delivery-challans/material-transfer/${selectedTransfer.id}/receive`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          challan_id: selectedTransfer.id,
          received_by: localStorage.getItem('storeUser') ? JSON.parse(localStorage.getItem('storeUser')).id : 'system',
          received_by_name: localStorage.getItem('storeUser') ? JSON.parse(localStorage.getItem('storeUser')).name : 'Store Manager',
          goods_condition: receiveForm.goods_condition,
          receiver_remarks: receiveForm.receiver_remarks
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        alert('Material received successfully!');
        setShowReceiveModal(false);
        setSelectedTransfer(null);
        fetchTransfers();
      } else {
        alert(data.detail || 'Failed to receive material');
      }
    } catch (error) {
      console.error('Error receiving material:', error);
      alert('Error receiving material');
    } finally {
      setSubmitting(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0
    }).format(amount || 0);
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { bg: 'bg-amber-100', text: 'text-amber-700', label: 'Pending' },
      in_transit: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'In Transit' },
      delivered: { bg: 'bg-green-100', text: 'text-green-700', label: 'Delivered' },
      cancelled: { bg: 'bg-red-100', text: 'text-red-700', label: 'Cancelled' }
    };
    const config = statusConfig[status] || statusConfig.pending;
    return (
      <span className={`px-2 py-1 text-xs rounded-full ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header with Tabs */}
      <div className="bg-white rounded-xl shadow-sm p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Truck className="w-6 h-6 text-teal-600" />
            <h2 className="text-xl font-bold text-gray-800">Material Transfer DC</h2>
          </div>
          <button
            onClick={fetchTransfers}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Refresh"
          >
            <RefreshCw className={`w-5 h-5 text-gray-600 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b">
          <button
            onClick={() => setActiveTab('create')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'create'
                ? 'border-teal-600 text-teal-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Plus className="w-4 h-4 inline mr-2" />
            Create Transfer
          </button>
          <button
            onClick={() => setActiveTab('list')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'list'
                ? 'border-teal-600 text-teal-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <FileText className="w-4 h-4 inline mr-2" />
            Transfer History ({transfers.length})
          </button>
        </div>
      </div>

      {/* Create Transfer Form */}
      {activeTab === 'create' && (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm p-6 space-y-6">
          {/* Transfer Type & Locations */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Transfer Type</label>
              <select
                value={formData.transfer_type}
                onChange={(e) => handleTransferTypeChange(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
              >
                <option value="store_to_store">Store to Store</option>
                <option value="warehouse_to_store">Warehouse to Store</option>
                <option value="store_to_warehouse">Store to Warehouse</option>
                <option value="store_to_customer">Store to Customer</option>
                <option value="warehouse_to_customer">Warehouse to Customer</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">From Location</label>
              {/* Show dropdown if user needs to select warehouse (store user doing warehouse outbound) */}
              {getFromLocationOptions().length > 0 ? (
                <select
                  value={formData.from_location}
                  onChange={(e) => handleFromLocationChange(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                  required
                >
                  <option value="">Select warehouse...</option>
                  {getFromLocationOptions().map(store => (
                    <option key={store.code} value={store.code}>
                      {store.name} ({store.code})
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  type="text"
                  value={formData.from_location_name || formData.from_location}
                  disabled
                  className="w-full px-3 py-2 border rounded-lg bg-gray-50"
                />
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">To Location *</label>
              {formData.transfer_type.includes('customer') ? (
                <input
                  type="text"
                  value={formData.to_location_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, to_location: 'CUSTOMER', to_location_name: e.target.value }))}
                  placeholder="Customer name"
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                  required
                />
              ) : (
                <select
                  value={formData.to_location}
                  onChange={(e) => handleDestinationChange(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                  required
                >
                  <option value="">Select destination...</option>
                  {getDestinationOptions().map(store => (
                    <option key={store.code} value={store.code}>
                      {store.name} ({store.code})
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>

          {/* Customer Details (if customer transfer) */}
          {formData.transfer_type.includes('customer') && (
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h4 className="font-medium text-blue-800 mb-3">Customer Details</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Customer Name *</label>
                  <input
                    type="text"
                    value={formData.to_location_name || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, to_location_name: e.target.value }))}
                    className="w-full px-3 py-2 border rounded-lg"
                    placeholder="Enter customer name"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Contact Phone *</label>
                  <input
                    type="text"
                    value={formData.to_contact_phone}
                    onChange={(e) => setFormData(prev => ({ ...prev, to_contact_phone: e.target.value }))}
                    className="w-full px-3 py-2 border rounded-lg"
                    placeholder="Mobile number"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={formData.to_contact_email || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, to_contact_email: e.target.value }))}
                    className="w-full px-3 py-2 border rounded-lg"
                    placeholder="customer@email.com"
                  />
                </div>
                <div className="md:col-span-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Address *</label>
                  <input
                    type="text"
                    value={formData.to_location_address}
                    onChange={(e) => setFormData(prev => ({ ...prev, to_location_address: e.target.value }))}
                    className="w-full px-3 py-2 border rounded-lg"
                    placeholder="Full delivery address"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                  <input
                    type="text"
                    value={formData.to_location_city}
                    onChange={(e) => setFormData(prev => ({ ...prev, to_location_city: e.target.value }))}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                  <input
                    type="text"
                    value={formData.to_location_state}
                    onChange={(e) => setFormData(prev => ({ ...prev, to_location_state: e.target.value }))}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Pincode</label>
                  <input
                    type="text"
                    value={formData.to_location_pincode}
                    onChange={(e) => setFormData(prev => ({ ...prev, to_location_pincode: e.target.value }))}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Items */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-medium text-gray-700">Items *</label>
              <button
                type="button"
                onClick={handleAddItem}
                className="px-3 py-1 text-sm bg-teal-100 text-teal-700 rounded-lg hover:bg-teal-200"
              >
                <Plus className="w-4 h-4 inline mr-1" />
                Add Item
              </button>
            </div>
            
            <div className="space-y-3">
              {formData.items.map((item, index) => (
                <div key={index} className="flex gap-3 items-start p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1 grid grid-cols-5 gap-2">
                    <input
                      type="text"
                      value={item.product_name}
                      onChange={(e) => handleItemChange(index, 'product_name', e.target.value)}
                      placeholder="Product name *"
                      className="col-span-2 px-3 py-2 border rounded-lg text-sm"
                      required
                    />
                    <input
                      type="text"
                      value={item.hsn_code}
                      onChange={(e) => handleItemChange(index, 'hsn_code', e.target.value)}
                      placeholder="HSN Code"
                      className="px-3 py-2 border rounded-lg text-sm"
                    />
                    <input
                      type="number"
                      value={item.quantity}
                      onChange={(e) => handleItemChange(index, 'quantity', parseInt(e.target.value) || 1)}
                      min="1"
                      className="px-3 py-2 border rounded-lg text-sm"
                    />
                    <input
                      type="number"
                      value={item.rate}
                      onChange={(e) => handleItemChange(index, 'rate', parseFloat(e.target.value) || 0)}
                      placeholder="Rate (optional)"
                      className="px-3 py-2 border rounded-lg text-sm"
                    />
                  </div>
                  {formData.items.length > 1 && (
                    <button
                      type="button"
                      onClick={() => handleRemoveItem(index)}
                      className="p-2 text-red-500 hover:bg-red-50 rounded-lg"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>
            
            {calculateTotalValue() > 0 && (
              <div className="mt-3 text-right">
                <span className="text-sm text-gray-500">Total Value: </span>
                <span className="font-bold text-lg">{formatCurrency(calculateTotalValue())}</span>
                {calculateTotalValue() >= 50000 && (
                  <span className="ml-2 px-2 py-1 text-xs bg-orange-100 text-orange-700 rounded">
                    E-Way Bill Required
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Transport & E-Way Bill */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                E-Way Bill Number
                <a 
                  href="https://ewaybillgst.gov.in" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="ml-2 text-blue-600 text-xs hover:underline"
                >
                  Generate E-Way Bill <ExternalLink className="w-3 h-3 inline" />
                </a>
              </label>
              <input
                type="text"
                value={formData.e_way_bill_number}
                onChange={(e) => setFormData(prev => ({ ...prev, e_way_bill_number: e.target.value }))}
                placeholder="E-Way Bill No."
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">E-Way Bill Date</label>
              <input
                type="date"
                value={formData.e_way_bill_date}
                onChange={(e) => setFormData(prev => ({ ...prev, e_way_bill_date: e.target.value }))}
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Vehicle Number</label>
              <input
                type="text"
                value={formData.vehicle_number}
                onChange={(e) => setFormData(prev => ({ ...prev, vehicle_number: e.target.value.toUpperCase() }))}
                placeholder="KA-01-XX-1234"
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Expected Delivery</label>
              <input
                type="date"
                value={formData.expected_delivery_date}
                onChange={(e) => setFormData(prev => ({ ...prev, expected_delivery_date: e.target.value }))}
                className="w-full px-3 py-2 border rounded-lg"
                required
              />
            </div>
          </div>

          {/* Reason & Notes */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Reason for Transfer</label>
              <input
                type="text"
                value={formData.reason_for_transfer}
                onChange={(e) => setFormData(prev => ({ ...prev, reason_for_transfer: e.target.value }))}
                placeholder="Stock balancing, customer request, etc."
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
              <input
                type="text"
                value={formData.notes}
                onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                placeholder="Additional notes..."
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end pt-4 border-t">
            <button
              type="submit"
              disabled={submitting}
              className="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50 flex items-center gap-2"
            >
              {submitting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4" />
                  Create Transfer DC
                </>
              )}
            </button>
          </div>
        </form>
      )}

      {/* Transfer History */}
      {activeTab === 'list' && (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-8 text-center">
              <RefreshCw className="w-8 h-8 text-gray-400 animate-spin mx-auto mb-2" />
              <p className="text-gray-500">Loading transfers...</p>
            </div>
          ) : transfers.length === 0 ? (
            <div className="p-8 text-center">
              <Truck className="w-12 h-12 text-gray-300 mx-auto mb-2" />
              <p className="text-gray-500">No material transfers found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left">Challan #</th>
                    <th className="px-4 py-3 text-left">From</th>
                    <th className="px-4 py-3 text-center">
                      <ArrowRight className="w-4 h-4 inline" />
                    </th>
                    <th className="px-4 py-3 text-left">To</th>
                    <th className="px-4 py-3 text-center">Items</th>
                    <th className="px-4 py-3 text-right">Value</th>
                    <th className="px-4 py-3 text-left">E-Way Bill</th>
                    <th className="px-4 py-3 text-center">Status</th>
                    <th className="px-4 py-3 text-center">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {transfers.map((transfer) => (
                    <tr key={transfer.id} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <span className="font-medium text-teal-700">{transfer.challan_number}</span>
                        <p className="text-xs text-gray-500">
                          {new Date(transfer.challan_date).toLocaleDateString('en-IN', {day: '2-digit', month: 'short', year: 'numeric'})}
                        </p>
                      </td>
                      <td className="px-4 py-3">
                        <p className="font-medium">{transfer.from_location?.name}</p>
                        <p className="text-xs text-gray-500">{transfer.from_location?.code}</p>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <ArrowRight className="w-4 h-4 text-gray-400 mx-auto" />
                      </td>
                      <td className="px-4 py-3">
                        <p className="font-medium">{transfer.to_location?.name}</p>
                        <p className="text-xs text-gray-500">{transfer.to_location?.code}</p>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className="px-2 py-1 bg-gray-100 rounded text-xs">
                          {transfer.total_quantity} items
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right font-medium">
                        {transfer.total_value > 0 ? formatCurrency(transfer.total_value) : '-'}
                      </td>
                      <td className="px-4 py-3">
                        {transfer.e_way_bill?.number ? (
                          <span className="text-xs text-green-700">{transfer.e_way_bill.number}</span>
                        ) : transfer.e_way_bill?.required ? (
                          <span className="text-xs text-orange-600">Required</span>
                        ) : (
                          <span className="text-xs text-gray-400">-</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-center">
                        {getStatusBadge(transfer.status)}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex items-center justify-center gap-1">
                          <button
                            onClick={() => setSelectedTransfer(transfer)}
                            className="p-1.5 bg-gray-100 text-gray-600 rounded hover:bg-gray-200"
                            title="View Details"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          {transfer.status === 'pending' && transfer.to_location?.code === storeCode && (
                            <button
                              onClick={() => {
                                setSelectedTransfer(transfer);
                                setShowReceiveModal(true);
                              }}
                              className="p-1.5 bg-green-100 text-green-600 rounded hover:bg-green-200"
                              title="Receive Material"
                            >
                              <Check className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* View Transfer Modal */}
      {selectedTransfer && !showReceiveModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-4 border-b bg-teal-600 text-white flex items-center justify-between rounded-t-xl">
              <h2 className="text-lg font-bold">Transfer DC: {selectedTransfer.challan_number}</h2>
              <button onClick={() => setSelectedTransfer(null)} className="p-1 hover:bg-teal-700 rounded-full">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              {/* Locations */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">From</p>
                  <p className="font-medium">{selectedTransfer.from_location?.name}</p>
                  <p className="text-sm text-gray-600">{selectedTransfer.from_location?.address}</p>
                </div>
                <div className="p-3 bg-teal-50 rounded-lg">
                  <p className="text-xs text-teal-600 mb-1">To</p>
                  <p className="font-medium">{selectedTransfer.to_location?.name}</p>
                  <p className="text-sm text-gray-600">{selectedTransfer.to_location?.address}</p>
                </div>
              </div>

              {/* Items */}
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Items</p>
                <table className="w-full text-sm border rounded-lg overflow-hidden">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-3 py-2 text-left">Product</th>
                      <th className="px-3 py-2 text-center">Qty</th>
                      <th className="px-3 py-2 text-right">Rate</th>
                      <th className="px-3 py-2 text-right">Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedTransfer.items?.map((item, idx) => (
                      <tr key={idx} className="border-t">
                        <td className="px-3 py-2">{item.product_name}</td>
                        <td className="px-3 py-2 text-center">{item.quantity} {item.unit}</td>
                        <td className="px-3 py-2 text-right">{formatCurrency(item.rate)}</td>
                        <td className="px-3 py-2 text-right font-medium">{formatCurrency(item.value)}</td>
                      </tr>
                    ))}
                    <tr className="border-t bg-gray-50">
                      <td colSpan="3" className="px-3 py-2 text-right font-medium">Total</td>
                      <td className="px-3 py-2 text-right font-bold">{formatCurrency(selectedTransfer.total_value)}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Transport Details */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">Vehicle Number</p>
                  <p className="font-medium">{selectedTransfer.vehicle_number || '-'}</p>
                </div>
                <div>
                  <p className="text-gray-500">E-Way Bill</p>
                  <p className="font-medium">{selectedTransfer.e_way_bill?.number || '-'}</p>
                </div>
                <div>
                  <p className="text-gray-500">Reason</p>
                  <p className="font-medium">{selectedTransfer.reason_for_transfer || '-'}</p>
                </div>
                <div>
                  <p className="text-gray-500">Status</p>
                  {getStatusBadge(selectedTransfer.status)}
                </div>
              </div>

              {/* Receipt Confirmation */}
              {selectedTransfer.receipt_confirmation && (
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <p className="font-medium text-green-800 mb-2">Goods Received Confirmation</p>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <p><span className="text-gray-500">Received By:</span> {selectedTransfer.receipt_confirmation.received_by_name}</p>
                    <p><span className="text-gray-500">Condition:</span> {selectedTransfer.receipt_confirmation.goods_condition}</p>
                    <p className="col-span-2"><span className="text-gray-500">Remarks:</span> {selectedTransfer.receipt_confirmation.receiver_remarks}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Receive Material Modal */}
      {showReceiveModal && selectedTransfer && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full">
            <div className="p-4 border-b bg-green-600 text-white flex items-center justify-between rounded-t-xl">
              <h2 className="text-lg font-bold">Receive Material</h2>
              <button onClick={() => { setShowReceiveModal(false); setSelectedTransfer(null); }} className="p-1 hover:bg-green-700 rounded-full">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div className="p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">Transfer DC</p>
                <p className="font-bold text-lg">{selectedTransfer.challan_number}</p>
                <p className="text-sm text-gray-600">
                  {selectedTransfer.total_quantity} items from {selectedTransfer.from_location?.name}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Goods Condition</label>
                <select
                  value={receiveForm.goods_condition}
                  onChange={(e) => setReceiveForm(prev => ({ ...prev, goods_condition: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-lg"
                >
                  <option value="good">Good Condition</option>
                  <option value="damaged">Damaged</option>
                  <option value="partial">Partial Received</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Remarks</label>
                <textarea
                  value={receiveForm.receiver_remarks}
                  onChange={(e) => setReceiveForm(prev => ({ ...prev, receiver_remarks: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-lg"
                  rows={2}
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => { setShowReceiveModal(false); setSelectedTransfer(null); }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleReceive}
                  disabled={submitting}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {submitting ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Check className="w-4 h-4" />
                  )}
                  Confirm Receipt
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MaterialTransferDC;
