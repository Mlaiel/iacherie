"""⚙️ Audio Processing Configuration - Professional Configuration Management

Centralized configuration system for all audio processing components.
Supports multiple environments, validation, and dynamic updates.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import logging
import os
import json
import yaml
from typing import Dict, List, Optional, Union, Any, Type
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import tempfile

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class AudioProcessingConfig:
    """
    🔧 Comprehensive Audio Processing Configuration
    
    Centralized configuration for all audio processing components:
    - Audio parameters and quality settings
    - Processing preferences and limits
    - Performance and resource management
    - File paths and directories
    - External service configurations
    """
    
    # Environment and general settings
    environment: Environment = Environment.DEVELOPMENT
    debug_mode: bool = True
    log_level: LogLevel = LogLevel.INFO
    temp_directory: Optional[Path] = None
    cache_directory: Optional[Path] = None
    
    # Audio processing parameters
    default_sample_rate: int = 44100
    default_channels: int = 2
    default_bit_depth: int = 16
    max_audio_duration: float = 600.0  # 10 minutes
    max_file_size_mb: float = 100.0
    
    # Quality and performance settings
    processing_quality: str = "high"  # low, medium, high, ultra
    enable_gpu_acceleration: bool = False
    max_cpu_cores: int = 4
    memory_limit_mb: int = 2048
    
    # Audio analysis settings
    fft_size: int = 2048
    hop_length: int = 512
    window_function: str = "hann"
    mel_filters: int = 128
    mfcc_coefficients: int = 13
    
    # Machine learning settings
    ml_model_directory: Optional[Path] = None
    enable_model_caching: bool = True
    model_inference_batch_size: int = 32
    enable_model_quantization: bool = False
    
    # Effects processing settings
    enable_real_time_effects: bool = True
    max_effect_latency_ms: float = 20.0
    effects_quality: str = "high"
    enable_parallel_effects: bool = True
    
    # File format settings
    supported_input_formats: List[str] = None
    supported_output_formats: List[str] = None
    default_output_format: str = "wav"
    
    # Fingerprinting settings
    fingerprint_algorithm: str = "spectral_landmarks"  # spectral_landmarks, chromaprint, etc.
    fingerprint_sample_rate: int = 11025
    fingerprint_duration: float = 30.0  # seconds
    database_url: str = "sqlite:///audio_fingerprints.db"
    
    # Security and copyright settings
    enable_copyright_detection: bool = True
    copyright_threshold: float = 0.85
    enable_watermarking: bool = False
    watermark_strength: float = 0.1
    
    # API and external services
    external_apis: Dict[str, str] = field(default_factory=dict)
    api_timeouts: Dict[str, float] = field(default_factory=lambda: {
        "default": 30.0,
        "ml_inference": 60.0,
        "fingerprinting": 10.0
    })
    
    # Monitoring and logging
    enable_performance_monitoring: bool = True
    metrics_collection_interval: float = 1.0
    log_audio_metadata: bool = True
    log_processing_times: bool = True
    
    # Advanced settings
    enable_experimental_features: bool = False
    custom_parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize derived settings after object creation"""
        # Initialize lists if None
        if self.supported_input_formats is None:
            self.supported_input_formats = [
                "wav", "mp3", "flac", "aac", "ogg", "m4a", "aiff", "wma"
            ]
        
        if self.supported_output_formats is None:
            self.supported_output_formats = [
                "wav", "mp3", "flac", "aac", "ogg", "m4a"
            ]
        
        if self.custom_parameters is None:
            self.custom_parameters = {}
        
        # Set default directories if not provided
        if self.temp_directory is None:
            self.temp_directory = Path(tempfile.gettempdir()) / "audio_processing"
        
        if self.cache_directory is None:
            self.cache_directory = self.temp_directory / "cache"
        
        if self.ml_model_directory is None:
            self.ml_model_directory = Path.cwd() / "models"
        
        # Ensure directories exist
        self.temp_directory.mkdir(parents=True, exist_ok=True)
        self.cache_directory.mkdir(parents=True, exist_ok=True)
        self.ml_model_directory.mkdir(parents=True, exist_ok=True)
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration parameters"""
        # Validate sample rate
        if self.default_sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        
        # Validate channels
        if self.default_channels not in [1, 2]:
            raise ValueError("Channels must be 1 (mono) or 2 (stereo)")
        
        # Validate bit depth
        if self.default_bit_depth not in [16, 24, 32]:
            raise ValueError("Bit depth must be 16, 24, or 32")
        
        # Validate file size limits
        if self.max_file_size_mb <= 0:
            raise ValueError("Max file size must be positive")
        
        # Validate processing quality
        if self.processing_quality not in ["low", "medium", "high", "ultra"]:
            raise ValueError("Processing quality must be low, medium, high, or ultra")
        
        # Validate FFT parameters
        if self.fft_size <= 0 or (self.fft_size & (self.fft_size - 1)) != 0:
            raise ValueError("FFT size must be a positive power of 2")
        
        if self.hop_length <= 0:
            raise ValueError("Hop length must be positive")
        
        # Validate ML parameters
        if self.model_inference_batch_size <= 0:
            raise ValueError("Model inference batch size must be positive")
        
        # Validate format lists
        if not self.supported_input_formats:
            raise ValueError("At least one input format must be supported")
        
        if self.default_output_format not in self.supported_output_formats:
            raise ValueError("Default output format must be in supported output formats")
    
    def get_quality_parameters(self) -> Dict[str, Any]:
        """Get quality-specific parameters"""
        quality_params = {
            "low": {
                "fft_size": 1024,
                "hop_length": 512,
                "mel_filters": 64,
                "mfcc_coefficients": 12,
                "sample_rate": 22050
            },
            "medium": {
                "fft_size": 2048,
                "hop_length": 512,
                "mel_filters": 128,
                "mfcc_coefficients": 13,
                "sample_rate": 44100
            },
            "high": {
                "fft_size": 4096,
                "hop_length": 512,
                "mel_filters": 256,
                "mfcc_coefficients": 13,
                "sample_rate": 44100
            },
            "ultra": {
                "fft_size": 8192,
                "hop_length": 256,
                "mel_filters": 512,
                "mfcc_coefficients": 13,
                "sample_rate": 48000
            }
        }
        
        return quality_params.get(self.processing_quality, quality_params["high"])
    
    def get_memory_limits(self) -> Dict[str, int]:
        """Get memory limits for different components"""
        total_memory = self.memory_limit_mb
        
        return {
            "audio_processing": int(total_memory * 0.4),  # 40%
            "ml_models": int(total_memory * 0.3),         # 30%
            "effects_processing": int(total_memory * 0.2), # 20%
            "cache": int(total_memory * 0.1)              # 10%
        }
    
    def get_cpu_allocation(self) -> Dict[str, int]:
        """Get CPU core allocation for different components"""
        total_cores = min(self.max_cpu_cores, os.cpu_count() or 1)
        
        if total_cores == 1:
            return {
                "audio_processing": 1,
                "ml_inference": 1,
                "effects_processing": 1,
                "background_tasks": 1
            }
        elif total_cores == 2:
            return {
                "audio_processing": 1,
                "ml_inference": 1,
                "effects_processing": 1,
                "background_tasks": 1
            }
        else:
            return {
                "audio_processing": max(1, total_cores // 2),
                "ml_inference": max(1, total_cores // 4),
                "effects_processing": max(1, total_cores // 4),
                "background_tasks": 1
            }
    
    def is_format_supported(self, format_name: str, input_format: bool = True) -> bool:
        """Check if a format is supported"""
        format_name = format_name.lower().lstrip('.')
        
        if input_format:
            return format_name in self.supported_input_formats
        else:
            return format_name in self.supported_output_formats
    
    def get_api_timeout(self, api_name: str) -> float:
        """Get timeout for specific API"""
        return self.api_timeouts.get(api_name, self.api_timeouts.get("default", 30.0))
    
    def update_parameter(self, parameter_path: str, value: Any):
        """Update a configuration parameter dynamically"""
        keys = parameter_path.split('.')
        obj = self
        
        # Navigate to the parent object
        for key in keys[:-1]:
            if hasattr(obj, key):
                obj = getattr(obj, key)
            else:
                raise KeyError(f"Parameter path not found: {parameter_path}")
        
        # Set the final value
        final_key = keys[-1]
        if hasattr(obj, final_key):
            setattr(obj, final_key, value)
            logger.info(f"Updated parameter {parameter_path} = {value}")
        else:
            raise KeyError(f"Parameter not found: {parameter_path}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        config_dict = {}
        
        for key, value in self.__dict__.items():
            if isinstance(value, (Path, Enum)):
                config_dict[key] = str(value)
            elif isinstance(value, (list, dict)):
                config_dict[key] = value.copy()
            else:
                config_dict[key] = value
        
        return config_dict
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AudioProcessingConfig':
        """Create configuration from dictionary"""
        # Convert string paths back to Path objects
        for key in ['temp_directory', 'cache_directory', 'ml_model_directory']:
            if key in config_dict and config_dict[key] is not None:
                config_dict[key] = Path(config_dict[key])
        
        # Convert string enums back to enum objects
        if 'environment' in config_dict:
            config_dict['environment'] = Environment(config_dict['environment'])
        
        if 'log_level' in config_dict:
            config_dict['log_level'] = LogLevel(config_dict['log_level'])
        
        return cls(**config_dict)
    
    def save_to_file(self, file_path: Union[str, Path]):
        """Save configuration to file"""
        file_path = Path(file_path)
        config_dict = self.to_dict()
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
        elif file_path.suffix.lower() in ['.yml', '.yaml']:
            with open(file_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        logger.info(f"Configuration saved to {file_path}")
    
    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> 'AudioProcessingConfig':
        """Load configuration from file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'r') as f:
                config_dict = json.load(f)
        elif file_path.suffix.lower() in ['.yml', '.yaml']:
            with open(file_path, 'r') as f:
                config_dict = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        logger.info(f"Configuration loaded from {file_path}")
        return cls.from_dict(config_dict)


