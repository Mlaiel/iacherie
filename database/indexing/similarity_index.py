"""Similarity Index Manager for IA-Influencer-Agent Platform

Advanced similarity indexing system for cross-modal content matching
and duplicate detection with enterprise-grade performance optimization.

🚀 Enterprise Team Project Specialties:
✅ Lead Dev + Architecte Développeur IA
✅ Développeur Backend Senior (Python/FastAPI/Django)  
✅ Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
✅ Spécialiste Sécurité Backend
✅ Architecte Microservices
✅ Développeur Audio
✅ DevOps Engineer
✅ IA Prompt Engineer

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. 
Unauthorized use, modification, or distribution by any individual or entity 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict
import json
import pickle
from dataclasses import dataclass

from ..connections.postgresql_manager import PostgreSQLManager
from ..connections.redis_manager import RedisManager
from ..monitoring.performance_tracker import PerformanceTracker
from ..security.similarity_security import SimilaritySecurityManager

logger = logging.getLogger(__name__)

@dataclass
class SimilarityResult:
    """
Data class for similarity search results"""
    content_id: str
    matched_content_id: str
    similarity_score: float
    confidence_level: float
    match_type: str
    metadata: Dict[str, Any]
    detected_at: datetime

class SimilarityMatchType:
    """
Types of similarity matches"""

    EXACT_MATCH = "exact_match"
    NEAR_DUPLICATE = "near_duplicate"
    SIMILAR_CONTENT = "similar_content"
    RELATED_CONTENT = "related_content"
    CROSS_MODAL = "cross_modal"
    TEMPORAL_MATCH = "temporal_match"
    SEMANTIC_MATCH = "semantic_match"

class SimilarityAlgorithm:
    """Similarity computation algorithms"""

    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    JACCARD = "jaccard"
    HAMMING = "hamming"
    PEARSON = "pearson"
    MANHATTAN = "manhattan"
    STRUCTURAL = "structural"

class SimilarityIndexManager:
    """
    Ultra-advanced similarity index manager for IA-Influencer platform
    
    Provides comprehensive similarity matching capabilities:
    - Multi-modal content similarity (audio, video, image, text)
    - Cross-modal similarity detection
    - Real-time similarity monitoring
    - Duplicate detection and clustering
    - Performance-optimized similarity search
    - Advanced similarity algorithms
    """
    
    def __init__(self):
        """
