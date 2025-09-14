"""
✅ FORMAT VALIDATION ENGINE - ENTERPRISE ARCHITECTURE
=====================================================

Comprehensive format validation and integrity checking for Ainflue Platform
Enterprise-grade validation with security compliance and quality assurance

**Expert Implementation:**
- Security Engineer: Security validation and threat detection
- Backend Senior: High-performance validation pipeline
- Database Administrator: Validation rule optimization
- ML Engineer: AI-powered content validation

**Features:** Multi-layer validation, Security compliance, Integrity checking
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Tuple, Any, Set
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import hashlib
import struct
import time
import mimetypes
import re

# Validation libraries
try:
    import magic
    from PIL import Image, ImageFile
    import cv2
    import librosa
    import mutagen
    import ffmpeg
    import numpy as np
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
except ImportError as e:
    logging.warning(f"Validation dependencies not available: {e}")

from .format_detection import AIFormatDetector, MediaType

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Validation thoroughness levels"""
    BASIC = "basic"           # Quick format and structure checks
    STANDARD = "standard"     # Standard validation with content checks
    STRICT = "strict"         # Comprehensive validation with security
    ENTERPRISE = "enterprise" # Full enterprise compliance validation

class ValidationResult(Enum):
    """Validation result status"""
    VALID = "valid"
    WARNING = "warning"
    INVALID = "invalid"
    ERROR = "error"

@dataclass
class ValidationIssue:
    """Individual validation issue"""
    level: str  # 'error', 'warning', 'info'
    code: str
    message: str
    details: Dict[str, Any]
    fix_suggestion: Optional[str] = None

@dataclass
class FormatValidationReport:
    """Comprehensive validation report"""
    file_path: str
    validation_level: ValidationLevel
    overall_result: ValidationResult
    confidence_score: float
    issues: List[ValidationIssue]
    metadata: Dict[str, Any]
    security_checks: Dict[str, bool]
    performance_metrics: Dict[str, Any]
    recommendations: List[str]
    processing_time: float

