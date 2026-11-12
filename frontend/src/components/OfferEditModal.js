import ProductModelPicker from './ProductModelPicker';
import ChipSelect from './ChipSelect';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Save, Loader2 } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const OFFER_TYPES = [
  { value: 'cashback', label: 'Cashback' },
  { value: 'bank_offer', label: 'Bank Offer' },
  { value: 'no_cost_emi', label: 'No Cost EMI' },
  { value: 'upi_offer', label: 'UPI Cashback / Offer' },
  { value: 'exchange_offer', label: 'Exchange Offer' },
  { value: 'extended_warranty', label: 'Extended Warranty' },
  { value: 'seasonal_offer', label: 'Limited Time / Seasonal Offer' },
  { value: 'partner_offer', label: 'Partner Offer' },
];

const AMOUNT_TYPES = [
  { value: 'flat', label: 'Flat ₹ amount' },
  { value: 'percentage', label: 'Percentage %' },
  { value: 'upto', label: 'Upto ₹' },
];

const REDEEM_LOCATIONS = [
  { value: 'offline_store', label: 'Offline Store (WhatsApp)' },
  { value: 'online', label: 'Online (Applied at checkout)' },
];

/**
 * Modal for creating or editing a cashback/bank/EMI/warranty offer.
 * Props:
 *   open (bool) — whether the modal is open
 *   offer (obj|null) — existing offer to edit, or null to create new
 *   onClose (fn) — called after save/close
 */
