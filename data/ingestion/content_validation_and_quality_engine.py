"""Content Validation and Quality Engine
====================================

Professional content validation and quality assessment engine for the IA Influencer Agent platform.
Provides comprehensive security validation, quality scoring, compliance checking, and threat detection
with enterprise-grade performance and AI-powered analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.
"""

import asyncio
import logging
import uuid
import hashlib
import tempfile
import os
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, BinaryIO, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import mimetypes

# Security and content analysis libraries
import magic
from PIL import Image
import cv2
import numpy as np
import librosa
import soundfile as sf

# AI/ML libraries for content analysis
from transformers import pipeline
import spacy
from langdetect import detect, DetectorFactory
import textstat

# Core exceptions
try:
    from core.exceptions import ValidationError, SecurityError, QualityError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class SecurityError(Exception): pass
    class QualityError(Exception): pass


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationCategory(Enum):
    """Validation category types"""
    SECURITY = "security"
    QUALITY = "quality"
    COMPLIANCE = "compliance"
    CONTENT_POLICY = "content_policy"
    TECHNICAL = "technical"
    METADATA = "metadata"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"


class ThreatLevel(Enum):
    """Security threat levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class QualityDimension(Enum):
    """Quality assessment dimensions"""
    TECHNICAL_QUALITY = "technical_quality"
    CONTENT_QUALITY = "content_quality"
    AESTHETIC_QUALITY = "aesthetic_quality"
    AUDIO_QUALITY = "audio_quality"
    VIDEO_QUALITY = "video_quality"
    TEXT_QUALITY = "text_quality"
    METADATA_QUALITY = "metadata_quality"
    COMPLIANCE_QUALITY = "compliance_quality"


class ContentPolicy(Enum):
    """Content policy categories"""
    ADULT_CONTENT = "adult_content"
    VIOLENCE = "violence"
    HATE_SPEECH = "hate_speech"
    HARASSMENT = "harassment"
    MISINFORMATION = "misinformation"
    COPYRIGHT_VIOLATION = "copyright_violation"
    SPAM = "spam"
    MALWARE = "malware"
    PRIVACY_VIOLATION = "privacy_violation"
    ILLEGAL_CONTENT = "illegal_content"


@dataclass
class ValidationIssue:
    """Individual validation issue"""
    issue_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: ValidationCategory = ValidationCategory.TECHNICAL
    severity: ValidationSeverity = ValidationSeverity.LOW
    title: str = ""
    description: str = ""
    recommendation: str = ""
    affected_component: str = ""
    location: Optional[str] = None
    confidence: float = 1.0
    auto_fixable: bool = False
    fix_suggestion: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ValidationMetrics:
    """Validation performance metrics"""
    total_checks_performed: int = 0
    issues_found: int = 0
    critical_issues: int = 0
    high_issues: int = 0
    medium_issues: int = 0
    low_issues: int = 0
    info_issues: int = 0
    
    # Quality scores by dimension (0-100)
    technical_quality_score: float = 0.0
    content_quality_score: float = 0.0
    security_score: float = 0.0
    compliance_score: float = 0.0
    overall_quality_score: float = 0.0
    
    # Performance metrics
    validation_duration: float = 0.0
    checks_per_second: float = 0.0
    
    # Coverage metrics
    security_checks_coverage: float = 0.0
    quality_checks_coverage: float = 0.0
    compliance_checks_coverage: float = 0.0


@dataclass
class ValidationResult:
    """Complete validation result"""
    validation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: Optional[str] = None
    status: str = "pending"  # pending, completed, failed
    
    # Validation results
    is_valid: bool = True
    is_safe: bool = True
    is_compliant: bool = True
    is_high_quality: bool = True
    
    # Issues and recommendations
    issues: List[ValidationIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Metrics and scores
    metrics: Optional[ValidationMetrics] = None
    quality_scores: Dict[str, float] = field(default_factory=dict)
    security_assessment: Dict[str, Any] = field(default_factory=dict)
    compliance_status: Dict[str, bool] = field(default_factory=dict)
    
    # Policy violations
    policy_violations: List[ContentPolicy] = field(default_factory=list)
    threat_level: ThreatLevel = ThreatLevel.NONE
    
    # Metadata
    validation_timestamp: datetime = field(default_factory=datetime.utcnow)
    validator_version: str = "1.0.0"
    validation_config: Dict[str, Any] = field(default_factory=dict)
    
    # Results summary
    summary: Dict[str, Any] = field(default_factory=dict)


class ContentValidationEngine:
    """
    Professional content validation engine for enterprise security and quality assessment.
    
    Provides comprehensive validation capabilities including security scanning, quality assessment,
    compliance checking, content policy enforcement, and AI-powered threat detection.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize content validation engine"""
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Validation configuration
        self.strict_mode = self.config.get('strict_mode', False)
        self.enable_ai_analysis = self.config.get('enable_ai_analysis', True)
        self.max_file_size_mb = self.config.get('max_file_size_mb', 1024)
        self.timeout_seconds = self.config.get('timeout_seconds', 300)
        
        # Security configuration
        self.malware_scanning_enabled = self.config.get('malware_scanning', True)
        self.content_policy_enforcement = self.config.get('content_policy_enforcement', True)
        self.privacy_scanning_enabled = self.config.get('privacy_scanning', True)
        
        # Quality thresholds
        self.quality_thresholds = {
            'technical_quality_min': self.config.get('technical_quality_min', 0.7),
            'content_quality_min': self.config.get('content_quality_min', 0.6),
            'security_score_min': self.config.get('security_score_min', 0.8),
            'compliance_score_min': self.config.get('compliance_score_min', 0.9)
        }
        
        # Initialize AI models
        self._init_ai_models()
        
        # Initialize validation rules
        self._init_validation_rules()
        
        # Performance tracking
        self._validation_stats = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'average_validation_time': 0.0,
            'security_threats_detected': 0,
            'quality_issues_found': 0
        }
    
    def _init_ai_models(self):
        """Initialize AI models for content analysis"""
        try:
            if self.enable_ai_analysis:
                # NSFW content detection
                self.nsfw_detector = pipeline(
                    "image-classification",
                    model="Falconsai/nsfw_image_detection",
                    device=-1  # Use CPU
                ) if self.config.get('nsfw_detection', True) else None
                
                # Toxicity detection
                self.toxicity_detector = pipeline(
                    "text-classification",
                    model="unitary/toxic-bert",
                    device=-1
                ) if self.config.get('toxicity_detection', True) else None
                
                # Hate speech detection
                self.hate_speech_detector = pipeline(
                    "text-classification",
                    model="davidson/hate-speech-detection",
                    device=-1
                ) if self.config.get('hate_speech_detection', True) else None
                
                # Sentiment analysis
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    device=-1
                )
                
                # Load spaCy for advanced NLP
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                except OSError:
                    self.logger.warning("spaCy model not found, some NLP features disabled")
                    self.nlp = None
            
            else:
                self.nsfw_detector = None
                self.toxicity_detector = None
                self.hate_speech_detector = None
                self.sentiment_analyzer = None
                self.nlp = None
            
            self.logger.info("AI models initialized successfully")
            
        except Exception as e:
            self.logger.warning(f"AI model initialization failed: {str(e)}")
            # Set fallback None values
            self.nsfw_detector = None
            self.toxicity_detector = None
            self.hate_speech_detector = None
            self.sentiment_analyzer = None
            self.nlp = None
    
    def _init_validation_rules(self):
        """Initialize validation rules and patterns"""
        try:
            # Malware signatures (simplified examples)
            self.malware_signatures = [
                b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*',  # EICAR test
                b'\\x4d\\x5a',  # PE executable header
                b'\\x7f\\x45\\x4c\\x46',  # ELF executable header
            ]
            
            # Suspicious patterns
            self.suspicious_patterns = [
                re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
                re.compile(r'javascript:', re.IGNORECASE),
                re.compile(r'data:.*base64,', re.IGNORECASE),
                re.compile(r'eval\s*\(', re.IGNORECASE),
                re.compile(r'document\.write\s*\(', re.IGNORECASE),
            ]
            
            # Privacy patterns (PII detection)
            self.privacy_patterns = {
                'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
                'phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
                'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
                'credit_card': re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
                'ip_address': re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
            }
            
            # Content policy keywords
            self.policy_keywords = {
                ContentPolicy.HATE_SPEECH: [
                    'hate', 'discrimination', 'prejudice', 'bigotry', 'racism'
                ],
                ContentPolicy.VIOLENCE: [
                    'violence', 'weapon', 'gun', 'knife', 'bomb', 'kill', 'murder'
                ],
                ContentPolicy.ADULT_CONTENT: [
                    'explicit', 'adult', 'nsfw', 'pornographic', 'sexual'
                ],
                ContentPolicy.HARASSMENT: [
                    'harassment', 'bullying', 'stalking', 'intimidation', 'threat'
                ]
            }
            
            # Quality indicators
            self.quality_indicators = {
                'high_quality_formats': ['.flac', '.wav', '.png', '.tiff', '.mp4', '.mov'],
                'medium_quality_formats': ['.mp3', '.jpg', '.jpeg', '.avi', '.mkv'],
                'low_quality_formats': ['.gif', '.bmp', '.3gp', '.wmv'],
                'min_resolution_hd': (1280, 720),
                'min_bitrate_hq': 320000,  # 320 kbps
                'min_sample_rate': 44100
            }
            
        except Exception as e:
            self.logger.error(f"Validation rules initialization failed: {str(e)}")
    
    async def validate_content(self, content_data: bytes, filename: str,
                             metadata: Dict[str, Any] = None) -> ValidationResult:
        """
        Perform comprehensive content validation.
        
        Args:
            content_data: Content file data
            filename: Original filename
            metadata: Optional content metadata
            
        Returns:
            Complete validation result
        """
        start_time = datetime.utcnow()
        result = ValidationResult()
        
        try:
            self.logger.info(f"Starting content validation: {filename}")
            
            # Initialize validation metrics
            result.metrics = ValidationMetrics()
            result.validation_config = self.config.copy()
            
            # Basic file validation
            await self._validate_file_basics(content_data, filename, result)
            
            # Security validation
            await self._validate_security(content_data, filename, result)
            
            # Content policy validation
            await self._validate_content_policy(content_data, filename, result)
            
            # Quality assessment
            await self._assess_quality(content_data, filename, result)
            
            # Compliance checking
            await self._check_compliance(content_data, filename, result, metadata)
            
            # AI-powered analysis
            if self.enable_ai_analysis:
                await self._ai_content_analysis(content_data, filename, result)
            
            # Calculate final scores and status
            await self._calculate_final_scores(result)
            
            # Generate summary and recommendations
            await self._generate_summary_and_recommendations(result)
            
            result.status = "completed"
            self._validation_stats['total_validations'] += 1
            self._validation_stats['successful_validations'] += 1
            
        except Exception as e:
            self.logger.error(f"Content validation failed: {filename} - {str(e)}")
            result.status = "failed"
            result.is_valid = False
            result.issues.append(ValidationIssue(
                category=ValidationCategory.TECHNICAL,
                severity=ValidationSeverity.CRITICAL,
                title="Validation Failed",
                description=f"Validation process failed: {str(e)}",
                recommendation="Review content and retry validation"
            ))
            self._validation_stats['failed_validations'] += 1
        
        finally:
            # Calculate metrics
            validation_duration = (datetime.utcnow() - start_time).total_seconds()
            if result.metrics:
                result.metrics.validation_duration = validation_duration
                if result.metrics.total_checks_performed > 0:
                    result.metrics.checks_per_second = (
                        result.metrics.total_checks_performed / validation_duration
                    )
            
            # Update global stats
            self._validation_stats['average_validation_time'] = (
                self._validation_stats['average_validation_time'] * 
                (self._validation_stats['total_validations'] - 1) + validation_duration
            ) / self._validation_stats['total_validations']
        
        return result
    
    async def batch_validate_content(self, content_items: List[Tuple[bytes, str, Dict[str, Any]]]) -> List[ValidationResult]:
        """
        Validate multiple content items in batch.
        
        Args:
            content_items: List of (content_data, filename, metadata) tuples
            
        Returns:
            List of validation results
        """
        try:
            self.logger.info(f"Starting batch validation: {len(content_items)} items")
            
            # Process items concurrently with semaphore control
            semaphore = asyncio.Semaphore(3)  # Limit concurrent validations
            
            async def validate_single(item):
                async with semaphore:
                    content_data, filename, metadata = item
                    return await self.validate_content(content_data, filename, metadata)
            
            tasks = [validate_single(item) for item in content_items]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    error_result = ValidationResult()
                    error_result.status = "failed"
                    error_result.is_valid = False
                    error_result.issues.append(ValidationIssue(
                        category=ValidationCategory.TECHNICAL,
                        severity=ValidationSeverity.CRITICAL,
                        title="Batch Validation Failed",
                        description=str(result),
                        recommendation="Review content and retry validation"
                    ))
                    final_results.append(error_result)
                else:
                    final_results.append(result)
            
            return final_results
            
        except Exception as e:
            self.logger.error(f"Batch validation failed: {str(e)}")
            raise ValidationError(f"Batch validation failed: {str(e)}")
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation engine statistics"""
        return self._validation_stats.copy()
    
    def get_validation_capabilities(self) -> Dict[str, Any]:
        """Get validation engine capabilities"""
        return {
            'security_scanning': self.malware_scanning_enabled,
            'content_policy_enforcement': self.content_policy_enforcement,
            'privacy_scanning': self.privacy_scanning_enabled,
            'ai_analysis': self.enable_ai_analysis,
            'supported_formats': list(self.quality_indicators['high_quality_formats'] + 
                                   self.quality_indicators['medium_quality_formats'] +
                                   self.quality_indicators['low_quality_formats']),
            'quality_dimensions': [d.value for d in QualityDimension],
            'validation_categories': [c.value for c in ValidationCategory],
            'threat_levels': [t.value for t in ThreatLevel],
            'content_policies': [p.value for p in ContentPolicy]
        }
    
    # Private validation methods
    
    async def _validate_file_basics(self, content_data: bytes, filename: str, result: ValidationResult):
        """Validate basic file properties"""
        try:
            result.metrics.total_checks_performed += 1
            
            # File size validation
            file_size_mb = len(content_data) / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                result.issues.append(ValidationIssue(
                    category=ValidationCategory.TECHNICAL,
                    severity=ValidationSeverity.HIGH,
                    title="File Size Exceeded",
                    description=f"File size {file_size_mb:.1f}MB exceeds limit of {self.max_file_size_mb}MB",
                    recommendation="Compress file or reduce quality",
                    affected_component="file_size"
                ))
                result.is_valid = False
            
            # File format validation
            try:
                detected_type = magic.from_buffer(content_data, mime=True)
                file_ext = Path(filename).suffix.lower()
                
                # Check if MIME type matches extension
                expected_mime = mimetypes.guess_type(filename)[0]
                if expected_mime and detected_type != expected_mime:
                    result.issues.append(ValidationIssue(
                        category=ValidationCategory.SECURITY,
                        severity=ValidationSeverity.MEDIUM,
                        title="MIME Type Mismatch",
                        description=f"Detected MIME type {detected_type} doesn't match extension {file_ext}",
                        recommendation="Verify file integrity and format",
                        affected_component="file_format"
                    ))
                
                result.security_assessment['mime_type'] = detected_type
                result.security_assessment['file_extension'] = file_ext
                
            except Exception as e:
                result.warnings.append(f"MIME type detection failed: {str(e)}")
            
            # File integrity check (basic)
            if len(content_data) == 0:
                result.issues.append(ValidationIssue(
                    category=ValidationCategory.TECHNICAL,
                    severity=ValidationSeverity.CRITICAL,
                    title="Empty File",
                    description="File contains no data",
                    recommendation="Provide valid file content",
                    affected_component="file_content"
                ))
                result.is_valid = False
            
        except Exception as e:
            self.logger.error(f"Basic file validation failed: {str(e)}")
            result.warnings.append(f"Basic validation warning: {str(e)}")
    
    async def _validate_security(self, content_data: bytes, filename: str, result: ValidationResult):
        """Perform security validation"""
        try:
            result.metrics.total_checks_performed += 1
            
            # Malware signature scanning
            if self.malware_scanning_enabled:
                for signature in self.malware_signatures:
                    if signature in content_data:
                        result.issues.append(ValidationIssue(
                            category=ValidationCategory.SECURITY,
                            severity=ValidationSeverity.CRITICAL,
                            title="Malware Signature Detected",
                            description="Content contains known malware signature",
                            recommendation="Do not process this content",
                            affected_component="content_data"
                        ))
                        result.is_safe = False
                        result.threat_level = ThreatLevel.CRITICAL
                        self._validation_stats['security_threats_detected'] += 1
            
            # Suspicious pattern detection
            content_str = content_data.decode('utf-8', errors='ignore')
            for pattern in self.suspicious_patterns:
                matches = pattern.findall(content_str)
                if matches:
                    result.issues.append(ValidationIssue(
                        category=ValidationCategory.SECURITY,
                        severity=ValidationSeverity.HIGH,
                        title="Suspicious Pattern Detected",
                        description=f"Content contains suspicious patterns: {len(matches)} matches",
                        recommendation="Review content for security risks",
                        affected_component="content_patterns",
                        metadata={'matches_count': len(matches)}
                    ))
                    if result.threat_level == ThreatLevel.NONE:
                        result.threat_level = ThreatLevel.MEDIUM
            
            # Privacy/PII scanning
            if self.privacy_scanning_enabled:
                pii_found = {}
                for pii_type, pattern in self.privacy_patterns.items():
                    matches = pattern.findall(content_str)
                    if matches:
                        pii_found[pii_type] = len(matches)
                
                if pii_found:
                    result.issues.append(ValidationIssue(
                        category=ValidationCategory.COMPLIANCE,
                        severity=ValidationSeverity.HIGH,
                        title="Personal Information Detected",
                        description=f"Content contains PII: {', '.join(pii_found.keys())}",
                        recommendation="Remove or redact personal information",
                        affected_component="pii_data",
                        metadata={'pii_types': pii_found}
                    ))
                    result.compliance_status['privacy_compliant'] = False
            
            # File hash for integrity
            result.security_assessment['file_hash'] = hashlib.sha256(content_data).hexdigest()
            result.security_assessment['file_size'] = len(content_data)
            
        except Exception as e:
            self.logger.error(f"Security validation failed: {str(e)}")
            result.warnings.append(f"Security validation warning: {str(e)}")
    
    async def _validate_content_policy(self, content_data: bytes, filename: str, result: ValidationResult):
        """Validate content against policies"""
        try:
            result.metrics.total_checks_performed += 1
            
            if not self.content_policy_enforcement:
                return
            
            # Text-based policy checking
            content_str = content_data.decode('utf-8', errors='ignore').lower()
            
            for policy, keywords in self.policy_keywords.items():
                violations = []
                for keyword in keywords:
                    if keyword in content_str:
                        violations.append(keyword)
                
                if violations:
                    result.policy_violations.append(policy)
                    result.issues.append(ValidationIssue(
                        category=ValidationCategory.CONTENT_POLICY,
                        severity=ValidationSeverity.HIGH,
                        title=f"Content Policy Violation: {policy.value}",
                        description=f"Content may violate {policy.value} policy",
                        recommendation="Review and modify content to comply with policies",
                        affected_component="content_text",
                        metadata={'violating_keywords': violations}
                    ))
            
            # Additional policy checks based on file type
            file_ext = Path(filename).suffix.lower()
            
            if file_ext in ['.exe', '.bat', '.cmd', '.scr', '.vbs']:
                result.policy_violations.append(ContentPolicy.MALWARE)
                result.issues.append(ValidationIssue(
                    category=ValidationCategory.CONTENT_POLICY,
                    severity=ValidationSeverity.CRITICAL,
                    title="Executable File Detected",
                    description="Executable files are not allowed",
                    recommendation="Upload non-executable content only",
                    affected_component="file_type"
                ))
                result.is_safe = False
            
        except Exception as e:
            self.logger.error(f"Content policy validation failed: {str(e)}")
            result.warnings.append(f"Content policy validation warning: {str(e)}")
    
    async def _assess_quality(self, content_data: bytes, filename: str, result: ValidationResult):
        """Assess content quality across multiple dimensions"""
        try:
            result.metrics.total_checks_performed += 1
            
            file_ext = Path(filename).suffix.lower()
            
            # Technical quality assessment based on format
            technical_score = 0.0
            
            if file_ext in self.quality_indicators['high_quality_formats']:
                technical_score = 0.9
            elif file_ext in self.quality_indicators['medium_quality_formats']:
                technical_score = 0.7
            elif file_ext in self.quality_indicators['low_quality_formats']:
                technical_score = 0.5
            else:
                technical_score = 0.3
            
            result.quality_scores[QualityDimension.TECHNICAL_QUALITY.value] = technical_score
            
            # Format-specific quality assessment
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
                await self._assess_image_quality(content_data, result)
            elif file_ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']:
                await self._assess_audio_quality(content_data, result)
            elif file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']:
                await self._assess_video_quality(content_data, result)
            elif file_ext in ['.txt', '.md', '.html', '.pdf', '.docx']:
                await self._assess_text_quality(content_data, result)
            
            # Metadata quality assessment
            metadata_score = 0.8  # Default score, would be calculated based on actual metadata
            result.quality_scores[QualityDimension.METADATA_QUALITY.value] = metadata_score
            
            # Overall technical quality
            result.metrics.technical_quality_score = technical_score * 100
            
            # Quality threshold checking
            if technical_score < self.quality_thresholds['technical_quality_min']:
                result.issues.append(ValidationIssue(
                    category=ValidationCategory.QUALITY,
                    severity=ValidationSeverity.MEDIUM,
                    title="Low Technical Quality",
                    description=f"Technical quality score {technical_score:.2f} below threshold",
                    recommendation="Use higher quality formats or improve content",
                    affected_component="technical_quality"
                ))
                result.is_high_quality = False
                self._validation_stats['quality_issues_found'] += 1
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {str(e)}")
            result.warnings.append(f"Quality assessment warning: {str(e)}")
    
    async def _assess_image_quality(self, content_data: bytes, result: ValidationResult):
        """Assess image-specific quality metrics"""
        try:
            with tempfile.NamedTemporaryFile() as temp_file:
                temp_file.write(content_data)
                temp_file.flush()
                
                # Load image
                image = Image.open(temp_file.name)
                
                # Resolution assessment
                width, height = image.size
                total_pixels = width * height
                
                quality_score = 0.5  # Base score
                
                if total_pixels >= 2073600:  # 1920x1080 (Full HD)
                    quality_score = 0.9
                elif total_pixels >= 921600:  # 1280x720 (HD)
                    quality_score = 0.8
                elif total_pixels >= 307200:  # 640x480 (VGA)
                    quality_score = 0.6
                
                # Aspect ratio check
                aspect_ratio = width / height
                if 0.5 <= aspect_ratio <= 2.0:  # Reasonable aspect ratio
                    quality_score += 0.1
                
                result.quality_scores[QualityDimension.AESTHETIC_QUALITY.value] = quality_score
                
                # Technical image analysis
                if content_data[:10]:  # Basic image validation
                    # Sharpness assessment using OpenCV
                    img_array = np.array(image.convert('L'))
                    laplacian_var = cv2.Laplacian(img_array, cv2.CV_64F).var()
                    
                    # Sharpness threshold (100 is reasonably sharp)
                    sharpness_score = min(laplacian_var / 100, 1.0)
                    
                    result.quality_scores['image_sharpness'] = sharpness_score
                    result.quality_scores['image_resolution'] = f"{width}x{height}"
                    result.quality_scores['image_aspect_ratio'] = round(aspect_ratio, 2)
        
        except Exception as e:
            self.logger.warning(f"Image quality assessment failed: {str(e)}")
    
    async def _assess_audio_quality(self, content_data: bytes, result: ValidationResult):
        """Assess audio-specific quality metrics"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav') as temp_file:
                temp_file.write(content_data)
                temp_file.flush()
                
                try:
                    # Load audio data
                    audio_data, sample_rate = librosa.load(temp_file.name, sr=None)
                    
                    quality_score = 0.5  # Base score
                    
                    # Sample rate assessment
                    if sample_rate >= 48000:
                        quality_score = 0.9
                    elif sample_rate >= 44100:
                        quality_score = 0.8
                    elif sample_rate >= 22050:
                        quality_score = 0.6
                    
                    # Dynamic range assessment
                    dynamic_range = np.max(audio_data) - np.min(audio_data)
                    if dynamic_range > 0.8:
                        quality_score += 0.1
                    
                    result.quality_scores[QualityDimension.AUDIO_QUALITY.value] = quality_score
                    result.quality_scores['audio_sample_rate'] = sample_rate
                    result.quality_scores['audio_duration'] = len(audio_data) / sample_rate
                    result.quality_scores['audio_dynamic_range'] = dynamic_range
                    
                except Exception as e:
                    self.logger.warning(f"Audio analysis failed: {str(e)}")
        
        except Exception as e:
            self.logger.warning(f"Audio quality assessment failed: {str(e)}")
    
    async def _assess_video_quality(self, content_data: bytes, result: ValidationResult):
        """Assess video-specific quality metrics"""
        try:
            # Video quality assessment would require more complex analysis
            # For now, provide basic assessment
            quality_score = 0.7  # Default score
            
            result.quality_scores[QualityDimension.VIDEO_QUALITY.value] = quality_score
            
        except Exception as e:
            self.logger.warning(f"Video quality assessment failed: {str(e)}")
    
    async def _assess_text_quality(self, content_data: bytes, result: ValidationResult):
        """Assess text-specific quality metrics"""
        try:
            text_content = content_data.decode('utf-8', errors='ignore')
            
            if len(text_content.strip()) == 0:
                result.quality_scores[QualityDimension.TEXT_QUALITY.value] = 0.0
                return
            
            quality_score = 0.5  # Base score
            
            # Length assessment
            word_count = len(text_content.split())
            if word_count >= 100:
                quality_score += 0.2
            elif word_count >= 50:
                quality_score += 0.1
            
            # Readability assessment
            try:
                flesch_score = textstat.flesch_reading_ease(text_content)
                if flesch_score >= 60:  # Easy to read
                    quality_score += 0.2
                elif flesch_score >= 30:  # Fairly difficult
                    quality_score += 0.1
                
                result.quality_scores['text_readability'] = flesch_score
                
            except Exception as e:
                self.logger.warning(f"Readability assessment failed: {str(e)}")
            
            # Language detection
            try:
                detected_lang = detect(text_content[:1000])  # Use first 1000 chars
                result.quality_scores['detected_language'] = detected_lang
                quality_score += 0.1  # Bonus for detected language
                
            except Exception as e:
                self.logger.warning(f"Language detection failed: {str(e)}")
            
            result.quality_scores[QualityDimension.TEXT_QUALITY.value] = min(quality_score, 1.0)
            result.quality_scores['text_word_count'] = word_count
            result.quality_scores['text_character_count'] = len(text_content)
            
        except Exception as e:
            self.logger.warning(f"Text quality assessment failed: {str(e)}")
    
    async def _check_compliance(self, content_data: bytes, filename: str, 
                              result: ValidationResult, metadata: Dict[str, Any] = None):
        """Check regulatory compliance"""
        try:
            result.metrics.total_checks_performed += 1
            
            # GDPR compliance check
            gdpr_compliant = True
            if result.security_assessment.get('pii_detected', False):
                gdpr_compliant = False
            
            # CCPA compliance check
            ccpa_compliant = gdpr_compliant  # Similar requirements
            
            # Content accessibility check
            accessibility_compliant = True
            file_ext = Path(filename).suffix.lower()
            
            # Check for accessibility features in various formats
            if file_ext in ['.mp4', '.avi', '.mov']:
                # Video should have captions/subtitles (simplified check)
                accessibility_compliant = False  # Assume no captions unless proven otherwise
                result.recommendations.append("Add captions/subtitles for accessibility compliance")
            
            elif file_ext in ['.mp3', '.wav', '.flac']:
                # Audio content should have transcripts
                accessibility_compliant = False  # Assume no transcript unless provided
                result.recommendations.append("Provide transcript for audio accessibility")
            
            # Platform-specific compliance
            platform_compliant = True
            if result.policy_violations:
                platform_compliant = False
            
            # Update compliance status
            result.compliance_status.update({
                'gdpr_compliant': gdpr_compliant,
                'ccpa_compliant': ccpa_compliant,
                'accessibility_compliant': accessibility_compliant,
                'platform_compliant': platform_compliant
            })
            
            # Overall compliance assessment
            compliance_score = sum(result.compliance_status.values()) / len(result.compliance_status)
            result.metrics.compliance_score = compliance_score * 100
            
            if compliance_score < self.quality_thresholds['compliance_score_min']:
                result.is_compliant = False
                result.issues.append(ValidationIssue(
                    category=ValidationCategory.COMPLIANCE,
                    severity=ValidationSeverity.HIGH,
                    title="Compliance Issues Detected",
                    description=f"Compliance score {compliance_score:.2f} below threshold",
                    recommendation="Address compliance issues before publishing",
                    affected_component="compliance",
                    metadata={'compliance_details': result.compliance_status}
                ))
            
        except Exception as e:
            self.logger.error(f"Compliance checking failed: {str(e)}")
            result.warnings.append(f"Compliance checking warning: {str(e)}")
    
    async def _ai_content_analysis(self, content_data: bytes, filename: str, result: ValidationResult):
        """Perform AI-powered content analysis"""
        try:
            result.metrics.total_checks_performed += 1
            
            file_ext = Path(filename).suffix.lower()
            
            # Image-based AI analysis
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'] and self.nsfw_detector:
                try:
                    with tempfile.NamedTemporaryFile() as temp_file:
                        temp_file.write(content_data)
                        temp_file.flush()
                        
                        image = Image.open(temp_file.name)
                        
                        # NSFW detection
                        nsfw_results = self.nsfw_detector(image)
                        
                        for prediction in nsfw_results:
                            if prediction['label'].lower() == 'nsfw' and prediction['score'] > 0.8:
                                result.policy_violations.append(ContentPolicy.ADULT_CONTENT)
                                result.issues.append(ValidationIssue(
                                    category=ValidationCategory.CONTENT_POLICY,
                                    severity=ValidationSeverity.HIGH,
                                    title="NSFW Content Detected",
                                    description=f"AI detected NSFW content (confidence: {prediction['score']:.2f})",
                                    recommendation="Review content appropriateness",
                                    affected_component="image_content",
                                    confidence=prediction['score']
                                ))
                        
                        result.security_assessment['nsfw_analysis'] = nsfw_results
                        
                except Exception as e:
                    self.logger.warning(f"NSFW detection failed: {str(e)}")
            
            # Text-based AI analysis
            if file_ext in ['.txt', '.md', '.html', '.pdf', '.docx']:
                try:
                    text_content = content_data.decode('utf-8', errors='ignore')
                    
                    if len(text_content.strip()) > 10:
                        # Toxicity detection
                        if self.toxicity_detector and len(text_content) < 512:
                            toxicity_results = self.toxicity_detector(text_content[:512])
                            
                            for result_item in toxicity_results:
                                if result_item['label'] == 'TOXIC' and result_item['score'] > 0.7:
                                    result.policy_violations.append(ContentPolicy.HATE_SPEECH)
                                    result.issues.append(ValidationIssue(
                                        category=ValidationCategory.CONTENT_POLICY,
                                        severity=ValidationSeverity.HIGH,
                                        title="Toxic Content Detected",
                                        description=f"AI detected toxic content (confidence: {result_item['score']:.2f})",
                                        recommendation="Review and moderate content",
                                        affected_component="text_content",
                                        confidence=result_item['score']
                                    ))
                            
                            result.security_assessment['toxicity_analysis'] = toxicity_results
                        
                        # Sentiment analysis
                        if self.sentiment_analyzer and len(text_content) < 512:
                            sentiment_results = self.sentiment_analyzer(text_content[:512])
                            result.quality_scores['sentiment_analysis'] = sentiment_results
                        
                        # Named entity recognition
                        if self.nlp and len(text_content) < 1000:
                            doc = self.nlp(text_content[:1000])
                            entities = [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]
                            result.quality_scores['named_entities'] = entities[:10]  # Limit to top 10
                
                except Exception as e:
                    self.logger.warning(f"Text AI analysis failed: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"AI content analysis failed: {str(e)}")
            result.warnings.append(f"AI analysis warning: {str(e)}")
    
    async def _calculate_final_scores(self, result: ValidationResult):
        """Calculate final validation scores"""
        try:
            # Security score based on threat level and issues
            security_score = 1.0
            if result.threat_level == ThreatLevel.CRITICAL:
                security_score = 0.0
            elif result.threat_level == ThreatLevel.HIGH:
                security_score = 0.3
            elif result.threat_level == ThreatLevel.MEDIUM:
                security_score = 0.6
            elif result.threat_level == ThreatLevel.LOW:
                security_score = 0.8
            
            # Adjust for security issues
            security_issues = sum(1 for issue in result.issues if issue.category == ValidationCategory.SECURITY)
            if security_issues > 0:
                security_score = max(0.0, security_score - (security_issues * 0.1))
            
            result.metrics.security_score = security_score * 100
            
            # Content quality score (average of all quality dimensions)
            quality_scores = [score for key, score in result.quality_scores.items() 
                            if isinstance(score, (int, float))]
            if quality_scores:
                result.metrics.content_quality_score = (sum(quality_scores) / len(quality_scores)) * 100
            else:
                result.metrics.content_quality_score = 50.0  # Default neutral score
            
            # Overall quality score (weighted average)
            weights = {
                'technical': 0.3,
                'content': 0.25,
                'security': 0.25,
                'compliance': 0.2
            }
            
            result.metrics.overall_quality_score = (
                result.metrics.technical_quality_score * weights['technical'] +
                result.metrics.content_quality_score * weights['content'] +
                result.metrics.security_score * weights['security'] +
                result.metrics.compliance_score * weights['compliance']
            )
            
            # Count issues by severity
            for issue in result.issues:
                if issue.severity == ValidationSeverity.CRITICAL:
                    result.metrics.critical_issues += 1
                elif issue.severity == ValidationSeverity.HIGH:
                    result.metrics.high_issues += 1
                elif issue.severity == ValidationSeverity.MEDIUM:
                    result.metrics.medium_issues += 1
                elif issue.severity == ValidationSeverity.LOW:
                    result.metrics.low_issues += 1
                elif issue.severity == ValidationSeverity.INFO:
                    result.metrics.info_issues += 1
            
            result.metrics.issues_found = len(result.issues)
            
            # Update final validation status
            if result.metrics.critical_issues > 0:
                result.is_valid = False
                result.is_safe = False
            
            if result.metrics.security_score < (self.quality_thresholds['security_score_min'] * 100):
                result.is_safe = False
            
            if result.metrics.overall_quality_score < 60:  # 60% minimum overall quality
                result.is_high_quality = False
            
        except Exception as e:
            self.logger.error(f"Final score calculation failed: {str(e)}")
    
    async def _generate_summary_and_recommendations(self, result: ValidationResult):
        """Generate validation summary and recommendations"""
        try:
            # Generate summary
            summary = {
                'overall_status': 'PASS' if result.is_valid and result.is_safe else 'FAIL',
                'quality_level': 'HIGH' if result.is_high_quality else 'MEDIUM' if result.metrics.overall_quality_score >= 40 else 'LOW',
                'security_status': 'SECURE' if result.is_safe else 'UNSAFE',
                'compliance_status': 'COMPLIANT' if result.is_compliant else 'NON_COMPLIANT',
                'total_issues': len(result.issues),
                'critical_issues': result.metrics.critical_issues,
                'policy_violations': len(result.policy_violations),
                'threat_level': result.threat_level.value,
                'overall_score': round(result.metrics.overall_quality_score, 1)
            }
            
            result.summary = summary
            
            # Generate recommendations based on issues
            recommendations = set()
            
            if result.metrics.critical_issues > 0:
                recommendations.add("Address all critical security issues before processing")
            
            if result.metrics.security_score < 80:
                recommendations.add("Enhance content security measures")
            
            if result.metrics.overall_quality_score < 70:
                recommendations.add("Improve content quality before publication")
            
            if result.policy_violations:
                recommendations.add("Review content for policy compliance")
            
            if not result.is_compliant:
                recommendations.add("Ensure regulatory compliance requirements are met")
            
            # Add format-specific recommendations
            if result.metrics.technical_quality_score < 70:
                recommendations.add("Consider using higher quality formats")
            
            # Add existing recommendations
            for rec in result.recommendations:
                recommendations.add(rec)
            
            result.recommendations = list(recommendations)
            
        except Exception as e:
            self.logger.error(f"Summary generation failed: {str(e)}")