class IntegrityChecker:
    """File integrity and corruption detection"""
    
    def __init__(self) -> None:
        self.chunk_size = 8192
        self.max_scan_size = 100 * 1024 * 1024  # 100MB max scan
    
    async def check_file_integrity(self, file_path: Path) -> Dict[str, Any]:
        """Comprehensive file integrity check"""
        integrity_report = {
            'file_accessible': False,
            'file_readable': False,
            'size_valid': False,
            'checksum': None,
            'corruption_detected': False,
            'header_valid': False,
            'footer_valid': False,
            'structure_valid': False
        }
        
        try:
            # Basic accessibility check
            if not file_path.exists():
                return integrity_report
            
            integrity_report['file_accessible'] = True
            
            # Readability check
            try:
                with open(file_path, 'rb') as f:
                    f.read(1)  # Try to read first byte
                integrity_report['file_readable'] = True
            except:
                return integrity_report
            
            # Size validation
            file_size = file_path.stat().st_size
            if file_size > 0:
                integrity_report['size_valid'] = True
            
            # Calculate file checksum
            integrity_report['checksum'] = await self._calculate_checksum(file_path)
            
            # Check for corruption patterns
            corruption_detected = await self._detect_corruption_patterns(file_path)
            integrity_report['corruption_detected'] = corruption_detected
            
            # Validate file structure
            structure_checks = await self._validate_file_structure(file_path)
            integrity_report.update(structure_checks)
            
        except Exception as e:
            logger.error(f"Integrity check failed: {e}")
        
        return integrity_report
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(self.chunk_size), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.warning(f"Checksum calculation failed: {e}")
            return ""
    
    async def _detect_corruption_patterns(self, file_path: Path) -> bool:
        """Detect common corruption patterns"""
        try:
            file_size = file_path.stat().st_size
            scan_size = min(file_size, self.max_scan_size)
            
            with open(file_path, 'rb') as f:
                # Check beginning
                header = f.read(min(1024, scan_size))
                
                # Check for excessive null bytes (corruption indicator)
                null_ratio = header.count(0) / len(header) if header else 0
                if null_ratio > 0.8:  # More than 80% null bytes
                    return True
                
                # Check for excessive repeated patterns
                if len(set(header)) < 5:  # Very few unique bytes
                    return True
                
                # Check end of file if large enough
                if file_size > 2048:
                    f.seek(-1024, 2)  # Seek to last 1KB
                    footer = f.read(1024)
                    
                    # Similar checks for footer
                    if len(set(footer)) < 5:
                        return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Corruption detection failed: {e}")
            return False
    
    async def _validate_file_structure(self, file_path: Path) -> Dict[str, bool]:
        """Validate file structure based on format"""
        structure_checks = {
            'header_valid': False,
            'footer_valid': False,
            'structure_valid': False
        }
        
        try:
            # Detect format first
            detector = AIFormatDetector()
            analysis = await detector.detect_format(file_path)
            
            media_type = analysis.primary_result.media_type
            format_name = analysis.primary_result.format_name
            
            # Perform format-specific structure validation
            if media_type == MediaType.IMAGE:
                structure_checks = await self._validate_image_structure(file_path, format_name)
            elif media_type == MediaType.AUDIO:
                structure_checks = await self._validate_audio_structure(file_path, format_name)
            elif media_type == MediaType.VIDEO:
                structure_checks = await self._validate_video_structure(file_path, format_name)
            
        except Exception as e:
            logger.warning(f"Structure validation failed: {e}")
        
        return structure_checks
    
    async def _validate_image_structure(self, file_path: Path, format_name: str) -> Dict[str, bool]:
        """Validate image file structure"""
        checks = {'header_valid': False, 'footer_valid': False, 'structure_valid': False}
        
        try:
            # Use PIL to validate image structure
            with Image.open(file_path) as img:
                # If we can open it, structure is likely valid
                img.verify()  # This will raise exception if corrupted
                checks['structure_valid'] = True
                checks['header_valid'] = True
                checks['footer_valid'] = True
                
        except Exception as e:
            logger.debug(f"Image structure validation failed: {e}")
        
        return checks
    
    async def _validate_audio_structure(self, file_path: Path, format_name: str) -> Dict[str, bool]:
        """Validate audio file structure"""
        checks = {'header_valid': False, 'footer_valid': False, 'structure_valid': False}
        
        try:
            # Use mutagen to validate audio structure
            audio_file = mutagen.File(str(file_path))
            if audio_file is not None:
                checks['structure_valid'] = True
                checks['header_valid'] = True
                
                # Try to load with librosa for deeper validation
                y, sr = librosa.load(str(file_path), duration=1.0)
                if len(y) > 0 and sr > 0:
                    checks['footer_valid'] = True
                    
        except Exception as e:
            logger.debug(f"Audio structure validation failed: {e}")
        
        return checks
    
    async def _validate_video_structure(self, file_path: Path, format_name: str) -> Dict[str, bool]:
        """Validate video file structure"""
        checks = {'header_valid': False, 'footer_valid': False, 'structure_valid': False}
        
        try:
            # Use ffprobe to validate video structure
            probe = ffmpeg.probe(str(file_path))
            
            if probe and 'streams' in probe:
                # Check for valid video stream
                video_streams = [s for s in probe['streams'] if s['codec_type'] == 'video']
                if video_streams:
                    checks['header_valid'] = True
                    checks['structure_valid'] = True
                    
                    # Check if we can read the duration (indicates complete file)
                    if 'duration' in probe.get('format', {}):
                        checks['footer_valid'] = True
                        
        except Exception as e:
            logger.debug(f"Video structure validation failed: {e}")
        
        return checks

