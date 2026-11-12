/**
 * Performance Monitoring Utilities
 * Tracks Web Vitals and sends to analytics
 */

/**
 * Report Web Vitals to console (or analytics service)
 * @param {Object} metric - Web Vital metric
 */
export const reportWebVitals = (metric) => {
  // In development, log to console
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Performance] ${metric.name}:`, metric.value, metric);
  }
  
  // In production, send to analytics
  if (process.env.NODE_ENV === 'production' && window.gtag) {
    window.gtag('event', metric.name, {
      event_category: 'Web Vitals',
      value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
      event_label: metric.id,
      non_interaction: true,
    });
  }
};

/**
 * Measure and report page load time
 */
export const measurePageLoad = () => {
  if (window.performance && window.performance.timing) {
    const perfData = window.performance.timing;
    const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
    const connectTime = perfData.responseEnd - perfData.requestStart;
    const renderTime = perfData.domComplete - perfData.domLoading;
    
    console.log('[Performance Metrics]');
    console.log('Page Load Time:', pageLoadTime + 'ms');
    console.log('Server Response Time:', connectTime + 'ms');
    console.log('DOM Render Time:', renderTime + 'ms');
    
    return {
      pageLoadTime,
      connectTime,
      renderTime
    };
  }
};

/**
 * Lazy load images with Intersection Observer
 * @param {string} selector - CSS selector for images
 */
export const enableLazyLoading = (selector = 'img[loading="lazy"]') => {
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
          }
          observer.unobserve(img);
        }
      });
    });

    document.querySelectorAll(selector).forEach(img => {
      imageObserver.observe(img);
    });
  }
};

/**
 * Preload critical resources
 * @param {Array} resources - Array of resource URLs
 * @param {string} type - Resource type (script, style, image)
 */
export const preloadResources = (resources, type = 'script') => {
  resources.forEach(url => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = url;
    link.as = type;
    document.head.appendChild(link);
  });
};

/**
 * Measure component render time
 * @param {string} componentName
 * @param {Function} callback
 */
export const measureComponentRender = (componentName, callback) => {
  const startTime = performance.now();
  callback();
  const endTime = performance.now();
  const renderTime = endTime - startTime;
  
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Component Render] ${componentName}: ${renderTime.toFixed(2)}ms`);
  }
  
  return renderTime;
};

/**
 * Get performance recommendations
 */
export const getPerformanceRecommendations = () => {
  const recommendations = [];
  
  if (window.performance && window.performance.timing) {
    const perfData = window.performance.timing;
    const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
    
    if (pageLoadTime > 3000) {
      recommendations.push('Page load time is slow (>3s). Consider code splitting and lazy loading.');
    }
    
    const connectTime = perfData.responseEnd - perfData.requestStart;
    if (connectTime > 1000) {
      recommendations.push('Server response time is slow (>1s). Optimize backend queries and add caching.');
    }
    
    const renderTime = perfData.domComplete - perfData.domLoading;
    if (renderTime > 2000) {
      recommendations.push('DOM rendering is slow (>2s). Reduce JavaScript execution and optimize CSS.');
    }
  }
  
  // Check for lazy-loaded images
  const totalImages = document.querySelectorAll('img').length;
  const lazyImages = document.querySelectorAll('img[loading="lazy"]').length;
  
  if (totalImages > 0 && lazyImages / totalImages < 0.5) {
    recommendations.push(`Only ${Math.round((lazyImages / totalImages) * 100)}% of images use lazy loading. Add loading="lazy" to more images.`);
  }
  
  return recommendations;
};

/**
 * Log performance summary on page load
 */
export const logPerformanceSummary = () => {
  if (typeof window !== 'undefined') {
    window.addEventListener('load', () => {
      setTimeout(() => {
        const metrics = measurePageLoad();
        const recommendations = getPerformanceRecommendations();
        
        console.log('[Performance Summary]');
        console.log('Recommendations:', recommendations);
        
        // Check if page meets Core Web Vitals
        if (metrics.pageLoadTime < 2500) {
          console.log('✅ Good page load time');
        } else if (metrics.pageLoadTime < 4000) {
          console.log('⚠️ Needs improvement - page load time');
        } else {
          console.log('❌ Poor page load time');
        }
      }, 1000);
    });
  }
};
