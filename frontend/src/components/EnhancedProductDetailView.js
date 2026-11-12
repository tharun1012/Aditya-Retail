import React, { useState, useEffect } from 'react';
import { 
  X, ChevronLeft, ChevronRight, Star, Heart, Share2, ShoppingCart, 
  Truck, Shield, RotateCcw, Award, MessageCircle, Zap, CheckCircle,
  Info, TrendingUp, Users, Clock, Phone
} from 'lucide-react';

const EnhancedProductDetailView = ({ product, isOpen, onClose, onAddToCart, onAIChat }) => {
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [selectedTab, setSelectedTab] = useState('overview');
  const [quantity, setQuantity] = useState(1);
  const [aiInsights, setAiInsights] = useState(null);
  const [showAiConsultant, setShowAiConsultant] = useState(false);

  // Generate AI Insights function
  const generateAIInsights = () => {
    if (!product) return;
    const aiFeatures = product.ai_features || {};
    const usageRecommendations = aiFeatures.usage_recommendations || [];
    
    const insights = {
      priceAnalysis: product.price < 50000 ? "Great Value" : product.price < 100000 ? "Premium Choice" : "Luxury Option",
      popularityScore: Math.floor(Math.random() * 30) + 70, // 70-100
      bestFor: usageRecommendations[0] || "Modern homes",
      energyRating: product.specifications?.energy_rating || "4 Star",
      installationComplexity: product.specifications?.installation?.includes("Professional") ? "Professional Required" : "Easy Setup"
    };
    setAiInsights(insights);
  };


  // Early return after all hooks
  if (!isOpen || !product) return null;

  const images = product.images && product.images.length > 0 ? product.images : [
    product.image || '/api/placeholder/400/400'
  ];

  const nextImage = () => {
    setSelectedImageIndex((prev) => (prev + 1) % images.length);
  };

  const prevImage = () => {
    setSelectedImageIndex((prev) => (prev - 1 + images.length) % images.length);
  };

  const discountPercentage = product.original_price 
    ? Math.round(((product.original_price - product.price) / product.original_price) * 100)
    : 0;

  // AI-Enhanced Features
  const aiFeatures = product.ai_features || {};
  const aiTips = aiFeatures.ai_consultant_tips || [];
  const usageRecommendations = aiFeatures.usage_recommendations || [];
  const smartFeatures = aiFeatures.smart_features || [];


  const handleAIConsultant = () => {
    setShowAiConsultant(true);
    onAIChat && onAIChat(product);
  };

  const TabButton = ({ id, label, icon: Icon, isActive, onClick }) => (
    <button
      onClick={() => onClick(id)}
      className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
        isActive 
          ? 'bg-blue-600 text-white' 
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
      }`}
    >
      <Icon className="w-4 h-4" />
      <span>{label}</span>
    </button>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-7xl h-[95vh] overflow-hidden flex flex-col">
        
        {/* Enhanced Header with AI Badge */}
        <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-blue-50 to-purple-50">
          <div className="flex items-center space-x-4">
            <h2 className="text-xl font-semibold text-gray-900">Product Details</h2>
            <div className="flex items-center space-x-2 bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
              <Zap className="w-4 h-4" />
              <span>AI-Enhanced</span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 p-6">
            
            {/* Enhanced Image Gallery */}
            <div className="space-y-4">
              {/* Main Image with AI-powered zoom hint */}
              <div className="relative aspect-square bg-gray-100 rounded-2xl overflow-hidden group">
                <img
                  src={images[selectedImageIndex]}
                  alt={product.name}
                  className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                />
                
                {/* Enhanced Navigation */}
                {images.length > 1 && (
                  <>
                    <button
                      onClick={prevImage}
                      className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-white/90 backdrop-blur-sm p-2 rounded-full shadow-lg hover:bg-white transition-colors"
                    >
                      <ChevronLeft className="w-6 h-6" />
                    </button>
                    <button
                      onClick={nextImage}
                      className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-white/90 backdrop-blur-sm p-2 rounded-full shadow-lg hover:bg-white transition-colors"
                    >
                      <ChevronRight className="w-6 h-6" />
                    </button>
                  </>
                )}

                {/* Image indicator */}
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
                  {images.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedImageIndex(index)}
                      className={`w-3 h-3 rounded-full transition-colors ${
                        index === selectedImageIndex ? 'bg-white' : 'bg-white/60'
                      }`}
                    />
                  ))}
                </div>

                {/* Quick Actions */}
                <div className="absolute top-4 right-4 flex flex-col space-y-2">
                  <button className="bg-white/90 backdrop-blur-sm p-2 rounded-full shadow-lg hover:bg-white transition-colors">
                    <Heart className="w-5 h-5 text-gray-600" />
                  </button>
                  <button className="bg-white/90 backdrop-blur-sm p-2 rounded-full shadow-lg hover:bg-white transition-colors">
                    <Share2 className="w-5 h-5 text-gray-600" />
                  </button>
                </div>
              </div>

              {/* Thumbnail Strip */}
              {images.length > 1 && (
                <div className="flex space-x-2 overflow-x-auto">
                  {images.map((image, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedImageIndex(index)}
                      className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-colors ${
                        index === selectedImageIndex ? 'border-blue-500' : 'border-gray-200'
                      }`}
                    >
                      <img
                        src={image}
                        alt={`View ${index + 1}`}
                        className="w-full h-full object-cover"
                      />
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Enhanced Product Information */}
            <div className="space-y-6">
              {/* Product Header with AI Insights */}
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="text-sm text-blue-600 font-medium mb-1">
                      {product.category}
                    </div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2 leading-tight">
                      {product.name}
                    </h1>
                    <div className="text-lg text-gray-600 mb-3">
                      by <span className="font-semibold">{product.brand}</span>
                    </div>
                  </div>
                  
                  {/* AI Popularity Score */}
                  {aiInsights && (
                    <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                      {aiInsights.popularityScore}% Popular
                    </div>
                  )}
                </div>

                {/* Enhanced Rating */}
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
                    <div className="flex items-center text-sm text-orange-600 bg-orange-100 px-2 py-1 rounded">
                      <TrendingUp className="w-4 h-4 mr-1" />
                      Fast Moving
                    </div>
                  )}
                </div>

                {/* Enhanced Pricing */}
                <div className="bg-gray-50 p-4 rounded-xl">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="text-3xl font-bold text-gray-900">
                      ₹{product.price?.toLocaleString()}
                    </span>
                    {product.original_price && (
                      <>
                        <span className="text-xl text-gray-500 line-through">
                          ₹{product.original_price.toLocaleString()}
                        </span>
                        <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm font-medium">
                          {discountPercentage}% OFF
                        </span>
                      </>
                    )}
                  </div>
                  
                  {aiInsights && (
                    <div className="text-sm text-gray-600">
                      <Zap className="w-4 h-4 inline mr-1" />
                      AI Analysis: <span className="font-medium">{aiInsights.priceAnalysis}</span>
                    </div>
                  )}
                </div>

                {/* Stock Status */}
                <div className={`flex items-center space-x-2 p-3 rounded-lg ${
                  product.stock > 10 ? 'bg-green-50 text-green-800' :
                  product.stock > 0 ? 'bg-yellow-50 text-yellow-800' :
                  'bg-red-50 text-red-800'
                }`}>
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-medium">
                    {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
                  </span>
                  {product.stock > 0 && product.stock <= 5 && (
                    <span className="text-sm">- Only few left!</span>
                  )}
                </div>

                {/* AI Consultant Button */}
                <button
                  onClick={handleAIConsultant}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-300 flex items-center justify-center space-x-2"
                >
                  <MessageCircle className="w-5 h-5" />
                  <span>Ask AI Product Consultant</span>
                </button>

                {/* Quantity and Add to Cart */}
                {product.stock > 0 && (
                  <div className="flex space-x-4">
                    <div className="flex items-center border rounded-lg">
                      <button
                        onClick={() => setQuantity(Math.max(1, quantity - 1))}
                        className="px-4 py-2 hover:bg-gray-100"
                      >
                        -
                      </button>
                      <span className="px-4 py-2 font-medium">{quantity}</span>
                      <button
                        onClick={() => setQuantity(Math.min(product.stock, quantity + 1))}
                        className="px-4 py-2 hover:bg-gray-100"
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
            </div>
          </div>

          {/* Enhanced Tabbed Content */}
          <div className="border-t">
            <div className="p-6">
              {/* Tab Navigation */}
              <div className="flex space-x-4 mb-6 overflow-x-auto">
                <TabButton
                  id="overview"
                  label="Overview"
                  icon={Info}
                  isActive={selectedTab === 'overview'}
                  onClick={setSelectedTab}
                />
                <TabButton
                  id="ai-insights"
                  label="AI Insights"
                  icon={Zap}
                  isActive={selectedTab === 'ai-insights'}
                  onClick={setSelectedTab}
                />
                <TabButton
                  id="specifications"
                  label="Specifications"
                  icon={CheckCircle}
                  isActive={selectedTab === 'specifications'}
                  onClick={setSelectedTab}
                />
                <TabButton
                  id="warranty"
                  label="Warranty & Support"
                  icon={Shield}
                  isActive={selectedTab === 'warranty'}
                  onClick={setSelectedTab}
                />
              </div>

              {/* Tab Content */}
              <div className="min-h-[300px]">
                {selectedTab === 'overview' && (
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-xl font-semibold mb-4">Product Description</h3>
                      <p className="text-gray-700 leading-relaxed">
                        {product.description}
                      </p>
                    </div>
                    
                    <div>
                      <h3 className="text-xl font-semibold mb-4">Key Features</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {product.features?.map((feature, index) => (
                          <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                            <span className="text-gray-800">{feature}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {selectedTab === 'ai-insights' && (
                  <div className="space-y-6">
                    <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-xl border">
                      <h3 className="text-xl font-semibold mb-4 flex items-center">
                        <Zap className="w-6 h-6 text-blue-600 mr-2" />
                        AI Product Analysis
                      </h3>
                      
                      {aiInsights && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                          <div className="bg-white p-4 rounded-lg">
                            <div className="text-sm text-gray-600">Price Category</div>
                            <div className="text-lg font-semibold text-blue-600">{aiInsights.priceAnalysis}</div>
                          </div>
                          <div className="bg-white p-4 rounded-lg">
                            <div className="text-sm text-gray-600">Best For</div>
                            <div className="text-lg font-semibold text-green-600">{aiInsights.bestFor}</div>
                          </div>
                          <div className="bg-white p-4 rounded-lg">
                            <div className="text-sm text-gray-600">Energy Rating</div>
                            <div className="text-lg font-semibold text-yellow-600">{aiInsights.energyRating}</div>
                          </div>
                          <div className="bg-white p-4 rounded-lg">
                            <div className="text-sm text-gray-600">Installation</div>
                            <div className="text-lg font-semibold text-purple-600">{aiInsights.installationComplexity}</div>
                          </div>
                        </div>
                      )}
                    </div>

                    {aiTips.length > 0 && (
                      <div>
                        <h4 className="text-lg font-semibold mb-3">AI Consultant Recommendations</h4>
                        <div className="space-y-3">
                          {aiTips.map((tip, index) => (
                            <div key={index} className="flex items-start space-x-3 p-4 bg-blue-50 rounded-lg">
                              <MessageCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                              <span className="text-gray-800">{tip}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {smartFeatures.length > 0 && (
                      <div>
                        <h4 className="text-lg font-semibold mb-3">Smart Features</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {smartFeatures.map((feature, index) => (
                            <div key={index} className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg">
                              <Zap className="w-5 h-5 text-purple-600 flex-shrink-0" />
                              <span className="text-gray-800">{feature}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {selectedTab === 'specifications' && (
                  <div>
                    <h3 className="text-xl font-semibold mb-4">Technical Specifications</h3>
                    <div className="bg-gray-50 rounded-xl p-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {product.specifications && Object.entries(product.specifications).map(([key, value]) => (
                          <div key={key} className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                            <span className="font-medium text-gray-700 capitalize">
                              {key.replace(/_/g, ' ')}
                            </span>
                            <span className="text-gray-900">{value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {selectedTab === 'warranty' && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="bg-green-50 p-4 rounded-lg text-center">
                        <Shield className="w-8 h-8 text-green-600 mx-auto mb-2" />
                        <div className="font-semibold text-green-900">
                          {product.warranty_details?.manufacturer || '2 Years'} Warranty
                        </div>
                        <div className="text-sm text-green-700">Comprehensive Coverage</div>
                      </div>
                      
                      <div className="bg-blue-50 p-4 rounded-lg text-center">
                        <Truck className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                        <div className="font-semibold text-blue-900">Free Installation</div>
                        <div className="text-sm text-blue-700">Professional Setup</div>
                      </div>
                      
                      <div className="bg-purple-50 p-4 rounded-lg text-center">
                        <Phone className="w-8 h-8 text-purple-600 mx-auto mb-2" />
                        <div className="font-semibold text-purple-900">24/7 Support</div>
                        <div className="text-sm text-purple-700">AI + Human Assistance</div>
                      </div>
                    </div>

                    <div className="bg-gray-50 p-6 rounded-xl">
                      <h4 className="font-semibold mb-3">What's Covered</h4>
                      <ul className="space-y-2 text-gray-700">
                        <li className="flex items-center"><CheckCircle className="w-4 h-4 text-green-600 mr-2" /> Manufacturing defects</li>
                        <li className="flex items-center"><CheckCircle className="w-4 h-4 text-green-600 mr-2" /> Electrical components</li>
                        <li className="flex items-center"><CheckCircle className="w-4 h-4 text-green-600 mr-2" /> Free repairs and replacements</li>
                        <li className="flex items-center"><CheckCircle className="w-4 h-4 text-green-600 mr-2" /> Nationwide service network</li>
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedProductDetailView;