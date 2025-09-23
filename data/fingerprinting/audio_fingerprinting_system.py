#!/usr/bin/env python3
"""
Audio Fingerprinting System - Ainflue Data Fingerprinting Module
================================================================
Advanced audio fingerprinting system with ML-powered analysis,
chromaprint integration, and specialized audio content protection
for music creators on the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Data Fingerprinting
Version: 1.0 Enterprise Production
"""

import asyncio
import hashlib
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

# Core imports for audio processing
try:
    import librosa
    import chromaprint
    import scipy.signal
    from scipy.spatial.distance import cosine
    import torch
    import torchaudio
    from transformers import Wav2Vec2Processor, Wav2Vec2Model
except ImportError as e:
    logging.error(f"Required audio dependencies not installed: {e}")

# Ainflue core imports
from .multimodal_fingerprinting_engine import FingerprintResult, FingerprintConfig
from .vector_database_matching import VectorDatabaseManager
from .performance_analytics_engine import PerformanceAnalytics


class AudioFingerprintType(Enum):
    """Types of audio fingerprints supported."""
    CHROMAPRINT = "chromaprint"
    SPECTRAL = "spectral"
    MFCC = "mfcc"
    MEL_SPECTROGRAM = "mel_spectrogram"
    CHROMA = "chroma"
    TEMPO = "tempo"
    HARMONIC = "harmonic"
    PERCUSSIVE = "percussive"
    NEURAL = "neural"
    COMBINED = "combined"


class AudioFormat(Enum):
    """Supported audio formats."""
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"


@dataclass
class AudioMetadata:
    """Audio file metadata container."""
    duration: float
    sample_rate: int
    channels: int
    bit_depth: Optional[int] = None
    bitrate: Optional[int] = None
    format: Optional[AudioFormat] = None
    codec: Optional[str] = None
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    bpm: Optional[float] = None
    key: Optional[str] = None
    energy: Optional[float] = None
    valence: Optional[float] = None
    danceability: Optional[float] = None


@dataclass
class AudioFingerprint:
    """Audio fingerprint data structure."""
    fingerprint_id: str
    fingerprint_type: AudioFingerprintType
    data: np.ndarray
    confidence: float
    metadata: AudioMetadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    processing_time: float = 0.0
    file_path: Optional[str] = None
    hash_sha256: Optional[str] = None
    additional_features: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AudioAnalysisConfig:
    """Configuration for audio analysis."""
    sample_rate: int = 22050
    hop_length: int = 512
    n_fft: int = 2048
    n_mels: int = 128
    n_mfcc: int = 13
    n_chroma: int = 12
    window_size: float = 2.0  # seconds
    overlap: float = 0.5  # 50% overlap
    enable_neural_features: bool = True
    enable_chromaprint: bool = True
    enable_spectral_analysis: bool = True
    quality_threshold: float = 0.7
    confidence_threshold: float = 0.8


