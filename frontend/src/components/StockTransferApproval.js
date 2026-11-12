import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  ArrowRightLeft, Check, X, Eye, RefreshCw, Package, 
  Store, Truck, AlertCircle, Clock, CheckCircle
} from 'lucide-react';


const StockTransferApproval = () => {
  const [transfers, setTransfers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTransfer, setSelectedTransfer] = useState(null);
  const [filter, setFilter] = useState('all');
  const [actionLoading, setActionLoading] = useState(null);
  const [stores, setStores] = useState([]);

  useEffect(() => {
    fetchTransfers();
    fetchStores();
  }, [filter]);

  const fetchTransfers = async () => {
    setLoading(true);
    try {
      const statusParam = filter !== 'all' ? `?status=${filter}` : '';
      const response = await fetch(`${BACKEND_URL}/api/inventory/transfers${statusParam}`);
      const data = await response.json();
      if (data.status === 'success') {
        setTransfers(data.transfers || []);
      }
    } catch (error) {
      console.error('Error fetching transfers:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStores = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/`);
      const data = await response.json();
      if (data.status === 'success') {
        setStores(data.stores || []);
      }
    } catch (error) {
      console.error('Error fetching stores:', error);
    }
  };

  const handleApproval = async (transferId, status) => {
    setActionLoading(transferId);
    try {
      const response = await fetch(`${BACKEND_URL}/api/inventory/transfer/${transferId}/approve`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status, notes: '' })
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        fetchTransfers();
        setSelectedTransfer(null);
      }
    } catch (error) {
      console.error('Error processing approval:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-700';
      case 'pending': return 'bg-yellow-100 text-yellow-700';
      case 'rejected': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'pending': return <Clock className="w-4 h-4" />;
      case 'rejected': return <X className="w-4 h-4" />;
      default: return null;
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Stock Transfer Management</h1>
          <p className="text-gray-500">Approve or reject stock transfer requests between stores</p>
        </div>
        <button
          onClick={fetchTransfers}
          className="flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4">
        <div 
          className={`p-4 rounded-xl cursor-pointer transition-all ${
            filter === 'all' ? 'bg-teal-100 border-2 border-teal-500' : 'bg-white shadow-sm hover:shadow-md'
          }`}
          onClick={() => setFilter('all')}
        >
          <ArrowRightLeft className="w-8 h-8 text-teal-600 mb-2" />
          <p className="text-2xl font-bold text-gray-800">{transfers.length}</p>
          <p className="text-sm text-gray-500">All Transfers</p>
        </div>
        
        <div 
          className={`p-4 rounded-xl cursor-pointer transition-all ${
            filter === 'pending' ? 'bg-yellow-100 border-2 border-yellow-500' : 'bg-white shadow-sm hover:shadow-md'
          }`}
          onClick={() => setFilter('pending')}
        >
          <Clock className="w-8 h-8 text-yellow-600 mb-2" />
          <p className="text-2xl font-bold text-gray-800">
            {transfers.filter(t => t.status === 'pending').length}
          </p>
          <p className="text-sm text-gray-500">Pending Approval</p>
        </div>
        
        <div 
          className={`p-4 rounded-xl cursor-pointer transition-all ${
            filter === 'completed' ? 'bg-green-100 border-2 border-green-500' : 'bg-white shadow-sm hover:shadow-md'
          }`}
          onClick={() => setFilter('completed')}
        >
          <CheckCircle className="w-8 h-8 text-green-600 mb-2" />
          <p className="text-2xl font-bold text-gray-800">
            {transfers.filter(t => t.status === 'completed').length}
          </p>
          <p className="text-sm text-gray-500">Completed</p>
        </div>
        
        <div 
          className={`p-4 rounded-xl cursor-pointer transition-all ${
            filter === 'rejected' ? 'bg-red-100 border-2 border-red-500' : 'bg-white shadow-sm hover:shadow-md'
          }`}
          onClick={() => setFilter('rejected')}
        >
          <X className="w-8 h-8 text-red-600 mb-2" />
          <p className="text-2xl font-bold text-gray-800">
            {transfers.filter(t => t.status === 'rejected').length}
          </p>
          <p className="text-sm text-gray-500">Rejected</p>
        </div>
      </div>

      {/* Transfers Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold text-gray-800">Transfer Requests</h2>
        </div>
        
        {loading ? (
          <div className="p-8 text-center">
            <RefreshCw className="w-8 h-8 text-gray-400 animate-spin mx-auto mb-2" />
            <p className="text-gray-500">Loading transfers...</p>
          </div>
        ) : transfers.length === 0 ? (
          <div className="p-8 text-center">
            <Package className="w-12 h-12 text-gray-300 mx-auto mb-2" />
            <p className="text-gray-500">No stock transfers found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Transfer #</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">From</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">To</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Items</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {transfers.map((transfer) => (
                  <tr key={transfer.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-teal-600">
                      {transfer.transfer_number}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className="flex items-center gap-2">
                        <Store className="w-4 h-4 text-gray-400" />
                        {transfer.from_store_name}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className="flex items-center gap-2">
                        <Truck className="w-4 h-4 text-gray-400" />
                        {transfer.to_store_name}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {transfer.items?.length || 0} items
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {formatDate(transfer.created_at)}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(transfer.status)}`}>
                        {getStatusIcon(transfer.status)}
                        {transfer.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setSelectedTransfer(transfer)}
                          className="p-1 text-gray-500 hover:bg-gray-100 rounded"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        
                        {transfer.status === 'pending' && (
                          <>
                            <button
                              onClick={() => handleApproval(transfer.id, 'approved')}
                              disabled={actionLoading === transfer.id}
                              className="p-1 text-green-600 hover:bg-green-50 rounded disabled:opacity-50"
                              title="Approve"
                            >
                              {actionLoading === transfer.id ? (
                                <RefreshCw className="w-4 h-4 animate-spin" />
                              ) : (
                                <Check className="w-4 h-4" />
                              )}
                            </button>
                            <button
                              onClick={() => handleApproval(transfer.id, 'rejected')}
                              disabled={actionLoading === transfer.id}
                              className="p-1 text-red-600 hover:bg-red-50 rounded disabled:opacity-50"
                              title="Reject"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </>
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

      {/* Transfer Detail Modal */}
      {selectedTransfer && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
            <div className="p-4 border-b flex items-center justify-between bg-gray-50">
              <div>
                <h3 className="text-lg font-semibold text-gray-800">Transfer Details</h3>
                <p className="text-sm text-gray-500">{selectedTransfer.transfer_number}</p>
              </div>
              <button
                onClick={() => setSelectedTransfer(null)}
                className="p-2 hover:bg-gray-200 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-6 space-y-6 overflow-y-auto max-h-[60vh]">
              {/* Transfer Info */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500 mb-1">From Store</p>
                  <p className="font-semibold text-gray-800">{selectedTransfer.from_store_name}</p>
                  <p className="text-xs text-gray-500">{selectedTransfer.from_store_code}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500 mb-1">To Store</p>
                  <p className="font-semibold text-gray-800">{selectedTransfer.to_store_name}</p>
                  <p className="text-xs text-gray-500">{selectedTransfer.to_store_code}</p>
                </div>
              </div>

              {/* Items */}
              <div>
                <h4 className="font-medium text-gray-800 mb-3">Items to Transfer</h4>
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Product</th>
                      <th className="px-3 py-2 text-right text-xs font-medium text-gray-500">Qty</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {selectedTransfer.items?.map((item, idx) => (
                      <tr key={idx}>
                        <td className="px-3 py-2 text-sm">{item.product_name}</td>
                        <td className="px-3 py-2 text-sm text-right font-medium">{item.quantity}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Notes */}
              {selectedTransfer.notes && (
                <div className="p-4 bg-yellow-50 rounded-lg">
                  <p className="text-sm text-gray-500 mb-1">Notes</p>
                  <p className="text-gray-800">{selectedTransfer.notes}</p>
                </div>
              )}

              {/* Timestamps */}
              <div className="text-sm text-gray-500 space-y-1">
                <p>Created: {formatDate(selectedTransfer.created_at)}</p>
                {selectedTransfer.approved_at && (
                  <p>Processed: {formatDate(selectedTransfer.approved_at)}</p>
                )}
              </div>
            </div>

            {/* Actions */}
            {selectedTransfer.status === 'pending' && (
              <div className="p-4 border-t bg-gray-50 flex justify-end gap-3">
                <button
                  onClick={() => handleApproval(selectedTransfer.id, 'rejected')}
                  disabled={actionLoading === selectedTransfer.id}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 flex items-center gap-2"
                >
                  <X className="w-4 h-4" />
                  Reject
                </button>
                <button
                  onClick={() => handleApproval(selectedTransfer.id, 'approved')}
                  disabled={actionLoading === selectedTransfer.id}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {actionLoading === selectedTransfer.id ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Check className="w-4 h-4" />
                  )}
                  Approve Transfer
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default StockTransferApproval;
