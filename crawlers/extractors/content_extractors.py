"""
Content Extractors - Industrial IA Content Processing System
==========================================================

Ultra-advanced professional content extraction for audio, video, image, and text processing.
Implements enterprise-grade content analysis and metadata extraction capabilities with AI.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

 STRICT COPYRIGHT PROTECTION 
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.
"""

import asyncio
import logging
import io
import mimetypes
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple, BinaryIO
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import json
import base64
from urllib.parse import urlparse
import aiohttp
import aiofiles

# Audio processing
# Audio processing with advanced fingerprinting
try:
    import librosa
    import soundfile as sf
    import numpy as np
    import essentia.standard as es
    import chromaprint
    import pyAudioAnalysis.audioFeatureExtraction as aF
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False

# Video processing with AI recognition
try:
    import cv2
    import ffmpeg
    import torch
    import torchvision.transforms as transforms
    from torchvision.models import resnet50
    import face_recognition
    HAS_VIDEO = True
except ImportError:
    HAS_VIDEO = False

# Image processing with CLIP embeddings
try:
    from PIL import Image, ImageStat, ImageFilter, ImageEnhance
    import imagehash
    import clip
    import torch
    from transformers import CLIPProcessor, CLIPModel
    import cv2
    HAS_IMAGE = True
except ImportError:
    HAS_IMAGE = False

# Text processing with semantic understanding
try:
    import nltk
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    import langdetect
    from transformers import AutoTokenizer, AutoModel, pipeline
    import spacy
    import gensim
    HAS_TEXT = True
except ImportError:
    HAS_TEXT = False

# Advanced ML and fingerprinting
try:
    import faiss
    import sklearn
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import tensorflow as tf
    HAS_ML = True
except ImportError:
    HAS_ML = False

from .extraction_engine import BaseExtractor, ExtractionRequest, ExtractionResult, ExtractionStatus, ContentType

logger = logging.getLogger(__name__)


@dataclass
class ContentMetadata:
    """Advanced content metadata container with AI features"""
    
    # Basic metadata
    file_size: int = 0
    mime_type: Optional[str] = None
    encoding: Optional[str] = None
    duration: Optional[float] = None
    dimensions: Optional[Tuple[int, int]] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    quality_score: float = 0.0
    content_hash: Optional[str] = None
    language: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    
    # Advanced AI metadata
    fingerprint_hash: Optional[str] = None
    ai_features: Dict[str, Any] = field(default_factory=dict)
    semantic_embedding: Optional[List[float]] = None
    similarity_scores: Dict[str, float] = field(default_factory=dict)
    content_category: Optional[str] = None
    content_tags: List[str] = field(default_factory=list)
    protection_level: str = "medium"
    monetization_potential: float = 0.0
    collaboration_matches: List[Dict] = field(default_factory=list)
    
    # Compliance and legal
    copyright_status: str = "unknown"
    licensing_info: Optional[Dict] = None
    usage_rights: List[str] = field(default_factory=list)
    content_warnings: List[str] = field(default_factory=list)
    
    # Performance metrics
    extraction_time: float = 0.0
    processing_quality: float = 0.0
    confidence_score: float = 0.0


@dataclass
class AudioFeatures:
    """Advanced audio feature container"""
    
    # Basic audio features
    mfcc: Optional[np.ndarray] = None
    spectral_centroid: Optional[np.ndarray] = None
    spectral_rolloff: Optional[np.ndarray] = None
    zero_crossing_rate: Optional[np.ndarray] = None
    chroma: Optional[np.ndarray] = None
    mel_spectrogram: Optional[np.ndarray] = None
    
    # Advanced features
    chromaprint_fingerprint: Optional[str] = None
    audio_fingerprint: Optional[np.ndarray] = None
    tempo: Optional[float] = None
    key: Optional[str] = None
    loudness: Optional[float] = None
    energy: Optional[float] = None
    
    # AI-extracted features
    mood_classification: Optional[Dict[str, float]] = None
    genre_prediction: Optional[Dict[str, float]] = None
    instrumental_confidence: float = 0.0
    speech_detection: float = 0.0
    music_similarity_vector: Optional[List[float]] = None


@dataclass  
class VideoFeatures:
    """Advanced video feature container"""
    
    # Basic video features
    frame_count: int = 0
    fps: float = 0.0
    resolution: Optional[Tuple[int, int]] = None
    aspect_ratio: float = 0.0
    codec: Optional[str] = None
    
    # Visual features
    keyframes: List[np.ndarray] = field(default_factory=list)
    dominant_colors: List[Tuple[int, int, int]] = field(default_factory=list)
    scene_changes: List[float] = field(default_factory=list)
    motion_vectors: Optional[np.ndarray] = None
    
    # AI features
    object_detection: List[Dict] = field(default_factory=list)
    face_detection: List[Dict] = field(default_factory=list)
    text_recognition: List[Dict] = field(default_factory=list)
    content_classification: Optional[Dict[str, float]] = None
    visual_similarity_hash: Optional[str] = None


@dataclass
class ImageFeatures:
    """Advanced image feature container"""
    
    # Basic image features
    color_histogram: Optional[np.ndarray] = None
    dominant_colors: List[Tuple[int, int, int]] = field(default_factory=list)
    brightness: float = 0.0
    contrast: float = 0.0
    sharpness: float = 0.0
    
    # Hash features
    perceptual_hash: Optional[str] = None
    difference_hash: Optional[str] = None
    average_hash: Optional[str] = None
    wavelet_hash: Optional[str] = None
    
    # AI features
    clip_embedding: Optional[List[float]] = None
    object_detection: List[Dict] = field(default_factory=list)
    face_detection: List[Dict] = field(default_factory=list)
    text_detection: List[str] = field(default_factory=list)
    style_classification: Optional[Dict[str, float]] = None
    aesthetic_score: float = 0.0


@dataclass
class TextFeatures:
    """Advanced text feature container"""
    
    # Basic text features
    word_count: int = 0
    character_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    readability_score: float = 0.0
    language_confidence: float = 0.0
    
    # Semantic features
    semantic_embedding: Optional[List[float]] = None
    topic_distribution: Optional[Dict[str, float]] = None
    sentiment_score: float = 0.0
    emotion_analysis: Optional[Dict[str, float]] = None
    
    # Content analysis
    keywords: List[str] = field(default_factory=list)
    entities: List[Dict] = field(default_factory=list)
    key_phrases: List[str] = field(default_factory=list)
    content_categories: List[str] = field(default_factory=list)
    
    # Quality metrics
    grammar_score: float = 0.0
    plagiarism_risk: float = 0.0
    uniqueness_score: float = 0.0


