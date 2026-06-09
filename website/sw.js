const CACHE_NAME = 'yuksak-cache-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/style.css',
  '/main.js',
  '/manifest.json',
  '/assets/yuksak_logo_192.png',
  '/assets/yuksak_logo_512.png'
];

// Install Service Worker and cache essential static shell assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[PWA ServiceWorker] Caching essential cyber-deck resources...');
        return cache.addAll(ASSETS_TO_CACHE);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate Service Worker and clean up older caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            console.log('[PWA ServiceWorker] Removing legacy cache:', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch events: intercept and serve from cache if available, falling back to network
self.addEventListener('fetch', event => {
  // Do not intercept admin panel or API POST routes
  if (event.request.url.includes('/admin') || 
      event.request.url.includes('/grant_access') || 
      event.request.url.includes('/reject_payment') ||
      event.request.url.includes('/fake_payment')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        if (cachedResponse) {
          // Return cached version immediately
          return cachedResponse;
        }
        // Fallback to fetch from the web server
        return fetch(event.request).then(networkResponse => {
          // If response is valid, cache a clone for subsequent requests
          if (networkResponse.status === 200 && networkResponse.type === 'basic') {
            const cacheClone = networkResponse.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, cacheClone);
            });
          }
          return networkResponse;
        });
      }).catch(() => {
        // Offline fallback
        if (event.request.mode === 'navigate') {
          return caches.match('/index.html');
        }
      })
  );
});
