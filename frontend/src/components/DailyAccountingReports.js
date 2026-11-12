import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { Calendar, AlertCircle, CheckCircle, TrendingUp, FileText, Play, RefreshCw } from 'lucide-react';


const formatFieldLabel = (key) => {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
};

const formatFieldValue = (value) => {
  if (value === null || value === undefined || value === '') return '-';
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (typeof value === 'number') return value.toLocaleString('en-IN');
  return String(value);
};

// Renders a single document (invoice, voucher, GRN, purchase bill, etc.)
// as readable sections instead of raw JSON. Adapts to whichever fields
// are actually present rather than assuming one fixed shape per type.
const TransactionDetailContent = ({ doc }) => {
  if (!doc) return null;

  const partyBlock = doc.customer || doc.vendor || null;
  const partyLabel = doc.customer ? 'Customer' : 'Vendor';
  const items = Array.isArray(doc.items) ? doc.items : null;
  const payments = Array.isArray(doc.payments) ? doc.payments : null;

  // Fields already shown in a dedicated section above - excluded from
  // the generic "Other Details" grid at the bottom so nothing repeats.
  const handledKeys = new Set([
    'id', 'customer', 'vendor', 'party_name', 'store_details', 'items',
    'payments', 'linked_document'
  ]);

  const totalsFields = [
    'subtotal', 'total_tax', 'tax_total', 'tax', 'cgst', 'sgst', 'igst',
    'total_amount', 'grand_total', 'total_value', 'amount', 'balance_due',
    'total_paid_till_now', 'previously_paid', 'so_total_amount'
  ].filter((k) => doc[k] !== undefined);
  totalsFields.forEach((k) => handledKeys.add(k));

  const paymentInfoFields = [
    'payment_mode', 'payment_status', 'payment_method', 'due_date',
    'is_advance', 'approval_status'
  ].filter((k) => doc[k] !== undefined);
  paymentInfoFields.forEach((k) => handledKeys.add(k));

  const metaFields = ['created_at', 'updated_at', 'created_by', 'notes', 'description', 'remarks'];
  metaFields.forEach((k) => { if (doc[k] !== undefined) handledKeys.add(k); });

  const otherFields = Object.keys(doc).filter((k) =>
    !handledKeys.has(k) &&
    typeof doc[k] !== 'object' &&
    doc[k] !== null &&
    doc[k] !== ''
  );

  return (
    <div className="space-y-4">
      {/* Party (customer / vendor / voucher party name) */}
      {(partyBlock || doc.party_name) && (
        <div className="bg-gray-50 rounded p-3">
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">{partyLabel}</h4>
          {doc.party_name && <p className="text-sm font-medium text-gray-900">{doc.party_name}</p>}
          {partyBlock && (
            <div className="text-sm text-gray-700 space-y-0.5">
              {partyBlock.name && <p className="font-medium text-gray-900">{partyBlock.name}</p>}
              {partyBlock.phone && <p>{partyBlock.phone}</p>}
              {partyBlock.email && <p>{partyBlock.email}</p>}
              {partyBlock.billing_address && <p>{partyBlock.billing_address}</p>}
              {!partyBlock.billing_address && partyBlock.address && <p>{partyBlock.address}</p>}
              {partyBlock.gst_number && <p className="text-xs text-gray-500">GSTIN: {partyBlock.gst_number}</p>}
            </div>
          )}
        </div>
      )}

      {/* Store */}
      {doc.store_details && (
        <div className="bg-gray-50 rounded p-3">
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Store</h4>
          <p className="text-sm font-medium text-gray-900">{doc.store_details.name}</p>
          <p className="text-sm text-gray-700">{doc.store_details.address}</p>
        </div>
      )}

      {/* Items table */}
      {items && items.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Items ({items.length})</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border rounded">
              <thead className="bg-gray-50">
                <tr className="text-left">
                  <th className="p-2">Product</th>
                  <th className="p-2 text-right">Qty</th>
                  <th className="p-2 text-right">Rate</th>
                  <th className="p-2 text-right">Tax</th>
                  <th className="p-2 text-right">Total</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item, i) => (
                  <tr key={i} className="border-t">
                    <td className="p-2">{item.product_name || '-'}</td>
                    <td className="p-2 text-right">{item.received_quantity ?? item.quantity ?? '-'}</td>
                    <td className="p-2 text-right">₹{formatFieldValue(item.rate ?? item.unit_price ?? 0)}</td>
                    <td className="p-2 text-right">₹{formatFieldValue(item.tax_amount ?? 0)}</td>
                    <td className="p-2 text-right">₹{formatFieldValue(item.total ?? 0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Payments table (SO payment receipts with split payments) */}
      {payments && payments.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Payments</h4>
          <table className="w-full text-sm border rounded">
            <thead className="bg-gray-50">
              <tr className="text-left">
                <th className="p-2">Mode</th>
                <th className="p-2 text-right">Amount</th>
                <th className="p-2">Reference</th>
              </tr>
            </thead>
            <tbody>
              {payments.map((p, i) => (
                <tr key={i} className="border-t">
                  <td className="p-2 capitalize">{p.mode || '-'}</td>
                  <td className="p-2 text-right">₹{formatFieldValue(p.amount ?? 0)}</td>
                  <td className="p-2">{p.reference || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Totals */}
      {totalsFields.length > 0 && (
        <div className="bg-gray-50 rounded p-3">
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Amounts</h4>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
            {totalsFields.map((k) => (
              <div key={k} className="flex justify-between">
                <span className="text-gray-500">{formatFieldLabel(k)}</span>
                <span className="font-medium text-gray-900">₹{formatFieldValue(doc[k])}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Payment info */}
      {paymentInfoFields.length > 0 && (
        <div className="bg-gray-50 rounded p-3">
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Payment Info</h4>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
            {paymentInfoFields.map((k) => (
              <div key={k} className="flex justify-between">
                <span className="text-gray-500">{formatFieldLabel(k)}</span>
                <span className="font-medium text-gray-900 capitalize">{formatFieldValue(doc[k])}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Description / narration / remarks / notes */}
      {(doc.description || doc.notes || doc.remarks) && (
        <div className="bg-gray-50 rounded p-3">
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Notes</h4>
          <p className="text-sm text-gray-700">{doc.description || doc.notes || doc.remarks}</p>
        </div>
      )}

      {/* Anything else, generically */}
      {otherFields.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Other Details</h4>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
            {otherFields.map((k) => (
              <div key={k} className="flex justify-between">
                <span className="text-gray-500">{formatFieldLabel(k)}</span>
                <span className="font-medium text-gray-900">{formatFieldValue(doc[k])}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {doc.created_at && (
        <p className="text-xs text-gray-400 pt-2 border-t">
          Created: {new Date(doc.created_at).toLocaleString('en-IN')}
        </p>
      )}
    </div>
  );
};

const DailyAccountingReports = () => {
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [runningManual, setRunningManual] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [detailTxn, setDetailTxn] = useState(null);       // { type, id } of transaction being viewed
  const [detailDoc, setDetailDoc] = useState(null);        // fetched full document
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState('');

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/ai-accountant/daily-reports?limit=30`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setReports(data.reports);
      }
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const viewTransactionDetail = async (tx) => {
    setDetailTxn({ type: tx.type, id: tx.id });
    setDetailDoc(null);
    setDetailError('');
    setDetailLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/ai-accountant/transaction-detail?type=${encodeURIComponent(tx.type)}&id=${encodeURIComponent(tx.id)}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setDetailDoc(data.document);
      } else {
        setDetailError(data.detail || 'Failed to load details');
      }
    } catch (error) {
      setDetailError('Failed to load transaction details');
    } finally {
      setDetailLoading(false);
    }
  };

  const closeTransactionDetail = () => {
    setDetailTxn(null);
    setDetailDoc(null);
    setDetailError('');
  };

  const runManualAccounting = async () => {
    try {
      setRunningManual(true);
      showMessage('info', 'Starting daily accounting process...');
      
      const response = await fetch(`${BACKEND_URL}/api/ai-accountant/run-daily-accounting`, {
        method: 'POST'
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        showMessage('success', 'Daily accounting started! Refresh in a few moments to see results.');
        setTimeout(() => fetchReports(), 5000);  // Refresh after 5 seconds
      }
    } catch (error) {
      showMessage('error', 'Failed to start accounting process');
    } finally {
      setRunningManual(false);
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-700"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Calendar className="w-8 h-8 text-indigo-700" />
              Daily Accounting Reports
            </h1>
            <p className="text-gray-600 mt-2">
              Automated daily reports generated by AI Accountant
            </p>
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={fetchReports}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            <button
              onClick={runManualAccounting}
              disabled={runningManual}
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 flex items-center gap-2"
            >
              {runningManual ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  Running...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Run Now
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Message */}
      {message.text && (
        <div className={`mb-4 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-100 text-green-800' :
          message.type === 'error' ? 'bg-red-100 text-red-800' :
          'bg-blue-100 text-blue-800'
        }`}>
          {message.text}
        </div>
      )}

      {/* Info Card */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-start gap-3">
          <FileText className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <h3 className="font-semibold text-blue-900 mb-1">About Daily Accounting</h3>
            <p className="text-sm text-blue-800">
              The AI Daily Accountant runs automatically every night at 2:00 AM. It processes all transactions,
              creates journal entries, calculates GST liability, reconciles payments, and generates a comprehensive report.
              You can also run it manually using the "Run Now" button.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Reports List */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b">
              <h2 className="font-semibold text-gray-900">Recent Reports</h2>
              <p className="text-sm text-gray-600 mt-1">{reports.length} reports</p>
            </div>
            
            <div className="max-h-[600px] overflow-y-auto">
              {reports.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <Calendar className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>No reports yet</p>
                  <button
                    onClick={runManualAccounting}
                    className="mt-4 text-indigo-600 hover:text-indigo-800 text-sm"
                  >
                    Run your first report
                  </button>
                </div>
              ) : (
                <div className="divide-y">
                  {reports.map((report) => (
                    <div
                      key={report.id}
                      onClick={() => setSelectedReport(report)}
                      className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                        selectedReport?.id === report.id ? 'bg-indigo-50 border-l-4 border-indigo-600' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="font-semibold text-gray-900">
                          {new Date(report.report_date).toLocaleDateString('en-IN', {
                            day: 'numeric',
                            month: 'short',
                            year: 'numeric'
                          })}
                        </div>
                        {report.issues_found && report.issues_found.length > 0 ? (
                          <AlertCircle className="w-4 h-4 text-orange-600" />
                        ) : (
                          <CheckCircle className="w-4 h-4 text-green-600" />
                        )}
                      </div>
                      
                      <div className="text-sm text-gray-600 space-y-1">
                        <div>{report.transactions_processed} transactions</div>
                        <div>₹{report.gst_liability?.toLocaleString()} GST</div>
                        {report.issues_found && report.issues_found.length > 0 && (
                          <div className="text-orange-600 font-medium">
                            {report.issues_found.length} issues found
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Report Details */}
        <div className="lg:col-span-2">
          {selectedReport ? (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-600 mb-1">Transactions</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {selectedReport.transactions_processed}
                  </div>
                </div>
                
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-600 mb-1">Journal Entries</div>
                  <div className="text-2xl font-bold text-indigo-600">
                    {selectedReport.journal_entries_created}
                  </div>
                </div>
                
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-600 mb-1">GST Liability</div>
                  <div className="text-2xl font-bold text-orange-600">
                    ₹{selectedReport.gst_liability?.toLocaleString()}
                  </div>
                </div>
              </div>

              {/* AI Summary */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-indigo-600" />
                  AI Summary
                </h3>
                <p className="text-gray-700 leading-relaxed">
                  {selectedReport.summary}
                </p>
              </div>

              {/* Transactions */}
              {selectedReport.transactions && selectedReport.transactions.length > 0 && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="font-semibold text-gray-900 mb-4">
                    Transactions ({selectedReport.transactions.length})
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-left text-gray-500 border-b">
                          <th className="pb-2 pr-4">Ref</th>
                          <th className="pb-2 pr-4">Type</th>
                          <th className="pb-2 pr-4">Party</th>
                          <th className="pb-2 pr-4">Payment</th>
                          <th className="pb-2 pr-4 text-right">Amount</th>
                          <th className="pb-2 pr-4 text-right">Tax</th>
                          <th className="pb-2 text-right">Details</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedReport.transactions.map((tx, index) => (
                          <tr key={tx.id || index} className="border-b last:border-0">
                            <td className="py-2 pr-4">{tx.id || '-'}</td>
                            <td className="py-2 pr-4 capitalize">{(tx.type || '').replace('_', ' ')}</td>
                            <td className="py-2 pr-4">{tx.customer || tx.vendor || tx.category || '-'}</td>
                            <td className="py-2 pr-4 capitalize">{tx.payment_method || '-'}</td>
                            <td className="py-2 pr-4 text-right">₹{Number(tx.amount || 0).toLocaleString()}</td>
                            <td className="py-2 pr-4 text-right">₹{Number(tx.tax || 0).toLocaleString()}</td>
                            <td className="py-2 text-right">
                              <button
                                onClick={() => viewTransactionDetail(tx)}
                                className="text-indigo-600 hover:text-indigo-800 text-xs font-medium underline"
                              >
                                View
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Reconciliation Status */}
              {selectedReport.reconciliation_status && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="font-semibold text-gray-900 mb-4">Payment Reconciliation</h3>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-600 mb-1">Total Expected</div>
                      <div className="text-xl font-semibold text-gray-900">
                        ₹{selectedReport.reconciliation_status.total_expected?.toLocaleString()}
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-sm text-gray-600 mb-1">Total Received</div>
                      <div className="text-xl font-semibold text-green-600">
                        ₹{selectedReport.reconciliation_status.total_received?.toLocaleString()}
                      </div>
                    </div>
                  </div>
                  
                  {selectedReport.reconciliation_status.reconciled ? (
                    <div className="mt-4 p-3 bg-green-50 rounded-lg flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <span className="text-green-800 font-medium">Fully Reconciled</span>
                    </div>
                  ) : (
                    <div className="mt-4 p-3 bg-orange-50 rounded-lg flex items-center gap-2">
                      <AlertCircle className="w-5 h-5 text-orange-600" />
                      <span className="text-orange-800 font-medium">
                        Difference: ₹{selectedReport.reconciliation_status.difference?.toLocaleString()}
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* Issues Found */}
              {selectedReport.issues_found && selectedReport.issues_found.length > 0 && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-orange-600" />
                    Issues Found ({selectedReport.issues_found.length})
                  </h3>
                  
                  <div className="space-y-3">
                    {selectedReport.issues_found.map((issue, index) => (
                      <div
                        key={index}
                        className={`p-4 rounded-lg border-l-4 ${
                          issue.severity === 'high' ? 'bg-red-50 border-red-500' :
                          issue.severity === 'medium' ? 'bg-orange-50 border-orange-500' :
                          'bg-yellow-50 border-yellow-500'
                        }`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="font-semibold text-gray-900">{issue.type}</div>
                          <span className={`text-xs px-2 py-1 rounded ${
                            issue.severity === 'high' ? 'bg-red-100 text-red-800' :
                            issue.severity === 'medium' ? 'bg-orange-100 text-orange-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {issue.severity}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700">{issue.message}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <Calendar className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No Report Selected</h3>
              <p className="text-gray-600">Select a report from the list to view details</p>
            </div>
          )}
        </div>
      </div>
      {detailTxn && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={closeTransactionDetail}
        >
          <div
            className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[85vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between p-4 border-b sticky top-0 bg-white">
              <h3 className="font-semibold text-gray-900 capitalize">
                {(detailTxn.type || '').replace('_', ' ')} - {detailTxn.id}
              </h3>
              <button
                onClick={closeTransactionDetail}
                className="text-gray-400 hover:text-gray-600 text-xl leading-none"
              >
                &times;
              </button>
            </div>
            <div className="p-4">
              {detailLoading && (
                <p className="text-gray-500 text-sm">Loading details...</p>
              )}
              {detailError && (
                <p className="text-red-600 text-sm">{detailError}</p>
              )}
              {detailDoc && <TransactionDetailContent doc={detailDoc} />}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DailyAccountingReports;
