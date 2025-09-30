"""SEO Module for Ainflue Platform

This module provides comprehensive SEO automation and optimization capabilities
for the Ainflue AI-powered content platform including automated meta optimization,
AMP pages, Core Web Vitals optimization, multilingual SEO, and sitemap generation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .optimization import *
from .analytics import *
from .automation_service import *

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    "optimization",
    "analytics", 
    "automation_service"
]