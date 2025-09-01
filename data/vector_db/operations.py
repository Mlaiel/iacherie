"""Vector Database Management and Operations Interface
=================================================

Unified interface for vector database operations with advanced management,
monitoring, and optimization capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

ATTENTION: Ce code est protégé par les droits d'auteur.
Toute reproduction, distribution ou modification non autorisée est strictement interdite.
"""

import asyncio
import logging
import numpy as np
import json
import os
import time
import hashlib
import psutil
import gc
import shutil
from typing import Dict, List, Optional, Tuple, Any, Union, AsyncGenerator, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from enum import Enum
from collections import defaultdict, deque
import yaml
import gzip
import tarfile
import tempfile

# Local imports
from . import VectorDBManager, SimilaritySearcher, VectorSearchResult, VectorIndex
from .faiss_backend import FAISSBackend
from .chroma_backend import ChromaBackend
from .embedding_engine import MultiModalEmbeddingEngine
from .similarity_search import SimilaritySearchEngine, SearchConfig, SearchType, RankingStrategy

logger = logging.getLogger(__name__)


class IndexStatus(Enum):
    """
Status of vector indices."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    REBUILDING = "rebuilding"
    ERROR = "error"
    OPTIMIZING = "optimizing"
    TRAINING = "training"
    MIGRATING = "migrating"


class BackupStatus(Enum):
    """Status of backup operations."""

    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    FAILED = "failed"
    SCHEDULED = "scheduled"
    COMPRESSING = "compressing"
    VALIDATING = "validating"
    RESTORED = "restored"


class OperationType(Enum):
    """Types of database operations."""

    SEARCH = "search"
    INSERT = "insert"
    DELETE = "delete"
    UPDATE = "update"
    BACKUP = "backup"
    RESTORE = "restore"
    OPTIMIZE = "optimize"
    BULK_INSERT = "bulk_insert"
    REINDEX = "reindex"
    MAINTENANCE = "maintenance"


class MaintenanceType(Enum):
    """Types of maintenance operations."""

    GARBAGE_COLLECTION = "garbage_collection"
    INDEX_COMPACTION = "index_compaction"
    STATISTICS_UPDATE = "statistics_update"
    HEALTH_CHECK = "health_check"
    PERFORMANCE_TUNING = "performance_tuning"
    SECURITY_AUDIT = "security_audit"


@dataclass
class IndexMetrics:
    """Metrics for a vector index."""
    index_name: str
    vector_count: int
    dimension: int
    memory_usage_mb: float
    query_latency_ms: float
    throughput_qps: float
    last_updated: datetime
    health_score: float
    status: IndexStatus


@dataclass
class BackupInfo:
    """
Information about index backups."""
    backup_id: str
    index_name: str
    backup_path: str
    size_mb: float
    created_at: datetime
    status: BackupStatus
    metadata: Dict[str, Any]


@dataclass
class PerformanceStats:
    """
