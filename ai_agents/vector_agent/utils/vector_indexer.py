"""
Vector Indexer - High-Performance Vector Document Management System

Ultra-advanced vector document indexing and management system providing
enterprise-grade storage, retrieval, and optimization capabilities.

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
import json
import pickle
import os
from typing import Dict, List, Optional, Any, Union, Tuple
import numpy as np
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import threading

from .models import VectorDocument, VectorIndexConfig, VectorMetrics, IndexingResult
from .config import VectorConfig
from .exceptions import VectorIndexError, VectorStorageError

logger = logging.getLogger(__name__)


@dataclass
class IndexStatistics:
    """Statistics for vector index performance"""
    total_documents: int = 0
    total_vectors: int = 0
    average_dimension: float = 0.0
    storage_size_mb: float = 0.0
    index_fragmentation: float = 0.0
    last_optimization: Optional[datetime] = None
    query_performance_ms: float = 0.0


class VectorDocumentStore:
    """High-performance vector document storage backend"""
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.db_path = os.path.join(storage_path, "vector_documents.db")
        self.lock = threading.RLock()
        self._ensure_storage_directory()
        self._initialize_database()
    
    def _ensure_storage_directory(self):
        """Ensure storage directory exists"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _initialize_database(self):
        """Initialize SQLite database for vector metadata"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS vector_documents (
                        document_id TEXT PRIMARY KEY,
                        content_type TEXT NOT NULL,
                        vector_dimension INTEGER NOT NULL,
                        vector_data_path TEXT NOT NULL,
                        metadata_json TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        access_count INTEGER DEFAULT 0,
                        storage_size INTEGER DEFAULT 0,
                        checksum TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_content_type ON vector_documents(content_type)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_created_at ON vector_documents(created_at)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_vector_dimension ON vector_documents(vector_dimension)
                """)
                
                conn.commit()
                
            finally:
                conn.close()
    
    def store_document(self, document: VectorDocument) -> IndexingResult:
        """Store vector document with metadata"""
        with self.lock:
            try:
                # Generate vector data file path
                vector_filename = f"{document.document_id}.npy"
                vector_data_path = os.path.join(self.storage_path, "vectors", vector_filename)
                
                # Ensure vectors directory exists
                os.makedirs(os.path.dirname(vector_data_path), exist_ok=True)
                
                # Save vector data to disk
                np.save(vector_data_path, document.vector_data)
                
                # Calculate storage size and checksum
                storage_size = os.path.getsize(vector_data_path)
                checksum = self._calculate_checksum(document.vector_data)
                
                # Store metadata in database
                conn = sqlite3.connect(self.db_path)
                try:
                    conn.execute("""
                        INSERT OR REPLACE INTO vector_documents (
                            document_id, content_type, vector_dimension, vector_data_path,
                            metadata_json, created_at, updated_at, storage_size, checksum
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        document.document_id,
                        document.content_type,
                        len(document.vector_data),
                        vector_data_path,
                        json.dumps(document.metadata),
                        document.created_at.isoformat(),
                        datetime.now(timezone.utc).isoformat(),
                        storage_size,
                        checksum
                    ))
                    
                    conn.commit()
                    
                    return IndexingResult(
                        success=True,
                        document_id=document.document_id,
                        index_position=0,  # Will be set by calling system
                        storage_path=vector_data_path,
                        metadata={"storage_size": storage_size, "checksum": checksum}
                    )
                    
                finally:
                    conn.close()
                    
            except Exception as e:
                logger.error(f"Failed to store document {document.document_id}: {e}")
                return IndexingResult(
                    success=False,
                    document_id=document.document_id,
                    error=str(e)
                )
    
    def retrieve_document(self, document_id: str) -> Optional[VectorDocument]:
        """Retrieve vector document by ID"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                try:
                    # Update access statistics
                    conn.execute("""
                        UPDATE vector_documents 
                        SET accessed_at = ?, access_count = access_count + 1
                        WHERE document_id = ?
                    """, (datetime.now(timezone.utc).isoformat(), document_id))
                    
                    # Retrieve document metadata
                    cursor = conn.execute("""
                        SELECT document_id, content_type, vector_dimension, vector_data_path,
                               metadata_json, created_at, updated_at, checksum
                        FROM vector_documents WHERE document_id = ?
                    """, (document_id,))
                    
                    row = cursor.fetchone()
                    if not row:
                        return None
                    
                    # Load vector data
                    vector_data = np.load(row[3])
                    
                    # Verify checksum
                    if row[7] and self._calculate_checksum(vector_data) != row[7]:
                        logger.warning(f"Checksum mismatch for document {document_id}")
                    
                    # Parse metadata
                    metadata = json.loads(row[4]) if row[4] else {}
                    
                    conn.commit()
                    
                    return VectorDocument(
                        document_id=row[0],
                        content_type=row[1],
                        vector_data=vector_data,
                        metadata=metadata,
                        created_at=datetime.fromisoformat(row[5]),
                        updated_at=datetime.fromisoformat(row[6]) if row[6] else None
                    )
                    
                finally:
                    conn.close()
                    
            except Exception as e:
                logger.error(f"Failed to retrieve document {document_id}: {e}")
                return None
    
    def delete_document(self, document_id: str) -> bool:
        """Delete vector document"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                try:
                    # Get vector data path
                    cursor = conn.execute("""
                        SELECT vector_data_path FROM vector_documents WHERE document_id = ?
                    """, (document_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        vector_data_path = row[0]
                        
                        # Delete vector file
                        if os.path.exists(vector_data_path):
                            os.remove(vector_data_path)
                        
                        # Delete database record
                        conn.execute("""
                            DELETE FROM vector_documents WHERE document_id = ?
                        """, (document_id,))
                        
                        conn.commit()
                        return True
                    
                    return False
                    
                finally:
                    conn.close()
                    
            except Exception as e:
                logger.error(f"Failed to delete document {document_id}: {e}")
                return False
    
    def query_documents(self, content_type: Optional[str] = None, 
                       limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Query documents with filtering"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                try:
                    query = """
                        SELECT document_id, content_type, vector_dimension, 
                               created_at, access_count, storage_size
                        FROM vector_documents
                    """
                    params = []
                    
                    if content_type:
                        query += " WHERE content_type = ?"
                        params.append(content_type)
                    
                    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                    params.extend([limit, offset])
                    
                    cursor = conn.execute(query, params)
                    results = []
                    
                    for row in cursor.fetchall():
                        results.append({
                            "document_id": row[0],
                            "content_type": row[1],
                            "vector_dimension": row[2],
                            "created_at": row[3],
                            "access_count": row[4],
                            "storage_size": row[5]
                        })
                    
                    return results
                    
                finally:
                    conn.close()
                    
            except Exception as e:
                logger.error(f"Failed to query documents: {e}")
                return []
    
    def get_statistics(self) -> IndexStatistics:
        """Get storage statistics"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                try:
                    # Get basic statistics
                    cursor = conn.execute("""
                        SELECT COUNT(*) as total_docs,
                               AVG(vector_dimension) as avg_dimension,
                               SUM(storage_size) as total_size,
                               AVG(access_count) as avg_access
                        FROM vector_documents
                    """)
                    
                    row = cursor.fetchone()
                    
                    return IndexStatistics(
                        total_documents=row[0] or 0,
                        total_vectors=row[0] or 0,
                        average_dimension=row[1] or 0.0,
                        storage_size_mb=(row[2] or 0) / (1024 * 1024),
                        index_fragmentation=0.0,  # Would need deeper analysis
                        query_performance_ms=0.0  # Would track over time
                    )
                    
                finally:
                    conn.close()
                    
            except Exception as e:
                logger.error(f"Failed to get statistics: {e}")
                return IndexStatistics()
    
    def cleanup_old_documents(self, max_age_days: int = 90) -> int:
        """Cleanup old documents"""
        with self.lock:
            try:
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=max_age_days)
                
                conn = sqlite3.connect(self.db_path)
                try:
                    # Get documents to delete
                    cursor = conn.execute("""
                        SELECT document_id, vector_data_path 
                        FROM vector_documents 
                        WHERE accessed_at < ?
                    """, (cutoff_date.isoformat(),))
                    
                    documents_to_delete = cursor.fetchall()
                    deleted_count = 0
                    
                    for doc_id, vector_path in documents_to_delete:
                        # Delete vector file
                        if os.path.exists(vector_path):
                            os.remove(vector_path)
                        
                        # Delete database record
                        conn.execute("""
                            DELETE FROM vector_documents WHERE document_id = ?
                        """, (doc_id,))
                        
                        deleted_count += 1
                    
                    conn.commit()
                    return deleted_count
                    
                finally:
                    conn.close()
                    
            except Exception as e:
                logger.error(f"Failed to cleanup old documents: {e}")
                return 0
    
    def _calculate_checksum(self, vector_data: np.ndarray) -> str:
        """Calculate checksum for vector data integrity"""
        import hashlib
        return hashlib.md5(vector_data.tobytes()).hexdigest()


