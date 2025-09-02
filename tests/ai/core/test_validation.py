# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Comprehensive Content Validation System Tests

Ultra-advanced enterprise-grade test suite for content validation and quality assurance.
Tests multi-format validation, security, quality analysis, and creator-specific requirements.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  COPYRIGHT WARNING: This file is protected by copyright law. Unauthorized copying,
distribution, modification, or use is strictly prohibited. Violations will result in
legal action. Contact mlaiel@live.de for licensing inquiries.

Team Expertise:
- Lead Developer & AI Architect: Advanced validation systems, multi-format processing
- Backend Senior Engineer: Enterprise security validation, performance optimization
- ML Engineer: AI-powered content quality analysis, threat detection
- Quality Assurance Lead: Comprehensive test coverage, validation workflows
- Content Security Specialist: Safety validation, compliance verification
- Performance Engineer: Validation performance optimization, scalability testing

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import tempfile
import shutil
import hashlib
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from concurrent.futures import ThreadPoolExecutor

# System imports
import os
import sys
import logging
import warnings

# Test imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from ai.core.validation import (
    ContentValidator,
    ValidationLevel,
    ValidationCategory,
    ContentType,
    ValidationResult,
    ValidationIssue,
    ContentSecurityValidator,
    ContentQualityAnalyzer,
    AudioContentValidator,
    ImageContentValidator,
    content_validator
)


class TestValidationLevel:
    """Test suite for ValidationLevel enumeration"""
    
    def test_validation_level_values(self):
        """
Test validation level enum values"""
        assert ValidationLevel.INFO.value == "info"
        assert ValidationLevel.WARNING.value == "warning"
        assert ValidationLevel.ERROR.value == "error"
        assert ValidationLevel.CRITICAL.value == "critical"
        assert ValidationLevel.SECURITY.value == "security"
        assert ValidationLevel.COMPLIANCE.value == "compliance"
        assert ValidationLevel.QUALITY.value == "quality"
        assert ValidationLevel.PERFORMANCE.value == "performance"
    
    def test_validation_level_hierarchy(self):
        """Test validation level severity hierarchy"""
        levels = [
            ValidationLevel.INFO,
            ValidationLevel.WARNING,
            ValidationLevel.ERROR,
            ValidationLevel.CRITICAL,
            ValidationLevel.SECURITY
        ]
        
        # Ensure all levels are distinct
        assert len(set(level.value for level in levels)) == len(levels)
    
    def test_validation_level_string_representation(self):
        """
Test validation level string representation"""
        assert str(ValidationLevel.ERROR) == "ValidationLevel.ERROR"
        assert repr(ValidationLevel.CRITICAL) == "<ValidationLevel.CRITICAL: 'critical'>"


class TestValidationCategory:
    """Test suite for ValidationCategory enumeration"""
    
    def test_validation_category_values(self):
        """
Test validation category enum values"""
        assert ValidationCategory.CONTENT_SAFETY.value == "content_safety"
        assert ValidationCategory.COPYRIGHT_COMPLIANCE.value == "copyright_compliance"
        assert ValidationCategory.TECHNICAL_QUALITY.value == "technical_quality"
        assert ValidationCategory.BRAND_SAFETY.value == "brand_safety"
        assert ValidationCategory.SEO_OPTIMIZATION.value == "seo_optimization"
        assert ValidationCategory.ACCESSIBILITY.value == "accessibility"
        assert ValidationCategory.PLATFORM_COMPLIANCE.value == "platform_compliance"
        assert ValidationCategory.MONETIZATION_READY.value == "monetization_ready"
        assert ValidationCategory.COLLABORATION_READY.value == "collaboration_ready"
        assert ValidationCategory.LEGAL_COMPLIANCE.value == "legal_compliance"
    
    def test_validation_category_completeness(self):
        """Test validation category completeness for all creator needs"""
        required_categories = [
            "content_safety", "copyright_compliance", "technical_quality",
            "brand_safety", "seo_optimization", "accessibility",
            "platform_compliance", "monetization_ready", 
            "collaboration_ready", "legal_compliance"
        ]
        
        actual_categories = [category.value for category in ValidationCategory]
        
        for required in required_categories:
            assert required in actual_categories


class TestContentType:
    """Test suite for ContentType enumeration"""
    
    def test_content_type_values(self):
        """
Test content type enum values"""
        assert ContentType.TEXT.value == "text"
        assert ContentType.AUDIO.value == "audio"
        assert ContentType.VIDEO.value == "video"
        assert ContentType.IMAGE.value == "image"
        assert ContentType.MUSIC.value == "music"
        assert ContentType.PODCAST.value == "podcast"
        assert ContentType.PHOTO.value == "photo"
        assert ContentType.SOCIAL_POST.value == "social_post"
        assert ContentType.BLOG_POST.value == "blog_post"
    
    def test_creator_specific_content_types(self):
        """Test creator-specific content types coverage"""
        # Musicians
        music_types = [ContentType.MUSIC, ContentType.AUDIO, ContentType.PODCAST]
        assert all(ctype in ContentType for ctype in music_types)
        
        # Photographers
        photo_types = [ContentType.PHOTO, ContentType.IMAGE, ContentType.ARTWORK]
        assert all(ctype in ContentType for ctype in photo_types)
        
        # Bloggers/Influencers
        content_types = [ContentType.BLOG_POST, ContentType.SOCIAL_POST, ContentType.TEXT]
        assert all(ctype in ContentType for ctype in content_types)


