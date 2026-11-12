import React, { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Search, Filter, Edit, Save, X, ChevronLeft, ChevronRight, 
  FileText, Package, Truck, CreditCard, Store, Eye, Plus, Trash2,
  AlertTriangle, Check, RefreshCw, Hash, Download
} from 'lucide-react';
import { showToast } from '../utils/toast';

const DOC_TYPES = [
  { id: 'all', label: 'All Documents', icon: FileText },
  { id: 'sales_order', label: 'Sales Orders', icon: Package },
  { id: 'invoice', label: 'Invoices', icon: FileText },
];

const STATUS_OPTIONS = [
  'pending', 'confirmed', 'processing', 'ready_for_delivery', 
  'pending_delivery', 'partially_delivered', 'dispatched', 'delivered', 'cancelled', 'completed', 'converted'
];

const PAYMENT_STATUS_OPTIONS = ['pending', 'partial', 'paid', 'refunded'];

const StoreDocumentManager = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState('all');
  const [docTypeFilter, setDocTypeFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0, pages: 1 });

  // Edit modal
  const [showEditModal, setShowEditModal] = useState(false);
  const [editDoc, setEditDoc] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [editItems, setEditItems] = useState([]);
  const [saving, setSaving] = useState(false);
  const [activeEditTab, setActiveEditTab] = useState('details');
  const [products, setProducts] = useState([]);
  const [hsnCodes, setHsnCodes] = useState([]);
  const [productSearch, setProductSearch] = useState({});
  const [hsnSuggestions, setHsnSuggestions] = useState({});
  const [showAddProductModal, setShowAddProductModal] = useState(false);
  const [addProductForIndex, setAddProductForIndex] = useState(null);
  const [addProductLoading, setAddProductLoading] = useState(false);
  const [newProductHsnSuggestions, setNewProductHsnSuggestions] = useState([]);
  const [manualHsnMode, setManualHsnMode] = useState(false);
  const [manualHsnGstRate, setManualHsnGstRate] = useState(18);
  const [newProduct, setNewProduct] = useState({
    name: '', brand: '', model_number: '', price: 0, hsn_code: '',
    category: '', description: '', current_stock: 0
  });

  // View modal
  const [showViewModal, setShowViewModal] = useState(false);
  const [viewDoc, setViewDoc] = useState(null);

  // Fetch stores
  useEffect(() => {
    const fetchStores = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/stores`);
        const data = await response.json();
        if (data.stores) setStores(data.stores);
      } catch (e) {
        console.error('Error fetching stores:', e);
      }
    };
    fetchStores();
  }, []);

  // Fetch documents
  const fetchDocuments = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        limit: pagination.limit,
        page: pagination.page,
        ...(searchTerm && { search: searchTerm }),
        ...(docTypeFilter !== 'all' && { document_type: docTypeFilter }),
        ...(docTypeFilter === 'sales_order' && { include_converted: 'true' }),
        ...(selectedStore !== 'all' && { store_code: selectedStore }),
      });

      const response = await fetch(`${BACKEND_URL}/api/invoices/offline/?${params}`);
      const data = await response.json();

      if (data.status === 'success') {
        let docs = data.invoices || [];
        if (docTypeFilter === 'sales_order') {
          docs = docs.map(d => (d.document_type === 'invoice' && d.original_so_number)
            ? { ...d, _soView: true } : d);
        }
        if (statusFilter === 'converted') {
          docs = docs.filter(d => d._soView || d.status === 'completed' || d.converted_invoice_number);
        } else if (statusFilter !== 'all') {
          docs = docs.filter(d => d.status === statusFilter);
        }
        setDocuments(docs);
        setPagination(prev => ({
          ...prev,
          total: data.total || docs.length,
          pages: data.pages || Math.ceil((data.total || docs.length) / prev.limit)
        }));
      }
    } catch (error) {
      showToast.error('Failed to load documents');
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.limit, searchTerm, docTypeFilter, selectedStore, statusFilter]);

  useEffect(() => { fetchDocuments(); }, [fetchDocuments]);

  // Open edit modal
  const openEditModal = (doc) => {
    setEditDoc(doc);
    setEditForm({
      invoice_number: doc.invoice_number || '',
      invoice_date: (doc.invoice_date || doc.created_at || '').substring(0, 10),
      expected_delivery_date: (doc.expected_delivery_date || '').substring(0, 10),
      customer_name: doc.customer_name || doc.customer?.name || '',
      customer_phone: doc.customer_phone || doc.customer?.phone || '',
      customer_email: doc.customer_email || doc.customer?.email || '',
      customer_address: doc.customer_address || doc.customer?.address || '',
      payment_mode: doc.payment_mode || doc.payment_method || '',
      payment_status: doc.payment_status || 'pending',
      status: doc.status || 'pending',
      notes: doc.notes || '',
      discount: doc.discount_percentage || doc.discount || 0,
      delivery_charges: doc.delivery_charges || 0,
      round_off: doc.round_off || 0,
      edit_reason: ''
    });
    setEditItems((doc.items || []).map((item, idx) => ({
      _key: idx,
      product_id: item.product_id || '',
      product_name: item.product_name || item.name || '',
      model_number: item.model_number || '',
      hsn_code: item.hsn_code || '',
      quantity: item.quantity || 1,
      rate: item.unit_price || item.rate || 0,
      tax_rate: item.gst_rate || item.tax_rate || 18,
      discount: item.discount || 0,
      has_serial_tracking: !!item.has_serial_tracking || (item.serial_numbers || []).length > 0,
      serial_numbers: item.serial_numbers || [],
      available_serials: [],
      manual_serials: (item.serial_numbers || []).join(', ')
    })));
    setProductSearch({});
    setHsnSuggestions({});
    loadEditLookups();
    setActiveEditTab('details');
    setShowEditModal(true);
  };

  // Save edits
  const handleSave = async () => {
    if (!editForm.edit_reason?.trim()) {
      showToast.error('Please provide a reason for editing');
      return;
    }
    setSaving(true);
    try {
      // Build items payload
      const itemsPayload = editItems.map(item => ({
        product_id: item.product_id || null,
        product_name: item.product_name,
        model_number: item.model_number || null,
        hsn_code: item.hsn_code,
        quantity: parseInt(item.quantity) || 1,
        rate: parseFloat(item.rate) || 0,
        tax_rate: parseFloat(item.tax_rate) || 18,
        discount: parseFloat(item.discount) || 0,
        has_serial_tracking: !!item.has_serial_tracking,
        serial_numbers: item.has_serial_tracking ? (item.serial_numbers || []) : [],
      }));

      const payload = {
        invoice_number: editForm.invoice_number,
        invoice_date: editForm.invoice_date,
        expected_delivery_date: editForm.expected_delivery_date || undefined,
        customer_name: editForm.customer_name,
        customer_phone: editForm.customer_phone,
        customer_email: editForm.customer_email,
        customer_address: editForm.customer_address,
        payment_mode: editForm.payment_mode || undefined,
        payment_status: editForm.payment_status,
        status: editForm.status,
        notes: editForm.notes,
        discount: parseFloat(editForm.discount) || 0,
        delivery_charges: parseFloat(editForm.delivery_charges) || 0,
        round_off: parseFloat(editForm.round_off) || 0,
        items: itemsPayload,
        edited_by: 'super_admin',
        edit_reason: editForm.edit_reason,
      };

      const response = await fetch(`${BACKEND_URL}/api/invoices/offline/${editDoc.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('adminToken')}` },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (data.status === 'success') {
        showToast.success('Document updated successfully');
        if (data.number_release?.released) {
          showToast.success(`Number ${editDoc.invoice_number} released — the next document will reuse it`);
        }
        setShowEditModal(false);
        fetchDocuments();
      } else {
        showToast.error(data.detail || 'Failed to save');
      }
    } catch (error) {
      showToast.error('Failed to save document');
    } finally {
      setSaving(false);
    }
  };

  // Item edit helpers (same behaviour as Create Offline Invoice)
  const fetchProducts = async () => {
    try {
      const r = await fetch(`${BACKEND_URL}/api/products?include_unlisted=true`);
      const d = await r.json();
      const list = Array.isArray(d?.products) ? d.products : (Array.isArray(d) ? d : []);
      if (!r.ok || list.length === 0) console.warn('Products load problem:', r.status, d);
      setProducts(list);
    } catch (e) { console.error('Error fetching products:', e); }
  };

  const fetchHsnCodes = async () => {
    try {
      const r = await fetch(`${BACKEND_URL}/api/hsn/?active_only=true`);
      const d = await r.json();
      setHsnCodes(Array.isArray(d) ? d : []);
    } catch (e) { console.error('Error fetching HSN codes:', e); }
  };

  const loadEditLookups = () => {
    if (products.length === 0) fetchProducts();
    if (hsnCodes.length === 0) fetchHsnCodes();
  };

  const updateItem = (idx, field, value) => {
    setEditItems(prev => prev.map((it, i) => i === idx ? { ...it, [field]: value } : it));
  };

  const patchItem = (idx, patch) => {
    setEditItems(prev => prev.map((it, i) => i === idx ? { ...it, ...patch } : it));
  };

  const addItem = () => {
    setEditItems(prev => [...prev, {
      _key: Date.now(), product_id: '', product_name: '', model_number: '', hsn_code: '',
      quantity: 1, rate: 0, tax_rate: 18, discount: 0,
      has_serial_tracking: false, serial_numbers: [], available_serials: [], manual_serials: ''
    }]);
  };

  const removeItem = (idx) => {
    setEditItems(prev => prev.length > 1 ? prev.filter((_, i) => i !== idx) : prev);
  };

  const getFilteredProducts = (term) => {
    if (!term) return products;
    const t = term.toLowerCase();
    return products.filter(p =>
      p.name?.toLowerCase().includes(t) ||
      p.brand?.toLowerCase().includes(t) ||
      p.model_number?.toLowerCase().includes(t)
    );
  };

  // GST state code decides CGST+SGST vs IGST ('29' = Karnataka), same rule as Create page
  const isInterStateGst = () => {
    const gst = ((editDoc?.customer?.gst_number || editDoc?.customer_gstin || '') + '').trim();
    if (!gst) return false;
    return gst.substring(0, 2) !== '29';
  };

  const calculateItemTotal = (item) => {
    const inclusivePrice = (parseFloat(item.rate) || 0) * (parseInt(item.quantity) || 1);
    const discountAmount = (inclusivePrice * (parseFloat(item.discount) || 0)) / 100;
    const finalPrice = inclusivePrice - discountAmount;
    const taxRate = parseFloat(item.tax_rate) || 18;
    const taxableAmount = finalPrice / (1 + taxRate / 100);
    const taxAmount = finalPrice - taxableAmount;
    const interState = isInterStateGst();
    return {
      discountAmount, taxableAmount, taxAmount,
      cgst: interState ? 0 : taxAmount / 2,
      sgst: interState ? 0 : taxAmount / 2,
      igst: interState ? taxAmount : 0,
      total: finalPrice
    };
  };

  const fetchHsnSuggestion = async (productName, idx) => {
    if (!productName || productName.length < 3) {
      setHsnSuggestions(prev => ({ ...prev, [idx]: [] }));
      return;
    }
    try {
      const r = await fetch(`${BACKEND_URL}/api/hsn/suggest?product_name=${encodeURIComponent(productName)}`);
      const d = await r.json();
      if (d.suggestions && d.suggestions.length > 0) {
        setHsnSuggestions(prev => ({ ...prev, [idx]: d.suggestions }));
        const top = d.suggestions[0];
        if (!editItems[idx]?.hsn_code && top.match_score >= 50) {
          patchItem(idx, { hsn_code: top.code, tax_rate: top.gst_rate || 18 });
        }
      } else {
        setHsnSuggestions(prev => ({ ...prev, [idx]: [] }));
      }
    } catch (e) { console.error('Error fetching HSN suggestions:', e); }
  };

  const applyHsnSuggestion = (idx, sg) => {
    patchItem(idx, { hsn_code: sg.code, tax_rate: sg.gst_rate || 18 });
    setHsnSuggestions(prev => ({ ...prev, [idx]: null }));
  };

  const fetchNewProductHsnSuggestion = async (productName) => {
    if (!productName || productName.length < 2) { setNewProductHsnSuggestions([]); return; }
    try {
      const r = await fetch(`${BACKEND_URL}/api/hsn/suggest?product_name=${encodeURIComponent(productName)}`);
      const d = await r.json();
      if (d.suggestions && d.suggestions.length > 0) {
        setNewProductHsnSuggestions(d.suggestions);
        const top = d.suggestions[0];
        if (!newProduct.hsn_code && top.match_score >= 50) {
          setNewProduct(prev => ({ ...prev, hsn_code: top.code }));
        }
      } else {
        setNewProductHsnSuggestions([]);
      }
    } catch (e) { console.error('Error fetching HSN suggestions for new product:', e); }
  };

  const handleProductSelect = async (idx, productId) => {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    const productHsn = product.hsn_code || '';
    const gstRate = hsnCodes.find(h => h.code === productHsn)?.gst_rate || 18;
    const storeCode = editDoc?.store_code;
    let hasSerialTracking = false;
    let availableSerials = [];
    try {
      const chk = await fetch(`${BACKEND_URL}/api/grn/serial-inventory/check-product/${productId}${storeCode ? `?store_code=${storeCode}` : ''}`);
      const chkData = await chk.json();
      if (chkData.status === 'success' && chkData.has_serial_tracking) {
        hasSerialTracking = true;
        const sr = await fetch(`${BACKEND_URL}/api/grn/serial-inventory/product/${productId}/available${storeCode ? `?store_code=${storeCode}` : ''}`);
        const srData = await sr.json();
        if (srData.status === 'success') availableSerials = srData.serials || [];
      }
    } catch (e) { console.error('Error checking serial tracking:', e); }

    patchItem(idx, {
      product_id: product.id,
      product_name: product.name,
      model_number: product.model_number || '',
      rate: product.price || 0,
      hsn_code: productHsn,
      tax_rate: gstRate,
      available_stock: product.current_stock || 0,
      stock_warning: product.current_stock <= 0 ? 'OUT_OF_STOCK' :
                     product.current_stock <= (product.reorder_level || 5) ? 'LOW_STOCK' : null,
      has_serial_tracking: hasSerialTracking,
      serial_numbers: [],
      manual_serials: '',
      available_serials: availableSerials
    });
  };

  const toggleSerial = (idx, sn) => {
    setEditItems(prev => prev.map((it, i) => {
      if (i !== idx) return it;
      const cur = it.serial_numbers || [];
      if (cur.includes(sn)) return { ...it, serial_numbers: cur.filter(x => x !== sn) };
      if (cur.length >= (parseInt(it.quantity) || 1)) return it;
      return { ...it, serial_numbers: [...cur, sn] };
    }));
  };

  const setManualSerials = (idx, value) => {
    setEditItems(prev => prev.map((it, i) => {
      if (i !== idx) return it;
      const manualList = value.split(',').map(x => x.trim()).filter(x => x.length > 0);
      const inventorySelected = (it.serial_numbers || [])
        .filter(sn => (it.available_serials || []).some(a => a.serial_number === sn));
      return { ...it, manual_serials: value, serial_numbers: [...new Set([...inventorySelected, ...manualList])] };
    }));
  };

  const removeSerial = (idx, sn) => {
    setEditItems(prev => prev.map((it, i) => {
      if (i !== idx) return it;
      const manual = (it.manual_serials || '').split(',').map(x => x.trim()).filter(x => x && x !== sn).join(', ');
      return { ...it, serial_numbers: (it.serial_numbers || []).filter(x => x !== sn), manual_serials: manual };
    }));
  };

  const openAddProductModal = (idx) => {
    setAddProductForIndex(idx);
    setNewProduct({ name: '', brand: '', model_number: '', price: 0, hsn_code: '', category: '', description: '', current_stock: 0 });
    setManualHsnMode(false);
    setManualHsnGstRate(18);
    setNewProductHsnSuggestions([]);
    setShowAddProductModal(true);
  };

  const handleCreateProduct = async () => {
    if (!newProduct.name || !newProduct.price || !newProduct.hsn_code) {
      showToast.error('Please fill in product name, price, and HSN code');
      return;
    }
    setAddProductLoading(true);
    try {
      let gstRate = 18;
      const existingHsn = hsnCodes.find(h => h.code === newProduct.hsn_code);
      if (manualHsnMode && !existingHsn) {
        try {
          await fetch(`${BACKEND_URL}/api/hsn/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              code: newProduct.hsn_code,
              description: `HSN ${newProduct.hsn_code} - ${newProduct.category || newProduct.name}`,
              gst_rate: manualHsnGstRate,
              category: newProduct.category || 'Uncategorized',
              is_active: true
            })
          });
          await fetchHsnCodes();
        } catch (e) { console.log('HSN code might already exist or failed to save:', e); }
        gstRate = manualHsnGstRate;
      } else if (existingHsn) {
        gstRate = existingHsn.gst_rate || 18;
      }

      const response = await fetch(`${BACKEND_URL}/api/products`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newProduct,
          id: `PROD-${Date.now()}`,
          price: parseFloat(newProduct.price),
          current_stock: parseInt(newProduct.current_stock) || 0
        })
      });
      const data = await response.json();
      if (response.ok) {
        await fetchProducts();
        if (addProductForIndex !== null) {
          patchItem(addProductForIndex, {
            product_id: data.product?.id || data.id,
            product_name: newProduct.name,
            model_number: newProduct.model_number || '',
            rate: parseFloat(newProduct.price),
            hsn_code: newProduct.hsn_code,
            tax_rate: gstRate,
            available_stock: parseInt(newProduct.current_stock) || 0
          });
        }
        showToast.success(`Product "${newProduct.name}" created successfully!`);
        setShowAddProductModal(false);
        setManualHsnMode(false);
        setManualHsnGstRate(18);
      } else {
        showToast.error(data.detail || 'Failed to create product');
      }
    } catch (e) {
      showToast.error('Error creating product: ' + e.message);
    } finally {
      setAddProductLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      confirmed: 'bg-blue-100 text-blue-800',
      processing: 'bg-indigo-100 text-indigo-800',
      ready_for_delivery: 'bg-cyan-100 text-cyan-800',
      pending_delivery: 'bg-orange-100 text-orange-800',
      dispatched: 'bg-purple-100 text-purple-800',
      delivered: 'bg-green-100 text-green-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const formatCurrency = (val) => {
    const num = parseFloat(val);
    return isNaN(num) ? '0.00' : num.toLocaleString('en-IN', { minimumFractionDigits: 2 });
  };

  return (
    <div className="p-6 max-w-full" data-testid="store-document-manager">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900" data-testid="sdm-title">Store Document Manager</h1>
          <p className="text-sm text-gray-500 mt-1">View and edit all store documents — Invoices, Sales Orders, Vouchers</p>
        </div>
        <button onClick={fetchDocuments} className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium">
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      {/* Store Selector + Filters */}
      <div className="bg-white rounded-xl shadow-sm border p-4 mb-4 space-y-3">
        {/* Row 1: Store + Doc Type */}
        <div className="flex flex-wrap gap-3 items-center">
          <div className="flex items-center gap-2">
            <Store className="w-4 h-4 text-gray-500" />
            <select
              value={selectedStore}
              onChange={(e) => { setSelectedStore(e.target.value); setPagination(p => ({...p, page: 1})); }}
              className="px-3 py-2 border rounded-lg text-sm font-medium focus:ring-2 focus:ring-amber-500 min-w-[160px]"
              data-testid="store-selector"
            >
              <option value="all">All Stores</option>
              {stores.map(s => (
                <option key={s.code} value={s.code}>{s.name || s.code}</option>
              ))}
            </select>
          </div>

          <div className="flex bg-gray-100 rounded-lg p-0.5">
            {DOC_TYPES.map(dt => (
              <button
                key={dt.id}
                onClick={() => { setDocTypeFilter(dt.id); setPagination(p => ({...p, page: 1})); }}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                  docTypeFilter === dt.id ? 'bg-white shadow text-amber-700' : 'text-gray-600 hover:text-gray-900'
                }`}
                data-testid={`filter-${dt.id}`}
              >
                <dt.icon className="w-3.5 h-3.5" />
                {dt.label}
              </button>
            ))}
          </div>

          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPagination(p => ({...p, page: 1})); }}
            className="px-3 py-2 border rounded-lg text-sm"
          >
            <option value="all">All Statuses</option>
            {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>)}
          </select>
        </div>

        {/* Row 2: Search */}
        <div className="relative">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search by document number, customer name, or phone..."
            value={searchTerm}
            onChange={(e) => { setSearchTerm(e.target.value); setPagination(p => ({...p, page: 1})); }}
            className="w-full pl-10 pr-4 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-amber-500"
            data-testid="search-input"
          />
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div className="bg-white rounded-lg border p-3">
          <p className="text-xs text-gray-500">Total Documents</p>
          <p className="text-xl font-bold text-gray-900">{pagination.total}</p>
        </div>
        <div className="bg-white rounded-lg border p-3">
          <p className="text-xs text-gray-500">Sales Orders</p>
          <p className="text-xl font-bold text-blue-600">{documents.filter(d => d.document_type === 'sales_order').length}</p>
        </div>
        <div className="bg-white rounded-lg border p-3">
          <p className="text-xs text-gray-500">Invoices</p>
          <p className="text-xl font-bold text-green-600">{documents.filter(d => d.document_type === 'invoice').length}</p>
        </div>
        <div className="bg-white rounded-lg border p-3">
          <p className="text-xs text-gray-500">Store</p>
          <p className="text-xl font-bold text-amber-700">{selectedStore === 'all' ? 'All' : selectedStore}</p>
        </div>
      </div>

      {/* Documents Table */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        {loading ? (
          <div className="p-12 text-center">
            <RefreshCw className="w-8 h-8 text-gray-400 animate-spin mx-auto mb-3" />
            <p className="text-gray-500">Loading documents...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No documents found</p>
            <p className="text-xs text-gray-400 mt-1">Try changing your filters or search term</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-left px-4 py-3 font-semibold text-gray-700">Document #</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-700">Type</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-700">Store</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-700">Customer</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-700">Date</th>
                  <th className="text-right px-4 py-3 font-semibold text-gray-700">Amount</th>
                  <th className="text-center px-4 py-3 font-semibold text-gray-700">Status</th>
                  <th className="text-center px-4 py-3 font-semibold text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {documents.map(doc => (
                  <tr key={doc.id} className="hover:bg-gray-50 transition-colors" data-testid={`doc-row-${doc.id}`}>
                    <td className="px-4 py-3 font-mono font-semibold text-gray-900 text-xs">
                      {doc._soView ? doc.original_so_number : (doc.invoice_number || '-')}
                      {doc._soView && (
                        <div className="text-[10px] font-normal text-gray-500 mt-0.5">Invoice: {doc.invoice_number}</div>
                      )}
                      {doc.document_type === 'sales_order' && (() => {
                        const linked = [
                          ...(doc.converted_invoice_number ? [doc.converted_invoice_number] : []),
                          ...((doc.partial_invoices || []).filter(n => n !== doc.converted_invoice_number)),
                        ];
                        return linked.length > 0 ? (
                          <div className="text-[10px] font-normal text-gray-500 mt-0.5">
                            Invoice: {linked.join(', ')}
                          </div>
                        ) : null;
                      })()}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${
                        doc.document_type === 'sales_order' ? 'bg-blue-50 text-blue-700' : 'bg-green-50 text-green-700'
                      }`}>
                        {(doc.document_type === 'sales_order' || doc._soView) ? 'SO' : 'INV'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600 text-xs">{doc.store_code || doc.store_name || '-'}</td>
                    <td className="px-4 py-3">
                      <div className="text-gray-900 text-xs font-medium">{doc.customer_name || doc.customer?.name || '-'}</div>
                      <div className="text-gray-400 text-xs">{doc.customer_phone || doc.customer?.phone || ''}</div>
                    </td>
                    <td className="px-4 py-3 text-gray-600 text-xs">
                      {(doc.invoice_date || doc.created_at || '').substring(0, 10)}
                    </td>
                    <td className="px-4 py-3 text-right font-semibold text-gray-900 text-xs">
                      {formatCurrency(doc.total_amount)}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(doc.status)}`}>
                        {doc._soView ? 'converted' : (doc.status || 'pending').replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <div className="flex items-center justify-center gap-1">
                        <button
                          onClick={() => { setViewDoc(doc); setShowViewModal(true); }}
                          className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                          title="View"
                          data-testid={`view-btn-${doc.id}`}
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => openEditModal(doc)}
                          className="p-1.5 text-gray-400 hover:text-amber-600 hover:bg-amber-50 rounded"
                          title="Edit"
                          data-testid={`edit-btn-${doc.id}`}
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={async () => {
                            const confirmText = window.prompt(`Type the invoice number "${doc.invoice_number}" to confirm deletion:`);
                            if (confirmText !== doc.invoice_number) {
                              if (confirmText !== null) window.alert('Invoice number did not match. Deletion cancelled.');
                              return;
                            }
                            const reason = window.prompt('Reason for deletion (optional):', '') || '';
                            try {
                              const response = await fetch(`${BACKEND_URL}/api/invoices/offline/admin/delete-by-ids`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('adminToken')}` },
                                body: JSON.stringify({
                                  ids: [doc.id],
                                  confirm: 'DELETE',
                                  deleted_by: 'super_admin',
                                  delete_reason: reason
                                })
                              });
                              const data = await response.json();
                              if (data.status === 'success') {
                                showToast.success(`${doc.invoice_number} deleted`);
                                fetchDocuments();
                              } else {
                                showToast.error(data.detail || 'Failed to delete');
                              }
                            } catch (error) {
                              showToast.error('Failed to delete document');
                            }
                          }}
                          className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                          title="Delete"
                          data-testid={`delete-btn-${doc.id}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {pagination.pages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t bg-gray-50">
            <p className="text-xs text-gray-500">
              Page {pagination.page} of {pagination.pages} ({pagination.total} documents)
            </p>
            <div className="flex gap-1">
              <button
                disabled={pagination.page <= 1}
                onClick={() => setPagination(p => ({...p, page: p.page - 1}))}
                className="p-1.5 rounded hover:bg-gray-200 disabled:opacity-40"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                disabled={pagination.page >= pagination.pages}
                onClick={() => setPagination(p => ({...p, page: p.page + 1}))}
                className="p-1.5 rounded hover:bg-gray-200 disabled:opacity-40"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* =========== VIEW MODAL =========== */}
      {showViewModal && viewDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={() => setShowViewModal(false)}>
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto m-4" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between p-5 border-b">
              <div>
                <h3 className="text-lg font-bold">{viewDoc.invoice_number}</h3>
                <p className="text-xs text-gray-500">{viewDoc.document_type === 'sales_order' ? 'Sales Order' : 'Invoice'} | {viewDoc.store_code}</p>
              </div>
              <button onClick={() => setShowViewModal(false)} className="p-2 hover:bg-gray-100 rounded-full">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-5 space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div><span className="text-gray-500">Date:</span> <span className="font-medium">{(viewDoc.invoice_date || viewDoc.created_at || '').substring(0, 10)}</span></div>
                <div><span className="text-gray-500">Status:</span> <span className={`ml-1 px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(viewDoc.status)}`}>{viewDoc.status}</span></div>
                <div><span className="text-gray-500">Customer:</span> <span className="font-medium">{viewDoc.customer_name || viewDoc.customer?.name || '-'}</span></div>
                <div><span className="text-gray-500">Phone:</span> <span className="font-medium">{viewDoc.customer_phone || viewDoc.customer?.phone || '-'}</span></div>
                <div><span className="text-gray-500">Payment:</span> <span className="font-medium">{viewDoc.payment_mode || viewDoc.payment_method || '-'}</span></div>
                <div><span className="text-gray-500">Total:</span> <span className="font-bold text-lg">{formatCurrency(viewDoc.total_amount)}</span></div>
              </div>
              {viewDoc.items && viewDoc.items.length > 0 && (
                <div>
                  <h4 className="font-semibold text-sm mb-2">Items ({viewDoc.items.length})</h4>
                  <table className="w-full text-xs border rounded">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="text-left p-2">Product</th>
                        <th className="text-left p-2">Model / HSN</th>
                        <th className="text-center p-2">Qty</th>
                        <th className="text-right p-2">Rate</th>
                        <th className="text-right p-2">GST%</th>
                        <th className="text-right p-2">Amount</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {viewDoc.items.map((item, i) => (
                        <tr key={i}>
                          <td className="p-2">{item.product_name || item.name}</td>
                          <td className="p-2 text-gray-500">{item.model_number} {item.hsn_code ? `/ ${item.hsn_code}` : ''}</td>
                          <td className="p-2 text-center">{item.quantity}</td>
                          <td className="p-2 text-right">{formatCurrency(item.unit_price || item.rate)}</td>
                          <td className="p-2 text-right">{item.gst_rate || item.tax_rate || 18}%</td>
                          <td className="p-2 text-right font-medium">{formatCurrency(item.amount || item.total)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              {viewDoc.notes && <div className="text-sm"><span className="text-gray-500">Notes:</span> {viewDoc.notes}</div>}
            </div>
            <div className="flex justify-end gap-2 p-5 border-t">
              <button onClick={() => { setShowViewModal(false); openEditModal(viewDoc); }} className="px-4 py-2 bg-amber-600 text-white rounded-lg text-sm font-medium hover:bg-amber-700">
                <Edit className="w-4 h-4 inline mr-1" /> Edit Document
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =========== EDIT MODAL =========== */}
      {showEditModal && editDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={() => setShowEditModal(false)}>
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[92vh] overflow-y-auto m-4" onClick={e => e.stopPropagation()}>
            {/* Modal Header */}
            <div className="flex items-center justify-between p-5 border-b sticky top-0 bg-white z-10">
              <div>
                <h3 className="text-lg font-bold">Edit: {editDoc.invoice_number}</h3>
                <p className="text-xs text-gray-500">{editDoc.document_type === 'sales_order' ? 'Sales Order' : 'Invoice'} | Store: {editDoc.store_code}</p>
              </div>
              <button onClick={() => setShowEditModal(false)} className="p-2 hover:bg-gray-100 rounded-full"><X className="w-5 h-5" /></button>
            </div>

            {/* Tabs */}
            <div className="flex border-b px-5 sticky top-[73px] bg-white z-10">
              {['details', 'customer', 'items', 'payment'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveEditTab(tab)}
                  className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                    activeEditTab === tab ? 'border-amber-600 text-amber-700' : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            <div className="p-5 space-y-4">
              {/* TAB: Details */}
              {activeEditTab === 'details' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Document Number</label>
                    <input type="text" value={editForm.invoice_number} onChange={e => setEditForm({...editForm, invoice_number: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-amber-500" data-testid="edit-invoice-number" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Document Date</label>
                    <input type="date" value={editForm.invoice_date} onChange={e => setEditForm({...editForm, invoice_date: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-amber-500" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Expected Delivery Date</label>
                    <input type="date" value={editForm.expected_delivery_date} onChange={e => setEditForm({...editForm, expected_delivery_date: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-amber-500" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Status</label>
                    <select value={editForm.status} onChange={e => setEditForm({...editForm, status: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-amber-500">
                      {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>)}
                    </select>
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Notes</label>
                    <textarea value={editForm.notes} onChange={e => setEditForm({...editForm, notes: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-amber-500" rows={2} />
                  </div>
                </div>
              )}

              {/* TAB: Customer */}
              {activeEditTab === 'customer' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Customer Name</label>
                    <input type="text" value={editForm.customer_name} onChange={e => setEditForm({...editForm, customer_name: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-amber-500" data-testid="edit-customer-name" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Phone</label>
                    <input type="text" value={editForm.customer_phone} onChange={e => setEditForm({...editForm, customer_phone: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-amber-500" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Email</label>
                    <input type="email" value={editForm.customer_email} onChange={e => setEditForm({...editForm, customer_email: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-amber-500" />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Address</label>
                    <textarea value={editForm.customer_address} onChange={e => setEditForm({...editForm, customer_address: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-amber-500" rows={2} />
                  </div>
                </div>
              )}

              {/* TAB: Items */}
              {activeEditTab === 'items' && (
                <div>
                  {editDoc?.document_type !== 'sales_order' && (
                    <div className="mb-3 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800">
                      <AlertTriangle className="w-3.5 h-3.5 inline mr-1" />
                      This is an invoice. Stock was already deducted when it was created, so changing a
                      quantity or product here does <strong>not</strong> adjust inventory.
                    </div>
                  )}
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-semibold text-sm">Line Items ({editItems.length})</h4>
                    <button type="button" onClick={addItem} className="flex items-center gap-1 px-3 py-1.5 bg-amber-600 text-white rounded-lg text-xs font-medium hover:bg-amber-700">
                      <Plus className="w-3.5 h-3.5" /> Add Item
                    </button>
                  </div>

                  <div className="space-y-4">
                    {editItems.map((item, idx) => (
                      <div key={item._key} className="border rounded-lg p-4 relative" data-testid={`edit-item-${idx}`}>
                        {editItems.length > 1 && (
                          <button type="button" onClick={() => removeItem(idx)} className="absolute top-2 right-2 text-red-600 hover:bg-red-50 p-1 rounded" title="Remove">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}

                        <div className="grid grid-cols-6 gap-3">
                          <div className="col-span-4">
                            <label className="block text-xs font-medium text-gray-700 mb-1">Search & Select Product *</label>
                            <div className="flex gap-2">
                              <div className="flex-1 relative">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                <input
                                  type="text"
                                  value={productSearch[idx] || ''}
                                  onChange={(e) => setProductSearch({ ...productSearch, [idx]: e.target.value })}
                                  className="w-full pl-10 pr-3 py-2 border rounded text-sm"
                                  placeholder="Type model no, brand or product name..."
                                />
                                {productSearch[idx] && productSearch[idx].length > 1 && (
                                  <div className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg max-h-60 overflow-y-auto">
                                    {getFilteredProducts(productSearch[idx]).length === 0 ? (
                                      <div className="p-3 text-sm text-gray-500">No products found matching "{productSearch[idx]}"</div>
                                    ) : (
                                      getFilteredProducts(productSearch[idx]).slice(0, 10).map(product => (
                                        <div
                                          key={product.id}
                                          onClick={() => {
                                            handleProductSelect(idx, product.id);
                                            setProductSearch({ ...productSearch, [idx]: '' });
                                          }}
                                          className="p-3 hover:bg-amber-50 cursor-pointer border-b last:border-b-0"
                                        >
                                          <div className="font-medium text-gray-900 text-sm">{product.name}</div>
                                          <div className="text-xs text-gray-500 flex gap-2 mt-1">
                                            <span className="bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">{product.brand}</span>
                                            {product.model_number && <span className="bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">{product.model_number}</span>}
                                            <span className="text-emerald-600 font-medium">₹{product.price?.toLocaleString()}</span>
                                            <span className={`px-1.5 py-0.5 rounded ${product.current_stock > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                              Stock: {product.current_stock || 0}
                                            </span>
                                          </div>
                                        </div>
                                      ))
                                    )}
                                  </div>
                                )}
                              </div>
                              <select
                                value={item.product_id || ''}
                                onChange={(e) => { if (e.target.value) handleProductSelect(idx, e.target.value); }}
                                className="w-32 px-2 py-2 border rounded text-sm bg-white"
                              >
                                <option value="">All Products ▼</option>
                                {products.map(product => (
                                  <option key={product.id} value={product.id}>
                                    {product.model_number || product.name?.substring(0, 30)}
                                  </option>
                                ))}
                              </select>
                              <button
                                type="button"
                                onClick={() => openAddProductModal(idx)}
                                className="px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 flex items-center gap-1 whitespace-nowrap"
                                title="Add new product to inventory"
                              >
                                <Package className="w-4 h-4" />
                                + New
                              </button>
                            </div>
                            <div className="text-xs mt-1">
                              {item.product_id ? (
                                <div>
                                  <span className="text-green-600 font-medium">✓ Selected: {item.product_name}</span>
                                  {item.stock_warning === 'OUT_OF_STOCK' && (
                                    <div className="mt-1 bg-red-50 border border-red-200 rounded px-2 py-1 text-red-700">
                                      ⚠️ <span className="font-semibold">OUT OF STOCK</span> - Available: {item.available_stock || 0} units
                                    </div>
                                  )}
                                  {item.stock_warning === 'LOW_STOCK' && (
                                    <div className="mt-1 bg-orange-50 border border-orange-200 rounded px-2 py-1 text-orange-700">
                                      ⚠️ <span className="font-semibold">LOW STOCK</span> - Available: {item.available_stock || 0} units
                                    </div>
                                  )}
                                  {!item.stock_warning && item.available_stock !== undefined && (
                                    <div className="mt-1 text-gray-600">Stock available: {item.available_stock} units</div>
                                  )}
                                </div>
                              ) : (
                                <span className="text-gray-500">Start typing or select from dropdown</span>
                              )}
                            </div>
                          </div>

                          <div className="col-span-2">
                            <label className="block text-xs font-medium text-gray-700 mb-1">Product Name (Manual)</label>
                            <input
                              type="text"
                              value={item.product_name || ''}
                              onChange={(e) => {
                                updateItem(idx, 'product_name', e.target.value);
                                fetchHsnSuggestion(e.target.value, idx);
                              }}
                              className="w-full px-3 py-2 border rounded text-sm"
                              placeholder="Custom product/service name"
                            />
                            <div className="text-xs text-gray-500 mt-1">For custom items not in inventory</div>
                            {hsnSuggestions[idx] && hsnSuggestions[idx].length > 0 && !item.product_id && (
                              <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded">
                                <div className="text-xs font-medium text-blue-800 mb-1">💡 Suggested HSN Codes:</div>
                                <div className="space-y-1">
                                  {hsnSuggestions[idx].slice(0, 3).map((sg, sIdx) => (
                                    <button
                                      key={sIdx}
                                      type="button"
                                      onClick={() => applyHsnSuggestion(idx, sg)}
                                      className={`w-full text-left px-2 py-1 rounded text-xs hover:bg-blue-100 ${item.hsn_code === sg.code ? 'bg-blue-200' : 'bg-white'}`}
                                    >
                                      <span className="font-semibold text-blue-700">{sg.code}</span>
                                      <span className="text-gray-600 ml-2">{sg.category || sg.description?.substring(0, 35)}</span>
                                      <span className="text-green-600 ml-2 font-medium">{sg.gst_rate}% GST</span>
                                    </button>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="grid grid-cols-5 gap-3 mt-3">
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">HSN Code *</label>
                            <input
                              type="text"
                              list={`edit-hsn-list-${idx}`}
                              value={item.hsn_code || ''}
                              onChange={(e) => {
                                const value = e.target.value;
                                const sel = hsnCodes.find(h => h.code === value);
                                patchItem(idx, sel && sel.gst_rate ? { hsn_code: value, tax_rate: sel.gst_rate } : { hsn_code: value });
                              }}
                              className="w-full px-3 py-2 border rounded text-sm"
                              placeholder="Type or select HSN"
                            />
                            <datalist id={`edit-hsn-list-${idx}`}>
                              {hsnCodes.map(hsn => (
                                <option key={hsn.id || hsn.code} value={hsn.code}>{hsn.description?.substring(0, 40)}</option>
                              ))}
                            </datalist>
                            {item.hsn_code && hsnCodes.find(h => h.code === item.hsn_code) && (
                              <div className="text-xs text-gray-500 mt-1">
                                {hsnCodes.find(h => h.code === item.hsn_code)?.description?.substring(0, 35)}...
                              </div>
                            )}
                            {item.hsn_code && hsnCodes.length > 0 && !hsnCodes.find(h => h.code === item.hsn_code) && (
                              <div className="text-xs text-amber-600 mt-1">Custom HSN code</div>
                            )}
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Quantity *</label>
                            <input type="number" min="1" value={item.quantity} onChange={(e) => updateItem(idx, 'quantity', parseInt(e.target.value) || 1)} className="w-full px-3 py-2 border rounded text-sm" />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Rate (₹) * <span className="text-gray-500 font-normal">(incl. GST)</span></label>
                            <input type="number" step="0.01" value={item.rate} onChange={(e) => updateItem(idx, 'rate', parseFloat(e.target.value) || 0)} className="w-full px-3 py-2 border rounded text-sm" />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Tax Rate %</label>
                            <select value={item.tax_rate} onChange={(e) => updateItem(idx, 'tax_rate', parseFloat(e.target.value) || 0)} className="w-full px-3 py-2 border rounded text-sm">
                              <option value="0">0%</option>
                              <option value="5">5%</option>
                              <option value="12">12%</option>
                              <option value="18">18%</option>
                              <option value="28">28%</option>
                            </select>
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Discount %</label>
                            <input type="number" step="0.01" min="0" max="100" value={item.discount} onChange={(e) => updateItem(idx, 'discount', parseFloat(e.target.value) || 0)} className="w-full px-3 py-2 border rounded text-sm" />
                          </div>
                        </div>

                        {/* Serial numbers */}
                        <div className="mt-3 p-3 bg-gray-50 border border-gray-200 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <label className="flex items-center gap-2 cursor-pointer">
                              <input
                                type="checkbox"
                                checked={item.has_serial_tracking || false}
                                onChange={(e) => patchItem(idx, e.target.checked
                                  ? { has_serial_tracking: true }
                                  : { has_serial_tracking: false, serial_numbers: [], manual_serials: '' })}
                                className="w-4 h-4 text-blue-600 rounded"
                              />
                              <span className="text-xs font-medium text-gray-700">This item requires Serial Number</span>
                            </label>
                            {item.has_serial_tracking && (item.serial_numbers?.length || 0) !== (parseInt(item.quantity) || 1) && (
                              <span className="text-xs text-orange-600">⚠️ Enter {item.quantity || 1} serial(s)</span>
                            )}
                          </div>

                          {item.has_serial_tracking && (
                            <div className="space-y-3">
                              {item.available_serials && item.available_serials.length > 0 && (
                                <div>
                                  <label className="text-xs font-medium text-blue-800 mb-1 block">
                                    Select from Inventory ({item.available_serials.length} available):
                                  </label>
                                  <div className="flex flex-wrap gap-2 max-h-24 overflow-y-auto p-2 bg-blue-50 rounded">
                                    {item.available_serials.map((serial) => {
                                      const isSelected = item.serial_numbers?.includes(serial.serial_number);
                                      const canSelect = isSelected || (item.serial_numbers?.length || 0) < (parseInt(item.quantity) || 1);
                                      return (
                                        <button
                                          key={serial.serial_number}
                                          type="button"
                                          onClick={() => toggleSerial(idx, serial.serial_number)}
                                          disabled={!canSelect && !isSelected}
                                          className={`px-2 py-1 text-xs rounded border ${
                                            isSelected
                                              ? 'bg-blue-600 text-white border-blue-600'
                                              : canSelect
                                                ? 'bg-white text-blue-700 border-blue-300 hover:bg-blue-100'
                                                : 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed'
                                          }`}
                                          title={serial.warranty_months ? `Warranty: ${serial.warranty_months} months` : ''}
                                        >
                                          {serial.serial_number}{isSelected && ' ✓'}
                                        </button>
                                      );
                                    })}
                                  </div>
                                </div>
                              )}
                              <div>
                                <label className="text-xs font-medium text-gray-700 mb-1 block">
                                  {item.available_serials?.length > 0 ? 'Or enter manually:' : 'Enter Serial Number(s):'}
                                </label>
                                <input
                                  type="text"
                                  placeholder={item.quantity > 1 ? 'Enter serial numbers separated by comma' : 'Enter serial number'}
                                  value={item.manual_serials || ''}
                                  onChange={(e) => setManualSerials(idx, e.target.value)}
                                  className="w-full px-3 py-1.5 border rounded text-sm"
                                />
                                <p className="text-xs text-gray-500 mt-1">
                                  {item.quantity > 1 ? 'For multiple units, separate with commas (e.g., SN001, SN002)' : 'Serial number will be recorded with this sale'}
                                </p>
                              </div>
                              {item.serial_numbers?.length > 0 && (
                                <div className="flex flex-wrap gap-1 pt-2 border-t">
                                  <span className="text-xs text-gray-500">Selected ({item.serial_numbers.length}/{item.quantity}):</span>
                                  {item.serial_numbers.map((sn, snIdx) => (
                                    <span key={snIdx} className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded flex items-center gap-1">
                                      {sn}
                                      <button type="button" onClick={() => removeSerial(idx, sn)} className="text-green-600 hover:text-red-600">×</button>
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          )}
                          {!item.has_serial_tracking && (
                            <p className="text-xs text-gray-500">Enable serial tracking to record individual unit serial numbers for warranty and service tracking.</p>
                          )}
                        </div>

                        {/* Per-line GST breakup */}
                        <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                          {(() => {
                            const calc = calculateItemTotal(item);
                            const interState = isInterStateGst();
                            const tr = parseFloat(item.tax_rate) || 18;
                            return (
                              <div className="grid grid-cols-6 gap-2 text-xs">
                                <div className="text-gray-600">
                                  <div className="font-medium">Taxable Amt</div>
                                  <div className="text-gray-900">₹{calc.taxableAmount.toFixed(2)}</div>
                                </div>
                                {interState ? (
                                  <div className="text-gray-600">
                                    <div className="font-medium">IGST @{tr}%</div>
                                    <div className="text-gray-900">₹{calc.igst.toFixed(2)}</div>
                                  </div>
                                ) : (
                                  <>
                                    <div className="text-gray-600">
                                      <div className="font-medium">CGST @{tr / 2}%</div>
                                      <div className="text-gray-900">₹{calc.cgst.toFixed(2)}</div>
                                    </div>
                                    <div className="text-gray-600">
                                      <div className="font-medium">SGST @{tr / 2}%</div>
                                      <div className="text-gray-900">₹{calc.sgst.toFixed(2)}</div>
                                    </div>
                                  </>
                                )}
                                <div className="text-gray-600">
                                  <div className="font-medium">Total Tax</div>
                                  <div className="text-gray-900">₹{calc.taxAmount.toFixed(2)}</div>
                                </div>
                                <div className="text-gray-600">
                                  <div className="font-medium">Discount</div>
                                  <div className="text-red-600">-₹{calc.discountAmount.toFixed(2)}</div>
                                </div>
                                <div className="text-right">
                                  <div className="font-medium text-gray-600">Line Total</div>
                                  <div className="text-lg font-bold text-emerald-700">₹{calc.total.toFixed(2)}</div>
                                </div>
                              </div>
                            );
                          })()}
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="mt-3 text-right text-sm font-semibold text-gray-900">
                    Items total: ₹{editItems.reduce((sum, it) => sum + calculateItemTotal(it).total, 0).toFixed(2)}
                  </div>

                  {/* Add New Product Modal */}
                  {showAddProductModal && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center" style={{ zIndex: 60 }}>
                      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
                        <div className="bg-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
                          <h3 className="text-lg font-semibold flex items-center gap-2"><Package className="w-5 h-5" />Add New Product</h3>
                          <button type="button" onClick={() => setShowAddProductModal(false)} className="text-white hover:bg-blue-700 p-1 rounded"><X className="w-5 h-5" /></button>
                        </div>
                        <div className="p-6 space-y-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Product Name *</label>
                            <input
                              type="text"
                              value={newProduct.name}
                              onChange={(e) => {
                                setNewProduct({ ...newProduct, name: e.target.value });
                                fetchNewProductHsnSuggestion(e.target.value);
                              }}
                              className="w-full px-3 py-2 border rounded-lg"
                              placeholder="e.g., Bosch Built-in Oven 60cm"
                            />
                            {newProductHsnSuggestions.length > 0 && (
                              <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded">
                                <div className="text-xs font-medium text-blue-800 mb-1">💡 Suggested HSN Codes based on product name:</div>
                                <div className="space-y-1">
                                  {newProductHsnSuggestions.slice(0, 3).map((sg, sIdx) => (
                                    <button
                                      key={sIdx}
                                      type="button"
                                      onClick={() => { setNewProduct({ ...newProduct, hsn_code: sg.code }); setNewProductHsnSuggestions([]); }}
                                      className={`w-full text-left px-2 py-1 rounded text-xs hover:bg-blue-100 ${newProduct.hsn_code === sg.code ? 'bg-blue-200 border border-blue-400' : 'bg-white'}`}
                                    >
                                      <span className="font-semibold text-blue-700">{sg.code}</span>
                                      <span className="text-gray-600 ml-2">{sg.category || sg.description?.substring(0, 30)}</span>
                                      <span className="text-green-600 ml-2 font-medium">{sg.gst_rate}% GST</span>
                                    </button>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">Brand</label>
                              <input type="text" value={newProduct.brand} onChange={(e) => setNewProduct({ ...newProduct, brand: e.target.value })} className="w-full px-3 py-2 border rounded-lg" placeholder="e.g., Bosch, Siemens" />
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">Model Number</label>
                              <input type="text" value={newProduct.model_number} onChange={(e) => setNewProduct({ ...newProduct, model_number: e.target.value })} className="w-full px-3 py-2 border rounded-lg" placeholder="e.g., HBA534BS0" />
                            </div>
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">Selling Price (₹) *</label>
                              <input type="number" step="0.01" min="0" value={newProduct.price} onChange={(e) => setNewProduct({ ...newProduct, price: e.target.value })} className="w-full px-3 py-2 border rounded-lg" placeholder="Price incl. GST" />
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">Opening Stock</label>
                              <input type="number" min="0" value={newProduct.current_stock} onChange={(e) => setNewProduct({ ...newProduct, current_stock: e.target.value })} className="w-full px-3 py-2 border rounded-lg" placeholder="Initial stock quantity" />
                            </div>
                          </div>
                          <div>
                            <div className="flex items-center justify-between mb-1">
                              <label className="block text-sm font-medium text-gray-700">HSN Code *</label>
                              <button
                                type="button"
                                onClick={() => {
                                  setManualHsnMode(!manualHsnMode);
                                  if (!manualHsnMode) setNewProduct({ ...newProduct, hsn_code: '' });
                                }}
                                className="text-xs text-blue-600 hover:text-blue-800 underline"
                              >
                                {manualHsnMode ? 'Select from list' : 'Enter manually'}
                              </button>
                            </div>
                            {manualHsnMode ? (
                              <div className="space-y-2">
                                <input type="text" maxLength={8} value={newProduct.hsn_code} onChange={(e) => setNewProduct({ ...newProduct, hsn_code: e.target.value })} className="w-full px-3 py-2 border rounded-lg" placeholder="Enter HSN code (e.g., 85081100)" />
                                <div className="flex items-center gap-2">
                                  <label className="text-xs text-gray-600">GST Rate:</label>
                                  <select value={manualHsnGstRate} onChange={(e) => setManualHsnGstRate(parseFloat(e.target.value))} className="px-2 py-1 border rounded text-sm">
                                    <option value={0}>0%</option>
                                    <option value={5}>5%</option>
                                    <option value={12}>12%</option>
                                    <option value={18}>18%</option>
                                    <option value={28}>28%</option>
                                  </select>
                                </div>
                                <p className="text-xs text-amber-600">Note: Manually entered HSN codes will be added to the system</p>
                              </div>
                            ) : (
                              <>
                                <select value={newProduct.hsn_code} onChange={(e) => setNewProduct({ ...newProduct, hsn_code: e.target.value })} className="w-full px-3 py-2 border rounded-lg">
                                  <option value="">-- Select HSN Code --</option>
                                  {hsnCodes.map(hsn => (
                                    <option key={hsn.id || hsn.code} value={hsn.code}>
                                      {hsn.code} - {hsn.description?.substring(0, 40)}{hsn.description?.length > 40 ? '...' : ''} ({hsn.gst_rate}%)
                                    </option>
                                  ))}
                                </select>
                                {newProduct.hsn_code && (
                                  <p className="text-xs text-gray-500 mt-1">GST Rate: {hsnCodes.find(h => h.code === newProduct.hsn_code)?.gst_rate || 18}%</p>
                                )}
                              </>
                            )}
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                            <input type="text" value={newProduct.category} onChange={(e) => setNewProduct({ ...newProduct, category: e.target.value })} className="w-full px-3 py-2 border rounded-lg" placeholder="e.g., Built-in Ovens, Refrigerators" />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                            <textarea rows={2} value={newProduct.description} onChange={(e) => setNewProduct({ ...newProduct, description: e.target.value })} className="w-full px-3 py-2 border rounded-lg" placeholder="Optional description" />
                          </div>
                          <div className="flex justify-end gap-3 pt-2">
                            <button type="button" onClick={() => setShowAddProductModal(false)} className="px-4 py-2 border rounded-lg hover:bg-gray-50">Cancel</button>
                            <button type="button" onClick={handleCreateProduct} disabled={addProductLoading} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
                              {addProductLoading ? 'Creating...' : 'Create Product'}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* TAB: Payment */}
              {activeEditTab === 'payment' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Payment Mode</label>
                    <select value={editForm.payment_mode} onChange={e => setEditForm({...editForm, payment_mode: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-amber-500">
                      <option value="">Not Set</option>
                      <option value="cash">Cash</option>
                      <option value="card">Card</option>
                      <option value="upi">UPI</option>
                      <option value="bank_transfer">Bank Transfer</option>
                      <option value="cheque">Cheque</option>
                      <option value="credit">Credit</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Payment Status</label>
                    <select value={editForm.payment_status} onChange={e => setEditForm({...editForm, payment_status: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-amber-500">
                      {PAYMENT_STATUS_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Discount %</label>
                    <input type="number" value={editForm.discount} onChange={e => setEditForm({...editForm, discount: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg text-sm" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Delivery Charges</label>
                    <input type="number" value={editForm.delivery_charges} onChange={e => setEditForm({...editForm, delivery_charges: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg text-sm" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Round Off</label>
                    <input type="number" value={editForm.round_off} onChange={e => setEditForm({...editForm, round_off: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg text-sm" step="0.01" />
                  </div>
                </div>
              )}

              {/* Edit Reason (always visible) */}
              <div className="border-t pt-4">
                <label className="block text-xs font-semibold text-red-600 mb-1">
                  <AlertTriangle className="w-3.5 h-3.5 inline mr-1" />
                  Reason for Edit (Required)
                </label>
                <input type="text" value={editForm.edit_reason} onChange={e => setEditForm({...editForm, edit_reason: e.target.value})}
                  placeholder="e.g., FY transition renumbering, customer correction..."
                  className="w-full px-3 py-2 border border-red-200 rounded-lg text-sm focus:ring-2 focus:ring-red-500"
                  data-testid="edit-reason" />
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex justify-end gap-3 p-5 border-t sticky bottom-0 bg-white">
              <button onClick={() => setShowEditModal(false)} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200">Cancel</button>
              <button
                onClick={handleSave}
                disabled={saving || !editForm.edit_reason?.trim()}
                className="flex items-center gap-2 px-6 py-2 bg-amber-600 text-white rounded-lg text-sm font-semibold hover:bg-amber-700 disabled:opacity-50"
                data-testid="save-edit-btn"
              >
                {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StoreDocumentManager;
