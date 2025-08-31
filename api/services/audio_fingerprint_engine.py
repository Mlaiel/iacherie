"""Advanced Audio Fingerprinting Engine
Uses Chromaprint, Essentia, and spectral analysis for audio content identification

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All Rights Reserved - Unauthorized use prohibited
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Engineer

WARNING: This code is proprietary and confidential. Any unauthorized copying,
distribution, modification or use is strictly prohibited and will be prosecuted
to the full extent of the law.
"""
import hashlib
import librosa
import numpy as np
from typing import Dict, Optional, Tuple, List
import chromaprint
import acoustid
from essentia.standard import MonoLoader, Windowing, Spectrum, SpectralPeaks, HPCP
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AudioFingerprint:
    """Audio fingerprint data structure"""    chromaprint_hash: str
    spectral_hash: str
    mfcc_features: np.ndarray
    chroma_features: np.ndarray
    tempo: float
    duration: float
    sample_rate: int
    confidence_score: float


class AudioFingerprintEngine:
    """    Enterprise-grade audio fingerprinting using multiple algorithms
    Combines Chromaprint, Essentia, and custom spectral analysis
    """    
    def __init__(self, sample_rate: int = 22050, hop_length: int = 512):
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.windowing = Windowing(type='hann')
        self.spectrum = Spectrum()
        self.spectral_peaks = SpectralPeaks()
        self.hpcp = HPCP()
        
    def extract_fingerprint(self, audio_file_path: str) -> AudioFingerprint:
        """Extract comprehensive audio fingerprint from file"""        try:
            # Load audio with librosa
            y, sr = librosa.load(audio_file_path, sr=self.sample_rate)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # 1. Chromaprint fingerprint
            chromaprint_hash = self._extract_chromaprint(audio_file_path)
            
            # 2. Spectral hash using Essentia
            spectral_hash = self._extract_spectral_hash(y, sr)
            
            # 3. MFCC features
            mfcc_features = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # 4. Chroma features
            chroma_features = librosa.feature.chroma_stft(y=y, sr=sr)
            
            # 5. Tempo extraction
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            
            # 6. Calculate confidence score
            confidence_score = self._calculate_confidence(y, sr)
            
            return AudioFingerprint(
                chromaprint_hash=chromaprint_hash,
                spectral_hash=spectral_hash,
                mfcc_features=mfcc_features,
                chroma_features=chroma_features,
                tempo=float(tempo),
                duration=duration,
                sample_rate=sr,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"Error extracting audio fingerprint: {str(e)}")
            raise
            
    def _extract_chromaprint(self, audio_file_path: str) -> str:
        """Extract Chromaprint fingerprint"""        try:
            duration, fp_encoded = acoustid.fingerprint_file(audio_file_path)
            return fp_encoded
        except Exception as e:
            logger.warning(f"Chromaprint extraction failed: {str(e)}")
            return ""
            
    def _extract_spectral_hash(self, y: np.ndarray, sr: int) -> str:
        """Extract custom spectral hash using Essentia"""        try:
            # Convert to mono if stereo
            if len(y.shape) > 1:
                y = np.mean(y, axis=1)
                
            # Extract spectral features
            frame_size = 2048
            hop_size = 512
            
            spectral_centroids = []
            for i in range(0, len(y) - frame_size, hop_size):
                frame = y[i:i + frame_size]
                windowed_frame = self.windowing(frame.astype(np.float32))
                spectrum = self.spectrum(windowed_frame)
                peaks_freq, peaks_mag = self.spectral_peaks(spectrum)
                
                if len(peaks_freq) > 0:
                    centroid = np.average(peaks_freq, weights=peaks_mag)
                    spectral_centroids.append(centroid)
                    
            # Create hash from spectral centroids
            spectral_array = np.array(spectral_centroids)
            spectral_string = ''.join([f"{x:.2f}" for x in spectral_array[:100]])  # Limit size
            return hashlib.md5(spectral_string.encode()).hexdigest()
            
        except Exception as e:
            logger.warning(f"Spectral hash extraction failed: {str(e)}")
            return ""
            
    def _calculate_confidence(self, y: np.ndarray, sr: int) -> float:
        """Calculate confidence score based on audio quality metrics"""        try:
            # Signal-to-noise ratio estimation
            signal_power = np.mean(y ** 2)
            noise_floor = np.percentile(np.abs(y), 10) ** 2
            snr = 10 * np.log10(signal_power / max(noise_floor, 1e-10))
            
            # Dynamic range
            dynamic_range = np.max(np.abs(y)) - np.min(np.abs(y))
            
            # Spectral rolloff
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            rolloff_std = np.std(rolloff)
            
            # Combine metrics into confidence score (0-1)
            confidence = min(1.0, max(0.0, (snr + 20) / 40 * 0.5 + 
                                         dynamic_range * 0.3 + 
                                         min(rolloff_std / 1000, 0.2)))
            
            return confidence
            
        except Exception:
            return 0.5  # Default confidence
            
    def compare_fingerprints(self, fp1: AudioFingerprint, fp2: AudioFingerprint) -> float:
        """Compare two audio fingerprints and return similarity score (0-1)"""        try:
            scores = []
            
            # 1. Chromaprint similarity
            if fp1.chromaprint_hash and fp2.chromaprint_hash:
                chroma_sim = self._chromaprint_similarity(fp1.chromaprint_hash, fp2.chromaprint_hash)
                scores.append(chroma_sim * 0.4)  # Weight: 40%
                
            # 2. Spectral hash similarity
            if fp1.spectral_hash and fp2.spectral_hash:
                spectral_sim = 1.0 if fp1.spectral_hash == fp2.spectral_hash else 0.0
                scores.append(spectral_sim * 0.2)  # Weight: 20%
                
            # 3. MFCC similarity
            mfcc_sim = self._mfcc_similarity(fp1.mfcc_features, fp2.mfcc_features)
            scores.append(mfcc_sim * 0.3)  # Weight: 30%
            
            # 4. Tempo similarity
            tempo_diff = abs(fp1.tempo - fp2.tempo) / max(fp1.tempo, fp2.tempo, 1.0)
            tempo_sim = max(0.0, 1.0 - tempo_diff)
            scores.append(tempo_sim * 0.1)  # Weight: 10%
            
            # Weighted average
            total_similarity = sum(scores) if scores else 0.0
            
            # Apply confidence weighting
            confidence_factor = (fp1.confidence_score + fp2.confidence_score) / 2
            
            return total_similarity * confidence_factor
            
        except Exception as e:
            logger.error(f"Error comparing fingerprints: {str(e)}")
            return 0.0
            
    def _chromaprint_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate Chromaprint hash similarity"""        try:
            # Decode fingerprints
            fp1 = chromaprint.decode_fingerprint(hash1)[0]
            fp2 = chromaprint.decode_fingerprint(hash2)[0]
            
            # Calculate Hamming distance
            min_len = min(len(fp1), len(fp2))
            if min_len == 0:
                return 0.0
                
            matches = sum(1 for i in range(min_len) if fp1[i] == fp2[i])
            similarity = matches / min_len
            
            return similarity
            
        except Exception:
            return 0.0
            
    def _mfcc_similarity(self, mfcc1: np.ndarray, mfcc2: np.ndarray) -> float:
        """Calculate MFCC feature similarity using cosine similarity"""        try:
            # Average MFCC features across time
            avg_mfcc1 = np.mean(mfcc1, axis=1)
            avg_mfcc2 = np.mean(mfcc2, axis=1)
            
            # Cosine similarity
            dot_product = np.dot(avg_mfcc1, avg_mfcc2)
            norm1 = np.linalg.norm(avg_mfcc1)
            norm2 = np.linalg.norm(avg_mfcc2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            similarity = dot_product / (norm1 * norm2)
            return max(0.0, similarity)  # Ensure non-negative
            
        except Exception:
            return 0.0
            
    def batch_extract_fingerprints(self, audio_files: List[str]) -> Dict[str, AudioFingerprint]:
        """Extract fingerprints from multiple audio files"""        fingerprints = {}
        
        for audio_file in audio_files:
            try:
                fp = self.extract_fingerprint(audio_file)
                fingerprints[audio_file] = fp
                logger.info(f"Successfully extracted fingerprint for: {audio_file}")
            except Exception as e:
                logger.error(f"Failed to extract fingerprint for {audio_file}: {str(e)}")
                
        return fingerprints
        
    def find_similar_audio(self, target_fingerprint: AudioFingerprint, 
                          candidate_fingerprints: Dict[str, AudioFingerprint],
                          threshold: float = 0.8) -> List[Tuple[str, float]]:
        """Find similar audio files above threshold"""        similar_files = []
        
        for file_path, candidate_fp in candidate_fingerprints.items():
            similarity = self.compare_fingerprints(target_fingerprint, candidate_fp)
            
            if similarity >= threshold:
                similar_files.append((file_path, similarity))
                
        # Sort by similarity score (descending)
        similar_files.sort(key=lambda x: x[1], reverse=True)
        
        return similar_files
