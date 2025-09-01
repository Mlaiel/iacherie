"""Quality Assessment Configuration

Advanced configuration settings and constants for the quality assessment module.
Provides customizable thresholds, parameters, and platform-specific settings.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class ConfigurationLevel(Enum):
    """
Configuration complexity levels"""

    BASIC = "basic"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class QualityThresholds:
    """Quality assessment thresholds configuration"""
    
    # Audio quality thresholds
    audio_thresholds: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'professional': {
            'sample_rate_min': 48000,
            'bit_depth_min': 24,
            'thd_max': 0.05,  # Total Harmonic Distortion
            'snr_min': 90,    # Signal-to-Noise Ratio (dB)
            'dynamic_range_min': 20,
            'lufs_target': -16,  # Loudness Units Full Scale
            'true_peak_max': -1.0
        },
        'broadcast': {
            'sample_rate_min': 48000,
            'bit_depth_min': 24,
            'thd_max': 0.1,
            'snr_min': 80,
            'dynamic_range_min': 15,
            'lufs_target': -23,
            'true_peak_max': -1.0
        },
        'streaming': {
            'sample_rate_min': 44100,
            'bit_depth_min': 16,
            'thd_max': 0.5,
            'snr_min': 70,
            'dynamic_range_min': 12,
            'lufs_target': -14,
            'true_peak_max': -1.0
        },
        'social_media': {
            'sample_rate_min': 44100,
            'bit_depth_min': 16,
            'thd_max': 1.0,
            'snr_min': 60,
            'dynamic_range_min': 10,
            'lufs_target': -16,
            'true_peak_max': -1.0
        }
    })
    
    # Video quality thresholds
    video_thresholds: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'professional': {
            'resolution_min': (3840, 2160),  # 4K UHD
            'bitrate_min': 50000,  # kbps
            'frame_rate_min': 24,
            'frame_rate_max': 60,
            'codec_preferred': ['h264', 'h265', 'av1'],
            'color_depth_min': 10,
            'noise_level_max': 5.0,
            'sharpness_min': 80.0,
            'contrast_min': 70.0
        },
        'broadcast': {
            'resolution_min': (1920, 1080),  # Full HD
            'bitrate_min': 25000,
            'frame_rate_min': 24,
            'frame_rate_max': 60,
            'codec_preferred': ['h264', 'h265'],
            'color_depth_min': 8,
            'noise_level_max': 10.0,
            'sharpness_min': 70.0,
            'contrast_min': 60.0
        },
        'streaming': {
            'resolution_min': (1920, 1080),
            'bitrate_min': 8000,
            'frame_rate_min': 24,
            'frame_rate_max': 60,
            'codec_preferred': ['h264'],
            'color_depth_min': 8,
            'noise_level_max': 15.0,
            'sharpness_min': 60.0,
            'contrast_min': 50.0
        },
        'social_media': {
            'resolution_min': (1280, 720),  # HD
            'bitrate_min': 3000,
            'frame_rate_min': 24,
            'frame_rate_max': 60,
            'codec_preferred': ['h264'],
            'color_depth_min': 8,
            'noise_level_max': 20.0,
            'sharpness_min': 50.0,
            'contrast_min': 40.0
        }
    })
    
    # Image quality thresholds
    image_thresholds: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'professional': {
            'resolution_min': (4000, 3000),
            'dpi_min': 300,
            'compression_quality_min': 98,
            'color_depth_min': 8,
            'sharpness_min': 90.0,
            'noise_level_max': 2.0,
            'dynamic_range_min': 80.0,
            'color_accuracy_min': 95.0
        },
        'commercial': {
            'resolution_min': (2000, 1500),
            'dpi_min': 300,
            'compression_quality_min': 95,
            'color_depth_min': 8,
            'sharpness_min': 80.0,
            'noise_level_max': 5.0,
            'dynamic_range_min': 70.0,
            'color_accuracy_min': 90.0
        },
        'web': {
            'resolution_min': (1920, 1080),
            'dpi_min': 72,
            'compression_quality_min': 85,
            'color_depth_min': 8,
            'sharpness_min': 70.0,
            'noise_level_max': 10.0,
            'dynamic_range_min': 60.0,
            'color_accuracy_min': 85.0
        },
        'social_media': {
            'resolution_min': (1080, 1080),
            'dpi_min': 72,
            'compression_quality_min': 80,
            'color_depth_min': 8,
            'sharpness_min': 60.0,
            'noise_level_max': 15.0,
            'dynamic_range_min': 50.0,
            'color_accuracy_min': 80.0
        }
    })
    
    # Text quality thresholds
    text_thresholds: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'professional': {
            'flesch_kincaid_min': 8.0,
            'flesch_reading_ease_min': 60.0,
            'grammar_accuracy_min': 98.0,
            'spelling_accuracy_min': 99.5,
            'sentiment_neutrality_min': -0.1,
            'keyword_density_max': 3.0,
            'readability_score_min': 80.0,
            'engagement_potential_min': 70.0
        },
        'commercial': {
            'flesch_kincaid_min': 6.0,
            'flesch_reading_ease_min': 50.0,
            'grammar_accuracy_min': 95.0,
            'spelling_accuracy_min': 98.0,
            'sentiment_neutrality_min': -0.2,
            'keyword_density_max': 4.0,
            'readability_score_min': 70.0,
            'engagement_potential_min': 60.0
        },
        'social_media': {
            'flesch_kincaid_min': 4.0,
            'flesch_reading_ease_min': 40.0,
            'grammar_accuracy_min': 90.0,
            'spelling_accuracy_min': 95.0,
            'sentiment_neutrality_min': -0.3,
            'keyword_density_max': 5.0,
            'readability_score_min': 60.0,
            'engagement_potential_min': 50.0
        }
    })


@dataclass
class PlatformConfiguration:
    """
