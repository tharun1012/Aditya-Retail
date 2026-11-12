import React, { useState, useEffect } from 'react';
import { WifiOff, Wifi } from 'lucide-react';

/**
 * Offline Indicator Component
 * Shows when the app is offline and when it comes back online
 */
const OfflineIndicator = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showOnlineMessage, setShowOnlineMessage] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setShowOnlineMessage(true);
      
      // Hide the "back online" message after 3 seconds
      setTimeout(() => {
        setShowOnlineMessage(false);
      }, 3000);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowOnlineMessage(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Show offline indicator
  if (!isOnline) {
    return (
      <div className="fixed top-0 left-0 right-0 bg-red-600 text-white py-2 px-4 z-50 shadow-lg">
        <div className="max-w-7xl mx-auto flex items-center justify-center gap-2">
          <WifiOff className="w-5 h-5" />
          <span className="font-medium">You're offline</span>
          <span className="text-sm opacity-90">- Some features may be limited</span>
        </div>
      </div>
    );
  }

  // Show "back online" message temporarily
  if (showOnlineMessage) {
    return (
      <div className="fixed top-0 left-0 right-0 bg-green-600 text-white py-2 px-4 z-50 shadow-lg animate-slide-down">
        <div className="max-w-7xl mx-auto flex items-center justify-center gap-2">
          <Wifi className="w-5 h-5" />
          <span className="font-medium">Back online!</span>
        </div>
      </div>
    );
  }

  return null;
};

export default OfflineIndicator;
