"""
Emotion Detection Module - IA Influencer Agent

Advanced emotion detection and sentiment analysis from voice for content creators,
enabling emotional intelligence in conversational AI and content optimization.

Features:
- Real-time emotion detection from voice
- Multi-dimensional emotion analysis (arousal, valence, dominance)
- Temporal emotion tracking and transition analysis
- Cultural and linguistic emotion adaptation
- Emotion-based content recommendation
- Professional emotion analytics for creators

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
import time
from datetime import datetime

from .config import EmotionConfig, ModelConfiguration
from .models import EmotionAnalysisResult, EmotionType

logger = logging.getLogger(__name__)

@dataclass
class EmotionFeatures:
    """Voice emotion features"""
    prosodic_features: Dict[str, float]
    spectral_features: Dict[str, float]
    temporal_features: Dict[str, float]
    linguistic_features: Dict[str, float]

@dataclass
class EmotionFrame:
    """Single frame emotion analysis"""
    timestamp: float
    emotion: EmotionType
    confidence: float
    arousal: float
    valence: float
    intensity: float

class EmotionDetector:
    """
    Advanced emotion detection and analysis system for voice content
    
    Capabilities:
    - Real-time emotion detection from voice samples
    - Multi-dimensional emotion analysis (arousal, valence, dominance)
    - Temporal emotion tracking and change detection
    - Emotion intensity and stability measurement
    - Cultural and contextual emotion adaptation
    - Professional emotion analytics for content optimization
    """
    
    def __init__(self, config: EmotionConfig):
        """Initialize emotion detector"""
        self.config = config
        self.is_initialized = False
        
        # Models and processors
        self.emotion_model = None
        self.feature_extractor = None
        self.temporal_analyzer = None
        
        # Emotion processing
        self.emotion_history: List[EmotionFrame] = []
        self.processing_cache: Dict[str, EmotionAnalysisResult] = {}
        
        # Performance metrics
        self.detection_stats = {
            "total_detections": 0,
            "processing_times": [],
            "confidence_scores": [],
            "emotion_distribution": {emotion.value: 0 for emotion in EmotionType}
        }
        
        logger.info("EmotionDetector initialized")
    
    async def initialize(self) -> bool:
        """Initialize emotion detection components"""



        try:
            logger.info("Initializing emotion detection system...")
            
            # Initialize emotion model
            await self._initialize_emotion_model()
            
            # Initialize feature extractor
            await self._initialize_feature_extractor()
            
            # Initialize temporal analyzer
            await self._initialize_temporal_analyzer()
            
            # Warm up models
            await self._warm_up_models()
            
            self.is_initialized = True
            logger.info("Emotion detection system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize emotion detector: {e}")
            return False
    
    async def _initialize_emotion_model(self) -> None:
        """Initialize emotion detection model"""



        try:
            # Mock implementation - in real system would load actual model
            self.emotion_model = {
                "provider": self.config.emotion_model.provider.value,
                "model_name": self.config.emotion_model.model_name,
                "emotion_categories": self.config.emotion_categories,
                "loaded": True,
                "capabilities": {
                    "basic_emotions": True,
                    "arousal_valence": self.config.enable_arousal_valence,
                    "temporal_analysis": self.config.enable_temporal_analysis,
                    "real_time": True
                }
            }
            logger.info("Emotion detection model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize emotion model: {e}")
            raise
    
    async def _initialize_feature_extractor(self) -> None:
        """Initialize voice feature extractor for emotion analysis"""



        try:
            # Mock implementation
            self.feature_extractor = {
                "prosodic_features": ["pitch", "intensity", "tempo", "rhythm"],
                "spectral_features": ["mfcc", "spectral_centroid", "spectral_rolloff", "chroma"],
                "temporal_features": ["energy_contour", "zero_crossing_rate", "duration_patterns"],
                "frame_duration": self.config.frame_duration,
                "overlap_duration": self.config.overlap_duration,
                "loaded": True
            }
            logger.info("Voice feature extractor initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize feature extractor: {e}")
            raise
    
    async def _initialize_temporal_analyzer(self) -> None:
        """Initialize temporal emotion analysis"""



        try:
            # Mock implementation
            self.temporal_analyzer = {
                "smoothing_window": self.config.smoothing_window,
                "transition_detection": True,
                "stability_analysis": True,
                "loaded": True
            }
            logger.info("Temporal emotion analyzer initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize temporal analyzer: {e}")
    
    async def _warm_up_models(self) -> None:
        """Warm up emotion detection models"""



        try:
            # Generate dummy audio for warm-up
            dummy_audio = np.random.randn(8000).astype(np.float32)  # 0.5 second at 16kHz
            
            # Warm up emotion detection
            await self._detect_emotion_internal(dummy_audio, 16000, is_warmup=True)
            
            logger.info("Emotion detection models warmed up")
            
        except Exception as e:
            logger.warning(f"Model warm-up failed: {e}")
    
    async def warm_up(self, audio_data: np.ndarray) -> None:
        """Public warm-up method"""
        await self._warm_up_models()
    
    async def detect_emotion(self,
                           audio_data: np.ndarray,
                           sample_rate: int = 16000,
                           granularity: str = "basic",
                           include_confidence: bool = True,
                           enable_temporal: bool = True) -> EmotionAnalysisResult:
        """
        Detect emotions from voice audio
        
        Args:
            audio_data: Audio samples for emotion detection
            sample_rate: Sample rate of audio
            granularity: Analysis granularity ("basic", "detailed", "micro")
            include_confidence: Include confidence scores for all emotions
            enable_temporal: Enable temporal emotion analysis
            
        Returns:
            EmotionAnalysisResult with comprehensive emotion analysis
        """
        if not self.is_initialized:
            raise RuntimeError("Emotion detector not initialized")
        
        start_time = time.time()
        
        try:
            logger.info("Starting emotion detection...")
            
            # Validate audio input
            audio_data = self._validate_audio_input(audio_data, sample_rate)
            
            # Extract emotion features
            features = await self._extract_emotion_features(audio_data, sample_rate)
            
            # Detect primary emotion
            primary_emotion, confidence_score = await self._classify_emotion(features)
            
            # Get emotion scores for all categories
            emotion_scores = await self._get_emotion_scores(features) if include_confidence else {}
            
            # Calculate arousal and valence
            arousal, valence = await self._calculate_arousal_valence(features)
            
            # Calculate emotion intensity
            intensity = await self._calculate_emotion_intensity(features)
            
            # Temporal analysis
            emotion_timeline = []
            emotional_stability = 0.0
            emotion_transitions = []
            
            if enable_temporal and self.config.enable_temporal_analysis:
                temporal_results = await self._analyze_temporal_emotions(
                    audio_data, sample_rate, features
                )
                emotion_timeline = temporal_results.get("timeline", [])
                emotional_stability = temporal_results.get("stability", 0.0)
                emotion_transitions = temporal_results.get("transitions", [])
            
            # Create result
            processing_time = time.time() - start_time
            result = EmotionAnalysisResult(
                primary_emotion=primary_emotion,
                confidence_score=confidence_score,
                emotion_scores=emotion_scores,
                arousal_level=arousal,
                valence_level=valence,
                intensity=intensity,
                emotion_timeline=emotion_timeline,
                emotional_stability=emotional_stability,
                emotion_transitions=emotion_transitions,
                analysis_duration=processing_time
            )
            
            # Update statistics
            self._update_detection_stats(result, processing_time)
            
            logger.info(f"Emotion detection completed: {primary_emotion.value} ({confidence_score:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Emotion detection failed: {e}")
            raise
    
    async def _detect_emotion_internal(self,
                                     audio_data: np.ndarray,
                                     sample_rate: int,
                                     is_warmup: bool = False) -> Tuple[EmotionType, float]:
        """Internal emotion detection implementation"""



        try:
            if is_warmup:
                # Return minimal result for warm-up
                return EmotionType.NEUTRAL, 0.8
            
            # Extract features
            features = await self._extract_emotion_features(audio_data, sample_rate)
            
            # Classify emotion
            return await self._classify_emotion(features)
            
        except Exception as e:
            logger.error(f"Internal emotion detection failed: {e}")
            return EmotionType.NEUTRAL, 0.0
    
    async def _extract_emotion_features(self,
                                      audio_data: np.ndarray,
                                      sample_rate: int) -> EmotionFeatures:
        """Extract emotion-relevant features from audio"""



        try:
            # Prosodic features
            prosodic_features = self._extract_prosodic_features(audio_data, sample_rate)
            
            # Spectral features
            spectral_features = self._extract_spectral_features(audio_data, sample_rate)
            
            # Temporal features
            temporal_features = self._extract_temporal_features(audio_data, sample_rate)
            
            # Linguistic features (placeholder for text analysis)
            linguistic_features = {}
            
            return EmotionFeatures(
                prosodic_features=prosodic_features,
                spectral_features=spectral_features,
                temporal_features=temporal_features,
                linguistic_features=linguistic_features
            )
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            raise
    
    def _extract_prosodic_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Extract prosodic features (pitch, intensity, rhythm)"""



        try:
            features = {}
            
            # Fundamental frequency (pitch) analysis
            f0_contour = self._estimate_f0_contour(audio_data, sample_rate)
            if len(f0_contour) > 0:
                features["pitch_mean"] = np.mean(f0_contour)
                features["pitch_std"] = np.std(f0_contour)
                features["pitch_range"] = np.max(f0_contour) - np.min(f0_contour)
                features["pitch_slope"] = np.polyfit(range(len(f0_contour)), f0_contour, 1)[0]
            
            # Intensity (energy) analysis
            frame_size = int(0.025 * sample_rate)  # 25ms frames
            hop_size = int(0.010 * sample_rate)    # 10ms hop
            
            intensities = []
            for i in range(0, len(audio_data) - frame_size, hop_size):
                frame = audio_data[i:i + frame_size]
                intensity = np.sum(frame ** 2)
                intensities.append(intensity)
            
            if intensities:
                features["intensity_mean"] = np.mean(intensities)
                features["intensity_std"] = np.std(intensities)
                features["intensity_range"] = np.max(intensities) - np.min(intensities)
            
            # Speaking rate (simplified)
            features["speaking_rate"] = len(intensities) / (len(audio_data) / sample_rate)
            
            return features
            
        except Exception as e:
            logger.warning(f"Prosodic feature extraction failed: {e}")
            return {}
    
    def _extract_spectral_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Extract spectral features"""



        try:
            features = {}
            
            # FFT analysis
            fft = np.fft.fft(audio_data)
            magnitude = np.abs(fft)
            freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
            
            # Spectral centroid
            positive_freqs = freqs[:len(freqs)//2]
            positive_magnitude = magnitude[:len(magnitude)//2]
            
            if np.sum(positive_magnitude) > 0:
                spectral_centroid = np.sum(positive_freqs * positive_magnitude) / np.sum(positive_magnitude)
                features["spectral_centroid"] = spectral_centroid
            
            # Spectral rolloff (85% of energy)
            cumulative_magnitude = np.cumsum(positive_magnitude)
            total_energy = cumulative_magnitude[-1]
            rolloff_threshold = 0.85 * total_energy
            rolloff_idx = np.where(cumulative_magnitude >= rolloff_threshold)[0]
            if len(rolloff_idx) > 0:
                features["spectral_rolloff"] = positive_freqs[rolloff_idx[0]]
            
            # Spectral bandwidth
            if "spectral_centroid" in features:
                centroid = features["spectral_centroid"]
                bandwidth = np.sqrt(np.sum(((positive_freqs - centroid) ** 2) * positive_magnitude) / np.sum(positive_magnitude))
                features["spectral_bandwidth"] = bandwidth
            
            # Zero crossing rate
            zcr = np.sum(np.diff(np.sign(audio_data)) != 0) / len(audio_data)
            features["zero_crossing_rate"] = zcr
            
            return features
            
        except Exception as e:
            logger.warning(f"Spectral feature extraction failed: {e}")
            return {}
    
    def _extract_temporal_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Extract temporal features"""



        try:
            features = {}
            
            # Audio duration
            duration = len(audio_data) / sample_rate
            features["duration"] = duration
            
            # RMS energy over time
            frame_size = int(0.025 * sample_rate)
            hop_size = int(0.010 * sample_rate)
            
            rms_values = []
            for i in range(0, len(audio_data) - frame_size, hop_size):
                frame = audio_data[i:i + frame_size]
                rms = np.sqrt(np.mean(frame ** 2))
                rms_values.append(rms)
            
            if rms_values:
                features["rms_mean"] = np.mean(rms_values)
                features["rms_std"] = np.std(rms_values)
                
                # Temporal dynamics
                features["energy_variation"] = np.std(rms_values) / (np.mean(rms_values) + 1e-10)
            
            # Pause detection (simplified)
            silence_threshold = 0.01
            silence_frames = np.sum(np.array(rms_values) < silence_threshold)
            features["silence_ratio"] = silence_frames / len(rms_values) if rms_values else 0.0
            
            return features
            
        except Exception as e:
            logger.warning(f"Temporal feature extraction failed: {e}")
            return {}
    
    def _estimate_f0_contour(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Estimate fundamental frequency contour"""



        try:
            # Simple autocorrelation-based pitch detection
            frame_size = int(0.025 * sample_rate)  # 25ms
            hop_size = int(0.010 * sample_rate)    # 10ms
            
            f0_contour = []
            
            for i in range(0, len(audio_data) - frame_size, hop_size):
                frame = audio_data[i:i + frame_size]
                
                # Autocorrelation
                autocorr = np.correlate(frame, frame, mode='full')
                autocorr = autocorr[len(autocorr)//2:]
                
                # Find peak in expected F0 range (80-400 Hz)
                min_period = int(sample_rate / 400)
                max_period = int(sample_rate / 80)
                
                if max_period < len(autocorr):
                    search_range = autocorr[min_period:max_period]
                    if len(search_range) > 0:
                        peak_idx = np.argmax(search_range) + min_period
                        f0 = sample_rate / peak_idx
                        f0_contour.append(f0)
                    else:
                        f0_contour.append(0.0)
                else:
                    f0_contour.append(0.0)
            
            return np.array(f0_contour)
            
        except Exception as e:
            logger.warning(f"F0 estimation failed: {e}")
            return np.array([])
    
    async def _classify_emotion(self, features: EmotionFeatures) -> Tuple[EmotionType, float]:
        """Classify emotion from features"""



        try:
            # Mock emotion classification - in real system would use trained model
            # Combine all features for classification
            all_features = {**features.prosodic_features, 
                          **features.spectral_features, 
                          **features.temporal_features}
            
            if not all_features:
                return EmotionType.NEUTRAL, 0.5
            
            # Simple rule-based classification for demonstration
            emotion_scores = {}
            
            # Pitch-based rules
            pitch_mean = all_features.get("pitch_mean", 150)
            pitch_std = all_features.get("pitch_std", 20)
            
            if pitch_mean > 200 and pitch_std > 30:
                emotion_scores[EmotionType.EXCITED] = 0.8
                emotion_scores[EmotionType.HAPPY] = 0.7
            elif pitch_mean < 120 and pitch_std < 15:
                emotion_scores[EmotionType.SAD] = 0.7
                emotion_scores[EmotionType.CALM] = 0.6
            elif pitch_std > 40:
                emotion_scores[EmotionType.ANGRY] = 0.8
                emotion_scores[EmotionType.STRESSED] = 0.7
            else:
                emotion_scores[EmotionType.NEUTRAL] = 0.6
            
            # Energy-based rules
            intensity_std = all_features.get("intensity_std", 0.1)
            energy_variation = all_features.get("energy_variation", 0.1)
            
            if intensity_std > 0.2 or energy_variation > 0.3:
                emotion_scores[EmotionType.EXCITED] = emotion_scores.get(EmotionType.EXCITED, 0.0) + 0.2
                emotion_scores[EmotionType.ANGRY] = emotion_scores.get(EmotionType.ANGRY, 0.0) + 0.2
            
            # Select emotion with highest score
            if emotion_scores:
                primary_emotion = max(emotion_scores.keys(), key=lambda k: emotion_scores[k])
                confidence = emotion_scores[primary_emotion]
            else:
                primary_emotion = EmotionType.NEUTRAL
                confidence = 0.5
            
            return primary_emotion, min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"Emotion classification failed: {e}")
            return EmotionType.NEUTRAL, 0.0
    
    async def _get_emotion_scores(self, features: EmotionFeatures) -> Dict[EmotionType, float]:
        """Get confidence scores for all emotion categories"""



        try:
            # Mock implementation - in real system would use model predictions
            primary_emotion, primary_confidence = await self._classify_emotion(features)
            
            scores = {}
            for emotion in EmotionType:
                if emotion == primary_emotion:
                    scores[emotion] = primary_confidence
                else:
                    # Assign lower random scores to other emotions
                    scores[emotion] = max(0.0, primary_confidence - 0.3 - np.random.random() * 0.4)
            
            return scores
            
        except Exception as e:
            logger.warning(f"Emotion scoring failed: {e}")
            return {}
    
    async def _calculate_arousal_valence(self, features: EmotionFeatures) -> Tuple[float, float]:
        """Calculate arousal and valence dimensions"""



        try:
            # Mock calculation - in real system would use dimensional emotion model
            all_features = {**features.prosodic_features, 
                          **features.spectral_features}
            
            # Arousal (activation level)
            pitch_std = all_features.get("pitch_std", 20)
            intensity_std = all_features.get("intensity_std", 0.1)
            speaking_rate = all_features.get("speaking_rate", 10)
            
            arousal = min(1.0, (pitch_std / 50.0 + intensity_std * 5.0 + speaking_rate / 20.0) / 3.0)
            
            # Valence (positive/negative)
            pitch_mean = all_features.get("pitch_mean", 150)
            spectral_centroid = all_features.get("spectral_centroid", 1000)
            
            # Higher pitch and spectral centroid often correlate with positive emotions
            valence_score = (pitch_mean / 300.0 + spectral_centroid / 2000.0) / 2.0
            valence = max(-1.0, min(1.0, valence_score * 2.0 - 1.0))  # Convert to [-1, 1] range
            
            return arousal, valence
            
        except Exception as e:
            logger.warning(f"Arousal/valence calculation failed: {e}")
            return 0.0, 0.0
    
    async def _calculate_emotion_intensity(self, features: EmotionFeatures) -> float:
        """Calculate emotion intensity"""



        try:
            # Combine multiple indicators of emotional intensity
            all_features = {**features.prosodic_features, 
                          **features.spectral_features, 
                          **features.temporal_features}
            
            intensity_indicators = []
            
            # Pitch variation intensity
            if "pitch_std" in all_features:
                pitch_intensity = min(1.0, all_features["pitch_std"] / 50.0)
                intensity_indicators.append(pitch_intensity)
            
            # Energy variation intensity
            if "energy_variation" in all_features:
                energy_intensity = min(1.0, all_features["energy_variation"])
                intensity_indicators.append(energy_intensity)
            
            # Spectral intensity
            if "spectral_bandwidth" in all_features:
                spectral_intensity = min(1.0, all_features["spectral_bandwidth"] / 2000.0)
                intensity_indicators.append(spectral_intensity)
            
            # Calculate overall intensity
            if intensity_indicators:
                intensity = np.mean(intensity_indicators)
            else:
                intensity = 0.5  # Default medium intensity
            
            return float(intensity)
            
        except Exception as e:
            logger.warning(f"Intensity calculation failed: {e}")
            return 0.5
    
    async def _analyze_temporal_emotions(self,
                                       audio_data: np.ndarray,
                                       sample_rate: int,
                                       global_features: EmotionFeatures) -> Dict[str, Any]:
        """Analyze emotions over time"""



        try:
            frame_duration = self.config.frame_duration
            overlap_duration = self.config.overlap_duration
            
            frame_samples = int(frame_duration * sample_rate)
            hop_samples = int((frame_duration - overlap_duration) * sample_rate)
            
            emotion_timeline = []
            emotion_sequence = []
            
            # Analyze emotions frame by frame
            for i in range(0, len(audio_data) - frame_samples, hop_samples):
                frame = audio_data[i:i + frame_samples]
                timestamp = i / sample_rate
                
                # Extract features for this frame
                frame_features = await self._extract_emotion_features(frame, sample_rate)
                
                # Classify emotion for this frame
                emotion, confidence = await self._classify_emotion(frame_features)
                
                # Calculate arousal and valence for this frame
                arousal, valence = await self._calculate_arousal_valence(frame_features)
                intensity = await self._calculate_emotion_intensity(frame_features)
                
                frame_result = EmotionFrame(
                    timestamp=timestamp,
                    emotion=emotion,
                    confidence=confidence,
                    arousal=arousal,
                    valence=valence,
                    intensity=intensity
                )
                
                emotion_timeline.append({
                    "timestamp": timestamp,
                    "emotion": emotion.value,
                    "confidence": confidence,
                    "arousal": arousal,
                    "valence": valence,
                    "intensity": intensity
                })
                
                emotion_sequence.append(emotion)
            
            # Calculate emotional stability
            if len(emotion_sequence) > 1:
                # Count emotion changes
                changes = sum(1 for i in range(1, len(emotion_sequence)) 
                            if emotion_sequence[i] != emotion_sequence[i-1])
                stability = 1.0 - (changes / (len(emotion_sequence) - 1))
            else:
                stability = 1.0
            
            # Detect emotion transitions
            transitions = []
            for i in range(1, len(emotion_sequence)):
                if emotion_sequence[i] != emotion_sequence[i-1]:
                    prev_emotion = emotion_sequence[i-1]
                    curr_emotion = emotion_sequence[i]
                    timestamp = emotion_timeline[i]["timestamp"]
                    confidence = emotion_timeline[i]["confidence"]
                    transitions.append((prev_emotion, curr_emotion, confidence))
            
            return {
                "timeline": emotion_timeline,
                "stability": stability,
                "transitions": transitions
            }
            
        except Exception as e:
            logger.warning(f"Temporal emotion analysis failed: {e}")
            return {"timeline": [], "stability": 0.0, "transitions": []}
    
    def _validate_audio_input(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Validate audio input for emotion detection"""
        if not isinstance(audio_data, np.ndarray):
            raise ValueError("Audio data must be numpy array")
        
        if len(audio_data) == 0:
            raise ValueError("Audio data cannot be empty")
        
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        
        # Ensure minimum duration for reliable emotion detection
        min_duration = 0.5  # 500ms minimum
        min_samples = int(min_duration * sample_rate)
        
        if len(audio_data) < min_samples:
            logger.warning(f"Audio too short for reliable emotion detection: {len(audio_data)/sample_rate:.2f}s")
        
        return audio_data.astype(np.float32)
    
    def _update_detection_stats(self, result: EmotionAnalysisResult, processing_time: float) -> None:
        """Update emotion detection statistics"""



        try:
            self.detection_stats["total_detections"] += 1
            self.detection_stats["processing_times"].append(processing_time)
            self.detection_stats["confidence_scores"].append(result.confidence_score)
            
            # Update emotion distribution
            emotion_key = result.primary_emotion.value
            self.detection_stats["emotion_distribution"][emotion_key] += 1
            
            # Keep only recent processing times (last 1000)
            if len(self.detection_stats["processing_times"]) > 1000:
                self.detection_stats["processing_times"] = self.detection_stats["processing_times"][-1000:]
            
            if len(self.detection_stats["confidence_scores"]) > 1000:
                self.detection_stats["confidence_scores"] = self.detection_stats["confidence_scores"][-1000:]
                
        except Exception as e:
            logger.warning(f"Failed to update detection stats: {e}")
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get emotion detection performance statistics"""
        stats = {}
        
        # Basic counts
        stats["total_detections"] = self.detection_stats["total_detections"]
        stats["emotion_distribution"] = self.detection_stats["emotion_distribution"].copy()
        
        # Processing performance
        processing_times = self.detection_stats["processing_times"]
        if processing_times:
            stats["average_processing_time"] = np.mean(processing_times)
            stats["median_processing_time"] = np.median(processing_times)
            stats["max_processing_time"] = np.max(processing_times)
        
        # Confidence metrics
        confidence_scores = self.detection_stats["confidence_scores"]
        if confidence_scores:
            stats["average_confidence"] = np.mean(confidence_scores)
            stats["confidence_std"] = np.std(confidence_scores)
        
        # Most common emotions
        emotion_counts = self.detection_stats["emotion_distribution"]
        if any(emotion_counts.values()):
            most_common = max(emotion_counts.keys(), key=lambda k: emotion_counts[k])
            stats["most_common_emotion"] = most_common
        
        return stats
    
    async def shutdown(self) -> None:
        """Shutdown emotion detector"""



        try:
            logger.info("Shutting down emotion detector...")
            
            # Clear caches and history
            self.processing_cache.clear()
            self.emotion_history.clear()
            
            # Reset state
            self.is_initialized = False
            
            logger.info("Emotion detector shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during emotion detector shutdown: {e}")

# Support classes
class VoiceEmotionAnalyzer:
    """Voice emotion analysis utilities"""
    def __init__(self, detector: EmotionDetector):
        self.detector = detector
    
    async def analyze_emotional_profile(self, audio_samples: List[np.ndarray]) -> Dict[str, float]:
        """Analyze emotional profile across multiple samples"""
        results = []
        for audio in audio_samples:
            result = await self.detector.detect_emotion(audio)
            results.append(result)
        
        # Aggregate results
        emotions = [r.primary_emotion for r in results]
        emotion_counts = {emotion.value: emotions.count(emotion) for emotion in EmotionType}
        total_count = len(results)
        
        return {emotion: count/total_count for emotion, count in emotion_counts.items()}

class SentimentProcessor:
    """Sentiment processing utilities"""
    def __init__(self, detector: EmotionDetector):
        self.detector = detector
    
    async def calculate_sentiment_score(self, audio_data: np.ndarray) -> float:
        """Calculate overall sentiment score (-1 to 1)"""
        result = await self.detector.detect_emotion(audio_data)
        return result.valence_level

class EmotionalStateClassifier:
    """Emotional state classification utilities"""
    def __init__(self, detector: EmotionDetector):
        self.detector = detector
    
    async def classify_emotional_state(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Classify comprehensive emotional state"""
        result = await self.detector.detect_emotion(audio_data)
        
        return {
            "primary_emotion": result.primary_emotion.value,
            "emotional_intensity": result.intensity,
            "arousal_level": result.arousal_level,
            "valence_level": result.valence_level,
            "emotional_stability": result.emotional_stability,
            "confidence": result.confidence_score
        }

class MoodExtractor:
    """Mood extraction and analysis utilities"""
    def __init__(self, detector: EmotionDetector):
        self.detector = detector
    
    async def extract_mood_profile(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Extract detailed mood profile"""
        result = await self.detector.detect_emotion(audio_data)
        
        # Map emotions to mood categories
        mood_mapping = {
            EmotionType.HAPPY: "positive",
            EmotionType.EXCITED: "energetic", 
            EmotionType.CALM: "relaxed",
            EmotionType.SAD: "melancholic",
            EmotionType.ANGRY: "aggressive",
            EmotionType.NEUTRAL: "balanced"
        }
        
        mood_scores = {}
        for emotion, score in result.emotion_scores.items():
            mood = mood_mapping.get(emotion, "other")
            mood_scores[mood] = mood_scores.get(mood, 0.0) + score
        
        return mood_scores
