/**
 * Image utility functions for handling product images
 */

// Fallback images by category
const FALLBACK_IMAGES = {
  'Chimney': 'https://images.unsplash.com/photo-1556911220-bff31c812dba?w=800&q=80',
  'Microwave': 'https://images.unsplash.com/photo-1585659722983-3a675dabf23d?w=800&q=80',
  'Oven': 'https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?w=800&q=80',
  'Hob': 'https://images.unsplash.com/photo-1556911220-bff31c812dba?w=800&q=80',
  'Dishwasher': 'https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=800&q=80',
  'Washing Machine': 'https://images.unsplash.com/photo-1626806819282-2c1dc01a5e0c?w=800&q=80',
  'Mixer Grinder': 'https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=800&q=80',
  'Air Fryer': 'https://images.unsplash.com/photo-1585659722983-3a675dabf23d?w=800&q=80',
  'Coffee Machine': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&q=80',
  'default': 'https://images.unsplash.com/photo-1588856905962-a0e9e81b8f1d?w=800&q=80'
};

/**
 * Get product image with fallback support
 * @param {Object} product - Product object
 * @param {number} index - Image index (default: 0)
 * @returns {string} - Image URL
 */
export const getProductImage = (product, index = 0) => {
  // Check if product has images
  if (product?.images && Array.isArray(product.images) && product.images.length > index) {
    const imageUrl = product.images[index];
    
    // Check if it's a valid full URL
    if (imageUrl && (imageUrl.startsWith('http://') || imageUrl.startsWith('https://'))) {
      return imageUrl;
    }
    
    // If it's a relative path, skip it and use fallback
  }
  
  // Check legacy 'image' field
  if (product?.image && (product.image.startsWith('http://') || product.image.startsWith('https://'))) {
    return product.image;
  }
  
  // Return category-specific fallback or default
  const category = product?.category || product?.subcategory || 'default';
  return FALLBACK_IMAGES[category] || FALLBACK_IMAGES['default'];
};

/**
 * Get all product images with fallback
 * @param {Object} product - Product object
 * @returns {Array} - Array of image URLs
 */
export const getProductImages = (product) => {
  if (!product?.images || !Array.isArray(product.images)) {
    return [getProductImage(product, 0)];
  }
  
  // Filter valid URLs and add fallback if needed
  const validImages = product.images.filter(img => 
    img && (img.startsWith('http://') || img.startsWith('https://'))
  );
  
  if (validImages.length === 0) {
    return [getProductImage(product, 0)];
  }
  
  return validImages;
};

/**
 * Handle image loading error
 * @param {Event} e - Error event
 * @param {Object} product - Product object
 */
export const handleImageError = (e, product) => {
  const fallbackUrl = getProductImage(product, 0);
  if (e.target.src !== fallbackUrl) {
    e.target.src = fallbackUrl;
  }
};
