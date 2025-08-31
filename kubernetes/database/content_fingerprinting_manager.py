"""Content Fingerprinting Database Manager
Advanced fingerprinting data management for IA Influencer Agent

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

AVERTISSEMENT LEGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET SPÉCIALISÉE:
- Lead Developer IA: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- Database Administrator: Fahed Mlaiel
- Sécurité Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Processing Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

⚠️ ATTENTION IMPORTANTE ⚠️
Toute tentative de vol, copie, ou utilisation non autorisée de ce code, 
concept ou idée sans autorisation écrite explicite de Fahed Mlaiel 
sera poursuivie selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

FONCTIONNALITÉS ENTERPRISE:
=========================

🧠 AI FINGERPRINTING DATABASE:
- Stockage haute performance des fingerprints
- Vector similarity search optimization
- Multi-format content support (audio, video, image, text)
- Chunked processing pour gros fichiers
- Duplicate detection avancée
- Real-time indexing avec FAISS

🎵 AUDIO FINGERPRINTING:
- Chromaprint hash storage
- Spectral features vectorization
- Tempo et key detection metadata
- Multi-bitrate fingerprint variants
- Acoustic similarity clustering
- Performance optimization pour matching

🎬 VIDEO FINGERPRINTING:
- Frame-by-frame hash sequences
- Scene detection markers
- Motion vector analysis
- Perceptual hash variants
- Temporal fingerprint segments
- Object detection metadata

🖼️ IMAGE FINGERPRINTING:
- Perceptual hash computation
- CLIP vector embeddings
- Feature point descriptors
- Color histogram analysis
- Edge detection patterns
- Multi-scale representation

📝 TEXT FINGERPRINTING:
- BERT/RoBERTa embeddings
- TF-IDF vectorization
- Semantic similarity vectors
- N-gram pattern analysis
- Language detection metadata
- Content classification tags

⚡ PERFORMANCE OPTIMIZATION:
- Parallel fingerprint processing
- Batch insertion optimization
- Index strategy per content type
- Memory-efficient vector storage
- Cache-friendly data layout
- Query performance tuning

🔍 SIMILARITY SEARCH:
- FAISS index integration
- Approximate nearest neighbor
- Multi-modal similarity scoring
- Threshold-based matching
- Ranked result sets
- Real-time search optimization

📊 ANALYTICS ET REPORTING:
- Fingerprint quality metrics
- Search performance analytics
- Storage utilization tracking
- Duplicate detection statistics
- Content type distributions
- Processing time optimization

🛡️ SÉCURITÉ ET INTÉGRITÉ:
- Fingerprint integrity validation
- Access control per content type
- Audit trail pour modifications
- Encryption des données sensibles
- Backup strategy optimization
- Data retention policies
"""import asyncio
from typing import Dict, Any, Optional, List, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import hashlib
import logging
import struct
import numpy as np
from sqlalchemy import (
    text, select, insert, update, delete, func, and_, or_,
    Index, ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, BYTEA, ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
import faiss
import pickle
from pathlib import Path

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.deployment.database.postgresql_manager import get_postgresql_manager


class ContentType(Enum):
    """Content types for fingerprinting"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MIXED = "mixed"


class FingerprintAlgorithm(Enum):
    """Fingerprinting algorithms"""    # Audio algorithms
    CHROMAPRINT = "chromaprint"
    ESSENTIA_SPECTRAL = "essentia_spectral"
    MFCC_FEATURES = "mfcc_features"
    AUDIO_PERCEPTUAL = "audio_perceptual"
    
    # Video algorithms
    OPENCV_HASH = "opencv_hash"
    PERCEPTUAL_VIDEO = "perceptual_video"
    YOLO_FEATURES = "yolo_features"
    FRAME_DIFFERENCE = "frame_difference"
    
    # Image algorithms
    CLIP_EMBEDDING = "clip_embedding"
    IMAGEHASH_PHASH = "imagehash_phash"
    SIFT_FEATURES = "sift_features"
    COLOR_HISTOGRAM = "color_histogram"
    
    # Text algorithms
    BERT_EMBEDDING = "bert_embedding"
    ROBERTA_EMBEDDING = "roberta_embedding"
    TFIDF_VECTOR = "tfidf_vector"
    SENTENCE_TRANSFORMER = "sentence_transformer"


class SimilarityMetric(Enum):
    """Similarity metrics for matching"""    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    HAMMING = "hamming"
    JACCARD = "jaccard"
    CORRELATION = "correlation"


@dataclass
class FingerprintMetadata:
    """Fingerprint metadata structure"""    content_id: str
    content_type: ContentType
    algorithm: FingerprintAlgorithm
    version: str
    quality_score: float
    processing_time: float
    file_size: int
    duration: Optional[float] = None
    dimensions: Optional[Tuple[int, int]] = None
    encoding_params: Optional[Dict[str, Any]] = None
    extraction_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SimilarityMatch:
    """Similarity match result"""    fingerprint_id: str
    target_fingerprint_id: str
    similarity_score: float
    algorithm: FingerprintAlgorithm
    metric: SimilarityMetric
    match_regions: Optional[List[Dict[str, Any]]] = None
    confidence_level: float = 0.0
    processing_time: float = 0.0


class ContentFingerprintingManager:
    """    Enterprise Content Fingerprinting Database Manager
    
    Manages all aspects of content fingerprinting data storage,
    retrieval, and similarity matching with enterprise-grade
    performance and reliability.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger(f"{__name__}.ContentFingerprintingManager")
        self.settings = get_settings()
        
        # Database components
        self._db_manager = None
        self._faiss_indices: Dict[str, faiss.Index] = {}
        self._vector_dimensions: Dict[FingerprintAlgorithm, int] = {
            FingerprintAlgorithm.CLIP_EMBEDDING: 512,
            FingerprintAlgorithm.BERT_EMBEDDING: 768,
            FingerprintAlgorithm.ROBERTA_EMBEDDING: 768,
            FingerprintAlgorithm.SENTENCE_TRANSFORMER: 384,
            FingerprintAlgorithm.MFCC_FEATURES: 128,
            FingerprintAlgorithm.ESSENTIA_SPECTRAL: 256,
            FingerprintAlgorithm.YOLO_FEATURES: 1024,
            FingerprintAlgorithm.SIFT_FEATURES: 128
        }
        
        # Performance settings
        self.batch_size = self.config.get('batch_size', 1000)
        self.similarity_threshold = self.config.get('similarity_threshold', 0.8)
        self.max_search_results = self.config.get('max_search_results', 100)
        
        # Caching
        self._fingerprint_cache: Dict[str, Any] = {}
        self._cache_size_limit = self.config.get('cache_size_limit', 10000)
    
    async def initialize(self) -> bool:
        """Initialize the fingerprinting manager"""        try:
            self.logger.info("🚀 Initializing Content Fingerprinting Manager...")
            
            # Get database manager
            self._db_manager = get_postgresql_manager()
            
            # Create schema if not exists
            await self._create_fingerprinting_schema()
            
            # Initialize FAISS indices
            await self._initialize_faiss_indices()
            
            # Load existing fingerprints into indices
            await self._load_existing_fingerprints()
            
            self.logger.info("✅ Content Fingerprinting Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Content Fingerprinting Manager: {e}")
            return False
    
    async def _create_fingerprinting_schema(self):
        """Create fingerprinting database schema"""        self.logger.debug("Creating fingerprinting database schema...")
        
        schema_sql = """        -- Content Fingerprints Main Table
        CREATE TABLE IF NOT EXISTS content_fingerprints (
            fingerprint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            content_id VARCHAR(255) NOT NULL,
            content_type VARCHAR(20) NOT NULL CHECK (content_type IN ('audio', 'video', 'image', 'text', 'document', 'mixed')),
            original_filename VARCHAR(500),
            file_size BIGINT NOT NULL,
            mime_type VARCHAR(100),
            
            -- Fingerprint data
            algorithm VARCHAR(50) NOT NULL,
            algorithm_version VARCHAR(20) NOT NULL DEFAULT '1.0',
            fingerprint_hash TEXT NOT NULL,
            vector_embedding BYTEA,
            vector_dimension INTEGER,
            
            -- Quality and performance metrics
            quality_score FLOAT DEFAULT 0.0 CHECK (quality_score >= 0.0 AND quality_score <= 1.0),
            processing_time FLOAT DEFAULT 0.0,
            extraction_timestamp TIMESTAMP DEFAULT NOW(),
            
            -- Content metadata
            duration FLOAT,
            dimensions JSONB,
            encoding_params JSONB,
            content_metadata JSONB,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            is_active BOOLEAN DEFAULT true,
            
            -- Indexes
            UNIQUE(content_id, algorithm),
            INDEX idx_content_fingerprints_user_id (user_id),
            INDEX idx_content_fingerprints_content_type (content_type),
            INDEX idx_content_fingerprints_algorithm (algorithm),
            INDEX idx_content_fingerprints_hash (fingerprint_hash),
            INDEX idx_content_fingerprints_quality (quality_score),
            INDEX idx_content_fingerprints_created (created_at),
            INDEX idx_content_fingerprints_active (is_active)
        );
        
        -- Fingerprint Chunks (for large files)
        CREATE TABLE IF NOT EXISTS fingerprint_chunks (
            chunk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            fingerprint_id UUID NOT NULL REFERENCES content_fingerprints(fingerprint_id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            start_time FLOAT,
            end_time FLOAT,
            chunk_hash TEXT NOT NULL,
            chunk_vector BYTEA,
            
            -- Chunk metadata
            chunk_metadata JSONB,
            processing_time FLOAT DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT NOW(),
            
            -- Indexes
            UNIQUE(fingerprint_id, chunk_index),
            INDEX idx_fingerprint_chunks_fingerprint (fingerprint_id),
            INDEX idx_fingerprint_chunks_time_range (start_time, end_time),
            INDEX idx_fingerprint_chunks_hash (chunk_hash)
        );
        
        -- Similarity Matches
        CREATE TABLE IF NOT EXISTS similarity_matches (
            match_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            source_fingerprint_id UUID NOT NULL REFERENCES content_fingerprints(fingerprint_id) ON DELETE CASCADE,
            target_fingerprint_id UUID NOT NULL REFERENCES content_fingerprints(fingerprint_id) ON DELETE CASCADE,
            
            -- Similarity metrics
            similarity_score FLOAT NOT NULL CHECK (similarity_score >= 0.0 AND similarity_score <= 1.0),
            similarity_metric VARCHAR(20) NOT NULL DEFAULT 'cosine',
            confidence_level FLOAT DEFAULT 0.0,
            
            -- Match details
            algorithm VARCHAR(50) NOT NULL,
            match_regions JSONB,
            processing_time FLOAT DEFAULT 0.0,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            is_verified BOOLEAN DEFAULT false,
            
            -- Indexes
            UNIQUE(source_fingerprint_id, target_fingerprint_id, algorithm),
            INDEX idx_similarity_matches_source (source_fingerprint_id),
            INDEX idx_similarity_matches_target (target_fingerprint_id),
            INDEX idx_similarity_matches_score (similarity_score),
            INDEX idx_similarity_matches_algorithm (algorithm),
            INDEX idx_similarity_matches_created (created_at)
        );
        
        -- Vector Index Mappings (for FAISS)
        CREATE TABLE IF NOT EXISTS vector_index_mappings (
            mapping_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            fingerprint_id UUID NOT NULL REFERENCES content_fingerprints(fingerprint_id) ON DELETE CASCADE,
            algorithm VARCHAR(50) NOT NULL,
            faiss_index_id BIGINT NOT NULL,
            vector_dimension INTEGER NOT NULL,
            index_type VARCHAR(50) DEFAULT 'IVFFlat',
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            
            -- Indexes
            UNIQUE(fingerprint_id, algorithm),
            INDEX idx_vector_mappings_algorithm (algorithm),
            INDEX idx_vector_mappings_faiss_id (faiss_index_id)
        );
        
        -- Content Protection Alerts
        CREATE TABLE IF NOT EXISTS protection_alerts (
            alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            fingerprint_id UUID NOT NULL REFERENCES content_fingerprints(fingerprint_id) ON DELETE CASCADE,
            match_id UUID REFERENCES similarity_matches(match_id) ON DELETE SET NULL,
            
            -- Alert details
            detected_url TEXT NOT NULL,
            platform VARCHAR(100),
            alert_type VARCHAR(50) DEFAULT 'copyright_violation',
            alert_status VARCHAR(20) DEFAULT 'pending' CHECK (alert_status IN ('pending', 'investigating', 'resolved', 'false_positive')),
            
            -- Evidence
            evidence_screenshot TEXT,
            evidence_metadata JSONB,
            detection_method VARCHAR(100),
            
            -- Processing
            similarity_score FLOAT,
            confidence_score FLOAT,
            processing_time FLOAT DEFAULT 0.0,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            resolved_at TIMESTAMP,
            resolved_by UUID,
            
            -- Indexes
            INDEX idx_protection_alerts_fingerprint (fingerprint_id),
            INDEX idx_protection_alerts_status (alert_status),
            INDEX idx_protection_alerts_platform (platform),
            INDEX idx_protection_alerts_created (created_at),
            INDEX idx_protection_alerts_similarity (similarity_score)
        );
        
        -- Performance tracking
        CREATE TABLE IF NOT EXISTS fingerprint_performance_metrics (
            metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            algorithm VARCHAR(50) NOT NULL,
            content_type VARCHAR(20) NOT NULL,
            
            -- Performance metrics
            avg_processing_time FLOAT DEFAULT 0.0,
            total_fingerprints BIGINT DEFAULT 0,
            success_rate FLOAT DEFAULT 0.0,
            avg_quality_score FLOAT DEFAULT 0.0,
            
            -- Time window
            measurement_date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT NOW(),
            
            -- Indexes
            UNIQUE(algorithm, content_type, measurement_date),
            INDEX idx_performance_algorithm (algorithm),
            INDEX idx_performance_content_type (content_type),
            INDEX idx_performance_date (measurement_date)
        );
        
        -- Update timestamp trigger
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        -- Apply triggers
        DROP TRIGGER IF EXISTS update_content_fingerprints_updated_at ON content_fingerprints;
        CREATE TRIGGER update_content_fingerprints_updated_at
            BEFORE UPDATE ON content_fingerprints
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_vector_index_mappings_updated_at ON vector_index_mappings;
        CREATE TRIGGER update_vector_index_mappings_updated_at
            BEFORE UPDATE ON vector_index_mappings
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_protection_alerts_updated_at ON protection_alerts;
        CREATE TRIGGER update_protection_alerts_updated_at
            BEFORE UPDATE ON protection_alerts
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """        
        async with self._db_manager.get_session() as session:
            await session.execute(text(schema_sql))
            await session.commit()
        
        self.logger.debug("✅ Fingerprinting schema created successfully")
    
    async def _initialize_faiss_indices(self):
        """Initialize FAISS indices for vector similarity search"""        self.logger.debug("Initializing FAISS indices...")
        
        try:
            # Create indices for each algorithm that uses vectors
            for algorithm, dimension in self._vector_dimensions.items():
                index_key = f"{algorithm.value}_{dimension}"
                
                # Create IVFFlat index for better performance
                quantizer = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
                index = faiss.IndexIVFFlat(quantizer, dimension, min(100, max(10, dimension // 10)))
                
                # Enable GPU if available
                if faiss.get_num_gpus() > 0:
                    try:
                        index = faiss.index_cpu_to_gpu(faiss.StandardGpuResources(), 0, index)
                        self.logger.debug(f"GPU acceleration enabled for {algorithm.value}")
                    except Exception as e:
                        self.logger.warning(f"GPU acceleration failed for {algorithm.value}: {e}")
                
                self._faiss_indices[index_key] = index
                self.logger.debug(f"Created FAISS index for {algorithm.value} (dimension: {dimension})")
            
            self.logger.debug("✅ FAISS indices initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize FAISS indices: {e}")
            raise
    
    async def _load_existing_fingerprints(self):
        """Load existing fingerprints into FAISS indices"""        self.logger.debug("Loading existing fingerprints into FAISS indices...")
        
        try:
            query = """            SELECT fingerprint_id, algorithm, vector_embedding, vector_dimension
            FROM content_fingerprints 
            WHERE vector_embedding IS NOT NULL AND is_active = true
            ORDER BY created_at
            """            
            async with self._db_manager.get_session() as session:
                result = await session.execute(text(query))
                fingerprints = result.fetchall()
            
            # Group by algorithm
            algorithm_fingerprints = {}
            for fp in fingerprints:
                algorithm = fp.algorithm
                if algorithm not in algorithm_fingerprints:
                    algorithm_fingerprints[algorithm] = []
                algorithm_fingerprints[algorithm].append(fp)
            
            # Load into FAISS indices
            for algorithm, fps in algorithm_fingerprints.items():
                try:
                    algorithm_enum = FingerprintAlgorithm(algorithm)
                    dimension = self._vector_dimensions.get(algorithm_enum)
                    
                    if not dimension:
                        continue
                    
                    index_key = f"{algorithm}_{dimension}"
                    index = self._faiss_indices.get(index_key)
                    
                    if not index:
                        continue
                    
                    # Prepare vectors and IDs
                    vectors = []
                    fp_ids = []
                    
                    for fp in fps:
                        if fp.vector_embedding and fp.vector_dimension == dimension:
                            vector = pickle.loads(fp.vector_embedding)
                            if isinstance(vector, np.ndarray) and vector.shape[0] == dimension:
                                vectors.append(vector)
                                fp_ids.append(fp.fingerprint_id)
                    
                    if vectors:
                        vectors_array = np.array(vectors, dtype=np.float32)
                        
                        # Train index if necessary
                        if not index.is_trained:
                            index.train(vectors_array)
                        
                        # Add vectors to index
                        index.add(vectors_array)
                        
                        # Store mapping
                        await self._store_vector_mappings(fp_ids, algorithm, index_key)
                        
                        self.logger.debug(f"Loaded {len(vectors)} fingerprints for {algorithm}")
                
                except Exception as e:
                    self.logger.error(f"Failed to load fingerprints for {algorithm}: {e}")
            
            self.logger.debug("✅ Existing fingerprints loaded successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load existing fingerprints: {e}")
    
    async def _store_vector_mappings(self, fingerprint_ids: List[str], algorithm: str, index_key: str):
        """Store vector index mappings"""        try:
            mappings = []
            for i, fp_id in enumerate(fingerprint_ids):
                mappings.append({
                    'fingerprint_id': fp_id,
                    'algorithm': algorithm,
                    'faiss_index_id': i,
                    'vector_dimension': self._vector_dimensions.get(FingerprintAlgorithm(algorithm), 0),
                    'index_type': 'IVFFlat'
                })
            
            # Batch insert mappings
            if mappings:
                async with self._db_manager.get_session() as session:
                    await session.execute(
                        text("""                            INSERT INTO vector_index_mappings 
                            (fingerprint_id, algorithm, faiss_index_id, vector_dimension, index_type)
                            VALUES (:fingerprint_id, :algorithm, :faiss_index_id, :vector_dimension, :index_type)
                            ON CONFLICT (fingerprint_id, algorithm) DO UPDATE SET
                                faiss_index_id = EXCLUDED.faiss_index_id,
                                updated_at = NOW()
                        """),
                        mappings
                    )
                    await session.commit()
        
        except Exception as e:
            self.logger.error(f"Failed to store vector mappings: {e}")
    
    async def store_fingerprint(
        self,
        user_id: str,
        content_id: str,
        content_type: ContentType,
        algorithm: FingerprintAlgorithm,
        fingerprint_hash: str,
        vector_embedding: Optional[np.ndarray] = None,
        metadata: Optional[FingerprintMetadata] = None,
        chunks: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """        Store a content fingerprint in the database
        
        Args:
            user_id: User ID who owns the content
            content_id: Unique content identifier
            content_type: Type of content
            algorithm: Fingerprinting algorithm used
            fingerprint_hash: Hash representation of fingerprint
            vector_embedding: Vector representation for similarity search
            metadata: Additional fingerprint metadata
            chunks: Chunk data for large files
        
        Returns:
            Fingerprint ID
        """        try:
            self.logger.debug(f"Storing fingerprint for content {content_id} using {algorithm.value}")
            
            # Prepare fingerprint data
            fingerprint_data = {
                'user_id': user_id,
                'content_id': content_id,
                'content_type': content_type.value,
                'algorithm': algorithm.value,
                'fingerprint_hash': fingerprint_hash,
                'created_at': datetime.utcnow()
            }
            
            # Add metadata if provided
            if metadata:
                fingerprint_data.update({
                    'original_filename': metadata.content_id,
                    'file_size': metadata.file_size,
                    'quality_score': metadata.quality_score,
                    'processing_time': metadata.processing_time,
                    'duration': metadata.duration,
                    'dimensions': json.dumps(metadata.dimensions) if metadata.dimensions else None,
                    'encoding_params': json.dumps(metadata.encoding_params) if metadata.encoding_params else None,
                    'extraction_timestamp': metadata.extraction_timestamp
                })
            
            # Handle vector embedding
            if vector_embedding is not None:
                fingerprint_data['vector_embedding'] = pickle.dumps(vector_embedding)
                fingerprint_data['vector_dimension'] = len(vector_embedding)
            
            # Store in database
            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""                        INSERT INTO content_fingerprints 
                        (user_id, content_id, content_type, algorithm, fingerprint_hash, 
                         vector_embedding, vector_dimension, original_filename, file_size,
                         quality_score, processing_time, duration, dimensions, encoding_params,
                         extraction_timestamp)
                        VALUES (:user_id, :content_id, :content_type, :algorithm, :fingerprint_hash,
                               :vector_embedding, :vector_dimension, :original_filename, :file_size,
                               :quality_score, :processing_time, :duration, :dimensions, :encoding_params,
                               :extraction_timestamp)
                        RETURNING fingerprint_id
                    """),
                    fingerprint_data
                )
                
                fingerprint_id = result.scalar()
                
                # Store chunks if provided
                if chunks:
                    for chunk in chunks:
                        chunk_data = {
                            'fingerprint_id': fingerprint_id,
                            'chunk_index': chunk.get('index'),
                            'start_time': chunk.get('start_time'),
                            'end_time': chunk.get('end_time'),
                            'chunk_hash': chunk.get('hash'),
                            'chunk_vector': pickle.dumps(chunk.get('vector')) if chunk.get('vector') is not None else None,
                            'chunk_metadata': json.dumps(chunk.get('metadata', {})),
                            'processing_time': chunk.get('processing_time', 0.0)
                        }
                        
                        await session.execute(
                            text("""                                INSERT INTO fingerprint_chunks
                                (fingerprint_id, chunk_index, start_time, end_time, chunk_hash,
                                 chunk_vector, chunk_metadata, processing_time)
                                VALUES (:fingerprint_id, :chunk_index, :start_time, :end_time, :chunk_hash,
                                       :chunk_vector, :chunk_metadata, :processing_time)
                            """),
                            chunk_data
                        )
                
                await session.commit()
            
            # Add to FAISS index if vector embedding provided
            if vector_embedding is not None:
                await self._add_to_faiss_index(fingerprint_id, algorithm, vector_embedding)
            
            # Update performance metrics
            await self._update_performance_metrics(algorithm, content_type, metadata)
            
            self.logger.debug(f"✅ Fingerprint stored successfully: {fingerprint_id}")
            return fingerprint_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store fingerprint: {e}")
            raise
    
    async def _add_to_faiss_index(self, fingerprint_id: str, algorithm: FingerprintAlgorithm, vector: np.ndarray):
        """Add vector to FAISS index"""        try:
            dimension = len(vector)
            index_key = f"{algorithm.value}_{dimension}"
            index = self._faiss_indices.get(index_key)
            
            if not index:
                self.logger.warning(f"No FAISS index found for {algorithm.value}")
                return
            
            # Normalize vector for cosine similarity
            vector_normalized = vector / np.linalg.norm(vector)
            vector_array = np.array([vector_normalized], dtype=np.float32)
            
            # Train index if not trained yet
            if not index.is_trained:
                index.train(vector_array)
            
            # Get current index size for mapping
            current_size = index.ntotal
            
            # Add vector to index
            index.add(vector_array)
            
            # Store mapping
            await self._store_vector_mappings([fingerprint_id], algorithm.value, index_key)
            
            self.logger.debug(f"Added fingerprint {fingerprint_id} to FAISS index at position {current_size}")
            
        except Exception as e:
            self.logger.error(f"Failed to add vector to FAISS index: {e}")
    
    async def _update_performance_metrics(
        self, 
        algorithm: FingerprintAlgorithm, 
        content_type: ContentType, 
        metadata: Optional[FingerprintMetadata]
    ):
        """Update performance metrics"""        try:
            if not metadata:
                return
            
            today = datetime.utcnow().date()
            
            async with self._db_manager.get_session() as session:
                await session.execute(
                    text("""                        INSERT INTO fingerprint_performance_metrics 
                        (algorithm, content_type, avg_processing_time, total_fingerprints, 
                         success_rate, avg_quality_score, measurement_date)
                        VALUES (:algorithm, :content_type, :processing_time, 1, 1.0, :quality_score, :date)
                        ON CONFLICT (algorithm, content_type, measurement_date) DO UPDATE SET
                            avg_processing_time = (
                                fingerprint_performance_metrics.avg_processing_time * fingerprint_performance_metrics.total_fingerprints + 
                                EXCLUDED.avg_processing_time
                            ) / (fingerprint_performance_metrics.total_fingerprints + 1),
                            total_fingerprints = fingerprint_performance_metrics.total_fingerprints + 1,
                            avg_quality_score = (
                                fingerprint_performance_metrics.avg_quality_score * fingerprint_performance_metrics.total_fingerprints + 
                                EXCLUDED.avg_quality_score
                            ) / (fingerprint_performance_metrics.total_fingerprints + 1)
                    """),
                    {
                        'algorithm': algorithm.value,
                        'content_type': content_type.value,
                        'processing_time': metadata.processing_time,
                        'quality_score': metadata.quality_score,
                        'date': today
                    }
                )
                await session.commit()
        
        except Exception as e:
            self.logger.error(f"Failed to update performance metrics: {e}")
    
    async def find_similar_content(
        self,
        query_vector: np.ndarray,
        algorithm: FingerprintAlgorithm,
        similarity_threshold: Optional[float] = None,
        max_results: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> List[SimilarityMatch]:
        """        Find similar content using vector similarity search
        
        Args:
            query_vector: Query vector for similarity search
            algorithm: Algorithm used for fingerprinting
            similarity_threshold: Minimum similarity score
            max_results: Maximum number of results
            user_id: Filter by user ID
        
        Returns:
            List of similarity matches
        """        try:
            self.logger.debug(f"Searching for similar content using {algorithm.value}")
            
            threshold = similarity_threshold or self.similarity_threshold
            max_results = max_results or self.max_search_results
            
            dimension = len(query_vector)
            index_key = f"{algorithm.value}_{dimension}"
            index = self._faiss_indices.get(index_key)
            
            if not index or index.ntotal == 0:
                self.logger.warning(f"No FAISS index or no vectors for {algorithm.value}")
                return []
            
            # Normalize query vector
            query_normalized = query_vector / np.linalg.norm(query_vector)
            query_array = np.array([query_normalized], dtype=np.float32)
            
            # Search in FAISS index
            similarities, indices = index.search(query_array, min(max_results * 2, index.ntotal))
            
            # Get fingerprint IDs for matching indices
            matches = []
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if similarity >= threshold and idx != -1:
                    # Get fingerprint ID from mapping
                    async with self._db_manager.get_session() as session:
                        result = await session.execute(
                            text("""                                SELECT vm.fingerprint_id, cf.user_id, cf.content_id, cf.content_type
                                FROM vector_index_mappings vm
                                JOIN content_fingerprints cf ON vm.fingerprint_id = cf.fingerprint_id
                                WHERE vm.algorithm = :algorithm AND vm.faiss_index_id = :index_id
                                AND cf.is_active = true
                            """),
                            {'algorithm': algorithm.value, 'index_id': int(idx)}
                        )
                        
                        fingerprint_data = result.fetchone()
                        
                        if fingerprint_data:
                            # Filter by user if specified
                            if user_id and fingerprint_data.user_id != user_id:
                                continue
                            
                            match = SimilarityMatch(
                                fingerprint_id="",  # Will be set by caller
                                target_fingerprint_id=fingerprint_data.fingerprint_id,
                                similarity_score=float(similarity),
                                algorithm=algorithm,
                                metric=SimilarityMetric.COSINE,
                                confidence_level=min(1.0, similarity * 1.2),
                                processing_time=0.0
                            )
                            matches.append(match)
            
            # Store similarity matches in database
            if matches:
                await self._store_similarity_matches(matches)
            
            self.logger.debug(f"Found {len(matches)} similar content items")
            return matches[:max_results]
            
        except Exception as e:
            self.logger.error(f"❌ Failed to find similar content: {e}")
            return []
    
    async def _store_similarity_matches(self, matches: List[SimilarityMatch]):
        """Store similarity matches in database"""        try:
            match_data = []
            for match in matches:
                match_data.append({
                    'source_fingerprint_id': match.fingerprint_id,
                    'target_fingerprint_id': match.target_fingerprint_id,
                    'similarity_score': match.similarity_score,
                    'similarity_metric': match.metric.value,
                    'algorithm': match.algorithm.value,
                    'confidence_level': match.confidence_level,
                    'processing_time': match.processing_time,
                    'match_regions': json.dumps(match.match_regions) if match.match_regions else None
                })
            
            if match_data:
                async with self._db_manager.get_session() as session:
                    await session.execute(
                        text("""                            INSERT INTO similarity_matches
                            (source_fingerprint_id, target_fingerprint_id, similarity_score,
                             similarity_metric, algorithm, confidence_level, processing_time, match_regions)
                            VALUES (:source_fingerprint_id, :target_fingerprint_id, :similarity_score,
                                   :similarity_metric, :algorithm, :confidence_level, :processing_time, :match_regions)
                            ON CONFLICT (source_fingerprint_id, target_fingerprint_id, algorithm) DO UPDATE SET
                                similarity_score = EXCLUDED.similarity_score,
                                confidence_level = EXCLUDED.confidence_level,
                                processing_time = EXCLUDED.processing_time
                        """),
                        match_data
                    )
                    await session.commit()
        
        except Exception as e:
            self.logger.error(f"Failed to store similarity matches: {e}")
    
    async def get_fingerprint_by_id(self, fingerprint_id: str) -> Optional[Dict[str, Any]]:
        """Get fingerprint by ID"""        try:
            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""                        SELECT * FROM content_fingerprints 
                        WHERE fingerprint_id = :fingerprint_id AND is_active = true
                    """),
                    {'fingerprint_id': fingerprint_id}
                )
                
                fingerprint = result.fetchone()
                
                if fingerprint:
                    # Convert to dict and decode binary data
                    fp_dict = dict(fingerprint._mapping)
                    
                    if fp_dict.get('vector_embedding'):
                        fp_dict['vector_embedding'] = pickle.loads(fp_dict['vector_embedding'])
                    
                    return fp_dict
                
                return None
        
        except Exception as e:
            self.logger.error(f"Failed to get fingerprint by ID: {e}")
            return None
    
    async def get_user_fingerprints(
        self, 
        user_id: str, 
        content_type: Optional[ContentType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get fingerprints for a user"""        try:
            query = """                SELECT fingerprint_id, content_id, content_type, algorithm, 
                       fingerprint_hash, quality_score, processing_time,
                       original_filename, file_size, created_at
                FROM content_fingerprints 
                WHERE user_id = :user_id AND is_active = true
            """            
            params = {'user_id': user_id}
            
            if content_type:
                query += " AND content_type = :content_type"
                params['content_type'] = content_type.value
            
            query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            params.update({'limit': limit, 'offset': offset})
            
            async with self._db_manager.get_session() as session:
                result = await session.execute(text(query), params)
                fingerprints = result.fetchall()
                
                return [dict(fp._mapping) for fp in fingerprints]
        
        except Exception as e:
            self.logger.error(f"Failed to get user fingerprints: {e}")
            return []
    
    async def delete_fingerprint(self, fingerprint_id: str, user_id: str) -> bool:
        """Delete a fingerprint (soft delete)"""        try:
            async with self._db_manager.get_session() as session:
                # Verify ownership
                result = await session.execute(
                    text("SELECT user_id FROM content_fingerprints WHERE fingerprint_id = :fingerprint_id"),
                    {'fingerprint_id': fingerprint_id}
                )
                
                fingerprint = result.fetchone()
                if not fingerprint or fingerprint.user_id != user_id:
                    return False
                
                # Soft delete
                await session.execute(
                    text("""                        UPDATE content_fingerprints 
                        SET is_active = false, updated_at = NOW() 
                        WHERE fingerprint_id = :fingerprint_id
                    """),
                    {'fingerprint_id': fingerprint_id}
                )
                
                await session.commit()
                
                self.logger.debug(f"Fingerprint {fingerprint_id} deleted successfully")
                return True
        
        except Exception as e:
            self.logger.error(f"Failed to delete fingerprint: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""        try:
            health = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'components': {
                    'database': 'healthy',
                    'faiss_indices': 'healthy',
                    'performance': 'healthy'
                },
                'metrics': {
                    'total_fingerprints': 0,
                    'total_indices': len(self._faiss_indices),
                    'cache_size': len(self._fingerprint_cache)
                }
            }
            
            # Check database connectivity
            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    text("SELECT COUNT(*) FROM content_fingerprints WHERE is_active = true")
                )
                health['metrics']['total_fingerprints'] = result.scalar()
            
            # Check FAISS indices
            for index_key, index in self._faiss_indices.items():
                if not index.is_trained and index.ntotal > 0:
                    health['components']['faiss_indices'] = 'warning'
                    health['status'] = 'warning'
            
            return health
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""        try:
            async with self._db_manager.get_session() as session:
                # Overall stats
                result = await session.execute(text("""                    SELECT 
                        COUNT(*) as total_fingerprints,
                        COUNT(DISTINCT user_id) as unique_users,
                        COUNT(DISTINCT content_type) as content_types,
                        COUNT(DISTINCT algorithm) as algorithms_used,
                        AVG(quality_score) as avg_quality,
                        AVG(processing_time) as avg_processing_time
                    FROM content_fingerprints 
                    WHERE is_active = true
                """))
                
                overall_stats = dict(result.fetchone()._mapping)
                
                # Performance by algorithm
                result = await session.execute(text("""                    SELECT algorithm, content_type, 
                           AVG(processing_time) as avg_time,
                           AVG(quality_score) as avg_quality,
                           COUNT(*) as total_count
                    FROM content_fingerprints 
                    WHERE is_active = true
                    GROUP BY algorithm, content_type
                    ORDER BY algorithm, content_type
                """))
                
                algorithm_stats = [dict(row._mapping) for row in result.fetchall()]
                
                # Recent activity
                result = await session.execute(text("""                    SELECT DATE(created_at) as date, COUNT(*) as fingerprints_created
                    FROM content_fingerprints 
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                """))
                
                recent_activity = [dict(row._mapping) for row in result.fetchall()]
                
                return {
                    'overall': overall_stats,
                    'by_algorithm': algorithm_stats,
                    'recent_activity': recent_activity,
                    'faiss_stats': {
                        'total_indices': len(self._faiss_indices),
                        'trained_indices': sum(1 for idx in self._faiss_indices.values() if idx.is_trained),
                        'total_vectors': sum(idx.ntotal for idx in self._faiss_indices.values())
                    },
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            self.logger.error(f"Failed to get performance stats: {e}")
            return {'error': str(e)}
    
    async def shutdown(self):
        """Shutdown the fingerprinting manager"""        try:
            self.logger.info("🚨 Shutting down Content Fingerprinting Manager...")
            
            # Clear caches
            self._fingerprint_cache.clear()
            
            # Save FAISS indices if needed
            for index_key, index in self._faiss_indices.items():
                try:
                    # Could save indices to disk here for persistence
                    pass
                except Exception as e:
                    self.logger.error(f"Failed to save FAISS index {index_key}: {e}")
            
            self._faiss_indices.clear()
            
            self.logger.info("✅ Content Fingerprinting Manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Shutdown failed: {e}")


# Factory function
_content_fingerprinting_manager: Optional[ContentFingerprintingManager] = None


def get_content_fingerprinting_manager(config: Optional[Dict[str, Any]] = None) -> ContentFingerprintingManager:
    """Get or create content fingerprinting manager instance"""    global _content_fingerprinting_manager
    
    if _content_fingerprinting_manager is None:
        _content_fingerprinting_manager = ContentFingerprintingManager(config)
    
    return _content_fingerprinting_manager
