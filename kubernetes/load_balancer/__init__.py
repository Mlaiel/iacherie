"""Load Balancer Module for IA Influencer Agent Platform

This module provides enterprise-grade load balancing capabilities for the
IA Influencer Agent platform, handling high-traffic scenarios for content
protection, fingerprinting, and monetization services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""

from .nginx_manager import NginxManager
from .haproxy_manager import HAProxyManager
from .envoy_manager import EnvoyManager
from .health_monitor import HealthMonitor
from .traffic_distributor import TrafficDistributor
from .ssl_terminator import SSLTerminator
from .rate_limiter import RateLimiter
from .circuit_breaker import CircuitBreaker
from .metrics_collector import MetricsCollector
from .session_manager import SessionManager
from .bandwidth_monitor import BandwidthMonitor
from .config_manager import ConfigurationManager
from .performance_optimizer import PerformanceOptimizer
from .failover_manager import FailoverManager
from .geo_load_balancer import GeographicLoadBalancer
from .traffic_shaping_engine import TrafficShapingEngine
from .request_router import RequestRouter
from .realtime_monitor import RealtimeMonitor
from .ai_optimizer import AILoadBalancerOptimizer

__all__ = [
    # Core Load Balancers
    'NginxManager',
    'HAProxyManager', 
    'EnvoyManager',
    
    # Traffic Management
    'HealthMonitor',
    'TrafficDistributor',
    'GeographicLoadBalancer',
    'TrafficShapingEngine',
    'RequestRouter',
    
    # Security & Reliability
    'SSLTerminator',
    'RateLimiter',
    'CircuitBreaker',
    'FailoverManager',
    
    # Monitoring & Analytics
    'MetricsCollector',
    'RealtimeMonitor',
    
    # Performance & Optimization
    'SessionManager',
    'BandwidthMonitor',
    'PerformanceOptimizer',
    'AILoadBalancerOptimizer',
    
    # Configuration
    'ConfigurationManager'
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__platform__ = "IA Influencer Agent - Enterprise Load Balancing"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Contact mlaiel@live.de for licensing"

# Module metadata for enterprise deployment
MODULE_INFO = {
    "name": "IA Influencer Agent Load Balancer",
    "version": __version__,
    "description": "Enterprise-grade load balancing infrastructure for content protection, fingerprinting, and monetization services",
    "author": __author__,
    "email": __email__,
    "components": len(__all__),
    "features": [
        "High-performance HTTP/HTTPS load balancing",
        "Advanced Layer 4/7 traffic management",
        "AI-powered optimization and prediction",
        "Real-time monitoring and alerting",
        "Geographic traffic distribution",
        "Enterprise security and compliance",
        "Automatic failover and disaster recovery",
        "ML-based anomaly detection",
        "Intelligent traffic shaping",
        "Multi-tenant isolation",
        "Performance optimization",
        "Cost optimization recommendations"
    ],
    "supported_services": [
        "Fingerprinting Services (Audio, Video, Image, Text)",
        "Content Protection and Monitoring",
        "AI Agent Services and Spotify Integration",
        "Monetization and Payment Processing",
        "Web Crawlers and Data Collection",
        "Licensing and Contract Management"
    ]
}

def get_module_info() -> None:
    """Get comprehensive module information"""
    return MODULE_INFO

def get_version() -> None:
    """
Get module version"""
    return __version__

def get_available_components() -> None:
    """
Get list of available load balancer components"""
    return __all__
