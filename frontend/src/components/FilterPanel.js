import React, { useState } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { Filter, X, ChevronDown, ChevronUp } from 'lucide-react';

const FilterPanel = ({ 
  onApplyFilters, 
  onClearFilters,
  showDateRange = true,
  showAmountRange = true,
  showStatus = true,
  showPaymentMode = true,
  showSearch = true,
  statusOptions = ['All', 'Paid', 'Pending', 'Cancelled'],
  paymentModes = ['All', 'Cash', 'Card', 'UPI', 'NEFT', 'Cheque'],
  searchPlaceholder = 'Search...'
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [filters, setFilters] = useState({
    dateFrom: null,
    dateTo: null,
    amountMin: '',
    amountMax: '',
    status: 'All',
    paymentMode: 'All',
    searchTerm: ''
  });

  const handleApply = () => {
    onApplyFilters(filters);
  };

  const handleClear = () => {
    const clearedFilters = {
      dateFrom: null,
      dateTo: null,
      amountMin: '',
      amountMax: '',
      status: 'All',
      paymentMode: 'All',
      searchTerm: ''
    };
    setFilters(clearedFilters);
    onClearFilters(clearedFilters);
  };

  const activeFilterCount = () => {
    let count = 0;
    if (filters.dateFrom || filters.dateTo) count++;
    if (filters.amountMin || filters.amountMax) count++;
    if (filters.status !== 'All') count++;
    if (filters.paymentMode !== 'All') count++;
    if (filters.searchTerm) count++;
    return count;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg mb-6 overflow-hidden">
      {/* Header */}
      <div 
        className="bg-gradient-to-r from-blue-600 to-indigo-600 p-4 flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <Filter className="w-5 h-5 text-white" />
          <h3 className="text-lg font-bold text-white">Filters</h3>
          {activeFilterCount() > 0 && (
            <span className="bg-white text-blue-600 px-2 py-1 rounded-full text-xs font-bold">
              {activeFilterCount()} active
            </span>
          )}
        </div>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-white" />
        ) : (
          <ChevronDown className="w-5 h-5 text-white" />
        )}
      </div>

      {/* Filter Content */}
      {isExpanded && (
        <div className="p-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Date Range */}
            {showDateRange && (
              <>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    From Date
                  </label>
                  <DatePicker
                    selected={filters.dateFrom}
                    onChange={(date) => setFilters({...filters, dateFrom: date})}
                    dateFormat="dd/MM/yyyy"
                    placeholderText="Select start date"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    To Date
                  </label>
                  <DatePicker
                    selected={filters.dateTo}
                    onChange={(date) => setFilters({...filters, dateTo: date})}
                    dateFormat="dd/MM/yyyy"
                    placeholderText="Select end date"
                    minDate={filters.dateFrom}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </>
            )}

            {/* Amount Range */}
            {showAmountRange && (
              <>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Min Amount (₹)
                  </label>
                  <input
                    type="number"
                    value={filters.amountMin}
                    onChange={(e) => setFilters({...filters, amountMin: e.target.value})}
                    placeholder="0"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Max Amount (₹)
                  </label>
                  <input
                    type="number"
                    value={filters.amountMax}
                    onChange={(e) => setFilters({...filters, amountMax: e.target.value})}
                    placeholder="999999"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </>
            )}

            {/* Status Filter */}
            {showStatus && (
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Status
                </label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters({...filters, status: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {statusOptions.map(status => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Payment Mode Filter */}
            {showPaymentMode && (
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Payment Mode
                </label>
                <select
                  value={filters.paymentMode}
                  onChange={(e) => setFilters({...filters, paymentMode: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {paymentModes.map(mode => (
                    <option key={mode} value={mode}>{mode}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Search */}
            {showSearch && (
              <div className="md:col-span-2">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Search
                </label>
                <input
                  type="text"
                  value={filters.searchTerm}
                  onChange={(e) => setFilters({...filters, searchTerm: e.target.value})}
                  placeholder={searchPlaceholder}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <button
              onClick={handleApply}
              className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold"
            >
              Apply Filters
            </button>
            <button
              onClick={handleClear}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-semibold flex items-center gap-2"
            >
              <X className="w-4 h-4" />
              Clear All
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FilterPanel;
