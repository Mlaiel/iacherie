"""
Crawling Agent Module - Advanced Web Surveillance & Content Discovery System

Industrial web crawling, content monitoring, and automated surveillance system.
Handles multi-platform crawling, content detection, and real-time monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

# Core agent components
from .crawling_agent import (
    CrawlingAgent, 
    CrawlingAgentManager,
    CrawlingConfig,
    CrawledContent,
    SurveillanceTarget
)

# Web crawling components
from .web_crawler import (
    WebCrawler, 
    SiteMonitor,
    CrawlerMode,
    ContentExtractionMethod,
    RobotsPolicyLevel
)

# Content detection and analysis
from .content_detector import (
    ContentDetector, 
    SimilarityScanner,
    ContentType,
    SimilarityMethod,
    DetectionLevel,
    ContentSignature
)

# NEW FUSIONED MODULES FROM WEB_MONITORING_AGENT
from .violation_analyzer import ViolationAnalyzer
from .models import MonitoringModels

# Platform-specific crawling
from .platform_crawler import (
    PlatformCrawler, 
    APIHarvester,
    PlatformType,
    CrawlingMethod,
    ContentCategory,
    PlatformConfig,
    PlatformContent
)

# Surveillance and monitoring
from .surveillance_engine import (
    SurveillanceEngine, 
    AlertSystem,
    SurveillanceStatus,
    ThreatLevel,
    AlertType,
    MonitoringMode
)

# Configuration and utilities
from .config import (
    CrawlingAgentConfig,
    CrawlingPerformanceConfig,
    SecurityConfig,
    PlatformAPIConfig,
    get_config
)

from .utils import (
    URLProcessor,
    ContentAnalyzer,
    HTMLProcessor,
    PerformanceOptimizer,
    RobotsChecker,
    UserAgentRotator,
    create_fingerprint,
    calculate_similarity_score
)

from .exceptions import (
    CrawlingAgentException,
    CrawlingError,
    NetworkError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    SurveillanceError,
    ContentProcessingError
)

# Service interface
from .index import (
    CrawlingServiceInterface,
    CrawlingServiceConfig,
    create_crawling_service,
    quick_content_discovery,
    quick_similarity_check
)

# Version information
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary"
__copyright__ = "Copyright (c) 2025 Fahed Mlaiel. All rights reserved."

# Export all public interfaces
__all__ = [
    # Core classes
    'CrawlingAgent',
    'CrawlingAgentManager',
    'WebCrawler',
    'SiteMonitor',
    'ContentDetector',
    'SimilarityScanner',
    'PlatformCrawler',
    'APIHarvester',
    'SurveillanceEngine',
    'AlertSystem',
    
    # Configuration classes
    'CrawlingConfig',
    'CrawledContent',
    'SurveillanceTarget',
    'ContentSignature',
    'PlatformConfig',
    'PlatformContent',
    'CrawlingAgentConfig',
    'CrawlingServiceInterface',
    'CrawlingServiceConfig',
    
    # Enum classes
    'CrawlerMode',
    'ContentExtractionMethod',
    'RobotsPolicyLevel',
    'ContentType',
    'SimilarityMethod',
    'DetectionLevel',
    'PlatformType',
    'CrawlingMethod',
    'ContentCategory',
    'SurveillanceStatus',
    'ThreatLevel',
    'AlertType',
    'MonitoringMode',
    
    # Utility classes
    'URLProcessor',
    'ContentAnalyzer',
    'HTMLProcessor',
    'PerformanceOptimizer',
    'RobotsChecker',
    'UserAgentRotator',
    
    # Exception classes
    'CrawlingAgentException',
    'CrawlingError',
    'NetworkError',
    'AuthenticationError',
    'RateLimitError',
    'ValidationError',
    'SurveillanceError',
    'ContentProcessingError',
    
    # Factory functions
    'create_crawling_service',
    'quick_content_discovery',
    'quick_similarity_check',
    'get_config',
    
    # Utility functions
    'create_fingerprint',
    'calculate_similarity_score',
    
    # Module metadata
    '__version__',
    '__author__',
    '__email__',
    '__license__',
    '__copyright__'
]

# Module initialization
def initialize_module():
    """Initialize the crawling agent module with default settings"""
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info(f"Crawling Agent Module v{__version__} initialized")
    logger.info(f"Author: {__author__} ({__email__})")
    logger.info("Industrial-grade web crawling and surveillance system ready")
    
    # Verify critical dependencies
    try:
        import aiohttp
        import selenium
        import beautifulsoup4
        import numpy
        import sklearn
        logger.info("All critical dependencies verified")
    except ImportError as e:
        logger.warning(f"Missing optional dependency: {e}")

# Auto-initialize on import
initialize_module()
