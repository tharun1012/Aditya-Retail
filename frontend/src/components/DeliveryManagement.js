import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { utils } from '../services/api';
import { Package, Truck, MapPin, CheckCircle, TrendingUp, ArrowLeft, IndianRupee } from 'lucide-react';

const DeliveryManagement = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('pending');
  const [pendingOrders, setPendingOrders] = useState([]);
  const [activeShipments, setActiveShipments] = useState([]);
  const [deliveredShipments, setDeliveredShipments] = useState([]);
  const [analytics, setAnalytics] = useState({});

  useEffect(() => {
    fetchDeliveryData();
  }, [activeTab]);

  const fetchDeliveryData = async () => {
    try {
      setLoading(true);

      const summaryRes = await utils.fetchAPI('/api/delivery-challans/reports/summary');
      const summaryData = await summaryRes.json();
      const summary = summaryData.summary || {};

      const inTransitRes = await utils.fetchAPI('/api/delivery-challans/?status=in_transit&limit=1');
      const inTransitData = await inTransitRes.json();

      const pendingRes = await utils.fetchAPI('/api/delivery-challans/pending-orders');
      const pendingData = await pendingRes.json();

      setAnalytics({
        total_shipments: summary.total_challans || 0,
        in_transit: inTransitData.total || 0,
        delivered: summary.completed || 0,
        delivery_rate: summary.completion_rate || 0,
        pending: pendingData.total || 0
      });

      if (activeTab === 'pending') {
        setPendingOrders(pendingData.orders || []);
      } else if (activeTab === 'active') {
        const activeRes = await utils.fetchAPI('/api/delivery-challans/?status=in_transit');
        const activeData = await activeRes.json();
        setActiveShipments(activeData.challans || []);
      } else if (activeTab === 'delivered') {
        const deliveredRes = await utils.fetchAPI('/api/delivery-challans/?status=delivered');
        const deliveredData = await deliveredRes.json();
        setDeliveredShipments(deliveredData.challans || []);
      }

      setLoading(false);
    } catch (error) {
      console.error('Error fetching delivery data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <button
          onClick={() => navigate('/admin')}
          className="flex items-center px-4 py-2 mb-6 text-gray-700 bg-white hover:bg-gray-100 rounded-lg transition-all border border-gray-300 hover:border-gray-400 shadow-sm"
          data-testid="back-to-dashboard-btn"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          <span className="font-medium">Back to Dashboard</span>
        </button>

        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Delivery & Logistics</h1>
          <p className="text-gray-600 mt-2">Manage shipments and track deliveries</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Shipments</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{analytics.total_shipments || 0}</p>
              </div>
              <Package className="w-10 h-10 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">In Transit</p>
                <p className="text-2xl font-bold text-orange-600 mt-1">{analytics.in_transit || 0}</p>
              </div>
              <Truck className="w-10 h-10 text-orange-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Delivered</p>
                <p className="text-2xl font-bold text-green-600 mt-1">{analytics.delivered || 0}</p>
              </div>
              <CheckCircle className="w-10 h-10 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Delivery Rate</p>
                <p className="text-2xl font-bold text-blue-600 mt-1">{analytics.delivery_rate || 0}%</p>
              </div>
              <TrendingUp className="w-10 h-10 text-blue-500" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <div className="flex">
              <button
                onClick={() => setActiveTab('pending')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'pending'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Pending Shipments ({analytics.pending || 0})
              </button>
              <button
                onClick={() => setActiveTab('active')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'active'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Active Shipments ({analytics.in_transit || 0})
              </button>
              <button
                onClick={() => setActiveTab('delivered')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'delivered'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Delivered ({analytics.delivered || 0})
              </button>
            </div>
          </div>

          <div className="p-6">
            {activeTab === 'pending' && (
              <div>
                {pendingOrders.length === 0 ? (
                  <div className="text-center py-12">
                    <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No pending shipments</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {pendingOrders.map((order) => (
                      <div key={order.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3">
                              <Package className="w-5 h-5 text-gray-400" />
                              <div>
                                <p className="font-semibold text-gray-900">
                                  Order #{order.order_number}
                                </p>
                                <p className="text-sm text-gray-600">
                                  {order.customer_name || 'Customer'}
                                </p>
                                <p className="text-sm text-gray-500">
                                  {order.customer_city || '-'}, {order.customer_pincode || '-'}
                                </p>
                                <p className="text-sm text-gray-500">
                                  Store: {order.store_name || order.store_code || '-'}
                                </p>
                              </div>
                            </div>
                          </div>
                          <span className="px-3 py-1 text-xs rounded bg-amber-100 text-amber-700">
                            Awaiting assignment
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'active' && (
              <div>
                {activeShipments.length === 0 ? (
                  <div className="text-center py-12">
                    <Truck className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No active shipments</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {activeShipments.map((shipment) => (
                      <div key={shipment.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-3">
                              <Truck className="w-5 h-5 text-orange-500" />
                              <div>
                                <p className="font-semibold text-gray-900">
                                  Challan: {shipment.challan_number}
                                </p>
                                <p className="text-sm text-gray-600">
                                  {shipment.delivery_person_name || 'Unassigned'} • {shipment.customer?.name}
                                </p>
                                <div className="flex items-center gap-2 mt-1">
                                  <span className={`px-2 py-1 text-xs rounded ${
                                    shipment.status === 'in_transit' ? 'bg-orange-100 text-orange-700' :
                                    shipment.status === 'delivered' ? 'bg-green-100 text-green-700' :
                                    'bg-gray-100 text-gray-700'
                                  }`}>
                                    {shipment.status}
                                  </span>
                                  <MapPin className="w-3 h-3 text-gray-400" />
                                  <span className="text-xs text-gray-600">
                                    {shipment.customer?.city || '-'}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                          {shipment.google_maps_link && (
                            <a
                              href={shipment.google_maps_link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                            >
                              View on Map
                            </a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'delivered' && (
              <div>
                {deliveredShipments.length === 0 ? (
                  <div className="text-center py-12">
                    <CheckCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No delivered shipments yet</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {deliveredShipments.map((shipment) => (
                      <div key={shipment.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3">
                              <CheckCircle className="w-5 h-5 text-green-500" />
                              <div>
                                <p className="font-semibold text-gray-900">
                                  Challan: {shipment.challan_number}
                                </p>
                                <p className="text-sm text-gray-600">
                                  {shipment.delivery_person_name || 'Unassigned'} • {shipment.customer?.name}
                                </p>
                                <p className="text-sm text-gray-500">
                                  {shipment.customer?.city || '-'}
                                </p>
                                {shipment.delivered_at && (
                                  <p className="text-xs text-gray-500 mt-1">
                                    Delivered on {new Date(shipment.delivered_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                          <div className="text-right">
                            <span className="px-3 py-1 text-xs rounded bg-green-100 text-green-700 inline-block mb-1">
                              Delivered
                            </span>
                            {(shipment.is_cod || shipment.is_pod) && (
                              <div className="flex items-center justify-end gap-1 text-sm text-gray-700">
                                <IndianRupee className="w-3 h-3" />
                                <span>{shipment.total_amount || 0}</span>
                                <span className={`ml-1 px-2 py-0.5 text-xs rounded ${
                                  shipment.payment_collected ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                }`}>
                                  {shipment.payment_collected ? 'Collected' : 'Not Collected'}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DeliveryManagement;
