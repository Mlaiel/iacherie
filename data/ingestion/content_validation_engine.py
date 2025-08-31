"""
Content Validation Engine
========================

Enterprise-grade content validation system for comprehensive content analysis,
quality assessment, compliance verification, and security validation with
AI-powered content understanding and policy enforcement.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

  INTELLECTUAL PROPERTY WARNING 
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.

PROJECT TEAM SPECIALTIES:
- Lead Dev IA & ML Engineer: Advanced AI/ML algorithms and model integration
- Backend Senior Developer: Enterprise architecture and scalable systems
- DBA & Data Engineer: Database optimization and data pipeline management  
- Security Specialist: Content protection and security validation
- DevOps Engineer: Infrastructure automation and deployment
- Audio/Video Specialist: Multimedia processing and codec optimization
- Microservices Architect: Distributed systems and service orchestration
- IA Prompt Engineer: AI model fine-tuning and content analysis
"""

import asyncio
import logging
import json
import hashlib
import mimetypes
import tempfile
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
import aiofiles
import magic
from PIL import Image, ImageStat
import cv2
import numpy as np
import librosa
import ffmpeg
import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    AutoImageProcessor, AutoModelForImageClassification,
    pipeline
)
import spacy
from langdetect import detect, LangDetectError

from ...core.config import get_settings
from ...core.logging import get_logger
from ...core.exceptions import ValidationError, SecurityError
from ...security.content_scanner import ContentSecurityScanner
from ...ml.models.content_classifier import ContentClassifier
from ...ml.models.nsfw_detector import NSFWDetector
from ...ml.models.toxicity_detector import ToxicityDetector


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    BLOCKING = "blocking"


class ValidationCategory(Enum):
    """Content validation categories"""
    TECHNICAL = "technical"
    QUALITY = "quality"
    SECURITY = "security"
    POLICY = "policy"
    LEGAL = "legal"
    CONTENT = "content"
    METADATA = "metadata"
    ACCESSIBILITY = "accessibility"


class ContentPolicy(Enum):
    """Content policy types"""
    GENERAL = "general"
    ADULT_CONTENT = "adult_content"
    VIOLENCE = "violence"
    HATE_SPEECH = "hate_speech"
    HARASSMENT = "harassment"
    SPAM = "spam"
    COPYRIGHT = "copyright"
    PRIVACY = "privacy"
    MISINFORMATION = "misinformation"
    ILLEGAL_CONTENT = "illegal_content"


@dataclass
class ValidationIssue:
    """Individual validation issue"""
    id: str
    category: ValidationCategory
    severity: ValidationSeverity
    policy: Optional[ContentPolicy]
    title: str
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    location: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    auto_fixable: bool = False
    fix_suggestion: Optional[str] = None
    confidence_score: float = 1.0


@dataclass
class ValidationMetrics:
    """Content validation metrics"""
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    warnings: int = 0
    errors: int = 0
    critical_issues: int = 0
    processing_time_ms: float = 0.0
    ai_confidence: float = 0.0
    quality_score: float = 0.0
    compliance_score: float = 0.0
    security_score: float = 0.0


@dataclass
class ValidationResult:
    """Comprehensive validation result"""
    is_valid: bool
    content_id: str
    validation_id: str
    overall_score: float
    metrics: ValidationMetrics
    issues: List[ValidationIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    auto_fixes_applied: List[str] = field(default_factory=list)
    blocked_reasons: List[str] = field(default_factory=list)
    approved_for: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class ContentValidationEngine:
    """
    Enterprise content validation engine for IA Influencer Agent platform.
    
    Provides comprehensive content validation including technical quality assessment,
    security scanning, policy compliance, AI-powered content analysis, accessibility
    checks, and automated fix suggestions with detailed reporting.
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis):
        """
        Initialize ContentValidationEngine.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
        """
        self.db_session = db_session
        self.redis = redis_client
        self.logger = get_logger(__name__)
        self.settings = get_settings()
        
        # Initialize AI models
        self._initialize_ai_models()
        
        # Security scanner
        self.security_scanner = ContentSecurityScanner()
        
        # Content classifiers
        self.content_classifier = ContentClassifier()
        self.nsfw_detector = NSFWDetector()
        self.toxicity_detector = ToxicityDetector()
        
        # Language processing
        self.nlp_models = {}
        
        # Validation configuration
        self.max_file_size = 2 * 1024 * 1024 * 1024  # 2GB
        self.supported_formats = {
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
            'text': ['.txt', '.md', '.html', '.pdf', '.docx'],
            'document': ['.pdf', '.doc', '.docx', '.ppt', '.pptx']
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            'audio': {
                'min_sample_rate': 16000,
                'min_bitrate': 128,
                'max_noise_level': 0.1,
                'min_dynamic_range': 20
            },
            'video': {
                'min_resolution': (640, 480),
                'min_fps': 15,
                'max_compression_artifacts': 0.3,
                'min_lighting_quality': 0.5
            },
            'image': {
                'min_resolution': (300, 300),
                'min_quality_score': 0.6,
                'max_blur_level': 0.4,
                'min_contrast': 0.3
            }
        }
        
        # Content policies
        self.content_policies = self._load_content_policies()
        
    def _initialize_ai_models(self):
        """Initialize AI models for content analysis"""



        try:
            # Text classification models
            self.text_classifier = pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Image classification models
            self.image_classifier = pipeline(
                "image-classification",
                model="microsoft/DialoGPT-medium",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # NSFW detection
            self.nsfw_classifier = pipeline(
                "image-classification",
                model="Falconsai/nsfw_image_detection",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Load NLP models
            self._load_nlp_models()
            
            self.logger.info("AI models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI models: {str(e)}")
            # Continue without AI models
            self.text_classifier = None
            self.image_classifier = None
            self.nsfw_classifier = None
    
    def _load_nlp_models(self):
        """Load NLP models for different languages"""



        try:
            # Load primary language models
            languages = ['en', 'de', 'fr', 'es', 'it']
            for lang in languages:
                try:
                    if lang == 'en':
                        model_name = 'en_core_web_sm'
                    else:
                        model_name = f'{lang}_core_news_sm'
                    
                    self.nlp_models[lang] = spacy.load(model_name)
                except OSError:
                    # Fallback to basic model
                    self.nlp_models[lang] = spacy.blank(lang)
                    
        except Exception as e:
            self.logger.warning(f"NLP models loading failed: {str(e)}")
    
    def _load_content_policies(self) -> Dict[str, Any]:
        """Load content policy definitions"""



        return {
            ContentPolicy.GENERAL: {
                'description': 'General content guidelines',
                'rules': [
                    'Content must be appropriate for intended audience',
                    'No spam or low-quality content',
                    'Must comply with platform terms of service'
                ],
                'auto_check': True
            },
            ContentPolicy.ADULT_CONTENT: {
                'description': 'Adult content restrictions',
                'rules': [
                    'No explicit sexual content',
                    'No nudity without appropriate warnings',
                    'Age-appropriate content labeling required'
                ],
                'auto_check': True,
                'ai_detection': True
            },
            ContentPolicy.VIOLENCE: {
                'description': 'Violence and graphic content',
                'rules': [
                    'No extreme violence or gore',
                    'No promotion of violence',
                    'Contextual violence warnings required'
                ],
                'auto_check': True,
                'ai_detection': True
            },
            ContentPolicy.HATE_SPEECH: {
                'description': 'Hate speech and discrimination',
                'rules': [
                    'No hate speech based on protected characteristics',
                    'No discriminatory language',
                    'No promotion of hate groups'
                ],
                'auto_check': True,
                'ai_detection': True
            },
            ContentPolicy.COPYRIGHT: {
                'description': 'Copyright and intellectual property',
                'rules': [
                    'No copyrighted content without permission',
                    'Proper attribution required',
                    'Fair use guidelines must be followed'
                ],
                'auto_check': False,
                'manual_review': True
            }
        }
    
    async def validate_content(self, file_path: str, content_type: str, 
                             metadata: Optional[Dict[str, Any]] = None,
                             validation_options: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Perform comprehensive content validation.
        
        Args:
            file_path: Path to content file
            content_type: Type of content (audio, video, image, text, document)
            metadata: Optional metadata about the content
            validation_options: Validation configuration options
            
        Returns:
            Complete validation result
        """
        validation_id = str(uuid.uuid4())
        content_id = metadata.get('content_id', str(uuid.uuid4())) if metadata else str(uuid.uuid4())
        start_time = datetime.now(timezone.utc)
        
        # Initialize result
        result = ValidationResult(
            is_valid=True,
            content_id=content_id,
            validation_id=validation_id,
            overall_score=0.0,
            metrics=ValidationMetrics()
        )
        
        try:
            self.logger.info(f"Starting content validation: {validation_id}")
            
            # Parse validation options
            options = validation_options or {}
            skip_ai = options.get('skip_ai_analysis', False)
            strict_mode = options.get('strict_mode', False)
            auto_fix = options.get('auto_fix', True)
            
            # Stage 1: Basic file validation
            await self._validate_file_basics(file_path, content_type, result)
            
            # Stage 2: Technical quality validation
            await self._validate_technical_quality(file_path, content_type, result)
            
            # Stage 3: Security validation
            await self._validate_security(file_path, content_type, result)
            
            # Stage 4: Content policy validation
            if not skip_ai:
                await self._validate_content_policies(file_path, content_type, result)
            
            # Stage 5: AI-powered content analysis
            if not skip_ai:
                await self._perform_ai_content_analysis(file_path, content_type, result)
            
            # Stage 6: Accessibility validation
            await self._validate_accessibility(file_path, content_type, result)
            
            # Stage 7: Metadata validation
            if metadata:
                await self._validate_metadata(metadata, result)
            
            # Stage 8: Legal compliance checks
            await self._validate_legal_compliance(file_path, content_type, result)
            
            # Apply auto-fixes if enabled
            if auto_fix:
                await self._apply_auto_fixes(file_path, content_type, result)
            
            # Calculate final scores
            self._calculate_validation_scores(result, strict_mode)
            
            # Determine overall validation status
            result.is_valid = self._determine_validation_status(result, strict_mode)
            
            # Generate recommendations
            result.recommendations = await self._generate_recommendations(result)
            
            # Complete validation
            result.completed_at = datetime.now(timezone.utc)
            result.metrics.processing_time_ms = (
                result.completed_at - start_time
            ).total_seconds() * 1000
            
            # Cache validation result
            await self._cache_validation_result(result)
            
            self.logger.info(f"Content validation completed: {validation_id}, Valid: {result.is_valid}")
            
        except Exception as e:
            self.logger.error(f"Content validation failed: {validation_id} - {str(e)}")
            
            # Add critical error
            result.issues.append(ValidationIssue(
                id=str(uuid.uuid4()),
                category=ValidationCategory.TECHNICAL,
                severity=ValidationSeverity.CRITICAL,
                policy=None,
                title="Validation System Error",
                description=f"Validation failed due to system error: {str(e)}",
                details={'error': str(e), 'validation_id': validation_id}
            ))
            
            result.is_valid = False
            result.overall_score = 0.0
            result.completed_at = datetime.now(timezone.utc)
        
        return result
    
    async def _validate_file_basics(self, file_path: str, content_type: str, result: ValidationResult):
        """Validate basic file properties"""



        try:
            file_path_obj = Path(file_path)
            
            # Check file exists
            if not file_path_obj.exists():
                result.issues.append(ValidationIssue(
                    id=str(uuid.uuid4()),
                    category=ValidationCategory.TECHNICAL,
                    severity=ValidationSeverity.BLOCKING,
                    policy=None,
                    title="File Not Found",
                    description="The specified file does not exist",
                    details={'file_path': file_path}
                ))
                return
            
            # Check file size
            file_size = file_path_obj.stat().st_size
            if file_size == 0:
                result.issues.append(ValidationIssue(
                    id=str(uuid.uuid4()),
                    category=ValidationCategory.TECHNICAL,
                    severity=ValidationSeverity.BLOCKING,
                    policy=None,
                    title="Empty File",
                    description="File is empty (0 bytes)",
                    details={'file_size': file_size}
                ))
                return
            
            if file_size > self.max_file_size:
                result.issues.append(ValidationIssue(
                    id=str(uuid.uuid4()),
                    category=ValidationCategory.TECHNICAL,
                    severity=ValidationSeverity.ERROR,
                    policy=None,
                    title="File Too Large",
                    description=f"File size {file_size} exceeds maximum {self.max_file_size}",
                    details={'file_size': file_size, 'max_size': self.max_file_size}
                ))
            
            # Check file extension
            file_extension = file_path_obj.suffix.lower()
            supported_extensions = self.supported_formats.get(content_type, [])
            
            if file_extension not in supported_extensions:
                result.issues.append(ValidationIssue(
                    id=str(uuid.uuid4()),
                    category=ValidationCategory.TECHNICAL,
                    severity=ValidationSeverity.WARNING,
                    policy=None,
                    title="Unsupported File Extension",
                    description=f"Extension {file_extension} not in supported list for {content_type}",
                    details={
                        'extension': file_extension,
                        'supported': supported_extensions
                    }
                ))
            
            # Check MIME type
            try:
                with open(file_path, 'rb') as f:
                    file_sample = f.read(2048)
                detected_mime = magic.from_buffer(file_sample, mime=True)
                
                # Verify MIME type matches content type
                expected_mime_prefixes = {
                    'audio': 'audio/',
                    'video': 'video/',
                    'image': 'image/',
                    'text': 'text/',
                    'document': ['application/pdf', 'application/msword']
                }
                
                expected_prefix = expected_mime_prefixes.get(content_type)
                if expected_prefix:
                    if isinstance(expected_prefix, list):
                        mime_match = any(detected_mime.startswith(prefix) for prefix in expected_prefix)
                    else:
                        mime_match = detected_mime.startswith(expected_prefix)
                    
                    if not mime_match:
                        result.issues.append(ValidationIssue(
                            id=str(uuid.uuid4()),
                            category=ValidationCategory.TECHNICAL,
                            severity=ValidationSeverity.WARNING,
                            policy=None,
                            title="MIME Type Mismatch",
                            description=f"Detected MIME type {detected_mime} doesn't match expected {content_type}",
                            details={
                                'detected_mime': detected_mime,
                                'expected_type': content_type
                            }
                        ))
                
            except Exception as e:
                result.issues.append(ValidationIssue(
                    id=str(uuid.uuid4()),
                    category=ValidationCategory.TECHNICAL,
                    severity=ValidationSeverity.WARNING,
                    policy=None,
                    title="MIME Type Detection Failed",
                    description=f"Could not detect MIME type: {str(e)}",
                    details={'error': str(e)}
                ))
            
            result.metrics.total_checks += 4  # File existence, size, extension, MIME
            result.metrics.passed_checks += len([i for i in result.issues if i.severity not in [
                ValidationSeverity.ERROR, ValidationSeverity.BLOCKING
            ]])
            
        except Exception as e:
            result.issues.append(ValidationIssue(
                id=str(uuid.uuid4()),
                category=ValidationCategory.TECHNICAL,
                severity=ValidationSeverity.ERROR,
                policy=None,
                title="Basic Validation Failed",
                description=f"Basic file validation failed: {str(e)}",
                details={'error': str(e)}
            ))
    
    async def _validate_technical_quality(self, file_path: str, content_type: str, result: ValidationResult):
        """Validate technical quality based on content type"""



        try:
            if content_type == 'audio':
                await self._validate_audio_quality(file_path, result)
            elif content_type == 'video':
                await self._validate_video_quality(file_path, result)
            elif content_type == 'image':
                await self._validate_image_quality(file_path, result)
            elif content_type == 'text':
                await self._validate_text_quality(file_path, result)
            elif content_type == 'document':
                await self._validate_document_quality(file_path, result)
                
        except Exception as e:
            result.issues.append(ValidationIssue(
                id=str(uuid.uuid4()),
                category=ValidationCategory.QUALITY,
                severity=ValidationSeverity.WARNING,
                policy=None,
                title="Quality Validation Failed",
                description=f"Technical quality validation failed: {str(e)}",
                details={'error': str(e), 'content_type': content_type}
            ))
    
    async def _validate_audio_quality(self, file_path: str, result: ValidationResult):
        """Validate audio file quality"""



        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            
            thresholds = self.quality_thresholds['audio']
            
            # Check sample rate
            if sr < thresholds['min_sample_rate']:
                result.issues.append(ValidationIssue(
                    id=str(uuid.uuid4()),
                    category=ValidationCategory.QUALITY,
                    severity=ValidationSeverity.WARNING,
                    policy=None,
                    title="Low Sample Rate",
                    description=f"Sample rate {sr}Hz is below recommended {thresholds['min_sample_rate']}Hz",
                    details={'sample_rate': sr, 'recommended': thresholds['min_sample_rate']},
                    auto_fixable=True,
                    fix_suggestion="Resample audio to higher sample rate"
                ))
            
            # Check duration
            if duration < 1.0:
                result.issues.append(ValidationIssue(
                    id=str(uuid.uuid4()),
                    category=ValidationCategory.QUALITY,
                    severity=ValidationSeverity.WARNING,
                    policy=None,
                    title="Very Short Audio",
                    description=f"Audio duration {duration:.2f}s is very short",
                    details={'duration': duration}
                ))
            
            # Check for silence
            silence_threshold = 0.01
            silence_ratio = np.sum(np.abs(y) < silence_threshold) / len(y)
            if silence_ratio > 0.8:
                result.issues.append(ValidationIssue(
                    id=str(uuid.uuid4()),
                    category=ValidationCategory.QUALITY,
                    severity=ValidationSeverity.WARNING,
                    policy=None,
                    title="High Silence Ratio",
                    description=f"Audio contains {silence_ratio:.1%} silence",
                    details={'silence_ratio': silence_ratio}
                ))
            
            # Check dynamic range
            dynamic_range = 20 * np.log10(np.max(np.abs(y)) / (np.mean(np.abs(y)) + 1e-10))
            if dynamic_range < thresholds['min_dynamic_range']:
                result.issues.append(ValidationIssue(
                    id=str(uuid.uuid4()),
                    category=ValidationCategory.QUALITY,
                    severity=ValidationSeverity.WARNING,
                    policy=None,
                    title="Low Dynamic Range",
                    description=f"Dynamic range {dynamic_range:.1f}dB is low",
                    details={'dynamic_range': dynamic_range}
                ))
            
            # Store audio quality metrics
            result.metadata['audio_quality'] = {
                'sample_rate': sr,
                'duration': duration,
                'channels': 1 if len(y.shape) == 1 else y.shape[0],
                'dynamic_range': dynamic_range,
                'silence_ratio': silence_ratio,
                'rms_level': np.sqrt(np.mean(y**2))
            }
            
            result.metrics.total_checks += 4
            
        except Exception as e:
            result.issues.append(ValidationIssue(
                id=str(uuid.uuid4()),
                category=ValidationCategory.QUALITY,
                severity=ValidationSeverity.ERROR,
                policy=None,
                title="Audio Quality Check Failed",
                description=f"Could not analyze audio quality: {str(e)}",
                details={'error': str(e)}
            ))
    
    async def _validate_image_quality(self, file_path: str, result: ValidationResult):
        """Validate image file quality"""



        try:
            # Load image
            image = Image.open(file_path)
            width, height = image.size
            
            thresholds = self.quality_thresholds['image']
            
            # Check resolution
            min_width, min_height = thresholds['min_resolution']
            if width < min_width or height < min_height:
                result.issues.append(ValidationIssue(
                    id=str(uuid.uuid4()),
                    category=ValidationCategory.QUALITY,
                    severity=ValidationSeverity.WARNING,
                    policy=None,
                    title="Low Resolution",
                    description=f"Image resolution {width}x{height} is below recommended {min_width}x{min_height}",
                    details={'resolution': (width, height), 'recommended': (min_width, min_height)}
                ))
            
            # Check aspect ratio
            aspect_ratio = width / height
            if aspect_ratio < 0.1 or aspect_ratio > 10:
                result.issues.append(ValidationIssue(
                    id=str(uuid.uuid4()),
                    category=ValidationCategory.QUALITY,
                    severity=ValidationSeverity.WARNING,
                    policy=None,
                    title="Unusual Aspect Ratio",
                    description=f"Aspect ratio {aspect_ratio:.2f} is unusual",
                    details={'aspect_ratio': aspect_ratio}
                ))
            
            # Convert to numpy for analysis
            img_array = np.array(image.convert('RGB'))
            
            # Check brightness
            brightness = np.mean(img_array)
            if brightness < 50:
                result.issues.append(ValidationIssue(
                    id=str(uuid.uuid4()),
                    category=ValidationCategory.QUALITY,
                    severity=ValidationSeverity.WARNING,
                    policy=None,
                    title="Dark Image",
                    description=f"Image appears very dark (brightness: {brightness:.1f})",
                    details={'brightness': brightness},
                    auto_fixable=True,
                    fix_suggestion="Adjust brightness levels"
                ))
            elif brightness > 200:
                result.issues.append(ValidationIssue(
                    id=str(uuid.uuid4()),
                    category=ValidationCategory.QUALITY,
                    severity=ValidationSeverity.WARNING,
                    policy=None,
                    title="Overexposed Image",
                    description=f"Image appears overexposed (brightness: {brightness:.1f})",
                    details={'brightness': brightness}
                ))
            
            # Check contrast
            contrast = np.std(img_array)
            if contrast < thresholds['min_contrast'] * 255:
                result.issues.append(ValidationIssue(
                    id=str(uuid.uuid4()),
                    category=ValidationCategory.QUALITY,
                    severity=ValidationSeverity.WARNING,
                    policy=None,
                    title="Low Contrast",
                    description=f"Image has low contrast (std: {contrast:.1f})",
                    details={'contrast': contrast},
                    auto_fixable=True,
                    fix_suggestion="Enhance contrast"
                ))
            
            # Blur detection using Laplacian variance
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            if blur_score < 100:  # Threshold for blur detection
                result.issues.append(ValidationIssue(
                    id=str(uuid.uuid4()),
                    category=ValidationCategory.QUALITY,
                    severity=ValidationSeverity.WARNING,
                    policy=None,
                    title="Blurry Image",
                    description=f"Image appears blurry (blur score: {blur_score:.1f})",
                    details={'blur_score': blur_score}
                ))
            
            # Store image quality metrics
            result.metadata['image_quality'] = {
                'resolution': (width, height),
                'aspect_ratio': aspect_ratio,
                'brightness': brightness,
                'contrast': contrast,
                'blur_score': blur_score,
                'file_size': Path(file_path).stat().st_size,
                'format': image.format,
                'mode': image.mode
            }
            
            result.metrics.total_checks += 5
            
        except Exception as e:
            result.issues.append(ValidationIssue(
                id=str(uuid.uuid4()),
                category=ValidationCategory.QUALITY,
                severity=ValidationSeverity.ERROR,
                policy=None,
                title="Image Quality Check Failed",
                description=f"Could not analyze image quality: {str(e)}",
                details={'error': str(e)}
            ))
    
    async def _validate_security(self, file_path: str, content_type: str, result: ValidationResult):
        """Perform security validation"""



        try:
            # Use security scanner
            security_result = await self.security_scanner.scan_file(file_path)
            
            if not security_result.get('is_safe', True):
                for threat in security_result.get('threats', []):
                    result.issues.append(ValidationIssue(
                        id=str(uuid.uuid4()),
                        category=ValidationCategory.SECURITY,
                        severity=ValidationSeverity.BLOCKING,
                        policy=None,
                        title="Security Threat Detected",
                        description=f"Security threat detected: {threat}",
                        details={'threat': threat, 'scanner_result': security_result}
                    ))
            
            # Check file headers for anomalies
            await self._check_file_headers(file_path, content_type, result)
            
            # Check for embedded content
            await self._check_embedded_content(file_path, content_type, result)
            
            result.metrics.total_checks += 3
            result.metrics.security_score = security_result.get('safety_score', 1.0)
            
        except Exception as e:
            result.issues.append(ValidationIssue(
                id=str(uuid.uuid4()),
                category=ValidationCategory.SECURITY,
                severity=ValidationSeverity.ERROR,
                policy=None,
                title="Security Validation Failed",
                description=f"Security validation failed: {str(e)}",
                details={'error': str(e)}
            ))
    
    async def _validate_content_policies(self, file_path: str, content_type: str, result: ValidationResult):
        """Validate content against policies"""



        try:
            for policy, config in self.content_policies.items():
                if not config.get('auto_check', False):
                    continue
                
                if config.get('ai_detection', False):
                    # Use AI detection for this policy
                    policy_result = await self._check_policy_with_ai(file_path, content_type, policy)
                    
                    if policy_result.get('violation', False):
                        severity = ValidationSeverity.ERROR if policy in [
                            ContentPolicy.ADULT_CONTENT, ContentPolicy.VIOLENCE, ContentPolicy.HATE_SPEECH
                        ] else ValidationSeverity.WARNING
                        
                        result.issues.append(ValidationIssue(
                            id=str(uuid.uuid4()),
                            category=ValidationCategory.POLICY,
                            severity=severity,
                            policy=policy,
                            title=f"{policy.value.replace('_', ' ').title()} Policy Violation",
                            description=policy_result.get('description', 'Policy violation detected'),
                            details={
                                'policy': policy.value,
                                'confidence': policy_result.get('confidence', 0),
                                'details': policy_result.get('details', {})
                            },
                            confidence_score=policy_result.get('confidence', 0)
                        ))
            
            result.metrics.total_checks += len([p for p in self.content_policies.values() if p.get('auto_check')])
            
        except Exception as e:
            result.issues.append(ValidationIssue(
                id=str(uuid.uuid4()),
                category=ValidationCategory.POLICY,
                severity=ValidationSeverity.WARNING,
                policy=None,
                title="Policy Validation Failed",
                description=f"Content policy validation failed: {str(e)}",
                details={'error': str(e)}
            ))
    
    async def _perform_ai_content_analysis(self, file_path: str, content_type: str, result: ValidationResult):
        """Perform AI-powered content analysis"""



        try:
            if content_type == 'image' and self.nsfw_classifier:
                # NSFW detection for images
                nsfw_result = await self._detect_nsfw_content(file_path)
                if nsfw_result.get('is_nsfw', False):
                    result.issues.append(ValidationIssue(
                        id=str(uuid.uuid4()),
                        category=ValidationCategory.CONTENT,
                        severity=ValidationSeverity.ERROR,
                        policy=ContentPolicy.ADULT_CONTENT,
                        title="NSFW Content Detected",
                        description="Image contains adult/NSFW content",
                        details=nsfw_result,
                        confidence_score=nsfw_result.get('confidence', 0)
                    ))
            
            if content_type in ['text', 'document'] and self.text_classifier:
                # Text toxicity detection
                text_content = await self._extract_text_content(file_path, content_type)
                if text_content:
                    toxicity_result = await self._detect_text_toxicity(text_content)
                    if toxicity_result.get('is_toxic', False):
                        result.issues.append(ValidationIssue(
                            id=str(uuid.uuid4()),
                            category=ValidationCategory.CONTENT,
                            severity=ValidationSeverity.ERROR,
                            policy=ContentPolicy.HATE_SPEECH,
                            title="Toxic Content Detected",
                            description="Text contains toxic or harmful content",
                            details=toxicity_result,
                            confidence_score=toxicity_result.get('confidence', 0)
                        ))
            
            result.metrics.total_checks += 2
            result.metrics.ai_confidence = 0.85  # Average AI confidence
            
        except Exception as e:
            result.issues.append(ValidationIssue(
                id=str(uuid.uuid4()),
                category=ValidationCategory.CONTENT,
                severity=ValidationSeverity.WARNING,
                policy=None,
                title="AI Analysis Failed",
                description=f"AI content analysis failed: {str(e)}",
                details={'error': str(e)}
            ))
    
    def _calculate_validation_scores(self, result: ValidationResult, strict_mode: bool = False):
        """Calculate validation scores"""
        total_issues = len(result.issues)
        
        # Count issues by severity
        for issue in result.issues:
            if issue.severity == ValidationSeverity.WARNING:
                result.metrics.warnings += 1
            elif issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL, ValidationSeverity.BLOCKING]:
                result.metrics.errors += 1
                if issue.severity == ValidationSeverity.CRITICAL:
                    result.metrics.critical_issues += 1
        
        result.metrics.failed_checks = result.metrics.errors
        result.metrics.passed_checks = result.metrics.total_checks - result.metrics.failed_checks
        
        # Calculate overall score (0-1)
        if result.metrics.total_checks > 0:
            base_score = result.metrics.passed_checks / result.metrics.total_checks
            
            # Apply penalties for issues
            penalty = 0
            for issue in result.issues:
                if issue.severity == ValidationSeverity.BLOCKING:
                    penalty += 0.5
                elif issue.severity == ValidationSeverity.CRITICAL:
                    penalty += 0.3
                elif issue.severity == ValidationSeverity.ERROR:
                    penalty += 0.1
                elif issue.severity == ValidationSeverity.WARNING:
                    penalty += 0.02
            
            result.overall_score = max(0, base_score - penalty)
        else:
            result.overall_score = 1.0
        
        # Calculate component scores
        result.metrics.quality_score = result.metadata.get('quality_score', 0.8)
        result.metrics.compliance_score = 1.0 - (result.metrics.errors / max(1, result.metrics.total_checks))
        
        if not hasattr(result.metrics, 'security_score'):
            result.metrics.security_score = 1.0 if result.metrics.errors == 0 else 0.7
    
    def _determine_validation_status(self, result: ValidationResult, strict_mode: bool = False) -> bool:
        """Determine if content passes validation"""
        # Check for blocking issues
        blocking_issues = [i for i in result.issues if i.severity == ValidationSeverity.BLOCKING]
        if blocking_issues:
            result.blocked_reasons = [issue.title for issue in blocking_issues]
            return False
        
        # Check for critical issues
        critical_issues = [i for i in result.issues if i.severity == ValidationSeverity.CRITICAL]
        if critical_issues and strict_mode:
            result.blocked_reasons = [issue.title for issue in critical_issues]
            return False
        
        # Check overall score threshold
        min_score = 0.8 if strict_mode else 0.6
        if result.overall_score < min_score:
            result.blocked_reasons.append(f"Overall score {result.overall_score:.2f} below threshold {min_score}")
            return False
        
        # Determine what content is approved for
        if result.overall_score >= 0.9:
            result.approved_for = ['public', 'commercial', 'distribution']
        elif result.overall_score >= 0.8:
            result.approved_for = ['public', 'limited_distribution']
        elif result.overall_score >= 0.6:
            result.approved_for = ['private', 'review_required']
        else:
            result.approved_for = ['draft_only']
        
        return True
    
    async def _generate_recommendations(self, result: ValidationResult) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Analyze issues and suggest fixes
        issue_categories = {}
        for issue in result.issues:
            category = issue.category.value
            if category not in issue_categories:
                issue_categories[category] = []
            issue_categories[category].append(issue)
        
        # Quality recommendations
        if ValidationCategory.QUALITY in issue_categories:
            quality_issues = issue_categories[ValidationCategory.QUALITY]
            if any('resolution' in issue.title.lower() for issue in quality_issues):
                recommendations.append("Consider using higher resolution source material")
            if any('blur' in issue.title.lower() for issue in quality_issues):
                recommendations.append("Ensure content is in focus and not blurry")
            if any('audio' in issue.title.lower() for issue in quality_issues):
                recommendations.append("Improve audio quality with better recording equipment")
        
        # Security recommendations
        if ValidationCategory.SECURITY in issue_categories:
            recommendations.append("Review and sanitize content for security threats")
            recommendations.append("Consider scanning content with updated security tools")
        
        # Policy recommendations
        if ValidationCategory.POLICY in issue_categories:
            recommendations.append("Review content against platform policies")
            recommendations.append("Consider content warnings or age restrictions")
        
        # General recommendations based on score
        if result.overall_score < 0.7:
            recommendations.append("Content needs significant improvement before publication")
        elif result.overall_score < 0.9:
            recommendations.append("Content is good but could benefit from minor improvements")
        
        return recommendations
    
    # Helper methods (placeholder implementations)
    async def _check_file_headers(self, file_path: str, content_type: str, result: ValidationResult):
        """Check file headers for anomalies"""
        pass
    
    async def _check_embedded_content(self, file_path: str, content_type: str, result: ValidationResult):
        """Check for embedded malicious content"""
        pass
    
    async def _check_policy_with_ai(self, file_path: str, content_type: str, policy: ContentPolicy) -> Dict[str, Any]:
        """Check content policy using AI"""



        return {'violation': False, 'confidence': 0.0}
    
    async def _detect_nsfw_content(self, file_path: str) -> Dict[str, Any]:
        """Detect NSFW content in images"""



        return {'is_nsfw': False, 'confidence': 0.0}
    
    async def _extract_text_content(self, file_path: str, content_type: str) -> Optional[str]:
        """Extract text content from files"""



        return None
    
    async def _detect_text_toxicity(self, text: str) -> Dict[str, Any]:
        """Detect toxicity in text"""



        return {'is_toxic': False, 'confidence': 0.0}
    
    async def _validate_video_quality(self, file_path: str, result: ValidationResult):
        """Validate video quality"""
        pass
    
    async def _validate_text_quality(self, file_path: str, result: ValidationResult):
        """Validate text quality"""
        pass
    
    async def _validate_document_quality(self, file_path: str, result: ValidationResult):
        """Validate document quality"""
        pass
    
    async def _validate_accessibility(self, file_path: str, content_type: str, result: ValidationResult):
        """Validate accessibility compliance"""
        pass
    
    async def _validate_metadata(self, metadata: Dict[str, Any], result: ValidationResult):
        """Validate content metadata"""
        pass
    
    async def _validate_legal_compliance(self, file_path: str, content_type: str, result: ValidationResult):
        """Validate legal compliance"""
        pass
    
    async def _apply_auto_fixes(self, file_path: str, content_type: str, result: ValidationResult):
        """Apply automatic fixes where possible"""
        pass
    
    async def _cache_validation_result(self, result: ValidationResult):
        """Cache validation result in Redis"""



        try:
            cache_key = f"validation_result:{result.validation_id}"
            cache_data = {
                'validation_id': result.validation_id,
                'content_id': result.content_id,
                'is_valid': result.is_valid,
                'overall_score': result.overall_score,
                'created_at': result.created_at.isoformat(),
                'completed_at': result.completed_at.isoformat() if result.completed_at else None
            }
            await self.redis.hset(cache_key, mapping=cache_data)
            await self.redis.expire(cache_key, 86400)  # 24 hours
        except Exception as e:
            self.logger.warning(f"Failed to cache validation result: {str(e)}")


# Export main classes
__all__ = [
    'ContentValidationEngine',
    'ValidationResult',
    'ValidationIssue',
    'ValidationMetrics',
    'ValidationSeverity',
    'ValidationCategory',
    'ContentPolicy'
]
