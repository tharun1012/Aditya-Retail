import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  BarChart3, Calendar, TrendingUp, Package, Truck, FileText,
  Clock, AlertTriangle, Download, RefreshCw, Filter, ChevronDown,
  FileSpreadsheet, File
} from 'lucide-react';


const AdvancedReports = () => {
  const [activeReport, setActiveReport] = useState('daily');
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [reportData, setReportData] = useState(null);
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState('all');
  
  // Date filters
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);

  useEffect(() => {
    fetchStores();
  }, []);

  useEffect(() => {
    fetchReport();
  }, [activeReport, selectedStore, fromDate, toDate, selectedYear, selectedMonth]);

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

  const fetchReport = async () => {
    setLoading(true);
    try {
      let url = '';
      const storeParam = selectedStore !== 'all' ? `&store_id=${selectedStore}` : '';
      
      switch (activeReport) {
        case 'daily':
          const date = fromDate || new Date().toISOString().split('T')[0];
          url = `${BACKEND_URL}/api/reports/sales/daily?date=${date}${storeParam}`;
          break;
        case 'monthly':
          url = `${BACKEND_URL}/api/reports/sales/monthly?year=${selectedYear}&month=${selectedMonth}${storeParam}`;
          break;
        case 'yearly':
          url = `${BACKEND_URL}/api/reports/sales/yearly?year=${selectedYear}${storeParam}`;
          break;
        case 'item-sales':
          url = `${BACKEND_URL}/api/reports/sales/by-item?${fromDate ? `from_date=${fromDate}` : ''}${toDate ? `&to_date=${toDate}` : ''}${storeParam}`;
          break;
        case 'item-purchases':
          url = `${BACKEND_URL}/api/reports/purchases/by-item?${fromDate ? `from_date=${fromDate}` : ''}${toDate ? `&to_date=${toDate}` : ''}${storeParam}`;
          break;
        case 'pending-deliveries':
          url = `${BACKEND_URL}/api/reports/pending/deliveries?${storeParam.replace('&', '')}`;
          break;
        case 'pending-po':
          url = `${BACKEND_URL}/api/reports/pending/purchase-orders?${storeParam.replace('&', '')}`;
          break;
        case 'pending-bills':
          url = `${BACKEND_URL}/api/reports/pending/purchase-bills?${storeParam.replace('&', '')}`;
          break;
        default:
          return;
      }
      
      const response = await fetch(url);
      const data = await response.json();
      if (data.status === 'success') {
        setReportData(data);
      }
    } catch (error) {
      console.error('Error fetching report:', error);
    } finally {
      setLoading(false);
    }
  };

  // Export functionality
  const exportReport = async (format) => {
    setExporting(true);
    try {
      let url = '';
      const storeParam = selectedStore !== 'all' ? `&store_id=${selectedStore}` : '';
      
      // Determine the export URL based on report type
      if (['daily', 'monthly', 'yearly', 'item-sales'].includes(activeReport)) {
        const reportType = activeReport === 'item-sales' ? 'item-wise' : activeReport;
        url = `${BACKEND_URL}/api/reports/export/sales/${reportType}?format=${format}${storeParam}`;
        
        if (activeReport === 'daily' && fromDate) {
          url += `&date=${fromDate}`;
        } else if (activeReport === 'monthly') {
          url += `&year=${selectedYear}&month=${selectedMonth}`;
        } else if (activeReport === 'yearly') {
          url += `&year=${selectedYear}`;
        } else if (activeReport === 'item-sales') {
          if (fromDate) url += `&from_date=${fromDate}`;
          if (toDate) url += `&to_date=${toDate}`;
        }
      } else if (activeReport === 'item-purchases') {
        url = `${BACKEND_URL}/api/reports/export/purchases/item-wise?format=${format}${storeParam}`;
        if (fromDate) url += `&from_date=${fromDate}`;
        if (toDate) url += `&to_date=${toDate}`;
      } else if (activeReport.startsWith('pending-')) {
        const reportType = activeReport.replace('pending-', '');
        url = `${BACKEND_URL}/api/reports/export/pending/${reportType === 'po' ? 'purchase-orders' : reportType === 'bills' ? 'purchase-bills' : reportType}?format=${format}${storeParam.replace('&', '')}`;
      }
      
      if (!url) {
        alert('Export not available for this report type');
        return;
      }
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error('Export failed');
      }
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      
      const contentDisposition = response.headers.get('Content-Disposition');
      const filenameMatch = contentDisposition?.match(/filename=(.+)/);
      a.download = filenameMatch ? filenameMatch[1] : `report.${format === 'pdf' ? 'pdf' : 'xlsx'}`;
      
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(downloadUrl);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to export report. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const reportTypes = [
    { id: 'daily', label: 'Daily Sales', icon: Calendar, color: 'blue' },
    { id: 'monthly', label: 'Monthly Sales', icon: BarChart3, color: 'emerald' },
    { id: 'yearly', label: 'Yearly Sales', icon: TrendingUp, color: 'purple' },
    { id: 'item-sales', label: 'Item-wise Sales', icon: Package, color: 'orange' },
    { id: 'item-purchases', label: 'Item-wise Purchases', icon: FileText, color: 'teal' },
    { id: 'pending-deliveries', label: 'Pending Deliveries', icon: Truck, color: 'yellow' },
    { id: 'pending-po', label: 'Pending PO', icon: Clock, color: 'red' },
    { id: 'pending-bills', label: 'Pending Bills', icon: AlertTriangle, color: 'pink' }
  ];

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Advanced Reports</h1>
          <p className="text-gray-500">Date-wise, Item-wise, and Pending Reports</p>
        </div>
        <div className="flex items-center gap-2">
          {/* Export Buttons */}
          <div className="flex items-center gap-1 bg-white border border-gray-200 rounded-lg p-1">
            <button
              onClick={() => exportReport('excel')}
              disabled={exporting || !reportData}
              className="flex items-center gap-2 px-3 py-2 text-sm text-green-700 hover:bg-green-50 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
              title="Export to Excel"
              data-testid="export-excel-btn"
            >
              <FileSpreadsheet className="w-4 h-4" />
              Excel
            </button>
            <button
              onClick={() => exportReport('pdf')}
              disabled={exporting || !reportData}
              className="flex items-center gap-2 px-3 py-2 text-sm text-red-700 hover:bg-red-50 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
              title="Export to PDF"
              data-testid="export-pdf-btn"
            >
              <File className="w-4 h-4" />
              PDF
            </button>
          </div>
          <button
            onClick={fetchReport}
            className="flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700"
            data-testid="refresh-report-btn"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Report Type Selector */}
      <div className="grid grid-cols-4 md:grid-cols-8 gap-2">
        {reportTypes.map((report) => (
          <button
            key={report.id}
            onClick={() => setActiveReport(report.id)}
            className={`p-3 rounded-lg text-center transition-all ${
              activeReport === report.id
                ? `bg-${report.color}-100 border-2 border-${report.color}-500 text-${report.color}-700`
                : 'bg-white border border-gray-200 text-gray-600 hover:border-gray-300'
            }`}
          >
            <report.icon className={`w-5 h-5 mx-auto mb-1 ${activeReport === report.id ? `text-${report.color}-600` : ''}`} />
            <span className="text-xs font-medium">{report.label}</span>
          </button>
        ))}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm p-4">
        <div className="flex flex-wrap items-center gap-4">
          {/* Store Filter */}
          <div>
            <label className="block text-xs text-gray-500 mb-1">Store</label>
            <select
              value={selectedStore}
              onChange={(e) => setSelectedStore(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            >
              <option value="all">All Stores</option>
              {stores.map((store) => (
                <option key={store.id} value={store.id}>{store.name}</option>
              ))}
            </select>
          </div>

          {/* Date Filters for daily/item reports */}
          {['daily', 'item-sales', 'item-purchases'].includes(activeReport) && (
            <>
              <div>
                <label className="block text-xs text-gray-500 mb-1">From Date</label>
                <input
                  type="date"
                  value={fromDate}
                  onChange={(e) => setFromDate(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>
              {activeReport !== 'daily' && (
                <div>
                  <label className="block text-xs text-gray-500 mb-1">To Date</label>
                  <input
                    type="date"
                    value={toDate}
                    onChange={(e) => setToDate(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  />
                </div>
              )}
            </>
          )}

          {/* Month/Year Filters */}
          {['monthly', 'yearly'].includes(activeReport) && (
            <>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Year</label>
                <select
                  value={selectedYear}
                  onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                >
                  {[2024, 2025, 2026].map((year) => (
                    <option key={year} value={year}>{year}</option>
                  ))}
                </select>
              </div>
              {activeReport === 'monthly' && (
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Month</label>
                  <select
                    value={selectedMonth}
                    onChange={(e) => setSelectedMonth(parseInt(e.target.value))}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  >
                    {months.map((month, idx) => (
                      <option key={idx} value={idx + 1}>{month}</option>
                    ))}
                  </select>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Report Content */}
      {loading ? (
        <div className="bg-white rounded-xl shadow-sm p-8 text-center">
          <RefreshCw className="w-8 h-8 text-gray-400 animate-spin mx-auto mb-2" />
          <p className="text-gray-500">Loading report...</p>
        </div>
      ) : reportData ? (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          {/* Summary Cards */}
          {reportData.summary && (
            <div className="p-4 bg-gray-50 border-b grid grid-cols-2 md:grid-cols-4 gap-4">
              {reportData.summary.total_orders !== undefined && (
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-800">{reportData.summary.total_orders}</p>
                  <p className="text-xs text-gray-500">Total Orders</p>
                </div>
              )}
              {reportData.summary.total_sales !== undefined && (
                <div className="text-center">
                  <p className="text-2xl font-bold text-emerald-600">{formatCurrency(reportData.summary.total_sales)}</p>
                  <p className="text-xs text-gray-500">Total Sales</p>
                </div>
              )}
              {reportData.summary.total_revenue !== undefined && (
                <div className="text-center">
                  <p className="text-2xl font-bold text-emerald-600">{formatCurrency(reportData.summary.total_revenue)}</p>
                  <p className="text-xs text-gray-500">Total Revenue</p>
                </div>
              )}
              {reportData.summary.average_order_value !== undefined && (
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">{formatCurrency(reportData.summary.average_order_value)}</p>
                  <p className="text-xs text-gray-500">Avg Order Value</p>
                </div>
              )}
              {reportData.total_pending !== undefined && (
                <div className="text-center">
                  <p className="text-2xl font-bold text-orange-600">{reportData.total_pending}</p>
                  <p className="text-xs text-gray-500">Pending Items</p>
                </div>
              )}
              {reportData.total_pending_amount !== undefined && (
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-600">{formatCurrency(reportData.total_pending_amount)}</p>
                  <p className="text-xs text-gray-500">Pending Amount</p>
                </div>
              )}
            </div>
          )}

          {/* Data Table */}
          <div className="overflow-x-auto">
            {/* Daily/Monthly/Yearly Sales */}
            {['daily', 'monthly', 'yearly'].includes(activeReport) && reportData.orders && (
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order #</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payment</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {reportData.orders.map((order, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium text-teal-600">{order.order_number || order.id?.slice(0, 8)}</td>
                      <td className="px-4 py-3 text-sm">{order.customer_name}</td>
                      <td className="px-4 py-3 text-sm text-gray-500">{formatDate(order.created_at)}</td>
                      <td className="px-4 py-3 text-sm text-right font-medium">{formatCurrency(order.total_amount)}</td>
                      <td className="px-4 py-3 text-sm">{order.payment_method}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          order.order_status === 'delivered' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                        }`}>
                          {order.order_status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {/* Monthly/Yearly Breakdown */}
            {(activeReport === 'monthly' && reportData.daily_breakdown) && (
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Day</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Orders</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Sales</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {reportData.daily_breakdown.map((day, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium">Day {day._id}</td>
                      <td className="px-4 py-3 text-sm text-right">{day.order_count}</td>
                      <td className="px-4 py-3 text-sm text-right font-medium text-emerald-600">{formatCurrency(day.total_sales)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {(activeReport === 'yearly' && reportData.monthly_breakdown) && (
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Month</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Orders</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Sales</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {reportData.monthly_breakdown.map((month, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium">{months[month._id - 1] || `Month ${month._id}`}</td>
                      <td className="px-4 py-3 text-sm text-right">{month.order_count}</td>
                      <td className="px-4 py-3 text-sm text-right font-medium text-emerald-600">{formatCurrency(month.total_sales)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {/* Item-wise Reports */}
            {['item-sales', 'item-purchases'].includes(activeReport) && reportData.items && (
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Qty</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Avg Price</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {reportData.items.map((item, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium">{item.product_name || item._id}</td>
                      <td className="px-4 py-3 text-sm text-gray-500">{item.category || 'N/A'}</td>
                      <td className="px-4 py-3 text-sm text-right">{item.quantity_sold || item.quantity_purchased}</td>
                      <td className="px-4 py-3 text-sm text-right">{formatCurrency(item.avg_price)}</td>
                      <td className="px-4 py-3 text-sm text-right font-medium text-emerald-600">
                        {formatCurrency(item.total_revenue || item.total_cost)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {/* Pending Deliveries */}
            {activeReport === 'pending-deliveries' && reportData.orders && (
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order #</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {reportData.orders.map((order, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium text-teal-600">{order.order_number || order.id?.slice(0, 8)}</td>
                      <td className="px-4 py-3 text-sm">{order.customer_name}</td>
                      <td className="px-4 py-3 text-sm text-gray-500">{formatDate(order.created_at)}</td>
                      <td className="px-4 py-3 text-sm text-right font-medium">{formatCurrency(order.total_amount)}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          order.order_status === 'shipped' ? 'bg-blue-100 text-blue-700' :
                          order.order_status === 'processing' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-orange-100 text-orange-700'
                        }`}>
                          {order.order_status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {/* Pending POs */}
            {activeReport === 'pending-po' && reportData.purchase_orders && (
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">PO #</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vendor</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {reportData.purchase_orders.map((po, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium text-teal-600">{po.po_number || po.id?.slice(0, 8)}</td>
                      <td className="px-4 py-3 text-sm">{po.vendor_name}</td>
                      <td className="px-4 py-3 text-sm text-gray-500">{formatDate(po.created_at)}</td>
                      <td className="px-4 py-3 text-sm text-right font-medium">{formatCurrency(po.total_amount)}</td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-700">
                          {po.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {/* Pending Bills */}
            {activeReport === 'pending-bills' && reportData.bills && (
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bill #</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vendor</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Due Date</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {reportData.bills.map((bill, idx) => (
                    <tr key={idx} className={`hover:bg-gray-50 ${bill.is_overdue ? 'bg-red-50' : ''}`}>
                      <td className="px-4 py-3 text-sm font-medium text-teal-600">{bill.bill_number || bill.id?.slice(0, 8)}</td>
                      <td className="px-4 py-3 text-sm">{bill.vendor_name}</td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {formatDate(bill.due_date)}
                        {bill.is_overdue && <span className="ml-1 text-red-600 text-xs">(Overdue)</span>}
                      </td>
                      <td className="px-4 py-3 text-sm text-right font-medium">{formatCurrency(bill.total_amount)}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          bill.is_overdue ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'
                        }`}>
                          {bill.payment_status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm p-8 text-center">
          <BarChart3 className="w-12 h-12 text-gray-300 mx-auto mb-2" />
          <p className="text-gray-500">Select a report type to view data</p>
        </div>
      )}
    </div>
  );
};

export default AdvancedReports;
