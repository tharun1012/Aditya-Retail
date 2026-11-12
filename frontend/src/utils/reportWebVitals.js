/**
 * Web Vitals Reporter
 * Measures and reports Core Web Vitals (LCP, FID, CLS, FCP, TTFB)
 */

const reportWebVitals = (onPerfEntry) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ onCLS, onFCP, onLCP, onTTFB, onINP }) => {
      // Cumulative Layout Shift (CLS)
      // Good: < 0.1, Needs Improvement: 0.1-0.25, Poor: > 0.25
      onCLS(onPerfEntry);
      
      // Interaction to Next Paint (INP) - replaces deprecated FID
      // Good: < 200ms, Needs Improvement: 200-500ms, Poor: > 500ms
      onINP(onPerfEntry);
      
      // First Contentful Paint (FCP)
      // Good: < 1.8s, Needs Improvement: 1.8-3s, Poor: > 3s
      onFCP(onPerfEntry);
      
      // Largest Contentful Paint (LCP)
      // Good: < 2.5s, Needs Improvement: 2.5-4s, Poor: > 4s
      onLCP(onPerfEntry);
      
      // Time to First Byte (TTFB)
      // Good: < 800ms, Needs Improvement: 800-1800ms, Poor: > 1800ms
      onTTFB(onPerfEntry);
    });
  }
};

/**
 * Custom handler to log and send metrics to analytics
 */
export const handleWebVitals = (metric) => {
  const { name, value, rating, id } = metric;
  
  // Log in development
  if (process.env.NODE_ENV === 'development') {
    const emoji = rating === 'good' ? '✅' : rating === 'needs-improvement' ? '⚠️' : '❌';
    console.log(`[Web Vitals] ${emoji} ${name}:`, {
      value: Math.round(name === 'CLS' ? value * 1000 : value),
      rating,
      id
    });
  }
  
  // Send to Google Analytics in production
  if (process.env.NODE_ENV === 'production' && window.gtag) {
    window.gtag('event', name, {
      event_category: 'Web Vitals',
      value: Math.round(name === 'CLS' ? value * 1000 : value),
      event_label: id,
      non_interaction: true,
      metric_rating: rating
    });
  }
  
  // Log thresholds
  if (process.env.NODE_ENV === 'development') {
    const thresholds = {
      CLS: { good: 0.1, poor: 0.25 },
      INP: { good: 200, poor: 500 },
      LCP: { good: 2500, poor: 4000 },
      FCP: { good: 1800, poor: 3000 },
      TTFB: { good: 800, poor: 1800 }
    };
    
    const threshold = thresholds[name];
    if (threshold) {
      const normalizedValue = name === 'CLS' ? value : Math.round(value);
      if (normalizedValue <= threshold.good) {
        console.log(`✅ ${name} is Good (≤ ${threshold.good})`);
      } else if (normalizedValue <= threshold.poor) {
        console.log(`⚠️ ${name} Needs Improvement (${threshold.good} - ${threshold.poor})`);
      } else {
        console.log(`❌ ${name} is Poor (> ${threshold.poor})`);
      }
    }
  }
};

export default reportWebVitals;
