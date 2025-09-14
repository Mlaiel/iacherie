"""{{audio_name}} Audio Processing Agent Template for Ainflue Platform
{{audio_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
import asyncio
import numpy as np
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from enum import Enum
from pathlib import Path
import io

import librosa
import soundfile as sf
from pydantic import BaseModel, Field, validator
import ffmpeg

from ai.base_agent import BaseAIAgent
from core.config import get_settings
from utils.exceptions import AudioProcessingError
from monitoring.audio_metrics import AudioMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class AudioFormat(Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"
    M4A = "m4a"
    AAC = "aac"


class AudioTask(Enum):
    """Audio processing tasks"""
    TRANSCRIPTION = "transcription"
    NOISE_REDUCTION = "noise_reduction"
    FORMAT_CONVERSION = "format_conversion"
    AUDIO_ENHANCEMENT = "audio_enhancement"
    SPEECH_SYNTHESIS = "speech_synthesis"
    MUSIC_ANALYSIS = "music_analysis"
    AUDIO_CLASSIFICATION = "audio_classification"
    VOLUME_NORMALIZATION = "volume_normalization"
    AUDIO_MIXING = "audio_mixing"
    SILENCE_DETECTION = "silence_detection"


class AudioQuality(Enum):
    """Audio quality levels"""
    LOW = "low"          # 22kHz, mono
    MEDIUM = "medium"    # 44.1kHz, stereo
    HIGH = "high"        # 48kHz, stereo
    STUDIO = "studio"    # 96kHz, stereo


class AudioProcessingRequest(BaseModel):
    """Audio processing request"""
    id: str = Field(..., description="Unique request identifier")
    task: AudioTask = Field(..., description="Type of audio processing task")
    input_file: str = Field(..., description="Input audio file path or data")
    output_format: Optional[AudioFormat] = Field(default=None, description="Desired output format")
    quality: AudioQuality = Field(default=AudioQuality.MEDIUM, description="Audio quality level")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Task-specific parameters")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    priority: int = Field(default=1, description="Processing priority (1-10)")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AudioProcessingResult(BaseModel):
    """Audio processing result"""
    request_id: str = Field(..., description="Original request identifier")
    success: bool = Field(..., description="Processing success status")
    output_file: Optional[str] = Field(default=None, description="Output file path")
    output_data: Optional[bytes] = Field(default=None, description="Output audio data")
    analysis_results: Optional[Dict[str, Any]] = Field(default=None, description="Analysis results")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Processing metadata")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
    """Config: class implementation"""
        arbitrary_types_allowed = True


class {{audio_name}}AudioAgent(BaseAIAgent):
    """{{audio_description}}
    
    Comprehensive audio processing agent providing:
    - Multi-format audio conversion and transcoding
    - Speech-to-text transcription and synthesis
    - Advanced noise reduction and audio enhancement
    - Music analysis and feature extraction
    - Audio classification and content detection
    - Real-time audio streaming processing
    - Audio mixing and mastering tools
    - Voice activity detection and silence removal
    - Audio quality assessment and optimization
    - Batch processing for large audio datasets
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.metrics_collector = AudioMetricsCollector()
        self.supported_formats = {fmt.value for fmt in AudioFormat}
        self.sample_rates = {
            AudioQuality.LOW: 22050,
            AudioQuality.MEDIUM: 44100,
            AudioQuality.HIGH: 48000,
            AudioQuality.STUDIO: 96000
        }
        
        # Processing state
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        
    async def process_audio(self, request: AudioProcessingRequest) -> AudioProcessingResult:
        """Process audio with specified task and parameters"""
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting audio processing task: {request.id} - {request.task.value}")
            
            # Validate input
            if not await self._validate_input(request):
                return AudioProcessingResult(
                    request_id=request.id,
                    success=False,
                    error_message="Input validation failed"
                )
            
            # Load audio data
            audio_data, sample_rate = await self._load_audio(request.input_file)
            if audio_data is None:
                return AudioProcessingResult(
                    request_id=request.id,
                    success=False,
                    error_message="Failed to load audio data"
                )
            
            # Route to specific processing function
            if request.task == AudioTask.TRANSCRIPTION:
                result_data = await self._transcribe_audio(audio_data, sample_rate, request.parameters)
            elif request.task == AudioTask.NOISE_REDUCTION:
                result_data = await self._reduce_noise(audio_data, sample_rate, request.parameters)
            elif request.task == AudioTask.FORMAT_CONVERSION:
                result_data = await self._convert_format(audio_data, sample_rate, request)
            elif request.task == AudioTask.AUDIO_ENHANCEMENT:
                result_data = await self._enhance_audio(audio_data, sample_rate, request.parameters)
            elif request.task == AudioTask.SPEECH_SYNTHESIS:
                result_data = await self._synthesize_speech(request.parameters)
            elif request.task == AudioTask.MUSIC_ANALYSIS:
                result_data = await self._analyze_music(audio_data, sample_rate, request.parameters)
            elif request.task == AudioTask.AUDIO_CLASSIFICATION:
                result_data = await self._classify_audio(audio_data, sample_rate, request.parameters)
            elif request.task == AudioTask.VOLUME_NORMALIZATION:
                result_data = await self._normalize_volume(audio_data, sample_rate, request.parameters)
            elif request.task == AudioTask.AUDIO_MIXING:
                result_data = await self._mix_audio(request.parameters)
            elif request.task == AudioTask.SILENCE_DETECTION:
                result_data = await self._detect_silence(audio_data, sample_rate, request.parameters)
            else:
                raise AudioProcessingError(f"Unsupported task: {request.task}")
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Record metrics
            await self.metrics_collector.record_processing_metrics(
                task_type=request.task.value,
                execution_time=execution_time,
                success=True,
                audio_duration=len(audio_data) / sample_rate if audio_data is not None else 0
            )
            
            return AudioProcessingResult(
                request_id=request.id,
                success=True,
                output_data=result_data.get("output_data"),
                output_file=result_data.get("output_file"),
                analysis_results=result_data.get("analysis"),
                metadata=result_data.get("metadata"),
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Audio processing failed for task {request.id}: {str(e)}")
            await self.metrics_collector.record_processing_metrics(
                task_type=request.task.value,
                execution_time=0,
                success=False,
                audio_duration=0
            )
            return AudioProcessingResult(
                request_id=request.id,
                success=False,
                error_message=str(e)
            )
    
    async def _load_audio(self, input_file: str) -> Tuple[Optional[np.ndarray], Optional[int]]:
        """Load audio file and return audio data with sample rate"""
        try:
            if input_file.startswith('http'):
                # Handle URL input
                audio_data, sample_rate = await self._load_from_url(input_file)
            elif Path(input_file).exists():
                # Handle file path
                audio_data, sample_rate = librosa.load(input_file, sr=None)
            else:
                # Handle base64 or binary data
                audio_data, sample_rate = await self._load_from_data(input_file)
            
            return audio_data, sample_rate
            
        except Exception as e:
            logger.error(f"Failed to load audio: {str(e)}")
            return None, None
    
    async def _transcribe_audio(self, audio_data: np.ndarray, sample_rate: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Transcribe audio to text"""
        try:
            # This would integrate with speech recognition services
            # For now, returning mock transcription
            language = parameters.get("language", "en")
            model = parameters.get("model", "whisper")
            
            # Mock transcription result
            transcription = {
                "text": "This is a mock transcription of the audio content.",
                "confidence": 0.95,
                "language": language,
                "model_used": model,
                "duration": len(audio_data) / sample_rate,
                "segments": [
                    {
                        "start": 0.0,
                        "end": len(audio_data) / sample_rate,
                        "text": "This is a mock transcription of the audio content.",
                        "confidence": 0.95
                    }
                ]
            }
            
            return {
                "analysis": transcription,
                "metadata": {
                    "original_sample_rate": sample_rate,
                    "duration_seconds": len(audio_data) / sample_rate
                }
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise AudioProcessingError(f"Transcription failed: {str(e)}")
    
    async def _reduce_noise(self, audio_data: np.ndarray, sample_rate: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Reduce noise in audio"""
        try:
            # Implement noise reduction using spectral subtraction or other techniques
            noise_reduction_factor = parameters.get("noise_reduction_factor", 0.5)
            
            # Simple spectral subtraction approach
            # This is a simplified implementation
            stft = librosa.stft(audio_data)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise spectrum from the first few frames
            noise_frames = parameters.get("noise_frames", 10)
            noise_spectrum = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
            
            # Apply spectral subtraction
            enhanced_magnitude = magnitude - noise_reduction_factor * noise_spectrum
            enhanced_magnitude = np.maximum(enhanced_magnitude, 0.1 * magnitude)
            
            # Reconstruct audio
            enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
            enhanced_audio = librosa.istft(enhanced_stft)
            
            # Convert to bytes for output
            output_bytes = await self._audio_to_bytes(enhanced_audio, sample_rate)
            
            return {
                "output_data": output_bytes,
                "metadata": {
                    "noise_reduction_factor": noise_reduction_factor,
                    "original_sample_rate": sample_rate,
                    "processed_length": len(enhanced_audio)
                }
            }
            
        except Exception as e:
            logger.error(f"Noise reduction failed: {str(e)}")
            raise AudioProcessingError(f"Noise reduction failed: {str(e)}")
    
    async def _convert_format(self, audio_data: np.ndarray, sample_rate: int, request: AudioProcessingRequest) -> Dict[str, Any]:
        """Convert audio format"""
        try:
            target_format = request.output_format or AudioFormat.WAV
            target_sample_rate = self.sample_rates[request.quality]
            
            # Resample if needed
            if sample_rate != target_sample_rate:
                audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=target_sample_rate)
                sample_rate = target_sample_rate
            
            # Convert to target format
            output_bytes = await self._audio_to_bytes(audio_data, sample_rate, target_format)
            
            return {
                "output_data": output_bytes,
                "metadata": {
                    "target_format": target_format.value,
                    "target_sample_rate": target_sample_rate,
                    "original_sample_rate": sample_rate,
                    "channels": 1 if audio_data.ndim == 1 else audio_data.shape[0]
                }
            }
            
        except Exception as e:
            logger.error(f"Format conversion failed: {str(e)}")
            raise AudioProcessingError(f"Format conversion failed: {str(e)}")
    
    async def _enhance_audio(self, audio_data: np.ndarray, sample_rate: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance audio quality"""
        try:
            # Apply various enhancement techniques
            enhanced_audio = audio_data.copy()
            
            # Normalize volume
            if parameters.get("normalize", True):
                enhanced_audio = librosa.util.normalize(enhanced_audio)
            
            # Apply compression
            if parameters.get("apply_compression", False):
                threshold = parameters.get("compression_threshold", 0.8)
                ratio = parameters.get("compression_ratio", 4.0)
                enhanced_audio = await self._apply_compression(enhanced_audio, threshold, ratio)
            
            # Apply EQ
            if parameters.get("apply_eq", False):
                eq_settings = parameters.get("eq_settings", {})
                enhanced_audio = await self._apply_eq(enhanced_audio, sample_rate, eq_settings)
            
            # Convert to bytes
            output_bytes = await self._audio_to_bytes(enhanced_audio, sample_rate)
            
            return {
                "output_data": output_bytes,
                "metadata": {
                    "enhancements_applied": list(parameters.keys()),
                    "original_sample_rate": sample_rate,
                    "processed_length": len(enhanced_audio)
                }
            }
            
        except Exception as e:
            logger.error(f"Audio enhancement failed: {str(e)}")
            raise AudioProcessingError(f"Audio enhancement failed: {str(e)}")
    
    async def _synthesize_speech(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize speech from text"""
        try:
            text = parameters.get("text", "")
            voice = parameters.get("voice", "default")
            language = parameters.get("language", "en")
            speed = parameters.get("speed", 1.0)
            
            if not text:
                raise AudioProcessingError("Text is required for speech synthesis")
            
            # This would integrate with TTS services
            # For now, returning mock synthesis
            duration = len(text) * 0.1  # Mock duration calculation
            sample_rate = 22050
            
            # Generate mock audio (sine wave for demonstration)
            t = np.linspace(0, duration, int(duration * sample_rate))
            frequency = 440  # A4 note
            mock_audio = 0.5 * np.sin(2 * np.pi * frequency * t)
            
            output_bytes = await self._audio_to_bytes(mock_audio, sample_rate)
            
            return {
                "output_data": output_bytes,
                "metadata": {
                    "text": text,
                    "voice": voice,
                    "language": language,
                    "speed": speed,
                    "duration": duration,
                    "sample_rate": sample_rate
                }
            }
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {str(e)}")
            raise AudioProcessingError(f"Speech synthesis failed: {str(e)}")
    
    async def _analyze_music(self, audio_data: np.ndarray, sample_rate: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze music features"""
        try:
            # Extract various music features
            features = {}
            
            # Tempo detection
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            features["tempo"] = float(tempo)
            features["beat_times"] = beats.tolist()
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            features["spectral_centroid_mean"] = float(np.mean(spectral_centroids))
            features["spectral_centroid_std"] = float(np.std(spectral_centroids))
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            features["chroma_mean"] = np.mean(chroma, axis=1).tolist()
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            features["mfcc_mean"] = np.mean(mfccs, axis=1).tolist()
            features["mfcc_std"] = np.std(mfccs, axis=1).tolist()
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
            features["zero_crossing_rate_mean"] = float(np.mean(zcr))
            
            # RMS energy
            rms = librosa.feature.rms(y=audio_data)[0]
            features["rms_energy_mean"] = float(np.mean(rms))
            features["rms_energy_std"] = float(np.std(rms))
            
            return {
                "analysis": features,
                "metadata": {
                    "sample_rate": sample_rate,
                    "duration": len(audio_data) / sample_rate,
                    "features_extracted": list(features.keys())
                }
            }
            
        except Exception as e:
            logger.error(f"Music analysis failed: {str(e)}")
            raise AudioProcessingError(f"Music analysis failed: {str(e)}")
    
    async def _classify_audio(self, audio_data: np.ndarray, sample_rate: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Classify audio content"""
        try:
            # This would use trained models for audio classification
            # For now, implementing basic heuristics
            
            # Extract features for classification
            features = {}
            
            # Energy-based features
            rms = librosa.feature.rms(y=audio_data)[0]
            features["average_energy"] = float(np.mean(rms))
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            features["spectral_centroid"] = float(np.mean(spectral_centroids))
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
            features["zero_crossing_rate"] = float(np.mean(zcr))
            
            # Simple classification logic
            classifications = []
            
            if features["zero_crossing_rate"] > 0.1:
                classifications.append({"label": "speech", "confidence": 0.8})
            else:
                classifications.append({"label": "music", "confidence": 0.7})
            
            if features["average_energy"] < 0.01:
                classifications.append({"label": "quiet", "confidence": 0.9})
            elif features["average_energy"] > 0.1:
                classifications.append({"label": "loud", "confidence": 0.9})
            else:
                classifications.append({"label": "normal", "confidence": 0.8})
            
            return {
                "analysis": {
                    "classifications": classifications,
                    "features": features,
                    "primary_class": classifications[0]["label"] if classifications else "unknown"
                },
                "metadata": {
                    "sample_rate": sample_rate,
                    "duration": len(audio_data) / sample_rate
                }
            }
            
        except Exception as e:
            logger.error(f"Audio classification failed: {str(e)}")
            raise AudioProcessingError(f"Audio classification failed: {str(e)}")
    
    async def _normalize_volume(self, audio_data: np.ndarray, sample_rate: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize audio volume"""
        try:
            target_db = parameters.get("target_db", -20)
            method = parameters.get("method", "peak")
            
            if method == "peak":
                # Peak normalization
                normalized_audio = librosa.util.normalize(audio_data)
            elif method == "rms":
                # RMS normalization
                current_rms = np.sqrt(np.mean(audio_data**2))
                target_rms = 10**(target_db/20)
                gain = target_rms / current_rms if current_rms > 0 else 1
                normalized_audio = audio_data * gain
            else:
                # Loudness normalization (simplified)
                normalized_audio = librosa.util.normalize(audio_data)
            
            # Prevent clipping
            normalized_audio = np.clip(normalized_audio, -1.0, 1.0)
            
            output_bytes = await self._audio_to_bytes(normalized_audio, sample_rate)
            
            return {
                "output_data": output_bytes,
                "metadata": {
                    "normalization_method": method,
                    "target_db": target_db,
                    "original_peak": float(np.max(np.abs(audio_data))),
                    "normalized_peak": float(np.max(np.abs(normalized_audio)))
                }
            }
            
        except Exception as e:
            logger.error(f"Volume normalization failed: {str(e)}")
            raise AudioProcessingError(f"Volume normalization failed: {str(e)}")
    
    async def _detect_silence(self, audio_data: np.ndarray, sample_rate: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Detect silence in audio"""
        try:
            threshold_db = parameters.get("threshold_db", -40)
            min_silence_duration = parameters.get("min_silence_duration", 0.5)
            
            # Convert to dB
            audio_db = 20 * np.log10(np.abs(audio_data) + 1e-10)
            
            # Find silent regions
            silence_mask = audio_db < threshold_db
            
            # Find continuous silent regions
            silence_regions = []
            in_silence = False
            silence_start = 0
            
            frame_duration = 1.0 / sample_rate
            
            for i, is_silent in enumerate(silence_mask):
                if is_silent and not in_silence:
                    silence_start = i * frame_duration
                    in_silence = True
                elif not is_silent and in_silence:
                    silence_duration = i * frame_duration - silence_start
                    if silence_duration >= min_silence_duration:
                        silence_regions.append({
                            "start": silence_start,
                            "end": i * frame_duration,
                            "duration": silence_duration
                        })
                    in_silence = False
            
            # Handle case where audio ends in silence
            if in_silence:
                silence_duration = len(audio_data) * frame_duration - silence_start
                if silence_duration >= min_silence_duration:
                    silence_regions.append({
                        "start": silence_start,
                        "end": len(audio_data) * frame_duration,
                        "duration": silence_duration
                    })
            
            total_silence_duration = sum(region["duration"] for region in silence_regions)
            total_duration = len(audio_data) / sample_rate
            silence_percentage = (total_silence_duration / total_duration) * 100
            
            return {
                "analysis": {
                    "silence_regions": silence_regions,
                    "total_silence_duration": total_silence_duration,
                    "total_duration": total_duration,
                    "silence_percentage": silence_percentage,
                    "num_silence_regions": len(silence_regions)
                },
                "metadata": {
                    "threshold_db": threshold_db,
                    "min_silence_duration": min_silence_duration,
                    "sample_rate": sample_rate
                }
            }
            
        except Exception as e:
            logger.error(f"Silence detection failed: {str(e)}")
            raise AudioProcessingError(f"Silence detection failed: {str(e)}")
    
    async def _audio_to_bytes(self, audio_data: np.ndarray, sample_rate: int, format: AudioFormat = AudioFormat.WAV) -> bytes:
        """Convert audio data to bytes in specified format"""
        try:
            buffer = io.BytesIO()
            sf.write(buffer, audio_data, sample_rate, format=format.value.upper())
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Audio to bytes conversion failed: {str(e)}")
            raise AudioProcessingError(f"Audio conversion failed: {str(e)}")
    
    async def _validate_input(self, request: AudioProcessingRequest) -> bool:
        """Validate audio processing request"""
        if not request.input_file:
            return False
        
        if request.output_format and request.output_format not in self.supported_formats:
            return False
        
        return True
    
    # Additional helper methods would be implemented here
    async def _load_from_url(self, url: str) -> Tuple[np.ndarray, int]: pass
    async def _load_from_data(self, data: str) -> Tuple[np.ndarray, int]: pass
    async def _apply_compression(self, audio: np.ndarray, threshold: float, ratio: float) -> np.ndarray: return audio
    async def _apply_eq(self, audio: np.ndarray, sample_rate: int, eq_settings: Dict) -> np.ndarray: return audio
    async def _mix_audio(self, parameters: Dict[str, Any]) -> Dict[str, Any]: return {}

# File has syntax issues - needs manual review