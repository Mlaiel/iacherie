"""Technical SEO Package
Core technical SEO modules for website optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .schema_markup_generator import SchemaMarkupGenerator
from .robots_txt_manager import RobotsTxtManager
from .canonical_url_manager import CanonicalURLManager
from .xml_sitemap_generator import XMLSitemapGenerator, SitemapManager
from .core_web_vitals_optimizer import CoreWebVitalsOptimizer, PerformanceMonitor
from .image_technical_optimizer import ImageTechnicalOptimizer, ImageOptimizationManager
from .technical_performance_monitor import TechnicalPerformanceMonitor, PerformanceMonitoringManager
from .mobile_technical_seo import MobileTechnicalSEO, MobileOptimizationManager
from .internationalization_manager import InternationalizationManager, GlobalExpansionManager
from .url_structure_optimizer import URLStructureOptimizer, URLArchitectureManager

__all__ = [
    "SchemaMarkupGenerator",
    "RobotsTxtManager", 
    "CanonicalURLManager",
    "XMLSitemapGenerator",
    "SitemapManager",
    "CoreWebVitalsOptimizer",
    "PerformanceMonitor",
    "ImageTechnicalOptimizer",
    "ImageOptimizationManager",
    "TechnicalPerformanceMonitor",
    "PerformanceMonitoringManager",
    "MobileTechnicalSEO",
    "MobileOptimizationManager",
    "InternationalizationManager",
    "GlobalExpansionManager",
    "URLStructureOptimizer",
    "URLArchitectureManager"
]