class ConfigurationManager:
    """
    🔧 Configuration Manager
    
    Advanced configuration management system:
    - Environment-specific configurations
    - Configuration validation and merging
    - Dynamic configuration updates
    - Configuration templates and presets
    """
    
    def __init__(self, config_directory: Optional[Path] = None):
        self.config_directory = config_directory or Path.cwd() / "config"
        self.config_directory.mkdir(parents=True, exist_ok=True)
        
        # Current configuration
        self.current_config: Optional[AudioProcessingConfig] = None
        
        # Configuration templates
        self.templates = self._initialize_templates()
        
        logger.info(f"ConfigurationManager initialized with directory: {self.config_directory}")
    
    def _initialize_templates(self) -> Dict[str, AudioProcessingConfig]:
        """Initialize configuration templates"""
        templates = {}
        
        # Development template
        templates['development'] = AudioProcessingConfig(
            environment=Environment.DEVELOPMENT,
            debug_mode=True,
            log_level=LogLevel.DEBUG,
            processing_quality="medium",
            enable_gpu_acceleration=False,
            max_cpu_cores=2,
            memory_limit_mb=1024,
            enable_performance_monitoring=True,
            enable_experimental_features=True
        )
        
        # Testing template
        templates['testing'] = AudioProcessingConfig(
            environment=Environment.TESTING,
            debug_mode=True,
            log_level=LogLevel.INFO,
            processing_quality="low",
            enable_gpu_acceleration=False,
            max_cpu_cores=1,
            memory_limit_mb=512,
            enable_performance_monitoring=False,
            enable_experimental_features=False
        )
        
        # Production template
        templates['production'] = AudioProcessingConfig(
            environment=Environment.PRODUCTION,
            debug_mode=False,
            log_level=LogLevel.WARNING,
            processing_quality="high",
            enable_gpu_acceleration=True,
            max_cpu_cores=8,
            memory_limit_mb=4096,
            enable_performance_monitoring=True,
            enable_experimental_features=False
        )
        
        # High-performance template
        templates['high_performance'] = AudioProcessingConfig(
            environment=Environment.PRODUCTION,
            debug_mode=False,
            log_level=LogLevel.ERROR,
            processing_quality="ultra",
            enable_gpu_acceleration=True,
            max_cpu_cores=16,
            memory_limit_mb=8192,
            enable_performance_monitoring=True,
            enable_parallel_effects=True,
            enable_model_caching=True,
            enable_model_quantization=True
        )
        
        # Streaming template
        templates['streaming'] = AudioProcessingConfig(
            environment=Environment.PRODUCTION,
            debug_mode=False,
            log_level=LogLevel.INFO,
            processing_quality="medium",
            enable_real_time_effects=True,
            max_effect_latency_ms=10.0,
            enable_gpu_acceleration=True,
            max_cpu_cores=4,
            memory_limit_mb=2048,
            default_sample_rate=48000,
            enable_performance_monitoring=True
        )
        
        return templates
    
    def get_template(self, template_name: str) -> AudioProcessingConfig:
        """Get a configuration template"""
        if template_name not in self.templates:
            available = list(self.templates.keys())
            raise ValueError(f"Template '{template_name}' not found. Available: {available}")
        
        return self.templates[template_name]
    
    def create_config_from_template(self, 
                                  template_name: str,
                                  overrides: Optional[Dict[str, Any]] = None) -> AudioProcessingConfig:
        """Create configuration from template with optional overrides"""
        base_config = self.get_template(template_name)
        config_dict = base_config.to_dict()
        
        # Apply overrides
        if overrides:
            config_dict.update(overrides)
        
        return AudioProcessingConfig.from_dict(config_dict)
    
    def load_config(self, 
                   config_name: str = "default",
                   environment: Optional[Environment] = None) -> AudioProcessingConfig:
        """Load configuration from file"""
        if environment:
            config_file = self.config_directory / f"{config_name}_{environment.value}.yaml"
        else:
            config_file = self.config_directory / f"{config_name}.yaml"
        
        if config_file.exists():
            self.current_config = AudioProcessingConfig.load_from_file(config_file)
        else:
            # Use default template for environment
            template_name = environment.value if environment else "development"
            if template_name in self.templates:
                self.current_config = self.get_template(template_name)
            else:
                self.current_config = self.get_template("development")
            
            # Save the default configuration
            self.save_config(config_name, environment)
        
        logger.info(f"Loaded configuration: {config_name} ({self.current_config.environment.value})")
        return self.current_config
    
    def save_config(self, 
                   config_name: str = "default",
                   environment: Optional[Environment] = None,
                   config: Optional[AudioProcessingConfig] = None):
        """Save configuration to file"""
        if config is None:
            config = self.current_config
        
        if config is None:
            raise ValueError("No configuration to save")
        
        if environment:
            config_file = self.config_directory / f"{config_name}_{environment.value}.yaml"
        else:
            config_file = self.config_directory / f"{config_name}.yaml"
        
        config.save_to_file(config_file)
    
    def merge_configs(self, 
                     base_config: AudioProcessingConfig,
                     override_config: AudioProcessingConfig) -> AudioProcessingConfig:
        """Merge two configurations, with override taking precedence"""
        base_dict = base_config.to_dict()
        override_dict = override_config.to_dict()
        
        # Merge dictionaries
        merged_dict = {**base_dict, **override_dict}
        
        return AudioProcessingConfig.from_dict(merged_dict)
    
    def validate_config(self, config: AudioProcessingConfig) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        try:
            # Basic validation is done in __post_init__
            config._validate_config()
        except ValueError as e:
            issues.append(str(e))
        
        # Additional environment-specific validation
        if config.environment == Environment.PRODUCTION:
            if config.debug_mode:
                issues.append("Debug mode should be disabled in production")
            
            if config.log_level in [LogLevel.DEBUG]:
                issues.append("Log level should not be DEBUG in production")
            
            if config.enable_experimental_features:
                issues.append("Experimental features should be disabled in production")
        
        # Performance validation
        if config.memory_limit_mb < 512:
            issues.append("Memory limit may be too low for reliable operation")
        
        if config.max_cpu_cores > (os.cpu_count() or 1):
            issues.append(f"Max CPU cores ({config.max_cpu_cores}) exceeds available cores ({os.cpu_count()})")
        
        # File system validation
        if not config.temp_directory.exists():
            try:
                config.temp_directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                issues.append(f"Cannot create temp directory: {e}")
        
        return issues
    
    def get_environment_config(self, environment: Environment) -> AudioProcessingConfig:
        """Get configuration for specific environment"""
        return self.load_config("default", environment)
    
    def list_available_configs(self) -> List[str]:
        """List available configuration files"""
        config_files = []
        
        for file_path in self.config_directory.glob("*.yaml"):
            config_files.append(file_path.stem)
        
        for file_path in self.config_directory.glob("*.json"):
            config_files.append(file_path.stem)
        
        return sorted(list(set(config_files)))
    
    def get_current_config(self) -> Optional[AudioProcessingConfig]:
        """Get current configuration"""
        return self.current_config
    
    def set_current_config(self, config: AudioProcessingConfig):
        """Set current configuration"""
        self.current_config = config
        logger.info(f"Current configuration set to {config.environment.value} mode")


