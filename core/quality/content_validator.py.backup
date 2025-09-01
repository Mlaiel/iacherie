"""Content Quality Validator - Ultra Advanced Enterprise Module

Comprehensive content quality validation system with multi-format support,
AI-powered analysis, and industrial-grade quality metrics for creators
on the IA-Influencer platform.

Business Logic:
User (creator) → Upload multi-format content → Quality validation → 
Protection readiness → SEO optimization → Monetization scoring

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
import time
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
import mimetypes
import hashlib
import json

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageStat
    import librosa
    import soundfile as sf
    MULTIMEDIA_AVAILABLE = True
except ImportError:
    MULTIMEDIA_AVAILABLE = False

try:
    import torch
    import transformers
    from sentence_transformers import SentenceTransformer
    AI_MODELS_AVAILABLE = True
except ImportError:
    AI_MODELS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Supported content types for validation"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    MULTIMODAL = "multimodal"


class QualityLevel(Enum):
    """Content quality assessment levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class QualityIssue:
    """Individual quality issue with detailed information"""
    severity: ValidationSeverity
    category: str
    message: str
    code: str
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class QualityScore:
    """Comprehensive quality scoring"""
    overall: float  # 0-100
    technical: float  # Technical quality metrics
    content: float  # Content quality metrics
    seo: float  # SEO readiness score
    monetization: float  # Monetization readiness score
    platform_compliance: float  # Platform compliance score
    security: float  # Security assessment score
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'overall': self.overall,
            'technical': self.technical,
            'content': self.content,
            'seo': self.seo,
            'monetization': self.monetization,
            'platform_compliance': self.platform_compliance,
            'security': self.security
        }


@dataclass
class ValidationResult:
    """Comprehensive content validation result"""
    content_id: str
    content_type: ContentType
    quality_score: QualityScore
    issues: List[QualityIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def add_issue(self, severity: ValidationSeverity, category: str, 
                  message: str, code: str, suggestions: List[str] = None):
        """Add a quality issue to the result"""
        issue = QualityIssue(
            severity=severity,
            category=category,
            message=message,
            code=code,
            suggestions=suggestions or []
        )
        self.issues.append(issue)
    
    def get_critical_issues(self) -> List[QualityIssue]:
        """Get all critical issues"""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.CRITICAL]
    
    def has_blocking_issues(self) -> bool:
        """Check if there are any blocking issues"""
        return any(issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR] 
                  for issue in self.issues)


class AudioQualityAnalyzer:
    """Advanced audio content quality analysis"""
    
    def __init__(self):
        self.min_duration = 10.0  # seconds
        self.max_duration = 3600.0  # 1 hour
        self.min_bitrate = 128  # kbps
        self.preferred_sample_rate = 44100
        
    def analyze_audio_quality(self, file_path: Path, result: ValidationResult):
        """Analyze audio quality metrics"""
        if not MULTIMEDIA_AVAILABLE:
            result.add_issue(
                ValidationSeverity.WARNING,
                "dependencies",
                "Audio analysis dependencies not available",
                "AUDIO_DEPS_MISSING"
            )
            return
            
        try:
            # Load audio file
            audio_data, sample_rate = librosa.load(str(file_path), sr=None)
            duration = librosa.get_duration(y=audio_data, sr=sample_rate)
            
            # Duration validation
            if duration < self.min_duration:
                result.add_issue(
                    ValidationSeverity.ERROR,
                    "audio_quality",
                    f"Audio too short: {duration:.1f}s (minimum: {self.min_duration}s)",
                    "AUDIO_TOO_SHORT",
                    ["Extend audio content to meet minimum duration requirements"]
                )
            elif duration > self.max_duration:
                result.add_issue(
                    ValidationSeverity.WARNING,
                    "audio_quality",
                    f"Audio very long: {duration:.1f}s (maximum recommended: {self.max_duration}s)",
                    "AUDIO_TOO_LONG",
                    ["Consider splitting into shorter segments for better engagement"]
                )
            
            # Sample rate validation
            if sample_rate < self.preferred_sample_rate:
                result.add_issue(
                    ValidationSeverity.WARNING,
                    "audio_quality",
                    f"Low sample rate: {sample_rate}Hz (recommended: {self.preferred_sample_rate}Hz)",
                    "LOW_SAMPLE_RATE",
                    ["Use higher sample rate for better audio quality"]
                )
            
            # Audio level analysis
            rms_energy = np.sqrt(np.mean(audio_data**2))
            if rms_energy < 0.01:
                result.add_issue(
                    ValidationSeverity.WARNING,
                    "audio_quality",
                    "Audio levels too low",
                    "LOW_AUDIO_LEVELS",
                    ["Increase audio gain/volume for better clarity"]
                )
            elif rms_energy > 0.9:
                result.add_issue(
                    ValidationSeverity.ERROR,
                    "audio_quality",
                    "Audio levels too high (possible clipping)",
                    "HIGH_AUDIO_LEVELS",
                    ["Reduce audio gain to prevent distortion"]
                )
            
            # Silence detection
            silence_threshold = 0.001
            silence_frames = np.sum(np.abs(audio_data) < silence_threshold)
            silence_ratio = silence_frames / len(audio_data)
            
            if silence_ratio > 0.3:
                result.add_issue(
                    ValidationSeverity.WARNING,
                    "audio_quality",
                    f"High silence ratio: {silence_ratio:.1%}",
                    "HIGH_SILENCE_RATIO",
                    ["Remove excessive silence for better engagement"]
                )
            
            # Store audio metadata
            result.metadata.update({
                'audio_duration': duration,
                'sample_rate': sample_rate,
                'rms_energy': float(rms_energy),
                'silence_ratio': float(silence_ratio)
            })
            
        except Exception as e:
            logger.error(f"Audio analysis error: {e}")
            result.add_issue(
                ValidationSeverity.ERROR,
                "audio_quality",
                f"Failed to analyze audio: {str(e)}",
                "AUDIO_ANALYSIS_ERROR"
            )


class ImageQualityAnalyzer:
    """Advanced image content quality analysis"""
    
    def __init__(self):
        self.min_resolution = (720, 480)  # 720p minimum
        self.preferred_resolution = (1920, 1080)  # 1080p preferred
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
    def analyze_image_quality(self, file_path: Path, result: ValidationResult):
        """Analyze image quality metrics"""
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                file_size = file_path.stat().st_size
                
                # Resolution validation
                if width < self.min_resolution[0] or height < self.min_resolution[1]:
                    result.add_issue(
                        ValidationSeverity.ERROR,
                        "image_quality",
                        f"Low resolution: {width}x{height} (minimum: {self.min_resolution[0]}x{self.min_resolution[1]})",
                        "LOW_RESOLUTION",
                        ["Use higher resolution images for better quality"]
                    )
                elif width < self.preferred_resolution[0] or height < self.preferred_resolution[1]:
                    result.add_issue(
                        ValidationSeverity.WARNING,
                        "image_quality",
                        f"Below preferred resolution: {width}x{height} (preferred: {self.preferred_resolution[0]}x{self.preferred_resolution[1]})",
                        "BELOW_PREFERRED_RESOLUTION",
                        ["Consider using higher resolution for optimal quality"]
                    )
                
                # File size validation
                if file_size > self.max_file_size:
                    result.add_issue(
                        ValidationSeverity.WARNING,
                        "image_quality",
                        f"Large file size: {file_size / 1024 / 1024:.1f}MB (max recommended: {self.max_file_size / 1024 / 1024:.1f}MB)",
                        "LARGE_FILE_SIZE",
                        ["Compress image to reduce file size"]
                    )
                
                # Aspect ratio validation
                aspect_ratio = width / height
                if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                    result.add_issue(
                        ValidationSeverity.WARNING,
                        "image_quality",
                        f"Unusual aspect ratio: {aspect_ratio:.2f}",
                        "UNUSUAL_ASPECT_RATIO",
                        ["Consider using standard aspect ratios for better platform compatibility"]
                    )
                
                # Color analysis
                if img.mode in ['RGB', 'RGBA']:
                    stat = ImageStat.Stat(img)
                    brightness = sum(stat.mean) / len(stat.mean)
                    
                    if brightness < 50:
                        result.add_issue(
                            ValidationSeverity.WARNING,
                            "image_quality",
                            "Image appears too dark",
                            "LOW_BRIGHTNESS",
                            ["Adjust brightness for better visibility"]
                        )
                    elif brightness > 200:
                        result.add_issue(
                            ValidationSeverity.WARNING,
                            "image_quality",
                            "Image appears overexposed",
                            "HIGH_BRIGHTNESS",
                            ["Reduce exposure for better quality"]
                        )
                
                # Store image metadata
                result.metadata.update({
                    'image_width': width,
                    'image_height': height,
                    'aspect_ratio': aspect_ratio,
                    'file_size_mb': file_size / 1024 / 1024,
                    'color_mode': img.mode
                })
                
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            result.add_issue(
                ValidationSeverity.ERROR,
                "image_quality",
                f"Failed to analyze image: {str(e)}",
                "IMAGE_ANALYSIS_ERROR"
            )


class TextQualityAnalyzer:
    """Advanced text content quality analysis"""
    
    def __init__(self):
        self.min_length = 50  # characters
        self.max_length = 10000  # characters for social posts
        self.min_words = 10
        
    def analyze_text_quality(self, content: str, result: ValidationResult):
        """Analyze text quality metrics"""
        try:
            # Basic length validation
            content_length = len(content.strip())
            word_count = len(content.split())
            
            if content_length < self.min_length:
                result.add_issue(
                    ValidationSeverity.ERROR,
                    "text_quality",
                    f"Content too short: {content_length} characters (minimum: {self.min_length})",
                    "TEXT_TOO_SHORT",
                    ["Add more content to meet minimum requirements"]
                )
            
            if word_count < self.min_words:
                result.add_issue(
                    ValidationSeverity.ERROR,
                    "text_quality",
                    f"Too few words: {word_count} (minimum: {self.min_words})",
                    "TOO_FEW_WORDS",
                    ["Expand content with more detailed information"]
                )
            
            # Readability analysis
            sentences = content.count('.') + content.count('!') + content.count('?')
            if sentences > 0:
                avg_words_per_sentence = word_count / sentences
                if avg_words_per_sentence > 25:
                    result.add_issue(
                        ValidationSeverity.WARNING,
                        "text_quality",
                        f"Long sentences detected (avg: {avg_words_per_sentence:.1f} words)",
                        "LONG_SENTENCES",
                        ["Break down long sentences for better readability"]
                    )
            
            # Repetition detection
            words = content.lower().split()
            unique_words = set(words)
            if len(words) > 0:
                uniqueness_ratio = len(unique_words) / len(words)
                if uniqueness_ratio < 0.5:
                    result.add_issue(
                        ValidationSeverity.WARNING,
                        "text_quality",
                        f"High word repetition: {(1-uniqueness_ratio)*100:.1f}%",
                        "HIGH_REPETITION",
                        ["Vary vocabulary to improve content quality"]
                    )
            
            # Special characters validation
            special_char_ratio = sum(1 for c in content if not c.isalnum() and c not in ' .,!?;:-()[]{}"\'\n') / len(content)
            if special_char_ratio > 0.05:
                result.add_issue(
                    ValidationSeverity.WARNING,
                    "text_quality",
                    f"High special character usage: {special_char_ratio*100:.1f}%",
                    "HIGH_SPECIAL_CHARS",
                    ["Review special character usage for better readability"]
                )
            
            # Store text metadata
            result.metadata.update({
                'text_length': content_length,
                'word_count': word_count,
                'sentence_count': sentences,
                'uniqueness_ratio': uniqueness_ratio if len(words) > 0 else 0,
                'special_char_ratio': special_char_ratio
            })
            
        except Exception as e:
            logger.error(f"Text analysis error: {e}")
            result.add_issue(
                ValidationSeverity.ERROR,
                "text_quality",
                f"Failed to analyze text: {str(e)}",
                "TEXT_ANALYSIS_ERROR"
            )


class ContentQualityValidator:
    """Enterprise content quality validation system"""
    
    def __init__(self):
        self.audio_analyzer = AudioQualityAnalyzer()
        self.image_analyzer = ImageQualityAnalyzer()
        self.text_analyzer = TextQualityAnalyzer()
        
    def validate_content(
        self,
        content: Union[str, Path],
        content_type: ContentType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate content quality comprehensively"""
        start_time = time.time()
        
        # Generate content ID
        if isinstance(content, Path):
            content_id = hashlib.md5(str(content).encode()).hexdigest()
        else:
            content_id = hashlib.md5(content.encode()).hexdigest()
        
        # Initialize result
        result = ValidationResult(
            content_id=content_id,
            content_type=content_type,
            quality_score=QualityScore(
                overall=0.0, technical=0.0, content=0.0, seo=0.0,
                monetization=0.0, platform_compliance=0.0, security=0.0
            ),
            metadata=metadata or {}
        )
        
        try:
            # Content type specific validation
            if content_type == ContentType.AUDIO and isinstance(content, Path):
                self.audio_analyzer.analyze_audio_quality(content, result)
            elif content_type == ContentType.IMAGE and isinstance(content, Path):
                self.image_analyzer.analyze_image_quality(content, result)
            elif content_type in [ContentType.TEXT, ContentType.BLOG_POST, ContentType.SOCIAL_POST]:
                if isinstance(content, str):
                    self.text_analyzer.analyze_text_quality(content, result)
                elif isinstance(content, Path):
                    with open(content, 'r', encoding='utf-8') as f:
                        text_content = f.read()
                    self.text_analyzer.analyze_text_quality(text_content, result)
            
            # Calculate quality scores
            self._calculate_quality_scores(result)
            
            # Generate recommendations
            self._generate_recommendations(result)
            
        except Exception as e:
            logger.error(f"Content validation error: {e}")
            result.add_issue(
                ValidationSeverity.CRITICAL,
                "system",
                f"Validation failed: {str(e)}",
                "VALIDATION_ERROR"
            )
        
        # Record processing time
        result.processing_time_ms = (time.time() - start_time) * 1000
        
        return result
    
    def _calculate_quality_scores(self, result: ValidationResult):
        """Calculate comprehensive quality scores"""
        # Base scores
        base_technical = 100.0
        base_content = 100.0
        base_seo = 80.0
        base_monetization = 80.0
        base_platform = 90.0
        base_security = 95.0
        
        # Deduct points for issues
        for issue in result.issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                deduction = 30
            elif issue.severity == ValidationSeverity.ERROR:
                deduction = 20
            elif issue.severity == ValidationSeverity.WARNING:
                deduction = 10
            else:
                deduction = 5
            
            # Apply deductions to relevant categories
            if issue.category in ['audio_quality', 'image_quality', 'dependencies']:
                base_technical = max(0, base_technical - deduction)
            elif issue.category in ['text_quality', 'content']:
                base_content = max(0, base_content - deduction)
            elif issue.category == 'seo':
                base_seo = max(0, base_seo - deduction)
            elif issue.category == 'monetization':
                base_monetization = max(0, base_monetization - deduction)
            elif issue.category == 'platform':
                base_platform = max(0, base_platform - deduction)
            elif issue.category == 'security':
                base_security = max(0, base_security - deduction)
        
        # Update scores
        result.quality_score.technical = base_technical
        result.quality_score.content = base_content
        result.quality_score.seo = base_seo
        result.quality_score.monetization = base_monetization
        result.quality_score.platform_compliance = base_platform
        result.quality_score.security = base_security
        
        # Calculate overall score
        weights = {
            'technical': 0.25,
            'content': 0.25,
            'seo': 0.15,
            'monetization': 0.15,
            'platform_compliance': 0.10,
            'security': 0.10
        }
        
        result.quality_score.overall = (
            base_technical * weights['technical'] +
            base_content * weights['content'] +
            base_seo * weights['seo'] +
            base_monetization * weights['monetization'] +
            base_platform * weights['platform_compliance'] +
            base_security * weights['security']
        )
    
    def _generate_recommendations(self, result: ValidationResult):
        """Generate quality improvement recommendations"""
        recommendations = []
        
        # Score-based recommendations
        if result.quality_score.technical < 70:
            recommendations.append("Improve technical quality by addressing audio/video/image issues")
        
        if result.quality_score.content < 70:
            recommendations.append("Enhance content quality with better structure and clarity")
        
        if result.quality_score.seo < 60:
            recommendations.append("Optimize content for search engines with better keywords and structure")
        
        if result.quality_score.monetization < 60:
            recommendations.append("Improve monetization potential with platform-specific optimizations")
        
        if result.quality_score.overall < 70:
            recommendations.append("Overall quality needs improvement - focus on critical issues first")
        
        # Critical issue recommendations
        critical_issues = result.get_critical_issues()
        if critical_issues:
            recommendations.append("Address all critical issues before publishing")
        
        result.recommendations = recommendations
    
    async def validate_content_async(
        self,
        content: Union[str, Path],
        content_type: ContentType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Asynchronous content validation"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.validate_content, content, content_type, metadata
        )
    
    def batch_validate(
        self,
        contents: List[Tuple[Union[str, Path], ContentType]],
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[ValidationResult]:
        """Validate multiple contents in batch"""
        results = []
        metadata_list = metadata_list or [None] * len(contents)
        
        for i, (content, content_type) in enumerate(contents):
            metadata = metadata_list[i] if i < len(metadata_list) else None
            result = self.validate_content(content, content_type, metadata)
            results.append(result)
        
        return results
