import React, { useEffect, useRef, useState } from 'react';

const API = process.env.REACT_APP_BACKEND_URL || '';

const toList = (v) =>
  Array.isArray(v)
    ? v.filter(Boolean)
    : String(v || '').split(',').map((s) => s.trim()).filter(Boolean);

export default function ProductModelPicker({ value, onChange, brand, categories }) {
  const ids = toList(value);
  const brandKey = toList(brand).join(',');
  const catKey = toList(categories).join(',');
  const [selected, setSelected] = useState({});
  const [q, setQ] = useState('');
  const [results, setResults] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const timer = useRef(null);

  // Load names for already-selected ids (edit mode)
  useEffect(() => {
    const missing = ids.filter((id) => !selected[id]);
    if (!missing.length) return;
    fetch(`${API}/api/offers/admin/product-search?ids=${encodeURIComponent(missing.join(','))}`)
      .then((r) => r.json())
      .then((d) => {
        const m = {};
        (d.products || []).forEach((p) => { m[p.id] = p; });
        setSelected((prev) => ({ ...prev, ...m }));
      })
      .catch(() => {});
    // eslint-disable-next-line
  }, [value]);

  // Debounced search
  useEffect(() => {
    if (!open) return undefined;
    clearTimeout(timer.current);
    timer.current = setTimeout(async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams({ q });
        if (brandKey) params.set('brand', brandKey);
        if (catKey) params.set('category', catKey);
        const r = await fetch(`${API}/api/offers/admin/product-search?${params.toString()}`);
        const d = await r.json();
        setResults(d.products || []);
      } catch (e) {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => clearTimeout(timer.current);
  }, [q, open, brandKey, catKey]);

  const emit = (list) => onChange(list.join(', '));
  const add = (p) => {
    setSelected((prev) => ({ ...prev, [p.id]: p }));
    if (!ids.includes(p.id)) emit([...ids, p.id]);
  };
  const remove = (id) => emit(ids.filter((x) => x !== id));
  const label = (p) => p.model_number || p.sku || p.model || p.name || '';

  return (
    <div className="relative">
      {ids.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {ids.map((id) => {
            const p = selected[id];
            return (
              <span key={id} className="inline-flex items-center gap-1 bg-blue-50 border border-blue-200 text-blue-800 text-xs rounded px-2 py-1">
                {p ? label(p) : id.slice(0, 8)}
                <button type="button" onClick={() => remove(id)} className="text-blue-600 hover:text-red-600 font-bold">×</button>
              </span>
            );
          })}
        </div>
      )}
      <input
        type="text"
        value={q}
        placeholder="Search model number / product name…"
        onChange={(e) => setQ(e.target.value)}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 200)}
        onKeyDown={(e) => { if (e.key === 'Enter') e.preventDefault(); }}
        className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
      />
      {open && (
        <div className="absolute z-50 left-0 right-0 mt-1 bg-white border border-gray-200 rounded shadow-lg max-h-56 overflow-y-auto">
          {loading && <div className="px-3 py-2 text-xs text-gray-500">Searching…</div>}
          {!loading && results.length === 0 && (
            <div className="px-3 py-2 text-xs text-gray-500">No products found</div>
          )}
          {results.map((p) => {
            const isSel = ids.includes(p.id);
            return (
              <div
                key={p.id}
                onMouseDown={(e) => { e.preventDefault(); add(p); }}
                className={`px-3 py-2 text-xs cursor-pointer hover:bg-blue-50 ${isSel ? 'bg-blue-50' : ''}`}
              >
                <div className="font-medium text-gray-800">{label(p)} {isSel && '✓'}</div>
                <div className="text-gray-500 truncate">{p.brand} · {p.category} · {p.name}</div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
