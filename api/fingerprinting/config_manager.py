"""IA Influencer Agent - Fingerprinting Configuration Manager
Author: Fahed Mlaiel <mlaiel@live.de>

AVERTISSEMENT LÉGAL STRICT:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée 
sans permission écrite expresse est strictement interdite et 
constituera une violation des droits d'auteur.

Configuration management for content fingerprinting system
"""import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FingerprintConfig:
    """    Professional configuration manager for fingerprinting system
    Handles environment variables, config files, and default settings
    """    
    DEFAULT_CONFIG = {
        # Global settings
        'similarity_threshold': 0.85,
        'max_file_size': 100 * 1024 * 1024,  # 100MB
        'batch_size': 50,
        'max_concurrent': 10,
        'enable_parallel_processing': True,
        'duplicate_action': 'flag',  # 'flag', 'block', 'quarantine'
        
        # Database settings
        'database': {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'ia_influencer_fingerprints'),
            'user': os.getenv('DB_USER', 'ia_user'),
            'password': os.getenv('DB_PASSWORD', 'ia_secure_pass'),
            'min_connections': 2,
            'max_connections': 10,
            'command_timeout': 60
        },
        
        # Audio processing settings
        'audio': {
            'sample_rate': 22050,
            'n_mfcc': 13,
            'n_chroma': 12,
            'n_fft': 2048,
            'hop_length': 512,
            'window_size': 1024,
            'similarity_threshold': 0.85
        },
        
        # Video processing settings
        'video': {
            'sample_frames': 30,
            'keyframe_threshold': 0.3,
            'resize_width': 320,
            'resize_height': 240,
            'similarity_threshold': 0.8,
            'hash_size': 16
        },
        
        # Image processing settings
        'image': {
            'resize_width': 512,
            'resize_height': 512,
            'similarity_threshold': 0.85,
            'hash_size': 16,
            'histogram_bins': 64,
            'texture_radius': 3,
            'texture_points': 24
        },
        
        # Text processing settings
        'text': {
            'similarity_threshold': 0.8,
            'max_text_length': 100000,
            'supported_languages': ['en', 'fr', 'de', 'es'],
            'min_words': 10
        },
        
        # Logging settings
        'logging': {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file_path': os.getenv('LOG_FILE_PATH', None)
        },
        
        # Monitoring settings
        'monitoring': {
            'enable_metrics': True,
            'metrics_port': int(os.getenv('METRICS_PORT', '8090')),
            'health_check_interval': 30,
            'performance_tracking': True
        },
        
        # Security settings
        'security': {
            'enable_rate_limiting': True,
            'rate_limit_requests': 1000,
            'rate_limit_window': 3600,  # 1 hour
            'api_key_required': os.getenv('API_KEY_REQUIRED', 'false').lower() == 'true',
            'encrypt_fingerprints': True
        }
    }
    
    def __init__(self, config_file: Optional[Path] = None, config_dict: Optional[Dict[str, Any]] = None):
        """        Initialize configuration manager
        
        Args:
            config_file: Optional path to configuration file
            config_dict: Optional configuration dictionary
        """        self.config = self.DEFAULT_CONFIG.copy()
        
        # Load from file if provided
        if config_file:
            self.load_from_file(config_file)
        
        # Update with provided dictionary
        if config_dict:
            self.update_config(config_dict)
        
        # Apply environment variable overrides
        self._apply_env_overrides()
        
        logger.info("Configuration manager initialized")
    
    def load_from_file(self, config_file: Path):
        """Load configuration from JSON file"""        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                    self.update_config(file_config)
                logger.info(f"Configuration loaded from {config_file}")
            else:
                logger.warning(f"Configuration file not found: {config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration file: {str(e)}")
            raise
    
    def save_to_file(self, config_file: Path):
        """Save current configuration to JSON file"""        try:
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration file: {str(e)}")
            raise
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update configuration with new values"""        def deep_update(base_dict, update_dict):
            for key, value in update_dict.items():
                if isinstance(value, dict) and key in base_dict:
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_update(self.config, new_config)
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides"""        env_mappings = {
            'IA_SIMILARITY_THRESHOLD': ('similarity_threshold', float),
            'IA_MAX_FILE_SIZE': ('max_file_size', int),
            'IA_BATCH_SIZE': ('batch_size', int),
            'IA_MAX_CONCURRENT': ('max_concurrent', int),
            'IA_DUPLICATE_ACTION': ('duplicate_action', str),
            'IA_ENABLE_PARALLEL': ('enable_parallel_processing', lambda x: x.lower() == 'true'),
            
            # Database overrides
            'IA_DB_HOST': ('database.host', str),
            'IA_DB_PORT': ('database.port', int),
            'IA_DB_NAME': ('database.database', str),
            'IA_DB_USER': ('database.user', str),
            'IA_DB_PASSWORD': ('database.password', str),
            'IA_DB_MIN_CONNECTIONS': ('database.min_connections', int),
            'IA_DB_MAX_CONNECTIONS': ('database.max_connections', int),
            
            # Audio overrides
            'IA_AUDIO_SAMPLE_RATE': ('audio.sample_rate', int),
            'IA_AUDIO_N_MFCC': ('audio.n_mfcc', int),
            'IA_AUDIO_SIMILARITY_THRESHOLD': ('audio.similarity_threshold', float),
            
            # Video overrides
            'IA_VIDEO_SAMPLE_FRAMES': ('video.sample_frames', int),
            'IA_VIDEO_SIMILARITY_THRESHOLD': ('video.similarity_threshold', float),
            
            # Image overrides
            'IA_IMAGE_RESIZE_WIDTH': ('image.resize_width', int),
            'IA_IMAGE_RESIZE_HEIGHT': ('image.resize_height', int),
            'IA_IMAGE_SIMILARITY_THRESHOLD': ('image.similarity_threshold', float),
            
            # Text overrides
            'IA_TEXT_SIMILARITY_THRESHOLD': ('text.similarity_threshold', float),
            'IA_TEXT_MAX_LENGTH': ('text.max_text_length', int),
            
            # Security overrides
            'IA_ENABLE_RATE_LIMITING': ('security.enable_rate_limiting', lambda x: x.lower() == 'true'),
            'IA_API_KEY_REQUIRED': ('security.api_key_required', lambda x: x.lower() == 'true'),
            'IA_ENCRYPT_FINGERPRINTS': ('security.encrypt_fingerprints', lambda x: x.lower() == 'true')
        }
        
        for env_var, (config_path, type_converter) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    converted_value = type_converter(env_value)
                    self._set_nested_config(config_path, converted_value)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid value for {env_var}: {env_value}, error: {str(e)}")
    
    def _set_nested_config(self, path: str, value: Any):
        """Set nested configuration value using dot notation"""        keys = path.split('.')
        current = self.config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""        try:
            keys = key.split('.')
            current = self.config
            
            for k in keys:
                current = current[k]
            
            return current
        except (KeyError, TypeError):
            return default
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""        return self.config.get('database', {})
    
    def get_audio_config(self) -> Dict[str, Any]:
        """Get audio processing configuration"""        return self.config.get('audio', {})
    
    def get_video_config(self) -> Dict[str, Any]:
        """Get video processing configuration"""        return self.config.get('video', {})
    
    def get_image_config(self) -> Dict[str, Any]:
        """Get image processing configuration"""        return self.config.get('image', {})
    
    def get_text_config(self) -> Dict[str, Any]:
        """Get text processing configuration"""        return self.config.get('text', {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""        return self.config.get('security', {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""        return self.config.get('monitoring', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""        return self.config.get('logging', {})
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of errors"""        errors = []
        
        # Validate similarity thresholds
        if not 0.0 <= self.get('similarity_threshold', 0) <= 1.0:
            errors.append("similarity_threshold must be between 0.0 and 1.0")
        
        # Validate file size
        if self.get('max_file_size', 0) <= 0:
            errors.append("max_file_size must be positive")
        
        # Validate batch size
        if self.get('batch_size', 0) <= 0:
            errors.append("batch_size must be positive")
        
        # Validate database config
        db_config = self.get_database_config()
        required_db_fields = ['host', 'port', 'database', 'user', 'password']
        for field in required_db_fields:
            if not db_config.get(field):
                errors.append(f"database.{field} is required")
        
        # Validate port numbers
        if not 1 <= db_config.get('port', 0) <= 65535:
            errors.append("database.port must be between 1 and 65535")
        
        # Validate connection pool settings
        min_conn = db_config.get('min_connections', 0)
        max_conn = db_config.get('max_connections', 0)
        if min_conn <= 0 or max_conn <= 0 or min_conn > max_conn:
            errors.append("Invalid database connection pool configuration")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if configuration is valid"""        return len(self.validate_config()) == 0
    
    def get_full_config(self) -> Dict[str, Any]:
        """Get full configuration dictionary"""        return self.config.copy()
    
    def __str__(self) -> str:
        """String representation of configuration"""        # Create a safe copy without sensitive information
        safe_config = self.config.copy()
        if 'database' in safe_config and 'password' in safe_config['database']:
            safe_config['database']['password'] = '***HIDDEN***'
        
        return json.dumps(safe_config, indent=2)

# Global configuration instance
_global_config = None

def get_global_config() -> FingerprintConfig:
    """Get global configuration instance"""    global _global_config
    if _global_config is None:
        _global_config = FingerprintConfig()
    return _global_config

def set_global_config(config: FingerprintConfig):
    """Set global configuration instance"""    global _global_config
    _global_config = config

def load_config_from_file(config_file: Path) -> FingerprintConfig:
    """Load configuration from file and set as global"""    config = FingerprintConfig(config_file=config_file)
    set_global_config(config)
    return config
