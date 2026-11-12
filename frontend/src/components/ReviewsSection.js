import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { Star, ThumbsUp, UserCircle } from 'lucide-react';


const ReviewsSection = ({ productId }) => {
  const [reviews, setReviews] = useState([]);
  const [stats, setStats] = useState({ total_reviews: 0, average_rating: 0, rating_distribution: {} });
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('recent');
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [formData, setFormData] = useState({
    user_name: '',
    user_email: '',
    rating: 5,
    review_title: '',
    review_text: ''
  });
  const [submitLoading, setSubmitLoading] = useState(false);

  useEffect(() => {
    fetchReviews();
  }, [productId, sortBy]);

  const fetchReviews = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/reviews/product/${productId}?sort_by=${sortBy}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setReviews(data.reviews || []);
        setStats({
          total_reviews: data.total_reviews || 0,
          average_rating: data.average_rating || 0,
          rating_distribution: data.rating_distribution || {}
        });
      }
    } catch (error) {
      console.error('Error fetching reviews:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    
    try {
      setSubmitLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/reviews/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          product_id: productId,
          verified_purchase: false
        })
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        alert('✅ Review submitted successfully! It will be visible after approval.');
        setShowReviewForm(false);
        setFormData({
          user_name: '',
          user_email: '',
          rating: 5,
          review_title: '',
          review_text: ''
        });
      } else {
        alert(`❌ ${data.detail || 'Failed to submit review'}`);
      }
    } catch (error) {
      console.error('Error submitting review:', error);
      alert('❌ Failed to submit review');
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleMarkHelpful = async (reviewId) => {
    try {
      await fetch(`${BACKEND_URL}/api/reviews/${reviewId}/helpful`, {
        method: 'PUT'
      });
      fetchReviews(); // Refresh reviews
    } catch (error) {
      console.error('Error marking review helpful:', error);
    }
  };

  const renderStars = (rating, size = 'small') => {
    const sizeClass = size === 'large' ? 'w-6 h-6' : 'w-4 h-4';
    return (
      <div className="flex">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`${sizeClass} ${star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}
          />
        ))}
      </div>
    );
  };

  const renderRatingDistribution = () => {
    const total = stats.total_reviews;
    if (total === 0) return null;

    return (
      <div className="space-y-2">
        {[5, 4, 3, 2, 1].map((rating) => {
          const count = stats.rating_distribution[rating] || 0;
          const percentage = (count / total) * 100;
          
          return (
            <div key={rating} className="flex items-center gap-2">
              <span className="text-sm w-12">{rating} star</span>
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-yellow-400 h-2 rounded-full"
                  style={{ width: `${percentage}%` }}
                />
              </div>
              <span className="text-sm text-gray-600 w-12 text-right">{count}</span>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg p-6 mt-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Customer Reviews</h2>

      {/* Rating Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 pb-8 border-b">
        <div className="text-center">
          <div className="text-5xl font-bold text-gray-900 mb-2">{stats.average_rating.toFixed(1)}</div>
          {renderStars(Math.round(stats.average_rating), 'large')}
          <div className="text-sm text-gray-600 mt-2">{stats.total_reviews} reviews</div>
        </div>
        
        <div>
          {renderRatingDistribution()}
        </div>
      </div>

      {/* Sort and Write Review */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <label className="text-sm text-gray-600 mr-2">Sort by:</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="border rounded px-3 py-1"
          >
            <option value="recent">Most Recent</option>
            <option value="helpful">Most Helpful</option>
            <option value="rating">Highest Rating</option>
          </select>
        </div>
        
        <button
          onClick={() => setShowReviewForm(!showReviewForm)}
          className="bg-red-700 text-white px-6 py-2 rounded-lg hover:bg-red-800"
        >
          Write a Review
        </button>
      </div>

      {/* Write Review Form */}
      {showReviewForm && (
        <div className="bg-gray-50 p-6 rounded-lg mb-6">
          <h3 className="text-lg font-semibold mb-4">Write Your Review</h3>
          <form onSubmit={handleSubmitReview}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <input
                type="text"
                placeholder="Your Name"
                value={formData.user_name}
                onChange={(e) => setFormData({...formData, user_name: e.target.value})}
                className="border rounded px-3 py-2"
                required
              />
              <input
                type="email"
                placeholder="Your Email"
                value={formData.user_email}
                onChange={(e) => setFormData({...formData, user_email: e.target.value})}
                className="border rounded px-3 py-2"
                required
              />
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Rating</label>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((rating) => (
                  <button
                    key={rating}
                    type="button"
                    onClick={() => setFormData({...formData, rating})}
                    className="focus:outline-none"
                  >
                    <Star
                      className={`w-8 h-8 ${rating <= formData.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}
                    />
                  </button>
                ))}
              </div>
            </div>
            
            <input
              type="text"
              placeholder="Review Title"
              value={formData.review_title}
              onChange={(e) => setFormData({...formData, review_title: e.target.value})}
              className="w-full border rounded px-3 py-2 mb-4"
              required
            />
            
            <textarea
              placeholder="Write your review..."
              value={formData.review_text}
              onChange={(e) => setFormData({...formData, review_text: e.target.value})}
              className="w-full border rounded px-3 py-2 mb-4"
              rows="4"
              required
            />
            
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={submitLoading}
                className="bg-red-700 text-white px-6 py-2 rounded-lg hover:bg-red-800 disabled:opacity-50"
              >
                {submitLoading ? 'Submitting...' : 'Submit Review'}
              </button>
              <button
                type="button"
                onClick={() => setShowReviewForm(false)}
                className="border border-gray-300 px-6 py-2 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Reviews List */}
      {loading ? (
        <div className="text-center py-8">Loading reviews...</div>
      ) : reviews.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No reviews yet. Be the first to review this product!
        </div>
      ) : (
        <div className="space-y-6">
          {reviews.map((review) => (
            <div key={review.id} className="border-b pb-6 last:border-b-0">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-3">
                  <UserCircle className="w-10 h-10 text-gray-400" />
                  <div>
                    <div className="font-semibold">{review.user_name}</div>
                    <div className="text-sm text-gray-500">
                      {new Date(review.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
                {renderStars(review.rating)}
              </div>
              
              <h4 className="font-semibold mb-2">{review.review_title}</h4>
              <p className="text-gray-700 mb-3">{review.review_text}</p>
              
              {review.verified_purchase && (
                <span className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded mb-3">
                  ✓ Verified Purchase
                </span>
              )}
              
              <button
                onClick={() => handleMarkHelpful(review.id)}
                className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
              >
                <ThumbsUp className="w-4 h-4" />
                Helpful ({review.helpful_count})
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ReviewsSection;
