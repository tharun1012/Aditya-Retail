import React, { useState, useEffect } from 'react';
import { X, Phone, Mail, ShoppingBag, IndianRupee, MapPin } from 'lucide-react';
import { utils } from '../../services/api';

const formatCurrency = (amount) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount || 0);

export const CustomerDetailModal = ({ customerId, onClose }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const res = await utils.fetchAPI(`/api/admin/customers/${customerId}`);
        if (!res.ok) throw new Error('Failed to load customer');
        const json = await res.json();
        setData(json);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [customerId]);

  const customer = data?.customer || {};
  const orders = data?.orders || [];
  const totalSpent = orders.reduce((s, o) => s + (o.total_amount || o.total || 0), 0);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" data-testid="customer-detail-modal">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-gray-900">Customer Details</h2>
          <button onClick={onClose} className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg" data-testid="customer-modal-close-btn">
            <X className="w-5 h-5" />
          </button>
        </div>

        {loading ? (
          <div className="p-10 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto" />
            <p className="mt-3 text-sm text-gray-500">Loading customer...</p>
          </div>
        ) : error ? (
          <div className="p-10 text-center text-sm text-red-600">{error}</div>
        ) : (
          <div className="px-6 py-4 space-y-5">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white text-xl font-bold">
                {(customer.name || 'C').charAt(0).toUpperCase()}
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">{customer.name || 'Unknown'}</h3>
                <p className="text-xs text-gray-500">{customer.id}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="bg-gray-50 rounded-lg p-3 flex items-center gap-2 text-sm">
                <Phone className="w-4 h-4 text-green-600" />
                {customer.phone ? <a href={`tel:${customer.phone}`} className="text-blue-600 font-medium">{customer.phone}</a> : <span className="text-gray-400">No phone</span>}
              </div>
              <div className="bg-gray-50 rounded-lg p-3 flex items-center gap-2 text-sm overflow-hidden">
                <Mail className="w-4 h-4 text-blue-600" />
                {customer.email ? <a href={`mailto:${customer.email}`} className="text-blue-600 font-medium truncate">{customer.email}</a> : <span className="text-gray-400">No email</span>}
              </div>
              <div className="bg-gray-50 rounded-lg p-3 flex items-center gap-2 text-sm">
                <ShoppingBag className="w-4 h-4 text-purple-600" />
                <span className="font-semibold">{orders.length}</span> orders
              </div>
              <div className="bg-gray-50 rounded-lg p-3 flex items-center gap-2 text-sm">
                <IndianRupee className="w-4 h-4 text-emerald-600" />
                <span className="font-semibold">{formatCurrency(customer.total_spent || totalSpent)}</span> spent
              </div>
            </div>

            {(customer.address || customer.city) && (
              <div className="bg-gray-50 rounded-lg p-3 flex items-start gap-2 text-sm">
                <MapPin className="w-4 h-4 text-red-500 mt-0.5" />
                <span>{[customer.address, customer.city, customer.state, customer.pincode].filter(Boolean).join(', ')}</span>
              </div>
            )}

            <div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Order History</h4>
              {orders.length === 0 ? (
                <p className="text-sm text-gray-400 italic">No orders found</p>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto" data-testid="customer-order-history">
                  {orders.map((o) => (
                    <div key={o.id || o.order_number} className="border border-gray-200 rounded-lg px-4 py-2.5 flex items-center justify-between text-sm">
                      <div>
                        <p className="font-medium text-gray-900">{o.order_number || o.id}</p>
                        <p className="text-xs text-gray-500">
                          {o.created_at ? new Date(o.created_at).toLocaleDateString('en-IN') : ''} · {(o.items || []).length} item(s)
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-gray-900">{formatCurrency(o.total_amount || o.total || 0)}</p>
                        <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full ${
                          o.status === 'delivered' ? 'bg-green-100 text-green-700' :
                          o.status === 'cancelled' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
                        }`}>
                          {o.status || 'pending'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
