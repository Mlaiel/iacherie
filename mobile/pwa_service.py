"""Progressive Web App (PWA) Service
Production-ready PWA service for mobile-optimized web experience with offline capabilities,
push notifications, and native app-like features.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ STRICT COPYRIGHT NOTICE ⚠️
This code is proprietary and confidential to Fahed Mlaiel.
Any unauthorized use, copying, modification, or distribution
without explicit written permission is strictly prohibited.
Violations will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field
import aiofiles

# Internal imports
try:
    from core.config import get_settings
    from core.logging import get_logger
    from mobile.push_notifications import MobilePushService
except ImportError:
    # Fallback for standalone operation
    def get_logger(name: str):
        return logging.getLogger(name)
    
    def get_settings():
        return {"pwa_enabled": True}

logger = get_logger(__name__)


class PWAFeature(Enum):
    """PWA feature capabilities."""

    OFFLINE_SUPPORT = "offline_support"
    PUSH_NOTIFICATIONS = "push_notifications"
    BACKGROUND_SYNC = "background_sync"
    ADD_TO_HOMESCREEN = "add_to_homescreen"
    CAMERA_ACCESS = "camera_access"
    MICROPHONE_ACCESS = "microphone_access"
    FILE_SYSTEM_ACCESS = "file_system_access"
    GEOLOCATION = "geolocation"
    DEVICE_ORIENTATION = "device_orientation"
    PAYMENT_REQUEST = "payment_request"


class PWAInstallPrompt(Enum):
    """PWA installation prompt types."""

    AUTOMATIC = "automatic"
    MANUAL = "manual"
    AFTER_ENGAGEMENT = "after_engagement"
    CONTEXTUAL = "contextual"


@dataclass
class PWAConfiguration:
    """PWA configuration settings."""
    app_name: str
    short_name: str
    description: str
    theme_color: str
    background_color: str
    display_mode: str  # standalone, fullscreen, minimal-ui
    orientation: str  # portrait, landscape, any
    start_url: str
    scope: str
    icons: List[Dict[str, str]]
    features: List[PWAFeature]
    offline_pages: List[str]
    cache_strategies: Dict[str, str]


@dataclass
class PWAInstallData:
    """
