"""Audio Detection Engine Module
============================

Advanced audio fingerprinting and detection engine for music content surveillance.
Implements state-of-the-art audio analysis and matching algorithms.

Author: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All Rights Reserved.

WARNING: This code and concept are protected intellectual property.
Any unauthorized use, copying, or distribution without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import librosa
import chromadb
from scipy.spatial.distance import cosine
from dataclasses import dataclass
import io
import hashlib
import json

logger = logging.getLogger(__name__)


@dataclass
class AudioFingerprint:
    """
Audio fingerprint data structure."""
    fingerprint_id: str
    user_id: str
    title: str
    artist: str
    duration: float
    sample_rate: int
    features: Dict[str, np.ndarray]
    hash_signature: str
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class AudioMatch:
    """
Audio match result structure."""
    original_fingerprint_id: str
    detected_url: str
    similarity_score: float
    confidence_level: float
    time_offset: float
    duration_match: float
    platform: str
    detected_at: datetime
    audio_features: Dict[str, Any]


class AudioFeatureExtractor:
    """
Advanced audio feature extraction for fingerprinting."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sample_rate = config.get("sample_rate", 22050)
        self.n_mfcc = config.get("n_mfcc", 13)
        self.n_chroma = config.get("n_chroma", 12)
        self.n_spectral_contrast = config.get("n_spectral_contrast", 7)
        self.hop_length = config.get("hop_length", 512)
        
    async def extract_features(self, audio_data: bytes) -> Dict[str, np.ndarray]:
        """Extract comprehensive audio features from audio data."""
        try:
            # Load audio from bytes
            audio_array, sr = librosa.load(io.BytesIO(audio_data), sr=self.sample_rate)
            
            features = {}
            
            # MFCC features (Mel-frequency cepstral coefficients)
            mfcc = librosa.feature.mfcc(
                y=audio_array, 
                sr=sr, 
                n_mfcc=self.n_mfcc,
                hop_length=self.hop_length
            )
            features["mfcc"] = mfcc
            features["mfcc_mean"] = np.mean(mfcc, axis=1)
            features["mfcc_std"] = np.std(mfcc, axis=1)
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(
                y=audio_array, 
                sr=sr,
                hop_length=self.hop_length
            )
            features["chroma"] = chroma
            features["chroma_mean"] = np.mean(chroma, axis=1)
            
            # Spectral contrast
            spectral_contrast = librosa.feature.spectral_contrast(
                y=audio_array, 
                sr=sr,
                hop_length=self.hop_length
            )
            features["spectral_contrast"] = spectral_contrast
            features["spectral_contrast_mean"] = np.mean(spectral_contrast, axis=1)
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(
                audio_array,
                hop_length=self.hop_length
            )
            features["zcr"] = zcr
            features["zcr_mean"] = np.mean(zcr)
            
            # Spectral centroid
            spectral_centroid = librosa.feature.spectral_centroid(
                y=audio_array, 
                sr=sr,
                hop_length=self.hop_length
            )
            features["spectral_centroid"] = spectral_centroid
            features["spectral_centroid_mean"] = np.mean(spectral_centroid)
            
            # Tempo and beat tracking
            tempo, beats = librosa.beat.beat_track(
                y=audio_array, 
                sr=sr,
                hop_length=self.hop_length
            )
            features["tempo"] = tempo
            features["beats"] = beats
            
            # Tonnetz (tonal centroid features)
            tonnetz = librosa.feature.tonnetz(
                y=librosa.effects.harmonic(audio_array), 
                sr=sr
            )
            features["tonnetz"] = tonnetz
            features["tonnetz_mean"] = np.mean(tonnetz, axis=1)
            
            # Mel-scale spectrogram
            mel_spectrogram = librosa.feature.melspectrogram(
                y=audio_array, 
                sr=sr,
                hop_length=self.hop_length
            )
            features["mel_spectrogram"] = mel_spectrogram
            features["mel_mean"] = np.mean(mel_spectrogram, axis=1)
            
            # Root Mean Square Energy
            rms = librosa.feature.rms(
                y=audio_array,
                hop_length=self.hop_length
            )
            features["rms"] = rms
            features["rms_mean"] = np.mean(rms)
            
            logger.info(f"Extracted {len(features)} audio feature sets")
            return features
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {e}")
            raise