class AudioContentExtractor(BaseExtractor):
    """Industrial-grade audio content extractor with AI fingerprinting"""
    
    def __init__(self):
        super().__init__("AudioContentExtractor")
        self.supported_formats = {
            '.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma', 
            '.mp4', '.avi', '.mov', '.webm'  # Video with audio
        }
        
        self.fingerprint_models = {}
        self.feature_extractors = {}
        
        if not HAS_AUDIO:
            self.logger.warning("Audio processing libraries not available")
            
        self._initialize_audio_models()
    
    def _initialize_audio_models(self):
        """Initialize audio processing models"""



        try:
            if HAS_AUDIO:
                # Initialize Essentia extractors
                self.feature_extractors = {
                    'mfcc': es.MFCC(),
                    'spectral_centroid': es.SpectralCentroid(),
                    'spectral_rolloff': es.RollOff(),
                    'zero_crossing_rate': es.ZeroCrossingRate(),
                    'chromagram': es.HPCP(),
                    'tempo': es.PercivalBpmEstimator(),
                    'key': es.KeyExtractor(),
                    'loudness': es.Loudness()
                }
                
                # Initialize windowing for frame-based analysis
                self.windowing = es.Windowing(type='hann')
                self.spectrum = es.Spectrum()
                
                self.logger.info("Audio models initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize audio models: {e}")
    
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request contains audio content"""
        if request.content_type == ContentType.AUDIO:
            return True
            
        # Check file extension
        if request.url:
            path = Path(urlparse(request.url).path)
            return path.suffix.lower() in self.supported_formats
            
        # Check MIME type
        if request.content and hasattr(request.content, 'content_type'):
            return request.content.content_type.startswith('audio/')
            
        return False
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract comprehensive audio features and metadata"""
        start_time = datetime.now()
        
        try:
            # Load audio data
            audio_data, sample_rate = await self._load_audio(request)
            
            if audio_data is None:
                return ExtractionResult(
                    extractor_name=self.name,
                    status=ExtractionStatus.FAILED,
                    error="Failed to load audio data"
                )
            
            # Extract basic metadata
            metadata = await self._extract_basic_metadata(audio_data, sample_rate, request)
            
            # Extract advanced audio features
            audio_features = await self._extract_audio_features(audio_data, sample_rate)
            
            # Generate fingerprints
            fingerprints = await self._generate_fingerprints(audio_data, sample_rate)
            
            # AI-based analysis
            ai_analysis = await self._ai_content_analysis(audio_data, sample_rate)
            
            # Calculate quality scores
            quality_metrics = await self._calculate_quality_metrics(audio_data, sample_rate)
            
            # Monetization potential analysis
            monetization_score = await self._analyze_monetization_potential(
                audio_features, ai_analysis
            )
            
            # Combine all results
            metadata.ai_features.update({
                'audio_features': audio_features.__dict__,
                'fingerprints': fingerprints,
                'ai_analysis': ai_analysis,
                'quality_metrics': quality_metrics,
                'monetization_score': monetization_score
            })
            
            extraction_time = (datetime.now() - start_time).total_seconds()
            metadata.extraction_time = extraction_time
            
            return ExtractionResult(
                extractor_name=self.name,
                status=ExtractionStatus.SUCCESS,
                content_type=ContentType.AUDIO,
                metadata=metadata,
                data={
                    'audio_features': audio_features,
                    'fingerprints': fingerprints,
                    'ai_analysis': ai_analysis,
                    'quality_metrics': quality_metrics
                },
                processing_time=extraction_time
            )
            
        except Exception as e:
            self.logger.error(f"Audio extraction failed: {e}")
            return ExtractionResult(
                extractor_name=self.name,
                status=ExtractionStatus.FAILED,
                error=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _load_audio(self, request: ExtractionRequest) -> Tuple[Optional[np.ndarray], Optional[int]]:
        """Load audio data from various sources"""



        try:
            if request.file_path:
                # Load from file
                audio_data, sample_rate = librosa.load(request.file_path, sr=None)
                return audio_data, sample_rate
                
            elif request.content:
                # Load from binary content
                with io.BytesIO(request.content) as audio_buffer:
                    audio_data, sample_rate = librosa.load(audio_buffer, sr=None)
                    return audio_data, sample_rate
                    
            elif request.url:
                # Download and load from URL
                async with aiohttp.ClientSession() as session:
                    async with session.get(request.url) as response:
                        if response.status == 200:
                            content = await response.read()
                            with io.BytesIO(content) as audio_buffer:
                                audio_data, sample_rate = librosa.load(audio_buffer, sr=None)
                                return audio_data, sample_rate
                                
            return None, None
            
        except Exception as e:
            self.logger.error(f"Failed to load audio: {e}")
            return None, None
    
    async def _extract_basic_metadata(
        self, audio_data: np.ndarray, sample_rate: int, request: ExtractionRequest
    ) -> ContentMetadata:
        """Extract basic audio metadata"""
        
        duration = len(audio_data) / sample_rate
        file_size = len(audio_data) * 4  # Assuming 32-bit float
        
        # Calculate content hash
        content_hash = hashlib.sha256(audio_data.tobytes()).hexdigest()
        
        metadata = ContentMetadata(
            file_size=file_size,
            mime_type="audio/wav",  # Default after loading
            duration=duration,
            sample_rate=sample_rate,
            channels=1 if len(audio_data.shape) == 1 else audio_data.shape[1],
            content_hash=content_hash,
            created_at=datetime.now()
        )
        
        return metadata
    
    async def _extract_audio_features(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> AudioFeatures:
        """Extract comprehensive audio features"""
        
        features = AudioFeatures()
        
        try:
            # MFCC features
            mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            features.mfcc = np.mean(mfcc, axis=1)
            
            # Spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            features.spectral_centroid = np.mean(spectral_centroid)
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
            features.spectral_rolloff = np.mean(spectral_rolloff)
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio_data)
            features.zero_crossing_rate = np.mean(zcr)
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            features.chroma = np.mean(chroma, axis=1)
            
            # Mel spectrogram
            mel_spec = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate)
            features.mel_spectrogram = np.mean(mel_spec, axis=1)
            
            # Tempo estimation
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            features.tempo = float(tempo)
            
            # Energy calculation
            features.energy = np.mean(audio_data ** 2)
            
            # Loudness (RMS)
            rms = librosa.feature.rms(y=audio_data)
            features.loudness = np.mean(rms)
            
            # Advanced Essentia features if available
            if HAS_AUDIO and self.feature_extractors:
                await self._extract_essentia_features(audio_data, sample_rate, features)
                
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
            
        return features
    
    async def _extract_essentia_features(
        self, audio_data: np.ndarray, sample_rate: int, features: AudioFeatures
    ):
        """Extract advanced features using Essentia"""



        try:
            # Convert to Essentia format
            audio_essentia = es.MonoLoader(filename="", sampleRate=sample_rate)()
            
            # Key detection
            key_extractor = self.feature_extractors.get('key')
            if key_extractor:
                key, scale, strength = key_extractor(audio_essentia)
                features.key = f"{key} {scale}"
            
            # More advanced analysis can be added here
            
        except Exception as e:
            self.logger.error(f"Essentia feature extraction failed: {e}")
    
    async def _generate_fingerprints(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> Dict[str, Any]:
        """Generate multiple types of audio fingerprints"""
        
        fingerprints = {}
        
        try:
            # Chromaprint fingerprint
            if HAS_AUDIO:
                # Convert to appropriate format for chromaprint
                audio_int16 = (audio_data * 32767).astype(np.int16)
                duration = len(audio_data) / sample_rate
                
                fingerprint = chromaprint.fingerprint(audio_int16, sample_rate)
                fingerprints['chromaprint'] = fingerprint
            
            # Spectral hash fingerprint
            spectral_hash = await self._generate_spectral_hash(audio_data, sample_rate)
            fingerprints['spectral_hash'] = spectral_hash
            
            # MFCC-based fingerprint
            mfcc_fingerprint = await self._generate_mfcc_fingerprint(audio_data, sample_rate)
            fingerprints['mfcc_fingerprint'] = mfcc_fingerprint
            
        except Exception as e:
            self.logger.error(f"Fingerprint generation failed: {e}")
            
        return fingerprints
    
    async def _generate_spectral_hash(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> str:
        """Generate spectral-based hash fingerprint"""



        try:
            # Compute spectrogram
            stft = librosa.stft(audio_data)
            magnitude = np.abs(stft)
            
            # Reduce to key spectral bands
            mel_basis = librosa.filters.mel(sr=sample_rate, n_fft=2048, n_mels=32)
            mel_spec = np.dot(mel_basis, magnitude)
            
            # Create hash from spectral peaks
            peaks = np.mean(mel_spec, axis=1)
            binary_hash = ''.join('1' if peak > np.median(peaks) else '0' for peak in peaks)
            
            return hashlib.md5(binary_hash.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Spectral hash generation failed: {e}")
            return ""
    
    async def _generate_mfcc_fingerprint(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> str:
        """Generate MFCC-based fingerprint"""



        try:
            mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            mfcc_mean = np.mean(mfcc, axis=1)
            
            # Quantize and create binary representation
            mfcc_quantized = np.digitize(mfcc_mean, np.linspace(mfcc_mean.min(), mfcc_mean.max(), 16))
            binary_repr = ''.join(format(x, '04b') for x in mfcc_quantized)
            
            return hashlib.sha256(binary_repr.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"MFCC fingerprint generation failed: {e}")
            return ""
    
    async def _ai_content_analysis(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> Dict[str, Any]:
        """AI-based content analysis"""
        
        analysis = {
            'mood_classification': {},
            'genre_prediction': {},
            'instrumental_confidence': 0.0,
            'speech_detection': 0.0,
            'content_category': 'unknown'
        }
        
        try:
            # Basic speech detection using spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
            
            # Simple heuristic for speech vs music
            centroid_mean = np.mean(spectral_centroid)
            rolloff_mean = np.mean(spectral_rolloff)
            
            if centroid_mean > 2000 and rolloff_mean > 8000:
                analysis['speech_detection'] = 0.8
                analysis['instrumental_confidence'] = 0.2
                analysis['content_category'] = 'speech'
            else:
                analysis['speech_detection'] = 0.2
                analysis['instrumental_confidence'] = 0.8
                analysis['content_category'] = 'music'
            
            # Mood analysis based on spectral features
            energy = np.mean(audio_data ** 2)
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            
            if energy > 0.01 and tempo > 120:
                analysis['mood_classification'] = {'energetic': 0.8, 'calm': 0.2}
            else:
                analysis['mood_classification'] = {'calm': 0.8, 'energetic': 0.2}
                
        except Exception as e:
            self.logger.error(f"AI content analysis failed: {e}")
            
        return analysis
    
    async def _calculate_quality_metrics(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> Dict[str, float]:
        """Calculate audio quality metrics"""
        
        metrics = {
            'signal_to_noise_ratio': 0.0,
            'dynamic_range': 0.0,
            'frequency_response': 0.0,
            'distortion_level': 0.0,
            'overall_quality': 0.0
        }
        
        try:
            # Signal-to-noise ratio estimation
            signal_power = np.mean(audio_data ** 2)
            noise_estimation = np.mean(np.abs(np.diff(audio_data))) / np.sqrt(2)
            
            if noise_estimation > 0:
                snr = 10 * np.log10(signal_power / (noise_estimation ** 2))
                metrics['signal_to_noise_ratio'] = max(0, min(100, snr))
            
            # Dynamic range
            rms = librosa.feature.rms(y=audio_data)
            dynamic_range = np.max(rms) / (np.min(rms) + 1e-10)
            metrics['dynamic_range'] = min(100, 20 * np.log10(dynamic_range))
            
            # Frequency response analysis
            stft = librosa.stft(audio_data)
            magnitude = np.abs(stft)
            freq_response = np.mean(magnitude, axis=1)
            freq_balance = 1.0 - np.std(freq_response) / (np.mean(freq_response) + 1e-10)
            metrics['frequency_response'] = max(0, min(100, freq_balance * 100))
            
            # Overall quality score
            metrics['overall_quality'] = np.mean([
                metrics['signal_to_noise_ratio'] / 100,
                metrics['dynamic_range'] / 100,
                metrics['frequency_response'] / 100
            ]) * 100
            
        except Exception as e:
            self.logger.error(f"Quality metrics calculation failed: {e}")
            
        return metrics
    
    async def _analyze_monetization_potential(
        self, audio_features: AudioFeatures, ai_analysis: Dict[str, Any]
    ) -> float:
        """Analyze monetization potential based on audio characteristics"""



        
        try:
            score = 0.0
            
            # Quality-based scoring
            if hasattr(audio_features, 'energy') and audio_features.energy:
                score += min(30, audio_features.energy * 1000)  # Energy factor
            
            # Content type scoring
            if ai_analysis.get('content_category') == 'music':
                score += 40  # Music has higher monetization potential
            elif ai_analysis.get('content_category') == 'speech':
                score += 25  # Speech content (podcasts, etc.)
            
            # Mood and engagement scoring
            mood_scores = ai_analysis.get('mood_classification', {})
            if mood_scores.get('energetic', 0) > 0.6:
                score += 20  # Energetic content performs better
            
            # Duration factor
            if hasattr(audio_features, 'duration'):
                # Optimal duration range for monetization
                if 30 <= getattr(audio_features, 'duration', 0) <= 300:  # 30s to 5min
                    score += 10
            
            return min(100, max(0, score))
            
        except Exception as e:
            self.logger.error(f"Monetization analysis failed: {e}")
            return 0.0
        
        if request.content_type != ContentType.AUDIO:
            return False
        
        if not HAS_AUDIO:
            return False
        
        # Check file extension if path provided
        if request.source_path:
            path = Path(request.source_path)
            return path.suffix.lower() in self.supported_formats
        
        # Check URL extension
        if request.source_url:
            parsed = urlparse(request.source_url)
            path = Path(parsed.path)
            return path.suffix.lower() in self.supported_formats
        
        return True
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract audio content and metadata"""
        
        start_time = datetime.utcnow()
        result = ExtractionResult(
            request_id=request.request_id,
            status=ExtractionStatus.RUNNING
        )
        
        try:
            # Load audio data
            audio_data = await self._load_audio_data(request)
            if not audio_data:
                result.status = ExtractionStatus.FAILED
                result.errors.append("Failed to load audio data")
                return result
            
            # Extract audio features
            features = await self._extract_audio_features(audio_data, request)
            result.extracted_data.update(features)
            
            # Extract metadata
            metadata = await self._extract_audio_metadata(audio_data, request)
            result.metadata.update(metadata)
            
            # Calculate quality score
            quality_score = await self._calculate_audio_quality(audio_data)
            result.quality_score = quality_score
            
            # Generate content hash
            if isinstance(audio_data, np.ndarray):
                content_bytes = audio_data.tobytes()
            else:
                content_bytes = audio_data
            
            result.content_hash = hashlib.sha256(content_bytes).hexdigest()
            result.file_size = len(content_bytes)
            
            result.status = ExtractionStatus.COMPLETED
            self.logger.info(f"Audio extraction completed for {request.request_id}")
            
        except Exception as e:
            self.logger.error(f"Audio extraction failed: {e}")
            result.status = ExtractionStatus.FAILED
            result.errors.append(str(e))
        
        finally:
            result.extraction_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_stats(result.status == ExtractionStatus.COMPLETED, result.extraction_time)
        
        return result
    
    async def _load_audio_data(self, request: ExtractionRequest) -> Optional[np.ndarray]:
        """Load audio data from various sources"""



        
        try:
            if request.source_data:
                # Load from binary data
                audio_buffer = io.BytesIO(request.source_data)
                y, sr = librosa.load(audio_buffer, sr=None)
                return y
            
            elif request.source_path:
                # Load from file path
                y, sr = librosa.load(request.source_path, sr=None)
                return y
            
            elif request.source_url:
                # Load from URL
                async with aiohttp.ClientSession() as session:
                    async with session.get(request.source_url) as response:
                        if response.status == 200:
                            data = await response.read()
                            audio_buffer = io.BytesIO(data)
                            y, sr = librosa.load(audio_buffer, sr=None)
                            return y
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to load audio data: {e}")
            return None
    
    async def _extract_audio_features(self, audio_data: np.ndarray, request: ExtractionRequest) -> Dict[str, Any]:
        """Extract comprehensive audio features"""
        
        features = {}
        
        try:
            # Basic audio properties
            features['duration'] = len(audio_data) / 22050  # Default sample rate
            features['amplitude'] = {
                'max': float(np.max(np.abs(audio_data))),
                'mean': float(np.mean(np.abs(audio_data))),
                'rms': float(np.sqrt(np.mean(audio_data**2)))
            }
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data)[0]
            features['spectral_centroid'] = {
                'mean': float(np.mean(spectral_centroids)),
                'std': float(np.std(spectral_centroids))
            }
            
            # Rhythm features
            tempo, beats = librosa.beat.beat_track(y=audio_data)
            features['tempo'] = float(tempo)
            features['beat_count'] = len(beats)
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, n_mfcc=13)
            features['mfcc'] = {
                'mean': mfccs.mean(axis=1).tolist(),
                'std': mfccs.std(axis=1).tolist()
            }
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
            features['zero_crossing_rate'] = {
                'mean': float(np.mean(zcr)),
                'std': float(np.std(zcr))
            }
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data)
            features['chroma'] = {
                'mean': chroma.mean(axis=1).tolist(),
                'std': chroma.std(axis=1).tolist()
            }
            
        except Exception as e:
            self.logger.warning(f"Feature extraction partially failed: {e}")
        
        return features
    
    async def _extract_audio_metadata(self, audio_data: np.ndarray, request: ExtractionRequest) -> Dict[str, Any]:
        """Extract audio metadata"""
        
        metadata = {}
        
        try:
            # Basic properties
            metadata['sample_rate'] = 22050  # Default librosa sample rate
            metadata['channels'] = 1 if audio_data.ndim == 1 else audio_data.shape[0]
            metadata['bit_depth'] = 32  # Float32 from librosa
            metadata['format'] = 'numpy_array'
            
            # File info if available
            if request.source_path:
                path = Path(request.source_path)
                metadata['filename'] = path.name
                metadata['extension'] = path.suffix.lower()
                
                if path.exists():
                    stat = path.stat()
                    metadata['file_size'] = stat.st_size
                    metadata['created_at'] = datetime.fromtimestamp(stat.st_ctime).isoformat()
                    metadata['modified_at'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            # Content analysis
            metadata['silence_ratio'] = float(np.sum(np.abs(audio_data) < 0.01) / len(audio_data))
            metadata['dynamic_range'] = float(np.max(audio_data) - np.min(audio_data))
            
        except Exception as e:
            self.logger.warning(f"Metadata extraction failed: {e}")
        
        return metadata
    
    async def _calculate_audio_quality(self, audio_data: np.ndarray) -> float:
        """Calculate audio quality score"""



        
        try:
            quality_factors = []
            
            # Dynamic range score
            dynamic_range = np.max(audio_data) - np.min(audio_data)
            quality_factors.append(min(dynamic_range / 2.0, 1.0))
            
            # SNR estimation
            signal_power = np.mean(audio_data**2)
            noise_floor = np.percentile(np.abs(audio_data), 10)**2
            snr = 10 * np.log10(signal_power / max(noise_floor, 1e-10))
            quality_factors.append(min(snr / 30.0, 1.0))
            
            # Clipping detection
            clipping_ratio = np.sum(np.abs(audio_data) > 0.98) / len(audio_data)
            quality_factors.append(1.0 - clipping_ratio)
            
            return float(np.mean(quality_factors))
            
        except Exception as e:
            self.logger.warning(f"Quality calculation failed: {e}")
            return 0.5


class VideoContentExtractor(BaseExtractor):
    """Industrial-grade video content extractor with AI recognition and fingerprinting"""
    
    def __init__(self):
        super().__init__("VideoContentExtractor")
        self.supported_formats = {
            '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', 
            '.m4v', '.3gp', '.ogv', '.ts', '.mts'
        }
        
        self.ai_models = {}
        self.object_detector = None
        self.face_detector = None
        
        if not HAS_VIDEO:
            self.logger.warning("Video processing libraries not available")
            
        self._initialize_video_models()
    
    def _initialize_video_models(self):
        """Initialize video AI models"""



        try:
            if HAS_VIDEO:
                # Initialize object detection model
                if torch.cuda.is_available():
                    self.device = 'cuda'
                else:
                    self.device = 'cpu'
                
                # Load pre-trained ResNet for feature extraction
                self.feature_extractor = resnet50(pretrained=True)
                self.feature_extractor.eval()
                
                # Initialize transforms
                self.transform = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                       std=[0.229, 0.224, 0.225])
                ])
                
                self.logger.info("Video AI models initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize video models: {e}")
    
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request contains video content"""
        if request.content_type == ContentType.VIDEO:
            return True
            
        # Check file extension
        if request.url:
            path = Path(urlparse(request.url).path)
            return path.suffix.lower() in self.supported_formats
            
        # Check MIME type
        if request.content and hasattr(request.content, 'content_type'):
            return request.content.content_type.startswith('video/')
            
        return False
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract comprehensive video features and metadata"""
        start_time = datetime.now()
        
        try:
            # Load video data
            video_path = await self._prepare_video_file(request)
            
            if not video_path or not Path(video_path).exists():
                return ExtractionResult(
                    extractor_name=self.name,
                    status=ExtractionStatus.FAILED,
                    error="Failed to load video data"
                )
            
            # Extract basic video metadata
            metadata = await self._extract_video_metadata(video_path)
            
            # Extract video features
            video_features = await self._extract_video_features(video_path)
            
            # AI-based content analysis
            ai_analysis = await self._ai_video_analysis(video_path)
            
            # Generate video fingerprints
            fingerprints = await self._generate_video_fingerprints(video_path)
            
            # Audio extraction from video
            audio_analysis = await self._extract_audio_from_video(video_path)
            
            # Quality assessment
            quality_metrics = await self._assess_video_quality(video_path)
            
            # Monetization potential
            monetization_score = await self._analyze_video_monetization_potential(
                video_features, ai_analysis, quality_metrics
            )
            
            # Combine all results
            metadata.ai_features.update({
                'video_features': video_features.__dict__,
                'ai_analysis': ai_analysis,
                'fingerprints': fingerprints,
                'audio_analysis': audio_analysis,
                'quality_metrics': quality_metrics,
                'monetization_score': monetization_score
            })
            
            extraction_time = (datetime.now() - start_time).total_seconds()
            metadata.extraction_time = extraction_time
            
            # Cleanup temporary file if created
            if video_path.startswith('/tmp/'):
                try:
                    Path(video_path).unlink()
                except:
                    pass
            
            return ExtractionResult(
                extractor_name=self.name,
                status=ExtractionStatus.SUCCESS,
                content_type=ContentType.VIDEO,
                metadata=metadata,
                data={
                    'video_features': video_features,
                    'ai_analysis': ai_analysis,
                    'fingerprints': fingerprints,
                    'quality_metrics': quality_metrics
                },
                processing_time=extraction_time
            )
            
        except Exception as e:
            self.logger.error(f"Video extraction failed: {e}")
            return ExtractionResult(
                extractor_name=self.name,
                status=ExtractionStatus.FAILED,
                error=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _prepare_video_file(self, request: ExtractionRequest) -> Optional[str]:
        """Prepare video file for processing"""



        try:
            if request.file_path and Path(request.file_path).exists():
                return request.file_path
                
            elif request.url:
                # Download video file
                async with aiohttp.ClientSession() as session:
                    async with session.get(request.url) as response:
                        if response.status == 200:
                            # Create temporary file
                            import tempfile
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                                async for chunk in response.content.iter_chunked(8192):
                                    temp_file.write(chunk)
                                return temp_file.name
                                
            elif request.content:
                # Save binary content to temporary file
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                    temp_file.write(request.content)
                    return temp_file.name
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to prepare video file: {e}")
            return None
    
    async def _extract_video_metadata(self, video_path: str) -> ContentMetadata:
        """Extract basic video metadata"""



        try:
            # Use ffprobe to get metadata
            probe = ffmpeg.probe(video_path)
            video_stream = next((stream for stream in probe['streams'] 
                               if stream['codec_type'] == 'video'), None)
            
            if not video_stream:
                raise ValueError("No video stream found")
            
            # Extract basic information
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            duration = float(video_stream.get('duration', 0))
            fps = eval(video_stream.get('r_frame_rate', '0/1'))
            codec = video_stream.get('codec_name', 'unknown')
            
            # Calculate file size
            file_size = Path(video_path).stat().st_size
            
            # Calculate content hash
            with open(video_path, 'rb') as f:
                content_sample = f.read(min(1024*1024, file_size))  # First 1MB
                content_hash = hashlib.sha256(content_sample).hexdigest()
            
            metadata = ContentMetadata(
                file_size=file_size,
                mime_type="video/mp4",
                duration=duration,
                dimensions=(width, height),
                content_hash=content_hash,
                created_at=datetime.now(),
                ai_features={
                    'codec': codec,
                    'fps': fps,
                    'aspect_ratio': width / height if height > 0 else 0
                }
            )
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Video metadata extraction failed: {e}")
            return ContentMetadata()
    
    async def _extract_video_features(self, video_path: str) -> VideoFeatures:
        """Extract comprehensive video features"""
        features = VideoFeatures()
        
        try:
            # Open video with OpenCV
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                self.logger.error("Failed to open video file")
                return features
            
            # Basic video properties
            features.frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            features.fps = cap.get(cv2.CAP_PROP_FPS)
            features.resolution = (
                int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            )
            features.aspect_ratio = features.resolution[0] / features.resolution[1] if features.resolution[1] > 0 else 0
            
            # Extract keyframes and analyze
            await self._extract_keyframes(cap, features)
            
            # Analyze dominant colors
            await self._analyze_dominant_colors(cap, features)
            
            # Detect scene changes
            await self._detect_scene_changes(cap, features)
            
            cap.release()
            
        except Exception as e:
            self.logger.error(f"Video feature extraction failed: {e}")
            
        return features
    
    async def _extract_keyframes(self, cap, features: VideoFeatures):
        """Extract and analyze keyframes"""



        try:
            frame_interval = max(1, int(features.fps * 5))  # Every 5 seconds
            keyframes = []
            
            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    # Resize frame for processing
                    frame_resized = cv2.resize(frame, (224, 224))
                    keyframes.append(frame_resized)
                    
                    if len(keyframes) >= 10:  # Limit to 10 keyframes
                        break
                
                frame_count += 1
            
            features.keyframes = keyframes
            
        except Exception as e:
            self.logger.error(f"Keyframe extraction failed: {e}")
    
    async def _analyze_dominant_colors(self, cap, features: VideoFeatures):
        """Analyze dominant colors in video"""



        try:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
            
            color_samples = []
            frame_interval = max(1, int(features.fps * 10))  # Every 10 seconds
            
            frame_count = 0
            while cap.isOpened() and len(color_samples) < 5:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    # Convert to RGB and analyze colors
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_small = cv2.resize(frame_rgb, (50, 50))
                    
                    # Get dominant colors using k-means
                    pixels = frame_small.reshape(-1, 3)
                    from sklearn.cluster import KMeans
                    
                    kmeans = KMeans(n_clusters=3, random_state=42)
                    kmeans.fit(pixels)
                    colors = kmeans.cluster_centers_.astype(int)
                    
                    color_samples.extend([tuple(color) for color in colors])
                
                frame_count += 1
            
            # Get most common colors
            from collections import Counter
            color_counts = Counter(color_samples)
            features.dominant_colors = [color for color, _ in color_counts.most_common(5)]
            
        except Exception as e:
            self.logger.error(f"Color analysis failed: {e}")
    
    async def _detect_scene_changes(self, cap, features: VideoFeatures):
        """Detect scene changes in video"""



        try:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
            
            prev_frame = None
            scene_changes = []
            frame_count = 0
            
            while cap.isOpened() and len(scene_changes) < 20:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to grayscale for comparison
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, (100, 100))
                
                if prev_frame is not None:
                    # Calculate frame difference
                    diff = cv2.absdiff(prev_frame, gray)
                    diff_score = np.mean(diff)
                    
                    # Threshold for scene change detection
                    if diff_score > 30:  # Adjust threshold as needed
                        timestamp = frame_count / features.fps
                        scene_changes.append(timestamp)
                
                prev_frame = gray
                frame_count += 1
            
            features.scene_changes = scene_changes
            
        except Exception as e:
            self.logger.error(f"Scene change detection failed: {e}")
    
    async def _ai_video_analysis(self, video_path: str) -> Dict[str, Any]:
        """AI-based video content analysis"""
        analysis = {
            'object_detection': [],
            'face_detection': [],
            'text_recognition': [],
            'content_classification': {},
            'visual_similarity_hash': '',
            'scene_understanding': {},
            'content_category': 'unknown'
        }
        
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return analysis
            
            # Analyze a few sample frames
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            sample_frames = []
            for i in range(min(5, frame_count)):
                frame_pos = i * (frame_count // 5) if frame_count > 5 else i
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()
                if ret:
                    sample_frames.append(frame)
            
            cap.release()
            
            # Analyze each sample frame
            for idx, frame in enumerate(sample_frames):
                frame_analysis = await self._analyze_frame(frame)
                
                # Aggregate results
                if frame_analysis['objects']:
                    analysis['object_detection'].extend(frame_analysis['objects'])
                if frame_analysis['faces']:
                    analysis['face_detection'].extend(frame_analysis['faces'])
                if frame_analysis['text']:
                    analysis['text_recognition'].extend(frame_analysis['text'])
            
            # Content categorization based on detected objects
            analysis['content_category'] = self._categorize_video_content(analysis)
            
            # Generate visual similarity hash
            analysis['visual_similarity_hash'] = await self._generate_visual_hash(sample_frames)
            
        except Exception as e:
            self.logger.error(f"AI video analysis failed: {e}")
            
        return analysis
    
    async def _analyze_frame(self, frame) -> Dict[str, Any]:
        """Analyze individual frame for objects, faces, text"""
        frame_analysis = {
            'objects': [],
            'faces': [],
            'text': []
        }
        
        try:
            # Face detection using face_recognition
            if HAS_VIDEO:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame)
                
                for top, right, bottom, left in face_locations:
                    frame_analysis['faces'].append({
                        'bbox': [left, top, right, bottom],
                        'confidence': 0.8  # face_recognition doesn't provide confidence
                    })
            
            # Text detection using OCR (basic implementation)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Simple text detection based on contours
            # This is a basic implementation - could be enhanced with Tesseract OCR
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 20 and h > 10:  # Filter small contours
                    aspect_ratio = w / h
                    if 2 < aspect_ratio < 10:  # Text-like aspect ratio
                        frame_analysis['text'].append({
                            'bbox': [x, y, x+w, y+h],
                            'text': 'detected_text'  # Placeholder
                        })
            
        except Exception as e:
            self.logger.error(f"Frame analysis failed: {e}")
            
        return frame_analysis
    
    def _categorize_video_content(self, analysis: Dict[str, Any]) -> str:
        """Categorize video content based on analysis"""



        try:
            # Simple categorization logic
            if analysis['face_detection']:
                if len(analysis['face_detection']) > 5:
                    return 'social_content'
                else:
                    return 'personal_content'
            elif analysis['text_recognition']:
                return 'educational_content'
            elif analysis['object_detection']:
                return 'general_content'
            else:
                return 'unknown'
                
        except Exception as e:
            self.logger.error(f"Content categorization failed: {e}")
            return 'unknown'
    
    async def _generate_visual_hash(self, frames: List[np.ndarray]) -> str:
        """Generate visual similarity hash from frames"""



        try:
            if not frames:
                return ""
            
            # Combine features from all frames
            combined_features = []
            
            for frame in frames:
                # Resize and convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                resized = cv2.resize(gray, (32, 32))
                
                # Calculate histogram
                hist = cv2.calcHist([resized], [0], None, [256], [0, 256])
                hist_normalized = hist.flatten() / (hist.sum() + 1e-10)
                
                combined_features.extend(hist_normalized[:32])  # Take first 32 values
            
            # Create hash from combined features
            features_array = np.array(combined_features)
            binary_hash = ''.join('1' if f > np.median(features_array) else '0' for f in features_array)
            
            return hashlib.md5(binary_hash.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Visual hash generation failed: {e}")
            return ""
    
    async def _generate_video_fingerprints(self, video_path: str) -> Dict[str, Any]:
        """Generate multiple types of video fingerprints"""
        fingerprints = {}
        
        try:
            # Frame-based fingerprint
            frame_fingerprint = await self._generate_frame_fingerprint(video_path)
            fingerprints['frame_fingerprint'] = frame_fingerprint
            
            # Motion-based fingerprint
            motion_fingerprint = await self._generate_motion_fingerprint(video_path)
            fingerprints['motion_fingerprint'] = motion_fingerprint
            
            # Color-based fingerprint
            color_fingerprint = await self._generate_color_fingerprint(video_path)
            fingerprints['color_fingerprint'] = color_fingerprint
            
        except Exception as e:
            self.logger.error(f"Video fingerprint generation failed: {e}")
            
        return fingerprints
    
    async def _generate_frame_fingerprint(self, video_path: str) -> str:
        """Generate fingerprint based on frame characteristics"""



        try:
            cap = cv2.VideoCapture(video_path)
            frame_hashes = []
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_interval = max(1, frame_count // 20)  # Sample 20 frames
            
            for i in range(0, frame_count, sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    # Convert to grayscale and resize
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    resized = cv2.resize(gray, (16, 16))
                    
                    # Calculate frame hash
                    frame_hash = hashlib.md5(resized.tobytes()).hexdigest()[:8]
                    frame_hashes.append(frame_hash)
            
            cap.release()
            
            # Combine frame hashes
            combined_hash = ''.join(frame_hashes)
            return hashlib.sha256(combined_hash.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Frame fingerprint generation failed: {e}")
            return ""
    
    async def _generate_motion_fingerprint(self, video_path: str) -> str:
        """Generate fingerprint based on motion patterns"""



        try:
            cap = cv2.VideoCapture(video_path)
            motion_vectors = []
            
            prev_frame = None
            while cap.isOpened() and len(motion_vectors) < 50:
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, (64, 64))
                
                if prev_frame is not None:
                    # Calculate optical flow
                    flow = cv2.calcOpticalFlowPyrLK(
                        prev_frame, gray, 
                        corners=cv2.goodFeaturesToTrack(prev_frame, 100, 0.01, 10),
                        nextPts=None
                    )[0]
                    
                    if flow is not None and len(flow) > 0:
                        # Calculate motion magnitude
                        motion_mag = np.mean(np.linalg.norm(flow - np.mean(flow, axis=0), axis=1))
                        motion_vectors.append(motion_mag)
                
                prev_frame = gray
            
            cap.release()
            
            if motion_vectors:
                # Quantize motion patterns
                motion_pattern = np.array(motion_vectors)
                quantized = np.digitize(motion_pattern, np.linspace(motion_pattern.min(), motion_pattern.max(), 8))
                pattern_str = ''.join(str(q) for q in quantized)
                return hashlib.md5(pattern_str.encode()).hexdigest()
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Motion fingerprint generation failed: {e}")
            return ""
    
    async def _generate_color_fingerprint(self, video_path: str) -> str:
        """Generate fingerprint based on color characteristics"""



        try:
            cap = cv2.VideoCapture(video_path)
            color_histograms = []
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_interval = max(1, frame_count // 10)  # Sample 10 frames
            
            for i in range(0, frame_count, sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    # Calculate color histogram
                    hist_b = cv2.calcHist([frame], [0], None, [32], [0, 256])
                    hist_g = cv2.calcHist([frame], [1], None, [32], [0, 256])
                    hist_r = cv2.calcHist([frame], [2], None, [32], [0, 256])
                    
                    combined_hist = np.concatenate([hist_b, hist_g, hist_r]).flatten()
                    color_histograms.append(combined_hist)
            
            cap.release()
            
            if color_histograms:
                # Average histograms and create fingerprint
                avg_histogram = np.mean(color_histograms, axis=0)
                normalized_hist = avg_histogram / (np.sum(avg_histogram) + 1e-10)
                
                # Quantize to create binary fingerprint
                binary_pattern = ''.join('1' if h > np.median(normalized_hist) else '0' 
                                       for h in normalized_hist)
                return hashlib.md5(binary_pattern.encode()).hexdigest()
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Color fingerprint generation failed: {e}")
            return ""
    
    async def _extract_audio_from_video(self, video_path: str) -> Dict[str, Any]:
        """Extract and analyze audio track from video"""
        audio_analysis = {}
        
        try:
            # Extract audio using ffmpeg
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio_path = temp_audio.name
            
            # Extract audio track
            stream = ffmpeg.input(video_path)
            audio = stream.audio
            out = ffmpeg.output(audio, temp_audio_path, acodec='pcm_s16le', ac=1, ar='22050')
            ffmpeg.run(out, quiet=True, overwrite_output=True)
            
            # Use AudioContentExtractor to analyze extracted audio
            if Path(temp_audio_path).exists():
                from .content_extractors import AudioContentExtractor
                audio_extractor = AudioContentExtractor()
                
                audio_request = ExtractionRequest(
                    request_id=f"audio_from_video_{int(datetime.now().timestamp())}",
                    content_type=ContentType.AUDIO,
                    file_path=temp_audio_path
                )
                
                audio_result = await audio_extractor.extract(audio_request)
                
                if audio_result.status == ExtractionStatus.SUCCESS:
                    audio_analysis = audio_result.data
                
                # Cleanup temporary audio file
                Path(temp_audio_path).unlink()
            
        except Exception as e:
            self.logger.error(f"Audio extraction from video failed: {e}")
            
        return audio_analysis
    
    async def _assess_video_quality(self, video_path: str) -> Dict[str, float]:
        """Assess video quality metrics"""
        quality_metrics = {
            'resolution_score': 0.0,
            'bitrate_score': 0.0,
            'frame_rate_score': 0.0,
            'stability_score': 0.0,
            'overall_quality': 0.0
        }
        
        try:
            # Get video properties
            probe = ffmpeg.probe(video_path)
            video_stream = next((stream for stream in probe['streams'] 
                               if stream['codec_type'] == 'video'), None)
            
            if video_stream:
                width = int(video_stream.get('width', 0))
                height = int(video_stream.get('height', 0))
                fps = eval(video_stream.get('r_frame_rate', '0/1'))
                bitrate = int(video_stream.get('bit_rate', 0))
                
                # Resolution score (normalized to 4K)
                resolution_pixels = width * height
                quality_metrics['resolution_score'] = min(100, (resolution_pixels / (3840 * 2160)) * 100)
                
                # Frame rate score (optimal around 30fps)
                if 24 <= fps <= 30:
                    quality_metrics['frame_rate_score'] = 100
                elif 30 < fps <= 60:
                    quality_metrics['frame_rate_score'] = 90
                else:
                    quality_metrics['frame_rate_score'] = max(0, 60)
                
                # Bitrate score (relative to resolution)
                expected_bitrate = resolution_pixels * 0.1  # Rough estimate
                if bitrate > 0:
                    bitrate_ratio = bitrate / expected_bitrate
                    quality_metrics['bitrate_score'] = min(100, bitrate_ratio * 50)
                
                # Overall quality
                quality_metrics['overall_quality'] = np.mean([
                    quality_metrics['resolution_score'],
                    quality_metrics['frame_rate_score'],
                    quality_metrics['bitrate_score']
                ])
            
        except Exception as e:
            self.logger.error(f"Video quality assessment failed: {e}")
            
        return quality_metrics
    
    async def _analyze_video_monetization_potential(
        self, video_features: VideoFeatures, ai_analysis: Dict[str, Any], 
        quality_metrics: Dict[str, float]
    ) -> float:
        """Analyze monetization potential for video content"""



        
        try:
            score = 0.0
            
            # Quality-based scoring (40% weight)
            quality_score = quality_metrics.get('overall_quality', 0)
            score += quality_score * 0.4
            
            # Content-based scoring (40% weight)
            content_category = ai_analysis.get('content_category', 'unknown')
            content_scores = {
                'educational_content': 35,
                'social_content': 30,
                'personal_content': 25,
                'general_content': 20,
                'unknown': 10
            }
            score += content_scores.get(content_category, 10)
            
            # Engagement potential based on AI features (20% weight)
            if ai_analysis.get('face_detection'):
                score += 10  # Human presence increases engagement
            if ai_analysis.get('text_recognition'):
                score += 5   # Text content can be educational
            if len(video_features.scene_changes) > 2:
                score += 5   # Dynamic content
            
            return min(100, max(0, score))
            
        except Exception as e:
            self.logger.error(f"Video monetization analysis failed: {e}")
            return 0.0
            # Get video source path
            video_path = await self._prepare_video_source(request)
            if not video_path:
                result.status = ExtractionStatus.FAILED
                result.errors.append("Failed to prepare video source")
                return result
            
            # Extract video features
            features = await self._extract_video_features(video_path)
            result.extracted_data.update(features)
            
            # Extract metadata
            metadata = await self._extract_video_metadata(video_path)
            result.metadata.update(metadata)
            
            # Calculate quality score
            quality_score = await self._calculate_video_quality(video_path)
            result.quality_score = quality_score
            
            # Generate content hash
            result.content_hash = await self._generate_video_hash(video_path)
            
            if Path(video_path).exists():
                result.file_size = Path(video_path).stat().st_size
            
            result.status = ExtractionStatus.COMPLETED
            self.logger.info(f"Video extraction completed for {request.request_id}")
            
        except Exception as e:
            self.logger.error(f"Video extraction failed: {e}")
            result.status = ExtractionStatus.FAILED
            result.errors.append(str(e))
        
        finally:
            result.extraction_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_stats(result.status == ExtractionStatus.COMPLETED, result.extraction_time)
        
        return result
    
    async def _prepare_video_source(self, request: ExtractionRequest) -> Optional[str]:
        """Prepare video source for processing"""
        
        if request.source_path:
            return request.source_path
        
        elif request.source_url:
            # Download video temporarily
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(request.source_url) as response:
                        if response.status == 200:
                            temp_path = f"/tmp/video_{request.request_id}.mp4"
                            async with aiofiles.open(temp_path, 'wb') as f:
                                async for chunk in response.content.iter_chunked(8192):
                                    await f.write(chunk)
                            return temp_path
            except Exception as e:
                self.logger.error(f"Failed to download video: {e}")
        
        elif request.source_data:
            # Save binary data to temporary file
            try:
                temp_path = f"/tmp/video_{request.request_id}.mp4"
                async with aiofiles.open(temp_path, 'wb') as f:
                    await f.write(request.source_data)
                return temp_path
            except Exception as e:
                self.logger.error(f"Failed to save video data: {e}")
        
        return None
    
    async def _extract_video_features(self, video_path: str) -> Dict[str, Any]:
        """Extract comprehensive video features"""
        
        features = {}
        
        try:
            # Open video file
            cap = cv2.VideoCapture(video_path)
            
            # Basic properties
            features['frame_count'] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            features['fps'] = cap.get(cv2.CAP_PROP_FPS)
            features['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            features['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            features['duration'] = features['frame_count'] / features['fps'] if features['fps'] > 0 else 0
            
            # Analyze frames for additional features
            frame_features = []
            frame_count = 0
            sample_interval = max(1, features['frame_count'] // 30)  # Sample 30 frames max
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % sample_interval == 0:
                    # Analyze frame
                    frame_analysis = self._analyze_frame(frame)
                    frame_features.append(frame_analysis)
                
                frame_count += 1
                
                # Limit analysis to prevent timeout
                if len(frame_features) >= 30:
                    break
            
            cap.release()
            
            # Aggregate frame features
            if frame_features:
                features['brightness'] = {
                    'mean': np.mean([f['brightness'] for f in frame_features]),
                    'std': np.std([f['brightness'] for f in frame_features])
                }
                features['contrast'] = {
                    'mean': np.mean([f['contrast'] for f in frame_features]),
                    'std': np.std([f['contrast'] for f in frame_features])
                }
                features['motion'] = {
                    'mean': np.mean([f.get('motion', 0) for f in frame_features]),
                    'std': np.std([f.get('motion', 0) for f in frame_features])
                }
            
        except Exception as e:
            self.logger.warning(f"Video feature extraction failed: {e}")
        
        return features
    
    def _analyze_frame(self, frame: np.ndarray) -> Dict[str, float]:
        """Analyze individual video frame"""
        
        analysis = {}
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Brightness (mean intensity)
            analysis['brightness'] = float(np.mean(gray))
            
            # Contrast (standard deviation)
            analysis['contrast'] = float(np.std(gray))
            
            # Edge density (complexity)
            edges = cv2.Canny(gray, 50, 150)
            analysis['edge_density'] = float(np.sum(edges > 0) / edges.size)
            
        except Exception as e:
            self.logger.warning(f"Frame analysis failed: {e}")
        
        return analysis
    
    async def _extract_video_metadata(self, video_path: str) -> Dict[str, Any]:
        """Extract video metadata using ffmpeg"""
        
        metadata = {}
        
        try:
            # Use ffprobe to get detailed metadata
            probe = ffmpeg.probe(video_path)
            
            # Video stream info
            video_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'video'), 
                None
            )
            
            if video_stream:
                metadata['codec'] = video_stream.get('codec_name')
                metadata['bitrate'] = int(video_stream.get('bit_rate', 0))
                metadata['pixel_format'] = video_stream.get('pix_fmt')
                metadata['profile'] = video_stream.get('profile')
                metadata['level'] = video_stream.get('level')
            
            # Audio stream info
            audio_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), 
                None
            )
            
            if audio_stream:
                metadata['audio_codec'] = audio_stream.get('codec_name')
                metadata['audio_bitrate'] = int(audio_stream.get('bit_rate', 0))
                metadata['sample_rate'] = int(audio_stream.get('sample_rate', 0))
                metadata['channels'] = int(audio_stream.get('channels', 0))
            
            # Format info
            format_info = probe.get('format', {})
            metadata['format'] = format_info.get('format_name')
            metadata['size'] = int(format_info.get('size', 0))
            
        except Exception as e:
            self.logger.warning(f"Video metadata extraction failed: {e}")
        
        return metadata
    
    async def _calculate_video_quality(self, video_path: str) -> float:
        """Calculate video quality score"""



        
        try:
            quality_factors = []
            
            # Resolution score
            cap = cv2.VideoCapture(video_path)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            
            resolution_score = min((width * height) / (1920 * 1080), 1.0)
            quality_factors.append(resolution_score)
            
            # Bitrate score (if available)
            try:
                probe = ffmpeg.probe(video_path)
                video_stream = next(
                    (stream for stream in probe['streams'] if stream['codec_type'] == 'video'), 
                    None
                )
                if video_stream and 'bit_rate' in video_stream:
                    bitrate = int(video_stream['bit_rate'])
                    bitrate_score = min(bitrate / 5000000, 1.0)  # 5Mbps as reference
                    quality_factors.append(bitrate_score)
            except:
                pass
            
            return float(np.mean(quality_factors)) if quality_factors else 0.5
            
        except Exception as e:
            self.logger.warning(f"Video quality calculation failed: {e}")
            return 0.5
    
    async def _generate_video_hash(self, video_path: str) -> str:
        """Generate perceptual hash for video"""



        
        try:
            # Sample frames and create composite hash
            cap = cv2.VideoCapture(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Sample 5 frames evenly distributed
            sample_indices = [i * frame_count // 6 for i in range(1, 6)]
            frame_hashes = []
            
            for idx in sample_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    # Convert to grayscale and resize
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    resized = cv2.resize(gray, (8, 8))
                    frame_hash = hashlib.md5(resized.tobytes()).hexdigest()
                    frame_hashes.append(frame_hash)
            
            cap.release()
            
            # Combine frame hashes
            combined_hash = hashlib.sha256(''.join(frame_hashes).encode()).hexdigest()
            return combined_hash
            
        except Exception as e:
            self.logger.warning(f"Video hash generation failed: {e}")
            return hashlib.sha256(video_path.encode()).hexdigest()


class ImageContentExtractor(BaseExtractor):
    """Advanced image content extractor"""
    
    def __init__(self):
        super().__init__("ImageContentExtractor")
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        
        if not HAS_IMAGE:
            self.logger.warning("Image processing libraries not available")
    
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request contains image content"""
        
        if request.content_type != ContentType.IMAGE:
            return False
        
        if not HAS_IMAGE:
            return False
        
        # Check file extension
        if request.source_path:
            path = Path(request.source_path)
            return path.suffix.lower() in self.supported_formats
        
        if request.source_url:
            parsed = urlparse(request.source_url)
            path = Path(parsed.path)
            return path.suffix.lower() in self.supported_formats
        
        return True
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract image content and metadata"""
        
        start_time = datetime.utcnow()
        result = ExtractionResult(
            request_id=request.request_id,
            status=ExtractionStatus.RUNNING
        )
        
        try:
            # Load image
            image = await self._load_image(request)
            if not image:
                result.status = ExtractionStatus.FAILED
                result.errors.append("Failed to load image")
                return result
            
            # Extract image features
            features = await self._extract_image_features(image)
            result.extracted_data.update(features)
            
            # Extract metadata
            metadata = await self._extract_image_metadata(image, request)
            result.metadata.update(metadata)
            
            # Calculate quality score
            quality_score = await self._calculate_image_quality(image)
            result.quality_score = quality_score
            
            # Generate perceptual hash
            result.content_hash = await self._generate_image_hash(image)
            
            # Get file size
            if hasattr(image, 'fp') and image.fp:
                try:
                    image.fp.seek(0, 2)  # Seek to end
                    result.file_size = image.fp.tell()
                    image.fp.seek(0)  # Reset
                except:
                    pass
            
            result.status = ExtractionStatus.COMPLETED
            self.logger.info(f"Image extraction completed for {request.request_id}")
            
        except Exception as e:
            self.logger.error(f"Image extraction failed: {e}")
            result.status = ExtractionStatus.FAILED
            result.errors.append(str(e))
        
        finally:
            result.extraction_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_stats(result.status == ExtractionStatus.COMPLETED, result.extraction_time)
        
        return result
    
    async def _load_image(self, request: ExtractionRequest) -> Optional[Image.Image]:
        """Load image from various sources"""



        
        try:
            if request.source_data:
                # Load from binary data
                image_buffer = io.BytesIO(request.source_data)
                return Image.open(image_buffer)
            
            elif request.source_path:
                # Load from file path
                return Image.open(request.source_path)
            
            elif request.source_url:
                # Load from URL
                async with aiohttp.ClientSession() as session:
                    async with session.get(request.source_url) as response:
                        if response.status == 200:
                            data = await response.read()
                            image_buffer = io.BytesIO(data)
                            return Image.open(image_buffer)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to load image: {e}")
            return None
    
    async def _extract_image_features(self, image: Image.Image) -> Dict[str, Any]:
        """Extract comprehensive image features"""
        
        features = {}
        
        try:
            # Basic properties
            features['width'], features['height'] = image.size
            features['mode'] = image.mode
            features['format'] = image.format
            features['aspect_ratio'] = features['width'] / features['height']
            
            # Color analysis
            if image.mode == 'RGB' or image.mode == 'RGBA':
                # Convert to RGB if needed
                rgb_image = image.convert('RGB')
                
                # Color statistics
                stat = ImageStat.Stat(rgb_image)
                features['color_stats'] = {
                    'mean': stat.mean,
                    'median': stat.median,
                    'stddev': stat.stddev
                }
                
                # Dominant colors
                colors = rgb_image.getcolors(maxcolors=256*256*256)
                if colors:
                    # Sort by frequency
                    colors.sort(key=lambda x: x[0], reverse=True)
                    dominant_colors = []
                    for count, color in colors[:5]:  # Top 5 colors
                        dominant_colors.append({
                            'color': color,
                            'count': count,
                            'percentage': count / (features['width'] * features['height'])
                        })
                    features['dominant_colors'] = dominant_colors
            
            # Brightness and contrast
            grayscale = image.convert('L')
            stat = ImageStat.Stat(grayscale)
            features['brightness'] = stat.mean[0]
            features['contrast'] = stat.stddev[0]
            
            # Edge detection for complexity
            edges = grayscale.filter(ImageFilter.FIND_EDGES)
            edge_stat = ImageStat.Stat(edges)
            features['edge_density'] = edge_stat.mean[0]
            
            # Texture analysis (simplified)
            features['texture_variance'] = stat.stddev[0]
            
        except Exception as e:
            self.logger.warning(f"Image feature extraction failed: {e}")
        
        return features
    
    async def _extract_image_metadata(self, image: Image.Image, request: ExtractionRequest) -> Dict[str, Any]:
        """Extract image metadata including EXIF"""
        
        metadata = {}
        
        try:
            # Basic metadata
            metadata['format'] = image.format
            metadata['mode'] = image.mode
            metadata['size'] = image.size
            
            # EXIF data
            exif_data = {}
            if hasattr(image, '_getexif') and image._getexif():
                exif = image._getexif()
                for tag_id, value in exif.items():
                    try:
                        tag = Image.ExifTags.TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
                    except:
                        pass
            
            if exif_data:
                metadata['exif'] = exif_data
                
                # Extract useful EXIF fields
                if 'DateTime' in exif_data:
                    metadata['taken_at'] = exif_data['DateTime']
                if 'Make' in exif_data:
                    metadata['camera_make'] = exif_data['Make']
                if 'Model' in exif_data:
                    metadata['camera_model'] = exif_data['Model']
            
            # File info if available
            if request.source_path:
                path = Path(request.source_path)
                metadata['filename'] = path.name
                metadata['extension'] = path.suffix.lower()
                
                if path.exists():
                    stat = path.stat()
                    metadata['file_size'] = stat.st_size
                    metadata['created_at'] = datetime.fromtimestamp(stat.st_ctime).isoformat()
                    metadata['modified_at'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
        except Exception as e:
            self.logger.warning(f"Image metadata extraction failed: {e}")
        
        return metadata
    
    async def _calculate_image_quality(self, image: Image.Image) -> float:
        """Calculate image quality score"""



        
        try:
            quality_factors = []
            
            # Resolution score
            width, height = image.size
            resolution_score = min((width * height) / (1920 * 1080), 1.0)
            quality_factors.append(resolution_score)
            
            # Sharpness estimation
            grayscale = image.convert('L')
            edges = grayscale.filter(ImageFilter.FIND_EDGES)
            edge_stat = ImageStat.Stat(edges)
            sharpness_score = min(edge_stat.mean[0] / 50.0, 1.0)
            quality_factors.append(sharpness_score)
            
            # Color depth score
            if image.mode in ['RGB', 'RGBA']:
                quality_factors.append(1.0)
            elif image.mode == 'L':
                quality_factors.append(0.7)
            else:
                quality_factors.append(0.5)
            
            return float(np.mean(quality_factors))
            
        except Exception as e:
            self.logger.warning(f"Image quality calculation failed: {e}")
            return 0.5
    
    async def _generate_image_hash(self, image: Image.Image) -> str:
        """Generate perceptual hash for image"""



        
        try:
            # Use multiple hash algorithms for better accuracy
            phash = str(imagehash.phash(image))
            dhash = str(imagehash.dhash(image))
            whash = str(imagehash.whash(image))
            
            # Combine hashes
            combined = f"{phash}:{dhash}:{whash}"
            return hashlib.sha256(combined.encode()).hexdigest()
            
        except Exception as e:
            self.logger.warning(f"Image hash generation failed: {e}")
            # Fallback to simple hash
            image_bytes = image.tobytes()
            return hashlib.sha256(image_bytes).hexdigest()


class TextContentExtractor(BaseExtractor):
    """Advanced text content extractor"""
    
    def __init__(self):
        super().__init__("TextContentExtractor")
        
        if not HAS_TEXT:
            self.logger.warning("Text processing libraries not available")
    
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request contains text content"""



        return request.content_type == ContentType.TEXT
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract text content and metadata"""
        
        start_time = datetime.utcnow()
        result = ExtractionResult(
            request_id=request.request_id,
            status=ExtractionStatus.RUNNING
        )
        
        try:
            # Load text content
            text_content = await self._load_text_content(request)
            if not text_content:
                result.status = ExtractionStatus.FAILED
                result.errors.append("Failed to load text content")
                return result
            
            # Extract text features
            features = await self._extract_text_features(text_content)
            result.extracted_data.update(features)
            
            # Extract metadata
            metadata = await self._extract_text_metadata(text_content, request)
            result.metadata.update(metadata)
            
            # Calculate quality score
            quality_score = await self._calculate_text_quality(text_content)
            result.quality_score = quality_score
            
            # Generate content hash
            result.content_hash = hashlib.sha256(text_content.encode('utf-8')).hexdigest()
            result.file_size = len(text_content.encode('utf-8'))
            
            result.status = ExtractionStatus.COMPLETED
            self.logger.info(f"Text extraction completed for {request.request_id}")
            
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            result.status = ExtractionStatus.FAILED
            result.errors.append(str(e))
        
        finally:
            result.extraction_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_stats(result.status == ExtractionStatus.COMPLETED, result.extraction_time)
        
        return result
    
    async def _load_text_content(self, request: ExtractionRequest) -> Optional[str]:
        """Load text content from various sources"""



        
        try:
            if request.source_data:
                # Load from binary data
                return request.source_data.decode('utf-8')
            
            elif request.source_path:
                # Load from file path
                async with aiofiles.open(request.source_path, 'r', encoding='utf-8') as f:
                    return await f.read()
            
            elif request.source_url:
                # Load from URL
                async with aiohttp.ClientSession() as session:
                    async with session.get(request.source_url) as response:
                        if response.status == 200:
                            return await response.text()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to load text content: {e}")
            return None
    
    async def _extract_text_features(self, text_content: str) -> Dict[str, Any]:
        """Extract comprehensive text features"""
        
        features = {}
        
        try:
            # Basic statistics
            features['character_count'] = len(text_content)
            features['word_count'] = len(text_content.split())
            features['line_count'] = text_content.count('\n') + 1
            features['paragraph_count'] = len([p for p in text_content.split('\n\n') if p.strip()])
            
            # Readability scores (if textstat available)
            if HAS_TEXT:
                try:
                    features['flesch_reading_ease'] = flesch_reading_ease(text_content)
                    features['flesch_kincaid_grade'] = flesch_kincaid_grade(text_content)
                except:
                    pass
            
            # Language detection
            try:
                detected_lang = langdetect.detect(text_content)
                features['detected_language'] = detected_lang
                features['language_confidence'] = langdetect.detect_langs(text_content)[0].prob
            except:
                features['detected_language'] = 'unknown'
                features['language_confidence'] = 0.0
            
            # Text patterns
            import string
            features['punctuation_ratio'] = sum(1 for c in text_content if c in string.punctuation) / len(text_content)
            features['uppercase_ratio'] = sum(1 for c in text_content if c.isupper()) / len(text_content)
            features['digit_ratio'] = sum(1 for c in text_content if c.isdigit()) / len(text_content)
            
            # Sentence analysis
            sentences = [s.strip() for s in text_content.split('.') if s.strip()]
            if sentences:
                sentence_lengths = [len(s.split()) for s in sentences]
                features['sentence_count'] = len(sentences)
                features['average_sentence_length'] = np.mean(sentence_lengths)
                features['sentence_length_variance'] = np.var(sentence_lengths)
            
            # Word analysis
            words = text_content.split()
            if words:
                word_lengths = [len(w) for w in words]
                features['average_word_length'] = np.mean(word_lengths)
                features['word_length_variance'] = np.var(word_lengths)
                
                # Unique words ratio
                unique_words = set(words)
                features['unique_word_ratio'] = len(unique_words) / len(words)
            
        except Exception as e:
            self.logger.warning(f"Text feature extraction failed: {e}")
        
        return features
    
    async def _extract_text_metadata(self, text_content: str, request: ExtractionRequest) -> Dict[str, Any]:
        """Extract text metadata"""
        
        metadata = {}
        
        try:
            # Content type analysis
            metadata['encoding'] = 'utf-8'
            metadata['content_type'] = 'text/plain'
            
            # Structure analysis
            has_html = bool(re.search(r'<[^>]+>', text_content))
            has_markdown = bool(re.search(r'[#*`\[\]]', text_content))
            has_json = text_content.strip().startswith(('{', '['))
            
            if has_html:
                metadata['format'] = 'html'
            elif has_markdown:
                metadata['format'] = 'markdown'
            elif has_json:
                metadata['format'] = 'json'
            else:
                metadata['format'] = 'plain_text'
            
            # File info if available
            if request.source_path:
                path = Path(request.source_path)
                metadata['filename'] = path.name
                metadata['extension'] = path.suffix.lower()
                
                if path.exists():
                    stat = path.stat()
                    metadata['file_size'] = stat.st_size
                    metadata['created_at'] = datetime.fromtimestamp(stat.st_ctime).isoformat()
                    metadata['modified_at'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            # Content analysis
            metadata['has_urls'] = bool(re.search(r'https?://', text_content))
            metadata['has_emails'] = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text_content))
            metadata['has_phone_numbers'] = bool(re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text_content))
            
        except Exception as e:
            self.logger.warning(f"Text metadata extraction failed: {e}")
        
        return metadata
    
    async def _calculate_text_quality(self, text_content: str) -> float:
        """Calculate text quality score"""



        
        try:
            quality_factors = []
            
            # Length adequacy (not too short, not too long)
            length = len(text_content)
            if 100 <= length <= 10000:
                length_score = 1.0
            elif length < 100:
                length_score = length / 100.0
            else:
                length_score = max(0.5, 10000.0 / length)
            quality_factors.append(length_score)
            
            # Readability score
            if HAS_TEXT:
                try:
                    ease_score = flesch_reading_ease(text_content)
                    # Convert to 0-1 scale (30-100 is good range)
                    readability_score = max(0, min(1, (ease_score - 30) / 70))
                    quality_factors.append(readability_score)
                except:
                    quality_factors.append(0.5)
            
            # Structure score (balanced punctuation, etc.)
            import string
            punct_ratio = sum(1 for c in text_content if c in string.punctuation) / len(text_content)
            structure_score = 1.0 - abs(punct_ratio - 0.05)  # Target ~5% punctuation
            quality_factors.append(max(0, structure_score))
            
            return float(np.mean(quality_factors))
            
        except Exception as e:
            self.logger.warning(f"Text quality calculation failed: {e}")
            return 0.5


class MetadataExtractor(BaseExtractor):
    """Universal metadata extractor"""
    
    def __init__(self):
        super().__init__("MetadataExtractor")
    
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Can handle any request for metadata extraction"""



        return "metadata" in request.extraction_types
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract universal metadata"""
        
        start_time = datetime.utcnow()
        result = ExtractionResult(
            request_id=request.request_id,
            status=ExtractionStatus.RUNNING
        )
        
        try:
            metadata = {}
            
            # Source information
            if request.source_url:
                metadata['source_url'] = request.source_url
                parsed = urlparse(request.source_url)
                metadata['domain'] = parsed.netloc
                metadata['scheme'] = parsed.scheme
            
            if request.source_path:
                metadata['source_path'] = request.source_path
                path = Path(request.source_path)
                if path.exists():
                    stat = path.stat()
                    metadata['file_size'] = stat.st_size
                    metadata['created_at'] = datetime.fromtimestamp(stat.st_ctime).isoformat()
                    metadata['modified_at'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    metadata['mime_type'] = mimetypes.guess_type(request.source_path)[0]
            
            # Request metadata
            metadata['content_type'] = request.content_type.value
            metadata['platform'] = request.platform
            metadata['extraction_types'] = request.extraction_types
            metadata['user_id'] = request.user_id
            metadata['request_created_at'] = request.created_at.isoformat()
            
            result.extracted_data = metadata
            result.status = ExtractionStatus.COMPLETED
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {e}")
            result.status = ExtractionStatus.FAILED
            result.errors.append(str(e))
        
        finally:
            result.extraction_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_stats(result.status == ExtractionStatus.COMPLETED, result.extraction_time)
        
        return result


class ThumbnailExtractor(BaseExtractor):
    """Thumbnail and preview generation extractor"""
    
    def __init__(self):
        super().__init__("ThumbnailExtractor")
    
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Can handle image and video content for thumbnails"""



        return (request.content_type in [ContentType.IMAGE, ContentType.VIDEO] and
                "thumbnail" in request.extraction_types)
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract thumbnails and previews"""
        
        start_time = datetime.utcnow()
        result = ExtractionResult(
            request_id=request.request_id,
            status=ExtractionStatus.RUNNING
        )
        
        try:
            thumbnails = {}
            
            if request.content_type == ContentType.IMAGE and HAS_IMAGE:
                thumbnails.update(await self._generate_image_thumbnails(request))
            
            elif request.content_type == ContentType.VIDEO and HAS_VIDEO:
                thumbnails.update(await self._generate_video_thumbnails(request))
            
            result.extracted_data = thumbnails
            result.status = ExtractionStatus.COMPLETED
            
        except Exception as e:
            self.logger.error(f"Thumbnail extraction failed: {e}")
            result.status = ExtractionStatus.FAILED
            result.errors.append(str(e))
        
        finally:
            result.extraction_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_stats(result.status == ExtractionStatus.COMPLETED, result.extraction_time)
        
        return result
    
    async def _generate_image_thumbnails(self, request: ExtractionRequest) -> Dict[str, str]:
        """Generate image thumbnails in multiple sizes"""
        
        thumbnails = {}
        sizes = [(64, 64), (128, 128), (256, 256), (512, 512)]
        
        try:
            # Load original image
            if request.source_path:
                image = Image.open(request.source_path)
            elif request.source_url:
                async with aiohttp.ClientSession() as session:
                    async with session.get(request.source_url) as response:
                        if response.status == 200:
                            data = await response.read()
                            image = Image.open(io.BytesIO(data))
                        else:
                            return thumbnails
            elif request.source_data:
                image = Image.open(io.BytesIO(request.source_data))
            else:
                return thumbnails
            
            # Generate thumbnails
            for width, height in sizes:
                thumb = image.copy()
                thumb.thumbnail((width, height), Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                thumb.save(buffer, format='JPEG', quality=85)
                thumb_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                thumbnails[f'thumbnail_{width}x{height}'] = f'data:image/jpeg;base64,{thumb_b64}'
            
        except Exception as e:
            self.logger.error(f"Image thumbnail generation failed: {e}")
        
        return thumbnails
    
    async def _generate_video_thumbnails(self, request: ExtractionRequest) -> Dict[str, str]:
        """Generate video thumbnails from key frames"""
        
        thumbnails = {}
        
        try:
            # Prepare video source
            if request.source_path:
                video_path = request.source_path
            elif request.source_url:
                # Download temporarily
                async with aiohttp.ClientSession() as session:
                    async with session.get(request.source_url) as response:
                        if response.status == 200:
                            video_path = f'/tmp/video_{request.request_id}.mp4'
                            async with aiofiles.open(video_path, 'wb') as f:
                                async for chunk in response.content.iter_chunked(8192):
                                    await f.write(chunk)
                        else:
                            return thumbnails
            elif request.source_data:
                video_path = f'/tmp/video_{request.request_id}.mp4'
                async with aiofiles.open(video_path, 'wb') as f:
                    await f.write(request.source_data)
            else:
                return thumbnails
            
            # Extract frames
            cap = cv2.VideoCapture(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Generate thumbnails from different timestamps
            timestamps = [0.1, 0.3, 0.5, 0.7, 0.9]  # 10%, 30%, 50%, 70%, 90%
            
            for i, timestamp in enumerate(timestamps):
                frame_pos = int(frame_count * timestamp)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                
                ret, frame = cap.read()
                if ret:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame_rgb)
                    
                    # Create thumbnail
                    image.thumbnail((256, 256), Image.Resampling.LANCZOS)
                    
                    # Convert to base64
                    buffer = io.BytesIO()
                    image.save(buffer, format='JPEG', quality=85)
                    thumb_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    
                    thumbnails[f'thumbnail_frame_{i}'] = f'data:image/jpeg;base64,{thumb_b64}'
            
            cap.release()
            
            # Clean up temp file if created
            if request.source_url or request.source_data:
                try:
                    Path(video_path).unlink()
                except:
                    pass
            
        except Exception as e:
            self.logger.error(f"Video thumbnail generation failed: {e}")
        
        return thumbnails
