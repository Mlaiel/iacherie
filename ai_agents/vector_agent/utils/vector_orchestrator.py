"""Vector Orchestrator - High-Performance Vector Database Management System

Ultra-advanced vector orchestration engine for content fingerprinting, similarity matching,
and AI-powered search capabilities with industrial-grade performance and scalability.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Any attempt to steal the concept, idea, or code without explicit written authorization
from Fahed Mlaiel will result in immediate legal prosecution under German and international law.
"""
import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
import numpy as np
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor

from ..base import BaseAgent, AgentRequest, AgentResponse
from .faiss_manager import FAISSManager
from .similarity_engine import SimilarityEngine
from .vector_indexer import VectorIndexer
from .search_optimizer import SearchOptimizer
from .models import (
    VectorDocument, VectorSearchRequest, VectorSearchResult,
    SimilarityMatch, VectorIndexConfig, VectorMetrics
)
from .config import VectorConfig
from .exceptions import VectorProcessingError, VectorIndexError

logger = logging.getLogger(__name__)


@dataclass
class VectorProcessingTask:
    """Task for vector processing operations"""
    task_id: str
    content_id: str
    content_type: str
    vector_data: np.ndarray
    metadata: Dict[str, Any]
    priority: int = 1
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


class VectorOrchestrator(BaseAgent):
    """
    Ultra-Advanced Vector Database Management Orchestrator
    
    Provides comprehensive vector storage, indexing, and similarity search capabilities
    for content fingerprinting and AI-powered matching operations.
    
    Key Features:
    - High-performance FAISS vector indexing
    - Multi-modal content vector management
    - Real-time similarity search
    - Batch processing optimization
    - Advanced caching strategies
    - Cross-content-type matching
    """
    
    def __init__(self, config: Optional[VectorConfig] = None):
        """Initialize Vector Orchestrator with enterprise configuration"""
        super().__init__(
            agent_id="vector_orchestrator",
            agent_type="vector_management",
            version="1.0.0",
            config=config.to_dict() if config else {}
        )
        
        self.config = config or VectorConfig()
        self.faiss_manager = FAISSManager(self.config)
        self.similarity_engine = SimilarityEngine(self.config)
        self.vector_indexer = VectorIndexer(self.config)
        self.search_optimizer = SearchOptimizer(self.config)
        
        # Performance tracking
        self.processing_stats = VectorMetrics()
        self.active_tasks: Dict[str, VectorProcessingTask] = {}
        
        # Thread pool for CPU-intensive operations
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.config.max_worker_threads,
            thread_name_prefix="VectorWorker"
        )
        
        # Processing queues
        self.priority_queue = asyncio.PriorityQueue()
        self.batch_queue: List[VectorProcessingTask] = []
        
        logger.info(f"Vector Orchestrator initialized - {self.agent_id}")
    
    async def initialize(self) -> None:
        """Initialize vector orchestrator and all components"""
        try:
            await super().initialize()
            
            # Initialize all vector components
            await self.faiss_manager.initialize()
            await self.similarity_engine.initialize()
            await self.vector_indexer.initialize()
            await self.search_optimizer.initialize()
            
            # Start background processing tasks
            asyncio.create_task(self._process_vector_queue())
            asyncio.create_task(self._process_batch_operations())
            asyncio.create_task(self._optimize_indices_periodically())
            asyncio.create_task(self._collect_metrics())
            
            self.status = "active"
            logger.info("Vector Orchestrator fully initialized")
            
        except Exception as e:
            logger.error(f"Vector Orchestrator initialization failed: {e}")
            raise VectorProcessingError(f"Initialization failed: {str(e)}")
    
    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """Process vector operation requests"""
        start_time = time.time()
        
        try:
            action = request.action.lower()
            
            # Route request to appropriate handler
            if action == "store_vector":
                result = await self._handle_store_vector(request)
            elif action == "search_similar":
                result = await self._handle_similarity_search(request)
            elif action == "batch_index":
                result = await self._handle_batch_indexing(request)
            elif action == "cross_modal_search":
                result = await self._handle_cross_modal_search(request)
            elif action == "optimize_index":
                result = await self._handle_index_optimization(request)
            elif action == "get_statistics":
                result = await self._handle_get_statistics(request)
            else:
                raise VectorProcessingError(f"Unknown action: {action}")
            
            processing_time = time.time() - start_time
            self.processing_stats.total_requests += 1
            self.processing_stats.total_processing_time += processing_time
            
            return AgentResponse(
                success=True,
                data=result,
                metadata={
                    "processing_time": processing_time,
                    "action": action,
                    "agent_id": self.agent_id
                }
            )
            
        except Exception as e:
            logger.error(f"Vector request processing failed: {e}")
            return AgentResponse(
                success=False,
                error=str(e),
                metadata={"action": request.action}
            )
    
    async def _handle_store_vector(self, request: AgentRequest) -> Dict[str, Any]:
        """Handle vector storage requests"""
        content_id = request.data.get("content_id")
        content_type = request.data.get("content_type")
        vector_data = request.data.get("vector_data")
        metadata = request.data.get("metadata", {})
        
        if not all([content_id, content_type, vector_data is not None]):
            raise VectorProcessingError("Missing required fields for vector storage")
        
        # Convert to numpy array if needed
        if not isinstance(vector_data, np.ndarray):
            vector_data = np.array(vector_data, dtype=np.float32)
        
        # Create vector document
        document = VectorDocument(
            document_id=content_id,
            content_type=content_type,
            vector_data=vector_data,
            metadata=metadata,
            created_at=datetime.now(timezone.utc)
        )
        
        # Store in vector index
        index_result = await self.vector_indexer.add_document(document)
        
        # Update FAISS indices
        await self.faiss_manager.add_vector(
            content_id, vector_data, content_type, metadata
        )
        
        # Update statistics
        self.processing_stats.vectors_stored += 1
        
        return {
            "content_id": content_id,
            "index_id": index_result.get("index_id"),
            "vector_dimension": len(vector_data),
            "storage_success": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _handle_similarity_search(self, request: AgentRequest) -> Dict[str, Any]:
        """Handle similarity search requests"""
        search_request = VectorSearchRequest(**request.data)
        
        # Perform similarity search
        start_time = time.time()
        search_results = await self.similarity_engine.search_similar(search_request)
        search_time = time.time() - start_time
        
        # Optimize search results
        optimized_results = await self.search_optimizer.optimize_results(
            search_results, search_request
        )
        
        # Update statistics
        self.processing_stats.similarity_searches += 1
        self.processing_stats.average_search_time = (
            (self.processing_stats.average_search_time * (self.processing_stats.similarity_searches - 1) + search_time) /
            self.processing_stats.similarity_searches
        )
        
        return {
            "query_id": search_request.query_id,
            "total_matches": len(optimized_results),
            "search_time": search_time,
            "results": [asdict(result) for result in optimized_results],
            "search_parameters": asdict(search_request)
        }
    
    async def _handle_batch_indexing(self, request: AgentRequest) -> Dict[str, Any]:
        """Handle batch vector indexing operations"""
        batch_data = request.data.get("batch_data", [])
        batch_size = request.data.get("batch_size", self.config.batch_size)
        
        if not batch_data:
            raise VectorProcessingError("No batch data provided")
        
        # Process in batches
        results = []
        total_processed = 0
        
        for i in range(0, len(batch_data), batch_size):
            batch = batch_data[i:i + batch_size]
            batch_result = await self._process_vector_batch(batch)
            results.extend(batch_result)
            total_processed += len(batch)
            
            # Yield control for other operations
            await asyncio.sleep(0.01)
        
        return {
            "batch_id": request.data.get("batch_id", f"batch_{int(time.time())}"),
            "total_processed": total_processed,
            "successful": len([r for r in results if r.get("success", False)]),
            "failed": len([r for r in results if not r.get("success", False)]),
            "results": results
        }
    
    async def _handle_cross_modal_search(self, request: AgentRequest) -> Dict[str, Any]:
        """Handle cross-modal similarity search"""
        query_vector = request.data.get("query_vector")
        content_types = request.data.get("content_types", ["audio", "video", "image", "text"])
        similarity_threshold = request.data.get("similarity_threshold", 0.75)
        max_results = request.data.get("max_results", 10)
        
        if query_vector is None:
            raise VectorProcessingError("Query vector is required for cross-modal search")
        
        # Convert to numpy array
        query_vector = np.array(query_vector, dtype=np.float32)
        
        # Search across multiple content types
        all_results = []
        
        for content_type in content_types:
            type_results = await self.faiss_manager.search_by_type(
                query_vector, content_type, max_results, similarity_threshold
            )
            
            for result in type_results:
                all_results.append(SimilarityMatch(
                    document_id=result["document_id"],
                    similarity_score=result["similarity_score"],
                    content_type=content_type,
                    metadata=result.get("metadata", {})
                ))
        
        # Sort by similarity score
        all_results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return {
            "cross_modal_results": all_results[:max_results],
            "content_types_searched": content_types,
            "total_matches": len(all_results),
            "query_vector_dimension": len(query_vector)
        }
    
    async def _handle_index_optimization(self, request: AgentRequest) -> Dict[str, Any]:
        """Handle index optimization requests"""
        optimization_type = request.data.get("type", "full")
        content_types = request.data.get("content_types", [])
        
        start_time = time.time()
        
        if optimization_type == "full":
            # Full optimization of all indices
            optimization_results = await self.faiss_manager.optimize_all_indices()
        elif optimization_type == "selective":
            # Selective optimization for specific content types
            optimization_results = await self.faiss_manager.optimize_indices(content_types)
        else:
            raise VectorProcessingError(f"Unknown optimization type: {optimization_type}")
        
        optimization_time = time.time() - start_time
        
        return {
            "optimization_type": optimization_type,
            "optimization_time": optimization_time,
            "indices_optimized": optimization_results.get("optimized_count", 0),
            "performance_improvement": optimization_results.get("improvement_ratio", 0),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _handle_get_statistics(self, request: AgentRequest) -> Dict[str, Any]:
        """Handle statistics retrieval requests"""
        include_detailed = request.data.get("include_detailed", False)
        
        stats = asdict(self.processing_stats)
        
        # Add FAISS statistics
        faiss_stats = await self.faiss_manager.get_statistics()
        stats["faiss_statistics"] = faiss_stats
        
        # Add index statistics
        index_stats = await self.vector_indexer.get_statistics()
        stats["index_statistics"] = index_stats
        
        if include_detailed:
            # Add detailed performance metrics
            stats["detailed_metrics"] = await self._get_detailed_metrics()
        
        return stats
    
    async def _process_vector_queue(self):
        """Process vector operations from priority queue"""
        while not self.shutdown_requested:
            try:
                # Get task from priority queue (timeout to prevent blocking)
                try:
                    priority, task = await asyncio.wait_for(
                        self.priority_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Process the task
                await self._execute_vector_task(task)
                
                # Mark task as done
                self.priority_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing vector queue: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_batch_operations(self):
        """Process batch operations periodically"""
        while not self.shutdown_requested:
            try:
                if len(self.batch_queue) >= self.config.batch_size:
                    # Process accumulated batch
                    batch = self.batch_queue[:self.config.batch_size]
                    self.batch_queue = self.batch_queue[self.config.batch_size:]
                    
                    await self._process_vector_batch([task for task in batch])
                
                await asyncio.sleep(self.config.batch_processing_interval)
                
            except Exception as e:
                logger.error(f"Error processing batch operations: {e}")
                await asyncio.sleep(1.0)
    
    async def _optimize_indices_periodically(self):
        """Periodically optimize vector indices"""
        while not self.shutdown_requested:
            try:
                # Wait for optimization interval
                await asyncio.sleep(self.config.optimization_interval)
                
                # Perform automatic optimization
                await self.faiss_manager.auto_optimize()
                
                logger.info("Periodic index optimization completed")
                
            except Exception as e:
                logger.error(f"Error in periodic optimization: {e}")
    
    async def _collect_metrics(self):
        """Collect and update performance metrics"""
        while not self.shutdown_requested:
            try:
                # Update metrics from all components
                faiss_metrics = await self.faiss_manager.get_metrics()
                similarity_metrics = await self.similarity_engine.get_metrics()
                indexer_metrics = await self.vector_indexer.get_metrics()
                
                # Aggregate metrics
                self.processing_stats.update_from_components(
                    faiss_metrics, similarity_metrics, indexer_metrics
                )
                
                await asyncio.sleep(self.config.metrics_collection_interval)
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(5.0)
    
    async def _execute_vector_task(self, task: VectorProcessingTask):
        """Execute individual vector processing task"""
        try:
            self.active_tasks[task.task_id] = task
            
            # Process based on task type
            if task.content_type in ["audio", "music"]:
                result = await self._process_audio_vector(task)
            elif task.content_type in ["video", "visual"]:
                result = await self._process_video_vector(task)
            elif task.content_type in ["image", "photo"]:
                result = await self._process_image_vector(task)
            elif task.content_type in ["text", "document"]:
                result = await self._process_text_vector(task)
            else:
                result = await self._process_generic_vector(task)
            
            # Store result
            await self.vector_indexer.store_processing_result(task.task_id, result)
            
        except Exception as e:
            logger.error(f"Task execution failed: {task.task_id} - {e}")
        finally:
            # Clean up task
            self.active_tasks.pop(task.task_id, None)
    
    async def _process_vector_batch(self, batch: List[VectorProcessingTask]) -> List[Dict[str, Any]]:
        """Process a batch of vector operations"""
        results = []
        
        try:
            # Group by content type for efficient processing
            type_groups = {}
            for task in batch:
                content_type = task.content_type
                if content_type not in type_groups:
                    type_groups[content_type] = []
                type_groups[content_type].append(task)
            
            # Process each type group
            for content_type, tasks in type_groups.items():
                type_results = await self._process_type_batch(content_type, tasks)
                results.extend(type_results)
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            # Return error results for all tasks
            results = [{"success": False, "error": str(e)} for _ in batch]
        
        return results
    
    async def _process_type_batch(self, content_type: str, tasks: List[VectorProcessingTask]) -> List[Dict[str, Any]]:
        """Process batch of tasks for specific content type"""
        results = []
        
        try:
            # Extract vectors and metadata
            vectors = np.array([task.vector_data for task in tasks], dtype=np.float32)
            content_ids = [task.content_id for task in tasks]
            metadata_list = [task.metadata for task in tasks]
            
            # Batch add to FAISS index
            batch_result = await self.faiss_manager.add_batch_vectors(
                content_ids, vectors, content_type, metadata_list
            )
            
            # Create individual results
            for i, task in enumerate(tasks):
                results.append({
                    "task_id": task.task_id,
                    "content_id": task.content_id,
                    "success": batch_result.get("success", False),
                    "index_position": batch_result.get("positions", [])[i] if batch_result.get("positions") else -1
                })
                
        except Exception as e:
            logger.error(f"Type batch processing failed for {content_type}: {e}")
            results = [{"success": False, "error": str(e)} for _ in tasks]
        
        return results
    
    async def _process_audio_vector(self, task: VectorProcessingTask) -> Dict[str, Any]:
        """Process audio-specific vector operations"""
        # Audio-specific processing logic
        return await self.similarity_engine.process_audio_similarity(
            task.vector_data, task.metadata
        )
    
    async def _process_video_vector(self, task: VectorProcessingTask) -> Dict[str, Any]:
        """Process video-specific vector operations"""
        # Video-specific processing logic
        return await self.similarity_engine.process_video_similarity(
            task.vector_data, task.metadata
        )
    
    async def _process_image_vector(self, task: VectorProcessingTask) -> Dict[str, Any]:
        """Process image-specific vector operations"""
        # Image-specific processing logic
        return await self.similarity_engine.process_image_similarity(
            task.vector_data, task.metadata
        )
    
    async def _process_text_vector(self, task: VectorProcessingTask) -> Dict[str, Any]:
        """Process text-specific vector operations"""
        # Text-specific processing logic
        return await self.similarity_engine.process_text_similarity(
            task.vector_data, task.metadata
        )
    
    async def _process_generic_vector(self, task: VectorProcessingTask) -> Dict[str, Any]:
        """Process generic vector operations"""
        # Generic processing logic
        return await self.similarity_engine.process_generic_similarity(
            task.vector_data, task.metadata
        )
    
    async def _get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        return {
            "active_tasks_count": len(self.active_tasks),
            "queue_size": self.priority_queue.qsize(),
            "batch_queue_size": len(self.batch_queue),
            "thread_pool_active": self.thread_pool._threads,
            "memory_usage": await self._get_memory_usage(),
            "cache_statistics": await self.search_optimizer.get_cache_stats()
        }
    
    async def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": process.memory_percent()
        }
    
    async def shutdown(self):
        """Graceful shutdown of vector orchestrator"""
        try:
            self.shutdown_requested = True
            
            # Wait for active tasks to complete
            if self.active_tasks:
                logger.info(f"Waiting for {len(self.active_tasks)} active tasks to complete")
                await asyncio.sleep(2.0)
            
            # Shutdown components
            await self.faiss_manager.shutdown()
            await self.similarity_engine.shutdown()
            await self.vector_indexer.shutdown()
            await self.search_optimizer.shutdown()
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            await super().shutdown()
            logger.info("Vector Orchestrator shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during Vector Orchestrator shutdown: {e}")
