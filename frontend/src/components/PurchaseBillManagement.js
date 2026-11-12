import React, { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  FileText, Plus, Search, Upload, Eye, Trash2, CheckCircle, Clock, 
  AlertCircle, Camera, X, Download, Filter, RefreshCw, Sparkles,
  IndianRupee, Calendar, Building2, Package, ShoppingBag, Wrench, Link2
} from 'lucide-react';
import { showToast } from '../utils/toast';
import Pagination from './Pagination';
import EmptyState from './EmptyState';
import GRNMatchingPanel from './GRNMatchingPanel';

// Extract the 2-digit GST state code from a GSTIN (first 2 chars)
const getGstStateCode = (gstin) => {
  if (!gstin || typeof gstin !== 'string') return null;
  const code = gstin.trim().substring(0, 2);
  return /^\d{2}$/.test(code) ? code : null;
};

const GSTIN_REGEX = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;
const isValidGstin = (gstin) => {
  if (!gstin) return true;
  return GSTIN_REGEX.test(gstin.trim().toUpperCase());
};

// Company's registered GSTIN - all stores currently share this single registration (Karnataka)
const COMPANY_GSTIN = '29ABAFA6295J1Z2';


const PurchaseBillManagement = () => {
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showScanModal, setShowScanModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showNewItemsModal, setShowNewItemsModal] = useState(false);
  const [newItemsToCreate, setNewItemsToCreate] = useState([]);
  const [pendingBillData, setPendingBillData] = useState(null);
  const [selectedBill, setSelectedBill] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [scannedData, setScannedData] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalBills, setTotalBills] = useState(0);
  const [stats, setStats] = useState(null);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [dateFilter, setDateFilter] = useState({ from: '', to: '' });
  const [gstFilter, setGstFilter] = useState('');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [pendingPOs, setPendingPOs] = useState([]);
  const [msmeCompliance, setMsmeCompliance] = useState(null);
  const [showPOWarning, setShowPOWarning] = useState(false);
  const [showGRNMatching, setShowGRNMatching] = useState(false);
  const [invoiceGRNMatch, setInvoiceGRNMatch] = useState(null);
  const [checkingGRNMatch, setCheckingGRNMatch] = useState(false);
  const [tdsRates, setTdsRates] = useState([]);
  const [tdsSearchTerm, setTdsSearchTerm] = useState('');
  const [showTdsDropdown, setShowTdsDropdown] = useState(false);
  const [selectedTds, setSelectedTds] = useState(null);
  const [tdsRateOverride, setTdsRateOverride] = useState('');
  const [tdsNoDeduction, setTdsNoDeduction] = useState(false);
  const [vendorSuggestions, setVendorSuggestions] = useState([]);
  const [showVendorSuggestions, setShowVendorSuggestions] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    bill_number: '',
    bill_date: new Date().toISOString().split('T')[0],
    po_number: '',
    vendor: {
      name: '',
      phone: '',
      email: '',
      gst_number: '',
      msme_udyam_number: '',
      address: '',
      city: '',
      state: '',
      pincode: ''
    },
    items: [],
    payment_mode: 'credit',
    payment_status: 'pending',
    due_date: '',
    notes: '',
    invoice_file_url: null
  });

  useEffect(() => {
    fetch(`${BACKEND_URL}/api/tds/rates`)
      .then(res => res.json())
      .then(data => { if (data.status === 'success') setTdsRates(data.rates || []); })
      .catch(err => console.error('Failed to load TDS rates:', err));
  }, []);

  useEffect(() => {
    const name = formData.vendor.name;
    if (!name || name.length < 2) { setVendorSuggestions([]); return; }
    const timer = setTimeout(() => {
      fetch(`${BACKEND_URL}/api/tds/vendor-suggestions?q=${encodeURIComponent(name)}`)
        .then(res => res.json())
        .then(data => { if (data.status === 'success') setVendorSuggestions(data.suggestions || []); })
        .catch(() => {});
    }, 400);
    return () => clearTimeout(timer);
  }, [formData.vendor.name]);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
      setCurrentPage(1); // Reset to first page on search
    }, 400);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Debounced live lookup: as the user types a vendor invoice/bill number, check for a matching GRN
  useEffect(() => {
    if (!showCreateModal || !formData.bill_number || formData.bill_number.trim().length < 3) {
      setInvoiceGRNMatch(null);
      return;
    }
    const timer = setTimeout(async () => {
      setCheckingGRNMatch(true);
      try {
        const response = await fetch(`${BACKEND_URL}/api/grn/lookup-by-invoice/${encodeURIComponent(formData.bill_number.trim())}`);
        const data = await response.json();
        if (data.status === 'success' && data.found) {
          setInvoiceGRNMatch(data.grn);
        } else {
          setInvoiceGRNMatch(null);
        }
      } catch (error) {
        console.error('Error looking up GRN by invoice number:', error);
        setInvoiceGRNMatch(null);
      } finally {
        setCheckingGRNMatch(false);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [formData.bill_number, showCreateModal]);

  const fillFromMatchedGRN = (grn) => {
    if (!grn) return;
    setFormData(prev => ({
      ...prev,
      po_number: grn.po_number || prev.po_number,
      bill_date: grn.vendor_invoice_date || prev.bill_date,
      vendor: {
        ...prev.vendor,
        name: grn.vendor_name || prev.vendor.name,
        gst_number: grn.vendor_gstin || prev.vendor.gst_number
      },
      items: (grn.items || []).map(item => ({
        product_name: item.product_name || '',
        hsn_code: item.hsn_code || '',
        quantity: item.received_quantity ?? item.ordered_quantity ?? 1,
        rate: item.unit_price ?? 0,
        discount_percent: 0,
        tax_rate: 18
      }))
    }));
    showToast.success(`Filled from GRN ${grn.grn_number}`);
    setInvoiceGRNMatch(null);
  };


  const [currentItem, setCurrentItem] = useState({
    product_name: '',
    hsn_code: '',
    quantity: 1,
    rate: 0,
    discount_percent: 0,
    tax_rate: 18
  });

  const fetchBills = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({ page: currentPage, limit: 15 });
      
      // Status filter
      if (statusFilter !== 'all') params.append('status', statusFilter);
      
      // Search term (searches across all fields: bill_number, vendor, GST, items)
      if (debouncedSearch) params.append('search', debouncedSearch);
      
      // Date range filters
      if (dateFilter.from) params.append('from_date', dateFilter.from);
      if (dateFilter.to) params.append('to_date', dateFilter.to);
      
      // GST number filter
      if (gstFilter) params.append('gst_number', gstFilter);
      
      const response = await fetch(`${BACKEND_URL}/api/purchase-bills/?${params}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setBills(data.bills);
        setTotalPages(data.pages);
        setTotalBills(data.total);
      }
    } catch (error) {
      console.error('Failed to fetch bills:', error);
      showToast.error('Failed to load purchase bills');
    } finally {
      setLoading(false);
    }
  }, [currentPage, statusFilter, debouncedSearch, dateFilter, gstFilter]);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/purchase-bills/stats/summary`);
      const data = await response.json();
      if (data.status === 'success') {
        setStats(data.stats);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  // Fetch pending POs and MSME compliance
  const fetchPendingPOs = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/purchase-orders/pending/for-billing`);
      const data = await response.json();
      if (data.status === 'success') {
        setPendingPOs(data.pending_pos || []);
      }
    } catch (error) {
      console.error('Failed to fetch POs:', error);
    }
  };

  const fetchMsmeCompliance = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/purchase-bills/compliance/msme-pending`);
      const data = await response.json();
      if (data.status === 'success') {
        setMsmeCompliance(data);
      }
    } catch (error) {
      console.error('Failed to fetch MSME compliance:', error);
    }
  };

  useEffect(() => {
    fetchBills();
    fetchStats();
    fetchPendingPOs();
    fetchMsmeCompliance();
  }, [fetchBills]);

  const handleScanInvoice = async (file) => {
    setScanning(true);
    const formDataUpload = new FormData();
    formDataUpload.append('file', file);

    try {
      const response = await fetch(`${BACKEND_URL}/api/purchase-bills/scan-invoice`, {
        method: 'POST',
        body: formDataUpload
      });
      
      const data = await response.json();
      
      if (data.status === 'success' && data.extracted_data) {
        setScannedData(data.extracted_data);
        
        // Try to auto-match PO number from scanned invoice
        let matchedPONumber = '';
        const scannedPONumber = data.extracted_data.po_number || '';
        
        if (scannedPONumber) {
          // Check if scanned PO number matches any pending PO
          const matchedPO = pendingPOs.find(po => 
            po.po_number.toLowerCase() === scannedPONumber.toLowerCase() ||
            po.po_number.toLowerCase().includes(scannedPONumber.toLowerCase()) ||
            scannedPONumber.toLowerCase().includes(po.po_number.toLowerCase())
          );
          
          if (matchedPO) {
            matchedPONumber = matchedPO.po_number;
            showToast.success(`Auto-matched with PO: ${matchedPO.po_number}`);
          } else {
            // No match found - show info
            showToast.custom(`PO "${scannedPONumber}" not found in pending POs. Please select from list or choose "Verbal".`);
          }
        }
        
        // Pre-fill form with scanned data
        setFormData({
          bill_number: data.extracted_data.bill_number || '',
          bill_date: data.extracted_data.bill_date || new Date().toISOString().split('T')[0],
          po_number: matchedPONumber, // Use matched PO number or empty
          vendor: {
            name: data.extracted_data.vendor?.name || '',
            phone: data.extracted_data.vendor?.phone || '',
            email: data.extracted_data.vendor?.email || '',
            gst_number: data.extracted_data.vendor?.gst_number || '',
            msme_udyam_number: data.extracted_data.vendor?.msme_udyam_number || '',
            address: data.extracted_data.vendor?.address || '',
            city: data.extracted_data.vendor?.city || '',
            state: data.extracted_data.vendor?.state || '',
            pincode: data.extracted_data.vendor?.pincode || ''
          },
          items: (data.extracted_data.items || []).map(item => {
            // AI extracts rate as GST-EXCLUSIVE (matches invoice's own Rate
            // column), but calculateTotals() expects GST-INCLUSIVE rates
            // (matches manual-entry UX where people type the inclusive
            // per-unit price). Convert once here so downstream math is correct.
            const taxRate = item.tax_rate || 0;
            const inclusiveRate = item.rate * (1 + taxRate / 100);
            return { ...item, rate: inclusiveRate };
          }),
          payment_mode: 'credit',
          payment_status: 'pending',
          due_date: data.extracted_data.due_date || '',
          notes: scannedPONumber && !matchedPONumber ? `Scanned PO Reference: ${scannedPONumber}` : '',
          invoice_file_url: data.extracted_data.invoice_file_url
        });
        showToast.success('Invoice scanned successfully! Review and save.');
        setShowScanModal(false);
        setShowCreateModal(true);
      } else if (data.status === 'partial') {
        showToast.warning('File uploaded but AI extraction failed. Please enter details manually.');
        setFormData(prev => ({ ...prev, invoice_file_url: data.invoice_file_url }));
        setShowScanModal(false);
        setShowCreateModal(true);
      } else {
        showToast.error(data.message || 'Scan failed');
      }
    } catch (error) {
      console.error('Scan failed:', error);
      showToast.error('Failed to scan invoice');
    } finally {
      setScanning(false);
    }
  };

  const addItemToList = () => {
    if (currentItem.product_name && currentItem.rate > 0 && currentItem.quantity > 0) {
      setFormData(prev => ({
        ...prev,
        items: [...prev.items, { ...currentItem }]
      }));
      setCurrentItem({
        product_name: '',
        hsn_code: '',
        quantity: 1,
        rate: 0,
        discount_percent: 0,
        tax_rate: 18
      });
    } else {
      showToast.error('Please fill product name, quantity, and rate');
    }
  };

  const removeItem = (index) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }));
  };

  const calculateTotals = () => {
    // Rates entered are GST-INCLUSIVE (the vendor's actual invoice amount),
    // so tax is extracted out of the entered rate rather than added on top.
    let taxableTotal = 0;
    let totalTax = 0;
    let grandTotal = 0;

    const storeGstin = COMPANY_GSTIN;
    const storeStateCode = getGstStateCode(storeGstin);
    const vendorStateCode = getGstStateCode(formData.vendor?.gst_number);
    const isInterState = !!(storeStateCode && vendorStateCode && storeStateCode !== vendorStateCode);

    formData.items.forEach(item => {
      const itemGross = item.quantity * item.rate;
      const discount = itemGross * (item.discount_percent / 100);
      const inclusiveAfterDiscount = itemGross - discount;
      const taxRate = item.tax_rate || 0;
      const taxable = inclusiveAfterDiscount / (1 + taxRate / 100);
      const tax = inclusiveAfterDiscount - taxable;

      taxableTotal += taxable;
      totalTax += tax;
      grandTotal += inclusiveAfterDiscount;
    });

    const cgst = isInterState ? 0 : totalTax / 2;
    const sgst = isInterState ? 0 : totalTax / 2;
    const igst = isInterState ? totalTax : 0;

    let tdsRatePercent = 0;
    if (selectedTds && !tdsNoDeduction) {
      if (selectedTds.rate_type === 'percentage') {
        tdsRatePercent = selectedTds.rate_value;
      } else {
        const parsed = parseFloat(tdsRateOverride);
        tdsRatePercent = isNaN(parsed) ? 0 : parsed / 100;
      }
    }
    const tdsDeduction = taxableTotal * tdsRatePercent;
    const netPayable = grandTotal - tdsDeduction;

    return {
      subtotal: taxableTotal.toFixed(2),
      cgst: cgst.toFixed(2),
      sgst: sgst.toFixed(2),
      igst: igst.toFixed(2),
      isInterState,
      totalTax: totalTax.toFixed(2),
      grandTotal: grandTotal.toFixed(2),
      tdsDeduction: tdsDeduction.toFixed(2),
      netPayable: netPayable.toFixed(2)
    };
  };

  const handleCreateBill = async () => {
    if (!formData.bill_number || !formData.vendor.name || formData.items.length === 0) {
      showToast.error('Please fill bill number, vendor name, and add at least one item');
      return;
    }

    // PO Validation - Must select a PO or "VERBAL"
    console.log('DEBUG po_number at save time:', JSON.stringify(formData.po_number));
    if (!formData.po_number) {
      setShowPOWarning(true);
      showToast.error('Please select a Purchase Order or choose "VERBAL" for direct purchases.');
      return;
    }

    const totals = calculateTotals();
    const billData = {
      ...formData,
      is_verbal_purchase: formData.po_number === 'VERBAL',
      po_number: formData.po_number === 'VERBAL' ? null : formData.po_number,
      po_reference: formData.po_number, // Keep original selection for reference
      subtotal: parseFloat(totals.subtotal),
      cgst: parseFloat(totals.cgst),
      sgst: parseFloat(totals.sgst),
      igst: parseFloat(totals.igst),
      total_tax: parseFloat(totals.totalTax),
      other_charges: 0,
      round_off: 0,
      grand_total: parseFloat(totals.grandTotal),
      tds: selectedTds ? {
        section: selectedTds.old_section,
        code: selectedTds.code,
        rate_applied: tdsNoDeduction ? 0 : (selectedTds.rate_type === 'percentage' ? selectedTds.rate_value : ((parseFloat(tdsRateOverride) || 0) / 100)),
        deducted: !tdsNoDeduction,
        amount_deducted: tdsNoDeduction ? 0 : parseFloat(totals.tdsDeduction)
      } : null
    };

    // First check if any items are new (not in catalog)
    try {
      const checkResponse = await fetch(`${BACKEND_URL}/api/draft-products/check-items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData.items)
      });
      
      const checkData = await checkResponse.json();
      
      if (checkData.status === 'success' && checkData.new_items > 0) {
        // There are new items - show the popup
        setNewItemsToCreate(checkData.items_to_create.map(item => ({
          ...item,
          action: 'product', // default action: add as product
          brand: formData.vendor.name // default brand from vendor
        })));
        setPendingBillData(billData);
        setShowNewItemsModal(true);
        return;
      }
      
      // No new items, proceed with bill creation
      await saveBill(billData);
      
    } catch (error) {
      console.error('Check items failed:', error);
      // If check fails, still try to create the bill
      await saveBill(billData);
    }
  };

  const saveBill = async (billData) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/purchase-bills/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(billData)
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success(`Bill ${formData.bill_number} created successfully`);
        setShowCreateModal(false);
        resetForm();
        fetchBills();
        fetchStats();
      } else {
        showToast.error(data.detail || 'Failed to create bill');
      }
    } catch (error) {
      console.error('Create failed:', error);
      showToast.error('Failed to create purchase bill');
    }
  };

  const handleNewItemsDecision = async () => {
    // Filter items that need to be created (not skipped)
    const itemsToCreate = newItemsToCreate
      .filter(item => item.action !== 'skip')
      .map(item => ({
        item_name: item.item_name,
        model_number: item.item_name,
        hsn_code: item.hsn_code || '',
        brand: item.brand || formData.vendor.name,
        category: 'uncategorized',
        purchase_price: item.rate || 0,
        item_type: item.action, // 'product', 'part', or 'consumable'
        vendor_name: formData.vendor.name,
        source_bill_number: formData.bill_number
      }));

    // Create draft products
    if (itemsToCreate.length > 0) {
      try {
        const createResponse = await fetch(`${BACKEND_URL}/api/draft-products/bulk-create`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ items: itemsToCreate })
        });
        
        const createData = await createResponse.json();
        
        if (createData.status === 'success') {
          const productCount = itemsToCreate.filter(i => i.item_type === 'product').length;
          const partCount = itemsToCreate.filter(i => i.item_type === 'part' || i.item_type === 'consumable').length;
          
          if (productCount > 0) {
            showToast.success(`${productCount} draft product(s) created! Add images to publish to website.`);
          }
          if (partCount > 0) {
            showToast.info(`${partCount} part(s)/consumable(s) added to inventory.`);
          }
        }
      } catch (error) {
        console.error('Failed to create draft products:', error);
        showToast.error('Failed to create some products');
      }
    }

    // Now save the bill
    setShowNewItemsModal(false);
    await saveBill(pendingBillData);
    setPendingBillData(null);
    setNewItemsToCreate([]);
  };

  const updateNewItemAction = (index, action) => {
    setNewItemsToCreate(prev => prev.map((item, i) => 
      i === index ? { ...item, action } : item
    ));
  };

  const handleDeleteBill = async (billId) => {
    if (!window.confirm('Are you sure you want to delete this bill?')) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/purchase-bills/${billId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        showToast.success('Bill deleted successfully');
        fetchBills();
        fetchStats();
      } else {
        showToast.error('Failed to delete bill');
      }
    } catch (error) {
      showToast.error('Failed to delete bill');
    }
  };

  const handleUpdatePaymentStatus = async (billId, newStatus) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/purchase-bills/${billId}/payment-status?status=${newStatus}`, {
        method: 'PUT'
      });
      
      if (response.ok) {
        showToast.success(`Payment status updated to ${newStatus}`);
        fetchBills();
        fetchStats();
      }
    } catch (error) {
      showToast.error('Failed to update status');
    }
  };

  const resetForm = () => {
    setFormData({
      bill_number: '',
      bill_date: new Date().toISOString().split('T')[0],
      po_number: '',
      vendor: { name: '', phone: '', email: '', gst_number: '', address: '', city: '', state: '', pincode: '' },
      items: [],
      payment_mode: 'credit',
      payment_status: 'pending',
      due_date: '',
      notes: '',
      invoice_file_url: null
    });
    setScannedData(null);
    setSelectedTds(null);
    setTdsSearchTerm('');
    setTdsRateOverride('');
    setTdsNoDeduction(false);
    setShowTdsDropdown(false);
    setVendorSuggestions([]);
  };

  const getStatusBadge = (status) => {
    const styles = {
      pending: 'bg-yellow-100 text-yellow-800',
      partial: 'bg-blue-100 text-blue-800',
      paid: 'bg-green-100 text-green-800'
    };
    return styles[status] || 'bg-gray-100 text-gray-800';
  };

  const totals = calculateTotals();

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <FileText className="text-orange-500" />
              Purchase Bills
            </h1>
            <p className="text-gray-600 mt-1">Manage vendor invoices and purchase bills</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setShowGRNMatching(!showGRNMatching)}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                showGRNMatching 
                  ? 'bg-indigo-600 text-white' 
                  : 'bg-white border border-indigo-300 text-indigo-600 hover:bg-indigo-50'
              }`}
              data-testid="grn-matching-btn"
            >
              <Link2 size={20} />
              GRN Matching
            </button>
            <button
              onClick={() => setShowScanModal(true)}
              className="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 flex items-center gap-2 shadow-lg"
              data-testid="scan-invoice-btn"
            >
              <Camera size={20} />
              AI Scan Invoice
            </button>
            <button
              onClick={() => { resetForm(); setShowCreateModal(true); }}
              className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 flex items-center gap-2"
              data-testid="create-bill-btn"
            >
              <Plus size={20} />
              Add Bill Manually
            </button>
          </div>
        </div>

        {/* MSME Compliance Alerts */}
        {msmeCompliance && (msmeCompliance.compliance_summary?.critical_count > 0 || msmeCompliance.compliance_summary?.warning_count > 0) && (
          <div className="mb-6">
            {msmeCompliance.compliance_summary?.critical_count > 0 && (
              <div className="bg-red-50 border border-red-300 rounded-lg p-4 mb-3">
                <div className="flex items-start gap-3">
                  <AlertCircle className="text-red-600 flex-shrink-0" size={24} />
                  <div>
                    <h3 className="font-bold text-red-800">MSME Payment Overdue - Critical</h3>
                    <p className="text-red-700 text-sm">
                      {msmeCompliance.compliance_summary.critical_count} MSME invoice(s) overdue totaling 
                      ₹{msmeCompliance.compliance_summary.critical_amount?.toLocaleString('en-IN')}
                    </p>
                    <p className="text-red-600 text-xs mt-1">
                      As per MSMED Act 2006, interest at 3x bank rate is applicable on delayed payments
                    </p>
                  </div>
                </div>
              </div>
            )}
            {msmeCompliance.compliance_summary?.warning_count > 0 && (
              <div className="bg-yellow-50 border border-yellow-300 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <Clock className="text-yellow-600 flex-shrink-0" size={24} />
                  <div>
                    <h3 className="font-bold text-yellow-800">MSME Payments Due Soon</h3>
                    <p className="text-yellow-700 text-sm">
                      {msmeCompliance.compliance_summary.warning_count} MSME invoice(s) due within 7 days totaling 
                      ₹{msmeCompliance.compliance_summary.warning_amount?.toLocaleString('en-IN')}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <FileText className="text-blue-600" size={24} />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Total Bills</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_bills}</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-yellow-100 rounded-lg">
                  <Clock className="text-yellow-600" size={24} />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Pending</p>
                  <p className="text-2xl font-bold text-yellow-600">{stats.pending_bills}</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-green-100 rounded-lg">
                  <CheckCircle className="text-green-600" size={24} />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Paid</p>
                  <p className="text-2xl font-bold text-green-600">{stats.paid_bills}</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-red-100 rounded-lg">
                  <IndianRupee className="text-red-600" size={24} />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Pending Amount</p>
                  <p className="text-2xl font-bold text-red-600">₹{stats.pending_amount?.toLocaleString()}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* GRN Matching Panel */}
        {showGRNMatching && (
          <div className="mb-6">
            <GRNMatchingPanel onMatchComplete={fetchBills} />
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 space-y-4">
          {/* Primary Filters Row */}
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center gap-2">
              <Filter size={18} className="text-gray-500" />
              <select
                value={statusFilter}
                onChange={(e) => { setStatusFilter(e.target.value); setCurrentPage(1); }}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                data-testid="status-filter"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="partial">Partial</option>
                <option value="paid">Paid</option>
              </select>
            </div>
            <div className="flex-1 min-w-[300px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type="text"
                  placeholder="Search bill no, vendor, GST, items across ALL pages..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm"
                  data-testid="search-input"
                />
              </div>
            </div>
            <button
              onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
              className={`px-4 py-2 border rounded-lg flex items-center gap-2 transition ${
                showAdvancedFilters ? 'bg-blue-50 border-blue-300 text-blue-700' : 'border-gray-300 hover:bg-gray-50'
              }`}
            >
              <Calendar size={18} />
              {showAdvancedFilters ? 'Hide Filters' : 'Date & More'}
            </button>
            <button
              onClick={() => { fetchBills(); fetchStats(); }}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <RefreshCw size={18} />
              Refresh
            </button>
          </div>
          
          {/* Advanced Filters Row */}
          {showAdvancedFilters && (
            <div className="pt-4 border-t border-gray-200">
              <div className="flex flex-wrap gap-4 items-end">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">From Date</label>
                  <input
                    type="date"
                    value={dateFilter.from}
                    onChange={(e) => { setDateFilter({ ...dateFilter, from: e.target.value }); setCurrentPage(1); }}
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    data-testid="from-date-filter"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">To Date</label>
                  <input
                    type="date"
                    value={dateFilter.to}
                    onChange={(e) => { setDateFilter({ ...dateFilter, to: e.target.value }); setCurrentPage(1); }}
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    data-testid="to-date-filter"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">GST Number</label>
                  <input
                    type="text"
                    placeholder="e.g., 29AAECB..."
                    value={gstFilter}
                    onChange={(e) => { setGstFilter(e.target.value); setCurrentPage(1); }}
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-44"
                    data-testid="gst-filter"
                  />
                </div>
                <button
                  onClick={() => {
                    setSearchTerm('');
                    setStatusFilter('all');
                    setDateFilter({ from: '', to: '' });
                    setGstFilter('');
                    setCurrentPage(1);
                  }}
                  className="px-4 py-2 text-red-600 border border-red-200 rounded-lg hover:bg-red-50 text-sm"
                >
                  Clear All Filters
                </button>
              </div>
            </div>
          )}
          
          {/* Results Summary */}
          <div className="pt-2 text-sm text-gray-500">
            Showing {bills.length} of {totalBills} bills
            {(debouncedSearch || statusFilter !== 'all' || dateFilter.from || dateFilter.to || gstFilter) && (
              <span className="ml-2 text-blue-600">(filtered)</span>
            )}
          </div>
        </div>
      </div>

      {/* Bills Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto"></div>
            <p className="mt-4 text-gray-500">Loading bills...</p>
          </div>
        ) : bills.length === 0 ? (
          <EmptyState
            type="purchases"
            title="No Purchase Bills Found"
            description="Start by adding your first purchase bill or scan a vendor invoice"
            actionLabel="Add Purchase Bill"
            onAction={() => setShowCreateModal(true)}
          />
        ) : (
          <>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bill No</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vendor</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">GRN</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {bills.map((bill) => (
                  <tr key={bill.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{bill.bill_number}</div>
                      {bill.source === 'tally_import' && (
                        <span className="text-xs text-purple-600">Tally Import</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{bill.vendor?.name}</div>
                      {bill.vendor?.gst_number && (
                        <div className="text-xs text-gray-500">GST: {bill.vendor.gst_number}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(bill.bill_date).toLocaleDateString('en-IN')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-semibold text-gray-900">₹{(bill.grand_total || bill.total_amount || 0)?.toLocaleString()}</div>
                      <div className="text-xs text-gray-500">Tax: ₹{(bill.total_tax || 0)?.toLocaleString()}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {bill.linked_grn_number ? (
                        <div className="flex items-center gap-1">
                          <Link2 className="w-3 h-3 text-green-600" />
                          <span className="text-xs font-medium text-green-700 bg-green-50 px-2 py-0.5 rounded">
                            {bill.linked_grn_number}
                          </span>
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400">Not linked</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <select
                        value={bill.payment_status}
                        onChange={(e) => handleUpdatePaymentStatus(bill.id, e.target.value)}
                        className={`text-xs font-semibold rounded-full px-3 py-1 ${getStatusBadge(bill.payment_status)}`}
                      >
                        <option value="pending">Pending</option>
                        <option value="partial">Partial</option>
                        <option value="paid">Paid</option>
                      </select>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex gap-2">
                        <button
                          onClick={() => { setSelectedBill(bill); setShowDetailsModal(true); }}
                          className="text-blue-600 hover:text-blue-800"
                          title="View Details"
                        >
                          <Eye size={18} />
                        </button>
                        <button
                          onClick={() => handleDeleteBill(bill.id)}
                          className="text-red-600 hover:text-red-800"
                          title="Delete"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {totalPages > 1 && (
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={setCurrentPage}
              />
            )}
          </>
        )}
      </div>

      {/* AI Scan Modal */}
      {showScanModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold flex items-center gap-2">
                  <Sparkles className="text-purple-500" />
                  AI Invoice Scanner
                </h2>
                <button onClick={() => setShowScanModal(false)} className="text-gray-500 hover:text-gray-700">
                  <X size={24} />
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="border-2 border-dashed border-purple-300 rounded-lg p-8 text-center bg-purple-50">
                {scanning ? (
                  <div>
                    <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-500 border-t-transparent mx-auto mb-4"></div>
                    <p className="text-purple-700 font-medium">AI is reading your invoice...</p>
                    <p className="text-sm text-purple-500 mt-2">Extracting vendor, items, and tax details</p>
                  </div>
                ) : (
                  <>
                    <Camera size={48} className="mx-auto text-purple-400 mb-4" />
                    <p className="text-gray-700 mb-4">Upload a vendor invoice (PDF or Image)</p>
                    <p className="text-sm text-gray-500 mb-4">AI will automatically extract all details</p>
                    <input
                      type="file"
                      accept=".pdf,.png,.jpg,.jpeg,.webp"
                      onChange={(e) => e.target.files[0] && handleScanInvoice(e.target.files[0])}
                      className="hidden"
                      id="invoice-upload"
                    />
                    <label
                      htmlFor="invoice-upload"
                      className="inline-flex items-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg cursor-pointer hover:bg-purple-700 transition"
                    >
                      <Upload size={20} />
                      Select File
                    </label>
                  </>
                )}
              </div>
              <div className="mt-4 text-sm text-gray-500">
                <p><strong>Supported formats:</strong> PDF, PNG, JPG, JPEG, WebP</p>
                <p className="mt-1"><strong>AI extracts:</strong> Bill number, date, vendor details, all items, GST breakup</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create/Edit Bill Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 my-8">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold">
                  {scannedData ? '✨ Review Scanned Invoice' : 'Create Purchase Bill'}
                </h2>
                <button onClick={() => { setShowCreateModal(false); resetForm(); }} className="text-gray-500 hover:text-gray-700">
                  <X size={24} />
                </button>
              </div>
              {scannedData && (
                <p className="text-sm text-green-600 mt-2">AI extracted data - please review and edit if needed</p>
              )}
            </div>
            
            <div className="p-6 max-h-[70vh] overflow-y-auto">
              {/* Bill Details */}
              <div className="mb-6 bg-orange-50 border border-orange-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3 text-orange-900 flex items-center gap-2">
                  <FileText size={20} />
                  Bill Details
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Bill Number *</label>
                    <input
                      type="text"
                      value={formData.bill_number}
                      onChange={(e) => setFormData({ ...formData, bill_number: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="INV-12345"
                      data-testid="bill-number-input"
                    />
                    {checkingGRNMatch && (
                      <p className="text-xs text-gray-500 mt-1">Checking for matching GRN...</p>
                    )}
                    {invoiceGRNMatch && (
                      <div className="mt-2 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                        <p className="text-sm text-purple-900">
                          <span className="font-semibold">Match found:</span> GRN {invoiceGRNMatch.grn_number} from {invoiceGRNMatch.vendor_name}
                          {Array.isArray(invoiceGRNMatch.items) && ` (${invoiceGRNMatch.items.length} item${invoiceGRNMatch.items.length === 1 ? '' : 's'})`}
                        </p>
                        <button
                          type="button"
                          onClick={() => fillFromMatchedGRN(invoiceGRNMatch)}
                          className="mt-2 px-3 py-1.5 bg-purple-600 text-white text-xs font-medium rounded-lg hover:bg-purple-700"
                          data-testid="use-matched-grn-btn"
                        >
                          Use this GRN — fill vendor &amp; items
                        </button>
                      </div>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Bill Date *</label>
                    <input
                      type="date"
                      value={formData.bill_date}
                      onChange={(e) => setFormData({ ...formData, bill_date: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      PO Reference <span className="text-xs text-gray-500">(Select PO or Verbal)</span>
                    </label>
                    <select
                      value={formData.po_number}
                      onChange={(e) => {
                        setFormData({ ...formData, po_number: e.target.value });
                        setShowPOWarning(false);
                        // Auto-fill vendor from selected PO (not for Verbal)
                        if (e.target.value && e.target.value !== 'VERBAL') {
                          const selectedPO = pendingPOs.find(po => po.po_number === e.target.value);
                          if (selectedPO && selectedPO.vendor) {
                            setFormData(prev => ({ 
                              ...prev, 
                              po_number: e.target.value,
                              vendor: {
                                ...prev.vendor,
                                name: selectedPO.vendor.name || prev.vendor.name,
                                gst_number: selectedPO.vendor.gst_number || prev.vendor.gst_number,
                                msme_udyam_number: selectedPO.vendor.msme_udyam_number || prev.vendor.msme_udyam_number,
                                phone: selectedPO.vendor.phone || prev.vendor.phone,
                                email: selectedPO.vendor.email || prev.vendor.email,
                                address: selectedPO.vendor.address || prev.vendor.address,
                                city: selectedPO.vendor.city || prev.vendor.city,
                                state: selectedPO.vendor.state || prev.vendor.state
                              }
                            }));
                          }
                        }
                      }}
                      className={`w-full px-3 py-2 border rounded-lg ${showPOWarning ? 'border-red-500 bg-red-50' : 'border-gray-300'}`}
                    >
                      <option value="">-- Select Purchase Order --</option>
                      <option value="VERBAL" className="bg-yellow-100 font-medium">📞 VERBAL (No PO - Direct Purchase)</option>
                      <optgroup label="Pending Purchase Orders">
                        {pendingPOs.map(po => (
                          <option key={po.po_number} value={po.po_number}>
                            {po.po_number} - {po.vendor?.name} (₹{po.grand_total?.toLocaleString('en-IN')})
                          </option>
                        ))}
                      </optgroup>
                    </select>
                    {showPOWarning && (
                      <p className="text-red-600 text-xs mt-1 flex items-center gap-1">
                        <AlertCircle size={12} />
                        Please select a PO or choose "Verbal" for direct purchases.
                      </p>
                    )}
                    {formData.po_number === 'VERBAL' && (
                      <p className="text-yellow-600 text-xs mt-1 flex items-center gap-1">
                        <AlertCircle size={12} />
                        Verbal purchase - No PO linked. Ensure vendor details are correct.
                      </p>
                    )}
                  </div>
                </div>
                {pendingPOs.length === 0 && (
                  <div className="mt-3 p-3 bg-blue-100 border border-blue-300 rounded-lg text-blue-800 text-sm">
                    <AlertCircle size={16} className="inline mr-2" />
                    No pending POs available. You can select <strong>"VERBAL"</strong> for direct purchases without a PO, or create a Purchase Order first.
                  </div>
                )}
              </div>

              {/* Vendor Details */}
              <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3 text-blue-900 flex items-center gap-2">
                  <Building2 size={20} />
                  Vendor Details
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="Vendor Name *"
                      value={formData.vendor.name}
                      onChange={(e) => { setFormData({ ...formData, vendor: { ...formData.vendor, name: e.target.value } }); setShowVendorSuggestions(true); }}
                      onFocus={() => setShowVendorSuggestions(true)}
                      onBlur={() => setTimeout(() => setShowVendorSuggestions(false), 150)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      data-testid="vendor-name-input"
                    />
                    {showVendorSuggestions && vendorSuggestions.length > 0 && (
                      <div className="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                        {vendorSuggestions.map((v) => (
                          <div
                            key={v.id}
                            onMouseDown={() => {
                              setFormData({
                                ...formData,
                                vendor: {
                                  name: v.vendor_name || '',
                                  phone: v.phone || '',
                                  email: v.email || '',
                                  gst_number: v.gst_number || '',
                                  msme_udyam_number: v.msme_udyam_number || '',
                                  address: v.address || '',
                                  city: v.city || '',
                                  state: v.state || '',
                                  pincode: v.pincode || ''
                                }
                              });
                              if (v.tds && v.tds.section) {
                                const match = tdsRates.find(r => r.code === v.tds.code && r.old_section === v.tds.section);
                                setSelectedTds(match || null);
                                setTdsNoDeduction(!v.tds.deducted);
                                setTdsRateOverride(match && match.rate_type !== 'percentage' ? String((v.tds.rate_applied || 0) * 100) : '');
                              }
                              setShowVendorSuggestions(false);
                            }}
                            className="px-3 py-2 hover:bg-blue-50 cursor-pointer text-sm border-b border-gray-100"
                          >
                            <div className="font-medium">{v.vendor_name}</div>
                            {v.gst_number && <div className="text-xs text-gray-500">GST: {v.gst_number}</div>}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <div>
                    <input
                      type="text"
                      placeholder="GST Number"
                      value={formData.vendor.gst_number}
                      onChange={(e) => setFormData({ ...formData, vendor: { ...formData.vendor, gst_number: e.target.value.toUpperCase().trim() } })}
                      maxLength={15}
                      className={"px-3 py-2 border rounded-lg uppercase w-full " + (formData.vendor.gst_number && !isValidGstin(formData.vendor.gst_number) ? "border-red-500" : "border-gray-300")}
                    />
                    {formData.vendor.gst_number && !isValidGstin(formData.vendor.gst_number) && (
                      <p className="text-xs text-red-500 mt-1">Invalid GSTIN format</p>
                    )}
                  </div>
                  <input
                    type="text"
                    placeholder="MSME/Udyam Number (e.g., UDYAM-KA-01-0123456)"
                    value={formData.vendor.msme_udyam_number || ''}
                    onChange={(e) => setFormData({ ...formData, vendor: { ...formData.vendor, msme_udyam_number: e.target.value } })}
                    className="px-3 py-2 border border-blue-300 rounded-lg text-blue-700"
                  />
                  <input
                    type="text"
                    placeholder="Phone"
                    value={formData.vendor.phone}
                    onChange={(e) => setFormData({ ...formData, vendor: { ...formData.vendor, phone: e.target.value } })}
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                  />
                  <input
                    type="email"
                    placeholder="Email"
                    value={formData.vendor.email}
                    onChange={(e) => setFormData({ ...formData, vendor: { ...formData.vendor, email: e.target.value } })}
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                  />
                  <input
                    type="text"
                    placeholder="Address"
                    value={formData.vendor.address}
                    onChange={(e) => setFormData({ ...formData, vendor: { ...formData.vendor, address: e.target.value } })}
                    className="px-3 py-2 border border-gray-300 rounded-lg col-span-2"
                  />
                  <input
                    type="text"
                    placeholder="City"
                    value={formData.vendor.city}
                    onChange={(e) => setFormData({ ...formData, vendor: { ...formData.vendor, city: e.target.value } })}
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                  />
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="text"
                      placeholder="State"
                      value={formData.vendor.state}
                      onChange={(e) => setFormData({ ...formData, vendor: { ...formData.vendor, state: e.target.value } })}
                      className="px-3 py-2 border border-gray-300 rounded-lg"
                    />
                    <input
                      type="text"
                      placeholder="Pincode"
                      value={formData.vendor.pincode}
                      onChange={(e) => setFormData({ ...formData, vendor: { ...formData.vendor, pincode: e.target.value } })}
                      className="px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                </div>
              </div>

              {/* TDS Details */}
              <div className="mb-6 bg-purple-50 border border-purple-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3 text-purple-900 flex items-center gap-2">
                  <IndianRupee size={20} />
                  TDS Details
                </h3>
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Search TDS section..."
                    value={selectedTds ? selectedTds.old_section : tdsSearchTerm}
                    onChange={(e) => {
                      setTdsSearchTerm(e.target.value);
                      setSelectedTds(null);
                      setTdsRateOverride('');
                      setTdsNoDeduction(false);
                      setShowTdsDropdown(true);
                    }}
                    onFocus={() => { if (!selectedTds) setShowTdsDropdown(true); }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                  {selectedTds && (
                    <button
                      type="button"
                      onClick={() => { setSelectedTds(null); setTdsSearchTerm(''); setTdsRateOverride(''); setTdsNoDeduction(false); }}
                      className="absolute right-2 top-2 text-gray-400 hover:text-gray-600"
                    >
                      <X size={18} />
                    </button>
                  )}
                  {showTdsDropdown && !selectedTds && tdsSearchTerm.length > 0 && (
                    <div className="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-lg shadow-lg max-h-56 overflow-y-auto">
                      {tdsRates
                        .filter(r => r.old_section.toLowerCase().includes(tdsSearchTerm.toLowerCase()))
                        .map(r => (
                          <div
                            key={r.code + r.nature_of_payment}
                            onClick={() => {
                              setSelectedTds(r);
                              setTdsSearchTerm('');
                              setShowTdsDropdown(false);
                              setTdsRateOverride('');
                              setTdsNoDeduction(false);
                            }}
                            className="px-3 py-2 hover:bg-purple-50 cursor-pointer text-sm border-b border-gray-100"
                          >
                            <div className="font-medium">{r.old_section}</div>
                            <div className="text-xs text-gray-500">{r.nature_of_payment} — {r.rate_type === 'percentage' ? `${(r.rate_value * 100).toFixed(2)}%` : r.rate_text}</div>
                          </div>
                        ))}
                      {tdsRates.filter(r => r.old_section.toLowerCase().includes(tdsSearchTerm.toLowerCase())).length === 0 && (
                        <div className="px-3 py-2 text-sm text-gray-400">No matching section</div>
                      )}
                    </div>
                  )}
                </div>

                {selectedTds && (
                  <div className="mt-3 p-3 bg-white border border-purple-200 rounded-lg">
                    <p className="text-sm font-medium text-gray-800">{selectedTds.nature_of_payment}</p>
                    <p className="text-xs text-gray-500 mb-2">Code: {selectedTds.code} | Threshold: {selectedTds.threshold}</p>

                    <div className="flex items-center gap-3 mb-2">
                      <label className="text-sm text-gray-700">Rate:</label>
                      {selectedTds.rate_type === 'percentage' ? (
                        <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-sm font-medium">
                          {(selectedTds.rate_value * 100).toFixed(2)}%
                        </span>
                      ) : (
                        <>
                          <input
                            type="number"
                            step="0.01"
                            placeholder="Enter %"
                            value={tdsRateOverride}
                            onChange={(e) => setTdsRateOverride(e.target.value)}
                            disabled={tdsNoDeduction}
                            className="w-24 px-2 py-1 border border-gray-300 rounded text-sm disabled:bg-gray-100"
                          />
                          <span className="text-xs text-gray-500">(rate marked "{selectedTds.rate_text}" — enter manually)</span>
                        </>
                      )}
                    </div>

                    <label className="flex items-center gap-2 text-sm text-gray-700">
                      <input
                        type="checkbox"
                        checked={tdsNoDeduction}
                        onChange={(e) => setTdsNoDeduction(e.target.checked)}
                      />
                      No deduction (threshold already met elsewhere)
                    </label>
                  </div>
                )}
              </div>

              {/* Items */}
              <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3 text-green-900 flex items-center gap-2">
                  <Package size={20} />
                  Line Items
                </h3>
                
                {/* Add Item Form */}
                <div className="grid grid-cols-6 gap-2 mb-4">
                  <input
                    type="text"
                    placeholder="Product Name"
                    value={currentItem.product_name}
                    onChange={(e) => setCurrentItem({ ...currentItem, product_name: e.target.value })}
                    className="col-span-2 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  />
                  <input
                    type="text"
                    placeholder="HSN"
                    value={currentItem.hsn_code}
                    onChange={(e) => setCurrentItem({ ...currentItem, hsn_code: e.target.value })}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  />
                  <input
                    type="number"
                    placeholder="Qty"
                    value={currentItem.quantity}
                    onChange={(e) => setCurrentItem({ ...currentItem, quantity: parseInt(e.target.value) || 0 })}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    min="1"
                  />
                  <input
                    type="number"
                    placeholder="Rate"
                    value={currentItem.rate}
                    onChange={(e) => setCurrentItem({ ...currentItem, rate: parseFloat(e.target.value) || 0 })}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    min="0"
                  />
                  <button
                    onClick={addItemToList}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                  >
                    Add
                  </button>
                </div>

                {/* Items List */}
                {formData.items.length > 0 && (
                  <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                    <table className="min-w-full text-sm">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left">Product</th>
                          <th className="px-4 py-2 text-left">HSN</th>
                          <th className="px-4 py-2 text-right">Qty</th>
                          <th className="px-4 py-2 text-right">Rate</th>
                          <th className="px-4 py-2 text-right">Tax %</th>
                          <th className="px-4 py-2 text-right">Total</th>
                          <th className="px-4 py-2"></th>
                        </tr>
                      </thead>
                      <tbody>
                        {formData.items.map((item, index) => {
                          // item.rate is GST-INCLUSIVE (matches calculateTotals()'s assumption), so no tax added here.
                          const itemTotal = item.quantity * item.rate;
                          return (
                            <tr key={index} className="border-t">
                              <td className="px-4 py-2">{item.product_name}</td>
                              <td className="px-4 py-2">{item.hsn_code}</td>
                              <td className="px-4 py-2 text-right">{item.quantity}</td>
                              <td className="px-4 py-2 text-right">₹{item.rate}</td>
                              <td className="px-4 py-2 text-right">{item.tax_rate}%</td>
                              <td className="px-4 py-2 text-right font-medium">₹{itemTotal.toFixed(2)}</td>
                              <td className="px-4 py-2">
                                <button onClick={() => removeItem(index)} className="text-red-500 hover:text-red-700">
                                  <X size={16} />
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {/* Payment Details */}
              <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Payment Mode</label>
                  <select
                    value={formData.payment_mode}
                    onChange={(e) => setFormData({ ...formData, payment_mode: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="credit">Credit</option>
                    <option value="cash">Cash</option>
                    <option value="bank_transfer">Bank Transfer</option>
                    <option value="upi">UPI</option>
                    <option value="cheque">Cheque</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Payment Status</label>
                  <select
                    value={formData.payment_status}
                    onChange={(e) => setFormData({ ...formData, payment_status: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="pending">Pending</option>
                    <option value="partial">Partial</option>
                    <option value="paid">Paid</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
                  <input
                    type="date"
                    value={formData.due_date}
                    onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>

              <textarea
                placeholder="Notes (optional)"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                rows="2"
              />
            </div>

            {/* Footer with Totals */}
            <div className="p-6 border-t border-gray-200 bg-gray-50">
              <div className="flex justify-between items-start">
                <div className="text-sm space-y-1">
                  <div className="flex justify-between gap-8">
                    <span className="text-gray-600">Subtotal:</span>
                    <span className="font-medium">₹{totals.subtotal}</span>
                  </div>
                  {totals.isInterState ? (
                    <div className="flex justify-between gap-8">
                      <span className="text-gray-600">IGST:</span>
                      <span>₹{totals.igst}</span>
                    </div>
                  ) : (
                    <>
                      <div className="flex justify-between gap-8">
                        <span className="text-gray-600">CGST:</span>
                        <span>₹{totals.cgst}</span>
                      </div>
                      <div className="flex justify-between gap-8">
                        <span className="text-gray-600">SGST:</span>
                        <span>₹{totals.sgst}</span>
                      </div>
                    </>
                  )}
                  <div className="flex justify-between gap-8 text-lg font-bold pt-2 border-t">
                    <span>Grand Total:</span>
                    <span className="text-green-600">₹{totals.grandTotal}</span>
                  </div>
                  {selectedTds && (
                    <>
                      <div className="flex justify-between gap-8 text-sm text-purple-700 pt-1">
                        <span>TDS {tdsNoDeduction ? '(no deduction)' : `(${(selectedTds.rate_type === 'percentage' ? (selectedTds.rate_value * 100) : (parseFloat(tdsRateOverride) || 0)).toFixed(2)}%)`}:</span>
                        <span>- ₹{totals.tdsDeduction}</span>
                      </div>
                      <div className="flex justify-between gap-8 text-base font-semibold pt-1 border-t">
                        <span>Net Payable:</span>
                        <span className="text-purple-700">₹{totals.netPayable}</span>
                      </div>
                    </>
                  )}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => { setShowCreateModal(false); resetForm(); }}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleCreateBill}
                    className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 font-medium"
                    data-testid="save-bill-btn"
                  >
                    Save Bill
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Details Modal */}
      {showDetailsModal && selectedBill && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold">Bill Details - {selectedBill.bill_number}</h2>
                <button onClick={() => setShowDetailsModal(false)} className="text-gray-500 hover:text-gray-700">
                  <X size={24} />
                </button>
              </div>
            </div>
            <div className="p-6">
              {/* Vendor Info */}
              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-2">Vendor</h3>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="font-medium">{selectedBill.vendor?.name}</p>
                  {selectedBill.vendor?.gst_number && (
                    <p className="text-sm text-gray-600">GST: {selectedBill.vendor.gst_number}</p>
                  )}
                  <p className="text-sm text-gray-600">{selectedBill.vendor?.address}</p>
                  <p className="text-sm text-gray-600">
                    {selectedBill.vendor?.city}, {selectedBill.vendor?.state} - {selectedBill.vendor?.pincode}
                  </p>
                </div>
              </div>

              {/* Items */}
              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-2">Items</h3>
                <table className="min-w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left">Item</th>
                      <th className="px-4 py-2 text-right">Qty</th>
                      <th className="px-4 py-2 text-right">Rate</th>
                      <th className="px-4 py-2 text-right">Tax</th>
                      <th className="px-4 py-2 text-right">Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedBill.items?.map((item, idx) => (
                      <tr key={idx} className="border-t">
                        <td className="px-4 py-2">
                          {item.product_name}
                          {item.hsn_code && <span className="text-xs text-gray-500 block">HSN: {item.hsn_code}</span>}
                        </td>
                        <td className="px-4 py-2 text-right">{item.quantity}</td>
                        <td className="px-4 py-2 text-right">₹{item.rate}</td>
                        <td className="px-4 py-2 text-right">{item.tax_rate}%</td>
                        <td className="px-4 py-2 text-right font-medium">₹{item.total?.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Totals */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Subtotal:</span>
                    <span>₹{(selectedBill.subtotal || 0)?.toLocaleString()}</span>
                  </div>
                  {selectedBill.igst > 0 ? (
                    <div className="flex justify-between">
                      <span>IGST:</span>
                      <span>₹{selectedBill.igst?.toLocaleString()}</span>
                    </div>
                  ) : (
                    <>
                      <div className="flex justify-between">
                        <span>CGST:</span>
                        <span>₹{(selectedBill.cgst || selectedBill.total_tax / 2 || 0)?.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>SGST:</span>
                        <span>₹{(selectedBill.sgst || selectedBill.total_tax / 2 || 0)?.toLocaleString()}</span>
                      </div>
                    </>
                  )}
                  <div className="flex justify-between font-bold text-lg pt-2 border-t">
                    <span>Grand Total:</span>
                    <span className="text-green-600">₹{(selectedBill.grand_total || selectedBill.total_amount || 0)?.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* Invoice File Link */}
              {selectedBill.invoice_file_url && (
                <div className="mt-4">
                  <a
                    href={`${BACKEND_URL}${selectedBill.invoice_file_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800"
                  >
                    <Download size={18} />
                    View Original Invoice
                  </a>
                </div>
              )}
            </div>
            <div className="p-6 border-t bg-gray-50 flex justify-end">
              <button
                onClick={() => setShowDetailsModal(false)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* New Items Detection Modal */}
      {showNewItemsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[85vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-purple-600 to-indigo-600">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Package size={24} />
                New Items Detected!
              </h2>
              <p className="text-purple-100 mt-1">
                {newItemsToCreate.length} item(s) are not in your catalog. Choose what to do with each:
              </p>
            </div>
            
            <div className="p-4 max-h-[50vh] overflow-y-auto">
              <div className="space-y-3">
                {newItemsToCreate.map((item, index) => (
                  <div key={index} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{item.item_name}</h4>
                        <p className="text-sm text-gray-500">
                          HSN: {item.hsn_code || 'N/A'} | Qty: {item.quantity} | Rate: ₹{item.rate?.toLocaleString()}
                        </p>
                      </div>
                    </div>
                    
                    <div className="mt-3 flex flex-wrap gap-2">
                      <button
                        onClick={() => updateNewItemAction(index, 'product')}
                        className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-1.5 border transition-all ${
                          item.action === 'product' 
                            ? 'bg-blue-600 text-white border-blue-600' 
                            : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400'
                        }`}
                      >
                        <ShoppingBag size={14} />
                        Add as Product
                        <span className="text-xs opacity-75">(Website)</span>
                      </button>
                      <button
                        onClick={() => updateNewItemAction(index, 'part')}
                        className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-1.5 border transition-all ${
                          item.action === 'part' 
                            ? 'bg-orange-600 text-white border-orange-600' 
                            : 'bg-white text-gray-700 border-gray-300 hover:border-orange-400'
                        }`}
                      >
                        <Wrench size={14} />
                        Add as Part
                        <span className="text-xs opacity-75">(Backend)</span>
                      </button>
                      <button
                        onClick={() => updateNewItemAction(index, 'consumable')}
                        className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-1.5 border transition-all ${
                          item.action === 'consumable' 
                            ? 'bg-green-600 text-white border-green-600' 
                            : 'bg-white text-gray-700 border-gray-300 hover:border-green-400'
                        }`}
                      >
                        <Package size={14} />
                        Consumable
                      </button>
                      <button
                        onClick={() => updateNewItemAction(index, 'skip')}
                        className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-1.5 border transition-all ${
                          item.action === 'skip' 
                            ? 'bg-gray-600 text-white border-gray-600' 
                            : 'bg-white text-gray-700 border-gray-300 hover:border-gray-400'
                        }`}
                      >
                        <X size={14} />
                        Skip
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-4 border-t bg-gray-50">
              <div className="flex items-center justify-between mb-3">
                <div className="text-sm text-gray-600">
                  <span className="font-medium text-blue-600">
                    {newItemsToCreate.filter(i => i.action === 'product').length} Products
                  </span>
                  {' • '}
                  <span className="font-medium text-orange-600">
                    {newItemsToCreate.filter(i => i.action === 'part').length} Parts
                  </span>
                  {' • '}
                  <span className="font-medium text-green-600">
                    {newItemsToCreate.filter(i => i.action === 'consumable').length} Consumables
                  </span>
                  {' • '}
                  <span className="font-medium text-gray-600">
                    {newItemsToCreate.filter(i => i.action === 'skip').length} Skipped
                  </span>
                </div>
              </div>
              
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => { setShowNewItemsModal(false); setPendingBillData(null); }}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
                >
                  Cancel
                </button>
                <button
                  onClick={handleNewItemsDecision}
                  className="px-6 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 flex items-center gap-2"
                >
                  <CheckCircle size={18} />
                  Save Bill & Create Items
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PurchaseBillManagement;
