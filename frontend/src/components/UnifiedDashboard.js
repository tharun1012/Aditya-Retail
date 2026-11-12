import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { 
  Store, ShoppingCart, Package, TrendingUp, FileText, Receipt, 
  Users, BarChart3, Truck, Wrench, Settings, Gift, Sparkles, 
  ImageIcon, Search, MessageSquare, Target, Calculator, Hash,
  BookOpen, FolderTree, Shield, Bot, Facebook, Building2,
  LogOut, Home, Bell, RefreshCw, ChevronDown, Plus, Database, Download, CreditCard
} from 'lucide-react';
import NotificationBell from './NotificationBell';


// Maps each admin module path to its permission key (PERMISSION_MODULES from
// backend/roles_permissions.py). Used to hide modules a logged-in admin
// has no `view` permission for.
const MODULE_PERMISSION_MAP = {
  '/admin/products': 'products',
  '/admin/incomplete-products': 'products',
  '/admin/images': 'products',
  '/admin/new-products': 'products',
  '/admin/orders': 'orders',
  '/admin/pine-labs': 'orders',
  '/admin/inventory': 'inventory',
  '/admin/delivery': 'delivery',
  '/admin/service-tickets': 'service_tickets',
  '/admin/accounting': 'accounting',
  '/admin/tally-import': 'tally_import',
  '/admin/quotations': 'quotations',
  '/admin/reports': 'reports_exports',
  '/admin/customers': 'customers',
  '/admin/leads': 'leads',
  '/admin/lead-scraping': 'leads',
  '/admin/consultations': 'consultations',
  '/admin/combo-offers': 'combo_offers',
  '/admin/promotions': 'promotions',
  '/admin/banners': 'banners',
  '/admin/campaigns': 'campaigns',
  '/admin/ai-marketing': 'campaigns',
  '/admin/social-media': 'social_media',
  '/admin/blog': 'blog',
  '/admin/analytics': 'analytics',
  '/admin/customer-journey': 'analytics',
  '/admin/website-analytics': 'analytics',
  '/admin/ai-agents': 'ai_agents',
  '/admin/marketing-analytics': 'marketing_analytics',
  '/admin/categories': 'categories',
  '/admin/knowledge-base': 'knowledge_base',
  '/admin/seo-manager': 'seo_manager',
  '/admin/settings': 'system_settings',
  '/admin/store-team': 'team',
};


// Store-specific modules - these don't require admin authentication
const STORE_MODULES = [
  {
    id: 'store_lead_management',
    title: 'Lead Management',
    description: "Track and manage your store's leads.",
    icon: Target,
    color: 'bg-rose-500',
    path: '/store/leads',
    category: 'customers'
  },
  // Operations
  {
    id: 'create_invoice',
    title: 'Create Invoice',
    description: 'Create a direct invoice for walk-in customers taking products immediately.',
    icon: Receipt,
    color: 'bg-gradient-to-r from-emerald-500 to-emerald-600',
    path: '/store/create-invoice',
    category: 'operations',
    isHighlighted: true
  },
  {
    id: 'create_order',
    title: 'Create Sales Order',
    description: 'Create new sales orders for walk-in or phone customers.',
    icon: Plus,
    color: 'bg-gradient-to-r from-teal-500 to-teal-600',
    path: '/store/create-order',
    category: 'operations',
    isHighlighted: false
  },
  {
    id: 'orders',
    title: 'Orders & Sales',
    description: 'View and manage customer orders.',
    icon: ShoppingCart,
    color: 'bg-green-500',
    path: '/store/orders',
    category: 'operations'
  },
  {
    id: 'sales_invoices',
    title: 'Sales Invoices',
    description: 'Generate and manage sales invoices.',
    icon: Receipt,
    color: 'bg-cyan-500',
    path: '/store/invoices',
    category: 'operations'
  },
  {
    id: 'inventory',
    title: 'Inventory & Stock',
    description: 'Stock levels, low stock alerts, reorder management.',
    icon: BarChart3,
    color: 'bg-teal-500',
    path: '/store/inventory',
    category: 'operations'
  },
  {
    id: 'delivery',
    title: 'Delivery Management',
    description: 'Track orders, shipments, and delivery status.',
    icon: Truck,
    color: 'bg-yellow-500',
    path: '/store/deliveries',
    category: 'operations'
  },
  {
    id: 'service_tickets',
    title: 'Service Tickets',
    description: 'Manage customer service requests and track resolutions.',
    icon: Wrench,
    color: 'bg-amber-500',
    path: '/store/service',
    category: 'operations'
  },
  
  // Stock Management
  {
    id: 'stock_transfers',
    title: 'Stock Transfer',
    description: 'Request stock from warehouse or transfer between stores.',
    icon: FileText,
    color: 'bg-orange-500',
    path: '/store/transfers',
    category: 'stock'
  },
  {
    id: 'po_requests',
    title: 'PO Requests',
    description: 'Create and track purchase order requests.',
    icon: FileText,
    color: 'bg-indigo-500',
    path: '/store/po-requests',
    category: 'stock'
  },
  {
    id: 'purchase_orders',
    title: 'Purchase Orders',
    description: 'Create and manage purchase orders to vendors.',
    icon: Receipt,
    color: 'bg-blue-600',
    path: '/store/purchase-orders',
    category: 'stock'
  },
  {
    id: 'purchase_bills',
    title: 'Purchase Bills',
    description: 'Record vendor invoices with AI scan support.',
    icon: FileText,
    color: 'bg-orange-600',
    path: '/store/purchase-bills',
    category: 'stock'
  },
  {
    id: 'goods_receipt',
    title: 'Goods Receipt',
    description: 'Record goods received from suppliers.',
    icon: Package,
    color: 'bg-green-500',
    path: '/store/grn',
    category: 'stock'
  },
  
  // Reports
  {
    id: 'quotations',
    title: 'Quotations',
    description: 'Create and manage customer quotations.',
    icon: Receipt,
    color: 'bg-violet-600',
    path: '/store/quotations',
    category: 'reports'
  },
  {
    id: 'reports_exports',
    title: 'Sales Reports',
    description: 'View daily, monthly sales reports and analytics.',
    icon: BarChart3,
    color: 'bg-emerald-500',
    path: '/store/reports',
    category: 'reports'
  },
  
  // Customer
  {
    id: 'customers',
    title: 'Customer CRM',
    description: 'Manage customers, view purchase history.',
    icon: Users,
    color: 'bg-pink-500',
    path: '/store/customers',
    category: 'customers'
  }
];

