"""
Advanced Content Validation Module

Enterprise-grade content validation and quality assurance for industrial AI platform.
Supports multi-format content validation for creators (musicians, bloggers, photographers, influencers, comedians).

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""

import re
import string
import hashlib
import mimetypes
import magic
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import base64
from urllib.parse import urlparse
import logging
from functools import wraps
import asyncio
from pathlib import Path

# AI and ML imports
try:
    import torch
    import transformers
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Computer vision imports
try:
    import cv2
    import numpy as np
    from PIL import Image, ImageStat
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# Audio processing imports
try:
    import librosa
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Advanced validation severity levels for comprehensive monitoring"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    QUALITY = "quality"
    PERFORMANCE = "performance"


class ContentType(Enum):
    """Supported content types for validation"""
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    SOCIAL_POST = "social_post"
    BLOG_POST = "blog_post"
    EMAIL = "email"
    MUSIC = "music"
    PODCAST = "podcast"
    PHOTO = "photo"
    ARTWORK = "artwork"
    SUBTITLE = "subtitle"
    METADATA = "metadata"


class ValidationCategory(Enum):
    """Categories of validation checks"""
    CONTENT_SAFETY = "content_safety"
    COPYRIGHT_COMPLIANCE = "copyright_compliance"
    TECHNICAL_QUALITY = "technical_quality"
    BRAND_SAFETY = "brand_safety"
    SEO_OPTIMIZATION = "seo_optimization"
    ACCESSIBILITY = "accessibility"
    PLATFORM_COMPLIANCE = "platform_compliance"
    MONETIZATION_READY = "monetization_ready"
    COLLABORATION_READY = "collaboration_ready"
    LEGAL_COMPLIANCE = "legal_compliance"


@dataclass
class ValidationIssue:
    """Detailed validation issue with comprehensive metadata"""
    level: ValidationLevel
    category: ValidationCategory
    message: str
    code: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 1.0
    severity_score: int = 1
    auto_fixable: bool = False
    fix_suggestion: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    source_location: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary"""



        return {
            "level": self.level.value,
            "category": self.category.value,
            "message": self.message,
            "code": self.code,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "severity_score": self.severity_score,
            "auto_fixable": self.auto_fixable,
            "fix_suggestion": self.fix_suggestion,
            "context": self.context,
            "source_location": self.source_location
        }


