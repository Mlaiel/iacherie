"""Audio Analysis Configuration for IA-Influencer Agent Platform
============================================================

Professional Audio Processing and Music Intelligence configuration.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

STRICT COPYRIGHT NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or reverse engineering
without explicit written permission is STRICTLY PROHIBITED and will be
prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from pydantic import BaseSettings, validator
from enum import Enum
from dataclasses import dataclass
import os


class AudioTask(str, Enum):
    """
Supported audio processing tasks."""

    
    AUDIO_FINGERPRINTING = "audio_fingerprinting"
    MUSIC_CLASSIFICATION = "music_classification"
    GENRE_DETECTION = "genre_detection"
    MOOD_ANALYSIS = "mood_analysis"
    TEMPO_DETECTION = "tempo_detection"
    KEY_DETECTION = "key_detection"
    BEAT_TRACKING = "beat_tracking"
    ONSET_DETECTION = "onset_detection"
    SPECTRAL_ANALYSIS = "spectral_analysis"
    AUDIO_SIMILARITY = "audio_similarity"
    VOICE_DETECTION = "voice_detection"
    SPEECH_RECOGNITION = "speech_recognition"
    MUSIC_TRANSCRIPTION = "music_transcription"
    AUDIO_QUALITY_ASSESSMENT = "audio_quality_assessment"
    LOUDNESS_ANALYSIS = "loudness_analysis"
    HARMONIC_ANALYSIS = "harmonic_analysis"
    AUDIO_SEGMENTATION = "audio_segmentation"
    INSTRUMENT_RECOGNITION = "instrument_recognition"
    COPYRIGHT_DETECTION = "copyright_detection"
    AUDIO_ENHANCEMENT = "audio_enhancement"


class AudioFormat(str, Enum):
    """Supported audio formats."""

    
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    WMA = "wma"
    AIFF = "aiff"


class MusicGenre(str, Enum):
    """Supported music genres for classification."""

    
    ROCK = "rock"
    POP = "pop"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    ELECTRONIC = "electronic"
    HIP_HOP = "hip_hop"
    REGGAE = "reggae"
    BLUES = "blues"
    COUNTRY = "country"
    FOLK = "folk"
    METAL = "metal"
    FUNK = "funk"
    DISCO = "disco"
    LATIN = "latin"
    WORLD = "world"
    AMBIENT = "ambient"
    EXPERIMENTAL = "experimental"


@dataclass
class AudioModelSpec:
    """Specification for audio processing model configuration."""
    
    task: AudioTask
    model_name: str
    model_path: str
    sample_rate: int = 22050
    n_fft: int = 2048
    hop_length: int = 512
    batch_size: int = 16
    requires_gpu: bool = False
    memory_requirement_mb: int = 512
    processing_time_factor: float = 0.1  # processing_time = audio_duration * factor
    accuracy_score: float = 0.85
    supports_streaming: bool = False
    output_dimension: Optional[int] = None
    custom_params: Optional[Dict[str, Any]] = None


class AudioAnalysisConfig(BaseSettings):
    """
    Professional Audio Analysis Configuration for IA-Influencer Agent Platform.
    
    Manages all audio processing models and configurations for music analysis,
    fingerprinting, copyright detection, and audio intelligence.
    """
    
    # Core Audio Configuration
    DEFAULT_SAMPLE_RATE: int = 22050
    HIGH_QUALITY_SAMPLE_RATE: int = 44100
    MAX_AUDIO_DURATION: int = 600  # seconds (10 minutes)
    MAX_AUDIO_SIZE_MB: float = 100.0
    SUPPORTED_AUDIO_FORMATS: List[str] = ["mp3", "wav", "flac", "aac", "ogg", "m4a"]
    
    # Audio Processing Parameters
    AUDIO_CHUNK_SIZE: int = 4096
    OVERLAP_RATIO: float = 0.5
    WINDOW_TYPE: str = "hann"
    N_FFT: int = 2048
    HOP_LENGTH: int = 512
    N_MELS: int = 128
    N_MFCC: int = 13
    
    # Model Configuration
    AUDIO_MODEL_CACHE_DIR: str = "/tmp/audio_models"
    GPU_ACCELERATION: bool = False  # Most audio tasks don't require GPU
    BATCH_PROCESSING: bool = True
    
    # Audio Fingerprinting Models
    CHROMAPRINT_MODEL: str = "chromaprint"
    SPECTRAL_FINGERPRINT_MODEL: str = "librosa-spectral"
    AUDIO_EMBEDDING_MODEL: str = "facebook/wav2vec2-base"
    MUSIC_FINGERPRINT_MODEL: str = "spotify/basic-pitch"
    
    # Music Analysis Models
    GENRE_CLASSIFIER_MODEL: str = "facebook/wav2vec2-base-960h"
    MOOD_ANALYZER_MODEL: str = "marsyas/gtzan-genre"
    TEMPO_DETECTION_MODEL: str = "librosa-tempo"
    KEY_DETECTION_MODEL: str = "madmom-key"
    BEAT_TRACKER_MODEL: str = "librosa-beat"
    
    # Advanced Music Intelligence
    INSTRUMENT_CLASSIFIER: str = "facebook/wav2vec2-base"
    HARMONIC_ANALYZER: str = "librosa-harmony"
    CHORD_RECOGNITION: str = "madmom-chord"
    MUSIC_TRANSCRIPTION: str = "spotify/basic-pitch"
    
    # Speech and Voice Models
    VOICE_DETECTOR: str = "pyannote/voice-activity-detection"
    SPEECH_RECOGNITION: str = "openai/whisper-base"
    SPEAKER_IDENTIFICATION: str = "pyannote/speaker-diarization"
    
    # Audio Quality and Enhancement
    QUALITY_ASSESSOR: str = "pesq-stoi"
    NOISE_REDUCER: str = "facebook/demucs"
    AUDIO_ENHANCER: str = "juce/neural-reverb"
    LOUDNESS_ANALYZER: str = "ebu-r128"
    
    # Similarity and Matching Thresholds
    SIMILARITY_THRESHOLD: float = 0.85
    COPYRIGHT_MATCH_THRESHOLD: float = 0.92
    DUPLICATE_THRESHOLD: float = 0.95
    GENRE_CONFIDENCE_THRESHOLD: float = 0.8
    
    # Processing Performance
    AUDIO_BATCH_SIZE: int = 8
    MAX_CONCURRENT_JOBS: int = 2  # Audio processing is CPU intensive
    PROCESSING_TIMEOUT: int = 300  # seconds
    
    # Music Analysis Configuration
    SUPPORTED_GENRES: List[str] = [
        "rock", "pop", "jazz", "classical", "electronic", "hip_hop",
        "reggae", "blues", "country", "folk", "metal", "funk", "disco"
    ]
    
    SUPPORTED_MOODS: List[str] = [
        "happy", "sad", "energetic", "calm", "aggressive", "romantic",
        "melancholic", "uplifting", "dark", "peaceful", "intense"
    ]
    
    SUPPORTED_INSTRUMENTS: List[str] = [
        "piano", "guitar", "drums", "bass", "violin", "saxophone",
        "trumpet", "flute", "vocals", "synthesizer", "organ"
    ]
    
    class Config:
        env_prefix = "AUDIO_"
        case_sensitive = False
        env_file = ".env"
    
    @validator("AUDIO_MODEL_CACHE_DIR")
    def create_cache_dir(cls, v):
        """Ensure audio model cache directory exists."""
        os.makedirs(v, exist_ok=True)
        os.makedirs(f"{v}/fingerprinting", exist_ok=True)
        os.makedirs(f"{v}/classification", exist_ok=True)
        os.makedirs(f"{v}/analysis", exist_ok=True)
        os.makedirs(f"{v}/speech", exist_ok=True)
        return v
    
    def get_audio_model_spec(self, task: AudioTask) -> AudioModelSpec:
        """Get audio model specification by task."""
        specs = {
            AudioTask.AUDIO_FINGERPRINTING: AudioModelSpec(
                task=AudioTask.AUDIO_FINGERPRINTING,
                model_name="chromaprint_fingerprinter",
                model_path=self.CHROMAPRINT_MODEL,
                sample_rate=self.DEFAULT_SAMPLE_RATE,
                n_fft=self.N_FFT,
                hop_length=self.HOP_LENGTH,
                batch_size=16,
                requires_gpu=False,
                memory_requirement_mb=256,
                processing_time_factor=0.05,
                accuracy_score=0.95,
                supports_streaming=True,
                output_dimension=32,  # Chromaprint hash size
                custom_params={
                    "algorithm": "chromaprint",
                    "duration_limit": 120,
                    "silence_threshold": -40
                }
            ),
            
            AudioTask.GENRE_DETECTION: AudioModelSpec(
                task=AudioTask.GENRE_DETECTION,
                model_name="genre_classifier",
                model_path=self.GENRE_CLASSIFIER_MODEL,
                sample_rate=self.DEFAULT_SAMPLE_RATE,
                n_fft=self.N_FFT,
                hop_length=self.HOP_LENGTH,
                batch_size=8,
                requires_gpu=False,
                memory_requirement_mb=768,
                processing_time_factor=0.15,
                accuracy_score=0.87,
                supports_streaming=False,
                output_dimension=len(self.SUPPORTED_GENRES),
                custom_params={
                    "genres": self.SUPPORTED_GENRES,
                    "confidence_threshold": self.GENRE_CONFIDENCE_THRESHOLD,
                    "analysis_window": 30  # seconds
                }
            ),
            
            AudioTask.MOOD_ANALYSIS: AudioModelSpec(
                task=AudioTask.MOOD_ANALYSIS,
                model_name="mood_analyzer",
                model_path=self.MOOD_ANALYZER_MODEL,
                sample_rate=self.DEFAULT_SAMPLE_RATE,
                n_fft=self.N_FFT,
                hop_length=self.HOP_LENGTH,
                batch_size=8,
                requires_gpu=False,
                memory_requirement_mb=512,
                processing_time_factor=0.12,
                accuracy_score=0.83,
                output_dimension=len(self.SUPPORTED_MOODS),
                custom_params={
                    "moods": self.SUPPORTED_MOODS,
                    "valence_arousal": True,
                    "temporal_analysis": True
                }
            ),
            
            AudioTask.TEMPO_DETECTION: AudioModelSpec(
                task=AudioTask.TEMPO_DETECTION,
                model_name="tempo_detector",
                model_path=self.TEMPO_DETECTION_MODEL,
                sample_rate=self.DEFAULT_SAMPLE_RATE,
                n_fft=self.N_FFT,
                hop_length=self.HOP_LENGTH,
                batch_size=16,
                requires_gpu=False,
                memory_requirement_mb=256,
                processing_time_factor=0.08,
                accuracy_score=0.89,
                supports_streaming=True,
                output_dimension=1,  # BPM value
                custom_params={
                    "bpm_range": (60, 200),
                    "onset_detection": True,
                    "beat_tracking": True
                }
            ),
            
            AudioTask.KEY_DETECTION: AudioModelSpec(
                task=AudioTask.KEY_DETECTION,
                model_name="key_detector",
                model_path=self.KEY_DETECTION_MODEL,
                sample_rate=self.DEFAULT_SAMPLE_RATE,
                n_fft=self.N_FFT,
                hop_length=self.HOP_LENGTH,
                batch_size=8,
                requires_gpu=False,
                memory_requirement_mb=384,
                processing_time_factor=0.10,
                accuracy_score=0.85,
                output_dimension=24,  # 12 major + 12 minor keys
                custom_params={
                    "chromagram": True,
                    "harmonic_analysis": True,
                    "key_profiles": "krumhansl"
                }
            ),
            
            AudioTask.AUDIO_SIMILARITY: AudioModelSpec(
                task=AudioTask.AUDIO_SIMILARITY,
                model_name="audio_similarity",
                model_path=self.AUDIO_EMBEDDING_MODEL,
                sample_rate=self.DEFAULT_SAMPLE_RATE,
                n_fft=self.N_FFT,
                hop_length=self.HOP_LENGTH,
                batch_size=4,
                requires_gpu=True,
                memory_requirement_mb=1024,
                processing_time_factor=0.20,
                accuracy_score=0.88,
                output_dimension=768,  # Wav2Vec2 embedding size
                custom_params={
                    "embedding_layer": -1,
                    "pooling": "mean",
                    "normalize": True
                }
            ),
            
            AudioTask.INSTRUMENT_RECOGNITION: AudioModelSpec(
                task=AudioTask.INSTRUMENT_RECOGNITION,
                model_name="instrument_classifier",
                model_path=self.INSTRUMENT_CLASSIFIER,
                sample_rate=self.DEFAULT_SAMPLE_RATE,
                n_fft=self.N_FFT,
                hop_length=self.HOP_LENGTH,
                batch_size=8,
                requires_gpu=False,
                memory_requirement_mb=512,
                processing_time_factor=0.15,
                accuracy_score=0.82,
                output_dimension=len(self.SUPPORTED_INSTRUMENTS),
                custom_params={
                    "instruments": self.SUPPORTED_INSTRUMENTS,
                    "multi_label": True,
                    "confidence_threshold": 0.7
                }
            ),
            
            AudioTask.SPEECH_RECOGNITION: AudioModelSpec(
                task=AudioTask.SPEECH_RECOGNITION,
                model_name="speech_recognizer",
                model_path=self.SPEECH_RECOGNITION,
                sample_rate=16000,  # Whisper uses 16kHz
                n_fft=400,
                hop_length=160,
                batch_size=1,  # Speech is typically processed individually
                requires_gpu=True,
                memory_requirement_mb=1536,
                processing_time_factor=0.25,
                accuracy_score=0.92,
                supports_streaming=True,
                custom_params={
                    "language": "auto",
                    "task": "transcribe",
                    "return_timestamps": True
                }
            ),
            
            AudioTask.VOICE_DETECTION: AudioModelSpec(
                task=AudioTask.VOICE_DETECTION,
                model_name="voice_detector",
                model_path=self.VOICE_DETECTOR,
                sample_rate=16000,
                n_fft=512,
                hop_length=256,
                batch_size=32,
                requires_gpu=False,
                memory_requirement_mb=256,
                processing_time_factor=0.05,
                accuracy_score=0.94,
                supports_streaming=True,
                output_dimension=1,  # Binary classification
                custom_params={
                    "min_duration": 0.1,
                    "onset_detection": True,
                    "offset_detection": True
                }
            ),
            
            AudioTask.AUDIO_QUALITY_ASSESSMENT: AudioModelSpec(
                task=AudioTask.AUDIO_QUALITY_ASSESSMENT,
                model_name="quality_assessor",
                model_path=self.QUALITY_ASSESSOR,
                sample_rate=self.HIGH_QUALITY_SAMPLE_RATE,
                n_fft=self.N_FFT,
                hop_length=self.HOP_LENGTH,
                batch_size=16,
                requires_gpu=False,
                memory_requirement_mb=384,
                processing_time_factor=0.08,
                accuracy_score=0.86,
                output_dimension=1,  # Quality score 0-1
                custom_params={
                    "metrics": ["snr", "thd", "dynamic_range", "spectral_flatness"],
                    "reference_free": True
                }
            ),
        }
        
        return specs.get(task, self._get_default_audio_spec(task))
    
    def _get_default_audio_spec(self, task: AudioTask) -> AudioModelSpec:
        """Get default audio model specification."""
        return AudioModelSpec(
            task=task,
            model_name="default_audio",
            model_path=self.AUDIO_EMBEDDING_MODEL,
            sample_rate=self.DEFAULT_SAMPLE_RATE,
            n_fft=self.N_FFT,
            hop_length=self.HOP_LENGTH,
            batch_size=self.AUDIO_BATCH_SIZE,
        )
    
    def get_audio_processing_config(self) -> Dict[str, Any]:
        """Get audio processing configuration."""
        return {
            "supported_formats": self.SUPPORTED_AUDIO_FORMATS,
            "max_size_mb": self.MAX_AUDIO_SIZE_MB,
            "max_duration": self.MAX_AUDIO_DURATION,
            "default_sample_rate": self.DEFAULT_SAMPLE_RATE,
            "high_quality_sample_rate": self.HIGH_QUALITY_SAMPLE_RATE,
            "chunk_size": self.AUDIO_CHUNK_SIZE,
            "overlap_ratio": self.OVERLAP_RATIO,
            "window_type": self.WINDOW_TYPE,
            "spectral_params": {
                "n_fft": self.N_FFT,
                "hop_length": self.HOP_LENGTH,
                "n_mels": self.N_MELS,
                "n_mfcc": self.N_MFCC,
            }
        }
    
    def get_fingerprinting_config(self) -> Dict[str, Any]:
        """Get audio fingerprinting configuration."""
        return {
            "algorithms": {
                "chromaprint": {
                    "model": self.CHROMAPRINT_MODEL,
                    "hash_size": 32,
                    "duration_limit": 120
                },
                "spectral": {
                    "model": self.SPECTRAL_FINGERPRINT_MODEL,
                    "features": ["mfcc", "chroma", "spectral_centroid"],
                    "dimension": 128
                },
                "embedding": {
                    "model": self.AUDIO_EMBEDDING_MODEL,
                    "dimension": 768,
                    "pooling": "mean"
                }
            },
            "similarity_threshold": self.SIMILARITY_THRESHOLD,
            "copyright_threshold": self.COPYRIGHT_MATCH_THRESHOLD,
            "duplicate_threshold": self.DUPLICATE_THRESHOLD,
            "batch_processing": self.BATCH_PROCESSING
        }
    
    def get_music_analysis_config(self) -> Dict[str, Any]:
        """Get music analysis configuration."""
        return {
            "genre_detection": {
                "model": self.GENRE_CLASSIFIER_MODEL,
                "supported_genres": self.SUPPORTED_GENRES,
                "confidence_threshold": self.GENRE_CONFIDENCE_THRESHOLD
            },
            "mood_analysis": {
                "model": self.MOOD_ANALYZER_MODEL,
                "supported_moods": self.SUPPORTED_MOODS,
                "valence_arousal": True
            },
            "tempo_detection": {
                "model": self.TEMPO_DETECTION_MODEL,
                "bpm_range": (60, 200),
                "beat_tracking": True
            },
            "key_detection": {
                "model": self.KEY_DETECTION_MODEL,
                "key_profiles": "krumhansl",
                "harmonic_analysis": True
            },
            "instrument_recognition": {
                "model": self.INSTRUMENT_CLASSIFIER,
                "supported_instruments": self.SUPPORTED_INSTRUMENTS,
                "multi_label": True
            }
        }
    
    def get_speech_analysis_config(self) -> Dict[str, Any]:
        """Get speech analysis configuration."""
        return {
            "voice_detection": {
                "model": self.VOICE_DETECTOR,
                "min_duration": 0.1,
                "streaming": True
            },
            "speech_recognition": {
                "model": self.SPEECH_RECOGNITION,
                "language": "auto",
                "timestamps": True,
                "streaming": True
            },
            "speaker_identification": {
                "model": self.SPEAKER_IDENTIFICATION,
                "diarization": True,
                "embeddings": True
            }
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get audio processing performance configuration."""
        return {
            "gpu_acceleration": self.GPU_ACCELERATION,
            "batch_processing": self.BATCH_PROCESSING,
            "batch_size": self.AUDIO_BATCH_SIZE,
            "max_concurrent_jobs": self.MAX_CONCURRENT_JOBS,
            "processing_timeout": self.PROCESSING_TIMEOUT,
            "memory_optimization": True,
            "streaming_support": True,
            "cache_enabled": True
        }
    
    def get_supported_tasks(self) -> List[AudioTask]:
        """Get list of all supported audio tasks."""
        return [task for task in AudioTask]
    
    def estimate_processing_time(self, task: AudioTask, audio_duration_seconds: float) -> float:
        """
Estimate processing time for audio task."""
        spec = self.get_audio_model_spec(task)
        return audio_duration_seconds * spec.processing_time_factor
    
    def get_optimal_sample_rate(self, task: AudioTask) -> int:
        """
Get optimal sample rate for specific audio task."""
        # Speech tasks typically work better with 16kHz
        if task in [AudioTask.SPEECH_RECOGNITION, AudioTask.VOICE_DETECTION]:
            return 16000
        
        # High quality analysis needs higher sample rates
        if task == AudioTask.AUDIO_QUALITY_ASSESSMENT:
            return self.HIGH_QUALITY_SAMPLE_RATE
        
        # Default for music analysis
        return self.DEFAULT_SAMPLE_RATE


# Global audio analysis configuration instance
audio_analysis_config = AudioAnalysisConfig()
