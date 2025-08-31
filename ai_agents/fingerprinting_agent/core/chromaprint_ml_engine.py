"""Enhanced Chromaprint + ML Audio Fingerprinting System
====================================================

Advanced audio fingerprinting system combining Chromaprint acoustic fingerprinting
with machine learning for improved accuracy and intelligent audio analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved
"""
import asyncio
import logging
import hashlib
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import io
import tempfile
import os

try:
    import librosa
    import soundfile as sf
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False

try:
    import acoustid
    import chromaprint
    HAS_CHROMAPRINT = True
except ImportError:
    HAS_CHROMAPRINT = False

try:
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

logger = logging.getLogger(__name__)

@dataclass
class AudioFingerprint:
    """Container for audio fingerprint data"""    content_id: str
    chromaprint_hash: str
    acoustic_features: List[float]
    spectral_features: List[float]
    chromaprint_raw: Optional[str] = None
    duration: float = 0.0
    sample_rate: int = 22050
    confidence_score: float = 1.0
    metadata: Dict[str, Any] = None
    timestamp: datetime = None

@dataclass
class FingerprintMatch:
    """Result of fingerprint matching"""    source_id: str
    target_id: str
    similarity_score: float
    match_type: str  # 'exact', 'near_duplicate', 'similar'
    confidence: float
    match_details: Dict[str, Any]
    detected_at: datetime = None

