import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import OfflineInvoiceCreation from './OfflineInvoiceCreation';

/**
 * Wrapper component for store users to create invoices/sales orders
 * Uses the same OfflineInvoiceCreation component as admin, but with store locked
 */
const StoreInvoiceCreation = ({ forcedDocumentType = null }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [storeId, setStoreId] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Get pre-filled data from navigation state (e.g., from Customer PO)
  const prefilledData = location.state || null;

  useEffect(() => {
    // Get store data from localStorage (set during store login)
    const storeData = localStorage.getItem('storeData');
    
    if (!storeData) {
      // Not logged in as store user, redirect to store login
      navigate('/store/login');
      return;
    }
    
    try {
      const store = JSON.parse(storeData);
      // Use store code for matching (works with both static config and dynamic stores)
      setStoreId(store.code || store.id);
    } catch (e) {
      console.error('Error parsing store data:', e);
      navigate('/store/login');
    }
    
    setLoading(false);
  }, [navigate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header with back button */}
      <div className="bg-white shadow-sm border-b px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center gap-4">
          <button
            onClick={() => navigate('/store/dashboard')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-800"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Dashboard</span>
          </button>
          <h1 className="text-xl font-semibold text-gray-800">
            {prefilledData?.fromCustomerPO
              ? `Create from Customer PO: ${prefilledData.customerPONumber}`
              : forcedDocumentType === 'invoice'
                ? 'Create Invoice'
                : forcedDocumentType === 'sales_order'
                  ? 'Create Sales Order'
                  : 'Create Invoice / Sales Order'}
          </h1>
        </div>
      </div>
      
      {/* Use the same OfflineInvoiceCreation component with store locked */}
      <OfflineInvoiceCreation 
        storeId={storeId} 
        storeOnly={true} 
        prefilledData={prefilledData}
        forcedDocumentType={forcedDocumentType}
      />
    </div>
  );
};

export default StoreInvoiceCreation;
