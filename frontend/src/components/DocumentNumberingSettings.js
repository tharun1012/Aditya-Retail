import React, { useState, useEffect } from 'react';
import { BACKEND_URL as API_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { 
  Hash, Store, ArrowLeft, Save, RefreshCw, Info, Eye
} from 'lucide-react';
import { showToast } from '../utils/toast';

const DocumentNumberingSettings = () => {
  const navigate = useNavigate();
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState('');
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState({});
  const [editValues, setEditValues] = useState({});
  const [previews, setPreviews] = useState({});

  useEffect(() => {
    fetchStores();
  }, []);

  useEffect(() => {
    if (selectedStore) {
      fetchConfig(selectedStore);
    }
  }, [selectedStore]);

  const fetchStores = async () => {
    try {
      const response = await fetch(`${API_URL}/api/stores/`);
      if (response.ok) {
        const data = await response.json();
        setStores(data.stores || []);
        if (data.stores?.length > 0) {
          setSelectedStore(data.stores[0].id);
        }
      }
    } catch (error) {
      console.error('Error fetching stores:', error);
    }
  };

  const fetchConfig = async (storeId) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/document-numbering/config?store_id=${storeId}`);
      if (response.ok) {
        const data = await response.json();
        setConfig(data.config);
        initializeEditValues(data.config?.document_configs || {});
        fetchAllPreviews(storeId, data.config?.document_configs || {});
      } else if (response.status === 404) {
        const initResponse = await fetch(`${API_URL}/api/document-numbering/initialize/${storeId}`, {
          method: 'POST'
        });
        if (initResponse.ok) {
          const initData = await initResponse.json();
          setConfig(initData.config);
          initializeEditValues(initData.config?.document_configs || {});
          fetchAllPreviews(storeId, initData.config?.document_configs || {});
        }
      }
    } catch (error) {
      console.error('Error fetching config:', error);
      showToast.error('Failed to load configuration');
    } finally {
      setLoading(false);
    }
  };

  const initializeEditValues = (docConfigs) => {
    const values = {};
    const storeCode = stores.find(s => s.id === selectedStore)?.code || 'STORE';
    
    Object.entries(docConfigs).forEach(([docType, docConfig]) => {
      // If custom format exists, use it; otherwise create a suggested format
      let format = docConfig.custom_format || '';
      
      if (!format) {
        // Create suggested format based on doc type
        if (docType === 'invoice') {
          format = `{STORE}{SEQ:4}/{FY}`;
        } else if (docType === 'sales_order') {
          format = `{STORE}SO{SEQ:4}/{FY}`;
        } else if (docType === 'quotation') {
          format = `{STORE}QT{SEQ:4}/{FY}`;
        } else if (docType === 'purchase_order') {
          format = `{STORE}PO{SEQ:4}/{FY}`;
        } else if (docType === 'voucher') {
          format = `{STORE}VCH{SEQ:4}/{FY}`;
        } else if (docType === 'delivery_challan') {
          format = `{STORE}DC{SEQ:4}/{FY}`;
        } else {
          format = `{STORE}{PREFIX}{SEQ:4}/{FY}`;
        }
      }
      
      values[docType] = {
        customFormat: format,
        nextNumber: docConfig.current_number || 1
      };
    });
    setEditValues(values);
  };

  const fetchAllPreviews = async (storeId, docConfigs) => {
    const newPreviews = {};
    for (const docType of Object.keys(docConfigs)) {
      try {
        const response = await fetch(`${API_URL}/api/document-numbering/preview/${storeId}/${docType}`);
        if (response.ok) {
          const data = await response.json();
          newPreviews[docType] = data.preview;
        }
      } catch (error) {
        console.error(`Error fetching preview for ${docType}:`, error);
      }
    }
    setPreviews(newPreviews);
  };

  const handleFormatChange = (docType, field, value) => {
    setEditValues(prev => ({
      ...prev,
      [docType]: {
        ...prev[docType],
        [field]: value
      }
    }));
  };

  const getPreviewFromFormat = (format) => {
    const storeCode = stores.find(s => s.id === selectedStore)?.code || 'ARM';
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;
    
    // Calculate FY
    let fyStart, fyEnd;
    if (month >= 4) {
      fyStart = String(year).slice(-2);
      fyEnd = String(year + 1).slice(-2);
    } else {
      fyStart = String(year - 1).slice(-2);
      fyEnd = String(year).slice(-2);
    }
    
    let result = format;
    result = result.replace(/\{STORE_CODE\}/gi, storeCode);
    result = result.replace(/\{STORE\}/gi, storeCode);
    result = result.replace(/\{PREFIX\}/gi, 'INV');
    result = result.replace(/\{YYYY\}/gi, String(year));
    result = result.replace(/\{YEAR\}/gi, String(year));
    result = result.replace(/\{YY\}/gi, String(year).slice(-2));
    result = result.replace(/\{FY\}/gi, `${fyStart}-${fyEnd}`);
    result = result.replace(/\{MM\}/gi, String(month).padStart(2, '0'));
    result = result.replace(/\{DD\}/gi, String(now.getDate()).padStart(2, '0'));
    
    // Handle sequence
    const seqMatch = result.match(/\{SEQ:(\d+)\}/i);
    if (seqMatch) {
      const padding = parseInt(seqMatch[1]);
      result = result.replace(/\{SEQ:\d+\}/gi, '1'.padStart(padding, '0'));
    } else {
      result = result.replace(/\{SEQ\}/gi, '0001');
    }
    
    // Handle {####} style
    const hashMatch = result.match(/\{(#+)\}/);
    if (hashMatch) {
      const padding = hashMatch[1].length;
      result = result.replace(/\{#+\}/, '1'.padStart(padding, '0'));
    }
    
    return result;
  };

  const saveFormat = async (docType) => {
    const editValue = editValues[docType];
    if (!editValue?.customFormat) {
      showToast.error('Please enter a format');
      return;
    }
    
    setSaving(prev => ({ ...prev, [docType]: true }));
    
    try {
      const response = await fetch(`${API_URL}/api/document-numbering/format`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_type: docType,
          store_id: selectedStore,
          custom_format: editValue.customFormat,
          use_custom_format: true,
          starting_number: editValue.nextNumber || 1
        })
      });

      if (response.ok) {
        const data = await response.json();
        showToast.success(`Format saved! Next: ${data.preview}`);
        setPreviews(prev => ({ ...prev, [docType]: data.preview }));
        fetchConfig(selectedStore);
      } else {
        const error = await response.json();
        showToast.error(error.detail || 'Failed to update');
      }
    } catch (error) {
      showToast.error('Failed to save format');
    } finally {
      setSaving(prev => ({ ...prev, [docType]: false }));
    }
  };

  const selectedStoreCode = stores.find(s => s.id === selectedStore)?.code || 'STORE';

  const documentTypeLabels = {
    invoice: { label: 'Invoice / SO to Invoice', icon: '🧾', color: 'bg-blue-50 border-blue-200', example: `${selectedStoreCode}0001/26-27` },
    sales_order: { label: 'Sales Order', icon: '📋', color: 'bg-green-50 border-green-200', example: `${selectedStoreCode}SO0001/26-27` },
    quotation: { label: 'Quotation', icon: '📝', color: 'bg-purple-50 border-purple-200', example: `${selectedStoreCode}QT0001/26-27` },
    purchase_order: { label: 'Purchase Order', icon: '🛒', color: 'bg-orange-50 border-orange-200', example: `${selectedStoreCode}PO0001/26-27` },
    voucher: { label: 'Payment Voucher', icon: '💰', color: 'bg-yellow-50 border-yellow-200', example: `${selectedStoreCode}VCH0001/26-27` },
    delivery_challan: { label: 'Delivery Challan', icon: '🚚', color: 'bg-teal-50 border-teal-200', example: `${selectedStoreCode}DC0001/26-27` },
    credit_note: { label: 'Credit Note', icon: '📉', color: 'bg-red-50 border-red-200', example: `${selectedStoreCode}CN0001/26-27` },
    debit_note: { label: 'Debit Note', icon: '📈', color: 'bg-pink-50 border-pink-200', example: `${selectedStoreCode}DN0001/26-27` }
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-4xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center px-4 py-2 mb-6 text-gray-700 bg-white hover:bg-gray-100 rounded-lg transition-all border border-gray-300 shadow-sm"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          <span className="font-medium">Back</span>
        </button>

        {/* Header */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-amber-100 rounded-xl">
              <Hash className="w-6 h-6 text-amber-700" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Document Numbering</h1>
              <p className="text-gray-600 text-sm">Set custom number formats for each document type</p>
            </div>
          </div>
        </div>

        {/* Store Selector */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
          <div className="flex items-center space-x-4">
            <Store className="w-5 h-5 text-gray-500" />
            <select
              value={selectedStore}
              onChange={(e) => setSelectedStore(e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
            >
              {stores.map(store => (
                <option key={store.id} value={store.id}>
                  {store.name} ({store.code})
                </option>
              ))}
            </select>
            <button
              onClick={() => fetchConfig(selectedStore)}
              className="p-2 text-gray-500 hover:text-amber-600 hover:bg-amber-50 rounded-lg"
              title="Refresh"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Help Box - Your Format */}
        <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl p-5 mb-6">
          <div className="flex items-start gap-3">
            <Info className="w-6 h-6 text-amber-600 mt-0.5" />
            <div className="text-sm">
              <p className="font-semibold text-amber-800 text-base mb-2">Your Format: {selectedStoreCode}0001/26-27</p>
              <p className="text-amber-700 mb-3">Use these placeholders to create your format:</p>
              
              <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-amber-800">
                <div><code className="bg-amber-100 px-1.5 py-0.5 rounded font-mono text-xs">{'{STORE}'}</code> → {selectedStoreCode}</div>
                <div><code className="bg-amber-100 px-1.5 py-0.5 rounded font-mono text-xs">{'{SEQ:4}'}</code> → 0001 (4 digits)</div>
                <div><code className="bg-amber-100 px-1.5 py-0.5 rounded font-mono text-xs">{'{FY}'}</code> → 26-27</div>
                <div><code className="bg-amber-100 px-1.5 py-0.5 rounded font-mono text-xs">{'{SEQ:6}'}</code> → 000001 (6 digits)</div>
                <div><code className="bg-amber-100 px-1.5 py-0.5 rounded font-mono text-xs">{'{YY}'}</code> → 26</div>
                <div><code className="bg-amber-100 px-1.5 py-0.5 rounded font-mono text-xs">{'{YYYY}'}</code> → 2026</div>
              </div>
              
              <div className="mt-4 pt-3 border-t border-amber-200">
                <p className="font-medium text-amber-800 mb-1">Examples for {selectedStoreCode}:</p>
                <div className="space-y-1 text-amber-700">
                  <div>Invoice: <code className="bg-white px-2 py-0.5 rounded font-mono text-xs">{'{STORE}{SEQ:4}/{FY}'}</code> → <span className="font-semibold">{selectedStoreCode}0001/26-27</span></div>
                  <div>Sales Order: <code className="bg-white px-2 py-0.5 rounded font-mono text-xs">{'{STORE}SO{SEQ:4}/{FY}'}</code> → <span className="font-semibold">{selectedStoreCode}SO0001/26-27</span></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Document Types */}
        {loading ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <RefreshCw className="w-8 h-8 text-amber-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Loading configuration...</p>
          </div>
        ) : config ? (
          <div className="space-y-4">
            {Object.entries(config.document_configs || {}).map(([docType, docConfig]) => {
              const typeInfo = documentTypeLabels[docType] || { label: docType, icon: '📄', color: 'bg-gray-50 border-gray-200', example: 'DOC0001' };
              const editValue = editValues[docType] || { customFormat: '', nextNumber: 1 };
              const isSaving = saving[docType];
              const livePreview = getPreviewFromFormat(editValue.customFormat || '');

              return (
                <div key={docType} className={`bg-white rounded-xl shadow-sm border-2 ${typeInfo.color} overflow-hidden`}>
                  <div className="p-5">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{typeInfo.icon}</span>
                        <div>
                          <h3 className="font-semibold text-gray-900 text-lg">{typeInfo.label}</h3>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-gray-500">Current:</span>
                            <span className="font-mono bg-amber-100 text-amber-800 px-2 py-0.5 rounded text-sm font-semibold">
                              {previews[docType] || '...'}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Format Input */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Format Template
                        </label>
                        <input
                          type="text"
                          value={editValue.customFormat}
                          onChange={(e) => handleFormatChange(docType, 'customFormat', e.target.value.toUpperCase())}
                          className="w-full px-3 py-2.5 border-2 border-gray-200 rounded-lg font-mono text-sm focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                          placeholder={`{STORE}${docType === 'sales_order' ? 'SO' : ''}{SEQ:4}/{FY}`}
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Next #
                        </label>
                        <input
                          type="number"
                          min="1"
                          value={editValue.nextNumber}
                          onChange={(e) => handleFormatChange(docType, 'nextNumber', parseInt(e.target.value) || 1)}
                          className="w-full px-3 py-2.5 border-2 border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                        />
                      </div>
                      <div>
                        <button
                          onClick={() => saveFormat(docType)}
                          disabled={isSaving}
                          className="w-full px-4 py-2.5 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50 flex items-center justify-center gap-2 text-sm font-semibold"
                        >
                          {isSaving ? (
                            <RefreshCw className="w-4 h-4 animate-spin" />
                          ) : (
                            <Save className="w-4 h-4" />
                          )}
                          Save
                        </button>
                      </div>
                    </div>

                    {/* Live Preview */}
                    {editValue.customFormat && (
                      <div className="mt-3 flex items-center gap-2 text-sm">
                        <Eye className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-500">Preview:</span>
                        <span className="font-mono font-semibold text-green-700 bg-green-50 px-2 py-0.5 rounded">
                          {livePreview}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <p className="text-gray-600">Select a store to configure document numbering.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentNumberingSettings;
