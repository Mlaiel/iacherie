"""
CDN Module - Global Content Delivery Network Infrastructure
================================================================================

Expert Team: Backend Senior + Audio Engineer + DevOps + Security
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🏗️ Backend Senior: CDN orchestration, multi-provider management
🎵 Audio Engineer: High-quality audio/video streaming optimization
⚙️ DevOps: Edge computing automation, performance monitoring
🔒 Security: CDN security, DDoS protection, content protection

Global CDN infrastructure for Ainflue creator content delivery supporting:
- Multi-CDN orchestration across providers
- Edge computing for real-time processing
- High-quality media streaming optimization
- Intelligent caching and invalidation
- Bandwidth optimization and cost management
- Mobile-optimized content delivery
- Specialized audio and video CDN services
"""

from .global_cdn_manager import GlobalCDNManager
from .edge_computing_manager import EdgeComputingManager
from .media_cdn_optimizer import MediaCDNOptimizer
from .cdn_analytics import CDNAnalytics
from .cache_invalidation import CacheInvalidation
from .cdn_performance_optimizer import CDNPerformanceOptimizer
from .multi_cdn_orchestrator import MultiCDNOrchestrator
from .bandwidth_optimizer import BandwidthOptimizer
from .cdn_security_manager import CDNSecurityManager
from .mobile_cdn_optimizer import MobileCDNOptimizer
from .video_cdn_specialist import VideoCDNSpecialist
from .audio_cdn_specialist import AudioCDNSpecialist

__all__ = [
    'GlobalCDNManager',
    'EdgeComputingManager',
    'MediaCDNOptimizer',
    'CDNAnalytics',
    'CacheInvalidation',
    'CDNPerformanceOptimizer',
    'MultiCDNOrchestrator',
    'BandwidthOptimizer',
    'CDNSecurityManager',
    'MobileCDNOptimizer',
    'VideoCDNSpecialist',
    'AudioCDNSpecialist'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Global CDN infrastructure for high-performance content delivery"