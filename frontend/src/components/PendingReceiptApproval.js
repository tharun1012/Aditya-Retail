import React, { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { 
  Receipt, CheckCircle, XCircle, Clock, Search, Filter, RefreshCw,
  IndianRupee, User, Calendar, FileText, Eye, ArrowLeft, AlertCircle,
  ChevronLeft, ChevronRight, Download, Printer, Check, X
} from 'lucide-react';

const PendingReceiptApproval = () => {
  const navigate = useNavigate();
  const [receipts, setReceipts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedReceipt, setSelectedReceipt] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(null);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [remarks, setRemarks] = useState('');
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0
  });

  const adminUser = JSON.parse(localStorage.getItem('adminUser') || '{}');

  const fetchPendingReceipts = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/vouchers/payment-receipt/pending-approval?page=${pagination.page}&limit=${pagination.limit}`
      );
      const data = await response.json();
      
      if (data.status === 'success') {
        setReceipts(data.vouchers || []);
        setPagination(prev => ({
          ...prev,
          total: data.total || 0,
          totalPages: data.total_pages || 1
        }));
      }
    } catch (error) {
      console.error('Error fetching receipts:', error);
      setMessage({ type: 'error', text: 'Failed to fetch pending receipts' });
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.limit]);

  useEffect(() => {
    fetchPendingReceipts();
  }, [fetchPendingReceipts]);

  const handleApprove = async (receipt) => {
    setActionLoading(receipt.id);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/vouchers/payment-receipt/${receipt.id}/approve`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            approved_by: adminUser.email || 'admin',
            remarks: remarks || 'Approved'
          })
        }
      );
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setMessage({ type: 'success', text: `Receipt ${receipt.voucher_number} approved successfully` });
        setShowDetailsModal(false);
        setRemarks('');
        fetchPendingReceipts();
      } else {
        setMessage({ type: 'error', text: data.detail || 'Failed to approve' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error approving receipt' });
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (receipt) => {
    if (!remarks.trim()) {
      setMessage({ type: 'error', text: 'Please provide a reason for rejection' });
      return;
    }
    
    setActionLoading(receipt.id);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/vouchers/payment-receipt/${receipt.id}/reject`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            approved_by: adminUser.email || 'admin',
            remarks: remarks
          })
        }
      );
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setMessage({ type: 'success', text: `Receipt ${receipt.voucher_number} rejected` });
        setShowDetailsModal(false);
        setRemarks('');
        fetchPendingReceipts();
      } else {
        setMessage({ type: 'error', text: data.detail || 'Failed to reject' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error rejecting receipt' });
    } finally {
      setActionLoading(null);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    try {
      return new Date(dateStr).toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateStr;
    }
  };

  const formatCurrency = (amount) => {
    if (!amount && amount !== 0) return '₹0';
    return `₹${Number(amount).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
  };

  const filteredReceipts = receipts.filter(r => 
    r.voucher_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    r.party_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    r.reference_number?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6" data-testid="pending-receipt-approval">
      {/* Back Button */}
      <button
        onClick={() => navigate('/admin')}
        className="flex items-center px-4 py-2 mb-6 text-gray-700 bg-white hover:bg-gray-100 rounded-lg transition-all border border-gray-300 shadow-sm"
        data-testid="back-to-dashboard-btn"
      >
        <ArrowLeft className="h-5 w-5 mr-2" />
        <span className="font-medium">Back to Dashboard</span>
      </button>

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Receipt className="w-7 h-7 text-amber-600" />
          Pending Receipt Approvals
        </h1>
        <p className="text-gray-600 mt-1">Review and approve payment receipts before sending to customers</p>
      </div>

      {/* Message */}
      {message.text && (
        <div className={`mb-4 p-4 rounded-lg flex items-center gap-2 ${
          message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {message.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
          {message.text}
          <button onClick={() => setMessage({ type: '', text: '' })} className="ml-auto">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-xl shadow-sm p-4 border-l-4 border-amber-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Pending Approvals</p>
              <p className="text-2xl font-bold text-amber-600">{pagination.total}</p>
            </div>
            <Clock className="w-10 h-10 text-amber-100" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Amount Pending</p>
              <p className="text-2xl font-bold text-green-600">
                {formatCurrency(receipts.reduce((sum, r) => sum + (r.amount || 0), 0))}
              </p>
            </div>
            <IndianRupee className="w-10 h-10 text-green-100" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Advance Payments</p>
              <p className="text-2xl font-bold text-blue-600">
                {receipts.filter(r => r.is_advance).length}
              </p>
            </div>
            <FileText className="w-10 h-10 text-blue-100" />
          </div>
        </div>
      </div>

      {/* Search & Refresh */}
      <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
        <div className="flex gap-4 items-center">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search by receipt no, customer, reference..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500"
              data-testid="search-receipts"
            />
          </div>
          <button
            onClick={fetchPendingReceipts}
            className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 flex items-center gap-2"
            data-testid="refresh-receipts"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Receipts Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin text-amber-600" />
          </div>
        ) : filteredReceipts.length === 0 ? (
          <div className="text-center py-12">
            <CheckCircle className="w-16 h-16 text-green-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900">All caught up!</h3>
            <p className="text-gray-500">No receipts pending approval</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full" data-testid="receipts-table">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Receipt #</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payment Mode</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reference</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Linked To</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredReceipts.map((receipt, idx) => (
                    <tr key={receipt.id || idx} className="hover:bg-amber-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="font-medium text-amber-600">{receipt.voucher_number}</span>
                        {receipt.is_advance && (
                          <span className="ml-2 px-2 py-0.5 text-xs bg-orange-100 text-orange-700 rounded">
                            Advance
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <User className="w-4 h-4 text-gray-400 mr-2" />
                          <span className="text-gray-900">{receipt.party_name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-lg font-semibold text-green-600">{formatCurrency(receipt.amount)}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full capitalize">
                          {receipt.payment_mode}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="font-mono text-sm text-gray-600">{receipt.reference_number || '-'}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {receipt.linked_document ? (
                          <span className="text-sm text-purple-600 font-medium">
                            {receipt.linked_document.type}: {receipt.linked_document.number}
                          </span>
                        ) : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(receipt.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => {
                              setSelectedReceipt(receipt);
                              setShowDetailsModal(true);
                              setRemarks('');
                            }}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                            title="View & Approve"
                            data-testid={`view-receipt-${idx}`}
                          >
                            <Eye className="w-5 h-5" />
                          </button>
                          <button
                            onClick={() => handleApprove(receipt)}
                            disabled={actionLoading === receipt.id}
                            className="p-2 text-green-600 hover:bg-green-50 rounded-lg disabled:opacity-50"
                            title="Quick Approve"
                          >
                            <CheckCircle className="w-5 h-5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-6 py-4 border-t flex items-center justify-between">
              <div className="text-sm text-gray-500">
                Showing {filteredReceipts.length} of {pagination.total} receipts
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                  disabled={pagination.page === 1}
                  className="p-2 rounded-lg border hover:bg-gray-50 disabled:opacity-50"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <span className="px-4 py-2 bg-amber-50 text-amber-600 rounded-lg font-medium">
                  {pagination.page}
                </span>
                <button
                  onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                  disabled={pagination.page >= pagination.totalPages}
                  className="p-2 rounded-lg border hover:bg-gray-50 disabled:opacity-50"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Receipt Details Modal */}
      {showDetailsModal && selectedReceipt && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg">
            <div className="p-6 border-b bg-gradient-to-r from-amber-600 to-amber-700 text-white rounded-t-xl">
              <h2 className="text-xl font-bold flex items-center gap-2">
                <Receipt className="w-6 h-6" />
                Receipt - {selectedReceipt.voucher_number}
              </h2>
            </div>
            
            <div className="p-6 space-y-4">
              {/* Receipt Info */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Customer</p>
                  <p className="font-medium text-gray-900">{selectedReceipt.party_name}</p>
                </div>
                <div className="bg-green-50 rounded-lg p-3">
                  <p className="text-xs text-green-600">Amount</p>
                  <p className="text-xl font-bold text-green-700">{formatCurrency(selectedReceipt.amount)}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Payment Mode</p>
                  <p className="font-medium text-gray-900 capitalize">{selectedReceipt.payment_mode}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Reference #</p>
                  <p className="font-mono text-gray-900">{selectedReceipt.reference_number || '-'}</p>
                </div>
              </div>

              {/* Linked Document */}
              {selectedReceipt.linked_document && (
                <div className="bg-purple-50 rounded-lg p-3">
                  <p className="text-xs text-purple-600">Linked Document</p>
                  <p className="font-medium text-purple-900">
                    {selectedReceipt.linked_document.type === 'sales_order' ? 'Sales Order' : 'Invoice'}: {selectedReceipt.linked_document.number}
                  </p>
                </div>
              )}

              {selectedReceipt.is_advance && (
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                  <p className="text-sm text-orange-700 font-medium">
                    ⚠️ This is an Advance Payment
                  </p>
                </div>
              )}

              {/* Description */}
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500">Description</p>
                <p className="text-gray-900">{selectedReceipt.description}</p>
              </div>

              {/* Remarks Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Remarks {selectedReceipt.is_advance ? '(Optional for Approve, Required for Reject)' : '(Optional)'}
                </label>
                <textarea
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500"
                  rows={2}
                  placeholder="Add approval/rejection remarks..."
                />
              </div>
            </div>

            <div className="p-6 border-t bg-gray-50 flex justify-between rounded-b-xl">
              <button
                onClick={() => {
                  setShowDetailsModal(false);
                  setRemarks('');
                }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
              <div className="flex gap-3">
                <button
                  onClick={() => handleReject(selectedReceipt)}
                  disabled={actionLoading === selectedReceipt.id}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2 disabled:opacity-50"
                >
                  <XCircle className="w-4 h-4" />
                  Reject
                </button>
                <button
                  onClick={() => handleApprove(selectedReceipt)}
                  disabled={actionLoading === selectedReceipt.id}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2 disabled:opacity-50"
                >
                  <CheckCircle className="w-4 h-4" />
                  Approve
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PendingReceiptApproval;
