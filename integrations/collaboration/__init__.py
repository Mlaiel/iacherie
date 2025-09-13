"""
Collaboration Module - Ainflue Integrations
==========================================
Module de collaboration IA avancé pour matching créateurs,
gamification, et orchestration de workflows collaboratifs.

Support pour:
- Matching IA créateurs compatibles
- Collaboration temps réel
- Gestion projets collaboratifs
- Système de réputation
- Partage de revenus automatisé

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

from .ai_matching_engine import AIMatchingEngine
from .real_time_collaboration import RealTimeCollaboration
from .collaboration_analytics import CollaborationAnalytics
from .project_management import ProjectManagement
from .reputation_system import ReputationSystem
from .revenue_sharing import RevenueSharing

__all__ = [
    'AIMatchingEngine',
    'RealTimeCollaboration',
    'CollaborationAnalytics',
    'ProjectManagement',
    'ReputationSystem',
    'RevenueSharing'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Collaboration IA enterprise pour créateurs Ainflue"