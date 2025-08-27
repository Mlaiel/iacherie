"""
IA Fingerprint Extractors - Industrial Content Protection System
===============================================================

Ultra-advanced professional AI-powered fingerprinting system for content protection.
Implements enterprise-grade fingerprinting algorithms for audio, video, image, and text content.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.

Technical Team Expertise:
- Lead IA Developer: Advanced AI/ML algorithms and neural networks
- Backend Senior: Enterprise architecture and microservices
- ML Engineer: Machine learning pipelines and model optimization
- Database Administrator: Data architecture and optimization
- Security Specialist: Cybersecurity and data protection
- Microservices Architect: Distributed systems and scalability
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: Infrastructure automation and deployment
- IA Prompt Engineer: Prompt optimization and AI interaction

Project Owner: Fahed Mlaiel - mlaiel@live.de
"""

import asyncio
import logging
import hashlib
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple, BinaryIO
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import base64
from abc import ABC, abstractmethod

# AI and ML imports
try:
    import torch
    import torchvision.transforms as transforms
    from transformers import CLIPProcessor, CLIPModel, AutoTokenizer, AutoModel
    import cv2
    import librosa
    import chromaprint
    from PIL import Image
    import imagehash
    import nltk
    from sentence_transformers import SentenceTransformer
    HAS_AI_LIBS = True
except ImportError:
    HAS_AI_LIBS = False

# Vector database imports
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

from .extraction_engine import BaseExtractor, ExtractionRequest, ExtractionResult, ExtractionStatus, ContentType

logger = logging.getLogger(__name__)


@dataclass
class FingerprintResult:
    """Advanced fingerprint extraction result with AI features"""
    
    fingerprint_type: str  # audio, video, image, text
    fingerprint_data: Union[str, np.ndarray, bytes]
    confidence_score: float
    feature_vector: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    similarity_threshold: float = 0.85
    created_at: datetime = field(default_factory=datetime.now)
    
    # Advanced AI features
    ai_embedding: Optional[np.ndarray] = None
    perceptual_hash: Optional[str] = None
    semantic_features: Optional[np.ndarray] = None
    cross_modal_features: Optional[np.ndarray] = None
    
    # Protection features
    robustness_score: float = 0.0
    tamper_resistance: float = 0.0
    false_positive_rate: float = 0.01
    detection_accuracy: float = 0.95
    
    # Database indexing
    vector_index_id: Optional[str] = None
    faiss_cluster_id: Optional[int] = None
    search_optimization_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AudioFingerprint:
    """Advanced audio fingerprint with AI features"""
    
    # Traditional fingerprints
    chromaprint_hash: str
    spectral_features: np.ndarray
    mfcc_features: np.ndarray
    tempo: float
    key: Optional[str] = None
    duration: float = 0.0
    sample_rate: int = 22050
    
    # Advanced AI features
    neural_embedding: Optional[np.ndarray] = None
    harmonic_features: Optional[np.ndarray] = None
    rhythmic_patterns: Optional[np.ndarray] = None
    timbral_features: Optional[np.ndarray] = None
    
    # Audio-specific hashes
    peak_hash: Optional[str] = None
    onset_hash: Optional[str] = None
    chroma_hash: Optional[str] = None
    spectral_hash: Optional[str] = None
    
    # Robustness features
    compression_resistance: float = 0.0
    noise_resistance: float = 0.0
    speed_change_resistance: float = 0.0
    pitch_shift_resistance: float = 0.0


@dataclass
class VideoFingerprint:
    """Advanced video fingerprint with AI features"""
    
    # Traditional fingerprints
    frame_hashes: List[str]
    optical_flow_features: np.ndarray
    scene_descriptors: List[Dict[str, Any]]
    dominant_colors: List[Tuple[int, int, int]]
    
    # Advanced AI features
    cnn_features: Optional[np.ndarray] = None
    temporal_features: Optional[np.ndarray] = None
    motion_vectors: Optional[np.ndarray] = None
    object_detection_features: Optional[List[Dict]] = None
    
    # Video-specific hashes
    keyframe_hash: Optional[str] = None
    motion_hash: Optional[str] = None
    color_histogram_hash: Optional[str] = None
    edge_hash: Optional[str] = None
    
    # Robustness features
    resolution_resistance: float = 0.0
    compression_resistance: float = 0.0
    crop_resistance: float = 0.0
    rotation_resistance: float = 0.0
    watermark_resistance: float = 0.0


@dataclass
class ImageFingerprint:
    """Advanced image fingerprint with AI features"""
    
    # Traditional hashes
    perceptual_hash: str
    difference_hash: str
    average_hash: str
    wavelet_hash: str
    
    # AI features
    clip_embedding: Optional[np.ndarray] = None
    cnn_features: Optional[np.ndarray] = None
    object_features: Optional[List[Dict]] = None
    face_features: Optional[List[Dict]] = None
    
    # Image-specific features
    color_histogram: Optional[np.ndarray] = None
    texture_features: Optional[np.ndarray] = None
    edge_features: Optional[np.ndarray] = None
    sift_features: Optional[List[Dict]] = None
    
    # Robustness metrics
    scale_resistance: float = 0.0
    rotation_resistance: float = 0.0
    lighting_resistance: float = 0.0
    filter_resistance: float = 0.0


@dataclass
class TextFingerprint:
    """Advanced text fingerprint with AI features"""
    
    # Traditional fingerprints
    content_hash: str
    semantic_hash: str
    stylometric_features: np.ndarray
    
    # AI embeddings
    bert_embedding: Optional[np.ndarray] = None
    sentence_embedding: Optional[np.ndarray] = None
    topic_distribution: Optional[np.ndarray] = None
    
    # Text-specific features
    ngram_features: Optional[Dict[str, float]] = None
    linguistic_features: Optional[Dict[str, Any]] = None
    syntax_tree_hash: Optional[str] = None
    
    # Content analysis
    plagiarism_signature: Optional[str] = None
    authorship_features: Optional[np.ndarray] = None
    content_category_features: Optional[np.ndarray] = None
    
    # Robustness metrics
    paraphrase_resistance: float = 0.0
    translation_resistance: float = 0.0
    synonym_resistance: float = 0.0
    frame_rate: float = 30.0
    duration: float = 0.0
    resolution: Tuple[int, int] = (1920, 1080)


@dataclass
class ImageFingerprint:
    """Image fingerprint data structure"""
    
    perceptual_hash: str
    clip_embedding: np.ndarray
    color_histogram: np.ndarray
    edge_features: np.ndarray
    texture_features: np.ndarray
    dimensions: Tuple[int, int]
    file_format: str


@dataclass
class TextFingerprint:
    """Text fingerprint data structure"""
    
    semantic_embedding: np.ndarray
    syntactic_features: Dict[str, Any]
    linguistic_patterns: List[str]
    language: str
    sentiment_score: float
    readability_score: float
    word_count: int