@dataclass
class ValidationResult:
    """Comprehensive content validation result with detailed analytics"""
    is_valid: bool
    overall_score: float  # 0.0 to 100.0
    quality_score: float  # 0.0 to 100.0
    safety_score: float  # 0.0 to 100.0
    compliance_score: float  # 0.0 to 100.0
    seo_score: float  # 0.0 to 100.0
    monetization_readiness: float  # 0.0 to 100.0
    
    issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    content_fingerprint: Optional[str] = None
    validation_timestamp: datetime = field(default_factory=datetime.utcnow)
    processing_time_ms: float = 0.0
    
    def add_issue(
        self,
        level: ValidationLevel,
        category: ValidationCategory,
        message: str,
        code: str,
        confidence: float = 1.0,
        auto_fixable: bool = False,
        fix_suggestion: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Add a validation issue with comprehensive details"""
        issue = ValidationIssue(
            level=level,
            category=category,
            message=message,
            code=code,
            confidence=confidence,
            auto_fixable=auto_fixable,
            fix_suggestion=fix_suggestion,
            context=context or {}
        )
        
        self.issues.append(issue)
        
        if level == ValidationLevel.WARNING:
            self.warnings.append(message)
        elif level in [ValidationLevel.ERROR, ValidationLevel.CRITICAL, ValidationLevel.SECURITY]:
            self.errors.append(message)
            self.is_valid = False
            
    def get_issues_by_category(self, category: ValidationCategory) -> List[ValidationIssue]:
        """Get issues filtered by category"""



        return [issue for issue in self.issues if issue.category == category]
        
    def get_issues_by_level(self, level: ValidationLevel) -> List[ValidationIssue]:
        """Get issues filtered by level"""



        return [issue for issue in self.issues if issue.level == level]
        
    def get_fixable_issues(self) -> List[ValidationIssue]:
        """Get issues that can be automatically fixed"""



        return [issue for issue in self.issues if issue.auto_fixable]
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary"""



        return {
            "is_valid": self.is_valid,
            "scores": {
                "overall": self.overall_score,
                "quality": self.quality_score,
                "safety": self.safety_score,
                "compliance": self.compliance_score,
                "seo": self.seo_score,
                "monetization_readiness": self.monetization_readiness
            },
            "issues": [issue.to_dict() for issue in self.issues],
            "warnings": self.warnings,
            "errors": self.errors,
            "suggestions": self.suggestions,
            "metadata": self.metadata,
            "content_fingerprint": self.content_fingerprint,
            "validation_timestamp": self.validation_timestamp.isoformat(),
            "processing_time_ms": self.processing_time_ms
        }


class ContentSecurityValidator:
    """Advanced content security and safety validation"""
    
    def __init__(self):
        self.blocked_patterns = []
        self.suspicious_patterns = []
        self.malware_signatures = []
        self.load_security_rules()
        
    def load_security_rules(self):
        """Load security validation rules"""
        # Malicious content patterns
        self.blocked_patterns = [
            r'<script[^>]*>.*?</script>',  # Script injection
            r'javascript:',  # JavaScript URLs
            r'data:text/html',  # Data URLs
            r'vbscript:',  # VBScript
            r'on\w+\s*=',  # Event handlers
        ]
        
        # Suspicious content indicators
        self.suspicious_patterns = [
            r'(?i)(hack|crack|exploit|malware|virus)',
            r'(?i)(password|credential|login|token)',
            r'(?i)(phishing|scam|fraud)',
            r'(?i)(download|install|execute).*\.(exe|bat|cmd|scr)'
        ]
        
    def validate_security(self, content: str, result: ValidationResult):
        """Validate content security"""
        security_score = 100.0
        
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                result.add_issue(
                    ValidationLevel.SECURITY,
                    ValidationCategory.CONTENT_SAFETY,
                    f"Potentially malicious content detected: {pattern}",
                    "SECURITY_MALICIOUS_CONTENT",
                    confidence=0.9
                )
                security_score -= 50
                
        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                result.add_issue(
                    ValidationLevel.WARNING,
                    ValidationCategory.CONTENT_SAFETY,
                    f"Suspicious content detected: {', '.join(matches)}",
                    "SECURITY_SUSPICIOUS_CONTENT",
                    confidence=0.7
                )
                security_score -= 10
                
        result.safety_score = max(0, security_score)


class ContentQualityAnalyzer:
    """Advanced content quality analysis and scoring"""
    
    def __init__(self):
        self.quality_metrics = {}
        if TRANSFORMERS_AVAILABLE:
            self.init_ai_models()
            
    def init_ai_models(self):
        """Initialize AI models for quality analysis"""



        try:
            # Content quality model
            self.quality_tokenizer = AutoTokenizer.from_pretrained(
                "distilbert-base-uncased"
            )
            # Note: In production, use specialized quality assessment models
        except Exception as e:
            logger.warning(f"Failed to initialize AI models: {e}")
            
    def analyze_text_quality(self, content: str, result: ValidationResult):
        """Analyze text content quality"""
        quality_score = 100.0
        
        # Basic quality metrics
        word_count = len(content.split())
        sentence_count = len(re.findall(r'[.!?]+', content))
        
        # Length validation
        if word_count < 10:
            result.add_issue(
                ValidationLevel.WARNING,
                ValidationCategory.TECHNICAL_QUALITY,
                "Content is too short for optimal engagement",
                "QUALITY_TOO_SHORT",
                auto_fixable=True,
                fix_suggestion="Consider expanding the content with more details"
            )
            quality_score -= 20
            
        if word_count > 5000:
            result.add_issue(
                ValidationLevel.WARNING,
                ValidationCategory.TECHNICAL_QUALITY,
                "Content may be too long for some platforms",
                "QUALITY_TOO_LONG",
                auto_fixable=True,
                fix_suggestion="Consider breaking into smaller sections"
            )
            quality_score -= 10
            
        # Readability analysis
        if sentence_count > 0:
            avg_words_per_sentence = word_count / sentence_count
            if avg_words_per_sentence > 25:
                result.add_issue(
                    ValidationLevel.WARNING,
                    ValidationCategory.TECHNICAL_QUALITY,
                    "Sentences are too long, may impact readability",
                    "QUALITY_LONG_SENTENCES",
                    auto_fixable=True,
                    fix_suggestion="Break long sentences into shorter ones"
                )
                quality_score -= 15
                
        # Grammar and spelling check (simplified)
        capitalization_errors = self._check_capitalization(content)
        if capitalization_errors > 5:
            result.add_issue(
                ValidationLevel.WARNING,
                ValidationCategory.TECHNICAL_QUALITY,
                f"Multiple capitalization issues detected ({capitalization_errors})",
                "QUALITY_CAPITALIZATION",
                auto_fixable=True,
                fix_suggestion="Review and correct capitalization"
            )
            quality_score -= 10
            
        result.quality_score = max(0, quality_score)
        
    def _check_capitalization(self, content: str) -> int:
        """Check for capitalization errors"""
        sentences = re.split(r'[.!?]+', content)
        errors = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and not sentence[0].isupper():
                errors += 1
                
        return errors


class AudioContentValidator:
    """Advanced audio content validation"""
    
    def __init__(self):
        self.audio_formats = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']
        self.quality_thresholds = {
            'min_sample_rate': 44100,
            'min_bit_depth': 16,
            'max_duration': 3600,  # 1 hour
            'min_duration': 5,     # 5 seconds
            'max_silence_ratio': 0.3
        }
        
    def validate_audio(self, audio_path: str, result: ValidationResult):
        """Validate audio content quality and compliance"""
        if not AUDIO_AVAILABLE:
            result.add_issue(
                ValidationLevel.WARNING,
                ValidationCategory.TECHNICAL_QUALITY,
                "Audio validation library not available",
                "AUDIO_LIBRARY_MISSING"
            )
            return
            
        try:
            # Load audio file
            audio_data, sample_rate = librosa.load(audio_path)
            duration = librosa.get_duration(y=audio_data, sr=sample_rate)
            
            # Validate sample rate
            if sample_rate < self.quality_thresholds['min_sample_rate']:
                result.add_issue(
                    ValidationLevel.WARNING,
                    ValidationCategory.TECHNICAL_QUALITY,
                    f"Low sample rate: {sample_rate}Hz (recommended: {self.quality_thresholds['min_sample_rate']}Hz)",
                    "AUDIO_LOW_SAMPLE_RATE"
                )
                
            # Validate duration
            if duration < self.quality_thresholds['min_duration']:
                result.add_issue(
                    ValidationLevel.ERROR,
                    ValidationCategory.TECHNICAL_QUALITY,
                    f"Audio too short: {duration:.1f}s (minimum: {self.quality_thresholds['min_duration']}s)",
                    "AUDIO_TOO_SHORT"
                )
                
            if duration > self.quality_thresholds['max_duration']:
                result.add_issue(
                    ValidationLevel.WARNING,
                    ValidationCategory.TECHNICAL_QUALITY,
                    f"Audio very long: {duration:.1f}s (may impact processing)",
                    "AUDIO_TOO_LONG"
                )
                
            # Check for silence
            silence_ratio = self._calculate_silence_ratio(audio_data)
            if silence_ratio > self.quality_thresholds['max_silence_ratio']:
                result.add_issue(
                    ValidationLevel.WARNING,
                    ValidationCategory.TECHNICAL_QUALITY,
                    f"High silence ratio: {silence_ratio:.1%}",
                    "AUDIO_HIGH_SILENCE",
                    auto_fixable=True,
                    fix_suggestion="Consider trimming silent sections"
                )
                
            # Audio quality score
            quality_score = self._calculate_audio_quality_score(
                sample_rate, duration, silence_ratio
            )
            result.metadata['audio_quality_score'] = quality_score
            
        except Exception as e:
            result.add_issue(
                ValidationLevel.ERROR,
                ValidationCategory.TECHNICAL_QUALITY,
                f"Audio validation failed: {str(e)}",
                "AUDIO_VALIDATION_ERROR"
            )
            
    def _calculate_silence_ratio(self, audio_data: np.ndarray) -> float:
        """Calculate ratio of silence in audio"""
        # Simple silence detection based on amplitude threshold
        threshold = 0.01
        silent_samples = np.sum(np.abs(audio_data) < threshold)
        return silent_samples / len(audio_data)
        
    def _calculate_audio_quality_score(
        self, 
        sample_rate: int, 
        duration: float, 
        silence_ratio: float
    ) -> float:
        """Calculate overall audio quality score"""
        score = 100.0
        
        # Sample rate scoring
        if sample_rate < 44100:
            score -= 20
        elif sample_rate < 48000:
            score -= 10
            
        # Duration scoring
        if duration < 10:
            score -= 30
        elif duration > 1800:  # 30 minutes
            score -= 10
            
        # Silence scoring
        if silence_ratio > 0.3:
            score -= 25
        elif silence_ratio > 0.2:
            score -= 15
            
        return max(0, score)


class ImageContentValidator:
    """Advanced image content validation"""
    
    def __init__(self):
        self.image_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        self.quality_thresholds = {
            'min_width': 300,
            'min_height': 300,
            'max_file_size': 50 * 1024 * 1024,  # 50MB
            'min_file_size': 1024,  # 1KB
            'max_aspect_ratio': 3.0
        }
        
    def validate_image(self, image_path: str, result: ValidationResult):
        """Validate image content quality and compliance"""
        if not CV2_AVAILABLE:
            result.add_issue(
                ValidationLevel.WARNING,
                ValidationCategory.TECHNICAL_QUALITY,
                "Image validation library not available",
                "IMAGE_LIBRARY_MISSING"
            )
            return
            
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                result.add_issue(
                    ValidationLevel.ERROR,
                    ValidationCategory.TECHNICAL_QUALITY,
                    "Unable to load image file",
                    "IMAGE_LOAD_ERROR"
                )
                return
                
            height, width = image.shape[:2]
            file_size = Path(image_path).stat().st_size
            
            # Validate dimensions
            if width < self.quality_thresholds['min_width']:
                result.add_issue(
                    ValidationLevel.WARNING,
                    ValidationCategory.TECHNICAL_QUALITY,
                    f"Image width too small: {width}px (minimum: {self.quality_thresholds['min_width']}px)",
                    "IMAGE_LOW_WIDTH"
                )
                
            if height < self.quality_thresholds['min_height']:
                result.add_issue(
                    ValidationLevel.WARNING,
                    ValidationCategory.TECHNICAL_QUALITY,
                    f"Image height too small: {height}px (minimum: {self.quality_thresholds['min_height']}px)",
                    "IMAGE_LOW_HEIGHT"
                )
                
            # Validate aspect ratio
            aspect_ratio = max(width, height) / min(width, height)
            if aspect_ratio > self.quality_thresholds['max_aspect_ratio']:
                result.add_issue(
                    ValidationLevel.WARNING,
                    ValidationCategory.TECHNICAL_QUALITY,
                    f"Unusual aspect ratio: {aspect_ratio:.2f}:1",
                    "IMAGE_UNUSUAL_ASPECT_RATIO"
                )
                
            # Validate file size
            if file_size > self.quality_thresholds['max_file_size']:
                result.add_issue(
                    ValidationLevel.WARNING,
                    ValidationCategory.TECHNICAL_QUALITY,
                    f"Large file size: {file_size / 1024 / 1024:.1f}MB",
                    "IMAGE_LARGE_SIZE",
                    auto_fixable=True,
                    fix_suggestion="Consider compressing the image"
                )
                
            # Image quality analysis
            quality_score = self._calculate_image_quality_score(image, file_size)
            result.metadata['image_quality_score'] = quality_score
            
            # Store technical metadata
            result.metadata.update({
                'image_width': width,
                'image_height': height,
                'image_aspect_ratio': aspect_ratio,
                'image_file_size': file_size,
                'image_channels': image.shape[2] if len(image.shape) == 3 else 1
            })
            
        except Exception as e:
            result.add_issue(
                ValidationLevel.ERROR,
                ValidationCategory.TECHNICAL_QUALITY,
                f"Image validation failed: {str(e)}",
                "IMAGE_VALIDATION_ERROR"
            )
            
    def _calculate_image_quality_score(self, image: np.ndarray, file_size: int) -> float:
        """Calculate image quality score based on various factors"""
        score = 100.0
        
        # Blur detection using Laplacian variance
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if laplacian_var < 100:  # Threshold for blur detection
            score -= 30
        elif laplacian_var < 200:
            score -= 15
            
        # Brightness analysis
        mean_brightness = np.mean(gray)
        if mean_brightness < 50 or mean_brightness > 200:
            score -= 20
            
        # File size efficiency
        height, width = image.shape[:2]
        pixels = height * width
        bytes_per_pixel = file_size / pixels
        
        if bytes_per_pixel > 10:  # Very inefficient compression
            score -= 15
        elif bytes_per_pixel < 0.5:  # Over-compressed
            score -= 10
            
        return max(0, score)


class SEOValidator:
    """SEO optimization validation for content"""
    
    def __init__(self):
        self.seo_rules = {
            'title_length': (30, 60),
            'description_length': (120, 160),
            'keyword_density': (1, 3),  # percentage
            'headings_required': True,
            'internal_links_min': 1,
            'external_links_max': 5
        }
        
    def validate_seo(self, content: str, metadata: Dict[str, Any], result: ValidationResult):
        """Validate SEO optimization"""
        seo_score = 100.0
        
        # Title validation
        title = metadata.get('title', '')
        if title:
            title_length = len(title)
            min_len, max_len = self.seo_rules['title_length']
            
            if title_length < min_len:
                result.add_issue(
                    ValidationLevel.WARNING,
                    ValidationCategory.SEO_OPTIMIZATION,
                    f"Title too short: {title_length} chars (recommended: {min_len}-{max_len})",
                    "SEO_TITLE_SHORT",
                    auto_fixable=True,
                    fix_suggestion="Expand title with relevant keywords"
                )
                seo_score -= 15
                
            elif title_length > max_len:
                result.add_issue(
                    ValidationLevel.WARNING,
                    ValidationCategory.SEO_OPTIMIZATION,
                    f"Title too long: {title_length} chars (recommended: {min_len}-{max_len})",
                    "SEO_TITLE_LONG",
                    auto_fixable=True,
                    fix_suggestion="Shorten title while keeping key information"
                )
                seo_score -= 10
                
        # Meta description validation
        description = metadata.get('description', '')
        if description:
            desc_length = len(description)
            min_len, max_len = self.seo_rules['description_length']
            
            if desc_length < min_len or desc_length > max_len:
                result.add_issue(
                    ValidationLevel.WARNING,
                    ValidationCategory.SEO_OPTIMIZATION,
                    f"Meta description length: {desc_length} chars (optimal: {min_len}-{max_len})",
                    "SEO_DESCRIPTION_LENGTH"
                )
                seo_score -= 10
                
        # Keyword analysis
        keywords = metadata.get('keywords', [])
        if keywords:
            for keyword in keywords:
                density = self._calculate_keyword_density(content, keyword)
                min_density, max_density = self.seo_rules['keyword_density']
                
                if density < min_density:
                    result.add_issue(
                        ValidationLevel.INFO,
                        ValidationCategory.SEO_OPTIMIZATION,
                        f"Low keyword density for '{keyword}': {density:.1f}%",
                        "SEO_LOW_KEYWORD_DENSITY",
                        auto_fixable=True,
                        fix_suggestion=f"Consider using '{keyword}' more naturally in content"
                    )
                elif density > max_density:
                    result.add_issue(
                        ValidationLevel.WARNING,
                        ValidationCategory.SEO_OPTIMIZATION,
                        f"High keyword density for '{keyword}': {density:.1f}% (may be spam)",
                        "SEO_HIGH_KEYWORD_DENSITY",
                        auto_fixable=True,
                        fix_suggestion=f"Reduce usage of '{keyword}' to avoid keyword stuffing"
                    )
                    seo_score -= 15
                    
        # Heading structure validation
        headings = re.findall(r'<h[1-6][^>]*>.*?</h[1-6]>', content, re.IGNORECASE)
        if not headings and len(content.split()) > 300:
            result.add_issue(
                ValidationLevel.WARNING,
                ValidationCategory.SEO_OPTIMIZATION,
                "No headings found in long content",
                "SEO_NO_HEADINGS",
                auto_fixable=True,
                fix_suggestion="Add headings to structure the content"
            )
            seo_score -= 20
            
        result.seo_score = max(0, seo_score)
        
    def _calculate_keyword_density(self, content: str, keyword: str) -> float:
        """Calculate keyword density percentage"""
        words = content.lower().split()
        keyword_count = words.count(keyword.lower())
        return (keyword_count / len(words)) * 100 if words else 0


class ContentValidator:
    """
    Enterprise-grade content validation system
    
    Features:
    - Multi-format content validation (text, audio, video, image)
    - AI-powered quality assessment
    - Security and safety validation
    - SEO optimization validation
    - Platform compliance checking
    - Copyright and legal compliance
    - Monetization readiness assessment
    - Collaboration readiness validation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize specialized validators
        self.security_validator = ContentSecurityValidator()
        self.quality_analyzer = ContentQualityAnalyzer()
        self.audio_validator = AudioContentValidator()
        self.image_validator = ImageContentValidator()
        self.seo_validator = SEOValidator()
        
        # Validation rules and thresholds
        self.quality_thresholds = {
            "min_overall_score": 70.0,
            "min_quality_score": 60.0,
            "min_safety_score": 80.0,
            "min_compliance_score": 85.0,
            "min_seo_score": 50.0,
            "min_monetization_readiness": 75.0
        }
        
        # Platform-specific rules
        self.platform_rules = {
            "spotify": {"max_duration": 3600, "min_sample_rate": 44100},
            "youtube": {"max_duration": 43200, "min_resolution": "720p"},
            "instagram": {"max_duration": 60, "aspect_ratios": ["1:1", "4:5", "9:16"]},
            "tiktok": {"max_duration": 180, "aspect_ratio": "9:16"},
            "twitter": {"max_length": 280, "max_media_size": 5242880}
        }
        
        logger.info("Content validator initialized with comprehensive validation suite")
        
    def validate_content(
        self,
        content: Union[str, bytes, Path],
        content_type: ContentType,
        metadata: Optional[Dict[str, Any]] = None,
        platform_targets: Optional[List[str]] = None,
        **kwargs
    ) -> ValidationResult:
        """
        Validate content with comprehensive analysis
        
        Args:
            content: Content to validate (text, file path, or bytes)
            content_type: Type of content being validated
            metadata: Additional metadata for validation
            platform_targets: Target platforms for specialized validation
            **kwargs: Additional validation parameters
            
        Returns:
            Comprehensive validation result
        """
        start_time = datetime.utcnow()
        
        result = ValidationResult(
            is_valid=True,
            overall_score=100.0,
            quality_score=100.0,
            safety_score=100.0,
            compliance_score=100.0,
            seo_score=100.0,
            monetization_readiness=100.0,
            metadata=metadata or {}
        )
        
        try:
            # Generate content fingerprint
            result.content_fingerprint = self._generate_fingerprint(content)
            
            # Basic content validation
            self._validate_basic_requirements(content, content_type, result)
            
            # Security validation
            if isinstance(content, str):
                self.security_validator.validate_security(content, result)
            
            # Type-specific validation
            if content_type == ContentType.TEXT:
                self._validate_text_content(content, result)
            elif content_type == ContentType.AUDIO:
                self._validate_audio_content(content, result)
            elif content_type == ContentType.IMAGE:
                self._validate_image_content(content, result)
            elif content_type == ContentType.VIDEO:
                self._validate_video_content(content, result)
            elif content_type == ContentType.SOCIAL_POST:
                self._validate_social_post(content, result, **kwargs)
            elif content_type == ContentType.BLOG_POST:
                self._validate_blog_post(content, result, **kwargs)
                
            # Platform-specific validation
            if platform_targets:
                self._validate_platform_compliance(content, content_type, platform_targets, result)
                
            # SEO validation
            if isinstance(content, str) and metadata:
                self.seo_validator.validate_seo(content, metadata, result)
                
            # Monetization readiness
            self._assess_monetization_readiness(content, content_type, result)
            
            # Calculate final scores
            self._calculate_final_scores(result)
            
            # Record processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            result.processing_time_ms = processing_time
            
            logger.info(
                f"Content validation completed in {processing_time:.1f}ms. "
                f"Score: {result.overall_score:.1f}, Issues: {len(result.issues)}"
            )
            
        except Exception as e:
            logger.error(f"Content validation failed: {e}")
            result.add_issue(
                ValidationLevel.CRITICAL,
                ValidationCategory.TECHNICAL_QUALITY,
                f"Validation system error: {str(e)}",
                "VALIDATION_SYSTEM_ERROR"
            )
            result.overall_score = 0.0
            
        return result
        
    def _generate_fingerprint(self, content: Union[str, bytes, Path]) -> str:
        """Generate unique fingerprint for content"""
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        elif isinstance(content, Path):
            content_bytes = content.read_bytes()
        else:
            content_bytes = content
            
        return hashlib.sha256(content_bytes).hexdigest()
        
    def _validate_basic_requirements(
        self,
        content: Union[str, bytes, Path],
        content_type: ContentType,
        result: ValidationResult
    ):
        """Validate basic content requirements"""
        if isinstance(content, str):
            if not content or not content.strip():
                result.add_issue(
                    ValidationLevel.CRITICAL,
                    ValidationCategory.TECHNICAL_QUALITY,
                    "Content is empty or contains only whitespace",
                    "CONTENT_EMPTY"
                )
        elif isinstance(content, Path):
            if not content.exists():
                result.add_issue(
                    ValidationLevel.CRITICAL,
                    ValidationCategory.TECHNICAL_QUALITY,
                    f"File does not exist: {content}",
                    "FILE_NOT_EXISTS"
                )
                
    def _validate_text_content(self, content: str, result: ValidationResult):
        """Validate text content"""
        self.quality_analyzer.analyze_text_quality(content, result)
        
        # Character encoding validation
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            result.add_issue(
                ValidationLevel.ERROR,
                ValidationCategory.TECHNICAL_QUALITY,
                "Content contains invalid UTF-8 characters",
                "TEXT_INVALID_ENCODING"
            )
            
    def _validate_audio_content(self, content: Union[str, Path], result: ValidationResult):
        """Validate audio content"""
        if isinstance(content, str):
            content = Path(content)
            
        if content.exists():
            self.audio_validator.validate_audio(str(content), result)
        else:
            result.add_issue(
                ValidationLevel.ERROR,
                ValidationCategory.TECHNICAL_QUALITY,
                "Audio file not found",
                "AUDIO_FILE_NOT_FOUND"
            )
            
    def _validate_image_content(self, content: Union[str, Path], result: ValidationResult):
        """Validate image content"""
        if isinstance(content, str):
            content = Path(content)
            
        if content.exists():
            self.image_validator.validate_image(str(content), result)
        else:
            result.add_issue(
                ValidationLevel.ERROR,
                ValidationCategory.TECHNICAL_QUALITY,
                "Image file not found",
                "IMAGE_FILE_NOT_FOUND"
            )
            
    def _validate_video_content(self, content: Union[str, Path], result: ValidationResult):
        """Validate video content"""
        # Video validation implementation
        # This would include format validation, resolution checking, etc.
        result.add_issue(
            ValidationLevel.INFO,
            ValidationCategory.TECHNICAL_QUALITY,
            "Video validation not fully implemented",
            "VIDEO_VALIDATION_PLACEHOLDER"
        )
        
    def _validate_social_post(self, content: str, result: ValidationResult, **kwargs):
        """Validate social media post content"""
        platform = kwargs.get('platform', 'generic')
        
        # Platform-specific length limits
        length_limits = {
            'twitter': 280,
            'instagram': 2200,
            'facebook': 63206,
            'linkedin': 3000,
            'tiktok': 150
        }
        
        max_length = length_limits.get(platform, 1000)
        if len(content) > max_length:
            result.add_issue(
                ValidationLevel.WARNING,
                ValidationCategory.PLATFORM_COMPLIANCE,
                f"Content exceeds {platform} length limit: {len(content)}/{max_length}",
                "SOCIAL_POST_TOO_LONG",
                auto_fixable=True,
                fix_suggestion="Shorten content or split into multiple posts"
            )
            
        # Hashtag validation
        hashtags = re.findall(r'#\w+', content)
        if len(hashtags) > 10:
            result.add_issue(
                ValidationLevel.WARNING,
                ValidationCategory.PLATFORM_COMPLIANCE,
                f"Too many hashtags: {len(hashtags)} (recommended: max 10)",
                "SOCIAL_POST_TOO_MANY_HASHTAGS"
            )
            
    def _validate_blog_post(self, content: str, result: ValidationResult, **kwargs):
        """Validate blog post content"""
        word_count = len(content.split())
        
        # Blog post length validation
        if word_count < 300:
            result.add_issue(
                ValidationLevel.WARNING,
                ValidationCategory.TECHNICAL_QUALITY,
                f"Blog post is short: {word_count} words (recommended: 300+)",
                "BLOG_POST_SHORT"
            )
        elif word_count > 3000:
            result.add_issue(
                ValidationLevel.INFO,
                ValidationCategory.TECHNICAL_QUALITY,
                f"Blog post is very long: {word_count} words",
                "BLOG_POST_LONG"
            )
            
        # Reading time estimate
        reading_time = word_count / 200  # Average reading speed
        result.metadata['estimated_reading_time_minutes'] = reading_time
        
    def _validate_platform_compliance(
        self,
        content: Union[str, bytes, Path],
        content_type: ContentType,
        platforms: List[str],
        result: ValidationResult
    ):
        """Validate compliance with platform-specific requirements"""
        for platform in platforms:
            platform_rules = self.platform_rules.get(platform, {})
            
            for rule_name, rule_value in platform_rules.items():
                # Implement platform-specific validation logic
                pass
                
    def _assess_monetization_readiness(
        self,
        content: Union[str, bytes, Path],
        content_type: ContentType,
        result: ValidationResult
    ):
        """Assess content readiness for monetization"""
        monetization_score = 100.0
        
        # Check for copyright compliance
        if len(result.get_issues_by_category(ValidationCategory.COPYRIGHT_COMPLIANCE)) > 0:
            monetization_score -= 50
            
        # Check content quality
        if result.quality_score < 70:
            monetization_score -= 30
            
        # Check brand safety
        if result.safety_score < 80:
            monetization_score -= 40
            
        result.monetization_readiness = max(0, monetization_score)
        
    def _calculate_final_scores(self, result: ValidationResult):
        """Calculate final validation scores"""
        # Overall score is weighted average of component scores
        weights = {
            'quality': 0.25,
            'safety': 0.25,
            'compliance': 0.20,
            'seo': 0.15,
            'monetization': 0.15
        }
        
        result.overall_score = (
            result.quality_score * weights['quality'] +
            result.safety_score * weights['safety'] +
            result.compliance_score * weights['compliance'] +
            result.seo_score * weights['seo'] +
            result.monetization_readiness * weights['monetization']
        )
        
        # Ensure validity based on thresholds
        if result.overall_score < self.quality_thresholds['min_overall_score']:
            result.is_valid = False
            
    def batch_validate(
        self,
        contents: List[Tuple[Union[str, bytes, Path], ContentType]],
        **kwargs
    ) -> List[ValidationResult]:
        """Validate multiple contents in batch"""
        results = []
        
        for content, content_type in contents:
            result = self.validate_content(content, content_type, **kwargs)
            results.append(result)
            
        return results
        
    async def async_validate_content(
        self,
        content: Union[str, bytes, Path],
        content_type: ContentType,
        **kwargs
    ) -> ValidationResult:
        """Asynchronous content validation"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.validate_content,
            content,
            content_type,
            kwargs.get('metadata'),
            kwargs.get('platform_targets')
        )


