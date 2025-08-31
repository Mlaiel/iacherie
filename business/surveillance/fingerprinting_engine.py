"""🔬 Digital Fingerprinting Engine - IA Influencer Agent Surveillance Module
=========================================================================

Ultra-advanced digital fingerprinting system for multi-modal content identification,
similarity detection, and sophisticated content matching across all media types.

Architecture: Enterprise 3-Tier Professional (Backend Level 2)
Module: backend/business/surveillance/fingerprinting_engine.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================

Business Logic Flow:
Content Input → Multi-Modal Analysis → Feature Extraction → 
Fingerprint Generation → Vector Encoding → Database Storage → 
Similarity Indexing → Match Detection → Confidence Scoring → 
Results Ranking → Content Identification
"""import asyncio
import logging
import hashlib
import numpy as np
import librosa
import cv2
import torch
import torch.nn as nn
from PIL import Image, ImageHash
import imagehash
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoModel, AutoTokenizer, pipeline
import pickle
import json
import base64
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import uuid
import redis
from pathlib import Path
import tempfile
import subprocess
import io
from moviepy.editor import VideoFileClip
import wave
import struct
import math
import spacy
from collections import defaultdict
import sqlite3
import psycopg2
from sqlalchemy import create_engine, text
from chromaprint import compute_fingerprint

logger = logging.getLogger(__name__)


class FingerprintType(Enum):
    """Types of digital fingerprints"""    AUDIO_CHROMAPRINT = "audio_chromaprint"
    AUDIO_MFCC = "audio_mfcc"
    AUDIO_SPECTRAL = "audio_spectral"
    VIDEO_PERCEPTUAL = "video_perceptual"
    VIDEO_HISTOGRAM = "video_histogram"
    VIDEO_OPTICAL_FLOW = "video_optical_flow"
    IMAGE_PHASH = "image_phash"
    IMAGE_DHASH = "image_dhash"
    IMAGE_WHASH = "image_whash"
    IMAGE_AHASH = "image_ahash"
    IMAGE_DEEP = "image_deep"
    TEXT_TFIDF = "text_tfidf"
    TEXT_SEMANTIC = "text_semantic"
    TEXT_SYNTACTIC = "text_syntactic"
    COMBINED = "combined"


class SimilarityAlgorithm(Enum):
    """Similarity calculation algorithms"""    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    HAMMING = "hamming"
    JACCARD = "jaccard"
    PEARSON = "pearson"
    SPEARMAN = "spearman"
    DEEP_LEARNING = "deep_learning"


class MatchConfidence(Enum):
    """Match confidence levels"""    IDENTICAL = "identical"  # 95-100%
    VERY_HIGH = "very_high"  # 85-95%
    HIGH = "high"  # 70-85%
    MEDIUM = "medium"  # 50-70%
    LOW = "low"  # 20-50%
    VERY_LOW = "very_low"  # 0-20%


@dataclass
class ContentFingerprint:
    """Digital fingerprint for content"""    fingerprint_id: str
    content_id: str
    fingerprint_type: FingerprintType
    fingerprint_data: Union[np.ndarray, str, bytes]
    vector_embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 1.0
    extraction_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    algorithm_version: str = "1.0.0"
    processing_time: float = 0.0
    file_hash: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""        return {
            'fingerprint_id': self.fingerprint_id,
            'content_id': self.content_id,
            'fingerprint_type': self.fingerprint_type.value,
            'fingerprint_data': self._serialize_data(self.fingerprint_data),
            'vector_embedding': self._serialize_data(self.vector_embedding),
            'metadata': self.metadata,
            'confidence_score': self.confidence_score,
            'extraction_timestamp': self.extraction_timestamp.isoformat(),
            'algorithm_version': self.algorithm_version,
            'processing_time': self.processing_time,
            'file_hash': self.file_hash
        }
    
    def _serialize_data(self, data: Any) -> Optional[str]:
        """Serialize data for storage"""        if data is None:
            return None
        if isinstance(data, np.ndarray):
            return base64.b64encode(pickle.dumps(data)).decode('utf-8')
        if isinstance(data, (str, bytes)):
            if isinstance(data, bytes):
                return base64.b64encode(data).decode('utf-8')
            return data
        return str(data)


@dataclass
class SimilarityMatch:
    """Similarity match result"""    match_id: str
    source_fingerprint_id: str
    target_fingerprint_id: str
    similarity_score: float
    confidence_level: MatchConfidence
    algorithm_used: SimilarityAlgorithm
    match_details: Dict[str, Any] = field(default_factory=dict)
    detection_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    false_positive_probability: float = 0.0
    verification_status: str = "pending"