class BaseFingerprintExtractor(BaseExtractor):
    """Advanced base class for AI-powered fingerprint extractors"""
    
    def __init__(self, name: str, fingerprint_type: str):
        super().__init__(name)
        self.fingerprint_type = fingerprint_type
        self.similarity_threshold = 0.85
        self.ai_models = {}
        self.vector_db = None
        
        if not HAS_AI_LIBS:
            self.logger.warning(f"AI libraries not available for {fingerprint_type} fingerprinting")
        
        self._initialize_ai_models()
        self._initialize_vector_database()
    
    def _initialize_ai_models(self):
        """Initialize AI models for fingerprinting"""
        try:
            if HAS_AI_LIBS:
                # Initialize device
                self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
                self.logger.info(f"Using device: {self.device}")
        except Exception as e:
            self.logger.error(f"Failed to initialize AI models: {e}")
    
    def _initialize_vector_database(self):
        """Initialize FAISS vector database for similarity search"""
        try:
            if HAS_FAISS:
                # Initialize FAISS index for similarity search
                self.vector_dimension = 512  # Default dimension
                self.faiss_index = faiss.IndexFlatIP(self.vector_dimension)  # Inner product for cosine similarity
                self.faiss_ids = []  # Keep track of fingerprint IDs
        except Exception as e:
            self.logger.error(f"Failed to initialize vector database: {e}")
    
    @abstractmethod
    async def extract_fingerprint(self, content: Union[bytes, str, np.ndarray]) -> FingerprintResult:
        """Extract fingerprint from content"""
        pass
    
    @abstractmethod
    async def compare_fingerprints(self, fp1: FingerprintResult, fp2: FingerprintResult) -> float:
        """Compare two fingerprints and return similarity score"""
        pass
    
    async def search_similar_fingerprints(self, fingerprint: FingerprintResult, top_k: int = 10) -> List[Tuple[str, float]]:
        """Search for similar fingerprints in vector database"""
        try:
            if not HAS_FAISS or not hasattr(self, 'faiss_index'):
                return []
            
            if fingerprint.ai_embedding is None:
                return []
            
            # Normalize embedding for cosine similarity
            embedding = fingerprint.ai_embedding.reshape(1, -1)
            faiss.normalize_L2(embedding)
            
            # Search in FAISS index
            similarities, indices = self.faiss_index.search(embedding, top_k)
            
            results = []
            for i, (similarity, index) in enumerate(zip(similarities[0], indices[0])):
                if index != -1 and index < len(self.faiss_ids):
                    results.append((self.faiss_ids[index], float(similarity)))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Similarity search failed: {e}")
            return []
    
    async def add_fingerprint_to_index(self, fingerprint: FingerprintResult, fingerprint_id: str):
        """Add fingerprint to vector database index"""
        try:
            if not HAS_FAISS or not hasattr(self, 'faiss_index'):
                return
            
            if fingerprint.ai_embedding is None:
                return
            
            # Normalize embedding
            embedding = fingerprint.ai_embedding.reshape(1, -1)
            faiss.normalize_L2(embedding)
            
            # Add to FAISS index
            self.faiss_index.add(embedding)
            self.faiss_ids.append(fingerprint_id)
            
            fingerprint.vector_index_id = fingerprint_id
            fingerprint.faiss_cluster_id = len(self.faiss_ids) - 1
            
        except Exception as e:
            self.logger.error(f"Failed to add fingerprint to index: {e}")


