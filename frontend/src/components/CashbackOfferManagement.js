import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Upload, Trash2, Wallet, CreditCard, Building2, Gift, Percent, Loader2, RefreshCw, ArrowLeft, Plus, Pencil, ShieldCheck, Sun, Smartphone } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import OfferEditModal from './OfferEditModal';

const API = process.env.REACT_APP_BACKEND_URL;

const TYPE_META = {
  bank_offer: { label: 'Bank Offer', icon: CreditCard, tint: 'bg-blue-100 text-blue-700' },
  no_cost_emi: { label: 'No Cost EMI', icon: Building2, tint: 'bg-emerald-100 text-emerald-700' },
  cashback: { label: 'Cashback', icon: Wallet, tint: 'bg-amber-100 text-amber-700' },
  partner_offer: { label: 'Partner Offer', icon: Gift, tint: 'bg-purple-100 text-purple-700' },
  exchange_offer: { label: 'Exchange Offer', icon: Percent, tint: 'bg-orange-100 text-orange-700' },
  extended_warranty: { label: 'Extended Warranty', icon: ShieldCheck, tint: 'bg-indigo-100 text-indigo-700' },
  seasonal_offer: { label: 'Limited Time', icon: Sun, tint: 'bg-rose-100 text-rose-700' },
  upi_offer: { label: 'UPI Offer', icon: Smartphone, tint: 'bg-teal-100 text-teal-700' },
};

