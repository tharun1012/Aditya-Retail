import axios from 'axios';
import { BACKEND_URL, API_BASE } from '../config/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding session ID
api.interceptors.request.use(
  (config) => {
    // Add session ID to requests that need it
    const sessionId = getSessionId();
    if (config.data && typeof config.data === 'object') {
      config.data.session_id = config.data.session_id || sessionId;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    
    // Handle different error scenarios
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. Please try again.');
    }
    
    if (error.response?.status === 500) {
      throw new Error('Server error. Please try again later.');
    }
    
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    
    throw error;
  }
);

// Session management
function getSessionId() {
  let sessionId = localStorage.getItem('aditya_retail_session_id');
  if (!sessionId) {
    sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('aditya_retail_session_id', sessionId);
  }
  return sessionId;
}

// Product API
export const productAPI = {
  // Get all products with filtering
  getProducts: async (filters = {}) => {
    const params = new URLSearchParams();
    
    if (filters.category) params.append('category', filters.category);
    if (filters.brand) params.append('brand', filters.brand);
    if (filters.min_price) params.append('min_price', filters.min_price);
    if (filters.max_price) params.append('max_price', filters.max_price);
    if (filters.in_stock) params.append('in_stock', 'true');
    
    const response = await api.get(`/products?${params}`);
    return response.data;
  },

  // Get single product
  getProduct: async (productId) => {
    const response = await api.get(`/products/${productId}`);
    return response.data;
  },

  // Get categories
  getCategories: async () => {
    const response = await api.get('/categories');
    return response.data;
  },

  // Get brands
  getBrands: async () => {
    const response = await api.get('/brands');
    return response.data;
  },
};

// Cart API
export const cartAPI = {
  // Add item to cart
  addToCart: async (productId, quantity = 1) => {
    const sessionId = getSessionId();
    const response = await api.post('/cart/add', {
      product_id: productId,
      quantity: quantity,
      session_id: sessionId
    });
    return response.data;
  },

  // Get cart contents
  getCart: async () => {
    const sessionId = getSessionId();
    const response = await api.get(`/cart/${sessionId}`);
    return response.data;
  },
};

// Order API
export const orderAPI = {
  // Create order
  createOrder: async (orderData) => {
    const response = await api.post('/orders', orderData);
    return response.data;
  },

  // Get order details
  getOrder: async (orderId) => {
    const response = await api.get(`/orders/${orderId}`);
    return response.data;
  },
};

// AI Agent API
export const aiAPI = {
  // Chat with AI agents
  chat: async (agentType, message, context = {}) => {
    const sessionId = getSessionId();
    const response = await api.post('/ai/chat', {
      session_id: sessionId,
      agent_type: agentType,
      message: message,
      context: context
    });
    return response.data;
  },

  // Get chat history
  getChatHistory: async (agentType = null) => {
    const sessionId = getSessionId();
    const params = agentType ? `?agent_type=${agentType}` : '';
    const response = await api.get(`/ai/chat/history/${sessionId}${params}`);
    return response.data;
  },

  // Create service request
  createServiceRequest: async (serviceData) => {
    const response = await api.post('/ai/service/request', serviceData);
    return response.data;
  },

  // Get inventory analysis
  getInventoryAnalysis: async () => {
    const response = await api.get('/ai/inventory/analysis');
    return response.data;
  },

  // Get marketing insights
  getMarketingInsights: async () => {
    const response = await api.get('/ai/marketing/insights');
    return response.data;
  },

  // Update delivery status
  updateDeliveryStatus: async (orderId, status, trackingId = null, customerMessage = null) => {
    const response = await api.post('/ai/delivery/update', {
      order_id: orderId,
      status: status,
      tracking_id: trackingId,
      customer_message: customerMessage
    });
    return response.data;
  },

  // Get AI dashboard summary
  getDashboardSummary: async () => {
    const response = await api.get('/ai/dashboard/summary');
    return response.data;
  },
};

// Status/Health check API
export const statusAPI = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/');
    return response.data;
  },

  // Create status check
  createStatusCheck: async (clientName) => {
    const response = await api.post('/status', { client_name: clientName });
    return response.data;
  },
};

// Utility functions
export const utils = {
  getSessionId,
  
  // Custom fetch wrapper that forces HTTPS
  fetchAPI: async (endpoint, options = {}) => {
    // Ensure endpoint starts with /
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    
    // Force HTTPS by using window.location.origin which will always be HTTPS in production
    const baseUrl = window.location.origin;
    const url = `${baseUrl}${cleanEndpoint}`;
    
    // Force HTTPS protocol
    const httpsUrl = url.replace(/^http:/, 'https:');
    
    console.log('[API Utils] Fetch URL:', httpsUrl);
    
    return fetch(httpsUrl, options);
  },
  
  // Format price for display
  formatPrice: (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  },

  // Calculate discount percentage
  calculateDiscount: (originalPrice, salePrice) => {
    if (!originalPrice || originalPrice <= salePrice) return 0;
    return Math.round(((originalPrice - salePrice) / originalPrice) * 100);
  },

  // Generate product URL slug
  generateSlug: (name) => {
    return name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '');
  },
};

export default api;