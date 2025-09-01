"""🔬 Audio Fingerprinting Module - Advanced Content Identification Engine

Professional audio fingerprinting and content matching system for the IA Influencer Agent platform.
Implements state-of-the-art audio identification algorithms for copyright protection and content discovery.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Union, Any, Set
import numpy as np
import hashlib
import pickle
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import time
import librosa
from scipy.signal import find_peaks
from scipy.spatial.distance import hamming
import sqlite3
import json

from .core import AudioProcessor, AudioFeatures
from .config import AudioProcessingConfig

logger = logging.getLogger(__name__)


class FingerprintType(Enum):
    """Audio fingerprint algorithm types"""
    CHROMAPRINT = "chromaprint"
    LANDMARK = "landmark"
    SPECTRAL_HASH = "spectral_hash"
    MFCC_HASH = "mfcc_hash"
    COMBINED = "combined"


@dataclass
class AudioFingerprint:
    """Audio fingerprint representation"""
    fingerprint_data: Union[np.ndarray, str, bytes]
    fingerprint_type: FingerprintType
    audio_id: str
    duration: float
    sample_rate: int
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert fingerprint to dictionary for storage"""
        return {
            'fingerprint_data': self._serialize_fingerprint_data(),
            'fingerprint_type': self.fingerprint_type.value,
            'audio_id': self.audio_id,
            'duration': self.duration,
            'sample_rate': self.sample_rate,
            'timestamp': self.timestamp,
            'metadata': self.metadata,
            'confidence': self.confidence
        }
    
    def _serialize_fingerprint_data(self) -> str:
        """Serialize fingerprint data for storage"""
        if isinstance(self.fingerprint_data, np.ndarray):
            return pickle.dumps(self.fingerprint_data).hex()
        elif isinstance(self.fingerprint_data, bytes):
            return self.fingerprint_data.hex()
        else:
            return str(self.fingerprint_data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioFingerprint':
        """Create fingerprint from dictionary"""
        fingerprint_type = FingerprintType(data['fingerprint_type'])
        
        # Deserialize fingerprint data
        fingerprint_data = data['fingerprint_data']
        if fingerprint_type in [FingerprintType.LANDMARK, FingerprintType.SPECTRAL_HASH, FingerprintType.MFCC_HASH]:
            fingerprint_data = pickle.loads(bytes.fromhex(fingerprint_data))
        elif fingerprint_type == FingerprintType.CHROMAPRINT:
            fingerprint_data = bytes.fromhex(fingerprint_data)
        
        return cls(
            fingerprint_data=fingerprint_data,
            fingerprint_type=fingerprint_type,
            audio_id=data['audio_id'],
            duration=data['duration'],
            sample_rate=data['sample_rate'],
            timestamp=data['timestamp'],
            metadata=data.get('metadata', {}),
            confidence=data.get('confidence', 1.0)
        )


@dataclass
class MatchResult:
    """Audio content matching result"""
    matched_audio_id: str
    similarity_score: float
    confidence: float
    match_type: FingerprintType
    time_offset: Optional[float] = None
    duration_overlap: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class SpectralLandmarkExtractor:
    """
    🗺️ Spectral Landmark Extraction Engine
    
    Advanced landmark-based fingerprinting similar to Shazam algorithm:
    - Peak detection in spectral domain
    - Combinatorial hash generation
    - Time-frequency constellation mapping
    - Robust to noise and distortion
    """
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 window_size: int = 4096,
                 hop_length: int = 1024):
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.hop_length = hop_length
        
        # Landmark extraction parameters
        self.min_peak_height = 0.1
        self.min_peak_distance = 10
        self.target_zone_size = 5
        self.max_time_delta = 200  # frames
        
        logger.debug(f"SpectralLandmarkExtractor initialized: "
                    f"sr={sample_rate}, win={window_size}, hop={hop_length}")
    
    async def extract_landmarks(self, audio_data: np.ndarray) -> List[Tuple[int, int, int]]:
        """
        Extract spectral landmarks from audio
        
        Args:
            audio_data: Input audio samples
            
        Returns:
            List of landmarks as (time_frame, freq_bin, target_time_frame) tuples
        """
        try:
            # Compute spectrogram
            stft = librosa.stft(
                audio_data, 
                n_fft=self.window_size, 
                hop_length=self.hop_length
            )
            magnitude = np.abs(stft)
            
            # Convert to dB and normalize
            magnitude_db = librosa.amplitude_to_db(magnitude)
            magnitude_db = (magnitude_db - np.min(magnitude_db)) / (
                np.max(magnitude_db) - np.min(magnitude_db) + 1e-10
            )
            
            # Find peaks in each time frame
            landmarks = []
            
            for time_frame in range(magnitude_db.shape[1]):
                frame_data = magnitude_db[:, time_frame]
                
                # Find peaks in frequency domain
                peaks, properties = find_peaks(
                    frame_data,
                    height=self.min_peak_height,
                    distance=self.min_peak_distance
                )
                
                # Sort peaks by magnitude (strongest first)
                if len(peaks) > 0:
                    peak_heights = frame_data[peaks]
                    sorted_indices = np.argsort(peak_heights)[::-1]
                    peaks = peaks[sorted_indices]
                    
                    # Take top peaks (limit to avoid too many landmarks)
                    peaks = peaks[:min(5, len(peaks))]
                    
                    # Create landmarks by pairing with future peaks
                    for peak_freq in peaks:
                        landmarks.extend(
                            self._create_landmark_pairs(
                                time_frame, peak_freq, magnitude_db
                            )
                        )
            
            logger.debug(f"Extracted {len(landmarks)} spectral landmarks")
            return landmarks
            
        except Exception as e:
            logger.error(f"Landmark extraction failed: {e}")
            return []
    
    def _create_landmark_pairs(self, 
                             anchor_time: int, 
                             anchor_freq: int, 
                             magnitude_db: np.ndarray) -> List[Tuple[int, int, int]]:
        """Create landmark pairs from anchor point"""
        landmarks = []
        
        # Define target zone (future time frames)
        start_time = anchor_time + 1
        end_time = min(
            anchor_time + self.max_time_delta, 
            magnitude_db.shape[1]
        )
        
        if start_time >= end_time:
            return landmarks
        
        # Find peaks in target zone
        for target_time in range(start_time, end_time, 5):  # Sample every 5 frames
            if target_time < magnitude_db.shape[1]:
                frame_data = magnitude_db[:, target_time]
                
                # Find peaks in this frame
                peaks, _ = find_peaks(
                    frame_data,
                    height=self.min_peak_height,
                    distance=self.min_peak_distance
                )
                
                # Create landmarks with top peaks
                peak_heights = frame_data[peaks] if len(peaks) > 0 else []
                if len(peak_heights) > 0:
                    sorted_indices = np.argsort(peak_heights)[::-1]
                    top_peaks = peaks[sorted_indices[:self.target_zone_size]]
                    
                    for target_freq in top_peaks:
                        # Create landmark triplet
                        landmark = (anchor_time, anchor_freq, target_time)
                        landmarks.append(landmark)
        
        return landmarks
    
    def landmarks_to_hashes(self, landmarks: List[Tuple[int, int, int]]) -> Set[int]:
        """Convert landmarks to hash set for fast matching"""
        hashes = set()
        
        for anchor_time, anchor_freq, target_time in landmarks:
            # Create combinatorial hash
            # Format: freq1 | (freq2 << 8) | (time_delta << 16)
            time_delta = target_time - anchor_time
            
            # Combine frequencies and time delta into hash
            hash_value = (
                anchor_freq |
                (anchor_freq << 8) |  # Use anchor freq twice for simplicity
                (time_delta << 16)
            )
            
            hashes.add(hash_value)
        
        return hashes


