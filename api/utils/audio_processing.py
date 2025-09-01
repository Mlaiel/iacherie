"""Audio Processing Utilities for IA Influencer Agent Platform
Comprehensive audio analysis, fingerprinting and feature extraction

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform with Multi-Content Protection
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""

import librosa
import numpy as np
import hashlib
import chromadb
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import soundfile as sf
from scipy.signal import spectrogram
import essentia
import essentia.standard as es


@dataclass
class AudioFeatures:
    """
Comprehensive audio feature representation"""
    tempo: float
    key: str
    energy: float
    valence: float
    spectral_centroid: float
    spectral_rolloff: float
    zero_crossing_rate: float
    mfcc: List[float]
    chroma: List[float]
    spectral_contrast: List[float]
    tonnetz: List[float]
    fingerprint_hash: str
    duration: float
    sample_rate: int


class AudioAnalyzer:
    """
Professional audio analysis engine for content protection and insights"""
    
    def __init__(self, sample_rate: int = 22050, hop_length: int = 512):
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.frame_length = hop_length * 2
        
    def analyze_audio_file(self, file_path: str) -> AudioFeatures:
        """
Complete audio analysis with feature extraction"""
        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=self.sample_rate)
            
            # Extract comprehensive features
            features = self._extract_all_features(y, sr)
            
            # Generate fingerprint
            fingerprint = self._generate_fingerprint(y, sr)
            
            return AudioFeatures(
                tempo=features['tempo'],
                key=features['key'],
                energy=features['energy'],
                valence=features['valence'],
                spectral_centroid=features['spectral_centroid'],
                spectral_rolloff=features['spectral_rolloff'],
                zero_crossing_rate=features['zero_crossing_rate'],
                mfcc=features['mfcc'].tolist(),
                chroma=features['chroma'].tolist(),
                spectral_contrast=features['spectral_contrast'].tolist(),
                tonnetz=features['tonnetz'].tolist(),
                fingerprint_hash=fingerprint,
                duration=len(y) / sr,
                sample_rate=sr
            )
            
        except Exception as e:
            raise AudioProcessingError(f"Failed to analyze audio file: {str(e)}")
    
    def _extract_all_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract comprehensive audio features"""
        features = {}
        
        # Tempo and beat tracking
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        features['tempo'] = float(tempo)
        
        # Key detection using chroma
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        key = self._detect_key(chroma)
        features['key'] = key
        
        # Energy and valence
        features['energy'] = float(np.mean(librosa.feature.rmse(y=y)))
        features['valence'] = self._calculate_valence(y, sr)
        
        # Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        features['spectral_centroid'] = float(np.mean(spectral_centroids))
        
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        features['spectral_rolloff'] = float(np.mean(spectral_rolloff))
        
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        features['zero_crossing_rate'] = float(np.mean(zcr))
        
        # Advanced features
        features['mfcc'] = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13), axis=1)
        features['chroma'] = np.mean(chroma, axis=1)
        features['spectral_contrast'] = np.mean(
            librosa.feature.spectral_contrast(y=y, sr=sr), axis=1
        )
        features['tonnetz'] = np.mean(
            librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr), axis=1
        )
        
        return features
    
    def _detect_key(self, chroma: np.ndarray) -> str:
        """
Detect musical key from chroma features"""
        key_profiles = {
            'C': [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
            'C#': [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0],
            'D': [0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
            'D#': [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
            'E': [0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
            'F': [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0],
            'F#': [0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1],
            'G': [1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
            'G#': [1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0],
            'A': [0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
            'A#': [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0],
            'B': [0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1]
        }
        
        chroma_mean = np.mean(chroma, axis=1)
        correlations = {}
        
        for key, profile in key_profiles.items():
            correlation = np.corrcoef(chroma_mean, profile)[0, 1]
            correlations[key] = correlation if not np.isnan(correlation) else 0
        
        return max(correlations, key=correlations.get)
    
    def _calculate_valence(self, y: np.ndarray, sr: int) -> float:
        """
Calculate audio valence (positivity/negativity)"""
        # Use spectral features as proxy for valence
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
        
        # Normalize and combine features
        valence = (spectral_centroid / sr + spectral_rolloff / sr) / 2
        return float(np.clip(valence, 0, 1))
    
    def _generate_fingerprint(self, y: np.ndarray, sr: int) -> str:
        """
Generate audio fingerprint hash"""
        # Combine multiple fingerprinting techniques
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        
        # Create combined feature vector
        features = np.concatenate([
            np.mean(mfcc, axis=1),
            np.mean(chroma, axis=1),
            np.mean(spectral_contrast, axis=1)
        ])
        
        # Generate hash
        features_bytes = features.astype(np.float32).tobytes()
        return hashlib.sha256(features_bytes).hexdigest()


class AudioFingerprinter:
    """
Advanced audio fingerprinting for copyright protection"""
    
    def __init__(self):
        self.sample_rate = 22050
        self.frame_size = 2048
        self.hop_size = 1024
        
    def create_fingerprint(self, audio_path: str) -> Dict[str, Any]:
        """
Create comprehensive audio fingerprint"""
        try:
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            fingerprint_data = {
                'chromaprint': self._generate_chromaprint(y, sr),
                'spectral_hash': self._generate_spectral_hash(y, sr),
                'perceptual_hash': self._generate_perceptual_hash(y, sr),
                'onset_patterns': self._extract_onset_patterns(y, sr),
                'harmonic_features': self._extract_harmonic_features(y, sr)
            }
            
            return fingerprint_data
            
        except Exception as e:
            raise AudioProcessingError(f"Failed to create fingerprint: {str(e)}")
    
    def _generate_chromaprint(self, y: np.ndarray, sr: int) -> str:
        """Generate Chromaprint-style fingerprint"""
        # Simplified chromaprint implementation
        chroma = librosa.feature.chroma_stft(
            y=y, sr=sr, hop_length=self.hop_size, n_fft=self.frame_size
        )
        
        # Quantize chroma features
        chroma_quantized = np.round(chroma * 7).astype(int)
        
        # Create hash from quantized features
        chroma_bytes = chroma_quantized.tobytes()
        return hashlib.md5(chroma_bytes).hexdigest()
    
    def _generate_spectral_hash(self, y: np.ndarray, sr: int) -> str:
        """
Generate spectral-based hash"""
        # Compute STFT
        stft = librosa.stft(y, hop_length=self.hop_size, n_fft=self.frame_size)
        magnitude = np.abs(stft)
        
        # Extract peak frequencies
        peak_freqs = np.argmax(magnitude, axis=0)
        
        # Create hash from peak frequency pattern
        peak_bytes = peak_freqs.astype(np.int16).tobytes()
        return hashlib.sha256(peak_bytes).hexdigest()
    
    def _generate_perceptual_hash(self, y: np.ndarray, sr: int) -> str:
        """
Generate perceptual hash for similarity matching"""
        # Use mel-spectrogram for perceptual similarity
        mel_spec = librosa.feature.melspectrogram(
            y=y, sr=sr, hop_length=self.hop_size, n_fft=self.frame_size
        )
        
        # Convert to log scale
        log_mel = librosa.power_to_db(mel_spec)
        
        # Reduce dimensionality
        reduced = np.mean(log_mel, axis=1)
        
        # Create binary hash
        median_val = np.median(reduced)
        binary_hash = (reduced > median_val).astype(int)
        
        # Convert to hex string
        binary_str = ''.join(binary_hash.astype(str))
        hash_int = int(binary_str, 2)
        return format(hash_int, 'x')
    
    def _extract_onset_patterns(self, y: np.ndarray, sr: int) -> List[float]:
        """
Extract onset timing patterns"""
        onset_frames = librosa.onset.onset_detect(
            y=y, sr=sr, hop_length=self.hop_size
        )
        onset_times = librosa.frames_to_time(
            onset_frames, sr=sr, hop_length=self.hop_size
        )
        
        # Calculate inter-onset intervals
        intervals = np.diff(onset_times)
        return intervals.tolist()
    
    def _extract_harmonic_features(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
Extract harmonic content features"""
        # Separate harmonic and percussive components
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        
        # Calculate harmonic/percussive ratio
        harmonic_energy = np.sum(y_harmonic**2)
        percussive_energy = np.sum(y_percussive**2)
        total_energy = harmonic_energy + percussive_energy
        
        return {
            'harmonic_ratio': harmonic_energy / total_energy,
            'percussive_ratio': percussive_energy / total_energy,
            'harmonic_centroid': float(np.mean(
                librosa.feature.spectral_centroid(y=y_harmonic, sr=sr)
            )),
            'percussive_centroid': float(np.mean(
                librosa.feature.spectral_centroid(y=y_percussive, sr=sr)
            ))
        }


class SpectralAnalyzer:
    """
Advanced spectral analysis for audio content"""
    
    def __init__(self, n_fft: int = 2048, hop_length: int = 512):
        self.n_fft = n_fft
        self.hop_length = hop_length
        
    def analyze_spectrum(self, audio_path: str) -> Dict[str, Any]:
        """
Comprehensive spectral analysis"""
        y, sr = librosa.load(audio_path)
        
        analysis = {
            'spectral_centroid': self._calculate_spectral_centroid(y, sr),
            'spectral_bandwidth': self._calculate_spectral_bandwidth(y, sr),
            'spectral_contrast': self._calculate_spectral_contrast(y, sr),
            'spectral_flatness': self._calculate_spectral_flatness(y, sr),
            'spectral_rolloff': self._calculate_spectral_rolloff(y, sr),
            'frequency_peaks': self._find_frequency_peaks(y, sr),
            'harmonic_percussive_ratio': self._calculate_hpr(y)
        }
        
        return analysis
    
    def _calculate_spectral_centroid(self, y: np.ndarray, sr: int) -> float:
        """
Calculate spectral centroid"""
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        return float(np.mean(centroid))
    
    def _calculate_spectral_bandwidth(self, y: np.ndarray, sr: int) -> float:
        """
Calculate spectral bandwidth"""
        bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        return float(np.mean(bandwidth))
    
    def _calculate_spectral_contrast(self, y: np.ndarray, sr: int) -> List[float]:
        """
Calculate spectral contrast"""
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        return np.mean(contrast, axis=1).tolist()
    
    def _calculate_spectral_flatness(self, y: np.ndarray, sr: int) -> float:
        """
Calculate spectral flatness"""
        flatness = librosa.feature.spectral_flatness(y=y)[0]
        return float(np.mean(flatness))
    
    def _calculate_spectral_rolloff(self, y: np.ndarray, sr: int) -> float:
        """
Calculate spectral rolloff"""
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        return float(np.mean(rolloff))
    
    def _find_frequency_peaks(self, y: np.ndarray, sr: int) -> List[float]:
        """
Find dominant frequency peaks"""
        # Compute FFT
        fft = np.fft.fft(y)
        magnitude = np.abs(fft)
        
        # Find peaks
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(magnitude, height=np.max(magnitude) * 0.1)
        
        # Convert to frequencies
        freqs = np.fft.fftfreq(len(fft), 1/sr)
        peak_freqs = freqs[peaks]
        
        # Return positive frequencies only
        return peak_freqs[peak_freqs > 0].tolist()[:10]  # Top 10 peaks
    
    def _calculate_hpr(self, y: np.ndarray) -> float:
        """
Calculate harmonic-percussive ratio"""
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        
        harmonic_energy = np.sum(y_harmonic**2)
        percussive_energy = np.sum(y_percussive**2)
        
        if percussive_energy == 0:
            return float('inf')
        
        return harmonic_energy / percussive_energy


class ChromaprintProcessor:
    """
Chromaprint-compatible fingerprinting processor"""
    
    def __init__(self):
        self.sample_rate = 11025  # Chromaprint standard
        self.frame_size = 4096
        self.overlap = 0.75
        
    def generate_chromaprint(self, audio_path: str) -> str:
        """
Generate Chromaprint-compatible fingerprint"""
        try:
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Preprocess audio
            y = self._preprocess_audio(y)
            
            # Extract chroma features
            chroma_features = self._extract_chroma_features(y, sr)
            
            # Quantize and encode
            fingerprint = self._quantize_and_encode(chroma_features)
            
            return fingerprint
            
        except Exception as e:
            raise AudioProcessingError(f"Failed to generate Chromaprint: {str(e)}")
    
    def _preprocess_audio(self, y: np.ndarray) -> np.ndarray:
        """Preprocess audio for fingerprinting"""
        # Apply pre-emphasis filter
        y_emphasized = np.append(y[0], y[1:] - 0.97 * y[:-1])
        
        # Normalize
        y_normalized = y_emphasized / np.max(np.abs(y_emphasized))
        
        return y_normalized
    
    def _extract_chroma_features(self, y: np.ndarray, sr: int) -> np.ndarray:
        """
Extract chroma features compatible with Chromaprint"""
        # Calculate hop length
        hop_length = int(self.frame_size * (1 - self.overlap))
        
        # Extract chroma
        chroma = librosa.feature.chroma_stft(
            y=y, 
            sr=sr, 
            n_fft=self.frame_size, 
            hop_length=hop_length,
            n_chroma=12
        )
        
        return chroma
    
    def _quantize_and_encode(self, chroma: np.ndarray) -> str:
        """
Quantize chroma features and encode as fingerprint"""
        # Quantize to 3 bits per coefficient
        quantized = np.round(chroma * 7).astype(np.uint8)
        
        # Flatten and convert to bytes
        flattened = quantized.flatten()
        
        # Create fingerprint hash
        fingerprint_bytes = flattened.tobytes()
        fingerprint = hashlib.sha256(fingerprint_bytes).hexdigest()
        
        return fingerprint


class AudioFeatureExtractor:
    """
Comprehensive audio feature extraction for ML models"""
    
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        
    def extract_features(self, audio_path: str) -> Dict[str, Any]:
        """
Extract all available audio features"""
        y, sr = librosa.load(audio_path, sr=self.sample_rate)
        
        features = {}
        
        # Basic features
        features.update(self._extract_basic_features(y, sr))
        
        # Spectral features  
        features.update(self._extract_spectral_features(y, sr))
        
        # Rhythmic features
        features.update(self._extract_rhythmic_features(y, sr))
        
        # Harmonic features
        features.update(self._extract_harmonic_features(y, sr))
        
        # Advanced features
        features.update(self._extract_advanced_features(y, sr))
        
        return features
    
    def _extract_basic_features(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
Extract basic audio features"""
        return {
            'duration': len(y) / sr,
            'rms_energy': float(np.mean(librosa.feature.rms(y=y))),
            'zero_crossing_rate': float(np.mean(librosa.feature.zero_crossing_rate(y))),
            'tempo': float(librosa.beat.tempo(y=y, sr=sr)[0])
        }
    
    def _extract_spectral_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
Extract spectral features"""
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        
        return {
            'spectral_centroid_mean': float(np.mean(spectral_centroids)),
            'spectral_centroid_std': float(np.std(spectral_centroids)),
            'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
            'spectral_rolloff_std': float(np.std(spectral_rolloff)),
            'spectral_bandwidth_mean': float(np.mean(spectral_bandwidth)),
            'spectral_bandwidth_std': float(np.std(spectral_bandwidth))
        }
    
    def _extract_rhythmic_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
Extract rhythmic features"""
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        
        return {
            'tempo': float(tempo),
            'beat_count': len(beats),
            'rhythm_regularity': self._calculate_rhythm_regularity(beats, sr)
        }
    
    def _extract_harmonic_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
Extract harmonic features"""
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        
        return {
            'harmonic_energy': float(np.sum(y_harmonic**2)),
            'percussive_energy': float(np.sum(y_percussive**2)),
            'harmonic_percussive_ratio': float(
                np.sum(y_harmonic**2) / (np.sum(y_percussive**2) + 1e-8)
            )
        }
    
    def _extract_advanced_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
Extract advanced features"""
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        
        features = {}
        
        # MFCC statistics
        for i in range(13):
            features[f'mfcc_{i}_mean'] = float(np.mean(mfcc[i]))
            features[f'mfcc_{i}_std'] = float(np.std(mfcc[i]))
        
        # Chroma statistics
        for i in range(12):
            features[f'chroma_{i}_mean'] = float(np.mean(chroma[i]))
            features[f'chroma_{i}_std'] = float(np.std(chroma[i]))
        
        # Spectral contrast statistics
        for i in range(7):
            features[f'contrast_{i}_mean'] = float(np.mean(contrast[i]))
            features[f'contrast_{i}_std'] = float(np.std(contrast[i]))
        
        return features
    
    def _calculate_rhythm_regularity(self, beats: np.ndarray, sr: int) -> float:
        """
Calculate rhythm regularity measure"""
        if len(beats) < 2:
            return 0.0
            
        # Convert beats to time
        beat_times = librosa.frames_to_time(beats, sr=sr)
        
        # Calculate inter-beat intervals
        intervals = np.diff(beat_times)
        
        # Measure regularity as inverse of coefficient of variation
        if np.mean(intervals) == 0:
            return 0.0
            
        cv = np.std(intervals) / np.mean(intervals)
        regularity = 1.0 / (1.0 + cv)
        
        return float(regularity)


class AudioProcessingError(Exception):
    """
Custom exception for audio processing errors"""
    pass
