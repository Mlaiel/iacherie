"""
Vector Agent Index - Service Registry & Factory Pattern

Ultra-advanced service registry providing centralized access to all vector
agent components with dependency injection and lifecycle management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Any attempt to steal the concept, idea, or code without explicit written authorization
from Fahed Mlaiel will result in immediate legal prosecution under German and international law.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Type, Union
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from .vector_orchestrator import VectorOrchestrator
from .faiss_manager import FAISSManager
from .similarity_engine import SimilarityEngine
from .vector_indexer import VectorIndexer
from .search_optimizer import SearchOptimizer
from .config import VectorConfig, get_config_for_environment
from .models import VectorDocument, VectorSearchRequest, VectorSearchResult
from .exceptions import VectorConfigurationError, VectorProcessingError

logger = logging.getLogger(__name__)


class VectorServiceRegistry:
    """
    Ultra-Advanced Vector Service Registry
    
    Centralized registry providing factory methods, dependency injection,
    and lifecycle management for all vector agent components.
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._initialized = False
        self._config: Optional[VectorConfig] = None
        self._shutdown_requested = False
        
    async def initialize(self, config: Optional[VectorConfig] = None) -> None:
        """Initialize the service registry with configuration"""



        try:
            if self._initialized:
                logger.warning("Service registry already initialized")
                return
            
            # Load configuration
            self._config = config or get_config_for_environment()
            
            # Initialize core services
            await self._initialize_core_services()
            
            # Initialize orchestrator
            await self._initialize_orchestrator()
            
            self._initialized = True
            logger.info("Vector service registry initialized successfully")
            
        except Exception as e:
            logger.error(f"Service registry initialization failed: {e}")
            raise VectorConfigurationError(f"Registry initialization failed: {str(e)}")
    
    async def _initialize_core_services(self) -> None:
        """Initialize core vector services"""



        try:
            # Initialize FAISS Manager
            faiss_manager = FAISSManager(self._config)
            await faiss_manager.initialize()
            self._services["faiss_manager"] = faiss_manager
            
            # Initialize Similarity Engine
            similarity_engine = SimilarityEngine(self._config)
            await similarity_engine.initialize()
            self._services["similarity_engine"] = similarity_engine
            
            # Initialize Vector Indexer
            vector_indexer = VectorIndexer(self._config)
            await vector_indexer.initialize()
            self._services["vector_indexer"] = vector_indexer
            
            # Initialize Search Optimizer
            search_optimizer = SearchOptimizer(self._config)
            await search_optimizer.initialize()
            self._services["search_optimizer"] = search_optimizer
            
            logger.info("Core vector services initialized")
            
        except Exception as e:
            logger.error(f"Core services initialization failed: {e}")
            raise
    
    async def _initialize_orchestrator(self) -> None:
        """Initialize the main vector orchestrator"""



        try:
            orchestrator = VectorOrchestrator(self._config)
            await orchestrator.initialize()
            self._services["orchestrator"] = orchestrator
            
            logger.info("Vector orchestrator initialized")
            
        except Exception as e:
            logger.error(f"Orchestrator initialization failed: {e}")
            raise
    
    def get_service(self, service_name: str) -> Any:
        """Get service by name"""
        if not self._initialized:
            raise VectorConfigurationError("Service registry not initialized")
        
        if service_name not in self._services:
            raise VectorConfigurationError(f"Service '{service_name}' not found")
        
        return self._services[service_name]
    
    def get_orchestrator(self) -> VectorOrchestrator:
        """Get the main vector orchestrator"""



        return self.get_service("orchestrator")
    
    def get_faiss_manager(self) -> FAISSManager:
        """Get the FAISS manager"""



        return self.get_service("faiss_manager")
    
    def get_similarity_engine(self) -> SimilarityEngine:
        """Get the similarity engine"""



        return self.get_service("similarity_engine")
    
    def get_vector_indexer(self) -> VectorIndexer:
        """Get the vector indexer"""



        return self.get_service("vector_indexer")
    
    def get_search_optimizer(self) -> SearchOptimizer:
        """Get the search optimizer"""



        return self.get_service("search_optimizer")
    
    def get_config(self) -> VectorConfig:
        """Get the current configuration"""
        if not self._config:
            raise VectorConfigurationError("Configuration not available")
        return self._config
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all services"""
        if not self._initialized:
            return {"status": "unhealthy", "reason": "Not initialized"}
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {}
        }
        
        # Check each service
        for service_name, service in self._services.items():
            try:
                # Check if service has health check method
                if hasattr(service, "health_check"):
                    service_health = await service.health_check()
                else:
                    # Basic health check - service exists and is accessible
                    service_health = {"status": "healthy", "method": "basic"}
                
                health_status["services"][service_name] = service_health
                
            except Exception as e:
                health_status["services"][service_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["status"] = "degraded"
        
        return health_status
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all services"""
        if not self._initialized:
            return {"error": "Service registry not initialized"}
        
        statistics = {
            "registry_status": "active",
            "initialized_at": self._initialized,
            "services_count": len(self._services),
            "service_statistics": {}
        }
        
        # Collect statistics from each service
        for service_name, service in self._services.items():
            try:
                if hasattr(service, "get_statistics"):
                    service_stats = await service.get_statistics()
                else:
                    service_stats = {"status": "available", "no_statistics": True}
                
                statistics["service_statistics"][service_name] = service_stats
                
            except Exception as e:
                statistics["service_statistics"][service_name] = {
                    "error": str(e)
                }
        
        return statistics
    
    async def shutdown(self) -> None:
        """Graceful shutdown of all services"""
        if self._shutdown_requested:
            return
        
        self._shutdown_requested = True
        logger.info("Shutting down vector service registry")
        
        # Shutdown services in reverse order of initialization
        shutdown_order = ["orchestrator", "search_optimizer", "vector_indexer", 
                         "similarity_engine", "faiss_manager"]
        
        for service_name in shutdown_order:
            if service_name in self._services:
                try:
                    service = self._services[service_name]
                    if hasattr(service, "shutdown"):
                        await service.shutdown()
                    logger.info(f"Service {service_name} shut down successfully")
                except Exception as e:
                    logger.error(f"Error shutting down service {service_name}: {e}")
        
        self._services.clear()
        self._initialized = False
        logger.info("Vector service registry shut down completed")


