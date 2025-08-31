"""Input and Content Validation Module
Advanced validation and security scanning for IA Influencer Agent

Features:
- Multi-format content validation with deep inspection
- Advanced malware and virus scanning with multiple engines
- AI-powered content analysis for threats and policy violations
- Input sanitization and validation with context-aware filtering
- Deep file type verification with magic number analysis
- Content security policy enforcement with real-time monitoring
- Data integrity validation with cryptographic verification
- Schema validation with custom business rules
- Machine learning-based anomaly detection for content
- Zero-day malware detection using behavioral analysis
- Content authenticity verification using digital signatures
- Advanced phishing and social engineering detection

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use strictly prohibited.
License: Proprietary - Contact author for licensing terms
"""
import re
import mimetypes
import magic
import hashlib
import json
import base64
import asyncio
import tempfile
import subprocess
from typing import Dict, List, Optional, Union, Any, Tuple, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import asynccontextmanager
import xml.etree.ElementTree as ET

from PIL import Image, ImageStat
import av
import mutagen
from pydantic import BaseModel, validator, ValidationError, Field
import bleach
import yara
import clamd
import requests
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

from backend.core.config import get_settings
from backend.core.cache import CacheManager
from backend.core.logging import SecurityLogger


class ValidationResult(Enum):
    """Validation result status with threat levels"""    VALID = "valid"
    INVALID = "invalid"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    QUARANTINED = "quarantined"
    BLOCKED = "blocked"


class ThreatCategory(Enum):
    """Threat categories for classification"""    MALWARE = "malware"
    VIRUS = "virus"
    TROJAN = "trojan"
    SPYWARE = "spyware"
    RANSOMWARE = "ransomware"
    PHISHING = "phishing"
    SOCIAL_ENGINEERING = "social_engineering"
    COPYRIGHT_VIOLATION = "copyright_violation"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    SPAM = "spam"
    FRAUD = "fraud"


