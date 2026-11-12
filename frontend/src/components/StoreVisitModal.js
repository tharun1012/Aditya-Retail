import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { X, MapPin, Phone, Clock, Calendar } from 'lucide-react';


const StoreVisitModal = ({ isOpen, onClose, product }) => {
  const [stores, setStores] = useState({});
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    preferred_store: 'banaswadi',
    preferred_date: '',
    preferred_time: '',
    notes: ''
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchStores();
      // Pre-fill product info
      if (product) {
        setFormData(prev => ({
          ...prev,
          notes: `Interested in: ${product.name} (${product.brand})`
        }));
      }
    }
  }, [isOpen, product]);

  const fetchStores = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/store-visit/stores`);
      const data = await response.json();
      setStores(data.stores || {});
    } catch (error) {
      console.error('Error fetching stores:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${BACKEND_URL}/api/store-visit/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          interested_products: product ? [product.name] : []
        })
      });

      const data = await response.json();

      if (data.status === 'success') {
        alert('✅ Store visit request received! Our team will contact you shortly.');
        onClose();
        setFormData({
          name: '',
          email: '',
          phone: '',
          preferred_store: 'banaswadi',
          preferred_date: '',
          preferred_time: '',
          notes: ''
        });
      } else {
        alert('Error: ' + (data.detail || 'Failed to submit request'));
      }
    } catch (error) {
      console.error('Error submitting store visit:', error);
      alert('Failed to submit request. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const selectedStore = stores[formData.preferred_store];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <MapPin className="w-6 h-6 text-amber-700" />
              Visit Our Store
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Product Info */}
          {product && (
            <div className="mb-6 p-4 bg-amber-50 rounded-lg border border-amber-200">
              <div className="flex items-center gap-4">
                <img
                  src={product.images?.[0] || '/placeholder.png'}
                  alt={product.name}
                  className="w-16 h-16 object-contain rounded"
                />
                <div>
                  <h3 className="font-semibold text-gray-900">{product.name}</h3>
                  <p className="text-sm text-gray-600">{product.brand}</p>
                  <p className="text-lg font-bold text-amber-700">
                    ₹{product.price?.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Contact Details */}
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number *
                  </label>
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                    required
                  />
                </div>
              </div>
            </div>

            {/* Store Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Store *
              </label>
              <select
                value={formData.preferred_store}
                onChange={(e) => setFormData({...formData, preferred_store: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                required
              >
                {Object.entries(stores).map(([key, store]) => (
                  <option key={key} value={key}>{store.name}</option>
                ))}
              </select>

              {/* Selected Store Info */}
              {selectedStore && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <div className="space-y-2">
                    <div className="flex items-start gap-2">
                      <MapPin className="w-4 h-4 text-gray-500 mt-1" />
                      <p className="text-sm text-gray-700">{selectedStore.address}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Phone className="w-4 h-4 text-gray-500" />
                      <p className="text-sm text-gray-700">{selectedStore.phone}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-gray-500" />
                      <p className="text-sm text-gray-700">{selectedStore.hours}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Preferred Visit Time */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Preferred Date
                </label>
                <input
                  type="date"
                  value={formData.preferred_date}
                  onChange={(e) => setFormData({...formData, preferred_date: e.target.value})}
                  min={new Date().toISOString().split('T')[0]}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Preferred Time
                </label>
                <select
                  value={formData.preferred_time}
                  onChange={(e) => setFormData({...formData, preferred_time: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                >
                  <option value="">Anytime</option>
                  <option value="10:00 AM - 12:00 PM">10:00 AM - 12:00 PM</option>
                  <option value="12:00 PM - 2:00 PM">12:00 PM - 2:00 PM</option>
                  <option value="2:00 PM - 4:00 PM">2:00 PM - 4:00 PM</option>
                  <option value="4:00 PM - 6:00 PM">4:00 PM - 6:00 PM</option>
                  <option value="6:00 PM - 8:00 PM">6:00 PM - 8:00 PM</option>
                </select>
              </div>
            </div>

            {/* Additional Notes */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Additional Notes
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({...formData, notes: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                rows="3"
                placeholder="Any specific requirements or questions..."
              ></textarea>
            </div>

            {/* Benefits */}
            <div className="mb-6 p-4 bg-green-50 rounded-lg border border-green-200">
              <h4 className="font-semibold text-green-900 mb-2">When You Visit:</h4>
              <ul className="text-sm text-green-800 space-y-1">
                <li>✓ Expert product demonstration</li>
                <li>✓ Special in-store offers</li>
                <li>✓ Instant price negotiation</li>
                <li>✓ Test products before buying</li>
                <li>✓ Free installation guidance</li>
              </ul>
            </div>

            {/* Submit */}
            <div className="flex gap-3">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-6 py-3 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-amber-700 text-white px-6 py-3 rounded-lg hover:bg-amber-800 transition-colors disabled:bg-gray-400"
              >
                {loading ? 'Submitting...' : 'Schedule Visit'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default StoreVisitModal;
