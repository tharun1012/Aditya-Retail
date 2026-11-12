import React, { useState } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function ComboPdfImport({ onDone }) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');
  const [data, setData] = useState(null);
  const [sel, setSel] = useState({});
  const [from, setFrom] = useState('');
  const [until, setUntil] = useState('');
  const [banner, setBanner] = useState(false);

  const upload = async (e) => {
    const f = e.target.files[0]; if (!f) return;
    setBusy(true); setErr(''); setData(null);
    try {
      const fd = new FormData(); fd.append('file', f);
      const r = await fetch(`${BACKEND_URL}/api/combo-offers/pdf-import/preview`, { method: 'POST', body: fd });
      const start = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(start.detail || 'Upload failed');
      let d = null;
      for (let i = 0; i < 100; i++) {
        await new Promise(res => setTimeout(res, 3000));
        const pr = await fetch(`${BACKEND_URL}/api/combo-offers/pdf-import/preview/${start.job_id}`);
        const job = await pr.json().catch(() => ({}));
        if (!pr.ok) throw new Error(job.detail || 'Lost the job, please upload again');
        if (job.status === 'error') throw new Error(job.detail);
        if (job.status === 'done') { d = job.result; break; }
      }
      if (!d) throw new Error('Timed out waiting for the AI. Please retry.');
      setData(d); setFrom(d.valid_from || ''); setUntil(d.valid_till || '');
      const sel0 = {}; d.combos.forEach((c, i) => { sel0[i] = c.fully_matched && c.price_check_ok; });
      setSel(sel0);
    } catch (x) { setErr(x.message); } finally { setBusy(false); }
  };

  const confirm = async () => {
    setBusy(true); setErr('');
    try {
      const combos = data.combos.filter((_, i) => sel[i]);
      const r = await fetch(`${BACKEND_URL}/api/combo-offers/pdf-import/confirm`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ combos, valid_from: from || null, valid_until: until,
                               show_on_banner: banner, source_file: data.source_file })
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || 'Failed');
      alert(`Created ${d.created}, updated ${d.updated}, skipped ${d.skipped}`);
      setOpen(false); setData(null); onDone && onDone();
    } catch (x) { setErr(x.message); } finally { setBusy(false); }
  };

  const n = Object.values(sel).filter(Boolean).length;
  return (
    <>
      <button onClick={() => setOpen(true)} data-testid="import-pdf-btn"
        className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700">Import from PDF</button>
      {open && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-5xl max-h-[90vh] overflow-y-auto p-6">
            <div className="flex justify-between mb-4">
              <h3 className="text-xl font-bold">Import combos from PDF</h3>
              <button onClick={() => setOpen(false)}>✕</button>
            </div>
            <input type="file" accept="application/pdf" onChange={upload} disabled={busy} />
            {busy && <p className="mt-3 text-gray-600">Working... reading a big leaflet can take 1-2 minutes.</p>}
            {err && <p className="mt-3 text-red-600">{err}</p>}
            {data && (<>
              <div className="flex flex-wrap gap-4 my-4 items-end">
                <label className="text-sm">Valid from<input type="date" value={from} onChange={e => setFrom(e.target.value)} className="block border rounded px-2 py-1" /></label>
                <label className="text-sm">Valid until<input type="date" value={until} onChange={e => setUntil(e.target.value)} className="block border rounded px-2 py-1" /></label>
                <label className="text-sm flex gap-2"><input type="checkbox" checked={banner} onChange={e => setBanner(e.target.checked)} />Show on banner</label>
              </div>
              {data.rules?.length > 0 && <p className="text-sm bg-yellow-50 p-2 rounded mb-3">Pairing rules (not imported): {data.rules.join(' | ')}</p>}
              <table className="w-full text-sm">
                <thead><tr className="text-left border-b"><th></th><th>Combo</th><th>Products (✅ in inventory)</th><th>Leaflet price</th></tr></thead>
                <tbody>
                  {data.combos.map((c, i) => (
                    <tr key={i} className="border-b align-top">
                      <td className="py-2"><input type="checkbox" checked={!!sel[i]} disabled={!c.fully_matched}
                        onChange={e => setSel({ ...sel, [i]: e.target.checked })} /></td>
                      <td className="py-2 pr-2">{c.name}{!c.price_check_ok && <div className="text-orange-600 text-xs">item prices don't add up, verify</div>}</td>
                      <td className="py-2 pr-2">{c.items.map((it, j) => (
                        <div key={j}>{it.matched ? '✅' : '❌'} {it.model}{it.matched && ` (stock ${it.stock ?? '?'})`}</div>))}</td>
                      <td className="py-2">₹<input type="number" value={c.combo_price ?? ''} onChange={e => setData({ ...data, combos: data.combos.map((x, k) => k === i ? { ...x, combo_price: parseFloat(e.target.value) || 0 } : x) })} className="border rounded px-1 w-24 ml-1" /><div className="text-xs text-gray-400 line-through">₹{c.total_mrp?.toLocaleString('en-IN')}</div></td>
                    </tr>))}
                </tbody>
              </table>
              <button onClick={confirm} disabled={busy || !n || !until}
                className="mt-4 px-5 py-2 rounded-lg bg-green-600 text-white disabled:opacity-40">Create {n} combos</button>
            </>)}
          </div>
        </div>
      )}
    </>
  );
}
