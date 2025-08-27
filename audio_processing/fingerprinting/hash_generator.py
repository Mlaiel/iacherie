"""
Advanced hash generation algorithms for audio content protection.
Industrial-grade implementation with multiple hashing strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Audio Protection Suite
License: Proprietary - All rights reserved

WARNING: This code is proprietary and protected by copyright.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Contact: Fahed Mlaiel (mlaiel@live.de) for licensing agreements.
"""

import hashlib
import numpy as np
import librosa
from typing import Dict, List, Optional, Tuple, Union, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from dataclasses import dataclass
from scipy import signal, fft
from scipy.spatial.distance import hamming
import pickle
import zlib

logger = logging.getLogger(__name__)


@dataclass
class HashConfiguration:
    """Configuration for hash generation algorithms."""
    
    hash_size: int = 64
    sample_rate: int = 22050
    window_size: int = 2048
    hop_length: int = 512
    n_mels: int = 128
    use_compression: bool = True
    enable_normalization: bool = True


class PerceptualHashGenerator:
    """
    Advanced perceptual hash generator for audio content.
    Implements multiple algorithms for robust content identification.
    """
    
    def __init__(self, config: Optional[HashConfiguration] = None):
        """Initialize the perceptual hash generator."""
        self.config = config or HashConfiguration()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info("PerceptualHashGenerator initialized with config: %s", 
                   self.config.__dict__)
    
    async def generate_spectral_hash(
        self, 
        audio_data: Union[str, np.ndarray], 
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Generate perceptual hash based on spectral characteristics.
        
        Args:
            audio_data: Audio file path or numpy array
            metadata: Additional metadata for hash generation
            
        Returns:
            Hexadecimal string representation of the spectral hash
        """
        try:
            # Load and preprocess audio
            y, sr = self._load_audio(audio_data)
            
            # Generate spectrogram
            stft = librosa.stft(
                y, 
                n_fft=self.config.window_size, 
                hop_length=self.config.hop_length
            )
            magnitude = np.abs(stft)
            
            # Apply mel-scale transformation
            mel_spec = librosa.feature.melspectrogram(
                S=magnitude**2, 
                sr=sr, 
                n_mels=self.config.n_mels
            )
            
            # Convert to dB scale
            log_mel = librosa.power_to_db(mel_spec)
            
            # Resize to fixed dimensions for consistent hashing
            resized = self._resize_spectrogram(log_mel, (32, 32))
            
            # Generate binary hash
            hash_bits = await self._generate_binary_hash(resized)
            
            # Convert to hexadecimal string
            hash_hex = self._bits_to_hex(hash_bits)
            
            logger.debug("Generated spectral hash: %s", hash_hex[:16])
            return hash_hex
            
        except Exception as e:
            logger.error("Error generating spectral hash: %s", str(e))
            raise
    
    async def generate_chromagram_hash(
        self, 
        audio_data: Union[str, np.ndarray]
    ) -> str:
        """
        Generate hash based on chromagram features.
        Robust to tempo and key variations.
        """
        try:
            y, sr = self._load_audio(audio_data)
            
            # Extract chroma features
            chroma = librosa.feature.chroma_stft(
                y=y, 
                sr=sr, 
                hop_length=self.config.hop_length
            )
            
            # Temporal averaging to reduce sensitivity to timing
            chroma_avg = np.mean(chroma, axis=1)
            
            # Normalize to [0, 1] range
            if self.config.enable_normalization:
                chroma_avg = (chroma_avg - np.min(chroma_avg)) / (
                    np.max(chroma_avg) - np.min(chroma_avg) + 1e-8
                )
            
            # Generate binary representation
            threshold = np.mean(chroma_avg)
            binary_chroma = chroma_avg > threshold
            
            # Pad to desired hash size
            hash_bits = self._pad_to_size(binary_chroma, self.config.hash_size)
            
            return self._bits_to_hex(hash_bits)
            
        except Exception as e:
            logger.error("Error generating chromagram hash: %s", str(e))
            raise
    
    async def generate_rhythm_hash(
        self, 
        audio_data: Union[str, np.ndarray]
    ) -> str:
        """
        Generate hash based on rhythmic patterns.
        Captures tempo and beat structure.
        """
        try:
            y, sr = self._load_audio(audio_data)
            
            # Extract onset strength
            onset_strength = librosa.onset.onset_strength(
                y=y, sr=sr, hop_length=self.config.hop_length
            )
            
            # Estimate tempo and beat tracking
            tempo, beats = librosa.beat.beat_track(
                onset_envelope=onset_strength, 
                sr=sr, 
                hop_length=self.config.hop_length
            )
            
            # Create rhythm pattern from beat intervals
            if len(beats) > 1:
                beat_intervals = np.diff(beats)
                rhythm_pattern = self._quantize_intervals(beat_intervals)
            else:
                # Fallback for tracks without clear beats
                rhythm_pattern = np.zeros(self.config.hash_size, dtype=bool)
            
            # Ensure consistent size
            hash_bits = self._pad_to_size(rhythm_pattern, self.config.hash_size)
            
            return self._bits_to_hex(hash_bits)
            
        except Exception as e:
            logger.error("Error generating rhythm hash: %s", str(e))
            raise
    
    async def generate_mfcc_hash(
        self, 
        audio_data: Union[str, np.ndarray]
    ) -> str:
        """
        Generate hash based on Mel-Frequency Cepstral Coefficients.
        Captures timbral characteristics.
        """
        try:
            y, sr = self._load_audio(audio_data)
            
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(
                y=y, 
                sr=sr, 
                n_mfcc=13, 
                hop_length=self.config.hop_length
            )
            
            # Statistical aggregation across time
            mfcc_stats = np.column_stack([
                np.mean(mfccs, axis=1),
                np.std(mfccs, axis=1)
            ]).flatten()
            
            # Normalize features
            if self.config.enable_normalization:
                mfcc_stats = (mfcc_stats - np.mean(mfcc_stats)) / (
                    np.std(mfcc_stats) + 1e-8
                )
            
            # Quantize to binary
            threshold = np.median(mfcc_stats)
            binary_mfcc = mfcc_stats > threshold
            
            # Ensure consistent size
            hash_bits = self._pad_to_size(binary_mfcc, self.config.hash_size)
            
            return self._bits_to_hex(hash_bits)
            
        except Exception as e:
            logger.error("Error generating MFCC hash: %s", str(e))
            raise
    
    async def generate_composite_hash(
        self, 
        audio_data: Union[str, np.ndarray], 
        weights: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Generate composite hash combining multiple algorithms.
        Provides maximum robustness for content identification.
        """
        default_weights = {
            'spectral': 0.3,
            'chromagram': 0.25,
            'rhythm': 0.2,
            'mfcc': 0.25
        }
        weights = weights or default_weights
        
        try:
            # Generate individual hashes concurrently
            tasks = [
                self.generate_spectral_hash(audio_data),
                self.generate_chromagram_hash(audio_data),
                self.generate_rhythm_hash(audio_data),
                self.generate_mfcc_hash(audio_data)
            ]
            
            hash_results = await asyncio.gather(*tasks)
            
            # Convert hex strings to bit arrays
            bit_arrays = [self._hex_to_bits(h) for h in hash_results]
            
            # Weighted combination
            composite_bits = np.zeros(self.config.hash_size, dtype=float)
            hash_names = ['spectral', 'chromagram', 'rhythm', 'mfcc']
            
            for bits, name in zip(bit_arrays, hash_names):
                weight = weights.get(name, 0.0)
                composite_bits += weight * bits.astype(float)
            
            # Threshold to binary
            binary_composite = composite_bits > 0.5
            
            return self._bits_to_hex(binary_composite)
            
        except Exception as e:
            logger.error("Error generating composite hash: %s", str(e))
            raise
    
    def _load_audio(self, audio_data: Union[str, np.ndarray]) -> Tuple[np.ndarray, int]:
        """Load and preprocess audio data."""
        if isinstance(audio_data, str):
            y, sr = librosa.load(audio_data, sr=self.config.sample_rate)
        else:
            y, sr = audio_data, self.config.sample_rate
        
        # Apply normalization if enabled
        if self.config.enable_normalization:
            y = librosa.util.normalize(y)
        
        return y, sr
    
    def _resize_spectrogram(self, spectrogram: np.ndarray, target_shape: Tuple[int, int]) -> np.ndarray:
        """Resize spectrogram to target dimensions using interpolation."""
        return signal.resample(
            signal.resample(spectrogram, target_shape[1], axis=1), 
            target_shape[0], 
            axis=0
        )
    
    async def _generate_binary_hash(self, data: np.ndarray) -> np.ndarray:
        """Generate binary hash from 2D data matrix."""
        loop = asyncio.get_event_loop()
        
        def _hash_sync():
            # Calculate gradient-based features
            grad_x = np.gradient(data, axis=0)
            grad_y = np.gradient(data, axis=1)
            
            # Combine gradients
            combined = np.abs(grad_x) + np.abs(grad_y)
            
            # Flatten and threshold
            flattened = combined.flatten()
            threshold = np.median(flattened)
            
            binary_hash = flattened > threshold
            
            # Ensure consistent size
            return self._pad_to_size(binary_hash, self.config.hash_size)
        
        return await loop.run_in_executor(self.executor, _hash_sync)
    
    def _quantize_intervals(self, intervals: np.ndarray) -> np.ndarray:
        """Quantize beat intervals to create rhythm pattern."""
        if len(intervals) == 0:
            return np.zeros(16, dtype=bool)
        
        # Normalize intervals
        intervals = intervals / np.mean(intervals)
        
        # Quantize to common beat subdivisions
        quantized = np.round(intervals * 4) / 4
        
        # Convert to binary pattern
        pattern = []
        for interval in quantized:
            # Map to binary representation
            binary_interval = format(int(interval * 16) % 16, '04b')
            pattern.extend([c == '1' for c in binary_interval])
        
        return np.array(pattern[:self.config.hash_size], dtype=bool)
    
    def _pad_to_size(self, data: np.ndarray, target_size: int) -> np.ndarray:
        """Pad or truncate array to target size."""
        if len(data) >= target_size:
            return data[:target_size]
        else:
            padded = np.zeros(target_size, dtype=data.dtype)
            padded[:len(data)] = data
            return padded
    
    def _bits_to_hex(self, bits: np.ndarray) -> str:
        """Convert bit array to hexadecimal string."""
        # Ensure multiple of 8 bits for byte conversion
        padded_bits = self._pad_to_size(bits, ((len(bits) + 7) // 8) * 8)
        
        # Convert to bytes
        bytes_data = np.packbits(padded_bits)
        
        # Apply compression if enabled
        if self.config.use_compression:
            bytes_data = zlib.compress(bytes_data.tobytes())
        else:
            bytes_data = bytes_data.tobytes()
        
        return bytes_data.hex()
    
    def _hex_to_bits(self, hex_string: str) -> np.ndarray:
        """Convert hexadecimal string back to bit array."""
        try:
            # Convert hex to bytes
            bytes_data = bytes.fromhex(hex_string)
            
            # Decompress if needed
            if self.config.use_compression:
                bytes_data = zlib.decompress(bytes_data)
            
            # Convert to numpy array
            byte_array = np.frombuffer(bytes_data, dtype=np.uint8)
            
            # Unpack bits
            bits = np.unpackbits(byte_array)
            
            return bits[:self.config.hash_size]
            
        except Exception as e:
            logger.warning("Error converting hex to bits: %s", str(e))
            return np.zeros(self.config.hash_size, dtype=bool)
    
    def cleanup(self):
        """Cleanup resources."""
        self.executor.shutdown(wait=True)
        logger.info("PerceptualHashGenerator cleanup completed")


class HashComparator:
    """
    Advanced hash comparison algorithms with multiple similarity metrics.
    Provides robust matching capabilities for audio content protection.
    """
    
    def __init__(self):
        """Initialize the hash comparator."""
        self.executor = ThreadPoolExecutor(max_workers=2)
        logger.info("HashComparator initialized")
    
    async def calculate_similarity(
        self, 
        hash1: str, 
        hash2: str, 
        method: str = 'hamming'
    ) -> float:
        """
        Calculate similarity between two hashes.
        
        Args:
            hash1: First hash (hexadecimal string)
            hash2: Second hash (hexadecimal string)
            method: Similarity calculation method
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        methods = {
            'hamming': self._hamming_similarity,
            'jaccard': self._jaccard_similarity,
            'cosine': self._cosine_similarity,
            'normalized_hamming': self._normalized_hamming_similarity
        }
        
        if method not in methods:
            raise ValueError(f"Unknown similarity method: {method}")
        
        try:
            # Convert hex strings to bit arrays
            config = HashConfiguration()  # Use default config
            generator = PerceptualHashGenerator(config)
            
            bits1 = generator._hex_to_bits(hash1)
            bits2 = generator._hex_to_bits(hash2)
            
            # Ensure same length
            min_len = min(len(bits1), len(bits2))
            bits1 = bits1[:min_len]
            bits2 = bits2[:min_len]
            
            # Calculate similarity
            similarity = methods[method](bits1, bits2)
            
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error("Error calculating similarity: %s", str(e))
            return 0.0
    
    def _hamming_similarity(self, bits1: np.ndarray, bits2: np.ndarray) -> float:
        """Calculate Hamming similarity between bit arrays."""
        if len(bits1) == 0 or len(bits2) == 0:
            return 0.0
        
        hamming_dist = hamming(bits1, bits2)
        return 1.0 - hamming_dist
    
    def _jaccard_similarity(self, bits1: np.ndarray, bits2: np.ndarray) -> float:
        """Calculate Jaccard similarity between bit arrays."""
        intersection = np.logical_and(bits1, bits2).sum()
        union = np.logical_or(bits1, bits2).sum()
        
        if union == 0:
            return 1.0  # Both arrays are all zeros
        
        return intersection / union
    
    def _cosine_similarity(self, bits1: np.ndarray, bits2: np.ndarray) -> float:
        """Calculate cosine similarity between bit arrays."""
        dot_product = np.dot(bits1.astype(float), bits2.astype(float))
        norm1 = np.linalg.norm(bits1.astype(float))
        norm2 = np.linalg.norm(bits2.astype(float))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _normalized_hamming_similarity(self, bits1: np.ndarray, bits2: np.ndarray) -> float:
        """Calculate normalized Hamming similarity with bit position weighting."""
        if len(bits1) == 0 or len(bits2) == 0:
            return 0.0
        
        # Weight bits by position (earlier bits more important)
        weights = np.exp(-np.arange(len(bits1)) / len(bits1))
        weights = weights / np.sum(weights)
        
        # Calculate weighted hamming distance
        differences = (bits1 != bits2).astype(float)
        weighted_distance = np.sum(differences * weights)
        
        return 1.0 - weighted_distance
    
    async def batch_compare(
        self, 
        target_hash: str, 
        candidate_hashes: List[str], 
        method: str = 'hamming',
        threshold: float = 0.8
    ) -> List[Tuple[int, float]]:
        """
        Compare target hash against multiple candidates.
        
        Args:
            target_hash: Target hash to match against
            candidate_hashes: List of candidate hashes
            method: Similarity calculation method
            threshold: Minimum similarity threshold
            
        Returns:
            List of tuples (index, similarity_score) for matches above threshold
        """
        tasks = []
        for i, candidate_hash in enumerate(candidate_hashes):
            task = self.calculate_similarity(target_hash, candidate_hash, method)
            tasks.append((i, task))
        
        # Execute comparisons concurrently
        results = []
        for i, task in tasks:
            try:
                similarity = await task
                if similarity >= threshold:
                    results.append((i, similarity))
            except Exception as e:
                logger.warning("Error comparing hash at index %d: %s", i, str(e))
        
        # Sort by similarity score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def cleanup(self):
        """Cleanup resources."""
        self.executor.shutdown(wait=True)
        logger.info("HashComparator cleanup completed")
