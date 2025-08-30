"""
🎮 Gamification Repository Index - IA Influencer Agent Platform Enterprise
===========================================================================
Module: backend/database/gamification/index.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Gamification Repository Registry - Production-Ready
Responsibility: Centralized repository management and dependency injection
============================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
Repository Registry → Dependency Injection → Factory Pattern → 
Service Integration → Configuration Management → Performance Optimization

GAMIFICATION INDEX ARCHITECTURE:
Repository Factory → Service Locator → Dependency Management → 
Configuration Registry → Connection Pooling → Performance Monitoring
"""

from typing import Dict, List, Optional, Any, Type, TypeVar
import logging
from dataclasses import dataclass
from enum import Enum
from contextlib import contextmanager

from .achievement_repository import AchievementRepository
from .challenge_repository import ChallengeRepository
from .leaderboard_repository import LeaderboardRepository
from .reward_repository import RewardRepository

T = TypeVar('T')

class GamificationRepositoryType(Enum):
    """Available gamification repository types"""
    ACHIEVEMENT = "achievement"
    CHALLENGE = "challenge"
    LEADERBOARD = "leaderboard"
    REWARD = "reward"

@dataclass
class RepositoryConfig:
    """Repository configuration"""
    repository_type: GamificationRepositoryType
    cache_enabled: bool = True
    cache_ttl: int = 300
    audit_enabled: bool = True
    metrics_enabled: bool = True
    batch_size: int = 1000
    connection_pool_size: int = 10
    retry_attempts: int = 3
    timeout_seconds: int = 30

