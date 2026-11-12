import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { TrendingUp, Star } from 'lucide-react';
import ProductCard from './ProductCard';


const BestSellersSection = ({ onViewProduct, onAddToCart, onAISalesChat }) => {
  const [bestSellers, setBestSellers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBestSellers();
  }, []);

  const fetchBestSellers = async () => {
    try {
      // Fetch products and sort by a "best_seller" flag or by price/popularity
      const response = await fetch(`${BACKEND_URL}/api/products`);
      const data = await response.json();
      
      if (data.status === 'success' && data.products) {
        // Get all active products from all brands with valid prices
        const activeProducts = data.products.filter(p => p.is_active !== false && p.price > 0);
        
        // First try to get explicitly marked best sellers
        let sellers = activeProducts.filter(p => p.is_best_seller || p.featured);
        
        // If not enough, add high-rated products
        if (sellers.length < 8) {
          const highRated = activeProducts
            .filter(p => (p.rating >= 4) && !sellers.find(s => s.id === p.id));
          sellers = [...sellers, ...highRated];
        }
        
        // If still not enough, add recently added or discounted products from ALL brands
        if (sellers.length < 8) {
          const others = activeProducts
            .filter(p => !sellers.find(s => s.id === p.id))
            .sort((a, b) => {
              // Prioritize discounted items
              const aDiscount = a.original_price ? (a.original_price - a.price) / a.original_price : 0;
              const bDiscount = b.original_price ? (b.original_price - b.price) / b.original_price : 0;
              return bDiscount - aDiscount;
            });
          sellers = [...sellers, ...others];
        }
        
        // Ensure diversity of brands in the selection
        const selectedIds = new Set();
        const diverseSellers = [];
        const brandCounts = {};
        
        // First pass: include at least 1 product from each brand
        const brands = [...new Set(sellers.map(p => p.brand))];
        for (const brand of brands) {
          const brandProduct = sellers.find(p => p.brand === brand);
          if (brandProduct && diverseSellers.length < 8) {
            diverseSellers.push(brandProduct);
            selectedIds.add(brandProduct.id);
            brandCounts[brand] = 1;
          }
        }
        
        // Second pass: fill remaining slots with diversity limit
        for (const product of sellers) {
          const brand = product.brand || 'Unknown';
          brandCounts[brand] = brandCounts[brand] || 0;
          
          // Limit to max 3 products per brand to ensure diversity
          if (!selectedIds.has(product.id) && brandCounts[brand] < 3 && diverseSellers.length < 8) {
            diverseSellers.push(product);
            selectedIds.add(product.id);
            brandCounts[brand]++;
          }
        }
        
        // If still need more, add remaining products
        if (diverseSellers.length < 8) {
          for (const product of sellers) {
            if (!selectedIds.has(product.id) && diverseSellers.length < 8) {
              diverseSellers.push(product);
            }
          }
        }
        
        setBestSellers(diverseSellers.slice(0, 8));
      }
    } catch (error) {
      console.error('Error fetching best sellers:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="py-16 bg-gradient-to-b from-white to-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-64 mb-8"></div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-96 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (bestSellers.length === 0) return null;

  return (
    <section className="py-16 bg-gradient-to-b from-white to-gray-50">
      <div className="max-w-7xl mx-auto px-4">
        {/* Section Header */}
        <div className="flex items-center justify-between mb-12">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-gradient-to-r from-orange-500 to-red-600 rounded-full">
              <TrendingUp className="h-8 w-8 text-white" />
            </div>
            <div>
              <h2 className="text-4xl font-bold text-gray-900">Best Sellers</h2>
              <p className="text-gray-600 mt-1">Top-rated products loved by customers</p>
            </div>
          </div>
          <div className="hidden md:flex items-center space-x-2 text-amber-600">
            <Star className="h-5 w-5 fill-current" />
            <span className="font-semibold">Customer Favorites</span>
          </div>
        </div>

        {/* Products Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {bestSellers.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onViewProduct={onViewProduct}
              onAddToCart={onAddToCart}
              onAISalesChat={onAISalesChat}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default BestSellersSection;
