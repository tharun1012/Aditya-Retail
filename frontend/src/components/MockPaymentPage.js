import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CreditCard, CheckCircle } from 'lucide-react';

const MockPaymentPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [processing, setProcessing] = useState(false);
  
  const txnId = searchParams.get('txn_id');
  const amount = searchParams.get('amount');

  const handlePayment = async (success = true) => {
    setProcessing(true);
    
    // Simulate payment processing
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    if (success) {
      // Redirect to success page
      navigate('/payment-success');
    } else {
      // Redirect back to checkout with error
      navigate('/checkout?error=payment_failed');
    }
  };

  const formatAmount = (paise) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2
    }).format(paise / 100);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-blue-100 mb-4">
            <CreditCard className="h-10 w-10 text-blue-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Mock Payment Gateway</h1>
          <p className="text-gray-600">Testing Payment Flow - No Real Money</p>
        </div>

        <div className="bg-gray-50 rounded-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <span className="text-gray-600">Transaction ID:</span>
            <span className="font-mono text-sm text-gray-900">{txnId}</span>
          </div>
          <div className="flex justify-between items-center border-t pt-4">
            <span className="text-xl font-semibold text-gray-900">Amount to Pay:</span>
            <span className="text-3xl font-bold text-blue-600">{formatAmount(amount)}</span>
          </div>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-yellow-800">
            <strong>⚠️ Test Mode:</strong> This is a mock payment for testing. No actual payment will be processed.
          </p>
        </div>

        {!processing ? (
          <div className="space-y-3">
            <button
              onClick={() => handlePayment(true)}
              className="w-full py-4 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-semibold text-lg flex items-center justify-center gap-2"
            >
              <CheckCircle className="h-6 w-6" />
              Simulate Successful Payment
            </button>
            
            <button
              onClick={() => handlePayment(false)}
              className="w-full py-4 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-semibold text-lg"
            >
              Simulate Failed Payment
            </button>
            
            <button
              onClick={() => navigate('/checkout')}
              className="w-full py-3 bg-white border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-semibold"
            >
              Cancel & Go Back
            </button>
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600 font-medium">Processing payment...</p>
          </div>
        )}

        <div className="mt-6 text-center text-xs text-gray-500">
          <p>Once PhonePe test account is activated,</p>
          <p>this will be replaced with real PhonePe payment gateway</p>
        </div>
      </div>
    </div>
  );
};

export default MockPaymentPage;