# Global configuration manager instance
_config_manager = ConfigurationManager()


def get_config() -> AudioProcessingConfig:
    """Get current audio processing configuration"""
    config = _config_manager.get_current_config()
    if config is None:
        # Load default configuration
        config = _config_manager.load_config()
    return config


def set_config(config: AudioProcessingConfig):
    """Set current audio processing configuration"""
    _config_manager.set_current_config(config)


def load_config(config_name: str = "default", 
               environment: Optional[Environment] = None) -> AudioProcessingConfig:
    """Load configuration from file"""
    return _config_manager.load_config(config_name, environment)


def save_config(config: AudioProcessingConfig,
               config_name: str = "default",
               environment: Optional[Environment] = None):
    """Save configuration to file"""
    _config_manager.save_config(config_name, environment, config)


def get_template(template_name: str) -> AudioProcessingConfig:
    """Get configuration template"""
    return _config_manager.get_template(template_name)


def create_config_from_template(template_name: str,
                               overrides: Optional[Dict[str, Any]] = None) -> AudioProcessingConfig:
    """Create configuration from template"""
    return _config_manager.create_config_from_template(template_name, overrides)


# Environment detection
def detect_environment() -> Environment:
    """Detect current environment from environment variables"""
    env_name = os.getenv('AUDIO_PROCESSING_ENV', 'development').lower()
    
    env_mapping = {
        'dev': Environment.DEVELOPMENT,
        'development': Environment.DEVELOPMENT,
        'test': Environment.TESTING,
        'testing': Environment.TESTING,
        'stage': Environment.STAGING,
        'staging': Environment.STAGING,
        'prod': Environment.PRODUCTION,
        'production': Environment.PRODUCTION
    }
    
    return env_mapping.get(env_name, Environment.DEVELOPMENT)


