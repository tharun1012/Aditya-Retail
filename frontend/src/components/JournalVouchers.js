import React, { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  BookOpen, Plus, Search, Eye, Edit, Trash2, X, Save,
  IndianRupee, ArrowRight, Calendar, FileText, CheckCircle,
  AlertTriangle, RefreshCw, Filter, Download
} from 'lucide-react';
import { showToast } from '../utils/toast';


const JournalVouchers = () => {
  const [vouchers, setVouchers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedVoucher, setSelectedVoucher] = useState(null);
  const [ledgerAccounts, setLedgerAccounts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFilter, setDateFilter] = useState({ from: '', to: '' });
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Form state for creating voucher
  const [formData, setFormData] = useState({
    voucher_date: new Date().toISOString().split('T')[0],
    narration: '',
    entries: [
      { ledger_id: '', ledger_name: '', debit: 0, credit: 0 },
      { ledger_id: '', ledger_name: '', debit: 0, credit: 0 }
    ]
  });

  const fetchVouchers = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: currentPage,
        limit: 20
      });
      if (searchTerm) params.append('search', searchTerm);
      if (dateFilter.from) params.append('from_date', dateFilter.from);
      if (dateFilter.to) params.append('to_date', dateFilter.to);
      
      const response = await fetch(`${BACKEND_URL}/api/journal-vouchers?${params}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setVouchers(data.vouchers);
        setTotalPages(data.pages || 1);
      }
    } catch (error) {
      console.error('Failed to fetch vouchers:', error);
      showToast.error('Failed to load journal vouchers');
    } finally {
      setLoading(false);
    }
  }, [currentPage, searchTerm, dateFilter]);

  const fetchLedgerAccounts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/ledger/accounts?limit=500`);
      const data = await response.json();
      if (data.status === 'success') {
        setLedgerAccounts(data.accounts || []);
      }
    } catch (error) {
      console.error('Failed to fetch ledger accounts:', error);
    }
  };

  useEffect(() => {
    fetchVouchers();
    fetchLedgerAccounts();
  }, [fetchVouchers]);

  const calculateTotals = () => {
    const totalDebit = formData.entries.reduce((sum, e) => sum + (parseFloat(e.debit) || 0), 0);
    const totalCredit = formData.entries.reduce((sum, e) => sum + (parseFloat(e.credit) || 0), 0);
    return { totalDebit, totalCredit, isBalanced: Math.abs(totalDebit - totalCredit) < 0.01 };
  };

  const handleAddEntry = () => {
    setFormData({
      ...formData,
      entries: [...formData.entries, { ledger_id: '', ledger_name: '', debit: 0, credit: 0 }]
    });
  };

  const handleRemoveEntry = (index) => {
    if (formData.entries.length <= 2) {
      showToast.error('Minimum 2 entries required');
      return;
    }
    const newEntries = formData.entries.filter((_, i) => i !== index);
    setFormData({ ...formData, entries: newEntries });
  };

  const handleEntryChange = (index, field, value) => {
    const newEntries = [...formData.entries];
    newEntries[index][field] = value;
    
    // If ledger_id changes, update ledger_name
    if (field === 'ledger_id') {
      const selectedLedger = ledgerAccounts.find(l => l.id === value);
      newEntries[index].ledger_name = selectedLedger?.name || '';
    }
    
    // If debit is entered, clear credit and vice versa
    if (field === 'debit' && parseFloat(value) > 0) {
      newEntries[index].credit = 0;
    } else if (field === 'credit' && parseFloat(value) > 0) {
      newEntries[index].debit = 0;
    }
    
    setFormData({ ...formData, entries: newEntries });
  };

  const handleCreateVoucher = async () => {
    const { totalDebit, totalCredit, isBalanced } = calculateTotals();
    
    if (!isBalanced) {
      showToast.error(`Debit (₹${totalDebit.toLocaleString()}) and Credit (₹${totalCredit.toLocaleString()}) must be equal`);
      return;
    }
    
    if (totalDebit === 0) {
      showToast.error('Total amount cannot be zero');
      return;
    }
    
    // Validate entries have ledger selected
    const invalidEntries = formData.entries.filter(e => !e.ledger_id || (e.debit === 0 && e.credit === 0));
    if (invalidEntries.length > 0) {
      showToast.error('All entries must have a ledger selected and an amount');
      return;
    }
    
    if (!formData.narration.trim()) {
      showToast.error('Please enter a narration/description');
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/journal-vouchers/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success(data.message || 'Journal voucher created successfully');
        setShowCreateModal(false);
        resetForm();
        fetchVouchers();
      } else {
        showToast.error(data.detail || 'Failed to create voucher');
      }
    } catch (error) {
      console.error('Create voucher error:', error);
      showToast.error('Failed to create journal voucher');
    }
  };

  const handleDeleteVoucher = async (voucherId) => {
    if (!window.confirm('Are you sure you want to delete this voucher? This will reverse all ledger entries.')) {
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/journal-vouchers/${voucherId}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success('Voucher deleted and entries reversed');
        fetchVouchers();
      } else {
        showToast.error(data.detail || 'Failed to delete voucher');
      }
    } catch (error) {
      showToast.error('Failed to delete voucher');
    }
  };

  const resetForm = () => {
    setFormData({
      voucher_date: new Date().toISOString().split('T')[0],
      narration: '',
      entries: [
        { ledger_id: '', ledger_name: '', debit: 0, credit: 0 },
        { ledger_id: '', ledger_name: '', debit: 0, credit: 0 }
      ]
    });
  };

  const { totalDebit, totalCredit, isBalanced } = calculateTotals();

  return (
    <div className="p-6 bg-gray-50 min-h-screen" data-testid="journal-vouchers-page">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <BookOpen className="text-indigo-500" />
              Journal Vouchers
            </h1>
            <p className="text-gray-600 mt-1">Manual adjustments and contra entries</p>
          </div>
          <button
            onClick={() => { resetForm(); setShowCreateModal(true); }}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
            data-testid="create-journal-btn"
          >
            <Plus size={18} />
            Create Journal Entry
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 flex flex-wrap gap-4 items-center">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search by narration or voucher number..."
              value={searchTerm}
              onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg"
              data-testid="journal-search"
            />
          </div>
          <div className="flex items-center gap-2">
            <Calendar size={18} className="text-gray-500" />
            <input
              type="date"
              value={dateFilter.from}
              onChange={(e) => setDateFilter({ ...dateFilter, from: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-lg"
            />
            <span className="text-gray-500">to</span>
            <input
              type="date"
              value={dateFilter.to}
              onChange={(e) => setDateFilter({ ...dateFilter, to: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <button
            onClick={() => { setSearchTerm(''); setDateFilter({ from: '', to: '' }); setCurrentPage(1); }}
            className="px-3 py-2 text-gray-600 hover:text-gray-800"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Vouchers List */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b">
          <h2 className="font-semibold text-gray-900">All Journal Vouchers</h2>
        </div>
        
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
            <p className="mt-4 text-gray-500">Loading vouchers...</p>
          </div>
        ) : vouchers.length === 0 ? (
          <div className="p-12 text-center">
            <BookOpen size={48} className="mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium text-gray-900">No journal vouchers found</p>
            <p className="text-gray-500 mt-2">Create your first journal entry to record adjustments</p>
          </div>
        ) : (
          <div className="divide-y">
            {vouchers.map((voucher) => (
              <div key={voucher.id} className="p-4 hover:bg-gray-50 transition" data-testid={`voucher-${voucher.id}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="font-mono text-sm bg-indigo-100 text-indigo-700 px-2 py-1 rounded">
                        {voucher.voucher_number}
                      </span>
                      <span className="text-sm text-gray-500">
                        {new Date(voucher.voucher_date).toLocaleDateString('en-IN', {
                          day: 'numeric',
                          month: 'short',
                          year: 'numeric'
                        })}
                      </span>
                    </div>
                    <p className="text-gray-900 font-medium">{voucher.narration}</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {voucher.entries?.slice(0, 3).map((entry, idx) => (
                        <span key={idx} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                          {entry.ledger_name}: {entry.debit > 0 ? `Dr ₹${entry.debit.toLocaleString()}` : `Cr ₹${entry.credit.toLocaleString()}`}
                        </span>
                      ))}
                      {voucher.entries?.length > 3 && (
                        <span className="text-xs text-gray-500">+{voucher.entries.length - 3} more</span>
                      )}
                    </div>
                  </div>
                  <div className="text-right ml-4">
                    <p className="text-lg font-bold text-gray-900">₹{(voucher.total_amount || 0).toLocaleString()}</p>
                    <div className="flex gap-2 mt-2">
                      <button
                        onClick={() => { setSelectedVoucher(voucher); setShowViewModal(true); }}
                        className="p-2 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded"
                        title="View Details"
                      >
                        <Eye size={18} />
                      </button>
                      <button
                        onClick={() => handleDeleteVoucher(voucher.id)}
                        className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded"
                        title="Delete"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="p-4 border-t flex justify-center gap-2">
            {Array.from({ length: totalPages }, (_, i) => (
              <button
                key={i}
                onClick={() => setCurrentPage(i + 1)}
                className={`px-3 py-1 rounded ${
                  currentPage === i + 1 
                    ? 'bg-indigo-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {i + 1}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b bg-gradient-to-r from-indigo-600 to-purple-600">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold text-white">Create Journal Entry</h2>
                <button onClick={() => setShowCreateModal(false)} className="text-white hover:text-gray-200">
                  <X size={24} />
                </button>
              </div>
            </div>
            
            <div className="p-6 max-h-[60vh] overflow-y-auto">
              {/* Date and Narration */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Voucher Date *</label>
                  <input
                    type="date"
                    value={formData.voucher_date}
                    onChange={(e) => setFormData({ ...formData, voucher_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Narration *</label>
                  <input
                    type="text"
                    value={formData.narration}
                    onChange={(e) => setFormData({ ...formData, narration: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="Description of this journal entry"
                  />
                </div>
              </div>

              {/* Entries Table */}
              <div className="border rounded-lg overflow-hidden mb-4">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Account (Ledger)</th>
                      <th className="px-4 py-3 text-right text-sm font-medium text-gray-700 w-32">Debit (₹)</th>
                      <th className="px-4 py-3 text-right text-sm font-medium text-gray-700 w-32">Credit (₹)</th>
                      <th className="px-4 py-3 w-12"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {formData.entries.map((entry, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-4 py-3">
                          <select
                            value={entry.ledger_id}
                            onChange={(e) => handleEntryChange(index, 'ledger_id', e.target.value)}
                            className="w-full px-2 py-1 border border-gray-300 rounded"
                          >
                            <option value="">Select Account...</option>
                            <optgroup label="Customers">
                              {ledgerAccounts.filter(l => l.account_type === 'customer').map(l => (
                                <option key={l.id} value={l.id}>{l.name}</option>
                              ))}
                            </optgroup>
                            <optgroup label="Vendors">
                              {ledgerAccounts.filter(l => l.account_type === 'vendor').map(l => (
                                <option key={l.id} value={l.id}>{l.name}</option>
                              ))}
                            </optgroup>
                            <optgroup label="Bank">
                              {ledgerAccounts.filter(l => l.account_type === 'bank').map(l => (
                                <option key={l.id} value={l.id}>{l.name}</option>
                              ))}
                            </optgroup>
                            <optgroup label="Cash">
                              {ledgerAccounts.filter(l => l.account_type === 'cash').map(l => (
                                <option key={l.id} value={l.id}>{l.name}</option>
                              ))}
                            </optgroup>
                            <optgroup label="Income">
                              {ledgerAccounts.filter(l => l.account_type === 'income').map(l => (
                                <option key={l.id} value={l.id}>{l.name}</option>
                              ))}
                            </optgroup>
                            <optgroup label="Expense">
                              {ledgerAccounts.filter(l => l.account_type === 'expense').map(l => (
                                <option key={l.id} value={l.id}>{l.name}</option>
                              ))}
                            </optgroup>
                          </select>
                        </td>
                        <td className="px-4 py-3">
                          <input
                            type="number"
                            value={entry.debit || ''}
                            onChange={(e) => handleEntryChange(index, 'debit', parseFloat(e.target.value) || 0)}
                            className="w-full px-2 py-1 border border-gray-300 rounded text-right"
                            placeholder="0"
                            min="0"
                          />
                        </td>
                        <td className="px-4 py-3">
                          <input
                            type="number"
                            value={entry.credit || ''}
                            onChange={(e) => handleEntryChange(index, 'credit', parseFloat(e.target.value) || 0)}
                            className="w-full px-2 py-1 border border-gray-300 rounded text-right"
                            placeholder="0"
                            min="0"
                          />
                        </td>
                        <td className="px-4 py-3">
                          <button
                            onClick={() => handleRemoveEntry(index)}
                            className="p-1 text-gray-400 hover:text-red-600"
                            disabled={formData.entries.length <= 2}
                          >
                            <X size={18} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot className="bg-gray-100">
                    <tr>
                      <td className="px-4 py-3 font-semibold text-gray-700">Total</td>
                      <td className="px-4 py-3 text-right font-bold text-green-600">₹{totalDebit.toLocaleString()}</td>
                      <td className="px-4 py-3 text-right font-bold text-red-600">₹{totalCredit.toLocaleString()}</td>
                      <td></td>
                    </tr>
                  </tfoot>
                </table>
              </div>

              {/* Add Entry Button */}
              <button
                onClick={handleAddEntry}
                className="text-indigo-600 hover:text-indigo-800 text-sm flex items-center gap-1"
              >
                <Plus size={16} /> Add Another Entry
              </button>

              {/* Balance Check */}
              <div className={`mt-4 p-3 rounded-lg flex items-center gap-2 ${
                isBalanced && totalDebit > 0 ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'
              }`}>
                {isBalanced && totalDebit > 0 ? (
                  <>
                    <CheckCircle size={18} />
                    <span>Voucher is balanced</span>
                  </>
                ) : (
                  <>
                    <AlertTriangle size={18} />
                    <span>
                      {totalDebit === 0 ? 'Enter amounts' : `Difference: ₹${Math.abs(totalDebit - totalCredit).toLocaleString()}`}
                    </span>
                  </>
                )}
              </div>
            </div>
            
            <div className="p-6 border-t bg-gray-50 flex justify-end gap-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateVoucher}
                disabled={!isBalanced || totalDebit === 0}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Save size={18} />
                Create Voucher
              </button>
            </div>
          </div>
        </div>
      )}

      {/* View Modal */}
      {showViewModal && selectedVoucher && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
            <div className="p-6 border-b">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{selectedVoucher.voucher_number}</h2>
                  <p className="text-gray-500">
                    {new Date(selectedVoucher.voucher_date).toLocaleDateString('en-IN', {
                      weekday: 'long',
                      day: 'numeric',
                      month: 'long',
                      year: 'numeric'
                    })}
                  </p>
                </div>
                <button onClick={() => setShowViewModal(false)} className="text-gray-500 hover:text-gray-700">
                  <X size={24} />
                </button>
              </div>
            </div>
            
            <div className="p-6">
              <div className="mb-4">
                <label className="text-sm text-gray-500">Narration</label>
                <p className="text-gray-900 font-medium">{selectedVoucher.narration}</p>
              </div>
              
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Account</th>
                      <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">Debit</th>
                      <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">Credit</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {selectedVoucher.entries?.map((entry, idx) => (
                      <tr key={idx}>
                        <td className="px-4 py-3 text-gray-900">{entry.ledger_name}</td>
                        <td className="px-4 py-3 text-right text-green-600 font-medium">
                          {entry.debit > 0 ? `₹${entry.debit.toLocaleString()}` : '-'}
                        </td>
                        <td className="px-4 py-3 text-right text-red-600 font-medium">
                          {entry.credit > 0 ? `₹${entry.credit.toLocaleString()}` : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot className="bg-gray-100">
                    <tr>
                      <td className="px-4 py-3 font-semibold">Total</td>
                      <td className="px-4 py-3 text-right font-bold text-green-600">
                        ₹{(selectedVoucher.entries?.reduce((s, e) => s + (e.debit || 0), 0) || 0).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-right font-bold text-red-600">
                        ₹{(selectedVoucher.entries?.reduce((s, e) => s + (e.credit || 0), 0) || 0).toLocaleString()}
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
              
              <div className="mt-4 text-xs text-gray-500">
                Created: {new Date(selectedVoucher.created_at).toLocaleString('en-IN')}
              </div>
            </div>
            
            <div className="p-6 border-t bg-gray-50 flex justify-end">
              <button
                onClick={() => setShowViewModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
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

export default JournalVouchers;
