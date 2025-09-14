"""
Enterprise Audio Engine - Advanced Audio Processing & Distribution System
Author: Fahed Mlaiel (mlaiel@live.de)
Role: Audio Engineer + Multimedia Specialist + Content Processing Expert
Version: 2.0 Enterprise Production
"""

import asyncio
import logging
import json
import time
import math
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import os
import tempfile
import hashlib
import base64

# Audio processing imports
import librosa
import soundfile as sf
import pydub
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
import scipy.signal
import scipy.fft
from scipy.io import wavfile

# Machine learning for audio
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import tensorflow as tf

# Real-time audio processing
import threading
from collections import deque

class AudioFormat(Enum):
    """Supported audio formats"""
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    OPUS = "opus"

class AudioQuality(Enum):
    """Audio quality presets"""
    PHONE = "phone"       # 8kHz, mono, heavily compressed
    PODCAST = "podcast"   # 22kHz, mono, compressed
    MUSIC_LOW = "music_low"       # 44.1kHz, stereo, medium quality
    MUSIC_HIGH = "music_high"     # 44.1kHz, stereo, high quality
    PROFESSIONAL = "professional" # 48kHz, stereo, lossless
    BROADCAST = "broadcast"       # 48kHz, stereo, broadcast standards

class AudioEffect(Enum):
    """Audio effects"""
    NORMALIZE = "normalize"
    COMPRESS = "compress"
    EQ = "equalizer"
    REVERB = "reverb"
    DELAY = "delay"
    CHORUS = "chorus"
    DISTORTION = "distortion"
    NOISE_GATE = "noise_gate"
    LIMITER = "limiter"
    DUCKING = "ducking"

@dataclass
class AudioConfig:
    """Audio processing configuration"""
    sample_rate: int = 44100
    channels: int = 2
    bit_depth: int = 16
    format: AudioFormat = AudioFormat.WAV
    quality: AudioQuality = AudioQuality.MUSIC_HIGH
    normalize: bool = True
    compress: bool = False
    effects: List[AudioEffect] = field(default_factory=list)

@dataclass
class AudioMetadata:
    """Audio file metadata"""
    duration: float
    sample_rate: int
    channels: int
    bit_depth: int
    format: str
    file_size: int
    peak_level: float
    rms_level: float
    dynamic_range: float
    frequency_response: Dict[str, float]
    tempo: Optional[float] = None
    key: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None

@dataclass
class AudioAnalysis:
    """Audio analysis results"""
    metadata: AudioMetadata
    spectral_features: Dict[str, Any]
    rhythm_features: Dict[str, Any]
    harmonic_features: Dict[str, Any]
    quality_metrics: Dict[str, float]
    content_classification: Dict[str, float]
    platform_suitability: Dict[str, float]