def initialize_config(environment: Optional[Environment] = None) -> AudioProcessingConfig:
    """Initialize configuration for current environment"""
    if environment is None:
        environment = detect_environment()
    
    config = _config_manager.load_config("default", environment)
    
    # Apply environment variable overrides
    env_overrides = {}
    
    # Sample rate override
    if os.getenv('AUDIO_SAMPLE_RATE'):
        try:
            env_overrides['default_sample_rate'] = int(os.getenv('AUDIO_SAMPLE_RATE'))
        except ValueError:
            logger.warning("Invalid AUDIO_SAMPLE_RATE environment variable")
    
    # Memory limit override
    if os.getenv('AUDIO_MEMORY_LIMIT_MB'):
        try:
            env_overrides['memory_limit_mb'] = int(os.getenv('AUDIO_MEMORY_LIMIT_MB'))
        except ValueError:
            logger.warning("Invalid AUDIO_MEMORY_LIMIT_MB environment variable")
    
    # CPU cores override
    if os.getenv('AUDIO_MAX_CPU_CORES'):
        try:
            env_overrides['max_cpu_cores'] = int(os.getenv('AUDIO_MAX_CPU_CORES'))
        except ValueError:
            logger.warning("Invalid AUDIO_MAX_CPU_CORES environment variable")
    
    # Apply overrides
    if env_overrides:
        config_dict = config.to_dict()
        config_dict.update(env_overrides)
        config = AudioProcessingConfig.from_dict(config_dict)
    
    _config_manager.set_current_config(config)
    
    logger.info(f"Configuration initialized for {environment.value} environment")
    return config