class AudioSimilarityCalculator:
    """Advanced audio similarity calculation engine."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feature_weights = config.get("feature_weights", {
            "mfcc": 0.3,
            "chroma": 0.2,
            "spectral_contrast": 0.15,
            "zcr": 0.1,
            "spectral_centroid": 0.1,
            "tempo": 0.05,
            "tonnetz": 0.1
        })
        
    async def calculate_similarity(
        self, 
        features1: Dict[str, np.ndarray], 
        features2: Dict[str, np.ndarray]
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate comprehensive similarity between two audio feature sets."""
        try:
            similarities = {}
            weighted_sum = 0.0
            total_weight = 0.0
            
            # MFCC similarity
            if "mfcc_mean" in features1 and "mfcc_mean" in features2:
                mfcc_sim = 1 - cosine(features1["mfcc_mean"], features2["mfcc_mean"])
                similarities["mfcc"] = max(0, mfcc_sim)
                weighted_sum += similarities["mfcc"] * self.feature_weights.get("mfcc", 0.3)
                total_weight += self.feature_weights.get("mfcc", 0.3)
            
            # Chroma similarity
            if "chroma_mean" in features1 and "chroma_mean" in features2:
                chroma_sim = 1 - cosine(features1["chroma_mean"], features2["chroma_mean"])
                similarities["chroma"] = max(0, chroma_sim)
                weighted_sum += similarities["chroma"] * self.feature_weights.get("chroma", 0.2)
                total_weight += self.feature_weights.get("chroma", 0.2)
            
            # Spectral contrast similarity
            if "spectral_contrast_mean" in features1 and "spectral_contrast_mean" in features2:
                sc_sim = 1 - cosine(features1["spectral_contrast_mean"], features2["spectral_contrast_mean"])
                similarities["spectral_contrast"] = max(0, sc_sim)
                weighted_sum += similarities["spectral_contrast"] * self.feature_weights.get("spectral_contrast", 0.15)
                total_weight += self.feature_weights.get("spectral_contrast", 0.15)
            
            # ZCR similarity
            if "zcr_mean" in features1 and "zcr_mean" in features2:
                zcr_diff = abs(features1["zcr_mean"] - features2["zcr_mean"])
                zcr_sim = 1 / (1 + zcr_diff)
                similarities["zcr"] = zcr_sim
                weighted_sum += similarities["zcr"] * self.feature_weights.get("zcr", 0.1)
                total_weight += self.feature_weights.get("zcr", 0.1)
            
            # Spectral centroid similarity
            if "spectral_centroid_mean" in features1 and "spectral_centroid_mean" in features2:
                sc_diff = abs(features1["spectral_centroid_mean"] - features2["spectral_centroid_mean"])
                sc_sim = 1 / (1 + sc_diff / 1000)  # Normalize by 1000
                similarities["spectral_centroid"] = sc_sim
                weighted_sum += similarities["spectral_centroid"] * self.feature_weights.get("spectral_centroid", 0.1)
                total_weight += self.feature_weights.get("spectral_centroid", 0.1)
            
            # Tempo similarity
            if "tempo" in features1 and "tempo" in features2:
                tempo_diff = abs(features1["tempo"] - features2["tempo"])
                tempo_sim = 1 / (1 + tempo_diff / 60)  # Normalize by 60 BPM
                similarities["tempo"] = tempo_sim
                weighted_sum += similarities["tempo"] * self.feature_weights.get("tempo", 0.05)
                total_weight += self.feature_weights.get("tempo", 0.05)
            
            # Tonnetz similarity
            if "tonnetz_mean" in features1 and "tonnetz_mean" in features2:
                tonnetz_sim = 1 - cosine(features1["tonnetz_mean"], features2["tonnetz_mean"])
                similarities["tonnetz"] = max(0, tonnetz_sim)
                weighted_sum += similarities["tonnetz"] * self.feature_weights.get("tonnetz", 0.1)
                total_weight += self.feature_weights.get("tonnetz", 0.1)
            
            # Calculate overall similarity
            overall_similarity = weighted_sum / total_weight if total_weight > 0 else 0.0
            
            logger.debug(f"Audio similarity calculated: {overall_similarity:.4f}")
            return overall_similarity, similarities
            
        except Exception as e:
            logger.error(f"Audio similarity calculation failed: {e}")
            return 0.0, {}