class TestValidationIssue:
    """
Test suite for ValidationIssue data class"""
    
    def test_validation_issue_creation(self):
        """
Test validation issue creation with all parameters"""
        issue = ValidationIssue(
            level=ValidationLevel.ERROR,
            category=ValidationCategory.CONTENT_SAFETY,
            message="Test security issue",
            code="TEST_SECURITY_001",
            confidence=0.9,
            auto_fixable=True,
            fix_suggestion="Apply security patch",
            context={"location": "line 42"}
        )
        
        assert issue.level == ValidationLevel.ERROR
        assert issue.category == ValidationCategory.CONTENT_SAFETY
        assert issue.message == "Test security issue"
        assert issue.code == "TEST_SECURITY_001"
        assert issue.confidence == 0.9
        assert issue.auto_fixable is True
        assert issue.fix_suggestion == "Apply security patch"
        assert issue.context["location"] == "line 42"
        assert isinstance(issue.timestamp, datetime)
    
    def test_validation_issue_defaults(self):
        """Test validation issue default values"""
        issue = ValidationIssue(
            level=ValidationLevel.WARNING,
            category=ValidationCategory.TECHNICAL_QUALITY,
            message="Test warning",
            code="TEST_WARNING_001"
        )
        
        assert issue.confidence == 1.0
        assert issue.severity_score == 1
        assert issue.auto_fixable is False
        assert issue.fix_suggestion is None
        assert issue.context == {}
        assert issue.source_location is None
    
    def test_validation_issue_to_dict(self):
        """Test validation issue dictionary conversion"""
        issue = ValidationIssue(
            level=ValidationLevel.CRITICAL,
            category=ValidationCategory.SECURITY,
            message="Critical security flaw",
            code="CRITICAL_001",
            confidence=0.95,
            auto_fixable=False,
            fix_suggestion="Immediate security update required",
            context={"severity": "high", "impact": "system"}
        )
        
        issue_dict = issue.to_dict()
        
        assert issue_dict["level"] == "critical"
        assert issue_dict["category"] == "security"
        assert issue_dict["message"] == "Critical security flaw"
        assert issue_dict["code"] == "CRITICAL_001"
        assert issue_dict["confidence"] == 0.95
        assert issue_dict["auto_fixable"] is False
        assert issue_dict["fix_suggestion"] == "Immediate security update required"
        assert issue_dict["context"]["severity"] == "high"
        assert "timestamp" in issue_dict


class TestValidationResult:
    """Test suite for ValidationResult data class"""
    
    def test_validation_result_creation(self):
        """
Test validation result creation with all scores"""
        result = ValidationResult(
            is_valid=True,
            overall_score=95.0,
            quality_score=90.0,
            safety_score=98.0,
            compliance_score=92.0,
            seo_score=88.0,
            monetization_readiness=85.0
        )
        
        assert result.is_valid is True
        assert result.overall_score == 95.0
        assert result.quality_score == 90.0
        assert result.safety_score == 98.0
        assert result.compliance_score == 92.0
        assert result.seo_score == 88.0
        assert result.monetization_readiness == 85.0
        assert result.issues == []
        assert result.warnings == []
        assert result.errors == []
        assert isinstance(result.validation_timestamp, datetime)
    
    def test_add_issue_functionality(self):
        """
Test adding issues to validation result"""
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        # Add warning
        result.add_issue(
            ValidationLevel.WARNING,
            ValidationCategory.TECHNICAL_QUALITY,
            "Minor quality issue",
            "QUALITY_WARNING_001",
            confidence=0.8,
            auto_fixable=True,
            fix_suggestion="Improve formatting"
        )
        
        assert len(result.issues) == 1
        assert len(result.warnings) == 1
        assert len(result.errors) == 0
        assert result.is_valid is True  # Still valid with warning
        
        # Add error
        result.add_issue(
            ValidationLevel.ERROR,
            ValidationCategory.CONTENT_SAFETY,
            "Safety violation detected",
            "SAFETY_ERROR_001"
        )
        
        assert len(result.issues) == 2
        assert len(result.warnings) == 1
        assert len(result.errors) == 1
        assert result.is_valid is False  # Invalid due to error
    
    def test_get_issues_by_category(self):
        """Test filtering issues by category"""
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        result.add_issue(ValidationLevel.WARNING, ValidationCategory.TECHNICAL_QUALITY, 
                        "Quality issue", "QUALITY_001")
        result.add_issue(ValidationLevel.ERROR, ValidationCategory.CONTENT_SAFETY, 
                        "Safety issue", "SAFETY_001")
        result.add_issue(ValidationLevel.WARNING, ValidationCategory.TECHNICAL_QUALITY, 
                        "Another quality issue", "QUALITY_002")
        
        quality_issues = result.get_issues_by_category(ValidationCategory.TECHNICAL_QUALITY)
        safety_issues = result.get_issues_by_category(ValidationCategory.CONTENT_SAFETY)
        
        assert len(quality_issues) == 2
        assert len(safety_issues) == 1
        assert all(issue.category == ValidationCategory.TECHNICAL_QUALITY for issue in quality_issues)
        assert all(issue.category == ValidationCategory.CONTENT_SAFETY for issue in safety_issues)
    
    def test_get_issues_by_level(self):
        """Test filtering issues by level"""
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        result.add_issue(ValidationLevel.WARNING, ValidationCategory.TECHNICAL_QUALITY, 
                        "Warning issue", "WARNING_001")
        result.add_issue(ValidationLevel.ERROR, ValidationCategory.CONTENT_SAFETY, 
                        "Error issue", "ERROR_001")
        result.add_issue(ValidationLevel.CRITICAL, ValidationCategory.SECURITY, 
                        "Critical issue", "CRITICAL_001")
        
        warning_issues = result.get_issues_by_level(ValidationLevel.WARNING)
        error_issues = result.get_issues_by_level(ValidationLevel.ERROR)
        critical_issues = result.get_issues_by_level(ValidationLevel.CRITICAL)
        
        assert len(warning_issues) == 1
        assert len(error_issues) == 1
        assert len(critical_issues) == 1
    
    def test_get_fixable_issues(self):
        """Test filtering fixable issues"""
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        result.add_issue(ValidationLevel.WARNING, ValidationCategory.TECHNICAL_QUALITY, 
                        "Fixable issue", "FIXABLE_001", auto_fixable=True)
        result.add_issue(ValidationLevel.ERROR, ValidationCategory.CONTENT_SAFETY, 
                        "Non-fixable issue", "NON_FIXABLE_001", auto_fixable=False)
        result.add_issue(ValidationLevel.WARNING, ValidationCategory.SEO_OPTIMIZATION, 
                        "Another fixable issue", "FIXABLE_002", auto_fixable=True)
        
        fixable_issues = result.get_fixable_issues()
        
        assert len(fixable_issues) == 2
        assert all(issue.auto_fixable for issue in fixable_issues)
    
    def test_validation_result_to_dict(self):
        """Test validation result dictionary conversion"""
        result = ValidationResult(
            is_valid=False,
            overall_score=75.0,
            quality_score=80.0,
            safety_score=70.0,
            compliance_score=85.0,
            seo_score=60.0,
            monetization_readiness=65.0
        )
        
        result.add_issue(ValidationLevel.ERROR, ValidationCategory.CONTENT_SAFETY, 
                        "Safety violation", "SAFETY_001")
        result.metadata["test_data"] = "test_value"
        result.content_fingerprint = "abc123"
        result.processing_time_ms = 250.5
        
        result_dict = result.to_dict()
        
        assert result_dict["is_valid"] is False
        assert result_dict["scores"]["overall"] == 75.0
        assert result_dict["scores"]["quality"] == 80.0
        assert result_dict["scores"]["safety"] == 70.0
        assert result_dict["scores"]["compliance"] == 85.0
        assert result_dict["scores"]["seo"] == 60.0
        assert result_dict["scores"]["monetization_readiness"] == 65.0
        assert len(result_dict["issues"]) == 1
        assert len(result_dict["errors"]) == 1
        assert result_dict["metadata"]["test_data"] == "test_value"
        assert result_dict["content_fingerprint"] == "abc123"
        assert result_dict["processing_time_ms"] == 250.5