PWA installation tracking data."""
    user_id: str
    session_id: str
    device_info: Dict[str, Any]
    install_timestamp: datetime
    install_source: str  # organic, prompt, banner
    user_agent: str
    platform: str
    is_installed: bool


class MobilePWAService:
    """
    Production-ready Progressive Web App service.
    
    Features:
    - Complete PWA manifest generation
    - Service worker management
    - Offline-first architecture
    - Push notification integration
    - App-like mobile experience
    - Installation tracking and optimization
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger(__name__)
        self.install_tracking: Dict[str, PWAInstallData] = {}
        self.offline_cache: Dict[str, Any] = {}
        
        # Initialize PWA configuration
        self.pwa_config = self._create_default_pwa_config()
        
        # Initialize push service
        try:
            self.push_service = MobilePushService()
        except:
            self.push_service = None
    
    def _create_default_pwa_config(self) -> PWAConfiguration:
        """
Create default PWA configuration."""
        return PWAConfiguration(
            app_name="Ainflue - AI Content Protection",
            short_name="Ainflue",
            description="AI-powered content protection and monetization platform for creators",
            theme_color="#1a1a2e",
            background_color="#16213e",
            display_mode="standalone",
            orientation="any",
            start_url="/",
            scope="/",
            icons=[
                {
                    "src": "/static/icons/icon-72x72.png",
                    "sizes": "72x72",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/static/icons/icon-96x96.png",
                    "sizes": "96x96",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/static/icons/icon-128x128.png",
                    "sizes": "128x128",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/static/icons/icon-144x144.png",
                    "sizes": "144x144",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/static/icons/icon-152x152.png",
                    "sizes": "152x152",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/static/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/static/icons/icon-384x384.png",
                    "sizes": "384x384",
                    "type": "image/png",
                    "purpose": "any"
                },
                {
                    "src": "/static/icons/icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "maskable any"
                }
            ],
            features=[
                PWAFeature.OFFLINE_SUPPORT,
                PWAFeature.PUSH_NOTIFICATIONS,
                PWAFeature.BACKGROUND_SYNC,
                PWAFeature.ADD_TO_HOMESCREEN,
                PWAFeature.CAMERA_ACCESS,
                PWAFeature.MICROPHONE_ACCESS,
                PWAFeature.FILE_SYSTEM_ACCESS
            ],
            offline_pages=[
                "/",
                "/dashboard",
                "/upload",
                "/analytics",
                "/collaboration"
            ],
            cache_strategies={
                "api": "cache_first",
                "static": "cache_first",
                "images": "cache_first",
                "audio": "network_first",
                "video": "network_first"
            }
        )
    
    async def generate_pwa_manifest(
        self,
        user_customizations: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate PWA manifest.json file.
        
        Args:
            user_customizations: Optional user-specific customizations
            
        Returns:
            PWA manifest dictionary
        """
        config = self.pwa_config
        
        # Apply user customizations if provided
        if user_customizations:
            if "theme_color" in user_customizations:
                config.theme_color = user_customizations["theme_color"]
            if "background_color" in user_customizations:
                config.background_color = user_customizations["background_color"]
        
        manifest = {
            "name": config.app_name,
            "short_name": config.short_name,
            "description": config.description,
            "start_url": config.start_url,
            "scope": config.scope,
            "display": config.display_mode,
            "orientation": config.orientation,
            "theme_color": config.theme_color,
            "background_color": config.background_color,
            "icons": config.icons,
            "categories": [
                "music",
                "entertainment",
                "productivity",
                "business",
                "social"
            ],
            "lang": "en",
            "dir": "ltr",
            "prefer_related_applications": False,
            "shortcuts": [
                {
                    "name": "Upload Content",
                    "short_name": "Upload",
                    "description": "Upload new content for protection",
                    "url": "/upload",
                    "icons": [
                        {
                            "src": "/static/icons/upload-96x96.png",
                            "sizes": "96x96"
                        }
                    ]
                },
                {
                    "name": "Analytics Dashboard",
                    "short_name": "Analytics",
                    "description": "View content performance analytics",
                    "url": "/analytics",
                    "icons": [
                        {
                            "src": "/static/icons/analytics-96x96.png",
                            "sizes": "96x96"
                        }
                    ]
                },
                {
                    "name": "Collaboration Hub",
                    "short_name": "Collaborate",
                    "description": "Find and manage collaborations",
                    "url": "/collaboration",
                    "icons": [
                        {
                            "src": "/static/icons/collaborate-96x96.png",
                            "sizes": "96x96"
                        }
                    ]
                },
                {
                    "name": "Revenue Tracking",
                    "short_name": "Revenue",
                    "description": "Track earnings and payouts",
                    "url": "/revenue",
                    "icons": [
                        {
                            "src": "/static/icons/revenue-96x96.png",
                            "sizes": "96x96"
                        }
                    ]
                }
            ],
            "related_applications": [],
            "edge_side_panel": {
                "preferred_width": 350
            },
            "handle_links": "preferred",
            "launch_handler": {
                "client_mode": "navigate-existing"
            }
        }
        
        return manifest
    
    async def generate_service_worker(self) -> str:
        """
        Generate service worker JavaScript code.
        
        Returns:
            Service worker JavaScript code
        """
        config = self.pwa_config
        
        service_worker_code = f"""// Ainflue PWA Service Worker
// Auto-generated by MobilePWAService
// Author: Fahed Mlaiel <mlaiel@live.de>

const CACHE_NAME = 'ainflue-v1.0.0';
const CACHE_URLS = {json.dumps(config.offline_pages)};

// Static assets to cache
const STATIC_CACHE_URLS = [
    '/',
    '/static/css/main.css',
    '/static/js/main.js',
    '/static/js/pwa.js',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png',
    '/manifest.json'
];

// Install event - cache static resources
self.addEventListener('install', (event) => {{
    console.log('PWA Service Worker installing...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {{
                console.log('PWA Cache opened');
                return cache.addAll([...CACHE_URLS, ...STATIC_CACHE_URLS]);
            }})
            .then(() => {{
                console.log('PWA Static resources cached');
                return self.skipWaiting();
            }})
    );
}});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {{
    console.log('PWA Service Worker activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {{
                return Promise.all(
                    cacheNames.map((cacheName) => {{
                        if (cacheName !== CACHE_NAME) {{
                            console.log('PWA Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }}
                    }})
                );
            }})
            .then(() => {{
                console.log('PWA Service Worker activated');
                return self.clients.claim();
            }})
    );
}});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {{
    const url = new URL(event.request.url);
    
    // Skip non-GET requests
    if (event.request.method !== 'GET') {{
        return;
    }}
    
    // Handle API requests
    if (url.pathname.startsWith('/api/')) {{
        event.respondWith(handleApiRequest(event.request));
        return;
    }}
    
    // Handle static assets
    if (url.pathname.startsWith('/static/')) {{
        event.respondWith(handleStaticRequest(event.request));
        return;
    }}
    
    // Handle audio/video content
    if (url.pathname.match(/\\.(mp3|wav|mp4|webm|ogg)$/)) {{
        event.respondWith(handleMediaRequest(event.request));
        return;
    }}
    
    // Handle page requests
    event.respondWith(handlePageRequest(event.request));
}});