// Warehouse-specific modules
const WAREHOUSE_MODULES = [
  // Logistics & Delivery - Primary Focus
  {
    id: 'delivery_management',
    title: 'Delivery Management',
    description: 'Manage pending orders, create challans, track deliveries.',
    icon: Truck,
    color: 'bg-gradient-to-r from-purple-500 to-purple-600',
    path: '/store/deliveries',
    category: 'logistics',
    isHighlighted: true
  },
  {
    id: 'delivery_personnel',
    title: 'Delivery Personnel',
    description: 'Add and manage delivery drivers and their assignments.',
    icon: Users,
    color: 'bg-purple-500',
    path: '/store/deliveries?tab=personnel',
    category: 'logistics'
  },
  {
    id: 'pending_orders',
    title: 'Pending SOs',
    description: 'View Sales Orders from stores awaiting dispatch.',
    icon: ShoppingCart,
    color: 'bg-amber-500',
    path: '/store/orders',
    category: 'logistics'
  },
  {
    id: 'so_to_invoice',
    title: 'SO to Invoice',
    description: 'Convert delivered Sales Orders to Tax Invoices.',
    icon: Receipt,
    color: 'bg-teal-500',
    path: '/store/invoices',
    category: 'logistics'
  },
  {
    id: 'all_invoices',
    title: 'All Invoices',
    description: 'View every invoice created across every store.',
    icon: Receipt,
    color: 'bg-indigo-500',
    path: '/store/all-invoices',
    category: 'logistics'
  },
  
  // Stock Management
  {
    id: 'inventory_stock',
    title: 'Stock Management',
    description: 'Central warehouse inventory and stock levels.',
    icon: Package,
    color: 'bg-blue-500',
    path: '/store/inventory',
    category: 'stock'
  },
  {
    id: 'stock_transfers',
    title: 'Stock Transfers',
    description: 'Process stock transfer requests from stores.',
    icon: FileText,
    color: 'bg-orange-500',
    path: '/store/transfers',
    category: 'stock'
  },
  
  // Procurement
  {
    id: 'purchase_requests',
    title: 'Purchase Requests',
    description: 'View and manage purchase order requests.',
    icon: FileText,
    color: 'bg-indigo-500',
    path: '/store/po-requests',
    category: 'procurement'
  },
  {
    id: 'purchase_orders',
    title: 'Purchase Orders',
    description: 'Manage purchase orders and supplier invoices.',
    icon: FileText,
    color: 'bg-blue-600',
    path: '/store/purchase-orders',
    category: 'procurement'
  },
  {
    id: 'grn_management',
    title: 'Goods Receipt',
    description: 'Record goods received from suppliers.',
    icon: Package,
    color: 'bg-green-500',
    path: '/store/grn',
    category: 'procurement'
  },
  {
    id: 'purchase_bills',
    title: 'Purchase Bills',
    description: 'Record vendor invoices and manage payables.',
    icon: FileText,
    color: 'bg-orange-500',
    path: '/store/purchase-bills',
    category: 'procurement'
  },
  
  // Reports
  {
    id: 'warehouse_reports',
    title: 'Warehouse Reports',
    description: 'Stock movement, delivery analytics, and performance.',
    icon: BarChart3,
    color: 'bg-emerald-500',
    path: '/store/reports',
    category: 'reports'
  }
];

