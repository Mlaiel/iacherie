# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Advanced Prompts Configuration Tests
Ultra-professional test suite for Prompts Configuration system

Created by: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de)
Any unauthorized use, copying, or distribution without explicit written permission is strictly prohibited.
Violators will be prosecuted under German and International copyright law.
"""import pytest
import sys
import os
from pathlib import Path
import asyncio
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

from ai.prompts.prompts_config import (
    PromptsConfig, PromptQualityLevel, ContentFormat, Platform,
    PROMPTS_CONFIG, validate_config
)


class TestPromptsConfig:
    """Ultra-comprehensive test suite for Prompts Configuration"""    
    @pytest.fixture
    def fresh_config(self):
        """Create a fresh PromptsConfig instance for each test"""        config = PromptsConfig()
        return config
    
    @pytest.fixture
    def custom_config(self):
        """Create a custom configuration for testing"""        return PromptsConfig(
            default_quality_level=PromptQualityLevel.ENTERPRISE,
            min_quality_score=90.0,
            max_prompt_length=2500,
            cache_enabled=True,
            cache_ttl_seconds=7200,
            max_concurrent_generations=15,
            default_ai_model="gpt-4-turbo",
            fallback_ai_model="claude-3-opus",
            temperature=0.8,
            max_tokens=2000,
            supported_languages=["en", "de", "fr", "es", "it", "pt", "ja", "ko"],
            enable_content_filtering=True,
            enable_toxicity_check=True,
            enable_bias_detection=True,
            enable_metrics=True,
            enable_logging=True,
            log_level="DEBUG"
        )
    
    @pytest.fixture
    def minimal_config(self):
        """Create a minimal configuration for testing"""        return PromptsConfig(
            default_quality_level=PromptQualityLevel.BASIC,
            min_quality_score=60.0,
            max_prompt_length=500,
            cache_enabled=False,
            max_concurrent_generations=1,
            temperature=0.3,
            max_tokens=500,
            enable_content_filtering=False,
            enable_toxicity_check=False,
            enable_bias_detection=False,
            enable_metrics=False,
            enable_logging=False
        )
    
    # ===== INITIALIZATION TESTS =====
    
    def test_config_initialization_default(self, fresh_config):
        """Test default configuration initialization"""        assert fresh_config.default_quality_level == PromptQualityLevel.ADVANCED
        assert fresh_config.min_quality_score == 85.0
        assert fresh_config.max_prompt_length == 2000
        assert fresh_config.cache_enabled is True
        assert fresh_config.cache_ttl_seconds == 3600
        assert fresh_config.max_concurrent_generations == 10
        assert fresh_config.default_ai_model == "gpt-4"
        assert fresh_config.fallback_ai_model == "claude-3-sonnet"
        assert fresh_config.temperature == 0.7
        assert fresh_config.max_tokens == 1500
        assert fresh_config.enable_content_filtering is True
        assert fresh_config.enable_toxicity_check is True
        assert fresh_config.enable_bias_detection is True
        assert fresh_config.enable_metrics is True
        assert fresh_config.enable_logging is True
        assert fresh_config.log_level == "INFO"
    
    def test_config_post_init_languages(self, fresh_config):
        """Test post-init default language configuration"""        expected_languages = ["en", "de", "fr", "es", "it", "pt"]
        assert fresh_config.supported_languages == expected_languages
        assert len(fresh_config.supported_languages) == 6
        assert "en" in fresh_config.supported_languages
        assert "de" in fresh_config.supported_languages
        assert "fr" in fresh_config.supported_languages
    
    def test_config_post_init_platforms(self, fresh_config):
        """Test post-init default platform configuration"""        expected_platforms = [
            Platform.SPOTIFY, Platform.APPLE_MUSIC, Platform.YOUTUBE,
            Platform.INSTAGRAM, Platform.TIKTOK, Platform.FACEBOOK,
            Platform.TWITTER, Platform.SOUNDCLOUD, Platform.LINKEDIN,
            Platform.TWITCH
        ]
        assert fresh_config.supported_platforms == expected_platforms
        assert len(fresh_config.supported_platforms) == 10
        assert Platform.SPOTIFY in fresh_config.supported_platforms
        assert Platform.YOUTUBE in fresh_config.supported_platforms
        assert Platform.TIKTOK in fresh_config.supported_platforms
    
    def test_config_post_init_formats(self, fresh_config):
        """Test post-init default format configuration"""        expected_formats = [
            ContentFormat.AUDIO, ContentFormat.VIDEO, 
            ContentFormat.IMAGE, ContentFormat.TEXT, ContentFormat.MIXED
        ]
        assert fresh_config.supported_formats == expected_formats
        assert len(fresh_config.supported_formats) == 5
        assert ContentFormat.AUDIO in fresh_config.supported_formats
        assert ContentFormat.VIDEO in fresh_config.supported_formats
        assert ContentFormat.MIXED in fresh_config.supported_formats
    
    def test_custom_config_initialization(self, custom_config):
        """Test custom configuration initialization"""        assert custom_config.default_quality_level == PromptQualityLevel.ENTERPRISE
        assert custom_config.min_quality_score == 90.0
        assert custom_config.max_prompt_length == 2500
        assert custom_config.cache_ttl_seconds == 7200
        assert custom_config.max_concurrent_generations == 15
        assert custom_config.default_ai_model == "gpt-4-turbo"
        assert custom_config.fallback_ai_model == "claude-3-opus"
        assert custom_config.temperature == 0.8
        assert custom_config.max_tokens == 2000
        assert len(custom_config.supported_languages) == 8
        assert "ja" in custom_config.supported_languages
        assert "ko" in custom_config.supported_languages
        assert custom_config.log_level == "DEBUG"
    
    # ===== ENUM TESTS =====
    
    def test_prompt_quality_level_enum(self):
        """Test PromptQualityLevel enum values"""        assert PromptQualityLevel.BASIC.value == "basic"
        assert PromptQualityLevel.ADVANCED.value == "advanced"
        assert PromptQualityLevel.PROFESSIONAL.value == "professional"
        assert PromptQualityLevel.ENTERPRISE.value == "enterprise"
        
        # Test all enum members
        quality_levels = list(PromptQualityLevel)
        assert len(quality_levels) == 4
        assert PromptQualityLevel.BASIC in quality_levels
        assert PromptQualityLevel.ADVANCED in quality_levels
        assert PromptQualityLevel.PROFESSIONAL in quality_levels
        assert PromptQualityLevel.ENTERPRISE in quality_levels
    
    def test_content_format_enum(self):
        """Test ContentFormat enum values"""        assert ContentFormat.AUDIO.value == "audio"
        assert ContentFormat.VIDEO.value == "video"
        assert ContentFormat.IMAGE.value == "image"
        assert ContentFormat.TEXT.value == "text"
        assert ContentFormat.MIXED.value == "mixed"
        
        # Test all enum members
        content_formats = list(ContentFormat)
        assert len(content_formats) == 5
        assert ContentFormat.AUDIO in content_formats
        assert ContentFormat.VIDEO in content_formats
        assert ContentFormat.IMAGE in content_formats
        assert ContentFormat.TEXT in content_formats
        assert ContentFormat.MIXED in content_formats
    
    def test_platform_enum(self):
        """Test Platform enum values"""        assert Platform.SPOTIFY.value == "spotify"
        assert Platform.APPLE_MUSIC.value == "apple_music"
        assert Platform.YOUTUBE.value == "youtube"
        assert Platform.INSTAGRAM.value == "instagram"
        assert Platform.TIKTOK.value == "tiktok"
        assert Platform.FACEBOOK.value == "facebook"
        assert Platform.TWITTER.value == "twitter"
        assert Platform.SOUNDCLOUD.value == "soundcloud"
        assert Platform.LINKEDIN.value == "linkedin"
        assert Platform.TWITCH.value == "twitch"
        
        # Test all enum members
        platforms = list(Platform)
        assert len(platforms) == 10
        for platform in platforms:
            assert isinstance(platform.value, str)
            assert platform.value.replace("_", "").isalpha()
    
    # ===== VALIDATION TESTS =====
    
    def test_validate_config_valid(self):
        """Test configuration validation with valid config"""        # Temporarily modify global config to valid values
        original_config = PROMPTS_CONFIG
        
        try:
            test_config = PromptsConfig(
                min_quality_score=85.0,
                max_prompt_length=2000,
                temperature=0.7,
                max_tokens=1500,
                max_concurrent_generations=10,
                cache_ttl_seconds=3600
            )
            
            # Patch global config for validation
            with patch('backend.ai.prompts.prompts_config.PROMPTS_CONFIG', test_config):
                validation_result = validate_config()
                
                assert validation_result["valid"] is True
                assert len(validation_result["issues"]) == 0
                assert isinstance(validation_result["warnings"], list)
                assert validation_result["config"] == test_config
        
        finally:
            # Restore original config
            pass  # Global config restoration handled by patch
    
    def test_validate_config_invalid_quality_score(self):
        """Test validation with invalid quality score"""        test_config = PromptsConfig(min_quality_score=150.0)  # Invalid: > 100
        
        with patch('backend.ai.prompts.prompts_config.PROMPTS_CONFIG', test_config):
            validation_result = validate_config()
            
            assert validation_result["valid"] is False
            assert any("min_quality_score must be between 0 and 100" in issue for issue in validation_result["issues"])
    
    def test_validate_config_invalid_temperature(self):
        """Test validation with invalid temperature"""        test_config = PromptsConfig(temperature=3.0)  # Invalid: > 2
        
        with patch('backend.ai.prompts.prompts_config.PROMPTS_CONFIG', test_config):
            validation_result = validate_config()
            
            assert validation_result["valid"] is False
            assert any("temperature must be between 0 and 2" in issue for issue in validation_result["issues"])
    
    def test_validate_config_invalid_max_tokens(self):
        """Test validation with invalid max tokens"""        test_config = PromptsConfig(max_tokens=30)  # Invalid: < 50
        
        with patch('backend.ai.prompts.prompts_config.PROMPTS_CONFIG', test_config):
            validation_result = validate_config()
            
            assert validation_result["valid"] is False
            assert any("max_tokens is too low for quality prompts" in issue for issue in validation_result["issues"])
    
    def test_validate_config_invalid_concurrent_generations(self):
        """Test validation with invalid concurrent generations"""        test_config = PromptsConfig(max_concurrent_generations=0)  # Invalid: < 1
        
        with patch('backend.ai.prompts.prompts_config.PROMPTS_CONFIG', test_config):
            validation_result = validate_config()
            
            assert validation_result["valid"] is False
            assert any("max_concurrent_generations must be at least 1" in issue for issue in validation_result["issues"])
    
    def test_validate_config_warnings(self):
        """Test configuration validation with warnings"""        test_config = PromptsConfig(
            max_prompt_length=50,  # Warning: very low
            cache_ttl_seconds=30   # Warning: very low
        )
        
        with patch('backend.ai.prompts.prompts_config.PROMPTS_CONFIG', test_config):
            validation_result = validate_config()
            
            assert validation_result["valid"] is True  # No critical issues
            assert len(validation_result["warnings"]) >= 2
            assert any("max_prompt_length is very low" in warning for warning in validation_result["warnings"])
            assert any("cache_ttl_seconds is very low" in warning for warning in validation_result["warnings"])
    
    def test_validate_config_multiple_issues(self):
        """Test validation with multiple configuration issues"""        test_config = PromptsConfig(
            min_quality_score=-10.0,    # Invalid
            temperature=5.0,            # Invalid
            max_tokens=10,              # Invalid
            max_concurrent_generations=-1,  # Invalid
            max_prompt_length=25,       # Warning
            cache_ttl_seconds=10        # Warning
        )
        
        with patch('backend.ai.prompts.prompts_config.PROMPTS_CONFIG', test_config):
            validation_result = validate_config()
            
            assert validation_result["valid"] is False
            assert len(validation_result["issues"]) >= 4
            assert len(validation_result["warnings"]) >= 2
    
    # ===== CONFIGURATION SCENARIOS TESTS =====
    
    def test_development_environment_config(self):
        """Test configuration for development environment"""        dev_config = PromptsConfig(
            default_quality_level=PromptQualityLevel.ADVANCED,
            cache_enabled=True,
            cache_ttl_seconds=1800,  # 30 minutes
            max_concurrent_generations=5,
            enable_metrics=True,
            enable_logging=True,
            log_level="DEBUG",
            temperature=0.8,  # Higher creativity for experimentation
            max_tokens=1000
        )
        
        assert dev_config.default_quality_level == PromptQualityLevel.ADVANCED
        assert dev_config.cache_ttl_seconds == 1800
        assert dev_config.log_level == "DEBUG"
        assert dev_config.temperature == 0.8
        assert dev_config.enable_metrics is True
        assert dev_config.enable_logging is True
        
        with patch('backend.ai.prompts.prompts_config.PROMPTS_CONFIG', dev_config):
            validation_result = validate_config()
            assert validation_result["valid"] is True
    
    def test_production_environment_config(self):
        """Test configuration for production environment"""        prod_config = PromptsConfig(
            default_quality_level=PromptQualityLevel.PROFESSIONAL,
            min_quality_score=90.0,
            cache_enabled=True,
            cache_ttl_seconds=7200,  # 2 hours
            max_concurrent_generations=20,
            default_ai_model="gpt-4-turbo",
            temperature=0.6,  # Lower creativity for consistency
            max_tokens=1800,
            enable_content_filtering=True,
            enable_toxicity_check=True,
            enable_bias_detection=True,
            enable_metrics=True,
            enable_logging=True,
            log_level="INFO"
        )
        
        assert prod_config.default_quality_level == PromptQualityLevel.PROFESSIONAL
        assert prod_config.min_quality_score == 90.0
        assert prod_config.max_concurrent_generations == 20
        assert prod_config.temperature == 0.6
        assert prod_config.enable_content_filtering is True
        assert prod_config.enable_toxicity_check is True
        assert prod_config.enable_bias_detection is True
        assert prod_config.log_level == "INFO"
        
        with patch('backend.ai.prompts.prompts_config.PROMPTS_CONFIG', prod_config):
            validation_result = validate_config()
            assert validation_result["valid"] is True
    
    def test_enterprise_environment_config(self):
        """Test configuration for enterprise environment"""        enterprise_config = PromptsConfig(
            default_quality_level=PromptQualityLevel.ENTERPRISE,
            min_quality_score=95.0,
            max_prompt_length=3000,
            cache_enabled=True,
            cache_ttl_seconds=14400,  # 4 hours
            max_concurrent_generations=50,
            default_ai_model="gpt-4-turbo",
            fallback_ai_model="claude-3-opus",
            temperature=0.5,  # Conservative for enterprise
            max_tokens=2500,
            supported_languages=["en", "de", "fr", "es", "it", "pt", "ja", "ko", "zh", "ru"],
            enable_content_filtering=True,
            enable_toxicity_check=True,
            enable_bias_detection=True,
            enable_metrics=True,
            enable_logging=True,
            log_level="WARN"  # Reduce noise in enterprise logs
        )
        
        assert enterprise_config.default_quality_level == PromptQualityLevel.ENTERPRISE
        assert enterprise_config.min_quality_score == 95.0
        assert enterprise_config.max_prompt_length == 3000
        assert enterprise_config.max_concurrent_generations == 50
        assert enterprise_config.temperature == 0.5
        assert len(enterprise_config.supported_languages) == 10
        assert "zh" in enterprise_config.supported_languages
        assert "ru" in enterprise_config.supported_languages
        assert enterprise_config.log_level == "WARN"
        
        with patch('backend.ai.prompts.prompts_config.PROMPTS_CONFIG', enterprise_config):
            validation_result = validate_config()
            assert validation_result["valid"] is True
    
    def test_minimal_resource_config(self):
        """Test configuration for minimal resource environments"""        minimal_config = PromptsConfig(
            default_quality_level=PromptQualityLevel.BASIC,
            min_quality_score=70.0,
            max_prompt_length=800,
            cache_enabled=False,  # No caching to save memory
            max_concurrent_generations=2,
            default_ai_model="gpt-3.5-turbo",
            temperature=0.4,
            max_tokens=800,
            supported_languages=["en", "de", "fr"],  # Limited languages
            supported_platforms=[Platform.SPOTIFY, Platform.YOUTUBE, Platform.INSTAGRAM],  # Limited platforms
            enable_content_filtering=False,  # Disabled to save resources
            enable_toxicity_check=False,
            enable_bias_detection=False,
            enable_metrics=False,
            enable_logging=False
        )
        
        assert minimal_config.default_quality_level == PromptQualityLevel.BASIC
        assert minimal_config.cache_enabled is False
        assert minimal_config.max_concurrent_generations == 2
        assert len(minimal_config.supported_languages) == 3
        assert len(minimal_config.supported_platforms) == 3
        assert minimal_config.enable_content_filtering is False
        assert minimal_config.enable_metrics is False
        
        with patch('backend.ai.prompts.prompts_config.PROMPTS_CONFIG', minimal_config):
            validation_result = validate_config()
            assert validation_result["valid"] is True
    
    # ===== PLATFORM-SPECIFIC TESTS =====
    
    def test_music_platform_config(self):
        """Test configuration optimized for music platforms"""        music_config = PromptsConfig(
            supported_platforms=[
                Platform.SPOTIFY, Platform.APPLE_MUSIC, Platform.SOUNDCLOUD,
                Platform.YOUTUBE, Platform.BANDCAMP
            ],
            supported_formats=[ContentFormat.AUDIO, ContentFormat.VIDEO],
            supported_languages=["en", "de", "fr", "es", "it", "pt", "ja"],
            default_quality_level=PromptQualityLevel.PROFESSIONAL,
            temperature=0.65,  # Balanced creativity for music content
            max_tokens=1800
        )
        
        music_platforms = [Platform.SPOTIFY, Platform.APPLE_MUSIC, Platform.SOUNDCLOUD]
        for platform in music_platforms:
            assert platform in music_config.supported_platforms
        
        assert ContentFormat.AUDIO in music_config.supported_formats
        assert len(music_config.supported_platforms) == 5
        assert music_config.temperature == 0.65
    
    def test_video_platform_config(self):
        """Test configuration optimized for video platforms"""        video_config = PromptsConfig(
            supported_platforms=[
                Platform.YOUTUBE, Platform.INSTAGRAM, Platform.TIKTOK,
                Platform.FACEBOOK, Platform.TWITCH
            ],
            supported_formats=[ContentFormat.VIDEO, ContentFormat.IMAGE, ContentFormat.MIXED],
            default_quality_level=PromptQualityLevel.ADVANCED,
            temperature=0.75,  # Higher creativity for video content
            max_tokens=2000,
            max_prompt_length=2500
        )
        
        video_platforms = [Platform.YOUTUBE, Platform.INSTAGRAM, Platform.TIKTOK]
        for platform in video_platforms:
            assert platform in video_config.supported_platforms
        
        assert ContentFormat.VIDEO in video_config.supported_formats
        assert ContentFormat.MIXED in video_config.supported_formats
        assert len(video_config.supported_platforms) == 5
        assert video_config.temperature == 0.75
        assert video_config.max_prompt_length == 2500
    
    def test_social_media_config(self):
        """Test configuration optimized for social media platforms"""        social_config = PromptsConfig(
            supported_platforms=[
                Platform.INSTAGRAM, Platform.TIKTOK, Platform.FACEBOOK,
                Platform.TWITTER, Platform.LINKEDIN
            ],
            supported_formats=[ContentFormat.IMAGE, ContentFormat.VIDEO, ContentFormat.TEXT],
            temperature=0.8,  # High creativity for social engagement
            max_tokens=1200,  # Shorter prompts for social content
            max_prompt_length=1500,
            enable_content_filtering=True,  # Important for social platforms
            enable_toxicity_check=True,
            enable_bias_detection=True
        )
        
        social_platforms = [Platform.INSTAGRAM, Platform.TIKTOK, Platform.TWITTER]
        for platform in social_platforms:
            assert platform in social_config.supported_platforms
        
        assert social_config.temperature == 0.8
        assert social_config.max_tokens == 1200
        assert social_config.enable_content_filtering is True
        assert social_config.enable_toxicity_check is True
    
    # ===== SERIALIZATION TESTS =====
    
    def test_config_to_dict(self, custom_config):
        """Test configuration serialization to dictionary"""        # Note: Since dataclass doesn't have built-in to_dict, we'll test the attributes
        config_dict = {
            "default_quality_level": custom_config.default_quality_level.value,
            "min_quality_score": custom_config.min_quality_score,
            "max_prompt_length": custom_config.max_prompt_length,
            "cache_enabled": custom_config.cache_enabled,
            "cache_ttl_seconds": custom_config.cache_ttl_seconds,
            "max_concurrent_generations": custom_config.max_concurrent_generations,
            "default_ai_model": custom_config.default_ai_model,
            "fallback_ai_model": custom_config.fallback_ai_model,
            "temperature": custom_config.temperature,
            "max_tokens": custom_config.max_tokens,
            "supported_languages": custom_config.supported_languages,
            "supported_platforms": [p.value for p in custom_config.supported_platforms],
            "supported_formats": [f.value for f in custom_config.supported_formats],
            "enable_content_filtering": custom_config.enable_content_filtering,
            "enable_toxicity_check": custom_config.enable_toxicity_check,
            "enable_bias_detection": custom_config.enable_bias_detection,
            "enable_metrics": custom_config.enable_metrics,
            "enable_logging": custom_config.enable_logging,
            "log_level": custom_config.log_level
        }
        
        assert config_dict["default_quality_level"] == "enterprise"
        assert config_dict["min_quality_score"] == 90.0
        assert config_dict["max_prompt_length"] == 2500
        assert config_dict["default_ai_model"] == "gpt-4-turbo"
        assert config_dict["temperature"] == 0.8
        assert len(config_dict["supported_languages"]) == 8
        assert "spotify" in config_dict["supported_platforms"]
        assert "audio" in config_dict["supported_formats"]
    
    def test_config_json_serialization(self, custom_config):
        """Test configuration JSON serialization"""        config_dict = {
            "default_quality_level": custom_config.default_quality_level.value,
            "min_quality_score": custom_config.min_quality_score,
            "max_prompt_length": custom_config.max_prompt_length,
            "cache_enabled": custom_config.cache_enabled,
            "temperature": custom_config.temperature,
            "supported_languages": custom_config.supported_languages
        }
        
        json_str = json.dumps(config_dict)
        assert isinstance(json_str, str)
        
        # Verify JSON can be parsed back
        parsed_config = json.loads(json_str)
        assert parsed_config["default_quality_level"] == "enterprise"
        assert parsed_config["min_quality_score"] == 90.0
        assert parsed_config["temperature"] == 0.8
        assert isinstance(parsed_config["supported_languages"], list)
    
    # ===== GLOBAL CONFIG TESTS =====
    
    def test_global_config_instance(self):
        """Test global configuration instance"""        assert PROMPTS_CONFIG is not None
        assert isinstance(PROMPTS_CONFIG, PromptsConfig)
        assert PROMPTS_CONFIG.default_quality_level == PromptQualityLevel.ADVANCED
        assert PROMPTS_CONFIG.cache_enabled is True
        assert PROMPTS_CONFIG.enable_content_filtering is True
    
    def test_global_config_validation(self):
        """Test global configuration validation"""        validation_result = validate_config()
        assert isinstance(validation_result, dict)
        assert "valid" in validation_result
        assert "issues" in validation_result
        assert "warnings" in validation_result
        assert "config" in validation_result
        
        # Global config should be valid by default
        assert validation_result["valid"] is True or len(validation_result["issues"]) == 0
    
    # ===== PERFORMANCE TESTS =====
    
    def test_config_initialization_performance(self):
        """Test configuration initialization performance"""        start_time = datetime.now()
        
        # Create multiple config instances
        configs = []
        for _ in range(100):
            config = PromptsConfig()
            configs.append(config)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        assert len(configs) == 100
        assert duration < 1.0  # Should complete within 1 second
        
        # Verify all configs are properly initialized
        for config in configs[:5]:  # Check first 5
            assert config.default_quality_level == PromptQualityLevel.ADVANCED
            assert len(config.supported_languages) == 6
            assert len(config.supported_platforms) == 10
    
    def test_validation_performance(self):
        """Test configuration validation performance"""        test_configs = []
        
        # Create various config scenarios
        for i in range(20):
            config = PromptsConfig(
                min_quality_score=float(60 + i),
                temperature=0.5 + (i * 0.01),
                max_tokens=500 + (i * 50),
                max_concurrent_generations=1 + i
            )
            test_configs.append(config)
        
        start_time = datetime.now()
        
        validation_results = []
        for config in test_configs:
            with patch('backend.ai.prompts.prompts_config.PROMPTS_CONFIG', config):
                result = validate_config()
                validation_results.append(result)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        assert len(validation_results) == 20
        assert duration < 2.0  # Should complete within 2 seconds
        
        # Verify all validations completed
        for result in validation_results:
            assert "valid" in result
            assert isinstance(result["issues"], list)
            assert isinstance(result["warnings"], list)
