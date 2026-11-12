import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { CreditCard, Plus, Search, Eye, FileText } from 'lucide-react';
import DocumentActions from './DocumentActions';
import BulkActionToolbar from './BulkActionToolbar';
import FilterPanel from './FilterPanel';
import { exportVouchersToExcel } from '../utils/excelExport';


const VouchersManagement = () => {
  const [activeTab, setActiveTab] = useState('payment-receipt');
  const [vouchers, setVouchers] = useState([]);
  const [filteredVouchers, setFilteredVouchers] = useState([]);
  const [notes, setNotes] = useState([]);
  const [filteredNotes, setFilteredNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [modalType, setModalType] = useState('payment');
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [selectedItem, setSelectedItem] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedItems, setSelectedItems] = useState([]);
  const [filters, setFilters] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalVouchers, setTotalVouchers] = useState(0);
  const vouchersPerPage = 50;

  // Payment/Receipt Voucher Form
  const [voucherForm, setVoucherForm] = useState({
    voucher_type: 'payment',
    party_name: '',
    amount: 0,
    payment_mode: 'cash',
    reference_number: '',
    description: '',
    voucher_date: new Date().toISOString().split('T')[0],
    created_by: 'admin'
  });

  // Credit/Debit Note Form
  const [noteForm, setNoteForm] = useState({
    note_type: 'credit_note',
    party_name: '',
    original_invoice_number: '',
    amount: 0,
    reason: '',
    note_date: new Date().toISOString().split('T')[0],
    created_by: 'admin'
  });

  useEffect(() => {
    if (activeTab === 'payment-receipt') {
      fetchVouchers();
    } else {
      fetchNotes();
    }
  }, [activeTab, typeFilter, currentPage]);

  useEffect(() => {
    setCurrentPage(1);
  }, [typeFilter, activeTab]);

  const fetchVouchers = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page: currentPage, limit: vouchersPerPage });
      if (typeFilter !== 'all') {
        params.set('voucher_type', typeFilter);
      }
      const url = `${BACKEND_URL}/api/vouchers/payment-receipt?${params.toString()}`;
      
      const response = await fetch(url);
      const data = await response.json();
      if (data.status === 'success') {
        setVouchers(data.vouchers);
        setTotalVouchers(data.total || 0);
      }
    } catch (error) {
      console.error('Failed to fetch vouchers:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchNotes = async () => {
    setLoading(true);
    try {
      const url = typeFilter === 'all' 
        ? `${BACKEND_URL}/api/vouchers/credit-debit-note`
        : `${BACKEND_URL}/api/vouchers/credit-debit-note?note_type=${typeFilter}`;
      
      const response = await fetch(url);
      const data = await response.json();
      if (data.status === 'success') {
        setNotes(data.notes);
      }
    } catch (error) {
      console.error('Failed to fetch notes:', error);
    } finally {
      setLoading(false);
    }
  };

  // Apply filters for vouchers
  useEffect(() => {
    const dataToFilter = activeTab === 'payment-receipt' ? vouchers : notes;
    let filtered = [...dataToFilter];

    if (filters?.dateFrom) {
      const dateField = activeTab === 'payment-receipt' ? 'voucher_date' : 'note_date';
      filtered = filtered.filter(item => new Date(item[dateField]) >= filters.dateFrom);
    }
    if (filters?.dateTo) {
      const dateField = activeTab === 'payment-receipt' ? 'voucher_date' : 'note_date';
      filtered = filtered.filter(item => new Date(item[dateField]) <= filters.dateTo);
    }
    if (filters?.amountMin) {
      filtered = filtered.filter(item => item.amount >= parseFloat(filters.amountMin));
    }
    if (filters?.amountMax) {
      filtered = filtered.filter(item => item.amount <= parseFloat(filters.amountMax));
    }
    if (filters?.paymentMode && filters.paymentMode !== 'All') {
      filtered = filtered.filter(item => item.payment_mode?.toLowerCase() === filters.paymentMode.toLowerCase());
    }
    if (filters?.searchTerm) {
      filtered = filtered.filter(item =>
        item.party_name?.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
        (item.voucher_number && item.voucher_number.toLowerCase().includes(filters.searchTerm.toLowerCase()))
      );
    }

    if (activeTab === 'payment-receipt') {
      setFilteredVouchers(filtered);
    } else {
      setFilteredNotes(filtered);
    }
  }, [vouchers, notes, filters, activeTab]);

  const handleApplyFilters = (newFilters) => {
    setFilters(newFilters);
  };

  const handleClearFilters = () => {
    setFilters(null);
    setFilteredVouchers(vouchers);
    setFilteredNotes(notes);
  };

  // Bulk actions
  const handleSelectAll = (e) => {
    const dataToSelect = activeTab === 'payment-receipt' ? filteredVouchers : filteredNotes;
    if (e.target.checked) {
      setSelectedItems(dataToSelect.map(item => item.id));
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
    const dataToExport = activeTab === 'payment-receipt' ? vouchers : notes;
    const selectedData = dataToExport.filter(item => selectedItems.includes(item.id));
    const result = exportVouchersToExcel(selectedData);
    if (result.success) {
      alert(`Exported ${selectedData.length} items to ${result.filename}`);
    } else {
      alert('Export failed: ' + result.error);
    }
  };

  const handleDeleteSelected = async () => {
    const endpoint = activeTab === 'payment-receipt' ? 'payment-receipt' : 'credit-debit-note';
    if (window.confirm(`Are you sure you want to delete ${selectedItems.length} items?`)) {
      try {
        for (const id of selectedItems) {
          await fetch(`${BACKEND_URL}/api/vouchers/${endpoint}/${id}`, { method: 'DELETE' });
        }
        alert('Items deleted successfully');
        setSelectedItems([]);
        if (activeTab === 'payment-receipt') {
          fetchVouchers();
        } else {
          fetchNotes();
        }
      } catch (error) {
        console.error('Delete failed:', error);
        alert('Failed to delete items');
      }
    }
  };

  const handleCreateVoucher = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/vouchers/payment-receipt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(voucherForm)
      });

      const data = await response.json();
      if (data.status === 'success') {
        alert(`Voucher Created: ${data.voucher_number}`);
        setShowCreateModal(false);
        fetchVouchers();
        resetVoucherForm();
      }
    } catch (error) {
      console.error('Failed to create voucher:', error);
      alert('Failed to create voucher');
    }
  };

  const handleCreateNote = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/vouchers/credit-debit-note`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(noteForm)
      });

      const data = await response.json();
      if (data.status === 'success') {
        alert(`Note Created: ${data.note_number}`);
        setShowCreateModal(false);
        fetchNotes();
        resetNoteForm();
      }
    } catch (error) {
      console.error('Failed to create note:', error);
      alert('Failed to create note');
    }
  };

  const resetVoucherForm = () => {
    setVoucherForm({
      voucher_type: 'payment',
      party_name: '',
      amount: 0,
      payment_mode: 'cash',
      reference_number: '',
      description: '',
      voucher_date: new Date().toISOString().split('T')[0],
      created_by: 'admin'
    });
  };

  const resetNoteForm = () => {
    setNoteForm({
      note_type: 'credit_note',
      party_name: '',
      original_invoice_number: '',
      amount: 0,
      reason: '',
      note_date: new Date().toISOString().split('T')[0],
      created_by: 'admin'
    });
  };

  const renderVouchersTab = () => (
    <div>
      {/* Advanced Filters */}
      <FilterPanel
        onApplyFilters={handleApplyFilters}
        onClearFilters={handleClearFilters}
        showDateRange={true}
        showAmountRange={true}
        showStatus={false}
        showPaymentMode={true}
        showSearch={true}
        paymentModes={['All', 'Cash', 'Card', 'UPI', 'NEFT', 'Cheque', 'Bank Transfer']}
        searchPlaceholder="Search by voucher number or party name..."
      />

      {/* Bulk Actions */}
      <BulkActionToolbar
        selectedCount={selectedItems.length}
        onExportExcel={handleExportExcel}
        onDelete={handleDeleteSelected}
        onPrint={() => alert('Print functionality')}
        onClear={() => setSelectedItems([])}
        showPrint={true}
      />

      {/* Vouchers Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-3 py-3 text-left">
                <input
                  type="checkbox"
                  checked={selectedItems.length === filteredVouchers.length && filteredVouchers.length > 0}
                  onChange={handleSelectAll}
                  className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                />
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Voucher #</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Party Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payment Mode</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredVouchers.length === 0 ? (
              <tr>
                <td colSpan="8" className="px-6 py-12 text-center text-gray-500">
                  No vouchers found
                </td>
              </tr>
            ) : (
              filteredVouchers.map((voucher) => (
                <tr key={voucher.id} className={selectedItems.includes(voucher.id) ? 'bg-indigo-50' : ''}>
                  <td className="px-3 py-4">
                    <input
                      type="checkbox"
                      checked={selectedItems.includes(voucher.id)}
                      onChange={() => handleSelectItem(voucher.id)}
                      className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {voucher.voucher_number}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      voucher.voucher_type === 'payment' 
                        ? 'bg-red-100 text-red-800' 
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {voucher.voucher_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{voucher.party_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold">₹{voucher.amount?.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{voucher.payment_mode}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {new Date(voucher.voucher_date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => {
                        setSelectedItem(voucher);
                        setShowDetailsModal(true);
                      }}
                      className="text-indigo-600 hover:text-indigo-900"
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

      {/* Pagination */}
      {totalVouchers > vouchersPerPage && (
        <div className="flex items-center justify-between mt-4 px-2">
          <p className="text-sm text-gray-600">
            Showing {((currentPage - 1) * vouchersPerPage) + 1}-{Math.min(currentPage * vouchersPerPage, totalVouchers)} of {totalVouchers}
          </p>
          <div className="flex gap-2 items-center">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 rounded border border-gray-300 text-sm disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Previous
            </button>
            <span className="text-sm text-gray-700">
              Page {currentPage} of {Math.ceil(totalVouchers / vouchersPerPage)}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(Math.ceil(totalVouchers / vouchersPerPage), p + 1))}
              disabled={currentPage >= Math.ceil(totalVouchers / vouchersPerPage)}
              className="px-3 py-1 rounded border border-gray-300 text-sm disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );

  const renderNotesTab = () => (
    <div>
      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search notes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
          />
        </div>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
        >
          <option value="all">All Types</option>
          <option value="credit_note">Credit Note</option>
          <option value="debit_note">Debit Note</option>
        </select>
      </div>

      {/* Notes Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Note #</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Party Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Invoice #</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredNotes.length === 0 ? (
              <tr>
                <td colSpan="7" className="px-6 py-12 text-center text-gray-500">
                  No notes found
                </td>
              </tr>
            ) : (
              filteredNotes.map((note) => (
                <tr key={note.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {note.note_number}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      note.note_type === 'credit_note' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {note.note_type.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{note.party_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold">₹{note.amount?.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{note.original_invoice_number || 'N/A'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {new Date(note.note_date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => {
                        setSelectedItem(note);
                        setShowDetailsModal(true);
                      }}
                      className="text-red-600 hover:text-red-900"
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
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
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
              <CreditCard className="text-indigo-500" />
              Vouchers Management
            </h1>
            <p className="text-gray-600 mt-1">Payment, receipt vouchers, and credit/debit notes</p>
          </div>
          <button
            onClick={() => {
              setModalType(activeTab === 'payment-receipt' ? 'payment' : 'credit_note');
              setShowCreateModal(true);
            }}
            className="px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 flex items-center gap-2"
          >
            <Plus size={20} />
            Create {activeTab === 'payment-receipt' ? 'Voucher' : 'Note'}
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          <button
            onClick={() => {
              setActiveTab('payment-receipt');
              setTypeFilter('all');
            }}
            className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
              activeTab === 'payment-receipt'
                ? 'bg-indigo-500 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            <CreditCard size={18} />
            Payment & Receipts
          </button>
          <button
            onClick={() => {
              setActiveTab('credit-debit-notes');
              setTypeFilter('all');
            }}
            className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
              activeTab === 'credit-debit-notes'
                ? 'bg-red-500 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            <FileText size={18} />
            Credit & Debit Notes
          </button>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'payment-receipt' ? renderVouchersTab() : renderNotesTab()}

      {/* Create Voucher Modal */}
      {showCreateModal && activeTab === 'payment-receipt' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
            <div className="p-6 border-b">
              <h2 className="text-2xl font-bold">Create {modalType === 'payment' ? 'Payment' : 'Receipt'} Voucher</h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="block text-sm font-medium mb-1">Type</label>
                  <select
                    value={voucherForm.voucher_type}
                    onChange={(e) => setVoucherForm({ ...voucherForm, voucher_type: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                  >
                    <option value="payment">Payment</option>
                    <option value="receipt">Receipt</option>
                  </select>
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium mb-1">Party Name *</label>
                  <input
                    type="text"
                    value={voucherForm.party_name}
                    onChange={(e) => setVoucherForm({ ...voucherForm, party_name: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Amount *</label>
                  <input
                    type="number"
                    value={voucherForm.amount}
                    onChange={(e) => setVoucherForm({ ...voucherForm, amount: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Payment Mode *</label>
                  <select
                    value={voucherForm.payment_mode}
                    onChange={(e) => setVoucherForm({ ...voucherForm, payment_mode: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                  >
                    <option value="cash">Cash</option>
                    <option value="upi">UPI</option>
                    <option value="bank_transfer">Bank Transfer</option>
                    <option value="cheque">Cheque</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Reference Number</label>
                  <input
                    type="text"
                    value={voucherForm.reference_number}
                    onChange={(e) => setVoucherForm({ ...voucherForm, reference_number: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Date *</label>
                  <input
                    type="date"
                    value={voucherForm.voucher_date}
                    onChange={(e) => setVoucherForm({ ...voucherForm, voucher_date: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium mb-1">Description *</label>
                  <textarea
                    value={voucherForm.description}
                    onChange={(e) => setVoucherForm({ ...voucherForm, description: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                    rows="3"
                  />
                </div>
              </div>
            </div>
            <div className="p-6 border-t flex justify-end gap-2">
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  resetVoucherForm();
                }}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateVoucher}
                className="px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600"
              >
                Create Voucher
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Note Modal */}
      {showCreateModal && activeTab === 'credit-debit-notes' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
            <div className="p-6 border-b">
              <h2 className="text-2xl font-bold">Create {modalType === 'credit_note' ? 'Credit' : 'Debit'} Note</h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="block text-sm font-medium mb-1">Type</label>
                  <select
                    value={noteForm.note_type}
                    onChange={(e) => setNoteForm({ ...noteForm, note_type: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                  >
                    <option value="credit_note">Credit Note</option>
                    <option value="debit_note">Debit Note</option>
                  </select>
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium mb-1">Party Name *</label>
                  <input
                    type="text"
                    value={noteForm.party_name}
                    onChange={(e) => setNoteForm({ ...noteForm, party_name: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Amount *</label>
                  <input
                    type="number"
                    value={noteForm.amount}
                    onChange={(e) => setNoteForm({ ...noteForm, amount: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Original Invoice #</label>
                  <input
                    type="text"
                    value={noteForm.original_invoice_number}
                    onChange={(e) => setNoteForm({ ...noteForm, original_invoice_number: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium mb-1">Date *</label>
                  <input
                    type="date"
                    value={noteForm.note_date}
                    onChange={(e) => setNoteForm({ ...noteForm, note_date: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium mb-1">Reason *</label>
                  <textarea
                    value={noteForm.reason}
                    onChange={(e) => setNoteForm({ ...noteForm, reason: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                    rows="3"
                  />
                </div>
              </div>
            </div>
            <div className="p-6 border-t flex justify-end gap-2">
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  resetNoteForm();
                }}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateNote}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
              >
                Create Note
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Details Modal */}
      {showDetailsModal && selectedItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
            <div className="p-6 border-b">
              <h2 className="text-2xl font-bold">Details</h2>
              <p className="text-gray-600">{selectedItem.voucher_number || selectedItem.note_number}</p>
            </div>
            <div className="p-6">
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">Party Name</p>
                  <p className="font-medium">{selectedItem.party_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Amount</p>
                  <p className="font-medium text-lg">₹{selectedItem.amount?.toFixed(2)}</p>
                </div>
                {selectedItem.description && (
                  <div>
                    <p className="text-sm text-gray-600">Description</p>
                    <p className="font-medium">{selectedItem.description}</p>
                  </div>
                )}
                {selectedItem.reason && (
                  <div>
                    <p className="text-sm text-gray-600">Reason</p>
                    <p className="font-medium">{selectedItem.reason}</p>
                  </div>
                )}
              </div>

              {/* Document Actions */}
              <div className="border-t border-gray-200 pt-4 mt-4">
                <h3 className="font-semibold mb-3">Document Actions</h3>
                <DocumentActions 
                  document={selectedItem} 
                  documentType={selectedItem.voucher_number ? 'voucher' : 'note'}
                />
              </div>
            </div>
            <div className="p-6 border-t flex justify-end">
              <button
                onClick={() => setShowDetailsModal(false)}
                className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
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

export default VouchersManagement;