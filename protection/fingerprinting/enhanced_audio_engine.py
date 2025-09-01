#!/usr/bin/env python3
"""Enhanced Audio Fingerprinting Engine for Production
ML-powered audio fingerprinting with Chromaprint integration

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import hashlib
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
import base64

# Core audio processing
try:
    import librosa
    import librosa.feature
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    librosa = None

try:
    import pyacoustid
    ACOUSTID_AVAILABLE = True
except ImportError:
    ACOUSTID_AVAILABLE = False
    pyacoustid = None

# ML and signal processing
from scipy import signal
from scipy.fft import fft, fftfreq
import sklearn.metrics.pairwise as smp

logger = logging.getLogger(__name__)

@dataclass
class EnhancedAudioFingerprint:
    """Enhanced audio fingerprint with ML features"""
    file_id: str
    chromaprint_hash: Optional[str]
    spectral_features: Dict[str, Any]
    mel_spectrogram: np.ndarray
    mfcc_features: np.ndarray
    chroma_features: np.ndarray
    tempo: float
    rhythm_pattern: List[float]
    harmonic_features: Dict[str, Any]
    zero_crossing_rate: float
    spectral_centroid: float
    spectral_rolloff: float
    confidence_score: float
    duration: float
    sample_rate: int
    created_at: datetime

class EnhancedAudioFingerprintEngine:
    """Production-ready audio fingerprinting engine with ML integration"""
    
    def __init__(self, 
                 sample_rate: int = 22050,
                 hop_length: int = 512,
                 n_mels: int = 128,
                 n_mfcc: int = 13,
                 max_duration: int = 300):
        """
        Initialize enhanced audio fingerprinting engine
        
        Args:
            sample_rate: Target sample rate for processing
            hop_length: Number of samples between successive frames
            n_mels: Number of Mel bands
            n_mfcc: Number of MFCC coefficients
            max_duration: Maximum duration to process (seconds)
        """
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.n_mels = n_mels
        self.n_mfcc = n_mfcc
        self.max_duration = max_duration
        self.n_fft = 2048
        
        self.similarity_threshold = 0.85
        
        # Initialize feature extractors
        self._init_feature_extractors()
        
        logger.info(f"Enhanced Audio Fingerprinting Engine initialized")
        logger.info(f"Librosa available: {LIBROSA_AVAILABLE}")
        logger.info(f"AcoustID available: {ACOUSTID_AVAILABLE}")
    
    def _init_feature_extractors(self):
        """Initialize feature extraction components"""
        self.feature_config = {
            'mel_bands': self.n_mels,
            'mfcc_coeffs': self.n_mfcc,
            'tempo_estimation': True,
            'harmonic_analysis': True,
            'chromagram': True
        }
    
    async def extract_fingerprint(self, 
                                audio_path: Union[str, Path],
                                use_chromaprint: bool = True) -> EnhancedAudioFingerprint:
        """
        Extract comprehensive audio fingerprint
        
        Args:
            audio_path: Path to audio file
            use_chromaprint: Whether to use Chromaprint (requires external tool)
            
        Returns:
            Enhanced audio fingerprint
        """
        if not LIBROSA_AVAILABLE:
            raise RuntimeError("librosa is required for audio fingerprinting")
        
        # Load audio file
        audio_data, sr = librosa.load(str(audio_path), 
                                     sr=self.sample_rate, 
                                     duration=self.max_duration)
        
        # Generate file ID
        file_id = self._generate_file_id(audio_path, audio_data)
        
        # Extract features in parallel
        features = await self._extract_all_features(audio_data, sr)
        
        # Extract Chromaprint if available and requested
        chromaprint_hash = None
        if use_chromaprint and ACOUSTID_AVAILABLE:
            try:
                chromaprint_hash = await self._extract_chromaprint(str(audio_path))
            except Exception as e:
                logger.warning(f"Chromaprint extraction failed: {e}")
        
        # Calculate confidence score
        confidence = self._calculate_confidence(features)
        
        return EnhancedAudioFingerprint(
            file_id=file_id,
            chromaprint_hash=chromaprint_hash,
            spectral_features=features['spectral'],
            mel_spectrogram=features['mel_spectrogram'],
            mfcc_features=features['mfcc'],
            chroma_features=features['chroma'],
            tempo=features['tempo'],
            rhythm_pattern=features['rhythm_pattern'],
            harmonic_features=features['harmonic'],
            zero_crossing_rate=features['zcr'],
            spectral_centroid=features['spectral_centroid'],
            spectral_rolloff=features['spectral_rolloff'],
            confidence_score=confidence,
            duration=len(audio_data) / sr,
            sample_rate=sr,
            created_at=datetime.utcnow()
        )
    
    async def _extract_all_features(self, audio_data: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract all audio features"""
        features = {}
        
        # Mel spectrogram
        mel_spec = librosa.feature.melspectrogram(
            y=audio_data, sr=sr, n_mels=self.n_mels, hop_length=self.hop_length
        )
        features['mel_spectrogram'] = mel_spec
        
        # MFCC
        mfcc = librosa.feature.mfcc(
            y=audio_data, sr=sr, n_mfcc=self.n_mfcc, hop_length=self.hop_length
        )
        features['mfcc'] = mfcc
        
        # Chroma features
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr, hop_length=self.hop_length)
        features['chroma'] = chroma
        
        # Tempo and rhythm
        tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sr)
        features['tempo'] = float(tempo)
        
        # Rhythm pattern (beat histogram)
        beat_times = librosa.frames_to_time(beats, sr=sr)
        if len(beat_times) > 1:
            beat_intervals = np.diff(beat_times)
            rhythm_pattern = np.histogram(beat_intervals, bins=20)[0].tolist()
        else:
            rhythm_pattern = [0] * 20
        features['rhythm_pattern'] = rhythm_pattern
        
        # Harmonic and percussive separation
        harmonic, percussive = librosa.effects.hpss(audio_data)
        harmonic_energy = np.sum(harmonic ** 2)
        percussive_energy = np.sum(percussive ** 2)
        features['harmonic'] = {
            'harmonic_energy': float(harmonic_energy),
            'percussive_energy': float(percussive_energy),
            'harmonic_ratio': float(harmonic_energy / (harmonic_energy + percussive_energy + 1e-10))
        }
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio_data, hop_length=self.hop_length)
        features['zcr'] = float(np.mean(zcr))
        
        # Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sr)
        
        features['spectral_centroid'] = float(np.mean(spectral_centroids))
        features['spectral_rolloff'] = float(np.mean(spectral_rolloff))
        
        # Additional spectral features
        features['spectral'] = {
            'centroid_mean': float(np.mean(spectral_centroids)),
            'centroid_std': float(np.std(spectral_centroids)),
            'rolloff_mean': float(np.mean(spectral_rolloff)),
            'rolloff_std': float(np.std(spectral_rolloff)),
            'zcr_mean': float(np.mean(zcr)),
            'zcr_std': float(np.std(zcr))
        }
        
        return features
    
    async def _extract_chromaprint(self, audio_path: str) -> Optional[str]:
        """Extract Chromaprint fingerprint using pyacoustid"""
        try:
            # Use pyacoustid to get fingerprint
            duration, fingerprint = pyacoustid.fingerprint_file(audio_path)
            return fingerprint
        except Exception as e:
            logger.error(f"Chromaprint extraction failed: {e}")
            return None
    
    def _generate_file_id(self, audio_path: Union[str, Path], audio_data: np.ndarray) -> str:
        """Generate unique file ID"""
        path_str = str(audio_path)
        audio_hash = hashlib.md5(audio_data.tobytes()).hexdigest()[:16]
        file_hash = hashlib.md5(path_str.encode()).hexdigest()[:16]
        return f"audio_{file_hash}_{audio_hash}"
    
    def _calculate_confidence(self, features: Dict[str, Any]) -> float:
        """Calculate confidence score based on feature quality"""
        confidence_factors = []
        
        # Check feature completeness
        required_features = ['mel_spectrogram', 'mfcc', 'chroma', 'tempo', 'harmonic']
        completeness = sum(1 for feat in required_features if feat in features) / len(required_features)
        confidence_factors.append(completeness)
        
        # Check audio quality indicators
        if 'spectral' in features:
            # Higher spectral diversity indicates better quality
            spectral_diversity = 1.0 - (features['spectral'].get('centroid_std', 0) / 
                                      (features['spectral'].get('centroid_mean', 1) + 1e-10))
            confidence_factors.append(min(spectral_diversity, 1.0))
        
        # Check harmonic content
        if 'harmonic' in features:
            harmonic_ratio = features['harmonic'].get('harmonic_ratio', 0)
            confidence_factors.append(harmonic_ratio)
        
        return float(np.mean(confidence_factors))
    
    async def compare_fingerprints(self, 
                                 fp1: EnhancedAudioFingerprint, 
                                 fp2: EnhancedAudioFingerprint) -> float:
        """
        Compare two audio fingerprints
        
        Returns:
            Similarity score between 0 and 1
        """
        similarities = []
        
        # Compare Chromaprint if available
        if fp1.chromaprint_hash and fp2.chromaprint_hash:
            chromaprint_sim = self._compare_chromaprint(fp1.chromaprint_hash, fp2.chromaprint_hash)
            similarities.append(chromaprint_sim)
        
        # Compare MFCC features
        mfcc_sim = self._compare_mfcc(fp1.mfcc_features, fp2.mfcc_features)
        similarities.append(mfcc_sim)
        
        # Compare chroma features
        chroma_sim = self._compare_chroma(fp1.chroma_features, fp2.chroma_features)
        similarities.append(chroma_sim)
        
        # Compare tempo
        tempo_sim = self._compare_tempo(fp1.tempo, fp2.tempo)
        similarities.append(tempo_sim)
        
        # Compare spectral features
        spectral_sim = self._compare_spectral_features(fp1.spectral_features, fp2.spectral_features)
        similarities.append(spectral_sim)
        
        # Weighted average
        weights = [0.3, 0.25, 0.2, 0.1, 0.15]  # Chromaprint gets highest weight
        if not fp1.chromaprint_hash or not fp2.chromaprint_hash:
            # Reweight if no chromaprint available
            weights = [0.35, 0.25, 0.15, 0.25]
            similarities = similarities[1:]  # Remove chromaprint similarity
        
        return float(np.average(similarities, weights=weights))
    
    def _compare_chromaprint(self, hash1: str, hash2: str) -> float:
        """Compare Chromaprint hashes"""
        if hash1 == hash2:
            return 1.0
        
        # Simple character-based similarity for now
        # In production, use proper Chromaprint comparison
        common_chars = sum(1 for a, b in zip(hash1, hash2) if a == b)
        return common_chars / max(len(hash1), len(hash2))
    
    def _compare_mfcc(self, mfcc1: np.ndarray, mfcc2: np.ndarray) -> float:
        """Compare MFCC features using cosine similarity"""
        # Flatten and normalize
        mfcc1_flat = mfcc1.flatten()
        mfcc2_flat = mfcc2.flatten()
        
        # Pad to same length if needed
        min_len = min(len(mfcc1_flat), len(mfcc2_flat))
        mfcc1_flat = mfcc1_flat[:min_len]
        mfcc2_flat = mfcc2_flat[:min_len]
        
        # Cosine similarity
        return float(smp.cosine_similarity([mfcc1_flat], [mfcc2_flat])[0][0])
    
    def _compare_chroma(self, chroma1: np.ndarray, chroma2: np.ndarray) -> float:
        """Compare chroma features"""
        # Mean chroma vectors
        chroma1_mean = np.mean(chroma1, axis=1)
        chroma2_mean = np.mean(chroma2, axis=1)
        
        # Cosine similarity
        return float(smp.cosine_similarity([chroma1_mean], [chroma2_mean])[0][0])
    
    def _compare_tempo(self, tempo1: float, tempo2: float) -> float:
        """Compare tempo values"""
        tempo_diff = abs(tempo1 - tempo2)
        max_tempo = max(tempo1, tempo2, 1.0)
        return 1.0 - (tempo_diff / max_tempo)
    
    def _compare_spectral_features(self, spec1: Dict, spec2: Dict) -> float:
        """Compare spectral features"""
        similarities = []
        
        common_keys = set(spec1.keys()) & set(spec2.keys())
        for key in common_keys:
            if isinstance(spec1[key], (int, float)) and isinstance(spec2[key], (int, float)):
                val_diff = abs(spec1[key] - spec2[key])
                max_val = max(abs(spec1[key]), abs(spec2[key]), 1.0)
                sim = 1.0 - (val_diff / max_val)
                similarities.append(sim)
        
        return float(np.mean(similarities)) if similarities else 0.0
    
    def export_fingerprint(self, fingerprint: EnhancedAudioFingerprint) -> Dict[str, Any]:
        """Export fingerprint to serializable format"""
        return {
            'file_id': fingerprint.file_id,
            'chromaprint_hash': fingerprint.chromaprint_hash,
            'spectral_features': fingerprint.spectral_features,
            'mel_spectrogram_shape': fingerprint.mel_spectrogram.shape,
            'mel_spectrogram_b64': base64.b64encode(fingerprint.mel_spectrogram.tobytes()).decode(),
            'mfcc_features_shape': fingerprint.mfcc_features.shape,
            'mfcc_features_b64': base64.b64encode(fingerprint.mfcc_features.tobytes()).decode(),
            'chroma_features_shape': fingerprint.chroma_features.shape,
            'chroma_features_b64': base64.b64encode(fingerprint.chroma_features.tobytes()).decode(),
            'tempo': fingerprint.tempo,
            'rhythm_pattern': fingerprint.rhythm_pattern,
            'harmonic_features': fingerprint.harmonic_features,
            'zero_crossing_rate': fingerprint.zero_crossing_rate,
            'spectral_centroid': fingerprint.spectral_centroid,
            'spectral_rolloff': fingerprint.spectral_rolloff,
            'confidence_score': fingerprint.confidence_score,
            'duration': fingerprint.duration,
            'sample_rate': fingerprint.sample_rate,
            'created_at': fingerprint.created_at.isoformat()
        }
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get engine information and capabilities"""
        return {
            'engine': 'EnhancedAudioFingerprintEngine',
            'version': '1.0.0',
            'capabilities': {
                'chromaprint': ACOUSTID_AVAILABLE,
                'librosa': LIBROSA_AVAILABLE,
                'ml_features': True,
                'real_time': False,
                'batch_processing': True
            },
            'config': {
                'sample_rate': self.sample_rate,
                'hop_length': self.hop_length,
                'n_mels': self.n_mels,
                'n_mfcc': self.n_mfcc,
                'max_duration': self.max_duration
            },
            'supported_formats': ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.wma']
        }