class AudioFingerprintingSystem:
    """
    Advanced Audio Fingerprinting System
    
    Provides comprehensive audio content fingerprinting with:
    - Multiple fingerprinting algorithms (chromaprint, spectral, neural)
    - ML-powered feature extraction
    - Real-time processing capabilities
    - Music industry standard compatibility
    - Creator protection optimization
    """
    
    def __init__(self, config: Optional[AudioAnalysisConfig] = None):
        """Initialize audio fingerprinting system."""
        self.config = config or AudioAnalysisConfig()
        self.logger = logging.getLogger(__name__)
        
        # Vector database for similarity matching
        self.vector_db = VectorDatabaseManager()
        self.performance_analytics = PerformanceAnalytics()
        
        # Neural models for advanced analysis
        self.wav2vec_processor = None
        self.wav2vec_model = None
        
        # Initialize components
        self._initialize_neural_models()
        
        self.logger.info("AudioFingerprintingSystem initialized successfully")
    
    def _initialize_neural_models(self):
        """Initialize neural models for advanced audio analysis."""
        try:
            if self.config.enable_neural_features:
                self.wav2vec_processor = Wav2Vec2Processor.from_pretrained(
                    "facebook/wav2vec2-base-960h"
                )
                self.wav2vec_model = Wav2Vec2Model.from_pretrained(
                    "facebook/wav2vec2-base-960h"
                )
                self.logger.info("Neural models initialized successfully")
        except Exception as e:
            self.logger.warning(f"Failed to initialize neural models: {e}")
            self.config.enable_neural_features = False
    
    async def process_audio_file(
        self,
        file_path: str,
        creator_id: str,
        fingerprint_types: Optional[List[AudioFingerprintType]] = None
    ) -> List[AudioFingerprint]:
        """
        Process audio file and generate multiple fingerprints.
        
        Args:
            file_path: Path to audio file
            creator_id: Creator identifier for protection
            fingerprint_types: Types of fingerprints to generate
        
        Returns:
            List of generated audio fingerprints
        """
        start_time = datetime.utcnow()
        
        try:
            # Load audio file
            audio_data, sample_rate = librosa.load(file_path, sr=self.config.sample_rate)
            
            # Extract metadata
            metadata = await self._extract_metadata(file_path, audio_data, sample_rate)
            
            # Generate file hash
            file_hash = await self._generate_file_hash(file_path)
            
            # Default fingerprint types
            if fingerprint_types is None:
                fingerprint_types = [
                    AudioFingerprintType.CHROMAPRINT,
                    AudioFingerprintType.SPECTRAL,
                    AudioFingerprintType.MFCC,
                    AudioFingerprintType.MEL_SPECTROGRAM,
                    AudioFingerprintType.COMBINED
                ]
            
            # Generate fingerprints
            fingerprints = []
            for fp_type in fingerprint_types:
                fingerprint = await self._generate_fingerprint(
                    audio_data=audio_data,
                    sample_rate=sample_rate,
                    fingerprint_type=fp_type,
                    metadata=metadata,
                    file_path=file_path,
                    file_hash=file_hash
                )
                fingerprints.append(fingerprint)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update fingerprints with processing time
            for fp in fingerprints:
                fp.processing_time = processing_time
            
            # Store fingerprints in vector database
            await self._store_fingerprints(fingerprints, creator_id)
            
            # Record analytics
            await self.performance_analytics.record_processing_metrics({
                'operation': 'audio_fingerprinting',
                'file_path': file_path,
                'creator_id': creator_id,
                'processing_time': processing_time,
                'fingerprint_count': len(fingerprints),
                'success': True
            })
            
            self.logger.info(
                f"Generated {len(fingerprints)} fingerprints for {file_path} "
                f"in {processing_time:.2f}s"
            )
            
            return fingerprints
            
        except Exception as e:
            error_msg = f"Failed to process audio file {file_path}: {e}"
            self.logger.error(error_msg)
            
            await self.performance_analytics.record_processing_metrics({
                'operation': 'audio_fingerprinting',
                'file_path': file_path,
                'creator_id': creator_id,
                'processing_time': (datetime.utcnow() - start_time).total_seconds(),
                'fingerprint_count': 0,
                'success': False,
                'error': str(e)
            })
            
            raise
    
    async def _generate_fingerprint(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        fingerprint_type: AudioFingerprintType,
        metadata: AudioMetadata,
        file_path: str,
        file_hash: str
    ) -> AudioFingerprint:
        """Generate specific type of audio fingerprint."""
        
        try:
            if fingerprint_type == AudioFingerprintType.CHROMAPRINT:
                data, confidence = await self._generate_chromaprint(audio_data, sample_rate)
            
            elif fingerprint_type == AudioFingerprintType.SPECTRAL:
                data, confidence = await self._generate_spectral_fingerprint(audio_data, sample_rate)
            
            elif fingerprint_type == AudioFingerprintType.MFCC:
                data, confidence = await self._generate_mfcc_fingerprint(audio_data, sample_rate)
            
            elif fingerprint_type == AudioFingerprintType.MEL_SPECTROGRAM:
                data, confidence = await self._generate_mel_spectrogram(audio_data, sample_rate)
            
            elif fingerprint_type == AudioFingerprintType.CHROMA:
                data, confidence = await self._generate_chroma_fingerprint(audio_data, sample_rate)
            
            elif fingerprint_type == AudioFingerprintType.TEMPO:
                data, confidence = await self._generate_tempo_fingerprint(audio_data, sample_rate)
            
            elif fingerprint_type == AudioFingerprintType.HARMONIC:
                data, confidence = await self._generate_harmonic_fingerprint(audio_data, sample_rate)
            
            elif fingerprint_type == AudioFingerprintType.PERCUSSIVE:
                data, confidence = await self._generate_percussive_fingerprint(audio_data, sample_rate)
            
            elif fingerprint_type == AudioFingerprintType.NEURAL:
                data, confidence = await self._generate_neural_fingerprint(audio_data, sample_rate)
            
            elif fingerprint_type == AudioFingerprintType.COMBINED:
                data, confidence = await self._generate_combined_fingerprint(audio_data, sample_rate)
            
            else:
                raise ValueError(f"Unsupported fingerprint type: {fingerprint_type}")
            
            # Generate unique fingerprint ID
            fingerprint_id = self._generate_fingerprint_id(
                file_hash, fingerprint_type.value, data
            )
            
            return AudioFingerprint(
                fingerprint_id=fingerprint_id,
                fingerprint_type=fingerprint_type,
                data=data,
                confidence=confidence,
                metadata=metadata,
                file_path=file_path,
                hash_sha256=file_hash
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate {fingerprint_type.value} fingerprint: {e}")
            raise
    
    async def _generate_chromaprint(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> Tuple[np.ndarray, float]:
        """Generate Chromaprint fingerprint."""
        try:
            # Convert to 16-bit PCM
            audio_pcm = (audio_data * 32767).astype(np.int16)
            
            # Generate chromaprint
            fingerprint = chromaprint.encode(audio_pcm, sample_rate)
            
            # Convert to numpy array
            fp_array = np.array([int(x) for x in fingerprint])
            
            # Calculate confidence based on fingerprint entropy
            confidence = self._calculate_entropy_confidence(fp_array)
            
            return fp_array, confidence
            
        except Exception as e:
            self.logger.error(f"Chromaprint generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_spectral_fingerprint(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> Tuple[np.ndarray, float]:
        """Generate spectral fingerprint."""
        try:
            # Compute short-time Fourier transform
            stft = librosa.stft(
                audio_data,
                hop_length=self.config.hop_length,
                n_fft=self.config.n_fft
            )
            
            # Get magnitude spectrogram
            magnitude = np.abs(stft)
            
            # Extract spectral features
            spectral_centroid = librosa.feature.spectral_centroid(
                y=audio_data, sr=sample_rate
            )[0]
            
            spectral_bandwidth = librosa.feature.spectral_bandwidth(
                y=audio_data, sr=sample_rate
            )[0]
            
            spectral_rolloff = librosa.feature.spectral_rolloff(
                y=audio_data, sr=sample_rate
            )[0]
            
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)[0]
            
            # Combine features
            features = np.concatenate([
                spectral_centroid,
                spectral_bandwidth,
                spectral_rolloff,
                zero_crossing_rate
            ])
            
            # Calculate confidence
            confidence = self._calculate_feature_confidence(features)
            
            return features, confidence
            
        except Exception as e:
            self.logger.error(f"Spectral fingerprint generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_mfcc_fingerprint(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> Tuple[np.ndarray, float]:
        """Generate MFCC fingerprint."""
        try:
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(
                y=audio_data,
                sr=sample_rate,
                n_mfcc=self.config.n_mfcc,
                hop_length=self.config.hop_length
            )
            
            # Calculate statistics
            mfcc_mean = np.mean(mfccs, axis=1)
            mfcc_std = np.std(mfccs, axis=1)
            
            # Combine features
            features = np.concatenate([mfcc_mean, mfcc_std])
            
            # Calculate confidence
            confidence = self._calculate_feature_confidence(features)
            
            return features, confidence
            
        except Exception as e:
            self.logger.error(f"MFCC fingerprint generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_mel_spectrogram(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> Tuple[np.ndarray, float]:
        """Generate mel-spectrogram fingerprint."""
        try:
            # Extract mel-spectrogram
            mel_spec = librosa.feature.melspectrogram(
                y=audio_data,
                sr=sample_rate,
                n_mels=self.config.n_mels,
                hop_length=self.config.hop_length
            )
            
            # Convert to log scale
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Calculate statistics
            mel_mean = np.mean(mel_spec_db, axis=1)
            mel_std = np.std(mel_spec_db, axis=1)
            
            # Combine features
            features = np.concatenate([mel_mean, mel_std])
            
            # Calculate confidence
            confidence = self._calculate_feature_confidence(features)
            
            return features, confidence
            
        except Exception as e:
            self.logger.error(f"Mel-spectrogram fingerprint generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_chroma_fingerprint(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> Tuple[np.ndarray, float]:
        """Generate chroma fingerprint."""
        try:
            # Extract chroma features
            chroma = librosa.feature.chroma_stft(
                y=audio_data,
                sr=sample_rate,
                hop_length=self.config.hop_length
            )
            
            # Calculate statistics
            chroma_mean = np.mean(chroma, axis=1)
            chroma_std = np.std(chroma, axis=1)
            
            # Combine features
            features = np.concatenate([chroma_mean, chroma_std])
            
            # Calculate confidence
            confidence = self._calculate_feature_confidence(features)
            
            return features, confidence
            
        except Exception as e:
            self.logger.error(f"Chroma fingerprint generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_tempo_fingerprint(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> Tuple[np.ndarray, float]:
        """Generate tempo-based fingerprint."""
        try:
            # Extract tempo and beat tracking
            tempo, beats = librosa.beat.beat_track(
                y=audio_data, sr=sample_rate
            )
            
            # Calculate beat intervals
            beat_times = librosa.frames_to_time(beats, sr=sample_rate)
            beat_intervals = np.diff(beat_times)
            
            # Extract rhythm features
            features = np.array([
                tempo,
                np.mean(beat_intervals),
                np.std(beat_intervals),
                len(beats) / (len(audio_data) / sample_rate)  # beat density
            ])
            
            # Calculate confidence
            confidence = min(1.0, tempo / 200.0) if tempo > 0 else 0.0
            
            return features, confidence
            
        except Exception as e:
            self.logger.error(f"Tempo fingerprint generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_harmonic_fingerprint(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> Tuple[np.ndarray, float]:
        """Generate harmonic fingerprint."""
        try:
            # Separate harmonic and percussive components
            y_harmonic, _ = librosa.effects.hpss(audio_data)
            
            # Extract spectral features from harmonic component
            spectral_centroid = librosa.feature.spectral_centroid(
                y=y_harmonic, sr=sample_rate
            )[0]
            
            spectral_bandwidth = librosa.feature.spectral_bandwidth(
                y=y_harmonic, sr=sample_rate
            )[0]
            
            # Extract tonal features
            chroma = librosa.feature.chroma_stft(
                y=y_harmonic, sr=sample_rate
            )
            
            # Combine features
            features = np.concatenate([
                np.mean(spectral_centroid),
                np.std(spectral_centroid),
                np.mean(spectral_bandwidth),
                np.std(spectral_bandwidth),
                np.mean(chroma, axis=1)
            ])
            
            # Calculate confidence
            confidence = self._calculate_feature_confidence(features)
            
            return features, confidence
            
        except Exception as e:
            self.logger.error(f"Harmonic fingerprint generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_percussive_fingerprint(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> Tuple[np.ndarray, float]:
        """Generate percussive fingerprint."""
        try:
            # Separate harmonic and percussive components
            _, y_percussive = librosa.effects.hpss(audio_data)
            
            # Extract rhythm features
            tempo, beats = librosa.beat.beat_track(
                y=y_percussive, sr=sample_rate
            )
            
            # Extract spectral features from percussive component
            spectral_centroid = librosa.feature.spectral_centroid(
                y=y_percussive, sr=sample_rate
            )[0]
            
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y_percussive)[0]
            
            # Combine features
            features = np.concatenate([
                [tempo],
                np.mean(spectral_centroid),
                np.std(spectral_centroid),
                np.mean(zero_crossing_rate),
                np.std(zero_crossing_rate)
            ])
            
            # Calculate confidence
            confidence = min(1.0, tempo / 200.0) if tempo > 0 else 0.0
            
            return features, confidence
            
        except Exception as e:
            self.logger.error(f"Percussive fingerprint generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_neural_fingerprint(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> Tuple[np.ndarray, float]:
        """Generate neural network-based fingerprint."""
        try:
            if not self.config.enable_neural_features or self.wav2vec_model is None:
                return np.array([]), 0.0
            
            # Resample if necessary
            if sample_rate != 16000:
                audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=16000)
            
            # Convert to tensor
            audio_tensor = torch.tensor(audio_data).unsqueeze(0)
            
            # Extract features using Wav2Vec2
            with torch.no_grad():
                features = self.wav2vec_model(audio_tensor).last_hidden_state
                
            # Pool features
            features_pooled = torch.mean(features, dim=1).squeeze().numpy()
            
            # Calculate confidence
            confidence = self._calculate_feature_confidence(features_pooled)
            
            return features_pooled, confidence
            
        except Exception as e:
            self.logger.error(f"Neural fingerprint generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_combined_fingerprint(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> Tuple[np.ndarray, float]:
        """Generate combined fingerprint from multiple features."""
        try:
            features_list = []
            confidences = []
            
            # Generate multiple fingerprints
            fingerprint_types = [
                AudioFingerprintType.SPECTRAL,
                AudioFingerprintType.MFCC,
                AudioFingerprintType.CHROMA,
                AudioFingerprintType.TEMPO
            ]
            
            for fp_type in fingerprint_types:
                if fp_type == AudioFingerprintType.SPECTRAL:
                    features, confidence = await self._generate_spectral_fingerprint(
                        audio_data, sample_rate
                    )
                elif fp_type == AudioFingerprintType.MFCC:
                    features, confidence = await self._generate_mfcc_fingerprint(
                        audio_data, sample_rate
                    )
                elif fp_type == AudioFingerprintType.CHROMA:
                    features, confidence = await self._generate_chroma_fingerprint(
                        audio_data, sample_rate
                    )
                elif fp_type == AudioFingerprintType.TEMPO:
                    features, confidence = await self._generate_tempo_fingerprint(
                        audio_data, sample_rate
                    )
                
                if len(features) > 0:
                    features_list.append(features)
                    confidences.append(confidence)
            
            # Combine all features
            if features_list:
                combined_features = np.concatenate(features_list)
                combined_confidence = np.mean(confidences)
            else:
                combined_features = np.array([])
                combined_confidence = 0.0
            
            return combined_features, combined_confidence
            
        except Exception as e:
            self.logger.error(f"Combined fingerprint generation failed: {e}")
            return np.array([]), 0.0
    
    async def _extract_metadata(
        self, file_path: str, audio_data: np.ndarray, sample_rate: int
    ) -> AudioMetadata:
        """Extract comprehensive audio metadata."""
        try:
            # Basic audio properties
            duration = len(audio_data) / sample_rate
            channels = 1 if audio_data.ndim == 1 else audio_data.shape[0]
            
            # Audio analysis features
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            
            # Spectral features for energy/valence estimation
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(
                y=audio_data, sr=sample_rate
            ))
            
            zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(audio_data))
            
            # Estimate audio characteristics
            energy = float(spectral_centroid / 10000.0)  # Normalized energy
            valence = float(min(1.0, zero_crossing_rate * 10))  # Approximated valence
            danceability = float(min(1.0, tempo / 200.0)) if tempo > 0 else 0.0
            
            return AudioMetadata(
                duration=duration,
                sample_rate=sample_rate,
                channels=channels,
                bpm=float(tempo) if tempo > 0 else None,
                energy=energy,
                valence=valence,
                danceability=danceability
            )
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {e}")
            return AudioMetadata(
                duration=len(audio_data) / sample_rate,
                sample_rate=sample_rate,
                channels=1 if audio_data.ndim == 1 else audio_data.shape[0]
            )
    
    async def _generate_file_hash(self, file_path: str) -> str:
        """Generate SHA-256 hash of audio file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"File hash generation failed: {e}")
            return ""
    
    def _generate_fingerprint_id(
        self, file_hash: str, fingerprint_type: str, data: np.ndarray
    ) -> str:
        """Generate unique fingerprint identifier."""
        content = f"{file_hash}_{fingerprint_type}_{hash(data.tobytes())}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _calculate_entropy_confidence(self, data: np.ndarray) -> float:
        """Calculate confidence based on data entropy."""
        try:
            if len(data) == 0:
                return 0.0
            
            # Calculate entropy
            _, counts = np.unique(data, return_counts=True)
            probabilities = counts / len(data)
            entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
            
            # Normalize to [0, 1]
            max_entropy = np.log2(len(data))
            confidence = entropy / max_entropy if max_entropy > 0 else 0.0
            
            return min(1.0, max(0.0, confidence))
            
        except Exception:
            return 0.0
    
    def _calculate_feature_confidence(self, features: np.ndarray) -> float:
        """Calculate confidence based on feature variance."""
        try:
            if len(features) == 0:
                return 0.0
            
            # Calculate coefficient of variation
            mean_val = np.mean(np.abs(features))
            std_val = np.std(features)
            
            if mean_val == 0:
                return 0.0
            
            cv = std_val / mean_val
            confidence = min(1.0, cv)  # Higher variance = higher confidence
            
            return max(0.0, confidence)
            
        except Exception:
            return 0.0
    
    async def _store_fingerprints(
        self, fingerprints: List[AudioFingerprint], creator_id: str
    ):
        """Store fingerprints in vector database."""
        try:
            for fingerprint in fingerprints:
                await self.vector_db.store_fingerprint(
                    fingerprint_id=fingerprint.fingerprint_id,
                    vector=fingerprint.data,
                    metadata={
                        'type': 'audio',
                        'subtype': fingerprint.fingerprint_type.value,
                        'creator_id': creator_id,
                        'confidence': fingerprint.confidence,
                        'duration': fingerprint.metadata.duration,
                        'file_path': fingerprint.file_path,
                        'hash': fingerprint.hash_sha256,
                        'created_at': fingerprint.created_at.isoformat()
                    }
                )
        except Exception as e:
            self.logger.error(f"Failed to store fingerprints: {e}")
            raise
    
    async def find_similar_audio(
        self,
        fingerprint: AudioFingerprint,
        similarity_threshold: float = 0.85,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Find similar audio content based on fingerprint."""
        try:
            # Search in vector database
            results = await self.vector_db.search_similar(
                vector=fingerprint.data,
                threshold=similarity_threshold,
                max_results=max_results,
                metadata_filter={'type': 'audio', 'subtype': fingerprint.fingerprint_type.value}
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Similarity search failed: {e}")
            return []
    
    async def analyze_audio_quality(self, fingerprint: AudioFingerprint) -> Dict[str, float]:
        """Analyze audio quality metrics."""
        try:
            quality_metrics = {
                'confidence': fingerprint.confidence,
                'duration_score': min(1.0, fingerprint.metadata.duration / 30.0),  # 30s baseline
                'sample_rate_score': min(1.0, fingerprint.metadata.sample_rate / 44100.0),
                'feature_completeness': 1.0 if len(fingerprint.data) > 0 else 0.0
            }
            
            # Overall quality score
            quality_metrics['overall_quality'] = np.mean(list(quality_metrics.values()))
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Quality analysis failed: {e}")
            return {'overall_quality': 0.0}


# Factory function for creating audio fingerprinting system
def create_audio_fingerprinting_system(
    config: Optional[AudioAnalysisConfig] = None
) -> AudioFingerprintingSystem:
    """Create and initialize audio fingerprinting system."""
    return AudioFingerprintingSystem(config)


# Export public interface
__all__ = [
    'AudioFingerprintingSystem',
    'AudioFingerprint',
    'AudioFingerprintType',
    'AudioFormat',
    'AudioMetadata',
    'AudioAnalysisConfig',
    'create_audio_fingerprinting_system'
]