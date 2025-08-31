#!/usr/bin/env python3
"""Advanced AI Prompts Configuration Module
Configuration settings for the prompts system

Created by: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de)
Any unauthorized use, copying, or distribution without explicit written permission is strictly prohibited.
Violators will be prosecuted under German and International copyright law.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum

class PromptQualityLevel(Enum):
    """Quality levels for prompt generation"""    BASIC = "basic"
    ADVANCED = "advanced" 
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class ContentFormat(Enum):
    """Supported content formats"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED = "mixed"

class Platform(Enum):
    """Supported platforms"""    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    SOUNDCLOUD = "soundcloud"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"

@dataclass
class PromptsConfig:
    """Main configuration for prompts system"""    
    # Quality settings
    default_quality_level: PromptQualityLevel = PromptQualityLevel.ADVANCED
    min_quality_score: float = 85.0
    max_prompt_length: int = 2000
    
    # Performance settings
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    max_concurrent_generations: int = 10
    
    # AI Model settings
    default_ai_model: str = "gpt-4"
    fallback_ai_model: str = "claude-3-sonnet"
    temperature: float = 0.7
    max_tokens: int = 1500
    
    # Content settings
    supported_languages: List[str] = None
    supported_platforms: List[Platform] = None
    supported_formats: List[ContentFormat] = None
    
    # Security settings
    enable_content_filtering: bool = True
    enable_toxicity_check: bool = True
    enable_bias_detection: bool = True
    
    # Monitoring settings
    enable_metrics: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"

    def __post_init__(self):
        """Initialize default values after object creation"""        if self.supported_languages is None:
            self.supported_languages = ["en", "de", "fr", "es", "it", "pt"]
            
        if self.supported_platforms is None:
            self.supported_platforms = [
                Platform.SPOTIFY, Platform.APPLE_MUSIC, Platform.YOUTUBE,
                Platform.INSTAGRAM, Platform.TIKTOK, Platform.FACEBOOK,
                Platform.TWITTER, Platform.SOUNDCLOUD, Platform.LINKEDIN,
                Platform.TWITCH
            ]
            
        if self.supported_formats is None:
            self.supported_formats = [
                ContentFormat.AUDIO, ContentFormat.VIDEO, 
                ContentFormat.IMAGE, ContentFormat.TEXT, ContentFormat.MIXED
            ]

# Global configuration instance
PROMPTS_CONFIG = PromptsConfig()

# Configuration validation
def validate_config() -> Dict[str, Any]:
    """Validate configuration settings"""    issues = []
    warnings = []
    
    # Validate quality settings
    if PROMPTS_CONFIG.min_quality_score < 0 or PROMPTS_CONFIG.min_quality_score > 100:
        issues.append("min_quality_score must be between 0 and 100")
        
    if PROMPTS_CONFIG.max_prompt_length < 100:
        warnings.append("max_prompt_length is very low, may limit prompt quality")
        
    # Validate AI settings
    if PROMPTS_CONFIG.temperature < 0 or PROMPTS_CONFIG.temperature > 2:
        issues.append("temperature must be between 0 and 2")
        
    if PROMPTS_CONFIG.max_tokens < 50:
        issues.append("max_tokens is too low for quality prompts")
        
    # Validate performance settings
    if PROMPTS_CONFIG.max_concurrent_generations < 1:
        issues.append("max_concurrent_generations must be at least 1")
        
    if PROMPTS_CONFIG.cache_ttl_seconds < 60:
        warnings.append("cache_ttl_seconds is very low, may impact performance")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "config": PROMPTS_CONFIG
    }

# Export configuration constants
__all__ = [
    "PromptsConfig",
    "PromptQualityLevel", 
    "ContentFormat",
    "Platform",
    "PROMPTS_CONFIG",
    "validate_config"
]
