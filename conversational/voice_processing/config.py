"""
Voice Processing Configuration Module - IA Influencer Agent Conversational System

Ultra-advanced enterprise-grade configuration management for voice processing components 
including real-time speech recognition, neural voice synthesis, deep emotion detection,
biometric speaker identification, voice security, and multi-language processing systems
optimized for content creators, influencers, and conversational AI workflows.

Features:
- Neural speech recognition engines (Whisper, Google Cloud, Azure Cognitive, OpenAI)
- Advanced voice synthesis models (Coqui TTS, Tacotron2, FastSpeech2, StyleTTS)
- Deep emotion detection AI with sentiment analysis (Wav2Vec2, HuBERT, WavLM)
- Biometric speaker identification with anti-spoofing (X-Vector, ECAPA-TDNN)
- Voice security and forensic fingerprinting (Chromaprint, Spectral Hashing)
- Multi-language processing configurations (50+ languages)
- Real-time streaming optimization with low-latency processing
- Professional quality assessment with perceptual metrics
- Voice cloning and transformation with ethical safeguards
- Forensic audio analysis and voice authentication

Business Logic Integration:
Creator Upload → Voice Analysis → AI Enhancement → Quality Assessment → Protection → Monetization

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Project Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE - ZERO TOLERANCE FOR INTELLECTUAL PROPERTY THEFT ⚠️

This revolutionary voice processing configuration system, neural audio algorithms, and advanced 
conversational architectures are the EXCLUSIVE intellectual property of Fahed Mlaiel representing 
thousands of hours of expert development work.

ABSOLUTELY PROHIBITED WITHOUT EXPLICIT WRITTEN AUTHORIZATION FROM FAHED MLAIEL:
- Using, copying, modifying, or distributing this code
- Reverse engineering algorithms or architectural patterns  
- Commercial exploitation or resale of concepts
- Creating derivative works or competitive products
- Unauthorized access to proprietary methods

For official licensing inquiries ONLY: mlaiel@live.de
"""

import os
import sys
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json
import yaml
import logging
from enum import Enum, IntEnum
import hashlib
import secrets
from datetime import datetime, timedelta
import numpy as np
from pydantic import BaseModel, Field, validator
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class VoiceEngine(Enum):
    """Advanced voice processing engines with industrial capabilities."""
    # Speech Recognition Engines
    WHISPER_OPENAI = "whisper_openai"
    WHISPER_LARGE_V3 = "whisper_large_v3"
    WHISPER_TURBO = "whisper_turbo"
    GOOGLE_SPEECH_V2 = "google_speech_v2"
    AZURE_SPEECH_STUDIO = "azure_speech_studio"
    AWS_TRANSCRIBE = "aws_transcribe"
    NVIDIA_RIVA = "nvidia_riva"
    
    # Voice Synthesis Engines
    COQUI_TTS_XTTS = "coqui_tts_xtts"
    TACOTRON2_NVIDIA = "tacotron2_nvidia"
    FASTSPEECH2_ADVANCED = "fastspeech2_advanced"
    STYLETTS2 = "styletts2"
    TORTOISE_TTS = "tortoise_tts"
    BARK_SUNO = "bark_suno"
    ELEVENLABS_API = "elevenlabs_api"
    
    # Emotion Detection Engines
    WAV2VEC2_EMOTION = "wav2vec2_emotion"
    HUBERT_EMOTION = "hubert_emotion"
    WAVLM_EMOTION = "wavlm_emotion"
    OPENSMILE_ADVANCED = "opensmile_advanced"
    
    # Speaker Identification Engines
    ECAPA_TDNN = "ecapa_tdnn"
    XVECTOR_ADVANCED = "xvector_advanced"
    RESEMBLYZER = "resemblyzer"
    SPEECHBRAIN_SPKREC = "speechbrain_spkrec"

class AudioFormat(Enum):
    """Professional audio formats with high-quality specifications."""
    WAV_PCM = "wav_pcm"
    FLAC_LOSSLESS = "flac_lossless"
    MP3_320KBPS = "mp3_320kbps"
    AAC_256KBPS = "aac_256kbps"
    OGG_VORBIS = "ogg_vorbis"
    OPUS_WEBRTC = "opus_webrtc"
    M4A_ALAC = "m4a_alac"
    AIFF_PROFESSIONAL = "aiff_professional"

class ProcessingMode(Enum):
    """Voice processing operation modes."""
    REAL_TIME = "real_time"
    BATCH_PROCESSING = "batch_processing"
    STREAMING = "streaming"
    OFFLINE_ANALYSIS = "offline_analysis"