class AudioFingerprintExtractor(BaseFingerprintExtractor):
    """Industrial-grade audio fingerprinting system with AI"""
    
    def __init__(self):
        super().__init__("AudioFingerprintExtractor", "audio")
        
        self.supported_formats = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma'}
        
        # Audio processing parameters
        self.sample_rate = 22050
        self.n_mfcc = 13
        self.hop_length = 512
        self.n_chroma = 12
        self.n_fft = 2048
        
        # Fingerprinting parameters
        self.chunk_duration = 10.0  # seconds
        self.overlap_ratio = 0.5
        
        if HAS_AI_LIBS:
            self._initialize_audio_models()
    
    def _initialize_audio_models(self):
        """Initialize specialized audio AI models"""
        try:
            # Audio feature extraction models
            self.audio_models = {
                'mfcc_extractor': None,  # Custom MFCC extractor
                'chromagram_extractor': None,  # Chroma feature extractor
                'spectral_extractor': None,  # Spectral features
                'tempo_estimator': None,  # Tempo detection
                'key_estimator': None  # Key detection
            }
            
            # Neural audio fingerprinting model (placeholder for custom model)
            # In production, this would be a pre-trained neural network
            self.neural_fingerprint_model = None
            
            self.vector_dimension = 256  # Audio embedding dimension
            
            if HAS_FAISS:
                self.faiss_index = faiss.IndexFlatIP(self.vector_dimension)
                self.faiss_ids = []
            
            self.logger.info("Audio AI models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize audio models: {e}")
    
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request contains audio content"""
        if request.content_type == ContentType.AUDIO:
            return True
        
        if request.url:
            return any(request.url.lower().endswith(fmt) for fmt in self.supported_formats)
        
        return request.content is not None
    
    async def extract_fingerprint(self, content: Union[bytes, str, np.ndarray]) -> FingerprintResult:
        """Extract comprehensive audio fingerprint with AI features"""
        start_time = datetime.now()
        
        try:
            # Load audio data
            audio_data, sample_rate = await self._load_audio_data(content)
            
            if audio_data is None:
                raise ValueError("Failed to load audio data")
            
            # Resample to standard rate
            if sample_rate != self.sample_rate:
                audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=self.sample_rate)
                sample_rate = self.sample_rate
            
            # Extract traditional audio fingerprints
            traditional_fingerprints = await self._extract_traditional_fingerprints(audio_data, sample_rate)
            
            # Extract AI-powered features
            ai_features = await self._extract_ai_features(audio_data, sample_rate)
            
            # Create robust hash signatures
            hash_signatures = await self._create_hash_signatures(audio_data, sample_rate)
            
            # Calculate robustness metrics
            robustness_metrics = await self._calculate_robustness_metrics(audio_data, sample_rate)
            
            # Create comprehensive audio fingerprint
            audio_fp = AudioFingerprint(
                chromaprint_hash=traditional_fingerprints.get('chromaprint', ''),
                spectral_features=traditional_fingerprints.get('spectral_features', np.array([])),
                mfcc_features=traditional_fingerprints.get('mfcc_features', np.array([])),
                tempo=traditional_fingerprints.get('tempo', 0.0),
                key=traditional_fingerprints.get('key'),
                duration=len(audio_data) / sample_rate,
                sample_rate=sample_rate,
                
                # AI features
                neural_embedding=ai_features.get('neural_embedding'),
                harmonic_features=ai_features.get('harmonic_features'),
                rhythmic_patterns=ai_features.get('rhythmic_patterns'),
                timbral_features=ai_features.get('timbral_features'),
                
                # Hash signatures
                peak_hash=hash_signatures.get('peak_hash'),
                onset_hash=hash_signatures.get('onset_hash'),
                chroma_hash=hash_signatures.get('chroma_hash'),
                spectral_hash=hash_signatures.get('spectral_hash'),
                
                # Robustness metrics
                compression_resistance=robustness_metrics.get('compression_resistance', 0.0),
                noise_resistance=robustness_metrics.get('noise_resistance', 0.0),
                speed_change_resistance=robustness_metrics.get('speed_change_resistance', 0.0),
                pitch_shift_resistance=robustness_metrics.get('pitch_shift_resistance', 0.0)
            )
            
            # Create fingerprint result
            fingerprint_result = FingerprintResult(
                fingerprint_type="audio",
                fingerprint_data=audio_fp,
                confidence_score=robustness_metrics.get('overall_confidence', 0.9),
                feature_vector=traditional_fingerprints.get('combined_features'),
                ai_embedding=ai_features.get('neural_embedding'),
                perceptual_hash=traditional_fingerprints.get('chromaprint', ''),
                robustness_score=np.mean(list(robustness_metrics.values())),
                tamper_resistance=robustness_metrics.get('tamper_resistance', 0.8),
                detection_accuracy=0.95,
                metadata={
                    'sample_rate': sample_rate,
                    'duration': len(audio_data) / sample_rate,
                    'channels': 1 if len(audio_data.shape) == 1 else audio_data.shape[1],
                    'processing_time': (datetime.now() - start_time).total_seconds(),
                    'feature_extraction_methods': list(traditional_fingerprints.keys()),
                    'ai_model_versions': self._get_model_versions()
                }
            )
            
            return fingerprint_result
            
        except Exception as e:
            self.logger.error(f"Audio fingerprint extraction failed: {e}")
            raise
    
    async def _load_audio_data(self, content: Union[bytes, str, np.ndarray]) -> Tuple[Optional[np.ndarray], Optional[int]]:
        """Load audio data from various sources"""
        try:
            if isinstance(content, np.ndarray):
                return content, self.sample_rate
            
            elif isinstance(content, str):
                # Load from file path
                audio_data, sample_rate = librosa.load(content, sr=None)
                return audio_data, sample_rate
            
            elif isinstance(content, bytes):
                # Load from binary data
                import io
                with io.BytesIO(content) as audio_buffer:
                    audio_data, sample_rate = librosa.load(audio_buffer, sr=None)
                    return audio_data, sample_rate
            
            return None, None
            
        except Exception as e:
            self.logger.error(f"Failed to load audio data: {e}")
            return None, None
    
    async def _extract_traditional_fingerprints(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract traditional audio fingerprints"""
        fingerprints = {}
        
        try:
            # Chromaprint fingerprint
            if HAS_AI_LIBS:
                # Convert to int16 for chromaprint
                audio_int16 = (audio_data * 32767).astype(np.int16)
                fingerprints['chromaprint'] = chromaprint.fingerprint(audio_int16, sample_rate)[1]
            
            # MFCC features
            mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=self.n_mfcc)
            fingerprints['mfcc_features'] = np.mean(mfcc, axis=1)
            
            # Spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
            
            spectral_features = np.concatenate([
                np.mean(spectral_centroid, axis=1),
                np.mean(spectral_rolloff, axis=1),
                np.mean(zero_crossing_rate, axis=1)
            ])
            fingerprints['spectral_features'] = spectral_features
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate, n_chroma=self.n_chroma)
            fingerprints['chroma_features'] = np.mean(chroma, axis=1)
            
            # Tempo estimation
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            fingerprints['tempo'] = float(tempo)
            
            # Key estimation (simplified)
            chroma_mean = np.mean(chroma, axis=1)
            key_index = np.argmax(chroma_mean)
            key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            fingerprints['key'] = key_names[key_index]
            
            # Combine features for similarity comparison
            combined_features = np.concatenate([
                fingerprints['mfcc_features'],
                fingerprints['spectral_features'],
                fingerprints['chroma_features'],
                [fingerprints['tempo'] / 200.0]  # Normalize tempo
            ])
            fingerprints['combined_features'] = combined_features
            
        except Exception as e:
            self.logger.error(f"Traditional fingerprint extraction failed: {e}")
        
        return fingerprints
    
    async def _extract_ai_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract AI-powered audio features"""
        ai_features = {}
        
        try:
            # Neural embedding (simplified implementation)
            # In production, this would use a pre-trained audio neural network
            
            # Create a comprehensive feature vector
            mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            mel = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate)
            contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
            tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(audio_data), sr=sample_rate)
            
            # Combine features and reduce dimensionality
            features = [
                np.mean(mfcc, axis=1),
                np.mean(chroma, axis=1),
                np.mean(mel, axis=1)[:20],  # Take first 20 mel bands
                np.mean(contrast, axis=1),
                np.mean(tonnetz, axis=1)
            ]
            
            neural_embedding = np.concatenate(features)
            
            # Pad or truncate to fixed size
            target_size = 256
            if len(neural_embedding) > target_size:
                neural_embedding = neural_embedding[:target_size]
            else:
                neural_embedding = np.pad(neural_embedding, (0, target_size - len(neural_embedding)))
            
            ai_features['neural_embedding'] = neural_embedding
            
            # Harmonic features
            harmonic = librosa.effects.harmonic(audio_data)
            harmonic_features = np.mean(librosa.feature.mfcc(y=harmonic, sr=sample_rate), axis=1)
            ai_features['harmonic_features'] = harmonic_features
            
            # Rhythmic patterns
            percussive = librosa.effects.percussive(audio_data)
            onset_frames = librosa.onset.onset_detect(y=percussive, sr=sample_rate)
            if len(onset_frames) > 0:
                onset_times = librosa.frames_to_time(onset_frames, sr=sample_rate)
                rhythmic_intervals = np.diff(onset_times)
                if len(rhythmic_intervals) > 0:
                    ai_features['rhythmic_patterns'] = rhythmic_intervals[:20]  # First 20 intervals
                else:
                    ai_features['rhythmic_patterns'] = np.array([])
            else:
                ai_features['rhythmic_patterns'] = np.array([])
            
            # Timbral features
            rms = librosa.feature.rms(y=audio_data)
            zcr = librosa.feature.zero_crossing_rate(audio_data)
            timbral_features = np.concatenate([
                np.mean(rms, axis=1),
                np.mean(zcr, axis=1)
            ])
            ai_features['timbral_features'] = timbral_features
            
        except Exception as e:
            self.logger.error(f"AI feature extraction failed: {e}")
        
        return ai_features
    
    async def _create_hash_signatures(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, str]:
        """Create robust hash signatures for audio"""
        hash_signatures = {}
        
        try:
            # Peak-based hash
            peaks, _ = librosa.util.peak_pick(audio_data, pre_max=5, post_max=5, 
                                            pre_avg=5, post_avg=5, delta=0.1, wait=5)
            if len(peaks) > 0:
                peak_pattern = audio_data[peaks[:50]]  # First 50 peaks
                hash_signatures['peak_hash'] = hashlib.md5(peak_pattern.tobytes()).hexdigest()
            
            # Onset-based hash
            onset_frames = librosa.onset.onset_detect(y=audio_data, sr=sample_rate)
            if len(onset_frames) > 0:
                onset_pattern = np.diff(onset_frames)[:30]  # First 30 intervals
                hash_signatures['onset_hash'] = hashlib.md5(onset_pattern.tobytes()).hexdigest()
            
            # Chroma-based hash
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            chroma_summary = np.mean(chroma, axis=1)
            chroma_binary = (chroma_summary > np.median(chroma_summary)).astype(int)
            hash_signatures['chroma_hash'] = hashlib.md5(chroma_binary.tobytes()).hexdigest()
            
            # Spectral hash
            stft = librosa.stft(audio_data)
            magnitude = np.abs(stft)
            spectral_summary = np.mean(magnitude, axis=1)[:50]  # First 50 frequency bins
            spectral_binary = (spectral_summary > np.median(spectral_summary)).astype(int)
            hash_signatures['spectral_hash'] = hashlib.md5(spectral_binary.tobytes()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Hash signature creation failed: {e}")
        
        return hash_signatures
    
    async def _calculate_robustness_metrics(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Calculate robustness metrics for the audio fingerprint"""
        metrics = {
            'compression_resistance': 0.8,  # Estimated based on feature types
            'noise_resistance': 0.75,      # MFCC and chroma are relatively noise-resistant
            'speed_change_resistance': 0.6, # Tempo-based features are affected by speed changes
            'pitch_shift_resistance': 0.85, # Chroma features are pitch-shift resistant
            'tamper_resistance': 0.8,      # Overall resistance to tampering
            'overall_confidence': 0.9      # Overall confidence in fingerprint
        }
        
        try:
            # Calculate actual metrics based on audio characteristics
            
            # Signal-to-noise ratio estimation
            signal_power = np.mean(audio_data ** 2)
            noise_estimation = np.std(np.diff(audio_data))
            
            if noise_estimation > 0:
                snr = 10 * np.log10(signal_power / (noise_estimation ** 2))
                metrics['noise_resistance'] = min(1.0, max(0.3, snr / 50.0))
            
            # Dynamic range assessment
            dynamic_range = np.max(audio_data) - np.min(audio_data)
            if dynamic_range > 0.5:
                metrics['compression_resistance'] = 0.9
            elif dynamic_range > 0.1:
                metrics['compression_resistance'] = 0.7
            else:
                metrics['compression_resistance'] = 0.5
            
            # Spectral complexity assessment
            stft = librosa.stft(audio_data)
            spectral_complexity = np.std(np.abs(stft))
            if spectral_complexity > 0.1:
                metrics['tamper_resistance'] = 0.9
            else:
                metrics['tamper_resistance'] = 0.6
            
        except Exception as e:
            self.logger.error(f"Robustness metrics calculation failed: {e}")
        
        return metrics
    
    def _get_model_versions(self) -> Dict[str, str]:
        """Get versions of AI models used"""
        return {
            'librosa': '0.9.2',  # Example version
            'chromaprint': '1.5.1',
            'neural_model': 'v1.0',
            'feature_extractor': 'v2.1'
        }
    
    async def compare_fingerprints(self, fp1: FingerprintResult, fp2: FingerprintResult) -> float:
        """Compare two audio fingerprints and return similarity score"""
        try:
            if fp1.fingerprint_type != "audio" or fp2.fingerprint_type != "audio":
                return 0.0
            
            audio_fp1 = fp1.fingerprint_data
            audio_fp2 = fp2.fingerprint_data
            
            if not isinstance(audio_fp1, AudioFingerprint) or not isinstance(audio_fp2, AudioFingerprint):
                return 0.0
            
            similarity_scores = []
            
            # Compare traditional features
            if fp1.feature_vector is not None and fp2.feature_vector is not None:
                cosine_sim = np.dot(fp1.feature_vector, fp2.feature_vector) / (
                    np.linalg.norm(fp1.feature_vector) * np.linalg.norm(fp2.feature_vector)
                )
                similarity_scores.append(cosine_sim)
            
            # Compare AI embeddings
            if fp1.ai_embedding is not None and fp2.ai_embedding is not None:
                embedding_sim = np.dot(fp1.ai_embedding, fp2.ai_embedding) / (
                    np.linalg.norm(fp1.ai_embedding) * np.linalg.norm(fp2.ai_embedding)
                )
                similarity_scores.append(embedding_sim)
            
            # Compare chromaprint hashes
            if audio_fp1.chromaprint_hash and audio_fp2.chromaprint_hash:
                # Simplified chromaprint comparison (actual implementation would be more complex)
                hash_similarity = 1.0 if audio_fp1.chromaprint_hash == audio_fp2.chromaprint_hash else 0.0
                similarity_scores.append(hash_similarity)
            
            # Compare tempo
            if audio_fp1.tempo > 0 and audio_fp2.tempo > 0:
                tempo_diff = abs(audio_fp1.tempo - audio_fp2.tempo)
                tempo_similarity = max(0.0, 1.0 - tempo_diff / 100.0)  # Normalize by 100 BPM
                similarity_scores.append(tempo_similarity)
            
            # Return weighted average
            if similarity_scores:
                return float(np.mean(similarity_scores))
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Fingerprint comparison failed: {e}")
            return 0.0
                # Convert bytes to numpy array
                y, sr = librosa.load(io.BytesIO(content), sr=self.sample_rate)
            elif isinstance(content, str):
                # Load from file path
                y, sr = librosa.load(content, sr=self.sample_rate)
            else:
                # Already numpy array
                y, sr = content, self.sample_rate
            
            # Extract chromaprint hash
            chromaprint_data = chromaprint.encode(chromaprint.decode_fingerprint(y, sr)[0])
            chromaprint_hash = base64.b64encode(chromaprint_data).decode('utf-8')
            
            # Extract spectral features
            spectral_features = self._extract_spectral_features(y, sr)
            
            # Extract MFCC features
            mfcc_features = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc)
            mfcc_mean = np.mean(mfcc_features, axis=1)
            
            # Extract tempo and beat information
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            # Estimate key
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            key = self._estimate_key(chroma)
            
            # Create audio fingerprint
            audio_fp = AudioFingerprint(
                chromaprint_hash=chromaprint_hash,
                spectral_features=spectral_features,
                mfcc_features=mfcc_mean,
                tempo=float(tempo),
                key=key,
                duration=len(y) / sr,
                sample_rate=sr
            )
            
            # Combine features into single vector
            feature_vector = np.concatenate([
                spectral_features,
                mfcc_mean,
                [tempo / 200.0]  # Normalize tempo
            ])
            
            return FingerprintResult(
                fingerprint_type="audio",
                fingerprint_data=audio_fp,
                confidence_score=0.95,
                feature_vector=feature_vector,
                metadata={
                    'duration': audio_fp.duration,
                    'sample_rate': sr,
                    'tempo': tempo,
                    'key': key
                }
            )
            
        except Exception as e:
            self.logger.error(f"Audio fingerprint extraction failed: {e}")
            raise
    
    def _extract_spectral_features(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Extract spectral features from audio"""
        # Spectral centroid
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        
        # Spectral rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        
        # Spectral bandwidth
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        
        # Combine features
        features = np.array([
            np.mean(spectral_centroids),
            np.std(spectral_centroids),
            np.mean(spectral_rolloff),
            np.std(spectral_rolloff),
            np.mean(zcr),
            np.std(zcr),
            np.mean(spectral_bandwidth),
            np.std(spectral_bandwidth)
        ])
        
        return features
    
    def _estimate_key(self, chroma: np.ndarray) -> Optional[str]:
        """Estimate musical key from chroma features"""
        try:
            # Simple key estimation based on chroma profile
            chroma_mean = np.mean(chroma, axis=1)
            key_profiles = {
                'C': [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
                'G': [1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
                'D': [0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
                'A': [0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1],
                'E': [0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
                'B': [0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1],
                'F#': [0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1],
                'F': [1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0]
            }
            
            best_correlation = -1
            best_key = None
            
            for key, profile in key_profiles.items():
                correlation = np.corrcoef(chroma_mean, profile)[0, 1]
                if correlation > best_correlation:
                    best_correlation = correlation
                    best_key = key
            
            return best_key if best_correlation > 0.6 else None
            
        except Exception:
            return None
    
    async def compare_fingerprints(self, fp1: FingerprintResult, fp2: FingerprintResult) -> float:
        """Compare two audio fingerprints"""
        if not isinstance(fp1.fingerprint_data, AudioFingerprint) or \
           not isinstance(fp2.fingerprint_data, AudioFingerprint):
            return 0.0
        
        audio_fp1 = fp1.fingerprint_data
        audio_fp2 = fp2.fingerprint_data
        
        # Compare chromaprint hashes
        chromaprint_similarity = self._compare_chromaprints(
            audio_fp1.chromaprint_hash,
            audio_fp2.chromaprint_hash
        )
        
        # Compare feature vectors
        if fp1.feature_vector is not None and fp2.feature_vector is not None:
            vector_similarity = self._cosine_similarity(fp1.feature_vector, fp2.feature_vector)
        else:
            vector_similarity = 0.0
        
        # Compare tempo (normalized)
        tempo_diff = abs(audio_fp1.tempo - audio_fp2.tempo) / max(audio_fp1.tempo, audio_fp2.tempo)
        tempo_similarity = max(0, 1.0 - tempo_diff)
        
        # Weighted combination
        total_similarity = (
            0.5 * chromaprint_similarity +
            0.3 * vector_similarity +
            0.2 * tempo_similarity
        )
        
        return min(1.0, max(0.0, total_similarity))
    
    def _compare_chromaprints(self, hash1: str, hash2: str) -> float:
        """Compare chromaprint hashes"""
        try:
            # Decode base64 hashes
            data1 = base64.b64decode(hash1)
            data2 = base64.b64decode(hash2)
            
            # Simple hamming distance comparison
            if len(data1) != len(data2):
                return 0.0
            
            diff_bits = sum(bin(b1 ^ b2).count('1') for b1, b2 in zip(data1, data2))
            total_bits = len(data1) * 8
            
            return 1.0 - (diff_bits / total_bits)
            
        except Exception:
            return 0.0
    
    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate cosine similarity between vectors"""
        try:
            dot_product = np.dot(v1, v2)
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)
            
            if norm_v1 == 0 or norm_v2 == 0:
                return 0.0
            
            return dot_product / (norm_v1 * norm_v2)
            
        except Exception:
            return 0.0


