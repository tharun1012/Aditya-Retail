import React, { useState, useEffect, useRef } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Truck, 
  Package, 
  MapPin, 
  Phone, 
  Camera, 
  CheckCircle, 
  Clock, 
  DollarSign,
  CreditCard,
  Banknote,
  LogOut,
  AlertCircle,
  Navigation,
  Eye,
  Printer,
  X
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';


const DeliveryPersonInterface = () => {
  const navigate = useNavigate();
  const [deliveryUser, setDeliveryUser] = useState(null);
  const [challans, setChallans] = useState([]);
  const [selectedChallan, setSelectedChallan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedPhoto, setSelectedPhoto] = useState(null);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [detailChallan, setDetailChallan] = useState(null);
  const printRef = useRef();
  const [paymentData, setPaymentData] = useState({
    amount_received: '',
    payment_mode: 'Cash',
    reference_number: '',
    notes: ''
  });

  useEffect(() => {
    // Check if delivery person is logged in
    const token = localStorage.getItem('delivery_token');
    const userStr = localStorage.getItem('delivery_user');
    
    // Debug logging
    console.log('DeliveryPersonInterface - Token exists:', !!token);
    console.log('DeliveryPersonInterface - User string:', userStr);
    
    if (!token || !userStr) {
      console.log('No delivery credentials found, redirecting to login');
      // Use window.location for reliable redirect
      window.location.href = window.location.origin + window.location.pathname + '#/delivery-login';
      return;
    }
    
    try {
      const user = JSON.parse(userStr);
      if (!user || !user.id) {
        console.log('Invalid user data, redirecting to login');
        localStorage.removeItem('delivery_token');
        localStorage.removeItem('delivery_user');
        window.location.href = window.location.origin + window.location.pathname + '#/delivery-login';
        return;
      }
      
      setDeliveryUser(user);
      fetchAssignedDeliveries(user.id);
    } catch (error) {
      console.error('Error parsing delivery user:', error);
      localStorage.removeItem('delivery_token');
      localStorage.removeItem('delivery_user');
      window.location.href = window.location.origin + window.location.pathname + '#/delivery-login';
    }
  }, []);

  const fetchAssignedDeliveries = async (deliveryPersonId) => {
    try {
      const challanRes = await fetch(
        `${BACKEND_URL}/api/delivery-challans/delivery-person/assigned?delivery_person_id=${deliveryPersonId}`
      );
      const challanData = await challanRes.json();
      const challanList = (challanRes.ok ? (challanData.challans || []) : []).map(c => ({
        ...c,
        source: 'challan'
      }));

      const invoiceRes = await fetch(
        `${BACKEND_URL}/api/invoices/offline/invoices/out-for-delivery?delivery_person_id=${deliveryPersonId}`
      );
      const invoiceData = await invoiceRes.json();
      const invoiceList = (invoiceRes.ok ? (invoiceData.invoices || []) : []).map(inv => ({
        id: inv.id,
        challan_number: inv.invoice_number,
        invoice_number: inv.invoice_number,
        total_amount: inv.total_amount || 0,
        items: inv.items || [],
        customer: {
          name: inv.customer?.name || inv.customer_name || 'Customer',
          phone: inv.customer?.phone || inv.customer_phone || '',
          address: inv.customer?.address || inv.customer_address || '',
          city: inv.customer?.city || '',
          pincode: inv.customer?.pincode || ''
        },
        is_cod: (inv.payment_status !== 'paid'),
        is_pod: false,
        payment_collected: inv.payment_status === 'paid',
        delivery_photos: inv.delivery_photos || [],
        delivered_at: inv.delivered_at || null,
        payment_details: inv.payment_status === 'paid' ? { amount_received: inv.delivery_payment?.amount || inv.total_amount || 0 } : null,
        google_maps_link: null,
        status: inv.delivered_at ? 'delivered' : 'pending',
        source: 'invoice'
      }));

      let deliveredInvoiceList = [];
      try {
        const delRes = await fetch(
          `${BACKEND_URL}/api/invoices/offline/invoices/delivered?delivery_person_id=${deliveryPersonId}`
        );
        const delData = await delRes.json();
        deliveredInvoiceList = (delRes.ok ? (delData.invoices || []) : []).map(inv => ({
          id: inv.id,
          challan_number: inv.invoice_number,
          invoice_number: inv.invoice_number,
          total_amount: inv.total_amount || 0,
          items: inv.items || [],
          customer: {
            name: inv.customer?.name || inv.customer_name || 'Customer',
            phone: inv.customer?.phone || inv.customer_phone || '',
            address: inv.customer?.address || inv.customer_address || '',
            city: inv.customer?.city || '',
            pincode: inv.customer?.pincode || ''
          },
          is_cod: false,
          is_pod: false,
          payment_collected: true,
          delivery_photos: inv.delivery_photos || [],
          delivered_at: inv.delivered_at || null,
          payment_details: { amount_received: inv.delivery_payment?.amount || inv.total_amount || 0 },
          google_maps_link: null,
          status: 'delivered',
          source: 'invoice'
        }));
      } catch (e) {
        console.error('Error fetching delivered invoices:', e);
      }

      const seen = new Set();
      const merged = [...challanList, ...invoiceList, ...deliveredInvoiceList].filter(c => {
        if (seen.has(c.id)) return false;
        seen.add(c.id);
        return true;
      });
      setChallans(merged);
    } catch (error) {
      console.error('Error fetching deliveries:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePhotoUpload = async (item, photoFile) => {
    if (!photoFile) return;
    const challanId = item.id;

    setUploadingPhoto(true);
    try {
      const formData = new FormData();
      formData.append('file', photoFile);

      const uploadUrl = item.source === 'invoice'
        ? `${BACKEND_URL}/api/invoices/offline/invoices/${challanId}/upload-photo`
        : `${BACKEND_URL}/api/delivery-challans/${challanId}/upload-photo`;

      const response = await fetch(
        uploadUrl,
        {
          method: 'POST',
          body: formData
        }
      );

      const data = await response.json();

      if (response.ok) {
        alert('Photo uploaded successfully!');
        setSelectedPhoto(null);
        fetchAssignedDeliveries(deliveryUser.id);
      } else {
        alert(data.detail || 'Failed to upload photo');
      }
    } catch (error) {
      console.error('Error uploading photo:', error);
      alert('Failed to upload photo');
    } finally {
      setUploadingPhoto(false);
    }
  };

  const handleCollectPayment = async (challanId) => {
    const target = challans.find(c => c.id === challanId);
    if (target && target.source === 'invoice') {
      setChallans(prev => prev.map(c => c.id === challanId ? {
        ...c,
        payment_collected: true,
        payment_details: {
          amount_received: parseFloat(paymentData.amount_received),
          payment_mode: paymentData.payment_mode,
          reference_number: paymentData.reference_number || null
        }
      } : c));
      setShowPaymentModal(false);
      setPaymentData({ amount_received: '', payment_mode: 'Cash', reference_number: '', notes: '' });
      return;
    }
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/delivery-challans/${challanId}/collect-payment?delivery_person_id=${deliveryUser.id}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            amount_received: parseFloat(paymentData.amount_received),
            payment_mode: paymentData.payment_mode,
            reference_number: paymentData.reference_number || null,
            notes: paymentData.notes || null
          })
        }
      );

      const data = await response.json();

      if (response.ok) {
        alert('Payment collected successfully!');
        setShowPaymentModal(false);
        setPaymentData({
          amount_received: '',
          payment_mode: 'Cash',
          reference_number: '',
          notes: ''
        });
        fetchAssignedDeliveries(deliveryUser.id);
      } else {
        alert(data.detail || 'Failed to collect payment');
      }
    } catch (error) {
      console.error('Error collecting payment:', error);
      alert('Failed to collect payment');
    }
  };

  const handleMarkDelivered = async (item) => {
    try {
      const isInvoice = item.source === 'invoice';
      const url = isInvoice
        ? `${BACKEND_URL}/api/invoices/offline/invoices/mark-delivered`
        : `${BACKEND_URL}/api/delivery-challans/${item.id}/status`;

      const body = isInvoice
        ? JSON.stringify({
            invoice_id: item.id,
            delivered_by: deliveryUser.id,
            payment_collected: item.payment_collected || false,
            payment_amount: item.payment_details?.amount_received ?? item.total_amount,
            payment_method: item.payment_details?.payment_mode || null,
            payment_reference: item.payment_details?.reference_number || null
          })
        : JSON.stringify({
            status: 'delivered',
            delivered_by: deliveryUser.full_name
          });

      const response = await fetch(url, {
        method: isInvoice ? 'POST' : 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body
      });

      const data = await response.json();

      if (response.ok) {
        alert('Delivery marked as completed!');
        fetchAssignedDeliveries(deliveryUser.id);
      } else {
        alert(data.detail || 'Failed to update delivery status');
      }
    } catch (error) {
      console.error('Error updating delivery status:', error);
      alert('Failed to update delivery status');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('delivery_token');
    localStorage.removeItem('delivery_user');
    navigate('/delivery-login');
  };

  const openPaymentModal = (challan) => {
    setSelectedChallan(challan);
    setPaymentData({
      ...paymentData,
      amount_received: challan.total_amount.toString()
    });
    setShowPaymentModal(true);
  };

  const openDetailModal = (challan) => {
    setDetailChallan(challan);
    setShowDetailModal(true);
  };

  const handlePrint = () => {
    const printContent = printRef.current;
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
        <head>
          <title>Delivery Challan - ${detailChallan?.challan_number}</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .header { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #333; padding-bottom: 10px; }
            .header h1 { margin: 0; font-size: 24px; }
            .header p { margin: 5px 0; color: #666; }
            .section { margin-bottom: 15px; }
            .section-title { font-weight: bold; font-size: 14px; margin-bottom: 5px; color: #333; border-bottom: 1px solid #ddd; padding-bottom: 3px; }
            .row { display: flex; justify-content: space-between; margin-bottom: 5px; }
            .label { color: #666; }
            .value { font-weight: 500; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f5f5f5; }
            .total-row { font-weight: bold; background-color: #f0f0f0; }
            .status-badge { display: inline-block; padding: 3px 10px; border-radius: 15px; font-size: 12px; }
            .status-delivered { background-color: #d4edda; color: #155724; }
            .footer { margin-top: 30px; text-align: center; font-size: 12px; color: #666; }
          </style>
        </head>
        <body>
          ${printContent.innerHTML}
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading deliveries...</p>
        </div>
      </div>
    );
  }

  const pendingChallans = challans.filter(c => c.status === 'pending' || c.status === 'in_transit');
  const completedChallans = challans.filter(c => c.status === 'delivered');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 shadow-lg">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="bg-white/20 p-3 rounded-full">
              <Truck className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Welcome, {deliveryUser?.full_name}</h1>
              <p className="text-blue-100">{deliveryUser?.phone}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span>Logout</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="max-w-6xl mx-auto p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-4">
              <div className="bg-orange-100 p-4 rounded-full">
                <Clock className="w-8 h-8 text-orange-600" />
              </div>
              <div>
                <div className="text-3xl font-bold text-orange-600">{pendingChallans.length}</div>
                <div className="text-gray-600">Pending Deliveries</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-4">
              <div className="bg-green-100 p-4 rounded-full">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <div>
                <div className="text-3xl font-bold text-green-600">{completedChallans.length}</div>
                <div className="text-gray-600">Completed</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-4">
              <div className="bg-blue-100 p-4 rounded-full">
                <Package className="w-8 h-8 text-blue-600" />
              </div>
              <div>
                <div className="text-3xl font-bold text-blue-600">{challans.length}</div>
                <div className="text-gray-600">Total Deliveries</div>
              </div>
            </div>
          </div>
        </div>

        {/* Pending Deliveries */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Package className="w-6 h-6 text-blue-600" />
            Pending Deliveries
          </h2>

          {pendingChallans.length === 0 ? (
            <div className="text-center py-12">
              <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">No pending deliveries</p>
            </div>
          ) : (
            <div className="space-y-6">
              {pendingChallans.map((challan) => (
                <div key={challan.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                  {/* Challan Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <div className="text-lg font-bold text-gray-900">{challan.challan_number}</div>
                      <div className="text-sm text-gray-500">Invoice: {challan.invoice_number}</div>
                      {(challan.is_cod || challan.is_pod) && (
                        <div className="mt-2 inline-flex items-center gap-1 bg-orange-100 text-orange-700 px-3 py-1 rounded-full text-sm font-semibold">
                          <DollarSign className="w-4 h-4" />
                          {challan.is_cod ? 'Cash on Delivery' : 'Payment on Delivery'}
                        </div>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600">₹{challan.total_amount.toLocaleString()}</div>
                      <div className="text-sm text-gray-500">{challan.items.length} items</div>
                    </div>
                  </div>

                  {/* Customer Details */}
                  <div className="bg-gray-50 rounded-lg p-4 mb-4">
                    <h4 className="font-semibold text-gray-900 mb-2">Customer Details</h4>
                    <div className="space-y-1 text-sm text-gray-700">
                      <div><strong>Name:</strong> {challan.customer.name}</div>
                      <div className="flex items-center gap-2">
                        <Phone className="w-4 h-4" />
                        {challan.customer.phone}
                      </div>
                      <div className="flex items-start gap-2">
                        <MapPin className="w-4 h-4 mt-0.5" />
                        <div>
                          {challan.customer.address}, {challan.customer.city} - {challan.customer.pincode}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-wrap gap-3">
                    {/* Google Maps */}
                    <a
                      href={challan.google_maps_link || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent((challan.customer?.address || '') + ', ' + (challan.customer?.city || '') + ' ' + (challan.customer?.pincode || ''))}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                    >
                      <Navigation className="w-4 h-4" />
                      Open in Maps
                    </a>

                    {/* Collect Payment (COD/POD only) */}
                    {(challan.is_cod || challan.is_pod) && !challan.payment_collected && (
                      <button
                        onClick={() => openPaymentModal(challan)}
                        className="flex items-center gap-2 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors"
                      >
                        <DollarSign className="w-4 h-4" />
                        Collect Payment
                      </button>
                    )}

                    {/* Upload Photo */}
                    <label className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors cursor-pointer">
                      <Camera className="w-4 h-4" />
                      Upload Photo
                      <input
                        type="file"
                        accept="image/*"
                        capture="environment"
                        className="hidden"
                        onChange={(e) => {
                          const file = e.target.files[0];
                          if (file) {
                            setSelectedPhoto(file);
                            setSelectedChallan(challan);
                            handlePhotoUpload(challan, file);
                          }
                        }}
                      />
                    </label>

                    {/* Mark Delivered */}
                    {challan.delivery_photos.length > 0 && (!challan.is_cod && !challan.is_pod || challan.payment_collected) && (
                      <button
                        onClick={() => handleMarkDelivered(challan)}
                        className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                      >
                        <CheckCircle className="w-4 h-4" />
                        Mark Delivered
                      </button>
                    )}
                  </div>

                  {/* Payment Collected Status */}
                  {challan.payment_collected && (
                    <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-3 flex items-center gap-2 text-green-700">
                      <CheckCircle className="w-5 h-5" />
                      <span className="font-semibold">Payment Collected: ₹{challan.payment_details?.amount_received.toLocaleString()}</span>
                    </div>
                  )}

                  {/* Photos Uploaded Status */}
                  {challan.delivery_photos.length > 0 && (
                    <div className="mt-2 text-sm text-gray-600 flex items-center gap-2">
                      <Camera className="w-4 h-4" />
                      {challan.delivery_photos.length} photo(s) uploaded
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Completed Deliveries */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <CheckCircle className="w-6 h-6 text-green-600" />
            Completed Deliveries
          </h2>

          {completedChallans.length === 0 ? (
            <div className="text-center py-12">
              <CheckCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">No completed deliveries yet</p>
            </div>
          ) : (
            <div className="space-y-4">
              {completedChallans.map((challan) => (
                <div key={challan.id} className="border border-green-200 bg-green-50 rounded-lg p-4">
                  {/* Challan Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="text-lg font-bold text-gray-900">{challan.challan_number}</div>
                      <div className="text-sm text-gray-500">Invoice: {challan.invoice_number}</div>
                      <div className="mt-1 inline-flex items-center gap-1 bg-green-100 text-green-700 px-2 py-0.5 rounded-full text-xs font-semibold">
                        <CheckCircle className="w-3 h-3" />
                        Delivered
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold text-green-600">₹{challan.total_amount?.toLocaleString()}</div>
                      <div className="text-sm text-gray-500">{challan.items?.length || 0} items</div>
                    </div>
                  </div>

                  {/* Customer Details */}
                  <div className="bg-white rounded-lg p-3 mb-3">
                    <div className="text-sm text-gray-700">
                      <div><strong>Customer:</strong> {challan.customer?.name}</div>
                      <div className="flex items-center gap-1 text-gray-600">
                        <MapPin className="w-3 h-3" />
                        {challan.customer?.address}, {challan.customer?.city}
                      </div>
                    </div>
                  </div>

                  {/* Delivery Info */}
                  <div className="text-sm text-gray-600 mb-3">
                    {challan.delivered_at && (
                      <div>Delivered: {new Date(challan.delivered_at).toLocaleString()}</div>
                    )}
                    {challan.payment_collected && (
                      <div className="text-green-700 font-medium">
                        Payment Collected: ₹{challan.payment_details?.amount_received?.toLocaleString()} ({challan.payment_details?.payment_mode})
                      </div>
                    )}
                    {challan.delivery_photos?.length > 0 && (
                      <div className="flex items-center gap-1 mt-1">
                        <Camera className="w-3 h-3" />
                        {challan.delivery_photos.length} delivery photo(s)
                      </div>
                    )}
                  </div>

                  {/* View Details Button */}
                  <button
                    onClick={() => openDetailModal(challan)}
                    className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
                  >
                    <Eye className="w-4 h-4" />
                    View Details & Print
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Challan Detail Modal */}
      {showDetailModal && detailChallan && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl my-8">
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 rounded-t-xl flex items-center justify-between">
              <h3 className="text-xl font-bold">Delivery Challan Details</h3>
              <div className="flex items-center gap-2">
                <button
                  onClick={handlePrint}
                  className="flex items-center gap-2 bg-white/20 hover:bg-white/30 px-3 py-1.5 rounded-lg transition-colors text-sm"
                >
                  <Printer className="w-4 h-4" />
                  Print
                </button>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="p-1 hover:bg-white/20 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Printable Content */}
            <div ref={printRef} className="p-6">
              {/* Header */}
              <div className="header text-center mb-6 border-b-2 border-gray-300 pb-4">
                <h1 className="text-2xl font-bold text-gray-900">DELIVERY CHALLAN</h1>
                <p className="text-lg font-semibold text-blue-600 mt-1">{detailChallan.challan_number}</p>
                <p className="text-sm text-gray-600">Invoice: {detailChallan.invoice_number}</p>
                <span className={`inline-block mt-2 px-3 py-1 rounded-full text-sm font-semibold ${
                  detailChallan.status === 'delivered' ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'
                }`}>
                  {detailChallan.status?.toUpperCase()}
                </span>
              </div>

              {/* Store & Customer Info */}
              <div className="grid grid-cols-2 gap-6 mb-6">
                {/* From Store */}
                <div className="section">
                  <div className="section-title font-bold text-gray-700 border-b pb-1 mb-2">From (Store)</div>
                  <div className="text-sm space-y-1">
                    <div className="font-semibold">{detailChallan.store_details?.name}</div>
                    <div>{detailChallan.store_details?.address}</div>
                    <div>{detailChallan.store_details?.city}, {detailChallan.store_details?.state} - {detailChallan.store_details?.pincode}</div>
                    <div>Phone: {detailChallan.store_details?.phone}</div>
                    <div>GSTIN: {detailChallan.store_details?.gst_number}</div>
                  </div>
                </div>

                {/* To Customer */}
                <div className="section">
                  <div className="section-title font-bold text-gray-700 border-b pb-1 mb-2">Ship To (Customer)</div>
                  <div className="text-sm space-y-1">
                    <div className="font-semibold">{detailChallan.customer?.name}</div>
                    <div>{detailChallan.customer?.shipping_address || detailChallan.customer?.address}</div>
                    <div>{detailChallan.customer?.shipping_city || detailChallan.customer?.city}, {detailChallan.customer?.shipping_state || detailChallan.customer?.state} - {detailChallan.customer?.shipping_pincode || detailChallan.customer?.pincode}</div>
                    <div>Phone: {detailChallan.customer?.phone}</div>
                    {detailChallan.customer?.gst_number && <div>GSTIN: {detailChallan.customer?.gst_number}</div>}
                  </div>
                </div>
              </div>

              {/* Items Table */}
              <div className="section mb-6">
                <div className="section-title font-bold text-gray-700 border-b pb-1 mb-2">Items</div>
                <table className="w-full border-collapse text-sm">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="border p-2 text-left">#</th>
                      <th className="border p-2 text-left">Product</th>
                      <th className="border p-2 text-center">HSN</th>
                      <th className="border p-2 text-center">Qty</th>
                      <th className="border p-2 text-right">Rate</th>
                      <th className="border p-2 text-right">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {detailChallan.items?.map((item, index) => (
                      <tr key={index}>
                        <td className="border p-2">{index + 1}</td>
                        <td className="border p-2">{item.product_name}</td>
                        <td className="border p-2 text-center">{item.hsn_code}</td>
                        <td className="border p-2 text-center">{item.quantity}</td>
                        <td className="border p-2 text-right">₹{item.rate?.toLocaleString()}</td>
                        <td className="border p-2 text-right">₹{item.total?.toLocaleString()}</td>
                      </tr>
                    ))}
                    <tr className="total-row bg-gray-100 font-bold">
                      <td colSpan="5" className="border p-2 text-right">Total Amount:</td>
                      <td className="border p-2 text-right">₹{detailChallan.total_amount?.toLocaleString()}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Delivery Info */}
              <div className="grid grid-cols-2 gap-6 mb-6">
                <div className="section">
                  <div className="section-title font-bold text-gray-700 border-b pb-1 mb-2">Delivery Details</div>
                  <div className="text-sm space-y-1">
                    <div><span className="text-gray-600">Driver:</span> {detailChallan.delivery_person_name}</div>
                    <div><span className="text-gray-600">Phone:</span> {detailChallan.delivery_person_phone}</div>
                    <div><span className="text-gray-600">Vehicle:</span> {detailChallan.vehicle_number}</div>
                    {detailChallan.delivered_at && (
                      <div><span className="text-gray-600">Delivered At:</span> {new Date(detailChallan.delivered_at).toLocaleString()}</div>
                    )}
                  </div>
                </div>

                <div className="section">
                  <div className="section-title font-bold text-gray-700 border-b pb-1 mb-2">Payment Details</div>
                  <div className="text-sm space-y-1">
                    {detailChallan.is_cod && <div className="text-orange-600 font-semibold">Cash on Delivery</div>}
                    {detailChallan.is_pod && <div className="text-orange-600 font-semibold">Payment on Delivery</div>}
                    {detailChallan.payment_collected ? (
                      <>
                        <div className="text-green-600 font-semibold">Payment Collected ✓</div>
                        <div><span className="text-gray-600">Amount:</span> ₹{detailChallan.payment_details?.amount_received?.toLocaleString()}</div>
                        <div><span className="text-gray-600">Mode:</span> {detailChallan.payment_details?.payment_mode}</div>
                        {detailChallan.payment_details?.reference_number && (
                          <div><span className="text-gray-600">Ref:</span> {detailChallan.payment_details?.reference_number}</div>
                        )}
                      </>
                    ) : (
                      <div className="text-gray-500">Payment Pending</div>
                    )}
                  </div>
                </div>
              </div>

              {/* E-Way Bill */}
              {detailChallan.eway_bill_number && (
                <div className="section mb-4">
                  <div className="section-title font-bold text-gray-700 border-b pb-1 mb-2">E-Way Bill</div>
                  <div className="text-sm">
                    <span className="font-semibold">{detailChallan.eway_bill_number}</span>
                  </div>
                </div>
              )}

              {/* Footer */}
              <div className="footer text-center text-xs text-gray-500 mt-6 pt-4 border-t">
                <p>This is a computer generated document. No signature required.</p>
                <p>Generated on: {new Date().toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Payment Collection Modal */}
      {showPaymentModal && selectedChallan && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-md">
            <div className="bg-gradient-to-r from-orange-600 to-red-600 text-white p-6 rounded-t-xl">
              <h3 className="text-xl font-bold flex items-center gap-2">
                <DollarSign className="w-6 h-6" />
                Collect Payment
              </h3>
              <p className="text-orange-100 mt-1">Invoice: {selectedChallan.invoice_number}</p>
            </div>

            <div className="p-6 space-y-4">
              {/* Amount */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Amount to Collect
                </label>
                <input
                  type="number"
                  value={paymentData.amount_received}
                  onChange={(e) => setPaymentData({...paymentData, amount_received: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  placeholder="Enter amount"
                />
              </div>

              {/* Payment Mode */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Payment Mode
                </label>
                <select
                  value={paymentData.payment_mode}
                  onChange={(e) => setPaymentData({...paymentData, payment_mode: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                >
                  <option value="Cash">Cash</option>
                  <option value="Card">Card</option>
                  <option value="UPI">UPI</option>
                  <option value="Bank Transfer">Bank Transfer</option>
                  <option value="Cheque">Cheque</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              {/* Reference Number (shown for non-cash) */}
              {paymentData.payment_mode !== 'Cash' && (
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Reference Number {paymentData.payment_mode !== 'Cash' && '*'}
                  </label>
                  <input
                    type="text"
                    value={paymentData.reference_number}
                    onChange={(e) => setPaymentData({...paymentData, reference_number: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    placeholder="Transaction ID / Reference"
                  />
                </div>
              )}

              {/* Notes */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Notes (Optional)
                </label>
                <textarea
                  value={paymentData.notes}
                  onChange={(e) => setPaymentData({...paymentData, notes: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  rows="3"
                  placeholder="Any additional notes..."
                />
              </div>

              {/* Buttons */}
              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => setShowPaymentModal(false)}
                  className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-semibold"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleCollectPayment(selectedChallan.id)}
                  className="flex-1 px-4 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors font-semibold"
                >
                  Confirm Payment
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DeliveryPersonInterface;