const WAREHOUSE_CATEGORIES = {
  logistics: { label: 'Logistics & Delivery', color: 'text-purple-600' },
  stock: { label: 'Stock Management', color: 'text-blue-600' },
  procurement: { label: 'Procurement', color: 'text-indigo-600' },
  reports: { label: 'Reports', color: 'text-emerald-600' }
};

// All available modules - Admin Dashboard only
const ALL_MODULES = [
  // Core Operations
  {
    id: 'product_manager',
    title: 'Product Manager',
    description: 'Add, edit, delete products. Manage inventory and pricing.',
    icon: Package,
    color: 'bg-blue-500',
    path: '/admin/products',
    category: 'operations'
  },
  {
    id: 'orders_sales',
    title: 'Orders & Sales',
    description: 'View and manage customer orders.',
    icon: ShoppingCart,
    color: 'bg-green-500',
    path: '/admin/orders',
    category: 'accounting'
  },
  {
    id: 'pine_labs_transactions',
    title: 'Pine Labs Transactions',
    description: 'Payment gateway — transactions, refunds & reconciliation.',
    icon: CreditCard,
    color: 'bg-indigo-600',
    path: '/admin/pine-labs',
    category: 'accounting'
  },
  {
    id: 'sales_invoices',
    title: 'Sales Invoices',
    description: 'Generate and manage sales invoices.',
    icon: Receipt,
    color: 'bg-cyan-600',
    path: '/admin/sales-invoices',
    category: 'accounting'
  },
  {
    id: 'inventory_stock',
    title: 'Inventory & Stock',
    description: 'Stock levels, low stock alerts, reorder management.',
    icon: BarChart3,
    color: 'bg-teal-500',
    path: '/admin/inventory',
    category: 'operations'
  },
  {
    id: 'delivery_management',
    title: 'Delivery Management',
    description: 'Track orders, shipments, and delivery status.',
    icon: Truck,
    color: 'bg-yellow-500',
    path: '/admin/delivery',
    category: 'operations'
  },
  {
    id: 'delivery_challans',
    title: 'Delivery Challans',
    description: 'View and manage delivery challans created from invoices.',
    icon: FileText,
    color: 'bg-orange-500',
    path: '/admin/accounting?module=delivery-challans',
    category: 'operations'
  },
  {
    id: 'delivery_reports',
    title: 'Delivery Reports',
    description: 'Track driver performance, completion rates, and delivery analytics.',
    icon: BarChart3,
    color: 'bg-indigo-500',
    path: '/admin/delivery-reports',
    category: 'operations'
  },
  {
    id: 'delivery_personnel',
    title: 'Delivery Personnel',
    description: 'Add and manage delivery drivers for order fulfillment.',
    icon: Users,
    color: 'bg-purple-500',
    path: '/admin/accounting?module=delivery-persons',
    category: 'operations'
  },
  {
    id: 'service_tickets',
    title: 'Service Tickets',
    description: 'Manage customer service requests and track resolutions.',
    icon: Wrench,
    color: 'bg-amber-500',
    path: '/admin/service-tickets',
    category: 'operations'
  },
  
  // Accounting & Finance
  {
    id: 'accounting_billing',
    title: 'Accounting Dashboard',
    description: 'Main accounting dashboard with summary and navigation.',
    icon: Calculator,
    color: 'bg-teal-600',
    path: '/admin/accounting',
    category: 'accounting'
  },
  {
    id: 'tally_import',
    title: 'Tally Data Import',
    description: 'Import sales, purchases, customers from Tally/Excel.',
    icon: FileText,
    color: 'bg-orange-500',
    path: '/admin/tally-import',
    category: 'accounting'
  },
  {
    id: 'purchase_orders',
    title: 'Purchase Orders',
    description: 'Create and manage purchase orders to vendors.',
    icon: FileText,
    color: 'bg-blue-600',
    path: '/admin/purchase-orders',
    category: 'accounting'
  },
  {
    id: 'purchase_bills',
    title: 'Purchase Bills',
    description: 'Manage vendor bills, ITC, and payments.',
    icon: Receipt,
    color: 'bg-amber-600',
    path: '/admin/purchase-bills',
    category: 'accounting'
  },
  {
    id: 'gst_reports',
    title: 'GST Reports',
    description: 'GSTR-1, GSTR-2B, GSTR-3B, GSTR-9 and tax analysis.',
    icon: FileText,
    color: 'bg-green-600',
    path: '/admin/accounting-reports',
    category: 'accounting'
  },
  {
    id: 'compliance_audits',
    title: 'Compliance & Audits',
    description: 'MSME compliance, invoice locking, audit trails.',
    icon: Shield,
    color: 'bg-red-600',
    path: '/admin/compliance',
    category: 'accounting'
  },
  {
    id: 'quotations',
    title: 'Quotations',
    description: 'Create and manage customer quotations.',
    icon: Receipt,
    color: 'bg-violet-600',
    path: '/admin/quotations',
    category: 'accounting'
  },
  {
    id: 'reports_exports',
    title: 'Reports & Exports',
    description: 'Generate reports and export data.',
    icon: FileText,
    color: 'bg-gray-500',
    path: '/admin/reports',
    category: 'accounting'
  },
  {
    id: 'export_center',
    title: 'Export Center',
    description: 'Export data for Tally, GSTR-1, Excel with date range.',
    icon: Download,
    color: 'bg-blue-600',
    path: '/admin/export-center',
    category: 'accounting'
  },
  
  // Customer Management
  {
    id: 'customer_crm',
    title: 'Customer CRM',
    description: 'Manage customers, view purchase history, segments.',
    icon: Users,
    color: 'bg-pink-500',
    path: '/admin/customers',
    category: 'customers'
  },
  {
    id: 'lead_management',
    title: 'Lead Management',
    description: 'Track leads, funnel, AI agent interactions.',
    icon: Target,
    color: 'bg-rose-500',
    path: '/admin/leads',
    category: 'customers'
  },
  {
    id: 'expert_consultations',
    title: 'Expert Consultations',
    description: 'Track & manage customer consultation requests.',
    icon: FileText,
    color: 'bg-indigo-600',
    path: '/admin/consultations',
    category: 'customers'
  },
  
  // Marketing
  {
    id: 'combo_offers',
    title: 'Combo & Bundle Offers',
    description: 'Create special pricing for product bundles.',
    icon: Gift,
    color: 'bg-amber-600',
    path: '/admin/combo-offers',
    category: 'marketing'
  },
  {
    id: 'promotions_themes',
    title: 'Promotions & Themes',
    description: 'Manage seasonal themes, sales, festivals.',
    icon: Sparkles,
    color: 'bg-purple-500',
    path: '/admin/promotions',
    category: 'marketing'
  },
  {
    id: 'banner_management',
    title: 'Banner Management',
    description: 'Manage homepage banners and slides.',
    icon: ImageIcon,
    color: 'bg-cyan-500',
    path: '/admin/banners',
    category: 'marketing'
  },
  {
    id: 'marketing_campaigns',
    title: 'Marketing Campaigns',
    description: 'Create and manage marketing campaigns.',
    icon: MessageSquare,
    color: 'bg-red-500',
    path: '/admin/campaigns',
    category: 'marketing'
  },
  {
    id: 'social_media',
    title: 'Social Media Posts',
    description: 'AI-powered social media content generation.',
    icon: Facebook,
    color: 'bg-blue-600',
    path: '/admin/social-media',
    category: 'marketing'
  },
  
  // Analytics
  {
    id: 'analytics_dashboard',
    title: 'Analytics Dashboard',
    description: 'Sales trends, revenue analysis, and projections.',
    icon: TrendingUp,
    color: 'bg-indigo-500',
    path: '/admin/analytics',
    category: 'analytics'
  },
  {
    id: 'ai_agents_performance',
    title: 'AI Agents Performance',
    description: 'Monitor Sales, Service, Marketing AI agents.',
    icon: Bot,
    color: 'bg-indigo-500',
    path: '/admin/ai-agents',
    category: 'analytics'
  },
  {
    id: 'marketing_analytics',
    title: 'Marketing Analytics',
    description: 'Campaign performance, ROI tracking.',
    icon: BarChart3,
    color: 'bg-blue-600',
    path: '/admin/marketing-analytics',
    category: 'analytics'
  },
  
  // Configuration
  {
    id: 'category_management',
    title: 'Category Management',
    description: 'Organize products with categories.',
    icon: FolderTree,
    color: 'bg-indigo-500',
    path: '/admin/categories',
    category: 'config'
  },
  {
    id: 'knowledge_base',
    title: 'Knowledge Base',
    description: 'Train AI agents with product manuals.',
    icon: BookOpen,
    color: 'bg-emerald-500',
    path: '/admin/knowledge-base',
    category: 'config'
  },
  {
    id: 'document_numbering',
    title: 'Document Numbering',
    description: 'Configure document sequences.',
    icon: Hash,
    color: 'bg-cyan-600',
    path: '/admin/document-numbering',
    category: 'config'
  },
  {
    id: 'seo_manager',
    title: 'SEO Manager',
    description: 'Manage meta tags, titles & SEO settings.',
    icon: Search,
    color: 'bg-green-600',
    path: '/admin/seo-manager',
    category: 'config'
  },
  
  // Admin Only
  {
    id: 'team_management',
    title: 'Team & Admin Management',
    description: 'Manage admin users, team members, roles, and permissions.',
    icon: Shield,
    color: 'bg-purple-500',
    path: '/admin/team',
    category: 'admin_only',
    superAdminOnly: true
  },
  {
    id: 'store_management',
    title: 'Store Management',
    description: 'Multi-store setup and permissions.',
    icon: Building2,
    color: 'bg-emerald-600',
    path: '/admin/store-management',
    category: 'admin_only'
  },
  {
    id: 'admin_settings',
    title: 'Admin Settings',
    description: 'API credentials and system settings.',
    icon: Settings,
    color: 'bg-gray-700',
    path: '/admin/settings',
    category: 'admin_only'
  },
  {
    id: 'data_management',
    title: 'Data Management',
    description: 'Delete data, backups, edit permissions. Super Admin only.',
    icon: Database,
    color: 'bg-red-700',
    path: '/admin/data-management',
    category: 'admin_only',
    superAdminOnly: true
  }
];