class AudioFingerprinter:
    """
    🔍 Professional Audio Fingerprinting Engine
    
    Advanced multi-algorithm fingerprinting system:
    - Multiple fingerprinting algorithms
    - Robust content identification
    - Real-time processing capabilities
    - Database integration
    - Copyright protection support
    """
    
    def __init__(self, 
                 config: Optional[AudioProcessingConfig] = None,
                 database_path: Optional[Path] = None):
        self.config = config or AudioProcessingConfig()
        self.audio_processor = AudioProcessor(config)
        
        # Initialize fingerprinting algorithms
        self.landmark_extractor = SpectralLandmarkExtractor()
        
        # Database setup
        self.database_path = database_path or Path("fingerprint_database.db")
        self._init_database()
        
        logger.info(f"AudioFingerprinter initialized with database: {self.database_path}")
    
    def _init_database(self):
        """Initialize fingerprint database"""
        try:
            with sqlite3.connect(str(self.database_path)) as conn:
                cursor = conn.cursor()
                
                # Create fingerprints table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS fingerprints (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        audio_id TEXT NOT NULL,
                        fingerprint_type TEXT NOT NULL,
                        fingerprint_data TEXT NOT NULL,
                        duration REAL NOT NULL,
                        sample_rate INTEGER NOT NULL,
                        timestamp REAL NOT NULL,
                        metadata TEXT,
                        confidence REAL DEFAULT 1.0,
                        UNIQUE(audio_id, fingerprint_type)
                    )
                ''')
                
                # Create index for fast lookups
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_audio_id 
                    ON fingerprints(audio_id)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_fingerprint_type 
                    ON fingerprints(fingerprint_type)
                ''')
                
                conn.commit()
                
            logger.debug("Fingerprint database initialized")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    async def generate_fingerprint(self,
                                 audio_data: np.ndarray,
                                 sample_rate: int,
                                 audio_id: str,
                                 fingerprint_type: FingerprintType = FingerprintType.COMBINED) -> AudioFingerprint:
        """
        Generate audio fingerprint using specified algorithm
        
        Args:
            audio_data: Input audio samples
            sample_rate: Sample rate
            audio_id: Unique audio identifier
            fingerprint_type: Fingerprinting algorithm to use
            
        Returns:
            AudioFingerprint object
        """
        try:
            duration = len(audio_data) / sample_rate
            
            if fingerprint_type == FingerprintType.LANDMARK:
                fingerprint_data = await self._generate_landmark_fingerprint(audio_data)
            elif fingerprint_type == FingerprintType.SPECTRAL_HASH:
                fingerprint_data = await self._generate_spectral_hash_fingerprint(audio_data, sample_rate)
            elif fingerprint_type == FingerprintType.MFCC_HASH:
                fingerprint_data = await self._generate_mfcc_hash_fingerprint(audio_data, sample_rate)
            elif fingerprint_type == FingerprintType.CHROMAPRINT:
                fingerprint_data = await self._generate_chromaprint_fingerprint(audio_data, sample_rate)
            elif fingerprint_type == FingerprintType.COMBINED:
                fingerprint_data = await self._generate_combined_fingerprint(audio_data, sample_rate)
            else:
                raise ValueError(f"Unknown fingerprint type: {fingerprint_type}")
            
            fingerprint = AudioFingerprint(
                fingerprint_data=fingerprint_data,
                fingerprint_type=fingerprint_type,
                audio_id=audio_id,
                duration=duration,
                sample_rate=sample_rate,
                confidence=1.0
            )
            
            logger.debug(f"Generated {fingerprint_type.value} fingerprint for {audio_id}")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Fingerprint generation failed: {e}")
            raise
    
    async def _generate_landmark_fingerprint(self, audio_data: np.ndarray) -> Set[int]:
        """Generate landmark-based fingerprint"""
        landmarks = await self.landmark_extractor.extract_landmarks(audio_data)
        hashes = self.landmark_extractor.landmarks_to_hashes(landmarks)
        return hashes
    
    async def _generate_spectral_hash_fingerprint(self, 
                                                audio_data: np.ndarray, 
                                                sample_rate: int) -> np.ndarray:
        """Generate spectral hash fingerprint"""
        try:
            # Compute mel spectrogram
            mel_spec = librosa.feature.melspectrogram(
                y=audio_data,
                sr=sample_rate,
                n_mels=32,  # Reduced for hash generation
                hop_length=1024
            )
            
            # Convert to dB and normalize
            mel_spec_db = librosa.power_to_db(mel_spec)
            
            # Create binary hash based on spectral differences
            hash_matrix = np.zeros_like(mel_spec_db, dtype=bool)
            
            # Compare adjacent frequency bins
            for i in range(mel_spec_db.shape[0] - 1):
                hash_matrix[i] = mel_spec_db[i] > mel_spec_db[i + 1]
            
            # Flatten to 1D hash
            spectral_hash = hash_matrix.flatten()
            
            return spectral_hash
            
        except Exception as e:
            logger.error(f"Spectral hash generation failed: {e}")
            return np.array([])
    
    async def _generate_mfcc_hash_fingerprint(self, 
                                            audio_data: np.ndarray, 
                                            sample_rate: int) -> np.ndarray:
        """Generate MFCC-based hash fingerprint"""
        try:
            # Extract MFCC features
            mfcc = librosa.feature.mfcc(
                y=audio_data,
                sr=sample_rate,
                n_mfcc=20,  # Increased for better discrimination
                hop_length=1024
            )
            
            # Normalize MFCC
            mfcc_mean = np.mean(mfcc, axis=1, keepdims=True)
            mfcc_normalized = mfcc - mfcc_mean
            
            # Create binary hash based on sign
            mfcc_hash = mfcc_normalized > 0
            
            return mfcc_hash.flatten()
            
        except Exception as e:
            logger.error(f"MFCC hash generation failed: {e}")
            return np.array([])
    
    async def _generate_chromaprint_fingerprint(self, 
                                              audio_data: np.ndarray, 
                                              sample_rate: int) -> bytes:
        """Generate Chromaprint-style fingerprint"""
        try:
            # Extract chroma features
            chroma = librosa.feature.chroma_cqt(
                y=audio_data,
                sr=sample_rate,
                hop_length=1024
            )
            
            # Normalize chroma
            chroma_normalized = chroma / (np.sum(chroma, axis=0, keepdims=True) + 1e-10)
            
            # Create hash based on chroma differences
            hash_bits = []
            
            for i in range(chroma_normalized.shape[1] - 1):
                current_frame = chroma_normalized[:, i]
                next_frame = chroma_normalized[:, i + 1]
                
                # Compare adjacent frames
                diff = next_frame - current_frame
                hash_bits.extend((diff > 0).astype(int))
            
            # Convert to bytes
            hash_array = np.array(hash_bits)
            
            # Pad to byte boundary
            padding = 8 - (len(hash_array) % 8)
            if padding != 8:
                hash_array = np.pad(hash_array, (0, padding))
            
            # Pack into bytes
            hash_bytes = np.packbits(hash_array).tobytes()
            
            return hash_bytes
            
        except Exception as e:
            logger.error(f"Chromaprint generation failed: {e}")
            return b''
    
    async def _generate_combined_fingerprint(self, 
                                           audio_data: np.ndarray, 
                                           sample_rate: int) -> Dict[str, Any]:
        """Generate combined fingerprint using multiple algorithms"""
        try:
            combined = {}
            
            # Generate multiple fingerprints
            combined['landmark'] = await self._generate_landmark_fingerprint(audio_data)
            combined['spectral_hash'] = await self._generate_spectral_hash_fingerprint(audio_data, sample_rate)
            combined['mfcc_hash'] = await self._generate_mfcc_hash_fingerprint(audio_data, sample_rate)
            combined['chromaprint'] = await self._generate_chromaprint_fingerprint(audio_data, sample_rate)
            
            return combined
            
        except Exception as e:
            logger.error(f"Combined fingerprint generation failed: {e}")
            return {}
    
    async def store_fingerprint(self, fingerprint: AudioFingerprint) -> bool:
        """Store fingerprint in database"""
        try:
            with sqlite3.connect(str(self.database_path)) as conn:
                cursor = conn.cursor()
                
                fingerprint_dict = fingerprint.to_dict()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO fingerprints 
                    (audio_id, fingerprint_type, fingerprint_data, duration, 
                     sample_rate, timestamp, metadata, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    fingerprint.audio_id,
                    fingerprint.fingerprint_type.value,
                    fingerprint_dict['fingerprint_data'],
                    fingerprint.duration,
                    fingerprint.sample_rate,
                    fingerprint.timestamp,
                    json.dumps(fingerprint.metadata),
                    fingerprint.confidence
                ))
                
                conn.commit()
                
            logger.debug(f"Stored fingerprint for {fingerprint.audio_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store fingerprint: {e}")
            return False
    
    async def load_fingerprint(self, 
                             audio_id: str, 
                             fingerprint_type: FingerprintType) -> Optional[AudioFingerprint]:
        """Load fingerprint from database"""
        try:
            with sqlite3.connect(str(self.database_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM fingerprints 
                    WHERE audio_id = ? AND fingerprint_type = ?
                ''', (audio_id, fingerprint_type.value))
                
                row = cursor.fetchone()
                
                if row:
                    # Reconstruct fingerprint
                    fingerprint_data = {
                        'fingerprint_data': row[3],
                        'fingerprint_type': row[2],
                        'audio_id': row[1],
                        'duration': row[4],
                        'sample_rate': row[5],
                        'timestamp': row[6],
                        'metadata': json.loads(row[7]) if row[7] else {},
                        'confidence': row[8] if row[8] is not None else 1.0
                    }
                    
                    return AudioFingerprint.from_dict(fingerprint_data)
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to load fingerprint: {e}")
            return None
    
    async def generate_and_store_fingerprint(self,
                                           audio_data: np.ndarray,
                                           sample_rate: int,
                                           audio_id: str,
                                           fingerprint_type: FingerprintType = FingerprintType.COMBINED) -> AudioFingerprint:
        """Generate and store fingerprint in one operation"""
        fingerprint = await self.generate_fingerprint(
            audio_data, sample_rate, audio_id, fingerprint_type
        )
        
        await self.store_fingerprint(fingerprint)
        
        return fingerprint


class ContentMatcher:
    """
    🎯 Advanced Audio Content Matching Engine
    
    High-performance content matching system:
    - Multi-algorithm matching strategies
    - Real-time content identification
    - Similarity scoring and ranking
    - Copyright violation detection
    - Content discovery and recommendation
    """
    
    def __init__(self, 
                 fingerprinter: AudioFingerprinter,
                 config: Optional[AudioProcessingConfig] = None):
        self.fingerprinter = fingerprinter
        self.config = config or AudioProcessingConfig()
        
        # Matching parameters
        self.similarity_thresholds = {
            FingerprintType.LANDMARK: 0.3,
            FingerprintType.SPECTRAL_HASH: 0.7,
            FingerprintType.MFCC_HASH: 0.6,
            FingerprintType.CHROMAPRINT: 0.5,
            FingerprintType.COMBINED: 0.4
        }
        
        logger.info("ContentMatcher initialized")
    
    async def find_matches(self,
                         query_fingerprint: AudioFingerprint,
                         max_results: int = 10,
                         min_similarity: Optional[float] = None) -> List[MatchResult]:
        """
        Find matching content for query fingerprint
        
        Args:
            query_fingerprint: Query audio fingerprint
            max_results: Maximum number of results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of match results sorted by similarity
        """
        try:
            if min_similarity is None:
                min_similarity = self.similarity_thresholds.get(
                    query_fingerprint.fingerprint_type, 0.5
                )
            
            # Load all fingerprints of the same type from database
            candidate_fingerprints = await self._load_candidate_fingerprints(
                query_fingerprint.fingerprint_type
            )
            
            if not candidate_fingerprints:
                logger.warning(f"No candidate fingerprints found for type: "
                             f"{query_fingerprint.fingerprint_type.value}")
                return []
            
            # Calculate similarities
            matches = []
            
            for candidate in candidate_fingerprints:
                if candidate.audio_id == query_fingerprint.audio_id:
                    continue  # Skip self-matches
                
                similarity = await self._calculate_similarity(
                    query_fingerprint, candidate
                )
                
                if similarity >= min_similarity:
                    match_result = MatchResult(
                        matched_audio_id=candidate.audio_id,
                        similarity_score=similarity,
                        confidence=min(query_fingerprint.confidence, candidate.confidence),
                        match_type=query_fingerprint.fingerprint_type,
                        metadata=candidate.metadata
                    )
                    matches.append(match_result)
            
            # Sort by similarity (descending)
            matches.sort(key=lambda x: x.similarity_score, reverse=True)
            
            # Return top results
            matches = matches[:max_results]
            
            logger.info(f"Found {len(matches)} matches for {query_fingerprint.audio_id}")
            return matches
            
        except Exception as e:
            logger.error(f"Content matching failed: {e}")
            return []
    
    async def _load_candidate_fingerprints(self, 
                                         fingerprint_type: FingerprintType) -> List[AudioFingerprint]:
        """Load candidate fingerprints from database"""
        try:
            candidates = []
            
            with sqlite3.connect(str(self.fingerprinter.database_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM fingerprints 
                    WHERE fingerprint_type = ?
                    ORDER BY timestamp DESC
                ''', (fingerprint_type.value,))
                
                rows = cursor.fetchall()
                
                for row in rows:
                    fingerprint_data = {
                        'fingerprint_data': row[3],
                        'fingerprint_type': row[2],
                        'audio_id': row[1],
                        'duration': row[4],
                        'sample_rate': row[5],
                        'timestamp': row[6],
                        'metadata': json.loads(row[7]) if row[7] else {},
                        'confidence': row[8] if row[8] is not None else 1.0
                    }
                    
                    fingerprint = AudioFingerprint.from_dict(fingerprint_data)
                    candidates.append(fingerprint)
            
            logger.debug(f"Loaded {len(candidates)} candidate fingerprints")
            return candidates
            
        except Exception as e:
            logger.error(f"Failed to load candidate fingerprints: {e}")
            return []
    
    async def _calculate_similarity(self,
                                  query_fp: AudioFingerprint,
                                  candidate_fp: AudioFingerprint) -> float:
        """Calculate similarity between two fingerprints"""
        try:
            fingerprint_type = query_fp.fingerprint_type
            
            if fingerprint_type == FingerprintType.LANDMARK:
                return self._calculate_landmark_similarity(
                    query_fp.fingerprint_data, candidate_fp.fingerprint_data
                )
            elif fingerprint_type == FingerprintType.SPECTRAL_HASH:
                return self._calculate_hash_similarity(
                    query_fp.fingerprint_data, candidate_fp.fingerprint_data
                )
            elif fingerprint_type == FingerprintType.MFCC_HASH:
                return self._calculate_hash_similarity(
                    query_fp.fingerprint_data, candidate_fp.fingerprint_data
                )
            elif fingerprint_type == FingerprintType.CHROMAPRINT:
                return self._calculate_chromaprint_similarity(
                    query_fp.fingerprint_data, candidate_fp.fingerprint_data
                )
            elif fingerprint_type == FingerprintType.COMBINED:
                return self._calculate_combined_similarity(
                    query_fp.fingerprint_data, candidate_fp.fingerprint_data
                )
            else:
                logger.warning(f"Unknown fingerprint type for similarity: {fingerprint_type}")
                return 0.0
                
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    def _calculate_landmark_similarity(self, 
                                     query_hashes: Set[int], 
                                     candidate_hashes: Set[int]) -> float:
        """Calculate similarity for landmark fingerprints"""
        if not query_hashes or not candidate_hashes:
            return 0.0
        
        # Jaccard similarity
        intersection = len(query_hashes.intersection(candidate_hashes))
        union = len(query_hashes.union(candidate_hashes))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_hash_similarity(self, 
                                 query_hash: np.ndarray, 
                                 candidate_hash: np.ndarray) -> float:
        """Calculate similarity for binary hash fingerprints"""
        if len(query_hash) == 0 or len(candidate_hash) == 0:
            return 0.0
        
        # Ensure same length (pad or truncate)
        min_length = min(len(query_hash), len(candidate_hash))
        query_hash = query_hash[:min_length]
        candidate_hash = candidate_hash[:min_length]
        
        # Hamming distance similarity
        hamming_dist = hamming(query_hash, candidate_hash)
        return 1.0 - hamming_dist
    
    def _calculate_chromaprint_similarity(self, 
                                        query_bytes: bytes, 
                                        candidate_bytes: bytes) -> float:
        """Calculate similarity for Chromaprint fingerprints"""
        if not query_bytes or not candidate_bytes:
            return 0.0
        
        # Convert bytes to bit arrays
        query_bits = np.unpackbits(np.frombuffer(query_bytes, dtype=np.uint8))
        candidate_bits = np.unpackbits(np.frombuffer(candidate_bytes, dtype=np.uint8))
        
        # Calculate similarity
        return self._calculate_hash_similarity(query_bits, candidate_bits)
    
    def _calculate_combined_similarity(self, 
                                     query_combined: Dict[str, Any], 
                                     candidate_combined: Dict[str, Any]) -> float:
        """Calculate similarity for combined fingerprints"""
        if not query_combined or not candidate_combined:
            return 0.0
        
        similarities = []
        weights = {
            'landmark': 0.4,
            'spectral_hash': 0.2,
            'mfcc_hash': 0.2,
            'chromaprint': 0.2
        }
        
        total_weight = 0.0
        
        for fingerprint_name, weight in weights.items():
            if (fingerprint_name in query_combined and 
                fingerprint_name in candidate_combined):
                
                query_data = query_combined[fingerprint_name]
                candidate_data = candidate_combined[fingerprint_name]
                
                if fingerprint_name == 'landmark':
                    sim = self._calculate_landmark_similarity(query_data, candidate_data)
                elif fingerprint_name in ['spectral_hash', 'mfcc_hash']:
                    sim = self._calculate_hash_similarity(query_data, candidate_data)
                elif fingerprint_name == 'chromaprint':
                    sim = self._calculate_chromaprint_similarity(query_data, candidate_data)
                else:
                    continue
                
                similarities.append(sim * weight)
                total_weight += weight
        
        if total_weight > 0:
            return sum(similarities) / total_weight
        else:
            return 0.0
    
    async def detect_copyright_violation(self,
                                       query_fingerprint: AudioFingerprint,
                                       copyright_threshold: float = 0.8) -> List[MatchResult]:
        """
        Detect potential copyright violations
        
        Args:
            query_fingerprint: Query audio fingerprint
            copyright_threshold: Minimum similarity for copyright violation
            
        Returns:
            List of potential copyright violations
        """
        try:
            # Find high-similarity matches
            matches = await self.find_matches(
                query_fingerprint,
                max_results=50,  # Check more candidates for copyright
                min_similarity=copyright_threshold
            )
            
            # Filter for potential violations
            violations = []
            for match in matches:
                if match.similarity_score >= copyright_threshold:
                    violations.append(match)
            
            logger.info(f"Detected {len(violations)} potential copyright violations")
            return violations
            
        except Exception as e:
            logger.error(f"Copyright violation detection failed: {e}")
            return []
    
    async def batch_content_matching(self,
                                   query_fingerprints: List[AudioFingerprint],
                                   max_results_per_query: int = 5) -> Dict[str, List[MatchResult]]:
        """Perform batch content matching for multiple queries"""
        try:
            results = {}
            
            for query_fp in query_fingerprints:
                matches = await self.find_matches(
                    query_fp,
                    max_results=max_results_per_query
                )
                results[query_fp.audio_id] = matches
            
            logger.info(f"Completed batch matching for {len(query_fingerprints)} queries")
            return results
            
        except Exception as e:
            logger.error(f"Batch content matching failed: {e}")
            return {}
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get fingerprint database statistics"""
        try:
            stats = {}
            
            with sqlite3.connect(str(self.fingerprinter.database_path)) as conn:
                cursor = conn.cursor()
                
                # Total fingerprints
                cursor.execute('SELECT COUNT(*) FROM fingerprints')
                stats['total_fingerprints'] = cursor.fetchone()[0]
                
                # Fingerprints by type
                cursor.execute('''
                    SELECT fingerprint_type, COUNT(*) 
                    FROM fingerprints 
                    GROUP BY fingerprint_type
                ''')
                
                type_counts = dict(cursor.fetchall())
                stats['fingerprints_by_type'] = type_counts
                
                # Unique audio IDs
                cursor.execute('SELECT COUNT(DISTINCT audio_id) FROM fingerprints')
                stats['unique_audio_tracks'] = cursor.fetchone()[0]
                
                # Database size
                cursor.execute('PRAGMA page_count')
                page_count = cursor.fetchone()[0]
                cursor.execute('PRAGMA page_size')
                page_size = cursor.fetchone()[0]
                stats['database_size_mb'] = (page_count * page_size) / (1024 * 1024)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get database statistics: {e}")
            return {"error": str(e)}
