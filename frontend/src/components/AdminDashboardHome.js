import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { 
  Package, 
  Image as ImageIcon, 
  ShoppingCart, 
  Users, 
  TrendingUp, 
  Settings,
  BarChart3,
  Bot,
  Truck,
  MessageSquare,
  FileText,
  LogOut,
  Target,
  Wrench,
  FolderTree,
  Shield,
  Gift,
  Sparkles,
  Facebook,
  Menu,
  X as CloseIcon,
  Receipt,
  Hash,
  Calculator,
  BookOpen,
  Search,
  Building2,
  Database,
  CreditCard,
  AlertCircle,
  BadgePercent
} from 'lucide-react';
import NotificationBell from './NotificationBell';

// Maps each dashboard module path to its permission key from
// backend/roles_permissions.py PERMISSION_MODULES. Used to hide modules
// that the logged-in user has no `view` permission for.
// Paths not listed here are treated as universally visible.
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
  '/admin/fy-transition': 'tally_import',
  '/admin/quotations': 'quotations',
  '/admin/reports': 'reports_exports',
  '/admin/customers': 'customers',
  '/admin/leads': 'leads',
  '/admin/lead-scraping': 'leads',
  '/admin/consultations': 'consultations',
  '/admin/combo-offers': 'combo_offers',
  '/admin/offers': 'cashback_offers',
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


