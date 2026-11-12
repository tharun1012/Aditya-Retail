import React, { useState } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { Package, Search, Mail, CheckCircle, Clock, Truck, Home, AlertCircle } from 'lucide-react';

const OrderTrackingPage = () => {
  const navigate = useNavigate();
  const [orderNumber, setOrderNumber] = useState('');
  const [email, setEmail] = useState('');
  const [orderData, setOrderData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  
  const statusIcons = {
    'placed': Clock,
    'pending': Clock,
    'confirmed': CheckCircle,
    'processing': Package,
    'shipped': Truck,
    'delivered': Home,
    'cancelled': AlertCircle
  };

  const statusColors = {
    'placed': 'text-yellow-600 bg-yellow-50 border-yellow-200',
    'pending': 'text-yellow-600 bg-yellow-50 border-yellow-200',
    'confirmed': 'text-blue-600 bg-blue-50 border-blue-200',
    'processing': 'text-purple-600 bg-purple-50 border-purple-200',
    'shipped': 'text-indigo-600 bg-indigo-50 border-indigo-200',
    'delivered': 'text-green-600 bg-green-50 border-green-200',
    'cancelled': 'text-red-600 bg-red-50 border-red-200'
  };

  const getStatusProgress = (status) => {
    const progressMap = {
      'placed': 20,
      'pending': 20,
      'confirmed': 40,
      'processing': 60,
      'shipped': 80,
      'delivered': 100,
      'cancelled': 0
    };
    return progressMap[status] || 0;
  };

  const handleTrackOrder = async (e) => {
    e.preventDefault();
    setError('');
    setOrderData(null);
    setLoading(true);

    try {
      // Search for order by order number and email
      const response = await fetch(`${BACKEND_URL}/api/orders/track?order_number=${orderNumber}&email=${email}`);
      
      if (!response.ok) {
        throw new Error('Order not found. Please check your order number and email.');
      }

      const data = await response.json();
      setOrderData(data.order);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <button
            onClick={() => navigate('/')}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            ← Back to Store
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Track Your Order</h1>
          <div className="w-24"></div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Search Card */}
        {!orderData && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                <Package className="w-8 h-8 text-blue-600" />
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Track Your Order</h2>
              <p className="text-gray-600">Enter your order details to see the current status</p>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <p className="text-red-600">{error}</p>
              </div>
            )}

            <form onSubmit={handleTrackOrder} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Order Number
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={orderNumber}
                    onChange={(e) => setOrderNumber(e.target.value)}
                    placeholder="AD202511030032"
                    className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                  <Package className="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your.email@example.com"
                    className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                  <Mail className="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-5 h-5" />
                    <span>Track Order</span>
                  </>
                )}
              </button>
            </form>
          </div>
        )}

        {/* Order Details */}
        {orderData && (
          <div className="space-y-6">
            {/* Order Header */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Order {orderData.order_number}</h2>
                  <p className="text-gray-600">Placed on {new Date(orderData.created_at).toLocaleDateString()}</p>
                </div>
                <button
                  onClick={() => {
                    setOrderData(null);
                    setOrderNumber('');
                    setEmail('');
                  }}
                  className="text-blue-600 hover:text-blue-700 font-medium"
                >
                  Track Another Order
                </button>
              </div>

              {/* Status Badge */}
              <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border ${statusColors[orderData.order_status]}`}>
                {React.createElement(statusIcons[orderData.order_status] || Clock, { className: 'w-5 h-5' })}
                <span className="font-semibold capitalize">{orderData.order_status}</span>
              </div>

              {/* Progress Bar */}
              <div className="mt-6">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${getStatusProgress(orderData.order_status)}%` }}
                  />
                </div>
              </div>

              {/* Timeline */}
              <div className="mt-8 space-y-4">
                {[
                  { status: 'placed', label: 'Order Placed', date: orderData.created_at },
                  { status: 'confirmed', label: 'Order Confirmed', date: orderData.confirmed_at },
                  { status: 'processing', label: 'Processing', date: orderData.processing_at },
                  { status: 'shipped', label: 'Shipped', date: orderData.shipped_at },
                  { status: 'delivered', label: 'Delivered', date: orderData.delivered_at }
                ].map((step, index) => {
                  const isCompleted = getStatusProgress(orderData.order_status) >= getStatusProgress(step.status);
                  const isCurrent = orderData.order_status === step.status;

                  return (
                    <div key={step.status} className="flex items-center gap-4">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        isCompleted ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-400'
                      }`}>
                        {isCompleted ? (
                          <CheckCircle className="w-6 h-6" />
                        ) : (
                          <Clock className="w-6 h-6" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p className={`font-semibold ${isCurrent ? 'text-blue-600' : 'text-gray-900'}`}>
                          {step.label}
                        </p>
                        {step.date && (
                          <p className="text-sm text-gray-600">
                            {new Date(step.date).toLocaleString()}
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Order Items */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Order Items</h3>
              <div className="space-y-4">
                {orderData.items?.map((item, index) => (
                  <div key={index} className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                    <div className="w-20 h-20 bg-gray-200 rounded-lg"></div>
                    <div className="flex-1">
                      <p className="font-semibold text-gray-900">{item.product_name}</p>
                      <p className="text-sm text-gray-600">Quantity: {item.quantity}</p>
                    </div>
                    <p className="font-bold text-gray-900">₹{(item.price * item.quantity).toLocaleString()}</p>
                  </div>
                ))}
              </div>

              <div className="mt-6 pt-6 border-t space-y-2">
                <div className="flex justify-between text-gray-600">
                  <span>Subtotal</span>
                  <span>₹{(orderData.subtotal || 0).toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Tax</span>
                  <span>₹{(orderData.tax_amount || 0).toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Shipping</span>
                  <span>₹{(orderData.shipping_cost || 0).toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-xl font-bold text-gray-900 pt-2 border-t">
                  <span>Total</span>
                  <span>₹{(orderData.total_amount || 0).toLocaleString()}</span>
                </div>
              </div>
            </div>

            {/* Delivery Info */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Delivery Information</h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">Delivery Address</p>
                  <p className="font-medium text-gray-900">
                    {orderData.shipping_address?.address}<br />
                    {orderData.shipping_address?.city}, {orderData.shipping_address?.state} {orderData.shipping_address?.pincode}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Contact</p>
                  <p className="font-medium text-gray-900">{orderData.customer_details?.phone}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Payment Method</p>
                  <p className="font-medium text-gray-900 uppercase">{orderData.payment_method}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Payment Status</p>
                  <p className={`font-medium ${orderData.payment_status === 'completed' ? 'text-green-600' : 'text-yellow-600'}`}>
                    {orderData.payment_status === 'completed' ? '✓ Paid' : 'Payment Pending'}
                  </p>
                </div>
              </div>
            </div>

            {/* Help Section */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-xl p-8 text-white text-center">
              <h3 className="text-2xl font-bold mb-2">Need Help?</h3>
              <p className="mb-6">Our customer support team is here to assist you</p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                  Contact Support
                </button>
                <button className="bg-transparent border-2 border-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors">
                  Report an Issue
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OrderTrackingPage;
