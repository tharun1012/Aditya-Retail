import React, { useState, useEffect } from 'react';
import { 
  X, ChevronLeft, ChevronRight, Heart, Share2, 
  FileText, Download, Star, MessageCircle, ShoppingCart,
  CheckCircle, Info, Shield, Zap, Box, Ruler, Settings,
  Wifi, Package, TrendingUp, Award
} from 'lucide-react';
import ReviewsSection from './ReviewsSection';
import SEOHead, { SEOConfigs } from './SEOHead';
import Breadcrumbs, { generateBreadcrumbs } from './Breadcrumbs';

const BoschStyleProductDetail = ({ product, isOpen, onClose, onAddToCart, onAIChat }) => {
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [selectedTab, setSelectedTab] = useState('technical-overview');
  const [quantity, setQuantity] = useState(1);
  const [expandedSpec, setExpandedSpec] = useState(null);

  useEffect(() => {
    if (isOpen && product) {
      setSelectedImageIndex(0);
      setSelectedTab('technical-overview');
    }
  }, [isOpen, product]);

  if (!isOpen || !product) return null;

  const images = product.images && product.images.length > 0 ? product.images : [
    product.image || '/api/placeholder/600/600'
  ];

  const nextImage = () => {
    setSelectedImageIndex((prev) => (prev + 1) % images.length);
  };

  const prevImage = () => {
    setSelectedImageIndex((prev) => (prev - 1 + images.length) % images.length);
  };

  const discountPercentage = product?.original_price && product?.price
    ? Math.round(((product.original_price - product.price) / product.original_price) * 100)
    : 0;

  // Tab Button Component
  const TabButton = ({ id, label, isActive, onClick }) => (
    <button
      onClick={() => onClick(id)}
      className={`px-6 py-3 font-medium transition-all border-b-2 whitespace-nowrap ${
        isActive
          ? 'border-blue-600 text-blue-600 bg-blue-50'
          : 'border-transparent text-gray-600 hover:text-blue-600 hover:border-gray-300'
      }`}
    >
      {label}
    </button>
  );

  // Specification Group Component
  const SpecGroup = ({ title, icon: Icon, specs, isExpanded, onToggle }) => {
    if (!specs || typeof specs !== 'object') return null;
    
    return (
      <div className="border-b border-gray-200">
        <button
          onClick={onToggle}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center space-x-3">
            {Icon && <Icon className="w-5 h-5 text-blue-600" />}
            <span className="font-semibold text-gray-900">{title}</span>
          </div>
          <ChevronRight className={`w-5 h-5 text-gray-400 transition-transform ${
            isExpanded ? 'rotate-90' : ''
          }`} />
        </button>
        
        {isExpanded && (
          <div className="px-6 pb-4 bg-gray-50">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(specs).map(([key, value]) => (
                <div key={key} className="flex justify-between py-2 border-b border-gray-200">
                  <span className="text-gray-700 font-medium">{key}</span>
                  <span className="text-gray-900">
                    {typeof value === 'object' && value !== null
                      ? JSON.stringify(value, null, 2).substring(0, 100) + '...'
                      : String(value || 'N/A')}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  // Document Download Component
  const DocumentCard = ({ title, icon: Icon, fileUrl, fileSize }) => (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start space-x-4">
        <div className="bg-blue-50 p-3 rounded-lg">
          <Icon className="w-6 h-6 text-blue-600" />
        </div>
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900 mb-1">{title}</h4>
          {fileSize && <p className="text-sm text-gray-500 mb-2">{fileSize}</p>}
          <a
            href={fileUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            <Download className="w-4 h-4 mr-1" />
            Download PDF
          </a>
        </div>
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 overflow-y-auto">
      {/* SEO Meta Tags */}
      <SEOHead {...SEOConfigs.product(product)} />
      
      <div className="min-h-screen flex items-start justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-7xl my-8 relative">
          
          {/* Breadcrumbs */}
          {product.category && (
            <div className="px-6 pt-4">
              <Breadcrumbs items={generateBreadcrumbs.product(product, product.category)} />
            </div>
          )}
          
          {/* Header */}
          <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center z-10 rounded-t-2xl">
            <div className="flex items-center space-x-2">
              <h1 className="text-2xl font-bold text-gray-900">{product.name}</h1>
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
                Bosch Style
              </span>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          <div className="p-6">
            {/* Top Section - Product Images and Summary */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              
              {/* Image Gallery */}
              <div>
                <div className="relative bg-gray-100 rounded-xl overflow-hidden mb-4" style={{ height: '500px' }}>
                  <img
                    src={images[selectedImageIndex]}
                    alt={`${product.brand} ${product.name} - ${product.modelNumber || product.model_number || ''} - High resolution product image ${selectedImageIndex + 1} of ${images.length}`}
                    loading={selectedImageIndex === 0 ? 'eager' : 'lazy'}
                    decoding="async"
                    className="w-full h-full object-contain"
                  />
                  
                  {images.length > 1 && (
                    <>
                      <button
                        onClick={prevImage}
                        className="absolute left-4 top-1/2 -translate-y-1/2 bg-white bg-opacity-90 p-3 rounded-full shadow-lg hover:bg-opacity-100 transition-all"
                      >
                        <ChevronLeft className="w-6 h-6" />
                      </button>
                      <button
                        onClick={nextImage}
                        className="absolute right-4 top-1/2 -translate-y-1/2 bg-white bg-opacity-90 p-3 rounded-full shadow-lg hover:bg-opacity-100 transition-all"
                      >
                        <ChevronRight className="w-6 h-6" />
                      </button>
                    </>
                  )}

                  <div className="absolute top-4 right-4 flex space-x-2">
                    <button className="bg-white p-2 rounded-full shadow-lg hover:bg-gray-50">
                      <Heart className="w-5 h-5 text-gray-600" />
                    </button>
                    <button className="bg-white p-2 rounded-full shadow-lg hover:bg-gray-50">
                      <Share2 className="w-5 h-5 text-gray-600" />
                    </button>
                  </div>
                </div>

                {/* Thumbnail Gallery */}
                {images.length > 1 && (
                  <div className="grid grid-cols-6 gap-2">
                    {images.map((img, index) => (
                      <button
                        key={index}
                        onClick={() => setSelectedImageIndex(index)}
                        className={`border-2 rounded-lg overflow-hidden hover:border-blue-500 transition-colors ${
                          selectedImageIndex === index ? 'border-blue-600' : 'border-gray-200'
                        }`}
                      >
                        <img 
                          src={img} 
                          alt={`${product.brand} ${product.name} - Thumbnail view ${index + 1}`} 
                          loading="lazy"
                          decoding="async"
                          className="w-full h-16 object-cover" 
                        />
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Product Summary */}
              <div className="space-y-6">
                {/* Category Badge */}
                <div className="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                  {product.category}
                </div>

                {/* Product Title */}
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">
                    {product.name}
                  </h1>
                  <p className="text-lg text-gray-600">
                    by <span className="font-semibold text-gray-900">{product.brand}</span>
                  </p>
                  <p className="text-sm text-gray-500 mt-1">Model: {product.model}</p>
                </div>

                {/* Rating */}
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <div className="flex text-yellow-400">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Star key={star} className="w-5 h-5 fill-current" />
                      ))}
                    </div>
                    <span className="text-sm text-gray-600">
                      {product.customer_rating || 4.5} ({product.review_count || 0} reviews)
                    </span>
                  </div>
                  
                  {product.fast_moving && (
                    <div className="flex items-center text-sm text-orange-600 bg-orange-100 px-3 py-1 rounded-full">
                      <TrendingUp className="w-4 h-4 mr-1" />
                      Fast Moving
                    </div>
                  )}
                </div>

                {/* Pricing */}
                <div className="bg-gray-50 p-6 rounded-xl">
                  <div className="flex items-center space-x-4 mb-3">
                    <span className="text-4xl font-bold text-gray-900">
                      ₹{product.price?.toLocaleString()}
                    </span>
                    {product?.original_price && product.original_price > product.price && (
                      <>
                        <span className="text-2xl text-gray-500 line-through">
                          ₹{product.original_price?.toLocaleString()}
                        </span>
                        {discountPercentage > 0 && (
                          <span className="bg-red-100 text-red-800 px-3 py-1 rounded-lg text-sm font-bold">
                            {discountPercentage}% OFF
                          </span>
                        )}
                      </>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">
                    MRP (Inclusive of all taxes)
                  </p>
                </div>

                {/* Stock Status */}
                <div className={`flex items-center space-x-2 p-4 rounded-lg ${
                  product.stock > 10 ? 'bg-green-50 border border-green-200' :
                  product.stock > 0 ? 'bg-yellow-50 border border-yellow-200' :
                  'bg-red-50 border border-red-200'
                }`}>
                  <CheckCircle className={`w-5 h-5 ${
                    product.stock > 10 ? 'text-green-600' :
                    product.stock > 0 ? 'text-yellow-600' :
                    'text-red-600'
                  }`} />
                  <span className="font-semibold text-gray-900">
                    {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
                  </span>
                  {product.stock > 0 && product.stock <= 5 && (
                    <span className="text-sm text-gray-600">- Only few left!</span>
                  )}
                </div>

                {/* Quick Actions */}
                <div className="space-y-3">
                  {/* AI Consultant Button */}
                  <button
                    onClick={() => onAIChat && onAIChat(product)}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-300 flex items-center justify-center space-x-2"
                  >
                    <MessageCircle className="w-5 h-5" />
                    <span>Ask AI Product Consultant</span>
                  </button>

                  {/* Add to Cart */}
                  {product.stock > 0 && (
                    <div className="flex space-x-3">
                      <div className="flex items-center border-2 border-gray-300 rounded-lg">
                        <button
                          onClick={() => setQuantity(Math.max(1, quantity - 1))}
                          className="px-4 py-3 hover:bg-gray-100 font-bold text-lg"
                        >
                          -
                        </button>
                        <span className="px-6 py-3 font-semibold text-lg border-x-2 border-gray-300">{quantity}</span>
                        <button
                          onClick={() => setQuantity(Math.min(product.stock, quantity + 1))}
                          className="px-4 py-3 hover:bg-gray-100 font-bold text-lg"
                        >
                          +
                        </button>
                      </div>
                      
                      <button
                        onClick={() => onAddToCart({...product, quantity})}
                        className="flex-1 bg-red-700 text-white py-3 px-6 rounded-lg hover:bg-red-800 transition-colors font-semibold flex items-center justify-center space-x-2"
                      >
                        <ShoppingCart className="w-5 h-5" />
                        <span>Add to Cart</span>
                      </button>
                    </div>
                  )}
                </div>

                {/* Quick Info */}
                <div className="grid grid-cols-2 gap-3 pt-4 border-t">
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Package className="w-4 h-4" />
                    <span>Free Delivery</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Shield className="w-4 h-4" />
                    <span>
                      {(() => {
                        // Handle warranty field (could be string, object, or undefined)
                        if (typeof product?.warranty === 'string') {
                          return product.warranty;
                        } else if (product?.warranty?.period) {
                          return product.warranty.period;
                        } else if (typeof product?.warranty === 'object') {
                          // Handle malformed warranty object (stored as char array)
                          const warrantyStr = Object.values(product.warranty).join('');
                          return warrantyStr || '2 Years';
                        }
                        return '2 Years';
                      })()}
                      {' '}Warranty
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Award className="w-4 h-4" />
                    <span>Authorized Dealer</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <CheckCircle className="w-4 h-4" />
                    <span>Genuine Product</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Key Benefits Section */}
            {product?.key_features && Array.isArray(product.key_features) && product.key_features.length > 0 && (
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 py-8 px-6 border-t border-gray-200">
                <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                  <Award className="w-6 h-6 mr-2 text-blue-600" />
                  Benefits at a glance
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {product.key_features.slice(0, 6).map((benefit, index) => (
                    <div key={index} className="flex items-start space-x-3 bg-white p-4 rounded-lg shadow-sm border border-blue-100">
                      <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                        <CheckCircle className="w-5 h-5 text-white" />
                      </div>
                      <div className="flex-1">
                        <p className="text-gray-800 font-medium leading-relaxed">{benefit}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tabbed Content - Bosch Style */}
            <div className="border-t border-gray-200">
              {/* Tab Navigation */}
              <div className="flex space-x-1 overflow-x-auto border-b border-gray-200">
                <TabButton
                  id="technical-overview"
                  label="Technical Overview"
                  isActive={selectedTab === 'technical-overview'}
                  onClick={setSelectedTab}
                />
                <TabButton
                  id="highlights"
                  label="Highlights"
                  isActive={selectedTab === 'highlights'}
                  onClick={setSelectedTab}
                />
                <TabButton
                  id="special-features"
                  label="Special Features"
                  isActive={selectedTab === 'special-features'}
                  onClick={setSelectedTab}
                />
                <TabButton
                  id="specifications"
                  label="Specifications"
                  isActive={selectedTab === 'specifications'}
                  onClick={setSelectedTab}
                />
                <TabButton
                  id="manuals"
                  label="Manual and Documents"
                  isActive={selectedTab === 'manuals'}
                  onClick={setSelectedTab}
                />
                <TabButton
                  id="reviews"
                  label="Reviews"
                  isActive={selectedTab === 'reviews'}
                  onClick={setSelectedTab}
                />
              </div>

              {/* Tab Content */}
              <div className="py-8 px-6 min-h-[400px]">
                
                {/* Technical Overview Tab */}
                {selectedTab === 'technical-overview' && (
                  <div className="space-y-6">
                    <h3 className="text-2xl font-bold text-gray-900 mb-6">Technical Overview</h3>
                    
                    {product.short_description && (
                      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200 mb-6">
                        <p className="text-gray-800 leading-relaxed">{product.short_description}</p>
                      </div>
                    )}
                    
                    {product.description && !product.short_description && (
                      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200 mb-6">
                        <p className="text-gray-800 leading-relaxed">{product.description}</p>
                      </div>
                    )}
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {product.technical_overview && Object.entries(product.technical_overview).map(([key, value]) => (
                        <div key={key} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                          <div className="text-sm text-gray-600 mb-1 font-medium">{key}</div>
                          <div className="text-lg font-semibold text-gray-900">{value}</div>
                        </div>
                      ))}
                      {product?.specifications && !product?.technical_overview && typeof product.specifications === 'object' && Object.entries(product.specifications).slice(0, 9).map(([key, value]) => (
                        <div key={key} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                          <div className="text-sm text-gray-600 mb-1 font-medium">{key}</div>
                          <div className="text-lg font-semibold text-gray-900">
                            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    {!product.technical_overview && (!product?.specifications || Object.keys(product.specifications).length === 0) && (
                      <div className="text-center py-12">
                        <p className="text-gray-500">Technical specifications will be updated soon.</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Highlights Tab */}
                {selectedTab === 'highlights' && (
                  <div className="space-y-6">
                    <h3 className="text-2xl font-bold text-gray-900 mb-6">Highlights</h3>
                    
                    {product.long_description && (
                      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-xl border border-blue-100 mb-6">
                        <p className="text-gray-700 leading-relaxed whitespace-pre-line">{product.long_description}</p>
                      </div>
                    )}
                    
                    {product.description && !product.long_description && (
                      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-xl border border-blue-100 mb-6">
                        <p className="text-gray-700 leading-relaxed whitespace-pre-line">{product.description}</p>
                      </div>
                    )}
                    
                    <div className="space-y-8">
                      {product?.highlights && Array.isArray(product.highlights) && product.highlights.map((highlight, index) => (
                        <div key={index} className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-xl border border-blue-100">
                          <h4 className="text-xl font-bold text-gray-900 mb-3">{highlight.title}</h4>
                          <p className="text-gray-700 leading-relaxed">{highlight.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Special Features Tab */}
                {selectedTab === 'special-features' && (
                  <div className="space-y-6">
                    <h3 className="text-2xl font-bold text-gray-900 mb-6">Special Features</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {product.features?.map((feature, index) => (
                        <div key={index} className="flex items-start space-x-3 p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                          <Zap className="w-5 h-5 text-blue-600 flex-shrink-0 mt-1" />
                          <span className="text-gray-800">{feature}</span>
                        </div>
                      ))}
                      {product?.key_features && !product?.features && Array.isArray(product.key_features) && product.key_features.map((feature, index) => (
                        <div key={index} className="flex items-start space-x-3 p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                          <Zap className="w-5 h-5 text-blue-600 flex-shrink-0 mt-1" />
                          <span className="text-gray-800">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Specifications Tab - Expandable Groups */}
                {selectedTab === 'specifications' && (
                  <div className="space-y-4">
                    <h3 className="text-2xl font-bold text-gray-900 mb-6">Specifications</h3>
                    
                    {/* Show structured spec_groups if available */}
                    {product?.spec_groups && (
                      <div className="border border-gray-200 rounded-lg overflow-hidden">
                        {product?.spec_groups?.general && (
                          <SpecGroup
                            title="General"
                            icon={Info}
                            specs={product.spec_groups.general}
                            isExpanded={expandedSpec === 'general'}
                            onToggle={() => setExpandedSpec(expandedSpec === 'general' ? null : 'general')}
                          />
                        )}
                        
                        {product?.spec_groups?.size_weight && (
                          <SpecGroup
                            title="Size and Weight"
                            icon={Ruler}
                            specs={product.spec_groups.size_weight}
                            isExpanded={expandedSpec === 'size_weight'}
                            onToggle={() => setExpandedSpec(expandedSpec === 'size_weight' ? null : 'size_weight')}
                          />
                        )}
                        
                        {product?.spec_groups?.technical && (
                          <SpecGroup
                            title="Technical Specifications"
                            icon={Settings}
                            specs={product.spec_groups.technical}
                            isExpanded={expandedSpec === 'technical'}
                            onToggle={() => setExpandedSpec(expandedSpec === 'technical' ? null : 'technical')}
                          />
                        )}
                        
                        {product?.spec_groups?.comfort && (
                          <SpecGroup
                            title="Comfort"
                            icon={Box}
                            specs={product.spec_groups.comfort}
                            isExpanded={expandedSpec === 'comfort'}
                            onToggle={() => setExpandedSpec(expandedSpec === 'comfort' ? null : 'comfort')}
                          />
                        )}
                        
                        {product?.spec_groups?.connectivity && (
                          <SpecGroup
                            title="Connectivity"
                            icon={Wifi}
                            specs={product.spec_groups.connectivity}
                            isExpanded={expandedSpec === 'connectivity'}
                            onToggle={() => setExpandedSpec(expandedSpec === 'connectivity' ? null : 'connectivity')}
                          />
                        )}
                      </div>
                    )}
                    
                    {/* Show flat specifications if spec_groups not available */}
                    {!product?.spec_groups && product?.specifications && typeof product.specifications === 'object' && (
                      <div className="border border-gray-200 rounded-lg overflow-hidden">
                        <SpecGroup
                          title="Product Specifications"
                          icon={Settings}
                          specs={product.specifications}
                          isExpanded={expandedSpec === 'all_specs'}
                          onToggle={() => setExpandedSpec(expandedSpec === 'all_specs' ? null : 'all_specs')}
                        />
                      </div>
                    )}
                  </div>
                )}

                {/* Manual and Documents Tab */}
                {selectedTab === 'manuals' && (
                  <div className="space-y-6">
                    <h3 className="text-2xl font-bold text-gray-900 mb-6">Manual and Documents</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {product?.documents && Array.isArray(product.documents) && product.documents.map((doc, index) => (
                        <DocumentCard
                          key={index}
                          title={doc.title}
                          icon={doc.type === 'manual' ? FileText : Download}
                          fileUrl={doc.url}
                          fileSize={doc.size}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Reviews Tab */}
                {selectedTab === 'reviews' && (
                  <ReviewsSection productId={product.id} />
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BoschStyleProductDetail;