class SecurityValidator:
    """Security validation for multimedia files"""
    
    def __init__(self) -> None:
        self.max_file_size = 10 * 1024 * 1024 * 1024  # 10GB
        self.blocked_extensions = {'.exe', '.bat', '.cmd', '.scr', '.com', '.pif'}
        self.suspicious_patterns = [
            b'<script',
            b'javascript:',
            b'vbscript:',
            b'onload=',
            b'onerror=',
            b'eval(',
            b'document.cookie'
        ]
    
    async def validate_security(self, file_path: Path, 
                              validation_level: ValidationLevel) -> Dict[str, Any]:
        """Comprehensive security validation"""
        security_report = {
            'file_size_safe': False,
            'extension_safe': False,
            'content_safe': False,
            'no_executables': False,
            'no_scripts': False,
            'metadata_safe': False,
            'threat_score': 0.0,
            'security_issues': []
        }
        
        try:
            # File size check
            file_size = file_path.stat().st_size
            if file_size <= self.max_file_size:
                security_report['file_size_safe'] = True
            else:
                security_report['security_issues'].append(f"File size {file_size} exceeds limit")
            
            # Extension check
            extension = file_path.suffix.lower()
            if extension not in self.blocked_extensions:
                security_report['extension_safe'] = True
            else:
                security_report['security_issues'].append(f"Blocked extension: {extension}")
            
            # Content scanning
            content_checks = await self._scan_file_content(file_path, validation_level)
            security_report.update(content_checks)
            
            # Metadata security check
            metadata_safe = await self._validate_metadata_security(file_path)
            security_report['metadata_safe'] = metadata_safe
            
            # Calculate threat score
            security_report['threat_score'] = self._calculate_threat_score(security_report)
            
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            security_report['security_issues'].append(f"Security validation error: {e}")
        
        return security_report
    
    async def _scan_file_content(self, file_path: Path, 
                               validation_level: ValidationLevel) -> Dict[str, Any]:
        """Scan file content for security threats"""
        content_checks = {
            'content_safe': True,
            'no_executables': True,
            'no_scripts': True
        }
        
        try:
            scan_size = 1024 * 1024  # 1MB scan for basic/standard
            if validation_level in [ValidationLevel.STRICT, ValidationLevel.ENTERPRISE]:
                scan_size = 10 * 1024 * 1024  # 10MB scan for strict/enterprise
            
            with open(file_path, 'rb') as f:
                content = f.read(scan_size)
            
            # Check for executable signatures
            executable_signatures = [
                b'MZ',  # Windows PE
                b'\x7fELF',  # Linux ELF
                b'\xfe\xed\xfa\xde',  # macOS Mach-O
                b'\xfe\xed\xfa\xce',  # macOS Mach-O
            ]
            
            for sig in executable_signatures:
                if sig in content:
                    content_checks['no_executables'] = False
                    content_checks['content_safe'] = False
                    break
            
            # Check for script patterns
            for pattern in self.suspicious_patterns:
                if pattern in content.lower():
                    content_checks['no_scripts'] = False
                    content_checks['content_safe'] = False
                    break
            
            # Check for embedded files (basic check)
            if b'PK\x03\x04' in content:  # ZIP signature
                # Could be embedded archive - needs deeper inspection
                if validation_level == ValidationLevel.ENTERPRISE:
                    content_checks['content_safe'] = False
            
        except Exception as e:
            logger.warning(f"Content scanning failed: {e}")
        
        return content_checks
    
    async def _validate_metadata_security(self, file_path: Path) -> bool:
        """Validate metadata for security issues"""
        try:
            # Check EXIF data for images
            if file_path.suffix.lower() in ['.jpg', '.jpeg', '.tiff']:
                with Image.open(file_path) as img:
                    exif = img._getexif()
                    if exif:
                        # Check for suspicious EXIF entries
                        for tag_id, value in exif.items():
                            if isinstance(value, str):
                                # Check for script patterns in EXIF
                                if any(pattern.decode() in value.lower() 
                                      for pattern in self.suspicious_patterns 
                                      if isinstance(pattern, bytes)):
                                    return False
            
            # Check audio metadata
            if file_path.suffix.lower() in ['.mp3', '.flac', '.ogg', '.m4a']:
                audio_file = mutagen.File(str(file_path))
                if audio_file:
                    for tag, value in audio_file.items():
                        if isinstance(value, (str, list)):
                            value_str = str(value).lower()
                            if any(pattern.decode() in value_str 
                                  for pattern in self.suspicious_patterns 
                                  if isinstance(pattern, bytes)):
                                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Metadata security validation failed: {e}")
            return True  # Default to safe if check fails
    
    def _calculate_threat_score(self, security_report: Dict[str, Any]) -> float:
        """Calculate overall threat score (0.0 = safe, 1.0 = high threat)"""
        threat_score = 0.0
        
        # Weight different security factors
        if not security_report['file_size_safe']:
            threat_score += 0.1
        
        if not security_report['extension_safe']:
            threat_score += 0.3
        
        if not security_report['content_safe']:
            threat_score += 0.4
        
        if not security_report['no_executables']:
            threat_score += 0.5
        
        if not security_report['no_scripts']:
            threat_score += 0.3
        
        if not security_report['metadata_safe']:
            threat_score += 0.2
        
        return min(threat_score, 1.0)

class FormatValidator:
    """Main format validation engine"""
    
    def __init__(self) -> None:
        self.format_detector = AIFormatDetector()
        self.integrity_checker = IntegrityChecker()
        self.security_validator = SecurityValidator()
        
        # Validation rules
        self.format_rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load format-specific validation rules"""
        return {
            'image': {
                'max_resolution': (50000, 50000),
                'min_resolution': (1, 1),
                'max_file_size': 100 * 1024 * 1024,  # 100MB
                'allowed_formats': ['jpeg', 'png', 'webp', 'gif', 'bmp', 'tiff', 'avif', 'heif'],
                'required_checks': ['format', 'structure', 'security']
            },
            'audio': {
                'max_duration': 7200,  # 2 hours
                'min_duration': 0.1,   # 0.1 seconds
                'max_file_size': 500 * 1024 * 1024,  # 500MB
                'allowed_formats': ['mp3', 'flac', 'wav', 'aac', 'ogg', 'opus', 'm4a'],
                'sample_rate_range': (8000, 192000),
                'required_checks': ['format', 'structure', 'audio_content']
            },
            'video': {
                'max_duration': 14400,  # 4 hours
                'min_duration': 0.1,    # 0.1 seconds
                'max_file_size': 5 * 1024 * 1024 * 1024,  # 5GB
                'max_resolution': (7680, 4320),  # 8K
                'allowed_formats': ['mp4', 'webm', 'mov', 'avi', 'mkv', 'flv'],
                'required_checks': ['format', 'structure', 'video_content', 'streaming']
            }
        }
    
    async def validate(self, file_path: Union[str, Path], 
                      validation_level: ValidationLevel = ValidationLevel.STANDARD) -> FormatValidationReport:
        """Main validation method"""
        start_time = time.time()
        file_path = Path(file_path)
        
        # Initialize report
        report = FormatValidationReport(
            file_path=str(file_path),
            validation_level=validation_level,
            overall_result=ValidationResult.VALID,
            confidence_score=0.0,
            issues=[],
            metadata={},
            security_checks={},
            performance_metrics={},
            recommendations=[],
            processing_time=0.0
        )
        
        try:
            # Step 1: Basic file checks
            basic_checks = await self._perform_basic_checks(file_path)
            if not basic_checks['passed']:
                report.overall_result = ValidationResult.INVALID
                report.issues.extend(basic_checks['issues'])
                return report
            
            # Step 2: Format detection and validation
            format_checks = await self._perform_format_checks(file_path, validation_level)
            report.issues.extend(format_checks['issues'])
            report.metadata.update(format_checks['metadata'])
            
            # Step 3: Integrity checks
            if validation_level in [ValidationLevel.STANDARD, ValidationLevel.STRICT, ValidationLevel.ENTERPRISE]:
                integrity_checks = await self._perform_integrity_checks(file_path)
                report.issues.extend(integrity_checks['issues'])
                report.metadata['integrity'] = integrity_checks['results']
            
            # Step 4: Security validation
            if validation_level in [ValidationLevel.STRICT, ValidationLevel.ENTERPRISE]:
                security_checks = await self._perform_security_checks(file_path, validation_level)
                report.security_checks = security_checks['results']
                report.issues.extend(security_checks['issues'])
            
            # Step 5: Content-specific validation
            content_checks = await self._perform_content_checks(file_path, validation_level)
            report.issues.extend(content_checks['issues'])
            report.metadata.update(content_checks['metadata'])
            
            # Step 6: Generate recommendations
            report.recommendations = await self._generate_recommendations(file_path, report.issues)
            
            # Step 7: Calculate final results
            report.overall_result = self._determine_overall_result(report.issues)
            report.confidence_score = self._calculate_confidence_score(report.issues, validation_level)
            
            # Performance metrics
            processing_time = time.time() - start_time
            report.processing_time = processing_time
            report.performance_metrics = {
                'validation_time': processing_time,
                'checks_performed': len([c for c in [basic_checks, format_checks, 
                                                   integrity_checks if validation_level != ValidationLevel.BASIC else None,
                                                   security_checks if validation_level in [ValidationLevel.STRICT, ValidationLevel.ENTERPRISE] else None,
                                                   content_checks] if c]),
                'issues_found': len(report.issues)
            }
            
        except Exception as e:
            logger.error(f"Validation failed for {file_path}: {e}")
            report.overall_result = ValidationResult.ERROR
            report.issues.append(ValidationIssue(
                level='error',
                code='VALIDATION_ERROR',
                message=f"Validation process failed: {e}",
                details={'exception': str(e)}
            ))
        
        return report
    
    async def _perform_basic_checks(self, file_path: Path) -> Dict[str, Any]:
        """Perform basic file existence and accessibility checks"""
        checks = {'passed': True, 'issues': []}
        
        # File existence
        if not file_path.exists():
            checks['passed'] = False
            checks['issues'].append(ValidationIssue(
                level='error',
                code='FILE_NOT_FOUND',
                message='File does not exist',
                details={'path': str(file_path)}
            ))
            return checks
        
        # File readability
        try:
            with open(file_path, 'rb') as f:
                f.read(1)
        except Exception as e:
            checks['passed'] = False
            checks['issues'].append(ValidationIssue(
                level='error',
                code='FILE_NOT_READABLE',
                message='File cannot be read',
                details={'error': str(e)}
            ))
            return checks
        
        # File size check
        file_size = file_path.stat().st_size
        if file_size == 0:
            checks['passed'] = False
            checks['issues'].append(ValidationIssue(
                level='error',
                code='EMPTY_FILE',
                message='File is empty',
                details={'size': file_size}
            ))
        
        return checks
    
    async def _perform_format_checks(self, file_path: Path, 
                                   validation_level: ValidationLevel) -> Dict[str, Any]:
        """Perform format detection and validation"""
        checks = {'issues': [], 'metadata': {}}
        
        try:
            # Detect format
            analysis = await self.format_detector.detect_format(file_path)
            checks['metadata']['format_analysis'] = analysis
            
            # Validate detected format
            media_type = analysis.primary_result.media_type.value
            format_name = analysis.primary_result.format_name
            
            # Check if format is allowed
            format_rules = self.format_rules.get(media_type, {})
            allowed_formats = format_rules.get('allowed_formats', [])
            
            if allowed_formats and format_name not in allowed_formats:
                checks['issues'].append(ValidationIssue(
                    level='warning',
                    code='FORMAT_NOT_PREFERRED',
                    message=f'Format {format_name} is not in preferred list',
                    details={'detected_format': format_name, 'allowed_formats': allowed_formats}
                ))
            
            # Check detection confidence
            if analysis.consensus_confidence < 0.7:
                checks['issues'].append(ValidationIssue(
                    level='warning',
                    code='LOW_DETECTION_CONFIDENCE',
                    message='Format detection confidence is low',
                    details={'confidence': analysis.consensus_confidence}
                ))
            
        except Exception as e:
            checks['issues'].append(ValidationIssue(
                level='error',
                code='FORMAT_DETECTION_FAILED',
                message='Format detection failed',
                details={'error': str(e)}
            ))
        
        return checks
    
    async def _perform_integrity_checks(self, file_path: Path) -> Dict[str, Any]:
        """Perform file integrity checks"""
        checks = {'issues': [], 'results': {}}
        
        try:
            integrity_report = await self.integrity_checker.check_file_integrity(file_path)
            checks['results'] = integrity_report
            
            # Check integrity results
            if not integrity_report['file_readable']:
                checks['issues'].append(ValidationIssue(
                    level='error',
                    code='FILE_CORRUPTED',
                    message='File appears to be corrupted or unreadable',
                    details=integrity_report
                ))
            
            if integrity_report['corruption_detected']:
                checks['issues'].append(ValidationIssue(
                    level='error',
                    code='CORRUPTION_DETECTED',
                    message='File corruption patterns detected',
                    details=integrity_report
                ))
            
            if not integrity_report['structure_valid']:
                checks['issues'].append(ValidationIssue(
                    level='warning',
                    code='INVALID_STRUCTURE',
                    message='File structure validation failed',
                    details=integrity_report
                ))
            
        except Exception as e:
            checks['issues'].append(ValidationIssue(
                level='error',
                code='INTEGRITY_CHECK_FAILED',
                message='Integrity check failed',
                details={'error': str(e)}
            ))
        
        return checks
    
    async def _perform_security_checks(self, file_path: Path, 
                                     validation_level: ValidationLevel) -> Dict[str, Any]:
        """Perform security validation"""
        checks = {'issues': [], 'results': {}}
        
        try:
            security_report = await self.security_validator.validate_security(file_path, validation_level)
            checks['results'] = security_report
            
            # Check security results
            if security_report['threat_score'] > 0.7:
                checks['issues'].append(ValidationIssue(
                    level='error',
                    code='HIGH_THREAT_SCORE',
                    message='File has high security threat score',
                    details={'threat_score': security_report['threat_score']}
                ))
            elif security_report['threat_score'] > 0.3:
                checks['issues'].append(ValidationIssue(
                    level='warning',
                    code='MODERATE_THREAT_SCORE',
                    message='File has moderate security concerns',
                    details={'threat_score': security_report['threat_score']}
                ))
            
            # Add specific security issues
            for issue in security_report['security_issues']:
                checks['issues'].append(ValidationIssue(
                    level='warning',
                    code='SECURITY_ISSUE',
                    message=issue,
                    details=security_report
                ))
            
        except Exception as e:
            checks['issues'].append(ValidationIssue(
                level='error',
                code='SECURITY_CHECK_FAILED',
                message='Security validation failed',
                details={'error': str(e)}
            ))
        
        return checks
    
    async def _perform_content_checks(self, file_path: Path, 
                                    validation_level: ValidationLevel) -> Dict[str, Any]:
        """Perform content-specific validation"""
        checks = {'issues': [], 'metadata': {}}
        
        try:
            # Get detailed format info
            detailed_info = await self.format_detector.get_detailed_format_info(file_path)
            checks['metadata']['detailed_format_info'] = detailed_info
            
            # Perform format-specific checks based on detected type
            analysis = await self.format_detector.detect_format(file_path)
            media_type = analysis.primary_result.media_type.value
            
            if media_type == 'image':
                image_checks = await self._validate_image_content(detailed_info)
                checks['issues'].extend(image_checks)
            elif media_type == 'audio':
                audio_checks = await self._validate_audio_content(detailed_info)
                checks['issues'].extend(audio_checks)
            elif media_type == 'video':
                video_checks = await self._validate_video_content(detailed_info)
                checks['issues'].extend(video_checks)
            
        except Exception as e:
            checks['issues'].append(ValidationIssue(
                level='warning',
                code='CONTENT_CHECK_FAILED',
                message='Content validation failed',
                details={'error': str(e)}
            ))
        
        return checks
    
    async def _validate_image_content(self, image_info: Any) -> List[ValidationIssue]:
        """Validate image-specific content"""
        issues = []
        
        try:
            # Check resolution limits
            if hasattr(image_info, 'resolution'):
                width, height = image_info.resolution
                max_width, max_height = self.format_rules['image']['max_resolution']
                
                if width > max_width or height > max_height:
                    issues.append(ValidationIssue(
                        level='warning',
                        code='RESOLUTION_TOO_HIGH',
                        message=f'Image resolution {width}x{height} exceeds maximum {max_width}x{max_height}',
                        details={'resolution': (width, height), 'max_resolution': (max_width, max_height)},
                        fix_suggestion='Consider resizing the image'
                    ))
            
            # Check file size
            if hasattr(image_info, 'file_size'):
                max_size = self.format_rules['image']['max_file_size']
                if image_info.file_size > max_size:
                    issues.append(ValidationIssue(
                        level='warning',
                        code='FILE_SIZE_TOO_LARGE',
                        message=f'File size {image_info.file_size} exceeds maximum {max_size}',
                        details={'file_size': image_info.file_size, 'max_size': max_size},
                        fix_suggestion='Consider compressing the image'
                    ))
            
        except Exception as e:
            issues.append(ValidationIssue(
                level='warning',
                code='IMAGE_VALIDATION_ERROR',
                message='Image content validation failed',
                details={'error': str(e)}
            ))
        
        return issues
    
    async def _validate_audio_content(self, audio_info: Any) -> List[ValidationIssue]:
        """Validate audio-specific content"""
        issues = []
        
        try:
            # Check duration limits
            if hasattr(audio_info, 'duration'):
                max_duration = self.format_rules['audio']['max_duration']
                min_duration = self.format_rules['audio']['min_duration']
                
                if audio_info.duration > max_duration:
                    issues.append(ValidationIssue(
                        level='warning',
                        code='DURATION_TOO_LONG',
                        message=f'Audio duration {audio_info.duration}s exceeds maximum {max_duration}s',
                        details={'duration': audio_info.duration, 'max_duration': max_duration}
                    ))
                elif audio_info.duration < min_duration:
                    issues.append(ValidationIssue(
                        level='warning',
                        code='DURATION_TOO_SHORT',
                        message=f'Audio duration {audio_info.duration}s is below minimum {min_duration}s',
                        details={'duration': audio_info.duration, 'min_duration': min_duration}
                    ))
            
            # Check sample rate
            if hasattr(audio_info, 'sample_rate'):
                min_sr, max_sr = self.format_rules['audio']['sample_rate_range']
                if not (min_sr <= audio_info.sample_rate <= max_sr):
                    issues.append(ValidationIssue(
                        level='warning',
                        code='SAMPLE_RATE_OUT_OF_RANGE',
                        message=f'Sample rate {audio_info.sample_rate} is outside recommended range {min_sr}-{max_sr}',
                        details={'sample_rate': audio_info.sample_rate, 'range': (min_sr, max_sr)}
                    ))
            
        except Exception as e:
            issues.append(ValidationIssue(
                level='warning',
                code='AUDIO_VALIDATION_ERROR',
                message='Audio content validation failed',
                details={'error': str(e)}
            ))
        
        return issues
    
    async def _validate_video_content(self, video_info: Any) -> List[ValidationIssue]:
        """Validate video-specific content"""
        issues = []
        
        try:
            # Check duration limits
            if hasattr(video_info, 'duration'):
                max_duration = self.format_rules['video']['max_duration']
                min_duration = self.format_rules['video']['min_duration']
                
                if video_info.duration > max_duration:
                    issues.append(ValidationIssue(
                        level='warning',
                        code='DURATION_TOO_LONG',
                        message=f'Video duration {video_info.duration}s exceeds maximum {max_duration}s',
                        details={'duration': video_info.duration, 'max_duration': max_duration}
                    ))
                elif video_info.duration < min_duration:
                    issues.append(ValidationIssue(
                        level='warning',
                        code='DURATION_TOO_SHORT',
                        message=f'Video duration {video_info.duration}s is below minimum {min_duration}s',
                        details={'duration': video_info.duration, 'min_duration': min_duration}
                    ))
            
            # Check resolution limits
            if hasattr(video_info, 'resolution'):
                width, height = video_info.resolution
                max_width, max_height = self.format_rules['video']['max_resolution']
                
                if width > max_width or height > max_height:
                    issues.append(ValidationIssue(
                        level='warning',
                        code='RESOLUTION_TOO_HIGH',
                        message=f'Video resolution {width}x{height} exceeds maximum {max_width}x{max_height}',
                        details={'resolution': (width, height), 'max_resolution': (max_width, max_height)}
                    ))
            
        except Exception as e:
            issues.append(ValidationIssue(
                level='warning',
                code='VIDEO_VALIDATION_ERROR',
                message='Video content validation failed',
                details={'error': str(e)}
            ))
        
        return issues
    
    async def _generate_recommendations(self, file_path: Path, 
                                      issues: List[ValidationIssue]) -> List[str]:
        """Generate optimization recommendations based on validation issues"""
        recommendations = []
        
        # Analyze issues and generate recommendations
        error_codes = [issue.code for issue in issues]
        
        if 'RESOLUTION_TOO_HIGH' in error_codes:
            recommendations.append("Consider resizing image/video to reduce file size and improve compatibility")
        
        if 'FILE_SIZE_TOO_LARGE' in error_codes:
            recommendations.append("Compress the file to reduce size while maintaining acceptable quality")
        
        if 'FORMAT_NOT_PREFERRED' in error_codes:
            recommendations.append("Convert to a more widely supported format for better compatibility")
        
        if 'DURATION_TOO_LONG' in error_codes:
            recommendations.append("Consider splitting long content into shorter segments")
        
        if 'LOW_DETECTION_CONFIDENCE' in error_codes:
            recommendations.append("File format may be corrupted or non-standard - consider re-encoding")
        
        if any('SECURITY' in code for code in error_codes):
            recommendations.append("Review file for security issues and consider re-encoding from trusted source")
        
        return recommendations
    
    def _determine_overall_result(self, issues: List[ValidationIssue]) -> ValidationResult:
        """Determine overall validation result"""
        if not issues:
            return ValidationResult.VALID
        
        error_count = sum(1 for issue in issues if issue.level == 'error')
        warning_count = sum(1 for issue in issues if issue.level == 'warning')
        
        if error_count > 0:
            return ValidationResult.INVALID
        elif warning_count > 0:
            return ValidationResult.WARNING
        else:
            return ValidationResult.VALID
    
    def _calculate_confidence_score(self, issues: List[ValidationIssue], 
                                  validation_level: ValidationLevel) -> float:
        """Calculate validation confidence score"""
        base_score = 1.0
        
        # Reduce score based on issues
        for issue in issues:
            if issue.level == 'error':
                base_score -= 0.3
            elif issue.level == 'warning':
                base_score -= 0.1
        
        # Adjust based on validation level
        level_multiplier = {
            ValidationLevel.BASIC: 0.7,
            ValidationLevel.STANDARD: 0.8,
            ValidationLevel.STRICT: 0.9,
            ValidationLevel.ENTERPRISE: 1.0
        }
        
        confidence = base_score * level_multiplier.get(validation_level, 0.8)
        return max(0.0, min(1.0, confidence))

# Module exports for enterprise integration
__all__ = [
    'FormatValidator',
    'IntegrityChecker',
    'SecurityValidator',
    'ValidationLevel',
    'ValidationResult',
    'ValidationIssue',
    'FormatValidationReport'
]