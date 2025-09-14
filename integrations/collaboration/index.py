"""
Collaboration - Ainflue Integrations
====================================
Point d'entrée principal pour le module de collaboration IA.
Orchestration de matching créateurs et workflows collaboratifs.

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

# Configuration logique métier Ainflue
COLLABORATION_CONFIG = {
    'platforms_supported': 65,
    'ai_agents': 5,
    'matching_algorithms': ['compatibility', 'style', 'audience', 'revenue'],
    'workflow_types': ['audio', 'video', 'image', 'text', 'remix'],
    'revenue_models': ['split', 'performance', 'royalty', 'subscription'],
    'reputation_factors': ['quality', 'reliability', 'engagement', 'revenue']
}

def get_collaboration_manager() -> None:
    """Factory pour créer le gestionnaire principal de collaboration."""
    return {
        'matching': AIMatchingEngine(),
        'analytics': CollaborationAnalytics(),
        'realtime': RealTimeCollaboration(),
        'projects': ProjectManagement(),
        'reputation': ReputationSystem(),
        'revenue': RevenueSharing()
    }