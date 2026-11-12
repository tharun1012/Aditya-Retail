import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Percent, Building2, CreditCard, Wallet, Gift, ChevronLeft, ChevronRight, ShieldCheck, Sun, Smartphone, MessageCircle } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const TYPE_META = {
  bank_offer: { label: 'Bank Offer', icon: CreditCard, tint: 'bg-blue-50 border-blue-200 text-blue-700' },
  no_cost_emi: { label: 'No Cost EMI', icon: Building2, tint: 'bg-emerald-50 border-emerald-200 text-emerald-700' },
  cashback: { label: 'Cashback', icon: Wallet, tint: 'bg-amber-50 border-amber-200 text-amber-700' },
  partner_offer: { label: 'Partner Offer', icon: Gift, tint: 'bg-purple-50 border-purple-200 text-purple-700' },
  exchange_offer: { label: 'Exchange Offer', icon: Percent, tint: 'bg-orange-50 border-orange-200 text-orange-700' },
  extended_warranty: { label: 'Extended Warranty', icon: ShieldCheck, tint: 'bg-indigo-50 border-indigo-200 text-indigo-700' },
  seasonal_offer: { label: 'Limited Time', icon: Sun, tint: 'bg-rose-50 border-rose-200 text-rose-700' },
  upi_offer: { label: 'UPI Offer', icon: Smartphone, tint: 'bg-teal-50 border-teal-200 text-teal-700' },
};

const OfferCard = ({ offer }) => {
  const meta = TYPE_META[offer.offer_type] || TYPE_META.cashback;
  const Icon = meta.icon;
  const amountLabel = offer.amount_upto
    ? offer.amount_type === 'percentage'
      ? `${offer.amount_upto}% off`
      : `Upto ₹${Number(offer.amount_upto).toLocaleString('en-IN')}`
    : 'No Cost EMI';
  return (
    <div
      data-testid={`offer-card-${offer.offer_type}`}
      className="min-w-[300px] max-w-[300px] bg-white border border-gray-200 rounded-lg p-3 flex flex-col gap-2 shadow-sm hover:shadow-md transition-shadow"
    >
      <div className={`inline-flex items-center gap-1.5 self-start rounded-full border px-2 py-0.5 text-[10px] font-semibold ${meta.tint}`}>
        <Icon className="w-3 h-3" />
        {meta.label}
      </div>
      <div className="text-sm font-semibold text-gray-900 leading-snug line-clamp-2">
        {offer.title}
      </div>
      <div className="text-lg font-bold text-emerald-700">{amountLabel}</div>
      {offer.min_purchase ? (
        <div className="text-[11px] text-gray-500">Min purchase ₹{Number(offer.min_purchase).toLocaleString('en-IN')}</div>
      ) : null}
      {offer.terms && (
        <div className="text-[11px] text-gray-700 border-t border-gray-100 pt-1.5">
          <div className="font-semibold text-gray-600 mb-0.5">Bank Terms</div>
          <div className="line-clamp-3">{offer.terms}</div>
          {offer.tenure && <div className="mt-0.5 text-gray-500">Tenure: {offer.tenure}</div>}
        </div>
      )}
      {offer.valid_bank && (
        <div className="text-[11px] text-gray-700 border-t border-gray-100 pt-1.5">
          <div className="font-semibold text-gray-600 mb-0.5">Eligible Bank Cards</div>
          <div className="line-clamp-2">{offer.valid_bank}</div>
        </div>
      )}
      {/* WhatsApp CTA — prominent on every offer (customer contacts offline store to redeem) */}
      <a
        href={offer.whatsapp_message || '#'}
        target="_blank"
        rel="noopener noreferrer"
        data-testid={`offer-whatsapp-${offer.id}`}
        className="mt-auto inline-flex items-center justify-center gap-1.5 text-xs font-semibold bg-emerald-600 text-white rounded-md px-3 py-2 hover:bg-emerald-700 shadow-sm"
      >
        <MessageCircle className="w-4 h-4" />
        Contact Us on WhatsApp to Redeem
      </a>
    </div>
  );
};

/**
 * Displays available offers for a product or cart.
 * Props:
 *   productId  – fetch offers for a specific product
 *   cartProductIds – fetch offers for a cart (array of IDs)
 *   title       – custom heading
 */
const OffersDisplay = ({ productId, cartProductIds, title = 'Available Offers' }) => {
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = React.useRef(null);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        if (productId) {
          const r = await axios.get(`${API}/api/offers/product/${productId}`);
          setOffers(r.data?.offers || []);
        } else if (cartProductIds && cartProductIds.length > 0) {
          const r = await axios.post(`${API}/api/offers/cart`, { product_ids: cartProductIds });
          setOffers(r.data?.offers || []);
        }
      } catch (e) {
        setOffers([]);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [productId, JSON.stringify(cartProductIds || [])]);

  const scroll = (dir) => {
    if (scrollRef.current) {
      scrollRef.current.scrollBy({ left: dir * 280, behavior: 'smooth' });
    }
  };

  if (loading) {
    return (
      <div data-testid="offers-loading" className="text-xs text-gray-400 py-2">
        Loading offers…
      </div>
    );
  }
  if (!offers || offers.length === 0) return null;

  return (
    <div data-testid="offers-display" className="bg-white border border-gray-200 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-full border-2 border-amber-400 flex items-center justify-center">
            <Percent className="w-3 h-3 text-amber-600" />
          </div>
          <h3 className="text-sm font-semibold text-gray-800">{title}</h3>
          <span className="text-xs text-gray-500">({offers.length})</span>
        </div>
        {offers.length > 2 && (
          <div className="flex items-center gap-1">
            <button
              onClick={() => scroll(-1)}
              data-testid="offers-scroll-left"
              className="p-1 rounded border border-gray-200 hover:bg-gray-50"
            >
              <ChevronLeft className="w-4 h-4 text-gray-600" />
            </button>
            <button
              onClick={() => scroll(1)}
              data-testid="offers-scroll-right"
              className="p-1 rounded border border-gray-200 hover:bg-gray-50"
            >
              <ChevronRight className="w-4 h-4 text-gray-600" />
            </button>
          </div>
        )}
      </div>
      <div
        ref={scrollRef}
        className="flex gap-3 overflow-x-auto pb-2 scroll-smooth"
        style={{ scrollbarWidth: 'thin' }}
      >
        {offers.map((o) => (
          <OfferCard key={o.id} offer={o} />
        ))}
      </div>
      <p className="text-[11px] text-gray-500 mt-2">
        To redeem any offer, tap <b>&quot;Contact Us on WhatsApp&quot;</b> to reach our offline store team.
      </p>
    </div>
  );
};

export default OffersDisplay;
