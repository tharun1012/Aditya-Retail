import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { Truck, Plus, Search, Eye, MapPin, Camera, CheckCircle, Clock, XCircle, ArrowLeft } from 'lucide-react';
import DocumentActions from './DocumentActions';


const DeliveryChallanManagement = () => {
  const navigate = useNavigate();
  const [challans, setChallans] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [deliveryPersons, setDeliveryPersons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedChallan, setSelectedChallan] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  const [formData, setFormData] = useState({
    invoice_id: '',
    delivery_person_id: '',
    vehicle_number: '',
    expected_delivery_date: new Date().toISOString().split('T')[0],
    notes: '',
    created_by: 'admin'
  });

  useEffect(() => {
    fetchChallans();
    fetchInvoices();
    fetchDeliveryPersons();
  }, [statusFilter]);

  const fetchChallans = async () => {
    setLoading(true);
    try {
      const url = statusFilter === 'all' 
        ? `${BACKEND_URL}/api/delivery-challans/`
        : `${BACKEND_URL}/api/delivery-challans/?status=${statusFilter}`;
      
      const response = await fetch(url);
      const data = await response.json();
      if (data.status === 'success') {
        setChallans(data.challans);
      }
    } catch (error) {
      console.error('Failed to fetch challans:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchInvoices = async () => {
    try {
      // Fetch invoices that don't have delivery challans yet
      const response = await fetch(`${BACKEND_URL}/api/invoices/offline/`);
      const data = await response.json();
      if (data.status === 'success') {
        // Filter invoices without delivery challan
        const availableInvoices = data.invoices.filter(inv => !inv.delivery_challan_id);
        setInvoices(availableInvoices);
      }
    } catch (error) {
      console.error('Failed to fetch invoices:', error);
    }
  };

  const fetchDeliveryPersons = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`${BACKEND_URL}/api/auth/delivery-persons`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      if (data.status === 'success') {
        setDeliveryPersons(data.delivery_persons || []);
      }
    } catch (error) {
      console.error('Failed to fetch delivery persons:', error);
    }
  };

  const handleCreateChallan = async () => {
    try {
      const adminUser = JSON.parse(localStorage.getItem('admin_user') || '{}');
      const payload = {
        ...formData,
        created_by: adminUser.email || 'admin'
      };

      const response = await fetch(`${BACKEND_URL}/api/delivery-challans/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (data.status === 'success') {
        alert(`Delivery Challan Created: ${data.challan_number}`);
        setShowCreateModal(false);
        fetchChallans();
        fetchInvoices();
        resetForm();
      } else {
        alert('Failed to create delivery challan');
      }
    } catch (error) {
      console.error('Failed to create challan:', error);
      alert('Failed to create delivery challan');
    }
  };

  const resetForm = () => {
    setFormData({
      invoice_id: '',
      delivery_person_id: '',
      vehicle_number: '',
      expected_delivery_date: new Date().toISOString().split('T')[0],
      notes: '',
      created_by: 'admin'
    });
  };

  const updateStatus = async (challanId, newStatus) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/delivery-challans/${challanId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStatus,
          delivered_by: formData.delivery_person_name
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        alert(`Status updated to ${newStatus}`);
        fetchChallans();
      }
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };

  const getDeliveryLink = async (challanId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/delivery-challans/${challanId}/delivery-link`);
      const data = await response.json();
      
      if (data.status === 'success') {
        // Copy link to clipboard
        navigator.clipboard.writeText(data.delivery_link);
        alert('Delivery link copied to clipboard! Share this with delivery person.');
      }
    } catch (error) {
      console.error('Failed to get delivery link:', error);
    }
  };

  const filteredChallans = challans.filter(challan => {
    const matchesSearch = challan.challan_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         challan.customer?.name?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
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
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Truck className="text-green-500" />
              Delivery Challan Management
            </h1>
            <p className="text-gray-600 mt-1">Create and track delivery challans with real-time updates</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 flex items-center gap-2"
          >
            <Plus size={20} />
            Create Challan
          </button>
        </div>

        {/* Filters */}
        <div className="flex gap-4 mb-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search by challan number or customer..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="in_transit">In Transit</option>
            <option value="delivered">Delivered</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {/* Challans List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Challan #</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Invoice #</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Delivery Person</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Expected Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredChallans.length === 0 ? (
              <tr>
                <td colSpan="7" className="px-6 py-12 text-center text-gray-500">
                  No delivery challans found
                </td>
              </tr>
            ) : (
              filteredChallans.map((challan) => (
                <tr key={challan.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {challan.challan_number}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {challan.invoice_number}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div>
                      <div className="font-medium">{challan.customer?.name}</div>
                      <div className="text-gray-500 text-xs">{challan.customer?.phone}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div>
                      <div>{challan.delivery_person_name}</div>
                      <div className="text-xs">{challan.delivery_person_phone}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {challan.expected_delivery_date}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      challan.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      challan.status === 'in_transit' ? 'bg-blue-100 text-blue-800' :
                      challan.status === 'delivered' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {challan.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => {
                        setSelectedChallan(challan);
                        setShowDetailsModal(true);
                      }}
                      className="text-green-600 hover:text-green-900"
                      title="View Details"
                    >
                      <Eye size={18} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Create Challan Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 my-8">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold">Create Delivery Challan</h2>
            </div>
            <div className="p-6 max-h-[70vh] overflow-y-auto">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Select Invoice *</label>
                  <select
                    value={formData.invoice_id}
                    onChange={(e) => setFormData({ ...formData, invoice_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    required
                  >
                    <option value="">-- Select Invoice --</option>
                    {invoices.map(inv => (
                      <option key={inv.id} value={inv.id}>
                        {inv.invoice_number} - {inv.customer?.name} - ₹{inv.total_amount?.toFixed(2)}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Delivery Person *</label>
                  <select
                    value={formData.delivery_person_id}
                    onChange={(e) => setFormData({ ...formData, delivery_person_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    required
                  >
                    <option value="">-- Select Delivery Person --</option>
                    {deliveryPersons.map(person => (
                      <option key={person.id} value={person.id}>
                        {person.full_name} - {person.phone} {person.vehicle_number ? `(${person.vehicle_number})` : ''}
                      </option>
                    ))}
                  </select>
                  {deliveryPersons.length === 0 && (
                    <p className="text-sm text-orange-600 mt-1">No delivery persons available. Create one first.</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Vehicle Number</label>
                  <input
                    type="text"
                    value={formData.vehicle_number}
                    onChange={(e) => setFormData({ ...formData, vehicle_number: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    placeholder="Enter vehicle number"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Expected Delivery Date *</label>
                  <input
                    type="date"
                    value={formData.expected_delivery_date}
                    onChange={(e) => setFormData({ ...formData, expected_delivery_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    rows="3"
                    placeholder="Additional notes for delivery"
                  />
                </div>
              </div>
            </div>
            <div className="p-6 border-t border-gray-200 flex justify-end gap-2">
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
                onClick={handleCreateChallan}
                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
              >
                Create Challan
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Details Modal */}
      {showDetailsModal && selectedChallan && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold">Delivery Challan Details</h2>
              <p className="text-gray-600">{selectedChallan.challan_number}</p>
            </div>
            <div className="p-6">
              {/* Status and Actions */}
              <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-sm text-gray-600">Current Status</p>
                    <p className="text-2xl font-bold text-blue-900">{selectedChallan.status?.toUpperCase()}</p>
                  </div>
                  <div className="flex gap-2">
                    {selectedChallan.status === 'pending' && (
                      <button
                        onClick={() => updateStatus(selectedChallan.id, 'in_transit')}
                        className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
                      >
                        Mark In Transit
                      </button>
                    )}
                    {selectedChallan.status === 'in_transit' && (
                      <button
                        onClick={() => updateStatus(selectedChallan.id, 'delivered')}
                        className="px-3 py-1 bg-green-500 text-white rounded text-sm hover:bg-green-600"
                      >
                        Mark Delivered
                      </button>
                    )}
                    <button
                      onClick={() => getDeliveryLink(selectedChallan.id)}
                      className="px-3 py-1 bg-purple-500 text-white rounded text-sm hover:bg-purple-600"
                    >
                      Copy Delivery Link
                    </button>
                  </div>
                </div>
              </div>

              {/* Delivery Info */}
              <div className="grid grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="font-semibold text-lg mb-3">Delivery Information</h3>
                  <div className="space-y-2">
                    <p><strong>Person:</strong> {selectedChallan.delivery_person_name}</p>
                    <p><strong>Phone:</strong> {selectedChallan.delivery_person_phone}</p>
                    <p><strong>Vehicle:</strong> {selectedChallan.vehicle_number || 'N/A'}</p>
                    <p><strong>Expected Date:</strong> {selectedChallan.expected_delivery_date}</p>
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-3">Customer Information</h3>
                  <div className="space-y-2">
                    <p><strong>Name:</strong> {selectedChallan.customer?.name}</p>
                    <p><strong>Phone:</strong> {selectedChallan.customer?.phone}</p>
                    <p><strong>Address:</strong> {selectedChallan.customer?.address}</p>
                    {selectedChallan.google_maps_link && (
                      <a
                        href={selectedChallan.google_maps_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800"
                      >
                        <MapPin size={16} />
                        Open in Google Maps
                      </a>
                    )}
                  </div>
                </div>
              </div>

              {/* Items */}
              <div className="mb-6">
                <h3 className="font-semibold text-lg mb-3">Items</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs">Product</th>
                        <th className="px-4 py-2 text-left text-xs">Quantity</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y">
                      {selectedChallan.items?.map((item, idx) => (
                        <tr key={idx}>
                          <td className="px-4 py-2 text-sm">{item.product_name}</td>
                          <td className="px-4 py-2 text-sm">{item.quantity}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Delivery Photos */}
              {selectedChallan.delivery_photos && selectedChallan.delivery_photos.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold text-lg mb-3">Delivery Photos</h3>
                  <div className="grid grid-cols-3 gap-4">
                    {selectedChallan.delivery_photos.map((photo, idx) => (
                      <img
                        key={idx}
                        src={`${BACKEND_URL}${photo.url}`}
                        alt={`Delivery ${idx + 1}`}
                        className="w-full h-48 object-cover rounded-lg border"
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Document Actions */}
              <div className="border-t border-gray-200 pt-4">
                <h3 className="font-semibold text-lg mb-3">Document Actions</h3>
                <DocumentActions 
                  document={selectedChallan} 
                  documentType="delivery-challan"
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
    </div>
  );
};

export default DeliveryChallanManagement;