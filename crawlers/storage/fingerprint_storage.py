"""
Fingerprint Storage Module
=========================

Professional fingerprint management storage for IA-Influencer-Agent platform.
Handles content fingerprints, similarity matching, and violation detection using AI.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""

import logging
import asyncio
import json
import uuid
import hashlib
import base64
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import numpy as np

from .interfaces import (
    FingerPrintStorageProvider, FingerPrintType, ContentType, Platform,
    ViolationRecord, ViolationSeverity, CrawlerData, StorageException
)
from .database import DatabaseStorageProvider

logger = logging.getLogger(__name__)

@dataclass
class FingerPrintRecord:
    """Comprehensive fingerprint record."""
    id: str
    content_id: str
    user_id: str
    fingerprint_type: FingerPrintType
    fingerprint_data: Union[str, List[float]]
    content_type: ContentType
    metadata: Dict[str, Any] = field(default_factory=dict)
    algorithm_version: str = "1.0"
    quality_score: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_matched: Optional[datetime] = None
    match_count: int = 0

@dataclass
class SimilarityMatch:
    """Similarity search result."""
    content_id: str
    fingerprint_id: str
    similarity_score: float
    fingerprint_type: FingerPrintType
    metadata: Dict[str, Any] = field(default_factory=dict)
    matched_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ViolationDetectionResult:
    """Violation detection analysis result."""
    is_violation: bool
    confidence_score: float
    similarity_matches: List[SimilarityMatch] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    recommended_action: str = "review"  # review, auto_takedown, ignore
    violation_severity: ViolationSeverity = ViolationSeverity.MEDIUM

class DatabaseFingerPrintStorageProvider(DatabaseStorageProvider, FingerPrintStorageProvider):
    """
    Database-based fingerprint storage provider with advanced AI matching.
    
    Implements multi-algorithm fingerprinting, similarity search,
    and automated violation detection with high performance.
    """
    
    def __init__(self, provider_id: str, config: Dict[str, Any]):
        """Initialize database fingerprint storage provider."""
        super().__init__(provider_id, config)
        self.similarity_engines = {}
        self.violation_detectors = {}
        
    async def connect(self) -> None:
        """Connect to database and initialize fingerprint tables."""
        await super().connect()
        await self._create_fingerprint_tables()
        await self._initialize_similarity_engines()
        await self._initialize_violation_detectors()
        
    async def _create_fingerprint_tables(self) -> None:
        """Create fingerprint-specific database tables."""
        fingerprint_table_sql = """
        CREATE TABLE IF NOT EXISTS content_fingerprints (
            id VARCHAR(36) PRIMARY KEY,
            content_id VARCHAR(36) NOT NULL,
            user_id VARCHAR(36) NOT NULL,
            fingerprint_type VARCHAR(50) NOT NULL,
            fingerprint_hash VARCHAR(64),
            fingerprint_data LONGTEXT,
            vector_data BLOB,
            content_type VARCHAR(50) NOT NULL,
            algorithm_version VARCHAR(20) DEFAULT '1.0',
            quality_score FLOAT DEFAULT 1.0,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_matched TIMESTAMP,
            match_count INTEGER DEFAULT 0,
            
            INDEX idx_fingerprint_content (content_id),
            INDEX idx_fingerprint_user (user_id),
            INDEX idx_fingerprint_type (fingerprint_type),
            INDEX idx_fingerprint_hash (fingerprint_hash),
            INDEX idx_fingerprint_content_type (content_type),
            INDEX idx_fingerprint_quality (quality_score),
            INDEX idx_fingerprint_created (created_at)
        );
        """
        
        similarity_cache_sql = """
        CREATE TABLE IF NOT EXISTS similarity_cache (
            id VARCHAR(36) PRIMARY KEY,
            fingerprint_a_id VARCHAR(36) NOT NULL,
            fingerprint_b_id VARCHAR(36) NOT NULL,
            similarity_score FLOAT NOT NULL,
            algorithm_used VARCHAR(50) NOT NULL,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            valid_until TIMESTAMP,
            
            UNIQUE KEY unique_pair (fingerprint_a_id, fingerprint_b_id),
            INDEX idx_similarity_score (similarity_score),
            INDEX idx_similarity_fingerprint_a (fingerprint_a_id),
            INDEX idx_similarity_fingerprint_b (fingerprint_b_id),
            INDEX idx_similarity_calculated (calculated_at)
        );
        """
        
        violation_detections_sql = """
        CREATE TABLE IF NOT EXISTS violation_detections (
            id VARCHAR(36) PRIMARY KEY,
            original_fingerprint_id VARCHAR(36) NOT NULL,
            detected_fingerprint_id VARCHAR(36),
            crawler_data_id VARCHAR(36),
            platform VARCHAR(50) NOT NULL,
            violation_url VARCHAR(1000),
            similarity_score FLOAT NOT NULL,
            confidence_score FLOAT NOT NULL,
            fingerprint_matches JSONB,
            violation_severity VARCHAR(20) NOT NULL,
            evidence JSONB,
            recommended_action VARCHAR(50) DEFAULT 'review',
            status VARCHAR(20) DEFAULT 'pending',
            auto_processed BOOLEAN DEFAULT FALSE,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP,
            
            INDEX idx_violation_original (original_fingerprint_id),
            INDEX idx_violation_platform (platform),
            INDEX idx_violation_similarity (similarity_score),
            INDEX idx_violation_confidence (confidence_score),
            INDEX idx_violation_severity (violation_severity),
            INDEX idx_violation_status (status),
            INDEX idx_violation_detected (detected_at)
        );
        """
        
        fingerprint_index_sql = """
        CREATE TABLE IF NOT EXISTS fingerprint_search_index (
            id VARCHAR(36) PRIMARY KEY,
            fingerprint_id VARCHAR(36) NOT NULL,
            fingerprint_type VARCHAR(50) NOT NULL,
            search_tokens TEXT,
            embedding_vector BLOB,
            hash_buckets JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (fingerprint_id) REFERENCES content_fingerprints(id) ON DELETE CASCADE,
            INDEX idx_search_fingerprint (fingerprint_id),
            INDEX idx_search_type (fingerprint_type),
            FULLTEXT KEY ft_search_tokens (search_tokens)
        );
        """
        
        try:
            async with self.get_connection() as conn:
                await conn.execute(fingerprint_table_sql)
                await conn.execute(similarity_cache_sql)
                await conn.execute(violation_detections_sql)
                await conn.execute(fingerprint_index_sql)
                await conn.commit()
                
            logger.info("Fingerprint tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create fingerprint tables: {e}")
            raise StorageException(f"Fingerprint table creation failed: {e}")
    
    async def _initialize_similarity_engines(self) -> None:
        """Initialize similarity search engines for different fingerprint types."""
        try:
            self.similarity_engines = {
                FingerPrintType.CHROMAPRINT: self._chromaprint_similarity,
                FingerPrintType.PERCEPTUAL_HASH: self._perceptual_hash_similarity,
                FingerPrintType.CONTENT_HASH: self._content_hash_similarity,
                FingerPrintType.VECTOR_EMBEDDING: self._vector_embedding_similarity,
                FingerPrintType.BERT_EMBEDDING: self._bert_embedding_similarity,
                FingerPrintType.CLIP_EMBEDDING: self._clip_embedding_similarity
            }
            
            # Initialize LSH (Locality Sensitive Hashing) for fast similarity search
            self.lsh_engines = {}
            
            logger.info("Similarity engines initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize similarity engines: {e}")
    
    async def _initialize_violation_detectors(self) -> None:
        """Initialize violation detection algorithms."""
        try:
            self.violation_detectors = {
                'threshold_based': self._threshold_based_detection,
                'ml_classifier': self._ml_classifier_detection,
                'ensemble': self._ensemble_detection
            }
            
            # Load ML models for violation detection
            # In production, load actual trained models
            self.ml_models = {
                'audio_violation_classifier': None,  # Load audio classification model
                'video_violation_classifier': None,  # Load video classification model
                'image_violation_classifier': None,  # Load image classification model
                'text_violation_classifier': None    # Load text classification model
            }
            
            logger.info("Violation detectors initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize violation detectors: {e}")
    
    async def store_fingerprint(
        self,
        content_id: str,
        fingerprint_type: FingerPrintType,
        fingerprint_data: Union[str, List[float]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store content fingerprint with optimized indexing."""
        try:
            fingerprint_id = str(uuid.uuid4())
            fingerprint_hash = self._generate_fingerprint_hash(fingerprint_data)
            
            # Serialize fingerprint data
            if isinstance(fingerprint_data, list):
                # Vector data
                data_str = json.dumps(fingerprint_data)
                vector_data = np.array(fingerprint_data, dtype=np.float32).tobytes()
            else:
                # String data
                data_str = str(fingerprint_data)
                vector_data = None
            
            # Get content information
            content_info = await self._get_content_info(content_id)
            content_type = content_info.get('content_type', ContentType.TEXT)
            user_id = content_info.get('user_id', 'unknown')
            
            # Calculate quality score
            quality_score = self._calculate_fingerprint_quality(fingerprint_type, fingerprint_data)
            
            sql = """
            INSERT INTO content_fingerprints (
                id, content_id, user_id, fingerprint_type, fingerprint_hash,
                fingerprint_data, vector_data, content_type, quality_score, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (
                fingerprint_id,
                content_id,
                user_id,
                fingerprint_type.value,
                fingerprint_hash,
                data_str,
                vector_data,
                content_type.value if isinstance(content_type, ContentType) else content_type,
                quality_score,
                json.dumps(metadata or {})
            )
            
            async with self.get_connection() as conn:
                await conn.execute(sql, values)
                await conn.commit()
            
            # Update search index
            await self._update_search_index(fingerprint_id, fingerprint_type, fingerprint_data)
            
            logger.debug(f"Stored fingerprint: {fingerprint_id} for content: {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store fingerprint for content {content_id}: {e}")
            raise StorageException(f"Fingerprint storage failed: {e}")
    
    async def find_similar_content(
        self,
        fingerprint_data: Union[str, List[float]],
        fingerprint_type: FingerPrintType,
        similarity_threshold: float = 0.8,
        max_results: int = 10
    ) -> List[Tuple[str, float]]:
        """Find similar content using optimized similarity search."""
        try:
            # Get similarity engine for fingerprint type
            similarity_engine = self.similarity_engines.get(fingerprint_type)
            if not similarity_engine:
                raise ValueError(f"No similarity engine for {fingerprint_type}")
            
            # Fast pre-filtering using search index
            candidate_fingerprints = await self._get_similarity_candidates(
                fingerprint_data, fingerprint_type, max_results * 5
            )
            
            if not candidate_fingerprints:
                return []
            
            # Calculate similarity scores
            similarities = []
            for candidate in candidate_fingerprints:
                try:
                    score = await similarity_engine(fingerprint_data, candidate['fingerprint_data'])
                    
                    if score >= similarity_threshold:
                        similarities.append({
                            'content_id': candidate['content_id'],
                            'fingerprint_id': candidate['id'],
                            'similarity_score': score,
                            'quality_score': candidate['quality_score']
                        })
                        
                        # Update match statistics
                        await self._update_match_stats(candidate['id'])
                        
                except Exception as e:
                    logger.warning(f"Similarity calculation failed for fingerprint {candidate['id']}: {e}")
                    continue
            
            # Sort by combined score (similarity + quality)
            similarities.sort(key=lambda x: x['similarity_score'] * x['quality_score'], reverse=True)
            
            # Return top results
            return [
                (item['content_id'], item['similarity_score'])
                for item in similarities[:max_results]
            ]
            
        except Exception as e:
            logger.error(f"Failed to find similar content: {e}")
            raise StorageException(f"Similarity search failed: {e}")
    
    async def detect_violations(
        self,
        content_id: str,
        platform_data: CrawlerData
    ) -> List[ViolationRecord]:
        """Detect copyright violations using AI analysis."""
        try:
            # Get original content fingerprints
            original_fingerprints = await self._get_content_fingerprints(content_id)
            if not original_fingerprints:
                logger.warning(f"No fingerprints found for content: {content_id}")
                return []
            
            # Extract fingerprints from platform data
            detected_fingerprints = await self._extract_platform_fingerprints(platform_data)
            
            violations = []
            
            for original_fp in original_fingerprints:
                for detected_fp in detected_fingerprints:
                    if original_fp['fingerprint_type'] == detected_fp['fingerprint_type']:
                        # Calculate similarity
                        similarity_engine = self.similarity_engines.get(
                            FingerPrintType(original_fp['fingerprint_type'])
                        )
                        
                        if similarity_engine:
                            similarity_score = await similarity_engine(
                                original_fp['fingerprint_data'],
                                detected_fp['fingerprint_data']
                            )
                            
                            # Detect violation using multiple methods
                            detection_result = await self._analyze_violation(
                                original_fp, detected_fp, similarity_score, platform_data
                            )
                            
                            if detection_result.is_violation:
                                violation = self._create_violation_record(
                                    original_fp, detected_fp, detection_result, platform_data
                                )
                                violations.append(violation)
                                
                                # Store violation detection
                                await self._store_violation_detection(violation, detection_result)
            
            # Apply business rules and filtering
            violations = await self._filter_violations(violations)
            
            return violations
            
        except Exception as e:
            logger.error(f"Failed to detect violations for content {content_id}: {e}")
            raise StorageException(f"Violation detection failed: {e}")
    
    async def update_fingerprint_index(
        self,
        content_id: str,
        fingerprint_type: FingerPrintType
    ) -> bool:
        """Update fingerprint search index for improved performance."""
        try:
            # Get fingerprint
            sql = """
            SELECT id, fingerprint_data FROM content_fingerprints 
            WHERE content_id = ? AND fingerprint_type = ?
            """
            
            async with self.get_connection() as conn:
                cursor = await conn.execute(sql, [content_id, fingerprint_type.value])
                row = await cursor.fetchone()
            
            if not row:
                return False
            
            fingerprint_id, fingerprint_data = row
            
            # Parse fingerprint data
            if fingerprint_type in [FingerPrintType.VECTOR_EMBEDDING, FingerPrintType.BERT_EMBEDDING, FingerPrintType.CLIP_EMBEDDING]:
                data = json.loads(fingerprint_data)
            else:
                data = fingerprint_data
            
            # Update search index
            await self._update_search_index(fingerprint_id, fingerprint_type, data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update fingerprint index: {e}")
            return False
    
    async def _get_content_info(self, content_id: str) -> Dict[str, Any]:
        """Get content information for fingerprint storage."""
        # In a real implementation, query content table
        # For now, return defaults
        return {
            'content_type': ContentType.TEXT,
            'user_id': 'unknown'
        }
    
    def _generate_fingerprint_hash(self, fingerprint_data: Union[str, List[float]]) -> str:
        """Generate hash for fingerprint data."""
        if isinstance(fingerprint_data, list):
            # For vector data, create hash of normalized values
            normalized = json.dumps(sorted([round(x, 6) for x in fingerprint_data]))
            return hashlib.sha256(normalized.encode()).hexdigest()
        else:
            # For string data, direct hash
            return hashlib.sha256(str(fingerprint_data).encode()).hexdigest()
    
    def _calculate_fingerprint_quality(
        self,
        fingerprint_type: FingerPrintType,
        fingerprint_data: Union[str, List[float]]
    ) -> float:
        """Calculate quality score for fingerprint."""
        try:
            if fingerprint_type == FingerPrintType.CHROMAPRINT:
                # For audio fingerprints, longer is generally better
                if isinstance(fingerprint_data, str):
                    return min(1.0, len(fingerprint_data) / 1000.0)
            
            elif fingerprint_type in [FingerPrintType.VECTOR_EMBEDDING, FingerPrintType.BERT_EMBEDDING, FingerPrintType.CLIP_EMBEDDING]:
                # For embeddings, check vector properties
                if isinstance(fingerprint_data, list):
                    vector = np.array(fingerprint_data)
                    # Quality based on magnitude and distribution
                    magnitude = np.linalg.norm(vector)
                    std_dev = np.std(vector)
                    return min(1.0, magnitude * std_dev / 10.0)
            
            elif fingerprint_type == FingerPrintType.PERCEPTUAL_HASH:
                # For perceptual hashes, check bit distribution
                if isinstance(fingerprint_data, str):
                    # Convert to binary and check entropy
                    try:
                        binary = bin(int(fingerprint_data, 16))[2:]
                        ones = binary.count('1')
                        zeros = binary.count('0')
                        total = len(binary)
                        if total > 0:
                            entropy = -((ones/total) * np.log2(ones/total + 1e-10) + 
                                      (zeros/total) * np.log2(zeros/total + 1e-10))
                            return entropy  # Max entropy is 1.0
                    except Exception as entropy_error:
                        logger.debug(f"Entropy calculation failed: {entropy_error}")
                        # Fallback: simple distribution check
                        try:
                            unique_chars = len(set(fingerprint_data))
                            total_chars = len(fingerprint_data)
                            return min(1.0, unique_chars / max(1, total_chars * 0.5))
                        except:
                            return 0.5
            
            return 1.0  # Default quality
            
        except Exception as e:
            logger.warning(f"Failed to calculate fingerprint quality: {e}")
            return 1.0
    
    async def _update_search_index(
        self,
        fingerprint_id: str,
        fingerprint_type: FingerPrintType,
        fingerprint_data: Union[str, List[float]]
    ) -> None:
        """Update search index for faster similarity search."""
        try:
            # Generate search tokens
            search_tokens = self._generate_search_tokens(fingerprint_type, fingerprint_data)
            
            # Generate hash buckets for LSH
            hash_buckets = self._generate_hash_buckets(fingerprint_type, fingerprint_data)
            
            # Prepare embedding vector
            embedding_vector = None
            if isinstance(fingerprint_data, list):
                embedding_vector = np.array(fingerprint_data, dtype=np.float32).tobytes()
            
            sql = """
            INSERT INTO fingerprint_search_index (
                id, fingerprint_id, fingerprint_type, search_tokens, 
                embedding_vector, hash_buckets
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON DUPLICATE KEY UPDATE
                search_tokens = VALUES(search_tokens),
                embedding_vector = VALUES(embedding_vector),
                hash_buckets = VALUES(hash_buckets)
            """
            
            values = (
                str(uuid.uuid4()),
                fingerprint_id,
                fingerprint_type.value,
                search_tokens,
                embedding_vector,
                json.dumps(hash_buckets)
            )
            
            async with self.get_connection() as conn:
                await conn.execute(sql, values)
                await conn.commit()
            
        except Exception as e:
            logger.warning(f"Failed to update search index: {e}")
    
    def _generate_search_tokens(
        self,
        fingerprint_type: FingerPrintType,
        fingerprint_data: Union[str, List[float]]
    ) -> str:
        """Generate search tokens for text-based searching."""
        if fingerprint_type == FingerPrintType.CHROMAPRINT:
            # For audio fingerprints, generate n-grams
            if isinstance(fingerprint_data, str):
                tokens = []
                for i in range(0, len(fingerprint_data), 8):
                    tokens.append(fingerprint_data[i:i+8])
                return ' '.join(tokens)
        
        elif fingerprint_type == FingerPrintType.PERCEPTUAL_HASH:
            # For perceptual hashes, generate bit patterns
            if isinstance(fingerprint_data, str):
                tokens = []
                for i in range(0, len(fingerprint_data), 4):
                    tokens.append(fingerprint_data[i:i+4])
                return ' '.join(tokens)
        
        return str(fingerprint_data)[:1000]  # Truncate for text search
    
    def _generate_hash_buckets(
        self,
        fingerprint_type: FingerPrintType,
        fingerprint_data: Union[str, List[float]]
    ) -> List[str]:
        """Generate LSH hash buckets for fast similarity search."""
        buckets = []
        
        try:
            if fingerprint_type in [FingerPrintType.VECTOR_EMBEDDING, FingerPrintType.BERT_EMBEDDING, FingerPrintType.CLIP_EMBEDDING]:
                if isinstance(fingerprint_data, list):
                    vector = np.array(fingerprint_data)
                    
                    # Random projection LSH
                    num_buckets = 10
                    bucket_size = max(1, len(vector) // num_buckets)
                    
                    for i in range(num_buckets):
                        start_idx = i * bucket_size
                        end_idx = min((i + 1) * bucket_size, len(vector))
                        bucket_sum = np.sum(vector[start_idx:end_idx])
                        bucket_hash = hashlib.md5(str(bucket_sum).encode()).hexdigest()[:8]
                        buckets.append(bucket_hash)
            
            elif fingerprint_type == FingerPrintType.CHROMAPRINT:
                if isinstance(fingerprint_data, str):
                    # Create buckets from fingerprint segments
                    segment_size = max(1, len(fingerprint_data) // 10)
                    for i in range(0, len(fingerprint_data), segment_size):
                        segment = fingerprint_data[i:i+segment_size]
                        bucket_hash = hashlib.md5(segment.encode()).hexdigest()[:8]
                        buckets.append(bucket_hash)
            
        except Exception as e:
            logger.warning(f"Failed to generate hash buckets: {e}")
        
        return buckets[:20]  # Limit bucket count
    
    async def _get_similarity_candidates(
        self,
        fingerprint_data: Union[str, List[float]],
        fingerprint_type: FingerPrintType,
        max_candidates: int
    ) -> List[Dict[str, Any]]:
        """Get similarity candidates using search index."""
        try:
            # Generate hash buckets for query
            query_buckets = self._generate_hash_buckets(fingerprint_type, fingerprint_data)
            
            if not query_buckets:
                # Fallback to all fingerprints of same type
                sql = """
                SELECT cf.id, cf.content_id, cf.fingerprint_data, cf.quality_score
                FROM content_fingerprints cf
                WHERE cf.fingerprint_type = ?
                ORDER BY cf.quality_score DESC, cf.created_at DESC
                LIMIT ?
                """
                
                async with self.get_connection() as conn:
                    cursor = await conn.execute(sql, [fingerprint_type.value, max_candidates])
                    rows = await cursor.fetchall()
                
                return [
                    {
                        'id': row[0],
                        'content_id': row[1],
                        'fingerprint_data': row[2],
                        'quality_score': row[3]
                    }
                    for row in rows
                ]
            
            # Use hash buckets for fast filtering
            bucket_conditions = []
            params = []
            
            for bucket in query_buckets[:5]:  # Use top 5 buckets
                bucket_conditions.append("JSON_CONTAINS(fsi.hash_buckets, ?)")
                params.append(json.dumps(bucket))
            
            sql = f"""
            SELECT cf.id, cf.content_id, cf.fingerprint_data, cf.quality_score,
                   COUNT(*) as bucket_matches
            FROM content_fingerprints cf
            JOIN fingerprint_search_index fsi ON cf.id = fsi.fingerprint_id
            WHERE cf.fingerprint_type = ? 
                AND ({' OR '.join(bucket_conditions)})
            GROUP BY cf.id
            ORDER BY bucket_matches DESC, cf.quality_score DESC
            LIMIT ?
            """
            
            params = [fingerprint_type.value] + params + [max_candidates]
            
            async with self.get_connection() as conn:
                cursor = await conn.execute(sql, params)
                rows = await cursor.fetchall()
            
            return [
                {
                    'id': row[0],
                    'content_id': row[1],
                    'fingerprint_data': row[2],
                    'quality_score': row[3],
                    'bucket_matches': row[4]
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.warning(f"Failed to get similarity candidates: {e}")
            return []
    
    async def _chromaprint_similarity(self, fp1: str, fp2: str) -> float:
        """Calculate Chromaprint similarity for audio."""
        try:
            # Implement Hamming distance for Chromaprint
            if len(fp1) != len(fp2):
                # Align fingerprints or use subsequence matching
                return self._subsequence_similarity(fp1, fp2)
            
            # Calculate Hamming distance
            differences = sum(c1 != c2 for c1, c2 in zip(fp1, fp2))
            similarity = 1.0 - (differences / len(fp1))
            
            return max(0.0, similarity)
            
        except Exception as e:
            logger.warning(f"Chromaprint similarity calculation failed: {e}")
            return 0.0
    
    async def _perceptual_hash_similarity(self, fp1: str, fp2: str) -> float:
        """Calculate perceptual hash similarity for images/video."""
        try:
            # Convert hex strings to binary
            bin1 = bin(int(fp1, 16))[2:].zfill(64)
            bin2 = bin(int(fp2, 16))[2:].zfill(64)
            
            # Hamming distance
            differences = sum(b1 != b2 for b1, b2 in zip(bin1, bin2))
            similarity = 1.0 - (differences / 64)
            
            return max(0.0, similarity)
            
        except Exception as e:
            logger.warning(f"Perceptual hash similarity calculation failed: {e}")
            return 0.0
    
    async def _content_hash_similarity(self, fp1: str, fp2: str) -> float:
        """Calculate content hash similarity (exact match)."""
        return 1.0 if fp1 == fp2 else 0.0
    
    async def _vector_embedding_similarity(self, fp1: List[float], fp2: List[float]) -> float:
        """Calculate vector embedding similarity (cosine similarity)."""
        try:
            vec1 = np.array(fp1)
            vec2 = np.array(fp2)
            
            # Cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.warning(f"Vector embedding similarity calculation failed: {e}")
            return 0.0
    
    async def _bert_embedding_similarity(self, fp1: List[float], fp2: List[float]) -> float:
        """Calculate BERT embedding similarity."""
        return await self._vector_embedding_similarity(fp1, fp2)
    
    async def _clip_embedding_similarity(self, fp1: List[float], fp2: List[float]) -> float:
        """Calculate CLIP embedding similarity."""
        return await self._vector_embedding_similarity(fp1, fp2)
    
    def _subsequence_similarity(self, fp1: str, fp2: str) -> float:
        """Calculate similarity between fingerprints of different lengths."""
        if not fp1 or not fp2:
            return 0.0
        
        shorter, longer = (fp1, fp2) if len(fp1) <= len(fp2) else (fp2, fp1)
        
        best_similarity = 0.0
        window_size = len(shorter)
        
        # Sliding window approach
        for i in range(len(longer) - window_size + 1):
            window = longer[i:i + window_size]
            differences = sum(c1 != c2 for c1, c2 in zip(shorter, window))
            similarity = 1.0 - (differences / window_size)
            best_similarity = max(best_similarity, similarity)
        
        return best_similarity
    
    async def _get_content_fingerprints(self, content_id: str) -> List[Dict[str, Any]]:
        """Get all fingerprints for content."""
        try:
            sql = """
            SELECT id, fingerprint_type, fingerprint_data, quality_score
            FROM content_fingerprints 
            WHERE content_id = ?
            ORDER BY quality_score DESC
            """
            
            async with self.get_connection() as conn:
                cursor = await conn.execute(sql, [content_id])
                rows = await cursor.fetchall()
            
            return [
                {
                    'id': row[0],
                    'fingerprint_type': row[1],
                    'fingerprint_data': row[2],
                    'quality_score': row[3]
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Failed to get content fingerprints: {e}")
            return []
    
    async def _extract_platform_fingerprints(self, platform_data: CrawlerData) -> List[Dict[str, Any]]:
        """Extract fingerprints from platform data."""
        # In a real implementation, this would use specialized extractors
        # for different content types and platforms
        
        fingerprints = []
        
        # Extract from existing fingerprints in metadata
        if hasattr(platform_data, 'fingerprints') and platform_data.fingerprints:
            for fp_type, fp_data in platform_data.fingerprints.items():
                fingerprints.append({
                    'fingerprint_type': fp_type,
                    'fingerprint_data': fp_data
                })
        
        # Add content analysis to extract fingerprints from URLs
        # This involves downloading and analyzing content
        await self._analyze_content_urls(platform_data, fingerprints)
        
        return fingerprints
    
    async def _analyze_content_urls(self, platform_data: CrawlerData, fingerprints: List[Dict[str, Any]]):
        """Extract fingerprints from URLs in platform data."""
        try:
            # Extract URLs from various sources
            urls_to_analyze = []
            
            # From media URLs
            if hasattr(platform_data, 'media_urls') and platform_data.media_urls:
                urls_to_analyze.extend(platform_data.media_urls)
            
            # From content URLs
            if hasattr(platform_data, 'content_urls') and platform_data.content_urls:
                urls_to_analyze.extend(platform_data.content_urls)
            
            # From embedded links
            if hasattr(platform_data, 'links') and platform_data.links:
                urls_to_analyze.extend(platform_data.links)
            
            # Analyze each URL (limited to avoid excessive processing)
            for url in urls_to_analyze[:5]:  # Limit to 5 URLs per batch
                try:
                    content_fp = await self._extract_fingerprint_from_url(url)
                    if content_fp:
                        fingerprints.append(content_fp)
                except Exception as url_error:
                    logger.debug(f"Failed to extract fingerprint from URL {url}: {url_error}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Content URL analysis failed: {e}")
    
    async def _extract_fingerprint_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract fingerprint from a single URL."""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.head(url) as response:
                    content_type = response.headers.get('content-type', '').lower()
                    content_length = response.headers.get('content-length')
                    
                    # Generate simple URL-based fingerprint
                    url_hash = hashlib.sha256(url.encode()).hexdigest()
                    
                    fingerprint_data = {
                        'fingerprint_type': FingerPrintType.HASH.value,
                        'fingerprint_data': url_hash,
                        'metadata': {
                            'source_url': url,
                            'content_type': content_type,
                            'content_length': content_length,
                            'extracted_at': datetime.utcnow().isoformat()
                        }
                    }
                    
                    # For image/video content, could add more sophisticated analysis
                    if any(media_type in content_type for media_type in ['image/', 'video/', 'audio/']):
                        fingerprint_data['fingerprint_type'] = FingerPrintType.PERCEPTUAL.value
                        fingerprint_data['metadata']['media_type'] = content_type.split('/')[0]
                    
                    return fingerprint_data
                    
        except ImportError:
            # Fallback without aiohttp
            url_hash = hashlib.sha256(url.encode()).hexdigest()
            return {
                'fingerprint_type': FingerPrintType.HASH.value,
                'fingerprint_data': url_hash,
                'metadata': {
                    'source_url': url,
                    'extraction_method': 'fallback',
                    'extracted_at': datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            logger.debug(f"URL fingerprint extraction failed for {url}: {e}")
            return None
    
    async def _analyze_violation(
        self,
        original_fp: Dict[str, Any],
        detected_fp: Dict[str, Any],
        similarity_score: float,
        platform_data: CrawlerData
    ) -> ViolationDetectionResult:
        """Analyze potential violation using multiple detection methods."""
        # Threshold-based detection
        threshold_result = await self._threshold_based_detection(
            similarity_score, original_fp, detected_fp
        )
        
        # ML classifier detection (if available)
        ml_result = await self._ml_classifier_detection(
            original_fp, detected_fp, platform_data
        )
        
        # Ensemble detection
        ensemble_result = await self._ensemble_detection(
            threshold_result, ml_result, similarity_score
        )
        
        return ensemble_result
    
    async def _threshold_based_detection(
        self,
        similarity_score: float,
        original_fp: Dict[str, Any],
        detected_fp: Dict[str, Any]
    ) -> ViolationDetectionResult:
        """Simple threshold-based violation detection."""
        # Thresholds by fingerprint type
        thresholds = {
            FingerPrintType.CHROMAPRINT.value: 0.85,
            FingerPrintType.PERCEPTUAL_HASH.value: 0.90,
            FingerPrintType.CONTENT_HASH.value: 1.0,
            FingerPrintType.VECTOR_EMBEDDING.value: 0.80,
            FingerPrintType.BERT_EMBEDDING.value: 0.75,
            FingerPrintType.CLIP_EMBEDDING.value: 0.80
        }
        
        threshold = thresholds.get(original_fp['fingerprint_type'], 0.80)
        is_violation = similarity_score >= threshold
        
        # Determine severity
        if similarity_score >= 0.95:
            severity = ViolationSeverity.CRITICAL
        elif similarity_score >= 0.90:
            severity = ViolationSeverity.HIGH
        elif similarity_score >= 0.80:
            severity = ViolationSeverity.MEDIUM
        else:
            severity = ViolationSeverity.LOW
        
        # Determine recommended action
        if similarity_score >= 0.95:
            action = "auto_takedown"
        elif similarity_score >= 0.85:
            action = "review"
        else:
            action = "ignore"
        
        return ViolationDetectionResult(
            is_violation=is_violation,
            confidence_score=similarity_score,
            violation_severity=severity,
            recommended_action=action,
            evidence={
                'similarity_score': similarity_score,
                'threshold': threshold,
                'fingerprint_type': original_fp['fingerprint_type']
            }
        )
    
    async def _ml_classifier_detection(
        self,
        original_fp: Dict[str, Any],
        detected_fp: Dict[str, Any],
        platform_data: CrawlerData
    ) -> ViolationDetectionResult:
        """ML-based violation detection (placeholder)."""
        # In a real implementation, use trained ML models
        # For now, return neutral result
        
        return ViolationDetectionResult(
            is_violation=False,
            confidence_score=0.5,
            violation_severity=ViolationSeverity.MEDIUM,
            recommended_action="review"
        )
    
    async def _ensemble_detection(
        self,
        threshold_result: ViolationDetectionResult,
        ml_result: ViolationDetectionResult,
        similarity_score: float
    ) -> ViolationDetectionResult:
        """Ensemble detection combining multiple methods."""
        # Weighted combination
        threshold_weight = 0.7
        ml_weight = 0.3
        
        combined_confidence = (
            threshold_result.confidence_score * threshold_weight +
            ml_result.confidence_score * ml_weight
        )
        
        # Decision based on highest confidence method
        if threshold_result.confidence_score > ml_result.confidence_score:
            primary_result = threshold_result
        else:
            primary_result = ml_result
        
        return ViolationDetectionResult(
            is_violation=primary_result.is_violation,
            confidence_score=combined_confidence,
            violation_severity=primary_result.violation_severity,
            recommended_action=primary_result.recommended_action,
            evidence={
                **primary_result.evidence,
                'ensemble_confidence': combined_confidence,
                'threshold_confidence': threshold_result.confidence_score,
                'ml_confidence': ml_result.confidence_score
            }
        )
    
    def _create_violation_record(
        self,
        original_fp: Dict[str, Any],
        detected_fp: Dict[str, Any],
        detection_result: ViolationDetectionResult,
        platform_data: CrawlerData
    ) -> ViolationRecord:
        """Create violation record from detection result."""
        return ViolationRecord(
            id=str(uuid.uuid4()),
            original_content_id=original_fp.get('content_id', ''),
            detected_content_id=platform_data.content_id,
            platform=platform_data.platform,
            violation_url=platform_data.content_url,
            similarity_score=detection_result.confidence_score,
            severity=detection_result.violation_severity,
            violation_type="fingerprint_match",
            fingerprint_matches={
                FingerPrintType(original_fp['fingerprint_type']): detection_result.confidence_score
            },
            evidence_metadata=detection_result.evidence,
            automated_response=detection_result.recommended_action == "auto_takedown"
        )
    
    async def _store_violation_detection(
        self,
        violation: ViolationRecord,
        detection_result: ViolationDetectionResult
    ) -> None:
        """Store violation detection in database."""
        try:
            sql = """
            INSERT INTO violation_detections (
                id, original_fingerprint_id, platform, violation_url,
                similarity_score, confidence_score, fingerprint_matches,
                violation_severity, evidence, recommended_action, auto_processed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (
                violation.id,
                violation.original_content_id,
                violation.platform.value,
                violation.violation_url,
                violation.similarity_score,
                detection_result.confidence_score,
                json.dumps({k.value: v for k, v in violation.fingerprint_matches.items()}),
                violation.severity.name,
                json.dumps(violation.evidence_metadata),
                detection_result.recommended_action,
                violation.automated_response
            )
            
            async with self.get_connection() as conn:
                await conn.execute(sql, values)
                await conn.commit()
            
        except Exception as e:
            logger.warning(f"Failed to store violation detection: {e}")
    
    async def _filter_violations(self, violations: List[ViolationRecord]) -> List[ViolationRecord]:
        """Apply business rules to filter violations."""
        filtered = []
        
        for violation in violations:
            # Filter by minimum severity
            if violation.severity.value >= ViolationSeverity.MEDIUM.value:
                # Filter by minimum similarity score
                if violation.similarity_score >= 0.75:
                    # Check for duplicates
                    if not await self._is_duplicate_violation(violation):
                        filtered.append(violation)
        
        return filtered
    
    async def _is_duplicate_violation(self, violation: ViolationRecord) -> bool:
        """Check if violation is duplicate."""
        try:
            sql = """
            SELECT COUNT(*) FROM violation_detections 
            WHERE platform = ? AND violation_url = ?
            AND detected_at > ?
            """
            
            # Check for duplicates in last 7 days
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            
            async with self.get_connection() as conn:
                cursor = await conn.execute(sql, [
                    violation.platform.value,
                    violation.violation_url,
                    cutoff_date
                ])
                row = await cursor.fetchone()
            
            return row[0] > 0 if row else False
            
        except Exception as e:
            logger.warning(f"Failed to check duplicate violation: {e}")
            return False
    
    async def _update_match_stats(self, fingerprint_id: str) -> None:
        """Update match statistics for fingerprint."""
        try:
            sql = """
            UPDATE content_fingerprints 
            SET match_count = match_count + 1, last_matched = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            
            async with self.get_connection() as conn:
                await conn.execute(sql, [fingerprint_id])
                await conn.commit()
            
        except Exception as e:
            logger.warning(f"Failed to update match stats: {e}")

# Export fingerprint storage classes
__all__ = [
    'FingerPrintRecord',
    'SimilarityMatch',
    'ViolationDetectionResult',
    'DatabaseFingerPrintStorageProvider'
]
