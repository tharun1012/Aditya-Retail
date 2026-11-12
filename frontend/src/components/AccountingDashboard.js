import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { BACKEND_URL } from '../config/api';
import { 
  Calculator, 
  Receipt, 
  Hash, 
  ShoppingBag, 
  TrendingDown, 
  CreditCard, 
  FileText, 
  BarChart3,
  ChevronRight,
  Lock,
  Bot,
  Calendar,
  Truck,
  Package,
  Users,
  BookOpen,
  Building2,
  Bell,
  PieChart,
  Shield,
  ArrowRightLeft,
  AlertCircle
} from 'lucide-react';

// Import sub-components
import HSNCodeManagement from './HSNCodeManagement';
import OfflineInvoiceCreation from './OfflineInvoiceCreation';
import AIChatCA from './AIChatCA';
import DailyAccountingReports from './DailyAccountingReports';
import PurchaseManagement from './PurchaseManagement';
import PurchaseBillManagement from './PurchaseBillManagement';
import SalesInvoiceManagement from './SalesInvoiceManagement';
import StockReconciliation from './StockReconciliation';
import StockTransferApproval from './StockTransferApproval';
import DraftProductsReview from './DraftProductsReview';
import IncompleteProductsManager from './IncompleteProductsManager';
import PartyLedgerManagement from './PartyLedgerManagement';
import JournalVouchers from './JournalVouchers';
import BankReconciliation from './BankReconciliation';
import LandedCostCalculator from './LandedCostCalculator';
import PaymentReminders from './PaymentReminders';
import FinancialReports from './FinancialReports';
import ExpenseManagement from './ExpenseManagement';
import VouchersManagement from './VouchersManagement';
import AccountingReports from './AccountingReports';
import SalesOrderConversion from './SalesOrderConversion';
import DeliveryChallanManagement from './DeliveryChallanManagement';
import DeliveryPersonManagement from './DeliveryPersonManagement';
import InventoryDashboard from './InventoryDashboard';
import ComplianceAudits from './ComplianceAudits';
import AdminPORequestsView from './AdminPORequestsView';
import StoreDocumentManager from './StoreDocumentManager';