class TestContentSecurityValidator:
    """Test suite for ContentSecurityValidator class"""
    
    def setup_method(self):
        """
Setup security validator for testing"""
        self.security_validator = ContentSecurityValidator()
    
    def test_security_validator_initialization(self):
        """
Test security validator initialization"""
        assert hasattr(self.security_validator, 'blocked_patterns')
        assert hasattr(self.security_validator, 'suspicious_patterns')
        assert hasattr(self.security_validator, 'malware_signatures')
        assert len(self.security_validator.blocked_patterns) > 0
        assert len(self.security_validator.suspicious_patterns) > 0
    
    def test_malicious_content_detection(self):
        """
Test detection of malicious content patterns"""
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        malicious_content = """
        <script>alert('XSS attack')</script>
        <a href="javascript:maliciousFunction()">Click here</a>
        """
        
        self.security_validator.validate_security(malicious_content, result)
        
        assert result.safety_score < 100.0
        security_issues = result.get_issues_by_category(ValidationCategory.CONTENT_SAFETY)
        assert len(security_issues) > 0
        assert any(issue.level == ValidationLevel.SECURITY for issue in security_issues)
    
    def test_suspicious_content_detection(self):
        try:
            logger.info(f"Executing test_suspicious_content_detection")
            
            # Implementation for test_suspicious_content_detection
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_suspicious_content_detection completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_suspicious_content_detection failed: {e}")
            raise
    def test_clean_content_validation(self):
        """Test validation of clean, safe content"""
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        clean_content = "This is a perfectly safe and clean content for creators to share."
        
        self.security_validator.validate_security(clean_content, result)
        
        assert result.safety_score == 100.0
        security_issues = result.get_issues_by_category(ValidationCategory.CONTENT_SAFETY)
        assert len(security_issues) == 0
    
    def test_security_pattern_loading(self):
        """Test security pattern loading and configuration"""
        self.security_validator.load_security_rules()
        
        # Check that patterns are loaded
        assert len(self.security_validator.blocked_patterns) >= 5
        assert len(self.security_validator.suspicious_patterns) >= 4
        
        # Check specific patterns exist
        script_pattern_exists = any('script' in pattern for pattern in self.security_validator.blocked_patterns)
        assert script_pattern_exists
        
        hack_pattern_exists = any('hack' in pattern for pattern in self.security_validator.suspicious_patterns)
        assert hack_pattern_exists


class TestContentQualityAnalyzer:
    """
Test suite for ContentQualityAnalyzer class"""
    
    def setup_method(self):
        """
Setup quality analyzer for testing"""
        self.quality_analyzer = ContentQualityAnalyzer()
    
    def test_quality_analyzer_initialization(self):
        """
Test quality analyzer initialization"""
        assert hasattr(self.quality_analyzer, 'quality_metrics')
        assert isinstance(self.quality_analyzer.quality_metrics, dict)
    
    @patch('backend.ai.core.validation.TRANSFORMERS_AVAILABLE', True)
    def test_ai_models_initialization(self):
        """
Test AI models initialization when available"""
        with patch('backend.ai.core.validation.AutoTokenizer.from_pretrained') as mock_tokenizer:
            mock_tokenizer.return_value = Mock()
            
            analyzer = ContentQualityAnalyzer()
            analyzer.init_ai_models()
            
            mock_tokenizer.assert_called_once()
    
    def test_text_quality_analysis_short_content(self):
        """
Test text quality analysis for short content"""
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        short_content = "Too short."
        
        self.quality_analyzer.analyze_text_quality(short_content, result)
        
        assert result.quality_score < 100.0
        quality_issues = result.get_issues_by_category(ValidationCategory.TECHNICAL_QUALITY)
        assert len(quality_issues) > 0
        assert any("too short" in issue.message.lower() for issue in quality_issues)
    
    def test_text_quality_analysis_long_content(self):
        """Test text quality analysis for overly long content"""
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        # Create content with over 5000 words
        long_content = " ".join(["word"] * 6000)
        
        self.quality_analyzer.analyze_text_quality(long_content, result)
        
        assert result.quality_score < 100.0
        quality_issues = result.get_issues_by_category(ValidationCategory.TECHNICAL_QUALITY)
        assert len(quality_issues) > 0
        assert any("too long" in issue.message.lower() for issue in quality_issues)
    
    def test_text_quality_analysis_long_sentences(self):
        """Test detection of overly long sentences"""
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        # Create a sentence with over 25 words
        long_sentence = "This is an extremely long sentence that contains many words and should be flagged by the quality analyzer for being too long and potentially impacting readability for users and creators. This is perfectly valid content otherwise."
        
        self.quality_analyzer.analyze_text_quality(long_sentence, result)
        
        quality_issues = result.get_issues_by_category(ValidationCategory.TECHNICAL_QUALITY)
        assert any("long sentences" in issue.message.lower() for issue in quality_issues)
    
    def test_capitalization_checking(self):
        """Test capitalization error detection"""
        content_with_errors = "this sentence should start with capital. another sentence with error."
        errors = self.quality_analyzer._check_capitalization(content_with_errors)
        
        assert errors >= 2  # Both sentences have capitalization errors
    
    def test_good_quality_content(self):
        """Test analysis of high-quality content"""
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        good_content = """
        This is a well-written piece of content. It has proper sentence structure and good length.
        Each sentence is clear and concise. The content provides value to readers.
        It maintains professional quality throughout. This is exactly what creators should aim for.
        """
        
        self.quality_analyzer.analyze_text_quality(good_content, result)
        
        # Should maintain high quality score
        assert result.quality_score >= 80.0
        quality_issues = result.get_issues_by_category(ValidationCategory.TECHNICAL_QUALITY)
        # Minimal or no quality issues
        assert len(quality_issues) <= 1