// Cache-first strategy for API requests
async function handleApiRequest(request) {{
    try {{
        const cache = await caches.open(CACHE_NAME);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {{
            // Return cached version and update in background
            fetchAndCache(request, cache);
            return cachedResponse;
        }}
        
        // Fetch from network and cache
        const response = await fetch(request);
        if (response.ok) {{
            cache.put(request, response.clone());
        }}
        return response;
        
    }} catch (error) {{
        console.error('PWA API request failed:', error);
        return new Response(
            JSON.stringify({{ error: 'Offline - request failed' }}),
            {{ headers: {{ 'Content-Type': 'application/json' }} }}
        );
    }}
}}

// Cache-first strategy for static assets
async function handleStaticRequest(request) {{
    try {{
        const cache = await caches.open(CACHE_NAME);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {{
            return cachedResponse;
        }}
        
        const response = await fetch(request);
        if (response.ok) {{
            cache.put(request, response.clone());
        }}
        return response;
        
    }} catch (error) {{
        console.error('PWA Static request failed:', error);
        return new Response('Offline', {{ status: 503 }});
    }}
}}

// Network-first strategy for media content
async function handleMediaRequest(request) {{
    try {{
        const response = await fetch(request);
        
        if (response.ok) {{
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, response.clone());
        }}
        
        return response;
        
    }} catch (error) {{
        const cache = await caches.open(CACHE_NAME);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {{
            return cachedResponse;
        }}
        
        return new Response('Media offline', {{ status: 503 }});
    }}
}}

// Stale-while-revalidate for page requests
async function handlePageRequest(request) {{
    try {{
        const cache = await caches.open(CACHE_NAME);
        const cachedResponse = await cache.match(request);
        
        const fetchPromise = fetch(request).then((response) => {{
            if (response.ok) {{
                cache.put(request, response.clone());
            }}
            return response;
        }});
        
        return cachedResponse || fetchPromise;
        
    }} catch (error) {{
        const cache = await caches.open(CACHE_NAME);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {{
            return cachedResponse;
        }}
        
        // Return offline page
        return cache.match('/offline.html') || new Response('Offline', {{ status: 503 }});
    }}
}}

// Background fetch and cache
async function fetchAndCache(request, cache) {{
    try {{
        const response = await fetch(request);
        if (response.ok) {{
            cache.put(request, response.clone());
        }}
    }} catch (error) {{
        console.log('PWA Background fetch failed:', error);
    }}
}}

// Background sync event
self.addEventListener('sync', (event) => {{
    console.log('PWA Background sync triggered:', event.tag);
    
    if (event.tag === 'content-upload') {{
        event.waitUntil(syncContentUploads());
    }}
    
    if (event.tag === 'analytics-data') {{
        event.waitUntil(syncAnalyticsData());
    }}
}});

// Sync pending content uploads
async function syncContentUploads() {{
    try {{
        // Get pending uploads from IndexedDB
        const pendingUploads = await getPendingUploads();
        
        for (const upload of pendingUploads) {{
            try {{
                const response = await fetch('/api/mobile/upload', {{
                    method: 'POST',
                    body: upload.formData,
                    headers: upload.headers
                }});
                
                if (response.ok) {{
                    await removePendingUpload(upload.id);
                    console.log('PWA Synced upload:', upload.id);
                }}
            }} catch (error) {{
                console.error('PWA Upload sync failed:', upload.id, error);
            }}
        }}
    }} catch (error) {{
        console.error('PWA Content upload sync failed:', error);
    }}
}}

