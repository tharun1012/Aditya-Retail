import React, { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Upload, FileSpreadsheet, Download, CheckCircle, XCircle, 
  AlertCircle, RefreshCw, Trash2, Database, ShoppingCart,
  Users, Package, FileText, Scan, Camera, Save, Eye, BookOpen, X,
  Receipt, CreditCard, Banknote, ArrowLeftRight
} from 'lucide-react';


const TallyImport = () => {
  const [activeTab, setActiveTab] = useState('sales');
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [importHistory, setImportHistory] = useState(null);
  const [updateExisting, setUpdateExisting] = useState(false);
  
  // AI Scanner states
  const [scanning, setScanning] = useState(false);
  const [scannedData, setScannedData] = useState(null);
  const [saving, setSaving] = useState(false);
  const [clearBeforeImport, setClearBeforeImport] = useState(false);
  
  // Day Book Import states
  const [daybookFile, setDaybookFile] = useState(null);
  const [daybookPreview, setDaybookPreview] = useState(null);
  const [daybookResult, setDaybookResult] = useState(null);
  const [daybookLoading, setDaybookLoading] = useState(false);
  const [skipUnclassified, setSkipUnclassified] = useState(false);
  const [daybookHistory, setDaybookHistory] = useState([]);
  const [showDaybookHistory, setShowDaybookHistory] = useState(false);
  
  // Day Book Entries Manager states
  const [importSummary, setImportSummary] = useState(null);
  const [unclassifiedEntries, setUnclassifiedEntries] = useState([]);
  const [entriesLoading, setEntriesLoading] = useState(false);
  const [classifyingAll, setClassifyingAll] = useState(false);
  const [selectedCollection, setSelectedCollection] = useState(null);
  const [collectionEntries, setCollectionEntries] = useState([]);
  
  // Opening Balance states
  const [obFile, setObFile] = useState(null);
  const [obFinancialYear, setObFinancialYear] = useState('2025-26');
  const [obAsOnDate, setObAsOnDate] = useState('2025-04-01');
  const [obLoading, setObLoading] = useState(false);
  const [obResult, setObResult] = useState(null);
  const [balanceSheet, setBalanceSheet] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);

  const tabs = [
    { id: 'sales', label: 'Sales/Invoices', icon: ShoppingCart, color: 'green', tallyType: 'sales' },
    { id: 'purchases', label: 'Purchases', icon: FileText, color: 'blue', tallyType: 'purchases' },
    { id: 'expenses', label: 'Expenses', icon: Receipt, color: 'orange', tallyType: 'expenses' },
    { id: 'payments', label: 'Payments', icon: CreditCard, color: 'red', tallyType: 'payments' },
    { id: 'receipts', label: 'Receipts', icon: Banknote, color: 'emerald', tallyType: 'receipts' },
    { id: 'credit-notes', label: 'Credit Notes (CN)', icon: FileText, color: 'purple', tallyType: 'credit_notes' },
    { id: 'debit-notes', label: 'Debit Notes (DN)', icon: FileText, color: 'pink', tallyType: 'debit_notes' },
    { id: 'journals', label: 'Journal Entries', icon: BookOpen, color: 'indigo', tallyType: 'journals' },
    { id: 'contra', label: 'Contra Entries', icon: ArrowLeftRight, color: 'teal', tallyType: 'contra' },
    { id: 'opening-balance', label: 'Opening Balances', icon: Database, color: 'amber', isOpeningBalance: true },
    { id: 'view-entries', label: 'View Imported Entries', icon: Eye, color: 'gray', isEntriesManager: true },
  ];

  useEffect(() => {
    fetchImportHistory();
  }, []);

  const fetchImportHistory = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/tally-import/history`);
      const data = await response.json();
      if (data.status === 'success') {
        setImportHistory(data.import_summary);
      }
    } catch (error) {
      console.error('Error fetching import history:', error);
    }
  };

  const downloadTemplate = async (type) => {
    try {
      // Use new tally-voucher endpoint for voucher types, old endpoint for others
      const currentTab = tabs.find(t => t.id === type);
      let endpoint;
      if (currentTab?.tallyType) {
        endpoint = `tally-voucher/template/${currentTab.tallyType}`;
      } else {
        endpoint = `tally-import/templates/${type}`;
      }
      
      const response = await fetch(`${BACKEND_URL}/api/${endpoint}`);
      if (!response.ok) {
        throw new Error('Template not found');
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${type}_import_template.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading template:', error);
      alert('Failed to download template. Please try again.');
    }
  };

  const downloadExcelTemplate = async (templateType) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/tally-import/templates/download/${templateType}`);
      if (!response.ok) {
        throw new Error('Failed to download template');
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${templateType}_template.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading Excel template:', error);
      alert('Failed to download Excel template. Please try again.');
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('update_existing', updateExisting);
    
    setUploading(true);
    setResult(null);

    try {
      const currentTab = tabs.find(t => t.id === activeTab);
      
      // Use new tally-voucher endpoint for voucher types
      let endpoint;
      if (currentTab?.tallyType) {
        endpoint = `tally-voucher/import/${currentTab.tallyType}`;
      } else if (currentTab?.endpoint) {
        endpoint = currentTab.endpoint;
      } else {
        endpoint = `tally-import/${activeTab}`;
      }
      
      const response = await fetch(`${BACKEND_URL}/api/${endpoint}`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      setResult(data);
      fetchImportHistory();
      
    } catch (error) {
      setResult({
        status: 'error',
        message: `Upload failed: ${error.message}`,
        result: { total_rows: 0, imported: 0, skipped: 0, errors: [error.message] }
      });
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  };

  const clearImportedData = async (type) => {
    if (!window.confirm(`Are you sure you want to delete all ${type} data imported from Tally? This cannot be undone.`)) {
      return;
    }

    try {
      // Use new tally-voucher clear endpoint
      const currentTab = tabs.find(t => t.id === activeTab);
      let endpoint;
      if (currentTab?.tallyType) {
        endpoint = `tally-voucher/clear/${currentTab.tallyType}`;
      } else {
        endpoint = `tally-import/clear/${type}`;
      }
      
      const response = await fetch(`${BACKEND_URL}/api/${endpoint}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      alert(data.message);
      fetchImportHistory();
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  };

  // AI Scanner functions
  const handleScanInvoice = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setScanning(true);
    setScannedData(null);
    setResult(null);

    try {
      const response = await fetch(`${BACKEND_URL}/api/tally-import/scan-sales-invoice`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        setScannedData(data.extracted_data);
        setResult({
          status: 'success',
          message: 'Invoice scanned successfully! Review the extracted data below.'
        });
      } else {
        setResult({
          status: 'error',
          message: data.message || 'Failed to scan invoice'
        });
      }
    } catch (error) {
      setResult({
        status: 'error',
        message: `Scan failed: ${error.message}`
      });
    } finally {
      setScanning(false);
      event.target.value = '';
    }
  };

  const handleSaveScannedInvoice = async () => {
    if (!scannedData) return;

    setSaving(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/tally-import/save-scanned-sales-invoice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scannedData)
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        setResult({
          status: 'success',
          message: data.message
        });
        setScannedData(null);
        fetchImportHistory();
      } else {
        setResult({
          status: 'error',
          message: data.detail || data.message || 'Failed to save invoice'
        });
      }
    } catch (error) {
      setResult({
        status: 'error',
        message: `Save failed: ${error.message}`
      });
    } finally {
      setSaving(false);
    }
  };

  const activeTabInfo = tabs.find(t => t.id === activeTab);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Database className="w-8 h-8 text-blue-600" />
            Tally Data Import
          </h1>
          <p className="text-gray-600 mt-2">
            Import your Tally data (CSV/Excel) for Sales, Purchases, Customers, and Products
          </p>
        </div>

        {/* Import Summary Cards */}
        {importHistory && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-xl p-4 shadow-sm border border-blue-100">
              <div className="flex items-center gap-3">
                <div className="bg-blue-100 p-2 rounded-lg">
                  <ShoppingCart className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{importHistory.sales_orders}</p>
                  <p className="text-sm text-gray-500">Sales Orders</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm border border-green-100">
              <div className="flex items-center gap-3">
                <div className="bg-green-100 p-2 rounded-lg">
                  <FileText className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{importHistory.purchase_orders}</p>
                  <p className="text-sm text-gray-500">Purchase Orders</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm border border-purple-100">
              <div className="flex items-center gap-3">
                <div className="bg-purple-100 p-2 rounded-lg">
                  <Users className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{importHistory.customers}</p>
                  <p className="text-sm text-gray-500">Customers</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm border border-orange-100">
              <div className="flex items-center gap-3">
                <div className="bg-orange-100 p-2 rounded-lg">
                  <Package className="w-5 h-5 text-orange-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{importHistory.products}</p>
                  <p className="text-sm text-gray-500">Products</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm border">
          <div className="border-b flex">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => { setActiveTab(tab.id); setResult(null); }}
                className={`flex items-center gap-2 px-6 py-4 font-medium transition-colors ${
                  activeTab === tab.id 
                    ? `text-${tab.color}-600 border-b-2 border-${tab.color}-600 bg-${tab.color}-50` 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
                data-testid={`tab-${tab.id}`}
              >
                <tab.icon className="w-5 h-5" />
                {tab.label}
              </button>
            ))}
          </div>

          <div className="p-6">
            {/* Day Book Import Tab Content */}
            {activeTab === 'daybook' ? (
              <DayBookImportTab
                daybookFile={daybookFile}
                setDaybookFile={setDaybookFile}
                daybookPreview={daybookPreview}
                setDaybookPreview={setDaybookPreview}
                daybookResult={daybookResult}
                setDaybookResult={setDaybookResult}
                daybookLoading={daybookLoading}
                setDaybookLoading={setDaybookLoading}
                skipUnclassified={skipUnclassified}
                setSkipUnclassified={setSkipUnclassified}
                daybookHistory={daybookHistory}
                setDaybookHistory={setDaybookHistory}
                showDaybookHistory={showDaybookHistory}
                setShowDaybookHistory={setShowDaybookHistory}
              />
            ) : activeTab === 'opening-balance' ? (
              <OpeningBalanceTab
                obFile={obFile}
                setObFile={setObFile}
                obFinancialYear={obFinancialYear}
                setObFinancialYear={setObFinancialYear}
                obAsOnDate={obAsOnDate}
                setObAsOnDate={setObAsOnDate}
                obLoading={obLoading}
                setObLoading={setObLoading}
                obResult={obResult}
                setObResult={setObResult}
                balanceSheet={balanceSheet}
                setBalanceSheet={setBalanceSheet}
                aiAnalysis={aiAnalysis}
                setAiAnalysis={setAiAnalysis}
              />
            ) : activeTab === 'daybook-entries' ? (
              <DayBookEntriesManager
                importSummary={importSummary}
                setImportSummary={setImportSummary}
                unclassifiedEntries={unclassifiedEntries}
                setUnclassifiedEntries={setUnclassifiedEntries}
                entriesLoading={entriesLoading}
                setEntriesLoading={setEntriesLoading}
                classifyingAll={classifyingAll}
                setClassifyingAll={setClassifyingAll}
                selectedCollection={selectedCollection}
                setSelectedCollection={setSelectedCollection}
                collectionEntries={collectionEntries}
                setCollectionEntries={setCollectionEntries}
              />
            ) : activeTab === 'ai-scanner' ? (
              <div>
                {/* AI Scanner Instructions */}
                <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 mb-6">
                  <h3 className="font-semibold text-indigo-800 mb-2">🤖 AI Invoice Scanner</h3>
                  <p className="text-sm text-indigo-900">
                    Upload a PDF or image of your sales invoice. Our AI will automatically extract all details including customer info, items, taxes, and totals.
                  </p>
                </div>

                {/* Scan Upload Section */}
                <div className="border-2 border-dashed border-indigo-300 rounded-xl p-8 text-center mb-6 bg-indigo-50/30">
                  <Camera className="w-12 h-12 text-indigo-400 mx-auto mb-4" />
                  <h4 className="font-medium text-gray-900 mb-2">
                    Scan Sales Invoice
                  </h4>
                  <p className="text-sm text-gray-500 mb-4">
                    Supported formats: PDF, PNG, JPG, JPEG, WEBP
                  </p>

                  <label className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors cursor-pointer">
                    {scanning ? (
                      <>
                        <RefreshCw className="w-5 h-5 animate-spin" />
                        Scanning with AI...
                      </>
                    ) : (
                      <>
                        <Scan className="w-5 h-5" />
                        Select Invoice to Scan
                      </>
                    )}
                    <input
                      type="file"
                      accept=".pdf,.png,.jpg,.jpeg,.webp"
                      onChange={handleScanInvoice}
                      disabled={scanning}
                      className="hidden"
                      data-testid="ai-scan-input"
                    />
                  </label>
                </div>

                {/* Scanned Data Preview */}
                {scannedData && (
                  <div className="bg-white border border-green-200 rounded-xl p-6 mb-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-lg text-gray-900 flex items-center gap-2">
                        <Eye className="w-5 h-5 text-green-600" />
                        Extracted Data Preview
                      </h3>
                      <button
                        onClick={handleSaveScannedInvoice}
                        disabled={saving}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
                        data-testid="save-scanned-btn"
                      >
                        {saving ? (
                          <>
                            <RefreshCw className="w-4 h-4 animate-spin" />
                            Saving...
                          </>
                        ) : (
                          <>
                            <Save className="w-4 h-4" />
                            Save to Orders
                          </>
                        )}
                      </button>
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                      {/* Invoice Details */}
                      <div className="space-y-3">
                        <h4 className="font-medium text-gray-700 border-b pb-1">Invoice Details</h4>
                        <p><span className="text-gray-500">Invoice #:</span> <strong>{scannedData.invoice_number || 'N/A'}</strong></p>
                        <p><span className="text-gray-500">Date:</span> {scannedData.invoice_date || 'N/A'}</p>
                        <p><span className="text-gray-500">Payment:</span> {scannedData.payment_mode || 'N/A'}</p>
                      </div>

                      {/* Customer Details */}
                      <div className="space-y-3">
                        <h4 className="font-medium text-gray-700 border-b pb-1">Customer Details</h4>
                        <p><strong>{scannedData.customer?.name || 'N/A'}</strong></p>
                        <p className="text-sm text-gray-600">{scannedData.customer?.phone || ''}</p>
                        <p className="text-sm text-gray-600">{scannedData.customer?.address || ''}</p>
                        <p className="text-sm text-gray-600">
                          {[scannedData.customer?.city, scannedData.customer?.state, scannedData.customer?.pincode].filter(Boolean).join(', ')}
                        </p>
                      </div>
                    </div>

                    {/* Items Table */}
                    {scannedData.items?.length > 0 && (
                      <div className="mt-4">
                        <h4 className="font-medium text-gray-700 border-b pb-1 mb-2">Items ({scannedData.items.length})</h4>
                        <div className="overflow-x-auto">
                          <table className="w-full text-sm">
                            <thead className="bg-gray-50">
                              <tr>
                                <th className="px-3 py-2 text-left">Product</th>
                                <th className="px-3 py-2 text-right">Qty</th>
                                <th className="px-3 py-2 text-right">Price</th>
                                <th className="px-3 py-2 text-right">Tax%</th>
                              </tr>
                            </thead>
                            <tbody>
                              {scannedData.items.map((item, idx) => (
                                <tr key={idx} className="border-t">
                                  <td className="px-3 py-2">{item.product_name}</td>
                                  <td className="px-3 py-2 text-right">{item.quantity}</td>
                                  <td className="px-3 py-2 text-right">₹{item.unit_price?.toLocaleString()}</td>
                                  <td className="px-3 py-2 text-right">{item.tax_rate}%</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}

                    {/* Totals */}
                    <div className="mt-4 pt-4 border-t flex justify-end">
                      <div className="text-right space-y-1">
                        <p className="text-sm"><span className="text-gray-500">Subtotal:</span> ₹{scannedData.subtotal?.toLocaleString() || 0}</p>
                        {scannedData.cgst > 0 && <p className="text-sm"><span className="text-gray-500">CGST:</span> ₹{scannedData.cgst?.toLocaleString()}</p>}
                        {scannedData.sgst > 0 && <p className="text-sm"><span className="text-gray-500">SGST:</span> ₹{scannedData.sgst?.toLocaleString()}</p>}
                        {scannedData.igst > 0 && <p className="text-sm"><span className="text-gray-500">IGST:</span> ₹{scannedData.igst?.toLocaleString()}</p>}
                        <p className="text-lg font-bold"><span className="text-gray-500">Total:</span> ₹{scannedData.grand_total?.toLocaleString() || 0}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <>
                {/* Regular Import Tab Content */}
                {/* Instructions */}
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
                  <h3 className="font-semibold text-amber-800 mb-2">📋 Import Instructions</h3>
                  <ol className="list-decimal list-inside text-sm text-amber-900 space-y-1">
                    <li>Download the template file to see the required column format</li>
                    <li>Export your data from Tally in CSV or Excel format</li>
                    <li>Ensure your file columns match the template structure</li>
                    <li>Upload your file to import the data</li>
                  </ol>
                </div>

                {/* Download Template */}
                <div className="flex flex-col gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">Download Template</h4>
                      <p className="text-sm text-gray-500">Get the template with required columns (CSV or Excel with B2B/B2C examples)</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-3">
                    <button
                      onClick={() => downloadTemplate(activeTab)}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      data-testid="download-template-btn"
                    >
                      <Download className="w-4 h-4" />
                      CSV Template
                    </button>
                    {(activeTab === 'sales' || activeTab === 'purchases' || activeTab === 'purchase-bills') && (
                      <button
                        onClick={() => downloadExcelTemplate(activeTab === 'sales' ? 'sales_b2b_b2c' : 'purchase_b2b_b2c')}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        data-testid="download-excel-template-btn"
                      >
                        <Download className="w-4 h-4" />
                        Excel Template (B2B/B2C)
                      </button>
                    )}
                  </div>
                  {(activeTab === 'sales' || activeTab === 'purchases' || activeTab === 'purchase-bills') && (
                    <p className="text-xs text-gray-500">
                      💡 Excel template includes GST columns (CGST, SGST, IGST), GSTIN, and MSME/Udyam Number fields with sample B2B and B2C transactions
                    </p>
                  )}
                </div>

                {/* Upload Section */}
                <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center mb-6">
                  <FileSpreadsheet className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h4 className="font-medium text-gray-900 mb-2">
                    Upload {activeTabInfo?.label} Data
                  </h4>
                  <p className="text-sm text-gray-500 mb-4">
                    Supported formats: CSV, XLS, XLSX
                  </p>
                  
                  <div className="flex items-center justify-center gap-6 mb-4">
                    <label className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={updateExisting}
                        onChange={(e) => setUpdateExisting(e.target.checked)}
                        className="rounded border-gray-300"
                      />
                      Update existing records
                    </label>
                    
                    {activeTab === 'purchase-bills' && (
                      <label className="flex items-center gap-2 text-sm text-orange-700">
                        <input
                          type="checkbox"
                          checked={clearBeforeImport}
                          onChange={(e) => {
                            if (e.target.checked && !window.confirm('⚠️ This will DELETE all existing purchase bills imported from Tally before importing new ones. Are you sure?')) {
                              return;
                            }
                            setClearBeforeImport(e.target.checked);
                          }}
                          className="rounded border-orange-300"
                        />
                        Clear existing & re-import
                      </label>
                    )}
                  </div>

                  <label className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors cursor-pointer">
                    {uploading ? (
                      <>
                        <RefreshCw className="w-5 h-5 animate-spin" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="w-5 h-5" />
                        Select File to Upload
                      </>
                    )}
                    <input
                      type="file"
                      accept=".csv,.xls,.xlsx"
                      onChange={handleFileUpload}
                      disabled={uploading}
                      className="hidden"
                      data-testid="file-upload-input"
                    />
                  </label>
                </div>

                {/* Result Display */}
                {result && (
                  <ImportResultsDisplay 
                    result={result}
                    activeTab={activeTab}
                    tabs={tabs}
                    onOverwriteSuccess={() => {
                      setResult(prev => ({
                        ...prev,
                        results: {
                          ...prev.results,
                          skipped_entries: prev.results?.skipped_entries?.filter(e => e._overwritten) || []
                        }
                      }));
                    }}
                  />
                )}

                {/* Clear Data Option */}
                <div className="flex items-center justify-between p-4 bg-red-50 border border-red-200 rounded-lg">
                  <div>
                    <h4 className="font-medium text-red-800">Clear Imported Data</h4>
                    <p className="text-sm text-red-600">Remove all {activeTab} data imported from Tally (for testing)</p>
                  </div>
                  <button
                    onClick={() => clearImportedData(activeTab)}
                    className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    data-testid="clear-data-btn"
                  >
                    <Trash2 className="w-4 h-4" />
                    Clear Data
                  </button>
                </div>
              </>
            )}

            {/* Result Display for AI Scanner */}
            {activeTab === 'ai-scanner' && result && (
              <div className={`rounded-lg p-4 mb-6 ${
                result.status === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
              }`}>
                <div className="flex items-center gap-2">
                  {result.status === 'success' ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-600" />
                  )}
                  <h4 className={`font-medium ${result.status === 'success' ? 'text-green-800' : 'text-red-800'}`}>
                    {result.message}
                  </h4>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Help Section */}
        <div className="mt-6 bg-white rounded-xl p-6 shadow-sm border">
          <h3 className="font-semibold text-gray-900 mb-4">📖 Column Reference Guide</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-blue-600 mb-2">Sales/Invoices Columns</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• invoice_number, invoice_date</li>
                <li>• customer_name, phone, email, address</li>
                <li>• product_name, product_model, hsn_code</li>
                <li>• quantity, unit_price, discount_percent, tax_rate</li>
                <li>• payment_mode, payment_status, order_status</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-green-600 mb-2">Purchases Columns</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• po_number, po_date</li>
                <li>• vendor_name, phone, email, gst, address</li>
                <li>• product_name, hsn_code</li>
                <li>• quantity, unit_rate, discount_percent, tax_rate</li>
                <li>• payment_mode, payment_status</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-purple-600 mb-2">Customers Columns</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• customer_id, name, phone (required), email</li>
                <li>• address, city, state, pincode</li>
                <li>• gst_number, customer_type</li>
                <li>• credit_limit, payment_terms</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-orange-600 mb-2">Products Columns</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• product_id, name (required), model_number</li>
                <li>• brand, category, hsn_code</li>
                <li>• purchase_price, selling_price, mrp</li>
                <li>• stock_quantity, reorder_level, warranty_months</li>
                <li>• specifications (format: &quot;Key:Value,Key:Value&quot;)</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Import Results Display Component with Detailed Entry Lists
const ImportResultsDisplay = ({ result, activeTab, tabs, onOverwriteSuccess }) => {
  const [showImported, setShowImported] = useState(false);
  const [showSkipped, setShowSkipped] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [overwriting, setOverwriting] = useState(null);
  const [localSkippedEntries, setLocalSkippedEntries] = useState(result?.results?.skipped_entries || []);
  
  // Update local state when result changes
  useEffect(() => {
    setLocalSkippedEntries(result?.results?.skipped_entries || []);
  }, [result?.results?.skipped_entries]);
  
  const results = result?.results || result?.result || {};
  const importedEntries = results.imported_entries || [];
  const skippedEntries = localSkippedEntries;
  
  const formatCurrency = (amount) => {
    if (!amount && amount !== 0) return '-';
    return new Intl.NumberFormat('en-IN', { 
      style: 'currency', 
      currency: 'INR', 
      maximumFractionDigits: 0 
    }).format(amount);
  };
  
  const handleOverwrite = async (entry) => {
    const currentTab = tabs.find(t => t.id === activeTab);
    if (!currentTab?.tallyType) {
      alert('Cannot overwrite entries for this tab type');
      return;
    }
    
    if (!window.confirm(`Are you sure you want to overwrite the existing entry "${entry.voucher_no}"? This will replace the existing data.`)) {
      return;
    }
    
    setOverwriting(entry.voucher_no);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/tally-voucher/overwrite/${currentTab.tallyType}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entry)
      });
      
      const data = await response.json();
      
      if (response.ok && data.status === 'success') {
        alert(`✅ ${data.message}`);
        // Remove the overwritten entry from skipped list
        setLocalSkippedEntries(prev => prev.filter(e => e.voucher_no !== entry.voucher_no));
        if (onOverwriteSuccess) onOverwriteSuccess();
      } else {
        alert(`❌ Failed: ${data.detail || data.message || 'Unknown error'}`);
      }
    } catch (error) {
      alert(`❌ Error: ${error.message}`);
    } finally {
      setOverwriting(null);
    }
  };
  
  // Entry Detail Modal
  const EntryDetailModal = ({ entry, onClose }) => {
    if (!entry) return null;
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-xl shadow-xl w-full max-w-3xl max-h-[85vh] overflow-hidden">
          <div className="p-4 border-b flex items-center justify-between bg-gray-50">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Eye className="w-5 h-5 text-blue-600" />
              Entry Details - {entry.voucher_no || entry.id || 'N/A'}
            </h2>
            <button onClick={onClose} className="p-2 hover:bg-gray-200 rounded-full transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="p-6 overflow-y-auto max-h-[70vh]">
            {/* Basic Info */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="space-y-3">
                <div>
                  <label className="text-xs text-gray-500 uppercase">Voucher No</label>
                  <p className="font-semibold text-gray-900">{entry.voucher_no || '-'}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-500 uppercase">Date</label>
                  <p className="text-gray-900">{entry.date || '-'}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-500 uppercase">Row #</label>
                  <p className="text-gray-900">{entry.row_number || '-'}</p>
                </div>
              </div>
              <div className="space-y-3">
                <div>
                  <label className="text-xs text-gray-500 uppercase">Party</label>
                  <p className="font-semibold text-gray-900">{entry.party || '-'}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-500 uppercase">Amount</label>
                  <p className="text-lg font-bold text-green-600">{formatCurrency(entry.amount || entry.debit || entry.credit)}</p>
                </div>
                {entry.status && (
                  <div>
                    <label className="text-xs text-gray-500 uppercase">Status</label>
                    <span className={`inline-block px-2 py-1 rounded text-sm ${
                      entry.status === 'imported' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {entry.status}
                    </span>
                  </div>
                )}
              </div>
            </div>
            
            {/* Debit/Credit */}
            {(entry.debit > 0 || entry.credit > 0) && (
              <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                <div>
                  <label className="text-xs text-gray-500 uppercase">Debit</label>
                  <p className="text-lg font-semibold text-red-600">{formatCurrency(entry.debit)}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-500 uppercase">Credit</label>
                  <p className="text-lg font-semibold text-green-600">{formatCurrency(entry.credit)}</p>
                </div>
              </div>
            )}
            
            {/* Narration */}
            {entry.narration && (
              <div className="mb-6">
                <label className="text-xs text-gray-500 uppercase">Narration</label>
                <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">{entry.narration}</p>
              </div>
            )}
            
            {/* Skip Reason */}
            {entry.reason && (
              <div className="mb-6 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <label className="text-xs text-yellow-700 uppercase font-medium">Skip Reason</label>
                <p className="text-yellow-800">{entry.reason}</p>
              </div>
            )}
            
            {/* Raw Data Table */}
            {entry.raw_data && Object.keys(entry.raw_data).length > 0 && (
              <div>
                <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <Database className="w-4 h-4" />
                  Original Tally Data
                </h3>
                <div className="overflow-x-auto border rounded-lg">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="px-3 py-2 text-left font-medium text-gray-700">Column</th>
                        <th className="px-3 py-2 text-left font-medium text-gray-700">Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(entry.raw_data).map(([key, value], idx) => (
                        <tr key={idx} className="border-t hover:bg-gray-50">
                          <td className="px-3 py-2 font-medium text-gray-600">{key}</td>
                          <td className="px-3 py-2 text-gray-900">
                            {value === null || value === undefined ? (
                              <span className="text-gray-400">-</span>
                            ) : typeof value === 'object' ? (
                              JSON.stringify(value)
                            ) : (
                              String(value)
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };
  
  return (
    <div className={`rounded-lg p-4 mb-6 ${
      result.status === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
    }`}>
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        {result.status === 'success' ? (
          <CheckCircle className="w-5 h-5 text-green-600" />
        ) : (
          <XCircle className="w-5 h-5 text-red-600" />
        )}
        <h4 className={`font-medium ${result.status === 'success' ? 'text-green-800' : 'text-red-800'}`}>
          {result.message}
        </h4>
      </div>
      
      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        <div className="bg-white rounded-lg p-3 text-center shadow-sm">
          <p className="text-2xl font-bold text-gray-900">{results.total_rows || 0}</p>
          <p className="text-xs text-gray-500">Total Rows</p>
        </div>
        <div className="bg-white rounded-lg p-3 text-center shadow-sm">
          <p className="text-2xl font-bold text-green-600">{results.imported || 0}</p>
          <p className="text-xs text-gray-500">Imported</p>
        </div>
        <div className="bg-white rounded-lg p-3 text-center shadow-sm">
          <p className="text-2xl font-bold text-yellow-600">{results.skipped_duplicates || skippedEntries.length || 0}</p>
          <p className="text-xs text-gray-500">Skipped (Duplicates)</p>
        </div>
        <div className="bg-white rounded-lg p-3 text-center shadow-sm">
          <p className="text-2xl font-bold text-gray-500">{results.skipped_empty || 0}</p>
          <p className="text-xs text-gray-500">Skipped (Empty)</p>
        </div>
      </div>
      
      {/* Expandable Sections */}
      <div className="space-y-3">
        {/* Imported Entries Section */}
        {importedEntries.length > 0 && (
          <div className="bg-white rounded-lg border overflow-hidden">
            <button
              onClick={() => setShowImported(!showImported)}
              className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
              data-testid="toggle-imported-entries"
            >
              <span className="flex items-center gap-2 font-medium text-green-700">
                <CheckCircle className="w-4 h-4" />
                Imported Entries ({importedEntries.length})
              </span>
              <span className={`transform transition-transform ${showImported ? 'rotate-180' : ''}`}>▼</span>
            </button>
            
            {showImported && (
              <div className="border-t max-h-64 overflow-y-auto">
                <table className="w-full text-sm">
                  <thead className="bg-green-50 sticky top-0">
                    <tr>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-600">Row</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-600">Voucher No</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-600">Date</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-600">Party</th>
                      <th className="px-3 py-2 text-right text-xs font-medium text-gray-600">Amount</th>
                      <th className="px-3 py-2 text-center text-xs font-medium text-gray-600">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {importedEntries.map((entry, idx) => (
                      <tr key={idx} className="border-t hover:bg-gray-50">
                        <td className="px-3 py-2 text-gray-500">{entry.row_number}</td>
                        <td className="px-3 py-2 font-medium">{entry.voucher_no || '-'}</td>
                        <td className="px-3 py-2">{entry.date || '-'}</td>
                        <td className="px-3 py-2 truncate max-w-[150px]" title={entry.party}>{entry.party || '-'}</td>
                        <td className="px-3 py-2 text-right font-medium text-green-600">
                          {formatCurrency(entry.amount || entry.debit || entry.credit)}
                        </td>
                        <td className="px-3 py-2 text-center">
                          <button
                            onClick={() => setSelectedEntry(entry)}
                            className="p-1 hover:bg-blue-100 rounded text-blue-600 transition-colors"
                            title="View Details"
                            data-testid={`view-imported-${idx}`}
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
        
        {/* Skipped Entries Section */}
        {skippedEntries.length > 0 && (
          <div className="bg-white rounded-lg border overflow-hidden">
            <button
              onClick={() => setShowSkipped(!showSkipped)}
              className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
              data-testid="toggle-skipped-entries"
            >
              <span className="flex items-center gap-2 font-medium text-yellow-700">
                <AlertCircle className="w-4 h-4" />
                Skipped Entries ({skippedEntries.length}) - Click to expand & overwrite
              </span>
              <span className={`transform transition-transform ${showSkipped ? 'rotate-180' : ''}`}>▼</span>
            </button>
            
            {showSkipped && (
              <div className="border-t max-h-72 overflow-y-auto">
                <table className="w-full text-sm">
                  <thead className="bg-yellow-50 sticky top-0">
                    <tr>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-600">Row</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-600">Voucher No</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-600">Date</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-600">Party</th>
                      <th className="px-3 py-2 text-right text-xs font-medium text-gray-600">Amount</th>
                      <th className="px-3 py-2 text-center text-xs font-medium text-gray-600">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {skippedEntries.map((entry, idx) => (
                      <tr key={idx} className="border-t hover:bg-yellow-50">
                        <td className="px-3 py-2 text-gray-500">{entry.row_number}</td>
                        <td className="px-3 py-2 font-medium">{entry.voucher_no || '-'}</td>
                        <td className="px-3 py-2">{entry.date || '-'}</td>
                        <td className="px-3 py-2 truncate max-w-[150px]" title={entry.party}>{entry.party || '-'}</td>
                        <td className="px-3 py-2 text-right font-medium">
                          {formatCurrency(entry.amount || entry.debit || entry.credit)}
                        </td>
                        <td className="px-3 py-2 text-center">
                          <div className="flex items-center justify-center gap-1">
                            <button
                              onClick={() => setSelectedEntry(entry)}
                              className="p-1 hover:bg-blue-100 rounded text-blue-600 transition-colors"
                              title="View Details"
                              data-testid={`view-skipped-${idx}`}
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleOverwrite(entry)}
                              disabled={overwriting === entry.voucher_no}
                              className="px-2 py-1 text-xs bg-orange-500 hover:bg-orange-600 text-white rounded transition-colors disabled:bg-gray-400 flex items-center gap-1"
                              title="Overwrite existing entry with this data"
                              data-testid={`overwrite-${idx}`}
                            >
                              {overwriting === entry.voucher_no ? (
                                <RefreshCw className="w-3 h-3 animate-spin" />
                              ) : (
                                <>
                                  <RefreshCw className="w-3 h-3" />
                                  Overwrite
                                </>
                              )}
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Errors Section */}
      {results.errors?.length > 0 && (
        <div className="mt-4 p-3 bg-red-100 rounded-lg">
          <h5 className="font-medium text-red-800 mb-2 flex items-center gap-1">
            <AlertCircle className="w-4 h-4" />
            Errors ({results.errors.length})
          </h5>
          <ul className="text-sm text-red-700 space-y-1 max-h-32 overflow-y-auto">
            {results.errors.map((error, idx) => (
              <li key={idx} className="bg-red-50 px-2 py-1 rounded">{error}</li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Entry Detail Modal */}
      {selectedEntry && (
        <EntryDetailModal entry={selectedEntry} onClose={() => setSelectedEntry(null)} />
      )}
    </div>
  );
};

// Day Book Import Tab Component
const DayBookImportTab = ({
  daybookFile, setDaybookFile,
  daybookPreview, setDaybookPreview,
  daybookResult, setDaybookResult,
  daybookLoading, setDaybookLoading,
  skipUnclassified, setSkipUnclassified,
  daybookHistory, setDaybookHistory,
  showDaybookHistory, setShowDaybookHistory
}) => {
  const [error, setError] = useState('');

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setDaybookFile(selectedFile);
      setDaybookPreview(null);
      setDaybookResult(null);
      setError('');
    }
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.name.endsWith('.csv') || droppedFile.name.endsWith('.xlsx') || droppedFile.name.endsWith('.xls'))) {
      setDaybookFile(droppedFile);
      setDaybookPreview(null);
      setDaybookResult(null);
      setError('');
    } else {
      setError('Please upload a CSV or Excel file');
    }
  }, [setDaybookFile, setDaybookPreview, setDaybookResult]);

  const handlePreview = async () => {
    if (!daybookFile) return;
    
    setDaybookLoading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('file', daybookFile);
      
      // Use smart analyze endpoint that auto-detects format
      const response = await fetch(`${BACKEND_URL}/api/smart-daybook/analyze`, {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setDaybookPreview(data);
      } else {
        setError(data.detail || 'Analysis failed');
      }
    } catch (err) {
      setError('Failed to analyze file: ' + err.message);
    } finally {
      setDaybookLoading(false);
    }
  };

  const handleImport = async () => {
    if (!daybookFile) return;
    
    setDaybookLoading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('file', daybookFile);
      
      // Use smart import endpoint
      const response = await fetch(`${BACKEND_URL}/api/smart-daybook/import`, {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setDaybookResult(data);
        setDaybookPreview(null);
      } else {
        setError(data.detail || 'Import failed');
      }
    } catch (err) {
      setError('Failed to import file: ' + err.message);
    } finally {
      setDaybookLoading(false);
    }
  };

  const downloadTemplate = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/daybook-import/template`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'daybook_import_template.xlsx';
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      setError('Failed to download template');
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/daybook-import/history`);
      const data = await response.json();
      setDaybookHistory(data.imports || []);
      setShowDaybookHistory(true);
    } catch (err) {
      setError('Failed to fetch history');
    }
  };

  const deleteImportBatch = async (batchId) => {
    if (!window.confirm('Delete this import batch? All imported entries will be removed.')) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/daybook-import/batch/${batchId}`, { method: 'DELETE' });
      if (response.ok) fetchHistory();
      else setError('Failed to delete batch');
    } catch (err) {
      setError('Failed to delete batch');
    }
  };

  const getVoucherTypeColor = (type) => {
    const colors = {
      sales_invoice: 'bg-green-100 text-green-800',
      sales_order: 'bg-green-50 text-green-700',
      purchase_bill: 'bg-blue-100 text-blue-800',
      purchase_order: 'bg-blue-50 text-blue-700',
      payment: 'bg-red-100 text-red-800',
      receipt: 'bg-emerald-100 text-emerald-800',
      expense: 'bg-orange-100 text-orange-800',
      journal: 'bg-purple-100 text-purple-800',
      bank_entry: 'bg-indigo-100 text-indigo-800',
      unknown: 'bg-gray-100 text-gray-800'
    };
    return colors[type] || colors.unknown;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount || 0);
  };

  return (
    <div>
      {/* Info Banner */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-purple-800 mb-2">📚 Day Book Import - AI Auto-Classification</h3>
        <p className="text-sm text-purple-900 mb-3">
          Upload your complete Day Book from Tally (Excel/CSV). AI will automatically classify and route entries to the correct modules.
        </p>
        <div className="flex flex-wrap gap-2">
          {['Sales Invoice', 'Purchase Bill', 'Payment', 'Receipt', 'Expense', 'Journal', 'Bank Entry'].map(type => (
            <span key={type} className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">{type}</span>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3 mb-6 flex-wrap">
        <button onClick={downloadTemplate} className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
          <Download className="w-4 h-4" /> Download Template
        </button>
        <button onClick={fetchHistory} className="flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200">
          <RefreshCw className="w-4 h-4" /> Import History
        </button>
        <button 
          onClick={async () => {
            if (!window.confirm('⚠️ This will DELETE ALL Day Book imported data from all modules (Orders, Purchases, Payments, etc.).\n\nAre you sure you want to clear all Day Book data?')) return;
            try {
              const response = await fetch(`${BACKEND_URL}/api/daybook-import/clear-all`, { method: 'DELETE' });
              const data = await response.json();
              if (response.ok) {
                alert(`✅ Cleared ${data.deleted_count} Day Book entries successfully!`);
                setDaybookFile(null);
                setDaybookPreview(null);
                setDaybookResult(null);
              } else {
                setError(data.detail || 'Failed to clear data');
              }
            } catch (err) {
              setError('Failed to clear Day Book data: ' + err.message);
            }
          }} 
          className="flex items-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
        >
          <Trash2 className="w-4 h-4" /> Clear All Day Book Data
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between">
          <div className="flex items-center gap-2 text-red-700">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError('')} className="text-red-500 hover:text-red-700">
            <X className="w-5 h-5" />
          </button>
        </div>
      )}

      {/* File Upload */}
      {!daybookPreview && !daybookResult && (
        <div
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
            daybookFile ? 'border-green-400 bg-green-50' : 'border-gray-300 hover:border-purple-400 hover:bg-purple-50'
          }`}
        >
          {daybookFile ? (
            <div className="flex flex-col items-center">
              <FileSpreadsheet className="w-16 h-16 text-green-600 mb-4" />
              <p className="text-lg font-semibold text-gray-900">{daybookFile.name}</p>
              <p className="text-gray-500 mb-4">{(daybookFile.size / 1024).toFixed(1)} KB</p>
              <div className="flex gap-3">
                <button onClick={() => setDaybookFile(null)} className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg">Remove</button>
                <button
                  onClick={handlePreview}
                  disabled={daybookLoading}
                  className="flex items-center gap-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
                >
                  {daybookLoading ? (
                    <><RefreshCw className="w-4 h-4 animate-spin" /> Analyzing...</>
                  ) : (
                    <><Eye className="w-4 h-4" /> Analyze & Preview</>
                  )}
                </button>
              </div>
            </div>
          ) : (
            <>
              <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-lg text-gray-600 mb-2">Drag & drop your Tally Day Book here</p>
              <p className="text-gray-500 mb-4">AI will auto-detect format - no template needed!</p>
              <input type="file" accept=".csv,.xlsx,.xls" onChange={handleFileSelect} className="hidden" id="daybook-file-input" />
              <label htmlFor="daybook-file-input" className="inline-block px-6 py-2 bg-purple-600 text-white rounded-lg cursor-pointer hover:bg-purple-700">
                Select File
              </label>
              <p className="text-xs text-gray-400 mt-4">Supported: CSV, Excel - ANY format from Tally</p>
            </>
          )}
        </div>
      )}

      {/* Smart Analysis Results */}
      {daybookPreview && (
        <div className="space-y-6">
          {/* File Analysis */}
          <div className="bg-white rounded-lg border p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Scan className="w-5 h-5 text-purple-600" />
              AI File Analysis - {daybookPreview.filename}
            </h2>
            
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="p-4 bg-purple-50 rounded-lg">
                <p className="text-3xl font-bold text-purple-700">{daybookPreview.row_count}</p>
                <p className="text-sm text-gray-600">Total Rows</p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-3xl font-bold text-blue-700">{daybookPreview.columns?.length || 0}</p>
                <p className="text-sm text-gray-600">Columns Detected</p>
              </div>
            </div>

            {/* Auto-Detected Column Mapping */}
            <h3 className="font-medium text-gray-700 mb-3">🤖 AI Detected Column Mapping</h3>
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {Object.entries(daybookPreview.column_mapping || {}).map(([type, column]) => (
                  <div key={type} className="flex items-center gap-2 text-sm">
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded font-medium">{type}</span>
                    <span className="text-gray-500">→</span>
                    <span className="text-gray-700 truncate">{column}</span>
                  </div>
                ))}
              </div>
              {Object.keys(daybookPreview.column_mapping || {}).length === 0 && (
                <p className="text-yellow-600 text-sm">⚠️ Could not auto-detect columns. AI will analyze content during import.</p>
              )}
            </div>

            {/* Sample Data */}
            {daybookPreview.sample_rows && daybookPreview.sample_rows.length > 0 && (
              <>
                <h3 className="font-medium text-gray-700 mb-3">Sample Data (First 5 rows)</h3>
                <div className="overflow-x-auto mb-6">
                  <table className="w-full text-xs border">
                    <thead className="bg-gray-100">
                      <tr>
                        {daybookPreview.columns?.slice(0, 8).map((col, i) => (
                          <th key={i} className="px-2 py-1 text-left border">{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {daybookPreview.sample_rows.slice(0, 3).map((row, i) => (
                        <tr key={i} className="border-b">
                          {daybookPreview.columns?.slice(0, 8).map((col, j) => (
                            <td key={j} className="px-2 py-1 border truncate max-w-[150px]">{row[col] || '-'}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}

            {/* Import Button */}
            <div className="flex gap-3">
              <button onClick={() => { setDaybookPreview(null); setDaybookFile(null); }} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Cancel</button>
              <button
                onClick={handleImport}
                disabled={daybookLoading}
                className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {daybookLoading ? (
                  <><RefreshCw className="w-4 h-4 animate-spin" /> Importing...</>
                ) : (
                  <><CheckCircle className="w-4 h-4" /> Import {daybookPreview.row_count} Entries</>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Import Result */}
      {daybookResult && (
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Import Successful!</h2>
              <p className="text-gray-600">Batch ID: {daybookResult.import_batch_id}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
            <div className="p-4 bg-green-50 rounded-lg text-center">
              <p className="text-3xl font-bold text-green-700">{daybookResult.results.imported}</p>
              <p className="text-sm text-gray-600">Imported</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg text-center">
              <p className="text-3xl font-bold text-gray-700">{daybookResult.results.total_rows}</p>
              <p className="text-sm text-gray-600">Total Rows</p>
            </div>
          </div>

          {/* Column Mapping Used */}
          {daybookResult.results.column_mapping_used && (
            <div className="mb-6">
              <h3 className="font-medium text-gray-700 mb-2">AI Detected Columns</h3>
              <div className="flex flex-wrap gap-2">
                {Object.entries(daybookResult.results.column_mapping_used).map(([type, col]) => (
                  <span key={type} className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">{type}: {col}</span>
                ))}
              </div>
            </div>
          )}

          <h3 className="font-medium text-gray-700 mb-3">Entries by Voucher Type</h3>
          <div className="flex flex-wrap gap-2 mb-6">
            {Object.entries(daybookResult.results.by_type || {}).map(([type, count]) => (
              <span key={type} className={`px-3 py-1 rounded-full text-sm font-medium ${getVoucherTypeColor(type)}`}>{type.replace('_', ' ')}: {count}</span>
            ))}
          </div>

          {daybookResult.results.errors?.length > 0 && (
            <div className="p-4 bg-red-50 rounded-lg mb-4">
              <h4 className="font-medium text-red-800 mb-2">Errors ({daybookResult.results.errors.length})</h4>
              <ul className="text-sm text-red-700 max-h-32 overflow-y-auto">
                {daybookResult.results.errors.map((err, idx) => <li key={idx}>{err}</li>)}
              </ul>
            </div>
          )}

          <button onClick={() => { setDaybookResult(null); setDaybookFile(null); }} className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
            Import Another File
          </button>
        </div>
      )}

      {/* Import History Modal */}
      {showDaybookHistory && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-3xl max-h-[80vh] overflow-hidden">
            <div className="p-4 border-b flex items-center justify-between">
              <h2 className="text-lg font-semibold">Day Book Import History</h2>
              <button onClick={() => setShowDaybookHistory(false)} className="p-2 hover:bg-gray-100 rounded"><X className="w-5 h-5" /></button>
            </div>
            <div className="p-4 overflow-y-auto max-h-[60vh]">
              {daybookHistory.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No import history found</p>
              ) : (
                <div className="space-y-3">
                  {daybookHistory.map((log) => (
                    <div key={log.id} className="p-4 border rounded-lg hover:bg-gray-50">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <p className="font-medium">{log.filename}</p>
                          <p className="text-sm text-gray-500">{new Date(log.imported_at).toLocaleString()} • Batch: {log.id}</p>
                        </div>
                        <button onClick={() => deleteImportBatch(log.id)} className="p-2 text-red-600 hover:bg-red-50 rounded" title="Delete batch">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      <div className="flex gap-4 text-sm">
                        <span className="text-green-600">Imported: {log.results?.imported || 0}</span>
                        <span className="text-yellow-600">Skipped: {log.results?.skipped || 0}</span>
                        <span className="text-gray-600">Total: {log.results?.total_rows || 0}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Day Book Entries Manager Component with Pagination and Smart AI Classification
const DayBookEntriesManager = ({
  importSummary, setImportSummary,
  unclassifiedEntries, setUnclassifiedEntries,
  entriesLoading, setEntriesLoading,
  classifyingAll, setClassifyingAll,
  selectedCollection, setSelectedCollection,
  collectionEntries, setCollectionEntries
}) => {
  const [error, setError] = useState('');
  const [voucherTypes, setVoucherTypes] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalUnclassified, setTotalUnclassified] = useState(0);
  const [aiPreview, setAiPreview] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState(null); // For viewing entry details
  const PAGE_SIZE = 50;

  // Fetch summary on mount
  useEffect(() => {
    fetchSummary();
    fetchVoucherTypes();
  }, []);

  const fetchSummary = async () => {
    setEntriesLoading(true);
    try {
      // Use new AI stats endpoint for better data
      const response = await fetch(`${BACKEND_URL}/api/ai-daybook/classification-stats`);
      const data = await response.json();
      // Normalize data structure - map by_collection to collections for UI compatibility
      setImportSummary({
        total_imported: data.total_imported,
        unclassified_count: data.unclassified || 0,
        collections: data.by_collection || {}
      });
    } catch (err) {
      // Fallback to old endpoint
      try {
        const response = await fetch(`${BACKEND_URL}/api/daybook-entries/summary`);
        const data = await response.json();
        setImportSummary(data);
      } catch {
        setError('Failed to fetch summary');
      }
    } finally {
      setEntriesLoading(false);
    }
  };

  const fetchVoucherTypes = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/daybook-entries/voucher-types`);
      const data = await response.json();
      setVoucherTypes(data.voucher_types || []);
    } catch (err) {
      console.error('Failed to fetch voucher types');
    }
  };

  const fetchUnclassified = async (page = 1) => {
    setEntriesLoading(true);
    try {
      const skip = (page - 1) * PAGE_SIZE;
      const response = await fetch(`${BACKEND_URL}/api/daybook-entries/unclassified?skip=${skip}&limit=${PAGE_SIZE}`);
      const data = await response.json();
      setUnclassifiedEntries(data.entries || []);
      setTotalUnclassified(data.total || 0);
      setCurrentPage(page);
      setSelectedCollection('unclassified');
    } catch (err) {
      setError('Failed to fetch unclassified entries');
    } finally {
      setEntriesLoading(false);
    }
  };

  const fetchCollectionEntries = async (collectionName) => {
    setEntriesLoading(true);
    setCollectionEntries([]); // Clear previous entries first
    try {
      // Map display names to actual MongoDB collection names
      const collectionMap = {
        'Sales/Orders': 'orders',
        'Purchase Bills': 'purchase_bills',
        'Payments': 'payments',
        'Receipts': 'receipts',
        'Expenses': 'expenses',
        'Journal Vouchers': 'journal_vouchers',
        'Bank Transactions': 'bank_transactions',
        'Credit Notes': 'credit_notes',
        'Contra Entries': 'contra_entries'
      };
      const apiCollectionName = collectionMap[collectionName] || collectionName.toLowerCase().replace(/ /g, '_');
      console.log('Fetching collection:', collectionName, '-> API:', apiCollectionName);
      
      const response = await fetch(`${BACKEND_URL}/api/daybook-entries/by-collection/${apiCollectionName}?limit=100`);
      const data = await response.json();
      console.log('Received entries:', data.entries?.length || 0);
      
      setCollectionEntries(data.entries || []);
      setSelectedCollection(collectionName);
    } catch (err) {
      console.error('Error fetching entries:', err);
      setError('Failed to fetch entries: ' + err.message);
    } finally {
      setEntriesLoading(false);
    }
  };

  const reclassifyEntry = async (entryId, currentCollection, newVoucherType) => {
    if (!newVoucherType) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/daybook-entries/reclassify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          entry_id: entryId,
          current_collection: currentCollection,
          new_voucher_type: newVoucherType
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        // Remove entry from current view
        setCollectionEntries(prev => prev.filter(e => e.id !== entryId));
        // Refresh summary
        fetchSummary();
        alert(`Entry reclassified to ${newVoucherType}`);
      } else {
        setError(data.detail || 'Reclassification failed');
      }
    } catch (err) {
      setError('Failed to reclassify entry');
    }
  };

  const previewAiClassification = async () => {
    setPreviewLoading(true);
    setAiPreview(null);
    try {
      const response = await fetch(`${BACKEND_URL}/api/ai-daybook/unclassified-analysis?limit=100`);
      const data = await response.json();
      setAiPreview(data);
    } catch (err) {
      setError('Failed to preview AI classification');
    } finally {
      setPreviewLoading(false);
    }
  };

  const smartAiClassify = async (batchSize = 200) => {
    if (!window.confirm(`This will use Smart AI to classify up to ${batchSize} entries. Continue?`)) return;
    
    setClassifyingAll(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/ai-daybook/smart-classify?batch_size=${batchSize}&dry_run=false`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (response.ok) {
        const byType = Object.entries(data.results?.by_type || {})
          .map(([k, v]) => `  ${k.replace('_', ' ')}: ${v}`)
          .join('\n');
        alert(`Smart AI Classification Complete!\n\nClassified: ${data.results?.classified || 0} of ${data.results?.total_processed || 0}\n\nBy Type:\n${byType}`);
        fetchSummary();
        fetchUnclassified(1);
        setAiPreview(null);
      } else {
        setError(data.detail || 'AI classification failed');
      }
    } catch (err) {
      setError('Failed to run Smart AI classification');
    } finally {
      setClassifyingAll(false);
    }
  };

  const manualClassify = async (entryId, voucherType) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/daybook-entries/manual-classify/${entryId}?voucher_type=${voucherType}`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (response.ok) {
        setUnclassifiedEntries(prev => prev.filter(e => e.id !== entryId));
        setTotalUnclassified(prev => prev - 1);
        fetchSummary();
      } else {
        setError(data.detail || 'Classification failed');
      }
    } catch (err) {
      setError('Failed to classify entry');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount || 0);
  };

  const getCollectionColor = (name) => {
    const colors = {
      'Sales/Orders': 'bg-green-100 text-green-800',
      'Purchase Bills': 'bg-blue-100 text-blue-800',
      'Payments': 'bg-red-100 text-red-800',
      'Receipts': 'bg-emerald-100 text-emerald-800',
      'Expenses': 'bg-orange-100 text-orange-800',
      'Journal Vouchers': 'bg-purple-100 text-purple-800',
      'Bank Transactions': 'bg-indigo-100 text-indigo-800',
      'Unclassified': 'bg-yellow-100 text-yellow-800'
    };
    return colors[name] || 'bg-gray-100 text-gray-800';
  };

  const totalPages = Math.ceil(totalUnclassified / PAGE_SIZE);

  // Entry Detail Modal Component
  const EntryDetailModal = ({ entry, onClose }) => {
    if (!entry) return null;
    
    const formatValue = (value) => {
      if (value === null || value === undefined) return '-';
      if (typeof value === 'object') return JSON.stringify(value, null, 2);
      return String(value);
    };
    
    const importantFields = [
      { key: 'id', label: 'Entry ID' },
      { key: 'order_number', label: 'Order/Voucher No' },
      { key: 'bill_number', label: 'Bill Number' },
      { key: 'receipt_id', label: 'Receipt ID' },
      { key: 'payment_id', label: 'Payment ID' },
      { key: 'voucher_id', label: 'Voucher ID' },
      { key: 'date', label: 'Date' },
      { key: 'order_date', label: 'Order Date' },
      { key: 'bill_date', label: 'Bill Date' },
      { key: 'receipt_date', label: 'Receipt Date' },
      { key: 'payment_date', label: 'Payment Date' },
    ];
    
    const partyFields = [
      { key: 'customer_details', label: 'Customer Details' },
      { key: 'vendor_name', label: 'Vendor Name' },
      { key: 'paid_to', label: 'Paid To' },
      { key: 'received_from', label: 'Received From' },
      { key: 'ledger', label: 'Ledger' },
    ];
    
    const amountFields = [
      { key: 'total_amount', label: 'Total Amount' },
      { key: 'amount', label: 'Amount' },
      { key: 'debit_amount', label: 'Debit Amount' },
      { key: 'credit_amount', label: 'Credit Amount' },
      { key: 'debit', label: 'Debit' },
      { key: 'credit', label: 'Credit' },
    ];
    
    const metaFields = [
      { key: 'source', label: 'Source' },
      { key: 'source_file', label: 'Source File' },
      { key: 'ai_classified', label: 'AI Classified' },
      { key: 'status', label: 'Status' },
      { key: 'narration', label: 'Narration' },
      { key: 'description', label: 'Description' },
      { key: 'notes', label: 'Notes' },
      { key: 'created_at', label: 'Created At' },
    ];
    
    const aiFields = [
      { key: 'ai_classification', label: 'AI Classification' },
      { key: 'reclassified', label: 'Reclassified' },
      { key: 'reclassified_from', label: 'Reclassified From' },
      { key: 'reclassified_to', label: 'Reclassified To' },
      { key: 'reclassified_at', label: 'Reclassified At' },
    ];

    const renderFieldSection = (title, fields, bgColor = 'bg-gray-50') => {
      const hasData = fields.some(f => entry[f.key] !== undefined && entry[f.key] !== null);
      if (!hasData) return null;
      
      return (
        <div className={`${bgColor} rounded-lg p-3 mb-3`}>
          <h5 className="font-semibold text-gray-700 mb-2 text-sm">{title}</h5>
          <div className="grid grid-cols-2 gap-2">
            {fields.map(({ key, label }) => {
              const value = entry[key];
              if (value === undefined || value === null) return null;
              return (
                <div key={key} className="text-sm">
                  <span className="text-gray-500">{label}:</span>
                  <span className="ml-2 text-gray-800 font-medium">
                    {typeof value === 'object' ? (
                      value.name || JSON.stringify(value)
                    ) : typeof value === 'boolean' ? (
                      value ? '✅ Yes' : '❌ No'
                    ) : (
                      formatValue(value)
                    )}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      );
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-teal-600 to-teal-700 text-white p-4 flex items-center justify-between">
            <div>
              <h4 className="font-bold text-lg">Entry Details</h4>
              <p className="text-teal-100 text-sm">{entry.id || entry.order_number || entry.voucher_id || 'N/A'}</p>
            </div>
            <button 
              onClick={onClose}
              className="p-2 hover:bg-teal-500 rounded-full transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          {/* Content */}
          <div className="p-4 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 140px)' }}>
            {renderFieldSection('📋 Basic Information', importantFields, 'bg-blue-50')}
            {renderFieldSection('👤 Party Details', partyFields, 'bg-green-50')}
            {renderFieldSection('💰 Amount Details', amountFields, 'bg-yellow-50')}
            {renderFieldSection('🤖 AI Classification', aiFields, 'bg-purple-50')}
            {renderFieldSection('📝 Additional Info', metaFields, 'bg-gray-50')}
            
            {/* Raw Data Section - Display as Table */}
            {entry.raw_data && Object.keys(entry.raw_data).length > 0 && (
              <div className="bg-orange-50 rounded-lg p-3 mt-3 border border-orange-200">
                <h5 className="font-semibold text-orange-800 mb-3 text-sm">📦 Original Tally Data (All Columns)</h5>
                <div className="bg-white rounded-lg overflow-hidden border">
                  <table className="w-full text-sm">
                    <thead className="bg-orange-100">
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-semibold text-orange-800 w-1/3">Column</th>
                        <th className="px-3 py-2 text-left text-xs font-semibold text-orange-800">Value</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-orange-100">
                      {Object.entries(entry.raw_data)
                        .filter(([key, value]) => value !== null && value !== '' && value !== undefined)
                        .map(([key, value]) => (
                          <tr key={key} className="hover:bg-orange-50">
                            <td className="px-3 py-2 text-xs font-medium text-gray-700">{key}</td>
                            <td className="px-3 py-2 text-xs text-gray-900">
                              {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
            
            {/* No Raw Data Message */}
            {(!entry.raw_data || Object.keys(entry.raw_data).length === 0) && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-3">
                <p className="text-yellow-800 text-sm">
                  ⚠️ <strong>No raw data available.</strong> This entry was imported before raw data preservation was enabled. 
                  Please re-import your Day Book to see full details.
                </p>
              </div>
            )}
          </div>
          
          {/* Footer */}
          <div className="border-t p-4 bg-gray-50 flex justify-end gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div>
      {/* Entry Detail Modal */}
      {selectedEntry && (
        <EntryDetailModal entry={selectedEntry} onClose={() => setSelectedEntry(null)} />
      )}
      
      {/* Header */}
      <div className="bg-teal-50 border border-teal-200 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-teal-800 mb-2">📊 Day Book Entries Manager</h3>
        <p className="text-sm text-teal-900">
          View all imported entries, check where they were classified, and use AI to classify unclassified entries.
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between">
          <span className="text-red-700">{error}</span>
          <button onClick={() => setError('')} className="text-red-500"><X className="w-5 h-5" /></button>
        </div>
      )}

      {/* Summary Cards */}
      {importSummary && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold text-gray-800">Import Summary</h4>
            <button onClick={fetchSummary} className="flex items-center gap-2 px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200">
              <RefreshCw className="w-4 h-4" /> Refresh
            </button>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="p-4 bg-blue-50 rounded-lg text-center">
              <p className="text-3xl font-bold text-blue-700">{importSummary.total_imported}</p>
              <p className="text-sm text-gray-600">Total Imported</p>
            </div>
            <div className="p-4 bg-yellow-50 rounded-lg text-center cursor-pointer hover:bg-yellow-100" onClick={fetchUnclassified}>
              <p className="text-3xl font-bold text-yellow-700">{importSummary.unclassified_count}</p>
              <p className="text-sm text-gray-600">Unclassified</p>
              <p className="text-xs text-yellow-600 mt-1">Click to view</p>
            </div>
          </div>

          {/* Collections Breakdown */}
          <div className="bg-white border rounded-lg p-4">
            <h5 className="font-medium text-gray-700 mb-3">Entries by Voucher Type (Click to view)</h5>
            <div className="flex flex-wrap gap-2">
              {Object.entries(importSummary.collections || {}).map(([name, count]) => (
                <button
                  key={name}
                  onClick={() => name === 'Unclassified' ? fetchUnclassified() : fetchCollectionEntries(name)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all hover:scale-105 ${getCollectionColor(name)}`}
                >
                  {name}: {count}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Unclassified Entries Section with Pagination */}
      {selectedCollection === 'unclassified' && (
        <div className="bg-white border rounded-lg overflow-hidden mb-6">
          <div className="p-4 border-b bg-yellow-50">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h4 className="font-semibold text-yellow-800">Unclassified Entries ({totalUnclassified})</h4>
                <p className="text-sm text-yellow-700">These entries couldn't be auto-classified. Use Smart AI or manually classify them.</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={previewAiClassification}
                  disabled={previewLoading}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  data-testid="ai-preview-btn"
                >
                  {previewLoading ? (
                    <><RefreshCw className="w-4 h-4 animate-spin" /> Analyzing...</>
                  ) : (
                    <><Eye className="w-4 h-4" /> Preview AI Classification</>
                  )}
                </button>
                <button
                  onClick={() => smartAiClassify(200)}
                  disabled={classifyingAll}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
                  data-testid="smart-ai-classify-btn"
                >
                  {classifyingAll ? (
                    <><RefreshCw className="w-4 h-4 animate-spin" /> Classifying...</>
                  ) : (
                    <><Scan className="w-4 h-4" /> Smart AI Classify All</>
                  )}
                </button>
              </div>
            </div>
            
            {/* AI Preview Results */}
            {aiPreview && (
              <div className="mt-4 p-4 bg-white rounded-lg border">
                <h5 className="font-medium text-gray-800 mb-3">AI Classification Preview (First 100 entries)</h5>
                <div className="flex flex-wrap gap-3 mb-4">
                  {Object.entries(aiPreview.predictions || {}).filter(([_, v]) => v > 0).map(([type, count]) => (
                    <div key={type} className={`px-4 py-2 rounded-lg ${
                      type === 'receipt' ? 'bg-emerald-100 text-emerald-800' :
                      type === 'sales_invoice' ? 'bg-green-100 text-green-800' :
                      type === 'payment' ? 'bg-red-100 text-red-800' :
                      type === 'expense' ? 'bg-orange-100 text-orange-800' :
                      type === 'journal' ? 'bg-purple-100 text-purple-800' :
                      type === 'unknown' ? 'bg-gray-100 text-gray-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      <span className="font-bold text-lg">{count}</span>
                      <span className="text-sm ml-2">{type.replace('_', ' ')}</span>
                    </div>
                  ))}
                </div>
                <p className="text-sm text-gray-600">
                  Will classify {aiPreview.analyzed - (aiPreview.predictions?.unknown || 0)} of {aiPreview.analyzed} analyzed entries. 
                  Total unclassified: {aiPreview.total_unclassified}
                </p>
                <button
                  onClick={() => smartAiClassify(aiPreview.total_unclassified)}
                  className="mt-3 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Classify All {aiPreview.total_unclassified} Entries
                </button>
              </div>
            )}
          </div>
          
          {/* Entries Table */}
          {unclassifiedEntries.length > 0 && (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 sticky top-0">
                    <tr>
                      <th className="px-2 py-2 text-left text-xs w-10">View</th>
                      <th className="px-3 py-2 text-left text-xs">Row</th>
                      <th className="px-3 py-2 text-left text-xs">Date</th>
                      <th className="px-3 py-2 text-left text-xs">Party/Ledger</th>
                      <th className="px-3 py-2 text-left text-xs">Vch Type</th>
                      <th className="px-3 py-2 text-right text-xs">Debit</th>
                      <th className="px-3 py-2 text-right text-xs">Credit</th>
                      <th className="px-3 py-2 text-left text-xs">Narration</th>
                      <th className="px-3 py-2 text-left text-xs">Classify As</th>
                    </tr>
                  </thead>
                  <tbody>
                    {unclassifiedEntries.map((entry, idx) => (
                      <tr key={idx} className="border-b hover:bg-gray-50">
                        <td className="px-2 py-2">
                          <button
                            onClick={() => setSelectedEntry(entry)}
                            className="p-1 text-blue-600 hover:bg-blue-100 rounded transition-colors"
                            title="View Details"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                        </td>
                        <td className="px-3 py-2 text-xs">{entry.row_number}</td>
                        <td className="px-3 py-2 text-xs">{entry.date}</td>
                        <td className="px-3 py-2 max-w-[200px] truncate font-medium">
                          {entry.party || entry.party?.name || '-'}
                        </td>
                        <td className="px-3 py-2 text-xs text-gray-500">
                          {entry.original_voucher_type || entry.voucher_type_raw || '-'}
                        </td>
                        <td className="px-3 py-2 text-right text-red-600 font-medium">
                          {(entry.debit > 0 || entry.amounts?.debit > 0) ? formatCurrency(entry.debit || entry.amounts?.debit) : '-'}
                        </td>
                        <td className="px-3 py-2 text-right text-green-600 font-medium">
                          {(entry.credit > 0 || entry.amounts?.credit > 0) ? formatCurrency(entry.credit || entry.amounts?.credit) : '-'}
                        </td>
                        <td className="px-3 py-2 max-w-[150px] truncate text-xs text-gray-500">
                          {entry.narration || entry.references?.narration || '-'}
                        </td>
                        <td className="px-3 py-2">
                          <select
                            onChange={(e) => e.target.value && manualClassify(entry.id, e.target.value)}
                            className="text-xs border rounded px-2 py-1 w-full"
                            defaultValue=""
                          >
                            <option value="">Select...</option>
                            {voucherTypes.map(vt => (
                              <option key={vt.id} value={vt.id}>{vt.display}</option>
                            ))}
                          </select>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {/* Pagination */}
              {totalPages > 1 && (
                <div className="p-4 border-t bg-gray-50 flex items-center justify-between">
                  <div className="text-sm text-gray-600">
                    Showing {((currentPage - 1) * PAGE_SIZE) + 1} - {Math.min(currentPage * PAGE_SIZE, totalUnclassified)} of {totalUnclassified} entries
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => fetchUnclassified(currentPage - 1)}
                      disabled={currentPage === 1 || entriesLoading}
                      className="px-3 py-1 bg-white border rounded disabled:opacity-50 hover:bg-gray-100"
                    >
                      Previous
                    </button>
                    <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded">
                      Page {currentPage} of {totalPages}
                    </span>
                    <button
                      onClick={() => fetchUnclassified(currentPage + 1)}
                      disabled={currentPage === totalPages || entriesLoading}
                      className="px-3 py-1 bg-white border rounded disabled:opacity-50 hover:bg-gray-100"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
          
          {unclassifiedEntries.length === 0 && !entriesLoading && (
            <div className="p-8 text-center text-gray-500">
              <CheckCircle className="w-12 h-12 mx-auto text-green-500 mb-3" />
              <p>No unclassified entries!</p>
            </div>
          )}
        </div>
      )}

      {/* Collection Entries View */}
      {selectedCollection && selectedCollection !== 'unclassified' && (
        <div className="bg-white border-2 border-blue-200 rounded-lg overflow-hidden mt-6 shadow-lg">
          <div className="p-4 border-b bg-blue-50 flex items-center justify-between">
            <div>
              <h4 className="font-semibold text-blue-800">{selectedCollection}</h4>
              <p className="text-sm text-blue-600">{collectionEntries.length} entries loaded (showing up to 100)</p>
            </div>
            <button 
              onClick={() => { setSelectedCollection(null); setCollectionEntries([]); }} 
              className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 flex items-center gap-1"
            >
              <X className="w-4 h-4" /> Close
            </button>
          </div>
          
          {entriesLoading ? (
            <div className="p-8 text-center">
              <RefreshCw className="w-8 h-8 mx-auto text-blue-500 animate-spin mb-3" />
              <p className="text-gray-600">Loading entries...</p>
            </div>
          ) : collectionEntries.length > 0 ? (
            <div className="overflow-x-auto" style={{ maxHeight: '500px' }}>
              <table className="w-full text-sm">
                <thead className="bg-gray-100 sticky top-0 z-10">
                  <tr>
                    <th className="px-2 py-3 text-left text-xs font-semibold text-gray-700 w-10">View</th>
                    <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700">ID</th>
                    <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700">Date</th>
                    <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700">Party/Details</th>
                    <th className="px-3 py-3 text-right text-xs font-semibold text-gray-700">Amount</th>
                    <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700">Status</th>
                    <th className="px-3 py-3 text-left text-xs font-semibold text-gray-700">Reclassify</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {collectionEntries.map((entry, idx) => (
                    <tr key={entry.id || idx} className="hover:bg-blue-50 transition-colors">
                      <td className="px-2 py-2">
                        <button
                          onClick={() => setSelectedEntry(entry)}
                          className="p-1.5 text-blue-600 hover:bg-blue-100 rounded-full transition-colors"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      </td>
                      <td className="px-3 py-2 font-mono text-xs text-gray-600">
                        {entry.order_number || entry.bill_number || entry.payment_id || entry.receipt_id || entry.expense_id || entry.voucher_id || entry.transaction_id || entry.id}
                      </td>
                      <td className="px-3 py-2 text-xs">
                        {entry.order_date || entry.bill_date || entry.payment_date || entry.receipt_date || entry.expense_date || entry.voucher_date || entry.transaction_date || entry.date || '-'}
                      </td>
                      <td className="px-3 py-2 max-w-[200px]">
                        <div className="truncate font-medium text-gray-800">
                          {entry.customer_details?.name || entry.vendor_name || entry.paid_to || entry.received_from || entry.description || entry.ledger || entry.narration || '-'}
                        </div>
                        {entry.ai_classification?.reason && (
                          <div className="text-xs text-gray-500 truncate mt-1">
                            AI: {entry.ai_classification.reason}
                          </div>
                        )}
                      </td>
                      <td className="px-3 py-2 text-right font-semibold text-gray-800">
                        {formatCurrency(entry.total_amount || entry.amount || entry.debit_amount || entry.credit_amount || entry.debit || entry.credit || 0)}
                      </td>
                      <td className="px-3 py-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          entry.ai_classified ? 'bg-purple-100 text-purple-700' : 'bg-green-100 text-green-700'
                        }`}>
                          {entry.ai_classified ? 'AI' : entry.status || 'Imported'}
                        </span>
                      </td>
                      <td className="px-3 py-2">
                        <select
                          onChange={(e) => reclassifyEntry(entry.id, selectedCollection, e.target.value)}
                          className="text-xs border border-gray-300 rounded px-2 py-1 bg-white hover:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-500"
                          defaultValue=""
                        >
                          <option value="">Move to...</option>
                          {voucherTypes.filter(vt => vt.display !== selectedCollection).map(vt => (
                            <option key={vt.id} value={vt.id}>{vt.display}</option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center text-gray-500">
              <Database className="w-12 h-12 mx-auto text-gray-300 mb-3" />
              <p>No entries found in this collection.</p>
            </div>
          )}
        </div>
      )}

      {/* Loading State */}
      {entriesLoading && (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="w-8 h-8 text-teal-600 animate-spin" />
          <span className="ml-3 text-gray-600">Loading entries...</span>
        </div>
      )}

      {/* Empty State */}
      {!entriesLoading && importSummary?.total_imported === 0 && (
        <div className="text-center py-12 text-gray-500">
          <Database className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <p>No Day Book entries imported yet.</p>
          <p className="text-sm">Go to "Day Book Import" tab to upload your Tally Day Book.</p>
        </div>
      )}
    </div>
  );
};

// Opening Balance Tab Component
const OpeningBalanceTab = ({
  obFile, setObFile,
  obFinancialYear, setObFinancialYear,
  obAsOnDate, setObAsOnDate,
  obLoading, setObLoading,
  obResult, setObResult,
  balanceSheet, setBalanceSheet,
  aiAnalysis, setAiAnalysis
}) => {
  const [error, setError] = useState('');

  const downloadTemplate = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/opening-balance/template`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'opening_balance_template.xlsx';
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      setError('Failed to download template');
    }
  };

  const handleImport = async () => {
    if (!obFile) return;
    
    setObLoading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('file', obFile);
      formData.append('financial_year', obFinancialYear);
      formData.append('as_on_date', obAsOnDate);
      
      const response = await fetch(`${BACKEND_URL}/api/opening-balance/import`, {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setObResult(data);
        fetchBalanceSheet();
      } else {
        setError(data.detail || 'Import failed');
      }
    } catch (err) {
      setError('Failed to import: ' + err.message);
    } finally {
      setObLoading(false);
    }
  };

  const fetchBalanceSheet = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/opening-balance/balance-sheet?financial_year=${obFinancialYear}`);
      const data = await response.json();
      setBalanceSheet(data);
    } catch (err) {
      console.error('Failed to fetch balance sheet');
    }
  };

  const runAiAnalysis = async () => {
    setObLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/opening-balance/ai-analysis?financial_year=${obFinancialYear}`, {
        method: 'POST'
      });
      const data = await response.json();
      setAiAnalysis(data);
    } catch (err) {
      setError('AI Analysis failed');
    } finally {
      setObLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount || 0);
  };

  return (
    <div>
      {/* Info Banner */}
      <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-emerald-800 mb-2">📊 Opening Balances & Balance Sheet</h3>
        <p className="text-sm text-emerald-900">
          Import your previous year's balance sheet to set opening balances. The AI CA Agent can analyze your financial position.
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <span className="text-red-700">{error}</span>
          <button onClick={() => setError('')} className="float-right text-red-500"><X className="w-4 h-4" /></button>
        </div>
      )}

      {/* Upload Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Import Form */}
        <div className="bg-white border rounded-lg p-6">
          <h4 className="font-semibold mb-4">Import Balance Sheet</h4>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Financial Year</label>
              <select
                value={obFinancialYear}
                onChange={(e) => setObFinancialYear(e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              >
                <option value="2024-25">2024-25</option>
                <option value="2025-26">2025-26</option>
                <option value="2026-27">2026-27</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">As On Date (Opening Date)</label>
              <input
                type="date"
                value={obAsOnDate}
                onChange={(e) => setObAsOnDate(e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Balance Sheet File</label>
              <input
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={(e) => setObFile(e.target.files[0])}
                className="w-full border rounded-lg px-3 py-2"
              />
              {obFile && <p className="text-sm text-green-600 mt-1">Selected: {obFile.name}</p>}
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={downloadTemplate}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                <Download className="w-4 h-4" /> Template
              </button>
              <button
                onClick={handleImport}
                disabled={!obFile || obLoading}
                className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50"
              >
                {obLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                Import Balances
              </button>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white border rounded-lg p-6">
          <h4 className="font-semibold mb-4">Quick Actions</h4>
          
          <div className="space-y-3">
            <button
              onClick={fetchBalanceSheet}
              className="w-full flex items-center gap-3 px-4 py-3 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100"
            >
              <FileSpreadsheet className="w-5 h-5" />
              <span>View Balance Sheet</span>
            </button>
            
            <button
              onClick={runAiAnalysis}
              disabled={obLoading}
              className="w-full flex items-center gap-3 px-4 py-3 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 disabled:opacity-50"
            >
              <Scan className="w-5 h-5" />
              <span>{obLoading ? 'Analyzing...' : 'AI CA Analysis'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Import Result */}
      {obResult && (
        <div className="bg-white border rounded-lg p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <CheckCircle className="w-8 h-8 text-green-600" />
            <h4 className="text-lg font-semibold">Import Complete</h4>
          </div>
          
          <div className="grid grid-cols-4 gap-4 mb-4">
            <div className="p-3 bg-green-50 rounded text-center">
              <p className="text-2xl font-bold text-green-700">{obResult.results.accounts_created}</p>
              <p className="text-xs text-gray-600">Created</p>
            </div>
            <div className="p-3 bg-blue-50 rounded text-center">
              <p className="text-2xl font-bold text-blue-700">{obResult.results.accounts_updated}</p>
              <p className="text-xs text-gray-600">Updated</p>
            </div>
            <div className="p-3 bg-gray-50 rounded text-center">
              <p className="text-2xl font-bold text-gray-700">{formatCurrency(obResult.results.total_debit)}</p>
              <p className="text-xs text-gray-600">Total Debit</p>
            </div>
            <div className="p-3 bg-gray-50 rounded text-center">
              <p className="text-2xl font-bold text-gray-700">{formatCurrency(obResult.results.total_credit)}</p>
              <p className="text-xs text-gray-600">Total Credit</p>
            </div>
          </div>
          
          <p className={`text-sm ${obResult.results.balance_check === 'balanced' ? 'text-green-600' : 'text-yellow-600'}`}>
            Balance Check: {obResult.results.balance_check}
          </p>
        </div>
      )}

      {/* Balance Sheet View */}
      {balanceSheet && (
        <div className="bg-white border rounded-lg p-6 mb-6">
          <h4 className="text-lg font-semibold mb-4">Balance Sheet - FY {balanceSheet.financial_year || obFinancialYear}</h4>
          
          <div className="grid grid-cols-2 gap-6">
            {/* Assets */}
            <div>
              <h5 className="font-medium text-gray-800 mb-3 pb-2 border-b">ASSETS</h5>
              
              {balanceSheet.balance_sheet?.assets?.current_assets?.items?.length > 0 && (
                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-600 mb-2">Current Assets</p>
                  {balanceSheet.balance_sheet.assets.current_assets.items.map((item, i) => (
                    <div key={i} className="flex justify-between text-sm py-1">
                      <span>{item.name}</span>
                      <span>{formatCurrency(item.amount)}</span>
                    </div>
                  ))}
                  <div className="flex justify-between font-medium border-t pt-1 mt-1">
                    <span>Sub Total</span>
                    <span>{formatCurrency(balanceSheet.balance_sheet.assets.current_assets.total)}</span>
                  </div>
                </div>
              )}
              
              {balanceSheet.balance_sheet?.assets?.fixed_assets?.items?.length > 0 && (
                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-600 mb-2">Fixed Assets</p>
                  {balanceSheet.balance_sheet.assets.fixed_assets.items.map((item, i) => (
                    <div key={i} className="flex justify-between text-sm py-1">
                      <span>{item.name}</span>
                      <span>{formatCurrency(item.amount)}</span>
                    </div>
                  ))}
                  <div className="flex justify-between font-medium border-t pt-1 mt-1">
                    <span>Sub Total</span>
                    <span>{formatCurrency(balanceSheet.balance_sheet.assets.fixed_assets.total)}</span>
                  </div>
                </div>
              )}
              
              <div className="flex justify-between font-bold text-lg border-t-2 pt-2 mt-2">
                <span>TOTAL ASSETS</span>
                <span>{formatCurrency(balanceSheet.summary?.total_assets)}</span>
              </div>
            </div>
            
            {/* Liabilities & Equity */}
            <div>
              <h5 className="font-medium text-gray-800 mb-3 pb-2 border-b">LIABILITIES & EQUITY</h5>
              
              {balanceSheet.balance_sheet?.liabilities?.current_liabilities?.items?.length > 0 && (
                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-600 mb-2">Current Liabilities</p>
                  {balanceSheet.balance_sheet.liabilities.current_liabilities.items.map((item, i) => (
                    <div key={i} className="flex justify-between text-sm py-1">
                      <span>{item.name}</span>
                      <span>{formatCurrency(item.amount)}</span>
                    </div>
                  ))}
                  <div className="flex justify-between font-medium border-t pt-1 mt-1">
                    <span>Sub Total</span>
                    <span>{formatCurrency(balanceSheet.balance_sheet.liabilities.current_liabilities.total)}</span>
                  </div>
                </div>
              )}
              
              {balanceSheet.balance_sheet?.equity?.capital?.items?.length > 0 && (
                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-600 mb-2">Equity</p>
                  {balanceSheet.balance_sheet.equity.capital.items.map((item, i) => (
                    <div key={i} className="flex justify-between text-sm py-1">
                      <span>{item.name}</span>
                      <span>{formatCurrency(item.amount)}</span>
                    </div>
                  ))}
                  <div className="flex justify-between font-medium border-t pt-1 mt-1">
                    <span>Sub Total</span>
                    <span>{formatCurrency(balanceSheet.balance_sheet.equity.capital.total)}</span>
                  </div>
                </div>
              )}
              
              <div className="flex justify-between font-bold text-lg border-t-2 pt-2 mt-2">
                <span>TOTAL LIAB. & EQUITY</span>
                <span>{formatCurrency(balanceSheet.summary?.total_liabilities_equity)}</span>
              </div>
            </div>
          </div>
          
          {/* Balance Check */}
          <div className={`mt-4 p-3 rounded-lg text-center ${balanceSheet.summary?.is_balanced ? 'bg-green-50 text-green-800' : 'bg-yellow-50 text-yellow-800'}`}>
            {balanceSheet.summary?.is_balanced ? '✅ Balance Sheet is Balanced' : `⚠️ Difference: ${formatCurrency(Math.abs(balanceSheet.summary?.total_assets - balanceSheet.summary?.total_liabilities_equity))}`}
          </div>
        </div>
      )}

      {/* AI Analysis */}
      {aiAnalysis && (
        <div className="bg-white border rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <Scan className="w-6 h-6 text-purple-600" />
            <h4 className="text-lg font-semibold">AI CA Agent Analysis</h4>
          </div>
          
          {/* Key Metrics */}
          <div className="grid grid-cols-5 gap-4 mb-6">
            <div className="p-3 bg-blue-50 rounded text-center">
              <p className="text-xl font-bold text-blue-700">{formatCurrency(aiAnalysis.metrics?.total_assets)}</p>
              <p className="text-xs text-gray-600">Total Assets</p>
            </div>
            <div className="p-3 bg-red-50 rounded text-center">
              <p className="text-xl font-bold text-red-700">{formatCurrency(aiAnalysis.metrics?.total_liabilities)}</p>
              <p className="text-xs text-gray-600">Total Liabilities</p>
            </div>
            <div className="p-3 bg-green-50 rounded text-center">
              <p className="text-xl font-bold text-green-700">{formatCurrency(aiAnalysis.metrics?.total_equity)}</p>
              <p className="text-xs text-gray-600">Total Equity</p>
            </div>
            <div className="p-3 bg-purple-50 rounded text-center">
              <p className="text-xl font-bold text-purple-700">{aiAnalysis.metrics?.current_ratio}</p>
              <p className="text-xs text-gray-600">Current Ratio</p>
            </div>
            <div className="p-3 bg-orange-50 rounded text-center">
              <p className="text-xl font-bold text-orange-700">{aiAnalysis.metrics?.debt_equity_ratio}</p>
              <p className="text-xs text-gray-600">Debt/Equity</p>
            </div>
          </div>
          
          {/* AI Analysis Text */}
          {aiAnalysis.ai_analysis && (
            <div className="prose prose-sm max-w-none bg-gray-50 p-4 rounded-lg">
              <pre className="whitespace-pre-wrap text-sm text-gray-800">{aiAnalysis.ai_analysis}</pre>
            </div>
          )}
          
          {/* Basic Analysis Fallback */}
          {aiAnalysis.basic_analysis && !aiAnalysis.ai_analysis && (
            <div className="space-y-2">
              <p><strong>Liquidity:</strong> {aiAnalysis.basic_analysis.liquidity}</p>
              <p><strong>Leverage:</strong> {aiAnalysis.basic_analysis.leverage}</p>
              <p><strong>Balance:</strong> {aiAnalysis.basic_analysis.balance_check}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TallyImport;