class GamificationRepositoryRegistry:
    """Centralized registry for gamification repositories"""
    
    def __init__(self, db_connection=None, cache_manager=None,
                 analytics_service=None, notification_service=None,
                 payment_service=None, virtual_economy_service=None,
                 gamification_service=None, user_service=None,
                 reward_service=None):
        """Initialize repository registry with dependencies"""
        self.db_connection = db_connection
        self.cache_manager = cache_manager
        self.analytics_service = analytics_service
        self.notification_service = notification_service
        self.payment_service = payment_service
        self.virtual_economy_service = virtual_economy_service
        self.gamification_service = gamification_service
        self.user_service = user_service
        self.reward_service = reward_service
        
        self.logger = logging.getLogger(__name__)
        
        # Repository instances cache
        self._repository_cache: Dict[GamificationRepositoryType, Any] = {}
        
        # Repository configurations
        self._repository_configs: Dict[GamificationRepositoryType, RepositoryConfig] = {}
        
        # Repository class mappings
        self._repository_classes = {
            GamificationRepositoryType.ACHIEVEMENT: AchievementRepository,
            GamificationRepositoryType.CHALLENGE: ChallengeRepository,
            GamificationRepositoryType.LEADERBOARD: LeaderboardRepository,
            GamificationRepositoryType.REWARD: RewardRepository
        }
        
        # Initialize default configurations
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Initialize default repository configurations"""
        # Achievement repository config
        self._repository_configs[GamificationRepositoryType.ACHIEVEMENT] = RepositoryConfig(
            repository_type=GamificationRepositoryType.ACHIEVEMENT,
            cache_enabled=True,
            cache_ttl=600,  # 10 minutes for achievements
            audit_enabled=True,
            metrics_enabled=True,
            batch_size=500,
            connection_pool_size=15
        )
        
        # Challenge repository config
        self._repository_configs[GamificationRepositoryType.CHALLENGE] = RepositoryConfig(
            repository_type=GamificationRepositoryType.CHALLENGE,
            cache_enabled=True,
            cache_ttl=300,  # 5 minutes for challenges
            audit_enabled=True,
            metrics_enabled=True,
            batch_size=1000,
            connection_pool_size=20
        )
        
        # Leaderboard repository config
        self._repository_configs[GamificationRepositoryType.LEADERBOARD] = RepositoryConfig(
            repository_type=GamificationRepositoryType.LEADERBOARD,
            cache_enabled=True,
            cache_ttl=120,  # 2 minutes for leaderboards (frequent updates)
            audit_enabled=True,
            metrics_enabled=True,
            batch_size=2000,
            connection_pool_size=25
        )
        
        # Reward repository config
        self._repository_configs[GamificationRepositoryType.REWARD] = RepositoryConfig(
            repository_type=GamificationRepositoryType.REWARD,
            cache_enabled=True,
            cache_ttl=900,  # 15 minutes for rewards
            audit_enabled=True,
            metrics_enabled=True,
            batch_size=1500,
            connection_pool_size=20
        )
    
    def get_repository(
        self,
        repository_type: GamificationRepositoryType,
        force_new: bool = False
    ) -> Any:
        """Get repository instance with lazy loading"""
        try:
            # Return cached instance if available and not forcing new
            if not force_new and repository_type in self._repository_cache:
                return self._repository_cache[repository_type]
            
            # Get repository class
            repository_class = self._repository_classes.get(repository_type)
            if not repository_class:
                raise ValueError(f"Unknown repository type: {repository_type}")
            
            # Get configuration
            config = self._repository_configs.get(repository_type)
            if not config:
                raise ValueError(f"No configuration found for: {repository_type}")
            
            # Create repository instance with appropriate dependencies
            repository = self._create_repository_instance(repository_class, config)
            
            # Cache instance
            self._repository_cache[repository_type] = repository
            
            self.logger.info(f"Repository created: {repository_type.value}")
            return repository
            
        except Exception as e:
            self.logger.error(f"Failed to get repository {repository_type.value}: {str(e)}")
            raise
    
    def _create_repository_instance(self, repository_class: Type[T], config: RepositoryConfig) -> T:
        """Create repository instance with dependency injection"""
        kwargs = {
            "db_connection": self.db_connection,
            "cache_manager": self.cache_manager
        }
        
        # Add specific dependencies based on repository type
        if repository_class == AchievementRepository:
            kwargs.update({
                "analytics_service": self.analytics_service,
                "notification_service": self.notification_service,
                "gamification_service": self.gamification_service
            })
        
        elif repository_class == ChallengeRepository:
            kwargs.update({
                "analytics_service": self.analytics_service,
                "notification_service": self.notification_service,
                "reward_service": self.reward_service,
                "gamification_service": self.gamification_service
            })
        
        elif repository_class == LeaderboardRepository:
            kwargs.update({
                "analytics_service": self.analytics_service,
                "notification_service": self.notification_service,
                "user_service": self.user_service,
                "gamification_service": self.gamification_service
            })
        
        elif repository_class == RewardRepository:
            kwargs.update({
                "analytics_service": self.analytics_service,
                "notification_service": self.notification_service,
                "payment_service": self.payment_service,
                "virtual_economy_service": self.virtual_economy_service,
                "gamification_service": self.gamification_service
            })
        
        # Create instance
        repository = repository_class(**kwargs)
        
        # Apply configuration
        self._apply_repository_config(repository, config)
        
        return repository
    
    def _apply_repository_config(self, repository: Any, config: RepositoryConfig):
        """Apply configuration to repository instance"""
        try:
            # Configure cache settings
            if hasattr(repository, 'with_cache'):
                repository.with_cache(config.cache_enabled, config.cache_ttl)
            
            # Configure audit settings
            if hasattr(repository, 'with_audit'):
                repository.with_audit(config.audit_enabled)
            
            # Configure batch size
            if hasattr(repository, 'with_batch_size'):
                repository.with_batch_size(config.batch_size)
            
            # Configure performance thresholds
            if hasattr(repository, '_performance_threshold'):
                repository._performance_threshold = config.timeout_seconds / 10.0
            
        except Exception as e:
            self.logger.warning(f"Failed to apply some configuration settings: {str(e)}")
    
    def get_achievement_repository(self) -> AchievementRepository:
        """Get achievement repository instance"""
        return self.get_repository(GamificationRepositoryType.ACHIEVEMENT)
    
    def get_challenge_repository(self) -> ChallengeRepository:
        """Get challenge repository instance"""
        return self.get_repository(GamificationRepositoryType.CHALLENGE)
    
    def get_leaderboard_repository(self) -> LeaderboardRepository:
        """Get leaderboard repository instance"""
        return self.get_repository(GamificationRepositoryType.LEADERBOARD)
    
    def get_reward_repository(self) -> RewardRepository:
        """Get reward repository instance"""
        return self.get_repository(GamificationRepositoryType.REWARD)
    
    def configure_repository(
        self,
        repository_type: GamificationRepositoryType,
        config: RepositoryConfig
    ):
        """Configure specific repository"""
        try:
            self._repository_configs[repository_type] = config
            
            # Clear cached instance to force reconfiguration
            if repository_type in self._repository_cache:
                del self._repository_cache[repository_type]
            
            self.logger.info(f"Repository configured: {repository_type.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to configure repository: {str(e)}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all repositories"""
        health_status = {
            "overall_status": "healthy",
            "repositories": {},
            "timestamp": "2025-01-01T00:00:00Z"
        }
        
        try:
            for repo_type in GamificationRepositoryType:
                try:
                    repository = self.get_repository(repo_type)
                    
                    # Basic connectivity test
                    if hasattr(repository, 'list_all'):
                        repository.list_all(limit=1)
                    
                    health_status["repositories"][repo_type.value] = {
                        "status": "healthy",
                        "cached": repo_type in self._repository_cache,
                        "config": self._repository_configs.get(repo_type).__dict__ if repo_type in self._repository_configs else None
                    }
                    
                except Exception as e:
                    health_status["repositories"][repo_type.value] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
                    health_status["overall_status"] = "degraded"
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                "overall_status": "unhealthy",
                "error": str(e),
                "timestamp": "2025-01-01T00:00:00Z"
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all repositories"""
        metrics = {
            "repository_count": len(self._repository_cache),
            "cached_repositories": list(self._repository_cache.keys()),
            "configurations": {
                repo_type.value: config.__dict__ 
                for repo_type, config in self._repository_configs.items()
            },
            "memory_usage": self._calculate_memory_usage(),
            "connection_stats": self._get_connection_stats()
        }
        
        return metrics
    
    def _calculate_memory_usage(self) -> Dict[str, Any]:
        """Calculate memory usage statistics"""
        # Simplified memory calculation
        return {
            "cached_instances": len(self._repository_cache),
            "estimated_memory_mb": len(self._repository_cache) * 0.5  # Rough estimate
        }
    
    def _get_connection_stats(self) -> Dict[str, Any]:
        """Get database connection statistics"""
        # Would integrate with actual connection pool stats
        return {
            "total_configured_connections": sum(
                config.connection_pool_size for config in self._repository_configs.values()
            ),
            "active_connections": "N/A",  # Would get from actual pool
            "connection_utilization": "N/A"  # Would calculate from actual stats
        }
    
    @contextmanager
    def transaction_scope(self, *repository_types: GamificationRepositoryType):
        """Provide transactional scope for multiple repositories"""
        repositories = []
        try:
            # Get all requested repositories
            for repo_type in repository_types:
                repositories.append(self.get_repository(repo_type))
            
            # Begin transaction (would integrate with actual transaction management)
            self.logger.info(f"Transaction started for: {[rt.value for rt in repository_types]}")
            
            yield repositories
            
            # Commit transaction
            self.logger.info("Transaction committed")
            
        except Exception as e:
            # Rollback transaction
            self.logger.error(f"Transaction rolled back: {str(e)}")
            raise
        finally:
            # Cleanup
            pass
    
    def clear_cache(self, repository_type: Optional[GamificationRepositoryType] = None):
        """Clear repository cache"""
        try:
            if repository_type:
                if repository_type in self._repository_cache:
                    del self._repository_cache[repository_type]
                    self.logger.info(f"Cache cleared for: {repository_type.value}")
            else:
                self._repository_cache.clear()
                self.logger.info("All repository cache cleared")
                
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {str(e)}")
    
    def shutdown(self):
        """Graceful shutdown of all repositories"""
        try:
            for repo_type, repository in self._repository_cache.items():
                if hasattr(repository, 'close'):
                    repository.close()
                self.logger.info(f"Repository shutdown: {repo_type.value}")
            
            self._repository_cache.clear()
            self.logger.info("All repositories shutdown successfully")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")


# Factory function for easy registry creation
def create_gamification_registry(
    db_connection=None,
    cache_manager=None,
    analytics_service=None,
    notification_service=None,
    payment_service=None,
    virtual_economy_service=None,
    gamification_service=None,
    user_service=None,
    reward_service=None
) -> GamificationRepositoryRegistry:
    """Factory function to create configured gamification repository registry"""
    return GamificationRepositoryRegistry(
        db_connection=db_connection,
        cache_manager=cache_manager,
        analytics_service=analytics_service,
        notification_service=notification_service,
        payment_service=payment_service,
        virtual_economy_service=virtual_economy_service,
        gamification_service=gamification_service,
        user_service=user_service,
        reward_service=reward_service
    )


# Default registry instance (singleton pattern)
_default_registry: Optional[GamificationRepositoryRegistry] = None

def get_default_registry() -> GamificationRepositoryRegistry:
    """Get default registry instance"""
    global _default_registry
    if _default_registry is None:
        _default_registry = create_gamification_registry()
    return _default_registry

def set_default_registry(registry: GamificationRepositoryRegistry):
    """Set default registry instance"""
    global _default_registry
    _default_registry = registry

# Convenience functions
def get_achievement_repository() -> AchievementRepository:
    """Get achievement repository from default registry"""
    return get_default_registry().get_achievement_repository()

def get_challenge_repository() -> ChallengeRepository:
    """Get challenge repository from default registry"""
    return get_default_registry().get_challenge_repository()

def get_leaderboard_repository() -> LeaderboardRepository:
    """Get leaderboard repository from default registry"""
    return get_default_registry().get_leaderboard_repository()

def get_reward_repository() -> RewardRepository:
    """Get reward repository from default registry"""
    return get_default_registry().get_reward_repository()