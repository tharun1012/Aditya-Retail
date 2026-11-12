import React, { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Package, Image as ImageIcon, AlertCircle, Wand2, RefreshCw, 
  Search, Eye, Edit, Check, Filter, ChevronDown
} from 'lucide-react';
import { showToast } from '../utils/toast';
import EnhancedProductManager from './EnhancedProductManager';

const IncompleteProductsManager = () => {
  const [pmEdit, setPmEdit] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filterType, setFilterType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [enhancing, setEnhancing] = useState(false);
  const [bulkEnhancing, setBulkEnhancing] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);

  // URL-extraction modal state — "Step 3" of the offline-product workflow.
  // Admin pastes a competitor/brand URL, AI scrapes it, then the extracted
  // data is merged into the existing pending-review product.
  const [showExtractModal, setShowExtractModal] = useState(false);
  const [extractTargetProduct, setExtractTargetProduct] = useState(null);
  const [extractUrl, setExtractUrl] = useState('');
  const [extracting, setExtracting] = useState(false);
  const [extractedPreview, setExtractedPreview] = useState(null);
  const [applyingExtract, setApplyingExtract] = useState(false);

  // Approve-and-publish state (Step 4)
  const [publishingId, setPublishingId] = useState(null);

  const fetchProducts = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({ 
        page: currentPage, 
        limit: 20,
        filter_type: filterType
      });
      
      const response = await fetch(`${BACKEND_URL}/api/draft-products/incomplete?${params}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setProducts(data.products);
        setTotalPages(data.pages);
      }
    } catch (error) {
      console.error('Failed to fetch incomplete products:', error);
      showToast.error('Failed to load products');
    } finally {
      setLoading(false);
    }
  }, [currentPage, filterType]);

  const fetchSummary = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/draft-products/incomplete/summary`);
      const data = await response.json();
      if (data.status === 'success') {
        setSummary(data.summary);
      }
    } catch (error) {
      console.error('Failed to fetch summary:', error);
    }
  };

  useEffect(() => {
    fetchProducts();
    fetchSummary();
  }, [fetchProducts]);

  const handleAIEnhance = async (productId) => {
    setEnhancing(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/draft-products/incomplete/${productId}/ai-enhance`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success(data.message);
        fetchProducts();
        fetchSummary();
      } else {
        showToast.error(data.detail || 'Enhancement failed');
      }
    } catch (error) {
      showToast.error('AI enhancement failed');
    } finally {
      setEnhancing(false);
    }
  };

  const handleBulkAIEnhance = async () => {
    if (!window.confirm('AI will enhance up to 50 products with auto-generated categories and descriptions. Continue?')) {
      return;
    }
    
    setBulkEnhancing(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/draft-products/incomplete/bulk-ai-enhance?limit=50`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success(`Enhanced ${data.enhanced_count} products!`);
        fetchProducts();
        fetchSummary();
      } else {
        showToast.error(data.detail || 'Bulk enhancement failed');
      }
    } catch (error) {
      showToast.error('Bulk AI enhancement failed');
    } finally {
      setBulkEnhancing(false);
    }
  };

  // -------------------- Step 3: Extract from URL --------------------
  // Admin pastes a competitor/brand URL → backend scrapes + AI extracts
  // → preview shown → on confirm, merge into the existing product doc.
  const openExtractModal = (product) => {
    setExtractTargetProduct(product);
    setExtractUrl('');
    setExtractedPreview(null);
    setShowExtractModal(true);
  };

  const handleExtractFromUrl = async () => {
    const url = (extractUrl || '').trim();
    if (!url) {
      showToast.error('Please paste a product URL');
      return;
    }
    setExtracting(true);
    setExtractedPreview(null);
    try {
      const res = await fetch(`${BACKEND_URL}/api/products/extract-from-url`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      const data = await res.json();
      setExtractedPreview(data);
      showToast.success('Data extracted. Review and apply to product.');
    } catch (e) {
      showToast.error(`Extraction failed: ${e.message}`);
    } finally {
      setExtracting(false);
    }
  };

  const handleApplyExtractedData = async () => {
    if (!extractTargetProduct || !extractedPreview) return;
    setApplyingExtract(true);
    try {
      const payload = {
        // Send everything the extractor returned; backend will skip empty
        // values so existing fields aren't blanked out.
        name: extractedPreview.name,
        brand: extractedPreview.brand,
        category: extractedPreview.category,
        subcategory: extractedPreview.subcategory,
        model_number: extractedPreview.model_number,
        description: extractedPreview.description,
        short_description: extractedPreview.short_description,
        images: extractedPreview.images,
        specifications: extractedPreview.specifications,
        highlights: extractedPreview.highlights,
        special_features: extractedPreview.special_features,
        technical_overview: extractedPreview.technical_overview,
        energy_rating: extractedPreview.energy_rating,
        dimensions: extractedPreview.dimensions,
        documents: extractedPreview.documents,
        warranty: extractedPreview.warranty,
        source_url: extractUrl,
      };
      const res = await fetch(
        `${BACKEND_URL}/api/draft-products/incomplete/${extractTargetProduct.id}/apply-extracted-data`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        }
      );
      const data = await res.json();
      if (res.ok && data.status === 'success') {
        showToast.success(`Applied ${data.updated_fields?.length || 0} fields. Set price & stock, then publish.`);
        setShowExtractModal(false);
        setExtractTargetProduct(null);
        setExtractedPreview(null);
        setExtractUrl('');
        fetchProducts();
        fetchSummary();
      } else {
        showToast.error(data.detail || 'Failed to apply extracted data');
      }
    } catch (e) {
      showToast.error('Apply failed');
    } finally {
      setApplyingExtract(false);
    }
  };

  // -------------------- Step 4: Approve & Publish --------------------
  // Sets is_listed=True so the product becomes visible on adityaretail.com
  const handleApprovePublish = async (product) => {
    // Friendly client-side check — backend enforces this too
    const hasImage = !!(product.images?.length || product.image || product.image_url);
    if (!product.name || !hasImage) {
      showToast.error('Add a product name and at least one image before publishing.');
      return;
    }
    if (!window.confirm(`Publish "${product.name}" to the storefront?`)) return;
    setPublishingId(product.id);
    try {
      const res = await fetch(
        `${BACKEND_URL}/api/draft-products/incomplete/${product.id}/approve-publish`,
        { method: 'POST' }
      );
      const data = await res.json();
      if (res.ok && data.status === 'success') {
        showToast.success(`"${product.name}" is now live on the storefront.`);
        fetchProducts();
        fetchSummary();
      } else {
        showToast.error(data.detail || 'Could not publish product');
      }
    } catch (e) {
      showToast.error('Publish failed');
    } finally {
      setPublishingId(null);
    }
  };

  const filteredProducts = searchTerm
    ? products.filter(p => 
        p.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.brand?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : products;

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Incomplete Products</h1>
            <p className="text-gray-600">Products that need images, categories, or descriptions</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleBulkAIEnhance}
              disabled={bulkEnhancing}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2 disabled:opacity-50"
            >
              <Wand2 className="w-4 h-4" />
              {bulkEnhancing ? 'Enhancing...' : 'AI Enhance All'}
            </button>
            <button
              onClick={() => { fetchProducts(); fetchSummary(); }}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
            <button
              type="button"
              onClick={() => setFilterType('pending_review')}
              className={`bg-white rounded-xl p-4 shadow-sm border-l-4 border-purple-500 text-left transition-shadow hover:shadow-md ${filterType === 'pending_review' ? 'ring-2 ring-purple-400' : ''}`}
              data-testid="pending-review-tile"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">⏳ Pending Review</p>
                  <p className="text-2xl font-bold text-purple-600">{summary.pending_review ?? 0}</p>
                  <p className="text-[10px] text-gray-400 mt-0.5">From store / Tally / billing</p>
                </div>
                <AlertCircle className="w-8 h-8 text-purple-400" />
              </div>
            </button>
            <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-orange-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Total Incomplete</p>
                  <p className="text-2xl font-bold text-orange-600">{summary.total_incomplete}</p>
                </div>
                <Package className="w-8 h-8 text-orange-400" />
              </div>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-red-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Missing Image</p>
                  <p className="text-2xl font-bold text-red-600">{summary.missing_image}</p>
                </div>
                <ImageIcon className="w-8 h-8 text-red-400" />
              </div>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-yellow-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Missing Category</p>
                  <p className="text-2xl font-bold text-yellow-600">{summary.missing_category}</p>
                </div>
                <Filter className="w-8 h-8 text-yellow-400" />
              </div>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-blue-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Missing Description</p>
                  <p className="text-2xl font-bold text-blue-600">{summary.missing_description}</p>
                </div>
                <AlertCircle className="w-8 h-8 text-blue-400" />
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-xl p-4 shadow-sm mb-6">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by name or brand..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </div>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
            >
              <option value="all">All Issues</option>
              <option value="pending_review">⏳ Pending Review (offline)</option>
              <option value="no_image">Missing Image</option>
              <option value="no_category">Missing Category</option>
              <option value="no_description">Missing Description</option>
            </select>
          </div>
        </div>

        {/* Products Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin text-purple-600" />
          </div>
        ) : filteredProducts.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center shadow-sm">
            <Check className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-800 mb-2">All Products Complete!</h3>
            <p className="text-gray-600">No incomplete products found matching your criteria.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredProducts.map(product => (
              <div key={product.id} className="bg-white rounded-xl p-4 shadow-sm border hover:shadow-md transition-shadow">
                {/* Product Image or Placeholder */}
                <div className="w-full h-40 bg-gray-100 rounded-lg mb-3 flex items-center justify-center overflow-hidden">
                  {product.image_url || product.images?.[0] ? (
                    <img 
                      src={product.image_url || product.images[0]} 
                      alt={product.name}
                      className="w-full h-full object-contain"
                    />
                  ) : (
                    <div className="text-center text-gray-400">
                      <ImageIcon className="w-12 h-12 mx-auto mb-2" />
                      <span className="text-sm">No Image</span>
                    </div>
                  )}
                </div>

                {/* Product Info */}
                <h3 className="font-semibold text-gray-800 truncate mb-1" title={product.name}>
                  {product.name}
                </h3>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm text-gray-500">{product.brand || 'Unknown Brand'}</span>
                  {product.category && product.category !== 'uncategorized' && (
                    <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded">
                      {product.category.replace(/_/g, ' ')}
                    </span>
                  )}
                </div>

                {/* Missing Fields Badges */}
                <div className="flex flex-wrap gap-1 mb-3">
                  {product.missing_fields?.map(field => (
                    <span 
                      key={field} 
                      className={`px-2 py-0.5 text-xs rounded ${
                        field === 'image' ? 'bg-red-100 text-red-700' :
                        field === 'category' ? 'bg-yellow-100 text-yellow-700' :
                        field === 'description' ? 'bg-blue-100 text-blue-700' :
                        'bg-gray-100 text-gray-600'
                      }`}
                    >
                      No {field}
                    </span>
                  ))}
                </div>

                {/* Pending-review badge (auto-gated from offline workflow) */}
                {(product.is_listed === false || product.review_status === 'pending_review') && (
                  <div className="mb-2">
                    <span className="px-2 py-0.5 bg-orange-100 text-orange-800 text-xs rounded-full inline-flex items-center gap-1">
                      ⏳ Pending review · hidden from storefront
                    </span>
                  </div>
                )}

                {/* Actions */}
                <div className="grid grid-cols-2 gap-2 mt-2">
                  <button
                    onClick={() => setPmEdit({ product, action: 'extract' })}
                    data-testid={`extract-url-${product.id}`}
                    title="Paste a competitor URL and let AI extract specs, images, description"
                    className="px-3 py-1.5 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700 flex items-center justify-center gap-1"
                  >
                    🔗 Extract from URL
                  </button>
                  <button
                    onClick={() => setPmEdit({ product, action: 'enhance' })}
                    disabled={enhancing}
                    data-testid={`ai-enhance-${product.id}`}
                    title="AI fills in missing category/description from existing data"
                    className="px-3 py-1.5 bg-purple-600 text-white text-sm rounded hover:bg-purple-700 flex items-center justify-center gap-1 disabled:opacity-50"
                  >
                    <Wand2 className="w-3 h-3" />
                    AI Enhance
                  </button>
                  <button
                    onClick={() => setPmEdit({ product, action: 'edit' })}
                    data-testid={`edit-product-${product.id}`}
                    className="px-3 py-1.5 border rounded hover:bg-gray-50 flex items-center justify-center gap-1 text-sm"
                  >
                    <Edit className="w-3.5 h-3.5" /> Edit
                  </button>
                  <button
                    onClick={() => handleApprovePublish(product)}
                    disabled={publishingId === product.id}
                    data-testid={`publish-product-${product.id}`}
                    title="Make this product visible on the storefront"
                    className="px-3 py-1.5 bg-green-600 text-white text-sm rounded hover:bg-green-700 flex items-center justify-center gap-1 disabled:opacity-50"
                  >
                    <Check className="w-3.5 h-3.5" />
                    {publishingId === product.id ? 'Publishing…' : 'Approve & Publish'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-2 mt-6">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 border rounded-lg disabled:opacity-50 hover:bg-gray-50"
            >
              Previous
            </button>
            <span className="px-4 py-2">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 border rounded-lg disabled:opacity-50 hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        )}

        {pmEdit && (
          <div className="fixed inset-0 z-50 bg-black/50 overflow-y-auto">
            <div className="max-w-6xl mx-auto my-6 bg-white rounded-xl shadow-xl">
              <EnhancedProductManager
                embedded
                key={pmEdit.product.id + pmEdit.action}
                initialProduct={pmEdit.product}
                initialAction={pmEdit.action}
                onClose={() => setPmEdit(null)}
                onSaved={() => { fetchProducts(); fetchSummary(); }}
              />
            </div>
          </div>
        )}

        {/* Edit Modal */}
        {showEditModal && selectedProduct && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl w-full max-w-lg">
              <div className="p-6 border-b">
                <h2 className="text-xl font-semibold">Edit Product</h2>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Product Name</label>
                  <input
                    type="text"
                    value={selectedProduct.name || ''}
                    onChange={(e) => setSelectedProduct({...selectedProduct, name: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select
                    value={selectedProduct.category || ''}
                    onChange={(e) => setSelectedProduct({...selectedProduct, category: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg"
                  >
                    <option value="">Select Category</option>
                    <option value="refrigerator">Refrigerator</option>
                    <option value="washing_machine">Washing Machine</option>
                    <option value="dishwasher">Dishwasher</option>
                    <option value="oven">Oven</option>
                    <option value="microwave">Microwave</option>
                    <option value="cooktop">Cooktop / Hob</option>
                    <option value="chimney">Chimney / Hood</option>
                    <option value="dryer">Dryer</option>
                    <option value="coffee_machine">Coffee Machine</option>
                    <option value="air_fryer">Air Fryer</option>
                    <option value="mixer_grinder">Mixer / Grinder</option>
                    <option value="vacuum_cleaner">Vacuum Cleaner</option>
                    <option value="power_tools">Power Tools</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    value={selectedProduct.description || ''}
                    onChange={(e) => setSelectedProduct({...selectedProduct, description: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
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
                  onClick={async () => {
                    try {
                      const response = await fetch(`${BACKEND_URL}/api/products/${selectedProduct.id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                          name: selectedProduct.name,
                          category: selectedProduct.category,
                          description: selectedProduct.description
                        })
                      });
                      if (response.ok) {
                        showToast.success('Product updated!');
                        setShowEditModal(false);
                        fetchProducts();
                        fetchSummary();
                      } else {
                        showToast.error('Update failed');
                      }
                    } catch (error) {
                      showToast.error('Failed to update');
                    }
                  }}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ============== Step 3: Extract from URL modal ============== */}
        {showExtractModal && extractTargetProduct && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b sticky top-0 bg-white">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-xl font-semibold">🔗 AI Extract from Product URL</h3>
                    <p className="text-sm text-gray-500 mt-1">
                      Updating: <span className="font-medium">{extractTargetProduct.name}</span>
                    </p>
                  </div>
                  <button
                    onClick={() => { setShowExtractModal(false); setExtractedPreview(null); }}
                    className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
                    aria-label="Close"
                  >
                    ×
                  </button>
                </div>
              </div>

              <div className="p-6 space-y-4">
                <p className="text-sm text-gray-600">
                  Paste a manufacturer or competitor product page URL (e.g. Bosch, Croma, Amazon).
                  AI will scrape it and pre-fill name, brand, specs, images, description &amp; documents.
                  You only need to set the <strong>price &amp; stock</strong> afterwards.
                </p>

                <div className="flex gap-2">
                  <input
                    type="url"
                    value={extractUrl}
                    onChange={(e) => setExtractUrl(e.target.value)}
                    placeholder="https://www.example.com/product/..."
                    className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                    data-testid="extract-url-input"
                  />
                  <button
                    onClick={handleExtractFromUrl}
                    disabled={extracting}
                    data-testid="extract-url-submit"
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-2 whitespace-nowrap"
                  >
                    {extracting ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Extracting…
                      </>
                    ) : (
                      <>
                        <Wand2 className="w-4 h-4" />
                        Extract
                      </>
                    )}
                  </button>
                </div>

                {/* Extracted data preview */}
                {extractedPreview && (
                  <div className="border rounded-lg p-4 bg-gray-50 space-y-3 max-h-80 overflow-y-auto">
                    <p className="text-xs uppercase tracking-wide text-gray-500 font-semibold">Extracted Preview</p>

                    {extractedPreview.images?.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-500 mb-1">Images ({extractedPreview.images.length})</p>
                        <div className="flex gap-2 overflow-x-auto">
                          {extractedPreview.images.slice(0, 6).map((img, idx) => (
                            <img
                              key={idx}
                              src={img}
                              alt={`extracted ${idx}`}
                              className="w-20 h-20 object-contain border rounded bg-white flex-shrink-0"
                            />
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                      {extractedPreview.name && (
                        <div><span className="text-gray-500">Name:</span> <span className="font-medium">{extractedPreview.name}</span></div>
                      )}
                      {extractedPreview.brand && (
                        <div><span className="text-gray-500">Brand:</span> <span className="font-medium">{extractedPreview.brand}</span></div>
                      )}
                      {extractedPreview.model_number && (
                        <div><span className="text-gray-500">Model:</span> {extractedPreview.model_number}</div>
                      )}
                      {extractedPreview.category && (
                        <div><span className="text-gray-500">Category:</span> {extractedPreview.category}</div>
                      )}
                      {extractedPreview.energy_rating && (
                        <div><span className="text-gray-500">Energy:</span> {extractedPreview.energy_rating}</div>
                      )}
                      {extractedPreview.warranty?.period && (
                        <div><span className="text-gray-500">Warranty:</span> {extractedPreview.warranty.period}</div>
                      )}
                    </div>

                    {extractedPreview.description && (
                      <div>
                        <p className="text-xs text-gray-500 mb-1">Description</p>
                        <p className="text-sm text-gray-700 line-clamp-3">{extractedPreview.description}</p>
                      </div>
                    )}

                    {extractedPreview.highlights?.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-500 mb-1">Highlights</p>
                        <ul className="list-disc list-inside text-sm text-gray-700 space-y-0.5">
                          {extractedPreview.highlights.slice(0, 5).map((h, idx) => (
                            <li key={idx}>{h}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div className="p-6 border-t flex justify-end gap-3 sticky bottom-0 bg-white">
                <button
                  onClick={() => { setShowExtractModal(false); setExtractedPreview(null); }}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleApplyExtractedData}
                  disabled={!extractedPreview || applyingExtract}
                  data-testid="apply-extracted-data-btn"
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                >
                  <Check className="w-4 h-4" />
                  {applyingExtract ? 'Applying…' : 'Apply to Product'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default IncompleteProductsManager;