class QualityLevel(IntEnum):
    """Audio quality levels for processing."""
    DRAFT = 1
    STANDARD = 2
    HIGH = 3
    PROFESSIONAL = 4
    STUDIO = 5

class SecurityLevel(IntEnum):
    """Security levels for voice processing."""
    BASIC = 1
    STANDARD = 2
    HIGH = 3
    MILITARY = 4
    FORENSIC = 5

@dataclass
class AdvancedSpeechRecognitionConfig:
    """Ultra-advanced speech recognition configuration."""
    # Primary and fallback engines
    primary_engine: VoiceEngine = VoiceEngine.WHISPER_LARGE_V3
    fallback_engines: List[VoiceEngine] = field(default_factory=lambda: [
        VoiceEngine.GOOGLE_SPEECH_V2, VoiceEngine.AZURE_SPEECH_STUDIO
    ])
    
    # Language and detection
    auto_language_detection: bool = True
    supported_languages: List[str] = field(default_factory=lambda: [
        "en-US", "fr-FR", "de-DE", "es-ES", "it-IT", "pt-BR", "ru-RU", 
        "zh-CN", "ja-JP", "ko-KR", "ar-SA", "hi-IN", "nl-NL", "sv-SE"
    ])
    
    # Quality and performance
    confidence_threshold: float = 0.85
    word_confidence_threshold: float = 0.70
    silence_threshold: float = 0.01
    chunk_size: int = 8192
    sample_rate: int = 16000
    channels: int = 1
    bit_depth: int = 16
    
    # Advanced processing
    noise_reduction_enabled: bool = True
    voice_activity_detection: bool = True
    speaker_diarization: bool = True
    punctuation_restoration: bool = True
    profanity_filtering: bool = True
    
    # Real-time settings
    real_time_processing: bool = True
    streaming_chunk_duration: float = 0.1  # seconds
    max_streaming_duration: int = 3600  # 1 hour
    
    # Whisper specific advanced settings
    whisper_model_size: str = "large-v3"
    whisper_device: str = "auto"  # auto, cpu, cuda
    whisper_compute_type: str = "float16"
    whisper_beam_size: int = 5
    whisper_temperature: float = 0.0
    whisper_compression_ratio_threshold: float = 2.4
    whisper_logprob_threshold: float = -1.0
    whisper_no_speech_threshold: float = 0.6
    
    # Google Speech advanced settings
    google_model: str = "latest_long"
    google_use_enhanced: bool = True
    google_enable_automatic_punctuation: bool = True
    google_enable_spoken_punctuation: bool = False
    google_enable_spoken_emojis: bool = False
    google_max_alternatives: int = 3
    
    # Azure Speech advanced settings
    azure_region: str = "westeurope"
    azure_endpoint_id: Optional[str] = None
    azure_detailed_results: bool = True
    azure_profanity_option: str = "Masked"  # Masked, Removed, Raw
    azure_output_format: str = "detailed"

@dataclass
class NeuralVoiceSynthesisConfig:
    """Neural voice synthesis configuration for professional voice generation."""
    # Engine selection
    primary_engine: VoiceEngine = VoiceEngine.COQUI_TTS_XTTS
    fallback_engines: List[VoiceEngine] = field(default_factory=lambda: [
        VoiceEngine.TACOTRON2_NVIDIA, VoiceEngine.FASTSPEECH2_ADVANCED
    ])
    
    # Voice cloning and personalization
    voice_cloning_enabled: bool = True
    multi_speaker_support: bool = True
    emotion_controllable: bool = True
    speaking_rate_control: bool = True
    pitch_control: bool = True
    
    # Quality settings
    quality_level: QualityLevel = QualityLevel.PROFESSIONAL
    sample_rate: int = 22050
    bit_depth: int = 16
    channels: int = 1
    
    # Advanced neural settings
    use_gpu_acceleration: bool = True
    batch_synthesis: bool = True
    streaming_synthesis: bool = True
    low_latency_mode: bool = True
    
    # Coqui TTS XTTS advanced settings
    coqui_model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    coqui_vocoder: str = "vocoder_models/universal/libri-tts/wavegrad"
    coqui_language_detection: bool = True
    coqui_emotion_control: bool = True
    coqui_speed_factor: float = 1.0
    
    # Tacotron2 advanced settings
    tacotron2_checkpoint: str = "tacotron2_statedict.pt"
    waveglow_checkpoint: str = "waveglow_256channels_ljs_v2.pt"
    tacotron2_gate_threshold: float = 0.5
    tacotron2_max_decoder_steps: int = 1000
    
    # Voice characteristics
    supported_voices: List[str] = field(default_factory=lambda: [
        "female_professional", "male_professional", "neutral_ai",
        "energetic_young", "calm_mature", "authoritative_deep"
    ])
    
    # Security and ethics
    voice_signature_required: bool = True
    deepfake_detection: bool = True
    consent_verification: bool = True
    usage_logging: bool = True