const AdminDashboardHome = () => {
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [moduleSearchQuery, setModuleSearchQuery] = useState('');
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalOrders: 0,
    totalRevenue: 0,
    activeAgents: 5
  });

  useEffect(() => {
    // Get user from localStorage
    const adminUser = localStorage.getItem('adminUser');
    
    if (adminUser) {
      try {
        const parsedUser = JSON.parse(adminUser);
        setUser(parsedUser);
      } catch (e) {
        console.error('Error parsing adminUser:', e);
        setUser({
          email: "admin@test.com",
          name: "Admin User",
          role: "admin"
        });
      }
    } else {
      setUser({
        email: "admin@test.com",
        name: "Admin User",
        role: "admin"
      });
    }
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/products`);
      const data = await response.json();
      if (data.status === 'success') {
        setStats(prev => ({
          ...prev,
          totalProducts: data.count || data.products?.length || 0
        }));
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchUser = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth-verify/user`, {
        credentials: 'include'
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      }
    } catch (error) {
      console.error('Error fetching user:', error);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch(`${BACKEND_URL}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
    // Clear admin session data
    localStorage.removeItem('adminToken');
    localStorage.removeItem('adminUser');
    // Redirect to admin login page
    navigate('/admin/login');
  };

  const adminModules = [
    {
      title: 'Product Manager',
      description: 'Add, edit, delete products. Manage inventory and pricing.',
      icon: Package,
      color: 'bg-blue-500',
      path: '/admin/products',
      status: 'active'
    },
    {
      title: 'Cashback & Bank Offers',
      description: 'Upload brand PDFs — AI auto-extracts offers and maps them to matching products.',
      icon: BadgePercent,
      color: 'bg-amber-500',
      path: '/admin/offers',
      status: 'active',
      isNew: true
    },
    {
      title: 'Incomplete Products',
      description: 'Review & approve products from offline billing — AI-extract data from URLs, then publish to storefront.',
      icon: AlertCircle,
      color: 'bg-orange-500',
      path: '/admin/incomplete-products',
      status: 'active',
      isNew: true
    },
    {
      title: 'Image Manager',
      description: 'Update product images and media assets.',
      icon: ImageIcon,
      color: 'bg-purple-500',
      path: '/admin/images',
      status: 'active'
    },
    {
      title: 'Orders & Sales',
      description: 'View and manage customer orders.',
      icon: ShoppingCart,
      color: 'bg-green-500',
      path: '/admin/orders',
      status: 'active'
    },
    {
      title: 'Pine Labs Transactions',
      description: 'Payment gateway dashboard — transactions, refunds, reconciliation.',
      icon: CreditCard,
      color: 'bg-indigo-600',
      path: '/admin/pine-labs',
      status: 'active',
      isNew: true
    },
    {
      title: 'Analytics Dashboard',
      description: 'Sales trends, revenue analysis, and projections.',
      icon: TrendingUp,
      color: 'bg-orange-500',
      path: '/admin/analytics',
      status: 'active'
    },
    {
      title: 'Lead Management',
      description: 'Track leads, funnel, AI agent interactions & conversions.',
      icon: Target,
      color: 'bg-rose-500',
      path: '/admin/leads',
      status: 'active'
    },
    {
      title: 'Service Tickets',
      description: 'Manage customer service requests and track resolutions.',
      icon: Wrench,
      color: 'bg-amber-500',
      path: '/admin/service-tickets',
      status: 'active'
    },
    {
      title: 'Store & Team Management',
      description: 'Unified management - Stores, team members, roles, permissions, and document numbering.',
      icon: Building2,
      color: 'bg-teal-600',
      path: '/admin/store-team',
      status: 'active'
    },
    {
      title: 'Category Management',
      description: 'Organize products with categories and sub-categories.',
      icon: FolderTree,
      color: 'bg-indigo-500',
      path: '/admin/categories',
      status: 'active'
    },
    {
      title: 'Knowledge Base',
      description: 'Train AI agents with product manuals and documents.',
      icon: BookOpen,
      color: 'bg-emerald-500',
      path: '/admin/knowledge-base',
      status: 'active'
    },
    {
      title: 'Combo & Bundle Offers',
      description: 'Create special pricing for product bundles.',
      icon: Gift,
      color: 'bg-amber-600',
      path: '/admin/combo-offers',
      status: 'active'
    },
    {
      title: '🎉 Promotions & Themes',
      description: 'Manage seasonal themes, sales, festivals & promotions.',
      icon: Sparkles,
      color: 'bg-gradient-to-r from-purple-500 to-pink-500',
      path: '/admin/promotions',
      status: 'active',
      isNew: true
    },
    {
      title: 'Banner Management',
      description: 'Manage homepage banners and promotional slides.',
      icon: ImageIcon,
      color: 'bg-cyan-500',
      path: '/admin/banners',
      status: 'active'
    },
    {
      title: 'New Product Highlighting',
      description: 'Mark products as NEW to highlight on homepage.',
      icon: Sparkles,
      color: 'bg-yellow-500',
      path: '/admin/new-products',
      status: 'active'
    },
    {
      title: 'Social Media Posts',
      description: 'AI-powered social media content generation.',
      icon: Facebook,
      color: 'bg-blue-600',
      path: '/admin/social-media',
      status: 'active'
    },
    {
      title: 'SEO Manager',
      description: 'Manage meta tags, titles & SEO settings.',
      icon: Search,
      color: 'bg-green-600',
      path: '/admin/seo-manager',
      status: 'active'
    },
    {
      title: 'Customer CRM',
      description: 'Customer Relationship Management - Manage customers, view purchase history, segments & analytics.',
      icon: Users,
      color: 'bg-pink-500',
      path: '/admin/customers',
      status: 'active'
    },
    {
      title: 'AI Agents Performance',
      description: 'Monitor Sales, Service, Marketing, Delivery AI agents.',
      icon: Bot,
      color: 'bg-indigo-500',
      path: '/admin/ai-agents',
      status: 'active'
    },
    {
      title: 'Inventory & Stock',
      description: 'Stock levels, low stock alerts, reorder management.',
      icon: BarChart3,
      color: 'bg-teal-500',
      path: '/admin/inventory',
      status: 'active'
    },
    {
      title: 'Delivery Management',
      description: 'Track orders, shipments, and delivery status.',
      icon: Truck,
      color: 'bg-yellow-500',
      path: '/admin/delivery',
      status: 'active'
    },
    {
      title: 'Marketing Campaigns',
      description: 'Create and manage marketing campaigns.',
      icon: MessageSquare,
      color: 'bg-red-500',
      path: '/admin/campaigns',
      status: 'active'
    },
    {
      title: 'AI Marketing Agent',
      description: '24/7 autonomous lead generation & campaign management.',
      icon: Target,
      color: 'bg-purple-600',
      path: '/admin/ai-marketing',
      status: 'active'
    },
    {
      title: 'Marketing Analytics',
      description: 'Campaign performance, ROI tracking & channel insights.',
      icon: BarChart3,
      color: 'bg-blue-600',
      path: '/admin/marketing-analytics',
      status: 'active'
    },
    {
      title: 'Customer Journey',
      description: 'Funnel analysis, conversion tracking & attribution.',
      icon: TrendingUp,
      color: 'bg-green-600',
      path: '/admin/customer-journey',
      status: 'active'
    },
    {
      title: 'Lead Scraping',
      description: 'Autonomous AI lead generation from social media & directories.',
      icon: Target,
      color: 'bg-purple-600',
      path: '/admin/lead-scraping',
      status: 'active'
    },
    {
      title: 'Expert Consultations',
      description: 'Track & manage customer consultation requests with CRM integration.',
      icon: FileText,
      color: 'bg-indigo-600',
      path: '/admin/consultations',
      status: 'active'
    },
    {
      title: 'Website Analytics',
      description: 'AI Chat analytics, Expert Consultation tracking & Abandoned Cart recovery.',
      icon: BarChart3,
      color: 'bg-gradient-to-r from-orange-500 to-red-500',
      path: '/admin/website-analytics',
      status: 'active',
      isNew: true
    },
    {
      title: 'Blog Management',
      description: 'Create SEO-optimized blog posts with AI assistance. Boost organic traffic.',
      icon: FileText,
      color: 'bg-gradient-to-r from-emerald-500 to-teal-500',
      path: '/admin/blog',
      status: 'active',
      isNew: true
    },
    {
      title: 'Admin Settings',
      description: 'API credentials for Ad platforms, Social Media & Lead generation.',
      icon: Settings,
      color: 'bg-gray-700',
      path: '/admin/settings',
      status: 'active'
    },
    {
      title: 'Reports & Exports',
      description: 'Generate reports and export data.',
      icon: FileText,
      color: 'bg-gray-500',
      path: '/admin/reports',
      status: 'active'
    },
    {
      title: 'Accounting & Billing',
      description: 'Invoices, Purchases, Expenses, Vouchers, GST Reports - Complete accounting system with role-based access.',
      icon: Calculator,
      color: 'bg-teal-600',
      path: '/admin/accounting',
      status: 'active'
    },
    {
      title: 'Quotations',
      description: 'Create and manage customer quotations with Email, WhatsApp, and PDF download options.',
      icon: Receipt,
      color: 'bg-violet-600',
      path: '/admin/quotations',
      status: 'active'
    },
    {
      title: 'Tally Data Import',
      description: 'Import Sales, Purchases, Customers & Products from Tally (CSV/Excel).',
      icon: FileText,
      color: 'bg-amber-600',
      path: '/admin/tally-import',
      status: 'active'
    },
    {
      title: 'FY Transition Tools',
      description: 'AI-scan old SO PDFs/photos, backdate entries & sync document numbering for FY transition.',
      icon: FileText,
      color: 'bg-rose-600',
      path: '/admin/fy-transition',
      status: 'active'
    },
    {
      title: 'ROI Calculator',
      description: 'Store viability analysis, breakeven calculations, existing store ROI & business overview.',
      icon: Calculator,
      color: 'bg-indigo-600',
      path: '/admin/roi-calculator',
      status: 'active'
    },
    {
      title: 'Settings',
      description: 'General settings, configurations, and preferences.',
      icon: Settings,
      color: 'bg-slate-500',
      path: '/admin/settings',
      status: 'active'
    },
    {
      title: 'Admin User Management',
      description: 'Create company-level admins: Accountant, Marketing, Service Head, etc.',
      icon: Shield,
      color: 'bg-purple-600',
      path: '/admin/user-management',
      status: 'active',
      superAdminOnly: true
    },
    {
      title: 'Data Management',
      description: 'Delete data, backups, and edit permissions.',
      icon: Database,
      color: 'bg-red-700',
      path: '/admin/data-management',
      status: 'active',
      superAdminOnly: true
    }
  ];

  // Filter modules based on user role + granular permissions.
  // - super_admin: sees everything
  // - users with legacy permissions list (e.g. ['orders','customers']): show module if its
  //   permission key is in the list
  // - users with new permissions dict (e.g. {orders:['view',...]}): show module if its
  //   permission key exists in the dict AND that module has 'view' access
  // - if user has no permissions at all (legacy admin/manager roles): show everything
  //   except superAdminOnly modules (preserves backward compat)
  const getVisibleModules = () => {
    const isSuperAdmin = user?.role === 'super_admin';
    const perms = user?.permissions;

    const visible = adminModules.filter(module => {
      if (module.superAdminOnly && !isSuperAdmin) return false;
      if (isSuperAdmin) return true;

      // No permissions data → fall back to "show all" (legacy behaviour)
      if (!perms) return true;

      // Map this module's path to its permission key
      const permKey = MODULE_PERMISSION_MAP[module.path];
      // Modules without a defined permission mapping (e.g. dashboard tiles like
      // ROI Calculator) are always visible
      if (!permKey) return true;

      // Legacy List[str] shape: ['orders', 'customers', ...]
      if (Array.isArray(perms)) {
        return perms.includes(permKey) || perms.includes('all');
      }

      // New Dict[str, List[str]] shape: { orders: ['view',...] }
      if (typeof perms === 'object') {
        const modulePerms = perms[permKey];
        return Array.isArray(modulePerms) && modulePerms.includes('view');
      }

      return false;
    });

    // Apply search filter (matches title OR description, case-insensitive)
    const q = (moduleSearchQuery || '').trim().toLowerCase();
    const searched = q
      ? visible.filter(m =>
          (m.title || '').toLowerCase().includes(q) ||
          (m.description || '').toLowerCase().includes(q))
      : visible;

    // Alphabetical sort by title — strips leading emoji so "🎉 Promotions"
    // sorts under P not under emoji codepoints.
    return [...searched].sort((a, b) => {
      const norm = (s) => (s || '').replace(/^[\W_]+/, '').trim().toLowerCase();
      return norm(a.title).localeCompare(norm(b.title));
    });
  };

  const handleModuleClick = (module) => {
    if (module.status === 'active') {
      navigate(module.path);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {/* Mobile Menu Button */}
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
                aria-label="Toggle menu"
              >
                {sidebarOpen ? (
                  <CloseIcon className="w-6 h-6 text-gray-700" />
                ) : (
                  <Menu className="w-6 h-6 text-gray-700" />
                )}
              </button>
              <div>
                <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">Admin Dashboard</h1>
                <p className="text-gray-600 mt-1 text-sm sm:text-base hidden sm:block">Manage your e-commerce platform</p>
              </div>
            </div>
            <div className="flex items-center gap-2 sm:gap-4">
              {/* Notification Bell */}
              <NotificationBell 
                userRole={user?.role || 'admin'}
                userId={user?.id}
              />
              
              {user && (
                <div className="text-right hidden sm:block">
                  <p className="text-sm text-gray-600">Welcome back,</p>
                  <p className="font-semibold text-gray-900">{user.name}</p>
                  <p className="text-xs text-gray-500 capitalize">{user.role}</p>
                </div>
              )}
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Mobile Sidebar */}
      <div className={`fixed top-0 left-0 h-full w-80 bg-white shadow-2xl z-40 transform transition-transform duration-300 ease-in-out md:hidden ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="p-4 border-b flex items-center justify-between">
          <h2 className="text-lg font-bold">Navigation</h2>
          <button onClick={() => setSidebarOpen(false)} className="p-2">
            <CloseIcon className="w-6 h-6" />
          </button>
        </div>
        <div className="overflow-y-auto h-[calc(100vh-5rem)] p-4">
          {getVisibleModules().map((module, index) => (
            <button
              key={index}
              onClick={() => {
                handleModuleClick(module);
                setSidebarOpen(false);
              }}
              className="w-full text-left p-4 mb-2 rounded-lg hover:bg-gray-50 transition-colors border"
            >
              <div className="flex items-center gap-3">
                <div className={`${module.color} p-3 rounded-lg`}>
                  <module.icon className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 text-sm">{module.title}</h3>
                  <p className="text-xs text-gray-600 mt-1">{module.description}</p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
          <div className="bg-white rounded-lg shadow p-4 sm:p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-xs sm:text-sm">Total Products</p>
                <p className="text-2xl sm:text-3xl font-bold mt-1 sm:mt-2">{stats.totalProducts}</p>
              </div>
              <Package className="w-8 h-8 sm:w-12 sm:h-12 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Orders</p>
                <p className="text-3xl font-bold mt-2">0</p>
              </div>
              <ShoppingCart className="w-12 h-12 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Revenue</p>
                <p className="text-3xl font-bold mt-2">₹0</p>
              </div>
              <TrendingUp className="w-12 h-12 text-orange-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Active AI Agents</p>
                <p className="text-3xl font-bold mt-2">5</p>
              </div>
              <Bot className="w-12 h-12 text-indigo-500" />
            </div>
          </div>
        </div>

        {/* Module search bar — sticky-feel, alphabetised tile grid below */}
        <div className="bg-white rounded-lg shadow p-3 sm:p-4 mb-4 sm:mb-6 flex items-center gap-3"
             data-testid="admin-module-search">
          <Search className="w-5 h-5 text-gray-400 flex-shrink-0" />
          <input
            type="text"
            value={moduleSearchQuery}
            onChange={(e) => setModuleSearchQuery(e.target.value)}
            placeholder="Search modules… (e.g. orders, blog, pine labs)"
            className="flex-1 outline-none border-none text-sm sm:text-base bg-transparent"
            data-testid="admin-module-search-input"
          />
          {moduleSearchQuery && (
            <button
              onClick={() => setModuleSearchQuery('')}
              className="text-xs px-2 py-1 text-gray-500 hover:text-gray-700"
              data-testid="admin-module-search-clear"
            >
              Clear
            </button>
          )}
          <span className="text-xs text-gray-400 hidden sm:inline">
            {getVisibleModules().length} module{getVisibleModules().length === 1 ? '' : 's'}
          </span>
        </div>

        {/* Admin Modules Grid (alphabetised) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {getVisibleModules().length === 0 ? (
            <div className="col-span-full bg-white rounded-lg shadow p-8 text-center text-gray-500 text-sm">
              No modules match <span className="font-medium text-gray-700">&quot;{moduleSearchQuery}&quot;</span>.
              <button
                onClick={() => setModuleSearchQuery('')}
                className="ml-2 text-blue-600 hover:underline"
              >
                Clear search
              </button>
            </div>
          ) : getVisibleModules().map((module, index) => (
            <div
              key={index}
              onClick={() => handleModuleClick(module)}
              className={`bg-white rounded-lg shadow-lg p-4 sm:p-6 transition-all duration-300 ${
                module.status === 'active' 
                  ? 'hover:shadow-xl cursor-pointer hover:-translate-y-1 active:scale-95' 
                  : 'opacity-60 cursor-not-allowed'
              }`}
            >
              <div className="flex items-start gap-3 sm:gap-4">
                <div className={`${module.color} p-2 sm:p-3 rounded-lg flex-shrink-0`}>
                  <module.icon className="w-6 h-6 sm:w-8 sm:h-8 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between mb-2 gap-2">
                    <h3 className="text-base sm:text-lg font-semibold truncate">{module.title}</h3>
                    {module.status === 'coming-soon' && (
                      <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">
                        Coming Soon
                      </span>
                    )}
                    {module.status === 'active' && (
                      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                        Active
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">{module.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Info Box */}
        <div className="mt-8 bg-blue-50 border-l-4 border-blue-500 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            🚀 Getting Started
          </h3>
          <p className="text-blue-800">
            <strong>Active Modules:</strong> Product Manager and Image Manager are ready to use.
            <br />
            <strong>Coming Soon:</strong> Analytics, Orders, AI Performance tracking, and more advanced features will be available in the Enterprise Dashboard (2-3 days development).
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboardHome;
