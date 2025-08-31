"""Core fingerprinting engine for audio content protection and identification.
Advanced industrial implementation for multi-format audio fingerprinting.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Audio Protection Suite
License: Proprietary - All rights reserved

WARNING: This code is proprietary and protected by copyright.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Contact: Fahed Mlaiel (mlaiel@live.de) for licensing agreements.
"""import hashlib
import numpy as np
import librosa
import chromaprint
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from scipy import signal
from scipy.spatial.distance import cosine
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FingerprintResult:
    """Result container for audio fingerprinting operations."""    
    fingerprint_hash: str
    chromaprint: Optional[str]
    spectral_features: Optional[np.ndarray]
    metadata: Dict
    confidence_score: float
    processing_time: float
    file_hash: str


@dataclass
class MatchResult:
    """Result container for fingerprint matching operations."""    
    similarity_score: float
    match_confidence: float
    matched_fingerprint_id: str
    offset_seconds: float
    duration_match: float
    metadata_match: Dict


class AudioFingerprintCore:
    """    Core audio fingerprinting engine with advanced algorithms.
    Supports multiple fingerprinting techniques for robust content identification.
    """    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the core fingerprinting engine."""        self.config = config or self._default_config()
        self.executor = ThreadPoolExecutor(max_workers=self.config['max_workers'])
        
        # Initialize fingerprinting parameters
        self.sr = self.config['sample_rate']
        self.hop_length = self.config['hop_length']
        self.n_fft = self.config['n_fft']
        self.n_mels = self.config['n_mels']
        
        logger.info("AudioFingerprintCore initialized with config: %s", self.config)
    
    def _default_config(self) -> Dict:
        """Default configuration for fingerprinting engine."""        return {
            'sample_rate': 22050,
            'hop_length': 512,
            'n_fft': 2048,
            'n_mels': 128,
            'max_workers': 4,
            'chromaprint_algorithm': chromaprint.ALGORITHM_DEFAULT,
            'spectral_window_size': 4096,
            'similarity_threshold': 0.85,
            'min_match_duration': 5.0
        }
    
    async def generate_fingerprint(
        self, 
        audio_data: Union[str, np.ndarray], 
        metadata: Optional[Dict] = None
    ) -> FingerprintResult:
        """        Generate comprehensive fingerprint for audio content.
        
        Args:
            audio_data: Path to audio file or numpy array of audio samples
            metadata: Additional metadata to include in fingerprint
            
        Returns:
            FingerprintResult containing all fingerprint components
        """        start_time = asyncio.get_event_loop().time()
        
        try:
            # Load and preprocess audio
            if isinstance(audio_data, str):
                y, sr = librosa.load(audio_data, sr=self.sr)
                file_hash = self._calculate_file_hash(audio_data)
            else:
                y, sr = audio_data, self.sr
                file_hash = hashlib.sha256(y.tobytes()).hexdigest()
            
            # Generate multiple fingerprint components
            chromaprint_fp = await self._generate_chromaprint(y, sr)
            spectral_features = await self._extract_spectral_features(y, sr)
            perceptual_hash = await self._generate_perceptual_hash(y, sr)
            
            # Combine fingerprints into unified hash
            combined_data = f"{chromaprint_fp}:{perceptual_hash}:{file_hash}"
            fingerprint_hash = hashlib.sha256(combined_data.encode()).hexdigest()
            
            # Calculate confidence based on audio quality
            confidence_score = self._calculate_confidence(y, sr)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            result = FingerprintResult(
                fingerprint_hash=fingerprint_hash,
                chromaprint=chromaprint_fp,
                spectral_features=spectral_features,
                metadata=metadata or {},
                confidence_score=confidence_score,
                processing_time=processing_time,
                file_hash=file_hash
            )
            
            logger.info("Generated fingerprint %s in %.3fs", fingerprint_hash[:16], processing_time)
            return result
            
        except Exception as e:
            logger.error("Error generating fingerprint: %s", str(e))
            raise
    
    async def _generate_chromaprint(self, y: np.ndarray, sr: int) -> str:
        """Generate Chromaprint fingerprint using AcoustID algorithm."""        loop = asyncio.get_event_loop()
        
        def _chromaprint_sync():
            # Convert to proper format for chromaprint
            audio_int16 = (y * 32767).astype(np.int16)
            return chromaprint.encode(
                self.config['chromaprint_algorithm'],
                audio_int16,
                sr,
                channels=1
            )
        
        return await loop.run_in_executor(self.executor, _chromaprint_sync)
    
    async def _extract_spectral_features(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Extract advanced spectral features for robust matching."""        loop = asyncio.get_event_loop()
        
        def _extract_sync():
            # Mel-frequency cepstral coefficients
            mfccs = librosa.feature.mfcc(
                y=y, sr=sr, n_mfcc=13, hop_length=self.hop_length
            )
            
            # Spectral centroid and bandwidth
            spectral_centroids = librosa.feature.spectral_centroid(
                y=y, sr=sr, hop_length=self.hop_length
            )
            spectral_bandwidth = librosa.feature.spectral_bandwidth(
                y=y, sr=sr, hop_length=self.hop_length
            )
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(
                y, frame_length=self.n_fft, hop_length=self.hop_length
            )
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(
                y=y, sr=sr, hop_length=self.hop_length
            )
            
            # Concatenate all features
            features = np.vstack([
                mfccs,
                spectral_centroids,
                spectral_bandwidth,
                zcr,
                chroma
            ])
            
            # Reduce dimensionality by taking statistics
            feature_stats = np.column_stack([
                np.mean(features, axis=1),
                np.std(features, axis=1),
                np.max(features, axis=1),
                np.min(features, axis=1)
            ]).flatten()
            
            return feature_stats
        
        return await loop.run_in_executor(self.executor, _extract_sync)
    
    async def _generate_perceptual_hash(self, y: np.ndarray, sr: int) -> str:
        """Generate perceptual hash based on audio characteristics."""        loop = asyncio.get_event_loop()
        
        def _hash_sync():
            # Generate spectrogram
            stft = librosa.stft(y, hop_length=self.hop_length, n_fft=self.n_fft)
            magnitude = np.abs(stft)
            
            # Reduce to fixed size for consistent hashing
            resized = signal.resample(magnitude, (64, 64))
            
            # Create binary hash based on median
            median_val = np.median(resized)
            binary_hash = resized > median_val
            
            # Convert to hex string
            hash_bytes = np.packbits(binary_hash.flatten())
            return hash_bytes.tobytes().hex()
        
        return await loop.run_in_executor(self.executor, _hash_sync)
    
    def _calculate_file_hash(self, filepath: str) -> str:
        """Calculate SHA-256 hash of the audio file."""        hasher = hashlib.sha256()
        
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def _calculate_confidence(self, y: np.ndarray, sr: int) -> float:
        """Calculate confidence score based on audio quality metrics."""        # Signal-to-noise ratio estimation
        energy = np.sum(y ** 2) / len(y)
        
        # Dynamic range
        dynamic_range = np.max(y) - np.min(y)
        
        # Spectral complexity
        stft = librosa.stft(y)
        spectral_complexity = np.mean(np.std(np.abs(stft), axis=1))
        
        # Combine metrics for confidence score
        confidence = min(1.0, (energy * 10 + dynamic_range * 2 + spectral_complexity) / 3)
        return max(0.1, confidence)  # Minimum confidence of 0.1
    
    async def match_fingerprints(
        self, 
        query_fingerprint: FingerprintResult,
        candidate_fingerprints: List[FingerprintResult],
        threshold: Optional[float] = None
    ) -> List[MatchResult]:
        """        Match query fingerprint against candidates.
        
        Args:
            query_fingerprint: The fingerprint to match
            candidate_fingerprints: List of candidate fingerprints
            threshold: Similarity threshold (uses config default if None)
            
        Returns:
            List of MatchResult objects sorted by similarity score
        """        threshold = threshold or self.config['similarity_threshold']
        matches = []
        
        for candidate in candidate_fingerprints:
            try:
                similarity = await self._calculate_similarity(
                    query_fingerprint, candidate
                )
                
                if similarity >= threshold:
                    match = MatchResult(
                        similarity_score=similarity,
                        match_confidence=min(
                            query_fingerprint.confidence_score,
                            candidate.confidence_score
                        ),
                        matched_fingerprint_id=candidate.fingerprint_hash,
                        offset_seconds=0.0,  # Could be enhanced with timing analysis
                        duration_match=0.0,  # Could be enhanced with duration analysis
                        metadata_match=candidate.metadata
                    )
                    matches.append(match)
                    
            except Exception as e:
                logger.warning("Error matching against candidate %s: %s", 
                             candidate.fingerprint_hash[:16], str(e))
        
        # Sort by similarity score (descending)
        matches.sort(key=lambda x: x.similarity_score, reverse=True)
        return matches
    
    async def _calculate_similarity(
        self, 
        fp1: FingerprintResult, 
        fp2: FingerprintResult
    ) -> float:
        """Calculate similarity between two fingerprints."""        loop = asyncio.get_event_loop()
        
        def _similarity_sync():
            # Chromaprint similarity
            chromaprint_sim = 0.0
            if fp1.chromaprint and fp2.chromaprint:
                chromaprint_sim = self._chromaprint_similarity(
                    fp1.chromaprint, fp2.chromaprint
                )
            
            # Spectral features similarity
            spectral_sim = 0.0
            if fp1.spectral_features is not None and fp2.spectral_features is not None:
                spectral_sim = 1 - cosine(fp1.spectral_features, fp2.spectral_features)
                spectral_sim = max(0, spectral_sim)  # Ensure non-negative
            
            # File hash exact match
            file_match = 1.0 if fp1.file_hash == fp2.file_hash else 0.0
            
            # Weighted combination
            weights = [0.4, 0.4, 0.2]  # chromaprint, spectral, file_hash
            similarities = [chromaprint_sim, spectral_sim, file_match]
            
            weighted_similarity = sum(w * s for w, s in zip(weights, similarities))
            return min(1.0, max(0.0, weighted_similarity))
        
        return await loop.run_in_executor(self.executor, _similarity_sync)
    
    def _chromaprint_similarity(self, fp1: str, fp2: str) -> float:
        """Calculate similarity between two chromaprint fingerprints."""        try:
            # Decode fingerprints
            raw_fp1 = chromaprint.decode(fp1)
            raw_fp2 = chromaprint.decode(fp2)
            
            if not raw_fp1 or not raw_fp2:
                return 0.0
            
            # Calculate bit similarity
            min_len = min(len(raw_fp1), len(raw_fp2))
            if min_len == 0:
                return 0.0
            
            matches = sum(1 for i in range(min_len) if raw_fp1[i] == raw_fp2[i])
            return matches / min_len
            
        except Exception as e:
            logger.warning("Error calculating chromaprint similarity: %s", str(e))
            return 0.0
    
    async def batch_fingerprint(
        self, 
        audio_files: List[str], 
        metadata_list: Optional[List[Dict]] = None
    ) -> List[FingerprintResult]:
        """        Generate fingerprints for multiple audio files in parallel.
        
        Args:
            audio_files: List of paths to audio files
            metadata_list: Optional list of metadata for each file
            
        Returns:
            List of FingerprintResult objects
        """        metadata_list = metadata_list or [{}] * len(audio_files)
        
        tasks = []
        for audio_file, metadata in zip(audio_files, metadata_list):
            task = self.generate_fingerprint(audio_file, metadata)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log errors
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error("Error processing %s: %s", audio_files[i], str(result))
            else:
                valid_results.append(result)
        
        return valid_results
    
    def cleanup(self):
        """Cleanup resources."""        self.executor.shutdown(wait=True)
        logger.info("AudioFingerprintCore cleanup completed")
