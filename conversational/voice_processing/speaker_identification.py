"""
Speaker Identification Module - IA Influencer Agent

Advanced speaker identification, verification, and voice biometrics system
for voice authentication, content protection, and speaker analytics.

Features:
- Real-time speaker identification and verification
- Voice biometric analysis and profiling
- Multi-speaker detection and separation
- Speaker enrollment and training
- Voice signature extraction
- Anti-spoofing detection
- Speaker clustering and analytics

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
import time
import json
import hashlib
from pathlib import Path

from .config import SpeakerConfig, ModelConfiguration
from .models import SpeakerProfile, VoiceGender

logger = logging.getLogger(__name__)

@dataclass
class SpeakerEmbedding:
    """Speaker voice embedding representation"""
    speaker_id: str
    embedding_vector: np.ndarray
    confidence_score: float
    extraction_timestamp: str
    audio_duration: float
    quality_score: float

@dataclass
class IdentificationResult:
    """Speaker identification result"""
    identified_speaker: Optional[SpeakerProfile]
    confidence_score: float
    similarity_scores: Dict[str, float]
    verification_status: str  # verified, rejected, unknown
    processing_time: float
    embedding: Optional[SpeakerEmbedding] = None

@dataclass
class VerificationResult:
    """Speaker verification result"""
    is_verified: bool
    confidence_score: float
    threshold_used: float
    decision_score: float
    processing_time: float
    anti_spoofing_score: float

class SpeakerIdentifier:
    """
    Advanced speaker identification and verification system
    
    Capabilities:
    - Real-time speaker identification from voice samples
    - Speaker verification against enrolled profiles
    - Voice biometric feature extraction
    - Multi-speaker detection and clustering
    - Anti-spoofing and liveness detection
    - Speaker analytics and profiling
    """
    
    def __init__(self, config: SpeakerConfig):
        """Initialize speaker identifier"""
        self.config = config
        self.is_initialized = False
        
        # Models and processors
        self.identification_model = None
        self.embedding_extractor = None
        self.anti_spoofing_detector = None
        
        # Speaker database
        self.enrolled_speakers: Dict[str, SpeakerProfile] = {}
        self.speaker_embeddings: Dict[str, List[SpeakerEmbedding]] = {}
        
        # Processing cache
        self.embedding_cache: Dict[str, SpeakerEmbedding] = {}
        self.identification_cache: Dict[str, IdentificationResult] = {}
        
        # Performance metrics
        self.identification_stats = {
            "total_identifications": 0,
            "successful_identifications": 0,
            "verification_attempts": 0,
            "successful_verifications": 0,
            "false_acceptance_rate": 0.0,
            "false_rejection_rate": 0.0,
            "average_processing_time": 0.0
        }
        
        logger.info("SpeakerIdentifier initialized")
    
    async def initialize(self) -> bool:
        """Initialize speaker identification components"""
        try:
            logger.info("Initializing speaker identification system...")
            
            # Initialize identification model
            await self._initialize_identification_model()
            
            # Initialize embedding extractor
            await self._initialize_embedding_extractor()
            
            # Initialize anti-spoofing detector
            await self._initialize_anti_spoofing_detector()
            
            # Load enrolled speakers
            await self._load_enrolled_speakers()
            
            # Warm up models
            await self._warm_up_models()
            
            self.is_initialized = True
            logger.info("Speaker identification system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize speaker identifier: {e}")
            return False
    
    async def _initialize_identification_model(self) -> None:
        """Initialize speaker identification model"""
        try:
            # Mock implementation - in real system would load actual model
            self.identification_model = {
                "provider": self.config.identification_model.provider.value,
                "model_name": self.config.identification_model.model_name,
                "embedding_dim": self.config.embedding_dimension,
                "loaded": True,
                "capabilities": {
                    "identification": True,
                    "verification": True,
                    "clustering": True,
                    "real_time": True
                }
            }
            logger.info("Speaker identification model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize identification model: {e}")
            raise
    
    async def _initialize_embedding_extractor(self) -> None:
        """Initialize voice embedding extractor"""
        try:
            # Mock implementation
            self.embedding_extractor = {
                "frame_length": self.config.frame_length,
                "frame_shift": self.config.frame_shift,
                "embedding_dim": self.config.embedding_dimension,
                "loaded": True
            }
            logger.info("Voice embedding extractor initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding extractor: {e}")
            raise
    
    async def _initialize_anti_spoofing_detector(self) -> None:
        """Initialize anti-spoofing detection system"""
        try:
            # Mock implementation
            self.anti_spoofing_detector = {
                "algorithms": ["spectral_analysis", "liveness_detection", "replay_detection"],
                "loaded": True
            }
            logger.info("Anti-spoofing detector initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize anti-spoofing detector: {e}")
    
    async def _load_enrolled_speakers(self) -> None:
        """Load enrolled speaker profiles"""
        try:
            # Mock enrolled speakers for demonstration
            demo_speakers = [
                SpeakerProfile(
                    speaker_id="speaker_001",
                    name="Demo User 1",
                    gender=VoiceGender.FEMALE,
                    age_range=(25, 35),
                    language="en-US",
                    confidence_score=0.95,
                    sample_count=5
                ),
                SpeakerProfile(
                    speaker_id="speaker_002",
                    name="Demo User 2",
                    gender=VoiceGender.MALE,
                    age_range=(30, 40),
                    language="en-US",
                    confidence_score=0.92,
                    sample_count=3
                )
            ]
            
            for speaker in demo_speakers:
                self.enrolled_speakers[speaker.speaker_id] = speaker
                # Initialize empty embeddings list
                self.speaker_embeddings[speaker.speaker_id] = []
            
            logger.info(f"Loaded {len(self.enrolled_speakers)} enrolled speakers")
            
        except Exception as e:
            logger.error(f"Failed to load enrolled speakers: {e}")
    
    async def _warm_up_models(self) -> None:
        """Warm up identification models"""
        try:
            # Generate dummy audio for warm-up
            dummy_audio = np.random.randn(16000).astype(np.float32)  # 1 second at 16kHz
            
            # Warm up embedding extraction
            await self._extract_embedding_internal(dummy_audio, 16000, is_warmup=True)
            
            logger.info("Speaker identification models warmed up")
            
        except Exception as e:
            logger.warning(f"Model warm-up failed: {e}")
    
    async def warm_up(self, audio_data: np.ndarray) -> None:
        """Public warm-up method"""
        await self._warm_up_models()
    
    async def identify_speaker(self,
                             audio_data: np.ndarray,
                             sample_rate: int = 16000,
                             reference_profiles: Optional[List[str]] = None,
                             confidence_threshold: float = None) -> IdentificationResult:
        """
        Identify speaker from voice sample
        
        Args:
            audio_data: Audio samples for identification
            sample_rate: Sample rate of audio
            reference_profiles: Optional list of speaker IDs to compare against
            confidence_threshold: Minimum confidence for positive identification
            
        Returns:
            IdentificationResult with speaker information
        """
        if not self.is_initialized:
            raise RuntimeError("Speaker identifier not initialized")
        
        start_time = time.time()
        confidence_threshold = confidence_threshold or self.config.verification_threshold
        
        try:
            logger.info("Starting speaker identification...")
            
            # Validate audio input
            audio_data = self._validate_audio_input(audio_data, sample_rate)
            
            # Extract speaker embedding
            embedding = await self._extract_embedding_internal(audio_data, sample_rate)
            
            # Compare against enrolled speakers
            similarity_scores = await self._compare_embeddings(
                embedding, reference_profiles
            )
            
            # Find best match
            identified_speaker = None
            best_score = 0.0
            verification_status = "unknown"
            
            if similarity_scores:
                best_speaker_id = max(similarity_scores.keys(), key=lambda k: similarity_scores[k])
                best_score = similarity_scores[best_speaker_id]
                
                if best_score >= confidence_threshold:
                    identified_speaker = self.enrolled_speakers.get(best_speaker_id)
                    verification_status = "verified"
                else:
                    verification_status = "rejected"
            
            # Create result
            processing_time = time.time() - start_time
            result = IdentificationResult(
                identified_speaker=identified_speaker,
                confidence_score=best_score,
                similarity_scores=similarity_scores,
                verification_status=verification_status,
                processing_time=processing_time,
                embedding=embedding
            )
            
            # Update statistics
            self._update_identification_stats(result)
            
            logger.info(f"Speaker identification completed in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"Speaker identification failed: {e}")
            raise
    
    async def verify_speaker(self,
                           audio_data: np.ndarray,
                           claimed_speaker_id: str,
                           sample_rate: int = 16000,
                           threshold: float = None) -> VerificationResult:
        """
        Verify if audio matches claimed speaker identity
        
        Args:
            audio_data: Audio samples for verification
            claimed_speaker_id: Claimed speaker identity
            sample_rate: Sample rate of audio
            threshold: Verification threshold
            
        Returns:
            VerificationResult with verification decision
        """
        start_time = time.time()
        threshold = threshold or self.config.verification_threshold
        
        try:
            logger.info(f"Verifying speaker: {claimed_speaker_id}")
            
            # Check if speaker is enrolled
            if claimed_speaker_id not in self.enrolled_speakers:
                raise ValueError(f"Speaker not enrolled: {claimed_speaker_id}")
            
            # Extract embedding from test audio
            test_embedding = await self._extract_embedding_internal(audio_data, sample_rate)
            
            # Get reference embeddings for claimed speaker
            reference_embeddings = self.speaker_embeddings.get(claimed_speaker_id, [])
            if not reference_embeddings:
                # Generate a mock reference embedding
                reference_embeddings = [await self._generate_mock_reference_embedding(claimed_speaker_id)]
            
            # Calculate similarity scores
            similarities = []
            for ref_embedding in reference_embeddings:
                similarity = self._calculate_embedding_similarity(
                    test_embedding.embedding_vector,
                    ref_embedding.embedding_vector
                )
                similarities.append(similarity)
            
            # Decision based on maximum similarity
            decision_score = max(similarities) if similarities else 0.0
            is_verified = decision_score >= threshold
            
            # Anti-spoofing check
            anti_spoofing_score = await self._detect_spoofing(audio_data, sample_rate)
            if anti_spoofing_score < 0.5:  # Low anti-spoofing score indicates potential spoofing
                is_verified = False
            
            processing_time = time.time() - start_time
            
            result = VerificationResult(
                is_verified=is_verified,
                confidence_score=decision_score,
                threshold_used=threshold,
                decision_score=decision_score,
                processing_time=processing_time,
                anti_spoofing_score=anti_spoofing_score
            )
            
            # Update statistics
            self._update_verification_stats(result)
            
            logger.info(f"Speaker verification completed: {is_verified} (score: {decision_score:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Speaker verification failed: {e}")
            raise
    
    async def enroll_speaker(self,
                           speaker_id: str,
                           audio_samples: List[np.ndarray],
                           speaker_info: Dict[str, Any],
                           sample_rate: int = 16000) -> SpeakerProfile:
        """
        Enroll a new speaker with multiple audio samples
        
        Args:
            speaker_id: Unique speaker identifier
            audio_samples: List of audio samples for enrollment
            speaker_info: Speaker metadata (name, gender, etc.)
            sample_rate: Sample rate of audio samples
            
        Returns:
            SpeakerProfile of enrolled speaker
        """
        try:
            logger.info(f"Enrolling speaker: {speaker_id}")
            
            if speaker_id in self.enrolled_speakers:
                raise ValueError(f"Speaker already enrolled: {speaker_id}")
            
            # Extract embeddings from all samples
            embeddings = []
            for i, audio in enumerate(audio_samples):
                embedding = await self._extract_embedding_internal(audio, sample_rate)
                embedding.speaker_id = speaker_id
                embeddings.append(embedding)
            
            # Calculate average embedding quality
            avg_quality = np.mean([emb.quality_score for emb in embeddings])
            
            # Analyze voice characteristics
            characteristics = await self._analyze_speaker_characteristics(audio_samples[0], sample_rate)
            
            # Create speaker profile
            speaker_profile = SpeakerProfile(
                speaker_id=speaker_id,
                name=speaker_info.get("name", f"Speaker {speaker_id}"),
                gender=VoiceGender(speaker_info.get("gender", "unknown")),
                age_range=speaker_info.get("age_range"),
                accent=speaker_info.get("accent"),
                language=speaker_info.get("language", "en-US"),
                confidence_score=avg_quality,
                sample_count=len(audio_samples),
                voice_characteristics=characteristics
            )
            
            # Store speaker and embeddings
            self.enrolled_speakers[speaker_id] = speaker_profile
            self.speaker_embeddings[speaker_id] = embeddings
            
            logger.info(f"Speaker enrolled successfully: {speaker_id}")
            return speaker_profile
            
        except Exception as e:
            logger.error(f"Speaker enrollment failed: {e}")
            raise
    
    async def _extract_embedding_internal(self,
                                        audio_data: np.ndarray,
                                        sample_rate: int,
                                        is_warmup: bool = False) -> SpeakerEmbedding:
        """Extract speaker embedding from audio"""
        try:
            # Preprocess audio
            audio_data = self._preprocess_audio(audio_data, sample_rate)
            
            # Mock embedding extraction - in real system would use actual model
            if is_warmup:
                # Minimal embedding for warm-up
                embedding_vector = np.random.randn(64).astype(np.float32)
            else:
                # Generate realistic speaker embedding
                embedding_vector = self._generate_mock_embedding(audio_data, sample_rate)
            
            # Calculate quality score
            quality_score = self._calculate_embedding_quality(audio_data, embedding_vector)
            
            return SpeakerEmbedding(
                speaker_id="unknown",
                embedding_vector=embedding_vector,
                confidence_score=quality_score,
                extraction_timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                audio_duration=len(audio_data) / sample_rate,
                quality_score=quality_score
            )
            
        except Exception as e:
            logger.error(f"Embedding extraction failed: {e}")
            raise
    
    def _generate_mock_embedding(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Generate mock speaker embedding for demonstration"""
        # Use simple spectral features as mock embedding
        # In real implementation would use trained neural network
        
        # Calculate spectral features
        fft = np.fft.fft(audio_data)
        magnitude = np.abs(fft)
        
        # Take log magnitude spectrum
        log_magnitude = np.log(magnitude + 1e-10)
        
        # Downsample to embedding dimension
        target_dim = self.config.embedding_dimension
        if len(log_magnitude) > target_dim:
            # Downsample
            step = len(log_magnitude) // target_dim
            embedding = log_magnitude[::step][:target_dim]
        else:
            # Pad with zeros
            embedding = np.pad(log_magnitude, (0, target_dim - len(log_magnitude)))
        
        # Normalize
        embedding = (embedding - np.mean(embedding)) / (np.std(embedding) + 1e-10)
        
        return embedding.astype(np.float32)
    
    async def _compare_embeddings(self,
                                test_embedding: SpeakerEmbedding,
                                reference_speakers: Optional[List[str]]) -> Dict[str, float]:
        """Compare test embedding against enrolled speakers"""
        try:
            similarity_scores = {}
            
            # Determine which speakers to compare against
            speakers_to_compare = reference_speakers or list(self.enrolled_speakers.keys())
            
            for speaker_id in speakers_to_compare:
                if speaker_id not in self.speaker_embeddings:
                    continue
                
                # Get reference embeddings for this speaker
                reference_embeddings = self.speaker_embeddings[speaker_id]
                if not reference_embeddings:
                    continue
                
                # Calculate similarities against all reference embeddings
                similarities = []
                for ref_embedding in reference_embeddings:
                    similarity = self._calculate_embedding_similarity(
                        test_embedding.embedding_vector,
                        ref_embedding.embedding_vector
                    )
                    similarities.append(similarity)
                
                # Use maximum similarity
                similarity_scores[speaker_id] = max(similarities) if similarities else 0.0
            
            return similarity_scores
            
        except Exception as e:
            logger.error(f"Embedding comparison failed: {e}")
            return {}
    
    def _calculate_embedding_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate similarity between two embeddings"""
        try:
            # Cosine similarity
            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            
            # Convert to positive range [0, 1]
            similarity = (similarity + 1) / 2
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    async def _detect_spoofing(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Detect potential voice spoofing"""
        try:
            # Mock anti-spoofing detection
            # In real implementation would use sophisticated spoofing detection
            
            # Simple heuristics for demonstration
            scores = []
            
            # Check spectral consistency
            fft = np.fft.fft(audio_data)
            magnitude = np.abs(fft)
            spectral_score = 1.0 - min(1.0, np.std(magnitude) / (np.mean(magnitude) + 1e-10))
            scores.append(spectral_score)
            
            # Check temporal consistency
            frame_size = sample_rate // 10  # 100ms frames
            frame_energies = []
            for i in range(0, len(audio_data) - frame_size, frame_size):
                frame = audio_data[i:i + frame_size]
                energy = np.sum(frame ** 2)
                frame_energies.append(energy)
            
            if frame_energies:
                temporal_score = 1.0 - min(1.0, np.std(frame_energies) / (np.mean(frame_energies) + 1e-10))
                scores.append(temporal_score)
            
            # Return average score
            return np.mean(scores) if scores else 0.5
            
        except Exception as e:
            logger.warning(f"Anti-spoofing detection failed: {e}")
            return 0.5  # Neutral score
    
    def _preprocess_audio(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Preprocess audio for speaker identification"""
        # Ensure minimum duration
        min_samples = int(self.config.min_audio_duration * sample_rate)
        if len(audio_data) < min_samples:
            # Pad with zeros
            audio_data = np.pad(audio_data, (0, min_samples - len(audio_data)))
        
        # Simple preprocessing
        # In real implementation would include voice activity detection,
        # noise reduction, normalization, etc.
        
        # Normalize amplitude
        max_amp = np.max(np.abs(audio_data))
        if max_amp > 0:
            audio_data = audio_data / max_amp
        
        return audio_data
    
    def _validate_audio_input(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Validate audio input"""
        if not isinstance(audio_data, np.ndarray):
            raise ValueError("Audio data must be numpy array")
        
        if len(audio_data) == 0:
            raise ValueError("Audio data cannot be empty")
        
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        
        # Check minimum duration
        duration = len(audio_data) / sample_rate
        if duration < self.config.min_audio_duration:
            logger.warning(f"Audio duration ({duration:.2f}s) below minimum ({self.config.min_audio_duration}s)")
        
        return audio_data.astype(np.float32)
    
    def _calculate_embedding_quality(self, audio_data: np.ndarray, embedding: np.ndarray) -> float:
        """Calculate quality score for embedding"""
        try:
            # Mock quality calculation
            # In real implementation would use sophisticated quality metrics
            
            # Check audio signal quality
            rms = np.sqrt(np.mean(audio_data ** 2))
            snr_estimate = rms / (np.std(audio_data) + 1e-10)
            
            # Check embedding characteristics
            embedding_norm = np.linalg.norm(embedding)
            embedding_std = np.std(embedding)
            
            # Combine factors
            quality_score = min(1.0, (snr_estimate + embedding_norm + embedding_std) / 3.0)
            
            return max(0.0, min(1.0, quality_score))
            
        except Exception:
            return 0.7  # Default quality score
    
    async def _analyze_speaker_characteristics(self,
                                             audio_data: np.ndarray,
                                             sample_rate: int) -> Dict[str, float]:
        """Analyze speaker voice characteristics"""
        try:
            characteristics = {}
            
            # Fundamental frequency analysis
            # Simple autocorrelation-based pitch detection
            autocorr = np.correlate(audio_data, audio_data, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            
            # Find peak in expected F0 range (80-400 Hz)
            min_period = int(sample_rate / 400)  # Max F0
            max_period = int(sample_rate / 80)   # Min F0
            
            if max_period < len(autocorr):
                peak_idx = np.argmax(autocorr[min_period:max_period]) + min_period
                f0 = sample_rate / peak_idx
                characteristics["fundamental_frequency"] = f0
            
            # Spectral characteristics
            fft = np.fft.fft(audio_data)
            magnitude = np.abs(fft)
            freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
            
            # Find formant-like peaks (simplified)
            positive_freqs = freqs[:len(freqs)//2]
            positive_magnitude = magnitude[:len(magnitude)//2]
            
            # Look for peaks in formant ranges
            formant_ranges = [(300, 1000), (900, 2500), (1500, 3500)]
            for i, (f_min, f_max) in enumerate(formant_ranges):
                range_mask = (positive_freqs >= f_min) & (positive_freqs <= f_max)
                if np.any(range_mask):
                    range_magnitudes = positive_magnitude[range_mask]
                    range_freqs = positive_freqs[range_mask]
                    peak_idx = np.argmax(range_magnitudes)
                    formant_freq = range_freqs[peak_idx]
                    characteristics[f"formant_{i+1}"] = formant_freq
            
            return characteristics
            
        except Exception as e:
            logger.warning(f"Speaker characteristics analysis failed: {e}")
            return {}
    
    async def _generate_mock_reference_embedding(self, speaker_id: str) -> SpeakerEmbedding:
        """Generate mock reference embedding for enrolled speaker"""
        # Generate consistent embedding based on speaker ID
        np.random.seed(hash(speaker_id) % 2**32)
        embedding_vector = np.random.randn(self.config.embedding_dimension).astype(np.float32)
        
        return SpeakerEmbedding(
            speaker_id=speaker_id,
            embedding_vector=embedding_vector,
            confidence_score=0.9,
            extraction_timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            audio_duration=5.0,
            quality_score=0.9
        )
    
    def _update_identification_stats(self, result: IdentificationResult) -> None:
        """Update identification statistics"""
        try:
            self.identification_stats["total_identifications"] += 1
            
            if result.verification_status == "verified":
                self.identification_stats["successful_identifications"] += 1
            
            # Update average processing time
            current_avg = self.identification_stats["average_processing_time"]
            total_count = self.identification_stats["total_identifications"]
            new_avg = (current_avg * (total_count - 1) + result.processing_time) / total_count
            self.identification_stats["average_processing_time"] = new_avg
            
        except Exception as e:
            logger.warning(f"Failed to update identification stats: {e}")
    
    def _update_verification_stats(self, result: VerificationResult) -> None:
        """Update verification statistics"""
        try:
            self.identification_stats["verification_attempts"] += 1
            
            if result.is_verified:
                self.identification_stats["successful_verifications"] += 1
                
        except Exception as e:
            logger.warning(f"Failed to update verification stats: {e}")
    
    def get_enrolled_speakers(self) -> List[Dict[str, Any]]:
        """Get list of enrolled speakers"""
        return [
            {
                "speaker_id": profile.speaker_id,
                "name": profile.name,
                "gender": profile.gender.value,
                "language": profile.language,
                "confidence_score": profile.confidence_score,
                "sample_count": profile.sample_count,
                "created_at": profile.created_at.isoformat() if profile.created_at else None
            }
            for profile in self.enrolled_speakers.values()
        ]
    
    def get_identification_statistics(self) -> Dict[str, Any]:
        """Get identification performance statistics"""
        stats = self.identification_stats.copy()
        stats["enrolled_speakers"] = len(self.enrolled_speakers)
        stats["total_embeddings"] = sum(len(embeddings) for embeddings in self.speaker_embeddings.values())
        return stats
    
    async def shutdown(self) -> None:
        """Shutdown speaker identifier"""
        try:
            logger.info("Shutting down speaker identifier...")
            
            # Clear caches and data
            self.embedding_cache.clear()
            self.identification_cache.clear()
            
            # Reset state
            self.is_initialized = False
            
            logger.info("Speaker identifier shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during speaker identifier shutdown: {e}")

# Support classes
class VoiceBiometrics:
    """Voice biometric analysis utilities"""
    def __init__(self, identifier: SpeakerIdentifier):
        self.identifier = identifier
    
    async def extract_biometric_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Extract biometric features from voice"""
        embedding = await self.identifier._extract_embedding_internal(audio_data, sample_rate)
        characteristics = await self.identifier._analyze_speaker_characteristics(audio_data, sample_rate)
        return characteristics

class SpeakerVerifier:
    """Speaker verification utilities"""
    def __init__(self, identifier: SpeakerIdentifier):
        self.identifier = identifier
    
    async def batch_verify(self, audio_samples: List[np.ndarray], speaker_id: str) -> List[VerificationResult]:
        """Verify multiple audio samples"""
        results = []
        for audio in audio_samples:
            result = await self.identifier.verify_speaker(audio, speaker_id)
            results.append(result)
        return results

class VoiceSignatureExtractor:
    """Voice signature extraction utilities"""
    def __init__(self, identifier: SpeakerIdentifier):
        self.identifier = identifier
    
    async def extract_signature(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract unique voice signature"""
        embedding = await self.identifier._extract_embedding_internal(audio_data, sample_rate)
        return {
            "embedding": embedding.embedding_vector,
            "confidence": embedding.confidence_score,
            "signature_hash": hashlib.md5(embedding.embedding_vector.tobytes()).hexdigest()
        }

class IdentityValidator:
    """Identity validation utilities"""
    def __init__(self, identifier: SpeakerIdentifier):
        self.identifier = identifier
    
    async def validate_identity(self, audio_data: np.ndarray, claimed_identity: str) -> bool:
        """Validate claimed identity against voice"""
        result = await self.identifier.verify_speaker(audio_data, claimed_identity)
        return result.is_verified and result.anti_spoofing_score > 0.7
