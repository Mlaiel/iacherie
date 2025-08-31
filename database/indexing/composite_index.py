"""
Composite Index Manager for IA-Influencer-Agent Platform

Advanced composite indexing system combining multiple index types
for optimal performance across diverse query patterns.

 Enterprise Team Project Specialties:
 Lead Dev + Architecte Développeur IA
 Développeur Backend Senior (Python/FastAPI/Django)  
 Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
 DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
 Spécialiste Sécurité Backend
 Architecte Microservices
 Développeur Audio
 DevOps Engineer
 IA Prompt Engineer

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

 STRICT COPYRIGHT WARNING 
This software is proprietary and confidential. 
Unauthorized use, modification, or distribution by any individual or entity 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json

from .content_index import ContentIndexManager
from .vector_index import VectorIndexManager
from .faiss_index import FAISSIndexManager
from .elasticsearch_index import ElasticsearchIndexManager
from .fingerprint_index import FingerprintIndexManager
from .similarity_index import SimilarityIndexManager
from ..monitoring.performance_tracker import PerformanceTracker

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Types of queries supported by composite indexes"""
    EXACT_MATCH = "exact_match"
    FUZZY_SEARCH = "fuzzy_search"
    SEMANTIC_SEARCH = "semantic_search"
    SIMILARITY_SEARCH = "similarity_search"
    RANGE_QUERY = "range_query"
    AGGREGATION = "aggregation"
    HYBRID_SEARCH = "hybrid_search"

