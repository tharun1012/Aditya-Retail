import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapPin, Truck, Loader2, CheckCircle2, XCircle, MessageCircle } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;
const STORAGE_KEY = 'ar_last_pincode';
const OFFLINE_WHATSAPP = '919844577440';

/**
 * Reusable Pincode Delivery Checker.
 * Calls /api/shipping/serviceability (Shiprocket-backed) and shows
 * estimated delivery date + shipping cost.
 *
 * Props:
 *   weight  (number, default 1) — approx product weight in kg
 *   compact (bool, default false) — smaller layout for inline use (e.g., checkout)
 *   onResult (fn, optional) — called with the result object
 */
export const PincodeChecker = ({ weight = 1, compact = false, onResult, initialPincode = '' }) => {
  const [pincode, setPincode] = useState(initialPincode);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!initialPincode) {
      const cached = localStorage.getItem(STORAGE_KEY);
      if (cached && /^\d{6}$/.test(cached)) {
        setPincode(cached);
      }
    }
  }, [initialPincode]);

  const handleCheck = async () => {
    setError('');
    setResult(null);
    if (!/^\d{6}$/.test(pincode)) {
      setError('Please enter a valid 6-digit pincode');
      return;
    }
    setLoading(true);
    try {
      const resp = await axios.post(`${API}/api/shipping/serviceability`, {
        pickup_pincode: '560058',
        delivery_pincode: pincode,
        weight: weight || 1,
        cod: 1,
      });
      const data = resp.data;
      if (data.status === 'success' && data.serviceable) {
        localStorage.setItem(STORAGE_KEY, pincode);
        setResult(data);
        if (onResult) onResult(data);
      } else {
        setError('unserviceable');
      }
    } catch (e) {
      // 503 = Shiprocket service down. Show WhatsApp fallback instead of generic error.
      if (e?.response?.status === 503) {
        setError('unserviceable');
      } else {
        setError('generic');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleCheck();
  };

  return (
    <div
      data-testid="pincode-checker"
      className={compact ? 'space-y-2' : 'border border-gray-200 rounded-lg p-4 bg-gray-50 space-y-3'}
    >
      {!compact && (
        <div className="flex items-center gap-2 text-gray-800 font-medium text-sm">
          <Truck className="w-4 h-4 text-blue-600" />
          Check Delivery Date & Charges
        </div>
      )}

      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <MapPin className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            data-testid="pincode-input"
            type="text"
            inputMode="numeric"
            maxLength={6}
            value={pincode}
            onChange={(e) => setPincode(e.target.value.replace(/\D/g, ''))}
            onKeyDown={handleKeyDown}
            placeholder="Enter 6-digit pincode"
            className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <button
          data-testid="pincode-check-btn"
          onClick={handleCheck}
          disabled={loading || pincode.length !== 6}
          className="px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-1"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Check'}
        </button>
      </div>

      {error && (
        <div data-testid="pincode-error-block" className="space-y-2">
          <div
            data-testid="pincode-error"
            className="flex items-start gap-2 text-sm text-red-700 bg-red-50 border border-red-200 rounded-md px-3 py-2"
          >
            <XCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>
              {error === 'unserviceable'
                ? 'Delivery postcode not serviceable online.'
                : 'Unable to check delivery. Please try again.'}
            </span>
          </div>
          {error === 'unserviceable' && (
            <a
              href={`https://wa.me/${OFFLINE_WHATSAPP}?text=${encodeURIComponent(
                `Hi Aditya Retail, my pincode ${pincode} is showing as not serviceable online. Can your offline team help me with delivery?`
              )}`}
              target="_blank"
              rel="noopener noreferrer"
              data-testid="pincode-whatsapp-cta"
              className="flex items-start gap-2 text-sm bg-emerald-50 border border-emerald-200 rounded-md px-3 py-2 hover:bg-emerald-100"
            >
              <MessageCircle className="w-4 h-4 mt-0.5 flex-shrink-0 text-emerald-600" />
              <span className="text-emerald-800">
                Oops, don&apos;t worry — our offline team can help with delivery to your area.{' '}
                <b className="underline">Contact us on WhatsApp</b>
              </span>
            </a>
          )}
        </div>
      )}

      {result && result.recommended && (
        <div
          data-testid="pincode-result"
          className="bg-white border border-green-200 rounded-md p-3"
        >
          <div className="flex items-start gap-2 text-sm text-green-700 font-medium">
            <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span data-testid="pincode-delivery-date">
              Delivery by <b>{result.recommended.estimated_delivery}</b>
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default PincodeChecker;
