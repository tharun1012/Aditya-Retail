import authFetch from './authFetch';
import ComboPriceEdit from './ComboPriceEdit';
import ComboPdfImport from './ComboPdfImport';
import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { Package, Plus, Edit, Trash2, Calendar, TrendingDown, Gift, Home, Sparkles, Eye, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import AdminHeader from './AdminHeader';


const ComboOffersManagement = () => {
  const navigate = useNavigate();
  const [offers, setOffers] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [aiGenerating, setAiGenerating] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    product_ids: [],
    discount_type: 'percentage',
    discount_value: 0,
    valid_from: new Date().toISOString().split('T')[0],
    valid_until: '',
    is_active: true,
    // Banner display options
    show_on_banner: false,
    banner_title: '',
    banner_subtitle: '',
    banner_cta_text: 'Shop Now',
    banner_gradient: 'from-purple-600 to-indigo-600',
    banner_priority: 1
  });
  const [productSearch, setProductSearch] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch offers
      const offersRes = await fetch(`${BACKEND_URL}/api/combo-offers/`, { cache: 'no-store' });
      const offersData = await offersRes.json();
      setOffers(offersData.offers || []);

      // Fetch products
      const productsRes = await fetch(`${BACKEND_URL}/api/products`);
      const productsData = await productsRes.json();
      setProducts(productsData.products || productsData || []);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${BACKEND_URL}/api/combo-offers/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        alert('✅ Combo offer created successfully!');
        setShowModal(false);
        setFormData({
          name: '',
          description: '',
          product_ids: [],
          discount_type: 'percentage',
          discount_value: 0,
          valid_from: new Date().toISOString().split('T')[0],
          valid_until: '',
          is_active: true,
          show_on_banner: false,
          banner_title: '',
          banner_subtitle: '',
          banner_cta_text: 'Shop Now',
          banner_gradient: 'from-purple-600 to-indigo-600',
          banner_priority: 1
        });
        fetchData();
      }
    } catch (error) {
      console.error('Error creating offer:', error);
      alert('Failed to create combo offer');
    }
  };

  const handleAIGenerate = async () => {
    setAiGenerating(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/combo-offers/ai/create?discount_percent=15&show_on_banner=true`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        alert(`✅ AI Combo Created: ${data.combo.name}\nSavings: ₹${data.combo.savings?.toLocaleString('en-IN')}\n\nAdded to homepage banner!`);
        fetchData();
      } else {
        alert('Failed to generate AI combo: ' + (data.detail || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error generating AI combo:', error);
      alert('Failed to generate AI combo');
    } finally {
      setAiGenerating(false);
    }
  };

  const callAdmin = async (path, method, body) => {
    const r = await authFetch(`${BACKEND_URL}/api/combo-offers/${path}`, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined
    });
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(d.detail || `Request failed (${r.status})`);
    return d;
  };

  const toggleBannerSafe = async (offer) => {
    try { await callAdmin(`${offer.id}/banner`, 'PUT', { show_on_banner: !offer.show_on_banner }); await fetchData(); }
    catch (e) { alert('Banner update failed: ' + e.message); }
  };

  const toggleActiveSafe = async (offer) => {
    try { await callAdmin(`${offer.id}/active`, 'PUT', { is_active: !offer.is_active }); await fetchData(); }
    catch (e) { alert('Status update failed: ' + e.message); }
  };

  const deleteSafe = async (offer) => {
    if (!window.confirm(`Delete "${offer.name}" permanently?`)) return;
    try { await callAdmin(`${offer.id}/permanent`, 'DELETE'); await fetchData(); }
    catch (e) { alert('Delete failed: ' + e.message); }
  };

  // eslint-disable-next-line no-unused-vars
  const toggleBannerDisplay = async (offerId, currentValue) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/combo-offers/${offerId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ show_on_banner: !currentValue })
      });
      const data = await response.json();
      if (data.status === 'success') {
        fetchData();
      }
    } catch (error) {
      console.error('Error toggling banner display:', error);
    }
  };

  // eslint-disable-next-line no-unused-vars
  const handleDelete = async (offerId) => {
    if (!window.confirm('Are you sure you want to delete this combo offer?')) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/combo-offers/${offerId}`, {
        method: 'DELETE'
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        alert('Combo offer deleted!');
        fetchData();
      }
    } catch (error) {
      console.error('Error deleting offer:', error);
    }
  };

  const toggleProductSelection = (productId) => {
    setFormData(prev => ({
      ...prev,
      product_ids: prev.product_ids.includes(productId)
        ? prev.product_ids.filter(id => id !== productId)
        : [...prev.product_ids, productId]
    }));
  };

  const calculatePreview = () => {
    const selectedProducts = products.filter(p => formData.product_ids.includes(p.id));
    const totalPrice = selectedProducts.reduce((sum, p) => sum + (p.price || 0), 0);
    
    let finalPrice = totalPrice;
    let savings = 0;
    
    if (formData.discount_type === 'percentage') {
      savings = totalPrice * (formData.discount_value / 100);
      finalPrice = totalPrice - savings;
    } else {
      savings = formData.discount_value;
      finalPrice = totalPrice - formData.discount_value;
    }
    
    return { totalPrice, finalPrice, savings, selectedProducts };
  };

  const preview = calculatePreview();

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-700"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <AdminHeader 
        title="Combo Offers" 
        icon={Gift}
        breadcrumb={[{ label: 'Combo Offers' }]}
      />
      
      <div className="p-6">
        {/* Header */}
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Gift className="w-8 h-8 text-amber-700" />
              Combo & Bundle Offers
            </h1>
            <p className="text-gray-600 mt-2">Create special pricing for product bundles</p>
          </div>
          <div className="flex gap-3">
            <ComboPdfImport onDone={fetchData} />
            <button
              onClick={handleAIGenerate}
              disabled={aiGenerating}
              className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg hover:from-purple-700 hover:to-pink-700 transition-colors flex items-center gap-2 disabled:opacity-50"
              data-testid="ai-generate-combo-btn"
            >
              <Sparkles className={`w-5 h-5 ${aiGenerating ? 'animate-spin' : ''}`} />
              {aiGenerating ? 'Generating...' : 'AI Generate Combo'}
            </button>
            <button
              onClick={() => setShowModal(true)}
              className="bg-amber-700 text-white px-6 py-3 rounded-lg hover:bg-amber-800 transition-colors flex items-center gap-2"
              data-testid="create-combo-btn"
            >
              <Plus className="w-5 h-5" />
              Create Combo Offer
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-gray-900">{offers.length}</div>
          <div className="text-sm text-gray-600">Total Combos</div>
        </div>
        <div className="bg-green-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-green-700">
            {offers.filter(o => o.is_active).length}
          </div>
          <div className="text-sm text-green-600">Active Offers</div>
        </div>
        <div className="bg-amber-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-amber-700">
            {offers.reduce((sum, o) => sum + (o.orders_count || 0), 0)}
          </div>
          <div className="text-sm text-amber-600">Total Orders</div>
        </div>
        <div className="bg-blue-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-blue-700">
            ₹{offers.reduce((sum, o) => sum + (o.revenue_generated || 0), 0).toLocaleString()}
          </div>
          <div className="text-sm text-blue-600">Revenue Generated</div>
        </div>
      </div>

      {/* Offers Grid */}
      {offers.length === 0 ? (
        <div className="bg-white rounded-lg shadow-lg p-12 text-center">
          <Gift className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Combo Offers Yet</h3>
          <p className="text-gray-600 mb-6">
            Create your first combo offer to boost sales with bundle discounts
          </p>
          <button
            onClick={() => setShowModal(true)}
            className="bg-amber-700 text-white px-6 py-3 rounded-lg hover:bg-amber-800 transition-colors flex items-center gap-2 mx-auto"
          >
            <Plus className="w-5 h-5" />
            Create First Combo Offer
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {offers.map((offer) => (
          <div key={offer.id} className={`bg-white rounded-lg shadow-lg overflow-hidden ${offer.show_on_banner ? 'ring-2 ring-purple-500' : ''}`}>
            <div className="bg-gradient-to-r from-amber-600 to-orange-500 text-white p-4">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-lg">{offer.name}</h3>
                  <p className="text-sm opacity-90">{offer.description}</p>
                </div>
                <div className="flex flex-col gap-1 items-end">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    offer.is_active ? 'bg-green-500' : 'bg-gray-500'
                  }`}>
                    {offer.is_active ? 'Active' : 'Inactive'}
                  </span>
                  {offer.show_on_banner && (
                    <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-purple-600 flex items-center gap-1">
                      <Eye className="w-3 h-3" /> On Banner
                    </span>
                  )}
                  {offer.ai_generated && (
                    <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-600 flex items-center gap-1">
                      <Sparkles className="w-3 h-3" /> AI
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="p-4">
              {/* Products */}
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Products in Bundle:</h4>
                <div className="space-y-1">
                  {offer.products?.slice(0, 3).map((product) => (
                    <div key={product.id} className="text-sm text-gray-600 flex items-center gap-2">
                      <Package className="w-3 h-3" />
                      {product.name}
                    </div>
                  ))}
                  {offer.products?.length > 3 && (
                    <div className="text-xs text-gray-500">+{offer.products.length - 3} more</div>
                  )}
                </div>
              </div>

              {/* Pricing */}
              <div className="bg-gray-50 rounded-lg p-3 mb-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">Original Price:</span>
                  <span className="line-through text-gray-500">₹{offer.original_price?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-semibold text-gray-700">Combo Price:</span>
                  <span className="text-xl font-bold text-green-600">₹{offer.final_price?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-amber-700 font-semibold">You Save:</span>
                  <span className="text-sm font-bold text-amber-700">₹{offer.savings?.toLocaleString()}</span>
                </div>
              </div>

              {/* Validity */}
              <div className="flex items-center gap-2 text-xs text-gray-600 mb-4">
                <Calendar className="w-4 h-4" />
                <span>Valid till {new Date(offer.valid_until).toLocaleDateString()}</span>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  onClick={() => toggleBannerSafe(offer)}
                  className={`flex-1 py-2 rounded-lg transition-colors flex items-center justify-center gap-2 ${
                    offer.show_on_banner 
                      ? 'bg-purple-100 text-purple-700 hover:bg-purple-200' 
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                  data-testid={`toggle-banner-${offer.id}`}
                >
                  <Eye className="w-4 h-4" />
                  {offer.show_on_banner ? 'On Banner' : 'Add to Banner'}
                </button>
                <button onClick={() => toggleActiveSafe(offer)} data-testid={`toggle-active-${offer.id}`} className="flex-1 bg-gray-100 text-gray-700 py-2 rounded-lg hover:bg-gray-200">{offer.is_active ? 'Deactivate' : 'Activate'}</button>
                <ComboPriceEdit offer={offer} onDone={fetchData} />
                <button
                  onClick={() => deleteSafe(offer)}
                  className="flex-1 bg-red-50 text-red-600 py-2 rounded-lg hover:bg-red-100 transition-colors flex items-center justify-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </div>
            </div>
          </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full my-8">
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <Gift className="w-6 h-6 text-amber-700" />
                Create Combo Offer
              </h2>

              <form onSubmit={handleSubmit}>
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Offer Name</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                      placeholder="e.g., Kitchen Appliance Combo"
                      required
                    />
                  </div>

                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                      rows="2"
                      placeholder="Describe the combo offer..."
                    ></textarea>
                  </div>

                  {/* Product Selection */}
                  <div className="col-span-2">
                    <div className="flex items-center justify-between mb-2">
                      <label className="block text-sm font-medium text-gray-700">
                        Select Products ({formData.product_ids.length} selected out of {products.length} total)
                      </label>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => {
                            const filteredProducts = products.filter(p => 
                              !productSearch || 
                              p.name?.toLowerCase().includes(productSearch.toLowerCase()) ||
                              p.brand?.toLowerCase().includes(productSearch.toLowerCase())
                            );
                            setFormData({...formData, product_ids: filteredProducts.map(p => p.id)});
                          }}
                          className="text-xs text-blue-600 hover:text-blue-800"
                        >
                          Select All
                        </button>
                        <button
                          type="button"
                          onClick={() => setFormData({...formData, product_ids: []})}
                          className="text-xs text-red-600 hover:text-red-800"
                        >
                          Clear All
                        </button>
                      </div>
                    </div>
                    
                    {/* Search Products */}
                    <input
                      type="text"
                      value={productSearch}
                      onChange={(e) => setProductSearch(e.target.value)}
                      placeholder="Search products by name or brand..."
                      className="w-full px-4 py-2 border rounded-lg mb-3 focus:ring-2 focus:ring-amber-600"
                    />
                    
                    <div className="border rounded-lg p-4 max-h-96 overflow-y-auto">
                      <div className="grid grid-cols-2 gap-2">
                        {products
                          .filter(p => 
                            !productSearch || 
                            p.name?.toLowerCase().includes(productSearch.toLowerCase()) ||
                            p.brand?.toLowerCase().includes(productSearch.toLowerCase())
                          )
                          .map((product) => (
                          <label
                            key={product.id}
                            className={`flex items-center gap-2 p-2 rounded cursor-pointer ${
                              formData.product_ids.includes(product.id) ? 'bg-amber-50 border-2 border-amber-500' : 'bg-gray-50'
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={formData.product_ids.includes(product.id)}
                              onChange={() => toggleProductSelection(product.id)}
                              className="w-4 h-4 text-amber-600"
                            />
                            <div className="flex-1">
                              <div className="text-sm font-medium">{product.name}</div>
                              <div className="text-xs text-gray-500">{product.brand} - ₹{product.price?.toLocaleString()}</div>
                            </div>
                          </label>
                        ))}
                      </div>
                      {products.filter(p => 
                        !productSearch || 
                        p.name?.toLowerCase().includes(productSearch.toLowerCase()) ||
                        p.brand?.toLowerCase().includes(productSearch.toLowerCase())
                      ).length === 0 && (
                        <div className="text-center text-gray-500 py-4">
                          No products found matching "{productSearch}"
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Discount */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Discount Type</label>
                    <select
                      value={formData.discount_type}
                      onChange={(e) => setFormData({...formData, discount_type: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                    >
                      <option value="percentage">Percentage (%)</option>
                      <option value="fixed">Fixed Amount (₹)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Discount Value</label>
                    <input
                      type="number"
                      value={formData.discount_value}
                      onChange={(e) => setFormData({...formData, discount_value: parseFloat(e.target.value)})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                      min="0"
                      step="0.01"
                      required
                    />
                  </div>

                  {/* Validity */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Valid From</label>
                    <input
                      type="date"
                      value={formData.valid_from}
                      onChange={(e) => setFormData({...formData, valid_from: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Valid Until</label>
                    <input
                      type="date"
                      value={formData.valid_until}
                      onChange={(e) => setFormData({...formData, valid_until: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                      required
                    />
                  </div>
                </div>

                {/* Preview */}
                {preview.selectedProducts.length > 0 && (
                  <div className="mb-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border-2 border-green-200">
                    <h3 className="font-semibold text-gray-900 mb-2">Offer Preview</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Original Price:</span>
                        <span className="line-through text-gray-500">₹{preview.totalPrice.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-semibold text-gray-700">Final Price:</span>
                        <span className="text-xl font-bold text-green-600">₹{preview.finalPrice.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm font-semibold text-amber-700">Savings:</span>
                        <span className="font-bold text-amber-700">₹{preview.savings.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 bg-amber-700 text-white px-4 py-2 rounded-lg hover:bg-amber-800"
                    disabled={formData.product_ids.length < 2}
                  >
                    Create Combo Offer
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
};

export default ComboOffersManagement;