const MODULE_CATEGORIES = {
  operations: { label: 'Operations', color: 'text-blue-600' },
  stock: { label: 'Stock Management', color: 'text-orange-600' },
  reports: { label: 'Reports & Quotations', color: 'text-emerald-600' },
  accounting: { label: 'Accounting & Finance', color: 'text-teal-600' },
  customers: { label: 'Customer Management', color: 'text-pink-600' },
  marketing: { label: 'Marketing', color: 'text-purple-600' },
  analytics: { label: 'Analytics', color: 'text-indigo-600' },
  config: { label: 'Configuration', color: 'text-gray-600' },
  admin_only: { label: 'Admin Only', color: 'text-red-600' }
};

const UnifiedDashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [userType, setUserType] = useState(null); // 'admin' or 'store'
  const [storeData, setStoreData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalOrders: 0,
    totalRevenue: 0,
    activeAIAgents: 0
  });
  const [topProducts, setTopProducts] = useState([]);
  const [topProductsLoading, setTopProductsLoading] = useState(false);
  const [salesSource, setSalesSource] = useState('both');

  useEffect(() => {
    // Check if store user
    const storeUser = localStorage.getItem('storeUser');
    if (storeUser) {
      const userData = JSON.parse(storeUser);
      setUser(userData);
      setUserType('store');
      fetchStoreData(userData.store_id);
      fetchStoreStats(userData.store_id);
      fetchTopProducts(userData.store_id);
      return;
    }

    // Check if admin user
    const adminToken = localStorage.getItem('authToken');
    const adminUser = localStorage.getItem('user');
    if (adminToken && adminUser) {
      setUser(JSON.parse(adminUser));
      setUserType('admin');
      fetchAdminStats();
      setLoading(false);
      return;
    }

    // No user logged in
    navigate('/admin/login');
  }, [navigate]);

  const fetchStoreData = async (storeId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/${storeId}`);
      const data = await response.json();
      if (data.status === 'success') {
        setStoreData(data.store);
      }
    } catch (error) {
      console.error('Error fetching store:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStoreStats = async (storeId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/${storeId}/dashboard?period=today`);
      const data = await response.json();
      if (data.status === 'success') {
        setStats({
          totalProducts: data.summary?.total_products || 0,
          totalOrders: data.summary?.order_count || 0,
          totalRevenue: data.summary?.total_sales || 0,
          activeAIAgents: 3
        });
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchTopProducts = async (storeId, source = 'both') => {
    setTopProductsLoading(true);
    try {
      const now = new Date();
      const firstOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
      const fromDate = firstOfMonth.toISOString().split('T')[0];
      const toDate = now.toISOString().split('T')[0];
      const response = await fetch(
        `${BACKEND_URL}/api/stores/${storeId}/reports/sales?group_by=item&from_date=${fromDate}&to_date=${toDate}&source=${source}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setTopProducts(data.data || []);
      }
    } catch (error) {
      console.error('Error fetching product-wise sales:', error);
    } finally {
      setTopProductsLoading(false);
    }
  };

  const handleSalesSourceChange = (newSource) => {
    setSalesSource(newSource);
    if (storeData?.id) {
      fetchTopProducts(storeData.id, newSource);
    }
  };

  const fetchAdminStats = async () => {
    try {
      const [productsRes, ordersRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/products?limit=1`),
        fetch(`${BACKEND_URL}/api/orders?limit=1`)
      ]);
      const productsData = await productsRes.json();
      const ordersData = await ordersRes.json();
      
      setStats({
        totalProducts: productsData.total || 0,
        totalOrders: ordersData.total || 0,
        totalRevenue: ordersData.total_revenue || 0,
        activeAIAgents: 5
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleLogout = () => {
    if (userType === 'store') {
      localStorage.removeItem('storeUser');
      localStorage.removeItem('storeToken');
      navigate('/store/login');
    } else {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      navigate('/admin/login');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  // Get allowed modules based on user type and permissions
  const getAllowedModules = () => {
    if (userType === 'admin') {
      // Check if user is super_admin - check both possible localStorage keys
      const adminUser = JSON.parse(localStorage.getItem('adminUser') || localStorage.getItem('user') || '{}');
      const isSuperAdmin = adminUser.role === 'super_admin';
      const perms = adminUser.permissions;

      return ALL_MODULES.filter(module => {
        // Super admin sees everything except never-applicable modules
        if (module.superAdminOnly && !isSuperAdmin) return false;
        if (isSuperAdmin) return true;

        // No permissions data → fall back to "show all non-super-admin modules"
        if (!perms) return true;

        const permKey = MODULE_PERMISSION_MAP[module.path];
        if (!permKey) return true; // unmapped modules always visible

        // Legacy List[str] shape
        if (Array.isArray(perms)) {
          return perms.includes(permKey) || perms.includes('all');
        }
        // Dict[str, List[str]] shape — require explicit 'view' permission
        if (typeof perms === 'object') {
          const modulePerms = perms[permKey];
          return Array.isArray(modulePerms) && modulePerms.includes('view');
        }
        return false;
      });
    }

    if (userType === 'store') {
      // Check if this is a warehouse
      if (storeData?.is_warehouse) {
        // Warehouse user - use warehouse-specific modules
        const permissions = storeData?.module_permissions || {};
        return WAREHOUSE_MODULES.filter(module => {
          if (permissions[module.id] !== undefined) {
            return permissions[module.id];
          }
          return true;
        });
      }
      
      // Store user - use store-specific modules that don't require admin auth
      // Filter based on module_permissions if set
      const permissions = storeData?.module_permissions || {};
      
      return STORE_MODULES.filter(module => {
        // Check specific permission if set
        if (permissions[module.id] !== undefined) {
          return permissions[module.id];
        }
        // Default to showing all store modules
        return true;
      });
    }

    return [];
  };

  const allowedModules = getAllowedModules();
  
  // Get appropriate categories based on user type
  const getCategories = () => {
    if (userType === 'store' && storeData?.is_warehouse) {
      return WAREHOUSE_CATEGORIES;
    }
    return MODULE_CATEGORIES;
  };

  // Group modules by category
  const categories = getCategories();
  const groupedModules = allowedModules.reduce((acc, module) => {
    const category = module.category;
    if (!acc[category]) acc[category] = [];
    acc[category].push(module);
    return acc;
  }, {});

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const displayName = userType === 'store' 
    ? storeData?.name || 'Store Dashboard'
    : 'Admin Dashboard';

  const displaySubtitle = userType === 'store'
    ? `${storeData?.is_warehouse ? 'Warehouse' : 'Store'} Code: ${storeData?.code || 'N/A'}`
    : 'Manage your e-commerce platform';

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className={`${userType === 'store' ? 'bg-gradient-to-r from-teal-700 to-teal-800' : 'bg-white border-b'} shadow-sm`}>
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className={`text-2xl font-bold ${userType === 'store' ? 'text-white' : 'text-gray-800'}`}>
                {displayName}
              </h1>
              <p className={`text-sm ${userType === 'store' ? 'text-teal-200' : 'text-gray-500'}`}>
                {displaySubtitle}
              </p>
            </div>
            
            <div className="flex items-center gap-4">
              {userType === 'store' && (
                <NotificationBell 
                  userRole={user?.role || 'store_manager'}
                  storeId={storeData?.id}
                  userId={user?.id}
                />
              )}
              
              <div className={`text-right hidden sm:block ${userType === 'store' ? 'text-white' : ''}`}>
                <p className="text-sm font-medium">
                  {userType === 'store' ? `${user?.first_name} ${user?.last_name}` : user?.name || 'Admin User'}
                </p>
                <p className={`text-xs ${userType === 'store' ? 'text-teal-200' : 'text-gray-500'}`}>
                  {userType === 'store' ? user?.role?.replace('_', ' ') : 'Admin'}
                </p>
              </div>
              
              <button
                onClick={() => navigate('/')}
                className={`p-2 rounded-lg transition-colors ${
                  userType === 'store' ? 'hover:bg-white/10 text-white' : 'hover:bg-gray-100 text-gray-600'
                }`}
                title="Go to Main Website"
              >
                <Home className="w-5 h-5" />
              </button>
              
              <button
                onClick={handleLogout}
                className={`p-2 rounded-lg transition-colors ${
                  userType === 'store' ? 'hover:bg-white/10 text-white' : 'hover:bg-gray-100 text-gray-600'
                }`}
                title="Logout"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards - Different for Warehouse vs Store */}
        {userType === 'store' && storeData?.is_warehouse ? (
          /* Warehouse Stats */
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-xl shadow-sm p-5 border-l-4 border-amber-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Pending SOs</p>
                  <p className="text-2xl font-bold text-gray-800">{stats.totalOrders}</p>
                </div>
                <ShoppingCart className="w-10 h-10 text-amber-200" />
              </div>
            </div>
            
            <div className="bg-white rounded-xl shadow-sm p-5 border-l-4 border-blue-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">In Transit</p>
                  <p className="text-2xl font-bold text-gray-800">0</p>
                </div>
                <Truck className="w-10 h-10 text-blue-200" />
              </div>
            </div>
            
            <div className="bg-white rounded-xl shadow-sm p-5 border-l-4 border-green-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Stock Items</p>
                  <p className="text-2xl font-bold text-gray-800">{stats.totalProducts}</p>
                </div>
                <Package className="w-10 h-10 text-green-200" />
              </div>
            </div>
            
            <div className="bg-white rounded-xl shadow-sm p-5 border-l-4 border-purple-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Pending Transfers</p>
                  <p className="text-2xl font-bold text-gray-800">0</p>
                </div>
                <FileText className="w-10 h-10 text-purple-200" />
              </div>
            </div>
          </div>
        ) : (
          /* Store/Admin Stats */
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-xl shadow-sm p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Total Products</p>
                  <p className="text-2xl font-bold text-gray-800">{stats.totalProducts}</p>
                </div>
                <Package className="w-10 h-10 text-blue-200" />
              </div>
            </div>
            
            <div className="bg-white rounded-xl shadow-sm p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Total Orders</p>
                  <p className="text-2xl font-bold text-gray-800">{stats.totalOrders}</p>
                </div>
                <ShoppingCart className="w-10 h-10 text-green-200" />
              </div>
            </div>
            
            <div className="bg-white rounded-xl shadow-sm p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Total Revenue</p>
                  <p className="text-2xl font-bold text-gray-800">{formatCurrency(stats.totalRevenue)}</p>
                </div>
                <TrendingUp className="w-10 h-10 text-purple-200" />
              </div>
            </div>
            
            <div className="bg-white rounded-xl shadow-sm p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Active AI Agents</p>
                  <p className="text-2xl font-bold text-gray-800">{stats.activeAIAgents}</p>
                </div>
                <Bot className="w-10 h-10 text-indigo-200" />
              </div>
            </div>
          </div>
        )}

        {/* Product-wise Sales & Best Sellers (This Month) — store users only */}
        {userType === 'store' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Best Sellers */}
            <div className="bg-white rounded-xl shadow-sm p-5">
              <div className="flex items-center justify-between mb-1">
                <h3 className="text-lg font-semibold text-gray-800">Best Sellers</h3>
                <select
                  value={salesSource}
                  onChange={(e) => handleSalesSourceChange(e.target.value)}
                  className="text-xs border rounded-lg px-2 py-1 text-gray-600 focus:outline-none focus:ring-1 focus:ring-teal-500"
                >
                  <option value="both">Online + Offline</option>
                  <option value="online">Online Sales</option>
                  <option value="offline">Offline Sales</option>
                </select>
              </div>
              <p className="text-xs text-gray-400 mb-4">This month, ranked by revenue</p>
              {topProductsLoading ? (
                <p className="text-sm text-gray-400">Loading...</p>
              ) : topProducts.length === 0 ? (
                <p className="text-sm text-gray-400">No sales recorded this month yet.</p>
              ) : (
                <div className="space-y-3">
                  {topProducts.slice(0, 5).map((item, idx) => (
                    <div key={item.product_id || idx} className="flex items-center justify-between">
                      <div className="flex items-center gap-3 min-w-0">
                        <span className="w-6 h-6 flex items-center justify-center rounded-full bg-orange-100 text-orange-700 text-xs font-bold flex-shrink-0">
                          {idx + 1}
                        </span>
                        <span className="text-sm text-gray-700 truncate">{item._id}</span>
                      </div>
                      <div className="text-right flex-shrink-0 ml-3">
                        <p className="text-sm font-semibold text-gray-800">{formatCurrency(item.total_revenue)}</p>
                        <p className="text-xs text-gray-400">{item.quantity_sold} sold</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Product-wise Sales */}
            <div className="bg-white rounded-xl shadow-sm p-5">
              <h3 className="text-lg font-semibold text-gray-800 mb-1">Product-wise Sales</h3>
              <p className="text-xs text-gray-400 mb-4">
                This month, all products ({salesSource === 'both' ? 'Online + Offline' : salesSource === 'online' ? 'Online Sales' : 'Offline Sales'})
              </p>
              {topProductsLoading ? (
                <p className="text-sm text-gray-400">Loading...</p>
              ) : topProducts.length === 0 ? (
                <p className="text-sm text-gray-400">No sales recorded this month yet.</p>
              ) : (
                <div className="max-h-64 overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-gray-400 text-xs border-b">
                        <th className="pb-2 font-medium">Product</th>
                        <th className="pb-2 font-medium text-right">Qty</th>
                        <th className="pb-2 font-medium text-right">Revenue</th>
                      </tr>
                    </thead>
                    <tbody>
                      {topProducts.map((item, idx) => (
                        <tr key={item.product_id || idx} className="border-b last:border-0">
                          <td className="py-2 text-gray-700 truncate max-w-[150px]">{item._id}</td>
                          <td className="py-2 text-right text-gray-600">{item.quantity_sold}</td>
                          <td className="py-2 text-right font-medium text-gray-800">{formatCurrency(item.total_revenue)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Module Tiles by Category */}
        {Object.entries(groupedModules).map(([category, modules]) => {
          const categoryInfo = categories[category];
          if (!categoryInfo || modules.length === 0) return null;
          
          return (
            <div key={category} className="mb-8">
              <h2 className={`text-lg font-semibold mb-4 ${categoryInfo.color}`}>
                {categoryInfo.label}
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {modules.map((module) => {
                  const Icon = module.icon;
                  return (
                    <button
                      key={module.id}
                      onClick={() => navigate(module.path)}
                      data-testid={`module-${module.id}`}
                      className={`relative p-5 bg-white rounded-xl shadow-sm hover:shadow-md transition-all text-left group ${
                        module.isHighlighted ? 'ring-2 ring-teal-500 ring-offset-2' : ''
                      }`}
                    >
                      {/* Highlighted Badge */}
                      {module.isHighlighted && (
                        <div className="absolute -top-2 -left-2 bg-teal-500 text-white text-xs font-bold px-2 py-1 rounded-full z-10">
                          Quick Action
                        </div>
                      )}
                      <div className="flex items-start gap-4">
                        <div className={`w-12 h-12 ${module.color} rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform`}>
                          <Icon className="w-6 h-6 text-white" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <h3 className="font-semibold text-gray-800 group-hover:text-blue-600 transition-colors">
                              {module.title}
                            </h3>
                            <span className="px-2 py-0.5 text-xs bg-green-100 text-green-700 rounded-full">
                              Active
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                            {module.description}
                          </p>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}

        {/* Help for Store Users */}
        {userType === 'store' && (
          <div className="mt-8 p-4 bg-teal-50 rounded-xl border border-teal-100">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-teal-100 rounded-lg">
                <Settings className="w-5 h-5 text-teal-600" />
              </div>
              <div>
                <h4 className="font-medium text-teal-800">Need more access?</h4>
                <p className="text-sm text-teal-600">
                  Contact your administrator to request additional module permissions for this store.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export { ALL_MODULES, STORE_MODULES, MODULE_CATEGORIES };
export default UnifiedDashboard;