Platform-specific configuration settings"""
    
    platform_specs: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'youtube': {
            'video': {
                'max_duration': 43200,  # 12 hours in seconds
                'recommended_resolution': [(1920, 1080), (3840, 2160)],
                'recommended_bitrate': {'1080p': 8000, '4k': 35000},
                'recommended_framerate': [24, 30, 60],
                'max_file_size': 256 * 1024 * 1024 * 1024,  # 256GB
                'supported_formats': ['mp4', 'mov', 'avi', 'wmv', 'flv', 'webm'],
                'audio_codec': ['aac', 'mp3'],
                'video_codec': ['h264', 'h265', 'av1']
            },
            'thumbnail': {
                'resolution': (1280, 720),
                'max_file_size': 2 * 1024 * 1024,  # 2MB
                'formats': ['jpg', 'png', 'gif', 'bmp']
            },
            'seo_requirements': {
                'title_length_max': 100,
                'description_length_max': 5000,
                'tags_max': 500,
                'keywords_density_optimal': 2.5
            }
        },
        'instagram': {
            'image': {
                'feed_resolution': (1080, 1080),
                'story_resolution': (1080, 1920),
                'max_file_size': 30 * 1024 * 1024,  # 30MB
                'supported_formats': ['jpg', 'png'],
                'aspect_ratios': [(1, 1), (4, 5), (16, 9)]
            },
            'video': {
                'feed_duration_max': 60,
                'story_duration_max': 15,
                'reel_duration_max': 90,
                'resolution': [(1080, 1080), (1080, 1920)],
                'max_file_size': 4 * 1024 * 1024 * 1024,  # 4GB
                'supported_formats': ['mp4', 'mov'],
                'frame_rate': [23, 30]
            },
            'caption_limits': {
                'max_length': 2200,
                'hashtags_max': 30,
                'mentions_max': 20
            }
        },
        'tiktok': {
            'video': {
                'duration_min': 15,
                'duration_max': 600,  # 10 minutes
                'resolution': (1080, 1920),
                'aspect_ratio': (9, 16),
                'max_file_size': 4 * 1024 * 1024 * 1024,  # 4GB
                'supported_formats': ['mp4', 'mov'],
                'frame_rate': [25, 30],
                'bitrate_recommended': 1500  # kbps
            },
            'audio': {
                'max_duration': 600,
                'supported_formats': ['mp3', 'wav', 'aac'],
                'sample_rate': [44100, 48000],
                'bitrate': 128  # kbps
            },
            'caption_limits': {
                'max_length': 2200,
                'hashtags_recommended': 3-5
            }
        },
        'twitter': {
            'image': {
                'single_image': (1200, 675),
                'multiple_images': (1200, 600),
                'max_file_size': 5 * 1024 * 1024,  # 5MB
                'supported_formats': ['jpg', 'png', 'gif', 'webp']
            },
            'video': {
                'duration_max': 140,
                'resolution_max': (1920, 1080),
                'max_file_size': 512 * 1024 * 1024,  # 512MB
                'supported_formats': ['mp4', 'mov'],
                'frame_rate_max': 40
            },
            'text_limits': {
                'tweet_length': 280,
                'thread_max': 25
            }
        },
        'linkedin': {
            'image': {
                'feed_resolution': (1200, 627),
                'max_file_size': 5 * 1024 * 1024,  # 5MB
                'supported_formats': ['jpg', 'png', 'gif']
            },
            'video': {
                'duration_max': 600,  # 10 minutes
                'resolution_max': (1920, 1080),
                'max_file_size': 5 * 1024 * 1024 * 1024,  # 5GB
                'supported_formats': ['mp4', 'avi', 'mov', 'wmv']
            },
            'content_guidelines': {
                'professional_tone': True,
                'business_focus': True,
                'networking_oriented': True
            }
        }
    })


@dataclass
class ProcessingConfiguration:
    """
