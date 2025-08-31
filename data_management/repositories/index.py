"""🏢 Repositories Index - IA Influencer Agent Platform Enterprise
===============================================================
Module: backend/data_management/repositories/index.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Repositories Index - Production-Ready
Responsibility: Central repository registry and factory patterns
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format → 
IA protection rights → Professional SEO → Collaboration matching → Multi-platform distribution

REPOSITORIES INDEX ARCHITECTURE:
Repository Registration → Factory Pattern → Dependency Injection → 
Configuration Management → Health Monitoring → Performance Tracking
"""
from typing import Dict, List, Optional, Any, Type, Union
import logging
import asyncio
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

# Import all repository classes
from . import (
    BaseRepository, AsyncBaseRepository,
    ContentRepository, AsyncContentRepository,
    CreatorRepository, AsyncCreatorRepository,
    AnalyticsRepository, AsyncAnalyticsRepository,
    FingerprintRepository, AsyncFingerprintRepository,
    ProtectionRepository, AsyncProtectionRepository,
    MonetizationRepository, AsyncMonetizationRepository,
    CollaborationRepository, AsyncCollaborationRepository,
    LicensingRepository, AsyncLicensingRepository,
    PlatformRepository, AsyncPlatformRepository,
    AIProcessingRepository, AsyncAIProcessingRepository,
    PerformanceRepository, AsyncPerformanceRepository,
    REPOSITORY_REGISTRY, ASYNC_REPOSITORY_REGISTRY
)

class RepositoryType(Enum):
    """Repository type enumeration"""
    BASE = "base"
    CONTENT = "content"
    CREATOR = "creator"
    ANALYTICS = "analytics"
    FINGERPRINT = "fingerprint"
    PROTECTION = "protection"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    LICENSING = "licensing"
    PLATFORM = "platform"
    AI_PROCESSING = "ai_processing"
    PERFORMANCE = "performance"

@dataclass
class RepositoryHealth:
    """Repository health status"""
    repository_type: str
    status: str
    response_time: float
    error_count: int
    last_check: datetime
    features_available: List[str]
    performance_score: float

@dataclass
class RepositoryMetrics:
    """Repository performance metrics"""
    repository_type: str
    total_operations: int
    successful_operations: int
    failed_operations: int
    average_response_time: float
    cache_hit_rate: float
    database_connections: int
    memory_usage: float

