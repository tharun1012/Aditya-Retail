import React, { useState, useEffect } from 'react';
import { Download } from 'lucide-react';

/**
 * Install App Button - Always visible option to install PWA
 * Shows in header/nav for easy access.
 * Uses the browser's real native install prompt only — no QR code or manual instructions modal.
 */
const InstallAppButton = ({ variant = 'default' }) => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [isAndroid, setIsAndroid] = useState(false);

  useEffect(() => {
    // Check if already installed
    const standalone = window.matchMedia('(display-mode: standalone)').matches ||
                      window.navigator.standalone === true;
    setIsInstalled(standalone);

    // Check if iOS
    const iOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    setIsIOS(iOS);

    // Check if Android
    const android = /Android/.test(navigator.userAgent);
    setIsAndroid(android);

    // Listen for install prompt (Android/Desktop)
    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const handleNativeInstall = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;

      if (outcome === 'accepted') {
        console.log('[PWA] User accepted install');
      }

      setDeferredPrompt(null);
    }
  };

  const handleInstall = async () => {
    if (deferredPrompt) {
      await handleNativeInstall();
    } else if (isIOS) {
      alert('On iPhone/iPad: tap the Share button, then "Add to Home Screen".');
    } else {
      alert('This app is already installed, or your browser doesn\'t support one-click install.');
    }
  };

  // Don't show if already running inside the installed standalone app
  if (isInstalled) {
    return null;
  }

  // Button variants
  if (variant === 'header') {
    return (
      <button
        onClick={handleInstall}
        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
        data-testid="install-app-header-btn"
      >
        <Download className="w-4 h-4" />
        <span className="hidden sm:inline">Install App</span>
        <span className="sm:hidden">Install</span>
      </button>
    );
  }

  if (variant === 'floating') {
    return (
      <button
        onClick={handleInstall}
        className="fixed bottom-20 right-4 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-all hover:scale-110 z-40"
        title="Install App"
        data-testid="install-app-floating-btn"
      >
        <Download className="w-6 h-6" />
      </button>
    );
  }

  // Default variant
  return (
    <button
      onClick={handleInstall}
      className="flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-md"
      data-testid="install-app-btn"
    >
      <Download className="w-5 h-5" />
      <span className="font-medium">Install App</span>
    </button>
  );
};

export default InstallAppButton;