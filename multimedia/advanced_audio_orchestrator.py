#!/usr/bin/env python3
"""
Advanced Real-Time Audio Processing Orchestrator for Ainflue Platform
Enterprise-grade audio processing with ML-powered enhancement and analysis
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
import librosa
import soundfile as sf
import torch
import torch.nn as nn
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json
import time
from datetime import datetime
import threading
import queue
import subprocess
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor
import redis
import uuid
from scipy import signal
from scipy.fftpack import fft, ifft
import warnings
warnings.filterwarnings('ignore')

@dataclass
class AudioConfig:
    """Audio processing configuration"""
    sample_rate: int = 44100
    bit_depth: int = 16
    channels: int = 2
    chunk_size: int = 1024
    buffer_size: int = 4096
    max_latency_ms: float = 10.0
    enable_ml_enhancement: bool = True
    enable_real_time: bool = True
    
@dataclass
class AudioMetadata:
    """Audio file metadata"""
    filename: str
    duration_seconds: float
    sample_rate: int
    channels: int
    bit_rate: int
    format: str
    size_bytes: int
    codec: str
    fingerprint: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    
@dataclass
class ProcessingResult:
    """Audio processing result"""
    processing_id: str
    input_file: str
    output_file: str
    processing_time_ms: float
    enhancements_applied: List[str]
    quality_metrics: Dict[str, float]
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[AudioMetadata] = None

class AudioEnhancementML:
    """ML-powered audio enhancement"""
    
    def __init__(self, device: str = 'cpu'):
        self.device = device
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained audio enhancement models"""
        try:
            # Placeholder for real ML models
            # In production, these would be actual trained models
            self.models = {
                'noise_reduction': self._create_noise_reduction_model(),
                'enhancement': self._create_enhancement_model(),
                'voice_isolation': self._create_voice_isolation_model()
            }
            self.logger.info("Audio ML models loaded successfully")
        except Exception as e:
            self.logger.warning(f"Failed to load some ML models: {e}")
    
    def _create_noise_reduction_model(self) -> nn.Module:
        """Create noise reduction model"""
        class NoiseReductionModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.encoder = nn.Sequential(
                    nn.Conv1d(1, 64, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.Conv1d(64, 128, kernel_size=3, padding=1),
                    nn.ReLU()
                )
                self.decoder = nn.Sequential(
                    nn.Conv1d(128, 64, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.Conv1d(64, 1, kernel_size=3, padding=1),
                    nn.Tanh()
                )
            
            def forward(self, x):
                encoded = self.encoder(x)
                decoded = self.decoder(encoded)
                return decoded
        
        return NoiseReductionModel().to(self.device)
    
    def _create_enhancement_model(self) -> nn.Module:
        """Create audio enhancement model"""
        class AudioEnhancementModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.network = nn.Sequential(
                    nn.Linear(1024, 512),
                    nn.ReLU(),
                    nn.Linear(512, 256),
                    nn.ReLU(),
                    nn.Linear(256, 1024),
                    nn.Sigmoid()
                )
            
            def forward(self, x):
                return self.network(x)
        
        return AudioEnhancementModel().to(self.device)
    
    def _create_voice_isolation_model(self) -> nn.Module:
        """Create voice isolation model"""
        class VoiceIsolationModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.separator = nn.Sequential(
                    nn.Conv2d(1, 32, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.Conv2d(32, 64, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.Conv2d(64, 2, kernel_size=3, padding=1),
                    nn.Softmax(dim=1)
                )
            
            def forward(self, x):
                return self.separator(x)
        
        return VoiceIsolationModel().to(self.device)
    
    async def enhance_audio(self, audio_data: np.ndarray, 
                          enhancement_type: str = 'general') -> np.ndarray:
        """Apply ML-based audio enhancement"""
        try:
            if enhancement_type == 'noise_reduction':
                return await self._apply_noise_reduction(audio_data)
            elif enhancement_type == 'voice_isolation':
                return await self._apply_voice_isolation(audio_data)
            else:
                return await self._apply_general_enhancement(audio_data)
        except Exception as e:
            self.logger.error(f"Audio enhancement failed: {e}")
            return audio_data  # Return original if enhancement fails
    
    async def _apply_noise_reduction(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply noise reduction using ML model"""
        if 'noise_reduction' not in self.models:
            return audio_data
        
        model = self.models['noise_reduction']
        model.eval()
        
        with torch.no_grad():
            # Prepare input
            audio_tensor = torch.FloatTensor(audio_data).unsqueeze(0).unsqueeze(0)
            audio_tensor = audio_tensor.to(self.device)
            
            # Apply model
            enhanced = model(audio_tensor)
            
            # Convert back to numpy
            enhanced_audio = enhanced.squeeze().cpu().numpy()
            
        return enhanced_audio
    
    async def _apply_voice_isolation(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply voice isolation using ML model"""
        # Convert to spectrogram
        stft = librosa.stft(audio_data)
        magnitude = np.abs(stft)
        
        # Apply spectral processing (simplified)
        voice_mask = magnitude > np.mean(magnitude) * 1.5
        isolated_stft = stft * voice_mask
        
        # Convert back to audio
        isolated_audio = librosa.istft(isolated_stft)
        return isolated_audio
    
    async def _apply_general_enhancement(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply general audio enhancement"""
        # Apply dynamic range compression
        compressed = self._dynamic_range_compression(audio_data)
        
        # Apply EQ enhancement
        equalized = self._apply_eq_enhancement(compressed)
        
        return equalized
    
    def _dynamic_range_compression(self, audio_data: np.ndarray, 
                                 threshold: float = 0.3, ratio: float = 4.0) -> np.ndarray:
        """Apply dynamic range compression"""
        compressed = np.copy(audio_data)
        
        # Find samples above threshold
        above_threshold = np.abs(compressed) > threshold
        
        # Apply compression
        compressed[above_threshold] = np.sign(compressed[above_threshold]) * (
            threshold + (np.abs(compressed[above_threshold]) - threshold) / ratio
        )
        
        return compressed
    
    def _apply_eq_enhancement(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply EQ enhancement"""
        # Simple high-pass filter to remove low-frequency noise
        sos = signal.butter(4, 80, 'hp', fs=44100, output='sos')
        filtered = signal.sosfilt(sos, audio_data)
        
        return filtered

class AudioFingerprinting:
    """Advanced audio fingerprinting for content identification"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def generate_fingerprint(self, audio_data: np.ndarray, 
                                 sample_rate: int = 44100) -> str:
        """Generate audio fingerprint"""
        try:
            # Extract features
            features = await self._extract_audio_features(audio_data, sample_rate)
            
            # Create fingerprint hash
            fingerprint = self._create_fingerprint_hash(features)
            
            return fingerprint
        except Exception as e:
            self.logger.error(f"Fingerprinting failed: {e}")
            return ""
    
    async def _extract_audio_features(self, audio_data: np.ndarray, 
                                    sample_rate: int) -> Dict[str, Any]:
        """Extract audio features for fingerprinting"""
        features = {}
        
        # Spectral features
        stft = librosa.stft(audio_data)
        features['spectral_centroid'] = librosa.feature.spectral_centroid(
            S=np.abs(stft), sr=sample_rate
        ).mean()
        
        features['spectral_bandwidth'] = librosa.feature.spectral_bandwidth(
            S=np.abs(stft), sr=sample_rate
        ).mean()
        
        features['spectral_rolloff'] = librosa.feature.spectral_rolloff(
            S=np.abs(stft), sr=sample_rate
        ).mean()
        
        # MFCC features
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        features['mfcc_mean'] = mfccs.mean(axis=1).tolist()
        
        # Tempo and rhythm
        tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
        features['tempo'] = float(tempo)
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio_data)
        features['zero_crossing_rate'] = zcr.mean()
        
        return features
    
    def _create_fingerprint_hash(self, features: Dict[str, Any]) -> str:
        """Create fingerprint hash from features"""
        import hashlib
        
        # Serialize features to string
        feature_string = json.dumps(features, sort_keys=True)
        
        # Create hash
        fingerprint = hashlib.sha256(feature_string.encode()).hexdigest()[:16]
        
        return fingerprint

class RealTimeAudioProcessor:
    """Real-time audio processing engine"""
    
    def __init__(self, config: AudioConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_processing = False
        self.audio_queue = queue.Queue(maxsize=100)
        self.result_queue = queue.Queue()
        self.enhancement_ml = AudioEnhancementML()
        self.fingerprinting = AudioFingerprinting()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def start_real_time_processing(self, 
                                       input_callback: Optional[Callable] = None,
                                       output_callback: Optional[Callable] = None):
        """Start real-time audio processing"""
        self.is_processing = True
        
        # Start processing threads
        processing_tasks = [
            asyncio.create_task(self._audio_input_loop(input_callback)),
            asyncio.create_task(self._audio_processing_loop()),
            asyncio.create_task(self._audio_output_loop(output_callback))
        ]
        
        self.logger.info("Real-time audio processing started")
        
        try:
            await asyncio.gather(*processing_tasks)
        except Exception as e:
            self.logger.error(f"Real-time processing error: {e}")
        finally:
            self.is_processing = False
    
    async def _audio_input_loop(self, input_callback: Optional[Callable]):
        """Audio input processing loop"""
        while self.is_processing:
            try:
                # Get audio data from callback or simulate
                if input_callback:
                    audio_chunk = await input_callback()
                else:
                    # Simulate audio input
                    await asyncio.sleep(self.config.chunk_size / self.config.sample_rate)
                    audio_chunk = np.random.randn(self.config.chunk_size).astype(np.float32) * 0.1
                
                # Add to processing queue
                if not self.audio_queue.full():
                    self.audio_queue.put(audio_chunk)
                else:
                    self.logger.warning("Audio input queue full, dropping chunk")
                    
            except Exception as e:
                self.logger.error(f"Audio input error: {e}")
                await asyncio.sleep(0.001)
    
    async def _audio_processing_loop(self):
        """Main audio processing loop"""
        while self.is_processing:
            try:
                # Get audio chunk from queue
                if not self.audio_queue.empty():
                    audio_chunk = self.audio_queue.get()
                    
                    # Process audio
                    processed_chunk = await self._process_audio_chunk(audio_chunk)
                    
                    # Add to output queue
                    self.result_queue.put(processed_chunk)
                else:
                    await asyncio.sleep(0.001)
                    
            except Exception as e:
                self.logger.error(f"Audio processing error: {e}")
                await asyncio.sleep(0.001)
    
    async def _audio_output_loop(self, output_callback: Optional[Callable]):
        """Audio output processing loop"""
        while self.is_processing:
            try:
                if not self.result_queue.empty():
                    processed_chunk = self.result_queue.get()
                    
                    if output_callback:
                        await output_callback(processed_chunk)
                else:
                    await asyncio.sleep(0.001)
                    
            except Exception as e:
                self.logger.error(f"Audio output error: {e}")
                await asyncio.sleep(0.001)
    
    async def _process_audio_chunk(self, audio_chunk: np.ndarray) -> np.ndarray:
        """Process individual audio chunk"""
        start_time = time.time()
        
        try:
            # Apply ML enhancement if enabled
            if self.config.enable_ml_enhancement:
                enhanced_chunk = await self.enhancement_ml.enhance_audio(
                    audio_chunk, 'general'
                )
            else:
                enhanced_chunk = audio_chunk
            
            # Check processing latency
            processing_time = (time.time() - start_time) * 1000
            if processing_time > self.config.max_latency_ms:
                self.logger.warning(f"Processing latency exceeded: {processing_time:.2f}ms")
            
            return enhanced_chunk
            
        except Exception as e:
            self.logger.error(f"Chunk processing failed: {e}")
            return audio_chunk
    
    def stop_processing(self):
        """Stop real-time processing"""
        self.is_processing = False
        self.logger.info("Real-time audio processing stopped")

class AudioFormatConverter:
    """High-performance audio format converter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_formats = ['wav', 'mp3', 'flac', 'aac', 'ogg', 'm4a']
    
    async def convert_format(self, input_path: Path, output_path: Path,
                           target_format: str, quality: str = 'high') -> bool:
        """Convert audio file format"""
        try:
            if target_format not in self.supported_formats:
                raise ValueError(f"Unsupported format: {target_format}")
            
            # Use ffmpeg for conversion
            quality_settings = {
                'low': ['-b:a', '128k'],
                'medium': ['-b:a', '256k'],
                'high': ['-b:a', '320k'],
                'lossless': ['-c:a', 'flac']
            }
            
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-y',  # Overwrite output file
                *quality_settings.get(quality, quality_settings['high']),
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"Converted {input_path} to {output_path}")
                return True
            else:
                self.logger.error(f"Conversion failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Format conversion error: {e}")
            return False

class AudioQualityAnalyzer:
    """Audio quality analysis and metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def analyze_quality(self, audio_data: np.ndarray, 
                            sample_rate: int) -> Dict[str, float]:
        """Analyze audio quality metrics"""
        metrics = {}
        
        try:
            # Signal-to-noise ratio
            metrics['snr_db'] = self._calculate_snr(audio_data)
            
            # Dynamic range
            metrics['dynamic_range_db'] = self._calculate_dynamic_range(audio_data)
            
            # Frequency response
            metrics['frequency_balance'] = self._analyze_frequency_response(
                audio_data, sample_rate
            )
            
            # Distortion metrics
            metrics['thd_percent'] = self._calculate_thd(audio_data, sample_rate)
            
            # Loudness metrics
            metrics['lufs'] = self._calculate_lufs(audio_data, sample_rate)
            
            # Peak levels
            metrics['peak_db'] = 20 * np.log10(np.max(np.abs(audio_data)) + 1e-10)
            
            # RMS level
            metrics['rms_db'] = 20 * np.log10(np.sqrt(np.mean(audio_data**2)) + 1e-10)
            
        except Exception as e:
            self.logger.error(f"Quality analysis failed: {e}")
        
        return metrics
    
    def _calculate_snr(self, audio_data: np.ndarray) -> float:
        """Calculate signal-to-noise ratio"""
        # Simple SNR estimation
        signal_power = np.mean(audio_data**2)
        noise_floor = np.percentile(audio_data**2, 10)  # Bottom 10% as noise
        
        if noise_floor > 0:
            snr = 10 * np.log10(signal_power / noise_floor)
        else:
            snr = 100.0  # Very clean signal
        
        return float(snr)
    
    def _calculate_dynamic_range(self, audio_data: np.ndarray) -> float:
        """Calculate dynamic range"""
        peak = np.max(np.abs(audio_data))
        rms = np.sqrt(np.mean(audio_data**2))
        
        if rms > 0:
            dynamic_range = 20 * np.log10(peak / rms)
        else:
            dynamic_range = 0.0
        
        return float(dynamic_range)
    
    def _analyze_frequency_response(self, audio_data: np.ndarray, 
                                  sample_rate: int) -> float:
        """Analyze frequency response balance"""
        # Compute FFT
        fft_data = np.abs(fft(audio_data))
        freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)
        
        # Analyze frequency bands
        low_band = np.mean(fft_data[(freqs >= 20) & (freqs < 250)])
        mid_band = np.mean(fft_data[(freqs >= 250) & (freqs < 4000)])
        high_band = np.mean(fft_data[(freqs >= 4000) & (freqs < 20000)])
        
        # Calculate balance (closer to 1.0 is better)
        total_energy = low_band + mid_band + high_band
        if total_energy > 0:
            balance = 1.0 - np.std([low_band, mid_band, high_band]) / (total_energy / 3)
        else:
            balance = 0.0
        
        return float(balance)
    
    def _calculate_thd(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate Total Harmonic Distortion"""
        # Simplified THD calculation
        # In practice, this would require more sophisticated analysis
        fft_data = np.abs(fft(audio_data))
        
        # Find fundamental frequency (simplified)
        freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)
        fundamental_idx = np.argmax(fft_data[1:len(fft_data)//2]) + 1
        
        # Estimate harmonics
        harmonic_energy = 0
        fundamental_energy = fft_data[fundamental_idx]
        
        for harmonic in range(2, 6):  # Check first 4 harmonics
            harmonic_idx = fundamental_idx * harmonic
            if harmonic_idx < len(fft_data):
                harmonic_energy += fft_data[harmonic_idx]**2
        
        if fundamental_energy > 0:
            thd = np.sqrt(harmonic_energy) / fundamental_energy * 100
        else:
            thd = 0.0
        
        return float(min(thd, 100.0))  # Cap at 100%
    
    def _calculate_lufs(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate LUFS (Loudness Units relative to Full Scale)"""
        # Simplified LUFS calculation
        # Real implementation would use proper K-weighting filter
        
        # Apply basic filtering
        sos = signal.butter(2, [20, 20000], 'band', fs=sample_rate, output='sos')
        filtered = signal.sosfilt(sos, audio_data)
        
        # Calculate mean square
        mean_square = np.mean(filtered**2)
        
        if mean_square > 0:
            lufs = -0.691 + 10 * np.log10(mean_square)
        else:
            lufs = -100.0
        
        return float(lufs)

class AdvancedAudioOrchestrator:
    """Main orchestrator for advanced audio processing"""
    
    def __init__(self, config: AudioConfig, redis_host: str = 'localhost'):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.redis_client = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)
        
        # Initialize components
        self.ml_enhancement = AudioEnhancementML()
        self.fingerprinting = AudioFingerprinting()
        self.format_converter = AudioFormatConverter()
        self.quality_analyzer = AudioQualityAnalyzer()
        self.real_time_processor = RealTimeAudioProcessor(config)
        
        # Processing metrics
        self.processing_stats = {
            'total_processed': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0,
            'errors': 0
        }
    
    async def process_audio_file(self, input_path: Path, 
                               enhancements: List[str] = None,
                               output_format: str = None) -> ProcessingResult:
        """Process audio file with specified enhancements"""
        processing_id = str(uuid.uuid4())
        start_time = time.time()
        
        self.logger.info(f"Processing audio file: {input_path} (ID: {processing_id})")
        
        try:
            # Load audio file
            audio_data, sample_rate = librosa.load(str(input_path), sr=self.config.sample_rate)
            
            # Extract metadata
            metadata = await self._extract_metadata(input_path, audio_data, sample_rate)
            
            # Apply enhancements
            enhanced_audio = audio_data
            applied_enhancements = []
            
            if enhancements:
                for enhancement in enhancements:
                    enhanced_audio = await self.ml_enhancement.enhance_audio(
                        enhanced_audio, enhancement
                    )
                    applied_enhancements.append(enhancement)
            
            # Analyze quality
            quality_metrics = await self.quality_analyzer.analyze_quality(
                enhanced_audio, sample_rate
            )
            
            # Save processed audio
            output_path = self._generate_output_path(input_path, output_format)
            sf.write(str(output_path), enhanced_audio, sample_rate)
            
            # Convert format if requested
            if output_format and output_format != 'wav':
                converted_path = output_path.with_suffix(f'.{output_format}')
                await self.format_converter.convert_format(
                    output_path, converted_path, output_format
                )
                output_path = converted_path
            
            # Update statistics
            processing_time = (time.time() - start_time) * 1000
            self._update_stats(processing_time, True)
            
            # Cache result
            await self._cache_processing_result(processing_id, {
                'input_file': str(input_path),
                'output_file': str(output_path),
                'processing_time_ms': processing_time,
                'enhancements': applied_enhancements,
                'quality_metrics': quality_metrics
            })
            
            return ProcessingResult(
                processing_id=processing_id,
                input_file=str(input_path),
                output_file=str(output_path),
                processing_time_ms=processing_time,
                enhancements_applied=applied_enhancements,
                quality_metrics=quality_metrics,
                success=True,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Audio processing failed: {e}")
            self._update_stats(0, False)
            
            return ProcessingResult(
                processing_id=processing_id,
                input_file=str(input_path),
                output_file="",
                processing_time_ms=(time.time() - start_time) * 1000,
                enhancements_applied=[],
                quality_metrics={},
                success=False,
                error_message=str(e)
            )
    
    async def _extract_metadata(self, file_path: Path, audio_data: np.ndarray,
                              sample_rate: int) -> AudioMetadata:
        """Extract comprehensive audio metadata"""
        try:
            # Get file info
            file_stats = file_path.stat()
            
            # Generate fingerprint
            fingerprint = await self.fingerprinting.generate_fingerprint(
                audio_data, sample_rate
            )
            
            # Detect format and codec
            format_info = self._detect_audio_format(file_path)
            
            return AudioMetadata(
                filename=file_path.name,
                duration_seconds=len(audio_data) / sample_rate,
                sample_rate=sample_rate,
                channels=1 if audio_data.ndim == 1 else audio_data.shape[1],
                bit_rate=self._estimate_bitrate(file_stats.st_size, len(audio_data) / sample_rate),
                format=format_info['format'],
                size_bytes=file_stats.st_size,
                codec=format_info['codec'],
                fingerprint=fingerprint
            )
            
        except Exception as e:
            self.logger.warning(f"Metadata extraction failed: {e}")
            return AudioMetadata(
                filename=file_path.name,
                duration_seconds=0.0,
                sample_rate=sample_rate,
                channels=1,
                bit_rate=0,
                format="unknown",
                size_bytes=0,
                codec="unknown",
                fingerprint=""
            )
    
    def _detect_audio_format(self, file_path: Path) -> Dict[str, str]:
        """Detect audio format and codec"""
        suffix = file_path.suffix.lower()
        
        format_map = {
            '.wav': {'format': 'WAV', 'codec': 'PCM'},
            '.mp3': {'format': 'MP3', 'codec': 'MP3'},
            '.flac': {'format': 'FLAC', 'codec': 'FLAC'},
            '.aac': {'format': 'AAC', 'codec': 'AAC'},
            '.ogg': {'format': 'OGG', 'codec': 'Vorbis'},
            '.m4a': {'format': 'M4A', 'codec': 'AAC'}
        }
        
        return format_map.get(suffix, {'format': 'Unknown', 'codec': 'Unknown'})
    
    def _estimate_bitrate(self, file_size_bytes: int, duration_seconds: float) -> int:
        """Estimate audio bitrate"""
        if duration_seconds > 0:
            return int((file_size_bytes * 8) / duration_seconds)
        return 0
    
    def _generate_output_path(self, input_path: Path, output_format: str = None) -> Path:
        """Generate output file path"""
        output_dir = input_path.parent / "processed"
        output_dir.mkdir(exist_ok=True)
        
        if output_format:
            suffix = f".{output_format}"
        else:
            suffix = input_path.suffix
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"{input_path.stem}_processed_{timestamp}{suffix}"
        
        return output_dir / output_name
    
    def _update_stats(self, processing_time: float, success: bool):
        """Update processing statistics"""
        self.processing_stats['total_processed'] += 1
        
        if success:
            self.processing_stats['total_processing_time'] += processing_time
            self.processing_stats['average_processing_time'] = (
                self.processing_stats['total_processing_time'] / 
                self.processing_stats['total_processed']
            )
        else:
            self.processing_stats['errors'] += 1
    
    async def _cache_processing_result(self, processing_id: str, result_data: Dict[str, Any]):
        """Cache processing result in Redis"""
        try:
            cache_key = f"audio_processing:{processing_id}"
            self.redis_client.setex(
                cache_key, 
                3600,  # 1 hour TTL
                json.dumps(result_data, default=str)
            )
        except Exception as e:
            self.logger.warning(f"Failed to cache result: {e}")
    
    async def start_real_time_processing(self):
        """Start real-time audio processing"""
        await self.real_time_processor.start_real_time_processing()
    
    def stop_real_time_processing(self):
        """Stop real-time audio processing"""
        self.real_time_processor.stop_processing()
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.processing_stats,
            'success_rate': (
                (self.processing_stats['total_processed'] - self.processing_stats['errors']) / 
                self.processing_stats['total_processed'] * 100
            ) if self.processing_stats['total_processed'] > 0 else 0
        }

# Example usage and testing
async def main():
    """Example usage of advanced audio orchestrator"""
    
    # Configuration
    config = AudioConfig(
        sample_rate=44100,
        bit_depth=16,
        channels=2,
        enable_ml_enhancement=True,
        enable_real_time=True
    )
    
    # Initialize orchestrator
    orchestrator = AdvancedAudioOrchestrator(config)
    
    print("🎵 Advanced Audio Processing Orchestrator - Demo")
    
    # Test with a sample audio file (create if needed)
    test_audio_path = Path("test_audio.wav")
    if not test_audio_path.exists():
        # Generate test audio
        sample_rate = 44100
        duration = 3  # seconds
        t = np.linspace(0, duration, int(sample_rate * duration))
        test_audio = 0.3 * np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
        sf.write(str(test_audio_path), test_audio, sample_rate)
        print(f"✅ Created test audio file: {test_audio_path}")
    
    # Process audio file
    enhancements = ['noise_reduction', 'general']
    result = await orchestrator.process_audio_file(
        test_audio_path,
        enhancements=enhancements,
        output_format='wav'
    )
    
    if result.success:
        print(f"✅ Audio processing successful!")
        print(f"   Input: {result.input_file}")
        print(f"   Output: {result.output_file}")
        print(f"   Processing time: {result.processing_time_ms:.2f}ms")
        print(f"   Enhancements: {result.enhancements_applied}")
        print(f"   Quality metrics: {result.quality_metrics}")
    else:
        print(f"❌ Audio processing failed: {result.error_message}")
    
    # Get statistics
    stats = orchestrator.get_processing_stats()
    print(f"✅ Processing stats: {stats}")
    
    # Clean up test file
    if test_audio_path.exists():
        test_audio_path.unlink()

if __name__ == "__main__":
    asyncio.run(main())