Processing and performance configuration"""
    
    # Performance settings
    max_workers: int = field(default=8)
    use_gpu: bool = field(default=True)
    gpu_memory_limit: str = field(default="4GB")
    cache_enabled: bool = field(default=True)
    cache_size_mb: int = field(default=1024)
    
    # Processing timeouts (seconds)
    audio_processing_timeout: int = field(default=300)
    video_processing_timeout: int = field(default=600)
    image_processing_timeout: int = field(default=120)
    text_processing_timeout: int = field(default=60)
    
    # Quality analysis settings
    spectral_analysis_window_size: int = field(default=2048)
    spectral_analysis_hop_length: int = field(default=512)
    mfcc_coefficients: int = field(default=13)
    
    # Video analysis settings
    frame_sampling_rate: float = field(default=1.0)  # frames per second
    motion_detection_threshold: float = field(default=10.0)
    scene_change_threshold: float = field(default=0.3)
    
    # Image analysis settings
    color_histogram_bins: int = field(default=256)
    edge_detection_threshold: Tuple[int, int] = field(default=(50, 150))
    corner_detection_quality: float = field(default=0.01)
    
    # Text analysis settings
    sentiment_model: str = field(default="bert-base-uncased")
    grammar_check_enabled: bool = field(default=True)
    spelling_check_enabled: bool = field(default=True)
    seo_analysis_enabled: bool = field(default=True)


@dataclass
class MonitoringConfiguration:
    """Monitoring and logging configuration"""
    
    # Logging settings
    log_level: str = field(default="INFO")
    log_file_path: str = field(default="logs/quality_assessment.log")
    log_rotation_size: str = field(default="100MB")
    log_retention_days: int = field(default=30)
    
    # Performance monitoring
    performance_tracking_enabled: bool = field(default=True)
    metrics_collection_enabled: bool = field(default=True)
    error_reporting_enabled: bool = field(default=True)
    
    # Alerting settings
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'processing_time_warning': 30.0,  # seconds
        'processing_time_critical': 60.0,
        'memory_usage_warning': 80.0,  # percentage
        'memory_usage_critical': 95.0,
        'error_rate_warning': 5.0,  # percentage
        'error_rate_critical': 15.0
    })


@dataclass
class SecurityConfiguration:
    """Security and compliance configuration"""
    
    # Content validation
    malware_scanning_enabled: bool = field(default=True)
    content_safety_checking: bool = field(default=True)
    copyright_detection: bool = field(default=True)
    
    # Privacy protection
    personal_data_detection: bool = field(default=True)
    face_detection_blur: bool = field(default=False)
    audio_privacy_filtering: bool = field(default=True)
    
    # Compliance requirements
    gdpr_compliance: bool = field(default=True)
    ccpa_compliance: bool = field(default=True)
    coppa_compliance: bool = field(default=True)
    
    # Data retention
    analysis_data_retention_days: int = field(default=90)
    processed_content_retention_days: int = field(default=30)
    logs_retention_days: int = field(default=365)


class QualityAssessmentConfig:
    """