@dataclass
class FingerprintingResult:
    """Result of fingerprinting operation"""    content_id: str
    fingerprints: List[ContentFingerprint]
    processing_summary: Dict[str, Any]
    total_processing_time: float
    success_count: int
    failure_count: int
    errors: List[str] = field(default_factory=list)


class AudioFingerprintExtractor:
    """Advanced audio fingerprinting"""    
    def __init__(self):
        self.sample_rate = 22050
        self.hop_length = 512
        self.n_fft = 2048
        self.n_mels = 128
        self.n_mfcc = 13
    
    def extract_chromaprint(self, audio_path: str) -> Optional[str]:
        """Extract Chromaprint fingerprint"""        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Generate chromaprint
            fingerprint = compute_fingerprint(y, sr)
            return fingerprint
            
        except Exception as e:
            logger.error(f"Chromaprint extraction failed: {e}")
            return None
    
    def extract_mfcc_features(self, audio_path: str) -> Optional[np.ndarray]:
        """Extract MFCC features"""        try:
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Extract MFCC features
            mfcc = librosa.feature.mfcc(
                y=y, sr=sr, 
                n_mfcc=self.n_mfcc,
                hop_length=self.hop_length
            )
            
            # Calculate statistics
            mfcc_mean = np.mean(mfcc, axis=1)
            mfcc_std = np.std(mfcc, axis=1)
            mfcc_delta = np.mean(librosa.feature.delta(mfcc), axis=1)
            
            # Combine features
            features = np.concatenate([mfcc_mean, mfcc_std, mfcc_delta])
            
            return features
            
        except Exception as e:
            logger.error(f"MFCC extraction failed: {e}")
            return None
    
    def extract_spectral_features(self, audio_path: str) -> Optional[np.ndarray]:
        """Extract spectral features"""        try:
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Extract various spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
            
            # Calculate statistics
            features = np.array([
                np.mean(spectral_centroids),
                np.std(spectral_centroids),
                np.mean(spectral_rolloff),
                np.std(spectral_rolloff),
                np.mean(spectral_bandwidth),
                np.std(spectral_bandwidth),
                np.mean(zero_crossing_rate),
                np.std(zero_crossing_rate)
            ])
            
            return features
            
        except Exception as e:
            logger.error(f"Spectral feature extraction failed: {e}")
            return None


class VideoFingerprintExtractor:
    """Advanced video fingerprinting"""    
    def __init__(self):
        self.frame_sample_rate = 1  # Extract features every N frames
        self.target_resolution = (224, 224)
    
    def extract_perceptual_hash(self, video_path: str) -> Optional[List[str]]:
        """Extract perceptual hashes from video frames"""        try:
            clip = VideoFileClip(video_path)
            frame_hashes = []
            
            # Sample frames
            duration = clip.duration
            sample_times = np.arange(0, duration, self.frame_sample_rate)
            
            for t in sample_times:
                frame = clip.get_frame(t)
                frame_pil = Image.fromarray(frame)
                
                # Calculate perceptual hash
                phash = str(imagehash.phash(frame_pil))
                frame_hashes.append(phash)
            
            clip.close()
            return frame_hashes
            
        except Exception as e:
            logger.error(f"Video perceptual hash extraction failed: {e}")
            return None
    
    def extract_histogram_features(self, video_path: str) -> Optional[np.ndarray]:
        """Extract color histogram features"""        try:
            clip = VideoFileClip(video_path)
            histograms = []
            
            # Sample frames
            duration = clip.duration
            sample_times = np.arange(0, duration, 5.0)  # Every 5 seconds
            
            for t in sample_times:
                frame = clip.get_frame(t)
                
                # Calculate color histogram
                hist_r = cv2.calcHist([frame], [0], None, [256], [0, 256])
                hist_g = cv2.calcHist([frame], [1], None, [256], [0, 256])
                hist_b = cv2.calcHist([frame], [2], None, [256], [0, 256])
                
                # Normalize and combine
                hist = np.concatenate([
                    hist_r.flatten() / np.sum(hist_r),
                    hist_g.flatten() / np.sum(hist_g),
                    hist_b.flatten() / np.sum(hist_b)
                ])
                
                histograms.append(hist)
            
            clip.close()
            
            # Calculate average histogram
            if histograms:
                return np.mean(histograms, axis=0)
            
            return None
            
        except Exception as e:
            logger.error(f"Video histogram extraction failed: {e}")
            return None
    
    def extract_optical_flow_features(self, video_path: str) -> Optional[np.ndarray]:
        """Extract optical flow features"""        try:
            cap = cv2.VideoCapture(video_path)
            
            # Read first frame
            ret, frame1 = cap.read()
            if not ret:
                return None
            
            prev_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            flow_features = []
            
            while True:
                ret, frame2 = cap.read()
                if not ret:
                    break
                
                curr_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, None, None)
                
                if flow[0] is not None:
                    # Calculate flow statistics
                    magnitude = np.sqrt(flow[0][:, 0]**2 + flow[0][:, 1]**2)
                    angle = np.arctan2(flow[0][:, 1], flow[0][:, 0])
                    
                    features = np.array([
                        np.mean(magnitude),
                        np.std(magnitude),
                        np.mean(angle),
                        np.std(angle)
                    ])
                    
                    flow_features.append(features)
                
                prev_gray = curr_gray
            
            cap.release()
            
            if flow_features:
                return np.mean(flow_features, axis=0)
            
            return None
            
        except Exception as e:
            logger.error(f"Optical flow extraction failed: {e}")
            return None


