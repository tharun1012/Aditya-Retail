import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Bell, Send, Settings, Clock, Search, Filter, Mail,
  Phone, MessageSquare, AlertTriangle, CheckCircle, X,
  IndianRupee, Calendar, RefreshCw, ChevronDown, Eye,
  Play, Pause, Users, TrendingUp
} from 'lucide-react';
import { showToast } from '../utils/toast';


const PaymentReminders = () => {
  const [pendingReminders, setPendingReminders] = useState([]);
  const [reminderHistory, setReminderHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('pending');
  const [selectedCustomers, setSelectedCustomers] = useState([]);
  const [showSettings, setShowSettings] = useState(false);
  const [showPreview, setShowPreview] = useState(null);
  const [sending, setSending] = useState(false);
  
  // Filters
  const [minDaysOverdue, setMinDaysOverdue] = useState(0);
  const [minAmount, setMinAmount] = useState(0);

  useEffect(() => {
    fetchData();
  }, [minDaysOverdue, minAmount]);

  const fetchData = async () => {
    setLoading(true);
    await Promise.all([
      fetchPendingReminders(),
      fetchHistory(),
      fetchStats(),
      fetchSettings()
    ]);
    setLoading(false);
  };

  const fetchPendingReminders = async () => {
    try {
      const params = new URLSearchParams();
      if (minDaysOverdue > 0) params.append('min_days_overdue', minDaysOverdue);
      if (minAmount > 0) params.append('min_amount', minAmount);
      
      const response = await fetch(`${BACKEND_URL}/api/payment-reminders/pending?${params}`);
      const data = await response.json();
      if (data.status === 'success') {
        setPendingReminders(data.reminders || []);
      }
    } catch (error) {
      console.error('Failed to fetch pending reminders:', error);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/payment-reminders/history?limit=50`);
      const data = await response.json();
      if (data.status === 'success') {
        setReminderHistory(data.history || []);
      }
    } catch (error) {
      console.error('Failed to fetch history:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/payment-reminders/stats`);
      const data = await response.json();
      if (data.status === 'success') {
        setStats(data.stats || {});
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const fetchSettings = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/payment-reminders/settings`);
      const data = await response.json();
      if (data.status === 'success') {
        setSettings(data.settings || {});
      }
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    }
  };

  const handleSelectAll = () => {
    if (selectedCustomers.length === pendingReminders.length) {
      setSelectedCustomers([]);
    } else {
      setSelectedCustomers(pendingReminders.map(r => r.id));
    }
  };

  const handleSelectCustomer = (id) => {
    if (selectedCustomers.includes(id)) {
      setSelectedCustomers(selectedCustomers.filter(c => c !== id));
    } else {
      setSelectedCustomers([...selectedCustomers, id]);
    }
  };

  const handleSendReminders = async () => {
    if (selectedCustomers.length === 0) {
      showToast.error('Please select at least one customer');
      return;
    }

    setSending(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/payment-reminders/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ledger_ids: selectedCustomers,
          message_type: 'email'
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success(data.message);
        setSelectedCustomers([]);
        setTimeout(() => {
          fetchHistory();
          fetchStats();
          fetchPendingReminders();
        }, 2000);
      } else {
        showToast.error(data.detail || 'Failed to send reminders');
      }
    } catch (error) {
      showToast.error('Failed to send reminders');
    } finally {
      setSending(false);
    }
  };

  const handleTriggerAutoReminders = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/payment-reminders/trigger-auto`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success(data.message);
        setTimeout(() => {
          fetchHistory();
          fetchStats();
        }, 2000);
      } else {
        showToast.info(data.message);
      }
    } catch (error) {
      showToast.error('Failed to trigger auto reminders');
    }
  };

  const handleUpdateSettings = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/payment-reminders/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success('Settings updated');
        setShowSettings(false);
      } else {
        showToast.error('Failed to update settings');
      }
    } catch (error) {
      showToast.error('Failed to update settings');
    }
  };

  const getReminderTypeColor = (type) => {
    switch(type) {
      case 'final': return 'text-red-600 bg-red-100';
      case 'urgent': return 'text-orange-600 bg-orange-100';
      case 'friendly': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const totalOutstanding = pendingReminders.reduce((sum, r) => sum + (r.outstanding_amount || 0), 0);

  return (
    <div className="p-6 bg-gray-50 min-h-screen" data-testid="payment-reminders-page">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Bell className="text-purple-600" />
              Payment Reminders
            </h1>
            <p className="text-gray-600 mt-1">Automated reminders for outstanding customer balances</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleTriggerAutoReminders}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <Play size={18} />
              Run Auto Reminders
            </button>
            <button
              onClick={() => setShowSettings(true)}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <Settings size={18} />
              Settings
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 border-b border-gray-200">
          {[
            { id: 'pending', label: 'Pending Reminders', icon: Clock, count: pendingReminders.length },
            { id: 'history', label: 'History', icon: Mail }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 flex items-center gap-2 border-b-2 transition ${
                activeTab === tab.id 
                  ? 'border-purple-500 text-purple-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon size={18} />
              {tab.label}
              {tab.count !== undefined && (
                <span className="px-2 py-0.5 bg-purple-100 text-purple-600 rounded-full text-xs">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Total Reminders Sent</p>
            <p className="text-2xl font-bold text-purple-600">{stats.total_reminders_sent || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Customers Reminded</p>
            <p className="text-2xl font-bold text-blue-600">{stats.unique_customers_reminded || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Outstanding Reminded</p>
            <p className="text-2xl font-bold text-orange-600">₹{(stats.total_outstanding_reminded || 0).toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Pending to Remind</p>
            <p className="text-2xl font-bold text-red-600">₹{totalOutstanding.toLocaleString()}</p>
          </div>
        </div>
      )}

      {/* Pending Tab */}
      {activeTab === 'pending' && (
        <div className="bg-white rounded-lg shadow">
          {/* Filters & Actions */}
          <div className="p-4 border-b flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <label className="text-sm text-gray-600">Min Days Overdue:</label>
                <select
                  value={minDaysOverdue}
                  onChange={(e) => setMinDaysOverdue(parseInt(e.target.value))}
                  className="px-3 py-1 border border-gray-300 rounded"
                >
                  <option value={0}>All</option>
                  <option value={7}>7+ days</option>
                  <option value={15}>15+ days</option>
                  <option value={30}>30+ days</option>
                  <option value={45}>45+ days</option>
                </select>
              </div>
              <div className="flex items-center gap-2">
                <label className="text-sm text-gray-600">Min Amount:</label>
                <select
                  value={minAmount}
                  onChange={(e) => setMinAmount(parseInt(e.target.value))}
                  className="px-3 py-1 border border-gray-300 rounded"
                >
                  <option value={0}>All</option>
                  <option value={1000}>₹1,000+</option>
                  <option value={5000}>₹5,000+</option>
                  <option value={10000}>₹10,000+</option>
                  <option value={25000}>₹25,000+</option>
                </select>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">
                {selectedCustomers.length} selected
              </span>
              <button
                onClick={handleSendReminders}
                disabled={selectedCustomers.length === 0 || sending}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
              >
                {sending ? (
                  <>
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                    Sending...
                  </>
                ) : (
                  <>
                    <Send size={18} />
                    Send Reminders
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Customer List */}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left">
                    <input
                      type="checkbox"
                      checked={selectedCustomers.length === pendingReminders.length && pendingReminders.length > 0}
                      onChange={handleSelectAll}
                      className="rounded"
                    />
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Customer</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Contact</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">Outstanding</th>
                  <th className="px-4 py-3 text-center text-sm font-medium text-gray-700">Days Overdue</th>
                  <th className="px-4 py-3 text-center text-sm font-medium text-gray-700">Reminders Sent</th>
                  <th className="px-4 py-3 text-center text-sm font-medium text-gray-700">Type</th>
                  <th className="px-4 py-3 text-center text-sm font-medium text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center">
                      <div className="animate-spin h-8 w-8 border-b-2 border-purple-500 rounded-full mx-auto"></div>
                    </td>
                  </tr>
                ) : pendingReminders.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-gray-500">
                      <CheckCircle size={48} className="mx-auto mb-3 text-green-300" />
                      <p className="font-medium">All caught up!</p>
                      <p className="text-sm">No pending payment reminders</p>
                    </td>
                  </tr>
                ) : (
                  pendingReminders.map((reminder) => (
                    <tr key={reminder.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <input
                          type="checkbox"
                          checked={selectedCustomers.includes(reminder.id)}
                          onChange={() => handleSelectCustomer(reminder.id)}
                          className="rounded"
                        />
                      </td>
                      <td className="px-4 py-3">
                        <p className="font-medium text-gray-900">{reminder.name}</p>
                      </td>
                      <td className="px-4 py-3">
                        <p className="text-sm text-gray-600">{reminder.email || '-'}</p>
                        <p className="text-xs text-gray-400">{reminder.phone || '-'}</p>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <p className="font-bold text-red-600">₹{(reminder.outstanding_amount || 0).toLocaleString()}</p>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-sm ${
                          reminder.days_overdue > 30 ? 'bg-red-100 text-red-600' :
                          reminder.days_overdue > 15 ? 'bg-orange-100 text-orange-600' :
                          'bg-yellow-100 text-yellow-600'
                        }`}>
                          <Clock size={14} />
                          {reminder.days_overdue} days
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className="font-medium">{reminder.reminder_count || 0}</span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getReminderTypeColor(reminder.suggested_reminder_type)}`}>
                          {reminder.suggested_reminder_type?.toUpperCase() || 'STANDARD'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <button
                          onClick={() => setShowPreview(reminder)}
                          className="p-2 text-gray-400 hover:text-purple-600"
                          title="Preview"
                        >
                          <Eye size={18} />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h2 className="font-semibold">Reminder History</h2>
          </div>
          <div className="divide-y max-h-[600px] overflow-y-auto">
            {reminderHistory.length === 0 ? (
              <div className="p-12 text-center text-gray-500">
                <Mail size={48} className="mx-auto mb-3 text-gray-300" />
                <p>No reminders sent yet</p>
              </div>
            ) : (
              reminderHistory.map((entry) => (
                <div key={entry.id} className="p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-gray-900">{entry.customer_name}</p>
                      <p className="text-sm text-gray-500">{entry.customer_email}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs bg-purple-100 text-purple-600 px-2 py-0.5 rounded">
                          Reminder #{entry.reminder_number}
                        </span>
                        <span className="text-xs text-gray-400">
                          {new Date(entry.sent_at).toLocaleString()}
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-gray-900">₹{(entry.outstanding_amount || 0).toLocaleString()}</p>
                      <p className={`text-xs ${entry.status === 'sent' ? 'text-green-600' : 'text-red-600'}`}>
                        {entry.status?.toUpperCase()}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Settings Modal */}
      {showSettings && settings && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6 border-b bg-purple-600">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold text-white">Reminder Settings</h2>
                <button onClick={() => setShowSettings(false)} className="text-white hover:text-gray-200">
                  <X size={24} />
                </button>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={settings.enabled}
                    onChange={(e) => setSettings({...settings, enabled: e.target.checked})}
                    className="rounded"
                  />
                  <span className="font-medium">Enable Automatic Reminders</span>
                </label>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Minimum Outstanding Amount (₹)
                </label>
                <input
                  type="number"
                  value={settings.min_amount || 0}
                  onChange={(e) => setSettings({...settings, min_amount: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Reminder Schedule (days after due)
                </label>
                <div className="flex gap-2">
                  {(settings.reminder_days || [7, 15, 30]).map((day, idx) => (
                    <input
                      key={idx}
                      type="number"
                      value={day}
                      onChange={(e) => {
                        const newDays = [...(settings.reminder_days || [7, 15, 30])];
                        newDays[idx] = parseInt(e.target.value) || 0;
                        setSettings({...settings, reminder_days: newDays});
                      }}
                      className="w-20 px-3 py-2 border border-gray-300 rounded-lg text-center"
                    />
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-1">Days after last transaction to send reminders</p>
              </div>
              
              <div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={settings.escalation_enabled}
                    onChange={(e) => setSettings({...settings, escalation_enabled: e.target.checked})}
                    className="rounded"
                  />
                  <span className="text-sm">Enable escalation after</span>
                  <input
                    type="number"
                    value={settings.escalation_days || 45}
                    onChange={(e) => setSettings({...settings, escalation_days: parseInt(e.target.value) || 45})}
                    className="w-16 px-2 py-1 border border-gray-300 rounded text-center text-sm"
                    disabled={!settings.escalation_enabled}
                  />
                  <span className="text-sm">days</span>
                </label>
              </div>
            </div>
            <div className="p-6 border-t bg-gray-50 flex justify-end gap-2">
              <button
                onClick={() => setShowSettings(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                onClick={handleUpdateSettings}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                Save Settings
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {showPreview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
            <div className="p-6 border-b">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold">Customer Details</h2>
                <button onClick={() => setShowPreview(null)} className="text-gray-500 hover:text-gray-700">
                  <X size={24} />
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-500">Customer Name</p>
                  <p className="font-bold text-lg">{showPreview.name}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Email</p>
                    <p className="font-medium">{showPreview.email || 'Not available'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Phone</p>
                    <p className="font-medium">{showPreview.phone || 'Not available'}</p>
                  </div>
                </div>
                <div className="p-4 bg-red-50 rounded-lg">
                  <p className="text-sm text-red-600">Outstanding Amount</p>
                  <p className="text-2xl font-bold text-red-700">
                    ₹{(showPreview.outstanding_amount || 0).toLocaleString()}
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-gray-50 rounded">
                    <p className="text-sm text-gray-500">Days Overdue</p>
                    <p className="font-bold">{showPreview.days_overdue} days</p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded">
                    <p className="text-sm text-gray-500">Reminders Sent</p>
                    <p className="font-bold">{showPreview.reminder_count || 0}</p>
                  </div>
                </div>
                {showPreview.last_reminder_sent && (
                  <div>
                    <p className="text-sm text-gray-500">Last Reminder</p>
                    <p className="font-medium">{new Date(showPreview.last_reminder_sent).toLocaleString()}</p>
                  </div>
                )}
              </div>
            </div>
            <div className="p-6 border-t bg-gray-50 flex justify-end gap-2">
              <button
                onClick={() => setShowPreview(null)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                Close
              </button>
              <button
                onClick={() => {
                  setSelectedCustomers([showPreview.id]);
                  setShowPreview(null);
                  handleSendReminders();
                }}
                disabled={!showPreview.email}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
              >
                <Send size={18} />
                Send Reminder
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PaymentReminders;
