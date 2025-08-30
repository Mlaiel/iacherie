"""
Mobile Application Infrastructure - Ainflue Platform
Enterprise-grade mobile backend services and infrastructure

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

# Core mobile infrastructure modules
from mobile.backend import *
from mobile.services import *
from mobile.security import *

# Mobile API endpoints
from mobile.api import *

# Mobile analytics and monitoring
from mobile.analytics import *

# Mobile configuration
from mobile.config import *

__all__ = [
    "backend",
    "services", 
    "security",
    "api",
    "analytics",
    "config"
]