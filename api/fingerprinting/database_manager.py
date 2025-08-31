"""
IA Influencer Agent - Database Manager for Fingerprinting
Author: Fahed Mlaiel <mlaiel@live.de>

AVERTISSEMENT LÉGAL STRICT:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée 
sans permission écrite expresse est strictement interdite et 
constituera une violation des droits d'auteur.

Advanced database management for content fingerprints with high-performance storage
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
import numpy as np
import asyncpg
from dataclasses import asdict
import pickle
import base64

from .audio_processor import AudioFingerprint
from .video_processor import VideoFingerprint
from .image_processor import ImageFingerprint
from .text_processor import TextFingerprint

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Professional database manager for content fingerprints
    Handles high-performance storage, retrieval, and similarity searches
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize database manager"""
        self.config = config or self._get_default_config()
        self.pool = None
        self._initialized = False
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default database configuration"""



        return {
            'host': 'localhost',
            'port': 5432,
            'database': 'ia_influencer_fingerprints',
            'user': 'ia_user',
            'password': 'ia_secure_pass',
            'min_connections': 2,
            'max_connections': 10,
            'command_timeout': 60
        }
    
    async def initialize(self):
        """Initialize database connection pool and tables"""



        try:
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                min_size=self.config['min_connections'],
                max_size=self.config['max_connections'],
                command_timeout=self.config['command_timeout']
            )
            
            # Create tables if they don't exist
            await self._create_tables()
            
            # Create indexes for performance
            await self._create_indexes()
            
            self._initialized = True
            logger.info("Database manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    async def _create_tables(self):
        """Create database tables for fingerprints"""
        async with self.pool.acquire() as conn:
            # Main fingerprints table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS fingerprints (
                    id SERIAL PRIMARY KEY,
                    content_hash VARCHAR(64) UNIQUE NOT NULL,
                    content_type VARCHAR(20) NOT NULL,
                    file_path TEXT,
                    file_format VARCHAR(10),
                    file_size BIGINT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    metadata JSONB,
                    fingerprint_data BYTEA NOT NULL
                )
            """)
            
            # Audio fingerprints table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS audio_fingerprints (
                    id SERIAL PRIMARY KEY,
                    fingerprint_id INTEGER REFERENCES fingerprints(id) ON DELETE CASCADE,
                    spectral_features FLOAT8[],
                    mfcc_features FLOAT8[],
                    chromagram FLOAT8[],
                    tempo FLOAT8,
                    duration FLOAT8,
                    sample_rate INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Video fingerprints table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS video_fingerprints (
                    id SERIAL PRIMARY KEY,
                    fingerprint_id INTEGER REFERENCES fingerprints(id) ON DELETE CASCADE,
                    frame_hashes TEXT[],
                    histogram_features FLOAT8[],
                    edge_features FLOAT8[],
                    motion_vectors FLOAT8[],
                    keyframes INTEGER[],
                    duration FLOAT8,
                    fps FLOAT8,
                    resolution_width INTEGER,
                    resolution_height INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Image fingerprints table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS image_fingerprints (
                    id SERIAL PRIMARY KEY,
                    fingerprint_id INTEGER REFERENCES fingerprints(id) ON DELETE CASCADE,
                    perceptual_hash VARCHAR(64),
                    color_histogram FLOAT8[],
                    texture_features FLOAT8[],
                    shape_features FLOAT8[],
                    sift_features FLOAT8[],
                    resolution_width INTEGER,
                    resolution_height INTEGER,
                    color_space VARCHAR(10),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Text fingerprints table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS text_fingerprints (
                    id SERIAL PRIMARY KEY,
                    fingerprint_id INTEGER REFERENCES fingerprints(id) ON DELETE CASCADE,
                    semantic_hash VARCHAR(32),
                    style_features FLOAT8[],
                    linguistic_features FLOAT8[],
                    tfidf_features FLOAT8[],
                    readability_scores JSONB,
                    language VARCHAR(10),
                    word_count INTEGER,
                    character_count INTEGER,
                    sentence_count INTEGER,
                    paragraph_count INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Similarity matches table for caching
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS similarity_matches (
                    id SERIAL PRIMARY KEY,
                    fingerprint1_id INTEGER REFERENCES fingerprints(id) ON DELETE CASCADE,
                    fingerprint2_id INTEGER REFERENCES fingerprints(id) ON DELETE CASCADE,
                    similarity_score FLOAT8 NOT NULL,
                    match_type VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    UNIQUE(fingerprint1_id, fingerprint2_id)
                )
            """)
            
            logger.info("Database tables created successfully")
    
    async def _create_indexes(self):
        """Create database indexes for performance optimization"""
        async with self.pool.acquire() as conn:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_fingerprints_content_hash ON fingerprints(content_hash)",
                "CREATE INDEX IF NOT EXISTS idx_fingerprints_content_type ON fingerprints(content_type)",
                "CREATE INDEX IF NOT EXISTS idx_fingerprints_created_at ON fingerprints(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_audio_fingerprints_fingerprint_id ON audio_fingerprints(fingerprint_id)",
                "CREATE INDEX IF NOT EXISTS idx_video_fingerprints_fingerprint_id ON video_fingerprints(fingerprint_id)",
                "CREATE INDEX IF NOT EXISTS idx_image_fingerprints_fingerprint_id ON image_fingerprints(fingerprint_id)",
                "CREATE INDEX IF NOT EXISTS idx_image_fingerprints_perceptual_hash ON image_fingerprints(perceptual_hash)",
                "CREATE INDEX IF NOT EXISTS idx_text_fingerprints_fingerprint_id ON text_fingerprints(fingerprint_id)",
                "CREATE INDEX IF NOT EXISTS idx_text_fingerprints_semantic_hash ON text_fingerprints(semantic_hash)",
                "CREATE INDEX IF NOT EXISTS idx_similarity_matches_fingerprint1_id ON similarity_matches(fingerprint1_id)",
                "CREATE INDEX IF NOT EXISTS idx_similarity_matches_fingerprint2_id ON similarity_matches(fingerprint2_id)",
                "CREATE INDEX IF NOT EXISTS idx_similarity_matches_similarity_score ON similarity_matches(similarity_score DESC)"
            ]
            
            for index_sql in indexes:
                try:
                    await conn.execute(index_sql)
                except Exception as e:
                    logger.warning(f"Failed to create index: {str(e)}")
            
            logger.info("Database indexes created successfully")
    
    def _serialize_fingerprint(self, fingerprint: Union[AudioFingerprint, VideoFingerprint, ImageFingerprint, TextFingerprint]) -> bytes:
        """Serialize fingerprint object to bytes"""



        try:
            return pickle.dumps(fingerprint)
        except Exception as e:
            logger.error(f"Failed to serialize fingerprint: {str(e)}")
            raise
    
    def _deserialize_fingerprint(self, data: bytes, content_type: str) -> Union[AudioFingerprint, VideoFingerprint, ImageFingerprint, TextFingerprint]:
        """Deserialize fingerprint object from bytes"""



        try:
            return pickle.loads(data)
        except Exception as e:
            logger.error(f"Failed to deserialize fingerprint: {str(e)}")
            raise
    
    async def store_audio_fingerprint(self, fingerprint: AudioFingerprint, file_path: Optional[Path] = None) -> int:
        """Store audio fingerprint in database"""
        if not self._initialized:
            await self.initialize()
        
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Insert main fingerprint record
                fingerprint_id = await conn.fetchval("""
                    INSERT INTO fingerprints (content_hash, content_type, file_path, file_format, 
                                            file_size, metadata, fingerprint_data)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (content_hash) DO UPDATE SET
                        updated_at = NOW(),
                        metadata = EXCLUDED.metadata
                    RETURNING id
                """, fingerprint.content_hash, 'audio', 
                    str(file_path) if file_path else None,
                    fingerprint.file_format,
                    fingerprint.metadata.get('file_size'),
                    json.dumps(fingerprint.metadata),
                    self._serialize_fingerprint(fingerprint))
                
                # Insert audio-specific data
                await conn.execute("""
                    INSERT INTO audio_fingerprints (fingerprint_id, spectral_features, mfcc_features,
                                                  chromagram, tempo, duration, sample_rate)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (fingerprint_id) DO UPDATE SET
                        spectral_features = EXCLUDED.spectral_features,
                        mfcc_features = EXCLUDED.mfcc_features,
                        chromagram = EXCLUDED.chromagram,
                        tempo = EXCLUDED.tempo,
                        duration = EXCLUDED.duration,
                        sample_rate = EXCLUDED.sample_rate
                """, fingerprint_id,
                    fingerprint.spectral_features.tolist(),
                    fingerprint.mfcc_features.tolist(),
                    fingerprint.chromagram.tolist(),
                    fingerprint.tempo,
                    fingerprint.duration,
                    fingerprint.sample_rate)
                
                logger.info(f"Audio fingerprint stored with ID: {fingerprint_id}")
                return fingerprint_id
    
    async def store_video_fingerprint(self, fingerprint: VideoFingerprint, file_path: Optional[Path] = None) -> int:
        """Store video fingerprint in database"""
        if not self._initialized:
            await self.initialize()
        
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Insert main fingerprint record
                fingerprint_id = await conn.fetchval("""
                    INSERT INTO fingerprints (content_hash, content_type, file_path, file_format, 
                                            file_size, metadata, fingerprint_data)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (content_hash) DO UPDATE SET
                        updated_at = NOW(),
                        metadata = EXCLUDED.metadata
                    RETURNING id
                """, fingerprint.content_hash, 'video',
                    str(file_path) if file_path else None,
                    fingerprint.file_format,
                    fingerprint.metadata.get('file_size'),
                    json.dumps(fingerprint.metadata),
                    self._serialize_fingerprint(fingerprint))
                
                # Insert video-specific data
                await conn.execute("""
                    INSERT INTO video_fingerprints (fingerprint_id, frame_hashes, histogram_features,
                                                  edge_features, motion_vectors, keyframes, duration,
                                                  fps, resolution_width, resolution_height)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (fingerprint_id) DO UPDATE SET
                        frame_hashes = EXCLUDED.frame_hashes,
                        histogram_features = EXCLUDED.histogram_features,
                        edge_features = EXCLUDED.edge_features,
                        motion_vectors = EXCLUDED.motion_vectors,
                        keyframes = EXCLUDED.keyframes,
                        duration = EXCLUDED.duration,
                        fps = EXCLUDED.fps,
                        resolution_width = EXCLUDED.resolution_width,
                        resolution_height = EXCLUDED.resolution_height
                """, fingerprint_id,
                    fingerprint.frame_hashes,
                    fingerprint.histogram_features.tolist(),
                    fingerprint.edge_features.tolist(),
                    fingerprint.motion_vectors.tolist(),
                    fingerprint.keyframes,
                    fingerprint.duration,
                    fingerprint.fps,
                    fingerprint.resolution[0],
                    fingerprint.resolution[1])
                
                logger.info(f"Video fingerprint stored with ID: {fingerprint_id}")
                return fingerprint_id
    
    async def store_image_fingerprint(self, fingerprint: ImageFingerprint, file_path: Optional[Path] = None) -> int:
        """Store image fingerprint in database"""
        if not self._initialized:
            await self.initialize()
        
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Insert main fingerprint record
                fingerprint_id = await conn.fetchval("""
                    INSERT INTO fingerprints (content_hash, content_type, file_path, file_format, 
                                            file_size, metadata, fingerprint_data)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (content_hash) DO UPDATE SET
                        updated_at = NOW(),
                        metadata = EXCLUDED.metadata
                    RETURNING id
                """, fingerprint.content_hash, 'image',
                    str(file_path) if file_path else None,
                    fingerprint.file_format,
                    fingerprint.metadata.get('file_size'),
                    json.dumps(fingerprint.metadata),
                    self._serialize_fingerprint(fingerprint))
                
                # Insert image-specific data
                await conn.execute("""
                    INSERT INTO image_fingerprints (fingerprint_id, perceptual_hash, color_histogram,
                                                  texture_features, shape_features, sift_features,
                                                  resolution_width, resolution_height, color_space)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (fingerprint_id) DO UPDATE SET
                        perceptual_hash = EXCLUDED.perceptual_hash,
                        color_histogram = EXCLUDED.color_histogram,
                        texture_features = EXCLUDED.texture_features,
                        shape_features = EXCLUDED.shape_features,
                        sift_features = EXCLUDED.sift_features,
                        resolution_width = EXCLUDED.resolution_width,
                        resolution_height = EXCLUDED.resolution_height,
                        color_space = EXCLUDED.color_space
                """, fingerprint_id,
                    fingerprint.perceptual_hash,
                    fingerprint.color_histogram.tolist(),
                    fingerprint.texture_features.tolist(),
                    fingerprint.shape_features.tolist(),
                    fingerprint.sift_features.tolist() if fingerprint.sift_features is not None else None,
                    fingerprint.resolution[0],
                    fingerprint.resolution[1],
                    fingerprint.color_space)
                
                logger.info(f"Image fingerprint stored with ID: {fingerprint_id}")
                return fingerprint_id
    
    async def store_text_fingerprint(self, fingerprint: TextFingerprint, file_path: Optional[Path] = None) -> int:
        """Store text fingerprint in database"""
        if not self._initialized:
            await self.initialize()
        
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Insert main fingerprint record
                fingerprint_id = await conn.fetchval("""
                    INSERT INTO fingerprints (content_hash, content_type, file_path, file_format, 
                                            file_size, metadata, fingerprint_data)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (content_hash) DO UPDATE SET
                        updated_at = NOW(),
                        metadata = EXCLUDED.metadata
                    RETURNING id
                """, fingerprint.content_hash, 'text',
                    str(file_path) if file_path else None,
                    '.txt',  # Default text format
                    fingerprint.metadata.get('file_size'),
                    json.dumps(fingerprint.metadata),
                    self._serialize_fingerprint(fingerprint))
                
                # Insert text-specific data
                await conn.execute("""
                    INSERT INTO text_fingerprints (fingerprint_id, semantic_hash, style_features,
                                                 linguistic_features, tfidf_features, readability_scores,
                                                 language, word_count, character_count, sentence_count,
                                                 paragraph_count)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    ON CONFLICT (fingerprint_id) DO UPDATE SET
                        semantic_hash = EXCLUDED.semantic_hash,
                        style_features = EXCLUDED.style_features,
                        linguistic_features = EXCLUDED.linguistic_features,
                        tfidf_features = EXCLUDED.tfidf_features,
                        readability_scores = EXCLUDED.readability_scores,
                        language = EXCLUDED.language,
                        word_count = EXCLUDED.word_count,
                        character_count = EXCLUDED.character_count,
                        sentence_count = EXCLUDED.sentence_count,
                        paragraph_count = EXCLUDED.paragraph_count
                """, fingerprint_id,
                    fingerprint.semantic_hash,
                    fingerprint.style_features.tolist(),
                    fingerprint.linguistic_features.tolist(),
                    fingerprint.tfidf_features.tolist(),
                    json.dumps(fingerprint.readability_scores),
                    fingerprint.language,
                    fingerprint.word_count,
                    fingerprint.character_count,
                    fingerprint.sentence_count,
                    fingerprint.paragraph_count)
                
                logger.info(f"Text fingerprint stored with ID: {fingerprint_id}")
                return fingerprint_id
    
    async def get_fingerprint(self, fingerprint_id: int) -> Optional[Union[AudioFingerprint, VideoFingerprint, ImageFingerprint, TextFingerprint]]:
        """Retrieve fingerprint by ID"""
        if not self._initialized:
            await self.initialize()
        
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow("""
                SELECT content_type, fingerprint_data
                FROM fingerprints
                WHERE id = $1
            """, fingerprint_id)
            
            if record:
                return self._deserialize_fingerprint(record['fingerprint_data'], record['content_type'])
            return None
    
    async def find_similar_fingerprints(self, fingerprint: Union[AudioFingerprint, VideoFingerprint, ImageFingerprint, TextFingerprint], 
                                      similarity_threshold: float = 0.8, limit: int = 10) -> List[Tuple[int, float]]:
        """Find similar fingerprints in database"""
        if not self._initialized:
            await self.initialize()
        
        content_type = type(fingerprint).__name__.replace('Fingerprint', '').lower()
        
        # First, check if we already have this exact fingerprint
        async with self.pool.acquire() as conn:
            existing_id = await conn.fetchval("""
                SELECT id FROM fingerprints
                WHERE content_hash = $1
            """, fingerprint.content_hash)
            
            if existing_id:
                return [(existing_id, 1.0)]
            
            # Get all fingerprints of the same type for similarity comparison
            records = await conn.fetch("""
                SELECT id, fingerprint_data
                FROM fingerprints
                WHERE content_type = $1
                ORDER BY created_at DESC
                LIMIT 1000
            """, content_type)
        
        # Calculate similarities (this could be optimized with vector similarity search)
        similarities = []
        for record in records:
            try:
                stored_fingerprint = self._deserialize_fingerprint(record['fingerprint_data'], content_type)
                
                # Calculate similarity based on fingerprint type
                if isinstance(fingerprint, AudioFingerprint):
                    from .audio_processor import AudioFingerprintProcessor
                    processor = AudioFingerprintProcessor()
                    similarity = processor.calculate_similarity(fingerprint, stored_fingerprint)
                elif isinstance(fingerprint, VideoFingerprint):
                    from .video_processor import VideoFingerprintProcessor
                    processor = VideoFingerprintProcessor()
                    similarity = processor.calculate_similarity(fingerprint, stored_fingerprint)
                elif isinstance(fingerprint, ImageFingerprint):
                    from .image_processor import ImageFingerprintProcessor
                    processor = ImageFingerprintProcessor()
                    similarity = processor.calculate_similarity(fingerprint, stored_fingerprint)
                elif isinstance(fingerprint, TextFingerprint):
                    from .text_processor import TextFingerprintProcessor
                    processor = TextFingerprintProcessor()
                    similarity = processor.calculate_similarity(fingerprint, stored_fingerprint)
                else:
                    continue
                
                if similarity >= similarity_threshold:
                    similarities.append((record['id'], similarity))
                    
            except Exception as e:
                logger.warning(f"Error calculating similarity for fingerprint {record['id']}: {str(e)}")
                continue
        
        # Sort by similarity and return top matches
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]
    
    async def store_similarity_match(self, fingerprint1_id: int, fingerprint2_id: int, similarity_score: float, match_type: str):
        """Store similarity match for caching"""
        if not self._initialized:
            await self.initialize()
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO similarity_matches (fingerprint1_id, fingerprint2_id, similarity_score, match_type)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (fingerprint1_id, fingerprint2_id) DO UPDATE SET
                    similarity_score = EXCLUDED.similarity_score,
                    match_type = EXCLUDED.match_type
            """, fingerprint1_id, fingerprint2_id, similarity_score, match_type)
    
    async def get_similarity_matches(self, fingerprint_id: int, similarity_threshold: float = 0.8) -> List[Tuple[int, float]]:
        """Get cached similarity matches for a fingerprint"""
        if not self._initialized:
            await self.initialize()
        
        async with self.pool.acquire() as conn:
            records = await conn.fetch("""
                SELECT fingerprint2_id, similarity_score
                FROM similarity_matches
                WHERE fingerprint1_id = $1 AND similarity_score >= $2
                ORDER BY similarity_score DESC
            """, fingerprint_id, similarity_threshold)
            
            return [(record['fingerprint2_id'], record['similarity_score']) for record in records]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self._initialized:
            await self.initialize()
        
        async with self.pool.acquire() as conn:
            stats = {}
            
            # Total fingerprints by type
            type_counts = await conn.fetch("""
                SELECT content_type, COUNT(*) as count
                FROM fingerprints
                GROUP BY content_type
            """)
            
            stats['fingerprints_by_type'] = {record['content_type']: record['count'] for record in type_counts}
            
            # Total storage size
            storage_size = await conn.fetchval("""
                SELECT pg_size_pretty(pg_total_relation_size('fingerprints')) as size
            """)
            stats['storage_size'] = storage_size
            
            # Recent activity
            recent_count = await conn.fetchval("""
                SELECT COUNT(*) FROM fingerprints
                WHERE created_at >= NOW() - INTERVAL '24 hours'
            """)
            stats['recent_fingerprints_24h'] = recent_count
            
            # Similarity matches count
            matches_count = await conn.fetchval("""
                SELECT COUNT(*) FROM similarity_matches
            """)
            stats['similarity_matches'] = matches_count
            
            return stats
    
    async def cleanup_old_records(self, days_to_keep: int = 90):
        """Cleanup old fingerprint records"""
        if not self._initialized:
            await self.initialize()
        
        async with self.pool.acquire() as conn:
            deleted_count = await conn.fetchval("""
                WITH deleted AS (
                    DELETE FROM fingerprints
                    WHERE created_at < NOW() - INTERVAL '%s days'
                    RETURNING id
                )
                SELECT COUNT(*) FROM deleted
            """, days_to_keep)
            
            logger.info(f"Cleaned up {deleted_count} old fingerprint records")
            return deleted_count
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            self._initialized = False
            logger.info("Database connection pool closed")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
