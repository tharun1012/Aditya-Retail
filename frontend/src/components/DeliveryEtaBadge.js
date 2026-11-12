import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Truck } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;
const STORAGE_KEY = 'ar_last_pincode';

// Module-level in-memory cache so 20 product cards on a listing page
// share a single API call per (pincode + weight bucket).
const etaCache = new Map();

const getEta = (pincode, weight) => {
  const bucket = Math.max(1, Math.round(weight));
  const cacheKey = `${pincode}_${bucket}`;
  if (etaCache.has(cacheKey)) return etaCache.get(cacheKey);

  const promise = axios
    .post(`${API}/api/shipping/serviceability`, {
      pickup_pincode: '560058',
      delivery_pincode: pincode,
      weight: bucket,
      cod: 1,
    })
    .then((r) => {
      if (r.data?.status === 'success' && r.data?.serviceable && r.data?.recommended) {
        return {
          eta: r.data.recommended.estimated_delivery,
          rate: r.data.recommended.rate,
        };
      }
      return null;
    })
    .catch(() => null);

  etaCache.set(cacheKey, promise);
  return promise;
};

/**
 * Shows a compact "Ships by <date>" badge on product cards
 * when the customer already has a saved pincode. Silent otherwise.
 */
const DeliveryEtaBadge = ({ weight = 1 }) => {
  const [pincode, setPincode] = useState('');
  const [eta, setEta] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored && /^\d{6}$/.test(stored)) {
      setPincode(stored);
    }
  }, []);

  useEffect(() => {
    if (!pincode) return;
    let cancelled = false;
    setLoading(true);
    getEta(pincode, weight).then((data) => {
      if (!cancelled) {
        setEta(data);
        setLoading(false);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [pincode, weight]);

  if (!pincode) return null;
  if (loading && !eta) {
    return (
      <div
        data-testid="delivery-eta-badge-loading"
        className="text-xs text-gray-400 flex items-center gap-1 mb-2"
      >
        <Truck className="w-3 h-3" />
        Checking delivery to {pincode}…
      </div>
    );
  }
  if (!eta) return null;

  return (
    <div
      data-testid="delivery-eta-badge"
      className="text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 rounded px-2 py-1 flex items-center gap-1 mb-2"
    >
      <Truck className="w-3 h-3 flex-shrink-0" />
      <span>
        Ships by <b>{eta.eta}</b> to {pincode}
      </span>
    </div>
  );
};

export default DeliveryEtaBadge;
