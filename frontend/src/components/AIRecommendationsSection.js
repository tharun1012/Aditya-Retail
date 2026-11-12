import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { Sparkles, Brain, TrendingUp } from 'lucide-react';
import ProductCard from './ProductCard';


const AIRecommendationsSection = ({ onViewProduct, onAddToCart, onAISalesChat, userActivity }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reason, setReason] = useState('');

  useEffect(() => {
    fetchAIRecommendations();
  }, [userActivity]);

  const fetchAIRecommendations = async () => {
    try {
      // Get browsing history from localStorage
      const viewedProducts = JSON.parse(localStorage.getItem('viewedProducts') || '[]');
      const searchHistory = JSON.parse(localStorage.getItem('searchHistory') || '[]');
      const categoryViews = JSON.parse(localStorage.getItem('categoryViews') || '{}');
      
      // Call AI recommendation endpoint
      const response = await fetch(`${BACKEND_URL}/api/ai-recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          viewed_products: viewedProducts.slice(-10), // Last 10 viewed
          search_history: searchHistory.slice(-5), // Last 5 searches
          category_views: categoryViews,
          user_session: sessionStorage.getItem('sessionId') || `session_${Date.now()}`
        })
      });

      const data = await response.json();
      
      if (data.status === 'success' && data.recommendations) {
        setRecommendations(data.recommendations.slice(0, 8));
        setReason(data.reason || 'Based on your browsing history');
      } else {
        // Fallback: Show popular products
        await fetchFallbackRecommendations();
      }
    } catch (error) {
      console.error('Error fetching AI recommendations:', error);
      await fetchFallbackRecommendations();
    } finally {
      setLoading(false);
    }
  };

  const fetchFallbackRecommendations = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/products`);
      const data = await response.json();
      
      if (data.status === 'success' && data.products) {
        // Get all active products
        const activeProducts = data.products.filter(p => p.is_active !== false);
        
        // Sort by featured, rating, and newness
        const sorted = activeProducts.sort((a, b) => {
          const aScore = (a.featured ? 10 : 0) + (a.rating || 0) * 2 + (a.is_new ? 5 : 0);
          const bScore = (b.featured ? 10 : 0) + (b.rating || 0) * 2 + (b.is_new ? 5 : 0);
          return bScore - aScore;
        });
        
        // Ensure brand diversity - include products from all brands
        const diverseRecommendations = [];
        const brandCounts = {};
        
        for (const product of sorted) {
          const brand = product.brand || 'Unknown';
          brandCounts[brand] = (brandCounts[brand] || 0);
          
          // Max 2 products per brand initially to ensure diversity
          if (brandCounts[brand] < 2 && diverseRecommendations.length < 8) {
            diverseRecommendations.push(product);
            brandCounts[brand]++;
          }
        }
        
        // Fill remaining slots if needed
        if (diverseRecommendations.length < 8) {
          for (const product of sorted) {
            if (!diverseRecommendations.find(p => p.id === product.id) && diverseRecommendations.length < 8) {
              diverseRecommendations.push(product);
            }
          }
        }
        
        setRecommendations(diverseRecommendations);
        setReason('Popular products from all brands');
      }
    } catch (error) {
      console.error('Fallback recommendations error:', error);
    }
  };

  if (loading) {
    return (
      <div className="py-16 bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
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

  if (recommendations.length === 0) return null;

  return (
    <section className="py-16 bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 border-t border-b border-purple-100">
      <div className="max-w-7xl mx-auto px-4">
        {/* Section Header */}
        <div className="flex items-center justify-between mb-12">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full animate-pulse">
              <Brain className="h-8 w-8 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-4xl font-bold text-gray-900">Recommended for You</h2>
                <Sparkles className="h-6 w-6 text-purple-600" />
              </div>
              <p className="text-gray-600 mt-1 flex items-center space-x-2">
                <span className="inline-flex items-center px-3 py-1 bg-white rounded-full text-sm font-medium text-purple-700 border border-purple-200">
                  <Sparkles className="h-3 w-3 mr-1" />
                  AI Powered
                </span>
                <span className="text-sm">{reason}</span>
              </p>
            </div>
          </div>
          <div className="hidden md:flex items-center space-x-2 text-purple-600">
            <TrendingUp className="h-5 w-5" />
            <span className="font-semibold">Personalized Just for You</span>
          </div>
        </div>

        {/* Info Banner */}
        <div className="mb-8 bg-gradient-to-r from-purple-100 to-pink-100 border border-purple-200 rounded-xl p-4">
          <div className="flex items-center space-x-3">
            <Brain className="h-5 w-5 text-purple-700" />
            <p className="text-sm text-purple-900">
              <strong>Smart Recommendations:</strong> Our AI analyzes your browsing patterns, 
              search history, and preferences to suggest products perfect for your needs.
            </p>
          </div>
        </div>

        {/* Products Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {recommendations.map((product, index) => (
            <div key={product.id} className="relative group">
              {/* AI Badge */}
              {index < 3 && (
                <div className="absolute -top-2 -right-2 z-10">
                  <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg flex items-center space-x-1">
                    <Sparkles className="h-3 w-3" />
                    <span>Top Pick</span>
                  </div>
                </div>
              )}
              <ProductCard
                product={product}
                onViewProduct={onViewProduct}
                onAddToCart={onAddToCart}
                onAISalesChat={onAISalesChat}
              />
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="mt-12 text-center">
          <p className="text-gray-600 text-sm mb-4">
            Not what you're looking for? Chat with our AI assistant for personalized help!
          </p>
          <button
            onClick={() => {
              // Dispatch event to open AI chat with sales agent
              window.dispatchEvent(new CustomEvent('openAIChatWithAgent', { detail: { agentType: 'sales' } }));
            }}
            className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition-all shadow-lg hover:shadow-xl"
          >
            <Sparkles className="h-5 w-5 mr-2" />
            Get AI Shopping Assistance
          </button>
        </div>
      </div>
    </section>
  );
};

export default AIRecommendationsSection;
