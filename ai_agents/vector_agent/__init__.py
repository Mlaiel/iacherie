"""Vector Agent Module - Ultra-Advanced Vector Database Management

Comprehensive vector database management system with FAISS integration,
multi-modal similarity search, and enterprise-grade performance optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""
# Core vector agent components
from .vector_orchestrator import VectorOrchestrator
from .faiss_manager import FAISSManager, FAISSIndexManager
from .similarity_engine import SimilarityEngine, ContentTypeSimilarityProcessor
from .vector_indexer import VectorIndexer, VectorDocumentStore
from .search_optimizer import SearchOptimizer, QueryCache, QueryOptimizer, ResultEnhancer

# Data models and configuration
from .models import (
    VectorDocument,
    VectorSearchRequest,
    VectorSearchResult,
    VectorMetrics,
    VectorStatistics,
    FAISSIndexConfig,
    SimilarityConfig,
    CacheConfig,
    ContentTypeConfig
)
from .config import VectorConfig, get_config_for_environment

# Exceptions and error handling
from .exceptions import (
    VectorAgentBaseException,
    VectorConfigurationError,
    VectorProcessingError,
    VectorDimensionError,
    FAISSIndexError,
    SimilarityComputationError,
    VectorStorageError,
    VectorValidationError,
    VectorTimeoutError,
    VectorResourceError
)

# Service registry and factory functions
from .index import (
    VectorServiceRegistry,
    get_service_registry,
    initialize_vector_services,
    shutdown_vector_services,
    vector_service_context,
    create_vector_orchestrator,
    create_faiss_manager,
    create_similarity_engine,
    create_vector_indexer,
    create_search_optimizer,
    store_vector_document,
    search_similar_vectors,
    get_vector_statistics,
    perform_health_check
)

# Base agent integration
from ..base import BaseAgent, AgentRequest, AgentResponse


class VectorAgent(BaseAgent):
    """    Ultra-Advanced Vector Database Agent
    
    Enterprise-grade vector database management with FAISS integration,
    multi-modal similarity search, and intelligent caching.
    """    
    def __init__(self, agent_id: str = "vector_agent", config: dict = None):
        super().__init__(agent_id=agent_id, config=config)
        self.orchestrator: VectorOrchestrator = None
        self.service_registry: VectorServiceRegistry = None
        
    async def initialize(self) -> bool:
        """Initialize the vector agent"""


        try:
            # Create vector configuration
            vector_config = get_config_for_environment()
            
            # Initialize service registry
            self.service_registry = await initialize_vector_services(vector_config)
            
            # Get the main orchestrator
            self.orchestrator = self.service_registry.get_orchestrator()
            
            self.logger.info("Vector agent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Vector agent initialization failed: {e}")
            return False
    
    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """Process vector agent requests"""


        try:
            if not self.orchestrator:
                return AgentResponse(
                    success=False,
                    error="Vector agent not initialized"
                )
            
            # Delegate to orchestrator
            return await self.orchestrator.process_request(request)
            
        except Exception as e:
            self.logger.error(f"Vector request processing failed: {e}")
            return AgentResponse(
                success=False,
                error=f"Vector processing error: {str(e)}"
            )
    
    async def shutdown(self) -> None:
        """Shutdown the vector agent"""


        try:
            if self.service_registry:
                await self.service_registry.shutdown()
            
            await super().shutdown()
            self.logger.info("Vector agent shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Vector agent shutdown error: {e}")
    
    async def health_check(self) -> dict:
        """Perform health check on vector agent"""


        try:
            if not self.service_registry:
                return {"status": "unhealthy", "reason": "Not initialized"}
            
            return await self.service_registry.health_check()
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def get_statistics(self) -> dict:
        """Get vector agent statistics"""


        try:
            if not self.service_registry:
                return {"error": "Vector agent not initialized"}
            
            return await self.service_registry.get_statistics()
            
        except Exception as e:
            return {"error": str(e)}


# Module exports
__all__ = [
    # Main agent class
    "VectorAgent",
    
    # Core components
    "VectorOrchestrator",
    "FAISSManager",
    "FAISSIndexManager", 
    "SimilarityEngine",
    "ContentTypeSimilarityProcessor",
    "VectorIndexer",
    "VectorDocumentStore",
    "SearchOptimizer",
    "QueryCache",
    "QueryOptimizer",
    "ResultEnhancer",
    
    # Data models
    "VectorDocument",
    "VectorSearchRequest",
    "VectorSearchResult",
    "VectorMetrics",
    "VectorStatistics",
    "FAISSIndexConfig",
    "SimilarityConfig",
    "CacheConfig",
    "ContentTypeConfig",
    
    # Configuration
    "VectorConfig",
    "get_config_for_environment",
    
    # Exceptions
    "VectorAgentBaseException",
    "VectorConfigurationError",
    "VectorProcessingError",
    "VectorDimensionError",
    "FAISSIndexError",
    "SimilarityComputationError",
    "VectorStorageError",
    "VectorValidationError",
    "VectorTimeoutError",
    "VectorResourceError",
    
    # Service registry
    "VectorServiceRegistry",
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

from .vector_orchestrator import VectorOrchestrator
from .faiss_manager import FAISSManager
from .similarity_engine import SimilarityEngine
from .vector_indexer import VectorIndexer
from .search_optimizer import SearchOptimizer

__all__ = [
    "VectorOrchestrator",
    "FAISSManager", 
    "SimilarityEngine",
    "VectorIndexer",
    "SearchOptimizer"
]

def create_vector_agent():
    """Factory function to create configured vector agent"""


    return VectorOrchestrator()