const OfferEditModal = ({ open, offer, onClose }) => {
  const [form, setForm] = useState(defaultForm());
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState('');

  useEffect(() => {
    if (offer) {
      setForm({
        offer_type: offer.offer_type || 'cashback',
        title: offer.title || '',
        description: offer.description || '',
        amount_upto: offer.amount_upto ?? '',
        amount_type: offer.amount_type || 'flat',
        min_purchase: offer.min_purchase ?? '',
        valid_bank: offer.valid_bank || '',
        valid_till: offer.valid_till || '',
        brand: offer.brand || '',
        categories: (offer.categories || []).join(', '),
        product_ids: (offer.product_ids || []).join(', '),
        terms: offer.terms || '',
        tenure: offer.tenure || '',
        redeem_location: offer.redeem_location || 'offline_store',
        is_active: offer.is_active !== false,
      });
    } else {
      setForm(defaultForm());
    }
    setErr('');
  }, [offer, open]);

  const update = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const handleSubmit = async () => {
    setErr('');
    if (!form.title.trim()) {
      setErr('Title is required');
      return;
    }
    const payload = {
      offer_type: form.offer_type,
      title: form.title.trim(),
      description: form.description.trim(),
      amount_upto: form.amount_upto === '' ? null : Number(form.amount_upto),
      amount_type: form.amount_type,
      min_purchase: form.min_purchase === '' ? null : Number(form.min_purchase),
      valid_bank: form.valid_bank.trim() || null,
      valid_till: form.valid_till || null,
      brand: form.brand.trim() || null,
      categories: form.categories.split(',').map((c) => c.trim()).filter(Boolean),
      product_ids: form.product_ids.split(',').map((c) => c.trim()).filter(Boolean),
      terms: form.terms.trim() || null,
      tenure: form.tenure.trim() || null,
      redeem_location: form.redeem_location,
      is_active: !!form.is_active,
    };

    setSaving(true);
    try {
      if (offer && offer.id) {
        await axios.put(`${API}/api/offers/admin/${offer.id}`, payload);
      } else {
        await axios.post(`${API}/api/offers/admin/create`, payload);
      }
      onClose(true);
    } catch (e) {
      setErr(e.response?.data?.detail || 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  if (!open) return null;

  return (
    <div
      data-testid="offer-edit-modal"
      className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
    >
      <div className="bg-white rounded-xl shadow-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-5 py-3 flex items-center justify-between z-10">
          <h3 className="text-lg font-semibold text-gray-900">
            {offer ? 'Edit Offer' : 'Add New Offer'}
          </h3>
          <button onClick={() => onClose(false)} className="p-1 rounded hover:bg-gray-100">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-4">
          <Field label="Offer Type" required>
            <select
              data-testid="offer-type-select"
              value={form.offer_type}
              onChange={(e) => update('offer_type', e.target.value)}
              className="input"
            >
              {OFFER_TYPES.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </Field>

          <Field label="Redemption Location">
            <select
              value={form.redeem_location}
              onChange={(e) => update('redeem_location', e.target.value)}
              className="input"
            >
              {REDEEM_LOCATIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </Field>

          <Field label="Title" required className="md:col-span-2">
            <input
              data-testid="offer-title-input"
              type="text"
              value={form.title}
              onChange={(e) => update('title', e.target.value)}
              placeholder="e.g. HDFC 10% Cashback on Bosch Refrigerators"
              className="input"
            />
          </Field>

          <Field label="Amount Type">
            <select value={form.amount_type} onChange={(e) => update('amount_type', e.target.value)} className="input">
              {AMOUNT_TYPES.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </Field>

          <Field label="Amount (₹ or %)">
            <input
              type="number"
              value={form.amount_upto}
              onChange={(e) => update('amount_upto', e.target.value)}
              placeholder="e.g. 5000"
              className="input"
            />
          </Field>

          <Field label="Min Purchase ₹">
            <input
              type="number"
              value={form.min_purchase}
              onChange={(e) => update('min_purchase', e.target.value)}
              placeholder="e.g. 40000"
              className="input"
            />
          </Field>

          <Field label="Valid Till">
            <input
              type="date"
              value={form.valid_till}
              onChange={(e) => update('valid_till', e.target.value)}
              className="input"
            />
          </Field>

          <Field label="Brand" hint="One brand OR comma-separated (e.g. Bosch, Electrolux, Siemens). Leave blank for all brands.">
            <ChipSelect field="brand" value={form.brand} onChange={(v) => update('brand', v)} placeholder="Search brand… (blank = all brands)" extra={['Bosch','Siemens','Electrolux','Haier','Hindware']} />
          </Field>

          <Field label="Categories">
            <ChipSelect field="category" value={form.categories} onChange={(v) => update('categories', v)} placeholder="Search category…" extra={['Washing Machine','Refrigerator','Dishwasher','Gas Hob','Induction Hob','Chimney','Oven','Microwave']} />
          </Field>

          <Field label="Eligible Bank Cards" className="md:col-span-2" hint="Enter bank names comma-separated. Leave blank for brand-wide offers.">
            <input
              data-testid="offer-banks-input"
              type="text"
              value={form.valid_bank}
              onChange={(e) => update('valid_bank', e.target.value)}
              placeholder="HDFC, ICICI, Axis, SBI, Kotak, AMEX, BOB"
              className="input"
            />
          </Field>

          <Field label="Bank Terms / EMI Details" className="md:col-span-2">
            <textarea
              value={form.terms}
              onChange={(e) => update('terms', e.target.value)}
              placeholder="e.g. No Cost EMI on 3/6 months, 2.5% interest on 9/12 months"
              rows={2}
              className="input"
            />
          </Field>

          <Field label="Tenure (months)">
            <input
              type="text"
              value={form.tenure}
              onChange={(e) => update('tenure', e.target.value)}
              placeholder="3, 6, 9, 12"
              className="input"
            />
          </Field>

          <Field label="Specific Models (optional)">
            <ProductModelPicker
              value={form.product_ids}
              onChange={(v) => update('product_ids', v)}
              brand={form.brand}
              categories={form.categories}
            />
            <p className="text-[10px] text-gray-500 mt-1">Leave empty to apply to all products of the brand/category. Select models to restrict this offer to only those models.</p>
          </Field>

          <Field label="Description" className="md:col-span-2">
            <textarea
              value={form.description}
              onChange={(e) => update('description', e.target.value)}
              placeholder="Additional details shown on the offer card"
              rows={2}
              className="input"
            />
          </Field>

          <div className="md:col-span-2">
            <label className="inline-flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={!!form.is_active}
                onChange={(e) => update('is_active', e.target.checked)}
              />
              Active (visible on live site)
            </label>
          </div>
        </div>

        {err && (
          <div className="px-5 pb-3 text-sm text-red-700 bg-red-50 border-t border-red-200">{err}</div>
        )}

        <div className="sticky bottom-0 bg-white border-t border-gray-200 px-5 py-3 flex justify-end gap-2">
          <button
            onClick={() => onClose(false)}
            className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            data-testid="offer-save-btn"
            onClick={handleSubmit}
            disabled={saving}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-md"
          >
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            {saving ? 'Saving…' : offer ? 'Update Offer' : 'Create Offer'}
          </button>
        </div>
      </div>

      <style>{`
        .input {
          width: 100%;
          font-size: 0.875rem;
          border: 1px solid #d1d5db;
          border-radius: 0.375rem;
          padding: 0.5rem 0.75rem;
          background: white;
        }
        .input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59,130,246,0.2); }
      `}</style>
    </div>
  );
};

const Field = ({ label, required, hint, className, children }) => (
  <div className={className}>
    <label className="block text-xs font-medium text-gray-700 mb-1">
      {label} {required && <span className="text-red-500">*</span>}
    </label>
    {children}
    {hint && <p className="text-[10px] text-gray-500 mt-0.5">{hint}</p>}
  </div>
);

function defaultForm() {
  return {
    offer_type: 'cashback',
    title: '',
    description: '',
    amount_upto: '',
    amount_type: 'flat',
    min_purchase: '',
    valid_bank: '',
    valid_till: '',
    brand: '',
    categories: '',
    product_ids: '',
    terms: '',
    tenure: '',
    redeem_location: 'offline_store',
    is_active: true,
  };
}

export default OfferEditModal;
