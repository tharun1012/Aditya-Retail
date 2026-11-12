import React, { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Shield, 
  AlertCircle, 
  Clock, 
  CheckCircle, 
  Lock, 
  Unlock,
  FileText,
  Users,
  TrendingUp,
  Calendar,
  IndianRupee,
  ChevronRight,
  RefreshCw,
  Download,
  Eye,
  AlertTriangle
} from 'lucide-react';


const ComplianceAudits = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [msmeCompliance, setMsmeCompliance] = useState(null);
  const [overdueInvoices, setOverdueInvoices] = useState(null);
  const [lockedInvoices, setLockedInvoices] = useState(null);
  const [overdueSales, setOverdueSales] = useState(null);
  const [auditTrail, setAuditTrail] = useState([]);
  const [unlockModal, setUnlockModal] = useState({ show: false, invoice: null });
  const [unlockReason, setUnlockReason] = useState('');
  const [requestedBy, setRequestedBy] = useState('');

  const fetchMsmeCompliance = useCallback(async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/purchase-bills/compliance/msme-pending`);
      const data = await response.json();
      if (data.status === 'success') {
        setMsmeCompliance(data);
      }
    } catch (error) {
      console.error('Failed to fetch MSME compliance:', error);
    }
  }, []);

  const fetchOverdueInvoices = useCallback(async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/purchase-bills/compliance/overdue-invoices`);
      const data = await response.json();
      if (data.status === 'success') {
        setOverdueInvoices(data);
      }
    } catch (error) {
      console.error('Failed to fetch overdue invoices:', error);
    }
  }, []);

  const fetchLockedInvoices = useCallback(async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/orders/compliance/locked-invoices`);
      const data = await response.json();
      if (data.status === 'success') {
        setLockedInvoices(data);
      }
    } catch (error) {
      console.error('Failed to fetch locked invoices:', error);
    }
  }, []);

  const fetchOverdueSales = useCallback(async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/orders/compliance/overdue-sales`);
      const data = await response.json();
      if (data.status === 'success') {
        setOverdueSales(data);
      }
    } catch (error) {
      console.error('Failed to fetch overdue sales:', error);
    }
  }, []);

  const fetchAuditTrail = useCallback(async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/financial-reports/audit-trail?limit=50`);
      const data = await response.json();
      if (data.status === 'success') {
        setAuditTrail(data.records || []);
      }
    } catch (error) {
      console.error('Failed to fetch audit trail:', error);
    }
  }, []);

  const fetchAllData = useCallback(async () => {
    setLoading(true);
    await Promise.all([
      fetchMsmeCompliance(),
      fetchOverdueInvoices(),
      fetchLockedInvoices(),
      fetchOverdueSales(),
      fetchAuditTrail()
    ]);
    setLoading(false);
  }, [fetchMsmeCompliance, fetchOverdueInvoices, fetchLockedInvoices, fetchOverdueSales, fetchAuditTrail]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  const handleUnlockInvoice = async () => {
    if (!unlockReason || !requestedBy) {
      alert('Please provide both reason and requester name');
      return;
    }

    try {
      const response = await fetch(
        `${BACKEND_URL}/api/admin/orders/${unlockModal.invoice.order_id}/unlock?unlock_reason=${encodeURIComponent(unlockReason)}&requested_by=${encodeURIComponent(requestedBy)}&approved_by_super_admin=true`,
        { method: 'POST' }
      );
      const data = await response.json();
      if (data.status === 'success') {
        alert('Invoice unlocked successfully');
        setUnlockModal({ show: false, invoice: null });
        setUnlockReason('');
        setRequestedBy('');
        fetchLockedInvoices();
        fetchOverdueSales();
      } else {
        alert(data.detail || 'Failed to unlock invoice');
      }
    } catch (error) {
      alert('Error unlocking invoice');
    }
  };

  const tabs = [
    { id: 'overview', name: 'Overview', icon: Shield },
    { id: 'msme', name: 'MSME Compliance', icon: Users },
    { id: 'purchase-overdue', name: 'Purchase Overdue', icon: AlertCircle },
    { id: 'sales-locked', name: 'Sales Locked', icon: Lock },
    { id: 'audit-trail', name: 'Audit Trail', icon: FileText }
  ];

  // Calculate summary stats
  const summaryStats = {
    msmeOverdue: msmeCompliance?.compliance_summary?.critical_count || 0,
    msmeOverdueAmount: msmeCompliance?.compliance_summary?.critical_amount || 0,
    msmeDueSoon: msmeCompliance?.compliance_summary?.warning_count || 0,
    purchaseOverdue: overdueInvoices?.summary?.total_overdue_count || 0,
    purchaseOverdueAmount: overdueInvoices?.summary?.total_overdue_amount || 0,
    salesLocked: lockedInvoices?.total_locked || 0,
    salesLockedAmount: lockedInvoices?.total_locked_amount || 0
  };

  const hasAlerts = summaryStats.msmeOverdue > 0 || summaryStats.purchaseOverdue > 0 || summaryStats.salesLocked > 0;

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Shield className="text-indigo-600" size={28} />
            Compliance & Audits
          </h1>
          <p className="text-gray-600">Monitor MSME compliance, overdue payments, and locked invoices</p>
        </div>
        <button
          onClick={fetchAllData}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
          disabled={loading}
        >
          <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Alert Banner */}
      {hasAlerts && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="text-red-600 flex-shrink-0" size={24} />
            <div>
              <h3 className="font-bold text-red-800">Compliance Alerts Require Attention</h3>
              <div className="text-red-700 text-sm mt-1 space-y-1">
                {summaryStats.msmeOverdue > 0 && (
                  <p>• {summaryStats.msmeOverdue} MSME payment(s) overdue - ₹{summaryStats.msmeOverdueAmount.toLocaleString('en-IN')}</p>
                )}
                {summaryStats.purchaseOverdue > 0 && (
                  <p>• {summaryStats.purchaseOverdue} purchase invoice(s) overdue - ₹{summaryStats.purchaseOverdueAmount.toLocaleString('en-IN')}</p>
                )}
                {summaryStats.salesLocked > 0 && (
                  <p>• {summaryStats.salesLocked} sales invoice(s) locked - ₹{summaryStats.salesLockedAmount.toLocaleString('en-IN')}</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-lg whitespace-nowrap text-sm font-medium transition-colors flex items-center gap-2 ${
              activeTab === tab.id
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <tab.icon size={18} />
            {tab.name}
            {tab.id === 'msme' && summaryStats.msmeOverdue > 0 && (
              <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">{summaryStats.msmeOverdue}</span>
            )}
            {tab.id === 'purchase-overdue' && summaryStats.purchaseOverdue > 0 && (
              <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">{summaryStats.purchaseOverdue}</span>
            )}
            {tab.id === 'sales-locked' && summaryStats.salesLocked > 0 && (
              <span className="bg-orange-500 text-white text-xs px-2 py-0.5 rounded-full">{summaryStats.salesLocked}</span>
            )}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      ) : (
        <>
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className={`rounded-lg p-4 ${summaryStats.msmeOverdue > 0 ? 'bg-red-50 border-2 border-red-300' : 'bg-green-50 border border-green-200'}`}>
                  <div className="flex items-center gap-3">
                    <div className={`p-3 rounded-lg ${summaryStats.msmeOverdue > 0 ? 'bg-red-100' : 'bg-green-100'}`}>
                      <Users className={summaryStats.msmeOverdue > 0 ? 'text-red-600' : 'text-green-600'} size={24} />
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">MSME Overdue</p>
                      <p className={`text-2xl font-bold ${summaryStats.msmeOverdue > 0 ? 'text-red-700' : 'text-green-700'}`}>
                        {summaryStats.msmeOverdue}
                      </p>
                      {summaryStats.msmeOverdue > 0 && (
                        <p className="text-xs text-red-600">₹{summaryStats.msmeOverdueAmount.toLocaleString('en-IN')}</p>
                      )}
                    </div>
                  </div>
                </div>

                <div className={`rounded-lg p-4 ${summaryStats.msmeDueSoon > 0 ? 'bg-yellow-50 border-2 border-yellow-300' : 'bg-gray-50 border border-gray-200'}`}>
                  <div className="flex items-center gap-3">
                    <div className={`p-3 rounded-lg ${summaryStats.msmeDueSoon > 0 ? 'bg-yellow-100' : 'bg-gray-100'}`}>
                      <Clock className={summaryStats.msmeDueSoon > 0 ? 'text-yellow-600' : 'text-gray-600'} size={24} />
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">MSME Due Soon</p>
                      <p className={`text-2xl font-bold ${summaryStats.msmeDueSoon > 0 ? 'text-yellow-700' : 'text-gray-700'}`}>
                        {summaryStats.msmeDueSoon}
                      </p>
                      <p className="text-xs text-gray-500">Within 7 days</p>
                    </div>
                  </div>
                </div>

                <div className={`rounded-lg p-4 ${summaryStats.purchaseOverdue > 0 ? 'bg-orange-50 border-2 border-orange-300' : 'bg-green-50 border border-green-200'}`}>
                  <div className="flex items-center gap-3">
                    <div className={`p-3 rounded-lg ${summaryStats.purchaseOverdue > 0 ? 'bg-orange-100' : 'bg-green-100'}`}>
                      <AlertCircle className={summaryStats.purchaseOverdue > 0 ? 'text-orange-600' : 'text-green-600'} size={24} />
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Purchase Overdue</p>
                      <p className={`text-2xl font-bold ${summaryStats.purchaseOverdue > 0 ? 'text-orange-700' : 'text-green-700'}`}>
                        {summaryStats.purchaseOverdue}
                      </p>
                      {summaryStats.purchaseOverdue > 0 && (
                        <p className="text-xs text-orange-600">₹{summaryStats.purchaseOverdueAmount.toLocaleString('en-IN')}</p>
                      )}
                    </div>
                  </div>
                </div>

                <div className={`rounded-lg p-4 ${summaryStats.salesLocked > 0 ? 'bg-purple-50 border-2 border-purple-300' : 'bg-green-50 border border-green-200'}`}>
                  <div className="flex items-center gap-3">
                    <div className={`p-3 rounded-lg ${summaryStats.salesLocked > 0 ? 'bg-purple-100' : 'bg-green-100'}`}>
                      <Lock className={summaryStats.salesLocked > 0 ? 'text-purple-600' : 'text-green-600'} size={24} />
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Sales Locked</p>
                      <p className={`text-2xl font-bold ${summaryStats.salesLocked > 0 ? 'text-purple-700' : 'text-green-700'}`}>
                        {summaryStats.salesLocked}
                      </p>
                      {summaryStats.salesLocked > 0 && (
                        <p className="text-xs text-purple-600">₹{summaryStats.salesLockedAmount.toLocaleString('en-IN')}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">Compliance Status</h3>
                <div className="space-y-3">
                  {summaryStats.msmeOverdue === 0 && summaryStats.msmeDueSoon === 0 && summaryStats.purchaseOverdue === 0 && summaryStats.salesLocked === 0 ? (
                    <div className="flex items-center gap-3 text-green-700 bg-green-50 p-4 rounded-lg">
                      <CheckCircle size={24} />
                      <div>
                        <p className="font-semibold">All Clear!</p>
                        <p className="text-sm">No compliance issues found. All payments and invoices are up to date.</p>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <p className="text-gray-600 text-sm">Click on the tabs above to view detailed information and take action.</p>
                      <div className="grid grid-cols-2 gap-4 mt-4">
                        {summaryStats.msmeOverdue > 0 && (
                          <button 
                            onClick={() => setActiveTab('msme')}
                            className="p-3 bg-red-50 border border-red-200 rounded-lg text-left hover:bg-red-100"
                          >
                            <p className="font-semibold text-red-800">Clear MSME Dues</p>
                            <p className="text-sm text-red-600">Interest applicable as per MSMED Act</p>
                          </button>
                        )}
                        {summaryStats.salesLocked > 0 && (
                          <button 
                            onClick={() => setActiveTab('sales-locked')}
                            className="p-3 bg-purple-50 border border-purple-200 rounded-lg text-left hover:bg-purple-100"
                          >
                            <p className="font-semibold text-purple-800">Review Locked Invoices</p>
                            <p className="text-sm text-purple-600">Super admin can unlock with reason</p>
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* MSME Compliance Tab */}
          {activeTab === 'msme' && msmeCompliance && (
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <p className="text-blue-800 text-sm">
                  <strong>MSMED Act 2006:</strong> Payment to MSME vendors must be made within 45 days. 
                  Interest at 3x bank rate is applicable on delayed payments.
                </p>
              </div>

              {/* Critical - Overdue */}
              {msmeCompliance.critical_overdue?.length > 0 && (
                <div className="bg-white rounded-lg shadow">
                  <div className="p-4 border-b bg-red-50">
                    <h3 className="font-semibold text-red-800 flex items-center gap-2">
                      <AlertCircle size={20} />
                      Critical - Overdue ({msmeCompliance.critical_overdue.length})
                    </h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Bill Number</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Vendor</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">MSME/Udyam</th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500">Amount</th>
                          <th className="px-4 py-3 text-center text-xs font-medium text-gray-500">Due Date</th>
                          <th className="px-4 py-3 text-center text-xs font-medium text-gray-500">Days Overdue</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {msmeCompliance.critical_overdue.map((bill, index) => (
                          <tr key={index} className="bg-red-50">
                            <td className="px-4 py-3 text-sm font-medium">{bill.bill_number}</td>
                            <td className="px-4 py-3 text-sm">{bill.vendor_name}</td>
                            <td className="px-4 py-3 text-sm text-blue-600">{bill.msme_udyam_number || '-'}</td>
                            <td className="px-4 py-3 text-sm text-right font-semibold">₹{bill.grand_total?.toLocaleString('en-IN')}</td>
                            <td className="px-4 py-3 text-sm text-center">{bill.due_date}</td>
                            <td className="px-4 py-3 text-center">
                              <span className="px-2 py-1 bg-red-600 text-white text-xs rounded-full font-bold">
                                {bill.days_overdue} days
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Warning - Due Soon */}
              {msmeCompliance.warning_due_soon?.length > 0 && (
                <div className="bg-white rounded-lg shadow">
                  <div className="p-4 border-b bg-yellow-50">
                    <h3 className="font-semibold text-yellow-800 flex items-center gap-2">
                      <Clock size={20} />
                      Due Soon - Within 7 Days ({msmeCompliance.warning_due_soon.length})
                    </h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Bill Number</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Vendor</th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500">Amount</th>
                          <th className="px-4 py-3 text-center text-xs font-medium text-gray-500">Due Date</th>
                          <th className="px-4 py-3 text-center text-xs font-medium text-gray-500">Days Left</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {msmeCompliance.warning_due_soon.map((bill, index) => (
                          <tr key={index}>
                            <td className="px-4 py-3 text-sm font-medium">{bill.bill_number}</td>
                            <td className="px-4 py-3 text-sm">{bill.vendor_name}</td>
                            <td className="px-4 py-3 text-sm text-right font-semibold">₹{bill.grand_total?.toLocaleString('en-IN')}</td>
                            <td className="px-4 py-3 text-sm text-center">{bill.due_date}</td>
                            <td className="px-4 py-3 text-center">
                              <span className="px-2 py-1 bg-yellow-500 text-white text-xs rounded-full">
                                {bill.days_remaining} days
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {msmeCompliance.critical_overdue?.length === 0 && msmeCompliance.warning_due_soon?.length === 0 && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
                  <CheckCircle className="mx-auto text-green-600 mb-2" size={48} />
                  <p className="text-green-800 font-semibold">No MSME Compliance Issues</p>
                  <p className="text-green-600 text-sm">All MSME vendor payments are up to date</p>
                </div>
              )}
            </div>
          )}

          {/* Purchase Overdue Tab */}
          {activeTab === 'purchase-overdue' && overdueInvoices && (
            <div className="space-y-6">
              {overdueInvoices.overdue_invoices?.length > 0 ? (
                <div className="bg-white rounded-lg shadow">
                  <div className="p-4 border-b">
                    <h3 className="font-semibold">Overdue Purchase Invoices ({overdueInvoices.summary?.total_overdue_count})</h3>
                    <p className="text-sm text-gray-600">Total Amount: ₹{overdueInvoices.summary?.total_overdue_amount?.toLocaleString('en-IN')}</p>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Bill Number</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Vendor</th>
                          <th className="px-4 py-3 text-center text-xs font-medium text-gray-500">Type</th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500">Amount</th>
                          <th className="px-4 py-3 text-center text-xs font-medium text-gray-500">Due Date</th>
                          <th className="px-4 py-3 text-center text-xs font-medium text-gray-500">Days Overdue</th>
                          <th className="px-4 py-3 text-center text-xs font-medium text-gray-500">Priority</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {overdueInvoices.overdue_invoices.map((bill, index) => (
                          <tr key={index} className={bill.is_msme ? 'bg-red-50' : ''}>
                            <td className="px-4 py-3 text-sm font-medium">{bill.bill_number}</td>
                            <td className="px-4 py-3 text-sm">{bill.vendor_name}</td>
                            <td className="px-4 py-3 text-center">
                              {bill.is_msme ? (
                                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">MSME</span>
                              ) : (
                                <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded">Regular</span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-sm text-right font-semibold">₹{bill.grand_total?.toLocaleString('en-IN')}</td>
                            <td className="px-4 py-3 text-sm text-center">{bill.due_date}</td>
                            <td className="px-4 py-3 text-center">
                              <span className="px-2 py-1 bg-red-600 text-white text-xs rounded-full">
                                {bill.days_overdue} days
                              </span>
                            </td>
                            <td className="px-4 py-3 text-center">
                              <span className={`px-2 py-1 text-xs rounded ${bill.priority === 'CRITICAL' ? 'bg-red-600 text-white' : 'bg-orange-500 text-white'}`}>
                                {bill.priority}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
                  <CheckCircle className="mx-auto text-green-600 mb-2" size={48} />
                  <p className="text-green-800 font-semibold">No Overdue Purchase Invoices</p>
                  <p className="text-green-600 text-sm">All purchase payments are on schedule</p>
                </div>
              )}
            </div>
          )}

          {/* Sales Locked Tab */}
          {activeTab === 'sales-locked' && (
            <div className="space-y-6">
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-4">
                <p className="text-purple-800 text-sm">
                  <strong>Invoice Locking Policy:</strong> Overdue sales invoices are automatically locked. 
                  Only super_admin can unlock with a valid reason. All unlock actions are logged for audit.
                </p>
              </div>

              {lockedInvoices?.locked_invoices?.length > 0 ? (
                <div className="bg-white rounded-lg shadow">
                  <div className="p-4 border-b">
                    <h3 className="font-semibold">Locked Sales Invoices ({lockedInvoices.total_locked})</h3>
                    <p className="text-sm text-gray-600">Total Amount: ₹{lockedInvoices.total_locked_amount?.toLocaleString('en-IN')}</p>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Invoice #</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Customer</th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500">Amount</th>
                          <th className="px-4 py-3 text-center text-xs font-medium text-gray-500">Locked At</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Reason</th>
                          <th className="px-4 py-3 text-center text-xs font-medium text-gray-500">Action</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {lockedInvoices.locked_invoices.map((invoice, index) => (
                          <tr key={index}>
                            <td className="px-4 py-3 text-sm font-medium">{invoice.order_number}</td>
                            <td className="px-4 py-3 text-sm">{invoice.customer_name}</td>
                            <td className="px-4 py-3 text-sm text-right font-semibold">₹{invoice.total_amount?.toLocaleString('en-IN')}</td>
                            <td className="px-4 py-3 text-sm text-center">{invoice.locked_at?.split('T')[0]}</td>
                            <td className="px-4 py-3 text-sm text-gray-600">{invoice.locked_reason}</td>
                            <td className="px-4 py-3 text-center">
                              <button
                                onClick={() => setUnlockModal({ show: true, invoice })}
                                className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 flex items-center gap-1 mx-auto"
                              >
                                <Unlock size={14} />
                                Unlock
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
                  <CheckCircle className="mx-auto text-green-600 mb-2" size={48} />
                  <p className="text-green-800 font-semibold">No Locked Invoices</p>
                  <p className="text-green-600 text-sm">All sales invoices are active and accessible</p>
                </div>
              )}
            </div>
          )}

          {/* Audit Trail Tab */}
          {activeTab === 'audit-trail' && (
            <div className="bg-white rounded-lg shadow">
              <div className="p-4 border-b">
                <h3 className="font-semibold">Recent Audit Trail</h3>
                <p className="text-sm text-gray-600">Last 50 financial actions</p>
              </div>
              {auditTrail.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Timestamp</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Action</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Entity</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Details</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">User</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {auditTrail.map((record, index) => (
                        <tr key={index}>
                          <td className="px-4 py-3 text-sm">{record.timestamp?.split('T')[0]}</td>
                          <td className="px-4 py-3 text-sm">
                            <span className={`px-2 py-1 rounded text-xs ${
                              record.action?.includes('UNLOCK') ? 'bg-green-100 text-green-800' :
                              record.action?.includes('LOCK') ? 'bg-red-100 text-red-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {record.action}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm">{record.entity_type} - {record.entity_id?.slice(0, 8)}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">{record.unlock_reason || record.details || '-'}</td>
                          <td className="px-4 py-3 text-sm">{record.requested_by || record.user || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="p-6 text-center text-gray-500">
                  No audit records found
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Unlock Modal */}
      {unlockModal.show && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Unlock className="text-green-600" size={24} />
              Unlock Invoice
            </h3>
            <p className="text-gray-600 text-sm mb-4">
              Invoice: <strong>{unlockModal.invoice?.order_number}</strong><br />
              Amount: <strong>₹{unlockModal.invoice?.total_amount?.toLocaleString('en-IN')}</strong>
            </p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Requested By *</label>
                <input
                  type="text"
                  value={requestedBy}
                  onChange={(e) => setRequestedBy(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="Store Manager / Sales Rep name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Reason for Unlock *</label>
                <textarea
                  value={unlockReason}
                  onChange={(e) => setUnlockReason(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg"
                  rows={3}
                  placeholder="Provide valid reason for unlocking..."
                />
              </div>
              <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm text-yellow-800">
                <strong>Note:</strong> This action will be logged in the audit trail with your approval as super_admin.
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => {
                  setUnlockModal({ show: false, invoice: null });
                  setUnlockReason('');
                  setRequestedBy('');
                }}
                className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleUnlockInvoice}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Approve & Unlock
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComplianceAudits;
