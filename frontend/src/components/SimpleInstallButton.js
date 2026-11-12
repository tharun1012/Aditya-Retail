import React, { useState, useEffect } from 'react';
import { Download } from 'lucide-react';

/**
 * Simple Install Button - floating action button
 * Only appears when the browser has a real native install prompt available.
 * No QR code or manual instructions — pure native install trigger.
 */
const SimpleInstallButton = () => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    const standalone =
      window.matchMedia('(display-mode: standalone)').matches ||
      window.navigator.standalone === true;

    setIsInstalled(standalone);

    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
    };

    window.addEventListener(
      'beforeinstallprompt',
      handleBeforeInstallPrompt
    );

    return () => {
      window.removeEventListener(
        'beforeinstallprompt',
        handleBeforeInstallPrompt
      );
    };
  }, []);

  const handleClick = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    await deferredPrompt.userChoice;
    setDeferredPrompt(null);
  };

  if (isInstalled || !deferredPrompt) {
    return null;
  }

  return (
    <button
      onClick={handleClick}
      className="fixed bottom-20 right-4 bg-blue-600 text-white rounded-full shadow-xl hover:bg-blue-700 transition-all hover:scale-105 z-[9998] flex items-center justify-center"
      style={{ width: '50px', height: '50px' }}
      aria-label="Install App"
      data-testid="install-app-fab"
    >
      <Download className="w-5 h-5" />
    </button>
  );
};

export default SimpleInstallButton;