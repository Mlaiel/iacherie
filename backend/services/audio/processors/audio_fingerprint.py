"""🔍 Audio Fingerprinting - Advanced Audio Content Identification

Sophisticated audio fingerprinting system for content identification,
copyright protection, and audio matching capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import hashlib
import sqlite3
import json
from pathlib import Path
import librosa
from scipy.signal import find_peaks
from scipy.spatial.distance import hamming, euclidean
import time

# Import from existing audio processing modules
try:
    from ....ai_engine.audio_processing.fingerprinting import (
        AudioFingerprint as BaseFingerprint,
        FingerprintType,
        AudioFingerprinter as BaseFingerprinter
    )
    from ....ai_engine.audio_processing.core import AudioProcessor
except ImportError:
    # Fallback definitions if imports fail
    class FingerprintType(Enum):
        CHROMAPRINT = "chromaprint"
        LANDMARK = "landmark" 
        SPECTRAL_HASH = "spectral_hash"
        MFCC_HASH = "mfcc_hash"
        COMBINED = "combined"
    
    BaseFingerprint = None
    BaseFingerprinter = None
    AudioProcessor = None

logger = logging.getLogger(__name__)


@dataclass
class FingerprintMatch:
    """Audio fingerprint match result"""
    audio_id: str
    confidence: float
    offset_seconds: float
    duration_seconds: float
    fingerprint_type: FingerprintType
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FingerprintResult:
    """Audio fingerprinting result"""
    fingerprint_id: str
    fingerprint_data: Union[np.ndarray, str, bytes]
    fingerprint_type: FingerprintType
    audio_duration: float
    sample_rate: int
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class AudioFingerprinter:
    """
    Advanced audio fingerprinting system for content identification.
    
    Provides multiple fingerprinting algorithms for robust audio identification,
    copyright protection, and content matching.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the audio fingerprinter.
        
        Args:
            config: Configuration dictionary for fingerprinting parameters
        """
        self.config = config or {}
        self.sample_rate = self.config.get('sample_rate', 22050)
        self.hop_length = self.config.get('hop_length', 512)
        self.n_fft = self.config.get('n_fft', 2048)
        self.db_path = self.config.get('db_path', ':memory:')
        
        # Initialize database
        self._init_database()
        
        # Fingerprint storage
        self.fingerprints: Dict[str, FingerprintResult] = {}
        
        logger.info("AudioFingerprinter initialized successfully")
    
    def _init_database(self):
        """Initialize fingerprint database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS fingerprints (
                    id TEXT PRIMARY KEY,
                    audio_id TEXT,
                    fingerprint_type TEXT,
                    fingerprint_data BLOB,
                    duration REAL,
                    sample_rate INTEGER,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
            logger.info("Fingerprint database initialized")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def generate_fingerprint(
        self,
        audio_data: Union[np.ndarray, bytes, str, Path],
        fingerprint_type: FingerprintType = FingerprintType.COMBINED,
        audio_id: Optional[str] = None
    ) -> FingerprintResult:
        """
        Generate audio fingerprint for content identification.
        
        Args:
            audio_data: Audio data (numpy array, bytes, or file path)
            fingerprint_type: Type of fingerprint to generate
            audio_id: Optional identifier for the audio
            
        Returns:
            FingerprintResult: Generated fingerprint data
        """
        start_time = time.time()
        
        try:
            # Load audio data
            audio_array, sr = self._load_audio(audio_data)
            
            # Generate fingerprint based on type
            if fingerprint_type == FingerprintType.LANDMARK:
                fingerprint_data = await self._generate_landmark_fingerprint(audio_array, sr)
            elif fingerprint_type == FingerprintType.SPECTRAL_HASH:
                fingerprint_data = await self._generate_spectral_hash(audio_array, sr)
            elif fingerprint_type == FingerprintType.MFCC_HASH:
                fingerprint_data = await self._generate_mfcc_hash(audio_array, sr)
            elif fingerprint_type == FingerprintType.CHROMAPRINT:
                fingerprint_data = await self._generate_chromaprint(audio_array, sr)
            elif fingerprint_type == FingerprintType.COMBINED:
                fingerprint_data = await self._generate_combined_fingerprint(audio_array, sr)
            else:
                raise ValueError(f"Unsupported fingerprint type: {fingerprint_type}")
            
            # Create fingerprint ID
            fingerprint_id = audio_id or self._generate_fingerprint_id(fingerprint_data)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create result
            result = FingerprintResult(
                fingerprint_id=fingerprint_id,
                fingerprint_data=fingerprint_data,
                fingerprint_type=fingerprint_type,
                audio_duration=len(audio_array) / sr,
                sample_rate=sr,
                processing_time=processing_time,
                metadata={
                    'channels': 1 if audio_array.ndim == 1 else audio_array.shape[0],
                    'algorithm_version': '1.0'
                }
            )
            
            # Store fingerprint
            await self._store_fingerprint(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Fingerprint generation failed: {e}")
            raise
    
    async def match_fingerprint(
        self,
        audio_data: Union[np.ndarray, bytes, str, Path],
        threshold: float = 0.8,
        fingerprint_type: Optional[FingerprintType] = None
    ) -> List[FingerprintMatch]:
        """
        Match audio against stored fingerprints.
        
        Args:
            audio_data: Audio data to match
            threshold: Minimum confidence threshold for matches
            fingerprint_type: Specific fingerprint type to use (all if None)
            
        Returns:
            List[FingerprintMatch]: List of matches above threshold
        """
        try:
            # Generate fingerprint for the input audio
            query_fingerprint = await self.generate_fingerprint(
                audio_data, 
                fingerprint_type or FingerprintType.COMBINED
            )
            
            # Search for matches
            matches = []
            
            # Query database for stored fingerprints
            cursor = self.conn.execute('''
                SELECT id, audio_id, fingerprint_type, fingerprint_data, duration, metadata
                FROM fingerprints
                WHERE fingerprint_type = ? OR ? IS NULL
            ''', (fingerprint_type.value if fingerprint_type else None, fingerprint_type))
            
            for row in cursor.fetchall():
                stored_id, audio_id, stored_type, stored_data, duration, metadata = row
                
                # Compare fingerprints
                confidence = await self._compare_fingerprints(
                    query_fingerprint.fingerprint_data,
                    stored_data,
                    FingerprintType(stored_type)
                )
                
                if confidence >= threshold:
                    match = FingerprintMatch(
                        audio_id=audio_id,
                        confidence=confidence,
                        offset_seconds=0.0,  # Simplified - would calculate actual offset
                        duration_seconds=duration,
                        fingerprint_type=FingerprintType(stored_type),
                        metadata=json.loads(metadata) if metadata else {}
                    )
                    matches.append(match)
            
            # Sort by confidence
            matches.sort(key=lambda x: x.confidence, reverse=True)
            
            return matches
            
        except Exception as e:
            logger.error(f"Fingerprint matching failed: {e}")
            return []
    
    def _load_audio(self, audio_data: Union[np.ndarray, bytes, str, Path]) -> Tuple[np.ndarray, int]:
        """Load audio data into numpy array"""
        if isinstance(audio_data, np.ndarray):
            return audio_data, self.sample_rate
        elif isinstance(audio_data, (str, Path)):
            audio_array, sr = librosa.load(str(audio_data), sr=self.sample_rate)
            return audio_array, sr
        elif isinstance(audio_data, bytes):
            # Convert bytes to numpy array (simplified)
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            return audio_array, self.sample_rate
        else:
            raise ValueError(f"Unsupported audio data type: {type(audio_data)}")
    
    async def _generate_landmark_fingerprint(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Generate landmark-based fingerprint"""
        try:
            # Compute spectrogram
            stft = librosa.stft(audio, hop_length=self.hop_length, n_fft=self.n_fft)
            magnitude = np.abs(stft)
            
            # Find spectral peaks
            landmarks = []
            
            for t in range(magnitude.shape[1]):
                spectrum = magnitude[:, t]
                peaks, _ = find_peaks(spectrum, height=np.max(spectrum) * 0.3)
                
                # Take top peaks
                if len(peaks) > 0:
                    top_peaks = peaks[np.argsort(spectrum[peaks])[-5:]]  # Top 5 peaks
                    for peak in top_peaks:
                        landmarks.append([t, peak, spectrum[peak]])
            
            return np.array(landmarks) if landmarks else np.array([[0, 0, 0]])
            
        except Exception as e:
            logger.warning(f"Landmark fingerprint generation failed: {e}")
            return np.array([[0, 0, 0]])
    
    async def _generate_spectral_hash(self, audio: np.ndarray, sr: int) -> str:
        """Generate spectral hash fingerprint"""
        try:
            # Compute spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)[0]
            
            # Combine features
            features = np.concatenate([spectral_centroids, spectral_rolloff, spectral_bandwidth])
            
            # Create hash
            features_bytes = features.astype(np.float32).tobytes()
            hash_value = hashlib.sha256(features_bytes).hexdigest()
            
            return hash_value
            
        except Exception as e:
            logger.warning(f"Spectral hash generation failed: {e}")
            return "0" * 64
    
    async def _generate_mfcc_hash(self, audio: np.ndarray, sr: int) -> str:
        """Generate MFCC-based hash fingerprint"""
        try:
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            
            # Compute mean and std for each coefficient
            mfcc_features = np.concatenate([np.mean(mfccs, axis=1), np.std(mfccs, axis=1)])
            
            # Create hash
            features_bytes = mfcc_features.astype(np.float32).tobytes()
            hash_value = hashlib.md5(features_bytes).hexdigest()
            
            return hash_value
            
        except Exception as e:
            logger.warning(f"MFCC hash generation failed: {e}")
            return "0" * 32
    
    async def _generate_chromaprint(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Generate chroma-based fingerprint"""
        try:
            # Extract chroma features
            chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
            
            # Quantize chroma values
            chroma_quantized = (chroma > np.mean(chroma, axis=1, keepdims=True)).astype(int)
            
            return chroma_quantized
            
        except Exception as e:
            logger.warning(f"Chromaprint generation failed: {e}")
            return np.zeros((12, 1))
    
    async def _generate_combined_fingerprint(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Generate combined fingerprint using multiple algorithms"""
        try:
            fingerprints = {
                'landmark': await self._generate_landmark_fingerprint(audio, sr),
                'spectral_hash': await self._generate_spectral_hash(audio, sr),
                'mfcc_hash': await self._generate_mfcc_hash(audio, sr),
                'chromaprint': await self._generate_chromaprint(audio, sr)
            }
            
            return fingerprints
            
        except Exception as e:
            logger.warning(f"Combined fingerprint generation failed: {e}")
            return {}
    
    def _generate_fingerprint_id(self, fingerprint_data: Any) -> str:
        """Generate unique ID for fingerprint"""
        data_str = str(fingerprint_data)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    async def _store_fingerprint(self, result: FingerprintResult):
        """Store fingerprint in database"""
        try:
            # Convert fingerprint data to bytes for storage
            if isinstance(result.fingerprint_data, np.ndarray):
                data_bytes = result.fingerprint_data.tobytes()
            elif isinstance(result.fingerprint_data, str):
                data_bytes = result.fingerprint_data.encode()
            elif isinstance(result.fingerprint_data, dict):
                data_bytes = json.dumps(result.fingerprint_data, default=str).encode()
            else:
                data_bytes = str(result.fingerprint_data).encode()
            
            self.conn.execute('''
                INSERT OR REPLACE INTO fingerprints 
                (id, audio_id, fingerprint_type, fingerprint_data, duration, sample_rate, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.fingerprint_id,
                result.fingerprint_id,  # Using fingerprint_id as audio_id for simplicity
                result.fingerprint_type.value,
                data_bytes,
                result.audio_duration,
                result.sample_rate,
                json.dumps(result.metadata)
            ))
            self.conn.commit()
            
            # Also store in memory
            self.fingerprints[result.fingerprint_id] = result
            
        except Exception as e:
            logger.error(f"Failed to store fingerprint: {e}")
    
    async def _compare_fingerprints(
        self,
        fingerprint1: Any,
        fingerprint2: bytes,
        fingerprint_type: FingerprintType
    ) -> float:
        """Compare two fingerprints and return confidence score"""
        try:
            if fingerprint_type == FingerprintType.SPECTRAL_HASH or fingerprint_type == FingerprintType.MFCC_HASH:
                # String hash comparison
                hash1 = fingerprint1 if isinstance(fingerprint1, str) else str(fingerprint1)
                hash2 = fingerprint2.decode() if isinstance(fingerprint2, bytes) else str(fingerprint2)
                
                # Simple string comparison
                return 1.0 if hash1 == hash2 else 0.0
                
            elif fingerprint_type == FingerprintType.LANDMARK:
                # Landmark comparison
                if isinstance(fingerprint1, np.ndarray) and len(fingerprint2) > 0:
                    landmarks2 = np.frombuffer(fingerprint2, dtype=np.float64).reshape(-1, 3)
                    
                    # Simple overlap-based comparison
                    overlap = len(set(map(tuple, fingerprint1)) & set(map(tuple, landmarks2)))
                    max_landmarks = max(len(fingerprint1), len(landmarks2))
                    return overlap / max_landmarks if max_landmarks > 0 else 0.0
                
            elif fingerprint_type == FingerprintType.CHROMAPRINT:
                # Chroma fingerprint comparison
                if isinstance(fingerprint1, np.ndarray) and len(fingerprint2) > 0:
                    chroma2 = np.frombuffer(fingerprint2, dtype=np.int32).reshape(12, -1)
                    
                    # Calculate similarity
                    min_frames = min(fingerprint1.shape[1], chroma2.shape[1])
                    if min_frames > 0:
                        similarity = np.mean(fingerprint1[:, :min_frames] == chroma2[:, :min_frames])
                        return float(similarity)
                
            elif fingerprint_type == FingerprintType.COMBINED:
                # Combined fingerprint comparison
                if isinstance(fingerprint1, dict):
                    combined_data = json.loads(fingerprint2.decode())
                    
                    # Average similarity across all fingerprint types
                    similarities = []
                    for key in fingerprint1.keys():
                        if key in combined_data:
                            # Simplified comparison for each type
                            if key in ['spectral_hash', 'mfcc_hash']:
                                sim = 1.0 if str(fingerprint1[key]) == str(combined_data[key]) else 0.0
                            else:
                                sim = 0.5  # Default similarity for complex types
                            similarities.append(sim)
                    
                    return np.mean(similarities) if similarities else 0.0
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Fingerprint comparison failed: {e}")
            return 0.0
    
    async def get_stored_fingerprints(self) -> List[str]:
        """Get list of stored fingerprint IDs"""
        try:
            cursor = self.conn.execute('SELECT id FROM fingerprints')
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get stored fingerprints: {e}")
            return []
    
    async def remove_fingerprint(self, fingerprint_id: str) -> bool:
        """Remove a stored fingerprint"""
        try:
            self.conn.execute('DELETE FROM fingerprints WHERE id = ?', (fingerprint_id,))
            self.conn.commit()
            
            if fingerprint_id in self.fingerprints:
                del self.fingerprints[fingerprint_id]
            
            return True
        except Exception as e:
            logger.error(f"Failed to remove fingerprint: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()