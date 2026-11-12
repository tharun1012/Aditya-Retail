import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { 
  Download, FileSpreadsheet, FileText, Calendar, ArrowLeft,
  Database, FileCheck, RefreshCw, AlertCircle, CheckCircle,
  TrendingUp, Receipt, ShoppingCart, Building2
} from 'lucide-react';

const ExportCenter = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [exportSummary, setExportSummary] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  
  // Date range
  const [startDate, setStartDate] = useState(() => {
    const date = new Date();
    date.setDate(1); // First day of current month
    return date.toISOString().split('T')[0];
  });
  const [endDate, setEndDate] = useState(() => {
    return new Date().toISOString().split('T')[0];
  });
  
  // GSTR-1 options
  const [gstrMonth, setGstrMonth] = useState(new Date().getMonth() + 1);
  const [gstrYear, setGstrYear] = useState(new Date().getFullYear());
  
  // Export type
  const [exportType, setExportType] = useState('all'); // all, sales, purchases

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  const fetchExportSummary = async () => {
    setLoadingSummary(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/export/summary?start_date=${startDate}&end_date=${endDate}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setExportSummary(data);
      }
    } catch (error) {
      console.error('Error fetching summary:', error);
    } finally {
      setLoadingSummary(false);
    }
  };

  useEffect(() => {
    if (startDate && endDate) {
      fetchExportSummary();
    }
  }, [startDate, endDate]);

  const handleExport = async (format) => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/export/date-range?start_date=${startDate}&end_date=${endDate}&data_type=${exportType}&format=${format}`
      );
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Export failed');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      
      const extension = format === 'excel' ? 'xlsx' : format === 'tally' ? 'xml' : 'json';
      a.download = `export_${startDate}_to_${endDate}.${extension}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      
      showMessage('success', `${format.toUpperCase()} export downloaded successfully!`);
    } catch (error) {
      showMessage('error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTallyExport = async (type) => {
    setLoading(true);
    try {
      let url = `${BACKEND_URL}/api/export/tally/${type}`;
      if (type !== 'masters') {
        url += `?start_date=${startDate}&end_date=${endDate}`;
      }
      
      const response = await fetch(url);
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Export failed');
      }
      
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = `tally_${type}_${new Date().toISOString().split('T')[0]}.xml`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(blobUrl);
      
      showMessage('success', `Tally ${type} XML downloaded successfully!`);
    } catch (error) {
      showMessage('error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGSTR1Export = async (format) => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/export/gstr1?month=${gstrMonth}&year=${gstrYear}&format=${format}`
      );
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Export failed');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `GSTR1_${gstrMonth.toString().padStart(2, '0')}${gstrYear}.${format === 'excel' ? 'xlsx' : 'json'}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      
      showMessage('success', `GSTR-1 ${format.toUpperCase()} downloaded successfully!`);
    } catch (error) {
      showMessage('error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount || 0);
  };

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center px-4 py-2 mb-6 text-gray-700 bg-white hover:bg-gray-100 rounded-lg transition-all border border-gray-300 shadow-sm"
      >
        <ArrowLeft className="h-5 w-5 mr-2" />
        <span className="font-medium">Back</span>
      </button>

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <Database className="w-8 h-8 text-blue-600" />
          Export Center
        </h1>
        <p className="text-gray-600 mt-2">Export your billing data in multiple formats for Tally, GST filing, and more</p>
      </div>

      {/* Message */}
      {message.text && (
        <div className={`mb-6 p-4 rounded-lg flex items-center gap-2 ${
          message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {message.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
          {message.text}
        </div>
      )}

      {/* Date Range Selector */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-blue-600" />
          Select Date Range
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Data Type</label>
            <select
              value={exportType}
              onChange={(e) => setExportType(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Data</option>
              <option value="sales">Sales Only</option>
              <option value="purchases">Purchases Only</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={fetchExportSummary}
              disabled={loadingSummary}
              className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center justify-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${loadingSummary ? 'animate-spin' : ''}`} />
              Refresh Summary
            </button>
          </div>
        </div>

        {/* Export Summary */}
        {exportSummary && (
          <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center gap-2 text-blue-600 mb-1">
                <Receipt className="w-4 h-4" />
                <span className="text-sm font-medium">Invoices</span>
              </div>
              <div className="text-2xl font-bold text-blue-800">{exportSummary.counts?.invoices || 0}</div>
            </div>
            <div className="bg-amber-50 rounded-lg p-4">
              <div className="flex items-center gap-2 text-amber-600 mb-1">
                <ShoppingCart className="w-4 h-4" />
                <span className="text-sm font-medium">Sales Orders</span>
              </div>
              <div className="text-2xl font-bold text-amber-800">{exportSummary.counts?.sales_orders || 0}</div>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center gap-2 text-green-600 mb-1">
                <TrendingUp className="w-4 h-4" />
                <span className="text-sm font-medium">Sales Amount</span>
              </div>
              <div className="text-xl font-bold text-green-800">{formatCurrency(exportSummary.totals?.sales_amount)}</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="flex items-center gap-2 text-purple-600 mb-1">
                <Building2 className="w-4 h-4" />
                <span className="text-sm font-medium">Tax Collected</span>
              </div>
              <div className="text-xl font-bold text-purple-800">{formatCurrency(exportSummary.totals?.tax_collected)}</div>
            </div>
          </div>
        )}
      </div>

      {/* Export Options Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Date Range Export */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <Download className="w-5 h-5" />
              Date Range Export
            </h2>
            <p className="text-blue-100 text-sm mt-1">Export all data for selected period</p>
          </div>
          <div className="p-6 space-y-3">
            <button
              onClick={() => handleExport('excel')}
              disabled={loading}
              className="w-full flex items-center justify-between px-4 py-3 bg-green-50 hover:bg-green-100 rounded-lg border border-green-200 transition-colors"
            >
              <div className="flex items-center gap-3">
                <FileSpreadsheet className="w-6 h-6 text-green-600" />
                <div className="text-left">
                  <div className="font-medium text-green-800">Excel Export</div>
                  <div className="text-xs text-green-600">Download as .xlsx spreadsheet</div>
                </div>
              </div>
              <Download className="w-5 h-5 text-green-600" />
            </button>
            
            <button
              onClick={() => handleExport('tally')}
              disabled={loading}
              className="w-full flex items-center justify-between px-4 py-3 bg-purple-50 hover:bg-purple-100 rounded-lg border border-purple-200 transition-colors"
            >
              <div className="flex items-center gap-3">
                <FileText className="w-6 h-6 text-purple-600" />
                <div className="text-left">
                  <div className="font-medium text-purple-800">Tally XML</div>
                  <div className="text-xs text-purple-600">Import directly into Tally</div>
                </div>
              </div>
              <Download className="w-5 h-5 text-purple-600" />
            </button>
            
            <button
              onClick={() => handleExport('json')}
              disabled={loading}
              className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors"
            >
              <div className="flex items-center gap-3">
                <FileText className="w-6 h-6 text-gray-600" />
                <div className="text-left">
                  <div className="font-medium text-gray-800">JSON Export</div>
                  <div className="text-xs text-gray-600">Raw data format</div>
                </div>
              </div>
              <Download className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Direct Tally Export */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-6 py-4">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <FileCheck className="w-5 h-5" />
              Direct Tally Export
            </h2>
            <p className="text-purple-100 text-sm mt-1">Quick export without backup</p>
          </div>
          <div className="p-6 space-y-3">
            <button
              onClick={() => handleTallyExport('sales')}
              disabled={loading}
              className="w-full flex items-center justify-between px-4 py-3 bg-blue-50 hover:bg-blue-100 rounded-lg border border-blue-200 transition-colors"
            >
              <div className="flex items-center gap-3">
                <Receipt className="w-6 h-6 text-blue-600" />
                <div className="text-left">
                  <div className="font-medium text-blue-800">Sales Vouchers</div>
                  <div className="text-xs text-blue-600">Export sales invoices as Tally vouchers</div>
                </div>
              </div>
              <Download className="w-5 h-5 text-blue-600" />
            </button>
            
            <button
              onClick={() => handleTallyExport('purchases')}
              disabled={loading}
              className="w-full flex items-center justify-between px-4 py-3 bg-amber-50 hover:bg-amber-100 rounded-lg border border-amber-200 transition-colors"
            >
              <div className="flex items-center gap-3">
                <ShoppingCart className="w-6 h-6 text-amber-600" />
                <div className="text-left">
                  <div className="font-medium text-amber-800">Purchase Vouchers</div>
                  <div className="text-xs text-amber-600">Export purchase bills as Tally vouchers</div>
                </div>
              </div>
              <Download className="w-5 h-5 text-amber-600" />
            </button>
            
            <button
              onClick={() => handleTallyExport('masters')}
              disabled={loading}
              className="w-full flex items-center justify-between px-4 py-3 bg-teal-50 hover:bg-teal-100 rounded-lg border border-teal-200 transition-colors"
            >
              <div className="flex items-center gap-3">
                <Building2 className="w-6 h-6 text-teal-600" />
                <div className="text-left">
                  <div className="font-medium text-teal-800">Master Data</div>
                  <div className="text-xs text-teal-600">Customers, Vendors, Products</div>
                </div>
              </div>
              <Download className="w-5 h-5 text-teal-600" />
            </button>
          </div>
        </div>

        {/* GSTR-1 Export */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden md:col-span-2">
          <div className="bg-gradient-to-r from-orange-500 to-red-500 px-6 py-4">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <FileCheck className="w-5 h-5" />
              GSTR-1 Export
            </h2>
            <p className="text-orange-100 text-sm mt-1">Export data in GSTR-1 format for GST filing</p>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Month</label>
                <select
                  value={gstrMonth}
                  onChange={(e) => setGstrMonth(parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                >
                  {months.map((month, idx) => (
                    <option key={idx} value={idx + 1}>{month}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Year</label>
                <select
                  value={gstrYear}
                  onChange={(e) => setGstrYear(parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                >
                  {[2024, 2025, 2026, 2027].map(year => (
                    <option key={year} value={year}>{year}</option>
                  ))}
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={() => handleGSTR1Export('json')}
                  disabled={loading}
                  className="w-full px-4 py-2 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 flex items-center justify-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  JSON Format
                </button>
              </div>
              <div className="flex items-end">
                <button
                  onClick={() => handleGSTR1Export('excel')}
                  disabled={loading}
                  className="w-full px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 flex items-center justify-center gap-2"
                >
                  <FileSpreadsheet className="w-4 h-4" />
                  Excel Format
                </button>
              </div>
            </div>
            
            <div className="bg-orange-50 rounded-lg p-4">
              <h4 className="font-medium text-orange-800 mb-2">GSTR-1 Export Includes:</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-orange-700">
                <div className="flex items-center gap-1">
                  <CheckCircle className="w-4 h-4" />
                  <span>B2B Invoices</span>
                </div>
                <div className="flex items-center gap-1">
                  <CheckCircle className="w-4 h-4" />
                  <span>B2C Large</span>
                </div>
                <div className="flex items-center gap-1">
                  <CheckCircle className="w-4 h-4" />
                  <span>B2C Small (Consolidated)</span>
                </div>
                <div className="flex items-center gap-1">
                  <CheckCircle className="w-4 h-4" />
                  <span>HSN Summary</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 flex items-center gap-4">
            <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
            <div>
              <div className="font-medium text-gray-800">Generating Export...</div>
              <div className="text-sm text-gray-500">This may take a few moments</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExportCenter;
