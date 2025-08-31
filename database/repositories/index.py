"""
Repository Module Index

Central entry point for the database repositories module of the 
IA Influencer Agent + Content Protection Platform.

This module provides enterprise-grade repository implementations with
comprehensive data access patterns, security, monitoring, and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
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

from typing import Dict, List, Type, Any, Optional
from sqlalchemy.orm import Session
import logging

# Import all repository components
from . import (
    BaseRepository,
    RepositoryException,
    RepositoryFactory,
    create_repository_factory,
    REPOSITORY_REGISTRY,
    
    # Core repositories
    ContentFingerprintRepository,
    ProtectionAlertRepository,
    RevenueTrackingRepository,
    UserContentRepository,
    PlatformIntegrationRepository,
    LicensingAgreementRepository,
    AuditLogRepository,
    ContentMetadataRepository,
    MonetizationRuleRepository,
    CollaborationRequestRepository,
    
    # Enterprise repositories
    AIContentGenerationRepository,
    ContentDistributionRepository,
    SocialMediaAnalyticsRepository,
    ContentOptimizationRepository,
    CreatorProfileRepository,
    AudioAnalyticsRepository
)

logger = logging.getLogger(__name__)

class RepositoryManager:
    """
    Central manager for all repository operations and coordination
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize repository manager
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        self.factory = create_repository_factory(db_session)
        self._initialized_repositories: Dict[str, BaseRepository] = {}
        
    def get_repository(self, repository_name: str) -> BaseRepository:
        """
        Get repository instance by name with lazy loading
        
        Args:
            repository_name: Name of repository to retrieve
            
        Returns:
            Repository instance
        """
        if repository_name not in self._initialized_repositories:
            self._initialized_repositories[repository_name] = self.factory.get_repository(repository_name)
            
        return self._initialized_repositories[repository_name]
    
    def health_check_all(self) -> Dict[str, Any]:
        """
        Perform health check on all repositories
        
        Returns:
            Health status for all repositories
        """
        health_results = {
            'overall_status': 'healthy',
            'repository_health': {},
            'failed_repositories': [],
            'total_repositories': len(REPOSITORY_REGISTRY)
        }
        
        failed_count = 0
        
        for repo_name in REPOSITORY_REGISTRY.keys():
            try:
                repo = self.get_repository(repo_name)
                repo_health = repo.health_check()
                health_results['repository_health'][repo_name] = repo_health
                
                if repo_health.get('status') != 'healthy':
                    failed_count += 1
                    health_results['failed_repositories'].append(repo_name)
                    
            except Exception as e:
                failed_count += 1
                health_results['repository_health'][repo_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                health_results['failed_repositories'].append(repo_name)
                logger.error(f"Health check failed for repository {repo_name}: {e}")
        
        # Determine overall status
        if failed_count == 0:
            health_results['overall_status'] = 'healthy'
        elif failed_count < len(REPOSITORY_REGISTRY) / 2:
            health_results['overall_status'] = 'degraded'
        else:
            health_results['overall_status'] = 'unhealthy'
            
        health_results['healthy_count'] = len(REPOSITORY_REGISTRY) - failed_count
        health_results['failed_count'] = failed_count
        
        return health_results
    
    def get_all_statistics(self) -> Dict[str, Any]:
        """
        Get statistics from all repositories
        
        Returns:
            Aggregated statistics from all repositories
        """
        all_stats = {
            'repository_statistics': {},
            'aggregate_metrics': {
                'total_records': 0,
                'total_tables': 0
            }
        }
        
        for repo_name in REPOSITORY_REGISTRY.keys():
            try:
                repo = self.get_repository(repo_name)
                repo_stats = repo.get_statistics()
                all_stats['repository_statistics'][repo_name] = repo_stats
                
                # Aggregate metrics
                if 'total_count' in repo_stats:
                    all_stats['aggregate_metrics']['total_records'] += repo_stats['total_count']
                    all_stats['aggregate_metrics']['total_tables'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to get statistics for repository {repo_name}: {e}")
                all_stats['repository_statistics'][repo_name] = {'error': str(e)}
        
        return all_stats
    
    def optimize_all_tables(self) -> Dict[str, Any]:
        """
        Optimize all repository tables
        
        Returns:
            Optimization results for all repositories
        """
        optimization_results = {
            'optimization_summary': {},
            'successful_optimizations': 0,
            'failed_optimizations': 0
        }
        
        for repo_name in REPOSITORY_REGISTRY.keys():
            try:
                repo = self.get_repository(repo_name)
                optimization_result = repo.optimize_table()
                optimization_results['optimization_summary'][repo_name] = optimization_result
                
                if 'error' not in optimization_result:
                    optimization_results['successful_optimizations'] += 1
                else:
                    optimization_results['failed_optimizations'] += 1
                    
            except Exception as e:
                optimization_results['failed_optimizations'] += 1
                optimization_results['optimization_summary'][repo_name] = {'error': str(e)}
                logger.error(f"Failed to optimize repository {repo_name}: {e}")
        
        return optimization_results
    
    def cleanup_old_data(self, days_to_keep: int = 90) -> Dict[str, Any]:
        """
        Cleanup old data from repositories that support it
        
        Args:
            days_to_keep: Number of days to keep data
            
        Returns:
            Cleanup results
        """
        cleanup_results = {
            'cleanup_summary': {},
            'total_records_cleaned': 0,
            'repositories_cleaned': 0
        }
        
        # Repositories that support cleanup
        cleanup_methods = {
            'ai_content_generation': 'cleanup_old_generations',
            'content_distribution': 'cleanup_old_distributions',
            'audit_log': 'cleanup_old_logs'  # If implemented
        }
        
        for repo_name, method_name in cleanup_methods.items():
            try:
                repo = self.get_repository(repo_name)
                if hasattr(repo, method_name):
                    cleanup_method = getattr(repo, method_name)
                    cleaned_count = cleanup_method(days_to_keep)
                    
                    cleanup_results['cleanup_summary'][repo_name] = {
                        'records_cleaned': cleaned_count,
                        'days_to_keep': days_to_keep
                    }
                    cleanup_results['total_records_cleaned'] += cleaned_count
                    cleanup_results['repositories_cleaned'] += 1
                    
            except Exception as e:
                cleanup_results['cleanup_summary'][repo_name] = {'error': str(e)}
                logger.error(f"Failed to cleanup repository {repo_name}: {e}")
        
        return cleanup_results
    
    def get_repository_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about all repositories
        
        Returns:
            Repository information summary
        """
        info = {
            'repository_count': len(REPOSITORY_REGISTRY),
            'available_repositories': list(REPOSITORY_REGISTRY.keys()),
            'repository_categories': {
                'content_management': [
                    'content_fingerprint',
                    'content_metadata', 
                    'user_content',
                    'content_distribution',
                    'content_optimization'
                ],
                'protection_security': [
                    'protection_alert',
                    'audit_log'
                ],
                'analytics_insights': [
                    'social_media_analytics',
                    'audio_analytics',
                    'revenue_tracking'
                ],
                'ai_generation': [
                    'ai_content_generation',
                    'creator_profile'
                ],
                'business_logic': [
                    'monetization_rule',
                    'licensing_agreement',
                    'collaboration_request',
                    'platform_integration'
                ]
            },
            'initialized_repositories': list(self._initialized_repositories.keys()),
            'factory_info': {
                'class': self.factory.__class__.__name__,
                'session_info': str(self.db_session)
            }
        }
        
        return info

def initialize_repository_manager(db_session: Session) -> RepositoryManager:
    """
    Initialize repository manager with database session
    
    Args:
        db_session: SQLAlchemy database session
        
    Returns:
        Configured repository manager
    """
    manager = RepositoryManager(db_session)
    logger.info("Repository manager initialized successfully")
    return manager

# Quick access functions for common operations
def quick_health_check(db_session: Session) -> Dict[str, Any]:
    """Quick health check for all repositories"""
    manager = initialize_repository_manager(db_session)
    return manager.health_check_all()

def quick_statistics(db_session: Session) -> Dict[str, Any]:
    """Quick statistics from all repositories"""
    manager = initialize_repository_manager(db_session)
    return manager.get_all_statistics()

def quick_optimization(db_session: Session) -> Dict[str, Any]:
    """Quick optimization for all repositories"""
    manager = initialize_repository_manager(db_session)
    return manager.optimize_all_tables()

# Export main components
__all__ = [
    'RepositoryManager',
    'initialize_repository_manager',
    'quick_health_check',
    'quick_statistics', 
    'quick_optimization',
    # Re-export from main module
    'BaseRepository',
    'RepositoryException',
    'RepositoryFactory',
    'create_repository_factory',
    'REPOSITORY_REGISTRY'
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
