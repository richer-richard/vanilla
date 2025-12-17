/**
 * VANILLA Collection Service Worker
 * 
 * Provides offline support for the game collection.
 * Uses a cache-first strategy for static assets and games,
 * with network-first for API calls.
 */

const CACHE_VERSION = 'v2';
const CACHE_NAME = `vanilla-${CACHE_VERSION}`;
const STATIC_CACHE = `vanilla-static-${CACHE_VERSION}`;
const DYNAMIC_CACHE = `vanilla-dynamic-${CACHE_VERSION}`;

// Static assets to cache immediately on install
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/games.html',
    '/about.html',
    '/styles.css',
    '/game-common.css',
    '/sounds.js',
    '/scoreboard.js',
    '/engine.js',
    '/favicon.svg',
    '/manifest.json',
    // Game intro pages
    '/snake/intro.html',
    '/pong/intro.html',
    '/breakout/intro.html',
    '/tetris/intro.html',
    '/minesweeper/intro.html',
    '/space_shooters/intro.html',
    '/geometry_dash/intro.html',
    '/flappy/intro.html',
    '/pacman/intro.html',
    '/asteroids/intro.html',
    // Game pages
    '/snake/game.html',
    '/pong/game.html',
    '/breakout/game.html',
    '/tetris/game.html',
    '/minesweeper/game.html',
    '/space_shooters/game.html',
    '/geometry_dash/game.html',
    '/flappy/game.html',
    '/pacman/game.html',
    '/asteroids/game.html'
];

// External resources to cache
const EXTERNAL_ASSETS = [
    'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&family=Press+Start+2P&display=swap'
];

/**
 * Install event - cache static assets
 */
self.addEventListener('install', (event) => {
    console.log('[SW] Installing service worker...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('[SW] Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                // Cache external assets separately (may fail due to CORS)
                return caches.open(DYNAMIC_CACHE)
                    .then((cache) => {
                        return Promise.allSettled(
                            EXTERNAL_ASSETS.map(url => 
                                cache.add(url).catch(err => 
                                    console.warn(`[SW] Failed to cache ${url}:`, err)
                                )
                            )
                        );
                    });
            })
            .then(() => self.skipWaiting())
    );
});

/**
 * Activate event - clean up old caches
 */
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating service worker...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames
                        .filter((name) => {
                            // Remove old versioned caches
                            return name.startsWith('vanilla-') && 
                                   name !== STATIC_CACHE && 
                                   name !== DYNAMIC_CACHE;
                        })
                        .map((name) => {
                            console.log('[SW] Deleting old cache:', name);
                            return caches.delete(name);
                        })
                );
            })
            .then(() => self.clients.claim())
    );
});

/**
 * Fetch event - serve from cache with network fallback
 */
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip Chrome extension requests
    if (url.protocol === 'chrome-extension:') {
        return;
    }
    
    // API calls - network first with cache fallback
    if (url.pathname.startsWith('/api/') || 
        url.pathname === '/health' ||
        url.pathname === '/scores' ||
        url.pathname === '/score' ||
        url.pathname.startsWith('/leaderboard/')) {
        event.respondWith(networkFirst(request));
        return;
    }

    // HTML pages - network first to avoid stale cached UI
    if (request.mode === 'navigate' || request.headers.get('accept')?.includes('text/html')) {
        event.respondWith(networkFirst(request));
        return;
    }
    
    // Static assets - cache first
    event.respondWith(cacheFirst(request));
});

/**
 * Cache-first strategy
 * Try cache, fall back to network, cache the result
 */
async function cacheFirst(request) {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
        // Return cached response, but also update cache in background
        updateCache(request);
        return cachedResponse;
    }
    
    return fetchAndCache(request);
}

/**
 * Network-first strategy
 * Try network, fall back to cache
 */
async function networkFirst(request) {
    try {
        const networkResponse = await fetch(request);
        
        // Cache successful responses
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('[SW] Network failed, trying cache:', request.url);
        
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline fallback for HTML requests
        if (request.headers.get('accept')?.includes('text/html')) {
            return caches.match('/index.html');
        }
        
        // Return empty JSON for API requests
        if (request.headers.get('accept')?.includes('application/json')) {
            return new Response(
                JSON.stringify({ error: 'offline', message: 'You are currently offline' }),
                { 
                    status: 503,
                    headers: { 'Content-Type': 'application/json' }
                }
            );
        }
        
        throw error;
    }
}

/**
 * Fetch from network and cache the response
 */
async function fetchAndCache(request) {
    try {
        const networkResponse = await fetch(request);
        
        // Only cache successful responses
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.error('[SW] Fetch failed:', request.url, error);
        
        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
            const offlineResponse = await caches.match('/index.html');
            if (offlineResponse) {
                return offlineResponse;
            }
        }
        
        throw error;
    }
}

/**
 * Update cache in background
 */
async function updateCache(request) {
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse);
        }
    } catch (error) {
        // Silent fail - we already have a cached version
    }
}

/**
 * Handle messages from clients
 */
self.addEventListener('message', (event) => {
    if (event.data === 'skipWaiting') {
        self.skipWaiting();
    }
    
    if (event.data === 'clearCache') {
        event.waitUntil(
            caches.keys().then((names) => {
                return Promise.all(names.map(name => caches.delete(name)));
            })
        );
    }
});

/**
 * Background sync for score submissions
 */
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-scores') {
        event.waitUntil(syncScores());
    }
});

/**
 * Sync pending scores when back online
 */
async function syncScores() {
    // Get pending scores from IndexedDB or localStorage proxy
    // This would need to be implemented with a proper offline storage solution
    console.log('[SW] Syncing scores...');
}

/**
 * Push notification handler (for future use)
 */
self.addEventListener('push', (event) => {
    if (!event.data) return;
    
    const data = event.data.json();
    
    event.waitUntil(
        self.registration.showNotification(data.title || 'VANILLA', {
            body: data.body || 'New game update available!',
            icon: '/favicon.svg',
            badge: '/favicon.svg',
            tag: 'vanilla-notification'
        })
    );
});

/**
 * Notification click handler
 */
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    
    event.waitUntil(
        clients.openWindow('/')
    );
});
