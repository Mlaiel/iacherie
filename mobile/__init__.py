"""Mobile Application Infrastructure - Ainflue Platform
Enterprise-grade mobile backend services and infrastructure

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ STRICT COPYRIGHT NOTICE ⚠️
This code is proprietary and confidential to Fahed Mlaiel.
Any unauthorized use, copying, modification, or distribution
without explicit written permission is strictly prohibited.
Violations will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""
__version__ = "2.0.0"
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

# Production-ready mobile business services
from mobile.content_pipeline import *
from mobile.monetization_engine import *
from mobile.collaboration_service import *
from mobile.pwa_service import *

__all__ = [
    "backend",
    "services", 
    "security",
    "api",
    "analytics",
    "config",
    "content_pipeline",
    "monetization_engine", 
    "collaboration_service",
    "pwa_service"
]