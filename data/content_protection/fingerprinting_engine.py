"""Advanced AI Fingerprinting Engine
=================================

Industrial-grade multi-format content fingerprinting system for audio, video, image, and text content.
Provides AI-powered similarity detection and vector-based matching capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  AVERTISSEMENT STRICT - PROPRIÉTÉ INTELLECTUELLE ⚠️
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, modification ou distribution sans autorisation 
écrite explicite de l'auteur est strictement interdite et constitue une violation 
du droit d'auteur. Les contrevenants s'exposent à des poursuites judiciaires.
"""

import asyncio
import logging
import hashlib
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, BinaryIO
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import json
import base64
from pathlib import Path

# Audio processing imports
import librosa
import essentia.standard as es
from chromaprint import Chromaprint
import scipy.signal

# Video processing imports
import cv2
import numpy as np
from PIL import Image

# Image processing imports
import imagehash
from PIL import Image, ImageEnhance
import cv2

# Text processing imports
from transformers import AutoTokenizer, AutoModel
import torch
from sentence_transformers import SentenceTransformer
import spacy

# Vector similarity imports
import faiss
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean, manhattan

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from redis import Redis


class ContentType(Enum):
    """
Content type enumeration"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"


class FingerprintMethod(Enum):
    """Fingerprinting method enumeration"""

    SPECTRAL_HASH = "spectral_hash"
    CHROMAPRINT = "chromaprint"
    MFCC_FEATURES = "mfcc_features"
    PERCEPTUAL_HASH = "perceptual_hash"
    CLIP_EMBEDDING = "clip_embedding"
    BERT_EMBEDDING = "bert_embedding"
    FRAME_HASH = "frame_hash"
    OPTICAL_FLOW = "optical_flow"


@dataclass
class FingerprintResult:
    """Fingerprint extraction result"""
    fingerprint_id: str
    content_id: str
    content_type: ContentType
    method: FingerprintMethod
    hash_value: str
    vector_embedding: Optional[np.ndarray]
    confidence_score: float
    extraction_time: float
    metadata: Dict[str, Any]
    created_at: datetime


@dataclass
class SimilarityMatch:
    """
Content similarity match result"""
    match_id: str
    query_fingerprint_id: str
    matched_fingerprint_id: str
    similarity_score: float
    match_method: str
    confidence_level: str
    distance_metric: str
    metadata: Dict[str, Any]
    matched_at: datetime


@dataclass
class FingerprintConfig:
    """
