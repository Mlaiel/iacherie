"""
Repository Module Initialization

Enterprise-grade repository collection for the IA Influencer Agent + Content Protection Platform.
Comprehensive repository pattern implementation with CRUD operations, business logic, and analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from typing import Dict, Type, Any
from sqlalchemy.orm import Session

# Import base repository
from .base_repository import BaseRepository, RepositoryException

# Import all repository implementations
from .content_fingerprint_repository import ContentFingerprintRepository
from .protection_alert_repository import ProtectionAlertRepository
from .revenue_tracking_repository import RevenueTrackingRepository
from .user_content_repository import UserContentRepository
from .platform_integration_repository import PlatformIntegrationRepository
from .licensing_agreement_repository import LicensingAgreementRepository
from .audit_log_repository import AuditLogRepository
from .content_metadata_repository import ContentMetadataRepository
from .monetization_rule_repository import MonetizationRuleRepository
from .collaboration_request_repository import CollaborationRequestRepository

# Import new enterprise repositories
from .ai_content_generation_repository import AIContentGenerationRepository
from .content_distribution_repository import ContentDistributionRepository
from .social_media_analytics_repository import SocialMediaAnalyticsRepository
from .content_optimization_repository import ContentOptimizationRepository
from .creator_profile_repository import CreatorProfileRepository
from .audio_analytics_repository import AudioAnalyticsRepository

# Import latest advanced repositories
from .blockchain_rights_repository import BlockchainRightsRepository
from .cross_platform_monitoring_repository import CrossPlatformMonitoringRepository
from .ai_revenue_analytics_repository import AIRevenueAnalyticsRepository
from .advanced_team_collaboration_repository import AdvancedTeamCollaborationRepository

# Import new licensing repositories
from .license_repository import LicenseRepository
from .content_repository import ContentRepository

# Repository registry for dynamic access and dependency injection
REPOSITORY_REGISTRY: Dict[str, Type[BaseRepository]] = {
    'content_fingerprint': ContentFingerprintRepository,
    'protection_alert': ProtectionAlertRepository,
    'revenue_tracking': RevenueTrackingRepository,
    'user_content': UserContentRepository,
    'platform_integration': PlatformIntegrationRepository,
    'licensing_agreement': LicensingAgreementRepository,
    'audit_log': AuditLogRepository,
    'content_metadata': ContentMetadataRepository,
    'monetization_rule': MonetizationRuleRepository,
    'collaboration_request': CollaborationRequestRepository,
    # New enterprise repositories
    'ai_content_generation': AIContentGenerationRepository,
    'content_distribution': ContentDistributionRepository,
    'social_media_analytics': SocialMediaAnalyticsRepository,
    'content_optimization': ContentOptimizationRepository,
    'creator_profile': CreatorProfileRepository,
    'audio_analytics': AudioAnalyticsRepository,
    
    # Latest advanced repositories
    'blockchain_rights': BlockchainRightsRepository,
    'cross_platform_monitoring': CrossPlatformMonitoringRepository,
    'ai_revenue_analytics': AIRevenueAnalyticsRepository,
    'advanced_team_collaboration': AdvancedTeamCollaborationRepository,
    
    # Licensing repositories
    'license': LicenseRepository,
    'content': ContentRepository
}

class RepositoryFactory:
    """
    Factory class for creating repository instances with dependency injection
    and session management for enterprise-grade operations.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize repository factory with database session
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        self._repository_cache: Dict[str, BaseRepository] = {}
        
    def get_repository(self, repository_name: str) -> BaseRepository:
        """
        Get repository instance by name with caching
        
        Args:
            repository_name: Name of repository to retrieve
            
        Returns:
            Repository instance
            
        Raises:
            RepositoryException: If repository name is not found
        """
        if repository_name not in REPOSITORY_REGISTRY:
            raise RepositoryException(f"Repository '{repository_name}' not found")
        
        # Return cached instance if available
        if repository_name in self._repository_cache:
            return self._repository_cache[repository_name]
        
        # Create new instance and cache it
        repository_class = REPOSITORY_REGISTRY[repository_name]
        repository_instance = repository_class(self.db_session)
        self._repository_cache[repository_name] = repository_instance
        
        return repository_instance
    
    def get_content_fingerprint_repository(self) -> ContentFingerprintRepository:
        """Get ContentFingerprintRepository instance"""
        return self.get_repository('content_fingerprint')
    
    def get_protection_alert_repository(self) -> ProtectionAlertRepository:
        """Get ProtectionAlertRepository instance"""
        return self.get_repository('protection_alert')
    
    def get_revenue_tracking_repository(self) -> RevenueTrackingRepository:
        """Get RevenueTrackingRepository instance"""
        return self.get_repository('revenue_tracking')
    
    def get_user_content_repository(self) -> UserContentRepository:
        """Get UserContentRepository instance"""
        return self.get_repository('user_content')
    
    def get_platform_integration_repository(self) -> PlatformIntegrationRepository:
        """Get PlatformIntegrationRepository instance"""
        return self.get_repository('platform_integration')
    
    def get_licensing_agreement_repository(self) -> LicensingAgreementRepository:
        """Get LicensingAgreementRepository instance"""
        return self.get_repository('licensing_agreement')
    
    def get_audit_log_repository(self) -> AuditLogRepository:
        """Get AuditLogRepository instance"""
        return self.get_repository('audit_log')
    
    def get_content_metadata_repository(self) -> ContentMetadataRepository:
        """Get ContentMetadataRepository instance"""
        return self.get_repository('content_metadata')
    
    def get_monetization_rule_repository(self) -> MonetizationRuleRepository:
        """Get MonetizationRuleRepository instance"""
        return self.get_repository('monetization_rule')
    
    def get_collaboration_request_repository(self) -> CollaborationRequestRepository:
        """Get CollaborationRequestRepository instance"""
        return self.get_repository('collaboration_request')
    
    def get_ai_content_generation_repository(self) -> AIContentGenerationRepository:
        """Get AIContentGenerationRepository instance"""
        return self.get_repository('ai_content_generation')
    
    def get_content_distribution_repository(self) -> ContentDistributionRepository:
        """Get ContentDistributionRepository instance"""
        return self.get_repository('content_distribution')
    
    def get_social_media_analytics_repository(self) -> SocialMediaAnalyticsRepository:
        """Get SocialMediaAnalyticsRepository instance"""
        return self.get_repository('social_media_analytics')
    
    def get_content_optimization_repository(self) -> ContentOptimizationRepository:
        """Get ContentOptimizationRepository instance"""
        return self.get_repository('content_optimization')
    
    def get_creator_profile_repository(self) -> CreatorProfileRepository:
        """Get CreatorProfileRepository instance"""
        return self.get_repository('creator_profile')
    
    def get_audio_analytics_repository(self) -> AudioAnalyticsRepository:
        """Get AudioAnalyticsRepository instance"""
        return self.get_repository('audio_analytics')
    
    def get_blockchain_rights_repository(self) -> BlockchainRightsRepository:
        """Get BlockchainRightsRepository instance"""
        return self.get_repository('blockchain_rights')
    
    def get_cross_platform_monitoring_repository(self) -> CrossPlatformMonitoringRepository:
        """Get CrossPlatformMonitoringRepository instance"""
        return self.get_repository('cross_platform_monitoring')
    
    def get_ai_revenue_analytics_repository(self) -> AIRevenueAnalyticsRepository:
        """Get AIRevenueAnalyticsRepository instance"""
        return self.get_repository('ai_revenue_analytics')
    
    def get_advanced_team_collaboration_repository(self) -> AdvancedTeamCollaborationRepository:
        """Get AdvancedTeamCollaborationRepository instance"""
        return self.get_repository('advanced_team_collaboration')
    
    def clear_cache(self) -> None:
        """Clear repository instance cache"""
        self._repository_cache.clear()
    
    def get_all_repositories(self) -> Dict[str, BaseRepository]:
        """
        Get all repository instances
        
        Returns:
            Dictionary of repository instances by name
        """
        repositories = {}
        for name in REPOSITORY_REGISTRY.keys():
            repositories[name] = self.get_repository(name)
        return repositories

