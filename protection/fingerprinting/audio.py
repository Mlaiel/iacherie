"""
 Audio Content Fingerprinting Service
=======================================

Enterprise-grade audio fingerprinting with multiple algorithms:
- Chromaprint (acoustic fingerprinting)
- Essentia audio analysis
- Spectral hashing
- Neural audio embeddings

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written 
permission from Fahed Mlaiel is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization requests.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json

try:
    import librosa
    import acoustid
    import chromaprint
    import essentia
    import essentia.standard as es
    from scipy.signal import spectrogram
    from sklearn.preprocessing import StandardScaler
    import torch
    import torch.nn as nn
    from transformers import Wav2Vec2Model, Wav2Vec2Processor
except ImportError as e:
    logging.warning(f"Some audio dependencies not available: {e}")

from ..models import FingerprintResult, SimilarityMatch

logger = logging.getLogger(__name__)

@dataclass
class AudioMetadata:
    """Comprehensive audio metadata extraction."""
    duration: float
    sample_rate: int
    channels: int
    bitrate: Optional[int]
    format: str
    codec: Optional[str]
    tempo: Optional[float]
    key: Optional[str]
    loudness: Optional[float]
    spectral_centroid: Optional[float]
    zero_crossing_rate: Optional[float]
    mfcc_features: Optional[np.ndarray]
    chroma_features: Optional[np.ndarray]

class ChromaprintExtractor:
    """Advanced Chromaprint fingerprinting with extended features."""
    
    def __init__(self, algorithm: int = chromaprint.ALGORITHM_DEFAULT):
        self.algorithm = algorithm
        self.duration_threshold = 30.0  # Minimum 30 seconds for reliable fingerprint
        
    def extract_fingerprint(self, audio_path: str) -> Dict[str, Any]:
        """
        Extract Chromaprint fingerprint with enhanced features.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary containing fingerprint data and metadata
        """



        try:
            # Load audio with librosa
            y, sr = librosa.load(audio_path, sr=None, mono=True)
            
            # Convert to int16 for chromaprint
            audio_data = (y * 32767).astype(np.int16)
            
            # Generate fingerprint
            raw_fingerprint = chromaprint.hash_fingerprint(
                chromaprint.encode_fingerprint(
                    chromaprint.fingerprint(audio_data, sr, algorithm=self.algorithm)[1]
                )
            )
            
            # Enhanced fingerprint with multiple segments
            segment_fingerprints = self._extract_segment_fingerprints(audio_data, sr)
            
            return {
                "raw_fingerprint": raw_fingerprint,
                "segment_fingerprints": segment_fingerprints,
                "duration": len(y) / sr,
                "sample_rate": sr,
                "algorithm": self.algorithm,
                "confidence": self._calculate_confidence(audio_data, sr),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Chromaprint extraction failed for {audio_path}: {e}")
            return {"error": str(e)}
    
    def _extract_segment_fingerprints(self, audio_data: np.ndarray, sr: int) -> List[str]:
        """Extract fingerprints from multiple audio segments."""
        segment_duration = 10  # 10 seconds per segment
        segment_samples = segment_duration * sr
        fingerprints = []
        
        for i in range(0, len(audio_data), segment_samples):
            segment = audio_data[i:i + segment_samples]
            if len(segment) >= sr:  # At least 1 second
                try:
                    fp = chromaprint.hash_fingerprint(
                        chromaprint.encode_fingerprint(
                            chromaprint.fingerprint(segment, sr, algorithm=self.algorithm)[1]
                        )
                    )
                    fingerprints.append(fp)
                except Exception:
                    continue
                    
        return fingerprints
    
    def _calculate_confidence(self, audio_data: np.ndarray, sr: int) -> float:
        """Calculate fingerprint confidence based on audio quality."""
        # Signal-to-noise ratio estimation
        signal_power = np.mean(audio_data.astype(float) ** 2)
        noise_floor = np.percentile(np.abs(audio_data), 10) ** 2
        
        if noise_floor > 0:
            snr = 10 * np.log10(signal_power / noise_floor)
            confidence = min(max(snr / 40.0, 0.0), 1.0)  # Normalize to 0-1
        else:
            confidence = 0.8  # Default for very quiet signals
            
        return confidence

class EssentiaAnalyzer:
    """Advanced Essentia-based audio analysis and fingerprinting."""
    
    def __init__(self):
        self.algorithms = self._initialize_algorithms()
        
    def _initialize_algorithms(self) -> Dict[str, Any]:
        """Initialize Essentia algorithms."""



        try:
            return {
                'windowing': es.Windowing(type='hann'),
                'spectrum': es.Spectrum(),
                'spectral_peaks': es.SpectralPeaks(),
                'mfcc': es.MFCC(),
                'chroma': es.ChromaCrossSimilarity(),
                'tempo': es.PercivalBpmEstimator(),
                'key': es.KeyExtractor(),
                'loudness': es.LoudnessEBUR128(),
                'onset_detection': es.OnsetRate(),
                'harmonic': es.HarmonicBpm()
            }
        except Exception as e:
            logger.warning(f"Essentia initialization warning: {e}")
            return {}
    
    def extract_features(self, audio_path: str) -> Dict[str, Any]:
        """
        Extract comprehensive audio features using Essentia.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary containing extracted features
        """



        try:
            # Load audio
            loader = es.MonoLoader(filename=audio_path)
            audio = loader()
            
            features = {
                "basic_features": self._extract_basic_features(audio),
                "spectral_features": self._extract_spectral_features(audio),
                "rhythmic_features": self._extract_rhythmic_features(audio),
                "harmonic_features": self._extract_harmonic_features(audio),
                "perceptual_features": self._extract_perceptual_features(audio),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Essentia feature extraction failed for {audio_path}: {e}")
            return {"error": str(e)}
    
    def _extract_basic_features(self, audio: np.ndarray) -> Dict[str, Any]:
        """Extract basic audio features."""



        try:
            duration = len(audio) / 44100.0  # Assuming 44.1kHz
            rms_energy = es.RMS()(audio)
            zcr = es.ZeroCrossingRate()(audio)
            
            return {
                "duration": duration,
                "rms_energy": float(rms_energy),
                "zero_crossing_rate": float(zcr),
                "dynamic_range": float(np.max(audio) - np.min(audio))
            }
        except Exception as e:
            logger.error(f"Basic features extraction failed: {e}")
            return {}
    
    def _extract_spectral_features(self, audio: np.ndarray) -> Dict[str, Any]:
        """Extract spectral domain features."""



        try:
            # Frame-based analysis
            frame_size = 2048
            hop_size = 1024
            
            windowing = es.Windowing(type='hann')
            spectrum = es.Spectrum()
            spectral_centroid = es.SpectralCentroidTime()
            spectral_rolloff = es.SpectralRolloffTime()
            spectral_flux = es.SpectralFlux()
            
            centroids = []
            rolloffs = []
            fluxes = []
            
            for frame in es.FrameGenerator(audio, frameSize=frame_size, hopSize=hop_size):
                windowed_frame = windowing(frame)
                spectrum_frame = spectrum(windowed_frame)
                
                centroids.append(spectral_centroid(spectrum_frame))
                rolloffs.append(spectral_rolloff(spectrum_frame))
                fluxes.append(spectral_flux(spectrum_frame))
            
            return {
                "spectral_centroid_mean": float(np.mean(centroids)),
                "spectral_centroid_std": float(np.std(centroids)),
                "spectral_rolloff_mean": float(np.mean(rolloffs)),
                "spectral_rolloff_std": float(np.std(rolloffs)),
                "spectral_flux_mean": float(np.mean(fluxes)),
                "spectral_flux_std": float(np.std(fluxes))
            }
        except Exception as e:
            logger.error(f"Spectral features extraction failed: {e}")
            return {}
    
    def _extract_rhythmic_features(self, audio: np.ndarray) -> Dict[str, Any]:
        """Extract rhythm and tempo features."""



        try:
            tempo_estimator = es.PercivalBpmEstimator()
            onset_rate = es.OnsetRate()
            
            tempo = tempo_estimator(audio)
            onset_rate_value = onset_rate(audio)
            
            return {
                "tempo": float(tempo),
                "onset_rate": float(onset_rate_value)
            }
        except Exception as e:
            logger.error(f"Rhythmic features extraction failed: {e}")
            return {}
    
    def _extract_harmonic_features(self, audio: np.ndarray) -> Dict[str, Any]:
        """Extract harmonic and tonal features."""



        try:
            key_extractor = es.KeyExtractor()
            key, scale, strength = key_extractor(audio)
            
            return {
                "key": key,
                "scale": scale,
                "key_strength": float(strength)
            }
        except Exception as e:
            logger.error(f"Harmonic features extraction failed: {e}")
            return {}
    
    def _extract_perceptual_features(self, audio: np.ndarray) -> Dict[str, Any]:
        """Extract perceptual audio features."""



        try:
            loudness = es.LoudnessEBUR128()
            loudness_value = loudness(audio)
            
            return {
                "loudness_lufs": float(loudness_value)
            }
        except Exception as e:
            logger.error(f"Perceptual features extraction failed: {e}")
            return {}

class SpectralHashGenerator:
    """Generate spectral-based audio hashes for similarity detection."""
    
    def __init__(self, n_fft: int = 2048, hop_length: int = 512):
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.frequency_bins = 32  # Reduced dimensionality
        
    def generate_hash(self, audio_path: str) -> Dict[str, Any]:
        """
        Generate spectral hash from audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary containing hash and metadata
        """



        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=22050, mono=True)
            
            # Compute spectrogram
            stft = librosa.stft(y, n_fft=self.n_fft, hop_length=self.hop_length)
            magnitude = np.abs(stft)
            
            # Mel-scale conversion
            mel_spec = librosa.feature.melspectrogram(
                y=y, sr=sr, n_mels=self.frequency_bins
            )
            
            # Generate hash components
            spectral_hash = self._compute_spectral_hash(mel_spec)
            temporal_hash = self._compute_temporal_hash(mel_spec)
            
            return {
                "spectral_hash": spectral_hash,
                "temporal_hash": temporal_hash,
                "hash_size": len(spectral_hash),
                "duration": len(y) / sr,
                "sample_rate": sr,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Spectral hash generation failed for {audio_path}: {e}")
            return {"error": str(e)}
    
    def _compute_spectral_hash(self, mel_spec: np.ndarray) -> str:
        """Compute hash based on spectral characteristics."""
        # Average over time axis
        spectral_profile = np.mean(mel_spec, axis=1)
        
        # Normalize and quantize
        normalized_profile = (spectral_profile - np.mean(spectral_profile)) / np.std(spectral_profile)
        binary_hash = (normalized_profile > 0).astype(int)
        
        # Convert to hex string
        hash_string = ''.join([str(bit) for bit in binary_hash])
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _compute_temporal_hash(self, mel_spec: np.ndarray) -> str:
        """Compute hash based on temporal evolution."""
        # Compute differences between consecutive frames
        temporal_diff = np.diff(mel_spec, axis=1)
        
        # Average over frequency axis
        temporal_profile = np.mean(temporal_diff, axis=0)
        
        # Normalize and quantize
        if len(temporal_profile) > 0:
            normalized_profile = (temporal_profile - np.mean(temporal_profile)) / (np.std(temporal_profile) + 1e-8)
            binary_hash = (normalized_profile > 0).astype(int)
            hash_string = ''.join([str(bit) for bit in binary_hash])
            return hashlib.md5(hash_string.encode()).hexdigest()
        
        return ""

class NeuralAudioEmbedding:
    """Neural network-based audio embeddings using pre-trained models."""
    
    def __init__(self, model_name: str = "facebook/wav2vec2-base"):
        self.model_name = model_name
        self.model = None
        self.processor = None
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize the pre-trained model."""



        try:
            self.processor = Wav2Vec2Processor.from_pretrained(self.model_name)
            self.model = Wav2Vec2Model.from_pretrained(self.model_name)
            self.model.eval()
        except Exception as e:
            logger.warning(f"Neural model initialization failed: {e}")
    
    def extract_embedding(self, audio_path: str) -> Dict[str, Any]:
        """
        Extract neural embeddings from audio.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary containing embeddings and metadata
        """
        if not self.model or not self.processor:
            return {"error": "Model not initialized"}
            
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=16000, mono=True)
            
            # Process with model
            inputs = self.processor(y, sampling_rate=sr, return_tensors="pt", padding=True)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                
            # Extract embeddings
            embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            
            # Generate embedding fingerprint
            embedding_hash = self._compute_embedding_hash(embeddings)
            
            return {
                "embeddings": embeddings.tolist(),
                "embedding_hash": embedding_hash,
                "embedding_size": len(embeddings),
                "model_name": self.model_name,
                "duration": len(y) / sr,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Neural embedding extraction failed for {audio_path}: {e}")
            return {"error": str(e)}
    
    def _compute_embedding_hash(self, embeddings: np.ndarray) -> str:
        """Compute hash from neural embeddings."""
        # Normalize embeddings
        normalized_embeddings = embeddings / (np.linalg.norm(embeddings) + 1e-8)
        
        # Quantize to binary
        binary_embeddings = (normalized_embeddings > np.median(normalized_embeddings)).astype(int)
        
        # Convert to hash
        hash_string = ''.join([str(bit) for bit in binary_embeddings])
        return hashlib.md5(hash_string.encode()).hexdigest()

class AudioFingerprintingService:
    """
    Comprehensive audio fingerprinting service combining multiple algorithms.
    
    Features:
    - Chromaprint acoustic fingerprinting
    - Essentia audio analysis
    - Spectral hashing
    - Neural audio embeddings
    - Multi-level similarity matching
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.chromaprint_extractor = ChromaprintExtractor()
        self.essentia_analyzer = EssentiaAnalyzer()
        self.spectral_hasher = SpectralHashGenerator()
        self.neural_embedder = NeuralAudioEmbedding()
        
        # Similarity thresholds
        self.similarity_thresholds = {
            "chromaprint": 0.85,
            "spectral": 0.80,
            "neural": 0.90,
            "combined": 0.82
        }
        
    async def process_audio(self, audio_path: str, user_id: int) -> FingerprintResult:
        """
        Process audio file and generate comprehensive fingerprint.
        
        Args:
            audio_path: Path to audio file
            user_id: User ID for attribution
            
        Returns:
            FingerprintResult containing all fingerprint data
        """



        try:
            logger.info(f"Processing audio fingerprint for: {audio_path}")
            
            # Extract metadata
            metadata = await self._extract_metadata(audio_path)
            
            # Run all fingerprinting algorithms in parallel
            tasks = [
                asyncio.create_task(self._run_chromaprint(audio_path)),
                asyncio.create_task(self._run_essentia(audio_path)),
                asyncio.create_task(self._run_spectral_hash(audio_path)),
                asyncio.create_task(self._run_neural_embedding(audio_path))
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            chromaprint_result = results[0] if not isinstance(results[0], Exception) else {}
            essentia_result = results[1] if not isinstance(results[1], Exception) else {}
            spectral_result = results[2] if not isinstance(results[2], Exception) else {}
            neural_result = results[3] if not isinstance(results[3], Exception) else {}
            
            # Combine results
            fingerprint_data = {
                "chromaprint": chromaprint_result,
                "essentia": essentia_result,
                "spectral": spectral_result,
                "neural": neural_result,
                "metadata": metadata,
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
            # Generate combined hash
            combined_hash = self._generate_combined_hash(fingerprint_data)
            
            return FingerprintResult(
                user_id=user_id,
                content_type="audio",
                file_path=audio_path,
                fingerprint_data=fingerprint_data,
                hash_value=combined_hash,
                processing_time=datetime.utcnow(),
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Audio fingerprinting failed for {audio_path}: {e}")
            raise
    
    async def _extract_metadata(self, audio_path: str) -> AudioMetadata:
        """Extract comprehensive audio metadata."""



        try:
            y, sr = librosa.load(audio_path, sr=None, mono=True)
            
            # Basic metadata
            duration = len(y) / sr
            channels = 1  # Mono after loading
            
            # Compute additional features
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            mfcc = librosa.feature.mfcc(y=y, sr=sr)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            zcr = librosa.feature.zero_crossing_rate(y)
            
            return AudioMetadata(
                duration=duration,
                sample_rate=sr,
                channels=channels,
                bitrate=None,  # Would need different library for bitrate
                format=Path(audio_path).suffix.lower(),
                codec=None,
                tempo=float(tempo),
                key=None,  # Would need key detection
                loudness=float(np.mean(np.abs(y))),
                spectral_centroid=float(np.mean(spectral_centroid)),
                zero_crossing_rate=float(np.mean(zcr)),
                mfcc_features=mfcc,
                chroma_features=chroma
            )
            
        except Exception as e:
            logger.error(f"Metadata extraction failed for {audio_path}: {e}")
            return AudioMetadata(
                duration=0.0,
                sample_rate=0,
                channels=0,
                bitrate=None,
                format="unknown",
                codec=None,
                tempo=None,
                key=None,
                loudness=None,
                spectral_centroid=None,
                zero_crossing_rate=None,
                mfcc_features=None,
                chroma_features=None
            )
    
    async def _run_chromaprint(self, audio_path: str) -> Dict[str, Any]:
        """Run Chromaprint fingerprinting."""



        return await asyncio.get_event_loop().run_in_executor(
            None, self.chromaprint_extractor.extract_fingerprint, audio_path
        )
    
    async def _run_essentia(self, audio_path: str) -> Dict[str, Any]:
        """Run Essentia analysis."""



        return await asyncio.get_event_loop().run_in_executor(
            None, self.essentia_analyzer.extract_features, audio_path
        )
    
    async def _run_spectral_hash(self, audio_path: str) -> Dict[str, Any]:
        """Run spectral hash generation."""



        return await asyncio.get_event_loop().run_in_executor(
            None, self.spectral_hasher.generate_hash, audio_path
        )
    
    async def _run_neural_embedding(self, audio_path: str) -> Dict[str, Any]:
        """Run neural embedding extraction."""



        return await asyncio.get_event_loop().run_in_executor(
            None, self.neural_embedder.extract_embedding, audio_path
        )
    
    def _generate_combined_hash(self, fingerprint_data: Dict[str, Any]) -> str:
        """Generate combined hash from all fingerprint components."""
        hash_components = []
        
        # Extract key hash components
        if "chromaprint" in fingerprint_data and "raw_fingerprint" in fingerprint_data["chromaprint"]:
            hash_components.append(fingerprint_data["chromaprint"]["raw_fingerprint"])
            
        if "spectral" in fingerprint_data and "spectral_hash" in fingerprint_data["spectral"]:
            hash_components.append(fingerprint_data["spectral"]["spectral_hash"])
            
        if "neural" in fingerprint_data and "embedding_hash" in fingerprint_data["neural"]:
            hash_components.append(fingerprint_data["neural"]["embedding_hash"])
        
        # Combine and hash
        combined_string = "|".join(hash_components)
        return hashlib.sha256(combined_string.encode()).hexdigest()
    
    async def find_similar(self, fingerprint_data: Dict[str, Any], threshold: float = 0.8) -> List[SimilarityMatch]:
        """
        Find similar audio content based on fingerprint data.
        
        Args:
            fingerprint_data: Fingerprint data to match against
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            List of similarity matches
        """
        # This would typically interface with a vector database
        # For now, return empty list (implementation depends on storage backend)
        logger.info(f"Searching for similar audio with threshold {threshold}")
        return []
    
    def calculate_similarity(self, fp1: Dict[str, Any], fp2: Dict[str, Any]) -> float:
        """
        Calculate similarity score between two audio fingerprints.
        
        Args:
            fp1: First fingerprint data
            fp2: Second fingerprint data
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        similarity_scores = []
        
        # Chromaprint similarity
        if ("chromaprint" in fp1 and "chromaprint" in fp2 and
            "raw_fingerprint" in fp1["chromaprint"] and "raw_fingerprint" in fp2["chromaprint"]):
            chromaprint_sim = self._chromaprint_similarity(
                fp1["chromaprint"]["raw_fingerprint"],
                fp2["chromaprint"]["raw_fingerprint"]
            )
            similarity_scores.append(chromaprint_sim * 0.4)  # 40% weight
        
        # Spectral similarity
        if ("spectral" in fp1 and "spectral" in fp2 and
            "spectral_hash" in fp1["spectral"] and "spectral_hash" in fp2["spectral"]):
            spectral_sim = self._hash_similarity(
                fp1["spectral"]["spectral_hash"],
                fp2["spectral"]["spectral_hash"]
            )
            similarity_scores.append(spectral_sim * 0.3)  # 30% weight
        
        # Neural similarity
        if ("neural" in fp1 and "neural" in fp2 and
            "embeddings" in fp1["neural"] and "embeddings" in fp2["neural"]):
            neural_sim = self._neural_similarity(
                fp1["neural"]["embeddings"],
                fp2["neural"]["embeddings"]
            )
            similarity_scores.append(neural_sim * 0.3)  # 30% weight
        
        return sum(similarity_scores) if similarity_scores else 0.0
    
    def _chromaprint_similarity(self, fp1: str, fp2: str) -> float:
        """Calculate Chromaprint similarity."""
        # Simple hash comparison (could be enhanced with Hamming distance)
        return 1.0 if fp1 == fp2 else 0.0
    
    def _hash_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate hash similarity using Hamming distance."""
        if len(hash1) != len(hash2):
            return 0.0
        
        matches = sum(c1 == c2 for c1, c2 in zip(hash1, hash2))
        return matches / len(hash1)
    
    def _neural_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Calculate neural embedding similarity using cosine similarity."""



        try:
            emb1_array = np.array(emb1)
            emb2_array = np.array(emb2)
            
            # Cosine similarity
            dot_product = np.dot(emb1_array, emb2_array)
            norm1 = np.linalg.norm(emb1_array)
            norm2 = np.linalg.norm(emb2_array)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            logger.error(f"Neural similarity calculation failed: {e}")
            return 0.0