@dataclass
class DeepEmotionDetectionConfig:
    """Deep learning emotion detection configuration."""
    enabled: bool = True
    
    # Model selection
    primary_model: VoiceEngine = VoiceEngine.WAV2VEC2_EMOTION
    fallback_models: List[VoiceEngine] = field(default_factory=lambda: [
        VoiceEngine.HUBERT_EMOTION, VoiceEngine.WAVLM_EMOTION
    ])
    
    # Emotion categories
    emotion_labels: List[str] = field(default_factory=lambda: [
        "neutral", "happiness", "sadness", "anger", "fear", "surprise", 
        "disgust", "contempt", "excitement", "frustration", "confusion",
        "confidence", "uncertainty", "stress", "relaxation"
    ])
    
    # Detection thresholds
    confidence_threshold: float = 0.70
    multi_emotion_detection: bool = True
    emotion_intensity_scaling: bool = True
    
    # Processing settings
    real_time_processing: bool = True
    window_size: float = 3.0  # seconds
    overlap_ratio: float = 0.5
    frame_shift: float = 0.01  # 10ms
    
    # Advanced features
    arousal_valence_detection: bool = True
    emotion_transition_tracking: bool = True
    speaker_emotion_profiling: bool = True
    cultural_emotion_adaptation: bool = True
    
    # Output settings
    emotion_timestamps: bool = True
    emotion_confidence_scores: bool = True
    emotion_trend_analysis: bool = True

@dataclass
class BiometricSpeakerConfig:
    """Biometric speaker identification and verification configuration."""
    enabled: bool = True
    
    # Engine selection
    primary_engine: VoiceEngine = VoiceEngine.ECAPA_TDNN
    fallback_engines: List[VoiceEngine] = field(default_factory=lambda: [
        VoiceEngine.XVECTOR_ADVANCED, VoiceEngine.SPEECHBRAIN_SPKREC
    ])
    
    # Identification settings
    enrollment_threshold: float = 0.80
    verification_threshold: float = 0.75
    identification_threshold: float = 0.70
    
    # Biometric features
    embedding_dimension: int = 512
    max_enrolled_speakers: int = 1000
    speaker_update_frequency: int = 10  # enrollments
    
    # Security features
    liveness_detection: bool = True
    anti_spoofing_enabled: bool = True
    replay_attack_detection: bool = True
    synthetic_voice_detection: bool = True
    
    # Voice activity detection
    vad_enabled: bool = True
    vad_threshold: float = 0.5
    min_speech_duration: float = 1.0  # seconds
    max_silence_duration: float = 2.0  # seconds
    
    # Performance optimization
    fast_enrollment: bool = True
    incremental_learning: bool = True
    speaker_clustering: bool = True
    
    # Privacy and compliance
    biometric_encryption: bool = True
    gdpr_compliance: bool = True
    data_retention_days: int = 365
    consent_tracking: bool = True

@dataclass
class ForensicVoiceSecurityConfig:
    """Forensic-grade voice security and protection configuration."""
    enabled: bool = True
    security_level: SecurityLevel = SecurityLevel.HIGH
    
    # Voice fingerprinting
    fingerprinting_enabled: bool = True
    fingerprint_algorithms: List[str] = field(default_factory=lambda: [
        "chromaprint", "spectral_hash", "mfcc_hash", "mel_spectrogram_hash"
    ])
    hash_length: int = 256
    similarity_threshold: float = 0.85
    
    # Real-time monitoring
    real_time_monitoring: bool = True
    threat_detection: bool = True
    anomaly_detection: bool = True
    intrusion_detection: bool = True
    
    # Encryption and protection
    voice_encryption: bool = True
    encryption_algorithm: str = "AES-256-GCM"
    key_rotation_interval: int = 86400  # 24 hours
    secure_key_storage: bool = True
    
    # Forensic analysis
    forensic_logging: bool = True
    chain_of_custody: bool = True
    tamper_detection: bool = True
    metadata_preservation: bool = True
    
    # Threat intelligence
    deepfake_detection: bool = True
    voice_conversion_detection: bool = True
    impersonation_detection: bool = True
    
    # Security monitoring
    max_processing_time: int = 300  # seconds
    suspicious_activity_threshold: int = 5
    rate_limiting_enabled: bool = True
    ip_geolocation_tracking: bool = True
    
    # Compliance
    audit_trail_enabled: bool = True
    compliance_reporting: bool = True
    data_sovereignty: bool = True