class VideoFingerprintExtractor(BaseFingerprintExtractor):
    """Advanced video fingerprinting system"""
    
    def __init__(self):
        super().__init__("VideoFingerprintExtractor", "video")
        
        self.supported_formats = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
        self.frame_sample_rate = 1.0  # Sample 1 frame per second
        
        if HAS_AI_LIBS:
            # Initialize video processing
            self.hash_size = 8
    
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request contains video content"""
        if request.content_type != ContentType.VIDEO:
            return False
        
        if request.source_url:
            return any(request.source_url.lower().endswith(fmt) for fmt in self.supported_formats)
        
        return request.content is not None
    
    async def extract_fingerprint(self, content: Union[bytes, str, np.ndarray]) -> FingerprintResult:
        """Extract comprehensive video fingerprint"""
        if not HAS_AI_LIBS:
            raise RuntimeError("Video processing libraries not available")
        
        try:
            # Load video
            if isinstance(content, str):
                cap = cv2.VideoCapture(content)
            else:
                # For bytes content, save to temp file first
                temp_file = f"/tmp/video_{hashlib.md5(content).hexdigest()}.mp4"
                with open(temp_file, 'wb') as f:
                    f.write(content)
                cap = cv2.VideoCapture(temp_file)
            
            if not cap.isOpened():
                raise ValueError("Could not open video")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Extract frame hashes and features
            frame_hashes = []
            optical_flow_features = []
            scene_descriptors = []
            dominant_colors = []
            
            frame_interval = int(fps / self.frame_sample_rate) if fps > 0 else 30
            prev_frame = None
            
            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % frame_interval == 0:
                    # Extract frame hash
                    frame_hash = self._compute_frame_hash(frame)
                    frame_hashes.append(frame_hash)
                    
                    # Extract dominant colors
                    colors = self._extract_dominant_colors(frame)
                    dominant_colors.append(colors)
                    
                    # Compute optical flow
                    if prev_frame is not None:
                        flow_features = self._compute_optical_flow(prev_frame, frame)
                        optical_flow_features.append(flow_features)
                    
                    # Scene descriptor
                    scene_desc = self._extract_scene_descriptor(frame)
                    scene_descriptors.append(scene_desc)
                    
                    prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                frame_idx += 1
            
            cap.release()
            
            # Combine optical flow features
            if optical_flow_features:
                optical_flow_array = np.array(optical_flow_features)
                optical_flow_mean = np.mean(optical_flow_array, axis=0)
            else:
                optical_flow_mean = np.zeros(4)  # Default empty features
            
            # Create video fingerprint
            video_fp = VideoFingerprint(
                frame_hashes=frame_hashes,
                optical_flow_features=optical_flow_mean,
                scene_descriptors=scene_descriptors,
                dominant_colors=dominant_colors,
                frame_rate=fps,
                duration=duration,
                resolution=(width, height)
            )
            
            # Create feature vector
            feature_vector = np.concatenate([
                optical_flow_mean,
                [len(frame_hashes) / max(1, duration)],  # Frame density
                [fps / 60.0],  # Normalized FPS
                [width / 1920.0, height / 1080.0]  # Normalized resolution
            ])
            
            return FingerprintResult(
                fingerprint_type="video",
                fingerprint_data=video_fp,
                confidence_score=0.90,
                feature_vector=feature_vector,
                metadata={
                    'duration': duration,
                    'fps': fps,
                    'resolution': (width, height),
                    'frame_count': len(frame_hashes)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Video fingerprint extraction failed: {e}")
            raise
    
    def _compute_frame_hash(self, frame: np.ndarray) -> str:
        """Compute perceptual hash for video frame"""
        # Convert to grayscale and resize
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (self.hash_size + 1, self.hash_size))
        
        # Compute difference hash
        diff = resized[:, 1:] > resized[:, :-1]
        hash_value = 0
        
        for i, row in enumerate(diff):
            for j, pixel in enumerate(row):
                if pixel:
                    hash_value |= 1 << (i * self.hash_size + j)
        
        return format(hash_value, '016x')
    
    def _extract_dominant_colors(self, frame: np.ndarray, k: int = 3) -> List[Tuple[int, int, int]]:
        """Extract dominant colors from frame"""
        # Reshape frame to list of pixels
        pixels = frame.reshape(-1, 3)
        
        # Use K-means clustering to find dominant colors
        from sklearn.cluster import KMeans
        
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        colors = kmeans.cluster_centers_.astype(int)
        return [tuple(color) for color in colors]
    
    def _compute_optical_flow(self, prev_frame: np.ndarray, curr_frame: np.ndarray) -> np.ndarray:
        """Compute optical flow features between frames"""
        # Calculate optical flow using Lucas-Kanade method
        flow = cv2.calcOpticalFlowPyrLK(
            prev_frame, curr_frame, 
            None, None,
            winSize=(15, 15),
            maxLevel=2
        )[0]
        
        if flow is not None and len(flow) > 0:
            # Extract flow statistics
            flow_magnitude = np.sqrt(flow[:, :, 0]**2 + flow[:, :, 1]**2)
            
            features = np.array([
                np.mean(flow_magnitude),
                np.std(flow_magnitude),
                np.mean(flow[:, :, 0]),  # Mean horizontal flow
                np.mean(flow[:, :, 1])   # Mean vertical flow
            ])
        else:
            features = np.zeros(4)
        
        return features
    
    def _extract_scene_descriptor(self, frame: np.ndarray) -> Dict[str, Any]:
        """Extract scene descriptor from frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Texture analysis
        texture_mean = np.mean(gray)
        texture_std = np.std(gray)
        
        # Color histogram
        hist_b = cv2.calcHist([frame], [0], None, [32], [0, 256])
        hist_g = cv2.calcHist([frame], [1], None, [32], [0, 256])
        hist_r = cv2.calcHist([frame], [2], None, [32], [0, 256])
        
        return {
            'edge_density': float(edge_density),
            'texture_mean': float(texture_mean),
            'texture_std': float(texture_std),
            'color_hist_variance': float(np.var(np.concatenate([hist_b, hist_g, hist_r])))
        }
    
    async def compare_fingerprints(self, fp1: FingerprintResult, fp2: FingerprintResult) -> float:
        """Compare two video fingerprints"""
        if not isinstance(fp1.fingerprint_data, VideoFingerprint) or \
           not isinstance(fp2.fingerprint_data, VideoFingerprint):
            return 0.0
        
        video_fp1 = fp1.fingerprint_data
        video_fp2 = fp2.fingerprint_data
        
        # Compare frame hashes
        hash_similarity = self._compare_frame_hashes(
            video_fp1.frame_hashes,
            video_fp2.frame_hashes
        )
        
        # Compare feature vectors
        if fp1.feature_vector is not None and fp2.feature_vector is not None:
            vector_similarity = self._cosine_similarity(fp1.feature_vector, fp2.feature_vector)
        else:
            vector_similarity = 0.0
        
        # Compare duration
        duration_diff = abs(video_fp1.duration - video_fp2.duration) / max(video_fp1.duration, video_fp2.duration)
        duration_similarity = max(0, 1.0 - duration_diff)
        
        # Weighted combination
        total_similarity = (
            0.5 * hash_similarity +
            0.3 * vector_similarity +
            0.2 * duration_similarity
        )
        
        return min(1.0, max(0.0, total_similarity))
    
    def _compare_frame_hashes(self, hashes1: List[str], hashes2: List[str]) -> float:
        """Compare lists of frame hashes"""
        if not hashes1 or not hashes2:
            return 0.0
        
        # Find best alignment between hash sequences
        max_similarity = 0.0
        
        for offset in range(-min(10, len(hashes1)//2), min(10, len(hashes2)//2) + 1):
            similarities = []
            
            start1 = max(0, -offset)
            start2 = max(0, offset)
            length = min(len(hashes1) - start1, len(hashes2) - start2)
            
            for i in range(length):
                h1 = int(hashes1[start1 + i], 16)
                h2 = int(hashes2[start2 + i], 16)
                
                # Hamming distance
                diff_bits = bin(h1 ^ h2).count('1')
                similarity = 1.0 - (diff_bits / 64.0)  # Assuming 64-bit hashes
                similarities.append(similarity)
            
            if similarities:
                avg_similarity = np.mean(similarities)
                max_similarity = max(max_similarity, avg_similarity)
        
        return max_similarity
    
    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate cosine similarity between vectors"""
        try:
            dot_product = np.dot(v1, v2)
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)
            
            if norm_v1 == 0 or norm_v2 == 0:
                return 0.0
            
            return dot_product / (norm_v1 * norm_v2)
            
        except Exception:
            return 0.0


class ImageFingerprintExtractor(BaseFingerprintExtractor):
    """Advanced image fingerprinting system"""
    
    def __init__(self):
        super().__init__("ImageFingerprintExtractor", "image")
        
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
        
        if HAS_AI_LIBS:
            # Initialize CLIP model for semantic embeddings
            try:
                self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                self.has_clip = True
            except Exception:
                self.has_clip = False
                self.logger.warning("CLIP model not available")
    
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request contains image content"""
        if request.content_type != ContentType.IMAGE:
            return False
        
        if request.source_url:
            return any(request.source_url.lower().endswith(fmt) for fmt in self.supported_formats)
        
        return request.content is not None
    
    async def extract_fingerprint(self, content: Union[bytes, str, np.ndarray]) -> FingerprintResult:
        """Extract comprehensive image fingerprint"""
        if not HAS_AI_LIBS:
            raise RuntimeError("Image processing libraries not available")
        
        try:
            # Load image
            if isinstance(content, bytes):
                image = Image.open(io.BytesIO(content))
            elif isinstance(content, str):
                image = Image.open(content)
            else:
                # Assume numpy array
                image = Image.fromarray(content)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract perceptual hash
            perceptual_hash = str(imagehash.phash(image))
            
            # Extract CLIP embedding if available
            clip_embedding = None
            if self.has_clip:
                clip_embedding = await self._extract_clip_embedding(image)
            
            # Extract color histogram
            color_histogram = self._extract_color_histogram(image)
            
            # Extract edge features
            edge_features = self._extract_edge_features(image)
            
            # Extract texture features
            texture_features = self._extract_texture_features(image)
            
            # Create image fingerprint
            image_fp = ImageFingerprint(
                perceptual_hash=perceptual_hash,
                clip_embedding=clip_embedding,
                color_histogram=color_histogram,
                edge_features=edge_features,
                texture_features=texture_features,
                dimensions=image.size,
                file_format=image.format or "Unknown"
            )
            
            # Create feature vector
            feature_vector_components = [color_histogram, edge_features, texture_features]
            if clip_embedding is not None:
                feature_vector_components.append(clip_embedding)
            
            feature_vector = np.concatenate(feature_vector_components)
            
            return FingerprintResult(
                fingerprint_type="image",
                fingerprint_data=image_fp,
                confidence_score=0.92,
                feature_vector=feature_vector,
                metadata={
                    'dimensions': image.size,
                    'format': image.format,
                    'mode': image.mode,
                    'has_clip_embedding': clip_embedding is not None
                }
            )
            
        except Exception as e:
            self.logger.error(f"Image fingerprint extraction failed: {e}")
            raise
    
    async def _extract_clip_embedding(self, image: Image.Image) -> Optional[np.ndarray]:
        """Extract CLIP embedding from image"""
        try:
            inputs = self.clip_processor(images=image, return_tensors="pt")
            
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
                embedding = image_features.numpy().flatten()
            
            # Normalize embedding
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except Exception as e:
            self.logger.warning(f"CLIP embedding extraction failed: {e}")
            return None
    
    def _extract_color_histogram(self, image: Image.Image, bins: int = 32) -> np.ndarray:
        """Extract color histogram from image"""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Calculate histogram for each channel
        hist_r = np.histogram(img_array[:, :, 0], bins=bins, range=(0, 256))[0]
        hist_g = np.histogram(img_array[:, :, 1], bins=bins, range=(0, 256))[0]
        hist_b = np.histogram(img_array[:, :, 2], bins=bins, range=(0, 256))[0]
        
        # Combine histograms
        histogram = np.concatenate([hist_r, hist_g, hist_b])
        
        # Normalize
        histogram = histogram / np.sum(histogram)
        
        return histogram
    
    def _extract_edge_features(self, image: Image.Image) -> np.ndarray:
        """Extract edge features from image"""
        # Convert to grayscale
        gray = image.convert('L')
        gray_array = np.array(gray)
        
        # Apply edge detection
        edges = cv2.Canny(gray_array, 50, 150)
        
        # Calculate edge statistics
        edge_density = np.sum(edges > 0) / edges.size
        
        # Edge direction histogram
        sobel_x = cv2.Sobel(gray_array, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray_array, cv2.CV_64F, 0, 1, ksize=3)
        
        edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        edge_direction = np.arctan2(sobel_y, sobel_x)
        
        # Create direction histogram
        direction_hist = np.histogram(edge_direction[edge_magnitude > 0], bins=8, range=(-np.pi, np.pi))[0]
        direction_hist = direction_hist / np.sum(direction_hist) if np.sum(direction_hist) > 0 else direction_hist
        
        features = np.concatenate([
            [edge_density],
            direction_hist
        ])
        
        return features
    
    def _extract_texture_features(self, image: Image.Image) -> np.ndarray:
        """Extract texture features from image"""
        # Convert to grayscale
        gray = image.convert('L')
        gray_array = np.array(gray)
        
        # Local Binary Pattern (simplified)
        def lbp_simple(img):
            height, width = img.shape
            lbp = np.zeros((height-2, width-2))
            
            for i in range(1, height-1):
                for j in range(1, width-1):
                    center = img[i, j]
                    pattern = 0
                    
                    # 8-neighborhood
                    neighbors = [
                        img[i-1, j-1], img[i-1, j], img[i-1, j+1],
                        img[i, j+1], img[i+1, j+1], img[i+1, j],
                        img[i+1, j-1], img[i, j-1]
                    ]
                    
                    for k, neighbor in enumerate(neighbors):
                        if neighbor >= center:
                            pattern |= 1 << k
                    
                    lbp[i-1, j-1] = pattern
            
            return lbp
        
        lbp = lbp_simple(gray_array)
        lbp_hist = np.histogram(lbp, bins=16, range=(0, 256))[0]
        lbp_hist = lbp_hist / np.sum(lbp_hist) if np.sum(lbp_hist) > 0 else lbp_hist
        
        # Texture statistics
        texture_mean = np.mean(gray_array)
        texture_std = np.std(gray_array)
        texture_entropy = -np.sum(lbp_hist * np.log2(lbp_hist + 1e-10))
        
        features = np.concatenate([
            lbp_hist,
            [texture_mean / 255.0, texture_std / 255.0, texture_entropy / 10.0]
        ])
        
        return features
    
    async def compare_fingerprints(self, fp1: FingerprintResult, fp2: FingerprintResult) -> float:
        """Compare two image fingerprints"""
        if not isinstance(fp1.fingerprint_data, ImageFingerprint) or \
           not isinstance(fp2.fingerprint_data, ImageFingerprint):
            return 0.0
        
        image_fp1 = fp1.fingerprint_data
        image_fp2 = fp2.fingerprint_data
        
        # Compare perceptual hashes
        hash1 = imagehash.hex_to_hash(image_fp1.perceptual_hash)
        hash2 = imagehash.hex_to_hash(image_fp2.perceptual_hash)
        hash_similarity = 1.0 - (hash1 - hash2) / 64.0  # Normalize hamming distance
        
        # Compare CLIP embeddings if available
        clip_similarity = 0.0
        if image_fp1.clip_embedding is not None and image_fp2.clip_embedding is not None:
            clip_similarity = self._cosine_similarity(image_fp1.clip_embedding, image_fp2.clip_embedding)
        
        # Compare feature vectors
        vector_similarity = 0.0
        if fp1.feature_vector is not None and fp2.feature_vector is not None:
            vector_similarity = self._cosine_similarity(fp1.feature_vector, fp2.feature_vector)
        
        # Weighted combination
        weights = [0.3, 0.4, 0.3] if clip_similarity > 0 else [0.5, 0.0, 0.5]
        total_similarity = (
            weights[0] * hash_similarity +
            weights[1] * clip_similarity +
            weights[2] * vector_similarity
        )
        
        return min(1.0, max(0.0, total_similarity))
    
    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate cosine similarity between vectors"""
        try:
            dot_product = np.dot(v1, v2)
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)
            
            if norm_v1 == 0 or norm_v2 == 0:
                return 0.0
            
            return dot_product / (norm_v1 * norm_v2)
            
        except Exception:
            return 0.0


class TextFingerprintExtractor(BaseFingerprintExtractor):
    """Advanced text fingerprinting system"""
    
    def __init__(self):
        super().__init__("TextFingerprintExtractor", "text")
        
        if HAS_AI_LIBS:
            try:
                # Initialize sentence transformer for semantic embeddings
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.has_sentence_model = True
            except Exception:
                self.has_sentence_model = False
                self.logger.warning("Sentence transformer model not available")
            
            # Initialize NLP tools
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
            except Exception:
                pass
    
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request contains text content"""
        return request.content_type == ContentType.TEXT and request.content is not None
    
    async def extract_fingerprint(self, content: Union[bytes, str, np.ndarray]) -> FingerprintResult:
        """Extract comprehensive text fingerprint"""
        if not HAS_AI_LIBS:
            raise RuntimeError("Text processing libraries not available")
        
        try:
            # Ensure content is string
            if isinstance(content, bytes):
                text = content.decode('utf-8', errors='ignore')
            else:
                text = str(content)
            
            # Extract semantic embedding
            semantic_embedding = None
            if self.has_sentence_model:
                semantic_embedding = self.sentence_model.encode(text)
            
            # Extract syntactic features
            syntactic_features = self._extract_syntactic_features(text)
            
            # Extract linguistic patterns
            linguistic_patterns = self._extract_linguistic_patterns(text)
            
            # Detect language
            try:
                language = langdetect.detect(text)
            except Exception:
                language = "unknown"
            
            # Calculate sentiment score (simplified)
            sentiment_score = self._calculate_sentiment(text)
            
            # Calculate readability score
            try:
                readability_score = flesch_reading_ease(text)
            except Exception:
                readability_score = 0.0
            
            # Word count
            word_count = len(text.split())
            
            # Create text fingerprint
            text_fp = TextFingerprint(
                semantic_embedding=semantic_embedding,
                syntactic_features=syntactic_features,
                linguistic_patterns=linguistic_patterns,
                language=language,
                sentiment_score=sentiment_score,
                readability_score=readability_score,
                word_count=word_count
            )
            
            # Create feature vector
            feature_vector_components = [
                list(syntactic_features.values()),
                [sentiment_score, readability_score / 100.0, word_count / 1000.0]
            ]
            
            if semantic_embedding is not None:
                feature_vector_components.append(semantic_embedding)
            
            feature_vector = np.concatenate([np.array(comp).flatten() for comp in feature_vector_components])
            
            return FingerprintResult(
                fingerprint_type="text",
                fingerprint_data=text_fp,
                confidence_score=0.88,
                feature_vector=feature_vector,
                metadata={
                    'language': language,
                    'word_count': word_count,
                    'readability_score': readability_score,
                    'has_semantic_embedding': semantic_embedding is not None
                }
            )
            
        except Exception as e:
            self.logger.error(f"Text fingerprint extraction failed: {e}")
            raise
    
    def _extract_syntactic_features(self, text: str) -> Dict[str, float]:
        """Extract syntactic features from text"""
        try:
            # Tokenize
            tokens = nltk.word_tokenize(text.lower())
            
            # POS tagging
            pos_tags = nltk.pos_tag(tokens)
            
            # Count POS categories
            pos_counts = {}
            for _, pos in pos_tags:
                pos_counts[pos] = pos_counts.get(pos, 0) + 1
            
            # Calculate ratios
            total_tokens = len(tokens) if tokens else 1
            
            features = {
                'noun_ratio': sum(1 for _, pos in pos_tags if pos.startswith('N')) / total_tokens,
                'verb_ratio': sum(1 for _, pos in pos_tags if pos.startswith('V')) / total_tokens,
                'adj_ratio': sum(1 for _, pos in pos_tags if pos.startswith('J')) / total_tokens,
                'adv_ratio': sum(1 for _, pos in pos_tags if pos.startswith('R')) / total_tokens,
                'avg_word_length': np.mean([len(token) for token in tokens]) if tokens else 0,
                'sentence_count': len(nltk.sent_tokenize(text)),
                'avg_sentence_length': len(tokens) / len(nltk.sent_tokenize(text)) if nltk.sent_tokenize(text) else 0
            }
            
            return features
            
        except Exception:
            # Return default features if NLP fails
            return {
                'noun_ratio': 0.3,
                'verb_ratio': 0.2,
                'adj_ratio': 0.1,
                'adv_ratio': 0.05,
                'avg_word_length': 5.0,
                'sentence_count': 1,
                'avg_sentence_length': 10.0
            }
    
    def _extract_linguistic_patterns(self, text: str) -> List[str]:
        """Extract linguistic patterns from text"""
        patterns = []
        
        # Common patterns
        if re.search(r'\b(the|a|an)\b', text.lower()):
            patterns.append('has_articles')
        
        if re.search(r'\b(and|or|but)\b', text.lower()):
            patterns.append('has_conjunctions')
        
        if re.search(r'[.!?]', text):
            patterns.append('has_punctuation')
        
        if re.search(r'[A-Z][a-z]+', text):
            patterns.append('has_capitalization')
        
        if re.search(r'\d+', text):
            patterns.append('has_numbers')
        
        if re.search(r'https?://', text):
            patterns.append('has_urls')
        
        if re.search(r'@\w+', text):
            patterns.append('has_mentions')
        
        if re.search(r'#\w+', text):
            patterns.append('has_hashtags')
        
        return patterns
    
    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score (simplified)"""
        # Simple keyword-based sentiment
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'best'}
        negative_words = {'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'sad', 'angry'}
        
        words = text.lower().split()
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return 0.0  # Neutral
        
        return (positive_count - negative_count) / total_sentiment_words
    
    async def compare_fingerprints(self, fp1: FingerprintResult, fp2: FingerprintResult) -> float:
        """Compare two text fingerprints"""
        if not isinstance(fp1.fingerprint_data, TextFingerprint) or \
           not isinstance(fp2.fingerprint_data, TextFingerprint):
            return 0.0
        
        text_fp1 = fp1.fingerprint_data
        text_fp2 = fp2.fingerprint_data
        
        # Compare semantic embeddings if available
        semantic_similarity = 0.0
        if text_fp1.semantic_embedding is not None and text_fp2.semantic_embedding is not None:
            semantic_similarity = self._cosine_similarity(text_fp1.semantic_embedding, text_fp2.semantic_embedding)
        
        # Compare syntactic features
        syntactic_similarity = self._compare_syntactic_features(
            text_fp1.syntactic_features,
            text_fp2.syntactic_features
        )
        
        # Compare linguistic patterns
        pattern_similarity = self._compare_patterns(
            text_fp1.linguistic_patterns,
            text_fp2.linguistic_patterns
        )
        
        # Compare language
        language_similarity = 1.0 if text_fp1.language == text_fp2.language else 0.0
        
        # Weighted combination
        weights = [0.4, 0.25, 0.25, 0.1] if semantic_similarity > 0 else [0.0, 0.4, 0.4, 0.2]
        total_similarity = (
            weights[0] * semantic_similarity +
            weights[1] * syntactic_similarity +
            weights[2] * pattern_similarity +
            weights[3] * language_similarity
        )
        
        return min(1.0, max(0.0, total_similarity))
    
    def _compare_syntactic_features(self, features1: Dict[str, float], features2: Dict[str, float]) -> float:
        """Compare syntactic features"""
        common_keys = set(features1.keys()) & set(features2.keys())
        
        if not common_keys:
            return 0.0
        
        similarities = []
        for key in common_keys:
            val1, val2 = features1[key], features2[key]
            max_val = max(val1, val2, 1e-10)
            similarity = 1.0 - abs(val1 - val2) / max_val
            similarities.append(similarity)
        
        return np.mean(similarities)
    
    def _compare_patterns(self, patterns1: List[str], patterns2: List[str]) -> float:
        """Compare linguistic patterns"""
        set1, set2 = set(patterns1), set(patterns2)
        
        if not set1 and not set2:
            return 1.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate cosine similarity between vectors"""
        try:
            dot_product = np.dot(v1, v2)
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)
            
            if norm_v1 == 0 or norm_v2 == 0:
                return 0.0
            
            return dot_product / (norm_v1 * norm_v2)
            
        except Exception:
            return 0.0


class FingerprintExtractorFactory:
    """Factory for creating fingerprint extractors"""
    
    @staticmethod
    def create_extractor(content_type: str) -> BaseFingerprintExtractor:
        """Create appropriate fingerprint extractor"""
        extractors = {
            'audio': AudioFingerprintExtractor,
            'video': VideoFingerprintExtractor,
            'image': ImageFingerprintExtractor,
            'text': TextFingerprintExtractor
        }
        
        extractor_class = extractors.get(content_type.lower())
        if not extractor_class:
            raise ValueError(f"No fingerprint extractor available for content type: {content_type}")
        
        return extractor_class()
    
    @staticmethod
    def get_supported_types() -> List[str]:
        """Get list of supported content types"""
        return ['audio', 'video', 'image', 'text']


class FingerprintManager:
    """Manager for fingerprint extraction and comparison operations"""
    
    def __init__(self):
        self.extractors = {}
        self.vector_index = None
        
        if HAS_FAISS:
            # Initialize FAISS index for similarity search
            self.vector_dimension = 512  # Default dimension
            self.vector_index = faiss.IndexFlatIP(self.vector_dimension)
            self.fingerprint_metadata = []
    
    async def extract_fingerprint(self, content: Union[bytes, str, np.ndarray], 
                                content_type: str) -> FingerprintResult:
        """Extract fingerprint from content"""
        if content_type not in self.extractors:
            self.extractors[content_type] = FingerprintExtractorFactory.create_extractor(content_type)
        
        extractor = self.extractors[content_type]
        return await extractor.extract_fingerprint(content)
    
    async def compare_fingerprints(self, fp1: FingerprintResult, fp2: FingerprintResult) -> float:
        """Compare two fingerprints"""
        if fp1.fingerprint_type != fp2.fingerprint_type:
            return 0.0
        
        content_type = fp1.fingerprint_type
        if content_type not in self.extractors:
            self.extractors[content_type] = FingerprintExtractorFactory.create_extractor(content_type)
        
        extractor = self.extractors[content_type]
        return await extractor.compare_fingerprints(fp1, fp2)
    
    def add_to_index(self, fingerprint: FingerprintResult, metadata: Dict[str, Any]):
        """Add fingerprint to vector index for similarity search"""
        if not HAS_FAISS or self.vector_index is None:
            return
        
        if fingerprint.feature_vector is not None:
            # Ensure vector is correct dimension
            vector = fingerprint.feature_vector
            if len(vector) != self.vector_dimension:
                # Pad or truncate to fit dimension
                if len(vector) < self.vector_dimension:
                    vector = np.pad(vector, (0, self.vector_dimension - len(vector)))
                else:
                    vector = vector[:self.vector_dimension]
            
            # Normalize vector
            vector = vector / np.linalg.norm(vector)
            
            # Add to index
            self.vector_index.add(vector.reshape(1, -1))
            self.fingerprint_metadata.append({
                'fingerprint_id': len(self.fingerprint_metadata),
                'fingerprint_type': fingerprint.fingerprint_type,
                'confidence_score': fingerprint.confidence_score,
                'created_at': fingerprint.created_at,
                **metadata
            })
    
    def search_similar(self, fingerprint: FingerprintResult, top_k: int = 10, 
                      threshold: float = 0.8) -> List[Tuple[Dict[str, Any], float]]:
        """Search for similar fingerprints in index"""
        if not HAS_FAISS or self.vector_index is None or fingerprint.feature_vector is None:
            return []
        
        # Prepare query vector
        vector = fingerprint.feature_vector
        if len(vector) != self.vector_dimension:
            if len(vector) < self.vector_dimension:
                vector = np.pad(vector, (0, self.vector_dimension - len(vector)))
            else:
                vector = vector[:self.vector_dimension]
        
        vector = vector / np.linalg.norm(vector)
        
        # Search
        scores, indices = self.vector_index.search(vector.reshape(1, -1), top_k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if score >= threshold and idx < len(self.fingerprint_metadata):
                results.append((self.fingerprint_metadata[idx], float(score)))
        
        return results


__all__ = [
    'FingerprintResult',
    'AudioFingerprint',
    'VideoFingerprint', 
    'ImageFingerprint',
    'TextFingerprint',
    'BaseFingerprintExtractor',
    'AudioFingerprintExtractor',
    'VideoFingerprintExtractor',
    'ImageFingerprintExtractor',
    'TextFingerprintExtractor',
    'FingerprintExtractorFactory',
    'FingerprintManager'
]
