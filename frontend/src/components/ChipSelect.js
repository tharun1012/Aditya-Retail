import React, { useEffect, useState } from 'react';

const API = process.env.REACT_APP_BACKEND_URL || '';

const toList = (v) =>
  Array.isArray(v) ? v.filter(Boolean) : String(v || '').split(',').map((s) => s.trim()).filter(Boolean);

// One shared load for all ChipSelect instances: unique brands and categories from the catalogue
let catalogue = null;
const loadCatalogue = () => {
  if (catalogue) return catalogue;
  const brands = new Map();
  const cats = new Map();
  const take = (list) =>
    (list || []).forEach((p) => {
      const b = (p.brand || '').trim();
      const c = (p.category || '').trim();
      if (b) brands.set(b.toLowerCase(), brands.get(b.toLowerCase()) || b);
      if (c) cats.set(c.toLowerCase(), cats.get(c.toLowerCase()) || c);
    });
  const get = (url) =>
    fetch(url).then((r) => r.json()).then((d) => (Array.isArray(d) ? d : d.products || [])).catch(() => []);
  catalogue = Promise.all([
    get(`${API}/api/offers/admin/product-search?q=`),
    get(`${API}/api/products`),
  ]).then(([a, b]) => {
    take(a);
    take(b);
    return { brand: [...brands.values()].sort(), category: [...cats.values()].sort() };
  });
  return catalogue;
};

export default function ChipSelect({ value, onChange, field, placeholder, extra = [] }) {
  const chips = toList(value);
  const [options, setOptions] = useState([]);
  const [q, setQ] = useState('');
  const [open, setOpen] = useState(false);

  useEffect(() => {
    let alive = true;
    loadCatalogue().then((c) => {
      if (!alive) return;
      const m = new Map();
      [...(c[field] || []), ...extra].forEach((o) => m.set(o.toLowerCase(), m.get(o.toLowerCase()) || o));
      setOptions([...m.values()].sort());
    });
    return () => { alive = false; };
    // eslint-disable-next-line
  }, [field]);

  const has = (o) => chips.some((c) => c.toLowerCase() === o.toLowerCase());
  const emit = (list) => onChange(list.join(', '));
  const add = (o) => {
    const t = o.trim();
    if (t && !has(t)) emit([...chips, t]);
    setQ('');
  };
  const remove = (o) => emit(chips.filter((c) => c !== o));
  const matches = options.filter((o) => !has(o) && o.toLowerCase().includes(q.toLowerCase())).slice(0, 50);

  return (
    <div className="relative">
      {chips.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {chips.map((c) => (
            <span key={c} className="inline-flex items-center gap-1 bg-blue-50 border border-blue-200 text-blue-800 text-xs rounded px-2 py-1">
              {c}
              <button type="button" onClick={() => remove(c)} className="text-blue-600 hover:text-red-600 font-bold">×</button>
            </span>
          ))}
        </div>
      )}
      <input
        type="text"
        value={q}
        placeholder={placeholder}
        onChange={(e) => setQ(e.target.value)}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 200)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') { e.preventDefault(); if (matches[0]) add(matches[0]); else if (q.trim()) add(q); }
          if (e.key === 'Backspace' && !q && chips.length) remove(chips[chips.length - 1]);
        }}
        className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
      />
      {open && (
        <div className="absolute z-50 left-0 right-0 mt-1 bg-white border border-gray-200 rounded shadow-lg max-h-56 overflow-y-auto">
          {matches.map((o) => (
            <div key={o} onMouseDown={(e) => { e.preventDefault(); add(o); }}
              className="px-3 py-2 text-xs cursor-pointer hover:bg-blue-50 text-gray-800">{o}</div>
          ))}
          {matches.length === 0 && q.trim() && !has(q.trim()) && (
            <div onMouseDown={(e) => { e.preventDefault(); add(q); }}
              className="px-3 py-2 text-xs cursor-pointer hover:bg-blue-50 text-gray-700">Add "{q.trim()}"</div>
          )}
          {matches.length === 0 && !q.trim() && (
            <div className="px-3 py-2 text-xs text-gray-500">{options.length ? 'All options selected' : 'Loading…'}</div>
          )}
        </div>
      )}
    </div>
  );
}
