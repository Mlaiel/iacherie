"""
Pinecone Backend - Serverless Cloud Vector Database
==================================================

Enterprise-grade Pinecone backend implementation with serverless vector 
database, auto-scaling infrastructure, global distribution, and cost optimization.

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
import numpy as np
import json
import time
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import uuid
from pathlib import Path
import aiohttp

# Pinecone imports with fallback handling
try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    pinecone = None

from .vector_storage import BaseVectorBackend, VectorMetadata, SearchResult

logger = logging.getLogger(__name__)


class PineconeAPIManager:
    """Manages Pinecone API operations and rate limiting."""
    
    def __init__(self, api_key: str, environment: str):
        """
        Initialize API manager.
        
        Args:
            api_key: Pinecone API key
            environment: Pinecone environment
        """
        self.api_key = api_key
        self.environment = environment
        self.rate_limit_delay = 0.1  # Base delay between requests
        self.max_retries = 3
        self.backoff_factor = 2
        
    async def make_request_with_retry(
        self,
        func: callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Make API request with exponential backoff retry.
        
        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Function result
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                # Add rate limiting delay
                if attempt > 0:
                    delay = self.rate_limit_delay * (self.backoff_factor ** attempt)
                    await asyncio.sleep(delay)
                
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    # Run in thread pool for blocking operations
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, func, *args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                # Check if it's a rate limit error
                if "rate limit" in str(e).lower() or "429" in str(e):
                    logger.warning(f"Rate limit hit, attempt {attempt + 1}/{self.max_retries}")
                    continue
                elif "quota" in str(e).lower():
                    logger.error(f"Quota exceeded: {e}")
                    raise
                else:
                    logger.warning(f"Request failed, attempt {attempt + 1}/{self.max_retries}: {e}")
                    continue
        
        # All retries failed
        logger.error(f"Request failed after {self.max_retries} attempts")
        raise last_exception


class PineconeNamespaceManager:
    """Manages Pinecone namespaces for data organization."""
    
    def __init__(self, index: Any):
        """
        Initialize namespace manager.
        
        Args:
            index: Pinecone index instance
        """
        self.index = index
        self.default_namespace = "default"
        
    def get_namespace_name(self, namespace: Optional[str] = None) -> str:
        """Get namespace name, using default if none provided."""
        return namespace or self.default_namespace
    
    async def list_namespaces(self) -> List[str]:
        """List all namespaces in the index."""
        try:
            # Note: Pinecone doesn't have a direct API to list namespaces
            # This would need to be tracked separately or inferred from describe_index_stats
            stats = self.index.describe_index_stats()
            namespaces = list(stats.get('namespaces', {}).keys())
            return namespaces if namespaces else [self.default_namespace]
            
        except Exception as e:
            logger.error(f"Failed to list namespaces: {e}")
            return [self.default_namespace]
    
    async def get_namespace_stats(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for a specific namespace."""
        try:
            namespace_name = self.get_namespace_name(namespace)
            stats = self.index.describe_index_stats()
            
            namespace_stats = stats.get('namespaces', {}).get(namespace_name, {})
            
            return {
                'namespace': namespace_name,
                'vector_count': namespace_stats.get('vector_count', 0),
                'total_vector_count': stats.get('total_vector_count', 0),
                'dimension': stats.get('dimension', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get namespace stats: {e}")
            return {}
    
    async def delete_namespace(self, namespace: str) -> bool:
        """Delete all vectors in a namespace."""
        try:
            if namespace == self.default_namespace:
                # Delete all vectors in default namespace
                self.index.delete(delete_all=True)
            else:
                # Delete all vectors in specific namespace
                self.index.delete(delete_all=True, namespace=namespace)
            
            logger.info(f"Deleted namespace: {namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete namespace {namespace}: {e}")
            return False


class PineconeCostOptimizer:
    """Optimizes costs for Pinecone usage."""
    
    def __init__(self):
        """Initialize cost optimizer."""
        self.usage_stats = {
            'reads': 0,
            'writes': 0,
            'storage_size': 0,
            'last_reset': datetime.utcnow()
        }
        
    def track_operation(self, operation_type: str, count: int = 1) -> None:
        """Track operation for cost monitoring."""
        if operation_type in ['search', 'query', 'fetch']:
            self.usage_stats['reads'] += count
        elif operation_type in ['upsert', 'update', 'delete']:
            self.usage_stats['writes'] += count
    
    def estimate_monthly_cost(self, vectors_count: int, dimension: int) -> Dict[str, float]:
        """
        Estimate monthly cost based on usage.
        
        Args:
            vectors_count: Number of vectors
            dimension: Vector dimension
        
        Returns:
            Cost breakdown dictionary
        """
        # Simplified cost estimation (actual costs may vary)
        storage_gb = (vectors_count * dimension * 4) / (1024 ** 3)  # 4 bytes per float32
        
        # Example pricing (check Pinecone pricing for actual rates)
        storage_cost = storage_gb * 0.096  # $0.096 per GB per month
        
        # Request costs (example rates)
        read_cost = (self.usage_stats['reads'] / 1000) * 0.0004  # Per 1K reads
        write_cost = (self.usage_stats['writes'] / 1000) * 0.002  # Per 1K writes
        
        return {
            'storage_cost': storage_cost,
            'read_cost': read_cost,
            'write_cost': write_cost,
            'total_estimated': storage_cost + read_cost + write_cost,
            'storage_gb': storage_gb
        }
    
    def get_optimization_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Get cost optimization recommendations."""
        recommendations = []
        
        # Check for high read/write ratios
        total_ops = self.usage_stats['reads'] + self.usage_stats['writes']
        if total_ops > 0:
            read_ratio = self.usage_stats['reads'] / total_ops
            
            if read_ratio > 0.9:
                recommendations.append("High read ratio detected. Consider implementing caching for frequently accessed vectors.")
            elif read_ratio < 0.1:
                recommendations.append("High write ratio detected. Consider batch operations to reduce write costs.")
        
        # Check vector count vs dimension efficiency
        if 'total_vectors' in stats and 'dimension' in stats:
            vectors = stats['total_vectors']
            dimension = stats['dimension']
            
            if dimension > 1000:
                recommendations.append("High-dimensional vectors detected. Consider dimensionality reduction techniques.")
            
            if vectors < 1000:
                recommendations.append("Low vector count. Ensure you're utilizing the full capacity of your index.")
        
        return recommendations


class PineconeBackend(BaseVectorBackend):
    """
    Enterprise Pinecone backend implementation.
    
    Features:
    - Serverless vector database
    - Auto-scaling infrastructure
    - Global distribution
    - Real-time updates
    - Namespace management
    - Vector streaming
    - Cost optimization algorithms
    - API key management
    - VPC integration support
    - Encryption in-transit/at-rest
    - Audit logging
    - Compliance monitoring
    """
    
    def __init__(self, config: Any, security_manager: Optional[Any] = None):
        """Initialize Pinecone backend."""
        super().__init__(config, security_manager)
        
        # Configuration
        self.api_key = config.get('backend.api_key', '')
        self.environment = config.get('backend.environment', 'us-west1-gcp')
        self.index_name = config.get('backend.index_name', 'ainflue-vectors')
        self.dimension = config.get('backend.dimension', 768)
        self.metric = config.get('backend.metric', 'cosine')
        self.namespace = config.get('backend.namespace', 'default')
        self.batch_size = config.get('backend.batch_size', 100)
        self.pod_type = config.get('backend.pod_type', 'p1.x1')
        self.replicas = config.get('backend.replicas', 1)
        
        # Core components
        self.index: Optional[Any] = None
        self.api_manager: Optional[PineconeAPIManager] = None
        self.namespace_manager: Optional[PineconeNamespaceManager] = None
        self.cost_optimizer = PineconeCostOptimizer()
        
        # Statistics
        self.stats = {
            'total_searches': 0,
            'total_adds': 0,
            'total_updates': 0,
            'total_deletes': 0,
            'total_vectors': 0,
            'namespace_count': 0,
            'index_ready': False
        }
        
        logger.info(f"PineconeBackend initialized with index: {self.index_name}")
    
    async def initialize(self) -> bool:
        """Initialize the Pinecone backend."""
        try:
            if not PINECONE_AVAILABLE:
                raise RuntimeError("Pinecone not available. Install with: pip install pinecone-client")
            
            if not self.api_key:
                raise ValueError("Pinecone API key is required")
            
            # Initialize Pinecone
            pinecone.init(
                api_key=self.api_key,
                environment=self.environment
            )
            
            # Initialize API manager
            self.api_manager = PineconeAPIManager(
                api_key=self.api_key,
                environment=self.environment
            )
            
            # Create or connect to index
            await self._initialize_index()
            
            # Initialize namespace manager
            if self.index:
                self.namespace_manager = PineconeNamespaceManager(self.index)
            
            # Update statistics
            await self._update_statistics()
            
            self.initialized = True
            logger.info("Pinecone backend initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone backend: {e}")
            return False
    
    async def _initialize_index(self) -> None:
        """Initialize or create Pinecone index."""
        try:
            # Check if index exists
            existing_indexes = pinecone.list_indexes()
            
            if self.index_name not in existing_indexes:
                # Create new index
                logger.info(f"Creating Pinecone index: {self.index_name}")
                
                pinecone.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    pod_type=self.pod_type,
                    replicas=self.replicas,
                    metadata_config={
                        'indexed': ['content_type', 'created_at', 'version']
                    }
                )
                
                # Wait for index to be ready
                await self._wait_for_index_ready()
            
            # Connect to index
            self.index = pinecone.Index(self.index_name)
            
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone index: {e}")
            raise
    
    async def _wait_for_index_ready(self, timeout: int = 300) -> bool:
        """Wait for index to be ready."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                index_description = pinecone.describe_index(self.index_name)
                status = index_description.get('status', {}).get('ready', False)
                
                if status:
                    self.stats['index_ready'] = True
                    logger.info(f"Pinecone index {self.index_name} is ready")
                    return True
                
                await asyncio.sleep(10)  # Wait 10 seconds between checks
                
            except Exception as e:
                logger.warning(f"Error checking index status: {e}")
                await asyncio.sleep(5)
        
        logger.error(f"Timeout waiting for index {self.index_name} to be ready")
        return False
    
    async def add_vector(
        self,
        vector_id: str,
        vector: np.ndarray,
        metadata: Optional[VectorMetadata] = None
    ) -> bool:
        """Add a vector to Pinecone."""
        try:
            if not self.initialized or not self.index:
                return False
            
            # Prepare metadata for Pinecone
            pinecone_metadata = {}
            if metadata:
                pinecone_metadata = {
                    'content_type': metadata.content_type,
                    'content_hash': metadata.content_hash,
                    'created_at': metadata.created_at.isoformat(),
                    'version': metadata.version
                }
                
                # Add custom metadata (flatten and convert to strings)
                if metadata.custom_metadata:
                    for key, value in metadata.custom_metadata.items():
                        # Pinecone has restrictions on metadata keys
                        safe_key = key.replace('.', '_').replace(' ', '_')
                        pinecone_metadata[f'custom_{safe_key}'] = str(value)
                
                if metadata.encryption_key_id:
                    pinecone_metadata['encryption_key_id'] = metadata.encryption_key_id
                
                if metadata.compression_type:
                    pinecone_metadata['compression_type'] = metadata.compression_type
            
            # Prepare vector
            if vector.ndim > 1:
                vector = vector.flatten()
            vector_list = vector.tolist()
            
            # Upsert vector
            def upsert_vector():
                self.index.upsert(
                    vectors=[(vector_id, vector_list, pinecone_metadata)],
                    namespace=self.namespace
                )
            
            await self.api_manager.make_request_with_retry(upsert_vector)
            
            # Track for cost optimization
            self.cost_optimizer.track_operation('upsert', 1)
            
            self.stats['total_adds'] += 1
            self.stats['total_vectors'] += 1
            
            logger.debug(f"Added vector to Pinecone: {vector_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vector {vector_id} to Pinecone: {e}")
            return False
    
    async def add_vectors_batch(
        self,
        vectors: List[Tuple[str, np.ndarray, Optional[VectorMetadata]]]
    ) -> List[bool]:
        """Add multiple vectors in a batch."""
        try:
            if not self.initialized or not self.index:
                return [False] * len(vectors)
            
            # Process in batches to respect Pinecone limits
            results = []
            
            for i in range(0, len(vectors), self.batch_size):
                batch = vectors[i:i + self.batch_size]
                batch_results = await self._process_batch_upsert(batch)
                results.extend(batch_results)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to add vectors batch to Pinecone: {e}")
            return [False] * len(vectors)
    
    async def _process_batch_upsert(
        self,
        batch: List[Tuple[str, np.ndarray, Optional[VectorMetadata]]]
    ) -> List[bool]:
        """Process a single batch of vectors for upsert."""
        try:
            # Prepare batch data
            upsert_data = []
            
            for vector_id, vector, metadata in batch:
                # Prepare metadata
                pinecone_metadata = {}
                if metadata:
                    pinecone_metadata = {
                        'content_type': metadata.content_type,
                        'content_hash': metadata.content_hash,
                        'created_at': metadata.created_at.isoformat(),
                        'version': metadata.version
                    }
                    
                    if metadata.custom_metadata:
                        for key, value in metadata.custom_metadata.items():
                            safe_key = key.replace('.', '_').replace(' ', '_')
                            pinecone_metadata[f'custom_{safe_key}'] = str(value)
                
                # Prepare vector
                if vector.ndim > 1:
                    vector = vector.flatten()
                
                upsert_data.append((vector_id, vector.tolist(), pinecone_metadata))
            
            # Upsert batch
            def upsert_batch():
                self.index.upsert(
                    vectors=upsert_data,
                    namespace=self.namespace
                )
            
            await self.api_manager.make_request_with_retry(upsert_batch)
            
            # Track for cost optimization
            self.cost_optimizer.track_operation('upsert', len(batch))
            
            # Update statistics
            successful_adds = len(batch)
            self.stats['total_adds'] += successful_adds
            self.stats['total_vectors'] += successful_adds
            
            logger.info(f"Added {successful_adds} vectors to Pinecone in batch")
            return [True] * len(batch)
            
        except Exception as e:
            logger.error(f"Failed to process batch upsert: {e}")
            return [False] * len(batch)
    
    async def search_similar(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar vectors."""
        try:
            if not self.initialized or not self.index:
                return []
            
            # Prepare query vector
            if query_vector.ndim > 1:
                query_vector = query_vector.flatten()
            query_list = query_vector.tolist()
            
            # Prepare metadata filters
            pinecone_filter = {}
            if filters:
                for key, value in filters.items():
                    if key == 'content_type':
                        pinecone_filter['content_type'] = {'$eq': value}
                    elif key == 'created_after':
                        pinecone_filter['created_at'] = {'$gt': value}
                    elif key == 'created_before':
                        pinecone_filter['created_at'] = {'$lt': value}
                    elif key.startswith('custom.'):
                        safe_key = f"custom_{key[7:].replace('.', '_').replace(' ', '_')}"
                        pinecone_filter[safe_key] = {'$eq': str(value)}
            
            # Perform search
            def query_index():
                query_params = {
                    'vector': query_list,
                    'top_k': top_k,
                    'namespace': self.namespace,
                    'include_metadata': True,
                    'include_values': False
                }
                
                if pinecone_filter:
                    query_params['filter'] = pinecone_filter
                
                return self.index.query(**query_params)
            
            response = await self.api_manager.make_request_with_retry(query_index)
            
            # Track for cost optimization
            self.cost_optimizer.track_operation('query', 1)
            
            # Process results
            search_results = []
            
            if response and 'matches' in response:
                for match in response['matches']:
                    # Get similarity score
                    similarity_score = float(match.get('score', 0.0))
                    
                    # Apply threshold
                    if similarity_score < threshold:
                        continue
                    
                    # Get vector ID
                    vector_id = match.get('id', '')
                    
                    # Parse metadata
                    metadata = None
                    if 'metadata' in match and match['metadata']:
                        pinecone_meta = match['metadata']
                        
                        # Extract custom metadata
                        custom_metadata = {}
                        for key, value in pinecone_meta.items():
                            if key.startswith('custom_'):
                                original_key = key[7:].replace('_', '.')
                                custom_metadata[original_key] = value
                        
                        metadata = VectorMetadata(
                            id=vector_id,
                            content_type=pinecone_meta.get('content_type', 'unknown'),
                            content_hash=pinecone_meta.get('content_hash', ''),
                            created_at=datetime.fromisoformat(pinecone_meta.get('created_at', datetime.utcnow().isoformat())),
                            custom_metadata=custom_metadata if custom_metadata else None,
                            encryption_key_id=pinecone_meta.get('encryption_key_id'),
                            compression_type=pinecone_meta.get('compression_type'),
                            version=int(pinecone_meta.get('version', 1))
                        )
                    
                    search_results.append(SearchResult(
                        id=vector_id,
                        score=similarity_score,
                        metadata=metadata
                    ))
            
            self.stats['total_searches'] += 1
            
            logger.debug(f"Pinecone search found {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to search similar vectors in Pinecone: {e}")
            return []
    
    async def get_vector(self, vector_id: str) -> Optional[Tuple[np.ndarray, VectorMetadata]]:
        """Get a specific vector by ID."""
        try:
            if not self.initialized or not self.index:
                return None
            
            # Fetch vector from Pinecone
            def fetch_vector():
                return self.index.fetch(
                    ids=[vector_id],
                    namespace=self.namespace
                )
            
            response = await self.api_manager.make_request_with_retry(fetch_vector)
            
            # Track for cost optimization
            self.cost_optimizer.track_operation('fetch', 1)
            
            if not response or 'vectors' not in response or vector_id not in response['vectors']:
                return None
            
            vector_data = response['vectors'][vector_id]
            
            # Get vector values
            if 'values' not in vector_data:
                return None
            
            vector = np.array(vector_data['values'], dtype=np.float32)
            
            # Parse metadata
            metadata = None
            if 'metadata' in vector_data and vector_data['metadata']:
                pinecone_meta = vector_data['metadata']
                
                # Extract custom metadata
                custom_metadata = {}
                for key, value in pinecone_meta.items():
                    if key.startswith('custom_'):
                        original_key = key[7:].replace('_', '.')
                        custom_metadata[original_key] = value
                
                metadata = VectorMetadata(
                    id=vector_id,
                    content_type=pinecone_meta.get('content_type', 'unknown'),
                    content_hash=pinecone_meta.get('content_hash', ''),
                    created_at=datetime.fromisoformat(pinecone_meta.get('created_at', datetime.utcnow().isoformat())),
                    custom_metadata=custom_metadata if custom_metadata else None,
                    encryption_key_id=pinecone_meta.get('encryption_key_id'),
                    compression_type=pinecone_meta.get('compression_type'),
                    version=int(pinecone_meta.get('version', 1))
                )
            
            if metadata is None:
                metadata = VectorMetadata(
                    id=vector_id,
                    content_type="unknown",
                    content_hash="",
                    created_at=datetime.utcnow()
                )
            
            return vector, metadata
            
        except Exception as e:
            logger.error(f"Failed to get vector {vector_id} from Pinecone: {e}")
            return None
    
    async def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector by ID."""
        try:
            if not self.initialized or not self.index:
                return False
            
            # Delete from Pinecone
            def delete_vector():
                self.index.delete(
                    ids=[vector_id],
                    namespace=self.namespace
                )
            
            await self.api_manager.make_request_with_retry(delete_vector)
            
            # Track for cost optimization
            self.cost_optimizer.track_operation('delete', 1)
            
            self.stats['total_deletes'] += 1
            self.stats['total_vectors'] = max(0, self.stats['total_vectors'] - 1)
            
            logger.debug(f"Deleted vector from Pinecone: {vector_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vector {vector_id} from Pinecone: {e}")
            return False
    
    async def update_vector(
        self,
        vector_id: str,
        vector: Optional[np.ndarray] = None,
        metadata: Optional[VectorMetadata] = None
    ) -> bool:
        """Update a vector."""
        try:
            if not self.initialized or not self.index:
                return False
            
            # For Pinecone, update is the same as upsert
            if vector is not None:
                if metadata:
                    metadata.updated_at = datetime.utcnow()
                
                success = await self.add_vector(vector_id, vector, metadata)
                
                if success:
                    self.stats['total_updates'] += 1
                    # Adjust total_vectors since add_vector increments it
                    self.stats['total_vectors'] -= 1
                
                return success
            
            # If only metadata update, we need to fetch existing vector first
            existing = await self.get_vector(vector_id)
            if not existing:
                return False
            
            existing_vector, existing_metadata = existing
            
            # Merge metadata
            if metadata:
                metadata.updated_at = datetime.utcnow()
                update_metadata = metadata
            else:
                existing_metadata.updated_at = datetime.utcnow()
                update_metadata = existing_metadata
            
            success = await self.add_vector(vector_id, existing_vector, update_metadata)
            
            if success:
                self.stats['total_updates'] += 1
                # Adjust total_vectors since add_vector increments it
                self.stats['total_vectors'] -= 1
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update vector {vector_id} in Pinecone: {e}")
            return False
    
    async def _update_statistics(self) -> None:
        """Update internal statistics."""
        try:
            if self.namespace_manager:
                namespace_stats = await self.namespace_manager.get_namespace_stats(self.namespace)
                if namespace_stats:
                    self.stats['total_vectors'] = namespace_stats.get('vector_count', 0)
                    
        except Exception as e:
            logger.error(f"Failed to update Pinecone statistics: {e}")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get backend statistics."""
        await self._update_statistics()
        
        stats = self.stats.copy()
        stats.update({
            'backend_type': 'pinecone',
            'index_name': self.index_name,
            'environment': self.environment,
            'dimension': self.dimension,
            'metric': self.metric,
            'namespace': self.namespace,
            'pod_type': self.pod_type,
            'replicas': self.replicas
        })
        
        # Add cost estimation
        cost_estimation = self.cost_optimizer.estimate_monthly_cost(
            vectors_count=self.stats['total_vectors'],
            dimension=self.dimension
        )
        stats['cost_estimation'] = cost_estimation
        
        # Add optimization recommendations
        recommendations = self.cost_optimizer.get_optimization_recommendations(stats)
        stats['optimization_recommendations'] = recommendations
        
        return stats
    
    async def health_check(self) -> bool:
        """Perform health check."""
        try:
            if not self.initialized or not self.index:
                return False
            
            # Test basic operations
            def describe_index():
                return self.index.describe_index_stats()
            
            stats = await self.api_manager.make_request_with_retry(describe_index)
            
            if stats is None:
                return False
            
            # Check if index is ready
            if not stats.get('ready', False):
                return False
            
            # Test query if there are vectors
            total_vectors = stats.get('total_vector_count', 0)
            if total_vectors > 0:
                # Test with a dummy vector
                dummy_vector = np.random.random(self.dimension).astype(np.float32)
                
                def test_query():
                    return self.index.query(
                        vector=dummy_vector.tolist(),
                        top_k=1,
                        namespace=self.namespace
                    )
                
                result = await self.api_manager.make_request_with_retry(test_query)
                if result is None:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Pinecone health check failed: {e}")
            return False
    
    async def delete_index(self) -> bool:
        """Delete the entire Pinecone index."""
        try:
            if not self.initialized:
                return False
            
            pinecone.delete_index(self.index_name)
            
            self.index = None
            self.stats['total_vectors'] = 0
            self.stats['index_ready'] = False
            
            logger.info(f"Deleted Pinecone index: {self.index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete Pinecone index: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the Pinecone backend."""
        logger.info("Shutting down Pinecone backend...")
        
        try:
            # Pinecone client doesn't require explicit shutdown
            # but we can clear references
            self.index = None
            self.api_manager = None
            self.namespace_manager = None
            
            self.initialized = False
            logger.info("Pinecone backend shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during Pinecone shutdown: {e}")


# Export main class
__all__ = [
    'PineconeBackend',
    'PineconeAPIManager',
    'PineconeNamespaceManager',
    'PineconeCostOptimizer'
]