"""
Campaign Management Module for IA Influencer Agent Platform
===========================================================

This module handles comprehensive campaign management for multi-format content creators,
integrating AI processing, content protection, monetization, and collaboration features.

Core Features:
- Campaign lifecycle management (creation, execution, monitoring, optimization)
- Multi-format content integration (audio, video, image, text)
- AI-powered campaign optimization and recommendations
- Content protection and rights management
- Revenue tracking and distribution
- Collaboration and partnership management
- Performance analytics and reporting
- SEO optimization and multi-platform distribution

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Advanced Multi-Format Content Platform
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected by copyright law. Unauthorized use, reproduction,
or distribution without explicit written permission from Fahed Mlaiel is strictly
prohibited and may result in legal action.

Team Specialties:
- Lead AI Developer & Architecture
- Backend Senior Engineer  
- ML/AI Engineer
- Database Administrator
- Security Engineer
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from .campaign_manager import CampaignManager
from .campaign_analytics import CampaignAnalytics
from .campaign_optimization import CampaignOptimization
from .content_integration import ContentIntegration
from .collaboration_engine import CollaborationEngine
from .protection_manager import ProtectionManager
from .monetization_engine import MonetizationEngine
from .distribution_manager import DistributionManager
from .performance_tracker import PerformanceTracker
from .seo_optimizer import SEOOptimizer

__all__ = [
    "CampaignManager",
    "CampaignAnalytics", 
    "CampaignOptimization",
    "ContentIntegration",
    "CollaborationEngine",
    "ProtectionManager",
    "MonetizationEngine",
    "DistributionManager",
    "PerformanceTracker",
    "SEOOptimizer"
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
