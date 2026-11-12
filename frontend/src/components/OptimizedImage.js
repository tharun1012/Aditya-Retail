import React from 'react';

/**
 * Optimized Image Component with lazy loading, proper alt text, and performance optimizations
 * @param {string} src - Image source URL
 * @param {string} alt - Alt text for accessibility and SEO
 * @param {string} className - CSS classes
 * @param {boolean} priority - If true, loads immediately (for above-the-fold images)
 * @param {function} onError - Error handler
 * @param {object} props - Additional props
 */
const OptimizedImage = ({ 
  src, 
  alt, 
  className = '', 
  priority = false,
  onError,
  ...props 
}) => {
  return (
    <img
      src={src}
      alt={alt}
      loading={priority ? 'eager' : 'lazy'}
      decoding="async"
      className={className}
      onError={onError}
      {...props}
    />
  );
};

export default OptimizedImage;
