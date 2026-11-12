import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { TrendingDown, Plus, Search, Calendar, DollarSign, Tag, Eye } from 'lucide-react';
import DocumentActions from './DocumentActions';
import BulkActionToolbar from './BulkActionToolbar';
import FilterPanel from './FilterPanel';
import { exportExpensesToExcel } from '../utils/excelExport';


const ExpenseManagement = () => {
  const [expenses, setExpenses] = useState([]);
  const [filteredExpenses, setFilteredExpenses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [totalAmount, setTotalAmount] = useState(0);
  const [selectedExpense, setSelectedExpense] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedItems, setSelectedItems] = useState([]);
  const [filters, setFilters] = useState(null);

  const [formData, setFormData] = useState({
    category: 'Office Supplies',
    amount: 0,
    payment_mode: 'cash',
    vendor_name: '',
    description: '',
    expense_date: new Date().toISOString().split('T')[0],
    created_by: 'admin',
    notes: ''
  });

  const expenseCategories = [
    'Office Supplies',
    'Utilities',
    'Rent',
    'Salaries',
    'Marketing',
    'Transportation',
    'Maintenance',
    'Insurance',
    'Miscellaneous'
  ];

  useEffect(() => {
    fetchExpenses();
    fetchCategories();
  }, [categoryFilter]);

  const fetchExpenses = async () => {
    try {
      const url = categoryFilter === 'all' 
        ? `${BACKEND_URL}/api/expenses/`
        : `${BACKEND_URL}/api/expenses/?category=${categoryFilter}`;
      
      const response = await fetch(url);
      const data = await response.json();
      if (data.status === 'success') {
        setExpenses(data.expenses);
        setTotalAmount(data.total_amount || 0);
      }
    } catch (error) {
      console.error('Failed to fetch expenses:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/expenses/categories`);
      const data = await response.json();
      if (data.status === 'success') {
        setCategories(data.categories);
      }
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  // Apply filters
  useEffect(() => {
    let filtered = [...expenses];

    if (filters?.dateFrom) {
      filtered = filtered.filter(e => new Date(e.expense_date) >= filters.dateFrom);
    }
    if (filters?.dateTo) {
      filtered = filtered.filter(e => new Date(e.expense_date) <= filters.dateTo);
    }
    if (filters?.amountMin) {
      filtered = filtered.filter(e => e.amount >= parseFloat(filters.amountMin));
    }
    if (filters?.amountMax) {
      filtered = filtered.filter(e => e.amount <= parseFloat(filters.amountMax));
    }
    if (filters?.status && filters.status !== 'All') {
      filtered = filtered.filter(e => e.payment_status?.toLowerCase() === filters.status.toLowerCase());
    }
    if (filters?.paymentMode && filters.paymentMode !== 'All') {
      filtered = filtered.filter(e => e.payment_mode?.toLowerCase() === filters.paymentMode.toLowerCase());
    }
    if (filters?.searchTerm) {
      filtered = filtered.filter(e =>
        e.description?.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
        e.vendor_name?.toLowerCase().includes(filters.searchTerm.toLowerCase())
      );
    }

    setFilteredExpenses(filtered);
  }, [expenses, filters]);

  const handleApplyFilters = (newFilters) => {
    setFilters(newFilters);
  };

  const handleClearFilters = () => {
    setFilters(null);
    setFilteredExpenses(expenses);
  };

  // Bulk actions
  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedItems(filteredExpenses.map(e => e.id));
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
    const selectedExpenses = expenses.filter(e => selectedItems.includes(e.id));
    const result = exportExpensesToExcel(selectedExpenses);
    if (result.success) {
      alert(`Exported ${selectedExpenses.length} expenses to ${result.filename}`);
    } else {
      alert('Export failed: ' + result.error);
    }
  };

  const handleDeleteSelected = async () => {
    if (window.confirm(`Are you sure you want to delete ${selectedItems.length} expenses?`)) {
      try {
        for (const id of selectedItems) {
          await fetch(`${BACKEND_URL}/api/expenses/${id}`, { method: 'DELETE' });
        }
        alert('Expenses deleted successfully');
        setSelectedItems([]);
        fetchExpenses();
      } catch (error) {
        console.error('Delete failed:', error);
        alert('Failed to delete expenses');
      }
    }
  };

  const handleCreateExpense = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/expenses/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();
      if (data.status === 'success') {
        alert(`Expense Recorded: ${data.expense_number}`);
        setShowCreateModal(false);
        fetchExpenses();
        resetForm();
      }
    } catch (error) {
      console.error('Failed to create expense:', error);
      alert('Failed to record expense');
    }
  };

  const resetForm = () => {
    setFormData({
      category: 'Office Supplies',
      amount: 0,
      payment_mode: 'cash',
      vendor_name: '',
      description: '',
      expense_date: new Date().toISOString().split('T')[0],
      created_by: 'admin',
      notes: ''
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
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
              <TrendingDown className="text-orange-500" />
              Expense Management
            </h1>
            <p className="text-gray-600 mt-1">Record and track business expenses</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 flex items-center gap-2"
          >
            <Plus size={20} />
            Record Expense
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Expenses</p>
                <p className="text-2xl font-bold text-gray-900">₹{totalAmount.toFixed(2)}</p>
              </div>
              <DollarSign className="text-orange-500" size={32} />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Entries</p>
                <p className="text-2xl font-bold text-gray-900">{expenses.length}</p>
              </div>
              <Tag className="text-blue-500" size={32} />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Categories</p>
                <p className="text-2xl font-bold text-gray-900">{categories.length || expenseCategories.length}</p>
              </div>
              <Tag className="text-purple-500" size={32} />
            </div>
          </div>
        </div>

        {/* Advanced Filters */}
        <FilterPanel
          onApplyFilters={handleApplyFilters}
          onClearFilters={handleClearFilters}
          showDateRange={true}
          showAmountRange={true}
          showStatus={true}
          showPaymentMode={true}
          showSearch={true}
          statusOptions={['All', 'Paid', 'Pending', 'Approved']}
          paymentModes={['All', 'Cash', 'Card', 'UPI', 'NEFT', 'Cheque']}
          searchPlaceholder="Search by description or vendor..."
        />

        {/* Bulk Actions */}
        <BulkActionToolbar
          selectedCount={selectedItems.length}
          onExportExcel={handleExportExcel}
          onDelete={handleDeleteSelected}
          onClear={() => setSelectedItems([])}
          showPrint={false}
        />
      </div>

      {/* Expense List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-3 py-3 text-left">
                <input
                  type="checkbox"
                  checked={selectedItems.length === filteredExpenses.length && filteredExpenses.length > 0}
                  onChange={handleSelectAll}
                  className="w-4 h-4 text-orange-600 rounded focus:ring-orange-500"
                />
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Expense #</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vendor</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Payment</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredExpenses.length === 0 ? (
              <tr>
                <td colSpan="9" className="px-6 py-12 text-center text-gray-500">
                  No expenses recorded
                </td>
              </tr>
            ) : (
              filteredExpenses.map((expense) => (
                <tr key={expense.id} className={selectedItems.includes(expense.id) ? 'bg-orange-50' : ''}>
                  <td className="px-3 py-4">
                    <input
                      type="checkbox"
                      checked={selectedItems.includes(expense.id)}
                      onChange={() => handleSelectItem(expense.id)}
                      className="w-4 h-4 text-orange-600 rounded focus:ring-orange-500"
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {expense.expense_number}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {expense.description}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800">
                      {expense.category}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {expense.vendor_name || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">
                    ₹{expense.amount?.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(expense.expense_date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                      {expense.payment_mode}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => {
                        setSelectedExpense(expense);
                        setShowDetailsModal(true);
                      }}
                      className="text-orange-600 hover:text-orange-900"
                      title="View & Share"
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

      {/* Expense Details Modal */}
      {showDetailsModal && selectedExpense && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold">Expense Details</h2>
              <p className="text-gray-600">{selectedExpense.expense_number}</p>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-600">Category</p>
                  <p className="font-medium">{selectedExpense.category}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Amount</p>
                  <p className="font-medium text-lg">₹{selectedExpense.amount?.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Vendor</p>
                  <p className="font-medium">{selectedExpense.vendor_name || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Payment Mode</p>
                  <p className="font-medium">{selectedExpense.payment_mode}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Date</p>
                  <p className="font-medium">{new Date(selectedExpense.expense_date).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Created By</p>
                  <p className="font-medium">{selectedExpense.created_by}</p>
                </div>
              </div>
              <div className="mb-4">
                <p className="text-sm text-gray-600">Description</p>
                <p className="font-medium">{selectedExpense.description}</p>
              </div>
              {selectedExpense.notes && (
                <div className="mb-4">
                  <p className="text-sm text-gray-600">Notes</p>
                  <p className="font-medium">{selectedExpense.notes}</p>
                </div>
              )}

              {/* Document Actions */}
              <div className="border-t border-gray-200 pt-4 mt-4">
                <h3 className="font-semibold mb-3">Document Actions</h3>
                <DocumentActions 
                  document={selectedExpense} 
                  documentType="expense"
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

      {/* Create Expense Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold">Record Expense</h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category *</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                  >
                    {expenseCategories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Amount *</label>
                  <input
                    type="number"
                    value={formData.amount}
                    onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Payment Mode *</label>
                  <select
                    value={formData.payment_mode}
                    onChange={(e) => setFormData({ ...formData, payment_mode: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                  >
                    <option value="cash">Cash</option>
                    <option value="upi">UPI</option>
                    <option value="bank_transfer">Bank Transfer</option>
                    <option value="credit_card">Credit Card</option>
                    <option value="debit_card">Debit Card</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Expense Date *</label>
                  <input
                    type="date"
                    value={formData.expense_date}
                    onChange={(e) => setFormData({ ...formData, expense_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Vendor Name</label>
                  <input
                    type="text"
                    value={formData.vendor_name}
                    onChange={(e) => setFormData({ ...formData, vendor_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                    placeholder="Enter vendor name"
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                    rows="3"
                    placeholder="Enter expense description"
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                    rows="2"
                    placeholder="Additional notes (optional)"
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
                onClick={handleCreateExpense}
                className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
              >
                Record Expense
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExpenseManagement;