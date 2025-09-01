"""Validation and Quality Assurance Module for AI Engines

Enterprise-grade validation, testing, and quality assurance system
for the IA-Influencer platform AI content processing engines.

🚀 Enterprise Team Project Specialties:
✅ Lead Dev + Architecte Développeur IA
✅ Développeur Backend Senior (Python/FastAPI/Django)  
✅ Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
✅ Spécialiste Sécurité Backend
✅ Architecte Microservices
✅ Développeur Audio
✅ DevOps Engineer
✅ IA Prompt Engineer

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. 
Unauthorized use, modification, or distribution by any individual or entity 
without explicit written consent from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will face legal action under international copyright law.

⚖️ LEGAL NOTICE: THEFT OF IDEAS, CONCEPTS, OR CODE WITHOUT EXPLICIT WRITTEN AUTHORIZATION  
FROM FAHED MLAIEL (mlaiel@live.de) IS STRICTLY FORBIDDEN AND WILL RESULT  
IN IMMEDIATE LEGAL PROSECUTION UNDER INTERNATIONAL COPYRIGHT LAW.

🔒 NO UNAUTHORIZED USE, COPYING, MODIFICATION, OR DISTRIBUTION ALLOWED.

Business Logic: User Upload → AI Processing → Protection → SEO → Collaboration → Distribution
"""

import asyncio
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from pathlib import Path
import tempfile
import os


class ValidationLevel(Enum):
    """
Validation strictness levels"""

    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    ENTERPRISE = "enterprise"


class TestType(Enum):
    """Types of tests performed"""

    FUNCTIONALITY = "functionality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    QUALITY = "quality"
    INTEGRATION = "integration"
    LOAD = "load"
    STRESS = "stress"
    REGRESSION = "regression"


class ValidationStatus(Enum):
    """Validation result status"""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class ValidationRule:
    """Individual validation rule definition"""
    name: str
    description: str
    validation_function: Callable
    severity: str = "error"  # error, warning, info
    enabled: bool = True
    timeout: int = 30
    retry_count: int = 0
    tags: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of a validation check"""
    rule_name: str
    status: ValidationStatus
    message: str
    execution_time: float
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class TestCase:
    """
Test case definition"""
    name: str
    description: str
    test_type: TestType
    test_function: Callable
    expected_result: Any = None
    timeout: int = 60
    prerequisites: List[str] = field(default_factory=list)
    cleanup_function: Optional[Callable] = None
    test_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    """
Result of a test execution"""
    test_name: str
    status: ValidationStatus
    message: str
    execution_time: float
    actual_result: Any = None
    expected_result: Any = None
    error_details: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class ContentValidator:
    """
    Advanced content validation system.
    
    Provides comprehensive validation for all content types
    processed by AI engines with quality, security, and compliance checks.
    """
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        self.validation_level = validation_level
        self.logger = logging.getLogger(__name__)
        
        # Validation rules registry
        self.validation_rules: Dict[str, ValidationRule] = {}
        
        # Content type validators
        self.content_validators: Dict[str, List[ValidationRule]] = {
            "audio": [],
            "video": [],
            "image": [],
            "text": [],
            "multimodal": []
        }
        
        # Initialize validation rules
        self._initialize_validation_rules()
        
    def _initialize_validation_rules(self):
        """Initialize all validation rules"""
        
        # General content validation rules
        self.add_validation_rule(ValidationRule(
            name="content_not_empty",
            description="Validate that content is not empty or null",
            validation_function=self._validate_content_not_empty,
            severity="error"
        ))
        
        self.add_validation_rule(ValidationRule(
            name="file_size_limit",
            description="Validate file size is within acceptable limits",
            validation_function=self._validate_file_size,
            severity="error"
        ))
        
        self.add_validation_rule(ValidationRule(
            name="file_format_supported",
            description="Validate file format is supported",
            validation_function=self._validate_file_format,
            severity="error"
        ))
        
        # Security validation rules
        self.add_validation_rule(ValidationRule(
            name="malware_scan",
            description="Scan content for malware and viruses",
            validation_function=self._validate_malware_scan,
            severity="error",
            tags=["security"]
        ))
        
        self.add_validation_rule(ValidationRule(
            name="content_safety",
            description="Validate content for safety and appropriateness",
            validation_function=self._validate_content_safety,
            severity="warning",
            tags=["safety"]
        ))
        
        # Quality validation rules
        self.add_validation_rule(ValidationRule(
            name="content_quality",
            description="Assess overall content quality",
            validation_function=self._validate_content_quality,
            severity="warning",
            tags=["quality"]
        ))
        
        # Text-specific validation rules
        self.add_validation_rule(ValidationRule(
            name="text_readability",
            description="Validate text readability and comprehension",
            validation_function=self._validate_text_readability,
            severity="info",
            tags=["text", "quality"]
        ))
        
        self.add_validation_rule(ValidationRule(
            name="text_plagiarism",
            description="Check for plagiarism and originality",
            validation_function=self._validate_text_plagiarism,
            severity="error",
            tags=["text", "compliance"]
        ))
        
        # Audio-specific validation rules
        self.add_validation_rule(ValidationRule(
            name="audio_quality",
            description="Validate audio quality and technical parameters",
            validation_function=self._validate_audio_quality,
            severity="warning",
            tags=["audio", "quality"]
        ))
        
        # Video-specific validation rules
        self.add_validation_rule(ValidationRule(
            name="video_quality",
            description="Validate video quality and encoding",
            validation_function=self._validate_video_quality,
            severity="warning",
            tags=["video", "quality"]
        ))
        
        # Image-specific validation rules
        self.add_validation_rule(ValidationRule(
            name="image_quality",
            description="Validate image quality and resolution",
            validation_function=self._validate_image_quality,
            severity="warning",
            tags=["image", "quality"]
        ))
        
        # Assign rules to content types
        self._assign_rules_to_content_types()
        
    def add_validation_rule(self, rule: ValidationRule):
        """Add a validation rule to the registry"""
        self.validation_rules[rule.name] = rule
        
    def _assign_rules_to_content_types(self):
        """
