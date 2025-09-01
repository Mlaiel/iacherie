"""Conversation Memory Index - Main Entry Point
===========================================

Point d'entrée principal pour le système de mémoire conversationnelle
de la plateforme IA Influencer Agent. Ce module centralise l'accès à tous
les composants de gestion de mémoire pour créateurs multi-format.

Features:
- Point d'entrée unifié pour tous les composants de mémoire
- Factory pattern pour l'initialisation des services
- Configuration centralisée et gestion des dépendances
- Interface simplifiée pour l'intégration avec d'autres modules
- Monitoring et logging centralisé des composants
- Gestion des erreurs et fallback automatique

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE ⚠️
This software and all associated intellectual property are the exclusive property
of Fahed Mlaiel. Unauthorized use, copying, distribution, modification, or 
commercialization without explicit written permission is strictly prohibited.

Any violation will result in immediate legal action under German and International
copyright law. This includes but is not limited to code theft, concept copying,
or unauthorized derivative works.

Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, Optional, Any, Type, Union, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone

# Core backend imports
from backend.utils.cache import CacheManager
from backend.utils.metrics import MetricsCollector
from backend.core.database import get_async_session
from backend.core.config import settings

# Internal module imports
from .managers import (
    ConversationMemoryManager,
    ConversationHistoryManager,
    MemoryIndexer
)

from .storage import (
    LongTermMemory,
    ShortTermMemory,
    ConversationDatabase,
    VectorStore
)

from .retrieval import (
    ConversationRetriever,
    SemanticSearch,
    ContextualRetriever,
    ContentAwareRetriever
)

from .indexing import (
    ConversationIndexer,
    TopicIndexer,
    SemanticIndexer,
    ContentIndexer,
    TemporalIndexer
)

from .analytics import (
    ConversationAnalytics,
    MemoryMetrics,
    UsageTracker,
    PerformanceMonitor,
    InsightGenerator
)

from .models import (
    ConversationRecord,
    MemoryEntry,
    ContentType,
    ConversationStatus
)

# Configure logging
logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """
Available service types"""

    MEMORY_MANAGER = "memory_manager"
    HISTORY_MANAGER = "history_manager"
    INDEXER = "indexer"
    RETRIEVER = "retriever"
    ANALYTICS = "analytics"
    STORAGE = "storage"


@dataclass
class ServiceConfig:
    """Service configuration"""
    service_type: ServiceType
    enabled: bool = True
    auto_initialize: bool = True
    cache_enabled: bool = True
    metrics_enabled: bool = True
    retry_attempts: int = 3
    timeout_seconds: int = 30


class ConversationMemoryFactory:
    """
    Factory for creating and managing conversation memory services
    
    Provides centralized service creation, configuration, and lifecycle
    management for all conversation memory components.
    """
    
    def __init__(self):
        self._services: Dict[ServiceType, Any] = {}
        self._configs: Dict[ServiceType, ServiceConfig] = {}
        self._initialized = False
        self.metrics = MetricsCollector("conversation_memory_factory")
        
        # Default configurations
        self._setup_default_configs()
        
        logger.info("ConversationMemoryFactory initialized")
    
    def _setup_default_configs(self):
        """Setup default service configurations"""
        for service_type in ServiceType:
            self._configs[service_type] = ServiceConfig(
                service_type=service_type,
                enabled=True,
                auto_initialize=True,
                cache_enabled=True,
                metrics_enabled=True
            )
    
    async def initialize(self):
        """
