import React, { useState, useEffect } from 'react';
import { 
  Link2, Unlink, Search, RefreshCw, Check, X, 
  Package, FileText, AlertCircle, ChevronDown, ChevronUp,
  Sparkles, Calendar, DollarSign, Building2
} from 'lucide-react';
import { BACKEND_URL } from '../config/api';

const GRNMatchingPanel = ({ onMatchComplete }) => {
  const [activeTab, setActiveTab] = useState('unmatched-grns');
  const [unmatchedGRNs, setUnmatchedGRNs] = useState([]);
  const [unmatchedBills, setUnmatchedBills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedGRN, setSelectedGRN] = useState(null);
  const [selectedBill, setSelectedBill] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [linking, setLinking] = useState(false);
  const [showAllGRNs, setShowAllGRNs] = useState(false);

  useEffect(() => {
    fetchUnmatchedData();
  }, [showAllGRNs]);

  const fetchUnmatchedData = async () => {
    setLoading(true);
    try {
      // Use all-grns endpoint if showAllGRNs is true
      const grnEndpoint = showAllGRNs 
        ? `${BACKEND_URL}/api/purchase-bills/grn-matching/all-grns`
        : `${BACKEND_URL}/api/purchase-bills/grn-matching/unmatched-grns`;
      
      const [grnsRes, billsRes] = await Promise.all([
        fetch(grnEndpoint),
        fetch(`${BACKEND_URL}/api/purchase-bills/grn-matching/unmatched-bills`)
      ]);
      
      const grnsData = await grnsRes.json();
      const billsData = await billsRes.json();
      
      console.log('GRNs response:', grnsData);
      console.log('Bills response:', billsData);
      
      if (grnsData.status === 'success') {
        setUnmatchedGRNs(grnsData.grns || []);
      }
      if (billsData.status === 'success') {
        setUnmatchedBills(billsData.bills || []);
      }
    } catch (error) {
      console.error('Error fetching unmatched data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSuggestions = async (billId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/purchase-bills/grn-matching/suggest/${billId}`);
      const data = await response.json();
      if (data.status === 'success') {
        setSuggestions(data.suggestions || []);
        setShowSuggestions(true);
      }
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    }
  };

  const handleLink = async (grnId, billId) => {
    setLinking(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/purchase-bills/grn-matching/link?grn_id=${grnId}&bill_id=${billId}`,
        { method: 'POST' }
      );
      const data = await response.json();
      
      if (data.status === 'success') {
        alert(`✓ Linked: GRN ${data.grn_number} ↔ Bill ${data.bill_number}`);
        fetchUnmatchedData();
        setSelectedGRN(null);
        setSelectedBill(null);
        setSuggestions([]);
        setShowSuggestions(false);
        if (onMatchComplete) onMatchComplete();
      } else {
        alert(data.detail || 'Failed to link');
      }
    } catch (error) {
      alert('Error linking GRN and Bill');
    } finally {
      setLinking(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border">
      {/* Header */}
      <div className="p-4 border-b bg-gradient-to-r from-indigo-50 to-purple-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-100 rounded-lg">
              <Link2 className="w-5 h-5 text-indigo-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-800">GRN ↔ Purchase Bill Matching</h2>
              <p className="text-sm text-gray-500">Link goods receipts with vendor invoices</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={async () => {
                try {
                  const res = await fetch(`${BACKEND_URL}/api/purchase-bills/grn-matching/debug`);
                  const data = await res.json();
                  console.log('GRN Debug Data:', data);
                  
                  const debugInfo = data.debug_data;
                  let message = `=== GRN Debug Info ===\n\n`;
                  message += `📦 GRN Collection Count: ${debugInfo?.grn_collection_count || 0}\n`;
                  message += `✅ Unmatched: ${debugInfo?.unmatched_grns || 0}\n\n`;
                  
                  // Show all collections in DB
                  message += `📁 ALL Collections in DB:\n`;
                  (debugInfo?.all_collections_in_db || []).forEach(c => {
                    message += `  • ${c}\n`;
                  });
                  
                  // Show which collections have GRN data
                  message += `\n🔍 Collections with GRN data:\n`;
                  const grnCollections = debugInfo?.collections_with_grn_data || {};
                  if (Object.keys(grnCollections).length === 0) {
                    message += `  ⚠️ None found!\n`;
                  } else {
                    Object.entries(grnCollections).forEach(([name, info]) => {
                      message += `  • ${name}: ${info.count} GRNs (sample: ${info.sample_grn_number})\n`;
                    });
                  }
                  
                  message += `\n🔍 Check browser console (F12) for full details.`;
                  
                  alert(message);
                } catch (e) {
                  console.error('Debug error:', e);
                  alert('Debug failed: ' + e.message);
                }
              }}
              className="px-3 py-1.5 text-xs bg-gray-100 text-gray-600 hover:bg-gray-200 rounded-lg"
              title="Debug GRN data"
            >
              Debug
            </button>
            <button
              onClick={fetchUnmatchedData}
              disabled={loading}
              className="p-2 text-gray-500 hover:bg-white rounded-lg transition-colors"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="flex gap-4 mt-4">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-100 text-amber-700 rounded-full text-sm">
            <Package className="w-4 h-4" />
            <span>{unmatchedGRNs.length} Unmatched GRNs</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-100 text-blue-700 rounded-full text-sm">
            <FileText className="w-4 h-4" />
            <span>{unmatchedBills.length} Unmatched Bills</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b">
        <button
          onClick={() => setActiveTab('unmatched-grns')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'unmatched-grns'
              ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50'
              : 'text-gray-500 hover:bg-gray-50'
          }`}
        >
          <Package className="w-4 h-4 inline mr-2" />
          Unmatched GRNs ({unmatchedGRNs.length})
        </button>
        <button
          onClick={() => setActiveTab('unmatched-bills')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'unmatched-bills'
              ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50'
              : 'text-gray-500 hover:bg-gray-50'
          }`}
        >
          <FileText className="w-4 h-4 inline mr-2" />
          Unmatched Bills ({unmatchedBills.length})
        </button>
        <button
          onClick={() => setActiveTab('manual-match')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'manual-match'
              ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50'
              : 'text-gray-500 hover:bg-gray-50'
          }`}
        >
          <Link2 className="w-4 h-4 inline mr-2" />
          Manual Match
        </button>
      </div>

      {/* Content */}
      <div className="p-4">
        {loading ? (
          <div className="py-8 text-center">
            <RefreshCw className="w-8 h-8 mx-auto text-gray-400 animate-spin" />
            <p className="text-gray-500 mt-2">Loading...</p>
          </div>
        ) : (
          <>
            {/* Unmatched GRNs Tab */}
            {activeTab === 'unmatched-grns' && (
              <div className="space-y-3">
                {/* Toggle to show all GRNs */}
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-600">
                    {showAllGRNs ? 'Showing ALL GRNs' : 'Showing only Unmatched GRNs'}
                  </span>
                  <button
                    onClick={() => setShowAllGRNs(!showAllGRNs)}
                    className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                      showAllGRNs 
                        ? 'bg-indigo-100 text-indigo-700' 
                        : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                    }`}
                  >
                    {showAllGRNs ? 'Show Unmatched Only' : 'Show All GRNs'}
                  </button>
                </div>
                
                {unmatchedGRNs.length === 0 ? (
                  <div className="py-8 text-center text-gray-500">
                    <Check className="w-12 h-12 mx-auto text-green-400 mb-2" />
                    <p>{showAllGRNs ? 'No GRNs found in the database' : 'All GRNs are matched!'}</p>
                    {!showAllGRNs && (
                      <button 
                        onClick={() => setShowAllGRNs(true)}
                        className="mt-2 text-indigo-600 underline text-sm"
                      >
                        Click to show all GRNs
                      </button>
                    )}
                  </div>
                ) : (
                  unmatchedGRNs.map((grn) => (
                    <div
                      key={grn.id}
                      className={`p-4 border rounded-lg hover:shadow-md transition-all cursor-pointer ${
                        selectedGRN?.id === grn.id ? 'border-indigo-500 bg-indigo-50' : 'hover:border-gray-300'
                      }`}
                      onClick={() => setSelectedGRN(selectedGRN?.id === grn.id ? null : grn)}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-indigo-600">{grn.grn_number}</span>
                            <span className="px-2 py-0.5 bg-amber-100 text-amber-700 text-xs rounded-full">
                              Unmatched
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">
                            <Building2 className="w-3 h-3 inline mr-1" />
                            {grn.vendor_name}
                          </p>
                          <div className="flex gap-4 mt-2 text-xs text-gray-500">
                            <span>
                              <Calendar className="w-3 h-3 inline mr-1" />
                              {formatDate(grn.created_at)}
                            </span>
                            <span>
                              <DollarSign className="w-3 h-3 inline mr-1" />
                              {formatCurrency(grn.total_value)}
                            </span>
                            {grn.vendor_invoice_number && (
                              <span className="text-purple-600 font-medium">
                                Invoice: {grn.vendor_invoice_number}
                              </span>
                            )}
                          </div>
                        </div>
                        <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${
                          selectedGRN?.id === grn.id ? 'rotate-180' : ''
                        }`} />
                      </div>

                      {/* Expanded view with matching options */}
                      {selectedGRN?.id === grn.id && (
                        <div className="mt-4 pt-4 border-t">
                          <p className="text-sm font-medium text-gray-700 mb-2">Select a Purchase Bill to match:</p>
                          {unmatchedBills.length === 0 ? (
                            <p className="text-sm text-gray-500">No unmatched bills available</p>
                          ) : (
                            <div className="grid gap-2 max-h-40 overflow-y-auto">
                              {unmatchedBills.map((bill) => (
                                <button
                                  key={bill.id}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleLink(grn.id, bill.id);
                                  }}
                                  disabled={linking}
                                  className="flex items-center justify-between p-2 bg-white border rounded hover:bg-green-50 hover:border-green-300 transition-colors text-left"
                                >
                                  <div>
                                    <span className="font-medium text-blue-600">{bill.bill_number}</span>
                                    <span className="text-sm text-gray-500 ml-2">
                                      {bill.vendor?.name} • {formatCurrency(bill.grand_total)}
                                    </span>
                                  </div>
                                  <Link2 className="w-4 h-4 text-green-600" />
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Unmatched Bills Tab */}
            {activeTab === 'unmatched-bills' && (
              <div className="space-y-3">
                {unmatchedBills.length === 0 ? (
                  <div className="py-8 text-center text-gray-500">
                    <Check className="w-12 h-12 mx-auto text-green-400 mb-2" />
                    <p>All Purchase Bills are matched!</p>
                  </div>
                ) : (
                  unmatchedBills.map((bill) => (
                    <div
                      key={bill.id}
                      className={`p-4 border rounded-lg hover:shadow-md transition-all cursor-pointer ${
                        selectedBill?.id === bill.id ? 'border-indigo-500 bg-indigo-50' : 'hover:border-gray-300'
                      }`}
                      onClick={() => {
                        setSelectedBill(selectedBill?.id === bill.id ? null : bill);
                        if (selectedBill?.id !== bill.id) {
                          fetchSuggestions(bill.id);
                        } else {
                          setShowSuggestions(false);
                        }
                      }}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-blue-600">{bill.bill_number}</span>
                            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
                              Unmatched
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">
                            <Building2 className="w-3 h-3 inline mr-1" />
                            {bill.vendor?.name}
                          </p>
                          <div className="flex gap-4 mt-2 text-xs text-gray-500">
                            <span>
                              <Calendar className="w-3 h-3 inline mr-1" />
                              {formatDate(bill.bill_date)}
                            </span>
                            <span>
                              <DollarSign className="w-3 h-3 inline mr-1" />
                              {formatCurrency(bill.grand_total)}
                            </span>
                            {bill.po_number && (
                              <span className="text-purple-600">PO: {bill.po_number}</span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              fetchSuggestions(bill.id);
                              setSelectedBill(bill);
                            }}
                            className="p-1.5 text-purple-600 hover:bg-purple-100 rounded-lg"
                            title="Get AI Suggestions"
                          >
                            <Sparkles className="w-4 h-4" />
                          </button>
                          <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${
                            selectedBill?.id === bill.id ? 'rotate-180' : ''
                          }`} />
                        </div>
                      </div>

                      {/* Expanded view with suggestions */}
                      {selectedBill?.id === bill.id && showSuggestions && (
                        <div className="mt-4 pt-4 border-t">
                          <div className="flex items-center gap-2 mb-2">
                            <Sparkles className="w-4 h-4 text-purple-500" />
                            <p className="text-sm font-medium text-gray-700">AI-Suggested GRN Matches:</p>
                          </div>
                          
                          {suggestions.length === 0 ? (
                            <p className="text-sm text-gray-500">No matching GRNs found</p>
                          ) : (
                            <div className="space-y-2">
                              {suggestions.map((grn) => (
                                <div
                                  key={grn.id}
                                  className="flex items-center justify-between p-3 bg-white border rounded-lg hover:border-green-300 transition-colors"
                                >
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2">
                                      <span className="font-medium text-indigo-600">{grn.grn_number}</span>
                                      <span className={`px-2 py-0.5 text-xs rounded-full ${
                                        grn.match_score >= 70 ? 'bg-green-100 text-green-700' :
                                        grn.match_score >= 40 ? 'bg-yellow-100 text-yellow-700' :
                                        'bg-gray-100 text-gray-600'
                                      }`}>
                                        {grn.match_score}% match
                                      </span>
                                    </div>
                                    <p className="text-xs text-gray-500 mt-1">
                                      {grn.vendor_name} • {formatCurrency(grn.total_value)} • {formatDate(grn.created_at)}
                                    </p>
                                    {grn.match_reasons?.length > 0 && (
                                      <div className="flex flex-wrap gap-1 mt-1">
                                        {grn.match_reasons.map((reason, idx) => (
                                          <span key={idx} className="text-xs bg-purple-50 text-purple-600 px-1.5 py-0.5 rounded">
                                            {reason}
                                          </span>
                                        ))}
                                      </div>
                                    )}
                                  </div>
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleLink(grn.id, bill.id);
                                    }}
                                    disabled={linking}
                                    className="ml-3 px-3 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors flex items-center gap-1"
                                  >
                                    <Link2 className="w-4 h-4" />
                                    Link
                                  </button>
                                </div>
                              ))}
                            </div>
                          )}

                          {/* Manual selection */}
                          <div className="mt-4 pt-3 border-t">
                            <p className="text-sm font-medium text-gray-700 mb-2">Or select manually:</p>
                            <div className="grid gap-2 max-h-32 overflow-y-auto">
                              {unmatchedGRNs.filter(g => !suggestions.find(s => s.id === g.id)).map((grn) => (
                                <button
                                  key={grn.id}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleLink(grn.id, bill.id);
                                  }}
                                  disabled={linking}
                                  className="flex items-center justify-between p-2 bg-gray-50 border rounded hover:bg-green-50 hover:border-green-300 transition-colors text-left text-sm"
                                >
                                  <span>
                                    <span className="font-medium text-indigo-600">{grn.grn_number}</span>
                                    <span className="text-gray-500 ml-2">
                                      {grn.vendor_name} • {formatCurrency(grn.total_value)}
                                    </span>
                                  </span>
                                  <Link2 className="w-4 h-4 text-gray-400" />
                                </button>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Manual Match Tab */}
            {activeTab === 'manual-match' && (
              <div className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  {/* GRN Selection */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                      <Package className="w-4 h-4" />
                      Select GRN
                    </h3>
                    <div className="border rounded-lg max-h-64 overflow-y-auto">
                      {unmatchedGRNs.length === 0 ? (
                        <p className="p-4 text-center text-gray-500 text-sm">No unmatched GRNs</p>
                      ) : (
                        unmatchedGRNs.map((grn) => (
                          <div
                            key={grn.id}
                            onClick={() => setSelectedGRN(grn)}
                            className={`p-3 border-b last:border-b-0 cursor-pointer transition-colors ${
                              selectedGRN?.id === grn.id
                                ? 'bg-indigo-50 border-l-4 border-l-indigo-500'
                                : 'hover:bg-gray-50'
                            }`}
                          >
                            <p className="font-medium text-indigo-600">{grn.grn_number}</p>
                            <p className="text-xs text-gray-500">{grn.vendor_name}</p>
                            <p className="text-xs text-gray-400">{formatCurrency(grn.total_value)}</p>
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  {/* Bill Selection */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      Select Purchase Bill
                    </h3>
                    <div className="border rounded-lg max-h-64 overflow-y-auto">
                      {unmatchedBills.length === 0 ? (
                        <p className="p-4 text-center text-gray-500 text-sm">No unmatched bills</p>
                      ) : (
                        unmatchedBills.map((bill) => (
                          <div
                            key={bill.id}
                            onClick={() => setSelectedBill(bill)}
                            className={`p-3 border-b last:border-b-0 cursor-pointer transition-colors ${
                              selectedBill?.id === bill.id
                                ? 'bg-blue-50 border-l-4 border-l-blue-500'
                                : 'hover:bg-gray-50'
                            }`}
                          >
                            <p className="font-medium text-blue-600">{bill.bill_number}</p>
                            <p className="text-xs text-gray-500">{bill.vendor?.name}</p>
                            <p className="text-xs text-gray-400">{formatCurrency(bill.grand_total)}</p>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>

                {/* Match Button */}
                {selectedGRN && selectedBill && (
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="text-center">
                          <p className="text-xs text-gray-500">GRN</p>
                          <p className="font-semibold text-indigo-600">{selectedGRN.grn_number}</p>
                        </div>
                        <Link2 className="w-6 h-6 text-green-600" />
                        <div className="text-center">
                          <p className="text-xs text-gray-500">Bill</p>
                          <p className="font-semibold text-blue-600">{selectedBill.bill_number}</p>
                        </div>
                      </div>
                      <button
                        onClick={() => handleLink(selectedGRN.id, selectedBill.id)}
                        disabled={linking}
                        className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2 disabled:opacity-50"
                      >
                        {linking ? (
                          <>
                            <RefreshCw className="w-4 h-4 animate-spin" />
                            Linking...
                          </>
                        ) : (
                          <>
                            <Check className="w-4 h-4" />
                            Confirm Match
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default GRNMatchingPanel;
