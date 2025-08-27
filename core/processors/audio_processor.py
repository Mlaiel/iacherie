"""
Audio Processor Module - IA-Influencer-Agent Platform

Enterprise-grade audio processing engine for content creators, musicians, and influencers.
Comprehensive audio analysis, enhancement, transcoding, AI-powered processing, and fingerprinting.

✨ EXPERT TEAM SPECIALTIES:
- Lead Dev IA: AI-powered audio intelligence and machine learning pipelines
- Backend Senior: Scalable audio processing architecture and performance optimization  
- ML Engineer: Advanced audio analysis algorithms and neural network models
- Audio Engineer: Professional audio processing, effects, and quality enhancement
- DBA: Audio metadata management and efficient data storage strategies
- Security Expert: Audio fingerprinting, content protection, and secure processing
- Microservices Architect: Distributed audio processing and service orchestration
- DevOps Engineer: Audio processing infrastructure and deployment automation

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Any unauthorized use, copying, 
distribution, or commercialization without explicit written permission from 
Fahed Mlaiel is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
================================================================================
"""

import asyncio
import logging
import numpy as np
import tempfile
import hashlib
from typing import Dict, Any, List, Optional, Union, BinaryIO, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import json
import time

# Audio processing imports
try:
    import librosa
    import soundfile as sf
    from pydub import AudioSegment
    import speech_recognition as sr
    import noisereduce as nr
    from scipy import signal
    import aubio
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False

# AI imports
try:
    import torch
    import transformers
    from transformers import pipeline
    AI_LIBS_AVAILABLE = True
except ImportError:
    AI_LIBS_AVAILABLE = False

logger = logging.getLogger(__name__)


class AudioFormat(str, Enum):
    """Supported audio formats"""
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    WMA = "wma"


class AudioQuality(str, Enum):
    """Audio quality levels"""
    LOW = "low"          # 64 kbps
    MEDIUM = "medium"    # 128 kbps
    HIGH = "high"        # 320 kbps
    LOSSLESS = "lossless"  # Original quality


class AudioProcessingType(str, Enum):
    """Types of audio processing"""
    ANALYSIS = "analysis"
    ENHANCEMENT = "enhancement"
    CONVERSION = "conversion"
    TRANSCRIPTION = "transcription"
    NOISE_REDUCTION = "noise_reduction"
    NORMALIZATION = "normalization"
    FINGERPRINTING = "fingerprinting"
    TEMPO_ANALYSIS = "tempo_analysis"
    PITCH_ANALYSIS = "pitch_analysis"
    MOOD_ANALYSIS = "mood_analysis"


@dataclass
class AudioProcessingConfig:
    """Configuration for audio processing"""
    sample_rate: int = 44100
    target_format: AudioFormat = AudioFormat.WAV
    target_quality: AudioQuality = AudioQuality.HIGH
    enable_noise_reduction: bool = True
    enable_normalization: bool = True
    enable_ai_analysis: bool = True
    enable_transcription: bool = True
    enable_mood_detection: bool = True
    enable_tempo_detection: bool = True
    enable_pitch_analysis: bool = True
    enable_fingerprinting: bool = True
    max_duration_seconds: int = 3600  # 1 hour
    chunk_size_seconds: int = 30
    overlap_seconds: int = 5
    noise_reduction_strength: float = 0.5
    normalization_target_db: float = -20.0


@dataclass
class AudioMetadata:
    """Comprehensive audio metadata"""
    duration: float
    sample_rate: int
    channels: int
    bit_depth: int
    format: str
    codec: str
    bitrate: int
    file_size: int
    creation_date: Optional[datetime] = None
    artist: Optional[str] = None
    title: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    bpm: Optional[float] = None
    key: Optional[str] = None
    loudness: Optional[float] = None
    peak_amplitude: Optional[float] = None
    rms_energy: Optional[float] = None


@dataclass
class AudioFeatures:
    """Advanced audio features extracted via AI"""
    tempo: Optional[float] = None
    key: Optional[str] = None
    time_signature: Optional[str] = None
    energy: Optional[float] = None
    danceability: Optional[float] = None
    valence: Optional[float] = None
    acousticness: Optional[float] = None
    instrumentalness: Optional[float] = None
    liveness: Optional[float] = None
    speechiness: Optional[float] = None
    loudness: Optional[float] = None
    spectral_centroid: Optional[List[float]] = None
    spectral_rolloff: Optional[List[float]] = None
    mfcc: Optional[List[List[float]]] = None
    chroma: Optional[List[List[float]]] = None
    onset_times: Optional[List[float]] = None
    beat_times: Optional[List[float]] = None