# Global service registry instance
_service_registry: Optional[VectorServiceRegistry] = None


async def get_service_registry() -> VectorServiceRegistry:
    """Get the global service registry (singleton pattern)"""
    global _service_registry
    
    if _service_registry is None:
        _service_registry = VectorServiceRegistry()
        await _service_registry.initialize()
    
    return _service_registry


async def initialize_vector_services(config: Optional[VectorConfig] = None) -> VectorServiceRegistry:
    """Initialize vector services with configuration"""
    global _service_registry
    
    if _service_registry is not None:
        logger.warning("Vector services already initialized")
        return _service_registry
    
    _service_registry = VectorServiceRegistry()
    await _service_registry.initialize(config)
    
    return _service_registry


async def shutdown_vector_services() -> None:
    """Shutdown all vector services"""
    global _service_registry
    
    if _service_registry is not None:
        await _service_registry.shutdown()
        _service_registry = None


@asynccontextmanager
async def vector_service_context(config: Optional[VectorConfig] = None):
    """Context manager for vector services lifecycle"""
    registry = None
    try:
        registry = await initialize_vector_services(config)
        yield registry
    finally:
        if registry:
            await registry.shutdown()


# ===============================
# FACTORY FUNCTIONS
# ===============================

async def create_vector_orchestrator(config: Optional[VectorConfig] = None) -> VectorOrchestrator:
    """Factory function to create configured vector orchestrator"""
    if config is None:
        config = get_config_for_environment()
    
    orchestrator = VectorOrchestrator(config)
    await orchestrator.initialize()
    return orchestrator


async def create_faiss_manager(config: Optional[VectorConfig] = None) -> FAISSManager:
    """Factory function to create configured FAISS manager"""
    if config is None:
        config = get_config_for_environment()
    
    manager = FAISSManager(config)
    await manager.initialize()
    return manager