class AudioDetectionEngine:
    """
    Advanced audio detection engine for content surveillance.
    
    Implements sophisticated audio fingerprinting, matching, and detection
    algorithms for protecting musical content across platforms.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feature_extractor = AudioFeatureExtractor(config.get("feature_extraction", {}))
        self.similarity_calculator = AudioSimilarityCalculator(config.get("similarity", {}))
        
        # ChromaDB vector store for fast similarity search
        self.chroma_client = None
        self.fingerprint_collection = None
        
        # Detection thresholds
        self.similarity_threshold = config.get("similarity_threshold", 0.8)
        self.confidence_threshold = config.get("confidence_threshold", 0.75)
        
        # Performance metrics
        self.detection_stats = {
            "total_fingerprints": 0,
            "total_detections": 0,
            "false_positives": 0,
            "processing_time_avg": 0.0
        }
        
    async def initialize(self) -> bool:
        """Initialize the audio detection engine."""
        try:
            # Initialize ChromaDB client
            self.chroma_client = chromadb.Client()
            
            # Get or create fingerprint collection
            try:
                self.fingerprint_collection = self.chroma_client.get_collection(
                    name="audio_fingerprints"
                )
            except:
                self.fingerprint_collection = self.chroma_client.create_collection(
                    name="audio_fingerprints",
                    metadata={"description": "Audio fingerprint collection for content protection"}
                )
            
            logger.info("AudioDetectionEngine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AudioDetectionEngine: {e}")
            return False
    
    async def create_fingerprint(
        self, 
        audio_data: bytes, 
        metadata: Dict[str, Any]
    ) -> AudioFingerprint:
        """Create audio fingerprint from audio data."""
        try:
            start_time = datetime.utcnow()
            
            # Extract audio features
            features = await self.feature_extractor.extract_features(audio_data)
            
            # Create hash signature
            feature_string = json.dumps({
                k: v.tolist() if isinstance(v, np.ndarray) else v 
                for k, v in features.items() 
                if k.endswith("_mean") or k in ["tempo"]
            }, sort_keys=True)
            hash_signature = hashlib.sha256(feature_string.encode()).hexdigest()
            
            # Create fingerprint object
            fingerprint = AudioFingerprint(
                fingerprint_id=hashlib.sha256(f"{metadata.get('user_id', '')}{hash_signature}{start_time.isoformat()}".encode()).hexdigest(),
                user_id=metadata.get("user_id", ""),
                title=metadata.get("title", ""),
                artist=metadata.get("artist", ""),
                duration=metadata.get("duration", 0.0),
                sample_rate=self.feature_extractor.sample_rate,
                features=features,
                hash_signature=hash_signature,
                created_at=start_time,
                metadata=metadata
            )
            
            # Store in vector database
            await self._store_fingerprint(fingerprint)
            
            self.detection_stats["total_fingerprints"] += 1
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Audio fingerprint created in {processing_time:.2f}s: {fingerprint.fingerprint_id}")
            
            return fingerprint
            
        except Exception as e:
            logger.error(f"Audio fingerprint creation failed: {e}")
            raise
    
    async def _store_fingerprint(self, fingerprint: AudioFingerprint) -> None:
        """Store fingerprint in vector database."""
        try:
            # Create embedding vector from key features
            embedding_features = []
            
            if "mfcc_mean" in fingerprint.features:
                embedding_features.extend(fingerprint.features["mfcc_mean"].tolist())
            if "chroma_mean" in fingerprint.features:
                embedding_features.extend(fingerprint.features["chroma_mean"].tolist())
            if "spectral_contrast_mean" in fingerprint.features:
                embedding_features.extend(fingerprint.features["spectral_contrast_mean"].tolist())
            
            # Pad or truncate to fixed size (384 dimensions)
            target_size = 384
            if len(embedding_features) < target_size:
                embedding_features.extend([0.0] * (target_size - len(embedding_features)))
            else:
                embedding_features = embedding_features[:target_size]
            
            # Store in ChromaDB
            self.fingerprint_collection.add(
                embeddings=[embedding_features],
                documents=[json.dumps({
                    "title": fingerprint.title,
                    "artist": fingerprint.artist,
                    "duration": fingerprint.duration,
                    "hash_signature": fingerprint.hash_signature
                })],
                metadatas=[{
                    "fingerprint_id": fingerprint.fingerprint_id,
                    "user_id": fingerprint.user_id,
                    "created_at": fingerprint.created_at.isoformat(),
                    "sample_rate": fingerprint.sample_rate
                }],
                ids=[fingerprint.fingerprint_id]
            )
            
            logger.debug(f"Fingerprint stored in vector database: {fingerprint.fingerprint_id}")
            
        except Exception as e:
            logger.error(f"Failed to store fingerprint: {e}")
            raise
    
    async def detect_matches(
        self, 
        audio_data: bytes, 
        detection_metadata: Dict[str, Any]
    ) -> List[AudioMatch]:
        """Detect audio matches against stored fingerprints."""
        try:
            start_time = datetime.utcnow()
            
            # Extract features from input audio
            input_features = await self.feature_extractor.extract_features(audio_data)
            
            # Create embedding for similarity search
            embedding_features = []
            if "mfcc_mean" in input_features:
                embedding_features.extend(input_features["mfcc_mean"].tolist())
            if "chroma_mean" in input_features:
                embedding_features.extend(input_features["chroma_mean"].tolist())
            if "spectral_contrast_mean" in input_features:
                embedding_features.extend(input_features["spectral_contrast_mean"].tolist())
            
            # Pad or truncate to fixed size
            target_size = 384
            if len(embedding_features) < target_size:
                embedding_features.extend([0.0] * (target_size - len(embedding_features)))
            else:
                embedding_features = embedding_features[:target_size]
            
            # Search for similar fingerprints
            search_results = self.fingerprint_collection.query(
                query_embeddings=[embedding_features],
                n_results=20,  # Get top 20 candidates
                include=["documents", "metadatas", "distances"]
            )
            
            matches = []
            
            # Process search results
            if search_results['ids'][0]:
                for i, fingerprint_id in enumerate(search_results['ids'][0]):
                    distance = search_results['distances'][0][i]
                    metadata = search_results['metadatas'][0][i]
                    
                    # Convert distance to similarity score
                    initial_similarity = max(0, 1 - distance)
                    
                    # Skip if initial similarity is too low
                    if initial_similarity < self.similarity_threshold * 0.8:
                        continue
                    
                    # Load full fingerprint for detailed comparison
                    stored_fingerprint = await self._load_fingerprint(fingerprint_id)
                    if not stored_fingerprint:
                        continue
                    
                    # Calculate detailed similarity
                    detailed_similarity, feature_similarities = await self.similarity_calculator.calculate_similarity(
                        input_features, stored_fingerprint.features
                    )
                    
                    # Check if similarity meets threshold
                    if detailed_similarity >= self.similarity_threshold:
                        confidence = self._calculate_confidence(
                            detailed_similarity, 
                            feature_similarities,
                            input_features,
                            stored_fingerprint.features
                        )
                        
                        if confidence >= self.confidence_threshold:
                            match = AudioMatch(
                                original_fingerprint_id=fingerprint_id,
                                detected_url=detection_metadata.get("url", ""),
                                similarity_score=detailed_similarity,
                                confidence_level=confidence,
                                time_offset=self._calculate_time_alignment(
                                    detection_audio_features, 
                                    stored_fingerprint.features
                                ),  # Time alignment calculation
                                duration_match=min(
                                    detection_metadata.get("duration", 0.0),
                                    stored_fingerprint.duration
                                ),
                                platform=detection_metadata.get("platform", ""),
                                detected_at=datetime.utcnow(),
                                audio_features=feature_similarities
                            )
                            matches.append(match)
            
            self.detection_stats["total_detections"] += len(matches)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Audio detection completed in {processing_time:.2f}s: {len(matches)} matches found")
            
            return matches
            
        except Exception as e:
            logger.error(f"Audio detection failed: {e}")
            return []
    
    async def _load_fingerprint(self, fingerprint_id: str) -> Optional[AudioFingerprint]:
        """Load full fingerprint data (placeholder - implement with your storage system)."""
        # This would load the full fingerprint data from your database
        # For now, return None to indicate not found
        return True
    
    def _calculate_confidence(
        self, 
        similarity_score: float, 
        feature_similarities: Dict[str, float],
        input_features: Dict[str, Any],
        stored_features: Dict[str, Any]
    ) -> float:
        """
