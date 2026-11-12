import React, { useState, useEffect } from 'react';
import { X, Scale, Loader2, Search, Trophy, CheckCircle2 } from 'lucide-react';
import { BACKEND_URL } from '../config/api';

const AdvBadge = ({ adv, side }) => {
  if (adv !== side) return null;
  return <CheckCircle2 className="w-4 h-4 text-green-600 inline ml-1 flex-shrink-0" />;
};

export const ProductCompareModal = ({ product, onClose }) => {
  const [candidates, setCandidates] = useState([]);
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/products?category=${encodeURIComponent(product.category || '')}&limit=100`);
        const data = await res.json();
        const list = (data.products || data || []).filter((p) => p.id !== product.id);
        setCandidates(list);
      } catch (e) {
        setCandidates([]);
      }
    };
    load();
  }, [product]);

  const runCompare = async (other) => {
    setSelected(other);
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${BACKEND_URL}/api/products-compare/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id_1: product.id, product_id_2: other.id }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Comparison failed');
      setComparison(data.comparison);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const filtered = candidates.filter((p) =>
    (p.name || '').toLowerCase().includes(search.toLowerCase()) ||
    (p.brand || '').toLowerCase().includes(search.toLowerCase())
  );

  const p1 = comparison?.product1;
  const p2 = comparison?.product2;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" data-testid="product-compare-modal">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[88vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between z-10">
          <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <Scale className="w-5 h-5 text-indigo-600" /> AI Product Comparison
          </h2>
          <button onClick={onClose} className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg" data-testid="compare-modal-close-btn">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          {!comparison && !loading && (
            <>
              <p className="text-sm text-gray-600 mb-3">
                Comparing <span className="font-semibold text-gray-900">{product.name}</span> with:
              </p>
              <div className="relative mb-3">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search products to compare..."
                  className="w-full pl-9 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm"
                  data-testid="compare-search-input"
                />
              </div>
              <div className="space-y-2 max-h-80 overflow-y-auto">
                {filtered.length === 0 && <p className="text-sm text-gray-400 text-center py-6">No similar products found</p>}
                {filtered.slice(0, 30).map((p) => (
                  <button
                    key={p.id}
                    onClick={() => runCompare(p)}
                    className="w-full flex items-center justify-between px-4 py-3 border border-gray-200 rounded-lg hover:border-indigo-400 hover:bg-indigo-50/40 text-left transition-colors"
                    data-testid={`compare-candidate-${p.id}`}
                  >
                    <div>
                      <p className="text-sm font-medium text-gray-900">{p.name}</p>
                      <p className="text-xs text-gray-500">{p.brand} · ₹{(p.price || 0).toLocaleString('en-IN')}</p>
                    </div>
                    <Scale className="w-4 h-4 text-indigo-500" />
                  </button>
                ))}
              </div>
            </>
          )}

          {loading && (
            <div className="py-16 text-center">
              <Loader2 className="w-10 h-10 text-indigo-600 animate-spin mx-auto" />
              <p className="mt-4 text-sm text-gray-600">Our AI expert is comparing both products...</p>
              <p className="text-xs text-gray-400 mt-1">This takes 10-20 seconds</p>
            </div>
          )}

          {error && (
            <div className="py-8 text-center">
              <p className="text-sm text-red-600">{error}</p>
              <button onClick={() => { setComparison(null); setError(null); setSelected(null); }} className="mt-3 text-sm text-indigo-600 font-medium">
                ← Choose another product
              </button>
            </div>
          )}

          {comparison && !loading && (
            <div data-testid="compare-result">
              <div className="grid grid-cols-2 gap-4 mb-4">
                {[p1, p2].map((p, i) => (
                  <div key={i} className="border border-gray-200 rounded-xl p-4 text-center">
                    <p className="text-xs font-semibold text-indigo-600 uppercase mb-1">{p?.brand}</p>
                    <p className="text-sm font-bold text-gray-900 leading-snug">{p?.name}</p>
                    <p className="text-lg font-bold text-gray-900 mt-1">₹{(p?.price || 0).toLocaleString('en-IN')}</p>
                  </div>
                ))}
              </div>

              <p className="text-sm text-gray-700 bg-indigo-50 border border-indigo-100 rounded-lg p-3 mb-4">{comparison.summary}</p>

              <div className="overflow-x-auto border border-gray-200 rounded-xl">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="text-left px-3 py-2.5 text-xs font-semibold text-gray-500 uppercase w-1/4">Feature</th>
                      <th className="text-left px-3 py-2.5 text-xs font-semibold text-gray-700">{p1?.brand}</th>
                      <th className="text-left px-3 py-2.5 text-xs font-semibold text-gray-700">{p2?.brand}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(comparison.rows || []).map((row, i) => (
                      <tr key={i} className="border-t border-gray-100">
                        <td className="px-3 py-2.5 font-medium text-gray-700">{row.feature}</td>
                        <td className={`px-3 py-2.5 text-gray-600 ${row.advantage === 'product1' ? 'bg-green-50' : ''}`}>
                          {row.product1}<AdvBadge adv={row.advantage} side="product1" />
                        </td>
                        <td className={`px-3 py-2.5 text-gray-600 ${row.advantage === 'product2' ? 'bg-green-50' : ''}`}>
                          {row.product2}<AdvBadge adv={row.advantage} side="product2" />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-4 bg-amber-50 border border-amber-200 rounded-xl p-4">
                <p className="text-xs font-bold text-amber-800 uppercase flex items-center gap-1 mb-1">
                  <Trophy className="w-3.5 h-3.5" /> Expert Verdict
                </p>
                <p className="text-sm text-gray-800">{comparison.verdict}</p>
                <div className="grid sm:grid-cols-2 gap-2 mt-3 text-xs text-gray-600">
                  <p>👤 <span className="font-semibold">{p1?.brand}:</span> {comparison.best_for_product1}</p>
                  <p>👤 <span className="font-semibold">{p2?.brand}:</span> {comparison.best_for_product2}</p>
                </div>
              </div>

              <button
                onClick={() => { setComparison(null); setSelected(null); }}
                className="mt-4 text-sm text-indigo-600 font-medium"
                data-testid="compare-another-btn"
              >
                ← Compare with a different product
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
