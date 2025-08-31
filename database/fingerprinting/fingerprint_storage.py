"""Enterprise-Grade Fingerprint Storage Manager

Ultra-advanced database storage system for content fingerprints with industrial-strength
optimization, multi-modal vector storage, real-time indexing, and comprehensive security.

Industry Features:
- Multi-modal fingerprint storage (audio, video, image, text)
- Advanced vector embedding management with FAISS integration
- Real-time compression and encryption
- Intelligent storage partitioning and sharding
- Performance-optimized batch operations
- Comprehensive audit trails and compliance
- Advanced caching and retrieval optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Project: IA Influencer Agent + Content Protection Platform

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, modification, or distribution is strictly prohibited
and will result in immediate legal action under German and international law.
All violators will be prosecuted to the full extent of the law.

Development Team Specialties:
- Lead AI Developer: Advanced ML/NLP systems
- Senior Backend Engineer: Scalable microservices architecture  
- ML Engineer: Deep learning and neural network optimization
- Database Architect: Enterprise database design and optimization
- Security Engineer: Cryptography and data protection
- Microservices Specialist: Distributed systems and APIs
- Audio Engineer: Advanced audio processing and analysis
- DevOps Engineer: Infrastructure automation and monitoring
"""
import asyncio
import hashlib
import json
import logging
import uuid
import zlib
import pickle
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple, Set, AsyncIterator
from dataclasses import asdict, dataclass
from contextlib import asynccontextmanager
from enum import Enum
import struct

