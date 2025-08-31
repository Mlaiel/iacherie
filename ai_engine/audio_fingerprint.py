"""
Audio Fingerprinting Engine
===========================

Advanced audio fingerprinting using Chromaprint and Essentia for high-precision audio content identification.
Supports multiple audio formats and real-time fingerprint generation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import numpy as np
import hashlib
import io
import logging
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from pathlib import Path

try:
    import librosa
    import chromaprint
    import essentia
    import essentia.standard as es
except ImportError as e:
    logging.warning(f"Audio processing libraries not available: {e}")
    
from ..core.exceptions import FingerprintError
from ..utils.audio_utils import AudioProcessor
from ..database.repositories import FingerprintRepository

logger = logging.getLogger(__name__)

@dataclass
class AudioFingerprint:
    """Audio fingerprint data structure."""
    hash_value: str
    chromaprint_data: bytes
    spectral_features: Dict
    mfcc_features: np.ndarray
    tempo: float
    key: str
    energy: float
    duration: float
    sample_rate: int
    metadata: Dict

class AudioFingerprintEngine:
    """
    Professional audio fingerprinting engine with multiple algorithms.
    
    Features:
    - Chromaprint fingerprinting for audio identification
    - Spectral analysis using Essentia 
    - MFCC feature extraction
    - Tempo and key detection
    - Multi-format audio support
    - Batch processing capabilities
    """
    
    def __init__(self, 
                 sample_rate: int = 22050,
                 chunk_duration: float = 10.0,
                 overlap: float = 0.5,
                 precision_threshold: float = 0.95):
        """Initialize audio fingerprint engine."""
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.overlap = overlap
        self.precision_threshold = precision_threshold
        
        # Initialize audio processor
        self.audio_processor = AudioProcessor()
        
        # Initialize repository
        self.repository = FingerprintRepository()
        
        # Configuration
        self.config = {
            "chromaprint": {
                "algorithm": chromaprint.ALGORITHM_DEFAULT,
                "num_points": 120
            },
            "mfcc": {
                "n_mfcc": 13,
                "n_fft": 2048,
                "hop_length": 512
            },
            "spectral": {
                "n_fft": 2048,
                "hop_length": 512,
                "window": "hann"
            }
        }
        
        logger.info("AudioFingerprintEngine initialized successfully")
    
    def create_fingerprint(self, 
                          audio_data: Union[str, bytes, Path], 
                          metadata: Dict = None) -> AudioFingerprint:
        """
        Create comprehensive audio fingerprint.
        
        Args:
            audio_data: Audio file path, bytes, or Path object
            metadata: Optional metadata dictionary
            
        Returns:
            AudioFingerprint object with all computed features
        """



        try:
            # Load and preprocess audio
            y, sr = self._load_audio(audio_data)
            
            # Generate Chromaprint fingerprint
            chromaprint_data = self._generate_chromaprint(y, sr)
            
            # Extract spectral features
            spectral_features = self._extract_spectral_features(y, sr)
            
            # Extract MFCC features
            mfcc_features = self._extract_mfcc_features(y, sr)
            
            # Detect tempo and key
            tempo = self._detect_tempo(y, sr)
            key = self._detect_key(y, sr)
            
            # Calculate energy
            energy = self._calculate_energy(y)
            
            # Generate combined hash
            hash_value = self._generate_combined_hash(
                chromaprint_data, spectral_features, mfcc_features
            )
            
            # Create fingerprint object
            fingerprint = AudioFingerprint(
                hash_value=hash_value,
                chromaprint_data=chromaprint_data,
                spectral_features=spectral_features,
                mfcc_features=mfcc_features,
                tempo=tempo,
                key=key,
                energy=energy,
                duration=len(y) / sr,
                sample_rate=sr,
                metadata=metadata or {}
            )
            
            logger.info(f"Audio fingerprint created: {hash_value[:16]}...")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Error creating audio fingerprint: {str(e)}")
            raise FingerprintError(f"Failed to create audio fingerprint: {str(e)}")
    
    def match_fingerprint(self, 
                         fingerprint: AudioFingerprint,
                         similarity_threshold: float = 0.85) -> List[Dict]:
        """
        Match audio fingerprint against database.
        
        Args:
            fingerprint: AudioFingerprint to match
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of matching fingerprints with similarity scores
        """



        try:
            # Query database for potential matches
            candidates = self.repository.find_similar_audio_fingerprints(
                fingerprint.hash_value,
                fingerprint.spectral_features,
                threshold=similarity_threshold
            )
            
            matches = []
            for candidate in candidates:
                # Calculate similarity score
                similarity = self._calculate_similarity(fingerprint, candidate)
                
                if similarity >= similarity_threshold:
                    matches.append({
                        "fingerprint_id": candidate["id"],
                        "similarity_score": similarity,
                        "matched_features": self._get_matched_features(fingerprint, candidate),
                        "metadata": candidate.get("metadata", {})
                    })
            
            # Sort by similarity score
            matches.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            logger.info(f"Found {len(matches)} matches above threshold {similarity_threshold}")
            return matches
            
        except Exception as e:
            logger.error(f"Error matching audio fingerprint: {str(e)}")
            raise FingerprintError(f"Failed to match audio fingerprint: {str(e)}")
    
    def _load_audio(self, audio_data: Union[str, bytes, Path]) -> Tuple[np.ndarray, int]:
        """Load audio from various sources."""



        try:
            if isinstance(audio_data, (str, Path)):
                # Load from file
                y, sr = librosa.load(str(audio_data), sr=self.sample_rate)
            elif isinstance(audio_data, bytes):
                # Load from bytes
                audio_io = io.BytesIO(audio_data)
                y, sr = librosa.load(audio_io, sr=self.sample_rate)
            else:
                raise ValueError("Unsupported audio data format")
            
            # Normalize audio
            y = librosa.util.normalize(y)
            
            return y, sr
            
        except Exception as e:
            raise FingerprintError(f"Failed to load audio: {str(e)}")
    
    def _generate_chromaprint(self, y: np.ndarray, sr: int) -> bytes:
        """Generate Chromaprint fingerprint."""



        try:
            # Convert to int16 for chromaprint
            audio_int16 = (y * 32767).astype(np.int16)
            
            # Generate fingerprint
            fingerprint_data = chromaprint.encode_fingerprint(
                chromaprint.hash_fingerprint(
                    chromaprint.decode_fingerprint(
                        chromaprint.fingerprint(audio_int16, sr)[1]
                    )[0]
                )
            )
            
            return fingerprint_data
            
        except Exception as e:
            raise FingerprintError(f"Failed to generate chromaprint: {str(e)}")
    
    def _extract_spectral_features(self, y: np.ndarray, sr: int) -> Dict:
        """Extract spectral features using Essentia."""



        try:
            # Convert to essentia format
            audio_essentia = es.MonoLoader(filename='', sampleRate=sr)(y.astype(np.float32))
            
            # Spectral features
            spectral_centroid = es.SpectralCentroidTime()
            spectral_rolloff = es.SpectralRolloffTime() 
            spectral_flux = es.SpectralFlux()
            zero_crossing_rate = es.ZeroCrossingRate()
            
            # Extract features
            features = {
                "spectral_centroid": float(np.mean(spectral_centroid(audio_essentia))),
                "spectral_rolloff": float(np.mean(spectral_rolloff(audio_essentia))),
                "spectral_flux": float(np.mean(spectral_flux(audio_essentia))),
                "zero_crossing_rate": float(zero_crossing_rate(audio_essentia))
            }
            
            return features
            
        except Exception as e:
            logger.warning(f"Essentia not available, using librosa fallback: {str(e)}")
            return self._extract_spectral_features_librosa(y, sr)
    
    def _extract_spectral_features_librosa(self, y: np.ndarray, sr: int) -> Dict:
        """Extract spectral features using librosa fallback."""
        features = {
            "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
            "spectral_rolloff": float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))),
            "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(y))),
            "spectral_bandwidth": float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))
        }
        return features
    
    def _extract_mfcc_features(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Extract MFCC features."""



        try:
            mfccs = librosa.feature.mfcc(
                y=y, 
                sr=sr,
                n_mfcc=self.config["mfcc"]["n_mfcc"],
                n_fft=self.config["mfcc"]["n_fft"],
                hop_length=self.config["mfcc"]["hop_length"]
            )
            
            # Return mean across time
            return np.mean(mfccs, axis=1)
            
        except Exception as e:
            raise FingerprintError(f"Failed to extract MFCC features: {str(e)}")
    
    def _detect_tempo(self, y: np.ndarray, sr: int) -> float:
        """Detect tempo using librosa."""



        try:
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            return float(tempo)
        except Exception:
            return 0.0
    
    def _detect_key(self, y: np.ndarray, sr: int) -> str:
        """Detect musical key."""



        try:
            # Simplified key detection using chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            chroma_mean = np.mean(chroma, axis=1)
            
            # Key mapping (simplified)
            keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            key_idx = np.argmax(chroma_mean)
            
            return keys[key_idx]
        except Exception:
            return "unknown"
    
    def _calculate_energy(self, y: np.ndarray) -> float:
        """Calculate audio energy."""



        return float(np.mean(y ** 2))
    
    def _generate_combined_hash(self, 
                               chromaprint_data: bytes,
                               spectral_features: Dict,
                               mfcc_features: np.ndarray) -> str:
        """Generate combined hash from all features."""



        try:
            # Combine all features into a single byte string
            combined_data = chromaprint_data
            combined_data += str(spectral_features).encode('utf-8')
            combined_data += mfcc_features.tobytes()
            
            # Generate SHA-256 hash
            hash_obj = hashlib.sha256(combined_data)
            return hash_obj.hexdigest()
            
        except Exception as e:
            raise FingerprintError(f"Failed to generate combined hash: {str(e)}")
    
    def _calculate_similarity(self, fp1: AudioFingerprint, fp2: Dict) -> float:
        """Calculate similarity between two audio fingerprints."""



        try:
            # Chromaprint similarity (primary)
            chromaprint_sim = self._chromaprint_similarity(
                fp1.chromaprint_data, fp2.get("chromaprint_data", b"")
            )
            
            # Spectral features similarity
            spectral_sim = self._spectral_similarity(
                fp1.spectral_features, fp2.get("spectral_features", {})
            )
            
            # MFCC similarity
            mfcc_sim = self._mfcc_similarity(
                fp1.mfcc_features, fp2.get("mfcc_features", np.array([]))
            )
            
            # Weighted combination
            weights = {"chromaprint": 0.6, "spectral": 0.25, "mfcc": 0.15}
            
            combined_similarity = (
                weights["chromaprint"] * chromaprint_sim +
                weights["spectral"] * spectral_sim +
                weights["mfcc"] * mfcc_sim
            )
            
            return combined_similarity
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def _chromaprint_similarity(self, data1: bytes, data2: bytes) -> float:
        """Calculate Chromaprint similarity."""



        try:
            if not data1 or not data2:
                return 0.0
            
            # Simple byte comparison (can be enhanced with proper chromaprint comparison)
            if data1 == data2:
                return 1.0
            
            # Calculate Hamming distance approximation
            min_len = min(len(data1), len(data2))
            if min_len == 0:
                return 0.0
            
            matches = sum(a == b for a, b in zip(data1[:min_len], data2[:min_len]))
            return matches / min_len
            
        except Exception:
            return 0.0
    
    def _spectral_similarity(self, features1: Dict, features2: Dict) -> float:
        """Calculate spectral features similarity."""



        try:
            if not features1 or not features2:
                return 0.0
            
            similarities = []
            common_keys = set(features1.keys()) & set(features2.keys())
            
            for key in common_keys:
                val1, val2 = features1[key], features2[key]
                if val1 == 0 and val2 == 0:
                    sim = 1.0
                else:
                    sim = 1.0 - abs(val1 - val2) / max(abs(val1), abs(val2), 1.0)
                similarities.append(sim)
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception:
            return 0.0
    
    def _mfcc_similarity(self, mfcc1: np.ndarray, mfcc2: np.ndarray) -> float:
        """Calculate MFCC similarity using cosine similarity."""



        try:
            if mfcc1.size == 0 or mfcc2.size == 0:
                return 0.0
            
            # Ensure same dimensions
            min_len = min(len(mfcc1), len(mfcc2))
            mfcc1_norm = mfcc1[:min_len]
            mfcc2_norm = mfcc2[:min_len]
            
            # Cosine similarity
            dot_product = np.dot(mfcc1_norm, mfcc2_norm)
            norm1 = np.linalg.norm(mfcc1_norm)
            norm2 = np.linalg.norm(mfcc2_norm)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception:
            return 0.0
    
    def _get_matched_features(self, fp1: AudioFingerprint, fp2: Dict) -> List[str]:
        """Get list of matched features."""
        matched = []
        
        # Check tempo similarity
        tempo1 = fp1.tempo
        tempo2 = fp2.get("tempo", 0)
        if abs(tempo1 - tempo2) < 5:  # Within 5 BPM
            matched.append("tempo")
        
        # Check key match
        if fp1.key == fp2.get("key"):
            matched.append("key")
        
        # Check duration similarity
        duration1 = fp1.duration
        duration2 = fp2.get("duration", 0)
        if abs(duration1 - duration2) < 2:  # Within 2 seconds
            matched.append("duration")
        
        return matched
    
    def batch_process(self, audio_files: List[Union[str, Path]]) -> List[AudioFingerprint]:
        """Process multiple audio files in batch."""
        fingerprints = []
        
        for audio_file in audio_files:
            try:
                fingerprint = self.create_fingerprint(audio_file)
                fingerprints.append(fingerprint)
                logger.info(f"Processed: {audio_file}")
            except Exception as e:
                logger.error(f"Failed to process {audio_file}: {str(e)}")
        
        return fingerprints
    
    def get_engine_stats(self) -> Dict:
        """Get engine statistics."""



        return {
            "version": "1.0.0",
            "sample_rate": self.sample_rate,
            "chunk_duration": self.chunk_duration,
            "overlap": self.overlap,
            "precision_threshold": self.precision_threshold,
            "supported_formats": ["wav", "mp3", "flac", "aac", "ogg"],
            "algorithms": ["chromaprint", "essentia", "librosa"]
        }