class ChromaprintMLEngine:
    """    Enhanced Chromaprint + ML Audio Fingerprinting Engine
    
    Combines traditional acoustic fingerprinting with machine learning for:
    - High-accuracy duplicate detection
    - Similar content identification  
    - Music similarity analysis
    - Copyright infringement detection
    - Real-time audio monitoring
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.sample_rate = self.config.get('sample_rate', 22050)
        self.min_duration = self.config.get('min_duration', 10.0)  # seconds
        self.similarity_threshold = self.config.get('similarity_threshold', 0.85)
        
        # ML components
        self.feature_scaler = StandardScaler() if HAS_SKLEARN else None
        self.pca_reducer = None
        self.similarity_index = None
        
        # Fingerprint database (in production, this would be persistent storage)
        self.fingerprint_db = {}
        self.feature_vectors = []
        self.content_ids = []
        
        # Performance tracking
        self.metrics = {
            'fingerprints_generated': 0,
            'matches_found': 0,
            'processing_time_avg': 0.0,
            'accuracy_score': 0.0
        }
        
        self._initialize_ml_components()
    
    def _initialize_ml_components(self):
        """Initialize machine learning components"""        try:
            if HAS_SKLEARN:
                # Initialize dimensionality reduction
                self.pca_reducer = PCA(n_components=min(128, self.config.get('pca_components', 64)))
                logger.info("ML components initialized successfully")
            else:
                logger.warning("Scikit-learn not available, using basic fingerprinting only")
                
            if HAS_FAISS:
                # Initialize FAISS index for fast similarity search
                dimension = self.config.get('feature_dimension', 128)
                self.similarity_index = faiss.IndexFlatIP(dimension)
                logger.info(f"FAISS similarity index initialized with dimension {dimension}")
            
        except Exception as e:
            logger.warning(f"ML initialization warning: {e}")
    
    async def generate_fingerprint(
        self, 
        audio_data: bytes,
        content_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AudioFingerprint:
        """        Generate comprehensive audio fingerprint combining Chromaprint and ML features
        
        Args:
            audio_data: Raw audio bytes
            content_id: Unique identifier for the content
            metadata: Optional metadata about the audio
            
        Returns:
            AudioFingerprint with combined fingerprint data
        """        start_time = asyncio.get_event_loop().time()
        
        try:
            # Load and preprocess audio
            audio_array, sr, duration = await self._load_audio(audio_data)
            
            # Generate Chromaprint fingerprint
            chromaprint_hash, chromaprint_raw = await self._generate_chromaprint(audio_array, sr)
            
            # Extract acoustic features
            acoustic_features = await self._extract_acoustic_features(audio_array, sr)
            
            # Extract spectral features
            spectral_features = await self._extract_spectral_features(audio_array, sr)
            
            # Calculate confidence score based on audio quality
            confidence_score = self._calculate_confidence(audio_array, duration)
            
            fingerprint = AudioFingerprint(
                content_id=content_id,
                chromaprint_hash=chromaprint_hash,
                acoustic_features=acoustic_features,
                spectral_features=spectral_features,
                chromaprint_raw=chromaprint_raw,
                duration=duration,
                sample_rate=sr,
                confidence_score=confidence_score,
                metadata=metadata or {},
                timestamp=datetime.utcnow()
            )
            
            # Store fingerprint
            await self._store_fingerprint(fingerprint)
            
            # Update metrics
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            self.metrics['fingerprints_generated'] += 1
            self.metrics['processing_time_avg'] = (
                self.metrics['processing_time_avg'] + processing_time
            ) / self.metrics['fingerprints_generated']
            
            return fingerprint
            
        except Exception as e:
            logger.error(f"Fingerprint generation failed for {content_id}: {e}")
            raise
    
    async def find_matches(
        self, 
        fingerprint: AudioFingerprint,
        max_results: int = 10
    ) -> List[FingerprintMatch]:
        """        Find matching or similar content using combined fingerprinting approaches
        
        Args:
            fingerprint: AudioFingerprint to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of FingerprintMatch results
        """        try:
            matches = []
            
            # 1. Exact Chromaprint matching
            exact_matches = await self._find_chromaprint_matches(fingerprint)
            matches.extend(exact_matches)
            
            # 2. ML-based similarity matching
            if HAS_SKLEARN and len(self.feature_vectors) > 0:
                similar_matches = await self._find_ml_matches(fingerprint)
                matches.extend(similar_matches)
            
            # 3. FAISS-based fast similarity search
            if HAS_FAISS and self.similarity_index and self.similarity_index.ntotal > 0:
                faiss_matches = await self._find_faiss_matches(fingerprint)
                matches.extend(faiss_matches)
            
            # Remove duplicates and sort by similarity score
            unique_matches = self._deduplicate_matches(matches)
            sorted_matches = sorted(unique_matches, key=lambda x: x.similarity_score, reverse=True)
            
            # Update metrics
            self.metrics['matches_found'] += len(sorted_matches)
            
            return sorted_matches[:max_results]
            
        except Exception as e:
            logger.error(f"Match finding failed: {e}")
            raise
    
    async def batch_fingerprint(
        self, 
        audio_files: List[Dict[str, Any]]
    ) -> List[AudioFingerprint]:
        """        Generate fingerprints for multiple audio files in batch
        
        Args:
            audio_files: List of dictionaries with 'data', 'content_id', and optional 'metadata'
            
        Returns:
            List of AudioFingerprint objects
        """        fingerprints = []
        
        for audio_file in audio_files:
            try:
                fingerprint = await self.generate_fingerprint(
                    audio_file['data'],
                    audio_file['content_id'],
                    audio_file.get('metadata')
                )
                fingerprints.append(fingerprint)
                
            except Exception as e:
                logger.error(f"Batch fingerprinting failed for {audio_file.get('content_id')}: {e}")
                continue
        
        return fingerprints
    
    async def detect_copyright_infringement(
        self, 
        audio_data: bytes,
        reference_database: Optional[List[AudioFingerprint]] = None
    ) -> Dict[str, Any]:
        """        Detect potential copyright infringement using advanced matching
        
        Returns:
            Dictionary with infringement analysis results
        """        try:
            # Generate fingerprint for input audio
            temp_id = f"temp_{int(datetime.utcnow().timestamp())}"
            input_fingerprint = await self.generate_fingerprint(audio_data, temp_id)
            
            # Find matches
            matches = await self.find_matches(input_fingerprint)
            
            # Analyze matches for potential infringement
            infringement_analysis = {
                'potential_matches': len(matches),
                'high_similarity_matches': len([m for m in matches if m.similarity_score > 0.9]),
                'moderate_similarity_matches': len([m for m in matches if 0.7 <= m.similarity_score <= 0.9]),
                'infringement_risk': 'none',
                'confidence': 0.0,
                'detailed_matches': []
            }
            
            if matches:
                best_match = matches[0]
                infringement_analysis['confidence'] = best_match.confidence
                
                if best_match.similarity_score > 0.95:
                    infringement_analysis['infringement_risk'] = 'high'
                elif best_match.similarity_score > 0.85:
                    infringement_analysis['infringement_risk'] = 'moderate'
                elif best_match.similarity_score > 0.7:
                    infringement_analysis['infringement_risk'] = 'low'
                
                # Add detailed match information
                for match in matches[:5]:  # Top 5 matches
                    infringement_analysis['detailed_matches'].append({
                        'target_id': match.target_id,
                        'similarity_score': match.similarity_score,
                        'match_type': match.match_type,
                        'confidence': match.confidence
                    })
            
            return infringement_analysis
            
        except Exception as e:
            logger.error(f"Copyright infringement detection failed: {e}")
            raise
    
    # Private helper methods
    
    async def _load_audio(self, audio_data: bytes) -> Tuple[np.ndarray, int, float]:
        """Load audio data from bytes"""        try:
            if HAS_LIBROSA:
                # Use librosa for professional audio loading
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_file.write(audio_data)
                    temp_path = temp_file.name
                
                try:
                    audio_array, sr = librosa.load(temp_path, sr=self.sample_rate)
                    duration = len(audio_array) / sr
                    return audio_array, sr, duration
                finally:
                    os.unlink(temp_path)
            else:
                # Basic audio loading fallback
                return np.frombuffer(audio_data, dtype=np.int16).astype(np.float32), self.sample_rate, len(audio_data) / self.sample_rate
                
        except Exception as e:
            logger.error(f"Audio loading failed: {e}")
            raise
    
    async def _generate_chromaprint(self, audio_array: np.ndarray, sr: int) -> Tuple[str, Optional[str]]:
        """Generate Chromaprint acoustic fingerprint"""        try:
            if HAS_CHROMAPRINT:
                # Convert to format expected by chromaprint
                audio_int16 = (audio_array * 32767).astype(np.int16)
                
                # Generate chromaprint
                raw_fingerprint = chromaprint.encode(audio_int16.tobytes(), sr, algorithm=2)
                fingerprint_hash = hashlib.sha256(raw_fingerprint.encode()).hexdigest()
                
                return fingerprint_hash, raw_fingerprint
            else:
                # Fallback: generate hash from audio features
                feature_string = ','.join(f'{x:.6f}' for x in audio_array[:1000])  # First 1000 samples
                fingerprint_hash = hashlib.sha256(feature_string.encode()).hexdigest()
                
                return fingerprint_hash, None
                
        except Exception as e:
            logger.error(f"Chromaprint generation failed: {e}")
            raise
    
    async def _extract_acoustic_features(self, audio_array: np.ndarray, sr: int) -> List[float]:
        """Extract acoustic features for ML-based matching"""        try:
            if HAS_LIBROSA:
                # Extract comprehensive acoustic features
                features = []
                
                # Spectral features
                spectral_centroid = librosa.feature.spectral_centroid(y=audio_array, sr=sr)
                features.extend(np.mean(spectral_centroid, axis=1).tolist())
                
                spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_array, sr=sr)
                features.extend(np.mean(spectral_bandwidth, axis=1).tolist())
                
                spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_array, sr=sr)
                features.extend(np.mean(spectral_rolloff, axis=1).tolist())
                
                # MFCC features
                mfcc = librosa.feature.mfcc(y=audio_array, sr=sr, n_mfcc=13)
                features.extend(np.mean(mfcc, axis=1).tolist())
                
                # Zero crossing rate
                zcr = librosa.feature.zero_crossing_rate(audio_array)
                features.extend(np.mean(zcr, axis=1).tolist())
                
                # Tempo
                tempo, _ = librosa.beat.beat_track(y=audio_array, sr=sr)
                features.append(float(tempo))
                
                return features
            else:
                # Basic feature extraction
                return [
                    float(np.mean(audio_array)),
                    float(np.std(audio_array)),
                    float(np.max(audio_array)),
                    float(np.min(audio_array))
                ]
                
        except Exception as e:
            logger.error(f"Acoustic feature extraction failed: {e}")
            return []
    
    async def _extract_spectral_features(self, audio_array: np.ndarray, sr: int) -> List[float]:
        """Extract spectral features for advanced analysis"""        try:
            if HAS_LIBROSA:
                # Chroma features
                chroma = librosa.feature.chroma_stft(y=audio_array, sr=sr)
                chroma_features = np.mean(chroma, axis=1).tolist()
                
                # Tonnetz features
                tonnetz = librosa.feature.tonnetz(y=audio_array, sr=sr)
                tonnetz_features = np.mean(tonnetz, axis=1).tolist()
                
                # Spectral contrast
                contrast = librosa.feature.spectral_contrast(y=audio_array, sr=sr)
                contrast_features = np.mean(contrast, axis=1).tolist()
                
                return chroma_features + tonnetz_features + contrast_features
            else:
                # Basic spectral analysis using FFT
                fft = np.fft.fft(audio_array)
                magnitude = np.abs(fft)
                return [
                    float(np.mean(magnitude)),
                    float(np.std(magnitude)),
                    float(np.max(magnitude))
                ]
                
        except Exception as e:
            logger.error(f"Spectral feature extraction failed: {e}")
            return []
    
    def _calculate_confidence(self, audio_array: np.ndarray, duration: float) -> float:
        """Calculate confidence score for the fingerprint"""        try:
            confidence = 1.0
            
            # Reduce confidence for very short audio
            if duration < self.min_duration:
                confidence *= (duration / self.min_duration)
            
            # Reduce confidence for very quiet audio
            rms_energy = np.sqrt(np.mean(audio_array ** 2))
            if rms_energy < 0.01:
                confidence *= (rms_energy / 0.01)
            
            # Reduce confidence for clipped audio
            clipping_ratio = np.sum(np.abs(audio_array) > 0.95) / len(audio_array)
            if clipping_ratio > 0.01:
                confidence *= (1.0 - clipping_ratio)
            
            return max(0.1, min(1.0, confidence))
            
        except Exception:
            return 0.5  # Default confidence
    
    async def _store_fingerprint(self, fingerprint: AudioFingerprint):
        """Store fingerprint in database and update ML components"""        try:
            # Store in fingerprint database
            self.fingerprint_db[fingerprint.content_id] = fingerprint
            
            # Update ML components
            if HAS_SKLEARN and fingerprint.acoustic_features:
                combined_features = fingerprint.acoustic_features + fingerprint.spectral_features
                if len(combined_features) > 0:
                    self.feature_vectors.append(combined_features)
                    self.content_ids.append(fingerprint.content_id)
                    
                    # Update scaler and PCA if we have enough data
                    if len(self.feature_vectors) > 10:
                        await self._update_ml_models()
            
            # Update FAISS index
            if HAS_FAISS and self.similarity_index and fingerprint.acoustic_features:
                combined_features = np.array(fingerprint.acoustic_features + fingerprint.spectral_features).astype('float32')
                if len(combined_features) >= self.similarity_index.d:
                    self.similarity_index.add(combined_features.reshape(1, -1))
            
        except Exception as e:
            logger.error(f"Fingerprint storage failed: {e}")
    
    async def _update_ml_models(self):
        """Update ML models with new data"""        try:
            if HAS_SKLEARN and len(self.feature_vectors) > 1:
                # Update feature scaler
                self.feature_scaler.fit(self.feature_vectors)
                
                # Update PCA if we have enough features
                if len(self.feature_vectors) > self.pca_reducer.n_components:
                    self.pca_reducer.fit(self.feature_scaler.transform(self.feature_vectors))
                    
        except Exception as e:
            logger.warning(f"ML model update failed: {e}")
    
    async def _find_chromaprint_matches(self, fingerprint: AudioFingerprint) -> List[FingerprintMatch]:
        """Find exact Chromaprint matches"""        matches = []
        
        for content_id, stored_fingerprint in self.fingerprint_db.items():
            if content_id != fingerprint.content_id:
                if stored_fingerprint.chromaprint_hash == fingerprint.chromaprint_hash:
                    match = FingerprintMatch(
                        source_id=fingerprint.content_id,
                        target_id=content_id,
                        similarity_score=1.0,
                        match_type='exact',
                        confidence=min(fingerprint.confidence_score, stored_fingerprint.confidence_score),
                        match_details={'method': 'chromaprint_exact'},
                        detected_at=datetime.utcnow()
                    )
                    matches.append(match)
        
        return matches
    
    async def _find_ml_matches(self, fingerprint: AudioFingerprint) -> List[FingerprintMatch]:
        """Find matches using ML-based similarity"""        matches = []
        
        if not HAS_SKLEARN or not fingerprint.acoustic_features:
            return matches
        
        try:
            query_features = fingerprint.acoustic_features + fingerprint.spectral_features
            
            for i, stored_features in enumerate(self.feature_vectors):
                if len(query_features) == len(stored_features):
                    # Calculate cosine similarity
                    similarity = cosine_similarity([query_features], [stored_features])[0][0]
                    
                    if similarity > self.similarity_threshold:
                        match = FingerprintMatch(
                            source_id=fingerprint.content_id,
                            target_id=self.content_ids[i],
                            similarity_score=float(similarity),
                            match_type='similar' if similarity < 0.95 else 'near_duplicate',
                            confidence=fingerprint.confidence_score * similarity,
                            match_details={
                                'method': 'ml_similarity',
                                'feature_similarity': similarity
                            },
                            detected_at=datetime.utcnow()
                        )
                        matches.append(match)
        
        except Exception as e:
            logger.error(f"ML matching failed: {e}")
        
        return matches
    
    async def _find_faiss_matches(self, fingerprint: AudioFingerprint) -> List[FingerprintMatch]:
        """Find matches using FAISS similarity search"""        matches = []
        
        if not HAS_FAISS or not self.similarity_index or not fingerprint.acoustic_features:
            return matches
        
        try:
            query_features = np.array(fingerprint.acoustic_features + fingerprint.spectral_features).astype('float32')
            
            if len(query_features) >= self.similarity_index.d:
                # Search for similar vectors
                k = min(10, self.similarity_index.ntotal)  # Number of results to return
                similarities, indices = self.similarity_index.search(query_features.reshape(1, -1), k)
                
                for similarity, idx in zip(similarities[0], indices[0]):
                    if idx < len(self.content_ids) and similarity > self.similarity_threshold:
                        match = FingerprintMatch(
                            source_id=fingerprint.content_id,
                            target_id=self.content_ids[idx],
                            similarity_score=float(similarity),
                            match_type='similar' if similarity < 0.95 else 'near_duplicate',
                            confidence=fingerprint.confidence_score * similarity,
                            match_details={
                                'method': 'faiss_similarity',
                                'vector_similarity': similarity
                            },
                            detected_at=datetime.utcnow()
                        )
                        matches.append(match)
        
        except Exception as e:
            logger.error(f"FAISS matching failed: {e}")
        
        return matches
    
    def _deduplicate_matches(self, matches: List[FingerprintMatch]) -> List[FingerprintMatch]:
        """Remove duplicate matches and keep the best score for each target"""        unique_matches = {}
        
        for match in matches:
            key = (match.source_id, match.target_id)
            if key not in unique_matches or match.similarity_score > unique_matches[key].similarity_score:
                unique_matches[key] = match
        
        return list(unique_matches.values())
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get engine statistics and configuration"""        return {
            'fingerprints_stored': len(self.fingerprint_db),
            'feature_vectors': len(self.feature_vectors),
            'has_chromaprint': HAS_CHROMAPRINT,
            'has_librosa': HAS_LIBROSA,
            'has_sklearn': HAS_SKLEARN,
            'has_faiss': HAS_FAISS,
            'metrics': self.metrics,
            'config': {
                'sample_rate': self.sample_rate,
                'min_duration': self.min_duration,
                'similarity_threshold': self.similarity_threshold
            }
        }