"""
Collaboration - IA Chéries Integrations
====================================
Point d'entrée principal pour le module de collaboration IA.
Orchestration de matching créateurs et workflows collaboratifs.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Integrations  
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
from .gamification_engine import AdvancedGamificationEngine
from .ai_conflict_resolution import AIConflictResolutionSystem

# Configuration logique métier IA Chéries - UPDATED with Phase 2 components
COLLABORATION_CONFIG = {
    'platforms_supported': 65,
    'ai_agents': 5,
    'matching_algorithms': ['compatibility', 'style', 'audience', 'revenue'],
    'workflow_types': ['audio', 'video', 'image', 'text', 'remix'],
    'revenue_models': ['split', 'performance', 'royalty', 'subscription'],
    'reputation_factors': ['quality', 'reliability', 'engagement', 'revenue'],
    'security_levels': ['basic', 'enhanced', 'enterprise', 'maximum'],
    'notification_channels': ['email', 'sms', 'push', 'in_app', 'webhook', 'slack'],
    'tenant_tiers': ['free', 'professional', 'enterprise', 'ultimate'],
    'gamification_badges': 200,
    'conflict_resolution_methods': ['automated', 'ai_mediation', 'human_mediation', 'arbitration'],
    'skill_trees': 5
}

def get_collaboration_manager():
    """Factory pour créer le gestionnaire principal de collaboration avec composants enterprise Phase 1 & 2."""
    return {
        'matching': AIMatchingEngine(),
        'analytics': CollaborationAnalytics(),
        'realtime': RealTimeCollaboration(),
        'projects': ProjectManagement(),
        'reputation': ReputationSystem(),
        'revenue': RevenueSharing(),
        'gateway': EnterpriseCollaborationGateway(),
        'security': CollaborationSecurityManager(),
        'notifications': NotificationOrchestrator(),
        'gamification': AdvancedGamificationEngine(),
        'conflict_resolution': AIConflictResolutionSystem()
    }