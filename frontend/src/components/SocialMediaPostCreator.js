import React, { useState, useEffect, useRef } from 'react';
import { BACKEND_URL } from '../config/api';
import { MessageSquare, Plus, Facebook, Instagram, Linkedin, Twitter, Sparkles, Copy, Check, Trash2, Clock, Download, Image as ImageIcon } from 'lucide-react';
import { toPng, toJpeg } from 'html-to-image';


const SocialMediaPostCreator = () => {
  const [posts, setPosts] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const [showDesignModal, setShowDesignModal] = useState(false);
  const [currentDesign, setCurrentDesign] = useState(null);
  const [generatingImage, setGeneratingImage] = useState(false);
  const designRef = useRef(null);
  const [formData, setFormData] = useState({
    post_type: 'product',
    platform: 'facebook',
    content_type: 'new_product',
    product_ids: [],
    offer_details: '',
    custom_message: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch posts
      const postsRes = await fetch(`${BACKEND_URL}/api/social-media/posts`);
      const postsData = await postsRes.json();
      setPosts(postsData.posts || []);

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

  const handleGeneratePost = async () => {
    try {
      setGenerating(true);
      
      const response = await fetch(`${BACKEND_URL}/api/social-media/generate-post`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        alert('✅ Social media post generated successfully!');
        setShowModal(false);
        setFormData({
          post_type: 'product',
          platform: 'facebook',
          content_type: 'new_product',
          product_ids: [],
          offer_details: '',
          custom_message: ''
        });
        fetchData();
      }
    } catch (error) {
      console.error('Error generating post:', error);
      alert('Failed to generate post');
    } finally {
      setGenerating(false);
    }
  };

  const handleDeletePost = async (postId) => {
    if (!window.confirm('Are you sure you want to delete this post?')) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/social-media/${postId}`, {
        method: 'DELETE'
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        alert('Post deleted!');
        fetchData();
      }
    } catch (error) {
      console.error('Error deleting post:', error);
    }
  };

  const handleCopyToClipboard = (text, postId) => {
    navigator.clipboard.writeText(text);
    setCopiedId(postId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleGenerateVisualDesign = async (post) => {
    try {
      setGeneratingImage(true);
      
      // Get first product details if available
      let productData = {
        product_name: post.products?.[0]?.name || "Featured Product",
        product_price: post.products?.[0]?.price || null,
        product_mrp: post.products?.[0]?.originalPrice || post.products?.[0]?.original_price || null,
        product_image_url: post.products?.[0]?.images?.[0] || post.products?.[0]?.image || "https://via.placeholder.com/400",
        post_text: post.caption || "",
        platform: post.platform || "instagram",
        template_style: "professional",
        offer_text: post.offer_details || null,
        brand_name: "Aditya Retail",
        product_id: post.products?.[0]?.id || null
      };
      
      const response = await fetch(`${BACKEND_URL}/api/template-image-generation/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(productData)
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        // Update the post with generated image
        setPosts(prev => prev.map(p => 
          p.id === post.id 
            ? { ...p, generated_image: data.image_url }
            : p
        ));
        alert('✅ Visual design generated successfully! Scroll down to see it.');
      } else {
        throw new Error(data.detail || data.message || 'Generation failed');
      }
    } catch (error) {
      console.error('Error generating design:', error);
      alert('Failed to generate visual design: ' + error.message);
    } finally {
      setGeneratingImage(false);
    }
  };

  const handleDownloadDesign = async () => {
    if (!designRef.current) return;

    try {
      const dataUrl = await toPng(designRef.current, {
        quality: 0.95,
        pixelRatio: 2
      });
      
      const link = document.createElement('a');
      link.download = `social-post-${currentDesign.platform}-${Date.now()}.png`;
      link.href = dataUrl;
      link.click();
      
      alert('✅ Post design downloaded successfully!');
    } catch (error) {
      console.error('Error downloading design:', error);
      alert('Failed to download design');
    }
  };


  const handleGenerateAIImage = async (post) => {
    try {
      setGeneratingImage(true);
      
      const response = await fetch(`${BACKEND_URL}/api/ai-image-generation/generate-social-image`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          product_id: post.product_ids?.[0] || null,
          post_text: post.generated_content,
          platform: post.platform,
          style: "professional",
          include_product_image: true,
          offer_text: post.offer_details || null
        })
      });

      const data = await response.json();

      if (data.status === 'success') {
        // Update post with generated image
        setPosts(prev => prev.map(p => 
          p._id === post._id 
            ? { ...p, ai_generated_image: data.image_url }
            : p
        ));
        
        alert('✨ AI image generated successfully!');
      } else {
        const errorMsg = data.detail || data.message || 'Generation failed';
        throw new Error(errorMsg);
      }
    } catch (error) {
      console.error('Error generating AI image:', error);
      let errorMessage = 'Failed to generate AI image';
      
      if (error.message) {
        errorMessage += ': ' + error.message;
      } else if (typeof error === 'string') {
        errorMessage += ': ' + error;
      }
      
      alert(errorMessage);
    } finally {
      setGeneratingImage(false);
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

  const getPlatformIcon = (platform) => {
    const icons = {
      facebook: <Facebook className="w-5 h-5" />,
      instagram: <Instagram className="w-5 h-5" />,
      linkedin: <Linkedin className="w-5 h-5" />,
      twitter: <Twitter className="w-5 h-5" />
    };
    return icons[platform] || <MessageSquare className="w-5 h-5" />;
  };

  const getPlatformColor = (platform) => {
    const colors = {
      facebook: 'bg-blue-500',
      instagram: 'bg-pink-500',
      linkedin: 'bg-blue-700',
      twitter: 'bg-sky-500',
      all: 'bg-gray-500'
    };
    return colors[platform] || 'bg-gray-500';
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-700"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <MessageSquare className="w-8 h-8 text-amber-700" />
            Social Media Post Creator
          </h1>
          <p className="text-gray-600 mt-2">AI-powered social media content generation</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="bg-amber-700 text-white px-6 py-3 rounded-lg hover:bg-amber-800 transition-colors flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Generate New Post
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-gray-900">{posts.length}</div>
          <div className="text-sm text-gray-600">Total Posts</div>
        </div>
        <div className="bg-blue-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-blue-700">
            {posts.filter(p => p.status === 'draft').length}
          </div>
          <div className="text-sm text-blue-600">Draft</div>
        </div>
        <div className="bg-green-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-green-700">
            {posts.filter(p => p.status === 'posted').length}
          </div>
          <div className="text-sm text-green-600">Posted</div>
        </div>
        <div className="bg-purple-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-purple-700">
            {posts.reduce((sum, p) => sum + (p.engagement?.likes || 0), 0)}
          </div>
          <div className="text-sm text-purple-600">Total Likes</div>
        </div>
      </div>

      {/* Posts Grid */}
      {posts.length === 0 ? (
        <div className="bg-white rounded-lg shadow-lg p-12 text-center">
          <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Social Media Posts Yet</h3>
          <p className="text-gray-600 mb-6">
            Generate AI-powered social media content for Facebook, Instagram, LinkedIn, and Twitter
          </p>
          <button
            onClick={() => setShowModal(true)}
            className="bg-amber-700 text-white px-6 py-3 rounded-lg hover:bg-amber-800 transition-colors flex items-center gap-2 mx-auto"
          >
            <Plus className="w-5 h-5" />
            Generate First Post
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {posts.map((post) => (
          <div key={post.id} className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="p-6">
              {/* Header */}
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <div className={`${getPlatformColor(post.platform)} p-2 rounded-lg text-white`}>
                    {getPlatformIcon(post.platform)}
                  </div>
                  <div>
                    <h3 className="font-bold text-lg capitalize">{post.platform} Post</h3>
                    <p className="text-sm text-gray-600 capitalize">{post.content_type.replace('_', ' ')}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    post.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                    post.status === 'posted' ? 'bg-green-100 text-green-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {post.status}
                  </span>
                </div>
              </div>

              {/* Caption */}
              <div className="mb-4">
                <div className="bg-gray-50 rounded-lg p-4 relative">
                  <div className="prose max-w-none">
                    <p className="text-gray-800 whitespace-pre-wrap">{post.caption}</p>
                  </div>
                  <button
                    onClick={() => handleCopyToClipboard(post.caption, post.id)}
                    className="absolute top-2 right-2 p-2 bg-white rounded hover:bg-gray-100 transition-colors"
                  >
                    {copiedId === post.id ? (
                      <Check className="w-4 h-4 text-green-600" />
                    ) : (
                      <Copy className="w-4 h-4 text-gray-600" />
                    )}
                  </button>
                </div>
              </div>

              {/* Hashtags */}
              {post.hashtags && post.hashtags.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Hashtags:</h4>
                  <div className="flex flex-wrap gap-2">
                    {post.hashtags.map((tag, idx) => (
                      <span key={idx} className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm">
                        #{tag.replace('#', '')}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* CTA & Best Time */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-1">Call to Action:</h4>
                  <p className="text-sm text-gray-600">{post.cta}</p>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-1 flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    Best Time to Post:
                  </h4>
                  <p className="text-sm text-gray-600">{post.best_time}</p>
                </div>
              </div>

              {/* Products */}
              {post.products && post.products.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Featured Products:</h4>
                  <div className="flex flex-wrap gap-2">
                    {post.products.map((product) => (
                      <span key={product.id} className="bg-green-50 text-green-700 px-3 py-1 rounded text-sm">
                        {product.name} - ₹{product.price?.toLocaleString()}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Template Generated Image */}
              {post.generated_image && (
                <div className="mb-4">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                    <ImageIcon className="w-4 h-4 text-blue-500" />
                    Generated Visual Design:
                  </h4>
                  <div className="relative group">
                    <img 
                      src={post.generated_image} 
                      alt="Generated Design" 
                      className="w-full h-auto rounded-lg border-2 border-blue-200 shadow-md"
                    />
                    <div className="absolute top-2 right-2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <a
                        href={post.generated_image}
                        download={`social-media-${post.platform}-${Date.now()}.png`}
                        className="bg-white text-gray-800 p-2 rounded-lg shadow-lg hover:bg-gray-100"
                        title="Download Image"
                      >
                        <Download className="w-4 h-4" />
                      </a>
                    </div>
                  </div>
                </div>
              )}

              {/* AI Generated Image */}
              {post.ai_generated_image && (
                <div className="mb-4">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-purple-500" />
                    AI Generated Image:
                  </h4>
                  <div className="relative group">
                    <img 
                      src={post.ai_generated_image} 
                      alt="AI Generated" 
                      className="w-full h-auto rounded-lg border-2 border-purple-200"
                    />
                    <div className="absolute top-2 right-2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <a
                        href={post.ai_generated_image}
                        download="ai-generated-social-media.png"
                        className="bg-white text-gray-800 p-2 rounded-lg shadow-lg hover:bg-gray-100"
                        title="Download Image"
                      >
                        <Download className="w-4 h-4" />
                      </a>
                    </div>
                  </div>
                </div>
              )}


              {/* Engagement Stats */}
              {post.status === 'posted' && post.engagement && (
                <div className="grid grid-cols-3 gap-4 mb-4 p-3 bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <div className="text-xl font-bold text-gray-900">{post.engagement.likes || 0}</div>
                    <div className="text-xs text-gray-600">Likes</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-gray-900">{post.engagement.comments || 0}</div>
                    <div className="text-xs text-gray-600">Comments</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-gray-900">{post.engagement.shares || 0}</div>
                    <div className="text-xs text-gray-600">Shares</div>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  onClick={() => handleGenerateVisualDesign(post)}
                  disabled={generatingImage}
                  className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white py-2 rounded-lg hover:from-purple-600 hover:to-pink-600 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {generatingImage ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                      Generating...
                    </>
                  ) : (
                    <>
                      <ImageIcon className="w-4 h-4" />
                      Create Visual Design
                    </>
                  )}
                </button>
                
                {/* AI Image Generation Button */}
                <button
                  onClick={() => handleGenerateAIImage(post)}
                  disabled={generatingImage}
                  className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-lg hover:from-purple-600 hover:to-pink-600 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {generatingImage ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                      Generating AI Image...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Generate AI Image
                    </>
                  )}
                </button>
                
                <button
                  onClick={() => handleCopyToClipboard(`${post.caption}\n\n${post.hashtags?.map(h => `#${h.replace('#', '')}`).join(' ')}`, `${post.id}-full`)}
                  className="bg-blue-50 text-blue-600 px-4 py-2 rounded-lg hover:bg-blue-100 transition-colors flex items-center gap-2"
                >
                  {copiedId === `${post.id}-full` ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  Copy
                </button>
                <button
                  onClick={() => handleDeletePost(post.id)}
                  className="bg-red-50 text-red-600 px-4 py-2 rounded-lg hover:bg-red-100 transition-colors flex items-center gap-2"
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

      {/* Generate Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full my-8">
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <Sparkles className="w-6 h-6 text-amber-700" />
                Generate Social Media Post
              </h2>

              <div className="space-y-4">
                {/* Platform & Type */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Platform</label>
                    <select
                      value={formData.platform}
                      onChange={(e) => setFormData({...formData, platform: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                    >
                      <option value="facebook">Facebook</option>
                      <option value="instagram">Instagram</option>
                      <option value="linkedin">LinkedIn</option>
                      <option value="twitter">Twitter</option>
                      <option value="all">All Platforms</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Post Type</label>
                    <select
                      value={formData.post_type}
                      onChange={(e) => setFormData({...formData, post_type: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                    >
                      <option value="product">Product</option>
                      <option value="offer">Offer</option>
                      <option value="testimonial">Testimonial</option>
                      <option value="educational">Educational</option>
                      <option value="festival">Festival</option>
                    </select>
                  </div>
                </div>

                {/* Content Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Content Type</label>
                  <select
                    value={formData.content_type}
                    onChange={(e) => setFormData({...formData, content_type: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                  >
                    <option value="sale">Sale</option>
                    <option value="new_product">New Product</option>
                    <option value="combo_offer">Combo Offer</option>
                    <option value="seasonal">Seasonal</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>

                {/* Product Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Products (Optional) - {formData.product_ids.length} selected
                  </label>
                  <div className="border rounded-lg p-4 max-h-48 overflow-y-auto">
                    <div className="grid grid-cols-2 gap-2">
                      {products.slice(0, 20).map((product) => (
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
                            <div className="text-xs text-gray-500">₹{product.price?.toLocaleString()}</div>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Offer Details */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Offer Details (Optional)</label>
                  <input
                    type="text"
                    value={formData.offer_details}
                    onChange={(e) => setFormData({...formData, offer_details: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                    placeholder="e.g., 20% off, Buy 1 Get 1, Free Shipping"
                  />
                </div>

                {/* Custom Message */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Custom Message (Optional)</label>
                  <textarea
                    value={formData.custom_message}
                    onChange={(e) => setFormData({...formData, custom_message: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                    rows="3"
                    placeholder="Add any specific instructions or information..."
                  ></textarea>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setFormData({
                      post_type: 'product',
                      platform: 'facebook',
                      content_type: 'new_product',
                      product_ids: [],
                      offer_details: '',
                      custom_message: ''
                    });
                  }}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                  disabled={generating}
                >
                  Cancel
                </button>
                <button
                  onClick={handleGeneratePost}
                  className="flex-1 bg-amber-700 text-white px-4 py-2 rounded-lg hover:bg-amber-800 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  disabled={generating}
                >
                  {generating ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Generate Post with AI
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Visual Design Modal */}
      {showDesignModal && currentDesign && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full my-8">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold flex items-center gap-2">
                  <ImageIcon className="w-6 h-6 text-purple-600" />
                  Visual Design Preview
                </h2>
                <button
                  onClick={() => setShowDesignModal(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>

              {/* Design Preview */}
              <div className="mb-6">
                <div 
                  ref={designRef}
                  className="bg-gradient-to-br from-purple-100 to-pink-100 p-8 rounded-lg border-2 border-dashed border-purple-300 min-h-[400px] flex flex-col justify-center items-center text-center"
                  style={{
                    backgroundImage: currentDesign.background_style ? `linear-gradient(${currentDesign.background_style})` : undefined
                  }}
                >
                  {/* Brand Header */}
                  {currentDesign.brand_name && (
                    <div className="mb-6">
                      <h1 className="text-3xl font-bold text-gray-800 mb-2">
                        {currentDesign.brand_name}
                      </h1>
                      {currentDesign.brand_tagline && (
                        <p className="text-lg text-gray-600 italic">
                          {currentDesign.brand_tagline}
                        </p>
                      )}
                    </div>
                  )}

                  {/* Main Content */}
                  <div className="mb-6 max-w-2xl">
                    <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                      {currentDesign.headline || 'Your Amazing Product'}
                    </h2>
                    <p className="text-lg text-gray-700 leading-relaxed">
                      {currentDesign.caption}
                    </p>
                  </div>

                  {/* Products Display */}
                  {currentDesign.products && currentDesign.products.length > 0 && (
                    <div className="mb-6">
                      <div className="flex flex-wrap justify-center gap-4">
                        {currentDesign.products.slice(0, 3).map((product) => (
                          <div key={product.id} className="bg-white rounded-lg p-4 shadow-md">
                            <h3 className="font-semibold text-gray-800">{product.name}</h3>
                            <p className="text-purple-600 font-bold">₹{product.price?.toLocaleString()}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Call to Action */}
                  {currentDesign.cta && (
                    <div className="mb-4">
                      <button className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-8 py-3 rounded-full text-lg font-semibold shadow-lg hover:shadow-xl transition-shadow">
                        {currentDesign.cta}
                      </button>
                    </div>
                  )}

                  {/* Hashtags */}
                  {currentDesign.hashtags && currentDesign.hashtags.length > 0 && (
                    <div className="flex flex-wrap justify-center gap-2 mt-4">
                      {currentDesign.hashtags.slice(0, 5).map((tag, idx) => (
                        <span key={idx} className="text-purple-600 font-medium">
                          #{tag.replace('#', '')}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={() => setShowDesignModal(false)}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Close
                </button>
                <button
                  onClick={handleDownloadDesign}
                  className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-lg hover:from-purple-600 hover:to-pink-600 flex items-center justify-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Download Design
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SocialMediaPostCreator;