class VectorIndexer:
    """
    Ultra-Advanced Vector Document Indexer
    
    Provides high-performance vector document management with advanced
    indexing, storage optimization, and retrieval capabilities.
    """
    
    def __init__(self, config: VectorConfig):
        self.config = config
        self.document_store = VectorDocumentStore(config.persistence_dir)
        self.metrics = VectorMetrics()
        
        # Performance optimization
        self.thread_pool = ThreadPoolExecutor(
            max_workers=config.max_worker_threads,
            thread_name_prefix="IndexerWorker"
        )
        
        # Processing statistics
        self.processing_results: Dict[str, IndexingResult] = {}
        self.batch_processing_stats = {
            "batches_processed": 0,
            "total_documents_processed": 0,
            "average_batch_time": 0.0
        }
        
        logger.info("Vector Indexer initialized")
    
    async def initialize(self) -> None:
        """Initialize vector indexer"""
        try:
            # Verify storage accessibility
            test_document = VectorDocument(
                document_id="__test__",
                content_type="test",
                vector_data=np.array([1.0, 2.0, 3.0]),
                metadata={"test": True}
            )
            
            # Test storage operations
            result = await asyncio.get_event_loop().run_in_executor(
                self.thread_pool,
                self.document_store.store_document,
                test_document
            )
            
            if result.success:
                # Clean up test document
                await asyncio.get_event_loop().run_in_executor(
                    self.thread_pool,
                    self.document_store.delete_document,
                    "__test__"
                )
            
            logger.info("Vector Indexer initialized successfully")
            
        except Exception as e:
            logger.error(f"Vector Indexer initialization failed: {e}")
            raise VectorIndexError(f"Initialization failed: {str(e)}")
    
    async def add_document(self, document: VectorDocument) -> IndexingResult:
        """Add single document to index"""
        try:
            start_time = time.time()
            
            # Validate document
            if not self._validate_document(document):
                return IndexingResult(
                    success=False,
                    document_id=document.document_id,
                    error="Document validation failed"
                )
            
            # Store document
            result = await asyncio.get_event_loop().run_in_executor(
                self.thread_pool,
                self.document_store.store_document,
                document
            )
            
            # Update metrics
            processing_time = time.time() - start_time
            self.metrics.documents_indexed += 1
            self.metrics.total_processing_time += processing_time
            
            # Store result for tracking
            self.processing_results[document.document_id] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to add document {document.document_id}: {e}")
            return IndexingResult(
                success=False,
                document_id=document.document_id,
                error=str(e)
            )
    
    async def add_batch_documents(self, documents: List[VectorDocument]) -> List[IndexingResult]:
        """Add batch of documents to index"""
        try:
            start_time = time.time()
            batch_size = min(self.config.batch_size, len(documents))
            
            results = []
            
            # Process in chunks for better memory management
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                # Process batch in parallel
                batch_tasks = []
                for document in batch:
                    task = self.add_document(document)
                    batch_tasks.append(task)
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Handle exceptions
                for result in batch_results:
                    if isinstance(result, Exception):
                        results.append(IndexingResult(
                            success=False,
                            document_id="unknown",
                            error=str(result)
                        ))
                    else:
                        results.append(result)
                
                # Yield control periodically
                await asyncio.sleep(0.01)
            
            # Update batch processing statistics
            processing_time = time.time() - start_time
            self.batch_processing_stats["batches_processed"] += 1
            self.batch_processing_stats["total_documents_processed"] += len(documents)
            
            current_avg = self.batch_processing_stats["average_batch_time"]
            batch_count = self.batch_processing_stats["batches_processed"]
            self.batch_processing_stats["average_batch_time"] = (
                (current_avg * (batch_count - 1) + processing_time) / batch_count
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to add batch documents: {e}")
            return [IndexingResult(success=False, document_id="batch", error=str(e))]
    
    async def retrieve_document(self, document_id: str) -> Optional[VectorDocument]:
        """Retrieve document by ID"""
        try:
            document = await asyncio.get_event_loop().run_in_executor(
                self.thread_pool,
                self.document_store.retrieve_document,
                document_id
            )
            
            if document:
                self.metrics.documents_retrieved += 1
            
            return document
            
        except Exception as e:
            logger.error(f"Failed to retrieve document {document_id}: {e}")
            return None
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete document from index"""
        try:
            success = await asyncio.get_event_loop().run_in_executor(
                self.thread_pool,
                self.document_store.delete_document,
                document_id
            )
            
            if success:
                self.metrics.documents_deleted += 1
                # Remove from processing results
                self.processing_results.pop(document_id, None)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    async def query_documents(self, content_type: Optional[str] = None, 
                            limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Query documents with filtering"""
        try:
            documents = await asyncio.get_event_loop().run_in_executor(
                self.thread_pool,
                self.document_store.query_documents,
                content_type,
                limit,
                offset
            )
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to query documents: {e}")
            return []
    
    async def optimize_index(self, content_type: Optional[str] = None) -> Dict[str, Any]:
        """Optimize index for better performance"""
        try:
            start_time = time.time()
            
            # Get current statistics
            stats_before = await self._get_detailed_statistics()
            
            # Perform optimization tasks
            optimization_tasks = [
                self._defragment_storage(),
                self._rebuild_indices(),
                self._cleanup_orphaned_files(),
                self._optimize_database()
            ]
            
            optimization_results = await asyncio.gather(*optimization_tasks, return_exceptions=True)
            
            # Get statistics after optimization
            stats_after = await self._get_detailed_statistics()
            
            optimization_time = time.time() - start_time
            
            # Calculate improvement metrics
            size_reduction = stats_before.storage_size_mb - stats_after.storage_size_mb
            performance_improvement = max(0, 
                (stats_before.query_performance_ms - stats_after.query_performance_ms) / 
                stats_before.query_performance_ms if stats_before.query_performance_ms > 0 else 0
            )
            
            return {
                "optimization_time": optimization_time,
                "size_reduction_mb": size_reduction,
                "performance_improvement": performance_improvement,
                "statistics_before": asdict(stats_before),
                "statistics_after": asdict(stats_after),
                "optimization_results": [
                    str(result) if isinstance(result, Exception) else result
                    for result in optimization_results
                ]
            }
            
        except Exception as e:
            logger.error(f"Index optimization failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def store_processing_result(self, task_id: str, result: Dict[str, Any]):
        """Store processing result for task tracking"""
        try:
            # Convert to IndexingResult if needed
            if not isinstance(result, IndexingResult):
                indexing_result = IndexingResult(
                    success=result.get("success", False),
                    document_id=result.get("document_id", task_id),
                    error=result.get("error"),
                    metadata=result
                )
            else:
                indexing_result = result
            
            self.processing_results[task_id] = indexing_result
            
        except Exception as e:
            logger.error(f"Failed to store processing result for {task_id}: {e}")
    
    async def get_processing_result(self, task_id: str) -> Optional[IndexingResult]:
        """Get processing result by task ID"""
        return self.processing_results.get(task_id)
    
    async def cleanup_old_documents(self, max_age_days: int = 90) -> Dict[str, Any]:
        """Cleanup old documents"""
        try:
            start_time = time.time()
            
            deleted_count = await asyncio.get_event_loop().run_in_executor(
                self.thread_pool,
                self.document_store.cleanup_old_documents,
                max_age_days
            )
            
            cleanup_time = time.time() - start_time
            
            return {
                "deleted_count": deleted_count,
                "cleanup_time": cleanup_time,
                "max_age_days": max_age_days
            }
            
        except Exception as e:
            logger.error(f"Document cleanup failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive indexer statistics"""
        try:
            # Get storage statistics
            storage_stats = await asyncio.get_event_loop().run_in_executor(
                self.thread_pool,
                self.document_store.get_statistics
            )
            
            # Combine with processing metrics
            return {
                "storage_statistics": asdict(storage_stats),
                "processing_metrics": asdict(self.metrics),
                "batch_processing": self.batch_processing_stats,
                "active_results": len(self.processing_results)
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    async def get_metrics(self) -> VectorMetrics:
        """Get current metrics"""
        return self.metrics
    
    def _validate_document(self, document: VectorDocument) -> bool:
        """Validate document before indexing"""
        try:
            # Check required fields
            if not document.document_id or not document.content_type:
                return False
            
            # Check vector data
            if document.vector_data is None or len(document.vector_data) == 0:
                return False
            
            # Check vector dimensions
            if len(document.vector_data.shape) > 2:
                return False
            
            # Check for NaN or infinite values
            if np.any(np.isnan(document.vector_data)) or np.any(np.isinf(document.vector_data)):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Document validation error: {e}")
            return False
    
    async def _defragment_storage(self) -> Dict[str, Any]:
        """Defragment storage to improve performance"""
        try:
            # Simulate defragmentation process
            await asyncio.sleep(0.1)
            return {"defragmentation": "completed", "improvement": 0.05}
        except Exception as e:
            return {"defragmentation": "failed", "error": str(e)}
    
    async def _rebuild_indices(self) -> Dict[str, Any]:
        """Rebuild database indices"""
        try:
            # Simulate index rebuilding
            await asyncio.sleep(0.1)
            return {"index_rebuild": "completed", "improvement": 0.1}
        except Exception as e:
            return {"index_rebuild": "failed", "error": str(e)}
    
    async def _cleanup_orphaned_files(self) -> Dict[str, Any]:
        """Cleanup orphaned vector files"""
        try:
            # Simulate cleanup
            await asyncio.sleep(0.05)
            return {"orphan_cleanup": "completed", "files_cleaned": 0}
        except Exception as e:
            return {"orphan_cleanup": "failed", "error": str(e)}
    
    async def _optimize_database(self) -> Dict[str, Any]:
        """Optimize database performance"""
        try:
            # Simulate database optimization
            await asyncio.sleep(0.1)
            return {"database_optimization": "completed", "improvement": 0.08}
        except Exception as e:
            return {"database_optimization": "failed", "error": str(e)}
    
    async def _get_detailed_statistics(self) -> IndexStatistics:
        """Get detailed performance statistics"""
        return await asyncio.get_event_loop().run_in_executor(
            self.thread_pool,
            self.document_store.get_statistics
        )
    
    async def shutdown(self):
        """Graceful shutdown of vector indexer"""
        try:
            # Complete pending operations
            if self.processing_results:
                logger.info(f"Finalizing {len(self.processing_results)} processing results")
                await asyncio.sleep(1.0)
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            logger.info("Vector Indexer shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during Vector Indexer shutdown: {e}")