Main configuration class for Quality Assessment Module"""
    
    def __init__(self, config_level: ConfigurationLevel = ConfigurationLevel.ADVANCED):
        self.config_level = config_level
        self.thresholds = QualityThresholds()
        self.platforms = PlatformConfiguration()
        self.processing = ProcessingConfiguration()
        self.monitoring = MonitoringConfiguration()
        self.security = SecurityConfiguration()
        
        # Apply configuration level adjustments
        self._apply_config_level_settings()
    
    def _apply_config_level_settings(self):
        """
Apply configuration based on complexity level"""
        if self.config_level == ConfigurationLevel.BASIC:
            self.processing.max_workers = 4
            self.processing.use_gpu = False
            self.monitoring.performance_tracking_enabled = False
            self.security.malware_scanning_enabled = False
            
        elif self.config_level == ConfigurationLevel.PROFESSIONAL:
            self.processing.max_workers = 12
            self.processing.cache_size_mb = 2048
            self.monitoring.metrics_collection_enabled = True
            
        elif self.config_level == ConfigurationLevel.ENTERPRISE:
            self.processing.max_workers = 24
            self.processing.cache_size_mb = 4096
            self.monitoring.error_reporting_enabled = True
            self.security.content_safety_checking = True
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert configuration to dictionary"""
        return {
            'config_level': self.config_level.value,
            'thresholds': {
                'audio': self.thresholds.audio_thresholds,
                'video': self.thresholds.video_thresholds,
                'image': self.thresholds.image_thresholds,
                'text': self.thresholds.text_thresholds
            },
            'platforms': self.platforms.platform_specs,
            'processing': {
                'max_workers': self.processing.max_workers,
                'use_gpu': self.processing.use_gpu,
                'cache_enabled': self.processing.cache_enabled,
                'timeouts': {
                    'audio': self.processing.audio_processing_timeout,
                    'video': self.processing.video_processing_timeout,
                    'image': self.processing.image_processing_timeout,
                    'text': self.processing.text_processing_timeout
                }
            },
            'monitoring': {
                'log_level': self.monitoring.log_level,
                'performance_tracking': self.monitoring.performance_tracking_enabled,
                'metrics_collection': self.monitoring.metrics_collection_enabled
            },
            'security': {
                'content_validation': self.security.malware_scanning_enabled,
                'privacy_protection': self.security.personal_data_detection,
                'compliance': {
                    'gdpr': self.security.gdpr_compliance,
                    'ccpa': self.security.ccpa_compliance
                }
            }
        }
    
    def save_to_file(self, file_path: str):
        """
Save configuration to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'QualityAssessmentConfig':
        """
Load configuration from JSON file"""
        with open(file_path, 'r') as f:
            config_data = json.load(f)
        
        config_level = ConfigurationLevel(config_data.get('config_level', 'advanced'))
        instance = cls(config_level)
        
        # Apply loaded settings
        if 'processing' in config_data:
            proc_config = config_data['processing']
            instance.processing.max_workers = proc_config.get('max_workers', 8)
            instance.processing.use_gpu = proc_config.get('use_gpu', True)
            instance.processing.cache_enabled = proc_config.get('cache_enabled', True)
        
        return instance


# Default configuration instances
DEFAULT_CONFIG = QualityAssessmentConfig(ConfigurationLevel.ADVANCED)
BASIC_CONFIG = QualityAssessmentConfig(ConfigurationLevel.BASIC)
PROFESSIONAL_CONFIG = QualityAssessmentConfig(ConfigurationLevel.PROFESSIONAL)
ENTERPRISE_CONFIG = QualityAssessmentConfig(ConfigurationLevel.ENTERPRISE)


# Export configuration constants
__all__ = [
    'QualityAssessmentConfig',
    'QualityThresholds',
    'PlatformConfiguration',
    'ProcessingConfiguration',
    'MonitoringConfiguration',
    'SecurityConfiguration',
    'ConfigurationLevel',
    'DEFAULT_CONFIG',
    'BASIC_CONFIG',
    'PROFESSIONAL_CONFIG',
    'ENTERPRISE_CONFIG'
]