class ImageFingerprintExtractor:
    """Advanced image fingerprinting"""    
    def __init__(self):
        # Initialize deep learning model for image features
        try:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            # We can use a pre-trained model like ResNet for feature extraction
        except:
            self.device = torch.device('cpu')
    
    def extract_perceptual_hashes(self, image_path: str) -> Optional[Dict[str, str]]:
        """Extract multiple perceptual hashes"""        try:
            image = Image.open(image_path)
            
            hashes = {
                'phash': str(imagehash.phash(image)),
                'dhash': str(imagehash.dhash(image)),
                'whash': str(imagehash.whash(image)),
                'ahash': str(imagehash.average_hash(image)),
                'phash_simple': str(imagehash.phash_simple(image)),
                'colorhash': str(imagehash.colorhash(image))
            }
            
            return hashes
            
        except Exception as e:
            logger.error(f"Image hash extraction failed: {e}")
            return None
    
    def extract_deep_features(self, image_path: str) -> Optional[np.ndarray]:
        """Extract deep learning features"""        try:
            # Load and preprocess image
            image = cv2.imread(image_path)
            image = cv2.resize(image, (224, 224))
            image = image.astype(np.float32) / 255.0
            
            # For now, use traditional computer vision features
            # In production, this would use a pre-trained CNN
            
            # Extract color moments
            moments = []
            for channel in range(3):
                channel_data = image[:, :, channel].flatten()
                moments.extend([
                    np.mean(channel_data),
                    np.std(channel_data),
                    np.mean((channel_data - np.mean(channel_data))**3)
                ])
            
            # Extract texture features using Local Binary Patterns
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray_uint8 = (gray * 255).astype(np.uint8)
            
            # Simple texture analysis
            sobel_x = cv2.Sobel(gray_uint8, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray_uint8, cv2.CV_64F, 0, 1, ksize=3)
            
            texture_features = [
                np.mean(sobel_x),
                np.std(sobel_x),
                np.mean(sobel_y),
                np.std(sobel_y)
            ]
            
            # Combine features
            features = np.array(moments + texture_features)
            
            return features
            
        except Exception as e:
            logger.error(f"Deep feature extraction failed: {e}")
            return None


class TextFingerprintExtractor:
    """Advanced text fingerprinting"""    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        
        # Initialize NLP models
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except:
            logger.warning("Spacy model not available, using basic text processing")
            self.nlp = None
        
        # Initialize semantic embedding model
        try:
            self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
            self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        except:
            logger.warning("Transformer model not available")
            self.tokenizer = None
            self.model = None
    
    def extract_tfidf_features(self, text: str) -> Optional[np.ndarray]:
        """Extract TF-IDF features"""        try:
            # Fit and transform text
            tfidf_matrix = self.vectorizer.fit_transform([text])
            return tfidf_matrix.toarray()[0]
            
        except Exception as e:
            logger.error(f"TF-IDF extraction failed: {e}")
            return None
    
    def extract_semantic_features(self, text: str) -> Optional[np.ndarray]:
        """Extract semantic embeddings"""        try:
            if not self.tokenizer or not self.model:
                return None
            
            # Tokenize and encode
            inputs = self.tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
            
            return embeddings.numpy().flatten()
            
        except Exception as e:
            logger.error(f"Semantic feature extraction failed: {e}")
            return None
    
    def extract_syntactic_features(self, text: str) -> Optional[np.ndarray]:
        """Extract syntactic features"""        try:
            if not self.nlp:
                # Basic syntactic features without spacy
                features = [
                    len(text),
                    len(text.split()),
                    len([c for c in text if c.isupper()]),
                    len([c for c in text if c.islower()]),
                    len([c for c in text if c.isdigit()]),
                    text.count('.'),
                    text.count(','),
                    text.count('!'),
                    text.count('?')
                ]
                return np.array(features)
            
            doc = self.nlp(text)
            
            # Extract syntactic features
            pos_counts = defaultdict(int)
            dep_counts = defaultdict(int)
            
            for token in doc:
                pos_counts[token.pos_] += 1
                dep_counts[token.dep_] += 1
            
            # Create feature vector
            features = [
                len(doc),
                len(list(doc.sents)),
                sum(1 for token in doc if token.is_alpha),
                sum(1 for token in doc if token.is_digit),
                sum(1 for token in doc if token.is_punct),
                pos_counts.get('NOUN', 0),
                pos_counts.get('VERB', 0),
                pos_counts.get('ADJ', 0),
                pos_counts.get('ADV', 0)
            ]
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Syntactic feature extraction failed: {e}")
            return None


