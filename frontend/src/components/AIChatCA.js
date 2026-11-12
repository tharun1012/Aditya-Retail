import React, { useState, useEffect, useRef } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Bot, Send, Sparkles, TrendingUp, DollarSign, FileText, Loader, 
  Upload, AlertTriangle, Clock, CheckCircle, Mail, CreditCard,
  PieChart, BarChart3, ArrowUpRight, ArrowDownRight, RefreshCw,
  ClipboardCheck, Calendar, AlertCircle, Shield, FileSearch, XCircle
} from 'lucide-react';


const AIChatCA = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [quickStats, setQuickStats] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [activeTab, setActiveTab] = useState('chat');
  const [unpaidInvoices, setUnpaidInvoices] = useState(null);
  const [overdueVendors, setOverdueVendors] = useState(null);
  const [bankAnalysis, setBankAnalysis] = useState(null);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [auditResult, setAuditResult] = useState(null);
  const [runningAudit, setRunningAudit] = useState(false);
  const [auditHistory, setAuditHistory] = useState([]);
  const [selectedPeriod, setSelectedPeriod] = useState('month');
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    setMessages([{
      type: 'ai',
      content: `👋 Hello! I'm your AI Chartered Accountant & Auditor. I can help you with:

• **Financial Reports** - Sales, Purchases, P&L, GST
• **Date-specific Queries** - "Show me sales for April 2025"
• **Audit & Compliance** - Daily/Weekly audits, error detection
• **Payment Tracking** - Unpaid invoices, vendor payments
• **Bank Statement Analysis** - Upload & analyze bank statements

Try asking: "What were my total sales in April 2025?" or "Run a daily audit"`,
      timestamp: new Date()
    }]);
    fetchQuickStats();
    setSuggestions([
      "Show me sales for April 2025",
      "What's my GST liability this month?",
      "Run a weekly audit",
      "Show profit & loss report"
    ]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchQuickStats = async (period = 'month') => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/ai-ca/quick-stats?period=${period}`);
      const data = await response.json();
      if (data.status === 'success') {
        setQuickStats(data.stats);
      }
    } catch (error) {
      console.error('Failed to fetch quick stats:', error);
    }
  };

  const fetchUnpaidInvoices = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/ai-ca/unpaid-invoices`);
      const data = await response.json();
      if (data.status === 'success') {
        setUnpaidInvoices(data);
      }
    } catch (error) {
      console.error('Failed to fetch unpaid invoices:', error);
    }
  };

  const fetchOverdueVendors = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/ai-ca/overdue-vendor-payments`);
      const data = await response.json();
      if (data.status === 'success') {
        setOverdueVendors(data);
      }
    } catch (error) {
      console.error('Failed to fetch overdue vendors:', error);
    }
  };

  const fetchAuditHistory = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/ai-ca/audit-history?limit=10`);
      const data = await response.json();
      if (data.status === 'success') {
        setAuditHistory(data.audits);
      }
    } catch (error) {
      console.error('Failed to fetch audit history:', error);
    }
  };

  const runAudit = async (auditType, startDate = null, endDate = null) => {
    setRunningAudit(true);
    try {
      const payload = { audit_type: auditType };
      if (startDate) payload.start_date = startDate;
      if (endDate) payload.end_date = endDate;

      const response = await fetch(`${BACKEND_URL}/api/ai-ca/audit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      
      if (data.audit_id) {
        setAuditResult(data);
        fetchAuditHistory();
      } else {
        alert('Audit failed: ' + (data.detail || 'Unknown error'));
      }
    } catch (error) {
      alert('Failed to run audit: ' + error.message);
    } finally {
      setRunningAudit(false);
    }
  };

  const sendPaymentReminder = async (invoiceId, reminderType) => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/ai-ca/send-payment-reminder?invoice_id=${invoiceId}&reminder_type=${reminderType}`,
        { method: 'POST' }
      );
      const data = await response.json();
      alert(data.message || 'Reminder sent!');
    } catch (error) {
      alert('Failed to send reminder');
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadingFile(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${BACKEND_URL}/api/ai-ca/analyze-bank-statement`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        setBankAnalysis(data.analysis);
        setActiveTab('bank');
      } else {
        alert('Failed to analyze: ' + (data.detail || 'Unknown error'));
      }
    } catch (error) {
      alert('Failed to upload and analyze file');
    } finally {
      setUploadingFile(false);
    }
  };

  const sendMessage = async (messageText = null) => {
    const textToSend = messageText || inputMessage.trim();
    if (!textToSend) return;

    const userMessage = {
      type: 'user',
      content: textToSend,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const adminUser = JSON.parse(localStorage.getItem('admin_user') || '{}');
      
      const response = await fetch(`${BACKEND_URL}/api/ai-ca/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: textToSend,
          user_role: adminUser.role || 'admin'
        })
      });

      const data = await response.json();

      const aiMessage = {
        type: 'ai',
        content: data.response,
        data: data.data,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
      
      if (data.suggestions && data.suggestions.length > 0) {
        setSuggestions(data.suggestions);
      }

      if (textToSend.toLowerCase().includes('sales') || 
          textToSend.toLowerCase().includes('expense') ||
          textToSend.toLowerCase().includes('profit')) {
        fetchQuickStats(selectedPeriod);
      }

    } catch (error) {
      const errorMessage = {
        type: 'ai',
        content: `❌ Sorry, I encountered an error: ${error.message}. Please try again.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Severity badge component
  const SeverityBadge = ({ severity }) => {
    const colors = {
      critical: 'bg-red-100 text-red-800 border-red-200',
      high: 'bg-orange-100 text-orange-800 border-orange-200',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      info: 'bg-blue-100 text-blue-800 border-blue-200',
      low: 'bg-gray-100 text-gray-800 border-gray-200'
    };
    return (
      <span className={`px-2 py-0.5 text-xs font-medium rounded border ${colors[severity] || colors.info}`}>
        {severity.toUpperCase()}
      </span>
    );
  };

  // Audit Tab
  const renderAuditTab = () => {
    return (
      <div className="p-4 space-y-6">
        {/* Audit Actions */}
        <div className="bg-white rounded-lg border p-4">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <ClipboardCheck className="w-5 h-5 text-blue-600" />
            Run Audit
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <button
              onClick={() => runAudit('daily')}
              disabled={runningAudit}
              className="px-4 py-3 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg text-blue-700 font-medium text-sm transition-colors disabled:opacity-50"
            >
              <Calendar className="w-4 h-4 mx-auto mb-1" />
              Daily Audit
            </button>
            <button
              onClick={() => runAudit('weekly')}
              disabled={runningAudit}
              className="px-4 py-3 bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-lg text-purple-700 font-medium text-sm transition-colors disabled:opacity-50"
            >
              <FileSearch className="w-4 h-4 mx-auto mb-1" />
              Weekly Audit
            </button>
            <button
              onClick={() => runAudit('monthly')}
              disabled={runningAudit}
              className="px-4 py-3 bg-green-50 hover:bg-green-100 border border-green-200 rounded-lg text-green-700 font-medium text-sm transition-colors disabled:opacity-50"
            >
              <Shield className="w-4 h-4 mx-auto mb-1" />
              Monthly Audit
            </button>
            <button
              onClick={() => {
                const startDate = prompt('Enter start date (YYYY-MM-DD):');
                const endDate = prompt('Enter end date (YYYY-MM-DD):');
                if (startDate && endDate) runAudit('custom', startDate, endDate);
              }}
              disabled={runningAudit}
              className="px-4 py-3 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-lg text-gray-700 font-medium text-sm transition-colors disabled:opacity-50"
            >
              <Calendar className="w-4 h-4 mx-auto mb-1" />
              Custom Range
            </button>
          </div>
          {runningAudit && (
            <div className="mt-4 flex items-center justify-center gap-2 text-blue-600">
              <Loader className="w-5 h-5 animate-spin" />
              Running audit... This may take a moment.
            </div>
          )}
        </div>

        {/* Audit Result */}
        {auditResult && (
          <div className="space-y-4">
            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-600">Transactions</p>
                <p className="text-2xl font-bold text-blue-700">{auditResult.summary?.total_transactions || 0}</p>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-sm text-green-600">Sales</p>
                <p className="text-xl font-bold text-green-700">₹{(auditResult.summary?.sales_total || 0).toLocaleString()}</p>
              </div>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <p className="text-sm text-purple-600">Purchases</p>
                <p className="text-xl font-bold text-purple-700">₹{(auditResult.summary?.purchase_total || 0).toLocaleString()}</p>
              </div>
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-600">Critical Issues</p>
                <p className="text-2xl font-bold text-red-700">{auditResult.summary?.critical_issues || 0}</p>
              </div>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-600">Warnings</p>
                <p className="text-2xl font-bold text-yellow-700">{auditResult.summary?.warnings || 0}</p>
              </div>
            </div>

            {/* AI Analysis */}
            {auditResult.ai_analysis && (
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                  <Bot className="w-5 h-5 text-purple-600" />
                  AI Analysis
                </h4>
                <p className="text-gray-700 whitespace-pre-wrap">{auditResult.ai_analysis}</p>
              </div>
            )}

            {/* Issues Found */}
            {auditResult.issues && auditResult.issues.length > 0 && (
              <div className="bg-white rounded-lg border">
                <div className="p-4 border-b">
                  <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-red-500" />
                    Issues Found ({auditResult.issues.length})
                  </h4>
                </div>
                <div className="divide-y max-h-[400px] overflow-y-auto">
                  {auditResult.issues.map((issue, i) => (
                    <div key={i} className="p-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <SeverityBadge severity={issue.severity} />
                            <span className="font-medium text-gray-900">{issue.type.replace(/_/g, ' ').toUpperCase()}</span>
                          </div>
                          <p className="text-gray-600 text-sm">{issue.message}</p>
                          {issue.details && issue.details.length > 0 && (
                            <div className="mt-2 text-xs text-gray-500">
                              <span className="font-medium">Affected: </span>
                              {typeof issue.details[0] === 'object' 
                                ? issue.details.slice(0, 3).map(d => d.order_id || d.bill_number || JSON.stringify(d)).join(', ')
                                : issue.details.slice(0, 5).join(', ')
                              }
                              {issue.details.length > 5 && ` (+${issue.details.length - 5} more)`}
                            </div>
                          )}
                        </div>
                        <span className="text-sm text-gray-500 font-medium">{issue.count} items</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* No Issues */}
            {auditResult.issues && auditResult.issues.length === 0 && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
                <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-2" />
                <h4 className="font-semibold text-green-800">No Issues Found!</h4>
                <p className="text-green-600 text-sm">All transactions are compliant and properly recorded.</p>
              </div>
            )}

            {/* Recommendations */}
            {auditResult.recommendations && auditResult.recommendations.length > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h4 className="font-semibold text-yellow-800 mb-3 flex items-center gap-2">
                  <Sparkles className="w-5 h-5" />
                  Recommendations
                </h4>
                <ul className="space-y-2">
                  {auditResult.recommendations.map((rec, i) => (
                    <li key={i} className="text-sm text-yellow-800 flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Audit History */}
        {!auditResult && (
          <div className="bg-white rounded-lg border">
            <div className="p-4 border-b flex justify-between items-center">
              <h4 className="font-semibold text-gray-900">Recent Audits</h4>
              <button onClick={fetchAuditHistory} className="text-gray-500 hover:text-gray-700">
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
            {auditHistory.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <ClipboardCheck className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>No audit history yet. Run your first audit above.</p>
              </div>
            ) : (
              <div className="divide-y max-h-[300px] overflow-y-auto">
                {auditHistory.map((audit, i) => (
                  <div key={i} className="p-4 hover:bg-gray-50 cursor-pointer" onClick={() => setAuditResult(audit)}>
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium text-gray-900">{audit.audit_type.toUpperCase()} Audit</p>
                        <p className="text-sm text-gray-500">
                          {audit.period?.start} to {audit.period?.end}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">
                          {audit.summary?.issues_found || 0} issues
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(audit.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Clear Result Button */}
        {auditResult && (
          <div className="text-center">
            <button
              onClick={() => setAuditResult(null)}
              className="text-gray-600 hover:text-gray-800 text-sm"
            >
              ← Back to Audit History
            </button>
          </div>
        )}
      </div>
    );
  };

  // Tab content renderers
  const renderUnpaidInvoices = () => {
    if (!unpaidInvoices) {
      return (
        <div className="p-8 text-center">
          <button
            onClick={fetchUnpaidInvoices}
            className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 flex items-center gap-2 mx-auto"
          >
            <RefreshCw className="w-5 h-5" />
            Load Unpaid Invoices
          </button>
        </div>
      );
    }

    return (
      <div className="p-4 space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-sm text-red-600">Total Outstanding</p>
            <p className="text-2xl font-bold text-red-700">₹{unpaidInvoices.total_outstanding?.toLocaleString()}</p>
          </div>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-sm text-yellow-600">0-30 Days</p>
            <p className="text-xl font-bold text-yellow-700">₹{unpaidInvoices.aging_summary?.['0_30_days']?.amount?.toLocaleString() || 0}</p>
            <p className="text-xs text-yellow-500">{unpaidInvoices.aging_summary?.['0_30_days']?.count || 0} invoices</p>
          </div>
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
            <p className="text-sm text-orange-600">31-60 Days</p>
            <p className="text-xl font-bold text-orange-700">₹{unpaidInvoices.aging_summary?.['31_60_days']?.amount?.toLocaleString() || 0}</p>
            <p className="text-xs text-orange-500">{unpaidInvoices.aging_summary?.['31_60_days']?.count || 0} invoices</p>
          </div>
          <div className="bg-red-100 border border-red-300 rounded-lg p-4">
            <p className="text-sm text-red-600">60+ Days</p>
            <p className="text-xl font-bold text-red-700">
              ₹{((unpaidInvoices.aging_summary?.['61_90_days']?.amount || 0) + (unpaidInvoices.aging_summary?.['over_90_days']?.amount || 0)).toLocaleString()}
            </p>
            <p className="text-xs text-red-500">
              {(unpaidInvoices.aging_summary?.['61_90_days']?.count || 0) + (unpaidInvoices.aging_summary?.['over_90_days']?.count || 0)} invoices
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg border">
          <div className="p-4 border-b flex justify-between items-center">
            <h3 className="font-semibold">Unpaid Invoices ({unpaidInvoices.total_invoices})</h3>
            <button onClick={fetchUnpaidInvoices} className="text-gray-500 hover:text-gray-700">
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
          <div className="divide-y max-h-[400px] overflow-y-auto">
            {unpaidInvoices.invoices?.slice(0, 20).map((invoice, i) => (
              <div key={i} className="p-4 flex items-center justify-between hover:bg-gray-50">
                <div>
                  <p className="font-medium">{invoice.customer_name || 'Unknown Customer'}</p>
                  <p className="text-sm text-gray-500">
                    {invoice.invoice_number} • {invoice.days_old} days old
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-red-600">₹{invoice.outstanding_amount?.toLocaleString()}</p>
                  <div className="flex gap-1 mt-1">
                    <button
                      onClick={() => sendPaymentReminder(invoice.id, 'friendly')}
                      className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                      title="Send Friendly Reminder"
                    >
                      <Mail className="w-3 h-3" />
                    </button>
                    <button
                      onClick={() => sendPaymentReminder(invoice.id, 'urgent')}
                      className="px-2 py-1 text-xs bg-orange-100 text-orange-700 rounded hover:bg-orange-200"
                      title="Send Urgent Reminder"
                    >
                      <AlertTriangle className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderOverdueVendors = () => {
    if (!overdueVendors) {
      return (
        <div className="p-8 text-center">
          <button
            onClick={fetchOverdueVendors}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2 mx-auto"
          >
            <RefreshCw className="w-5 h-5" />
            Load Overdue Payments
          </button>
        </div>
      );
    }

    return (
      <div className="p-4 space-y-4">
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-purple-600">Total Overdue to Vendors</p>
              <p className="text-3xl font-bold text-purple-700">₹{overdueVendors.total_overdue?.toLocaleString()}</p>
            </div>
            <CreditCard className="w-12 h-12 text-purple-400" />
          </div>
        </div>

        <div className="bg-white rounded-lg border">
          <div className="p-4 border-b flex justify-between items-center">
            <h3 className="font-semibold">Overdue Vendor Payments ({overdueVendors.total_purchases})</h3>
            <button onClick={fetchOverdueVendors} className="text-gray-500 hover:text-gray-700">
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
          <div className="divide-y max-h-[400px] overflow-y-auto">
            {overdueVendors.purchases?.slice(0, 20).map((purchase, i) => (
              <div key={i} className="p-4 flex items-center justify-between hover:bg-gray-50">
                <div>
                  <p className="font-medium">{purchase.vendor_name || 'Unknown Vendor'}</p>
                  <p className="text-sm text-gray-500">
                    Bill: {purchase.bill_number || purchase.id} • {purchase.days_overdue} days overdue
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-purple-600">₹{purchase.outstanding_amount?.toLocaleString()}</p>
                  {purchase.days_overdue > 30 && (
                    <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded">
                      Critical
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderBankAnalysis = () => {
    if (!bankAnalysis) {
      return (
        <div className="p-8 text-center space-y-4">
          <div className="max-w-md mx-auto">
            <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Upload Bank Statement</h3>
            <p className="text-gray-500 text-sm mb-4">
              Upload your bank statement in CSV format to get detailed analysis, expense categorization, and insights.
            </p>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".csv"
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadingFile}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 flex items-center gap-2 mx-auto"
            >
              {uploadingFile ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5" />
                  Upload CSV File
                </>
              )}
            </button>
          </div>
        </div>
      );
    }

    return (
      <div className="p-4 space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <ArrowUpRight className="w-4 h-4 text-green-600" />
              <p className="text-sm text-green-600">Total Income</p>
            </div>
            <p className="text-2xl font-bold text-green-700">₹{bankAnalysis.summary?.total_income?.toLocaleString()}</p>
          </div>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <ArrowDownRight className="w-4 h-4 text-red-600" />
              <p className="text-sm text-red-600">Total Expenses</p>
            </div>
            <p className="text-2xl font-bold text-red-700">₹{bankAnalysis.summary?.total_expenses?.toLocaleString()}</p>
          </div>
          <div className={`border rounded-lg p-4 ${bankAnalysis.summary?.net_savings >= 0 ? 'bg-blue-50 border-blue-200' : 'bg-orange-50 border-orange-200'}`}>
            <p className="text-sm text-gray-600">Net Savings</p>
            <p className={`text-2xl font-bold ${bankAnalysis.summary?.net_savings >= 0 ? 'text-blue-700' : 'text-orange-700'}`}>
              ₹{bankAnalysis.summary?.net_savings?.toLocaleString()}
            </p>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <p className="text-sm text-gray-600">Transactions</p>
            <p className="text-2xl font-bold text-gray-700">{bankAnalysis.summary?.transaction_count}</p>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-white rounded-lg border p-4">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <PieChart className="w-5 h-5 text-red-500" />
              Expense Breakdown
            </h3>
            <div className="space-y-2">
              {Object.entries(bankAnalysis.expense_breakdown || {}).slice(0, 8).map(([category, amount], i) => (
                <div key={i} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{category}</span>
                  <span className="font-medium">₹{amount?.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div className="bg-white rounded-lg border p-4">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-green-500" />
              Income Sources
            </h3>
            <div className="space-y-2">
              {Object.entries(bankAnalysis.income_breakdown || {}).map(([category, amount], i) => (
                <div key={i} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{category}</span>
                  <span className="font-medium text-green-600">₹{amount?.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {bankAnalysis.insights?.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-blue-600" />
              AI Insights
            </h3>
            <ul className="space-y-2">
              {bankAnalysis.insights?.map((insight, i) => (
                <li key={i} className="text-sm text-blue-800 flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 mt-0.5 text-blue-600 flex-shrink-0" />
                  {insight}
                </li>
              ))}
            </ul>
          </div>
        )}

        {bankAnalysis.recommendations?.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
              Recommendations
            </h3>
            <ul className="space-y-2">
              {bankAnalysis.recommendations?.map((rec, i) => (
                <li key={i} className="text-sm text-yellow-800">• {rec}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="text-center">
          <button
            onClick={() => {
              setBankAnalysis(null);
              fileInputRef.current?.click();
            }}
            className="text-green-600 hover:text-green-700 text-sm"
          >
            Upload Another Statement
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen" data-testid="ai-ca-agent-page">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <Bot className="w-8 h-8 text-purple-700" />
          AI CA Agent - Virtual Chartered Accountant & Auditor
        </h1>
        <p className="text-gray-600 mt-2">
          Financial analysis, GST compliance, audits, payment tracking & business intelligence
        </p>
      </div>

      {/* Period Selector & Quick Stats */}
      {quickStats && (
        <>
          <div className="flex items-center gap-2 mb-4">
            <span className="text-sm text-gray-600">Showing data for:</span>
            <select
              value={selectedPeriod}
              onChange={(e) => {
                setSelectedPeriod(e.target.value);
                fetchQuickStats(e.target.value);
              }}
              className="px-3 py-1 border rounded-lg text-sm"
            >
              <option value="today">Today</option>
              <option value="week">Last 7 Days</option>
              <option value="month">This Month</option>
              <option value="year">This Year</option>
            </select>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow p-4 text-white">
              <div className="flex items-center justify-between mb-2">
                <DollarSign className="w-6 h-6" />
                <span className="text-xs opacity-80">{quickStats.period}</span>
              </div>
              <div className="text-2xl font-bold">₹{quickStats.total_sales?.toLocaleString()}</div>
              <div className="text-xs opacity-90 mt-1">Total Sales</div>
            </div>

            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow p-4 text-white">
              <div className="flex items-center justify-between mb-2">
                <FileText className="w-6 h-6" />
                <span className="text-xs opacity-80">{quickStats.period}</span>
              </div>
              <div className="text-2xl font-bold">₹{quickStats.total_purchases?.toLocaleString()}</div>
              <div className="text-xs opacity-90 mt-1">Total Purchases</div>
            </div>

            <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg shadow p-4 text-white">
              <div className="flex items-center justify-between mb-2">
                <TrendingUp className="w-6 h-6" />
                <span className="text-xs opacity-80">{quickStats.period}</span>
              </div>
              <div className="text-2xl font-bold">₹{quickStats.total_expenses?.toLocaleString()}</div>
              <div className="text-xs opacity-90 mt-1">Total Expenses</div>
            </div>

            <div className={`bg-gradient-to-br ${quickStats.gross_profit >= 0 ? 'from-teal-500 to-teal-600' : 'from-red-500 to-red-600'} rounded-lg shadow p-4 text-white`}>
              <div className="flex items-center justify-between mb-2">
                <Sparkles className="w-6 h-6" />
                <span className="text-xs opacity-80">{quickStats.period}</span>
              </div>
              <div className="text-2xl font-bold">₹{quickStats.gross_profit?.toLocaleString()}</div>
              <div className="text-xs opacity-90 mt-1">Gross Profit</div>
            </div>

            <div className={`bg-gradient-to-br ${quickStats.net_gst >= 0 ? 'from-purple-500 to-purple-600' : 'from-indigo-500 to-indigo-600'} rounded-lg shadow p-4 text-white`}>
              <div className="flex items-center justify-between mb-2">
                <Shield className="w-6 h-6" />
                <span className="text-xs opacity-80">{quickStats.period}</span>
              </div>
              <div className="text-2xl font-bold">₹{quickStats.net_gst?.toLocaleString()}</div>
              <div className="text-xs opacity-90 mt-1">Net GST {quickStats.net_gst >= 0 ? 'Payable' : 'Credit'}</div>
            </div>
          </div>
        </>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="flex border-b overflow-x-auto">
          <button
            onClick={() => setActiveTab('chat')}
            className={`px-6 py-3 font-medium text-sm flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'chat' ? 'text-purple-600 border-b-2 border-purple-600' : 'text-gray-500 hover:text-gray-700'
            }`}
            data-testid="ai-chat-tab"
          >
            <Bot className="w-4 h-4" />
            AI Chat
          </button>
          <button
            onClick={() => { setActiveTab('audit'); if (auditHistory.length === 0) fetchAuditHistory(); }}
            className={`px-6 py-3 font-medium text-sm flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'audit' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'
            }`}
            data-testid="audit-tab"
          >
            <ClipboardCheck className="w-4 h-4" />
            Audit & Review
          </button>
          <button
            onClick={() => { setActiveTab('unpaid'); if (!unpaidInvoices) fetchUnpaidInvoices(); }}
            className={`px-6 py-3 font-medium text-sm flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'unpaid' ? 'text-orange-600 border-b-2 border-orange-600' : 'text-gray-500 hover:text-gray-700'
            }`}
            data-testid="unpaid-invoices-tab"
          >
            <Clock className="w-4 h-4" />
            Unpaid Invoices
          </button>
          <button
            onClick={() => { setActiveTab('vendors'); if (!overdueVendors) fetchOverdueVendors(); }}
            className={`px-6 py-3 font-medium text-sm flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'vendors' ? 'text-purple-600 border-b-2 border-purple-600' : 'text-gray-500 hover:text-gray-700'
            }`}
            data-testid="vendor-payments-tab"
          >
            <CreditCard className="w-4 h-4" />
            Vendor Payments
          </button>
          <button
            onClick={() => setActiveTab('bank')}
            className={`px-6 py-3 font-medium text-sm flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'bank' ? 'text-green-600 border-b-2 border-green-600' : 'text-gray-500 hover:text-gray-700'
            }`}
            data-testid="bank-analysis-tab"
          >
            <Upload className="w-4 h-4" />
            Bank Analysis
          </button>
        </div>

        {/* Tab Content */}
        <div className="min-h-[500px]">
          {activeTab === 'chat' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-4">
              <div className="lg:col-span-2">
                <div className="bg-gray-50 rounded-lg flex flex-col h-[500px]">
                  <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.map((message, index) => (
                      <div
                        key={index}
                        className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[80%] rounded-lg p-4 ${
                            message.type === 'user'
                              ? 'bg-purple-600 text-white'
                              : 'bg-white border text-gray-900'
                          }`}
                        >
                          {message.type === 'ai' && (
                            <div className="flex items-center gap-2 mb-2">
                              <Bot className="w-4 h-4 text-purple-600" />
                              <span className="font-semibold text-purple-600 text-sm">AI CA Agent</span>
                            </div>
                          )}
                          <div className="whitespace-pre-wrap text-sm leading-relaxed">
                            {message.content}
                          </div>
                          <div className={`text-xs mt-2 ${message.type === 'user' ? 'text-purple-200' : 'text-gray-500'}`}>
                            {message.timestamp.toLocaleTimeString()}
                          </div>
                        </div>
                      </div>
                    ))}

                    {isLoading && (
                      <div className="flex justify-start">
                        <div className="bg-white border rounded-lg p-4">
                          <div className="flex items-center gap-2">
                            <Loader className="w-4 h-4 text-purple-600 animate-spin" />
                            <span className="text-sm text-gray-600">AI CA is analyzing...</span>
                          </div>
                        </div>
                      </div>
                    )}

                    <div ref={messagesEndRef} />
                  </div>

                  <div className="border-t p-4 bg-white rounded-b-lg">
                    <div className="flex gap-2">
                      <textarea
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask about sales, purchases, GST, audits... Try: 'Show me sales for April 2025'"
                        className="flex-1 px-4 py-3 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 resize-none"
                        rows="2"
                        disabled={isLoading}
                        data-testid="ai-chat-input"
                      />
                      <button
                        onClick={() => sendMessage()}
                        disabled={isLoading || !inputMessage.trim()}
                        className="bg-purple-600 text-white px-6 rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                        data-testid="ai-chat-send"
                      >
                        <Send className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="bg-white rounded-lg border p-4">
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-purple-600" />
                    Suggested Queries
                  </h3>
                  <div className="space-y-2">
                    {suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => sendMessage(suggestion)}
                        className="w-full text-left px-3 py-2 bg-purple-50 hover:bg-purple-100 rounded-lg text-sm text-purple-900 transition-colors border border-purple-200"
                        data-testid={`suggestion-${index}`}
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-4 text-white">
                  <h3 className="font-semibold mb-3 flex items-center gap-2">
                    <Bot className="w-5 h-5" />
                    What I Can Do
                  </h3>
                  <ul className="space-y-2 text-sm">
                    <li>• Query any date period (April 2025, last week, FY)</li>
                    <li>• Generate P&L and GST reports</li>
                    <li>• Run daily/weekly/monthly audits</li>
                    <li>• Detect errors and mismatches</li>
                    <li>• Track unpaid invoices</li>
                    <li>• Analyze bank statements</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'audit' && renderAuditTab()}
          {activeTab === 'unpaid' && renderUnpaidInvoices()}
          {activeTab === 'vendors' && renderOverdueVendors()}
          {activeTab === 'bank' && renderBankAnalysis()}
        </div>
      </div>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        accept=".csv"
        className="hidden"
      />
    </div>
  );
};

export default AIChatCA;
