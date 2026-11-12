import { useEffect } from 'react';

/**
 * Mobile Optimizer Component
 * Applies mobile-specific fixes and optimizations
 */
const MobileOptimizer = () => {
  useEffect(() => {
    // Force mobile viewport
    const viewport = document.querySelector('meta[name="viewport"]');
    if (viewport) {
      viewport.setAttribute('content', 'width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes, viewport-fit=cover');
    }

    // Add mobile class to body
    if (window.innerWidth <= 768) {
      document.body.classList.add('mobile-view');
    }

    // Prevent horizontal scroll
    document.documentElement.style.overflowX = 'hidden';
    document.body.style.overflowX = 'hidden';

    // Handle resize
    const handleResize = () => {
      if (window.innerWidth <= 768) {
        document.body.classList.add('mobile-view');
      } else {
        document.body.classList.remove('mobile-view');
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return null; // This component doesn't render anything
};

export default MobileOptimizer;
