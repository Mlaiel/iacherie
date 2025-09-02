"""Advanced Audio Processor - Industrial Audio Processing & Analysis Engine

Ultra-advanced audio processing system with ML-powered analysis, feature extraction,
and real-time audio processing capabilities for professional music production.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
import numpy as np
from dataclasses import dataclass
from datetime import datetime
import librosa
import soundfile as sf
from scipy import signal, fftpack
from scipy.signal import butter, filtfilt, hilbert
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
from concurrent.futures import ThreadPoolExecutor
import pickle
import hashlib
from pathlib import Path

try:
    from core.config import get_settings
except ImportError:
    # Fallback settings
    get_settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...core.cache import CacheManager
from ...core.monitoring import MetricsCollector
from ...security.audio_protection import AudioFingerprintManager
from ...ml.audio import AudioMLPipeline

logger = logging.getLogger(__name__)

@dataclass
class AudioProcessingConfig:
    """
Comprehensive audio processing configuration"""
    target_sample_rate: int = 44100
    frame_length: int = 2048
    hop_length: int = 512
    n_mels: int = 128
    n_fft: int = 2048
    max_frequency: float = 8000.0
    min_frequency: float = 20.0
    quality_threshold: float = 0.7
    enhancement_enabled: bool = True
    real_time_processing: bool = False
    batch_size: int = 32
    use_gpu: bool = True
    cache_features: bool = True
    
@dataclass
class AudioFeatures:
    """
Complete audio feature set for ML and analysis"""
    # Basic features
    duration_seconds: float
    sample_rate: int
    channels: int
    bit_depth: int
    
    # Spectral features
    spectral_centroid: np.ndarray
    spectral_rolloff: np.ndarray
    spectral_bandwidth: np.ndarray
    spectral_contrast: np.ndarray
    spectral_flatness: np.ndarray
    
    # Rhythmic features
    tempo: float
    beats: np.ndarray
    onset_strength: np.ndarray
    rhythm_regularity: float
    
    # Harmonic features
    chroma_features: np.ndarray
    harmonic_content: np.ndarray
    harmonic_to_percussive_ratio: float
    
    # Advanced features
    mfcc: np.ndarray
    mel_spectrogram: np.ndarray
    zero_crossing_rate: np.ndarray
    rms_energy: np.ndarray
    
    # Quality metrics
    dynamic_range: float
    snr_db: float
    thd_percentage: float
    frequency_response_flatness: float
    
    # ML features
    embeddings: Optional[np.ndarray] = None
    audio_fingerprint: Optional[str] = None

class AudioProcessor:
    """
    Advanced audio processing engine with industrial-grade capabilities
    
    Features:
    - Real-time and batch audio processing
    - ML-powered feature extraction and analysis
    - Professional audio quality assessment
    - Multi-threaded processing for performance
    - Audio fingerprinting and protection
    - Format conversion and optimization
    """
    
    def __init__(self, config: Optional[AudioProcessingConfig] = None):
        self.config = config or AudioProcessingConfig()
        self.settings = get_settings()
        self.cache_manager = CacheManager()
        self.metrics = MetricsCollector()
        self.fingerprint_manager = AudioFingerprintManager()
        self.ml_pipeline = AudioMLPipeline()
        
        # Initialize processing resources
        self.device = torch.device("cuda" if torch.cuda.is_available() and self.config.use_gpu else "cpu")
        self.scaler = StandardScaler()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Audio processing models
        self._initialize_models()
        
        logger.info(f"AudioProcessor initialized with device: {self.device}")
    
    def _initialize_models(self):
        """Initialize ML models for audio processing"""
        try:
            # Load pre-trained models for audio analysis
            self.feature_extraction_model = self._load_feature_model()
            self.quality_assessment_model = self._load_quality_model()
            self.genre_classification_model = self._load_genre_model()
            
        except Exception as e:
            logger.warning(f"Could not load some ML models: {e}")
            # Initialize simple fallback models
            self.feature_extraction_model = None
            self.quality_assessment_model = None
            self.genre_classification_model = None
    
    def _load_feature_model(self) -> Optional[nn.Module]:
        """Load feature extraction neural network model"""
        # In production, this would load a pre-trained model
        # For now, return a simple CNN-based feature extractor
        class AudioFeatureNet(nn.Module):
            def __init__(self):
                super().__init__()
                self.conv1 = nn.Conv1d(1, 64, kernel_size=1024, stride=512)
                self.conv2 = nn.Conv1d(64, 128, kernel_size=512, stride=256)
                self.conv3 = nn.Conv1d(128, 256, kernel_size=256, stride=128)
                self.pool = nn.AdaptiveAvgPool1d(1)
                self.fc = nn.Linear(256, 128)
                self.dropout = nn.Dropout(0.3)
                
            def forward(self, x):
                x = torch.relu(self.conv1(x))
                x = torch.relu(self.conv2(x))
                x = torch.relu(self.conv3(x))
                x = self.pool(x)
                x = x.view(x.size(0), -1)
                x = self.dropout(torch.relu(self.fc(x)))
                return x
        
        model = AudioFeatureNet().to(self.device)
        return model
    
    def _load_quality_model(self) -> Optional[nn.Module]:
        """
