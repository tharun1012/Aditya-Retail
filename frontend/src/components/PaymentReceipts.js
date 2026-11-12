import React, { useState, useEffect } from 'react';
import { 
  Receipt, Plus, Search, X, Printer, Share2, Check, 
  CreditCard, Banknote, Smartphone, Building2, ChevronDown,
  History, DollarSign, AlertCircle, RefreshCw, FileText
} from 'lucide-react';
import { BACKEND_URL } from '../config/api';

const PAYMENT_MODES = [
  { id: 'cash', label: 'Cash', icon: Banknote, color: 'green' },
  { id: 'upi', label: 'UPI', icon: Smartphone, color: 'purple' },
  { id: 'card', label: 'Card', icon: CreditCard, color: 'blue' },
  { id: 'neft', label: 'NEFT/RTGS', icon: Building2, color: 'orange' },
  { id: 'cheque', label: 'Cheque', icon: FileText, color: 'gray' }
];

// Payment Receipt Modal - For recording payments against SO
const PaymentReceiptModal = ({ 
  isOpen, 
  onClose, 
  salesOrder, 
  onSuccess,
  storeUser 
}) => {
  const [payments, setPayments] = useState([{ mode: 'cash', amount: '', reference: '', bank_name: '' }]);
  const [remarks, setRemarks] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  
  const soTotal = salesOrder?.total_amount || 0;
  const previouslyPaid = salesOrder?.total_paid || 0;
  const balanceDue = soTotal - previouslyPaid;
  
  const totalEntered = payments.reduce((sum, p) => sum + (parseFloat(p.amount) || 0), 0);
  const remainingBalance = balanceDue - totalEntered;
  
  const addPaymentRow = () => {
    setPayments([...payments, { mode: 'upi', amount: '', reference: '', bank_name: '' }]);
  };
  
  const removePaymentRow = (index) => {
    if (payments.length > 1) {
      setPayments(payments.filter((_, i) => i !== index));
    }
  };
  
  const updatePayment = (index, field, value) => {
    const updated = [...payments];
    updated[index][field] = value;
    setPayments(updated);
  };
  
  const handleSubmit = async () => {
    // Validate
    const validPayments = payments.filter(p => parseFloat(p.amount) > 0);
    if (validPayments.length === 0) {
      setError('Please enter at least one payment amount');
      return;
    }
    
    if (totalEntered > balanceDue) {
      setError(`Payment amount (₹${totalEntered.toLocaleString()}) exceeds balance due (₹${balanceDue.toLocaleString()})`);
      return;
    }
    
    setSubmitting(true);
    setError('');
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/vouchers/so-payment/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          so_id: salesOrder.id,
          payments: validPayments.map(p => ({
            mode: p.mode,
            amount: parseFloat(p.amount),
            reference: p.reference || null,
            bank_name: p.bank_name || null
          })),
          remarks: remarks,
          collected_by: storeUser?.name || 'Store Staff'
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        onSuccess(data);
        onClose();
      } else {
        setError(data.detail || 'Failed to create payment receipt');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };
  
  if (!isOpen || !salesOrder) return null;
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-4 border-b bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-t-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Receipt className="w-6 h-6" />
              <div>
                <h2 className="text-lg font-bold">Record Payment</h2>
                <p className="text-green-100 text-sm">SO: {salesOrder.invoice_number}</p>
              </div>
            </div>
            <button onClick={onClose} className="p-1 hover:bg-white/20 rounded-full">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        {/* Summary Card */}
        <div className="p-4 bg-gray-50 border-b">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-xs text-gray-500 uppercase">SO Total</p>
              <p className="text-lg font-bold text-gray-800">₹{soTotal.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase">Previously Paid</p>
              <p className="text-lg font-bold text-green-600">₹{previouslyPaid.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase">Balance Due</p>
              <p className="text-lg font-bold text-red-600">₹{balanceDue.toLocaleString()}</p>
            </div>
          </div>
          
          {/* Customer Info */}
          <div className="mt-3 pt-3 border-t border-gray-200 text-sm">
            <p className="font-medium">{salesOrder.customer?.name}</p>
            <p className="text-gray-500">{salesOrder.customer?.phone}</p>
          </div>
        </div>
        
        {/* Payment Entries */}
        <div className="p-4 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-700">Payment Details</h3>
            <button
              onClick={addPaymentRow}
              className="text-sm text-green-600 hover:text-green-700 flex items-center gap-1"
            >
              <Plus className="w-4 h-4" />
              Add Split Payment
            </button>
          </div>
          
          {payments.map((payment, index) => (
            <div key={index} className="p-3 border rounded-lg bg-white shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-600">Payment #{index + 1}</span>
                {payments.length > 1 && (
                  <button
                    onClick={() => removePaymentRow(index)}
                    className="text-red-500 hover:text-red-600 p-1"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
              
              {/* Payment Mode */}
              <div className="flex flex-wrap gap-2">
                {PAYMENT_MODES.map((mode) => (
                  <button
                    key={mode.id}
                    onClick={() => updatePayment(index, 'mode', mode.id)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                      payment.mode === mode.id
                        ? `bg-${mode.color}-100 text-${mode.color}-700 ring-2 ring-${mode.color}-500`
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                    style={{
                      backgroundColor: payment.mode === mode.id ? `var(--${mode.color}-100, #dcfce7)` : undefined,
                      color: payment.mode === mode.id ? `var(--${mode.color}-700, #15803d)` : undefined
                    }}
                  >
                    <mode.icon className="w-4 h-4" />
                    {mode.label}
                  </button>
                ))}
              </div>
              
              {/* Amount */}
              <div className="flex gap-3">
                <div className="flex-1">
                  <label className="block text-xs text-gray-500 mb-1">Amount *</label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">₹</span>
                    <input
                      type="number"
                      value={payment.amount}
                      onChange={(e) => updatePayment(index, 'amount', e.target.value)}
                      placeholder="Enter amount"
                      className="w-full pl-8 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                      max={balanceDue}
                    />
                  </div>
                </div>
                
                {/* Reference (for UPI/Card/NEFT/Cheque) */}
                {payment.mode !== 'cash' && (
                  <div className="flex-1">
                    <label className="block text-xs text-gray-500 mb-1">
                      {payment.mode === 'cheque' ? 'Cheque #' : 'Reference/Transaction ID'}
                    </label>
                    <input
                      type="text"
                      value={payment.reference}
                      onChange={(e) => updatePayment(index, 'reference', e.target.value)}
                      placeholder={payment.mode === 'cheque' ? 'Cheque number' : 'Transaction ID'}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    />
                  </div>
                )}
              </div>
              
              {/* Bank name for cheque/NEFT */}
              {(payment.mode === 'cheque' || payment.mode === 'neft') && (
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Bank Name</label>
                  <input
                    type="text"
                    value={payment.bank_name}
                    onChange={(e) => updatePayment(index, 'bank_name', e.target.value)}
                    placeholder="Enter bank name"
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  />
                </div>
              )}
            </div>
          ))}
          
          {/* Running Total */}
          <div className="p-3 bg-green-50 rounded-lg border border-green-200">
            <div className="flex justify-between items-center">
              <span className="text-sm text-green-700">This Payment Total:</span>
              <span className="text-xl font-bold text-green-700">₹{totalEntered.toLocaleString()}</span>
            </div>
            {remainingBalance > 0 && (
              <p className="text-xs text-green-600 mt-1">
                Remaining balance after this payment: ₹{remainingBalance.toLocaleString()}
              </p>
            )}
            {remainingBalance === 0 && totalEntered > 0 && (
              <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                <Check className="w-3 h-3" /> Full payment - SO will be marked as Paid
              </p>
            )}
          </div>
          
          {/* Remarks */}
          <div>
            <label className="block text-xs text-gray-500 mb-1">Remarks (Optional)</label>
            <textarea
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              placeholder="e.g., Advance payment, Part payment 2, etc."
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              rows={2}
            />
          </div>
          
          {/* Error */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm flex items-start gap-2">
              <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              {error}
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="p-4 border-t bg-gray-50 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={submitting || totalEntered === 0}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2 disabled:opacity-50"
          >
            {submitting ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Receipt className="w-4 h-4" />
                Create Receipt
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};


// Payment History Modal - View all payments for an SO
const PaymentHistoryModal = ({ isOpen, onClose, soId, soNumber }) => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [selectedReceipt, setSelectedReceipt] = useState(null);
  
  useEffect(() => {
    if (isOpen && soId) {
      fetchHistory();
    }
  }, [isOpen, soId]);
  
  const fetchHistory = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/vouchers/so-payment/by-so/${soId}`);
      const result = await response.json();
      if (result.status === 'success') {
        setData(result);
      }
    } catch (err) {
      console.error('Error fetching payment history:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const handlePrint = (receipt) => {
    // Open print preview for receipt
    const printContent = generatePrintableReceipt(receipt);
    const printWindow = window.open('', '_blank');
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
  };
  
  const handleShare = async (receipt) => {
    const text = `Payment Receipt: ${receipt.receipt_number}\nAmount: ₹${receipt.total_amount.toLocaleString()}\nSO: ${receipt.so_number}\nDate: ${new Date(receipt.created_at).toLocaleDateString()}`;
    
    if (navigator.share) {
      try {
        await navigator.share({ title: 'Payment Receipt', text });
      } catch (err) {
        navigator.clipboard.writeText(text);
        alert('Receipt details copied to clipboard!');
      }
    } else {
      navigator.clipboard.writeText(text);
      alert('Receipt details copied to clipboard!');
    }
  };
  
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 border-b bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <History className="w-6 h-6" />
              <div>
                <h2 className="text-lg font-bold">Payment History</h2>
                <p className="text-blue-100 text-sm">SO: {soNumber}</p>
              </div>
            </div>
            <button onClick={onClose} className="p-1 hover:bg-white/20 rounded-full">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        {loading ? (
          <div className="flex-1 flex items-center justify-center p-8">
            <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
          </div>
        ) : data ? (
          <>
            {/* Summary */}
            <div className="p-4 bg-gray-50 border-b">
              <div className="grid grid-cols-4 gap-3 text-center">
                <div className="p-2 bg-white rounded-lg shadow-sm">
                  <p className="text-xs text-gray-500">Total</p>
                  <p className="font-bold text-gray-800">₹{data.so_total?.toLocaleString()}</p>
                </div>
                <div className="p-2 bg-green-50 rounded-lg">
                  <p className="text-xs text-green-600">Paid</p>
                  <p className="font-bold text-green-700">₹{data.total_paid?.toLocaleString()}</p>
                </div>
                <div className={`p-2 rounded-lg ${data.balance_due > 0 ? 'bg-red-50' : 'bg-green-50'}`}>
                  <p className={`text-xs ${data.balance_due > 0 ? 'text-red-600' : 'text-green-600'}`}>Balance</p>
                  <p className={`font-bold ${data.balance_due > 0 ? 'text-red-700' : 'text-green-700'}`}>
                    ₹{data.balance_due?.toLocaleString()}
                  </p>
                </div>
                <div className="p-2 bg-blue-50 rounded-lg">
                  <p className="text-xs text-blue-600">Payments</p>
                  <p className="font-bold text-blue-700">{data.receipt_count}</p>
                </div>
              </div>
            </div>
            
            {/* Receipts List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {data.receipts?.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Receipt className="w-12 h-12 mx-auto mb-2 opacity-30" />
                  <p>No payments recorded yet</p>
                </div>
              ) : (
                data.receipts?.map((receipt, idx) => (
                  <div key={receipt.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                            Payment #{receipt.receipt_index || idx + 1}
                          </span>
                          <span className="font-mono text-sm text-gray-500">{receipt.receipt_number}</span>
                        </div>
                        <p className="text-xl font-bold text-green-600 mt-1">
                          ₹{receipt.total_amount?.toLocaleString()}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(receipt.created_at).toLocaleString()}
                        </p>
                      </div>
                      
                      <div className="flex gap-2">
                        <button
                          onClick={() => handlePrint(receipt)}
                          className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
                          title="Print Receipt"
                        >
                          <Printer className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleShare(receipt)}
                          className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
                          title="Share Receipt"
                        >
                          <Share2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    
                    {/* Payment modes breakdown */}
                    <div className="mt-3 flex flex-wrap gap-2">
                      {receipt.payments?.map((p, pIdx) => {
                        const modeInfo = PAYMENT_MODES.find(m => m.id === p.mode) || PAYMENT_MODES[0];
                        return (
                          <span
                            key={pIdx}
                            className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 rounded text-sm"
                          >
                            <modeInfo.icon className="w-3 h-3" />
                            {modeInfo.label}: ₹{p.amount?.toLocaleString()}
                            {p.reference && <span className="text-gray-400 text-xs">({p.reference})</span>}
                          </span>
                        );
                      })}
                    </div>
                    
                    {receipt.remarks && (
                      <p className="mt-2 text-sm text-gray-500 italic">"{receipt.remarks}"</p>
                    )}
                    
                    <p className="mt-2 text-xs text-gray-400">
                      Collected by: {receipt.collected_by}
                    </p>
                  </div>
                ))
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center p-8 text-red-500">
            Failed to load payment history
          </div>
        )}
        
        {/* Footer */}
        <div className="p-4 border-t bg-gray-50">
          <button
            onClick={onClose}
            className="w-full py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};


// Helper function to generate printable receipt HTML
const generatePrintableReceipt = (receipt) => {
  const paymentRows = receipt.payments?.map(p => {
    const modeLabel = PAYMENT_MODES.find(m => m.id === p.mode)?.label || p.mode;
    return `
      <tr>
        <td style="padding: 8px; border-bottom: 1px solid #eee;">${modeLabel}</td>
        <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">₹${p.amount?.toLocaleString()}</td>
        <td style="padding: 8px; border-bottom: 1px solid #eee;">${p.reference || '-'}</td>
      </tr>
    `;
  }).join('');
  
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Payment Receipt - ${receipt.receipt_number}</title>
      <style>
        body { font-family: Arial, sans-serif; padding: 20px; max-width: 400px; margin: 0 auto; }
        .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 15px; }
        .header h1 { margin: 0; font-size: 18px; }
        .header p { margin: 5px 0; color: #666; font-size: 12px; }
        .receipt-no { font-size: 14px; font-weight: bold; margin: 10px 0; }
        .info-row { display: flex; justify-content: space-between; padding: 5px 0; font-size: 13px; }
        .info-row .label { color: #666; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 13px; }
        th { background: #f5f5f5; padding: 8px; text-align: left; }
        .total { font-size: 18px; font-weight: bold; text-align: right; padding: 10px 0; border-top: 2px solid #333; }
        .footer { text-align: center; font-size: 11px; color: #666; margin-top: 20px; padding-top: 15px; border-top: 1px dashed #ccc; }
        @media print { body { padding: 0; } }
      </style>
    </head>
    <body>
      <div class="header">
        <h1>${receipt.store_name || 'Aditya Retail'}</h1>
        <p>Payment Receipt</p>
      </div>
      
      <div class="receipt-no">Receipt #: ${receipt.receipt_number}</div>
      
      <div class="info-row">
        <span class="label">Date:</span>
        <span>${new Date(receipt.created_at).toLocaleString()}</span>
      </div>
      <div class="info-row">
        <span class="label">SO Number:</span>
        <span>${receipt.so_number}</span>
      </div>
      <div class="info-row">
        <span class="label">Customer:</span>
        <span>${receipt.customer?.name || '-'}</span>
      </div>
      <div class="info-row">
        <span class="label">Phone:</span>
        <span>${receipt.customer?.phone || '-'}</span>
      </div>
      
      <table>
        <thead>
          <tr>
            <th>Mode</th>
            <th style="text-align: right;">Amount</th>
            <th>Reference</th>
          </tr>
        </thead>
        <tbody>
          ${paymentRows}
        </tbody>
      </table>
      
      <div class="total">Total: ₹${receipt.total_amount?.toLocaleString()}</div>
      
      <div class="info-row">
        <span class="label">SO Total:</span>
        <span>₹${receipt.so_total_amount?.toLocaleString()}</span>
      </div>
      <div class="info-row">
        <span class="label">Paid Till Now:</span>
        <span>₹${receipt.total_paid_till_now?.toLocaleString()}</span>
      </div>
      <div class="info-row">
        <span class="label">Balance Due:</span>
        <span style="color: ${receipt.balance_due > 0 ? 'red' : 'green'};">₹${receipt.balance_due?.toLocaleString()}</span>
      </div>
      
      ${receipt.remarks ? `<p style="font-style: italic; color: #666; font-size: 12px;">Remarks: ${receipt.remarks}</p>` : ''}
      
      <div class="footer">
        <p>Received by: ${receipt.collected_by}</p>
        <p>Thank you for your payment!</p>
      </div>
    </body>
    </html>
  `;
};


// Pending Payments List Component - Shows ALL Sales Orders with payment tracking
const PendingPaymentsList = ({ storeCode, userRole }) => {
  const [loading, setLoading] = useState(true);
  const [allSOs, setAllSOs] = useState([]);
  const [selectedSO, setSelectedSO] = useState(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [filter, setFilter] = useState('all'); // 'all', 'pending', 'paid'
  
  // Determine if user is admin-level (can see all stores)
  const isAdminLevel = ['admin', 'super_admin', 'accountant'].includes(userRole);
  
  useEffect(() => {
    fetchAllSOs();
  }, [storeCode]);
  
  const fetchAllSOs = async () => {
    setLoading(true);
    try {
      // RBAC: Store users MUST filter by their store_code
      // Admin users can see all (no store_code filter) or filter by specific store
      let url = `${BACKEND_URL}/api/invoices/offline/?document_type=sales_order&limit=100`;
      
      // Always pass store_code for store-level users to enforce RBAC
      if (storeCode) {
        url += `&store_code=${storeCode}`;
      }
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.status === 'success') {
        // Process SOs to calculate balance
        const processedSOs = (data.invoices || []).map(so => {
          const totalPaid = so.total_paid || 0;
          const balanceDue = (so.total_amount || 0) - totalPaid;
          return {
            ...so,
            total_paid: totalPaid,
            balance_due: balanceDue,
            payment_status: balanceDue <= 0 ? 'paid' : (totalPaid > 0 ? 'partially_paid' : 'pending')
          };
        });
        setAllSOs(processedSOs);
      }
    } catch (err) {
      console.error('Error fetching SOs:', err);
    } finally {
      setLoading(false);
    }
  };
  
  // Filter SOs based on selected filter
  const filteredSOs = allSOs.filter(so => {
    if (filter === 'pending') return so.balance_due > 0;
    if (filter === 'paid') return so.balance_due <= 0;
    return true; // 'all'
  });
  
  // Summary stats
  const stats = {
    total: allSOs.length,
    pending: allSOs.filter(s => s.balance_due > 0).length,
    paid: allSOs.filter(s => s.balance_due <= 0).length,
    totalAmount: allSOs.reduce((sum, s) => sum + (s.total_amount || 0), 0),
    totalCollected: allSOs.reduce((sum, s) => sum + (s.total_paid || 0), 0),
    totalDue: allSOs.reduce((sum, s) => sum + (s.balance_due || 0), 0)
  };
  
  const handleRecordPayment = (so) => {
    setSelectedSO(so);
    setShowPaymentModal(true);
  };
  
  const handleViewHistory = (so) => {
    setSelectedSO(so);
    setShowHistoryModal(true);
  };
  
  const handlePaymentSuccess = (result) => {
    alert(`Payment Receipt ${result.receipt_number} created!\n\nPaid: ₹${result.this_payment?.toLocaleString()}\nBalance Due: ₹${result.balance_due?.toLocaleString()}`);
    fetchAllSOs(); // Refresh list
  };
  
  return (
    <div className="bg-white rounded-xl shadow-sm">
      {/* Header with Stats */}
      <div className="p-4 border-b bg-gradient-to-r from-green-50 to-emerald-50">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-green-600" />
            <h2 className="text-lg font-semibold text-gray-800">Payment Tracker</h2>
          </div>
          <button
            onClick={fetchAllSOs}
            className="p-2 text-gray-500 hover:bg-white rounded-lg"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="bg-white p-2 rounded-lg shadow-sm">
            <p className="text-xs text-gray-500">Total Orders</p>
            <p className="text-lg font-bold text-gray-800">₹{stats.totalAmount?.toLocaleString()}</p>
            <p className="text-xs text-gray-400">{stats.total} SOs</p>
          </div>
          <div className="bg-green-100 p-2 rounded-lg">
            <p className="text-xs text-green-600">Collected</p>
            <p className="text-lg font-bold text-green-700">₹{stats.totalCollected?.toLocaleString()}</p>
            <p className="text-xs text-green-500">{stats.paid} paid</p>
          </div>
          <div className="bg-orange-100 p-2 rounded-lg">
            <p className="text-xs text-orange-600">Pending</p>
            <p className="text-lg font-bold text-orange-700">₹{stats.totalDue?.toLocaleString()}</p>
            <p className="text-xs text-orange-500">{stats.pending} due</p>
          </div>
        </div>
      </div>
      
      {/* Filter Tabs */}
      <div className="flex border-b">
        {[
          { id: 'all', label: 'All Orders', count: stats.total },
          { id: 'pending', label: 'Pending', count: stats.pending },
          { id: 'paid', label: 'Fully Paid', count: stats.paid }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setFilter(tab.id)}
            className={`flex-1 py-2 text-sm font-medium transition-colors ${
              filter === tab.id 
                ? 'text-green-600 border-b-2 border-green-500 bg-green-50' 
                : 'text-gray-500 hover:bg-gray-50'
            }`}
          >
            {tab.label} ({tab.count})
          </button>
        ))}
      </div>
      
      {loading ? (
        <div className="p-8 text-center">
          <RefreshCw className="w-8 h-8 mx-auto text-gray-400 animate-spin" />
        </div>
      ) : filteredSOs.length === 0 ? (
        <div className="p-8 text-center text-gray-500">
          <Check className="w-12 h-12 mx-auto mb-2 text-green-400" />
          <p>{filter === 'pending' ? 'No pending payments!' : filter === 'paid' ? 'No fully paid orders yet' : 'No orders found'}</p>
        </div>
      ) : (
        <div className="divide-y max-h-96 overflow-y-auto">
          {filteredSOs.map((so) => (
            <div key={so.id} className="p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-blue-600">{so.invoice_number}</span>
                    {so.balance_due <= 0 ? (
                      <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full flex items-center gap-1">
                        <Check className="w-3 h-3" /> Paid
                      </span>
                    ) : so.total_paid > 0 ? (
                      <span className="px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                        Partial
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full">
                        Pending
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{so.customer?.name} • {so.customer?.phone}</p>
                  
                  <div className="flex items-center gap-4 mt-2 text-sm">
                    <span className="text-gray-500">Total: ₹{so.total_amount?.toLocaleString()}</span>
                    <span className="text-green-600">Paid: ₹{(so.total_paid || 0)?.toLocaleString()}</span>
                    <span className={`font-medium ${so.balance_due > 0 ? 'text-red-600' : 'text-green-600'}`}>
                      Due: ₹{(so.balance_due || 0)?.toLocaleString()}
                    </span>
                  </div>
                </div>
                
                <div className="flex flex-col gap-2">
                  {so.balance_due > 0 && (
                    <button
                      onClick={() => handleRecordPayment(so)}
                      className="px-3 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 flex items-center gap-1"
                    >
                      <Plus className="w-4 h-4" />
                      Record Payment
                    </button>
                  )}
                  <button
                    onClick={() => handleViewHistory(so)}
                    className="px-3 py-1.5 bg-blue-50 text-blue-600 text-sm rounded-lg hover:bg-blue-100 flex items-center gap-1"
                  >
                    <History className="w-4 h-4" />
                    View History
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* Payment Modal */}
      <PaymentReceiptModal
        isOpen={showPaymentModal}
        onClose={() => {
          setShowPaymentModal(false);
          setSelectedSO(null);
        }}
        salesOrder={selectedSO}
        onSuccess={handlePaymentSuccess}
      />
      
      {/* History Modal */}
      <PaymentHistoryModal
        isOpen={showHistoryModal}
        onClose={() => {
          setShowHistoryModal(false);
          setSelectedSO(null);
        }}
        soId={selectedSO?.id}
        soNumber={selectedSO?.invoice_number}
      />
    </div>
  );
};


export { 
  PaymentReceiptModal, 
  PaymentHistoryModal, 
  PendingPaymentsList,
  PAYMENT_MODES 
};

// Default export for backward compatibility
export default PendingPaymentsList;
