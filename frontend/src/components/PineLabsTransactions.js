import React, { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft, RefreshCw, Search, Download, Eye, CheckCircle2, XCircle,
  Clock, AlertTriangle, CreditCard, TrendingUp, IndianRupee, RotateCcw,
  ShieldCheck, ShieldAlert, ExternalLink, Filter, Wrench, Users
} from 'lucide-react';

const STATUS_STYLES = {
  captured:   { label: 'Success',   bg: 'bg-emerald-100', text: 'text-emerald-800', icon: CheckCircle2 },
  completed:  { label: 'Success',   bg: 'bg-emerald-100', text: 'text-emerald-800', icon: CheckCircle2 },
  failed:     { label: 'Failed',    bg: 'bg-rose-100',    text: 'text-rose-800',    icon: XCircle },
  cancelled:  { label: 'Cancelled', bg: 'bg-gray-200',    text: 'text-gray-800',    icon: XCircle },
  pending:    { label: 'Pending',   bg: 'bg-amber-100',   text: 'text-amber-800',   icon: Clock },
};

const StatusBadge = ({ status }) => {
  const s = STATUS_STYLES[status] || STATUS_STYLES.pending;
  const Icon = s.icon;
  return (
    <span data-testid={`tx-status-${status}`} className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${s.bg} ${s.text}`}>
      <Icon className="w-3 h-3" />
      {s.label}
    </span>
  );
};

const formatINR = (paisa) => {
  if (paisa == null) return '—';
  const inr = typeof paisa === 'number' ? paisa / 100 : parseFloat(paisa) / 100;
  return `₹${inr.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

const formatDate = (iso) => {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' });
  } catch {
    return iso;
  }
};

const PineLabsTransactions = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats] = useState(null);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [selectedTx, setSelectedTx] = useState(null);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [refundOpen, setRefundOpen] = useState(false);
  const [refundAmount, setRefundAmount] = useState('');
  const [refundReason, setRefundReason] = useState('Customer requested refund');
  const [refundBusy, setRefundBusy] = useState(false);

  const fetchTransactions = useCallback(async () => {
    setRefreshing(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (fromDate) params.append('from_date', fromDate);
      if (toDate) params.append('to_date', toDate);
      params.append('page_size', '100');

      const res = await fetch(`${BACKEND_URL}/api/pine-labs/admin/transactions?${params}`);
      const data = await res.json();
      if (data.success) setTransactions(data.transactions || []);
    } catch (e) {
      console.error('Failed to fetch transactions', e);
    } finally {
      setRefreshing(false);
      setLoading(false);
    }
  }, [search, statusFilter, fromDate, toDate]);

  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/pine-labs/admin/stats?days=30`);
      const data = await res.json();
      if (data.success) setStats(data);
    } catch (e) {
      console.error('Failed to fetch stats', e);
    }
  }, []);

  useEffect(() => {
    fetchTransactions();
    fetchStats();
  }, [fetchTransactions, fetchStats]);

  const openDetail = async (tx) => {
    setSelectedTx(tx);
    setDetail(null);
    setDetailLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/pine-labs/admin/transaction/${encodeURIComponent(tx.order_id)}`);
      const data = await res.json();
      if (data.success) setDetail(data);
    } catch (e) {
      console.error('Detail fetch failed', e);
    } finally {
      setDetailLoading(false);
    }
  };

  const refreshLiveStatus = async (orderId) => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/pine-labs/status/${encodeURIComponent(orderId)}`);
      const data = await res.json();
      if (data.success) {
        alert(`Live status from Pine Labs:\n\nStatus: ${data.plural_status}\nPayment: ${data.payment_status}\nAmount: ${formatINR(data.amount)}`);
        fetchTransactions();
      } else {
        alert(`Status check failed: ${data.message || 'Unknown error'}`);
      }
    } catch (e) {
      alert(`Error: ${e.message}`);
    }
  };

  const reconcileTransaction = async (orderId) => {
    if (!window.confirm(`Reconcile Pine Labs order ${orderId}?\n\nThis will fetch the live status from Pine Labs and update the linked order in your system.`)) return;
    try {
      const res = await fetch(`${BACKEND_URL}/api/pine-labs/admin/reconcile/${encodeURIComponent(orderId)}`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        alert(
          `Reconciled!\n\n` +
          `Plural Status: ${data.plural_status}\n` +
          `Payment Status: ${data.payment_status}\n` +
          `Internal Order: ${data.internal_order_number || '(none)'}\n` +
          `Order Updated: ${data.order_updated ? '✓ Yes' : '✗ No (no matching internal order)'}`
        );
        fetchTransactions();
        fetchStats();
      } else {
        alert(`Reconcile failed: ${data.message}`);
      }
    } catch (e) {
      alert(`Error: ${e.message}`);
    }
  };

  const reconcileByPineId = async () => {
    const orderId = window.prompt('Enter the Pine Labs Order ID to reconcile (e.g., v1-260506xxxxx-aa-xxxxxxx):');
    if (orderId && orderId.trim()) {
      await reconcileTransaction(orderId.trim());
    }
  };

  const runBackfill = async () => {
    if (!window.confirm(
      'Link orphan customer orders?\n\n' +
      'This will scan all orders missing a customer_id and link them to user accounts by matching the email used at checkout.\n\n' +
      'Safe to run multiple times.'
    )) return;
    try {
      const res = await fetch(`${BACKEND_URL}/api/customer/admin/backfill-customer-ids`, { method: 'POST' });
      const data = await res.json();
      if (data.status === 'success') {
        alert(
          `Back-fill complete!\n\n` +
          `Orders scanned: ${data.total_orphans_scanned}\n` +
          `Linked to customers: ${data.linked}\n` +
          `Unmatched (no user account): ${data.unmatched_count}` +
          (data.unmatched_sample?.length ? `\n\nExamples of unmatched:\n${data.unmatched_sample.slice(0, 5).map(u => `• ${u.order_number || '?'}: ${u.reason}`).join('\n')}` : '')
        );
      } else {
        alert(`Back-fill failed: ${JSON.stringify(data)}`);
      }
    } catch (e) {
      alert(`Error: ${e.message}`);
    }
  };

  const submitRefund = async () => {
    if (!selectedTx || !refundAmount) return;
    const paisa = Math.round(parseFloat(refundAmount) * 100);
    if (!paisa || paisa <= 0) {
      alert('Enter a valid refund amount');
      return;
    }
    if (!window.confirm(`Refund ₹${refundAmount} for order ${selectedTx.order_id}? This action cannot be undone.`)) return;

    setRefundBusy(true);
    try {
      const params = new URLSearchParams({
        order_id: selectedTx.order_id,
        refund_amount: paisa,
        reason: refundReason,
      });
      const res = await fetch(`${BACKEND_URL}/api/pine-labs/refund?${params}`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        alert(`Refund initiated. Refund ID: ${data.refund_id}`);
        setRefundOpen(false);
        setRefundAmount('');
        fetchTransactions();
      } else {
        alert(`Refund failed: ${data.message}`);
      }
    } catch (e) {
      alert(`Error: ${e.message}`);
    } finally {
      setRefundBusy(false);
    }
  };

  const exportCSV = () => {
    const headers = ['Order ID', 'Merchant Ref', 'Amount', 'Status', 'Plural Status', 'Event', 'Verified', 'Invoice', 'Customer', 'Date'];
    const rows = transactions.map(tx => [
      tx.order_id,
      tx.merchant_order_reference || '',
      tx.amount ? (tx.amount / 100).toFixed(2) : '',
      tx.payment_status || '',
      tx.status || '',
      tx.event_type || '',
      tx.signature_verified ? 'Yes' : 'No',
      tx.linked_invoice?.invoice_number || '',
      tx.linked_invoice?.customer_name || '',
      tx.created_at || '',
    ]);
    const csv = [headers, ...rows].map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `pine-labs-transactions-${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-slate-50" data-testid="pine-labs-transactions-page">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/admin')}
              className="p-2 rounded-lg hover:bg-slate-100 transition"
              data-testid="back-btn"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                <CreditCard className="w-5 h-5 text-indigo-600" />
                Pine Labs Transactions
              </h1>
              <p className="text-sm text-slate-500">Live payment gateway dashboard & reconciliation</p>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={runBackfill}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-emerald-100 hover:bg-emerald-200 text-emerald-800 rounded-lg transition"
              data-testid="backfill-btn"
              title="Link orphan orders (missing customer_id) to customer accounts by email"
            >
              <Users className="w-4 h-4" />
              Link Orphan Orders
            </button>
            <button
              onClick={reconcileByPineId}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-amber-100 hover:bg-amber-200 text-amber-800 rounded-lg transition"
              data-testid="reconcile-by-id-btn"
              title="Manually reconcile a Pine Labs order ID that's missing from this dashboard"
            >
              <Wrench className="w-4 h-4" />
              Reconcile Order
            </button>
            <button
              onClick={() => { fetchTransactions(); fetchStats(); }}
              disabled={refreshing}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-slate-100 hover:bg-slate-200 rounded-lg transition"
              data-testid="refresh-btn"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button
              onClick={exportCSV}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition"
              data-testid="export-csv-btn"
            >
              <Download className="w-4 h-4" />
              Export CSV
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6" data-testid="stats-cards">
            <div className="bg-white rounded-xl p-4 border border-slate-200">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-slate-500">Total Transactions (30d)</span>
                <TrendingUp className="w-4 h-4 text-indigo-500" />
              </div>
              <p className="text-2xl font-bold text-slate-900">{stats.total_transactions}</p>
            </div>
            <div className="bg-white rounded-xl p-4 border border-slate-200">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-slate-500">Amount Processed</span>
                <IndianRupee className="w-4 h-4 text-emerald-500" />
              </div>
              <p className="text-2xl font-bold text-emerald-700">
                ₹{stats.total_amount_inr.toLocaleString('en-IN')}
              </p>
              <p className="text-xs text-slate-400 mt-1">{stats.captured_count} captured</p>
            </div>
            <div className="bg-white rounded-xl p-4 border border-slate-200">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-slate-500">Success Rate</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              </div>
              <p className="text-2xl font-bold text-slate-900">{stats.success_rate}%</p>
            </div>
            <div className="bg-white rounded-xl p-4 border border-slate-200">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-slate-500">Failed / Pending</span>
                <AlertTriangle className="w-4 h-4 text-amber-500" />
              </div>
              <p className="text-2xl font-bold text-slate-900">
                {(stats.by_status?.failed || 0) + (stats.by_status?.pending || 0)}
              </p>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 mb-4">
          <div className="flex items-center gap-2 mb-3 text-sm font-medium text-slate-700">
            <Filter className="w-4 h-4" /> Filters
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Order ID / Merchant Ref"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                data-testid="search-input"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"
              data-testid="status-filter"
            >
              <option value="all">All Status</option>
              <option value="success">Success</option>
              <option value="failed">Failed</option>
              <option value="pending">Pending</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"
              data-testid="from-date"
            />
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"
              data-testid="to-date"
            />
          </div>
        </div>

        {/* Transactions Table */}
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm" data-testid="transactions-table">
              <thead className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                <tr>
                  <th className="px-4 py-3 text-left">Order / Merchant Ref</th>
                  <th className="px-4 py-3 text-left">Customer / Invoice</th>
                  <th className="px-4 py-3 text-right">Amount</th>
                  <th className="px-4 py-3 text-center">Status</th>
                  <th className="px-4 py-3 text-center">Signature</th>
                  <th className="px-4 py-3 text-left">Date</th>
                  <th className="px-4 py-3 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr><td colSpan={7} className="px-4 py-10 text-center text-slate-400">Loading transactions...</td></tr>
                ) : transactions.length === 0 ? (
                  <tr><td colSpan={7} className="px-4 py-10 text-center text-slate-400">
                    No transactions found. Complete a test payment to see records here.
                  </td></tr>
                ) : (
                  transactions.map((tx) => (
                    <tr key={tx.order_id} className="hover:bg-slate-50" data-testid={`tx-row-${tx.order_id}`}>
                      <td className="px-4 py-3">
                        <div className="font-medium text-slate-900 font-mono text-xs">{tx.order_id}</div>
                        {tx.merchant_order_reference && (
                          <div className="text-xs text-slate-500 font-mono">{tx.merchant_order_reference}</div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {tx.linked_invoice ? (
                          <div>
                            <div className="font-medium text-slate-900">{tx.linked_invoice.customer_name || '—'}</div>
                            <div className="text-xs text-slate-500">{tx.linked_invoice.invoice_number}</div>
                          </div>
                        ) : (
                          <span className="text-xs text-slate-400">No linked invoice</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right font-semibold text-slate-900">
                        {formatINR(tx.amount)}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <StatusBadge status={tx.payment_status} />
                        {tx.status && (
                          <div className="text-xs text-slate-400 mt-1 font-mono">{tx.status}</div>
                        )}
                      </td>
                      <td className="px-4 py-3 text-center">
                        {tx.signature_verified ? (
                          <ShieldCheck className="w-5 h-5 text-emerald-500 inline" data-testid="sig-verified" />
                        ) : (
                          <ShieldAlert className="w-5 h-5 text-amber-500 inline" data-testid="sig-unverified" />
                        )}
                      </td>
                      <td className="px-4 py-3 text-xs text-slate-500 whitespace-nowrap">
                        {formatDate(tx.created_at)}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex items-center justify-center gap-1">
                          <button
                            onClick={() => openDetail(tx)}
                            className="p-1.5 rounded hover:bg-indigo-50 text-indigo-600"
                            title="View Details"
                            data-testid={`view-btn-${tx.order_id}`}
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => refreshLiveStatus(tx.order_id)}
                            className="p-1.5 rounded hover:bg-blue-50 text-blue-600"
                            title="Refresh Live Status"
                            data-testid={`refresh-tx-${tx.order_id}`}
                          >
                            <RefreshCw className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => reconcileTransaction(tx.order_id)}
                            className="p-1.5 rounded hover:bg-amber-50 text-amber-600"
                            title="Reconcile — update linked order from live status"
                            data-testid={`reconcile-tx-${tx.order_id}`}
                          >
                            <Wrench className="w-4 h-4" />
                          </button>
                          {tx.payment_status === 'captured' && (
                            <button
                              onClick={() => {
                                setSelectedTx(tx);
                                setRefundAmount(tx.amount ? (tx.amount / 100).toFixed(2) : '');
                                setRefundOpen(true);
                              }}
                              className="p-1.5 rounded hover:bg-rose-50 text-rose-600"
                              title="Initiate Refund"
                              data-testid={`refund-btn-${tx.order_id}`}
                            >
                              <RotateCcw className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Detail Modal */}
      {selectedTx && !refundOpen && (
        <div className="fixed inset-0 bg-black/50 z-30 flex items-center justify-center p-4" onClick={() => setSelectedTx(null)}>
          <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col" onClick={(e) => e.stopPropagation()}>
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-slate-900">Transaction Details</h2>
                <p className="text-xs text-slate-500 font-mono">{selectedTx.order_id}</p>
              </div>
              <button onClick={() => setSelectedTx(null)} className="p-2 hover:bg-slate-100 rounded-lg" data-testid="close-detail-btn">
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {detailLoading ? (
                <p className="text-center text-slate-400 py-10">Loading details...</p>
              ) : detail ? (
                <>
                  {/* Summary */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div>
                      <p className="text-xs text-slate-500">Payment Status</p>
                      <StatusBadge status={selectedTx.payment_status} />
                    </div>
                    <div>
                      <p className="text-xs text-slate-500">Plural Status</p>
                      <p className="text-sm font-mono">{selectedTx.status || '—'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500">Amount</p>
                      <p className="text-sm font-semibold">{formatINR(selectedTx.amount)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500">Event Type</p>
                      <p className="text-sm">{selectedTx.event_type || '—'}</p>
                    </div>
                  </div>

                  {/* Linked Invoice */}
                  {detail.linked_invoice && (
                    <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
                      <h3 className="text-sm font-semibold text-emerald-900 mb-2 flex items-center gap-1">
                        <ExternalLink className="w-4 h-4" /> Linked Invoice
                      </h3>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div><span className="text-slate-600">Invoice:</span> <span className="font-mono">{detail.linked_invoice.invoice_number}</span></div>
                        <div><span className="text-slate-600">Store:</span> {detail.linked_invoice.store_code}</div>
                        <div><span className="text-slate-600">Customer:</span> {detail.linked_invoice.customer_name}</div>
                        <div><span className="text-slate-600">Phone:</span> {detail.linked_invoice.customer_phone}</div>
                        <div><span className="text-slate-600">Email:</span> {detail.linked_invoice.customer_email}</div>
                        <div><span className="text-slate-600">Total:</span> ₹{detail.linked_invoice.total_amount}</div>
                      </div>
                    </div>
                  )}

                  {/* Callbacks */}
                  {detail.callbacks?.length > 0 && (
                    <div>
                      <h3 className="text-sm font-semibold text-slate-900 mb-2">Browser Callbacks ({detail.callbacks.length})</h3>
                      <div className="space-y-2">
                        {detail.callbacks.map((cb, idx) => (
                          <div key={idx} className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs">
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-mono">{cb.status}</span>
                              <span className="text-slate-500">{formatDate(cb.created_at)}</span>
                            </div>
                            {cb.error_message && <p className="text-rose-600">{cb.error_message}</p>}
                            <p className="text-slate-500">Signature: {cb.signature_verified ? '✓ Verified' : '✗ Unverified'}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Webhooks + Raw Payload */}
                  {detail.webhooks?.length > 0 && (
                    <div>
                      <h3 className="text-sm font-semibold text-slate-900 mb-2">Server Webhooks ({detail.webhooks.length})</h3>
                      {detail.webhooks.map((wh, idx) => (
                        <details key={idx} className="bg-slate-50 border border-slate-200 rounded-lg p-3 mb-2">
                          <summary className="cursor-pointer text-sm font-medium flex items-center justify-between">
                            <span>{wh.event_type || 'webhook'} — {wh.status}</span>
                            <span className="text-xs text-slate-500">{formatDate(wh.created_at)}</span>
                          </summary>
                          <pre className="mt-3 bg-slate-900 text-emerald-400 text-xs p-3 rounded overflow-x-auto">
                            {JSON.stringify(wh.payload, null, 2)}
                          </pre>
                        </details>
                      ))}
                    </div>
                  )}

                  {!detail.callbacks?.length && !detail.webhooks?.length && (
                    <p className="text-center text-slate-400 py-6">No callback or webhook events recorded yet.</p>
                  )}
                </>
              ) : null}
            </div>
          </div>
        </div>
      )}

      {/* Refund Modal */}
      {refundOpen && selectedTx && (
        <div className="fixed inset-0 bg-black/50 z-40 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6" data-testid="refund-modal">
            <h2 className="text-lg font-bold text-slate-900 mb-1">Initiate Refund</h2>
            <p className="text-xs text-slate-500 font-mono mb-4">{selectedTx.order_id}</p>

            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Amount (INR)</label>
                <input
                  type="number"
                  step="0.01"
                  value={refundAmount}
                  onChange={(e) => setRefundAmount(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                  data-testid="refund-amount-input"
                />
                <p className="text-xs text-slate-500 mt-1">Original: {formatINR(selectedTx.amount)}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Reason</label>
                <textarea
                  value={refundReason}
                  onChange={(e) => setRefundReason(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  rows={2}
                  data-testid="refund-reason-input"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-5">
              <button
                onClick={() => { setRefundOpen(false); setSelectedTx(null); }}
                disabled={refundBusy}
                className="px-4 py-2 text-sm bg-slate-100 hover:bg-slate-200 rounded-lg"
                data-testid="refund-cancel-btn"
              >Cancel</button>
              <button
                onClick={submitRefund}
                disabled={refundBusy}
                className="px-4 py-2 text-sm bg-rose-600 hover:bg-rose-700 disabled:opacity-60 text-white rounded-lg"
                data-testid="refund-submit-btn"
              >
                {refundBusy ? 'Processing…' : 'Confirm Refund'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PineLabsTransactions;
