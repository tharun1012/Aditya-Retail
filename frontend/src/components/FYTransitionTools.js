import React, { useState, useEffect, useCallback, useRef } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Calendar, FileText, Edit, Search, RefreshCw, Save, AlertTriangle,
  Check, X, ChevronLeft, ChevronRight, Filter, Hash, Upload, Download,
  FileSpreadsheet, Plus, Scan, Camera, Sparkles, Eye, Trash2
} from 'lucide-react';
import { showToast } from '../utils/toast';

const FYTransitionTools = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [docTypeFilter, setDocTypeFilter] = useState('all');
  const [fyFilter, setFyFilter] = useState('all');
  const [convertedFilter, setConvertedFilter] = useState('all'); // 'all', 'converted', 'direct'
  const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0 });
  
  // Edit modal state
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [editForm, setEditForm] = useState({
    invoice_number: '',
    invoice_date: '',
    expected_delivery_date: '',
    edit_reason: ''
  });
  const [saving, setSaving] = useState(false);

  // Delete modal state
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [docToDelete, setDocToDelete] = useState(null);
  const [deleteReason, setDeleteReason] = useState('');
  const [deleting, setDeleting] = useState(false);
  
  // Import modal state
  const [showImportModal, setShowImportModal] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [importStore, setImportStore] = useState('HRBR');
  const [stores, setStores] = useState([]);
  const fileInputRef = useRef(null);
  
  // AI Scan modal state
  const [showScanModal, setShowScanModal] = useState(false);
  const [scanFile, setScanFile] = useState(null);
  const [scanDocType, setScanDocType] = useState('sales_order');
  const [scanFileQueue, setScanFileQueue] = useState([]);
  const [scanQueueIndex, setScanQueueIndex] = useState(0);
  const [scanResults, setScanResults] = useState([]);
  const [showBulkSummaryModal, setShowBulkSummaryModal] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [scanStore, setScanStore] = useState('HRBR');
  const [scannedData, setScannedData] = useState(null);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [savingScanned, setSavingScanned] = useState(false);
  const scanFileInputRef = useRef(null);
  
  // Duplicate finder state
  const [showDuplicatesModal, setShowDuplicatesModal] = useState(false);
  const [duplicates, setDuplicates] = useState([]);
  const [loadingDuplicates, setLoadingDuplicates] = useState(false);

  // Sequence counter state
  const [showCounterModal, setShowCounterModal] = useState(false);
  const [counterData, setCounterData] = useState([]);
  const [loadingCounters, setLoadingCounters] = useState(false);
  const [savingCounter, setSavingCounter] = useState(false);
  const [editingCounter, setEditingCounter] = useState(null);
  const [newCounterValue, setNewCounterValue] = useState('');

  const fetchDocuments = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        limit: pagination.limit,
        skip: (pagination.page - 1) * pagination.limit,
        ...(searchTerm && { search: searchTerm }),
        ...(docTypeFilter !== 'all' && { document_type: docTypeFilter })
      });

      const response = await fetch(`${BACKEND_URL}/api/invoices/offline/?${params}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        let docs = data.invoices || data.orders || [];
        
        // Filter by FY if selected
        if (fyFilter !== 'all') {
          const currentYear = new Date().getFullYear();
          docs = docs.filter(doc => {
            const docDate = new Date(doc.invoice_date || doc.created_at);
            const docYear = docDate.getFullYear();
            const docMonth = docDate.getMonth() + 1;
            
            if (fyFilter === 'current') {
              // Current FY: Apr 2026 onwards (assuming April start)
              return (docYear === currentYear && docMonth >= 4) || docYear > currentYear;
            } else {
              // Previous FY: Before Apr 2026
              return (docYear === currentYear && docMonth < 4) || docYear < currentYear;
            }
          });
        }
        
        // Filter by converted status
        if (convertedFilter === 'converted') {
          docs = docs.filter(doc => doc.converted_from_so || doc.original_so_number);
        } else if (convertedFilter === 'direct') {
          docs = docs.filter(doc => !doc.converted_from_so && !doc.original_so_number);
        }
        
        setDocuments(docs);
        setPagination(prev => ({
          ...prev,
          total: data.total || docs.length
        }));
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
      showToast.error('Failed to load documents');
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.limit, searchTerm, docTypeFilter, fyFilter, convertedFilter]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // Fetch stores for import
  useEffect(() => {
    const fetchStores = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/stores`);
        const data = await response.json();
        if (data.stores) {
          setStores(data.stores);
          if (data.stores.length > 0) {
            setImportStore(data.stores[0].code);
          }
        }
      } catch (error) {
        console.error('Error fetching stores:', error);
      }
    };
    fetchStores();
  }, []);

  // Fetch sequence counter data
  const fetchCounterData = async () => {
    setLoadingCounters(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/document-numbering/sync-from-highest-preview`);
      const data = await response.json();
      if (data.status === 'success') {
        setCounterData(data.stores || []);
      }
    } catch (error) {
      console.error('Error fetching counters:', error);
      showToast.error('Failed to load sequence counters');
    } finally {
      setLoadingCounters(false);
    }
  };

  // Update a specific counter
  const updateCounter = async (storeCode, docType, newValue) => {
    setSavingCounter(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/document-numbering/starting-number`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          store_code: storeCode,
          document_type: docType,
          starting_number: parseInt(newValue)
        })
      });
      const data = await response.json();
      if (data.status === 'success') {
        showToast.success(`Counter updated to ${newValue}`);
        setEditingCounter(null);
        setNewCounterValue('');
        fetchCounterData(); // Refresh data
      } else {
        showToast.error(data.detail || 'Failed to update counter');
      }
    } catch (error) {
      console.error('Error updating counter:', error);
      showToast.error('Failed to update counter');
    } finally {
      setSavingCounter(false);
    }
  };

  // Sync all counters from highest
  const syncAllCounters = async () => {
    setSavingCounter(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/document-numbering/sync-from-highest`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.status === 'success') {
        showToast.success(data.message || 'Counters synced successfully');
        fetchCounterData(); // Refresh data
      } else {
        showToast.error(data.detail || 'Failed to sync counters');
      }
    } catch (error) {
      console.error('Error syncing counters:', error);
      showToast.error('Failed to sync counters');
    } finally {
      setSavingCounter(false);
    }
  };

  const downloadTemplate = () => {
    window.open(`${BACKEND_URL}/api/tally-import/templates/sales-orders`, '_blank');
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      const validTypes = ['.csv', '.xlsx', '.xls'];
      const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      if (!validTypes.includes(fileExt)) {
        showToast.error('Please upload a CSV or Excel file');
        return;
      }
      setImportFile(file);
    }
  };

  const handleImport = async () => {
    if (!importFile) {
      showToast.error('Please select a file first');
      return;
    }

    setImporting(true);
    try {
      const formData = new FormData();
      formData.append('file', importFile);
      formData.append('default_store_code', importStore);
      formData.append('update_existing', 'false');

      const response = await fetch(`${BACKEND_URL}/api/tally-import/sales-orders`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (data.status === 'success') {
        showToast.success(`Imported ${data.result.imported} Sales Orders successfully!`);
        setShowImportModal(false);
        setImportFile(null);
        fetchDocuments();
        
        if (data.result.errors && data.result.errors.length > 0) {
          console.log('Import warnings:', data.result.errors);
          showToast.error(`${data.result.skipped} records skipped. Check console for details.`);
        }
      } else {
        showToast.error(data.detail || 'Import failed');
      }
    } catch (error) {
      console.error('Import error:', error);
      showToast.error('Failed to import file');
    } finally {
      setImporting(false);
    }
  };

  // AI Scan functions
  const handleScanFileSelect = (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;
    const validTypes = ['.pdf', '.png', '.jpg', '.jpeg', '.webp'];
    const invalidFiles = files.filter(f => {
      const ext = f.name.toLowerCase().substring(f.name.lastIndexOf('.'));
      return !validTypes.includes(ext);
    });
    if (invalidFiles.length > 0) {
      showToast.error(`Unsupported file type: ${invalidFiles.map(f => f.name).join(', ')}. Please upload PDF, PNG, JPG, or WEBP.`);
      return;
    }
    setScanFile(files[0]);
    setScanFileQueue(files);
  };

  const moveQueuedFile = (index, direction) => {
    setScanFileQueue(prev => {
      const arr = [...prev];
      const newIndex = index + direction;
      if (newIndex < 0 || newIndex >= arr.length) return arr;
      [arr[index], arr[newIndex]] = [arr[newIndex], arr[index]];
      return arr;
    });
  };

  const sortQueuedFilesByName = () => {
    setScanFileQueue(prev => {
      const arr = [...prev];
      arr.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: 'base' }));
      return arr;
    });
  };

  const scanQueueFileAt = async (index, queue) => {
    if (index >= queue.length) {
      setShowReviewModal(false);
      setScannedData(null);
      setScanFile(null);
      setScanFileQueue([]);
      setScanQueueIndex(0);
      setShowBulkSummaryModal(true);
      fetchDocuments();
      return;
    }

    setScanQueueIndex(index);
    setScanning(true);
    const file = queue[index];
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('store_code', scanStore);

      const response = await fetch(`${BACKEND_URL}/api/tally-import/scan-sales-order`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (data.status === 'success') {
        setScannedData(data.extracted_data);
        setShowReviewModal(true);
      } else {
        setScanResults(prev => [...prev, { fileName: file.name, status: 'failed', message: data.detail || data.message || 'Scan failed' }]);
        await scanQueueFileAt(index + 1, queue);
      }
    } catch (error) {
      console.error('Scan error:', error);
      setScanResults(prev => [...prev, { fileName: file.name, status: 'failed', message: 'Failed to scan file' }]);
      await scanQueueFileAt(index + 1, queue);
    } finally {
      setScanning(false);
    }
  };

  const handleScanSO = async () => {
    if (!scanFileQueue || scanFileQueue.length === 0) {
      showToast.error('Please select at least one file');
      return;
    }
    setScanResults([]);
    setShowScanModal(false);
    await scanQueueFileAt(0, scanFileQueue);
  };

  const handleSkipScannedFile = async () => {
    const currentFile = scanFileQueue[scanQueueIndex];
    setScanResults(prev => [...prev, { fileName: currentFile?.name || 'Unknown file', status: 'skipped', message: 'Skipped by user' }]);
    setShowReviewModal(false);
    setScannedData(null);
    await scanQueueFileAt(scanQueueIndex + 1, scanFileQueue);
  };

  const handleSaveScannedSO = async () => {
    if (!scannedData || !scannedData.so_number) {
      showToast.error('SO/Invoice number is required');
      return;
    }

    setSavingScanned(true);
    try {
      const saveEndpoint = scanDocType === 'invoice' ? 'save-scanned-invoice-store' : 'save-scanned-so';
      const response = await fetch(`${BACKEND_URL}/api/tally-import/${saveEndpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scannedData)
      });

      const data = await response.json();
      const currentFile = scanFileQueue[scanQueueIndex];

      if (data.status === 'success') {
        const label = scanDocType === 'invoice' ? 'Sales Invoice' : 'Sales Order';
        setScanResults(prev => [...prev, { fileName: currentFile?.name || data.so.so_number, status: 'success', docNumber: data.so.so_number, message: `${label} created` }]);
        setShowReviewModal(false);
        setScannedData(null);
        if (scanFileQueue.length > 0) {
          await scanQueueFileAt(scanQueueIndex + 1, scanFileQueue);
        } else {
          setScanFile(null);
          fetchDocuments();
        }
      } else {
        showToast.error(data.detail || 'Failed to save');
      }
    } catch (error) {
      console.error('Save error:', error);
      showToast.error('Failed to save document');
    } finally {
      setSavingScanned(false);
    }
  };

  const updateScannedData = (field, value) => {
    setScannedData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const updateScannedCustomer = (field, value) => {
    setScannedData(prev => ({
      ...prev,
      customer: {
        ...prev.customer,
        [field]: value
      }
    }));
  };

  const updateScannedItem = (index, field, value) => {
    setScannedData(prev => {
      const newItems = [...prev.items];
      newItems[index] = { ...newItems[index], [field]: value };
      return { ...prev, items: newItems };
    });
  };

  const openDeleteModal = (doc) => {
    setDocToDelete(doc);
    setDeleteReason('');
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    if (!deleteReason.trim()) {
      showToast.error('Please provide a reason for this deletion');
      return;
    }

    setDeleting(true);
    try {
      const adminUser = JSON.parse(localStorage.getItem('adminUser') || localStorage.getItem('admin_user') || '{}');

      const response = await fetch(`${BACKEND_URL}/api/invoices/offline/admin/delete-by-ids`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('adminToken')}` },
        body: JSON.stringify({
          ids: [docToDelete.id],
          confirm: 'DELETE',
          deleted_by: adminUser.email || 'admin',
          delete_reason: deleteReason
        })
      });

      const data = await response.json();

      if (data.status === 'success' && data.deleted > 0) {
        showToast.success(`${docToDelete.invoice_number} deleted successfully`);
        setShowDeleteModal(false);
        setDocToDelete(null);
        fetchDocuments();
      } else {
        showToast.error(data.detail || 'Failed to delete document');
      }
    } catch (error) {
      console.error('Error deleting document:', error);
      showToast.error('Failed to delete document');
    } finally {
      setDeleting(false);
    }
  };

  const openEditModal = (doc) => {
    setSelectedDoc(doc);
    setEditForm({
      invoice_number: doc.invoice_number || '',
      invoice_date: doc.invoice_date || '',
      expected_delivery_date: doc.expected_delivery_date || '',
      edit_reason: ''
    });
    setShowEditModal(true);
  };

  const handleSaveEdit = async () => {
    if (!editForm.edit_reason.trim()) {
      showToast.error('Please provide a reason for this edit');
      return;
    }

    setSaving(true);
    try {
      const adminUser = JSON.parse(localStorage.getItem('adminUser') || localStorage.getItem('admin_user') || '{}');
      
      const response = await fetch(`${BACKEND_URL}/api/invoices/offline/admin/edit-document/${selectedDoc.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('adminToken')}` },
        body: JSON.stringify({
          invoice_number: editForm.invoice_number !== selectedDoc.invoice_number ? editForm.invoice_number : null,
          invoice_date: editForm.invoice_date !== selectedDoc.invoice_date ? editForm.invoice_date : null,
          expected_delivery_date: editForm.expected_delivery_date !== selectedDoc.expected_delivery_date ? editForm.expected_delivery_date : null,
          edited_by: adminUser.email || 'admin',
          edit_reason: editForm.edit_reason
        })
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success('Document updated successfully');
        setShowEditModal(false);
        fetchDocuments();
      } else {
        showToast.error(data.detail || 'Failed to update document');
      }
    } catch (error) {
      console.error('Error updating document:', error);
      showToast.error('Failed to update document');
    } finally {
      setSaving(false);
    }
  };

  const getFYFromDate = (dateStr) => {
    if (!dateStr) return 'Unknown';
    const date = new Date(dateStr);
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    
    // Indian FY: Apr-Mar
    if (month >= 4) {
      return `FY ${year}-${(year + 1).toString().slice(-2)}`;
    } else {
      return `FY ${year - 1}-${year.toString().slice(-2)}`;
    }
  };

  const getDocTypeBadge = (type) => {
    const badges = {
      'sales_order': { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Sales Order' },
      'invoice': { bg: 'bg-green-100', text: 'text-green-700', label: 'Invoice' },
      'quotation': { bg: 'bg-purple-100', text: 'text-purple-700', label: 'Quotation' }
    };
    const badge = badges[type] || { bg: 'bg-gray-100', text: 'text-gray-700', label: type };
    return (
      <span className={`px-2 py-0.5 rounded text-xs font-medium ${badge.bg} ${badge.text}`}>
        {badge.label}
      </span>
    );
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <Calendar className="w-6 h-6 text-indigo-600" />
            Financial Year Transition Tools
          </h1>
          <p className="text-gray-600 mt-1">
            Edit document numbers and dates for FY transition. All changes are logged for audit.
          </p>
        </div>

        {/* Instructions Banner */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5" />
            <div>
              <h3 className="font-semibold text-amber-800">Important Notes for FY Transition</h3>
              <ul className="text-sm text-amber-700 mt-2 space-y-1">
                <li>• You can edit SO/Invoice numbers to match your old FY format</li>
                <li>• You can backdate documents to previous FY dates</li>
                <li>• When converting old SOs to Invoices, the Invoice will use the NEW FY numbering</li>
                <li>• All edits are logged with timestamp, user, and reason for audit compliance</li>
                <li>• <strong>AI Scan:</strong> Upload a PDF/image of old SO - AI will extract all details automatically</li>
                <li>• <strong>Bulk Import:</strong> Use Excel/CSV for multiple SOs at once</li>
              </ul>
            </div>
          </div>
        </div>

        {/* AI Scan Action - Primary */}
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl p-5 shadow-lg mb-6 text-white">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-white/20 rounded-xl">
                <Sparkles className="w-8 h-8" />
              </div>
              <div>
                <h3 className="font-semibold text-lg flex items-center gap-2">
                  AI-Powered Sales Order Scanner
                </h3>
                <p className="text-purple-100 mt-1">
                  Upload a PDF or photo of your old SO - AI will read and create the entry automatically
                </p>
              </div>
            </div>
            <button
              onClick={() => setShowScanModal(true)}
              className="px-6 py-3 bg-white text-purple-700 rounded-lg hover:bg-purple-50 flex items-center gap-2 font-medium shadow-md"
            >
              <Scan className="w-5 h-5" />
              Scan Sales Order
            </button>
          </div>
        </div>

        {/* Import Actions */}
        <div className="bg-white rounded-xl p-4 shadow-sm mb-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h3 className="font-medium text-gray-800 flex items-center gap-2">
                <FileSpreadsheet className="w-5 h-5 text-green-600" />
                Bulk Import Old FY Sales Orders
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                Import multiple SOs from previous FY using Excel/CSV with custom numbering
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={downloadTemplate}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2 text-gray-700"
              >
                <Download className="w-4 h-4" />
                Download Template
              </button>
              <button
                onClick={() => setShowImportModal(true)}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
              >
                <Upload className="w-4 h-4" />
                Import Sales Orders
              </button>
            </div>
          </div>
        </div>

        {/* Find Duplicates Action */}
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 shadow-sm mb-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h3 className="font-medium text-red-800 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-red-600" />
                Find & Fix Duplicate Invoice Numbers
              </h3>
              <p className="text-sm text-red-600 mt-1">
                Identify invoices with duplicate numbers and edit them to have unique numbers
              </p>
            </div>
            <button
              onClick={async () => {
                setLoadingDuplicates(true);
                try {
                  const response = await fetch(`${BACKEND_URL}/api/invoices/offline/admin/find-duplicates`);
                  const data = await response.json();
                  if (data.status === 'success') {
                    setDuplicates(data.duplicates || []);
                    setShowDuplicatesModal(true);
                    if (data.duplicates?.length === 0) {
                      showToast.success('No duplicate invoice numbers found!');
                    }
                  } else {
                    showToast.error(data.detail || 'Failed to find duplicates');
                  }
                } catch (error) {
                  console.error('Error finding duplicates:', error);
                  showToast.error('Failed to find duplicates');
                } finally {
                  setLoadingDuplicates(false);
                }
              }}
              disabled={loadingDuplicates}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2 disabled:opacity-50"
            >
              {loadingDuplicates ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              Find Duplicates
            </button>
          </div>
        </div>

        {/* Sequence Counter Settings */}
        <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-4 shadow-sm mb-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h3 className="font-medium text-indigo-800 flex items-center gap-2">
                <Hash className="w-5 h-5 text-indigo-600" />
                Document Sequence Counters
              </h3>
              <p className="text-sm text-indigo-600 mt-1">
                Set the next document number for each store. Use after editing invoice/SO numbers.
              </p>
            </div>
            <button
              onClick={() => {
                fetchCounterData();
                setShowCounterModal(true);
              }}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
            >
              <Hash className="w-4 h-4" />
              Manage Counters
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl p-4 shadow-sm mb-6">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by document number, customer..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
            
            <select
              value={docTypeFilter}
              onChange={(e) => setDocTypeFilter(e.target.value)}
              className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Document Types</option>
              <option value="sales_order">Sales Orders Only</option>
              <option value="invoice">Invoices Only</option>
              <option value="quotation">Quotations Only</option>
            </select>
            
            <select
              value={fyFilter}
              onChange={(e) => setFyFilter(e.target.value)}
              className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Financial Years</option>
              <option value="previous">Previous FY (Before Apr 2026)</option>
              <option value="current">Current FY (Apr 2026 onwards)</option>
            </select>
            
            <select
              value={convertedFilter}
              onChange={(e) => setConvertedFilter(e.target.value)}
              className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 bg-orange-50"
            >
              <option value="all">All Invoices</option>
              <option value="converted">Converted from SO</option>
              <option value="direct">Direct Invoices</option>
            </select>
            
            <button
              onClick={fetchDocuments}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>

        {/* Documents Table */}
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin text-indigo-600" />
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>No documents found matching your criteria</p>
            </div>
          ) : (
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Document #</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">FY</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Hash className="w-4 h-4 text-gray-400" />
                        <span className="font-medium text-gray-900">{doc.invoice_number}</span>
                        {doc.converted_from_so && (
                          <span className="px-1.5 py-0.5 bg-orange-100 text-orange-700 rounded text-xs">
                            from SO
                          </span>
                        )}
                        {doc.original_so_number && (
                          <span className="text-xs text-gray-400" title={`Original SO: ${doc.original_so_number}`}>
                            ← {doc.original_so_number}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      {getDocTypeBadge(doc.document_type)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {doc.invoice_date || doc.created_at?.split('T')[0] || '-'}
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded text-xs font-medium">
                        {getFYFromDate(doc.invoice_date || doc.created_at)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {doc.customer?.name || '-'}
                    </td>
                    <td className="px-4 py-3 text-right font-medium text-gray-900">
                      ₹{(doc.total_amount || 0).toLocaleString('en-IN')}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        doc.status === 'delivered' || doc.status === 'confirmed' 
                          ? 'bg-green-100 text-green-700' 
                          : doc.status === 'pending_delivery' 
                            ? 'bg-yellow-100 text-yellow-700'
                            : 'bg-gray-100 text-gray-700'
                      }`}>
                        {doc.status?.replace(/_/g, ' ') || 'Unknown'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <div className="flex items-center gap-2 justify-center">
                        <button
                          onClick={() => openEditModal(doc)}
                          className="px-3 py-1.5 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700 flex items-center gap-1"
                        >
                          <Edit className="w-3 h-3" />
                          Edit
                        </button>
                        <button
                          onClick={() => openDeleteModal(doc)}
                          className="px-3 py-1.5 bg-red-600 text-white text-sm rounded hover:bg-red-700 flex items-center gap-1"
                        >
                          <Trash2 className="w-3 h-3" />
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          
          {/* Pagination */}
          {pagination.total > pagination.limit && (
            <div className="flex items-center justify-between px-4 py-3 border-t bg-gray-50">
              <span className="text-sm text-gray-600">
                Showing {((pagination.page - 1) * pagination.limit) + 1} to {Math.min(pagination.page * pagination.limit, pagination.total)} of {pagination.total}
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPagination(p => ({ ...p, page: p.page - 1 }))}
                  disabled={pagination.page === 1}
                  className="p-2 border rounded hover:bg-gray-100 disabled:opacity-50"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="px-4 py-2 text-sm">Page {pagination.page}</span>
                <button
                  onClick={() => setPagination(p => ({ ...p, page: p.page + 1 }))}
                  disabled={pagination.page * pagination.limit >= pagination.total}
                  className="p-2 border rounded hover:bg-gray-100 disabled:opacity-50"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Edit Modal */}
        {showEditModal && selectedDoc && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl w-full max-w-lg shadow-2xl">
              <div className="p-6 border-b flex items-center justify-between">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  <Edit className="w-5 h-5 text-indigo-600" />
                  Edit Document Number & Date
                </h2>
                <button onClick={() => setShowEditModal(false)} className="text-gray-400 hover:text-gray-600">
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="p-6 space-y-4">
                {/* Current Values */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500 mb-2">Current Values:</p>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div><span className="font-medium">Number:</span> {selectedDoc.invoice_number}</div>
                    <div><span className="font-medium">Date:</span> {selectedDoc.invoice_date || '-'}</div>
                    <div><span className="font-medium">Type:</span> {selectedDoc.document_type}</div>
                    <div><span className="font-medium">FY:</span> {getFYFromDate(selectedDoc.invoice_date)}</div>
                  </div>
                </div>

                {/* Edit Fields */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Document Number
                  </label>
                  <input
                    type="text"
                    value={editForm.invoice_number}
                    onChange={(e) => setEditForm({ ...editForm, invoice_number: e.target.value })}
                    placeholder="e.g., HRBR-SO-2025-0045"
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Document Date
                  </label>
                  <input
                    type="date"
                    value={editForm.invoice_date}
                    onChange={(e) => setEditForm({ ...editForm, invoice_date: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                {selectedDoc.document_type === 'sales_order' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Expected Delivery Date
                    </label>
                    <input
                      type="date"
                      value={editForm.expected_delivery_date}
                      onChange={(e) => setEditForm({ ...editForm, expected_delivery_date: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Reason for Edit <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    value={editForm.edit_reason}
                    onChange={(e) => setEditForm({ ...editForm, edit_reason: e.target.value })}
                    placeholder="e.g., FY 2025-26 transition - updating to old FY number format"
                    rows={2}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">Required for audit compliance</p>
                </div>
              </div>

              <div className="p-6 border-t flex justify-end gap-3">
                <button
                  onClick={() => setShowEditModal(false)}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveEdit}
                  disabled={saving || !editForm.edit_reason.trim()}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {saving ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4" />
                      Save Changes
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {showDeleteModal && docToDelete && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl max-w-md w-full">
              <div className="flex items-center justify-between p-5 border-b">
                <h3 className="text-lg font-bold flex items-center gap-2 text-red-600">
                  <Trash2 className="w-5 h-5" />
                  Delete Document
                </h3>
                <button onClick={() => setShowDeleteModal(false)} className="text-gray-400 hover:text-gray-600">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="p-5 space-y-4">
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-800">
                  This will permanently delete <strong>{docToDelete.invoice_number}</strong> ({docToDelete.customer?.name || 'Unknown customer'}, ₹{(docToDelete.total_amount || 0).toLocaleString('en-IN')}). This cannot be undone.
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Reason for Deletion <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    value={deleteReason}
                    onChange={(e) => setDeleteReason(e.target.value)}
                    rows={3}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    placeholder="e.g. Duplicate entry, test data, incorrect entry"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 p-5 border-t">
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg text-sm"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmDelete}
                  disabled={deleting}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {deleting ? 'Deleting...' : (<><Trash2 className="w-4 h-4" /> Delete Permanently</>)}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Import Modal */}
        {showImportModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl w-full max-w-lg shadow-2xl">
              <div className="p-6 border-b flex items-center justify-between">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  <Upload className="w-5 h-5 text-green-600" />
                  Import Sales Orders from Excel/CSV
                </h2>
                <button onClick={() => setShowImportModal(false)} className="text-gray-400 hover:text-gray-600">
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="p-6 space-y-4">
                {/* Instructions */}
                <div className="bg-blue-50 rounded-lg p-4 text-sm text-blue-800">
                  <p className="font-medium mb-2">How to use:</p>
                  <ol className="list-decimal list-inside space-y-1">
                    <li>Download the template using the button above</li>
                    <li>Fill in your old FY Sales Orders (SO numbers, dates, etc.)</li>
                    <li>The <code className="bg-blue-100 px-1 rounded">so_number</code> column will be used as-is (no auto-generation)</li>
                    <li>The <code className="bg-blue-100 px-1 rounded">so_date</code> can be any date (backdating supported)</li>
                    <li>Use <code className="bg-blue-100 px-1 rounded">store_code</code> column to assign to different stores</li>
                  </ol>
                </div>

                {/* Store Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Default Store (if not specified in file)
                  </label>
                  <select
                    value={importStore}
                    onChange={(e) => setImportStore(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                  >
                    {stores.map(store => (
                      <option key={store.code} value={store.code}>
                        {store.name} ({store.code})
                      </option>
                    ))}
                  </select>
                </div>

                {/* File Upload */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Select File
                  </label>
                  <input
                    type="file"
                    ref={fileInputRef}
                    accept=".csv,.xlsx,.xls"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <div 
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-green-500 hover:bg-green-50 transition-colors"
                  >
                    {importFile ? (
                      <div className="flex items-center justify-center gap-2 text-green-700">
                        <FileSpreadsheet className="w-6 h-6" />
                        <span className="font-medium">{importFile.name}</span>
                        <button 
                          onClick={(e) => { e.stopPropagation(); setImportFile(null); }}
                          className="ml-2 text-red-500 hover:text-red-700"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <>
                        <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                        <p className="text-gray-600">Click to select CSV or Excel file</p>
                        <p className="text-xs text-gray-400 mt-1">Supported: .csv, .xlsx, .xls</p>
                      </>
                    )}
                  </div>
                </div>
              </div>

              <div className="p-6 border-t flex justify-end gap-3">
                <button
                  onClick={() => { setShowImportModal(false); setImportFile(null); }}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleImport}
                  disabled={importing || !importFile}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {importing ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Importing...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" />
                      Import Sales Orders
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* AI Scan Modal */}
        {showScanModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl w-full max-w-lg shadow-2xl">
              <div className="p-6 border-b flex items-center justify-between bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-t-xl">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  <Sparkles className="w-5 h-5" />
                  AI {scanDocType === 'invoice' ? 'Sales Invoice' : 'Sales Order'} Scanner
                </h2>
                <button onClick={() => { setShowScanModal(false); setScanFile(null); }} className="text-white/80 hover:text-white">
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="p-6 space-y-4">
                {/* Instructions */}
                <div className="bg-purple-50 rounded-lg p-4 text-sm text-purple-800">
                  <p className="font-medium mb-2">How AI Scan Works:</p>
                  <ol className="list-decimal list-inside space-y-1">
                    <li>Upload a PDF or photo of your old Sales Order</li>
                    <li>AI will read and extract: SO number, date, customer, items, amounts</li>
                    <li>Review and edit the extracted data</li>
                    <li>Save to create the SO entry under the selected store</li>
                  </ol>
                </div>

                {/* Document Type Toggle */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Document Type
                  </label>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => setScanDocType('sales_order')}
                      className={`flex-1 px-3 py-2 rounded-lg border text-sm font-medium ${scanDocType === 'sales_order' ? 'bg-purple-600 text-white border-purple-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                    >
                      Sales Order
                    </button>
                    <button
                      type="button"
                      onClick={() => setScanDocType('invoice')}
                      className={`flex-1 px-3 py-2 rounded-lg border text-sm font-medium ${scanDocType === 'invoice' ? 'bg-purple-600 text-white border-purple-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                    >
                      Sales Invoice
                    </button>
                  </div>
                </div>

                {/* Store Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Assign to Store
                  </label>
                  <select
                    value={scanStore}
                    onChange={(e) => setScanStore(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                  >
                    {stores.map(store => (
                      <option key={store.code} value={store.code}>
                        {store.name} ({store.code})
                      </option>
                    ))}
                  </select>
                </div>

                {/* File Upload */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Upload Document(s) — select multiple to bulk scan
                  </label>
                  <input
                    type="file"
                    ref={scanFileInputRef}
                    accept=".pdf,.png,.jpg,.jpeg,.webp"
                    onChange={handleScanFileSelect}
                    className="hidden"
                    multiple
                  />
                  <div 
                    onClick={() => scanFileInputRef.current?.click()}
                    className="border-2 border-dashed border-purple-300 rounded-lg p-6 text-center cursor-pointer hover:border-purple-500 hover:bg-purple-50 transition-colors"
                  >
                    {scanFileQueue && scanFileQueue.length > 0 ? (
                      <div className="text-purple-700">
                        <div className="flex items-center justify-center gap-2">
                          <Camera className="w-6 h-6" />
                          <span className="font-medium">
                            {scanFileQueue.length === 1 ? scanFileQueue[0].name : `${scanFileQueue.length} files selected`}
                          </span>
                          <button 
                            onClick={(e) => { e.stopPropagation(); setScanFile(null); setScanFileQueue([]); }}
                            className="ml-2 text-red-500 hover:text-red-700"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                        {scanFileQueue.length > 1 && (
                          <div className="mt-2 text-xs text-gray-600 text-left max-h-40 overflow-y-auto space-y-1" onClick={(e) => e.stopPropagation()}>
                            <div className="flex items-center justify-between mb-1">
                              <p className="text-gray-400">Browsers don't always keep your selection order — use the arrows or sort:</p>
                              <button
                                type="button"
                                onClick={sortQueuedFilesByName}
                                className="text-purple-600 hover:text-purple-800 font-medium whitespace-nowrap ml-2"
                              >
                                Sort by filename
                              </button>
                            </div>
                            {scanFileQueue.map((f, i) => (
                              <div key={i} className="flex items-center justify-between bg-gray-50 rounded px-2 py-1">
                                <span className="truncate flex-1">{i + 1}. {f.name}</span>
                                <div className="flex items-center gap-1 ml-2">
                                  <button
                                    type="button"
                                    onClick={() => moveQueuedFile(i, -1)}
                                    disabled={i === 0}
                                    className="p-1 text-gray-400 hover:text-purple-600 disabled:opacity-30 disabled:cursor-not-allowed"
                                    title="Move up"
                                  >
                                    ▲
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => moveQueuedFile(i, 1)}
                                    disabled={i === scanFileQueue.length - 1}
                                    className="p-1 text-gray-400 hover:text-purple-600 disabled:opacity-30 disabled:cursor-not-allowed"
                                    title="Move down"
                                  >
                                    ▼
                                  </button>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ) : (
                      <>
                        <Camera className="w-10 h-10 mx-auto mb-2 text-purple-400" />
                        <p className="text-gray-600">Click to upload one or more PDFs/images</p>
                        <p className="text-xs text-gray-400 mt-1">Supported: PDF, PNG, JPG, WEBP</p>
                      </>
                    )}
                  </div>
                </div>
              </div>

              <div className="p-6 border-t flex justify-end gap-3">
                <button
                  onClick={() => { setShowScanModal(false); setScanFile(null); }}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleScanSO}
                  disabled={scanning || !scanFile}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {scanning ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Scanning with AI...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Scan Document
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Review Scanned Data Modal */}
        {showReviewModal && scannedData && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
            <div className="bg-white rounded-xl w-full max-w-3xl shadow-2xl my-8">
              <div className="p-6 border-b flex items-center justify-between bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-t-xl">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  <Eye className="w-5 h-5" />
                  Review Extracted Data ({scanDocType === 'invoice' ? 'Sales Invoice' : 'Sales Order'})
                </h2>
                <button onClick={() => { setShowReviewModal(false); setScannedData(null); setScanFileQueue([]); setScanQueueIndex(0); }} className="text-white/80 hover:text-white">
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
                {/* SO Details */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{scanDocType === 'invoice' ? 'Invoice Number' : 'SO Number'} *</label>
                    <input
                      type="text"
                      value={scannedData.so_number || ''}
                      onChange={(e) => updateScannedData('so_number', e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{scanDocType === 'invoice' ? 'Invoice Date' : 'SO Date'}</label>
                    <input
                      type="date"
                      value={scannedData.so_date || ''}
                      onChange={(e) => updateScannedData('so_date', e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Store</label>
                    <select
                      value={scannedData.store_code || ''}
                      onChange={(e) => updateScannedData('store_code', e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                    >
                      {stores.map(store => (
                        <option key={store.code} value={store.code}>{store.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Expected Delivery</label>
                    <input
                      type="date"
                      value={scannedData.expected_delivery_date || ''}
                      onChange={(e) => updateScannedData('expected_delivery_date', e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                </div>

                {/* Customer Details */}
                <div>
                  <h3 className="font-medium text-gray-800 mb-3">Customer Details</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">Name</label>
                      <input
                        type="text"
                        value={scannedData.customer?.name || ''}
                        onChange={(e) => updateScannedCustomer('name', e.target.value)}
                        className="w-full px-3 py-2 border rounded-lg text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">Phone</label>
                      <input
                        type="text"
                        value={scannedData.customer?.phone || ''}
                        onChange={(e) => updateScannedCustomer('phone', e.target.value)}
                        className="w-full px-3 py-2 border rounded-lg text-sm"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-sm text-gray-600 mb-1">Address</label>
                      <input
                        type="text"
                        value={scannedData.customer?.billing_address || ''}
                        onChange={(e) => updateScannedCustomer('billing_address', e.target.value)}
                        className="w-full px-3 py-2 border rounded-lg text-sm"
                      />
                    </div>
                  </div>
                </div>

                {/* Items */}
                <div>
                  <h3 className="font-medium text-gray-800 mb-3">Items ({scannedData.items?.length || 0})</h3>
                  <div className="space-y-3">
                    {scannedData.items?.map((item, idx) => (
                      <div key={idx} className="bg-gray-50 rounded-lg p-3">
                        <div className="grid grid-cols-4 gap-2">
                          <div className="col-span-2">
                            <label className="block text-xs text-gray-500 mb-1">Product</label>
                            <input
                              type="text"
                              value={item.product_name || ''}
                              onChange={(e) => updateScannedItem(idx, 'product_name', e.target.value)}
                              className="w-full px-2 py-1 border rounded text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-gray-500 mb-1">Qty</label>
                            <input
                              type="number"
                              value={item.quantity || 0}
                              onChange={(e) => updateScannedItem(idx, 'quantity', parseInt(e.target.value) || 0)}
                              className="w-full px-2 py-1 border rounded text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-gray-500 mb-1">Unit Price</label>
                            <input
                              type="number"
                              value={item.unit_price || 0}
                              onChange={(e) => updateScannedItem(idx, 'unit_price', parseFloat(e.target.value) || 0)}
                              className="w-full px-2 py-1 border rounded text-sm"
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Totals */}
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Subtotal:</span>
                      <span className="ml-2 font-medium">₹{(scannedData.subtotal || 0).toLocaleString('en-IN')}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Tax:</span>
                      <span className="ml-2 font-medium">₹{(scannedData.total_tax || 0).toLocaleString('en-IN')}</span>
                    </div>
                    <div>
                      <span className="text-gray-600 font-medium">Grand Total:</span>
                      <span className="ml-2 font-bold text-green-700">₹{(scannedData.grand_total || 0).toLocaleString('en-IN')}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-6 border-t flex justify-between items-center">
                <a 
                  href={scannedData.so_file_url ? `${BACKEND_URL}${scannedData.so_file_url}` : '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-purple-600 hover:underline flex items-center gap-1"
                >
                  <Eye className="w-4 h-4" />
                  View Original Document
                </a>
                <div className="flex items-center gap-3">
                  {scanFileQueue && scanFileQueue.length > 1 && (
                    <span className="text-sm text-gray-500 mr-2">
                      File {scanQueueIndex + 1} of {scanFileQueue.length}
                    </span>
                  )}
                  <button
                    onClick={handleSkipScannedFile}
                    className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                  >
                    {scanFileQueue && scanFileQueue.length > 1 ? 'Skip This File' : 'Cancel'}
                  </button>
                  <button
                    onClick={handleSaveScannedSO}
                    disabled={savingScanned || !scannedData.so_number}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                  >
                    {savingScanned ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4" />
                        {scanDocType === 'invoice' ? 'Create Sales Invoice' : 'Create Sales Order'}
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Bulk Scan Summary Modal */}
        {showBulkSummaryModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl w-full max-w-lg shadow-2xl">
              <div className="p-6 border-b flex items-center justify-between bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-t-xl">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  <Sparkles className="w-5 h-5" />
                  Bulk Scan Summary
                </h2>
                <button onClick={() => { setShowBulkSummaryModal(false); setScanResults([]); }} className="text-white/80 hover:text-white">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="p-6">
                <div className="mb-4 text-sm text-gray-600">
                  {scanResults.filter(r => r.status === 'success').length} created,{' '}
                  {scanResults.filter(r => r.status === 'skipped').length} skipped,{' '}
                  {scanResults.filter(r => r.status === 'failed').length} failed
                  {' '}out of {scanResults.length} file{scanResults.length !== 1 ? 's' : ''}
                </div>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {scanResults.map((r, i) => (
                    <div
                      key={i}
                      className={`p-3 rounded-lg text-sm flex items-start gap-2 ${
                        r.status === 'success' ? 'bg-green-50 text-green-800' :
                        r.status === 'skipped' ? 'bg-gray-50 text-gray-600' :
                        'bg-red-50 text-red-700'
                      }`}
                    >
                      <span className="font-medium">
                        {r.status === 'success' ? '✓' : r.status === 'skipped' ? '–' : '✗'}
                      </span>
                      <div>
                        <div className="font-medium">{r.fileName}</div>
                        <div className="text-xs opacity-80">
                          {r.docNumber ? `${r.message} — ${r.docNumber}` : r.message}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="p-6 border-t flex justify-end">
                <button
                  onClick={() => { setShowBulkSummaryModal(false); setScanResults([]); }}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Done
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Duplicates Modal */}
        {showDuplicatesModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
              <div className="p-6 border-b flex items-center justify-between bg-red-50">
                <div>
                  <h2 className="text-xl font-bold text-red-800 flex items-center gap-2">
                    <AlertTriangle className="w-6 h-6" />
                    Duplicate Invoice Numbers Found
                  </h2>
                  <p className="text-red-600 text-sm mt-1">
                    {duplicates.length} duplicate groups found. Click on an invoice to edit its number.
                  </p>
                </div>
                <button
                  onClick={() => setShowDuplicatesModal(false)}
                  className="p-2 hover:bg-red-100 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="p-6 overflow-y-auto max-h-[60vh]">
                {duplicates.length === 0 ? (
                  <div className="text-center py-8">
                    <Check className="w-16 h-16 text-green-500 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-green-700">No Duplicates Found!</h3>
                    <p className="text-gray-600 mt-2">All invoice numbers are unique.</p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {duplicates.map((group, idx) => (
                      <div key={idx} className="border border-red-200 rounded-lg overflow-hidden">
                        <div className="bg-red-100 px-4 py-3 flex items-center justify-between">
                          <span className="font-semibold text-red-800">
                            Invoice #: {group.invoice_number}
                          </span>
                          <span className="bg-red-600 text-white px-3 py-1 rounded-full text-sm">
                            {group.duplicate_count} duplicates
                          </span>
                        </div>
                        <div className="divide-y">
                          {group.documents.map((doc, docIdx) => (
                            <div key={doc.id} className="px-4 py-3 flex items-center justify-between hover:bg-gray-50">
                              <div>
                                <p className="font-medium">
                                  {doc.customer_name || 'N/A'}
                                  <span className="ml-2 text-sm text-gray-500">
                                    ({doc.document_type})
                                  </span>
                                </p>
                                <p className="text-sm text-gray-600">
                                  Store: {doc.store_code} | 
                                  Amount: ₹{(doc.total_amount || 0).toLocaleString()} | 
                                  Status: {doc.status} |
                                  Created: {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : 'N/A'}
                                </p>
                              </div>
                              <button
                                onClick={() => {
                                  // Find the full document and open edit modal
                                  setSelectedDoc(doc);
                                  setEditForm({
                                    invoice_number: doc.invoice_number,
                                    invoice_date: '',
                                    expected_delivery_date: '',
                                    edit_reason: 'Fixing duplicate invoice number'
                                  });
                                  setShowDuplicatesModal(false);
                                  setShowEditModal(true);
                                }}
                                className="px-3 py-1 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-1 text-sm"
                              >
                                <Edit className="w-4 h-4" />
                                Edit Number
                              </button>
                            </div>
                          ))}
                        </div>
                        <div className="bg-yellow-50 px-4 py-2 text-sm text-yellow-800">
                          <strong>Suggested fix:</strong> Change duplicates to {group.invoice_number.replace(/(\d+)/, (m) => String(parseInt(m) + 1).padStart(4, '0'))}, {group.invoice_number.replace(/(\d+)/, (m) => String(parseInt(m) + 2).padStart(4, '0'))}, etc.
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              <div className="p-4 border-t bg-gray-50 flex justify-end">
                <button
                  onClick={() => setShowDuplicatesModal(false)}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Sequence Counter Modal */}
        {showCounterModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
              <div className="p-4 border-b bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
                <h2 className="text-xl font-bold flex items-center gap-2">
                  <Hash className="w-6 h-6" />
                  Document Sequence Counters
                </h2>
                <p className="text-indigo-100 text-sm mt-1">
                  Set the next document number for Invoices, Sales Orders, Quotations & Delivery Challans
                </p>
              </div>
              
              <div className="p-4 max-h-[60vh] overflow-y-auto">
                {loadingCounters ? (
                  <div className="flex items-center justify-center py-8">
                    <RefreshCw className="w-8 h-8 animate-spin text-indigo-600" />
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Sync All Button */}
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-green-800">Auto-Sync from Highest Numbers</h4>
                        <p className="text-sm text-green-600">
                          Automatically set counters based on the highest document number found
                        </p>
                      </div>
                      <button
                        onClick={syncAllCounters}
                        disabled={savingCounter}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2 disabled:opacity-50"
                      >
                        {savingCounter ? (
                          <RefreshCw className="w-4 h-4 animate-spin" />
                        ) : (
                          <Sparkles className="w-4 h-4" />
                        )}
                        Auto-Sync All
                      </button>
                    </div>

                    {/* Store-wise counters */}
                    {counterData.map((store) => (
                      <div key={store.store_code} className="border rounded-lg overflow-hidden">
                        <div className="bg-gray-100 px-4 py-2 font-medium">
                          {store.store_name} ({store.store_code})
                        </div>
                        <div className="divide-y">
                          {store.documents.map((doc) => (
                            <div key={doc.type} className="px-4 py-3 flex items-center justify-between hover:bg-gray-50">
                              <div className="flex-1">
                                <p className="font-medium capitalize">{doc.type.replace('_', ' ')}</p>
                                <div className="text-sm text-gray-500 space-x-4">
                                  <span>Total Docs: {doc.total_docs}</span>
                                  {doc.highest_doc_number && (
                                    <span>Highest: <code className="bg-gray-100 px-1 rounded">{doc.highest_doc_number}</code></span>
                                  )}
                                </div>
                              </div>
                              <div className="flex items-center gap-4">
                                <div className="text-right">
                                  <p className="text-sm text-gray-500">Current Counter</p>
                                  <p className={`font-bold text-lg ${doc.needs_update ? 'text-orange-600' : 'text-green-600'}`}>
                                    {doc.current_counter}
                                  </p>
                                </div>
                                
                                {editingCounter === `${store.store_code}-${doc.type}` ? (
                                  <div className="flex items-center gap-2">
                                    <input
                                      type="number"
                                      value={newCounterValue}
                                      onChange={(e) => setNewCounterValue(e.target.value)}
                                      className="w-24 px-2 py-1 border rounded text-center"
                                      placeholder="New #"
                                      min="1"
                                    />
                                    <button
                                      onClick={() => updateCounter(store.store_code, doc.type, newCounterValue)}
                                      disabled={savingCounter || !newCounterValue}
                                      className="p-1 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                                    >
                                      {savingCounter ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                                    </button>
                                    <button
                                      onClick={() => {
                                        setEditingCounter(null);
                                        setNewCounterValue('');
                                      }}
                                      className="p-1 bg-gray-400 text-white rounded hover:bg-gray-500"
                                    >
                                      <X className="w-4 h-4" />
                                    </button>
                                  </div>
                                ) : (
                                  <button
                                    onClick={() => {
                                      setEditingCounter(`${store.store_code}-${doc.type}`);
                                      setNewCounterValue(doc.will_set_to.toString());
                                    }}
                                    className="px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 text-sm"
                                  >
                                    Edit
                                  </button>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}

                    {counterData.length === 0 && !loadingCounters && (
                      <div className="text-center py-8 text-gray-500">
                        No stores found
                      </div>
                    )}
                  </div>
                )}
              </div>
              
              <div className="p-4 border-t bg-gray-50 flex justify-between">
                <button
                  onClick={fetchCounterData}
                  disabled={loadingCounters}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 flex items-center gap-2"
                >
                  <RefreshCw className={`w-4 h-4 ${loadingCounters ? 'animate-spin' : ''}`} />
                  Refresh
                </button>
                <button
                  onClick={() => setShowCounterModal(false)}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FYTransitionTools;