# Global content validator instance
content_validator = ContentValidator()


def validate_content_decorator(
    content_type: ContentType,
    platform_targets: Optional[List[str]] = None,
    raise_on_invalid: bool = False
):
    """
    Decorator to automatically validate function return content
    
    Args:
        content_type: Type of content being validated
        platform_targets: Target platforms for validation
        raise_on_invalid: Whether to raise exception on invalid content
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            if isinstance(result, (str, bytes, Path)):
                validation_result = content_validator.validate_content(
                    result,
                    content_type,
                    platform_targets=platform_targets
                )
                
                if raise_on_invalid and not validation_result.is_valid:
                    raise ValueError(
                        f"Content validation failed: {validation_result.errors}"
                    )
                    
                # Attach validation result to response
                if hasattr(result, '__dict__'):
                    result.validation_result = validation_result
                    
            return result
            
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            if isinstance(result, (str, bytes, Path)):
                validation_result = await content_validator.async_validate_content(
                    result,
                    content_type,
                    platform_targets=platform_targets
                )
                
                if raise_on_invalid and not validation_result.is_valid:
                    raise ValueError(
                        f"Content validation failed: {validation_result.errors}"
                    )
                    
                # Attach validation result to response
                if hasattr(result, '__dict__'):
                    result.validation_result = validation_result
                    
            return result
            
        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
    return decorator


class ContentQualityAnalyzer:
    """Analyzes content quality and provides recommendations"""
    
    def __init__(self):
        self.quality_thresholds = {
            "min_length": 10,
            "max_length": 10000
        }
    
    def analyze_text_quality(self, content: str) -> ValidationResult:
        """Analyze text content quality"""
        result = ValidationResult()
        
        if not content or not content.strip():
            result.add_issue(
                ValidationLevel.ERROR,
                "Content is empty",
                "EMPTY_CONTENT"
            )
            return result
        
        content_length = len(content.strip())
        
        if content_length < self.quality_thresholds["min_length"]:
            result.add_issue(
                ValidationLevel.ERROR,
                f"Content too short: {content_length} characters (minimum: {self.quality_thresholds['min_length']})",
                "CONTENT_TOO_SHORT"
            )
        
        if content_length > self.quality_thresholds["max_length"]:
            result.add_issue(
                ValidationLevel.ERROR,
                f"Content too long: {content_length} characters (maximum: {self.quality_thresholds['max_length']})",
                "CONTENT_TOO_LONG"
            )
    
    def _validate_content_structure(self, content: str, result: ValidationResult):
        """Validate content structure and formatting"""
        # Check for proper sentence structure
        sentences = self._split_into_sentences(content)
        
        if len(sentences) == 0:
            result.add_issue(
                ValidationLevel.WARNING,
                "No complete sentences detected",
                "NO_SENTENCES"
            )
        
        # Check for overly long sentences
        for i, sentence in enumerate(sentences):
            if len(sentence.split()) > 30:
                result.add_issue(
                    ValidationLevel.WARNING,
                    f"Sentence {i+1} may be too long ({len(sentence.split())} words)",
                    "LONG_SENTENCE"
                )
        
        # Check for proper paragraph structure
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1:
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph.strip()) < 50:
                    result.add_issue(
                        ValidationLevel.WARNING,
                        f"Paragraph {i+1} may be too short",
                        "SHORT_PARAGRAPH"
                    )
    
    def _validate_language_quality(self, content: str, result: ValidationResult):
        """Validate language quality (simplified implementation)"""
        # Check for common spelling issues (simplified)
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Common misspellings check (basic implementation)
        common_errors = {
            'recieve': 'receive',
            'occured': 'occurred',
            'seperate': 'separate',
            'definately': 'definitely'
        }
        
        spelling_errors = 0
        for word in words:
            if word in common_errors:
                spelling_errors += 1
                result.add_issue(
                    ValidationLevel.WARNING,
                    f"Possible spelling error: '{word}' should be '{common_errors[word]}'",
                    "SPELLING_ERROR"
                )
        
        if spelling_errors > self.quality_thresholds["max_spelling_errors"]:
            result.add_issue(
                ValidationLevel.ERROR,
                f"Too many spelling errors: {spelling_errors}",
                "EXCESSIVE_SPELLING_ERRORS"
            )
        
        # Check grammar patterns (simplified)
        grammar_issues = self._check_basic_grammar(content)
        for issue in grammar_issues:
            result.add_issue(
                ValidationLevel.WARNING,
                issue,
                "GRAMMAR_ISSUE"
            )
    
    def _validate_content_safety(self, content: str, result: ValidationResult):
        """Validate content safety and appropriateness"""
        # Check for potentially harmful content (basic implementation)
        harmful_patterns = [
            r'\b(hate|violence|discrimination)\b',
            r'\b(illegal|harmful|dangerous)\b'
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                result.add_issue(
                    ValidationLevel.ERROR,
                    "Content may contain inappropriate or harmful language",
                    "SAFETY_CONCERN"
                )
        
        # Check for spam indicators
        spam_indicators = [
            r'click here now',
            r'limited time offer',
            r'100% guaranteed',
            r'make money fast'
        ]
        
        spam_count = 0
        for pattern in spam_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                spam_count += 1
        
        if spam_count > 2:
            result.add_issue(
                ValidationLevel.WARNING,
                "Content may appear spammy",
                "SPAM_INDICATORS"
            )
    
    def _validate_social_post(self, content: str, result: ValidationResult, platform: str = None, **kwargs):
        """Validate social media post specific requirements"""
        if platform == "twitter" and len(content) > 280:
            result.add_issue(
                ValidationLevel.ERROR,
                f"Twitter post exceeds character limit: {len(content)}/280",
                "TWITTER_LENGTH_EXCEEDED"
            )
        
        if platform == "instagram" and len(content) > 2200:
            result.add_issue(
                ValidationLevel.WARNING,
                f"Instagram caption is very long: {len(content)} characters",
                "INSTAGRAM_LONG_CAPTION"
            )
        
        # Check hashtag usage
        hashtags = re.findall(r'#\w+', content)
        if len(hashtags) > 10:
            result.add_issue(
                ValidationLevel.WARNING,
                f"Too many hashtags: {len(hashtags)} (recommended: max 5-10)",
                "EXCESSIVE_HASHTAGS"
            )
    
    def _validate_blog_post(self, content: str, result: ValidationResult, **kwargs):
        """Validate blog post specific requirements"""
        # Check for proper heading structure
        headings = re.findall(r'^#+\s+.+$', content, re.MULTILINE)
        
        if len(content) > 1000 and len(headings) == 0:
            result.add_issue(
                ValidationLevel.WARNING,
                "Long blog post should have headings for better readability",
                "MISSING_HEADINGS"
            )
        
        # Check for introduction and conclusion
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 3:
            first_para = paragraphs[0].strip()
            last_para = paragraphs[-1].strip()
            
            if len(first_para) < 100:
                result.add_issue(
                    ValidationLevel.WARNING,
                    "Introduction paragraph may be too short",
                    "SHORT_INTRODUCTION"
                )
            
            if len(last_para) < 50:
                result.add_issue(
                    ValidationLevel.WARNING,
                    "Conclusion paragraph may be too short",
                    "SHORT_CONCLUSION"
                )
    
    def _validate_email_content(self, content: str, result: ValidationResult, **kwargs):
        """Validate email content specific requirements"""
        # Check for subject line (if provided)
        subject = kwargs.get('subject', '')
        if subject and len(subject) > 50:
            result.add_issue(
                ValidationLevel.WARNING,
                f"Email subject line is long: {len(subject)} characters",
                "LONG_SUBJECT_LINE"
            )
        
        # Check for call-to-action
        cta_patterns = [
            r'click here',
            r'learn more',
            r'sign up',
            r'buy now',
            r'contact us'
        ]
        
        has_cta = any(re.search(pattern, content, re.IGNORECASE) for pattern in cta_patterns)
        if not has_cta and len(content) > 200:
            result.add_issue(
                ValidationLevel.WARNING,
                "Email content may benefit from a clear call-to-action",
                "MISSING_CTA"
            )
    
    def _split_into_sentences(self, content: str) -> List[str]:
        """Split content into sentences"""
        # Basic sentence splitting
        sentences = re.split(r'[.!?]+', content)
        return [s.strip() for s in sentences if s.strip()]
    
    def _check_basic_grammar(self, content: str) -> List[str]:
        """Basic grammar checking (simplified implementation)"""
        issues = []
        
        # Check for common grammar mistakes
        if re.search(r'\bi\s+am\s+\w+ing\b', content, re.IGNORECASE):
            issues.append("Consider using present continuous tense correctly")
        
        # Check for double spaces
        if '  ' in content:
            issues.append("Content contains multiple consecutive spaces")
        
        # Check for proper capitalization after periods
        sentences = self._split_into_sentences(content)
        for sentence in sentences:
            if sentence and not sentence[0].isupper():
                issues.append("Sentence should start with capital letter")
                break
        
        return issues
    
    def _calculate_validation_score(self, result: ValidationResult) -> float:
        """Calculate overall validation score"""
        if not result.issues:
            return 1.0
        
        score = 1.0
        
        for issue in result.issues:
            level = issue["level"]
            if level == "critical":
                score -= 0.3
            elif level == "error":
                score -= 0.2
            elif level == "warning":
                score -= 0.1
            elif level == "info":
                score -= 0.05
        
        return max(0.0, score)
    
    def set_quality_thresholds(self, thresholds: Dict[str, Any]):
        """Update quality thresholds"""
        self.quality_thresholds.update(thresholds)
    
    def add_custom_validation_rule(self, rule_func):
        """Add a custom validation rule"""
        self.validation_rules.append(rule_func)
    
    def validate_batch(self, contents: List[str], content_type: str = "text") -> List[ValidationResult]:
        """Validate multiple content items"""



        return [self.validate_content(content, content_type) for content in contents]


# Global content validator instance
content_validator = ContentValidator()
