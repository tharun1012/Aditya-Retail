import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  FileText, Download, Calendar, TrendingUp, TrendingDown,
  DollarSign, PieChart, BarChart3, ArrowUpRight, ArrowDownRight,
  RefreshCw, ChevronDown, Building2, Users, Package, AlertTriangle,
  CheckCircle, IndianRupee, Filter, Printer
} from 'lucide-react';
import { showToast } from '../utils/toast';


const FinancialReports = () => {
  const [activeReport, setActiveReport] = useState('dashboard');
  const [period, setPeriod] = useState('this_month');
  const [loading, setLoading] = useState(false);
  const [reportData, setReportData] = useState(null);
  const [customDates, setCustomDates] = useState({ from: '', to: '' });

  const reportTypes = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3, color: 'bg-blue-500' },
    { id: 'profit-loss', label: 'Profit & Loss', icon: TrendingUp, color: 'bg-green-500' },
    { id: 'balance-sheet', label: 'Balance Sheet', icon: Building2, color: 'bg-purple-500' },
    { id: 'cash-flow', label: 'Cash Flow', icon: DollarSign, color: 'bg-cyan-500' },
    { id: 'gst-summary', label: 'GST Summary', icon: FileText, color: 'bg-orange-500' },
    { id: 'hsn-wise', label: 'HSN-wise Report', icon: Package, color: 'bg-amber-500' },
    { id: 'audit-trail', label: 'Audit Trail', icon: CheckCircle, color: 'bg-gray-500' }
  ];

  const periodOptions = [
    { value: 'today', label: 'Today' },
    { value: 'this_week', label: 'This Week' },
    { value: 'this_month', label: 'This Month' },
    { value: 'last_month', label: 'Last Month' },
    { value: 'this_quarter', label: 'This Quarter' },
    { value: 'this_year', label: 'This Year' },
    { value: 'last_year', label: 'Last Year' },
    { value: 'custom', label: 'Custom Range' }
  ];

  useEffect(() => {
    fetchReport();
  }, [activeReport, period, customDates]);

  const fetchReport = async () => {
    setLoading(true);
    try {
      let url = `${BACKEND_URL}/api/financial-reports/`;
      let params = new URLSearchParams();
      
      if (activeReport === 'dashboard') {
        url += 'dashboard';
        params.append('period', period);
      } else if (activeReport === 'profit-loss') {
        url += 'profit-loss';
        params.append('period', period);
      } else if (activeReport === 'balance-sheet') {
        url += 'balance-sheet';
      } else if (activeReport === 'cash-flow') {
        url += 'cash-flow';
        params.append('period', period);
      } else if (activeReport === 'gst-summary') {
        url += 'gst/summary';
        params.append('period', period);
      } else if (activeReport === 'hsn-wise') {
        url += 'gst/hsn-wise';
        params.append('period', period);
      } else if (activeReport === 'audit-trail') {
        url += 'audit-trail';
        params.append('limit', '100');
      }
      
      if (period === 'custom' && customDates.from && customDates.to) {
        params.append('from_date', customDates.from);
        params.append('to_date', customDates.to);
      }
      
      const response = await fetch(`${url}?${params}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setReportData(data);
      } else {
        showToast.error('Failed to load report');
      }
    } catch (error) {
      console.error('Failed to fetch report:', error);
      showToast.error('Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const url = `${BACKEND_URL}/api/financial-reports/export/${activeReport}?period=${period}&format=csv`;
      window.open(url, '_blank');
      showToast.success('Report exported');
    } catch (error) {
      showToast.error('Export failed');
    }
  };

  const formatCurrency = (value) => {
    return `₹${(value || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
  };

  const renderDashboard = () => {
    const data = reportData?.dashboard;
    if (!data) return null;
    
    return (
      <div className="space-y-6">
        {/* Quick Stats */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-500">Monthly Revenue</p>
              <TrendingUp className="text-green-500" size={20} />
            </div>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(data.this_month?.revenue)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-500">Monthly Expenses</p>
              <TrendingDown className="text-red-500" size={20} />
            </div>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(data.this_month?.expenses)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-500">Net Profit</p>
              <IndianRupee className={data.this_month?.profit >= 0 ? "text-green-500" : "text-red-500"} size={20} />
            </div>
            <p className={`text-2xl font-bold ${data.this_month?.profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(data.this_month?.profit)}
            </p>
            <p className="text-xs text-gray-500 mt-1">{data.this_month?.margin?.toFixed(1)}% margin</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-500">Bank Balance</p>
              <Building2 className="text-blue-500" size={20} />
            </div>
            <p className="text-2xl font-bold text-blue-600">{formatCurrency(data.cash_position?.bank_balance)}</p>
            <p className="text-xs text-gray-500 mt-1">{data.cash_position?.bank_accounts} accounts</p>
          </div>
        </div>
        
        {/* Receivables & Payables */}
        <div className="grid grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <ArrowDownRight className="text-green-500" />
              Accounts Receivable
            </h3>
            <div className="flex justify-between items-end">
              <div>
                <p className="text-3xl font-bold text-green-600">{formatCurrency(data.receivables?.total)}</p>
                <p className="text-sm text-gray-500">{data.receivables?.count} customers</p>
              </div>
              <button 
                onClick={() => setActiveReport('audit-trail')}
                className="text-sm text-blue-600 hover:underline"
              >
                View Details →
              </button>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <ArrowUpRight className="text-red-500" />
              Accounts Payable
            </h3>
            <div className="flex justify-between items-end">
              <div>
                <p className="text-3xl font-bold text-red-600">{formatCurrency(data.payables?.total)}</p>
                <p className="text-sm text-gray-500">{data.payables?.count} vendors</p>
              </div>
              <button 
                onClick={() => setActiveReport('audit-trail')}
                className="text-sm text-blue-600 hover:underline"
              >
                View Details →
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderProfitLoss = () => {
    const data = reportData;
    if (!data) return null;
    
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b bg-gradient-to-r from-green-600 to-emerald-600">
          <h2 className="text-xl font-bold text-white">Profit & Loss Statement</h2>
          <p className="text-green-100 text-sm">
            {data.period?.from?.split('T')[0]} to {data.period?.to?.split('T')[0]}
          </p>
        </div>
        
        <div className="p-6 space-y-6">
          {/* Revenue Section */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3 text-lg">REVENUE</h3>
            <div className="space-y-2 pl-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Online Sales</span>
                <span className="font-medium">{formatCurrency(data.revenue?.online_sales)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Offline Sales</span>
                <span className="font-medium">{formatCurrency(data.revenue?.offline_sales)}</span>
              </div>
              <div className="flex justify-between font-semibold border-t pt-2">
                <span>Gross Revenue</span>
                <span>{formatCurrency(data.revenue?.gross_revenue)}</span>
              </div>
              <div className="flex justify-between text-red-600">
                <span>Less: GST Collected</span>
                <span>({formatCurrency(data.revenue?.less_gst)})</span>
              </div>
              <div className="flex justify-between font-bold text-lg border-t pt-2 bg-green-50 p-2 rounded">
                <span>Net Revenue</span>
                <span className="text-green-700">{formatCurrency(data.revenue?.net_revenue)}</span>
              </div>
            </div>
          </div>
          
          {/* Cost of Goods Sold */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3 text-lg">COST OF GOODS SOLD</h3>
            <div className="space-y-2 pl-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Purchases ({data.cost_of_goods_sold?.purchase_count} bills)</span>
                <span className="font-medium text-red-600">({formatCurrency(data.cost_of_goods_sold?.purchases)})</span>
              </div>
            </div>
          </div>
          
          {/* Gross Profit */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex justify-between items-center">
              <div>
                <span className="font-bold text-lg">GROSS PROFIT</span>
                <span className="ml-2 text-sm text-blue-600">({data.gross_margin_percent}% margin)</span>
              </div>
              <span className={`font-bold text-xl ${data.gross_profit >= 0 ? 'text-blue-700' : 'text-red-600'}`}>
                {formatCurrency(data.gross_profit)}
              </span>
            </div>
          </div>
          
          {/* Operating Expenses */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3 text-lg">OPERATING EXPENSES</h3>
            <div className="space-y-2 pl-4">
              {Object.entries(data.operating_expenses?.breakdown || {}).map(([category, amount]) => (
                <div key={category} className="flex justify-between">
                  <span className="text-gray-600 capitalize">{category.replace('_', ' ')}</span>
                  <span className="text-red-600">({formatCurrency(amount)})</span>
                </div>
              ))}
              <div className="flex justify-between font-semibold border-t pt-2">
                <span>Total Operating Expenses</span>
                <span className="text-red-600">({formatCurrency(data.operating_expenses?.total)})</span>
              </div>
            </div>
          </div>
          
          {/* Operating Profit */}
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="flex justify-between items-center">
              <div>
                <span className="font-bold text-lg">OPERATING PROFIT</span>
                <span className="ml-2 text-sm text-purple-600">({data.operating_margin_percent}% margin)</span>
              </div>
              <span className={`font-bold text-xl ${data.operating_profit >= 0 ? 'text-purple-700' : 'text-red-600'}`}>
                {formatCurrency(data.operating_profit)}
              </span>
            </div>
          </div>
          
          {/* Tax & Net Profit */}
          <div className="space-y-2 pl-4">
            <div className="flex justify-between">
              <span className="text-gray-600">Tax Provision (Est. 30%)</span>
              <span className="text-red-600">({formatCurrency(data.tax_provision)})</span>
            </div>
          </div>
          
          {/* Net Profit */}
          <div className={`p-4 rounded-lg ${data.net_profit >= 0 ? 'bg-green-100' : 'bg-red-100'}`}>
            <div className="flex justify-between items-center">
              <div>
                <span className="font-bold text-xl">NET PROFIT</span>
                <span className={`ml-2 text-sm ${data.net_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  ({data.net_margin_percent}% margin)
                </span>
              </div>
              <span className={`font-bold text-2xl ${data.net_profit >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                {formatCurrency(data.net_profit)}
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderBalanceSheet = () => {
    const data = reportData;
    if (!data) return null;
    
    return (
      <div className="grid grid-cols-2 gap-6">
        {/* Assets */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b bg-blue-600">
            <h2 className="text-lg font-bold text-white">ASSETS</h2>
          </div>
          <div className="p-4 space-y-4">
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">Current Assets</h3>
              <div className="space-y-2 pl-4 text-sm">
                <div className="flex justify-between">
                  <span>Cash & Bank</span>
                  <span className="font-medium">{formatCurrency(data.assets?.current_assets?.cash_and_bank?.total)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Accounts Receivable</span>
                  <span className="font-medium">{formatCurrency(data.assets?.current_assets?.accounts_receivable)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Inventory</span>
                  <span className="font-medium">{formatCurrency(data.assets?.current_assets?.inventory)}</span>
                </div>
                <div className="flex justify-between font-semibold border-t pt-2">
                  <span>Total Current Assets</span>
                  <span>{formatCurrency(data.assets?.current_assets?.total_current_assets)}</span>
                </div>
              </div>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">Fixed Assets</h3>
              <div className="space-y-2 pl-4 text-sm">
                <div className="flex justify-between font-semibold">
                  <span>Total Fixed Assets</span>
                  <span>{formatCurrency(data.assets?.fixed_assets?.total)}</span>
                </div>
              </div>
            </div>
            <div className="bg-blue-50 p-3 rounded-lg">
              <div className="flex justify-between font-bold text-lg">
                <span>TOTAL ASSETS</span>
                <span className="text-blue-700">{formatCurrency(data.assets?.total_assets)}</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Liabilities & Equity */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b bg-red-600">
            <h2 className="text-lg font-bold text-white">LIABILITIES & EQUITY</h2>
          </div>
          <div className="p-4 space-y-4">
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">Current Liabilities</h3>
              <div className="space-y-2 pl-4 text-sm">
                <div className="flex justify-between">
                  <span>Accounts Payable</span>
                  <span className="font-medium">{formatCurrency(data.liabilities?.current_liabilities?.accounts_payable)}</span>
                </div>
                <div className="flex justify-between">
                  <span>GST Payable</span>
                  <span className="font-medium">{formatCurrency(data.liabilities?.current_liabilities?.gst_payable)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Other Liabilities</span>
                  <span className="font-medium">{formatCurrency(data.liabilities?.current_liabilities?.other_liabilities)}</span>
                </div>
                <div className="flex justify-between font-semibold border-t pt-2">
                  <span>Total Current Liabilities</span>
                  <span>{formatCurrency(data.liabilities?.current_liabilities?.total_current_liabilities)}</span>
                </div>
              </div>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">Long-term Liabilities</h3>
              <div className="space-y-2 pl-4 text-sm">
                <div className="flex justify-between font-semibold">
                  <span>Total Long-term</span>
                  <span>{formatCurrency(data.liabilities?.long_term_liabilities?.total)}</span>
                </div>
              </div>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">Equity</h3>
              <div className="space-y-2 pl-4 text-sm">
                <div className="flex justify-between font-semibold">
                  <span>Retained Earnings</span>
                  <span>{formatCurrency(data.equity?.retained_earnings)}</span>
                </div>
              </div>
            </div>
            <div className="bg-red-50 p-3 rounded-lg">
              <div className="flex justify-between font-bold text-lg">
                <span>TOTAL LIAB. & EQUITY</span>
                <span className="text-red-700">{formatCurrency(data.total_liabilities_and_equity)}</span>
              </div>
            </div>
            {data.is_balanced && (
              <div className="flex items-center gap-2 text-green-600 text-sm">
                <CheckCircle size={16} />
                Balance Sheet is balanced
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderCashFlow = () => {
    const data = reportData;
    if (!data) return null;
    
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b bg-gradient-to-r from-cyan-600 to-blue-600">
          <h2 className="text-xl font-bold text-white">Cash Flow Statement</h2>
          <p className="text-cyan-100 text-sm">
            {data.period?.from?.split('T')[0]} to {data.period?.to?.split('T')[0]}
          </p>
        </div>
        
        <div className="p-6 space-y-6">
          {/* Operating Activities */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3 text-lg border-b pb-2">
              CASH FLOWS FROM OPERATING ACTIVITIES
            </h3>
            <div className="space-y-2 pl-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Cash from Customers</span>
                <span className="text-green-600">{formatCurrency(data.operating_activities?.cash_from_customers)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Cash from Online Sales</span>
                <span className="text-green-600">{formatCurrency(data.operating_activities?.cash_from_online_sales)}</span>
              </div>
              <div className="flex justify-between font-medium bg-green-50 p-2 rounded">
                <span>Total Inflows</span>
                <span className="text-green-700">{formatCurrency(data.operating_activities?.total_inflows)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Cash to Suppliers</span>
                <span className="text-red-600">({formatCurrency(data.operating_activities?.cash_to_suppliers)})</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Cash for Expenses</span>
                <span className="text-red-600">({formatCurrency(data.operating_activities?.cash_for_expenses)})</span>
              </div>
              <div className="flex justify-between font-medium bg-red-50 p-2 rounded">
                <span>Total Outflows</span>
                <span className="text-red-700">({formatCurrency(data.operating_activities?.total_outflows)})</span>
              </div>
              <div className={`flex justify-between font-bold text-lg p-3 rounded ${
                data.operating_activities?.net_operating_cash_flow >= 0 ? 'bg-blue-100' : 'bg-red-100'
              }`}>
                <span>Net Operating Cash Flow</span>
                <span className={data.operating_activities?.net_operating_cash_flow >= 0 ? 'text-blue-700' : 'text-red-700'}>
                  {formatCurrency(data.operating_activities?.net_operating_cash_flow)}
                </span>
              </div>
            </div>
          </div>
          
          {/* Investing & Financing */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold text-gray-700 mb-2">Investing Activities</h4>
              <div className="text-sm space-y-1">
                <div className="flex justify-between">
                  <span>Asset Purchases</span>
                  <span className="text-red-600">({formatCurrency(data.investing_activities?.asset_purchases)})</span>
                </div>
                <div className="flex justify-between">
                  <span>Asset Sales</span>
                  <span className="text-green-600">{formatCurrency(data.investing_activities?.asset_sales)}</span>
                </div>
                <div className="flex justify-between font-semibold border-t pt-1 mt-2">
                  <span>Net</span>
                  <span>{formatCurrency(data.investing_activities?.net_investing_cash_flow)}</span>
                </div>
              </div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold text-gray-700 mb-2">Financing Activities</h4>
              <div className="text-sm space-y-1">
                <div className="flex justify-between">
                  <span>Loan Receipts</span>
                  <span className="text-green-600">{formatCurrency(data.financing_activities?.loan_receipts)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Loan Payments</span>
                  <span className="text-red-600">({formatCurrency(data.financing_activities?.loan_payments)})</span>
                </div>
                <div className="flex justify-between font-semibold border-t pt-1 mt-2">
                  <span>Net</span>
                  <span>{formatCurrency(data.financing_activities?.net_financing_cash_flow)}</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Summary */}
          <div className="bg-gradient-to-r from-cyan-50 to-blue-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-3">CASH POSITION SUMMARY</h4>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-sm text-gray-500">Opening Balance</p>
                <p className="text-xl font-bold">{formatCurrency(data.summary?.opening_cash_balance)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Net Change</p>
                <p className={`text-xl font-bold ${data.summary?.net_change_in_cash >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {data.summary?.net_change_in_cash >= 0 ? '+' : ''}{formatCurrency(data.summary?.net_change_in_cash)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Closing Balance</p>
                <p className="text-xl font-bold text-blue-600">{formatCurrency(data.summary?.closing_cash_balance)}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderGSTSummary = () => {
    const data = reportData;
    if (!data) return null;
    
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b bg-gradient-to-r from-orange-500 to-amber-500">
          <h2 className="text-xl font-bold text-white">GST Summary</h2>
          <p className="text-orange-100 text-sm">
            {data.period?.from?.split('T')[0]} to {data.period?.to?.split('T')[0]}
          </p>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-2 gap-6">
            {/* Output GST */}
            <div className="p-4 bg-green-50 rounded-lg">
              <h3 className="font-semibold text-green-800 mb-3">OUTPUT GST (Sales)</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Taxable Value</span>
                  <span className="font-medium">{formatCurrency(data.output_gst?.taxable_value)}</span>
                </div>
                <div className="flex justify-between">
                  <span>CGST</span>
                  <span>{formatCurrency(data.output_gst?.cgst)}</span>
                </div>
                <div className="flex justify-between">
                  <span>SGST</span>
                  <span>{formatCurrency(data.output_gst?.sgst)}</span>
                </div>
                <div className="flex justify-between">
                  <span>IGST</span>
                  <span>{formatCurrency(data.output_gst?.igst)}</span>
                </div>
                <div className="flex justify-between font-bold border-t pt-2 text-green-700">
                  <span>Total Output GST</span>
                  <span>{formatCurrency(data.output_gst?.total)}</span>
                </div>
                <p className="text-xs text-gray-500">{data.output_gst?.invoice_count} invoices</p>
              </div>
            </div>
            
            {/* Input GST */}
            <div className="p-4 bg-blue-50 rounded-lg">
              <h3 className="font-semibold text-blue-800 mb-3">INPUT GST (Purchases)</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Taxable Value</span>
                  <span className="font-medium">{formatCurrency(data.input_gst?.taxable_value)}</span>
                </div>
                <div className="flex justify-between">
                  <span>CGST</span>
                  <span>{formatCurrency(data.input_gst?.cgst)}</span>
                </div>
                <div className="flex justify-between">
                  <span>SGST</span>
                  <span>{formatCurrency(data.input_gst?.sgst)}</span>
                </div>
                <div className="flex justify-between">
                  <span>IGST</span>
                  <span>{formatCurrency(data.input_gst?.igst)}</span>
                </div>
                <div className="flex justify-between font-bold border-t pt-2 text-blue-700">
                  <span>Total Input GST</span>
                  <span>{formatCurrency(data.input_gst?.total)}</span>
                </div>
                <p className="text-xs text-gray-500">{data.input_gst?.bill_count} bills</p>
              </div>
            </div>
          </div>
          
          {/* Net Liability */}
          <div className={`mt-6 p-6 rounded-lg text-center ${
            data.net_liability?.status === 'payable' ? 'bg-red-100' : 
            data.net_liability?.status === 'refundable' ? 'bg-green-100' : 'bg-gray-100'
          }`}>
            <p className="text-sm text-gray-600 mb-2">NET GST LIABILITY</p>
            <p className={`text-3xl font-bold ${
              data.net_liability?.status === 'payable' ? 'text-red-700' : 
              data.net_liability?.status === 'refundable' ? 'text-green-700' : 'text-gray-700'
            }`}>
              {formatCurrency(Math.abs(data.net_liability?.amount))}
            </p>
            <p className={`text-sm font-medium mt-2 uppercase ${
              data.net_liability?.status === 'payable' ? 'text-red-600' : 
              data.net_liability?.status === 'refundable' ? 'text-green-600' : 'text-gray-600'
            }`}>
              {data.net_liability?.status}
            </p>
          </div>
        </div>
      </div>
    );
  };

  const renderHSNWise = () => {
    const data = reportData;
    if (!data) return null;
    
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b">
          <h2 className="font-semibold text-gray-900">HSN-wise Summary</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left">HSN Code</th>
                <th className="px-4 py-3 text-left">Description</th>
                <th className="px-4 py-3 text-right">Qty</th>
                <th className="px-4 py-3 text-right">Taxable Value</th>
                <th className="px-4 py-3 text-right">Rate</th>
                <th className="px-4 py-3 text-right">CGST</th>
                <th className="px-4 py-3 text-right">SGST</th>
                <th className="px-4 py-3 text-right">Total GST</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {data.hsn_data?.map((item, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono">{item.hsn_code}</td>
                  <td className="px-4 py-3">{item.description}</td>
                  <td className="px-4 py-3 text-right">{item.quantity}</td>
                  <td className="px-4 py-3 text-right">{formatCurrency(item.taxable_value)}</td>
                  <td className="px-4 py-3 text-right">{item.gst_rate}%</td>
                  <td className="px-4 py-3 text-right">{formatCurrency(item.cgst)}</td>
                  <td className="px-4 py-3 text-right">{formatCurrency(item.sgst)}</td>
                  <td className="px-4 py-3 text-right font-medium">{formatCurrency(item.total_gst)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot className="bg-gray-100 font-semibold">
              <tr>
                <td className="px-4 py-3" colSpan={3}>TOTAL</td>
                <td className="px-4 py-3 text-right">{formatCurrency(data.totals?.taxable_value)}</td>
                <td className="px-4 py-3"></td>
                <td className="px-4 py-3 text-right">{formatCurrency(data.totals?.cgst)}</td>
                <td className="px-4 py-3 text-right">{formatCurrency(data.totals?.sgst)}</td>
                <td className="px-4 py-3 text-right">{formatCurrency(data.totals?.total_gst)}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    );
  };

  const renderAuditTrail = () => {
    const data = reportData;
    if (!data) return null;
    
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b">
          <h2 className="font-semibold text-gray-900">Audit Trail</h2>
          <p className="text-sm text-gray-500">{data.total} transactions</p>
        </div>
        <div className="divide-y max-h-[600px] overflow-y-auto">
          {data.entries?.map((entry, idx) => (
            <div key={idx} className="p-4 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded ${
                    entry.type === 'order' ? 'bg-green-100' :
                    entry.type === 'payment' ? 'bg-blue-100' :
                    entry.type === 'expense' ? 'bg-red-100' :
                    'bg-purple-100'
                  }`}>
                    {entry.type === 'order' && <TrendingUp size={16} className="text-green-600" />}
                    {entry.type === 'payment' && <IndianRupee size={16} className="text-blue-600" />}
                    {entry.type === 'expense' && <TrendingDown size={16} className="text-red-600" />}
                    {entry.type === 'journal' && <FileText size={16} className="text-purple-600" />}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{entry.reference}</p>
                    <p className="text-sm text-gray-500">{entry.description}</p>
                    <p className="text-xs text-gray-400">
                      {new Date(entry.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`font-bold ${
                    entry.direction === 'credit' ? 'text-green-600' :
                    entry.direction === 'debit' ? 'text-red-600' :
                    'text-purple-600'
                  }`}>
                    {entry.direction === 'credit' ? '+' : entry.direction === 'debit' ? '-' : ''}
                    {formatCurrency(entry.amount)}
                  </p>
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    entry.type === 'order' ? 'bg-green-100 text-green-700' :
                    entry.type === 'payment' ? 'bg-blue-100 text-blue-700' :
                    entry.type === 'expense' ? 'bg-red-100 text-red-700' :
                    'bg-purple-100 text-purple-700'
                  }`}>
                    {entry.type}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen" data-testid="financial-reports-page">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <PieChart className="text-indigo-600" />
              Financial Reports
            </h1>
            <p className="text-gray-600 mt-1">P&L, Balance Sheet, Cash Flow & GST Reports</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={fetchReport}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <RefreshCw size={18} />
              Refresh
            </button>
            {activeReport !== 'dashboard' && activeReport !== 'audit-trail' && (
              <button
                onClick={handleExport}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
              >
                <Download size={18} />
                Export CSV
              </button>
            )}
          </div>
        </div>
        
        {/* Report Type Tabs */}
        <div className="flex flex-wrap gap-2 mb-4">
          {reportTypes.map(report => (
            <button
              key={report.id}
              onClick={() => setActiveReport(report.id)}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 transition ${
                activeReport === report.id
                  ? `${report.color} text-white`
                  : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <report.icon size={18} />
              {report.label}
            </button>
          ))}
        </div>
        
        {/* Period Selector */}
        {activeReport !== 'balance-sheet' && activeReport !== 'audit-trail' && (
          <div className="bg-white rounded-lg shadow p-4 flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <Calendar size={18} className="text-gray-500" />
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg"
              >
                {periodOptions.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            {period === 'custom' && (
              <>
                <input
                  type="date"
                  value={customDates.from}
                  onChange={(e) => setCustomDates({...customDates, from: e.target.value})}
                  className="px-3 py-2 border border-gray-300 rounded-lg"
                />
                <span className="text-gray-500">to</span>
                <input
                  type="date"
                  value={customDates.to}
                  onChange={(e) => setCustomDates({...customDates, to: e.target.value})}
                  className="px-3 py-2 border border-gray-300 rounded-lg"
                />
              </>
            )}
          </div>
        )}
      </div>

      {/* Report Content */}
      {loading ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-gray-500">Generating report...</p>
        </div>
      ) : (
        <>
          {activeReport === 'dashboard' && renderDashboard()}
          {activeReport === 'profit-loss' && renderProfitLoss()}
          {activeReport === 'balance-sheet' && renderBalanceSheet()}
          {activeReport === 'cash-flow' && renderCashFlow()}
          {activeReport === 'gst-summary' && renderGSTSummary()}
          {activeReport === 'hsn-wise' && renderHSNWise()}
          {activeReport === 'audit-trail' && renderAuditTrail()}
        </>
      )}
    </div>
  );
};

export default FinancialReports;