# Convenience function for quick repository access
def create_repository_factory(db_session: Session) -> RepositoryFactory:
    """
    Create repository factory instance
    
    Args:
        db_session: SQLAlchemy database session
        
    Returns:
        RepositoryFactory instance
    """
    return RepositoryFactory(db_session)

# Export all repository classes for direct import
__all__ = [
    # Base classes
    'BaseRepository',
    'RepositoryException',
    'RepositoryFactory',
    
    # Repository implementations
    'ContentFingerprintRepository',
    'ProtectionAlertRepository',
    'RevenueTrackingRepository',
    'UserContentRepository',
    'PlatformIntegrationRepository',
    'LicensingAgreementRepository',
    'AuditLogRepository',
    'ContentMetadataRepository',
    'MonetizationRuleRepository',
    'CollaborationRequestRepository',
    
    # New enterprise repositories
    'AIContentGenerationRepository',
    'ContentDistributionRepository',
    'SocialMediaAnalyticsRepository',
    'ContentOptimizationRepository',
    'CreatorProfileRepository',
    'AudioAnalyticsRepository',
    
    # Latest advanced repositories
    'BlockchainRightsRepository',
    'CrossPlatformMonitoringRepository',
    'AIRevenueAnalyticsRepository',
    'AdvancedTeamCollaborationRepository',
    
    # Licensing repositories
    'LicenseRepository',
    'ContentRepository',
    
    # Utility functions
    'create_repository_factory',
    
    # Registry
    'REPOSITORY_REGISTRY'
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
