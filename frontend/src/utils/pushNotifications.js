import { BACKEND_URL } from '../config/api';
/**
 * Push Notification Manager
 * Handles push notification subscription and management
 */


/**
 * Check if push notifications are supported
 */
export function isPushNotificationSupported() {
  return 'serviceWorker' in navigator && 'PushManager' in window;
}

/**
 * Check current notification permission
 */
export function getNotificationPermission() {
  if (!('Notification' in window)) {
    return 'unsupported';
  }
  return Notification.permission;
}

/**
 * Request notification permission from user
 */
export async function requestNotificationPermission() {
  if (!('Notification' in window)) {
    console.log('[Push] Notifications not supported');
    return false;
  }

  if (Notification.permission === 'granted') {
    return true;
  }

  if (Notification.permission === 'denied') {
    console.log('[Push] Notifications permission denied');
    return false;
  }

  try {
    const permission = await Notification.requestPermission();
    console.log('[Push] Permission result:', permission);
    return permission === 'granted';
  } catch (error) {
    console.error('[Push] Error requesting permission:', error);
    return false;
  }
}

/**
 * Subscribe to push notifications
 */
export async function subscribeToPush(userId) {
  if (!isPushNotificationSupported()) {
    console.log('[Push] Push notifications not supported');
    return null;
  }

  try {
    // Request permission first
    const permissionGranted = await requestNotificationPermission();
    if (!permissionGranted) {
      return null;
    }

    // Get service worker registration
    const registration = await navigator.serviceWorker.ready;

    // Check if already subscribed
    let subscription = await registration.pushManager.getSubscription();

    if (subscription) {
      console.log('[Push] Already subscribed');
      return subscription;
    }

    // Create new subscription
    // Note: You'll need to generate VAPID keys and set REACT_APP_VAPID_PUBLIC_KEY
    const vapidPublicKey = process.env.REACT_APP_VAPID_PUBLIC_KEY;
    
    if (!vapidPublicKey) {
      console.warn('[Push] VAPID public key not configured');
      // For now, we'll skip actual push subscription until VAPID keys are set up
      return { demo: true };
    }

    subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
    });

    console.log('[Push] New subscription created');

    // Send subscription to backend
    await saveSubscriptionToBackend(subscription, userId);

    return subscription;
  } catch (error) {
    console.error('[Push] Subscription failed:', error);
    return null;
  }
}

/**
 * Unsubscribe from push notifications
 */
export async function unsubscribeFromPush() {
  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();

    if (subscription) {
      await subscription.unsubscribe();
      console.log('[Push] Unsubscribed successfully');
      
      // Notify backend
      await fetch(`${BACKEND_URL}/api/push/unsubscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ endpoint: subscription.endpoint })
      });
    }

    return true;
  } catch (error) {
    console.error('[Push] Unsubscribe failed:', error);
    return false;
  }
}

/**
 * Save subscription to backend
 */
async function saveSubscriptionToBackend(subscription, userId) {
  try {
    const response = await fetch(`${BACKEND_URL}/api/push/subscribe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        subscription,
        userId: userId || 'guest',
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString()
      })
    });

    if (!response.ok) {
      console.warn('[Push] Failed to save subscription to backend');
    } else {
      console.log('[Push] Subscription saved to backend');
    }
  } catch (error) {
    console.error('[Push] Error saving subscription:', error);
  }
}

/**
 * Send a test notification (for testing purposes)
 */
export async function sendTestNotification() {
  if (Notification.permission !== 'granted') {
    console.log('[Push] Permission not granted');
    return;
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    
    await registration.showNotification('Aditya Retail', {
      body: 'Welcome to Aditya Retail! You will receive updates on orders, offers, and more.',
      icon: '/logo192.png',
      badge: '/logo192.png',
      vibrate: [200, 100, 200],
      tag: 'welcome-notification',
      data: {
        url: '/',
        timestamp: Date.now()
      },
      actions: [
        {
          action: 'explore',
          title: 'Explore Products'
        },
        {
          action: 'close',
          title: 'Close'
        }
      ]
    });

    console.log('[Push] Test notification sent');
  } catch (error) {
    console.error('[Push] Error sending test notification:', error);
  }
}

/**
 * Helper function to convert VAPID key
 */
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

/**
 * Request notification permission and subscribe in one step
 */
export async function setupPushNotifications(userId) {
  const supported = isPushNotificationSupported();
  if (!supported) {
    return { success: false, reason: 'not_supported' };
  }

  const permission = await requestNotificationPermission();
  if (!permission) {
    return { success: false, reason: 'permission_denied' };
  }

  const subscription = await subscribeToPush(userId);
  if (!subscription) {
    return { success: false, reason: 'subscription_failed' };
  }

  // Send test notification
  await sendTestNotification();

  return { success: true, subscription };
}