// Sync analytics data
async function syncAnalyticsData() {{
    try {{
        const pendingEvents = await getPendingAnalyticsEvents();
        
        if (pendingEvents.length > 0) {{
            const response = await fetch('/api/mobile/analytics/batch', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ events: pendingEvents }})
            }});
            
            if (response.ok) {{
                await clearPendingAnalyticsEvents();
                console.log('PWA Synced analytics events:', pendingEvents.length);
            }}
        }}
    }} catch (error) {{
        console.error('PWA Analytics sync failed:', error);
    }}
}}

// Push notification event
self.addEventListener('push', (event) => {{
    console.log('PWA Push notification received');
    
    const options = {{
        body: 'You have new updates in Ainflue',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        tag: 'ainflue-notification',
        requireInteraction: true,
        actions: [
            {{
                action: 'view',
                title: 'View',
                icon: '/static/icons/view-action.png'
            }},
            {{
                action: 'dismiss',
                title: 'Dismiss'
            }}
        ]
    }};
    
    if (event.data) {{
        const data = event.data.json();
        options.body = data.message || options.body;
        options.data = data;
    }}
    
    event.waitUntil(
        self.registration.showNotification('Ainflue', options)
    );
}});

// Notification click event
self.addEventListener('notificationclick', (event) => {{
    console.log('PWA Notification clicked:', event.action);
    
    event.notification.close();
    
    if (event.action === 'view') {{
        event.waitUntil(
            clients.openWindow('/')
        );
    }}
}});

// Message event for communication with main thread
self.addEventListener('message', (event) => {{
    console.log('PWA Service Worker message:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {{
        self.skipWaiting();
    }}
}});

// Helper functions for IndexedDB operations
async function getPendingUploads() {{
    // Mock implementation - would use IndexedDB in real scenario
    return [];
}}

async function removePendingUpload(id) {{
    // Mock implementation
    console.log('Removing pending upload:', id);
}}

async function getPendingAnalyticsEvents() {{
    // Mock implementation
    return [];
}}

async function clearPendingAnalyticsEvents() {{
    // Mock implementation
    console.log('Clearing pending analytics events');
}}

