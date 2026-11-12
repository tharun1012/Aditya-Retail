import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  FileText, Search, Filter, RefreshCw, Mail, User, Phone, Calendar,
  Clock, CheckCircle, AlertCircle, Eye, Download, Send, UserPlus,
  ChevronLeft, ChevronRight, TrendingUp, Users, MailCheck
} from 'lucide-react';


const ConsultationManagement = () => {
  const [consultations, setConsultations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({});
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedConsultation, setSelectedConsultation] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [assignData, setAssignData] = useState({ assigned_to: '', follow_up_date: '', notes: '' });

  useEffect(() => {
    fetchConsultations();
  }, [page, statusFilter]);

  const fetchConsultations = async () => {
    setLoading(true);
    try {
      let url = `${BACKEND_URL}/api/consultation/admin/list?page=${page}&limit=10`;
      if (statusFilter) url += `&status=${statusFilter}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.status === 'success') {
        setConsultations(data.consultations);
        setTotalPages(data.pages);
        setStats(data.stats);
      }
    } catch (error) {
      console.error('Error fetching consultations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchConsultations();
  };

  const viewDetail = async (consultation) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/consultation/admin/detail/${consultation.id}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setSelectedConsultation({ ...data.consultation, lead: data.lead });
        setShowDetailModal(true);
      }
    } catch (error) {
      console.error('Error fetching detail:', error);
    }
  };

  const resendEmail = async (consultationId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/consultation/admin/resend-email/${consultationId}`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        alert('Email sent successfully!');
        fetchConsultations();
      } else {
        alert('Failed to send email: ' + data.message);
      }
    } catch (error) {
      alert('Error sending email');
    }
  };

  const openAssignModal = (consultation) => {
    setSelectedConsultation(consultation);
    setAssignData({
      assigned_to: consultation.assigned_to || '',
      follow_up_date: consultation.follow_up_date || '',
      notes: consultation.admin_notes || ''
    });
    setShowAssignModal(true);
  };

  const handleAssign = async () => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/consultation/admin/assign/${selectedConsultation.id}?assigned_to=${encodeURIComponent(assignData.assigned_to)}&follow_up_date=${assignData.follow_up_date}&notes=${encodeURIComponent(assignData.notes)}`,
        { method: 'PUT' }
      );
      const data = await response.json();
      
      if (data.status === 'success') {
        alert('Assigned successfully!');
        setShowAssignModal(false);
        fetchConsultations();
      }
    } catch (error) {
      alert('Error assigning consultation');
    }
  };

  const viewHtmlReport = async (consultationId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/consultation/admin/html-report/${consultationId}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        // Open report in new window
        const newWindow = window.open('', '_blank');
        newWindow.document.write(data.html_report);
        newWindow.document.close();
      }
    } catch (error) {
      alert('Error loading report');
    }
  };

  const getStatusBadge = (status, emailSent) => {
    if (status === 'completed' && emailSent) {
      return <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium flex items-center gap-1"><CheckCircle className="w-3 h-3" /> Sent</span>;
    } else if (status === 'completed') {
      return <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs font-medium flex items-center gap-1"><AlertCircle className="w-3 h-3" /> Completed</span>;
    } else if (status === 'processing') {
      return <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium flex items-center gap-1"><Clock className="w-3 h-3" /> Processing</span>;
    } else {
      return <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium flex items-center gap-1"><Clock className="w-3 h-3" /> Pending</span>;
    }
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
          <FileText className="w-7 h-7 text-blue-600" />
          Expert Consultation Management
        </h1>
        <p className="text-gray-600 mt-1">Track and manage customer consultation requests</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Consultations</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_consultations || 0}</p>
            </div>
            <Users className="w-10 h-10 text-blue-500 opacity-50" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Pending</p>
              <p className="text-2xl font-bold text-gray-900">{stats.pending || 0}</p>
            </div>
            <Clock className="w-10 h-10 text-yellow-500 opacity-50" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Completed</p>
              <p className="text-2xl font-bold text-gray-900">{stats.completed || 0}</p>
            </div>
            <CheckCircle className="w-10 h-10 text-green-500 opacity-50" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Emails Sent</p>
              <p className="text-2xl font-bold text-gray-900">{stats.emails_sent || 0}</p>
            </div>
            <MailCheck className="w-10 h-10 text-purple-500 opacity-50" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex flex-wrap gap-4 items-center">
          <form onSubmit={handleSearch} className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name, email, phone..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </form>
          
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
          </select>
          
          <button
            onClick={fetchConsultations}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Consultations Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading...</div>
        ) : consultations.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No consultations found</div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Budget</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Appliances</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Assigned</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {consultations.map((consultation) => (
                <tr key={consultation.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div>
                      <p className="font-medium text-gray-900">{consultation.customer_name}</p>
                      <p className="text-sm text-gray-500">{consultation.email}</p>
                      {consultation.phone && <p className="text-xs text-gray-400">{consultation.phone}</p>}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <p className="text-sm text-gray-900">
                      ₹{(consultation.requirements?.budget_min || 0).toLocaleString()} - ₹{(consultation.requirements?.budget_max || 0).toLocaleString()}
                    </p>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {(consultation.requirements?.appliance_types || []).slice(0, 3).map((type, i) => (
                        <span key={i} className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">
                          {type}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {getStatusBadge(consultation.status, consultation.email_sent)}
                  </td>
                  <td className="px-4 py-3">
                    {consultation.assigned_to ? (
                      <span className="text-sm text-gray-900">{consultation.assigned_to}</span>
                    ) : (
                      <span className="text-sm text-gray-400">Unassigned</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <p className="text-sm text-gray-600">
                      {new Date(consultation.created_at).toLocaleDateString()}
                    </p>
                    <p className="text-xs text-gray-400">
                      {new Date(consultation.created_at).toLocaleTimeString()}
                    </p>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-center gap-2">
                      <button
                        onClick={() => viewDetail(consultation)}
                        className="p-1.5 text-blue-600 hover:bg-blue-50 rounded"
                        title="View Details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      {consultation.status === 'completed' && (
                        <>
                          <button
                            onClick={() => viewHtmlReport(consultation.id)}
                            className="p-1.5 text-green-600 hover:bg-green-50 rounded"
                            title="View Report"
                          >
                            <FileText className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => resendEmail(consultation.id)}
                            className="p-1.5 text-purple-600 hover:bg-purple-50 rounded"
                            title="Resend Email"
                          >
                            <Send className="w-4 h-4" />
                          </button>
                        </>
                      )}
                      <button
                        onClick={() => openAssignModal(consultation)}
                        className="p-1.5 text-orange-600 hover:bg-orange-50 rounded"
                        title="Assign to Sales"
                      >
                        <UserPlus className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        
        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-4 py-3 border-t flex items-center justify-between">
            <p className="text-sm text-gray-500">
              Page {page} of {totalPages}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {showDetailModal && selectedConsultation && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{selectedConsultation.customer_name}</h2>
                  <p className="text-gray-500">{selectedConsultation.email}</p>
                </div>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
            </div>
            
            <div className="p-6 space-y-4">
              {/* Contact Info */}
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-2">
                  <Phone className="w-4 h-4 text-gray-400" />
                  <span>{selectedConsultation.phone || 'No phone'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span>{new Date(selectedConsultation.created_at).toLocaleString()}</span>
                </div>
              </div>
              
              {/* Requirements */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold mb-3">Requirements</h3>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div><span className="text-gray-500">Kitchen Size:</span> {selectedConsultation.requirements?.kitchen_size}</div>
                  <div><span className="text-gray-500">Family Size:</span> {selectedConsultation.requirements?.family_size}</div>
                  <div><span className="text-gray-500">Budget:</span> ₹{selectedConsultation.requirements?.budget_min?.toLocaleString()} - ₹{selectedConsultation.requirements?.budget_max?.toLocaleString()}</div>
                  <div><span className="text-gray-500">Cooking:</span> {selectedConsultation.requirements?.cooking_frequency}</div>
                </div>
                <div className="mt-3">
                  <span className="text-gray-500 text-sm">Appliances:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedConsultation.requirements?.appliance_types?.map((type, i) => (
                      <span key={i} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">{type}</span>
                    ))}
                  </div>
                </div>
                <div className="mt-3">
                  <span className="text-gray-500 text-sm">Brand Preference:</span>
                  <p>{selectedConsultation.requirements?.brand_preference?.join(', ')}</p>
                </div>
                {selectedConsultation.requirements?.special_requirements && (
                  <div className="mt-3">
                    <span className="text-gray-500 text-sm">Special Requirements:</span>
                    <p>{selectedConsultation.requirements.special_requirements}</p>
                  </div>
                )}
              </div>
              
              {/* Status & Report */}
              <div className="flex items-center justify-between bg-blue-50 rounded-lg p-4">
                <div>
                  <p className="text-sm text-gray-500">Status</p>
                  {getStatusBadge(selectedConsultation.status, selectedConsultation.email_sent)}
                </div>
                <div>
                  <p className="text-sm text-gray-500">Products Matched</p>
                  <p className="font-semibold">{selectedConsultation.products_matched || 0}</p>
                </div>
                {selectedConsultation.status === 'completed' && (
                  <button
                    onClick={() => viewHtmlReport(selectedConsultation.id)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                  >
                    <FileText className="w-4 h-4" />
                    View Report
                  </button>
                )}
              </div>
              
              {/* Lead Info */}
              {selectedConsultation.lead && (
                <div className="bg-green-50 rounded-lg p-4">
                  <h3 className="font-semibold mb-2 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-green-600" />
                    CRM Lead Created
                  </h3>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div><span className="text-gray-500">Lead ID:</span> {selectedConsultation.lead.id}</div>
                    <div><span className="text-gray-500">Score:</span> {selectedConsultation.lead.score}</div>
                    <div><span className="text-gray-500">Status:</span> {selectedConsultation.lead.status}</div>
                    <div><span className="text-gray-500">Assigned:</span> {selectedConsultation.lead.assigned_to || 'Unassigned'}</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Assign Modal */}
      {showAssignModal && selectedConsultation && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6 border-b">
              <h2 className="text-lg font-bold">Assign to Sales Team</h2>
              <p className="text-sm text-gray-500">{selectedConsultation.customer_name}</p>
            </div>
            
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Assign To</label>
                <input
                  type="text"
                  value={assignData.assigned_to}
                  onChange={(e) => setAssignData({ ...assignData, assigned_to: e.target.value })}
                  placeholder="Sales person name"
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Follow-up Date</label>
                <input
                  type="date"
                  value={assignData.follow_up_date}
                  onChange={(e) => setAssignData({ ...assignData, follow_up_date: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <textarea
                  value={assignData.notes}
                  onChange={(e) => setAssignData({ ...assignData, notes: e.target.value })}
                  placeholder="Add notes for follow-up..."
                  rows="3"
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <div className="p-6 border-t flex justify-end gap-3">
              <button
                onClick={() => setShowAssignModal(false)}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleAssign}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Assign
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConsultationManagement;
