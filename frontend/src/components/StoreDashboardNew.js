import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { 
  Store, ShoppingCart, Package, TrendingUp, FileText, Receipt, 
  Users, ArrowRightLeft, BarChart3, Truck, Wrench, Plus,
  LogOut, Home, RefreshCw, Settings, X, Check, Eye,
  Calendar, AlertTriangle, Clock, Building2, Printer, Download
} from 'lucide-react';
import NotificationBell from './NotificationBell';


const StoreDashboardNew = () => {
  const navigate = useNavigate();
  const [storeUser, setStoreUser] = useState(null);
  const [storeData, setStoreData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalSales: 0,
    totalOrders: 0,
    pendingDeliveries: 0,
    lowStockItems: 0
  });

  useEffect(() => {
    const userData = localStorage.getItem('storeUser');
    if (userData) {
      const user = JSON.parse(userData);
      setStoreUser(user);
      fetchStoreData(user.store_id);
      fetchDashboardStats(user.store_id);
    } else {
      navigate('/store/login');
    }
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

  const fetchDashboardStats = async (storeId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/${storeId}/dashboard?period=today`);
      const data = await response.json();
      if (data.status === 'success') {
        setStats({
          totalSales: data.total_sales || 0,
          totalOrders: data.total_orders || 0,
          pendingDeliveries: data.pending_deliveries || 0,
          lowStockItems: data.low_stock_items || 0
        });
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('storeUser');
    localStorage.removeItem('storeToken');
    navigate('/store/login');
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  // Get permissions from store data
  const permissions = storeData?.permissions || {
    can_create_orders: true,
    can_view_orders: true,
    can_manage_inventory: true,
    can_request_stock: true,
    can_view_reports: true,
    can_manage_service: false,
    can_manage_deliveries: false
  };

  // Store modules - similar to admin dashboard
  const storeModules = [
    {
      title: 'Create Sales Order',
      description: 'Create new sales orders for walk-in or phone customers.',
      icon: Plus,
      color: 'bg-gradient-to-r from-teal-500 to-teal-600',
      path: '/store/create-order',
      status: 'active',
      permission: 'can_create_orders',
      isHighlighted: true
    },
    {
      title: 'View Orders',
      description: 'View and manage all sales orders for this store.',
      icon: ShoppingCart,
      color: 'bg-blue-500',
      path: '/store/orders',
      status: 'active',
      permission: 'can_view_orders'
    },
    {
      title: 'Inventory Management',
      description: 'Check stock levels, view inventory, manage products.',
      icon: Package,
      color: 'bg-purple-500',
      path: '/store/inventory',
      status: 'active',
      permission: 'can_manage_inventory'
    },
    {
      title: 'Stock Transfer',
      description: 'Request stock from warehouse or transfer between stores.',
      icon: ArrowRightLeft,
      color: 'bg-orange-500',
      path: '/store/transfers',
      status: 'active',
      permission: 'can_request_stock'
    },
    {
      title: 'PO Requests',
      description: 'Create and track purchase order requests.',
      icon: FileText,
      color: 'bg-indigo-500',
      path: '/store/po-requests',
      status: 'active',
      permission: 'can_request_stock'
    },
    {
      title: 'Sales Reports',
      description: 'View daily, monthly sales reports and analytics.',
      icon: BarChart3,
      color: 'bg-emerald-500',
      path: '/store/reports',
      status: 'active',
      permission: 'can_view_reports'
    },
    {
      title: 'Delivery Tracking',
      description: 'Track pending deliveries and update delivery status.',
      icon: Truck,
      color: 'bg-amber-500',
      path: '/store/deliveries',
      status: 'active',
      permission: 'can_manage_deliveries'
    },
    {
      title: 'Service Requests',
      description: 'Create and manage customer service tickets.',
      icon: Wrench,
      color: 'bg-red-500',
      path: '/store/service',
      status: 'active',
      permission: 'can_manage_service'
    },
    {
      title: 'Generate Invoice',
      description: 'Generate and print invoices for completed orders.',
      icon: Receipt,
      color: 'bg-cyan-500',
      path: '/store/invoices',
      status: 'active',
      permission: 'can_view_orders'
    }
  ];

  // Filter modules based on permissions
  const availableModules = storeModules.filter(module => {
    // If no permission field, always show
    if (!module.permission) return true;
    // Check if permission is granted
    return permissions[module.permission] !== false;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-teal-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading store dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-teal-700 to-teal-800 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-white/10 rounded-xl">
                <Store className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-xl font-bold">{storeData?.name || 'Store Dashboard'}</h1>
                <p className="text-teal-200 text-sm">Store Code: {storeData?.code || 'N/A'}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <NotificationBell 
                userRole={storeUser?.role || 'store_manager'}
                storeId={storeData?.id}
                userId={storeUser?.id}
              />
              
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium">{storeUser?.first_name} {storeUser?.last_name}</p>
                <p className="text-teal-200 text-xs capitalize">{storeUser?.role?.replace('_', ' ')}</p>
              </div>
              
              <button
                onClick={() => navigate('/')}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                title="Go to Main Website"
              >
                <Home className="w-5 h-5" />
              </button>
              
              <button
                onClick={handleLogout}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
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
        {/* Welcome Message */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            Welcome back, {storeUser?.first_name || 'Store Manager'}!
          </h2>
          <p className="text-gray-600">Manage your store operations from here</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-4 border-l-4 border-teal-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Sales</p>
                <p className="text-2xl font-bold text-gray-800">{formatCurrency(stats.totalSales)}</p>
                <p className="text-xs text-gray-400">Today</p>
              </div>
              <TrendingUp className="w-10 h-10 text-teal-200" />
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm p-4 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Orders</p>
                <p className="text-2xl font-bold text-gray-800">{stats.totalOrders}</p>
                <p className="text-xs text-gray-400">Today</p>
              </div>
              <ShoppingCart className="w-10 h-10 text-blue-200" />
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm p-4 border-l-4 border-amber-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Pending Deliveries</p>
                <p className="text-2xl font-bold text-gray-800">{stats.pendingDeliveries}</p>
                <p className="text-xs text-gray-400">Awaiting dispatch</p>
              </div>
              <Truck className="w-10 h-10 text-amber-200" />
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm p-4 border-l-4 border-red-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Low Stock Items</p>
                <p className="text-2xl font-bold text-gray-800">{stats.lowStockItems}</p>
                <p className="text-xs text-gray-400">Need restock</p>
              </div>
              <AlertTriangle className="w-10 h-10 text-red-200" />
            </div>
          </div>
        </div>

        {/* Module Tiles - Like Admin Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {availableModules.map((module, index) => {
            const Icon = module.icon;
            return (
              <button
                key={index}
                onClick={() => navigate(module.path)}
                className={`relative p-6 bg-white rounded-2xl shadow-sm hover:shadow-lg transition-all duration-200 text-left group ${
                  module.isHighlighted ? 'ring-2 ring-teal-500 ring-offset-2' : ''
                }`}
              >
                {/* Status Badge */}
                <div className="absolute top-4 right-4">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    module.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                  }`}>
                    {module.status === 'active' ? 'Active' : 'Coming Soon'}
                  </span>
                </div>

                {/* Icon */}
                <div className={`w-14 h-14 ${module.color} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <Icon className="w-7 h-7 text-white" />
                </div>

                {/* Content */}
                <h3 className="text-lg font-semibold text-gray-800 mb-2 group-hover:text-teal-600 transition-colors">
                  {module.title}
                </h3>
                <p className="text-sm text-gray-500 line-clamp-2">
                  {module.description}
                </p>

                {/* Highlighted Badge */}
                {module.isHighlighted && (
                  <div className="absolute -top-2 -left-2 bg-teal-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                    Quick Action
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {/* Footer Help */}
        <div className="mt-8 p-4 bg-teal-50 rounded-xl border border-teal-100">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-teal-100 rounded-lg">
              <Settings className="w-5 h-5 text-teal-600" />
            </div>
            <div>
              <h4 className="font-medium text-teal-800">Need more access?</h4>
              <p className="text-sm text-teal-600">
                Contact your administrator to request additional permissions for this store.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default StoreDashboardNew;