class IndexPriority(Enum):
    """Priority levels for index selection"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    FALLBACK = "fallback"

class CompositeIndexManager:
    """
    Ultra-advanced composite index manager for IA-Influencer platform
    
    Orchestrates multiple index types for optimal query performance:
    - Content-specific indexes (B-tree, Hash, GIN, GiST)
    - Vector similarity indexes (FAISS, pgvector)
    - Full-text search indexes (Elasticsearch)
    - Fingerprint matching indexes
    - Cross-modal similarity indexes
    
    Features:
    - Intelligent query routing
    - Multi-index result merging
    - Performance-based index selection
    - Automatic fallback mechanisms
    - Load balancing across indexes
    """
    
    def __init__(self):
        """Initialize composite index manager"""
        self.content_manager = ContentIndexManager()
        self.vector_manager = VectorIndexManager()
        self.faiss_manager = FAISSIndexManager()
        self.elasticsearch_manager = ElasticsearchIndexManager()
        self.fingerprint_manager = FingerprintIndexManager()
        self.similarity_manager = SimilarityIndexManager()
        self.performance_tracker = PerformanceTracker()
        
        # Index routing configuration
        self.routing_config = {
            QueryType.EXACT_MATCH: [
                {'manager': 'content', 'priority': IndexPriority.PRIMARY, 'weight': 1.0},
                {'manager': 'fingerprint', 'priority': IndexPriority.SECONDARY, 'weight': 0.8}
            ],
            QueryType.FUZZY_SEARCH: [
                {'manager': 'elasticsearch', 'priority': IndexPriority.PRIMARY, 'weight': 1.0},
                {'manager': 'content', 'priority': IndexPriority.SECONDARY, 'weight': 0.6}
            ],
            QueryType.SEMANTIC_SEARCH: [
                {'manager': 'vector', 'priority': IndexPriority.PRIMARY, 'weight': 1.0},
                {'manager': 'faiss', 'priority': IndexPriority.PRIMARY, 'weight': 0.9},
                {'manager': 'elasticsearch', 'priority': IndexPriority.SECONDARY, 'weight': 0.7}
            ],
            QueryType.SIMILARITY_SEARCH: [
                {'manager': 'similarity', 'priority': IndexPriority.PRIMARY, 'weight': 1.0},
                {'manager': 'faiss', 'priority': IndexPriority.PRIMARY, 'weight': 0.95},
                {'manager': 'fingerprint', 'priority': IndexPriority.SECONDARY, 'weight': 0.8}
            ],
            QueryType.RANGE_QUERY: [
                {'manager': 'content', 'priority': IndexPriority.PRIMARY, 'weight': 1.0},
                {'manager': 'elasticsearch', 'priority': IndexPriority.SECONDARY, 'weight': 0.8}
            ],
            QueryType.AGGREGATION: [
                {'manager': 'elasticsearch', 'priority': IndexPriority.PRIMARY, 'weight': 1.0},
                {'manager': 'content', 'priority': IndexPriority.SECONDARY, 'weight': 0.7}
            ],
            QueryType.HYBRID_SEARCH: [
                {'manager': 'elasticsearch', 'priority': IndexPriority.PRIMARY, 'weight': 0.9},
                {'manager': 'vector', 'priority': IndexPriority.PRIMARY, 'weight': 0.9},
                {'manager': 'similarity', 'priority': IndexPriority.SECONDARY, 'weight': 0.8}
            ]
        }
        
        # Manager mapping
        self.managers = {
            'content': self.content_manager,
            'vector': self.vector_manager,
            'faiss': self.faiss_manager,
            'elasticsearch': self.elasticsearch_manager,
            'fingerprint': self.fingerprint_manager,
            'similarity': self.similarity_manager
        }
        
        # Performance statistics
        self.query_stats = {}
        self.index_performance = {}
        
        # Configuration
        self.max_concurrent_queries = 10
        self.result_merge_threshold = 1000
        self.cache_ttl = 300  # 5 minutes
        
        logger.info("CompositeIndexManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize composite index manager and all sub-managers"""



        try:
            # Initialize performance tracking
            await self.performance_tracker.initialize()
            
            # Initialize all sub-managers
            init_tasks = []
            for name, manager in self.managers.items():
                try:
                    task = asyncio.create_task(manager.initialize())
                    init_tasks.append((name, task))
                except Exception as e:
                    logger.warning(f"Failed to create init task for {name}: {str(e)}")
            
            # Wait for all initializations with timeout
            results = await asyncio.gather(
                *[task for _, task in init_tasks], 
                return_exceptions=True
            )
            
            # Check results
            successful_managers = []
            for (name, _), result in zip(init_tasks, results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to initialize {name} manager: {str(result)}")
                elif result:
                    successful_managers.append(name)
                    logger.info(f"{name} manager initialized successfully")
                else:
                    logger.warning(f"{name} manager initialization returned False")
            
            if len(successful_managers) < 2:
                raise Exception("Insufficient managers initialized for composite operations")
            
            # Load performance baselines
            await self._load_performance_baselines()
            
            # Setup optimization scheduling
            await self._setup_optimization_scheduling()
            
            logger.info(f"CompositeIndexManager initialization completed with {len(successful_managers)} managers")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize CompositeIndexManager: {str(e)}")
            return False
    
    async def create_index(self, index_name: str, config: Dict[str, Any]) -> bool:
        """Create composite index across multiple backends"""



        try:
            index_types = config.get('index_types', ['content'])
            if not isinstance(index_types, list):
                index_types = [index_types]
            
            success_count = 0
            total_count = len(index_types)
            
            # Create indexes in parallel across different managers
            create_tasks = []
            for index_type in index_types:
                if index_type in self.managers:
                    manager = self.managers[index_type]
                    task = asyncio.create_task(
                        manager.create_index(f"{index_name}_{index_type}", config)
                    )
                    create_tasks.append((index_type, task))
            
            # Wait for all creations
            results = await asyncio.gather(
                *[task for _, task in create_tasks], 
                return_exceptions=True
            )
            
            # Process results
            for (index_type, _), result in zip(create_tasks, results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to create {index_type} index: {str(result)}")
                elif result:
                    success_count += 1
                    logger.info(f"Created {index_type} index successfully")
                else:
                    logger.warning(f"Failed to create {index_type} index")
            
            # Consider successful if at least 50% of indexes were created
            success = success_count >= (total_count / 2)
            
            # Log performance
            await self.performance_tracker.log_index_operation(
                f"composite_{index_name}", 'create', 0,
                {'success_rate': success_count / total_count, 'total_indexes': total_count}
            )
            
            logger.info(f"Composite index {index_name} creation: {success_count}/{total_count} successful")
            return success
            
        except Exception as e:
            logger.error(f"Failed to create composite index {index_name}: {str(e)}")
            return False
    
    async def query(self, query_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute composite query across multiple indexes"""



        try:
            query_type = QueryType(query_config.get('type', 'exact_match'))
            query_text = query_config.get('query', '')
            max_results = query_config.get('max_results', 50)
            merge_results = query_config.get('merge_results', True)
            
            start_time = datetime.now()
            
            # Get routing configuration for query type
            routing = self.routing_config.get(query_type, [])
            if not routing:
                raise ValueError(f"No routing configuration for query type: {query_type}")
            
            # Execute queries in parallel across relevant indexes
            query_tasks = []
            for route in routing:
                manager_name = route['manager']
                if manager_name in self.managers:
                    manager = self.managers[manager_name]
                    weight = route['weight']
                    
                    # Adapt query for specific manager
                    adapted_query = await self._adapt_query_for_manager(
                        query_config, manager_name, weight
                    )
                    
                    task = asyncio.create_task(
                        self._execute_manager_query(manager, adapted_query)
                    )
                    query_tasks.append((manager_name, weight, task))
            
            # Wait for all queries with timeout
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*[task for _, _, task in query_tasks], return_exceptions=True),
                    timeout=30.0  # 30 seconds timeout
                )
            except asyncio.TimeoutError:
                logger.warning("Query timeout, returning partial results")
                results = [None] * len(query_tasks)
            
            # Process and merge results
            manager_results = {}
            for (manager_name, weight, _), result in zip(query_tasks, results):
                if isinstance(result, Exception):
                    logger.warning(f"Query failed on {manager_name}: {str(result)}")
                    manager_results[manager_name] = {'error': str(result), 'weight': weight}
                elif result:
                    manager_results[manager_name] = {
                        'results': result,
                        'weight': weight,
                        'count': len(result.get('hits', []))
                    }
                else:
                    manager_results[manager_name] = {'results': [], 'weight': weight, 'count': 0}
            
            # Merge results if requested
            if merge_results and len(manager_results) > 1:
                merged_results = await self._merge_query_results(
                    manager_results, max_results, query_type
                )
            else:
                # Return results from highest-weight successful manager
                merged_results = await self._select_best_results(manager_results, max_results)
            
            query_time = (datetime.now() - start_time).total_seconds()
            
            # Update statistics
            await self._update_query_statistics(query_type, query_time, manager_results)
            
            # Log performance
            await self.performance_tracker.log_index_operation(
                f"composite_query_{query_type.value}", 'query', query_time,
                {
                    'managers_used': len(manager_results),
                    'total_results': len(merged_results.get('hits', [])),
                    'query_length': len(query_text)
                }
            )
            
            return {
                'hits': merged_results.get('hits', []),
                'total_hits': merged_results.get('total_hits', 0),
                'query_time': query_time,
                'managers_used': list(manager_results.keys()),
                'query_type': query_type.value
            }
            
        except Exception as e:
            logger.error(f"Composite query failed: {str(e)}")
            return {
                'hits': [],
                'total_hits': 0,
                'error': str(e),
                'query_type': query_config.get('type', 'unknown')
            }
    
    async def _adapt_query_for_manager(self, query_config: Dict[str, Any], 
                                     manager_name: str, weight: float) -> Dict[str, Any]:
        """Adapt query configuration for specific index manager"""
        adapted_query = query_config.copy()
        
        if manager_name == 'elasticsearch':
            # Adapt for Elasticsearch
            if 'query' in adapted_query:
                adapted_query['body'] = {
                    'query': {
                        'multi_match': {
                            'query': adapted_query['query'],
                            'fields': ['title^2', 'description', 'content'],
                            'type': 'best_fields'
                        }
                    },
                    'size': adapted_query.get('max_results', 50)
                }
            
        elif manager_name in ['vector', 'faiss']:
            # Adapt for vector search
            if 'vector' in adapted_query:
                adapted_query['query_vector'] = adapted_query['vector']
                adapted_query['k'] = adapted_query.get('max_results', 50)
                adapted_query['similarity_threshold'] = 0.7 * weight  # Adjust threshold by weight
            
        elif manager_name == 'fingerprint':
            # Adapt for fingerprint search
            if 'fingerprint_hash' in adapted_query:
                adapted_query['similarity_threshold'] = 0.8 * weight
            
        elif manager_name == 'similarity':
            # Adapt for similarity search
            adapted_query['min_similarity'] = 0.6 * weight
            
        return adapted_query
    
    async def _execute_manager_query(self, manager, query_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query on specific index manager"""



        try:
            if hasattr(manager, 'search'):
                # For managers with search method (Elasticsearch)
                return await manager.search(
                    query_config.get('index_name', '*'),
                    query_config.get('body', {}),
                    query_config.get('max_results', 50)
                )
            elif hasattr(manager, 'search_similar'):
                # For vector/similarity managers
                results = await manager.search_similar(
                    query_config.get('index_name', 'default'),
                    query_config.get('query_vector'),
                    query_config.get('k', 50),
                    query_config.get('similarity_threshold', 0.7)
                )
                return {'hits': results, 'total_hits': len(results)}
            elif hasattr(manager, 'find_similar_fingerprints'):
                # For fingerprint manager
                results = await manager.find_similar_fingerprints(
                    query_config.get('fingerprint_hash', ''),
                    query_config.get('fingerprint_type', 'composite'),
                    query_config.get('similarity_threshold', 0.8),
                    query_config.get('max_results', 50)
                )
                return {'hits': results, 'total_hits': len(results)}
            else:
                # Generic query method
                return {'hits': [], 'total_hits': 0}
                
        except Exception as e:
            logger.warning(f"Manager query execution failed: {str(e)}")
            return {'hits': [], 'total_hits': 0, 'error': str(e)}
    
    async def _merge_query_results(self, manager_results: Dict[str, Any], 
                                 max_results: int, query_type: QueryType) -> Dict[str, Any]:
        """Merge results from multiple index managers"""



        try:
            all_hits = []
            total_weight = 0
            
            # Collect all hits with weighted scores
            for manager_name, result_data in manager_results.items():
                if 'results' not in result_data or 'error' in result_data:
                    continue
                
                weight = result_data['weight']
                total_weight += weight
                
                hits = result_data['results'].get('hits', [])
                for hit in hits:
                    # Normalize score and apply weight
                    original_score = hit.get('similarity_score', hit.get('_score', 0.5))
                    weighted_score = original_score * weight
                    
                    # Add metadata about source manager
                    enhanced_hit = hit.copy()
                    enhanced_hit['_composite_score'] = weighted_score
                    enhanced_hit['_source_manager'] = manager_name
                    enhanced_hit['_original_score'] = original_score
                    enhanced_hit['_weight'] = weight
                    
                    all_hits.append(enhanced_hit)
            
            # Remove duplicates based on content_id
            unique_hits = {}
            for hit in all_hits:
                content_id = hit.get('content_id', hit.get('_id', ''))
                if content_id:
                    if content_id not in unique_hits or hit['_composite_score'] > unique_hits[content_id]['_composite_score']:
                        unique_hits[content_id] = hit
            
            # Sort by composite score and limit results
            sorted_hits = sorted(
                unique_hits.values(),
                key=lambda x: x['_composite_score'],
                reverse=True
            )[:max_results]
            
            return {
                'hits': sorted_hits,
                'total_hits': len(sorted_hits),
                'merge_info': {
                    'total_managers': len(manager_results),
                    'total_weight': total_weight,
                    'unique_hits': len(unique_hits),
                    'final_hits': len(sorted_hits)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to merge query results: {str(e)}")
            return {'hits': [], 'total_hits': 0, 'error': str(e)}
    
    async def _select_best_results(self, manager_results: Dict[str, Any], 
                                 max_results: int) -> Dict[str, Any]:
        """Select best results from single manager"""
        best_manager = None
        best_weight = 0
        best_count = 0
        
        # Find manager with highest weight and results
        for manager_name, result_data in manager_results.items():
            if 'error' in result_data:
                continue
            
            weight = result_data['weight']
            count = result_data['count']
            
            if weight > best_weight or (weight == best_weight and count > best_count):
                best_manager = manager_name
                best_weight = weight
                best_count = count
        
        if best_manager and best_manager in manager_results:
            results = manager_results[best_manager]['results']
            hits = results.get('hits', [])[:max_results]
            
            return {
                'hits': hits,
                'total_hits': len(hits),
                'selected_manager': best_manager,
                'selection_weight': best_weight
            }
        
        return {'hits': [], 'total_hits': 0}
    
    async def _update_query_statistics(self, query_type: QueryType, query_time: float,
                                     manager_results: Dict[str, Any]):
        """Update query performance statistics"""



        try:
            stats_key = query_type.value
            
            if stats_key not in self.query_stats:
                self.query_stats[stats_key] = {
                    'total_queries': 0,
                    'total_time': 0.0,
                    'average_time': 0.0,
                    'manager_performance': {}
                }
            
            stats = self.query_stats[stats_key]
            stats['total_queries'] += 1
            stats['total_time'] += query_time
            stats['average_time'] = stats['total_time'] / stats['total_queries']
            
            # Update manager-specific performance
            for manager_name, result_data in manager_results.items():
                if manager_name not in stats['manager_performance']:
                    stats['manager_performance'][manager_name] = {
                        'success_count': 0,
                        'error_count': 0,
                        'average_results': 0.0
                    }
                
                manager_stats = stats['manager_performance'][manager_name]
                
                if 'error' in result_data:
                    manager_stats['error_count'] += 1
                else:
                    manager_stats['success_count'] += 1
                    count = result_data.get('count', 0)
                    total_success = manager_stats['success_count']
                    manager_stats['average_results'] = (
                        (manager_stats['average_results'] * (total_success - 1) + count) / total_success
                    )
            
        except Exception as e:
            logger.debug(f"Failed to update query statistics: {str(e)}")
    
    async def _load_performance_baselines(self):
        """Load performance baselines for index selection"""



        try:
            # Initialize performance tracking for each manager
            for manager_name in self.managers:
                self.index_performance[manager_name] = {
                    'average_query_time': 0.0,
                    'success_rate': 1.0,
                    'result_quality': 0.8,
                    'load_factor': 0.0,
                    'last_updated': datetime.now()
                }
            
            logger.info("Performance baselines initialized")
            
        except Exception as e:
            logger.debug(f"Failed to load performance baselines: {str(e)}")
    
    async def _setup_optimization_scheduling(self):
        """Setup automatic optimization scheduling"""
        # This would typically start background optimization tasks
        pass
    
    async def optimize_composite_indexes(self) -> Dict[str, Any]:
        """Optimize all composite indexes"""



        try:
            start_time = datetime.now()
            optimization_results = {}
            
            # Optimize each manager in parallel
            optimize_tasks = []
            for manager_name, manager in self.managers.items():
                if hasattr(manager, 'optimize_all_indexes'):
                    task = asyncio.create_task(manager.optimize_all_indexes())
                    optimize_tasks.append((manager_name, task))
                elif hasattr(manager, 'optimize_index'):
                    # Try to optimize default index
                    task = asyncio.create_task(manager.optimize_index('default'))
                    optimize_tasks.append((manager_name, task))
            
            # Wait for all optimizations
            results = await asyncio.gather(
                *[task for _, task in optimize_tasks], 
                return_exceptions=True
            )
            
            # Process results
            for (manager_name, _), result in zip(optimize_tasks, results):
                if isinstance(result, Exception):
                    optimization_results[manager_name] = {'error': str(result)}
                else:
                    optimization_results[manager_name] = result or {'status': 'completed'}
            
            optimization_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'total_time': optimization_time,
                'managers_optimized': len(optimization_results),
                'results': optimization_results,
                'completed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize composite indexes: {str(e)}")
            return {'error': str(e)}
    
    async def get_composite_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics for all composite indexes"""



        try:
            stats = {
                'query_statistics': self.query_stats,
                'index_performance': self.index_performance,
                'manager_statistics': {},
                'routing_configuration': {
                    query_type.value: routes for query_type, routes in self.routing_config.items()
                }
            }
            
            # Get statistics from each manager
            for manager_name, manager in self.managers.items():
                try:
                    if hasattr(manager, 'get_index_stats'):
                        manager_stats = await manager.get_index_stats()
                        stats['manager_statistics'][manager_name] = manager_stats
                    elif hasattr(manager, 'get_performance_metrics'):
                        manager_stats = await manager.get_performance_metrics()
                        stats['manager_statistics'][manager_name] = manager_stats
                except Exception as e:
                    stats['manager_statistics'][manager_name] = {'error': str(e)}
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get composite statistics: {str(e)}")
            return {'error': str(e)}
    
    async def cleanup(self):
        """Cleanup all managers and resources"""



        try:
            # Cleanup all managers in parallel
            cleanup_tasks = []
            for manager_name, manager in self.managers.items():
                if hasattr(manager, 'cleanup'):
                    task = asyncio.create_task(manager.cleanup())
                    cleanup_tasks.append((manager_name, task))
            
            # Wait for all cleanups
            if cleanup_tasks:
                await asyncio.gather(
                    *[task for _, task in cleanup_tasks], 
                    return_exceptions=True
                )
            
            # Cleanup performance tracker
            if self.performance_tracker:
                await self.performance_tracker.cleanup()
            
            logger.info("CompositeIndexManager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during CompositeIndexManager cleanup: {str(e)}")