@dataclass
class PerformanceOptimizationConfig:
    """Performance optimization configuration for voice processing."""
    # Processing modes
    processing_mode: ProcessingMode = ProcessingMode.REAL_TIME
    parallel_processing: bool = True
    gpu_acceleration: bool = True
    cpu_optimization: bool = True
    
    # Resource management
    max_concurrent_jobs: int = 8
    memory_limit_gb: int = 16
    gpu_memory_fraction: float = 0.8
    cpu_cores_limit: int = 0  # 0 = auto-detect
    
    # Caching and storage
    cache_enabled: bool = True
    cache_size_gb: int = 5
    cache_ttl_seconds: int = 3600
    persistent_cache: bool = True
    
    # Network optimization
    connection_pooling: bool = True
    request_timeout: int = 30
    retry_attempts: int = 3
    backoff_strategy: str = "exponential"
    
    # Quality vs performance trade-offs
    quality_vs_speed_balance: float = 0.7  # 0.0=speed, 1.0=quality
    adaptive_quality: bool = True
    dynamic_resource_allocation: bool = True

@dataclass
class MonitoringAndLoggingConfig:
    """Comprehensive monitoring and logging configuration."""
    # Logging levels
    detailed_logging: bool = True
    performance_logging: bool = True
    security_logging: bool = True
    debug_mode: bool = False
    
    # Metrics collection
    performance_metrics: bool = True
    usage_analytics: bool = True
    error_tracking: bool = True
    latency_monitoring: bool = True
    
    # Health checks
    health_check_interval: int = 60  # seconds
    heartbeat_monitoring: bool = True
    service_discovery: bool = True
    
    # Alerting
    alert_on_errors: bool = True
    alert_on_performance: bool = True
    alert_on_security: bool = True
    notification_channels: List[str] = field(default_factory=lambda: ["email", "slack"])
    
    # Data retention
    log_retention_days: int = 90
    metrics_retention_days: int = 365
    audit_retention_days: int = 2555  # 7 years