async def create_similarity_engine(config: Optional[VectorConfig] = None) -> SimilarityEngine:
    """Factory function to create configured similarity engine"""
    if config is None:
        config = get_config_for_environment()
    
    engine = SimilarityEngine(config)
    await engine.initialize()
    return engine


async def create_vector_indexer(config: Optional[VectorConfig] = None) -> VectorIndexer:
    """Factory function to create configured vector indexer"""
    if config is None:
        config = get_config_for_environment()
    
    indexer = VectorIndexer(config)
    await indexer.initialize()
    return indexer


async def create_search_optimizer(config: Optional[VectorConfig] = None) -> SearchOptimizer:
    """Factory function to create configured search optimizer"""
    if config is None:
        config = get_config_for_environment()
    
    optimizer = SearchOptimizer(config)
    await optimizer.initialize()
    return optimizer


# ===============================
# CONVENIENCE FUNCTIONS
# ===============================

async def store_vector_document(document: VectorDocument) -> Dict[str, Any]:
    """Convenience function to store vector document"""



    try:
        registry = await get_service_registry()
        orchestrator = registry.get_orchestrator()
        
        from ..base import AgentRequest
        request = AgentRequest(
            action="store_vector",
            data={
                "content_id": document.document_id,
                "content_type": document.content_type,
                "vector_data": document.vector_data.tolist(),
                "metadata": document.metadata
            }
        )
        
        response = await orchestrator.process_request(request)
        return response.data if response.success else {"error": response.error}
        
    except Exception as e:
        logger.error(f"Failed to store vector document: {e}")
        return {"error": str(e)}


async def search_similar_vectors(request: VectorSearchRequest) -> List[VectorSearchResult]:
    """Convenience function to search for similar vectors"""



    try:
        registry = await get_service_registry()
        orchestrator = registry.get_orchestrator()
        
        from ..base import AgentRequest
        agent_request = AgentRequest(
            action="search_similar",
            data={
                "query_vector": request.query_vector.tolist(),
                "content_type": request.content_type,
                "max_results": request.max_results,
                "similarity_threshold": request.similarity_threshold,
                "search_parameters": request.search_parameters
            }
        )
        
        response = await orchestrator.process_request(agent_request)
        
        if response.success:
            # Convert response data back to VectorSearchResult objects
            results = []
            for result_data in response.data.get("results", []):
                result = VectorSearchResult(
                    document_id=result_data["document_id"],
                    similarity_score=result_data["similarity_score"],
                    confidence=result_data.get("confidence", 0.0),
                    match_type=result_data.get("match_type", "similar"),
                    detailed_scores=result_data.get("detailed_scores"),
                    metadata=result_data.get("metadata")
                )
                results.append(result)
            return results
        else:
            logger.error(f"Vector search failed: {response.error}")
            return []
            
    except Exception as e:
        logger.error(f"Failed to search similar vectors: {e}")
        return []


async def get_vector_statistics() -> Dict[str, Any]:
    """Convenience function to get vector system statistics"""



    try:
        registry = await get_service_registry()
        return await registry.get_statistics()
    except Exception as e:
        logger.error(f"Failed to get vector statistics: {e}")
        return {"error": str(e)}


async def perform_health_check() -> Dict[str, Any]:
    """Convenience function to perform system health check"""



    try:
        registry = await get_service_registry()
        return await registry.health_check()
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


# ===============================
# MODULE EXPORTS
# ===============================

__all__ = [
    # Core classes
    "VectorServiceRegistry",
    
    # Registry functions
    "get_service_registry",
    "initialize_vector_services",
    "shutdown_vector_services",
    "vector_service_context",
    
    # Factory functions
    "create_vector_orchestrator",
    "create_faiss_manager",
    "create_similarity_engine",
    "create_vector_indexer",
    "create_search_optimizer",
    
    # Convenience functions
    "store_vector_document",
    "search_similar_vectors",
    "get_vector_statistics",
    "perform_health_check"
]
