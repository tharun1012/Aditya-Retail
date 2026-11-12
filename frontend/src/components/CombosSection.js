import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { Package, Percent, ShoppingCart, Eye } from 'lucide-react';


const CombosSection = ({ onViewProduct, onAddToCart }) => {
  const [combos, setCombos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCombos();
  }, []);

  const fetchCombos = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/combo-offers/?active_only=true`, { cache: 'no-store' });
      const data = await response.json();
      
      if (data.status === 'success' && data.combos) {
        // Filter to only show active combos
        const activeCombos = data.combos.filter(c => c.is_active !== false);
        setCombos(activeCombos.slice(0, 6)); // Top 6 active combos
      }
    } catch (error) {
      console.error('Error fetching combos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDeal = (combo, e) => {
    e.stopPropagation();
    window.location.href = `/combos/${combo.id}`;
  };

  const handleAddComboToCart = (combo, e) => {
    e.stopPropagation();
    try {
      const items = combo.products || [];
      if (!items.length) return;
      const existingCart = JSON.parse(localStorage.getItem('shopping_cart') || '[]');
      const base = items.reduce((t, x) => t + (x.price || 0), 0) || 1;
      const target = Math.round(combo.combo_price || base);
      let allocated = 0;
      const updatedCart = existingCart.filter(i => i.combo_id !== combo.id);
      items.forEach((product, idx) => {
        const share = idx === items.length - 1
          ? target - allocated
          : Math.round(target * (product.price || 0) / base);
        allocated += share;
        updatedCart.push({ product: { ...product, price: share, combo_id: combo.id, combo_name: combo.name, regular_price: product.price }, quantity: 1, combo_id: combo.id });
      });
      localStorage.setItem('shopping_cart', JSON.stringify(updatedCart));
      window.dispatchEvent(new CustomEvent('cartUpdated'));
    } catch (err) {
      console.error('Error adding combo to cart:', err);
    }
  };

  if (loading) {
    return (
      <div className="py-12 md:py-16 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-64 mb-8"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-80 bg-gray-200 rounded-2xl"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (combos.length === 0) return null;

  return (
    <section className="py-12 md:py-16 bg-gradient-to-b from-gray-50 to-white" data-testid="combos-section">
      <div className="max-w-7xl mx-auto px-4">
        {/* Section Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 md:mb-12 gap-4">
          <div className="flex items-center gap-3 md:gap-4">
            <div className="p-2.5 md:p-3 bg-gradient-to-r from-purple-500 to-indigo-600 rounded-xl md:rounded-2xl shadow-lg">
              <Package className="h-6 w-6 md:h-8 md:w-8 text-white" />
            </div>
            <div>
              <h2 className="text-2xl md:text-4xl font-bold text-gray-900">Combo Offers</h2>
              <p className="text-sm md:text-base text-gray-600 mt-0.5 md:mt-1">Save more with bundled deals</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-green-600 bg-green-50 px-3 py-1.5 rounded-full self-start sm:self-auto">
            <Percent className="h-4 w-4 md:h-5 md:w-5" />
            <span className="text-sm md:text-base font-semibold">Extra Savings</span>
          </div>
        </div>

        {/* Combos Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
          {combos.map((combo) => (
            <div
              key={combo.id}
              className="bg-white border border-gray-200 rounded-2xl overflow-hidden hover:shadow-xl transition-all duration-300 group"
              data-testid={`combo-card-${combo.id}`}
            >
              {/* Product Images Grid */}
              <div className="relative bg-gradient-to-br from-purple-50 to-indigo-50 p-4">
                <div className="flex gap-2 justify-center items-center min-h-[120px] md:min-h-[140px]">
                  {combo.products && combo.products.slice(0, 3).map((product, idx) => (
                    <div 
                      key={idx} 
                      className={`${combo.products.length === 1 ? 'w-32 h-32' : combo.products.length === 2 ? 'w-24 h-24' : 'w-20 h-20'} md:${combo.products.length === 1 ? 'w-36 h-36' : combo.products.length === 2 ? 'w-28 h-28' : 'w-24 h-24'} bg-white rounded-xl shadow-sm overflow-hidden flex-shrink-0`}
                    >
                      <img 
                        src={product.images?.[0] || product.image || product.thumbnail || 'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=200&q=80'}
                        alt={product.name}
                        className="w-full h-full object-contain p-1"
                        onError={(e) => {
                          e.target.src = 'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=200&q=80';
                        }}
                      />
                    </div>
                  ))}
                  {combo.products && combo.products.length > 3 && (
                    <div className="w-16 h-16 md:w-20 md:h-20 bg-white/80 rounded-xl flex items-center justify-center text-purple-600 font-bold text-sm">
                      +{combo.products.length - 3} more
                    </div>
                  )}
                </div>
                
                {/* Badges */}
                <div className="absolute top-3 left-3 flex flex-col gap-1.5">
                  <span className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-2.5 py-1 rounded-full text-xs font-bold shadow-md">
                    COMBO DEAL
                  </span>
                </div>
                {combo.discount_percentage && (
                  <div className="absolute top-3 right-3">
                    <span className="bg-green-500 text-white px-2.5 py-1 rounded-full text-xs font-bold shadow-md">
                      {combo.discount_percentage}% OFF
                    </span>
                  </div>
                )}
              </div>

              {/* Combo Details */}
              <div className="p-4 md:p-5">
                {/* Combo Title */}
                <h3 className="text-lg md:text-xl font-bold text-gray-900 mb-2 group-hover:text-purple-700 transition-colors line-clamp-1">
                  {combo.name}
                </h3>

                {/* Products List */}
                <div className="space-y-1.5 mb-4 max-h-[80px] overflow-y-auto">
                  {combo.products && combo.products.map((product, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-xs md:text-sm text-gray-600">
                      <div className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-1.5 flex-shrink-0"></div>
                      <span className="line-clamp-1">{product.name}</span>
                    </div>
                  ))}
                </div>

                {/* Pricing */}
                <div className="border-t border-gray-100 pt-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <p className="text-xs text-gray-500 mb-0.5">Combo Price</p>
                      <div className="flex items-baseline gap-2">
                        <p className="text-xl md:text-2xl font-bold text-purple-700">
                          ₹{Math.round(combo.combo_price || 0).toLocaleString()}
                        </p>
                        {combo.total_price && (
                          <p className="text-sm text-gray-400 line-through">
                            ₹{Math.round(combo.total_price).toLocaleString()}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {combo.savings && (
                    <p className="text-sm text-green-600 font-semibold mb-3 flex items-center gap-1">
                      <span className="text-base">💰</span> 
                      Save ₹{Math.round(combo.savings).toLocaleString()}
                    </p>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <button
                      className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-4 py-2.5 rounded-xl font-semibold text-sm hover:from-purple-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg"
                      onClick={(e) => handleViewDeal(combo, e)}
                      data-testid={`view-deal-btn-${combo.id}`}
                    >
                      <Eye className="w-4 h-4" />
                      View Deal
                    </button>
                    <button
                      className="flex items-center justify-center gap-2 bg-orange-500 text-white px-4 py-2.5 rounded-xl font-semibold text-sm hover:bg-orange-600 transition-all shadow-md hover:shadow-lg"
                      onClick={(e) => handleAddComboToCart(combo, e)}
                      data-testid={`add-combo-btn-${combo.id}`}
                    >
                      <ShoppingCart className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default CombosSection;
