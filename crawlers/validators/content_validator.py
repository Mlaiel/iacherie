"""
Content Validation Engine for Crawler System
============================================

Advanced content validation system for the IA Influencer Agent Platform
providing comprehensive content integrity, quality, and compliance validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use, reproduction, or distribution strictly prohibited

Features:
- Multi-format content validation
- Content quality assessment
- Platform-specific compliance
- Business rule enforcement
- Security threat detection
"""

import re
import hashlib
import mimetypes
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

from ..utils.exceptions import ValidationException

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content type enumeration for validation"""
    TEXT = "text"
    HTML = "html"
    JSON = "json"
    XML = "xml"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    SOCIAL_POST = "social_post"
    BLOG_POST = "blog_post"
    NEWS_ARTICLE = "news_article"
    PRODUCT_LISTING = "product_listing"
    USER_PROFILE = "user_profile"
    UNKNOWN = "unknown"


class ValidationLevel(Enum):
    """Validation strictness levels"""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    ENTERPRISE = "enterprise"


class ValidationStatus(Enum):
    """Validation result status"""
    VALID = "valid"
    WARNING = "warning"
    ERROR = "error"
    BLOCKED = "blocked"


@dataclass
class ValidationIssue:
    """Individual validation issue"""
    level: ValidationStatus
    code: str
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None
    rule_name: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ContentMetadata:
    """Content metadata for validation"""
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    language: Optional[str] = None
    charset: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    source_url: Optional[str] = None
    platform: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Comprehensive validation result"""
    is_valid: bool
    status: ValidationStatus
    content_type: ContentType
    validation_level: ValidationLevel
    issues: List[ValidationIssue] = field(default_factory=list)
    quality_score: float = 0.0
    compliance_score: float = 0.0
    security_score: float = 0.0
    overall_score: float = 0.0
    processing_time_ms: float = 0.0
    metadata: Optional[ContentMetadata] = None
    recommendations: List[str] = field(default_factory=list)
    validated_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def has_errors(self) -> bool:
        """Check if validation has errors"""
        return any(issue.level in [ValidationStatus.ERROR, ValidationStatus.BLOCKED] 
                  for issue in self.issues)
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings"""
        return any(issue.level == ValidationStatus.WARNING for issue in self.issues)
    
    @property
    def error_count(self) -> int:
        """Count of error-level issues"""
        return len([i for i in self.issues if i.level in [ValidationStatus.ERROR, ValidationStatus.BLOCKED]])
    
    @property
    def warning_count(self) -> int:
        """Count of warning-level issues"""
        return len([i for i in self.issues if i.level == ValidationStatus.WARNING])


class ContentValidator:
    """
    Enterprise-grade content validation engine for crawler systems.
    
    Provides comprehensive validation including:
    - Content structure and format validation
    - Quality assessment and scoring
    - Security threat detection
    - Platform compliance checking
    - Business rule enforcement
    """
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        self.validation_level = validation_level
        self.business_rules = self._load_business_rules()
        self.security_patterns = self._load_security_patterns()
        self.quality_metrics = self._load_quality_metrics()
        self.platform_requirements = self._load_platform_requirements()
        
        # Performance tracking
        self.validation_cache = {}
        self.cache_ttl = timedelta(minutes=30)
        
        logger.info(f"ContentValidator initialized with level: {validation_level.value}")
    
    def validate_content(
        self,
        content: Union[str, bytes],
        content_type: ContentType,
        metadata: Optional[ContentMetadata] = None,
        platform_target: Optional[str] = None,
        **kwargs
    ) -> ValidationResult:
        """
        Validate content comprehensively.
        
        Args:
            content: Content to validate
            content_type: Type of content
            metadata: Optional content metadata
            platform_target: Target platform for compliance
            **kwargs: Additional validation parameters
            
        Returns:
            ValidationResult: Comprehensive validation result
        """
        start_time = datetime.utcnow()
        
        # Check cache first
        cache_key = self._generate_cache_key(content, content_type, metadata)
        if cache_key in self.validation_cache:
            cached_result, cached_time = self.validation_cache[cache_key]
            if datetime.utcnow() - cached_time < self.cache_ttl:
                return cached_result
        
        result = ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            content_type=content_type,
            validation_level=self.validation_level,
            metadata=metadata
        )
        
        try:
            # Basic content validation
            self._validate_basic_content(content, result)
            
            # Content type specific validation
            self._validate_content_type_specific(content, content_type, result)
            
            # Security validation
            self._validate_security(content, result)
            
            # Quality assessment
            self._assess_quality(content, content_type, result, metadata)
            
            # Business rules validation
            self._validate_business_rules(content, content_type, result, **kwargs)
            
            # Platform compliance (if specified)
            if platform_target:
                self._validate_platform_compliance(content, content_type, platform_target, result)
            
            # Calculate final scores and status
            self._calculate_scores(result)
            self._determine_final_status(result)
            
            # Generate recommendations
            self._generate_recommendations(result)
            
        except Exception as e:
            logger.error(f"Content validation failed: {str(e)}")
            result.issues.append(ValidationIssue(
                level=ValidationStatus.ERROR,
                code="VALIDATION_EXCEPTION",
                message=f"Validation process failed: {str(e)}"
            ))
            result.is_valid = False
            result.status = ValidationStatus.ERROR
        
        # Record processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        result.processing_time_ms = processing_time
        
        # Cache result
        self.validation_cache[cache_key] = (result, datetime.utcnow())
        
        logger.debug(f"Content validation completed in {processing_time:.2f}ms")
        return result
    
    def _validate_basic_content(self, content: Union[str, bytes], result: ValidationResult) -> None:
        """Perform basic content validation"""
        
        # Check if content is empty
        if not content:
            result.issues.append(ValidationIssue(
                level=ValidationStatus.ERROR,
                code="EMPTY_CONTENT",
                message="Content is empty or null"
            ))
            return
        
        # Content size validation
        content_size = len(content)
        max_size = 50 * 1024 * 1024  # 50MB default limit
        
        if content_size > max_size:
            result.issues.append(ValidationIssue(
                level=ValidationStatus.ERROR,
                code="CONTENT_TOO_LARGE",
                message=f"Content size ({content_size} bytes) exceeds maximum ({max_size} bytes)"
            ))
        
        # Encoding validation for text content
        if isinstance(content, str):
            try:
                content.encode('utf-8')
            except UnicodeEncodeError as e:
                result.issues.append(ValidationIssue(
                    level=ValidationStatus.WARNING,
                    code="ENCODING_ISSUE",
                    message=f"Content encoding issue: {str(e)}"
                ))
    
    def _validate_content_type_specific(
        self, 
        content: Union[str, bytes], 
        content_type: ContentType, 
        result: ValidationResult
    ) -> None:
        """Perform content type specific validation"""
        
        if content_type == ContentType.HTML:
            self._validate_html_content(content, result)
        elif content_type == ContentType.JSON:
            self._validate_json_content(content, result)
        elif content_type == ContentType.XML:
            self._validate_xml_content(content, result)
        elif content_type == ContentType.SOCIAL_POST:
            self._validate_social_post(content, result)
        elif content_type == ContentType.BLOG_POST:
            self._validate_blog_post(content, result)
        elif content_type == ContentType.NEWS_ARTICLE:
            self._validate_news_article(content, result)
        elif content_type == ContentType.PRODUCT_LISTING:
            self._validate_product_listing(content, result)
        elif content_type == ContentType.USER_PROFILE:
            self._validate_user_profile(content, result)
        
        # Media content validation
        if content_type in [ContentType.AUDIO, ContentType.VIDEO, ContentType.IMAGE]:
            self._validate_media_content(content, content_type, result)
    
    def _validate_html_content(self, content: str, result: ValidationResult) -> None:
        """Validate HTML content structure and safety"""
        
        # Check for basic HTML structure
        if not re.search(r'<html[^>]*>', content, re.IGNORECASE):
            result.issues.append(ValidationIssue(
                level=ValidationStatus.WARNING,
                code="MISSING_HTML_TAG",
                message="HTML content missing root <html> tag"
            ))
        
        # Check for dangerous scripts
        script_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'data:text/html',
            r'on\w+\s*='
        ]
        
        for pattern in script_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                result.issues.append(ValidationIssue(
                    level=ValidationStatus.ERROR,
                    code="DANGEROUS_SCRIPT",
                    message=f"Potentially dangerous script detected: {pattern}"
                ))
        
        # Check for balanced tags
        self._validate_html_tag_balance(content, result)
    
    def _validate_json_content(self, content: str, result: ValidationResult) -> None:
        """Validate JSON content structure"""
        import json
        
        try:
            data = json.loads(content)
            
            # Check for excessive nesting
            max_depth = self._get_json_depth(data)
            if max_depth > 20:
                result.issues.append(ValidationIssue(
                    level=ValidationStatus.WARNING,
                    code="DEEP_JSON_NESTING",
                    message=f"JSON nesting depth ({max_depth}) is very deep"
                ))
                
        except json.JSONDecodeError as e:
            result.issues.append(ValidationIssue(
                level=ValidationStatus.ERROR,
                code="INVALID_JSON",
                message=f"Invalid JSON format: {str(e)}"
            ))
    
    def _validate_security(self, content: Union[str, bytes], result: ValidationResult) -> None:
        """Perform security validation"""
        
        if isinstance(content, bytes):
            try:
                content = content.decode('utf-8', errors='ignore')
            except:
                return  # Skip security validation for binary content
        
        # Check for malicious patterns
        for pattern_name, pattern in self.security_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                result.issues.append(ValidationIssue(
                    level=ValidationStatus.ERROR,
                    code=f"SECURITY_{pattern_name.upper()}",
                    message=f"Security threat detected: {pattern_name}",
                    suggestion="Remove or sanitize detected content"
                ))
        
        # Check for suspicious URLs
        url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+|[^\s<>"\']+\.[a-z]{2,}[^\s<>"\']*'
        urls = re.findall(url_pattern, content, re.IGNORECASE)
        
        for url in urls:
            if self._is_suspicious_url(url):
                result.issues.append(ValidationIssue(
                    level=ValidationStatus.WARNING,
                    code="SUSPICIOUS_URL",
                    message=f"Potentially suspicious URL detected: {url}"
                ))
    
    def _assess_quality(
        self, 
        content: Union[str, bytes], 
        content_type: ContentType, 
        result: ValidationResult,
        metadata: Optional[ContentMetadata] = None
    ) -> None:
        """Assess content quality and generate score"""
        
        if isinstance(content, bytes):
            content_str = content.decode('utf-8', errors='ignore')
        else:
            content_str = content
        
        quality_factors = {}
        
        # Length assessment
        content_length = len(content_str)
        optimal_ranges = self.quality_metrics.get('optimal_length', {})
        optimal_range = optimal_ranges.get(content_type.value, (100, 5000))
        
        if optimal_range[0] <= content_length <= optimal_range[1]:
            quality_factors['length'] = 1.0
        elif content_length < optimal_range[0]:
            quality_factors['length'] = content_length / optimal_range[0]
        else:
            excess_ratio = (content_length - optimal_range[1]) / optimal_range[1]
            quality_factors['length'] = max(0.5, 1.0 - excess_ratio * 0.5)
        
        # Readability assessment (for text content)
        if content_type in [ContentType.TEXT, ContentType.BLOG_POST, ContentType.NEWS_ARTICLE]:
            quality_factors['readability'] = self._assess_readability(content_str)
        
        # Structure assessment
        quality_factors['structure'] = self._assess_structure(content_str, content_type)
        
        # Uniqueness assessment
        quality_factors['uniqueness'] = self._assess_uniqueness(content_str)
        
        # Metadata completeness (if provided)
        if metadata:
            quality_factors['metadata'] = self._assess_metadata_completeness(metadata)
        
        # Calculate overall quality score
        weights = self.quality_metrics.get('weights', {})
        default_weight = 1.0 / len(quality_factors)
        
        result.quality_score = sum(
            score * weights.get(factor, default_weight) 
            for factor, score in quality_factors.items()
        )
        
        # Add quality-based recommendations
        if result.quality_score < 0.6:
            result.issues.append(ValidationIssue(
                level=ValidationStatus.WARNING,
                code="LOW_QUALITY_SCORE",
                message=f"Content quality score is low: {result.quality_score:.2f}",
                suggestion="Consider improving content structure, length, or readability"
            ))
    
    def _validate_business_rules(
        self, 
        content: Union[str, bytes], 
        content_type: ContentType, 
        result: ValidationResult,
        **kwargs
    ) -> None:
        """Validate against business rules"""
        
        rules = self.business_rules.get(content_type.value, {})
        
        # Content length rules
        if 'min_length' in rules:
            content_length = len(content)
            if content_length < rules['min_length']:
                result.issues.append(ValidationIssue(
                    level=ValidationStatus.ERROR,
                    code="MIN_LENGTH_VIOLATION",
                    message=f"Content length ({content_length}) below minimum ({rules['min_length']})"
                ))
        
        if 'max_length' in rules:
            content_length = len(content)
            if content_length > rules['max_length']:
                result.issues.append(ValidationIssue(
                    level=ValidationStatus.ERROR,
                    code="MAX_LENGTH_VIOLATION",
                    message=f"Content length ({content_length}) exceeds maximum ({rules['max_length']})"
                ))
        
        # Forbidden words/patterns
        forbidden_patterns = rules.get('forbidden_patterns', [])
        if isinstance(content, str):
            for pattern in forbidden_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    result.issues.append(ValidationIssue(
                        level=ValidationStatus.ERROR,
                        code="FORBIDDEN_CONTENT",
                        message=f"Content contains forbidden pattern: {pattern}"
                    ))
        
        # Required elements
        required_elements = rules.get('required_elements', [])
        if isinstance(content, str):
            for element in required_elements:
                if element not in content.lower():
                    result.issues.append(ValidationIssue(
                        level=ValidationStatus.WARNING,
                        code="MISSING_REQUIRED_ELEMENT",
                        message=f"Content missing required element: {element}"
                    ))
    
    def _validate_platform_compliance(
        self, 
        content: Union[str, bytes], 
        content_type: ContentType, 
        platform: str, 
        result: ValidationResult
    ) -> None:
        """Validate platform-specific compliance requirements"""
        
        platform_rules = self.platform_requirements.get(platform, {})
        if not platform_rules:
            result.issues.append(ValidationIssue(
                level=ValidationStatus.WARNING,
                code="UNKNOWN_PLATFORM",
                message=f"No compliance rules defined for platform: {platform}"
            ))
            return
        
        # Platform-specific content length limits
        length_limits = platform_rules.get('content_length', {})
        content_length = len(content)
        
        if content_type.value in length_limits:
            max_length = length_limits[content_type.value]
            if content_length > max_length:
                result.issues.append(ValidationIssue(
                    level=ValidationStatus.ERROR,
                    code="PLATFORM_LENGTH_VIOLATION",
                    message=f"Content length ({content_length}) exceeds {platform} limit ({max_length})"
                ))
        
        # Platform-specific format requirements
        format_requirements = platform_rules.get('format_requirements', {})
        if content_type.value in format_requirements:
            requirements = format_requirements[content_type.value]
            for requirement in requirements:
                if not self._check_format_requirement(content, requirement):
                    result.issues.append(ValidationIssue(
                        level=ValidationStatus.WARNING,
                        code="PLATFORM_FORMAT_ISSUE",
                        message=f"Content doesn't meet {platform} format requirement: {requirement}"
                    ))
    
    def _calculate_scores(self, result: ValidationResult) -> None:
        """Calculate various scoring metrics"""
        
        # Security score
        security_issues = [i for i in result.issues if i.code.startswith('SECURITY_')]
        result.security_score = max(0.0, 1.0 - len(security_issues) * 0.2)
        
        # Compliance score
        compliance_issues = [i for i in result.issues if 'COMPLIANCE' in i.code or 'PLATFORM' in i.code]
        result.compliance_score = max(0.0, 1.0 - len(compliance_issues) * 0.15)
        
        # Overall score (weighted average)
        weights = {'quality': 0.4, 'security': 0.3, 'compliance': 0.3}
        result.overall_score = (
            result.quality_score * weights['quality'] +
            result.security_score * weights['security'] +
            result.compliance_score * weights['compliance']
        )
    
    def _determine_final_status(self, result: ValidationResult) -> None:
        """Determine final validation status"""
        
        if result.has_errors:
            result.is_valid = False
            result.status = ValidationStatus.ERROR
            
            # Check for blocking issues
            blocking_codes = ['SECURITY_', 'DANGEROUS_SCRIPT', 'MALWARE_']
            if any(any(code in issue.code for code in blocking_codes) for issue in result.issues):
                result.status = ValidationStatus.BLOCKED
        elif result.has_warnings:
            result.status = ValidationStatus.WARNING
        else:
            result.status = ValidationStatus.VALID
    
    def _generate_recommendations(self, result: ValidationResult) -> None:
        """Generate improvement recommendations"""
        
        if result.quality_score < 0.7:
            result.recommendations.append("Consider improving content quality and structure")
        
        if result.security_score < 0.8:
            result.recommendations.append("Review and remove potential security threats")
        
        if result.compliance_score < 0.8:
            result.recommendations.append("Ensure content meets platform-specific requirements")
        
        if result.warning_count > 5:
            result.recommendations.append("Address multiple warning issues to improve content quality")
    
    # Helper methods
    
    def _generate_cache_key(
        self, 
        content: Union[str, bytes], 
        content_type: ContentType, 
        metadata: Optional[ContentMetadata]
    ) -> str:
        """Generate cache key for validation result"""
        content_hash = hashlib.md5(str(content).encode()).hexdigest()
        metadata_hash = hashlib.md5(str(metadata).encode()).hexdigest() if metadata else "none"
        return f"{content_hash}_{content_type.value}_{metadata_hash}_{self.validation_level.value}"
    
    def _get_json_depth(self, data: Any, depth: int = 0) -> int:
        """Calculate maximum JSON nesting depth"""
        if isinstance(data, dict):
            return max((self._get_json_depth(v, depth + 1) for v in data.values()), default=depth)
        elif isinstance(data, list):
            return max((self._get_json_depth(item, depth + 1) for item in data), default=depth)
        return depth
    
    def _is_suspicious_url(self, url: str) -> bool:
        """Check if URL is potentially suspicious"""
        suspicious_patterns = [
            r'bit\.ly|tinyurl|t\.co',  # URL shorteners
            r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+',  # IP addresses
            r'[a-z0-9]{20,}\.com',  # Very long domains
            r'(download|install|exe|malware)',  # Suspicious keywords
        ]
        
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in suspicious_patterns)
    
    def _assess_readability(self, content: str) -> float:
        """Assess content readability (simplified implementation)"""
        sentences = len(re.findall(r'[.!?]+', content))
        words = len(content.split())
        
        if sentences == 0 or words == 0:
            return 0.5
        
        avg_sentence_length = words / sentences
        
        # Optimal sentence length is around 15-20 words
        if 10 <= avg_sentence_length <= 25:
            return 1.0
        elif avg_sentence_length < 10:
            return 0.7
        else:
            return max(0.3, 1.0 - (avg_sentence_length - 25) * 0.02)
    
    def _assess_structure(self, content: str, content_type: ContentType) -> float:
        """Assess content structure quality"""
        structure_score = 0.5  # Base score
        
        if content_type == ContentType.HTML:
            # Check for proper heading structure
            headings = re.findall(r'<h[1-6][^>]*>', content, re.IGNORECASE)
            if headings:
                structure_score += 0.3
            
            # Check for paragraphs
            paragraphs = re.findall(r'<p[^>]*>', content, re.IGNORECASE)
            if paragraphs:
                structure_score += 0.2
        
        elif content_type in [ContentType.BLOG_POST, ContentType.NEWS_ARTICLE]:
            # Check for paragraph breaks
            paragraphs = content.count('\n\n')
            if paragraphs > 0:
                structure_score += 0.3
            
            # Check for bullet points or lists
            if re.search(r'[\*\-\+]\s|[0-9]+\.\s', content):
                structure_score += 0.2
        
        return min(1.0, structure_score)
    
    def _assess_uniqueness(self, content: str) -> float:
        """Assess content uniqueness (simplified implementation)"""
        # Count repeated phrases
        words = content.lower().split()
        if len(words) < 10:
            return 0.5
        
        trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
        unique_trigrams = len(set(trigrams))
        
        uniqueness_ratio = unique_trigrams / len(trigrams) if trigrams else 0
        return min(1.0, uniqueness_ratio * 1.2)
    
    def _assess_metadata_completeness(self, metadata: ContentMetadata) -> float:
        """Assess metadata completeness"""
        required_fields = ['title', 'description', 'language']
        optional_fields = ['author', 'keywords', 'created_at']
        
        required_score = sum(1 for field in required_fields if getattr(metadata, field))
        optional_score = sum(0.5 for field in optional_fields if getattr(metadata, field))
        
        total_possible = len(required_fields) + len(optional_fields) * 0.5
        return (required_score + optional_score) / total_possible if total_possible > 0 else 0
    
    def _validate_html_tag_balance(self, content: str, result: ValidationResult) -> None:
        """Validate HTML tag balance"""
        # Simplified tag balance check
        opening_tags = re.findall(r'<([a-z][a-z0-9]*)[^>]*>', content, re.IGNORECASE)
        closing_tags = re.findall(r'</([a-z][a-z0-9]*)>', content, re.IGNORECASE)
        
        # Filter out self-closing tags
        self_closing = {'img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 'embed'}
        opening_tags = [tag.lower() for tag in opening_tags if tag.lower() not in self_closing]
        closing_tags = [tag.lower() for tag in closing_tags]
        
        unmatched_tags = set(opening_tags) - set(closing_tags)
        if unmatched_tags:
            result.issues.append(ValidationIssue(
                level=ValidationStatus.WARNING,
                code="UNBALANCED_HTML_TAGS",
                message=f"Unmatched HTML tags detected: {', '.join(unmatched_tags)}"
            ))
    
    def _validate_social_post(self, content: str, result: ValidationResult) -> None:
        """Validate social media post content"""
        # Check for hashtags
        hashtags = re.findall(r'#\w+', content)
        if len(hashtags) > 10:
            result.issues.append(ValidationIssue(
                level=ValidationStatus.WARNING,
                code="EXCESSIVE_HASHTAGS",
                message=f"Too many hashtags ({len(hashtags)}), may appear as spam"
            ))
        
        # Check for mentions
        mentions = re.findall(r'@\w+', content)
        if len(mentions) > 5:
            result.issues.append(ValidationIssue(
                level=ValidationStatus.WARNING,
                code="EXCESSIVE_MENTIONS",
                message=f"Too many mentions ({len(mentions)}), may reduce engagement"
            ))
    
    def _validate_blog_post(self, content: str, result: ValidationResult) -> None:
        """Validate blog post content"""
        # Check for title (assuming first line or H1)
        lines = content.strip().split('\n')
        if not lines or len(lines[0]) < 10:
            result.issues.append(ValidationIssue(
                level=ValidationStatus.WARNING,
                code="MISSING_TITLE",
                message="Blog post should have a clear title"
            ))
        
        # Check for reasonable length
        word_count = len(content.split())
        if word_count < 300:
            result.issues.append(ValidationIssue(
                level=ValidationStatus.WARNING,
                code="SHORT_BLOG_POST",
                message=f"Blog post is quite short ({word_count} words)"
            ))
    
    def _validate_news_article(self, content: str, result: ValidationResult) -> None:
        """Validate news article content"""
        # Check for dateline
        dateline_pattern = r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\b|\b\w+\s\d{1,2},\s\d{4}\b'
        if not re.search(dateline_pattern, content):
            result.issues.append(ValidationIssue(
                level=ValidationStatus.WARNING,
                code="MISSING_DATELINE",
                message="News article should include publication date"
            ))
        
        # Check for quotes (indicating sources)
        quotes = re.findall(r'"[^"]{10,}"', content)
        if len(quotes) < 1:
            result.issues.append(ValidationIssue(
                level=ValidationStatus.WARNING,
                code="NO_QUOTES",
                message="News article should include quotes from sources"
            ))
    
    def _validate_product_listing(self, content: str, result: ValidationResult) -> None:
        """Validate product listing content"""
        # Check for price information
        price_pattern = r'\$\d+\.?\d*|€\d+\.?\d*|£\d+\.?\d*|\d+\.?\d*\s*(USD|EUR|GBP)'
        if not re.search(price_pattern, content, re.IGNORECASE):
            result.issues.append(ValidationIssue(
                level=ValidationStatus.WARNING,
                code="MISSING_PRICE",
                message="Product listing should include price information"
            ))
        
        # Check for product specifications
        spec_keywords = ['size', 'weight', 'material', 'color', 'brand', 'model']
        found_specs = sum(1 for keyword in spec_keywords if keyword in content.lower())
        if found_specs < 2:
            result.issues.append(ValidationIssue(
                level=ValidationStatus.WARNING,
                code="INSUFFICIENT_SPECS",
                message="Product listing should include more specifications"
            ))
    
    def _validate_user_profile(self, content: str, result: ValidationResult) -> None:
        """Validate user profile content"""
        # Check for contact information
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, content):
            result.issues.append(ValidationIssue(
                level=ValidationStatus.WARNING,
                code="PUBLIC_EMAIL",
                message="Email address detected in public profile"
            ))
        
        # Check for personal information
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        if re.search(phone_pattern, content):
            result.issues.append(ValidationIssue(
                level=ValidationStatus.WARNING,
                code="PUBLIC_PHONE",
                message="Phone number detected in public profile"
            ))
    
    def _validate_media_content(self, content: bytes, content_type: ContentType, result: ValidationResult) -> None:
        """Validate media content (audio, video, image)"""
        # Basic file signature validation
        signatures = {
            ContentType.IMAGE: [
                b'\xFF\xD8\xFF',  # JPEG
                b'\x89PNG\r\n\x1a\n',  # PNG
                b'GIF87a', b'GIF89a',  # GIF
                b'RIFF',  # WebP (partial)
            ],
            ContentType.AUDIO: [
                b'ID3',  # MP3
                b'\xFF\xFB', b'\xFF\xF3', b'\xFF\xF2',  # MP3
                b'fLaC',  # FLAC
                b'OggS',  # OGG
            ],
            ContentType.VIDEO: [
                b'\x00\x00\x00\x18ftypmp4', b'\x00\x00\x00\x1Cftypmp4',  # MP4
                b'RIFF',  # AVI (partial)
                b'\x1A\x45\xDF\xA3',  # MKV
            ]
        }
        
        if content_type in signatures:
            file_signatures = signatures[content_type]
            is_valid_format = any(content.startswith(sig) for sig in file_signatures)
            
            if not is_valid_format:
                result.issues.append(ValidationIssue(
                    level=ValidationStatus.ERROR,
                    code="INVALID_FILE_FORMAT",
                    message=f"Content doesn't match expected {content_type.value} format"
                ))
    
    def _check_format_requirement(self, content: Union[str, bytes], requirement: str) -> bool:
        """Check if content meets a specific format requirement"""
        # Simplified implementation
        if requirement == 'hashtags_allowed' and isinstance(content, str):
            return '#' in content
        elif requirement == 'no_html' and isinstance(content, str):
            return '<' not in content
        elif requirement == 'max_lines_10' and isinstance(content, str):
            return len(content.split('\n')) <= 10
        
        return True  # Default to passing unknown requirements
    
    def _load_business_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load business rules configuration"""
        return {
            'text': {
                'min_length': 10,
                'max_length': 100000,
                'forbidden_patterns': [
                    r'(spam|scam|fake|fraud)',
                    r'(password|credential|login)',
                    r'(hack|crack|exploit)',
                ]
            },
            'social_post': {
                'min_length': 1,
                'max_length': 2200,  # Twitter extended
                'forbidden_patterns': [
                    r'(spam|fake|bot)',
                    r'(click here|download now)',
                ]
            },
            'blog_post': {
                'min_length': 100,
                'max_length': 50000,
                'required_elements': ['title', 'content'],
                'forbidden_patterns': [
                    r'(plagiarized|copied|stolen)',
                ]
            },
            'news_article': {
                'min_length': 200,
                'max_length': 20000,
                'required_elements': ['date', 'source'],
                'forbidden_patterns': [
                    r'(fake news|misinformation)',
                ]
            },
            'product_listing': {
                'min_length': 50,
                'max_length': 10000,
                'required_elements': ['price', 'description'],
                'forbidden_patterns': [
                    r'(counterfeit|replica|fake)',
                ]
            }
        }
    
    def _load_security_patterns(self) -> Dict[str, str]:
        """Load security threat patterns"""
        return {
            'xss_script': r'<script[^>]*>.*?</script>',
            'javascript_url': r'javascript:',
            'vbscript_url': r'vbscript:',
            'data_url': r'data:text/html',
            'event_handler': r'on\w+\s*=',
            'sql_injection': r'(union|select|insert|update|delete|drop)\s+',
            'command_injection': r'(system|exec|eval|shell_exec)\s*\(',
            'malicious_file': r'\.(exe|bat|cmd|scr|vbs|ps1)$',
            'suspicious_encoding': r'(%[0-9a-f]{2}){5,}',
            'unicode_bypass': r'\\u[0-9a-f]{4}',
        }
    
    def _load_quality_metrics(self) -> Dict[str, Any]:
        """Load quality assessment metrics"""
        return {
            'optimal_length': {
                'text': (50, 5000),
                'social_post': (10, 280),
                'blog_post': (500, 3000),
                'news_article': (300, 2000),
                'product_listing': (100, 1000),
            },
            'weights': {
                'length': 0.2,
                'readability': 0.3,
                'structure': 0.25,
                'uniqueness': 0.15,
                'metadata': 0.1,
            }
        }
    
    def _load_platform_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Load platform-specific requirements"""
        return {
            'twitter': {
                'content_length': {
                    'social_post': 280,
                    'text': 280,
                },
                'format_requirements': {
                    'social_post': ['hashtags_allowed', 'mentions_allowed'],
                }
            },
            'instagram': {
                'content_length': {
                    'social_post': 2200,
                    'text': 2200,
                },
                'format_requirements': {
                    'social_post': ['hashtags_allowed', 'mentions_allowed'],
                }
            },
            'linkedin': {
                'content_length': {
                    'social_post': 3000,
                    'text': 3000,
                },
                'format_requirements': {
                    'social_post': ['professional_tone', 'hashtags_limited'],
                }
            },
            'youtube': {
                'content_length': {
                    'text': 5000,
                    'social_post': 5000,
                },
                'format_requirements': {
                    'text': ['no_html', 'line_breaks_allowed'],
                }
            },
            'tiktok': {
                'content_length': {
                    'social_post': 150,
                    'text': 150,
                },
                'format_requirements': {
                    'social_post': ['hashtags_required', 'max_lines_10'],
                }
            }
        }
