import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Wrench, Search, Filter, CheckCircle, Clock, AlertCircle, 
  XCircle, Eye, Edit, Mail, Phone, MapPin, Package, Plus, X
} from 'lucide-react';
import AdminHeader from './AdminHeader';


const ServiceTicketManagement = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [showUpdateModal, setShowUpdateModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [updateForm, setUpdateForm] = useState({
    brand_complaint_number: '',
    status: '',
    resolution_notes: ''
  });
  const [createForm, setCreateForm] = useState({
    customer_name: '',
    customer_phone: '',
    customer_email: '',
    customer_address: '',
    product_name: '',
    brand: 'Bosch',
    model_number: '',
    issue_description: '',
    priority: 'normal'
  });

  useEffect(() => {
    fetchTickets();
  }, [filterStatus]);

  const normalizeTicket = (t) => ({
    ...t,
    ticket_id: t.ticket_id || t.ticket_number || t.id,
    customer_name: t.customer_name || t.customer_details?.name || '',
    customer_phone: t.customer_phone || t.customer_details?.phone || '',
    customer_email: t.customer_email || t.customer_details?.email || '',
    brand: t.brand || t.product_details?.brand || '',
    product_name: t.product_name || t.product_details?.product_name || '',
    status: t.status || 'open',
  });

  const fetchTickets = async () => {
    try {
      setLoading(true);
      const url = filterStatus 
        ? `${BACKEND_URL}/api/service-tickets/?status=${filterStatus}`
        : `${BACKEND_URL}/api/service-tickets/`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.status === 'success') {
        setTickets((data.tickets || []).map(normalizeTicket));
      }
    } catch (error) {
      console.error('Error fetching tickets:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'open': 'bg-blue-100 text-blue-800',
      'awaiting_brand_response': 'bg-yellow-100 text-yellow-800',
      'brand_ticket_created': 'bg-purple-100 text-purple-800',
      'in_progress': 'bg-orange-100 text-orange-800',
      'resolved': 'bg-green-100 text-green-800',
      'closed': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'open':
        return <AlertCircle className="w-4 h-4" />;
      case 'awaiting_brand_response':
      case 'brand_ticket_created':
        return <Clock className="w-4 h-4" />;
      case 'in_progress':
        return <Wrench className="w-4 h-4" />;
      case 'resolved':
        return <CheckCircle className="w-4 h-4" />;
      case 'closed':
        return <XCircle className="w-4 h-4" />;
      default:
        return <AlertCircle className="w-4 h-4" />;
    }
  };

  const handleUpdateTicket = async () => {
    try {
      if (!selectedTicket) return;

      const response = await fetch(
        `${BACKEND_URL}/api/service-tickets/${selectedTicket.ticket_id}/update`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updateForm)
        }
      );

      const data = await response.json();
      
      if (data.status === 'success') {
        alert('✅ Ticket updated successfully! Customer notified via email.');
        setShowUpdateModal(false);
        setSelectedTicket(null);
        setUpdateForm({ brand_complaint_number: '', status: '', resolution_notes: '' });
        fetchTickets();
      } else {
        alert('Failed to update ticket');
      }
    } catch (error) {
      console.error('Error updating ticket:', error);
      alert('Error updating ticket');
    }
  };

  const handleCreateTicket = async (e) => {
    e.preventDefault();
    try {
      const ticketData = {
        customer_details: {
          name: createForm.customer_name,
          phone: createForm.customer_phone,
          email: createForm.customer_email,
          address: createForm.customer_address
        },
        product_details: {
          product_name: createForm.product_name,
          brand: createForm.brand,
          model_number: createForm.model_number
        },
        issue_description: createForm.issue_description,
        priority: createForm.priority,
        source: 'manual_entry'
      };

      const response = await fetch(`${BACKEND_URL}/api/service-tickets/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ticketData)
      });

      const data = await response.json();
      
      if (response.ok && data.status === 'success') {
        alert(`✅ Service ticket ${data.ticket_id} created successfully!`);
        setShowCreateModal(false);
        setCreateForm({
          customer_name: '', customer_phone: '', customer_email: '', customer_address: '',
          product_name: '', brand: 'Bosch', model_number: '', issue_description: '', priority: 'normal'
        });
        fetchTickets();
      } else {
        alert(data.detail || 'Failed to create ticket');
      }
    } catch (error) {
      console.error('Error creating ticket:', error);
      alert('Error creating ticket');
    }
  };

  const openUpdateModal = (ticket) => {
    setSelectedTicket(ticket);
    setUpdateForm({
      brand_complaint_number: ticket.brand_complaint_number || '',
      status: ticket.status,
      resolution_notes: ticket.resolution_notes || ''
    });
    setShowUpdateModal(true);
  };

  const filteredTickets = tickets.filter(ticket => {
    const searchLower = searchTerm.toLowerCase();
    return (
      (ticket.ticket_id || '').toLowerCase().includes(searchLower) ||
      (ticket.customer_name || '').toLowerCase().includes(searchLower) ||
      (ticket.customer_email || '').toLowerCase().includes(searchLower) ||
      (ticket.brand || '').toLowerCase().includes(searchLower)
    );
  });

  const stats = {
    total: tickets.length,
    open: tickets.filter(t => t.status === 'open').length,
    awaiting: tickets.filter(t => t.status === 'awaiting_brand_response').length,
    in_progress: tickets.filter(t => t.status === 'in_progress').length,
    resolved: tickets.filter(t => t.status === 'resolved').length
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <AdminHeader 
        title="Service Tickets" 
        icon={Wrench}
        breadcrumb={[{ label: 'Service Tickets' }]}
      />
      
      <div className="p-6">
        {/* Header */}
      <div className="mb-6 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Wrench className="w-8 h-8 text-red-700" />
            Service Ticket Management
          </h1>
          <p className="text-gray-600 mt-2">Manage customer service requests and track resolutions</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-red-700 text-white rounded-lg hover:bg-red-800 transition-colors"
          data-testid="create-ticket-btn"
        >
          <Plus className="w-5 h-5" />
          Create Ticket
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
          <div className="text-sm text-gray-600">Total Tickets</div>
        </div>
        <div className="bg-blue-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-blue-700">{stats.open}</div>
          <div className="text-sm text-blue-600">Open</div>
        </div>
        <div className="bg-yellow-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-yellow-700">{stats.awaiting}</div>
          <div className="text-sm text-yellow-600">Awaiting Brand</div>
        </div>
        <div className="bg-orange-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-orange-700">{stats.in_progress}</div>
          <div className="text-sm text-orange-600">In Progress</div>
        </div>
        <div className="bg-green-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-green-700">{stats.resolved}</div>
          <div className="text-sm text-green-600">Resolved</div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search by ticket ID, customer name, email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500"
          >
            <option value="">All Status</option>
            <option value="open">Open</option>
            <option value="awaiting_brand_response">Awaiting Brand</option>
            <option value="brand_ticket_created">Brand Ticket Created</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
        </div>
      </div>

      {/* Tickets Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-700 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading tickets...</p>
          </div>
        ) : filteredTickets.length === 0 ? (
          <div className="p-8 text-center">
            <Wrench className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600">No service tickets found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ticket ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Customer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Product
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Issue
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Brand Ticket
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredTickets.map((ticket) => (
                  <tr key={ticket.ticket_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {ticket.ticket_id}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {ticket.customer_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {ticket.customer_phone}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {ticket.brand}
                      </div>
                      <div className="text-sm text-gray-500">
                        {ticket.product_name}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 max-w-xs truncate">
                        {ticket.issue_description}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(ticket.status)}`}>
                        {getStatusIcon(ticket.status)}
                        {(ticket.status || 'open').replace(/_/g, ' ').toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {ticket.brand_complaint_number || '-'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {new Date(ticket.created_at).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => openUpdateModal(ticket)}
                        className="text-red-700 hover:text-red-900 flex items-center gap-1"
                      >
                        <Edit className="w-4 h-4" />
                        Update
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Update Modal */}
      {showUpdateModal && selectedTicket && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <Edit className="w-6 h-6 text-red-700" />
                Update Service Ticket
              </h2>

              {/* Ticket Info */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-xs text-gray-500">Ticket ID</div>
                    <div className="font-medium">{selectedTicket.ticket_id}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">Customer</div>
                    <div className="font-medium">{selectedTicket.customer_name}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">Product</div>
                    <div className="font-medium">{selectedTicket.brand} - {selectedTicket.product_name}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">Current Status</div>
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedTicket.status)}`}>
                      {(selectedTicket.status || 'open').replace(/_/g, ' ').toUpperCase()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Update Form */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Brand Complaint Number
                  </label>
                  <input
                    type="text"
                    value={updateForm.brand_complaint_number}
                    onChange={(e) => setUpdateForm({...updateForm, brand_complaint_number: e.target.value})}
                    placeholder="Enter brand complaint/ticket number"
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Customer will be notified via email with this number
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Update Status
                  </label>
                  <select
                    value={updateForm.status}
                    onChange={(e) => setUpdateForm({...updateForm, status: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500"
                  >
                    <option value="open">Open</option>
                    <option value="awaiting_brand_response">Awaiting Brand Response</option>
                    <option value="brand_ticket_created">Brand Ticket Created</option>
                    <option value="in_progress">In Progress</option>
                    <option value="resolved">Resolved</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>

                {(updateForm.status === 'resolved' || updateForm.status === 'closed') && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Resolution Notes
                    </label>
                    <textarea
                      value={updateForm.resolution_notes}
                      onChange={(e) => setUpdateForm({...updateForm, resolution_notes: e.target.value})}
                      placeholder="Describe how the issue was resolved..."
                      rows="3"
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500"
                    ></textarea>
                    <p className="text-xs text-gray-500 mt-1">
                      This will be included in the resolution email to customer
                    </p>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleUpdateTicket}
                  className="flex-1 bg-red-700 text-white px-4 py-2 rounded-lg hover:bg-red-800 transition-colors"
                >
                  Update & Notify Customer
                </button>
                <button
                  onClick={() => {
                    setShowUpdateModal(false);
                    setSelectedTicket(null);
                  }}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Ticket Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b flex items-center justify-between sticky top-0 bg-white">
              <h2 className="text-xl font-bold text-gray-800">Create Service Ticket</h2>
              <button onClick={() => setShowCreateModal(false)} className="p-2 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreateTicket} className="p-6 space-y-4">
              {/* Customer Details */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-700 mb-3">Customer Details</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Customer Name *</label>
                    <input
                      type="text"
                      value={createForm.customer_name}
                      onChange={(e) => setCreateForm({...createForm, customer_name: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-red-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone *</label>
                    <input
                      type="tel"
                      value={createForm.customer_phone}
                      onChange={(e) => setCreateForm({...createForm, customer_phone: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-red-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                      type="email"
                      value={createForm.customer_email}
                      onChange={(e) => setCreateForm({...createForm, customer_email: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-red-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                    <input
                      type="text"
                      value={createForm.customer_address}
                      onChange={(e) => setCreateForm({...createForm, customer_address: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-red-500"
                    />
                  </div>
                </div>
              </div>

              {/* Product Details */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-700 mb-3">Product Details</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Product Name *</label>
                    <input
                      type="text"
                      value={createForm.product_name}
                      onChange={(e) => setCreateForm({...createForm, product_name: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-red-500"
                      placeholder="e.g., Built-in Oven"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Brand *</label>
                    <select
                      value={createForm.brand}
                      onChange={(e) => setCreateForm({...createForm, brand: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-red-500"
                      required
                    >
                      <option value="Bosch">Bosch</option>
                      <option value="Siemens">Siemens</option>
                      <option value="Electrolux">Electrolux</option>
                      <option value="Hindware">Hindware</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Model Number</label>
                    <input
                      type="text"
                      value={createForm.model_number}
                      onChange={(e) => setCreateForm({...createForm, model_number: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-red-500"
                      placeholder="e.g., BEL550MS0I"
                    />
                  </div>
                </div>
              </div>

              {/* Issue Details */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-700 mb-3">Issue Details</h3>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Issue Description *</label>
                  <textarea
                    value={createForm.issue_description}
                    onChange={(e) => setCreateForm({...createForm, issue_description: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-red-500"
                    rows={4}
                    placeholder="Describe the issue in detail..."
                    required
                  ></textarea>
                </div>
                <div className="mt-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                  <select
                    value={createForm.priority}
                    onChange={(e) => setCreateForm({...createForm, priority: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-red-500"
                  >
                    <option value="low">Low</option>
                    <option value="normal">Normal</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-red-700 text-white rounded-lg hover:bg-red-800"
                >
                  Create Ticket
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      </div>
    </div>
  );
};

export default ServiceTicketManagement;