import numpy as np
import psycopg2
from sqlalchemy import (
    Column, String, DateTime, Text, LargeBinary, JSON, Float, Integer,
    Boolean, Index, UniqueConstraint, ForeignKey, and_, or_, text, desc, asc
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.dialects.postgresql import UUID, BYTEA, JSONB, ARRAY
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func, select, insert, update, delete, exists
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.pool import QueuePool

from backend.core.database import DatabaseManager
from backend.core.config import settings
from backend.core.exceptions import DatabaseError, ValidationError
from backend.utils.performance import PerformanceMonitor
from backend.utils.encryption import EncryptionManager
from backend.utils.compression import CompressionManager

logger = logging.getLogger(__name__)

Base = declarative_base()


class ContentType(Enum):
    """Content type enumeration for fingerprinting"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MIXED = "mixed"


class FingerprintAlgorithm(Enum):
    """Fingerprinting algorithm types"""    PERCEPTUAL = "perceptual"
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    CHROMAPRINT = "chromaprint"
    PHASH = "phash"
    CLIP = "clip"
    BERT = "bert"


class StorageStatus(Enum):
    """Storage status enumeration"""    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    CORRUPTED = "corrupted"
    PROCESSING = "processing"
    FAILED = "failed"


@dataclass
class FingerprintMetrics:
    """Performance metrics for fingerprint storage"""    storage_size: int
    compression_ratio: float
    encryption_overhead: float
    retrieval_time: float
    confidence_score: float
    quality_score: float


@dataclass
class StorageConfiguration:
    """Configuration for fingerprint storage"""    compression_enabled: bool = True
    encryption_enabled: bool = True
    vector_storage: bool = True
    auto_cleanup: bool = True
    retention_days: int = 365
    batch_size: int = 1000
    max_storage_mb: int = 1000


class FingerprintStorageModel(Base):
    """Enterprise SQLAlchemy model for fingerprint storage with advanced features"""    __tablename__ = "content_fingerprints_v2"
    
    # Primary identification
    fingerprint_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(255), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Content classification
    content_type = Column(String(50), nullable=False, index=True)
    fingerprint_algorithm = Column(String(50), nullable=False, index=True)
    quality_level = Column(String(20), nullable=False, default="standard")
    source_platform = Column(String(100), nullable=True, index=True)
    
    # Primary fingerprint hashes
    primary_hash = Column(String(255), nullable=False, index=True)
    perceptual_hash = Column(String(255), nullable=True, index=True)
    structural_hash = Column(String(255), nullable=True, index=True)
    semantic_hash = Column(String(255), nullable=True, index=True)
    
    # Secondary hashes for matching
    chromaprint_hash = Column(String(500), nullable=True, index=True)
    phash_signature = Column(String(255), nullable=True, index=True)
    dhash_signature = Column(String(255), nullable=True, index=True)
    wavelet_hash = Column(String(255), nullable=True, index=True)
    
    # Advanced vector data (compressed and encrypted)
    feature_vector = Column(BYTEA, nullable=True)
    embedding_vector = Column(BYTEA, nullable=True)
    spectral_features = Column(BYTEA, nullable=True)
    temporal_features = Column(BYTEA, nullable=True)
    
    # Vector dimensions and metadata
    vector_dimensions = Column(Integer, nullable=True)
    vector_type = Column(String(50), nullable=True)
    vector_model = Column(String(100), nullable=True)
    
    # Comprehensive metadata
    content_metadata = Column(JSONB, nullable=True)
    extraction_metadata = Column(JSONB, nullable=True)
    quality_metrics = Column(JSONB, nullable=True)
    processing_metrics = Column(JSONB, nullable=True)
    
    # File and content properties
    original_filename = Column(String(500), nullable=True)
    file_extension = Column(String(20), nullable=True)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Storage optimization
    compression_algorithm = Column(String(50), nullable=True)
    compression_ratio = Column(Float, nullable=True)
    encryption_algorithm = Column(String(50), nullable=True)
    storage_location = Column(String(255), nullable=True)
    
    # Performance and quality scores
    confidence_score = Column(Float, nullable=False, default=0.0)
    quality_score = Column(Float, nullable=False, default=0.0)
    processing_time = Column(Float, nullable=True)
    storage_size = Column(Integer, nullable=True)
    
    # Status and lifecycle management
    status = Column(String(20), nullable=False, default="active")
    is_encrypted = Column(Boolean, nullable=False, default=True)
    is_compressed = Column(Boolean, nullable=False, default=True)
    is_indexed = Column(Boolean, nullable=False, default=False)
    
    # Version control
    version = Column(Integer, nullable=False, default=1)
    parent_fingerprint_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Access tracking
    access_count = Column(Integer, nullable=False, default=0)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    last_matched = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps with timezone
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    matches = relationship("FingerprintMatchModel", back_populates="fingerprint", lazy="dynamic")
    versions = relationship("FingerprintVersionModel", back_populates="fingerprint", lazy="dynamic")
    
    # Advanced indexing for ultra-performance
    __table_args__ = (
        Index('idx_fp_composite_main', 'content_type', 'fingerprint_algorithm', 'status'),
        Index('idx_fp_user_tenant', 'user_id', 'tenant_id', 'status'),
        Index('idx_fp_content_lookup', 'content_id', 'status'),
        Index('idx_fp_temporal_range', 'created_at', 'expires_at'),
        Index('idx_fp_quality_performance', 'quality_score', 'confidence_score'),
        Index('idx_fp_platform_type', 'source_platform', 'content_type'),
        Index('idx_fp_version_tree', 'parent_fingerprint_id', 'version'),
        Index('idx_fp_hash_lookup', 'primary_hash'),
        Index('idx_fp_perceptual_search', 'perceptual_hash'),
        Index('idx_fp_semantic_search', 'semantic_hash'),
        UniqueConstraint('content_id', 'fingerprint_algorithm', 'version', name='uq_content_algorithm_version'),
    )


class FingerprintVersionModel(Base):
    """Version tracking for fingerprint evolution"""    __tablename__ = "fingerprint_versions"
    
    version_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fingerprint_id = Column(UUID(as_uuid=True), ForeignKey('content_fingerprints_v2.fingerprint_id'), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    change_type = Column(String(50), nullable=False)  # created, updated, reprocessed, archived
    change_reason = Column(Text, nullable=True)
    performance_delta = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Relationship
    fingerprint = relationship("FingerprintStorageModel", back_populates="versions")
    
    __table_args__ = (
        Index('idx_fp_version_tracking', 'fingerprint_id', 'version_number'),
        UniqueConstraint('fingerprint_id', 'version_number', name='uq_fingerprint_version'),
    )


class FingerprintStorageManager:
    """    Ultra-Advanced Enterprise Fingerprint Storage Manager
    
    Industrial-strength storage system with:
    - Multi-modal content fingerprint storage
    - Advanced vector embedding management
    - Real-time compression and encryption
    - Intelligent batch processing
    - Performance optimization and monitoring
    - Comprehensive audit trails
    """    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.encryption_manager = EncryptionManager()
        self.compression_manager = CompressionManager()
        self.performance_monitor = PerformanceMonitor()
        self.logger = logging.getLogger(__name__)
        self.config = StorageConfiguration()
        
        # Performance caches
        self._vector_cache = {}
        self._hash_cache = {}
        self._metadata_cache = {}
        
        # Statistics tracking
        self.stats = {
            'total_stored': 0,
            'total_retrieved': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'compression_savings': 0,
            'average_storage_time': 0,
            'average_retrieval_time': 0
        }
    
    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        """Get async database session with comprehensive error handling"""        session = None
        try:
            session = await self.db_manager.get_async_session()
            yield session
            await session.commit()
        except Exception as e:
            if session:
                await session.rollback()
            self.logger.error(f"Database session error: {str(e)}")
            raise DatabaseError(f"Storage operation failed: {str(e)}")
        finally:
            if session:
                await session.close()
    
    async def store_fingerprint(
        self,
        content_id: str,
        user_id: str,
        tenant_id: str,
        content_type: ContentType,
        fingerprint_data: Dict[str, Any],
        vector_data: Optional[np.ndarray] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """        Store content fingerprint with advanced optimization
        
        Args:
            content_id: Unique content identifier
            user_id: User UUID
            tenant_id: Tenant UUID for multi-tenancy
            content_type: Type of content being fingerprinted
            fingerprint_data: Extracted fingerprint hashes and signatures
            vector_data: High-dimensional feature vectors
            metadata: Additional content metadata
            
        Returns:
            fingerprint_id: Unique fingerprint identifier
        """        start_time = datetime.now()
        
        try:
            async with self.get_session() as session:
                # Generate fingerprint ID
                fingerprint_id = str(uuid.uuid4())
                
                # Process and optimize vector data
                processed_vector = await self._process_vector_data(vector_data)
                
                # Compress metadata if enabled
                compressed_metadata = await self._compress_metadata(metadata)
                
                # Create fingerprint model
                fingerprint = FingerprintStorageModel(
                    fingerprint_id=fingerprint_id,
                    content_id=content_id,
                    user_id=user_id,
                    tenant_id=tenant_id,
                    content_type=content_type.value,
                    fingerprint_algorithm=fingerprint_data.get('algorithm', 'hybrid'),
                    primary_hash=fingerprint_data.get('primary_hash'),
                    perceptual_hash=fingerprint_data.get('perceptual_hash'),
                    structural_hash=fingerprint_data.get('structural_hash'),
                    semantic_hash=fingerprint_data.get('semantic_hash'),
                    chromaprint_hash=fingerprint_data.get('chromaprint_hash'),
                    phash_signature=fingerprint_data.get('phash_signature'),
                    feature_vector=processed_vector.get('feature_vector') if processed_vector else None,
                    embedding_vector=processed_vector.get('embedding_vector') if processed_vector else None,
                    vector_dimensions=processed_vector.get('dimensions') if processed_vector else None,
                    vector_type=processed_vector.get('type') if processed_vector else None,
                    content_metadata=compressed_metadata,
                    quality_score=fingerprint_data.get('quality_score', 0.0),
                    confidence_score=fingerprint_data.get('confidence_score', 0.0),
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    source_platform=metadata.get('platform') if metadata else None,
                    original_filename=metadata.get('filename') if metadata else None,
                    file_size=metadata.get('file_size') if metadata else None
                )
                
                session.add(fingerprint)
                await session.flush()
                
                # Create version record
                await self._create_version_record(session, fingerprint_id, 1, "created", "Initial fingerprint creation")
                
                # Update statistics
                self._update_storage_stats(start_time)
                
                self.logger.info(f"Successfully stored fingerprint {fingerprint_id} for content {content_id}")
                return fingerprint_id
                
        except Exception as e:
            self.logger.error(f"Failed to store fingerprint for content {content_id}: {str(e)}")
            raise DatabaseError(f"Fingerprint storage failed: {str(e)}")
    
    async def retrieve_fingerprint(
        self,
        fingerprint_id: str,
        include_vectors: bool = True,
        decompress_metadata: bool = True
    ) -> Optional[Dict[str, Any]]:
        """        Retrieve fingerprint with advanced caching and optimization
        
        Args:
            fingerprint_id: Unique fingerprint identifier
            include_vectors: Whether to include vector data
            decompress_metadata: Whether to decompress metadata
            
        Returns:
            Complete fingerprint data or None if not found
        """        start_time = datetime.now()
        
        # Check cache first
        cache_key = f"fingerprint:{fingerprint_id}:{include_vectors}"
        if cache_key in self._vector_cache:
            self.stats['cache_hits'] += 1
            return self._vector_cache[cache_key]
        
        try:
            async with self.get_session() as session:
                # Optimized query with selective loading
                query = select(FingerprintStorageModel).where(
                    FingerprintStorageModel.fingerprint_id == fingerprint_id
                )
                
                result = await session.execute(query)
                fingerprint = result.scalar_one_or_none()
                
                if not fingerprint:
                    return None
                
                # Process fingerprint data
                fingerprint_data = await self._process_fingerprint_for_retrieval(
                    fingerprint, include_vectors, decompress_metadata
                )
                
                # Update access tracking
                await self._update_access_tracking(session, fingerprint_id)
                
                # Cache the result
                self._vector_cache[cache_key] = fingerprint_data
                self.stats['cache_misses'] += 1
                
                # Update statistics
                self._update_retrieval_stats(start_time)
                
                return fingerprint_data
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve fingerprint {fingerprint_id}: {str(e)}")
            raise DatabaseError(f"Fingerprint retrieval failed: {str(e)}")
    
    async def batch_store_fingerprints(
        self,
        fingerprints: List[Dict[str, Any]]
    ) -> List[str]:
        """        Batch store multiple fingerprints with optimized performance
        
        Args:
            fingerprints: List of fingerprint data dictionaries
            
        Returns:
            List of generated fingerprint IDs
        """        if not fingerprints:
            return []
        
        start_time = datetime.now()
        fingerprint_ids = []
        
        try:
            async with self.get_session() as session:
                # Process fingerprints in batches
                batch_size = self.config.batch_size
                
                for i in range(0, len(fingerprints), batch_size):
                    batch = fingerprints[i:i + batch_size]
                    batch_ids = await self._process_fingerprint_batch(session, batch)
                    fingerprint_ids.extend(batch_ids)
                
                self.logger.info(f"Successfully batch stored {len(fingerprint_ids)} fingerprints")
                return fingerprint_ids
                
        except Exception as e:
            self.logger.error(f"Failed to batch store fingerprints: {str(e)}")
            raise DatabaseError(f"Batch storage failed: {str(e)}")
    
    async def search_similar_fingerprints(
        self,
        query_hash: str,
        content_type: ContentType,
        similarity_threshold: float = 0.8,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """        Search for similar fingerprints using advanced matching algorithms
        
        Args:
            query_hash: Hash to search for
            content_type: Type of content
            similarity_threshold: Minimum similarity score
            max_results: Maximum number of results
            
        Returns:
            List of similar fingerprints with similarity scores
        """        try:
            async with self.get_session() as session:
                # Multi-hash similarity search
                query = select(FingerprintStorageModel).where(
                    and_(
                        FingerprintStorageModel.content_type == content_type.value,
                        FingerprintStorageModel.status == StorageStatus.ACTIVE.value,
                        or_(
                            FingerprintStorageModel.primary_hash.like(f"%{query_hash[:16]}%"),
                            FingerprintStorageModel.perceptual_hash.like(f"%{query_hash[:16]}%"),
                            FingerprintStorageModel.structural_hash.like(f"%{query_hash[:16]}%")
                        )
                    )
                ).limit(max_results)
                
                result = await session.execute(query)
                fingerprints = result.scalars().all()
                
                # Calculate similarity scores
                similar_fingerprints = []
                for fingerprint in fingerprints:
                    similarity_score = await self._calculate_similarity(
                        query_hash, fingerprint
                    )
                    
                    if similarity_score >= similarity_threshold:
                        similar_fingerprints.append({
                            'fingerprint_id': str(fingerprint.fingerprint_id),
                            'content_id': fingerprint.content_id,
                            'similarity_score': similarity_score,
                            'confidence_score': fingerprint.confidence_score,
                            'created_at': fingerprint.created_at
                        })
                
                # Sort by similarity score
                similar_fingerprints.sort(key=lambda x: x['similarity_score'], reverse=True)
                
                return similar_fingerprints
                
        except Exception as e:
            self.logger.error(f"Failed to search similar fingerprints: {str(e)}")
            raise DatabaseError(f"Similarity search failed: {str(e)}")
    
    async def update_fingerprint_metadata(
        self,
        fingerprint_id: str,
        metadata_updates: Dict[str, Any]
    ) -> bool:
        """        Update fingerprint metadata with version tracking
        
        Args:
            fingerprint_id: Unique fingerprint identifier
            metadata_updates: Dictionary of metadata updates
            
        Returns:
            Success status
        """        try:
            async with self.get_session() as session:
                query = select(FingerprintStorageModel).where(
                    FingerprintStorageModel.fingerprint_id == fingerprint_id
                )
                
                result = await session.execute(query)
                fingerprint = result.scalar_one_or_none()
                
                if not fingerprint:
                    return False
                
                # Update metadata
                if fingerprint.content_metadata:
                    fingerprint.content_metadata.update(metadata_updates)
                else:
                    fingerprint.content_metadata = metadata_updates
                
                # Increment version
                fingerprint.version += 1
                fingerprint.updated_at = datetime.now(timezone.utc)
                
                # Create version record
                await self._create_version_record(
                    session, fingerprint_id, fingerprint.version, "updated", 
                    "Metadata update"
                )
                
                # Invalidate cache
                self._invalidate_fingerprint_cache(fingerprint_id)
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update fingerprint metadata {fingerprint_id}: {str(e)}")
            raise DatabaseError(f"Metadata update failed: {str(e)}")
    
    async def archive_fingerprint(
        self,
        fingerprint_id: str,
        archive_reason: str = "User requested"
    ) -> bool:
        """        Archive fingerprint while preserving data for audit trails
        
        Args:
            fingerprint_id: Unique fingerprint identifier
            archive_reason: Reason for archiving
            
        Returns:
            Success status
        """        try:
            async with self.get_session() as session:
                query = update(FingerprintStorageModel).where(
                    FingerprintStorageModel.fingerprint_id == fingerprint_id
                ).values(
                    status=StorageStatus.ARCHIVED.value,
                    archived_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                
                result = await session.execute(query)
                
                if result.rowcount > 0:
                    # Create version record
                    await self._create_version_record(
                        session, fingerprint_id, None, "archived", archive_reason
                    )
                    
                    # Invalidate cache
                    self._invalidate_fingerprint_cache(fingerprint_id)
                    
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to archive fingerprint {fingerprint_id}: {str(e)}")
            raise DatabaseError(f"Archive operation failed: {str(e)}")
    
    async def get_storage_statistics(self) -> Dict[str, Any]:
        """        Get comprehensive storage statistics and performance metrics
        
        Returns:
            Dictionary containing storage statistics
        """        try:
            async with self.get_session() as session:
                # Count fingerprints by type and status
                type_counts = await session.execute(
                    select(
                        FingerprintStorageModel.content_type,
                        FingerprintStorageModel.status,
                        func.count().label('count')
                    ).group_by(
                        FingerprintStorageModel.content_type,
                        FingerprintStorageModel.status
                    )
                )
                
                # Calculate storage usage
                storage_usage = await session.execute(
                    select(
                        func.sum(FingerprintStorageModel.storage_size).label('total_size'),
                        func.avg(FingerprintStorageModel.storage_size).label('avg_size'),
                        func.count().label('total_count')
                    ).where(
                        FingerprintStorageModel.status == StorageStatus.ACTIVE.value
                    )
                )
                
                # Get performance metrics
                performance_metrics = await session.execute(
                    select(
                        func.avg(FingerprintStorageModel.processing_time).label('avg_processing_time'),
                        func.avg(FingerprintStorageModel.confidence_score).label('avg_confidence'),
                        func.avg(FingerprintStorageModel.quality_score).label('avg_quality')
                    ).where(
                        FingerprintStorageModel.status == StorageStatus.ACTIVE.value
                    )
                )
                
                # Compile statistics
                statistics = {
                    'runtime_stats': self.stats,
                    'type_distribution': {row.content_type: row.count for row in type_counts},
                    'storage_usage': dict(storage_usage.first()._asdict()),
                    'performance_metrics': dict(performance_metrics.first()._asdict()),
                    'cache_efficiency': {
                        'hit_ratio': self.stats['cache_hits'] / max(1, self.stats['cache_hits'] + self.stats['cache_misses']),
                        'cache_size': len(self._vector_cache)
                    }
                }
                
                return statistics
                
        except Exception as e:
            self.logger.error(f"Failed to get storage statistics: {str(e)}")
            raise DatabaseError(f"Statistics retrieval failed: {str(e)}")
    
    # Private helper methods
    
    async def _process_vector_data(self, vector_data: Optional[np.ndarray]) -> Optional[Dict[str, Any]]:
        """Process and optimize vector data for storage"""        if vector_data is None:
            return None
        
        try:
            # Compress vector data
            compressed_vector = self.compression_manager.compress_vector(vector_data)
            
            # Encrypt if configured
            if self.config.encryption_enabled:
                encrypted_vector = self.encryption_manager.encrypt_data(compressed_vector)
            else:
                encrypted_vector = compressed_vector
            
            return {
                'feature_vector': encrypted_vector,
                'dimensions': vector_data.shape[0] if vector_data.ndim == 1 else vector_data.shape,
                'type': str(vector_data.dtype),
                'compression_ratio': len(compressed_vector) / vector_data.nbytes
            }
            
        except Exception as e:
            self.logger.error(f"Vector processing error: {str(e)}")
            return None
    
    async def _compress_metadata(self, metadata: Optional[Dict[str, Any]]) -> Optional[bytes]:
        """Compress metadata for efficient storage"""        if not metadata or not self.config.compression_enabled:
            return metadata
        
        try:
            serialized = json.dumps(metadata, ensure_ascii=False)
            compressed = zlib.compress(serialized.encode('utf-8'))
            return compressed
        except Exception as e:
            self.logger.error(f"Metadata compression error: {str(e)}")
            return metadata
    
    async def _create_version_record(
        self,
        session: AsyncSession,
        fingerprint_id: str,
        version_number: Optional[int],
        change_type: str,
        change_reason: str
    ):
        """Create version tracking record"""        try:
            version_record = FingerprintVersionModel(
                fingerprint_id=fingerprint_id,
                version_number=version_number or 1,
                change_type=change_type,
                change_reason=change_reason
            )
            session.add(version_record)
            await session.flush()
        except Exception as e:
            self.logger.error(f"Version record creation error: {str(e)}")
    
    async def _process_fingerprint_for_retrieval(
        self,
        fingerprint: FingerprintStorageModel,
        include_vectors: bool,
        decompress_metadata: bool
    ) -> Dict[str, Any]:
        """Process fingerprint data for retrieval optimization"""        data = {
            'fingerprint_id': str(fingerprint.fingerprint_id),
            'content_id': fingerprint.content_id,
            'user_id': str(fingerprint.user_id),
            'content_type': fingerprint.content_type,
            'fingerprint_algorithm': fingerprint.fingerprint_algorithm,
            'primary_hash': fingerprint.primary_hash,
            'perceptual_hash': fingerprint.perceptual_hash,
            'structural_hash': fingerprint.structural_hash,
            'semantic_hash': fingerprint.semantic_hash,
            'quality_score': fingerprint.quality_score,
            'confidence_score': fingerprint.confidence_score,
            'created_at': fingerprint.created_at,
            'updated_at': fingerprint.updated_at,
            'status': fingerprint.status
        }
        
        # Include vector data if requested
        if include_vectors and fingerprint.feature_vector:
            try:
                # Decrypt and decompress vector data
                decrypted_vector = self.encryption_manager.decrypt_data(fingerprint.feature_vector)
                decompressed_vector = self.compression_manager.decompress_vector(decrypted_vector)
                data['feature_vector'] = decompressed_vector.tolist()
            except Exception as e:
                self.logger.error(f"Vector decompression error: {str(e)}")
        
        # Decompress metadata if requested
        if decompress_metadata and fingerprint.content_metadata:
            try:
                if isinstance(fingerprint.content_metadata, bytes):
                    decompressed = zlib.decompress(fingerprint.content_metadata)
                    data['metadata'] = json.loads(decompressed.decode('utf-8'))
                else:
                    data['metadata'] = fingerprint.content_metadata
            except Exception as e:
                self.logger.error(f"Metadata decompression error: {str(e)}")
                data['metadata'] = fingerprint.content_metadata
        
        return data
    
    async def _update_access_tracking(self, session: AsyncSession, fingerprint_id: str):
        """Update access tracking for fingerprint"""        try:
            await session.execute(
                update(FingerprintStorageModel)
                .where(FingerprintStorageModel.fingerprint_id == fingerprint_id)
                .values(
                    access_count=FingerprintStorageModel.access_count + 1,
                    last_accessed=datetime.now(timezone.utc)
                )
            )
        except Exception as e:
            self.logger.error(f"Access tracking update error: {str(e)}")
    
    async def _process_fingerprint_batch(
        self,
        session: AsyncSession,
        batch: List[Dict[str, Any]]
    ) -> List[str]:
        """Process a batch of fingerprints for optimized storage"""        fingerprint_ids = []
        
        for fingerprint_data in batch:
            fingerprint_id = str(uuid.uuid4())
            fingerprint_ids.append(fingerprint_id)
            
            # Create optimized fingerprint model
            fingerprint = FingerprintStorageModel(
                fingerprint_id=fingerprint_id,
                **fingerprint_data
            )
            session.add(fingerprint)
        
        await session.flush()
        return fingerprint_ids
    
    async def _calculate_similarity(
        self,
        query_hash: str,
        fingerprint: FingerprintStorageModel
    ) -> float:
        """Calculate similarity score between hashes"""        try:
            # Implement sophisticated similarity calculation
            # This is a simplified version - real implementation would use
            # advanced algorithms like Hamming distance, Jaccard similarity, etc.
            
            similarity_scores = []
            
            # Compare primary hash
            if fingerprint.primary_hash:
                similarity_scores.append(self._hash_similarity(query_hash, fingerprint.primary_hash))
            
            # Compare perceptual hash
            if fingerprint.perceptual_hash:
                similarity_scores.append(self._hash_similarity(query_hash, fingerprint.perceptual_hash))
            
            # Return highest similarity
            return max(similarity_scores) if similarity_scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Similarity calculation error: {str(e)}")
            return 0.0
    
    def _hash_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity between two hashes"""        if not hash1 or not hash2:
            return 0.0
        
        # Simple Hamming distance for demonstration
        # Real implementation would use more sophisticated algorithms
        common_chars = sum(c1 == c2 for c1, c2 in zip(hash1, hash2))
        max_length = max(len(hash1), len(hash2))
        
        return common_chars / max_length if max_length > 0 else 0.0
    
    def _update_storage_stats(self, start_time: datetime):
        """Update storage performance statistics"""        processing_time = (datetime.now() - start_time).total_seconds()
        self.stats['total_stored'] += 1
        self.stats['average_storage_time'] = (
            (self.stats['average_storage_time'] * (self.stats['total_stored'] - 1) + processing_time) /
            self.stats['total_stored']
        )
    
    def _update_retrieval_stats(self, start_time: datetime):
        """Update retrieval performance statistics"""        processing_time = (datetime.now() - start_time).total_seconds()
        self.stats['total_retrieved'] += 1
        self.stats['average_retrieval_time'] = (
            (self.stats['average_retrieval_time'] * (self.stats['total_retrieved'] - 1) + processing_time) /
            self.stats['total_retrieved']
        )
    
    def _invalidate_fingerprint_cache(self, fingerprint_id: str):
        """Invalidate cache entries for a specific fingerprint"""        keys_to_remove = [key for key in self._vector_cache.keys() if fingerprint_id in key]
        for key in keys_to_remove:
            del self._vector_cache[key]
    
    async def cleanup_expired_fingerprints(self) -> int:
        """        Clean up expired fingerprints and optimize storage
        
        Returns:
            Number of fingerprints cleaned up
        """        try:
            async with self.get_session() as session:
                # Find expired fingerprints
                current_time = datetime.now(timezone.utc)
                
                expired_query = select(FingerprintStorageModel).where(
                    and_(
                        FingerprintStorageModel.expires_at < current_time,
                        FingerprintStorageModel.status == StorageStatus.ACTIVE.value
                    )
                )
                
                result = await session.execute(expired_query)
                expired_fingerprints = result.scalars().all()
                
                # Archive expired fingerprints
                cleanup_count = 0
                for fingerprint in expired_fingerprints:
                    await self.archive_fingerprint(
                        str(fingerprint.fingerprint_id), 
                        "Automatic cleanup - expired"
                    )
                    cleanup_count += 1
                
                self.logger.info(f"Cleaned up {cleanup_count} expired fingerprints")
                return cleanup_count
                
        except Exception as e:
            self.logger.error(f"Cleanup operation failed: {str(e)}")
            raise DatabaseError(f"Cleanup failed: {str(e)}")


# Export for module initialization
__all__ = [
    "FingerprintStorageManager",
    "FingerprintStorageModel", 
    "FingerprintVersionModel",
    "ContentType",
    "FingerprintAlgorithm",
    "StorageStatus",
    "FingerprintMetrics",
    "StorageConfiguration"
]
        
        # Storage configuration
        self.max_vector_size = 10000  # Maximum vector size for storage
        self.compression_threshold = 1024  # Compress vectors larger than this
        self.encryption_enabled = settings.FINGERPRINT_ENCRYPTION_ENABLED
        
        # Performance caching
        self._storage_cache = {}
        self._cache_ttl = 300  # 5 minutes
        
    async def store_fingerprint(
        self,
        fingerprint: ContentFingerprint,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """        Store content fingerprint with enterprise-grade optimization
        
        Args:
            fingerprint: ContentFingerprint object to store
            user_id: User identifier for multi-tenant support
            metadata: Additional metadata for storage
            
        Returns:
            str: Stored fingerprint ID
            
        Raises:
            DatabaseError: Storage operation failed
            ValidationError: Invalid fingerprint data
        """        start_time = datetime.now()
        
        try:
            # Validate fingerprint data
            self._validate_fingerprint(fingerprint)
            
            # Prepare storage data
            storage_data = await self._prepare_storage_data(fingerprint, user_id, metadata)
            
            # Store with transaction safety
            async with self.db_manager.get_session() as session:
                storage_model = FingerprintStorageModel(**storage_data)
                session.add(storage_model)
                await session.commit()
                
                fingerprint_id = str(storage_model.fingerprint_id)
                
                # Update performance metrics
                processing_time = (datetime.now() - start_time).total_seconds()
                await self._update_performance_metrics(session, fingerprint_id, processing_time)
                
                self.logger.info(f"Stored fingerprint {fingerprint_id} for user {user_id}")
                return fingerprint_id
                
        except IntegrityError as e:
            self.logger.error(f"Integrity error storing fingerprint: {e}")
            raise DatabaseError(f"Fingerprint already exists: {e}")
        except SQLAlchemyError as e:
            self.logger.error(f"Database error storing fingerprint: {e}")
            raise DatabaseError(f"Storage failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error storing fingerprint: {e}")
            raise DatabaseError(f"Unexpected storage error: {e}")
    
    async def retrieve_fingerprint(
        self,
        fingerprint_id: str,
        include_vectors: bool = True
    ) -> Optional[ContentFingerprint]:
        """        Retrieve fingerprint by ID with optional vector data
        
        Args:
            fingerprint_id: Fingerprint identifier
            include_vectors: Whether to include vector data
            
        Returns:
            ContentFingerprint object or None if not found
        """        try:
            async with self.db_manager.get_session() as session:
                query = select(FingerprintStorageModel).where(
                    FingerprintStorageModel.fingerprint_id == fingerprint_id
                )
                result = await session.execute(query)
                model = result.scalar_one_or_none()
                
                if not model:
                    return None
                
                # Update last accessed time
                await self._update_access_time(session, fingerprint_id)
                
                # Convert to ContentFingerprint
                return await self._model_to_fingerprint(model, include_vectors)
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error retrieving fingerprint {fingerprint_id}: {e}")
            raise DatabaseError(f"Retrieval failed: {e}")
    
    async def search_fingerprints(
        self,
        user_id: Optional[str] = None,
        content_type: Optional[str] = None,
        fingerprint_type: Optional[str] = None,
        quality_level: Optional[str] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ContentFingerprint]:
        """        Advanced fingerprint search with multiple filters
        
        Args:
            user_id: Filter by user
            content_type: Filter by content type
            fingerprint_type: Filter by fingerprint type
            quality_level: Filter by quality level
            created_after: Filter by creation date (after)
            created_before: Filter by creation date (before)
            limit: Maximum results to return
            offset: Results offset for pagination
            
        Returns:
            List of matching ContentFingerprint objects
        """        try:
            async with self.db_manager.get_session() as session:
                query = select(FingerprintStorageModel)
                
                # Apply filters
                conditions = []
                if user_id:
                    conditions.append(FingerprintStorageModel.user_id == user_id)
                if content_type:
                    conditions.append(FingerprintStorageModel.content_type == content_type)
                if fingerprint_type:
                    conditions.append(FingerprintStorageModel.fingerprint_type == fingerprint_type)
                if quality_level:
                    conditions.append(FingerprintStorageModel.quality_level == quality_level)
                if created_after:
                    conditions.append(FingerprintStorageModel.created_at >= created_after)
                if created_before:
                    conditions.append(FingerprintStorageModel.created_at <= created_before)
                
                if conditions:
                    query = query.where(and_(*conditions))
                
                # Apply ordering and pagination
                query = query.order_by(FingerprintStorageModel.created_at.desc())
                query = query.limit(limit).offset(offset)
                
                result = await session.execute(query)
                models = result.scalars().all()
                
                # Convert to ContentFingerprint objects
                fingerprints = []
                for model in models:
                    fingerprint = await self._model_to_fingerprint(model, include_vectors=False)
                    fingerprints.append(fingerprint)
                
                return fingerprints
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error searching fingerprints: {e}")
            raise DatabaseError(f"Search failed: {e}")
    
    async def update_fingerprint(
        self,
        fingerprint_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """        Update fingerprint data with validation
        
        Args:
            fingerprint_id: Fingerprint identifier
            updates: Dictionary of fields to update
            
        Returns:
            bool: True if updated successfully
        """        try:
            async with self.db_manager.get_session() as session:
                query = update(FingerprintStorageModel).where(
                    FingerprintStorageModel.fingerprint_id == fingerprint_id
                ).values(**updates)
                
                result = await session.execute(query)
                await session.commit()
                
                updated = result.rowcount > 0
                if updated:
                    self.logger.info(f"Updated fingerprint {fingerprint_id}")
                
                return updated
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error updating fingerprint {fingerprint_id}: {e}")
            raise DatabaseError(f"Update failed: {e}")
    
    async def delete_fingerprint(self, fingerprint_id: str) -> bool:
        """        Delete fingerprint and associated data
        
        Args:
            fingerprint_id: Fingerprint identifier
            
        Returns:
            bool: True if deleted successfully
        """        try:
            async with self.db_manager.get_session() as session:
                # Delete matches first (foreign key constraint)
                await session.execute(
                    delete(FingerprintMatchModel).where(
                        or_(
                            FingerprintMatchModel.fingerprint_id == fingerprint_id,
                            FingerprintMatchModel.matched_fingerprint_id == fingerprint_id
                        )
                    )
                )
                
                # Delete fingerprint
                query = delete(FingerprintStorageModel).where(
                    FingerprintStorageModel.fingerprint_id == fingerprint_id
                )
                result = await session.execute(query)
                await session.commit()
                
                deleted = result.rowcount > 0
                if deleted:
                    self.logger.info(f"Deleted fingerprint {fingerprint_id}")
                
                return deleted
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error deleting fingerprint {fingerprint_id}: {e}")
            raise DatabaseError(f"Deletion failed: {e}")
    
    async def get_storage_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """        Get comprehensive storage statistics
        
        Args:
            user_id: Optional user filter
            
        Returns:
            Dictionary with storage statistics
        """        try:
            async with self.db_manager.get_session() as session:
                base_query = select(FingerprintStorageModel)
                if user_id:
                    base_query = base_query.where(FingerprintStorageModel.user_id == user_id)
                
                # Total count
                count_result = await session.execute(
                    select(func.count()).select_from(base_query.subquery())
                )
                total_count = count_result.scalar()
                
                # Content type distribution
                content_type_query = select(
                    FingerprintStorageModel.content_type,
                    func.count().label('count')
                ).group_by(FingerprintStorageModel.content_type)
                if user_id:
                    content_type_query = content_type_query.where(FingerprintStorageModel.user_id == user_id)
                
                content_type_result = await session.execute(content_type_query)
                content_type_dist = dict(content_type_result.fetchall())
                
                # Storage size
                size_query = select(func.sum(FingerprintStorageModel.storage_size))
                if user_id:
                    size_query = size_query.where(FingerprintStorageModel.user_id == user_id)
                
                size_result = await session.execute(size_query)
                total_size = size_result.scalar() or 0
                
                return {
                    'total_fingerprints': total_count,
                    'content_type_distribution': content_type_dist,
                    'total_storage_size': total_size,
                    'average_confidence': await self._calculate_average_confidence(session, user_id),
                    'quality_distribution': await self._get_quality_distribution(session, user_id)
                }
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting storage stats: {e}")
            raise DatabaseError(f"Statistics retrieval failed: {e}")
    
    # Private helper methods
    
    def _validate_fingerprint(self, fingerprint: ContentFingerprint) -> None:
        """Validate fingerprint data before storage"""        if not fingerprint.content_id:
            raise ValidationError("Content ID is required")
        if not fingerprint.primary_hash:
            raise ValidationError("Primary hash is required")
        if not fingerprint.content_type:
            raise ValidationError("Content type is required")
    
    async def _prepare_storage_data(
        self,
        fingerprint: ContentFingerprint,
        user_id: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare fingerprint data for storage"""        storage_data = {
            'content_id': fingerprint.content_id,
            'user_id': user_id,
            'content_type': fingerprint.content_type.value if hasattr(fingerprint.content_type, 'value') else str(fingerprint.content_type),
            'fingerprint_type': fingerprint.fingerprint_type.value if hasattr(fingerprint.fingerprint_type, 'value') else str(fingerprint.fingerprint_type),
            'primary_hash': fingerprint.primary_hash,
            'perceptual_hash': fingerprint.perceptual_hash,
            'structural_hash': fingerprint.structural_hash,
            'semantic_hash': fingerprint.semantic_hash,
            'temporal_signature': fingerprint.temporal_signature,
            'file_signature': fingerprint.file_signature,
            'confidence_score': fingerprint.confidence_score or 0.0,
            'metadata': {**(metadata or {}), **(fingerprint.metadata or {})},
        }
        
        # Handle vector data with encryption
        if hasattr(fingerprint, 'feature_vector') and fingerprint.feature_vector is not None:
            storage_data['feature_vector'] = await self._encrypt_vector(fingerprint.feature_vector)
        
        if hasattr(fingerprint, 'embedding_vector') and fingerprint.embedding_vector is not None:
            storage_data['embedding_vector'] = await self._encrypt_vector(fingerprint.embedding_vector)
        
        return storage_data
    
    async def _encrypt_vector(self, vector: np.ndarray) -> bytes:
        """Encrypt vector data for secure storage"""        if not self.encryption_enabled:
            return vector.tobytes()
        
        return await self.encryption_manager.encrypt_data(vector.tobytes())
    
    async def _decrypt_vector(self, encrypted_vector: bytes) -> np.ndarray:
        """Decrypt vector data from storage"""        if not self.encryption_enabled:
            return np.frombuffer(encrypted_vector, dtype=np.float32)
        
        decrypted_data = await self.encryption_manager.decrypt_data(encrypted_vector)
        return np.frombuffer(decrypted_data, dtype=np.float32)
    
    async def _model_to_fingerprint(
        self,
        model: FingerprintStorageModel,
        include_vectors: bool = True
    ) -> ContentFingerprint:
        """Convert storage model to ContentFingerprint object"""        fingerprint_data = {
            'content_id': model.content_id,
            'fingerprint_type': FingerprintType(model.fingerprint_type),
            'primary_hash': model.primary_hash,
            'perceptual_hash': model.perceptual_hash,
            'structural_hash': model.structural_hash,
            'semantic_hash': model.semantic_hash,
            'temporal_signature': model.temporal_signature,
            'file_signature': model.file_signature,
            'confidence_score': model.confidence_score,
            'metadata': model.metadata or {},
            'creation_timestamp': model.created_at,
        }
        
        # Add vector data if requested
        if include_vectors:
            if model.feature_vector:
                fingerprint_data['feature_vector'] = await self._decrypt_vector(model.feature_vector)
            if model.embedding_vector:
                fingerprint_data['embedding_vector'] = await self._decrypt_vector(model.embedding_vector)
        
        return ContentFingerprint(**fingerprint_data)
    
    async def _update_performance_metrics(
        self,
        session: AsyncSession,
        fingerprint_id: str,
        processing_time: float
    ) -> None:
        """Update performance metrics for fingerprint"""        await session.execute(
            update(FingerprintStorageModel)
            .where(FingerprintStorageModel.fingerprint_id == fingerprint_id)
            .values(processing_time=processing_time)
        )
    
    async def _update_access_time(self, session: AsyncSession, fingerprint_id: str) -> None:
        """Update last accessed time"""        await session.execute(
            update(FingerprintStorageModel)
            .where(FingerprintStorageModel.fingerprint_id == fingerprint_id)
            .values(last_accessed=func.now())
        )
    
    async def _calculate_average_confidence(
        self,
        session: AsyncSession,
        user_id: Optional[str]
    ) -> float:
        """Calculate average confidence score"""        query = select(func.avg(FingerprintStorageModel.confidence_score))
        if user_id:
            query = query.where(FingerprintStorageModel.user_id == user_id)
        
        result = await session.execute(query)
        return result.scalar() or 0.0
    
    async def _get_quality_distribution(
        self,
        session: AsyncSession,
        user_id: Optional[str]
    ) -> Dict[str, int]:
        """Get quality level distribution"""        query = select(
            FingerprintStorageModel.quality_level,
            func.count().label('count')
        ).group_by(FingerprintStorageModel.quality_level)
        
        if user_id:
            query = query.where(FingerprintStorageModel.user_id == user_id)
        
        result = await session.execute(query)
        return dict(result.fetchall())
    
    @asynccontextmanager
    async def batch_operation(self):
        """Context manager for batch operations with transaction safety"""        async with self.db_manager.get_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def cleanup_expired_fingerprints(self) -> int:
        """Clean up expired fingerprints"""        try:
            async with self.db_manager.get_session() as session:
                now = datetime.now(timezone.utc)
                
                query = delete(FingerprintStorageModel).where(
                    and_(
                        FingerprintStorageModel.expires_at.isnot(None),
                        FingerprintStorageModel.expires_at <= now
                    )
                )
                
                result = await session.execute(query)
                await session.commit()
                
                deleted_count = result.rowcount
                self.logger.info(f"Cleaned up {deleted_count} expired fingerprints")
                
                return deleted_count
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error during cleanup: {e}")
            raise DatabaseError(f"Cleanup failed: {e}")
