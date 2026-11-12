import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Store, Plus, Edit2, Trash2, Users, Settings, MapPin, Phone, Mail,
  ChevronRight, ChevronDown, Check, X, Eye, EyeOff, Shield, Building2,
  Package, ArrowRightLeft, FileText, ShoppingCart, Receipt, AlertCircle, Home
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import AdminHeader from './AdminHeader';
import { ALL_MODULES, MODULE_CATEGORIES } from './UnifiedDashboard';


// Default permissions for new stores
const DEFAULT_STORE_PERMISSIONS = {
  // Operations
  product_manager: true,
  orders_sales: true,
  inventory_stock: true,
  delivery_management: true,
  service_tickets: true,
  
  // Accounting & Finance
  accounting_billing: true,
  tally_import: true,
  purchase_orders: true,
  purchase_bills: true,
  gst_reports: true,
  compliance_audits: false,
  quotations: true,
  reports_exports: true,
  
  // Customer Management
  customer_crm: true,
  lead_management: false,
  expert_consultations: false,
  
  // Marketing
  combo_offers: false,
  promotions_themes: false,
  banner_management: false,
  marketing_campaigns: false,
  social_media: false,
  
  // Analytics
  analytics_dashboard: true,
  ai_agents_performance: false,
  marketing_analytics: false,
  
  // Configuration
  category_management: false,
  knowledge_base: false,
  document_numbering: false,
  seo_manager: false
};

