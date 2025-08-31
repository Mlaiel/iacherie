"""Fingerprint Index Manager for IA-Influencer-Agent Platform

Specialized indexing system for content fingerprints with optimized
performance for similarity matching and duplicate detection.

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
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. 
Unauthorized use, modification, or distribution by any individual or entity 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""
import asyncio
import logging
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

from ..connections.postgresql_manager import PostgreSQLManager
from ..connections.redis_manager import RedisManager
from ..monitoring.performance_tracker import PerformanceTracker
from ..security.fingerprint_security import FingerprintSecurityManager

logger = logging.getLogger(__name__)

class FingerprintType:
    """Types of content fingerprints"""    AUDIO_CHROMAPRINT = "audio_chromaprint"
    AUDIO_SPECTRAL = "audio_spectral"
    AUDIO_MFCC = "audio_mfcc"
    VIDEO_PERCEPTUAL = "video_perceptual"
    VIDEO_TEMPORAL = "video_temporal"
    VIDEO_MOTION = "video_motion"
    IMAGE_PHASH = "image_phash"
    IMAGE_DHASH = "image_dhash"
    IMAGE_WHASH = "image_whash"
    TEXT_SHINGLE = "text_shingle"
    TEXT_SEMANTIC = "text_semantic"
    COMPOSITE_MIXED = "composite_mixed"

class FingerprintStatus:
    """Status of fingerprint processing"""    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PROTECTED = "protected"
    VIOLATION_DETECTED = "violation_detected"

class FingerprintIndexManager:
    """    Ultra-advanced fingerprint index manager for content protection
    
    Provides sophisticated content fingerprinting and protection:
    - Multi-format content fingerprint generation and indexing
    - Real-time duplicate detection and copyright protection
    - Advanced similarity matching with configurable thresholds
    - Cross-platform content monitoring and violation detection
    - High-performance fingerprint search and comparison
    - Automated legal compliance and takedown assistance
    """    
    def __init__(self):
        """Initialize fingerprint index manager with enterprise components"""        self.db_manager = PostgreSQLManager()
        self.redis_manager = RedisManager()
        self.performance_tracker = PerformanceTracker()
        self.security_manager = FingerprintSecurityManager()
        
        # Fingerprint storage configuration
        self.fingerprint_config = {
            'hash_algorithms': ['sha256', 'md5', 'blake2b'],
            'similarity_thresholds': {
                FingerprintType.AUDIO_CHROMAPRINT: 0.85,
                FingerprintType.AUDIO_SPECTRAL: 0.80,
                FingerprintType.AUDIO_MFCC: 0.75,
                FingerprintType.VIDEO_PERCEPTUAL: 0.90,
                FingerprintType.VIDEO_TEMPORAL: 0.85,
                FingerprintType.VIDEO_MOTION: 0.80,
                FingerprintType.IMAGE_PHASH: 0.95,
                FingerprintType.IMAGE_DHASH: 0.90,
                FingerprintType.IMAGE_WHASH: 0.92,
                FingerprintType.TEXT_SHINGLE: 0.70,
                FingerprintType.TEXT_SEMANTIC: 0.85,
                FingerprintType.COMPOSITE_MIXED: 0.80
            },
            'batch_size': 1000,
            'cache_ttl': 3600,  # 1 hour
            'violation_alert_threshold': 0.95
        }
        
        # Index optimization parameters
        self.index_optimization = {
            'parallel_workers': 8,
            'bloom_filter_size': 10000000,  # 10M elements
            'bloom_filter_error_rate': 0.001,
            'locality_sensitive_hashing': True,
            'segment_size': 64,  # LSH segment size
            'hash_tables': 20    # Number of LSH hash tables
        }
        
        logger.info("FingerprintIndexManager initialized with enterprise configuration")
    
    async def initialize(self) -> bool:
        """Initialize fingerprint index manager and create necessary schemas"""        try:
            # Initialize supporting services
            await self.db_manager.initialize()
            await self.redis_manager.initialize()
            await self.performance_tracker.initialize()
            await self.security_manager.initialize()
            
            # Create fingerprint database schema
            await self._create_fingerprint_schema()
            
            # Initialize fingerprint indexes
            await self._create_fingerprint_indexes()
            
            # Setup monitoring and alerts
            await self._setup_fingerprint_monitoring()
            
            # Initialize bloom filters and LSH
            await self._initialize_optimization_structures()
            
            logger.info("FingerprintIndexManager initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"FingerprintIndexManager initialization failed: {str(e)}")
            return False
    
    async def _create_fingerprint_schema(self) -> bool:
        """Create database schema for fingerprint storage"""        try:
            schema_sql = """            -- Content fingerprints table
            CREATE TABLE IF NOT EXISTS content_fingerprints (
                id BIGSERIAL PRIMARY KEY,
                content_id VARCHAR(255) NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                fingerprint_type VARCHAR(100) NOT NULL,
                fingerprint_hash VARCHAR(512) NOT NULL,
                fingerprint_data JSONB NOT NULL,
                similarity_threshold FLOAT DEFAULT 0.8,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                protected_at TIMESTAMP WITH TIME ZONE,
                violation_count INTEGER DEFAULT 0
            );
            
            -- Fingerprint similarity matches table
            CREATE TABLE IF NOT EXISTS fingerprint_matches (
                id BIGSERIAL PRIMARY KEY,
                source_fingerprint_id BIGINT REFERENCES content_fingerprints(id),
                target_fingerprint_id BIGINT REFERENCES content_fingerprints(id),
                similarity_score FLOAT NOT NULL,
                match_type VARCHAR(100) NOT NULL,
                detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                verified BOOLEAN DEFAULT FALSE,
                action_taken VARCHAR(100),
                notes TEXT
            );
            
            -- Copyright violations table
            CREATE TABLE IF NOT EXISTS copyright_violations (
                id BIGSERIAL PRIMARY KEY,
                original_content_id VARCHAR(255) NOT NULL,
                violating_content_id VARCHAR(255) NOT NULL,
                similarity_score FLOAT NOT NULL,
                violation_type VARCHAR(100) NOT NULL,
                platform VARCHAR(100),
                detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                status VARCHAR(50) DEFAULT 'detected',
                legal_action VARCHAR(100),
                resolved_at TIMESTAMP WITH TIME ZONE,
                evidence_data JSONB
            );
            
            -- Fingerprint processing queue
            CREATE TABLE IF NOT EXISTS fingerprint_queue (
                id BIGSERIAL PRIMARY KEY,
                content_id VARCHAR(255) NOT NULL,
                content_type VARCHAR(100) NOT NULL,
                priority INTEGER DEFAULT 5,
                processing_attempts INTEGER DEFAULT 0,
                status VARCHAR(50) DEFAULT 'queued',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                scheduled_at TIMESTAMP WITH TIME ZONE,
                processed_at TIMESTAMP WITH TIME ZONE,
                error_message TEXT
            );
            """            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(schema_sql)
            
            logger.info("Fingerprint database schema created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Fingerprint schema creation failed: {str(e)}")
            return False
    
    async def _create_fingerprint_indexes(self) -> bool:
        """Create optimized indexes for fingerprint operations"""        try:
            index_sql = """            -- Primary fingerprint lookup indexes
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_content_id 
                ON content_fingerprints(content_id);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_user_id 
                ON content_fingerprints(user_id);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_type 
                ON content_fingerprints(fingerprint_type);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_hash 
                ON content_fingerprints USING hash(fingerprint_hash);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_status 
                ON content_fingerprints(status);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_created 
                ON content_fingerprints(created_at);
            
            -- Composite indexes for common queries
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_type_status 
                ON content_fingerprints(fingerprint_type, status);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_user_type 
                ON content_fingerprints(user_id, fingerprint_type);
            
            -- JSONB indexes for fingerprint data
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_data_gin 
                ON content_fingerprints USING gin(fingerprint_data);
            
            -- Similarity threshold index for range queries
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_threshold 
                ON content_fingerprints(similarity_threshold);
            
            -- Match indexes
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_matches_source 
                ON fingerprint_matches(source_fingerprint_id);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_matches_target 
                ON fingerprint_matches(target_fingerprint_id);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_matches_score 
                ON fingerprint_matches(similarity_score);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_matches_detected 
                ON fingerprint_matches(detected_at);
            
            -- Violation indexes
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_violations_original 
                ON copyright_violations(original_content_id);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_violations_violating 
                ON copyright_violations(violating_content_id);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_violations_platform 
                ON copyright_violations(platform);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_violations_status 
                ON copyright_violations(status);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_violations_detected 
                ON copyright_violations(detected_at);
            
            -- Queue indexes
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_queue_status 
                ON fingerprint_queue(status);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_queue_priority 
                ON fingerprint_queue(priority, created_at);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_queue_scheduled 
                ON fingerprint_queue(scheduled_at) WHERE scheduled_at IS NOT NULL;
            """            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(index_sql)
            
            logger.info("Fingerprint indexes created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Fingerprint index creation failed: {str(e)}")
            return False
    
    async def add_content_fingerprint(self, content_data: Dict[str, Any]) -> bool:
        """        Add content fingerprint to the protection system
        
        Args:
            content_data: Complete content fingerprint data
            
        Returns:
            bool: Success status of fingerprint addition
        """        try:
            # Validate security permissions
            if not await self.security_manager.validate_fingerprint_creation(content_data):
                logger.warning("Fingerprint creation denied by security manager")
                return False
            
            # Generate multiple fingerprint types for robust protection
            fingerprints = await self._generate_multi_type_fingerprints(content_data)
            
            # Store fingerprints in database
            success_count = 0
            for fingerprint in fingerprints:
                if await self._store_fingerprint(fingerprint):
                    success_count += 1
                    
                    # Cache fingerprint for fast lookup
                    await self._cache_fingerprint(fingerprint)
                    
                    # Add to bloom filter for duplicate detection
                    await self._add_to_bloom_filter(fingerprint['fingerprint_hash'])
            
            # Check for immediate matches
            await self._check_immediate_matches(content_data['content_id'])
            
            logger.info(f"Added {success_count}/{len(fingerprints)} fingerprints for content {content_data['content_id']}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Fingerprint addition failed: {str(e)}")
            return False
    
    async def _generate_multi_type_fingerprints(self, content_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate multiple fingerprint types for comprehensive protection"""        fingerprints = []
        content_type = content_data.get('content_type', 'unknown')
        
        try:
            base_fingerprint = {
                'content_id': content_data['content_id'],
                'user_id': content_data['user_id'],
                'status': FingerprintStatus.PENDING,
                'created_at': datetime.utcnow()
            }
            
            if content_type == 'audio':
                # Audio fingerprints
                if 'audio_features' in content_data:
                    audio_features = content_data['audio_features']
                    
                    # Chromaprint fingerprint
                    if 'chromaprint' in audio_features:
                        fingerprints.append({
                            **base_fingerprint,
                            'fingerprint_type': FingerprintType.AUDIO_CHROMAPRINT,
                            'fingerprint_hash': self._hash_data(audio_features['chromaprint']),
                            'fingerprint_data': {'chromaprint': audio_features['chromaprint']},
                            'similarity_threshold': self.fingerprint_config['similarity_thresholds'][FingerprintType.AUDIO_CHROMAPRINT]
                        })
                    
                    # Spectral fingerprint
                    if 'spectral_features' in audio_features:
                        fingerprints.append({
                            **base_fingerprint,
                            'fingerprint_type': FingerprintType.AUDIO_SPECTRAL,
                            'fingerprint_hash': self._hash_data(audio_features['spectral_features']),
                            'fingerprint_data': {'spectral_features': audio_features['spectral_features']},
                            'similarity_threshold': self.fingerprint_config['similarity_thresholds'][FingerprintType.AUDIO_SPECTRAL]
                        })
                    
                    # MFCC fingerprint
                    if 'mfcc' in audio_features:
                        fingerprints.append({
                            **base_fingerprint,
                            'fingerprint_type': FingerprintType.AUDIO_MFCC,
                            'fingerprint_hash': self._hash_data(audio_features['mfcc']),
                            'fingerprint_data': {'mfcc': audio_features['mfcc']},
                            'similarity_threshold': self.fingerprint_config['similarity_thresholds'][FingerprintType.AUDIO_MFCC]
                        })
            
            elif content_type == 'video':
                # Video fingerprints
                if 'video_features' in content_data:
                    video_features = content_data['video_features']
                    
                    # Perceptual hash
                    if 'perceptual_hash' in video_features:
                        fingerprints.append({
                            **base_fingerprint,
                            'fingerprint_type': FingerprintType.VIDEO_PERCEPTUAL,
                            'fingerprint_hash': self._hash_data(video_features['perceptual_hash']),
                            'fingerprint_data': {'perceptual_hash': video_features['perceptual_hash']},
                            'similarity_threshold': self.fingerprint_config['similarity_thresholds'][FingerprintType.VIDEO_PERCEPTUAL]
                        })
                    
                    # Temporal features
                    if 'temporal_features' in video_features:
                        fingerprints.append({
                            **base_fingerprint,
                            'fingerprint_type': FingerprintType.VIDEO_TEMPORAL,
                            'fingerprint_hash': self._hash_data(video_features['temporal_features']),
                            'fingerprint_data': {'temporal_features': video_features['temporal_features']},
                            'similarity_threshold': self.fingerprint_config['similarity_thresholds'][FingerprintType.VIDEO_TEMPORAL]
                        })
                    
                    # Motion vectors
                    if 'motion_vectors' in video_features:
                        fingerprints.append({
                            **base_fingerprint,
                            'fingerprint_type': FingerprintType.VIDEO_MOTION,
                            'fingerprint_hash': self._hash_data(video_features['motion_vectors']),
                            'fingerprint_data': {'motion_vectors': video_features['motion_vectors']},
                            'similarity_threshold': self.fingerprint_config['similarity_thresholds'][FingerprintType.VIDEO_MOTION]
                        })
            
            elif content_type == 'image':
                # Image fingerprints
                if 'image_features' in content_data:
                    image_features = content_data['image_features']
                    
                    # Perceptual hash (pHash)
                    if 'phash' in image_features:
                        fingerprints.append({
                            **base_fingerprint,
                            'fingerprint_type': FingerprintType.IMAGE_PHASH,
                            'fingerprint_hash': self._hash_data(image_features['phash']),
                            'fingerprint_data': {'phash': image_features['phash']},
                            'similarity_threshold': self.fingerprint_config['similarity_thresholds'][FingerprintType.IMAGE_PHASH]
                        })
                    
                    # Difference hash (dHash)
                    if 'dhash' in image_features:
                        fingerprints.append({
                            **base_fingerprint,
                            'fingerprint_type': FingerprintType.IMAGE_DHASH,
                            'fingerprint_hash': self._hash_data(image_features['dhash']),
                            'fingerprint_data': {'dhash': image_features['dhash']},
                            'similarity_threshold': self.fingerprint_config['similarity_thresholds'][FingerprintType.IMAGE_DHASH]
                        })
                    
                    # Wavelet hash (wHash)
                    if 'whash' in image_features:
                        fingerprints.append({
                            **base_fingerprint,
                            'fingerprint_type': FingerprintType.IMAGE_WHASH,
                            'fingerprint_hash': self._hash_data(image_features['whash']),
                            'fingerprint_data': {'whash': image_features['whash']},
                            'similarity_threshold': self.fingerprint_config['similarity_thresholds'][FingerprintType.IMAGE_WHASH]
                        })
            
            elif content_type == 'text':
                # Text fingerprints
                if 'text_features' in content_data:
                    text_features = content_data['text_features']
                    
                    # Shingle fingerprint
                    if 'shingles' in text_features:
                        fingerprints.append({
                            **base_fingerprint,
                            'fingerprint_type': FingerprintType.TEXT_SHINGLE,
                            'fingerprint_hash': self._hash_data(text_features['shingles']),
                            'fingerprint_data': {'shingles': text_features['shingles']},
                            'similarity_threshold': self.fingerprint_config['similarity_thresholds'][FingerprintType.TEXT_SHINGLE]
                        })
                    
                    # Semantic fingerprint
                    if 'semantic_embedding' in text_features:
                        fingerprints.append({
                            **base_fingerprint,
                            'fingerprint_type': FingerprintType.TEXT_SEMANTIC,
                            'fingerprint_hash': self._hash_data(text_features['semantic_embedding']),
                            'fingerprint_data': {'semantic_embedding': text_features['semantic_embedding']},
                            'similarity_threshold': self.fingerprint_config['similarity_thresholds'][FingerprintType.TEXT_SEMANTIC]
                        })
            
            # Composite fingerprint for multi-modal content
            if len(fingerprints) > 1:
                composite_data = {fp['fingerprint_type']: fp['fingerprint_hash'] for fp in fingerprints}
                fingerprints.append({
                    **base_fingerprint,
                    'fingerprint_type': FingerprintType.COMPOSITE_MIXED,
                    'fingerprint_hash': self._hash_data(composite_data),
                    'fingerprint_data': {'composite': composite_data},
                    'similarity_threshold': self.fingerprint_config['similarity_thresholds'][FingerprintType.COMPOSITE_MIXED]
                })
            
            return fingerprints
            
        except Exception as e:
            logger.error(f"Fingerprint generation failed: {str(e)}")
            return []
    
    def _hash_data(self, data: Any) -> str:
        """Generate cryptographic hash of fingerprint data"""        try:
            # Convert data to JSON string for consistent hashing
            json_str = json.dumps(data, sort_keys=True, default=str)
            
            # Generate SHA-256 hash
            hash_obj = hashlib.sha256(json_str.encode('utf-8'))
            return hash_obj.hexdigest()
            
        except Exception as e:
            logger.error(f"Data hashing failed: {str(e)}")
            return ""
    
    async def _store_fingerprint(self, fingerprint: Dict[str, Any]) -> bool:
        """Store fingerprint in database"""        try:
            sql = """            INSERT INTO content_fingerprints (
                content_id, user_id, fingerprint_type, fingerprint_hash,
                fingerprint_data, similarity_threshold, status, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
            """            
            async with self.db_manager.get_connection() as conn:
                result = await conn.fetchrow(
                    sql,
                    fingerprint['content_id'],
                    fingerprint['user_id'],
                    fingerprint['fingerprint_type'],
                    fingerprint['fingerprint_hash'],
                    json.dumps(fingerprint['fingerprint_data']),
                    fingerprint['similarity_threshold'],
                    fingerprint['status'],
                    fingerprint['created_at']
                )
                
                if result:
                    fingerprint['id'] = result['id']
                    return True
                
            return False
            
        except Exception as e:
            logger.error(f"Fingerprint storage failed: {str(e)}")
            return False
    
    async def _cache_fingerprint(self, fingerprint: Dict[str, Any]) -> bool:
        """Cache fingerprint for fast lookup"""        try:
            redis_client = await self.redis_manager.get_client()
            
            cache_key = f"fingerprint:{fingerprint['fingerprint_hash']}"
            cache_data = {
                'id': fingerprint.get('id'),
                'content_id': fingerprint['content_id'],
                'fingerprint_type': fingerprint['fingerprint_type'],
                'similarity_threshold': fingerprint['similarity_threshold']
            }
            
            await redis_client.hset(cache_key, mapping={
                k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                for k, v in cache_data.items()
            })
            await redis_client.expire(cache_key, self.fingerprint_config['cache_ttl'])
            
            return True
            
        except Exception as e:
            logger.error(f"Fingerprint caching failed: {str(e)}")
            return False
    
    async def _add_to_bloom_filter(self, fingerprint_hash: str) -> bool:
        """Add fingerprint hash to bloom filter for duplicate detection"""        try:
            # This would integrate with a proper bloom filter implementation
            # For now, we'll use Redis sets as a simplified approach
            redis_client = await self.redis_manager.get_client()
            
            bloom_key = "fingerprint_bloom_filter"
            await redis_client.sadd(bloom_key, fingerprint_hash)
            
            return True
            
        except Exception as e:
            logger.error(f"Bloom filter addition failed: {str(e)}")
            return False
    
    async def _check_immediate_matches(self, content_id: str) -> List[Dict[str, Any]]:
        """Check for immediate fingerprint matches"""        try:
            matches = []
            
            # Get all fingerprints for the content
            sql = """            SELECT id, fingerprint_type, fingerprint_hash, fingerprint_data, similarity_threshold
            FROM content_fingerprints
            WHERE content_id = $1 AND status = 'completed'
            """            
            async with self.db_manager.get_connection() as conn:
                fingerprints = await conn.fetch(sql, content_id)
                
                for fingerprint in fingerprints:
                    # Find similar fingerprints
                    similar = await self._find_similar_fingerprints(
                        fingerprint['fingerprint_hash'],
                        fingerprint['fingerprint_type'],
                        fingerprint['similarity_threshold']
                    )
                    
                    for similar_fp in similar:
                        match = await self._create_fingerprint_match(
                            fingerprint['id'],
                            similar_fp['id'],
                            similar_fp['similarity_score'],
                            'automatic'
                        )
                        if match:
                            matches.append(match)
            
            if matches:
                logger.info(f"Found {len(matches)} immediate matches for content {content_id}")
            
            return matches
            
        except Exception as e:
            logger.error(f"Immediate match checking failed: {str(e)}")
            return []
    
    async def _find_similar_fingerprints(self, fingerprint_hash: str, 
                                       fingerprint_type: str, 
                                       threshold: float) -> List[Dict[str, Any]]:
        """Find fingerprints similar to the given hash"""        try:
            # For exact hash matches
            sql = """            SELECT id, content_id, fingerprint_hash, fingerprint_data,
                   1.0 as similarity_score
            FROM content_fingerprints
            WHERE fingerprint_type = $1 
            AND fingerprint_hash = $2
            AND status = 'completed'
            """            
            async with self.db_manager.get_connection() as conn:
                exact_matches = await conn.fetch(sql, fingerprint_type, fingerprint_hash)
            
            similar_fingerprints = []
            
            # Add exact matches
            for match in exact_matches:
                similar_fingerprints.append({
                    'id': match['id'],
                    'content_id': match['content_id'],
                    'fingerprint_hash': match['fingerprint_hash'],
                    'similarity_score': 1.0
                })
            
            # For fuzzy matching, we would implement LSH or other similarity algorithms
            # This is a simplified version focusing on exact matches
            
            return similar_fingerprints
            
        except Exception as e:
            logger.error(f"Similar fingerprint search failed: {str(e)}")
            return []
    
    async def _create_fingerprint_match(self, source_id: int, target_id: int,
                                      similarity_score: float, match_type: str) -> Optional[Dict[str, Any]]:
        """Create a fingerprint match record"""        try:
            sql = """            INSERT INTO fingerprint_matches (
                source_fingerprint_id, target_fingerprint_id, 
                similarity_score, match_type, detected_at
            ) VALUES ($1, $2, $3, $4, $5)
            RETURNING id
            """            
            async with self.db_manager.get_connection() as conn:
                result = await conn.fetchrow(
                    sql, source_id, target_id, similarity_score, match_type, datetime.utcnow()
                )
                
                if result:
                    match = {
                        'id': result['id'],
                        'source_fingerprint_id': source_id,
                        'target_fingerprint_id': target_id,
                        'similarity_score': similarity_score,
                        'match_type': match_type
                    }
                    
                    # Check if this is a violation
                    if similarity_score >= self.fingerprint_config['violation_alert_threshold']:
                        await self._create_violation_alert(match)
                    
                    return match
            
            return None
            
        except Exception as e:
            logger.error(f"Fingerprint match creation failed: {str(e)}")
            return None
    
    async def _create_violation_alert(self, match: Dict[str, Any]) -> bool:
        """Create a copyright violation alert"""        try:
            # Get content information for both fingerprints
            sql = """            SELECT cf1.content_id as original_content_id, cf1.user_id as original_user_id,
                   cf2.content_id as violating_content_id, cf2.user_id as violating_user_id
            FROM content_fingerprints cf1
            JOIN content_fingerprints cf2 ON cf2.id = $2
            WHERE cf1.id = $1
            """            
            async with self.db_manager.get_connection() as conn:
                content_info = await conn.fetchrow(
                    sql, match['source_fingerprint_id'], match['target_fingerprint_id']
                )
                
                if content_info and content_info['original_user_id'] != content_info['violating_user_id']:
                    # Create violation record
                    violation_sql = """                    INSERT INTO copyright_violations (
                        original_content_id, violating_content_id, similarity_score,
                        violation_type, detected_at, evidence_data
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                    """                    
                    evidence = {
                        'match_id': match['id'],
                        'similarity_score': match['similarity_score'],
                        'detection_method': match['match_type']
                    }
                    
                    await conn.execute(
                        violation_sql,
                        content_info['original_content_id'],
                        content_info['violating_content_id'],
                        match['similarity_score'],
                        'fingerprint_match',
                        datetime.utcnow(),
                        json.dumps(evidence)
                    )
                    
                    logger.warning(f"Copyright violation detected: {content_info['violating_content_id']} vs {content_info['original_content_id']}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Violation alert creation failed: {str(e)}")
            return False
    
    async def search_content_matches(self, query_data: Dict[str, Any],
                                   similarity_threshold: float = 0.8,
                                   max_results: int = 100) -> List[Dict[str, Any]]:
        """        Search for content matches using fingerprint similarity
        
        Args:
            query_data: Query content fingerprint data
            similarity_threshold: Minimum similarity score
            max_results: Maximum number of results
            
        Returns:
            List of matching content with similarity scores
        """        try:
            matches = []
            
            # Generate fingerprints for query
            query_fingerprints = await self._generate_multi_type_fingerprints(query_data)
            
            for query_fp in query_fingerprints:
                # Search for similar fingerprints
                similar_fps = await self._find_similar_fingerprints(
                    query_fp['fingerprint_hash'],
                    query_fp['fingerprint_type'],
                    similarity_threshold
                )
                
                # Convert to match format
                for similar_fp in similar_fps:
                    if similar_fp['similarity_score'] >= similarity_threshold:
                        matches.append({
                            'content_id': similar_fp['content_id'],
                            'fingerprint_type': query_fp['fingerprint_type'],
                            'similarity_score': similar_fp['similarity_score'],
                            'fingerprint_hash': similar_fp['fingerprint_hash']
                        })
            
            # Remove duplicates and sort by similarity
            unique_matches = {}
            for match in matches:
                key = f"{match['content_id']}_{match['fingerprint_type']}"
                if key not in unique_matches or match['similarity_score'] > unique_matches[key]['similarity_score']:
                    unique_matches[key] = match
            
            # Sort by similarity score
            sorted_matches = sorted(
                unique_matches.values(),
                key=lambda x: x['similarity_score'],
                reverse=True
            )
            
            return sorted_matches[:max_results]
            
        except Exception as e:
            logger.error(f"Content match search failed: {str(e)}")
            return []
    
    async def _setup_fingerprint_monitoring(self) -> bool:
        """Setup monitoring for fingerprint operations"""        try:
            # Create monitoring functions and views
            monitoring_sql = """            -- Fingerprint statistics view
            CREATE OR REPLACE VIEW fingerprint_statistics AS
            SELECT 
                fingerprint_type,
                COUNT(*) as total_fingerprints,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                AVG(similarity_threshold) as avg_threshold,
                MAX(created_at) as latest_fingerprint
            FROM content_fingerprints
            GROUP BY fingerprint_type;
            
            -- Violation statistics view
            CREATE OR REPLACE VIEW violation_statistics AS
            SELECT 
                violation_type,
                COUNT(*) as total_violations,
                COUNT(CASE WHEN status = 'detected' THEN 1 END) as unresolved,
                AVG(similarity_score) as avg_similarity,
                DATE_TRUNC('day', detected_at) as detection_date
            FROM copyright_violations
            GROUP BY violation_type, DATE_TRUNC('day', detected_at)
            ORDER BY detection_date DESC;
            
            -- Performance monitoring function
            CREATE OR REPLACE FUNCTION get_fingerprint_performance()
            RETURNS TABLE(
                fingerprint_type text,
                avg_processing_time interval,
                match_accuracy float,
                violation_rate float
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT 
                    cf.fingerprint_type::text,
                    AVG(cf.updated_at - cf.created_at) as avg_processing_time,
                    COUNT(fm.id)::float / COUNT(cf.id) as match_accuracy,
                    COUNT(cv.id)::float / COUNT(cf.id) as violation_rate
                FROM content_fingerprints cf
                LEFT JOIN fingerprint_matches fm ON cf.id = fm.source_fingerprint_id
                LEFT JOIN copyright_violations cv ON cf.content_id = cv.original_content_id
                WHERE cf.created_at >= NOW() - INTERVAL '30 days'
                GROUP BY cf.fingerprint_type;
            END;
            $$ LANGUAGE plpgsql;
            """            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(monitoring_sql)
            
            logger.info("Fingerprint monitoring setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Fingerprint monitoring setup failed: {str(e)}")
            return False
    
    async def _initialize_optimization_structures(self) -> bool:
        """Initialize bloom filters and LSH structures"""        try:
            # Initialize bloom filter in Redis
            redis_client = await self.redis_manager.get_client()
            
            # Create bloom filter key if it doesn't exist
            bloom_key = "fingerprint_bloom_filter"
            if not await redis_client.exists(bloom_key):
                await redis_client.sadd(bloom_key, "initialization_key")
                await redis_client.srem(bloom_key, "initialization_key")
            
            # Initialize LSH structures if enabled
            if self.index_optimization['locality_sensitive_hashing']:
                await self._initialize_lsh_structures()
            
            logger.info("Optimization structures initialized")
            return True
            
        except Exception as e:
            logger.error(f"Optimization structure initialization failed: {str(e)}")
            return False
    
    async def _initialize_lsh_structures(self) -> bool:
        """Initialize Locality Sensitive Hashing structures"""        try:
            # This would implement proper LSH initialization
            # For now, we'll create the basic structure in Redis
            redis_client = await self.redis_manager.get_client()
            
            num_tables = self.index_optimization['hash_tables']
            for i in range(num_tables):
                lsh_key = f"lsh_table:{i}"
                if not await redis_client.exists(lsh_key):
                    await redis_client.hset(lsh_key, "initialized", "true")
            
            logger.info(f"LSH structures initialized with {num_tables} hash tables")
            return True
            
        except Exception as e:
            logger.error(f"LSH initialization failed: {str(e)}")
            return False
    
    async def get_fingerprint_statistics(self) -> Dict[str, Any]:
        """Get comprehensive fingerprint system statistics"""        try:
            statistics = {
                'fingerprint_counts': {},
                'violation_statistics': {},
                'performance_metrics': {},
                'system_health': 'healthy'
            }
            
            async with self.db_manager.get_connection() as conn:
                # Get fingerprint statistics
                fp_stats = await conn.fetch("SELECT * FROM fingerprint_statistics")
                for stat in fp_stats:
                    statistics['fingerprint_counts'][stat['fingerprint_type']] = dict(stat)
                
                # Get violation statistics
                violation_stats = await conn.fetch(
                    "SELECT * FROM violation_statistics WHERE detection_date >= NOW() - INTERVAL '30 days'"
                )
                for stat in violation_stats:
                    date_key = stat['detection_date'].strftime('%Y-%m-%d')
                    if date_key not in statistics['violation_statistics']:
                        statistics['violation_statistics'][date_key] = {}
                    statistics['violation_statistics'][date_key][stat['violation_type']] = dict(stat)
                
                # Get performance metrics
                perf_metrics = await conn.fetch("SELECT * FROM get_fingerprint_performance()")
                for metric in perf_metrics:
                    statistics['performance_metrics'][metric['fingerprint_type']] = dict(metric)
            
            # Calculate system health
            total_violations = sum(
                day_stats.get('total_violations', 0)
                for day_stats in statistics['violation_statistics'].values()
                for violation_type, day_stats in day_stats.items()
            )
            
            if total_violations > 100:  # Threshold for concern
                statistics['system_health'] = 'needs_attention'
            elif total_violations > 500:
                statistics['system_health'] = 'critical'
            
            return statistics
            
        except Exception as e:
            logger.error(f"Statistics collection failed: {str(e)}")
            return {'error': str(e)}
    
    async def cleanup(self):
        """Cleanup fingerprint manager resources"""        try:
            await self.db_manager.cleanup()
            await self.redis_manager.cleanup()
            await self.performance_tracker.cleanup()
            await self.security_manager.cleanup()
            
            logger.info("FingerprintIndexManager cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"FingerprintIndexManager cleanup failed: {str(e)}")
    IMAGE_DHASH = "image_dhash"
    IMAGE_AHASH = "image_ahash"
    IMAGE_WAVELET = "image_wavelet"
    TEXT_MINHASH = "text_minhash"
    TEXT_SIMHASH = "text_simhash"
    COMPOSITE_MULTI = "composite_multi"

class FingerprintStatus:
    """Status of fingerprint processing"""    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

class FingerprintIndexManager:
    """    Advanced fingerprint index manager for IA-Influencer platform
    
    Provides high-performance indexing and matching for content fingerprints:
    - Multi-modal fingerprint storage and retrieval
    - Fast similarity matching algorithms
    - Duplicate detection and clustering
    - Performance-optimized indexing strategies
    - Real-time fingerprint processing
    """    
    def __init__(self):
        """Initialize fingerprint index manager"""        self.db_manager = PostgreSQLManager()
        self.redis_manager = RedisManager()
        self.performance_tracker = PerformanceTracker()
        self.security_manager = FingerprintSecurityManager()
        
        # Index configurations for different fingerprint types
        self.fingerprint_configs = {
            FingerprintType.AUDIO_CHROMAPRINT: {
                'hash_length': 64,
                'similarity_threshold': 0.85,
                'index_type': 'btree',
                'clustering_enabled': True,
                'expiry_days': 365
            },
            FingerprintType.AUDIO_SPECTRAL: {
                'hash_length': 128,
                'similarity_threshold': 0.80,
                'index_type': 'gin',
                'clustering_enabled': True,
                'expiry_days': 365
            },
            FingerprintType.VIDEO_PERCEPTUAL: {
                'hash_length': 96,
                'similarity_threshold': 0.82,
                'index_type': 'gist',
                'clustering_enabled': True,
                'expiry_days': 180
            },
            FingerprintType.VIDEO_TEMPORAL: {
                'hash_length': 72,
                'similarity_threshold': 0.78,
                'index_type': 'btree',
                'clustering_enabled': False,
                'expiry_days': 180
            },
            FingerprintType.IMAGE_PHASH: {
                'hash_length': 64,
                'similarity_threshold': 0.90,
                'index_type': 'hash',
                'clustering_enabled': True,
                'expiry_days': 270
            },
            FingerprintType.IMAGE_DHASH: {
                'hash_length': 64,
                'similarity_threshold': 0.88,
                'index_type': 'hash',
                'clustering_enabled': True,
                'expiry_days': 270
            },
            FingerprintType.IMAGE_AHASH: {
                'hash_length': 64,
                'similarity_threshold': 0.85,
                'index_type': 'hash',
                'clustering_enabled': True,
                'expiry_days': 270
            },
            FingerprintType.IMAGE_WAVELET: {
                'hash_length': 96,
                'similarity_threshold': 0.83,
                'index_type': 'gin',
                'clustering_enabled': True,
                'expiry_days': 270
            },
            FingerprintType.TEXT_MINHASH: {
                'hash_length': 128,
                'similarity_threshold': 0.75,
                'index_type': 'gin',
                'clustering_enabled': True,
                'expiry_days': 90
            },
            FingerprintType.TEXT_SIMHASH: {
                'hash_length': 64,
                'similarity_threshold': 0.80,
                'index_type': 'btree',
                'clustering_enabled': True,
                'expiry_days': 90
            },
            FingerprintType.COMPOSITE_MULTI: {
                'hash_length': 256,
                'similarity_threshold': 0.70,
                'index_type': 'gin',
                'clustering_enabled': True,
                'expiry_days': 365
            }
        }
        
        # Performance settings
        self.batch_size = 1000
        self.cache_size = 50000
        self.similarity_cache_ttl = 3600  # 1 hour
        self.cleanup_interval = 86400  # 24 hours
        
        # Runtime statistics
        self.index_stats = defaultdict(lambda: {
            'total_fingerprints': 0,
            'matches_found': 0,
            'false_positives': 0,
            'average_similarity': 0.0,
            'last_updated': datetime.now()
        })
        
        logger.info("FingerprintIndexManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize fingerprint index manager"""        try:
            # Initialize database connections
            if not await self.db_manager.initialize():
                raise Exception("Failed to initialize PostgreSQL manager")
                
            if not await self.redis_manager.initialize():
                raise Exception("Failed to initialize Redis manager")
            
            # Initialize tracking and security
            await self.performance_tracker.initialize()
            await self.security_manager.initialize()
            
            # Setup database schema
            await self._setup_fingerprint_schema()
            
            # Create optimized indexes
            await self._create_fingerprint_indexes()
            
            # Load existing statistics
            await self._load_fingerprint_statistics()
            
            # Setup cleanup scheduling
            await self._setup_cleanup_schedule()
            
            logger.info("FingerprintIndexManager initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize FingerprintIndexManager: {str(e)}")
            return False
    
    async def _setup_fingerprint_schema(self):
        """Setup database schema for fingerprint storage"""        conn = await self.db_manager.get_connection()
        try:
            # Main fingerprints table
            await conn.execute("""                CREATE TABLE IF NOT EXISTS content_fingerprints (
                    fingerprint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    content_id VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    tenant_id VARCHAR(255) NOT NULL,
                    fingerprint_type VARCHAR(50) NOT NULL,
                    fingerprint_hash VARCHAR(512) NOT NULL,
                    fingerprint_data BYTEA,
                    quality_score FLOAT DEFAULT 0.0,
                    extraction_params JSONB DEFAULT '{}',
                    metadata JSONB DEFAULT '{}',
                    status VARCHAR(20) DEFAULT 'pending',
                    similarity_cluster_id UUID,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    expires_at TIMESTAMP WITH TIME ZONE
                );
            """)
            
            # Similarity matches table
            await conn.execute("""                CREATE TABLE IF NOT EXISTS fingerprint_similarity_matches (
                    match_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    query_fingerprint_id UUID REFERENCES content_fingerprints(fingerprint_id),
                    matched_fingerprint_id UUID REFERENCES content_fingerprints(fingerprint_id),
                    similarity_score FLOAT NOT NULL CHECK (similarity_score >= 0 AND similarity_score <= 1),
                    similarity_type VARCHAR(50) NOT NULL,
                    confidence_level FLOAT NOT NULL CHECK (confidence_level >= 0 AND confidence_level <= 1),
                    match_details JSONB DEFAULT '{}',
                    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    CONSTRAINT no_self_match CHECK (query_fingerprint_id != matched_fingerprint_id)
                );
            """)
            
            # Fingerprint clusters table
            await conn.execute("""                CREATE TABLE IF NOT EXISTS fingerprint_clusters (
                    cluster_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    fingerprint_type VARCHAR(50) NOT NULL,
                    cluster_centroid BYTEA,
                    cluster_size INTEGER DEFAULT 1,
                    average_similarity FLOAT DEFAULT 0.0,
                    quality_threshold FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            # Statistics table
            await conn.execute("""                CREATE TABLE IF NOT EXISTS fingerprint_statistics (
                    stat_id SERIAL PRIMARY KEY,
                    fingerprint_type VARCHAR(50) NOT NULL,
                    total_count INTEGER DEFAULT 0,
                    matches_count INTEGER DEFAULT 0,
                    false_positives INTEGER DEFAULT 0,
                    average_similarity FLOAT DEFAULT 0.0,
                    performance_metrics JSONB DEFAULT '{}',
                    date_collected DATE DEFAULT CURRENT_DATE,
                    UNIQUE(fingerprint_type, date_collected)
                );
            """)
            
            logger.info("Fingerprint database schema setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup fingerprint schema: {str(e)}")
            raise
        finally:
            await self.db_manager.return_connection(conn)
    
    async def _create_fingerprint_indexes(self):
        """Create optimized database indexes for fingerprint operations"""        conn = await self.db_manager.get_connection()
        try:
            # Performance indexes for content_fingerprints
            indexes = [
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_hash ON content_fingerprints USING HASH (fingerprint_hash);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_type_user ON content_fingerprints (fingerprint_type, user_id);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_content_id ON content_fingerprints (content_id);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_tenant ON content_fingerprints (tenant_id, fingerprint_type);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_status ON content_fingerprints (status, created_at DESC);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_cluster ON content_fingerprints (similarity_cluster_id);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_quality ON content_fingerprints (quality_score DESC, fingerprint_type);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_expires ON content_fingerprints (expires_at) WHERE expires_at IS NOT NULL;",
                
                # GIN indexes for JSONB fields
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_metadata_gin ON content_fingerprints USING GIN (metadata);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fingerprints_params_gin ON content_fingerprints USING GIN (extraction_params);",
                
                # Similarity matches indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_matches_query_fp ON fingerprint_similarity_matches (query_fingerprint_id);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_matches_matched_fp ON fingerprint_similarity_matches (matched_fingerprint_id);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_matches_similarity ON fingerprint_similarity_matches (similarity_score DESC);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_matches_type_score ON fingerprint_similarity_matches (similarity_type, similarity_score DESC);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_matches_detected ON fingerprint_similarity_matches (detected_at DESC);",
                
                # Cluster indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_clusters_type ON fingerprint_clusters (fingerprint_type);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_clusters_size ON fingerprint_clusters (cluster_size DESC);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_clusters_quality ON fingerprint_clusters (quality_threshold DESC);",
                
                # Statistics indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stats_type_date ON fingerprint_statistics (fingerprint_type, date_collected DESC);"
            ]
            
            for index_sql in indexes:
                try:
                    await conn.execute(index_sql)
                except Exception as e:
                    # Index might already exist
                    logger.debug(f"Index creation note: {str(e)}")
            
            logger.info("Fingerprint indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create fingerprint indexes: {str(e)}")
            raise
        finally:
            await self.db_manager.return_connection(conn)
    
    async def add_fingerprint(self, content_id: str, user_id: str, tenant_id: str,
                            fingerprint_type: str, fingerprint_hash: str,
                            fingerprint_data: Optional[bytes] = None,
                            quality_score: float = 0.0,
                            metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Add a new content fingerprint to the index"""        try:
            # Validate fingerprint type
            if fingerprint_type not in self.fingerprint_configs:
                raise ValueError(f"Unsupported fingerprint type: {fingerprint_type}")
            
            # Validate security permissions
            if not await self.security_manager.validate_fingerprint_creation(
                user_id, tenant_id, fingerprint_type
            ):
                raise Exception("Fingerprint creation not authorized")
            
            config = self.fingerprint_configs[fingerprint_type]
            
            # Calculate expiry date
            expires_at = datetime.now() + timedelta(days=config['expiry_days'])
            
            conn = await self.db_manager.get_connection()
            start_time = datetime.now()
            
            try:
                # Insert fingerprint
                fingerprint_id = await conn.fetchval("""                    INSERT INTO content_fingerprints 
                    (content_id, user_id, tenant_id, fingerprint_type, fingerprint_hash,
                     fingerprint_data, quality_score, metadata, status, expires_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    RETURNING fingerprint_id
                """, content_id, user_id, tenant_id, fingerprint_type, fingerprint_hash,
                    fingerprint_data, quality_score, json.dumps(metadata or {}),
                    FingerprintStatus.COMPLETED, expires_at)
                
                add_time = (datetime.now() - start_time).total_seconds()
                
                # Update statistics
                self.index_stats[fingerprint_type]['total_fingerprints'] += 1
                self.index_stats[fingerprint_type]['last_updated'] = datetime.now()
                
                # Cache fingerprint for fast lookup
                await self._cache_fingerprint(str(fingerprint_id), {
                    'content_id': content_id,
                    'fingerprint_type': fingerprint_type,
                    'fingerprint_hash': fingerprint_hash,
                    'quality_score': quality_score
                })
                
                # Check for clustering if enabled
                if config.get('clustering_enabled', False):
                    asyncio.create_task(
                        self._process_fingerprint_clustering(str(fingerprint_id), fingerprint_type)
                    )
                
                # Log performance
                await self.performance_tracker.log_index_operation(
                    f"fingerprint_{fingerprint_type}", 'add', add_time,
                    {'quality_score': quality_score, 'hash_length': len(fingerprint_hash)}
                )
                
                logger.info(f"Fingerprint {fingerprint_id} added for content {content_id} in {add_time:.3f}s")
                return str(fingerprint_id)
                
            except Exception as e:
                logger.error(f"Failed to add fingerprint: {str(e)}")
                return None
            finally:
                await self.db_manager.return_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to add fingerprint for content {content_id}: {str(e)}")
            return None
    
    async def find_similar_fingerprints(self, fingerprint_hash: str, fingerprint_type: str,
                                      similarity_threshold: Optional[float] = None,
                                      max_results: int = 100) -> List[Dict[str, Any]]:
        """Find similar fingerprints using optimized matching algorithms"""        try:
            config = self.fingerprint_configs.get(fingerprint_type)
            if not config:
                raise ValueError(f"Unsupported fingerprint type: {fingerprint_type}")
            
            threshold = similarity_threshold or config['similarity_threshold']
            
            start_time = datetime.now()
            
            # Try cache first for recent queries
            cache_key = f"similar_fp:{fingerprint_type}:{hashlib.md5(fingerprint_hash.encode()).hexdigest()}"
            cached_results = await self._get_cached_similarity_results(cache_key)
            
            if cached_results:
                logger.debug(f"Similarity search cache hit for {fingerprint_type}")
                return cached_results
            
            # Perform database search based on fingerprint type
            if fingerprint_type in [FingerprintType.AUDIO_CHROMAPRINT, FingerprintType.AUDIO_SPECTRAL]:
                results = await self._find_similar_audio_fingerprints(
                    fingerprint_hash, fingerprint_type, threshold, max_results
                )
            elif fingerprint_type.startswith('image_'):
                results = await self._find_similar_image_fingerprints(
                    fingerprint_hash, fingerprint_type, threshold, max_results
                )
            elif fingerprint_type.startswith('video_'):
                results = await self._find_similar_video_fingerprints(
                    fingerprint_hash, fingerprint_type, threshold, max_results
                )
            elif fingerprint_type.startswith('text_'):
                results = await self._find_similar_text_fingerprints(
                    fingerprint_hash, fingerprint_type, threshold, max_results
                )
            else:
                results = await self._find_similar_generic_fingerprints(
                    fingerprint_hash, fingerprint_type, threshold, max_results
                )
            
            search_time = (datetime.now() - start_time).total_seconds()
            
            # Cache results for future queries
            await self._cache_similarity_results(cache_key, results)
            
            # Update statistics
            self.index_stats[fingerprint_type]['matches_found'] += len(results)
            if results:
                avg_similarity = sum(r['similarity_score'] for r in results) / len(results)
                self.index_stats[fingerprint_type]['average_similarity'] = (
                    self.index_stats[fingerprint_type]['average_similarity'] * 0.9 + avg_similarity * 0.1
                )
            
            # Log performance
            await self.performance_tracker.log_index_operation(
                f"fingerprint_{fingerprint_type}", 'search', search_time,
                {'results_count': len(results), 'threshold': threshold}
            )
            
            logger.debug(f"Found {len(results)} similar fingerprints for {fingerprint_type} in {search_time:.3f}s")
            return results
            
        except Exception as e:
            logger.error(f"Failed to find similar fingerprints: {str(e)}")
            return []
    
    async def _find_similar_audio_fingerprints(self, fingerprint_hash: str, fingerprint_type: str,
                                             threshold: float, max_results: int) -> List[Dict[str, Any]]:
        """Find similar audio fingerprints using specialized audio matching"""        conn = await self.db_manager.get_connection()
        try:
            # Use Hamming distance for audio fingerprints
            results = await conn.fetch("""                SELECT cf.fingerprint_id, cf.content_id, cf.user_id, cf.fingerprint_hash,
                       cf.quality_score, cf.metadata, cf.created_at,
                       -- Calculate Hamming distance similarity
                       1.0 - (bit_count(cf.fingerprint_hash::bit(64) # $1::bit(64))::float / 64.0) as similarity_score
                FROM content_fingerprints cf
                WHERE cf.fingerprint_type = $2
                  AND cf.status = 'completed'
                  AND cf.fingerprint_hash != $1
                  AND (cf.expires_at IS NULL OR cf.expires_at > NOW())
                  AND 1.0 - (bit_count(cf.fingerprint_hash::bit(64) # $1::bit(64))::float / 64.0) >= $3
                ORDER BY similarity_score DESC
                LIMIT $4
            """, fingerprint_hash, fingerprint_type, threshold, max_results)
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Failed to find similar audio fingerprints: {str(e)}")
            return []
        finally:
            await self.db_manager.return_connection(conn)
    
    async def _find_similar_image_fingerprints(self, fingerprint_hash: str, fingerprint_type: str,
                                             threshold: float, max_results: int) -> List[Dict[str, Any]]:
        """Find similar image fingerprints using perceptual hashing"""        conn = await self.db_manager.get_connection()
        try:
            # Use Hamming distance for perceptual hashes
            results = await conn.fetch("""                SELECT cf.fingerprint_id, cf.content_id, cf.user_id, cf.fingerprint_hash,
                       cf.quality_score, cf.metadata, cf.created_at,
                       -- Calculate perceptual hash similarity
                       1.0 - (bit_count(cf.fingerprint_hash::bit(64) # $1::bit(64))::float / 64.0) as similarity_score
                FROM content_fingerprints cf
                WHERE cf.fingerprint_type = $2
                  AND cf.status = 'completed'
                  AND cf.fingerprint_hash != $1
                  AND (cf.expires_at IS NULL OR cf.expires_at > NOW())
                  AND 1.0 - (bit_count(cf.fingerprint_hash::bit(64) # $1::bit(64))::float / 64.0) >= $3
                ORDER BY similarity_score DESC
                LIMIT $4
            """, fingerprint_hash, fingerprint_type, threshold, max_results)
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Failed to find similar image fingerprints: {str(e)}")
            return []
        finally:
            await self.db_manager.return_connection(conn)
    
    async def _find_similar_text_fingerprints(self, fingerprint_hash: str, fingerprint_type: str,
                                            threshold: float, max_results: int) -> List[Dict[str, Any]]:
        """Find similar text fingerprints using locality-sensitive hashing"""        conn = await self.db_manager.get_connection()
        try:
            if fingerprint_type == FingerprintType.TEXT_MINHASH:
                # Use Jaccard similarity for MinHash
                results = await conn.fetch("""                    SELECT cf.fingerprint_id, cf.content_id, cf.user_id, cf.fingerprint_hash,
                           cf.quality_score, cf.metadata, cf.created_at,
                           -- Calculate MinHash Jaccard similarity (simplified)
                           CASE WHEN length($1) > 0 AND length(cf.fingerprint_hash) > 0
                                THEN similarity(cf.fingerprint_hash, $1)
                                ELSE 0.0 END as similarity_score
                    FROM content_fingerprints cf
                    WHERE cf.fingerprint_type = $2
                      AND cf.status = 'completed'
                      AND cf.fingerprint_hash != $1
                      AND (cf.expires_at IS NULL OR cf.expires_at > NOW())
                      AND similarity(cf.fingerprint_hash, $1) >= $3
                    ORDER BY similarity_score DESC
                    LIMIT $4
                """, fingerprint_hash, fingerprint_type, threshold, max_results)
            else:
                # Use Hamming distance for SimHash
                results = await conn.fetch("""                    SELECT cf.fingerprint_id, cf.content_id, cf.user_id, cf.fingerprint_hash,
                           cf.quality_score, cf.metadata, cf.created_at,
                           1.0 - (bit_count(cf.fingerprint_hash::bit(64) # $1::bit(64))::float / 64.0) as similarity_score
                    FROM content_fingerprints cf
                    WHERE cf.fingerprint_type = $2
                      AND cf.status = 'completed'
                      AND cf.fingerprint_hash != $1
                      AND (cf.expires_at IS NULL OR cf.expires_at > NOW())
                      AND 1.0 - (bit_count(cf.fingerprint_hash::bit(64) # $1::bit(64))::float / 64.0) >= $3
                    ORDER BY similarity_score DESC
                    LIMIT $4
                """, fingerprint_hash, fingerprint_type, threshold, max_results)
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Failed to find similar text fingerprints: {str(e)}")
            return []
        finally:
            await self.db_manager.return_connection(conn)
    
    async def _find_similar_generic_fingerprints(self, fingerprint_hash: str, fingerprint_type: str,
                                               threshold: float, max_results: int) -> List[Dict[str, Any]]:
        """Find similar fingerprints using generic string similarity"""        conn = await self.db_manager.get_connection()
        try:
            results = await conn.fetch("""                SELECT cf.fingerprint_id, cf.content_id, cf.user_id, cf.fingerprint_hash,
                       cf.quality_score, cf.metadata, cf.created_at,
                       similarity(cf.fingerprint_hash, $1) as similarity_score
                FROM content_fingerprints cf
                WHERE cf.fingerprint_type = $2
                  AND cf.status = 'completed'
                  AND cf.fingerprint_hash != $1
                  AND (cf.expires_at IS NULL OR cf.expires_at > NOW())
                  AND similarity(cf.fingerprint_hash, $1) >= $3
                ORDER BY similarity_score DESC
                LIMIT $4
            """, fingerprint_hash, fingerprint_type, threshold, max_results)
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Failed to find similar generic fingerprints: {str(e)}")
            return []
        finally:
            await self.db_manager.return_connection(conn)
    
    async def _cache_fingerprint(self, fingerprint_id: str, fingerprint_data: Dict[str, Any]):
        """Cache fingerprint data in Redis for fast access"""        try:
            redis_conn = await self.redis_manager.get_connection()
            cache_key = f"fingerprint:{fingerprint_id}"
            
            await redis_conn.setex(
                cache_key, 
                self.similarity_cache_ttl, 
                json.dumps(fingerprint_data)
            )
            
        except Exception as e:
            logger.debug(f"Failed to cache fingerprint: {str(e)}")
    
    async def _cache_similarity_results(self, cache_key: str, results: List[Dict[str, Any]]):
        """Cache similarity search results"""        try:
            redis_conn = await self.redis_manager.get_connection()
            
            # Convert datetime objects to strings for JSON serialization
            cacheable_results = []
            for result in results:
                result_copy = result.copy()
                if 'created_at' in result_copy:
                    result_copy['created_at'] = result_copy['created_at'].isoformat()
                cacheable_results.append(result_copy)
            
            await redis_conn.setex(
                cache_key,
                self.similarity_cache_ttl,
                json.dumps(cacheable_results)
            )
            
        except Exception as e:
            logger.debug(f"Failed to cache similarity results: {str(e)}")
    
    async def _get_cached_similarity_results(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached similarity search results"""        try:
            redis_conn = await self.redis_manager.get_connection()
            cached_data = await redis_conn.get(cache_key)
            
            if cached_data:
                results = json.loads(cached_data)
                # Convert string back to datetime objects
                for result in results:
                    if 'created_at' in result:
                        result['created_at'] = datetime.fromisoformat(result['created_at'])
                return results
            
            return None
            
        except Exception as e:
            logger.debug(f"Failed to get cached similarity results: {str(e)}")
            return None
    
    async def _process_fingerprint_clustering(self, fingerprint_id: str, fingerprint_type: str):
        """Process fingerprint for clustering analysis"""        try:
            # This is a simplified clustering implementation
            # In production, you'd use more sophisticated clustering algorithms
            
            conn = await self.db_manager.get_connection()
            
            # Find existing clusters for this fingerprint type
            similar_clusters = await conn.fetch("""                SELECT fc.cluster_id, fc.cluster_centroid, fc.cluster_size
                FROM fingerprint_clusters fc
                WHERE fc.fingerprint_type = $1
                  AND fc.cluster_size < 1000  -- Don't add to overly large clusters
                ORDER BY fc.cluster_size DESC
                LIMIT 10
            """, fingerprint_type)
            
            # For now, assign to the smallest cluster or create new one
            if similar_clusters:
                cluster_id = similar_clusters[-1]['cluster_id']
                
                # Update cluster
                await conn.execute("""                    UPDATE fingerprint_clusters 
                    SET cluster_size = cluster_size + 1,
                        updated_at = NOW()
                    WHERE cluster_id = $1
                """, cluster_id)
                
                # Assign fingerprint to cluster
                await conn.execute("""                    UPDATE content_fingerprints 
                    SET similarity_cluster_id = $1
                    WHERE fingerprint_id = $2
                """, cluster_id, fingerprint_id)
            
        except Exception as e:
            logger.debug(f"Clustering process failed for fingerprint {fingerprint_id}: {str(e)}")
        finally:
            await self.db_manager.return_connection(conn)
    
    async def _load_fingerprint_statistics(self):
        """Load existing fingerprint statistics"""        try:
            conn = await self.db_manager.get_connection()
            
            # Load latest statistics for each fingerprint type
            stats = await conn.fetch("""                SELECT fingerprint_type, total_count, matches_count, 
                       false_positives, average_similarity
                FROM fingerprint_statistics
                WHERE date_collected = CURRENT_DATE
            """)
            
            for stat in stats:
                self.index_stats[stat['fingerprint_type']] = {
                    'total_fingerprints': stat['total_count'],
                    'matches_found': stat['matches_count'],
                    'false_positives': stat['false_positives'],
                    'average_similarity': stat['average_similarity'],
                    'last_updated': datetime.now()
                }
            
            logger.info(f"Loaded statistics for {len(stats)} fingerprint types")
            
        except Exception as e:
            logger.debug(f"Failed to load fingerprint statistics: {str(e)}")
        finally:
            await self.db_manager.return_connection(conn)
    
    async def _setup_cleanup_schedule(self):
        """Setup automatic cleanup of expired fingerprints"""        # This would typically run as a background task
        pass
    
    async def get_fingerprint_statistics(self, fingerprint_type: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive fingerprint statistics"""        try:
            if fingerprint_type:
                if fingerprint_type not in self.index_stats:
                    return {'error': f'No statistics available for {fingerprint_type}'}
                
                return {
                    'fingerprint_type': fingerprint_type,
                    'statistics': self.index_stats[fingerprint_type],
                    'configuration': self.fingerprint_configs.get(fingerprint_type, {})
                }
            else:
                return {
                    'total_types': len(self.index_stats),
                    'statistics_by_type': dict(self.index_stats),
                    'total_fingerprints': sum(
                        stats['total_fingerprints'] for stats in self.index_stats.values()
                    ),
                    'total_matches': sum(
                        stats['matches_found'] for stats in self.index_stats.values()
                    )
                }
                
        except Exception as e:
            logger.error(f"Failed to get fingerprint statistics: {str(e)}")
            return {'error': str(e)}
    
    async def cleanup_expired_fingerprints(self) -> Dict[str, Any]:
        """Clean up expired fingerprints to maintain performance"""        try:
            conn = await self.db_manager.get_connection()
            start_time = datetime.now()
            
            # Delete expired fingerprints
            deleted_count = await conn.fetchval("""                DELETE FROM content_fingerprints
                WHERE expires_at IS NOT NULL AND expires_at < NOW()
            """)
            
            # Clean up orphaned similarity matches
            orphaned_matches = await conn.fetchval("""                DELETE FROM fingerprint_similarity_matches
                WHERE query_fingerprint_id NOT IN (SELECT fingerprint_id FROM content_fingerprints)
                   OR matched_fingerprint_id NOT IN (SELECT fingerprint_id FROM content_fingerprints)
            """)
            
            cleanup_time = (datetime.now() - start_time).total_seconds()
            
            # Clear related cache entries
            redis_conn = await self.redis_manager.get_connection()
            await redis_conn.flushdb()  # Clear similarity cache
            
            result = {
                'deleted_fingerprints': deleted_count or 0,
                'deleted_matches': orphaned_matches or 0,
                'cleanup_time': cleanup_time,
                'completed_at': datetime.now().isoformat()
            }
            
            logger.info(f"Fingerprint cleanup completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired fingerprints: {str(e)}")
            return {'error': str(e)}
        finally:
            await self.db_manager.return_connection(conn)
    
    async def cleanup(self):
        """Cleanup resources and connections"""        try:
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
            
            logger.info("FingerprintIndexManager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during FingerprintIndexManager cleanup: {str(e)}")
    
    async def _save_final_statistics(self):
        """Save current statistics to database"""        try:
            conn = await self.db_manager.get_connection()
            
            for fingerprint_type, stats in self.index_stats.items():
                await conn.execute("""                    INSERT INTO fingerprint_statistics 
                    (fingerprint_type, total_count, matches_count, false_positives, average_similarity)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (fingerprint_type, date_collected)
                    DO UPDATE SET
                        total_count = EXCLUDED.total_count,
                        matches_count = EXCLUDED.matches_count,
                        false_positives = EXCLUDED.false_positives,
                        average_similarity = EXCLUDED.average_similarity
                """, fingerprint_type, stats['total_fingerprints'], stats['matches_found'],
                    stats['false_positives'], stats['average_similarity'])
            
            logger.info("Final fingerprint statistics saved")
            
        except Exception as e:
            logger.debug(f"Failed to save final statistics: {str(e)}")
        finally:
            await self.db_manager.return_connection(conn)