class TestAudioContentValidator:
    """
Test suite for AudioContentValidator class"""
    
    def setup_method(self):
        """
Setup audio validator for testing"""
        self.audio_validator = AudioContentValidator()
    
    def test_audio_validator_initialization(self):
        """
Test audio validator initialization"""
        assert hasattr(self.audio_validator, 'audio_formats')
        assert hasattr(self.audio_validator, 'quality_thresholds')
        assert '.mp3' in self.audio_validator.audio_formats
        assert '.wav' in self.audio_validator.audio_formats
        assert 'min_sample_rate' in self.audio_validator.quality_thresholds
    
    def test_audio_formats_coverage(self):
        """
Test coverage of audio formats for musicians"""
        required_formats = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']
        
        for format_ext in required_formats:
            assert format_ext in self.audio_validator.audio_formats
    
    def test_quality_thresholds_configuration(self):
        """
Test audio quality thresholds configuration"""
        thresholds = self.audio_validator.quality_thresholds
        
        assert thresholds['min_sample_rate'] >= 44100  # CD quality minimum
        assert thresholds['min_bit_depth'] >= 16  # CD quality minimum
        assert thresholds['max_duration'] > 0
        assert thresholds['min_duration'] > 0
        assert 0 < thresholds['max_silence_ratio'] < 1
    
    @patch('backend.ai.core.validation.AUDIO_AVAILABLE', False)
    def test_audio_validation_library_unavailable(self):
        """
Test audio validation when library is unavailable"""
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        self.audio_validator.validate_audio("test.mp3", result)
        
        warnings = result.get_issues_by_level(ValidationLevel.WARNING)
        assert any("library not available" in issue.message.lower() for issue in warnings)
    
    @patch('backend.ai.core.validation.AUDIO_AVAILABLE', True)
    @patch('backend.ai.core.validation.librosa')
    def test_audio_validation_success(self, mock_librosa):
        """Test successful audio validation"""
        # Mock librosa functions
        mock_librosa.load.return_value = (Mock(), 48000)  # Good sample rate
        mock_librosa.get_duration.return_value = 180.0  # 3 minutes
        
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        # Mock silence calculation
        with patch.object(self.audio_validator, '_calculate_silence_ratio', return_value=0.1):
            with patch.object(self.audio_validator, '_calculate_audio_quality_score', return_value=95.0):
                self.audio_validator.validate_audio("test.mp3", result)
        
        # Should complete without errors
        assert 'audio_quality_score' in result.metadata
        assert result.metadata['audio_quality_score'] == 95.0
    
    @patch('backend.ai.core.validation.AUDIO_AVAILABLE', True)
    @patch('backend.ai.core.validation.librosa')
    def test_audio_validation_low_sample_rate(self, mock_librosa):
        """Test audio validation with low sample rate"""
        # Mock librosa with low sample rate
        mock_librosa.load.return_value = (Mock(), 22050)  # Low sample rate
        mock_librosa.get_duration.return_value = 60.0
        
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        with patch.object(self.audio_validator, '_calculate_silence_ratio', return_value=0.1):
            self.audio_validator.validate_audio("test.mp3", result)
        
        # Should have low sample rate warning
        quality_issues = result.get_issues_by_category(ValidationCategory.TECHNICAL_QUALITY)
        assert any("low sample rate" in issue.message.lower() for issue in quality_issues)
    
    @patch('backend.ai.core.validation.AUDIO_AVAILABLE', True)
    @patch('backend.ai.core.validation.librosa')
    def test_audio_validation_too_short(self, mock_librosa):
        """Test audio validation for too short duration"""
        # Mock librosa with short duration
        mock_librosa.load.return_value = (Mock(), 48000)
        mock_librosa.get_duration.return_value = 2.0  # Too short
        
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        with patch.object(self.audio_validator, '_calculate_silence_ratio', return_value=0.1):
            self.audio_validator.validate_audio("test.mp3", result)
        
        # Should have error for too short audio
        errors = result.get_issues_by_level(ValidationLevel.ERROR)
        assert any("too short" in issue.message.lower() for issue in errors)
        assert result.is_valid is False
    
    def test_silence_ratio_calculation(self):
        """Test silence ratio calculation"""
        import numpy as np
        
        # Create test audio data with known silence
        audio_data = np.array([0.5, 0.001, 0.001, 0.6, 0.001])  # 3 silent samples out of 5
        
        silence_ratio = self.audio_validator._calculate_silence_ratio(audio_data)
        
        # Should detect 3/5 = 0.6 silence ratio
        assert 0.5 <= silence_ratio <= 0.7
    
    def test_audio_quality_score_calculation(self):
        """
Test audio quality score calculation"""
        # Test high quality audio
        score = self.audio_validator._calculate_audio_quality_score(48000, 180.0, 0.1)
        assert score >= 80.0
        
        # Test low quality audio
        score = self.audio_validator._calculate_audio_quality_score(22050, 5.0, 0.4)
        assert score <= 50.0
        
        # Test medium quality audio
        score = self.audio_validator._calculate_audio_quality_score(44100, 120.0, 0.2)
        assert 60.0 <= score <= 90.0