@dataclass
class VoiceProcessingConfig:
    """Master configuration class for ultra-advanced voice processing module."""
    
    # Component configurations
    speech_recognition: AdvancedSpeechRecognitionConfig = field(default_factory=AdvancedSpeechRecognitionConfig)
    voice_synthesis: NeuralVoiceSynthesisConfig = field(default_factory=NeuralVoiceSynthesisConfig)
    emotion_detection: DeepEmotionDetectionConfig = field(default_factory=DeepEmotionDetectionConfig)
    speaker_identification: BiometricSpeakerConfig = field(default_factory=BiometricSpeakerConfig)
    voice_security: ForensicVoiceSecurityConfig = field(default_factory=ForensicVoiceSecurityConfig)
    performance: PerformanceOptimizationConfig = field(default_factory=PerformanceOptimizationConfig)
    monitoring: MonitoringAndLoggingConfig = field(default_factory=MonitoringAndLoggingConfig)
    
    # General settings
    version: str = "2.0.0"
    environment: str = "production"  # development, staging, production
    
    # Supported capabilities
    supported_languages: List[str] = field(default_factory=lambda: [
        "en-US", "en-GB", "fr-FR", "fr-CA", "de-DE", "de-AT", "es-ES", "es-MX",
        "it-IT", "pt-BR", "pt-PT", "ru-RU", "zh-CN", "zh-TW", "ja-JP", "ko-KR",
        "ar-SA", "ar-AE", "hi-IN", "nl-NL", "sv-SE", "no-NO", "da-DK", "fi-FI",
        "pl-PL", "cs-CZ", "hu-HU", "ro-RO", "bg-BG", "hr-HR", "sk-SK", "sl-SI",
        "et-EE", "lv-LV", "lt-LT", "uk-UA", "be-BY", "ka-GE", "hy-AM", "az-AZ",
        "kk-KZ", "ky-KG", "tg-TJ", "uz-UZ", "mn-MN", "my-MM", "th-TH", "vi-VN",
        "id-ID", "ms-MY", "tl-PH", "bn-BD", "ur-PK", "fa-IR", "tr-TR", "he-IL"
    ])
    
    supported_formats: List[AudioFormat] = field(default_factory=lambda: [
        AudioFormat.WAV_PCM, AudioFormat.FLAC_LOSSLESS, AudioFormat.MP3_320KBPS,
        AudioFormat.AAC_256KBPS, AudioFormat.OGG_VORBIS, AudioFormat.OPUS_WEBRTC
    ])
    
    # File processing limits
    max_file_size_mb: int = 500
    max_duration_minutes: int = 180  # 3 hours
    min_duration_seconds: float = 0.1
    processing_timeout_seconds: int = 900  # 15 minutes
    
    # Storage and temporary files
    temp_directory: str = "/tmp/voice_processing"
    upload_directory: str = "/var/uploads/voice"
    output_directory: str = "/var/output/voice"
    model_cache_directory: str = "/var/cache/voice_models"
    
    # API and service settings
    api_rate_limit: int = 1000  # requests per minute
    max_concurrent_requests: int = 50
    request_timeout: int = 300
    
    # Business logic settings
    content_creator_features: bool = True
    influencer_analytics: bool = True
    collaboration_tools: bool = True
    monetization_tracking: bool = True
    copyright_protection: bool = True
    
    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Create required directories
        directories = [
            self.temp_directory,
            self.upload_directory,
            self.output_directory,
            self.model_cache_directory
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Validate configuration
        self._validate_configuration()
        
        # Initialize security
        self._initialize_security()
        
        # Setup monitoring
        self._setup_monitoring()
        
        logger.info(f"VoiceProcessingConfig v{self.version} initialized successfully")
    
    def _validate_configuration(self) -> None:
        """Comprehensive configuration validation."""
        # Validate file size limits
        if self.max_file_size_mb <= 0 or self.max_file_size_mb > 1000:
            raise ValueError("max_file_size_mb must be between 1 and 1000")
        
        # Validate duration limits
        if self.max_duration_minutes <= 0 or self.max_duration_minutes > 360:
            raise ValueError("max_duration_minutes must be between 1 and 360")
        
        # Validate timeout settings
        if self.processing_timeout_seconds <= 0:
            raise ValueError("processing_timeout_seconds must be positive")
        
        # Validate concurrent limits
        if self.max_concurrent_requests <= 0 or self.max_concurrent_requests > 1000:
            raise ValueError("max_concurrent_requests must be between 1 and 1000")
        
        # Validate language support
        if not self.supported_languages:
            raise ValueError("At least one language must be supported")
        
        # Validate format support
        if not self.supported_formats:
            raise ValueError("At least one audio format must be supported")
        
        # Validate directories
        for directory in [self.temp_directory, self.upload_directory, 
                         self.output_directory, self.model_cache_directory]:
            if not os.path.isabs(directory):
                raise ValueError(f"Directory path must be absolute: {directory}")
    
    def _initialize_security(self) -> None:
        """Initialize security components."""
        if self.voice_security.enabled:
            # Generate encryption keys if needed
            if self.voice_security.voice_encryption:
                key_file = os.path.join(self.temp_directory, ".voice_encryption_key")
                if not os.path.exists(key_file):
                    encryption_key = secrets.token_bytes(32)  # 256-bit key
                    with open(key_file, 'wb') as f:
                        f.write(encryption_key)
                    os.chmod(key_file, 0o600)  # Read-write for owner only
    
    def _setup_monitoring(self) -> None:
        """Setup monitoring and logging."""
        if self.monitoring.performance_metrics:
            # Initialize performance monitoring
            pass
        
        if self.monitoring.health_check_interval > 0:
            # Setup health checks
            pass
    
    @classmethod
    def from_file(cls, config_path: str) -> 'VoiceProcessingConfig':
        """Load configuration from YAML or JSON file."""
        try:
            config_path = Path(config_path)
            
            if not config_path.exists():
                logger.warning(f"Configuration file not found: {config_path}")
                return cls()
            
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            # Convert enum strings back to enums where needed
            config_data = cls._convert_enums_from_strings(config_data)
            
            return cls(**config_data)
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            return cls()  # Return default configuration
    
    def to_file(self, config_path: str, format: str = "yaml") -> None:
        """Save configuration to YAML or JSON file."""
        try:
            config_path = Path(config_path)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dictionary with enum handling
            config_dict = self._to_dict_with_enums()
            
            with open(config_path, 'w', encoding='utf-8') as f:
                if format.lower() == "yaml":
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {config_path}: {e}")
            raise
    
    def _to_dict_with_enums(self) -> Dict[str, Any]:
        """Convert configuration to dictionary with proper enum handling."""
        result = {}
        
        for field_name, field_value in self.__dict__.items():
            if hasattr(field_value, '__dict__'):
                # Nested dataclass
                nested_dict = {}
                for nested_field, nested_value in field_value.__dict__.items():
                    if isinstance(nested_value, Enum):
                        nested_dict[nested_field] = nested_value.value
                    elif isinstance(nested_value, list) and nested_value and isinstance(nested_value[0], Enum):
                        nested_dict[nested_field] = [item.value for item in nested_value]
                    else:
                        nested_dict[nested_field] = nested_value
                result[field_name] = nested_dict
            elif isinstance(field_value, Enum):
                result[field_name] = field_value.value
            elif isinstance(field_value, list) and field_value and isinstance(field_value[0], Enum):
                result[field_name] = [item.value for item in field_value]
            else:
                result[field_name] = field_value
        
        return result
    
    @staticmethod
    def _convert_enums_from_strings(config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert enum strings back to enum objects."""
        # This is a simplified implementation
        # In a full implementation, you'd map specific fields to their enum types
        return config_data
    
    def get_processing_config_hash(self) -> str:
        """Generate a hash of the current processing configuration."""
        config_str = json.dumps(self._to_dict_with_enums(), sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    def validate_audio_file(self, file_path: str) -> Tuple[bool, str]:
        """Validate if an audio file meets configuration requirements."""
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            if file_size_mb > self.max_file_size_mb:
                return False, f"File size {file_size_mb:.1f}MB exceeds limit of {self.max_file_size_mb}MB"
            
            # Additional validation would go here (duration, format, etc.)
            return True, "File validation passed"
            
        except Exception as e:
            return False, f"File validation error: {str(e)}"

# Environment-based configuration loading
def get_voice_processing_config(config_file: Optional[str] = None) -> VoiceProcessingConfig:
    """Get voice processing configuration from file or environment."""
    # Try config file first
    if config_file and os.path.exists(config_file):
        return VoiceProcessingConfig.from_file(config_file)
    
    # Check environment variable for config file
    env_config_file = os.getenv("VOICE_CONFIG_FILE")
    if env_config_file and os.path.exists(env_config_file):
        return VoiceProcessingConfig.from_file(env_config_file)
    
    # Create default configuration with environment overrides
    config = VoiceProcessingConfig()
    
    # Environment variable overrides
    env_overrides = {
        "VOICE_MAX_FILE_SIZE_MB": "max_file_size_mb",
        "VOICE_MAX_DURATION_MINUTES": "max_duration_minutes",
        "VOICE_PROCESSING_TIMEOUT": "processing_timeout_seconds",
        "VOICE_MAX_CONCURRENT": "max_concurrent_requests",
        "VOICE_TEMP_DIR": "temp_directory",
        "VOICE_ENVIRONMENT": "environment"
    }
    
    for env_var, config_attr in env_overrides.items():
        env_value = os.getenv(env_var)
        if env_value:
            try:
                if config_attr.endswith(("_mb", "_minutes", "_seconds", "_requests")):
                    setattr(config, config_attr, int(env_value))
                else:
                    setattr(config, config_attr, env_value)
            except ValueError:
                logger.warning(f"Invalid value for {env_var}: {env_value}")
    
    # Validate API keys and credentials
    required_apis = []
    
    if os.getenv("OPENAI_API_KEY"):
        logger.info("OpenAI API key found")
        required_apis.append("OpenAI")
    
    if os.getenv("GOOGLE_CLOUD_API_KEY"):
        logger.info("Google Cloud API key found")
        required_apis.append("Google Cloud")
    
    if os.getenv("AZURE_SPEECH_KEY"):
        logger.info("Azure Speech key found")
        required_apis.append("Azure Speech")
    
    if os.getenv("AWS_ACCESS_KEY_ID"):
        logger.info("AWS credentials found")
        required_apis.append("AWS")
    
    if required_apis:
        logger.info(f"Available API services: {', '.join(required_apis)}")
    else:
        logger.warning("No API keys found in environment")
    
    return config

# Global configuration instance
voice_config = get_voice_processing_config()