Initialize all enabled services"""
        if self._initialized:
            return
        
        try:
            logger.info("Initializing ConversationMemoryFactory services...")
            
            # Initialize services in order of dependency
            await self._initialize_storage_services()
            await self._initialize_indexing_services()
            await self._initialize_retrieval_services()
            await self._initialize_manager_services()
            await self._initialize_analytics_services()
            
            self._initialized = True
            self.metrics.increment("factory_initialized")
            logger.info("ConversationMemoryFactory services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ConversationMemoryFactory: {e}")
            self.metrics.increment("factory_initialization_errors")
            raise
    
    async def _initialize_storage_services(self):
        """Initialize storage services"""
        if self._configs[ServiceType.STORAGE].enabled:
            try:
                # Initialize storage components
                long_term_memory = LongTermMemory()
                short_term_memory = ShortTermMemory()
                vector_store = VectorStore()
                conversation_db = ConversationDatabase()
                
                # Store in services registry
                self._services[ServiceType.STORAGE] = {
                    "long_term_memory": long_term_memory,
                    "short_term_memory": short_term_memory,
                    "vector_store": vector_store,
                    "conversation_db": conversation_db
                }
                
                # Initialize if auto-initialize is enabled
                if self._configs[ServiceType.STORAGE].auto_initialize:
                    await long_term_memory.initialize()
                    await short_term_memory.initialize()
                    await vector_store.initialize()
                    await conversation_db.initialize()
                
                logger.info("Storage services initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize storage services: {e}")
                raise
    
    async def _initialize_indexing_services(self):
        """Initialize indexing services"""
        if self._configs[ServiceType.INDEXER].enabled:
            try:
                # Initialize indexing components
                conversation_indexer = ConversationIndexer()
                topic_indexer = TopicIndexer()
                semantic_indexer = SemanticIndexer()
                content_indexer = ContentIndexer()
                temporal_indexer = TemporalIndexer()
                
                # Store in services registry
                self._services[ServiceType.INDEXER] = {
                    "conversation_indexer": conversation_indexer,
                    "topic_indexer": topic_indexer,
                    "semantic_indexer": semantic_indexer,
                    "content_indexer": content_indexer,
                    "temporal_indexer": temporal_indexer
                }
                
                # Initialize if auto-initialize is enabled
                if self._configs[ServiceType.INDEXER].auto_initialize:
                    await conversation_indexer.initialize()
                    await topic_indexer.initialize()
                    await semantic_indexer.initialize()
                    await content_indexer.initialize()
                    await temporal_indexer.initialize()
                
                logger.info("Indexing services initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize indexing services: {e}")
                raise
    
    async def _initialize_retrieval_services(self):
        """Initialize retrieval services"""
        if self._configs[ServiceType.RETRIEVER].enabled:
            try:
                # Initialize retrieval components
                conversation_retriever = ConversationRetriever()
                semantic_search = SemanticSearch()
                contextual_retriever = ContextualRetriever()
                content_aware_retriever = ContentAwareRetriever()
                
                # Store in services registry
                self._services[ServiceType.RETRIEVER] = {
                    "conversation_retriever": conversation_retriever,
                    "semantic_search": semantic_search,
                    "contextual_retriever": contextual_retriever,
                    "content_aware_retriever": content_aware_retriever
                }
                
                # Initialize if auto-initialize is enabled
                if self._configs[ServiceType.RETRIEVER].auto_initialize:
                    await conversation_retriever.initialize()
                    await semantic_search.initialize()
                    await contextual_retriever.initialize()
                    await content_aware_retriever.initialize()
                
                logger.info("Retrieval services initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize retrieval services: {e}")
                raise
    
    async def _initialize_manager_services(self):
        """Initialize manager services"""
        if self._configs[ServiceType.MEMORY_MANAGER].enabled:
            try:
                # Get dependencies
                storage_services = self._services.get(ServiceType.STORAGE, {})
                indexer_services = self._services.get(ServiceType.INDEXER, {})
                retriever_services = self._services.get(ServiceType.RETRIEVER, {})
                
                # Initialize manager components
                memory_manager = ConversationMemoryManager()
                history_manager = ConversationHistoryManager()
                memory_indexer = MemoryIndexer()
                
                # Store in services registry
                self._services[ServiceType.MEMORY_MANAGER] = {
                    "memory_manager": memory_manager,
                    "history_manager": history_manager,
                    "memory_indexer": memory_indexer
                }
                
                # Initialize if auto-initialize is enabled
                if self._configs[ServiceType.MEMORY_MANAGER].auto_initialize:
                    await memory_manager.initialize()
                    await history_manager.initialize()
                    await memory_indexer.initialize()
                
                logger.info("Manager services initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize manager services: {e}")
                raise
    
    async def _initialize_analytics_services(self):
        """Initialize analytics services"""
        if self._configs[ServiceType.ANALYTICS].enabled:
            try:
                # Initialize analytics components
                conversation_analytics = ConversationAnalytics()
                memory_metrics = MemoryMetrics()
                usage_tracker = UsageTracker()
                performance_monitor = PerformanceMonitor()
                insight_generator = InsightGenerator()
                
                # Store in services registry
                self._services[ServiceType.ANALYTICS] = {
                    "conversation_analytics": conversation_analytics,
                    "memory_metrics": memory_metrics,
                    "usage_tracker": usage_tracker,
                    "performance_monitor": performance_monitor,
                    "insight_generator": insight_generator
                }
                
                # Initialize if auto-initialize is enabled
                if self._configs[ServiceType.ANALYTICS].auto_initialize:
                    await conversation_analytics.initialize()
                
                logger.info("Analytics services initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize analytics services: {e}")
                raise
    
    def get_service(self, service_type: ServiceType, component_name: Optional[str] = None) -> Any:
        """
        Get a service instance
        
        Args:
            service_type: Type of service to retrieve
            component_name: Specific component name (optional)
            
        Returns:
            Service instance or service group
        """
        if not self._initialized:
            raise RuntimeError("Factory not initialized. Call initialize() first.")
        
        services = self._services.get(service_type)
        if not services:
            raise ValueError(f"Service type {service_type} not found")
        
        if component_name:
            if component_name not in services:
                raise ValueError(f"Component {component_name} not found in {service_type}")
            return services[component_name]
        
        return services
    
    def configure_service(self, service_type: ServiceType, config: ServiceConfig):
        """Configure a service"""
        self._configs[service_type] = config
        logger.info(f"Service {service_type} configured")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all services"""
        health_status = {
            "factory_initialized": self._initialized,
            "services": {},
            "overall_status": "healthy"
        }
        
        try:
            for service_type, services in self._services.items():
                service_health = {
                    "available": True,
                    "components": len(services) if isinstance(services, dict) else 1,
                    "status": "healthy"
                }
                
                # Check if service has health check method
                if isinstance(services, dict):
                    for component_name, component in services.items():
                        if hasattr(component, 'health_check'):
                            try:
                                await component.health_check()
                            except Exception as e:
                                service_health["status"] = "unhealthy"
                                service_health["error"] = str(e)
                                health_status["overall_status"] = "degraded"
                
                health_status["services"][service_type.value] = service_health
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health_status["overall_status"] = "unhealthy"
            health_status["error"] = str(e)
            return health_status
    
    async def shutdown(self):
        """Shutdown all services"""
        try:
            logger.info("Shutting down ConversationMemoryFactory services...")
            
            # Shutdown services in reverse order
            for service_type in reversed(list(ServiceType)):
                services = self._services.get(service_type)
                if services and isinstance(services, dict):
                    for component_name, component in services.items():
                        if hasattr(component, 'shutdown'):
                            try:
                                await component.shutdown()
                            except Exception as e:
                                logger.error(f"Error shutting down {component_name}: {e}")
            
            self._services.clear()
            self._initialized = False
            
            logger.info("ConversationMemoryFactory shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Global factory instance
_factory: Optional[ConversationMemoryFactory] = None


async def get_conversation_memory_factory() -> ConversationMemoryFactory:
    """Get the global conversation memory factory instance"""
    global _factory
    
    if _factory is None:
        _factory = ConversationMemoryFactory()
        await _factory.initialize()
    
    return _factory


async def get_memory_manager() -> ConversationMemoryManager:
    """
Get conversation memory manager"""
    factory = await get_conversation_memory_factory()
    return factory.get_service(ServiceType.MEMORY_MANAGER, "memory_manager")


async def get_history_manager() -> ConversationHistoryManager:
    """Get conversation history manager"""
    factory = await get_conversation_memory_factory()
    return factory.get_service(ServiceType.MEMORY_MANAGER, "history_manager")


async def get_indexer() -> MemoryIndexer:
    """Get memory indexer"""
    factory = await get_conversation_memory_factory()
    return factory.get_service(ServiceType.MEMORY_MANAGER, "memory_indexer")


async def get_conversation_retriever() -> ConversationRetriever:
    """Get conversation retriever"""
    factory = await get_conversation_memory_factory()
    return factory.get_service(ServiceType.RETRIEVER, "conversation_retriever")


async def get_semantic_search() -> SemanticSearch:
    """Get semantic search"""
    factory = await get_conversation_memory_factory()
    return factory.get_service(ServiceType.RETRIEVER, "semantic_search")


async def get_conversation_analytics() -> ConversationAnalytics:
    """Get conversation analytics"""
    factory = await get_conversation_memory_factory()
    return factory.get_service(ServiceType.ANALYTICS, "conversation_analytics")


async def get_storage_services() -> Dict[str, Any]:
    """Get all storage services"""
    factory = await get_conversation_memory_factory()
    return factory.get_service(ServiceType.STORAGE)


async def get_indexing_services() -> Dict[str, Any]:
    """
Get all indexing services"""
    factory = await get_conversation_memory_factory()
    return factory.get_service(ServiceType.INDEXER)


# Convenience functions for quick access
async def store_conversation(
    user_id: str,
    conversation_data: Dict[str, Any],
    content_type: ContentType = ContentType.GENERAL,
    **kwargs
) -> bool:
    """
Quick conversation storage"""
    manager = await get_memory_manager()
    return await manager.store_conversation(
        user_id=user_id,
        conversation_data=conversation_data,
        content_type=content_type,
        **kwargs
    )


async def search_conversations(
    user_id: str,
    query: str,
    content_type: Optional[ContentType] = None,
    limit: int = 10,
    **kwargs
) -> List[ConversationRecord]:
    """
Quick conversation search"""
    retriever = await get_conversation_retriever()
    return await retriever.search_conversations(
        user_id=user_id,
        query=query,
        content_type=content_type,
        limit=limit,
        **kwargs
    )


async def get_user_insights(user_id: str) -> Dict[str, Any]:
    """
Quick user insights generation"""
    analytics = await get_conversation_analytics()
    insights = await analytics.generate_user_insights(user_id)
    return insights.to_dict()


# Service health and monitoring
async def check_system_health() -> Dict[str, Any]:
    """
Check overall system health"""
    factory = await get_conversation_memory_factory()
    return await factory.health_check()


async def get_system_metrics() -> Dict[str, Any]:
    """
Get system performance metrics"""
    try:
        factory = await get_conversation_memory_factory()
        metrics_service = factory.get_service(ServiceType.ANALYTICS, "memory_metrics")
        return await metrics_service.collect_storage_metrics()
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        return {"error": str(e)}


# Module cleanup
async def shutdown_conversation_memory():
    """Shutdown conversation memory system"""
    global _factory
    if _factory:
        await _factory.shutdown()
        _factory = None


# Export all important components
__all__ = [
    # Factory and main entry point
    "ConversationMemoryFactory",
    "get_conversation_memory_factory",
    
    # Service getters
    "get_memory_manager",
    "get_history_manager", 
    "get_indexer",
    "get_conversation_retriever",
    "get_semantic_search",
    "get_conversation_analytics",
    "get_storage_services",
    "get_indexing_services",
    
    # Convenience functions
    "store_conversation",
    "search_conversations",
    "get_user_insights",
    
    # System monitoring
    "check_system_health",
    "get_system_metrics",
    "shutdown_conversation_memory",
    
    # Configuration
    "ServiceType",
    "ServiceConfig"
]
