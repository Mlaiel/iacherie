"""IA Influencer Agent - Audio Fingerprinting Engine
Advanced audio fingerprinting for content protection and identification

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved to Fahed Mlaiel
Warning: Unauthorized use, copying, or distribution of this code is strictly prohibited
"""
import asyncio
import hashlib
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import librosa
import chromaprint
from pydub import AudioSegment
from scipy.signal import spectrogram
from scipy.fftpack import fft
import json
import time

logger = logging.getLogger(__name__)


class AudioFingerprintEngine:
    """    Professional audio fingerprinting engine using multiple algorithms
    for robust content identification and protection
    """    
    def __init__(self, sample_rate: int = 22050, hop_length: int = 512):
        """        Initialize audio fingerprinting engine
        
        Args:
            sample_rate: Target sample rate for processing
            hop_length: Hop length for spectral analysis
        """        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.duration_threshold = 0.5  # Minimum duration in seconds
        self.similarity_threshold = 0.85
        
        # Chromaprint context
        self.chromaprint_ctx = chromaprint.Context()
        
        logger.info(f"AudioFingerprintEngine initialized with sample_rate={sample_rate}")
    
    async def extract_fingerprint(
        self, 
        audio_path: Union[str, Path],
        methods: List[str] = None
    ) -> Dict[str, any]:
        """        Extract comprehensive audio fingerprint using multiple methods
        
        Args:
            audio_path: Path to audio file
            methods: List of fingerprinting methods to use
                    ['chromaprint', 'spectral_hash', 'mfcc', 'tempo_rhythm']
        
        Returns:
            Dictionary containing all fingerprint data
        """        if methods is None:
            methods = ['chromaprint', 'spectral_hash', 'mfcc', 'tempo_rhythm']
        
        try:
            audio_path = Path(audio_path)
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Load audio with librosa
            y, sr = librosa.load(str(audio_path), sr=self.sample_rate)
            duration = librosa.duration(y=y, sr=sr)
            
            if duration < self.duration_threshold:
                raise ValueError(f"Audio too short: {duration}s < {self.duration_threshold}s")
            
            fingerprint_data = {
                'file_path': str(audio_path),
                'duration': duration,
                'sample_rate': sr,
                'channels': 1,  # librosa loads as mono by default
                'file_size': audio_path.stat().st_size,
                'created_at': time.time(),
                'methods': {}
            }
            
            # Execute fingerprinting methods
            if 'chromaprint' in methods:
                fingerprint_data['methods']['chromaprint'] = await self._extract_chromaprint(y, sr)
            
            if 'spectral_hash' in methods:
                fingerprint_data['methods']['spectral_hash'] = await self._extract_spectral_hash(y, sr)
            
            if 'mfcc' in methods:
                fingerprint_data['methods']['mfcc'] = await self._extract_mfcc_features(y, sr)
            
            if 'tempo_rhythm' in methods:
                fingerprint_data['methods']['tempo_rhythm'] = await self._extract_tempo_rhythm(y, sr)
            
            # Generate combined hash
            fingerprint_data['combined_hash'] = self._generate_combined_hash(fingerprint_data['methods'])
            
            logger.info(f"Successfully extracted fingerprint for {audio_path.name}")
            return fingerprint_data
            
        except Exception as e:
            logger.error(f"Error extracting fingerprint from {audio_path}: {str(e)}")
            raise
    
    async def _extract_chromaprint(self, y: np.ndarray, sr: int) -> Dict[str, any]:
        """Extract Chromaprint fingerprint"""        try:
            # Convert to int16 for chromaprint
            audio_int16 = (y * 32767).astype(np.int16)
            
            # Generate fingerprint
            self.chromaprint_ctx.start(sr, 1)  # channels = 1 (mono)
            self.chromaprint_ctx.feed(audio_int16)
            self.chromaprint_ctx.finish()
            
            raw_fingerprint = self.chromaprint_ctx.get_fingerprint()
            fingerprint_hash = hashlib.sha256(str(raw_fingerprint).encode()).hexdigest()
            
            return {
                'raw_fingerprint': raw_fingerprint,
                'hash': fingerprint_hash,
                'algorithm': 'chromaprint',
                'confidence': 0.95
            }
            
        except Exception as e:
            logger.error(f"Error in chromaprint extraction: {str(e)}")
            return {'error': str(e), 'algorithm': 'chromaprint'}
    
    async def _extract_spectral_hash(self, y: np.ndarray, sr: int) -> Dict[str, any]:
        """Extract spectral-based hash fingerprint"""        try:
            # Compute spectrogram
            D = librosa.stft(y, hop_length=self.hop_length)
            magnitude = np.abs(D)
            
            # Extract spectral features
            spectral_centroids = librosa.feature.spectral_centroid(S=magnitude, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(S=magnitude, sr=sr)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
            
            # Create hash from spectral features
            spectral_features = np.concatenate([
                spectral_centroids[:100] if len(spectral_centroids) > 100 else spectral_centroids,
                spectral_rolloff[:100] if len(spectral_rolloff) > 100 else spectral_rolloff,
                zero_crossing_rate[:100] if len(zero_crossing_rate) > 100 else zero_crossing_rate
            ])
            
            # Normalize and hash
            spectral_hash = hashlib.sha256(spectral_features.tobytes()).hexdigest()
            
            return {
                'spectral_hash': spectral_hash,
                'centroid_mean': float(np.mean(spectral_centroids)),
                'rolloff_mean': float(np.mean(spectral_rolloff)),
                'zcr_mean': float(np.mean(zero_crossing_rate)),
                'algorithm': 'spectral_hash',
                'confidence': 0.88
            }
            
        except Exception as e:
            logger.error(f"Error in spectral hash extraction: {str(e)}")
            return {'error': str(e), 'algorithm': 'spectral_hash'}
    
    async def _extract_mfcc_features(self, y: np.ndarray, sr: int) -> Dict[str, any]:
        """Extract MFCC-based fingerprint"""        try:
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=self.hop_length)
            
            # Statistical features from MFCCs
            mfcc_means = np.mean(mfccs, axis=1)
            mfcc_vars = np.var(mfccs, axis=1)
            mfcc_features = np.concatenate([mfcc_means, mfcc_vars])
            
            # Generate hash from MFCC features
            mfcc_hash = hashlib.sha256(mfcc_features.tobytes()).hexdigest()
            
            return {
                'mfcc_hash': mfcc_hash,
                'mfcc_means': mfcc_means.tolist(),
                'mfcc_vars': mfcc_vars.tolist(),
                'n_coefficients': len(mfcc_means),
                'algorithm': 'mfcc',
                'confidence': 0.82
            }
            
        except Exception as e:
            logger.error(f"Error in MFCC extraction: {str(e)}")
            return {'error': str(e), 'algorithm': 'mfcc'}
    
    async def _extract_tempo_rhythm(self, y: np.ndarray, sr: int) -> Dict[str, any]:
        """Extract tempo and rhythm features"""        try:
            # Tempo estimation
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            # Rhythm patterns
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)
            
            # Beat histogram
            beat_histogram = np.histogram(np.diff(onset_times), bins=20)[0]
            
            # Generate rhythm hash
            rhythm_features = np.concatenate([
                [tempo],
                beat_histogram.astype(float)
            ])
            rhythm_hash = hashlib.sha256(rhythm_features.tobytes()).hexdigest()
            
            return {
                'rhythm_hash': rhythm_hash,
                'tempo': float(tempo),
                'beat_count': len(beats),
                'onset_count': len(onset_frames),
                'beat_histogram': beat_histogram.tolist(),
                'algorithm': 'tempo_rhythm',
                'confidence': 0.75
            }
            
        except Exception as e:
            logger.error(f"Error in tempo/rhythm extraction: {str(e)}")
            return {'error': str(e), 'algorithm': 'tempo_rhythm'}
    
    def _generate_combined_hash(self, methods_data: Dict[str, any]) -> str:
        """Generate combined hash from all fingerprinting methods"""        try:
            hash_parts = []
            
            for method, data in methods_data.items():
                if 'error' not in data:
                    # Extract primary hash from each method
                    if method == 'chromaprint' and 'hash' in data:
                        hash_parts.append(data['hash'])
                    elif method == 'spectral_hash' and 'spectral_hash' in data:
                        hash_parts.append(data['spectral_hash'])
                    elif method == 'mfcc' and 'mfcc_hash' in data:
                        hash_parts.append(data['mfcc_hash'])
                    elif method == 'tempo_rhythm' and 'rhythm_hash' in data:
                        hash_parts.append(data['rhythm_hash'])
            
            # Combine all hashes
            combined_string = ''.join(sorted(hash_parts))
            combined_hash = hashlib.sha256(combined_string.encode()).hexdigest()
            
            return combined_hash
            
        except Exception as e:
            logger.error(f"Error generating combined hash: {str(e)}")
            return hashlib.sha256(str(time.time()).encode()).hexdigest()
    
    async def compare_fingerprints(
        self, 
        fingerprint1: Dict[str, any], 
        fingerprint2: Dict[str, any]
    ) -> Dict[str, float]:
        """        Compare two audio fingerprints and return similarity scores
        
        Args:
            fingerprint1: First fingerprint data
            fingerprint2: Second fingerprint data
        
        Returns:
            Dictionary with similarity scores for each method
        """        similarities = {}
        
        try:
            # Compare each method
            for method in ['chromaprint', 'spectral_hash', 'mfcc', 'tempo_rhythm']:
                if (method in fingerprint1.get('methods', {}) and 
                    method in fingerprint2.get('methods', {})):
                    
                    similarity = await self._compare_method(
                        fingerprint1['methods'][method],
                        fingerprint2['methods'][method],
                        method
                    )
                    similarities[method] = similarity
            
            # Overall similarity (weighted average)
            if similarities:
                weights = {'chromaprint': 0.4, 'spectral_hash': 0.3, 'mfcc': 0.2, 'tempo_rhythm': 0.1}
                overall_similarity = sum(
                    similarities.get(method, 0) * weight 
                    for method, weight in weights.items()
                ) / sum(weights[method] for method in similarities.keys())
                
                similarities['overall'] = overall_similarity
            else:
                similarities['overall'] = 0.0
            
            return similarities
            
        except Exception as e:
            logger.error(f"Error comparing fingerprints: {str(e)}")
            return {'overall': 0.0, 'error': str(e)}
    
    async def _compare_method(
        self, 
        data1: Dict[str, any], 
        data2: Dict[str, any], 
        method: str
    ) -> float:
        """Compare two fingerprints using specific method"""        try:
            if 'error' in data1 or 'error' in data2:
                return 0.0
            
            if method == 'chromaprint':
                return self._compare_chromaprint(data1, data2)
            elif method == 'spectral_hash':
                return self._compare_spectral(data1, data2)
            elif method == 'mfcc':
                return self._compare_mfcc(data1, data2)
            elif method == 'tempo_rhythm':
                return self._compare_rhythm(data1, data2)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error comparing {method}: {str(e)}")
            return 0.0
    
    def _compare_chromaprint(self, data1: Dict, data2: Dict) -> float:
        """Compare chromaprint fingerprints"""        try:
            hash1 = data1.get('hash', '')
            hash2 = data2.get('hash', '')
            
            if hash1 == hash2:
                return 1.0
            
            # Calculate Hamming distance for similar hashes
            if len(hash1) == len(hash2):
                hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
                similarity = 1.0 - (hamming_distance / len(hash1))
                return max(0.0, similarity)
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _compare_spectral(self, data1: Dict, data2: Dict) -> float:
        """Compare spectral hash fingerprints"""        try:
            # Compare statistical features
            centroid_diff = abs(data1.get('centroid_mean', 0) - data2.get('centroid_mean', 0))
            rolloff_diff = abs(data1.get('rolloff_mean', 0) - data2.get('rolloff_mean', 0))
            zcr_diff = abs(data1.get('zcr_mean', 0) - data2.get('zcr_mean', 0))
            
            # Normalize differences and calculate similarity
            centroid_sim = 1.0 - min(1.0, centroid_diff / 1000.0)
            rolloff_sim = 1.0 - min(1.0, rolloff_diff / 5000.0)
            zcr_sim = 1.0 - min(1.0, zcr_diff / 0.1)
            
            # Weighted average
            similarity = (centroid_sim * 0.4 + rolloff_sim * 0.4 + zcr_sim * 0.2)
            return max(0.0, similarity)
            
        except Exception:
            return 0.0
    
    def _compare_mfcc(self, data1: Dict, data2: Dict) -> float:
        """Compare MFCC fingerprints"""        try:
            means1 = np.array(data1.get('mfcc_means', []))
            means2 = np.array(data2.get('mfcc_means', []))
            
            if len(means1) == len(means2) and len(means1) > 0:
                # Cosine similarity
                dot_product = np.dot(means1, means2)
                norm1 = np.linalg.norm(means1)
                norm2 = np.linalg.norm(means2)
                
                if norm1 > 0 and norm2 > 0:
                    similarity = dot_product / (norm1 * norm2)
                    return max(0.0, similarity)
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _compare_rhythm(self, data1: Dict, data2: Dict) -> float:
        """Compare rhythm/tempo fingerprints"""        try:
            tempo1 = data1.get('tempo', 0)
            tempo2 = data2.get('tempo', 0)
            
            if tempo1 > 0 and tempo2 > 0:
                tempo_diff = abs(tempo1 - tempo2)
                tempo_similarity = 1.0 - min(1.0, tempo_diff / 50.0)  # Within 50 BPM
                
                # Compare beat histograms if available
                hist1 = np.array(data1.get('beat_histogram', []))
                hist2 = np.array(data2.get('beat_histogram', []))
                
                if len(hist1) == len(hist2) and len(hist1) > 0:
                    # Chi-square distance for histograms
                    chi_square = np.sum((hist1 - hist2) ** 2 / (hist1 + hist2 + 1e-10))
                    hist_similarity = 1.0 / (1.0 + chi_square)
                    
                    # Combine tempo and histogram similarity
                    similarity = (tempo_similarity * 0.6 + hist_similarity * 0.4)
                    return max(0.0, similarity)
                
                return tempo_similarity
            
            return 0.0
            
        except Exception:
            return 0.0
    
    async def batch_fingerprint(
        self, 
        audio_paths: List[Union[str, Path]], 
        methods: List[str] = None
    ) -> List[Dict[str, any]]:
        """        Process multiple audio files in batch
        
        Args:
            audio_paths: List of audio file paths
            methods: Fingerprinting methods to use
        
        Returns:
            List of fingerprint data for each file
        """        tasks = []
        for audio_path in audio_paths:
            task = self.extract_fingerprint(audio_path, methods)
            tasks.append(task)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log errors
            fingerprints = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error processing {audio_paths[i]}: {str(result)}")
                    fingerprints.append({'error': str(result), 'file_path': str(audio_paths[i])})
                else:
                    fingerprints.append(result)
            
            return fingerprints
            
        except Exception as e:
            logger.error(f"Error in batch fingerprinting: {str(e)}")
            raise
    
    def get_engine_info(self) -> Dict[str, any]:
        """Get engine configuration and capabilities"""        return {
            'engine': 'AudioFingerprintEngine',
            'version': '1.0.0',
            'sample_rate': self.sample_rate,
            'hop_length': self.hop_length,
            'duration_threshold': self.duration_threshold,
            'similarity_threshold': self.similarity_threshold,
            'supported_methods': ['chromaprint', 'spectral_hash', 'mfcc', 'tempo_rhythm'],
            'supported_formats': ['.mp3', '.wav', '.flac', '.m4a', '.ogg'],
            'capabilities': {
                'real_time_processing': True,
                'batch_processing': True,
                'similarity_matching': True,
                'multi_algorithm': True
            }
        }
