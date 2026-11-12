import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { Users, Shield, Plus, Edit, Trash2, CheckSquare, Square, X, UserCog, Building2, ChevronDown, ChevronRight, Save, Eye, EyeOff } from 'lucide-react';


// Category labels and colors
const CATEGORY_INFO = {
  operations: { label: 'Operations', color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200' },
  accounting: { label: 'Accounting & Finance', color: 'text-teal-600', bg: 'bg-teal-50', border: 'border-teal-200' },
  customers: { label: 'Customer Management', color: 'text-purple-600', bg: 'bg-purple-50', border: 'border-purple-200' },
  marketing: { label: 'Marketing', color: 'text-pink-600', bg: 'bg-pink-50', border: 'border-pink-200' },
  analytics: { label: 'Analytics', color: 'text-indigo-600', bg: 'bg-indigo-50', border: 'border-indigo-200' },
  config: { label: 'Configuration', color: 'text-gray-600', bg: 'bg-gray-50', border: 'border-gray-200' },
  admin: { label: 'Admin Only', color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200' }
};

// Role level badges
const LEVEL_INFO = {
  admin: { label: 'Admin Level', color: 'bg-purple-100 text-purple-800', icon: '👑' },
  manager: { label: 'Manager Level', color: 'bg-blue-100 text-blue-800', icon: '📋' },
  staff: { label: 'Staff Level', color: 'bg-green-100 text-green-800', icon: '👤' }
};

const EnhancedRoleManagement = () => {
  const [admins, setAdmins] = useState([]);
  const [roleTemplates, setRoleTemplates] = useState({});
  const [permissionModules, setPermissionModules] = useState({});
  const [rolesByLevel, setRolesByLevel] = useState({});
  const [modulesByCategory, setModulesByCategory] = useState({});
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingAdmin, setEditingAdmin] = useState(null);
  const [expandedCategories, setExpandedCategories] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    password: '',
    role: 'sales_staff',
    customPermissions: {}
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch admins
      const adminsRes = await fetch(`${BACKEND_URL}/api/admin/management/admins`);
      const adminsData = await adminsRes.json();
      setAdmins(adminsData.admins || []);

      // Fetch role templates
      const rolesRes = await fetch(`${BACKEND_URL}/api/admin/management/roles/templates`);
      const rolesData = await rolesRes.json();
      setRoleTemplates(rolesData.templates || {});

      // Fetch roles by level
      const rolesByLevelRes = await fetch(`${BACKEND_URL}/api/admin/management/roles/by-level`);
      const rolesByLevelData = await rolesByLevelRes.json();
      setRolesByLevel(rolesByLevelData.roles || {});

      // Fetch permission modules
      const permsRes = await fetch(`${BACKEND_URL}/api/admin/management/permissions/modules`);
      const permsData = await permsRes.json();
      setPermissionModules(permsData.modules || {});

      // Fetch modules by category
      const categoryRes = await fetch(`${BACKEND_URL}/api/admin/management/permissions/by-category`);
      const categoryData = await categoryRes.json();
      setModulesByCategory(categoryData.categories || {});
      
      // Expand all categories by default
      const expanded = {};
      Object.keys(categoryData.categories || {}).forEach(cat => {
        expanded[cat] = true;
      });
      setExpandedCategories(expanded);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  const handleRoleChange = (role) => {
    const rolePerms = roleTemplates[role]?.permissions || {};
    setFormData({
      ...formData,
      role: role,
      customPermissions: JSON.parse(JSON.stringify(rolePerms))
    });
  };

  const togglePermission = (module, permission) => {
    const modulePerms = formData.customPermissions[module] || [];
    const newPerms = modulePerms.includes(permission)
      ? modulePerms.filter(p => p !== permission)
      : [...modulePerms, permission];
    
    setFormData({
      ...formData,
      customPermissions: {
        ...formData.customPermissions,
        [module]: newPerms
      }
    });
  };

  const toggleAllModulePermissions = (moduleId, permissions) => {
    const modulePerms = formData.customPermissions[moduleId] || [];
    const allSelected = permissions.every(p => modulePerms.includes(p));
    
    setFormData({
      ...formData,
      customPermissions: {
        ...formData.customPermissions,
        [moduleId]: allSelected ? [] : [...permissions]
      }
    });
  };

  const toggleCategoryExpand = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const endpoint = editingAdmin 
        ? `${BACKEND_URL}/api/admin/management/admins/${editingAdmin.id}`
        : `${BACKEND_URL}/api/admin/management/admins/custom-role`;
      
      const method = editingAdmin ? 'PUT' : 'POST';
      
      const response = await fetch(endpoint, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          name: formData.name,
          password: formData.password,
          role: formData.role,
          permissions: formData.customPermissions
        })
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        alert(editingAdmin ? 'User updated successfully!' : 'User created successfully!');
        setShowModal(false);
        setEditingAdmin(null);
        resetForm();
        fetchData();
      } else {
        alert('Error: ' + (data.detail || data.message));
      }
    } catch (error) {
      console.error('Error saving user:', error);
      alert('Failed to save user');
    }
  };

  const handleEditAdmin = (admin) => {
    setEditingAdmin(admin);
    setFormData({
      email: admin.email,
      name: admin.name,
      password: '',
      role: admin.role,
      customPermissions: admin.custom_permissions || roleTemplates[admin.role]?.permissions || {}
    });
    setShowModal(true);
  };

  const handleDeleteAdmin = async (adminId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/management/admins/${adminId}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      if (data.status === 'success') {
        alert('User deleted successfully');
        fetchData();
      }
    } catch (error) {
      alert('Failed to delete user');
    }
  };

  const resetForm = () => {
    setFormData({
      email: '',
      name: '',
      password: '',
      role: 'sales_staff',
      customPermissions: {}
    });
  };

  const getRoleBadgeColor = (role) => {
    const template = roleTemplates[role];
    if (!template) return 'bg-gray-100 text-gray-800';
    
    const level = template.level || 'staff';
    return LEVEL_INFO[level]?.color || 'bg-gray-100 text-gray-800';
  };

  const getModulePermissionCount = (moduleId) => {
    const perms = formData.customPermissions[moduleId] || [];
    const totalPerms = permissionModules[moduleId]?.permissions?.length || 0;
    return { selected: perms.length, total: totalPerms };
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <UserCog className="w-8 h-8 text-blue-600" />
            Team & Role Management
          </h1>
          <p className="text-gray-600 mt-2">Create users with specific roles and module access permissions</p>
        </div>
        <button
          onClick={() => {
            setEditingAdmin(null);
            resetForm();
            setShowModal(true);
          }}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 shadow-lg"
          data-testid="add-team-member-btn"
        >
          <Plus className="w-5 h-5" />
          Add Team Member
        </button>
      </div>

      {/* Stats by Level */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl shadow p-5 border-l-4 border-gray-400">
          <div className="text-3xl font-bold text-gray-900">{admins.length}</div>
          <div className="text-sm text-gray-600">Total Team Members</div>
        </div>
        <div className="bg-white rounded-xl shadow p-5 border-l-4 border-purple-500">
          <div className="text-3xl font-bold text-purple-700">
            {admins.filter(a => ['super_admin', 'accounts_admin', 'marketing_admin', 'operations_admin'].includes(a.role)).length}
          </div>
          <div className="text-sm text-purple-600">👑 Admin Level</div>
        </div>
        <div className="bg-white rounded-xl shadow p-5 border-l-4 border-blue-500">
          <div className="text-3xl font-bold text-blue-700">
            {admins.filter(a => ['general_manager', 'accounts_manager', 'marketing_manager'].includes(a.role)).length}
          </div>
          <div className="text-sm text-blue-600">📋 Manager Level</div>
        </div>
        <div className="bg-white rounded-xl shadow p-5 border-l-4 border-green-500">
          <div className="text-3xl font-bold text-green-700">
            {admins.filter(a => ['sales_staff', 'accounts_staff', 'service_staff', 'marketing_staff', 'delivery_staff', 'warehouse_staff', 'data_analyst'].includes(a.role)).length}
          </div>
          <div className="text-sm text-green-600">👤 Staff Level</div>
        </div>
      </div>

      {/* Team Members Table */}
      <div className="bg-white rounded-xl shadow overflow-hidden">
        <div className="p-4 border-b bg-gray-50">
          <h2 className="text-lg font-semibold text-gray-800">Team Members</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Level</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {admins.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                    No team members found. Click "Add Team Member" to create one.
                  </td>
                </tr>
              ) : (
                admins.map((admin) => {
                  const template = roleTemplates[admin.role];
                  const level = template?.level || 'staff';
                  return (
                    <tr key={admin.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                            {admin.name?.charAt(0)?.toUpperCase() || 'U'}
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{admin.name}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-600">{admin.email}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-3 py-1 text-xs font-medium rounded-full ${getRoleBadgeColor(admin.role)}`}>
                          {template?.name || admin.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm">
                          {LEVEL_INFO[level]?.icon} {LEVEL_INFO[level]?.label}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded-full ${admin.is_active !== false ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                          {admin.is_active !== false ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleEditAdmin(admin)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                            title="Edit User"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          {admin.role !== 'super_admin' && (
                            <button
                              onClick={() => handleDeleteAdmin(admin.id)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                              title="Delete User"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full max-h-[95vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="p-6 border-b bg-gradient-to-r from-blue-600 to-blue-700 text-white flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold flex items-center gap-2">
                  {editingAdmin ? <Edit className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
                  {editingAdmin ? 'Edit Team Member' : 'Add Team Member'}
                </h2>
                <p className="text-blue-100 text-sm mt-1">Configure user details and permissions</p>
              </div>
              <button 
                onClick={() => {setShowModal(false); setEditingAdmin(null);}}
                className="p-2 hover:bg-white/20 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-6">
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Basic Info */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Full Name *</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="John Doe"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Email Address *</label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="john@company.com"
                      required
                      disabled={editingAdmin}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Password {editingAdmin ? '(leave blank to keep current)' : '*'}
                    </label>
                    <div className="relative">
                      <input
                        type={showPassword ? 'text' : 'password'}
                        value={formData.password}
                        onChange={(e) => setFormData({...formData, password: e.target.value})}
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 pr-10"
                        placeholder="••••••••"
                        required={!editingAdmin}
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Role Selection by Level */}
                <div className="border rounded-xl p-4 bg-gray-50">
                  <label className="block text-sm font-medium text-gray-700 mb-4">Select Role *</label>
                  <div className="space-y-4">
                    {Object.entries(rolesByLevel).map(([level, roles]) => (
                      <div key={level}>
                        <div className={`text-xs font-semibold mb-2 flex items-center gap-2 ${
                          level === 'admin' ? 'text-purple-700' : 
                          level === 'manager' ? 'text-blue-700' : 'text-green-700'
                        }`}>
                          {LEVEL_INFO[level]?.icon} {LEVEL_INFO[level]?.label}
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                          {roles.map((role) => (
                            <label
                              key={role.id}
                              className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-all ${
                                formData.role === role.id 
                                  ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200' 
                                  : 'border-gray-200 hover:border-gray-300 bg-white'
                              }`}
                            >
                              <input
                                type="radio"
                                name="role"
                                value={role.id}
                                checked={formData.role === role.id}
                                onChange={(e) => handleRoleChange(e.target.value)}
                                className="w-4 h-4 text-blue-600"
                              />
                              <div>
                                <div className="text-sm font-medium text-gray-800">{role.name}</div>
                              </div>
                            </label>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                  {roleTemplates[formData.role] && (
                    <p className="text-sm text-gray-500 mt-3 p-2 bg-white rounded border">
                      <strong>Description:</strong> {roleTemplates[formData.role].description}
                    </p>
                  )}
                </div>

                {/* Custom Permissions by Category */}
                <div className="border rounded-xl overflow-hidden">
                  <div className="p-4 bg-gray-100 border-b flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-800">Customize Module Permissions</h3>
                      <p className="text-xs text-gray-500 mt-1">Fine-tune access for each module. Role defaults are pre-selected.</p>
                    </div>
                  </div>
                  
                  <div className="divide-y">
                    {Object.entries(modulesByCategory).map(([category, modules]) => {
                      const catInfo = CATEGORY_INFO[category] || { label: category, color: 'text-gray-600', bg: 'bg-gray-50' };
                      const isExpanded = expandedCategories[category];
                      
                      return (
                        <div key={category}>
                          <button
                            type="button"
                            onClick={() => toggleCategoryExpand(category)}
                            className={`w-full p-4 flex items-center justify-between hover:bg-gray-50 ${catInfo.bg}`}
                          >
                            <div className="flex items-center gap-2">
                              {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                              <span className={`font-medium ${catInfo.color}`}>{catInfo.label}</span>
                              <span className="text-xs text-gray-400">({modules.length} modules)</span>
                            </div>
                          </button>
                          
                          {isExpanded && (
                            <div className="p-4 bg-white grid grid-cols-1 md:grid-cols-2 gap-3">
                              {modules.map((module) => {
                                const { selected, total } = getModulePermissionCount(module.id);
                                const modulePerms = formData.customPermissions[module.id] || [];
                                
                                return (
                                  <div key={module.id} className={`border rounded-lg p-3 ${catInfo.border}`}>
                                    <div className="flex items-center justify-between mb-2">
                                      <h4 className="font-medium text-gray-800 text-sm">{module.name}</h4>
                                      <button
                                        type="button"
                                        onClick={() => toggleAllModulePermissions(module.id, module.permissions)}
                                        className={`text-xs px-2 py-1 rounded ${
                                          selected === total ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
                                        }`}
                                      >
                                        {selected}/{total}
                                      </button>
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                      {module.permissions.map((perm) => (
                                        <label 
                                          key={perm} 
                                          className={`flex items-center gap-1.5 px-2 py-1 rounded text-xs cursor-pointer transition-all ${
                                            modulePerms.includes(perm)
                                              ? 'bg-blue-100 text-blue-800 border border-blue-300'
                                              : 'bg-gray-100 text-gray-600 border border-transparent hover:border-gray-300'
                                          }`}
                                        >
                                          <input
                                            type="checkbox"
                                            checked={modulePerms.includes(perm)}
                                            onChange={() => togglePermission(module.id, perm)}
                                            className="w-3 h-3 text-blue-600 rounded"
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

            {/* Modal Footer */}
            <div className="p-4 border-t bg-gray-50 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => {setShowModal(false); setEditingAdmin(null);}}
                className="px-6 py-2.5 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
                {editingAdmin ? 'Update User' : 'Create User'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedRoleManagement;