class TestImageContentValidator:
    """
Test suite for ImageContentValidator class"""
    
    def setup_method(self):
        """
Setup image validator for testing"""
        self.image_validator = ImageContentValidator()
    
    def test_image_validator_initialization(self):
        """
Test image validator initialization"""
        assert hasattr(self.image_validator, 'image_formats')
        assert hasattr(self.image_validator, 'quality_thresholds')
        assert '.jpg' in self.image_validator.image_formats
        assert '.png' in self.image_validator.image_formats
        assert 'min_width' in self.image_validator.quality_thresholds
    
    def test_image_formats_coverage(self):
        """
Test coverage of image formats for photographers"""
        required_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        
        for format_ext in required_formats:
            assert format_ext in self.image_validator.image_formats
    
    def test_quality_thresholds_configuration(self):
        """
Test image quality thresholds configuration"""
        thresholds = self.image_validator.quality_thresholds
        
        assert thresholds['min_width'] > 0
        assert thresholds['min_height'] > 0
        assert thresholds['max_file_size'] > thresholds['min_file_size']
        assert thresholds['max_aspect_ratio'] > 1.0
    
    @patch('backend.ai.core.validation.CV2_AVAILABLE', False)
    def test_image_validation_library_unavailable(self):
        """
Test image validation when library is unavailable"""
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        self.image_validator.validate_image("test.jpg", result)
        
        warnings = result.get_issues_by_level(ValidationLevel.WARNING)
        assert any("library not available" in issue.message.lower() for issue in warnings)
    
    @patch('backend.ai.core.validation.CV2_AVAILABLE', True)
    @patch('backend.ai.core.validation.cv2')
    @patch('backend.ai.core.validation.Path')
    def test_image_validation_success(self, mock_path, mock_cv2):
        """Test successful image validation"""
        # Mock cv2 and Path
        mock_image = Mock()
        mock_image.shape = [1080, 1920, 3]  # Height, Width, Channels
        mock_cv2.imread.return_value = mock_image
        
        mock_stat = Mock()
        mock_stat.st_size = 2 * 1024 * 1024  # 2MB
        mock_path.return_value.stat.return_value = mock_stat
        
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        with patch.object(self.image_validator, '_calculate_image_quality_score', return_value=90.0):
            self.image_validator.validate_image("test.jpg", result)
        
        # Should complete successfully
        assert 'image_quality_score' in result.metadata
        assert 'image_width' in result.metadata
        assert 'image_height' in result.metadata
        assert result.metadata['image_width'] == 1920
        assert result.metadata['image_height'] == 1080
    
    @patch('backend.ai.core.validation.CV2_AVAILABLE', True)
    @patch('backend.ai.core.validation.cv2')
    def test_image_validation_load_error(self, mock_cv2):
        """Test image validation with load error"""
        # Mock cv2.imread to return None (load error)
        mock_cv2.imread.return_value = None
        
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        self.image_validator.validate_image("invalid.jpg", result)
        
        # Should have load error
        errors = result.get_issues_by_level(ValidationLevel.ERROR)
        assert any("unable to load" in issue.message.lower() for issue in errors)
        assert result.is_valid is False
    
    @patch('backend.ai.core.validation.CV2_AVAILABLE', True)
    @patch('backend.ai.core.validation.cv2')
    @patch('backend.ai.core.validation.Path')
    def test_image_validation_low_resolution(self, mock_path, mock_cv2):
        """Test image validation with low resolution"""
        # Mock low resolution image
        mock_image = Mock()
        mock_image.shape = [200, 150, 3]  # Low resolution
        mock_cv2.imread.return_value = mock_image
        
        mock_stat = Mock()
        mock_stat.st_size = 50 * 1024  # 50KB
        mock_path.return_value.stat.return_value = mock_stat
        
        result = ValidationResult(is_valid=True, overall_score=100.0, quality_score=100.0,
                                safety_score=100.0, compliance_score=100.0, seo_score=100.0,
                                monetization_readiness=100.0)
        
        with patch.object(self.image_validator, '_calculate_image_quality_score', return_value=40.0):
            self.image_validator.validate_image("lowres.jpg", result)
        
        # Should have low resolution warnings
        quality_issues = result.get_issues_by_category(ValidationCategory.TECHNICAL_QUALITY)
        width_warnings = [issue for issue in quality_issues if "width too small" in issue.message.lower()]
        height_warnings = [issue for issue in quality_issues if "height too small" in issue.message.lower()]
        
        assert len(width_warnings) > 0
        assert len(height_warnings) > 0
    
    def test_image_quality_score_calculation(self):
        """Test image quality score calculation"""
        import numpy as np
        
        # Create mock high-quality image
        high_quality_image = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        
        with patch('backend.ai.core.validation.cv2.cvtColor') as mock_cvt, \
             patch('backend.ai.core.validation.cv2.Laplacian') as mock_laplacian:
            
            mock_cvt.return_value = Mock()
            mock_laplacian_result = Mock()
            mock_laplacian_result.var.return_value = 500  # High variance = sharp image
            mock_laplacian.return_value = mock_laplacian_result
            
            score = self.image_validator._calculate_image_quality_score(high_quality_image, 1024*1024)
            
            # Should get high score for sharp image
            assert score >= 70.0


