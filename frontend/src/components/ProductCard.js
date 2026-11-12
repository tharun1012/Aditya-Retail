import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShoppingCart, Heart, Eye, Star, Bot } from 'lucide-react';
import { getProductImage, handleImageError } from '../utils/imageUtils';
import DeliveryEtaBadge from './DeliveryEtaBadge';
import OfferTag from './OfferTag';
import { useCart } from '../hooks/useCart';

const ProductCard = ({ product, onAddToCart, onViewProduct, onAISalesChat }) => {
  const navigate = useNavigate();
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const { cartItems, updateQuantity } = useCart();

  // Guard: Return null if product is invalid
  if (!product || typeof product !== 'object') {
    console.error('ProductCard: Invalid product object', product);
    return null;
  }
  const cartItem = cartItems.find(item => (item.product || item).id === product.id);
  const cartQuantity = cartItem ? cartItem.quantity : 0;

  const discountPercentage = product?.originalPrice && product?.price && product.originalPrice > product.price
    ? Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100)
    : 0;

  const handleAIRecommendation = (e) => {
    e.stopPropagation();
    if (onAISalesChat && typeof onAISalesChat === 'function') {
      onAISalesChat(product);
    }
  };

const getProductUrl = (product) => {
  const categorySlug = product.category
    ? product.category.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
    : 'product';

  let productSlug = product.slug;
  if (!productSlug && product.name) {
    const nameHasBrand = product.brand &&
      product.name.toLowerCase().startsWith(product.brand.toLowerCase());
    const rawSlug = `${(!nameHasBrand && product.brand) ? product.brand + '-' : ''}${product.name}`
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();
    productSlug = rawSlug.length > 60
      ? rawSlug.slice(0, 60).replace(/-[^-]*$/, '')
      : rawSlug;
    productSlug = productSlug.replace(/^-+|-+$/g, '');
  }

  const brandSlug = product.brand
    ? product.brand.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
    : null;

  if (productSlug && brandSlug) {
    return `/${categorySlug}/${brandSlug}/${productSlug}`;
  }
  if (productSlug) {
    return `/${categorySlug}/${productSlug}`;
  }

  // Only use model_number if it looks like an actual model number,
  // NOT a brand name (guards against bad data like modelNumber === "Bosch")
  const modelNumber = product.model_number || product.modelNumber;
  const looksLikeRealModelNumber =
    modelNumber &&
    modelNumber.toLowerCase() !== (product.brand || '').toLowerCase() &&
    /[0-9]/.test(modelNumber); // real model numbers almost always contain a digit

  if (looksLikeRealModelNumber) {
    return `/${categorySlug}/${modelNumber.toLowerCase()}`;
  }

  // Safe fallback — always resolvable, never collides with brand-filter URLs
  return `/product/${(product.id || product._id || '').toLowerCase()}`;
};

  const handleProductClick = () => {
    // Navigate to product detail page with SEO-friendly URL
    const url = getProductUrl(product);
    navigate(url);
    
    // Also call onViewProduct if provided (for tracking, etc.)
    if (onViewProduct && typeof onViewProduct === 'function') {
      onViewProduct(product);
    }
  };

  return (
    <div
      className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group relative cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleProductClick}
    >
      {/* Product Image */}
      <div className="relative aspect-square overflow-hidden bg-gray-100 flex items-center justify-center">
        <img
          src={getProductImage(product, 0)}
          alt={`${product.brand} ${product.name} - ${product.modelNumber || ''} - ${product.category}`}
          loading="lazy"
          decoding="async"
          className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
          onError={(e) => handleImageError(e, product)}
        />
        
        {/* Discount Badge */}
        {discountPercentage > 0 && (
          <div className="absolute top-3 left-3 bg-red-600 text-white px-2 py-1 rounded-md text-xs font-semibold">
            -{discountPercentage}%
          </div>
        )}

        {/* Stock Status */}
        {(product?.stock !== undefined || product?.stock_quantity !== undefined || product?.current_stock !== undefined) && (
          <div className={`absolute top-3 right-3 px-2 py-1 rounded-md text-xs font-semibold ${
            (product.stock || product.stock_quantity || product.current_stock || 0) > 10 ? 'bg-green-100 text-green-800' :
            (product.stock || product.stock_quantity || product.current_stock || 0) > 0 ? 'bg-yellow-100 text-yellow-800' :
            'bg-red-100 text-red-800'
          }`}>
            {(product.stock || product.stock_quantity || product.current_stock || 0) > 0 
              ? `${(product.stock || product.stock_quantity || product.current_stock)} in stock` 
              : 'Out of stock'}
          </div>
        )}

        {/* Quick Actions (show on hover) */}
        <div className={`absolute inset-0 bg-black/20 flex items-center justify-center transition-opacity duration-300 ${
          isHovered ? 'opacity-100' : 'opacity-0'
        }`}>
          <div className="flex space-x-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onViewProduct(product);
              }}
              className="bg-white/90 backdrop-blur-sm p-2 rounded-full hover:bg-white transition-colors"
            >
              <Eye className="w-5 h-5 text-gray-700" />
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsWishlisted(!isWishlisted);
              }}
              className={`backdrop-blur-sm p-2 rounded-full transition-colors ${
                isWishlisted ? 'bg-red-500 text-white' : 'bg-white/90 text-gray-700 hover:bg-white'
              }`}
            >
              <Heart className={`w-5 h-5 ${isWishlisted ? 'fill-current' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Product Info */}
      <div className="p-4">
        {/* Category Badge */}
        <div className="text-xs font-medium text-red-700 mb-1 uppercase tracking-wide">
          {product.category}
        </div>

        {/* Product Name */}
        <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2 leading-tight">
          {product.name}
        </h3>

        {/* Brand and Model */}
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm font-medium text-gray-700">
            {product.brand}
          </div>
          {product.modelNumber && (
            <div className="text-xs text-gray-600 bg-gray-100 px-2 py-1 rounded font-mono">
              {product.modelNumber}
            </div>
          )}
        </div>

        {/* Key Benefits */}
        {product?.keyFeatures && Array.isArray(product.keyFeatures) && product.keyFeatures.length > 0 && (
          <div className="mb-3 bg-blue-50 p-3 rounded-md border border-blue-100">
            <div className="text-xs font-semibold text-blue-900 mb-2">Key Benefits:</div>
            <ul className="space-y-1">
              {product.keyFeatures.slice(0, 3).map((feature, index) => (
                <li key={index} className="text-xs text-gray-700 flex items-start">
                  <span className="text-blue-600 mr-1 flex-shrink-0">•</span>
                  <span className="line-clamp-1">{feature}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Rating */}
        <div className="flex items-center mb-3">
          <div className="flex text-yellow-400">
            {[1, 2, 3, 4, 5].map((star) => (
              <Star key={star} className="w-4 h-4 fill-current" />
            ))}
          </div>
          <span className="text-sm text-gray-500 ml-2">(0)</span>
        </div>

        {/* Price */}
        <div className="mb-4">
          <div className="flex items-center space-x-2">
            <span className="text-xl font-bold text-gray-900">
              ₹{product?.price?.toLocaleString() || '0'}
            </span>
            {product?.originalPrice && product.originalPrice > product.price && (
              <span className="text-sm text-gray-500 line-through">
                ₹{product.originalPrice?.toLocaleString()}
              </span>
            )}
          </div>
        </div>

        <OfferTag productId={product?.id} />

        {/* Action Buttons */}
        <div className="space-y-2" data-testid="pc-actions-v2">
          <DeliveryEtaBadge weight={product?.weight || product?.weight_kg || 1} />
          {cartQuantity === 0 ? (
  <button
    onClick={(e) => {
      e.stopPropagation();
      onAddToCart(product);
    }}
    disabled={(product?.stock || product?.stock_quantity || product?.current_stock || 0) === 0}
    className="w-full bg-amber-700 text-white py-2.5 px-3 rounded-lg hover:bg-amber-800 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
  >
    <ShoppingCart className="w-4 h-4 flex-shrink-0" />
    <span className="text-sm font-medium truncate">
      {(product?.stock || product?.stock_quantity || product?.current_stock || 0) === 0 ? 'Out of Stock' : 'Add to Cart'}
    </span>
  </button>
) : (
  <div className="w-full flex items-center justify-between bg-amber-700 text-white rounded-lg py-2 px-3">
    <button
      onClick={(e) => {
        e.stopPropagation();
        updateQuantity(product.id, cartQuantity - 1);
      }}
      className="px-3 py-1 hover:bg-amber-800 rounded transition-colors"
    >
      −
    </button>
    <span className="text-sm font-medium">{cartQuantity}</span>
    <button
      onClick={(e) => {
        e.stopPropagation();
        updateQuantity(product.id, cartQuantity + 1);
      }}
      className="px-3 py-1 hover:bg-amber-800 rounded transition-colors"
    >
      +
    </button>
  </div>
)}
          
          {/* Quick Actions Row */}
          <div className="flex gap-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleProductClick();
              }}
              className="flex-1 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center gap-1"
              title="Quick View"
            >
              <Eye className="w-4 h-4" />
            </button>
            <button
              onClick={handleAIRecommendation}
              className="flex-1 py-2 bg-gradient-to-r from-amber-600 to-orange-500 text-white rounded-lg hover:from-amber-700 hover:to-orange-600 transition-colors flex items-center justify-center gap-1"
              title="AI Assistant"
            >
              <Bot className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Fast Moving Indicator */}
        {product.fastMoving && (
          <div className="mt-2 text-xs text-green-600 font-medium flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
            Fast Moving Item
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductCard;