import React, { useEffect, useState } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import { CheckCircle, XCircle, Loader, Package } from 'lucide-react';
import { useCart } from '../hooks/useCart';

const PaymentSuccess = () => {
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { clearCart } = useCart();
  const [loading, setLoading] = useState(true);
  const [paymentStatus, setPaymentStatus] = useState(null);
  const [orderDetails, setOrderDetails] = useState(null);

  
  useEffect(() => {
    // Check if this is a COD order (from location state)
    if (location.state?.paymentMethod === 'Cash on Delivery') {
      setPaymentStatus('cod');
      setOrderDetails({
        orderId: location.state.orderNumber,
        paymentMode: 'Cash on Delivery',
        message: location.state.message
      });
      setLoading(false);
      return;
    }

    // Check URL query params (Pine Labs sends: ?order_id=xxx&status=PROCESSED&signature=xxx)
    const urlParams = new URLSearchParams(window.location.search);
    const plOrderId = urlParams.get('order_id');
    const plStatus = urlParams.get('status');

    if (plOrderId && plStatus) {
      handlePineLabsCallback(plOrderId, plStatus);
      return;
    }

    // Check for Pine Labs payment (stored in localStorage)
    const pineLabsOrderId = localStorage.getItem('pine_labs_order_id');
    const pineLabsTxnId = localStorage.getItem('pine_labs_transaction_id');
    const paymentGateway = localStorage.getItem('payment_gateway');
    const pendingTxnId = localStorage.getItem('pending_transaction_id');

    if (paymentGateway === 'pinelabs' || pineLabsOrderId || pineLabsTxnId) {
      verifyPineLabsPayment(pineLabsOrderId || pendingTxnId, pineLabsTxnId || pendingTxnId);
      return;
    }

    // FALLBACK: localStorage empty (cross-domain redirect or cache cleared).
    // Try to recover via customer's recent pending order.
    recoverFromBackend();
  }, []);

  // Recovery: query backend for the user's most recent pending Pine Labs order
  const recoverFromBackend = async () => {
    try {
      // Try the logged-in user first
      let email = null;
      let phone = null;
      try {
        const stored = localStorage.getItem('user') || sessionStorage.getItem('user');
        if (stored) {
          const u = JSON.parse(stored);
          email = u?.email;
          phone = u?.phone;
        }
      } catch (e) { /* ignore */ }

      if (!email && !phone) {
        // Last resort — ask the user
        const promptedEmail = window.prompt(
          'We need to verify your payment but lost the session.\n\nPlease enter the email used for checkout:'
        );
        if (!promptedEmail) {
          setPaymentStatus('error');
          setLoading(false);
          return;
        }
        email = promptedEmail.trim();
      }

      const params = new URLSearchParams();
      if (email) params.append('email', email);
      if (phone) params.append('phone', phone);
      const res = await fetch(`${BACKEND_URL}/api/pine-labs/recent-pending-order?${params}`);
      const data = await res.json();

      if (data.success && data.order_number) {
        // Trigger reconcile by merchant order — backend will look up live status
        const confirmRes = await fetch(`${BACKEND_URL}/api/pine-labs/confirm-payment`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            order_id: 'unknown',
            status: 'PROCESSED',
            merchant_order_id: data.order_number,
          }),
        });
        await confirmRes.json();

        setPaymentStatus('success');
        setOrderDetails({
          orderId: data.order_number,
          transactionId: 'Recovered',
          amount: data.total_amount,
          paymentMode: 'Pine Labs'
        });
        clearCart();
        setLoading(false);
      } else {
        setPaymentStatus('error');
        setLoading(false);
      }
    } catch (e) {
      console.error('[PaymentSuccess] Recovery failed:', e);
      setPaymentStatus('error');
      setLoading(false);
    }
  };

  // Handle Pine Labs redirect callback (status params in URL from Pine Labs redirect)
  const handlePineLabsCallback = async (orderId, status) => {
    const upperStatus = (status || '').toUpperCase();
    console.log('[PaymentSuccess] Pine Labs callback:', orderId, upperStatus);

    // Read all query params (including signature, error_code, error_message)
    const urlParams = new URLSearchParams(window.location.search);
    const signature = urlParams.get('signature');
    const errorCode = urlParams.get('error_code');
    const errorMessage = urlParams.get('error_message');
    const ourOrderNumber = localStorage.getItem('pending_order_id');

    // Clean URL params
    window.history.replaceState({}, document.title, window.location.pathname);

    // Notify backend so it records callback + updates the order
    try {
      const confirmRes = await fetch(`${BACKEND_URL}/api/pine-labs/confirm-payment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          order_id: orderId,
          status,
          signature,
          error_code: errorCode,
          error_message: errorMessage,
          merchant_order_id: ourOrderNumber,
        }),
      });
      const confirmData = await confirmRes.json();
      console.log('[PaymentSuccess] Confirm-payment response:', confirmData);
    } catch (err) {
      console.error('[PaymentSuccess] Confirm-payment error:', err);
    }

    if (['PROCESSED', 'AUTHORIZED', 'CHARGED', 'CAPTURED', 'SUCCESS'].includes(upperStatus)) {
      setPaymentStatus('success');
      setOrderDetails({
        orderId: ourOrderNumber || orderId,
        transactionId: orderId,
        paymentMode: 'Pine Labs'
      });
      clearCart();
      localStorage.removeItem('pine_labs_order_id');
      localStorage.removeItem('pine_labs_transaction_id');
      localStorage.removeItem('pending_order_id');
      localStorage.removeItem('pending_transaction_id');
      localStorage.removeItem('payment_gateway');
      setLoading(false);
    } else if (['FAILED', 'DECLINED', 'REJECTED', 'CANCELLED', 'ERROR'].includes(upperStatus)) {
      setPaymentStatus('failed');
      localStorage.removeItem('pine_labs_order_id');
      localStorage.removeItem('pine_labs_transaction_id');
      localStorage.removeItem('pending_transaction_id');
      localStorage.removeItem('payment_gateway');
      setLoading(false);
    } else {
      // Unknown status — verify via API
      verifyPineLabsPayment(orderId, orderId);
    }
  };

  const verifyPineLabsPayment = async (orderId, txnId, retryCount = 0) => {
    try {
      const checkId = txnId || orderId;
      const response = await fetch(`${BACKEND_URL}/api/pine-labs/status/${checkId}`);
      const data = await response.json();

      console.log('[PaymentSuccess] Pine Labs status:', data.payment_status, 'plural:', data.plural_status, 'retry:', retryCount);

      if (data.success && data.payment_status === 'captured') {
        // Sync order status to backend (in case URL-callback path didn't run)
        try {
          await fetch(`${BACKEND_URL}/api/pine-labs/confirm-payment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              order_id: checkId,
              status: data.plural_status || 'PROCESSED',
              merchant_order_id: localStorage.getItem('pending_order_id'),
            }),
          });
        } catch (e) {
          console.warn('[PaymentSuccess] Confirm-payment sync failed:', e);
        }

        setPaymentStatus('success');
        setOrderDetails({
          orderId: localStorage.getItem('pending_order_id') || orderId,
          transactionId: checkId,
          amount: data.amount ? data.amount / 100 : 0,
          paymentMode: 'Pine Labs'
        });
        clearCart();
        localStorage.removeItem('pine_labs_order_id');
        localStorage.removeItem('pine_labs_transaction_id');
        localStorage.removeItem('pending_order_id');
        localStorage.removeItem('pending_transaction_id');
        localStorage.removeItem('payment_gateway');
        setLoading(false);
      } else if (data.payment_status === 'failed' || data.payment_status === 'cancelled') {
        setPaymentStatus('failed');
        localStorage.removeItem('pine_labs_order_id');
        localStorage.removeItem('pine_labs_transaction_id');
        localStorage.removeItem('pending_transaction_id');
        localStorage.removeItem('payment_gateway');
        setLoading(false);
      } else if (data.payment_status === 'pending' && retryCount < 3) {
        // Payment might still be processing — retry after delay
        setTimeout(() => {
          verifyPineLabsPayment(orderId, txnId, retryCount + 1);
        }, 3000); // Wait 3 seconds before retry
        return; // Don't set loading false yet
      } else {
        // After retries exhausted or unknown status — show failed
        setPaymentStatus('failed');
        setLoading(false);
      }
    } catch (error) {
      console.error('Pine Labs verification error:', error);
      if (retryCount < 2) {
        // Network error — retry
        setTimeout(() => {
          verifyPineLabsPayment(orderId, txnId, retryCount + 1);
        }, 2000);
        return;
      }
      setPaymentStatus('error');
      setLoading(false);
    }
  };

  const verifyPayment = async () => {
    try {
      // Get transaction ID from localStorage
      const transactionId = localStorage.getItem('pending_transaction_id');
      const orderId = localStorage.getItem('pending_order_id');

      if (!transactionId) {
        setPaymentStatus('error');
        setLoading(false);
        return;
      }

      // Verify payment status with PhonePe
      const response = await fetch(
        `${BACKEND_URL}/api/phonepe/status/${transactionId}`
      );
      const data = await response.json();

      if (data.success && data.data.state === 'COMPLETED') {
        setPaymentStatus('success');
        setOrderDetails({
          orderId: orderId,
          transactionId: data.data.transactionId,
          amount: data.data.amount / 100, // Convert from paise to rupees
          paymentMode: data.data.paymentInstrument?.type
        });
        
        // Clear cart and localStorage
        clearCart();
        localStorage.removeItem('pending_transaction_id');
        localStorage.removeItem('pending_order_id');
      } else {
        setPaymentStatus('failed');
      }
    } catch (error) {
      console.error('Payment verification error:', error);
      setPaymentStatus('error');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="h-16 w-16 text-blue-600 animate-spin mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Verifying Payment...</h2>
          <p className="text-gray-600">Please wait while we confirm your payment</p>
        </div>
      </div>
    );
  }

  if (paymentStatus === 'cod') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8 text-center">
          <div className="mb-6">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="h-12 w-12 text-green-500" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">Order Placed Successfully!</h1>
            <p className="text-gray-600">Your Cash on Delivery order has been confirmed</p>
          </div>

          {orderDetails && (
            <div className="bg-blue-50 rounded-lg p-6 mb-6 text-left">
              <h3 className="font-semibold text-gray-900 mb-4">Order Details</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Order Number:</span>
                  <span className="font-semibold">{orderDetails.orderId}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Payment Method:</span>
                  <span className="font-semibold text-green-600">{orderDetails.paymentMode}</span>
                </div>
              </div>
              {orderDetails.message && (
                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800">
                  {orderDetails.message}
                </div>
              )}
            </div>
          )}

          <div className="space-y-3">
            <button
              onClick={() => navigate('/my-account')}
              className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold flex items-center justify-center gap-2"
            >
              <Package className="w-5 h-5" />
              View My Orders
            </button>
            <button
              onClick={() => navigate('/')}
              className="w-full py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-semibold"
            >
              Continue Shopping
            </button>
          </div>

          <p className="mt-6 text-sm text-gray-500">
            You will receive an order confirmation email shortly.
            <br />Track your order anytime from My Account.
          </p>
        </div>
      </div>
    );
  }

  if (paymentStatus === 'success') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8 text-center">
          <div className="mb-6">
            <CheckCircle className="h-20 w-20 text-green-500 mx-auto mb-4" />
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Payment Successful!</h1>
            <p className="text-gray-600">Thank you for your purchase</p>
          </div>

          {orderDetails && (
            <div className="bg-gray-50 rounded-lg p-6 mb-6 text-left">
              <h3 className="font-semibold text-gray-900 mb-4">Order Details</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Order ID:</span>
                  <span className="font-semibold">{orderDetails.orderId}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Transaction ID:</span>
                  <span className="font-semibold">{orderDetails.transactionId}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Amount Paid:</span>
                  <span className="font-semibold text-green-600">
                    {formatCurrency(orderDetails.amount)}
                  </span>
                </div>
                {orderDetails.paymentMode && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Payment Method:</span>
                    <span className="font-semibold">{orderDetails.paymentMode}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="space-y-3">
            <button
              onClick={() => navigate('/')}
              className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
            >
              Continue Shopping
            </button>
            <button
              onClick={() => navigate('/orders')}
              className="w-full py-3 bg-white border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-semibold"
            >
              View My Orders
            </button>
          </div>

          <p className="mt-6 text-sm text-gray-500">
            A confirmation email has been sent to your registered email address
          </p>
        </div>
      </div>
    );
  }

  if (paymentStatus === 'failed') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8 text-center">
          <div className="mb-6">
            <XCircle className="h-20 w-20 text-red-500 mx-auto mb-4" />
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Payment Failed</h1>
            <p className="text-gray-600">Your payment could not be processed</p>
          </div>

          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-red-800">
              The payment transaction was not completed successfully. 
              Please try again or contact support if the issue persists.
            </p>
          </div>

          <div className="space-y-3">
            <button
              onClick={() => navigate('/checkout')}
              className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
            >
              Try Again
            </button>
            <button
              onClick={() => navigate('/')}
              className="w-full py-3 bg-white border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-semibold"
            >
              Back to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8 text-center">
        <div className="mb-6">
          <XCircle className="h-20 w-20 text-gray-400 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Something Went Wrong</h1>
          <p className="text-gray-600">We couldn't verify your payment</p>
        </div>

        <div className="space-y-3">
          <button
            onClick={() => navigate('/')}
            className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            Back to Home
          </button>
          <button
            onClick={() => window.location.reload()}
            className="w-full py-3 bg-white border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-semibold"
          >
            Retry Verification
          </button>
        </div>
      </div>
    </div>
  );
};

export default PaymentSuccess;