Load audio quality assessment model"""
        class QualityAssessmentNet(nn.Module):
            def __init__(self):
                super().__init__()
                self.fc1 = nn.Linear(128, 64)
                self.fc2 = nn.Linear(64, 32)
                self.fc3 = nn.Linear(32, 1)
                self.dropout = nn.Dropout(0.2)
                
            def forward(self, x):
                x = torch.relu(self.fc1(x))
                x = self.dropout(x)
                x = torch.relu(self.fc2(x))
                x = self.dropout(x)
                x = torch.sigmoid(self.fc3(x))
                return x
        
        return QualityAssessmentNet().to(self.device)
    
    def _load_genre_model(self) -> Optional[nn.Module]:
        """
Load genre classification model"""
        class GenreClassifier(nn.Module):
            def __init__(self, num_genres=10):
                super().__init__()
                self.fc1 = nn.Linear(128, 64)
                self.fc2 = nn.Linear(64, 32)
                self.fc3 = nn.Linear(32, num_genres)
                self.dropout = nn.Dropout(0.3)
                
            def forward(self, x):
                x = torch.relu(self.fc1(x))
                x = self.dropout(x)
                x = torch.relu(self.fc2(x))
                x = self.dropout(x)
                x = torch.softmax(self.fc3(x), dim=1)
                return x
        
        return GenreClassifier().to(self.device)
    
    async def process_audio_comprehensive(self, 
                                        audio_data: np.ndarray, 
                                        sample_rate: int,
                                        extract_features: bool = True,
                                        analyze_quality: bool = True,
                                        create_fingerprint: bool = True) -> AudioFeatures:
        """
        Comprehensive audio processing and analysis
        
        Args:
            audio_data: Raw audio data
            sample_rate: Sample rate of audio
            extract_features: Whether to extract ML features
            analyze_quality: Whether to analyze audio quality
            create_fingerprint: Whether to create audio fingerprint
            
        Returns:
            Complete AudioFeatures object
        """
        start_time = datetime.now()
        
        try:
            # Normalize audio data
            audio_data = self._normalize_audio(audio_data)
            
            # Resample if necessary
            if sample_rate != self.config.target_sample_rate:
                audio_data = librosa.resample(
                    audio_data, 
                    orig_sr=sample_rate,
                    target_sr=self.config.target_sample_rate
                )
                sample_rate = self.config.target_sample_rate
            
            # Basic properties
            duration = len(audio_data) / sample_rate
            channels = 1 if len(audio_data.shape) == 1 else audio_data.shape[1]
            
            # Create cache key
            cache_key = self._generate_cache_key(audio_data, sample_rate)
            cached_features = await self.cache_manager.get(f"audio_features_{cache_key}")
            
            if cached_features and self.config.cache_features:
                logger.info("Using cached audio features")
                return cached_features
            
            # Parallel feature extraction
            tasks = []
            
            if extract_features:
                tasks.append(self._extract_spectral_features_async(audio_data, sample_rate))
                tasks.append(self._extract_rhythmic_features_async(audio_data, sample_rate))
                tasks.append(self._extract_harmonic_features_async(audio_data, sample_rate))
                tasks.append(self._extract_advanced_features_async(audio_data, sample_rate))
            
            if analyze_quality:
                tasks.append(self._analyze_quality_comprehensive_async(audio_data, sample_rate))
            
            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            spectral_features = results[0] if len(results) > 0 and not isinstance(results[0], Exception) else {}
            rhythmic_features = results[1] if len(results) > 1 and not isinstance(results[1], Exception) else {}
            harmonic_features = results[2] if len(results) > 2 and not isinstance(results[2], Exception) else {}
            advanced_features = results[3] if len(results) > 3 and not isinstance(results[3], Exception) else {}
            quality_metrics = results[4] if len(results) > 4 and not isinstance(results[4], Exception) else {}
            
            # Create audio fingerprint
            fingerprint = None
            if create_fingerprint:
                fingerprint = await self.fingerprint_manager.create_fingerprint(audio_data, sample_rate)
            
            # ML embeddings
            embeddings = None
            if self.feature_extraction_model and extract_features:
                embeddings = await self._extract_ml_embeddings(audio_data)
            
            # Construct comprehensive feature object
            features = AudioFeatures(
                # Basic properties
                duration_seconds=duration,
                sample_rate=sample_rate,
                channels=channels,
                bit_depth=32,  # Assuming float32
                
                # Spectral features
                spectral_centroid=spectral_features.get('centroid', np.array([])),
                spectral_rolloff=spectral_features.get('rolloff', np.array([])),
                spectral_bandwidth=spectral_features.get('bandwidth', np.array([])),
                spectral_contrast=spectral_features.get('contrast', np.array([])),
                spectral_flatness=spectral_features.get('flatness', np.array([])),
                
                # Rhythmic features
                tempo=rhythmic_features.get('tempo', 0.0),
                beats=rhythmic_features.get('beats', np.array([])),
                onset_strength=rhythmic_features.get('onset_strength', np.array([])),
                rhythm_regularity=rhythmic_features.get('regularity', 0.0),
                
                # Harmonic features
                chroma_features=harmonic_features.get('chroma', np.array([])),
                harmonic_content=harmonic_features.get('harmonic', np.array([])),
                harmonic_to_percussive_ratio=harmonic_features.get('hp_ratio', 0.0),
                
                # Advanced features
                mfcc=advanced_features.get('mfcc', np.array([])),
                mel_spectrogram=advanced_features.get('mel_spec', np.array([])),
                zero_crossing_rate=advanced_features.get('zcr', np.array([])),
                rms_energy=advanced_features.get('rms', np.array([])),
                
                # Quality metrics
                dynamic_range=quality_metrics.get('dynamic_range', 0.0),
                snr_db=quality_metrics.get('snr_db', 0.0),
                thd_percentage=quality_metrics.get('thd', 0.0),
                frequency_response_flatness=quality_metrics.get('freq_flatness', 0.0),
                
                # ML features
                embeddings=embeddings,
                audio_fingerprint=fingerprint
            )
            
            # Cache the features
            if self.config.cache_features:
                await self.cache_manager.set(f"audio_features_{cache_key}", features, ttl=3600)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.metrics.record_metric("audio_processing_time", processing_time)
            
            logger.info(f"Audio processing completed in {processing_time:.3f}s")
            return features
            
        except Exception as e:
            logger.error(f"Comprehensive audio processing failed: {e}")
            raise
    
    async def _extract_spectral_features_async(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract spectral features asynchronously"""
        def extract_spectral():
            # Spectral centroid
            centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            
            # Spectral rolloff
            rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
            
            # Spectral bandwidth
            bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)[0]
            
            # Spectral contrast
            contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
            
            # Spectral flatness
            flatness = librosa.feature.spectral_flatness(y=audio_data)[0]
            
            return {
                'centroid': centroid,
                'rolloff': rolloff,
                'bandwidth': bandwidth,
                'contrast': contrast,
                'flatness': flatness
            }
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, extract_spectral)
    
    async def _extract_rhythmic_features_async(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """
Extract rhythmic features asynchronously"""
        def extract_rhythmic():
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess_extract_rhythmic_input(data)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess_extract_rhythmic_result(result)
            
                    logger.info(f"AI processing extract_rhythmic completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing extract_rhythmic failed: {e}")
                    raise
                tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
                
                # Onset strength
                onset_strength = librosa.onset.onset_strength(y=audio_data, sr=sample_rate)
                
                # Rhythm regularity
                if len(beats) > 1:
                    beat_intervals = np.diff(beats)
                    regularity = 1.0 - (np.std(beat_intervals) / (np.mean(beat_intervals) + 1e-10))
                else:
                    regularity = 0.0
                
                return {
                    'tempo': float(tempo),
                    'beats': beats,
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess_extract_harmonic_input(data)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess_extract_harmonic_result(result)
            
                    logger.info(f"AI processing extract_harmonic completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing extract_harmonic failed: {e}")
                    raise
                    'regularity': float(regularity)
                }
            except Exception as e:
                logger.warning(f"Rhythmic feature extraction failed: {e}")
                return {
                    'tempo': 0.0,
                    'beats': np.array([]),
                    'onset_strength': np.array([]),
                    'regularity': 0.0
                }
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, extract_rhythmic)
    
    async def _extract_harmonic_features_async(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess_extract_advanced_input(data)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess_extract_advanced_result(result)
            
                    logger.info(f"AI processing extract_advanced completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing extract_advanced failed: {e}")
                    raise
        return await loop.run_in_executor(self.executor, extract_rhythmic)
    
    async def _extract_harmonic_features_async(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract harmonic features asynchronously"""
        def extract_harmonic():
            try:
                # Chroma features
                chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
                
                # Harmonic and percussive separation
                harmonic, percussive = librosa.effects.hpss(audio_data)
                
                # Harmonic to percussive ratio
                harmonic_energy = np.sum(harmonic**2)
                percussive_energy = np.sum(percussive**2)
                hp_ratio = harmonic_energy / (percussive_energy + 1e-10)
                
                return {
                    'chroma': chroma,
                    'harmonic': harmonic,
                    'hp_ratio': float(hp_ratio)
                }
            except Exception as e:
                logger.warning(f"Harmonic feature extraction failed: {e}")
                return {
                    'chroma': np.array([]),
                    'harmonic': np.array([]),
                    'hp_ratio': 0.0
                }
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, extract_harmonic)
    
    async def _extract_advanced_features_async(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract advanced features asynchronously"""
        def extract_advanced():
            try:
                # MFCC features
                mfcc = librosa.feature.mfcc(
                    y=audio_data, 
                    sr=sample_rate, 
                    n_mfcc=13,
                    n_fft=self.config.n_fft,
                    hop_length=self.config.hop_length
                )
                
                # Mel spectrogram
                mel_spec = librosa.feature.melspectrogram(
                    y=audio_data,
                    sr=sample_rate,
                    n_mels=self.config.n_mels,
                    n_fft=self.config.n_fft,
                    hop_length=self.config.hop_length
                )
                
                # Zero crossing rate
                zcr = librosa.feature.zero_crossing_rate(
                    audio_data, 
                    frame_length=self.config.frame_length,
                    hop_length=self.config.hop_length
                )[0]
                
                # RMS energy
                rms = librosa.feature.rms(
                    y=audio_data,
                    frame_length=self.config.frame_length,
                    hop_length=self.config.hop_length
                )[0]
                
                return {
                    'mfcc': mfcc,
                    'mel_spec': mel_spec,
                    'zcr': zcr,
                    'rms': rms
                }
            except Exception as e:
                logger.warning(f"Advanced feature extraction failed: {e}")
                return {
                    'mfcc': np.array([]),
                    'mel_spec': np.array([]),
                    'zcr': np.array([]),
                    'rms': np.array([])
                }
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, extract_advanced)
    
    async def _analyze_quality_comprehensive_async(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Comprehensive audio quality analysis"""
        def analyze_quality():
            # Dynamic range
            dynamic_range = np.max(audio_data) - np.min(audio_data)
            
            # Signal-to-noise ratio
            signal_power = np.mean(audio_data**2)
            noise_floor = np.percentile(np.abs(audio_data), 5)
            snr_db = 10 * np.log10(signal_power / (noise_floor**2 + 1e-10))
            
            # Total Harmonic Distortion (THD) approximation
            fft_audio = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)
            
            # Find fundamental frequency (simplified)
            fundamental_idx = np.argmax(np.abs(fft_audio[:len(fft_audio)//2]))
            fundamental_freq = freqs[fundamental_idx]
            
            # Calculate harmonic distortion (simplified)
            harmonic_power = 0
            fundamental_power = np.abs(fft_audio[fundamental_idx])**2
            
            for harmonic in range(2, 6):  # 2nd to 5th harmonics
                harmonic_freq = fundamental_freq * harmonic
                harmonic_idx = np.argmin(np.abs(freqs - harmonic_freq))
                if harmonic_idx < len(fft_audio)//2:
                    harmonic_power += np.abs(fft_audio[harmonic_idx])**2
            
            thd = np.sqrt(harmonic_power) / np.sqrt(fundamental_power + 1e-10) * 100
            
            # Frequency response flatness
            psd = np.abs(fft_audio)**2
            psd_smooth = signal.savgol_filter(psd[:len(psd)//2], 51, 3)
            freq_flatness = 1.0 - (np.std(psd_smooth) / (np.mean(psd_smooth) + 1e-10))
            
            return {
                'dynamic_range': float(dynamic_range),
                'snr_db': float(snr_db),
                'thd': float(thd),
                'freq_flatness': float(freq_flatness)
            }
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, analyze_quality)
    
    async def _extract_ml_embeddings(self, audio_data: np.ndarray) -> Optional[np.ndarray]:
        """
Extract ML embeddings using neural network"""
        try:
            if self.feature_extraction_model is None:
                return None
            
            # Prepare input tensor
            audio_tensor = torch.FloatTensor(audio_data).unsqueeze(0).unsqueeze(0).to(self.device)
            
            # Extract features
            with torch.no_grad():
                embeddings = self.feature_extraction_model(audio_tensor)
            
            return embeddings.cpu().numpy().flatten()
            
        except Exception as e:
            logger.warning(f"ML embedding extraction failed: {e}")
            return None
    
    def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        try:
            logger.info(f"Executing _apply_mastering_chain")
            
            # Implementation for _apply_mastering_chain
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_apply_mastering_chain completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_apply_mastering_chain failed: {e}")
            raise
        """Professional audio format conversion with quality optimization"""
        try:
            converted_audio = audio_data.copy()
            conversion_info = {
                "original_format": "float32",
                "target_format": target_format,
                "quality_level": quality_level,
                "processing_applied": []
            }
            
            # Apply quality-specific processing
            if quality_level == "high":
                # Apply anti-aliasing filter before any resampling
                if target_format in ["mp3", "aac"]:
                    # Low-pass filter to prevent aliasing
                    nyquist = sample_rate // 2
                    cutoff = min(nyquist * 0.9, 20000)  # 20kHz max
                    b, a = butter(8, cutoff / nyquist, btype='low')
                    converted_audio = filtfilt(b, a, converted_audio)
                    conversion_info["processing_applied"].append("anti_aliasing_filter")
                
                # Normalize for optimal dynamic range
                peak = np.max(np.abs(converted_audio))
                if peak > 0:
                    converted_audio = converted_audio / peak * 0.95
                    conversion_info["processing_applied"].append("peak_normalization")
            
            elif quality_level == "extreme":
                # Professional mastering chain
                converted_audio = await self._apply_mastering_chain(converted_audio, sample_rate)
                conversion_info["processing_applied"].append("mastering_chain")
            
            conversion_info["peak_level"] = float(np.max(np.abs(converted_audio)))
            conversion_info["rms_level"] = float(np.sqrt(np.mean(converted_audio**2)))
            
            return converted_audio, conversion_info
            
        except Exception as e:
            logger.error(f"Professional format conversion failed: {e}")
            raise
    
    async def _apply_mastering_chain(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply professional mastering chain"""
        processed = audio_data.copy()
        
        # 1. High-pass filter (remove DC and low-frequency rumble)
        nyquist = sample_rate // 2
        b, a = butter(4, 20 / nyquist, btype='high')
        processed = filtfilt(b, a, processed)
        
        # 2. Multiband compression (simplified)
        processed = self._apply_multiband_compression(processed, sample_rate)
        
        # 3. EQ enhancement
        processed = self._apply_mastering_eq(processed, sample_rate)
        
        # 4. Limiting
        processed = self._apply_limiter(processed, threshold=-0.1, ratio=10.0)
        
        return processed
    
    def _apply_multiband_compression(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """
Apply multiband compression"""
        # Split into frequency bands
        nyquist = sample_rate // 2
        
        # Low band (20-200 Hz)
        b_low, a_low = butter(4, [20/nyquist, 200/nyquist], btype='band')
        low_band = filtfilt(b_low, a_low, audio_data)
        
        # Mid band (200-2000 Hz)
        b_mid, a_mid = butter(4, [200/nyquist, 2000/nyquist], btype='band')
        mid_band = filtfilt(b_mid, a_mid, audio_data)
        
        # High band (2000 Hz+)
        b_high, a_high = butter(4, 2000/nyquist, btype='high')
        high_band = filtfilt(b_high, a_high, audio_data)
        
        # Apply compression to each band
        low_compressed = self._apply_compression(low_band, threshold=0.6, ratio=3.0)
        mid_compressed = self._apply_compression(mid_band, threshold=0.7, ratio=2.5)
        high_compressed = self._apply_compression(high_band, threshold=0.8, ratio=2.0)
        
        # Recombine bands
        return low_compressed + mid_compressed + high_compressed
    
    def _apply_compression(self, audio_data: np.ndarray, threshold: float = 0.7, ratio: float = 4.0) -> np.ndarray:
        """
Apply dynamic range compression"""
        compressed = audio_data.copy()
        
        # Simple compression algorithm
        for i in range(len(compressed)):
            if abs(compressed[i]) > threshold:
                excess = abs(compressed[i]) - threshold
                compressed[i] = np.sign(compressed[i]) * (threshold + excess / ratio)
        
        return compressed
    
    def _apply_mastering_eq(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """
Apply mastering EQ"""
        processed = audio_data.copy()
        nyquist = sample_rate // 2
        
        # Slight high-frequency enhancement (presence boost)
        b, a = butter(2, 8000/nyquist, btype='high')
        high_freq = filtfilt(b, a, processed)
        processed += high_freq * 0.05  # 5% boost
        
        # Low-frequency control
        b, a = butter(2, 60/nyquist, btype='high')
        processed = filtfilt(b, a, processed)
        
        return processed
    
    def _apply_limiter(self, audio_data: np.ndarray, threshold: float = -0.1, ratio: float = 10.0) -> np.ndarray:
        """
Apply peak limiting"""
        limited = audio_data.copy()
        threshold_linear = 10**(threshold/20)  # Convert dB to linear
        
        peaks = np.abs(limited) > threshold_linear
        limited[peaks] = np.sign(limited[peaks]) * (
            threshold_linear + (np.abs(limited[peaks]) - threshold_linear) / ratio
        )
        
        return limited
    
    async def batch_process_audio(self, 
                                audio_files: List[str],
                                processing_config: Dict[str, Any]) -> List[AudioFeatures]:
        """
Process multiple audio files in parallel"""
        async def process_single_file(file_path: str) -> AudioFeatures:
            try:
                # Load audio file
                audio_data, sample_rate = librosa.load(file_path, sr=None)
                
                # Process audio
                return await self.process_audio_comprehensive(
                    audio_data=audio_data,
                    sample_rate=sample_rate,
                    **processing_config
                )
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                raise
        
        # Process files in batches to manage memory
        batch_size = self.config.batch_size
        results = []
        
        for i in range(0, len(audio_files), batch_size):
            batch = audio_files[i:i + batch_size]
            batch_tasks = [process_single_file(file_path) for file_path in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Filter out exceptions
            valid_results = [r for r in batch_results if not isinstance(r, Exception)]
            results.extend(valid_results)
        
        return results
    
    async def real_time_process_stream(self, 
                                     audio_stream: asyncio.Queue,
                                     callback: callable) -> None:
        """Process real-time audio stream"""
        if not self.config.real_time_processing:
            raise ValueError("Real-time processing not enabled")
        
        buffer = []
        frame_size = self.config.frame_length
        
        while True:
            try:
                # Get audio chunk from stream
                audio_chunk = await audio_stream.get()
                
                if audio_chunk is None:  # End of stream signal
                    break
                
                buffer.extend(audio_chunk)
                
                # Process when we have enough samples
                if len(buffer) >= frame_size:
                    frame_data = np.array(buffer[:frame_size])
                    buffer = buffer[self.config.hop_length:]  # Overlapping frames
                    
                    # Process frame
                    features = await self.process_audio_comprehensive(
                        audio_data=frame_data,
                        sample_rate=self.config.target_sample_rate,
                        extract_features=True,
                        analyze_quality=False,  # Skip quality analysis for real-time
                        create_fingerprint=False
                    )
                    
                    # Send results to callback
                    await callback(features)
                    
            except Exception as e:
                logger.error(f"Real-time processing error: {e}")
                break

class AudioAnalyzer:
    """
    Advanced audio analyzer for comprehensive audio content analysis
    
    Features:
    - Genre classification
    - Mood detection
    - Content analysis (vocals, instruments)
    - Audio quality assessment
    - Similarity matching
    - Audio fingerprinting
    """
    
    def __init__(self, processor: Optional[AudioProcessor] = None):
        self.processor = processor or AudioProcessor()
        self.settings = get_settings()
        
        # Classification models
        self.genre_classes = [
            "rock", "pop", "jazz", "classical", "electronic", 
            "hip_hop", "country", "blues", "reggae", "folk"
        ]
        
        self.mood_classes = [
            "happy", "sad", "energetic", "calm", "aggressive",
            "romantic", "mysterious", "uplifting", "dark", "peaceful"
        ]
    
    async def analyze_audio_content(self, features: AudioFeatures) -> Dict[str, Any]:
        """Comprehensive audio content analysis"""
        analysis_results = {
            "genre_prediction": await self._classify_genre(features),
            "mood_prediction": await self._detect_mood(features),
            "content_analysis": await self._analyze_content_structure(features),
            "quality_assessment": await self._assess_audio_quality(features),
            "technical_analysis": await self._technical_analysis(features),
            "recommendations": await self._generate_recommendations(features)
        }
        
        return analysis_results
    
    async def _classify_genre(self, features: AudioFeatures) -> Dict[str, float]:
        """Classify audio genre using ML features"""
        try:
            if self.processor.genre_classification_model and features.embeddings is not None:
                # Use ML model for classification
                embeddings_tensor = torch.FloatTensor(features.embeddings).unsqueeze(0).to(self.processor.device)
                
                with torch.no_grad():
                    predictions = self.processor.genre_classification_model(embeddings_tensor)
                    probabilities = predictions.cpu().numpy().flatten()
                
                # Create genre probability mapping
                genre_probs = {
                    genre: float(prob) for genre, prob in zip(self.genre_classes, probabilities)
                }
                
                return dict(sorted(genre_probs.items(), key=lambda x: x[1], reverse=True))
            
            else:
                # Fallback to rule-based classification
                return await self._rule_based_genre_classification(features)
                
        except Exception as e:
            logger.error(f"Genre classification failed: {e}")
            return {genre: 0.1 for genre in self.genre_classes}
    
    async def _rule_based_genre_classification(self, features: AudioFeatures) -> Dict[str, float]:
        """Rule-based genre classification as fallback"""
        genre_scores = {genre: 0.0 for genre in self.genre_classes}
        
        # Tempo-based heuristics
        tempo = features.tempo
        if tempo > 140:
            genre_scores["electronic"] += 0.3
            genre_scores["rock"] += 0.2
            genre_scores["pop"] += 0.2
        elif tempo > 100:
            genre_scores["pop"] += 0.3
            genre_scores["rock"] += 0.2
        elif tempo > 60:
            genre_scores["jazz"] += 0.2
            genre_scores["blues"] += 0.2
            genre_scores["folk"] += 0.1
        else:
            genre_scores["classical"] += 0.3
            genre_scores["jazz"] += 0.2
        
        # Spectral characteristics
        if hasattr(features, 'spectral_centroid') and len(features.spectral_centroid) > 0:
            avg_centroid = np.mean(features.spectral_centroid)
            if avg_centroid > 3000:
                genre_scores["electronic"] += 0.2
                genre_scores["rock"] += 0.15
            elif avg_centroid < 1000:
                genre_scores["classical"] += 0.2
                genre_scores["jazz"] += 0.15
        
        # Normalize scores
        total_score = sum(genre_scores.values())
        if total_score > 0:
            genre_scores = {k: v/total_score for k, v in genre_scores.items()}
        
        return dict(sorted(genre_scores.items(), key=lambda x: x[1], reverse=True))
    
    async def _detect_mood(self, features: AudioFeatures) -> Dict[str, float]:
        """Detect mood from audio features"""
        mood_scores = {mood: 0.0 for mood in self.mood_classes}
        
        # Tempo-based mood inference
        tempo = features.tempo
        if tempo > 120:
            mood_scores["energetic"] += 0.4
            mood_scores["happy"] += 0.3
            mood_scores["uplifting"] += 0.2
        elif tempo < 80:
            mood_scores["calm"] += 0.4
            mood_scores["peaceful"] += 0.3
            mood_scores["sad"] += 0.2
        
        # Energy-based mood (using RMS)
        if hasattr(features, 'rms_energy') and len(features.rms_energy) > 0:
            avg_energy = np.mean(features.rms_energy)
            if avg_energy > 0.1:
                mood_scores["energetic"] += 0.3
                mood_scores["aggressive"] += 0.2
            else:
                mood_scores["calm"] += 0.3
                mood_scores["peaceful"] += 0.2
        
        # Normalize scores
        total_score = sum(mood_scores.values())
        if total_score > 0:
            mood_scores = {k: v/total_score for k, v in mood_scores.items()}
        
        return dict(sorted(mood_scores.items(), key=lambda x: x[1], reverse=True))
    
    async def _analyze_content_structure(self, features: AudioFeatures) -> Dict[str, Any]:
        """Analyze the structure and content of the audio"""
        structure_analysis = {
            "has_vocals": False,
            "instrument_presence": {},
            "structure_segments": [],
            "complexity_score": 0.0,
            "harmonic_richness": 0.0
        }
        
        try:
            # Vocal detection (simplified heuristic)
            if hasattr(features, 'spectral_centroid') and len(features.spectral_centroid) > 0:
                # Vocals typically have energy in 200-2000 Hz range
                vocal_range_energy = np.mean(features.spectral_centroid)
                structure_analysis["has_vocals"] = vocal_range_energy > 1000 and vocal_range_energy < 4000
            
            # Harmonic richness from chroma features
            if hasattr(features, 'chroma_features') and features.chroma_features.size > 0:
                structure_analysis["harmonic_richness"] = float(np.std(features.chroma_features))
            
            # Complexity score from spectral features
            if hasattr(features, 'spectral_contrast') and features.spectral_contrast.size > 0:
                structure_analysis["complexity_score"] = float(np.mean(features.spectral_contrast))
            
            # Harmonic to percussive ratio analysis
            hp_ratio = features.harmonic_to_percussive_ratio
            if hp_ratio > 2.0:
                structure_analysis["instrument_presence"]["melodic_instruments"] = "high"
                structure_analysis["instrument_presence"]["percussion"] = "low"
            elif hp_ratio < 0.5:
                structure_analysis["instrument_presence"]["melodic_instruments"] = "low"
                structure_analysis["instrument_presence"]["percussion"] = "high"
            else:
                structure_analysis["instrument_presence"]["melodic_instruments"] = "medium"
                structure_analysis["instrument_presence"]["percussion"] = "medium"
                
        except Exception as e:
            logger.warning(f"Content structure analysis failed: {e}")
        
        return structure_analysis
    
    async def _assess_audio_quality(self, features: AudioFeatures) -> Dict[str, Any]:
        """Assess overall audio quality"""
        quality_assessment = {
            "overall_score": 0.0,
            "quality_factors": {},
            "issues_detected": [],
            "improvement_suggestions": []
        }
        
        try:
            scores = []
            
            # Dynamic range assessment
            dr_score = min(features.dynamic_range * 50, 1.0)  # Normalize to 0-1
            quality_assessment["quality_factors"]["dynamic_range"] = dr_score
            scores.append(dr_score)
            
            if dr_score < 0.3:
                quality_assessment["issues_detected"].append("Low dynamic range (over-compressed)")
                quality_assessment["improvement_suggestions"].append("Reduce compression, increase dynamic range")
            
            # SNR assessment
            snr_score = min(max(features.snr_db - 20, 0) / 40, 1.0)  # 20-60 dB range
            quality_assessment["quality_factors"]["signal_to_noise"] = snr_score
            scores.append(snr_score)
            
            if snr_score < 0.5:
                quality_assessment["issues_detected"].append("High noise floor")
                quality_assessment["improvement_suggestions"].append("Apply noise reduction")
            
            # THD assessment
            thd_score = max(1.0 - features.thd_percentage / 10, 0)  # Lower THD is better
            quality_assessment["quality_factors"]["harmonic_distortion"] = thd_score
            scores.append(thd_score)
            
            if thd_score < 0.7:
                quality_assessment["issues_detected"].append("High harmonic distortion")
                quality_assessment["improvement_suggestions"].append("Check recording levels, reduce distortion")
            
            # Frequency response assessment
            freq_score = features.frequency_response_flatness
            quality_assessment["quality_factors"]["frequency_response"] = freq_score
            scores.append(freq_score)
            
            if freq_score < 0.6:
                quality_assessment["issues_detected"].append("Unbalanced frequency response")
                quality_assessment["improvement_suggestions"].append("Apply EQ correction")
            
            # Overall score
            quality_assessment["overall_score"] = np.mean(scores)
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            quality_assessment["overall_score"] = 0.5  # Default to medium quality
        
        return quality_assessment
    
    async def _technical_analysis(self, features: AudioFeatures) -> Dict[str, Any]:
        """Technical analysis of audio properties"""
        return {
            "format_info": {
                "duration_seconds": features.duration_seconds,
                "sample_rate": features.sample_rate,
                "channels": features.channels,
                "bit_depth": features.bit_depth
            },
            "spectral_properties": {
                "bandwidth": float(np.mean(features.spectral_bandwidth)) if len(features.spectral_bandwidth) > 0 else 0.0,
                "centroid": float(np.mean(features.spectral_centroid)) if len(features.spectral_centroid) > 0 else 0.0,
                "rolloff": float(np.mean(features.spectral_rolloff)) if len(features.spectral_rolloff) > 0 else 0.0
            },
            "rhythmic_properties": {
                "tempo_bpm": features.tempo,
                "rhythm_regularity": features.rhythm_regularity,
                "beat_count": len(features.beats)
            },
            "energy_properties": {
                "rms_energy": float(np.mean(features.rms_energy)) if len(features.rms_energy) > 0 else 0.0,
                "zero_crossing_rate": float(np.mean(features.zero_crossing_rate)) if len(features.zero_crossing_rate) > 0 else 0.0
            }
        }
    
    async def _generate_recommendations(self, features: AudioFeatures) -> List[str]:
        """Generate recommendations for audio improvement"""
        recommendations = []
        
        # Quality-based recommendations
        if features.dynamic_range < 0.5:
            recommendations.append("Consider reducing compression to increase dynamic range")
        
        if features.snr_db < 30:
            recommendations.append("Apply noise reduction to improve signal-to-noise ratio")
        
        if features.thd_percentage > 5:
            recommendations.append("Check recording levels to reduce harmonic distortion")
        
        # Content-based recommendations
        if features.tempo > 0:
            if features.tempo < 60:
                recommendations.append("Consider increasing tempo for more energy")
            elif features.tempo > 180:
                recommendations.append("Consider slowing down tempo for better listenability")
        
        # Spectral recommendations
        if hasattr(features, 'spectral_centroid') and len(features.spectral_centroid) > 0:
            avg_centroid = np.mean(features.spectral_centroid)
            if avg_centroid < 1000:
                recommendations.append("Add high-frequency content for more brightness")
            elif avg_centroid > 5000:
                recommendations.append("Consider reducing harsh high frequencies")
        
        return recommendations

    async def compare_audio_similarity(self, 
                                     features1: AudioFeatures, 
                                     features2: AudioFeatures) -> Dict[str, float]:
        """Compare similarity between two audio tracks"""
        similarity_metrics = {}
        
        try:
            # Tempo similarity
            tempo_diff = abs(features1.tempo - features2.tempo)
            tempo_similarity = max(0, 1 - tempo_diff / 100)  # Normalize by 100 BPM
            similarity_metrics["tempo_similarity"] = tempo_similarity
            
            # Spectral similarity
            if (len(features1.spectral_centroid) > 0 and len(features2.spectral_centroid) > 0):
                centroid1 = np.mean(features1.spectral_centroid)
                centroid2 = np.mean(features2.spectral_centroid)
                centroid_diff = abs(centroid1 - centroid2)
                spectral_similarity = max(0, 1 - centroid_diff / 5000)  # Normalize by 5kHz
                similarity_metrics["spectral_similarity"] = spectral_similarity
            
            # MFCC similarity (if available)
            if (features1.mfcc.size > 0 and features2.mfcc.size > 0):
                # Calculate cosine similarity between MFCC means
                mfcc1_mean = np.mean(features1.mfcc, axis=1)
                mfcc2_mean = np.mean(features2.mfcc, axis=1)
                
                cosine_sim = np.dot(mfcc1_mean, mfcc2_mean) / (
                    np.linalg.norm(mfcc1_mean) * np.linalg.norm(mfcc2_mean) + 1e-10
                )
                similarity_metrics["mfcc_similarity"] = float(cosine_sim)
            
            # Overall similarity (weighted average)
            weights = {"tempo": 0.2, "spectral": 0.4, "mfcc": 0.4}
            overall_similarity = 0.0
            weight_sum = 0.0
            
            if "tempo_similarity" in similarity_metrics:
                overall_similarity += similarity_metrics["tempo_similarity"] * weights["tempo"]
                weight_sum += weights["tempo"]
            
            if "spectral_similarity" in similarity_metrics:
                overall_similarity += similarity_metrics["spectral_similarity"] * weights["spectral"]
                weight_sum += weights["spectral"]
            
            if "mfcc_similarity" in similarity_metrics:
                overall_similarity += similarity_metrics["mfcc_similarity"] * weights["mfcc"]
                weight_sum += weights["mfcc"]
            
            if weight_sum > 0:
                similarity_metrics["overall_similarity"] = overall_similarity / weight_sum
            
        except Exception as e:
            logger.error(f"Audio similarity comparison failed: {e}")
            similarity_metrics["overall_similarity"] = 0.0
        
        return similarity_metrics
