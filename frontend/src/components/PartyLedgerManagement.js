import React, { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Users, Building2, Plus, Search, Eye, Edit, RefreshCw, Filter,
  IndianRupee, ArrowUpRight, ArrowDownRight, Clock, CheckCircle,
  X, CreditCard, Wallet, AlertTriangle, TrendingUp, TrendingDown,
  FileText, Phone, Mail, MapPin
} from 'lucide-react';
import { showToast } from '../utils/toast';


const PartyLedgerManagement = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('customers');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [summary, setSummary] = useState({});

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    account_type: 'customer',
    phone: '',
    email: '',
    gst_number: '',
    pan_number: '',
    address: '',
    city: '',
    state: '',
    pincode: '',
    credit_limit: 0,
    credit_days: 30,
    opening_balance: 0,
    opening_balance_type: 'debit'
  });

  // Payment form
  const [paymentData, setPaymentData] = useState({
    amount: 0,
    payment_mode: 'cash',
    reference_number: '',
    narration: ''
  });

  const fetchAccounts = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        account_type: activeTab === 'customers' ? 'customer' : 'vendor',
        page: currentPage,
        limit: 20
      });
      if (searchTerm) params.append('search', searchTerm);
      
      const response = await fetch(`${BACKEND_URL}/api/ledger/accounts?${params}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setAccounts(data.accounts);
        setTotalPages(data.pages);
        setSummary(data.summary);
      }
    } catch (error) {
      console.error('Failed to fetch accounts:', error);
      showToast.error('Failed to load accounts');
    } finally {
      setLoading(false);
    }
  }, [activeTab, currentPage, searchTerm]);

  const fetchDashboardStats = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/ledger/dashboard/stats`);
      const data = await response.json();
      if (data.status === 'success') {
        setDashboardStats(data.stats);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const fetchAccountTransactions = async (accountId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/ledger/transactions/${accountId}?limit=50`);
      const data = await response.json();
      if (data.status === 'success') {
        setTransactions(data.transactions);
      }
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
    }
  };

  useEffect(() => {
    fetchAccounts();
    fetchDashboardStats();
  }, [fetchAccounts]);

  const handleCreateAccount = async () => {
    if (!formData.name) {
      showToast.error('Please enter account name');
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/ledger/accounts/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          account_type: activeTab === 'customers' ? 'customer' : 'vendor'
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success(data.message);
        setShowCreateModal(false);
        resetForm();
        fetchAccounts();
        fetchDashboardStats();
      } else {
        showToast.error(data.detail || 'Failed to create account');
      }
    } catch (error) {
      showToast.error('Failed to create account');
    }
  };

  const handlePayment = async () => {
    if (!paymentData.amount || paymentData.amount <= 0) {
      showToast.error('Please enter valid amount');
      return;
    }

    const endpoint = activeTab === 'customers' 
      ? '/api/ledger/payments/receive'
      : '/api/ledger/payments/make';

    try {
      const response = await fetch(`${BACKEND_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ledger_id: selectedAccount.id,
          ...paymentData
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success(data.message);
        setShowPaymentModal(false);
        setPaymentData({ amount: 0, payment_mode: 'cash', reference_number: '', narration: '' });
        fetchAccounts();
        fetchDashboardStats();
        if (showDetailsModal) {
          fetchAccountTransactions(selectedAccount.id);
        }
      } else {
        showToast.error(data.detail || 'Payment failed');
      }
    } catch (error) {
      showToast.error('Payment failed');
    }
  };

  const handleSyncData = async (type) => {
    try {
      const endpoint = type === 'customers' 
        ? '/api/ledger/sync/customers'
        : '/api/ledger/sync/vendors';
      
      const response = await fetch(`${BACKEND_URL}${endpoint}`, { method: 'POST' });
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success(data.message);
        fetchAccounts();
        fetchDashboardStats();
      }
    } catch (error) {
      showToast.error('Sync failed');
    }
  };

  const openAccountDetails = async (account) => {
    setSelectedAccount(account);
    await fetchAccountTransactions(account.id);
    setShowDetailsModal(true);
  };

  const openPaymentModal = (account) => {
    setSelectedAccount(account);
    setPaymentData({ 
      amount: Math.abs(account.current_balance) || 0,
      payment_mode: 'cash', 
      reference_number: '', 
      narration: '' 
    });
    setShowPaymentModal(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      account_type: 'customer',
      phone: '',
      email: '',
      gst_number: '',
      pan_number: '',
      address: '',
      city: '',
      state: '',
      pincode: '',
      credit_limit: 0,
      credit_days: 30,
      opening_balance: 0,
      opening_balance_type: 'debit'
    });
  };

  const customerStats = dashboardStats?.customers || {};
  const vendorStats = dashboardStats?.vendors || {};

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Users className="text-blue-500" />
              Party Ledger Management
            </h1>
            <p className="text-gray-600 mt-1">Manage customer and vendor accounts</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => handleSyncData(activeTab)}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
              title="Sync from existing data"
            >
              <RefreshCw size={18} />
              Sync {activeTab === 'customers' ? 'Customers' : 'Vendors'}
            </button>
            <button
              onClick={() => { resetForm(); setShowCreateModal(true); }}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus size={18} />
              Add {activeTab === 'customers' ? 'Customer' : 'Vendor'}
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Users className="text-blue-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Customers</p>
                <p className="text-2xl font-bold text-gray-900">{customerStats.total_customers || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-100 rounded-lg">
                <ArrowDownRight className="text-green-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Receivables</p>
                <p className="text-2xl font-bold text-green-600">₹{(customerStats.total_receivable || 0).toLocaleString()}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Building2 className="text-purple-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Vendors</p>
                <p className="text-2xl font-bold text-gray-900">{vendorStats.total_vendors || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-red-100 rounded-lg">
                <ArrowUpRight className="text-red-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Payables</p>
                <p className="text-2xl font-bold text-red-600">₹{(vendorStats.total_payable || 0).toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b border-gray-200">
            <nav className="flex">
              <button
                onClick={() => { setActiveTab('customers'); setCurrentPage(1); }}
                className={`px-6 py-4 text-sm font-medium border-b-2 flex items-center gap-2 ${
                  activeTab === 'customers' 
                    ? 'border-blue-500 text-blue-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Users size={18} />
                Customers ({customerStats.total_customers || 0})
              </button>
              <button
                onClick={() => { setActiveTab('vendors'); setCurrentPage(1); }}
                className={`px-6 py-4 text-sm font-medium border-b-2 flex items-center gap-2 ${
                  activeTab === 'vendors' 
                    ? 'border-purple-500 text-purple-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Building2 size={18} />
                Vendors ({vendorStats.total_vendors || 0})
              </button>
            </nav>
          </div>

          {/* Search */}
          <div className="p-4 border-b">
            <div className="relative max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="Search by name, phone, or GST..."
                value={searchTerm}
                onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
          </div>

          {/* Accounts List */}
          <div className="p-4">
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                <p className="mt-4 text-gray-500">Loading accounts...</p>
              </div>
            ) : accounts.length === 0 ? (
              <div className="text-center py-12">
                <Users size={48} className="mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium text-gray-900">No accounts found</p>
                <p className="text-gray-500 mt-2">
                  {searchTerm ? 'Try a different search term' : `Click "Sync ${activeTab}" to import existing data`}
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {accounts.map(account => (
                  <div key={account.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:border-blue-300 transition">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-gray-900">{account.name}</h3>
                          {account.gst_number && (
                            <span className="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded">
                              GST: {account.gst_number}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          {account.phone && (
                            <span className="flex items-center gap-1">
                              <Phone size={14} /> {account.phone}
                            </span>
                          )}
                          {account.city && (
                            <span className="flex items-center gap-1">
                              <MapPin size={14} /> {account.city}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <div className={`text-lg font-bold ${
                          account.current_balance > 0 ? 'text-green-600' : 
                          account.current_balance < 0 ? 'text-red-600' : 'text-gray-500'
                        }`}>
                          ₹{Math.abs(account.current_balance || 0).toLocaleString()}
                          <span className="text-xs font-normal ml-1">
                            {account.current_balance > 0 ? '(Dr)' : account.current_balance < 0 ? '(Cr)' : ''}
                          </span>
                        </div>
                        <p className="text-xs text-gray-500">{account.total_transactions || 0} transactions</p>
                      </div>
                      
                      <div className="flex items-center gap-2 ml-4">
                        <button
                          onClick={() => openAccountDetails(account)}
                          className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg"
                          title="View Details"
                        >
                          <Eye size={18} />
                        </button>
                        {account.current_balance !== 0 && (
                          <button
                            onClick={() => openPaymentModal(account)}
                            className={`px-3 py-1.5 text-sm rounded-lg flex items-center gap-1 ${
                              activeTab === 'customers'
                                ? 'bg-green-600 text-white hover:bg-green-700'
                                : 'bg-red-600 text-white hover:bg-red-700'
                            }`}
                          >
                            <IndianRupee size={14} />
                            {activeTab === 'customers' ? 'Receive' : 'Pay'}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center gap-2 mt-4">
                {Array.from({ length: totalPages }, (_, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentPage(i + 1)}
                    className={`px-3 py-1 rounded ${
                      currentPage === i + 1 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {i + 1}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Create Account Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold">
                  Add New {activeTab === 'customers' ? 'Customer' : 'Vendor'}
                </h2>
                <button onClick={() => setShowCreateModal(false)} className="text-gray-500 hover:text-gray-700">
                  <X size={24} />
                </button>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="Enter name"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                  <input
                    type="text"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">GST Number</label>
                  <input
                    type="text"
                    value={formData.gst_number}
                    onChange={(e) => setFormData({...formData, gst_number: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="29AAECB6071D1ZS"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">PAN Number</label>
                  <input
                    type="text"
                    value={formData.pan_number}
                    onChange={(e) => setFormData({...formData, pan_number: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                <input
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData({...formData, address: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                  <input
                    type="text"
                    value={formData.city}
                    onChange={(e) => setFormData({...formData, city: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                  <input
                    type="text"
                    value={formData.state}
                    onChange={(e) => setFormData({...formData, state: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Pincode</label>
                  <input
                    type="text"
                    value={formData.pincode}
                    onChange={(e) => setFormData({...formData, pincode: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Credit Limit (₹)</label>
                  <input
                    type="number"
                    value={formData.credit_limit}
                    onChange={(e) => setFormData({...formData, credit_limit: parseFloat(e.target.value) || 0})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Credit Days</label>
                  <input
                    type="number"
                    value={formData.credit_days}
                    onChange={(e) => setFormData({...formData, credit_days: parseInt(e.target.value) || 30})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Opening Balance (₹)</label>
                  <input
                    type="number"
                    value={formData.opening_balance}
                    onChange={(e) => setFormData({...formData, opening_balance: parseFloat(e.target.value) || 0})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Balance Type</label>
                  <select
                    value={formData.opening_balance_type}
                    onChange={(e) => setFormData({...formData, opening_balance_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="debit">Debit (They Owe Us)</option>
                    <option value="credit">Credit (We Owe Them)</option>
                  </select>
                </div>
              </div>
            </div>
            <div className="p-6 border-t bg-gray-50 flex justify-end gap-2">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateAccount}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Create Account
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Account Details Modal */}
      {showDetailsModal && selectedAccount && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b bg-gradient-to-r from-blue-600 to-indigo-600">
              <div className="flex justify-between items-start">
                <div className="text-white">
                  <h2 className="text-xl font-bold">{selectedAccount.name}</h2>
                  <p className="text-blue-100 mt-1">
                    {selectedAccount.phone} • {selectedAccount.city}
                  </p>
                </div>
                <button onClick={() => setShowDetailsModal(false)} className="text-white hover:text-blue-200">
                  <X size={24} />
                </button>
              </div>
              <div className="mt-4 flex items-center gap-6">
                <div className="bg-white/20 rounded-lg px-4 py-2">
                  <p className="text-xs text-blue-100">Current Balance</p>
                  <p className="text-2xl font-bold text-white">
                    ₹{Math.abs(selectedAccount.current_balance || 0).toLocaleString()}
                    <span className="text-sm ml-1">
                      {selectedAccount.current_balance > 0 ? '(Dr)' : selectedAccount.current_balance < 0 ? '(Cr)' : ''}
                    </span>
                  </p>
                </div>
                <div className="bg-white/20 rounded-lg px-4 py-2">
                  <p className="text-xs text-blue-100">Total Transactions</p>
                  <p className="text-2xl font-bold text-white">{selectedAccount.total_transactions || 0}</p>
                </div>
              </div>
            </div>
            
            <div className="p-6 max-h-[50vh] overflow-y-auto">
              <h3 className="font-semibold text-gray-900 mb-4">Transaction History</h3>
              {transactions.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No transactions yet</p>
              ) : (
                <div className="space-y-2">
                  {transactions.map(txn => (
                    <div key={txn.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900">{txn.narration || txn.transaction_type}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(txn.transaction_date).toLocaleDateString('en-IN')} • {txn.reference_number}
                        </p>
                      </div>
                      <div className="text-right">
                        {txn.debit_amount > 0 && (
                          <p className="text-green-600 font-medium">+₹{txn.debit_amount.toLocaleString()}</p>
                        )}
                        {txn.credit_amount > 0 && (
                          <p className="text-red-600 font-medium">-₹{txn.credit_amount.toLocaleString()}</p>
                        )}
                        <p className="text-xs text-gray-500">Bal: ₹{txn.balance_after?.toLocaleString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            <div className="p-6 border-t bg-gray-50 flex justify-end gap-2">
              <button
                onClick={() => setShowDetailsModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                Close
              </button>
              {selectedAccount.current_balance !== 0 && (
                <button
                  onClick={() => openPaymentModal(selectedAccount)}
                  className={`px-4 py-2 text-white rounded-lg ${
                    activeTab === 'customers' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'
                  }`}
                >
                  {activeTab === 'customers' ? 'Receive Payment' : 'Make Payment'}
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Payment Modal */}
      {showPaymentModal && selectedAccount && (
        <PaymentAllocationModal
          account={selectedAccount}
          accountType={activeTab}
          onClose={() => setShowPaymentModal(false)}
          onSuccess={() => {
            setShowPaymentModal(false);
            fetchAccounts();
            fetchDashboardStats();
            if (showDetailsModal) {
              fetchAccountTransactions(selectedAccount.id);
            }
          }}
        />
      )}
    </div>
  );
};

// Payment Allocation Modal Component
const PaymentAllocationModal = ({ account, accountType, onClose, onSuccess }) => {
  const [paymentData, setPaymentData] = useState({
    amount: Math.abs(account.current_balance) || 0,
    payment_mode: 'cash',
    reference_number: '',
    narration: '',
    payment_date: new Date().toISOString().split('T')[0]
  });
  const [pendingItems, setPendingItems] = useState([]);
  const [allocations, setAllocations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingItems, setLoadingItems] = useState(true);
  const isCustomer = accountType === 'customers';

  // Fetch pending invoices/bills on mount
  useEffect(() => {
    const fetchPendingItems = async () => {
      try {
        setLoadingItems(true);
        const endpoint = isCustomer 
          ? `/api/ledger/pending/invoices/${account.id}`
          : `/api/ledger/pending/bills/${account.id}`;
        
        const response = await fetch(`${BACKEND_URL}${endpoint}`);
        const data = await response.json();
        
        if (data.status === 'success') {
          const items = isCustomer ? data.invoices : data.bills;
          setPendingItems(items || []);
          // Initialize allocations
          setAllocations(items?.map(item => ({
            id: isCustomer ? item.id : item.id,
            invoice_id: isCustomer ? item.id : undefined,
            bill_id: isCustomer ? undefined : item.id,
            amount: 0,
            pending: item.pending_amount
          })) || []);
        }
      } catch (error) {
        console.error('Failed to fetch pending items:', error);
      } finally {
        setLoadingItems(false);
      }
    };
    
    fetchPendingItems();
  }, [account.id, isCustomer]);

  const handleAllocationChange = (index, amount) => {
    const newAllocations = [...allocations];
    newAllocations[index].amount = Math.min(amount, newAllocations[index].pending);
    setAllocations(newAllocations);
  };

  const autoAllocate = () => {
    let remainingAmount = paymentData.amount;
    const newAllocations = allocations.map(alloc => {
      const allocAmount = Math.min(remainingAmount, alloc.pending);
      remainingAmount -= allocAmount;
      return { ...alloc, amount: allocAmount };
    });
    setAllocations(newAllocations);
  };

  const totalAllocated = allocations.reduce((sum, a) => sum + (a.amount || 0), 0);
  const unallocated = paymentData.amount - totalAllocated;

  const handleSubmit = async () => {
    if (paymentData.amount <= 0) {
      showToast.error('Please enter a valid amount');
      return;
    }

    setLoading(true);
    try {
      const endpoint = isCustomer 
        ? '/api/ledger/payments/receive'
        : '/api/ledger/payments/make';
      
      // Filter only non-zero allocations
      const validAllocations = allocations
        .filter(a => a.amount > 0)
        .map(a => isCustomer ? { invoice_id: a.invoice_id, amount: a.amount } : { bill_id: a.bill_id, amount: a.amount });

      const response = await fetch(`${BACKEND_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ledger_id: account.id,
          amount: paymentData.amount,
          payment_mode: paymentData.payment_mode,
          payment_date: paymentData.payment_date,
          reference_number: paymentData.reference_number,
          narration: paymentData.narration,
          allocations: validAllocations
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success(data.message);
        onSuccess();
      } else {
        showToast.error(data.detail || 'Payment failed');
      }
    } catch (error) {
      showToast.error('Payment failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden">
        <div className={`p-6 border-b ${isCustomer ? 'bg-green-600' : 'bg-red-600'}`}>
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold text-white">
              {isCustomer ? 'Receive Payment' : 'Make Payment'}
            </h2>
            <button onClick={onClose} className="text-white hover:text-gray-200">
              <X size={24} />
            </button>
          </div>
          <p className="text-white/80 mt-1">{account.name}</p>
          <p className="text-white/60 text-sm">
            Outstanding: ₹{Math.abs(account.current_balance || 0).toLocaleString()}
          </p>
        </div>
        
        <div className="p-6 max-h-[60vh] overflow-y-auto space-y-4">
          {/* Payment Details */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Amount (₹) *</label>
              <input
                type="number"
                value={paymentData.amount}
                onChange={(e) => setPaymentData({...paymentData, amount: parseFloat(e.target.value) || 0})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-lg font-bold"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
              <input
                type="date"
                value={paymentData.payment_date}
                onChange={(e) => setPaymentData({...paymentData, payment_date: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Payment Mode</label>
              <select
                value={paymentData.payment_mode}
                onChange={(e) => setPaymentData({...paymentData, payment_mode: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="cash">Cash</option>
                <option value="bank">Bank Transfer</option>
                <option value="upi">UPI</option>
                <option value="cheque">Cheque</option>
                <option value="card">Card</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Reference No.</label>
              <input
                type="text"
                value={paymentData.reference_number}
                onChange={(e) => setPaymentData({...paymentData, reference_number: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="Cheque/UTR No."
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Narration</label>
            <input
              type="text"
              value={paymentData.narration}
              onChange={(e) => setPaymentData({...paymentData, narration: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="Payment details..."
            />
          </div>
          
          {/* Invoice/Bill Allocation */}
          {pendingItems.length > 0 && (
            <div className="mt-4 border-t pt-4">
              <div className="flex justify-between items-center mb-3">
                <h3 className="font-semibold text-gray-900">
                  Allocate to {isCustomer ? 'Invoices' : 'Bills'}
                </h3>
                <button
                  onClick={autoAllocate}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Auto Allocate
                </button>
              </div>
              
              {loadingItems ? (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                </div>
              ) : (
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {pendingItems.map((item, index) => (
                    <div key={item.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div className="flex-1">
                        <p className="font-medium text-sm">
                          {isCustomer ? item.invoice_number : item.bill_number}
                        </p>
                        <p className="text-xs text-gray-500">
                          Pending: ₹{item.pending_amount.toLocaleString()}
                        </p>
                      </div>
                      <input
                        type="number"
                        value={allocations[index]?.amount || 0}
                        onChange={(e) => handleAllocationChange(index, parseFloat(e.target.value) || 0)}
                        className="w-24 px-2 py-1 border rounded text-right text-sm"
                        max={item.pending_amount}
                        min={0}
                      />
                    </div>
                  ))}
                </div>
              )}
              
              {/* Allocation Summary */}
              <div className="mt-3 p-2 bg-blue-50 rounded flex justify-between text-sm">
                <span>Total Allocated: <strong>₹{totalAllocated.toLocaleString()}</strong></span>
                <span className={unallocated > 0 ? 'text-orange-600' : 'text-green-600'}>
                  {unallocated > 0 ? `Unallocated: ₹${unallocated.toLocaleString()}` : 'Fully Allocated'}
                </span>
              </div>
            </div>
          )}
        </div>
        
        <div className="p-6 border-t bg-gray-50 flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading || paymentData.amount <= 0}
            className={`px-6 py-2 text-white rounded-lg flex items-center gap-2 ${
              isCustomer ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'
            } disabled:opacity-50`}
          >
            {loading ? (
              <>
                <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                Processing...
              </>
            ) : (
              <>
                <IndianRupee size={16} />
                {isCustomer ? 'Receive' : 'Pay'} ₹{paymentData.amount.toLocaleString()}
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PartyLedgerManagement;