Assign validation rules to specific content types"""
        for rule_name, rule in self.validation_rules.items():
            # General rules apply to all content types
            if not rule.tags or "general" in rule.tags:
                for content_type in self.content_validators:
                    self.content_validators[content_type].append(rule)
            else:
                # Type-specific rules
                for tag in rule.tags:
                    if tag in self.content_validators:
                        self.content_validators[tag].append(rule)
                        
    async def validate_content(
        self,
        content: Any,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[ValidationResult]:
        """
        Validate content against all applicable rules.
        
        Args:
            content: Content to validate
            content_type: Type of content (audio, video, image, text, etc.)
            metadata: Optional metadata about the content
            
        Returns:
            List of validation results
        """
        results = []
        metadata = metadata or {}
        
        # Get applicable validation rules
        applicable_rules = self.content_validators.get(content_type, [])
        
        # Add general rules if not already included
        general_rules = [rule for rule in self.validation_rules.values() 
                        if not rule.tags or "general" in rule.tags]
        
        all_rules = list(set(applicable_rules + general_rules))
        
        # Execute validation rules
        for rule in all_rules:
            if not rule.enabled:
                results.append(ValidationResult(
                    rule_name=rule.name,
                    status=ValidationStatus.SKIPPED,
                    message=f"Rule {rule.name} is disabled",
                    execution_time=0.0
                ))
                continue
                
            start_time = time.time()
            
            try:
                # Execute validation with timeout
                result = await asyncio.wait_for(
                    self._execute_validation_rule(rule, content, content_type, metadata),
                    timeout=rule.timeout
                )
                
                execution_time = time.time() - start_time
                
                if result["passed"]:
                    status = ValidationStatus.PASSED
                    message = result.get("message", f"{rule.name} validation passed")
                else:
                    status = ValidationStatus.FAILED if rule.severity == "error" else ValidationStatus.WARNING
                    message = result.get("message", f"{rule.name} validation failed")
                    
                results.append(ValidationResult(
                    rule_name=rule.name,
                    status=status,
                    message=message,
                    execution_time=execution_time,
                    details=result.get("details", {}),
                    suggestions=result.get("suggestions", [])
                ))
                
            except asyncio.TimeoutError:
                results.append(ValidationResult(
                    rule_name=rule.name,
                    status=ValidationStatus.ERROR,
                    message=f"Validation timeout after {rule.timeout} seconds",
                    execution_time=rule.timeout
                ))
                
            except Exception as e:
                results.append(ValidationResult(
                    rule_name=rule.name,
                    status=ValidationStatus.ERROR,
                    message=f"Validation error: {str(e)}",
                    execution_time=time.time() - start_time
                ))
                
        return results
        
    async def _execute_validation_rule(
        self,
        rule: ValidationRule,
        content: Any,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single validation rule"""
        try:
            return await rule.validation_function(content, content_type, metadata)
        except Exception as e:
            return {
                "passed": False,
                "message": f"Rule execution failed: {str(e)}",
                "details": {"error": str(e)}
            }
            
    # Validation rule implementations
    
    async def _validate_content_not_empty(
        self,
        content: Any,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that content is not empty"""
        if content is None:
            return {"passed": False, "message": "Content is None"}
            
        if isinstance(content, str) and not content.strip():
            return {"passed": False, "message": "Content is empty string"}
            
        if isinstance(content, (list, dict)) and len(content) == 0:
            return {"passed": False, "message": "Content is empty collection"}
            
        if hasattr(content, 'read') and content.tell() == 0:
            return {"passed": False, "message": "Content stream is empty"}
            
        return {"passed": True, "message": "Content is not empty"}
        
    async def _validate_file_size(
        self,
        content: Any,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate file size limits"""
        size_limits = {
            "audio": 100 * 1024 * 1024,  # 100MB
            "video": 500 * 1024 * 1024,  # 500MB
            "image": 50 * 1024 * 1024,   # 50MB
            "text": 10 * 1024 * 1024,    # 10MB
        }
        
        max_size = size_limits.get(content_type, 100 * 1024 * 1024)
        
        # Get content size
        content_size = 0
        if hasattr(content, 'read'):
            # File-like object
            current_pos = content.tell()
            content.seek(0, 2)  # Seek to end
            content_size = content.tell()
            content.seek(current_pos)  # Restore position
        elif isinstance(content, (str, bytes)):
            content_size = len(content)
        elif isinstance(content, dict) and 'size' in content:
            content_size = content['size']
            
        if content_size > max_size:
            return {
                "passed": False,
                "message": f"Content size ({content_size} bytes) exceeds limit ({max_size} bytes)",
                "details": {"size": content_size, "limit": max_size}
            }
            
        return {
            "passed": True,
            "message": f"Content size ({content_size} bytes) is within limits",
            "details": {"size": content_size, "limit": max_size}
        }
        
    async def _validate_file_format(
        self,
        content: Any,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate file format is supported"""
        supported_formats = {
            "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
            "video": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
            "image": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"],
            "text": [".txt", ".md", ".html", ".pdf", ".docx"]
        }
        
        formats = supported_formats.get(content_type, [])
        
        # Get file extension from metadata or content
        file_extension = None
        if 'filename' in metadata:
            file_extension = Path(metadata['filename']).suffix.lower()
        elif 'content_type' in metadata:
            # Map MIME types to extensions (simplified)
            mime_to_ext = {
                "audio/mpeg": ".mp3",
                "audio/wav": ".wav",
                "video/mp4": ".mp4",
                "image/jpeg": ".jpg",
                "image/png": ".png",
                "text/plain": ".txt"
            }
            file_extension = mime_to_ext.get(metadata['content_type'])
            
        if not file_extension:
            return {
                "passed": False,
                "message": "Could not determine file format",
                "details": {"supported_formats": formats}
            }
            
        if file_extension not in formats:
            return {
                "passed": False,
                "message": f"Unsupported file format: {file_extension}",
                "details": {"format": file_extension, "supported_formats": formats}
            }
            
        return {
            "passed": True,
            "message": f"File format {file_extension} is supported",
            "details": {"format": file_extension}
        }
        
    async def _validate_malware_scan(
        self,
        content: Any,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Scan content for malware (simplified implementation)"""
        # In a real implementation, this would integrate with antivirus APIs
        
        # Basic checks for suspicious patterns
        suspicious_patterns = [
            b"eval(",
            b"exec(",
            b"system(",
            b"<script",
            b"javascript:",
            b"vbscript:"
        ]
        
        content_bytes = b""
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        elif isinstance(content, bytes):
            content_bytes = content
        elif hasattr(content, 'read'):
            current_pos = content.tell()
            content_bytes = content.read(1024 * 1024)  # Read first 1MB
            content.seek(current_pos)
            
        # Check for suspicious patterns
        for pattern in suspicious_patterns:
            if pattern in content_bytes:
                return {
                    "passed": False,
                    "message": f"Suspicious pattern detected: {pattern.decode('utf-8', errors='ignore')}",
                    "details": {"pattern": pattern.decode('utf-8', errors='ignore')}
                }
                
        return {
            "passed": True,
            "message": "No malware detected",
            "details": {"scanned_bytes": len(content_bytes)}
        }
        
    async def _validate_content_safety(
        self,
        content: Any,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate content safety and appropriateness"""
        # Simplified content safety check
        # In production, this would use ML models for content moderation
        
        if content_type == "text" and isinstance(content, str):
            # Check for inappropriate keywords
            inappropriate_keywords = [
                "hate", "violence", "explicit", "illegal", "harmful"
            ]
            
            content_lower = content.lower()
            found_keywords = [kw for kw in inappropriate_keywords if kw in content_lower]
            
            if found_keywords:
                return {
                    "passed": False,
                    "message": f"Potentially inappropriate content detected",
                    "details": {"keywords": found_keywords},
                    "suggestions": ["Review content for appropriateness", "Consider content moderation"]
                }
                
        return {
            "passed": True,
            "message": "Content appears safe and appropriate"
        }
        
    async def _validate_content_quality(
        self,
        content: Any,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess overall content quality"""
        quality_score = 100.0
        issues = []
        
        if content_type == "text" and isinstance(content, str):
            # Text quality checks
            word_count = len(content.split())
            if word_count < 10:
                quality_score -= 20
                issues.append("Text is very short")
            elif word_count < 50:
                quality_score -= 10
                issues.append("Text is short")
                
            # Check for spelling errors (simplified)
            if content.count("teh") > 0 or content.count("recieve") > 0:
                quality_score -= 15
                issues.append("Potential spelling errors detected")
                
        quality_level = "high" if quality_score >= 80 else "medium" if quality_score >= 60 else "low"
        
        return {
            "passed": quality_score >= 60,
            "message": f"Content quality: {quality_level} (score: {quality_score})",
            "details": {
                "quality_score": quality_score,
                "quality_level": quality_level,
                "issues": issues
            },
            "suggestions": [
                "Improve content length and detail" if quality_score < 70 else "",
                "Review for grammar and spelling" if "spelling" in str(issues) else ""
            ]
        }
        
    async def _validate_text_readability(
        self,
        content: Any,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate text readability"""
        if content_type != "text" or not isinstance(content, str):
            return {"passed": True, "message": "Not applicable to non-text content"}
            
        # Simplified readability calculation
        sentences = content.split('.')
        words = content.split()
        
        if not sentences or not words:
            return {"passed": False, "message": "Cannot calculate readability for empty text"}
            
        avg_sentence_length = len(words) / len(sentences)
        
        # Simple readability score (Flesch-inspired)
        readability_score = 206.835 - (1.015 * avg_sentence_length)
        
        if readability_score >= 60:
            level = "good"
            passed = True
        elif readability_score >= 30:
            level = "moderate"
            passed = True
        else:
            level = "difficult"
            passed = False
            
        return {
            "passed": passed,
            "message": f"Text readability: {level} (score: {readability_score:.1f})",
            "details": {
                "readability_score": readability_score,
                "avg_sentence_length": avg_sentence_length,
                "word_count": len(words),
                "sentence_count": len(sentences)
            },
            "suggestions": [
                "Consider shorter sentences for better readability" if avg_sentence_length > 20 else "",
                "Add more content for better analysis" if len(words) < 50 else ""
            ]
        }
        
    async def _validate_text_plagiarism(
        self,
        content: Any,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check for plagiarism and originality"""
        if content_type != "text" or not isinstance(content, str):
            return {"passed": True, "message": "Not applicable to non-text content"}
            
        # Simplified plagiarism check
        # In production, this would integrate with plagiarism detection APIs
        
        # Check for common copied phrases
        common_phrases = [
            "lorem ipsum dolor sit amet",
            "the quick brown fox jumps",
            "to be or not to be",
            "all rights reserved"
        ]
        
        content_lower = content.lower()
        found_phrases = [phrase for phrase in common_phrases if phrase in content_lower]
        
        if found_phrases:
            return {
                "passed": False,
                "message": "Potential plagiarism detected",
                "details": {"detected_phrases": found_phrases},
                "suggestions": ["Review content for originality", "Rewrite potentially copied sections"]
            }
            
        # Check for repetitive patterns (simple check)
        words = content.split()
        if len(set(words)) < len(words) * 0.5:  # More than 50% duplicate words
            return {
                "passed": False,
                "message": "Content appears repetitive",
                "details": {"unique_word_ratio": len(set(words)) / len(words)},
                "suggestions": ["Vary vocabulary and sentence structure"]
            }
            
        return {
            "passed": True,
            "message": "Content appears original",
            "details": {"unique_word_ratio": len(set(words)) / len(words) if words else 0}
        }
        
    async def _validate_audio_quality(
        self,
        content: Any,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate audio quality"""
        if content_type != "audio":
            return {"passed": True, "message": "Not applicable to non-audio content"}
            
        # Simplified audio quality check based on metadata
        sample_rate = metadata.get("sample_rate", 44100)
        bit_depth = metadata.get("bit_depth", 16)
        channels = metadata.get("channels", 2)
        
        quality_score = 100.0
        issues = []
        
        if sample_rate < 22050:
            quality_score -= 30
            issues.append("Low sample rate")
        elif sample_rate < 44100:
            quality_score -= 15
            issues.append("Below standard sample rate")
            
        if bit_depth < 16:
            quality_score -= 25
            issues.append("Low bit depth")
            
        if channels < 2:
            quality_score -= 10
            issues.append("Mono audio")
            
        return {
            "passed": quality_score >= 70,
            "message": f"Audio quality score: {quality_score}",
            "details": {
                "quality_score": quality_score,
                "sample_rate": sample_rate,
                "bit_depth": bit_depth,
                "channels": channels,
                "issues": issues
            }
        }
        
    async def _validate_video_quality(
        self,
        content: Any,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate video quality"""
        if content_type != "video":
            return {"passed": True, "message": "Not applicable to non-video content"}
            
        # Simplified video quality check
        resolution = metadata.get("resolution", "720p")
        frame_rate = metadata.get("frame_rate", 30)
        codec = metadata.get("codec", "h264")
        
        quality_score = 100.0
        issues = []
        
        if "480p" in resolution:
            quality_score -= 20
            issues.append("Low resolution")
        elif "720p" in resolution:
            quality_score -= 5
            
        if frame_rate < 24:
            quality_score -= 15
            issues.append("Low frame rate")
            
        if codec not in ["h264", "h265", "vp9"]:
            quality_score -= 10
            issues.append("Non-standard codec")
            
        return {
            "passed": quality_score >= 70,
            "message": f"Video quality score: {quality_score}",
            "details": {
                "quality_score": quality_score,
                "resolution": resolution,
                "frame_rate": frame_rate,
                "codec": codec,
                "issues": issues
            }
        }
        
    async def _validate_image_quality(
        self,
        content: Any,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate image quality"""
        if content_type != "image":
            return {"passed": True, "message": "Not applicable to non-image content"}
            
        # Simplified image quality check
        width = metadata.get("width", 1920)
        height = metadata.get("height", 1080)
        format = metadata.get("format", "jpeg")
        
        quality_score = 100.0
        issues = []
        
        total_pixels = width * height
        
        if total_pixels < 1000000:  # Less than 1MP
            quality_score -= 25
            issues.append("Low resolution")
        elif total_pixels < 2000000:  # Less than 2MP
            quality_score -= 10
            
        if format.lower() in ["gif", "bmp"]:
            quality_score -= 15
            issues.append("Suboptimal format")
            
        if width < 800 or height < 600:
            quality_score -= 20
            issues.append("Small dimensions")
            
        return {
            "passed": quality_score >= 70,
            "message": f"Image quality score: {quality_score}",
            "details": {
                "quality_score": quality_score,
                "width": width,
                "height": height,
                "format": format,
                "total_pixels": total_pixels,
                "issues": issues
            }
        }


class EngineTestSuite:
    """
    Comprehensive test suite for AI engines.
    
    Provides automated testing capabilities for functionality,
    performance, security, and integration testing.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_cases: Dict[str, TestCase] = {}
        self.test_results: List[TestResult] = []
        
        # Initialize test cases
        self._initialize_test_cases()
        
    def _initialize_test_cases(self):
        """
Initialize all test cases"""
        
        # Functionality tests
        self.add_test_case(TestCase(
            name="engine_initialization",
            description="Test engine initialization and configuration",
            test_type=TestType.FUNCTIONALITY,
            test_function=self._test_engine_initialization
        ))
        
        self.add_test_case(TestCase(
            name="content_processing_basic",
            description="Test basic content processing functionality",
            test_type=TestType.FUNCTIONALITY,
            test_function=self._test_content_processing_basic
        ))
        
        # Performance tests
        self.add_test_case(TestCase(
            name="processing_speed",
            description="Test content processing speed",
            test_type=TestType.PERFORMANCE,
            test_function=self._test_processing_speed,
            timeout=120
        ))
        
        self.add_test_case(TestCase(
            name="memory_usage",
            description="Test memory usage during processing",
            test_type=TestType.PERFORMANCE,
            test_function=self._test_memory_usage
        ))
        
        # Security tests
        self.add_test_case(TestCase(
            name="input_validation",
            description="Test input validation and sanitization",
            test_type=TestType.SECURITY,
            test_function=self._test_input_validation
        ))
        
        # Load tests
        self.add_test_case(TestCase(
            name="concurrent_processing",
            description="Test concurrent content processing",
            test_type=TestType.LOAD,
            test_function=self._test_concurrent_processing,
            timeout=300
        ))
        
    def add_test_case(self, test_case: TestCase):
        """Add a test case to the suite"""
        self.test_cases[test_case.name] = test_case
        
    async def run_all_tests(self, engine: Any) -> List[TestResult]:
        """
Run all test cases for an engine"""
        results = []
        
        for test_name, test_case in self.test_cases.items():
            result = await self.run_test(test_name, engine)
            results.append(result)
            
        self.test_results.extend(results)
        return results
        
    async def run_test(self, test_name: str, engine: Any) -> TestResult:
        """
Run a specific test case"""
        test_case = self.test_cases.get(test_name)
        if not test_case:
            return TestResult(
                test_name=test_name,
                status=ValidationStatus.ERROR,
                message=f"Test case {test_name} not found",
                execution_time=0.0
            )
            
        start_time = time.time()
        
        try:
            # Check prerequisites
            for prereq in test_case.prerequisites:
                if prereq not in self.test_cases:
                    return TestResult(
                        test_name=test_name,
                        status=ValidationStatus.SKIPPED,
                        message=f"Prerequisite {prereq} not available",
                        execution_time=0.0
                    )
                    
            # Execute test with timeout
            result = await asyncio.wait_for(
                test_case.test_function(engine, test_case.test_data),
                timeout=test_case.timeout
            )
            
            execution_time = time.time() - start_time
            
            # Determine test status
            if result.get("passed", False):
                status = ValidationStatus.PASSED
                message = result.get("message", "Test passed")
            else:
                status = ValidationStatus.FAILED
                message = result.get("message", "Test failed")
                
            return TestResult(
                test_name=test_name,
                status=status,
                message=message,
                execution_time=execution_time,
                actual_result=result.get("actual_result"),
                expected_result=test_case.expected_result,
                performance_metrics=result.get("performance_metrics", {})
            )
            
        except asyncio.TimeoutError:
            return TestResult(
                test_name=test_name,
                status=ValidationStatus.FAILED,
                message=f"Test timeout after {test_case.timeout} seconds",
                execution_time=test_case.timeout
            )
            
        except Exception as e:
            return TestResult(
                test_name=test_name,
                status=ValidationStatus.ERROR,
                message=f"Test error: {str(e)}",
                execution_time=time.time() - start_time,
                error_details=str(e)
            )
            
        finally:
            # Cleanup if specified
            if test_case.cleanup_function:
                try:
                    await test_case.cleanup_function(engine)
                except Exception as e:
                    self.logger.warning(f"Cleanup failed for {test_name}: {str(e)}")
                    
    # Test case implementations
    
    async def _test_engine_initialization(self, engine: Any, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test engine initialization"""
        try:
            # Check if engine has required attributes
            required_attrs = ["engine_name", "status", "metrics"]
            missing_attrs = [attr for attr in required_attrs if not hasattr(engine, attr)]
            
            if missing_attrs:
                return {
                    "passed": False,
                    "message": f"Engine missing required attributes: {missing_attrs}",
                    "actual_result": missing_attrs
                }
                
            # Check if engine is in ready state
            if hasattr(engine, 'status') and engine.status.value != "ready":
                return {
                    "passed": False,
                    "message": f"Engine not in ready state: {engine.status.value}",
                    "actual_result": engine.status.value
                }
                
            return {
                "passed": True,
                "message": "Engine initialization successful",
                "actual_result": "initialized"
            }
            
        except Exception as e:
            return {
                "passed": False,
                "message": f"Initialization test failed: {str(e)}",
                "actual_result": str(e)
            }
            
    async def _test_content_processing_basic(self, engine: Any, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test basic content processing"""
        try:
            # Simple test content
            test_content = "This is a test content for processing validation."
            
            if hasattr(engine, 'process_content'):
                result = await engine.process_content(test_content, {})
                
                if result and result.success:
                    return {
                        "passed": True,
                        "message": "Basic content processing successful",
                        "actual_result": "processed"
                    }
                else:
                    return {
                        "passed": False,
                        "message": "Content processing failed",
                        "actual_result": result.errors if result else "No result"
                    }
            else:
                return {
                    "passed": False,
                    "message": "Engine does not support process_content method",
                    "actual_result": "method_missing"
                }
                
        except Exception as e:
            return {
                "passed": False,
                "message": f"Processing test failed: {str(e)}",
                "actual_result": str(e)
            }
            
    async def _test_processing_speed(self, engine: Any, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test content processing speed"""
        try:
            test_content = "This is a test content for speed validation." * 100
            
            start_time = time.time()
            
            if hasattr(engine, 'process_content'):
                result = await engine.process_content(test_content, {})
                processing_time = time.time() - start_time
                
                # Expected processing time threshold (adjustable)
                max_expected_time = 30.0  # seconds
                
                performance_metrics = {
                    "processing_time": processing_time,
                    "content_size": len(test_content),
                    "throughput": len(test_content) / processing_time if processing_time > 0 else 0
                }
                
                if processing_time <= max_expected_time:
                    return {
                        "passed": True,
                        "message": f"Processing speed acceptable: {processing_time:.2f}s",
                        "actual_result": processing_time,
                        "performance_metrics": performance_metrics
                    }
                else:
                    return {
                        "passed": False,
                        "message": f"Processing too slow: {processing_time:.2f}s > {max_expected_time}s",
                        "actual_result": processing_time,
                        "performance_metrics": performance_metrics
                    }
            else:
                return {
                    "passed": False,
                    "message": "Engine does not support process_content method",
                    "actual_result": "method_missing"
                }
                
        except Exception as e:
            return {
                "passed": False,
                "message": f"Speed test failed: {str(e)}",
                "actual_result": str(e)
            }
            
    async def _test_memory_usage(self, engine: Any, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test memory usage during processing"""
        try:
            import psutil
            import os
            
            # Get initial memory usage
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Process large content
            large_content = "Large test content for memory validation. " * 10000
            
            if hasattr(engine, 'process_content'):
                result = await engine.process_content(large_content, {})
                
                # Get final memory usage
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = final_memory - initial_memory
                
                # Expected memory threshold
                max_memory_increase = 500  # MB
                
                performance_metrics = {
                    "initial_memory_mb": initial_memory,
                    "final_memory_mb": final_memory,
                    "memory_increase_mb": memory_increase,
                    "content_size": len(large_content)
                }
                
                if memory_increase <= max_memory_increase:
                    return {
                        "passed": True,
                        "message": f"Memory usage acceptable: +{memory_increase:.1f}MB",
                        "actual_result": memory_increase,
                        "performance_metrics": performance_metrics
                    }
                else:
                    return {
                        "passed": False,
                        "message": f"Excessive memory usage: +{memory_increase:.1f}MB > {max_memory_increase}MB",
                        "actual_result": memory_increase,
                        "performance_metrics": performance_metrics
                    }
            else:
                return {
                    "passed": False,
                    "message": "Engine does not support process_content method",
                    "actual_result": "method_missing"
                }
                
        except ImportError:
            return {
                "passed": False,
                "message": "psutil not available for memory testing",
                "actual_result": "dependency_missing"
            }
        except Exception as e:
            return {
                "passed": False,
                "message": f"Memory test failed: {str(e)}",
                "actual_result": str(e)
            }
            
    async def _test_input_validation(self, engine: Any, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test input validation and security"""
        try:
            # Test with malicious inputs
            malicious_inputs = [
                None,
                "",
                "SELECT * FROM users; DROP TABLE users;",
                "<script>alert('xss')</script>",
                "../../etc/passwd",
                "A" * 1000000,  # Very long string
                {"malicious": "payload"},
                []
            ]
            
            security_issues = []
            
            for malicious_input in malicious_inputs:
                try:
                    if hasattr(engine, 'process_content'):
                        result = await engine.process_content(malicious_input, {})
                        
                        # Check if engine properly handled malicious input
                        if result and result.success:
                            # This might be a security issue if malicious content was processed
                            if isinstance(malicious_input, str) and any(pattern in malicious_input.lower() 
                                                                       for pattern in ["script", "select", "drop"]):
                                security_issues.append(f"Processed potentially malicious input: {str(malicious_input)[:50]}")
                                
                except Exception:
                    # Exception is expected for malicious inputs
                    pass
                    
            if security_issues:
                return {
                    "passed": False,
                    "message": f"Security vulnerabilities detected: {len(security_issues)}",
                    "actual_result": security_issues
                }
            else:
                return {
                    "passed": True,
                    "message": "Input validation appears secure",
                    "actual_result": "secure"
                }
                
        except Exception as e:
            return {
                "passed": False,
                "message": f"Security test failed: {str(e)}",
                "actual_result": str(e)
            }
            
    async def _test_concurrent_processing(self, engine: Any, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test concurrent content processing"""
        try:
            test_content = "Concurrent test content for load validation."
            concurrent_requests = 10
            
            if hasattr(engine, 'process_content'):
                start_time = time.time()
                
                # Create concurrent tasks
                tasks = []
                for i in range(concurrent_requests):
                    task = engine.process_content(f"{test_content} Request {i}", {})
                    tasks.append(task)
                    
                # Wait for all tasks to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                processing_time = time.time() - start_time
                
                # Count successful results
                successful_results = sum(1 for result in results 
                                       if not isinstance(result, Exception) and result and result.success)
                
                success_rate = successful_results / concurrent_requests * 100
                
                performance_metrics = {
                    "concurrent_requests": concurrent_requests,
                    "successful_requests": successful_results,
                    "success_rate": success_rate,
                    "total_processing_time": processing_time,
                    "avg_request_time": processing_time / concurrent_requests
                }
                
                if success_rate >= 90:  # 90% success rate threshold
                    return {
                        "passed": True,
                        "message": f"Concurrent processing successful: {success_rate:.1f}% success rate",
                        "actual_result": success_rate,
                        "performance_metrics": performance_metrics
                    }
                else:
                    return {
                        "passed": False,
                        "message": f"Poor concurrent performance: {success_rate:.1f}% success rate",
                        "actual_result": success_rate,
                        "performance_metrics": performance_metrics
                    }
            else:
                return {
                    "passed": False,
                    "message": "Engine does not support process_content method",
                    "actual_result": "method_missing"
                }
                
        except Exception as e:
            return {
                "passed": False,
                "message": f"Concurrent test failed: {str(e)}",
                "actual_result": str(e)
            }
            
    def generate_test_report(self, results: List[TestResult]) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.status == ValidationStatus.PASSED)
        failed_tests = sum(1 for r in results if r.status == ValidationStatus.FAILED)
        error_tests = sum(1 for r in results if r.status == ValidationStatus.ERROR)
        skipped_tests = sum(1 for r in results if r.status == ValidationStatus.SKIPPED)
        
        total_execution_time = sum(r.execution_time for r in results)
        avg_execution_time = total_execution_time / total_tests if total_tests > 0 else 0
        
        # Group by test type
        test_types = {}
        for result in results:
            test_case = self.test_cases.get(result.test_name)
            if test_case:
                test_type = test_case.test_type.value
                if test_type not in test_types:
                    test_types[test_type] = {"total": 0, "passed": 0, "failed": 0}
                    
                test_types[test_type]["total"] += 1
                if result.status == ValidationStatus.PASSED:
                    test_types[test_type]["passed"] += 1
                elif result.status == ValidationStatus.FAILED:
                    test_types[test_type]["failed"] += 1
                    
        return {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "error_tests": error_tests,
                "skipped_tests": skipped_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_execution_time": total_execution_time,
                "avg_execution_time": avg_execution_time
            },
            "test_types": test_types,
            "detailed_results": [
                {
                    "test_name": r.test_name,
                    "status": r.status.value,
                    "message": r.message,
                    "execution_time": r.execution_time,
                    "performance_metrics": r.performance_metrics,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in results
            ],
            "report_generated": datetime.now().isoformat()
        }


# Global instances
content_validator = ContentValidator()
engine_test_suite = EngineTestSuite()


# Convenience functions
async def validate_content(content: Any, content_type: str, **kwargs) -> List[ValidationResult]:
    """Validate content using the global validator"""
    return await content_validator.validate_content(content, content_type, **kwargs)


async def run_engine_tests(engine: Any) -> List[TestResult]:
    """
Run all tests for an engine"""
    return await engine_test_suite.run_all_tests(engine)


def generate_validation_report(results: List[ValidationResult]) -> Dict[str, Any]:
    """
Generate validation report"""
    total_validations = len(results)
    passed_validations = sum(1 for r in results if r.status == ValidationStatus.PASSED)
    failed_validations = sum(1 for r in results if r.status == ValidationStatus.FAILED)
    warning_validations = sum(1 for r in results if r.status == ValidationStatus.WARNING)
    
    return {
        "summary": {
            "total_validations": total_validations,
            "passed_validations": passed_validations,
            "failed_validations": failed_validations,
            "warning_validations": warning_validations,
            "success_rate": (passed_validations / total_validations * 100) if total_validations > 0 else 0
        },
        "detailed_results": [
            {
                "rule_name": r.rule_name,
                "status": r.status.value,
                "message": r.message,
                "execution_time": r.execution_time,
                "suggestions": r.suggestions,
                "timestamp": r.timestamp.isoformat()
            }
            for r in results
        ],
        "report_generated": datetime.now().isoformat()
    }


# Export all classes and functions
__all__ = [
    "ValidationLevel",
    "TestType",
    "ValidationStatus",
    "ValidationRule",
    "ValidationResult",
    "TestCase",
    "TestResult",
    "ContentValidator",
    "EngineTestSuite",
    "content_validator",
    "engine_test_suite",
    "validate_content",
    "run_engine_tests",
    "generate_validation_report"
]
