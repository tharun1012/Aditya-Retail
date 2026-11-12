/**
 * Google Analytics 4 Integration
 * Measurement ID: G-G2M4SXT484
 * Tracks user events for e-commerce analytics
 */

const GA_MEASUREMENT_ID = 'G-G2M4SXT484';

// Initialize Google Analytics
export const initGA = (measurementId = GA_MEASUREMENT_ID) => {
  if (!measurementId) {
    console.warn('Google Analytics Measurement ID not provided');
    return;
  }

  // Load gtag.js script if not already loaded
  if (!document.querySelector(`script[src*="googletagmanager.com/gtag"]`)) {
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
    document.head.appendChild(script);
  }

  // Initialize dataLayer and gtag
  window.dataLayer = window.dataLayer || [];
  function gtag() {
    window.dataLayer.push(arguments);
  }
  window.gtag = gtag;
  
  gtag('js', new Date());
  gtag('config', measurementId, {
    send_page_view: false // We'll manually track page views
  });
};

// Track page view
export const trackPageView = (path, title) => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'page_view', {
      page_path: path,
      page_title: title
    });
  }
};

// Track product view
export const trackProductView = (product) => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'view_item', {
      currency: 'INR',
      value: product.price || 0,
      items: [{
        item_id: product.id,
        item_name: product.name,
        item_brand: product.brand,
        item_category: product.category,
        price: product.price || 0,
        quantity: 1
      }]
    });
  }
};

// Track add to cart
export const trackAddToCart = (product, quantity = 1) => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'add_to_cart', {
      currency: 'INR',
      value: (product.price || 0) * quantity,
      items: [{
        item_id: product.id,
        item_name: product.name,
        item_brand: product.brand,
        item_category: product.category,
        price: product.price || 0,
        quantity: quantity
      }]
    });
  }
};

// Track remove from cart
export const trackRemoveFromCart = (product, quantity = 1) => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'remove_from_cart', {
      currency: 'INR',
      value: (product.price || 0) * quantity,
      items: [{
        item_id: product.id,
        item_name: product.name,
        item_brand: product.brand,
        item_category: product.category,
        price: product.price || 0,
        quantity: quantity
      }]
    });
  }
};

// Track begin checkout
export const trackBeginCheckout = (cartItems, totalValue) => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'begin_checkout', {
      currency: 'INR',
      value: totalValue,
      items: cartItems.map(item => ({
        item_id: item.id,
        item_name: item.name,
        item_brand: item.brand,
        item_category: item.category,
        price: item.price || 0,
        quantity: item.quantity || 1
      }))
    });
  }
};

// Track purchase
export const trackPurchase = (orderId, cartItems, totalValue, paymentMethod) => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'purchase', {
      transaction_id: orderId,
      currency: 'INR',
      value: totalValue,
      payment_type: paymentMethod,
      items: cartItems.map(item => ({
        item_id: item.id,
        item_name: item.name,
        item_brand: item.brand,
        item_category: item.category,
        price: item.price || 0,
        quantity: item.quantity || 1
      }))
    });
  }
};

// Track search
export const trackSearch = (searchTerm) => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'search', {
      search_term: searchTerm
    });
  }
};

// Track category view
export const trackCategoryView = (categoryName, productCount) => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'view_item_list', {
      item_list_id: categoryName,
      item_list_name: categoryName,
      items_count: productCount
    });
  }
};

// Track filter usage
export const trackFilterUsage = (filterType, filterValue) => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'filter_applied', {
      filter_type: filterType,
      filter_value: filterValue
    });
  }
};

// Track AI chat interaction
export const trackAIChatInteraction = (chatType, action) => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'ai_chat_interaction', {
      chat_type: chatType, // sales, service, delivery
      action: action // opened, closed, message_sent
    });
  }
};

// Track review submission
export const trackReviewSubmission = (productId, rating) => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'submit_review', {
      product_id: productId,
      rating: rating
    });
  }
};

// Generic custom event tracking
export const trackEvent = (eventName, eventParams = {}) => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', eventName, eventParams);
  }
};

// Track user login
export const trackLogin = (method = 'email') => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'login', { method });
  }
};

// Track user signup
export const trackSignUp = (method = 'email') => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'sign_up', { method });
  }
};

// Set user ID for cross-device tracking
export const setUserId = (userId) => {
  if (typeof window.gtag === 'function' && userId) {
    window.gtag('config', GA_MEASUREMENT_ID, { user_id: userId });
  }
};

// Track lead generated
export const trackLeadGenerated = (source = 'ai_chat', productCategory = '') => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'generate_lead', {
      source,
      product_category: productCategory
    });
  }
};

// Track service ticket created
export const trackServiceTicket = (productCategory, ticketId = '') => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'service_ticket_created', {
      product_category: productCategory,
      ticket_id: ticketId
    });
  }
};

// Track phone call click
export const trackPhoneCall = (phoneNumber) => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'click_to_call', {
      phone_number: phoneNumber
    });
  }
};

// Track WhatsApp click
export const trackWhatsAppClick = () => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'whatsapp_click');
  }
};

// Track consultation request
export const trackConsultationRequest = (consultationType = 'general') => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'consultation_requested', {
      consultation_type: consultationType
    });
  }
};

// Track AI chat start
export const trackAIChatStart = (agentType) => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'ai_chat_start', {
      agent_type: agentType
    });
  }
};

export default {
  initGA,
  trackPageView,
  trackProductView,
  trackAddToCart,
  trackRemoveFromCart,
  trackBeginCheckout,
  trackPurchase,
  trackSearch,
  trackCategoryView,
  trackFilterUsage,
  trackAIChatInteraction,
  trackAIChatStart,
  trackReviewSubmission,
  trackEvent,
  trackLogin,
  trackSignUp,
  setUserId,
  trackLeadGenerated,
  trackServiceTicket,
  trackPhoneCall,
  trackWhatsAppClick,
  trackConsultationRequest
};
