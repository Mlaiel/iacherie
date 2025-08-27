"""
IA Influencer Agent - Audio Fingerprinting Processor
Author: Fahed Mlaiel <mlaiel@live.de>

AVERTISSEMENT LÉGAL STRICT:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée 
sans permission écrite expresse est strictement interdite et 
constituera une violation des droits d'auteur.

Advanced audio fingerprinting processor for multi-format content protection
"""

import hashlib
import librosa
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class AudioFingerprint:
    """Audio fingerprint data structure"""
    content_hash: str
    spectral_features: np.ndarray
    mfcc_features: np.ndarray
    chromagram: np.ndarray
    tempo: float
    duration: float
    sample_rate: int
    file_format: str
    metadata: Dict[str, Any]

class AudioFingerprintProcessor:
    """
    Professional audio fingerprinting processor with advanced ML algorithms
    Handles multi-format audio content protection and similarity detection
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize audio fingerprinting processor"""
        self.config = config or self._get_default_config()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for audio processing"""
        return {
            'sample_rate': 22050,
            'n_mfcc': 13,
            'n_chroma': 12,
            'n_fft': 2048,
            'hop_length': 512,
            'window_size': 1024,
            'similarity_threshold': 0.85
        }
    
    async def process_audio_file(self, file_path: Path) -> AudioFingerprint:
        """
        Process audio file and generate comprehensive fingerprint
        
        Args:
            file_path: Path to audio file
            
        Returns:
            AudioFingerprint object with extracted features
        """
        try:
            # Load audio file asynchronously
            loop = asyncio.get_event_loop()
            audio_data, sr = await loop.run_in_executor(
                self.executor, 
                librosa.load, 
                str(file_path), 
                self.config['sample_rate']
            )
            
            # Generate content hash
            content_hash = self._generate_content_hash(audio_data)
            
            # Extract features in parallel
            features = await asyncio.gather(
                self._extract_spectral_features(audio_data, sr),
                self._extract_mfcc_features(audio_data, sr),
                self._extract_chromagram(audio_data, sr),
                self._extract_tempo(audio_data, sr)
            )
            
            spectral_features, mfcc_features, chromagram, tempo = features
            
            # Create fingerprint
            fingerprint = AudioFingerprint(
                content_hash=content_hash,
                spectral_features=spectral_features,
                mfcc_features=mfcc_features,
                chromagram=chromagram,
                tempo=tempo,
                duration=len(audio_data) / sr,
                sample_rate=sr,
                file_format=file_path.suffix.lower(),
                metadata=self._extract_metadata(file_path)
            )
            
            logger.info(f"Audio fingerprint generated for {file_path.name}")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Error processing audio file {file_path}: {str(e)}")
            raise
    
    def _generate_content_hash(self, audio_data: np.ndarray) -> str:
        """Generate unique hash for audio content"""
        audio_bytes = audio_data.tobytes()
        return hashlib.sha256(audio_bytes).hexdigest()
    
    async def _extract_spectral_features(self, audio_data: np.ndarray, sr: int) -> np.ndarray:
        """Extract spectral features from audio"""
        loop = asyncio.get_event_loop()
        
        def compute_features():
            # Spectral centroid
            spectral_centroid = librosa.feature.spectral_centroid(
                y=audio_data, sr=sr, hop_length=self.config['hop_length']
            )
            
            # Spectral bandwidth
            spectral_bandwidth = librosa.feature.spectral_bandwidth(
                y=audio_data, sr=sr, hop_length=self.config['hop_length']
            )
            
            # Spectral rolloff
            spectral_rolloff = librosa.feature.spectral_rolloff(
                y=audio_data, sr=sr, hop_length=self.config['hop_length']
            )
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(
                audio_data, hop_length=self.config['hop_length']
            )
            
            return np.vstack([
                spectral_centroid.mean(axis=1),
                spectral_bandwidth.mean(axis=1),
                spectral_rolloff.mean(axis=1),
                zcr.mean(axis=1)
            ]).flatten()
        
        return await loop.run_in_executor(self.executor, compute_features)
    
    async def _extract_mfcc_features(self, audio_data: np.ndarray, sr: int) -> np.ndarray:
        """Extract MFCC features from audio"""
        loop = asyncio.get_event_loop()
        
        def compute_mfcc():
            mfcc = librosa.feature.mfcc(
                y=audio_data,
                sr=sr,
                n_mfcc=self.config['n_mfcc'],
                hop_length=self.config['hop_length']
            )
            return mfcc.mean(axis=1)
        
        return await loop.run_in_executor(self.executor, compute_mfcc)
    
    async def _extract_chromagram(self, audio_data: np.ndarray, sr: int) -> np.ndarray:
        """Extract chromagram features from audio"""
        loop = asyncio.get_event_loop()
        
        def compute_chroma():
            chroma = librosa.feature.chroma_stft(
                y=audio_data,
                sr=sr,
                n_chroma=self.config['n_chroma'],
                hop_length=self.config['hop_length']
            )
            return chroma.mean(axis=1)
        
        return await loop.run_in_executor(self.executor, compute_chroma)
    
    async def _extract_tempo(self, audio_data: np.ndarray, sr: int) -> float:
        """Extract tempo from audio"""
        loop = asyncio.get_event_loop()
        
        def compute_tempo():
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sr)
            return float(tempo)
        
        return await loop.run_in_executor(self.executor, compute_tempo)
    
    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract file metadata"""
        return {
            'filename': file_path.name,
            'file_size': file_path.stat().st_size,
            'created_at': file_path.stat().st_ctime,
            'modified_at': file_path.stat().st_mtime
        }
    
    def calculate_similarity(self, fp1: AudioFingerprint, fp2: AudioFingerprint) -> float:
        """
        Calculate similarity score between two audio fingerprints
        
        Args:
            fp1: First audio fingerprint
            fp2: Second audio fingerprint
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Content hash exact match
            if fp1.content_hash == fp2.content_hash:
                return 1.0
            
            # Feature similarity calculations
            mfcc_similarity = self._cosine_similarity(fp1.mfcc_features, fp2.mfcc_features)
            chroma_similarity = self._cosine_similarity(fp1.chromagram, fp2.chromagram)
            spectral_similarity = self._cosine_similarity(fp1.spectral_features, fp2.spectral_features)
            
            # Tempo similarity
            tempo_diff = abs(fp1.tempo - fp2.tempo) / max(fp1.tempo, fp2.tempo)
            tempo_similarity = 1.0 - min(tempo_diff, 1.0)
            
            # Duration similarity
            duration_diff = abs(fp1.duration - fp2.duration) / max(fp1.duration, fp2.duration)
            duration_similarity = 1.0 - min(duration_diff, 1.0)
            
            # Weighted average
            weights = {
                'mfcc': 0.4,
                'chroma': 0.3,
                'spectral': 0.2,
                'tempo': 0.05,
                'duration': 0.05
            }
            
            similarity = (
                weights['mfcc'] * mfcc_similarity +
                weights['chroma'] * chroma_similarity +
                weights['spectral'] * spectral_similarity +
                weights['tempo'] * tempo_similarity +
                weights['duration'] * duration_similarity
            )
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            # Normalize vectors
            vec1_norm = vec1 / np.linalg.norm(vec1)
            vec2_norm = vec2 / np.linalg.norm(vec2)
            
            # Calculate cosine similarity
            similarity = np.dot(vec1_norm, vec2_norm)
            return float(np.clip(similarity, 0.0, 1.0))
            
        except Exception:
            return 0.0
    
    def is_duplicate(self, fp1: AudioFingerprint, fp2: AudioFingerprint) -> bool:
        """Check if two fingerprints represent duplicate content"""
        similarity = self.calculate_similarity(fp1, fp2)
        return similarity >= self.config['similarity_threshold']
    
    async def batch_process(self, file_paths: List[Path]) -> List[AudioFingerprint]:
        """Process multiple audio files in parallel"""
        tasks = [self.process_audio_file(path) for path in file_paths]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
