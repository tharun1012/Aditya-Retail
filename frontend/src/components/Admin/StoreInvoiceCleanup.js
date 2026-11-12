import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../../config/api';
import { Trash2, AlertTriangle, Store } from 'lucide-react';

export const StoreInvoiceCleanup = ({ onDone }) => {
  const [stores, setStores] = useState([]);
  const [storeCode, setStoreCode] = useState('');
  const [docType, setDocType] = useState('invoice');
  const [matched, setMatched] = useState(null);
  const [confirmText, setConfirmText] = useState('');
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState(null);

  useEffect(() => {
    fetch(`${BACKEND_URL}/api/stores/`)
      .then(r => r.json())
      .then(d => {
        const list = Array.isArray(d.stores) ? d.stores : (Array.isArray(d) ? d : []);
        setStores(list);
      })
      .catch(() => {});
  }, []);

  const call = async (dryRun) => {
    setBusy(true);
    setMsg(null);
    try {
      const res = await fetch(`${BACKEND_URL}/api/invoices/offline/admin/delete-by-store`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: JSON.stringify({
          store_code: storeCode,
          document_type: docType,
          confirm: `DELETE-${storeCode}`,
          dry_run: dryRun,
          deleted_by: 'super_admin'
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        if (dryRun) {
          setMatched(data.matched);
        } else {
          setMsg({ type: 'success', text: `Deleted ${data.deleted} document(s) from ${storeCode}` });
          setMatched(null);
          setConfirmText('');
          if (onDone) onDone();
        }
      } else {
        setMsg({ type: 'error', text: data.detail || 'Operation failed' });
      }
    } catch (e) {
      setMsg({ type: 'error', text: 'Request failed' });
    } finally {
      setBusy(false);
    }
  };

  const typeLabel = docType === 'invoice' ? 'Sales Invoices' : docType === 'sales_order' ? 'Sales Orders' : 'Invoices + SOs';

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 mt-6" data-testid="store-invoice-cleanup">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-orange-100 rounded-lg">
          <Store className="w-5 h-5 text-orange-600" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-gray-800">Delete Store Documents</h2>
          <p className="text-sm text-gray-500">Permanently delete ALL invoices or SOs of one store only</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <select
          value={storeCode}
          onChange={(e) => { setStoreCode(e.target.value); setMatched(null); setConfirmText(''); }}
          className="border rounded-lg px-3 py-2 text-sm"
          data-testid="cleanup-store-select"
        >
          <option value="">Select Store...</option>
          {stores.map(s => (
            <option key={s.code} value={s.code}>{s.name} ({s.code})</option>
          ))}
        </select>
        <select
          value={docType}
          onChange={(e) => { setDocType(e.target.value); setMatched(null); }}
          className="border rounded-lg px-3 py-2 text-sm"
          data-testid="cleanup-doctype-select"
        >
          <option value="invoice">Sales Invoices only</option>
          <option value="sales_order">Sales Orders only</option>
          <option value="all">Invoices + Sales Orders</option>
        </select>
        <button
          onClick={() => call(true)}
          disabled={!storeCode || busy}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium disabled:opacity-50 hover:bg-blue-700"
          data-testid="cleanup-preview-btn"
        >
          Preview Count
        </button>
      </div>

      {matched !== null && (
        <div className="border border-red-200 bg-red-50 rounded-lg p-4" data-testid="cleanup-confirm-panel">
          <div className="flex items-center gap-2 text-red-800 font-medium mb-2">
            <AlertTriangle className="w-4 h-4" />
            {matched} {typeLabel} in {storeCode} will be PERMANENTLY deleted. This cannot be undone.
          </div>
          <div className="flex flex-col md:flex-row gap-3">
            <input
              value={confirmText}
              onChange={(e) => setConfirmText(e.target.value)}
              placeholder={`Type DELETE-${storeCode} to confirm`}
              className="border border-red-300 rounded-lg px-3 py-2 text-sm flex-1"
              data-testid="cleanup-confirm-input"
            />
            <button
              onClick={() => call(false)}
              disabled={busy || confirmText !== `DELETE-${storeCode}` || matched === 0}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium disabled:opacity-50 hover:bg-red-700"
              data-testid="cleanup-delete-btn"
            >
              <Trash2 className="w-4 h-4" />
              {busy ? 'Deleting...' : `Delete ${matched} document(s)`}
            </button>
          </div>
        </div>
      )}

      {msg && (
        <div className={`mt-3 text-sm font-medium ${msg.type === 'success' ? 'text-green-700' : 'text-red-700'}`} data-testid="cleanup-message">
          {msg.text}
        </div>
      )}
    </div>
  );
};

export default StoreInvoiceCleanup;
