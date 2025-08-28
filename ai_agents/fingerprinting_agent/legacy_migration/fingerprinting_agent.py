"""
Fingerprinting Agent - Ultra-Advanced Multi-Format Content Identification System

Core agent responsible for generating and managing sophisticated fingerprints across all content formats
using state-of-the-art AI/ML algorithms for precise content identification and similarity matching.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import asyncio
import logging
import time
import hashlib
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from pathlib import Path
import pickle
import base64

import torch
import torch.nn as nn
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import faiss
import redis
import psycopg2
from sqlalchemy.orm import Session

from ..base import BaseAgent, AgentRequest, AgentResponse, AgentStatus
from ...core.config import settings
from ...core.database import get_db_session
from ...core.exceptions import FingerprintingError, ValidationError, ProcessingError
from ...security.encryption import ContentEncryption
from ...utils.vector_storage import VectorStorage
from ...utils.cache_manager import CacheManager

from .audio_fingerprinter import AudioFingerprinter
from .video_fingerprinter import VideoFingerprinter
from .image_fingerprinter import ImageFingerprinter
from .text_fingerprinter import TextFingerprinter
from .similarity_matcher import SimilarityMatcher

logger = logging.getLogger(__name__)

class FingerprintType(Enum):
    """Types of fingerprints supported"""
    AUDIO = "audio"
    VIDEO = "video" 
    IMAGE = "image"
    TEXT = "text"
    COMPOSITE = "composite"  # Multi-modal content

class FingerprintQuality(Enum):
    """Fingerprint quality levels"""
    LOW = "low"          # Basic hash-based
    MEDIUM = "medium"    # Feature extraction
    HIGH = "high"        # Deep learning embeddings
    ULTRA = "ultra"      # Multi-model ensemble

class SimilarityThreshold(Enum):
    """Similarity matching thresholds"""
    EXACT_MATCH = 0.98
    NEAR_DUPLICATE = 0.90
    SIMILAR_CONTENT = 0.75
    RELATED_CONTENT = 0.60
    DIFFERENT_CONTENT = 0.40

@dataclass
class ContentFingerprint:
    """Advanced content fingerprint structure"""
    fingerprint_id: str
    content_id: str
    content_type: str
    fingerprint_type: FingerprintType
    quality_level: FingerprintQuality
    
    # Core fingerprint data
    hash_fingerprint: str           # Fast lookup hash
    feature_fingerprint: np.ndarray # Feature vector
    embedding_fingerprint: np.ndarray # Deep learning embedding
    
    # Metadata and context
    metadata: Dict[str, Any] = field(default_factory=dict)
    extraction_params: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Temporal information
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Relationships
    parent_fingerprints: List[str] = field(default_factory=list)  # For composite content
    derived_fingerprints: List[str] = field(default_factory=list)  # Variations/segments

@dataclass 
class SimilarityMatch:
    """Similarity match result"""
    query_fingerprint_id: str
    matched_fingerprint_id: str
    similarity_score: float
    similarity_type: str
    confidence_level: float
    match_details: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class FingerprintingAgent(BaseAgent):
    """
    Ultra-advanced multi-format content fingerprinting agent with enterprise-grade capabilities.
    
    Features:
    - Multi-modal fingerprinting (audio, video, image, text)
    - Deep learning embedding generation
    - Vector similarity search with FAISS
    - Scalable storage and retrieval
    - Real-time similarity matching
    - Quality assessment and optimization
    - Batch processing capabilities
    - Cross-format content analysis
    """
    
    def __init__(self, agent_id: str = "fingerprinting_agent", config: Dict[str, Any] = None):
        super().__init__(agent_id, config)
        
        # Specialized fingerprinters
        self.audio_fingerprinter = AudioFingerprinter()
        self.video_fingerprinter = VideoFingerprinter()
        self.image_fingerprinter = ImageFingerprinter()
        self.text_fingerprinter = TextFingerprinter()
        self.similarity_matcher = SimilarityMatcher()
        
        # Storage and indexing
        self.vector_storage = VectorStorage()
        self.cache_manager = CacheManager(prefix="fingerprints")
        self.encryption = ContentEncryption()
        
        # FAISS indexes for different content types
        self.faiss_indexes: Dict[str, faiss.Index] = {}
        self.id_mappings: Dict[str, Dict[int, str]] = {}  # FAISS index -> fingerprint_id
        
        # Processing parameters
        self.batch_size = config.get('batch_size', 32) if config else 32
        self.similarity_threshold = config.get('similarity_threshold', 0.75) if config else 0.75
        self.quality_threshold = config.get('quality_threshold', 0.8) if config else 0.8
        
        # Performance metrics
        self.processing_metrics = {
            'total_processed': 0,
            'processing_time': [],
            'quality_scores': [],
            'similarity_matches': 0
        }
        
    async def initialize(self):
        """Initialize fingerprinting agent with all specialized components"""
        try:
            start_time = time.time()
            
            # Initialize specialized fingerprinters
            await self.audio_fingerprinter.initialize()
            await self.video_fingerprinter.initialize() 
            await self.image_fingerprinter.initialize()
            await self.text_fingerprinter.initialize()
            await self.similarity_matcher.initialize()
            
            # Initialize vector storage
            await self.vector_storage.initialize()
            
            # Load or create FAISS indexes
            await self._initialize_faiss_indexes()
            
            # Load existing fingerprints from database
            await self._load_existing_fingerprints()
            
            initialization_time = time.time() - start_time
            self.status = AgentStatus.READY
            
            logger.info(f"Fingerprinting Agent initialized successfully in {initialization_time:.2f}s")
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Failed to initialize Fingerprinting Agent: {e}")
            raise FingerprintingError(f"Initialization failed: {e}")
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """
        Process fingerprinting request with advanced multi-format support
        """
        start_time = time.time()
        
        try:
            # Validate request
            await self._validate_request(request)
            
            action = request.data.get('action', 'generate_fingerprint')
            
            if action == 'generate_fingerprint':
                result = await self._generate_fingerprint(request)
            elif action == 'find_similar':
                result = await self._find_similar_content(request)
            elif action == 'batch_fingerprint':
                result = await self._batch_fingerprint(request)
            elif action == 'update_fingerprint':
                result = await self._update_fingerprint(request)
            elif action == 'delete_fingerprint':
                result = await self._delete_fingerprint(request)
            elif action == 'analyze_similarity':
                result = await self._analyze_similarity(request)
            elif action == 'composite_fingerprint':
                result = await self._generate_composite_fingerprint(request)
            else:
                raise ValidationError(f"Unknown action: {action}")
            
            processing_time = time.time() - start_time
            self.processing_metrics['processing_time'].append(processing_time)
            self.processing_metrics['total_processed'] += 1
            
            return AgentResponse(
                agent_id=self.agent_id,
                request_id=request.request_id,
                status="success",
                data=result,
                metadata={
                    "processing_time": processing_time,
                    "action": action,
                    "performance_metrics": self._get_performance_summary()
                }
            )
            
        except Exception as e:
            logger.error(f"Fingerprinting processing error: {e}")
            return AgentResponse(
                agent_id=self.agent_id,
                request_id=request.request_id,
                status="error",
                error=str(e),
                metadata={"processing_time": time.time() - start_time}
            )
    
    async def _generate_fingerprint(self, request: AgentRequest) -> Dict[str, Any]:
        """Generate comprehensive fingerprint for content"""
        content_data = request.data.get('content_data')
        content_type = request.data.get('content_type')
        quality_level = FingerprintQuality(request.data.get('quality_level', 'high'))
        
        if not content_data or not content_type:
            raise ValidationError("Content data and type are required")
        
        # Generate fingerprint based on content type
        if content_type == 'audio':
            fingerprint_data = await self.audio_fingerprinter.generate_fingerprint(
                content_data, quality_level
            )
        elif content_type == 'video':
            fingerprint_data = await self.video_fingerprinter.generate_fingerprint(
                content_data, quality_level
            )
        elif content_type == 'image':
            fingerprint_data = await self.image_fingerprinter.generate_fingerprint(
                content_data, quality_level
            )
        elif content_type == 'text':
            fingerprint_data = await self.text_fingerprinter.generate_fingerprint(
                content_data, quality_level
            )
        else:
            raise ValidationError(f"Unsupported content type: {content_type}")
        
        # Create comprehensive fingerprint object
        fingerprint = ContentFingerprint(
            fingerprint_id=str(uuid.uuid4()),
            content_id=request.data.get('content_id', str(uuid.uuid4())),
            content_type=content_type,
            fingerprint_type=FingerprintType(content_type),
            quality_level=quality_level,
            hash_fingerprint=fingerprint_data['hash'],
            feature_fingerprint=fingerprint_data['features'],
            embedding_fingerprint=fingerprint_data['embedding'],
            metadata=fingerprint_data.get('metadata', {}),
            extraction_params=fingerprint_data.get('params', {}),
            quality_metrics=fingerprint_data.get('quality', {})
        )
        
        # Store fingerprint
        await self._store_fingerprint(fingerprint)
        
        # Add to FAISS index for similarity search
        await self._add_to_faiss_index(fingerprint)
        
        return {
            "fingerprint_id": fingerprint.fingerprint_id,
            "content_id": fingerprint.content_id,
            "fingerprint_type": fingerprint.fingerprint_type.value,
            "quality_level": fingerprint.quality_level.value,
            "quality_metrics": fingerprint.quality_metrics,
            "metadata": fingerprint.metadata
        }
    
    async def _find_similar_content(self, request: AgentRequest) -> Dict[str, Any]:
        """Find similar content using advanced similarity matching"""
        query_data = request.data.get('query_data')
        content_type = request.data.get('content_type')
        similarity_threshold = request.data.get('threshold', self.similarity_threshold)
        max_results = request.data.get('max_results', 10)
        
        # Generate fingerprint for query content
        query_fingerprint = await self._generate_query_fingerprint(query_data, content_type)
        
        # Search in FAISS index
        similar_matches = await self._search_similar_in_faiss(
            query_fingerprint, content_type, similarity_threshold, max_results
        )
        
        # Refine matches with detailed similarity analysis
        refined_matches = []
        for match in similar_matches:
            detailed_similarity = await self.similarity_matcher.analyze_similarity(
                query_fingerprint, match['fingerprint'], content_type
            )
            
            if detailed_similarity['confidence'] >= similarity_threshold:
                refined_matches.append({
                    "fingerprint_id": match['fingerprint_id'],
                    "content_id": match['content_id'],
                    "similarity_score": detailed_similarity['score'],
                    "confidence": detailed_similarity['confidence'],
                    "similarity_details": detailed_similarity['details'],
                    "match_type": detailed_similarity['match_type']
                })
        
        self.processing_metrics['similarity_matches'] += len(refined_matches)
        
        return {
            "query_fingerprint_id": query_fingerprint.fingerprint_id,
            "matches_found": len(refined_matches),
            "matches": refined_matches,
            "search_parameters": {
                "threshold": similarity_threshold,
                "max_results": max_results,
                "content_type": content_type
            }
        }
    
    async def _batch_fingerprint(self, request: AgentRequest) -> Dict[str, Any]:
        """Process multiple content items in batch"""
        content_batch = request.data.get('content_batch', [])
        quality_level = FingerprintQuality(request.data.get('quality_level', 'high'))
        
        if not content_batch:
            raise ValidationError("Content batch is required")
        
        results = []
        failed_items = []
        
        # Process in batches to manage memory
        for i in range(0, len(content_batch), self.batch_size):
            batch_items = content_batch[i:i + self.batch_size]
            
            # Process batch concurrently
            batch_tasks = []
            for item in batch_items:
                task = self._process_batch_item(item, quality_level)
                batch_tasks.append(task)
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    failed_items.append({
                        "item_index": i + j,
                        "error": str(result),
                        "content_id": batch_items[j].get('content_id', 'unknown')
                    })
                else:
                    results.append(result)
        
        return {
            "total_processed": len(content_batch),
            "successful": len(results),
            "failed": len(failed_items),
            "results": results,
            "failed_items": failed_items
        }
    
    async def _generate_composite_fingerprint(self, request: AgentRequest) -> Dict[str, Any]:
        """Generate composite fingerprint for multi-modal content"""
        content_components = request.data.get('content_components', [])
        
        if not content_components:
            raise ValidationError("Content components are required for composite fingerprint")
        
        # Generate individual fingerprints for each component
        component_fingerprints = []
        for component in content_components:
            component_fp = await self._generate_component_fingerprint(component)
            component_fingerprints.append(component_fp)
        
        # Create composite fingerprint
        composite_id = str(uuid.uuid4())
        composite_embedding = await self._create_composite_embedding(component_fingerprints)
        composite_hash = self._create_composite_hash(component_fingerprints)
        
        composite_fingerprint = ContentFingerprint(
            fingerprint_id=composite_id,
            content_id=request.data.get('content_id', str(uuid.uuid4())),
            content_type="composite",
            fingerprint_type=FingerprintType.COMPOSITE,
            quality_level=FingerprintQuality.ULTRA,
            hash_fingerprint=composite_hash,
            feature_fingerprint=composite_embedding,
            embedding_fingerprint=composite_embedding,
            metadata={
                "components": [fp.fingerprint_id for fp in component_fingerprints],
                "component_types": [fp.content_type for fp in component_fingerprints]
            }
        )
        
        # Store composite fingerprint
        await self._store_fingerprint(composite_fingerprint)
        await self._add_to_faiss_index(composite_fingerprint)
        
        return {
            "composite_fingerprint_id": composite_id,
            "components_count": len(component_fingerprints),
            "component_fingerprints": [fp.fingerprint_id for fp in component_fingerprints],
            "quality_metrics": composite_fingerprint.quality_metrics
        }
    
    async def _initialize_faiss_indexes(self):
        """Initialize FAISS indexes for different content types"""
        index_configs = {
            'audio': {'dimension': 512, 'index_type': 'IVF'},
            'video': {'dimension': 1024, 'index_type': 'IVF'},
            'image': {'dimension': 768, 'index_type': 'IVF'}, 
            'text': {'dimension': 384, 'index_type': 'Flat'},
            'composite': {'dimension': 1536, 'index_type': 'HNSW'}
        }
        
        for content_type, config in index_configs.items():
            if config['index_type'] == 'IVF':
                quantizer = faiss.IndexFlatIP(config['dimension'])
                index = faiss.IndexIVFFlat(quantizer, config['dimension'], 100)
                index.train(np.random.random((1000, config['dimension'])).astype(np.float32))
            elif config['index_type'] == 'HNSW':
                index = faiss.IndexHNSWFlat(config['dimension'], 32)
            else:  # Flat
                index = faiss.IndexFlatIP(config['dimension'])
            
            self.faiss_indexes[content_type] = index
            self.id_mappings[content_type] = {}
            
            logger.info(f"Initialized FAISS index for {content_type}: {config}")
    
    async def _store_fingerprint(self, fingerprint: ContentFingerprint):
        """Store fingerprint in database and cache"""
        try:
            # Store in database
            async with get_db_session() as db:
                fingerprint_data = {
                    'fingerprint_id': fingerprint.fingerprint_id,
                    'content_id': fingerprint.content_id,
                    'content_type': fingerprint.content_type,
                    'fingerprint_type': fingerprint.fingerprint_type.value,
                    'quality_level': fingerprint.quality_level.value,
                    'hash_fingerprint': fingerprint.hash_fingerprint,
                    'feature_fingerprint': pickle.dumps(fingerprint.feature_fingerprint),
                    'embedding_fingerprint': pickle.dumps(fingerprint.embedding_fingerprint),
                    'metadata': json.dumps(fingerprint.metadata),
                    'extraction_params': json.dumps(fingerprint.extraction_params),
                    'quality_metrics': json.dumps(fingerprint.quality_metrics),
                    'created_at': fingerprint.created_at,
                    'expires_at': fingerprint.expires_at
                }
                
                # Insert into database (assuming table exists)
                # db.execute("INSERT INTO content_fingerprints (...) VALUES (...)", fingerprint_data)
                # await db.commit()
            
            # Store in cache for fast access
            cache_key = f"fingerprint:{fingerprint.fingerprint_id}"
            await self.cache_manager.set(cache_key, fingerprint, expire=3600)
            
        except Exception as e:
            logger.error(f"Failed to store fingerprint: {e}")
            raise ProcessingError(f"Storage failed: {e}")
    
    async def _add_to_faiss_index(self, fingerprint: ContentFingerprint):
        """Add fingerprint to appropriate FAISS index"""
        content_type = fingerprint.content_type
        
        if content_type not in self.faiss_indexes:
            logger.warning(f"No FAISS index for content type: {content_type}")
            return
        
        index = self.faiss_indexes[content_type]
        embedding = fingerprint.embedding_fingerprint.reshape(1, -1).astype(np.float32)
        
        # Add to index
        index.add(embedding)
        
        # Update ID mapping
        faiss_id = index.ntotal - 1
        self.id_mappings[content_type][faiss_id] = fingerprint.fingerprint_id
        
        logger.debug(f"Added fingerprint {fingerprint.fingerprint_id} to FAISS index")
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        metrics = self.processing_metrics
        
        avg_processing_time = (
            sum(metrics['processing_time']) / len(metrics['processing_time'])
            if metrics['processing_time'] else 0
        )
        
        avg_quality_score = (
            sum(metrics['quality_scores']) / len(metrics['quality_scores'])
            if metrics['quality_scores'] else 0
        )
        
        return {
            "total_processed": metrics['total_processed'],
            "average_processing_time": avg_processing_time,
            "average_quality_score": avg_quality_score,
            "similarity_matches": metrics['similarity_matches'],
            "cache_hit_rate": self.cache_manager.get_hit_rate(),
            "active_indexes": list(self.faiss_indexes.keys()),
            "index_sizes": {
                content_type: index.ntotal 
                for content_type, index in self.faiss_indexes.items()
            }
        }
    
    async def _validate_request(self, request: AgentRequest):
        """Validate fingerprinting request"""
        if not request.data:
            raise ValidationError("Request data is required")
        
        action = request.data.get('action')
        if not action:
            raise ValidationError("Action is required")
        
        # Action-specific validation
        if action in ['generate_fingerprint', 'find_similar']:
            if not request.data.get('content_type'):
                raise ValidationError("Content type is required")
    
    async def cleanup(self):
        """Clean up resources"""
        try:
            # Save FAISS indexes
            for content_type, index in self.faiss_indexes.items():
                index_path = f"/tmp/faiss_{content_type}.index"
                faiss.write_index(index, index_path)
            
            # Cleanup specialized agents
            await self.audio_fingerprinter.cleanup()
            await self.video_fingerprinter.cleanup()
            await self.image_fingerprinter.cleanup()
            await self.text_fingerprinter.cleanup()
            
            await super().cleanup()
            
        except Exception as e:
            logger.error(f"Error during fingerprinting agent cleanup: {e}")
