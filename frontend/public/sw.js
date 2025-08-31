/**
 * Ainflue PWA Service Worker
 * 
 * Offline-first Progressive Web App with intelligent caching,
 * background sync, and push notification support.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

const CACHE_NAME = 'ainflue-pwa-v1.0.0';
const STATIC_CACHE = 'ainflue-static-v1.0.0';
const DYNAMIC_CACHE = 'ainflue-dynamic-v1.0.0';

// Resources to cache immediately
const STATIC_ASSETS = [
  '/',
  '/upload',
  '/studio',
  '/analytics',
  '/profile',
  '/offline',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
  // Add critical CSS and JS files
  '/_next/static/css/',
  '/_next/static/js/',
];

// API endpoints that should be cached
const API_ENDPOINTS = [
  '/api/user/profile',
  '/api/content/list',
  '/api/analytics/summary',
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('🔧 PWA Service Worker installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('📦 Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('✅ PWA Service Worker installed');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('❌ PWA install failed:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('🚀 PWA Service Worker activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && 
                cacheName !== DYNAMIC_CACHE && 
                cacheName !== CACHE_NAME) {
              console.log('🗑️ Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('✅ PWA Service Worker activated');
        return self.clients.claim();
      })
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Handle API requests with network-first strategy
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstStrategy(request));
    return;
  }

  // Handle navigation requests
  if (request.mode === 'navigate') {
    event.respondWith(navigationHandler(request));
    return;
  }

  // Handle static assets with cache-first strategy
  if (request.destination === 'image' || 
      request.destination === 'style' || 
      request.destination === 'script') {
    event.respondWith(cacheFirstStrategy(request));
    return;
  }

  // Default strategy for other requests
  event.respondWith(staleWhileRevalidateStrategy(request));
});

// Network-first strategy for API calls
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    
    // Cache successful API responses
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('🌐 Network failed, checking cache for:', request.url);
    
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline fallback for failed API calls
    return new Response(
      JSON.stringify({ 
        error: 'Offline', 
        message: 'Content will sync when connection is restored',
        offline: true 
      }),
      { 
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Cache-first strategy for static assets
async function cacheFirstStrategy(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    const cache = await caches.open(STATIC_CACHE);
    cache.put(request, networkResponse.clone());
    return networkResponse;
  } catch (error) {
    console.error('❌ Failed to fetch asset:', request.url);
    return new Response('Asset not available offline', { status: 404 });
  }
}

// Stale-while-revalidate strategy
async function staleWhileRevalidateStrategy(request) {
  const cache = await caches.open(DYNAMIC_CACHE);
  const cachedResponse = await cache.match(request);
  
  const fetchPromise = fetch(request)
    .then((networkResponse) => {
      cache.put(request, networkResponse.clone());
      return networkResponse;
    })
    .catch(() => cachedResponse);
  
  return cachedResponse || fetchPromise;
}

// Navigation handler with offline fallback
async function navigationHandler(request) {
  try {
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    console.log('🌐 Navigation offline, serving cached page');
    
    // Try to serve cached page
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Serve offline page
    return caches.match('/offline') || new Response(
      generateOfflinePage(),
      { headers: { 'Content-Type': 'text/html' } }
    );
  }
}

// Background sync for uploads
self.addEventListener('sync', (event) => {
  console.log('🔄 PWA Background sync triggered:', event.tag);
  
  if (event.tag === 'content-upload') {
    event.waitUntil(syncContentUploads());
  }
  
  if (event.tag === 'analytics-sync') {
    event.waitUntil(syncAnalyticsData());
  }
});

// Sync pending content uploads
async function syncContentUploads() {
  try {
    console.log('📤 Syncing pending uploads...');
    
    // Get pending uploads from IndexedDB
    const pendingUploads = await getPendingUploads();
    
    for (const upload of pendingUploads) {
      try {
        const response = await fetch('/api/content/upload', {
          method: 'POST',
          body: upload.formData,
          headers: upload.headers
        });
        
        if (response.ok) {
          await removePendingUpload(upload.id);
          console.log('✅ Synced upload:', upload.filename);
          
          // Notify user of successful sync
          self.registration.showNotification('Upload Complete', {
            body: `${upload.filename} has been uploaded and processed`,
            icon: '/icons/icon-192x192.png',
            badge: '/icons/badge-72x72.png',
            tag: 'upload-complete',
            data: { uploadId: upload.id }
          });
        }
      } catch (error) {
        console.error('❌ Upload sync failed:', upload.filename, error);
      }
    }
  } catch (error) {
    console.error('❌ Background sync failed:', error);
  }
}

// Push notification handler
self.addEventListener('push', (event) => {
  console.log('📨 Push notification received');
  
  const options = {
    body: 'You have new content updates',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View Content',
        icon: '/icons/view-action.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icons/close-action.png'
      }
    ]
  };
  
  if (event.data) {
    const pushData = event.data.json();
    options.body = pushData.body || options.body;
    options.data = { ...options.data, ...pushData.data };
  }
  
  event.waitUntil(
    self.registration.showNotification('Ainflue', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  console.log('🔔 Notification clicked:', event.action);
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      self.clients.openWindow('/dashboard')
    );
  } else if (event.action === 'close') {
    // Just close the notification
    return;
  } else {
    // Default action - open the app
    event.waitUntil(
      self.clients.openWindow('/')
    );
  }
});

// Helper functions for IndexedDB operations
async function getPendingUploads() {
  // Implementation would use IndexedDB
  return [];
}

async function removePendingUpload(uploadId) {
  // Implementation would remove from IndexedDB
  console.log('Removing upload:', uploadId);
}

async function syncAnalyticsData() {
  // Implementation would sync analytics data
  console.log('Syncing analytics data...');
}

// Generate offline page HTML
function generateOfflinePage() {
  return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Ainflue - Offline</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
          color: white;
          margin: 0;
          padding: 20px;
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .offline-container {
          text-align: center;
          max-width: 400px;
        }
        .offline-icon {
          font-size: 4rem;
          margin-bottom: 1rem;
        }
        .offline-title {
          font-size: 1.5rem;
          font-weight: bold;
          margin-bottom: 1rem;
          color: #3B82F6;
        }
        .offline-message {
          margin-bottom: 2rem;
          opacity: 0.8;
          line-height: 1.6;
        }
        .retry-button {
          background: #3B82F6;
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 8px;
          font-size: 1rem;
          cursor: pointer;
          margin-bottom: 2rem;
        }
        .features-list {
          text-align: left;
          background: rgba(55, 65, 81, 0.5);
          border-radius: 8px;
          padding: 1rem;
        }
        .features-list h3 {
          margin-top: 0;
          color: #3B82F6;
        }
        .features-list ul {
          list-style: none;
          padding: 0;
        }
        .features-list li {
          padding: 0.25rem 0;
          opacity: 0.8;
        }
        .features-list li:before {
          content: "✓ ";
          color: #10B981;
          font-weight: bold;
        }
      </style>
    </head>
    <body>
      <div class="offline-container">
        <div class="offline-icon">🌐</div>
        <h1 class="offline-title">You're Offline</h1>
        <p class="offline-message">
          Don't worry! Ainflue works offline too. You can still access your content,
          view analytics, and prepare uploads for when you're back online.
        </p>
        
        <button class="retry-button" onclick="window.location.reload()">
          Try Again
        </button>
        
        <div class="features-list">
          <h3>Available Offline:</h3>
          <ul>
            <li>View cached content</li>
            <li>Access analytics dashboard</li>
            <li>Prepare content uploads</li>
            <li>Browse collaboration history</li>
            <li>Manage account settings</li>
          </ul>
        </div>
      </div>
      
      <script>
        // Auto-retry when connection is restored
        window.addEventListener('online', () => {
          setTimeout(() => {
            window.location.reload();
          }, 1000);
        });
        
        // Update UI based on connection status
        function updateConnectionStatus() {
          if (navigator.onLine) {
            document.querySelector('.offline-title').textContent = 'Connection Restored!';
            document.querySelector('.offline-message').textContent = 'Reloading to sync your data...';
            setTimeout(() => window.location.reload(), 2000);
          }
        }
        
        // Check connection status periodically
        setInterval(updateConnectionStatus, 5000);
      </script>
    </body>
    </html>
  `;
}