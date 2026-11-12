import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Percent, ChevronRight, X, Building2 } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;
const inr = (n) => Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });

const progLabel = (p) => {
  if (p === 'BRAND_EMI') return 'Brand EMI';
  if (p === 'BANK_EMI') return 'Bank EMI';
  if (p === 'MERCHANT_BANK_OFFER') return 'Bank offer';
  return String(p || '').replace(/_/g, ' ');
};

const mergeIssuers = (issuers) => {
  const map = new Map();
  issuers.forEach((i) => {
    const k = (i.name || '').trim() + '|' + (i.type || '');
    if (!map.has(k)) map.set(k, { name: (i.name || '').trim(), type: i.type || '', tenures: [], seen: new Set() });
    const g = map.get(k);
    i.tenures.forEach((t) => {
      const key = `${t.months}|${(t.programs || []).join('+')}|${t.emi}`;
      if (g.seen.has(key)) return;
      g.seen.add(key);
      g.tenures.push(t);
    });
  });
  return [...map.values()].map((g) => ({
    name: g.name,
    type: g.type,
    tenures: g.tenures.sort((a, b) => (a.months || 0) - (b.months || 0)),
  }));
};

const OffersModal = ({ banks: allBanks, startBank, startKind, onClose }) => {
  const kinds = ['CC_BANK', 'DC_BANK'].filter((k) => allBanks.some((b) => b.type === k));
  const [kind, setKind] = useState(startKind || kinds[0] || '');
  const banks = kinds.length ? allBanks.filter((b) => b.type === kind) : allBanks;
  const [sel, setSel] = useState(startBank || banks[0]?.name);
  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = prev;
    };
  }, [onClose]);
  const bank = banks.find((b) => b.name === sel) || banks[0];
  return (
    <div
      data-testid="pine-offers-modal"
      className="fixed inset-0 z-[1000] flex items-end sm:items-center justify-center bg-black/50"
      onClick={onClose}
    >
      <div
        className="bg-white w-full sm:max-w-2xl rounded-t-2xl sm:rounded-2xl max-h-[85vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-4 py-3 border-b">
          <div>
            <div className="text-base font-bold text-gray-900">Available Offers</div>
            <div className="text-[11px] text-blue-700">Live from Pine Labs</div>
          </div>
          <button onClick={onClose} aria-label="Close" className="p-1.5 rounded-full hover:bg-gray-100">
            <X className="w-5 h-5" />
          </button>
        </div>
        {kinds.length > 1 && (
          <div className="flex gap-2 px-4 pt-3">
            {kinds.map((k) => (
              <button
                key={k}
                onClick={() => { setKind(k); setSel(null); }}
                data-testid={'offer-kind-' + k}
                className={`flex-1 text-sm font-semibold rounded-lg py-2 ${k === kind ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600'}`}
              >
                {k === 'CC_BANK' ? 'Credit Card' : 'Debit Card'}
              </button>
            ))}
          </div>
        )}
        <div className="flex gap-2 overflow-x-auto px-4 py-3 border-b">
          {banks.map((b) => (
            <button
              key={b.name}
              onClick={() => setSel(b.name)}
              className={`whitespace-nowrap text-xs font-semibold rounded-full border px-3 py-1.5 ${
                b.name === bank.name
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400'
              }`}
            >
              {b.name}
            </button>
          ))}
        </div>
        <div className="overflow-y-auto px-4 py-3">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[11px] text-gray-500 border-b">
                <th className="py-2 font-medium">Tenure</th>
                <th className="py-2 font-medium">Monthly EMI</th>
                <th className="py-2 font-medium">Interest</th>
                <th className="py-2 font-medium">Fee</th>
              </tr>
            </thead>
            <tbody>
              {bank.tenures.map((t, i) => (
                <tr key={`${t.months}-${i}`} className="border-b last:border-0 align-top">
                  <td className="py-2.5">
                    <div className="font-semibold text-gray-900">
                      {t.months > 0 ? `${t.months} months` : 'Pay now'}
                    </div>
                    <div className="text-[10px] text-gray-500">
                      {(t.programs || []).map(progLabel).join(' + ')}
                    </div>
                  </td>
                  <td className="py-2.5 font-semibold text-gray-900">₹{inr(t.emi)}</td>
                  <td className="py-2.5">
                    {t.no_cost ? (
                      <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 rounded px-1.5 py-0.5">
                        No Cost EMI
                      </span>
                    ) : (
                      <span className="text-gray-700">{t.rate}% p.a.</span>
                    )}
                  </td>
                  <td className="py-2.5 text-gray-700">{t.fee ? `₹${inr(t.fee)}` : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="text-[11px] text-gray-500 mt-3">
            Offers and EMI amounts are provided by Pine Labs. Final amount is confirmed at checkout.
          </div>
        </div>
      </div>
    </div>
  );
};

const Row = ({ icon: Icon, tint, children, onClick, testid }) => (
  <button
    onClick={onClick}
    data-testid={testid}
    className="w-full flex items-start gap-2.5 text-left py-2.5 hover:bg-gray-50 rounded-lg px-1"
  >
    <span className={`mt-0.5 shrink-0 rounded-full p-1 ${tint}`}>
      <Icon className="w-3.5 h-3.5" />
    </span>
    <span className="flex-1 text-sm text-gray-800 leading-snug">{children}</span>
    <ChevronRight className="w-4 h-4 mt-0.5 text-gray-400 shrink-0" />
  </button>
);

const PineLiveOffers = ({ productId }) => {
  const [offer, setOffer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [startBank, setStartBank] = useState(null);
  const [startKind, setStartKind] = useState(null);

  useEffect(() => {
    let alive = true;
    if (!productId) return undefined;
    setLoading(true);
    axios.get(`${API}/api/offers/pine-live/${productId}`)
      .then((r) => alive && setOffer(r.data?.offer || null))
      .catch(() => alive && setOffer(null))
      .finally(() => alive && setLoading(false));
    return () => { alive = false; };
  }, [productId]);

  if (loading) return <div className="text-xs text-gray-400 py-2">Loading offers…</div>;
  if (!offer || !offer.issuers || offer.issuers.length === 0) return null;

  const banks = mergeIssuers(offer.issuers);
  const real = [];
  banks.forEach((b) => b.tenures.forEach((t) => {
    if (t.months > 0) real.push({ ...t, bank: b.name, kind: b.type });
  }));
  const noCost = real.filter((t) => t.no_cost);
  const noCostBanks = [...new Set(noCost.map((t) => t.bank))];
  const bestNoCost = noCost.length ? noCost.reduce((a, b) => (a.emi < b.emi ? a : b)) : null;
  const best = real.length ? real.reduce((a, b) => (a.emi < b.emi ? a : b)) : null;

  const show = (bank, kind) => { setStartBank(bank || null); setStartKind(kind || null); setOpen(true); };

  return (
    <div data-testid="pine-live-offers" className="bg-white border border-gray-200 rounded-xl p-4">
      <div className="flex items-center justify-between mb-1">
        <div className="text-base font-bold text-gray-900">Available Offers</div>
        <span className="text-[10px] font-semibold text-blue-700 bg-blue-50 border border-blue-200 rounded-full px-2 py-0.5">
          Pine Labs
        </span>
      </div>
      <div className="divide-y divide-gray-100">
        {bestNoCost && (
          <Row icon={Percent} tint="bg-emerald-100 text-emerald-700" onClick={() => show(bestNoCost.bank, bestNoCost.kind)} testid="offer-row-nocost">
            <b>No Cost EMI</b> from ₹{inr(bestNoCost.emi)}/mo on {noCostBanks.slice(0, 2).join(', ')}
            {noCostBanks.length > 2 ? ` +${noCostBanks.length - 2} more` : ''}
          </Row>
        )}
        {best && (
          <Row icon={Building2} tint="bg-blue-100 text-blue-700" onClick={() => show(best.bank, best.kind)} testid="offer-row-emi">
            <b>Bank EMI</b> from ₹{inr(best.emi)}/mo · {new Set(banks.map((b) => b.name)).size} banks, up to {Math.max(...real.map((t) => t.months))} months
          </Row>
        )}
      </div>
      <button
        onClick={() => show(null)}
        data-testid="offer-view-all"
        className="mt-2 text-sm font-semibold text-blue-600 hover:text-blue-700 inline-flex items-center"
      >
        View all offers <ChevronRight className="w-4 h-4" />
      </button>
      {open && <OffersModal banks={banks} startBank={startBank} startKind={startKind} onClose={() => setOpen(false)} />}
    </div>
  );
};

export default PineLiveOffers;