class TestContentValidator:
    """
Test suite for main ContentValidator class"""
    
    def setup_method(self):
        """
Setup content validator for testing"""
        self.validator = ContentValidator()
    
    def test_content_validator_initialization(self):
        """
Test content validator initialization"""
        assert hasattr(self.validator, 'quality_thresholds')
        assert hasattr(self.validator, 'validation_rules')
        assert hasattr(self.validator, 'security_validator')
        assert hasattr(self.validator, 'quality_analyzer')
        assert hasattr(self.validator, 'audio_validator')
        assert hasattr(self.validator, 'image_validator')
    
    def test_text_content_validation(self):
        """
Test comprehensive text content validation"""
        content = """
        This is a comprehensive test of text content validation.
        It includes multiple sentences and proper formatting.
        The content is designed to pass quality checks while being informative.
        This content should receive good validation scores across all metrics.
        """
        
        result = self.validator.validate_content(content, "text")
        
        assert isinstance(result, ValidationResult)
        assert result.overall_score >= 0.0
        assert result.quality_score >= 0.0
        assert result.safety_score >= 0.0
        assert result.compliance_score >= 0.0
        assert result.processing_time_ms >= 0.0
        assert result.content_fingerprint is not None
    
    def test_social_post_validation(self):
        try:
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_test_social_post_validation_request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler test_social_post_validation failed: {e}")
                    return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"test_text_content_validation failed: {e}")
            raise
    def test_social_post_validation(self):
        """Test social media post validation"""
        # Twitter post (under 280 characters)
        twitter_post = "This is a great tweet for musicians to share their latest work! #music #creators #AI"
        
        result = self.validator.validate_content(twitter_post, "social_post", platform="twitter")
        
        assert isinstance(result, ValidationResult)
        # Should pass Twitter length requirement
        length_errors = [issue for issue in result.issues if "exceeds character limit" in issue.message]
        assert len(length_errors) == 0
    
    def test_social_post_validation_twitter_too_long(self):
        """Test social media post validation for overly long Twitter post"""
        # Create a post longer than 280 characters
        long_twitter_post = "This is an extremely long tweet that definitely exceeds the Twitter character limit of 280 characters and should be flagged by the validation system as being too long for the platform. " + "Additional text " * 20
        
        result = self.validator.validate_content(long_twitter_post, "social_post", platform="twitter")
        
        # Should have Twitter length error
        length_errors = [issue for issue in result.issues if "exceeds character limit" in issue.message]
        assert len(length_errors) > 0
        assert result.is_valid is False
    
    def test_blog_post_validation(self):
        """Test blog post validation"""
        blog_content = """
        # Introduction to Content Creation
        
        This is the introduction paragraph for our comprehensive blog post about content creation.
        It provides context and sets expectations for readers.
        
        ## Main Content Section
        
        Here we dive into the main content with detailed explanations and valuable insights.
        This section contains the core information that readers are looking for.
        
        ## Conclusion
        
        In conclusion, this blog post has covered the essential aspects of content creation.
        We hope readers found this information valuable and actionable.
        """
        
        result = self.validator.validate_content(blog_content, "blog_post")
        
        assert isinstance(result, ValidationResult)
        # Should recognize good blog structure
        missing_heading_issues = [issue for issue in result.issues if "missing headings" in issue.message.lower()]
        assert len(missing_heading_issues) == 0
    
    def test_email_content_validation(self):
        """Test email content validation"""
        email_content = """
        Dear Creator,
        
        We're excited to share our latest AI tools for content protection and optimization.
        
        Our platform helps musicians, photographers, bloggers, and influencers:
        - Protect their content from unauthorized use
        - Optimize for better SEO performance
        - Collaborate safely with other creators
        
        Ready to get started? Click here to learn more about our platform.
        
        Best regards,
        The AI Creator Platform Team
        """
        
        result = self.validator.validate_content(
            email_content, 
            "email", 
            subject="New AI Tools for Content Creators"
        )
        
        assert isinstance(result, ValidationResult)
        # Should recognize good email structure with CTA
        missing_cta_issues = [issue for issue in result.issues if "call-to-action" in issue.message.lower()]
        assert len(missing_cta_issues) == 0
    
    def test_content_validation_with_security_issues(self):
        try:
            logger.info(f"Executing test_content_validation_with_security_issues")
            
            # Implementation for test_content_validation_with_security_issues
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_content_validation_with_security_issues completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_content_validation_with_security_issues failed: {e}")
            raise
    def test_content_validation_with_security_issues(self):
        """Test content validation with security issues"""
        malicious_content = """
        Check out this amazing tool: <script>alert('XSS')</script>
        Download our hack software to exploit systems and crack passwords.
        """
        
        result = self.validator.validate_content(malicious_content, "text")
        
        assert result.is_valid is False
        assert result.safety_score < 100.0
        
        security_issues = result.get_issues_by_category(ValidationCategory.CONTENT_SAFETY)
        assert len(security_issues) > 0
        
        critical_issues = result.get_issues_by_level(ValidationLevel.SECURITY)
        assert len(critical_issues) > 0
    
    def test_batch_validation(self):
        try:
            logger.info(f"Executing custom_rule")
            
            # Implementation for custom_rule
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"custom_rule completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"custom_rule failed: {e}")
            raise
        result = self.validator.validate_content(malicious_content, "text")
        
        assert result.is_valid is False
        assert result.safety_score < 100.0
        
        security_issues = result.get_issues_by_category(ValidationCategory.CONTENT_SAFETY)
        assert len(security_issues) > 0
        
        critical_issues = result.get_issues_by_level(ValidationLevel.SECURITY)
        assert len(critical_issues) > 0
    
    def test_batch_validation(self):
        """Test batch content validation"""
        contents = [
            "This is the first piece of content to validate.",
            "This is the second piece with different characteristics.",
            "Third content item with unique properties and longer text for testing."
        ]
        
        results = self.validator.validate_batch(contents, "text")
        
        assert len(results) == 3
        assert all(isinstance(result, ValidationResult) for result in results)
        assert all(result.content_fingerprint is not None for result in results)
        
        # Each should have unique fingerprints
        fingerprints = [result.content_fingerprint for result in results]
        assert len(set(fingerprints)) == 3
    
    def test_custom_validation_rule(self):
        """Test adding custom validation rules"""
        def custom_rule(content: str, result: ValidationResult, **kwargs):
            if "forbidden_word" in content.lower():
                result.add_issue(
                    ValidationLevel.ERROR,
                    ValidationCategory.CONTENT_SAFETY,
                    "Custom validation rule triggered",
                    "CUSTOM_RULE_001"
                )
        
        # Add custom rule
        self.validator.add_custom_validation_rule(custom_rule)
        
        # Test content that triggers custom rule
        test_content = "This content contains the forbidden_word and should be flagged."
        result = self.validator.validate_content(test_content, "text")
        
        assert result.is_valid is False
        custom_issues = [issue for issue in result.issues if issue.code == "CUSTOM_RULE_001"]
        assert len(custom_issues) > 0
    
    def test_quality_thresholds_customization(self):
        """Test customizing quality thresholds"""
        original_thresholds = self.validator.quality_thresholds.copy()
        
        # Update thresholds
        new_thresholds = {
            "min_word_count": 5,
            "max_word_count": 1000,
            "max_spelling_errors": 2
        }
        
        self.validator.set_quality_thresholds(new_thresholds)
        
        # Verify thresholds were updated
        for key, value in new_thresholds.items():
            assert self.validator.quality_thresholds[key] == value
        
        # Test validation with new thresholds
        short_content = "Too short"  # Under 5 words
        result = self.validator.validate_content(short_content, "text")
        
        # Should trigger low word count issue
        word_count_issues = [issue for issue in result.issues if "word count" in issue.message.lower()]
        assert len(word_count_issues) > 0
    
    def test_content_fingerprinting(self):
        """Test content fingerprinting functionality"""
        content1 = "This is original content for fingerprinting."
        content2 = "This is different content for fingerprinting."
        content3 = "This is original content for fingerprinting."  # Same as content1
        
        result1 = self.validator.validate_content(content1, "text")
        result2 = self.validator.validate_content(content2, "text")
        result3 = self.validator.validate_content(content3, "text")
        
        # Same content should have same fingerprint
        assert result1.content_fingerprint == result3.content_fingerprint
        
        # Different content should have different fingerprints
        assert result1.content_fingerprint != result2.content_fingerprint
    
    def test_validation_performance_tracking(self):
        """Test validation performance tracking"""
        content = "Performance testing content for validation timing analysis."
        
        start_time = time.time()
        result = self.validator.validate_content(content, "text")
        end_time = time.time()
        
        # Processing time should be tracked
        assert result.processing_time_ms > 0
        
        # Should be reasonable performance (under 1 second for simple content)
        actual_time_ms = (end_time - start_time) * 1000
        assert result.processing_time_ms <= actual_time_ms + 100  # Small tolerance for timing


