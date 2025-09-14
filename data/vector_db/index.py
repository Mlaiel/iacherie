"""
Vector Database Module - Main Entry Point
=========================================

Enterprise-grade vector database orchestrator for Ainflue platform.
Provides unified interface for multi-backend vector operations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel and is protected by 
international copyright law. Any unauthorized use, reproduction, distribution 
or modification is strictly prohibited and will result in legal action.

For licensing inquiries: mlaiel@live.de
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import numpy as np
from datetime import datetime
import uuid

from .config_manager import ConfigManager
from .vector_storage import VectorStorage
from .embedding_engine import EmbeddingEngine
from .similarity_engine import SimilarityEngine
from .query_processor import QueryProcessor
from .cache_manager import CacheManager
from .security_manager import SecurityManager
from .performance_monitor import PerformanceMonitor
from .analytics_engine import AnalyticsEngine
from .optimization_engine import OptimizationEngine
from .metadata_processor import MetadataProcessor

logger = logging.getLogger(__name__)


class VectorDatabase:
    """
    Main orchestrator for the Vector Database Module.
    
    Provides unified interface for all vector operations including:
    - Multi-backend storage (FAISS, ChromaDB, Pinecone)
    - Advanced similarity search with ML optimization
    - Content fingerprinting and protection
    - Real-time analytics and monitoring
    - Enterprise security and compliance
    
    Usage:
        db = VectorDatabase(config_path='config/vector_db.yaml')
        await db.initialize()
        results = await db.search_similar(query_vector, top_k=10)
    """
    
    def __init__(
        self,
        config_path -> None: Optional[str] = None,
        backend -> None: str = "faiss",
        security_enabled -> None: bool = True,
        monitoring_enabled -> None: bool = True
    ) -> None:
        """
        Initialize Vector Database with configuration.
        
        Args:
            config_path: Path to configuration file
            backend: Vector backend ('faiss', 'chromadb', 'pinecone')
            security_enabled: Enable enterprise security features
            monitoring_enabled: Enable performance monitoring
        """
        self.config_path = config_path
        self.backend_type = backend
        self.security_enabled = security_enabled
        self.monitoring_enabled = monitoring_enabled
        
        # Core components
        self.config: Optional[ConfigManager] = None
        self.storage: Optional[VectorStorage] = None
        self.embedding_engine: Optional[EmbeddingEngine] = None
        self.similarity_engine: Optional[SimilarityEngine] = None
        self.query_processor: Optional[QueryProcessor] = None
        self.cache_manager: Optional[CacheManager] = None
        self.security_manager: Optional[SecurityManager] = None
        self.performance_monitor: Optional[PerformanceMonitor] = None
        self.analytics_engine: Optional[AnalyticsEngine] = None
        self.optimization_engine: Optional[OptimizationEngine] = None
        self.metadata_processor: Optional[MetadataProcessor] = None
        
        # State management
        self._initialized = False
        self._health_status = "unknown"
        self._last_health_check = None
        
        logger.info(f"VectorDatabase initialized with backend: {backend}")
    
    async def initialize(self) -> bool:
        """
        Initialize all components of the vector database.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Initialize configuration
            self.config = ConfigManager(config_path=self.config_path)
            await self.config.load_config()
            
            # Initialize security if enabled
            if self.security_enabled:
                self.security_manager = SecurityManager(self.config)
                await self.security_manager.initialize()
            
            # Initialize performance monitoring
            if self.monitoring_enabled:
                self.performance_monitor = PerformanceMonitor(self.config)
                await self.performance_monitor.start()
            
            # Initialize cache manager
            self.cache_manager = CacheManager(self.config)
            await self.cache_manager.initialize()
            
            # Initialize metadata processor
            self.metadata_processor = MetadataProcessor(self.config)
            await self.metadata_processor.initialize()
            
            # Initialize embedding engine
            self.embedding_engine = EmbeddingEngine(self.config)
            await self.embedding_engine.initialize()
            
            # Initialize vector storage with specified backend
            self.storage = VectorStorage(
                backend_type=self.backend_type,
                config=self.config,
                security_manager=self.security_manager
            )
            await self.storage.initialize()
            
            # Initialize similarity engine
            self.similarity_engine = SimilarityEngine(
                storage=self.storage,
                config=self.config
            )
            await self.similarity_engine.initialize()
            
            # Initialize query processor
            self.query_processor = QueryProcessor(
                similarity_engine=self.similarity_engine,
                cache_manager=self.cache_manager,
                config=self.config
            )
            await self.query_processor.initialize()
            
            # Initialize analytics engine
            self.analytics_engine = AnalyticsEngine(
                storage=self.storage,
                config=self.config
            )
            await self.analytics_engine.initialize()
            
            # Initialize optimization engine
            self.optimization_engine = OptimizationEngine(
                storage=self.storage,
                analytics=self.analytics_engine,
                config=self.config
            )
            await self.optimization_engine.initialize()
            
            self._initialized = True
            await self._perform_health_check()
            
            logger.info("VectorDatabase initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize VectorDatabase: {e}")
            self._health_status = "error"
            return False
    
    async def add_content(
        self,
        content: Union[str, bytes, np.ndarray],
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        content_id: Optional[str] = None
    ) -> str:
        """
        Add content to the vector database.
        
        Args:
            content: Content to add (text, audio, image, or vector)
            content_type: Type of content ('text', 'audio', 'image', 'vector')
            metadata: Optional metadata dictionary
            content_id: Optional custom ID, auto-generated if None
        
        Returns:
            str: Content ID
        """
        if not self._initialized:
            raise RuntimeError("VectorDatabase not initialized")
        
        # Generate ID if not provided
        if content_id is None:
            content_id = str(uuid.uuid4())
        
        try:
            # Start monitoring
            if self.performance_monitor:
                await self.performance_monitor.start_operation("add_content")
            
            # Process metadata
            if metadata is None:
                metadata = {}
            
            processed_metadata = await self.metadata_processor.process_metadata(
                content=content,
                content_type=content_type,
                custom_metadata=metadata
            )
            
            # Generate embeddings if content is not already a vector
            if content_type != 'vector':
                embedding = await self.embedding_engine.generate_embedding(
                    content=content,
                    content_type=content_type
                )
            else:
                embedding = content
            
            # Store vector with metadata
            await self.storage.add_vector(
                vector_id=content_id,
                vector=embedding,
                metadata=processed_metadata
            )
            
            # Update analytics
            if self.analytics_engine:
                await self.analytics_engine.record_addition(
                    content_id=content_id,
                    content_type=content_type,
                    metadata=processed_metadata
                )
            
            # End monitoring
            if self.performance_monitor:
                await self.performance_monitor.end_operation("add_content")
            
            logger.info(f"Content added successfully: {content_id}")
            return content_id
            
        except Exception as e:
            logger.error(f"Failed to add content: {e}")
            if self.performance_monitor:
                await self.performance_monitor.record_error("add_content", str(e))
            raise
    
    async def search_similar(
        self,
        query: Union[str, bytes, np.ndarray],
        query_type: str = "auto",
        top_k: int = 10,
        threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar content in the database.
        
        Args:
            query: Query content (text, audio, image, or vector)
            query_type: Type of query ('text', 'audio', 'image', 'vector', 'auto')
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            filters: Optional metadata filters
        
        Returns:
            List of similar content with scores and metadata
        """
        if not self._initialized:
            raise RuntimeError("VectorDatabase not initialized")
        
        try:
            # Start monitoring
            if self.performance_monitor:
                await self.performance_monitor.start_operation("search_similar")
            
            # Auto-detect query type if needed
            if query_type == "auto":
                query_type = await self._detect_content_type(query)
            
            # Generate query embedding if needed
            if query_type != 'vector':
                query_embedding = await self.embedding_engine.generate_embedding(
                    content=query,
                    content_type=query_type
                )
            else:
                query_embedding = query
            
            # Process query through query processor
            results = await self.query_processor.process_query(
                query_vector=query_embedding,
                top_k=top_k,
                threshold=threshold,
                filters=filters
            )
            
            # Update analytics
            if self.analytics_engine:
                await self.analytics_engine.record_search(
                    query_type=query_type,
                    results_count=len(results),
                    threshold=threshold
                )
            
            # End monitoring
            if self.performance_monitor:
                await self.performance_monitor.end_operation("search_similar")
            
            logger.info(f"Search completed: {len(results)} results found")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search similar content: {e}")
            if self.performance_monitor:
                await self.performance_monitor.record_error("search_similar", str(e))
            raise
    
    async def bulk_add(
        self,
        contents: List[Tuple[Union[str, bytes, np.ndarray], str, Optional[Dict[str, Any]]]],
        batch_size: int = 100
    ) -> List[str]:
        """
        Add multiple contents in batches for efficiency.
        
        Args:
            contents: List of (content, content_type, metadata) tuples
            batch_size: Number of items to process per batch
        
        Returns:
            List of content IDs
        """
        if not self._initialized:
            raise RuntimeError("VectorDatabase not initialized")
        
        content_ids = []
        
        try:
            # Process in batches
            for i in range(0, len(contents), batch_size):
                batch = contents[i:i + batch_size]
                batch_ids = []
                
                for content, content_type, metadata in batch:
                    content_id = await self.add_content(
                        content=content,
                        content_type=content_type,
                        metadata=metadata
                    )
                    batch_ids.append(content_id)
                
                content_ids.extend(batch_ids)
                logger.info(f"Processed batch {i//batch_size + 1}: {len(batch_ids)} items")
            
            logger.info(f"Bulk add completed: {len(content_ids)} items added")
            return content_ids
            
        except Exception as e:
            logger.error(f"Failed to bulk add content: {e}")
            raise
    
    async def get_analytics(self, metric_type: str = "summary") -> Dict[str, Any]:
        """
        Get analytics and performance metrics.
        
        Args:
            metric_type: Type of metrics ('summary', 'performance', 'usage')
        
        Returns:
            Analytics data dictionary
        """
        if not self._initialized or not self.analytics_engine:
            raise RuntimeError("VectorDatabase or analytics not initialized")
        
        return await self.analytics_engine.get_metrics(metric_type)
    
    async def optimize(self, optimization_type: str = "auto") -> Dict[str, Any]:
        """
        Run optimization algorithms on the database.
        
        Args:
            optimization_type: Type of optimization ('auto', 'index', 'query', 'cache')
        
        Returns:
            Optimization results
        """
        if not self._initialized or not self.optimization_engine:
            raise RuntimeError("VectorDatabase or optimization not initialized")
        
        return await self.optimization_engine.optimize(optimization_type)
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.
        
        Returns:
            Health status dictionary
        """
        await self._perform_health_check()
        
        return {
            "status": self._health_status,
            "last_check": self._last_health_check,
            "initialized": self._initialized,
            "components": await self._get_component_health()
        }
    
    async def _perform_health_check(self) -> None:
        """Internal health check implementation."""
        try:
            checks = []
            
            # Check storage
            if self.storage:
                checks.append(await self.storage.health_check())
            
            # Check embedding engine
            if self.embedding_engine:
                checks.append(await self.embedding_engine.health_check())
            
            # Check cache
            if self.cache_manager:
                checks.append(await self.cache_manager.health_check())
            
            # Determine overall status
            if all(checks):
                self._health_status = "healthy"
            elif any(checks):
                self._health_status = "degraded"
            else:
                self._health_status = "unhealthy"
            
            self._last_health_check = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self._health_status = "error"
            self._last_health_check = datetime.utcnow()
    
    async def _get_component_health(self) -> Dict[str, str]:
        """Get health status of individual components."""
        health = {}
        
        components = [
            ("config", self.config),
            ("storage", self.storage),
            ("embedding_engine", self.embedding_engine),
            ("similarity_engine", self.similarity_engine),
            ("query_processor", self.query_processor),
            ("cache_manager", self.cache_manager),
            ("security_manager", self.security_manager),
            ("performance_monitor", self.performance_monitor),
            ("analytics_engine", self.analytics_engine),
            ("optimization_engine", self.optimization_engine),
            ("metadata_processor", self.metadata_processor)
        ]
        
        for name, component in components:
            if component and hasattr(component, 'health_check'):
                try:
                    health[name] = "healthy" if await component.health_check() else "unhealthy"
                except Exception:
                    health[name] = "error"
            else:
                health[name] = "not_initialized" if component is None else "no_health_check"
        
        return health
    
    async def _detect_content_type(self, content: Union[str, bytes, np.ndarray]) -> str:
        """Auto-detect content type from input."""
        if isinstance(content, np.ndarray):
            return "vector"
        elif isinstance(content, str):
            return "text"
        elif isinstance(content, bytes):
            # Simple heuristic - could be enhanced with magic number detection
            if len(content) > 44 and content[:4] in [b'RIFF', b'fLaC', b'\xff\xfb']:
                return "audio"
            else:
                return "image"
        else:
            return "unknown"
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the vector database."""
        logger.info("Shutting down VectorDatabase...")
        
        # Shutdown components in reverse order
        components = [
            self.optimization_engine,
            self.analytics_engine,
            self.performance_monitor,
            self.security_manager,
            self.cache_manager,
            self.query_processor,
            self.similarity_engine,
            self.storage,
            self.embedding_engine,
            self.metadata_processor,
            self.config
        ]
        
        for component in components:
            if component and hasattr(component, 'shutdown'):
                try:
                    await component.shutdown()
                except Exception as e:
                    logger.warning(f"Error shutting down component: {e}")
        
        self._initialized = False
        logger.info("VectorDatabase shutdown completed")
    
    def __repr__(self) -> str:
        return f"VectorDatabase(backend={self.backend_type}, initialized={self._initialized})"


# Convenience functions for quick usage
async def create_vector_db(
    backend: str = "faiss",
    config_path: Optional[str] = None
) -> VectorDatabase:
    """
    Create and initialize a VectorDatabase instance.
    
    Args:
        backend: Vector backend to use
        config_path: Path to configuration file
    
    Returns:
        Initialized VectorDatabase instance
    """
    db = VectorDatabase(backend=backend, config_path=config_path)
    await db.initialize()
    return db


async def quick_search(
    query: Union[str, bytes, np.ndarray],
    db_path: Optional[str] = None,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Quick similarity search with minimal setup.
    
    Args:
        query: Query content
        db_path: Database path
        top_k: Number of results
    
    Returns:
        Search results
    """
    db = await create_vector_db(config_path=db_path)
    try:
        return await db.search_similar(query=query, top_k=top_k)
    finally:
        await db.shutdown()


# Export main class and functions
__all__ = [
    'VectorDatabase',
    'create_vector_db',
    'quick_search'
]