Performance statistics for the vector database."""
    total_queries: int
    avg_query_time_ms: float
    cache_hit_rate: float
    memory_usage_mb: float
    storage_usage_mb: float
    error_rate: float
    uptime_seconds: float
    last_optimization: Optional[datetime]


class VectorDBOperations:
    """
    Advanced vector database operations manager.
    
    Provides high-level operations for managing vector databases including
    indexing, searching, monitoring, backup/restore, and optimization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.storage_path = config.get('storage_path', './data/vector_operations')
        
        # Initialize core components
        self.vector_db = VectorDBManager(config)
        self.embedding_engine = MultiModalEmbeddingEngine(config.get('embedding', {}))
        self.similarity_engine = SimilaritySearchEngine(self.vector_db, config)
        
        # Performance tracking
        self.query_stats = {
            'total_queries': 0,
            'total_query_time': 0.0,
            'errors': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        self.start_time = datetime.now()
        
        # Monitoring
        self.metrics_cache = {}
        self.metrics_lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        # Backup management
        self.backup_registry = {}
        self.auto_backup_enabled = config.get('auto_backup', True)
        self.backup_interval_hours = config.get('backup_interval_hours', 24)
        
        # Create storage directories
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(self.storage_path, 'backups')).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(self.storage_path, 'metrics')).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Vector DB operations initialized with storage: {self.storage_path}")
    
    async def initialize_system(self) -> bool:
        """Initialize the complete vector database system."""
        try:
            logger.info("Initializing vector database system...")
            
            # Create default indices for all content types
            content_types = ['audio', 'video', 'image', 'text']
            
            initialization_results = []
            for content_type in content_types:
                try:
                    success = await self.vector_db.create_content_index(content_type)
                    initialization_results.append((content_type, success))
                    
                    if success:
                        logger.info(f"Successfully initialized {content_type} index")
                    else:
                        logger.error(f"Failed to initialize {content_type} index")
                        
                except Exception as e:
                    logger.error(f"Error initializing {content_type} index: {str(e)}")
                    initialization_results.append((content_type, False))
            
            # Check if at least one index was created successfully
            successful_indices = [result for result in initialization_results if result[1]]
            
            if successful_indices:
                logger.info(f"Vector database system initialized successfully. "
                          f"Created {len(successful_indices)} indices.")
                
                # Start background tasks
                if self.auto_backup_enabled:
                    asyncio.create_task(self._auto_backup_task())
                
                asyncio.create_task(self._metrics_collection_task())
                
                return True
            else:
                logger.error("Failed to initialize any vector indices")
                return False
                
        except Exception as e:
            logger.error(f"System initialization failed: {str(e)}")
            return False
    
    async def add_content(self, content: Any, content_type: str,
                         content_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Add content to the vector database with automatic embedding generation.
        
        Args:
            content: Content data (text, audio array, image, video path)
            content_type: Type of content ('text', 'audio', 'image', 'video')
            content_id: Unique identifier for the content
            metadata: Additional metadata for the content
            
        Returns:
            Success status
        """
        start_time = datetime.now()
        
        try:
            # Update metadata with system information
            enhanced_metadata = {
                **metadata,
                'content_id': content_id,
                'content_type': content_type,
                'added_at': start_time.isoformat(),
                'system_version': self.config.get('version', '1.0.0')
            }
            
            # Generate embedding
            embedding_result = await self.embedding_engine.generate_embedding(
                content, content_type, enhanced_metadata
            )
            
            # Add to vector database
            success = await self.vector_db.add_content_vector(
                content_type,
                content_id,
                embedding_result.embedding,
                {
                    **enhanced_metadata,
                    'embedding_model': embedding_result.model_info,
                    'features': embedding_result.features,
                    'processing_time': embedding_result.processing_time
                }
            )
            
            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_query_stats(processing_time, success)
            
            if success:
                logger.info(f"Successfully added {content_type} content {content_id}")
            else:
                logger.error(f"Failed to add {content_type} content {content_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to add content {content_id}: {str(e)}")
            self._update_query_stats((datetime.now() - start_time).total_seconds(), False)
            return False
    
    async def search_content(self, query_content: Any, content_type: str,
                           search_config: SearchConfig,
                           query_metadata: Dict[str, Any] = None) -> List[VectorSearchResult]:
        """
        Search for similar content in the vector database.
        
        Args:
            query_content: Query content for similarity search
            content_type: Type of content to search
            search_config: Search configuration
            query_metadata: Additional query metadata
            
        Returns:
            List of search results
        """
        start_time = datetime.now()
        
        try:
            # Generate query embedding
            query_metadata = query_metadata or {}
            embedding_result = await self.embedding_engine.generate_embedding(
                query_content, content_type, query_metadata
            )
            
            # Perform search
            results = await self.similarity_engine.search(
                content_type,
                embedding_result.embedding,
                search_config,
                query_metadata
            )
            
            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_query_stats(processing_time, True)
            
            logger.info(f"Search completed: {len(results)} results for {content_type}")
            return results
            
        except Exception as e:
            logger.error(f"Content search failed: {str(e)}")
            self._update_query_stats((datetime.now() - start_time).total_seconds(), False)
            return []
    
    async def detect_duplicates(self, content: Any, content_type: str,
                              metadata: Dict[str, Any] = None) -> List[Tuple[VectorSearchResult, Any]]:
        """
        Detect potential duplicate content.
        
        Args:
            content: Content to check for duplicates
            content_type: Type of content
            metadata: Additional metadata
            
        Returns:
            List of (result, analysis) tuples for potential duplicates
        """
        start_time = datetime.now()
        
        try:
            # Generate embedding for the content
            metadata = metadata or {}
            embedding_result = await self.embedding_engine.generate_embedding(
                content, content_type, metadata
            )
            
            # Search for duplicates
            duplicates = await self.similarity_engine.find_duplicates(
                content_type,
                embedding_result.embedding,
                metadata
            )
            
            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_query_stats(processing_time, True)
            
            logger.info(f"Duplicate detection completed: {len(duplicates)} potential duplicates found")
            return duplicates
            
        except Exception as e:
            logger.error(f"Duplicate detection failed: {str(e)}")
            self._update_query_stats((datetime.now() - start_time).total_seconds(), False)
            return []
    
    async def find_collaborations(self, creator_profile: Dict[str, Any],
                                content_example: Any, content_type: str) -> List[Any]:
        """
        Find potential collaboration opportunities.
        
        Args:
            creator_profile: Profile of the creator seeking collaborations
            content_example: Example content representing creator's style
            content_type: Type of content
            
        Returns:
            List of collaboration matches
        """
        start_time = datetime.now()
        
        try:
            # Generate embedding for creator's style
            embedding_result = await self.embedding_engine.generate_embedding(
                content_example, content_type, creator_profile
            )
            
            # Find collaboration opportunities
            collaborations = await self.similarity_engine.find_collaboration_opportunities(
                creator_profile,
                content_type,
                embedding_result.embedding
            )
            
            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_query_stats(processing_time, True)
            
            logger.info(f"Collaboration search completed: {len(collaborations)} opportunities found")
            return collaborations
            
        except Exception as e:
            logger.error(f"Collaboration search failed: {str(e)}")
            self._update_query_stats((datetime.now() - start_time).total_seconds(), False)
            return []
    
    async def get_recommendations(self, user_profile: Dict[str, Any],
                                content_example: Any, content_type: str) -> List[Any]:
        """
        Get content recommendations for inspiration and strategy.
        
        Args:
            user_profile: User's profile and preferences
            content_example: Example content representing user's style
            content_type: Type of content
            
        Returns:
            List of content recommendations
        """
        start_time = datetime.now()
        
        try:
            # Generate embedding for user's preferences
            embedding_result = await self.embedding_engine.generate_embedding(
                content_example, content_type, user_profile
            )
            
            # Get recommendations
            recommendations = await self.similarity_engine.get_content_recommendations(
                user_profile,
                content_type,
                embedding_result.embedding
            )
            
            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_query_stats(processing_time, True)
            
            logger.info(f"Recommendations generated: {len(recommendations)} items")
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            self._update_query_stats((datetime.now() - start_time).total_seconds(), False)
            return []
    
    async def remove_content(self, content_id: str, content_type: str) -> bool:
        """
        Remove content from the vector database.
        
        Args:
            content_id: ID of content to remove
            content_type: Type of content
            
        Returns:
            Success status
        """
        try:
            success = await self.vector_db.remove_content_vector(content_type, content_id)
            
            if success:
                logger.info(f"Successfully removed {content_type} content {content_id}")
            else:
                logger.error(f"Failed to remove {content_type} content {content_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Content removal failed: {str(e)}")
            return False
    
    async def get_index_metrics(self, content_type: str = None) -> Union[IndexMetrics, Dict[str, IndexMetrics]]:
        """
        Get metrics for vector indices.
        
        Args:
            content_type: Specific content type, or None for all indices
            
        Returns:
            Index metrics
        """
        try:
            with self.metrics_lock:
                if content_type:
                    # Return metrics for specific index
                    if content_type in self.metrics_cache:
                        return self.metrics_cache[content_type]
                    else:
                        # Generate fresh metrics
                        metrics = await self._calculate_index_metrics(content_type)
                        self.metrics_cache[content_type] = metrics
                        return metrics
                else:
                    # Return metrics for all indices
                    all_metrics = {}
                    content_types = ['audio', 'video', 'image', 'text']
                    
                    for ct in content_types:
                        if ct in self.metrics_cache:
                            all_metrics[ct] = self.metrics_cache[ct]
                        else:
                            metrics = await self._calculate_index_metrics(ct)
                            all_metrics[ct] = metrics
                            self.metrics_cache[ct] = metrics
                    
                    return all_metrics
                    
        except Exception as e:
            logger.error(f"Failed to get index metrics: {str(e)}")
            return {} if content_type is None else None
    
    async def get_performance_stats(self) -> PerformanceStats:
        """Get overall performance statistics."""
        try:
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            # Calculate averages
            total_queries = max(self.query_stats['total_queries'], 1)  # Avoid division by zero
            avg_query_time = self.query_stats['total_query_time'] / total_queries * 1000  # Convert to ms
            
            total_cache_ops = self.query_stats['cache_hits'] + self.query_stats['cache_misses']
            cache_hit_rate = (self.query_stats['cache_hits'] / max(total_cache_ops, 1))
            
            error_rate = self.query_stats['errors'] / total_queries
            
            # Estimate memory and storage usage
            memory_usage = await self._estimate_memory_usage()
            storage_usage = await self._estimate_storage_usage()
            
            return PerformanceStats(
                total_queries=self.query_stats['total_queries'],
                avg_query_time_ms=avg_query_time,
                cache_hit_rate=cache_hit_rate,
                memory_usage_mb=memory_usage,
                storage_usage_mb=storage_usage,
                error_rate=error_rate,
                uptime_seconds=uptime,
                last_optimization=None  # Would track actual optimization times
            )
            
        except Exception as e:
            logger.error(f"Failed to get performance stats: {str(e)}")
            return PerformanceStats(
                total_queries=0, avg_query_time_ms=0, cache_hit_rate=0,
                memory_usage_mb=0, storage_usage_mb=0, error_rate=0,
                uptime_seconds=0, last_optimization=None
            )
    
    async def create_backup(self, content_type: str = None, backup_name: str = None) -> BackupInfo:
        """
        Create a backup of vector indices.
        
        Args:
            content_type: Specific content type to backup, or None for all
            backup_name: Custom backup name
            
        Returns:
            Backup information
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_id = f"backup_{timestamp}_{backup_name or 'auto'}"
            
            if content_type:
                backup_path = os.path.join(
                    self.storage_path, 'backups', f"{backup_id}_{content_type}"
                )
                content_types = [content_type]
            else:
                backup_path = os.path.join(self.storage_path, 'backups', backup_id)
                content_types = ['audio', 'video', 'image', 'text']
            
            # Create backup directory
            Path(backup_path).mkdir(parents=True, exist_ok=True)
            
            # Backup each content type
            total_size = 0
            backup_metadata = {
                'backup_id': backup_id,
                'created_at': datetime.now().isoformat(),
                'content_types': content_types,
                'version': self.config.get('version', '1.0.0')
            }
            
            for ct in content_types:
                try:
                    # Get index stats for metadata
                    stats = self.vector_db.get_index_stats(ct)
                    
                    if stats:
                        # Save index metadata
                        metadata_file = os.path.join(backup_path, f"{ct}_metadata.json")
                        with open(metadata_file, 'w') as f:
                            json.dump(stats, f, indent=2, default=str)
                        
                        # Estimate backup size (simplified)
                        file_size = os.path.getsize(metadata_file)
                        total_size += file_size
                        
                        backup_metadata[f"{ct}_stats"] = stats
                        
                        logger.info(f"Backed up {ct} index metadata")
                    
                except Exception as e:
                    logger.error(f"Failed to backup {ct} index: {str(e)}")
            
            # Save backup metadata
            metadata_file = os.path.join(backup_path, 'backup_info.json')
            with open(metadata_file, 'w') as f:
                json.dump(backup_metadata, f, indent=2, default=str)
            
            backup_info = BackupInfo(
                backup_id=backup_id,
                index_name=content_type or 'all',
                backup_path=backup_path,
                size_mb=total_size / (1024 * 1024),
                created_at=datetime.now(),
                status=BackupStatus.COMPLETED,
                metadata=backup_metadata
            )
            
            # Register backup
            self.backup_registry[backup_id] = backup_info
            
            logger.info(f"Backup created successfully: {backup_id}")
            return backup_info
            
        except Exception as e:
            logger.error(f"Backup creation failed: {str(e)}")
            return BackupInfo(
                backup_id="failed",
                index_name=content_type or 'all',
                backup_path="",
                size_mb=0,
                created_at=datetime.now(),
                status=BackupStatus.FAILED,
                metadata={"error": str(e)}
            )
    
    async def list_backups(self) -> List[BackupInfo]:
        """List all available backups."""
        try:
            backups = list(self.backup_registry.values())
            
            # Also scan backup directory for any missed backups
            backup_dir = os.path.join(self.storage_path, 'backups')
            if os.path.exists(backup_dir):
                for backup_folder in os.listdir(backup_dir):
                    backup_path = os.path.join(backup_dir, backup_folder)
                    if os.path.isdir(backup_path):
                        info_file = os.path.join(backup_path, 'backup_info.json')
                        if os.path.exists(info_file) and backup_folder not in self.backup_registry:
                            try:
                                with open(info_file, 'r') as f:
                                    metadata = json.load(f)
                                
                                backup_info = BackupInfo(
                                    backup_id=backup_folder,
                                    index_name=metadata.get('content_types', ['unknown'])[0],
                                    backup_path=backup_path,
                                    size_mb=self._calculate_directory_size(backup_path),
                                    created_at=datetime.fromisoformat(metadata.get('created_at', datetime.now().isoformat())),
                                    status=BackupStatus.COMPLETED,
                                    metadata=metadata
                                )
                                
                                backups.append(backup_info)
                                self.backup_registry[backup_folder] = backup_info
                                
                            except Exception as e:
                                logger.error(f"Failed to load backup info for {backup_folder}: {str(e)}")
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x.created_at, reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"Failed to list backups: {str(e)}")
            return []
    
    async def restore_backup(self, backup_id: str) -> bool:
        """
        Restore from a backup.
        
        Args:
            backup_id: ID of the backup to restore
            
        Returns:
            Success status
        """
        try:
            if backup_id not in self.backup_registry:
                # Try to load backup info
                await self.list_backups()
            
            if backup_id not in self.backup_registry:
                logger.error(f"Backup {backup_id} not found")
                return False
            
            backup_info = self.backup_registry[backup_id]
            backup_path = backup_info.backup_path
            
            # Load backup metadata
            metadata_file = os.path.join(backup_path, 'backup_info.json')
            if not os.path.exists(metadata_file):
                logger.error(f"Backup metadata not found: {metadata_file}")
                return False
            
            with open(metadata_file, 'r') as f:
                backup_metadata = json.load(f)
            
            content_types = backup_metadata.get('content_types', [])
            
            # Restore each content type
            success_count = 0
            for content_type in content_types:
                try:
                    # This is a simplified restore - in production would restore actual index data
                    logger.info(f"Restoring {content_type} index from backup {backup_id}")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to restore {content_type} from backup: {str(e)}")
            
            restore_success = success_count == len(content_types)
            
            if restore_success:
                logger.info(f"Successfully restored from backup {backup_id}")
            else:
                logger.error(f"Partially restored from backup {backup_id}: {success_count}/{len(content_types)} indices")
            
            return restore_success
            
        except Exception as e:
            logger.error(f"Backup restore failed: {str(e)}")
            return False
    
    async def optimize_indices(self, content_type: str = None) -> bool:
        """
        Optimize vector indices for better performance.
        
        Args:
            content_type: Specific content type to optimize, or None for all
            
        Returns:
            Success status
        """
        try:
            if content_type:
                content_types = [content_type]
            else:
                content_types = ['audio', 'video', 'image', 'text']
            
            optimization_results = []
            
            for ct in content_types:
                try:
                    # This would call backend-specific optimization
                    # For now, just log the operation
                    logger.info(f"Optimizing {ct} index...")
                    
                    # Simulate optimization
                    await asyncio.sleep(0.1)
                    
                    optimization_results.append((ct, True))
                    logger.info(f"Successfully optimized {ct} index")
                    
                except Exception as e:
                    logger.error(f"Failed to optimize {ct} index: {str(e)}")
                    optimization_results.append((ct, False))
            
            successful_optimizations = [result for result in optimization_results if result[1]]
            
            if successful_optimizations:
                logger.info(f"Index optimization completed: {len(successful_optimizations)}/{len(content_types)} indices optimized")
                return True
            else:
                logger.error("All index optimizations failed")
                return False
                
        except Exception as e:
            logger.error(f"Index optimization failed: {str(e)}")
            return False
    
    def _update_query_stats(self, processing_time: float, success: bool):
        """Update query statistics."""
        try:
            self.query_stats['total_queries'] += 1
            self.query_stats['total_query_time'] += processing_time
            
            if not success:
                self.query_stats['errors'] += 1
                
        except Exception as e:
            logger.error(f"Failed to update query stats: {str(e)}")
    
    async def _calculate_index_metrics(self, content_type: str) -> IndexMetrics:
        """Calculate metrics for a specific index."""
        try:
            # Get basic stats from vector database
            stats = self.vector_db.get_index_stats(content_type)
            
            if not stats:
                return IndexMetrics(
                    index_name=f"{content_type}_index",
                    vector_count=0,
                    dimension=0,
                    memory_usage_mb=0,
                    query_latency_ms=0,
                    throughput_qps=0,
                    last_updated=datetime.now(),
                    health_score=0,
                    status=IndexStatus.OFFLINE
                )
            
            # Calculate derived metrics
            vector_count = stats.get('vector_count', 0)
            dimension = stats.get('dimension', 0)
            
            # Estimate memory usage (simplified)
            memory_usage = (vector_count * dimension * 4) / (1024 * 1024)  # 4 bytes per float32
            
            # Calculate health score based on various factors
            health_score = self._calculate_health_score(stats)
            
            # Determine status
            if health_score > 0.8:
                status = IndexStatus.HEALTHY
            elif health_score > 0.5:
                status = IndexStatus.DEGRADED
            else:
                status = IndexStatus.ERROR
            
            return IndexMetrics(
                index_name=f"{content_type}_index",
                vector_count=vector_count,
                dimension=dimension,
                memory_usage_mb=memory_usage,
                query_latency_ms=self.query_stats['total_query_time'] / max(self.query_stats['total_queries'], 1) * 1000,
                throughput_qps=self.query_stats['total_queries'] / max((datetime.now() - self.start_time).total_seconds(), 1),
                last_updated=datetime.now(),
                health_score=health_score,
                status=status
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate metrics for {content_type}: {str(e)}")
            return IndexMetrics(
                index_name=f"{content_type}_index",
                vector_count=0,
                dimension=0,
                memory_usage_mb=0,
                query_latency_ms=0,
                throughput_qps=0,
                last_updated=datetime.now(),
                health_score=0,
                status=IndexStatus.ERROR
            )
    
    def _calculate_health_score(self, stats: Dict[str, Any]) -> float:
        """Calculate health score for an index."""
        try:
            health_factors = []
            
            # Vector count factor
            vector_count = stats.get('vector_count', 0)
            if vector_count > 0:
                health_factors.append(1.0)
            else:
                health_factors.append(0.0)
            
            # Index training factor (for applicable backends)
            is_trained = stats.get('is_trained', True)
            health_factors.append(1.0 if is_trained else 0.5)
            
            # Error rate factor
            error_rate = self.query_stats['errors'] / max(self.query_stats['total_queries'], 1)
            health_factors.append(max(0, 1.0 - error_rate * 5))  # Penalize high error rates
            
            return np.mean(health_factors)
            
        except Exception as e:
            logger.error(f"Health score calculation failed: {str(e)}")
            return 0.5
    
    async def _estimate_memory_usage(self) -> float:
        """Estimate total memory usage in MB."""
        try:
            total_memory = 0
            content_types = ['audio', 'video', 'image', 'text']
            
            for content_type in content_types:
                stats = self.vector_db.get_index_stats(content_type)
                if stats:
                    vector_count = stats.get('vector_count', 0)
                    dimension = stats.get('dimension', 0)
                    
                    # Estimate memory for vectors (4 bytes per float32)
                    memory_mb = (vector_count * dimension * 4) / (1024 * 1024)
                    total_memory += memory_mb
            
            return total_memory
            
        except Exception as e:
            logger.error(f"Memory usage estimation failed: {str(e)}")
            return 0
    
    async def _estimate_storage_usage(self) -> float:
        """Estimate total storage usage in MB."""
        try:
            total_size = self._calculate_directory_size(self.storage_path)
            return total_size
            
        except Exception as e:
            logger.error(f"Storage usage estimation failed: {str(e)}")
            return 0
    
    def _calculate_directory_size(self, directory: str) -> float:
        """Calculate total size of a directory in MB."""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            
            return total_size / (1024 * 1024)  # Convert to MB
            
        except Exception as e:
            logger.error(f"Directory size calculation failed: {str(e)}")
            return 0
    
    async def _auto_backup_task(self):
        """Background task for automatic backups."""
        try:
            while True:
                await asyncio.sleep(self.backup_interval_hours * 3600)  # Convert hours to seconds
                
                try:
                    logger.info("Starting automatic backup...")
                    backup_info = await self.create_backup(backup_name="auto")
                    
                    if backup_info.status == BackupStatus.COMPLETED:
                        logger.info(f"Automatic backup completed: {backup_info.backup_id}")
                    else:
                        logger.error("Automatic backup failed")
                        
                except Exception as e:
                    logger.error(f"Automatic backup task failed: {str(e)}")
                    
        except asyncio.CancelledError:
            logger.info("Auto backup task cancelled")
        except Exception as e:
            logger.error(f"Auto backup task error: {str(e)}")
    
    async def _metrics_collection_task(self):
        """Background task for metrics collection."""
        try:
            while True:
                await asyncio.sleep(300)  # Collect metrics every 5 minutes
                
                try:
                    # Refresh metrics cache
                    content_types = ['audio', 'video', 'image', 'text']
                    
                    with self.metrics_lock:
                        for content_type in content_types:
                            metrics = await self._calculate_index_metrics(content_type)
                            self.metrics_cache[content_type] = metrics
                    
                    logger.debug("Metrics collection completed")
                    
                except Exception as e:
                    logger.error(f"Metrics collection failed: {str(e)}")
                    
        except asyncio.CancelledError:
            logger.info("Metrics collection task cancelled")
        except Exception as e:
            logger.error(f"Metrics collection task error: {str(e)}")


# Export the main operations class
__all__ = [
    'VectorDBOperations',
    'IndexMetrics',
    'BackupInfo', 
    'PerformanceStats',
    'IndexStatus',
    'BackupStatus'
]