class SpectralAnalyzer:
    """Advanced spectral analysis for audio content"""
    
    def __init__(self):
        self.window_size = 2048
        self.hop_length = 512
        self.mel_bins = 128
        
    def analyze_spectrum(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Perform comprehensive spectral analysis"""
        try:
            # Compute various spectral features
            spectral_features = {}
            
            # 1. Spectral centroid
            spectral_centroids = librosa.feature.spectral_centroid(
                y=audio_data, sr=sample_rate, hop_length=self.hop_length
            )[0]
            spectral_features['centroid_mean'] = float(np.mean(spectral_centroids))
            spectral_features['centroid_std'] = float(np.std(spectral_centroids))
            
            # 2. Spectral rolloff
            spectral_rolloff = librosa.feature.spectral_rolloff(
                y=audio_data, sr=sample_rate, hop_length=self.hop_length
            )[0]
            spectral_features['rolloff_mean'] = float(np.mean(spectral_rolloff))
            spectral_features['rolloff_std'] = float(np.std(spectral_rolloff))
            
            # 3. Spectral bandwidth
            spectral_bandwidth = librosa.feature.spectral_bandwidth(
                y=audio_data, sr=sample_rate, hop_length=self.hop_length
            )[0]
            spectral_features['bandwidth_mean'] = float(np.mean(spectral_bandwidth))
            spectral_features['bandwidth_std'] = float(np.std(spectral_bandwidth))
            
            # 4. Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(
                audio_data, hop_length=self.hop_length
            )[0]
            spectral_features['zcr_mean'] = float(np.mean(zcr))
            spectral_features['zcr_std'] = float(np.std(zcr))
            
            # 5. Mel-frequency cepstral coefficients (MFCCs)
            mfccs = librosa.feature.mfcc(
                y=audio_data, sr=sample_rate, n_mfcc=13, hop_length=self.hop_length
            )
            for i in range(13):
                spectral_features[f'mfcc_{i}_mean'] = float(np.mean(mfccs[i]))
                spectral_features[f'mfcc_{i}_std'] = float(np.std(mfccs[i]))
            
            # 6. Chroma features
            chroma = librosa.feature.chroma_stft(
                y=audio_data, sr=sample_rate, hop_length=self.hop_length
            )
            spectral_features['chroma_mean'] = float(np.mean(chroma))
            spectral_features['chroma_std'] = float(np.std(chroma))
            
            # 7. Spectral contrast
            contrast = librosa.feature.spectral_contrast(
                y=audio_data, sr=sample_rate, hop_length=self.hop_length
            )
            spectral_features['contrast_mean'] = float(np.mean(contrast))
            spectral_features['contrast_std'] = float(np.std(contrast))
            
            return spectral_features
            
        except Exception as e:
            logging.error(f"Spectral analysis failed: {str(e)}")
            return {}
    
    def analyze_frequency_response(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Analyze frequency response characteristics"""
        try:
            # Compute FFT
            fft = np.fft.rfft(audio_data)
            magnitude = np.abs(fft)
            
            # Frequency bins
            freqs = np.fft.rfftfreq(len(audio_data), 1/sample_rate)
            
            # Define frequency bands
            bands = {
                'sub_bass': (20, 60),
                'bass': (60, 250),
                'low_mid': (250, 500),
                'mid': (500, 2000),
                'high_mid': (2000, 4000),
                'presence': (4000, 6000),
                'brilliance': (6000, 20000)
            }
            
            frequency_response = {}
            
            for band_name, (low_freq, high_freq) in bands.items():
                # Find frequency indices
                low_idx = np.argmax(freqs >= low_freq)
                high_idx = np.argmax(freqs >= high_freq)
                
                if high_idx == 0:  # Handle case where high_freq is beyond Nyquist
                    high_idx = len(freqs) - 1
                
                # Calculate average magnitude in band
                band_magnitude = np.mean(magnitude[low_idx:high_idx])
                frequency_response[band_name] = float(20 * np.log10(band_magnitude + 1e-10))
            
            return frequency_response
            
        except Exception as e:
            logging.error(f"Frequency response analysis failed: {str(e)}")
            return {}

class RhythmAnalyzer:
    """Advanced rhythm and tempo analysis"""
    
    def __init__(self):
        self.tempo_min = 60
        self.tempo_max = 200
        
    def analyze_rhythm(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Analyze rhythm characteristics"""
        try:
            rhythm_features = {}
            
            # 1. Tempo estimation
            tempo, beats = librosa.beat.beat_track(
                y=audio_data, sr=sample_rate, start_bpm=120
            )
            rhythm_features['tempo'] = float(tempo)
            rhythm_features['beat_count'] = len(beats)
            
            # 2. Beat consistency
            if len(beats) > 1:
                beat_intervals = np.diff(beats) / sample_rate
                rhythm_features['beat_consistency'] = float(1.0 / (np.std(beat_intervals) + 1e-6))
            else:
                rhythm_features['beat_consistency'] = 0.0
            
            # 3. Onset detection
            onset_frames = librosa.onset.onset_detect(
                y=audio_data, sr=sample_rate, units='time'
            )
            rhythm_features['onset_density'] = len(onset_frames) / (len(audio_data) / sample_rate)
            
            # 4. Rhythmic regularity
            if len(onset_frames) > 2:
                onset_intervals = np.diff(onset_frames)
                rhythm_features['rhythmic_regularity'] = float(1.0 / (np.std(onset_intervals) + 1e-6))
            else:
                rhythm_features['rhythmic_regularity'] = 0.0
            
            # 5. Meter estimation (simplified)
            rhythm_features['meter_strength'] = self._estimate_meter_strength(beats, tempo)
            
            return rhythm_features
            
        except Exception as e:
            logging.error(f"Rhythm analysis failed: {str(e)}")
            return {}
    
    def _estimate_meter_strength(self, beats: np.ndarray, tempo: float) -> float:
        """Estimate meter strength (how strong the beat is)"""
        if len(beats) < 4:
            return 0.0
        
        # Calculate beat intervals
        intervals = np.diff(beats)
        
        # Look for regular patterns
        mean_interval = np.mean(intervals)
        variance = np.var(intervals)
        
        # Lower variance indicates stronger meter
        meter_strength = 1.0 / (1.0 + variance / (mean_interval + 1e-6))
        
        return float(meter_strength)

class HarmonicAnalyzer:
    """Advanced harmonic and tonal analysis"""
    
    def __init__(self):
        self.pitches = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
    def analyze_harmony(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Analyze harmonic characteristics"""
        try:
            harmonic_features = {}
            
            # 1. Pitch estimation
            pitches, magnitudes = librosa.piptrack(
                y=audio_data, sr=sample_rate, threshold=0.1
            )
            
            # Extract fundamental frequency
            fundamental_freqs = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    fundamental_freqs.append(pitch)
            
            if fundamental_freqs:
                harmonic_features['fundamental_freq_mean'] = float(np.mean(fundamental_freqs))
                harmonic_features['fundamental_freq_std'] = float(np.std(fundamental_freqs))
                
                # Estimate key
                harmonic_features['estimated_key'] = self._estimate_key(fundamental_freqs)
            else:
                harmonic_features['fundamental_freq_mean'] = 0.0
                harmonic_features['fundamental_freq_std'] = 0.0
                harmonic_features['estimated_key'] = 'Unknown'
            
            # 2. Harmonic-percussive separation
            harmonic, percussive = librosa.effects.hpss(audio_data)
            
            # Calculate harmonic/percussive ratio
            harmonic_energy = np.sum(harmonic ** 2)
            percussive_energy = np.sum(percussive ** 2)
            total_energy = harmonic_energy + percussive_energy
            
            if total_energy > 0:
                harmonic_features['harmonic_ratio'] = float(harmonic_energy / total_energy)
                harmonic_features['percussive_ratio'] = float(percussive_energy / total_energy)
            else:
                harmonic_features['harmonic_ratio'] = 0.0
                harmonic_features['percussive_ratio'] = 0.0
            
            # 3. Tonal centroid features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            harmonic_features['tonal_centroid'] = float(np.mean(chroma))
            
            # 4. Key strength
            harmonic_features['key_strength'] = self._calculate_key_strength(chroma)
            
            return harmonic_features
            
        except Exception as e:
            logging.error(f"Harmonic analysis failed: {str(e)}")
            return {}
    
    def _estimate_key(self, fundamental_freqs: List[float]) -> str:
        """Estimate musical key from fundamental frequencies"""
        if not fundamental_freqs:
            return 'Unknown'
        
        # Convert frequencies to pitch classes
        pitch_classes = []
        for freq in fundamental_freqs:
            if freq > 0:
                # Convert frequency to MIDI note
                midi_note = 69 + 12 * np.log2(freq / 440.0)
                pitch_class = int(midi_note) % 12
                pitch_classes.append(pitch_class)
        
        if not pitch_classes:
            return 'Unknown'
        
        # Count occurrences of each pitch class
        pitch_counts = np.bincount(pitch_classes, minlength=12)
        
        # Find most common pitch class
        most_common_pitch = np.argmax(pitch_counts)
        
        return self.pitches[most_common_pitch]
    
    def _calculate_key_strength(self, chroma: np.ndarray) -> float:
        """Calculate how strong the key signature is"""
        if chroma.size == 0:
            return 0.0
        
        # Calculate the variance across pitch classes
        pitch_variance = np.var(np.mean(chroma, axis=1))
        
        # Higher variance indicates stronger key signature
        return float(pitch_variance)

class AudioQualityAnalyzer:
    """Audio quality assessment and metrics"""
    
    def __init__(self):
        self.quality_thresholds = {
            'excellent': 0.9,
            'good': 0.7,
            'fair': 0.5,
            'poor': 0.3
        }
        
    def analyze_quality(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Comprehensive audio quality analysis"""
        try:
            quality_metrics = {}
            
            # 1. Signal-to-noise ratio
            quality_metrics['snr'] = self._calculate_snr(audio_data)
            
            # 2. Dynamic range
            quality_metrics['dynamic_range'] = self._calculate_dynamic_range(audio_data)
            
            # 3. Frequency response flatness
            quality_metrics['frequency_flatness'] = self._calculate_frequency_flatness(audio_data, sample_rate)
            
            # 4. Distortion estimation
            quality_metrics['thd'] = self._estimate_thd(audio_data, sample_rate)
            
            # 5. Clipping detection
            quality_metrics['clipping_ratio'] = self._detect_clipping(audio_data)
            
            # 6. Silence ratio
            quality_metrics['silence_ratio'] = self._calculate_silence_ratio(audio_data)
            
            # 7. Overall quality score
            quality_metrics['overall_quality'] = self._calculate_overall_quality(quality_metrics)
            
            return quality_metrics
            
        except Exception as e:
            logging.error(f"Quality analysis failed: {str(e)}")
            return {}
    
    def _calculate_snr(self, audio_data: np.ndarray) -> float:
        """Calculate signal-to-noise ratio"""
        if len(audio_data) == 0:
            return 0.0
        
        # Estimate noise floor (lowest 10% of signal)
        sorted_magnitudes = np.sort(np.abs(audio_data))
        noise_floor = np.mean(sorted_magnitudes[:int(len(sorted_magnitudes) * 0.1)])
        
        # Calculate signal power
        signal_power = np.mean(audio_data ** 2)
        noise_power = noise_floor ** 2
        
        if noise_power > 0:
            snr_db = 10 * np.log10(signal_power / noise_power)
            return float(max(0, min(60, snr_db)))  # Clamp between 0-60 dB
        
        return 60.0  # Maximum SNR if no noise detected
    
    def _calculate_dynamic_range(self, audio_data: np.ndarray) -> float:
        """Calculate dynamic range in dB"""
        if len(audio_data) == 0:
            return 0.0
        
        # Calculate RMS over time windows
        window_size = int(0.1 * 44100)  # 100ms windows
        rms_values = []
        
        for i in range(0, len(audio_data) - window_size, window_size):
            window = audio_data[i:i + window_size]
            rms = np.sqrt(np.mean(window ** 2))
            if rms > 0:
                rms_values.append(rms)
        
        if len(rms_values) > 0:
            max_rms = np.max(rms_values)
            min_rms = np.min(rms_values)
            
            if min_rms > 0:
                dynamic_range = 20 * np.log10(max_rms / min_rms)
                return float(max(0, min(80, dynamic_range)))  # Clamp between 0-80 dB
        
        return 0.0
    
    def _calculate_frequency_flatness(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate frequency response flatness"""
        if len(audio_data) == 0:
            return 0.0
        
        # Compute FFT
        fft = np.fft.rfft(audio_data)
        magnitude = np.abs(fft)
        
        # Focus on audible range (20Hz - 20kHz)
        freqs = np.fft.rfftfreq(len(audio_data), 1/sample_rate)
        audible_mask = (freqs >= 20) & (freqs <= 20000)
        
        if np.sum(audible_mask) > 0:
            audible_magnitude = magnitude[audible_mask]
            
            # Calculate variance (lower variance = flatter response)
            magnitude_db = 20 * np.log10(audible_magnitude + 1e-10)
            variance = np.var(magnitude_db)
            
            # Convert to flatness score (0-1, higher is flatter)
            flatness = 1.0 / (1.0 + variance / 100.0)
            return float(flatness)
        
        return 0.0
    
    def _estimate_thd(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Estimate Total Harmonic Distortion"""
        if len(audio_data) == 0:
            return 1.0
        
        # Simplified THD estimation using spectral analysis
        fft = np.fft.rfft(audio_data)
        magnitude = np.abs(fft)
        
        # Find the fundamental frequency (peak in spectrum)
        fundamental_idx = np.argmax(magnitude)
        fundamental_magnitude = magnitude[fundamental_idx]
        
        # Look for harmonics (2f, 3f, 4f, etc.)
        harmonic_energy = 0.0
        for harmonic in range(2, 6):  # Check up to 5th harmonic
            harmonic_idx = fundamental_idx * harmonic
            if harmonic_idx < len(magnitude):
                harmonic_energy += magnitude[harmonic_idx] ** 2
        
        # Calculate THD
        if fundamental_magnitude > 0:
            thd = np.sqrt(harmonic_energy) / fundamental_magnitude
            return float(min(1.0, thd))
        
        return 0.0
    
    def _detect_clipping(self, audio_data: np.ndarray) -> float:
        """Detect clipping in audio signal"""
        if len(audio_data) == 0:
            return 0.0
        
        # Normalize to [-1, 1] range
        max_value = np.max(np.abs(audio_data))
        if max_value > 0:
            normalized_audio = audio_data / max_value
        else:
            return 0.0
        
        # Count samples at or near clipping level
        clipping_threshold = 0.99
        clipped_samples = np.sum(np.abs(normalized_audio) >= clipping_threshold)
        
        clipping_ratio = clipped_samples / len(audio_data)
        return float(clipping_ratio)
    
    def _calculate_silence_ratio(self, audio_data: np.ndarray) -> float:
        """Calculate ratio of silence in audio"""
        if len(audio_data) == 0:
            return 1.0
        
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_data ** 2))
        
        # Define silence threshold (relative to max RMS)
        max_possible_rms = np.max(np.abs(audio_data))
        silence_threshold = max_possible_rms * 0.01  # 1% of max
        
        # Count silent samples
        silent_samples = np.sum(np.abs(audio_data) < silence_threshold)
        
        silence_ratio = silent_samples / len(audio_data)
        return float(silence_ratio)
    
    def _calculate_overall_quality(self, metrics: Dict[str, float]) -> float:
        """Calculate overall quality score from individual metrics"""
        if not metrics:
            return 0.0
        
        # Weighted combination of quality metrics
        weights = {
            'snr': 0.25,
            'dynamic_range': 0.20,
            'frequency_flatness': 0.15,
            'thd': 0.15,  # Lower THD is better
            'clipping_ratio': 0.15,  # Lower clipping is better
            'silence_ratio': 0.10   # Lower silence is usually better
        }
        
        quality_score = 0.0
        total_weight = 0.0
        
        for metric, weight in weights.items():
            if metric in metrics:
                if metric == 'snr':
                    # SNR: normalize 0-60 dB to 0-1
                    normalized = metrics[metric] / 60.0
                elif metric == 'dynamic_range':
                    # Dynamic range: normalize 0-80 dB to 0-1
                    normalized = metrics[metric] / 80.0
                elif metric == 'frequency_flatness':
                    # Already 0-1
                    normalized = metrics[metric]
                elif metric in ['thd', 'clipping_ratio', 'silence_ratio']:
                    # Lower is better: invert the score
                    normalized = 1.0 - min(1.0, metrics[metric])
                else:
                    normalized = metrics[metric]
                
                quality_score += weight * normalized
                total_weight += weight
        
        if total_weight > 0:
            return quality_score / total_weight
        
        return 0.0

class PlatformOptimizer:
    """Platform-specific audio optimization"""
    
    def __init__(self):
        self.platform_specs = {
            'instagram': {
                'max_duration': 60,  # seconds
                'sample_rate': 44100,
                'format': AudioFormat.MP3,
                'bitrate': 128,  # kbps
                'channels': 2,
                'loudness_target': -14  # LUFS
            },
            'tiktok': {
                'max_duration': 180,
                'sample_rate': 44100,
                'format': AudioFormat.MP3,
                'bitrate': 128,
                'channels': 2,
                'loudness_target': -14
            },
            'youtube': {
                'max_duration': None,  # No limit
                'sample_rate': 48000,
                'format': AudioFormat.AAC,
                'bitrate': 256,
                'channels': 2,
                'loudness_target': -23
            },
            'spotify': {
                'max_duration': None,
                'sample_rate': 44100,
                'format': AudioFormat.OGG,
                'bitrate': 320,
                'channels': 2,
                'loudness_target': -14
            },
            'podcast': {
                'max_duration': None,
                'sample_rate': 44100,
                'format': AudioFormat.MP3,
                'bitrate': 128,
                'channels': 1,  # Mono for voice
                'loudness_target': -16
            }
        }
    
    def optimize_for_platform(self, audio_data: np.ndarray, sample_rate: int, 
                             platform: str) -> Tuple[np.ndarray, int, Dict[str, Any]]:
        """Optimize audio for specific platform"""
        if platform not in self.platform_specs:
            return audio_data, sample_rate, {'error': f'Unknown platform: {platform}'}
        
        specs = self.platform_specs[platform]
        optimized_audio = audio_data.copy()
        optimized_sr = sample_rate
        
        optimization_log = []
        
        # 1. Duration trimming
        if specs['max_duration'] and len(optimized_audio) / optimized_sr > specs['max_duration']:
            max_samples = int(specs['max_duration'] * optimized_sr)
            optimized_audio = optimized_audio[:max_samples]
            optimization_log.append(f"Trimmed to {specs['max_duration']} seconds")
        
        # 2. Sample rate conversion
        if optimized_sr != specs['sample_rate']:
            optimized_audio = librosa.resample(
                optimized_audio, 
                orig_sr=optimized_sr, 
                target_sr=specs['sample_rate']
            )
            optimized_sr = specs['sample_rate']
            optimization_log.append(f"Resampled to {specs['sample_rate']} Hz")
        
        # 3. Channel conversion
        if len(optimized_audio.shape) == 1 and specs['channels'] == 2:
            # Mono to stereo
            optimized_audio = np.stack([optimized_audio, optimized_audio])
            optimization_log.append("Converted mono to stereo")
        elif len(optimized_audio.shape) == 2 and specs['channels'] == 1:
            # Stereo to mono
            optimized_audio = np.mean(optimized_audio, axis=0)
            optimization_log.append("Converted stereo to mono")
        
        # 4. Loudness normalization
        optimized_audio = self._normalize_loudness(
            optimized_audio, optimized_sr, specs['loudness_target']
        )
        optimization_log.append(f"Normalized to {specs['loudness_target']} LUFS")
        
        # 5. Dynamic range optimization
        if platform in ['instagram', 'tiktok']:
            # Apply compression for social media
            optimized_audio = self._apply_compression(optimized_audio, ratio=3.0)
            optimization_log.append("Applied compression for social media")
        
        return optimized_audio, optimized_sr, {
            'platform': platform,
            'optimizations_applied': optimization_log,
            'target_specs': specs
        }
    
    def _normalize_loudness(self, audio_data: np.ndarray, sample_rate: int, target_lufs: float) -> np.ndarray:
        """Normalize audio to target loudness (simplified LUFS approximation)"""
        if len(audio_data) == 0:
            return audio_data
        
        # Calculate current RMS level
        current_rms = np.sqrt(np.mean(audio_data ** 2))
        
        if current_rms == 0:
            return audio_data
        
        # Convert target LUFS to linear scale (simplified)
        # This is a rough approximation - actual LUFS requires more complex calculation
        target_linear = 10 ** (target_lufs / 20.0)
        
        # Calculate gain needed
        gain = target_linear / current_rms
        
        # Apply gain with limiting to prevent clipping
        normalized_audio = audio_data * gain
        
        # Soft limiting
        max_value = np.max(np.abs(normalized_audio))
        if max_value > 0.95:
            normalized_audio = normalized_audio * (0.95 / max_value)
        
        return normalized_audio
    
    def _apply_compression(self, audio_data: np.ndarray, ratio: float = 4.0, 
                          threshold: float = 0.5, attack: float = 0.001, 
                          release: float = 0.1) -> np.ndarray:
        """Apply dynamic range compression"""
        if len(audio_data) == 0:
            return audio_data
        
        # Simple RMS-based compressor
        compressed_audio = audio_data.copy()
        
        # Calculate window size for RMS calculation
        window_size = int(0.01 * 44100)  # 10ms window
        
        for i in range(0, len(compressed_audio) - window_size, window_size):
            window = compressed_audio[i:i + window_size]
            rms = np.sqrt(np.mean(window ** 2))
            
            if rms > threshold:
                # Calculate compression gain
                excess = rms - threshold
                compressed_excess = excess / ratio
                new_rms = threshold + compressed_excess
                
                if rms > 0:
                    gain = new_rms / rms
                    compressed_audio[i:i + window_size] *= gain
        
        return compressed_audio

class EnterpriseAudioEngine:
    """Central enterprise audio processing system"""
    
    def __init__(self):
        self.spectral_analyzer = SpectralAnalyzer()
        self.rhythm_analyzer = RhythmAnalyzer()
        self.harmonic_analyzer = HarmonicAnalyzer()
        self.quality_analyzer = AudioQualityAnalyzer()
        self.platform_optimizer = PlatformOptimizer()
        
        # Processing queue and cache
        self.processing_queue = deque()
        self.analysis_cache: Dict[str, AudioAnalysis] = {}
        self.processed_audio_cache: Dict[str, Dict[str, Any]] = {}
        
        # Background processing
        self.processing_active = False
        self.processing_tasks: List[asyncio.Task] = []
        
        self.logger = logging.getLogger(__name__)
    
    async def analyze_audio(self, audio_file_path: str, cache_results: bool = True) -> AudioAnalysis:
        """Comprehensive audio analysis"""
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(audio_file_path)
            
            if cache_results and cache_key in self.analysis_cache:
                return self.analysis_cache[cache_key]
            
            # Load audio file
            audio_data, sample_rate = librosa.load(audio_file_path, sr=None, mono=False)
            
            # Ensure mono for analysis (convert stereo to mono)
            if len(audio_data.shape) == 2:
                audio_data_mono = np.mean(audio_data, axis=0)
            else:
                audio_data_mono = audio_data
            
            # Basic metadata
            duration = len(audio_data_mono) / sample_rate
            file_stats = os.stat(audio_file_path)
            
            # Audio level analysis
            peak_level = float(np.max(np.abs(audio_data_mono)))
            rms_level = float(np.sqrt(np.mean(audio_data_mono ** 2)))
            
            # Frequency response analysis
            frequency_response = self.spectral_analyzer.analyze_frequency_response(
                audio_data_mono, sample_rate
            )
            
            # Create metadata
            metadata = AudioMetadata(
                duration=duration,
                sample_rate=sample_rate,
                channels=len(audio_data.shape),
                bit_depth=16,  # Default assumption
                format=os.path.splitext(audio_file_path)[1][1:].lower(),
                file_size=file_stats.st_size,
                peak_level=peak_level,
                rms_level=rms_level,
                dynamic_range=20 * np.log10(peak_level / (rms_level + 1e-10)),
                frequency_response=frequency_response
            )
            
            # Perform comprehensive analysis
            spectral_features = self.spectral_analyzer.analyze_spectrum(audio_data_mono, sample_rate)
            rhythm_features = self.rhythm_analyzer.analyze_rhythm(audio_data_mono, sample_rate)
            harmonic_features = self.harmonic_analyzer.analyze_harmony(audio_data_mono, sample_rate)
            quality_metrics = self.quality_analyzer.analyze_quality(audio_data_mono, sample_rate)
            
            # Content classification
            content_classification = self._classify_audio_content(
                spectral_features, rhythm_features, harmonic_features
            )
            
            # Platform suitability analysis
            platform_suitability = self._analyze_platform_suitability(
                metadata, quality_metrics, content_classification
            )
            
            # Create analysis result
            analysis = AudioAnalysis(
                metadata=metadata,
                spectral_features=spectral_features,
                rhythm_features=rhythm_features,
                harmonic_features=harmonic_features,
                quality_metrics=quality_metrics,
                content_classification=content_classification,
                platform_suitability=platform_suitability
            )
            
            # Cache results
            if cache_results:
                self.analysis_cache[cache_key] = analysis
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Audio analysis failed: {str(e)}")
            raise
    
    async def optimize_for_platforms(self, audio_file_path: str, target_platforms: List[str],
                                   output_dir: str) -> Dict[str, Dict[str, Any]]:
        """Optimize audio for multiple platforms"""
        try:
            # Load audio
            audio_data, sample_rate = librosa.load(audio_file_path, sr=None, mono=False)
            
            optimization_results = {}
            
            for platform in target_platforms:
                self.logger.info(f"Optimizing audio for {platform}")
                
                # Optimize for platform
                optimized_audio, optimized_sr, optimization_log = self.platform_optimizer.optimize_for_platform(
                    audio_data, sample_rate, platform
                )
                
                # Generate output filename
                base_name = os.path.splitext(os.path.basename(audio_file_path))[0]
                platform_specs = self.platform_optimizer.platform_specs[platform]
                output_format = platform_specs['format'].value
                output_filename = f"{base_name}_{platform}.{output_format}"
                output_path = os.path.join(output_dir, output_filename)
                
                # Save optimized audio
                await self._save_audio(optimized_audio, optimized_sr, output_path, platform_specs)
                
                # Calculate quality metrics for optimized version
                if len(optimized_audio.shape) == 2:
                    mono_audio = np.mean(optimized_audio, axis=0)
                else:
                    mono_audio = optimized_audio
                
                optimized_quality = self.quality_analyzer.analyze_quality(mono_audio, optimized_sr)
                
                optimization_results[platform] = {
                    'output_path': output_path,
                    'optimization_log': optimization_log,
                    'quality_metrics': optimized_quality,
                    'file_size': os.path.getsize(output_path) if os.path.exists(output_path) else 0
                }
            
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Platform optimization failed: {str(e)}")
            raise
    
    async def _save_audio(self, audio_data: np.ndarray, sample_rate: int, 
                         output_path: str, specs: Dict[str, Any]):
        """Save audio with platform-specific encoding"""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert to appropriate format using pydub
            if len(audio_data.shape) == 1:
                # Mono
                audio_segment = AudioSegment(
                    audio_data.tobytes(),
                    frame_rate=sample_rate,
                    sample_width=2,  # 16-bit
                    channels=1
                )
            else:
                # Stereo
                # Interleave channels
                interleaved = np.column_stack((audio_data[0], audio_data[1])).flatten()
                audio_segment = AudioSegment(
                    interleaved.tobytes(),
                    frame_rate=sample_rate,
                    sample_width=2,  # 16-bit
                    channels=2
                )
            
            # Export with platform-specific settings
            format_name = specs['format'].value
            bitrate = f"{specs['bitrate']}k"
            
            if format_name == 'mp3':
                audio_segment.export(output_path, format="mp3", bitrate=bitrate)
            elif format_name == 'aac':
                audio_segment.export(output_path, format="mp4", bitrate=bitrate)
            elif format_name == 'ogg':
                audio_segment.export(output_path, format="ogg", bitrate=bitrate)
            else:
                # Default to WAV
                audio_segment.export(output_path, format="wav")
            
        except Exception as e:
            self.logger.error(f"Failed to save audio: {str(e)}")
            raise
    
    def _classify_audio_content(self, spectral_features: Dict[str, Any],
                               rhythm_features: Dict[str, Any],
                               harmonic_features: Dict[str, Any]) -> Dict[str, float]:
        """Classify audio content type using ML features"""
        try:
            content_scores = {}
            
            # Music classification
            music_score = 0.0
            if harmonic_features.get('harmonic_ratio', 0) > 0.6:
                music_score += 0.3
            if rhythm_features.get('beat_consistency', 0) > 0.5:
                music_score += 0.3
            if spectral_features.get('chroma_mean', 0) > 0.1:
                music_score += 0.2
            if rhythm_features.get('tempo', 0) > 60:
                music_score += 0.2
            
            content_scores['music'] = music_score
            
            # Speech classification
            speech_score = 0.0
            if spectral_features.get('zcr_mean', 0) > 0.1:
                speech_score += 0.3
            if harmonic_features.get('percussive_ratio', 0) > 0.4:
                speech_score += 0.2
            if spectral_features.get('spectral_centroid_mean', 0) > 1000:
                speech_score += 0.3
            if rhythm_features.get('rhythmic_regularity', 0) < 0.3:
                speech_score += 0.2
            
            content_scores['speech'] = speech_score
            
            # Ambient/background classification
            ambient_score = 0.0
            if spectral_features.get('bandwidth_mean', 0) > 2000:
                ambient_score += 0.3
            if rhythm_features.get('onset_density', 0) < 1:
                ambient_score += 0.3
            if harmonic_features.get('key_strength', 0) < 0.3:
                ambient_score += 0.2
            if spectral_features.get('rolloff_mean', 0) > 5000:
                ambient_score += 0.2
            
            content_scores['ambient'] = ambient_score
            
            # Ensure scores sum to 1.0
            total_score = sum(content_scores.values())
            if total_score > 0:
                content_scores = {k: v / total_score for k, v in content_scores.items()}
            
            return content_scores
            
        except Exception as e:
            self.logger.error(f"Content classification failed: {str(e)}")
            return {'unknown': 1.0}
    
    def _analyze_platform_suitability(self, metadata: AudioMetadata, 
                                     quality_metrics: Dict[str, float],
                                     content_classification: Dict[str, float]) -> Dict[str, float]:
        """Analyze how suitable the audio is for different platforms"""
        try:
            suitability_scores = {}
            
            for platform, specs in self.platform_optimizer.platform_specs.items():
                score = 1.0
                
                # Duration check
                if specs['max_duration'] and metadata.duration > specs['max_duration']:
                    score *= 0.7  # Penalty for being too long
                
                # Quality check
                overall_quality = quality_metrics.get('overall_quality', 0)
                if overall_quality < 0.6:
                    score *= 0.8  # Penalty for low quality
                
                # Content type suitability
                if platform in ['instagram', 'tiktok']:
                    # Social media prefers music content
                    music_score = content_classification.get('music', 0)
                    score *= (0.5 + 0.5 * music_score)
                elif platform == 'podcast':
                    # Podcasts prefer speech content
                    speech_score = content_classification.get('speech', 0)
                    score *= (0.3 + 0.7 * speech_score)
                
                # Technical compatibility
                if metadata.sample_rate != specs['sample_rate']:
                    score *= 0.9  # Small penalty for resampling needed
                
                if metadata.channels != specs['channels']:
                    score *= 0.95  # Small penalty for channel conversion
                
                suitability_scores[platform] = min(1.0, max(0.0, score))
            
            return suitability_scores
            
        except Exception as e:
            self.logger.error(f"Platform suitability analysis failed: {str(e)}")
            return {}
    
    def _generate_cache_key(self, file_path: str) -> str:
        """Generate cache key for audio file"""
        # Use file path and modification time for cache key
        stat = os.stat(file_path)
        cache_string = f"{file_path}:{stat.st_mtime}:{stat.st_size}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    async def process_audio_batch(self, audio_files: List[str], target_platforms: List[str],
                                 output_dir: str) -> Dict[str, Any]:
        """Process multiple audio files in batch"""
        try:
            batch_results = {
                'processed_files': 0,
                'failed_files': 0,
                'total_processing_time': 0.0,
                'file_results': {}
            }
            
            start_time = time.time()
            
            for audio_file in audio_files:
                file_start_time = time.time()
                
                try:
                    # Analyze audio
                    analysis = await self.analyze_audio(audio_file)
                    
                    # Optimize for platforms
                    optimization_results = await self.optimize_for_platforms(
                        audio_file, target_platforms, output_dir
                    )
                    
                    file_processing_time = time.time() - file_start_time
                    
                    batch_results['file_results'][audio_file] = {
                        'status': 'success',
                        'analysis': analysis,
                        'optimizations': optimization_results,
                        'processing_time': file_processing_time
                    }
                    
                    batch_results['processed_files'] += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to process {audio_file}: {str(e)}")
                    
                    batch_results['file_results'][audio_file] = {
                        'status': 'failed',
                        'error': str(e),
                        'processing_time': time.time() - file_start_time
                    }
                    
                    batch_results['failed_files'] += 1
            
            batch_results['total_processing_time'] = time.time() - start_time
            
            return batch_results
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {str(e)}")
            raise
    
    async def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive engine status"""
        return {
            'cache_size': len(self.analysis_cache),
            'processed_cache_size': len(self.processed_audio_cache),
            'processing_queue_size': len(self.processing_queue),
            'processing_active': self.processing_active,
            'active_tasks': len(self.processing_tasks),
            'supported_platforms': list(self.platform_optimizer.platform_specs.keys()),
            'supported_formats': [fmt.value for fmt in AudioFormat],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def clear_cache(self):
        """Clear analysis and processing caches"""
        self.analysis_cache.clear()
        self.processed_audio_cache.clear()
        self.logger.info("Audio engine caches cleared")

# Factory function
async def create_enterprise_audio_engine() -> EnterpriseAudioEngine:
    """Factory function to create audio engine"""
    engine = EnterpriseAudioEngine()
    return engine

# Export main components
__all__ = [
    'EnterpriseAudioEngine',
    'AudioConfig',
    'AudioMetadata',
    'AudioAnalysis',
    'AudioFormat',
    'AudioQuality',
    'AudioEffect',
    'SpectralAnalyzer',
    'RhythmAnalyzer',
    'HarmonicAnalyzer',
    'AudioQualityAnalyzer',
    'PlatformOptimizer',
    'create_enterprise_audio_engine'
]