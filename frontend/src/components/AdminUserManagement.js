import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Users, Shield, Edit, Trash2, Plus, Key, Eye, EyeOff, ArrowLeft, ChevronDown, ChevronRight, CheckSquare, Square, Package, ShoppingCart, BarChart3, Truck, Wrench, Calculator, FileText, Receipt, Bot, FolderTree, AlertCircle, MessageSquare, CreditCard, Target, TrendingUp, Gift, BadgePercent, Sparkles, Image, Facebook, BookOpen, Search, Database, Settings, Building2 } from 'lucide-react';

// Category labels and colors
const CATEGORY_INFO = {
  operations: { label: 'Operations', color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200' },
  accounting: { label: 'Accounting & Finance', color: 'text-teal-600', bg: 'bg-teal-50', border: 'border-teal-200' },
  customers: { label: 'Customer Management', color: 'text-purple-600', bg: 'bg-purple-50', border: 'border-purple-200' },
  marketing: { label: 'Marketing', color: 'text-pink-600', bg: 'bg-pink-50', border: 'border-pink-200' },
  analytics: { label: 'Analytics & Reports', color: 'text-indigo-600', bg: 'bg-indigo-50', border: 'border-indigo-200' },
  config: { label: 'Configuration', color: 'text-cyan-600', bg: 'bg-cyan-50', border: 'border-cyan-200' },
  admin: { label: 'Admin Settings', color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200' }
};

// Icon + color + description per module, mirrored from the Super Admin dashboard cards
// (AdminDashboardHome.js adminModules) so the permission picker matches that visual style.
const MODULE_ICON_MAP = {
  products: { icon: Package, color: 'bg-blue-500', description: 'Add, edit, delete products. Manage inventory and pricing.' },
  orders: { icon: ShoppingCart, color: 'bg-green-500', description: 'View and manage customer orders.' },
  inventory: { icon: BarChart3, color: 'bg-teal-500', description: 'Stock levels, low stock alerts, reorder management.' },
  delivery: { icon: Truck, color: 'bg-yellow-500', description: 'Track orders, shipments, and delivery status.' },
  service_tickets: { icon: Wrench, color: 'bg-amber-500', description: 'Manage customer service requests and track resolutions.' },

  accounting: { icon: Calculator, color: 'bg-teal-600', description: 'Invoices, Purchases, Expenses, Vouchers, GST Reports.' },
  tally_import: { icon: FileText, color: 'bg-amber-600', description: 'Import Sales, Purchases, Customers & Products from Tally.' },
  purchase_orders: { icon: Receipt, color: 'bg-violet-600', description: 'Create and manage purchase orders.' },
  purchase_bills: { icon: Receipt, color: 'bg-violet-500', description: 'Manage purchase bills and payments.' },
  gst_reports: { icon: FileText, color: 'bg-gray-500', description: 'GST filing and tax reports.' },
  compliance: { icon: Shield, color: 'bg-red-600', description: 'Compliance and audit tracking.' },
  quotations: { icon: Receipt, color: 'bg-violet-600', description: 'Create and manage customer quotations.' },
  reports_exports: { icon: FileText, color: 'bg-gray-500', description: 'Generate reports and export data.' },
  ai_ca_assistant: { icon: Bot, color: 'bg-indigo-500', description: 'AI chartered-accountant assistant.' },
  daily_accounting_reports: { icon: FileText, color: 'bg-teal-500', description: 'Daily accounting summary reports.' },
  offline_invoices: { icon: Receipt, color: 'bg-violet-500', description: 'Offline invoice management.' },
  sales_order_conversion: { icon: Package, color: 'bg-blue-600', description: 'Convert sales orders to invoices.' },
  sales_invoices: { icon: Receipt, color: 'bg-violet-600', description: 'Sales invoice management.' },
  hsn_management: { icon: FolderTree, color: 'bg-indigo-500', description: 'HSN code management.' },
  po_requests: { icon: Receipt, color: 'bg-amber-500', description: 'Purchase order approval requests.' },
  stock_reconciliation: { icon: BarChart3, color: 'bg-teal-500', description: 'Stock reconciliation tools.' },
  stock_transfer_approval: { icon: Truck, color: 'bg-yellow-600', description: 'Approve stock transfers between stores.' },
  draft_products_review: { icon: AlertCircle, color: 'bg-orange-400', description: 'Review draft products before publishing.' },
  incomplete_products: { icon: AlertCircle, color: 'bg-orange-500', description: 'Review & approve products from offline billing.' },
  party_ledger: { icon: FileText, color: 'bg-gray-600', description: 'Party ledger and account statements.' },
  journal_vouchers: { icon: FileText, color: 'bg-gray-600', description: 'Journal voucher entries.' },
  bank_reconciliation: { icon: Calculator, color: 'bg-teal-600', description: 'Bank reconciliation tools.' },
  landed_cost_calculator: { icon: Calculator, color: 'bg-indigo-600', description: 'Landed cost calculations for imports.' },
  payment_reminders: { icon: MessageSquare, color: 'bg-red-500', description: 'Send payment reminders to customers.' },
  financial_reports: { icon: FileText, color: 'bg-gray-500', description: 'Financial reporting and analysis.' },
  expense_management: { icon: Receipt, color: 'bg-rose-500', description: 'Track and manage expenses.' },
  vouchers_notes: { icon: FileText, color: 'bg-gray-600', description: 'Vouchers and credit/debit notes.' },
  delivery_challans: { icon: Truck, color: 'bg-yellow-600', description: 'Delivery challan management.' },
  delivery_personnel: { icon: Users, color: 'bg-yellow-700', description: 'Manage delivery staff.' },
  pine_labs_transactions: { icon: CreditCard, color: 'bg-indigo-600', description: 'Payment gateway dashboard.' },
  store_document_manager: { icon: FileText, color: 'bg-teal-500', description: 'Store document management.' },

  customers: { icon: Users, color: 'bg-pink-500', description: 'Customer Relationship Management.' },
  leads: { icon: Target, color: 'bg-rose-500', description: 'Track leads, funnel, AI agent interactions & conversions.' },
  consultations: { icon: FileText, color: 'bg-indigo-600', description: 'Track & manage customer consultation requests.' },
  customer_journey: { icon: TrendingUp, color: 'bg-green-600', description: 'Funnel analysis, conversion tracking & attribution.' },

  combo_offers: { icon: Gift, color: 'bg-amber-600', description: 'Create special pricing for product bundles.' },
  cashback_offers: { icon: BadgePercent, color: 'bg-amber-500', description: 'Cashback and bank offer management.' },
  promotions: { icon: Sparkles, color: 'bg-gradient-to-r from-purple-500 to-pink-500', description: 'Manage seasonal themes, sales, festivals & promotions.' },
  banners: { icon: Image, color: 'bg-cyan-500', description: 'Manage homepage banners and promotional slides.' },
  campaigns: { icon: MessageSquare, color: 'bg-red-500', description: 'Create and manage marketing campaigns.' },
  social_media: { icon: Facebook, color: 'bg-blue-600', description: 'AI-powered social media content generation.' },
  blog: { icon: FileText, color: 'bg-gradient-to-r from-emerald-500 to-teal-500', description: 'Create SEO-optimized blog posts with AI assistance.' },
  new_product_highlighting: { icon: Sparkles, color: 'bg-yellow-500', description: 'Mark products as NEW to highlight on homepage.' },

  analytics: { icon: TrendingUp, color: 'bg-orange-500', description: 'Sales trends, revenue analysis, and projections.' },
  ai_agents: { icon: Bot, color: 'bg-indigo-500', description: 'Monitor Sales, Service, Marketing, Delivery AI agents.' },
  marketing_analytics: { icon: BarChart3, color: 'bg-blue-600', description: 'Campaign performance, ROI tracking & channel insights.' },
  ai_marketing_agent: { icon: Target, color: 'bg-purple-600', description: '24/7 autonomous lead generation & campaign management.' },
  website_analytics: { icon: BarChart3, color: 'bg-gradient-to-r from-orange-500 to-red-500', description: 'AI Chat analytics, Expert Consultation & Abandoned Cart recovery.' },
  roi_calculator: { icon: Calculator, color: 'bg-indigo-600', description: 'Store viability analysis, breakeven calculations.' },
  lead_scraping: { icon: Target, color: 'bg-purple-600', description: 'Autonomous AI lead generation from social media & directories.' },

  categories: { icon: FolderTree, color: 'bg-indigo-500', description: 'Organize products with categories and sub-categories.' },
  knowledge_base: { icon: BookOpen, color: 'bg-emerald-500', description: 'Train AI agents with product manuals and documents.' },
  document_numbering: { icon: FileText, color: 'bg-slate-500', description: 'Configure invoice/SO document numbering sequences.' },
  seo_manager: { icon: Search, color: 'bg-green-600', description: 'Manage meta tags, titles & SEO settings.' },
  image_manager: { icon: Image, color: 'bg-purple-500', description: 'Update product images and media assets.' },
  data_management: { icon: Database, color: 'bg-red-700', description: 'Delete data, backups, and edit permissions.' },
  fy_transition_tools: { icon: FileText, color: 'bg-rose-600', description: 'AI-scan old SO PDFs/photos, backdate entries & sync numbering.' },

  stores: { icon: Building2, color: 'bg-teal-600', description: 'Manage stores and store-level configuration.' },
  team: { icon: Users, color: 'bg-teal-700', description: 'Manage team members and staff accounts.' },
  system_settings: { icon: Settings, color: 'bg-slate-500', description: 'General settings, configurations, and preferences.' },
  admin_settings: { icon: Settings, color: 'bg-gray-700', description: 'API credentials for Ad platforms, Social Media & Lead generation.' },
  admin_user_management: { icon: Shield, color: 'bg-purple-600', description: 'Create company-level admins with custom roles & permissions.' }
};

const AdminUserManagement = () => {
  const navigate = useNavigate();
  const [admins, setAdmins] = useState([]);
  const [roles, setRoles] = useState({});
  const [roleTemplates, setRoleTemplates] = useState({}); // built-in + custom role templates
  const [permissions, setPermissions] = useState({});
  const [modulesByCategory, setModulesByCategory] = useState({});
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedAdmin, setSelectedAdmin] = useState(null);
  const [expandedCategories, setExpandedCategories] = useState({});
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    phone: '',
    name: '',
    password: '',
    role: 'manager',
    custom_permissions: {},  // Changed to object {module_id: [permission1, permission2, ...]}
    use_custom_permissions: false
  });
  const [showPassword, setShowPassword] = useState(false);

  
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);

      // Fetch all admins
      const adminsRes = await fetch(`${BACKEND_URL}/api/admin/management/admins`);
      const adminsData = await adminsRes.json();
      setAdmins(adminsData.admins || []);

      // Fetch available roles
      const rolesRes = await fetch(`${BACKEND_URL}/api/admin/management/roles`);
      const rolesData = await rolesRes.json();
      setRoles(rolesData.roles || {});

      // Fetch available permissions
      const permsRes = await fetch(`${BACKEND_URL}/api/admin/management/permissions`);
      const permsData = await permsRes.json();
      setPermissions(permsData.permissions || {});

      // Fetch modules by category for granular permission selection
      const categoryRes = await fetch(`${BACKEND_URL}/api/admin/management/permissions/by-category`);
      const categoryData = await categoryRes.json();
      setModulesByCategory(categoryData.categories || {});

      // Fetch role templates (built-in + custom) for quick-create buttons
      const tmplRes = await fetch(`${BACKEND_URL}/api/admin/management/roles/templates`);
      const tmplData = await tmplRes.json();
      setRoleTemplates(tmplData.templates || {});

      // Expand all categories by default
      const expanded = {};
      Object.keys(categoryData.categories || {}).forEach(cat => {
        expanded[cat] = true;
      });
      setExpandedCategories(expanded);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching admin data:', error);
      setLoading(false);
    }
  };

  // Toggle a single permission for a module
  const togglePermission = (moduleId, permission) => {
    setFormData(prev => {
      const currentPerms = prev.custom_permissions[moduleId] || [];
      const newPerms = currentPerms.includes(permission)
        ? currentPerms.filter(p => p !== permission)
        : [...currentPerms, permission];
      
      return {
        ...prev,
        custom_permissions: {
          ...prev.custom_permissions,
          [moduleId]: newPerms
        }
      };
    });
  };

  // Toggle all permissions for a module
  const toggleAllModulePermissions = (moduleId, modulePermissions) => {
    setFormData(prev => {
      const currentPerms = prev.custom_permissions[moduleId] || [];
      const allSelected = modulePermissions.every(p => currentPerms.includes(p));
      
      return {
        ...prev,
        custom_permissions: {
          ...prev.custom_permissions,
          [moduleId]: allSelected ? [] : [...modulePermissions]
        }
      };
    });
  };

  // Check if a module has all permissions selected
  const hasAllPermissions = (moduleId, modulePermissions) => {
    const currentPerms = formData.custom_permissions[moduleId] || [];
    return modulePermissions.every(p => currentPerms.includes(p));
  };

  // Count total selected permissions
  const getTotalSelectedPermissions = () => {
    return Object.values(formData.custom_permissions).reduce((total, perms) => total + perms.length, 0);
  };

  // Convert any API error payload into a human-readable string.
  // FastAPI 422 returns { detail: [{ loc, msg, type }, ...] } which would
  // otherwise stringify as "[object Object]" if interpolated directly.
  const formatApiError = (err, fallback = 'Request failed') => {
    if (!err) return fallback;
    if (typeof err === 'string') return err;
    if (typeof err.detail === 'string') return err.detail;
    if (Array.isArray(err.detail)) {
      return err.detail
        .map(e => {
          if (typeof e === 'string') return e;
          const loc = Array.isArray(e?.loc) ? e.loc.slice(-1)[0] : '';
          return loc ? `${loc}: ${e.msg || ''}` : (e.msg || JSON.stringify(e));
        })
        .join('; ');
    }
    if (err.message) return err.message;
    try { return JSON.stringify(err); } catch (_) { return fallback; }
  };

  // Pre-fill the create-modal with a role template's permissions and open it.
  // Quick-Create role buttons call this so the admin doesn't have to tick boxes.
  const applyRoleTemplate = (templateId) => {
    const tmpl = roleTemplates[templateId];
    if (!tmpl) return;
    setSelectedAdmin(null);
    setFormData({
      email: '',
      username: '',
      phone: '',
      name: '',
      password: '',
      role: templateId,
      custom_permissions: tmpl.permissions || {},
      use_custom_permissions: true,
    });
    setShowCreateModal(true);
  };

  // Save the currently-selected permission set as a reusable custom role template
  const saveAsCustomRole = async () => {
    const name = window.prompt('Name this custom role (e.g., "Delivery Manager"):');
    if (!name || !name.trim()) return;
    const id = name.trim().toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
    if (!id) return;
    if (roleTemplates[id]) {
      if (!window.confirm(`A role with id '${id}' already exists. Overwrite?`)) return;
    }
    try {
      const res = await fetch(`${BACKEND_URL}/api/admin/management/roles/templates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id,
          name: name.trim(),
          level: 'manager',
          description: `Custom role: ${name.trim()}`,
          permissions: formData.custom_permissions || {},
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        alert(`Custom role "${name}" saved. You can now reuse it from the Quick Create panel.`);
        // Refresh templates so the new role button appears
        const tmplRes = await fetch(`${BACKEND_URL}/api/admin/management/roles/templates`);
        const tmplData = await tmplRes.json();
        setRoleTemplates(tmplData.templates || {});
      } else {
        alert(`Error: ${formatApiError(data, `HTTP ${res.status}`)}`);
      }
    } catch (e) {
      alert('Failed to save custom role');
    }
  };

  // Delete a previously-saved custom role template
  const deleteCustomRole = async (roleId, roleName) => {
    if (!window.confirm(`Delete the custom role "${roleName}"? This won't affect users already assigned to it.`)) return;
    try {
      const res = await fetch(`${BACKEND_URL}/api/admin/management/roles/templates/${roleId}`, {
        method: 'DELETE',
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        const tmplRes = await fetch(`${BACKEND_URL}/api/admin/management/roles/templates`);
        const tmplData = await tmplRes.json();
        setRoleTemplates(tmplData.templates || {});
      } else {
        alert(`Error: ${formatApiError(data, `HTTP ${res.status}`)}`);
      }
    } catch (e) {
      alert('Failed to delete custom role');
    }
  };

  const handleCreateAdmin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/management/admins`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        alert('Admin created successfully!');
        setShowCreateModal(false);
        resetForm();
        fetchData();
      } else {
        const error = await response.json().catch(() => ({}));
        alert(`Error: ${formatApiError(error, `HTTP ${response.status}`)}`);
      }
    } catch (error) {
      console.error('Error creating admin:', error);
      alert('Failed to create admin');
    }
  };

  const handleUpdateAdmin = async (e) => {
    e.preventDefault();
    try {
      const hasCustomPerms = Object.keys(formData.custom_permissions || {}).length > 0;
      const updateData = {
        name: formData.name,
        role: formData.role,
        permissions: hasCustomPerms ? formData.custom_permissions : undefined,
        is_active: true
      };

      const response = await fetch(`${BACKEND_URL}/api/admin/management/admins/${selectedAdmin.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });

      if (response.ok) {
        alert('Admin updated successfully!');
        setShowEditModal(false);
        setSelectedAdmin(null);
        resetForm();
        fetchData();
      } else {
        const error = await response.json().catch(() => ({}));
        alert(`Error: ${formatApiError(error, `HTTP ${response.status}`)}`);
      }
    } catch (error) {
      console.error('Error updating admin:', error);
      alert('Failed to update admin');
    }
  };

  const handleDeleteAdmin = async (adminId, adminEmail) => {
    if (!window.confirm(`Are you sure you want to delete admin: ${adminEmail}?`)) {
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/management/admins/${adminId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        alert('Admin deleted successfully!');
        fetchData();
      } else {
        const error = await response.json().catch(() => ({}));
        alert(`Error: ${formatApiError(error, `HTTP ${response.status}`)}`);
      }
    } catch (error) {
      console.error('Error deleting admin:', error);
      alert('Failed to delete admin');
    }
  };

  const handleEditClick = (admin) => {
    // Normalize permissions: support both legacy List[str] (e.g. ['orders','customers'])
    // and new Dict[str, List[str]] (e.g. {orders: ['view','edit']}) shapes so the
    // checkbox grid renders correctly without crashing.
    const raw = admin.permissions;
    let normalizedPerms = {};
    if (Array.isArray(raw)) {
      // Legacy shape: assume `view` on each named module
      raw.forEach((m) => { normalizedPerms[m] = ['view']; });
    } else if (raw && typeof raw === 'object') {
      normalizedPerms = raw;
    }

    setSelectedAdmin(admin);
    setFormData({
      email: admin.email || '',
      username: admin.username || '',
      phone: admin.phone || '',
      name: admin.name || '',
      password: '',
      role: admin.role,
      custom_permissions: normalizedPerms,
      use_custom_permissions: Object.keys(normalizedPerms).length > 0
    });
    setShowEditModal(true);
  };

  const resetForm = () => {
    setFormData({
      email: '',
      username: '',
      phone: '',
      name: '',
      password: '',
      role: 'manager',
      custom_permissions: {},
      use_custom_permissions: false
    });
    setShowPassword(false);
  };

  const getRoleBadgeColor = (role) => {
    const colors = {
      super_admin: 'bg-red-100 text-red-800',
      admin: 'bg-blue-100 text-blue-800',
      manager: 'bg-green-100 text-green-800',
      support: 'bg-yellow-100 text-yellow-800',
      content_manager: 'bg-purple-100 text-purple-800'
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading admin users...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => navigate('/admin')}
          className="flex items-center px-4 py-2 mb-6 text-gray-700 bg-white hover:bg-gray-100 rounded-lg transition-all border border-gray-300 hover:border-gray-400 shadow-sm"
          data-testid="back-to-dashboard-btn"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          <span className="font-medium">Back to Dashboard</span>
        </button>

        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin User Management</h1>
            <p className="text-gray-600">Manage team access and permissions</p>
          </div>
          <button
            onClick={() => {
              resetForm();
              setShowCreateModal(true);
            }}
            className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            <span>Create Admin</span>
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Total Admins</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">{admins.length}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Super Admins</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-600">
                {admins.filter(a => a.role === 'super_admin').length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Managers</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {admins.filter(a => a.role === 'manager').length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Support Staff</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-yellow-600">
                {admins.filter(a => a.role === 'support').length}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Create from Role Templates */}
        <Card className="mb-6" data-testid="quick-create-roles-section">
          <CardHeader>
            <CardTitle className="flex items-center justify-between flex-wrap gap-2">
              <span>Quick Create by Role</span>
              <span className="text-xs font-normal text-gray-500">
                Click a role to pre-fill the create form with that role's permissions
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {/* Group by level: admin / manager / staff / custom */}
            {['admin', 'manager', 'staff'].map(level => {
              const entries = Object.entries(roleTemplates).filter(
                ([id, t]) => (t.level || 'manager') === level && id !== 'super_admin' && !t.is_custom
              );
              if (entries.length === 0) return null;
              const levelLabel = level.charAt(0).toUpperCase() + level.slice(1);
              return (
                <div key={level} className="mb-4 last:mb-0">
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">{levelLabel} Roles</p>
                  <div className="flex flex-wrap gap-2">
                    {entries.map(([id, tmpl]) => (
                      <button
                        key={id}
                        type="button"
                        onClick={() => applyRoleTemplate(id)}
                        title={tmpl.description}
                        data-testid={`quick-role-${id}`}
                        className="px-3 py-2 text-sm rounded-lg border border-blue-200 bg-blue-50 hover:bg-blue-100 text-blue-700 transition-colors flex items-center gap-2"
                      >
                        <Plus className="w-3.5 h-3.5" />
                        {tmpl.name}
                      </button>
                    ))}
                  </div>
                </div>
              );
            })}

            {/* Custom roles, with delete buttons */}
            {(() => {
              const customs = Object.entries(roleTemplates).filter(([_, t]) => t.is_custom);
              if (customs.length === 0) return null;
              return (
                <div className="pt-3 border-t border-dashed">
                  <p className="text-xs font-semibold text-purple-600 uppercase tracking-wide mb-2">Your Custom Roles</p>
                  <div className="flex flex-wrap gap-2">
                    {customs.map(([id, tmpl]) => (
                      <div key={id} className="inline-flex items-stretch rounded-lg border border-purple-200 bg-purple-50 overflow-hidden">
                        <button
                          type="button"
                          onClick={() => applyRoleTemplate(id)}
                          title={tmpl.description}
                          data-testid={`quick-role-${id}`}
                          className="px-3 py-2 text-sm hover:bg-purple-100 text-purple-700 flex items-center gap-2"
                        >
                          <Plus className="w-3.5 h-3.5" />
                          {tmpl.name}
                        </button>
                        <button
                          type="button"
                          onClick={() => deleteCustomRole(id, tmpl.name)}
                          title={`Delete custom role "${tmpl.name}"`}
                          data-testid={`delete-custom-role-${id}`}
                          className="px-2 border-l border-purple-200 hover:bg-red-50 text-red-500"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })()}

            <p className="text-xs text-gray-500 mt-3">
              Need a unique role? Open <strong>Create Admin</strong>, tick "Use custom permissions",
              configure the modules you need, then click <strong>Save as Custom Role</strong>
              inside the form.
            </p>
          </CardContent>
        </Card>

        {/* Admins List */}
        <Card>
          <CardHeader>
            <CardTitle>All Admin Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Name</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Username / Email</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Role</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Permissions</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {admins.map((admin) => (
                    <tr key={admin.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                            {(admin.name || 'U').charAt(0).toUpperCase()}
                          </div>
                          <div>
                            <span className="font-medium block">{admin.name || 'Unknown'}</span>
                            {admin.phone && <span className="text-xs text-gray-500">{admin.phone}</span>}
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-gray-600">
                        <div>
                          {admin.username && <span className="font-medium text-gray-800">{admin.username}</span>}
                          {admin.email && <span className="block text-sm text-gray-500">{admin.email}</span>}
                          {!admin.username && !admin.email && <span className="text-gray-400">-</span>}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getRoleBadgeColor(admin.role)}`}>
                          {roles[admin.role]?.name || admin.role || 'Unknown'}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex flex-wrap gap-1">
                          {(() => {
                            // Permissions can be either legacy List[str] or new Dict[str, List[str]]
                            const p = admin.permissions;
                            let flat = [];
                            if (Array.isArray(p)) {
                              flat = p;
                            } else if (p && typeof p === 'object') {
                              // For dict shape, show module names that have at least one permission
                              flat = Object.keys(p).filter(k => Array.isArray(p[k]) && p[k].length > 0);
                            }
                            return (
                              <>
                                {flat.slice(0, 3).map((perm, idx) => (
                                  <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                                    {perm}
                                  </span>
                                ))}
                                {flat.length > 3 && (
                                  <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                                    +{flat.length - 3} more
                                  </span>
                                )}
                                {flat.length === 0 && (
                                  <span className="text-xs text-gray-400">—</span>
                                )}
                              </>
                            );
                          })()}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          admin.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {admin.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex justify-end space-x-2">
                          <button
                            onClick={() => handleEditClick(admin)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                            title="Edit"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          {admin.role !== 'super_admin' && (
                            <button
                              onClick={() => handleDeleteAdmin(admin.id, admin.email)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Create Admin Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <h2 className="text-2xl font-bold mb-6">Create New Admin</h2>
                <form onSubmit={handleCreateAdmin} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Name *</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Username <span className="text-gray-400 text-xs">(or auto-generated)</span>
                      </label>
                      <input
                        type="text"
                        value={formData.username}
                        onChange={(e) => setFormData({...formData, username: e.target.value.toLowerCase().replace(/\s/g, '_')})}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., john_smith"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                      <input
                        type="tel"
                        value={formData.phone}
                        onChange={(e) => setFormData({...formData, phone: e.target.value})}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., 9876543210"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email <span className="text-gray-400 text-xs">(optional if username/phone provided)</span>
                    </label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="user@example.com"
                    />
                  </div>

                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-700">
                    <strong>Login Options:</strong> User can login using any of: Username, Email, or Phone number
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Password *</label>
                    <div className="relative">
                      <input
                        type={showPassword ? 'text' : 'password'}
                        value={formData.password}
                        onChange={(e) => setFormData({...formData, password: e.target.value})}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500"
                      >
                        {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
                    <select
                      value={formData.role}
                      onChange={(e) => {
                        const newRole = e.target.value;
                        // If the chosen role matches a template, pre-fill its permissions.
                        // Otherwise keep whatever the admin currently has selected.
                        const tmpl = roleTemplates[newRole];
                        if (tmpl && tmpl.permissions) {
                          setFormData({
                            ...formData,
                            role: newRole,
                            custom_permissions: tmpl.permissions,
                            use_custom_permissions: true,
                          });
                        } else {
                          setFormData({ ...formData, role: newRole });
                        }
                      }}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      data-testid="admin-role-select"
                    >
                      {/* Legacy short roles (admin, manager, support, etc.) */}
                      {Object.entries(roles).map(([key, role]) => (
                        key !== 'super_admin' && (
                          <option key={`legacy-${key}`} value={key}>
                            {role.name} {role.description ? `- ${role.description}` : ''}
                          </option>
                        )
                      ))}
                      {/* Role templates from PERMISSION_MODULES + custom saved roles */}
                      {Object.entries(roleTemplates).map(([key, tmpl]) => (
                        key !== 'super_admin' && !roles[key] && (
                          <option key={`tmpl-${key}`} value={key}>
                            {tmpl.name}{tmpl.is_custom ? ' (Custom)' : ''}
                          </option>
                        )
                      ))}
                    </select>
                  </div>

                  {/* Custom Permissions Section - Module Based */}
                  <div className="border rounded-lg p-4 bg-gray-50">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Module Permissions
                        </label>
                        <p className="text-xs text-gray-500">
                          Select specific features this user can access
                        </p>
                      </div>
                      <label className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          checked={formData.use_custom_permissions}
                          onChange={(e) => setFormData({...formData, use_custom_permissions: e.target.checked})}
                          className="w-4 h-4"
                        />
                        <span className="text-gray-700">Use custom permissions</span>
                      </label>
                    </div>
                    
                    {formData.use_custom_permissions && (
                      <div className="space-y-3 max-h-96 overflow-y-auto">
                        {Object.entries(modulesByCategory).map(([category, modules]) => {
                          const catInfo = CATEGORY_INFO[category] || { label: category, color: 'text-gray-600', bg: 'bg-gray-50', border: 'border-gray-200' };
                          const isExpanded = expandedCategories[category] !== false;
                          
                          return (
                            <div key={category} className={`border ${catInfo.border} rounded-lg overflow-hidden`}>
                              <button
                                type="button"
                                onClick={() => setExpandedCategories(prev => ({...prev, [category]: !isExpanded}))}
                                className={`w-full flex items-center justify-between px-4 py-2 ${catInfo.bg} hover:opacity-80`}
                              >
                                <span className={`font-medium ${catInfo.color}`}>{catInfo.label}</span>
                                {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                              </button>
                              
                              {isExpanded && (
                                <div className="p-3 bg-white grid grid-cols-1 sm:grid-cols-2 gap-3">
                                  {modules.map(module => {
                                    const allSelected = hasAllPermissions(module.id, module.permissions);
                                    const someSelected = (formData.custom_permissions[module.id] || []).length > 0;
                                    const meta = MODULE_ICON_MAP[module.id] || { icon: Settings, color: 'bg-gray-400', description: 'Manage permissions for this module.' };
                                    const ModuleIcon = meta.icon;

                                    return (
                                      <div
                                        key={module.id}
                                        className={`bg-white rounded-lg shadow p-3 transition-all duration-200 border ${
                                          allSelected ? 'border-green-300' : someSelected ? 'border-blue-300' : 'border-gray-200'
                                        }`}
                                      >
                                        <div className="flex items-start gap-3">
                                          <button
                                            type="button"
                                            onClick={() => toggleAllModulePermissions(module.id, module.permissions)}
                                            className={`${meta.color} p-2 rounded-lg flex-shrink-0 hover:opacity-80 transition-opacity`}
                                            title="Toggle all permissions for this module"
                                          >
                                            <ModuleIcon className="w-5 h-5 text-white" />
                                          </button>
                                          <div className="flex-1 min-w-0">
                                            <div className="flex items-start justify-between gap-2 mb-1">
                                              <h4 className="text-sm font-semibold text-gray-900 truncate">{module.name}</h4>
                                              {allSelected && (
                                                <span className="px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded flex-shrink-0">
                                                  All
                                                </span>
                                              )}
                                              {!allSelected && someSelected && (
                                                <span className="px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded flex-shrink-0">
                                                  Partial
                                                </span>
                                              )}
                                            </div>
                                            <p className="text-xs text-gray-500 mb-2 line-clamp-2">{meta.description}</p>
                                            <div className="flex flex-wrap gap-1">
                                              {module.permissions.map(perm => {
                                                const isSelected = (formData.custom_permissions[module.id] || []).includes(perm);
                                                return (
                                                  <button
                                                    key={perm}
                                                    type="button"
                                                    onClick={() => togglePermission(module.id, perm)}
                                                    className={`px-2 py-0.5 text-xs rounded border transition-colors ${
                                                      isSelected
                                                        ? 'bg-blue-100 border-blue-300 text-blue-700'
                                                        : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
                                                    }`}
                                                  >
                                                    {perm}
                                                  </button>
                                                );
                                              })}
                                            </div>
                                          </div>
                                        </div>
                                      </div>
                                    );
                                  })}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}
                    
                    {formData.use_custom_permissions && getTotalSelectedPermissions() > 0 && (
                      <div className="mt-3 flex items-center justify-between border-t pt-3 flex-wrap gap-2">
                        <span className="text-xs text-blue-600">
                          {getTotalSelectedPermissions()} permission(s) selected across {Object.keys(formData.custom_permissions).filter(k => formData.custom_permissions[k].length > 0).length} module(s)
                        </span>
                        <div className="flex items-center gap-3">
                          <button
                            type="button"
                            onClick={saveAsCustomRole}
                            data-testid="save-as-custom-role-btn"
                            className="text-xs text-purple-700 bg-purple-50 hover:bg-purple-100 border border-purple-200 px-2 py-1 rounded"
                          >
                            💾 Save as Custom Role
                          </button>
                          <button
                            type="button"
                            onClick={() => setFormData({...formData, custom_permissions: {}})}
                            className="text-xs text-red-600 hover:underline"
                          >
                            Clear all
                          </button>
                        </div>
                      </div>
                    )}
                    
                    {!formData.use_custom_permissions && (
                      <div className="text-center py-4 text-gray-500 text-sm">
                        Using default permissions from selected role
                      </div>
                    )}
                  </div>

                  <div className="flex justify-end space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setShowCreateModal(false);
                        resetForm();
                      }}
                      className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Create Admin
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Edit Admin Modal */}
        {showEditModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <h2 className="text-2xl font-bold mb-6">Edit Admin: {selectedAdmin?.name}</h2>
                <form onSubmit={handleUpdateAdmin} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Email (cannot be changed)</label>
                    <input
                      type="email"
                      value={formData.email}
                      className="w-full px-4 py-2 border rounded-lg bg-gray-100"
                      disabled
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
                    <select
                      value={formData.role}
                      onChange={(e) => setFormData({...formData, role: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      disabled={selectedAdmin?.role === 'super_admin'}
                    >
                      {Object.entries(roles).map(([key, role]) => (
                        <option key={key} value={key}>
                          {role.name} - {role.description}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex justify-end space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setShowEditModal(false);
                        setSelectedAdmin(null);
                        resetForm();
                      }}
                      className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Update Admin
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminUserManagement;