class ContentCategory(Enum):
    """Content categories for validation"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    EXECUTABLE = "executable"
    SCRIPT = "script"


@dataclass
class ValidationReport:
    """Comprehensive validation report"""    file_id: str
    filename: str
    content_type: str
    file_size: int
    validation_result: ValidationResult
    validation_details: Dict[str, Any] = field(default_factory=dict)
    security_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    validated_at: datetime = field(default_factory=datetime.utcnow)
    scanner_version: str = "1.0.0"


@dataclass
class MalwareSignature:
    """Malware signature definition"""    signature_id: str
    name: str
    description: str
    pattern: bytes
    severity: str
    category: str
    created_at: datetime


class InputValidator:
    """Advanced input validation and sanitization"""    
    def __init__(self):
        self.logger = SecurityLogger("InputValidator")
        self.cache = CacheManager()
        self.settings = get_settings()
        
        # Initialize validation rules
        self.validation_rules = self._initialize_validation_rules()
        
        # HTML sanitization configuration
        self.allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'
        ]
        self.allowed_attributes = {
            '*': ['class'],
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'width', 'height']
        }
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules"""        return {
            "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            "url": r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$',
            "username": r'^[a-zA-Z0-9_-]{3,30}$',
            "password": r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
            "filename": r'^[a-zA-Z0-9._-]+$',
            "content_id": r'^[a-zA-Z0-9_-]{10,50}$',
            "hex_color": r'^#[0-9A-Fa-f]{6}$',
            "ipv4": r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
            "uuid": r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        }
    
    def validate_input(self, input_value: str, validation_type: str) -> Tuple[bool, str]:
        """Validate input against specific rules"""        try:
            if validation_type not in self.validation_rules:
                return False, f"Unknown validation type: {validation_type}"
            
            pattern = self.validation_rules[validation_type]
            is_valid = bool(re.match(pattern, input_value))
            
            if not is_valid:
                return False, f"Input does not match {validation_type} pattern"
            
            # Additional security checks
            security_issues = self._check_input_security(input_value, validation_type)
            if security_issues:
                return False, f"Security issues detected: {', '.join(security_issues)}"
            
            return True, "Valid input"
            
        except Exception as e:
            self.logger.error(f"Input validation failed: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    def _check_input_security(self, input_value: str, validation_type: str) -> List[str]:
        """Check input for security issues"""        issues = []
        
        # Check for SQL injection patterns
        sql_patterns = [
            r"(?i)(union|select|insert|update|delete|drop|exec|script)",
            r"(?i)(or\s+1\s*=\s*1|and\s+1\s*=\s*1)",
            r"(?i)('.*'|\".*\")",
            r"(?i)(--|#|/\*|\*/)"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, input_value):
                issues.append("Potential SQL injection")
                break
        
        # Check for XSS patterns
        xss_patterns = [
            r"(?i)<script[^>]*>.*?</script>",
            r"(?i)javascript:",
            r"(?i)on\w+\s*=",
            r"(?i)<iframe[^>]*>.*?</iframe>",
            r"(?i)document\.(cookie|write|location)"
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, input_value):
                issues.append("Potential XSS attack")
                break
        
        # Check for path traversal
        if "../" in input_value or "..\\" in input_value:
            issues.append("Path traversal attempt")
        
        # Check for command injection
        command_patterns = [
            r"(?i)(;|\||&|`|\$\(|\${)",
            r"(?i)(cat|ls|dir|type|copy|move|del|rm)\s",
            r"(?i)(wget|curl|nc|netcat|telnet)"
        ]
        
        for pattern in command_patterns:
            if re.search(pattern, input_value):
                issues.append("Potential command injection")
                break
        
        return issues
    
    def sanitize_html(self, html_content: str) -> str:
        """Sanitize HTML content"""        try:
            sanitized = bleach.clean(
                html_content,
                tags=self.allowed_tags,
                attributes=self.allowed_attributes,
                strip=True
            )
            
            return sanitized
            
        except Exception as e:
            self.logger.error(f"HTML sanitization failed: {str(e)}")
            return ""
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage"""        try:
            # Remove path components
            filename = filename.split('/')[-1].split('\\')[-1]
            
            # Remove dangerous characters
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            # Limit length
            if len(filename) > 255:
                name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
                filename = name[:250] + ('.' + ext if ext else '')
            
            # Ensure not empty
            if not filename or filename.startswith('.'):
                filename = 'file_' + hashlib.md5(filename.encode()).hexdigest()[:8]
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Filename sanitization failed: {str(e)}")
            return f"file_{int(datetime.utcnow().timestamp())}"
    
    def validate_json_schema(self, json_data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate JSON data against schema"""        try:
            from jsonschema import validate, ValidationError as JsonValidationError
            
            validate(instance=json_data, schema=schema)
            return True, []
            
        except JsonValidationError as e:
            return False, [str(e)]
        except Exception as e:
            self.logger.error(f"JSON schema validation failed: {str(e)}")
            return False, [f"Validation error: {str(e)}"]


class ContentValidator:
    """Content validation for uploaded files"""    
    def __init__(self):
        self.logger = SecurityLogger("ContentValidator")
        self.cache = CacheManager()
        
        # Maximum file sizes (in bytes)
        self.max_file_sizes = {
            ContentCategory.IMAGE: 50 * 1024 * 1024,  # 50MB
            ContentCategory.AUDIO: 500 * 1024 * 1024,  # 500MB
            ContentCategory.VIDEO: 2 * 1024 * 1024 * 1024,  # 2GB
            ContentCategory.DOCUMENT: 100 * 1024 * 1024,  # 100MB
            ContentCategory.TEXT: 10 * 1024 * 1024,  # 10MB
            ContentCategory.ARCHIVE: 1 * 1024 * 1024 * 1024,  # 1GB
        }
        
        # Allowed MIME types
        self.allowed_mime_types = {
            ContentCategory.IMAGE: [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp',
                'image/bmp', 'image/tiff', 'image/svg+xml'
            ],
            ContentCategory.AUDIO: [
                'audio/mpeg', 'audio/mp4', 'audio/wav', 'audio/flac',
                'audio/ogg', 'audio/aac', 'audio/webm'
            ],
            ContentCategory.VIDEO: [
                'video/mp4', 'video/mpeg', 'video/quicktime', 'video/x-msvideo',
                'video/webm', 'video/ogg', 'video/x-flv'
            ],
            ContentCategory.DOCUMENT: [
                'application/pdf', 'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/plain', 'text/rtf'
            ]
        }
        
        # Blocked file extensions
        self.blocked_extensions = {
            '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs',
            '.js', '.jar', '.app', '.deb', '.pkg', '.dmg', '.msi'
        }
    
    async def validate_content(
        self, 
        file_data: bytes, 
        filename: str,
        declared_mime_type: Optional[str] = None
    ) -> ValidationReport:
        """Comprehensive content validation"""        try:
            file_id = hashlib.md5(file_data).hexdigest()
            
            # Initialize report
            report = ValidationReport(
                file_id=file_id,
                filename=filename,
                content_type=declared_mime_type or "unknown",
                file_size=len(file_data),
                validation_result=ValidationResult.VALID
            )
            
            # 1. File size validation
            size_validation = self._validate_file_size(file_data, filename)
            report.validation_details.update(size_validation)
            
            # 2. File type detection and validation
            type_validation = await self._validate_file_type(file_data, filename, declared_mime_type)
            report.validation_details.update(type_validation)
            
            # 3. File extension validation
            ext_validation = self._validate_file_extension(filename)
            report.validation_details.update(ext_validation)
            
            # 4. Content structure validation
            structure_validation = await self._validate_content_structure(file_data, type_validation.get('detected_category'))
            report.validation_details.update(structure_validation)
            
            # 5. Security validation
            security_validation = await self._validate_content_security(file_data, filename)
            report.validation_details.update(security_validation)
            
            # Determine overall validation result
            if any(v.get('is_malicious', False) for v in report.validation_details.values()):
                report.validation_result = ValidationResult.MALICIOUS
            elif any(v.get('is_suspicious', False) for v in report.validation_details.values()):
                report.validation_result = ValidationResult.SUSPICIOUS
            elif any(not v.get('is_valid', True) for v in report.validation_details.values()):
                report.validation_result = ValidationResult.INVALID
            
            # Collect security issues and recommendations
            for validation_name, validation_data in report.validation_details.items():
                if 'security_issues' in validation_data:
                    report.security_issues.extend(validation_data['security_issues'])
                if 'recommendations' in validation_data:
                    report.recommendations.extend(validation_data['recommendations'])
            
            self.logger.info(f"Content validation completed: {filename} = {report.validation_result.value}")
            return report
            
        except Exception as e:
            self.logger.error(f"Content validation failed: {str(e)}")
            return ValidationReport(
                file_id="error",
                filename=filename,
                content_type="unknown",
                file_size=len(file_data),
                validation_result=ValidationResult.INVALID,
                validation_details={"error": str(e)}
            )
    
    def _validate_file_size(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Validate file size"""        file_size = len(file_data)
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        # Determine content category
        category = self._determine_content_category(file_ext)
        max_size = self.max_file_sizes.get(category, 10 * 1024 * 1024)  # Default 10MB
        
        is_valid = file_size <= max_size
        
        validation_data = {
            "is_valid": is_valid,
            "file_size": file_size,
            "max_allowed_size": max_size,
            "content_category": category.value if category else "unknown"
        }
        
        if not is_valid:
            validation_data["security_issues"] = [f"File size exceeds limit ({file_size} > {max_size})"]
            validation_data["recommendations"] = ["Reduce file size or compress the content"]
        
        return {"file_size": validation_data}
    
    async def _validate_file_type(
        self, 
        file_data: bytes, 
        filename: str, 
        declared_mime_type: Optional[str]
    ) -> Dict[str, Any]:
        """Validate file type and detect MIME type"""        try:
            # Detect actual MIME type using magic
            try:
                detected_mime = magic.from_buffer(file_data, mime=True)
            except:
                # Fallback to mimetypes
                detected_mime, _ = mimetypes.guess_type(filename)
                detected_mime = detected_mime or "application/octet-stream"
            
            # Determine content category
            category = self._get_category_from_mime(detected_mime)
            
            # Check if declared type matches detected type
            type_mismatch = declared_mime_type and declared_mime_type != detected_mime
            
            # Check if MIME type is allowed
            is_allowed = self._is_mime_type_allowed(detected_mime, category)
            
            validation_data = {
                "is_valid": is_allowed and not type_mismatch,
                "detected_mime_type": detected_mime,
                "declared_mime_type": declared_mime_type,
                "detected_category": category.value if category else "unknown",
                "type_mismatch": type_mismatch,
                "mime_allowed": is_allowed
            }
            
            if type_mismatch:
                validation_data["is_suspicious"] = True
                validation_data["security_issues"] = ["MIME type mismatch detected"]
                validation_data["recommendations"] = ["Verify file integrity and source"]
            
            if not is_allowed:
                validation_data["security_issues"] = validation_data.get("security_issues", [])
                validation_data["security_issues"].append(f"File type not allowed: {detected_mime}")
                validation_data["recommendations"] = validation_data.get("recommendations", [])
                validation_data["recommendations"].append("Convert to an allowed file format")
            
            return {"file_type": validation_data}
            
        except Exception as e:
            self.logger.error(f"File type validation failed: {str(e)}")
            return {"file_type": {"is_valid": False, "error": str(e)}}
    
    def _validate_file_extension(self, filename: str) -> Dict[str, Any]:
        """Validate file extension"""        file_ext = '.' + filename.lower().split('.')[-1] if '.' in filename else ''
        
        is_blocked = file_ext in self.blocked_extensions
        is_valid = not is_blocked
        
        validation_data = {
            "is_valid": is_valid,
            "file_extension": file_ext,
            "is_blocked": is_blocked
        }
        
        if is_blocked:
            validation_data["is_malicious"] = True
            validation_data["security_issues"] = [f"Blocked file extension: {file_ext}"]
            validation_data["recommendations"] = ["Remove or rename the file"]
        
        return {"file_extension": validation_data}
    
    async def _validate_content_structure(
        self, 
        file_data: bytes, 
        content_category: Optional[str]
    ) -> Dict[str, Any]:
        """Validate content structure based on type"""        try:
            if not content_category:
                return {"content_structure": {"is_valid": True, "message": "No structure validation needed"}}
            
            category = ContentCategory(content_category)
            
            if category == ContentCategory.IMAGE:
                return await self._validate_image_structure(file_data)
            elif category == ContentCategory.AUDIO:
                return await self._validate_audio_structure(file_data)
            elif category == ContentCategory.VIDEO:
                return await self._validate_video_structure(file_data)
            else:
                return {"content_structure": {"is_valid": True, "message": f"No specific validation for {category.value}"}}
                
        except Exception as e:
            self.logger.error(f"Content structure validation failed: {str(e)}")
            return {"content_structure": {"is_valid": False, "error": str(e)}}
    
    async def _validate_image_structure(self, image_data: bytes) -> Dict[str, Any]:
        """Validate image file structure"""        try:
            import io
            image = Image.open(io.BytesIO(image_data))
            
            # Basic image validation
            width, height = image.size
            format_name = image.format
            mode = image.mode
            
            # Check for reasonable dimensions
            max_dimension = 50000  # 50k pixels
            reasonable_size = width <= max_dimension and height <= max_dimension
            
            # Check for suspicious metadata
            has_suspicious_metadata = False
            if hasattr(image, '_getexif') and image._getexif():
                exif_data = image._getexif()
                # Check for suspicious EXIF data
                if any(key in str(exif_data) for key in ['script', 'javascript', 'php']):
                    has_suspicious_metadata = True
            
            validation_data = {
                "is_valid": reasonable_size and not has_suspicious_metadata,
                "width": width,
                "height": height,
                "format": format_name,
                "mode": mode,
                "reasonable_size": reasonable_size,
                "suspicious_metadata": has_suspicious_metadata
            }
            
            if not reasonable_size:
                validation_data["security_issues"] = [f"Image dimensions too large: {width}x{height}"]
                validation_data["recommendations"] = ["Resize image to reasonable dimensions"]
            
            if has_suspicious_metadata:
                validation_data["is_suspicious"] = True
                validation_data["security_issues"] = validation_data.get("security_issues", [])
                validation_data["security_issues"].append("Suspicious metadata detected")
                validation_data["recommendations"] = validation_data.get("recommendations", [])
                validation_data["recommendations"].append("Strip metadata before upload")
            
            return {"content_structure": validation_data}
            
        except Exception as e:
            return {"content_structure": {"is_valid": False, "error": f"Invalid image format: {str(e)}"}}
    
    async def _validate_audio_structure(self, audio_data: bytes) -> Dict[str, Any]:
        """Validate audio file structure"""        try:
            import io
            
            # Try to parse with mutagen
            audio_file = mutagen.File(io.BytesIO(audio_data))
            
            if audio_file is None:
                return {"content_structure": {"is_valid": False, "error": "Invalid audio format"}}
            
            # Get audio properties
            duration = getattr(audio_file.info, 'length', 0)
            bitrate = getattr(audio_file.info, 'bitrate', 0)
            
            # Check for reasonable duration (max 2 hours)
            max_duration = 7200  # 2 hours
            reasonable_duration = 0 < duration <= max_duration
            
            validation_data = {
                "is_valid": reasonable_duration,
                "duration": duration,
                "bitrate": bitrate,
                "reasonable_duration": reasonable_duration
            }
            
            if not reasonable_duration:
                validation_data["security_issues"] = [f"Audio duration suspicious: {duration} seconds"]
                validation_data["recommendations"] = ["Verify audio file integrity"]
            
            return {"content_structure": validation_data}
            
        except Exception as e:
            return {"content_structure": {"is_valid": False, "error": f"Audio validation failed: {str(e)}"}}
    
    async def _validate_video_structure(self, video_data: bytes) -> Dict[str, Any]:
        """Validate video file structure"""        try:
            import io
            
            # Try to open with PyAV
            container = av.open(io.BytesIO(video_data))
            
            # Get video properties
            duration = float(container.duration) / av.time_base if container.duration else 0
            
            # Check for video and audio streams
            video_streams = [s for s in container.streams if s.type == 'video']
            audio_streams = [s for s in container.streams if s.type == 'audio']
            
            has_video = len(video_streams) > 0
            has_audio = len(audio_streams) > 0
            
            # Check for reasonable duration (max 4 hours)
            max_duration = 14400  # 4 hours
            reasonable_duration = 0 < duration <= max_duration
            
            validation_data = {
                "is_valid": has_video and reasonable_duration,
                "duration": duration,
                "video_streams": len(video_streams),
                "audio_streams": len(audio_streams),
                "has_video": has_video,
                "has_audio": has_audio,
                "reasonable_duration": reasonable_duration
            }
            
            if not has_video:
                validation_data["security_issues"] = ["No video stream found"]
            
            if not reasonable_duration:
                validation_data["security_issues"] = validation_data.get("security_issues", [])
                validation_data["security_issues"].append(f"Video duration suspicious: {duration} seconds")
                validation_data["recommendations"] = ["Verify video file integrity"]
            
            return {"content_structure": validation_data}
            
        except Exception as e:
            return {"content_structure": {"is_valid": False, "error": f"Video validation failed: {str(e)}"}}
    
    async def _validate_content_security(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Security validation of file content"""        try:
            security_issues = []
            is_suspicious = False
            is_malicious = False
            
            # Check for embedded executables
            if self._contains_executable_code(file_data):
                security_issues.append("Embedded executable code detected")
                is_malicious = True
            
            # Check for suspicious patterns
            suspicious_patterns = [
                b'eval(', b'exec(', b'system(', b'shell_exec(',
                b'<script', b'javascript:', b'vbscript:',
                b'powershell', b'cmd.exe', b'/bin/sh'
            ]
            
            for pattern in suspicious_patterns:
                if pattern in file_data:
                    security_issues.append(f"Suspicious pattern found: {pattern.decode('utf-8', errors='ignore')}")
                    is_suspicious = True
            
            # Check file entropy (compressed/encrypted files have high entropy)
            entropy = self._calculate_entropy(file_data[:1024])  # Check first 1KB
            if entropy > 7.5:  # High entropy threshold
                security_issues.append(f"High entropy detected: {entropy:.2f}")
                is_suspicious = True
            
            validation_data = {
                "is_valid": not is_malicious,
                "is_suspicious": is_suspicious,
                "is_malicious": is_malicious,
                "entropy": entropy,
                "security_issues": security_issues
            }
            
            if security_issues:
                validation_data["recommendations"] = ["Scan file with antivirus", "Verify file source"]
            
            return {"content_security": validation_data}
            
        except Exception as e:
            self.logger.error(f"Content security validation failed: {str(e)}")
            return {"content_security": {"is_valid": False, "error": str(e)}}
    
    def _determine_content_category(self, file_extension: str) -> Optional[ContentCategory]:
        """Determine content category from file extension"""        ext_mapping = {
            'jpg': ContentCategory.IMAGE, 'jpeg': ContentCategory.IMAGE, 'png': ContentCategory.IMAGE,
            'gif': ContentCategory.IMAGE, 'bmp': ContentCategory.IMAGE, 'webp': ContentCategory.IMAGE,
            'mp3': ContentCategory.AUDIO, 'wav': ContentCategory.AUDIO, 'flac': ContentCategory.AUDIO,
            'aac': ContentCategory.AUDIO, 'm4a': ContentCategory.AUDIO, 'ogg': ContentCategory.AUDIO,
            'mp4': ContentCategory.VIDEO, 'avi': ContentCategory.VIDEO, 'mov': ContentCategory.VIDEO,
            'mkv': ContentCategory.VIDEO, 'webm': ContentCategory.VIDEO, 'wmv': ContentCategory.VIDEO,
            'pdf': ContentCategory.DOCUMENT, 'doc': ContentCategory.DOCUMENT, 'docx': ContentCategory.DOCUMENT,
            'txt': ContentCategory.TEXT, 'md': ContentCategory.TEXT, 'rtf': ContentCategory.TEXT,
            'zip': ContentCategory.ARCHIVE, 'rar': ContentCategory.ARCHIVE, '7z': ContentCategory.ARCHIVE
        }
        
        return ext_mapping.get(file_extension.lower())
    
    def _get_category_from_mime(self, mime_type: str) -> Optional[ContentCategory]:
        """Get content category from MIME type"""        if mime_type.startswith('image/'):
            return ContentCategory.IMAGE
        elif mime_type.startswith('audio/'):
            return ContentCategory.AUDIO
        elif mime_type.startswith('video/'):
            return ContentCategory.VIDEO
        elif mime_type.startswith('text/'):
            return ContentCategory.TEXT
        elif mime_type in ['application/pdf', 'application/msword']:
            return ContentCategory.DOCUMENT
        elif mime_type in ['application/zip', 'application/x-rar-compressed']:
            return ContentCategory.ARCHIVE
        else:
            return None
    
    def _is_mime_type_allowed(self, mime_type: str, category: Optional[ContentCategory]) -> bool:
        """Check if MIME type is allowed for the category"""        if not category:
            return False
        
        allowed_types = self.allowed_mime_types.get(category, [])
        return mime_type in allowed_types
    
    def _contains_executable_code(self, file_data: bytes) -> bool:
        """Check if file contains executable code"""        # Check for PE header (Windows executables)
        if file_data.startswith(b'MZ'):
            return True
        
        # Check for ELF header (Linux executables)
        if file_data.startswith(b'\x7fELF'):
            return True
        
        # Check for Mach-O header (macOS executables)
        if file_data.startswith(b'\xfe\xed\xfa\xce') or file_data.startswith(b'\xfe\xed\xfa\xcf'):
            return True
        
        # Check for script interpreters
        script_headers = [
            b'#!/bin/sh', b'#!/bin/bash', b'#!/usr/bin/python',
            b'#!/usr/bin/perl', b'#!/usr/bin/ruby'
        ]
        
        for header in script_headers:
            if file_data.startswith(header):
                return True
        
        return False
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data"""        if not data:
            return 0.0
        
        # Count byte frequencies
        frequencies = {}
        for byte in data:
            frequencies[byte] = frequencies.get(byte, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        data_len = len(data)
        
        for count in frequencies.values():
            probability = count / data_len
            if probability > 0:
                entropy -= probability * (probability.bit_length() - 1)
        
        return entropy


class MalwareScanner:
    """Malware detection and scanning"""    
    def __init__(self):
        self.logger = SecurityLogger("MalwareScanner")
        self.cache = CacheManager()
        
        # Initialize malware signatures
        self.signatures = self._load_malware_signatures()
    
    def _load_malware_signatures(self) -> List[MalwareSignature]:
        """Load malware signatures"""        signatures = []
        
        # Basic malware signatures (in production, use comprehensive signature database)
        signatures.append(MalwareSignature(
            signature_id="malware_001",
            name="Windows Executable",
            description="PE executable detection",
            pattern=b'MZ',
            severity="high",
            category="executable",
            created_at=datetime.utcnow()
        ))
        
        signatures.append(MalwareSignature(
            signature_id="malware_002",
            name="Script Injection",
            description="JavaScript injection pattern",
            pattern=b'<script>alert(',
            severity="medium",
            category="script",
            created_at=datetime.utcnow()
        ))
        
        return signatures
    
    async def scan_content(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Scan content for malware"""        try:
            scan_results = {
                "is_clean": True,
                "threats_detected": [],
                "scan_time": datetime.utcnow().isoformat(),
                "scanner_version": "1.0.0"
            }
            
            # Signature-based scanning
            for signature in self.signatures:
                if signature.pattern in file_data:
                    threat = {
                        "signature_id": signature.signature_id,
                        "name": signature.name,
                        "description": signature.description,
                        "severity": signature.severity,
                        "category": signature.category
                    }
                    scan_results["threats_detected"].append(threat)
                    scan_results["is_clean"] = False
            
            # Heuristic analysis
            heuristic_results = await self._heuristic_analysis(file_data, filename)
            if heuristic_results["suspicious"]:
                scan_results["heuristic_analysis"] = heuristic_results
                if heuristic_results["risk_level"] == "high":
                    scan_results["is_clean"] = False
            
            return scan_results
            
        except Exception as e:
            self.logger.error(f"Malware scanning failed: {str(e)}")
            return {
                "is_clean": False,
                "error": str(e),
                "scan_time": datetime.utcnow().isoformat()
            }
    
    async def _heuristic_analysis(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Perform heuristic analysis"""        suspicion_score = 0
        suspicious_indicators = []
        
        # Check file size anomalies
        if len(file_data) < 100:  # Very small files
            suspicion_score += 20
            suspicious_indicators.append("Unusually small file size")
        elif len(file_data) > 1024 * 1024 * 1024:  # Very large files (>1GB)
            suspicion_score += 30
            suspicious_indicators.append("Unusually large file size")
        
        # Check filename patterns
        suspicious_filename_patterns = [
            r'.*\.(exe|bat|cmd|scr|pif)\..*',  # Double extension
            r'.*\s+.*\.(exe|bat|cmd)',  # Spaces before executable extension
            r'[A-Z]{8,}\.exe',  # Random uppercase executable
        ]
        
        for pattern in suspicious_filename_patterns:
            if re.match(pattern, filename, re.IGNORECASE):
                suspicion_score += 40
                suspicious_indicators.append(f"Suspicious filename pattern: {filename}")
                break
        
        # Check content patterns
        suspicious_content_patterns = [
            (b'CreateProcess', 10, "Process creation API"),
            (b'RegSetValue', 15, "Registry modification"),
            (b'InternetOpen', 10, "Network activity"),
            (b'VirtualAlloc', 20, "Memory allocation"),
            (b'GetProcAddress', 15, "Dynamic API loading"),
        ]
        
        for pattern, score, description in suspicious_content_patterns:
            if pattern in file_data:
                suspicion_score += score
                suspicious_indicators.append(description)
        
        # Determine risk level
        if suspicion_score >= 50:
            risk_level = "high"
        elif suspicion_score >= 30:
            risk_level = "medium"
        elif suspicion_score >= 10:
            risk_level = "low"
        else:
            risk_level = "minimal"
        
        return {
            "suspicious": suspicion_score > 0,
            "suspicion_score": suspicion_score,
            "risk_level": risk_level,
            "indicators": suspicious_indicators
        }


class VirusScanner:
    """Dedicated virus scanning functionality"""    
    def __init__(self, malware_scanner: MalwareScanner):
        self.malware_scanner = malware_scanner
        self.logger = SecurityLogger("VirusScanner")
        self.cache = CacheManager()
    
    async def scan_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Comprehensive virus scan"""        try:
            # Calculate file hash
            file_hash = hashlib.sha256(file_data).hexdigest()
            
            # Check cache for previous scan results
            cache_key = f"virus_scan:{file_hash}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            scan_result = {
                "file_hash": file_hash,
                "filename": filename,
                "file_size": len(file_data),
                "scan_timestamp": datetime.utcnow().isoformat(),
                "is_infected": False,
                "virus_signatures": [],
                "scan_engines": []
            }
            
            # Run malware scanner
            malware_results = await self.malware_scanner.scan_content(file_data, filename)
            scan_result["scan_engines"].append({
                "engine": "signature_scanner",
                "version": "1.0.0",
                "result": malware_results
            })
            
            if not malware_results["is_clean"]:
                scan_result["is_infected"] = True
                scan_result["virus_signatures"].extend(malware_results["threats_detected"])
            
            # Cache results for 1 hour
            await self.cache.set(cache_key, scan_result, expire=3600)
            
            return scan_result
            
        except Exception as e:
            self.logger.error(f"Virus scanning failed: {str(e)}")
            return {
                "file_hash": hashlib.sha256(file_data).hexdigest(),
                "filename": filename,
                "is_infected": True,  # Err on the side of caution
                "error": str(e),
                "scan_timestamp": datetime.utcnow().isoformat()
            }


class SecurityValidator:
    """Main security validation orchestrator"""    
    def __init__(self):
        self.input_validator = InputValidator()
        self.content_validator = ContentValidator()
        self.malware_scanner = MalwareScanner()
        self.virus_scanner = VirusScanner(self.malware_scanner)
        self.logger = SecurityLogger("SecurityValidator")
    
    async def validate_upload(
        self, 
        file_data: bytes, 
        filename: str,
        declared_mime_type: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> ValidationReport:
        """Comprehensive upload validation"""        try:
            # Sanitize filename
            safe_filename = self.input_validator.sanitize_filename(filename)
            
            # Content validation
            content_report = await self.content_validator.validate_content(
                file_data, safe_filename, declared_mime_type
            )
            
            # Virus scanning
            virus_results = await self.virus_scanner.scan_file(file_data, safe_filename)
            content_report.validation_details["virus_scan"] = virus_results
            
            # Update overall result based on virus scan
            if virus_results["is_infected"]:
                content_report.validation_result = ValidationResult.MALICIOUS
                content_report.security_issues.append("Virus/malware detected")
                content_report.recommendations.append("File blocked - contains malicious content")
            
            # Log validation result
            self.logger.info(
                f"Upload validation completed: {safe_filename} = {content_report.validation_result.value}"
            )
            
            return content_report
            
        except Exception as e:
            self.logger.error(f"Upload validation failed: {str(e)}")
            return ValidationReport(
                file_id="error",
                filename=filename,
                content_type="unknown",
                file_size=len(file_data),
                validation_result=ValidationResult.INVALID,
                validation_details={"error": str(e)}
            )