const AccountingDashboard = () => {
  const location = useLocation();
  const [activeSection, setActiveSection] = useState(
    location.state?.openModule === 'conversion' ? 'sales-order-conversion' : 'dashboard'
  );
  const [userRole, setUserRole] = useState(null);
  const [userPermissions, setUserPermissions] = useState([]);

  useEffect(() => {
    // Get user role from localStorage (check both key formats for compatibility)
    const adminUserStr = localStorage.getItem('adminUser') || localStorage.getItem('admin_user') || '{}';
    const adminUser = JSON.parse(adminUserStr);
    setUserRole(adminUser.role || 'admin');

    // Super admins, admins, and accountants have full access
    if (adminUser.role === 'admin' || adminUser.role === 'super_admin' ||
        adminUser.role === 'accountant' || adminUser.email === 'rohit.gadiya@gmail.com') {
      setUserPermissions(['all']);
    } else {
      // Load this admin's individually assigned permissions (from Admin User Management)
      setUserPermissions(adminUser.permissions || []);
    }
  }, []);

  // Define accounting modules with role requirements
  const accountingModules = [
    {
      id: 'ai-ca-chat',
      title: 'AI CA Assistant',
      description: 'Chat with your AI Chartered Accountant for insights & reports',
      icon: Bot,
      color: 'bg-purple-500',
      requiredRole: ['admin', 'accountant', 'manager'],
      component: AIChatCA,
      featured: true
    },
    {
      id: 'daily-reports',
      title: 'Daily Accounting Reports',
      description: 'Automated daily reports with journal entries & reconciliation',
      icon: Calendar,
      color: 'bg-indigo-500',
      requiredRole: ['admin', 'accountant'],
      component: DailyAccountingReports,
      featured: true
    },
    {
      id: 'offline-invoices',
      title: 'Offline Invoices',
      description: 'Create invoices for walk-in customers',
      icon: Receipt,
      color: 'bg-emerald-500',
      requiredRole: ['admin', 'store_manager', 'cashier'],
      component: OfflineInvoiceCreation
    },
    {
      id: 'sales-order-conversion',
      title: 'Sales Order Conversion',
      description: 'Convert sales orders to invoices for delivery',
      icon: FileText,
      color: 'bg-green-500',
      requiredRole: ['admin', 'accountant', 'warehouse_manager'],
      component: SalesOrderConversion,
      featured: true
    },
    {
      id: 'sales-invoices',
      title: 'Sales Invoices',
      description: 'View and manage all sales invoices',
      icon: Receipt,
      color: 'bg-teal-500',
      requiredRole: ['admin', 'accountant', 'manager'],
      component: SalesInvoiceManagement,
      featured: true
    },
    {
      id: 'hsn-codes',
      title: 'HSN Code Management',
      description: 'Manage HSN/SAC codes for GST',
      icon: Hash,
      color: 'bg-violet-500',
      requiredRole: ['admin', 'accountant'],
      component: HSNCodeManagement
    },
    {
      id: 'purchases',
      title: 'Purchase Orders',
      description: 'Create and manage purchase orders',
      icon: ShoppingBag,
      color: 'bg-blue-500',
      requiredRole: ['admin', 'purchase_manager', 'accountant'],
      component: PurchaseManagement
    },
    {
      id: 'po-requests',
      title: 'PO Requests',
      description: 'Review and approve store PO requests',
      icon: Bell,
      color: 'bg-amber-500',
      requiredRole: ['admin', 'super_admin', 'accountant'],
      component: AdminPORequestsView,
      featured: true
    },
    {
      id: 'purchase-bills',
      title: 'Purchase Bills',
      description: 'Record vendor invoices with AI scan support',
      icon: Receipt,
      color: 'bg-orange-500',
      requiredRole: ['admin', 'purchase_manager', 'accountant'],
      component: PurchaseBillManagement,
      featured: true
    },
    {
      id: 'stock-reconciliation',
      title: 'Stock Reconciliation',
      description: 'Auto-link purchase items to products',
      icon: Package,
      color: 'bg-cyan-500',
      requiredRole: ['admin', 'purchase_manager', 'accountant'],
      component: StockReconciliation,
      featured: true
    },
    {
      id: 'stock-transfer-approval',
      title: 'Stock Transfer Approval',
      description: 'Approve or reject inter-store stock transfer requests',
      icon: ArrowRightLeft,
      color: 'bg-orange-500',
      requiredRole: ['admin', 'warehouse_manager', 'super_admin'],
      component: StockTransferApproval,
      featured: true
    },
    {
      id: 'draft-products',
      title: 'Draft Products Review',
      description: 'Review and publish products from purchases',
      icon: FileText,
      color: 'bg-purple-500',
      requiredRole: ['admin', 'purchase_manager'],
      component: DraftProductsReview,
      featured: true
    },
    {
      id: 'incomplete-products',
      title: 'Incomplete Products',
      description: 'Products missing images, categories, or descriptions - AI enhancement available',
      icon: AlertCircle,
      color: 'bg-orange-500',
      requiredRole: ['admin', 'purchase_manager', 'manager'],
      component: IncompleteProductsManager,
      featured: true
    },
    {
      id: 'party-ledger',
      title: 'Party Ledger',
      description: 'Customer & Vendor accounts with payments tracking',
      icon: Users,
      color: 'bg-teal-500',
      requiredRole: ['admin', 'accountant', 'manager'],
      component: PartyLedgerManagement,
      featured: true
    },
    {
      id: 'journal-vouchers',
      title: 'Journal Vouchers',
      description: 'Manual adjustments and contra entries',
      icon: BookOpen,
      color: 'bg-indigo-500',
      requiredRole: ['admin', 'accountant'],
      component: JournalVouchers,
      featured: true
    },
    {
      id: 'bank-reconciliation',
      title: 'Bank Reconciliation',
      description: 'Match bank statements with ledger entries',
      icon: Building2,
      color: 'bg-blue-600',
      requiredRole: ['admin', 'accountant'],
      component: BankReconciliation,
      featured: true
    },
    {
      id: 'landed-cost',
      title: 'Landed Cost Calculator',
      description: 'Calculate total cost with freight & expenses',
      icon: Package,
      color: 'bg-orange-600',
      requiredRole: ['admin', 'accountant', 'purchase_manager'],
      component: LandedCostCalculator,
      featured: true
    },
    {
      id: 'payment-reminders',
      title: 'Payment Reminders',
      description: 'Automated reminders for outstanding balances',
      icon: Bell,
      color: 'bg-purple-600',
      requiredRole: ['admin', 'accountant', 'sales'],
      component: PaymentReminders,
      featured: true
    },
    {
      id: 'financial-reports',
      title: 'Financial Reports',
      description: 'P&L, Balance Sheet, Cash Flow & GST Reports',
      icon: PieChart,
      color: 'bg-indigo-600',
      requiredRole: ['admin', 'accountant'],
      component: FinancialReports,
      featured: true
    },
    {
      id: 'expenses',
      title: 'Expense Management',
      description: 'Record and track business expenses',
      icon: TrendingDown,
      color: 'bg-amber-500',
      requiredRole: ['admin', 'accountant', 'manager'],
      component: ExpenseManagement
    },
    {
      id: 'vouchers',
      title: 'Vouchers & Notes',
      description: 'Payment, receipt vouchers and credit/debit notes',
      icon: CreditCard,
      color: 'bg-indigo-500',
      requiredRole: ['admin', 'accountant', 'cashier'],
      component: VouchersManagement
    },
    {
      id: 'reports',
      title: 'Reports & GST',
      description: 'Sales, purchase, GST reports',
      icon: BarChart3,
      color: 'bg-teal-500',
      requiredRole: ['admin', 'accountant', 'manager'],
      component: AccountingReports
    },
    {
      id: 'delivery-challans',
      title: 'Delivery Challans',
      description: 'Create and track delivery challans with photo proof',
      icon: Truck,
      color: 'bg-green-500',
      requiredRole: ['admin', 'accountant', 'warehouse_manager'],
      component: DeliveryChallanManagement,
      featured: true
    },
    {
      id: 'delivery-persons',
      title: 'Delivery Personnel',
      description: 'Manage delivery person accounts',
      icon: Truck,
      color: 'bg-blue-500',
      requiredRole: ['admin', 'manager'],
      component: DeliveryPersonManagement
    },
    {
      id: 'inventory',
      title: 'Inventory Management',
      description: 'Track stock levels and manage inventory',
      icon: Package,
      color: 'bg-purple-500',
      requiredRole: ['admin', 'accountant', 'warehouse_manager'],
      component: InventoryDashboard,
      featured: true
    },
    {
      id: 'compliance-audits',
      title: 'Compliance & Audits',
      description: 'MSME compliance, overdue tracking, invoice locking & audit trail',
      icon: Shield,
      color: 'bg-red-500',
      requiredRole: ['admin', 'super_admin', 'accountant'],
      component: ComplianceAudits,
      featured: true
    },
    {
      id: 'store-documents',
      title: 'Store Document Manager',
      description: 'View & edit all store documents — Invoices, Sales Orders, Vouchers, with store-wise filtering',
      icon: Calendar,
      color: 'bg-indigo-600',
      requiredRole: ['admin', 'super_admin'],
      component: StoreDocumentManager,
      featured: true
    }
  ];

  // Maps each module's internal id to the permission key used in
  // Admin User Management, so a specifically-assigned permission
  // grants access to ONLY that module, regardless of role.
  const MODULE_PERMISSION_MAP = {
    'ai-ca-chat': 'ai_ca_assistant',
    'daily-reports': 'daily_accounting_reports',
    'offline-invoices': 'offline_invoices',
    'sales-order-conversion': 'sales_order_conversion',
    'sales-invoices': 'sales_invoices',
    'hsn-codes': 'hsn_management',
    'purchases': 'purchase_orders',
    'po-requests': 'po_requests',
    'purchase-bills': 'purchase_bills',
    'stock-reconciliation': 'stock_reconciliation',
    'stock-transfer-approval': 'stock_transfer_approval',
    'draft-products': 'draft_products_review',
    'incomplete-products': 'incomplete_products',
    'party-ledger': 'party_ledger',
    'journal-vouchers': 'journal_vouchers',
    'bank-reconciliation': 'bank_reconciliation',
    'landed-cost': 'landed_cost_calculator',
    'payment-reminders': 'payment_reminders',
    'financial-reports': 'financial_reports',
    'expenses': 'expense_management',
    'vouchers': 'vouchers_notes',
    'reports': 'reports_exports',
    'delivery-challans': 'delivery_challans',
    'delivery-persons': 'delivery_personnel',
    'inventory': 'inventory',
    'compliance-audits': 'compliance',
    'store-documents': 'store_document_manager'
  };

  // Check if user has access to a module.
  // Order: (1) 'all' permission, (2) a specifically assigned permission
  // for THIS module, (3) fallback to role-based access.
  // userPermissions may be either:
  //   - a legacy array of strings: ['orders', 'vouchers_notes', ...]
  //   - a newer dict: { orders: ['view'], vouchers_notes: ['view'], ... }
  const hasAccess = (requiredRoles, moduleId) => {
    if (!userRole) return false;

    const perms = userPermissions;
    const permissionKey = MODULE_PERMISSION_MAP[moduleId];

    if (Array.isArray(perms)) {
      if (perms.includes('all')) return true;
      if (permissionKey && perms.includes(permissionKey)) return true;
    } else if (perms && typeof perms === 'object') {
      if (Array.isArray(perms.all)) return true;
      if (permissionKey) {
        const modulePerms = perms[permissionKey];
        if (Array.isArray(modulePerms) && modulePerms.includes('view')) return true;
      }
    }

    return requiredRoles.includes(userRole);
  };

  // Filter modules based on user access
  const accessibleModules = accountingModules.filter(module =>
    hasAccess(module.requiredRole, module.id)
  );

  // Fetch accounting stats
  const [stats, setStats] = useState({
    totalSales: 0,
    totalPurchases: 0,
    totalExpenses: 0,
    netProfit: 0,
    period: 'All Time'
  });

  // GST Summary state
  const [gstSummary, setGstSummary] = useState({
    outputTax: 0,
    inputTax: 0,
    netPayable: 0,
    itcCarryForward: 0,
    invoiceCount: 0,
    billCount: 0,
    period: 'Loading...'
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const now = new Date();
        const thisMonthLabel = `${monthNames[now.getMonth()]} ${now.getFullYear()}`;
        const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
        const lastMonthLabel = `${monthNames[lastMonth.getMonth()]} ${lastMonth.getFullYear()}`;

        // First try this_month
        let response = await fetch(`${BACKEND_URL}/api/financial-reports/profit-loss?period=this_month`);
        let data = await response.json();
        
        // If no activity this month, try last month
        if (data.status === 'success' && data.revenue?.gross_revenue === 0 && data.cost_of_goods_sold?.purchases === 0) {
          response = await fetch(`${BACKEND_URL}/api/financial-reports/profit-loss?period=last_month`);
          data = await response.json();
          
          if (data.status === 'success' && (data.revenue?.gross_revenue > 0 || data.cost_of_goods_sold?.purchases > 0)) {
            setStats({
              totalSales: data.revenue?.gross_revenue || 0,
              totalPurchases: data.cost_of_goods_sold?.purchases || 0,
              totalExpenses: data.operating_expenses?.total || 0,
              netProfit: data.net_profit || 0,
              period: `Last Month (${lastMonthLabel})`
            });
            return;
          }
          
          // If still no data, get this FY
          response = await fetch(`${BACKEND_URL}/api/financial-reports/profit-loss?period=this_fy`);
          data = await response.json();
          if (data.status === 'success') {
            setStats({
              totalSales: data.revenue?.gross_revenue || 0,
              totalPurchases: data.cost_of_goods_sold?.purchases || 0,
              totalExpenses: data.operating_expenses?.total || 0,
              netProfit: data.net_profit || 0,
              period: `FY ${now.getMonth() >= 3 ? now.getFullYear() : now.getFullYear() - 1}-${now.getMonth() >= 3 ? now.getFullYear() + 1 : now.getFullYear()}`
            });
            return;
          }
        }
        
        if (data.status === 'success') {
          setStats({
            totalSales: data.revenue?.gross_revenue || 0,
            totalPurchases: data.cost_of_goods_sold?.purchases || 0,
            totalExpenses: data.operating_expenses?.total || 0,
            netProfit: data.net_profit || 0,
            period: thisMonthLabel
          });
        }
      } catch (error) {
        console.error('Error fetching accounting stats:', error);
      }
    };

    const fetchGstSummary = async () => {
      try {
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const now = new Date();
        const thisMonthLabel = `${monthNames[now.getMonth()]} ${now.getFullYear()}`;
        const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
        const lastMonthLabel = `${monthNames[lastMonth.getMonth()]} ${lastMonth.getFullYear()}`;

        // Try this_month first
        let response = await fetch(`${BACKEND_URL}/api/financial-reports/gst/summary?period=this_month`);
        let data = await response.json();
        
        if (data.status === 'success' && (data.output_gst?.total > 0 || data.input_gst?.total > 0)) {
          const outputTax = data.output_gst?.total || 0;
          const inputTax = data.input_gst?.total || 0;
          const net = outputTax - inputTax;
          
          setGstSummary({
            outputTax,
            inputTax,
            netPayable: net > 0 ? net : 0,
            itcCarryForward: net < 0 ? Math.abs(net) : 0,
            invoiceCount: data.output_gst?.invoice_count || 0,
            billCount: data.input_gst?.bill_count || 0,
            period: thisMonthLabel
          });
          return;
        }
        
        // Fallback to last_month
        response = await fetch(`${BACKEND_URL}/api/financial-reports/gst/summary?period=last_month`);
        data = await response.json();
        
        if (data.status === 'success') {
          const outputTax = data.output_gst?.total || 0;
          const inputTax = data.input_gst?.total || 0;
          const net = outputTax - inputTax;
          
          setGstSummary({
            outputTax,
            inputTax,
            netPayable: net > 0 ? net : 0,
            itcCarryForward: net < 0 ? Math.abs(net) : 0,
            invoiceCount: data.output_gst?.invoice_count || 0,
            billCount: data.input_gst?.bill_count || 0,
            period: lastMonthLabel
          });
        }
      } catch (error) {
        console.error('Error fetching GST summary:', error);
      }
    };

    fetchStats();
    fetchGstSummary();
  }, []);

  // Render active component
  const renderActiveSection = () => {
    if (activeSection === 'dashboard') {
      return (
        <div className="p-6 bg-gray-50 min-h-screen">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Calculator className="w-8 h-8 text-teal-700" />
              Accounting & Billing
            </h1>
            <p className="text-gray-600 mt-2">
              Complete accounting system for sales, purchases, expenses, and GST compliance
            </p>
          </div>

          {/* User Role Info */}
          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-2">
              <Lock className="w-5 h-5 text-blue-600" />
              <span className="font-semibold text-blue-900">
                Logged in as: <span className="text-blue-600">{userRole || 'Admin'}</span>
              </span>
              <span className="text-sm text-blue-700 ml-2">
                ({accessibleModules.length} modules accessible)
              </span>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-3xl font-bold text-emerald-600">₹{stats.totalSales.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
              <div className="text-sm text-gray-600 mt-1">Total Sales ({stats.period})</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-3xl font-bold text-blue-600">₹{stats.totalPurchases.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
              <div className="text-sm text-gray-600 mt-1">Total Purchases</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-3xl font-bold text-orange-600">₹{stats.totalExpenses.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
              <div className="text-sm text-gray-600 mt-1">Total Expenses</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-3xl font-bold text-teal-600">₹{stats.netProfit.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
              <div className="text-sm text-gray-600 mt-1">Net Profit</div>
            </div>
          </div>

          {/* GST Summary Widget */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl shadow-lg p-6 mb-8 text-white">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="bg-white/20 p-2 rounded-lg">
                  <Receipt className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-xl font-bold">GST Summary</h3>
                  <p className="text-indigo-200 text-sm">{gstSummary.period}</p>
                </div>
              </div>
              <button 
                onClick={() => setActiveSection('reports')}
                className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
              >
                View Details <ChevronRight className="w-4 h-4" />
              </button>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {/* Output Tax */}
              <div className="bg-white/10 rounded-lg p-4">
                <div className="text-indigo-200 text-xs uppercase tracking-wide mb-1">Output Tax (Sales)</div>
                <div className="text-2xl font-bold">₹{gstSummary.outputTax.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
                <div className="text-indigo-200 text-xs mt-1">{gstSummary.invoiceCount} invoices</div>
              </div>
              
              {/* Input Tax */}
              <div className="bg-white/10 rounded-lg p-4">
                <div className="text-indigo-200 text-xs uppercase tracking-wide mb-1">Input Tax Credit</div>
                <div className="text-2xl font-bold">₹{gstSummary.inputTax.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
                <div className="text-indigo-200 text-xs mt-1">{gstSummary.billCount} purchase bills</div>
              </div>
              
              {/* Net Payable or ITC Carry Forward */}
              {gstSummary.netPayable > 0 ? (
                <div className="bg-red-500/30 rounded-lg p-4 border border-red-400/50">
                  <div className="text-red-200 text-xs uppercase tracking-wide mb-1">Net Tax Payable</div>
                  <div className="text-2xl font-bold text-red-100">₹{gstSummary.netPayable.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
                  <div className="text-red-200 text-xs mt-1">Due to Government</div>
                </div>
              ) : (
                <div className="bg-green-500/30 rounded-lg p-4 border border-green-400/50">
                  <div className="text-green-200 text-xs uppercase tracking-wide mb-1">ITC Carry Forward</div>
                  <div className="text-2xl font-bold text-green-100">₹{gstSummary.itcCarryForward.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
                  <div className="text-green-200 text-xs mt-1">Credit Available</div>
                </div>
              )}
              
              {/* Status Indicator */}
              <div className="bg-white/10 rounded-lg p-4 flex flex-col justify-center items-center">
                {gstSummary.netPayable > 0 ? (
                  <>
                    <div className="w-12 h-12 rounded-full bg-red-500/30 flex items-center justify-center mb-2">
                      <TrendingDown className="w-6 h-6 text-red-200" />
                    </div>
                    <div className="text-xs text-center text-red-200">Tax Liability</div>
                  </>
                ) : (
                  <>
                    <div className="w-12 h-12 rounded-full bg-green-500/30 flex items-center justify-center mb-2">
                      <svg className="w-6 h-6 text-green-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <div className="text-xs text-center text-green-200">No Tax Due</div>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Accessible Modules Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {accessibleModules.map((module) => {
              const Icon = module.icon;
              return (
                <div
                  key={module.id}
                  onClick={() => setActiveSection(module.id)}
                  className={`bg-white rounded-lg shadow-lg p-6 cursor-pointer hover:shadow-xl transition-shadow border-2 ${module.featured ? 'border-purple-500 ring-2 ring-purple-200' : 'border-transparent hover:border-teal-500'}`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className={`${module.color} p-3 rounded-lg`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      {module.featured && (
                        <span className="bg-purple-100 text-purple-700 text-xs px-2 py-1 rounded-full font-semibold">
                          ✨ NEW
                        </span>
                      )}
                      <ChevronRight className="w-5 h-5 text-gray-400" />
                    </div>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {module.title}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {module.description}
                  </p>
                  <div className="mt-4 text-xs text-gray-500">
                    Access: {module.requiredRole.join(', ')}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Restricted Modules (if any) */}
          {accountingModules.length > accessibleModules.length && (
            <div className="mt-8">
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                Restricted Modules (Contact Admin for Access)
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {accountingModules
                  .filter(module => !hasAccess(module.requiredRole, module.id))
                  .map((module) => {
                    const Icon = module.icon;
                    return (
                      <div
                        key={module.id}
                        className="bg-gray-100 rounded-lg shadow p-6 opacity-60 cursor-not-allowed"
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div className="bg-gray-400 p-3 rounded-lg">
                            <Icon className="w-6 h-6 text-white" />
                          </div>
                          <Lock className="w-5 h-5 text-gray-500" />
                        </div>
                        <h3 className="text-xl font-bold text-gray-700 mb-2">
                          {module.title}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {module.description}
                        </p>
                        <div className="mt-4 text-xs text-red-600">
                          Requires: {module.requiredRole.join(' or ')}
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
          )}
        </div>
      );
    }

    // Render the selected module component
    const selectedModule = accountingModules.find(m => m.id === activeSection);
    if (selectedModule && hasAccess(selectedModule.requiredRole, selectedModule.id)) {
      const Component = selectedModule.component;
      return (
        <div>
          {/* Back button */}
          <div className="bg-white border-b p-4">
            <button
              onClick={() => setActiveSection('dashboard')}
              className="text-teal-600 hover:text-teal-800 flex items-center gap-2"
            >
              ← Back to Accounting Dashboard
            </button>
          </div>
          <Component />
        </div>
      );
    }

    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <Lock className="w-12 h-12 text-red-600 mb-4" />
          <h2 className="text-xl font-bold text-red-900 mb-2">Access Denied</h2>
          <p className="text-red-700">
            You don't have permission to access this module. Contact your administrator.
          </p>
          <button
            onClick={() => setActiveSection('dashboard')}
            className="mt-4 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {renderActiveSection()}
    </div>
  );
};

export default AccountingDashboard;
