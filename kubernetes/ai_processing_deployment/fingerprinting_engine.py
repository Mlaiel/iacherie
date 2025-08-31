"""
AI Fingerprinting Engine for Multi-Format Content Analysis
=========================================================

Enterprise-grade fingerprinting engine supporting audio, video, image, and text
content with advanced AI-powered similarity detection and vector matching.

Features:
- Multi-format content fingerprinting (audio, video, image, text)
- Advanced perceptual hashing algorithms
- Vector embeddings for semantic similarity
- Real-time similarity matching with FAISS
- Enterprise-scale performance optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialization: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
                    Security + Microservices + Audio + DevOps + IA Prompt Engineer

  WARNING: PROPRIETARY CODE
All code, concepts, and implementations in this module are proprietary 
intellectual property of Fahed Mlaiel. Any unauthorized use, copying, 
distribution, or commercial exploitation without explicit written 
permission is strictly prohibited and will result in legal action.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import hashlib
import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
import json
import base64

import numpy as np
import cv2
from PIL import Image
import librosa
import essentia.standard as es
import chromaprint
import imagehash
import torch
import tensorflow as tf
from transformers import CLIPProcessor, CLIPModel, BertTokenizer, BertModel
from sentence_transformers import SentenceTransformer
import faiss
from prometheus_client import Counter, Histogram, Gauge

from .core import ProcessingTask, ProcessingStatus, AIModelType

# Metrics
fingerprint_operations_total = Counter('fingerprint_operations_total', 'Total fingerprinting operations', ['content_type'])
fingerprint_processing_time = Histogram('fingerprint_processing_time_seconds', 'Fingerprinting processing time', ['content_type'])
fingerprint_accuracy_score = Gauge('fingerprint_accuracy_score', 'Fingerprinting accuracy score', ['content_type'])
similarity_search_time = Histogram('similarity_search_time_seconds', 'Similarity search time')

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content types for fingerprinting."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"


class FingerprintType(Enum):
    """Types of fingerprints generated."""
    PERCEPTUAL_HASH = "perceptual_hash"
    SPECTRAL_HASH = "spectral_hash"
    VECTOR_EMBEDDING = "vector_embedding"
    CONTENT_HASH = "content_hash"
    FEATURE_HASH = "feature_hash"


@dataclass
class FingerprintResult:
    """Result of fingerprinting operation."""
    content_id: str
    content_type: ContentType
    fingerprint_type: FingerprintType
    hash_value: str
    vector_embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = None
    confidence_score: float = 1.0
    processing_time_ms: float = 0.0
    created_at: datetime = None


@dataclass
class SimilarityMatch:
    """Similarity match result."""
    original_id: str
    matched_id: str
    similarity_score: float
    fingerprint_type: FingerprintType
    content_type: ContentType
    metadata: Dict[str, Any] = None
    found_at: datetime = None


class AudioFingerprintEngine:
    """
    Advanced audio fingerprinting engine using multiple algorithms
    for robust content identification and similarity detection.
    """
    
    def __init__(self, sample_rate: int = 22050, feature_size: int = 512):
        """Initialize audio fingerprinting engine."""
        self.sample_rate = sample_rate
        self.feature_size = feature_size
        self.windowing = es.Windowing(type='hann')
        self.spectrum = es.Spectrum()
        self.mfcc = es.MFCC()
        self.spectral_peaks = es.SpectralPeaks()
        
    async def generate_fingerprint(self, audio_data: Union[str, np.ndarray], 
                                 metadata: Dict[str, Any] = None) -> List[FingerprintResult]:
        """
        Generate comprehensive audio fingerprints using multiple algorithms.
        
        Args:
            audio_data: Audio file path or numpy array
            metadata: Additional metadata for the audio
            
        Returns:
            List[FingerprintResult]: Generated fingerprints
        """
        start_time = time.time()
        fingerprints = []
        
        try:
            # Load audio if path provided
            if isinstance(audio_data, str):
                audio, sr = librosa.load(audio_data, sr=self.sample_rate)
            else:
                audio = audio_data
                sr = self.sample_rate
                
            content_id = str(uuid.uuid4())
            
            # 1. Chromaprint fingerprint
            chromaprint_result = await self._generate_chromaprint(audio, sr, content_id, metadata)
            if chromaprint_result:
                fingerprints.append(chromaprint_result)
            
            # 2. Spectral features fingerprint
            spectral_result = await self._generate_spectral_features(audio, sr, content_id, metadata)
            if spectral_result:
                fingerprints.append(spectral_result)
            
            # 3. MFCC-based fingerprint
            mfcc_result = await self._generate_mfcc_fingerprint(audio, sr, content_id, metadata)
            if mfcc_result:
                fingerprints.append(mfcc_result)
            
            # 4. Perceptual hash
            perceptual_result = await self._generate_perceptual_hash(audio, sr, content_id, metadata)
            if perceptual_result:
                fingerprints.append(perceptual_result)
                
            processing_time = (time.time() - start_time) * 1000
            
            # Update metrics
            fingerprint_operations_total.labels(content_type='audio').inc()
            fingerprint_processing_time.labels(content_type='audio').observe(processing_time / 1000)
            
            logger.info(f"Generated {len(fingerprints)} audio fingerprints in {processing_time:.2f}ms")
            
            return fingerprints
            
        except Exception as e:
            logger.error(f"Audio fingerprinting failed: {e}")
            return []
    
    async def _generate_chromaprint(self, audio: np.ndarray, sr: int, 
                                  content_id: str, metadata: Dict[str, Any]) -> Optional[FingerprintResult]:
        """Generate Chromaprint-based fingerprint."""



        try:
            # Convert to int16 for chromaprint
            audio_int16 = (audio * 32767).astype(np.int16)
            
            # Generate chromaprint
            fingerprint_data = chromaprint.encode(audio_int16, sr)
            hash_value = base64.b64encode(fingerprint_data).decode('utf-8')
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.AUDIO,
                fingerprint_type=FingerprintType.CONTENT_HASH,
                hash_value=hash_value,
                metadata=metadata,
                confidence_score=0.95,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Chromaprint generation failed: {e}")
            return None
    
    async def _generate_spectral_features(self, audio: np.ndarray, sr: int,
                                        content_id: str, metadata: Dict[str, Any]) -> Optional[FingerprintResult]:
        """Generate spectral features-based fingerprint."""



        try:
            # Extract spectral features
            stft = librosa.stft(audio, n_fft=2048, hop_length=512)
            spectral_centroids = librosa.feature.spectral_centroid(S=np.abs(stft))[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(S=np.abs(stft))[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)[0]
            
            # Combine features
            features = np.concatenate([
                spectral_centroids[:100],  # First 100 frames
                spectral_rolloff[:100],
                zero_crossing_rate[:100]
            ])
            
            # Create hash from features
            features_bytes = features.tobytes()
            hash_value = hashlib.sha256(features_bytes).hexdigest()
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.AUDIO,
                fingerprint_type=FingerprintType.SPECTRAL_HASH,
                hash_value=hash_value,
                vector_embedding=features,
                metadata=metadata,
                confidence_score=0.88,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Spectral features generation failed: {e}")
            return None
    
    async def _generate_mfcc_fingerprint(self, audio: np.ndarray, sr: int,
                                       content_id: str, metadata: Dict[str, Any]) -> Optional[FingerprintResult]:
        """Generate MFCC-based fingerprint."""



        try:
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            
            # Statistical features from MFCCs
            mfcc_features = np.concatenate([
                np.mean(mfccs, axis=1),
                np.std(mfccs, axis=1),
                np.min(mfccs, axis=1),
                np.max(mfccs, axis=1)
            ])
            
            # Create hash
            mfcc_bytes = mfcc_features.tobytes()
            hash_value = hashlib.sha256(mfcc_bytes).hexdigest()
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.AUDIO,
                fingerprint_type=FingerprintType.FEATURE_HASH,
                hash_value=hash_value,
                vector_embedding=mfcc_features,
                metadata=metadata,
                confidence_score=0.92,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"MFCC fingerprint generation failed: {e}")
            return None
    
    async def _generate_perceptual_hash(self, audio: np.ndarray, sr: int,
                                      content_id: str, metadata: Dict[str, Any]) -> Optional[FingerprintResult]:
        """Generate perceptual hash for audio."""



        try:
            # Convert to spectrogram
            S = librosa.stft(audio, n_fft=2048, hop_length=512)
            S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)
            
            # Resize to fixed size for consistent hashing
            S_resized = cv2.resize(S_db, (64, 64))
            
            # Generate perceptual hash using DCT
            S_float32 = S_resized.astype(np.float32)
            dct = cv2.dct(S_float32)
            
            # Keep top-left 8x8 for hash
            dct_reduced = dct[:8, :8]
            median = np.median(dct_reduced)
            
            # Create binary hash
            hash_bits = (dct_reduced > median).flatten()
            hash_value = ''.join(['1' if bit else '0' for bit in hash_bits])
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.AUDIO,
                fingerprint_type=FingerprintType.PERCEPTUAL_HASH,
                hash_value=hash_value,
                metadata=metadata,
                confidence_score=0.85,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Perceptual hash generation failed: {e}")
            return None


class VideoFingerprintEngine:
    """
    Advanced video fingerprinting engine using frame analysis,
    motion vectors, and temporal features for robust video identification.
    """
    
    def __init__(self, frame_sample_rate: int = 1, feature_size: int = 1024):
        """Initialize video fingerprinting engine."""
        self.frame_sample_rate = frame_sample_rate  # Extract 1 frame per second
        self.feature_size = feature_size
        
    async def generate_fingerprint(self, video_path: str, 
                                 metadata: Dict[str, Any] = None) -> List[FingerprintResult]:
        """
        Generate comprehensive video fingerprints using multiple algorithms.
        
        Args:
            video_path: Path to video file
            metadata: Additional metadata for the video
            
        Returns:
            List[FingerprintResult]: Generated fingerprints
        """
        start_time = time.time()
        fingerprints = []
        
        try:
            content_id = str(uuid.uuid4())
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = max(1, int(fps // self.frame_sample_rate))
            
            # 1. Frame-based fingerprint
            frame_result = await self._generate_frame_fingerprint(cap, frame_interval, content_id, metadata)
            if frame_result:
                fingerprints.append(frame_result)
            
            # 2. Motion-based fingerprint
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
            motion_result = await self._generate_motion_fingerprint(cap, frame_interval, content_id, metadata)
            if motion_result:
                fingerprints.append(motion_result)
            
            # 3. Color histogram fingerprint
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
            color_result = await self._generate_color_fingerprint(cap, frame_interval, content_id, metadata)
            if color_result:
                fingerprints.append(color_result)
            
            # 4. Temporal features fingerprint
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
            temporal_result = await self._generate_temporal_fingerprint(cap, frame_interval, content_id, metadata)
            if temporal_result:
                fingerprints.append(temporal_result)
            
            cap.release()
            
            processing_time = (time.time() - start_time) * 1000
            
            # Update metrics
            fingerprint_operations_total.labels(content_type='video').inc()
            fingerprint_processing_time.labels(content_type='video').observe(processing_time / 1000)
            
            logger.info(f"Generated {len(fingerprints)} video fingerprints in {processing_time:.2f}ms")
            
            return fingerprints
            
        except Exception as e:
            logger.error(f"Video fingerprinting failed: {e}")
            return []
    
    async def _generate_frame_fingerprint(self, cap: cv2.VideoCapture, frame_interval: int,
                                        content_id: str, metadata: Dict[str, Any]) -> Optional[FingerprintResult]:
        """Generate fingerprint based on frame analysis."""



        try:
            frame_hashes = []
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    # Convert frame to grayscale
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Resize to standard size
                    resized = cv2.resize(gray, (64, 64))
                    
                    # Generate perceptual hash
                    dct = cv2.dct(resized.astype(np.float32))
                    dct_reduced = dct[:8, :8]
                    median = np.median(dct_reduced)
                    hash_bits = (dct_reduced > median).flatten()
                    frame_hash = ''.join(['1' if bit else '0' for bit in hash_bits])
                    frame_hashes.append(frame_hash)
                
                frame_count += 1
                
                # Limit to reasonable number of frames
                if len(frame_hashes) >= 100:
                    break
            
            if not frame_hashes:
                return None
            
            # Combine frame hashes
            combined_hash = hashlib.sha256(''.join(frame_hashes).encode()).hexdigest()
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.VIDEO,
                fingerprint_type=FingerprintType.PERCEPTUAL_HASH,
                hash_value=combined_hash,
                metadata={**(metadata or {}), 'frame_count': len(frame_hashes)},
                confidence_score=0.90,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Frame fingerprint generation failed: {e}")
            return None
    
    async def _generate_motion_fingerprint(self, cap: cv2.VideoCapture, frame_interval: int,
                                         content_id: str, metadata: Dict[str, Any]) -> Optional[FingerprintResult]:
        """Generate fingerprint based on motion analysis."""



        try:
            motion_vectors = []
            prev_frame = None
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray = cv2.resize(gray, (64, 64))
                    
                    if prev_frame is not None:
                        # Calculate optical flow
                        flow = cv2.calcOpticalFlowPyrLK(
                            prev_frame, gray, 
                            np.array([[x, y] for x in range(0, 64, 8) for y in range(0, 64, 8)], dtype=np.float32).reshape(-1, 1, 2),
                            None
                        )[0]
                        
                        if flow is not None:
                            # Calculate motion magnitude
                            motion_mag = np.sqrt(flow[:, 0, 0]**2 + flow[:, 0, 1]**2)
                            motion_vectors.extend(motion_mag.tolist())
                    
                    prev_frame = gray
                
                frame_count += 1
                
                # Limit analysis
                if len(motion_vectors) >= 1000:
                    break
            
            if not motion_vectors:
                return None
            
            # Statistical features from motion
            motion_array = np.array(motion_vectors)
            motion_features = np.array([
                np.mean(motion_array),
                np.std(motion_array),
                np.min(motion_array),
                np.max(motion_array),
                np.median(motion_array)
            ])
            
            # Create hash
            motion_bytes = motion_features.tobytes()
            hash_value = hashlib.sha256(motion_bytes).hexdigest()
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.VIDEO,
                fingerprint_type=FingerprintType.FEATURE_HASH,
                hash_value=hash_value,
                vector_embedding=motion_features,
                metadata={**(metadata or {}), 'motion_vectors_count': len(motion_vectors)},
                confidence_score=0.85,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Motion fingerprint generation failed: {e}")
            return None
    
    async def _generate_color_fingerprint(self, cap: cv2.VideoCapture, frame_interval: int,
                                        content_id: str, metadata: Dict[str, Any]) -> Optional[FingerprintResult]:
        """Generate fingerprint based on color analysis."""



        try:
            color_histograms = []
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    # Calculate color histogram
                    hist_b = cv2.calcHist([frame], [0], None, [32], [0, 256])
                    hist_g = cv2.calcHist([frame], [1], None, [32], [0, 256])
                    hist_r = cv2.calcHist([frame], [2], None, [32], [0, 256])
                    
                    # Normalize and combine
                    hist_combined = np.concatenate([
                        hist_b.flatten(), 
                        hist_g.flatten(), 
                        hist_r.flatten()
                    ])
                    hist_normalized = hist_combined / np.sum(hist_combined)
                    color_histograms.append(hist_normalized)
                
                frame_count += 1
                
                # Limit to reasonable number
                if len(color_histograms) >= 50:
                    break
            
            if not color_histograms:
                return None
            
            # Average color histogram
            avg_histogram = np.mean(color_histograms, axis=0)
            
            # Create hash
            hist_bytes = avg_histogram.tobytes()
            hash_value = hashlib.sha256(hist_bytes).hexdigest()
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.VIDEO,
                fingerprint_type=FingerprintType.SPECTRAL_HASH,
                hash_value=hash_value,
                vector_embedding=avg_histogram,
                metadata={**(metadata or {}), 'analyzed_frames': len(color_histograms)},
                confidence_score=0.82,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Color fingerprint generation failed: {e}")
            return None
    
    async def _generate_temporal_fingerprint(self, cap: cv2.VideoCapture, frame_interval: int,
                                           content_id: str, metadata: Dict[str, Any]) -> Optional[FingerprintResult]:
        """Generate fingerprint based on temporal features."""



        try:
            temporal_features = []
            prev_frame = None
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray = cv2.resize(gray, (32, 32))
                    
                    if prev_frame is not None:
                        # Frame difference
                        diff = cv2.absdiff(gray, prev_frame)
                        
                        # Temporal features
                        features = [
                            np.mean(diff),
                            np.std(diff),
                            np.sum(diff > 10),  # Changed pixels
                            np.sum(diff > 50)   # Significantly changed pixels
                        ]
                        temporal_features.extend(features)
                    
                    prev_frame = gray
                
                frame_count += 1
                
                # Limit analysis
                if len(temporal_features) >= 400:
                    break
            
            if not temporal_features:
                return None
            
            # Statistical features
            temporal_array = np.array(temporal_features)
            summary_features = np.array([
                np.mean(temporal_array),
                np.std(temporal_array),
                np.min(temporal_array),
                np.max(temporal_array)
            ])
            
            # Create hash
            temporal_bytes = summary_features.tobytes()
            hash_value = hashlib.sha256(temporal_bytes).hexdigest()
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.VIDEO,
                fingerprint_type=FingerprintType.FEATURE_HASH,
                hash_value=hash_value,
                vector_embedding=summary_features,
                metadata={**(metadata or {}), 'temporal_features_count': len(temporal_features)},
                confidence_score=0.87,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Temporal fingerprint generation failed: {e}")
            return None


class ImageFingerprintEngine:
    """
    Advanced image fingerprinting engine using perceptual hashing,
    CLIP embeddings, and feature detection for robust image identification.
    """
    
    def __init__(self):
        """Initialize image fingerprinting engine."""
        # Load CLIP model for semantic embeddings
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
    async def generate_fingerprint(self, image_data: Union[str, np.ndarray, Image.Image],
                                 metadata: Dict[str, Any] = None) -> List[FingerprintResult]:
        """
        Generate comprehensive image fingerprints using multiple algorithms.
        
        Args:
            image_data: Image file path, numpy array, or PIL Image
            metadata: Additional metadata for the image
            
        Returns:
            List[FingerprintResult]: Generated fingerprints
        """
        start_time = time.time()
        fingerprints = []
        
        try:
            # Load and convert image
            if isinstance(image_data, str):
                image = Image.open(image_data).convert('RGB')
            elif isinstance(image_data, np.ndarray):
                image = Image.fromarray(image_data).convert('RGB')
            else:
                image = image_data.convert('RGB')
            
            content_id = str(uuid.uuid4())
            
            # 1. Perceptual hashes
            perceptual_results = await self._generate_perceptual_hashes(image, content_id, metadata)
            fingerprints.extend(perceptual_results)
            
            # 2. CLIP semantic embedding
            clip_result = await self._generate_clip_embedding(image, content_id, metadata)
            if clip_result:
                fingerprints.append(clip_result)
            
            # 3. Feature-based fingerprint
            feature_result = await self._generate_feature_fingerprint(image, content_id, metadata)
            if feature_result:
                fingerprints.append(feature_result)
            
            # 4. Color-based fingerprint
            color_result = await self._generate_color_fingerprint(image, content_id, metadata)
            if color_result:
                fingerprints.append(color_result)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Update metrics
            fingerprint_operations_total.labels(content_type='image').inc()
            fingerprint_processing_time.labels(content_type='image').observe(processing_time / 1000)
            
            logger.info(f"Generated {len(fingerprints)} image fingerprints in {processing_time:.2f}ms")
            
            return fingerprints
            
        except Exception as e:
            logger.error(f"Image fingerprinting failed: {e}")
            return []
    
    async def _generate_perceptual_hashes(self, image: Image.Image, content_id: str,
                                        metadata: Dict[str, Any]) -> List[FingerprintResult]:
        """Generate multiple perceptual hashes."""
        fingerprints = []
        
        try:
            # Different perceptual hash algorithms
            hash_algorithms = [
                ('dhash', imagehash.dhash),
                ('phash', imagehash.phash),
                ('ahash', imagehash.average_hash),
                ('whash', imagehash.whash)
            ]
            
            for algo_name, algo_func in hash_algorithms:
                try:
                    hash_value = str(algo_func(image))
                    
                    fingerprints.append(FingerprintResult(
                        content_id=content_id,
                        content_type=ContentType.IMAGE,
                        fingerprint_type=FingerprintType.PERCEPTUAL_HASH,
                        hash_value=hash_value,
                        metadata={**(metadata or {}), 'algorithm': algo_name},
                        confidence_score=0.90 if algo_name == 'phash' else 0.85,
                        created_at=datetime.utcnow()
                    ))
                    
                except Exception as e:
                    logger.warning(f"Failed to generate {algo_name}: {e}")
                    continue
            
            return fingerprints
            
        except Exception as e:
            logger.error(f"Perceptual hash generation failed: {e}")
            return []
    
    async def _generate_clip_embedding(self, image: Image.Image, content_id: str,
                                     metadata: Dict[str, Any]) -> Optional[FingerprintResult]:
        """Generate CLIP semantic embedding."""



        try:
            # Process image with CLIP
            inputs = self.clip_processor(images=image, return_tensors="pt")
            
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
                embedding = image_features.numpy().flatten()
            
            # Create hash from embedding
            embedding_bytes = embedding.tobytes()
            hash_value = hashlib.sha256(embedding_bytes).hexdigest()
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.IMAGE,
                fingerprint_type=FingerprintType.VECTOR_EMBEDDING,
                hash_value=hash_value,
                vector_embedding=embedding,
                metadata={**(metadata or {}), 'model': 'clip-vit-base-patch32'},
                confidence_score=0.95,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"CLIP embedding generation failed: {e}")
            return None
    
    async def _generate_feature_fingerprint(self, image: Image.Image, content_id: str,
                                          metadata: Dict[str, Any]) -> Optional[FingerprintResult]:
        """Generate feature-based fingerprint using computer vision."""



        try:
            # Convert to OpenCV format
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
            
            # Feature detection using ORB
            orb = cv2.ORB_create(nfeatures=100)
            keypoints, descriptors = orb.detectAndCompute(gray, None)
            
            if descriptors is None or len(descriptors) == 0:
                return None
            
            # Create feature summary
            feature_summary = np.array([
                len(keypoints),
                np.mean(descriptors),
                np.std(descriptors),
                np.min(descriptors),
                np.max(descriptors)
            ])
            
            # Create hash
            feature_bytes = feature_summary.tobytes()
            hash_value = hashlib.sha256(feature_bytes).hexdigest()
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.IMAGE,
                fingerprint_type=FingerprintType.FEATURE_HASH,
                hash_value=hash_value,
                vector_embedding=feature_summary,
                metadata={**(metadata or {}), 'keypoints_count': len(keypoints)},
                confidence_score=0.80,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Feature fingerprint generation failed: {e}")
            return None
    
    async def _generate_color_fingerprint(self, image: Image.Image, content_id: str,
                                        metadata: Dict[str, Any]) -> Optional[FingerprintResult]:
        """Generate color-based fingerprint."""



        try:
            # Convert to numpy array
            image_array = np.array(image)
            
            # Color histogram features
            hist_r = np.histogram(image_array[:, :, 0], bins=32, range=(0, 256))[0]
            hist_g = np.histogram(image_array[:, :, 1], bins=32, range=(0, 256))[0]
            hist_b = np.histogram(image_array[:, :, 2], bins=32, range=(0, 256))[0]
            
            # Normalize and combine
            color_features = np.concatenate([hist_r, hist_g, hist_b])
            color_features = color_features / np.sum(color_features)
            
            # Dominant colors
            dominant_colors = []
            for channel in [0, 1, 2]:
                channel_data = image_array[:, :, channel]
                unique, counts = np.unique(channel_data, return_counts=True)
                dominant_idx = np.argmax(counts)
                dominant_colors.append(unique[dominant_idx])
            
            # Combine all color features
            all_features = np.concatenate([color_features, dominant_colors])
            
            # Create hash
            color_bytes = all_features.tobytes()
            hash_value = hashlib.sha256(color_bytes).hexdigest()
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.IMAGE,
                fingerprint_type=FingerprintType.SPECTRAL_HASH,
                hash_value=hash_value,
                vector_embedding=all_features,
                metadata={**(metadata or {}), 'dominant_colors': dominant_colors},
                confidence_score=0.75,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Color fingerprint generation failed: {e}")
            return None


class TextFingerprintEngine:
    """
    Advanced text fingerprinting engine using semantic embeddings,
    n-grams, and linguistic features for robust text identification.
    """
    
    def __init__(self):
        """Initialize text fingerprinting engine."""
        # Load pre-trained models
        self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
        self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.bert_model = BertModel.from_pretrained('bert-base-uncased')
        
    async def generate_fingerprint(self, text: str,
                                 metadata: Dict[str, Any] = None) -> List[FingerprintResult]:
        """
        Generate comprehensive text fingerprints using multiple algorithms.
        
        Args:
            text: Input text content
            metadata: Additional metadata for the text
            
        Returns:
            List[FingerprintResult]: Generated fingerprints
        """
        start_time = time.time()
        fingerprints = []
        
        try:
            content_id = str(uuid.uuid4())
            
            # 1. Semantic embedding fingerprint
            semantic_result = await self._generate_semantic_embedding(text, content_id, metadata)
            if semantic_result:
                fingerprints.append(semantic_result)
            
            # 2. N-gram based fingerprint
            ngram_result = await self._generate_ngram_fingerprint(text, content_id, metadata)
            if ngram_result:
                fingerprints.append(ngram_result)
            
            # 3. Linguistic features fingerprint
            linguistic_result = await self._generate_linguistic_fingerprint(text, content_id, metadata)
            if linguistic_result:
                fingerprints.append(linguistic_result)
            
            # 4. Hash-based fingerprint
            hash_result = await self._generate_content_hash(text, content_id, metadata)
            if hash_result:
                fingerprints.append(hash_result)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Update metrics
            fingerprint_operations_total.labels(content_type='text').inc()
            fingerprint_processing_time.labels(content_type='text').observe(processing_time / 1000)
            
            logger.info(f"Generated {len(fingerprints)} text fingerprints in {processing_time:.2f}ms")
            
            return fingerprints
            
        except Exception as e:
            logger.error(f"Text fingerprinting failed: {e}")
            return []
    
    async def _generate_semantic_embedding(self, text: str, content_id: str,
                                         metadata: Dict[str, Any]) -> Optional[FingerprintResult]:
        """Generate semantic embedding using sentence transformers."""



        try:
            # Generate embedding
            embedding = self.sentence_transformer.encode(text)
            
            # Create hash from embedding
            embedding_bytes = embedding.tobytes()
            hash_value = hashlib.sha256(embedding_bytes).hexdigest()
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.TEXT,
                fingerprint_type=FingerprintType.VECTOR_EMBEDDING,
                hash_value=hash_value,
                vector_embedding=embedding,
                metadata={**(metadata or {}), 'model': 'all-MiniLM-L6-v2'},
                confidence_score=0.93,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Semantic embedding generation failed: {e}")
            return None
    
    async def _generate_ngram_fingerprint(self, text: str, content_id: str,
                                        metadata: Dict[str, Any]) -> Optional[FingerprintResult]:
        """Generate n-gram based fingerprint."""



        try:
            # Clean and tokenize text
            words = text.lower().split()
            
            # Generate n-grams
            ngrams = []
            for n in [2, 3, 4]:  # bigrams, trigrams, 4-grams
                for i in range(len(words) - n + 1):
                    ngram = ' '.join(words[i:i+n])
                    ngrams.append(ngram)
            
            # Create frequency distribution
            from collections import Counter
            ngram_counts = Counter(ngrams)
            
            # Top frequent n-grams
            top_ngrams = [ngram for ngram, count in ngram_counts.most_common(50)]
            
            # Create fingerprint from top n-grams
            ngram_string = '|'.join(sorted(top_ngrams))
            hash_value = hashlib.sha256(ngram_string.encode()).hexdigest()
            
            # Create feature vector
            feature_vector = np.array([ngram_counts.get(ngram, 0) for ngram in top_ngrams[:20]])
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.TEXT,
                fingerprint_type=FingerprintType.FEATURE_HASH,
                hash_value=hash_value,
                vector_embedding=feature_vector,
                metadata={**(metadata or {}), 'ngrams_count': len(ngrams), 'unique_ngrams': len(ngram_counts)},
                confidence_score=0.85,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"N-gram fingerprint generation failed: {e}")
            return None
    
    async def _generate_linguistic_fingerprint(self, text: str, content_id: str,
                                             metadata: Dict[str, Any]) -> Optional[FingerprintResult]:
        """Generate linguistic features fingerprint."""



        try:
            # Basic linguistic features
            words = text.split()
            sentences = text.split('.')
            
            # Character-level features
            char_counts = {char: text.count(char) for char in set(text.lower())}
            
            # Linguistic features
            features = [
                len(text),  # Text length
                len(words),  # Word count
                len(sentences),  # Sentence count
                len(set(words)),  # Unique words
                np.mean([len(word) for word in words]) if words else 0,  # Average word length
                text.count(' '),  # Space count
                text.count(','),  # Comma count
                text.count('.'),  # Period count
                text.count('!'),  # Exclamation count
                text.count('?'),  # Question count
                sum(1 for char in text if char.isupper()),  # Uppercase count
                sum(1 for char in text if char.isdigit()),  # Digit count
            ]
            
            # Add most common character frequencies
            most_common_chars = sorted(char_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            features.extend([count for char, count in most_common_chars])
            
            # Pad to fixed size
            while len(features) < 30:
                features.append(0)
            
            feature_array = np.array(features[:30])
            
            # Create hash
            feature_bytes = feature_array.tobytes()
            hash_value = hashlib.sha256(feature_bytes).hexdigest()
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.TEXT,
                fingerprint_type=FingerprintType.FEATURE_HASH,
                hash_value=hash_value,
                vector_embedding=feature_array,
                metadata={**(metadata or {}), 'feature_count': len(features)},
                confidence_score=0.80,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Linguistic fingerprint generation failed: {e}")
            return None
    
    async def _generate_content_hash(self, text: str, content_id: str,
                                   metadata: Dict[str, Any]) -> Optional[FingerprintResult]:
        """Generate content-based hash."""



        try:
            # Clean text for consistent hashing
            cleaned_text = ' '.join(text.lower().split())
            
            # Multiple hash algorithms
            md5_hash = hashlib.md5(cleaned_text.encode()).hexdigest()
            sha256_hash = hashlib.sha256(cleaned_text.encode()).hexdigest()
            
            # Combine hashes
            combined_hash = hashlib.sha256(f"{md5_hash}{sha256_hash}".encode()).hexdigest()
            
            return FingerprintResult(
                content_id=content_id,
                content_type=ContentType.TEXT,
                fingerprint_type=FingerprintType.CONTENT_HASH,
                hash_value=combined_hash,
                metadata={**(metadata or {}), 'cleaned_length': len(cleaned_text)},
                confidence_score=0.95,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Content hash generation failed: {e}")
            return None


class SimilaritySearchEngine:
    """
    High-performance similarity search engine using FAISS
    for fast vector similarity matching across all content types.
    """
    
    def __init__(self, dimension: int = 512):
        """Initialize similarity search engine."""
        self.dimension = dimension
        self.indices: Dict[str, faiss.IndexFlatIP] = {}
        self.fingerprint_store: Dict[str, List[FingerprintResult]] = {}
        
    async def add_fingerprints(self, fingerprints: List[FingerprintResult]):
        """Add fingerprints to the search index."""



        try:
            for fingerprint in fingerprints:
                if fingerprint.vector_embedding is not None:
                    # Get or create index for this fingerprint type
                    index_key = f"{fingerprint.content_type.value}_{fingerprint.fingerprint_type.value}"
                    
                    if index_key not in self.indices:
                        # Create new FAISS index
                        self.indices[index_key] = faiss.IndexFlatIP(len(fingerprint.vector_embedding))
                        self.fingerprint_store[index_key] = []
                    
                    # Normalize vector for cosine similarity
                    vector = fingerprint.vector_embedding.copy()
                    vector = vector / np.linalg.norm(vector)
                    
                    # Add to index
                    self.indices[index_key].add(vector.reshape(1, -1))
                    self.fingerprint_store[index_key].append(fingerprint)
            
            logger.info(f"Added {len(fingerprints)} fingerprints to similarity index")
            
        except Exception as e:
            logger.error(f"Failed to add fingerprints to index: {e}")
    
    async def search_similar(self, query_fingerprint: FingerprintResult,
                           threshold: float = 0.8, max_results: int = 10) -> List[SimilarityMatch]:
        """
        Search for similar fingerprints in the index.
        
        Args:
            query_fingerprint: Fingerprint to search for
            threshold: Minimum similarity threshold
            max_results: Maximum number of results to return
            
        Returns:
            List[SimilarityMatch]: Similar fingerprints found
        """
        start_time = time.time()
        matches = []
        
        try:
            if query_fingerprint.vector_embedding is None:
                return matches
            
            index_key = f"{query_fingerprint.content_type.value}_{query_fingerprint.fingerprint_type.value}"
            
            if index_key not in self.indices:
                return matches
            
            # Normalize query vector
            query_vector = query_fingerprint.vector_embedding.copy()
            query_vector = query_vector / np.linalg.norm(query_vector)
            
            # Search in FAISS index
            similarities, indices = self.indices[index_key].search(
                query_vector.reshape(1, -1), max_results
            )
            
            # Filter by threshold and create matches
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if similarity >= threshold and idx < len(self.fingerprint_store[index_key]):
                    matched_fingerprint = self.fingerprint_store[index_key][idx]
                    
                    match = SimilarityMatch(
                        original_id=query_fingerprint.content_id,
                        matched_id=matched_fingerprint.content_id,
                        similarity_score=float(similarity),
                        fingerprint_type=query_fingerprint.fingerprint_type,
                        content_type=query_fingerprint.content_type,
                        metadata={
                            'query_metadata': query_fingerprint.metadata,
                            'match_metadata': matched_fingerprint.metadata
                        },
                        found_at=datetime.utcnow()
                    )
                    matches.append(match)
            
            search_time = time.time() - start_time
            similarity_search_time.observe(search_time)
            
            logger.info(f"Found {len(matches)} similar fingerprints in {search_time:.3f}s")
            
            return matches
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return matches


class MultiformatFingerprintEngine:
    """
    Unified fingerprinting engine that coordinates all content type engines
    for comprehensive multi-format content analysis and protection.
    """
    
    def __init__(self):
        """Initialize multiformat fingerprinting engine."""
        self.audio_engine = AudioFingerprintEngine()
        self.video_engine = VideoFingerprintEngine()
        self.image_engine = ImageFingerprintEngine()
        self.text_engine = TextFingerprintEngine()
        self.similarity_engine = SimilaritySearchEngine()
        
    async def generate_fingerprints(self, content_path: str, content_type: ContentType,
                                  metadata: Dict[str, Any] = None) -> List[FingerprintResult]:
        """
        Generate fingerprints for any content type.
        
        Args:
            content_path: Path to content file
            content_type: Type of content
            metadata: Additional metadata
            
        Returns:
            List[FingerprintResult]: Generated fingerprints
        """



        try:
            if content_type == ContentType.AUDIO:
                fingerprints = await self.audio_engine.generate_fingerprint(content_path, metadata)
            elif content_type == ContentType.VIDEO:
                fingerprints = await self.video_engine.generate_fingerprint(content_path, metadata)
            elif content_type == ContentType.IMAGE:
                fingerprints = await self.image_engine.generate_fingerprint(content_path, metadata)
            elif content_type == ContentType.TEXT:
                # For text, content_path is the actual text content
                fingerprints = await self.text_engine.generate_fingerprint(content_path, metadata)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Add to similarity index
            if fingerprints:
                await self.similarity_engine.add_fingerprints(fingerprints)
            
            return fingerprints
            
        except Exception as e:
            logger.error(f"Multiformat fingerprinting failed: {e}")
            return []
    
    async def find_similar_content(self, fingerprints: List[FingerprintResult],
                                 threshold: float = 0.8) -> List[SimilarityMatch]:
        """
        Find similar content across all fingerprints.
        
        Args:
            fingerprints: Fingerprints to search for
            threshold: Similarity threshold
            
        Returns:
            List[SimilarityMatch]: All similarity matches found
        """
        all_matches = []
        
        for fingerprint in fingerprints:
            matches = await self.similarity_engine.search_similar(fingerprint, threshold)
            all_matches.extend(matches)
        
        # Remove duplicates and sort by similarity
        unique_matches = {}
        for match in all_matches:
            key = f"{match.original_id}_{match.matched_id}"
            if key not in unique_matches or match.similarity_score > unique_matches[key].similarity_score:
                unique_matches[key] = match
        
        return sorted(unique_matches.values(), key=lambda x: x.similarity_score, reverse=True)
    
    async def get_engine_statistics(self) -> Dict[str, Any]:
        """Get comprehensive engine statistics."""



        return {
            'audio_engine': 'active',
            'video_engine': 'active', 
            'image_engine': 'active',
            'text_engine': 'active',
            'similarity_engine': {
                'indices_count': len(self.similarity_engine.indices),
                'total_fingerprints': sum(len(store) for store in self.similarity_engine.fingerprint_store.values())
            }
        }
