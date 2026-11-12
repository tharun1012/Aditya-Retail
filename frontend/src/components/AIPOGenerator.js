import React, { useState } from 'react';
import { BACKEND_URL } from '../config/api';
import { Sparkles, AlertCircle, CheckCircle, Loader, X } from 'lucide-react';
import { showToast, successMessages, errorMessages } from '../utils/toast';


const AIPOGenerator = ({ isOpen, onClose, onPOGenerated }) => {
  const [request, setRequest] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    if (!request.trim()) {
      showToast.error('Please enter a request');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${BACKEND_URL}/api/ai-po-generator/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          request: request,
          user_email: 'admin@adityaretail.com'
        }),
      });

      const data = await response.json();

      if (data.status === 'success') {
        setResult(data);
        showToast.success(successMessages.purchaseOrder.create(data.draft_number));
      } else {
        setError(data.message || 'Failed to generate PO');
        showToast.error(data.message || 'Failed to generate PO');
      }
    } catch (err) {
      console.error('AI PO Generator error:', err);
      setError('Network error. Please try again.');
      showToast.error(errorMessages.purchaseOrder.create);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setRequest('');
    setResult(null);
    setError(null);
    onClose();
  };

  const handleApproveDraft = () => {
    if (result) {
      onPOGenerated();
      handleClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-purple-600 to-indigo-600">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-white rounded-lg">
              <Sparkles className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">AI Purchase Order Generator</h2>
              <p className="text-sm text-purple-100 mt-1">Generate draft POs from natural language</p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
          >
            <X className="h-5 w-5 text-white" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Input Section */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              What would you like to purchase?
            </label>
            <textarea
              value={request}
              onChange={(e) => setRequest(e.target.value)}
              placeholder="Example: Create PO for 10 Bosch washing machines model WAJ2846IIN"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              rows="4"
              disabled={loading}
            />
            <div className="mt-2 text-xs text-gray-500">
              <p className="font-semibold mb-1">💡 Example requests:</p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>Create PO for 5 Samsung refrigerators</li>
                <li>Need 10 Bosch washing machines model WAJ2846IIN</li>
                <li>Purchase 3 Siemens ovens from Vendor ABC with urgent delivery</li>
              </ul>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={loading || !request.trim()}
            className={`w-full py-3 px-4 rounded-lg font-medium flex items-center justify-center space-x-2 transition-colors ${
              loading || !request.trim()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700'
            }`}
          >
            {loading ? (
              <>
                <Loader className="h-5 w-5 animate-spin" />
                <span>Generating PO...</span>
              </>
            ) : (
              <>
                <Sparkles className="h-5 w-5" />
                <span>Generate Draft PO</span>
              </>
            )}
          </button>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-900">Error</p>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Success Result */}
          {result && (
            <div className="border border-green-200 rounded-lg overflow-hidden">
              {/* Success Header */}
              <div className="bg-green-50 p-4 flex items-center space-x-3">
                <CheckCircle className="h-6 w-6 text-green-600" />
                <div>
                  <p className="text-sm font-medium text-green-900">Draft PO Created Successfully!</p>
                  <p className="text-xs text-green-700 mt-1">Draft Number: {result.draft_number}</p>
                </div>
              </div>

              {/* Matched Product */}
              <div className="p-4 bg-white border-t border-gray-200">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">Matched Product</h3>
                <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Product Name:</span>
                    <span className="text-sm font-medium text-gray-900">{result.matched_product.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Brand:</span>
                    <span className="text-sm font-medium text-gray-900">{result.matched_product.brand}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Model:</span>
                    <span className="text-sm font-medium text-gray-900">{result.matched_product.model_number || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Price:</span>
                    <span className="text-sm font-medium text-gray-900">₹{result.matched_product.price?.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* Draft Details */}
              <div className="p-4 bg-white border-t border-gray-200">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">Draft PO Summary</h3>
                <div className="space-y-3">
                  <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Quantity:</span>
                      <span className="text-sm font-medium text-gray-900">{result.draft_po.items[0].quantity} units</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Rate per unit:</span>
                      <span className="text-sm font-medium text-gray-900">₹{result.draft_po.items[0].rate?.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Tax Rate:</span>
                      <span className="text-sm font-medium text-gray-900">{result.draft_po.items[0].tax_rate}%</span>
                    </div>
                    <div className="flex justify-between border-t border-gray-200 pt-2 mt-2">
                      <span className="text-sm font-semibold text-gray-900">Total Amount:</span>
                      <span className="text-lg font-bold text-green-600">₹{result.draft_po.total_amount?.toLocaleString()}</span>
                    </div>
                  </div>

                  <div className="bg-blue-50 rounded-lg p-3">
                    <p className="text-xs text-blue-800">
                      <span className="font-semibold">Note:</span> {result.draft_po.notes}
                    </p>
                  </div>

                  {result.draft_po.vendor.name !== 'TO BE DECIDED' && (
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs text-gray-700">
                        <span className="font-semibold">Vendor:</span> {result.draft_po.vendor.name}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Alternative Products */}
              {result.alternative_products && result.alternative_products.length > 0 && (
                <div className="p-4 bg-gray-50 border-t border-gray-200">
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">Alternative Products Found</h3>
                  <div className="space-y-2">
                    {result.alternative_products.map((product, index) => (
                      <div key={index} className="bg-white rounded-lg p-3 border border-gray-200">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{product.name}</p>
                            <p className="text-xs text-gray-600 mt-1">{product.brand} • {product.model_number}</p>
                          </div>
                          <span className="text-sm font-semibold text-gray-900">₹{product.price?.toLocaleString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200 bg-gray-50">
          <button
            onClick={handleClose}
            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
          >
            Close
          </button>
          {result && (
            <button
              onClick={handleApproveDraft}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
            >
              View Draft in Purchase Management
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIPOGenerator;
