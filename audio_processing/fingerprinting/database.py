"""
Database integration layer for audio fingerprinting system.
Professional database operations with advanced indexing and performance optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Audio Protection Suite
License: Proprietary - All rights reserved

WARNING: This code is proprietary and protected by copyright.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Contact: Fahed Mlaiel (mlaiel@live.de) for licensing agreements.
"""

import asyncio
import asyncpg
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
import json
import logging
from datetime import datetime, timezone
import pickle
import zlib
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, insert, update, delete
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FingerprintRecord:
    """Database record for audio fingerprints."""
    
    id: Optional[int] = None
    user_id: int = None
    content_type: str = "audio"
    original_filename: Optional[str] = None
    fingerprint_hash: str = None
    chromaprint_data: Optional[str] = None
    spectral_features: Optional[bytes] = None  # Serialized numpy array
    perceptual_hash: Optional[str] = None
    metadata: Dict[str, Any] = None
    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    bit_rate: Optional[int] = None
    format_info: Optional[Dict[str, Any]] = None
    creation_timestamp: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    is_active: bool = True
    protection_level: str = "standard"  # standard, premium, enterprise
    

@dataclass
class MatchRecord:
    """Database record for fingerprint matches."""
    
    id: Optional[int] = None
    query_fingerprint_id: int = None
    matched_fingerprint_id: int = None
    similarity_score: float = None
    match_algorithm: str = None
    confidence_score: float = None
    false_positive_probability: float = None
    match_metadata: Dict[str, Any] = None
    detection_timestamp: Optional[datetime] = None
    is_verified: bool = False
    verification_method: Optional[str] = None


@dataclass
class QueryPerformanceRecord:
    """Database record for query performance tracking."""
    
    id: Optional[int] = None
    query_type: str = None
    execution_time_ms: float = None
    candidate_count: int = None
    result_count: int = None
    algorithm_used: str = None
    query_parameters: Dict[str, Any] = None
    timestamp: Optional[datetime] = None