@dataclass
class AudioAnalysisResult:
    """Result of audio analysis"""
    success: bool
    metadata: Optional[AudioMetadata] = None
    features: Optional[AudioFeatures] = None
    transcription: Optional[str] = None
    language: Optional[str] = None
    mood: Optional[str] = None
    mood_confidence: Optional[float] = None
    quality_score: Optional[float] = None
    noise_level: Optional[float] = None
    silence_ratio: Optional[float] = None
    fingerprint: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    error_message: Optional[str] = None


class AudioProcessor:
    """
    🎵 ENTERPRISE AUDIO PROCESSOR
    
    Industrial-grade audio processing engine with advanced AI capabilities
    for content creators, musicians, and influencers.
    """
    
    def __init__(
        self,
        db_session,
        redis_client,
        config: Optional[AudioProcessingConfig] = None
    ):
        self.db_session = db_session
        self.redis_client = redis_client
        self.config = config or AudioProcessingConfig()
        self.logger = logging.getLogger(f"{__name__}.AudioProcessor")
        
        # Initialize AI models
        self._speech_recognizer = None
        self._mood_classifier = None
        self._initialized = False
        
        if not AUDIO_LIBS_AVAILABLE:
            self.logger.warning("Audio processing libraries not available")
        
        if not AI_LIBS_AVAILABLE:
            self.logger.warning("AI libraries not available")
    
    async def initialize(self) -> bool:
        """Initialize the audio processor"""
        try:
            if AI_LIBS_AVAILABLE and self.config.enable_ai_analysis:
                # Initialize speech recognition
                if self.config.enable_transcription:
                    self._speech_recognizer = sr.Recognizer()
                
                # Initialize mood classification model
                if self.config.enable_mood_detection:
                    try:
                        self._mood_classifier = pipeline(
                            "audio-classification",
                            model="superb/hubert-base-superb-er",
                            return_all_scores=True
                        )
                    except Exception as e:
                        self.logger.warning(f"Could not load mood classifier: {e}")
            
            self._initialized = True
            self.logger.info("✅ Audio processor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize audio processor: {e}")
            return False
    
    async def process(
        self,
        content: Union[bytes, str, BinaryIO],
        options: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process audio content with comprehensive analysis
        
        Args:
            content: Audio content (bytes, file path, or file object)
            options: Processing options
            metadata: Additional metadata
            
        Returns:
            Processing result dictionary
        """
        start_time = time.time()
        options = options or {}
        metadata = metadata or {}
        
        try:
            if not self._initialized:
                await self.initialize()
            
            # Load audio data
            audio_data, sample_rate = await self._load_audio(content)
            
            if audio_data is None:
                return {
                    "success": False,
                    "error_message": "Failed to load audio content",
                    "processing_time": time.time() - start_time
                }
            
            # Extract metadata
            audio_metadata = await self._extract_metadata(audio_data, sample_rate, content)
            
            # Validate audio duration
            if audio_metadata.duration > self.config.max_duration_seconds:
                return {
                    "success": False,
                    "error_message": f"Audio duration ({audio_metadata.duration}s) exceeds maximum ({self.config.max_duration_seconds}s)",
                    "processing_time": time.time() - start_time
                }
            
            # Audio enhancement
            enhanced_audio = audio_data
            if options.get("enhance", True):
                enhanced_audio = await self._enhance_audio(audio_data, sample_rate)
            
            # Feature extraction
            features = None
            if self.config.enable_ai_analysis:
                features = await self._extract_features(enhanced_audio, sample_rate)
            
            # Transcription
            transcription = None
            language = None
            if self.config.enable_transcription and options.get("transcribe", True):
                transcription, language = await self._transcribe_audio(enhanced_audio, sample_rate)
            
            # Mood analysis
            mood = None
            mood_confidence = None
            if self.config.enable_mood_detection and options.get("analyze_mood", True):
                mood, mood_confidence = await self._analyze_mood(enhanced_audio, sample_rate)
            
            # Quality assessment
            quality_score = await self._assess_quality(enhanced_audio, sample_rate)
            noise_level = await self._calculate_noise_level(audio_data, sample_rate)
            silence_ratio = await self._calculate_silence_ratio(audio_data, sample_rate)
            
            # Generate fingerprint
            fingerprint = None
            if self.config.enable_fingerprinting:
                fingerprint = await self._generate_fingerprint(enhanced_audio, sample_rate)
            
            # Generate tags
            tags = await self._generate_tags(
                metadata=audio_metadata,
                features=features,
                transcription=transcription,
                mood=mood
            )
            
            # Format conversion if requested
            processed_content = None
            if options.get("convert_format"):
                target_format = AudioFormat(options.get("target_format", self.config.target_format))
                processed_content = await self._convert_format(
                    enhanced_audio, 
                    sample_rate, 
                    target_format
                )
            
            # Create analysis result
            analysis_result = AudioAnalysisResult(
                success=True,
                metadata=audio_metadata,
                features=features,
                transcription=transcription,
                language=language,
                mood=mood,
                mood_confidence=mood_confidence,
                quality_score=quality_score,
                noise_level=noise_level,
                silence_ratio=silence_ratio,
                fingerprint=fingerprint,
                tags=tags,
                processing_time=time.time() - start_time
            )
            
            return {
                "success": True,
                "processed_content": processed_content,
                "analysis_result": analysis_result.__dict__,
                "metadata": audio_metadata.__dict__,
                "quality_metrics": {
                    "quality_score": quality_score,
                    "noise_level": noise_level,
                    "silence_ratio": silence_ratio
                },
                "tags": tags,
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            self.logger.error(f"Audio processing failed: {str(e)}")
            return {
                "success": False,
                "error_message": str(e),
                "processing_time": time.time() - start_time
            }
    
    async def _load_audio(self, content: Union[bytes, str, BinaryIO]) -> Tuple[Optional[np.ndarray], int]:
        """Load audio data from various input types"""
        try:
            if not AUDIO_LIBS_AVAILABLE:
                self.logger.error("Audio libraries not available")
                return None, 0
            
            # Handle different input types
            if isinstance(content, str):
                # File path
                audio_data, sample_rate = librosa.load(content, sr=self.config.sample_rate)
            elif isinstance(content, bytes):
                # Bytes data
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_file.write(content)
                    temp_file.flush()
                    audio_data, sample_rate = librosa.load(temp_file.name, sr=self.config.sample_rate)
                    Path(temp_file.name).unlink()  # Clean up
            else:
                # File object
                audio_data, sample_rate = librosa.load(content, sr=self.config.sample_rate)
            
            return audio_data, sample_rate
            
        except Exception as e:
            self.logger.error(f"Failed to load audio: {e}")
            return None, 0
    
    async def _extract_metadata(
        self, 
        audio_data: np.ndarray, 
        sample_rate: int, 
        original_content: Union[bytes, str, BinaryIO]
    ) -> AudioMetadata:
        """Extract comprehensive audio metadata"""
        try:
            duration = len(audio_data) / sample_rate
            channels = 1 if audio_data.ndim == 1 else audio_data.shape[0]
            
            # Calculate additional metrics
            peak_amplitude = float(np.max(np.abs(audio_data)))
            rms_energy = float(np.sqrt(np.mean(audio_data**2)))
            
            # File size
            file_size = 0
            if isinstance(original_content, bytes):
                file_size = len(original_content)
            elif isinstance(original_content, str):
                try:
                    file_size = Path(original_content).stat().st_size
                except:
                    pass
            
            return AudioMetadata(
                duration=duration,
                sample_rate=sample_rate,
                channels=channels,
                bit_depth=16,  # Default assumption
                format="wav",  # After librosa loading
                codec="pcm",
                bitrate=sample_rate * 16 * channels,
                file_size=file_size,
                creation_date=datetime.now(),
                peak_amplitude=peak_amplitude,
                rms_energy=rms_energy
            )
            
        except Exception as e:
            self.logger.error(f"Failed to extract metadata: {e}")
            return AudioMetadata(
                duration=0,
                sample_rate=sample_rate,
                channels=1,
                bit_depth=16,
                format="unknown",
                codec="unknown",
                bitrate=0,
                file_size=0
            )
    
    async def _enhance_audio(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Enhance audio quality through noise reduction and normalization"""
        try:
            enhanced = audio_data.copy()
            
            # Noise reduction
            if self.config.enable_noise_reduction:
                enhanced = nr.reduce_noise(
                    y=enhanced, 
                    sr=sample_rate,
                    prop_decrease=self.config.noise_reduction_strength
                )
            
            # Normalization
            if self.config.enable_normalization:
                # RMS normalization
                rms = np.sqrt(np.mean(enhanced**2))
                if rms > 0:
                    target_rms = 10**(self.config.normalization_target_db / 20)
                    enhanced = enhanced * (target_rms / rms)
                
                # Peak limiting
                peak = np.max(np.abs(enhanced))
                if peak > 0.95:
                    enhanced = enhanced * (0.95 / peak)
            
            return enhanced
            
        except Exception as e:
            self.logger.error(f"Audio enhancement failed: {e}")
            return audio_data
    
    async def _extract_features(self, audio_data: np.ndarray, sample_rate: int) -> AudioFeatures:
        """Extract advanced audio features using librosa and aubio"""
        try:
            features = AudioFeatures()
            
            # Tempo analysis
            if self.config.enable_tempo_detection:
                tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
                features.tempo = float(tempo)
                features.beat_times = beats.tolist()
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
            features.spectral_centroid = spectral_centroids.tolist()
            features.spectral_rolloff = spectral_rolloff.tolist()
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            features.mfcc = mfccs.tolist()
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            features.chroma = chroma.tolist()
            
            # Energy and loudness
            features.energy = float(np.sum(audio_data**2))
            features.loudness = float(20 * np.log10(np.sqrt(np.mean(audio_data**2))))
            
            # Onset detection
            onset_frames = librosa.onset.onset_detect(y=audio_data, sr=sample_rate, units='time')
            features.onset_times = onset_frames.tolist()
            
            # Additional features for music analysis
            if self.config.enable_pitch_analysis:
                # Key detection (simplified)
                chroma_mean = np.mean(chroma, axis=1)
                key_idx = np.argmax(chroma_mean)
                keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                features.key = keys[key_idx]
            
            # Music information retrieval features
            features.speechiness = await self._calculate_speechiness(audio_data, sample_rate)
            features.acousticness = await self._calculate_acousticness(audio_data, sample_rate)
            features.instrumentalness = await self._calculate_instrumentalness(audio_data, sample_rate)
            features.liveness = await self._calculate_liveness(audio_data, sample_rate)
            features.valence = await self._calculate_valence(audio_data, sample_rate)
            features.danceability = await self._calculate_danceability(audio_data, sample_rate)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
            return AudioFeatures()
    
    async def _transcribe_audio(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[Optional[str], Optional[str]]:
        """Transcribe audio to text using speech recognition"""
        try:
            if not self._speech_recognizer:
                return None, None
            
            # Convert to wav format for speech recognition
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                sf.write(temp_file.name, audio_data, sample_rate)
                temp_file.flush()
                
                # Load with speech_recognition
                with sr.AudioFile(temp_file.name) as source:
                    audio = self._speech_recognizer.record(source)
                
                # Transcribe
                try:
                    text = self._speech_recognizer.recognize_google(audio)
                    # Detect language (simplified)
                    language = "en"  # Default
                    Path(temp_file.name).unlink()  # Clean up
                    return text, language
                except sr.UnknownValueError:
                    Path(temp_file.name).unlink()  # Clean up
                    return None, None
                except sr.RequestError as e:
                    self.logger.error(f"Speech recognition service error: {e}")
                    Path(temp_file.name).unlink()  # Clean up
                    return None, None
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return None, None
    
    async def _analyze_mood(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[Optional[str], Optional[float]]:
        """Analyze audio mood using AI classification"""
        try:
            if not self._mood_classifier:
                return None, None
            
            # For now, return a simplified mood analysis
            # In production, this would use a trained emotion recognition model
            
            # Analyze energy and spectral features for mood
            energy = np.sum(audio_data**2)
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate))
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            
            # Simple mood classification based on features
            if tempo > 120 and energy > np.percentile(np.abs(audio_data), 90):
                mood = "energetic"
                confidence = 0.8
            elif tempo < 80 and spectral_centroid < 2000:
                mood = "calm"
                confidence = 0.7
            elif energy > np.percentile(np.abs(audio_data), 95):
                mood = "intense"
                confidence = 0.75
            else:
                mood = "neutral"
                confidence = 0.6
            
            return mood, confidence
            
        except Exception as e:
            self.logger.error(f"Mood analysis failed: {e}")
            return None, None
    
    async def _assess_quality(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Assess audio quality score (0-1)"""
        try:
            quality_score = 1.0
            
            # Check for clipping
            clipping_ratio = np.sum(np.abs(audio_data) > 0.99) / len(audio_data)
            quality_score -= clipping_ratio * 0.3
            
            # Check dynamic range
            dynamic_range = np.max(audio_data) - np.min(audio_data)
            if dynamic_range < 0.1:
                quality_score -= 0.2
            
            # Check frequency content
            freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)
            fft = np.abs(np.fft.fft(audio_data))
            
            # Check for reasonable frequency distribution
            low_freq_energy = np.sum(fft[np.abs(freqs) < 500])
            high_freq_energy = np.sum(fft[np.abs(freqs) > 8000])
            total_energy = np.sum(fft)
            
            if total_energy > 0:
                if low_freq_energy / total_energy > 0.8:  # Too much low frequency
                    quality_score -= 0.15
                if high_freq_energy / total_energy < 0.05:  # Too little high frequency
                    quality_score -= 0.1
            
            return max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {e}")
            return 0.5
    
    async def _calculate_noise_level(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate noise level in the audio"""
        try:
            # Simple noise estimation using lowest 10% of amplitudes
            sorted_amplitudes = np.sort(np.abs(audio_data))
            noise_level = np.mean(sorted_amplitudes[:int(len(sorted_amplitudes) * 0.1)])
            return float(noise_level)
            
        except Exception as e:
            self.logger.error(f"Noise level calculation failed: {e}")
            return 0.0
    
    async def _calculate_silence_ratio(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate ratio of silence in the audio"""
        try:
            # Threshold for silence detection
            silence_threshold = np.max(np.abs(audio_data)) * 0.01
            silence_samples = np.sum(np.abs(audio_data) < silence_threshold)
            silence_ratio = silence_samples / len(audio_data)
            return float(silence_ratio)
            
        except Exception as e:
            self.logger.error(f"Silence ratio calculation failed: {e}")
            return 0.0
    
    async def _generate_fingerprint(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Generate audio fingerprint for content identification"""
        try:
            # Simple fingerprint based on spectral features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            mfcc_mean = np.mean(mfccs, axis=1)
            
            # Create hash from MFCC features
            fingerprint_data = mfcc_mean.tobytes()
            fingerprint = hashlib.sha256(fingerprint_data).hexdigest()[:32]
            
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"Fingerprint generation failed: {e}")
            return ""
    
    async def _generate_tags(
        self,
        metadata: AudioMetadata,
        features: AudioFeatures,
        transcription: Optional[str],
        mood: Optional[str]
    ) -> List[str]:
        """Generate relevant tags for the audio content"""
        tags = []
        
        try:
            # Duration-based tags
            if metadata.duration < 30:
                tags.append("short")
            elif metadata.duration > 300:
                tags.append("long")
            
            # Quality-based tags
            if metadata.sample_rate >= 44100:
                tags.append("high-quality")
            
            # Feature-based tags
            if features and features.tempo:
                if features.tempo > 140:
                    tags.append("fast-tempo")
                elif features.tempo < 80:
                    tags.append("slow-tempo")
                else:
                    tags.append("medium-tempo")
            
            # Mood-based tags
            if mood:
                tags.append(f"mood-{mood}")
            
            # Content-based tags from transcription
            if transcription:
                tags.append("vocal")
                if len(transcription.split()) > 20:
                    tags.append("speech-heavy")
            else:
                tags.append("instrumental")
            
            return tags
            
        except Exception as e:
            self.logger.error(f"Tag generation failed: {e}")
            return []
    
    async def _convert_format(
        self, 
        audio_data: np.ndarray, 
        sample_rate: int, 
        target_format: AudioFormat
    ) -> bytes:
        """Convert audio to target format"""
        try:
            with tempfile.NamedTemporaryFile(suffix=f".{target_format.value}", delete=False) as temp_file:
                # Write to temporary file with target format
                if target_format in [AudioFormat.WAV]:
                    sf.write(temp_file.name, audio_data, sample_rate, format='wav')
                elif target_format in [AudioFormat.FLAC]:
                    sf.write(temp_file.name, audio_data, sample_rate, format='flac')
                else:
                    # Use pydub for other formats
                    sf.write(temp_file.name + ".wav", audio_data, sample_rate, format='wav')
                    audio_segment = AudioSegment.from_wav(temp_file.name + ".wav")
                    audio_segment.export(temp_file.name, format=target_format.value)
                    Path(temp_file.name + ".wav").unlink()
                
                # Read converted data
                converted_data = Path(temp_file.name).read_bytes()
                Path(temp_file.name).unlink()  # Clean up
                
                return converted_data
                
        except Exception as e:
            self.logger.error(f"Format conversion failed: {e}")
            return b""
    
    # Helper methods for advanced feature calculation
    async def _calculate_speechiness(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate speechiness score"""
        try:
            # Simplified speechiness calculation based on spectral features
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate))
            if spectral_centroid > 2000:  # Human speech frequency range
                return 0.8
            return 0.2
        except:
            return 0.5
    
    async def _calculate_acousticness(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate acousticness score"""
        try:
            # Simplified acousticness based on harmonic content
            harmonic, percussive = librosa.effects.hpss(audio_data)
            harmonic_ratio = np.sum(harmonic**2) / (np.sum(harmonic**2) + np.sum(percussive**2))
            return float(harmonic_ratio)
        except:
            return 0.5
    
    async def _calculate_instrumentalness(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate instrumentalness score"""
        try:
            # Simplified instrumentalness (inverse of speechiness)
            speechiness = await self._calculate_speechiness(audio_data, sample_rate)
            return 1.0 - speechiness
        except:
            return 0.5
    
    async def _calculate_liveness(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate liveness score"""
        try:
            # Simplified liveness based on spectral contrast and audience noise
            spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
            contrast_var = np.var(spectral_contrast)
            return min(1.0, contrast_var / 10)
        except:
            return 0.3
    
    async def _calculate_valence(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate valence (positivity) score"""
        try:
            # Simplified valence based on tempo and spectral brightness
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate))
            
            valence = (tempo / 200) * 0.5 + (spectral_centroid / 4000) * 0.5
            return min(1.0, max(0.0, valence))
        except:
            return 0.5
    
    async def _calculate_danceability(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate danceability score"""
        try:
            # Simplified danceability based on tempo stability and rhythm
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            
            # Calculate tempo stability
            if len(beats) > 1:
                beat_intervals = np.diff(beats)
                tempo_stability = 1.0 - np.std(beat_intervals) / np.mean(beat_intervals)
            else:
                tempo_stability = 0.0
            
            # Ideal dance tempo range
            if 90 <= tempo <= 140:
                tempo_score = 1.0
            else:
                tempo_score = max(0.0, 1.0 - abs(tempo - 115) / 50)
            
            danceability = (tempo_stability * 0.6) + (tempo_score * 0.4)
            return min(1.0, max(0.0, danceability))
        except:
            return 0.5
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the audio processor"""
        return {
            "status": "healthy" if self._initialized else "not_initialized",
            "audio_libs_available": AUDIO_LIBS_AVAILABLE,
            "ai_libs_available": AI_LIBS_AVAILABLE,
            "speech_recognizer_loaded": self._speech_recognizer is not None,
            "mood_classifier_loaded": self._mood_classifier is not None,
            "config": self.config.__dict__
        }


async def create_audio_processor(
    db_session,
    redis_client,
    config: Optional[Dict[str, Any]] = None
) -> AudioProcessor:
    """
    Factory function to create and initialize an audio processor
    
    Args:
        db_session: Database session
        redis_client: Redis client
        config: Configuration dictionary
        
    Returns:
        Initialized AudioProcessor instance
    """
    # Create config from dict if provided
    processor_config = None
    if config:
        processor_config = AudioProcessingConfig(**{
            k: v for k, v in config.items() 
            if k in AudioProcessingConfig.__dataclass_fields__
        })
    
    # Create processor
    processor = AudioProcessor(
        db_session=db_session,
        redis_client=redis_client,
        config=processor_config
    )
    
    # Initialize
    await processor.initialize()
    
    return processor