Initialize similarity index manager"""
        self.db_manager = PostgreSQLManager()
        self.redis_manager = RedisManager()
        self.performance_tracker = PerformanceTracker()
        self.security_manager = SimilaritySecurityManager()
        
        # Similarity thresholds by content type and match type
        self.similarity_thresholds = {
            'audio': {
                SimilarityMatchType.EXACT_MATCH: 0.95,
                SimilarityMatchType.NEAR_DUPLICATE: 0.85,
                SimilarityMatchType.SIMILAR_CONTENT: 0.75,
                SimilarityMatchType.RELATED_CONTENT: 0.65
            },
            'video': {
                SimilarityMatchType.EXACT_MATCH: 0.92,
                SimilarityMatchType.NEAR_DUPLICATE: 0.82,
                SimilarityMatchType.SIMILAR_CONTENT: 0.72,
                SimilarityMatchType.RELATED_CONTENT: 0.62
            },
            'image': {
                SimilarityMatchType.EXACT_MATCH: 0.98,
                SimilarityMatchType.NEAR_DUPLICATE: 0.88,
                SimilarityMatchType.SIMILAR_CONTENT: 0.78,
                SimilarityMatchType.RELATED_CONTENT: 0.68
            },
            'text': {
                SimilarityMatchType.EXACT_MATCH: 0.95,
                SimilarityMatchType.NEAR_DUPLICATE: 0.80,
                SimilarityMatchType.SIMILAR_CONTENT: 0.70,
                SimilarityMatchType.RELATED_CONTENT: 0.60
            },
            'composite': {
                SimilarityMatchType.EXACT_MATCH: 0.90,
                SimilarityMatchType.NEAR_DUPLICATE: 0.75,
                SimilarityMatchType.SIMILAR_CONTENT: 0.65,
                SimilarityMatchType.RELATED_CONTENT: 0.55,
                SimilarityMatchType.CROSS_MODAL: 0.50
            }
        }
        
        # Algorithm configurations
        self.algorithm_configs = {
            SimilarityAlgorithm.COSINE: {
                'normalize_vectors': True,
                'use_magnitude': False,
                'precision': 'float32'
            },
            SimilarityAlgorithm.EUCLIDEAN: {
                'normalize_vectors': False,
                'use_squared_distance': False,
                'precision': 'float32'
            },
            SimilarityAlgorithm.JACCARD: {
                'binary_threshold': 0.5,
                'use_weighted': False,
                'precision': 'float32'
            },
            SimilarityAlgorithm.HAMMING: {
                'binary_vectors': True,
                'normalize_by_length': True,
                'precision': 'uint8'
            }
        }
        
        # Performance settings
        self.batch_size = 500
        self.cache_size = 100000
        self.similarity_cache_ttl = 1800  # 30 minutes
        self.index_update_interval = 300  # 5 minutes
        
        # Runtime statistics
        self.similarity_stats = defaultdict(lambda: {
            'total_comparisons': 0,
            'matches_found': 0,
            'false_positives': 0,
            'average_score': 0.0,
            'processing_time': 0.0,
            'last_updated': datetime.now()
        })
        
        logger.info("SimilarityIndexManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize similarity index manager"""
        try:
            # Initialize database connections
            if not await self.db_manager.initialize():
                raise Exception("Failed to initialize PostgreSQL manager")
                
            if not await self.redis_manager.initialize():
                raise Exception("Failed to initialize Redis manager")
            
            # Initialize tracking and security
            await self.performance_tracker.initialize()
            await self.security_manager.initialize()
            
            # Setup database schema
            await self._setup_similarity_schema()
            
            # Create optimized indexes
            await self._create_similarity_indexes()
            
            # Load existing similarity data
            await self._load_similarity_mappings()
            
            # Setup background processing
            await self._setup_background_processing()
            
            logger.info("SimilarityIndexManager initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize SimilarityIndexManager: {str(e)}")
            return False
    
    async def _setup_similarity_schema(self):
        """Setup database schema for similarity management"""
        conn = await self.db_manager.get_connection()
        try:
            # Similarity mappings table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS content_similarity_mappings (
                    mapping_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    source_content_id VARCHAR(255) NOT NULL,
                    target_content_id VARCHAR(255) NOT NULL,
                    source_content_type VARCHAR(50) NOT NULL,
                    target_content_type VARCHAR(50) NOT NULL,
                    similarity_score FLOAT NOT NULL CHECK (similarity_score >= 0 AND similarity_score <= 1),
                    match_type VARCHAR(50) NOT NULL,
                    algorithm_used VARCHAR(50) NOT NULL,
                    confidence_level FLOAT NOT NULL CHECK (confidence_level >= 0 AND confidence_level <= 1),
                    match_details JSONB DEFAULT '{}',
                    is_cross_modal BOOLEAN DEFAULT FALSE,
                    verified_match BOOLEAN DEFAULT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    CONSTRAINT no_self_similarity CHECK (source_content_id != target_content_id),
                    CONSTRAINT unique_similarity_pair UNIQUE (source_content_id, target_content_id)
                );
            """)
            
            # Similarity clusters table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS similarity_clusters (
                    cluster_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    cluster_name VARCHAR(255),
                    cluster_type VARCHAR(50) NOT NULL,
                    content_type VARCHAR(50) NOT NULL,
                    cluster_centroid BYTEA,
                    member_count INTEGER DEFAULT 0,
                    average_similarity FLOAT DEFAULT 0.0,
                    quality_score FLOAT DEFAULT 0.0,
                    cluster_metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            # Cluster memberships table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS cluster_memberships (
                    membership_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    cluster_id UUID REFERENCES similarity_clusters(cluster_id) ON DELETE CASCADE,
                    content_id VARCHAR(255) NOT NULL,
                    membership_score FLOAT NOT NULL CHECK (membership_score >= 0 AND membership_score <= 1),
                    distance_to_centroid FLOAT DEFAULT 0.0,
                    is_core_member BOOLEAN DEFAULT FALSE,
                    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    CONSTRAINT unique_cluster_membership UNIQUE (cluster_id, content_id)
                );
            """)
            
            # Similarity processing queue
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS similarity_processing_queue (
                    queue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    content_id VARCHAR(255) NOT NULL,
                    content_type VARCHAR(50) NOT NULL,
                    processing_type VARCHAR(50) NOT NULL,
                    priority INTEGER DEFAULT 5,
                    processing_params JSONB DEFAULT '{}',
                    status VARCHAR(20) DEFAULT 'pending',
                    error_message TEXT,
                    attempts INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 3,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    started_at TIMESTAMP WITH TIME ZONE,
                    completed_at TIMESTAMP WITH TIME ZONE
                );
            """)
            
            # Similarity statistics table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS similarity_statistics (
                    stat_id SERIAL PRIMARY KEY,
                    content_type VARCHAR(50) NOT NULL,
                    algorithm_used VARCHAR(50) NOT NULL,
                    match_type VARCHAR(50) NOT NULL,
                    total_comparisons INTEGER DEFAULT 0,
                    matches_found INTEGER DEFAULT 0,
                    false_positives INTEGER DEFAULT 0,
                    average_score FLOAT DEFAULT 0.0,
                    processing_time FLOAT DEFAULT 0.0,
                    date_collected DATE DEFAULT CURRENT_DATE,
                    UNIQUE(content_type, algorithm_used, match_type, date_collected)
                );
            """)
            
            logger.info("Similarity database schema setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup similarity schema: {str(e)}")
            raise
        finally:
            await self.db_manager.return_connection(conn)
    
    async def _create_similarity_indexes(self):
        """Create optimized database indexes for similarity operations"""
        conn = await self.db_manager.get_connection()
        try:
            indexes = [
                # Similarity mappings indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_similarity_source ON content_similarity_mappings (source_content_id);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_similarity_target ON content_similarity_mappings (target_content_id);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_similarity_score ON content_similarity_mappings (similarity_score DESC);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_similarity_type_score ON content_similarity_mappings (match_type, similarity_score DESC);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_similarity_cross_modal ON content_similarity_mappings (is_cross_modal, similarity_score DESC);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_similarity_verified ON content_similarity_mappings (verified_match, similarity_score DESC);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_similarity_created ON content_similarity_mappings (created_at DESC);",
                
                # Content type indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_similarity_source_type ON content_similarity_mappings (source_content_type, similarity_score DESC);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_similarity_target_type ON content_similarity_mappings (target_content_type, similarity_score DESC);",
                
                # Cluster indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_clusters_type ON similarity_clusters (cluster_type, content_type);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_clusters_quality ON similarity_clusters (quality_score DESC);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_clusters_size ON similarity_clusters (member_count DESC);",
                
                # Membership indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_memberships_cluster ON cluster_memberships (cluster_id);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_memberships_content ON cluster_memberships (content_id);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_memberships_score ON cluster_memberships (membership_score DESC);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_memberships_core ON cluster_memberships (is_core_member, membership_score DESC);",
                
                # Processing queue indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_queue_status ON similarity_processing_queue (status, priority DESC);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_queue_content ON similarity_processing_queue (content_id, processing_type);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_queue_created ON similarity_processing_queue (created_at DESC);",
                
                # Statistics indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stats_type_alg ON similarity_statistics (content_type, algorithm_used, date_collected DESC);",
                
                # GIN indexes for JSONB fields
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_similarity_details_gin ON content_similarity_mappings USING GIN (match_details);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cluster_metadata_gin ON similarity_clusters USING GIN (cluster_metadata);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_queue_params_gin ON similarity_processing_queue USING GIN (processing_params);"
            ]
            
            for index_sql in indexes:
                try:
                    await conn.execute(index_sql)
                except Exception as e:
                    logger.debug(f"Index creation note: {str(e)}")
            
            logger.info("Similarity indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create similarity indexes: {str(e)}")
            raise
        finally:
            await self.db_manager.return_connection(conn)
    
    async def compute_similarity(self, source_content_id: str, target_content_id: str,
                               source_features: np.ndarray, target_features: np.ndarray,
                               content_type: str, algorithm: str = SimilarityAlgorithm.COSINE) -> SimilarityResult:
        """Compute similarity between two content items"""
        try:
            # Validate security permissions
            if not await self.security_manager.validate_similarity_computation(
                source_content_id, target_content_id
            ):
                raise Exception("Similarity computation not authorized")
            
            start_time = datetime.now()
            
            # Compute similarity score based on algorithm
            similarity_score = await self._compute_similarity_score(
                source_features, target_features, algorithm
            )
            
            # Determine match type based on score and thresholds
            match_type = self._determine_match_type(similarity_score, content_type)
            
            # Calculate confidence level
            confidence_level = self._calculate_confidence_level(
                similarity_score, source_features, target_features, algorithm
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create similarity result
            result = SimilarityResult(
                content_id=source_content_id,
                matched_content_id=target_content_id,
                similarity_score=float(similarity_score),
                confidence_level=float(confidence_level),
                match_type=match_type,
                metadata={
                    'algorithm_used': algorithm,
                    'content_type': content_type,
                    'processing_time': processing_time,
                    'feature_dimensions': {
                        'source': source_features.shape,
                        'target': target_features.shape
                    }
                },
                detected_at=datetime.now()
            )
            
            # Store similarity mapping if significant
            if similarity_score >= self.similarity_thresholds[content_type][SimilarityMatchType.RELATED_CONTENT]:
                await self._store_similarity_mapping(result)
            
            # Update statistics
            self.similarity_stats[f"{content_type}_{algorithm}"].update({
                'total_comparisons': self.similarity_stats[f"{content_type}_{algorithm}"]['total_comparisons'] + 1,
                'processing_time': processing_time,
                'last_updated': datetime.now()
            })
            
            if match_type != SimilarityMatchType.RELATED_CONTENT:
                self.similarity_stats[f"{content_type}_{algorithm}"]['matches_found'] += 1
            
            # Log performance
            await self.performance_tracker.log_index_operation(
                f"similarity_{content_type}_{algorithm}", 'compute', processing_time,
                {'similarity_score': similarity_score, 'match_type': match_type}
            )
            
            logger.debug(f"Similarity computed: {similarity_score:.3f} ({match_type}) in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"Failed to compute similarity: {str(e)}")
            raise
    
    async def _compute_similarity_score(self, features1: np.ndarray, features2: np.ndarray,
                                      algorithm: str) -> float:
        """Compute similarity score using specified algorithm"""
        config = self.algorithm_configs.get(algorithm, {})
        
        if algorithm == SimilarityAlgorithm.COSINE:
            # Cosine similarity
            if config.get('normalize_vectors', True):
                features1 = features1 / np.linalg.norm(features1)
                features2 = features2 / np.linalg.norm(features2)
            
            similarity = np.dot(features1, features2)
            return float(np.clip(similarity, 0.0, 1.0))
            
        elif algorithm == SimilarityAlgorithm.EUCLIDEAN:
            # Euclidean distance to similarity
            distance = np.linalg.norm(features1 - features2)
            if config.get('use_squared_distance', False):
                distance = distance ** 2
            
            # Convert distance to similarity (0-1 range)
            max_distance = np.sqrt(len(features1))  # Maximum possible distance
            similarity = 1.0 - (distance / max_distance)
            return float(np.clip(similarity, 0.0, 1.0))
            
        elif algorithm == SimilarityAlgorithm.JACCARD:
            # Jaccard similarity for binary/sparse features
            threshold = config.get('binary_threshold', 0.5)
            binary1 = features1 > threshold
            binary2 = features2 > threshold
            
            intersection = np.sum(binary1 & binary2)
            union = np.sum(binary1 | binary2)
            
            if union == 0:
                return 0.0
            
            similarity = intersection / union
            return float(similarity)
            
        elif algorithm == SimilarityAlgorithm.HAMMING:
            # Hamming distance to similarity
            if config.get('binary_vectors', True):
                # Convert to binary if needed
                features1 = (features1 > 0.5).astype(np.uint8)
                features2 = (features2 > 0.5).astype(np.uint8)
            
            hamming_distance = np.sum(features1 != features2)
            
            if config.get('normalize_by_length', True):
                hamming_distance = hamming_distance / len(features1)
            
            similarity = 1.0 - hamming_distance
            return float(np.clip(similarity, 0.0, 1.0))
            
        elif algorithm == SimilarityAlgorithm.PEARSON:
            # Pearson correlation coefficient
            correlation = np.corrcoef(features1, features2)[0, 1]
            if np.isnan(correlation):
                return 0.0
            
            # Convert from [-1, 1] to [0, 1]
            similarity = (correlation + 1.0) / 2.0
            return float(np.clip(similarity, 0.0, 1.0))
            
        elif algorithm == SimilarityAlgorithm.MANHATTAN:
            # Manhattan distance to similarity
            distance = np.sum(np.abs(features1 - features2))
            max_distance = np.sum(np.abs(features1) + np.abs(features2))
            
            if max_distance == 0:
                return 1.0
            
            similarity = 1.0 - (distance / max_distance)
            return float(np.clip(similarity, 0.0, 1.0))
            
        else:
            raise ValueError(f"Unsupported similarity algorithm: {algorithm}")
    
    def _determine_match_type(self, similarity_score: float, content_type: str) -> str:
        """Determine match type based on similarity score and thresholds"""
        thresholds = self.similarity_thresholds.get(content_type, 
                                                   self.similarity_thresholds['composite'])
        
        if similarity_score >= thresholds[SimilarityMatchType.EXACT_MATCH]:
            return SimilarityMatchType.EXACT_MATCH
        elif similarity_score >= thresholds[SimilarityMatchType.NEAR_DUPLICATE]:
            return SimilarityMatchType.NEAR_DUPLICATE
        elif similarity_score >= thresholds[SimilarityMatchType.SIMILAR_CONTENT]:
            return SimilarityMatchType.SIMILAR_CONTENT
        else:
            return SimilarityMatchType.RELATED_CONTENT
    
    def _calculate_confidence_level(self, similarity_score: float, features1: np.ndarray,
                                  features2: np.ndarray, algorithm: str) -> float:
        """
Calculate confidence level for similarity score"""
        # Base confidence from similarity score
        base_confidence = similarity_score
        
        # Adjust based on feature quality
        feature_quality = min(
            1.0,
            (np.std(features1) + np.std(features2)) / 2.0  # Higher variance = higher quality
        )
        
        # Adjust based on feature dimensionality
        dimensionality_factor = min(1.0, len(features1) / 100.0)  # More dimensions = higher confidence
        
        # Algorithm-specific adjustments
        algorithm_factor = 1.0
        if algorithm == SimilarityAlgorithm.COSINE:
            algorithm_factor = 1.1  # Cosine is generally more reliable
        elif algorithm == SimilarityAlgorithm.HAMMING:
            algorithm_factor = 0.9   # Hamming can be less precise
        
        # Combined confidence
        confidence = base_confidence * feature_quality * dimensionality_factor * algorithm_factor
        return float(np.clip(confidence, 0.0, 1.0))
    
    async def _store_similarity_mapping(self, result: SimilarityResult):
        """
Store similarity mapping in database"""
        try:
            conn = await self.db_manager.get_connection()
            
            # Determine if this is cross-modal
            source_type = result.metadata.get('content_type', 'unknown')
            target_type = result.metadata.get('content_type', 'unknown')
            is_cross_modal = source_type != target_type
            
            await conn.execute("""
                INSERT INTO content_similarity_mappings 
                (source_content_id, target_content_id, source_content_type, target_content_type,
                 similarity_score, match_type, algorithm_used, confidence_level, match_details,
                 is_cross_modal)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (source_content_id, target_content_id) 
                DO UPDATE SET
                    similarity_score = GREATEST(content_similarity_mappings.similarity_score, EXCLUDED.similarity_score),
                    match_type = CASE 
                        WHEN EXCLUDED.similarity_score > content_similarity_mappings.similarity_score 
                        THEN EXCLUDED.match_type 
                        ELSE content_similarity_mappings.match_type 
                    END,
                    algorithm_used = EXCLUDED.algorithm_used,
                    confidence_level = EXCLUDED.confidence_level,
                    match_details = EXCLUDED.match_details,
                    updated_at = NOW()
            """, result.content_id, result.matched_content_id, source_type, target_type,
                result.similarity_score, result.match_type, 
                result.metadata['algorithm_used'], result.confidence_level,
                json.dumps(result.metadata), is_cross_modal)
            
        except Exception as e:
            logger.error(f"Failed to store similarity mapping: {str(e)}")
        finally:
            await self.db_manager.return_connection(conn)
    
    async def find_similar_content(self, content_id: str, content_type: str,
                                 max_results: int = 50, min_similarity: float = 0.7,
                                 include_cross_modal: bool = False) -> List[SimilarityResult]:
        """Find similar content for a given content item"""
        try:
            conn = await self.db_manager.get_connection()
            start_time = datetime.now()
            
            # Build query based on parameters
            where_conditions = [
                "csm.source_content_id = $1",
                "csm.similarity_score >= $2"
            ]
            params = [content_id, min_similarity, max_results]
            param_count = 3
            
            if not include_cross_modal:
                param_count += 1
                where_conditions.append(f"csm.source_content_type = ${param_count}")
                params.append(content_type)
            
            where_clause = " AND ".join(where_conditions)
            
            results = await conn.fetch(f"""
                SELECT csm.target_content_id, csm.target_content_type, csm.similarity_score,
                       csm.match_type, csm.algorithm_used, csm.confidence_level,
                       csm.match_details, csm.is_cross_modal, csm.created_at
                FROM content_similarity_mappings csm
                WHERE {where_clause}
                ORDER BY csm.similarity_score DESC, csm.confidence_level DESC
                LIMIT $3
            """, *params)
            
            search_time = (datetime.now() - start_time).total_seconds()
            
            # Convert to SimilarityResult objects
            similarity_results = []
            for row in results:
                result = SimilarityResult(
                    content_id=content_id,
                    matched_content_id=row['target_content_id'],
                    similarity_score=float(row['similarity_score']),
                    confidence_level=float(row['confidence_level']),
                    match_type=row['match_type'],
                    metadata={
                        'algorithm_used': row['algorithm_used'],
                        'target_content_type': row['target_content_type'],
                        'is_cross_modal': row['is_cross_modal'],
                        'search_time': search_time,
                        **row['match_details']
                    },
                    detected_at=row['created_at']
                )
                similarity_results.append(result)
            
            # Log performance
            await self.performance_tracker.log_index_operation(
                f"similarity_search_{content_type}", 'find', search_time,
                {'results_count': len(similarity_results), 'min_similarity': min_similarity}
            )
            
            logger.debug(f"Found {len(similarity_results)} similar content items in {search_time:.3f}s")
            return similarity_results
            
        except Exception as e:
            logger.error(f"Failed to find similar content: {str(e)}")
            return []
        finally:
            await self.db_manager.return_connection(conn)
    
    async def detect_duplicates(self, content_type: str, similarity_threshold: float = 0.95) -> List[List[str]]:
        """Detect potential duplicate content clusters"""
        try:
            conn = await self.db_manager.get_connection()
            start_time = datetime.now()
            
            # Find high-similarity pairs
            results = await conn.fetch("""
                SELECT source_content_id, target_content_id, similarity_score
                FROM content_similarity_mappings
                WHERE source_content_type = $1 
                  AND target_content_type = $1
                  AND similarity_score >= $2
                  AND match_type IN ('exact_match', 'near_duplicate')
                ORDER BY similarity_score DESC
            """, content_type, similarity_threshold)
            
            # Build duplicate clusters using union-find algorithm
            duplicate_clusters = self._build_duplicate_clusters(results)
            
            detection_time = (datetime.now() - start_time).total_seconds()
            
            # Log performance
            await self.performance_tracker.log_index_operation(
                f"duplicate_detection_{content_type}", 'detect', detection_time,
                {'clusters_found': len(duplicate_clusters), 'threshold': similarity_threshold}
            )
            
            logger.info(f"Detected {len(duplicate_clusters)} duplicate clusters in {detection_time:.3f}s")
            return duplicate_clusters
            
        except Exception as e:
            logger.error(f"Failed to detect duplicates: {str(e)}")
            return []
        finally:
            await self.db_manager.return_connection(conn)
    
    def _build_duplicate_clusters(self, similarity_pairs: List[Dict]) -> List[List[str]]:
        """Build duplicate clusters using union-find algorithm"""
        # Union-Find data structure
        parent = {}
        rank = {}
        
        def find(x):
            if x not in parent:
                parent[x] = x
                rank[x] = 0
            if parent[x] != x:
                parent[x] = find(parent[x])  # Path compression
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px == py:
                return
            # Union by rank
            if rank[px] < rank[py]:
                parent[px] = py
            elif rank[px] > rank[py]:
                parent[py] = px
            else:
                parent[py] = px
                rank[px] += 1
        
        # Process similarity pairs
        for pair in similarity_pairs:
            union(pair['source_content_id'], pair['target_content_id'])
        
        # Group content IDs by cluster
        clusters = defaultdict(list)
        for content_id in parent:
            cluster_root = find(content_id)
            clusters[cluster_root].append(content_id)
        
        # Return clusters with more than one member
        return [cluster for cluster in clusters.values() if len(cluster) > 1]
    
    async def create_similarity_cluster(self, content_ids: List[str], cluster_type: str,
                                      content_type: str, cluster_name: Optional[str] = None) -> Optional[str]:
        """
Create a new similarity cluster"""
        try:
            conn = await self.db_manager.get_connection()
            
            # Create cluster
            cluster_id = await conn.fetchval("""
                INSERT INTO similarity_clusters 
                (cluster_name, cluster_type, content_type, member_count)
                VALUES ($1, $2, $3, $4)
                RETURNING cluster_id
            """, cluster_name or f"{cluster_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                cluster_type, content_type, len(content_ids))
            
            # Add cluster memberships
            membership_data = [
                (cluster_id, content_id, 1.0, 0.0, True)  # All members are core for now
                for content_id in content_ids
            ]
            
            await conn.executemany("""
                INSERT INTO cluster_memberships 
                (cluster_id, content_id, membership_score, distance_to_centroid, is_core_member)
                VALUES ($1, $2, $3, $4, $5)
            """, membership_data)
            
            logger.info(f"Created similarity cluster {cluster_id} with {len(content_ids)} members")
            return str(cluster_id)
            
        except Exception as e:
            logger.error(f"Failed to create similarity cluster: {str(e)}")
            return None
        finally:
            await self.db_manager.return_connection(conn)
    
    async def _load_similarity_mappings(self):
        """Load existing similarity mappings and statistics"""
        try:
            conn = await self.db_manager.get_connection()
            
            # Load recent statistics
            stats = await conn.fetch("""
                SELECT content_type, algorithm_used, match_type, total_comparisons,
                       matches_found, false_positives, average_score, processing_time
                FROM similarity_statistics
                WHERE date_collected >= CURRENT_DATE - INTERVAL '7 days'
            """)
            
            for stat in stats:
                key = f"{stat['content_type']}_{stat['algorithm_used']}"
                self.similarity_stats[key].update({
                    'total_comparisons': stat['total_comparisons'],
                    'matches_found': stat['matches_found'],
                    'false_positives': stat['false_positives'],
                    'average_score': stat['average_score'],
                    'processing_time': stat['processing_time']
                })
            
            logger.info(f"Loaded similarity statistics for {len(stats)} configurations")
            
        except Exception as e:
            logger.debug(f"Failed to load similarity mappings: {str(e)}")
        finally:
            await self.db_manager.return_connection(conn)
    
    async def _setup_background_processing(self):
        """Setup background processing for similarity tasks"""
        # This would typically start background workers
        pass
    
    async def get_similarity_statistics(self, content_type: Optional[str] = None) -> Dict[str, Any]:
        """
Get comprehensive similarity statistics"""
        try:
            if content_type:
                # Filter statistics for specific content type
                filtered_stats = {
                    key: stats for key, stats in self.similarity_stats.items()
                    if key.startswith(content_type)
                }
                
                return {
                    'content_type': content_type,
                    'algorithm_statistics': filtered_stats,
                    'total_comparisons': sum(s['total_comparisons'] for s in filtered_stats.values()),
                    'total_matches': sum(s['matches_found'] for s in filtered_stats.values())
                }
            else:
                return {
                    'total_algorithm_configurations': len(self.similarity_stats),
                    'algorithm_statistics': dict(self.similarity_stats),
                    'total_comparisons': sum(s['total_comparisons'] for s in self.similarity_stats.values()),
                    'total_matches': sum(s['matches_found'] for s in self.similarity_stats.values()),
                    'average_processing_time': np.mean([
                        s['processing_time'] for s in self.similarity_stats.values()
                        if s['processing_time'] > 0
                    ]) if self.similarity_stats else 0.0
                }
                
        except Exception as e:
            logger.error(f"Failed to get similarity statistics: {str(e)}")
            return {'error': str(e)}
    
    async def cleanup(self):
        """Cleanup resources and save final statistics"""
        try:
            # Save final statistics
            await self._save_final_statistics()
            
            # Cleanup managers
            if self.performance_tracker:
                await self.performance_tracker.cleanup()
            if self.security_manager:
                await self.security_manager.cleanup()
            if self.redis_manager:
                await self.redis_manager.cleanup()
            if self.db_manager:
                await self.db_manager.cleanup()
            
            logger.info("SimilarityIndexManager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during SimilarityIndexManager cleanup: {str(e)}")
    
    async def _save_final_statistics(self):
        """Save final statistics to database"""
        try:
            conn = await self.db_manager.get_connection()
            
            for key, stats in self.similarity_stats.items():
                parts = key.split('_', 1)
                if len(parts) == 2:
                    content_type, algorithm = parts[0], parts[1]
                    
                    await conn.execute("""
                        INSERT INTO similarity_statistics 
                        (content_type, algorithm_used, match_type, total_comparisons,
                         matches_found, false_positives, average_score, processing_time)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        ON CONFLICT (content_type, algorithm_used, match_type, date_collected)
                        DO UPDATE SET
                            total_comparisons = EXCLUDED.total_comparisons,
                            matches_found = EXCLUDED.matches_found,
                            false_positives = EXCLUDED.false_positives,
                            average_score = EXCLUDED.average_score,
                            processing_time = EXCLUDED.processing_time
                    """, content_type, algorithm, 'all', stats['total_comparisons'],
                        stats['matches_found'], stats['false_positives'],
                        stats['average_score'], stats['processing_time'])
            
            logger.info("Final similarity statistics saved")
            
        except Exception as e:
            logger.debug(f"Failed to save final statistics: {str(e)}")
        finally:
            await self.db_manager.return_connection(conn)
