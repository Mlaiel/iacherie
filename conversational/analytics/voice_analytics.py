"""Voice Analytics Engine for IA Influencer Agent Platform
Advanced voice processing, speech analytics, and audio intelligence.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution prohibited.

WARNING: This code is proprietary and confidential. Any unauthorized use,
copying, distribution, or reproduction is strictly prohibited and will be
prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing and collaboration inquiries.
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import librosa
import soundfile as sf
import speech_recognition as sr
from pydub import AudioSegment
import webrtcvad
from scipy import signal
from scipy.stats import pearsonr
import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer
import pyaudio
import wave
from concurrent.futures import ThreadPoolExecutor
import io
import base64


class VoiceMetricType(Enum):
    """Types of voice metrics for analysis."""    PITCH = "pitch"
    TONE = "tone"
    PACE = "pace"
    VOLUME = "volume"
    EMOTION = "emotion"
    STRESS_LEVEL = "stress_level"
    CONFIDENCE = "confidence"
    CLARITY = "clarity"
    ACCENT = "accent"
    LANGUAGE_PROFICIENCY = "language_proficiency"
    BREATHING_PATTERN = "breathing_pattern"
    VOCAL_FATIGUE = "vocal_fatigue"


class EmotionalState(Enum):
    """Emotional states detectable through voice."""    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    EXCITED = "excited"
    CALM = "calm"
    STRESSED = "stressed"
    CONFUSED = "confused"
    CONFIDENT = "confident"
    NERVOUS = "nervous"
    FRUSTRATED = "frustrated"


@dataclass
class VoiceFeatures:
    """Voice feature extraction results."""    audio_id: str
    duration: float
    sample_rate: int
    mfcc: np.ndarray
    spectral_features: Dict[str, float]
    prosodic_features: Dict[str, float]
    voice_quality: Dict[str, float]
    emotional_indicators: Dict[str, float]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VoiceAnalysisResult:
    """Complete voice analysis result."""    analysis_id: str
    user_id: Optional[str]
    audio_duration: float
    transcription: str
    confidence_score: float
    emotional_state: EmotionalState
    voice_metrics: Dict[VoiceMetricType, float]
    speech_patterns: Dict[str, Any]
    voice_signature: Dict[str, float]
    quality_assessment: Dict[str, float]
    recommendations: List[str]
    timestamp: datetime


class VoiceAnalytics:
    """    Enterprise-grade voice analytics engine for comprehensive
    speech analysis, emotion detection, and voice intelligence.
    """    
    def __init__(self, model_cache_dir: str = "./voice_models"):
        self.model_cache_dir = model_cache_dir
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Voice processing models
        self.speech_recognizer = None
        self.emotion_detector = None
        self.speaker_verifier = None
        self.voice_activity_detector = None
        
        # Audio processing settings
        self.audio_settings = {
            'sample_rate': 16000,
            'chunk_size': 1024,
            'channels': 1,
            'format': pyaudio.paInt16
        }
        
        # Voice analysis parameters
        self.analysis_params = {
            'frame_length': 2048,
            'hop_length': 512,
            'n_mfcc': 13,
            'n_fft': 2048,
            'window': 'hamming'
        }
        
        # Emotional voice signatures
        self.emotional_signatures = {
            EmotionalState.HAPPY: {
                'pitch_range': (150, 300),
                'pitch_variance': 'high',
                'pace': 'fast',
                'volume': 'medium_high'
            },
            EmotionalState.SAD: {
                'pitch_range': (80, 180),
                'pitch_variance': 'low',
                'pace': 'slow',
                'volume': 'low'
            },
            EmotionalState.ANGRY: {
                'pitch_range': (120, 250),
                'pitch_variance': 'high',
                'pace': 'fast',
                'volume': 'high'
            },
            EmotionalState.STRESSED: {
                'pitch_range': (160, 320),
                'pitch_variance': 'very_high',
                'pace': 'fast',
                'volume': 'medium_high'
            }
        }
        
        # Processing thread pool
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def initialize_voice_models(self):
        """Initialize voice processing and analysis models."""        try:
            self.logger.info("Initializing voice analytics models")
            
            # Initialize speech recognition
            self.speech_recognizer = sr.Recognizer()
            self.speech_recognizer.energy_threshold = 300
            self.speech_recognizer.dynamic_energy_threshold = True
            
            # Initialize voice activity detection
            self.voice_activity_detector = webrtcvad.Vad()
            self.voice_activity_detector.set_mode(3)  # Most aggressive filtering
            
            # Initialize Wav2Vec2 for advanced speech processing
            self.wav2vec_tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-base-960h")
            self.wav2vec_model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
            
            self.logger.info("Voice analytics models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing voice models: {str(e)}")
            raise
    
    async def analyze_voice_audio(self, audio_data: bytes, user_id: Optional[str] = None) -> VoiceAnalysisResult:
        """Perform comprehensive voice analysis on audio data."""        try:
            analysis_id = f"voice_{int(datetime.utcnow().timestamp())}"
            
            # Convert audio data to numpy array
            audio_array, sample_rate = await self._process_audio_data(audio_data)
            
            # Extract voice features
            voice_features = await self._extract_voice_features(audio_array, sample_rate)
            
            # Perform speech recognition
            transcription, transcription_confidence = await self._transcribe_audio(audio_data)
            
            # Detect emotional state
            emotional_state, emotion_confidence = await self._detect_emotional_state(voice_features)
            
            # Calculate voice metrics
            voice_metrics = await self._calculate_voice_metrics(voice_features, audio_array, sample_rate)
            
            # Analyze speech patterns
            speech_patterns = await self._analyze_speech_patterns(audio_array, sample_rate, transcription)
            
            # Generate voice signature
            voice_signature = await self._generate_voice_signature(voice_features)
            
            # Assess audio quality
            quality_assessment = await self._assess_audio_quality(audio_array, sample_rate)
            
            # Generate recommendations
            recommendations = await self._generate_voice_recommendations(
                voice_metrics, emotional_state, quality_assessment
            )
            
            result = VoiceAnalysisResult(
                analysis_id=analysis_id,
                user_id=user_id,
                audio_duration=len(audio_array) / sample_rate,
                transcription=transcription,
                confidence_score=transcription_confidence,
                emotional_state=emotional_state,
                voice_metrics=voice_metrics,
                speech_patterns=speech_patterns,
                voice_signature=voice_signature,
                quality_assessment=quality_assessment,
                recommendations=recommendations,
                timestamp=datetime.utcnow()
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing voice audio: {str(e)}")
            raise
    
    async def analyze_conversation_voice_dynamics(self, audio_segments: List[bytes]) -> Dict[str, Any]:
        """Analyze voice dynamics throughout a conversation."""        try:
            conversation_analysis = {
                'total_segments': len(audio_segments),
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'segment_analyses': [],
                'conversation_metrics': {},
                'emotional_journey': [],
                'voice_consistency': {},
                'engagement_indicators': {}
            }
            
            segment_results = []
            
            # Analyze each audio segment
            for i, audio_segment in enumerate(audio_segments):
                segment_analysis = await self.analyze_voice_audio(audio_segment)
                segment_results.append(segment_analysis)
                
                conversation_analysis['segment_analyses'].append({
                    'segment_number': i + 1,
                    'duration': segment_analysis.audio_duration,
                    'emotional_state': segment_analysis.emotional_state.value,
                    'confidence': segment_analysis.confidence_score,
                    'voice_metrics': segment_analysis.voice_metrics,
                    'transcription': segment_analysis.transcription
                })
            
            # Calculate conversation-level metrics
            conversation_analysis['conversation_metrics'] = await self._calculate_conversation_voice_metrics(segment_results)
            
            # Map emotional journey
            conversation_analysis['emotional_journey'] = self._map_emotional_voice_journey(segment_results)
            
            # Analyze voice consistency
            conversation_analysis['voice_consistency'] = await self._analyze_voice_consistency(segment_results)
            
            # Calculate engagement indicators
            conversation_analysis['engagement_indicators'] = await self._calculate_voice_engagement(segment_results)
            
            return conversation_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing conversation voice dynamics: {str(e)}")
            return {}
    
    async def generate_voice_insights_report(self, user_id: str, time_period: int = 30) -> Dict[str, Any]:
        """Generate comprehensive voice insights report for a user."""        try:
            # Get user's voice data for the period
            voice_analyses = await self._get_user_voice_analyses(user_id, time_period)
            
            if not voice_analyses:
                return {'error': 'No voice data found for user'}
            
            # Analyze voice evolution
            voice_evolution = await self._analyze_voice_evolution(voice_analyses)
            
            # Identify voice patterns
            voice_patterns = await self._identify_voice_patterns(voice_analyses)
            
            # Calculate voice health metrics
            voice_health = await self._assess_voice_health(voice_analyses)
            
            # Analyze emotional voice patterns
            emotional_patterns = await self._analyze_emotional_voice_patterns(voice_analyses)
            
            # Generate personalized recommendations
            personalized_recommendations = await self._generate_personalized_voice_recommendations(
                voice_evolution, voice_patterns, voice_health
            )
            
            return {
                'user_id': user_id,
                'report_period_days': time_period,
                'total_voice_analyses': len(voice_analyses),
                'report_timestamp': datetime.utcnow().isoformat(),
                'voice_evolution': voice_evolution,
                'voice_patterns': voice_patterns,
                'voice_health_assessment': voice_health,
                'emotional_voice_patterns': emotional_patterns,
                'personalized_recommendations': personalized_recommendations,
                'voice_coaching_plan': await self._generate_voice_coaching_plan(voice_analyses),
                'progress_tracking': await self._track_voice_progress(voice_analyses)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating voice insights report: {str(e)}")
            return {}
    
    async def real_time_voice_feedback(self, audio_stream: bytes) -> Dict[str, Any]:
        """Provide real-time voice feedback during conversation."""        try:
            # Quick voice analysis for real-time feedback
            audio_array, sample_rate = await self._process_audio_data(audio_stream)
            
            # Extract key features quickly
            quick_features = await self._extract_quick_voice_features(audio_array, sample_rate)
            
            # Real-time emotional state detection
            emotional_state = await self._quick_emotion_detection(quick_features)
            
            # Calculate real-time metrics
            real_time_metrics = {
                'volume_level': self._calculate_volume_level(audio_array),
                'pace_score': self._calculate_speaking_pace(audio_array, sample_rate),
                'clarity_score': self._calculate_speech_clarity(quick_features),
                'emotional_intensity': self._calculate_emotional_intensity(quick_features)
            }
            
            # Generate instant feedback
            instant_feedback = self._generate_instant_voice_feedback(real_time_metrics, emotional_state)
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'emotional_state': emotional_state.value if emotional_state else 'unknown',
                'real_time_metrics': real_time_metrics,
                'instant_feedback': instant_feedback,
                'voice_coaching_tips': self._get_real_time_coaching_tips(real_time_metrics),
                'adjustment_suggestions': self._suggest_voice_adjustments(real_time_metrics)
            }
            
        except Exception as e:
            self.logger.error(f"Error providing real-time voice feedback: {str(e)}")
            return {}
    
    # Private helper methods
    
    async def _process_audio_data(self, audio_data: bytes) -> Tuple[np.ndarray, int]:
        """Process audio data and convert to numpy array."""        try:
            # Convert bytes to audio segment
            audio_segment = AudioSegment.from_raw(
                io.BytesIO(audio_data),
                sample_width=2,
                frame_rate=self.audio_settings['sample_rate'],
                channels=self.audio_settings['channels']
            )
            
            # Convert to numpy array
            audio_array = np.array(audio_segment.get_array_of_samples())
            
            # Normalize audio
            audio_array = audio_array.astype(np.float32) / 32768.0
            
            return audio_array, self.audio_settings['sample_rate']
            
        except Exception as e:
            self.logger.error(f"Error processing audio data: {str(e)}")
            raise
    
    async def _extract_voice_features(self, audio_array: np.ndarray, sample_rate: int) -> VoiceFeatures:
        """Extract comprehensive voice features from audio."""        try:
            # Extract MFCC features
            mfcc = librosa.feature.mfcc(
                y=audio_array,
                sr=sample_rate,
                n_mfcc=self.analysis_params['n_mfcc'],
                hop_length=self.analysis_params['hop_length']
            )
            
            # Extract spectral features
            spectral_features = {
                'spectral_centroid': np.mean(librosa.feature.spectral_centroid(y=audio_array, sr=sample_rate)),
                'spectral_rolloff': np.mean(librosa.feature.spectral_rolloff(y=audio_array, sr=sample_rate)),
                'spectral_bandwidth': np.mean(librosa.feature.spectral_bandwidth(y=audio_array, sr=sample_rate)),
                'zero_crossing_rate': np.mean(librosa.feature.zero_crossing_rate(audio_array))
            }
            
            # Extract prosodic features
            prosodic_features = await self._extract_prosodic_features(audio_array, sample_rate)
            
            # Extract voice quality features
            voice_quality = await self._extract_voice_quality_features(audio_array, sample_rate)
            
            # Extract emotional indicators
            emotional_indicators = await self._extract_emotional_indicators(audio_array, sample_rate)
            
            return VoiceFeatures(
                audio_id=f"audio_{int(datetime.utcnow().timestamp())}",
                duration=len(audio_array) / sample_rate,
                sample_rate=sample_rate,
                mfcc=mfcc,
                spectral_features=spectral_features,
                prosodic_features=prosodic_features,
                voice_quality=voice_quality,
                emotional_indicators=emotional_indicators,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Error extracting voice features: {str(e)}")
            raise
    
    async def _transcribe_audio(self, audio_data: bytes) -> Tuple[str, float]:
        """Transcribe audio to text with confidence score."""        try:
            # Convert audio data for speech recognition
            audio_segment = AudioSegment.from_raw(
                io.BytesIO(audio_data),
                sample_width=2,
                frame_rate=self.audio_settings['sample_rate'],
                channels=self.audio_settings['channels']
            )
            
            # Export to wav format for speech recognition
            wav_io = io.BytesIO()
            audio_segment.export(wav_io, format="wav")
            wav_io.seek(0)
            
            # Transcribe using speech recognition
            with sr.AudioFile(wav_io) as source:
                audio = self.speech_recognizer.record(source)
                
            try:
                # Use Google Speech Recognition
                transcription = self.speech_recognizer.recognize_google(audio)
                confidence = 0.8  # Default confidence for Google API
                
            except sr.UnknownValueError:
                transcription = ""
                confidence = 0.0
            except sr.RequestError:
                # Fallback to offline recognition
                try:
                    transcription = self.speech_recognizer.recognize_sphinx(audio)
                    confidence = 0.6  # Lower confidence for offline
                except:
                    transcription = ""
                    confidence = 0.0
            
            return transcription, confidence
            
        except Exception as e:
            self.logger.error(f"Error transcribing audio: {str(e)}")
            return "", 0.0
    
    async def _detect_emotional_state(self, voice_features: VoiceFeatures) -> Tuple[EmotionalState, float]:
        """Detect emotional state from voice features."""        try:
            # Extract key emotional indicators
            pitch_mean = np.mean(voice_features.prosodic_features.get('pitch', [0]))
            pitch_variance = np.var(voice_features.prosodic_features.get('pitch', [0]))
            energy = voice_features.emotional_indicators.get('energy', 0)
            speaking_rate = voice_features.prosodic_features.get('speaking_rate', 0)
            
            # Score each emotional state
            emotion_scores = {}
            
            for emotion, signature in self.emotional_signatures.items():
                score = 0.0
                
                # Check pitch range
                pitch_range = signature['pitch_range']
                if pitch_range[0] <= pitch_mean <= pitch_range[1]:
                    score += 0.3
                
                # Check pitch variance
                if signature['pitch_variance'] == 'high' and pitch_variance > 100:
                    score += 0.2
                elif signature['pitch_variance'] == 'low' and pitch_variance < 50:
                    score += 0.2
                
                # Check pace
                if signature['pace'] == 'fast' and speaking_rate > 150:
                    score += 0.2
                elif signature['pace'] == 'slow' and speaking_rate < 100:
                    score += 0.2
                
                # Check volume/energy
                if signature['volume'] == 'high' and energy > 0.7:
                    score += 0.3
                elif signature['volume'] == 'low' and energy < 0.3:
                    score += 0.3
                
                emotion_scores[emotion] = score
            
            # Find most likely emotion
            best_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            
            return best_emotion[0], best_emotion[1]
            
        except Exception as e:
            self.logger.error(f"Error detecting emotional state: {str(e)}")
            return EmotionalState.CALM, 0.0
    
    async def _extract_prosodic_features(self, audio_array: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract prosodic features (pitch, rhythm, stress)."""        try:
            # Extract pitch using librosa
            pitches, magnitudes = librosa.piptrack(y=audio_array, sr=sample_rate)
            pitch_values = []
            
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            # Calculate prosodic features
            prosodic_features = {
                'pitch': pitch_values,
                'pitch_mean': np.mean(pitch_values) if pitch_values else 0,
                'pitch_std': np.std(pitch_values) if pitch_values else 0,
                'pitch_range': max(pitch_values) - min(pitch_values) if pitch_values else 0,
                'speaking_rate': self._calculate_speaking_rate(audio_array, sample_rate),
                'rhythm_regularity': self._calculate_rhythm_regularity(audio_array, sample_rate),
                'stress_pattern': self._analyze_stress_pattern(audio_array, sample_rate)
            }
            
            return prosodic_features
            
        except Exception as e:
            self.logger.error(f"Error extracting prosodic features: {str(e)}")
            return {}
    
    def _calculate_speaking_rate(self, audio_array: np.ndarray, sample_rate: int) -> float:
        """Calculate speaking rate (words per minute)."""        try:
            # Estimate speaking rate based on voice activity
            frame_length = int(0.025 * sample_rate)  # 25ms frames
            frame_shift = int(0.010 * sample_rate)   # 10ms shift
            
            frames = []
            for i in range(0, len(audio_array) - frame_length, frame_shift):
                frame = audio_array[i:i + frame_length]
                frames.append(frame)
            
            # Detect voice activity
            voice_frames = []
            for frame in frames:
                energy = np.sum(frame ** 2)
                if energy > 0.01:  # Voice activity threshold
                    voice_frames.append(frame)
            
            # Estimate speaking rate
            voice_duration = len(voice_frames) * frame_shift / sample_rate
            estimated_syllables = len(voice_frames) / 10  # Rough estimate
            
            # Convert to words per minute (assuming ~1.5 syllables per word)
            wpm = (estimated_syllables / 1.5) * (60 / voice_duration) if voice_duration > 0 else 0
            
            return wpm
            
        except Exception as e:
            self.logger.error(f"Error calculating speaking rate: {str(e)}")
            return 0.0
