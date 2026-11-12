/* eslint-disable no-restricted-globals */
// Service Worker for Aditya Retail PWA
// Version 6 (auto-update) — clients auto-reload once when a new SW takes control after a deploy.
// v5: Bypass HTTP cache for /api/products & /api/categories so admin price
// edits show up immediately on the storefront. Older v3 cached product responses
// with max-age=300 which caused stale prices for up to 5 min after edits.
//
// Cache strategy:
// - HTML (navigation requests): NETWORK-FIRST → always fetch latest index.html so JS chunk
//   references stay valid after a new deploy. Fall back to cache only when offline.
// - Hashed assets (static/js, static/css, images): CACHE-FIRST → fast offline reload
// - API: NETWORK-FIRST with cache fallback; /products & /categories bypass HTTP cache entirely

const CACHE_VERSION = 'v6';
const STATIC_CACHE = `aditya-retail-static-${CACHE_VERSION}`;
const API_CACHE = `aditya-retail-api-${CACHE_VERSION}`;

const STATIC_ASSETS = [
  '/manifest.json',
  '/logo192.png',
  '/logo512.png'
];

// Install — pre-cache only stable assets (NOT index.html — that must always be fresh)
self.addEventListener('install', (event) => {
  console.log('[SW] Installing v4 (no-cache for /products & /categories)...');
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll(STATIC_ASSETS.map(url => new Request(url, { cache: 'reload' })))
        .catch((e) => console.warn('[SW] Pre-cache failed (continuing):', e));
    })
  );
  self.skipWaiting();
});

// Activate — wipe every cache that isn't on the current version
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating v4, clearing old caches...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== STATIC_CACHE && name !== API_CACHE) {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          }
          return null;
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch dispatcher
self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Bail on non-GET requests
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  // Skip cross-origin
  if (url.origin !== self.location.origin) return;

  // API → network-first
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request, API_CACHE));
    return;
  }

  // Navigation (HTML pages) → ALWAYS network-first (fixes blank-screen after deploy)
  if (request.mode === 'navigate' || request.destination === 'document') {
    event.respondWith(networkFirstHTML(request));
    return;
  }

  // JS/CSS → network-first (avoids serving stale bundle.js during development,
  // where filenames don't change between builds like they do in production)
  if (request.destination === 'script' || request.destination === 'style') {
    event.respondWith(networkFirst(request, STATIC_CACHE));
    return;
  }

  // Other static assets (images, fonts, etc.) → cache-first is still fine
  event.respondWith(cacheFirst(request, STATIC_CACHE));
});
// Network-first for HTML — fresh index.html every time, cache only as offline fallback
async function networkFirstHTML(request) {
  try {
    const fresh = await fetch(request, { cache: 'no-store' });
    if (fresh && fresh.status === 200) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, fresh.clone()).catch(() => {});
    }
    return fresh;
  } catch (e) {
    console.log('[SW] HTML network fetch failed, trying cache:', e);
    const cached = await caches.match(request);
    if (cached) return cached;
    // Last resort — try the root document
    const rootCached = await caches.match('/');
    if (rootCached) return rootCached;
    return new Response('<h1>Offline</h1><p>Please check your connection.</p>', {
      status: 503,
      headers: { 'Content-Type': 'text/html' }
    });
  }
}

// Cache-first for hashed static assets
async function cacheFirst(request, cacheName) {
  try {
    const cached = await caches.match(request);
    if (cached) return cached;

    const fresh = await fetch(request);
    if (fresh && fresh.status === 200) {
      const cache = await caches.open(cacheName);
      cache.put(request, fresh.clone()).catch(() => {});
    }
    return fresh;
  } catch (e) {
    if (request.destination === 'document') {
      const fallback = await caches.match('/');
      if (fallback) return fallback;
    }
    return new Response('Offline', { status: 503, statusText: 'Service Unavailable' });
  }
}

// Network-first for API
async function networkFirst(request, cacheName) {
  try {
    // For admin-editable catalogue endpoints, bypass browser HTTP cache so
    // freshly saved prices are visible immediately (no stale cache window).
    const url = new URL(request.url);
    const bypassHttpCache = /\/api\/(products|categories|invoices|document-numbering|leads|mail-leads|quotations)/.test(url.pathname);
    const fresh = await fetch(request, bypassHttpCache ? { cache: 'no-store' } : undefined);
    if (fresh && fresh.status === 200 && !bypassHttpCache) {
      const cache = await caches.open(cacheName);
      cache.put(request, fresh.clone()).catch(() => {});
    }
    return fresh;
  } catch (e) {
    const cached = await caches.match(request);
    if (cached) return cached;
    return new Response(JSON.stringify({ error: 'Network unavailable', offline: true }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Background sync (existing)
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-orders' || event.tag === 'sync-cart') {
    event.waitUntil(Promise.resolve());
  }
});

// Push notifications
self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || 'Aditya Retail';
  const options = {
    body: data.body || 'You have a new notification',
    icon: '/logo192.png',
    badge: '/logo192.png',
    vibrate: [200, 100, 200],
    data: data.data || {},
    actions: data.actions || []
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url === '/' && 'focus' in client) return client.focus();
      }
      if (self.clients.openWindow) {
        const urlToOpen = event.notification.data?.url || '/';
        return self.clients.openWindow(urlToOpen);
      }
    })
  );
});

// Message handler — supports forced cache clear from app
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then((names) => Promise.all(names.map((n) => caches.delete(n))))
    );
  }
});

console.log('[SW v4] Loaded — no-cache for /api/products & /api/categories');
