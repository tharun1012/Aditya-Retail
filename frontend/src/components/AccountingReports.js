import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { BarChart3, Download, Calendar, TrendingUp, DollarSign, ShoppingCart, Package, FileSpreadsheet } from 'lucide-react';
import { 
  SalesTrendChart, 
  ExpenseCategoryPieChart, 
  PaymentModeChart, 
  PurchaseVsSalesChart,
  GSTSummaryChart 
} from './Charts';
import { exportSalesReportToExcel } from '../utils/excelExport';


const AccountingReports = () => {
  const [activeReport, setActiveReport] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState({
    from_date: new Date(new Date().setDate(1)).toISOString().split('T')[0],
    to_date: new Date().toISOString().split('T')[0]
  });
  const [selectedPeriod, setSelectedPeriod] = useState('this_month');

  const [dashboardData, setDashboardData] = useState(null);
  const [salesReport, setSalesReport] = useState(null);
  const [purchaseReport, setPurchaseReport] = useState(null);
  const [expenseReport, setExpenseReport] = useState(null);
  const [gstReport, setGstReport] = useState(null);
  const [paymentReceiptReport, setPaymentReceiptReport] = useState(null);
  
  // New GST Report States
  const [gstr2bReport, setGstr2bReport] = useState(null);
  const [taxSlabReport, setTaxSlabReport] = useState(null);
  const [b2bB2cReport, setB2bB2cReport] = useState(null);
  const [taxBifurcationReport, setTaxBifurcationReport] = useState(null);
  const [gstr9Report, setGstr9Report] = useState(null);
  const [activeGstTab, setActiveGstTab] = useState('summary');
  const [selectedFinancialYear, setSelectedFinancialYear] = useState('2025-26');

  useEffect(() => {
    fetchDashboardSummary();
  }, []);

  const fetchDashboardSummary = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/accounting/reports/dashboard-summary`);
      const data = await response.json();
      if (data.status === 'success') {
        setDashboardData(data.summary);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSalesReport = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/accounting/reports/sales-summary?from_date=${dateRange.from_date}&to_date=${dateRange.to_date}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setSalesReport(data.report);
      }
    } catch (error) {
      console.error('Failed to fetch sales report:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPurchaseReport = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/accounting/reports/purchase-summary?from_date=${dateRange.from_date}&to_date=${dateRange.to_date}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setPurchaseReport(data.report);
      }
    } catch (error) {
      console.error('Failed to fetch purchase report:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchExpenseReport = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/accounting/reports/expense-summary?from_date=${dateRange.from_date}&to_date=${dateRange.to_date}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setExpenseReport(data.report);
      }
    } catch (error) {
      console.error('Failed to fetch expense report:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchGSTReport = async (reportType = 'gstr1') => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/accounting/reports/gst-report?from_date=${dateRange.from_date}&to_date=${dateRange.to_date}&report_type=${reportType}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setGstReport(data);
      }
    } catch (error) {
      console.error('Failed to fetch GST report:', error);
    } finally {
      setLoading(false);
    }
  };

  // New GST Report Fetch Functions
  const fetchGstr2bReport = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/financial-reports/gst/gstr2b?period=${selectedPeriod}&from_date=${dateRange.from_date}&to_date=${dateRange.to_date}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setGstr2bReport(data);
      }
    } catch (error) {
      console.error('Failed to fetch GSTR-2B report:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTaxSlabReport = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/financial-reports/gst/tax-slabs?period=${selectedPeriod}&from_date=${dateRange.from_date}&to_date=${dateRange.to_date}&report_type=both`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setTaxSlabReport(data);
      }
    } catch (error) {
      console.error('Failed to fetch tax slab report:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchB2bB2cReport = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/financial-reports/gst/b2b-b2c-analysis?period=${selectedPeriod}&from_date=${dateRange.from_date}&to_date=${dateRange.to_date}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setB2bB2cReport(data);
      }
    } catch (error) {
      console.error('Failed to fetch B2B/B2C report:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTaxBifurcationReport = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/financial-reports/gst/tax-bifurcation?period=${selectedPeriod}&from_date=${dateRange.from_date}&to_date=${dateRange.to_date}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setTaxBifurcationReport(data);
      }
    } catch (error) {
      console.error('Failed to fetch tax bifurcation report:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAllGstReports = async () => {
    await Promise.all([
      fetchGstr2bReport(),
      fetchTaxSlabReport(),
      fetchB2bB2cReport(),
      fetchTaxBifurcationReport()
    ]);
  };

  const fetchGstr9Report = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/financial-reports/gst/gstr9?financial_year=${selectedFinancialYear}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setGstr9Report(data);
      }
    } catch (error) {
      console.error('Failed to fetch GSTR-9 report:', error);
    } finally {
      setLoading(false);
    }
  };

  // Excel Export Functions
  const downloadGstr1Excel = () => {
    const url = `${BACKEND_URL}/api/financial-reports/gst/export/gstr1?period=${selectedPeriod}&from_date=${dateRange.from_date}&to_date=${dateRange.to_date}`;
    window.open(url, '_blank');
  };

  const downloadGstr2bExcel = () => {
    const url = `${BACKEND_URL}/api/financial-reports/gst/export/gstr2b?period=${selectedPeriod}&from_date=${dateRange.from_date}&to_date=${dateRange.to_date}`;
    window.open(url, '_blank');
  };

  const downloadGstr9Excel = () => {
    const url = `${BACKEND_URL}/api/financial-reports/gst/export/gstr9?financial_year=${selectedFinancialYear}`;
    window.open(url, '_blank');
  };

  const fetchPaymentReceiptReport = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/accounting/reports/payment-receipt-summary?from_date=${dateRange.from_date}&to_date=${dateRange.to_date}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setPaymentReceiptReport(data.report);
      }
    } catch (error) {
      console.error('Failed to fetch payment/receipt report:', error);
    } finally {
      setLoading(false);
    }
  };

  const reportTabs = [
    { id: 'dashboard', name: 'Dashboard', icon: BarChart3 },
    { id: 'sales', name: 'Sales Report', icon: TrendingUp },
    { id: 'purchase', name: 'Purchase Report', icon: ShoppingCart },
    { id: 'expense', name: 'Expense Report', icon: DollarSign },
    { id: 'gst', name: 'GST Reports', icon: Package },
    { id: 'payments', name: 'Payments & Receipts', icon: DollarSign },
    { id: 'data_export', name: 'Data Export', icon: FileSpreadsheet }
  ];

  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-green-400 to-green-600 text-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Total Sales</p>
              <p className="text-3xl font-bold">₹{dashboardData?.total_sales?.toFixed(2) || '0.00'}</p>
            </div>
            <TrendingUp size={40} className="opacity-80" />
          </div>
        </div>
        <div className="bg-gradient-to-br from-blue-400 to-blue-600 text-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Total Purchases</p>
              <p className="text-3xl font-bold">₹{dashboardData?.total_purchases?.toFixed(2) || '0.00'}</p>
            </div>
            <ShoppingCart size={40} className="opacity-80" />
          </div>
        </div>
        <div className="bg-gradient-to-br from-orange-400 to-orange-600 text-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm">Total Expenses</p>
              <p className="text-3xl font-bold">₹{dashboardData?.total_expenses?.toFixed(2) || '0.00'}</p>
            </div>
            <DollarSign size={40} className="opacity-80" />
          </div>
        </div>
        <div className="bg-gradient-to-br from-purple-400 to-purple-600 text-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Gross Profit</p>
              <p className="text-3xl font-bold">₹{dashboardData?.gross_profit?.toFixed(2) || '0.00'}</p>
            </div>
            <BarChart3 size={40} className="opacity-80" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-gray-600 text-sm">Online Orders</p>
          <p className="text-2xl font-bold text-gray-900">{dashboardData?.online_orders || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-gray-600 text-sm">Offline Invoices</p>
          <p className="text-2xl font-bold text-gray-900">{dashboardData?.offline_invoices || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-gray-600 text-sm">Purchase Orders</p>
          <p className="text-2xl font-bold text-gray-900">{dashboardData?.purchase_orders || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-gray-600 text-sm">Expense Entries</p>
          <p className="text-2xl font-bold text-gray-900">{dashboardData?.expense_entries || 0}</p>
        </div>
      </div>

      {/* Charts Section */}
      <div className="mt-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Analytics & Trends</h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Sales Trend */}
          <SalesTrendChart data={[
            { month: 'Jul', sales: dashboardData?.sales_trend?.[0] || 50000 },
            { month: 'Aug', sales: dashboardData?.sales_trend?.[1] || 65000 },
            { month: 'Sep', sales: dashboardData?.sales_trend?.[2] || 80000 },
            { month: 'Oct', sales: dashboardData?.sales_trend?.[3] || 75000 },
            { month: 'Nov', sales: dashboardData?.sales_trend?.[4] || 90000 },
            { month: 'Dec', sales: dashboardData?.sales_trend?.[5] || 100000 },
          ]} />
          
          {/* Expense Category Pie */}
          <ExpenseCategoryPieChart data={[
            { name: 'Rent', value: dashboardData?.expense_by_category?.rent || 25000 },
            { name: 'Utilities', value: dashboardData?.expense_by_category?.utilities || 15000 },
            { name: 'Salaries', value: dashboardData?.expense_by_category?.salaries || 50000 },
            { name: 'Marketing', value: dashboardData?.expense_by_category?.marketing || 20000 },
            { name: 'Travel', value: dashboardData?.expense_by_category?.travel || 10000 },
            { name: 'Others', value: dashboardData?.expense_by_category?.others || 5000 },
          ]} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Payment Mode Distribution */}
          <PaymentModeChart data={[
            { mode: 'Cash', amount: dashboardData?.payment_mode?.cash || 30000 },
            { mode: 'Card', amount: dashboardData?.payment_mode?.card || 25000 },
            { mode: 'UPI', amount: dashboardData?.payment_mode?.upi || 35000 },
            { mode: 'NEFT', amount: dashboardData?.payment_mode?.neft || 15000 },
            { mode: 'Cheque', amount: dashboardData?.payment_mode?.cheque || 10000 },
          ]} />

          {/* Purchase vs Sales */}
          <PurchaseVsSalesChart data={[
            { month: 'Jul', purchases: 40000, sales: 50000 },
            { month: 'Aug', purchases: 55000, sales: 65000 },
            { month: 'Sep', purchases: 65000, sales: 80000 },
            { month: 'Oct', purchases: 60000, sales: 75000 },
            { month: 'Nov', purchases: 75000, sales: 90000 },
            { month: 'Dec', purchases: 80000, sales: 100000 },
          ]} />
        </div>

        {/* GST Summary */}
        <GSTSummaryChart data={[
          { month: 'Jul', cgst: 2500, sgst: 2500, igst: 1000 },
          { month: 'Aug', cgst: 3250, sgst: 3250, igst: 1500 },
          { month: 'Sep', cgst: 4000, sgst: 4000, igst: 2000 },
          { month: 'Oct', cgst: 3750, sgst: 3750, igst: 1800 },
          { month: 'Nov', cgst: 4500, sgst: 4500, igst: 2200 },
          { month: 'Dec', cgst: 5000, sgst: 5000, igst: 2500 },
        ]} />
      </div>
    </div>
  );

  const renderSalesReport = () => (
    <div className="space-y-4">
      {salesReport && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold mb-4">Sales Summary</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-gray-600">Total Sales</p>
              <p className="text-2xl font-bold">₹{salesReport.total_sales?.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-gray-600">Total Orders</p>
              <p className="text-2xl font-bold">{salesReport.total_orders}</p>
            </div>
            <div>
              <p className="text-gray-600">Online Sales</p>
              <p className="text-xl font-semibold text-green-600">₹{salesReport.online_sales?.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-gray-600">Offline Sales</p>
              <p className="text-xl font-semibold text-blue-600">₹{salesReport.offline_sales?.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-gray-600">Total Tax Collected</p>
              <p className="text-xl font-semibold">₹{salesReport.total_tax_collected?.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-gray-600">Average Order Value</p>
              <p className="text-xl font-semibold">₹{salesReport.average_order_value?.toFixed(2)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderPurchaseReport = () => (
    <div className="space-y-4">
      {purchaseReport && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold mb-4">Purchase Summary</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-gray-600">Total Purchases</p>
              <p className="text-2xl font-bold">₹{purchaseReport.total_purchases?.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-gray-600">Total Orders</p>
              <p className="text-2xl font-bold">{purchaseReport.total_orders}</p>
            </div>
            <div>
              <p className="text-gray-600">Tax Paid</p>
              <p className="text-xl font-semibold">₹{purchaseReport.total_tax_paid?.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-gray-600">Average Purchase Value</p>
              <p className="text-xl font-semibold">₹{purchaseReport.average_purchase_value?.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-gray-600">Pending Orders</p>
              <p className="text-xl font-semibold text-yellow-600">{purchaseReport.pending_orders}</p>
            </div>
            <div>
              <p className="text-gray-600">Completed Orders</p>
              <p className="text-xl font-semibold text-green-600">{purchaseReport.completed_orders}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderExpenseReport = () => (
    <div className="space-y-4">
      {expenseReport && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold mb-4">Expense Summary</h3>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <p className="text-gray-600">Total Expenses</p>
              <p className="text-2xl font-bold">₹{expenseReport.total_expenses?.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-gray-600">Total Entries</p>
              <p className="text-2xl font-bold">{expenseReport.total_entries}</p>
            </div>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Category-wise Breakdown</h4>
            <div className="space-y-2">
              {Object.entries(expenseReport.category_wise || {}).map(([category, amount]) => (
                <div key={category} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="font-medium">{category}</span>
                  <span className="font-bold">₹{amount.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderGSTReport = () => {
    const gstTabs = [
      { id: 'summary', name: 'Summary' },
      { id: 'gstr1', name: 'GSTR-1' },
      { id: 'gstr2b', name: 'GSTR-2B' },
      { id: 'gstr3b', name: 'GSTR-3B' },
      { id: 'gstr9', name: 'GSTR-9 (Annual)' },
      { id: 'tax-slabs', name: 'Tax Slabs' },
      { id: 'b2b-b2c', name: 'B2B/B2C Analysis' },
      { id: 'bifurcation', name: 'CGST/SGST/IGST' }
    ];

    return (
      <div className="space-y-4">
        {/* Period Selector */}
        <div className="bg-white rounded-lg shadow p-4 mb-4">
          <div className="flex flex-wrap gap-4 items-end">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Quick Period</label>
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="this_month">This Month</option>
                <option value="last_month">Last Month</option>
                <option value="this_quarter">This Quarter</option>
                <option value="last_quarter">Last Quarter</option>
                <option value="this_year">This Year</option>
                <option value="last_year">Last Year</option>
                <option value="custom">Custom Range</option>
              </select>
            </div>
            {selectedPeriod === 'custom' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">From</label>
                  <input
                    type="date"
                    value={dateRange.from_date}
                    onChange={(e) => setDateRange({ ...dateRange, from_date: e.target.value })}
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">To</label>
                  <input
                    type="date"
                    value={dateRange.to_date}
                    onChange={(e) => setDateRange({ ...dateRange, to_date: e.target.value })}
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </>
            )}
            {activeGstTab === 'gstr9' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Financial Year</label>
                <select
                  value={selectedFinancialYear}
                  onChange={(e) => setSelectedFinancialYear(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="2025-26">2025-26</option>
                  <option value="2024-25">2024-25</option>
                  <option value="2023-24">2023-24</option>
                </select>
              </div>
            )}
            <button
              onClick={fetchAllGstReports}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
            >
              <BarChart3 size={18} />
              Load All Reports
            </button>
          </div>
        </div>

        {/* GST Sub-tabs */}
        <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
          {gstTabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveGstTab(tab.id);
                if (tab.id === 'gstr1') fetchGSTReport('gstr1');
                else if (tab.id === 'gstr3b') fetchGSTReport('gstr3b');
                else if (tab.id === 'gstr2b') fetchGstr2bReport();
                else if (tab.id === 'gstr9') fetchGstr9Report();
                else if (tab.id === 'tax-slabs') fetchTaxSlabReport();
                else if (tab.id === 'b2b-b2c') fetchB2bB2cReport();
                else if (tab.id === 'bifurcation') fetchTaxBifurcationReport();
              }}
              className={`px-4 py-2 rounded-lg whitespace-nowrap text-sm font-medium transition-colors ${
                activeGstTab === tab.id
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {tab.name}
            </button>
          ))}
        </div>

        {/* GST Summary Tab */}
        {activeGstTab === 'summary' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-bold mb-4">GST Overview</h3>
            <p className="text-gray-600 mb-4">Click on any tab above to view detailed GST reports including GSTR-1, GSTR-2B, GSTR-3B, GSTR-9 (Annual), Tax Slabs, B2B/B2C Analysis, and CGST/SGST/IGST bifurcation.</p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <p className="text-sm text-green-700">GSTR-1</p>
                <p className="text-lg font-bold text-green-800">Outward Supplies</p>
                <p className="text-xs text-green-600 mt-1">Sales to customers</p>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <p className="text-sm text-blue-700">GSTR-2B</p>
                <p className="text-lg font-bold text-blue-800">Auto-drafted ITC</p>
                <p className="text-xs text-blue-600 mt-1">Input Tax Credit</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                <p className="text-sm text-purple-700">GSTR-3B</p>
                <p className="text-lg font-bold text-purple-800">Summary Return</p>
                <p className="text-xs text-purple-600 mt-1">Monthly filing</p>
              </div>
              <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                <p className="text-sm text-red-700">GSTR-9</p>
                <p className="text-lg font-bold text-red-800">Annual Return</p>
                <p className="text-xs text-red-600 mt-1">Yearly summary</p>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                <p className="text-sm text-orange-700">Tax Slabs</p>
                <p className="text-lg font-bold text-orange-800">0%, 5%, 12%, 18%, 28%</p>
                <p className="text-xs text-orange-600 mt-1">Slab-wise analysis</p>
              </div>
              <div className="bg-teal-50 p-4 rounded-lg border border-teal-200">
                <p className="text-sm text-teal-700">B2B/B2C</p>
                <p className="text-lg font-bold text-teal-800">Business Analysis</p>
                <p className="text-xs text-teal-600 mt-1">Customer type split</p>
              </div>
              <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-200">
                <p className="text-sm text-indigo-700">Bifurcation</p>
                <p className="text-lg font-bold text-indigo-800">CGST/SGST/IGST</p>
                <p className="text-xs text-indigo-600 mt-1">State-wise tax split</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <p className="text-sm text-gray-700">MSME/Udyam</p>
                <p className="text-lg font-bold text-gray-800">B2B Tracking</p>
                <p className="text-xs text-gray-600 mt-1">MSME registration</p>
              </div>
            </div>
          </div>
        )}

        {/* GSTR-1 Tab */}
        {activeGstTab === 'gstr1' && gstReport && gstReport.report_type === 'GSTR-1' && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">GSTR-1 - Outward Supplies</h3>
              <button
                onClick={downloadGstr1Excel}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
              >
                <Download size={18} />
                Download Excel (Govt. Format)
              </button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">Total Outward Supplies</p>
                <p className="text-2xl font-bold text-green-700">₹{(gstReport.summary?.total_outward_supplies || 0).toLocaleString('en-IN')}</p>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">Total Tax</p>
                <p className="text-2xl font-bold text-blue-700">₹{(gstReport.summary?.total_tax || 0).toLocaleString('en-IN')}</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">CGST</p>
                <p className="text-xl font-semibold text-purple-700">₹{(gstReport.summary?.cgst || 0).toLocaleString('en-IN')}</p>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">SGST</p>
                <p className="text-xl font-semibold text-orange-700">₹{(gstReport.summary?.sgst || 0).toLocaleString('en-IN')}</p>
              </div>
            </div>
            {gstReport.hsn_summary && gstReport.hsn_summary.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2">HSN-wise Summary</h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">HSN Code</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Quantity</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Taxable Value</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Tax Amount</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {gstReport.hsn_summary.map((item, index) => (
                        <tr key={index}>
                          <td className="px-4 py-2 text-sm font-mono">{item.hsn_code}</td>
                          <td className="px-4 py-2 text-sm text-right">{item.quantity}</td>
                          <td className="px-4 py-2 text-sm text-right">₹{(item.taxable_value || 0).toLocaleString('en-IN')}</td>
                          <td className="px-4 py-2 text-sm text-right">₹{(item.tax_amount || 0).toLocaleString('en-IN')}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* GSTR-2B Tab */}
        {activeGstTab === 'gstr2b' && gstr2bReport && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">GSTR-2B - Auto-drafted ITC Statement</h3>
              <button
                onClick={downloadGstr2bExcel}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
              >
                <Download size={18} />
                Download Excel (Govt. Format)
              </button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">Total Suppliers</p>
                <p className="text-2xl font-bold text-blue-700">{gstr2bReport.b2b_supplies?.summary?.supplier_count || 0}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">Total Invoices</p>
                <p className="text-2xl font-bold text-green-700">{gstr2bReport.b2b_supplies?.summary?.invoice_count || 0}</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">Taxable Value</p>
                <p className="text-xl font-semibold text-purple-700">₹{(gstr2bReport.b2b_supplies?.summary?.total_taxable_value || 0).toLocaleString('en-IN')}</p>
              </div>
              <div className="bg-teal-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">Total ITC Available</p>
                <p className="text-xl font-semibold text-teal-700">₹{(gstr2bReport.itc_summary?.available_itc?.total || 0).toLocaleString('en-IN')}</p>
              </div>
            </div>

            {/* ITC Breakdown */}
            <div className="bg-gray-50 p-4 rounded-lg mb-6">
              <h4 className="font-semibold mb-3">Input Tax Credit Breakdown</h4>
              <div className="grid grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-sm text-gray-600">CGST</p>
                  <p className="text-lg font-bold text-indigo-600">₹{(gstr2bReport.itc_summary?.available_itc?.cgst || 0).toLocaleString('en-IN')}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">SGST</p>
                  <p className="text-lg font-bold text-purple-600">₹{(gstr2bReport.itc_summary?.available_itc?.sgst || 0).toLocaleString('en-IN')}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">IGST</p>
                  <p className="text-lg font-bold text-orange-600">₹{(gstr2bReport.itc_summary?.available_itc?.igst || 0).toLocaleString('en-IN')}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">Net ITC</p>
                  <p className="text-lg font-bold text-green-600">₹{(gstr2bReport.itc_summary?.net_itc?.total || 0).toLocaleString('en-IN')}</p>
                </div>
              </div>
            </div>

            {/* Supplier-wise Details */}
            {gstr2bReport.b2b_supplies?.details?.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2">Supplier-wise ITC (with MSME/Udyam)</h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">GSTIN</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Supplier</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">MSME/Udyam</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Invoices</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Taxable Value</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">ITC Amount</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {gstr2bReport.b2b_supplies.details.map((supplier, index) => (
                        <tr key={index}>
                          <td className="px-4 py-2 text-sm font-mono">{supplier.gstin}</td>
                          <td className="px-4 py-2 text-sm">{supplier.supplier_name}</td>
                          <td className="px-4 py-2 text-sm text-blue-600">{supplier.msme_udyam_number || '-'}</td>
                          <td className="px-4 py-2 text-sm text-right">{supplier.invoice_count}</td>
                          <td className="px-4 py-2 text-sm text-right">₹{(supplier.taxable_value || 0).toLocaleString('en-IN')}</td>
                          <td className="px-4 py-2 text-sm text-right font-semibold text-green-600">₹{(supplier.total_itc || 0).toLocaleString('en-IN')}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* GSTR-3B Tab */}
        {activeGstTab === 'gstr3b' && gstReport && gstReport.report_type === 'GSTR-3B' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-bold mb-4">GSTR-3B - Summary Return</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                <p className="text-gray-600 text-sm">Output Tax</p>
                <p className="text-2xl font-bold text-red-700">₹{(gstReport.tax_liability?.output_tax || 0).toLocaleString('en-IN')}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <p className="text-gray-600 text-sm">Input Tax Credit</p>
                <p className="text-2xl font-bold text-green-700">₹{(gstReport.tax_liability?.input_tax_credit || 0).toLocaleString('en-IN')}</p>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                <p className="text-gray-600 text-sm">Net Tax Payable</p>
                <p className="text-2xl font-bold text-orange-700">₹{(gstReport.tax_liability?.net_tax_payable || 0).toLocaleString('en-IN')}</p>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <p className="text-gray-600 text-sm">Total Purchases</p>
                <p className="text-xl font-semibold text-blue-700">₹{(gstReport.inward_supplies?.total_purchases || 0).toLocaleString('en-IN')}</p>
              </div>
            </div>
          </div>
        )}

        {/* GSTR-9 Annual Return Tab */}
        {activeGstTab === 'gstr9' && gstr9Report && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h3 className="text-xl font-bold">GSTR-9 - Annual Return</h3>
                <p className="text-gray-600 text-sm">Financial Year: {gstr9Report.financial_year}</p>
              </div>
              <button
                onClick={downloadGstr9Excel}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
              >
                <Download size={18} />
                Download Excel (Govt. Format)
              </button>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <p className="text-gray-600 text-sm">Total Turnover</p>
                <p className="text-xl font-bold text-green-700">₹{(gstr9Report.summary?.total_turnover || 0).toLocaleString('en-IN')}</p>
              </div>
              <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                <p className="text-gray-600 text-sm">Total Tax Collected</p>
                <p className="text-xl font-bold text-red-700">₹{(gstr9Report.summary?.total_tax_collected || 0).toLocaleString('en-IN')}</p>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <p className="text-gray-600 text-sm">Total ITC Claimed</p>
                <p className="text-xl font-bold text-blue-700">₹{(gstr9Report.summary?.total_itc_claimed || 0).toLocaleString('en-IN')}</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                <p className="text-gray-600 text-sm">Net Tax Paid</p>
                <p className="text-xl font-bold text-purple-700">₹{(gstr9Report.summary?.net_tax_paid || 0).toLocaleString('en-IN')}</p>
              </div>
            </div>

            {/* Part II - Outward Supplies */}
            <div className="mb-6">
              <h4 className="font-semibold mb-3 text-green-700 border-b pb-2">Part II - Outward Supplies</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-green-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Description</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Taxable Value</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">CGST</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">SGST</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">IGST</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Invoices</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    <tr>
                      <td className="px-4 py-2 text-sm">B2B Supplies (Registered)</td>
                      <td className="px-4 py-2 text-sm text-right">₹{(gstr9Report.part_ii_outward_supplies?.b2b?.taxable_value || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right">₹{(gstr9Report.part_ii_outward_supplies?.b2b?.cgst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right">₹{(gstr9Report.part_ii_outward_supplies?.b2b?.sgst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right">₹{(gstr9Report.part_ii_outward_supplies?.b2b?.igst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right">{gstr9Report.part_ii_outward_supplies?.b2b?.invoice_count || 0}</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-2 text-sm">B2C Supplies (Unregistered)</td>
                      <td className="px-4 py-2 text-sm text-right">₹{(gstr9Report.part_ii_outward_supplies?.b2c?.taxable_value || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right">₹{(gstr9Report.part_ii_outward_supplies?.b2c?.cgst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right">₹{(gstr9Report.part_ii_outward_supplies?.b2c?.sgst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right">₹{(gstr9Report.part_ii_outward_supplies?.b2c?.igst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right">{gstr9Report.part_ii_outward_supplies?.b2c?.invoice_count || 0}</td>
                    </tr>
                    <tr className="bg-green-50 font-semibold">
                      <td className="px-4 py-2 text-sm">Total Outward Supplies</td>
                      <td className="px-4 py-2 text-sm text-right">₹{(gstr9Report.part_ii_outward_supplies?.total?.taxable_value || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right">₹{(gstr9Report.part_ii_outward_supplies?.total?.cgst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right">₹{(gstr9Report.part_ii_outward_supplies?.total?.sgst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right">₹{(gstr9Report.part_ii_outward_supplies?.total?.igst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right">{gstr9Report.part_ii_outward_supplies?.total?.invoice_count || 0}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Part III - ITC */}
            <div className="mb-6">
              <h4 className="font-semibold mb-3 text-blue-700 border-b pb-2">Part III - Input Tax Credit</h4>
              <div className="grid grid-cols-4 gap-4 bg-blue-50 p-4 rounded-lg">
                <div className="text-center">
                  <p className="text-sm text-gray-600">CGST ITC</p>
                  <p className="text-xl font-bold text-blue-700">₹{(gstr9Report.part_iii_inward_supplies?.itc_claimed?.cgst || 0).toLocaleString('en-IN')}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">SGST ITC</p>
                  <p className="text-xl font-bold text-blue-700">₹{(gstr9Report.part_iii_inward_supplies?.itc_claimed?.sgst || 0).toLocaleString('en-IN')}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">IGST ITC</p>
                  <p className="text-xl font-bold text-blue-700">₹{(gstr9Report.part_iii_inward_supplies?.itc_claimed?.igst || 0).toLocaleString('en-IN')}</p>
                </div>
                <div className="text-center bg-white rounded p-2">
                  <p className="text-sm text-gray-600">Total ITC</p>
                  <p className="text-xl font-bold text-green-700">₹{(gstr9Report.part_iii_inward_supplies?.itc_claimed?.total || 0).toLocaleString('en-IN')}</p>
                </div>
              </div>
            </div>

            {/* Part IV - Tax Paid */}
            <div className="mb-6">
              <h4 className="font-semibold mb-3 text-purple-700 border-b pb-2">Part IV - Tax Paid</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-purple-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Description</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">CGST</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">SGST</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">IGST</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Total</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    <tr>
                      <td className="px-4 py-2 text-sm">Output Tax Liability</td>
                      <td className="px-4 py-2 text-sm text-right text-red-600">₹{(gstr9Report.part_iv_tax_paid?.output_tax?.cgst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right text-red-600">₹{(gstr9Report.part_iv_tax_paid?.output_tax?.sgst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right text-red-600">₹{(gstr9Report.part_iv_tax_paid?.output_tax?.igst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right text-red-600 font-semibold">₹{(gstr9Report.part_iv_tax_paid?.output_tax?.total || 0).toLocaleString('en-IN')}</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-2 text-sm">ITC Utilized</td>
                      <td className="px-4 py-2 text-sm text-right text-green-600">₹{(gstr9Report.part_iv_tax_paid?.itc_utilized?.cgst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right text-green-600">₹{(gstr9Report.part_iv_tax_paid?.itc_utilized?.sgst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right text-green-600">₹{(gstr9Report.part_iv_tax_paid?.itc_utilized?.igst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right text-green-600 font-semibold">₹{(gstr9Report.part_iv_tax_paid?.itc_utilized?.total || 0).toLocaleString('en-IN')}</td>
                    </tr>
                    <tr className="bg-purple-50 font-semibold">
                      <td className="px-4 py-2 text-sm">Net Tax Payable</td>
                      <td className="px-4 py-2 text-sm text-right">₹{(gstr9Report.part_iv_tax_paid?.net_tax_liability?.cgst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right">₹{(gstr9Report.part_iv_tax_paid?.net_tax_liability?.sgst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right">₹{(gstr9Report.part_iv_tax_paid?.net_tax_liability?.igst || 0).toLocaleString('en-IN')}</td>
                      <td className="px-4 py-2 text-sm text-right text-purple-700">₹{(gstr9Report.part_iv_tax_paid?.net_tax_liability?.total || 0).toLocaleString('en-IN')}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Part V - Monthly Breakup */}
            <div>
              <h4 className="font-semibold mb-3 text-indigo-700 border-b pb-2">Part V - Monthly Breakup</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-indigo-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Month</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Outward Supplies</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Output Tax</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {(gstr9Report.part_v_monthly_breakup || []).map((month, index) => (
                      <tr key={index}>
                        <td className="px-4 py-2 text-sm">{month.month}</td>
                        <td className="px-4 py-2 text-sm text-right">₹{(month.outward_supplies || 0).toLocaleString('en-IN')}</td>
                        <td className="px-4 py-2 text-sm text-right">₹{(month.output_tax || 0).toLocaleString('en-IN')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Tax Slabs Tab */}
        {activeGstTab === 'tax-slabs' && taxSlabReport && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-bold mb-4">Tax Slab Analysis (0%, 5%, 12%, 18%, 28%)</h3>
            
            {/* Sales by Tax Slab */}
            <div className="mb-6">
              <h4 className="font-semibold mb-3 text-green-700">Sales by Tax Slab</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-green-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Tax Slab</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Taxable Value</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">CGST</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">SGST</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Total Tax</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {Object.entries(taxSlabReport.sales_by_tax_slab || {}).map(([slab, data]) => (
                      <tr key={slab}>
                        <td className="px-4 py-2 text-sm font-semibold">{slab}</td>
                        <td className="px-4 py-2 text-sm text-right">₹{(data.taxable_value || 0).toLocaleString('en-IN')}</td>
                        <td className="px-4 py-2 text-sm text-right">₹{(data.cgst || 0).toLocaleString('en-IN')}</td>
                        <td className="px-4 py-2 text-sm text-right">₹{(data.sgst || 0).toLocaleString('en-IN')}</td>
                        <td className="px-4 py-2 text-sm text-right font-semibold">₹{(data.total_tax || 0).toLocaleString('en-IN')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Purchases by Tax Slab */}
            <div className="mb-6">
              <h4 className="font-semibold mb-3 text-blue-700">Purchases by Tax Slab (ITC)</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-blue-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Tax Slab</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Taxable Value</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">CGST ITC</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">SGST ITC</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Total ITC</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {Object.entries(taxSlabReport.purchases_by_tax_slab || {}).map(([slab, data]) => (
                      <tr key={slab}>
                        <td className="px-4 py-2 text-sm font-semibold">{slab}</td>
                        <td className="px-4 py-2 text-sm text-right">₹{(data.taxable_value || 0).toLocaleString('en-IN')}</td>
                        <td className="px-4 py-2 text-sm text-right">₹{(data.cgst || 0).toLocaleString('en-IN')}</td>
                        <td className="px-4 py-2 text-sm text-right">₹{(data.sgst || 0).toLocaleString('en-IN')}</td>
                        <td className="px-4 py-2 text-sm text-right font-semibold text-green-600">₹{(data.total_itc || 0).toLocaleString('en-IN')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Net Tax by Slab */}
            <div>
              <h4 className="font-semibold mb-3 text-purple-700">Net Tax Payable by Slab</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-purple-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Tax Slab</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Output Tax</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Input Tax Credit</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Net Payable</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {Object.entries(taxSlabReport.net_tax_by_slab || {}).map(([slab, data]) => (
                      <tr key={slab}>
                        <td className="px-4 py-2 text-sm font-semibold">{slab}</td>
                        <td className="px-4 py-2 text-sm text-right text-red-600">₹{(data.output_tax || 0).toLocaleString('en-IN')}</td>
                        <td className="px-4 py-2 text-sm text-right text-green-600">₹{(data.input_tax_credit || 0).toLocaleString('en-IN')}</td>
                        <td className="px-4 py-2 text-sm text-right font-semibold">₹{(data.net_payable || 0).toLocaleString('en-IN')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* B2B/B2C Analysis Tab */}
        {activeGstTab === 'b2b-b2c' && b2bB2cReport && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-bold mb-4">B2B vs B2C Analysis</h3>
            
            {/* Sales Analysis */}
            <div className="mb-8">
              <h4 className="font-semibold mb-3 text-green-700 flex items-center gap-2">
                <TrendingUp size={20} />
                Sales Analysis
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                {/* B2B Sales */}
                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-semibold text-green-800">B2B Sales (with GSTIN)</p>
                      <p className="text-xs text-green-600">{b2bB2cReport.sales?.b2b?.description}</p>
                    </div>
                    <span className="bg-green-200 text-green-800 text-xs px-2 py-1 rounded">{b2bB2cReport.sales?.b2b?.invoice_count || 0} invoices</span>
                  </div>
                  <p className="text-2xl font-bold text-green-700">₹{(b2bB2cReport.sales?.b2b?.total_value || 0).toLocaleString('en-IN')}</p>
                  <div className="grid grid-cols-3 gap-2 mt-2 text-xs">
                    <div><span className="text-gray-600">CGST:</span> ₹{(b2bB2cReport.sales?.b2b?.cgst || 0).toLocaleString('en-IN')}</div>
                    <div><span className="text-gray-600">SGST:</span> ₹{(b2bB2cReport.sales?.b2b?.sgst || 0).toLocaleString('en-IN')}</div>
                    <div><span className="text-gray-600">IGST:</span> ₹{(b2bB2cReport.sales?.b2b?.igst || 0).toLocaleString('en-IN')}</div>
                  </div>
                </div>
                
                {/* B2C Sales */}
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-semibold text-blue-800">B2C Sales (without GSTIN)</p>
                      <p className="text-xs text-blue-600">{b2bB2cReport.sales?.b2c?.description}</p>
                    </div>
                    <span className="bg-blue-200 text-blue-800 text-xs px-2 py-1 rounded">{b2bB2cReport.sales?.b2c?.summary?.invoice_count || 0} invoices</span>
                  </div>
                  <p className="text-2xl font-bold text-blue-700">₹{(b2bB2cReport.sales?.b2c?.summary?.total_value || 0).toLocaleString('en-IN')}</p>
                  <div className="grid grid-cols-3 gap-2 mt-2 text-xs">
                    <div><span className="text-gray-600">CGST:</span> ₹{(b2bB2cReport.sales?.b2c?.summary?.cgst || 0).toLocaleString('en-IN')}</div>
                    <div><span className="text-gray-600">SGST:</span> ₹{(b2bB2cReport.sales?.b2c?.summary?.sgst || 0).toLocaleString('en-IN')}</div>
                    <div><span className="text-gray-600">IGST:</span> ₹{(b2bB2cReport.sales?.b2c?.summary?.igst || 0).toLocaleString('en-IN')}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Purchase Analysis */}
            <div className="mb-8">
              <h4 className="font-semibold mb-3 text-orange-700 flex items-center gap-2">
                <ShoppingCart size={20} />
                Purchase Analysis
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* B2B Purchases */}
                <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-semibold text-orange-800">B2B Purchases (ITC Eligible)</p>
                      <p className="text-xs text-orange-600">{b2bB2cReport.purchases?.b2b?.description}</p>
                    </div>
                    <span className="bg-orange-200 text-orange-800 text-xs px-2 py-1 rounded">{b2bB2cReport.purchases?.b2b?.bill_count || 0} bills</span>
                  </div>
                  <p className="text-2xl font-bold text-orange-700">₹{(b2bB2cReport.purchases?.b2b?.total_value || 0).toLocaleString('en-IN')}</p>
                  <p className="text-sm text-green-600 mt-1">ITC Available: ₹{(b2bB2cReport.purchases?.b2b?.itc_available || 0).toLocaleString('en-IN')}</p>
                </div>
                
                {/* Unregistered Purchases */}
                <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-semibold text-gray-800">Unregistered Vendors (No ITC)</p>
                      <p className="text-xs text-gray-600">{b2bB2cReport.purchases?.unregistered?.description}</p>
                    </div>
                    <span className="bg-gray-200 text-gray-800 text-xs px-2 py-1 rounded">{b2bB2cReport.purchases?.unregistered?.bill_count || 0} bills</span>
                  </div>
                  <p className="text-2xl font-bold text-gray-700">₹{(b2bB2cReport.purchases?.unregistered?.total_value || 0).toLocaleString('en-IN')}</p>
                </div>
              </div>
            </div>

            {/* GST Summary */}
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-4 rounded-lg border border-indigo-200">
              <h4 className="font-semibold mb-3 text-indigo-700">GST Summary</h4>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Output Tax</p>
                  <p className="text-xl font-bold text-red-600">₹{(b2bB2cReport.gst_summary?.output_tax?.total || 0).toLocaleString('en-IN')}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Input Tax Credit</p>
                  <p className="text-xl font-bold text-green-600">₹{(b2bB2cReport.gst_summary?.input_tax_credit?.total || 0).toLocaleString('en-IN')}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Net Payable</p>
                  <p className="text-xl font-bold text-indigo-700">₹{(b2bB2cReport.gst_summary?.net_payable?.total || 0).toLocaleString('en-IN')}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tax Bifurcation Tab (CGST/SGST/IGST) */}
        {activeGstTab === 'bifurcation' && taxBifurcationReport && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-bold mb-2">Tax Bifurcation - CGST / SGST / IGST</h3>
            <p className="text-gray-600 text-sm mb-4">Business State: <span className="font-semibold">{taxBifurcationReport.business_state}</span></p>
            
            {/* Sales Bifurcation */}
            <div className="mb-8">
              <h4 className="font-semibold mb-3 text-green-700">Sales Tax Bifurcation</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Intra-state */}
                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                  <p className="font-semibold text-green-800 mb-1">Intra-State Sales (CGST + SGST)</p>
                  <p className="text-xs text-green-600 mb-2">{taxBifurcationReport.sales?.intra_state?.description}</p>
                  <p className="text-xl font-bold text-green-700 mb-2">₹{(taxBifurcationReport.sales?.intra_state?.total_value || 0).toLocaleString('en-IN')}</p>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="bg-white p-2 rounded">
                      <span className="text-gray-600">CGST:</span>
                      <span className="font-semibold ml-1">₹{(taxBifurcationReport.sales?.intra_state?.cgst || 0).toLocaleString('en-IN')}</span>
                    </div>
                    <div className="bg-white p-2 rounded">
                      <span className="text-gray-600">SGST:</span>
                      <span className="font-semibold ml-1">₹{(taxBifurcationReport.sales?.intra_state?.sgst || 0).toLocaleString('en-IN')}</span>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">{taxBifurcationReport.sales?.intra_state?.invoice_count || 0} invoices</p>
                </div>
                
                {/* Inter-state */}
                <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                  <p className="font-semibold text-orange-800 mb-1">Inter-State Sales (IGST)</p>
                  <p className="text-xs text-orange-600 mb-2">{taxBifurcationReport.sales?.inter_state?.description}</p>
                  <p className="text-xl font-bold text-orange-700 mb-2">₹{(taxBifurcationReport.sales?.inter_state?.summary?.total_value || 0).toLocaleString('en-IN')}</p>
                  <div className="bg-white p-2 rounded text-sm">
                    <span className="text-gray-600">IGST:</span>
                    <span className="font-semibold ml-1">₹{(taxBifurcationReport.sales?.inter_state?.summary?.igst || 0).toLocaleString('en-IN')}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">{taxBifurcationReport.sales?.inter_state?.summary?.invoice_count || 0} invoices</p>
                </div>
              </div>
            </div>

            {/* Purchase Bifurcation */}
            <div className="mb-8">
              <h4 className="font-semibold mb-3 text-blue-700">Purchase ITC Bifurcation</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Intra-state */}
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <p className="font-semibold text-blue-800 mb-1">Intra-State Purchases (CGST + SGST ITC)</p>
                  <p className="text-xs text-blue-600 mb-2">{taxBifurcationReport.purchases?.intra_state?.description}</p>
                  <p className="text-xl font-bold text-blue-700 mb-2">₹{(taxBifurcationReport.purchases?.intra_state?.total_value || 0).toLocaleString('en-IN')}</p>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="bg-white p-2 rounded">
                      <span className="text-gray-600">CGST ITC:</span>
                      <span className="font-semibold ml-1 text-green-600">₹{(taxBifurcationReport.purchases?.intra_state?.cgst_itc || 0).toLocaleString('en-IN')}</span>
                    </div>
                    <div className="bg-white p-2 rounded">
                      <span className="text-gray-600">SGST ITC:</span>
                      <span className="font-semibold ml-1 text-green-600">₹{(taxBifurcationReport.purchases?.intra_state?.sgst_itc || 0).toLocaleString('en-IN')}</span>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">{taxBifurcationReport.purchases?.intra_state?.bill_count || 0} bills</p>
                </div>
                
                {/* Inter-state */}
                <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                  <p className="font-semibold text-purple-800 mb-1">Inter-State Purchases (IGST ITC)</p>
                  <p className="text-xs text-purple-600 mb-2">{taxBifurcationReport.purchases?.inter_state?.description}</p>
                  <p className="text-xl font-bold text-purple-700 mb-2">₹{(taxBifurcationReport.purchases?.inter_state?.summary?.total_value || 0).toLocaleString('en-IN')}</p>
                  <div className="bg-white p-2 rounded text-sm">
                    <span className="text-gray-600">IGST ITC:</span>
                    <span className="font-semibold ml-1 text-green-600">₹{(taxBifurcationReport.purchases?.inter_state?.summary?.igst_itc || 0).toLocaleString('en-IN')}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">{taxBifurcationReport.purchases?.inter_state?.summary?.bill_count || 0} bills</p>
                </div>
              </div>
            </div>

            {/* Final Tax Summary */}
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 rounded-lg text-white">
              <h4 className="font-semibold mb-4 text-lg">Net Tax Liability Summary</h4>
              <div className="grid grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-indigo-200 text-sm">CGST Payable</p>
                  <p className="text-2xl font-bold">₹{(taxBifurcationReport.tax_summary?.net_payable?.cgst || 0).toLocaleString('en-IN')}</p>
                </div>
                <div className="text-center">
                  <p className="text-indigo-200 text-sm">SGST Payable</p>
                  <p className="text-2xl font-bold">₹{(taxBifurcationReport.tax_summary?.net_payable?.sgst || 0).toLocaleString('en-IN')}</p>
                </div>
                <div className="text-center">
                  <p className="text-indigo-200 text-sm">IGST Payable</p>
                  <p className="text-2xl font-bold">₹{(taxBifurcationReport.tax_summary?.net_payable?.igst || 0).toLocaleString('en-IN')}</p>
                </div>
                <div className="text-center bg-white/20 rounded-lg p-2">
                  <p className="text-indigo-200 text-sm">Total Net Payable</p>
                  <p className="text-3xl font-bold">₹{(taxBifurcationReport.tax_summary?.net_payable?.total || 0).toLocaleString('en-IN')}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Legacy GSTR-1/3B buttons removed - handled by tabs now */}
      </div>
    );
  };

  const renderPaymentReceiptReport = () => (
    <div className="space-y-4">
      {paymentReceiptReport && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold mb-4">Payment & Receipt Summary</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-gray-600">Total Payments</p>
              <p className="text-2xl font-bold text-red-600">₹{paymentReceiptReport.total_payments?.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-gray-600">Total Receipts</p>
              <p className="text-2xl font-bold text-green-600">₹{paymentReceiptReport.total_receipts?.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-gray-600">Payment Count</p>
              <p className="text-xl font-semibold">{paymentReceiptReport.payment_count}</p>
            </div>
            <div>
              <p className="text-gray-600">Receipt Count</p>
              <p className="text-xl font-semibold">{paymentReceiptReport.receipt_count}</p>
            </div>
            <div className="col-span-2">
              <p className="text-gray-600">Net Cash Flow</p>
              <p className={`text-3xl font-bold ${
                paymentReceiptReport.net_cash_flow >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                ₹{paymentReceiptReport.net_cash_flow?.toFixed(2)}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const [exportLoading, setExportLoading] = useState(false);
  const [exportDateRange, setExportDateRange] = useState({
    from_date: '2025-04-01',
    to_date: '2025-04-30'
  });

  const handleDataExport = async (dataType, format) => {
    setExportLoading(true);
    try {
      const endpoint = dataType === 'sales' 
        ? `${BACKEND_URL}/api/financial-reports/export/sales-data`
        : `${BACKEND_URL}/api/financial-reports/export/purchase-data`;
      
      const url = `${endpoint}?from_date=${exportDateRange.from_date}&to_date=${exportDateRange.to_date}&format=${format}`;
      
      const response = await fetch(url);
      
      if (response.ok) {
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `${dataType === 'sales' ? 'Sales' : 'Purchase'}_Data_${exportDateRange.from_date}_to_${exportDateRange.to_date}.${format === 'excel' ? 'xlsx' : 'csv'}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);
      } else {
        alert('Export failed. Please try again.');
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('Export failed. Please try again.');
    }
    setExportLoading(false);
  };

  const renderDataExport = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <FileSpreadsheet className="text-teal-500" />
          Export Sales & Purchase Data
        </h2>
        <p className="text-gray-600 mb-6">
          Download raw sales and purchase data with GST breakup for any date range. 
          Useful for accounting, audit, and GST filing purposes.
        </p>
        
        {/* Date Range Selection */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h3 className="font-medium text-gray-800 mb-3">Select Date Range</h3>
          <div className="flex flex-wrap gap-4 items-end">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">From Date</label>
              <input
                type="date"
                value={exportDateRange.from_date}
                onChange={(e) => setExportDateRange({ ...exportDateRange, from_date: e.target.value })}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">To Date</label>
              <input
                type="date"
                value={exportDateRange.to_date}
                onChange={(e) => setExportDateRange({ ...exportDateRange, to_date: e.target.value })}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
              />
            </div>
            
            {/* Quick Period Selection */}
            <div className="flex gap-2">
              <button
                onClick={() => {
                  const now = new Date();
                  const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
                  setExportDateRange({
                    from_date: firstDay.toISOString().split('T')[0],
                    to_date: now.toISOString().split('T')[0]
                  });
                }}
                className="px-3 py-2 text-sm bg-gray-200 rounded-lg hover:bg-gray-300"
              >
                This Month
              </button>
              <button
                onClick={() => {
                  const now = new Date();
                  const firstDay = new Date(now.getFullYear(), now.getMonth() - 1, 1);
                  const lastDay = new Date(now.getFullYear(), now.getMonth(), 0);
                  setExportDateRange({
                    from_date: firstDay.toISOString().split('T')[0],
                    to_date: lastDay.toISOString().split('T')[0]
                  });
                }}
                className="px-3 py-2 text-sm bg-gray-200 rounded-lg hover:bg-gray-300"
              >
                Last Month
              </button>
              <button
                onClick={() => {
                  const now = new Date();
                  // Financial year starts April 1
                  const fyStart = now.getMonth() >= 3 
                    ? new Date(now.getFullYear(), 3, 1)
                    : new Date(now.getFullYear() - 1, 3, 1);
                  setExportDateRange({
                    from_date: fyStart.toISOString().split('T')[0],
                    to_date: now.toISOString().split('T')[0]
                  });
                }}
                className="px-3 py-2 text-sm bg-gray-200 rounded-lg hover:bg-gray-300"
              >
                This FY
              </button>
            </div>
          </div>
        </div>
        
        {/* Export Options */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Sales Data Export */}
          <div className="border border-green-200 rounded-lg p-5 bg-green-50">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-3 bg-green-500 text-white rounded-lg">
                <TrendingUp size={24} />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Sales Data</h3>
                <p className="text-sm text-gray-600">Invoice-wise sales with GST breakup</p>
              </div>
            </div>
            <ul className="text-sm text-gray-600 mb-4 space-y-1">
              <li>• Invoice Number, Date, Customer Details</li>
              <li>• Product Name, HSN Code, Quantity</li>
              <li>• Taxable Amount, CGST, SGST, IGST</li>
              <li>• Payment Status, Order Status</li>
            </ul>
            <div className="flex gap-2">
              <button
                onClick={() => handleDataExport('sales', 'excel')}
                disabled={exportLoading}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
              >
                <Download size={16} />
                {exportLoading ? 'Exporting...' : 'Download Excel'}
              </button>
              <button
                onClick={() => handleDataExport('sales', 'csv')}
                disabled={exportLoading}
                className="px-4 py-2 border border-green-600 text-green-600 rounded-lg hover:bg-green-50"
              >
                CSV
              </button>
            </div>
          </div>
          
          {/* Purchase Data Export */}
          <div className="border border-blue-200 rounded-lg p-5 bg-blue-50">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-3 bg-blue-500 text-white rounded-lg">
                <ShoppingCart size={24} />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Purchase Data</h3>
                <p className="text-sm text-gray-600">Bill-wise purchases for ITC claim</p>
              </div>
            </div>
            <ul className="text-sm text-gray-600 mb-4 space-y-1">
              <li>• Bill Number, Date, Vendor Details</li>
              <li>• Vendor GSTIN, MSME Number</li>
              <li>• Product Name, HSN Code, Quantity</li>
              <li>• Taxable Amount, CGST, SGST, IGST</li>
              <li>• ITC Summary at the end</li>
            </ul>
            <div className="flex gap-2">
              <button
                onClick={() => handleDataExport('purchase', 'excel')}
                disabled={exportLoading}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
              >
                <Download size={16} />
                {exportLoading ? 'Exporting...' : 'Download Excel'}
              </button>
              <button
                onClick={() => handleDataExport('purchase', 'csv')}
                disabled={exportLoading}
                className="px-4 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50"
              >
                CSV
              </button>
            </div>
          </div>
        </div>
        
        {/* Info Note */}
        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            <strong>Note:</strong> Excel exports include formatted headers, GST summary totals, and are ready for accounting software import. 
            CSV format is useful for custom analysis in spreadsheet applications.
          </p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <BarChart3 className="text-teal-500" />
          Accounting Reports
        </h1>
        <p className="text-gray-600 mt-1">Sales, purchase, GST, and financial reports</p>
      </div>

      {/* Date Range Selector */}
      {activeReport !== 'dashboard' && (
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex gap-4 items-end">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">From Date</label>
              <input
                type="date"
                value={dateRange.from_date}
                onChange={(e) => setDateRange({ ...dateRange, from_date: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">To Date</label>
              <input
                type="date"
                value={dateRange.to_date}
                onChange={(e) => setDateRange({ ...dateRange, to_date: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <button
              onClick={() => {
                if (activeReport === 'sales') fetchSalesReport();
                else if (activeReport === 'purchase') fetchPurchaseReport();
                else if (activeReport === 'expense') fetchExpenseReport();
                else if (activeReport === 'payments') fetchPaymentReceiptReport();
              }}
              className="px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600"
            >
              Generate Report
            </button>
          </div>
        </div>
      )}

      {/* Report Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto">
        {reportTabs.map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveReport(tab.id)}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 whitespace-nowrap ${
                activeReport === tab.id
                  ? 'bg-teal-500 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              <Icon size={18} />
              {tab.name}
            </button>
          );
        })}
      </div>

      {/* Report Content */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
        </div>
      ) : (
        <div>
          {activeReport === 'dashboard' && renderDashboard()}
          {activeReport === 'sales' && renderSalesReport()}
          {activeReport === 'purchase' && renderPurchaseReport()}
          {activeReport === 'expense' && renderExpenseReport()}
          {activeReport === 'gst' && renderGSTReport()}
          {activeReport === 'payments' && renderPaymentReceiptReport()}
          {activeReport === 'data_export' && renderDataExport()}
        </div>
      )}
    </div>
  );
};

export default AccountingReports;