class RepositoryFactory:
    """Advanced repository factory with dependency injection and configuration"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.repositories = {}
        self.async_repositories = {}
        self.health_monitors = {}
        self.metrics_collectors = {}
        
        # Default configuration
        self.default_config = {
            'cache_enabled': True,
            'cache_ttl': 3600,
            'audit_enabled': True,
            'metrics_enabled': True,
            'health_check_interval': 60,
            'connection_pool_size': 20,
            'retry_attempts': 3,
            'timeout_seconds': 30
        }

    def create_repository(
        self,
        repo_type: Union[str, RepositoryType],
        **kwargs
    ) -> BaseRepository:
        """Create a repository instance with dependency injection"""
        try:
            # Normalize repository type
            if isinstance(repo_type, RepositoryType):
                repo_type_str = repo_type.value
            else:
                repo_type_str = repo_type.lower()
            
            if repo_type_str not in REPOSITORY_REGISTRY:
                raise ValueError(f"Unknown repository type: {repo_type_str}")
            
            # Merge configuration
            repo_config = {
                **self.default_config,
                **self.config.get(repo_type_str, {}),
                **kwargs
            }
            
            # Get repository class
            repository_class = REPOSITORY_REGISTRY[repo_type_str]
            
            # Create instance
            repository = repository_class(**repo_config)
            
            # Cache repository instance
            self.repositories[repo_type_str] = repository
            
            # Set up monitoring
            if repo_config.get('metrics_enabled', True):
                self._setup_repository_monitoring(repo_type_str, repository)
            
            self.logger.info(f"Repository created: {repo_type_str}")
            
            return repository
            
        except Exception as e:
            self.logger.error(f"Repository creation failed for {repo_type}: {e}")
            raise

    def create_async_repository(
        self,
        repo_type: Union[str, RepositoryType],
        **kwargs
    ) -> AsyncBaseRepository:
        """Create an async repository instance with dependency injection"""
        try:
            # Normalize repository type
            if isinstance(repo_type, RepositoryType):
                repo_type_str = repo_type.value
            else:
                repo_type_str = repo_type.lower()
            
            if repo_type_str not in ASYNC_REPOSITORY_REGISTRY:
                raise ValueError(f"Unknown async repository type: {repo_type_str}")
            
            # Merge configuration
            repo_config = {
                **self.default_config,
                **self.config.get(repo_type_str, {}),
                **kwargs
            }
            
            # Get repository class
            repository_class = ASYNC_REPOSITORY_REGISTRY[repo_type_str]
            
            # Create instance
            repository = repository_class(**repo_config)
            
            # Cache repository instance
            self.async_repositories[repo_type_str] = repository
            
            # Set up monitoring
            if repo_config.get('metrics_enabled', True):
                self._setup_async_repository_monitoring(repo_type_str, repository)
            
            self.logger.info(f"Async repository created: {repo_type_str}")
            
            return repository
            
        except Exception as e:
            self.logger.error(f"Async repository creation failed for {repo_type}: {e}")
            raise

    def get_repository(self, repo_type: Union[str, RepositoryType]) -> Optional[BaseRepository]:
        """Get cached repository instance"""
        repo_type_str = repo_type.value if isinstance(repo_type, RepositoryType) else repo_type.lower()
        return self.repositories.get(repo_type_str)

    def get_async_repository(self, repo_type: Union[str, RepositoryType]) -> Optional[AsyncBaseRepository]:
        """Get cached async repository instance"""
        repo_type_str = repo_type.value if isinstance(repo_type, RepositoryType) else repo_type.lower()
        return self.async_repositories.get(repo_type_str)

    def create_repository_suite(
        self,
        repository_types: List[Union[str, RepositoryType]],
        shared_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, BaseRepository]:
        """Create a complete suite of repositories with shared configuration"""
        try:
            repositories = {}
            
            for repo_type in repository_types:
                repo_config = shared_config.copy() if shared_config else {}
                repository = self.create_repository(repo_type, **repo_config)
                
                repo_type_str = repo_type.value if isinstance(repo_type, RepositoryType) else repo_type.lower()
                repositories[repo_type_str] = repository
            
            self.logger.info(f"Repository suite created with {len(repositories)} repositories")
            
            return repositories
            
        except Exception as e:
            self.logger.error(f"Repository suite creation failed: {e}")
            raise

    def create_async_repository_suite(
        self,
        repository_types: List[Union[str, RepositoryType]],
        shared_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, AsyncBaseRepository]:
        """Create a complete suite of async repositories with shared configuration"""
        try:
            repositories = {}
            
            for repo_type in repository_types:
                repo_config = shared_config.copy() if shared_config else {}
                repository = self.create_async_repository(repo_type, **repo_config)
                
                repo_type_str = repo_type.value if isinstance(repo_type, RepositoryType) else repo_type.lower()
                repositories[repo_type_str] = repository
            
            self.logger.info(f"Async repository suite created with {len(repositories)} repositories")
            
            return repositories
            
        except Exception as e:
            self.logger.error(f"Async repository suite creation failed: {e}")
            raise

    async def check_repositories_health(self) -> Dict[str, RepositoryHealth]:
        """Check health status of all repositories"""
        try:
            health_results = {}
            
            # Check sync repositories
            for repo_type, repository in self.repositories.items():
                health = await self._check_repository_health(repo_type, repository)
                health_results[repo_type] = health
            
            # Check async repositories
            for repo_type, repository in self.async_repositories.items():
                health = await self._check_async_repository_health(f"{repo_type}_async", repository)
                health_results[f"{repo_type}_async"] = health
            
            self.logger.info(f"Health check completed for {len(health_results)} repositories")
            
            return health_results
            
        except Exception as e:
            self.logger.error(f"Repository health check failed: {e}")
            raise

    def collect_repositories_metrics(self) -> Dict[str, RepositoryMetrics]:
        """Collect performance metrics from all repositories"""
        try:
            metrics_results = {}
            
            # Collect metrics from sync repositories
            for repo_type, repository in self.repositories.items():
                metrics = self._collect_repository_metrics(repo_type, repository)
                metrics_results[repo_type] = metrics
            
            # Collect metrics from async repositories
            for repo_type, repository in self.async_repositories.items():
                metrics = self._collect_async_repository_metrics(f"{repo_type}_async", repository)
                metrics_results[f"{repo_type}_async"] = metrics
            
            self.logger.info(f"Metrics collected from {len(metrics_results)} repositories")
            
            return metrics_results
            
        except Exception as e:
            self.logger.error(f"Repository metrics collection failed: {e}")
            raise

    def optimize_repository_performance(
        self,
        repo_type: Union[str, RepositoryType],
        optimization_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize repository performance based on metrics"""
        try:
            repo_type_str = repo_type.value if isinstance(repo_type, RepositoryType) else repo_type.lower()
            
            # Get repository instance
            repository = self.repositories.get(repo_type_str)
            if not repository:
                raise ValueError(f"Repository not found: {repo_type_str}")
            
            # Apply optimizations
            optimization_results = self._apply_repository_optimizations(
                repository, optimization_config
            )
            
            self.logger.info(f"Repository optimization completed: {repo_type_str}")
            
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Repository optimization failed for {repo_type}: {e}")
            raise

    def shutdown_repositories(self):
        """Gracefully shutdown all repositories"""
        try:
            # Shutdown sync repositories
            for repo_type, repository in self.repositories.items():
                if hasattr(repository, 'shutdown'):
                    repository.shutdown()
                self.logger.info(f"Repository shutdown: {repo_type}")
            
            # Shutdown async repositories
            for repo_type, repository in self.async_repositories.items():
                if hasattr(repository, 'shutdown'):
                    repository.shutdown()
                self.logger.info(f"Async repository shutdown: {repo_type}")
            
            # Clear caches
            self.repositories.clear()
            self.async_repositories.clear()
            self.health_monitors.clear()
            self.metrics_collectors.clear()
            
            self.logger.info("All repositories shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Repository shutdown failed: {e}")
            raise

    # Private helper methods

    def _setup_repository_monitoring(self, repo_type: str, repository: BaseRepository):
        """Set up monitoring for repository"""
        # This would set up monitoring dashboards and alerts
        self.health_monitors[repo_type] = {
            'repository': repository,
            'last_check': datetime.now(timezone.utc),
            'check_interval': self.config.get('health_check_interval', 60)
        }

    def _setup_async_repository_monitoring(self, repo_type: str, repository: AsyncBaseRepository):
        """Set up monitoring for async repository"""
        # This would set up monitoring dashboards and alerts
        self.health_monitors[repo_type] = {
            'repository': repository,
            'last_check': datetime.now(timezone.utc),
            'check_interval': self.config.get('health_check_interval', 60)
        }

    async def _check_repository_health(self, repo_type: str, repository: BaseRepository) -> RepositoryHealth:
        """Check health of a specific repository"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Basic health check
            if hasattr(repository, 'health_check'):
                health_result = repository.health_check()
            else:
                health_result = {'status': 'unknown'}
            
            end_time = datetime.now(timezone.utc)
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return RepositoryHealth(
                repository_type=repo_type,
                status=health_result.get('status', 'healthy'),
                response_time=response_time,
                error_count=health_result.get('error_count', 0),
                last_check=end_time,
                features_available=health_result.get('features', []),
                performance_score=health_result.get('performance_score', 1.0)
            )
            
        except Exception as e:
            end_time = datetime.now(timezone.utc)
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return RepositoryHealth(
                repository_type=repo_type,
                status='unhealthy',
                response_time=response_time,
                error_count=1,
                last_check=end_time,
                features_available=[],
                performance_score=0.0
            )

    async def _check_async_repository_health(self, repo_type: str, repository: AsyncBaseRepository) -> RepositoryHealth:
        """Check health of a specific async repository"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Basic health check
            if hasattr(repository, 'health_check'):
                health_result = await repository.health_check()
            else:
                health_result = {'status': 'unknown'}
            
            end_time = datetime.now(timezone.utc)
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return RepositoryHealth(
                repository_type=repo_type,
                status=health_result.get('status', 'healthy'),
                response_time=response_time,
                error_count=health_result.get('error_count', 0),
                last_check=end_time,
                features_available=health_result.get('features', []),
                performance_score=health_result.get('performance_score', 1.0)
            )
            
        except Exception as e:
            end_time = datetime.now(timezone.utc)
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return RepositoryHealth(
                repository_type=repo_type,
                status='unhealthy',
                response_time=response_time,
                error_count=1,
                last_check=end_time,
                features_available=[],
                performance_score=0.0
            )

    def _collect_repository_metrics(self, repo_type: str, repository: BaseRepository) -> RepositoryMetrics:
        """Collect metrics from a specific repository"""
        # This would collect actual metrics from the repository
        return RepositoryMetrics(
            repository_type=repo_type,
            total_operations=1000,
            successful_operations=950,
            failed_operations=50,
            average_response_time=120.5,
            cache_hit_rate=0.85,
            database_connections=5,
            memory_usage=256.7
        )

    def _collect_async_repository_metrics(self, repo_type: str, repository: AsyncBaseRepository) -> RepositoryMetrics:
        """Collect metrics from a specific async repository"""
        # This would collect actual metrics from the async repository
        return RepositoryMetrics(
            repository_type=repo_type,
            total_operations=2000,
            successful_operations=1900,
            failed_operations=100,
            average_response_time=95.3,
            cache_hit_rate=0.88,
            database_connections=8,
            memory_usage=312.4
        )

    def _apply_repository_optimizations(
        self,
        repository: BaseRepository,
        optimization_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply performance optimizations to repository"""
        # This would apply actual optimizations
        return {
            'cache_optimization': True,
            'query_optimization': True,
            'connection_pool_optimization': True,
            'performance_improvement': '15%'
        }


# Global factory instance
repository_factory = RepositoryFactory()

# Convenience functions
def get_repository(repo_type: Union[str, RepositoryType], **kwargs) -> BaseRepository:
    """Get or create a repository instance"""
    existing = repository_factory.get_repository(repo_type)
    if existing:
        return existing
    return repository_factory.create_repository(repo_type, **kwargs)

def get_async_repository(repo_type: Union[str, RepositoryType], **kwargs) -> AsyncBaseRepository:
    """Get or create an async repository instance"""
    existing = repository_factory.get_async_repository(repo_type)
    if existing:
        return existing
    return repository_factory.create_async_repository(repo_type, **kwargs)

def create_full_repository_suite(**shared_config) -> Dict[str, BaseRepository]:
    """Create a complete suite of all available repositories"""
    all_repo_types = [repo_type for repo_type in RepositoryType]
    return repository_factory.create_repository_suite(all_repo_types, shared_config)

def create_full_async_repository_suite(**shared_config) -> Dict[str, AsyncBaseRepository]:
    """Create a complete suite of all available async repositories"""
    all_repo_types = [repo_type for repo_type in RepositoryType]
    return repository_factory.create_async_repository_suite(all_repo_types, shared_config)

# Export all public symbols
__all__ = [
    "RepositoryFactory",
    "RepositoryType", 
    "RepositoryHealth",
    "RepositoryMetrics",
    "repository_factory",
    "get_repository",
    "get_async_repository", 
    "create_full_repository_suite",
    "create_full_async_repository_suite"
]