const StoreManagement = () => {
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('stores');
  const [selectedStore, setSelectedStore] = useState(null);
  const [showCreateStore, setShowCreateStore] = useState(false);
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [showPermissions, setShowPermissions] = useState(false);
  const [showModulePermissions, setShowModulePermissions] = useState(false);
  const [storeUsers, setStoreUsers] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [modulePermissions, setModulePermissions] = useState({...DEFAULT_STORE_PERMISSIONS});

  // Form states
  const [storeForm, setStoreForm] = useState({
    name: '', code: '', address: '', city: '', state: '', pincode: '',
    phone: '', email: '', manager_name: '', is_warehouse: false,
    permissions: {...DEFAULT_STORE_PERMISSIONS}
  });
  const [userForm, setUserForm] = useState({
    email: '', password: '', first_name: '', last_name: '', phone: '', role: 'store_manager'
  });
  const [permissions, setPermissions] = useState({
    can_create_sales: true, can_create_purchases: true, can_create_expenses: true,
    can_view_reports: true, can_manage_stock: true, can_create_challans: true,
    can_view_other_stores: false, can_transfer_stock: true
  });
  const [showPassword, setShowPassword] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showEditUser, setShowEditUser] = useState(false);
  const [showEditStore, setShowEditStore] = useState(false);
  const [editStoreForm, setEditStoreForm] = useState({
    name: '', code: '', address: '', city: '', state: '', pincode: '',
    phone: '', email: '', manager_name: '', is_warehouse: false
  });

  useEffect(() => {
    fetchStores();
  }, []);

  useEffect(() => {
    if (selectedStore) {
      fetchStoreUsers(selectedStore.id);
    }
  }, [selectedStore]);

  // Populate form when editing a user
  useEffect(() => {
    if (selectedUser && showEditUser) {
      setUserForm({
        email: selectedUser.email || '',
        password: '',
        first_name: selectedUser.first_name || '',
        last_name: selectedUser.last_name || '',
        phone: selectedUser.phone || '',
        role: selectedUser.role || 'store_manager'
      });
    }
  }, [selectedUser, showEditUser]);

  const fetchStores = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      if (data.status === 'success') {
        setStores(data.stores);
      } else {
        setError(data.detail || 'Failed to load stores');
      }
    } catch (err) {
      console.error('Fetch stores error:', err);
      setError('Failed to load stores');
    } finally {
      setLoading(false);
    }
  };

  const fetchStoreUsers = async (storeId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/${storeId}/users`);
      const data = await response.json();
      if (data.status === 'success') {
        setStoreUsers(data.users);
      }
    } catch (err) {
      console.error('Failed to fetch users:', err);
    }
  };

  const handleCreateStore = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(storeForm)
      });
      const data = await response.json();
      if (response.ok && data.status === 'success') {
        setSuccess(`Store ${storeForm.name} created successfully!`);
        setShowCreateStore(false);
        setStoreForm({ name: '', code: '', address: '', city: '', state: '', pincode: '', phone: '', email: '', manager_name: '', is_warehouse: false });
        fetchStores();
      } else {
        setError(data.detail || 'Failed to create store');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  const handleEditStoreClick = (store) => {
    setSelectedStore(store);
    setEditStoreForm({
      name: store.name || '',
      code: store.code || '',
      address: store.address || '',
      city: store.city || '',
      state: store.state || '',
      pincode: store.pincode || '',
      phone: store.phone || '',
      email: store.email || '',
      manager_name: store.manager_name || '',
      is_warehouse: store.is_warehouse || false
    });
    setShowEditStore(true);
  };

  const handleUpdateStore = async (e) => {
    e.preventDefault();
    setError('');
    if (!selectedStore) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/${selectedStore.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editStoreForm)
      });
      const data = await response.json();
      if (response.ok && data.status === 'success') {
        setSuccess(`Store ${editStoreForm.name} updated successfully!`);
        setShowEditStore(false);
        setEditStoreForm({ name: '', code: '', address: '', city: '', state: '', pincode: '', phone: '', email: '', manager_name: '', is_warehouse: false });
        fetchStores();
      } else {
        setError(data.detail || 'Failed to update store');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setError('');
    if (!selectedStore) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/${selectedStore.id}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userForm)
      });
      const data = await response.json();
      if (response.ok && data.status === 'success') {
        setSuccess(`User ${userForm.email} created successfully!`);
        setShowCreateUser(false);
        setUserForm({ email: '', password: '', first_name: '', last_name: '', phone: '', role: 'store_manager' });
        fetchStoreUsers(selectedStore.id);
      } else {
        setError(data.detail || 'Failed to create user');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  const handleUpdatePermissions = async () => {
    if (!selectedStore) return;
    setError('');
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/${selectedStore.id}/permissions`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(permissions)
      });
      const data = await response.json();
      if (response.ok && data.status === 'success') {
        setSuccess('Permissions updated successfully!');
        setShowPermissions(false);
        fetchStores();
      } else {
        setError(data.detail || 'Failed to update permissions');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  const handleOpenModulePermissions = (store) => {
    setSelectedStore(store);
    // Load existing module_permissions or use defaults
    const existingPermissions = store.module_permissions || {...DEFAULT_STORE_PERMISSIONS};
    setModulePermissions(existingPermissions);
    setShowModulePermissions(true);
  };

  const handleSaveModulePermissions = async () => {
    if (!selectedStore) return;
    setError('');
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/${selectedStore.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ module_permissions: modulePermissions })
      });
      const data = await response.json();
      if (response.ok && data.status === 'success') {
        setSuccess('Module permissions updated successfully!');
        setShowModulePermissions(false);
        fetchStores();
      } else {
        setError(data.detail || 'Failed to update module permissions');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  const toggleModulePermission = (moduleId) => {
    setModulePermissions(prev => ({
      ...prev,
      [moduleId]: !prev[moduleId]
    }));
  };

  const selectAllModules = (category) => {
    const categoryModules = ALL_MODULES.filter(m => m.category === category);
    const newPermissions = {...modulePermissions};
    categoryModules.forEach(m => {
      if (m.category !== 'admin_only') {
        newPermissions[m.id] = true;
      }
    });
    setModulePermissions(newPermissions);
  };

  const deselectAllModules = (category) => {
    const categoryModules = ALL_MODULES.filter(m => m.category === category);
    const newPermissions = {...modulePermissions};
    categoryModules.forEach(m => {
      newPermissions[m.id] = false;
    });
    setModulePermissions(newPermissions);
  };

  const handleToggleStoreStatus = async (store) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/${store.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !store.is_active })
      });
      if (response.ok) {
        fetchStores();
        setSuccess(`Store ${store.is_active ? 'deactivated' : 'activated'} successfully!`);
      }
    } catch (err) {
      setError('Failed to update store status');
    }
  };

  const handleToggleUserStatus = async (user) => {
    if (!selectedStore) return;
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/${selectedStore.id}/users/${user.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: user.is_active === false ? true : false })
      });
      if (response.ok) {
        fetchStoreUsers(selectedStore.id);
        setSuccess(`User ${user.is_active === false ? 'enabled' : 'disabled'} successfully!`);
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to update user status');
      }
    } catch (err) {
      setError('Failed to update user status');
    }
  };

  const handleUpdateUser = async (e) => {
    e.preventDefault();
    if (!selectedStore || !selectedUser) return;
    setError('');
    
    try {
      const updateData = {
        first_name: userForm.first_name,
        last_name: userForm.last_name,
        phone: userForm.phone,
        role: userForm.role
      };
      
      // Only include password if it's been changed
      if (userForm.password && userForm.password.length >= 6) {
        updateData.password = userForm.password;
      }
      
      const response = await fetch(`${BACKEND_URL}/api/stores/${selectedStore.id}/users/${selectedUser.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData)
      });
      const data = await response.json();
      if (response.ok && data.status === 'success') {
        setSuccess(`User ${userForm.first_name} updated successfully!`);
        setShowEditUser(false);
        setSelectedUser(null);
        setUserForm({ email: '', password: '', first_name: '', last_name: '', phone: '', role: 'store_manager' });
        fetchStoreUsers(selectedStore.id);
      } else {
        setError(data.detail || 'Failed to update user');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  };

  const permissionLabels = {
    can_create_sales: { label: 'Create Sales Orders', icon: ShoppingCart, desc: 'Allow creating new sales invoices' },
    can_create_purchases: { label: 'Create Purchase Bills', icon: Receipt, desc: 'Allow recording purchase bills' },
    can_create_expenses: { label: 'Record Expenses', icon: FileText, desc: 'Allow recording store expenses' },
    can_view_reports: { label: 'View Reports', icon: FileText, desc: 'Access store reports and analytics' },
    can_manage_stock: { label: 'Manage Inventory', icon: Package, desc: 'Update stock levels and manage inventory' },
    can_create_challans: { label: 'Create Delivery Challans', icon: FileText, desc: 'Create and manage delivery challans' },
    can_view_other_stores: { label: 'View Other Stores', icon: Store, desc: 'View data from other stores' },
    can_transfer_stock: { label: 'Stock Transfers', icon: ArrowRightLeft, desc: 'Request/receive stock transfers' }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <AdminHeader 
        title="Store Management" 
        icon={Building2}
        breadcrumb={[{ label: 'Store Management' }]}
      />
      
      <div className="p-6">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Building2 className="w-8 h-8 text-teal-600" />
              Store Management
            </h1>
            <p className="text-gray-600 mt-1">Manage stores, users, and access permissions</p>
          </div>
          <button
            onClick={() => setShowCreateStore(true)}
            className="flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
            data-testid="create-store-btn"
          >
            <Plus className="w-5 h-5" />
            Add New Store
          </button>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3 text-red-700">
            <AlertCircle className="w-5 h-5" />
            {error}
            <button onClick={() => setError('')} className="ml-auto"><X className="w-4 h-4" /></button>
          </div>
        )}
        {success && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3 text-green-700">
            <Check className="w-5 h-5" />
            {success}
            <button onClick={() => setSuccess('')} className="ml-auto"><X className="w-4 h-4" /></button>
        </div>
      )}

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Store List */}
        <div className="lg:col-span-1 bg-white rounded-xl shadow-sm">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold text-gray-800">Stores ({stores.length})</h2>
          </div>
          <div className="divide-y max-h-[600px] overflow-y-auto">
            {stores.map((store) => (
              <div
                key={store.id}
                onClick={() => {
                  setSelectedStore(store);
                  setPermissions(store.permissions || {});
                }}
                className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                  selectedStore?.id === store.id ? 'bg-teal-50 border-l-4 border-teal-500' : ''
                }`}
                data-testid={`store-item-${store.code}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${store.is_warehouse ? 'bg-purple-100' : 'bg-teal-100'}`}>
                      {store.is_warehouse ? <Package className="w-5 h-5 text-purple-600" /> : <Store className="w-5 h-5 text-teal-600" />}
                    </div>
                    <div>
                      <p className="font-medium text-gray-800">{store.name}</p>
                      <p className="text-xs text-gray-500">{store.code} • {store.city}</p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    store.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  }`}>
                    {store.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                  <span>{store.total_products || 0} products</span>
                  <span>{store.total_stock || 0} units</span>
                </div>
              </div>
            ))}
            {stores.length === 0 && !loading && (
              <div className="p-8 text-center text-gray-500">
                No stores found. Create your first store!
              </div>
            )}
          </div>
        </div>

        {/* Store Details */}
        <div className="lg:col-span-2">
          {selectedStore ? (
            <div className="space-y-6">
              {/* Store Info Card */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-xl ${selectedStore.is_warehouse ? 'bg-purple-100' : 'bg-teal-100'}`}>
                      {selectedStore.is_warehouse ? <Package className="w-8 h-8 text-purple-600" /> : <Store className="w-8 h-8 text-teal-600" />}
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-800">{selectedStore.name}</h2>
                      <p className="text-gray-500">Code: {selectedStore.code}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleEditStoreClick(selectedStore)}
                      className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
                      title="Edit Store"
                      data-testid="edit-store-btn"
                    >
                      <Edit2 className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleOpenModulePermissions(selectedStore)}
                      className="p-2 text-blue-500 hover:bg-blue-50 rounded-lg"
                      title="Module Permissions"
                    >
                      <Package className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => setShowPermissions(true)}
                      className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
                      title="User Permissions"
                    >
                      <Shield className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleToggleStoreStatus(selectedStore)}
                      className={`px-3 py-1 text-sm rounded-lg ${
                        selectedStore.is_active ? 'bg-red-100 text-red-700 hover:bg-red-200' : 'bg-green-100 text-green-700 hover:bg-green-200'
                      }`}
                    >
                      {selectedStore.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center gap-2 text-gray-600">
                    <MapPin className="w-4 h-4" />
                    <span>{selectedStore.address}, {selectedStore.city}, {selectedStore.state} - {selectedStore.pincode}</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <Phone className="w-4 h-4" />
                    <span>{selectedStore.phone || 'N/A'}</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <Mail className="w-4 h-4" />
                    <span>{selectedStore.email || 'N/A'}</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <Users className="w-4 h-4" />
                    <span>Manager: {selectedStore.manager_name || 'Not Assigned'}</span>
                  </div>
                </div>
              </div>

              {/* Store Users */}
              <div className="bg-white rounded-xl shadow-sm">
                <div className="p-4 border-b flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-800">Store Users</h3>
                  <button
                    onClick={() => setShowCreateUser(true)}
                    className="flex items-center gap-2 px-3 py-1.5 bg-teal-600 text-white text-sm rounded-lg hover:bg-teal-700"
                    data-testid="add-store-user-btn"
                  >
                    <Plus className="w-4 h-4" />
                    Add User
                  </button>
                </div>
                <div className="divide-y">
                  {storeUsers.map((user) => (
                    <div key={user.id} className="p-4 flex items-center justify-between hover:bg-gray-50">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          user.is_active !== false ? 'bg-teal-100' : 'bg-gray-200'
                        }`}>
                          <span className={`font-medium ${user.is_active !== false ? 'text-teal-600' : 'text-gray-400'}`}>
                            {user.first_name?.[0]}{user.last_name?.[0]}
                          </span>
                        </div>
                        <div>
                          <p className={`font-medium ${user.is_active !== false ? 'text-gray-800' : 'text-gray-400'}`}>
                            {user.first_name} {user.last_name}
                            {user.is_active === false && <span className="ml-2 text-xs text-red-500">(Disabled)</span>}
                          </p>
                          <p className="text-sm text-gray-500">{user.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            user.role === 'store_manager' ? 'bg-purple-100 text-purple-700' :
                            user.role === 'store_accountant' ? 'bg-blue-100 text-blue-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {user.role?.replace('_', ' ')}
                          </span>
                          <p className="text-xs text-gray-500 mt-1">
                            Last login: {formatDate(user.last_login)}
                          </p>
                        </div>
                        {/* User Actions */}
                        <div className="flex items-center gap-1">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedUser(user);
                              setShowEditUser(true);
                            }}
                            className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
                            title="Edit User"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleToggleUserStatus(user);
                            }}
                            className={`p-2 rounded-lg ${
                              user.is_active !== false 
                                ? 'text-red-500 hover:bg-red-50' 
                                : 'text-green-500 hover:bg-green-50'
                            }`}
                            title={user.is_active !== false ? 'Disable User' : 'Enable User'}
                          >
                            {user.is_active !== false ? <X className="w-4 h-4" /> : <Check className="w-4 h-4" />}
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                  {storeUsers.length === 0 && (
                    <div className="p-8 text-center text-gray-500">
                      No users assigned to this store
                    </div>
                  )}
                </div>
              </div>

              {/* Current Permissions */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-800">Store Permissions</h3>
                  <button
                    onClick={() => setShowPermissions(true)}
                    className="flex items-center gap-2 px-3 py-1.5 bg-teal-600 text-white text-sm rounded-lg hover:bg-teal-700"
                    data-testid="edit-permissions-btn"
                  >
                    <Edit2 className="w-4 h-4" />
                    Edit Permissions
                  </button>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {Object.entries(permissionLabels).map(([key, { label, icon: Icon }]) => (
                    <div
                      key={key}
                      className={`p-3 rounded-lg border ${
                        selectedStore.permissions?.[key] ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        {selectedStore.permissions?.[key] ? (
                          <Check className="w-4 h-4 text-green-600" />
                        ) : (
                          <X className="w-4 h-4 text-gray-400" />
                        )}
                        <span className="text-sm font-medium">{label}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm p-12 text-center">
              <Store className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-700 mb-2">Select a Store</h3>
              <p className="text-gray-500">Choose a store from the list to view details and manage users</p>
            </div>
          )}
        </div>
      </div>

      {/* Create Store Modal */}
      {showCreateStore && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-800">Create New Store</h2>
              <button onClick={() => setShowCreateStore(false)} className="p-2 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreateStore} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Store Name *</label>
                  <input
                    type="text"
                    value={storeForm.name}
                    onChange={(e) => setStoreForm({...storeForm, name: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    placeholder="MG Road Store"
                    required
                    data-testid="store-name-input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Store Code *</label>
                  <input
                    type="text"
                    value={storeForm.code}
                    onChange={(e) => setStoreForm({...storeForm, code: e.target.value.toUpperCase()})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    placeholder="ST001 or BLR01"
                    required
                    data-testid="store-code-input"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Address *</label>
                <input
                  type="text"
                  value={storeForm.address}
                  onChange={(e) => setStoreForm({...storeForm, address: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                  placeholder="123 Main Street"
                  required
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">City *</label>
                  <input
                    type="text"
                    value={storeForm.city}
                    onChange={(e) => setStoreForm({...storeForm, city: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    placeholder="Bangalore"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">State *</label>
                  <input
                    type="text"
                    value={storeForm.state}
                    onChange={(e) => setStoreForm({...storeForm, state: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    placeholder="Karnataka"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Pincode *</label>
                  <input
                    type="text"
                    value={storeForm.pincode}
                    onChange={(e) => setStoreForm({...storeForm, pincode: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    placeholder="560001"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                  <input
                    type="tel"
                    value={storeForm.phone}
                    onChange={(e) => setStoreForm({...storeForm, phone: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    placeholder="+91 9876543210"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={storeForm.email}
                    onChange={(e) => setStoreForm({...storeForm, email: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    placeholder="store@adityaretail.com"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Manager Name</label>
                  <input
                    type="text"
                    value={storeForm.manager_name}
                    onChange={(e) => setStoreForm({...storeForm, manager_name: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    placeholder="John Doe"
                  />
                </div>
                <div className="flex items-center pt-6">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={storeForm.is_warehouse}
                      onChange={(e) => setStoreForm({...storeForm, is_warehouse: e.target.checked})}
                      className="w-4 h-4 rounded text-purple-600"
                    />
                    <span className="text-sm text-gray-700">This is a Warehouse (not retail store)</span>
                  </label>
                </div>

                {/* Warehouse Features - Show when warehouse is checked */}
                {storeForm.is_warehouse && (
                  <div className="mt-4 p-4 bg-purple-50 rounded-lg border border-purple-200">
                    <h4 className="font-semibold text-purple-800 mb-3 flex items-center gap-2">
                      <Package className="w-4 h-4" />
                      Warehouse Features (Auto-enabled)
                    </h4>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="flex items-center gap-2 text-purple-700">
                        <Check className="w-4 h-4 text-green-600" />
                        Purchase Invoice Entry
                      </div>
                      <div className="flex items-center gap-2 text-purple-700">
                        <Check className="w-4 h-4 text-green-600" />
                        Delivery Challan Creation
                      </div>
                      <div className="flex items-center gap-2 text-purple-700">
                        <Check className="w-4 h-4 text-green-600" />
                        Delivery Team Assignment
                      </div>
                      <div className="flex items-center gap-2 text-purple-700">
                        <Check className="w-4 h-4 text-green-600" />
                        SO to Invoice Conversion
                      </div>
                      <div className="flex items-center gap-2 text-purple-700">
                        <Check className="w-4 h-4 text-green-600" />
                        Stock Transfer Management
                      </div>
                      <div className="flex items-center gap-2 text-purple-700">
                        <Check className="w-4 h-4 text-green-600" />
                        Damaged Goods Entry
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setShowCreateStore(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700"
                  data-testid="submit-create-store"
                >
                  Create Store
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Store Modal */}
      {showEditStore && selectedStore && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-800">Edit Store: {selectedStore.name}</h2>
              <button onClick={() => setShowEditStore(false)} className="p-2 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleUpdateStore} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Store Name *</label>
                  <input
                    type="text"
                    value={editStoreForm.name}
                    onChange={(e) => setEditStoreForm({...editStoreForm, name: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    required
                    data-testid="edit-store-name-input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Store Code *</label>
                  <input
                    type="text"
                    value={editStoreForm.code}
                    onChange={(e) => setEditStoreForm({...editStoreForm, code: e.target.value.toUpperCase()})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    required
                    data-testid="edit-store-code-input"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Address *</label>
                <input
                  type="text"
                  value={editStoreForm.address}
                  onChange={(e) => setEditStoreForm({...editStoreForm, address: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                  required
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">City *</label>
                  <input
                    type="text"
                    value={editStoreForm.city}
                    onChange={(e) => setEditStoreForm({...editStoreForm, city: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">State *</label>
                  <input
                    type="text"
                    value={editStoreForm.state}
                    onChange={(e) => setEditStoreForm({...editStoreForm, state: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Pincode *</label>
                  <input
                    type="text"
                    value={editStoreForm.pincode}
                    onChange={(e) => setEditStoreForm({...editStoreForm, pincode: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                  <input
                    type="tel"
                    value={editStoreForm.phone}
                    onChange={(e) => setEditStoreForm({...editStoreForm, phone: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={editStoreForm.email}
                    onChange={(e) => setEditStoreForm({...editStoreForm, email: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Manager Name</label>
                <input
                  type="text"
                  value={editStoreForm.manager_name}
                  onChange={(e) => setEditStoreForm({...editStoreForm, manager_name: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="edit-is-warehouse"
                  checked={editStoreForm.is_warehouse}
                  onChange={(e) => setEditStoreForm({...editStoreForm, is_warehouse: e.target.checked})}
                  className="w-4 h-4 text-teal-600 rounded focus:ring-teal-500"
                />
                <label htmlFor="edit-is-warehouse" className="text-sm text-gray-700">This is a warehouse/distribution center</label>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setShowEditStore(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700"
                  data-testid="submit-edit-store"
                >
                  Update Store
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Create User Modal */}
      {showCreateUser && selectedStore && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="p-6 border-b flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-800">Add Store User</h2>
                <p className="text-sm text-gray-500">{selectedStore.name}</p>
              </div>
              <button onClick={() => setShowCreateUser(false)} className="p-2 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreateUser} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">First Name *</label>
                  <input
                    type="text"
                    value={userForm.first_name}
                    onChange={(e) => setUserForm({...userForm, first_name: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    required
                    data-testid="user-firstname-input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Last Name *</label>
                  <input
                    type="text"
                    value={userForm.last_name}
                    onChange={(e) => setUserForm({...userForm, last_name: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
                <input
                  type="email"
                  value={userForm.email}
                  onChange={(e) => setUserForm({...userForm, email: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                  placeholder="user@store.adityaretail.com"
                  required
                  data-testid="user-email-input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Password *</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={userForm.password}
                    onChange={(e) => setUserForm({...userForm, password: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 pr-10"
                    placeholder="Min 6 characters"
                    minLength={6}
                    required
                    data-testid="user-password-input"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                <input
                  type="tel"
                  value={userForm.phone}
                  onChange={(e) => setUserForm({...userForm, phone: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                  placeholder="+91 9876543210"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role *</label>
                <select
                  value={userForm.role}
                  onChange={(e) => setUserForm({...userForm, role: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                  data-testid="user-role-select"
                >
                  <option value="store_manager">Store Manager</option>
                  <option value="store_staff">Store Staff</option>
                  <option value="store_accountant">Store Accountant</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setShowCreateUser(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700"
                  data-testid="submit-create-user"
                >
                  Create User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Permissions Modal */}
      {showPermissions && selectedStore && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg">
            <div className="p-6 border-b flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-800">Store Permissions</h2>
                <p className="text-sm text-gray-500">{selectedStore.name}</p>
              </div>
              <button onClick={() => setShowPermissions(false)} className="p-2 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-3 max-h-[60vh] overflow-y-auto">
              {Object.entries(permissionLabels).map(([key, { label, icon: Icon, desc }]) => (
                <label
                  key={key}
                  className={`flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                    permissions[key] ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={permissions[key] || false}
                    onChange={(e) => setPermissions({...permissions, [key]: e.target.checked})}
                    className="w-5 h-5 rounded text-teal-600 mt-0.5"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <Icon className="w-4 h-4 text-gray-600" />
                      <span className="font-medium text-gray-800">{label}</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{desc}</p>
                  </div>
                </label>
              ))}
            </div>
            <div className="p-6 border-t flex justify-end gap-3">
              <button
                onClick={() => setShowPermissions(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleUpdatePermissions}
                className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700"
                data-testid="save-permissions-btn"
              >
                Save Permissions
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit User Modal */}
      {showEditUser && selectedStore && selectedUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="p-6 border-b flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-800">Edit User</h2>
                <p className="text-sm text-gray-500">{selectedUser.email}</p>
              </div>
              <button onClick={() => { setShowEditUser(false); setSelectedUser(null); }} className="p-2 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleUpdateUser} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">First Name *</label>
                  <input
                    type="text"
                    value={userForm.first_name}
                    onChange={(e) => setUserForm({...userForm, first_name: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Last Name *</label>
                  <input
                    type="text"
                    value={userForm.last_name}
                    onChange={(e) => setUserForm({...userForm, last_name: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">New Password (leave blank to keep current)</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={userForm.password}
                    onChange={(e) => setUserForm({...userForm, password: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 pr-10"
                    placeholder="Min 6 characters"
                    minLength={6}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                <input
                  type="tel"
                  value={userForm.phone}
                  onChange={(e) => setUserForm({...userForm, phone: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                  placeholder="+91 9876543210"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role *</label>
                <select
                  value={userForm.role}
                  onChange={(e) => setUserForm({...userForm, role: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                >
                  <option value="store_manager">Store Manager</option>
                  <option value="store_staff">Store Staff</option>
                  <option value="store_accountant">Store Accountant</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => { setShowEditUser(false); setSelectedUser(null); }}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700"
                >
                  Update User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Module Permissions Modal */}
      {showModulePermissions && selectedStore && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b flex items-center justify-between bg-gradient-to-r from-blue-600 to-blue-700 text-white">
              <div>
                <h2 className="text-xl font-bold">Module Permissions</h2>
                <p className="text-blue-100 text-sm">{selectedStore.name} ({selectedStore.code})</p>
              </div>
              <button onClick={() => setShowModulePermissions(false)} className="p-2 hover:bg-white/10 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6">
              <p className="text-gray-600 mb-6">
                Select which modules this store can access. These will appear in the store's dashboard.
              </p>
              
              {Object.entries(MODULE_CATEGORIES).map(([categoryKey, categoryInfo]) => {
                // Skip admin_only category
                if (categoryKey === 'admin_only') return null;
                
                const categoryModules = ALL_MODULES.filter(m => m.category === categoryKey);
                if (categoryModules.length === 0) return null;
                
                const enabledCount = categoryModules.filter(m => modulePermissions[m.id]).length;
                
                return (
                  <div key={categoryKey} className="mb-6">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className={`font-semibold ${categoryInfo.color}`}>
                        {categoryInfo.label}
                        <span className="ml-2 text-xs font-normal text-gray-400">
                          ({enabledCount}/{categoryModules.length} enabled)
                        </span>
                      </h3>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => selectAllModules(categoryKey)}
                          className="text-xs text-blue-600 hover:underline"
                        >
                          Select All
                        </button>
                        <span className="text-gray-300">|</span>
                        <button
                          type="button"
                          onClick={() => deselectAllModules(categoryKey)}
                          className="text-xs text-gray-500 hover:underline"
                        >
                          Deselect All
                        </button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {categoryModules.map(module => {
                        const Icon = module.icon;
                        const isEnabled = modulePermissions[module.id];
                        
                        return (
                          <label
                            key={module.id}
                            className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-all ${
                              isEnabled 
                                ? 'border-blue-300 bg-blue-50' 
                                : 'border-gray-200 hover:border-gray-300'
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={isEnabled || false}
                              onChange={() => toggleModulePermission(module.id)}
                              className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                            />
                            <div className={`w-10 h-10 ${module.color} rounded-lg flex items-center justify-center flex-shrink-0`}>
                              <Icon className="w-5 h-5 text-white" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="font-medium text-gray-800 text-sm">{module.title}</p>
                              <p className="text-xs text-gray-500 line-clamp-1">{module.description}</p>
                            </div>
                          </label>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
            
            <div className="p-4 border-t bg-gray-50 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowModulePermissions(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveModulePermissions}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Save Permissions
              </button>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
};

export default StoreManagement;
