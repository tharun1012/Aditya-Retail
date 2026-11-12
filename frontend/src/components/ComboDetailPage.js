import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { useCart } from '../hooks/useCart';
import Header from './Header';
import Footer from './Footer';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Package, ArrowLeft, ShoppingCart, Tag, Clock, CheckCircle, 
  Star, Truck, Shield, Gift, Percent, Calendar, ChevronRight,
  Heart, Share2, Info
} from 'lucide-react';


const ComboDetailInner = () => {
  const { comboId } = useParams();
  const navigate = useNavigate();
  const [combo, setCombo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState(0);
  const [addedToCart, setAddedToCart] = useState(false);

  useEffect(() => {
    const fetchCombo = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/combo-offers/detail/${comboId}`, { cache: 'no-store' });
        const data = await response.json();
        if (data.status === 'success') {
          setCombo(data.combo);
        }
      } catch (error) {
        console.error('Error fetching combo:', error);
      } finally {
        setLoading(false);
      }
    };

    if (comboId) {
      fetchCombo();
    }
  }, [comboId]);

  const handleAddToCart = async () => {
    if (combo) {
      try {
        // Get existing cart from localStorage
        const existingCart = JSON.parse(localStorage.getItem('shopping_cart') || '[]');
        
        // Add combo products at the combo price (split proportionally)
        const items = combo.products || [];
        const base = items.reduce((t, x) => t + (x.price || 0), 0) || 1;
        const target = Math.round(combo.final_price || base);
        let allocated = 0;
        const updatedCart = existingCart.filter(i => i.combo_id !== combo.id);
        items.forEach((product, idx) => {
          const share = idx === items.length - 1
            ? target - allocated
            : Math.round(target * (product.price || 0) / base);
          allocated += share;
          updatedCart.push({ product: { ...product, price: share, combo_id: combo.id, combo_name: combo.name, regular_price: product.price }, quantity: 1, combo_id: combo.id });
        });

        // Save to localStorage
        localStorage.setItem('shopping_cart', JSON.stringify(updatedCart));
        
        setAddedToCart(true);
        setTimeout(() => setAddedToCart(false), 3000);
        
        // Dispatch custom event to notify cart updates
        window.dispatchEvent(new CustomEvent('cartUpdated'));
      } catch (error) {
        console.error('Error adding to cart:', error);
      }
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(price || 0);
  };

  const getDaysRemaining = () => {
    if (!combo?.valid_until) return null;
    const end = new Date(combo.valid_until);
    const now = new Date();
    const diff = Math.ceil((end - now) / (1000 * 60 * 60 * 24));
    return diff > 0 ? diff : 0;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading combo details...</p>
        </div>
      </div>
    );
  }

  if (!combo) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Gift className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-700 mb-2">Combo Not Found</h2>
          <p className="text-gray-500 mb-6">This combo offer may have expired or doesn't exist.</p>
          <button
            onClick={() => navigate('/')}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  const allImages = combo.products?.flatMap(p => p.images || []).filter(Boolean) || [];
  const daysRemaining = getDaysRemaining();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Combo Badge */}
        <div className="mb-6">
          <span className="inline-flex items-center gap-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
            <Gift className="w-4 h-4" />
            Special Combo Offer
            {combo.ai_generated && (
              <span className="bg-white/20 px-2 py-0.5 rounded text-xs">AI Curated</span>
            )}
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left - Images */}
          <div className="space-y-4">
            {/* Main Image */}
            <div className="bg-white rounded-2xl p-4 shadow-lg">
              <div className="aspect-square bg-gray-100 rounded-xl overflow-hidden flex items-center justify-center">
                {allImages[selectedImage] ? (
                  <img 
                    src={allImages[selectedImage]} 
                    alt={combo.name}
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <div className="text-center p-8">
                    <Package className="w-24 h-24 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-400">Bundle of {combo.products?.length || 0} products</p>
                  </div>
                )}
              </div>
              
              {/* Discount Badge */}
              <div className="absolute top-6 right-6 bg-red-500 text-white px-4 py-2 rounded-lg font-bold shadow-lg">
                {combo.discount_type === 'percentage' 
                  ? `${combo.discount_value}% OFF` 
                  : `${formatPrice(combo.discount_value)} OFF`}
              </div>
            </div>

            {/* Thumbnail Images */}
            {allImages.length > 1 && (
              <div className="flex gap-3 overflow-x-auto pb-2">
                {allImages.map((img, index) => (
                  <button
                    key={index}
                    onClick={() => setSelectedImage(index)}
                    className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-all ${
                      selectedImage === index ? 'border-purple-600 shadow-lg' : 'border-gray-200'
                    }`}
                  >
                    <img src={img} alt="" className="w-full h-full object-cover" />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Right - Details */}
          <div className="space-y-6">
            {/* Title & Description */}
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-3">{combo.name}</h1>
              <p className="text-gray-600 text-lg">{combo.description}</p>
            </div>

            {/* Pricing */}
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl p-6 border border-purple-100">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Original Price</p>
                  <p className="text-xl text-gray-400 line-through">{formatPrice(combo.original_price)}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500 mb-1">Combo Price</p>
                  <p className="text-3xl font-bold text-purple-600">{formatPrice(combo.final_price)}</p>
                </div>
              </div>
              
              <div className="flex items-center justify-between pt-4 border-t border-purple-200">
                <div className="flex items-center gap-2 text-green-600">
                  <Tag className="w-5 h-5" />
                  <span className="font-semibold">You Save</span>
                </div>
                <span className="text-2xl font-bold text-green-600">{formatPrice(combo.savings)}</span>
              </div>
            </div>

            {/* Validity */}
            {daysRemaining !== null && (
              <div className={`flex items-center gap-3 p-4 rounded-xl ${
                daysRemaining <= 3 ? 'bg-red-50 text-red-700' : 'bg-amber-50 text-amber-700'
              }`}>
                <Clock className="w-5 h-5" />
                <div>
                  <p className="font-semibold">
                    {daysRemaining === 0 ? 'Expires Today!' : `${daysRemaining} days remaining`}
                  </p>
                  <p className="text-sm opacity-75">
                    Valid till {new Date(combo.valid_until).toLocaleDateString('en-IN', { 
                      day: 'numeric', month: 'long', year: 'numeric' 
                    })}
                  </p>
                </div>
              </div>
            )}

            {/* Add to Cart Button */}
            <button
              onClick={handleAddToCart}
              disabled={addedToCart}
              className={`w-full py-4 rounded-xl font-semibold text-lg transition-all flex items-center justify-center gap-3 ${
                addedToCart 
                  ? 'bg-green-600 text-white' 
                  : 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700 shadow-lg hover:shadow-xl'
              }`}
            >
              {addedToCart ? (
                <>
                  <CheckCircle className="w-6 h-6" />
                  Added to Cart!
                </>
              ) : (
                <>
                  <ShoppingCart className="w-6 h-6" />
                  Add Combo to Cart - {formatPrice(combo.final_price)}
                </>
              )}
            </button>

            {/* Features */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-3 p-3 bg-white rounded-xl border border-gray-100">
                <Truck className="w-5 h-5 text-blue-600" />
                <span className="text-sm text-gray-600">Free Delivery</span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-white rounded-xl border border-gray-100">
                <Shield className="w-5 h-5 text-green-600" />
                <span className="text-sm text-gray-600">Brand Warranty</span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-white rounded-xl border border-gray-100">
                <Star className="w-5 h-5 text-amber-500" />
                <span className="text-sm text-gray-600">Premium Quality</span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-white rounded-xl border border-gray-100">
                <Gift className="w-5 h-5 text-purple-600" />
                <span className="text-sm text-gray-600">Bundle Savings</span>
              </div>
            </div>
          </div>
        </div>

        {/* Products in Combo */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Package className="w-7 h-7 text-purple-600" />
            Products in this Combo ({combo.products?.length || 0})
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {combo.products?.map((product, index) => {
              // Generate SEO-friendly product URL
              const categorySlug = product.category 
                ? product.category.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
                : 'product';
              const productSlug = product.slug || product.name?.toLowerCase()
                .replace(/[^a-z0-9\s-]/g, '')
                .replace(/\s+/g, '-')
                .replace(/-+/g, '-');
              const productUrl = productSlug 
                ? `/product/${categorySlug}/${productSlug}`
                : `/product/${product.id}`;
              
              return (
              <div 
                key={product.id || index}
                className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => navigate(productUrl)}
              >
                <div className="aspect-video bg-gray-100 relative">
                  {product.images?.[0] ? (
                    <img 
                      src={product.images[0]} 
                      alt={product.name}
                      className="w-full h-full object-contain p-4"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <Package className="w-12 h-12 text-gray-300" />
                    </div>
                  )}
                  <span className="absolute top-3 left-3 bg-purple-600 text-white text-xs px-2 py-1 rounded">
                    #{index + 1}
                  </span>
                </div>
                
                <div className="p-4">
                  <p className="text-xs text-purple-600 font-semibold mb-1">{product.brand}</p>
                  <h3 className="font-semibold text-gray-900 line-clamp-2 mb-2">{product.name}</h3>
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-bold text-gray-900">{formatPrice(product.price)}</span>
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  </div>
                </div>
              </div>
              );
            })}
          </div>
        </div>

        {/* Why Buy This Combo */}
        <div className="mt-12 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl p-8 text-white">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Info className="w-7 h-7" />
            Why Buy This Combo?
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white/10 rounded-xl p-5">
              <Percent className="w-10 h-10 mb-3 text-yellow-300" />
              <h3 className="font-semibold text-lg mb-2">Maximum Savings</h3>
              <p className="text-white/80 text-sm">
                Save {formatPrice(combo.savings)} compared to buying products individually
              </p>
            </div>
            <div className="bg-white/10 rounded-xl p-5">
              <CheckCircle className="w-10 h-10 mb-3 text-green-300" />
              <h3 className="font-semibold text-lg mb-2">Perfectly Matched</h3>
              <p className="text-white/80 text-sm">
                Products selected to work together seamlessly for your kitchen
              </p>
            </div>
            <div className="bg-white/10 rounded-xl p-5">
              <Truck className="w-10 h-10 mb-3 text-blue-300" />
              <h3 className="font-semibold text-lg mb-2">Single Delivery</h3>
              <p className="text-white/80 text-sm">
                All products delivered together with professional installation support
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const ComboDetailPage = () => {
  const { cartCount, cartTotal } = useCart();
  return (
    <>
      <Header cartCount={cartCount} cartTotal={cartTotal} />
      <ComboDetailInner />
      <Footer />
    </>
  );
};

export default ComboDetailPage;
