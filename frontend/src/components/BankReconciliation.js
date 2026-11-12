import React, { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Building2, Plus, Search, Upload, Check, X, Link2, Unlink,
  ArrowRight, Calendar, FileText, RefreshCw, Download, ChevronDown,
  AlertTriangle, CheckCircle, Eye, IndianRupee, ArrowUpDown
} from 'lucide-react';
import { showToast } from '../utils/toast';


const BankReconciliation = () => {
  const [bankAccounts, setBankAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAddAccount, setShowAddAccount] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [filterReconciled, setFilterReconciled] = useState(null);
  const [dateFilter, setDateFilter] = useState({ from: '', to: '' });
  const [importOptions, setImportOptions] = useState({ autoCategorize: true, autoSync: false });
  const [importResult, setImportResult] = useState(null);
  
  // Form states
  const [accountForm, setAccountForm] = useState({
    name: '',
    account_number: '',
    bank_name: '',
    ifsc_code: '',
    branch: '',
    account_type: 'current',
    opening_balance: 0
  });

  const handleSmartImport = async (file) => {
    if (!selectedAccount) {
      showToast.error('Please select a bank account first');
      return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('bank_account_id', selectedAccount.id);
    formData.append('auto_categorize', importOptions.autoCategorize);
    formData.append('auto_sync', importOptions.autoSync);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/bank-statement/upload`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      setImportResult(data);
      
      if (data.status === 'success') {
        showToast.success(`Imported ${data.imported} transactions`);
        fetchTransactions();
        fetchSummary();
      } else {
        showToast.error(data.detail || 'Import failed');
      }
    } catch (error) {
      setImportResult({ status: 'error', message: error.message });
      showToast.error('Failed to import statement');
    }
  };

  const fetchBankAccounts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/bank-reconciliation/accounts`);
      const data = await response.json();
      if (data.status === 'success') {
        setBankAccounts(data.accounts || []);
        if (data.accounts?.length > 0 && !selectedAccount) {
          setSelectedAccount(data.accounts[0]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch bank accounts:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTransactions = useCallback(async () => {
    if (!selectedAccount) return;
    
    try {
      const params = new URLSearchParams();
      if (filterReconciled !== null) params.append('reconciled', filterReconciled);
      if (dateFilter.from) params.append('from_date', dateFilter.from);
      if (dateFilter.to) params.append('to_date', dateFilter.to);
      
      const response = await fetch(
        `${BACKEND_URL}/api/bank-reconciliation/transactions/${selectedAccount.id}?${params}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setTransactions(data.transactions || []);
      }
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
    }
  }, [selectedAccount, filterReconciled, dateFilter]);

  const fetchSuggestions = useCallback(async () => {
    if (!selectedAccount) return;
    
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/bank-reconciliation/suggestions/${selectedAccount.id}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setSuggestions(data.suggestions || []);
      }
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
    }
  }, [selectedAccount]);

  const fetchSummary = useCallback(async () => {
    if (!selectedAccount) return;
    
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/bank-reconciliation/summary/${selectedAccount.id}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setSummary(data);
      }
    } catch (error) {
      console.error('Failed to fetch summary:', error);
    }
  }, [selectedAccount]);

  useEffect(() => {
    fetchBankAccounts();
  }, []);

  useEffect(() => {
    if (selectedAccount) {
      fetchTransactions();
      fetchSuggestions();
      fetchSummary();
    }
  }, [selectedAccount, fetchTransactions, fetchSuggestions, fetchSummary]);

  const handleAddAccount = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/bank-reconciliation/accounts/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(accountForm)
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success(data.message);
        setShowAddAccount(false);
        setAccountForm({
          name: '', account_number: '', bank_name: '', ifsc_code: '',
          branch: '', account_type: 'current', opening_balance: 0
        });
        fetchBankAccounts();
      } else {
        showToast.error(data.detail || 'Failed to add account');
      }
    } catch (error) {
      showToast.error('Failed to add bank account');
    }
  };

  const handleImportStatement = async (e) => {
    const file = e.target.files[0];
    if (!file || !selectedAccount) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/bank-reconciliation/transactions/import?bank_account_id=${selectedAccount.id}`,
        {
          method: 'POST',
          body: formData
        }
      );
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success(`Imported ${data.imported} transactions`);
        fetchTransactions();
        fetchSummary();
      } else {
        showToast.error(data.detail || 'Import failed');
      }
    } catch (error) {
      showToast.error('Failed to import statement');
    }
    
    setShowImport(false);
  };

  const handleMatch = async (bankTxnId, ledgerTxnId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/bank-reconciliation/match`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bank_transaction_id: bankTxnId,
          ledger_transaction_id: ledgerTxnId,
          match_type: 'manual'
        })
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success('Transactions matched');
        fetchTransactions();
        fetchSuggestions();
        fetchSummary();
      } else {
        showToast.error(data.detail || 'Match failed');
      }
    } catch (error) {
      showToast.error('Failed to match transactions');
    }
  };

  const handleUnmatch = async (bankTxnId) => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/bank-reconciliation/unmatch/${bankTxnId}`,
        { method: 'POST' }
      );
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success('Transaction unmatched');
        fetchTransactions();
        fetchSummary();
      } else {
        showToast.error(data.detail || 'Unmatch failed');
      }
    } catch (error) {
      showToast.error('Failed to unmatch transaction');
    }
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen" data-testid="bank-reconciliation-page">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Building2 className="text-blue-600" />
              Bank Reconciliation
            </h1>
            <p className="text-gray-600 mt-1">Match bank statements with your ledger entries</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setShowImport(true)}
              disabled={!selectedAccount}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2 disabled:opacity-50"
            >
              <Upload size={18} />
              Import Statement
            </button>
            <button
              onClick={() => setShowAddAccount(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus size={18} />
              Add Bank Account
            </button>
          </div>
        </div>

        {/* Bank Account Selector */}
        {bankAccounts.length > 0 && (
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-4">
              <label className="font-medium text-gray-700">Bank Account:</label>
              <select
                value={selectedAccount?.id || ''}
                onChange={(e) => {
                  const account = bankAccounts.find(a => a.id === e.target.value);
                  setSelectedAccount(account);
                }}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg max-w-md"
              >
                {bankAccounts.map(account => (
                  <option key={account.id} value={account.id}>
                    {account.name} - {account.bank_name} ({account.account_number.slice(-4)})
                  </option>
                ))}
              </select>
              
              {selectedAccount && (
                <div className="flex items-center gap-4 ml-auto">
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Bank Balance</p>
                    <p className="text-lg font-bold text-gray-900">
                      ₹{(selectedAccount.current_balance || 0).toLocaleString()}
                    </p>
                  </div>
                  {selectedAccount.unreconciled_count > 0 && (
                    <div className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm font-medium">
                      {selectedAccount.unreconciled_count} unreconciled
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Reconciliation Summary */}
      {summary && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Bank Balance</p>
            <p className="text-2xl font-bold text-blue-600">₹{(summary.bank_balance || 0).toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Ledger Balance</p>
            <p className="text-2xl font-bold text-green-600">₹{(summary.ledger_balance || 0).toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Difference</p>
            <p className={`text-2xl font-bold ${summary.difference === 0 ? 'text-green-600' : 'text-red-600'}`}>
              ₹{Math.abs(summary.difference || 0).toLocaleString()}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Unreconciled (Bank)</p>
            <p className="text-2xl font-bold text-yellow-600">{summary.unreconciled_bank?.count || 0}</p>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="grid grid-cols-3 gap-6">
        {/* Bank Transactions */}
        <div className="col-span-2 bg-white rounded-lg shadow">
          <div className="p-4 border-b flex items-center justify-between">
            <h2 className="font-semibold text-gray-900">Bank Transactions</h2>
            <div className="flex gap-2">
              <select
                value={filterReconciled === null ? 'all' : filterReconciled.toString()}
                onChange={(e) => {
                  const val = e.target.value;
                  setFilterReconciled(val === 'all' ? null : val === 'true');
                }}
                className="px-3 py-1 border border-gray-300 rounded text-sm"
              >
                <option value="all">All</option>
                <option value="false">Unreconciled</option>
                <option value="true">Reconciled</option>
              </select>
            </div>
          </div>
          
          <div className="divide-y max-h-[500px] overflow-y-auto">
            {loading ? (
              <div className="p-8 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
              </div>
            ) : transactions.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <Building2 size={48} className="mx-auto mb-3 text-gray-300" />
                <p>No transactions found</p>
                <p className="text-sm">Import a bank statement to get started</p>
              </div>
            ) : (
              transactions.map((txn) => (
                <div 
                  key={txn.id} 
                  className={`p-4 hover:bg-gray-50 ${txn.is_reconciled ? 'bg-green-50' : ''}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm text-gray-500">{txn.transaction_date}</span>
                        {txn.is_reconciled ? (
                          <CheckCircle size={16} className="text-green-500" />
                        ) : (
                          <AlertTriangle size={16} className="text-yellow-500" />
                        )}
                      </div>
                      <p className="font-medium text-gray-900">{txn.description}</p>
                      {txn.reference_number && (
                        <p className="text-xs text-gray-500">Ref: {txn.reference_number}</p>
                      )}
                    </div>
                    <div className="text-right">
                      {txn.credit_amount > 0 && (
                        <p className="text-green-600 font-bold">+₹{txn.credit_amount.toLocaleString()}</p>
                      )}
                      {txn.debit_amount > 0 && (
                        <p className="text-red-600 font-bold">-₹{txn.debit_amount.toLocaleString()}</p>
                      )}
                      {txn.is_reconciled && (
                        <button
                          onClick={() => handleUnmatch(txn.id)}
                          className="text-xs text-gray-500 hover:text-red-600 mt-1 flex items-center gap-1"
                        >
                          <Unlink size={12} /> Unmatch
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Auto-Match Suggestions */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-900 flex items-center gap-2">
              <Link2 size={18} />
              Match Suggestions
            </h2>
          </div>
          
          <div className="divide-y max-h-[500px] overflow-y-auto">
            {suggestions.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                <CheckCircle size={48} className="mx-auto mb-3 text-green-300" />
                <p>No pending matches</p>
              </div>
            ) : (
              suggestions.map((suggestion, idx) => (
                <div key={idx} className="p-4">
                  <div className="mb-3">
                    <p className="text-sm text-gray-500">{suggestion.bank_transaction.transaction_date}</p>
                    <p className="font-medium">{suggestion.bank_transaction.description}</p>
                    <p className={suggestion.bank_transaction.credit_amount > 0 ? 'text-green-600' : 'text-red-600'}>
                      {suggestion.bank_transaction.credit_amount > 0 ? '+' : '-'}₹
                      {(suggestion.bank_transaction.credit_amount || suggestion.bank_transaction.debit_amount).toLocaleString()}
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    {suggestion.suggested_matches.map((match, mIdx) => (
                      <div 
                        key={mIdx}
                        className="p-2 bg-gray-50 rounded flex items-center justify-between"
                      >
                        <div className="text-sm">
                          <p className="font-medium">{match.ledger_name}</p>
                          <p className="text-gray-500">{match.narration}</p>
                        </div>
                        <button
                          onClick={() => handleMatch(suggestion.bank_transaction.id, match.id)}
                          className="p-2 bg-green-100 text-green-600 rounded hover:bg-green-200"
                          title="Match"
                        >
                          <Check size={16} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Add Account Modal */}
      {showAddAccount && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6 border-b bg-blue-600">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold text-white">Add Bank Account</h2>
                <button onClick={() => setShowAddAccount(false)} className="text-white hover:text-gray-200">
                  <X size={24} />
                </button>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Account Name *</label>
                <input
                  type="text"
                  value={accountForm.name}
                  onChange={(e) => setAccountForm({...accountForm, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="e.g., Main Business Account"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Bank Name *</label>
                  <input
                    type="text"
                    value={accountForm.bank_name}
                    onChange={(e) => setAccountForm({...accountForm, bank_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="HDFC Bank"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Account Type</label>
                  <select
                    value={accountForm.account_type}
                    onChange={(e) => setAccountForm({...accountForm, account_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="current">Current</option>
                    <option value="savings">Savings</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Account Number *</label>
                <input
                  type="text"
                  value={accountForm.account_number}
                  onChange={(e) => setAccountForm({...accountForm, account_number: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">IFSC Code</label>
                  <input
                    type="text"
                    value={accountForm.ifsc_code}
                    onChange={(e) => setAccountForm({...accountForm, ifsc_code: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Branch</label>
                  <input
                    type="text"
                    value={accountForm.branch}
                    onChange={(e) => setAccountForm({...accountForm, branch: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Opening Balance (₹)</label>
                <input
                  type="number"
                  value={accountForm.opening_balance}
                  onChange={(e) => setAccountForm({...accountForm, opening_balance: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>
            <div className="p-6 border-t bg-gray-50 flex justify-end gap-2">
              <button
                onClick={() => setShowAddAccount(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                onClick={handleAddAccount}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Add Account
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Import Modal - Enhanced with PDF support and Smart Sync */}
      {showImport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
            <div className="p-6 border-b bg-gradient-to-r from-blue-600 to-indigo-600">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <Upload size={24} />
                  Smart Bank Statement Import
                </h2>
                <button onClick={() => setShowImport(false)} className="text-white hover:text-gray-200">
                  <X size={24} />
                </button>
              </div>
            </div>
            
            <div className="p-6 space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-2">Supported Formats</h3>
                <div className="flex gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <FileText size={18} className="text-green-600" />
                    <span>CSV Files</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <FileText size={18} className="text-red-600" />
                    <span>PDF Statements</span>
                  </div>
                </div>
                <p className="text-xs text-blue-700 mt-2">
                  Supports all major Indian banks: SBI, HDFC, ICICI, Axis, Kotak, etc.
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Statement (CSV or PDF)
                </label>
                <input
                  type="file"
                  accept=".csv,.pdf"
                  onChange={(e) => {
                    const file = e.target.files[0];
                    if (file) {
                      handleSmartImport(file);
                    }
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  data-testid="bank-statement-file-input"
                />
              </div>
              
              <div className="space-y-3">
                <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                  <input
                    type="checkbox"
                    checked={importOptions.autoCategorize}
                    onChange={(e) => setImportOptions({...importOptions, autoCategorize: e.target.checked})}
                    className="w-4 h-4 text-blue-600"
                  />
                  <div>
                    <p className="font-medium text-gray-800">Auto-Categorize Transactions</p>
                    <p className="text-xs text-gray-500">Automatically identify payments, receipts, expenses, etc.</p>
                  </div>
                </label>
                
                <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                  <input
                    type="checkbox"
                    checked={importOptions.autoSync}
                    onChange={(e) => setImportOptions({...importOptions, autoSync: e.target.checked})}
                    className="w-4 h-4 text-green-600"
                  />
                  <div>
                    <p className="font-medium text-gray-800">Auto-Sync to Accounting</p>
                    <p className="text-xs text-gray-500">Create payment/receipt/expense entries automatically</p>
                  </div>
                </label>
              </div>
              
              {importResult && (
                <div className={`p-4 rounded-lg ${importResult.status === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                  <h4 className={`font-semibold ${importResult.status === 'success' ? 'text-green-800' : 'text-red-800'}`}>
                    {importResult.status === 'success' ? 'Import Successful!' : 'Import Failed'}
                  </h4>
                  {importResult.status === 'success' && (
                    <div className="mt-2 text-sm text-green-700 space-y-1">
                      <p>✓ {importResult.imported} transactions imported</p>
                      <p>✓ {importResult.categorized} auto-categorized</p>
                      {importResult.synced > 0 && <p>✓ {importResult.synced} synced to accounting</p>}
                      {importResult.skipped > 0 && <p className="text-yellow-700">⚠ {importResult.skipped} skipped (duplicates)</p>}
                    </div>
                  )}
                  {importResult.status !== 'success' && (
                    <p className="text-sm text-red-700 mt-1">{importResult.message || importResult.detail}</p>
                  )}
                </div>
              )}
            </div>
            
            <div className="p-4 bg-gray-50 border-t flex justify-end gap-2">
              <button
                onClick={() => {
                  setShowImport(false);
                  setImportResult(null);
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                {importResult ? 'Close' : 'Cancel'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BankReconciliation;
