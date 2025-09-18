"""Mobile Technical SEO
Advanced mobile optimization system for technical SEO and performance.

Features:
- Mobile-first indexing optimization
- Responsive design validation
- Mobile usability testing
- Touch-friendly interface validation
- Mobile page speed optimization
- AMP implementation support
- Progressive Web App (PWA) features
- Creator mobile experience optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Backend Senior + Lead Dev IA expertise applied
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import re
from urllib.parse import urljoin, urlparse
import hashlib

logger = logging.getLogger(__name__)

class DeviceType(Enum):
    """Mobile device types."""
    SMARTPHONE = "smartphone"
    TABLET = "tablet"
    FEATURE_PHONE = "feature_phone"
    FOLDABLE = "foldable"
    DESKTOP = "desktop"

class MobileOptimizationLevel(Enum):
    """Mobile optimization levels."""
    BASIC = "basic"
    ENHANCED = "enhanced"
    PROGRESSIVE = "progressive"
    ENTERPRISE = "enterprise"

class TouchTarget(Enum):
    """Touch target types."""
    BUTTON = "button"
    LINK = "link"
    INPUT = "input"
    NAVIGATION = "navigation"
    CONTENT = "content"

@dataclass
class MobileMetrics:
    """Mobile performance and usability metrics."""
    url: str
    device_type: DeviceType
    timestamp: datetime
    # Performance metrics
    mobile_speed_score: int = 0
    first_contentful_paint_mobile: float = 0.0
    largest_contentful_paint_mobile: float = 0.0
    cumulative_layout_shift_mobile: float = 0.0
    # Usability metrics
    mobile_friendly_score: int = 0
    touch_targets_appropriate: bool = False
    text_readable: bool = False
    content_wider_than_screen: bool = False
    viewport_configured: bool = False
    # Technical metrics
    amp_valid: bool = False
    pwa_features: int = 0
    responsive_breakpoints_working: bool = False
    mobile_redirects: int = 0
    # Creator-specific metrics
    creator_id: Optional[str] = None
    content_type: Optional[str] = None
    mobile_engagement_score: float = 0.0

@dataclass
class TouchTargetAnalysis:
    """Touch target analysis results."""
    target_type: TouchTarget
    element_selector: str
    size_pixels: Tuple[int, int]
    is_appropriate_size: bool
    spacing_adequate: bool
    accessibility_score: int
    recommendations: List[str] = field(default_factory=list)

@dataclass
class ResponsiveDesignAnalysis:
    """Responsive design analysis results."""
    viewport_meta_present: bool
    media_queries_count: int
    breakpoints_detected: List[int]
    flexible_layout: bool
    responsive_images: bool
    responsive_typography: bool
    mobile_navigation: bool
    score: int = 0
    issues: List[str] = field(default_factory=list)

@dataclass
class AMPAnalysis:
    """AMP (Accelerated Mobile Pages) analysis."""
    amp_valid: bool
    amp_version: Optional[str] = None
    amp_components_used: List[str] = field(default_factory=list)
    amp_errors: List[str] = field(default_factory=list)
    amp_warnings: List[str] = field(default_factory=list)
    performance_gains: Dict[str, float] = field(default_factory=dict)

@dataclass
class PWAAnalysis:
    """Progressive Web App analysis."""
    manifest_present: bool
    service_worker_present: bool
    app_shell_cached: bool
    offline_support: bool
    installable: bool
    features_score: int = 0
    recommendations: List[str] = field(default_factory=list)

class MobileTechnicalSEO:
    """
    Enterprise mobile technical SEO optimization system.
    Provides comprehensive mobile optimization for creator economy platform.
    """
    
    def __init__(self, optimization_level: MobileOptimizationLevel = MobileOptimizationLevel.ENHANCED):
        self.optimization_level = optimization_level
        self.mobile_metrics_history: List[MobileMetrics] = []
        self.optimization_cache: Dict[str, Dict[str, Any]] = {}
        
    async def analyze_mobile_performance(self,
                                       url: str,
                                       device_type: DeviceType = DeviceType.SMARTPHONE,
                                       creator_id: Optional[str] = None) -> MobileMetrics:
        """
        Comprehensive mobile performance analysis.
        
        Args:
            url: URL to analyze
            device_type: Type of mobile device
            creator_id: Associated creator ID
            
        Returns:
            Mobile metrics and analysis
        """
        try:
            metrics = MobileMetrics(
                url=url,
                device_type=device_type,
                timestamp=datetime.now(),
                creator_id=creator_id
            )
            
            # Measure mobile performance
            performance_data = await self._measure_mobile_performance(url, device_type)
            metrics.mobile_speed_score = performance_data['speed_score']
            metrics.first_contentful_paint_mobile = performance_data['fcp']
            metrics.largest_contentful_paint_mobile = performance_data['lcp']
            metrics.cumulative_layout_shift_mobile = performance_data['cls']
            
            # Analyze mobile usability
            usability_data = await self._analyze_mobile_usability(url, device_type)
            metrics.mobile_friendly_score = usability_data['mobile_friendly_score']
            metrics.touch_targets_appropriate = usability_data['touch_targets_ok']
            metrics.text_readable = usability_data['text_readable']
            metrics.content_wider_than_screen = usability_data['content_fits']
            metrics.viewport_configured = usability_data['viewport_configured']
            
            # Check technical features
            technical_data = await self._analyze_mobile_technical_features(url)
            metrics.amp_valid = technical_data['amp_valid']
            metrics.pwa_features = technical_data['pwa_features_count']
            metrics.responsive_breakpoints_working = technical_data['responsive_ok']
            metrics.mobile_redirects = technical_data['redirect_count']
            
            # Calculate mobile engagement score for creators
            if creator_id:
                metrics.mobile_engagement_score = await self._calculate_mobile_engagement_score(
                    metrics, creator_id
                )
            
            # Store metrics
            self.mobile_metrics_history.append(metrics)
            
            logger.info(f"Mobile analysis completed for {url}: Score {metrics.mobile_friendly_score}/100")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing mobile performance for {url}: {str(e)}")
            raise
    
    async def optimize_mobile_experience(self,
                                       url: str,
                                       current_metrics: MobileMetrics,
                                       target_device: DeviceType = DeviceType.SMARTPHONE) -> Dict[str, Any]:
        """
        Generate comprehensive mobile optimization recommendations.
        
        Args:
            url: URL to optimize
            current_metrics: Current mobile metrics
            target_device: Primary target device
            
        Returns:
            Mobile optimization plan
        """
        try:
            optimization_plan = {
                'url': url,
                'target_device': target_device.value,
                'current_scores': {
                    'mobile_speed': current_metrics.mobile_speed_score,
                    'mobile_friendly': current_metrics.mobile_friendly_score,
                    'pwa_features': current_metrics.pwa_features
                },
                'optimizations': {
                    'performance': [],
                    'usability': [],
                    'technical': [],
                    'creator_specific': []
                },
                'implementation_priority': [],
                'expected_improvements': {},
                'mobile_seo_enhancements': {}
            }
            
            # Performance optimizations
            if current_metrics.mobile_speed_score < 90:
                performance_optimizations = await self._generate_performance_optimizations(
                    current_metrics, target_device
                )
                optimization_plan['optimizations']['performance'] = performance_optimizations
            
            # Usability optimizations
            if current_metrics.mobile_friendly_score < 95:
                usability_optimizations = await self._generate_usability_optimizations(
                    current_metrics, target_device
                )
                optimization_plan['optimizations']['usability'] = usability_optimizations
            
            # Technical optimizations
            technical_optimizations = await self._generate_technical_optimizations(
                current_metrics, target_device
            )
            optimization_plan['optimizations']['technical'] = technical_optimizations
            
            # Creator-specific optimizations
            if current_metrics.creator_id:
                creator_optimizations = await self._generate_creator_mobile_optimizations(
                    current_metrics, target_device
                )
                optimization_plan['optimizations']['creator_specific'] = creator_optimizations
            
            # Prioritize implementations
            optimization_plan['implementation_priority'] = self._prioritize_mobile_optimizations(
                optimization_plan['optimizations']
            )
            
            # Calculate expected improvements
            optimization_plan['expected_improvements'] = self._calculate_expected_improvements(
                current_metrics, optimization_plan['optimizations']
            )
            
            # Mobile SEO enhancements
            optimization_plan['mobile_seo_enhancements'] = await self._generate_mobile_seo_enhancements(
                url, current_metrics
            )
            
            return optimization_plan
            
        except Exception as e:
            logger.error(f"Error optimizing mobile experience for {url}: {str(e)}")
            raise
    
    async def analyze_touch_targets(self, url: str) -> List[TouchTargetAnalysis]:
        """
        Analyze touch targets for mobile usability.
        
        Args:
            url: URL to analyze
            
        Returns:
            List of touch target analyses
        """
        try:
            # In real implementation, use browser automation to analyze page
            # For now, simulate touch target analysis
            
            touch_targets = []
            
            # Simulate common touch targets
            target_types = [
                (TouchTarget.BUTTON, "button.primary", (48, 48)),
                (TouchTarget.LINK, "a.nav-link", (44, 44)),
                (TouchTarget.INPUT, "input[type='text']", (48, 32)),
                (TouchTarget.NAVIGATION, ".mobile-menu-toggle", (44, 44)),
                (TouchTarget.CONTENT, ".content-card", (120, 80))
            ]
            
            for target_type, selector, size in target_types:
                is_appropriate = size[0] >= 44 and size[1] >= 44  # iOS/Android guidelines
                spacing_adequate = True  # Simulate spacing check
                
                recommendations = []
                if not is_appropriate:
                    recommendations.append(f"Increase touch target size to minimum 44x44px")
                if not spacing_adequate:
                    recommendations.append("Add adequate spacing between touch targets")
                
                accessibility_score = 100 if is_appropriate and spacing_adequate else 60
                
                analysis = TouchTargetAnalysis(
                    target_type=target_type,
                    element_selector=selector,
                    size_pixels=size,
                    is_appropriate_size=is_appropriate,
                    spacing_adequate=spacing_adequate,
                    accessibility_score=accessibility_score,
                    recommendations=recommendations
                )
                
                touch_targets.append(analysis)
            
            return touch_targets
            
        except Exception as e:
            logger.error(f"Error analyzing touch targets for {url}: {str(e)}")
            return []
    
    async def analyze_responsive_design(self, url: str) -> ResponsiveDesignAnalysis:
        """
        Analyze responsive design implementation.
        
        Args:
            url: URL to analyze
            
        Returns:
            Responsive design analysis
        """
        try:
            # Simulate responsive design analysis
            analysis = ResponsiveDesignAnalysis(
                viewport_meta_present=True,
                media_queries_count=5,
                breakpoints_detected=[320, 768, 1024, 1200],
                flexible_layout=True,
                responsive_images=True,
                responsive_typography=True,
                mobile_navigation=True
            )
            
            # Calculate score based on features
            score = 0
            if analysis.viewport_meta_present:
                score += 20
            if analysis.media_queries_count >= 3:
                score += 20
            if len(analysis.breakpoints_detected) >= 3:
                score += 20
            if analysis.flexible_layout:
                score += 15
            if analysis.responsive_images:
                score += 15
            if analysis.mobile_navigation:
                score += 10
            
            analysis.score = score
            
            # Identify issues
            if not analysis.viewport_meta_present:
                analysis.issues.append("Missing viewport meta tag")
            if analysis.media_queries_count < 3:
                analysis.issues.append("Insufficient media queries for responsive design")
            if not analysis.mobile_navigation:
                analysis.issues.append("Mobile navigation needs improvement")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing responsive design for {url}: {str(e)}")
            raise
    
    async def analyze_amp_implementation(self, url: str) -> AMPAnalysis:
        """
        Analyze AMP (Accelerated Mobile Pages) implementation.
        
        Args:
            url: URL to analyze
            
        Returns:
            AMP analysis
        """
        try:
            # Check if AMP version exists
            amp_url = url.replace('://', '://amp.') if '://amp.' not in url else url
            
            # Simulate AMP analysis
            analysis = AMPAnalysis(
                amp_valid=True,
                amp_version="1.0",
                amp_components_used=['amp-img', 'amp-video', 'amp-carousel'],
                amp_errors=[],
                amp_warnings=['Consider using amp-analytics for better tracking'],
                performance_gains={
                    'loading_speed_improvement': 0.65,  # 65% faster
                    'cache_hit_ratio': 0.85,
                    'mobile_experience_score': 95
                }
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing AMP implementation for {url}: {str(e)}")
            return AMPAnalysis(amp_valid=False)
    
    async def analyze_pwa_features(self, url: str) -> PWAAnalysis:
        """
        Analyze Progressive Web App features.
        
        Args:
            url: URL to analyze
            
        Returns:
            PWA analysis
        """
        try:
            # Simulate PWA analysis
            analysis = PWAAnalysis(
                manifest_present=True,
                service_worker_present=True,
                app_shell_cached=True,
                offline_support=True,
                installable=True
            )
            
            # Calculate features score
            features = [
                analysis.manifest_present,
                analysis.service_worker_present,
                analysis.app_shell_cached,
                analysis.offline_support,
                analysis.installable
            ]
            
            analysis.features_score = sum(features) * 20  # 20 points per feature
            
            # Generate recommendations
            if not analysis.manifest_present:
                analysis.recommendations.append("Add Web App Manifest for installability")
            if not analysis.service_worker_present:
                analysis.recommendations.append("Implement Service Worker for offline support")
            if not analysis.offline_support:
                analysis.recommendations.append("Add offline functionality for key features")
            if not analysis.installable:
                analysis.recommendations.append("Ensure PWA meets installability criteria")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing PWA features for {url}: {str(e)}")
            return PWAAnalysis(
                manifest_present=False,
                service_worker_present=False,
                app_shell_cached=False,
                offline_support=False,
                installable=False
            )
    
    async def generate_mobile_optimization_code(self,
                                              optimization_plan: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate implementation code for mobile optimizations.
        
        Args:
            optimization_plan: Mobile optimization plan
            
        Returns:
            Generated code snippets
        """
        try:
            code_snippets = {
                'viewport_meta': '',
                'responsive_css': '',
                'touch_optimization': '',
                'performance_optimizations': '',
                'pwa_manifest': '',
                'service_worker': ''
            }
            
            # Viewport meta tag
            code_snippets['viewport_meta'] = '''<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">'''
            
            # Responsive CSS
            code_snippets['responsive_css'] = '''
/* Mobile-first responsive design */
@media (min-width: 320px) {
    .container { padding: 1rem; }
    .touch-target { min-height: 44px; min-width: 44px; }
}

@media (min-width: 768px) {
    .container { padding: 2rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
}

@media (min-width: 1024px) {
    .container { max-width: 1200px; margin: 0 auto; }
}

/* Touch-friendly interactions */
.touch-target {
    padding: 12px;
    margin: 8px;
    border-radius: 8px;
    transition: transform 0.2s ease;
}

.touch-target:active {
    transform: scale(0.95);
}
'''
            
            # Touch optimization
            code_snippets['touch_optimization'] = '''
/* Touch optimization CSS */
html {
    -webkit-text-size-adjust: 100%;
    -webkit-tap-highlight-color: transparent;
}

button, a, [role="button"] {
    min-height: 44px;
    min-width: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}

/* Improve scrolling performance */
.scroll-container {
    -webkit-overflow-scrolling: touch;
    overflow-scrolling: touch;
}
'''
            
            # Performance optimizations
            code_snippets['performance_optimizations'] = '''
<!-- Resource hints for mobile performance -->
<link rel="dns-prefetch" href="//fonts.googleapis.com">
<link rel="preconnect" href="//api.example.com" crossorigin>
<link rel="preload" as="font" href="/fonts/main.woff2" crossorigin>

<!-- Critical CSS inlined -->
<style>
    /* Critical above-the-fold styles */
    body { font-family: system-ui, -apple-system, sans-serif; }
    .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
</style>

<!-- Non-critical CSS deferred -->
<link rel="preload" href="/css/non-critical.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
'''
            
            # PWA Manifest
            code_snippets['pwa_manifest'] = '''
{
    "name": "Ainflue Creator Platform",
    "short_name": "Ainflue",
    "description": "AI-powered creator economy platform",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#667eea",
    "orientation": "portrait-primary",
    "icons": [
        {
            "src": "/icons/icon-192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "any maskable"
        },
        {
            "src": "/icons/icon-512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ],
    "categories": ["productivity", "social", "entertainment"],
    "shortcuts": [
        {
            "name": "Create Content",
            "short_name": "Create",
            "description": "Create new content",
            "url": "/create",
            "icons": [{"src": "/icons/create-96.png", "sizes": "96x96"}]
        }
    ]
}
'''
            
            # Service Worker
            code_snippets['service_worker'] = '''
// Service Worker for PWA functionality
const CACHE_NAME = 'ainflue-v1';
const urlsToCache = [
    '/',
    '/css/main.css',
    '/js/main.js',
    '/icons/icon-192.png'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            })
    );
});

// Background sync for content upload
self.addEventListener('sync', event => {
    if (event.tag === 'content-upload') {
        event.waitUntil(uploadPendingContent());
    }
});
'''
            
            return code_snippets
            
        except Exception as e:
            logger.error(f"Error generating mobile optimization code: {str(e)}")
            return {}
    
    async def setup_creator_mobile_optimization(self,
                                              creator_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Setup mobile optimization for creator profiles and content.
        
        Args:
            creator_data: List of creator data
            
        Returns:
            Mobile optimization setup results
        """
        try:
            setup_results = {
                'creators_optimized': 0,
                'total_urls_analyzed': 0,
                'optimization_results': [],
                'mobile_performance_summary': {},
                'creator_mobile_features': {},
                'implementation_roadmap': {}
            }
            
            total_mobile_score = 0
            total_speed_score = 0
            
            for creator_info in creator_data:
                creator_id = creator_info.get('id')
                urls = creator_info.get('mobile_urls', [])
                creator_type = creator_info.get('type', 'standard')
                
                if not creator_id or not urls:
                    continue
                
                creator_results = {
                    'creator_id': creator_id,
                    'creator_type': creator_type,
                    'url_analyses': [],
                    'overall_mobile_score': 0,
                    'optimization_plan': {},
                    'mobile_features_enabled': []
                }
                
                # Analyze each URL
                for url_info in urls:
                    url = url_info.get('url')
                    content_type = url_info.get('content_type', 'profile')
                    
                    if not url:
                        continue
                    
                    # Perform mobile analysis
                    metrics = await self.analyze_mobile_performance(
                        url, DeviceType.SMARTPHONE, creator_id
                    )
                    
                    # Generate optimization plan
                    optimization_plan = await self.optimize_mobile_experience(
                        url, metrics, DeviceType.SMARTPHONE
                    )
                    
                    url_analysis = {
                        'url': url,
                        'content_type': content_type,
                        'metrics': metrics,
                        'optimization_plan': optimization_plan,
                        'mobile_seo_score': self._calculate_mobile_seo_score(metrics)
                    }
                    
                    creator_results['url_analyses'].append(url_analysis)
                    total_mobile_score += metrics.mobile_friendly_score
                    total_speed_score += metrics.mobile_speed_score
                
                # Calculate creator overall score
                if creator_results['url_analyses']:
                    creator_results['overall_mobile_score'] = sum(
                        analysis['mobile_seo_score'] for analysis in creator_results['url_analyses']
                    ) / len(creator_results['url_analyses'])
                
                # Generate creator-specific mobile features
                creator_results['mobile_features_enabled'] = await self._enable_creator_mobile_features(
                    creator_id, creator_type, creator_results['url_analyses']
                )
                
                setup_results['optimization_results'].append(creator_results)
                setup_results['creators_optimized'] += 1
                setup_results['total_urls_analyzed'] += len(creator_results['url_analyses'])
            
            # Calculate summary metrics
            if setup_results['total_urls_analyzed'] > 0:
                setup_results['mobile_performance_summary'] = {
                    'average_mobile_friendly_score': total_mobile_score / setup_results['total_urls_analyzed'],
                    'average_mobile_speed_score': total_speed_score / setup_results['total_urls_analyzed'],
                    'creators_needing_optimization': len([
                        r for r in setup_results['optimization_results'] 
                        if r['overall_mobile_score'] < 80
                    ]),
                    'top_performing_creators': sorted(
                        setup_results['optimization_results'],
                        key=lambda x: x['overall_mobile_score'],
                        reverse=True
                    )[:5]
                }
            
            # Generate platform-wide mobile features
            setup_results['creator_mobile_features'] = await self._generate_platform_mobile_features()
            
            # Create implementation roadmap
            setup_results['implementation_roadmap'] = self._create_mobile_implementation_roadmap(
                setup_results['optimization_results']
            )
            
            return setup_results
            
        except Exception as e:
            logger.error(f"Error setting up creator mobile optimization: {str(e)}")
            raise
    
    async def _measure_mobile_performance(self, url: str, device_type: DeviceType) -> Dict[str, Any]:
        """Measure mobile performance metrics."""
        # Simulate mobile performance measurement
        import random
        
        device_factors = {
            DeviceType.SMARTPHONE: 1.8,
            DeviceType.TABLET: 1.3,
            DeviceType.FEATURE_PHONE: 2.5,
            DeviceType.FOLDABLE: 1.5,
            DeviceType.DESKTOP: 1.0
        }
        
        factor = device_factors.get(device_type, 1.8)
        
        return {
            'speed_score': random.randint(45, 95),
            'fcp': round(random.uniform(1.2, 3.5) * factor, 2),
            'lcp': round(random.uniform(2.0, 5.0) * factor, 2),
            'cls': round(random.uniform(0.05, 0.4), 3),
            'tti': round(random.uniform(3.0, 8.0) * factor, 2)
        }
    
    async def _analyze_mobile_usability(self, url: str, device_type: DeviceType) -> Dict[str, Any]:
        """Analyze mobile usability factors."""
        # Simulate mobile usability analysis
        import random
        
        return {
            'mobile_friendly_score': random.randint(70, 100),
            'touch_targets_ok': random.choice([True, False]),
            'text_readable': random.choice([True, False]),
            'content_fits': random.choice([True, False]),
            'viewport_configured': random.choice([True, False]),
            'tap_targets_spaced': random.choice([True, False])
        }
    
    async def _analyze_mobile_technical_features(self, url: str) -> Dict[str, Any]:
        """Analyze mobile technical features."""
        # Simulate technical features analysis
        import random
        
        return {
            'amp_valid': random.choice([True, False]),
            'pwa_features_count': random.randint(0, 5),
            'responsive_ok': random.choice([True, False]),
            'redirect_count': random.randint(0, 3),
            'mobile_sitemap': random.choice([True, False]),
            'structured_data_mobile': random.choice([True, False])
        }
    
    async def _calculate_mobile_engagement_score(self,
                                               metrics: MobileMetrics,
                                               creator_id: str) -> float:
        """Calculate mobile engagement score for creators."""
        base_score = 0.0
        
        # Performance contribution (40%)
        if metrics.mobile_speed_score >= 90:
            base_score += 0.4
        elif metrics.mobile_speed_score >= 70:
            base_score += 0.3
        elif metrics.mobile_speed_score >= 50:
            base_score += 0.2
        
        # Usability contribution (35%)
        usability_factors = [
            metrics.touch_targets_appropriate,
            metrics.text_readable,
            not metrics.content_wider_than_screen,
            metrics.viewport_configured
        ]
        base_score += (sum(usability_factors) / len(usability_factors)) * 0.35
        
        # Modern features contribution (25%)
        modern_features = 0
        if metrics.amp_valid:
            modern_features += 1
        if metrics.pwa_features >= 3:
            modern_features += 1
        if metrics.responsive_breakpoints_working:
            modern_features += 1
        
        base_score += (modern_features / 3) * 0.25
        
        return round(base_score * 100, 1)
    
    async def _generate_performance_optimizations(self,
                                                metrics: MobileMetrics,
                                                target_device: DeviceType) -> List[Dict[str, Any]]:
        """Generate mobile performance optimizations."""
        optimizations = []
        
        if metrics.mobile_speed_score < 70:
            optimizations.append({
                'type': 'critical_resource_optimization',
                'priority': 'high',
                'description': 'Optimize critical resource loading for mobile',
                'implementation': 'Inline critical CSS, defer non-critical JS, optimize images',
                'expected_improvement': 15,
                'creator_impact': 'Faster page loads improve viewer retention'
            })
        
        if metrics.largest_contentful_paint_mobile > 4.0:
            optimizations.append({
                'type': 'lcp_mobile_optimization',
                'priority': 'high',
                'description': 'Optimize Largest Contentful Paint for mobile devices',
                'implementation': 'Preload hero images, optimize server response time',
                'expected_improvement': 20,
                'creator_impact': 'Content appears faster on mobile devices'
            })
        
        if metrics.cumulative_layout_shift_mobile > 0.25:
            optimizations.append({
                'type': 'cls_mobile_reduction',
                'priority': 'medium',
                'description': 'Reduce layout shifts on mobile',
                'implementation': 'Reserve space for dynamic content, specify image dimensions',
                'expected_improvement': 10,
                'creator_impact': 'Smoother mobile viewing experience'
            })
        
        return optimizations
    
    async def _generate_usability_optimizations(self,
                                              metrics: MobileMetrics,
                                              target_device: DeviceType) -> List[Dict[str, Any]]:
        """Generate mobile usability optimizations."""
        optimizations = []
        
        if not metrics.touch_targets_appropriate:
            optimizations.append({
                'type': 'touch_target_sizing',
                'priority': 'high',
                'description': 'Optimize touch target sizes for mobile',
                'implementation': 'Ensure minimum 44px touch targets, adequate spacing',
                'expected_improvement': 25,
                'creator_impact': 'Easier interaction with creator content on mobile'
            })
        
        if not metrics.text_readable:
            optimizations.append({
                'type': 'mobile_typography',
                'priority': 'medium',
                'description': 'Improve text readability on mobile',
                'implementation': 'Increase font sizes, improve contrast, optimize line height',
                'expected_improvement': 15,
                'creator_impact': 'Better content readability increases engagement'
            })
        
        if not metrics.viewport_configured:
            optimizations.append({
                'type': 'viewport_configuration',
                'priority': 'high',
                'description': 'Configure proper viewport settings',
                'implementation': 'Add responsive viewport meta tag',
                'expected_improvement': 20,
                'creator_impact': 'Proper mobile display of creator content'
            })
        
        return optimizations
    
    async def _generate_technical_optimizations(self,
                                              metrics: MobileMetrics,
                                              target_device: DeviceType) -> List[Dict[str, Any]]:
        """Generate mobile technical optimizations."""
        optimizations = []
        
        if not metrics.amp_valid and self.optimization_level in [MobileOptimizationLevel.PROGRESSIVE, MobileOptimizationLevel.ENTERPRISE]:
            optimizations.append({
                'type': 'amp_implementation',
                'priority': 'medium',
                'description': 'Implement AMP for ultra-fast mobile loading',
                'implementation': 'Create AMP versions of key pages',
                'expected_improvement': 40,
                'creator_impact': 'Lightning-fast mobile content loading'
            })
        
        if metrics.pwa_features < 3:
            optimizations.append({
                'type': 'pwa_enhancement',
                'priority': 'medium',
                'description': 'Add Progressive Web App features',
                'implementation': 'Add manifest, service worker, offline support',
                'expected_improvement': 30,
                'creator_impact': 'App-like mobile experience for creators and viewers'
            })
        
        if not metrics.responsive_breakpoints_working:
            optimizations.append({
                'type': 'responsive_design_fix',
                'priority': 'high',
                'description': 'Fix responsive design implementation',
                'implementation': 'Update CSS media queries, flexible layouts',
                'expected_improvement': 25,
                'creator_impact': 'Consistent experience across all mobile devices'
            })
        
        return optimizations
    
    async def _generate_creator_mobile_optimizations(self,
                                                   metrics: MobileMetrics,
                                                   target_device: DeviceType) -> List[Dict[str, Any]]:
        """Generate creator-specific mobile optimizations."""
        optimizations = []
        
        if metrics.creator_id:
            # Creator profile mobile optimization
            optimizations.append({
                'type': 'creator_profile_mobile',
                'priority': 'high',
                'description': 'Optimize creator profile for mobile discovery',
                'implementation': 'Mobile-first profile layout, touch-friendly navigation',
                'expected_improvement': 20,
                'creator_impact': 'Improved mobile profile visibility and engagement'
            })
            
            # Content consumption optimization
            optimizations.append({
                'type': 'mobile_content_consumption',
                'priority': 'medium',
                'description': 'Optimize content consumption on mobile',
                'implementation': 'Swipe gestures, mobile video controls, audio optimization',
                'expected_improvement': 18,
                'creator_impact': 'Better mobile content consumption experience'
            })
            
            # Mobile monetization optimization
            optimizations.append({
                'type': 'mobile_monetization',
                'priority': 'medium',
                'description': 'Optimize monetization features for mobile',
                'implementation': 'Mobile-friendly payment flows, subscription management',
                'expected_improvement': 22,
                'creator_impact': 'Improved mobile revenue potential'
            })
        
        return optimizations
    
    def _prioritize_mobile_optimizations(self, optimizations: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """Prioritize mobile optimizations by impact and effort."""
        all_optimizations = []
        
        for category, opts in optimizations.items():
            for opt in opts:
                priority_score = 0
                
                # Priority weight
                if opt.get('priority') == 'high':
                    priority_score += 10
                elif opt.get('priority') == 'medium':
                    priority_score += 5
                
                # Expected improvement weight
                priority_score += opt.get('expected_improvement', 0) / 5
                
                # Creator impact weight
                if opt.get('creator_impact'):
                    priority_score += 3
                
                all_optimizations.append((opt['type'], priority_score))
        
        # Sort by priority score
        prioritized = sorted(all_optimizations, key=lambda x: x[1], reverse=True)
        return [opt_type for opt_type, _ in prioritized]
    
    def _calculate_expected_improvements(self,
                                       current_metrics: MobileMetrics,
                                       optimizations: Dict[str, List[Dict[str, Any]]]) -> Dict[str, float]:
        """Calculate expected improvements from optimizations."""
        improvements = {
            'mobile_speed_score': 0,
            'mobile_friendly_score': 0,
            'engagement_score': 0,
            'seo_score': 0
        }
        
        for category, opts in optimizations.items():
            for opt in opts:
                improvement = opt.get('expected_improvement', 0)
                
                if 'performance' in opt.get('type', ''):
                    improvements['mobile_speed_score'] += improvement * 0.8
                if 'usability' in opt.get('type', ''):
                    improvements['mobile_friendly_score'] += improvement * 0.7
                if 'creator' in opt.get('type', ''):
                    improvements['engagement_score'] += improvement * 0.6
                
                improvements['seo_score'] += improvement * 0.5
        
        # Cap improvements at realistic levels
        for key in improvements:
            improvements[key] = min(improvements[key], 30)  # Max 30 point improvement
        
        return improvements
    
    async def _generate_mobile_seo_enhancements(self,
                                              url: str,
                                              metrics: MobileMetrics) -> Dict[str, Any]:
        """Generate mobile SEO enhancements."""
        enhancements = {
            'mobile_schema_markup': {},
            'mobile_structured_data': {},
            'mobile_meta_tags': {},
            'mobile_sitemap_optimization': {},
            'mobile_internal_linking': {}
        }
        
        # Mobile schema markup
        enhancements['mobile_schema_markup'] = {
            'mobileApplication': {
                '@type': 'MobileApplication',
                'name': 'Ainflue Mobile',
                'operatingSystem': 'Android, iOS',
                'applicationCategory': 'BusinessApplication'
            },
            'creator_mobile_schema': {
                '@type': 'Person',
                'identifier': metrics.creator_id,
                'sameAs': [f"{url}/mobile"]
            } if metrics.creator_id else {}
        }
        
        # Mobile meta tags
        enhancements['mobile_meta_tags'] = {
            'viewport': 'width=device-width, initial-scale=1.0',
            'mobile-web-app-capable': 'yes',
            'apple-mobile-web-app-capable': 'yes',
            'apple-mobile-web-app-status-bar-style': 'default',
            'theme-color': '#667eea'
        }
        
        # Mobile sitemap optimization
        enhancements['mobile_sitemap_optimization'] = {
            'mobile_sitemap_url': f"{url}/sitemap-mobile.xml",
            'mobile_specific_urls': True,
            'mobile_image_optimization': True,
            'mobile_video_optimization': True
        }
        
        return enhancements
    
    def _calculate_mobile_seo_score(self, metrics: MobileMetrics) -> float:
        """Calculate overall mobile SEO score."""
        score = 0.0
        
        # Performance score (30%)
        score += (metrics.mobile_speed_score / 100) * 30
        
        # Mobile friendly score (40%)
        score += (metrics.mobile_friendly_score / 100) * 40
        
        # Technical features (30%)
        technical_score = 0
        if metrics.viewport_configured:
            technical_score += 25
        if metrics.amp_valid:
            technical_score += 25
        if metrics.pwa_features >= 3:
            technical_score += 25
        if metrics.responsive_breakpoints_working:
            technical_score += 25
        
        score += (technical_score / 100) * 30
        
        return round(score, 1)
    
    async def _enable_creator_mobile_features(self,
                                            creator_id: str,
                                            creator_type: str,
                                            url_analyses: List[Dict[str, Any]]) -> List[str]:
        """Enable creator-specific mobile features."""
        features = []
        
        # Basic features for all creators
        features.extend([
            'mobile_responsive_profile',
            'touch_optimized_navigation',
            'mobile_content_upload'
        ])
        
        # Enhanced features for pro/premium creators
        if creator_type in ['pro', 'premium']:
            features.extend([
                'mobile_analytics_dashboard',
                'mobile_monetization_tools',
                'mobile_collaboration_features'
            ])
        
        # Advanced features for premium creators
        if creator_type == 'premium':
            features.extend([
                'mobile_app_integration',
                'advanced_mobile_customization',
                'mobile_priority_support'
            ])
        
        # Feature-specific enablement based on performance
        avg_mobile_score = sum(
            analysis['mobile_seo_score'] for analysis in url_analyses
        ) / len(url_analyses) if url_analyses else 0
        
        if avg_mobile_score >= 80:
            features.append('mobile_performance_badge')
        
        return features
    
    async def _generate_platform_mobile_features(self) -> Dict[str, Any]:
        """Generate platform-wide mobile features."""
        return {
            'universal_mobile_features': [
                'Progressive Web App support',
                'Mobile-first responsive design',
                'Touch-optimized interface',
                'Mobile performance monitoring',
                'AMP support for content pages'
            ],
            'creator_mobile_tools': [
                'Mobile content creation tools',
                'Mobile analytics dashboard',
                'Mobile audience engagement features',
                'Mobile monetization integration',
                'Mobile collaboration platform'
            ],
            'mobile_seo_features': [
                'Mobile-specific structured data',
                'Mobile sitemap generation',
                'Mobile performance optimization',
                'Mobile search optimization',
                'Mobile social sharing optimization'
            ]
        }
    
    def _create_mobile_implementation_roadmap(self, optimization_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create mobile implementation roadmap."""
        roadmap = {
            'phase_1_immediate': {
                'duration': '1-2 weeks',
                'tasks': [
                    'Fix critical viewport and touch target issues',
                    'Implement basic responsive design fixes',
                    'Optimize mobile page speed for top creators'
                ],
                'priority': 'critical'
            },
            'phase_2_enhancement': {
                'duration': '3-4 weeks',
                'tasks': [
                    'Implement PWA features',
                    'Add mobile-specific schema markup',
                    'Optimize mobile content consumption'
                ],
                'priority': 'high'
            },
            'phase_3_advanced': {
                'duration': '2-3 months',
                'tasks': [
                    'Implement AMP for key pages',
                    'Advanced mobile analytics integration',
                    'Mobile app integration features'
                ],
                'priority': 'medium'
            }
        }
        
        # Customize roadmap based on optimization results
        high_priority_creators = [
            r for r in optimization_results 
            if r['overall_mobile_score'] < 60
        ]
        
        if len(high_priority_creators) > 10:
            roadmap['phase_1_immediate']['tasks'].insert(0, 
                'Emergency mobile optimization for low-scoring creators')
        
        return roadmap

# Enterprise mobile optimization management
class MobileOptimizationManager:
    """High-level mobile optimization management for Ainflue platform."""
    
    def __init__(self, optimization_level: MobileOptimizationLevel = MobileOptimizationLevel.ENHANCED):
        self.mobile_seo = MobileTechnicalSEO(optimization_level)
        self.optimization_level = optimization_level
        
    async def optimize_platform_mobile_experience(self,
                                                 platform_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize entire platform mobile experience."""
        optimization_results = {
            'platform_mobile_analysis': {},
            'creator_optimizations': {},
            'technical_implementations': {},
            'performance_improvements': {},
            'mobile_seo_enhancements': {}
        }
        
        # Analyze platform mobile readiness
        core_urls = platform_data.get('core_urls', [])
        platform_analysis = []
        
        for url_info in core_urls:
            metrics = await self.mobile_seo.analyze_mobile_performance(
                url_info['url'], DeviceType.SMARTPHONE
            )
            platform_analysis.append({
                'url': url_info['url'],
                'type': url_info.get('type', 'page'),
                'metrics': metrics,
                'mobile_score': self.mobile_seo._calculate_mobile_seo_score(metrics)
            })
        
        optimization_results['platform_mobile_analysis'] = platform_analysis
        
        # Optimize creator mobile experiences
        creator_data = platform_data.get('creators', [])
        if creator_data:
            creator_optimizations = await self.mobile_seo.setup_creator_mobile_optimization(creator_data)
            optimization_results['creator_optimizations'] = creator_optimizations
        
        # Generate technical implementations
        if platform_analysis:
            best_metrics = max(platform_analysis, key=lambda x: x['mobile_score'])['metrics']
            optimization_plan = await self.mobile_seo.optimize_mobile_experience(
                best_metrics.url, best_metrics
            )
            code_snippets = await self.mobile_seo.generate_mobile_optimization_code(optimization_plan)
            optimization_results['technical_implementations'] = code_snippets
        
        return optimization_results