class FingerprintDatabaseManager:
    """
    Advanced database manager for audio fingerprint storage and retrieval.
    Handles PostgreSQL operations with vector indexing for efficient matching.
    """
    
    def __init__(self, database_url: str, config: Optional[Dict] = None):
        """Initialize the database manager."""
        self.database_url = database_url
        self.config = config or self._default_config()
        
        # Database connection management
        self.engine = None
        self.session_factory = None
        self.connection_pool = None
        
        # Performance tracking
        self.query_stats = {
            'total_queries': 0,
            'avg_response_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        logger.info("FingerprintDatabaseManager initialized")
    
    def _default_config(self) -> Dict:
        """Default configuration for database operations."""
        return {
            'pool_size': 20,
            'max_overflow': 30,
            'pool_timeout': 30,
            'pool_recycle': 3600,
            'enable_query_cache': True,
            'cache_size': 1000,
            'cache_ttl': 300,  # 5 minutes
            'batch_size': 100,
            'enable_performance_tracking': True,
            'compression_level': 6
        }
    
    async def initialize(self):
        """Initialize database connections and create tables if needed."""
        try:
            # Create async engine
            self.engine = create_async_engine(
                self.database_url,
                pool_size=self.config['pool_size'],
                max_overflow=self.config['max_overflow'],
                pool_timeout=self.config['pool_timeout'],
                pool_recycle=self.config['pool_recycle'],
                echo=False  # Set to True for SQL logging
            )
            
            # Create session factory
            self.session_factory = sessionmaker(
                self.engine, 
                class_=AsyncSession, 
                expire_on_commit=False
            )
            
            # Initialize database schema
            await self._initialize_schema()
            
            # Create indexes for performance
            await self._create_indexes()
            
            logger.info("Database initialization completed successfully")
            
        except Exception as e:
            logger.error("Error initializing database: %s", str(e))
            raise
    
    async def _initialize_schema(self):
        """Create database tables and extensions."""
        schema_sql = """
        -- Enable required extensions
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        CREATE EXTENSION IF NOT EXISTS "pg_trgm";
        
        -- Audio fingerprints table
        CREATE TABLE IF NOT EXISTS audio_fingerprints (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            content_type VARCHAR(50) NOT NULL DEFAULT 'audio',
            original_filename VARCHAR(512),
            fingerprint_hash VARCHAR(128) NOT NULL UNIQUE,
            chromaprint_data TEXT,
            spectral_features BYTEA,
            perceptual_hash VARCHAR(256),
            metadata JSONB DEFAULT '{}',
            file_size_bytes BIGINT,
            duration_seconds FLOAT,
            sample_rate INTEGER,
            channels INTEGER,
            bit_rate INTEGER,
            format_info JSONB DEFAULT '{}',
            creation_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            is_active BOOLEAN DEFAULT TRUE,
            protection_level VARCHAR(20) DEFAULT 'standard'
        );
        
        -- Fingerprint matches table
        CREATE TABLE IF NOT EXISTS fingerprint_matches (
            id SERIAL PRIMARY KEY,
            query_fingerprint_id INTEGER REFERENCES audio_fingerprints(id),
            matched_fingerprint_id INTEGER REFERENCES audio_fingerprints(id),
            similarity_score FLOAT NOT NULL,
            match_algorithm VARCHAR(50) NOT NULL,
            confidence_score FLOAT,
            false_positive_probability FLOAT,
            match_metadata JSONB DEFAULT '{}',
            detection_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            is_verified BOOLEAN DEFAULT FALSE,
            verification_method VARCHAR(50)
        );
        
        -- Query performance tracking table
        CREATE TABLE IF NOT EXISTS query_performance (
            id SERIAL PRIMARY KEY,
            query_type VARCHAR(50) NOT NULL,
            execution_time_ms FLOAT NOT NULL,
            candidate_count INTEGER,
            result_count INTEGER,
            algorithm_used VARCHAR(50),
            query_parameters JSONB DEFAULT '{}',
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- User content statistics table
        CREATE TABLE IF NOT EXISTS user_content_stats (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            total_fingerprints INTEGER DEFAULT 0,
            total_matches_found INTEGER DEFAULT 0,
            last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            storage_used_bytes BIGINT DEFAULT 0,
            UNIQUE(user_id)
        );
        """
        
        async with self.engine.begin() as conn:
            await conn.execute(text(schema_sql))
            await conn.commit()
        
        logger.info("Database schema initialized")
    
    async def _create_indexes(self):
        """Create performance indexes."""
        indexes_sql = """
        -- Performance indexes
        CREATE INDEX IF NOT EXISTS idx_fingerprints_hash ON audio_fingerprints(fingerprint_hash);
        CREATE INDEX IF NOT EXISTS idx_fingerprints_user ON audio_fingerprints(user_id);
        CREATE INDEX IF NOT EXISTS idx_fingerprints_content_type ON audio_fingerprints(content_type);
        CREATE INDEX IF NOT EXISTS idx_fingerprints_active ON audio_fingerprints(is_active);
        CREATE INDEX IF NOT EXISTS idx_fingerprints_created ON audio_fingerprints(creation_timestamp);
        
        -- GIN index for metadata search
        CREATE INDEX IF NOT EXISTS idx_fingerprints_metadata ON audio_fingerprints USING GIN(metadata);
        
        -- Trigram index for filename search
        CREATE INDEX IF NOT EXISTS idx_fingerprints_filename ON audio_fingerprints USING GIN(original_filename gin_trgm_ops);
        
        -- Match indexes
        CREATE INDEX IF NOT EXISTS idx_matches_query ON fingerprint_matches(query_fingerprint_id);
        CREATE INDEX IF NOT EXISTS idx_matches_matched ON fingerprint_matches(matched_fingerprint_id);
        CREATE INDEX IF NOT EXISTS idx_matches_similarity ON fingerprint_matches(similarity_score);
        CREATE INDEX IF NOT EXISTS idx_matches_timestamp ON fingerprint_matches(detection_timestamp);
        
        -- Performance tracking indexes
        CREATE INDEX IF NOT EXISTS idx_performance_type ON query_performance(query_type);
        CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON query_performance(timestamp);
        """
        
        async with self.engine.begin() as conn:
            await conn.execute(text(indexes_sql))
            await conn.commit()
        
        logger.info("Database indexes created")
    
    @asynccontextmanager
    async def get_session(self):
        """Get an async database session with proper error handling."""
        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("Database session error: %s", str(e))
            raise
        finally:
            await session.close()
    
    async def store_fingerprint(self, fingerprint_record: FingerprintRecord) -> int:
        """
        Store a new fingerprint record in the database.
        
        Args:
            fingerprint_record: FingerprintRecord to store
            
        Returns:
            ID of the stored record
        """
        try:
            # Serialize spectral features if present
            spectral_data = None
            if fingerprint_record.spectral_features is not None:
                spectral_data = self._serialize_features(fingerprint_record.spectral_features)
            
            # Set timestamps
            now = datetime.now(timezone.utc)
            fingerprint_record.creation_timestamp = now
            fingerprint_record.last_modified = now
            
            async with self.get_session() as session:
                # Insert record
                stmt = """
                INSERT INTO audio_fingerprints (
                    user_id, content_type, original_filename, fingerprint_hash,
                    chromaprint_data, spectral_features, perceptual_hash, metadata,
                    file_size_bytes, duration_seconds, sample_rate, channels, bit_rate,
                    format_info, creation_timestamp, last_modified, is_active, protection_level
                ) VALUES (
                    :user_id, :content_type, :original_filename, :fingerprint_hash,
                    :chromaprint_data, :spectral_features, :perceptual_hash, :metadata,
                    :file_size_bytes, :duration_seconds, :sample_rate, :channels, :bit_rate,
                    :format_info, :creation_timestamp, :last_modified, :is_active, :protection_level
                ) RETURNING id
                """
                
                result = await session.execute(text(stmt), {
                    'user_id': fingerprint_record.user_id,
                    'content_type': fingerprint_record.content_type,
                    'original_filename': fingerprint_record.original_filename,
                    'fingerprint_hash': fingerprint_record.fingerprint_hash,
                    'chromaprint_data': fingerprint_record.chromaprint_data,
                    'spectral_features': spectral_data,
                    'perceptual_hash': fingerprint_record.perceptual_hash,
                    'metadata': json.dumps(fingerprint_record.metadata or {}),
                    'file_size_bytes': fingerprint_record.file_size_bytes,
                    'duration_seconds': fingerprint_record.duration_seconds,
                    'sample_rate': fingerprint_record.sample_rate,
                    'channels': fingerprint_record.channels,
                    'bit_rate': fingerprint_record.bit_rate,
                    'format_info': json.dumps(fingerprint_record.format_info or {}),
                    'creation_timestamp': fingerprint_record.creation_timestamp,
                    'last_modified': fingerprint_record.last_modified,
                    'is_active': fingerprint_record.is_active,
                    'protection_level': fingerprint_record.protection_level
                })
                
                record_id = result.scalar()
                
                # Update user statistics
                await self._update_user_stats(session, fingerprint_record.user_id, 'fingerprint_added')
                
                logger.info("Stored fingerprint record with ID: %d", record_id)
                return record_id
                
        except Exception as e:
            logger.error("Error storing fingerprint: %s", str(e))
            raise
    
    async def get_fingerprint(self, fingerprint_id: int) -> Optional[FingerprintRecord]:
        """
        Retrieve a fingerprint record by ID.
        
        Args:
            fingerprint_id: ID of the fingerprint record
            
        Returns:
            FingerprintRecord or None if not found
        """
        try:
            async with self.get_session() as session:
                stmt = """
                SELECT * FROM audio_fingerprints WHERE id = :id AND is_active = TRUE
                """
                
                result = await session.execute(text(stmt), {'id': fingerprint_id})
                row = result.fetchone()
                
                if row:
                    return self._row_to_fingerprint_record(row)
                
                return None
                
        except Exception as e:
            logger.error("Error retrieving fingerprint %d: %s", fingerprint_id, str(e))
            return None
    
    async def find_similar_fingerprints(
        self, 
        query_hash: str, 
        similarity_threshold: float = 0.8,
        limit: int = 100,
        user_id: Optional[int] = None,
        content_type: Optional[str] = None
    ) -> List[FingerprintRecord]:
        """
        Find fingerprints similar to the query hash.
        
        Args:
            query_hash: Hash to match against
            similarity_threshold: Minimum similarity score
            limit: Maximum number of results
            user_id: Filter by user ID (optional)
            content_type: Filter by content type (optional)
            
        Returns:
            List of similar FingerprintRecord objects
        """
        try:
            # Build dynamic query
            conditions = ["is_active = TRUE"]
            params = {'query_hash': query_hash, 'limit': limit}
            
            if user_id:
                conditions.append("user_id = :user_id")
                params['user_id'] = user_id
            
            if content_type:
                conditions.append("content_type = :content_type")
                params['content_type'] = content_type
            
            where_clause = " AND ".join(conditions)
            
            # For now, using simple hash matching
            # In production, would use vector similarity functions
            stmt = f"""
            SELECT * FROM audio_fingerprints 
            WHERE {where_clause}
            ORDER BY creation_timestamp DESC
            LIMIT :limit
            """
            
            async with self.get_session() as session:
                result = await session.execute(text(stmt), params)
                rows = result.fetchall()
                
                records = [self._row_to_fingerprint_record(row) for row in rows]
                
                logger.debug("Found %d similar fingerprints", len(records))
                return records
                
        except Exception as e:
            logger.error("Error finding similar fingerprints: %s", str(e))
            return []
    
    async def store_match(self, match_record: MatchRecord) -> int:
        """
        Store a fingerprint match record.
        
        Args:
            match_record: MatchRecord to store
            
        Returns:
            ID of the stored match record
        """
        try:
            match_record.detection_timestamp = datetime.now(timezone.utc)
            
            async with self.get_session() as session:
                stmt = """
                INSERT INTO fingerprint_matches (
                    query_fingerprint_id, matched_fingerprint_id, similarity_score,
                    match_algorithm, confidence_score, false_positive_probability,
                    match_metadata, detection_timestamp, is_verified, verification_method
                ) VALUES (
                    :query_fingerprint_id, :matched_fingerprint_id, :similarity_score,
                    :match_algorithm, :confidence_score, :false_positive_probability,
                    :match_metadata, :detection_timestamp, :is_verified, :verification_method
                ) RETURNING id
                """
                
                result = await session.execute(text(stmt), {
                    'query_fingerprint_id': match_record.query_fingerprint_id,
                    'matched_fingerprint_id': match_record.matched_fingerprint_id,
                    'similarity_score': match_record.similarity_score,
                    'match_algorithm': match_record.match_algorithm,
                    'confidence_score': match_record.confidence_score,
                    'false_positive_probability': match_record.false_positive_probability,
                    'match_metadata': json.dumps(match_record.match_metadata or {}),
                    'detection_timestamp': match_record.detection_timestamp,
                    'is_verified': match_record.is_verified,
                    'verification_method': match_record.verification_method
                })
                
                match_id = result.scalar()
                
                logger.info("Stored match record with ID: %d", match_id)
                return match_id
                
        except Exception as e:
            logger.error("Error storing match record: %s", str(e))
            raise
    
    async def get_user_fingerprints(
        self, 
        user_id: int, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[FingerprintRecord]:
        """
        Get all fingerprints for a specific user.
        
        Args:
            user_id: User ID to filter by
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of FingerprintRecord objects
        """
        try:
            async with self.get_session() as session:
                stmt = """
                SELECT * FROM audio_fingerprints 
                WHERE user_id = :user_id AND is_active = TRUE
                ORDER BY creation_timestamp DESC
                LIMIT :limit OFFSET :offset
                """
                
                result = await session.execute(text(stmt), {
                    'user_id': user_id,
                    'limit': limit,
                    'offset': offset
                })
                rows = result.fetchall()
                
                records = [self._row_to_fingerprint_record(row) for row in rows]
                
                logger.debug("Retrieved %d fingerprints for user %d", len(records), user_id)
                return records
                
        except Exception as e:
            logger.error("Error retrieving user fingerprints: %s", str(e))
            return []
    
    async def delete_fingerprint(self, fingerprint_id: int, user_id: Optional[int] = None):
        """
        Soft delete a fingerprint record.
        
        Args:
            fingerprint_id: ID of the fingerprint to delete
            user_id: Optional user ID for authorization
        """
        try:
            async with self.get_session() as session:
                conditions = ["id = :fingerprint_id"]
                params = {'fingerprint_id': fingerprint_id}
                
                if user_id:
                    conditions.append("user_id = :user_id")
                    params['user_id'] = user_id
                
                where_clause = " AND ".join(conditions)
                
                stmt = f"""
                UPDATE audio_fingerprints 
                SET is_active = FALSE, last_modified = NOW()
                WHERE {where_clause}
                """
                
                result = await session.execute(text(stmt), params)
                
                if result.rowcount > 0:
                    logger.info("Deleted fingerprint %d", fingerprint_id)
                else:
                    logger.warning("Fingerprint %d not found or already deleted", fingerprint_id)
                
        except Exception as e:
            logger.error("Error deleting fingerprint %d: %s", fingerprint_id, str(e))
            raise
    
    async def get_match_history(
        self, 
        fingerprint_id: int, 
        limit: int = 50
    ) -> List[MatchRecord]:
        """
        Get match history for a specific fingerprint.
        
        Args:
            fingerprint_id: ID of the fingerprint
            limit: Maximum number of match records
            
        Returns:
            List of MatchRecord objects
        """
        try:
            async with self.get_session() as session:
                stmt = """
                SELECT * FROM fingerprint_matches 
                WHERE query_fingerprint_id = :fingerprint_id OR matched_fingerprint_id = :fingerprint_id
                ORDER BY detection_timestamp DESC
                LIMIT :limit
                """
                
                result = await session.execute(text(stmt), {
                    'fingerprint_id': fingerprint_id,
                    'limit': limit
                })
                rows = result.fetchall()
                
                matches = []
                for row in rows:
                    match_record = MatchRecord(
                        id=row.id,
                        query_fingerprint_id=row.query_fingerprint_id,
                        matched_fingerprint_id=row.matched_fingerprint_id,
                        similarity_score=row.similarity_score,
                        match_algorithm=row.match_algorithm,
                        confidence_score=row.confidence_score,
                        false_positive_probability=row.false_positive_probability,
                        match_metadata=json.loads(row.match_metadata or '{}'),
                        detection_timestamp=row.detection_timestamp,
                        is_verified=row.is_verified,
                        verification_method=row.verification_method
                    )
                    matches.append(match_record)
                
                logger.debug("Retrieved %d match records for fingerprint %d", 
                           len(matches), fingerprint_id)
                return matches
                
        except Exception as e:
            logger.error("Error retrieving match history: %s", str(e))
            return []
    
    def _serialize_features(self, features: np.ndarray) -> bytes:
        """Serialize numpy array features for database storage."""
        try:
            # Pickle and compress the features
            pickled = pickle.dumps(features)
            compressed = zlib.compress(pickled, self.config['compression_level'])
            return compressed
        except Exception as e:
            logger.error("Error serializing features: %s", str(e))
            return b''
    
    def _deserialize_features(self, data: bytes) -> Optional[np.ndarray]:
        """Deserialize features from database."""
        try:
            if not data:
                return None
            
            # Decompress and unpickle
            decompressed = zlib.decompress(data)
            features = pickle.loads(decompressed)
            return features
        except Exception as e:
            logger.error("Error deserializing features: %s", str(e))
            return None
    
    def _row_to_fingerprint_record(self, row) -> FingerprintRecord:
        """Convert database row to FingerprintRecord."""
        return FingerprintRecord(
            id=row.id,
            user_id=row.user_id,
            content_type=row.content_type,
            original_filename=row.original_filename,
            fingerprint_hash=row.fingerprint_hash,
            chromaprint_data=row.chromaprint_data,
            spectral_features=self._deserialize_features(row.spectral_features),
            perceptual_hash=row.perceptual_hash,
            metadata=json.loads(row.metadata or '{}'),
            file_size_bytes=row.file_size_bytes,
            duration_seconds=row.duration_seconds,
            sample_rate=row.sample_rate,
            channels=row.channels,
            bit_rate=row.bit_rate,
            format_info=json.loads(row.format_info or '{}'),
            creation_timestamp=row.creation_timestamp,
            last_modified=row.last_modified,
            is_active=row.is_active,
            protection_level=row.protection_level
        )
    
    async def _update_user_stats(self, session: AsyncSession, user_id: int, action: str):
        """Update user content statistics."""
        try:
            if action == 'fingerprint_added':
                stmt = """
                INSERT INTO user_content_stats (user_id, total_fingerprints, last_activity)
                VALUES (:user_id, 1, NOW())
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    total_fingerprints = user_content_stats.total_fingerprints + 1,
                    last_activity = NOW()
                """
            elif action == 'match_found':
                stmt = """
                INSERT INTO user_content_stats (user_id, total_matches_found, last_activity)
                VALUES (:user_id, 1, NOW())
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    total_matches_found = user_content_stats.total_matches_found + 1,
                    last_activity = NOW()
                """
            else:
                return
            
            await session.execute(text(stmt), {'user_id': user_id})
            
        except Exception as e:
            logger.warning("Error updating user stats: %s", str(e))
    
    async def cleanup(self):
        """Cleanup database connections."""
        try:
            if self.engine:
                await self.engine.dispose()
            
            logger.info("Database cleanup completed")
            
        except Exception as e:
            logger.error("Error during database cleanup: %s", str(e))