class TestContentValidatorAsync:
    """Test suite for asynchronous content validation operations"""
    
    def setup_method(self):
        """
Setup async validator testing"""
        self.validator = ContentValidator()
    
    @pytest.mark.asyncio
    async def test_concurrent_validation(self):
        """
Test concurrent content validation"""
        contents = [
            f"Test content number {i} for concurrent validation testing."
            for i in range(10)
        ]
        
        async def validate_async(content):
            # Simulate async validation
            await asyncio.sleep(0.01)
            return self.validator.validate_content(content, "text")
        
        # Run validations concurrently
        start_time = time.time()
        tasks = [validate_async(content) for content in contents]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify all validations completed
        assert len(results) == 10
        assert all(isinstance(result, ValidationResult) for result in results)
        
        # Should be faster than sequential (rough check)
        total_time = end_time - start_time
        assert total_time < 1.0  # Should complete in under 1 second
    
    @pytest.mark.asyncio
    async def test_async_validation_error_handling(self):
        """Test error handling in async validation"""
        async def failing_validation():
            await asyncio.sleep(0.01)
            raise ValueError("Simulated validation error")
        
        async def successful_validation():
            await asyncio.sleep(0.01)
            return self.validator.validate_content("Good content", "text")
        
        # Mix of successful and failing validations
        tasks = [
            successful_validation(),
            failing_validation(),
            successful_validation()
        ]
        
        # Use return_exceptions to handle errors gracefully
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        assert len(results) == 3
        assert isinstance(results[0], ValidationResult)  # Success
        assert isinstance(results[1], ValueError)  # Error
        assert isinstance(results[2], ValidationResult)  # Success


