"""Advanced Audio Analytics Engine
Professional audio analysis, spectral processing, and quality assessment.

This module provides comprehensive audio analytics including spectral analysis,
quality assessment, music information retrieval, and real-time audio metrics.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

⚠️ COPYRIGHT PROTECTION ⚠️
This code is proprietary and confidential. Unauthorized use is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import numpy as np
import librosa
import soundfile as sf
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from scipy import signal
from scipy.stats import entropy

logger = logging.getLogger(__name__)

@dataclass
class AudioMetrics:
    """Comprehensive audio metrics data structure"""
    file_path: str
    duration: float
    sample_rate: int
    channels: int
    bit_depth: Optional[int] = None
    
    # Quality metrics
    quality_score: float = 0.0
    dynamic_range: float = 0.0
    snr_estimate: float = 0.0
    
    # Spectral features
    spectral_centroid: float = 0.0
    spectral_bandwidth: float = 0.0
    spectral_rolloff: float = 0.0
    zero_crossing_rate: float = 0.0
    
    # Musical features
    tempo: Optional[float] = None
    key: Optional[str] = None
    mode: Optional[str] = None
    energy: float = 0.0
    
    # Frequency analysis
    frequency_distribution: Dict[str, float] = field(default_factory=dict)
    dominant_frequencies: List[float] = field(default_factory=list)
    
    # Perceptual features
    loudness_lufs: Optional[float] = None
    loudness_range: Optional[float] = None
    true_peak: Optional[float] = None
    
    # Anomaly detection
    anomalies_detected: List[Dict[str, Any]] = field(default_factory=list)
    
    # Processing metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0


class SpectrogramAnalyzer:
    """Advanced spectrogram analysis and visualization"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Spectrogram parameters
        self.n_fft = self.config.get('n_fft', 2048)
        self.hop_length = self.config.get('hop_length', 512)
        self.window = self.config.get('window', 'hann')
        
    async def generate_spectrogram(self, audio: np.ndarray, sr: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate mel-scale spectrogram"""
        try:
            # Compute mel-scale spectrogram
            mel_spec = librosa.feature.melspectrogram(
                y=audio, sr=sr, n_fft=self.n_fft, 
                hop_length=self.hop_length, window=self.window
            )
            
            # Convert to dB scale
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Time and frequency axes
            times = librosa.frames_to_time(np.arange(mel_spec.shape[1]), sr=sr, hop_length=self.hop_length)
            freqs = librosa.mel_frequencies(n_mels=mel_spec.shape[0])
            
            return mel_spec_db, times, freqs
            
        except Exception as e:
            self.logger.error(f"Spectrogram generation failed: {e}")
            raise
    
    async def analyze_spectral_patterns(self, spectrogram: np.ndarray) -> Dict[str, Any]:
        """Analyze spectral patterns and features"""
        try:
            patterns = {}
            
            # Spectral centroid variation
            spectral_centroids = np.mean(spectrogram * np.arange(spectrogram.shape[0])[:, np.newaxis], axis=0)
            patterns['centroid_stability'] = float(np.std(spectral_centroids))
            
            # Energy distribution across frequency bands
            low_freq = np.mean(spectrogram[:spectrogram.shape[0]//4, :])
            mid_freq = np.mean(spectrogram[spectrogram.shape[0]//4:3*spectrogram.shape[0]//4, :])
            high_freq = np.mean(spectrogram[3*spectrogram.shape[0]//4:, :])
            
            patterns['frequency_distribution'] = {
                'low_frequency_energy': float(low_freq),
                'mid_frequency_energy': float(mid_freq),
                'high_frequency_energy': float(high_freq)
            }
            
            # Temporal patterns
            energy_variation = np.std(np.mean(spectrogram, axis=0))
            patterns['temporal_stability'] = float(energy_variation)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Spectral pattern analysis failed: {e}")
            return {}


class AudioAnalyzer:
    """Comprehensive audio analysis engine"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        self.spectrogram_analyzer = SpectrogramAnalyzer(config)
        
        # Analysis parameters
        self.quality_threshold = self.config.get('quality_threshold', 0.7)
        self.enable_music_analysis = self.config.get('enable_music_analysis', True)
        self.enable_anomaly_detection = self.config.get('enable_anomaly_detection', True)
        
    async def analyze_file(self, file_path: str) -> AudioMetrics:
        """Comprehensive audio file analysis"""
        start_time = datetime.now()
        
        try:
            # Load audio file
            audio, sr = await self._load_audio(file_path)
            
            # Initialize metrics
            metrics = AudioMetrics(
                file_path=file_path,
                duration=len(audio) / sr,
                sample_rate=sr,
                channels=1 if audio.ndim == 1 else audio.shape[0]
            )
            
            # Basic quality assessment
            await self._analyze_quality(audio, sr, metrics)
            
            # Spectral analysis
            await self._analyze_spectral_features(audio, sr, metrics)
            
            # Musical analysis
            if self.enable_music_analysis:
                await self._analyze_musical_features(audio, sr, metrics)
            
            # Anomaly detection
            if self.enable_anomaly_detection:
                await self._detect_anomalies(audio, sr, metrics)
            
            # Calculate processing time
            metrics.processing_time = (datetime.now() - start_time).total_seconds()
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Audio analysis failed for {file_path}: {e}")
            raise
    
    async def _load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Load and preprocess audio file"""
        try:
            # Load with librosa for consistent preprocessing
            audio, sr = librosa.load(file_path, sr=None, mono=True)
            
            # Normalize audio
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio))
            
            return audio, sr
            
        except Exception as e:
            self.logger.error(f"Failed to load audio file {file_path}: {e}")
            raise
    
    async def _analyze_quality(self, audio: np.ndarray, sr: int, metrics: AudioMetrics) -> None:
        """Analyze audio quality metrics"""
        try:
            # Dynamic range
            rms = np.sqrt(np.mean(audio**2))
            peak = np.max(np.abs(audio))
            metrics.dynamic_range = float(20 * np.log10(peak / (rms + 1e-10)))
            
            # SNR estimation (simple)
            signal_power = np.mean(audio**2)
            # Estimate noise from quiet segments
            audio_abs = np.abs(audio)
            noise_threshold = np.percentile(audio_abs, 10)
            noise_segments = audio[audio_abs <= noise_threshold]
            noise_power = np.mean(noise_segments**2) if len(noise_segments) > 0 else 1e-10
            
            metrics.snr_estimate = float(10 * np.log10(signal_power / (noise_power + 1e-10)))
            
            # Overall quality score (composite metric)
            quality_factors = [
                min(metrics.dynamic_range / 40.0, 1.0),  # Normalize to 0-1
                min(metrics.snr_estimate / 30.0, 1.0),   # Normalize to 0-1
                1.0 - min(np.mean(np.abs(np.diff(audio))), 1.0)  # Smoothness
            ]
            metrics.quality_score = float(np.mean(quality_factors))
            
        except Exception as e:
            self.logger.error(f"Quality analysis failed: {e}")
    
    async def _analyze_spectral_features(self, audio: np.ndarray, sr: int, metrics: AudioMetrics) -> None:
        """Analyze spectral characteristics"""
        try:
            # Spectral centroid
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            metrics.spectral_centroid = float(np.mean(spectral_centroids))
            
            # Spectral bandwidth
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)[0]
            metrics.spectral_bandwidth = float(np.mean(spectral_bandwidth))
            
            # Spectral rolloff
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
            metrics.spectral_rolloff = float(np.mean(spectral_rolloff))
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio)[0]
            metrics.zero_crossing_rate = float(np.mean(zcr))
            
            # Frequency distribution analysis
            fft = np.fft.fft(audio)
            freqs = np.fft.fftfreq(len(fft), 1/sr)
            magnitude = np.abs(fft)
            
            # Frequency bands
            low_band = magnitude[(freqs >= 20) & (freqs < 250)]
            mid_band = magnitude[(freqs >= 250) & (freqs < 4000)]
            high_band = magnitude[(freqs >= 4000) & (freqs < sr//2)]
            
            total_energy = np.sum(magnitude)
            if total_energy > 0:
                metrics.frequency_distribution = {
                    'low_frequency': float(np.sum(low_band) / total_energy),
                    'mid_frequency': float(np.sum(mid_band) / total_energy),
                    'high_frequency': float(np.sum(high_band) / total_energy)
                }
            
            # Find dominant frequencies
            peak_indices = signal.find_peaks(magnitude, height=np.max(magnitude) * 0.1)[0]
            dominant_freqs = freqs[peak_indices]
            metrics.dominant_frequencies = [float(f) for f in dominant_freqs[:10]]  # Top 10
            
        except Exception as e:
            self.logger.error(f"Spectral analysis failed: {e}")
    
    async def _analyze_musical_features(self, audio: np.ndarray, sr: int, metrics: AudioMetrics) -> None:
        """Analyze musical characteristics"""
        try:
            # Tempo estimation
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
            metrics.tempo = float(tempo)
            
            # Energy
            metrics.energy = float(np.sum(audio**2))
            
            # Key estimation (simplified)
            chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
            key_strength = np.mean(chroma, axis=1)
            key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            estimated_key = key_names[np.argmax(key_strength)]
            metrics.key = estimated_key
            
        except Exception as e:
            self.logger.error(f"Musical analysis failed: {e}")
    
    async def _detect_anomalies(self, audio: np.ndarray, sr: int, metrics: AudioMetrics) -> None:
        """Detect audio anomalies and artifacts"""
        try:
            anomalies = []
            
            # Detect clipping
            clipping_threshold = 0.99
            clipped_samples = np.sum(np.abs(audio) > clipping_threshold)
            if clipped_samples > len(audio) * 0.001:  # More than 0.1% clipped
                anomalies.append({
                    'type': 'clipping',
                    'severity': 'high' if clipped_samples > len(audio) * 0.01 else 'medium',
                    'affected_samples': int(clipped_samples),
                    'percentage': float(clipped_samples / len(audio) * 100)
                })
            
            # Detect silence
            silence_threshold = 0.001
            silent_samples = np.sum(np.abs(audio) < silence_threshold)
            if silent_samples > len(audio) * 0.1:  # More than 10% silence
                anomalies.append({
                    'type': 'excessive_silence',
                    'severity': 'medium',
                    'affected_samples': int(silent_samples),
                    'percentage': float(silent_samples / len(audio) * 100)
                })
            
            # Detect DC offset
            dc_offset = np.mean(audio)
            if abs(dc_offset) > 0.1:
                anomalies.append({
                    'type': 'dc_offset',
                    'severity': 'medium',
                    'offset_value': float(dc_offset)
                })
            
            metrics.anomalies_detected = anomalies
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
    
    async def batch_analyze(self, file_paths: List[str]) -> List[AudioMetrics]:
        """Analyze multiple audio files in parallel"""
        try:
            tasks = [self.analyze_file(path) for path in file_paths]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log errors
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Failed to analyze {file_paths[i]}: {result}")
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            self.logger.error(f"Batch analysis failed: {e}")
            return []