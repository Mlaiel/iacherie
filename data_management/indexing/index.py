"""
IA Influencer Agent - Main Indexing Orchestrator
===============================================

Main orchestration module for the enterprise indexing system,
coordinating all components: engines, processors, security, monitoring, etc.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Content Protection Platform

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or reproduction
without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from redis.asyncio import Redis

# Import all components
from .engines import (
    VectorSearchEngine, ContentIndexEngine, 
    FingerprintIndexEngine, MetadataIndexEngine, IndexingConfig
)
from .processors import (
    MultiFormatProcessor, ProcessingConfig
)
from .services import (
    IndexingService, SearchService, VectorService, RealtimeIndexService,
    IndexingRequest, SearchRequest
)
from .monitoring import (
    MetricsCollector, AlertManager, PerformanceAnalyzer,
    PerformanceMetrics, AlertRule, AlertLevel
)
from .analytics import (
    ContentAnalyticsEngine, SearchAnalyticsEngine, VisualizationEngine
)
from .optimization import (
    OptimizationEngine, OptimizationConfig, OptimizationStrategy
)
from .security import (
    EncryptionManager, AccessControlManager, AuditLogger, ThreatDetector,
    SecurityConfig, SecurityLevel, AccessType
)

logger = logging.getLogger(__name__)


@dataclass
class SystemConfig:
    """Main system configuration"""
    # Core settings
    redis_url: str = "redis://localhost:6379"
    elasticsearch_hosts: List[str] = None
    enable_gpu: bool = True
    debug_mode: bool = False
    
    # Component configurations
    indexing_config: IndexingConfig = None
    processing_config: ProcessingConfig = None
    optimization_config: OptimizationConfig = None
    security_config: SecurityConfig = None
    
    # Feature flags
    enable_monitoring: bool = True
    enable_analytics: bool = True
    enable_optimization: bool = True
    enable_security: bool = True
    enable_real_time: bool = True


class IndexingOrchestrator:
    """Main orchestrator for the entire indexing system"""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.redis_client = None
        self.initialized = False
        self.start_time = None
        
        # Core components
        self.engines = {}
        self.processors = None
        self.services = {}
        
        # Advanced components
        self.monitoring_system = {}
        self.analytics_system = {}
        self.optimization_system = None
        self.security_system = {}
        
        # Status tracking
        self.component_status = {}
        self.health_checks = {}
        
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the complete indexing system"""
        try:
            self.start_time = datetime.now(timezone.utc)
            logger.info("🚀 Starting IA Influencer Agent Indexing System initialization...")
            
            # Initialize Redis connection
            await self._initialize_redis()
            
            # Initialize core components
            await self._initialize_core_engines()
            await self._initialize_processors()
            await self._initialize_services()
            
            # Initialize advanced components
            if self.config.enable_monitoring:
                await self._initialize_monitoring()
            
            if self.config.enable_analytics:
                await self._initialize_analytics()
            
            if self.config.enable_optimization:
                await self._initialize_optimization()
            
            if self.config.enable_security:
                await self._initialize_security()
            
            # Setup default configurations
            await self._setup_default_configurations()
            
            # Run initial health checks
            health_status = await self.health_check()
            
            self.initialized = True
            
            initialization_time = (datetime.now(timezone.utc) - self.start_time).total_seconds()
            
            logger.info(f"✅ IA Influencer Agent Indexing System initialized successfully in {initialization_time:.2f}s")
            
            return {
                "status": "initialized",
                "initialization_time_seconds": initialization_time,
                "components_initialized": list(self.component_status.keys()),
                "health_status": health_status,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize IndexingOrchestrator: {e}")
            raise
    
    async def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = Redis.from_url(self.config.redis_url)
            await self.redis_client.ping()
            self.component_status["redis"] = "initialized"
            logger.info("✅ Redis connection established")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Redis: {e}")
            raise
    
    async def _initialize_core_engines(self):
        """Initialize core indexing engines"""
        try:
            # Default indexing config if not provided
            indexing_config = self.config.indexing_config or IndexingConfig(
                elasticsearch_hosts=self.config.elasticsearch_hosts or ["localhost:9200"],
                redis_url=self.config.redis_url,
                enable_gpu=self.config.enable_gpu
            )
            
            # Initialize engines
            self.engines["vector_search"] = VectorSearchEngine(indexing_config)
            await self.engines["vector_search"].initialize()
            
            self.engines["content_index"] = ContentIndexEngine(indexing_config)
            await self.engines["content_index"].initialize()
            
            self.engines["fingerprint_index"] = FingerprintIndexEngine(indexing_config)
            await self.engines["fingerprint_index"].initialize()
            
            self.engines["metadata_index"] = MetadataIndexEngine(indexing_config)
            await self.engines["metadata_index"].initialize()
            
            self.component_status["engines"] = "initialized"
            logger.info("✅ Core indexing engines initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize core engines: {e}")
            raise
    
    async def _initialize_processors(self):
        """Initialize content processors"""
        try:
            processing_config = self.config.processing_config or ProcessingConfig(
                enable_gpu=self.config.enable_gpu
            )
            
            self.processors = MultiFormatProcessor(processing_config)
            await self.processors.initialize()
            
            self.component_status["processors"] = "initialized"
            logger.info("✅ Content processors initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize processors: {e}")
            raise
    
    async def _initialize_services(self):
        """Initialize business services"""
        try:
            # Initialize main services
            self.services["indexing"] = IndexingService(
                self.config.indexing_config or IndexingConfig(),
                self.config.processing_config or ProcessingConfig()
            )
            await self.services["indexing"].initialize()
            
            self.services["search"] = SearchService(
                self.config.indexing_config or IndexingConfig()
            )
            await self.services["search"].initialize()
            
            self.services["vector"] = VectorService(
                self.config.indexing_config or IndexingConfig()
            )
            await self.services["vector"].initialize()
            
            if self.config.enable_real_time:
                self.services["realtime"] = RealtimeIndexService(
                    self.config.indexing_config or IndexingConfig()
                )
                await self.services["realtime"].initialize()
            
            self.component_status["services"] = "initialized"
            logger.info("✅ Business services initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize services: {e}")
            raise
    
    async def _initialize_monitoring(self):
        """Initialize monitoring system"""
        try:
            # Metrics collector
            self.monitoring_system["metrics"] = MetricsCollector(
                self.config.redis_url
            )
            await self.monitoring_system["metrics"].initialize()
            
            # Alert manager
            self.monitoring_system["alerts"] = AlertManager(
                self.config.redis_url,
                {"email": {}, "slack": {}, "webhook": {}}
            )
            await self.monitoring_system["alerts"].initialize()
            
            # Performance analyzer
            self.monitoring_system["performance"] = PerformanceAnalyzer(
                self.monitoring_system["metrics"]
            )
            
            # Setup default alert rules
            await self._setup_default_alert_rules()
            
            self.component_status["monitoring"] = "initialized"
            logger.info("✅ Monitoring system initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize monitoring: {e}")
            raise
    
    async def _initialize_analytics(self):
        """Initialize analytics system"""
        try:
            self.analytics_system["content"] = ContentAnalyticsEngine(
                self.config.redis_url
            )
            await self.analytics_system["content"].initialize()
            
            self.analytics_system["search"] = SearchAnalyticsEngine(
                self.config.redis_url
            )
            await self.analytics_system["search"].initialize()
            
            self.analytics_system["visualization"] = VisualizationEngine()
            
            self.component_status["analytics"] = "initialized"
            logger.info("✅ Analytics system initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize analytics: {e}")
            raise
    
    async def _initialize_optimization(self):
        """Initialize optimization system"""
        try:
            optimization_config = self.config.optimization_config or OptimizationConfig(
                strategy=OptimizationStrategy.BALANCED,
                auto_scaling_enabled=True
            )
            
            self.optimization_system = OptimizationEngine(
                optimization_config,
                self.config.redis_url
            )
            await self.optimization_system.initialize()
            
            self.component_status["optimization"] = "initialized"
            logger.info("✅ Optimization system initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize optimization: {e}")
            raise
    
    async def _initialize_security(self):
        """Initialize security system"""
        try:
            security_config = self.config.security_config or SecurityConfig()
            
            # Encryption manager
            self.security_system["encryption"] = EncryptionManager(security_config)
            await self.security_system["encryption"].initialize()
            
            # Access control manager
            self.security_system["access_control"] = AccessControlManager(
                security_config, self.redis_client
            )
            
            # Audit logger
            self.security_system["audit"] = AuditLogger(
                security_config, self.redis_client
            )
            
            # Threat detector
            self.security_system["threat_detection"] = ThreatDetector(
                security_config, self.redis_client
            )
            
            # Create default admin user
            await self._create_default_admin_user()
            
            self.component_status["security"] = "initialized"
            logger.info("✅ Security system initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize security: {e}")
            raise
    
    async def _setup_default_configurations(self):
        """Setup default system configurations"""
        try:
            # Store system configuration
            await self.redis_client.set(
                "system_config",
                json.dumps(asdict(self.config), default=str)
            )
            
            # Store component status
            await self.redis_client.hset(
                "component_status",
                mapping=self.component_status
            )
            
            # Store initialization metadata
            init_metadata = {
                "initialized_at": datetime.now(timezone.utc).isoformat(),
                "version": "2.0.0",
                "author": "Fahed Mlaiel",
                "components": list(self.component_status.keys())
            }
            
            await self.redis_client.set(
                "system_metadata",
                json.dumps(init_metadata)
            )
            
            logger.info("✅ Default configurations set up")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup default configurations: {e}")
            raise
    
    async def _setup_default_alert_rules(self):
        """Setup default monitoring alert rules"""
        if "alerts" not in self.monitoring_system:
            return
        
        try:
            alert_manager = self.monitoring_system["alerts"]
            
            # High CPU usage alert
            await alert_manager.add_alert_rule(AlertRule(
                name="high_cpu_usage",
                metric_name="cpu_usage_percent",
                threshold=85.0,
                comparison=">",
                window_minutes=5,
                level=AlertLevel.WARNING,
                notification_channels=["email"]
            ))
            
            # High memory usage alert
            await alert_manager.add_alert_rule(AlertRule(
                name="high_memory_usage",
                metric_name="memory_usage_mb",
                threshold=80.0,
                comparison=">",
                window_minutes=5,
                level=AlertLevel.WARNING,
                notification_channels=["email"]
            ))
            
            # Low cache hit rate alert
            await alert_manager.add_alert_rule(AlertRule(
                name="low_cache_hit_rate",
                metric_name="cache_hit_rate",
                threshold=0.7,
                comparison="<",
                window_minutes=10,
                level=AlertLevel.WARNING,
                notification_channels=["email"]
            ))
            
            # High error rate alert
            await alert_manager.add_alert_rule(AlertRule(
                name="high_error_rate",
                metric_name="success_rate_percent",
                threshold=95.0,
                comparison="<",
                window_minutes=5,
                level=AlertLevel.ERROR,
                notification_channels=["email", "slack"]
            ))
            
            logger.info("✅ Default alert rules configured")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup alert rules: {e}")
    
    async def _create_default_admin_user(self):
        """Create default admin user for system access"""
        if "access_control" not in self.security_system:
            return
        
        try:
            access_control = self.security_system["access_control"]
            
            # Create admin user
            admin_user_id = await access_control.create_user(
                username="admin",
                password="IA_Influencer_Admin_2025!",  # Should be changed in production
                roles=["admin"],
                email="mlaiel@live.de"
            )
            
            logger.info(f"✅ Default admin user created: {admin_user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create admin user: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive system health check"""
        try:
            health_status = {
                "overall_status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds() if self.start_time else 0,
                "components": {}
            }
            
            # Check Redis connection
            try:
                await self.redis_client.ping()
                health_status["components"]["redis"] = "healthy"
            except:
                health_status["components"]["redis"] = "unhealthy"
                health_status["overall_status"] = "degraded"
            
            # Check engines
            for name, engine in self.engines.items():
                try:
                    engine_health = await engine.health_check()
                    health_status["components"][f"engine_{name}"] = engine_health.get("status", "unknown")
                except:
                    health_status["components"][f"engine_{name}"] = "unhealthy"
                    health_status["overall_status"] = "degraded"
            
            # Check services
            for name, service in self.services.items():
                try:
                    if hasattr(service, 'health_check'):
                        service_health = await service.health_check()
                        health_status["components"][f"service_{name}"] = service_health.get("status", "healthy")
                    else:
                        health_status["components"][f"service_{name}"] = "healthy"
                except:
                    health_status["components"][f"service_{name}"] = "unhealthy"
                    health_status["overall_status"] = "degraded"
            
            # Check component initialization status
            for component, status in self.component_status.items():
                if status != "initialized":
                    health_status["overall_status"] = "degraded"
            
            self.health_checks[datetime.now(timezone.utc).isoformat()] = health_status
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                "overall_status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def index_content(self, request: IndexingRequest) -> Dict[str, Any]:
        """Main entry point for content indexing"""
        try:
            if not self.initialized:
                raise RuntimeError("System not initialized")
            
            # Security check
            if self.config.enable_security and "access_control" in self.security_system:
                # This would normally check user authentication
                pass
            
            # Record metrics
            start_time = time.time()
            
            # Process through indexing service
            result = await self.services["indexing"].index_content(request)
            
            # Record performance metrics
            if self.config.enable_monitoring and "metrics" in self.monitoring_system:
                processing_time = (time.time() - start_time) * 1000
                await self.monitoring_system["metrics"].record_operation(
                    operation_type="indexing",
                    content_type=request.content_type or "unknown",
                    processing_time_ms=processing_time,
                    success=result.success,
                    creator_id=request.creator_id
                )
            
            # Audit log
            if self.config.enable_security and "audit" in self.security_system:
                await self.security_system["audit"].log_action(
                    user_id=request.creator_id,
                    action="index_content",
                    resource=request.content_id or "unknown",
                    result="success" if result.success else "failure",
                    details={"content_type": request.content_type}
                )
            
            return asdict(result)
            
        except Exception as e:
            logger.error(f"❌ Content indexing failed: {e}")
            
            # Record failure metrics
            if self.config.enable_monitoring and "metrics" in self.monitoring_system:
                await self.monitoring_system["metrics"].record_operation(
                    operation_type="indexing",
                    content_type=request.content_type or "unknown",
                    processing_time_ms=0,
                    success=False,
                    creator_id=request.creator_id
                )
            
            raise
    
    async def search_content(self, request: SearchRequest) -> Dict[str, Any]:
        """Main entry point for content search"""
        try:
            if not self.initialized:
                raise RuntimeError("System not initialized")
            
            # Record metrics
            start_time = time.time()
            
            # Process through search service
            results = await self.services["search"].search(request)
            
            # Record performance metrics
            if self.config.enable_monitoring and "metrics" in self.monitoring_system:
                processing_time = (time.time() - start_time) * 1000
                await self.monitoring_system["metrics"].record_operation(
                    operation_type="search",
                    content_type="search_query",
                    processing_time_ms=processing_time,
                    success=True
                )
            
            return {
                "results": [asdict(result) for result in results.results],
                "total_results": results.total_results,
                "search_time_ms": results.search_time_ms,
                "suggestions": results.suggestions
            }
            
        except Exception as e:
            logger.error(f"❌ Content search failed: {e}")
            raise
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            status = {
                "system_info": {
                    "version": "2.0.0",
                    "author": "Fahed Mlaiel",
                    "initialized": self.initialized,
                    "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds() if self.start_time else 0
                },
                "health": await self.health_check(),
                "components": self.component_status
            }
            
            # Add monitoring metrics if available
            if self.config.enable_monitoring and "metrics" in self.monitoring_system:
                status["metrics"] = await self.monitoring_system["metrics"].get_current_metrics()
            
            # Add analytics data if available
            if self.config.enable_analytics and "content" in self.analytics_system:
                status["analytics"] = await self.analytics_system["content"].generate_content_analytics()
            
            # Add optimization status if available
            if self.config.enable_optimization and self.optimization_system:
                status["optimization"] = await self.optimization_system._collect_performance_metrics()
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Failed to get system status: {e}")
            return {"error": str(e)}
    
    async def shutdown(self):
        """Graceful system shutdown"""
        try:
            logger.info("🛑 Shutting down IA Influencer Agent Indexing System...")
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            # Shutdown optimization system
            if self.optimization_system and hasattr(self.optimization_system, 'workload_balancer'):
                if hasattr(self.optimization_system.workload_balancer, 'worker_pool'):
                    self.optimization_system.workload_balancer.worker_pool.shutdown(wait=True)
            
            logger.info("✅ System shutdown completed")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")


# Factory function for easy initialization
async def create_indexing_system(config: SystemConfig = None) -> IndexingOrchestrator:
    """Factory function to create and initialize the indexing system"""
    if config is None:
        config = SystemConfig()
    
    orchestrator = IndexingOrchestrator(config)
    await orchestrator.initialize()
    return orchestrator

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path

# Import all modules
from .engines import (
    VectorSearchEngine, ContentIndexEngine, 
    FingerprintIndexEngine, MetadataIndexEngine, IndexingConfig
)
from .processors import (
    MultiFormatProcessor, ProcessingConfig
)
from .repositories import (
    IndexRepository, VectorRepository, FingerprintRepository, SearchRepository
)
from .services import (
    IndexingService, SearchService, VectorService, RealtimeIndexService,
    IndexingRequest, SearchRequest
)
from .strategies import (
    ContentIndexingStrategy, VectorEmbeddingStrategy,
    SimilaritySearchStrategy, RankingStrategy
)

logger = logging.getLogger(__name__)


@dataclass
class IndexingModuleConfig:
    """Configuration for the entire indexing module"""
    # Database configuration
    database_url: str = "postgresql+asyncpg://user:pass@localhost/ia_influencer"
    redis_url: str = "redis://localhost:6379"
    elasticsearch_hosts: List[str] = None
    
    # Performance configuration
    vector_dimension: int = 768
    similarity_threshold: float = 0.85
    batch_size: int = 100
    max_concurrent_operations: int = 50
    enable_gpu: bool = True
    
    # Storage configuration
    temp_directory: str = "/tmp/ia_influencer_indexing"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    
    # Feature flags
    enable_realtime_indexing: bool = True
    enable_vector_search: bool = True
    enable_fingerprinting: bool = True
    enable_caching: bool = True
    
    # Monitoring
    enable_metrics: bool = True
    log_level: str = "INFO"


class IndexingModuleFactory:
    """Factory class for creating indexing module components"""
    
    def __init__(self, config: IndexingModuleConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Configure logging
        logging.basicConfig(level=getattr(logging, config.log_level))
        
        # Initialize storage
        Path(config.temp_directory).mkdir(parents=True, exist_ok=True)
    
    def create_indexing_config(self) -> IndexingConfig:
        """Create indexing engine configuration"""
        return IndexingConfig(
            vector_dimension=self.config.vector_dimension,
            similarity_threshold=self.config.similarity_threshold,
            batch_size=self.config.batch_size,
            max_concurrent_operations=self.config.max_concurrent_operations,
            elasticsearch_hosts=self.config.elasticsearch_hosts or ["http://localhost:9200"],
            redis_url=self.config.redis_url,
            enable_gpu=self.config.enable_gpu
        )
    
    def create_processing_config(self) -> ProcessingConfig:
        """Create content processing configuration"""
        return ProcessingConfig(
            max_file_size=self.config.max_file_size,
            temp_directory=self.config.temp_directory,
            enable_gpu=self.config.enable_gpu
        )
    
    async def create_repositories(self) -> Dict[str, Any]:
        """Create repository instances"""
        try:
            # This would typically initialize database connections
            # For now, we'll return mock repositories
            
            repositories = {
                "index_repo": None,  # Would be IndexRepository(db_session, redis_client)
                "vector_repo": None,  # Would be VectorRepository(db_session, redis_client, faiss_index)
                "fingerprint_repo": None,  # Would be FingerprintRepository(db_session, redis_client)
                "search_repo": None  # Would be SearchRepository(index_repo, vector_repo, fingerprint_repo)
            }
            
            self.logger.info("Created repository instances")
            return repositories
            
        except Exception as e:
            self.logger.error(f"Failed to create repositories: {e}")
            raise
    
    async def create_services(self, repositories: Dict[str, Any]) -> Dict[str, Any]:
        """Create service instances"""
        try:
            indexing_config = self.create_indexing_config()
            processing_config = self.create_processing_config()
            
            # Create services
            indexing_service = IndexingService(
                indexing_config=indexing_config,
                processing_config=processing_config,
                index_repo=repositories["index_repo"],
                vector_repo=repositories["vector_repo"],
                fingerprint_repo=repositories["fingerprint_repo"]
            )
            
            search_service = SearchService(
                indexing_config=indexing_config,
                search_repo=repositories["search_repo"],
                index_repo=repositories["index_repo"],
                vector_repo=repositories["vector_repo"],
                fingerprint_repo=repositories["fingerprint_repo"]
            )
            
            vector_service = VectorService(
                indexing_config=indexing_config,
                vector_repo=repositories["vector_repo"],
                vector_engine=VectorSearchEngine(indexing_config)
            )
            
            realtime_service = None
            if self.config.enable_realtime_indexing:
                realtime_service = RealtimeIndexService(indexing_service)
            
            services = {
                "indexing_service": indexing_service,
                "search_service": search_service,
                "vector_service": vector_service,
                "realtime_service": realtime_service
            }
            
            self.logger.info("Created service instances")
            return services
            
        except Exception as e:
            self.logger.error(f"Failed to create services: {e}")
            raise


class IndexingModule:
    """Main indexing module providing unified access to all functionalities"""
    
    def __init__(self, config: IndexingModuleConfig = None):
        self.config = config or IndexingModuleConfig()
        self.factory = IndexingModuleFactory(self.config)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Component storage
        self._repositories = {}
        self._services = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the indexing module"""
        try:
            if self._initialized:
                self.logger.warning("IndexingModule already initialized")
                return
            
            self.logger.info("Initializing IndexingModule...")
            
            # Create repositories
            self._repositories = await self.factory.create_repositories()
            
            # Create services
            self._services = await self.factory.create_services(self._repositories)
            
            # Initialize services
            if self._services["indexing_service"]:
                await self._services["indexing_service"].initialize()
            
            if self._services["search_service"]:
                await self._services["search_service"].initialize()
            
            # Start realtime service if enabled
            if self._services["realtime_service"]:
                await self._services["realtime_service"].start()
            
            self._initialized = True
            self.logger.info("IndexingModule initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize IndexingModule: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the indexing module"""
        try:
            if not self._initialized:
                return
            
            self.logger.info("Shutting down IndexingModule...")
            
            # Stop realtime service
            if self._services.get("realtime_service"):
                await self._services["realtime_service"].stop()
            
            # Cleanup resources
            self._repositories.clear()
            self._services.clear()
            self._initialized = False
            
            self.logger.info("IndexingModule shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Failed to shutdown IndexingModule: {e}")
    
    # Public API Methods
    
    async def index_content(self, request: IndexingRequest) -> Dict[str, Any]:
        """Index content with comprehensive processing"""
        try:
            if not self._initialized:
                await self.initialize()
            
            indexing_service = self._services.get("indexing_service")
            if not indexing_service:
                raise RuntimeError("Indexing service not available")
            
            result = await indexing_service.index_content(request)
            
            return {
                "success": result.success,
                "content_id": result.content_id,
                "processing_time_ms": result.processing_time_ms,
                "features_extracted": result.features_extracted,
                "embeddings_generated": result.embeddings_generated,
                "fingerprints_created": result.fingerprints_created,
                "errors": result.errors,
                "warnings": result.warnings
            }
            
        except Exception as e:
            self.logger.error(f"Failed to index content: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_content(self, request: SearchRequest) -> Dict[str, Any]:
        """Search indexed content"""
        try:
            if not self._initialized:
                await self.initialize()
            
            search_service = self._services.get("search_service")
            if not search_service:
                raise RuntimeError("Search service not available")
            
            result = await search_service.search(request)
            
            return {
                "success": True,
                "results": result.results,
                "total_count": result.total_count,
                "query_time_ms": result.query_time_ms,
                "aggregations": result.aggregations,
                "suggestions": result.suggestions
            }
            
        except Exception as e:
            self.logger.error(f"Failed to search content: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "total_count": 0
            }
    
    async def find_similar_content(self, content_id: str, limit: int = 10) -> Dict[str, Any]:
        """Find content similar to the given content"""
        try:
            if not self._initialized:
                await self.initialize()
            
            search_service = self._services.get("search_service")
            if not search_service:
                raise RuntimeError("Search service not available")
            
            similar_content = await search_service.find_similar_content(content_id, limit)
            
            return {
                "success": True,
                "content_id": content_id,
                "similar_content": similar_content,
                "count": len(similar_content)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to find similar content: {e}")
            return {
                "success": False,
                "error": str(e),
                "similar_content": []
            }
    
    async def get_content_recommendations(self, content_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get content recommendations"""
        try:
            if not self._initialized:
                await self.initialize()
            
            search_service = self._services.get("search_service")
            if not search_service:
                raise RuntimeError("Search service not available")
            
            recommendations = await search_service.get_recommendations(content_id, limit)
            
            return {
                "success": True,
                "content_id": content_id,
                "recommendations": recommendations,
                "count": len(recommendations)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get recommendations: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": []
            }
    
    async def create_text_embedding(self, content_id: str, text: str) -> Dict[str, Any]:
        """Create text embedding for content"""
        try:
            if not self._initialized:
                await self.initialize()
            
            vector_service = self._services.get("vector_service")
            if not vector_service:
                raise RuntimeError("Vector service not available")
            
            vector_id = await vector_service.create_embedding(content_id, text)
            
            return {
                "success": vector_id is not None,
                "content_id": content_id,
                "vector_id": vector_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create text embedding: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def similarity_search_by_text(self, query_text: str, top_k: int = 10) -> Dict[str, Any]:
        """Perform similarity search using text query"""
        try:
            if not self._initialized:
                await self.initialize()
            
            vector_service = self._services.get("vector_service")
            if not vector_service:
                raise RuntimeError("Vector service not available")
            
            results = await vector_service.similarity_search_by_text(query_text, top_k)
            
            return {
                "success": True,
                "query_text": query_text,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to perform similarity search: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    async def update_content_index(self, content_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing content index"""
        try:
            if not self._initialized:
                await self.initialize()
            
            indexing_service = self._services.get("indexing_service")
            if not indexing_service:
                raise RuntimeError("Indexing service not available")
            
            success = await indexing_service.update_index(content_id, updates)
            
            return {
                "success": success,
                "content_id": content_id,
                "updated_fields": list(updates.keys())
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update content index: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_content_index(self, content_id: str) -> Dict[str, Any]:
        """Delete content from all indexes"""
        try:
            if not self._initialized:
                await self.initialize()
            
            indexing_service = self._services.get("indexing_service")
            if not indexing_service:
                raise RuntimeError("Indexing service not available")
            
            success = await indexing_service.delete_index(content_id)
            
            return {
                "success": success,
                "content_id": content_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to delete content index: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_indexing_stats(self, creator_id: Optional[str] = None) -> Dict[str, Any]:
        """Get indexing statistics"""
        try:
            if not self._initialized:
                await self.initialize()
            
            indexing_service = self._services.get("indexing_service")
            if not indexing_service:
                raise RuntimeError("Indexing service not available")
            
            stats = await indexing_service.get_indexing_stats(creator_id)
            
            return {
                "success": True,
                "stats": stats
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get indexing stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "stats": {}
            }
    
    async def queue_realtime_indexing(self, request: IndexingRequest) -> Dict[str, Any]:
        """Queue content for real-time indexing"""
        try:
            if not self._initialized:
                await self.initialize()
            
            realtime_service = self._services.get("realtime_service")
            if not realtime_service:
                return await self.index_content(request)  # Fallback to sync indexing
            
            await realtime_service.queue_indexing(request)
            
            return {
                "success": True,
                "content_id": request.content_id,
                "queued": True,
                "mode": "realtime"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to queue realtime indexing: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_realtime_queue_status(self) -> Dict[str, Any]:
        """Get real-time queue status"""
        try:
            if not self._initialized:
                await self.initialize()
            
            realtime_service = self._services.get("realtime_service")
            if not realtime_service:
                return {
                    "success": True,
                    "realtime_enabled": False
                }
            
            status = await realtime_service.get_queue_status()
            
            return {
                "success": True,
                "realtime_enabled": True,
                "queue_status": status
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get queue status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Utility methods
    
    def get_supported_file_formats(self) -> Dict[str, List[str]]:
        """Get supported file formats for processing"""
        return {
            "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"],
            "video": [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm", ".m4v"],
            "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"],
            "text": [".txt", ".md", ".rtf", ".doc", ".docx"]
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "name": "IA Influencer Agent - Indexing Module",
            "version": "2.0.0",
            "author": "Fahed Mlaiel",
            "email": "mlaiel@live.de",
            "initialized": self._initialized,
            "config": {
                "enable_realtime_indexing": self.config.enable_realtime_indexing,
                "enable_vector_search": self.config.enable_vector_search,
                "enable_fingerprinting": self.config.enable_fingerprinting,
                "enable_caching": self.config.enable_caching,
                "vector_dimension": self.config.vector_dimension,
                "similarity_threshold": self.config.similarity_threshold
            },
            "supported_formats": self.get_supported_file_formats()
        }


# Convenience functions for easy module usage

async def create_indexing_module(config: IndexingModuleConfig = None) -> IndexingModule:
    """Create and initialize an indexing module"""
    module = IndexingModule(config)
    await module.initialize()
    return module


async def quick_index_file(file_path: str, creator_id: str, 
                          title: str = "", description: str = "",
                          tags: List[str] = None) -> Dict[str, Any]:
    """Quick utility function to index a single file"""
    try:
        module = await create_indexing_module()
        
        request = IndexingRequest(
            creator_id=creator_id,
            file_path=file_path,
            title=title,
            description=description,
            tags=tags or [],
            process_embeddings=True,
            generate_fingerprints=True
        )
        
        result = await module.index_content(request)
        await module.shutdown()
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to quick index file {file_path}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def quick_search_content(query_text: str, content_types: List[str] = None,
                             limit: int = 10) -> Dict[str, Any]:
    """Quick utility function to search content"""
    try:
        module = await create_indexing_module()
        
        request = SearchRequest(
            query_text=query_text,
            content_types=content_types,
            limit=limit,
            enable_fuzzy=True
        )
        
        result = await module.search_content(request)
        await module.shutdown()
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to quick search content: {e}")
        return {
            "success": False,
            "error": str(e),
            "results": []
        }


# Export main classes and functions
__all__ = [
    "IndexingModule",
    "IndexingModuleConfig", 
    "IndexingModuleFactory",
    "create_indexing_module",
    "quick_index_file",
    "quick_search_content",
    "IndexingRequest",
    "SearchRequest"
]
