import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BACKEND_URL } from '../../config/api';
import {
  Shield, Trash2, Database, Download, Upload, AlertTriangle,
  CheckCircle, XCircle, RefreshCw, ArrowLeft, Lock, Users,
  FileText, ShoppingCart, Receipt, Package, Calendar, Settings,
  HardDrive, Clock, Save
} from 'lucide-react';
import { StoreInvoiceCleanup } from './StoreInvoiceCleanup';

const AdminDataManagement = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [adminUser, setAdminUser] = useState(null);
  const [isSuperAdmin, setIsSuperAdmin] = useState(false);
  const [dataStats, setDataStats] = useState({});
  const [selectedCollections, setSelectedCollections] = useState([]);
  const [deleteConfirm, setDeleteConfirm] = useState('');
  const [deleting, setDeleting] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [backups, setBackups] = useState([]);
  const [editPermissions, setEditPermissions] = useState({});
  const [savingPermissions, setSavingPermissions] = useState(false);

  // Data collections that can be managed
  const dataCollections = [
    { id: 'orders', name: 'Sales Orders', icon: ShoppingCart, category: 'sales' },
    { id: 'offline_invoices', name: 'Sales Invoices', icon: Receipt, category: 'sales' },
    { id: 'quotations', name: 'Quotations', icon: FileText, category: 'sales' },
    { id: 'purchase_orders', name: 'Purchase Orders', icon: FileText, category: 'purchase' },
    { id: 'purchase_bills', name: 'Purchase Bills', icon: Receipt, category: 'purchase' },
    { id: 'vouchers', name: 'Payment/Receipt Vouchers', icon: FileText, category: 'accounting' },
    { id: 'journal_entries', name: 'Journal Entries', icon: FileText, category: 'accounting' },
    { id: 'credit_debit_notes', name: 'Credit/Debit Notes', icon: FileText, category: 'accounting' },
    { id: 'expenses', name: 'Expenses', icon: Receipt, category: 'accounting' },
    { id: 'stock_transfers', name: 'Stock Transfers', icon: Package, category: 'inventory' },
    { id: 'delivery_challans', name: 'Delivery Challans', icon: FileText, category: 'inventory' },
  ];

  // Edit permission roles
  const editRoles = [
    { id: 'admin', name: 'Admin', description: 'Full access to all operations' },
    { id: 'accountant', name: 'Accountant', description: 'Can edit accounting entries' },
    { id: 'store_manager', name: 'Store Manager', description: 'Can edit store-level data' },
    { id: 'none', name: 'Locked (No One)', description: 'Document is locked, no edits allowed' },
  ];

  useEffect(() => {
    checkAdminAccess();
  }, []);

  const checkAdminAccess = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      const userData = localStorage.getItem('adminUser');
      
      if (!token || !userData) {
        navigate('/admin/login');
        return;
      }

      const user = JSON.parse(userData);
      setAdminUser(user);

      // Any admin role can access this page
      if (!['admin', 'super_admin', 'company_admin'].includes(user.role)) {
        setIsSuperAdmin(false);
        setLoading(false);
        return;
      }

      setIsSuperAdmin(true);
      await fetchDataStats();
      await fetchBackups();
      await fetchEditPermissions();
      setLoading(false);
    } catch (error) {
      console.error('Error checking admin access:', error);
      setLoading(false);
    }
  };

  const fetchDataStats = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      const response = await fetch(`${BACKEND_URL}/api/admin/data-stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDataStats(data.stats || {});
      }
    } catch (error) {
      console.error('Error fetching data stats:', error);
    }
  };

  const fetchBackups = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      const response = await fetch(`${BACKEND_URL}/api/admin/backups`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setBackups(data.backups || []);
      }
    } catch (error) {
      console.error('Error fetching backups:', error);
    }
  };

  const fetchEditPermissions = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      const response = await fetch(`${BACKEND_URL}/api/admin/edit-permissions`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setEditPermissions(data.permissions || {
          vouchers: 'admin',
          journal_entries: 'admin',
          invoices: 'admin',
          orders: 'admin',
          quotations: 'admin'
        });
      }
    } catch (error) {
      console.error('Error fetching edit permissions:', error);
    }
  };

  const handleDeleteData = async () => {
    if (deleteConfirm !== 'DELETE') {
      setMessage({ type: 'error', text: 'Please type DELETE to confirm' });
      return;
    }

    if (selectedCollections.length === 0) {
      setMessage({ type: 'error', text: 'Please select at least one data type to delete' });
      return;
    }

    setDeleting(true);
    try {
      const token = localStorage.getItem('adminToken');
      const response = await fetch(`${BACKEND_URL}/api/admin/delete-data`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ collections: selectedCollections })
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage({ type: 'success', text: `Successfully deleted data from ${selectedCollections.length} collections` });
        setSelectedCollections([]);
        setDeleteConfirm('');
        await fetchDataStats();
      } else {
        setMessage({ type: 'error', text: data.detail || 'Failed to delete data' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error deleting data: ' + error.message });
    } finally {
      setDeleting(false);
    }
  };

  const handleCreateBackup = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      setMessage({ type: 'info', text: 'Creating backup... This may take a few minutes.' });
      
      const response = await fetch(`${BACKEND_URL}/api/admin/create-backup`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage({ type: 'success', text: 'Backup created successfully!' });
        await fetchBackups();
      } else {
        setMessage({ type: 'error', text: data.detail || 'Failed to create backup' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error creating backup: ' + error.message });
    }
  };

  const handleDownloadBackup = async (backupId, format = 'json') => {
    try {
      const token = localStorage.getItem('adminToken');
      const response = await fetch(`${BACKEND_URL}/api/admin/download-backup/${backupId}?format=${format}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `backup_${backupId}.${format === 'tally' ? 'xml' : format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        setMessage({ type: 'error', text: 'Failed to download backup' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error downloading backup: ' + error.message });
    }
  };

  const handleSavePermissions = async () => {
    setSavingPermissions(true);
    try {
      const token = localStorage.getItem('adminToken');
      const response = await fetch(`${BACKEND_URL}/api/admin/edit-permissions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ permissions: editPermissions })
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Edit permissions saved successfully!' });
      } else {
        setMessage({ type: 'error', text: 'Failed to save permissions' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error saving permissions: ' + error.message });
    } finally {
      setSavingPermissions(false);
    }
  };

  const toggleCollection = (id) => {
    setSelectedCollections(prev => 
      prev.includes(id) ? prev.filter(c => c !== id) : [...prev, id]
    );
  };

  const selectAllInCategory = (category) => {
    const categoryCollections = dataCollections.filter(c => c.category === category).map(c => c.id);
    const allSelected = categoryCollections.every(c => selectedCollections.includes(c));
    
    if (allSelected) {
      setSelectedCollections(prev => prev.filter(c => !categoryCollections.includes(c)));
    } else {
      setSelectedCollections(prev => [...new Set([...prev, ...categoryCollections])]);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (!isSuperAdmin) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Shield className="w-8 h-8 text-red-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-6">
            This page is restricted to Super Administrators only. You do not have permission to access data management features.
          </p>
          <button
            onClick={() => navigate('/admin/dashboard')}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/admin/dashboard')}
          className="flex items-center gap-2 text-gray-600 hover:text-blue-600 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </button>
        <div className="flex items-center gap-3">
          <div className="p-3 bg-red-100 rounded-xl">
            <Database className="w-8 h-8 text-red-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Data Management</h1>
            <p className="text-gray-500">Super Admin Only - Manage data, backups, and permissions</p>
          </div>
        </div>
      </div>

      {/* Message */}
      {message.text && (
        <div className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${
          message.type === 'success' ? 'bg-green-50 text-green-800' :
          message.type === 'error' ? 'bg-red-50 text-red-800' :
          'bg-blue-50 text-blue-800'
        }`}>
          {message.type === 'success' ? <CheckCircle className="w-5 h-5" /> :
           message.type === 'error' ? <XCircle className="w-5 h-5" /> :
           <RefreshCw className="w-5 h-5 animate-spin" />}
          {message.text}
          <button onClick={() => setMessage({ type: '', text: '' })} className="ml-auto">
            <XCircle className="w-4 h-4" />
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Delete Data Section */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-red-100 rounded-lg">
              <Trash2 className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-800">Delete Data</h2>
              <p className="text-sm text-gray-500">Permanently remove selected data</p>
            </div>
          </div>

          {/* Category: Sales */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium text-gray-700">Sales Data</h3>
              <button
                onClick={() => selectAllInCategory('sales')}
                className="text-sm text-blue-600 hover:underline"
              >
                Select All
              </button>
            </div>
            <div className="space-y-2">
              {dataCollections.filter(c => c.category === 'sales').map(col => (
                <label key={col.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                  <input
                    type="checkbox"
                    checked={selectedCollections.includes(col.id)}
                    onChange={() => toggleCollection(col.id)}
                    className="w-4 h-4 text-red-600"
                  />
                  <col.icon className="w-5 h-5 text-gray-500" />
                  <span className="flex-1">{col.name}</span>
                  <span className="text-sm text-gray-400">{dataStats[col.id] || 0} records</span>
                </label>
              ))}
            </div>
          </div>

          {/* Category: Purchase */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium text-gray-700">Purchase Data</h3>
              <button
                onClick={() => selectAllInCategory('purchase')}
                className="text-sm text-blue-600 hover:underline"
              >
                Select All
              </button>
            </div>
            <div className="space-y-2">
              {dataCollections.filter(c => c.category === 'purchase').map(col => (
                <label key={col.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                  <input
                    type="checkbox"
                    checked={selectedCollections.includes(col.id)}
                    onChange={() => toggleCollection(col.id)}
                    className="w-4 h-4 text-red-600"
                  />
                  <col.icon className="w-5 h-5 text-gray-500" />
                  <span className="flex-1">{col.name}</span>
                  <span className="text-sm text-gray-400">{dataStats[col.id] || 0} records</span>
                </label>
              ))}
            </div>
          </div>

          {/* Category: Accounting */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium text-gray-700">Accounting Data</h3>
              <button
                onClick={() => selectAllInCategory('accounting')}
                className="text-sm text-blue-600 hover:underline"
              >
                Select All
              </button>
            </div>
            <div className="space-y-2">
              {dataCollections.filter(c => c.category === 'accounting').map(col => (
                <label key={col.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                  <input
                    type="checkbox"
                    checked={selectedCollections.includes(col.id)}
                    onChange={() => toggleCollection(col.id)}
                    className="w-4 h-4 text-red-600"
                  />
                  <col.icon className="w-5 h-5 text-gray-500" />
                  <span className="flex-1">{col.name}</span>
                  <span className="text-sm text-gray-400">{dataStats[col.id] || 0} records</span>
                </label>
              ))}
            </div>
          </div>

          {/* Category: Inventory */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium text-gray-700">Inventory Data</h3>
              <button
                onClick={() => selectAllInCategory('inventory')}
                className="text-sm text-blue-600 hover:underline"
              >
                Select All
              </button>
            </div>
            <div className="space-y-2">
              {dataCollections.filter(c => c.category === 'inventory').map(col => (
                <label key={col.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                  <input
                    type="checkbox"
                    checked={selectedCollections.includes(col.id)}
                    onChange={() => toggleCollection(col.id)}
                    className="w-4 h-4 text-red-600"
                  />
                  <col.icon className="w-5 h-5 text-gray-500" />
                  <span className="flex-1">{col.name}</span>
                  <span className="text-sm text-gray-400">{dataStats[col.id] || 0} records</span>
                </label>
              ))}
            </div>
          </div>

          {/* Delete Confirmation */}
          {selectedCollections.length > 0 && (
            <div className="border-t pt-4">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-red-800">Warning: This action cannot be undone!</p>
                    <p className="text-sm text-red-600 mt-1">
                      You are about to delete {selectedCollections.length} data type(s). 
                      Type <strong>DELETE</strong> to confirm.
                    </p>
                  </div>
                </div>
              </div>
              <input
                type="text"
                value={deleteConfirm}
                onChange={(e) => setDeleteConfirm(e.target.value)}
                placeholder="Type DELETE to confirm"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4 focus:ring-2 focus:ring-red-500"
              />
              <button
                onClick={handleDeleteData}
                disabled={deleting || deleteConfirm !== 'DELETE'}
                className="w-full py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {deleting ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    Deleting...
                  </>
                ) : (
                  <>
                    <Trash2 className="w-5 h-5" />
                    Delete Selected Data
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Edit Permissions */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Lock className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-800">Edit Permissions</h2>
                <p className="text-sm text-gray-500">Control who can edit saved documents</p>
              </div>
            </div>

            <div className="space-y-4">
              {/* Vouchers Permission */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Payment/Receipt Vouchers
                </label>
                <select
                  value={editPermissions.vouchers || 'super_admin'}
                  onChange={(e) => setEditPermissions(prev => ({ ...prev, vouchers: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  {editRoles.map(role => (
                    <option key={role.id} value={role.id}>{role.name} - {role.description}</option>
                  ))}
                </select>
              </div>

              {/* Journal Entries Permission */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Journal Entries
                </label>
                <select
                  value={editPermissions.journal_entries || 'super_admin'}
                  onChange={(e) => setEditPermissions(prev => ({ ...prev, journal_entries: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  {editRoles.map(role => (
                    <option key={role.id} value={role.id}>{role.name} - {role.description}</option>
                  ))}
                </select>
              </div>

              {/* Invoices Permission */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sales Invoices
                </label>
                <select
                  value={editPermissions.invoices || 'admin'}
                  onChange={(e) => setEditPermissions(prev => ({ ...prev, invoices: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  {editRoles.map(role => (
                    <option key={role.id} value={role.id}>{role.name} - {role.description}</option>
                  ))}
                </select>
              </div>

              {/* Orders Permission */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sales Orders
                </label>
                <select
                  value={editPermissions.orders || 'store_manager'}
                  onChange={(e) => setEditPermissions(prev => ({ ...prev, orders: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  {editRoles.map(role => (
                    <option key={role.id} value={role.id}>{role.name} - {role.description}</option>
                  ))}
                </select>
              </div>

              <button
                onClick={handleSavePermissions}
                disabled={savingPermissions}
                className="w-full py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {savingPermissions ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                Save Permissions
              </button>
            </div>
          </div>

          {/* Backup Section */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-green-100 rounded-lg">
                <HardDrive className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-800">Data Backup</h2>
                <p className="text-sm text-gray-500">Create and download backups</p>
              </div>
            </div>

            {/* Backup Info */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <h3 className="font-medium text-blue-800 mb-2">About Backups</h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• <strong>MongoDB Atlas</strong> handles automatic daily backups in cloud</li>
                <li>• Manual backups can be downloaded in JSON or Tally XML format</li>
                <li>• Tally XML format can be imported into Tally ERP</li>
                <li>• Backups include all transactions, masters, and settings</li>
              </ul>
            </div>

            <button
              onClick={handleCreateBackup}
              className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center justify-center gap-2 mb-4"
            >
              <Download className="w-5 h-5" />
              Create Manual Backup Now
            </button>

            {/* Recent Backups */}
            {backups.length > 0 && (
              <div>
                <h3 className="font-medium text-gray-700 mb-3">Recent Backups</h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {backups.map((backup, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-800">{backup.name}</p>
                        <p className="text-sm text-gray-500">{backup.date} • {backup.size}</p>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleDownloadBackup(backup.id, 'json')}
                          className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                          title="Download JSON"
                        >
                          JSON
                        </button>
                        <button
                          onClick={() => handleDownloadBackup(backup.id, 'tally')}
                          className="px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded hover:bg-purple-200"
                          title="Download Tally XML"
                        >
                          Tally
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Store-scoped invoice/SO deletion */}
      <StoreInvoiceCleanup onDone={() => window.location.reload()} />
    </div>
  );
};

export default AdminDataManagement;