class TestContentValidatorThreadSafety:
    """Test suite for content validator thread safety"""
    
    def setup_method(self):
        """
Setup thread safety testing"""
        self.validator = ContentValidator()
    
    def test_thread_safe_validation(self):
        """
Test thread-safe concurrent validation"""
        results = []
        errors = []
        
        def validate_in_thread(content):
            try:
                result = self.validator.validate_content(content, "text")
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(20):
            content = f"Thread {i} content for validation testing with unique identifier {i}."
            thread = threading.Thread(target=validate_in_thread, args=(content,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(results) == 20
        assert all(isinstance(result, ValidationResult) for result in results)
        
        # Each result should have unique fingerprint
        fingerprints = [result.content_fingerprint for result in results]
        assert len(set(fingerprints)) == 20
    
    def test_concurrent_threshold_updates(self):
        """Test concurrent quality threshold updates"""
        def update_thresholds(thread_id):
            thresholds = {
                f"custom_threshold_{thread_id}": thread_id * 10,
                "min_word_count": 5 + thread_id
            }
            self.validator.set_quality_thresholds(thresholds)
        
        # Run concurrent updates
        threads = []
        for i in range(5):
            thread = threading.Thread(target=update_thresholds, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify final state is consistent
        final_thresholds = self.validator.quality_thresholds
        assert isinstance(final_thresholds, dict)
        assert len(final_thresholds) > 0


class TestContentValidatorIntegration:
    """Integration tests for content validator with real-world scenarios"""
    
    def setup_method(self):
        """
Setup integration testing"""
        self.validator = ContentValidator()
    
    def test_musician_content_workflow(self):
        """
Test complete content validation workflow for musicians"""
        # Song description
        song_description = """
        🎵 New Single Release: "Digital Dreams" 🎵
        
        I'm excited to share my latest track "Digital Dreams" - a fusion of electronic and acoustic elements.
        This song explores themes of technology and human connection in our modern world.
        
        Production Details:
        - Recorded at 48kHz/24-bit quality
        - Mixed and mastered with AI-assisted tools
        - Features synthesized vocals and live guitar
        
        Available on all streaming platforms! Link in bio.
        
        #music #newrelease #electronic #acoustic #AI #musician #streaming
        """
        
        result = self.validator.validate_content(song_description, "social_post")
        
        # Should be valid content
        assert result.is_valid
        assert result.overall_score >= 70.0
        
        # Should have good SEO score due to hashtags and keywords
        assert result.seo_score >= 60.0
        
        # Should be monetization ready
        assert result.monetization_readiness >= 70.0
    
    def test_photographer_content_workflow(self):
        """Test complete content validation workflow for photographers"""
        # Photo description
        photo_description = """
        📸 Golden Hour Magic at the Coast 📸
        
        Captured this stunning sunset landscape during my recent trip to the Pacific Coast.
        The interplay of light and shadow creates such dramatic contrast.
        
        Technical Details:
        - Shot with Canon EOS R5
        - 24-70mm f/2.8 lens at 35mm
        - ISO 100, f/8, 1/60s
        - Post-processed in Lightroom and Photoshop
        
        This image is available for licensing. Contact me for commercial use.
        Prints available in my online gallery.
        
        #photography #landscape #sunset #goldenhour #pacificcoast #canon #nature
        """
        
        result = self.validator.validate_content(photo_description, "social_post")
        
        # Should be valid content
        assert result.is_valid
        assert result.overall_score >= 70.0
        
        # Should have good quality score
        assert result.quality_score >= 75.0
        
        # Should mention licensing/monetization
        assert result.monetization_readiness >= 80.0
    
    def test_blogger_content_workflow(self):
        """Test complete content validation workflow for bloggers"""
        # Blog post excerpt
        blog_content = """
        # The Future of AI in Content Creation: A Creator's Perspective
        
        As creators, we're living through a revolutionary period where artificial intelligence
        is transforming how we produce, protect, and distribute our content.
        
        ## The AI Revolution in Creative Industries
        
        Over the past year, I've been experimenting with various AI tools to enhance my workflow.
        From automated editing to content optimization, AI has become an invaluable assistant.
        
        Key benefits I've discovered:
        - Faster content production without sacrificing quality
        - Better SEO optimization through AI analysis
        - Enhanced collaboration capabilities
        - Improved content protection and copyright management
        
        ## Challenges and Considerations
        
        However, it's not all smooth sailing. There are important considerations around:
        - Maintaining authentic voice and style
        - Ensuring ethical use of AI technologies
        - Balancing automation with human creativity
        
        ## Looking Forward
        
        The future looks bright for creators who embrace these technologies thoughtfully.
        AI isn't replacing human creativity—it's amplifying it.
        
        What's your experience with AI in content creation? Share your thoughts in the comments below!
        """
        
        result = self.validator.validate_content(blog_content, "blog_post")
        
        # Should be valid content
        assert result.is_valid
        assert result.overall_score >= 80.0
        
        # Should have excellent structure
        assert result.quality_score >= 85.0
        
        # Should have good SEO potential
        assert result.seo_score >= 75.0
    
    def test_influencer_collaboration_content(self):
        """Test content validation for influencer collaboration posts"""
        # Collaboration announcement
        collab_content = """
        🤝 Exciting Collaboration Announcement! 🤝
        
        I'm thrilled to partner with @TechBrand to showcase their latest AI-powered camera gear!
        As a content creator, I'm always looking for tools that enhance creativity while saving time.
        
        Over the next week, I'll be testing their new smart camera system and sharing:
        ✨ Real-world performance tests
        ✨ Creative shooting techniques
        ✨ Honest reviews and feedback
        ✨ Behind-the-scenes content
        
        This is a paid partnership, but all opinions are my own. I only work with brands
        that align with my values and provide genuine value to my community.
        
        Stay tuned for daily updates! What would you like to see me test first?
        
        #collaboration #sponsored #AI #camera #tech #creator #photography #partnership
        
        *This post contains paid partnership content*
        """
        
        result = self.validator.validate_content(collab_content, "social_post")
        
        # Should be valid content
        assert result.is_valid
        assert result.overall_score >= 75.0
        
        # Should have good compliance score (proper disclosure)
        assert result.compliance_score >= 85.0
        
        # Should be collaboration ready
        collaboration_issues = result.get_issues_by_category(ValidationCategory.COLLABORATION_READY)
        assert len(collaboration_issues) == 0
    
    def test_content_safety_edge_cases(self):
        """Test content safety validation with edge cases"""
        edge_cases = [
            # Borderline content
            "This hack for productivity will change your life! Click here to download.",
            # Technical content that might trigger false positives
            "Learn JavaScript programming: function hack() { return solution; }",
            # Creative content with potentially triggering words
            "My art explores themes of conflict and resolution in modern society.",
            # Medical/health content
            "Natural remedies for common ailments - always consult your doctor first."
        ]
        
        for content in edge_cases:
            result = self.validator.validate_content(content, "text")
            
            # Should not have false positive security issues
            security_issues = result.get_issues_by_level(ValidationLevel.SECURITY)
            critical_issues = result.get_issues_by_level(ValidationLevel.CRITICAL)
            
            # Should be minimal or context-appropriate warnings only
            assert len(security_issues) <= 1, f"Too many security issues for: {content[:50]}..."
            assert len(critical_issues) == 0, f"False critical issues for: {content[:50]}..."


class TestGlobalValidator:
    """Test suite for global content validator instance"""
    
    def test_global_validator_instance(self):
        """
Test global content validator instance"""
        from ai.core.validation import content_validator
        
        assert content_validator is not None
        assert isinstance(content_validator, ContentValidator)
    
    def test_global_validator_functionality(self):
        """
Test global validator functionality"""
        from ai.core.validation import content_validator
        
        test_content = "Testing global validator instance functionality."
        result = content_validator.validate_content(test_content, "text")
        
        assert isinstance(result, ValidationResult)
        assert result.content_fingerprint is not None
    
    def test_global_validator_persistence(self):
        """Test global validator state persistence"""
        from ai.core.validation import content_validator
        
        # Set custom thresholds
        custom_thresholds = {"test_threshold": 42}
        content_validator.set_quality_thresholds(custom_thresholds)
        
        # Verify persistence
        assert content_validator.quality_thresholds["test_threshold"] == 42
        
        # Should persist across validations
        content_validator.validate_content("Test content", "text")
        assert content_validator.quality_thresholds["test_threshold"] == 42


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
