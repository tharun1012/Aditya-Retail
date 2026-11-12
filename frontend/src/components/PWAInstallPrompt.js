import React, { useState, useEffect } from 'react';
import { X, Download, Smartphone } from 'lucide-react';

/**
 * PWA Install Prompt Component
 * Shows a banner prompting users to install the app
 */
const PWAInstallPrompt = () => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [isStandalone, setIsStandalone] = useState(false);

  useEffect(() => {
    // Check if already installed
    const standalone = window.matchMedia('(display-mode: standalone)').matches || 
                      window.navigator.standalone === true;
    setIsStandalone(standalone);

    // Check if iOS
    const iOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    setIsIOS(iOS);

    // Check if user already dismissed
    const dismissed = localStorage.getItem('pwa-install-dismissed');
    const dismissedTime = dismissed ? parseInt(dismissed) : 0;
    const daysSinceDismissed = (Date.now() - dismissedTime) / (1000 * 60 * 60 * 24);

    // Show prompt if not standalone, not dismissed recently
    if (!standalone && daysSinceDismissed > 7) {
      // Listen for beforeinstallprompt event (Android/Desktop)
      const handleBeforeInstallPrompt = (e) => {
        e.preventDefault();
        setDeferredPrompt(e);
        setShowPrompt(true);
      };

      window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

      // For iOS, show manual instructions after a delay
      if (iOS && !standalone) {
        setTimeout(() => {
          setShowPrompt(true);
        }, 5000); // Show after 5 seconds
      }

      return () => {
        window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      };
    }
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt && !isIOS) {
      return;
    }

    if (deferredPrompt) {
      // Android/Desktop - show native install prompt
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      
      console.log(`[PWA] User response to install prompt: ${outcome}`);
      
      if (outcome === 'accepted') {
        console.log('[PWA] User accepted the install prompt');
      }
      
      setDeferredPrompt(null);
      setShowPrompt(false);
    }
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    localStorage.setItem('pwa-install-dismissed', Date.now().toString());
  };

  if (isStandalone || !showPrompt) {
    return null;
  }

  // iOS Install Instructions
  if (isIOS) {
    return (
      <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-r from-amber-700 to-amber-800 text-white p-4 shadow-2xl z-50 animate-slide-up">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={handleDismiss}
            className="absolute top-2 right-2 text-white hover:bg-white hover:bg-opacity-20 rounded-full p-1"
          >
            <X className="w-5 h-5" />
          </button>
          
          <div className="flex items-start gap-4 pr-8">
            <Smartphone className="w-8 h-8 flex-shrink-0 mt-1" />
            <div>
              <h3 className="font-bold text-lg mb-2">Install Aditya Retail App</h3>
              <p className="text-sm mb-3">
                Get the best shopping experience! Install our app on your iPhone:
              </p>
              <ol className="text-sm space-y-2">
                <li>1. Tap the <strong>Share</strong> button <span className="inline-block">⬆️</span> at the bottom of Safari</li>
                <li>2. Scroll and tap <strong>"Add to Home Screen"</strong> 📱</li>
                <li>3. Tap <strong>"Add"</strong> in the top right corner</li>
              </ol>
              <p className="text-xs mt-3 opacity-90">
                ✨ Enjoy offline access, faster loading, and app-like experience!
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Android/Desktop Install Prompt
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-r from-blue-700 to-blue-800 text-white p-4 shadow-2xl z-50 animate-slide-up">
      <div className="max-w-4xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-4 flex-1">
          <div className="bg-white bg-opacity-20 p-3 rounded-lg">
            <Download className="w-8 h-8" />
          </div>
          <div>
            <h3 className="font-bold text-lg">Install Aditya Retail App</h3>
            <p className="text-sm opacity-90">
              Get faster access, offline support, and notifications!
            </p>
          </div>
        </div>
        
        <div className="flex gap-3 ml-4">
          <button
            onClick={handleDismiss}
            className="px-4 py-2 text-white hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
          >
            Not Now
          </button>
          <button
            onClick={handleInstallClick}
            className="px-6 py-2 bg-white text-blue-800 font-semibold rounded-lg hover:bg-opacity-90 transition-colors"
          >
            Install
          </button>
        </div>
      </div>
    </div>
  );
};

export default PWAInstallPrompt;
