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
from .enterprise_collaboration_gateway import EnterpriseCollaborationGateway
from .collaboration_security import CollaborationSecurityManager
from .notification_orchestrator import NotificationOrchestrator
from .advanced_gamification import AdvancedGamificationEngine
from .ai_conflict_resolution import AIConflictResolutionSystem
from .workflow_automation import WorkflowAutomationEngine
from .collaboration_marketplace import CollaborationMarketplace
from .blockchain_payments import BlockchainPaymentProcessor
from .quality_assurance import QualityAssuranceManager
from .enterprise_reporting import EnterpriseReportingEngine

__all__ = [
    'AIMatchingEngine',
    'RealTimeCollaboration',
    'CollaborationAnalytics',
    'ProjectManagement',
    'ReputationSystem',
    'RevenueSharing',
    'EnterpriseCollaborationGateway',
    'CollaborationSecurityManager',
    'NotificationOrchestrator',
    'AdvancedGamificationEngine',
    'AIConflictResolutionSystem',
    'WorkflowAutomationEngine',
    'CollaborationMarketplace',
    'BlockchainPaymentProcessor',
    'QualityAssuranceManager',
    'EnterpriseReportingEngine'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Collaboration IA enterprise pour créateurs Ainflue"

# Configuration logique métier Ainflue - UPDATED with Phase 1, 2 & 3 components
COLLABORATION_CONFIG = {
    'platforms_supported': 65,
    'ai_agents': 53,
    'matching_algorithms': ['compatibility', 'style', 'audience', 'revenue'],
    'workflow_types': ['audio', 'video', 'image', 'text', 'remix'],
    'revenue_models': ['split', 'performance', 'royalty', 'subscription'],
    'reputation_factors': ['quality', 'reliability', 'engagement', 'revenue'],
    'security_levels': ['basic', 'enhanced', 'enterprise', 'maximum'],
    'notification_channels': ['email', 'sms', 'push', 'in_app', 'webhook', 'slack'],
    'tenant_tiers': ['free', 'professional', 'enterprise', 'ultimate'],
    'gamification_badges': 200,
    'conflict_resolution_methods': ['automated', 'ai_mediation', 'human_mediation', 'arbitration'],
    'skill_trees': 5,
    'payment_cryptocurrencies': ['ETH', 'USDC', 'USDT', 'DAI', 'MATIC', 'BNB'],
    'blockchain_networks': ['Ethereum', 'Polygon', 'BSC', 'Arbitrum', 'Optimism'],
    'quality_assessment_criteria': 8,
    'enterprise_features': ['multi_tenant', 'api_gateway', 'advanced_analytics', 'blockchain_integration']
}

def get_collaboration_manager():
    """Factory pour créer le gestionnaire principal de collaboration avec composants enterprise Phase 1, 2 & 3."""
    return {
        # Phase 1: Core Infrastructure (CRITICAL)
        'gateway': EnterpriseCollaborationGateway(),
        'security': CollaborationSecurityManager(),
        'notifications': NotificationOrchestrator(),
        
        # Phase 2: Advanced Features (HIGH PRIORITY)
        'gamification': AdvancedGamificationEngine(),
        'conflict_resolution': AIConflictResolutionSystem(),
        'workflow': WorkflowAutomationEngine(),
        
        # Phase 3: Enterprise Marketplace & Reporting (MEDIUM PRIORITY)
        'marketplace': CollaborationMarketplace(),
        'payments': BlockchainPaymentProcessor(),
        'quality_assurance': QualityAssuranceManager(),
        'reporting': EnterpriseReportingEngine(),
        
        # Original Core Components (FOUNDATION)
        'matching': AIMatchingEngine(),
        'analytics': CollaborationAnalytics(),
        'realtime': RealTimeCollaboration(),
        'projects': ProjectManagement(),
        'reputation': ReputationSystem(),
        'revenue': RevenueSharing()
    }

def get_enterprise_config():
    """Get enterprise configuration for collaboration module."""
    return COLLABORATION_CONFIG.copy()