import React, { useEffect, useState } from 'react';
import { BACKEND_URL } from '../config/api';

const COLOURS = ['Orange', 'White', 'Red', 'Royal Blue', 'Yellow', 'Green', 'Grey', 'Peacock Green', 'Pink'];
const OPTIONS = [
  ['auto', 'Auto (by date)'],
  ['off', 'Off (no festive theme)'],
  ...COLOURS.map((c, i) => [`force:${i + 1}`, `Force Day ${i + 1} · ${c}`])
];

const FestiveOverrideCard = () => {
  const [mode, setMode] = useState('auto');
  const [days, setDays] = useState({});
  const [msg, setMsg] = useState('');

  const load = async () => {
    try {
      const a = await (await fetch(`${BACKEND_URL}/api/promotions/festive-override`)).json();
      if (a.mode) setMode(a.mode);
      const b = await (await fetch(`${BACKEND_URL}/api/promotions/festive-stats`)).json();
      setDays(b.days || {});
    } catch (e) { /* ignore */ }
  };
  useEffect(() => { load(); }, []);

  const save = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/promotions/festive-override`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode })
      });
      setMsg(res.ok ? 'Saved. Reload the site to see it.' : 'Save failed');
    } catch (e) { setMsg('Save failed'); }
  };

  const rows = Object.keys(days).sort().reverse();
  return (
    <div className="mb-6 rounded-xl border bg-white p-5 shadow-sm">
      <h3 className="font-bold text-gray-900 mb-3">Festive theme control</h3>
      <div className="flex flex-wrap items-center gap-3">
        <select value={mode} onChange={(e) => setMode(e.target.value)}
          className="rounded-lg border px-3 py-2 text-sm">
          {OPTIONS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
        <button onClick={save} className="rounded-lg bg-amber-700 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-800">Save</button>
        {msg && <span className="text-sm text-gray-600">{msg}</span>}
      </div>
      {rows.length > 0 && (
        <table className="mt-4 w-full text-sm">
          <thead><tr className="text-left text-gray-500">
            <th className="py-1">Day</th><th>Popup opens</th><th>Popup CTA</th><th>Deal clicks</th>
          </tr></thead>
          <tbody>
            {rows.map((d) => (
              <tr key={d} className="border-t">
                <td className="py-1">{d}</td>
                <td>{days[d].popup_open || 0}</td>
                <td>{days[d].popup_cta || 0}</td>
                <td>{days[d].deal_click || 0}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default FestiveOverrideCard;