Calculate confidence level for match."""
        try:
            # Base confidence from overall similarity
            confidence = similarity_score
            
            # Boost confidence if multiple features match well
            high_similarity_features = sum(1 for sim in feature_similarities.values() if sim > 0.8)
            feature_boost = min(0.1, high_similarity_features * 0.02)
            confidence += feature_boost
            
            # Check tempo consistency (if available)
            if "tempo" in input_features and "tempo" in stored_features:
                tempo_diff = abs(input_features["tempo"] - stored_features["tempo"])
                if tempo_diff < 5:  # Within 5 BPM
                    confidence += 0.05
            
            # Ensure confidence is between 0 and 1
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return similarity_score
    
    async def get_detection_statistics(self) -> Dict[str, Any]:
        """Get detection engine statistics."""
        return {
            "engine_type": "audio",
            "status": "active",
            "statistics": self.detection_stats,
            "thresholds": {
                "similarity_threshold": self.similarity_threshold,
                "confidence_threshold": self.confidence_threshold
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _calculate_time_alignment(self, detected_features: Dict[str, np.ndarray], 
                                 reference_features: Dict[str, np.ndarray]) -> float:
        """Calculate time offset between detected and reference audio."""
        try:
            # Use MFCC features for time alignment
            detected_mfcc = detected_features.get('mfcc')
            reference_mfcc = reference_features.get('mfcc')
            
            if detected_mfcc is None or reference_mfcc is None:
                return 0.0
            
            # Cross-correlation to find optimal alignment
            # Ensure both arrays are 2D (features x time)
            if len(detected_mfcc.shape) == 1:
                detected_mfcc = detected_mfcc.reshape(-1, 1)
            if len(reference_mfcc.shape) == 1:
                reference_mfcc = reference_mfcc.reshape(-1, 1)
            
            # Use first MFCC coefficient for alignment
            detected_signal = detected_mfcc[0, :] if detected_mfcc.shape[0] > 0 else detected_mfcc.flatten()
            reference_signal = reference_mfcc[0, :] if reference_mfcc.shape[0] > 0 else reference_mfcc.flatten()
            
            # Simple cross-correlation for time alignment
            max_lag = min(len(detected_signal), len(reference_signal)) // 2
            correlations = np.correlate(reference_signal, detected_signal, mode='full')
            
            # Find peak correlation
            center = len(correlations) // 2
            start_idx = max(0, center - max_lag)
            end_idx = min(len(correlations), center + max_lag)
            
            local_correlations = correlations[start_idx:end_idx]
            max_corr_idx = np.argmax(local_correlations) + start_idx
            
            # Convert to time offset (assuming 22050 Hz sample rate, 512 hop length)
            time_offset = (max_corr_idx - center) * 512 / 22050
            
            return float(time_offset)
            
        except Exception as e:
            logger.warning(f"Time alignment calculation failed: {e}")
            return 0.0

    async def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            if self.chroma_client:
                # ChromaDB cleanup if needed
                pass
            logger.info("AudioDetectionEngine cleanup completed")
        except Exception as e:
            logger.error(f"AudioDetectionEngine cleanup failed: {e}")
