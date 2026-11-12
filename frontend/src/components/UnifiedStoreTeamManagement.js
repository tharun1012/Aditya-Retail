import React, { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Building2, Users, Plus, Edit2, Trash2, Settings, MapPin, Phone, Mail,
  ChevronRight, ChevronDown, Check, X, Eye, EyeOff, Shield, Package,
  Hash, Save, RefreshCw, FileText, UserCog, Store, AlertCircle,
  ChevronLeft, Truck
} from 'lucide-react';

// ============ DELIVERY PERSONNEL TAB COMPONENT ============
const DeliveryPersonnelTab = () => {
  const [deliveryPersons, setDeliveryPersons] = React.useState([]);
  const [showModal, setShowModal] = React.useState(false);
  const [editingPerson, setEditingPerson] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [formData, setFormData] = React.useState({
    full_name: '', email: '', password: '', phone: '', vehicle_number: '', address: ''
  });

  React.useEffect(() => {
    fetchDeliveryPersons();
  }, []);

  const fetchDeliveryPersons = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/delivery-persons/list`);
      const data = await response.json();
      if (response.ok) {
        setDeliveryPersons(data.delivery_persons || []);
      }
    } catch (error) {
      console.error('Error fetching delivery persons:', error);
    }
  };

  const resetForm = () => {
    setFormData({ full_name: '', email: '', password: '', phone: '', vehicle_number: '', address: '' });
    setEditingPerson(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const url = editingPerson
        ? `${BACKEND_URL}/api/auth/delivery-person/${editingPerson.id}/update`
        : `${BACKEND_URL}/api/auth/delivery-person/create-from-warehouse`;
      
      const method = editingPerson ? 'PUT' : 'POST';
      const payload = { ...formData };
      if (editingPerson && !payload.password) delete payload.password;

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (response.ok && data.status === 'success') {
        alert(editingPerson ? 'Updated successfully!' : 'Created successfully!');
        setShowModal(false);
        resetForm();
        fetchDeliveryPersons();
      } else {
        alert(data.detail || 'Operation failed');
      }
    } catch (error) {
      alert('Operation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (person) => {
    setFormData({
      full_name: person.full_name || '',
      email: person.email || '',
      password: '',
      phone: person.phone || '',
      vehicle_number: person.vehicle_number || '',
      address: person.address || ''
    });
    setEditingPerson(person);
    setShowModal(true);
  };

  const handleDeactivate = async (person) => {
    if (!window.confirm(`Deactivate ${person.full_name}?`)) return;
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/delivery-person/${person.id}/delete`, { method: 'DELETE' });
      const data = await response.json();
      if (response.ok && data.status === 'success') {
        alert('Deactivated!');
        fetchDeliveryPersons();
      }
    } catch (error) {
      alert('Failed to deactivate');
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm">
      <div className="p-4 border-b flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
          <Truck className="w-5 h-5 text-purple-600" />
          Delivery Personnel
        </h2>
        <button
          onClick={() => { resetForm(); setShowModal(true); }}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Delivery Person
        </button>
      </div>
      
      <div className="divide-y">
        {deliveryPersons.map(person => (
          <div key={person.id} className="p-4 flex items-center justify-between hover:bg-gray-50">
            <div className="flex items-center gap-4">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                person.is_active !== false ? 'bg-purple-100' : 'bg-gray-200'
              }`}>
                <Truck className={`w-6 h-6 ${person.is_active !== false ? 'text-purple-600' : 'text-gray-400'}`} />
              </div>
              <div>
                <p className={`font-medium ${person.is_active !== false ? 'text-gray-800' : 'text-gray-400'}`}>
                  {person.full_name}
                  {person.is_active === false && <span className="ml-2 text-xs text-red-500">(Inactive)</span>}
                </p>
                <p className="text-sm text-gray-500">{person.phone} • {person.email}</p>
                {person.vehicle_number && <p className="text-xs text-purple-600">{person.vehicle_number}</p>}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={() => handleEdit(person)} className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg">
                <Edit2 className="w-4 h-4" />
              </button>
              {person.is_active !== false && (
                <button onClick={() => handleDeactivate(person)} className="p-2 text-red-600 hover:bg-red-50 rounded-lg">
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        ))}
        {deliveryPersons.length === 0 && (
          <div className="p-12 text-center text-gray-500">
            <Truck className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p>No delivery personnel</p>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full">
            <div className="p-4 border-b bg-purple-600 text-white flex justify-between items-center rounded-t-xl">
              <h3 className="font-bold">{editingPerson ? 'Edit' : 'Add'} Delivery Person</h3>
              <button onClick={() => { setShowModal(false); resetForm(); }} className="p-1 hover:bg-purple-700 rounded">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-4 space-y-3">
              <input type="text" placeholder="Full Name *" required value={formData.full_name}
                onChange={e => setFormData({...formData, full_name: e.target.value})}
                className="w-full px-3 py-2 border rounded-lg" />
              <div className="grid grid-cols-2 gap-3">
                <input type="email" placeholder="Email *" required value={formData.email}
                  onChange={e => setFormData({...formData, email: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg" />
                <input type="password" placeholder={editingPerson ? "New Password (optional)" : "Password *"} 
                  required={!editingPerson} value={formData.password}
                  onChange={e => setFormData({...formData, password: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <input type="tel" placeholder="Phone *" required value={formData.phone}
                  onChange={e => setFormData({...formData, phone: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg" />
                <input type="text" placeholder="Vehicle Number" value={formData.vehicle_number}
                  onChange={e => setFormData({...formData, vehicle_number: e.target.value.toUpperCase()})}
                  className="w-full px-3 py-2 border rounded-lg" />
              </div>
              <textarea placeholder="Address" value={formData.address} rows={2}
                onChange={e => setFormData({...formData, address: e.target.value})}
                className="w-full px-3 py-2 border rounded-lg" />
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => { setShowModal(false); resetForm(); }}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50">Cancel</button>
                <button type="submit" disabled={loading}
                  className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50">
                  {loading ? 'Saving...' : (editingPerson ? 'Update' : 'Create')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};


// Category labels for permissions
const CATEGORY_INFO = {
  operations: { label: 'Operations', color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200' },
  accounting: { label: 'Accounting & Finance', color: 'text-teal-600', bg: 'bg-teal-50', border: 'border-teal-200' },
  customers: { label: 'Customer Management', color: 'text-purple-600', bg: 'bg-purple-50', border: 'border-purple-200' },
  marketing: { label: 'Marketing', color: 'text-pink-600', bg: 'bg-pink-50', border: 'border-pink-200' },
  analytics: { label: 'Analytics', color: 'text-indigo-600', bg: 'bg-indigo-50', border: 'border-indigo-200' },
  config: { label: 'Configuration', color: 'text-gray-600', bg: 'bg-gray-50', border: 'border-gray-200' },
  admin: { label: 'Admin Only', color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200' }
};

const LEVEL_INFO = {
  admin: { label: 'Admin Level', color: 'bg-purple-100 text-purple-800', icon: '👑' },
  manager: { label: 'Manager Level', color: 'bg-blue-100 text-blue-800', icon: '📋' },
  staff: { label: 'Staff Level', color: 'bg-green-100 text-green-800', icon: '👤' },
  custom: { label: 'Custom Role', color: 'bg-amber-100 text-amber-800', icon: '⚙️' }
};

const UnifiedStoreTeamManagement = () => {
  // Main state
  const [activeView, setActiveView] = useState('stores'); // 'stores' or 'store-detail'
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Store detail tabs
  const [activeTab, setActiveTab] = useState('info'); // 'info', 'permissions', 'documents', 'users'

  // Modal states
  const [showCreateStore, setShowCreateStore] = useState(false);
  const [showEditStore, setShowEditStore] = useState(false);
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [showEditUser, setShowEditUser] = useState(false);
  const [showCreateCustomRole, setShowCreateCustomRole] = useState(false);
  
  // Form states
  const [storeForm, setStoreForm] = useState({
    name: '', code: '', address: '', city: '', state: '', pincode: '',
    phone: '', email: '', manager_name: '', is_warehouse: false,
    // Document-related fields
    gst_number: '', pan_number: '', tagline: '',
    invoice_prefix: '', so_prefix: '',
    // Store Manager Login Credentials
    create_manager_login: false,
    manager_email: '',
    manager_password: '',
    manager_first_name: '',
    manager_last_name: ''
  });
  
  // User management
  const [storeUsers, setStoreUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userForm, setUserForm] = useState({
    email: '', password: '', first_name: '', last_name: '', phone: '', 
    role: 'sales_staff', customPermissions: {}
  });
  const [showPassword, setShowPassword] = useState(false);

  // Permissions data
  const [roleTemplates, setRoleTemplates] = useState({});
  const [customRoles, setCustomRoles] = useState([]);
  const [permissionModules, setPermissionModules] = useState({});
  const [modulesByCategory, setModulesByCategory] = useState({});
  const [rolesByLevel, setRolesByLevel] = useState({});
  const [expandedCategories, setExpandedCategories] = useState({});
  
  // Store module permissions
  const [storeModulePermissions, setStoreModulePermissions] = useState({});
  
  // Document numbering
  const [documentConfig, setDocumentConfig] = useState(null);
  const [savingDocument, setSavingDocument] = useState(false);

  // Custom role form
  const [customRoleForm, setCustomRoleForm] = useState({
    name: '', description: '', level: 'staff', permissions: {}
  });

  // Fetch initial data
  useEffect(() => {
    fetchStores();
    fetchRolesAndPermissions();
    fetchCustomRoles();
  }, []);

  // Fetch store users when store is selected
  useEffect(() => {
    if (selectedStore) {
      fetchStoreUsers(selectedStore.id);
      fetchDocumentConfig(selectedStore.id);
    }
  }, [selectedStore]);

  const fetchStores = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/stores/`);
      const data = await response.json();
      if (data.status === 'success') {
        setStores(data.stores || []);
      }
    } catch (err) {
      setError('Failed to load stores');
    } finally {
      setLoading(false);
    }
  };

  const fetchRolesAndPermissions = async () => {
    try {
      const [rolesRes, permsRes, categoryRes, levelRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/admin/management/roles/templates`),
        fetch(`${BACKEND_URL}/api/admin/management/permissions/modules`),
        fetch(`${BACKEND_URL}/api/admin/management/permissions/by-category`),
        fetch(`${BACKEND_URL}/api/admin/management/roles/by-level`)
      ]);

      const [rolesData, permsData, categoryData, levelData] = await Promise.all([
        rolesRes.json(), permsRes.json(), categoryRes.json(), levelRes.json()
      ]);

      setRoleTemplates(rolesData.templates || {});
      setPermissionModules(permsData.modules || {});
      setModulesByCategory(categoryData.categories || {});
      setRolesByLevel(levelData.roles || {});

      // Expand all categories by default
      const expanded = {};
      Object.keys(categoryData.categories || {}).forEach(cat => {
        expanded[cat] = true;
      });
      setExpandedCategories(expanded);
    } catch (err) {
      console.error('Failed to fetch roles/permissions:', err);
    }
  };

  const fetchCustomRoles = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/management/custom-roles`);
      if (response.ok) {
        const data = await response.json();
        setCustomRoles(data.roles || []);
      }
    } catch (err) {
      console.error('Failed to fetch custom roles:', err);
    }
  };

  const fetchStoreUsers = async (storeId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/${storeId}/users`);
      const data = await response.json();
      if (data.status === 'success') {
        setStoreUsers(data.users || []);
      }
    } catch (err) {
      console.error('Failed to fetch store users:', err);
    }
  };

  const fetchDocumentConfig = async (storeId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/document-numbering/config?store_id=${storeId}`);
      if (response.ok) {
        const data = await response.json();
        setDocumentConfig(data.config);
      } else if (response.status === 404) {
        // Initialize numbering
        const initRes = await fetch(`${BACKEND_URL}/api/document-numbering/initialize/${storeId}`, { method: 'POST' });
        if (initRes.ok) {
          const initData = await initRes.json();
          setDocumentConfig(initData.config);
        }
      }
    } catch (err) {
      console.error('Failed to fetch document config:', err);
    }
  };

  // Store CRUD
  const handleCreateStore = async (e) => {
    e.preventDefault();
    setError('');
    try {
      // First create the store
      const storeData = {
        name: storeForm.name,
        code: storeForm.code,
        address: storeForm.address,
        city: storeForm.city,
        state: storeForm.state,
        pincode: storeForm.pincode,
        phone: storeForm.phone,
        email: storeForm.email,
        manager_name: storeForm.manager_name,
        is_warehouse: storeForm.is_warehouse,
        // Tax & Document fields
        gst_number: storeForm.gst_number || null,
        pan_number: storeForm.pan_number || null,
        tagline: storeForm.tagline || null,
        invoice_prefix: storeForm.invoice_prefix || null,
        so_prefix: storeForm.so_prefix || null
      };
      
      const response = await fetch(`${BACKEND_URL}/api/stores/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(storeData)
      });
      const data = await response.json();
      
      if (response.ok && data.status === 'success') {
        const newStoreId = data.store_id;  // Fixed: use store_id from response
        
        // If create_manager_login is checked, create the manager user
        if (storeForm.create_manager_login && storeForm.manager_email && storeForm.manager_password) {
          try {
            const userResponse = await fetch(`${BACKEND_URL}/api/stores/${newStoreId}/users`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                email: storeForm.manager_email,
                password: storeForm.manager_password,
                first_name: storeForm.manager_first_name || storeForm.manager_name?.split(' ')[0] || 'Store',
                last_name: storeForm.manager_last_name || storeForm.manager_name?.split(' ')[1] || 'Manager',
                phone: storeForm.phone,
                role: 'store_manager'
              })
            });
            
            const userData = await userResponse.json();
            if (userResponse.ok && userData.status === 'success') {
              setSuccess(`Store "${storeForm.name}" created with manager login: ${storeForm.manager_email}`);
            } else {
              setSuccess(`Store created! But failed to create manager login: ${userData.detail || 'Unknown error'}`);
            }
          } catch (userErr) {
            setSuccess(`Store created! But failed to create manager login.`);
          }
        } else {
          setSuccess(`Store "${storeForm.name}" created successfully!`);
        }
        
        setShowCreateStore(false);
        resetStoreForm();
        fetchStores();
      } else {
        setError(data.detail || 'Failed to create store');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  const handleUpdateStore = async (e) => {
    e.preventDefault();
    if (!selectedStore) return;
    setError('');
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/${selectedStore.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(storeForm)
      });
      const data = await response.json();
      if (response.ok && data.status === 'success') {
        setSuccess(`Store "${storeForm.name}" updated!`);
        setShowEditStore(false);
        fetchStores();
        // Update selected store
        setSelectedStore({ ...selectedStore, ...storeForm });
      } else {
        setError(data.detail || 'Failed to update store');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  const handleDeleteStore = async (store) => {
    if (!window.confirm(`Are you sure you want to delete "${store.name}"?\n\nThis will also delete all team members associated with this store. This action cannot be undone.`)) {
      return;
    }
    
    setError('');
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/${store.id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      if (response.ok && data.status === 'success') {
        setSuccess(`Store "${store.name}" deleted successfully!`);
        setSelectedStore(null);
        // Force refresh the stores list
        setStores(prev => prev.filter(s => s.id !== store.id));
        // Also fetch fresh data from server
        setTimeout(() => fetchStores(), 500);
      } else {
        setError(data.detail || 'Failed to delete store');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  const handleSaveStorePermissions = async () => {
    if (!selectedStore) return;
    setError('');
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/${selectedStore.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ module_permissions: storeModulePermissions })
      });
      const data = await response.json();
      if (response.ok && data.status === 'success') {
        setSuccess('Store permissions updated!');
        fetchStores();
      } else {
        setError(data.detail || 'Failed to update permissions');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  // User CRUD
  const handleCreateUser = async (e) => {
    e.preventDefault();
    if (!selectedStore) return;
    setError('');
    try {
      const response = await fetch(`${BACKEND_URL}/api/stores/${selectedStore.id}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...userForm,
          permissions: userForm.customPermissions
        })
      });
      const data = await response.json();
      if (response.ok && data.status === 'success') {
        setSuccess(`User "${userForm.email}" created!`);
        setShowCreateUser(false);
        resetUserForm();
        fetchStoreUsers(selectedStore.id);
      } else {
        setError(data.detail || 'Failed to create user');
      }
    } catch (err) {
      setError('Connection error');
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
        role: userForm.role,
        permissions: userForm.customPermissions
      };
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
        setSuccess(`User updated!`);
        setShowEditUser(false);
        setSelectedUser(null);
        resetUserForm();
        fetchStoreUsers(selectedStore.id);
      } else {
        setError(data.detail || 'Failed to update user');
      }
    } catch (err) {
      setError('Connection error');
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
        setSuccess(`User ${user.is_active === false ? 'enabled' : 'disabled'}!`);
      }
    } catch (err) {
      setError('Failed to update user status');
    }
  };

  // Document numbering
  const handleUpdateDocumentConfig = async (docType, field, value) => {
    if (!selectedStore || !documentConfig) return;
    setSavingDocument(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/document-numbering/config/${selectedStore.id}?document_type=${docType}`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ [field]: value })
        }
      );
      if (response.ok) {
        setSuccess(`Document numbering updated for ${docType}`);
        fetchDocumentConfig(selectedStore.id);
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to update');
      }
    } catch (err) {
      setError('Failed to update document numbering');
    } finally {
      setSavingDocument(false);
    }
  };

  // Custom role creation
  const handleCreateCustomRole = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/management/custom-roles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(customRoleForm)
      });
      const data = await response.json();
      if (response.ok && data.status === 'success') {
        setSuccess(`Custom role "${customRoleForm.name}" created!`);
        setShowCreateCustomRole(false);
        setCustomRoleForm({ name: '', description: '', level: 'staff', permissions: {} });
        fetchCustomRoles();
        fetchRolesAndPermissions();
      } else {
        setError(data.detail || 'Failed to create custom role');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  // Helper functions
  const resetStoreForm = () => {
    setStoreForm({
      name: '', code: '', address: '', city: '', state: '', pincode: '',
      phone: '', email: '', manager_name: '', is_warehouse: false,
      gst_number: '', pan_number: '', tagline: '',
      invoice_prefix: '', so_prefix: '',
      create_manager_login: false,
      manager_email: '',
      manager_password: '',
      manager_first_name: '',
      manager_last_name: ''
    });
  };

  const resetUserForm = () => {
    setUserForm({
      email: '', password: '', first_name: '', last_name: '', phone: '',
      role: 'sales_staff', customPermissions: {}
    });
  };

  const handleRoleChange = (role) => {
    const rolePerms = roleTemplates[role]?.permissions || {};
    setUserForm({
      ...userForm,
      role: role,
      customPermissions: JSON.parse(JSON.stringify(rolePerms))
    });
  };

  const toggleUserPermission = (module, permission) => {
    const modulePerms = userForm.customPermissions[module] || [];
    const newPerms = modulePerms.includes(permission)
      ? modulePerms.filter(p => p !== permission)
      : [...modulePerms, permission];
    setUserForm({
      ...userForm,
      customPermissions: { ...userForm.customPermissions, [module]: newPerms }
    });
  };

  const toggleStoreModulePermission = (moduleId) => {
    setStoreModulePermissions(prev => ({
      ...prev,
      [moduleId]: !prev[moduleId]
    }));
  };

  const openStoreDetail = (store) => {
    setSelectedStore(store);
    setStoreModulePermissions(store.module_permissions || {});
    setActiveView('store-detail');
    setActiveTab('info');
  };

  const openEditStore = () => {
    setStoreForm({
      name: selectedStore.name || '',
      code: selectedStore.code || '',
      address: selectedStore.address || '',
      city: selectedStore.city || '',
      state: selectedStore.state || '',
      pincode: selectedStore.pincode || '',
      phone: selectedStore.phone || '',
      email: selectedStore.email || '',
      manager_name: selectedStore.manager_name || '',
      is_warehouse: selectedStore.is_warehouse || false,
      gst_number: selectedStore.gst_number || '',
      pan_number: selectedStore.pan_number || '',
      tagline: selectedStore.tagline || '',
      invoice_prefix: selectedStore.invoice_prefix || '',
      so_prefix: selectedStore.so_prefix || ''
    });
    setShowEditStore(true);
  };

  const openEditUser = (user) => {
    setSelectedUser(user);
    setUserForm({
      email: user.email || '',
      password: '',
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      phone: user.phone || '',
      role: user.role || 'sales_staff',
      customPermissions: user.permissions || roleTemplates[user.role]?.permissions || {}
    });
    setShowEditUser(true);
  };

  const getRoleBadgeColor = (role) => {
    const template = roleTemplates[role];
    if (!template) {
      // Check custom roles
      const customRole = customRoles.find(r => r.id === role);
      if (customRole) return LEVEL_INFO.custom.color;
      return 'bg-gray-100 text-gray-800';
    }
    const level = template.level || 'staff';
    return LEVEL_INFO[level]?.color || 'bg-gray-100 text-gray-800';
  };

  const getRoleName = (roleId) => {
    if (roleTemplates[roleId]) return roleTemplates[roleId].name;
    const customRole = customRoles.find(r => r.id === roleId);
    if (customRole) return customRole.name;
    return roleId;
  };

  // Clear messages after 5 seconds
  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError('');
        setSuccess('');
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

  // ================== RENDER ==================

  if (loading && stores.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          {activeView === 'store-detail' && (
            <button
              onClick={() => { setActiveView('stores'); setSelectedStore(null); }}
              className="p-2 hover:bg-gray-200 rounded-lg"
            >
              <ChevronLeft className="w-6 h-6" />
            </button>
          )}
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Building2 className="w-8 h-8 text-teal-600" />
              {activeView === 'stores' ? 'Store & Team Management' : selectedStore?.name}
            </h1>
            <p className="text-gray-600 mt-1">
              {activeView === 'stores' 
                ? 'Manage stores, team members, roles, and document numbering'
                : `Store Code: ${selectedStore?.code}`
              }
            </p>
          </div>
        </div>
        {activeView === 'stores' && (
          <div className="flex gap-3">
            <button
              onClick={() => setShowCreateCustomRole(true)}
              className="px-4 py-2 border border-amber-500 text-amber-700 rounded-lg hover:bg-amber-50 flex items-center gap-2"
              data-testid="create-custom-role-btn"
            >
              <Shield className="w-5 h-5" />
              Create Custom Role
            </button>
            <button
              onClick={() => { resetStoreForm(); setShowCreateStore(true); }}
              className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 flex items-center gap-2"
              data-testid="create-store-btn"
            >
              <Plus className="w-5 h-5" />
              Add New Store
            </button>
          </div>
        )}
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
      {activeView === 'stores' ? (
        // ============ STORES LIST VIEW ============
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {stores.map(store => (
            <div
              key={store.id}
              className="bg-white rounded-xl shadow-sm p-5 border border-gray-100 hover:shadow-md transition-shadow"
              data-testid={`store-card-${store.code}`}
            >
              <div className="flex items-start justify-between mb-4">
                <div 
                  className="flex items-center gap-3 cursor-pointer flex-1"
                  onClick={() => openStoreDetail(store)}
                >
                  <div className={`p-3 rounded-xl ${store.is_warehouse ? 'bg-purple-100' : 'bg-teal-100'}`}>
                    {store.is_warehouse ? <Package className="w-6 h-6 text-purple-600" /> : <Store className="w-6 h-6 text-teal-600" />}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800">{store.name}</h3>
                    <p className="text-sm text-gray-500">{store.code}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    store.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  }`}>
                    {store.is_active ? 'Active' : 'Inactive'}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteStore(store);
                    }}
                    className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete Store"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div 
                className="text-sm text-gray-600 space-y-1 cursor-pointer"
                onClick={() => openStoreDetail(store)}
              >
                <div className="flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-gray-400" />
                  {store.city}, {store.state}
                </div>
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-gray-400" />
                  {store.user_count || 0} team members
                </div>
              </div>
              <div 
                className="mt-4 flex items-center justify-between text-xs text-gray-400 cursor-pointer"
                onClick={() => openStoreDetail(store)}
              >
                <span>Click to manage</span>
                <ChevronRight className="w-4 h-4" />
              </div>
            </div>
          ))}
          {stores.length === 0 && (
            <div className="col-span-full bg-white rounded-xl shadow-sm p-12 text-center">
              <Store className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-700 mb-2">No Stores Yet</h3>
              <p className="text-gray-500 mb-4">Create your first store to get started</p>
              <button
                onClick={() => { resetStoreForm(); setShowCreateStore(true); }}
                className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700"
              >
                Create Store
              </button>
            </div>
          )}
        </div>
      ) : (
        // ============ STORE DETAIL VIEW ============
        <div>
          {/* Tabs */}
          <div className="bg-white rounded-xl shadow-sm mb-6">
            <div className="flex border-b overflow-x-auto">
              {[
                { id: 'info', label: 'Store Info', icon: Store },
                { id: 'permissions', label: 'Module Permissions', icon: Shield },
                { id: 'documents', label: 'Document Numbering', icon: Hash },
                { id: 'users', label: 'Team Members', icon: Users },
                { id: 'delivery', label: 'Delivery Personnel', icon: Truck }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-6 py-4 font-medium transition-colors ${
                    activeTab === tab.id 
                      ? 'text-teal-600 border-b-2 border-teal-600 bg-teal-50/50' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                  data-testid={`tab-${tab.id}`}
                >
                  <tab.icon className="w-5 h-5" />
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          {activeTab === 'info' && (
            // ============ STORE INFO TAB ============
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-800">Store Information</h2>
                <button
                  onClick={openEditStore}
                  className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 flex items-center gap-2"
                >
                  <Edit2 className="w-4 h-4" />
                  Edit Store
                </button>
              </div>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="text-sm font-medium text-gray-500">Store Name</label>
                  <p className="text-lg text-gray-800">{selectedStore?.name}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Store Code</label>
                  <p className="text-lg text-gray-800">{selectedStore?.code}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Address</label>
                  <p className="text-gray-800">{selectedStore?.address}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">City</label>
                  <p className="text-gray-800">{selectedStore?.city}, {selectedStore?.state} - {selectedStore?.pincode}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Phone</label>
                  <p className="text-gray-800">{selectedStore?.phone || 'Not set'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Email</label>
                  <p className="text-gray-800">{selectedStore?.email || 'Not set'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Manager</label>
                  <p className="text-gray-800">{selectedStore?.manager_name || 'Not assigned'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Type</label>
                  <p className="text-gray-800">{selectedStore?.is_warehouse ? 'Warehouse' : 'Retail Store'}</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'permissions' && (
            // ============ MODULE PERMISSIONS TAB ============
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-semibold text-gray-800">Store Module Permissions</h2>
                  <p className="text-sm text-gray-500">Select which modules this store can access</p>
                </div>
                <button
                  onClick={handleSaveStorePermissions}
                  className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 flex items-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  Save Permissions
                </button>
              </div>
              
              <div className="space-y-6">
                {Object.entries(modulesByCategory).map(([category, modules]) => {
                  if (category === 'admin') return null; // Skip admin-only modules for stores
                  const catInfo = CATEGORY_INFO[category] || { label: category, color: 'text-gray-600', bg: 'bg-gray-50' };
                  const enabledCount = modules.filter(m => storeModulePermissions[m.id]).length;
                  
                  return (
                    <div key={category} className="border rounded-lg overflow-hidden">
                      <div className={`p-4 flex items-center justify-between ${catInfo.bg}`}>
                        <div className="flex items-center gap-2">
                          <span className={`font-medium ${catInfo.color}`}>{catInfo.label}</span>
                          <span className="text-xs text-gray-400">({enabledCount}/{modules.length} enabled)</span>
                        </div>
                        <div className="flex gap-2">
                          <button
                            type="button"
                            onClick={() => {
                              const newPerms = { ...storeModulePermissions };
                              modules.forEach(m => { newPerms[m.id] = true; });
                              setStoreModulePermissions(newPerms);
                            }}
                            className="text-xs text-blue-600 hover:underline"
                          >
                            Select All
                          </button>
                          <span className="text-gray-300">|</span>
                          <button
                            type="button"
                            onClick={() => {
                              const newPerms = { ...storeModulePermissions };
                              modules.forEach(m => { newPerms[m.id] = false; });
                              setStoreModulePermissions(newPerms);
                            }}
                            className="text-xs text-gray-500 hover:underline"
                          >
                            Deselect All
                          </button>
                        </div>
                      </div>
                      <div className="p-4 grid grid-cols-2 md:grid-cols-3 gap-3">
                        {modules.map(module => (
                          <label
                            key={module.id}
                            className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all ${
                              storeModulePermissions[module.id]
                                ? 'border-teal-300 bg-teal-50'
                                : 'border-gray-200 hover:border-gray-300'
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={storeModulePermissions[module.id] || false}
                              onChange={() => toggleStoreModulePermission(module.id)}
                              className="w-4 h-4 text-teal-600 rounded"
                            />
                            <span className="text-sm font-medium text-gray-700">{module.name}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {activeTab === 'documents' && (
            // ============ DOCUMENT NUMBERING TAB ============
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-semibold text-gray-800">Document Numbering</h2>
                  <p className="text-sm text-gray-500">Set your custom format for each document type</p>
                </div>
                <button
                  onClick={() => fetchDocumentConfig(selectedStore.id)}
                  className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
                >
                  <RefreshCw className={`w-5 h-5 ${savingDocument ? 'animate-spin' : ''}`} />
                </button>
              </div>

              {/* Simple Format Guide - Your Format */}
              <div className="bg-gradient-to-r from-amber-50 to-orange-50 p-5 rounded-xl border border-amber-200 mb-6">
                <h4 className="font-semibold text-amber-800 text-lg mb-3">Your Format: {selectedStore?.code}0001/26-27</h4>
                <p className="text-sm text-amber-700 mb-3">Just type your format using these placeholders:</p>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                  <div className="bg-white px-3 py-2 rounded-lg border border-amber-200">
                    <code className="text-amber-800 font-mono">{'{STORE}'}</code>
                    <span className="text-gray-600 ml-2">→ {selectedStore?.code || 'ARM'}</span>
                  </div>
                  <div className="bg-white px-3 py-2 rounded-lg border border-amber-200">
                    <code className="text-amber-800 font-mono">{'{SEQ:4}'}</code>
                    <span className="text-gray-600 ml-2">→ 0001</span>
                  </div>
                  <div className="bg-white px-3 py-2 rounded-lg border border-amber-200">
                    <code className="text-amber-800 font-mono">{'{FY}'}</code>
                    <span className="text-gray-600 ml-2">→ 26-27</span>
                  </div>
                </div>
                <div className="mt-4 pt-3 border-t border-amber-200">
                  <p className="text-sm text-amber-800">
                    <strong>Examples:</strong><br/>
                    Invoice: <code className="bg-white px-2 py-0.5 rounded">{'{STORE}{SEQ:4}/{FY}'}</code> → <strong>{selectedStore?.code}0001/26-27</strong><br/>
                    Sales Order: <code className="bg-white px-2 py-0.5 rounded">{'{STORE}SO{SEQ:4}/{FY}'}</code> → <strong>{selectedStore?.code}SO0001/26-27</strong>
                  </p>
                </div>
              </div>

              {documentConfig ? (
                <div className="space-y-4">
                  {Object.entries(documentConfig.document_configs || {}).map(([docType, config]) => {
                    // Always use custom format mode
                    const customFormat = config.custom_format || `{STORE}${config.prefix === 'INV' ? '' : config.prefix}{SEQ:4}/{FY}`;
                    
                    // Generate live preview
                    const now = new Date();
                    const fy = now.getMonth() >= 3 
                      ? `${String(now.getFullYear()).slice(-2)}-${String(now.getFullYear() + 1).slice(-2)}`
                      : `${String(now.getFullYear() - 1).slice(-2)}-${String(now.getFullYear()).slice(-2)}`;
                    const preview = customFormat
                      .replace(/\{STORE\}/gi, documentConfig.store_code || '')
                      .replace(/\{STORE_CODE\}/gi, documentConfig.store_code || '')
                      .replace(/\{PREFIX\}/gi, config.prefix)
                      .replace(/\{YEAR\}/gi, String(now.getFullYear()))
                      .replace(/\{YYYY\}/gi, String(now.getFullYear()))
                      .replace(/\{YY\}/gi, String(now.getFullYear()).slice(-2))
                      .replace(/\{FY\}/gi, fy)
                      .replace(/\{MM\}/gi, String(now.getMonth() + 1).padStart(2, '0'))
                      .replace(/\{DD\}/gi, String(now.getDate()).padStart(2, '0'))
                      .replace(/\{SEQ:(\d+)\}/gi, (_, p) => String(config.current_number || 1).padStart(parseInt(p), '0'))
                      .replace(/\{SEQ\}/gi, String(config.current_number || 1).padStart(4, '0'));
                    
                    return (
                      <div key={docType} className="border-2 border-gray-100 rounded-xl p-4 hover:border-amber-200 hover:shadow-md transition-all">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-amber-50 rounded-lg">
                              <FileText className="w-5 h-5 text-amber-600" />
                            </div>
                            <div>
                              <h4 className="font-semibold text-gray-800">{config.description}</h4>
                              <p className="text-sm">
                                Preview: <span className="font-mono text-green-600 font-bold bg-green-50 px-2 py-0.5 rounded">{preview}</span>
                              </p>
                            </div>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
                          <div className="md:col-span-2">
                            <label className="text-xs text-gray-600 block mb-1">Format Pattern</label>
                            <input
                              type="text"
                              value={customFormat}
                              onChange={(e) => {
                                const newConfig = { ...documentConfig };
                                newConfig.document_configs[docType].custom_format = e.target.value.toUpperCase();
                                newConfig.document_configs[docType].use_custom_format = true;
                                setDocumentConfig(newConfig);
                              }}
                              onBlur={(e) => {
                                handleUpdateDocumentConfig(docType, 'custom_format', e.target.value.toUpperCase());
                                handleUpdateDocumentConfig(docType, 'use_custom_format', true);
                              }}
                              placeholder={`{STORE}${docType === 'invoice' ? '' : 'SO'}{SEQ:4}/{FY}`}
                              className="w-full px-3 py-2.5 border-2 border-gray-200 rounded-lg font-mono text-sm focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
                            />
                          </div>
                          <div>
                            <label className="text-xs text-gray-600 block mb-1">Next #</label>
                            <input
                              type="number"
                              min="1"
                              value={config.current_number || 1}
                              onChange={(e) => {
                                const newConfig = { ...documentConfig };
                                newConfig.document_configs[docType].current_number = parseInt(e.target.value) || 1;
                                setDocumentConfig(newConfig);
                              }}
                              onBlur={(e) => handleUpdateDocumentConfig(docType, 'current_number', parseInt(e.target.value) || 1)}
                              className="w-full px-3 py-2.5 border-2 border-gray-200 rounded-lg text-sm text-center focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
                            />
                          </div>
                          <div>
                            <button
                              onClick={() => {
                                handleUpdateDocumentConfig(docType, 'custom_format', customFormat);
                                handleUpdateDocumentConfig(docType, 'use_custom_format', true);
                                handleUpdateDocumentConfig(docType, 'current_number', config.current_number || 1);
                              }}
                              className="w-full px-4 py-2.5 bg-amber-600 text-white rounded-lg hover:bg-amber-700 flex items-center justify-center gap-2 text-sm font-semibold"
                            >
                              <Save className="w-4 h-4" />
                              Save
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
                  Loading document configuration...
                </div>
              )}
            </div>
          )}

          {activeTab === 'users' && (
            // ============ TEAM MEMBERS TAB ============
            <div className="bg-white rounded-xl shadow-sm">
              <div className="p-4 border-b flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-800">Team Members</h2>
                <button
                  onClick={() => { resetUserForm(); setShowCreateUser(true); }}
                  className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 flex items-center gap-2"
                  data-testid="add-store-user-btn"
                >
                  <Plus className="w-4 h-4" />
                  Add Team Member
                </button>
              </div>
              <div className="divide-y">
                {storeUsers.map(user => (
                  <div key={user.id} className="p-4 flex items-center justify-between hover:bg-gray-50">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                        user.is_active !== false ? 'bg-teal-100' : 'bg-gray-200'
                      }`}>
                        <span className={`text-lg font-medium ${user.is_active !== false ? 'text-teal-600' : 'text-gray-400'}`}>
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
                    <div className="flex items-center gap-4">
                      <span className={`px-3 py-1 text-xs font-medium rounded-full ${getRoleBadgeColor(user.role)}`}>
                        {getRoleName(user.role)}
                      </span>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => openEditUser(user)}
                          className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
                          title="Edit User"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleToggleUserStatus(user)}
                          className={`p-2 rounded-lg ${
                            user.is_active !== false ? 'text-red-500 hover:bg-red-50' : 'text-green-500 hover:bg-green-50'
                          }`}
                          title={user.is_active !== false ? 'Disable' : 'Enable'}
                        >
                          {user.is_active !== false ? <X className="w-4 h-4" /> : <Check className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
                {storeUsers.length === 0 && (
                  <div className="p-12 text-center text-gray-500">
                    <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                    <p>No team members in this store</p>
                    <button
                      onClick={() => { resetUserForm(); setShowCreateUser(true); }}
                      className="mt-4 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700"
                    >
                      Add First Member
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'delivery' && (
            // ============ DELIVERY PERSONNEL TAB ============
            <DeliveryPersonnelTab />
          )}
        </div>
      )}

      {/* ============ MODALS ============ */}
      
      {/* Create Store Modal */}
      {showCreateStore && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b flex items-center justify-between bg-gradient-to-r from-teal-600 to-teal-700 text-white rounded-t-2xl">
              <h2 className="text-xl font-bold">Create New Store</h2>
              <button onClick={() => setShowCreateStore(false)} className="p-2 hover:bg-white/20 rounded-lg">
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
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Store Code *</label>
                  <input
                    type="text"
                    value={storeForm.code}
                    onChange={(e) => setStoreForm({...storeForm, code: e.target.value.toUpperCase()})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    placeholder="MGRD"
                    required
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
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={storeForm.email}
                    onChange={(e) => setStoreForm({...storeForm, email: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
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
                  />
                </div>
                <div className="flex items-center pt-6">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={storeForm.is_warehouse}
                      onChange={(e) => setStoreForm({...storeForm, is_warehouse: e.target.checked})}
                      className="w-4 h-4 rounded text-teal-600"
                    />
                    <span className="text-sm text-gray-700">This is a Warehouse</span>
                  </label>
                </div>
              </div>

              {/* Tax & Document Fields */}
              <div className="border-t pt-4 mt-4">
                <h4 className="text-sm font-semibold text-gray-800 mb-3">Tax & Document Details</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">GST Number (GSTIN)</label>
                    <input
                      type="text"
                      value={storeForm.gst_number}
                      onChange={(e) => setStoreForm({...storeForm, gst_number: e.target.value.toUpperCase()})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                      placeholder="e.g., 29ABAFA6295J1Z2"
                      maxLength={15}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">PAN Number</label>
                    <input
                      type="text"
                      value={storeForm.pan_number}
                      onChange={(e) => setStoreForm({...storeForm, pan_number: e.target.value.toUpperCase()})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                      placeholder="e.g., ABAFA6295J"
                      maxLength={10}
                    />
                  </div>
                </div>
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Business Tagline (Optional)</label>
                  <input
                    type="text"
                    value={storeForm.tagline}
                    onChange={(e) => setStoreForm({...storeForm, tagline: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    placeholder="e.g., Premium Home Appliances"
                  />
                </div>
              </div>

              {/* Store Manager Login Section */}
              <div className="border-t pt-4 mt-4">
                <label className="flex items-center gap-3 cursor-pointer mb-4">
                  <input
                    type="checkbox"
                    checked={storeForm.create_manager_login}
                    onChange={(e) => setStoreForm({...storeForm, create_manager_login: e.target.checked})}
                    className="w-5 h-5 rounded text-teal-600"
                  />
                  <div>
                    <span className="font-medium text-gray-800">Create Store Manager Login</span>
                    <p className="text-xs text-gray-500">Create login credentials so the store manager can access the system</p>
                  </div>
                </label>

                {storeForm.create_manager_login && (
                  <div className="bg-teal-50 border border-teal-200 rounded-lg p-4 space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">First Name *</label>
                        <input
                          type="text"
                          value={storeForm.manager_first_name}
                          onChange={(e) => setStoreForm({...storeForm, manager_first_name: e.target.value})}
                          className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                          placeholder="John"
                          required={storeForm.create_manager_login}
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Last Name *</label>
                        <input
                          type="text"
                          value={storeForm.manager_last_name}
                          onChange={(e) => setStoreForm({...storeForm, manager_last_name: e.target.value})}
                          className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                          placeholder="Doe"
                          required={storeForm.create_manager_login}
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Login Email *</label>
                      <input
                        type="email"
                        value={storeForm.manager_email}
                        onChange={(e) => setStoreForm({...storeForm, manager_email: e.target.value})}
                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                        placeholder="manager@store.com"
                        required={storeForm.create_manager_login}
                      />
                      <p className="text-xs text-gray-500 mt-1">This email will be used to login to the store portal</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Login Password *</label>
                      <input
                        type="password"
                        value={storeForm.manager_password}
                        onChange={(e) => setStoreForm({...storeForm, manager_password: e.target.value})}
                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                        placeholder="••••••••"
                        minLength={6}
                        required={storeForm.create_manager_login}
                      />
                      <p className="text-xs text-gray-500 mt-1">Minimum 6 characters</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button type="button" onClick={() => setShowCreateStore(false)} className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700">
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
              {/* Same fields as create */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Store Name *</label>
                  <input
                    type="text"
                    value={storeForm.name}
                    onChange={(e) => setStoreForm({...storeForm, name: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Store Code *</label>
                  <input
                    type="text"
                    value={storeForm.code}
                    onChange={(e) => setStoreForm({...storeForm, code: e.target.value.toUpperCase()})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                <input
                  type="text"
                  value={storeForm.address}
                  onChange={(e) => setStoreForm({...storeForm, address: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                  <input type="text" value={storeForm.city} onChange={(e) => setStoreForm({...storeForm, city: e.target.value})} className="w-full px-3 py-2 border rounded-lg" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                  <input type="text" value={storeForm.state} onChange={(e) => setStoreForm({...storeForm, state: e.target.value})} className="w-full px-3 py-2 border rounded-lg" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Pincode</label>
                  <input type="text" value={storeForm.pincode} onChange={(e) => setStoreForm({...storeForm, pincode: e.target.value})} className="w-full px-3 py-2 border rounded-lg" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                  <input type="tel" value={storeForm.phone} onChange={(e) => setStoreForm({...storeForm, phone: e.target.value})} className="w-full px-3 py-2 border rounded-lg" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input type="email" value={storeForm.email} onChange={(e) => setStoreForm({...storeForm, email: e.target.value})} className="w-full px-3 py-2 border rounded-lg" />
                </div>
              </div>
              
              {/* Tax & Document Fields */}
              <div className="border-t pt-4 mt-4">
                <h4 className="text-sm font-semibold text-gray-800 mb-3">Tax & Document Details</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">GST Number (GSTIN)</label>
                    <input
                      type="text"
                      value={storeForm.gst_number}
                      onChange={(e) => setStoreForm({...storeForm, gst_number: e.target.value.toUpperCase()})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                      placeholder="e.g., 29ABAFA6295J1Z2"
                      maxLength={15}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">PAN Number</label>
                    <input
                      type="text"
                      value={storeForm.pan_number}
                      onChange={(e) => setStoreForm({...storeForm, pan_number: e.target.value.toUpperCase()})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                      placeholder="e.g., ABAFA6295J"
                      maxLength={10}
                    />
                  </div>
                </div>
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Business Tagline (Optional)</label>
                  <input
                    type="text"
                    value={storeForm.tagline}
                    onChange={(e) => setStoreForm({...storeForm, tagline: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    placeholder="e.g., Premium Home Appliances"
                  />
                </div>
              </div>
              
              <div className="flex justify-end gap-3 pt-4 border-t">
                <button type="button" onClick={() => setShowEditStore(false)} className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700">Update Store</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Create/Edit User Modal */}
      {(showCreateUser || showEditUser) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[95vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b bg-gradient-to-r from-teal-600 to-teal-700 text-white flex items-center justify-between rounded-t-2xl">
              <div>
                <h2 className="text-xl font-bold">{showEditUser ? 'Edit Team Member' : 'Add Team Member'}</h2>
                <p className="text-teal-100 text-sm">{selectedStore?.name}</p>
              </div>
              <button onClick={() => { setShowCreateUser(false); setShowEditUser(false); setSelectedUser(null); }} className="p-2 hover:bg-white/20 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6">
              <form onSubmit={showEditUser ? handleUpdateUser : handleCreateUser} className="space-y-6">
                {/* Basic Info */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                    <input
                      type="tel"
                      value={userForm.phone}
                      onChange={(e) => setUserForm({...userForm, phone: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
                    <input
                      type="email"
                      value={userForm.email}
                      onChange={(e) => setUserForm({...userForm, email: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500"
                      required
                      disabled={showEditUser}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Password {showEditUser ? '(leave blank to keep)' : '*'}
                    </label>
                    <div className="relative">
                      <input
                        type={showPassword ? 'text' : 'password'}
                        value={userForm.password}
                        onChange={(e) => setUserForm({...userForm, password: e.target.value})}
                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 pr-10"
                        required={!showEditUser}
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
                </div>

                {/* Role Selection */}
                <div className="border rounded-xl p-4 bg-gray-50">
                  <label className="block text-sm font-medium text-gray-700 mb-4">Select Role *</label>
                  <div className="space-y-4">
                    {Object.entries(rolesByLevel).map(([level, roles]) => (
                      <div key={level}>
                        <div className={`text-xs font-semibold mb-2 flex items-center gap-2 ${
                          level === 'admin' ? 'text-purple-700' : level === 'manager' ? 'text-blue-700' : 'text-green-700'
                        }`}>
                          {LEVEL_INFO[level]?.icon} {LEVEL_INFO[level]?.label}
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                          {roles.map(role => (
                            <label
                              key={role.id}
                              className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-all ${
                                userForm.role === role.id
                                  ? 'border-teal-500 bg-teal-50 ring-2 ring-teal-200'
                                  : 'border-gray-200 hover:border-gray-300 bg-white'
                              }`}
                            >
                              <input
                                type="radio"
                                name="role"
                                value={role.id}
                                checked={userForm.role === role.id}
                                onChange={(e) => handleRoleChange(e.target.value)}
                                className="w-4 h-4 text-teal-600"
                              />
                              <span className="text-sm font-medium text-gray-800">{role.name}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    ))}
                    
                    {/* Custom Roles */}
                    {customRoles.length > 0 && (
                      <div>
                        <div className="text-xs font-semibold mb-2 flex items-center gap-2 text-amber-700">
                          {LEVEL_INFO.custom.icon} Custom Roles
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                          {customRoles.map(role => (
                            <label
                              key={role.id}
                              className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-all ${
                                userForm.role === role.id
                                  ? 'border-amber-500 bg-amber-50 ring-2 ring-amber-200'
                                  : 'border-gray-200 hover:border-gray-300 bg-white'
                              }`}
                            >
                              <input
                                type="radio"
                                name="role"
                                value={role.id}
                                checked={userForm.role === role.id}
                                onChange={(e) => handleRoleChange(e.target.value)}
                                className="w-4 h-4 text-amber-600"
                              />
                              <span className="text-sm font-medium text-gray-800">{role.name}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Custom Permissions */}
                <div className="border rounded-xl overflow-hidden">
                  <div className="p-4 bg-gray-100 border-b">
                    <h3 className="font-semibold text-gray-800">Customize Permissions</h3>
                    <p className="text-xs text-gray-500">Fine-tune access for each module</p>
                  </div>
                  <div className="divide-y max-h-96 overflow-y-auto">
                    {Object.entries(modulesByCategory).map(([category, modules]) => {
                      const catInfo = CATEGORY_INFO[category] || { label: category, color: 'text-gray-600', bg: 'bg-gray-50' };
                      const isExpanded = expandedCategories[category];
                      
                      return (
                        <div key={category}>
                          <button
                            type="button"
                            onClick={() => setExpandedCategories(prev => ({ ...prev, [category]: !prev[category] }))}
                            className={`w-full p-3 flex items-center justify-between hover:bg-gray-50 ${catInfo.bg}`}
                          >
                            <div className="flex items-center gap-2">
                              {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                              <span className={`font-medium text-sm ${catInfo.color}`}>{catInfo.label}</span>
                            </div>
                          </button>
                          {isExpanded && (
                            <div className="p-3 bg-white grid grid-cols-1 md:grid-cols-2 gap-2">
                              {modules.map(module => {
                                const modulePerms = userForm.customPermissions[module.id] || [];
                                return (
                                  <div key={module.id} className="border rounded-lg p-2">
                                    <h4 className="font-medium text-gray-800 text-sm mb-2">{module.name}</h4>
                                    <div className="flex flex-wrap gap-1">
                                      {module.permissions.map(perm => (
                                        <label
                                          key={perm}
                                          className={`flex items-center gap-1 px-2 py-1 rounded text-xs cursor-pointer ${
                                            modulePerms.includes(perm)
                                              ? 'bg-teal-100 text-teal-800 border border-teal-300'
                                              : 'bg-gray-100 text-gray-600 border border-transparent hover:border-gray-300'
                                          }`}
                                        >
                                          <input
                                            type="checkbox"
                                            checked={modulePerms.includes(perm)}
                                            onChange={() => toggleUserPermission(module.id, perm)}
                                            className="w-3 h-3 text-teal-600 rounded"
                                          />
                                          <span className="capitalize">{perm}</span>
                                        </label>
                                      ))}
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
                </div>
              </form>
            </div>

            <div className="p-4 border-t bg-gray-50 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => { setShowCreateUser(false); setShowEditUser(false); setSelectedUser(null); }}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={showEditUser ? handleUpdateUser : handleCreateUser}
                className="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
                {showEditUser ? 'Update User' : 'Create User'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Custom Role Modal */}
      {showCreateCustomRole && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[95vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b bg-gradient-to-r from-amber-500 to-amber-600 text-white flex items-center justify-between rounded-t-2xl">
              <div>
                <h2 className="text-xl font-bold">Create Custom Role</h2>
                <p className="text-amber-100 text-sm">Define a new role with custom permissions</p>
              </div>
              <button onClick={() => setShowCreateCustomRole(false)} className="p-2 hover:bg-white/20 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6">
              <form onSubmit={handleCreateCustomRole} className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Role Name *</label>
                    <input
                      type="text"
                      value={customRoleForm.name}
                      onChange={(e) => setCustomRoleForm({...customRoleForm, name: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500"
                      placeholder="e.g., Junior Accountant"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Level</label>
                    <select
                      value={customRoleForm.level}
                      onChange={(e) => setCustomRoleForm({...customRoleForm, level: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500"
                    >
                      <option value="staff">Staff Level</option>
                      <option value="manager">Manager Level</option>
                      <option value="admin">Admin Level</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    value={customRoleForm.description}
                    onChange={(e) => setCustomRoleForm({...customRoleForm, description: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500"
                    rows={2}
                    placeholder="Describe what this role is for..."
                  />
                </div>
                
                {/* Permissions for custom role */}
                <div className="border rounded-xl overflow-hidden">
                  <div className="p-4 bg-amber-50 border-b">
                    <h3 className="font-semibold text-amber-800">Set Default Permissions</h3>
                  </div>
                  <div className="p-4 max-h-64 overflow-y-auto">
                    {Object.entries(modulesByCategory).map(([category, modules]) => {
                      const catInfo = CATEGORY_INFO[category] || { label: category };
                      return (
                        <div key={category} className="mb-4">
                          <h4 className={`text-sm font-medium ${catInfo.color} mb-2`}>{catInfo.label}</h4>
                          <div className="grid grid-cols-2 gap-2">
                            {modules.map(module => (
                              <label
                                key={module.id}
                                className="flex items-center gap-2 p-2 rounded border hover:bg-gray-50 cursor-pointer"
                              >
                                <input
                                  type="checkbox"
                                  checked={(customRoleForm.permissions[module.id] || []).includes('view')}
                                  onChange={(e) => {
                                    const newPerms = { ...customRoleForm.permissions };
                                    if (e.target.checked) {
                                      newPerms[module.id] = module.permissions;
                                    } else {
                                      delete newPerms[module.id];
                                    }
                                    setCustomRoleForm({...customRoleForm, permissions: newPerms});
                                  }}
                                  className="w-4 h-4 text-amber-600 rounded"
                                />
                                <span className="text-sm text-gray-700">{module.name}</span>
                              </label>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </form>
            </div>

            <div className="p-4 border-t bg-gray-50 flex justify-end gap-3">
              <button type="button" onClick={() => setShowCreateCustomRole(false)} className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
                Cancel
              </button>
              <button onClick={handleCreateCustomRole} className="px-6 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 flex items-center gap-2">
                <Save className="w-4 h-4" />
                Create Role
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UnifiedStoreTeamManagement;
