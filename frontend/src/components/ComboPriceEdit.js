import React, { useState } from 'react';
import * as AF from './authFetch';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const doFetch = AF.authFetch || AF.default || fetch;

export default function ComboPriceEdit({ offer, onDone }) {
  const [open, setOpen] = useState(false);
  const [orig, setOrig] = useState(Math.round(offer.original_price ?? offer.total_price ?? 0));
  const [price, setPrice] = useState(Math.round(offer.final_price ?? offer.combo_price ?? 0));
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');

  const save = async () => {
    setBusy(true); setErr('');
    try {
      const r = await doFetch(`${BACKEND_URL}/api/combo-offers/${offer.id}/pricing`, {
        method: 'PUT', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ final_price: Number(price), original_price: Number(orig) })
      });
      const d = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(d.detail || 'Could not save');
      setOpen(false); onDone && onDone();
    } catch (x) { setErr(x.message); } finally { setBusy(false); }
  };

  const saving = Math.max(0, Number(orig) - Number(price));
  return (
    <>
      <button onClick={() => { setOrig(Math.round(offer.original_price ?? offer.total_price ?? 0)); setPrice(Math.round(offer.final_price ?? offer.combo_price ?? 0)); setErr(''); setOpen(true); }} data-testid={`edit-price-${offer.id}`}
        className="flex-1 bg-blue-50 text-blue-600 py-2 rounded-lg hover:bg-blue-100">Edit Price</button>
      {open && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-md p-6">
            <h3 className="text-lg font-bold mb-1">Edit combo price</h3>
            <p className="text-sm text-gray-500 mb-4">{offer.name}</p>
            <label className="block text-sm mb-3">Original price (MRP total, ₹)
              <input type="number" value={orig} onChange={e => setOrig(e.target.value)} className="block w-full border rounded px-2 py-1 mt-1" />
            </label>
            <label className="block text-sm mb-3">Combo price (₹)
              <input type="number" value={price} onChange={e => setPrice(e.target.value)} className="block w-full border rounded px-2 py-1 mt-1" />
            </label>
            <p className="text-sm text-green-700 mb-3">Customer saves ₹{saving.toLocaleString('en-IN')}</p>
            {err && <p className="text-sm text-red-600 mb-3">{err}</p>}
            <div className="flex gap-2 justify-end">
              <button onClick={() => setOpen(false)} className="px-4 py-2 rounded-lg bg-gray-100">Cancel</button>
              <button onClick={save} disabled={busy} className="px-4 py-2 rounded-lg bg-green-600 text-white disabled:opacity-40">{busy ? 'Saving...' : 'Save'}</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