const CashbackOfferManagement = () => {
  const navigate = useNavigate();
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [brand, setBrand] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingOffer, setEditingOffer] = useState(null);
  const fileRef = useRef(null);

  const openCreate = () => { setEditingOffer(null); setModalOpen(true); };
  const openEdit = (offer) => { setEditingOffer(offer); setModalOpen(true); };
  const closeModal = (didSave) => { setModalOpen(false); setEditingOffer(null); if (didSave) loadOffers(); };

  const loadOffers = async () => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/api/offers/admin/list`);
      setOffers(r.data?.offers || []);
    } catch (e) {
      setError('Failed to load offers');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOffers();
  }, []);

  const handleUpload = async () => {
    setError('');
    setMessage('');
    if (!fileRef.current?.files?.[0]) {
      setError('Please choose a PDF or Excel file');
      return;
    }
    const file = fileRef.current.files[0];
    const name = file.name.toLowerCase();
    if (!name.endsWith('.pdf') && !name.endsWith('.xlsx') && !name.endsWith('.xls')) {
      setError('Only PDF, XLSX, or XLS files are supported');
      return;
    }
    setUploading(true);
    const fd = new FormData();
    fd.append('file', file);
    fd.append('brand', brand);
    try {
      const r = await axios.post(`${API}/api/offers/admin/upload-pdf`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const count = r.data?.offers_extracted || 0;
      setMessage(`✅ Extracted ${count} offer${count === 1 ? '' : 's'} from ${file.name}`);
      if (fileRef.current) fileRef.current.value = '';
      setBrand('');
      loadOffers();
    } catch (e) {
      setError(e.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const toggleActive = async (offer) => {
    try {
      await axios.put(`${API}/api/offers/admin/${offer.id}`, { is_active: !offer.is_active });
      loadOffers();
    } catch (e) {
      setError('Failed to update offer');
    }
  };

  const deleteOffer = async (id) => {
    if (!id) { setError('Offer id missing — please refresh'); loadOffers(); return; }
    if (!window.confirm('Delete this offer permanently?')) return;
    try {
      await axios.delete(`${API}/api/offers/admin/${id}`);
      setMessage('Offer deleted');
    } catch (e) {
      // 404 means already gone — treat as success; still refresh
      if (e?.response?.status === 404) {
        setMessage('Offer was already removed');
      } else {
        setError(`Delete failed: ${e?.response?.data?.detail || e.message || 'unknown'}`);
      }
    } finally {
      loadOffers();
    }
  };

  const bulkDeleteByBrand = async () => {
    const b = window.prompt('Enter brand name to delete ALL offers for (case-insensitive). Leave empty to cancel:');
    if (!b || !b.trim()) return;
    if (!window.confirm(`Permanently delete ALL offers for brand "${b}"?`)) return;
    try {
      const r = await axios.post(`${API}/api/offers/admin/bulk-delete`, { brand: b.trim() });
      setMessage(`Deleted ${r.data?.deleted || 0} offer(s) for brand "${b}"`);
      loadOffers();
    } catch (e) {
      setError(e.response?.data?.detail || 'Bulk delete failed');
    }
  };

  const bulkDeleteAll = async () => {
    if (!window.confirm('⚠️ Delete ALL offers in the database? This cannot be undone.')) return;
    const confirm2 = window.prompt('Type DELETE ALL to confirm:');
    if (confirm2 !== 'DELETE ALL') { setError('Cancelled — confirmation text did not match.'); return; }
    try {
      const r = await axios.post(`${API}/api/offers/admin/bulk-delete`, { all: true });
      setMessage(`Deleted ${r.data?.deleted || 0} offer(s)`);
      loadOffers();
    } catch (e) {
      setError(e.response?.data?.detail || 'Bulk delete failed');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50" data-testid="cashback-offer-mgmt">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button
          onClick={() => navigate('/admin')}
          className="mb-4 inline-flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Admin
        </button>

        <div className="flex items-start justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Cashback & Bank Offers</h1>
            <p className="text-sm text-gray-600 mt-1">
              Upload brand PDFs/Excel — AI will auto-extract. Or create offers manually for Extended Warranty, Exchange, etc.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              data-testid="add-offer-btn"
              onClick={openCreate}
              className="inline-flex items-center gap-1 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-md px-3 py-1.5"
            >
              <Plus className="w-4 h-4" /> Add Offer
            </button>
            <button
              onClick={loadOffers}
              className="inline-flex items-center gap-1 text-sm bg-white border border-gray-300 rounded-md px-3 py-1.5 hover:bg-gray-50"
            >
              <RefreshCw className="w-4 h-4" /> Refresh
            </button>
            <button
              data-testid="bulk-delete-brand-btn"
              onClick={bulkDeleteByBrand}
              className="inline-flex items-center gap-1 text-sm bg-white border border-red-300 text-red-700 rounded-md px-3 py-1.5 hover:bg-red-50"
            >
              <Trash2 className="w-4 h-4" /> Delete by Brand
            </button>
            <button
              data-testid="bulk-delete-all-btn"
              onClick={bulkDeleteAll}
              className="inline-flex items-center gap-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded-md px-3 py-1.5"
            >
              <Trash2 className="w-4 h-4" /> Delete All
            </button>
          </div>
        </div>

        {/* Upload Card */}
        <div className="bg-white border border-gray-200 rounded-xl p-5 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Upload className="w-5 h-5 text-blue-600" /> Upload Brand Offer File (PDF or Excel)
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Brand (hint)</label>
              <input
                data-testid="brand-input"
                type="text"
                value={brand}
                onChange={(e) => setBrand(e.target.value)}
                placeholder="e.g. Bosch, Samsung, LG"
                className="w-full text-sm border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-medium text-gray-700 mb-1">PDF or Excel file</label>
              <input
                data-testid="pdf-file-input"
                ref={fileRef}
                type="file"
                accept=".pdf,.xlsx,.xls,application/pdf,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel"
                className="w-full text-sm border border-gray-300 rounded-md px-3 py-1.5 bg-white"
              />
            </div>
          </div>
          <div className="flex items-center justify-between mt-4">
            <div className="text-xs text-gray-500">
              AI-powered — supports PDF, XLSX, XLS. Extraction takes ~10-20 seconds.
            </div>
            <button
              onClick={handleUpload}
              disabled={uploading}
              data-testid="upload-pdf-btn"
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white text-sm font-medium rounded-md px-4 py-2"
            >
              {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
              {uploading ? 'Extracting…' : 'Upload & Extract'}
            </button>
          </div>
          {message && <div className="mt-3 text-sm text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-md px-3 py-2">{message}</div>}
          {error && <div className="mt-3 text-sm text-red-700 bg-red-50 border border-red-200 rounded-md px-3 py-2">{error}</div>}
        </div>

        {/* Offers Table */}
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">All Offers</h2>
            <span className="text-xs text-gray-500">{offers.length} total</span>
          </div>
          {loading ? (
            <div className="p-8 text-center text-sm text-gray-500">Loading…</div>
          ) : offers.length === 0 ? (
            <div className="p-8 text-center text-sm text-gray-500">
              No offers yet. Upload a PDF above to get started.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-gray-50 text-gray-600 text-xs uppercase">
                  <tr>
                    <th className="px-4 py-2 text-left">Type</th>
                    <th className="px-4 py-2 text-left">Title</th>
                    <th className="px-4 py-2 text-left">Brand</th>
                    <th className="px-4 py-2 text-left">Categories</th>
                    <th className="px-4 py-2 text-left">Amount</th>
                    <th className="px-4 py-2 text-left">Products</th>
                    <th className="px-4 py-2 text-left">Status</th>
                    <th className="px-4 py-2 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {offers.map((o) => {
                    const meta = TYPE_META[o.offer_type] || TYPE_META.cashback;
                    const Icon = meta.icon;
                    return (
                      <tr key={o.id} className="border-t border-gray-100 hover:bg-gray-50">
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium ${meta.tint}`}>
                            <Icon className="w-3 h-3" />
                            {meta.label}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-medium text-gray-900 max-w-xs truncate" title={o.title}>{o.title}</td>
                        <td className="px-4 py-3 text-gray-700">{o.brand || '—'}</td>
                        <td className="px-4 py-3 text-gray-600 text-xs">{(o.categories || []).join(', ') || '—'}</td>
                        <td className="px-4 py-3 text-gray-700">
                          {o.amount_upto
                            ? o.amount_type === 'percentage'
                              ? `${o.amount_upto}%`
                              : `₹${Number(o.amount_upto).toLocaleString('en-IN')}`
                            : '—'}
                        </td>
                        <td className="px-4 py-3 text-gray-700">{(o.product_ids || []).length}</td>
                        <td className="px-4 py-3">
                          <button
                            onClick={() => toggleActive(o)}
                            className={`text-xs px-2 py-0.5 rounded-full font-medium ${o.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-200 text-gray-600'}`}
                          >
                            {o.is_active ? 'Active' : 'Inactive'}
                          </button>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <div className="inline-flex items-center gap-2">
                            <button
                              onClick={() => openEdit(o)}
                              data-testid={`offer-edit-${o.id}`}
                              className="text-blue-600 hover:text-blue-700"
                              title="Edit"
                            >
                              <Pencil className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => deleteOffer(o.id)}
                              className="text-red-600 hover:text-red-700"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
      <OfferEditModal open={modalOpen} offer={editingOffer} onClose={closeModal} />
    </div>
  );
};

export default CashbackOfferManagement;
