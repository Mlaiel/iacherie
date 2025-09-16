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
from .enterprise_collaboration_gateway import EnterpriseCollaborationGateway
from .collaboration_security import CollaborationSecurityManager
from .notification_orchestrator import NotificationOrchestrator

# Configuration logique métier Ainflue - UPDATED with Phase 1 components
COLLABORATION_CONFIG = {
    'platforms_supported': 65,
    'ai_agents': 5,
    'matching_algorithms': ['compatibility', 'style', 'audience', 'revenue'],
    'workflow_types': ['audio', 'video', 'image', 'text', 'remix'],
    'revenue_models': ['split', 'performance', 'royalty', 'subscription'],
    'reputation_factors': ['quality', 'reliability', 'engagement', 'revenue'],
    'security_levels': ['basic', 'enhanced', 'enterprise', 'maximum'],
    'notification_channels': ['email', 'sms', 'push', 'in_app', 'webhook', 'slack'],
    'tenant_tiers': ['free', 'professional', 'enterprise', 'ultimate']
}

def get_collaboration_manager():
    """Factory pour créer le gestionnaire principal de collaboration avec composants enterprise."""
    return {
        'matching': AIMatchingEngine(),
        'analytics': CollaborationAnalytics(),
        'realtime': RealTimeCollaboration(),
        'projects': ProjectManagement(),
        'reputation': ReputationSystem(),
        'revenue': RevenueSharing(),
        'gateway': EnterpriseCollaborationGateway(),
        'security': CollaborationSecurityManager(),
        'notifications': NotificationOrchestrator()
    }