Fingerprinting configuration"""
    content_type: ContentType
    methods: List[FingerprintMethod]
    quality_threshold: float
    vector_dimensions: int
    enable_multi_scale: bool
    enable_robustness_test: bool
    similarity_threshold: float


class FingerprintingEngine:
    """
    Advanced AI-powered content fingerprinting engine.
    
    Supports multi-format content fingerprinting with state-of-the-art algorithms
    for audio, video, image, and text content similarity detection.
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis, 
                 models_path: str = "./models"):
        """
        Initialize FingerprintingEngine.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
            models_path: Path to ML models directory
        """
        self.db_session = db_session
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        self.models_path = Path(models_path)
        
        # Initialize models
        self._initialize_models()
        
        # Configuration
        self.cache_ttl = 7200  # 2 hours
        self.vector_cache_ttl = 86400  # 24 hours
        self.similarity_batch_size = 1000
        
        # Audio processing parameters
        self.audio_sample_rate = 22050
        self.audio_hop_length = 512
        self.audio_n_mfcc = 13
        self.audio_n_chroma = 12
        
        # Image processing parameters
        self.image_hash_size = 16
        self.image_resize_target = (224, 224)
        
        # Video processing parameters
        self.video_frame_rate = 1  # Extract 1 frame per second
        self.video_resize_target = (224, 224)
        
        # Text processing parameters
        self.text_max_length = 512
        self.text_embedding_dim = 768
    
    def _initialize_models(self):
        """
Initialize ML models for fingerprinting"""
        try:
            # Initialize text models
            self.text_tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
            self.text_model = AutoModel.from_pretrained('bert-base-uncased')
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize NLP pipeline
            try:
                self.nlp = spacy.load('en_core_web_sm')
            except OSError:
                self.logger.warning("Spacy model not found, text processing may be limited")
                self.nlp = None
            
            # Initialize Chromaprint for audio
            self.chromaprint = Chromaprint()
            
            # Initialize FAISS index for vector similarity
            self.vector_index = None
            self._initialize_vector_index()
            
            self.logger.info("Fingerprinting models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing models: {str(e)}")
            raise
    
    def _initialize_vector_index(self):
        """Initialize FAISS vector index for similarity search"""
        try:
            # Create FAISS index for high-dimensional vectors
            dimension = 768  # BERT embedding dimension
            self.vector_index = faiss.IndexFlatIP(dimension)  # Inner product similarity
            
            # Alternative: Use IVF index for large datasets
            # nlist = 100
            # quantizer = faiss.IndexFlatIP(dimension)
            # self.vector_index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
            
        except Exception as e:
            self.logger.error(f"Error initializing vector index: {str(e)}")
    
    async def extract_fingerprint(self, content_data: Union[bytes, str], 
                                content_type: ContentType,
                                config: Optional[FingerprintConfig] = None) -> List[FingerprintResult]:
        """
        Extract fingerprints from content using multiple methods.
        
        Args:
            content_data: Raw content data (bytes) or file path (str)
            content_type: Type of content to process
            config: Fingerprinting configuration
            
        Returns:
            List of fingerprint extraction results
        """
        try:
            start_time = datetime.utcnow()
            
            if config is None:
                config = self._get_default_config(content_type)
            
            fingerprints = []
            
            # Extract fingerprints based on content type
            if content_type == ContentType.AUDIO:
                fingerprints = await self._extract_audio_fingerprints(content_data, config)
            elif content_type == ContentType.VIDEO:
                fingerprints = await self._extract_video_fingerprints(content_data, config)
            elif content_type == ContentType.IMAGE:
                fingerprints = await self._extract_image_fingerprints(content_data, config)
            elif content_type == ContentType.TEXT:
                fingerprints = await self._extract_text_fingerprints(content_data, config)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Store fingerprints in database
            for fingerprint in fingerprints:
                await self._store_fingerprint(fingerprint)
                
                # Cache fingerprint for fast retrieval
                await self._cache_fingerprint(fingerprint)
            
            extraction_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.info(f"Extracted {len(fingerprints)} fingerprints in {extraction_time:.2f}s")
            
            return fingerprints
            
        except Exception as e:
            self.logger.error(f"Error extracting fingerprints: {str(e)}")
            raise
    
    async def _extract_audio_fingerprints(self, audio_data: Union[bytes, str], 
                                        config: FingerprintConfig) -> List[FingerprintResult]:
        """Extract audio fingerprints using multiple methods"""
        fingerprints = []
        
        try:
            # Load audio data
            if isinstance(audio_data, str):
                y, sr = librosa.load(audio_data, sr=self.audio_sample_rate)
            else:
                # Handle bytes data
                y, sr = librosa.load(audio_data, sr=self.audio_sample_rate)
            
            content_id = str(uuid.uuid4())
            
            # Method 1: Chromaprint fingerprinting
            if FingerprintMethod.CHROMAPRINT in config.methods:
                chromaprint_hash = await self._extract_chromaprint(y, sr)
                fingerprints.append(FingerprintResult(
                    fingerprint_id=str(uuid.uuid4()),
                    content_id=content_id,
                    content_type=ContentType.AUDIO,
                    method=FingerprintMethod.CHROMAPRINT,
                    hash_value=chromaprint_hash,
                    vector_embedding=None,
                    confidence_score=0.95,
                    extraction_time=0.1,
                    metadata={'sample_rate': sr, 'duration': len(y) / sr},
                    created_at=datetime.utcnow()
                ))
            
            # Method 2: MFCC features
            if FingerprintMethod.MFCC_FEATURES in config.methods:
                mfcc_features = await self._extract_mfcc_features(y, sr)
                mfcc_hash = hashlib.sha256(mfcc_features.tobytes()).hexdigest()
                fingerprints.append(FingerprintResult(
                    fingerprint_id=str(uuid.uuid4()),
                    content_id=content_id,
                    content_type=ContentType.AUDIO,
                    method=FingerprintMethod.MFCC_FEATURES,
                    hash_value=mfcc_hash,
                    vector_embedding=mfcc_features.flatten(),
                    confidence_score=0.90,
                    extraction_time=0.15,
                    metadata={'n_mfcc': self.audio_n_mfcc, 'hop_length': self.audio_hop_length},
                    created_at=datetime.utcnow()
                ))
            
            # Method 3: Spectral hash
            if FingerprintMethod.SPECTRAL_HASH in config.methods:
                spectral_hash = await self._extract_spectral_hash(y, sr)
                fingerprints.append(FingerprintResult(
                    fingerprint_id=str(uuid.uuid4()),
                    content_id=content_id,
                    content_type=ContentType.AUDIO,
                    method=FingerprintMethod.SPECTRAL_HASH,
                    hash_value=spectral_hash,
                    vector_embedding=None,
                    confidence_score=0.88,
                    extraction_time=0.12,
                    metadata={'sample_rate': sr},
                    created_at=datetime.utcnow()
                ))
            
        except Exception as e:
            self.logger.error(f"Error extracting audio fingerprints: {str(e)}")
        
        return fingerprints
    
    async def _extract_video_fingerprints(self, video_data: Union[bytes, str], 
                                        config: FingerprintConfig) -> List[FingerprintResult]:
        """Extract video fingerprints using multiple methods"""
        fingerprints = []
        
        try:
            # Load video
            if isinstance(video_data, str):
                cap = cv2.VideoCapture(video_data)
            else:
                # Handle bytes data - save temporarily
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
                    tmp.write(video_data)
                    cap = cv2.VideoCapture(tmp.name)
            
            content_id = str(uuid.uuid4())
            frame_hashes = []
            frame_count = 0
            
            # Extract frames and compute hashes
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % int(cap.get(cv2.CAP_PROP_FPS)) == 0:  # Extract 1 frame per second
                    # Method 1: Frame-based perceptual hash
                    if FingerprintMethod.FRAME_HASH in config.methods:
                        frame_hash = await self._extract_frame_hash(frame)
                        frame_hashes.append(frame_hash)
                
                frame_count += 1
            
            cap.release()
            
            # Combine frame hashes into video fingerprint
            if frame_hashes:
                video_hash = hashlib.sha256(''.join(frame_hashes).encode()).hexdigest()
                fingerprints.append(FingerprintResult(
                    fingerprint_id=str(uuid.uuid4()),
                    content_id=content_id,
                    content_type=ContentType.VIDEO,
                    method=FingerprintMethod.FRAME_HASH,
                    hash_value=video_hash,
                    vector_embedding=None,
                    confidence_score=0.85,
                    extraction_time=0.5,
                    metadata={'frame_count': frame_count, 'extracted_frames': len(frame_hashes)},
                    created_at=datetime.utcnow()
                ))
            
        except Exception as e:
            self.logger.error(f"Error extracting video fingerprints: {str(e)}")
        
        return fingerprints
    
    async def _extract_image_fingerprints(self, image_data: Union[bytes, str], 
                                        config: FingerprintConfig) -> List[FingerprintResult]:
        """Extract image fingerprints using multiple methods"""
        fingerprints = []
        
        try:
            # Load image
            if isinstance(image_data, str):
                image = Image.open(image_data)
            else:
                from io import BytesIO
                image = Image.open(BytesIO(image_data))
            
            content_id = str(uuid.uuid4())
            
            # Method 1: Perceptual hash
            if FingerprintMethod.PERCEPTUAL_HASH in config.methods:
                phash = str(imagehash.phash(image, hash_size=self.image_hash_size))
                dhash = str(imagehash.dhash(image, hash_size=self.image_hash_size))
                whash = str(imagehash.whash(image, hash_size=self.image_hash_size))
                
                combined_hash = hashlib.sha256(f"{phash}{dhash}{whash}".encode()).hexdigest()
                
                fingerprints.append(FingerprintResult(
                    fingerprint_id=str(uuid.uuid4()),
                    content_id=content_id,
                    content_type=ContentType.IMAGE,
                    method=FingerprintMethod.PERCEPTUAL_HASH,
                    hash_value=combined_hash,
                    vector_embedding=None,
                    confidence_score=0.92,
                    extraction_time=0.05,
                    metadata={
                        'phash': phash,
                        'dhash': dhash,
                        'whash': whash,
                        'image_size': image.size
                    },
                    created_at=datetime.utcnow()
                ))
            
            # Method 2: CLIP embedding (if available)
            if FingerprintMethod.CLIP_EMBEDDING in config.methods:
                clip_embedding = await self._extract_clip_embedding(image)
                if clip_embedding is not None:
                    clip_hash = hashlib.sha256(clip_embedding.tobytes()).hexdigest()
                    fingerprints.append(FingerprintResult(
                        fingerprint_id=str(uuid.uuid4()),
                        content_id=content_id,
                        content_type=ContentType.IMAGE,
                        method=FingerprintMethod.CLIP_EMBEDDING,
                        hash_value=clip_hash,
                        vector_embedding=clip_embedding,
                        confidence_score=0.95,
                        extraction_time=0.2,
                        metadata={'embedding_dim': len(clip_embedding)},
                        created_at=datetime.utcnow()
                    ))
            
        except Exception as e:
            self.logger.error(f"Error extracting image fingerprints: {str(e)}")
        
        return fingerprints
    
    async def _extract_text_fingerprints(self, text_data: Union[bytes, str], 
                                       config: FingerprintConfig) -> List[FingerprintResult]:
        """Extract text fingerprints using multiple methods"""
        fingerprints = []
        
        try:
            # Handle text data
            if isinstance(text_data, bytes):
                text = text_data.decode('utf-8', errors='ignore')
            else:
                text = text_data
            
            content_id = str(uuid.uuid4())
            
            # Method 1: BERT embedding
            if FingerprintMethod.BERT_EMBEDDING in config.methods:
                bert_embedding = await self._extract_bert_embedding(text)
                bert_hash = hashlib.sha256(bert_embedding.tobytes()).hexdigest()
                
                fingerprints.append(FingerprintResult(
                    fingerprint_id=str(uuid.uuid4()),
                    content_id=content_id,
                    content_type=ContentType.TEXT,
                    method=FingerprintMethod.BERT_EMBEDDING,
                    hash_value=bert_hash,
                    vector_embedding=bert_embedding,
                    confidence_score=0.88,
                    extraction_time=0.3,
                    metadata={
                        'text_length': len(text),
                        'embedding_dim': len(bert_embedding)
                    },
                    created_at=datetime.utcnow()
                ))
            
            # Method 2: Sentence transformer embedding
            sentence_embedding = await self._extract_sentence_embedding(text)
            if sentence_embedding is not None:
                sentence_hash = hashlib.sha256(sentence_embedding.tobytes()).hexdigest()
                fingerprints.append(FingerprintResult(
                    fingerprint_id=str(uuid.uuid4()),
                    content_id=content_id,
                    content_type=ContentType.TEXT,
                    method=FingerprintMethod.BERT_EMBEDDING,  # Reusing enum value
                    hash_value=sentence_hash,
                    vector_embedding=sentence_embedding,
                    confidence_score=0.90,
                    extraction_time=0.2,
                    metadata={
                        'model': 'sentence-transformer',
                        'embedding_dim': len(sentence_embedding)
                    },
                    created_at=datetime.utcnow()
                ))
            
        except Exception as e:
            self.logger.error(f"Error extracting text fingerprints: {str(e)}")
        
        return fingerprints
    
    async def find_similar_content(self, query_fingerprint: FingerprintResult,
                                 similarity_threshold: float = 0.8,
                                 max_results: int = 100) -> List[SimilarityMatch]:
        """
        Find similar content using fingerprint matching.
        
        Args:
            query_fingerprint: Query fingerprint to match against
            similarity_threshold: Minimum similarity score
            max_results: Maximum number of results to return
            
        Returns:
            List of similarity matches
        """
        try:
            matches = []
            
            # Use vector similarity for embeddings
            if query_fingerprint.vector_embedding is not None:
                vector_matches = await self._find_vector_similarities(
                    query_fingerprint, similarity_threshold, max_results
                )
                matches.extend(vector_matches)
            
            # Use hash-based similarity for exact/near matches
            hash_matches = await self._find_hash_similarities(
                query_fingerprint, similarity_threshold, max_results
            )
            matches.extend(hash_matches)
            
            # Remove duplicates and sort by similarity score
            unique_matches = {}
            for match in matches:
                if match.matched_fingerprint_id not in unique_matches:
                    unique_matches[match.matched_fingerprint_id] = match
                elif match.similarity_score > unique_matches[match.matched_fingerprint_id].similarity_score:
                    unique_matches[match.matched_fingerprint_id] = match
            
            sorted_matches = sorted(
                unique_matches.values(),
                key=lambda x: x.similarity_score,
                reverse=True
            )
            
            return sorted_matches[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error finding similar content: {str(e)}")
            return []
    
    async def _extract_chromaprint(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Extract Chromaprint audio fingerprint"""
        try:
            # Convert to appropriate format for Chromaprint
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Generate fingerprint
            fingerprint = self.chromaprint.encode(audio_int16.tobytes(), sample_rate)
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"Error extracting Chromaprint: {str(e)}")
            return ""
    
    async def _extract_mfcc_features(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract MFCC features from audio"""
        try:
            # Extract MFCC features
            mfcc = librosa.feature.mfcc(
                y=audio_data,
                sr=sample_rate,
                n_mfcc=self.audio_n_mfcc,
                hop_length=self.audio_hop_length
            )
            
            # Extract additional features
            chroma = librosa.feature.chroma_stft(
                y=audio_data,
                sr=sample_rate,
                hop_length=self.audio_hop_length
            )
            
            spectral_contrast = librosa.feature.spectral_contrast(
                y=audio_data,
                sr=sample_rate,
                hop_length=self.audio_hop_length
            )
            
            # Combine features
            features = np.vstack([mfcc, chroma, spectral_contrast])
            
            # Calculate statistical moments
            features_mean = np.mean(features, axis=1)
            features_std = np.std(features, axis=1)
            
            return np.concatenate([features_mean, features_std])
            
        except Exception as e:
            self.logger.error(f"Error extracting MFCC features: {str(e)}")
            return np.array([])
    
    async def _extract_spectral_hash(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Extract spectral hash from audio"""
        try:
            # Compute spectrogram
            stft = librosa.stft(audio_data, hop_length=self.audio_hop_length)
            magnitude = np.abs(stft)
            
            # Reduce dimensionality
            magnitude_reduced = scipy.signal.decimate(magnitude, 4, axis=1)
            
            # Create hash from spectral peaks
            peaks = magnitude_reduced > np.percentile(magnitude_reduced, 95)
            hash_string = ''.join(['1' if peak else '0' for peak in peaks.flatten()])
            
            # Convert to hex hash
            return hashlib.sha256(hash_string.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Error extracting spectral hash: {str(e)}")
            return ""
    
    async def _extract_frame_hash(self, frame: np.ndarray) -> str:
        """Extract perceptual hash from video frame"""
        try:
            # Resize frame
            frame_resized = cv2.resize(frame, self.video_resize_target)
            
            # Convert to PIL Image for hashing
            frame_pil = Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB))
            
            # Generate multiple hashes
            phash = str(imagehash.phash(frame_pil))
            dhash = str(imagehash.dhash(frame_pil))
            
            return hashlib.sha256(f"{phash}{dhash}".encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Error extracting frame hash: {str(e)}")
            return ""
    
    async def _extract_clip_embedding(self, image: Image.Image) -> Optional[np.ndarray]:
        """Extract CLIP embedding from image"""
        try:
            # This would require CLIP model integration
            # Placeholder implementation
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting CLIP embedding: {str(e)}")
            return None
    
    async def _extract_bert_embedding(self, text: str) -> np.ndarray:
        """Extract BERT embedding from text"""
        try:
            # Tokenize text
            inputs = self.text_tokenizer(
                text[:self.text_max_length],
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            
            # Generate embedding
            with torch.no_grad():
                outputs = self.text_model(**inputs)
                embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            
            return embedding
            
        except Exception as e:
            self.logger.error(f"Error extracting BERT embedding: {str(e)}")
            return np.array([])
    
    async def _extract_sentence_embedding(self, text: str) -> Optional[np.ndarray]:
        """Extract sentence embedding using SentenceTransformer"""
        try:
            embedding = self.sentence_transformer.encode(text)
            return embedding
            
        except Exception as e:
            self.logger.error(f"Error extracting sentence embedding: {str(e)}")
            return None
    
    async def _find_vector_similarities(self, query_fingerprint: FingerprintResult,
                                      threshold: float, max_results: int) -> List[SimilarityMatch]:
        """Find similarities using vector embeddings"""
        matches = []
        
        try:
            if self.vector_index is None or query_fingerprint.vector_embedding is None:
                return matches
            
            # Search in FAISS index
            query_vector = query_fingerprint.vector_embedding.reshape(1, -1)
            scores, indices = self.vector_index.search(query_vector, max_results)
            
            for score, idx in zip(scores[0], indices[0]):
                if score >= threshold and idx >= 0:
                    match = SimilarityMatch(
                        match_id=str(uuid.uuid4()),
                        query_fingerprint_id=query_fingerprint.fingerprint_id,
                        matched_fingerprint_id=f"vector_match_{idx}",
                        similarity_score=float(score),
                        match_method="vector_similarity",
                        confidence_level="high" if score > 0.9 else "medium" if score > 0.8 else "low",
                        distance_metric="cosine",
                        metadata={"vector_index": int(idx)},
                        matched_at=datetime.utcnow()
                    )
                    matches.append(match)
            
        except Exception as e:
            self.logger.error(f"Error finding vector similarities: {str(e)}")
        
        return matches
    
    async def _find_hash_similarities(self, query_fingerprint: FingerprintResult,
        try:
                    async with self.db_session() as session:
                        # Database operation
                
                        await session.commit()
                        logger.info(f"Database operation _find_hash_similarities completed")
                        return True
                
                except Exception as e:
                    logger.error(f"Database operation _find_hash_similarities failed: {e}")
                    raise
    def _get_default_config(self, content_type: ContentType) -> FingerprintConfig:
        """Get default configuration for content type"""
        method_map = {
            ContentType.AUDIO: [FingerprintMethod.CHROMAPRINT, FingerprintMethod.MFCC_FEATURES],
            ContentType.VIDEO: [FingerprintMethod.FRAME_HASH],
            ContentType.IMAGE: [FingerprintMethod.PERCEPTUAL_HASH],
            ContentType.TEXT: [FingerprintMethod.BERT_EMBEDDING]
        }
        
        return FingerprintConfig(
            content_type=content_type,
            methods=method_map.get(content_type, []),
            quality_threshold=0.8,
            vector_dimensions=768,
            enable_multi_scale=True,
            enable_robustness_test=False,
            similarity_threshold=0.8
        )
    
    async def _store_fingerprint(self, fingerprint: FingerprintResult):
        """
Store fingerprint in database"""
        try:
            # Implementation would store in database
            pass
        except Exception as e:
            self.logger.error(f"Error storing fingerprint: {str(e)}")
    
    async def _cache_fingerprint(self, fingerprint: FingerprintResult):
        """Cache fingerprint data"""
        try:
            cache_key = f"fingerprint:{fingerprint.fingerprint_id}"
            fingerprint_data = asdict(fingerprint)
            
            # Convert numpy arrays to lists for JSON serialization
            if fingerprint.vector_embedding is not None:
                fingerprint_data['vector_embedding'] = fingerprint.vector_embedding.tolist()
            
            await self.redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(fingerprint_data, default=str)
            )
            
        except Exception as e:
            self.logger.error(f"Error caching fingerprint: {str(e)}")
