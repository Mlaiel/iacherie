"""
Fingerprint Cache for IA Influencer Agent Platform
Specialized caching for AI fingerprinting and content similarity detection

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
import json
import hashlib
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from .redis_cache import RedisCache, RedisConfig
from .vector_cache import VectorCache, FAISSCache
from .memory_cache import MemoryCache

logger = logging.getLogger(__name__)

class FingerprintType(Enum):
    """Types of fingerprints"""
    AUDIO_CHROMAPRINT = "audio_chromaprint"
    AUDIO_SPECTRAL = "audio_spectral"
    VIDEO_PERCEPTUAL = "video_perceptual"
    VIDEO_FRAME = "video_frame"
    IMAGE_PERCEPTUAL = "image_perceptual"
    IMAGE_CLIP = "image_clip"
    TEXT_SEMANTIC = "text_semantic"
    TEXT_SYNTACTIC = "text_syntactic"

class MatchConfidence(Enum):
    """Match confidence levels"""
    EXACT = "exact"        # 95-100%
    HIGH = "high"          # 85-95%
    MEDIUM = "medium"      # 70-85%
    LOW = "low"           # 50-70%
    NONE = "none"         # <50%

@dataclass
class FingerprintData:
    """Fingerprint data structure"""
    content_id: str
    fingerprint_type: FingerprintType
    fingerprint_hash: str
    vector_data: np.ndarray
    metadata: Dict[str, Any]
    
    # Content properties
    content_type: str  # audio, video, image, text
    file_size: int
    duration: Optional[float] = None
    dimensions: Optional[Tuple[int, int]] = None
    
    # Fingerprint properties
    algorithm_version: str = "1.0"
    extraction_params: Dict[str, Any] = None
    quality_score: float = 0.0
    
    # Timestamps
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.extraction_params is None:
            self.extraction_params = {}

@dataclass
class SimilarityMatch:
    """Similarity match result"""
    target_content_id: str
    query_content_id: str
    similarity_score: float
    confidence_level: MatchConfidence
    fingerprint_type: FingerprintType
    match_details: Dict[str, Any]
    
    # Match metadata
    matched_at: datetime
    algorithm_used: str
    processing_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['confidence_level'] = self.confidence_level.value
        data['fingerprint_type'] = self.fingerprint_type.value
        data['matched_at'] = self.matched_at.isoformat()
        return data

class FingerprintCache:
    """
    Advanced fingerprint cache for AI-powered content identification
    Handles storage and similarity search for multiple fingerprint types
    """
    
    def __init__(self,
                 redis_config: RedisConfig,
                 vector_cache: Optional[VectorCache] = None,
                 similarity_threshold: float = 0.8,
                 max_fingerprints: int = 1000000):
        
        self.similarity_threshold = similarity_threshold
        self.max_fingerprints = max_fingerprints
        
        # Initialize caches
        self.redis_cache = RedisCache(redis_config)
        self.memory_cache = MemoryCache(
            max_size=10000,
            default_ttl=3600  # 1 hour
        )
        
        # Vector cache for similarity search
        if vector_cache:
            self.vector_cache = vector_cache
        else:
            # Create default FAISS cache
            try:
                self.vector_cache = FAISSCache(
                    dimension=512,  # Default dimension
                    index_type="IndexHNSW",
                    max_vectors=max_fingerprints
                )
            except ImportError:
                logger.warning("FAISS not available, using basic vector cache")
                self.vector_cache = VectorCache(
                    dimension=512,
                    max_vectors=max_fingerprints
                )
        
        # Cache key prefixes
        self.FINGERPRINT_PREFIX = "fingerprint"
        self.HASH_PREFIX = "fingerprint:hash"
        self.CONTENT_PREFIX = "fingerprint:content"
        self.MATCHES_PREFIX = "fingerprint:matches"
        self.STATS_PREFIX = "fingerprint:stats"
        
        # Fingerprint type configurations
        self.type_configs = {
            FingerprintType.AUDIO_CHROMAPRINT: {
                'dimension': 128,
                'similarity_threshold': 0.85,
                'algorithm': 'chromaprint',
                'ttl': 86400 * 30  # 30 days
            },
            FingerprintType.AUDIO_SPECTRAL: {
                'dimension': 256,
                'similarity_threshold': 0.80,
                'algorithm': 'spectral_analysis',
                'ttl': 86400 * 30
            },
            FingerprintType.VIDEO_PERCEPTUAL: {
                'dimension': 512,
                'similarity_threshold': 0.75,
                'algorithm': 'perceptual_hash',
                'ttl': 86400 * 7  # 7 days
            },
            FingerprintType.VIDEO_FRAME: {
                'dimension': 1024,
                'similarity_threshold': 0.70,
                'algorithm': 'frame_analysis',
                'ttl': 86400 * 7
            },
            FingerprintType.IMAGE_PERCEPTUAL: {
                'dimension': 256,
                'similarity_threshold': 0.85,
                'algorithm': 'perceptual_hash',
                'ttl': 86400 * 14  # 14 days
            },
            FingerprintType.IMAGE_CLIP: {
                'dimension': 512,
                'similarity_threshold': 0.80,
                'algorithm': 'clip_embedding',
                'ttl': 86400 * 14
            },
            FingerprintType.TEXT_SEMANTIC: {
                'dimension': 768,
                'similarity_threshold': 0.75,
                'algorithm': 'bert_embedding',
                'ttl': 86400 * 7
            },
            FingerprintType.TEXT_SYNTACTIC: {
                'dimension': 300,
                'similarity_threshold': 0.70,
                'algorithm': 'tfidf_vector',
                'ttl': 86400 * 7
            }
        }
        
        # Statistics
        self._stats = {
            'fingerprints_stored': 0,
            'fingerprints_retrieved': 0,
            'similarity_searches': 0,
            'matches_found': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'false_positives': 0,
            'processing_time_total': 0.0
        }
        
        logger.info("FingerprintCache initialized")
    
    async def initialize(self):
        """Initialize cache connections"""
        await self.redis_cache.connect()
    
    def _get_config(self, fingerprint_type: FingerprintType) -> Dict[str, Any]:
        """Get configuration for fingerprint type"""



        return self.type_configs.get(fingerprint_type, {
            'dimension': 512,
            'similarity_threshold': self.similarity_threshold,
            'algorithm': 'default',
            'ttl': 86400 * 7
        })
    
    def _calculate_confidence(self, similarity_score: float) -> MatchConfidence:
        """Calculate confidence level from similarity score"""
        if similarity_score >= 0.95:
            return MatchConfidence.EXACT
        elif similarity_score >= 0.85:
            return MatchConfidence.HIGH
        elif similarity_score >= 0.70:
            return MatchConfidence.MEDIUM
        elif similarity_score >= 0.50:
            return MatchConfidence.LOW
        else:
            return MatchConfidence.NONE
    
    async def store_fingerprint(self,
                              content_id: str,
                              fingerprint_type: FingerprintType,
                              vector_data: Union[np.ndarray, List[float]],
                              metadata: Dict[str, Any],
                              content_type: str = "unknown",
                              file_size: int = 0,
                              duration: Optional[float] = None,
                              dimensions: Optional[Tuple[int, int]] = None,
                              quality_score: float = 0.0) -> bool:
        """Store fingerprint data"""



        
        try:
            import time
            start_time = time.time()
            
            # Convert to numpy array if needed
            if isinstance(vector_data, list):
                vector_data = np.array(vector_data, dtype=np.float32)
            
            # Validate vector dimension
            config = self._get_config(fingerprint_type)
            expected_dim = config['dimension']
            
            if vector_data.shape[0] != expected_dim:
                logger.error(f"Vector dimension mismatch: expected {expected_dim}, got {vector_data.shape[0]}")
                return False
            
            # Generate fingerprint hash
            vector_bytes = vector_data.tobytes()
            fingerprint_hash = hashlib.sha256(vector_bytes).hexdigest()
            
            # Create fingerprint data object
            fingerprint_data = FingerprintData(
                content_id=content_id,
                fingerprint_type=fingerprint_type,
                fingerprint_hash=fingerprint_hash,
                vector_data=vector_data,
                metadata=metadata,
                content_type=content_type,
                file_size=file_size,
                duration=duration,
                dimensions=dimensions,
                quality_score=quality_score,
                algorithm_version=config['algorithm']
            )
            
            # Store in Redis
            fingerprint_key = f"{self.FINGERPRINT_PREFIX}:{content_id}:{fingerprint_type.value}"
            fingerprint_dict = {
                'content_id': content_id,
                'fingerprint_type': fingerprint_type.value,
                'fingerprint_hash': fingerprint_hash,
                'vector_data': vector_data.tolist(),
                'metadata': metadata,
                'content_type': content_type,
                'file_size': file_size,
                'duration': duration,
                'dimensions': dimensions,
                'quality_score': quality_score,
                'algorithm_version': config['algorithm'],
                'created_at': fingerprint_data.created_at.isoformat(),
                'updated_at': fingerprint_data.updated_at.isoformat()
            }
            
            ttl = config['ttl']
            await self.redis_cache.set(
                fingerprint_key,
                json.dumps(fingerprint_dict),
                ttl=ttl
            )
            
            # Store hash mapping
            hash_key = f"{self.HASH_PREFIX}:{fingerprint_hash}"
            await self.redis_cache.set(hash_key, content_id, ttl=ttl)
            
            # Add to vector cache for similarity search
            vector_metadata = {
                'content_id': content_id,
                'content_type': content_type,
                'fingerprint_type': fingerprint_type.value,
                'quality_score': quality_score,
                'file_size': file_size
            }
            
            self.vector_cache.add_vector(
                content_id=content_id,
                vector=vector_data,
                metadata=vector_metadata,
                content_type=content_type,
                fingerprint_hash=fingerprint_hash
            )
            
            # Update content fingerprint list
            await self._update_content_fingerprints(content_id, fingerprint_type)
            
            # Update statistics
            processing_time = time.time() - start_time
            self._stats['fingerprints_stored'] += 1
            self._stats['processing_time_total'] += processing_time
            
            logger.info(f"Stored fingerprint: {content_id} ({fingerprint_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store fingerprint: {e}")
            return False
    
    async def get_fingerprint(self,
                            content_id: str,
                            fingerprint_type: FingerprintType) -> Optional[FingerprintData]:
        """Get fingerprint data"""
        
        # Try memory cache first
        cache_key = f"fp:{content_id}:{fingerprint_type.value}"
        cached_fp = self.memory_cache.get(cache_key)
        if cached_fp:
            self._stats['cache_hits'] += 1
            self._stats['fingerprints_retrieved'] += 1
            return cached_fp
        
        # Try Redis cache
        fingerprint_key = f"{self.FINGERPRINT_PREFIX}:{content_id}:{fingerprint_type.value}"
        fingerprint_data = await self.redis_cache.get(fingerprint_key)
        
        if fingerprint_data:
            try:
                fp_dict = json.loads(fingerprint_data)
                
                # Reconstruct fingerprint data
                vector_data = np.array(fp_dict['vector_data'], dtype=np.float32)
                
                fingerprint = FingerprintData(
                    content_id=fp_dict['content_id'],
                    fingerprint_type=FingerprintType(fp_dict['fingerprint_type']),
                    fingerprint_hash=fp_dict['fingerprint_hash'],
                    vector_data=vector_data,
                    metadata=fp_dict['metadata'],
                    content_type=fp_dict['content_type'],
                    file_size=fp_dict['file_size'],
                    duration=fp_dict.get('duration'),
                    dimensions=fp_dict.get('dimensions'),
                    quality_score=fp_dict.get('quality_score', 0.0),
                    algorithm_version=fp_dict.get('algorithm_version', '1.0'),
                    created_at=datetime.fromisoformat(fp_dict['created_at']),
                    updated_at=datetime.fromisoformat(fp_dict['updated_at'])
                )
                
                # Cache in memory
                self.memory_cache.set(cache_key, fingerprint, ttl=300)
                
                self._stats['cache_hits'] += 1
                self._stats['fingerprints_retrieved'] += 1
                return fingerprint
                
            except Exception as e:
                logger.error(f"Failed to deserialize fingerprint: {e}")
        
        self._stats['cache_misses'] += 1
        return None
    
    async def find_similar_content(self,
                                 query_vector: Union[np.ndarray, List[float]],
                                 fingerprint_type: FingerprintType,
                                 content_type: Optional[str] = None,
                                 top_k: int = 10,
                                 min_similarity: Optional[float] = None) -> List[SimilarityMatch]:
        """Find similar content using fingerprint vectors"""



        
        try:
            import time
            start_time = time.time()
            
            # Convert to numpy array if needed
            if isinstance(query_vector, list):
                query_vector = np.array(query_vector, dtype=np.float32)
            
            # Get configuration for fingerprint type
            config = self._get_config(fingerprint_type)
            similarity_threshold = min_similarity or config['similarity_threshold']
            
            # Search in vector cache
            vector_results = self.vector_cache.search_similar(
                query_vector=query_vector,
                top_k=top_k * 2,  # Get extra results for filtering
                content_type=content_type,
                min_similarity=similarity_threshold
            )
            
            # Convert to similarity matches
            matches = []
            for result in vector_results:
                # Skip if fingerprint type doesn't match
                if result.metadata.get('fingerprint_type') != fingerprint_type.value:
                    continue
                
                confidence = self._calculate_confidence(result.similarity_score)
                
                # Skip low confidence matches unless explicitly requested
                if confidence == MatchConfidence.NONE and min_similarity is None:
                    continue
                
                match = SimilarityMatch(
                    target_content_id=result.content_id,
                    query_content_id="query",  # This would be set by caller
                    similarity_score=result.similarity_score,
                    confidence_level=confidence,
                    fingerprint_type=fingerprint_type,
                    match_details={
                        'algorithm': config['algorithm'],
                        'vector_similarity': result.similarity_score,
                        'target_metadata': result.metadata
                    },
                    matched_at=datetime.utcnow(),
                    algorithm_used=config['algorithm'],
                    processing_time=time.time() - start_time
                )
                
                matches.append(match)
                
                if len(matches) >= top_k:
                    break
            
            # Update statistics
            processing_time = time.time() - start_time
            self._stats['similarity_searches'] += 1
            self._stats['matches_found'] += len(matches)
            self._stats['processing_time_total'] += processing_time
            
            return matches
            
        except Exception as e:
            logger.error(f"Failed to find similar content: {e}")
            return []
    
    async def find_exact_matches(self,
                               fingerprint_hash: str) -> List[str]:
        """Find exact matches by fingerprint hash"""



        
        try:
            hash_key = f"{self.HASH_PREFIX}:{fingerprint_hash}"
            content_id = await self.redis_cache.get(hash_key)
            
            if content_id:
                return [content_id]
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to find exact matches: {e}")
            return []
    
    async def store_match_result(self,
                               match: SimilarityMatch,
                               verified: bool = False,
                               false_positive: bool = False) -> bool:
        """Store similarity match result for analysis"""



        
        try:
            match_key = f"{self.MATCHES_PREFIX}:{match.target_content_id}:{match.query_content_id}"
            
            match_data = match.to_dict()
            match_data.update({
                'verified': verified,
                'false_positive': false_positive,
                'stored_at': datetime.utcnow().isoformat()
            })
            
            # Store for 30 days
            await self.redis_cache.set(
                match_key,
                json.dumps(match_data),
                ttl=86400 * 30
            )
            
            # Update false positive statistics
            if false_positive:
                self._stats['false_positives'] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store match result: {e}")
            return False
    
    async def get_content_fingerprints(self, content_id: str) -> List[FingerprintType]:
        """Get all fingerprint types available for content"""
        
        content_key = f"{self.CONTENT_PREFIX}:{content_id}"
        fingerprint_data = await self.redis_cache.get(content_key)
        
        if fingerprint_data:
            fingerprint_list = json.loads(fingerprint_data)
            return [FingerprintType(fp) for fp in fingerprint_list]
        
        return []
    
    async def delete_fingerprint(self,
                               content_id: str,
                               fingerprint_type: FingerprintType) -> bool:
        """Delete fingerprint data"""



        
        try:
            # Get fingerprint first to get hash
            fingerprint = await self.get_fingerprint(content_id, fingerprint_type)
            if not fingerprint:
                return False
            
            # Delete from Redis
            fingerprint_key = f"{self.FINGERPRINT_PREFIX}:{content_id}:{fingerprint_type.value}"
            await self.redis_cache.delete(fingerprint_key)
            
            # Delete hash mapping
            hash_key = f"{self.HASH_PREFIX}:{fingerprint.fingerprint_hash}"
            await self.redis_cache.delete(hash_key)
            
            # Remove from memory cache
            cache_key = f"fp:{content_id}:{fingerprint_type.value}"
            self.memory_cache.delete(cache_key)
            
            # Remove from vector cache
            self.vector_cache.remove_vector(content_id)
            
            # Update content fingerprint list
            await self._remove_content_fingerprint(content_id, fingerprint_type)
            
            logger.info(f"Deleted fingerprint: {content_id} ({fingerprint_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete fingerprint: {e}")
            return False
    
    async def delete_content_fingerprints(self, content_id: str) -> int:
        """Delete all fingerprints for content"""
        
        fingerprint_types = await self.get_content_fingerprints(content_id)
        deleted_count = 0
        
        for fp_type in fingerprint_types:
            if await self.delete_fingerprint(content_id, fp_type):
                deleted_count += 1
        
        return deleted_count
    
    async def _update_content_fingerprints(self,
                                         content_id: str,
                                         fingerprint_type: FingerprintType):
        """Update list of fingerprints for content"""
        
        content_key = f"{self.CONTENT_PREFIX}:{content_id}"
        fingerprint_data = await self.redis_cache.get(content_key)
        
        if fingerprint_data:
            fingerprint_list = json.loads(fingerprint_data)
        else:
            fingerprint_list = []
        
        if fingerprint_type.value not in fingerprint_list:
            fingerprint_list.append(fingerprint_type.value)
        
        await self.redis_cache.set(
            content_key,
            json.dumps(fingerprint_list),
            ttl=86400 * 30  # 30 days
        )
    
    async def _remove_content_fingerprint(self,
                                        content_id: str,
                                        fingerprint_type: FingerprintType):
        """Remove fingerprint type from content list"""
        
        content_key = f"{self.CONTENT_PREFIX}:{content_id}"
        fingerprint_data = await self.redis_cache.get(content_key)
        
        if fingerprint_data:
            fingerprint_list = json.loads(fingerprint_data)
            if fingerprint_type.value in fingerprint_list:
                fingerprint_list.remove(fingerprint_type.value)
                
                if fingerprint_list:
                    await self.redis_cache.set(
                        content_key,
                        json.dumps(fingerprint_list),
                        ttl=86400 * 30
                    )
                else:
                    await self.redis_cache.delete(content_key)
    
    async def get_fingerprint_stats(self) -> Dict[str, Any]:
        """Get fingerprint statistics"""
        
        # Count fingerprints by type
        type_counts = {}
        for fp_type in FingerprintType:
            pattern = f"{self.FINGERPRINT_PREFIX}:*:{fp_type.value}"
            keys = await self.redis_cache.keys(pattern)
            type_counts[fp_type.value] = len(keys)
        
        # Get vector cache stats
        vector_stats = self.vector_cache.get_stats() if self.vector_cache else {}
        
        # Calculate average processing time
        avg_processing_time = (
            self._stats['processing_time_total'] / 
            max(1, self._stats['fingerprints_stored'] + self._stats['similarity_searches'])
        )
        
        return {
            'fingerprint_stats': self._stats,
            'fingerprints_by_type': type_counts,
            'total_fingerprints': sum(type_counts.values()),
            'vector_cache_stats': vector_stats,
            'avg_processing_time': avg_processing_time,
            'similarity_threshold': self.similarity_threshold,
            'supported_types': [fp.value for fp in FingerprintType]
        }
    
    async def optimize_cache(self):
        """Optimize fingerprint cache performance"""



        
        try:
            # Rebuild vector index if using FAISS
            if hasattr(self.vector_cache, 'rebuild_index'):
                self.vector_cache.rebuild_index()
                logger.info("Rebuilt vector index for better performance")
            
            # Clean up expired fingerprints
            expired_count = 0
            for fp_type in FingerprintType:
                pattern = f"{self.FINGERPRINT_PREFIX}:*:{fp_type.value}"
                keys = await self.redis_cache.keys(pattern)
                
                for key in keys:
                    # Check if key exists (Redis will auto-expire)
                    if not await self.redis_cache.exists(key):
                        expired_count += 1
            
            logger.info(f"Cache optimization completed. {expired_count} expired fingerprints cleaned.")
            
        except Exception as e:
            logger.error(f"Failed to optimize cache: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        redis_stats = await self.redis_cache.get_stats()
        memory_stats = self.memory_cache.get_stats()
        fingerprint_stats = await self.get_fingerprint_stats()
        
        return {
            'cache_stats': {
                'redis_stats': redis_stats,
                'memory_stats': memory_stats,
                'fingerprint_stats': fingerprint_stats
            },
            'performance': {
                'similarity_threshold': self.similarity_threshold,
                'max_fingerprints': self.max_fingerprints
            }
        }
    
    async def close(self):
        """Close cache connections"""
        await self.redis_cache.close()
        self.memory_cache.close()
        if self.vector_cache:
            self.vector_cache.clear()

class SimilarityCache(FingerprintCache):
    """
    Specialized cache for similarity search results and duplicate detection
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Additional prefixes for similarity cache
        self.DUPLICATE_PREFIX = "similarity:duplicate"
        self.NEAR_DUPLICATE_PREFIX = "similarity:near_duplicate"
        self.SEARCH_RESULTS_PREFIX = "similarity:search_results"
    
    async def store_duplicate_group(self,
                                  group_id: str,
                                  content_ids: List[str],
                                  similarity_scores: List[float]) -> bool:
        """Store group of duplicate content"""



        
        try:
            duplicate_key = f"{self.DUPLICATE_PREFIX}:{group_id}"
            
            group_data = {
                'group_id': group_id,
                'content_ids': content_ids,
                'similarity_scores': similarity_scores,
                'created_at': datetime.utcnow().isoformat(),
                'member_count': len(content_ids)
            }
            
            await self.redis_cache.set(
                duplicate_key,
                json.dumps(group_data),
                ttl=86400 * 7  # 7 days
            )
            
            # Store reverse mapping for each content
            for content_id in content_ids:
                content_key = f"{self.DUPLICATE_PREFIX}:content:{content_id}"
                await self.redis_cache.set(content_key, group_id, ttl=86400 * 7)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store duplicate group: {e}")
            return False
    
    async def get_duplicate_group(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get duplicate group for content"""
        
        content_key = f"{self.DUPLICATE_PREFIX}:content:{content_id}"
        group_id = await self.redis_cache.get(content_key)
        
        if group_id:
            duplicate_key = f"{self.DUPLICATE_PREFIX}:{group_id}"
            group_data = await self.redis_cache.get(duplicate_key)
            
            if group_data:
                return json.loads(group_data)
        
        return None
    
    async def cache_search_results(self,
                                 query_hash: str,
                                 results: List[SimilarityMatch],
                                 ttl: int = 3600) -> bool:
        """Cache similarity search results"""



        
        try:
            search_key = f"{self.SEARCH_RESULTS_PREFIX}:{query_hash}"
            
            results_data = {
                'query_hash': query_hash,
                'results': [match.to_dict() for match in results],
                'result_count': len(results),
                'cached_at': datetime.utcnow().isoformat()
            }
            
            await self.redis_cache.set(search_key, json.dumps(results_data), ttl=ttl)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache search results: {e}")
            return False
    
    async def get_cached_search_results(self, query_hash: str) -> Optional[List[SimilarityMatch]]:
        """Get cached similarity search results"""
        
        search_key = f"{self.SEARCH_RESULTS_PREFIX}:{query_hash}"
        results_data = await self.redis_cache.get(search_key)
        
        if results_data:
            try:
                data = json.loads(results_data)
                matches = []
                
                for result_dict in data['results']:
                    # Reconstruct SimilarityMatch objects
                    result_dict['confidence_level'] = MatchConfidence(result_dict['confidence_level'])
                    result_dict['fingerprint_type'] = FingerprintType(result_dict['fingerprint_type'])
                    result_dict['matched_at'] = datetime.fromisoformat(result_dict['matched_at'])
                    
                    match = SimilarityMatch(**result_dict)
                    matches.append(match)
                
                return matches
                
            except Exception as e:
                logger.error(f"Failed to deserialize search results: {e}")
        
        return None