console.log('PWA Service Worker loaded successfully');
"""
        
        return service_worker_code
    
    async def track_pwa_install(
        self,
        user_id: str,
        session_id: str,
        device_info: Dict[str, Any],
        install_source: str,
        user_agent: str
    ) -> PWAInstallData:
        """
        Track PWA installation.
        
        Args:
            user_id: User who installed PWA
            session_id: Session during installation
            device_info: Device information
            install_source: Source of installation
            user_agent: Browser user agent
            
        Returns:
            PWA installation tracking data
        """
        install_data = PWAInstallData(
            user_id=user_id,
            session_id=session_id,
            device_info=device_info,
            install_timestamp=datetime.now(),
            install_source=install_source,
            user_agent=user_agent,
            platform=device_info.get("platform", "unknown"),
            is_installed=True
        )
        
        self.install_tracking[user_id] = install_data
        
        self.logger.info(
            f"PWA installation tracked for user: {user_id}, "
            f"platform: {install_data.platform}, source: {install_source}"
        )
        
        return install_data
    
    async def get_pwa_install_analytics(self) -> Dict[str, Any]:
        """
        Get PWA installation analytics.
        
        Returns:
            PWA installation analytics data
        """
        installs = list(self.install_tracking.values())
        
        if not installs:
            return {
                "total_installs": 0,
                "platform_breakdown": {},
                "source_breakdown": {},
                "recent_installs": []
            }
        
        # Platform breakdown
        platform_counts = {}
        for install in installs:
            platform = install.platform
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        # Source breakdown
        source_counts = {}
        for install in installs:
            source = install.install_source
            source_counts[source] = source_counts.get(source, 0) + 1
        
        # Recent installs (last 7 days)
        recent_cutoff = datetime.now() - timedelta(days=7)
        recent_installs = [
            {
                "user_id": install.user_id,
                "platform": install.platform,
                "timestamp": install.install_timestamp.isoformat(),
                "source": install.install_source
            }
            for install in installs
            if install.install_timestamp >= recent_cutoff
        ]
        
        return {
            "total_installs": len(installs),
            "platform_breakdown": platform_counts,
            "source_breakdown": source_counts,
            "recent_installs": recent_installs,
            "install_rate": len(recent_installs) / 7 if recent_installs else 0
        }
    
    async def optimize_pwa_for_mobile(
        self,
        device_capabilities: Dict[str, bool],
        network_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize PWA configuration for specific mobile device.
        
        Args:
            device_capabilities: Device capability information
            network_info: Network connection information
            
        Returns:
            Optimized PWA configuration
        """
        optimizations = {
            "cache_strategy": "cache_first",
            "preload_resources": [],
            "lazy_load_images": True,
            "compress_assets": True,
            "offline_features": []
        }
        
        # Optimize based on network connection
        connection_type = network_info.get("type", "unknown")
        
        if connection_type in ["2g", "slow-2g"]:
            optimizations.update({
                "cache_strategy": "cache_only",
                "compress_assets": True,
                "lazy_load_images": True,
                "preload_resources": ["/", "/dashboard"]  # Minimal preloading
            })
        elif connection_type in ["3g"]:
            optimizations.update({
                "cache_strategy": "cache_first",
                "preload_resources": ["/", "/dashboard", "/upload", "/analytics"]
            })
        else:  # 4g, 5g, wifi
            optimizations.update({
                "cache_strategy": "stale_while_revalidate",
                "preload_resources": self.pwa_config.offline_pages
            })
        
        # Optimize based on device capabilities
        if device_capabilities.get("camera", False):
            optimizations["offline_features"].append("camera_upload")
        
        if device_capabilities.get("microphone", False):
            optimizations["offline_features"].append("audio_recording")
        
        if device_capabilities.get("background_sync", False):
            optimizations["offline_features"].append("background_sync")
        
        return optimizations
    
    async def generate_offline_page(self) -> str:
        """
        Generate offline page HTML.
        
        Returns:
            Offline page HTML content
        """
        offline_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ainflue - Offline</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            text-align: center;
        }
        
        .offline-container {
            max-width: 400px;
            padding: 2rem;
        }
        
        .offline-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            opacity: 0.7;
        }
        
        .offline-title {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #64b5f6;
        }
        
        .offline-message {
            font-size: 1rem;
            line-height: 1.5;
            margin-bottom: 2rem;
            opacity: 0.8;
        }
        
        .retry-button {
            background: linear-gradient(45deg, #64b5f6, #42a5f5);
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            color: white;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .retry-button:hover {
            transform: translateY(-2px);
        }
        
        .features-list {
            margin-top: 2rem;
            text-align: left;
        }
        
        .features-list h3 {
            color: #64b5f6;
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
        }
        
        .features-list ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .features-list li {
            padding: 0.25rem 0;
            opacity: 0.8;
        }
        
        .features-list li:before {
            content: "✓ ";
            color: #4caf50;
            font-weight: bold;
            margin-right: 0.5rem;
        }
    </style>
</head>
<body>
    <div class="offline-container">
        <div class="offline-icon">📱</div>
        
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
"""
        
        return offline_html
    
    def get_pwa_configuration(self) -> PWAConfiguration:
        """
Get current PWA configuration."""
        return self.pwa_config
    
    async def update_pwa_configuration(
        self,
        updates: Dict[str, Any]
    ) -> PWAConfiguration:
        """
        Update PWA configuration.
        
        Args:
            updates: Configuration updates to apply
            
        Returns:
            Updated PWA configuration
        """
        if "app_name" in updates:
            self.pwa_config.app_name = updates["app_name"]
        
        if "theme_color" in updates:
            self.pwa_config.theme_color = updates["theme_color"]
        
        if "background_color" in updates:
            self.pwa_config.background_color = updates["background_color"]
        
        if "features" in updates:
            self.pwa_config.features = [
                PWAFeature(f) for f in updates["features"]
            ]
        
        self.logger.info("PWA configuration updated")
        return self.pwa_config


# Mobile PWA service instance
mobile_pwa = MobilePWAService()