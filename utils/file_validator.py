"""
File Validation Utilities - Enterprise File Security and Validation System
=========================================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive file validation utilities supporting:
- Security-focused file validation
- Malware and virus scanning simulation
- File format verification and integrity checking
- Content-based validation
- Performance optimization for large files

Expert Roles Covered:
- Security Expert: File security validation and threat detection
- Backend Senior: File format validation and processing
- DevOps Expert: Performance monitoring and system integration
"""

import os
import hashlib
import mimetypes
import asyncio
import aiofiles
import struct
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Set, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import json
import tempfile

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """File validation levels"""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    PARANOID = "paranoid"


class ThreatLevel(Enum):
    """File threat levels"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationResult(Enum):
    """Validation result types"""
    VALID = "valid"
    INVALID = "invalid"
    SUSPICIOUS = "suspicious"
    BLOCKED = "blocked"


@dataclass
class FileValidationRule:
    """File validation rule definition"""
    name: str
    description: str
    enabled: bool = True
    critical: bool = False
    max_file_size: Optional[int] = None
    allowed_extensions: Optional[Set[str]] = None
    blocked_extensions: Optional[Set[str]] = None
    allowed_mime_types: Optional[Set[str]] = None
    blocked_mime_types: Optional[Set[str]] = None
    content_patterns: Optional[List[str]] = None
    header_signatures: Optional[Dict[str, bytes]] = None


@dataclass
class ValidationIssue:
    """File validation issue"""
    rule_name: str
    severity: ThreatLevel
    message: str
    details: Optional[Dict[str, Any]] = None
    recommendation: Optional[str] = None


@dataclass
class FileValidationReport:
    """Comprehensive file validation report"""
    file_path: str
    file_size: int
    file_hash: str
    mime_type: str
    extension: str
    validation_level: ValidationLevel
    overall_result: ValidationResult
    threat_level: ThreatLevel
    issues: List[ValidationIssue]
    scan_duration: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class FileValidator:
    """
    Enterprise-grade file validation system with security focus.
    
    Features:
    - Multi-level validation (basic to paranoid)
    - Security threat detection
    - File format verification
    - Content scanning and analysis
    - Performance optimization for large files
    - Comprehensive reporting and logging
    """
    
    def __init__(self, 
                 validation_level: ValidationLevel = ValidationLevel.STANDARD,
                 max_file_size: int = 100 * 1024 * 1024,  # 100MB
                 temp_dir: Optional[str] = None,
                 enable_content_scanning: bool = True,
                 enable_signature_verification: bool = True):
        """
        Initialize file validator
        
        Args:
            validation_level: Default validation level
            max_file_size: Maximum allowed file size
            temp_dir: Temporary directory for file operations
            enable_content_scanning: Whether to scan file content
            enable_signature_verification: Whether to verify file signatures
        """
        try:
            logger.info("Initializing FileValidator")
            
            self.validation_level = validation_level
            self.max_file_size = max_file_size
            self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir())
            self.enable_content_scanning = enable_content_scanning
            self.enable_signature_verification = enable_signature_verification
            
            # Initialize validation rules
            self._setup_validation_rules()
            
            # File signatures for format verification
            self._setup_file_signatures()
            
            # Dangerous patterns and signatures
            self._setup_security_patterns()
            
            # Statistics
            self.validation_stats = {
                "total_files_validated": 0,
                "files_passed": 0,
                "files_failed": 0,
                "threats_detected": 0,
                "total_scan_time": 0.0
            }
            
            logger.info("FileValidator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize FileValidator: {e}")
            raise

    async def validate_file(self, 
                           file_path: str,
                           validation_level: Optional[ValidationLevel] = None,
                           custom_rules: Optional[List[FileValidationRule]] = None) -> FileValidationReport:
        """
        Validate a file comprehensively
        
        Args:
            file_path: Path to file to validate
            validation_level: Validation level to use
            custom_rules: Additional custom validation rules
            
        Returns:
            FileValidationReport with detailed results
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Validating file: {file_path}")
            
            # Check if file exists
            if not Path(file_path).exists():
                raise ValueError(f"File does not exist: {file_path}")
            
            path = Path(file_path)
            validation_level = validation_level or self.validation_level
            
            # Initialize report
            file_size = path.stat().st_size
            file_hash = await self._calculate_file_hash(path)
            mime_type, _ = mimetypes.guess_type(str(path))
            mime_type = mime_type or "application/octet-stream"
            extension = path.suffix.lower()
            
            issues: List[ValidationIssue] = []
            
            # Get validation rules based on level
            rules = self._get_validation_rules(validation_level)
            if custom_rules:
                rules.extend(custom_rules)
            
            # Run validation checks
            for rule in rules:
                if rule.enabled:
                    rule_issues = await self._apply_validation_rule(path, rule)
                    issues.extend(rule_issues)
            
            # Additional security checks based on validation level
            if validation_level in [ValidationLevel.STRICT, ValidationLevel.PARANOID]:
                security_issues = await self._perform_security_scan(path)
                issues.extend(security_issues)
            
            # Determine overall result and threat level
            overall_result, threat_level = self._evaluate_validation_results(issues)
            
            # Calculate scan duration
            scan_duration = (datetime.now() - start_time).total_seconds()
            
            # Update statistics
            self._update_validation_stats(overall_result, threat_level, scan_duration)
            
            # Create report
            report = FileValidationReport(
                file_path=str(path),
                file_size=file_size,
                file_hash=file_hash,
                mime_type=mime_type,
                extension=extension,
                validation_level=validation_level,
                overall_result=overall_result,
                threat_level=threat_level,
                issues=issues,
                scan_duration=scan_duration,
                timestamp=datetime.now(),
                metadata={
                    "rules_applied": len(rules),
                    "total_checks": len(issues),
                    "file_readable": os.access(path, os.R_OK),
                    "file_writable": os.access(path, os.W_OK)
                }
            )
            
            logger.info(f"File validation completed: {file_path} - Result: {overall_result.value}")
            return report
            
        except Exception as e:
            scan_duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"File validation failed for {file_path}: {e}")
            
            # Return error report
            return FileValidationReport(
                file_path=file_path,
                file_size=0,
                file_hash="",
                mime_type="unknown",
                extension="",
                validation_level=validation_level or self.validation_level,
                overall_result=ValidationResult.INVALID,
                threat_level=ThreatLevel.HIGH,
                issues=[ValidationIssue(
                    rule_name="system_error",
                    severity=ThreatLevel.HIGH,
                    message=f"Validation failed: {str(e)}",
                    recommendation="Check file accessibility and system resources"
                )],
                scan_duration=scan_duration,
                timestamp=datetime.now()
            )

    async def validate_multiple_files(self, 
                                    file_paths: List[str],
                                    validation_level: Optional[ValidationLevel] = None,
                                    max_concurrent: int = 5) -> List[FileValidationReport]:
        """
        Validate multiple files concurrently
        
        Args:
            file_paths: List of file paths to validate
            validation_level: Validation level to use
            max_concurrent: Maximum concurrent validations
            
        Returns:
            List of FileValidationReport objects
        """
        logger.info(f"Validating {len(file_paths)} files")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def validate_with_semaphore(file_path: str):
            async with semaphore:
                return await self.validate_file(file_path, validation_level)
        
        tasks = [validate_with_semaphore(file_path) for file_path in file_paths]
        reports = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        valid_reports = []
        for i, report in enumerate(reports):
            if isinstance(report, Exception):
                logger.error(f"Failed to validate {file_paths[i]}: {report}")
                # Create error report
                error_report = FileValidationReport(
                    file_path=file_paths[i],
                    file_size=0,
                    file_hash="",
                    mime_type="unknown",
                    extension="",
                    validation_level=validation_level or self.validation_level,
                    overall_result=ValidationResult.INVALID,
                    threat_level=ThreatLevel.HIGH,
                    issues=[ValidationIssue(
                        rule_name="validation_error",
                        severity=ThreatLevel.HIGH,
                        message=f"Validation error: {str(report)}",
                        recommendation="Check file and system status"
                    )],
                    scan_duration=0.0,
                    timestamp=datetime.now()
                )
                valid_reports.append(error_report)
            else:
                valid_reports.append(report)
        
        return valid_reports

    async def is_file_safe(self, file_path: str) -> bool:
        """
        Quick safety check for a file
        
        Args:
            file_path: Path to file to check
            
        Returns:
            True if file appears safe
        """
        try:
            report = await self.validate_file(file_path, ValidationLevel.BASIC)
            return (report.overall_result == ValidationResult.VALID and 
                   report.threat_level in [ThreatLevel.SAFE, ThreatLevel.LOW])
        except Exception as e:
            logger.error(f"Safety check failed for {file_path}: {e}")
            return False

    def get_validation_stats(self) -> Dict[str, Any]:
        """
        Get validation statistics
        
        Returns:
            Dictionary with validation statistics
        """
        total_files = self.validation_stats["total_files_validated"]
        
        return {
            **self.validation_stats,
            "success_rate": (self.validation_stats["files_passed"] / max(total_files, 1)) * 100,
            "failure_rate": (self.validation_stats["files_failed"] / max(total_files, 1)) * 100,
            "threat_detection_rate": (self.validation_stats["threats_detected"] / max(total_files, 1)) * 100,
            "average_scan_time": (self.validation_stats["total_scan_time"] / max(total_files, 1))
        }

    # Private methods
    def _setup_validation_rules(self):
        """Setup standard validation rules"""
        self.validation_rules = {
            ValidationLevel.BASIC: [
                FileValidationRule(
                    name="file_size_check",
                    description="Check file size limits",
                    critical=True,
                    max_file_size=self.max_file_size
                ),
                FileValidationRule(
                    name="extension_check",
                    description="Check file extension",
                    blocked_extensions={'.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.vbs', '.js'}
                )
            ],
            ValidationLevel.STANDARD: [
                FileValidationRule(
                    name="file_size_check",
                    description="Check file size limits",
                    critical=True,
                    max_file_size=self.max_file_size
                ),
                FileValidationRule(
                    name="extension_check",
                    description="Check file extension",
                    blocked_extensions={'.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.vbs', '.js', 
                                      '.jar', '.app', '.deb', '.rpm'}
                ),
                FileValidationRule(
                    name="mime_type_check",
                    description="Validate MIME type",
                    blocked_mime_types={'application/x-executable', 'application/x-msdownload',
                                      'application/x-msdos-program', 'application/x-winexe'}
                ),
                FileValidationRule(
                    name="signature_verification",
                    description="Verify file signature matches extension"
                )
            ],
            ValidationLevel.STRICT: [
                FileValidationRule(
                    name="file_size_check",
                    description="Check file size limits",
                    critical=True,
                    max_file_size=self.max_file_size // 2  # Stricter size limit
                ),
                FileValidationRule(
                    name="extension_check",
                    description="Check file extension",
                    allowed_extensions={'.txt', '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.mp3', 
                                      '.mp4', '.avi', '.mov', '.doc', '.docx', '.xls', '.xlsx'}
                ),
                FileValidationRule(
                    name="mime_type_check",
                    description="Validate MIME type",
                    allowed_mime_types={'text/plain', 'application/pdf', 'image/jpeg', 'image/png',
                                      'image/gif', 'audio/mpeg', 'video/mp4', 'video/avi'}
                ),
                FileValidationRule(
                    name="signature_verification",
                    description="Verify file signature matches extension",
                    critical=True
                ),
                FileValidationRule(
                    name="content_scanning",
                    description="Scan file content for threats",
                    content_patterns=[
                        r'<script[^>]*>.*?</script>',  # JavaScript
                        r'eval\s*\(',  # Eval functions
                        r'exec\s*\(',  # Exec functions
                        r'system\s*\(',  # System calls
                    ]
                )
            ],
            ValidationLevel.PARANOID: [
                FileValidationRule(
                    name="file_size_check",
                    description="Check file size limits",
                    critical=True,
                    max_file_size=10 * 1024 * 1024  # 10MB limit
                ),
                FileValidationRule(
                    name="extension_check",
                    description="Check file extension",
                    allowed_extensions={'.txt', '.pdf', '.jpg', '.jpeg', '.png'}  # Very limited
                ),
                FileValidationRule(
                    name="mime_type_check",
                    description="Validate MIME type",
                    allowed_mime_types={'text/plain', 'application/pdf', 'image/jpeg', 'image/png'}
                ),
                FileValidationRule(
                    name="signature_verification",
                    description="Verify file signature matches extension",
                    critical=True
                ),
                FileValidationRule(
                    name="content_scanning",
                    description="Comprehensive content scanning",
                    critical=True,
                    content_patterns=[
                        r'<script[^>]*>.*?</script>',
                        r'eval\s*\(',
                        r'exec\s*\(',
                        r'system\s*\(',
                        r'shell_exec\s*\(',
                        r'passthru\s*\(',
                        r'base64_decode\s*\(',
                        r'file_get_contents\s*\(',
                        r'fopen\s*\(',
                        r'curl_exec\s*\(',
                    ]
                )
            ]
        }

    def _setup_file_signatures(self):
        """Setup file signature database for verification"""
        self.file_signatures = {
            # Images
            '.jpg': [b'\xFF\xD8\xFF'],
            '.jpeg': [b'\xFF\xD8\xFF'],
            '.png': [b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'],
            '.gif': [b'\x47\x49\x46\x38\x37\x61', b'\x47\x49\x46\x38\x39\x61'],
            '.bmp': [b'\x42\x4D'],
            '.webp': [b'\x52\x49\x46\x46'],
            
            # Documents
            '.pdf': [b'\x25\x50\x44\x46'],
            '.doc': [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'],
            '.docx': [b'\x50\x4B\x03\x04'],
            '.xls': [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'],
            '.xlsx': [b'\x50\x4B\x03\x04'],
            '.ppt': [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'],
            '.pptx': [b'\x50\x4B\x03\x04'],
            
            # Audio
            '.mp3': [b'\xFF\xFB', b'\xFF\xF3', b'\xFF\xF2', b'\x49\x44\x33'],
            '.wav': [b'\x52\x49\x46\x46'],
            '.flac': [b'\x66\x4C\x61\x43'],
            '.ogg': [b'\x4F\x67\x67\x53'],
            
            # Video
            '.mp4': [b'\x00\x00\x00\x20\x66\x74\x79\x70', b'\x00\x00\x00\x18\x66\x74\x79\x70'],
            '.avi': [b'\x52\x49\x46\x46'],
            '.mov': [b'\x00\x00\x00\x14\x66\x74\x79\x70'],
            '.wmv': [b'\x30\x26\xB2\x75\x8E\x66\xCF\x11'],
            
            # Archives
            '.zip': [b'\x50\x4B\x03\x04', b'\x50\x4B\x05\x06', b'\x50\x4B\x07\x08'],
            '.rar': [b'\x52\x61\x72\x21\x1A\x07\x00'],
            '.7z': [b'\x37\x7A\xBC\xAF\x27\x1C'],
            '.tar': [b'\x75\x73\x74\x61\x72'],
            '.gz': [b'\x1F\x8B'],
            
            # Text
            '.txt': [],  # No specific signature
            '.csv': [],  # No specific signature
            '.json': [],  # No specific signature
            '.xml': [b'\x3C\x3F\x78\x6D\x6C'],
            '.html': [b'\x3C\x21\x44\x4F\x43\x54\x59\x50\x45', b'\x3C\x68\x74\x6D\x6C'],
            
            # Executables (dangerous)
            '.exe': [b'\x4D\x5A'],
            '.dll': [b'\x4D\x5A'],
            '.com': [b'\x4D\x5A'],
            '.scr': [b'\x4D\x5A'],
        }

    def _setup_security_patterns(self):
        """Setup security threat patterns"""
        self.dangerous_patterns = [
            # Script injections
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*=',
            
            # Command injections
            r'eval\s*\(',
            r'exec\s*\(',
            r'system\s*\(',
            r'shell_exec\s*\(',
            r'passthru\s*\(',
            r'proc_open\s*\(',
            
            # File operations
            r'file_get_contents\s*\(',
            r'file_put_contents\s*\(',
            r'fopen\s*\(',
            r'fwrite\s*\(',
            r'include\s*\(',
            r'require\s*\(',
            
            # Network operations
            r'curl_exec\s*\(',
            r'fsockopen\s*\(',
            r'socket_create\s*\(',
            r'wget\s+',
            r'curl\s+',
            
            # Encoding/obfuscation
            r'base64_decode\s*\(',
            r'base64_encode\s*\(',
            r'urldecode\s*\(',
            r'html_entity_decode\s*\(',
            
            # Database operations
            r'mysql_query\s*\(',
            r'mysqli_query\s*\(',
            r'SELECT\s+.*\s+FROM\s+',
            r'INSERT\s+INTO\s+',
            r'UPDATE\s+.*\s+SET\s+',
            r'DELETE\s+FROM\s+',
            r'DROP\s+TABLE\s+',
            r'UNION\s+SELECT\s+',
            
            # Registry operations (Windows)
            r'HKEY_',
            r'SOFTWARE\\',
            r'SYSTEM\\',
            
            # Suspicious URLs
            r'http://[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',
            r'ftp://[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',
        ]
        
        # Compile patterns for performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.dangerous_patterns]

    def _get_validation_rules(self, level: ValidationLevel) -> List[FileValidationRule]:
        """Get validation rules for specified level"""
        return self.validation_rules.get(level, self.validation_rules[ValidationLevel.STANDARD])

    async def _apply_validation_rule(self, file_path: Path, rule: FileValidationRule) -> List[ValidationIssue]:
        """Apply a single validation rule"""
        issues = []
        
        try:
            if rule.name == "file_size_check":
                issues.extend(await self._check_file_size(file_path, rule))
            elif rule.name == "extension_check":
                issues.extend(self._check_file_extension(file_path, rule))
            elif rule.name == "mime_type_check":
                issues.extend(self._check_mime_type(file_path, rule))
            elif rule.name == "signature_verification":
                issues.extend(await self._verify_file_signature(file_path, rule))
            elif rule.name == "content_scanning":
                issues.extend(await self._scan_file_content(file_path, rule))
            
        except Exception as e:
            logger.error(f"Error applying rule {rule.name} to {file_path}: {e}")
            issues.append(ValidationIssue(
                rule_name=rule.name,
                severity=ThreatLevel.MEDIUM,
                message=f"Rule application failed: {str(e)}",
                recommendation="Check file accessibility and rule configuration"
            ))
        
        return issues

    async def _check_file_size(self, file_path: Path, rule: FileValidationRule) -> List[ValidationIssue]:
        """Check file size against limits"""
        issues = []
        
        try:
            file_size = file_path.stat().st_size
            
            if rule.max_file_size and file_size > rule.max_file_size:
                severity = ThreatLevel.HIGH if rule.critical else ThreatLevel.MEDIUM
                issues.append(ValidationIssue(
                    rule_name=rule.name,
                    severity=severity,
                    message=f"File size {file_size} bytes exceeds maximum allowed {rule.max_file_size} bytes",
                    details={"actual_size": file_size, "max_size": rule.max_file_size},
                    recommendation="Reduce file size or contact administrator for higher limits"
                ))
        
        except Exception as e:
            issues.append(ValidationIssue(
                rule_name=rule.name,
                severity=ThreatLevel.MEDIUM,
                message=f"Failed to check file size: {str(e)}",
                recommendation="Check file accessibility"
            ))
        
        return issues

    def _check_file_extension(self, file_path: Path, rule: FileValidationRule) -> List[ValidationIssue]:
        """Check file extension against allowed/blocked lists"""
        issues = []
        
        extension = file_path.suffix.lower()
        
        # Check blocked extensions
        if rule.blocked_extensions and extension in rule.blocked_extensions:
            issues.append(ValidationIssue(
                rule_name=rule.name,
                severity=ThreatLevel.HIGH,
                message=f"File extension '{extension}' is blocked for security reasons",
                details={"extension": extension, "blocked_extensions": list(rule.blocked_extensions)},
                recommendation="Use a different file format"
            ))
        
        # Check allowed extensions (if specified)
        if rule.allowed_extensions and extension not in rule.allowed_extensions:
            issues.append(ValidationIssue(
                rule_name=rule.name,
                severity=ThreatLevel.MEDIUM,
                message=f"File extension '{extension}' is not in allowed list",
                details={"extension": extension, "allowed_extensions": list(rule.allowed_extensions)},
                recommendation="Use an allowed file format"
            ))
        
        return issues

    def _check_mime_type(self, file_path: Path, rule: FileValidationRule) -> List[ValidationIssue]:
        """Check MIME type against allowed/blocked lists"""
        issues = []
        
        mime_type, _ = mimetypes.guess_type(str(file_path))
        mime_type = mime_type or "application/octet-stream"
        
        # Check blocked MIME types
        if rule.blocked_mime_types and mime_type in rule.blocked_mime_types:
            issues.append(ValidationIssue(
                rule_name=rule.name,
                severity=ThreatLevel.HIGH,
                message=f"MIME type '{mime_type}' is blocked for security reasons",
                details={"mime_type": mime_type, "blocked_mime_types": list(rule.blocked_mime_types)},
                recommendation="Use a different file format"
            ))
        
        # Check allowed MIME types (if specified)
        if rule.allowed_mime_types and mime_type not in rule.allowed_mime_types:
            issues.append(ValidationIssue(
                rule_name=rule.name,
                severity=ThreatLevel.MEDIUM,
                message=f"MIME type '{mime_type}' is not in allowed list",
                details={"mime_type": mime_type, "allowed_mime_types": list(rule.allowed_mime_types)},
                recommendation="Use an allowed file format"
            ))
        
        return issues

    async def _verify_file_signature(self, file_path: Path, rule: FileValidationRule) -> List[ValidationIssue]:
        """Verify file signature matches extension"""
        issues = []
        
        try:
            extension = file_path.suffix.lower()
            expected_signatures = self.file_signatures.get(extension, [])
            
            if not expected_signatures:
                # No signature check for this extension
                return issues
            
            # Read file header
            async with aiofiles.open(file_path, 'rb') as f:
                header = await f.read(32)  # Read first 32 bytes
            
            # Check if any expected signature matches
            signature_match = False
            for expected_sig in expected_signatures:
                if header.startswith(expected_sig):
                    signature_match = True
                    break
            
            if not signature_match:
                severity = ThreatLevel.HIGH if rule.critical else ThreatLevel.MEDIUM
                issues.append(ValidationIssue(
                    rule_name=rule.name,
                    severity=severity,
                    message=f"File signature does not match extension '{extension}'",
                    details={
                        "extension": extension,
                        "expected_signatures": [sig.hex() for sig in expected_signatures],
                        "actual_header": header[:16].hex()
                    },
                    recommendation="Ensure file is not corrupted or maliciously renamed"
                ))
        
        except Exception as e:
            issues.append(ValidationIssue(
                rule_name=rule.name,
                severity=ThreatLevel.MEDIUM,
                message=f"Failed to verify file signature: {str(e)}",
                recommendation="Check file accessibility and integrity"
            ))
        
        return issues

    async def _scan_file_content(self, file_path: Path, rule: FileValidationRule) -> List[ValidationIssue]:
        """Scan file content for malicious patterns"""
        issues = []
        
        if not self.enable_content_scanning:
            return issues
        
        try:
            # Skip content scanning for very large files (performance)
            file_size = file_path.stat().st_size
            if file_size > 50 * 1024 * 1024:  # 50MB
                return issues
            
            # Try to read file as text
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = await f.read()
            except:
                async with aiofiles.open(file_path, 'rb') as f:
                    content_bytes = await f.read()
                    content = content_bytes.decode('utf-8', errors='ignore')
            
            # Scan for dangerous patterns
            detected_patterns = []
            for pattern in self.compiled_patterns:
                matches = pattern.findall(content)
                if matches:
                    detected_patterns.append({
                        "pattern": pattern.pattern,
                        "matches": len(matches),
                        "examples": matches[:3]  # First 3 matches
                    })
            
            # Scan for custom patterns in rule
            if rule.content_patterns:
                for pattern_str in rule.content_patterns:
                    pattern = re.compile(pattern_str, re.IGNORECASE)
                    matches = pattern.findall(content)
                    if matches:
                        detected_patterns.append({
                            "pattern": pattern_str,
                            "matches": len(matches),
                            "examples": matches[:3]
                        })
            
            if detected_patterns:
                severity = ThreatLevel.HIGH if rule.critical else ThreatLevel.MEDIUM
                issues.append(ValidationIssue(
                    rule_name=rule.name,
                    severity=severity,
                    message=f"Detected {len(detected_patterns)} potentially malicious patterns in file content",
                    details={"detected_patterns": detected_patterns},
                    recommendation="Review file content for malicious code and sanitize if necessary"
                ))
        
        except Exception as e:
            issues.append(ValidationIssue(
                rule_name=rule.name,
                severity=ThreatLevel.LOW,
                message=f"Content scanning failed: {str(e)}",
                recommendation="Manual review recommended"
            ))
        
        return issues

    async def _perform_security_scan(self, file_path: Path) -> List[ValidationIssue]:
        """Perform additional security scanning"""
        issues = []
        
        try:
            # Check for executable permissions
            if os.access(file_path, os.X_OK):
                issues.append(ValidationIssue(
                    rule_name="executable_permissions",
                    severity=ThreatLevel.MEDIUM,
                    message="File has executable permissions",
                    recommendation="Remove executable permissions if not required"
                ))
            
            # Check for hidden files (Unix-like systems)
            if file_path.name.startswith('.') and file_path.name != '.':
                issues.append(ValidationIssue(
                    rule_name="hidden_file",
                    severity=ThreatLevel.LOW,
                    message="File is hidden",
                    details={"filename": file_path.name},
                    recommendation="Verify if hidden file is intentional"
                ))
            
            # Check for suspicious names
            suspicious_names = [
                'autorun', 'autoexec', 'boot', 'config', 'install', 'setup',
                'update', 'patch', 'fix', 'crack', 'keygen', 'serial'
            ]
            
            filename_lower = file_path.stem.lower()
            for suspicious in suspicious_names:
                if suspicious in filename_lower:
                    issues.append(ValidationIssue(
                        rule_name="suspicious_filename",
                        severity=ThreatLevel.MEDIUM,
                        message=f"Filename contains suspicious keyword: '{suspicious}'",
                        details={"keyword": suspicious, "filename": file_path.name},
                        recommendation="Verify file legitimacy"
                    ))
                    break
        
        except Exception as e:
            logger.error(f"Security scan failed for {file_path}: {e}")
        
        return issues

    def _evaluate_validation_results(self, issues: List[ValidationIssue]) -> Tuple[ValidationResult, ThreatLevel]:
        """Evaluate overall validation results"""
        if not issues:
            return ValidationResult.VALID, ThreatLevel.SAFE
        
        # Count issues by severity
        severity_counts = {
            ThreatLevel.CRITICAL: 0,
            ThreatLevel.HIGH: 0,
            ThreatLevel.MEDIUM: 0,
            ThreatLevel.LOW: 0
        }
        
        for issue in issues:
            severity_counts[issue.severity] += 1
        
        # Determine overall threat level
        if severity_counts[ThreatLevel.CRITICAL] > 0:
            return ValidationResult.BLOCKED, ThreatLevel.CRITICAL
        elif severity_counts[ThreatLevel.HIGH] > 0:
            return ValidationResult.INVALID, ThreatLevel.HIGH
        elif severity_counts[ThreatLevel.MEDIUM] > 2:  # Multiple medium threats
            return ValidationResult.SUSPICIOUS, ThreatLevel.MEDIUM
        elif severity_counts[ThreatLevel.MEDIUM] > 0:
            return ValidationResult.SUSPICIOUS, ThreatLevel.MEDIUM
        else:
            return ValidationResult.VALID, ThreatLevel.LOW

    async def _calculate_file_hash(self, file_path: Path, algorithm: str = "sha256") -> str:
        """Calculate file hash"""
        try:
            hash_func = hashlib.new(algorithm)
            
            async with aiofiles.open(file_path, 'rb') as f:
                while chunk := await f.read(8192):
                    hash_func.update(chunk)
            
            return hash_func.hexdigest()
        
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return ""

    def _update_validation_stats(self, result: ValidationResult, threat_level: ThreatLevel, scan_duration: float):
        """Update validation statistics"""
        self.validation_stats["total_files_validated"] += 1
        self.validation_stats["total_scan_time"] += scan_duration
        
        if result == ValidationResult.VALID:
            self.validation_stats["files_passed"] += 1
        else:
            self.validation_stats["files_failed"] += 1
        
        if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            self.validation_stats["threats_detected"] += 1


# Utility functions
async def quick_file_check(file_path: str) -> bool:
    """
    Quick safety check for a file
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file appears safe
    """
    validator = FileValidator(validation_level=ValidationLevel.BASIC)
    return await validator.is_file_safe(file_path)


def is_safe_filename(filename: str) -> bool:
    """
    Check if filename is safe
    
    Args:
        filename: Filename to check
        
    Returns:
        True if filename appears safe
    """
    # Check for dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '/', '\\']
    if any(char in filename for char in dangerous_chars):
        return False
    
    # Check for dangerous extensions
    dangerous_extensions = {'.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.vbs', '.js'}
    extension = Path(filename).suffix.lower()
    if extension in dangerous_extensions:
        return False
    
    # Check for suspicious patterns
    suspicious_patterns = ['..', 'autorun', 'autoexec']
    filename_lower = filename.lower()
    if any(pattern in filename_lower for pattern in suspicious_patterns):
        return False
    
    return True


def get_file_risk_score(file_path: str) -> int:
    """
    Get a simple risk score for a file (0-100)
    
    Args:
        file_path: Path to file
        
    Returns:
        Risk score (0 = safe, 100 = very dangerous)
    """
    score = 0
    path = Path(file_path)
    
    # Extension risk
    extension = path.suffix.lower()
    high_risk_extensions = {'.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.vbs', '.js'}
    medium_risk_extensions = {'.jar', '.app', '.deb', '.rpm', '.msi'}
    
    if extension in high_risk_extensions:
        score += 50
    elif extension in medium_risk_extensions:
        score += 25
    
    # Filename risk
    filename_lower = path.name.lower()
    suspicious_words = ['crack', 'keygen', 'patch', 'hack', 'virus', 'trojan', 'backdoor']
    for word in suspicious_words:
        if word in filename_lower:
            score += 20
            break
    
    # Size risk (very small or very large files)
    try:
        size = path.stat().st_size
        if size < 100:  # Very small files
            score += 10
        elif size > 100 * 1024 * 1024:  # Very large files (>100MB)
            score += 15
    except:
        pass
    
    # Hidden file risk
    if path.name.startswith('.') and path.name != '.':
        score += 10
    
    return min(score, 100)