class FingerprintingEngine:
    """    Ultra-Advanced Digital Fingerprinting Engine
    
    Provides comprehensive content fingerprinting across all media types
    with sophisticated similarity matching and content identification.
    """    
    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        database_url: Optional[str] = None,
        storage_path: Optional[Path] = None,
        faiss_index_path: Optional[Path] = None
    ):
        """Initialize fingerprinting engine"""        self.redis_client = redis_client or redis.Redis(decode_responses=False)
        self.database_url = database_url
        self.storage_path = storage_path or Path("fingerprints")
        self.storage_path.mkdir(exist_ok=True)
        
        # Initialize extractors
        self.audio_extractor = AudioFingerprintExtractor()
        self.video_extractor = VideoFingerprintExtractor()
        self.image_extractor = ImageFingerprintExtractor()
        self.text_extractor = TextFingerprintExtractor()
        
        # Initialize FAISS indices for vector similarity
        self.faiss_indices = {}
        self.faiss_index_path = faiss_index_path or (self.storage_path / "faiss_indices")
        self.faiss_index_path.mkdir(exist_ok=True)
        
        # Internal state
        self.fingerprint_cache = {}
        self.similarity_cache = {}
        
        # Configuration
        self.similarity_threshold = 0.8
        self.batch_size = 100
        
        # Initialize database and indices
        self._initialize_database()
        self._load_faiss_indices()
        
        logger.info("FingerprintingEngine initialized successfully")
    
    def _initialize_database(self):
        """Initialize database connection and tables"""        try:
            if self.database_url:
                self.engine = create_engine(self.database_url)
                self._create_fingerprint_tables()
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            self.engine = None
    
    def _create_fingerprint_tables(self):
        """Create fingerprint tables"""        tables_sql = """        CREATE TABLE IF NOT EXISTS content_fingerprints (
            id SERIAL PRIMARY KEY,
            fingerprint_id VARCHAR(255) UNIQUE NOT NULL,
            content_id VARCHAR(255) NOT NULL,
            fingerprint_type VARCHAR(100) NOT NULL,
            fingerprint_data TEXT,
            vector_embedding BYTEA,
            metadata JSONB,
            confidence_score FLOAT DEFAULT 1.0,
            extraction_timestamp TIMESTAMP DEFAULT NOW(),
            algorithm_version VARCHAR(50),
            processing_time FLOAT DEFAULT 0.0,
            file_hash VARCHAR(255)
        );
        
        CREATE TABLE IF NOT EXISTS similarity_matches (
            id SERIAL PRIMARY KEY,
            match_id VARCHAR(255) UNIQUE NOT NULL,
            source_fingerprint_id VARCHAR(255) NOT NULL,
            target_fingerprint_id VARCHAR(255) NOT NULL,
            similarity_score FLOAT NOT NULL,
            confidence_level VARCHAR(50),
            algorithm_used VARCHAR(50),
            match_details JSONB,
            detection_timestamp TIMESTAMP DEFAULT NOW(),
            false_positive_probability FLOAT DEFAULT 0.0,
            verification_status VARCHAR(50) DEFAULT 'pending'
        );
        
        CREATE INDEX IF NOT EXISTS idx_fingerprints_content_id ON content_fingerprints(content_id);
        CREATE INDEX IF NOT EXISTS idx_fingerprints_type ON content_fingerprints(fingerprint_type);
        CREATE INDEX IF NOT EXISTS idx_matches_similarity ON similarity_matches(similarity_score DESC);
        """        
        if self.engine:
            with self.engine.begin() as conn:
                conn.execute(text(tables_sql))
    
    def _load_faiss_indices(self):
        """Load existing FAISS indices"""        try:
            for index_file in self.faiss_index_path.glob("*.faiss"):
                index_name = index_file.stem
                try:
                    index = faiss.read_index(str(index_file))
                    self.faiss_indices[index_name] = index
                    logger.info(f"Loaded FAISS index: {index_name}")
                except Exception as e:
                    logger.error(f"Failed to load FAISS index {index_name}: {e}")
        except Exception as e:
            logger.error(f"Failed to load FAISS indices: {e}")
    
    async def generate_fingerprints(
        self,
        content_path: str,
        content_id: str,
        fingerprint_types: Optional[List[FingerprintType]] = None
    ) -> FingerprintingResult:
        """Generate comprehensive fingerprints for content"""        try:
            start_time = datetime.now()
            fingerprints = []
            errors = []
            success_count = 0
            failure_count = 0
            
            # Determine content type
            content_type = self._detect_content_type(content_path)
            
            # Default fingerprint types based on content
            if not fingerprint_types:
                fingerprint_types = self._get_default_fingerprint_types(content_type)
            
            # Generate fingerprints
            for fp_type in fingerprint_types:
                try:
                    fingerprint = await self._generate_single_fingerprint(
                        content_path, content_id, fp_type
                    )
                    
                    if fingerprint:
                        fingerprints.append(fingerprint)
                        success_count += 1
                    else:
                        failure_count += 1
                        errors.append(f"Failed to generate {fp_type.value} fingerprint")
                        
                except Exception as e:
                    failure_count += 1
                    errors.append(f"Error generating {fp_type.value}: {str(e)}")
                    logger.error(f"Fingerprint generation error: {e}")
            
            # Store fingerprints
            for fingerprint in fingerprints:
                await self._store_fingerprint(fingerprint)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = FingerprintingResult(
                content_id=content_id,
                fingerprints=fingerprints,
                processing_summary={
                    'content_type': content_type,
                    'fingerprint_types_requested': [ft.value for ft in fingerprint_types],
                    'fingerprint_types_generated': [fp.fingerprint_type.value for fp in fingerprints]
                },
                total_processing_time=processing_time,
                success_count=success_count,
                failure_count=failure_count,
                errors=errors
            )
            
            logger.info(f"Generated {len(fingerprints)} fingerprints for {content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Fingerprinting failed for {content_id}: {e}")
            raise
    
    def _detect_content_type(self, content_path: str) -> str:
        """Detect content type from file"""        try:
            # Use python-magic if available, otherwise use mimetypes
            try:
                import magic
                mime = magic.from_file(content_path, mime=True)
            except:
                mime, _ = mimetypes.guess_type(content_path)
            
            if mime:
                if mime.startswith('audio/'):
                    return 'audio'
                elif mime.startswith('video/'):
                    return 'video'
                elif mime.startswith('image/'):
                    return 'image'
                elif mime.startswith('text/'):
                    return 'text'
            
            # Fallback to file extension
            ext = Path(content_path).suffix.lower()
            
            audio_exts = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'}
            video_exts = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
            image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
            text_exts = {'.txt', '.md', '.doc', '.docx', '.pdf'}
            
            if ext in audio_exts:
                return 'audio'
            elif ext in video_exts:
                return 'video'
            elif ext in image_exts:
                return 'image'
            elif ext in text_exts:
                return 'text'
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"Content type detection failed: {e}")
            return 'unknown'
    
    def _get_default_fingerprint_types(self, content_type: str) -> List[FingerprintType]:
        """Get default fingerprint types for content type"""        type_mapping = {
            'audio': [
                FingerprintType.AUDIO_CHROMAPRINT,
                FingerprintType.AUDIO_MFCC,
                FingerprintType.AUDIO_SPECTRAL
            ],
            'video': [
                FingerprintType.VIDEO_PERCEPTUAL,
                FingerprintType.VIDEO_HISTOGRAM,
                FingerprintType.AUDIO_CHROMAPRINT  # Extract audio from video
            ],
            'image': [
                FingerprintType.IMAGE_PHASH,
                FingerprintType.IMAGE_DHASH,
                FingerprintType.IMAGE_DEEP
            ],
            'text': [
                FingerprintType.TEXT_TFIDF,
                FingerprintType.TEXT_SEMANTIC,
                FingerprintType.TEXT_SYNTACTIC
            ]
        }
        
        return type_mapping.get(content_type, [FingerprintType.COMBINED])
    
    async def _generate_single_fingerprint(
        self,
        content_path: str,
        content_id: str,
        fingerprint_type: FingerprintType
    ) -> Optional[ContentFingerprint]:
        """Generate a single fingerprint"""        try:
            start_time = datetime.now()
            fingerprint_data = None
            vector_embedding = None
            
            # Generate fingerprint based on type
            if fingerprint_type == FingerprintType.AUDIO_CHROMAPRINT:
                fingerprint_data = self.audio_extractor.extract_chromaprint(content_path)
            
            elif fingerprint_type == FingerprintType.AUDIO_MFCC:
                fingerprint_data = self.audio_extractor.extract_mfcc_features(content_path)
                if fingerprint_data is not None:
                    vector_embedding = fingerprint_data
            
            elif fingerprint_type == FingerprintType.AUDIO_SPECTRAL:
                fingerprint_data = self.audio_extractor.extract_spectral_features(content_path)
                if fingerprint_data is not None:
                    vector_embedding = fingerprint_data
            
            elif fingerprint_type == FingerprintType.VIDEO_PERCEPTUAL:
                fingerprint_data = self.video_extractor.extract_perceptual_hash(content_path)
            
            elif fingerprint_type == FingerprintType.VIDEO_HISTOGRAM:
                fingerprint_data = self.video_extractor.extract_histogram_features(content_path)
                if fingerprint_data is not None:
                    vector_embedding = fingerprint_data
            
            elif fingerprint_type == FingerprintType.IMAGE_PHASH:
                hash_data = self.image_extractor.extract_perceptual_hashes(content_path)
                if hash_data:
                    fingerprint_data = hash_data.get('phash')
            
            elif fingerprint_type == FingerprintType.IMAGE_DEEP:
                fingerprint_data = self.image_extractor.extract_deep_features(content_path)
                if fingerprint_data is not None:
                    vector_embedding = fingerprint_data
            
            elif fingerprint_type == FingerprintType.TEXT_TFIDF:
                # Assume content_path contains text or is a text file
                with open(content_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                fingerprint_data = self.text_extractor.extract_tfidf_features(text)
                if fingerprint_data is not None:
                    vector_embedding = fingerprint_data
            
            elif fingerprint_type == FingerprintType.TEXT_SEMANTIC:
                with open(content_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                fingerprint_data = self.text_extractor.extract_semantic_features(text)
                if fingerprint_data is not None:
                    vector_embedding = fingerprint_data
            
            if fingerprint_data is None:
                return None
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Generate file hash
            file_hash = self._calculate_file_hash(content_path)
            
            # Create fingerprint object
            fingerprint = ContentFingerprint(
                fingerprint_id=str(uuid.uuid4()),
                content_id=content_id,
                fingerprint_type=fingerprint_type,
                fingerprint_data=fingerprint_data,
                vector_embedding=vector_embedding,
                processing_time=processing_time,
                file_hash=file_hash
            )
            
            return fingerprint
            
        except Exception as e:
            logger.error(f"Single fingerprint generation failed: {e}")
            return None
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"File hash calculation failed: {e}")
            return ""
    
    async def _store_fingerprint(self, fingerprint: ContentFingerprint):
        """Store fingerprint in database and cache"""        try:
            # Store in cache
            self.fingerprint_cache[fingerprint.fingerprint_id] = fingerprint
            
            # Store in Redis
            fingerprint_data = fingerprint.to_dict()
            await asyncio.to_thread(
                self.redis_client.hset,
                f"fingerprint:{fingerprint.fingerprint_id}",
                mapping={k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) 
                        for k, v in fingerprint_data.items()}
            )
            
            # Store in database
            if self.engine:
                insert_sql = """                INSERT INTO content_fingerprints (
                    fingerprint_id, content_id, fingerprint_type,
                    fingerprint_data, vector_embedding, metadata,
                    confidence_score, extraction_timestamp, algorithm_version,
                    processing_time, file_hash
                ) VALUES (
                    :fingerprint_id, :content_id, :fingerprint_type,
                    :fingerprint_data, :vector_embedding, :metadata,
                    :confidence_score, :extraction_timestamp, :algorithm_version,
                    :processing_time, :file_hash
                )
                """                
                with self.engine.begin() as conn:
                    conn.execute(text(insert_sql), {
                        'fingerprint_id': fingerprint.fingerprint_id,
                        'content_id': fingerprint.content_id,
                        'fingerprint_type': fingerprint.fingerprint_type.value,
                        'fingerprint_data': fingerprint._serialize_data(fingerprint.fingerprint_data),
                        'vector_embedding': fingerprint._serialize_data(fingerprint.vector_embedding),
                        'metadata': json.dumps(fingerprint.metadata),
                        'confidence_score': fingerprint.confidence_score,
                        'extraction_timestamp': fingerprint.extraction_timestamp,
                        'algorithm_version': fingerprint.algorithm_version,
                        'processing_time': fingerprint.processing_time,
                        'file_hash': fingerprint.file_hash
                    })
            
            # Update FAISS index if vector embedding exists
            if fingerprint.vector_embedding is not None:
                await self._update_faiss_index(fingerprint)
                
        except Exception as e:
            logger.error(f"Fingerprint storage failed: {e}")
    
    async def _update_faiss_index(self, fingerprint: ContentFingerprint):
        """Update FAISS index with new vector"""        try:
            index_name = f"{fingerprint.fingerprint_type.value}_vectors"
            
            if index_name not in self.faiss_indices:
                # Create new index
                dimension = len(fingerprint.vector_embedding)
                index = faiss.IndexFlatL2(dimension)
                self.faiss_indices[index_name] = index
            
            # Add vector to index
            vector = fingerprint.vector_embedding.reshape(1, -1).astype(np.float32)
            self.faiss_indices[index_name].add(vector)
            
            # Save index
            index_path = self.faiss_index_path / f"{index_name}.faiss"
            faiss.write_index(self.faiss_indices[index_name], str(index_path))
            
        except Exception as e:
            logger.error(f"FAISS index update failed: {e}")
    
    async def find_similar_content(
        self,
        query_fingerprint: ContentFingerprint,
        similarity_threshold: Optional[float] = None,
        max_results: int = 10
    ) -> List[SimilarityMatch]:
        """Find similar content using fingerprint matching"""        try:
            threshold = similarity_threshold or self.similarity_threshold
            matches = []
            
            # Vector-based similarity search using FAISS
            if query_fingerprint.vector_embedding is not None:
                vector_matches = await self._search_vector_similarity(
                    query_fingerprint, threshold, max_results
                )
                matches.extend(vector_matches)
            
            # Hash-based similarity search
            if isinstance(query_fingerprint.fingerprint_data, str):
                hash_matches = await self._search_hash_similarity(
                    query_fingerprint, threshold, max_results
                )
                matches.extend(hash_matches)
            
            # Sort by similarity score
            matches.sort(key=lambda x: x.similarity_score, reverse=True)
            
            return matches[:max_results]
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    async def _search_vector_similarity(
        self,
        query_fingerprint: ContentFingerprint,
        threshold: float,
        max_results: int
    ) -> List[SimilarityMatch]:
        """Search for similar vectors using FAISS"""        try:
            matches = []
            index_name = f"{query_fingerprint.fingerprint_type.value}_vectors"
            
            if index_name not in self.faiss_indices:
                return matches
            
            index = self.faiss_indices[index_name]
            query_vector = query_fingerprint.vector_embedding.reshape(1, -1).astype(np.float32)
            
            # Search for similar vectors
            distances, indices = index.search(query_vector, max_results * 2)
            
            # Convert distances to similarity scores
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1:  # No more results
                    break
                
                # Convert L2 distance to similarity score (0-1)
                similarity_score = 1.0 / (1.0 + distance)
                
                if similarity_score >= threshold:
                    # Get fingerprint ID (this is simplified - in production,
                    # you'd maintain a mapping between FAISS indices and fingerprint IDs)
                    match = SimilarityMatch(
                        match_id=str(uuid.uuid4()),
                        source_fingerprint_id=query_fingerprint.fingerprint_id,
                        target_fingerprint_id=f"target_{idx}",  # Simplified
                        similarity_score=similarity_score,
                        confidence_level=self._get_confidence_level(similarity_score),
                        algorithm_used=SimilarityAlgorithm.COSINE,
                        match_details={'distance': float(distance), 'faiss_index': idx}
                    )
                    matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Vector similarity search failed: {e}")
            return []
    
    async def _search_hash_similarity(
        self,
        query_fingerprint: ContentFingerprint,
        threshold: float,
        max_results: int
    ) -> List[SimilarityMatch]:
        """Search for similar hashes"""        try:
            matches = []
            
            # Get all fingerprints of the same type from database
            if not self.engine:
                return matches
            
            select_sql = """            SELECT fingerprint_id, fingerprint_data
            FROM content_fingerprints
            WHERE fingerprint_type = :fingerprint_type
            AND fingerprint_id != :query_fingerprint_id
            LIMIT :max_results
            """            
            with self.engine.begin() as conn:
                result = conn.execute(text(select_sql), {
                    'fingerprint_type': query_fingerprint.fingerprint_type.value,
                    'query_fingerprint_id': query_fingerprint.fingerprint_id,
                    'max_results': max_results * 5  # Get more to filter
                })
                
                for row in result.fetchall():
                    row_dict = dict(row._mapping)
                    
                    # Calculate similarity
                    similarity_score = self._calculate_hash_similarity(
                        query_fingerprint.fingerprint_data,
                        row_dict['fingerprint_data']
                    )
                    
                    if similarity_score >= threshold:
                        match = SimilarityMatch(
                            match_id=str(uuid.uuid4()),
                            source_fingerprint_id=query_fingerprint.fingerprint_id,
                            target_fingerprint_id=row_dict['fingerprint_id'],
                            similarity_score=similarity_score,
                            confidence_level=self._get_confidence_level(similarity_score),
                            algorithm_used=SimilarityAlgorithm.HAMMING,
                            match_details={'hash_comparison': True}
                        )
                        matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Hash similarity search failed: {e}")
            return []
    
    def _calculate_hash_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity between two hashes"""        try:
            if not hash1 or not hash2:
                return 0.0
            
            # For perceptual hashes, use Hamming distance
            if len(hash1) == len(hash2):
                hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
                similarity = 1.0 - (hamming_distance / len(hash1))
                return similarity
            
            # For other string comparisons, use character-level similarity
            from difflib import SequenceMatcher
            similarity = SequenceMatcher(None, hash1, hash2).ratio()
            return similarity
            
        except Exception as e:
            logger.error(f"Hash similarity calculation failed: {e}")
            return 0.0
    
    def _get_confidence_level(self, similarity_score: float) -> MatchConfidence:
        """Convert similarity score to confidence level"""        if similarity_score >= 0.95:
            return MatchConfidence.IDENTICAL
        elif similarity_score >= 0.85:
            return MatchConfidence.VERY_HIGH
        elif similarity_score >= 0.70:
            return MatchConfidence.HIGH
        elif similarity_score >= 0.50:
            return MatchConfidence.MEDIUM
        elif similarity_score >= 0.20:
            return MatchConfidence.LOW
        else:
            return MatchConfidence.VERY_LOW
    
    async def batch_fingerprint_generation(
        self,
        content_list: List[Tuple[str, str]],  # (content_path, content_id)
        fingerprint_types: Optional[List[FingerprintType]] = None
    ) -> List[FingerprintingResult]:
        """Generate fingerprints for multiple content items"""        try:
            results = []
            
            # Process in batches
            for i in range(0, len(content_list), self.batch_size):
                batch = content_list[i:i + self.batch_size]
                
                # Process batch concurrently
                batch_tasks = [
                    self.generate_fingerprints(content_path, content_id, fingerprint_types)
                    for content_path, content_id in batch
                ]
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.error(f"Batch processing error: {result}")
                    else:
                        results.append(result)
            
            logger.info(f"Processed {len(results)} content items in batches")
            return results
            
        except Exception as e:
            logger.error(f"Batch fingerprinting failed: {e}")
            return []
    
    async def get_fingerprint_statistics(self) -> Dict[str, Any]:
        """Get fingerprint database statistics"""        try:
            stats = {
                'total_fingerprints': 0,
                'fingerprint_types': {},
                'content_distribution': {},
                'processing_times': {},
                'storage_size': 0
            }
            
            if self.engine:
                # Get basic statistics
                stats_sql = """                SELECT 
                    COUNT(*) as total_fingerprints,
                    fingerprint_type,
                    COUNT(*) as type_count,
                    AVG(processing_time) as avg_processing_time
                FROM content_fingerprints
                GROUP BY fingerprint_type
                """                
                with self.engine.begin() as conn:
                    result = conn.execute(text(stats_sql))
                    
                    for row in result.fetchall():
                        row_dict = dict(row._mapping)
                        fp_type = row_dict['fingerprint_type']
                        
                        stats['fingerprint_types'][fp_type] = row_dict['type_count']
                        stats['processing_times'][fp_type] = row_dict['avg_processing_time']
                    
                    # Get total count
                    total_sql = "SELECT COUNT(*) as total FROM content_fingerprints"
                    total_result = conn.execute(text(total_sql))
                    stats['total_fingerprints'] = total_result.fetchone()[0]
            
            # Add FAISS index information
            stats['faiss_indices'] = {}
            for index_name, index in self.faiss_indices.items():
                stats['faiss_indices'][index_name] = {
                    'total_vectors': index.ntotal,
                    'dimension': index.d
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    async def cleanup_expired_fingerprints(self, retention_days: int = 90):
        """Clean up old fingerprints"""        try:
            if not self.engine:
                return
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
            
            cleanup_sql = """            DELETE FROM content_fingerprints
            WHERE extraction_timestamp < :cutoff_date
            """            
            with self.engine.begin() as conn:
                result = conn.execute(text(cleanup_sql), {'cutoff_date': cutoff_date})
                deleted_count = result.rowcount
            
            # Clear Redis cache
            pattern = "fingerprint:*"
            keys = await asyncio.to_thread(self.redis_client.keys, pattern)
            if keys:
                await asyncio.to_thread(self.redis_client.delete, *keys)
            
            # Rebuild FAISS indices (simplified approach)
            # In production, you'd want a more sophisticated approach
            for index_name in list(self.faiss_indices.keys()):
                index_path = self.faiss_index_path / f"{index_name}.faiss"
                if index_path.exists():
                    index_path.unlink()
                del self.faiss_indices[index_name]
            
            logger.info(f"Cleaned up {deleted_count} expired fingerprints")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
